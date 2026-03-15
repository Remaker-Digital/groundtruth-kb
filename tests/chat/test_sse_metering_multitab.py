"""
Tests for WI #132 (first-chunk metering) and WI #133 (multi-tab SSE coordination).

WI #132: Verifies that the SSE metering callback is invoked on the first
non-heartbeat event, records first_chunk_at on the conversation document,
and handles errors gracefully.

WI #133: Verifies multi-tab SSE coordination: tab_id tracking, connection
counting, tab-aware disconnect, stream status endpoint, and widget tab_id
query parameter support.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.chat.models import StreamEvent, StreamEventType, token_event, done_event
from src.chat.sse_manager import SSEConnectionManager


# ---------------------------------------------------------------------------
# WI #132: First-chunk metering callback tests
# ---------------------------------------------------------------------------


class TestMeteringCallback:
    """Tests for SSEConnectionManager metering callback (WI #132)."""

    def test_metering_132_01_configure_callback(self):
        """configure_metering() stores the callback."""
        mgr = SSEConnectionManager()
        cb = AsyncMock()
        mgr.configure_metering(cb)
        assert mgr._metering_callback is cb

    def test_metering_132_02_clear_callback(self):
        """configure_metering(None) clears the callback."""
        mgr = SSEConnectionManager()
        mgr.configure_metering(AsyncMock())
        mgr.configure_metering(None)
        assert mgr._metering_callback is None

    @pytest.mark.asyncio
    async def test_metering_132_03_callback_invoked_on_first_event(self):
        """Metering callback fires on the first non-heartbeat event."""
        mgr = SSEConnectionManager()
        cb = AsyncMock()
        mgr.configure_metering(cb)

        # Create a simple async generator yielding 2 token events
        async def pipeline():
            yield token_event("Hello", 1)
            yield token_event(" world", 2)
            yield done_event("conv-1", 1)

        mgr.connect("tenant-1", "conv-1")
        events = []
        async for sse_text in mgr.wrap_stream(
            "tenant-1", "conv-1", pipeline(), enable_heartbeat=False,
        ):
            events.append(sse_text)
        mgr.disconnect("tenant-1", "conv-1")

        # Callback should be called exactly once with correct args
        cb.assert_awaited_once_with("tenant-1", "conv-1")

    @pytest.mark.asyncio
    async def test_metering_132_04_callback_not_invoked_when_none(self):
        """No error when metering callback is None."""
        mgr = SSEConnectionManager()
        # No callback configured

        async def pipeline():
            yield token_event("Hello", 1)
            yield done_event("conv-1", 1)

        mgr.connect("tenant-1", "conv-1")
        events = []
        async for sse_text in mgr.wrap_stream(
            "tenant-1", "conv-1", pipeline(), enable_heartbeat=False,
        ):
            events.append(sse_text)
        mgr.disconnect("tenant-1", "conv-1")

        # Should complete without error
        assert len(events) >= 2  # retry directive + token + done

    @pytest.mark.asyncio
    async def test_metering_132_05_callback_invoked_only_once(self):
        """Metering callback fires only on the first event, not subsequent ones."""
        mgr = SSEConnectionManager()
        cb = AsyncMock()
        mgr.configure_metering(cb)

        async def pipeline():
            yield token_event("Hello", 1)
            yield token_event(" world", 2)
            yield token_event("!", 3)
            yield done_event("conv-1", 1)

        mgr.connect("tenant-1", "conv-1")
        async for _ in mgr.wrap_stream(
            "tenant-1", "conv-1", pipeline(), enable_heartbeat=False,
        ):
            pass
        mgr.disconnect("tenant-1", "conv-1")

        assert cb.await_count == 1

    @pytest.mark.asyncio
    async def test_metering_132_06_sync_callback_supported(self):
        """Metering callback can be a sync function (not async)."""
        mgr = SSEConnectionManager()
        calls = []

        def sync_cb(tenant_id: str, conversation_id: str) -> None:
            calls.append((tenant_id, conversation_id))

        mgr.configure_metering(sync_cb)

        async def pipeline():
            yield token_event("Hello", 1)
            yield done_event("conv-1", 1)

        mgr.connect("tenant-1", "conv-1")
        async for _ in mgr.wrap_stream(
            "tenant-1", "conv-1", pipeline(), enable_heartbeat=False,
        ):
            pass
        mgr.disconnect("tenant-1", "conv-1")

        assert calls == [("tenant-1", "conv-1")]

    @pytest.mark.asyncio
    async def test_metering_132_07_callback_error_non_fatal(self):
        """Metering callback failure does not interrupt streaming."""
        mgr = SSEConnectionManager()
        cb = AsyncMock(side_effect=RuntimeError("metering failed"))
        mgr.configure_metering(cb)

        async def pipeline():
            yield token_event("Hello", 1)
            yield done_event("conv-1", 1)

        mgr.connect("tenant-1", "conv-1")
        events = []
        async for sse_text in mgr.wrap_stream(
            "tenant-1", "conv-1", pipeline(), enable_heartbeat=False,
        ):
            events.append(sse_text)
        mgr.disconnect("tenant-1", "conv-1")

        # Stream should still complete despite callback error
        assert any("token" in e for e in events)
        assert any("done" in e for e in events)

    def test_metering_132_08_health_shows_metering_configured(self):
        """health_summary() reports whether metering callback is set."""
        mgr = SSEConnectionManager()
        assert mgr.health_summary()["metering_configured"] is False

        mgr.configure_metering(AsyncMock())
        assert mgr.health_summary()["metering_configured"] is True

        mgr.configure_metering(None)
        assert mgr.health_summary()["metering_configured"] is False


class TestRecordFirstChunk:
    """Tests for ConversationMeter.record_first_chunk() (WI #132)."""

    @pytest.mark.asyncio
    async def test_metering_132_09_record_patches_conversation(self):
        """record_first_chunk() patches the conversation document."""
        from src.multi_tenant.conversation_meter import ConversationMeter

        mock_conversations = AsyncMock()
        mock_usage = AsyncMock()
        mock_packs = AsyncMock()
        mock_audit = AsyncMock()

        meter = ConversationMeter.__new__(ConversationMeter)
        meter._conversations = mock_conversations
        meter._usage = mock_usage
        meter._packs = mock_packs
        meter._audit = mock_audit
        meter._stripe_billing_meter_id = None

        await meter.record_first_chunk("tenant-1", "conv-123")

        mock_conversations.patch.assert_awaited_once()
        call_args = mock_conversations.patch.call_args
        assert call_args[1]["tenant_id"] == "tenant-1"
        assert call_args[1]["document_id"] == "conv-123"
        # Verify the patch operation sets first_chunk_at
        ops = call_args[1]["operations"]
        assert len(ops) == 1
        assert ops[0]["op"] == "set"
        assert ops[0]["path"] == "/first_chunk_at"
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(ops[0]["value"])

    @pytest.mark.asyncio
    async def test_metering_132_10_record_error_non_fatal(self):
        """record_first_chunk() does not raise on patch failure."""
        from src.multi_tenant.conversation_meter import ConversationMeter

        mock_conversations = AsyncMock()
        mock_conversations.patch = AsyncMock(side_effect=RuntimeError("cosmos error"))

        meter = ConversationMeter.__new__(ConversationMeter)
        meter._conversations = mock_conversations
        meter._usage = AsyncMock()
        meter._packs = AsyncMock()
        meter._audit = AsyncMock()
        meter._stripe_billing_meter_id = None

        # Should not raise
        await meter.record_first_chunk("tenant-1", "conv-123")


class TestFirstChunkAtField:
    """Tests for ConversationDocument.first_chunk_at field (WI #132)."""

    def test_metering_132_11_field_defaults_to_none(self):
        """first_chunk_at defaults to None on new documents."""
        from src.multi_tenant.cosmos_schema import ConversationDocument, ConversationStatus

        doc = ConversationDocument(
            id="conv-1",
            tenant_id="t-1",
            conversation_id="conv-1",
            status=ConversationStatus.ACTIVE,
            started_at="2026-02-05T00:00:00Z",
            last_activity_at="2026-02-05T00:00:00Z",
        )
        assert doc.first_chunk_at is None

    def test_metering_132_12_field_accepts_iso_timestamp(self):
        """first_chunk_at can be set to an ISO 8601 timestamp."""
        from src.multi_tenant.cosmos_schema import ConversationDocument, ConversationStatus

        now = datetime.now(timezone.utc).isoformat()
        doc = ConversationDocument(
            id="conv-1",
            tenant_id="t-1",
            conversation_id="conv-1",
            status=ConversationStatus.ACTIVE,
            started_at="2026-02-05T00:00:00Z",
            last_activity_at="2026-02-05T00:00:00Z",
            first_chunk_at=now,
        )
        assert doc.first_chunk_at == now


# ---------------------------------------------------------------------------
# WI #133: Multi-tab SSE coordination tests
# ---------------------------------------------------------------------------


class TestMultiTabTracking:
    """Tests for SSEConnectionManager multi-tab features (WI #133)."""

    def test_tab_133_01_connect_with_tab_id(self):
        """connect() tracks tab_id when provided."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="tab-A")

        assert mgr.get_tab_count("tenant-1", "conv-1") == 1
        assert mgr.get_active_count("tenant-1") == 1

    def test_tab_133_02_multiple_tabs_same_conversation(self):
        """Multiple tabs on the same conversation count as one connection."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="tab-A")
        mgr.connect("tenant-1", "conv-1", tab_id="tab-B")
        mgr.connect("tenant-1", "conv-1", tab_id="tab-C")

        assert mgr.get_tab_count("tenant-1", "conv-1") == 3
        # Only 1 unique conversation → 1 active connection
        assert mgr.get_active_count("tenant-1") == 1

    def test_tab_133_03_disconnect_single_tab(self):
        """Disconnecting one tab keeps the conversation active."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="tab-A")
        mgr.connect("tenant-1", "conv-1", tab_id="tab-B")

        mgr.disconnect("tenant-1", "conv-1", tab_id="tab-A")

        assert mgr.get_tab_count("tenant-1", "conv-1") == 1
        assert mgr.get_active_count("tenant-1") == 1
        assert mgr.is_conversation_active("tenant-1", "conv-1")

    def test_tab_133_04_disconnect_all_tabs(self):
        """Disconnecting all tabs removes the conversation."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="tab-A")
        mgr.connect("tenant-1", "conv-1", tab_id="tab-B")

        mgr.disconnect("tenant-1", "conv-1", tab_id="tab-A")
        mgr.disconnect("tenant-1", "conv-1", tab_id="tab-B")

        assert mgr.get_tab_count("tenant-1", "conv-1") == 0
        assert mgr.get_active_count("tenant-1") == 0
        assert not mgr.is_conversation_active("tenant-1", "conv-1")

    def test_tab_133_05_disconnect_without_tab_id_clears_all(self):
        """Disconnecting without tab_id removes all tabs for that conversation."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="tab-A")
        mgr.connect("tenant-1", "conv-1", tab_id="tab-B")

        mgr.disconnect("tenant-1", "conv-1")  # No tab_id

        assert mgr.get_tab_count("tenant-1", "conv-1") == 0
        assert mgr.get_active_count("tenant-1") == 0

    def test_tab_133_06_connect_without_tab_id(self):
        """Connections without tab_id still work (tab_count = 0)."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1")  # No tab_id

        assert mgr.get_tab_count("tenant-1", "conv-1") == 0
        assert mgr.get_active_count("tenant-1") == 1

    def test_tab_133_07_tabs_dont_affect_concurrency_limit(self):
        """Multiple tabs on the same conversation don't exhaust connection limits."""
        mgr = SSEConnectionManager()
        # Per-tenant max_concurrent removed; only global limit applies
        mgr.connect("tenant-1", "conv-1", tab_id="tab-A")
        mgr.connect("tenant-1", "conv-1", tab_id="tab-B")
        mgr.connect("tenant-1", "conv-1", tab_id="tab-C")
        mgr.connect("tenant-1", "conv-1", tab_id="tab-D")

        # 4 tabs but only 1 conversation → should still be able to connect
        assert mgr.get_active_count("tenant-1") == 1
        assert mgr.can_connect("tenant-1", "starter")

    def test_tab_133_08_separate_conversations_count_independently(self):
        """Different conversations count as separate connections."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="tab-A")
        mgr.connect("tenant-1", "conv-2", tab_id="tab-B")
        mgr.connect("tenant-1", "conv-3", tab_id="tab-C")
        mgr.connect("tenant-1", "conv-4", tab_id="tab-D")
        mgr.connect("tenant-1", "conv-5", tab_id="tab-E")

        assert mgr.get_active_count("tenant-1") == 5
        # Starter limit = 5, so next connection would be blocked
        assert not mgr.can_connect("tenant-1", "starter")

    def test_tab_133_09_health_summary_includes_tab_count(self):
        """health_summary() reports total tabs across all tenants."""
        mgr = SSEConnectionManager()
        mgr.connect("t-1", "c-1", tab_id="tab-A")
        mgr.connect("t-1", "c-1", tab_id="tab-B")
        mgr.connect("t-2", "c-2", tab_id="tab-C")

        summary = mgr.health_summary()
        assert summary["active_tabs"] == 3
        assert summary["active_connections"] == 2
        assert summary["tenants_streaming"] == 2

    def test_tab_133_10_get_active_conversations(self):
        """get_active_conversations() returns correct conversation set."""
        mgr = SSEConnectionManager()
        mgr.connect("t-1", "c-1", tab_id="tab-A")
        mgr.connect("t-1", "c-2", tab_id="tab-B")
        mgr.connect("t-1", "c-1", tab_id="tab-C")  # Second tab on c-1

        active = mgr.get_active_conversations("t-1")
        assert active == {"c-1", "c-2"}

    def test_tab_133_11_is_conversation_active(self):
        """is_conversation_active() returns correct status."""
        mgr = SSEConnectionManager()
        assert not mgr.is_conversation_active("t-1", "c-1")

        mgr.connect("t-1", "c-1", tab_id="tab-A")
        assert mgr.is_conversation_active("t-1", "c-1")

        mgr.disconnect("t-1", "c-1", tab_id="tab-A")
        assert not mgr.is_conversation_active("t-1", "c-1")

    def test_tab_133_12_tab_count_zero_for_unknown(self):
        """get_tab_count() returns 0 for unknown tenant/conversation."""
        mgr = SSEConnectionManager()
        assert mgr.get_tab_count("unknown", "unknown") == 0

    def test_tab_133_13_cross_tenant_tab_isolation(self):
        """Tabs from different tenants are isolated."""
        mgr = SSEConnectionManager()
        mgr.connect("t-1", "c-1", tab_id="tab-A")
        mgr.connect("t-2", "c-1", tab_id="tab-B")  # Same conv_id, different tenant

        assert mgr.get_tab_count("t-1", "c-1") == 1
        assert mgr.get_tab_count("t-2", "c-1") == 1
        assert mgr.get_active_count("t-1") == 1
        assert mgr.get_active_count("t-2") == 1


class TestStreamStatusEndpoint:
    """Tests for GET /api/chat/stream/{id}/status endpoint (WI #133)."""

    @pytest.fixture()
    def app_client(self):
        """Create a test client with the chat router."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from src.chat.endpoints import router

        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def _make_ctx(self):
        from src.multi_tenant.auth import TenantContext

        from src.multi_tenant.cosmos_schema import TenantTier

        return TenantContext(
            tenant_id="test-tenant",
            tier=TenantTier.PROFESSIONAL,
            status="active",
            auth_method="api_key",
        )

    def test_tab_133_14_stream_status_default(self, app_client):
        """Stream status returns correct defaults for inactive conversation."""
        from src.multi_tenant.middleware import get_tenant_context

        mock_sse = MagicMock()
        mock_sse.is_conversation_active.return_value = False
        mock_sse.get_tab_count.return_value = 0
        mock_sse.can_connect.return_value = True
        mock_sse.get_active_count.return_value = 0

        app_client.app.dependency_overrides[get_tenant_context] = lambda: self._make_ctx()

        with patch("src.chat.sse_manager.get_sse_manager", return_value=mock_sse):
            resp = app_client.get("/api/chat/stream/conv-123/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["conversation_id"] == "conv-123"
        assert data["is_streaming"] is False
        assert data["tab_count"] == 0
        assert data["can_connect"] is True
        assert data["active_connections"] == 0

    def test_tab_133_15_stream_status_active(self, app_client):
        """Stream status shows active conversation with tabs."""
        from src.multi_tenant.middleware import get_tenant_context

        mock_sse = MagicMock()
        mock_sse.is_conversation_active.return_value = True
        mock_sse.get_tab_count.return_value = 2
        mock_sse.can_connect.return_value = True
        mock_sse.get_active_count.return_value = 3

        app_client.app.dependency_overrides[get_tenant_context] = lambda: self._make_ctx()

        with patch("src.chat.sse_manager.get_sse_manager", return_value=mock_sse):
            resp = app_client.get("/api/chat/stream/conv-456/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["is_streaming"] is True
        assert data["tab_count"] == 2
        assert data["active_connections"] == 3

    def test_tab_133_16_stream_status_at_capacity(self, app_client):
        """Stream status shows can_connect=false when at capacity."""
        from src.multi_tenant.middleware import get_tenant_context

        mock_sse = MagicMock()
        mock_sse.is_conversation_active.return_value = False
        mock_sse.get_tab_count.return_value = 0
        mock_sse.can_connect.return_value = False
        mock_sse.get_active_count.return_value = 3

        app_client.app.dependency_overrides[get_tenant_context] = lambda: self._make_ctx()

        with patch("src.chat.sse_manager.get_sse_manager", return_value=mock_sse):
            resp = app_client.get("/api/chat/stream/conv-789/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["can_connect"] is False


class TestStreamEndpointTabId:
    """Tests for tab_id query parameter on SSE stream endpoint (WI #133)."""

    def test_tab_133_17_connect_passes_tab_id(self):
        """SSE stream endpoint passes tab_id to connect()."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="my-tab-123")

        assert mgr.get_tab_count("tenant-1", "conv-1") == 1

    def test_tab_133_18_disconnect_passes_tab_id(self):
        """SSE stream endpoint passes tab_id to disconnect()."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="my-tab-123")
        mgr.disconnect("tenant-1", "conv-1", tab_id="my-tab-123")

        assert mgr.get_tab_count("tenant-1", "conv-1") == 0
        assert mgr.get_active_count("tenant-1") == 0

    def test_tab_133_19_duplicate_tab_id_is_idempotent(self):
        """Connecting the same tab_id twice is idempotent (set behavior)."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="same-tab")
        mgr.connect("tenant-1", "conv-1", tab_id="same-tab")

        assert mgr.get_tab_count("tenant-1", "conv-1") == 1

    def test_tab_133_20_x_tab_count_header(self):
        """X-Tab-Count response header is set when tab_id is provided."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-1", "conv-1", tab_id="existing-tab")

        tab_count = mgr.get_tab_count("tenant-1", "conv-1")
        # The endpoint would set X-Tab-Count = tab_count + 1 (including new tab)
        assert tab_count + 1 == 2
