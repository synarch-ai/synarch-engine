"""LangGraph StateGraph definition with conditional routing (FR-6 to FR-10)."""
from langgraph.graph import StateGraph, END

from domain.orchestrator.state import MissionState
from domain.orchestrator.routing import route_after_planning, route_after_review


def build_graph(agent_nodes: dict) -> StateGraph:
    """Build the mission orchestration graph.
    
    Args:
        agent_nodes: Dict mapping node names to async callables.
            Expected keys: synarch, zeus, thoth, hermes, hephaestus, janus, synthesize
    
    Returns:
        Compiled StateGraph ready for checkpointer attachment.
    """
    graph = StateGraph(MissionState)

    # Add agent nodes
    graph.add_node("synarch", agent_nodes["synarch"])
    graph.add_node("zeus", agent_nodes["zeus"])
    graph.add_node("thoth", agent_nodes["thoth"])
    graph.add_node("hermes", agent_nodes["hermes"])
    graph.add_node("hephaestus", agent_nodes["hephaestus"])
    graph.add_node("janus", agent_nodes["janus"])
    graph.add_node("synthesize", agent_nodes["synthesize"])

    # Entry point: Synarch plans and decomposes
    graph.set_entry_point("synarch")

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
        },
    )

    # Synthesis → END
    graph.add_edge("synthesize", END)

    return graph
