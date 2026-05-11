"""
Tests for SSE connection management — src/chat/sse_manager.py.

Covers: EventBuffer (append, replay_after, is_expired),
        SSEConnectionManager (can_connect, connect, disconnect,
        get_active_count, get_replay_events, wrap_stream,
        _with_heartbeat, format_retry_directive, format_error_event,
        configure_metering, get_active_conversations,
        is_conversation_active, get_tab_count,
        cleanup_expired_buffers, health_summary),
        module singleton (get_sse_manager).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import json
import time
from unittest.mock import MagicMock

import pytest

from src.chat.models import token_event
from src.chat.sse_manager import (
    BUFFER_EXPIRY_SECONDS,
    DEFAULT_RETRY_MS,
    MAX_BUFFERED_EVENTS,
    EventBuffer,
    SSEConnectionManager,
    get_sse_manager,
)


# ---------------------------------------------------------------------------
# Tests — EventBuffer
# ---------------------------------------------------------------------------


class TestEventBuffer:
    """Tests for the EventBuffer dataclass."""

    def test_append_returns_incrementing_sequence(self):
        buf = EventBuffer()
        seq1 = buf.append("event: token\ndata: {}\n\n")
        seq2 = buf.append("event: token\ndata: {}\n\n")
        assert seq1 == 1
        assert seq2 == 2

    def test_replay_after_returns_events_after_id(self):
        buf = EventBuffer()
        buf.append("event1")
        buf.append("event2")
        buf.append("event3")

        replayed = buf.replay_after(1)
        assert len(replayed) == 2
        assert replayed[0] == "event2"
        assert replayed[1] == "event3"

    def test_replay_after_zero_returns_all(self):
        buf = EventBuffer()
        buf.append("event1")
        buf.append("event2")

        replayed = buf.replay_after(0)
        assert len(replayed) == 2

    def test_replay_after_last_returns_empty(self):
        buf = EventBuffer()
        buf.append("event1")
        buf.append("event2")

        replayed = buf.replay_after(2)
        assert len(replayed) == 0

    def test_buffer_trims_at_max(self):
        buf = EventBuffer()
        for i in range(MAX_BUFFERED_EVENTS + 20):
            buf.append(f"event_{i}")

        assert len(buf.events) == MAX_BUFFERED_EVENTS

    def test_is_expired_false_when_recent(self):
        buf = EventBuffer()
        buf.append("event")
        assert buf.is_expired is False

    def test_is_expired_true_after_expiry(self):
        buf = EventBuffer()
        buf.last_activity = time.monotonic() - BUFFER_EXPIRY_SECONDS - 10
        assert buf.is_expired is True


# ---------------------------------------------------------------------------
# Tests — SSEConnectionManager — connection lifecycle
# ---------------------------------------------------------------------------


class TestSSEConnectionLifecycle:
    """Tests for connect/disconnect/can_connect."""

    def test_can_connect_under_limit(self):
        mgr = SSEConnectionManager()
        assert mgr.can_connect("tenant-001", "starter") is True

    def test_can_connect_no_per_tenant_limit(self):
        mgr = SSEConnectionManager()
        # Per-tenant max_concurrent removed; no per-tenant limit
        for i in range(10):
            mgr.connect("tenant-001", f"conv-{i}")
        # Still allowed — only global limit applies
        assert mgr.can_connect("tenant-001", "starter") is True

    def test_disconnect_reduces_count(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")
        mgr.connect("tenant-001", "conv-2")
        mgr.connect("tenant-001", "conv-3")
        assert mgr.get_active_count("tenant-001") == 3

        mgr.disconnect("tenant-001", "conv-1")
        assert mgr.get_active_count("tenant-001") == 2

    def test_get_active_count(self):
        mgr = SSEConnectionManager()
        assert mgr.get_active_count("tenant-001") == 0

        mgr.connect("tenant-001", "conv-1")
        mgr.connect("tenant-001", "conv-2")
        assert mgr.get_active_count("tenant-001") == 2

    def test_disconnect_empty_tenant_cleans_up(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")
        mgr.disconnect("tenant-001", "conv-1")
        assert mgr.get_active_count("tenant-001") == 0
        # Should have cleaned up the tenant entry
        assert "tenant-001" not in mgr._connections

    def test_connect_creates_event_buffer(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")
        assert "conv-1" in mgr._buffers


# ---------------------------------------------------------------------------
# Tests — Multi-tab support (WI #133)
# ---------------------------------------------------------------------------


class TestMultiTab:
    """Tests for multi-tab tracking."""

    def test_connect_with_tab_id(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1", tab_id="tab-a")
        assert mgr.get_tab_count("tenant-001", "conv-1") == 1

    def test_multiple_tabs_same_conversation(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1", tab_id="tab-a")
        mgr.connect("tenant-001", "conv-1", tab_id="tab-b")
        assert mgr.get_tab_count("tenant-001", "conv-1") == 2

    def test_disconnect_tab_keeps_connection_alive(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1", tab_id="tab-a")
        mgr.connect("tenant-001", "conv-1", tab_id="tab-b")

        mgr.disconnect("tenant-001", "conv-1", tab_id="tab-a")

        # Connection should still be active (tab-b remains)
        assert mgr.get_active_count("tenant-001") == 1
        assert mgr.get_tab_count("tenant-001", "conv-1") == 1

    def test_disconnect_last_tab_removes_connection(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1", tab_id="tab-a")

        mgr.disconnect("tenant-001", "conv-1", tab_id="tab-a")

        assert mgr.get_active_count("tenant-001") == 0
        assert mgr.get_tab_count("tenant-001", "conv-1") == 0

    def test_disconnect_without_tab_id_removes_all(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1", tab_id="tab-a")
        mgr.connect("tenant-001", "conv-1", tab_id="tab-b")

        mgr.disconnect("tenant-001", "conv-1")  # No tab_id

        assert mgr.get_active_count("tenant-001") == 0
        assert mgr.get_tab_count("tenant-001", "conv-1") == 0

    def test_get_tab_count_no_connection(self):
        mgr = SSEConnectionManager()
        assert mgr.get_tab_count("tenant-001", "conv-x") == 0

    def test_get_active_conversations(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")
        mgr.connect("tenant-001", "conv-2")

        convs = mgr.get_active_conversations("tenant-001")
        assert convs == {"conv-1", "conv-2"}

    def test_get_active_conversations_empty(self):
        mgr = SSEConnectionManager()
        assert mgr.get_active_conversations("tenant-x") == set()

    def test_is_conversation_active_true(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")
        assert mgr.is_conversation_active("tenant-001", "conv-1") is True

    def test_is_conversation_active_false(self):
        mgr = SSEConnectionManager()
        assert mgr.is_conversation_active("tenant-001", "conv-x") is False

    def test_is_conversation_active_no_tenant(self):
        mgr = SSEConnectionManager()
        assert mgr.is_conversation_active("no-tenant", "conv-1") is False


# ---------------------------------------------------------------------------
# Tests — Replay events
# ---------------------------------------------------------------------------


class TestReplayEvents:
    """Tests for get_replay_events."""

    def test_replay_from_buffer(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")
        buf = mgr._buffers["conv-1"]
        buf.append("event1")
        buf.append("event2")
        buf.append("event3")

        replayed = mgr.get_replay_events("conv-1", 1)
        assert len(replayed) == 2

    def test_replay_no_buffer(self):
        mgr = SSEConnectionManager()
        assert mgr.get_replay_events("conv-x", 0) == []


# ---------------------------------------------------------------------------
# Tests — wrap_stream
# ---------------------------------------------------------------------------


class TestWrapStream:
    """Tests for SSEConnectionManager.wrap_stream."""

    @pytest.mark.asyncio
    async def test_wrap_stream_emits_retry_and_events(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")

        async def fake_pipeline():
            yield token_event("Hello", 1)
            yield token_event(" world", 2)

        events = []
        async for sse_text in mgr.wrap_stream(
            "tenant-001", "conv-1", fake_pipeline(), enable_heartbeat=False,
        ):
            events.append(sse_text)

        # First event should be retry directive
        assert events[0].startswith("retry:")
        # Should have 2 token events after retry
        assert len(events) == 3
        assert "token" in events[1]

    @pytest.mark.asyncio
    async def test_wrap_stream_error_recovery(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")

        async def failing_pipeline():
            yield token_event("Hello", 1)
            raise RuntimeError("Pipeline exploded")

        events = []
        async for sse_text in mgr.wrap_stream(
            "tenant-001", "conv-1", failing_pipeline(), enable_heartbeat=False,
        ):
            events.append(sse_text)

        # Should have: retry, token, error, done
        assert len(events) == 4
        assert "error" in events[2]
        assert "done" in events[3]

    @pytest.mark.asyncio
    async def test_wrap_stream_cancelled(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")

        async def slow_pipeline():
            yield token_event("Hello", 1)
            await asyncio.sleep(100)  # Will be cancelled
            yield token_event("Never", 2)

        events = []
        # Collect with a timeout to simulate cancellation
        try:
            async for sse_text in mgr.wrap_stream(
                "tenant-001", "conv-1", slow_pipeline(), enable_heartbeat=False,
            ):
                events.append(sse_text)
                if len(events) >= 2:
                    break  # Cancel after first real event
        except asyncio.CancelledError:
            pass

        assert len(events) >= 2

    @pytest.mark.asyncio
    async def test_wrap_stream_metering_callback_sync(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")

        callback_calls = []

        def sync_callback(tenant_id, conv_id):
            callback_calls.append((tenant_id, conv_id))

        mgr.configure_metering(sync_callback)

        async def fake_pipeline():
            yield token_event("Hello", 1)
            yield token_event(" world", 2)

        events = []
        async for sse_text in mgr.wrap_stream(
            "tenant-001", "conv-1", fake_pipeline(), enable_heartbeat=False,
        ):
            events.append(sse_text)

        # Callback should be called exactly once (first chunk)
        assert len(callback_calls) == 1
        assert callback_calls[0] == ("tenant-001", "conv-1")

    @pytest.mark.asyncio
    async def test_wrap_stream_metering_callback_async(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")

        callback_calls = []

        async def async_callback(tenant_id, conv_id):
            callback_calls.append((tenant_id, conv_id))

        mgr.configure_metering(async_callback)

        async def fake_pipeline():
            yield token_event("Hello", 1)

        events = []
        async for sse_text in mgr.wrap_stream(
            "tenant-001", "conv-1", fake_pipeline(), enable_heartbeat=False,
        ):
            events.append(sse_text)

        assert len(callback_calls) == 1

    @pytest.mark.asyncio
    async def test_wrap_stream_metering_callback_failure(self):
        """Metering callback failure should not break the stream."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-001", "conv-1")

        def broken_callback(tenant_id, conv_id):
            raise RuntimeError("Metering service down")

        mgr.configure_metering(broken_callback)

        async def fake_pipeline():
            yield token_event("Hello", 1)

        events = []
        async for sse_text in mgr.wrap_stream(
            "tenant-001", "conv-1", fake_pipeline(), enable_heartbeat=False,
        ):
            events.append(sse_text)

        # Stream should complete despite callback failure
        assert len(events) == 2  # retry + token


# ---------------------------------------------------------------------------
# Tests — Static formatting methods
# ---------------------------------------------------------------------------


class TestFormattingMethods:
    """Tests for format_retry_directive and format_error_event."""

    def test_format_retry_directive_default(self):
        result = SSEConnectionManager.format_retry_directive()
        assert result == f"retry: {DEFAULT_RETRY_MS}\n\n"

    def test_format_retry_directive_custom(self):
        result = SSEConnectionManager.format_retry_directive(5000)
        assert result == "retry: 5000\n\n"

    def test_format_error_event(self):
        result = SSEConnectionManager.format_error_event(
            message="Something failed",
            code="pipeline_error",
            recoverable=True,
        )
        assert "event: error" in result
        data_line = [line for line in result.split("\n") if line.startswith("data:")][0]
        data = json.loads(data_line.replace("data: ", ""))
        assert data["message"] == "Something failed"
        assert data["code"] == "pipeline_error"
        assert data["recoverable"] is True

    def test_format_error_event_non_recoverable(self):
        result = SSEConnectionManager.format_error_event(
            message="Fatal", code="fatal", recoverable=False,
        )
        data_line = [line for line in result.split("\n") if line.startswith("data:")][0]
        data = json.loads(data_line.replace("data: ", ""))
        assert data["recoverable"] is False


# ---------------------------------------------------------------------------
# Tests — configure_metering
# ---------------------------------------------------------------------------


class TestConfigureMetering:
    """Tests for configure_metering."""

    def test_set_callback(self):
        mgr = SSEConnectionManager()
        cb = MagicMock()
        mgr.configure_metering(cb)
        assert mgr._metering_callback is cb

    def test_clear_callback(self):
        mgr = SSEConnectionManager()
        mgr.configure_metering(MagicMock())
        mgr.configure_metering(None)
        assert mgr._metering_callback is None


# ---------------------------------------------------------------------------
# Tests — cleanup_expired_buffers
# ---------------------------------------------------------------------------


class TestCleanupExpiredBuffers:
    """Tests for cleanup_expired_buffers."""

    def test_removes_expired_buffers(self):
        mgr = SSEConnectionManager()
        mgr._buffers["conv-old"] = EventBuffer()
        mgr._buffers["conv-old"].last_activity = time.monotonic() - BUFFER_EXPIRY_SECONDS - 10
        mgr._buffers["conv-new"] = EventBuffer()

        removed = mgr.cleanup_expired_buffers()

        assert removed == 1
        assert "conv-old" not in mgr._buffers
        assert "conv-new" in mgr._buffers

    def test_no_expired_buffers(self):
        mgr = SSEConnectionManager()
        mgr._buffers["conv-1"] = EventBuffer()

        removed = mgr.cleanup_expired_buffers()
        assert removed == 0


# ---------------------------------------------------------------------------
# Tests — health_summary
# ---------------------------------------------------------------------------


class TestHealthSummary:
    """Tests for health_summary."""

    def test_health_summary_empty(self):
        mgr = SSEConnectionManager()
        summary = mgr.health_summary()

        assert summary["active_connections"] == 0
        assert summary["active_tabs"] == 0
        assert summary["tenants_streaming"] == 0
        assert summary["event_buffers"] == 0
        assert summary["metering_configured"] is False

    def test_health_summary_with_connections(self):
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="tab-a")
        mgr.connect("tenant-1", "conv-2", tab_id="tab-b")
        mgr.connect("tenant-2", "conv-3")
        mgr.configure_metering(lambda t, c: None)

        summary = mgr.health_summary()

        assert summary["active_connections"] == 3
        assert summary["active_tabs"] == 2
        assert summary["tenants_streaming"] == 2
        assert summary["event_buffers"] == 3
        assert summary["metering_configured"] is True


# ---------------------------------------------------------------------------
# Tests — Module singleton
# ---------------------------------------------------------------------------


class TestModuleSingleton:
    """Tests for get_sse_manager singleton."""

    def test_returns_manager_instance(self):
        import src.chat.sse_manager as mod
        old = mod._manager
        mod._manager = None
        try:
            mgr = get_sse_manager()
            assert isinstance(mgr, SSEConnectionManager)
        finally:
            mod._manager = old

    def test_returns_same_instance(self):
        import src.chat.sse_manager as mod
        old = mod._manager
        mod._manager = None
        try:
            mgr1 = get_sse_manager()
            mgr2 = get_sse_manager()
            assert mgr1 is mgr2
        finally:
            mod._manager = old
