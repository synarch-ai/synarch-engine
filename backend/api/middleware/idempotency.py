"""Idempotency middleware for side-effecting API endpoints."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from ports.idempotency import IdempotencyRecord


def _error(request_id: str, code: str, message: str, status_code: int, details: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
                "request_id": request_id,
            }
        },
    )


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Enforce Idempotency-Key semantics for side-effecting requests."""

    def __init__(self, app, ttl_seconds: int = 86400) -> None:
        super().__init__(app)
        self.ttl_seconds = ttl_seconds

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return await call_next(request)
        if not request.url.path.startswith("/api/v1/"):
            return await call_next(request)

        request_id = getattr(request.state, "request_id", str(uuid4()))
        idem_key = request.headers.get("Idempotency-Key")
        if not idem_key:
            return _error(
                request_id=request_id,
                code="IDEMPOTENCY_KEY_REQUIRED",
                message="Idempotency-Key header is required for side-effecting endpoints.",
                status_code=400,
            )

        container = getattr(request.app.state, "container", None)
        repo = getattr(container, "idempotency_repo", None) if container is not None else None

        if repo is None:
            return _error(
                request_id=request_id,
                code="IDEMPOTENCY_STORE_UNAVAILABLE",
                message="Idempotency store is unavailable.",
                status_code=503,
            )

        # Fastapi BaseHTTPMiddleware body consumption fix
        # request.body() consumes the stream. We must store the bytes and
        # override the receive method so downstream endpoints can still read it.
        body_bytes = await request.body()

        async def receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}
        request._receive = receive

        request_hash = hashlib.sha256(body_bytes).hexdigest()
        scope = f"{request.method}:{request.url.path}"

        existing = await repo.get(scope, idem_key)

        if existing is not None:
            if existing.request_hash != request_hash:
                return _error(
                    request_id=request_id,
                    code="IDEMPOTENCY_CONFLICT",
                    message="Idempotency-Key was already used with a different payload.",
                    status_code=409,
                    details={"scope": scope, "idempotency_key": idem_key},
                )
            replay = JSONResponse(status_code=existing.response_status, content=existing.response_body)
            replay.headers["X-Request-Id"] = request_id
            replay.headers["X-Idempotent-Replay"] = "true"
            return replay

        response = await call_next(request)
        raw_body = b""
        if hasattr(response, "body_iterator"):
            async for chunk in response.body_iterator:
                raw_body += chunk
        elif hasattr(response, "body"):
            raw_body = response.body or b""

        try:
            parsed_body: Any = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except Exception:
            parsed_body = {"raw": raw_body.decode("utf-8", errors="replace")}

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds)

        record = IdempotencyRecord(
            scope=scope,
            idempotency_key=idem_key,
            request_hash=request_hash,
            response_status=int(response.status_code),
            response_body=parsed_body,
            expires_at=expires_at
        )
        await repo.save(record)

        proxied = Response(
            content=raw_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
        proxied.headers["X-Request-Id"] = request_id
        return proxied
