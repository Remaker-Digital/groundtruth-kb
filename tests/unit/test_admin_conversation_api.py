"""Tests for admin conversation inbox API — coverage expansion.

Covers: list, detail, messages, assign, escalate, resolve, archive,
unarchive, add_note, search, and the _extract_search_snippet helper.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_conversation_api import (
    _extract_search_snippet,
    _get_repo,
    _read_conversation,
    configure_admin_conversation_services,
    router,
)
from src.multi_tenant.cosmos_schema import ConversationStatus
from src.multi_tenant.repository import DocumentNotFoundError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_NOW = datetime.now(timezone.utc).isoformat()


def _make_conversation(
    conversation_id: str = "conv-001",
    status: str = "active",
    **overrides,
) -> dict:
    base = {
        "id": conversation_id,
        "conversation_id": conversation_id,
        "tenant_id": "tenant-001",
        "status": status,
        "customer_id": "cust-001",
        "customer_name": "John Doe",
        "is_billable": True,
        "message_count": 5,
        "turn_count": 3,
        "started_at": _NOW,
        "ended_at": None,
        "last_activity_at": _NOW,
        "assigned_to": None,
        "escalation_category": None,
        "agents_invoked": ["knowledge_retrieval"],
        "model_used": "gpt-4o-mini",
        "critic_passed": True,
        "archived_at": None,
        "messages": [
            {"role": "user", "content": "Hello, I need help", "timestamp": _NOW},
            {"role": "assistant", "content": "How can I assist you?", "timestamp": _NOW},
        ],
        "internal_notes": [],
    }
    base.update(overrides)
    return base


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "tenant-001"
    ctx.tier = "professional"
    ctx.user_id = "admin-user-001"
    ctx.auth_method = "api_key"
    return ctx


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.list_filtered = AsyncMock(return_value=[])
    repo.count_filtered = AsyncMock(return_value=0)
    repo.read = AsyncMock(return_value=_make_conversation())
    repo.query = AsyncMock(return_value=[])
    repo.assign_agent = AsyncMock()
    repo.add_internal_note = AsyncMock()
    repo.patch = AsyncMock()
    return repo


# ---------------------------------------------------------------------------
# Tests: _get_repo
# ---------------------------------------------------------------------------


class TestGetRepo:
    def test_raises_503_when_not_configured(self):
        import src.multi_tenant.admin_conversation_api as mod

        original = mod._conversation_repo
        mod._conversation_repo = None
        try:
            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc_info:
                _get_repo()
            assert exc_info.value.status_code == 503
        finally:
            mod._conversation_repo = original

    def test_returns_repo_when_configured(self, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        original = mod._conversation_repo
        mod._conversation_repo = mock_repo
        try:
            assert _get_repo() is mock_repo
        finally:
            mod._conversation_repo = original


# ---------------------------------------------------------------------------
# Tests: configure_admin_conversation_services
# ---------------------------------------------------------------------------


class TestConfigureServices:
    def test_sets_repos(self, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        team_repo = MagicMock()
        configure_admin_conversation_services(mock_repo, team_repo)
        assert mod._conversation_repo is mock_repo
        assert mod._team_repo is team_repo


# ---------------------------------------------------------------------------
# Tests: _read_conversation
# ---------------------------------------------------------------------------


class TestReadConversation:
    @pytest.mark.asyncio
    async def test_point_read_success(self, mock_repo):
        result = await _read_conversation(mock_repo, "tenant-001", "conv-001")
        assert result["conversation_id"] == "conv-001"
        mock_repo.read.assert_called_once_with("tenant-001", "conv-001")

    @pytest.mark.asyncio
    async def test_falls_back_to_query(self, mock_repo):
        mock_repo.read.side_effect = DocumentNotFoundError("conv", "conv-001", "tenant-001")
        mock_repo.query.return_value = [_make_conversation()]

        result = await _read_conversation(mock_repo, "tenant-001", "conv-001")
        assert result["conversation_id"] == "conv-001"
        mock_repo.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_404_when_both_fail(self, mock_repo):
        mock_repo.read.side_effect = DocumentNotFoundError("conv", "missing", "tenant-001")
        mock_repo.query.return_value = []

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await _read_conversation(mock_repo, "tenant-001", "missing")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_query_exception_still_raises_404(self, mock_repo):
        mock_repo.read.side_effect = DocumentNotFoundError("conv", "x", "tenant-001")
        mock_repo.query.side_effect = RuntimeError("cosmos error")

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await _read_conversation(mock_repo, "tenant-001", "x")
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Tests: _extract_search_snippet
# ---------------------------------------------------------------------------


class TestExtractSearchSnippet:
    def test_match_in_customer_name(self):
        doc = _make_conversation(customer_name="Jane Smith")
        snippet, matched_in = _extract_search_snippet(doc, "Jane")
        assert matched_in == "customer_name"
        assert "Jane" in snippet

    def test_match_in_messages(self):
        doc = _make_conversation(
            messages=[{"content": "I want to return my order #12345"}],
        )
        snippet, matched_in = _extract_search_snippet(doc, "return")
        assert matched_in == "messages"
        assert "return" in snippet.lower()

    def test_match_in_notes(self):
        doc = _make_conversation(
            messages=[{"content": "unrelated"}],
            internal_notes=[{"content": "Customer mentioned discount code SAVE20"}],
            customer_name="Anonymous",
        )
        snippet, matched_in = _extract_search_snippet(doc, "SAVE20")
        assert matched_in == "notes"

    def test_no_match_fallback(self):
        doc = _make_conversation(
            messages=[],
            internal_notes=[],
            customer_name="",
        )
        snippet, matched_in = _extract_search_snippet(doc, "nonexistent")
        assert snippet == ""
        assert matched_in == "messages"

    def test_snippet_with_ellipsis(self):
        long_content = "x" * 200 + "MATCH" + "y" * 200
        doc = {"customer_name": "", "messages": [{"content": long_content}], "internal_notes": []}
        snippet, matched_in = _extract_search_snippet(doc, "MATCH")
        assert matched_in == "messages"
        # Snippet is truncated and may have ellipsis
        assert len(snippet) <= 120

    def test_case_insensitive_matching(self):
        doc = _make_conversation(
            messages=[{"content": "Please help with My Order"}],
        )
        snippet, matched_in = _extract_search_snippet(doc, "my order")
        assert matched_in == "messages"


# ---------------------------------------------------------------------------
# Tests: list_conversations
# ---------------------------------------------------------------------------


class TestListConversations:
    @pytest.mark.asyncio
    async def test_list_basic(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.count_filtered.return_value = 1
        mock_repo.list_filtered.return_value = [_make_conversation()]

        from src.multi_tenant.admin_conversation_api import list_conversations

        result = await list_conversations(
            status=None, customer_id=None, since=None, until=None,
            assigned_to=None, archived=None, offset=0, limit=50, ctx=mock_ctx,
        )
        assert result.total_count == 1
        assert len(result.conversations) == 1

    @pytest.mark.asyncio
    async def test_list_with_status_filter(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo

        from src.multi_tenant.admin_conversation_api import list_conversations

        result = await list_conversations(
            status="escalated", customer_id=None, since=None, until=None,
            assigned_to=None, archived=None, offset=0, limit=50, ctx=mock_ctx,
        )
        call_kwargs = mock_repo.list_filtered.call_args.kwargs
        assert call_kwargs["status"] == ConversationStatus.ESCALATED

    @pytest.mark.asyncio
    async def test_list_invalid_status(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import list_conversations

        with pytest.raises(HTTPException) as exc_info:
            await list_conversations(
                status="bogus_status", customer_id=None, since=None, until=None,
                assigned_to=None, archived=None, offset=0, limit=50, ctx=mock_ctx,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_list_with_archived_filter(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo

        from src.multi_tenant.admin_conversation_api import list_conversations

        await list_conversations(
            status=None, customer_id=None, since=None, until=None,
            assigned_to=None, archived="only", offset=0, limit=50, ctx=mock_ctx,
        )
        call_kwargs = mock_repo.count_filtered.call_args.kwargs
        assert call_kwargs["archived_only"] is True

        await list_conversations(
            status=None, customer_id=None, since=None, until=None,
            assigned_to=None, archived="include", offset=0, limit=50, ctx=mock_ctx,
        )
        call_kwargs = mock_repo.count_filtered.call_args.kwargs
        assert call_kwargs["include_archived"] is True


# ---------------------------------------------------------------------------
# Tests: get_conversation_detail
# ---------------------------------------------------------------------------


class TestGetConversationDetail:
    @pytest.mark.asyncio
    async def test_detail_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo

        from src.multi_tenant.admin_conversation_api import get_conversation_detail

        result = await get_conversation_detail("conv-001", ctx=mock_ctx)
        assert result.conversation_id == "conv-001"
        assert result.tenant_id == "tenant-001"

    @pytest.mark.asyncio
    async def test_detail_not_found(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.side_effect = DocumentNotFoundError("conv", "missing", "tenant-001")
        mock_repo.query.return_value = []

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import get_conversation_detail

        with pytest.raises(HTTPException) as exc_info:
            await get_conversation_detail("missing", ctx=mock_ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Tests: get_conversation_messages
# ---------------------------------------------------------------------------


class TestGetConversationMessages:
    @pytest.mark.asyncio
    async def test_messages_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo

        from src.multi_tenant.admin_conversation_api import get_conversation_messages

        result = await get_conversation_messages("conv-001", ctx=mock_ctx)
        assert result.message_count == 2
        assert result.messages[0].role == "user"


# ---------------------------------------------------------------------------
# Tests: assign_agent
# ---------------------------------------------------------------------------


class TestAssignAgent:
    @pytest.mark.asyncio
    async def test_assign_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo

        from src.multi_tenant.admin_conversation_api import (
            AssignAgentRequest,
            assign_agent,
        )

        request = AssignAgentRequest(agent_id="agent-007")
        result = await assign_agent("conv-001", request=request, ctx=mock_ctx)
        assert result.assigned_to == "agent-007"
        assert result.conversation_id == "conv-001"

    @pytest.mark.asyncio
    async def test_assign_not_found(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.assign_agent.side_effect = DocumentNotFoundError("conv", "x", "tenant-001")

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import (
            AssignAgentRequest,
            assign_agent,
        )

        request = AssignAgentRequest(agent_id="agent-007")

        with pytest.raises(HTTPException) as exc_info:
            await assign_agent("x", request=request, ctx=mock_ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Tests: escalate_conversation
# ---------------------------------------------------------------------------


class TestEscalateConversation:
    @pytest.mark.asyncio
    async def test_escalate_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mod._team_repo = None

        from src.multi_tenant.admin_conversation_api import escalate_conversation

        with patch("src.multi_tenant.alert_delivery.send_escalation_alert", new_callable=AsyncMock):
            result = await escalate_conversation("conv-001", ctx=mock_ctx)

        assert result.status == "escalated"

    @pytest.mark.asyncio
    async def test_escalate_already_escalated(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation(status="escalated")

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import escalate_conversation

        with pytest.raises(HTTPException) as exc_info:
            await escalate_conversation("conv-001", ctx=mock_ctx)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_escalate_already_resolved(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation(status="resolved")

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import escalate_conversation

        with pytest.raises(HTTPException) as exc_info:
            await escalate_conversation("conv-001", ctx=mock_ctx)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_escalate_with_category(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mod._team_repo = None

        from src.multi_tenant.admin_conversation_api import (
            EscalateConversationRequest,
            escalate_conversation,
        )

        request = EscalateConversationRequest(category="billing", agent_id="agent-X")

        with patch("src.multi_tenant.alert_delivery.send_escalation_alert", new_callable=AsyncMock):
            result = await escalate_conversation("conv-001", request=request, ctx=mock_ctx)

        assert result.escalation_category == "billing"
        assert result.assigned_to == "agent-X"

    @pytest.mark.asyncio
    async def test_escalate_email_failure_non_blocking(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mod._team_repo = None

        from src.multi_tenant.admin_conversation_api import escalate_conversation

        with patch(
            "src.multi_tenant.alert_delivery.send_escalation_alert",
            new_callable=AsyncMock,
            side_effect=RuntimeError("email failed"),
        ):
            # Should not raise
            result = await escalate_conversation("conv-001", ctx=mock_ctx)
        assert result.status == "escalated"


# ---------------------------------------------------------------------------
# Tests: resolve_conversation
# ---------------------------------------------------------------------------


class TestResolveConversation:
    @pytest.mark.asyncio
    async def test_resolve_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo

        from src.multi_tenant.admin_conversation_api import resolve_conversation

        result = await resolve_conversation("conv-001", ctx=mock_ctx)
        assert result.status == "resolved"

    @pytest.mark.asyncio
    async def test_resolve_already_resolved(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation(status="resolved")

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import resolve_conversation

        with pytest.raises(HTTPException) as exc_info:
            await resolve_conversation("conv-001", ctx=mock_ctx)
        assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# Tests: add_note
# ---------------------------------------------------------------------------


class TestAddNote:
    @pytest.mark.asyncio
    async def test_add_note_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo

        from src.multi_tenant.admin_conversation_api import AddNoteRequest, add_note

        request = AddNoteRequest(content="Customer mentioned loyalty discount")
        result = await add_note("conv-001", request=request, ctx=mock_ctx)
        assert result.conversation_id == "conv-001"
        assert result.note_id is not None
        mock_repo.add_internal_note.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_note_not_found(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.add_internal_note.side_effect = DocumentNotFoundError("conv", "x", "tenant-001")

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import AddNoteRequest, add_note

        request = AddNoteRequest(content="Test note")

        with pytest.raises(HTTPException) as exc_info:
            await add_note("x", request=request, ctx=mock_ctx)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_add_note_with_explicit_author(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo

        from src.multi_tenant.admin_conversation_api import AddNoteRequest, add_note

        request = AddNoteRequest(content="Note", author="manager@store.com")
        await add_note("conv-001", request=request, ctx=mock_ctx)

        note_arg = mock_repo.add_internal_note.call_args.kwargs["note"]
        assert note_arg["author"] == "manager@store.com"


# ---------------------------------------------------------------------------
# Tests: archive_conversation
# ---------------------------------------------------------------------------


class TestArchiveConversation:
    @pytest.mark.asyncio
    async def test_archive_resolved(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation(status="resolved")

        from src.multi_tenant.admin_conversation_api import archive_conversation

        result = await archive_conversation("conv-001", ctx=mock_ctx)
        assert result.archived_at is not None

    @pytest.mark.asyncio
    async def test_archive_timed_out(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation(status="timed_out")

        from src.multi_tenant.admin_conversation_api import archive_conversation

        result = await archive_conversation("conv-001", ctx=mock_ctx)
        assert result.archived_at is not None

    @pytest.mark.asyncio
    async def test_archive_active_rejected(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation(status="active")

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import archive_conversation

        with pytest.raises(HTTPException) as exc_info:
            await archive_conversation("conv-001", ctx=mock_ctx)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_archive_already_archived(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation(
            status="resolved", archived_at=_NOW,
        )

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import archive_conversation

        with pytest.raises(HTTPException) as exc_info:
            await archive_conversation("conv-001", ctx=mock_ctx)
        assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# Tests: unarchive_conversation
# ---------------------------------------------------------------------------


class TestUnarchiveConversation:
    @pytest.mark.asyncio
    async def test_unarchive_success(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation(
            status="resolved", archived_at=_NOW,
        )

        from src.multi_tenant.admin_conversation_api import unarchive_conversation

        result = await unarchive_conversation("conv-001", ctx=mock_ctx)
        assert result.archived_at is None

    @pytest.mark.asyncio
    async def test_unarchive_not_archived(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation(archived_at=None)

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import unarchive_conversation

        with pytest.raises(HTTPException) as exc_info:
            await unarchive_conversation("conv-001", ctx=mock_ctx)
        assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# Tests: search_conversations
# ---------------------------------------------------------------------------


class TestSearchConversations:
    @pytest.mark.asyncio
    async def test_search_basic(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.query.return_value = [
            _make_conversation(customer_name="Jane Smith"),
        ]

        from src.multi_tenant.admin_conversation_api import (
            SearchConversationsRequest,
            search_conversations,
        )

        request = SearchConversationsRequest(query="Jane")
        result = await search_conversations(request=request, ctx=mock_ctx)
        assert result.total_results == 1
        assert result.query == "Jane"

    @pytest.mark.asyncio
    async def test_search_invalid_status(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo

        from fastapi import HTTPException

        from src.multi_tenant.admin_conversation_api import (
            SearchConversationsRequest,
            search_conversations,
        )

        request = SearchConversationsRequest(query="test", status="bogus")

        with pytest.raises(HTTPException) as exc_info:
            await search_conversations(request=request, ctx=mock_ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_search_query_failure_returns_empty(self, mock_ctx, mock_repo):
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.query.side_effect = RuntimeError("cosmos down")

        from src.multi_tenant.admin_conversation_api import (
            SearchConversationsRequest,
            search_conversations,
        )

        request = SearchConversationsRequest(query="test")
        result = await search_conversations(request=request, ctx=mock_ctx)
        assert result.total_results == 0


# ---------------------------------------------------------------------------
# Tests: set_agent_override (SPEC-1866)
# ---------------------------------------------------------------------------


class TestSetAgentOverride:
    @pytest.mark.asyncio
    async def test_set_override_success(self, mock_ctx, mock_repo):
        """PUT agent-override sets fields when agent passes validation."""
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation()
        mock_ctx.team_member_id = "tm-001"

        mock_defn = MagicMock()
        mock_defn.tier_gate = "free"

        mock_config = MagicMock()
        mock_config.enabled = True

        with (
            patch(
                "src.agents.plugins.registry.PluginAgentRegistry"
            ) as MockReg,
            patch(
                "src.agents.plugins.bindings.SkillBindingService"
            ) as MockSvc,
            patch(
                "src.agents.plugins.events.emit_invocation"
            ),
            patch(
                "src.agents.plugins.overlay.resolve_effective_config",
                return_value=mock_config,
            ),
            patch(
                "src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository"
            ) as MockOverlayRepo,
        ):
            MockReg.get_instance.return_value.get.return_value = mock_defn
            mock_svc = MockSvc.get_instance.return_value
            mock_svc.list_bindings.return_value = [{"skill_id": "s1"}]
            mock_svc._loaded_tenants = {"tenant-001"}
            MockOverlayRepo.return_value.get_overlay = AsyncMock(
                return_value={"enabled": True, "visibility_scope": "public"},
            )

            from src.multi_tenant.admin_conversation_api import (
                AgentOverrideRequest,
                set_agent_override,
            )

            request = AgentOverrideRequest(agent_id="sales_agent")
            result = await set_agent_override(
                "conv-001", request=request, ctx=mock_ctx,
            )

            assert result.conversation_id == "conv-001"
            assert result.agent_id == "sales_agent"
            assert result.set_at is not None
            assert result.set_by == "tm-001"
            mock_repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_override(self, mock_ctx, mock_repo):
        """PUT agent-override with null agent_id clears the override."""
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation(
            conversation_agent_override="sales_agent",
        )

        with patch(
            "src.agents.plugins.events.emit_invocation"
        ):
            from src.multi_tenant.admin_conversation_api import (
                AgentOverrideRequest,
                set_agent_override,
            )

            request = AgentOverrideRequest(agent_id=None)
            result = await set_agent_override(
                "conv-001", request=request, ctx=mock_ctx,
            )

            assert result.agent_id is None
            assert result.set_at is None
            assert result.set_by is None
            mock_repo.patch.assert_called_once()
            ops = mock_repo.patch.call_args.kwargs["operations"]
            assert any(
                op["path"] == "/conversation_agent_override" and op["value"] is None
                for op in ops
            )

    @pytest.mark.asyncio
    async def test_agent_not_in_registry(self, mock_ctx, mock_repo):
        """PUT agent-override returns 422 when agent doesn't exist."""
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation()

        with patch(
            "src.agents.plugins.registry.PluginAgentRegistry"
        ) as MockReg:
            MockReg.get_instance.return_value.get.return_value = None

            from fastapi import HTTPException

            from src.multi_tenant.admin_conversation_api import (
                AgentOverrideRequest,
                set_agent_override,
            )

            request = AgentOverrideRequest(agent_id="nonexistent_agent")
            with pytest.raises(HTTPException) as exc_info:
                await set_agent_override(
                    "conv-001", request=request, ctx=mock_ctx,
                )
            assert exc_info.value.status_code == 422
            assert "not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_no_bindings_returns_422(self, mock_ctx, mock_repo):
        """PUT agent-override returns 422 when no skill bindings exist."""
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation()

        mock_defn = MagicMock()
        mock_defn.tier_gate = "free"

        mock_config = MagicMock()
        mock_config.enabled = True

        with (
            patch(
                "src.agents.plugins.registry.PluginAgentRegistry"
            ) as MockReg,
            patch(
                "src.agents.plugins.bindings.SkillBindingService"
            ) as MockSvc,
            patch(
                "src.agents.plugins.overlay.resolve_effective_config",
                return_value=mock_config,
            ),
            patch(
                "src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository"
            ) as MockOverlayRepo,
        ):
            MockReg.get_instance.return_value.get.return_value = mock_defn
            mock_svc = MockSvc.get_instance.return_value
            mock_svc.list_bindings.return_value = []
            mock_svc._loaded_tenants = {"tenant-001"}
            MockOverlayRepo.return_value.get_overlay = AsyncMock(
                return_value={"enabled": True, "visibility_scope": "public"},
            )

            from fastapi import HTTPException

            from src.multi_tenant.admin_conversation_api import (
                AgentOverrideRequest,
                set_agent_override,
            )

            request = AgentOverrideRequest(agent_id="sales_agent")
            with pytest.raises(HTTPException) as exc_info:
                await set_agent_override(
                    "conv-001", request=request, ctx=mock_ctx,
                )
            assert exc_info.value.status_code == 422
            assert "No skill bindings" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_disabled_agent_returns_422(self, mock_ctx, mock_repo):
        """PUT agent-override returns 422 when agent is disabled via overlay."""
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation()

        mock_defn = MagicMock()
        mock_defn.tier_gate = "free"
        mock_config = MagicMock()
        mock_config.enabled = False

        with (
            patch(
                "src.agents.plugins.registry.PluginAgentRegistry"
            ) as MockReg,
            patch(
                "src.agents.plugins.overlay.resolve_effective_config",
                return_value=mock_config,
            ),
            patch(
                "src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository"
            ) as MockOverlayRepo,
        ):
            MockReg.get_instance.return_value.get.return_value = mock_defn
            MockOverlayRepo.return_value.get_overlay = AsyncMock(
                return_value={"enabled": False},
            )

            from fastapi import HTTPException

            from src.multi_tenant.admin_conversation_api import (
                AgentOverrideRequest,
                set_agent_override,
            )

            request = AgentOverrideRequest(agent_id="sales_agent")
            with pytest.raises(HTTPException) as exc_info:
                await set_agent_override(
                    "conv-001", request=request, ctx=mock_ctx,
                )
            assert exc_info.value.status_code == 422
            assert "disabled" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_private_scope_agent_returns_422(self, mock_ctx, mock_repo):
        """PUT agent-override returns 422 for private-scope agent."""
        import src.multi_tenant.admin_conversation_api as mod

        mod._conversation_repo = mock_repo
        mock_repo.read.return_value = _make_conversation()

        mock_defn = MagicMock()
        mock_defn.tier_gate = "free"
        mock_config = MagicMock()
        mock_config.enabled = True

        with (
            patch(
                "src.agents.plugins.registry.PluginAgentRegistry"
            ) as MockReg,
            patch(
                "src.agents.plugins.overlay.resolve_effective_config",
                return_value=mock_config,
            ),
            patch(
                "src.multi_tenant.repositories.agent_overlays.TenantAgentOverlayRepository"
            ) as MockOverlayRepo,
        ):
            MockReg.get_instance.return_value.get.return_value = mock_defn
            MockOverlayRepo.return_value.get_overlay = AsyncMock(
                return_value={"enabled": True, "visibility_scope": "private"},
            )

            from fastapi import HTTPException

            from src.multi_tenant.admin_conversation_api import (
                AgentOverrideRequest,
                set_agent_override,
            )

            request = AgentOverrideRequest(agent_id="sales_agent")
            with pytest.raises(HTTPException) as exc_info:
                await set_agent_override(
                    "conv-001", request=request, ctx=mock_ctx,
                )
            assert exc_info.value.status_code == 422
            assert "private-scoped" in exc_info.value.detail
