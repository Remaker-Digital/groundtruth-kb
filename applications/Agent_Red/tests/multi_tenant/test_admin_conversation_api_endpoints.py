"""Endpoint-level tests for Admin Conversation Inbox API.

Covers 7 specs:
    1. Router prefix /api/admin/conversations
    2. list_conversations — mock repo.count_filtered(0) and repo.list_filtered([])
    3. get_conversation_detail — mock repo.read returning conversation dict
    4. get_conversation_messages — mock repo.read returning dict with messages
    5. assign_agent — mock repo.assign_agent
    6. resolve_conversation — mock repo.read and repo.patch
    7. add_note — mock repo.add_internal_note

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.admin_conversation_api import (
    configure_admin_conversation_services,
    router,
)
from src.multi_tenant.repository import DocumentNotFoundError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TENANT_ID = "test-tenant-001"
NOW_ISO = "2026-02-27T12:00:00+00:00"


def _ctx(**overrides):
    ctx = MagicMock()
    ctx.tenant_id = overrides.get("tenant_id", TENANT_ID)
    ctx.tier = overrides.get("tier", "professional")
    ctx.user_id = overrides.get("user_id", "user-001")
    ctx.team_member_email = overrides.get("team_member_email", "admin@test.com")
    ctx.team_member_role = overrides.get("team_member_role", None)
    ctx.team_member_id = overrides.get("team_member_id", "member-001")
    ctx.auth_method = overrides.get("auth_method", "tenant_api_key")
    return ctx


def _conv_doc(
    conversation_id: str = "conv-001",
    status: str = "active",
    **extra,
) -> dict:
    doc = {
        "id": conversation_id,
        "conversation_id": conversation_id,
        "tenant_id": TENANT_ID,
        "customer_id": "cust-abc",
        "customer_name": "Alice Smith",
        "status": status,
        "is_billable": True,
        "message_count": 2,
        "turn_count": 1,
        "started_at": NOW_ISO,
        "ended_at": None,
        "last_activity_at": NOW_ISO,
        "assigned_to": None,
        "escalation_category": None,
        "agents_invoked": ["IC", "KR"],
        "model_used": "gpt-4o",
        "critic_passed": True,
        "archived_at": None,
        "internal_notes": [],
        "messages": [
            {"role": "customer", "content": "Hello", "timestamp": NOW_ISO},
            {"role": "ai", "content": "Hi there!", "timestamp": NOW_ISO},
        ],
        "customer_verified": False,
        "identity_email": None,
    }
    doc.update(extra)
    return doc


# ---------------------------------------------------------------------------
# 1. Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """Spec: Router has prefix /api/admin/conversations."""

    def test_router_prefix_is_correct(self):
        assert router.prefix == "/api/admin/conversations"

    def test_router_tags(self):
        assert "admin-inbox" in router.tags


# ---------------------------------------------------------------------------
# 2. list_conversations — empty list
# ---------------------------------------------------------------------------


class TestListConversationsEndpoint:
    """Spec: GET /api/admin/conversations returns paginated list."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_conversation_services(self.repo)
        yield
        configure_admin_conversation_services(None)

    @pytest.mark.asyncio
    async def test_returns_empty_list(self):
        from src.multi_tenant.admin_conversation_api import list_conversations

        self.repo.count_filtered.return_value = 0
        self.repo.list_filtered.return_value = []

        ctx = _ctx()
        result = await list_conversations(
            status=None, customer_id=None, since=None, until=None,
            assigned_to=None, archived=None, offset=0, limit=50, ctx=ctx,
        )

        assert result.total_count == 0
        assert result.conversations == []
        assert result.tenant_id == TENANT_ID
        assert result.offset == 0
        assert result.limit == 50

    @pytest.mark.asyncio
    async def test_repo_count_and_list_called(self):
        from src.multi_tenant.admin_conversation_api import list_conversations

        self.repo.count_filtered.return_value = 0
        self.repo.list_filtered.return_value = []

        ctx = _ctx()
        await list_conversations(
            status=None, customer_id=None, since=None, until=None,
            assigned_to=None, archived=None, offset=0, limit=50, ctx=ctx,
        )

        self.repo.count_filtered.assert_called_once()
        self.repo.list_filtered.assert_called_once()


# ---------------------------------------------------------------------------
# 3. get_conversation_detail — repo.read returning a dict
# ---------------------------------------------------------------------------


class TestGetConversationDetailEndpoint:
    """Spec: GET /api/admin/conversations/{id} returns full detail."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_conversation_services(self.repo)
        yield
        configure_admin_conversation_services(None)

    @pytest.mark.asyncio
    async def test_returns_detail_from_doc(self):
        from src.multi_tenant.admin_conversation_api import get_conversation_detail

        doc = _conv_doc("conv-42", status="active")
        self.repo.read.return_value = doc

        ctx = _ctx()
        result = await get_conversation_detail("conv-42", ctx=ctx)

        assert result.conversation_id == "conv-42"
        assert result.tenant_id == TENANT_ID
        assert result.status == "active"
        assert result.customer_name == "Alice Smith"
        assert result.message_count == 2

    @pytest.mark.asyncio
    async def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_conversation_api import get_conversation_detail

        self.repo.read.side_effect = DocumentNotFoundError(
            "conversations", "gone", TENANT_ID,
        )
        # Fallback query also fails
        self.repo.query.side_effect = Exception("not found")

        ctx = _ctx()
        with pytest.raises(HTTPException) as exc_info:
            await get_conversation_detail("gone", ctx=ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# 4. get_conversation_messages — repo.read returning dict with messages
# ---------------------------------------------------------------------------


class TestGetConversationMessagesEndpoint:
    """Spec: GET /api/admin/conversations/{id}/messages returns transcript."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_conversation_services(self.repo)
        yield
        configure_admin_conversation_services(None)

    @pytest.mark.asyncio
    async def test_returns_messages_list(self):
        from src.multi_tenant.admin_conversation_api import get_conversation_messages

        doc = _conv_doc("conv-42", messages=[
            {"role": "customer", "content": "Hello", "timestamp": NOW_ISO},
            {"role": "ai", "content": "Hi there!", "timestamp": NOW_ISO},
            {"role": "customer", "content": "Thanks", "timestamp": NOW_ISO},
        ])
        doc["message_count"] = 3
        self.repo.read.return_value = doc

        ctx = _ctx()
        result = await get_conversation_messages("conv-42", ctx=ctx)

        assert result.conversation_id == "conv-42"
        assert result.tenant_id == TENANT_ID
        assert result.message_count == 3
        assert len(result.messages) == 3
        assert result.messages[0].role == "customer"
        assert result.messages[0].content == "Hello"
        assert result.messages[1].role == "ai"

    @pytest.mark.asyncio
    async def test_empty_messages(self):
        from src.multi_tenant.admin_conversation_api import get_conversation_messages

        doc = _conv_doc("conv-empty", messages=[])
        self.repo.read.return_value = doc

        ctx = _ctx()
        result = await get_conversation_messages("conv-empty", ctx=ctx)

        assert result.message_count == 0
        assert result.messages == []


# ---------------------------------------------------------------------------
# 5. assign_agent — repo.assign_agent
# ---------------------------------------------------------------------------


class TestAssignAgentEndpoint:
    """Spec: POST /api/admin/conversations/{id}/assign assigns human agent."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_conversation_services(self.repo)
        yield
        configure_admin_conversation_services(None)

    @pytest.mark.asyncio
    async def test_assigns_agent_successfully(self):
        from src.multi_tenant.admin_conversation_api import (
            AssignAgentRequest,
            assign_agent,
        )

        self.repo.assign_agent.return_value = None

        req = AssignAgentRequest(agent_id="agent-42")
        ctx = _ctx()
        result = await assign_agent("conv-001", req, ctx=ctx)

        assert result.conversation_id == "conv-001"
        assert result.assigned_to == "agent-42"
        assert result.assigned_at is not None
        self.repo.assign_agent.assert_called_once_with(
            tenant_id=TENANT_ID,
            conversation_id="conv-001",
            agent_id="agent-42",
        )

    @pytest.mark.asyncio
    async def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_conversation_api import (
            AssignAgentRequest,
            assign_agent,
        )

        self.repo.assign_agent.side_effect = DocumentNotFoundError(
            "conversations", "gone", TENANT_ID,
        )

        req = AssignAgentRequest(agent_id="agent-42")
        ctx = _ctx()
        with pytest.raises(HTTPException) as exc_info:
            await assign_agent("gone", req, ctx=ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# 6. resolve_conversation — repo.read and repo.patch
# ---------------------------------------------------------------------------


class TestResolveConversationEndpoint:
    """Spec: POST /api/admin/conversations/{id}/resolve marks resolved."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_conversation_services(self.repo)
        yield
        configure_admin_conversation_services(None)

    @pytest.mark.asyncio
    async def test_resolves_active_conversation(self):
        from src.multi_tenant.admin_conversation_api import resolve_conversation

        doc = _conv_doc("conv-001", status="active")
        self.repo.read.return_value = doc

        ctx = _ctx()
        result = await resolve_conversation("conv-001", ctx=ctx)

        assert result.conversation_id == "conv-001"
        assert result.status == "resolved"
        assert result.resolved_at is not None
        self.repo.patch.assert_called_once()

        # Verify patch sets status to resolved
        patch_call = self.repo.patch.call_args
        operations = patch_call.kwargs.get(
            "operations", patch_call[1].get("operations", []),
        )
        paths = [op["path"] for op in operations]
        assert "/status" in paths
        assert "/resolved_at" in paths

    @pytest.mark.asyncio
    async def test_rejects_already_resolved(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_conversation_api import resolve_conversation

        doc = _conv_doc("conv-001", status="resolved")
        self.repo.read.return_value = doc

        ctx = _ctx()
        with pytest.raises(HTTPException) as exc_info:
            await resolve_conversation("conv-001", ctx=ctx)
        assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# 7. add_note — repo.add_internal_note
# ---------------------------------------------------------------------------


class TestAddNoteEndpoint:
    """Spec: POST /api/admin/conversations/{id}/notes adds internal note."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_conversation_services(self.repo)
        yield
        configure_admin_conversation_services(None)

    @pytest.mark.asyncio
    async def test_adds_note_successfully(self):
        from src.multi_tenant.admin_conversation_api import (
            AddNoteRequest,
            add_note,
        )

        self.repo.add_internal_note.return_value = None

        req = AddNoteRequest(content="Customer needs follow-up", author="Admin")
        ctx = _ctx()
        result = await add_note("conv-001", req, ctx=ctx)

        assert result.conversation_id == "conv-001"
        assert result.note_id is not None
        assert len(result.note_id) > 0
        assert result.created_at is not None
        self.repo.add_internal_note.assert_called_once()

        # Verify the note dict passed to repo
        call_kwargs = self.repo.add_internal_note.call_args.kwargs
        assert call_kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs["conversation_id"] == "conv-001"
        note = call_kwargs["note"]
        assert note["content"] == "Customer needs follow-up"
        assert note["author"] == "Admin"

    @pytest.mark.asyncio
    async def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_conversation_api import (
            AddNoteRequest,
            add_note,
        )

        self.repo.add_internal_note.side_effect = DocumentNotFoundError(
            "conversations", "gone", TENANT_ID,
        )

        req = AddNoteRequest(content="Test note")
        ctx = _ctx()
        with pytest.raises(HTTPException) as exc_info:
            await add_note("gone", req, ctx=ctx)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_default_author_uses_auth_method(self):
        from src.multi_tenant.admin_conversation_api import (
            AddNoteRequest,
            add_note,
        )

        self.repo.add_internal_note.return_value = None

        req = AddNoteRequest(content="Note without author")
        ctx = _ctx(auth_method="tenant_api_key")
        await add_note("conv-001", req, ctx=ctx)

        call_kwargs = self.repo.add_internal_note.call_args.kwargs
        note = call_kwargs["note"]
        assert note["author"] == "tenant_api_key"
