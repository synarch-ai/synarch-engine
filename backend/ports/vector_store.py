"""Abstract vector store port — semantic search interface (Phase 2)."""
from abc import ABC, abstractmethod


class VectorStorePort(ABC):
    @abstractmethod
    async def upsert(self, collection: str, id: str, vector: list[float], payload: dict) -> None: ...

    @abstractmethod
    async def search(self, collection: str, vector: list[float], limit: int = 10) -> list[dict]: ...
