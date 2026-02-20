"""Abstract checkpointer port — graph state persistence (FR-5, FR-10)."""
from abc import ABC, abstractmethod
from typing import Any


class CheckpointerPort(ABC):
    @abstractmethod
    async def setup(self) -> None:
        """Initialize checkpoint storage (create tables if needed)."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close checkpoint storage connections."""
        ...

    @abstractmethod
    def get_checkpointer(self) -> Any:
        """Return the underlying checkpointer for LangGraph compilation."""
        ...
