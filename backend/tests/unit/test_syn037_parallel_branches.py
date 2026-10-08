"""SYN-037: missions routed to both Zeus and Thoth must not fail on parallel writes."""
import pytest

from config import Settings
from domain.models.mission import AuthorityMode, Mission, MissionStatus
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from tests.unit.test_s02_runtime import (
    FakeCheckpointer, FakeEventBus, FakeModelProvider, FakeRedis, InMemoryMissionRepository,
)


class MixedPlanProvider(FakeModelProvider):
    async def invoke(self, model, messages, **kwargs):
        system = messages[0]["content"].lower()
        user = messages[-1]["content"].lower()
        if "synarch" in system and "decompose this goal" in user:
            return "Implement the backend API\nResearch competing approaches"
        return await super().invoke(model, messages, **kwargs)


def _runtime(repo, provider):
    return MissionOrchestratorRuntime(
        mission_repo=repo, model_provider=provider, event_bus=FakeEventBus(),
        checkpointer=FakeCheckpointer(), redis_client=FakeRedis(),
        settings=Settings(model_call_budget_cap=40, require_durable_checkpointer=False),
    )


@pytest.mark.asyncio
async def test_research_plus_engineering_mission_completes():
    repo = InMemoryMissionRepository()
    provider = MixedPlanProvider()
    mission = Mission(goal="Build and research", authority_mode=AuthorityMode.SUPERVISED, status=MissionStatus.CREATED)
    mission.thread_id = str(mission.id)
    mission = await repo.create(mission)

    await _runtime(repo, provider).run_mission(mission.id)
    updated = await repo.get(mission.id)

    assert updated.status == MissionStatus.COMPLETED.value, updated.error_context
    models = [c["model"] for c in provider.calls]
    s = Settings()
    assert s.model_zeus in models and s.model_thoth in models
    assert s.model_hephaestus in models and s.model_hermes in models
