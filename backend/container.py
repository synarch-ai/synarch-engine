"""Dependency injection container — wires ports to adapters."""
import logging
from dataclasses import dataclass
from typing import Any

from config import Settings
from ports.persistence import MissionRepository, TaskRepository, ApprovalRepository, DeliverableRepository
from ports.event_bus import EventBusPort
from ports.model_provider import ModelProviderPort
from ports.checkpointer import CheckpointerPort

logger = logging.getLogger(__name__)


@dataclass
class Container:
    """Application dependency container.
    
    Holds all port implementations (adapters) for dependency injection.
    Created once at startup, passed to API routes via FastAPI dependencies.
    """
    event_bus: EventBusPort
    model_provider: ModelProviderPort
    checkpointer: CheckpointerPort
    mission_repo: MissionRepository | None = None
    task_repo: TaskRepository | None = None
    approval_repo: ApprovalRepository | None = None
    deliverable_repo: DeliverableRepository | None = None
    db_pool: Any | None = None


async def create_container(settings: Settings) -> Container:
    """Bootstrap all adapters and wire them into the container."""

    # --- Event Bus (NATS) ---
    from adapters.nats.client import NATSEventBus
    event_bus = NATSEventBus(url=settings.nats_url)
    await event_bus.connect()

    # --- Model Provider (litellm) ---
    from adapters.litellm.provider import LiteLLMProvider
    model_provider = LiteLLMProvider()

    # --- Checkpointer (LangGraph + PostgreSQL) ---
    from adapters.langgraph.checkpointer import LangGraphCheckpointer
    checkpointer = LangGraphCheckpointer(database_url=settings.database_url)
    try:
        await checkpointer.setup()
    except Exception as e:
        logger.warning("Checkpointer setup failed (PostgreSQL may not be running): %s", e)

    # --- PostgreSQL Repositories ---
    db_pool: Any | None = None
    mission_repo: MissionRepository | None = None
    try:
        from adapters.postgres.repositories import (
            PostgresMissionRepository,
            create_postgres_pool,
        )

        db_pool = await create_postgres_pool(settings.database_url)
        mission_repo = PostgresMissionRepository(db_pool)
        logger.info("PostgreSQL mission repository initialized.")
    except Exception as e:
        logger.warning("PostgreSQL repository setup failed: %s", e)

    logger.info("Container created with all adapters.")
    return Container(
        event_bus=event_bus,
        model_provider=model_provider,
        checkpointer=checkpointer,
        mission_repo=mission_repo,
        db_pool=db_pool,
    )


async def shutdown_container(container: Container) -> None:
    """Gracefully shutdown all adapters."""
    await container.event_bus.close()
    await container.checkpointer.close()
    if container.db_pool is not None:
        await container.db_pool.close()
    logger.info("Container shutdown complete.")
