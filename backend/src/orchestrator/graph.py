from langgraph.graph import StateGraph, END
from .state import MissionState
from ..agents.synarch import SynarchAgent
from ..agents.zeus import ZeusAgent
from ..agents.thoth import ThothAgent

# Initialize Agents
synarch = SynarchAgent()
zeus = ZeusAgent()
thoth = ThothAgent()

# Define Nodes
async def synarch_node(state: MissionState):
    return await synarch.run(state)

async def zeus_node(state: MissionState):
    return await zeus.run(state)

async def thoth_node(state: MissionState):
    return await thoth.run(state)

# Define Graph
workflow = StateGraph(MissionState)

workflow.add_node("synarch", synarch_node)
workflow.add_node("zeus", zeus_node)
workflow.add_node("thoth", thoth_node)

# Entry Point
workflow.set_entry_point("synarch")

# Edges (Linear flow for PoC v1)
workflow.add_edge("synarch", "zeus")      # CEO delegates to Ops
workflow.add_edge("zeus", "thoth")         # Ops delegates to Research
workflow.add_edge("thoth", END)            # Research ends mission

app_graph = workflow.compile()
