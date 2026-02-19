"""Canonical event envelope for the Synarch nervous system (FR-19, FR-20)."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class EventEnvelope(BaseModel):
    """Every NATS message follows this canonical envelope.
    
    Fields:
        id: Unique event identifier (UUID v4)
        type: Event type from EventTypes taxonomy
        subject: Full NATS subject string
        mission_id: Associated mission UUID
        agent: Source agent name (optional for system events)
        timestamp: UTC timestamp of event creation
        sequence: Monotonic per-mission sequence counter
        schema_version: Event schema version for forward compatibility (FR-19)
        idempotency_key: Dedup key for side-effecting events (FR-14)
        payload: Event-specific data
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    subject: str
    mission_id: str
    agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sequence: int = 0
    schema_version: str = "1.0"
    idempotency_key: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)

    def to_nats_subject(self) -> str:
        """Return the NATS subject for this event."""
        return self.subject

    def to_json_bytes(self) -> bytes:
        """Serialize to JSON bytes for NATS publication."""
        return self.model_dump_json().encode("utf-8")

    @classmethod
    def create(
        cls,
        event_type: str,
        mission_id: str,
        payload: dict[str, Any],
        agent: str | None = None,
        sequence: int = 0,
        idempotency_key: str | None = None,
    ) -> "EventEnvelope":
        """Factory method for creating events with auto-generated subject."""
        # Build NATS subject from event type and identifiers
        parts = ["synarch"]
        if agent:
            parts.extend(["agent", agent, event_type.split(".")[-1]])
        else:
            type_parts = event_type.split(".")
            parts.extend([type_parts[0], mission_id, type_parts[-1]])
        
        return cls(
            type=event_type,
            subject=".".join(parts),
            mission_id=mission_id,
            agent=agent,
            sequence=sequence,
            idempotency_key=idempotency_key,
            payload=payload,
        )
