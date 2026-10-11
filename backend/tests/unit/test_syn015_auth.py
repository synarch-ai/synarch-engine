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


# --- review M2: no API_KEY means loopback-only, on every launch path ---------

import os
import subprocess
import sys
from pathlib import Path

from api.security import assert_safe_startup, cli_bind_host, is_loopback


def test_no_key_rejects_non_loopback_client():
    app = create_app(enable_idempotency=False, api_key=None)
    remote = TestClient(app, client=("203.0.113.7", 40000))
    r = remote.get("/api/v1/agents")
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "API_KEY_REQUIRED"
    assert remote.post("/api/v1/mission/start", json={"goal": "x"}).status_code == 403
    assert remote.get("/api/v1/health").status_code == 200


def test_no_key_allows_loopback_clients():
    app = create_app(enable_idempotency=False, api_key=None)
    for host in ("127.0.0.1", "::1", "::ffff:127.0.0.1"):
        assert TestClient(app, client=(host, 40000)).get("/api/v1/agents").status_code == 200


def test_is_loopback():
    assert is_loopback("127.0.0.1") and is_loopback("127.0.0.2") and is_loopback("::1") and is_loopback("localhost")
    assert not is_loopback("0.0.0.0") and not is_loopback("10.0.0.1") and not is_loopback("testclient")
    assert not is_loopback(None) and not is_loopback("")


def test_cli_host_detection():
    assert cli_bind_host(["uvicorn", "main:app", "--host", "0.0.0.0"], {}) == "0.0.0.0"
    assert cli_bind_host(["uvicorn", "main:app", "--host=::"], {}) == "::"
    assert cli_bind_host(["uvicorn", "main:app"], {"UVICORN_HOST": "0.0.0.0"}) == "0.0.0.0"
    assert cli_bind_host(["uvicorn", "main:app"], {}) is None


def test_startup_refuses_public_cli_bind_without_key():
    with pytest.raises(RuntimeError, match="Refusing to bind 0.0.0.0"):
        assert_safe_startup(None, ["uvicorn", "main:app", "--host", "0.0.0.0"], {})
    with pytest.raises(RuntimeError):
        assert_safe_startup(None, ["uvicorn", "main:app"], {"UVICORN_HOST": "0.0.0.0"})
    assert_safe_startup("k", ["uvicorn", "main:app", "--host", "0.0.0.0"], {})
    assert_safe_startup(None, ["uvicorn", "main:app", "--host", "127.0.0.1"], {})
    assert_safe_startup(None, ["uvicorn", "main:app"], {})


def test_uvicorn_cli_public_bind_without_key_exits():
    """End to end: `uvicorn main:app --host 0.0.0.0` without API_KEY fails at startup, before binding."""
    backend = Path(__file__).resolve().parents[2]
    env = {**os.environ, "API_KEY": "", "DATABASE_URL": "postgresql://nobody@127.0.0.1:1/none"}
    env.pop("UVICORN_HOST", None)
    proc = subprocess.run(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "0"],
        cwd=backend, env=env, capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode != 0
    assert "Refusing to bind 0.0.0.0" in proc.stderr + proc.stdout
