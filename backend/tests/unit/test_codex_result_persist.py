"""codex P1: a mission is never COMPLETED unless its result was actually stored."""
import pytest

from config import Settings
from domain.models.mission import AuthorityMode, Mission, MissionStatus
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from tests.unit.test_s02_runtime import (
    FakeCheckpointer, FakeEventBus, FakeModelProvider, FakeRedis, InMemoryMissionRepository,
)


# Extra settings are ignored by pydantic-settings before the fix, so the pre-fix run
# fails on the assertions below rather than on construction.
_RETRY = {"persist_retry_attempts": 3, "persist_retry_delay_seconds": 0}


class FlakyResultRepo(InMemoryMissionRepository):
    """Result writes fail ``failures`` times (None = always), other writes succeed."""

    def __init__(self, failures: int | None) -> None:
        super().__init__()
        self.failures = failures
        self.result_attempts = 0

    async def patch_payload(self, mission_id, *, plan=None, error_context=None, result=None):
        if result is not None:
            self.result_attempts += 1
            if self.failures is None or self.result_attempts <= self.failures:
                raise ConnectionError("transient database error")
        await super().patch_payload(mission_id, plan=plan, error_context=error_context, result=result)


async def _run(repo):
    runtime = MissionOrchestratorRuntime(
        mission_repo=repo, model_provider=FakeModelProvider(), event_bus=FakeEventBus(),
        checkpointer=FakeCheckpointer(), redis_client=FakeRedis(),
        settings=Settings(
            model_call_budget_cap=40, require_durable_checkpointer=False,
            **_RETRY,
        ),
    )
    m = Mission(goal="Build API", authority_mode=AuthorityMode.SUPERVISED, status=MissionStatus.CREATED)
    m.thread_id = str(m.id)
    m = await repo.create(m)
    await runtime.run_mission(m.id)
    return await repo.get(m.id)


@pytest.mark.asyncio
async def test_result_write_that_keeps_failing_fails_the_mission():
    repo = FlakyResultRepo(failures=None)
    got = await _run(repo)
    assert got.status != "completed"
    assert got.status == "failed"
    assert got.error_context["code"] == "RESULT_PERSIST_FAILED"
    assert repo.result_attempts == 3


@pytest.mark.asyncio
async def test_transient_result_write_failure_is_retried():
    repo = FlakyResultRepo(failures=2)
    got = await _run(repo)
    assert got.status == "completed"
    assert got.result is not None and got.result["final_output"]
    assert repo.result_attempts == 3
