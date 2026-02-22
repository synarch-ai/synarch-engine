import pytest
from domain.events.envelope import EventEnvelope

def test_event_envelope_subject_format():
    event = EventEnvelope.create(
        event_type="mission.created",
        mission_id="m123",
        payload={}
    )

    # Verify subject includes mission_id for filtering
    assert event.subject == "synarch.mission_events.m123.mission.created"
    assert event.mission_id == "m123"
