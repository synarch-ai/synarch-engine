from typing import List, Any, Dict
import os
# from litellm import completion # Commented out until litellm is configured
from ..orchestrator.state import MissionState

class AgentNode:
    """
    Base class for all Synarch Agents.
    Wraps the logic of loading a 'Soul', interacting with the LLM via litellm,
    and publishing events to NATS.
    """
    def __init__(self, soul_path: str, model: str, tools: List[Any] = []):
        self.soul_path = soul_path
        self.model = model
        self.tools = tools
        self.system_prompt = self._load_soul()

    def _load_soul(self) -> str:
        """
        Reads the soul.md file to establish the agent's persona and system prompt.
        """
        try:
            # Assuming soul_path is relative to the project root or a known location
            # For PoC, we might need to adjust this path resolution
            with open(self.soul_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Soul file not found at {self.soul_path}. Using default.")
            return "You are a helpful AI assistant."

    async def run(self, state: MissionState) -> Dict:
        """
        Core execution loop for the agent.
        1. Build Prompt (System + State)
        2. Call LLM (litellm)
        3. Publish Events (NATS) - TODO
        4. Return State Update
        """
        print(f"[{self.__class__.__name__}] Running with model {self.model}...")

        # Placeholder for LLM call
        # response = completion(model=self.model, messages=[...])

        # Placeholder logic
        return {"logs": [{"agent": self.__class__.__name__, "message": "Executed successfully.", "timestamp": "now"}]}
