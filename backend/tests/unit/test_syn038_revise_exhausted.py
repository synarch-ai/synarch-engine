"""SYN-038: exhausted REVISE verdicts must fail the mission, not re-plan and 'complete' it."""
import pytest

from config import Settings
from domain.models.mission import AuthorityMode, Mission, MissionStatus
from domain.orchestrator.routing import route_after_review
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from tests.unit.test_s02_runtime import (
    FakeCheckpointer, FakeEventBus, FakeModelProvider, FakeRedis, InMemoryMissionRepository,
)


def test_route_exhausted_revise_goes_to_fail():
    assert route_after_review({"review_verdict": "REVISE", "revision_count": 2}) == "revise"
    assert route_after_review({"review_verdict": "REVISE", "revision_count": 3}) == "fail"
    assert route_after_review({"review_verdict": "PASS", "revision_count": 3}) == "synthesize"


@pytest.mark.asyncio
async def test_always_revise_mission_fails_without_synthesis():
    repo = InMemoryMissionRepository()
    provider = FakeModelProvider(janus_verdict="REVISE")
    runtime = MissionOrchestratorRuntime(
        mission_repo=repo, model_provider=provider, event_bus=FakeEventBus(),
        checkpointer=FakeCheckpointer(), redis_client=FakeRedis(),
        settings=Settings(model_call_budget_cap=60, require_durable_checkpointer=False),
    )
    mission = Mission(goal="Build thing", authority_mode=AuthorityMode.SUPERVISED, status=MissionStatus.CREATED)
    mission.thread_id = str(mission.id)
    mission = await repo.create(mission)

    await runtime.run_mission(mission.id)
    updated = await repo.get(mission.id)

    assert updated.status == MissionStatus.FAILED.value
    assert "revision limit exhausted" in updated.error_context["message"]
    assert not any("mission is complete" in c["messages"][-1]["content"].lower() for c in provider.calls)
