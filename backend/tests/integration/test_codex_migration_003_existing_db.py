"""codex P1: a database created before migration 003 gets mission_payloads.result at startup.

docker-compose's initdb scripts only run on a fresh volume, so the backend must apply
003 itself when it connects to an existing database.
"""
import os
from uuid import uuid4

import pytest
from langgraph.checkpoint.memory import MemorySaver

import container as container_module
from config import Settings
from tests.unit.test_s02_runtime import FakeEventBus, FakeRedis


class _Conn:
    def __init__(self, pool):
        self.pool = pool

    async def fetchval(self, query, *args):
        self.pool.sql.append(query)
        return self.pool.has_result_column

    async def fetch(self, query, *args):
        self.pool.sql.append(query)
        return []

    async def execute(self, query, *args):
        self.pool.sql.append(query)


class _Pool:
    """Stands in for asyncpg: a database whose mission_payloads has no result column."""

    def __init__(self, has_result_column: bool) -> None:
        self.has_result_column = has_result_column
        self.sql: list[str] = []

    def acquire(self):
        pool = self

        class _Ctx:
            async def __aenter__(self):
                return _Conn(pool)

            async def __aexit__(self, *exc):
                return False

        return _Ctx()

    async def close(self):
        return None


class _Checkpointer:
    def __init__(self, database_url):
        pass

    async def setup(self):
        return None

    async def close(self):
        return None

    def get_checkpointer(self):
        return MemorySaver()


class _PingRedis(FakeRedis):
    async def ping(self):
        return True

    async def aclose(self):
        return None


def _patch_adapters(monkeypatch, pool):
    import adapters.langgraph.checkpointer as lg
    import adapters.litellm.provider as llm
    import adapters.nats.client as nats
    import adapters.postgres.repositories as pg
    import redis.asyncio as aioredis

    async def _create_pool(url):
        return pool

    monkeypatch.setattr(nats, "NATSEventBus", lambda url: FakeEventBus())
    monkeypatch.setattr(llm, "LiteLLMProvider", lambda: object())
    monkeypatch.setattr(lg, "LangGraphCheckpointer", _Checkpointer)
    monkeypatch.setattr(aioredis.Redis, "from_url", staticmethod(lambda *a, **k: _PingRedis()))
    monkeypatch.setattr(pg, "create_postgres_pool", _create_pool)


def _ran_003(pool) -> bool:
    return any("ADD COLUMN IF NOT EXISTS result" in q for q in pool.sql)


@pytest.mark.asyncio
async def test_container_applies_003_to_an_existing_database(monkeypatch):
    pool = _Pool(has_result_column=False)
    _patch_adapters(monkeypatch, pool)
    c = await container_module.create_container(Settings())
    assert c.mission_repo is not None
    assert _ran_003(pool)


@pytest.mark.asyncio
async def test_container_skips_003_when_already_applied(monkeypatch):
    pool = _Pool(has_result_column=True)
    _patch_adapters(monkeypatch, pool)
    await container_module.create_container(Settings())
    assert not _ran_003(pool)


@pytest.mark.asyncio
async def test_ensure_result_column_on_real_postgres():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set")
    import asyncpg

    from adapters.postgres.repositories import ensure_mission_result_column

    schema = f"c003_{uuid4().hex[:10]}"
    admin = await asyncpg.connect(url)
    await admin.execute(f"CREATE SCHEMA {schema}")
    await admin.execute(f"CREATE TABLE {schema}.mission_payloads (LIKE public.mission_payloads INCLUDING ALL)")
    await admin.execute(f"ALTER TABLE {schema}.mission_payloads DROP COLUMN IF EXISTS result")
    pool = await asyncpg.create_pool(url, min_size=1, max_size=2, server_settings={"search_path": f"{schema},public"})
    column_sql = (
        "SELECT count(*) FROM information_schema.columns "
        "WHERE table_schema = $1 AND table_name = 'mission_payloads' AND column_name = 'result'"
    )
    try:
        assert await admin.fetchval(column_sql, schema) == 0
        assert await ensure_mission_result_column(pool) is True
        assert await admin.fetchval(column_sql, schema) == 1
        assert await ensure_mission_result_column(pool) is False  # idempotent
    finally:
        await pool.close()
        await admin.execute(f"DROP SCHEMA {schema} CASCADE")
        await admin.close()
