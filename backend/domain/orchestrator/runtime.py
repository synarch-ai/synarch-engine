"""Mission orchestration runtime — LangGraph execution on the active API path.

Note:
This runtime currently uses in-process async tasks for mission execution dispatch.
Per canonical HLD, this should move to a dedicated NATS/JetStream worker pool in a
follow-up slice to fully decouple HTTP workers from orchestration workers.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import UUID

from redis.asyncio import Redis

from config import Settings
from domain.agents.hephaestus import HephaestusAgent
from domain.agents.hermes import HermesAgent
from domain.agents.janus import JanusAgent
from domain.agents.synarch import SynarchAgent
from domain.agents.thoth import ThothAgent
from domain.agents.zeus import ZeusAgent
from domain.models.agent_message import MissionPhase
from domain.models.mission import Mission, MissionStatus
from domain.orchestrator.exceptions import BudgetExceededError
from domain.orchestrator.graph import build_graph
from ports.checkpointer import CheckpointerPort
from ports.event_bus import EventBusPort
from ports.model_provider import ModelProviderPort
from ports.persistence import MissionRepository

logger = logging.getLogger(__name__)


def _enum_value(value: object) -> str:
    if hasattr(value, "value"):
        return str(getattr(value, "value"))
    return str(value)


class MissionBudgetGuard:
    """Distributed budget guard using Redis for mission-scoped model calls."""

    def __init__(self, *, max_model_calls: int, redis: Redis, ttl_seconds: int) -> None:
        self.max_model_calls = max_model_calls
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    async def check(self, mission_id: str, agent: str, model: str) -> None:
        key = f"synarch:mission:{mission_id}:model_calls"
        calls = await self.redis.incr(key)
        if calls == 1:
            await self.redis.expire(key, self.ttl_seconds)

        if calls > self.max_model_calls:
            raise BudgetExceededError(
                f"Mission '{mission_id}' exceeded model-call budget "
                f"({calls}>{self.max_model_calls}) at agent '{agent}' model '{model}'."
            )

    async def clear(self, mission_id: str) -> None:
        key = f"synarch:mission:{mission_id}:model_calls"
        await self.redis.delete(key)


class MissionOrchestratorRuntime:
    """Runs a mission through LangGraph using configured agents/models."""

    def __init__(
        self,
        mission_repo: MissionRepository,
        model_provider: ModelProviderPort,
        event_bus: EventBusPort,
        checkpointer: CheckpointerPort,
        redis_client: Redis,
        settings: Settings,
    ) -> None:
        self.mission_repo = mission_repo
        self.model_provider = model_provider
        self.event_bus = event_bus
        self.checkpointer = checkpointer
        self.redis_client = redis_client
        self.settings = settings
        self.budget_guard = MissionBudgetGuard(
            max_model_calls=settings.model_call_budget_cap,
            redis=redis_client,
            ttl_seconds=settings.budget_counter_ttl_seconds,
        )
        self._running_tasks: dict[str, asyncio.Task[Any]] = {}
        self._compiled_graph: Any = self._compile_graph()

    def _build_agent_nodes(self) -> dict[str, Any]:
        agent_common = {
            "model_provider": self.model_provider,
            "event_bus": self.event_bus,
            "soul_path": self.settings.souls_dir,
            "budget_guard": self.budget_guard.check,
        }

        synarch = SynarchAgent(
            name="synarch",
            model=self.settings.model_synarch,
            **agent_common,
        )
        zeus = ZeusAgent(
            name="zeus",
            model=self.settings.model_zeus,
            **agent_common,
        )
        thoth = ThothAgent(
            name="thoth",
            model=self.settings.model_thoth,
            **agent_common,
        )
        hermes = HermesAgent(
            name="hermes",
            model=self.settings.model_hermes,
            **agent_common,
        )
        hephaestus = HephaestusAgent(
            name="hephaestus",
            model=self.settings.model_hephaestus,
            **agent_common,
        )
        janus = JanusAgent(
            name="janus",
            model=self.settings.model_janus,
            **agent_common,
        )

        return {
            "synarch": synarch,
            "zeus": zeus,
            "thoth": thoth,
            "hermes": hermes,
            "hephaestus": hephaestus,
            "janus": janus,
            "synthesize": synarch,
            "fail": self._fail_node,
        }

    async def _fail_node(self, state: dict[str, Any]) -> dict[str, Any]:
        feedback = state.get("review_feedback") or "Janus returned FAIL verdict"
        return {
            "phase": MissionPhase.REVIEWING.value,
            "error": f"REVIEW_FAILED: {feedback}",
        }

    def _compile_graph(self) -> Any:
        graph = build_graph(self._build_agent_nodes())
        if self.settings.require_durable_checkpointer:
            checkpointer = self.checkpointer.get_checkpointer()
            logger.info("Compiling LangGraph with PostgreSQL checkpointer (strict mode).")
            return graph.compile(checkpointer=checkpointer)

        logger.warning("Compiling LangGraph without checkpointer (non-durable mode).")
        return graph.compile()

    async def _transition(self, mission_id: UUID, status: MissionStatus) -> Mission | None:
        for _ in range(3):
            mission = await self.mission_repo.get(mission_id)
            if mission is None:
                return None
            try:
                await self.mission_repo.update_status(
                    mission_id,
                    status.value,
                    expected_version=mission.version,
                )
                return await self.mission_repo.get(mission_id)
            except Exception as exc:
                if getattr(exc, "code", None) == "MISSION_CONFLICT":
                    continue
                raise
        raise RuntimeError(f"Failed to transition mission '{mission_id}' to '{status.value}' due to conflicts.")

    async def launch_mission(self, mission_id: UUID) -> None:
        mission_key = str(mission_id)
        existing = self._running_tasks.get(mission_key)
        if existing and not existing.done():
            return

        task = asyncio.create_task(self.run_mission(mission_id), name=f"mission:{mission_key}")
        self._running_tasks[mission_key] = task

        def _cleanup(completed: asyncio.Task[Any]) -> None:
            self._running_tasks.pop(mission_key, None)
            if completed.cancelled():
                return
            error = completed.exception()
            if error:
                logger.exception("Mission task %s crashed: %s", mission_key, error)

        task.add_done_callback(_cleanup)

    async def resume_inflight_missions(self) -> None:
        """Best-effort bootstrap recovery for missions mid-flight at startup."""
        resume_statuses = (
            MissionStatus.CREATED.value,
            MissionStatus.PLANNING.value,
            MissionStatus.EXECUTING.value,
        )
        for status in resume_statuses:
            missions = await self.mission_repo.list(status=status, limit=500, offset=0)
            for mission in missions:
                await self.launch_mission(mission.id)

    async def start_mission(self, mission_id: UUID) -> None:
        """Explicitly start a newly created mission."""
        await self.launch_mission(mission_id)

    async def resume_mission(self, mission_id: str, decision_payload: dict) -> None:
        """Resume a mission from an interruption (HITL)."""
        from langgraph.types import Command

        # Retrieve thread_id from mission_repo
        mission = await self.mission_repo.get(UUID(mission_id))
        if not mission or not mission.thread_id:
            raise ValueError(f"Mission {mission_id} not found or has no thread")

        config = {"configurable": {"thread_id": mission.thread_id}}

        # Resume the graph with the decision
        # The 'interrupt' value is returned to the node that called it.
        # We pass the decision payload.
        await self._compiled_graph.ainvoke(
            Command(resume=decision_payload),
            config=config
        )

    async def run_mission(self, mission_id: UUID) -> None:
        mission = await self.mission_repo.get(mission_id)
        if mission is None:
            logger.warning("Mission %s disappeared before orchestration start.", mission_id)
            return

        mission_id_str = str(mission.id)
        try:
            if _enum_value(mission.status) == MissionStatus.CREATED.value:
                planning = await self._transition(mission.id, MissionStatus.PLANNING)
                if planning is None:
                    return
                mission = planning

            if _enum_value(mission.status) in {MissionStatus.CREATED.value, MissionStatus.PLANNING.value}:
                executing = await self._transition(mission.id, MissionStatus.EXECUTING)
                if executing is None:
                    return
                mission = executing

            initial_state = {
                "mission_id": mission_id_str,
                "goal": mission.goal,
                "authority_mode": _enum_value(mission.authority_mode),
                "plan": mission.plan or [],
                "plan_rationale": "",
                "phase": MissionPhase.PLANNING.value,
                "tasks": [],
                "current_agent": "",
                "messages": [],
                "review_verdict": None,
                "review_feedback": None,
                "revision_count": 0,
                "deliverables": [],
                "final_output": None,
                "needs_approval": False,
                "approval_request": None,
                "error": None,
            }
            graph_config = {"configurable": {"thread_id": mission.thread_id or mission_id_str}}
            final_state = await self._compiled_graph.ainvoke(initial_state, config=graph_config)

            await self.mission_repo.patch_payload(
                mission.id,
                plan=final_state.get("plan") or [],
            )

            if final_state.get("error"):
                await self.mission_repo.patch_payload(
                    mission.id,
                    error_context={
                        "code": "MISSION_RUNTIME_ERROR",
                        "message": str(final_state["error"]),
                    },
                )
                await self._transition(mission.id, MissionStatus.FAILED)
                return

            await self._transition(mission.id, MissionStatus.COMPLETED)
        except BudgetExceededError as exc:
            await self.mission_repo.patch_payload(
                mission.id,
                error_context={
                    "code": "BUDGET_EXCEEDED",
                    "message": str(exc),
                },
            )
            await self._transition(mission.id, MissionStatus.PAUSED_AWAITING_RESOURCES)
        except Exception as exc:
            logger.exception("Mission orchestration failed for %s: %s", mission.id, exc)
            await self.mission_repo.patch_payload(
                mission.id,
                error_context={
                    "code": "MISSION_RUNTIME_ERROR",
                    "message": str(exc),
                },
            )
            await self._transition(mission.id, MissionStatus.FAILED)
        finally:
            await self.budget_guard.clear(mission_id_str)
