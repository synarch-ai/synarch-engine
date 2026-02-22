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

    # Use a Queue to control the mock subscription flow
    handler_queue = asyncio.Queue()

    async def mock_subscribe(subject, handler):
        # Verify new subject format with mission_id wildcard
        assert subject == f"synarch.mission_events.{mission_id}.*"
        await handler_queue.put(handler)
        return MagicMock()

    event_bus.subscribe.side_effect = mock_subscribe

    bridge = SSEBridge(event_bus, event_repo)

    # 3. Consume the stream
    stream = bridge.stream_mission_events(UUID(mission_id))

    # Fetch historical event
    evt1 = await anext(stream)
    assert evt1.event == "mission.created"

    # Trigger live event injection
    next_event_task = asyncio.create_task(anext(stream))
    handler = await asyncio.wait_for(handler_queue.get(), timeout=2.0)
    await handler(live_event)

    # Fetch live event
    evt2 = await asyncio.wait_for(next_event_task, timeout=2.0)
    assert evt2.event == "mission.started"
