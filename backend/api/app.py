"""FastAPI application factory."""
from fastapi import FastAPI
from api.routes import missions, agents, health
from api.middleware.cors import add_cors
from api.middleware.errors import SynarchError, synarch_error_handler, generic_error_handler


def create_app(cors_origins: list[str] | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Synarch Engine",
        version="0.1.0",
        description="Autonomous Multi-Agent Orchestration Engine",
    )

    # Middleware
    add_cors(app, cors_origins or ["http://localhost:3000"])

    # Error handlers
    app.add_exception_handler(SynarchError, synarch_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    # Routes
    app.include_router(missions.router, tags=["missions"])
    app.include_router(agents.router, tags=["agents"])
    app.include_router(health.router, tags=["health"])

    return app
