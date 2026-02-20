"""LangGraph checkpointer adapter — wraps AsyncPostgresSaver (FR-5, FR-10)."""
import logging
from typing import Any

from ports.checkpointer import CheckpointerPort

logger = logging.getLogger(__name__)


class LangGraphCheckpointer(CheckpointerPort):
    """PostgreSQL-backed checkpointer for LangGraph StateGraph."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self._checkpointer: Any = None
        self._conn_ctx: Any = None

    async def setup(self) -> None:
        """Initialize the PostgreSQL checkpointer and create tables."""
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        # langgraph-checkpoint-postgres v3+ uses async context manager
        self._conn_ctx = AsyncPostgresSaver.from_conn_string(self.database_url)
        self._checkpointer = await self._conn_ctx.__aenter__()
        await self._checkpointer.setup()
        logger.info("LangGraph PostgreSQL checkpointer initialized.")

    async def close(self) -> None:
        """Close the checkpointer connection."""
        if self._conn_ctx:
            await self._conn_ctx.__aexit__(None, None, None)
            logger.info("LangGraph checkpointer connection closed.")

    def get_checkpointer(self) -> Any:
        """Return the underlying checkpointer for graph compilation."""
        if self._checkpointer is None:
            raise RuntimeError("Checkpointer not initialized. Call setup() first.")
        return self._checkpointer
