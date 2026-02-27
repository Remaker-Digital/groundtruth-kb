"""Endpoint-level tests for Admin Team Management API.

Covers 8 specs:
    1. Router prefix /api/admin/team
    2. list_team_members — empty list
    3. whoami — with/without team_member_role
    4. get_team_member — mock repo.read returning a doc dict
    5. create_team_member — patch generate_user_api_key/hash_api_key, mock repo
    6. update_team_member — mock repo.read and repo.patch
    7. delete_team_member — mock repo.read and repo.delete
    8. rotate_user_api_key — patch generate_user_api_key/hash_api_key, mock repo

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_team_api import (
    configure_admin_team_services,
    router,
)
from src.multi_tenant.cosmos_schema import TeamMemberRole
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


def _member_doc(
    email: str = "alice@example.com",
    role: str = "admin",
    **extra,
) -> dict:
    member_id = f"{TENANT_ID}:{email}"
    doc = {
        "id": member_id,
        "tenant_id": TENANT_ID,
        "email": email,
        "display_name": email.split("@")[0].title(),
        "role": role,
        "is_active": True,
        "escalation_categories": [],
        "max_concurrent_conversations": 5,
        "user_api_key_hash": "fakehash",
        "user_api_key_prefix": "ar_user_test...",
        "created_at": NOW_ISO,
        "updated_at": NOW_ISO,
        "last_login_at": None,
        "invited_by": "system",
    }
    doc.update(extra)
    return doc


# ---------------------------------------------------------------------------
# 1. Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """Spec: Router has prefix /api/admin/team."""

    def test_router_prefix_is_correct(self):
        assert router.prefix == "/api/admin/team"

    def test_router_tags(self):
        assert "admin-team" in router.tags


# ---------------------------------------------------------------------------
# 2. list_team_members — empty list
# ---------------------------------------------------------------------------


class TestListTeamMembersEndpoint:
    """Spec: GET /api/admin/team returns paginated team list."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_returns_empty_list(self):
        from src.multi_tenant.admin_team_api import list_team_members

        self.repo.count_members.return_value = 0
        self.repo.list_members.return_value = []

        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)
        result = await list_team_members(
            role=None, is_active=None, offset=0, limit=50, ctx=ctx,
        )

        assert result.total_count == 0
        assert result.members == []
        assert result.tenant_id == TENANT_ID
        assert result.offset == 0
        assert result.limit == 50

    @pytest.mark.asyncio
    async def test_repo_count_and_list_called(self):
        from src.multi_tenant.admin_team_api import list_team_members

        self.repo.count_members.return_value = 0
        self.repo.list_members.return_value = []

        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)
        await list_team_members(
            role=None, is_active=None, offset=0, limit=50, ctx=ctx,
        )

        self.repo.count_members.assert_called_once()
        self.repo.list_members.assert_called_once()


# ---------------------------------------------------------------------------
# 3. whoami — with and without team_member_role
# ---------------------------------------------------------------------------


class TestWhoamiEndpoint:
    """Spec: GET /api/admin/team/whoami returns caller identity."""

    @pytest.mark.asyncio
    async def test_whoami_with_role(self):
        from src.multi_tenant.admin_team_api import whoami

        ctx = _ctx(
            team_member_role=TeamMemberRole.ADMIN,
            team_member_id="m-42",
            team_member_email="admin@example.com",
        )
        result = await whoami(ctx)

        assert result.tenant_id == TENANT_ID
        assert result.role == "admin"
        assert result.team_member_id == "m-42"
        assert result.email == "admin@example.com"
        assert result.auth_method == "user_api_key"

    @pytest.mark.asyncio
    async def test_whoami_without_role_returns_admin(self):
        from src.multi_tenant.admin_team_api import whoami

        ctx = _ctx(team_member_role=None)
        result = await whoami(ctx)

        assert result.role == "admin"
        assert result.auth_method == "tenant_api_key"
        assert result.team_member_id is None
        assert result.email is None


# ---------------------------------------------------------------------------
# 4. get_team_member — repo.read returning a doc
# ---------------------------------------------------------------------------


class TestGetTeamMemberEndpoint:
    """Spec: GET /api/admin/team/{member_id} returns single member."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_returns_member_from_doc(self):
        from src.multi_tenant.admin_team_api import get_team_member

        doc = _member_doc("alice@example.com", "admin")
        self.repo.read.return_value = doc

        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)
        result = await get_team_member(f"{TENANT_ID}:alice@example.com", ctx=ctx)

        assert result.email == "alice@example.com"
        assert result.role == "admin"
        assert result.tenant_id == TENANT_ID
        self.repo.read.assert_called_once_with(TENANT_ID, f"{TENANT_ID}:alice@example.com")

    @pytest.mark.asyncio
    async def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_team_api import get_team_member

        self.repo.read.side_effect = DocumentNotFoundError(
            "team_members", "nonexistent", TENANT_ID,
        )

        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await get_team_member("nonexistent", ctx=ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# 5. create_team_member — key generation and repo.create
# ---------------------------------------------------------------------------


class TestCreateTeamMemberEndpoint:
    """Spec: POST /api/admin/team creates member with per-user API key."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        self.repo.find_by_email.return_value = None
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_creates_member_with_api_key(self):
        from src.multi_tenant.admin_team_api import (
            CreateTeamMemberRequest,
            create_team_member,
        )

        req = CreateTeamMemberRequest(
            email="new@example.com",
            display_name="New User",
            role="admin",
        )
        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)

        with patch(
            "src.multi_tenant.admin_team_api.generate_user_api_key",
            return_value="ar_user_test_FAKEKEY123456789",
        ), patch(
            "src.multi_tenant.admin_team_api.hash_api_key",
            return_value="hashed_fake_key",
        ):
            result = await create_team_member(req, ctx=ctx)

        assert result.email == "new@example.com"
        assert result.role == "admin"
        assert result.user_api_key == "ar_user_test_FAKEKEY123456789"
        assert result.user_api_key_prefix == "ar_user_test..."
        self.repo.find_by_email.assert_called_once_with(TENANT_ID, "new@example.com")
        self.repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_rejects_duplicate_email(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_team_api import (
            CreateTeamMemberRequest,
            create_team_member,
        )

        self.repo.find_by_email.return_value = _member_doc("dup@example.com")
        req = CreateTeamMemberRequest(
            email="dup@example.com",
            display_name="Dup",
            role="admin",
        )
        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)

        with pytest.raises(HTTPException) as exc_info:
            await create_team_member(req, ctx=ctx)
        assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# 6. update_team_member — repo.read and repo.patch
# ---------------------------------------------------------------------------


class TestUpdateTeamMemberEndpoint:
    """Spec: PUT /api/admin/team/{member_id} updates member via patch."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_updates_display_name(self):
        from src.multi_tenant.admin_team_api import (
            UpdateTeamMemberRequest,
            update_team_member,
        )

        self.repo.read.return_value = _member_doc("alice@example.com", "admin")
        req = UpdateTeamMemberRequest(display_name="Alice Updated")
        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)

        result = await update_team_member(
            f"{TENANT_ID}:alice@example.com", req, ctx=ctx,
        )

        assert result.display_name == "Alice Updated"
        self.repo.read.assert_called_once_with(
            TENANT_ID, f"{TENANT_ID}:alice@example.com",
        )
        self.repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_team_api import (
            UpdateTeamMemberRequest,
            update_team_member,
        )

        self.repo.read.side_effect = DocumentNotFoundError(
            "team_members", "gone", TENANT_ID,
        )
        req = UpdateTeamMemberRequest(display_name="X")
        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)

        with pytest.raises(HTTPException) as exc_info:
            await update_team_member("gone", req, ctx=ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# 7. delete_team_member — repo.read and repo.delete
# ---------------------------------------------------------------------------


class TestDeleteTeamMemberEndpoint:
    """Spec: DELETE /api/admin/team/{member_id} removes member."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_deletes_existing_member(self):
        from src.multi_tenant.admin_team_api import delete_team_member

        doc = _member_doc("alice@example.com", "admin")
        self.repo.read.return_value = doc
        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)

        result = await delete_team_member(
            f"{TENANT_ID}:alice@example.com", ctx=ctx,
        )

        assert result.id == f"{TENANT_ID}:alice@example.com"
        assert result.deleted_at is not None
        self.repo.read.assert_called_once()
        self.repo.delete.assert_called_once_with(
            TENANT_ID, f"{TENANT_ID}:alice@example.com",
        )

    @pytest.mark.asyncio
    async def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_team_api import delete_team_member

        self.repo.read.side_effect = DocumentNotFoundError(
            "team_members", "gone", TENANT_ID,
        )
        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)

        with pytest.raises(HTTPException) as exc_info:
            await delete_team_member("gone", ctx=ctx)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# 8. rotate_user_api_key — key generation and repo.patch
# ---------------------------------------------------------------------------


class TestRotateUserApiKeyEndpoint:
    """Spec: POST /api/admin/team/{member_id}/rotate-key rotates API key."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = AsyncMock()
        configure_admin_team_services(self.repo)
        yield
        configure_admin_team_services(None)

    @pytest.mark.asyncio
    async def test_rotates_key_and_returns_new_key(self):
        from src.multi_tenant.admin_team_api import rotate_user_api_key

        self.repo.read.return_value = _member_doc("alice@example.com", "admin")
        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)

        with patch(
            "src.multi_tenant.admin_team_api.generate_user_api_key",
            return_value="ar_user_test_NEWKEY999999999",
        ), patch(
            "src.multi_tenant.admin_team_api.hash_api_key",
            return_value="new_hashed_key",
        ):
            result = await rotate_user_api_key(
                f"{TENANT_ID}:alice@example.com", ctx=ctx,
            )

        assert result.user_api_key == "ar_user_test_NEWKEY999999999"
        assert result.user_api_key_prefix == "ar_user_test..."
        assert result.rotated_at is not None
        assert result.id == f"{TENANT_ID}:alice@example.com"

        self.repo.read.assert_called_once()
        self.repo.patch.assert_called_once()

        # Verify patch operations include hash and prefix
        patch_call = self.repo.patch.call_args
        operations = patch_call.kwargs.get(
            "operations", patch_call[1].get("operations", []),
        )
        paths = [op["path"] for op in operations]
        assert "/user_api_key_hash" in paths
        assert "/user_api_key_prefix" in paths

    @pytest.mark.asyncio
    async def test_raises_404_when_not_found(self):
        from fastapi import HTTPException
        from src.multi_tenant.admin_team_api import rotate_user_api_key

        self.repo.read.side_effect = DocumentNotFoundError(
            "team_members", "gone", TENANT_ID,
        )
        ctx = _ctx(team_member_role=TeamMemberRole.ADMIN)

        with pytest.raises(HTTPException) as exc_info:
            await rotate_user_api_key("gone", ctx=ctx)
        assert exc_info.value.status_code == 404
