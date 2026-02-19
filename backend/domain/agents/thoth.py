"""Thoth — CRO Agent (Tier 2): Knowledge keeping and research planning."""
from domain.agents.base import AgentNode
from domain.orchestrator.state import MissionState
from domain.events.types import EventTypes


class ThothAgent(AgentNode):
    """Knowledge keeper. Plans research and delegates to Hermes."""

    async def process(self, state: MissionState) -> dict:
        mission_id = state["mission_id"]
        plan = state.get("plan", [])
        research_tasks = [t for t in plan if any(k in t.lower() for k in ("research", "investigate", "analyze", "compare"))]

        if not research_tasks:
            research_tasks = plan[:1]

        prompt = (
            f"You are Thoth, CRO of the Synarch hierarchy.\n\n"
            f"RESEARCH TASKS:\n" + "\n".join(f"- {t}" for t in research_tasks) + "\n\n"
            f"Create a research plan. Specify what information to find and from what sources."
        )

        response = await self.invoke_llm([{"role": "user", "content": prompt}])

        await self.emit_event(
            EventTypes.AGENT_DELEGATED,
            mission_id,
            {"delegate_to": "hermes", "tasks": research_tasks},
        )

        tasks = [{"task_id": f"res-{i}", "agent": "hermes", "description": t, "status": "PENDING", "result": None} for i, t in enumerate(research_tasks)]

        return {
            "current_agent": "thoth",
            "tasks": tasks,
            "messages": [{"agent": "thoth", "role": "delegation", "content": response, "timestamp": "", "metadata": {}}],
        }
