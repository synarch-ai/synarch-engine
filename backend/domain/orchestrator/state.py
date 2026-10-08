"""LangGraph mission state schema (FR-6)."""
from typing import TypedDict, List, Optional, Annotated
import operator


def last_value(_old, new):
    """Reducer: last writer wins. Lets parallel branches both set a scalar key."""
    return new


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
    phase: Annotated[str, last_value]  # MissionPhase value
    tasks: Annotated[List[TaskAssignment], operator.add]
    current_agent: Annotated[str, last_value]

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
