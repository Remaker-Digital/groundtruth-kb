"""Tests for Admin Team Management API — per-user API keys, role model, escalation.

Covers:
    - Team member CRUD with per-user API key generation
    - Role validation (superadmin protection, escalation_agent categories)
    - Superadmin visibility filtering
    - API key rotation
    - Escalation category validation
    - Response model fields

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.admin_team_api import (
    ESCALATION_CATEGORIES,
    PROTECTED_ROLES,
    VALID_ROLES,
    CreateTeamMemberRequest,
    UpdateTeamMemberRequest,
    WhoamiResponse,
    _build_member_response,
    configure_admin_team_services,
    whoami,
)
from src.multi_tenant.auth import generate_user_api_key, hash_api_key
from src.multi_tenant.cosmos_schema import ESCALATION_CATEGORIES as SCHEMA_CATEGORIES
from src.multi_tenant.cosmos_schema import TeamMemberRole
from src.multi_tenant.repository import DocumentNotFoundError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TENANT_ID = "remaker-digital-001"
NOW_ISO = "2026-02-12T12:00:00+00:00"


def _make_member_doc(
    email: str = "alice@example.com",
    role: str = "admin",
    is_active: bool = True,
    escalation_categories: list[str] | None = None,
    user_api_key_hash: str | None = "fakehash123",
    user_api_key_prefix: str | None = "ar_user_rema...",
) -> dict:
    member_id = f"{TENANT_ID}:{email}"
    return {
        "id": member_id,
        "tenant_id": TENANT_ID,
        "email": email,
        "display_name": email.split("@")[0].title(),
        "role": role,
        "is_active": is_active,
        "escalation_categories": escalation_categories or [],
        "max_concurrent_conversations": 5,
        "user_api_key_hash": user_api_key_hash,
        "user_api_key_prefix": user_api_key_prefix,
        "created_at": NOW_ISO,
        "updated_at": NOW_ISO,
        "last_login_at": None,
        "invited_by": "system",
    }


def _ctx(
    role: TeamMemberRole | None = None,
    member_id: str | None = None,
    email: str | None = None,
):
    """Build a mock TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = TENANT_ID
    ctx.user_id = "test-admin"
    ctx.team_member_role = role
    ctx.team_member_id = member_id
    ctx.team_member_email = email
    return ctx


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    """Verify role and category constants are correct."""

    def test_valid_roles_includes_all_enum_values(self):
        assert VALID_ROLES == {"superadmin", "admin", "escalation_agent", "viewer"}

    def test_protected_roles(self):
        assert PROTECTED_ROLES == {"superadmin"}

    def test_escalation_categories_match_schema(self):
        assert ESCALATION_CATEGORIES == SCHEMA_CATEGORIES

    def test_escalation_categories_values(self):
        expected = ["service", "support", "sales", "account", "technical_assistance", "general_inquiry"]
        assert ESCALATION_CATEGORIES == expected


# ---------------------------------------------------------------------------
# User API key generation
# ---------------------------------------------------------------------------


class TestUserApiKeyGeneration:
    """Test per-user API key generation and hashing."""

    def test_key_starts_with_user_prefix(self):
        key = generate_user_api_key(TENANT_ID)
        assert key.startswith("ar_user_")

    def test_key_includes_tenant_prefix(self):
        key = generate_user_api_key(TENANT_ID)
        assert key.startswith("ar_user_rema")

    def test_keys_are_unique(self):
        keys = {generate_user_api_key(TENANT_ID) for _ in range(50)}
        assert len(keys) == 50

    def test_hash_is_deterministic(self):
        key = "ar_user_rema_test123"
        assert hash_api_key(key) == hash_api_key(key)

    def test_different_keys_different_hashes(self):
        k1 = generate_user_api_key(TENANT_ID)
        k2 = generate_user_api_key(TENANT_ID)
        assert hash_api_key(k1) != hash_api_key(k2)


# ---------------------------------------------------------------------------
# Response helper
# ---------------------------------------------------------------------------


class TestBuildMemberResponse:
    """Test _build_member_response helper."""

    def test_basic_fields(self):
        doc = _make_member_doc()
        resp = _build_member_response(doc, TENANT_ID)
        assert resp.email == "alice@example.com"
        assert resp.role == "admin"
        assert resp.is_active is True
        assert resp.tenant_id == TENANT_ID

    def test_escalation_categories_included(self):
        doc = _make_member_doc(role="escalation_agent", escalation_categories=["sales", "support"])
        resp = _build_member_response(doc, TENANT_ID)
        assert resp.escalation_categories == ["sales", "support"]

    def test_user_api_key_prefix_included(self):
        doc = _make_member_doc(user_api_key_prefix="ar_user_rema...")
        resp = _build_member_response(doc, TENANT_ID)
        assert resp.user_api_key_prefix == "ar_user_rema..."

    def test_user_api_key_not_in_response(self):
        doc = _make_member_doc()
        resp = _build_member_response(doc, TENANT_ID)
        assert resp.user_api_key is None

    def test_missing_fields_have_defaults(self):
        doc = {"id": "x", "tenant_id": TENANT_ID}
        resp = _build_member_response(doc, TENANT_ID)
        assert resp.email == ""
        assert resp.role == "viewer"
        assert resp.escalation_categories == []
        assert resp.max_concurrent_conversations == 5

    def test_camel_case_serialization(self):
        doc = _make_member_doc(escalation_categories=["sales"])
        resp = _build_member_response(doc, TENANT_ID)
        data = resp.model_dump(by_alias=True)
        assert "escalationCategories" in data
        assert "userApiKeyPrefix" in data
        assert "maxConcurrentConversations" in data
        assert "displayName" in data


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class TestRequestModels:
    """Test Pydantic request model validation."""

    def test_create_request_defaults(self):
        req = CreateTeamMemberRequest(email="a@b.com", display_name="A", role="admin")
        assert req.escalation_categories == []
        assert req.max_concurrent_conversations == 5

    def test_create_request_with_categories(self):
        req = CreateTeamMemberRequest(
            email="a@b.com",
            display_name="A",
            role="escalation_agent",
            escalation_categories=["sales", "support"],
        )
        assert req.escalation_categories == ["sales", "support"]

    def test_update_request_all_none(self):
        req = UpdateTeamMemberRequest()
        assert req.display_name is None
        assert req.role is None
        assert req.escalation_categories is None
        assert req.is_active is None


# ---------------------------------------------------------------------------
# List team members
# ---------------------------------------------------------------------------


class TestListTeamMembers:
    """Test GET /api/admin/team."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.repo = AsyncMock()
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_basic_list(self):
        from src.multi_tenant.admin_team_api import list_team_members

        self.repo.count_members.return_value = 2
        self.repo.list_members.return_value = [
            _make_member_doc("alice@test.com", "admin"),
            _make_member_doc("bob@test.com", "viewer"),
        ]
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await list_team_members(role=None, is_active=None, offset=0, limit=50, ctx=ctx)
        assert len(result.members) == 2
        assert result.total_count == 2

    @pytest.mark.asyncio
    async def test_superadmin_hidden_from_admin(self):
        from src.multi_tenant.admin_team_api import list_team_members

        self.repo.count_members.return_value = 3
        self.repo.list_members.return_value = [
            _make_member_doc("sa@test.com", "superadmin"),
            _make_member_doc("alice@test.com", "admin"),
            _make_member_doc("bob@test.com", "viewer"),
        ]
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await list_team_members(role=None, is_active=None, offset=0, limit=50, ctx=ctx)
        assert len(result.members) == 2
        roles = [m.role for m in result.members]
        assert "superadmin" not in roles

    @pytest.mark.asyncio
    async def test_superadmin_visible_to_superadmin(self):
        from src.multi_tenant.admin_team_api import list_team_members

        self.repo.count_members.return_value = 2
        self.repo.list_members.return_value = [
            _make_member_doc("sa@test.com", "superadmin"),
            _make_member_doc("alice@test.com", "admin"),
        ]
        ctx = _ctx(role=TeamMemberRole.SUPERADMIN)
        result = await list_team_members(role=None, is_active=None, offset=0, limit=50, ctx=ctx)
        assert len(result.members) == 2

    @pytest.mark.asyncio
    async def test_filter_by_superadmin_role_blocked_for_admin(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import list_team_members

        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await list_team_members(role="superadmin", is_active=None, offset=0, limit=50, ctx=ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_role_filter(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import list_team_members

        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await list_team_members(role="owner", is_active=None, offset=0, limit=50, ctx=ctx)
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Get single team member
# ---------------------------------------------------------------------------


class TestGetTeamMember:
    """Test GET /api/admin/team/{member_id}."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.repo = AsyncMock()
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_get_existing(self):
        from src.multi_tenant.admin_team_api import get_team_member

        doc = _make_member_doc("alice@test.com", "admin")
        self.repo.read.return_value = doc
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await get_team_member(f"{TENANT_ID}:alice@test.com", ctx=ctx)
        assert result.email == "alice@test.com"

    @pytest.mark.asyncio
    async def test_get_not_found(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import get_team_member

        self.repo.read.side_effect = DocumentNotFoundError("team_members", "x", TENANT_ID)
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await get_team_member("nonexistent", ctx=ctx)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_superadmin_hidden_from_non_superadmin(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import get_team_member

        doc = _make_member_doc("sa@test.com", "superadmin")
        self.repo.read.return_value = doc
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await get_team_member(f"{TENANT_ID}:sa@test.com", ctx=ctx)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_superadmin_visible_to_superadmin(self):
        from src.multi_tenant.admin_team_api import get_team_member

        doc = _make_member_doc("sa@test.com", "superadmin")
        self.repo.read.return_value = doc
        ctx = _ctx(role=TeamMemberRole.SUPERADMIN)
        result = await get_team_member(f"{TENANT_ID}:sa@test.com", ctx=ctx)
        assert result.role == "superadmin"


# ---------------------------------------------------------------------------
# Create team member
# ---------------------------------------------------------------------------


class TestCreateTeamMember:
    """Test POST /api/admin/team."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.repo = AsyncMock()
        self.repo.find_by_email.return_value = None  # No duplicate by default
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_create_admin(self):
        from src.multi_tenant.admin_team_api import create_team_member

        req = CreateTeamMemberRequest(email="new@test.com", display_name="New User", role="admin")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await create_team_member(req, ctx=ctx)
        assert result.email == "new@test.com"
        assert result.role == "admin"
        assert result.user_api_key is not None
        assert result.user_api_key.startswith("ar_user_")
        assert result.user_api_key_prefix is not None
        self.repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_escalation_agent_with_categories(self):
        from src.multi_tenant.admin_team_api import create_team_member

        req = CreateTeamMemberRequest(
            email="agent@test.com",
            display_name="Agent",
            role="escalation_agent",
            escalation_categories=["sales", "support"],
        )
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await create_team_member(req, ctx=ctx)
        assert result.role == "escalation_agent"
        assert result.escalation_categories == ["sales", "support"]

    @pytest.mark.asyncio
    async def test_create_superadmin_blocked(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import create_team_member

        req = CreateTeamMemberRequest(email="sa@test.com", display_name="SA", role="superadmin")
        ctx = _ctx(role=TeamMemberRole.SUPERADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await create_team_member(req, ctx=ctx)
        assert exc_info.value.status_code == 400
        assert "auto-provisioned" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_invalid_role(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import create_team_member

        req = CreateTeamMemberRequest(email="x@test.com", display_name="X", role="owner")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await create_team_member(req, ctx=ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_duplicate_email(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import create_team_member

        self.repo.find_by_email.return_value = _make_member_doc("dup@test.com")
        req = CreateTeamMemberRequest(email="dup@test.com", display_name="Dup", role="admin")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await create_team_member(req, ctx=ctx)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_categories_on_non_agent_blocked(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import create_team_member

        req = CreateTeamMemberRequest(
            email="x@test.com",
            display_name="X",
            role="admin",
            escalation_categories=["sales"],
        )
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await create_team_member(req, ctx=ctx)
        assert exc_info.value.status_code == 400
        assert "escalation_agent" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_category(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import create_team_member

        req = CreateTeamMemberRequest(
            email="x@test.com",
            display_name="X",
            role="escalation_agent",
            escalation_categories=["bogus"],
        )
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await create_team_member(req, ctx=ctx)
        assert exc_info.value.status_code == 400
        assert "bogus" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_api_key_returned_once(self):
        """The raw API key should be in the create response but NOT stored in DB."""
        from src.multi_tenant.admin_team_api import create_team_member

        req = CreateTeamMemberRequest(email="new@test.com", display_name="New", role="viewer")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await create_team_member(req, ctx=ctx)

        # Key returned in response
        assert result.user_api_key is not None
        assert len(result.user_api_key) > 20

        # But the document stored in DB has hash, not raw key
        call_args = self.repo.create.call_args
        stored_doc = call_args[0][1]  # second positional arg
        doc_dict = stored_doc.model_dump()
        assert doc_dict.get("user_api_key_hash") is not None
        assert "user_api_key" not in doc_dict or doc_dict.get("user_api_key") is None


# ---------------------------------------------------------------------------
# Update team member
# ---------------------------------------------------------------------------


class TestUpdateTeamMember:
    """Test PUT /api/admin/team/{member_id}."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.repo = AsyncMock()
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_update_display_name(self):
        from src.multi_tenant.admin_team_api import update_team_member

        self.repo.read.return_value = _make_member_doc("alice@test.com", "admin")
        req = UpdateTeamMemberRequest(display_name="Alice Updated")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await update_team_member(f"{TENANT_ID}:alice@test.com", req, ctx=ctx)
        assert result.display_name == "Alice Updated"
        self.repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_role_to_escalation_agent(self):
        from src.multi_tenant.admin_team_api import update_team_member

        self.repo.read.return_value = _make_member_doc("alice@test.com", "admin")
        req = UpdateTeamMemberRequest(role="escalation_agent", escalation_categories=["sales"])
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await update_team_member(f"{TENANT_ID}:alice@test.com", req, ctx=ctx)
        assert result.role == "escalation_agent"
        assert result.escalation_categories == ["sales"]

    @pytest.mark.asyncio
    async def test_promote_to_superadmin_blocked(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import update_team_member

        self.repo.read.return_value = _make_member_doc("alice@test.com", "admin")
        req = UpdateTeamMemberRequest(role="superadmin")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await update_team_member(f"{TENANT_ID}:alice@test.com", req, ctx=ctx)
        assert exc_info.value.status_code == 400
        assert "auto-provisioned" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_modify_superadmin_by_admin_returns_404(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import update_team_member

        self.repo.read.return_value = _make_member_doc("sa@test.com", "superadmin")
        req = UpdateTeamMemberRequest(display_name="Hacked")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await update_team_member(f"{TENANT_ID}:sa@test.com", req, ctx=ctx)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_modify_superadmin_by_superadmin_ok(self):
        from src.multi_tenant.admin_team_api import update_team_member

        self.repo.read.return_value = _make_member_doc("sa@test.com", "superadmin")
        req = UpdateTeamMemberRequest(display_name="Super Admin Updated")
        ctx = _ctx(role=TeamMemberRole.SUPERADMIN)
        result = await update_team_member(f"{TENANT_ID}:sa@test.com", req, ctx=ctx)
        assert result.display_name == "Super Admin Updated"

    @pytest.mark.asyncio
    async def test_categories_cleared_on_role_change(self):
        from src.multi_tenant.admin_team_api import update_team_member

        self.repo.read.return_value = _make_member_doc(
            "agent@test.com", "escalation_agent", escalation_categories=["sales"]
        )
        req = UpdateTeamMemberRequest(role="admin")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await update_team_member(f"{TENANT_ID}:agent@test.com", req, ctx=ctx)
        assert result.role == "admin"
        assert result.escalation_categories == []

    @pytest.mark.asyncio
    async def test_categories_on_non_agent_blocked(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import update_team_member

        self.repo.read.return_value = _make_member_doc("alice@test.com", "admin")
        req = UpdateTeamMemberRequest(escalation_categories=["sales"])
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await update_team_member(f"{TENANT_ID}:alice@test.com", req, ctx=ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_category_on_update(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import update_team_member

        self.repo.read.return_value = _make_member_doc("agent@test.com", "escalation_agent")
        req = UpdateTeamMemberRequest(escalation_categories=["invalid_cat"])
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await update_team_member(f"{TENANT_ID}:agent@test.com", req, ctx=ctx)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_reactivate_member(self):
        from src.multi_tenant.admin_team_api import update_team_member

        self.repo.read.return_value = _make_member_doc("alice@test.com", "admin", is_active=False)
        req = UpdateTeamMemberRequest(is_active=True)
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await update_team_member(f"{TENANT_ID}:alice@test.com", req, ctx=ctx)
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_not_found(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import update_team_member

        self.repo.read.side_effect = DocumentNotFoundError("team_members", "x", TENANT_ID)
        req = UpdateTeamMemberRequest(display_name="X")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await update_team_member("nonexistent", req, ctx=ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Deactivate team member
# ---------------------------------------------------------------------------


class TestDeleteTeamMember:
    """Test DELETE /api/admin/team/{member_id} (hard delete)."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.repo = AsyncMock()
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_delete_admin(self):
        from src.multi_tenant.admin_team_api import delete_team_member

        self.repo.read.return_value = _make_member_doc("alice@test.com", "admin")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await delete_team_member(f"{TENANT_ID}:alice@test.com", ctx=ctx)
        assert result.id == f"{TENANT_ID}:alice@test.com"
        self.repo.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_superadmin_blocked(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import delete_team_member

        self.repo.read.return_value = _make_member_doc("sa@test.com", "superadmin")
        ctx = _ctx(role=TeamMemberRole.SUPERADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await delete_team_member(f"{TENANT_ID}:sa@test.com", ctx=ctx)
        assert exc_info.value.status_code == 400
        assert "superadmin" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_superadmin_hidden_from_admin(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import delete_team_member

        self.repo.read.return_value = _make_member_doc("sa@test.com", "superadmin")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await delete_team_member(f"{TENANT_ID}:sa@test.com", ctx=ctx)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import delete_team_member

        self.repo.read.side_effect = DocumentNotFoundError("team_members", "x", TENANT_ID)
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await delete_team_member("nonexistent", ctx=ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Rotate API key
# ---------------------------------------------------------------------------


class TestRotateUserApiKey:
    """Test POST /api/admin/team/{member_id}/rotate-key."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.repo = AsyncMock()
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_rotate_key(self):
        from src.multi_tenant.admin_team_api import rotate_user_api_key

        self.repo.read.return_value = _make_member_doc("alice@test.com", "admin")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await rotate_user_api_key(f"{TENANT_ID}:alice@test.com", ctx=ctx)
        assert result.user_api_key.startswith("ar_user_")
        assert result.user_api_key_prefix.endswith("...")
        assert result.rotated_at is not None
        self.repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_rotate_updates_hash_in_db(self):
        from src.multi_tenant.admin_team_api import rotate_user_api_key

        self.repo.read.return_value = _make_member_doc("alice@test.com", "admin")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        await rotate_user_api_key(f"{TENANT_ID}:alice@test.com", ctx=ctx)

        # Verify the patch includes new hash
        patch_call = self.repo.patch.call_args
        operations = patch_call.kwargs.get("operations", patch_call[1].get("operations", []))
        paths = [op["path"] for op in operations]
        assert "/user_api_key_hash" in paths
        assert "/user_api_key_prefix" in paths

    @pytest.mark.asyncio
    async def test_rotate_superadmin_key_by_admin_returns_404(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import rotate_user_api_key

        self.repo.read.return_value = _make_member_doc("sa@test.com", "superadmin")
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await rotate_user_api_key(f"{TENANT_ID}:sa@test.com", ctx=ctx)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_rotate_superadmin_key_by_superadmin_ok(self):
        from src.multi_tenant.admin_team_api import rotate_user_api_key

        self.repo.read.return_value = _make_member_doc("sa@test.com", "superadmin")
        ctx = _ctx(role=TeamMemberRole.SUPERADMIN)
        result = await rotate_user_api_key(f"{TENANT_ID}:sa@test.com", ctx=ctx)
        assert result.user_api_key.startswith("ar_user_")

    @pytest.mark.asyncio
    async def test_rotate_not_found(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import rotate_user_api_key

        self.repo.read.side_effect = DocumentNotFoundError("team_members", "x", TENANT_ID)
        ctx = _ctx(role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await rotate_user_api_key("nonexistent", ctx=ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Service configuration
# ---------------------------------------------------------------------------


class TestServiceConfiguration:
    """Test service wiring."""

    def test_repo_not_configured_raises_503(self):
        from fastapi import HTTPException

        from src.multi_tenant.admin_team_api import _get_repo

        configure_admin_team_services(None)
        with pytest.raises(HTTPException) as exc_info:
            _get_repo()
        assert exc_info.value.status_code == 503

    def test_repo_configured_returns_repo(self):
        from src.multi_tenant.admin_team_api import _get_repo

        repo = AsyncMock()
        configure_admin_team_services(repo)
        assert _get_repo() is repo
        configure_admin_team_services(None)


# ---------------------------------------------------------------------------
# Whoami endpoint
# ---------------------------------------------------------------------------


class TestWhoami:
    """Test GET /api/admin/team/whoami — caller identity."""

    @pytest.mark.asyncio
    async def test_whoami_user_api_key_admin(self):
        ctx = _ctx(role=TeamMemberRole.ADMIN, member_id="m1", email="admin@example.com")
        resp = await whoami(ctx)
        assert isinstance(resp, WhoamiResponse)
        assert resp.tenant_id == TENANT_ID
        assert resp.role == "admin"
        assert resp.team_member_id == "m1"
        assert resp.email == "admin@example.com"
        assert resp.auth_method == "user_api_key"

    @pytest.mark.asyncio
    async def test_whoami_user_api_key_superadmin(self):
        ctx = _ctx(role=TeamMemberRole.SUPERADMIN, member_id="sa1", email="super@example.com")
        resp = await whoami(ctx)
        assert resp.role == "superadmin"
        assert resp.auth_method == "user_api_key"

    @pytest.mark.asyncio
    async def test_whoami_user_api_key_escalation_agent(self):
        ctx = _ctx(role=TeamMemberRole.ESCALATION_AGENT, member_id="ea1", email="agent@example.com")
        resp = await whoami(ctx)
        assert resp.role == "escalation_agent"
        assert resp.team_member_id == "ea1"

    @pytest.mark.asyncio
    async def test_whoami_user_api_key_viewer(self):
        ctx = _ctx(role=TeamMemberRole.VIEWER, member_id="v1", email="viewer@example.com")
        resp = await whoami(ctx)
        assert resp.role == "viewer"
        assert resp.auth_method == "user_api_key"

    @pytest.mark.asyncio
    async def test_whoami_legacy_tenant_key(self):
        ctx = _ctx()  # No role = legacy tenant key
        resp = await whoami(ctx)
        assert resp.tenant_id == TENANT_ID
        assert resp.role == "admin"
        assert resp.team_member_id is None
        assert resp.email is None
        assert resp.auth_method == "tenant_api_key"

    def test_whoami_response_model_camel_case(self):
        resp = WhoamiResponse(
            tenant_id="t1",
            role="admin",
            team_member_id="m1",
            email="a@b.com",
            auth_method="user_api_key",
        )
        data = resp.model_dump(by_alias=True)
        assert "tenantId" in data
        assert "teamMemberId" in data
        assert "authMethod" in data


# ---------------------------------------------------------------------------
# Unresolved escalation count (Backlog #19 / D57)
# ---------------------------------------------------------------------------


class TestUnresolvedEscalationCount:
    """Verify unresolved_escalation_count enrichment in list endpoint."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.team_repo = AsyncMock()
        self.conv_repo = AsyncMock()
        configure_admin_team_services(self.team_repo, conv_repo=self.conv_repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_escalation_agent_has_count(self):
        """Escalation agent response includes unresolved count."""
        from src.multi_tenant.admin_team_api import list_team_members

        agent_doc = _make_member_doc(
            "agent@test.com", "escalation_agent",
            escalation_categories=["support"],
        )
        self.team_repo.count_members.return_value = 1
        self.team_repo.list_members.return_value = [agent_doc]
        self.conv_repo.count_filtered.return_value = 3

        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await list_team_members(role=None, is_active=None, offset=0, limit=50, ctx=ctx)

        assert len(result.members) == 1
        assert result.members[0].unresolved_escalation_count == 3

    @pytest.mark.asyncio
    async def test_non_agent_has_zero_count(self):
        """Admin role has 0 unresolved count (not an escalation agent)."""
        from src.multi_tenant.admin_team_api import list_team_members

        admin_doc = _make_member_doc("admin@test.com", "admin")
        self.team_repo.count_members.return_value = 1
        self.team_repo.list_members.return_value = [admin_doc]

        ctx = _ctx(role=TeamMemberRole.ADMIN)
        result = await list_team_members(role=None, is_active=None, offset=0, limit=50, ctx=ctx)

        assert result.members[0].unresolved_escalation_count == 0

    @pytest.mark.asyncio
    async def test_count_filters_by_escalated_status(self):
        """count_filtered is called with status=ESCALATED."""
        from src.multi_tenant.admin_team_api import list_team_members
        from src.multi_tenant.cosmos_schema import ConversationStatus

        agent_doc = _make_member_doc(
            "agent@test.com", "escalation_agent",
            escalation_categories=["support"],
        )
        self.team_repo.count_members.return_value = 1
        self.team_repo.list_members.return_value = [agent_doc]
        self.conv_repo.count_filtered.return_value = 0

        ctx = _ctx(role=TeamMemberRole.ADMIN)
        await list_team_members(role=None, is_active=None, offset=0, limit=50, ctx=ctx)

        self.conv_repo.count_filtered.assert_called_once()
        call_kwargs = self.conv_repo.count_filtered.call_args
        assert call_kwargs[1]["status"] == ConversationStatus.ESCALATED
        assert call_kwargs[1]["assigned_to"] == agent_doc["id"]
