"""Event type taxonomy for the Synarch nervous system."""


class EventTypes:
    """Canonical event type constants organized by domain."""

    # Mission lifecycle
    MISSION_CREATED = "mission.created"
    MISSION_PLANNED = "mission.planned"
    MISSION_STATE_CHANGED = "mission.state_changed"
    MISSION_COMPLETED = "mission.completed"
    MISSION_FAILED = "mission.failed"
    MISSION_CANCELLED = "mission.cancelled"

    # Agent lifecycle
    AGENT_ACTIVATED = "agent.activated"
    AGENT_THINKING = "agent.thinking"
    AGENT_DELEGATED = "agent.delegated"
    AGENT_RESULT = "agent.result"
    AGENT_ERROR = "agent.error"
    AGENT_DEACTIVATED = "agent.deactivated"

    # Task lifecycle
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_REVISION = "task.revision"

    # Deliverable lifecycle
    DELIVERABLE_CREATED = "deliverable.created"
    DELIVERABLE_REVIEWED = "deliverable.reviewed"
    DELIVERABLE_ACCEPTED = "deliverable.accepted"

    # Approval lifecycle
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_REJECTED = "approval.rejected"
    APPROVAL_TIMED_OUT = "approval.timed_out"
