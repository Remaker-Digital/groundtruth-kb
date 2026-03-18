"""Tests for per-message feedback (SPEC-1836).

Covers:
  - WI-1458: Chat feedback API endpoint
  - WI-1459: Widget feedback UI (model/transport layer)
  - WI-1460: Feedback aggregate metrics (superadmin API)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestMessageFeedbackModels:
    """Test SPEC-1836 request/response models."""

    def test_feedback_request_positive(self):
        from src.chat.models import MessageFeedbackRequest
        req = MessageFeedbackRequest(rating="positive")
        assert req.rating == "positive"
        assert req.comment is None

    def test_feedback_request_negative_with_comment(self):
        from src.chat.models import MessageFeedbackRequest
        req = MessageFeedbackRequest(rating="negative", comment="Not accurate")
        assert req.rating == "negative"
        assert req.comment == "Not accurate"

    def test_feedback_request_invalid_rating_rejected(self):
        from src.chat.models import MessageFeedbackRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            MessageFeedbackRequest(rating="neutral")

    def test_feedback_request_comment_max_length(self):
        from src.chat.models import MessageFeedbackRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            MessageFeedbackRequest(rating="positive", comment="x" * 501)

    def test_feedback_response_model(self):
        from src.chat.models import MessageFeedbackResponse
        resp = MessageFeedbackResponse(
            conversation_id="conv-1",
            message_id="msg-1",
            rating="positive",
        )
        assert resp.accepted is True
        assert resp.conversation_id == "conv-1"
        assert resp.message_id == "msg-1"


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------


class TestMessageFeedbackEndpoint:
    """Test POST /api/chat/conversations/{id}/messages/{mid}/feedback."""

    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.get_conversation = AsyncMock()
        session._conversation_repo = MagicMock()
        session._conversation_repo.patch = AsyncMock()
        return session

    @pytest.fixture
    def mock_tenant_context(self):
        from src.multi_tenant.auth import TenantContext
        from src.multi_tenant.cosmos_schema import TenantTier
        return TenantContext(
            tenant_id="test-tenant-001",
            tier=TenantTier.PROFESSIONAL,
            status="active",
            auth_method="widget_key",
            is_widget_auth=True,
        )

    @pytest.fixture
    def conversation_state(self):
        """Mock conversation state with AI messages."""
        from src.chat.models import ChatMessage, MessageRole, ConversationStateResponse
        return ConversationStateResponse(
            conversation_id="conv-123",
            status="active",
            turn_count=2,
            message_count=4,
            messages=[
                ChatMessage(
                    role=MessageRole.CUSTOMER,
                    content="Hello",
                    message_id="msg-1",
                ),
                ChatMessage(
                    role=MessageRole.AI,
                    content="Hi! How can I help?",
                    message_id="msg-2",
                ),
                ChatMessage(
                    role=MessageRole.CUSTOMER,
                    content="What's your return policy?",
                    message_id="msg-3",
                ),
                ChatMessage(
                    role=MessageRole.AI,
                    content="Our return policy is 30 days.",
                    message_id="msg-4",
                ),
            ],
            created_at=datetime.now(timezone.utc).isoformat(),
            last_activity_at=datetime.now(timezone.utc).isoformat(),
        )

    @pytest.mark.asyncio
    async def test_positive_feedback_on_ai_message(
        self, mock_session, mock_tenant_context, conversation_state,
    ):
        """Positive feedback on AI message should succeed and patch Cosmos."""
        from src.chat.models import MessageFeedbackRequest
        from src.chat.endpoints import submit_message_feedback

        mock_session.get_conversation.return_value = conversation_state

        with patch("src.chat.endpoints._session", mock_session):
            result = await submit_message_feedback(
                conversation_id="conv-123",
                message_id="msg-2",
                request=MessageFeedbackRequest(rating="positive"),
                ctx=mock_tenant_context,
            )

        assert result.rating == "positive"
        assert result.conversation_id == "conv-123"
        assert result.message_id == "msg-2"
        assert result.accepted is True

        # Verify Cosmos patch was called
        mock_session._conversation_repo.patch.assert_called_once()
        patch_args = mock_session._conversation_repo.patch.call_args
        assert patch_args[0][0] == "test-tenant-001"
        assert patch_args[0][1] == "conv-123"
        operations = patch_args[0][2]
        assert operations[0]["op"] == "set"
        assert "/messages/1/metadata" in operations[0]["path"]

    @pytest.mark.asyncio
    async def test_negative_feedback_with_comment(
        self, mock_session, mock_tenant_context, conversation_state,
    ):
        """Negative feedback with comment should be recorded."""
        from src.chat.models import MessageFeedbackRequest
        from src.chat.endpoints import submit_message_feedback

        mock_session.get_conversation.return_value = conversation_state

        with patch("src.chat.endpoints._session", mock_session):
            result = await submit_message_feedback(
                conversation_id="conv-123",
                message_id="msg-4",
                request=MessageFeedbackRequest(rating="negative", comment="Inaccurate"),
                ctx=mock_tenant_context,
            )

        assert result.rating == "negative"
        # Verify comment was included in the patch
        operations = mock_session._conversation_repo.patch.call_args[0][2]
        metadata = operations[0]["value"]
        assert metadata["feedback_rating"] == "negative"
        assert metadata["feedback_comment"] == "Inaccurate"

    @pytest.mark.asyncio
    async def test_feedback_on_customer_message_rejected(
        self, mock_session, mock_tenant_context, conversation_state,
    ):
        """Feedback on customer messages should return 422."""
        from src.chat.models import MessageFeedbackRequest
        from src.chat.endpoints import submit_message_feedback
        from fastapi import HTTPException

        mock_session.get_conversation.return_value = conversation_state

        with patch("src.chat.endpoints._session", mock_session):
            with pytest.raises(HTTPException) as exc_info:
                await submit_message_feedback(
                    conversation_id="conv-123",
                    message_id="msg-1",  # Customer message
                    request=MessageFeedbackRequest(rating="positive"),
                    ctx=mock_tenant_context,
                )
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_feedback_on_nonexistent_message_returns_404(
        self, mock_session, mock_tenant_context, conversation_state,
    ):
        """Feedback on a message that doesn't exist should return 404."""
        from src.chat.models import MessageFeedbackRequest
        from src.chat.endpoints import submit_message_feedback
        from fastapi import HTTPException

        mock_session.get_conversation.return_value = conversation_state

        with patch("src.chat.endpoints._session", mock_session):
            with pytest.raises(HTTPException) as exc_info:
                await submit_message_feedback(
                    conversation_id="conv-123",
                    message_id="msg-nonexistent",
                    request=MessageFeedbackRequest(rating="positive"),
                    ctx=mock_tenant_context,
                )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_feedback_on_nonexistent_conversation_returns_404(
        self, mock_session, mock_tenant_context,
    ):
        """Feedback on a conversation that doesn't exist should return 404."""
        from src.chat.models import MessageFeedbackRequest
        from src.chat.endpoints import submit_message_feedback
        from src.chat.session import ConversationNotFoundError
        from fastapi import HTTPException

        mock_session.get_conversation.side_effect = ConversationNotFoundError("conv-999", "test-tenant-001")

        with patch("src.chat.endpoints._session", mock_session):
            with pytest.raises(HTTPException) as exc_info:
                await submit_message_feedback(
                    conversation_id="conv-999",
                    message_id="msg-1",
                    request=MessageFeedbackRequest(rating="positive"),
                    ctx=mock_tenant_context,
                )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_feedback_cosmos_patch_failure_non_fatal(
        self, mock_session, mock_tenant_context, conversation_state,
    ):
        """Cosmos patch failure should not fail the HTTP response."""
        from src.chat.models import MessageFeedbackRequest
        from src.chat.endpoints import submit_message_feedback

        mock_session.get_conversation.return_value = conversation_state
        mock_session._conversation_repo.patch.side_effect = Exception("Cosmos error")

        with patch("src.chat.endpoints._session", mock_session):
            result = await submit_message_feedback(
                conversation_id="conv-123",
                message_id="msg-2",
                request=MessageFeedbackRequest(rating="positive"),
                ctx=mock_tenant_context,
            )

        # Should still succeed even if Cosmos patch fails
        assert result.accepted is True
        assert result.rating == "positive"


# ---------------------------------------------------------------------------
# Superadmin feedback metrics tests
# ---------------------------------------------------------------------------


class TestFeedbackMetrics:
    """Test superadmin feedback analytics (WI-1460)."""

    def test_feedback_summary_model_defaults(self):
        from src.multi_tenant.superadmin_api._feedback import FeedbackSummary
        s = FeedbackSummary()
        assert s.total_feedback == 0
        assert s.positive_count == 0
        assert s.negative_count == 0
        assert s.satisfaction_rate is None

    def test_feedback_summary_with_data(self):
        from src.multi_tenant.superadmin_api._feedback import FeedbackSummary
        s = FeedbackSummary(
            tenant_id="t1",
            total_feedback=10,
            positive_count=8,
            negative_count=2,
            satisfaction_rate=0.8,
            feedback_rate=0.25,
            total_ai_messages=40,
        )
        assert s.satisfaction_rate == 0.8
        assert s.feedback_rate == 0.25

    def test_feedback_detail_model(self):
        from src.multi_tenant.superadmin_api._feedback import FeedbackDetail
        d = FeedbackDetail(
            tenant_id="t1",
            conversation_id="conv-1",
            message_id="msg-1",
            rating="positive",
            comment="Great answer",
            feedback_at="2026-03-17T12:00:00Z",
        )
        assert d.rating == "positive"
        assert d.comment == "Great answer"

    @pytest.mark.asyncio
    async def test_feedback_metrics_empty_results(self):
        """Metrics endpoint with no conversations returns zeroes."""
        from src.multi_tenant.superadmin_api._feedback import get_feedback_metrics
        from src.multi_tenant.superadmin_api import _monolith as _state

        mock_conv_repo = MagicMock()
        mock_conv_repo.query = AsyncMock(return_value=[])
        original = _state._conv_repo

        try:
            _state._conv_repo = mock_conv_repo
            result = await get_feedback_metrics(days=30)
            assert result.platform_summary.total_feedback == 0
            assert result.platform_summary.satisfaction_rate is None
            assert len(result.per_tenant) == 0
        finally:
            _state._conv_repo = original

    @pytest.mark.asyncio
    async def test_feedback_metrics_with_data(self):
        """Metrics endpoint correctly aggregates feedback from conversations."""
        from src.multi_tenant.superadmin_api._feedback import get_feedback_metrics
        from src.multi_tenant.superadmin_api import _monolith as _state

        mock_conversations = [
            {
                "tenant_id": "t1",
                "conversation_id": "conv-1",
                "messages": [
                    {"role": "customer", "content": "Hi"},
                    {"role": "ai", "content": "Hello!", "message_id": "m1",
                     "metadata": {"feedback_rating": "positive"}},
                    {"role": "customer", "content": "Thanks"},
                    {"role": "ai", "content": "You're welcome", "message_id": "m2",
                     "metadata": {"feedback_rating": "positive"}},
                ],
            },
            {
                "tenant_id": "t1",
                "conversation_id": "conv-2",
                "messages": [
                    {"role": "customer", "content": "Help"},
                    {"role": "ai", "content": "Sure", "message_id": "m3",
                     "metadata": {"feedback_rating": "negative", "feedback_comment": "Wrong"}},
                ],
            },
        ]

        mock_conv_repo = MagicMock()
        mock_conv_repo.query = AsyncMock(return_value=mock_conversations)
        original = _state._conv_repo

        try:
            _state._conv_repo = mock_conv_repo
            result = await get_feedback_metrics(days=30)

            # Platform-wide: 2 positive, 1 negative
            assert result.platform_summary.total_feedback == 3
            assert result.platform_summary.positive_count == 2
            assert result.platform_summary.negative_count == 1
            assert result.platform_summary.satisfaction_rate == pytest.approx(0.6667, abs=0.001)

            # Per-tenant (only t1)
            assert len(result.per_tenant) == 1
            t1 = result.per_tenant[0]
            assert t1.tenant_id == "t1"
            assert t1.total_feedback == 3
            assert t1.total_ai_messages == 3
        finally:
            _state._conv_repo = original

    @pytest.mark.asyncio
    async def test_tenant_feedback_details(self):
        """Per-tenant feedback details returns individual records."""
        from src.multi_tenant.superadmin_api._feedback import get_tenant_feedback
        from src.multi_tenant.superadmin_api import _monolith as _state

        mock_conversations = [
            {
                "tenant_id": "t1",
                "conversation_id": "conv-1",
                "messages": [
                    {"role": "ai", "message_id": "m1", "content": "Hi",
                     "metadata": {"feedback_rating": "positive", "feedback_at": "2026-03-17T10:00:00Z"}},
                    {"role": "ai", "message_id": "m2", "content": "Bye",
                     "metadata": {"feedback_rating": "negative",
                                  "feedback_comment": "Wrong info",
                                  "feedback_at": "2026-03-17T11:00:00Z"}},
                ],
            },
        ]

        mock_conv_repo = MagicMock()
        mock_conv_repo.query = AsyncMock(return_value=mock_conversations)
        original = _state._conv_repo

        try:
            _state._conv_repo = mock_conv_repo
            result = await get_tenant_feedback(tenant_id="t1", days=30, limit=100)

            assert len(result) == 2
            # Should be sorted by most recent first
            assert result[0].rating == "negative"
            assert result[0].comment == "Wrong info"
            assert result[1].rating == "positive"
        finally:
            _state._conv_repo = original


# ---------------------------------------------------------------------------
# Widget model tests
# ---------------------------------------------------------------------------


class TestWidgetFeedbackModel:
    """Test Message interface feedback field (WI-1459)."""

    def test_message_interface_supports_feedback_rating(self):
        """The Message type should include feedbackRating field."""
        # This is a TypeScript interface test — we verify the field exists
        # by checking the store module source contains the field.
        import os
        store_path = os.path.join("widget", "src", "state", "store.ts")
        with open(store_path, "r") as f:
            content = f.read()
        assert "feedbackRating" in content
        assert "'positive' | 'negative'" in content

    def test_transport_exports_submit_message_feedback(self):
        """The HTTP transport should export submitMessageFeedback function."""
        import os
        transport_path = os.path.join("widget", "src", "transport", "http.ts")
        with open(transport_path, "r") as f:
            content = f.read()
        assert "submitMessageFeedback" in content
        assert "/messages/" in content
        assert "/feedback" in content

    def test_message_bubble_has_feedback_buttons(self):
        """MessageBubble should render feedback buttons for AI messages."""
        import os
        bubble_path = os.path.join("widget", "src", "components", "MessageBubble.tsx")
        with open(bubble_path, "r") as f:
            content = f.read()
        assert "ThumbUpIcon" in content
        assert "ThumbDownIcon" in content
        assert "onFeedback" in content
        assert "SPEC-1836" in content

    def test_message_list_passes_feedback_callback(self):
        """MessageList should pass onMessageFeedback to MessageBubble."""
        import os
        list_path = os.path.join("widget", "src", "components", "MessageList.tsx")
        with open(list_path, "r") as f:
            content = f.read()
        assert "onMessageFeedback" in content
        assert "onFeedback={onMessageFeedback}" in content
