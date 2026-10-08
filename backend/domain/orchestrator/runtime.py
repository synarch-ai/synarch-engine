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
from uuid import UUID, uuid4

from redis.asyncio import Redis

from config import Settings
from domain.agents.hephaestus import HephaestusAgent
from domain.agents.hermes import HermesAgent
from domain.agents.janus import JanusAgent
from domain.agents.synarch import SynarchAgent, SynthesizerAgent
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


_RUNNABLE = {
    MissionStatus.CREATED.value,
    MissionStatus.PLANNING.value,
    MissionStatus.EXECUTING.value,
}

# Compare-and-expire / compare-and-delete so a worker can never extend or delete
# a lease that another worker now owns (review m1).
_LEASE_RENEW_LUA = """
if redis.call('get', KEYS[1]) == ARGV[1] then
  return redis.call('expire', KEYS[1], ARGV[2])
end
return 0
"""
_LEASE_RELEASE_LUA = """
if redis.call('get', KEYS[1]) == ARGV[1] then
  return redis.call('del', KEYS[1])
end
return 0
"""


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

        synthesizer = SynthesizerAgent(
            name="synarch",
            model=self.settings.model_synarch,
            **agent_common,
        )

        return {
            "synarch": synarch,
            "zeus": zeus,
            "thoth": thoth,
            "hermes": hermes,
            "hephaestus": hephaestus,
            "janus": janus,
            "synthesize": synthesizer,
            "fail": self._fail_node,
        }

    async def _fail_node(self, state: dict[str, Any]) -> dict[str, Any]:
        feedback = state.get("review_feedback") or "Janus returned FAIL verdict"
        if state.get("review_verdict") == "REVISE":
            feedback = f"revision limit exhausted without PASS; needs human review. Last feedback: {feedback}"
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

    async def _load_checkpoint(self, graph_config: dict) -> Any | None:
        if not self.settings.require_durable_checkpointer:
            return None
        try:
            snapshot = await self._compiled_graph.aget_state(graph_config)
        except Exception as exc:  # no checkpoint / backend hiccup -> start fresh
            logger.warning("Could not load checkpoint: %s", exc)
            return None
        return snapshot if snapshot is not None and snapshot.values else None

    def _lease_key(self, mission_id: UUID) -> str:
        return f"synarch:mission:{mission_id}:lease"

    async def _renew_once(self, key: str, token: str) -> bool:
        """Extend our lease, or re-take it if it lapsed and nobody else holds it."""
        ttl = self.settings.mission_lease_seconds
        if await self.redis_client.eval(_LEASE_RENEW_LUA, 1, key, token, ttl):
            return True
        return bool(await self.redis_client.set(key, token, nx=True, ex=ttl))

    async def _renew_lease(self, key: str, token: str, lease_lost: asyncio.Event) -> None:
        """Keep the lease alive; survive transient Redis errors; flag loss (review m1)."""
        ttl = self.settings.mission_lease_seconds
        interval = max(ttl / 3, 0.01)
        loop = asyncio.get_running_loop()
        last_ok = loop.time()
        while True:
            await asyncio.sleep(interval)
            try:
                if await self._renew_once(key, token):
                    last_ok = loop.time()
                    continue
                logger.error("Lease %s was taken by another worker; stopping this run.", key)
            except Exception as exc:  # noqa: BLE001 - transient Redis failure: retry until the lease would lapse
                if loop.time() - last_ok < ttl:
                    logger.warning("Lease renewal for %s failed (%s); retrying.", key, exc)
                    continue
                logger.error("Lease %s could not be renewed for %ss; stopping this run.", key, ttl)
            lease_lost.set()
            return

    async def _release_lease(self, key: str, token: str) -> None:
        try:
            await self.redis_client.eval(_LEASE_RELEASE_LUA, 1, key, token)
        except Exception as exc:  # noqa: BLE001 - the lease expires on its own
            logger.warning("Could not release lease %s: %s", key, exc)

    async def run_mission(self, mission_id: UUID) -> bool:
        """Run a mission under a cross-replica Redis lease (SYN-039).

        Returns False without running when another worker holds the lease.
        """
        key = self._lease_key(mission_id)
        token = uuid4().hex
        acquired = await self.redis_client.set(key, token, nx=True, ex=self.settings.mission_lease_seconds)
        if not acquired:
            logger.info("Mission %s is leased by another worker; skipping.", mission_id)
            return False
        lease_lost = asyncio.Event()
        renewer = asyncio.create_task(self._renew_lease(key, token, lease_lost))
        work = asyncio.create_task(self._run_mission_locked(mission_id))
        lost_waiter = asyncio.create_task(lease_lost.wait())
        try:
            await asyncio.wait({work, lost_waiter}, return_when=asyncio.FIRST_COMPLETED)
            if not work.done():
                # Lease lost: another worker may now own the mission; stop ours without
                # touching its status (the CancelledError path writes nothing).
                work.cancel()
                try:
                    await work
                except asyncio.CancelledError:
                    pass
                return True
            await work  # propagate the run's own exception, if any
            return True
        except asyncio.CancelledError:
            work.cancel()
            try:
                await work
            except BaseException:  # noqa: BLE001
                pass
            raise
        finally:
            renewer.cancel()
            lost_waiter.cancel()
            await self._release_lease(key, token)

    async def _run_when_lease_free(self, mission_id: UUID) -> None:
        """Recovery path: if a stale lease (e.g. from a crashed process) blocks the run,
        retry once it has had time to expire instead of giving up (review M3)."""
        key = self._lease_key(mission_id)
        while True:
            if await self.run_mission(mission_id):
                return
            mission = await self.mission_repo.get(mission_id)
            if mission is None or _enum_value(mission.status) not in _RUNNABLE:
                return
            try:
                remaining_ms = await self.redis_client.pttl(key)
            except Exception:  # noqa: BLE001
                remaining_ms = -1
            wait = (remaining_ms / 1000) if remaining_ms and remaining_ms > 0 else self.settings.mission_lease_seconds
            logger.info("Mission %s is leased; retrying recovery in %.1fs.", mission_id, wait)
            await asyncio.sleep(wait + 0.05)

    async def stop_mission(self, mission_id: UUID) -> bool:
        """Cancel the in-process task running a mission (pause/cancel support, SYN-005)."""
        task = self._running_tasks.get(str(mission_id))
        if task is None or task.done():
            return False
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            current = asyncio.current_task()
            if current is not None and current.cancelling():
                raise  # the caller itself is being cancelled (disconnect/shutdown): propagate
        except Exception:  # noqa: BLE001 - the mission task's own failure is logged by its callback
            pass
        return True

    async def _finish(self, mission_id: UUID, status: MissionStatus) -> None:
        """Terminal transition that never overrides an externally-set status."""
        mission = await self.mission_repo.get(mission_id)
        if mission is None or _enum_value(mission.status) != MissionStatus.EXECUTING.value:
            logger.info(
                "Mission %s left executing state (%s); skipping transition to %s.",
                mission_id, _enum_value(mission.status) if mission else None, status.value,
            )
            return
        try:
            await self._transition(mission_id, status)
        except Exception as exc:
            if getattr(exc, "code", None) == "MISSION_INVALID_TRANSITION":
                logger.info("Mission %s transition to %s no longer valid: %s", mission_id, status.value, exc)
                return
            raise

    async def launch_mission(self, mission_id: UUID, *, wait_for_lease: bool = False) -> None:
        mission_key = str(mission_id)
        existing = self._running_tasks.get(mission_key)
        if existing and not existing.done():
            return

        runner = self._run_when_lease_free(mission_id) if wait_for_lease else self.run_mission(mission_id)
        task = asyncio.create_task(runner, name=f"mission:{mission_key}")
        self._running_tasks[mission_key] = task

        def _cleanup(completed: asyncio.Task[Any]) -> None:
            if self._running_tasks.get(mission_key) is completed:
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
                await self.launch_mission(mission.id, wait_for_lease=True)

    async def _run_mission_locked(self, mission_id: UUID) -> None:
        mission = await self.mission_repo.get(mission_id)
        if mission is None:
            logger.warning("Mission %s disappeared before orchestration start.", mission_id)
            return

        if _enum_value(mission.status) not in {
            MissionStatus.CREATED.value,
            MissionStatus.PLANNING.value,
            MissionStatus.EXECUTING.value,
        }:
            logger.info("Mission %s in status %s is not runnable; skipping.", mission_id, _enum_value(mission.status))
            return

        mission_id_str = str(mission.id)
        cancelled = False
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
            graph_input: Any = initial_state
            snapshot = await self._load_checkpoint(graph_config)
            if snapshot is not None and snapshot.next:
                logger.info("Resuming mission %s from checkpoint at %s.", mission.id, snapshot.next)
                graph_input = None  # continue from the saved checkpoint (SYN-039)
            elif snapshot is not None and snapshot.values:
                logger.info("Mission %s graph already finished; reusing final state.", mission.id)
                graph_input = None
            final_state = await self._compiled_graph.ainvoke(graph_input, config=graph_config)

            await self.mission_repo.patch_payload(
                mission.id,
                plan=final_state.get("plan") or [],
            )
            try:
                await self.mission_repo.patch_payload(
                    mission.id,
                    result={
                        "final_output": final_state.get("final_output"),
                        "deliverables": final_state.get("deliverables") or [],
                        "messages": final_state.get("messages") or [],
                        "tasks": final_state.get("tasks") or [],
                    },
                )
            except Exception:
                logger.exception("Failed to persist result for mission %s (is migration 003 applied?)", mission.id)

            if final_state.get("error"):
                await self.mission_repo.patch_payload(
                    mission.id,
                    error_context={
                        "code": "MISSION_RUNTIME_ERROR",
                        "message": str(final_state["error"]),
                    },
                )
                await self._finish(mission.id, MissionStatus.FAILED)
                return

            await self._finish(mission.id, MissionStatus.COMPLETED)
        except asyncio.CancelledError:
            cancelled = True
            raise
        except BudgetExceededError as exc:
            await self.mission_repo.patch_payload(
                mission.id,
                error_context={
                    "code": "BUDGET_EXCEEDED",
                    "message": str(exc),
                },
            )
            await self._finish(mission.id, MissionStatus.PAUSED_AWAITING_RESOURCES)
        except Exception as exc:
            logger.exception("Mission orchestration failed for %s: %s", mission.id, exc)
            await self.mission_repo.patch_payload(
                mission.id,
                error_context={
                    "code": "MISSION_RUNTIME_ERROR",
                    "message": str(exc),
                },
            )
            await self._finish(mission.id, MissionStatus.FAILED)
        finally:
            if not cancelled:
                await self.budget_guard.clear(mission_id_str)
