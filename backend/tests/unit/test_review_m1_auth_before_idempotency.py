"""Review M1: auth runs before IdempotencyMiddleware (idempotency ON)."""
from dataclasses import dataclass
from typing import Any

from fastapi.testclient import TestClient

from api.app import create_app
from tests.integration.test_missions_api import InMemoryMissionRepository, NoopMissionRuntime


class FakeIdemConn:
    def __init__(self, store: dict) -> None:
        self.store = store

    async def fetchrow(self, query: str, scope: str, key: str):
        return self.store.get((scope, key))

    async def execute(self, query: str, scope, key, request_hash, status, body, expires_at):
        import json
        self.store.setdefault(
            (scope, key),
            {"request_hash": request_hash, "response_status": status, "response_body": json.loads(body)},
        )


class FakePool:
    def __init__(self) -> None:
        self.store: dict[Any, dict] = {}

    def acquire(self):
        pool = self

        class _Ctx:
            async def __aenter__(self):
                return FakeIdemConn(pool.store)

            async def __aexit__(self, *exc):
                return False

        return _Ctx()


@dataclass
class _Container:
    mission_repo: Any
    mission_runtime: Any
    db_pool: Any


def _client(api_key="s3cret"):
    pool = FakePool()
    app = create_app(enable_idempotency=True, api_key=api_key)
    app.state.container = _Container(InMemoryMissionRepository(), NoopMissionRuntime(), pool)
    return TestClient(app, client=("127.0.0.1", 50000)), pool


GOOD = {"X-API-Key": "s3cret"}


def test_unauthenticated_request_is_not_cached_and_retry_with_key_executes():
    c, pool = _client()
    r1 = c.post("/api/v1/mission/start", json={"goal": "x"}, headers={"Idempotency-Key": "K"})
    assert r1.status_code == 401
    assert pool.store == {}  # no idempotency row written for an unauthenticated caller

    r2 = c.post("/api/v1/mission/start", json={"goal": "x"}, headers={"Idempotency-Key": "K", **GOOD})
    assert r2.status_code == 201
    assert "X-Idempotent-Replay" not in r2.headers


def test_cached_response_is_not_replayed_to_unauthenticated_caller():
    c, pool = _client()
    r1 = c.post("/api/v1/mission/start", json={"goal": "x"}, headers={"Idempotency-Key": "K2", **GOOD})
    assert r1.status_code == 201
    assert pool.store  # stored for the authenticated caller

    r2 = c.post("/api/v1/mission/start", json={"goal": "x"}, headers={"Idempotency-Key": "K2"})
    assert r2.status_code == 401
    assert "mission_id" not in r2.text
    assert "X-Idempotent-Replay" not in r2.headers

    r3 = c.post("/api/v1/mission/start", json={"goal": "x"}, headers={"Idempotency-Key": "K2", **GOOD})
    assert r3.status_code == 201 and r3.headers.get("X-Idempotent-Replay") == "true"


def test_idempotency_never_stores_auth_failures_from_inner_app():
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    from api.middleware.idempotency import IdempotencyMiddleware

    pool = FakePool()
    inner = FastAPI()

    @inner.post("/api/v1/thing")
    async def thing():
        return JSONResponse({"error": "nope"}, status_code=403)

    inner.add_middleware(IdempotencyMiddleware)
    inner.state.container = _Container(None, None, pool)
    r = TestClient(inner).post("/api/v1/thing", json={}, headers={"Idempotency-Key": "K3"})
    assert r.status_code == 403
    assert pool.store == {}
