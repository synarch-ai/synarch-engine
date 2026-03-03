from typing import Optional

from pydantic import BaseModel

from domain.models.approval import RiskLevel


class CreateApprovalRequest(BaseModel):
    action_type: str
    description: str
    risk_level: RiskLevel

class DecideApprovalRequest(BaseModel):
    decision: str
    reason: Optional[str] = None
    decided_by: str = "operator"
