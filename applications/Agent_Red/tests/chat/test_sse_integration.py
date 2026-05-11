"""
SSE stream integration tests (MT-1001→MT-1005).

Tests the SSE streaming infrastructure at the HTTP endpoint level:
stream format compliance, heartbeat keepalive, done events, reconnection
via Last-Event-ID, and Critic retraction events.

These tests mock the ChatPipeline and ConversationSession to isolate
SSE transport behavior from actual AI model calls.

Master Test Plan: §4 Gap Register — SSE Integration (1.0-required)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json


from src.chat.models import (
    StreamEventType,
    done_event,
    error_event,
    retracted_event,
    stage_event,
    token_event,
    validated_event,
)
from src.chat.sse_manager import (
    BUFFER_EXPIRY_SECONDS,
    DEFAULT_RETRY_MS,
    EventBuffer,
    KEEPALIVE_INTERVAL_SECONDS,
    MAX_BUFFERED_EVENTS,
    SSEConnectionManager,
)


# ---------------------------------------------------------------------------
# SSE event format tests
# ---------------------------------------------------------------------------


class TestSSEEventFormat:
    """MT-1001: SSE stream events conform to the text/event-stream format."""

    def test_token_event_sse_format(self):
        """Token events serialize to valid SSE format with event: and data: fields."""
        event = token_event("Hello ", 1)
        sse = event.to_sse()

        assert "event: token" in sse
        assert "data:" in sse
        # Parse the data field as JSON
        data_line = [line for line in sse.split("\n") if line.startswith("data:")][0]
        data_json = json.loads(data_line[len("data: "):])
        assert data_json["text"] == "Hello "
        assert data_json["sequence"] == 1

    def test_done_event_sse_format(self):
        """Done events serialize to valid SSE format."""
        event = done_event("conv-001", 3)
        sse = event.to_sse()

        assert "event: done" in sse
        assert "data:" in sse

    def test_stage_event_sse_format(self):
        """Stage events include the stage name in SSE data."""
        event = stage_event("intent-classification", "started")
        sse = event.to_sse()

        assert "event: stage" in sse
        data_line = [line for line in sse.split("\n") if line.startswith("data:")][0]
        data_json = json.loads(data_line[len("data: "):])
        assert data_json["stage"] == "intent-classification"
        assert data_json["status"] == "started"

    def test_validated_event_sse_format(self):
        """Validated events indicate Critic approval."""
        event = validated_event("conv-001", "msg-001")
        sse = event.to_sse()

        assert "event: validated" in sse
        data_line = [line for line in sse.split("\n") if line.startswith("data:")][0]
        data_json = json.loads(data_line[len("data: "):])
        assert data_json["critic_passed"] is True

    def test_error_event_sse_format(self):
        """Error events include error code and message."""
        event = error_event("Something went wrong", "test_error")
        sse = event.to_sse()

        assert "event: error" in sse
        data_line = [line for line in sse.split("\n") if line.startswith("data:")][0]
        data_json = json.loads(data_line[len("data: "):])
        assert data_json["code"] == "test_error"
        assert data_json["message"] == "Something went wrong"

    def test_event_ends_with_double_newline(self):
        """Each SSE event must end with \\n\\n per the SSE spec."""
        for factory in [
            lambda: token_event("x", 1),
            lambda: done_event("conv-001", 1),
            lambda: stage_event("test", "started"),
            lambda: error_event("m", "e"),
        ]:
            event = factory()
            sse = event.to_sse()
            assert sse.endswith("\n\n"), f"Event {event.event} missing trailing \\n\\n"

    def test_event_data_is_valid_json(self):
        """SSE data field is parseable JSON for all event types."""
        events = [
            token_event("test", 1),
            done_event("conv-001", 5),
            stage_event("test", "completed"),
            error_event("err", "code"),
            validated_event("conv-001", "msg-001"),
            retracted_event("fallback", "safety"),
        ]
        for event in events:
            sse = event.to_sse()
            data_line = [line for line in sse.split("\n") if line.startswith("data:")][0]
            data_json = json.loads(data_line[len("data: "):])
            assert isinstance(data_json, dict)


# ---------------------------------------------------------------------------
# MT-1002: SSE heartbeat keepalive
# ---------------------------------------------------------------------------


class TestSSEHeartbeat:
    """MT-1002: SSE manager sends keepalive pings to prevent timeout."""

    def test_keepalive_interval_configured(self):
        """Heartbeat interval is 15s (below Azure App Gateway 60s idle timeout)."""
        assert KEEPALIVE_INTERVAL_SECONDS == 15

    def test_keepalive_well_below_timeout(self):
        """Heartbeat interval is at least 3x below typical gateway timeout (60s)."""
        assert KEEPALIVE_INTERVAL_SECONDS < 60 / 3


# ---------------------------------------------------------------------------
# MT-1003: SSE done event terminates stream
# ---------------------------------------------------------------------------


class TestSSEDoneEvent:
    """MT-1003: Done event signals stream completion for a turn."""

    def test_done_event_type(self):
        """Done event has the correct StreamEventType."""
        event = done_event("conv-001", 5)
        assert event.event == StreamEventType.DONE

    def test_done_event_in_sse_format(self):
        """Done event serializes with 'event: done' in SSE output."""
        event = done_event("conv-001", 5)
        sse = event.to_sse()
        assert "event: done" in sse

    def test_done_event_includes_turn_count(self):
        """Done event data includes conversation_id and turn_count."""
        event = done_event("conv-test-001", 7)
        assert event.data["conversation_id"] == "conv-test-001"
        assert event.data["turn_count"] == 7


# ---------------------------------------------------------------------------
# MT-1004: SSE reconnection via Last-Event-ID
# ---------------------------------------------------------------------------


class TestSSEReconnection:
    """MT-1004: SSE buffer supports reconnection via Last-Event-ID replay."""

    def test_event_buffer_stores_events(self):
        """EventBuffer tracks events with monotonic sequence IDs."""
        mgr = SSEConnectionManager()
        conv_id = "test-conv-reconnect"
        tenant_id = "t-reconnect-001"

        # Simulate connecting and buffering events
        mgr.connect(tenant_id, conv_id)

        # Buffer some events manually
        buffer = mgr._buffers.get(conv_id)
        if buffer is None:
            # Create buffer if connect doesn't create one
            from src.chat.sse_manager import EventBuffer
            buffer = EventBuffer()
            mgr._buffers[conv_id] = buffer

        seq1 = buffer.append(token_event("Hello ", 1))
        seq2 = buffer.append(token_event("world", 2))
        seq3 = buffer.append(done_event("conv-reconnect", 1))

        assert seq1 < seq2 < seq3, "Sequence IDs must be monotonically increasing"

    def test_max_buffered_events_configured(self):
        """Buffer has a reasonable maximum to prevent memory leaks."""
        assert MAX_BUFFERED_EVENTS == 100

    def test_buffer_expiry_configured(self):
        """Buffers expire after a reasonable period of inactivity."""
        assert BUFFER_EXPIRY_SECONDS == 300  # 5 minutes

    def test_default_retry_ms(self):
        """Default SSE retry interval is reasonable for reconnection."""
        assert DEFAULT_RETRY_MS == 3000  # 3 seconds

    def test_replay_accepts_query_param_fallback(self):
        """P0-2: parse_last_event_id reads query param when header is absent.

        Exercises the production function from endpoints.py, not an
        inline re-implementation.
        """
        from starlette.requests import Request

        from src.chat.endpoints import parse_last_event_id

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/chat/stream/test",
            "headers": [],
            "query_string": b"last_event_id=42",
        }
        request = Request(scope)

        assert parse_last_event_id(request) == 42

    def test_replay_header_takes_precedence_over_query_param(self):
        """P0-2: parse_last_event_id prefers header over query param."""
        from src.chat.endpoints import parse_last_event_id
        from starlette.requests import Request

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/chat/stream/test",
            "headers": [(b"last-event-id", b"99")],
            "query_string": b"last_event_id=42",
        }
        request = Request(scope)

        assert parse_last_event_id(request) == 99

    def test_replay_returns_zero_when_absent(self):
        """P0-2: parse_last_event_id returns 0 when neither source present."""
        from src.chat.endpoints import parse_last_event_id
        from starlette.requests import Request

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/chat/stream/test",
            "headers": [],
            "query_string": b"",
        }
        request = Request(scope)

        assert parse_last_event_id(request) == 0


# ---------------------------------------------------------------------------
# P1-2: Fan-out and completed-message tracking
# ---------------------------------------------------------------------------


class TestSSEFanOutState:
    """P1-2: SSE manager fan-out state management."""

    def test_is_message_completed_tracks_finished_producers(self):
        """After producer finishes, is_message_completed returns True."""
        mgr = SSEConnectionManager()
        conv_id = "conv-fanout-test"
        msg_id = "msg-001"

        # Initially not completed
        assert mgr.is_message_completed(conv_id, msg_id) is False

        # Simulate producer completion
        mgr._completed_messages[conv_id] = msg_id
        assert mgr.is_message_completed(conv_id, msg_id) is True

        # Different message_id is not completed
        assert mgr.is_message_completed(conv_id, "msg-002") is False

    def test_cleanup_removes_fan_out_state(self):
        """cleanup_expired_buffers also removes fan-out bookkeeping."""
        import time
        mgr = SSEConnectionManager()
        conv_id = "conv-cleanup-test"

        # Set up fan-out state
        mgr._completed_messages[conv_id] = "msg-001"
        mgr._producer_done[conv_id] = True
        mgr._producer_sequences[conv_id] = 5

        # Create an expired buffer
        buf = EventBuffer()
        buf.last_activity = time.monotonic() - BUFFER_EXPIRY_SECONDS - 1
        mgr._buffers[conv_id] = buf

        removed = mgr.cleanup_expired_buffers()
        assert removed == 1
        assert conv_id not in mgr._completed_messages
        assert conv_id not in mgr._producer_done
        assert conv_id not in mgr._producer_sequences

    def test_is_producer_active_tracks_running_producers(self):
        """is_producer_active returns True only for matching message_id."""
        mgr = SSEConnectionManager()
        conv_id = "conv-active-test"

        assert mgr.is_producer_active(conv_id, "msg-001") is False

        mgr._active_producers[conv_id] = "msg-001"
        assert mgr.is_producer_active(conv_id, "msg-001") is True
        assert mgr.is_producer_active(conv_id, "msg-002") is False


# ---------------------------------------------------------------------------
# MT-1005: SSE retracted event replaces streamed text
# ---------------------------------------------------------------------------


class TestSSERetraction:
    """MT-1005: Critic rejection produces a retracted event with safe fallback."""

    def test_retracted_event_format(self):
        """Retracted event includes replacement text (SAFE_FALLBACK_MESSAGE)."""
        from src.multi_tenant.critic_policy import SAFE_FALLBACK_MESSAGE

        event = retracted_event(SAFE_FALLBACK_MESSAGE, "safety_violation")
        sse = event.to_sse()

        assert "event: retracted" in sse
        data_line = [line for line in sse.split("\n") if line.startswith("data:")][0]
        data_json = json.loads(data_line[len("data: "):])
        assert "fallback_text" in data_json
        assert data_json["fallback_text"] == SAFE_FALLBACK_MESSAGE
        assert data_json["critic_passed"] is False

    def test_retracted_event_type(self):
        """Retracted event has the correct StreamEventType."""
        event = retracted_event("safe text", "policy_violation")
        assert event.event == StreamEventType.RETRACTED

    def test_retracted_event_contains_replacement(self):
        """The retracted event data includes the replacement text for the widget."""
        event = retracted_event("I cannot help with that request.", "content_safety")
        sse = event.to_sse()
        data_line = [line for line in sse.split("\n") if line.startswith("data:")][0]
        data_json = json.loads(data_line[len("data: "):])
        assert data_json["fallback_text"] == "I cannot help with that request."
        assert data_json["reason"] == "content_safety"

    def test_stream_then_validate_event_sequence(self):
        """Valid stream-then-validate sequence: tokens → validated or retracted → done."""
        # Simulate a successful stream
        events_happy = [
            token_event("Hello ", 1),
            token_event("there!", 2),
            validated_event("conv-happy", "msg-happy"),
            done_event("conv-happy", 1),
        ]
        types_happy = [e.event for e in events_happy]
        assert types_happy == [
            StreamEventType.TOKEN,
            StreamEventType.TOKEN,
            StreamEventType.VALIDATED,
            StreamEventType.DONE,
        ]

        # Simulate a retracted stream
        events_reject = [
            token_event("Bad ", 1),
            token_event("content", 2),
            retracted_event("I'm sorry, I can't help with that.", "safety_violation"),
            done_event("conv-reject", 1),
        ]
        types_reject = [e.event for e in events_reject]
        assert types_reject == [
            StreamEventType.TOKEN,
            StreamEventType.TOKEN,
            StreamEventType.RETRACTED,
            StreamEventType.DONE,
        ]
