"""SSE connection management — keepalive, reconnection, tenant limits (WI #129/#131/#133).

Manages Server-Sent Event connections for the chat streaming endpoint.
Provides:

1. SSEConnectionManager: tracks active SSE connections per tenant, enforces
   limits aligned with concurrency settings, sends keepalive pings, and
   supports Last-Event-ID–based reconnection.

2. Heartbeat: periodic keepalive comments (`:ping`) to prevent proxy/LB
   timeouts. Azure Application Gateway has a 60s idle timeout; we send
   pings every 15s.

3. Event buffering: recent events are buffered per conversation so that
   a reconnecting client (``Last-Event-ID`` header) can resume from where
   it left off rather than missing events.

4. Mid-stream error recovery: if the pipeline generator raises during
   streaming, the manager emits an ``error`` event and ``done`` event
   before closing the connection cleanly.

Architecture references:
    - Decision UI-4: Hybrid protocol (HTTP + SSE + WebSocket)
    - Decision UI-5: SSE stream-then-validate
    - Decision #14: Per-tenant concurrency limits (reused for SSE)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

from src.chat.models import StreamEvent, done_event, error_event
from src.multi_tenant.cosmos_schema import TIER_DEFAULTS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Keepalive interval (seconds) — must be less than Azure App Gateway
# idle timeout (60s) and typical proxy timeouts (30-120s).
KEEPALIVE_INTERVAL_SECONDS = 15

# Maximum events buffered per conversation for reconnection support.
# Each event is ~200 bytes, so 100 events ≈ 20 KB per conversation.
MAX_BUFFERED_EVENTS = 100

# Buffer expiry — discard event buffers after this many seconds of
# inactivity (no new events). Prevents memory leaks from abandoned
# conversations.
BUFFER_EXPIRY_SECONDS = 300  # 5 minutes


# ---------------------------------------------------------------------------
# Event buffer (Last-Event-ID reconnection support)
# ---------------------------------------------------------------------------


@dataclass
class EventBuffer:
    """Circular buffer of recent SSE events for a single conversation.

    Events are identified by a monotonically increasing sequence number.
    When a client reconnects with ``Last-Event-ID: N``, we replay all
    events with sequence > N.
    """

    events: list[tuple[int, str]] = field(default_factory=list)
    last_sequence: int = 0
    last_activity: float = field(default_factory=time.monotonic)

    def append(self, sse_text: str) -> int:
        """Add an event and return its sequence number."""
        self.last_sequence += 1
        seq = self.last_sequence
        self.events.append((seq, sse_text))
        self.last_activity = time.monotonic()

        # Trim to max buffer size
        if len(self.events) > MAX_BUFFERED_EVENTS:
            self.events = self.events[-MAX_BUFFERED_EVENTS:]

        return seq

    def replay_after(self, last_event_id: int) -> list[str]:
        """Return all events with sequence > last_event_id."""
        return [text for seq, text in self.events if seq > last_event_id]

    @property
    def is_expired(self) -> bool:
        return (time.monotonic() - self.last_activity) > BUFFER_EXPIRY_SECONDS


# ---------------------------------------------------------------------------
# SSE Connection Manager
# ---------------------------------------------------------------------------


class SSEConnectionManager:
    """Manages active SSE streaming connections with per-tenant limits.

    Usage:
        manager = SSEConnectionManager()

        # In the streaming endpoint:
        async def stream_response(tenant_id, conversation_id, ...):
            if not manager.can_connect(tenant_id, tier):
                raise HTTPException(429, "Too many active streams")

            manager.connect(tenant_id, conversation_id)
            try:
                async for event in manager.wrap_stream(
                    tenant_id, conversation_id, pipeline_generator,
                ):
                    yield event
            finally:
                manager.disconnect(tenant_id, conversation_id)
    """

    def __init__(self) -> None:
        # {tenant_id: set[conversation_id]} — active SSE connections
        self._connections: dict[str, set[str]] = defaultdict(set)

        # {conversation_id: EventBuffer} — event buffers for reconnection
        self._buffers: dict[str, EventBuffer] = {}

    def can_connect(self, tenant_id: str, tier: str = "starter") -> bool:
        """Check if a new SSE connection is allowed for this tenant.

        Uses the same concurrency limits as TenantConcurrencyMiddleware
        (from TIER_DEFAULTS.max_concurrent).
        """
        tier_config = TIER_DEFAULTS.get(tier, TIER_DEFAULTS.get("starter", {}))
        max_concurrent = tier_config.get("max_concurrent", 3)

        current = len(self._connections.get(tenant_id, set()))
        return current < max_concurrent

    def connect(self, tenant_id: str, conversation_id: str) -> None:
        """Register an active SSE connection."""
        self._connections[tenant_id].add(conversation_id)

        # Initialize event buffer if not exists
        if conversation_id not in self._buffers:
            self._buffers[conversation_id] = EventBuffer()

        logger.debug(
            "SSE connected: tenant=%s conv=%s active=%d",
            tenant_id[:8], conversation_id[:8],
            len(self._connections[tenant_id]),
        )

    def disconnect(self, tenant_id: str, conversation_id: str) -> None:
        """Unregister an SSE connection."""
        conns = self._connections.get(tenant_id)
        if conns:
            conns.discard(conversation_id)
            if not conns:
                del self._connections[tenant_id]

        logger.debug(
            "SSE disconnected: tenant=%s conv=%s",
            tenant_id[:8], conversation_id[:8],
        )

    def get_active_count(self, tenant_id: str) -> int:
        """Get the number of active SSE connections for a tenant."""
        return len(self._connections.get(tenant_id, set()))

    def get_replay_events(
        self,
        conversation_id: str,
        last_event_id: int,
    ) -> list[str]:
        """Get buffered events after the given Last-Event-ID for reconnection."""
        buf = self._buffers.get(conversation_id)
        if buf is None:
            return []
        return buf.replay_after(last_event_id)

    async def wrap_stream(
        self,
        tenant_id: str,
        conversation_id: str,
        pipeline_events: AsyncGenerator[StreamEvent, None],
        *,
        enable_heartbeat: bool = True,
    ) -> AsyncGenerator[str, None]:
        """Wrap a pipeline event generator with heartbeat and buffering.

        Yields SSE-formatted strings (with ``id:`` field for reconnection).
        Sends ``:ping`` keepalive comments between events. Catches mid-stream
        errors and emits error/done events before closing.

        Args:
            tenant_id: Tenant identifier (for logging).
            conversation_id: Conversation identifier (for buffering).
            pipeline_events: Async generator of StreamEvent from ChatPipeline.
            enable_heartbeat: Whether to send keepalive pings (default True).

        Yields:
            SSE-formatted strings ready for HTTP response body.
        """
        buf = self._buffers.get(conversation_id)
        if buf is None:
            buf = EventBuffer()
            self._buffers[conversation_id] = buf

        try:
            async for event in self._with_heartbeat(
                pipeline_events, enable_heartbeat,
            ):
                if event is None:
                    # Heartbeat ping
                    yield ":ping\n\n"
                    continue

                # Serialize event with sequence ID for reconnection
                sse_text = event.to_sse()
                seq = buf.append(sse_text)

                # Prepend id: field for Last-Event-ID support
                yield f"id: {seq}\n{sse_text}"

        except asyncio.CancelledError:
            # Client disconnected — clean exit
            logger.debug(
                "SSE stream cancelled: tenant=%s conv=%s",
                tenant_id[:8], conversation_id[:8],
            )
        except Exception:
            # Mid-stream error — emit error + done events
            logger.exception(
                "SSE stream error: tenant=%s conv=%s",
                tenant_id[:8], conversation_id[:8],
            )
            err = error_event(
                "An error occurred during streaming. Please try again.",
                code="stream_error",
            )
            sse_text = err.to_sse()
            seq = buf.append(sse_text)
            yield f"id: {seq}\n{sse_text}"

            end = done_event(conversation_id, 0)
            sse_text = end.to_sse()
            seq = buf.append(sse_text)
            yield f"id: {seq}\n{sse_text}"

    async def _with_heartbeat(
        self,
        events: AsyncGenerator[StreamEvent, None],
        enable: bool,
    ) -> AsyncGenerator[StreamEvent | None, None]:
        """Interleave heartbeat pings with pipeline events.

        Yields None for heartbeat pings and StreamEvent for actual events.
        """
        if not enable:
            async for event in events:
                yield event
            return

        event_iter = events.__aiter__()
        while True:
            try:
                event = await asyncio.wait_for(
                    event_iter.__anext__(),
                    timeout=KEEPALIVE_INTERVAL_SECONDS,
                )
                yield event
            except asyncio.TimeoutError:
                # No event within keepalive interval — send ping
                yield None
            except StopAsyncIteration:
                break

    def cleanup_expired_buffers(self) -> int:
        """Remove expired event buffers. Returns the number removed.

        Call periodically (e.g., every 60s) to prevent memory leaks.
        """
        expired = [
            cid for cid, buf in self._buffers.items() if buf.is_expired
        ]
        for cid in expired:
            del self._buffers[cid]
        return len(expired)

    def health_summary(self) -> dict[str, Any]:
        """Health summary for the /ready endpoint."""
        total_connections = sum(
            len(convs) for convs in self._connections.values()
        )
        return {
            "active_connections": total_connections,
            "tenants_streaming": len(self._connections),
            "event_buffers": len(self._buffers),
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_manager: SSEConnectionManager | None = None


def get_sse_manager() -> SSEConnectionManager:
    """Get the module-level SSEConnectionManager singleton."""
    global _manager
    if _manager is None:
        _manager = SSEConnectionManager()
    return _manager
