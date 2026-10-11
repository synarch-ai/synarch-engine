"""Synarch Engine — Application bootstrap."""
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn

# Add backend/ to Python path for clean imports
sys.path.insert(0, ".")

from config import get_settings
from container import create_container, shutdown_container
from api.app import create_app
from api.security import assert_safe_startup, resolve_bind

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","component":"%(name)s","message":"%(message)s"}',
)
logger = logging.getLogger("synarch")

# Global container reference
_container = None


@asynccontextmanager
async def lifespan(app):
    """Application lifespan — bootstrap and shutdown."""
    global _container
    settings = get_settings()
    logger.info("Starting Synarch Engine v%s", settings.app_version)
    # Fail before touching any adapter if `uvicorn main:app --host <public>` is used without API_KEY.
    assert_safe_startup(settings.api_key or None)
    if not settings.api_key:
        logger.warning("API_KEY is not set: the API only accepts requests from loopback clients.")

    # Bootstrap DI container
    _container = await create_container(settings)
    app.state.container = _container
    logger.info("All adapters initialized. Synarch Engine ready.")

    yield

    # Shutdown
    if _container:
        await shutdown_container(_container)
    app.state.container = None
    logger.info("Synarch Engine shutdown complete.")


# Create app with lifespan
settings = get_settings()
app = create_app(
    cors_origins=settings.cors_origins,
    enable_idempotency=settings.enable_idempotency_middleware,
    idempotency_ttl_seconds=settings.idempotency_ttl_seconds,
    api_key=settings.api_key or None,
)
app.router.lifespan_context = lifespan


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=resolve_bind(settings.host, settings.api_key or None),
        port=settings.port,
        reload=settings.reload,
    )
