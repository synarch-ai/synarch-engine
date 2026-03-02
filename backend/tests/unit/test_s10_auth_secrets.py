import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from domain.security.context import get_actor, current_actor
from domain.security.secrets import registry
from api.middleware.auth import AuthMiddleware

@pytest.fixture
def auth_app():
    app = FastAPI()

    @app.get("/secure")
    async def secure_endpoint(request: Request):
        return {"actor": get_actor()}

    @app.get("/health")
    async def health_endpoint():
        return {"status": "ok"}

    return app

def test_auth_middleware_noauth(auth_app):
    auth_app.add_middleware(AuthMiddleware, auth_mode="NOAUTH")
    client = TestClient(auth_app)

    response = client.get("/secure")
    assert response.status_code == 200
    assert response.json() == {"actor": "anonymous"}

def test_auth_middleware_api_key_valid(auth_app):
    auth_app.add_middleware(AuthMiddleware, auth_mode="API_KEY", api_key="secret-key")
    client = TestClient(auth_app)

    response = client.get("/secure", headers={"Authorization": "Bearer secret-key"})
    assert response.status_code == 200
    assert response.json() == {"actor": "api-user"}

def test_auth_middleware_api_key_invalid(auth_app):
    auth_app.add_middleware(AuthMiddleware, auth_mode="API_KEY", api_key="secret-key")
    client = TestClient(auth_app)

    response = client.get("/secure", headers={"Authorization": "Bearer wrong-key"})
    assert response.status_code == 401

def test_auth_middleware_proxy_header(auth_app):
    auth_app.add_middleware(AuthMiddleware, auth_mode="PROXY_HEADER", proxy_header="x-remote-user")
    client = TestClient(auth_app)

    response = client.get("/secure", headers={"x-remote-user": "alice@synarch.ai"})
    assert response.status_code == 200
    assert response.json() == {"actor": "alice@synarch.ai"}

    response = client.get("/secure")
    assert response.status_code == 401

def test_secret_redaction():
    # Register secrets
    registry.register("SUPER_SECRET_TOKEN")
    registry.register("ANOTHER_SECRET")

    # Test text containing both secrets
    text = "The password is SUPER_SECRET_TOKEN, but don't tell anyone ANOTHER_SECRET."
    redacted = registry.redact(text)
    assert redacted == "The password is ***REDACTED***, but don't tell anyone ***REDACTED***."

    # Ensure regular text passes unmodified
    text2 = "No secrets here!"
    assert registry.redact(text2) == text2

    # Test JSON string payload redaction
    import json
    payload = {"mission_id": "123", "github_token": "SUPER_SECRET_TOKEN"}
    json_str = json.dumps(payload)
    redacted_json = registry.redact(json_str)
    assert "***REDACTED***" in redacted_json
    assert "SUPER_SECRET_TOKEN" not in redacted_json

def test_secret_redaction_logging_filter(caplog):
    import logging
    from domain.security.secrets import registry, SecretRedactionFilter

    # 1. Setup
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    filter_instance = SecretRedactionFilter()
    logger.addFilter(filter_instance)

    registry.register("AWS_SECRET_KEY_123")

    # 2. Log a secret
    logger.info("Connecting with key AWS_SECRET_KEY_123 to server")

    # 3. Assert Redaction
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "AWS_SECRET_KEY_123" not in record.getMessage()
    assert "***REDACTED***" in record.getMessage()

    # Clean up
    logger.removeFilter(filter_instance)

def test_secret_redaction_logging_dict_argument(caplog):
    import logging
    from domain.security.secrets import registry, SecretRedactionFilter

    logger = logging.getLogger("test_dict_logger")
    logger.setLevel(logging.INFO)
    filter_instance = SecretRedactionFilter()
    logger.addFilter(filter_instance)

    registry.register("DICT_LOG_SECRET")

    payload = {"user": "bob", "secret": "DICT_LOG_SECRET"}
    logger.info("Handling request with payload: %s", payload)

    assert len(caplog.records) == 1
    msg = caplog.records[0].getMessage()

    assert "DICT_LOG_SECRET" not in msg
    assert "***REDACTED***" in msg
