import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from domain.events.envelope import EventEnvelope, EventTelemetry
from adapters.postgres.repositories import PostgresEventRepository

def test_event_envelope_creation():
    payload = {"foo": "bar"}
    event = EventEnvelope.create(
        event_type="mission.created",
        mission_id="test-mission-123",
        payload=payload,
        agent="god"
    )

    assert event.type == "mission.created"
    assert event.subject == "synarch.mission_events.mission.created"
    assert event.mission_id == "test-mission-123"
    assert event.agent == "god"
    assert event.payload == payload
    assert event.timestamp is not None
    assert event.id is not None

def test_event_envelope_serialization():
    event = EventEnvelope.create(
        event_type="agent.thinking",
        mission_id="m1",
        payload={"thought": "I am thinking"},
        telemetry=EventTelemetry(tokens=100, latency_ms=50.5)
    )

    json_bytes = event.to_json_bytes()
    data = json.loads(json_bytes)

    assert data["type"] == "agent.thinking"
    assert data["telemetry"]["tokens"] == 100
    assert data["telemetry"]["latency_ms"] == 50.5
    assert data["telemetry"]["cost_usd"] is None

@pytest.mark.asyncio
async def test_event_repo_create():
    pool = MagicMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__.return_value = conn

    # Mock next_mission_sequence
    conn.fetchval.return_value = 42

    repo = PostgresEventRepository(pool)

    event = EventEnvelope.create(
        event_type="mission.started",
        mission_id="m1",
        payload={}
    )

    saved_event = await repo.create(event)

    # Check sequence was assigned
    assert saved_event.sequence == 42

    # Check DB interaction
    conn.fetchval.assert_called_once()
    assert "next_mission_sequence" in conn.fetchval.call_args[0][0]

    conn.execute.assert_called_once()
    args = conn.execute.call_args[0]
    assert "INSERT INTO mission_events" in args[0]
    # Check some values passed to execute
    # (query, id, mission_id, sequence, type, ...)
    assert args[1] == event.id
    assert args[2] == "m1"
    assert args[3] == 42
    assert args[4] == "mission.started"
