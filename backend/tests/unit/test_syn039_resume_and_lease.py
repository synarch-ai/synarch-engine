"""SYN-039: restart recovery resumes from checkpoint; one worker per mission."""
import asyncio

import pytest
from langgraph.checkpoint.memory import MemorySaver

from config import Settings
from domain.models.mission import AuthorityMode, Mission, MissionStatus
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from tests.unit.test_s02_runtime import (
    FakeEventBus, FakeModelProvider, FakeRedis, InMemoryMissionRepository,
)


class SaverPort:
    def __init__(self, saver):
        self.saver = saver

    def get_checkpointer(self):
        return self.saver


class GatedAtZeus(FakeModelProvider):
    def __init__(self, gate_open: bool):
        super().__init__()
        self.started = asyncio.Event()
        self.gate = asyncio.Event()
        if gate_open:
            self.gate.set()

    async def invoke(self, model, messages, **kwargs):
        if messages[-1]["content"].startswith("You are Zeus"):
            self.started.set()
            await self.gate.wait()
        return await super().invoke(model, messages, **kwargs)


def _runtime(repo, provider, saver, redis):
    return MissionOrchestratorRuntime(
        mission_repo=repo, model_provider=provider, event_bus=FakeEventBus(),
        checkpointer=SaverPort(saver), redis_client=redis,
        settings=Settings(model_call_budget_cap=40, require_durable_checkpointer=True),
    )


async def _mission(repo):
    m = Mission(goal="Build thing", authority_mode=AuthorityMode.SUPERVISED, status=MissionStatus.CREATED)
    m.thread_id = str(m.id)
    return await repo.create(m)


@pytest.mark.asyncio
async def test_restart_resumes_from_checkpoint_without_replanning():
    repo, saver, redis = InMemoryMissionRepository(), MemorySaver(), FakeRedis()
    p1 = GatedAtZeus(gate_open=False)
    r1 = _runtime(repo, p1, saver, redis)
    m = await _mission(repo)
    await r1.launch_mission(m.id)
    await asyncio.wait_for(p1.started.wait(), 5)
    await r1.stop_mission(m.id)  # simulate the process dying mid-mission; status stays executing
    assert (await repo.get(m.id)).status == "executing"

    p2 = GatedAtZeus(gate_open=True)
    r2 = _runtime(repo, p2, saver, redis)  # fresh runtime = restarted process
    await r2.resume_inflight_missions()
    await asyncio.wait_for(r2._running_tasks[str(m.id)], 10)

    assert (await repo.get(m.id)).status == "completed"
    synarch_plan_calls = [c for c in p1.calls + p2.calls if "decompose this goal" in c["messages"][-1]["content"].lower()]
    assert len(synarch_plan_calls) == 1


@pytest.mark.asyncio
async def test_second_worker_cannot_run_leased_mission():
    repo, saver, redis = InMemoryMissionRepository(), MemorySaver(), FakeRedis()
    m = await _mission(repo)
    redis.data[f"synarch:mission:{m.id}:lease"] = "other-worker"
    p = GatedAtZeus(gate_open=True)
    r = _runtime(repo, p, saver, redis)
    await r.run_mission(m.id)
    assert p.calls == []
    assert (await repo.get(m.id)).status == "created"
