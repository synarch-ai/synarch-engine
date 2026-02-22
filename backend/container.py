"""Dependency injection container — wires ports to adapters."""
import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Optional

from config import Settings
from ports.persistence import (
    MissionRepository,
    TaskRepository,
    ApprovalRepository,
    DeliverableRepository,
)
from ports.event_bus import EventBusPort
from ports.model_provider import ModelProviderPort
from ports.checkpointer import CheckpointerPort

logger = logging.getLogger(__name__)


@dataclass
class Container:
    """Application dependency container."""
    event_bus: EventBusPort
    model_provider: ModelProviderPort
    checkpointer: CheckpointerPort
    db_pool: Any  # asyncpg.Pool

    # Repositories
    mission_repo: MissionRepository
    task_repo: TaskRepository
    approval_repo: ApprovalRepository
    deliverable_repo: DeliverableRepository

    # Runtime
    mission_runtime: Any | None = None
    redis_client: Any | None = None


async def create_container(settings: Settings) -> Container:
    """Bootstrap all adapters and wire them into the container."""

    # --- 1. Infrastructure: PostgreSQL Pool ---
    from adapters.postgres.repositories import create_postgres_pool
    db_pool = await create_postgres_pool(settings.database_url)
    logger.info("PostgreSQL pool initialized.")

    # --- 2. Adapters: Repositories ---
    from adapters.postgres.repositories import (
        PostgresMissionRepository,
        PostgresTaskRepository,
        PostgresApprovalRepository,
        PostgresDeliverableRepository,
    )
    mission_repo = PostgresMissionRepository(db_pool)
    task_repo = PostgresTaskRepository(db_pool)
    approval_repo = PostgresApprovalRepository(db_pool)
    deliverable_repo = PostgresDeliverableRepository(db_pool)

    # --- 3. Adapters: Event Bus (NATS) ---
    # Assuming NATS client exists, if not we might need to stub or implement it.
    # The original file had import from adapters.nats.client.
    # Let's check if it exists. If not, we might need a stub or verify Phase 1 scope.
    # Phase 1 is Persistence. Event Bus is Phase 2.
    # But Container needs EventBusPort.
    # I will use a stub if NATS adapter missing, or try to import it.

    try:
        from adapters.nats.client import NATSEventBus
        event_bus = NATSEventBus(url=settings.nats_url)
        await event_bus.connect()
    except ImportError:
        logger.warning("NATS adapter not found, using MockEventBus.")
        from ports.event_bus import EventBusPort
        class MockEventBus(EventBusPort):
            async def connect(self): pass
            async def close(self): pass
            async def publish(self, *args, **kwargs): pass
            async def subscribe(self, *args, **kwargs): pass
        event_bus = MockEventBus()

    # --- 4. Adapters: Model Provider (LiteLLM) ---
    try:
        from adapters.litellm.provider import LiteLLMProvider
        model_provider = LiteLLMProvider()
    except ImportError:
         logger.warning("LiteLLM adapter not found, using MockModelProvider.")
         from ports.model_provider import ModelProviderPort
         class MockModelProvider(ModelProviderPort):
             async def generate(self, *args, **kwargs): return "mock"
         model_provider = MockModelProvider()

    # --- 5. Adapters: Checkpointer (LangGraph) ---
    from adapters.langgraph.checkpointer import LangGraphCheckpointer
    checkpointer = LangGraphCheckpointer(database_url=settings.database_url)
    await checkpointer.setup()

    # --- 6. Runtime: Mission Orchestrator ---
    # This is likely domain logic that needs repositories.
    # We will instantiate it if available.
    mission_runtime = None
    try:
        from domain.orchestrator.runtime import MissionOrchestratorRuntime
        # Assuming runtime accepts repos
        # We need to pass the checkpointer too.
        # This part depends on the Runtime implementation which might be Phase 2.
        # For Phase 1, we just need the persistence layer ready.
        pass
    except ImportError:
        pass

    return Container(
        event_bus=event_bus,
        model_provider=model_provider,
        checkpointer=checkpointer,
        db_pool=db_pool,
        mission_repo=mission_repo,
        task_repo=task_repo,
        approval_repo=approval_repo,
        deliverable_repo=deliverable_repo,
        mission_runtime=mission_runtime,
    )


async def shutdown_container(container: Container) -> None:
    """Gracefully shutdown all adapters."""
    if container.event_bus:
        await container.event_bus.close()
    if container.checkpointer:
        await container.checkpointer.close()
    if container.db_pool:
        await container.db_pool.close()
    logger.info("Container shutdown complete.")
