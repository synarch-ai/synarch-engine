from datetime import datetime, timezone
from typing import Dict, Optional

from ports.idempotency import IdempotencyRecord, IdempotencyRepository


class FakeIdempotencyRepository(IdempotencyRepository):
    def __init__(self):
        # Key: (scope, idempotency_key) -> Record
        self.records: Dict[tuple[str, str], IdempotencyRecord] = {}

    async def get(self, scope: str, idempotency_key: str) -> Optional[IdempotencyRecord]:
        key = (scope, idempotency_key)
        record = self.records.get(key)
        if record and record.expires_at > datetime.now(timezone.utc):
            return record
        return None

    async def save(self, record: IdempotencyRecord) -> None:
        key = (record.scope, record.idempotency_key)
        if key not in self.records:
            self.records[key] = record
