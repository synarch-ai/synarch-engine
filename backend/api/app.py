"""FastAPI application factory."""
import os

from fastapi import FastAPI

from api.middleware.auth import AuthMiddleware
from api.middleware.cors import add_cors
from api.middleware.errors import SynarchError, generic_error_handler, synarch_error_handler
from api.middleware.idempotency import IdempotencyMiddleware
from api.middleware.request_id import RequestIdMiddleware
from api.routes import agents, approvals, health, missions
from domain.security.secrets import setup_global_log_redaction


def create_app(
    cors_origins: list[str] | None = None,
    *,
    enable_idempotency: bool = True,
    idempotency_ttl_seconds: int = 86400,
) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Synarch Engine",
        version="0.1.0",
        description="Autonomous Multi-Agent Orchestration Engine",
    )

    # Set up global log redaction
    setup_global_log_redaction()

    # Middleware
    # Order matters: RequestId -> Auth -> Idempotency -> CORS
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        AuthMiddleware,
        auth_mode=os.getenv("AUTH_MODE", "NOAUTH"),
        api_key=os.getenv("API_KEY", None),
        proxy_header=os.getenv("PROXY_HEADER", "x-synarch-user")
    )
    if enable_idempotency:
        app.add_middleware(IdempotencyMiddleware, ttl_seconds=idempotency_ttl_seconds)
    add_cors(app, cors_origins or ["http://localhost:3000"])

    # Error handlers
    app.add_exception_handler(SynarchError, synarch_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    # Routes
    app.include_router(missions.router, tags=["missions"], prefix="/api/v1")
    app.include_router(agents.router, tags=["agents"], prefix="/api/v1")
    app.include_router(health.router, tags=["health"], prefix="/api/v1")
    app.include_router(approvals.router, tags=["approvals"], prefix="/api/v1")

    return app
