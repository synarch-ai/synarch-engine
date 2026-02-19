"""Abstract model provider port — LLM invocation interface (FR-11)."""
from abc import ABC, abstractmethod


class ModelProviderPort(ABC):
    @abstractmethod
    async def invoke(
        self,
        model: str,
        messages: list[dict],
        **kwargs,
    ) -> str:
        """Call an LLM and return the response content string."""
        ...
