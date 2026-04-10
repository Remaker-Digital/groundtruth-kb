# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Internal Integration Event Bus (SPEC-1778).

Fire-and-forget event bus for integration lifecycle events.  Handlers
are registered by event type and executed concurrently with error
isolation — a failing handler never blocks siblings.

Event taxonomy:
  ticket.created, ticket.updated, article.created, article.updated,
  message.received, action.completed, integration.connected,
  integration.disconnected, sync.completed, sync.failed

Uses asyncio background tasks.  Compatible with Redis pub/sub for
cross-replica broadcasting (future enhancement).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Event types
# ---------------------------------------------------------------------------


class IntegrationEventType(str, Enum):
    """Standardized integration event types."""

    TICKET_CREATED = "ticket.created"
    TICKET_UPDATED = "ticket.updated"
    ARTICLE_CREATED = "article.created"
    ARTICLE_UPDATED = "article.updated"
    MESSAGE_RECEIVED = "message.received"
    ACTION_COMPLETED = "action.completed"
    INTEGRATION_CONNECTED = "integration.connected"
    INTEGRATION_DISCONNECTED = "integration.disconnected"
    SYNC_COMPLETED = "sync.completed"
    SYNC_FAILED = "sync.failed"


# ---------------------------------------------------------------------------
# Event payload
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IntegrationEvent:
    """Immutable event payload emitted by the bus."""

    event_type: IntegrationEventType
    tenant_id: str
    integration_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = ""


# ---------------------------------------------------------------------------
# Handler type
# ---------------------------------------------------------------------------

EventHandler = Callable[[IntegrationEvent], Coroutine[Any, Any, None]]


# ---------------------------------------------------------------------------
# Event Bus
# ---------------------------------------------------------------------------


class IntegrationEventBus:
    """Singleton async event bus for integration events.

    Handlers are registered per event type.  ``emit()`` fires all
    matching handlers concurrently in background tasks.  Errors in
    individual handlers are logged but never propagate.
    """

    _instance: IntegrationEventBus | None = None

    def __init__(self) -> None:
        self._handlers: dict[
            IntegrationEventType, list[EventHandler]
        ] = defaultdict(list)
        self._background_tasks: set[asyncio.Task[None]] = set()
        self._emit_count: int = 0
        self._error_count: int = 0

    @classmethod
    def get_instance(cls) -> IntegrationEventBus:
        """Return the singleton bus instance."""
        if cls._instance is None:
            cls._instance = IntegrationEventBus()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (testing only)."""
        cls._instance = None

    # -- Registration -------------------------------------------------------

    def on(
        self,
        event_type: IntegrationEventType,
        handler: EventHandler,
    ) -> None:
        """Register a handler for an event type."""
        self._handlers[event_type].append(handler)
        logger.debug(
            "Registered handler %s for %s",
            handler.__qualname__,
            event_type.value,
        )

    def off(
        self,
        event_type: IntegrationEventType,
        handler: EventHandler,
    ) -> bool:
        """Unregister a handler.  Returns True if found and removed."""
        handlers = self._handlers.get(event_type, [])
        try:
            handlers.remove(handler)
            return True
        except ValueError:
            return False

    # -- Emission -----------------------------------------------------------

    async def emit(self, event: IntegrationEvent) -> int:
        """Emit an event to all registered handlers.

        Each handler runs in its own background task with error isolation.
        Returns the number of handlers dispatched.
        """
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            logger.debug(
                "No handlers for %s (tenant=%s)",
                event.event_type.value,
                event.tenant_id,
            )
            return 0

        self._emit_count += 1
        dispatched = 0

        for handler in handlers:
            task = asyncio.create_task(
                self._run_handler(handler, event),
                name=f"evt:{event.event_type.value}:{handler.__qualname__}",
            )
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
            dispatched += 1

        logger.info(
            "Emitted %s → %d handler(s) (tenant=%s, integration=%s)",
            event.event_type.value,
            dispatched,
            event.tenant_id,
            event.integration_id,
        )
        return dispatched

    def emit_sync(self, event: IntegrationEvent) -> int:
        """Schedule emission from a synchronous context.

        Creates the async emit task on the running event loop.
        Returns 0 immediately; actual dispatch is async.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.emit(event))
            return 0
        except RuntimeError:
            logger.warning(
                "No running event loop — cannot emit %s",
                event.event_type.value,
            )
            return 0

    async def _run_handler(
        self, handler: EventHandler, event: IntegrationEvent
    ) -> None:
        """Execute a single handler with error isolation."""
        try:
            await handler(event)
        except Exception:
            self._error_count += 1
            logger.exception(
                "Handler %s failed for %s (tenant=%s)",
                handler.__qualname__,
                event.event_type.value,
                event.tenant_id,
            )

    # -- Queries ------------------------------------------------------------

    def handler_count(self, event_type: IntegrationEventType) -> int:
        """Number of handlers registered for an event type."""
        return len(self._handlers.get(event_type, []))

    @property
    def total_handlers(self) -> int:
        """Total number of registered handlers across all event types."""
        return sum(len(h) for h in self._handlers.values())

    @property
    def emit_count(self) -> int:
        """Total number of emit() calls."""
        return self._emit_count

    @property
    def error_count(self) -> int:
        """Total number of handler errors."""
        return self._error_count

    @property
    def pending_tasks(self) -> int:
        """Number of background tasks still running."""
        return len(self._background_tasks)

    async def drain(self, timeout: float = 5.0) -> int:
        """Wait for all pending background tasks to complete.

        Returns the number of tasks that were pending.
        Useful for testing and graceful shutdown.
        """
        pending = list(self._background_tasks)
        if not pending:
            return 0
        count = len(pending)
        done, _ = await asyncio.wait(pending, timeout=timeout)
        return count
