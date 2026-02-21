"""Dependency injection container — wires ports to adapters."""
import asyncio
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
    mission_runtime: Any | None = None
    redis_client: Any | None = None
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
    await checkpointer.setup()

    # --- Redis (Distributed budget guard / coordination) ---
    from redis.asyncio import Redis

    redis_client = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    await redis_client.ping()

    # --- PostgreSQL Repositories ---
    db_pool: Any | None = None
    mission_repo: MissionRepository | None = None
    mission_runtime: Any | None = None
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

    if mission_repo is not None:
        from domain.orchestrator.runtime import MissionOrchestratorRuntime

        mission_runtime = MissionOrchestratorRuntime(
            mission_repo=mission_repo,
            model_provider=model_provider,
            event_bus=event_bus,
            checkpointer=checkpointer,
            redis_client=redis_client,
            settings=settings,
        )
        await mission_runtime.resume_inflight_missions()
        logger.info("Mission runtime initialized.")

    logger.info("Container created with all adapters.")
    return Container(
        event_bus=event_bus,
        model_provider=model_provider,
        checkpointer=checkpointer,
        mission_runtime=mission_runtime,
        redis_client=redis_client,
        mission_repo=mission_repo,
        db_pool=db_pool,
    )


async def shutdown_container(container: Container) -> None:
    """Gracefully shutdown all adapters."""
    await asyncio.wait_for(container.event_bus.close(), timeout=10)
    await asyncio.wait_for(container.checkpointer.close(), timeout=10)
    if container.redis_client is not None:
        await asyncio.wait_for(container.redis_client.aclose(), timeout=10)
    if container.db_pool is not None:
        await asyncio.wait_for(container.db_pool.close(), timeout=10)
    logger.info("Container shutdown complete.")
