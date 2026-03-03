import hashlib
import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from api.middleware.idempotency import IdempotencyMiddleware
from ports.idempotency import IdempotencyRecord
from tests.fakes.idempotency import FakeIdempotencyRepository


class MockRequest:
    def __init__(self, method, path, headers, body_bytes):
        self.method = method
        self.url = MagicMock()
        self.url.path = path
        self.headers = headers
        self._body_bytes = body_bytes
        self.state = MagicMock()
        self.state.request_id = "req-123"
        self.app = MagicMock()
        self.app.state.container = MagicMock()

    async def body(self):
        return self._body_bytes

class MockResponse:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.body = content
        self.headers = {}
        self.media_type = "application/json"

@pytest.mark.asyncio
async def test_idempotency_middleware_first_request():
    app = MagicMock()
    middleware = IdempotencyMiddleware(app)

    repo = FakeIdempotencyRepository()

    request = MockRequest(
        method="POST",
        path="/api/v1/test",
        headers={"Idempotency-Key": "idem-123"},
        body_bytes=b'{"foo": "bar"}'
    )
    request.app.state.container.idempotency_repo = repo

    mock_response = MockResponse(201, b'{"result": "ok"}')
    async def call_next(req):
        return mock_response

    # Execute
    res = await middleware.dispatch(request, call_next)

    # Assert
    assert res.status_code == 201

    # Check if saved to repo
    scope = "POST:/api/v1/test"
    record = await repo.get(scope, "idem-123")
    assert record is not None
    assert record.response_status == 201
    assert record.response_body == {"result": "ok"}

@pytest.mark.asyncio
async def test_idempotency_middleware_replay():
    app = MagicMock()
    middleware = IdempotencyMiddleware(app)
    repo = FakeIdempotencyRepository()

    scope = "POST:/api/v1/test"
    body_bytes = b'{"foo": "bar"}'
    request_hash = hashlib.sha256(body_bytes).hexdigest()

    # Pre-populate repo
    repo.records[(scope, "idem-123")] = IdempotencyRecord(
        scope=scope,
        idempotency_key="idem-123",
        request_hash=request_hash,
        response_status=201,
        response_body={"cached": "yes"},
        expires_at=datetime.now(timezone.utc) + timedelta(days=1)
    )

    request = MockRequest(
        method="POST",
        path="/api/v1/test",
        headers={"Idempotency-Key": "idem-123"},
        body_bytes=body_bytes
    )
    request.app.state.container.idempotency_repo = repo

    call_next = AsyncMock() # Should not be called

    # Execute
    res = await middleware.dispatch(request, call_next)

    # Assert Replay
    assert res.status_code == 201
    import json
    assert json.loads(res.body.decode()) == {"cached": "yes"}
    assert res.headers["X-Idempotent-Replay"] == "true"
    call_next.assert_not_called()

@pytest.mark.asyncio
async def test_idempotency_middleware_conflict():
    app = MagicMock()
    middleware = IdempotencyMiddleware(app)
    repo = FakeIdempotencyRepository()

    scope = "POST:/api/v1/test"
    body_bytes_orig = b'{"foo": "bar"}'
    request_hash_orig = hashlib.sha256(body_bytes_orig).hexdigest()

    # Pre-populate repo
    repo.records[(scope, "idem-123")] = IdempotencyRecord(
        scope=scope,
        idempotency_key="idem-123",
        request_hash=request_hash_orig,
        response_status=201,
        response_body={"cached": "yes"},
        expires_at=datetime.now(timezone.utc) + timedelta(days=1)
    )

    # Request with same key but DIFFERENT body
    request = MockRequest(
        method="POST",
        path="/api/v1/test",
        headers={"Idempotency-Key": "idem-123"},
        body_bytes=b'{"foo": "DIFFERENT"}'
    )
    request.app.state.container.idempotency_repo = repo

    call_next = AsyncMock()

    # Execute
    res = await middleware.dispatch(request, call_next)

    # Assert Conflict
    assert res.status_code == 409
    import json
    error = json.loads(res.body.decode())["error"]
    assert error["code"] == "IDEMPOTENCY_CONFLICT"
    call_next.assert_not_called()
