"""Domain model: Approval entity (FR-21 to FR-25)."""
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


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
