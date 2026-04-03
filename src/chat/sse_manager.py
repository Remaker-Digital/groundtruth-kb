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
import json
import logging
import os
import sys
import time
import traceback
from collections import defaultdict
from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass, field
from typing import Any

from src.chat.models import StreamEvent, done_event, error_event

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# SPEC-1756: Global SSE connection limit per replica.
# At 680 tenants worst case: 680 × 30 (Enterprise) = 20,400 concurrent SSE
# connections. Default 5000 per replica provides a safety valve well below
# OS file descriptor limits while allowing headroom for scaling.
# Configurable via SSE_MAX_CONNECTIONS env var.
GLOBAL_SSE_MAX_CONNECTIONS: int = int(
    os.environ.get("SSE_MAX_CONNECTIONS", "5000")
)

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

# Default client-side reconnection interval (milliseconds).
# The ``retry:`` SSE directive tells the browser's EventSource how long
# to wait before reconnecting after a connection drop.
DEFAULT_RETRY_MS = 3000


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

        # P1-2: Fan-out state for duplicate/reconnecting streams
        self._active_producers: dict[str, str] = {}  # conv_id → message_id
        self._producer_conditions: dict[str, asyncio.Condition] = {}
        self._producer_sequences: dict[str, int] = {}  # conv_id → latest seq
        self._producer_done: dict[str, bool] = {}  # conv_id → finished
        self._completed_messages: dict[str, str] = {}  # conv_id → last completed message_id

        # WI #132: Optional metering callback invoked on first streamed chunk.
        # Signature: callback(tenant_id: str, conversation_id: str) -> None
        self._metering_callback: Callable[[str, str], Any] | None = None

        # WI #133: Multi-tab tracking.
        # {tenant_id: {conversation_id: set[tab_id]}}
        self._tab_connections: dict[str, dict[str, set[str]]] = defaultdict(
            lambda: defaultdict(set),
        )

    def can_connect(self, tenant_id: str, tier: str = "starter") -> bool:
        """Check if a new SSE connection is allowed for this tenant.

        SPEC-1756: Checks global connection limit to protect the replica.
        Returns False (with global_limit_reached flag) when the
        replica-wide cap is hit, signaling HTTP 503 + Retry-After.
        """
        # SPEC-1756: Global cap check — protect the replica
        if self.global_connection_count >= GLOBAL_SSE_MAX_CONNECTIONS:
            logger.warning(
                "Global SSE connection limit reached: %d/%d (tenant=%s denied)",
                self.global_connection_count,
                GLOBAL_SSE_MAX_CONNECTIONS,
                tenant_id[:8],
            )
            return False

        return True

    @property
    def global_connection_count(self) -> int:
        """Total active SSE connections across all tenants on this replica.

        SPEC-1756: Used by can_connect() for global cap enforcement and
        by /health/metrics for monitoring.
        """
        return sum(len(convs) for convs in self._connections.values())

    @property
    def is_global_limit_reached(self) -> bool:
        """Whether the global SSE connection limit has been reached.

        SPEC-1756: Callers should return HTTP 503 with Retry-After header
        when this returns True.
        """
        return self.global_connection_count >= GLOBAL_SSE_MAX_CONNECTIONS

    def connect(
        self,
        tenant_id: str,
        conversation_id: str,
        tab_id: str | None = None,
    ) -> None:
        """Register an active SSE connection.

        Args:
            tenant_id: Tenant identifier.
            conversation_id: Conversation identifier.
            tab_id: Optional browser tab identifier for multi-tab support
                (WI #133). Multiple tabs can stream the same conversation.
        """
        self._connections[tenant_id].add(conversation_id)

        # WI #133: Track tab_id if provided
        if tab_id is not None:
            self._tab_connections[tenant_id][conversation_id].add(tab_id)

        # Initialize event buffer if not exists
        if conversation_id not in self._buffers:
            self._buffers[conversation_id] = EventBuffer()

        logger.debug(
            "SSE connected: tenant=%s conv=%s tab=%s active=%d",
            tenant_id[:8], conversation_id[:8],
            tab_id or "default",
            len(self._connections[tenant_id]),
        )

    def disconnect(
        self,
        tenant_id: str,
        conversation_id: str,
        tab_id: str | None = None,
    ) -> None:
        """Unregister an SSE connection.

        Args:
            tenant_id: Tenant identifier.
            conversation_id: Conversation identifier.
            tab_id: Optional browser tab identifier (WI #133). If provided,
                only that tab is removed. The conversation connection is
                removed only when no tabs remain (or if tab_id is None,
                which removes the conversation unconditionally).
        """
        if tab_id is not None:
            # WI #133: Remove specific tab
            tenant_tabs = self._tab_connections.get(tenant_id)
            if tenant_tabs and conversation_id in tenant_tabs:
                tenant_tabs[conversation_id].discard(tab_id)
                # If tabs remain, keep the conversation connection alive
                if tenant_tabs[conversation_id]:
                    logger.debug(
                        "SSE tab disconnected: tenant=%s conv=%s tab=%s remaining=%d",
                        tenant_id[:8], conversation_id[:8], tab_id,
                        len(tenant_tabs[conversation_id]),
                    )
                    return
                # No tabs left — clean up tab tracking and fall through
                # to remove the conversation connection
                del tenant_tabs[conversation_id]
                if not tenant_tabs:
                    del self._tab_connections[tenant_id]
        else:
            # No tab_id — unconditional disconnect; clean up all tab tracking
            tenant_tabs = self._tab_connections.get(tenant_id)
            if tenant_tabs and conversation_id in tenant_tabs:
                del tenant_tabs[conversation_id]
                if not tenant_tabs:
                    del self._tab_connections[tenant_id]

        # Remove conversation from active connections
        conns = self._connections.get(tenant_id)
        if conns:
            conns.discard(conversation_id)
            if not conns:
                del self._connections[tenant_id]

        logger.debug(
            "SSE disconnected: tenant=%s conv=%s tab=%s",
            tenant_id[:8], conversation_id[:8],
            tab_id or "all",
        )

    def get_active_count(self, tenant_id: str) -> int:
        """Get the number of active SSE conversations for a tenant.

        Counts unique conversations, not individual tabs (WI #133).
        Multiple browser tabs streaming the same conversation count as
        one active connection for limit-enforcement purposes.
        """
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

    def is_producer_active(self, conversation_id: str, message_id: str) -> bool:
        """Check if a pipeline producer is already running for this message."""
        return self._active_producers.get(conversation_id) == message_id

    def is_message_completed(self, conversation_id: str, message_id: str) -> bool:
        """Check if a message was recently completed (replay-only, no pipeline)."""
        return self._completed_messages.get(conversation_id) == message_id

    async def fan_out_stream(
        self,
        conversation_id: str,
        last_event_id: int = 0,
        *,
        retry_ms: int = DEFAULT_RETRY_MS,
    ) -> AsyncGenerator[str, None]:
        """Attach to an active producer's buffer as a secondary consumer.

        P1-2: Non-lossy fan-out using asyncio.Condition + sequence counter.
        The consumer replays buffered events, then waits for the producer
        to signal new events via the condition variable.
        """
        condition = self._producer_conditions.get(conversation_id)
        if condition is None:
            return

        yield self.format_retry_directive(retry_ms)

        # Replay buffered events first
        buf = self._buffers.get(conversation_id)
        consumer_seq = last_event_id
        if buf:
            for seq, sse_text in buf.events:
                if seq > consumer_seq:
                    yield f"id: {seq}\n{sse_text}"
                    consumer_seq = seq

        # Live tail: wait for producer signals
        while True:
            try:
                async with condition:
                    await asyncio.wait_for(
                        condition.wait_for(
                            lambda: (
                                self._producer_sequences.get(conversation_id, 0) > consumer_seq
                                or self._producer_done.get(conversation_id, False)
                            )
                        ),
                        timeout=KEEPALIVE_INTERVAL_SECONDS,
                    )
            except asyncio.TimeoutError:
                yield ":ping\n\n"
                if self._producer_done.get(conversation_id, False):
                    break
                continue

            # Read new events from buffer
            if buf:
                for seq, sse_text in buf.events:
                    if seq > consumer_seq:
                        yield f"id: {seq}\n{sse_text}"
                        consumer_seq = seq

            if self._producer_done.get(conversation_id, False):
                break

    async def wrap_stream(
        self,
        tenant_id: str,
        conversation_id: str,
        pipeline_events: AsyncGenerator[StreamEvent, None],
        *,
        message_id: str | None = None,
        enable_heartbeat: bool = True,
        retry_ms: int = DEFAULT_RETRY_MS,
    ) -> AsyncGenerator[str, None]:
        """Wrap a pipeline event generator with heartbeat and buffering.

        Yields SSE-formatted strings (with ``id:`` field for reconnection).
        Sends ``:ping`` keepalive comments between events. Catches mid-stream
        errors and emits error/done events before closing.

        WI #131: Emits a ``retry:`` directive as the first event in every
        stream so the client's EventSource knows the reconnection interval.

        WI #132: Invokes the metering callback on the first non-heartbeat
        event (first-chunk metering) if a callback has been configured via
        :meth:`configure_metering`.

        P1-2: When ``message_id`` is provided, registers this stream as
        the active producer and signals fan-out consumers on each event.

        Args:
            tenant_id: Tenant identifier (for logging).
            conversation_id: Conversation identifier (for buffering).
            pipeline_events: Async generator of StreamEvent from ChatPipeline.
            message_id: Message being processed (P1-2 fan-out tracking).
            enable_heartbeat: Whether to send keepalive pings (default True).
            retry_ms: Client-side reconnection interval in milliseconds
                (WI #131). Sent as the SSE ``retry:`` directive. Default
                is :data:`DEFAULT_RETRY_MS` (3000ms).

        Yields:
            SSE-formatted strings ready for HTTP response body.
        """
        buf = self._buffers.get(conversation_id)
        if buf is None:
            buf = EventBuffer()
            self._buffers[conversation_id] = buf

        # P1-2: Register as active producer
        if message_id:
            self._active_producers[conversation_id] = message_id
            self._producer_conditions[conversation_id] = asyncio.Condition()
            self._producer_sequences[conversation_id] = 0
            self._producer_done[conversation_id] = False

        # WI #131: Emit retry directive as the very first SSE line so the
        # client's EventSource sets its reconnection interval immediately.
        yield self.format_retry_directive(retry_ms)

        # WI #132: Track whether metering has been triggered for this stream.
        metering_triggered = False

        try:
            async for event in self._with_heartbeat(
                pipeline_events, enable_heartbeat,
            ):
                if event is None:
                    # Heartbeat ping
                    yield ":ping\n\n"
                    continue

                # WI #132: Meter conversation on first real (non-heartbeat) chunk.
                if not metering_triggered:
                    metering_triggered = True
                    if self._metering_callback is not None:
                        try:
                            result = self._metering_callback(
                                tenant_id, conversation_id,
                            )
                            # Support both sync and async callbacks
                            if asyncio.iscoroutine(result):
                                await result
                        except Exception:
                            logger.warning(
                                "Metering callback failed: tenant=%s conv=%s",
                                tenant_id[:8], conversation_id[:8],
                                exc_info=True,
                            )

                # Serialize event with sequence ID for reconnection
                sse_text = event.to_sse()
                seq = buf.append(sse_text)

                # P1-2: Signal fan-out consumers
                if message_id and conversation_id in self._producer_conditions:
                    cond = self._producer_conditions[conversation_id]
                    async with cond:
                        self._producer_sequences[conversation_id] = seq
                        cond.notify_all()

                # Prepend id: field for Last-Event-ID support
                yield f"id: {seq}\n{sse_text}"

        except asyncio.CancelledError:
            # Client disconnected — clean exit
            logger.debug(
                "SSE stream cancelled: tenant=%s conv=%s",
                tenant_id[:8], conversation_id[:8],
            )
        except Exception as exc:
            # Mid-stream error — emit error + done events (WI #131 enhanced)
            exc_type = type(exc).__name__
            exc_msg = str(exc)[:500]
            # Print to stderr to bypass structured logging formatter
            print(
                f"[SSE FATAL] tenant={tenant_id[:8]} conv={conversation_id[:8]}"
                f"\n{traceback.format_exc()}",
                file=sys.stderr, flush=True,
            )
            logger.exception(
                "SSE stream error: tenant=%s conv=%s type=%s msg=%s",
                tenant_id[:8], conversation_id[:8], exc_type, exc_msg,
            )
            err_sse = self.format_error_event(
                message=f"Stream error: {exc_type}: {exc_msg}",
                code="stream_error",
                recoverable=True,
            )
            seq = buf.append(err_sse)
            yield f"id: {seq}\n{err_sse}"

            end = done_event(conversation_id, 0)
            sse_text = end.to_sse()
            seq = buf.append(sse_text)
            yield f"id: {seq}\n{sse_text}"
        finally:
            # P1-2: Signal producer done and clean up
            if message_id and conversation_id in self._producer_conditions:
                cond = self._producer_conditions[conversation_id]
                async with cond:
                    self._producer_done[conversation_id] = True
                    cond.notify_all()
                self._active_producers.pop(conversation_id, None)
                # P1-2: Record completed message so post-completion
                # reconnects can replay buffer without re-running pipeline
                self._completed_messages[conversation_id] = message_id

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

    # ------------------------------------------------------------------
    # WI #131: SSE error handling enhancements
    # ------------------------------------------------------------------

    @staticmethod
    def format_retry_directive(retry_ms: int = DEFAULT_RETRY_MS) -> str:
        """Format an SSE ``retry:`` directive.

        The ``retry:`` field tells the browser's ``EventSource`` how many
        milliseconds to wait before attempting automatic reconnection
        after the connection drops.

        Args:
            retry_ms: Reconnection interval in milliseconds (default 3000).

        Returns:
            SSE-formatted retry directive string.
        """
        return f"retry: {retry_ms}\n\n"

    @staticmethod
    def format_error_event(
        message: str,
        code: str,
        recoverable: bool = True,
    ) -> str:
        """Format a fully-formed SSE error event with structured JSON data.

        Includes a ``recoverable`` flag so the client can decide whether
        to retry the connection or display a terminal error.

        Args:
            message: Human-readable error description.
            code: Machine-readable error code (e.g. ``"stream_error"``).
            recoverable: Whether the client should attempt reconnection.

        Returns:
            SSE-formatted error event string.
        """
        data = {
            "message": message,
            "code": code,
            "recoverable": recoverable,
        }
        return f"event: error\ndata: {json.dumps(data)}\n\n"

    # ------------------------------------------------------------------
    # WI #132: Conversation metering integration
    # ------------------------------------------------------------------

    def configure_metering(
        self,
        callback: Callable[[str, str], Any] | None,
    ) -> None:
        """Set (or clear) the metering callback for first-chunk billing.

        The callback is invoked once per stream on the first non-heartbeat
        event, allowing the billing system to meter the conversation at
        first-chunk delivery rather than waiting for response completion.

        Args:
            callback: A callable ``(tenant_id, conversation_id) -> None``
                (may be sync or async). Pass ``None`` to disable metering.
        """
        self._metering_callback = callback
        logger.debug(
            "SSE metering callback %s",
            "configured" if callback is not None else "cleared",
        )

    # ------------------------------------------------------------------
    # WI #133: Multi-tab coordination
    # ------------------------------------------------------------------

    def get_active_conversations(self, tenant_id: str) -> set[str]:
        """Return the set of conversation_ids with active SSE connections.

        Args:
            tenant_id: Tenant identifier.

        Returns:
            Set of conversation_id strings. Empty set if no active streams.
        """
        return set(self._connections.get(tenant_id, set()))

    def is_conversation_active(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> bool:
        """Check if a specific conversation has an active SSE connection.

        Args:
            tenant_id: Tenant identifier.
            conversation_id: Conversation identifier.

        Returns:
            True if the conversation currently has at least one active
            SSE stream for this tenant.
        """
        conns = self._connections.get(tenant_id)
        if conns is None:
            return False
        return conversation_id in conns

    def get_tab_count(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> int:
        """Return the number of tabs streaming a given conversation.

        Args:
            tenant_id: Tenant identifier.
            conversation_id: Conversation identifier.

        Returns:
            Number of distinct tab_ids. Returns 0 if no tabs are tracked
            (either no connection or connected without tab_id).
        """
        tenant_tabs = self._tab_connections.get(tenant_id)
        if tenant_tabs is None:
            return 0
        return len(tenant_tabs.get(conversation_id, set()))

    def cleanup_expired_buffers(self) -> int:
        """Remove expired event buffers and fan-out state. Returns count removed.

        Call periodically (e.g., every 60s) to prevent memory leaks.
        P1-2: Also cleans fan-out bookkeeping for expired conversations.
        """
        expired = [
            cid for cid, buf in self._buffers.items() if buf.is_expired
        ]
        for cid in expired:
            del self._buffers[cid]
            # P1-2: Clean fan-out state for expired conversations
            self._producer_conditions.pop(cid, None)
            self._producer_sequences.pop(cid, None)
            self._producer_done.pop(cid, None)
            self._completed_messages.pop(cid, None)
        return len(expired)

    def health_summary(self) -> dict[str, Any]:
        """Health summary for the /ready endpoint."""
        total_connections = self.global_connection_count
        total_tabs = sum(
            len(tabs)
            for tenant_tabs in self._tab_connections.values()
            for tabs in tenant_tabs.values()
        )
        return {
            "active_connections": total_connections,
            "global_connection_limit": GLOBAL_SSE_MAX_CONNECTIONS,
            "global_limit_reached": self.is_global_limit_reached,
            "active_tabs": total_tabs,
            "tenants_streaming": len(self._connections),
            "event_buffers": len(self._buffers),
            "metering_configured": self._metering_callback is not None,
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
