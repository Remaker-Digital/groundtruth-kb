"""Slice 2: S253 Phase 0 SSE replay fallback behavioral tests.

Tests parse_last_event_id() AND calls the real stream_response() endpoint
via httpx AsyncClient to exercise the three routing branches in event_generator().

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 2

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.chat.endpoints import parse_last_event_id, router
from src.chat.models import MessageRole
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantTier


# ── Helpers ───────────────────────────────────────────────────────

def _make_app():
    app = FastAPI()
    app.include_router(router)
    return app


def _mock_ctx():
    return TenantContext(
        tenant_id="test-tenant",
        tier=TenantTier.PROFESSIONAL,
        status="active",
        auth_method="widget_key",
    )


def _mock_conversation_state(messages=None):
    """Build a mock ConversationStateResponse with customer messages."""
    state = MagicMock()
    msg = MagicMock()
    msg.role = MessageRole.CUSTOMER
    msg.message_id = "msg-001"
    msg.content = "Hello"
    state.messages = messages or [msg]
    state.customer_verified = False
    state.target_agent_id = None
    return state


def _mock_prefs_doc():
    prefs = MagicMock()
    prefs.activated_at = "2026-01-01T00:00:00Z"
    return prefs


# ── parse_last_event_id behavioral tests ──────────────────────────

class TestParseLastEventId:
    """Behavioral tests for parse_last_event_id()."""

    def _mock_request(self, headers=None, query_params=None):
        req = MagicMock()
        req.headers = headers or {}
        req.query_params = query_params or {}
        return req

    def test_header_absent_query_present(self):
        assert parse_last_event_id(self._mock_request(query_params={"last_event_id": "42"})) == 42

    def test_header_present_overrides_query(self):
        assert parse_last_event_id(self._mock_request(
            headers={"last-event-id": "10"}, query_params={"last_event_id": "42"},
        )) == 10

    def test_both_absent_returns_zero(self):
        assert parse_last_event_id(self._mock_request()) == 0

    def test_invalid_non_numeric_returns_zero(self):
        assert parse_last_event_id(self._mock_request(headers={"last-event-id": "x"})) == 0

    def test_empty_string_returns_zero(self):
        assert parse_last_event_id(self._mock_request(headers={"last-event-id": ""})) == 0

    def test_negative_value_preserved(self):
        assert parse_last_event_id(self._mock_request(headers={"last-event-id": "-1"})) == -1

    def test_large_id_preserved(self):
        assert parse_last_event_id(self._mock_request(query_params={"last_event_id": "999999"})) == 999999


# ── stream_response() endpoint-level routing tests ────────────────

class TestStreamResponseEndpoint:
    """Tests that call the real stream_response() endpoint via AsyncClient.

    Each test mocks dependencies (session, pipeline, SSE manager, tenant context)
    and verifies which routing branch is taken by checking SSE manager method calls.
    """

    def _setup_endpoint_mocks(self, mock_sse_mgr, mock_session, mock_pipeline):
        """Configure module-level globals for stream_response."""
        import src.chat.endpoints as ep
        ep._session = mock_session
        ep._pipeline = mock_pipeline

    @pytest.mark.asyncio
    async def test_branch1_fan_out_when_producer_active(self):
        """Branch 1: is_producer_active=True -> fan_out_stream called."""
        mock_sse_mgr = MagicMock()
        mock_sse_mgr.can_connect.return_value = True
        mock_sse_mgr.is_producer_active.return_value = True
        mock_sse_mgr.connect = MagicMock()
        mock_sse_mgr.disconnect = MagicMock()
        mock_sse_mgr.get_tab_count.return_value = 1

        async def fake_fan_out(*args, **kwargs):
            yield "event: token\ndata: fanned-out\n\n"
            yield "event: done\ndata: {}\n\n"

        mock_sse_mgr.fan_out_stream = fake_fan_out

        mock_session = AsyncMock()
        mock_session.get_conversation = AsyncMock(return_value=_mock_conversation_state())

        mock_pipeline = MagicMock()

        self._setup_endpoint_mocks(mock_sse_mgr, mock_session, mock_pipeline)

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = _mock_ctx

        with patch("src.chat.sse_manager.get_sse_manager", return_value=mock_sse_mgr), \
             patch("src.chat.endpoints._load_tenant_context", return_value=(MagicMock(), _mock_prefs_doc())), \
             patch("src.chat.identity_preprocessor.preprocess_identity", AsyncMock(return_value=MagicMock(action="none"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/chat/stream/conv-001")

        assert resp.status_code == 200
        assert "fanned-out" in resp.text
        # Pipeline should NOT have been called (fan-out path)
        mock_pipeline.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_branch2_replay_only_when_completed(self):
        """Branch 2: is_producer_active=False, is_message_completed=True -> replay only."""
        mock_sse_mgr = MagicMock()
        mock_sse_mgr.can_connect.return_value = True
        mock_sse_mgr.is_producer_active.return_value = False
        mock_sse_mgr.is_message_completed.return_value = True
        mock_sse_mgr.get_replay_events.return_value = [
            "event: token\ndata: replayed\n\n",
            "event: done\ndata: {}\n\n",
        ]
        mock_sse_mgr.connect = MagicMock()
        mock_sse_mgr.disconnect = MagicMock()
        mock_sse_mgr.get_tab_count.return_value = 1

        mock_session = AsyncMock()
        mock_session.get_conversation = AsyncMock(return_value=_mock_conversation_state())

        mock_pipeline = MagicMock()

        self._setup_endpoint_mocks(mock_sse_mgr, mock_session, mock_pipeline)

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = _mock_ctx

        with patch("src.chat.sse_manager.get_sse_manager", return_value=mock_sse_mgr), \
             patch("src.chat.endpoints._load_tenant_context", return_value=(MagicMock(), _mock_prefs_doc())), \
             patch("src.chat.identity_preprocessor.preprocess_identity", AsyncMock(return_value=MagicMock(action="none"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/chat/stream/conv-001", headers={"last-event-id": "5"})

        assert resp.status_code == 200
        assert "replayed" in resp.text
        mock_sse_mgr.get_replay_events.assert_called_once()
        mock_pipeline.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_branch3_pipeline_fallback(self):
        """Branch 3: neither active nor completed -> pipeline.execute called."""
        mock_sse_mgr = MagicMock()
        mock_sse_mgr.can_connect.return_value = True
        mock_sse_mgr.is_producer_active.return_value = False
        mock_sse_mgr.is_message_completed.return_value = False
        mock_sse_mgr.get_replay_events.return_value = []
        mock_sse_mgr.connect = MagicMock()
        mock_sse_mgr.disconnect = MagicMock()
        mock_sse_mgr.get_tab_count.return_value = 1

        async def fake_wrap(*args, **kwargs):
            yield "event: token\ndata: from-pipeline\n\n"
            yield "event: done\ndata: {}\n\n"

        mock_sse_mgr.wrap_stream = fake_wrap

        mock_session = AsyncMock()
        mock_session.get_conversation = AsyncMock(return_value=_mock_conversation_state())

        async def fake_pipeline_execute(**kwargs):
            yield MagicMock()

        mock_pipeline = MagicMock()
        mock_pipeline.execute = fake_pipeline_execute

        self._setup_endpoint_mocks(mock_sse_mgr, mock_session, mock_pipeline)

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = _mock_ctx

        with patch("src.chat.sse_manager.get_sse_manager", return_value=mock_sse_mgr), \
             patch("src.chat.endpoints._load_tenant_context", return_value=(MagicMock(), _mock_prefs_doc())), \
             patch("src.chat.identity_preprocessor.preprocess_identity", AsyncMock(return_value=MagicMock(action="none"))):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/chat/stream/conv-001")

        assert resp.status_code == 200
        assert "from-pipeline" in resp.text
