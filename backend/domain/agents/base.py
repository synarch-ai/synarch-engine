"""Base agent node — soul loading and LLM invocation contract (FR-12)."""
import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from domain.events.envelope import EventEnvelope
from domain.events.types import EventTypes
from domain.orchestrator.exceptions import BudgetExceededError
from domain.orchestrator.state import MissionState


class AgentNode(ABC):
    """Base class for all Synarch agents.
    
    Every agent:
    1. Loads its soul.md as system prompt foundation (FR-12)
    2. Invokes an LLM via ModelProviderPort (FR-11)
    3. Emits events via EventBusPort (FR-13)
    4. Returns state updates for LangGraph
    """

    def __init__(
        self,
        name: str,
        model: str,
        soul_path: str,
        model_provider: Any = None,  # ModelProviderPort (injected)
        event_bus: Any = None,       # EventBusPort (injected)
        budget_guard: Any = None,    # Callable(mission_id, agent, model)
    ):
        self.name = name
        self.model = model
        self.soul_path = soul_path
        self.model_provider = model_provider
        self.event_bus = event_bus
        self.budget_guard = budget_guard
        self._soul: str | None = None

    @property
    def soul(self) -> str:
        """Lazily load and cache the soul.md content."""
        if self._soul is None:
            self._soul = self.load_soul()
        return self._soul

    def load_soul(self) -> str:
        """Read the agent's soul.md file (FR-12)."""
        path = Path(self.soul_path) / self.name / "soul.md"
        if not path.exists():
            # Try relative to project root
            path = Path("docs/agents") / self.name / "soul.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"You are {self.name}, an AI agent in the Synarch hierarchy."

    async def invoke_llm(self, messages: list[dict], **kwargs) -> str:
        """Call LLM via ModelProviderPort with soul as system prompt (FR-11)."""
        if self.model_provider is None:
            raise RuntimeError(f"Agent {self.name}: model_provider not injected")

        mission_id = kwargs.pop("mission_id", None)
        if mission_id and self.budget_guard is not None:
            maybe_result = self.budget_guard(
                mission_id=mission_id,
                agent=self.name,
                model=self.model,
            )
            if inspect.isawaitable(maybe_result):
                await maybe_result

        full_messages = [
            {"role": "system", "content": self.soul},
            *messages,
        ]
        return await self.model_provider.invoke(
            model=self.model,
            messages=full_messages,
            **kwargs,
        )

    async def emit_event(
        self,
        event_type: str,
        mission_id: str,
        payload: dict,
        sequence: int = 0,
        idempotency_key: str | None = None,
    ) -> None:
        """Publish event to nervous system (FR-13). Non-blocking on failure."""
        if self.event_bus is None:
            return  # Graceful degradation if event bus not available
        
        event = EventEnvelope.create(
            event_type=event_type,
            mission_id=mission_id,
            agent=self.name,
            payload=payload,
            sequence=sequence,
            idempotency_key=idempotency_key,
        )
        try:
            await self.event_bus.publish(event)
        except Exception:
            # Observation plane failure must not break control plane (ADR-005)
            pass

    @abstractmethod
    async def process(self, state: MissionState) -> dict:
        """Process the current state and return state updates.
        
        This is the LangGraph node function. Must return a partial state dict.
        """
        ...

    async def __call__(self, state: MissionState) -> dict:
        """LangGraph node callable — wraps process with event emission."""
        mission_id = state.get("mission_id", "unknown")
        
        # Emit activation event
        await self.emit_event(
            EventTypes.AGENT_ACTIVATED,
            mission_id,
            {"agent": self.name, "phase": state.get("phase", "")},
        )
        
        try:
            result = await self.process(state)
            
            # Emit deactivation event
            await self.emit_event(
                EventTypes.AGENT_DEACTIVATED,
                mission_id,
                {"agent": self.name},
            )
            
            return result
        except BudgetExceededError as e:
            await self.emit_event(
                EventTypes.AGENT_ERROR,
                mission_id,
                {
                    "agent": self.name,
                    "error": str(e),
                    "error_code": "BUDGET_EXCEEDED",
                },
            )
            raise
        except Exception as e:
            await self.emit_event(
                EventTypes.AGENT_ERROR,
                mission_id,
                {"agent": self.name, "error": str(e)},
            )
            raise
