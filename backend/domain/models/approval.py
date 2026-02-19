"""Domain model: Approval entity (FR-21 to FR-25)."""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    TIMED_OUT = "TIMED_OUT"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Approval(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    mission_id: UUID
    action_type: str
    requested_by: str
    description: str
    risk_level: RiskLevel
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_by: str | None = None
    decision_reason: str | None = None
    timeout_seconds: int = 300  # FR-25
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    decided_at: datetime | None = None
