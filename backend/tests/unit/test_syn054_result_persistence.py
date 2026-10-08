"""SYN-054: final_output / deliverables / messages are persisted and exposed."""
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from config import Settings
from domain.models.mission import AuthorityMode, Mission, MissionStatus
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from tests.integration.test_missions_api import InMemoryMissionRepository as ApiRepo, NoopMissionRuntime, _TestContainer
from tests.unit.test_s02_runtime import (
    FakeCheckpointer, FakeEventBus, FakeModelProvider, FakeRedis, InMemoryMissionRepository,
)


class PromptKeyedProvider(FakeModelProvider):
    """Keys on the user prompt (real souls mention other agents' names)."""

    async def invoke(self, model, messages, **kwargs):
        user = messages[-1]["content"]
        if "The mission is complete" in user:
            return "Final synthesized output."
        return await super().invoke(model, messages, **kwargs)


@pytest.mark.asyncio
async def test_completed_mission_has_retrievable_result():
    repo = InMemoryMissionRepository()
    runtime = MissionOrchestratorRuntime(
        mission_repo=repo, model_provider=PromptKeyedProvider(), event_bus=FakeEventBus(),
        checkpointer=FakeCheckpointer(), redis_client=FakeRedis(),
        settings=Settings(model_call_budget_cap=40, require_durable_checkpointer=False),
    )
    m = Mission(goal="Build API", authority_mode=AuthorityMode.SUPERVISED, status=MissionStatus.CREATED)
    m.thread_id = str(m.id)
    m = await repo.create(m)
    await runtime.run_mission(m.id)

    got = await repo.get(m.id)
    assert got.status == "completed"
    assert got.result["final_output"] == "Final synthesized output."
    assert got.result["deliverables"] and got.result["deliverables"][0]["agent"] == "hephaestus"
    assert got.result["messages"]


def test_state_endpoint_returns_result():
    repo = ApiRepo()
    app = create_app(enable_idempotency=False)
    app.state.container = _TestContainer(mission_repo=repo, mission_runtime=NoopMissionRuntime())
    with TestClient(app) as c:
        mid = c.post("/api/v1/mission/start", json={"goal": "x"}).json()["mission_id"]
        mission = next(iter(repo._missions.values()))
        mission.result = {"final_output": "done", "deliverables": [{"agent": "zeus"}], "messages": [{"m": 1}], "tasks": [{"t": 1}]}
        body = c.get(f"/api/v1/mission/{mid}/state").json()
    assert body["final_output"] == "done"
    assert body["deliverables"] == [{"agent": "zeus"}]
    assert body["messages"] == [{"m": 1}] and body["tasks"] == [{"t": 1}]


@pytest.mark.asyncio
async def test_postgres_roundtrip_result():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set")
    from adapters.postgres.repositories import PostgresMissionRepository, create_postgres_pool
    pool = await create_postgres_pool(url)
    repo = PostgresMissionRepository(pool)
    mid = None
    try:
        async with pool.acquire() as conn:
            await conn.execute((Path(__file__).parents[2] / "adapters/postgres/migrations/003_mission_result.sql").read_text())
        m = Mission(goal="persist result", status=MissionStatus.CREATED)
        m.thread_id = str(m.id)
        m = await repo.create(m)
        mid = m.id
        await repo.patch_payload(mid, result={"final_output": "ok", "deliverables": [{"a": 1}], "messages": [], "tasks": []})
        got = await repo.get(mid)
        assert got.result["final_output"] == "ok"
        assert got.result["deliverables"] == [{"a": 1}]
    finally:
        if mid is not None:
            async with pool.acquire() as conn:
                await conn.execute("DELETE FROM missions WHERE id = $1::uuid", mid)
        await pool.close()
