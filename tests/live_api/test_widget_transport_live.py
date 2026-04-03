"""
Live transport-level widget regression tests — HTTP POST + SSE streaming.

Verifies the full widget transport round-trip against the deployed environment:
  1. POST /api/chat/conversations → conversation_id + stream_url
  2. POST /api/chat/message → message_id (queued for pipeline)
  3. GET /api/chat/stream/{conversation_id} → SSE events (token, done)

These tests complement the browser-level tests in test_widget_readiness_live.py
by exercising the raw HTTP/SSE transport without Playwright.

Run:
    pytest tests/live_api/test_widget_transport_live.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import httpx
import pytest


# ---------------------------------------------------------------------------
# Tests: HTTP conversation lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.timeout(60)
class TestWidgetTransportHTTP:
    """Verify the HTTP request/response contract for widget chat."""

    def test_wt_01_create_conversation_returns_stream_url(
        self, live_client: httpx.Client, widget_key: str, platform_reachable: None
    ):
        """POST /api/chat/conversations returns conversation_id + stream_url."""
        resp = live_client.post(
            "/api/chat/conversations",
            headers={"X-Widget-Key": widget_key, "Content-Type": "application/json"},
            json={"message": "Hello, I need help with an order."},
        )
        assert resp.status_code in (200, 201), (
            f"Create conversation failed: HTTP {resp.status_code}\n{resp.text[:500]}"
        )
        data = resp.json()
        conv_id = data.get("conversationId") or data.get("conversation_id")
        assert conv_id, f"No conversation_id in response: {list(data.keys())}"

        stream_url = data.get("streamUrl") or data.get("stream_url")
        assert stream_url, f"No stream_url in response: {list(data.keys())}"
        assert conv_id in stream_url, (
            f"stream_url '{stream_url}' does not contain conversation_id '{conv_id}'"
        )

    def test_wt_02_send_message_returns_message_id(
        self, live_client: httpx.Client, widget_key: str, platform_reachable: None
    ):
        """POST /api/chat/message returns message_id for a queued message."""
        # First create a conversation
        create_resp = live_client.post(
            "/api/chat/conversations",
            headers={"X-Widget-Key": widget_key, "Content-Type": "application/json"},
            json={"message": "Hi there"},
        )
        assert create_resp.status_code in (200, 201)
        data = create_resp.json()
        conv_id = data.get("conversationId") or data.get("conversation_id")
        assert conv_id

        # Send a follow-up message
        msg_resp = live_client.post(
            "/api/chat/message",
            headers={"X-Widget-Key": widget_key, "Content-Type": "application/json"},
            json={"conversation_id": conv_id, "content": "What products do you sell?"},
        )
        assert msg_resp.status_code == 200, (
            f"Send message failed: HTTP {msg_resp.status_code}\n{msg_resp.text[:500]}"
        )
        msg_data = msg_resp.json()
        msg_id = msg_data.get("messageId") or msg_data.get("message_id")
        assert msg_id, f"No message_id in response: {list(msg_data.keys())}"

    def test_wt_03_missing_widget_key_rejected(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """POST /api/chat/conversations without widget key returns 401/403."""
        resp = live_client.post(
            "/api/chat/conversations",
            headers={"Content-Type": "application/json"},
            json={"message": "Hello"},
        )
        assert resp.status_code in (401, 403), (
            f"Expected auth rejection, got HTTP {resp.status_code}"
        )

    def test_wt_04_invalid_widget_key_rejected(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """POST /api/chat/conversations with invalid key returns 401/403."""
        resp = live_client.post(
            "/api/chat/conversations",
            headers={
                "X-Widget-Key": "pk_live_invalid_00000000_00000000",
                "Content-Type": "application/json",
            },
            json={"message": "Hello"},
        )
        assert resp.status_code in (401, 403), (
            f"Expected auth rejection, got HTTP {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# Tests: SSE stream transport
# ---------------------------------------------------------------------------


@pytest.mark.timeout(90)
class TestWidgetTransportSSE:
    """Verify the SSE stream delivers AI response events."""

    def test_wt_05_sse_stream_returns_event_stream(
        self, live_client: httpx.Client, widget_key: str, platform_reachable: None
    ):
        """GET /api/chat/stream/{id} returns content-type text/event-stream.

        The stream endpoint requires a pending message to process. We send a
        follow-up message via POST /api/chat/message, then immediately connect
        to the SSE stream for that turn.
        """
        headers = {"X-Widget-Key": widget_key, "Content-Type": "application/json"}

        # Create conversation (initial turn consumed by first response)
        create_resp = live_client.post(
            "/api/chat/conversations",
            headers=headers,
            json={"message": "What is your return policy?"},
        )
        assert create_resp.status_code in (200, 201)
        data = create_resp.json()
        conv_id = data.get("conversationId") or data.get("conversation_id")
        assert conv_id

        # Send a follow-up message to create a pending turn
        msg_resp = live_client.post(
            "/api/chat/message",
            headers=headers,
            json={"conversation_id": conv_id, "content": "Can you tell me more?"},
        )
        assert msg_resp.status_code == 200, f"Send message failed: {msg_resp.status_code}"

        # Connect to SSE stream for the new turn
        with live_client.stream(
            "GET",
            f"/api/chat/stream/{conv_id}",
            headers={"X-Widget-Key": widget_key, "Accept": "text/event-stream"},
            timeout=60.0,
        ) as stream:
            ct = stream.headers.get("content-type", "")
            assert "text/event-stream" in ct, (
                f"Expected text/event-stream, got: {ct} (HTTP {stream.status_code})"
            )

    def test_wt_06_sse_stream_delivers_tokens_and_done(
        self, live_client: httpx.Client, widget_key: str, platform_reachable: None
    ):
        """SSE stream delivers token events followed by a done event."""
        headers = {"X-Widget-Key": widget_key, "Content-Type": "application/json"}

        # Create conversation
        create_resp = live_client.post(
            "/api/chat/conversations",
            headers=headers,
            json={"message": "Tell me about your shipping options."},
        )
        assert create_resp.status_code in (200, 201)
        data = create_resp.json()
        conv_id = data.get("conversationId") or data.get("conversation_id")
        assert conv_id

        # Send follow-up to create a pending turn for the stream
        msg_resp = live_client.post(
            "/api/chat/message",
            headers=headers,
            json={"conversation_id": conv_id, "content": "What are the delivery times?"},
        )
        assert msg_resp.status_code == 200

        # Read SSE events
        events: list[str] = []
        token_data: list[str] = []

        with live_client.stream(
            "GET",
            f"/api/chat/stream/{conv_id}",
            headers={"X-Widget-Key": widget_key, "Accept": "text/event-stream"},
            timeout=60.0,
        ) as stream:
            for line in stream.iter_lines():
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                    events.append(event_type)
                elif line.startswith("data:") and events and events[-1] == "token":
                    token_data.append(line.split(":", 1)[1].strip())

                # Stop after done event
                if events and events[-1] == "done":
                    break

        # Must have received at least one token event
        assert "token" in events, f"No token events received. Events: {events}"

        # Must end with a done event
        assert events[-1] == "done", f"Stream did not end with done. Last events: {events[-5:]}"

        # Token data should contain actual AI-generated text
        combined = " ".join(token_data)
        assert len(combined) > 10, (
            f"Token content too short ({len(combined)} chars) — AI may not have responded"
        )
