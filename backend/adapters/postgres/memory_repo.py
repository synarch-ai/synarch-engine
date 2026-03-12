import json
from typing import List, Optional
from uuid import UUID
from asyncpg import Pool
from domain.models.memory import Memory, MemoryType
from ports.persistence import MemoryRepository

class PostgresMemoryRepository(MemoryRepository):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create(self, memory: Memory) -> Memory:
        query = """
            INSERT INTO memories (
                id, mission_id, agent, memory_type, content,
                embedding, metadata, importance, created_at, expires_at
            ) VALUES (
                $1::uuid, $2::uuid, $3, $4::memory_type, $5,
                $6::vector, $7::jsonb, $8, $9, $10
            )
            RETURNING id
        """
        embedding_str = f"[{','.join(map(str, memory.embedding))}]" if memory.embedding else None

        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                memory.id,
                memory.mission_id,
                memory.agent,
                memory.memory_type.value,
                memory.content,
                embedding_str,
                json.dumps(memory.metadata),
                memory.importance,
                memory.created_at,
                memory.expires_at,
            )
        return memory

    async def search(self, agent: str, embedding: List[float], limit: int = 5, threshold: float = 0.7) -> List[Memory]:
        max_distance = 1.0 - threshold
        embedding_str = f"[{','.join(map(str, embedding))}]"

        query = """
            SELECT
                id, mission_id, agent, memory_type, content,
                metadata, importance, created_at, expires_at,
                1 - (embedding <=> $1::vector) AS similarity
            FROM memories
            WHERE agent = $2
              AND (archived_at IS NULL)
              AND (expires_at IS NULL OR expires_at > NOW())
              AND (embedding <=> $1::vector) <= $3
            ORDER BY embedding <=> $1::vector
            LIMIT $4
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, embedding_str, agent, max_distance, limit)

            results = []
            for row in rows:
                results.append(Memory(
                    id=row["id"],
                    mission_id=row["mission_id"],
                    agent=row["agent"],
                    memory_type=MemoryType(row["memory_type"]),
                    content=row["content"],
                    metadata=json.loads(row["metadata"]),
                    importance=float(row["importance"]),
                    created_at=row["created_at"],
                    expires_at=row["expires_at"],
                ))
            return results
