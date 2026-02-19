"""Abstract event bus port — publish/subscribe interface (FR-16)."""
from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable

from domain.events.envelope import EventEnvelope


class EventBusPort(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def publish(self, event: EventEnvelope) -> None: ...

    @abstractmethod
    async def subscribe(self, subject: str, callback: Callable[[EventEnvelope], Awaitable[None]]) -> Any: ...

    @abstractmethod
    async def close(self) -> None: ...
