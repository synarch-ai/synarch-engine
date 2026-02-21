"""S02 runtime tests: LangGraph routing + model/prompt baseline + budget guard."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pytest

from config import Settings
from domain.models.mission import AuthorityMode, Mission, MissionStatus
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from ports.persistence import MissionRepository


class InMemoryMissionRepository(MissionRepository):
    def __init__(self) -> None:
        self._missions: dict[UUID, Mission] = {}

    async def create(self, mission: Mission) -> Mission:
        now = datetime.utcnow()
        mission.created_at = now
        mission.updated_at = now
        mission.version = 1
        self._missions[mission.id] = mission
        return mission

    async def get(self, mission_id: UUID) -> Mission | None:
        return self._missions.get(mission_id)

    async def update_status(self, mission_id: UUID, status: str, **kwargs) -> None:
        mission = self._missions.get(mission_id)
        if mission is None:
            return
        expected_version = kwargs.get("expected_version")
        if expected_version is not None and int(expected_version) != mission.version:
            raise RuntimeError("MISSION_CONFLICT")
        mission.status = status
        mission.version += 1
        mission.updated_at = datetime.utcnow()
        if status == "completed":
            mission.completed_at = mission.updated_at

    async def list(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Mission]:
        rows = list(self._missions.values())
        if status:
            rows = [row for row in rows if str(row.status) == status or getattr(row.status, "value", None) == status]
        return rows[offset : offset + limit]

    async def patch_payload(
        self,
        mission_id: UUID,
        *,
        plan: list[str] | None = None,
        error_context: dict | None = None,
    ) -> None:
        mission = self._missions.get(mission_id)
        if mission is None:
            return
        if plan is not None:
            mission.plan = plan
        if error_context is not None:
            mission.error_context = error_context


class FakeEventBus:
    async def connect(self) -> None:
        return None

    async def publish(self, event) -> None:
        return None

    async def subscribe(self, subject: str, callback):
        return None

    async def close(self) -> None:
        return None


class FakeCheckpointer:
    async def setup(self) -> None:
        return None

    async def close(self) -> None:
        return None

    def get_checkpointer(self):
        raise RuntimeError("checkpointer not configured for unit tests")


class FakeRedis:
    def __init__(self) -> None:
        self.data: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]

    async def expire(self, key: str, ttl: int) -> bool:
        return True

    async def delete(self, key: str) -> int:
        return 1 if self.data.pop(key, None) is not None else 0


class FakeModelProvider:
    def __init__(self, *, janus_verdict: str = "PASS") -> None:
        self.calls: list[dict] = []
        self.janus_verdict = janus_verdict

    async def invoke(self, model: str, messages: list[dict], **kwargs) -> str:
        self.calls.append({"model": model, "messages": messages})
        system = (messages[0].get("content", "") if messages else "").lower()
        user = (messages[-1].get("content", "") if messages else "").lower()

        if "synarch" in system and "decompose this goal" in user:
            return "Build backend API endpoints"
        if "zeus" in system:
            return "Implement mission orchestration service."
        if "hephaestus" in system:
            return "Implemented code artifacts."
        if "janus" in system:
            if self.janus_verdict == "FAIL":
                return "FAIL: deliverables do not satisfy acceptance criteria."
            if self.janus_verdict == "REVISE":
                return "REVISE: needs improvements."
            return "PASS: quality bar met."
        if "synarch" in system and "mission is complete" in user:
            return "Final synthesized output."
        return "generic response"


@pytest.mark.asyncio
async def test_runtime_executes_langgraph_and_completes_mission() -> None:
    repo = InMemoryMissionRepository()
    model_provider = FakeModelProvider()
    settings = Settings(model_call_budget_cap=24, require_durable_checkpointer=False)
    runtime = MissionOrchestratorRuntime(
        mission_repo=repo,
        model_provider=model_provider,
        event_bus=FakeEventBus(),
        checkpointer=FakeCheckpointer(),
        redis_client=FakeRedis(),
        settings=settings,
    )

    mission = Mission(
        goal="Build API service for mission runtime",
        authority_mode=AuthorityMode.SUPERVISED,
        status=MissionStatus.CREATED,
    )
    mission.thread_id = str(mission.id)
    mission = await repo.create(mission)

    await runtime.run_mission(mission.id)
    updated = await repo.get(mission.id)

    assert updated is not None
    assert updated.status == MissionStatus.COMPLETED.value
    assert updated.plan is not None
    assert any("build backend api" in step.lower() for step in updated.plan)

    models_used = [call["model"] for call in model_provider.calls]
    assert settings.model_synarch in models_used
    assert settings.model_zeus in models_used
    assert settings.model_hephaestus in models_used
    assert settings.model_janus in models_used

    # FR-12 baseline: every call carries a non-empty system prompt sourced from soul/config.
    assert all(call["messages"][0]["role"] == "system" for call in model_provider.calls)
    assert all(bool(call["messages"][0]["content"].strip()) for call in model_provider.calls)


@pytest.mark.asyncio
async def test_runtime_budget_guard_degrades_to_paused_awaiting_resources() -> None:
    repo = InMemoryMissionRepository()
    model_provider = FakeModelProvider()
    settings = Settings(model_call_budget_cap=1, require_durable_checkpointer=False)
    runtime = MissionOrchestratorRuntime(
        mission_repo=repo,
        model_provider=model_provider,
        event_bus=FakeEventBus(),
        checkpointer=FakeCheckpointer(),
        redis_client=FakeRedis(),
        settings=settings,
    )

    mission = Mission(
        goal="Build a full API service",
        authority_mode=AuthorityMode.SUPERVISED,
        status=MissionStatus.CREATED,
    )
    mission.thread_id = str(mission.id)
    mission = await repo.create(mission)

    await runtime.run_mission(mission.id)
    updated = await repo.get(mission.id)

    assert updated is not None
    assert updated.status == MissionStatus.PAUSED_AWAITING_RESOURCES.value
    assert updated.error_context is not None
    assert updated.error_context.get("code") == "BUDGET_EXCEEDED"


@pytest.mark.asyncio
async def test_runtime_fail_verdict_transitions_mission_to_failed() -> None:
    repo = InMemoryMissionRepository()
    model_provider = FakeModelProvider(janus_verdict="FAIL")
    settings = Settings(model_call_budget_cap=24, require_durable_checkpointer=False)
    runtime = MissionOrchestratorRuntime(
        mission_repo=repo,
        model_provider=model_provider,
        event_bus=FakeEventBus(),
        checkpointer=FakeCheckpointer(),
        redis_client=FakeRedis(),
        settings=settings,
    )

    mission = Mission(
        goal="Build API service that should fail review",
        authority_mode=AuthorityMode.SUPERVISED,
        status=MissionStatus.CREATED,
    )
    mission.thread_id = str(mission.id)
    mission = await repo.create(mission)

    await runtime.run_mission(mission.id)
    updated = await repo.get(mission.id)

    assert updated is not None
    assert updated.status == MissionStatus.FAILED.value
    assert updated.error_context is not None
    assert "REVIEW_FAILED" in updated.error_context.get("message", "")
