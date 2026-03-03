"""LangGraph mission state schema (FR-6)."""
import operator
from typing import Annotated, List, Optional, TypedDict


class TaskAssignment(TypedDict):
    task_id: str
    agent: str
    description: str
    status: str
    result: Optional[str]


class MissionState(TypedDict):
    """Global state flowing through the LangGraph StateGraph."""

    # Identity
    mission_id: str
    goal: str
    authority_mode: str  # "guided", "supervised", "free_rein"

    # Planning
    plan: List[str]
    plan_rationale: str

    # Execution
    phase: str  # MissionPhase value
    tasks: Annotated[List[TaskAssignment], operator.add]
    current_agent: str

    # Communication (append-only via reducer)
    messages: Annotated[List[dict], operator.add]

    # Review
    review_verdict: Optional[str]  # "PASS", "FAIL", "REVISE"
    review_feedback: Optional[str]
    revision_count: int

    # Output
    deliverables: Annotated[List[dict], operator.add]
    final_output: Optional[str]

    # Control
    needs_approval: bool
    approval_request: Optional[dict]
    error: Optional[str]
