"""SSE bridge — streams NATS events to HTTP clients via Server-Sent Events (FR-18)."""
import asyncio
import json
import logging
from typing import AsyncGenerator

from adapters.nats.client import NATSEventBus
from domain.events.envelope import EventEnvelope

logger = logging.getLogger(__name__)


async def sse_event_generator(
    event_bus: NATSEventBus,
    mission_id: str,
) -> AsyncGenerator[str, None]:
    """Subscribe to NATS events for a mission and yield SSE-formatted strings.

    Usage in FastAPI:
        return EventSourceResponse(sse_event_generator(event_bus, mission_id))
    """
    queue: asyncio.Queue[EventEnvelope] = asyncio.Queue()

    async def _enqueue(event: EventEnvelope) -> None:
        await queue.put(event)

    # Subscribe to all events for this mission via wildcard
    subject = f"synarch.*.{mission_id}.>"
    sub = await event_bus.subscribe(subject, _enqueue)

    # Also subscribe to agent events (different subject pattern)
    agent_subject = "synarch.agent.>"
    agent_sub = await event_bus.subscribe(agent_subject, _enqueue)

    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                # Filter to only this mission's events
                if event.mission_id == mission_id:
                    sse_data = event.model_dump_json()
                    yield f"event: {event.type}\ndata: {sse_data}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive comment to prevent connection timeout
                yield ": keepalive\n\n"
    except asyncio.CancelledError:
        logger.info("SSE stream cancelled for mission %s", mission_id)
    finally:
        if sub:
            await sub.unsubscribe()
        if agent_sub:
            await agent_sub.unsubscribe()
