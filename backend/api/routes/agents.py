"""Agent API routes."""
from pathlib import Path
from fastapi import APIRouter

from api.middleware.errors import SynarchError
from config import get_settings

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
        raise SynarchError("AGENT_NOT_FOUND", f"Agent '{name}' not found.", status_code=404)

    soul_path = Path(get_settings().souls_dir) / name / "soul.md"
    if soul_path.exists():
        content = soul_path.read_text(encoding="utf-8")
        return {"agent": name, "soul": content}
    raise SynarchError("SOUL_NOT_FOUND", f"Soul file not found for {name}.", status_code=404)
