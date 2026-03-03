"""Agent API routes."""
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

AGENTS = ["synarch", "zeus", "thoth", "hermes", "hephaestus", "janus"]


@router.get("/agents")
async def list_agents():
    """List all agent definitions."""
    return {
        "agents": [
            {"name": name, "soul_url": f"/agents/{name}/soul"}
            for name in AGENTS
        ]
    }


@router.get("/agents/{name}/soul")
async def get_agent_soul(name: str):
    """Get agent's soul.md content (FR-12)."""
    if name not in AGENTS:
        return {"error": f"Agent '{name}' not found"}, 404
    
    soul_path = Path("docs/agents") / name / "soul.md"
    if soul_path.exists():
        content = soul_path.read_text(encoding="utf-8")
        return {"agent": name, "soul": content}
    return {"agent": name, "soul": f"Soul file not found for {name}"}
