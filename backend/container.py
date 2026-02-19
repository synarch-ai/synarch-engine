"""Dependency injection container — wires ports to adapters."""
import logging
from dataclasses import dataclass
from typing import Optional

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
    # Repositories will be added in Milestone A when PostgreSQL adapter is implemented
    # mission_repo: MissionRepository
    # task_repo: TaskRepository
    # approval_repo: ApprovalRepository
    # deliverable_repo: DeliverableRepository


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

    logger.info("Container created with all adapters.")
    return Container(
        event_bus=event_bus,
        model_provider=model_provider,
        checkpointer=checkpointer,
    )


async def shutdown_container(container: Container) -> None:
    """Gracefully shutdown all adapters."""
    await container.event_bus.close()
    logger.info("Container shutdown complete.")
