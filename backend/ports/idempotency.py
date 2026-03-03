from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class IdempotencyRecord:
    def __init__(self, scope: str, idempotency_key: str, request_hash: str, response_status: int, response_body: Dict[str, Any], expires_at: datetime):
        self.scope = scope
        self.idempotency_key = idempotency_key
        self.request_hash = request_hash
        self.response_status = response_status
        self.response_body = response_body
        self.expires_at = expires_at

class IdempotencyRepository(ABC):
    @abstractmethod
    async def get(self, scope: str, idempotency_key: str) -> Optional[IdempotencyRecord]:
        """Get an unexpired idempotency record."""
        ...

    @abstractmethod
    async def save(self, record: IdempotencyRecord) -> None:
        """Save a new idempotency record. Should ignore if already exists (ON CONFLICT DO NOTHING)."""
        ...
