"""Domain model: Deliverable entity with provenance tracking."""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class DeliverableType(str, Enum):
    RESEARCH_REPORT = "research_report"
    CODE = "code"
    REVIEW_VERDICT = "review_verdict"
    SYNTHESIS = "synthesis"


class ReviewStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"


class Deliverable(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    mission_id: UUID
    task_id: UUID | None = None
    agent: str
    type: DeliverableType
    content: dict
    review_status: ReviewStatus = ReviewStatus.PENDING_REVIEW
    provenance_refs: list[str] = Field(default_factory=list)  # FR-20
    created_at: datetime = Field(default_factory=datetime.utcnow)
