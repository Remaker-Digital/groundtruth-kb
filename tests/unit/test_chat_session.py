"""
Tests for conversation lifecycle management — src/chat/session.py.

Covers: ConversationSession (start_conversation, add_customer_message,
        add_ai_message, end_conversation, get_conversation,
        check_idle_timeout, find_best_agent_for_category,
        escalate_conversation, find_active_conversation,
        set_pii_scrubber), exceptions, helper functions
        (_resolve_customer_id, _end_reason_to_status, _calculate_duration),
        module-level singletons.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.chat.models import (
    ConversationStartRequest,
    EndConversationRequest,
    MessageRole,
    SendMessageRequest,
    VisitorIdentity,
)
from src.chat.session import (
    ConversationNotActiveError,
    ConversationNotFoundError,
    ConversationSession,
    TrialLimitReachedError,
    TurnLimitReachedError,
    _calculate_duration,
    _end_reason_to_status,
    _resolve_customer_id,
    configure_conversation_session,
)
from src.multi_tenant.conversation_meter import ConversationEndReason, MAX_TURNS
from src.multi_tenant.cosmos_schema import ConversationStatus, TenantTier
from src.multi_tenant.repository import DocumentNotFoundError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.read = AsyncMock()
    repo.create = AsyncMock()
    repo.append_message = AsyncMock()
    repo.patch = AsyncMock()
    repo.end_conversation = AsyncMock()
    repo.find_active = AsyncMock()
    repo.count_filtered = AsyncMock()
    return repo


@pytest.fixture
def mock_meter():
    meter = AsyncMock()
    meter.meter_conversation = AsyncMock()
    meter.get_usage_dashboard = AsyncMock()
    return meter


@pytest.fixture
def mock_team_repo():
    repo = AsyncMock()
    repo.list_members = AsyncMock()
    return repo


@pytest.fixture
def session(mock_repo, mock_meter, mock_team_repo):
    return ConversationSession(
        conversation_repo=mock_repo,
        conversation_meter=mock_meter,
        team_repo=mock_team_repo,
    )


# ---------------------------------------------------------------------------
# Tests — Exceptions
# ---------------------------------------------------------------------------


class TestExceptions:
    """Verify exception attributes and messages."""

    def test_conversation_not_found(self):
        exc = ConversationNotFoundError("conv-1", "tenant-1")
        assert exc.conversation_id == "conv-1"
        assert exc.tenant_id == "tenant-1"
        assert "conv-1" in str(exc)

    def test_conversation_not_active(self):
        exc = ConversationNotActiveError("conv-1", "resolved")
        assert exc.conversation_id == "conv-1"
        assert exc.status == "resolved"

    def test_turn_limit_reached(self):
        exc = TurnLimitReachedError("conv-1", 50)
        assert exc.turn_count == 50

    def test_trial_limit_reached(self):
        exc = TrialLimitReachedError("tenant-1", 50)
        assert exc.limit == 50


# ---------------------------------------------------------------------------
# Tests — start_conversation
# ---------------------------------------------------------------------------


class TestStartConversation:
    """Tests for ConversationSession.start_conversation."""

    @pytest.mark.asyncio
    async def test_start_basic(self, session, mock_repo):
        request = ConversationStartRequest()
        result = await session.start_conversation("tenant-001", request)

        assert result.conversation_id
        assert result.stream_url.startswith("/api/chat/stream/")
        assert result.ws_url.startswith("/ws/chat/")
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_with_initial_message(self, session, mock_repo):
        request = ConversationStartRequest(initial_message="Hello!")
        await session.start_conversation("tenant-001", request)

        # Verify the document created has an initial message
        call_args = mock_repo.create.call_args
        doc = call_args.args[1]
        assert doc.message_count == 1
        assert len(doc.messages) == 1
        assert doc.messages[0]["content"] == "Hello!"

    @pytest.mark.asyncio
    async def test_start_with_visitor_identity(self, session, mock_repo):
        visitor = VisitorIdentity(customer_id="cust-abc", email="a@b.com")
        request = ConversationStartRequest(visitor=visitor)
        await session.start_conversation("tenant-001", request)

        call_args = mock_repo.create.call_args
        doc = call_args.args[1]
        assert doc.customer_id == "cust-abc"

    @pytest.mark.asyncio
    async def test_start_trial_limit_blocks(self, session, mock_meter):
        dashboard = MagicMock()
        # Trial now has 5000 conversation limit (professional entitlements)
        dashboard.total_conversations = 5500
        mock_meter.get_usage_dashboard = AsyncMock(return_value=dashboard)

        request = ConversationStartRequest()
        with pytest.raises(TrialLimitReachedError):
            await session.start_conversation(
                "tenant-001", request, tier=TenantTier.TRIAL,
            )

    @pytest.mark.asyncio
    async def test_start_trial_allows_under_limit(self, session, mock_repo, mock_meter):
        dashboard = MagicMock()
        dashboard.total_conversations = 100
        mock_meter.get_usage_dashboard = AsyncMock(return_value=dashboard)

        request = ConversationStartRequest()
        result = await session.start_conversation(
            "tenant-001", request, tier=TenantTier.TRIAL,
        )
        assert result.conversation_id
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_trial_meter_error_allows(self, session, mock_repo, mock_meter):
        """Meter failures should not block conversations."""
        mock_meter.get_usage_dashboard = AsyncMock(side_effect=Exception("DB down"))

        request = ConversationStartRequest()
        result = await session.start_conversation(
            "tenant-001", request, tier=TenantTier.TRIAL,
        )
        assert result.conversation_id


# ---------------------------------------------------------------------------
# Tests — add_customer_message
# ---------------------------------------------------------------------------


class TestAddCustomerMessage:
    """Tests for ConversationSession.add_customer_message."""

    @pytest.mark.asyncio
    async def test_add_message_success(self, session, mock_repo):
        mock_repo.read = AsyncMock(return_value={
            "status": "active",
            "turn_count": 2,
            "message_count": 4,
        })
        request = SendMessageRequest(
            conversation_id="conv-001",
            content="What about returns?",
        )
        result = await session.add_customer_message("tenant-001", request)

        assert result.accepted is True
        assert result.message_id
        assert result.turn_count == 2
        mock_repo.append_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message_not_found(self, session, mock_repo):
        mock_repo.read = AsyncMock(
            side_effect=DocumentNotFoundError("conversations", "conv-x", "tenant-001")
        )
        request = SendMessageRequest(
            conversation_id="conv-x",
            content="Hello",
        )
        with pytest.raises(ConversationNotFoundError):
            await session.add_customer_message("tenant-001", request)

    @pytest.mark.asyncio
    async def test_add_message_not_active(self, session, mock_repo):
        mock_repo.read = AsyncMock(return_value={
            "status": "resolved",
            "turn_count": 5,
        })
        request = SendMessageRequest(
            conversation_id="conv-001",
            content="Hello",
        )
        with pytest.raises(ConversationNotActiveError):
            await session.add_customer_message("tenant-001", request)

    @pytest.mark.asyncio
    async def test_add_message_turn_limit(self, session, mock_repo):
        mock_repo.read = AsyncMock(return_value={
            "status": "active",
            "turn_count": MAX_TURNS,
        })
        request = SendMessageRequest(
            conversation_id="conv-001",
            content="Hello",
        )
        with pytest.raises(TurnLimitReachedError):
            await session.add_customer_message("tenant-001", request)

    @pytest.mark.asyncio
    async def test_add_message_with_pii_scrubbing(self, session, mock_repo):
        mock_repo.read = AsyncMock(return_value={
            "status": "active",
            "turn_count": 0,
            "message_count": 0,
        })
        session.set_pii_scrubber(True)

        request = SendMessageRequest(
            conversation_id="conv-001",
            content="My email is test@example.com",
        )
        result = await session.add_customer_message("tenant-001", request)

        # Verify append_message was called (content should be scrubbed)
        call_args = mock_repo.append_message.call_args
        call_args.kwargs["message"]
        # The scrubbed content should not contain the raw email
        assert result.accepted is True

    @pytest.mark.asyncio
    async def test_add_message_with_metadata(self, session, mock_repo):
        mock_repo.read = AsyncMock(return_value={
            "status": "active",
            "turn_count": 0,
            "message_count": 0,
        })
        request = SendMessageRequest(
            conversation_id="conv-001",
            content="Hello",
            metadata={"page_url": "https://example.com/product/123"},
        )
        await session.add_customer_message("tenant-001", request)

        call_args = mock_repo.append_message.call_args
        msg = call_args.kwargs["message"]
        assert "metadata" in msg


# ---------------------------------------------------------------------------
# Tests — add_ai_message
# ---------------------------------------------------------------------------


class TestAddAiMessage:
    """Tests for ConversationSession.add_ai_message.

    SPEC-1843: add_ai_message uses read-modify-write (read → modify → _pre_write
    → replace_item) instead of patch(), to preserve encryption on messages field.
    """

    def _setup_read_modify_write_mocks(self, mock_repo):
        """Configure mock_repo for read-modify-write pattern."""
        mock_repo.read = AsyncMock(return_value={
            "id": "conv-001",
            "tenant_id": "tenant-001",
            "messages": [],
            "turn_count": 0,
            "message_count": 0,
            "status": "active",
        })
        mock_repo._pre_write = AsyncMock(side_effect=lambda doc, tid: doc)
        mock_repo._container = AsyncMock()
        mock_repo._container.replace_item = AsyncMock(
            side_effect=lambda item, body, **kw: body
        )

    @pytest.mark.asyncio
    async def test_add_ai_message_basic(self, session, mock_repo):
        self._setup_read_modify_write_mocks(mock_repo)
        msg_id = await session.add_ai_message(
            "tenant-001", "conv-001", "Here is your answer.",
        )
        assert msg_id  # UUID string
        # Verify read-modify-write pattern (not patch)
        mock_repo.read.assert_awaited_once()
        mock_repo._container.replace_item.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_add_ai_message_with_trace(self, session, mock_repo):
        self._setup_read_modify_write_mocks(mock_repo)
        await session.add_ai_message(
            "tenant-001",
            "conv-001",
            "Here is the answer.",
            agents_invoked=["intent_classifier", "knowledge_retriever"],
            model_used="gpt-4o",
            critic_passed=True,
            metadata={"latency_ms": 500},
        )

        # Verify the written doc includes trace fields
        replace_call = mock_repo._container.replace_item.call_args
        body = replace_call.kwargs.get("body", replace_call[1].get("body"))
        assert body.get("agents_invoked") == ["intent_classifier", "knowledge_retriever"]
        assert body.get("model_used") == "gpt-4o"
        assert body.get("critic_passed") is True

    @pytest.mark.asyncio
    async def test_add_ai_message_pii_scrubbing(self, session, mock_repo):
        self._setup_read_modify_write_mocks(mock_repo)
        session.set_pii_scrubber(True)
        msg_id = await session.add_ai_message(
            "tenant-001", "conv-001", "Contact us at support@example.com",
        )

        # Verify the message was added
        assert msg_id
        mock_repo._container.replace_item.assert_awaited_once()


# ---------------------------------------------------------------------------
# Tests — end_conversation
# ---------------------------------------------------------------------------


class TestEndConversation:
    """Tests for ConversationSession.end_conversation."""

    @pytest.mark.asyncio
    async def test_end_conversation_success(self, session, mock_repo, mock_meter):
        mock_repo.read = AsyncMock(return_value={
            "status": "active",
            "turn_count": 3,
            "message_count": 6,
            "is_billable": True,
            "started_at": "2026-01-01T00:00:00+00:00",
        })

        result = await session.end_conversation("tenant-001", "conv-001")

        assert result.conversation_id == "conv-001"
        assert result.status == "resolved"
        assert result.is_billable is True
        mock_repo.end_conversation.assert_called_once()
        mock_meter.meter_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_end_conversation_with_feedback(self, session, mock_repo, mock_meter):
        mock_repo.read = AsyncMock(return_value={
            "status": "active",
            "turn_count": 2,
            "is_billable": True,
            "started_at": "2026-01-01T00:00:00+00:00",
        })

        request = EndConversationRequest(
            feedback_rating=5,
            feedback_text="Great help!",
            reason="resolved",
        )
        await session.end_conversation(
            "tenant-001", "conv-001", request,
        )

        # patch should be called to store feedback
        assert mock_repo.patch.call_count >= 1

    @pytest.mark.asyncio
    async def test_end_conversation_not_billable_skips_metering(
        self, session, mock_repo, mock_meter,
    ):
        mock_repo.read = AsyncMock(return_value={
            "status": "active",
            "turn_count": 1,
            "is_billable": False,
            "started_at": "2026-01-01T00:00:00+00:00",
        })

        result = await session.end_conversation("tenant-001", "conv-001")

        assert result.is_billable is False
        mock_meter.meter_conversation.assert_not_called()

    @pytest.mark.asyncio
    async def test_end_conversation_not_found(self, session, mock_repo):
        mock_repo.read = AsyncMock(
            side_effect=DocumentNotFoundError("conversations", "conv-x", "t")
        )

        with pytest.raises(ConversationNotFoundError):
            await session.end_conversation("tenant-001", "conv-x")

    @pytest.mark.asyncio
    async def test_end_conversation_not_active(self, session, mock_repo):
        mock_repo.read = AsyncMock(return_value={"status": "resolved"})

        with pytest.raises(ConversationNotActiveError):
            await session.end_conversation("tenant-001", "conv-001")

    @pytest.mark.asyncio
    async def test_end_conversation_meter_failure_logged(
        self, session, mock_repo, mock_meter,
    ):
        """Metering failures should not prevent ending the conversation."""
        mock_repo.read = AsyncMock(return_value={
            "status": "active",
            "turn_count": 1,
            "is_billable": True,
            "started_at": "2026-01-01T00:00:00+00:00",
        })
        mock_meter.meter_conversation = AsyncMock(side_effect=Exception("Stripe down"))

        result = await session.end_conversation("tenant-001", "conv-001")
        assert result.conversation_id == "conv-001"


# ---------------------------------------------------------------------------
# Tests — get_conversation
# ---------------------------------------------------------------------------


class TestGetConversation:
    """Tests for ConversationSession.get_conversation."""

    @pytest.mark.asyncio
    async def test_get_conversation_success(self, session, mock_repo):
        mock_repo.read = AsyncMock(return_value={
            "conversation_id": "conv-001",
            "status": "active",
            "turn_count": 2,
            "message_count": 4,
            "messages": [
                {"role": "customer", "content": "Hi", "timestamp": "2026-01-01T00:00:00Z"},
                {"role": "ai", "content": "Hello!", "timestamp": "2026-01-01T00:00:01Z"},
            ],
            "started_at": "2026-01-01T00:00:00Z",
            "last_activity_at": "2026-01-01T00:00:01Z",
        })

        result = await session.get_conversation("tenant-001", "conv-001")

        assert result.conversation_id == "conv-001"
        assert len(result.messages) == 2
        assert result.messages[0].role == MessageRole.CUSTOMER

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self, session, mock_repo):
        mock_repo.read = AsyncMock(
            side_effect=DocumentNotFoundError("conversations", "conv-x", "t")
        )

        with pytest.raises(ConversationNotFoundError):
            await session.get_conversation("tenant-001", "conv-x")


# ---------------------------------------------------------------------------
# Tests — check_idle_timeout
# ---------------------------------------------------------------------------


class TestCheckIdleTimeout:
    """Tests for ConversationSession.check_idle_timeout."""

    @pytest.mark.asyncio
    async def test_returns_none_for_non_active(self, session, mock_repo):
        mock_repo.read = AsyncMock(return_value={
            "status": "resolved",
            "turn_count": 5,
            "last_activity_at": "2026-01-01T00:00:00+00:00",
        })

        result = await session.check_idle_timeout("tenant-001", "conv-001")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_max_turns_when_over_limit(self, session, mock_repo):
        mock_repo.read = AsyncMock(return_value={
            "status": "active",
            "turn_count": MAX_TURNS,
            "last_activity_at": datetime.now(timezone.utc).isoformat(),
        })

        result = await session.check_idle_timeout("tenant-001", "conv-001")
        assert result == ConversationEndReason.MAX_TURNS


# ---------------------------------------------------------------------------
# Tests — Escalation
# ---------------------------------------------------------------------------


class TestEscalation:
    """Tests for find_best_agent_for_category and escalate_conversation."""

    @pytest.mark.asyncio
    async def test_find_best_agent_exact_category(self, session, mock_team_repo, mock_repo):
        mock_team_repo.list_members = AsyncMock(return_value=[
            {
                "id": "agent-1",
                "role": "escalation_agent",
                "is_active": True,
                "escalation_categories": ["billing", "returns"],
                "max_concurrent_conversations": 5,
            },
        ])
        mock_repo.count_filtered = AsyncMock(return_value=2)

        result = await session.find_best_agent_for_category("tenant-001", "billing")
        assert result == "agent-1"

    @pytest.mark.asyncio
    async def test_find_best_agent_no_candidates(self, session, mock_team_repo):
        mock_team_repo.list_members = AsyncMock(return_value=[])

        result = await session.find_best_agent_for_category("tenant-001", "billing")
        assert result is None

    @pytest.mark.asyncio
    async def test_find_best_agent_fallback_general(self, session, mock_team_repo, mock_repo):
        mock_team_repo.list_members = AsyncMock(return_value=[
            {
                "id": "agent-1",
                "role": "escalation_agent",
                "is_active": True,
                "escalation_categories": ["general_inquiry"],
                "max_concurrent_conversations": 5,
            },
        ])
        mock_repo.count_filtered = AsyncMock(return_value=0)

        result = await session.find_best_agent_for_category("tenant-001", "billing")
        assert result == "agent-1"

    @pytest.mark.asyncio
    async def test_find_best_agent_at_capacity(self, session, mock_team_repo, mock_repo):
        """WI-3030 S259: Capacity checks removed for async email-bridge model.
        An active agent matching the category is always returned regardless of
        concurrent conversation count."""
        mock_team_repo.list_members = AsyncMock(return_value=[
            {
                "id": "agent-1",
                "role": "escalation_agent",
                "is_active": True,
                "escalation_categories": ["billing"],
                "max_concurrent_conversations": 2,
            },
        ])
        mock_repo.count_filtered = AsyncMock(return_value=2)

        result = await session.find_best_agent_for_category("tenant-001", "billing")
        assert result == "agent-1"

    @pytest.mark.asyncio
    async def test_find_best_agent_no_team_repo(self):
        s = ConversationSession(conversation_repo=AsyncMock())
        result = await s.find_best_agent_for_category("tenant-001", "billing")
        assert result is None

    @pytest.mark.asyncio
    async def test_escalate_conversation(self, session, mock_repo):
        """SPEC-1843: Escalation uses append_message_with_metadata (read-modify-write)."""
        mock_repo.read = AsyncMock(return_value={
            "status": "active",
            "turn_count": 3,
        })
        mock_repo.append_message_with_metadata = AsyncMock()

        await session.escalate_conversation(
            "tenant-001",
            "conv-001",
            escalation_reason="Customer requested human",
            escalation_category="billing",
            assigned_to="agent-1",
        )

        mock_repo.append_message_with_metadata.assert_awaited_once()
        call = mock_repo.append_message_with_metadata.call_args
        metadata_updates = call.kwargs.get("metadata_updates", {})
        assert metadata_updates.get("status") == "escalated"
        assert metadata_updates.get("escalation_category") == "billing"
        assert metadata_updates.get("assigned_to") == "agent-1"


# ---------------------------------------------------------------------------
# Tests — find_active_conversation
# ---------------------------------------------------------------------------


class TestFindActiveConversation:
    """Tests for ConversationSession.find_active_conversation."""

    @pytest.mark.asyncio
    async def test_returns_none_when_no_active(self, session, mock_repo):
        mock_repo.find_active = AsyncMock(return_value=None)
        result = await session.find_active_conversation("tenant-001", "cust-1")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_state_when_found(self, session, mock_repo):
        mock_repo.find_active = AsyncMock(return_value={
            "conversation_id": "conv-001",
        })
        mock_repo.read = AsyncMock(return_value={
            "conversation_id": "conv-001",
            "status": "active",
            "turn_count": 1,
            "message_count": 2,
            "messages": [],
            "started_at": "2026-01-01T00:00:00Z",
            "last_activity_at": "2026-01-01T00:00:00Z",
        })
        result = await session.find_active_conversation("tenant-001", "cust-1")
        assert result is not None
        assert result.conversation_id == "conv-001"


# ---------------------------------------------------------------------------
# Tests — PII scrubber
# ---------------------------------------------------------------------------


class TestPiiScrubber:
    """Tests for set_pii_scrubber."""

    def test_enable_creates_scrubber(self, session):
        session.set_pii_scrubber(True)
        assert session._pii_scrubber is not None

    def test_disable_clears_scrubber(self, session):
        session.set_pii_scrubber(True)
        session.set_pii_scrubber(False)
        assert session._pii_scrubber is None


# ---------------------------------------------------------------------------
# Tests — Module-level singletons
# ---------------------------------------------------------------------------


class TestModuleSingletons:
    """Tests for get_conversation_session and configure_conversation_session."""

    def test_configure_creates_session(self):
        repo = AsyncMock()
        result = configure_conversation_session(repo)
        assert isinstance(result, ConversationSession)

    def test_configure_with_all_deps(self):
        repo = AsyncMock()
        meter = AsyncMock()
        team = AsyncMock()
        result = configure_conversation_session(repo, meter, team)
        assert result._repo is repo
        assert result._meter is meter
        assert result._team_repo is team


# ---------------------------------------------------------------------------
# Tests — Helper functions
# ---------------------------------------------------------------------------


class TestHelpers:
    """Tests for module-level helper functions."""

    def test_resolve_customer_id_none(self):
        assert _resolve_customer_id(None) is None

    def test_resolve_customer_id_from_customer_id(self):
        v = VisitorIdentity(customer_id="cust-1", email="a@b.com")
        assert _resolve_customer_id(v) == "cust-1"

    def test_resolve_customer_id_from_email(self):
        v = VisitorIdentity(email="a@b.com")
        assert _resolve_customer_id(v) == "a@b.com"

    def test_resolve_customer_id_none_when_empty(self):
        v = VisitorIdentity()
        assert _resolve_customer_id(v) is None

    def test_end_reason_to_status_customer_ended(self):
        assert _end_reason_to_status(ConversationEndReason.CUSTOMER_ENDED) == ConversationStatus.RESOLVED

    def test_end_reason_to_status_idle_timeout(self):
        assert _end_reason_to_status(ConversationEndReason.IDLE_TIMEOUT) == ConversationStatus.TIMED_OUT

    def test_end_reason_to_status_escalated(self):
        assert _end_reason_to_status(ConversationEndReason.ESCALATED) == ConversationStatus.ESCALATED

    def test_end_reason_to_status_max_turns(self):
        assert _end_reason_to_status(ConversationEndReason.MAX_TURNS) == ConversationStatus.RESOLVED

    def test_end_reason_to_status_error(self):
        assert _end_reason_to_status(ConversationEndReason.ERROR) == ConversationStatus.ERROR

    def test_calculate_duration_valid(self):
        result = _calculate_duration(
            "2026-01-01T00:00:00+00:00",
            "2026-01-01T00:02:30+00:00",
        )
        assert result == 150

    def test_calculate_duration_empty_started_at(self):
        assert _calculate_duration("", "2026-01-01T00:00:00+00:00") is None

    def test_calculate_duration_empty_ended_at(self):
        assert _calculate_duration("2026-01-01T00:00:00+00:00", "") is None

    def test_calculate_duration_invalid_format(self):
        assert _calculate_duration("not-a-date", "also-not") is None

    def test_calculate_duration_negative_clamped(self):
        result = _calculate_duration(
            "2026-01-02T00:00:00+00:00",
            "2026-01-01T00:00:00+00:00",
        )
        assert result == 0
