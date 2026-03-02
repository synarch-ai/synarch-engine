"""Canonical event envelope for the Synarch nervous system (FR-19, FR-20)."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class EventTelemetry(BaseModel):
    """Performance and cost telemetry for an event."""
    cost_usd: float | None = None
    latency_ms: float | None = None
    tokens: int | None = None


class EventEnvelope(BaseModel):
    """Every NATS message follows this canonical envelope.
    
    Fields:
        id: Unique event identifier (UUID v4)
        type: Event type from EventTypes taxonomy
        subject: Full NATS subject string
        mission_id: Associated mission UUID
        agent: Source agent name (optional for system events)
        stage: Mission stage (e.g. 'planning', 'executing')
        timestamp: UTC timestamp of event creation
        sequence: Monotonic per-mission sequence counter (assigned by DB)
        schema_version: Event schema version for forward compatibility (FR-19)
        idempotency_key: Dedup key for side-effecting events (FR-14)
        correlation_id: Trace context ID
        causation_id: Parent event ID
        telemetry: Cost/Performance metrics
        payload: Event-specific data
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    subject: str
    mission_id: str
    agent: Optional[str] = None
    stage: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sequence: int = 0  # Assigned by persistence layer
    schema_version: str = "1.0"
    idempotency_key: Optional[str] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    telemetry: EventTelemetry = Field(default_factory=EventTelemetry)
    payload: dict[str, Any] = Field(default_factory=dict)

    def to_nats_subject(self) -> str:
        """Return the NATS subject for this event."""
        return self.subject

    def to_json_bytes(self) -> bytes:
        """Serialize to JSON bytes for NATS publication."""
        # Use model_dump_json to handle datetime serialization automatically
        json_str = self.model_dump_json()

        # Redact any active secrets before serializing
        from domain.security.secrets import registry
        redacted_json = registry.redact(json_str)

        return redacted_json.encode("utf-8")

    @classmethod
    def create(
        cls,
        event_type: str,
        mission_id: str,
        payload: dict[str, Any],
        agent: str | None = None,
        stage: str | None = None,
        sequence: int = 0,
        idempotency_key: str | None = None,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        telemetry: EventTelemetry | None = None,
    ) -> "EventEnvelope":
        """Factory method for creating events with auto-generated subject."""
        # Build NATS subject from event type and identifiers
        # Pattern: synarch.mission_events.{domain}.{verb} (from Catalog v2.0)
        # However, the catalog example is "synarch.mission_events.mission.created"
        # which aligns with type "mission.created".
        # So we can map type prefix to domain.
        
        # Pattern: synarch.mission_events.{mission_id}.{event_type}
        # This allows filtering by mission_id at the NATS server level
        subject = f"synarch.mission_events.{mission_id}.{event_type}"

        return cls(
            type=event_type,
            subject=subject,
            mission_id=mission_id,
            agent=agent,
            stage=stage,
            sequence=sequence,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
            causation_id=causation_id,
            telemetry=telemetry or EventTelemetry(),
            payload=payload,
        )
