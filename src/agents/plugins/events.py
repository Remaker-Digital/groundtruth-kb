"""In-process invocation event bus (SPEC-1855).

Provides a lightweight event bus for agent/skill invocation events.
Events are emitted by the dispatcher and orchestrator, and consumed
by observability, audit, and billing subscribers.

The bus is in-process only — no external messaging dependency.
Subscribers receive events synchronously to ensure ordering guarantees.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class InvocationEvent:
    """Structured invocation event (SPEC-1855 req 1).

    Events form a tree: pipeline root -> agent invocations -> skill calls.
    """

    event_id: str = ""
    trace_id: str = ""
    parent_event_id: str | None = None
    invoker: str = "system"
    target_agent_id: str = ""
    skill_id: str | None = None
    tenant_id: str = ""
    conversation_id: str = ""
    timestamp: str = ""
    latency_ms: float = 0
    result_class: str = "success"
    policy_verdict: str = "allowed"
    error_detail: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


# Type alias for event subscribers
EventSubscriber = Callable[[InvocationEvent], None]


class InvocationEventBus:
    """In-process event bus for invocation events (SPEC-1855).

    Thread-safe singleton. Subscribers are called synchronously in
    registration order to preserve event ordering.
    """

    _instance: InvocationEventBus | None = None

    def __init__(self) -> None:
        self._subscribers: list[EventSubscriber] = []
        self._buffer: list[InvocationEvent] = []
        self._buffer_enabled = False

    @classmethod
    def get_instance(cls) -> InvocationEventBus:
        if cls._instance is None:
            cls._instance = InvocationEventBus()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (testing only)."""
        cls._instance = None

    def subscribe(self, subscriber: EventSubscriber) -> None:
        """Register a subscriber for invocation events."""
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: EventSubscriber) -> None:
        """Remove a subscriber."""
        self._subscribers = [s for s in self._subscribers if s is not subscriber]

    def emit(self, event: InvocationEvent) -> None:
        """Emit an invocation event to all subscribers."""
        if self._buffer_enabled:
            self._buffer.append(event)

        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                logger.exception(
                    "Invocation event subscriber failed for event %s",
                    event.event_id,
                )

    def enable_buffer(self) -> None:
        """Enable event buffering (for batch retrieval in tests/audit)."""
        self._buffer_enabled = True

    def disable_buffer(self) -> None:
        """Disable event buffering."""
        self._buffer_enabled = False
        self._buffer.clear()

    def get_buffered_events(self) -> list[InvocationEvent]:
        """Return buffered events (does not clear buffer)."""
        return list(self._buffer)

    def clear_buffer(self) -> None:
        """Clear the event buffer."""
        self._buffer.clear()

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)


def emit_invocation(
    *,
    trace_id: str,
    target_agent_id: str,
    tenant_id: str,
    conversation_id: str,
    invoker: str = "system",
    parent_event_id: str | None = None,
    skill_id: str | None = None,
    latency_ms: float = 0,
    result_class: str = "success",
    policy_verdict: str = "allowed",
    error_detail: str | None = None,
) -> InvocationEvent:
    """Convenience function to create and emit an invocation event."""
    event = InvocationEvent(
        trace_id=trace_id,
        parent_event_id=parent_event_id,
        invoker=invoker,
        target_agent_id=target_agent_id,
        skill_id=skill_id,
        tenant_id=tenant_id,
        conversation_id=conversation_id,
        latency_ms=latency_ms,
        result_class=result_class,
        policy_verdict=policy_verdict,
        error_detail=error_detail,
    )
    InvocationEventBus.get_instance().emit(event)
    return event
