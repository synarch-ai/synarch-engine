"""Zeus — CTO Agent (Tier 2): Engineering command and delegation."""
from domain.agents.base import AgentNode
from domain.events.types import EventTypes
from domain.orchestrator.state import MissionState


class ZeusAgent(AgentNode):
    """Engineering commander. Creates technical plans and delegates to Hephaestus."""

    async def process(self, state: MissionState) -> dict:
        mission_id = state["mission_id"]
        plan = state.get("plan", [])
        engineering_tasks = [t for t in plan if any(k in t.lower() for k in ("engineer", "code", "implement", "build"))]

        if not engineering_tasks:
            engineering_tasks = plan[:1]  # fallback

        prompt = (
            "You are Zeus, CTO of the Synarch hierarchy.\n\n"
            "ENGINEERING TASKS:\n" + "\n".join(f"- {t}" for t in engineering_tasks) + "\n\n"
            "Create a technical implementation plan. Be specific about what code to write."
        )

        response = await self.invoke_llm(
            [{"role": "user", "content": prompt}],
            mission_id=mission_id,
        )

        await self.emit_event(
            EventTypes.AGENT_DELEGATED,
            mission_id,
            {"delegate_to": "hephaestus", "tasks": engineering_tasks},
        )

        tasks = [{"task_id": f"eng-{i}", "agent": "hephaestus", "description": t, "status": "pending", "result": None} for i, t in enumerate(engineering_tasks)]

        return {
            "current_agent": "zeus",
            "tasks": tasks,
            "messages": [{"agent": "zeus", "role": "delegation", "content": response, "timestamp": "", "metadata": {}}],
        }
