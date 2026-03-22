"""Tests for SPA Platform Admin User Management (SPEC-1675).

Covers:
    GET    /api/superadmin/platform-admin/users              — list users
    POST   /api/superadmin/platform-admin/users              — create operator
    DELETE /api/superadmin/platform-admin/users/{admin_id}   — deactivate operator
    POST   /api/superadmin/platform-admin/users/backup-codes — generate backup codes
    PUT    /api/superadmin/platform-admin/users/notification-email — set notif email
    require_spa_superadmin() guard
    TenantContext.platform_admin_role field

Run:
    pytest tests/multi_tenant/test_spa_user_management.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.multi_tenant.auth import TenantContext, hash_api_key
from src.multi_tenant.cosmos_schema import AuditEventType, TenantStatus
from src.multi_tenant.superadmin_api import (
    BackupCodesResponse,
    CreateOperatorRequest,
    CreateOperatorResponse,
    PlatformAdminUserResponse,
    UpdateNotificationEmailRequest,
    configure_superadmin_services,
    create_platform_admin_operator,
    deactivate_platform_admin_user,
    generate_backup_codes,
    list_platform_admin_users,
    update_notification_email,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _superadmin_ctx() -> TenantContext:
    return TenantContext(
        tenant_id="__platform__",
        is_platform_admin=True,
        auth_method="spa_api_key",
        status=TenantStatus.ACTIVE,
        platform_admin_id="admin-001",
        platform_admin_email="super@remaker.digital",
        platform_admin_role="superadmin",
    )


def _operator_ctx() -> TenantContext:
    return TenantContext(
        tenant_id="__platform__",
        is_platform_admin=True,
        auth_method="spa_api_key",
        status=TenantStatus.ACTIVE,
        platform_admin_id="admin-002",
        platform_admin_email="ops@remaker.digital",
        platform_admin_role="operator",
    )


@pytest.fixture()
def mock_platform_admin_repo():
    repo = MagicMock()
    repo.list_admins = AsyncMock(return_value=[
        {
            "admin_id": "admin-001",
            "email": "super@remaker.digital",
            "display_name": "Super Admin",
            "role": "superadmin",
            "is_active": True,
            "created_at": "2026-03-01T00:00:00Z",
            "last_login_at": "2026-03-08T10:00:00Z",
            "notification_email_address": None,
            "backup_codes_remaining": 8,
            "created_by": None,
        },
    ])
    repo.find_by_email = AsyncMock(return_value=None)
    repo.find_by_admin_id = AsyncMock(return_value=None)
    repo.create_admin = AsyncMock(return_value={"admin_id": "admin-new"})
    repo.deactivate_admin = AsyncMock(return_value={"admin_id": "admin-002"})
    repo.update_backup_code_hashes = AsyncMock(return_value={})
    repo.update_notification_email = AsyncMock(return_value={})
    return repo


@pytest.fixture()
def mock_audit_repo():
    repo = MagicMock()
    repo.log_event = AsyncMock()
    return repo


@pytest.fixture(autouse=True)
def _wire_repos(mock_platform_admin_repo, mock_audit_repo):
    configure_superadmin_services(
        tenant_repo=MagicMock(),
        audit_repo=mock_audit_repo,
        platform_admin_repo=mock_platform_admin_repo,
    )
    yield
    # Reset
    configure_superadmin_services(
        tenant_repo=MagicMock(),
        audit_repo=MagicMock(),
        platform_admin_repo=None,
    )


# ---------------------------------------------------------------------------
# TenantContext role field
# ---------------------------------------------------------------------------


class TestTenantContextRole:
    """Verify platform_admin_role field on TenantContext."""

    def test_superadmin_role_set(self):
        ctx = _superadmin_ctx()
        assert ctx.platform_admin_role == "superadmin"

    def test_operator_role_set(self):
        ctx = _operator_ctx()
        assert ctx.platform_admin_role == "operator"

    def test_role_default_none(self):
        ctx = TenantContext(tenant_id="t1")
        assert ctx.platform_admin_role is None


# ---------------------------------------------------------------------------
# require_spa_superadmin() guard
# ---------------------------------------------------------------------------


class TestRequireSpaSuperadmin:
    """Test the require_spa_superadmin() FastAPI dependency."""

    def test_guard_exists(self):
        from src.multi_tenant.middleware import require_spa_superadmin
        dep = require_spa_superadmin()
        assert callable(dep)

    @pytest.mark.asyncio
    async def test_superadmin_passes(self):
        from src.multi_tenant.middleware import require_spa_superadmin
        from unittest.mock import MagicMock as MM

        dep = require_spa_superadmin()
        request = MM()
        request.state.tenant_context = _superadmin_ctx()
        result = await dep(request)
        assert result.platform_admin_role == "superadmin"

    @pytest.mark.asyncio
    async def test_operator_blocked(self):
        from src.multi_tenant.middleware import require_spa_superadmin

        dep = require_spa_superadmin()
        request = MagicMock()
        request.state.tenant_context = _operator_ctx()
        with pytest.raises(HTTPException) as exc_info:
            await dep(request)
        assert exc_info.value.status_code == 403
        assert "superadmin" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_non_platform_admin_blocked(self):
        from src.multi_tenant.middleware import require_spa_superadmin

        dep = require_spa_superadmin()
        request = MagicMock()
        request.state.tenant_context = TenantContext(
            tenant_id="tenant-1",
            is_platform_admin=False,
        )
        with pytest.raises(HTTPException) as exc_info:
            await dep(request)
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# List users
# ---------------------------------------------------------------------------


class TestListUsers:

    @pytest.mark.asyncio
    async def test_list_users_returns_admins(self):
        result = await list_platform_admin_users(ctx=_superadmin_ctx())
        assert len(result) == 1
        assert result[0].admin_id == "admin-001"
        assert result[0].role == "superadmin"

    @pytest.mark.asyncio
    async def test_list_users_repo_not_initialized(self):
        configure_superadmin_services(
            tenant_repo=MagicMock(),
            audit_repo=MagicMock(),
            platform_admin_repo=None,
        )
        with pytest.raises(HTTPException) as exc_info:
            await list_platform_admin_users(ctx=_superadmin_ctx())
        assert exc_info.value.status_code == 503


# ---------------------------------------------------------------------------
# Create operator
# ---------------------------------------------------------------------------


class TestCreateOperator:

    @pytest.mark.asyncio
    async def test_create_operator_success(self, mock_platform_admin_repo):
        body = CreateOperatorRequest(email="ops@remaker.digital", display_name="Operator 1")
        result = await create_platform_admin_operator(body=body, ctx=_superadmin_ctx())
        assert result.role == "operator"
        assert result.email == "ops@remaker.digital"
        assert result.api_key.startswith("ar_spa_plat_")
        mock_platform_admin_repo.create_admin.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_operator_blocked_for_operator(self):
        body = CreateOperatorRequest(email="new@test.com", display_name="New")
        with pytest.raises(HTTPException) as exc_info:
            await create_platform_admin_operator(body=body, ctx=_operator_ctx())
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_create_operator_duplicate_email(self, mock_platform_admin_repo):
        mock_platform_admin_repo.find_by_email.return_value = {"admin_id": "existing"}
        body = CreateOperatorRequest(email="existing@test.com", display_name="Dup")
        with pytest.raises(HTTPException) as exc_info:
            await create_platform_admin_operator(body=body, ctx=_superadmin_ctx())
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_create_operator_audit_logged(self, mock_audit_repo):
        body = CreateOperatorRequest(email="new@test.com", display_name="New Op")
        await create_platform_admin_operator(body=body, ctx=_superadmin_ctx())
        mock_audit_repo.log_event.assert_called_once()
        call_kwargs = mock_audit_repo.log_event.call_args
        assert call_kwargs.kwargs["event_type"] == AuditEventType.SECURITY_EVENT
        assert "spa_operator_created" in str(call_kwargs.kwargs["payload"])


# ---------------------------------------------------------------------------
# Deactivate operator
# ---------------------------------------------------------------------------


class TestDeactivateOperator:

    @pytest.mark.asyncio
    async def test_deactivate_operator_success(self, mock_platform_admin_repo):
        mock_platform_admin_repo.find_by_admin_id.return_value = {
            "admin_id": "admin-002",
            "email": "ops@test.com",
            "role": "operator",
        }
        result = await deactivate_platform_admin_user(
            admin_id="admin-002", ctx=_superadmin_ctx(),
        )
        assert "deactivated" in result.message.lower()
        mock_platform_admin_repo.deactivate_admin.assert_called_once()

    @pytest.mark.asyncio
    async def test_cannot_deactivate_self(self):
        with pytest.raises(HTTPException) as exc_info:
            await deactivate_platform_admin_user(
                admin_id="admin-001", ctx=_superadmin_ctx(),
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_cannot_deactivate_superadmin(self, mock_platform_admin_repo):
        mock_platform_admin_repo.find_by_admin_id.return_value = {
            "admin_id": "admin-003",
            "email": "other-super@test.com",
            "role": "superadmin",
        }
        with pytest.raises(HTTPException) as exc_info:
            await deactivate_platform_admin_user(
                admin_id="admin-003", ctx=_superadmin_ctx(),
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_operator_cannot_deactivate(self):
        with pytest.raises(HTTPException) as exc_info:
            await deactivate_platform_admin_user(
                admin_id="admin-001", ctx=_operator_ctx(),
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_deactivate_not_found(self, mock_platform_admin_repo):
        mock_platform_admin_repo.find_by_admin_id.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await deactivate_platform_admin_user(
                admin_id="nonexistent", ctx=_superadmin_ctx(),
            )
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Backup codes
# ---------------------------------------------------------------------------


class TestBackupCodes:

    @pytest.mark.asyncio
    async def test_generate_backup_codes_returns_8(self, mock_platform_admin_repo):
        result = await generate_backup_codes(ctx=_superadmin_ctx())
        assert len(result.codes) == 8
        assert result.count == 8
        # Each code is 8 hex chars
        for code in result.codes:
            assert len(code) == 8
            int(code, 16)  # Valid hex

    @pytest.mark.asyncio
    async def test_backup_codes_stored_as_hashes(self, mock_platform_admin_repo):
        result = await generate_backup_codes(ctx=_superadmin_ctx())
        call_kwargs = mock_platform_admin_repo.update_backup_code_hashes.call_args
        stored_hashes = call_kwargs.kwargs.get("hashes") or call_kwargs[1].get("hashes") or call_kwargs[0][1]
        assert len(stored_hashes) == 8
        # Hashes should be SHA-256 hex (64 chars)
        for h in stored_hashes:
            assert len(h) == 64

    @pytest.mark.asyncio
    async def test_backup_codes_all_unique(self):
        result = await generate_backup_codes(ctx=_superadmin_ctx())
        assert len(set(result.codes)) == 8

    @pytest.mark.asyncio
    async def test_operator_can_generate_own_codes(self):
        result = await generate_backup_codes(ctx=_operator_ctx())
        assert len(result.codes) == 8


# ---------------------------------------------------------------------------
# Notification email
# ---------------------------------------------------------------------------


class TestNotificationEmail:

    @pytest.mark.asyncio
    async def test_set_notification_email(self, mock_platform_admin_repo):
        body = UpdateNotificationEmailRequest(email="alerts@remaker.digital")
        result = await update_notification_email(body=body, ctx=_superadmin_ctx())
        assert "set" in result.message.lower()
        mock_platform_admin_repo.update_notification_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_notification_email(self, mock_platform_admin_repo):
        body = UpdateNotificationEmailRequest(email=None)
        result = await update_notification_email(body=body, ctx=_superadmin_ctx())
        assert "cleared" in result.message.lower()

    @pytest.mark.asyncio
    async def test_operator_can_set_own_email(self, mock_platform_admin_repo):
        body = UpdateNotificationEmailRequest(email="ops-alert@test.com")
        result = await update_notification_email(body=body, ctx=_operator_ctx())
        assert "set" in result.message.lower()
