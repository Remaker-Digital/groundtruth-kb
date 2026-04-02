"""
Tests for Chat API endpoints — src/chat/endpoints.py.

Covers: configure_chat_services, _get_session, _get_pipeline,
        _load_tenant_context, start_conversation, send_message,
        stream_response, stream_status, get_conversation,
        end_conversation, report_issue, websocket_chat,
        broadcast_to_conversation, _broadcast,
        _extract_last_customer_message, _extract_conversation_history.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.chat.endpoints import (
    _broadcast,
    _extract_conversation_history,
    _extract_last_customer_message,
    _ws_connections,
    broadcast_to_conversation,
    configure_chat_services,
    router,
)
from src.chat.models import (
    ChatMessage,
    ConversationStartResponse,
    ConversationStateResponse,
    EndConversationResponse,
    IssueReportResponse,
    MessageRole,
    SendMessageResponse,
    WebSocketMessage,
    WebSocketMessageType,
)
from src.chat.session import (
    ConversationNotActiveError,
    ConversationNotFoundError,
    TrialLimitReachedError,
    TurnLimitReachedError,
)
from src.multi_tenant.cosmos_schema import TenantTier


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "tenant-001"
    ctx.tier = TenantTier.STARTER
    ctx.status = "active"
    return ctx


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_pipeline():
    return MagicMock()


@pytest.fixture(autouse=True)
def _reset_module_state():
    """Reset module-level globals between tests."""
    import src.chat.endpoints as ep
    old_session = ep._session
    old_pipeline = ep._pipeline
    old_ws = dict(_ws_connections)
    yield
    ep._session = old_session
    ep._pipeline = old_pipeline
    _ws_connections.clear()
    _ws_connections.update(old_ws)


# ---------------------------------------------------------------------------
# Tests — Service configuration
# ---------------------------------------------------------------------------


class TestConfigureChatServices:
    """Tests for configure_chat_services and _get helpers."""

    def test_configure_sets_services(self, mock_session, mock_pipeline):
        import src.chat.endpoints as ep
        configure_chat_services(mock_session, mock_pipeline)
        assert ep._session is mock_session
        assert ep._pipeline is mock_pipeline

    def test_get_session_raises_when_not_configured(self):
        import src.chat.endpoints as ep
        ep._session = None
        with pytest.raises(Exception) as exc_info:
            ep._get_session()
        assert exc_info.value.status_code == 503

    def test_get_pipeline_raises_when_not_configured(self):
        import src.chat.endpoints as ep
        ep._pipeline = None
        with pytest.raises(Exception) as exc_info:
            ep._get_pipeline()
        assert exc_info.value.status_code == 503

    def test_get_session_returns_when_configured(self, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session
        assert ep._get_session() is mock_session

    def test_get_pipeline_returns_when_configured(self, mock_pipeline):
        import src.chat.endpoints as ep
        ep._pipeline = mock_pipeline
        assert ep._get_pipeline() is mock_pipeline


# ---------------------------------------------------------------------------
# Tests — _load_tenant_context
# ---------------------------------------------------------------------------


class TestLoadTenantContext:
    """Tests for _load_tenant_context helper.

    Note: _load_tenant_context does a lazy import inside its body:
        from src.multi_tenant.repository import PreferencesRepository, TenantRepository
    So we must patch at the source module, not at src.chat.endpoints.
    """

    @pytest.mark.asyncio
    async def test_load_tenant_context_success(self, mock_ctx):
        from src.chat.endpoints import _load_tenant_context

        tenant_raw = {
            "id": "tenant-001",
            "tenant_id": "tenant-001",
            "status": "active",
            "billing_channel": "stripe",
            "tier": "starter",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        prefs_raw = {
            "id": "tenant-001:v1",
            "tenant_id": "tenant-001",
            "version": 1,
            "is_current": True,
            "created_at": "2026-01-01T00:00:00Z",
        }

        with patch("src.multi_tenant.repository.TenantRepository") as MockTR, \
             patch("src.multi_tenant.repository.PreferencesRepository") as MockPR:
            MockTR.return_value.read = AsyncMock(return_value=tenant_raw)
            MockPR.return_value.get_current = AsyncMock(return_value=prefs_raw)

            tenant_doc, prefs_doc = await _load_tenant_context(mock_ctx)

        assert tenant_doc.tenant_id == "tenant-001"
        assert prefs_doc.tenant_id == "tenant-001"

    @pytest.mark.asyncio
    async def test_load_tenant_context_fallback_on_error(self, mock_ctx):
        """When both repos raise, the tenant fallback succeeds but the prefs
        fallback fails because PreferencesDocument requires created_at.
        This is a known limitation in the production default-document builder.
        """
        from src.chat.endpoints import _load_tenant_context
        from pydantic import ValidationError

        with patch("src.multi_tenant.repository.TenantRepository") as MockTR, \
             patch("src.multi_tenant.repository.PreferencesRepository") as MockPR:
            MockTR.return_value.read = AsyncMock(side_effect=Exception("boom"))
            MockPR.return_value.get_current = AsyncMock(side_effect=Exception("boom"))

            # The default PreferencesDocument fallback is missing created_at,
            # so this raises a ValidationError (production code gap).
            with pytest.raises(ValidationError, match="created_at"):
                await _load_tenant_context(mock_ctx)

    @pytest.mark.asyncio
    async def test_load_tenant_context_prefs_none(self, mock_ctx):
        """When prefs repo returns None, the fallback PreferencesDocument
        construction fails due to missing created_at (production code gap).
        """
        from src.chat.endpoints import _load_tenant_context
        from pydantic import ValidationError

        with patch("src.multi_tenant.repository.TenantRepository") as MockTR, \
             patch("src.multi_tenant.repository.PreferencesRepository") as MockPR:
            MockTR.return_value.read = AsyncMock(side_effect=Exception("err"))
            MockPR.return_value.get_current = AsyncMock(return_value=None)

            with pytest.raises(ValidationError, match="created_at"):
                await _load_tenant_context(mock_ctx)


# ---------------------------------------------------------------------------
# Tests — POST /api/chat/conversations
# ---------------------------------------------------------------------------


class TestStartConversation:
    """Tests for POST /api/chat/conversations endpoint."""

    @pytest.mark.asyncio
    async def test_start_conversation_success(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.start_conversation = AsyncMock(
            return_value=ConversationStartResponse(
                conversation_id="conv-001",
                stream_url="/api/chat/stream/conv-001",
                ws_url="/ws/chat/conv-001",
                created_at="2026-01-01T00:00:00Z",
            )
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        with patch("src.chat.endpoints.PreferencesRepository") as MockPR:
            MockPR.return_value.get_active = AsyncMock(
                return_value={"activated_at": "2026-01-01T00:00:00Z"}
            )
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/conversations",
                    json={},
                )

        assert resp.status_code == 201
        body = resp.json()
        assert body["conversation_id"] == "conv-001"
        assert "stream_url" in body

    @pytest.mark.asyncio
    async def test_start_conversation_not_activated(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        with patch("src.chat.endpoints.PreferencesRepository") as MockPR:
            MockPR.return_value.get_active = AsyncMock(return_value=None)
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/chat/conversations", json={})

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_start_conversation_deactivated(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        with patch("src.chat.endpoints.PreferencesRepository") as MockPR:
            MockPR.return_value.get_active = AsyncMock(
                return_value={"activated_at": "2026-01-01", "deactivated_at": "2026-02-01"}
            )
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/chat/conversations", json={})

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_start_conversation_trial_limit(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.start_conversation = AsyncMock(
            side_effect=TrialLimitReachedError("tenant-001", 50)
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        with patch("src.chat.endpoints.PreferencesRepository") as MockPR:
            MockPR.return_value.get_active = AsyncMock(
                return_value={"activated_at": "2026-01-01"}
            )
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/chat/conversations", json={})

        assert resp.status_code == 403
        assert "Trial conversation limit" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_start_conversation_503_no_session(self, mock_ctx):
        import src.chat.endpoints as ep
        ep._session = None

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        with patch("src.chat.endpoints.PreferencesRepository") as MockPR:
            MockPR.return_value.get_active = AsyncMock(
                return_value={"activated_at": "2026-01-01"}
            )
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/chat/conversations", json={})

        assert resp.status_code == 503


# ---------------------------------------------------------------------------
# Tests — POST /api/chat/message
# ---------------------------------------------------------------------------


class TestSendMessage:
    """Tests for POST /api/chat/message endpoint."""

    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.add_customer_message_idempotent = AsyncMock(
            return_value=SendMessageResponse(
                message_id="msg-001",
                conversation_id="conv-001",
                turn_count=1,
                accepted=True,
            )
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat/message",
                json={"conversation_id": "conv-001", "content": "Hello"},
            )

        assert resp.status_code == 200
        assert resp.json()["message_id"] == "msg-001"

    @pytest.mark.asyncio
    async def test_send_message_not_found(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.add_customer_message_idempotent = AsyncMock(
            side_effect=ConversationNotFoundError("conv-x", "tenant-001")
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat/message",
                json={"conversation_id": "conv-x", "content": "Hello"},
            )

        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_send_message_not_active(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.add_customer_message_idempotent = AsyncMock(
            side_effect=ConversationNotActiveError("conv-x", "resolved")
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat/message",
                json={"conversation_id": "conv-x", "content": "Hello"},
            )

        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_send_message_turn_limit(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.add_customer_message_idempotent = AsyncMock(
            side_effect=TurnLimitReachedError("conv-x", 50)
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat/message",
                json={"conversation_id": "conv-x", "content": "Hello"},
            )

        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_send_message_in_flight_response(self, mock_ctx, mock_session):
        """P1-2: InFlightResponseError returns structured 409 with code."""
        import src.chat.endpoints as ep
        from src.chat.session import InFlightResponseError
        ep._session = mock_session

        mock_session.add_customer_message_idempotent = AsyncMock(
            side_effect=InFlightResponseError("conv-x")
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat/message",
                json={"conversation_id": "conv-x", "content": "Hello"},
            )

        assert resp.status_code == 409
        body = resp.json()
        assert body["code"] == "in_flight_response"
        assert "retry_after_ms" in body

    @pytest.mark.asyncio
    async def test_send_message_concurrency_exhausted(self, mock_ctx, mock_session):
        """P1-2: ConcurrencyExhaustedError returns structured 409 with code."""
        import src.chat.endpoints as ep
        from src.chat.session import ConcurrencyExhaustedError
        ep._session = mock_session

        mock_session.add_customer_message_idempotent = AsyncMock(
            side_effect=ConcurrencyExhaustedError("conv-x")
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat/message",
                json={"conversation_id": "conv-x", "content": "Hello"},
            )

        assert resp.status_code == 409
        body = resp.json()
        assert body["code"] == "concurrency_exhausted"
        assert "retry_after_ms" in body


# ---------------------------------------------------------------------------
# Tests — GET /api/chat/conversations/{id}
# ---------------------------------------------------------------------------


class TestGetConversation:
    """Tests for GET /api/chat/conversations/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_conversation_success(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.get_conversation = AsyncMock(
            return_value=ConversationStateResponse(
                conversation_id="conv-001",
                status="active",
                turn_count=2,
                message_count=4,
                messages=[],
                created_at="2026-01-01T00:00:00Z",
                last_activity_at="2026-01-01T00:01:00Z",
            )
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/chat/conversations/conv-001")

        assert resp.status_code == 200
        assert resp.json()["conversation_id"] == "conv-001"

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.get_conversation = AsyncMock(
            side_effect=ConversationNotFoundError("conv-x", "tenant-001")
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/chat/conversations/conv-x")

        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Tests — POST /api/chat/conversations/{id}/end
# ---------------------------------------------------------------------------


class TestEndConversation:
    """Tests for POST /api/chat/conversations/{id}/end endpoint."""

    @pytest.mark.asyncio
    async def test_end_conversation_success(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.end_conversation = AsyncMock(
            return_value=EndConversationResponse(
                conversation_id="conv-001",
                status="resolved",
                turn_count=3,
                duration_seconds=120,
                is_billable=True,
            )
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat/conversations/conv-001/end",
                json={"feedback_rating": 5, "feedback_text": "Great!"},
            )

        assert resp.status_code == 200
        assert resp.json()["status"] == "resolved"

    @pytest.mark.asyncio
    async def test_end_conversation_not_found(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.end_conversation = AsyncMock(
            side_effect=ConversationNotFoundError("conv-x", "tenant-001")
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/chat/conversations/conv-x/end")

        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_end_conversation_not_active(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.end_conversation = AsyncMock(
            side_effect=ConversationNotActiveError("conv-x", "resolved")
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/chat/conversations/conv-x/end")

        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Tests — Stream status
# ---------------------------------------------------------------------------


class TestStreamStatus:
    """Tests for GET /api/chat/stream/{id}/status endpoint.

    Note: stream_status does a lazy import inside its body:
        from src.chat.sse_manager import get_sse_manager
    So we must patch at the source module.
    """

    @pytest.mark.asyncio
    async def test_stream_status_returns_data(self, mock_ctx):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        mock_mgr = MagicMock()
        mock_mgr.is_conversation_active.return_value = False
        mock_mgr.get_tab_count.return_value = 0
        mock_mgr.can_connect.return_value = True
        mock_mgr.get_active_count.return_value = 0

        with patch("src.chat.sse_manager.get_sse_manager", return_value=mock_mgr):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/chat/stream/conv-001/status")

        assert resp.status_code == 200
        body = resp.json()
        assert body["conversation_id"] == "conv-001"
        assert body["is_streaming"] is False
        assert body["can_connect"] is True


# ---------------------------------------------------------------------------
# Tests — Report issue
# ---------------------------------------------------------------------------


class TestReportIssue:
    """Tests for POST /api/chat/conversations/{id}/issue endpoint.

    Note: report_issue does lazy imports inside its body:
        from src.multi_tenant.repository import AuditLogRepository
        from src.multi_tenant.cosmos_schema import AuditEventType
    So we must patch at the source modules.
    """

    @pytest.mark.asyncio
    async def test_report_issue_success(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.get_state = AsyncMock(return_value={
            "status": "active",
            "messages": [],
        })
        mock_session._conversation_repo = AsyncMock()
        mock_session._conversation_repo.patch = AsyncMock()

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        with patch("src.multi_tenant.repository.AuditLogRepository") as MockAR:
            MockAR.return_value.log_event = AsyncMock()

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/conversations/conv-001/issue",
                    json={"issue_type": "wrong_information", "details": "Bad answer"},
                )

        assert resp.status_code == 200
        body = resp.json()
        assert body["accepted"] is True
        assert body["conversation_id"] == "conv-001"
        assert body["issue_id"].startswith("issue_")

    @pytest.mark.asyncio
    async def test_report_issue_conversation_not_found(self, mock_ctx, mock_session):
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.get_state = AsyncMock(
            side_effect=ConversationNotFoundError("conv-x", "tenant-001")
        )

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/chat/conversations/conv-x/issue",
                json={"issue_type": "other", "details": ""},
            )

        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_report_issue_persist_failure_still_succeeds(self, mock_ctx, mock_session):
        """Issue report should succeed even if Cosmos DB persist fails."""
        import src.chat.endpoints as ep
        ep._session = mock_session

        mock_session.get_state = AsyncMock(return_value={"status": "active"})
        mock_session._conversation_repo = AsyncMock()
        mock_session._conversation_repo.patch = AsyncMock(side_effect=Exception("DB down"))

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        with patch("src.multi_tenant.repository.AuditLogRepository") as MockAR:
            MockAR.return_value.log_event = AsyncMock(side_effect=Exception("Audit fail"))

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/conversations/conv-001/issue",
                    json={"issue_type": "rude_response", "details": "Not nice"},
                )

        assert resp.status_code == 200
        assert resp.json()["accepted"] is True


# ---------------------------------------------------------------------------
# Tests — Helper functions
# ---------------------------------------------------------------------------


class TestExtractLastCustomerMessage:
    """Tests for _extract_last_customer_message."""

    def test_returns_last_customer_message(self):
        state = ConversationStateResponse(
            conversation_id="c1",
            status="active",
            turn_count=1,
            message_count=3,
            messages=[
                ChatMessage(role=MessageRole.CUSTOMER, content="Hello"),
                ChatMessage(role=MessageRole.AI, content="Hi there"),
                ChatMessage(role=MessageRole.CUSTOMER, content="Question?"),
            ],
            created_at="2026-01-01T00:00:00Z",
            last_activity_at="2026-01-01T00:01:00Z",
        )
        assert _extract_last_customer_message(state) == "Question?"

    def test_returns_none_when_no_customer_messages(self):
        state = ConversationStateResponse(
            conversation_id="c1",
            status="active",
            turn_count=0,
            message_count=1,
            messages=[
                ChatMessage(role=MessageRole.AI, content="Welcome!"),
            ],
            created_at="2026-01-01T00:00:00Z",
            last_activity_at="2026-01-01T00:00:00Z",
        )
        assert _extract_last_customer_message(state) is None

    def test_returns_none_on_empty_messages(self):
        state = ConversationStateResponse(
            conversation_id="c1",
            status="active",
            turn_count=0,
            message_count=0,
            messages=[],
            created_at="2026-01-01T00:00:00Z",
            last_activity_at="2026-01-01T00:00:00Z",
        )
        assert _extract_last_customer_message(state) is None


class TestExtractConversationHistory:
    """Tests for _extract_conversation_history."""

    def test_extracts_history_excluding_last_customer(self):
        state = ConversationStateResponse(
            conversation_id="c1",
            status="active",
            turn_count=1,
            message_count=3,
            messages=[
                ChatMessage(role=MessageRole.CUSTOMER, content="First"),
                ChatMessage(role=MessageRole.AI, content="Reply 1"),
                ChatMessage(role=MessageRole.CUSTOMER, content="Second"),
            ],
            created_at="2026-01-01T00:00:00Z",
            last_activity_at="2026-01-01T00:01:00Z",
        )
        history = _extract_conversation_history(state)
        assert len(history) == 2
        assert history[0] == {"role": "user", "content": "First"}
        assert history[1] == {"role": "assistant", "content": "Reply 1"}

    def test_empty_messages_returns_empty(self):
        state = ConversationStateResponse(
            conversation_id="c1",
            status="active",
            turn_count=0,
            message_count=0,
            messages=[],
            created_at="2026-01-01T00:00:00Z",
            last_activity_at="2026-01-01T00:00:00Z",
        )
        assert _extract_conversation_history(state) == []

    def test_caps_at_max_messages(self):
        msgs = []
        for i in range(30):
            msgs.append(ChatMessage(role=MessageRole.CUSTOMER, content=f"Q{i}"))
            msgs.append(ChatMessage(role=MessageRole.AI, content=f"A{i}"))
        # Add one more customer message as "current turn"
        msgs.append(ChatMessage(role=MessageRole.CUSTOMER, content="Current"))

        state = ConversationStateResponse(
            conversation_id="c1",
            status="active",
            turn_count=30,
            message_count=61,
            messages=msgs,
            created_at="2026-01-01T00:00:00Z",
            last_activity_at="2026-01-01T00:01:00Z",
        )
        history = _extract_conversation_history(state, max_messages=10)
        assert len(history) == 10

    def test_skips_system_messages(self):
        state = ConversationStateResponse(
            conversation_id="c1",
            status="active",
            turn_count=1,
            message_count=4,
            messages=[
                ChatMessage(role=MessageRole.CUSTOMER, content="Hello"),
                ChatMessage(role=MessageRole.SYSTEM, content="Escalated"),
                ChatMessage(role=MessageRole.AI, content="Connecting you"),
                ChatMessage(role=MessageRole.CUSTOMER, content="Current"),
            ],
            created_at="2026-01-01T00:00:00Z",
            last_activity_at="2026-01-01T00:01:00Z",
        )
        history = _extract_conversation_history(state)
        # System messages should be skipped
        roles = [h["role"] for h in history]
        assert "system" not in roles


# ---------------------------------------------------------------------------
# Tests — _broadcast / WebSocket helpers
# ---------------------------------------------------------------------------


class TestBroadcast:
    """Tests for _broadcast and broadcast_to_conversation."""

    @pytest.mark.asyncio
    async def test_broadcast_to_empty_set(self):
        msg = WebSocketMessage(
            type=WebSocketMessageType.TYPING_START,
            conversation_id="conv-001",
        )
        # Should not raise with no connections
        await _broadcast("conv-001", msg)

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all_except_excluded(self):
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        _ws_connections["conv-001"] = {ws1, ws2}

        msg = WebSocketMessage(
            type=WebSocketMessageType.PRESENCE,
            conversation_id="conv-001",
        )
        await _broadcast("conv-001", msg, exclude=ws1)

        ws2.send_json.assert_called_once()
        ws1.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_broadcast_removes_dead_connections(self):
        ws_alive = AsyncMock()
        ws_dead = AsyncMock()
        ws_dead.send_json.side_effect = Exception("Connection closed")
        _ws_connections["conv-001"] = {ws_alive, ws_dead}

        msg = WebSocketMessage(
            type=WebSocketMessageType.PRESENCE,
            conversation_id="conv-001",
        )
        await _broadcast("conv-001", msg)

        # Dead connection should be removed
        assert ws_dead not in _ws_connections.get("conv-001", set())

    @pytest.mark.asyncio
    async def test_broadcast_to_conversation_public_api(self):
        ws = AsyncMock()
        _ws_connections["conv-001"] = {ws}

        msg = WebSocketMessage(
            type=WebSocketMessageType.SYSTEM_EVENT,
            conversation_id="conv-001",
            data={"event": "escalation_started"},
        )
        await broadcast_to_conversation("conv-001", msg)

        ws.send_json.assert_called_once()
