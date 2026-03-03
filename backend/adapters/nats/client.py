"""NATS adapter — EventBusPort implementation (FR-16).

Implements graceful degradation per ADR-005 Event Delivery Semantics:
- Publish failures log warning but do NOT throw
- Mission execution continues even if NATS is unavailable
"""
import json
import logging
from typing import Any, Awaitable, Callable

import nats
from nats.aio.client import Client as NATSClient

from domain.events.envelope import EventEnvelope
from ports.event_bus import EventBusPort

logger = logging.getLogger(__name__)


class NATSEventBus(EventBusPort):
    """NATS-backed event bus for the Synarch nervous system."""

    def __init__(self, url: str = "nats://localhost:4222"):
        self.url = url
        self._nc: NATSClient | None = None
        self._connected = False

    async def connect(self) -> None:
        try:
            self._nc = await nats.connect(self.url)
            self._connected = True
            logger.info("Connected to NATS at %s", self.url)
        except Exception as e:
            logger.warning("Failed to connect to NATS: %s. Events will be degraded.", e)
            self._connected = False

    async def publish(self, event: EventEnvelope) -> None:
        """Publish event. Non-blocking on failure (ADR-005)."""
        if not self._connected or self._nc is None:
            logger.warning("NATS not connected. Event %s dropped.", event.type)
            return
        try:
            await self._nc.publish(
                event.to_nats_subject(),
                event.to_json_bytes(),
            )
        except Exception as e:
            logger.warning("NATS publish failed for %s: %s", event.type, e)

    async def subscribe(self, subject: str, callback: Callable[[EventEnvelope], Awaitable[None]]) -> Any:
        if not self._connected or self._nc is None:
            logger.warning("NATS not connected. Cannot subscribe to %s.", subject)
            return None

        async def _handler(msg):
            try:
                data = json.loads(msg.data.decode("utf-8"))
                envelope = EventEnvelope(**data)
                await callback(envelope)
            except Exception as e:
                logger.error("Error handling NATS message: %s", e)

        return await self._nc.subscribe(subject, cb=_handler)

    async def unsubscribe(self, subscription: Any) -> None:
        """Unsubscribe from a NATS subject."""
        if subscription:
            try:
                await subscription.unsubscribe()
            except Exception as e:
                logger.warning("Error unsubscribing: %s", e)

    async def close(self) -> None:
        if self._nc and self._connected:
            await self._nc.drain()
            self._connected = False
            logger.info("NATS connection closed.")
