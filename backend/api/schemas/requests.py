"""API request schemas."""
from pydantic import BaseModel, Field


class MissionStartRequest(BaseModel):
    goal: str = Field(..., min_length=1, description="Natural language mission goal")
    authority_mode: str = Field(default="supervised", description="guided | supervised | free_rein")


class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="approve | reject")
    reason: str | None = Field(default=None, description="Optional explanation")
