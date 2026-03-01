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
            skip = last_event_id is not None
            for evt in history:
                if skip:
                    if str(evt.id) == last_event_id:
                        skip = False  # Found cursor, yield subsequent events
                    continue

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

        # Subscribe to mission-specific events
        # Subject: synarch.mission_events.{mission_id}.>
        subject = f"synarch.mission_events.{str(mission_id)}.*"
        # Note: Depending on envelope implementation, the subject format might vary.
        # But we updated EventEnvelope.create to use `synarch.mission_events.{event_type}` in previous step (which was flagged as regression).
        # We need to fix EventEnvelope first.
        # BUT assuming we fix EventEnvelope to include mission_id in subject:
        # e.g. synarch.mission_events.{mission_id}.{type}

        # Let's fix the subject subscription to wildcard on mission_id if possible,
        # OR if we reverted to `synarch.mission_events.{type}` we must use `synarch.mission_events.>` and filter.

        # The plan says "Update EventEnvelope.create to include mission_id".
        # So we expect: synarch.mission_events.<mission_id>.<event_type>
        subject = f"synarch.mission_events.{str(mission_id)}.*"

        sub = await self.event_bus.subscribe(subject, handler)

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
            if sub:
                # Assuming event_bus has unsubscribe method now
                if hasattr(self.event_bus, "unsubscribe"):
                    await self.event_bus.unsubscribe(sub)
            pass
