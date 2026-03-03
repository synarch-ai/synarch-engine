import json
from typing import Optional

from asyncpg import Pool

from ports.idempotency import IdempotencyRecord, IdempotencyRepository


class PostgresIdempotencyRepository(IdempotencyRepository):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def get(self, scope: str, idempotency_key: str) -> Optional[IdempotencyRecord]:
        query = """
            SELECT request_hash, response_status, response_body, expires_at
            FROM idempotency_records
            WHERE scope = $1
              AND idempotency_key = $2
              AND expires_at > NOW()
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, scope, idempotency_key)
            if not row:
                return None

            return IdempotencyRecord(
                scope=scope,
                idempotency_key=idempotency_key,
                request_hash=row["request_hash"],
                response_status=row["response_status"],
                response_body=json.loads(row["response_body"]),
                expires_at=row["expires_at"]
            )

    async def save(self, record: IdempotencyRecord) -> None:
        query = """
            INSERT INTO idempotency_records (
                scope, idempotency_key, request_hash,
                response_status, response_body, expires_at
            )
            VALUES ($1, $2, $3, $4, $5::jsonb, $6)
            ON CONFLICT (scope, idempotency_key) DO NOTHING
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                record.scope,
                record.idempotency_key,
                record.request_hash,
                record.response_status,
                json.dumps(record.response_body),
                record.expires_at
            )
