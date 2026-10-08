"""codex P1: a checkpoint read error is not "no checkpoint"; never restart the graph from scratch."""
import asyncio

import pytest
from langgraph.checkpoint.memory import MemorySaver

from config import Settings
from tests.unit.test_s02_runtime import FakeRedis, InMemoryMissionRepository
from tests.unit.test_syn039_resume_and_lease import GatedAtZeus, SaverPort, _mission
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from tests.unit.test_s02_runtime import FakeEventBus

# Extra settings are ignored before the fix, so the pre-fix run fails on assertions.
_RETRY = {"persist_retry_attempts": 3, "persist_retry_delay_seconds": 0}


class FlakyStateGraph:
    """Delegates to the compiled graph, but ``aget_state`` fails ``failures`` times (None = always)."""

    def __init__(self, inner, failures):
        self.inner = inner
        self.failures = failures
        self.reads = 0

    async def aget_state(self, config, *args, **kwargs):
        self.reads += 1
        if self.failures is None or self.reads <= self.failures:
            raise ConnectionError("checkpoint store unavailable")
        return await self.inner.aget_state(config, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.inner, name)


def _runtime(repo, provider, saver, redis):
    return MissionOrchestratorRuntime(
        mission_repo=repo, model_provider=provider, event_bus=FakeEventBus(),
        checkpointer=SaverPort(saver), redis_client=redis,
        settings=Settings(model_call_budget_cap=40, require_durable_checkpointer=True, **_RETRY),
    )


async def _interrupted_mission():
    """A mission that already ran planning and was interrupted mid-graph (status executing)."""
    repo, saver, redis = InMemoryMissionRepository(), MemorySaver(), FakeRedis()
    p1 = GatedAtZeus(gate_open=False)
    r1 = _runtime(repo, p1, saver, redis)
    m = await _mission(repo)
    await r1.launch_mission(m.id)
    await asyncio.wait_for(p1.started.wait(), 5)
    await r1.stop_mission(m.id)
    assert (await repo.get(m.id)).status == "executing"
    return repo, saver, redis, m, p1


def _plan_calls(*providers):
    return [
        c for p in providers for c in p.calls
        if "decompose this goal" in c["messages"][-1]["content"].lower()
    ]


@pytest.mark.asyncio
async def test_persistent_checkpoint_read_error_fails_instead_of_restarting():
    repo, saver, redis, m, p1 = await _interrupted_mission()
    p2 = GatedAtZeus(gate_open=True)
    r2 = _runtime(repo, p2, saver, redis)
    flaky = FlakyStateGraph(r2._compiled_graph, failures=None)
    r2._compiled_graph = flaky
    await r2.run_mission(m.id)

    got = await repo.get(m.id)
    assert len(_plan_calls(p1, p2)) == 1  # the graph was not re-run from the initial state
    assert got.status == "failed"
    assert got.error_context["code"] == "CHECKPOINT_READ_FAILED"
    assert flaky.reads == 3


@pytest.mark.asyncio
async def test_transient_checkpoint_read_error_is_retried_and_resumes():
    repo, saver, redis, m, p1 = await _interrupted_mission()
    p2 = GatedAtZeus(gate_open=True)
    r2 = _runtime(repo, p2, saver, redis)
    r2._compiled_graph = FlakyStateGraph(r2._compiled_graph, failures=1)
    await r2.run_mission(m.id)

    assert len(_plan_calls(p1, p2)) == 1
    assert (await repo.get(m.id)).status == "completed"
