from typing import Any, Dict

from domain.orchestrator.state import MissionState
from domain.security.guardrails import InjectionScanner


async def security_preflight_node(state: MissionState) -> Dict[str, Any]:
    """
    Scans the latest inputs in the state for prompt injection (FR-54).
    If malicious, fails the mission.
    """
    # Assuming 'messages' contains the user inputs or latest tool outputs
    if not state.get("messages"):
        return state

    latest_msg = state["messages"][-1]
    content = ""
    if isinstance(latest_msg, dict):
        content = latest_msg.get("content", "")
    elif hasattr(latest_msg, "content"):
        content = latest_msg.content

    if not InjectionScanner.scan(content):
        return {
            "error": "SECURITY_VIOLATION: Prompt injection detected in input.",
            "phase": "failed"
        }

    return {}
