import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from adapters.nats.sse_bridge import SSEBridge
from domain.events.envelope import EventEnvelope

@pytest.mark.asyncio
async def test_sse_bridge_replay_and_stream():
    # Mock EventBus
    event_bus = AsyncMock()
    # Mock EventRepo
    event_repo = AsyncMock()

    mission_id = str(uuid4())

    # 1. Setup Historical Events
    hist_event = EventEnvelope.create("mission.created", mission_id, {})
    event_repo.list_by_mission.return_value = [hist_event]

    # 2. Setup Live Events
    live_event = EventEnvelope.create("mission.started", mission_id, {})

    # Use a Queue to capture the handler
    handler_queue = asyncio.Queue()

    async def mock_subscribe(subject, handler):
        await handler_queue.put(handler)
        return MagicMock()

    event_bus.subscribe.side_effect = mock_subscribe

    bridge = SSEBridge(event_bus, event_repo)

    # 3. Consume the stream
    stream = bridge.stream_mission_events(UUID(mission_id))

    # The stream is an async generator.
    # We must iterate it to trigger internal logic.

    # A) Fetch historical event
    # This call enters stream_mission_events, awaits list_by_mission, yields hist_event.
    evt1 = await anext(stream)
    assert evt1.event == "mission.created"

    # B) Trigger subscription
    # After yielding history, the code proceeds to:
    # sub = await self.event_bus.subscribe(...)
    # We need to pump the generator to reach this point.
    # However, 'anext(stream)' blocks waiting for the NEXT yield.
    # The next yield comes from the queue.
    # The queue is populated by the handler.
    # The handler is registered via subscribe.

    # So we call anext(stream) in a background task so it can hit the subscribe await.
    next_event_task = asyncio.create_task(anext(stream))

    # Wait for subscribe to be called and handler to be captured
    # This means the generator has advanced past history and called subscribe
    handler = await asyncio.wait_for(handler_queue.get(), timeout=2.0)

    # Now inject the live event
    await handler(live_event)

    # Now the background task should complete with the live event
    evt2 = await asyncio.wait_for(next_event_task, timeout=2.0)
    assert evt2.event == "mission.started"

    # Verify repo called
    event_repo.list_by_mission.assert_called_once()
