"""API-key authentication (SYN-015).

Auth runs as an outermost ASGI middleware (inside CORS only), so it executes
before IdempotencyMiddleware: unauthenticated requests never reach the
idempotency store, are never cached, and can never be served a cached response.

With no ``API_KEY`` configured the API is loopback-only: requests from a
non-loopback client are rejected, and startup refuses a non-loopback bind.
"""
from __future__ import annotations

import hmac
import ipaddress
import json
import os
from collections.abc import Mapping, Sequence
from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}

# Paths under the API prefix that stay open (liveness probes).
PUBLIC_PATHS = {"/api/v1/health"}
PROTECTED_PREFIX = "/api/v1/"


def is_loopback(host: str | None) -> bool:
    if not host:
        return False
    if host == "localhost":
        return True
    try:
        addr = ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
        addr = addr.ipv4_mapped
    return addr.is_loopback


def _extract_key(authorization: str | None, x_api_key: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return x_api_key


def key_matches(provided: str | None, api_key: str) -> bool:
    return bool(provided) and hmac.compare_digest(provided.encode(), api_key.encode())


class ApiKeyMiddleware:
    """Enforce the shared API key on ``/api/v1/*`` (except health) before anything else runs."""

    def __init__(self, app: ASGIApp, api_key: str | None = None) -> None:
        self.app = app
        self.api_key = api_key or None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("method") == "OPTIONS":
            await self.app(scope, receive, send)
            return
        path = scope.get("path", "")
        if not path.startswith(PROTECTED_PREFIX) or path.rstrip("/") in PUBLIC_PATHS:
            await self.app(scope, receive, send)
            return

        headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
        if self.api_key:
            provided = _extract_key(headers.get("authorization"), headers.get("x-api-key"))
            if not key_matches(provided, self.api_key):
                await _reject(scope, send, headers, 401, "UNAUTHORIZED", "Missing or invalid API key.")
                return
        else:
            # No key configured: fail closed for anything that is not a loopback client,
            # whatever launcher or bind address was used (review M2).
            client = scope.get("client")
            if not client or not is_loopback(client[0]):
                await _reject(
                    scope, send, headers, 403, "API_KEY_REQUIRED",
                    "API_KEY is not configured; only loopback clients are allowed.",
                )
                return
        await self.app(scope, receive, send)


async def _reject(scope: Scope, send: Send, headers: Mapping[str, str], status: int, code: str, message: str) -> None:
    request_id = headers.get("x-request-id") or str(uuid4())
    body = json.dumps(
        {"error": {"code": code, "message": message, "details": {}, "request_id": request_id}}
    ).encode()
    response_headers = [
        (b"content-type", b"application/json"),
        (b"content-length", str(len(body)).encode()),
        (b"x-request-id", request_id.encode("latin-1")),
    ]
    if status == 401:
        response_headers.append((b"www-authenticate", b"Bearer"))
    await send({"type": "http.response.start", "status": status, "headers": response_headers})
    await send({"type": "http.response.body", "body": body})


def resolve_bind(host: str, api_key: str | None) -> str:
    """Refuse to bind a non-loopback interface without an API key."""
    if not is_loopback(host) and not api_key:
        raise RuntimeError(
            f"Refusing to bind {host}: set API_KEY (settings.api_key) before exposing the API."
        )
    return host


def cli_bind_host(argv: Sequence[str], environ: Mapping[str, str]) -> str | None:
    """Best-effort: the host passed to the uvicorn CLI (``--host``/``UVICORN_HOST``).

    Returns None when no host was given on the command line or environment
    (uvicorn's own default is 127.0.0.1).
    """
    host: str | None = None
    args = list(argv)
    for i, arg in enumerate(args):
        if arg == "--host" and i + 1 < len(args):
            host = args[i + 1]
        elif arg.startswith("--host="):
            host = arg.split("=", 1)[1]
    if host is None:
        host = environ.get("UVICORN_HOST") or None
    return host


def assert_safe_startup(api_key: str | None, argv: Sequence[str] | None = None, environ: Mapping[str, str] | None = None) -> None:
    """Fail startup when the API would be exposed on a non-loopback bind without a key.

    Covers ``uvicorn main:app --host 0.0.0.0`` (``python main.py`` is covered by
    ``resolve_bind``). Requests from non-loopback clients are additionally
    rejected by ``ApiKeyMiddleware`` for launchers this cannot detect.
    """
    import sys

    if api_key:
        return
    host = cli_bind_host(sys.argv if argv is None else argv, os.environ if environ is None else environ)
    if host is not None:
        resolve_bind(host, api_key)
