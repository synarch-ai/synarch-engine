"""LangGraph StateGraph definition with conditional routing (FR-6 to FR-10)."""
from langgraph.graph import StateGraph, END
from langgraph.types import Command, interrupt

from domain.orchestrator.state import MissionState
from domain.orchestrator.routing import route_after_planning, route_after_review
from domain.orchestrator.security_node import security_preflight_node


def check_approval(state: MissionState) -> Command:
    """Approval gate node using LangGraph interrupt."""
    # Logic: If approval_request exists in state (populated by agent logic), interrupt.
    # Note: In a real implementation, agents would emit 'tool_calls' that we inspect here.
    # For S06, we assume the agent or a preceding step flagged `approval_pending`.

    # Actually, the requirement is "Sensitive operations generate approval requests".
    # We'll simulate this by checking if the state indicates a pending approval is needed.
    # Or, simpler: Agents return a special flag.

    # Refined approach: If we are in 'AWAITING_APPROVAL' status, we interrupt.
    # But how do we get there?
    # Let's assume an agent sets `status="awaiting_approval"`.

    # However, `interrupt` is best called *inside* the node that wants to do the action,
    # OR we have a dedicated approval node.

    # Let's add a dedicated "approval_gate" node.
    # It checks if the *last message* requests a sensitive tool.
    pass


def build_graph(agent_nodes: dict) -> StateGraph:
    """Build the mission orchestration graph.
    
    Args:
        agent_nodes: Dict mapping node names to async callables.
            Expected keys: synarch, zeus, thoth, hermes, hephaestus, janus, synthesize, fail
    
    Returns:
        Compiled StateGraph ready for checkpointer attachment.
    """
    graph = StateGraph(MissionState)

    # Add security/guardrail nodes
    graph.add_node("security_preflight", security_preflight_node)

    # Add agent nodes
    graph.add_node("synarch", agent_nodes["synarch"])
    graph.add_node("zeus", agent_nodes["zeus"])
    graph.add_node("thoth", agent_nodes["thoth"])
    graph.add_node("hermes", agent_nodes["hermes"])
    graph.add_node("hephaestus", agent_nodes["hephaestus"])
    graph.add_node("janus", agent_nodes["janus"])
    graph.add_node("synthesize", agent_nodes["synthesize"])
    graph.add_node("fail", agent_nodes["fail"])

    # Entry point: Security scan before Synarch plans
    graph.set_entry_point("security_preflight")

    # Simple conditional router for security preflight
    def route_after_security(state: MissionState) -> str:
        error = state.get("error")
        if error and error.startswith("SECURITY_VIOLATION"):
            return "fail"
        return "synarch"

    graph.add_conditional_edges(
        "security_preflight",
        route_after_security,
        {
            "fail": "fail",
            "synarch": "synarch"
        }
    )

    # After planning: conditional routing to Zeus and/or Thoth (FR-7)
    graph.add_conditional_edges(
        "synarch",
        route_after_planning,
        {
            "zeus": "zeus",
            "thoth": "thoth",
        },
    )

    # Zeus delegates to Hephaestus
    graph.add_edge("zeus", "hephaestus")

    # Thoth delegates to Hermes
    graph.add_edge("thoth", "hermes")

    # Specialists converge to Janus review gate
    graph.add_edge("hephaestus", "janus")
    graph.add_edge("hermes", "janus")

    # Janus review: conditional routing (FR-9)
    graph.add_conditional_edges(
        "janus",
        route_after_review,
        {
            "synthesize": "synthesize",
            "revise": "zeus",  # revision loops back to execution
            "fail": "fail",
        },
    )

    # Synthesis → END
    graph.add_edge("synthesize", END)
    graph.add_edge("fail", END)

    return graph
