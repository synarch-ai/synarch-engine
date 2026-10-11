"""Review M3 (recovery after a hard crash) and m1 (fail-safe Redis lease)."""
import asyncio
import time

import pytest
from langgraph.checkpoint.memory import MemorySaver

from config import Settings
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from tests.unit.test_s02_runtime import FakeEventBus, FakeRedis, InMemoryMissionRepository
from tests.unit.test_syn039_resume_and_lease import GatedAtZeus, SaverPort, _mission


def _runtime(repo, provider, saver, redis, lease_seconds=1):
    return MissionOrchestratorRuntime(
        mission_repo=repo, model_provider=provider, event_bus=FakeEventBus(),
        checkpointer=SaverPort(saver), redis_client=redis,
        settings=Settings(model_call_budget_cap=40, require_durable_checkpointer=True,
                          mission_lease_seconds=lease_seconds),
    )


def _plan_calls(*providers):
    return [c for p in providers for c in p.calls
            if "decompose this goal" in c["messages"][-1]["content"].lower()]


@pytest.mark.asyncio
async def test_restart_after_hard_crash_recovers_once_stale_lease_expires():
    repo, saver, redis = InMemoryMissionRepository(), MemorySaver(), FakeRedis()
    p1 = GatedAtZeus(gate_open=False)
    r1 = _runtime(repo, p1, saver, redis)
    m = await _mission(repo)
    await r1.launch_mission(m.id)
    await asyncio.wait_for(p1.started.wait(), 5)
    await r1.stop_mission(m.id)
    # A hard crash never runs `finally`: the dead worker's lease survives until its TTL.
    key = f"synarch:mission:{m.id}:lease"
    await redis.set(key, "dead-worker-token", ex=1)
    assert (await repo.get(m.id)).status == "executing"

    p2 = GatedAtZeus(gate_open=True)
    r2 = _runtime(repo, p2, saver, redis)  # restarted process, within the lease TTL
    started = time.monotonic()
    await r2.resume_inflight_missions()
    await asyncio.wait_for(r2._running_tasks[str(m.id)], 10)

    assert (await repo.get(m.id)).status == "completed"
    assert time.monotonic() - started >= 0.9  # waited for the stale lease to lapse
    assert len(_plan_calls(p1, p2)) == 1  # resumed from checkpoint, not re-planned
    assert await redis.get(key) is None  # our lease released


@pytest.mark.asyncio
async def test_recovery_gives_up_when_other_worker_finishes_mission():
    repo, saver, redis = InMemoryMissionRepository(), MemorySaver(), FakeRedis()
    m = await _mission(repo)
    key = f"synarch:mission:{m.id}:lease"
    await redis.set(key, "live-worker", ex=1)
    p = GatedAtZeus(gate_open=True)
    r = _runtime(repo, p, saver, redis)
    await r.resume_inflight_missions()
    await asyncio.sleep(0.2)
    await repo.update_status(m.id, "cancelled")  # the live worker's mission ended elsewhere
    await asyncio.wait_for(r._running_tasks[str(m.id)], 5)
    assert p.calls == []


class FlakyRedis(FakeRedis):
    """First lease renewal attempt after the lease is taken hits a connection error."""

    def __init__(self) -> None:
        super().__init__()
        self.leased = False
        self.failed = False

    async def set(self, key, value, nx=False, ex=None):
        result = await super().set(key, value, nx=nx, ex=ex)
        if key.endswith(":lease") and result:
            self.leased = True
        return result

    def _maybe_fail(self, key):
        if self.leased and key.endswith(":lease") and not self.failed:
            self.failed = True
            raise ConnectionError("transient")

    async def get(self, key):
        self._maybe_fail(key)
        return await super().get(key)

    async def eval(self, script, numkeys, key, *args):
        self._maybe_fail(key)
        return await super().eval(script, numkeys, key, *args)


@pytest.mark.asyncio
async def test_renewer_survives_transient_redis_error_and_keeps_lease():
    repo, saver, redis = InMemoryMissionRepository(), MemorySaver(), FlakyRedis()
    m = await _mission(repo)
    p = GatedAtZeus(gate_open=False)
    r = _runtime(repo, p, saver, redis, lease_seconds=1)
    run = asyncio.create_task(r.run_mission(m.id))
    await asyncio.wait_for(p.started.wait(), 5)
    await asyncio.sleep(1.6)  # well past the 1s TTL: only renewals keep the lease alive
    assert redis.failed
    key = f"synarch:mission:{m.id}:lease"
    assert not await redis.set(key, "second-worker", nx=True, ex=1)  # still held by us
    p.gate.set()
    await asyncio.wait_for(run, 10)
    assert (await repo.get(m.id)).status == "completed"


@pytest.mark.asyncio
async def test_lost_lease_stops_the_run_and_keeps_new_owner_lease():
    repo, saver, redis = InMemoryMissionRepository(), MemorySaver(), FakeRedis()
    m = await _mission(repo)
    p = GatedAtZeus(gate_open=False)
    r = _runtime(repo, p, saver, redis, lease_seconds=1)
    run = asyncio.create_task(r.run_mission(m.id))
    await asyncio.wait_for(p.started.wait(), 5)
    key = f"synarch:mission:{m.id}:lease"
    await redis.set(key, "new-owner", ex=30)  # e.g. our lease lapsed and another worker took over
    await asyncio.wait_for(run, 5)  # renewer notices within ~1/3 TTL and stops our run
    p.gate.set()
    await asyncio.sleep(0.05)
    assert (await repo.get(m.id)).status == "executing"  # left for the new owner
    assert await redis.get(key) == "new-owner"  # never deleted another worker's lease
