"""SYN-015: API key dependency + loopback-by-default bind."""
import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.security import resolve_bind
from config import Settings


def _client(api_key):
    return TestClient(create_app(enable_idempotency=False, api_key=api_key))


def test_protected_routes_reject_missing_and_wrong_key():
    c = _client("s3cret")
    assert c.get("/api/v1/agents").status_code == 401
    assert c.get("/api/v1/agents", headers={"X-API-Key": "nope"}).status_code == 401
    assert c.get("/api/v1/missions").status_code == 401
    assert c.post("/api/v1/mission/start", json={"goal": "x"}).status_code == 401
    assert c.get("/api/v1/metrics/daily").status_code == 401


def test_valid_key_via_header_or_bearer():
    c = _client("s3cret")
    assert c.get("/api/v1/agents", headers={"X-API-Key": "s3cret"}).status_code == 200
    assert c.get("/api/v1/agents", headers={"Authorization": "Bearer s3cret"}).status_code == 200


def test_health_stays_open():
    assert _client("s3cret").get("/api/v1/health").status_code == 200


def test_default_bind_is_loopback_without_reload():
    s = Settings()
    assert s.host == "127.0.0.1"
    assert s.reload is False


def test_non_loopback_bind_requires_key():
    assert resolve_bind("127.0.0.1", None) == "127.0.0.1"
    with pytest.raises(RuntimeError):
        resolve_bind("0.0.0.0", None)
    assert resolve_bind("0.0.0.0", "k") == "0.0.0.0"
