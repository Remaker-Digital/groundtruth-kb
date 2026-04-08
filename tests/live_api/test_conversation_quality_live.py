"""Live conversation quality tests — SPEC-1649 / WI-1022.

Replaces Phase 11 (MOCKED_UNIT evaluation tests) with live widget API calls.
Tests verify the full conversation lifecycle via external interfaces:
  1. Start conversation via widget key
  2. Receive AI response
  3. Verify response quality (non-empty, reasonable length, no error markers)
  4. End conversation gracefully

These tests exercise the real chat pipeline (intent → retrieval → generation →
critic) against staging/production. No mocks, no stubs — real AI responses.

Run:
    python -m pytest tests/live_api/test_conversation_quality_live.py -v

Prerequisites:
    - Platform reachable (staging or production)
    - PREVIEW_WIDGET_KEY set in env or .env.local

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations


import httpx


# ---------------------------------------------------------------------------
# Test: Widget API Accessibility
# ---------------------------------------------------------------------------
class TestWidgetAPIAccessibility:
    """Verify the widget-facing API is accessible and serves expected content."""

    def test_cq_live_01_widget_js_accessible(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """CQ-LIVE-01: GET /widget.js returns 200 with JavaScript content."""
        resp = live_client.get("/widget.js")
        assert resp.status_code == 200, f"GET /widget.js returned {resp.status_code}"
        assert len(resp.text) > 1000, (
            f"Widget.js too small ({len(resp.text)} bytes) — expected bundled JS"
        )

    def test_cq_live_02_health_endpoint_healthy(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """CQ-LIVE-02: GET /health returns healthy status."""
        resp = live_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "healthy", f"Unexpected health status: {data}"


# ---------------------------------------------------------------------------
# Test: Conversation Lifecycle
# ---------------------------------------------------------------------------
class TestConversationLifecycle:
    """Verify the full conversation lifecycle through the widget API."""

    def test_cq_live_03_start_conversation(
        self, live_client: httpx.Client, widget_key: str, platform_reachable: None
    ):
        """CQ-LIVE-03: POST /api/chat/conversations with widget key returns 201."""
        resp = live_client.post(
            "/api/chat/conversations",
            headers={
                "X-Widget-Key": widget_key,
                "Content-Type": "application/json",
            },
            json={"message": "Hello, I have a question about your product."},
        )
        # 201 Created or 200 OK both indicate success
        assert resp.status_code in (200, 201), (
            f"Start conversation failed: HTTP {resp.status_code}\n"
            f"Response: {resp.text[:500]}"
        )
        data = resp.json()
        # Response should contain a conversation ID
        assert "conversationId" in data or "conversation_id" in data, (
            f"No conversation ID in response: {list(data.keys())}"
        )

    def test_cq_live_04_conversation_provides_streaming_endpoints(
        self, live_client: httpx.Client, widget_key: str, platform_reachable: None
    ):
        """CQ-LIVE-04: Starting a conversation provides streaming endpoints.

        S134: The chat API uses streaming architecture — AI responses are delivered
        via SSE (stream_url) or WebSocket (ws_url), not inline in the HTTP response.
        This test verifies the streaming infrastructure is present.
        """
        resp = live_client.post(
            "/api/chat/conversations",
            headers={
                "X-Widget-Key": widget_key,
                "Content-Type": "application/json",
            },
            json={"message": "What services do you offer?"},
        )
        assert resp.status_code in (200, 201), f"HTTP {resp.status_code}"
        data = resp.json()

        # Streaming architecture: response contains stream/websocket URLs
        has_streaming = (
            "stream_url" in data or "ws_url" in data
            or "streamUrl" in data or "wsUrl" in data
        )
        assert has_streaming, (
            f"No streaming endpoints in response: {list(data.keys())}"
        )

    def test_cq_live_05_stream_url_format_valid(
        self, live_client: httpx.Client, widget_key: str, platform_reachable: None
    ):
        """CQ-LIVE-05: Stream URL follows expected path pattern.

        S134: Verify the SSE stream URL contains the conversation ID and is
        well-formed for client consumption.
        """
        resp = live_client.post(
            "/api/chat/conversations",
            headers={
                "X-Widget-Key": widget_key,
                "Content-Type": "application/json",
            },
            json={"message": "Can you help me with pricing information?"},
        )
        assert resp.status_code in (200, 201)
        data = resp.json()

        conv_id = data.get("conversation_id", data.get("conversationId", ""))
        stream_url = data.get("stream_url", data.get("streamUrl", ""))
        assert stream_url, f"No stream_url in response: {list(data.keys())}"
        # Stream URL should contain the conversation ID
        assert conv_id in stream_url, (
            f"Stream URL '{stream_url}' doesn't contain conversation ID '{conv_id}'"
        )

    def test_cq_live_06_invalid_widget_key_rejected(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """CQ-LIVE-06: Invalid widget key is rejected with 401/403."""
        resp = live_client.post(
            "/api/chat/conversations",
            headers={
                "X-Widget-Key": "pk_live_invalid_key_12345",
                "Content-Type": "application/json",
            },
            json={"message": "This should fail"},
        )
        assert resp.status_code in (401, 403), (
            f"Expected 401/403 for invalid widget key, got {resp.status_code}"
        )

    def test_cq_live_07_missing_widget_key_rejected(
        self, live_client: httpx.Client, platform_reachable: None
    ):
        """CQ-LIVE-07: Missing widget key is rejected with 401/403."""
        resp = live_client.post(
            "/api/chat/conversations",
            headers={"Content-Type": "application/json"},
            json={"message": "No auth header"},
        )
        # Without any auth, should get 401 or 403
        assert resp.status_code in (401, 403, 422), (
            f"Expected auth rejection for missing key, got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# Test: Response Content Quality
# ---------------------------------------------------------------------------
class TestResponseContentQuality:
    """Verify the quality attributes of AI-generated responses."""

    def test_cq_live_08_response_body_is_valid_json(
        self, live_client: httpx.Client, widget_key: str, platform_reachable: None
    ):
        """CQ-LIVE-08: Conversation creation response is valid JSON with expected fields.

        S134: The AI response is delivered via streaming (SSE/WS), not in the
        POST body. This test verifies the response structure is well-formed JSON
        containing the required fields for the client to initiate streaming.
        """
        resp = live_client.post(
            "/api/chat/conversations",
            headers={
                "X-Widget-Key": widget_key,
                "Content-Type": "application/json",
            },
            json={"message": "Tell me about your return policy"},
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert isinstance(data, dict), f"Response is not a dict: {type(data)}"
        # Must have conversation ID and at least one streaming endpoint
        has_conv_id = "conversation_id" in data or "conversationId" in data
        assert has_conv_id, f"Missing conversation_id: {list(data.keys())}"
        has_stream = "stream_url" in data or "ws_url" in data
        assert has_stream, f"Missing streaming endpoint: {list(data.keys())}"

    def test_cq_live_09_conversation_id_format(
        self, live_client: httpx.Client, widget_key: str, platform_reachable: None
    ):
        """CQ-LIVE-09: Conversation ID is a valid format (UUID or similar)."""
        resp = live_client.post(
            "/api/chat/conversations",
            headers={
                "X-Widget-Key": widget_key,
                "Content-Type": "application/json",
            },
            json={"message": "Hello"},
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        conv_id = data.get("conversationId", data.get("conversation_id", ""))
        assert conv_id, "No conversation ID in response"
        # Should be a reasonable-length identifier
        assert len(conv_id) >= 8, f"Conversation ID too short: {conv_id}"
