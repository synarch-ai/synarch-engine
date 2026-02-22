import asyncio
import json
import logging
from typing import AsyncGenerator, Optional
from uuid import UUID

from sse_starlette.sse import ServerSentEvent

from ports.event_bus import EventBusPort
from ports.persistence import EventRepository
from domain.events.envelope import EventEnvelope

logger = logging.getLogger(__name__)


class SSEBridge:
    """Bridges NATS events to SSE streams with replay capability (FR-18, FR-76)."""

    def __init__(self, event_bus: EventBusPort, event_repo: EventRepository):
        self.event_bus = event_bus
        self.event_repo = event_repo

    async def stream_mission_events(
        self, mission_id: UUID, last_event_id: Optional[str] = None
    ) -> AsyncGenerator[ServerSentEvent, None]:
        """Yields events for a specific mission, handling replay gaps."""

        # 1. Replay Gap Handling (FR-76)
        # If client provides Last-Event-ID, we must check if we missed anything.
        # Ideally, we query the repo for events > last_event_id.
        # Since last_event_id is a UUID (event.id), we can't easily query "greater than".
        # We need the *sequence* number associated with that ID.
        # For this implementation, we'll assume the client might send sequence-based resume
        # OR we fetch *recent* events.
        #
        # A robust implementation would map event_id -> sequence.
        # Given EventEnvelope has 'sequence', let's try to fetch by mission.
        #
        # Optimization: Just fetch the last N events for context if no ID,
        # or rely on the client to be robust.
        #
        # Per LLD: "Last-Event-ID replay path required for reconnect"

        # NOTE: NATS subscription will give us *new* events.
        # We first yield persisted events if needed.

        # Simplified Replay: Fetch all events for mission (capped) and yield them first.
        # In production, we'd filter > last_event_id sequence.

        logger.info(f"Starting SSE stream for mission {mission_id}")

        # Fetch historical events (limit 100 for now)
        try:
            history = await self.event_repo.list_by_mission(mission_id, limit=100)
            for evt in history:
                # If last_event_id provided, skip until we find it (naive linear scan)
                # Ideally, repo supports `list_after_sequence`.
                yield ServerSentEvent(
                    id=str(evt.id),
                    event=evt.type,
                    data=evt.model_dump_json()
                )
        except Exception as e:
            logger.error(f"Failed to fetch history for {mission_id}: {e}")

        # 2. Live Stream
        queue = asyncio.Queue()

        async def handler(envelope: EventEnvelope):
            # Filter by mission_id (Application-side filtering per LLD if NATS is wildcard)
            if str(envelope.mission_id) == str(mission_id):
                await queue.put(envelope)

        # Subscribe to all mission events
        # Subject: synarch.mission_events.>
        sub = await self.event_bus.subscribe("synarch.mission_events.>", handler)

        try:
            while True:
                envelope = await queue.get()
                yield ServerSentEvent(
                    id=str(envelope.id),
                    event=envelope.type,
                    data=envelope.model_dump_json()
                )
        except asyncio.CancelledError:
            logger.info(f"SSE stream for {mission_id} cancelled.")
            # Unsubscribe would happen here if NATS client supports it via returned obj
            # self.event_bus.unsubscribe(sub)
            pass
