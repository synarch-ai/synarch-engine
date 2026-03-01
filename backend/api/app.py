"""FastAPI application factory."""
from fastapi import FastAPI
from api.routes import missions, agents, health, approvals
from api.middleware.cors import add_cors
from api.middleware.request_id import RequestIdMiddleware
from api.middleware.idempotency import IdempotencyMiddleware
from api.middleware.errors import SynarchError, synarch_error_handler, generic_error_handler


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

    # Middleware
    app.add_middleware(RequestIdMiddleware)
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
