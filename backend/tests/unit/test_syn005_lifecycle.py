"""SYN-005: pause/cancel/resume must act on the running mission task."""
import asyncio

import pytest

from config import Settings
from domain.models.mission import AuthorityMode, Mission, MissionStatus
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from tests.unit.test_s02_runtime import (
    FakeCheckpointer, FakeEventBus, FakeModelProvider, FakeRedis, InMemoryMissionRepository,
)


class GatedProvider(FakeModelProvider):
    def __init__(self):
        super().__init__()
        self.started = asyncio.Event()
        self.gate = asyncio.Event()

    async def invoke(self, model, messages, **kwargs):
        self.started.set()
        await self.gate.wait()
        return await super().invoke(model, messages, **kwargs)


async def _setup():
    repo = InMemoryMissionRepository()
    provider = GatedProvider()
    runtime = MissionOrchestratorRuntime(
        mission_repo=repo, model_provider=provider, event_bus=FakeEventBus(),
        checkpointer=FakeCheckpointer(), redis_client=FakeRedis(),
        settings=Settings(model_call_budget_cap=40, require_durable_checkpointer=False),
    )
    m = Mission(goal="Build thing", authority_mode=AuthorityMode.SUPERVISED, status=MissionStatus.CREATED)
    m.thread_id = str(m.id)
    m = await repo.create(m)
    await runtime.launch_mission(m.id)
    await asyncio.wait_for(provider.started.wait(), 5)
    return repo, provider, runtime, m


@pytest.mark.asyncio
async def test_cancel_stops_task_without_bogus_error():
    repo, provider, runtime, m = await _setup()
    cur = await repo.get(m.id)
    await repo.update_status(m.id, "cancelled", expected_version=cur.version)
    assert await runtime.stop_mission(m.id) is True
    provider.gate.set()
    await asyncio.sleep(0.05)
    got = await repo.get(m.id)
    assert got.status == "cancelled"
    assert got.error_context is None
    assert str(m.id) not in runtime._running_tasks


@pytest.mark.asyncio
async def test_pause_then_resume_completes():
    repo, provider, runtime, m = await _setup()
    cur = await repo.get(m.id)
    await repo.update_status(m.id, "paused", expected_version=cur.version)
    await runtime.stop_mission(m.id)
    got = await repo.get(m.id)
    assert got.status == "paused" and got.error_context is None

    provider.gate.set()
    cur = await repo.get(m.id)
    await repo.update_status(m.id, "executing", expected_version=cur.version)
    await runtime.launch_mission(m.id)
    await asyncio.wait_for(runtime._running_tasks[str(m.id)], 5)
    assert (await repo.get(m.id)).status == "completed"


@pytest.mark.asyncio
async def test_completion_does_not_override_cancelled_status():
    repo, provider, runtime, m = await _setup()
    cur = await repo.get(m.id)
    await repo.update_status(m.id, "cancelled", expected_version=cur.version)
    provider.gate.set()  # task NOT stopped: it finishes on its own
    await asyncio.wait_for(runtime._running_tasks[str(m.id)], 5)
    assert (await repo.get(m.id)).status == "cancelled"
