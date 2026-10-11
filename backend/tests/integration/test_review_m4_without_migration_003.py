"""Review M4: mission writes must not depend on migration 003 (mission_payloads.result)."""
import os
from uuid import uuid4

import pytest
import pytest_asyncio

from adapters.postgres.repositories import PostgresMissionRepository
from config import Settings
from domain.models.mission import AuthorityMode, Mission, MissionStatus
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from tests.unit.test_s02_runtime import FakeCheckpointer, FakeEventBus, FakeModelProvider, FakeRedis


class _RecordingConn:
    def __init__(self, sql: list) -> None:
        self.sql = sql

    def transaction(self):
        class _Tx:
            async def __aenter__(self):
                return None

            async def __aexit__(self, *exc):
                return False

        return _Tx()

    async def execute(self, query, *args):
        self.sql.append((query, args))


class _RecordingPool:
    def __init__(self) -> None:
        self.sql: list = []

    def acquire(self):
        pool = self

        class _Ctx:
            async def __aenter__(self):
                return _RecordingConn(pool.sql)

            async def __aexit__(self, *exc):
                return False

        return _Ctx()


@pytest.mark.asyncio
async def test_patch_payload_only_names_written_columns():
    pool = _RecordingPool()
    repo = PostgresMissionRepository(pool)
    mid = uuid4()
    await repo.patch_payload(mid, plan=["a"])
    await repo.patch_payload(mid, error_context={"code": "X"})
    upserts = [q for q, _ in pool.sql if "mission_payloads" in q]
    assert len(upserts) == 2
    assert all("result" not in q for q in upserts)
    pool.sql.clear()
    await repo.patch_payload(mid, result={"final_output": "ok"})
    assert "result" in pool.sql[0][0]


@pytest_asyncio.fixture
async def repo_without_003():
    """A Postgres repository whose mission_payloads table lacks the 003 ``result`` column."""
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set")
    import asyncpg

    schema = f"m4_{uuid4().hex[:10]}"
    admin = await asyncpg.connect(url)
    await admin.execute(f"CREATE SCHEMA {schema}")
    await admin.execute(f"CREATE TABLE {schema}.mission_payloads (LIKE public.mission_payloads INCLUDING ALL)")
    await admin.execute(f"ALTER TABLE {schema}.mission_payloads DROP COLUMN IF EXISTS result")
    pool = await asyncpg.create_pool(url, min_size=1, max_size=4, server_settings={"search_path": f"{schema},public"})
    created: list = []
    try:
        yield PostgresMissionRepository(pool), created
    finally:
        await pool.close()
        for mid in created:
            await admin.execute("DELETE FROM public.missions WHERE id = $1::uuid", mid)
        await admin.execute(f"DROP SCHEMA {schema} CASCADE")
        await admin.close()


@pytest.mark.asyncio
async def test_payload_writes_and_mission_run_work_without_003(repo_without_003):
    repo, created = repo_without_003
    m = Mission(goal="no 003", authority_mode=AuthorityMode.SUPERVISED, status=MissionStatus.CREATED)
    m.thread_id = str(m.id)
    m = await repo.create(m)
    created.append(m.id)

    await repo.patch_payload(m.id, plan=["step 1"])
    await repo.patch_payload(m.id, error_context={"code": "X", "message": "y"})
    got = await repo.get(m.id)
    assert got.plan == ["step 1"] and got.error_context["code"] == "X"
    assert got.result is None

    m2 = Mission(goal="Build API", authority_mode=AuthorityMode.SUPERVISED, status=MissionStatus.CREATED)
    m2.thread_id = str(m2.id)
    m2 = await repo.create(m2)
    created.append(m2.id)
    runtime = MissionOrchestratorRuntime(
        mission_repo=repo, model_provider=FakeModelProvider(), event_bus=FakeEventBus(),
        checkpointer=FakeCheckpointer(), redis_client=FakeRedis(),
        settings=Settings(
            model_call_budget_cap=40, require_durable_checkpointer=False, persist_retry_delay_seconds=0,
        ),
    )
    await runtime.run_mission(m2.id)
    done = await repo.get(m2.id)
    # Not stuck in executing, and never COMPLETED without a stored result (codex P1).
    assert str(getattr(done.status, "value", done.status)) == "failed"
    assert done.error_context["code"] == "RESULT_PERSIST_FAILED"
    assert done.plan
