"""Tests for SPA Platform Admin Key Regeneration endpoint (SPEC-1669).

Covers:
    POST /api/superadmin/platform-admin/regenerate-key — 12 tests
    - Happy path: key regenerated, old key invalidated
    - Response contains new ar_spa_* key
    - Response contains correct admin identity
    - Key hash updated in repository
    - Audit event logged as SECURITY_EVENT
    - Audit failure does not block regeneration
    - Repository not initialized → 503
    - Admin identity missing from context → 500
    - Repository update failure → 500
    - New key has correct prefix and format
    - key_regenerated_at timestamp stored
    - PlatformAdminRepository.update_api_key_hash method

Run:
    pytest tests/multi_tenant/test_superadmin_key_regeneration.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.multi_tenant.auth import (
    SPA_API_KEY_PREFIX,
    TenantContext,
    generate_spa_api_key,
    hash_api_key,
)
from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    TenantStatus,
)
from src.multi_tenant.superadmin_api import (
    RegenerateKeyResponse,
    configure_superadmin_services,
    regenerate_platform_admin_key,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_platform_admin_repo():
    """Create a mock PlatformAdminRepository."""
    repo = MagicMock()
    repo.update_api_key_hash = AsyncMock(return_value={
        "id": "admin-001",
        "admin_id": "admin-001",
        "email": "admin@remaker.digital",
        "api_key_hash": "new_hash_placeholder",
        "is_active": True,
        "updated_at": "2026-03-08T00:00:00+00:00",
        "key_regenerated_at": "2026-03-08T00:00:00+00:00",
    })
    return repo


@pytest.fixture()
def mock_audit_repo():
    """Create a mock AuditLogRepository."""
    repo = MagicMock()
    repo.log_event = AsyncMock(return_value={"id": "audit-001"})
    return repo


@pytest.fixture()
def mock_tenant_repo():
    """Create a mock TenantRepository for configure_superadmin_services."""
    return MagicMock()


@pytest.fixture()
def spa_admin_ctx():
    """Create a SPA platform admin TenantContext."""
    return TenantContext(
        tenant_id="__platform__",
        is_platform_admin=True,
        auth_method="spa_api_key",
        status=TenantStatus.ACTIVE,
        platform_admin_id="admin-001",
        platform_admin_email="admin@remaker.digital",
    )


@pytest.fixture()
def spa_admin_ctx_no_id():
    """Create a SPA platform admin context without admin_id."""
    return TenantContext(
        tenant_id="__platform__",
        is_platform_admin=True,
        auth_method="spa_api_key",
        status=TenantStatus.ACTIVE,
        platform_admin_id=None,
        platform_admin_email="admin@remaker.digital",
    )


@pytest.fixture(autouse=True)
def _setup_services(mock_tenant_repo, mock_platform_admin_repo, mock_audit_repo):
    """Wire up the module-level service references."""
    configure_superadmin_services(
        tenant_repo=mock_tenant_repo,
        audit_repo=mock_audit_repo,
        platform_admin_repo=mock_platform_admin_repo,
    )


# ---------------------------------------------------------------------------
# Tests: Happy path
# ---------------------------------------------------------------------------


class TestRegenerateKeyHappyPath:
    """SPEC-1669: Key regeneration happy path."""

    @pytest.mark.asyncio
    async def test_returns_new_key(
        self, spa_admin_ctx, mock_platform_admin_repo,
    ):
        """Key regeneration returns a new ar_spa_* key."""
        result = await regenerate_platform_admin_key(ctx=spa_admin_ctx)

        assert isinstance(result, RegenerateKeyResponse)
        assert result.new_api_key.startswith(SPA_API_KEY_PREFIX)
        assert result.admin_id == "admin-001"
        assert result.email == "admin@remaker.digital"

    @pytest.mark.asyncio
    async def test_key_hash_updated_in_repo(
        self, spa_admin_ctx, mock_platform_admin_repo,
    ):
        """Key regeneration calls repository with new hash."""
        result = await regenerate_platform_admin_key(ctx=spa_admin_ctx)

        mock_platform_admin_repo.update_api_key_hash.assert_called_once()
        call_kwargs = mock_platform_admin_repo.update_api_key_hash.call_args
        assert call_kwargs.kwargs["admin_id"] == "admin-001"

        # Verify the stored hash matches the returned raw key
        stored_hash = call_kwargs.kwargs["new_key_hash"]
        expected_hash = hash_api_key(result.new_api_key)
        assert stored_hash == expected_hash

    @pytest.mark.asyncio
    async def test_key_format_correct(self, spa_admin_ctx):
        """New key follows ar_spa_plat_{random} format."""
        result = await regenerate_platform_admin_key(ctx=spa_admin_ctx)

        key = result.new_api_key
        assert key.startswith("ar_spa_plat_")
        # Random part should be non-empty
        random_part = key[len("ar_spa_plat_"):]
        assert len(random_part) >= 20

    @pytest.mark.asyncio
    async def test_regenerated_at_is_iso_timestamp(self, spa_admin_ctx):
        """Regeneration timestamp is a valid ISO 8601 string."""
        result = await regenerate_platform_admin_key(ctx=spa_admin_ctx)

        # Must parse as a valid datetime
        ts = datetime.fromisoformat(result.regenerated_at)
        assert ts.tzinfo is not None  # Must be timezone-aware

    @pytest.mark.asyncio
    async def test_response_message_warns_about_single_display(self, spa_admin_ctx):
        """Response message warns that key is displayed once."""
        result = await regenerate_platform_admin_key(ctx=spa_admin_ctx)

        assert "not be shown again" in result.message
        assert "previous key" in result.message.lower()


# ---------------------------------------------------------------------------
# Tests: Audit logging
# ---------------------------------------------------------------------------


class TestRegenerateKeyAudit:
    """SPEC-1669 requirement 4: Key regeneration MUST be auditable."""

    @pytest.mark.asyncio
    async def test_audit_event_logged(
        self, spa_admin_ctx, mock_audit_repo,
    ):
        """Key regeneration logs a SECURITY_EVENT audit entry."""
        await regenerate_platform_admin_key(ctx=spa_admin_ctx)

        mock_audit_repo.log_event.assert_called_once()
        call_kwargs = mock_audit_repo.log_event.call_args
        assert call_kwargs.kwargs["event_type"] == AuditEventType.SECURITY_EVENT
        assert call_kwargs.kwargs["tenant_id"] == "__platform__"
        assert call_kwargs.kwargs["actor"] == "admin@remaker.digital"
        assert call_kwargs.kwargs["payload"]["action"] == "spa_key_regenerated"
        assert call_kwargs.kwargs["payload"]["admin_id"] == "admin-001"

    @pytest.mark.asyncio
    async def test_audit_failure_does_not_block_regeneration(
        self, spa_admin_ctx, mock_audit_repo,
    ):
        """Audit log failure must not prevent key regeneration."""
        mock_audit_repo.log_event = AsyncMock(
            side_effect=Exception("Cosmos unavailable"),
        )

        # Should NOT raise — audit failure is non-blocking
        result = await regenerate_platform_admin_key(ctx=spa_admin_ctx)
        assert result.new_api_key.startswith(SPA_API_KEY_PREFIX)


# ---------------------------------------------------------------------------
# Tests: Error cases
# ---------------------------------------------------------------------------


class TestRegenerateKeyErrors:
    """SPEC-1669: Error handling for key regeneration."""

    @pytest.mark.asyncio
    async def test_repo_not_initialized_returns_503(
        self, spa_admin_ctx, mock_tenant_repo, mock_audit_repo,
    ):
        """503 when platform admin repository is not wired."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            platform_admin_repo=None,
        )

        with pytest.raises(HTTPException) as exc_info:
            await regenerate_platform_admin_key(ctx=spa_admin_ctx)
        assert exc_info.value.status_code == 503
        assert "not initialized" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_missing_admin_id_returns_500(
        self, spa_admin_ctx_no_id,
    ):
        """500 when admin identity is not in context."""
        with pytest.raises(HTTPException) as exc_info:
            await regenerate_platform_admin_key(ctx=spa_admin_ctx_no_id)
        assert exc_info.value.status_code == 500
        assert "identity" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_repo_update_failure_returns_500(
        self, spa_admin_ctx, mock_platform_admin_repo,
    ):
        """500 when Cosmos DB update fails."""
        mock_platform_admin_repo.update_api_key_hash = AsyncMock(
            side_effect=Exception("Cosmos conflict"),
        )

        with pytest.raises(HTTPException) as exc_info:
            await regenerate_platform_admin_key(ctx=spa_admin_ctx)
        assert exc_info.value.status_code == 500
        assert "failed" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# Tests: Repository method
# ---------------------------------------------------------------------------


class TestUpdateApiKeyHash:
    """PlatformAdminRepository.update_api_key_hash method (SPEC-1669)."""

    def test_repository_has_update_method(self):
        """PlatformAdminRepository exposes update_api_key_hash."""
        from src.multi_tenant.repositories.platform_admin import (
            PlatformAdminRepository,
        )

        assert hasattr(PlatformAdminRepository, "update_api_key_hash")
        # Verify it's an async method (coroutine function)
        import inspect
        assert inspect.iscoroutinefunction(PlatformAdminRepository.update_api_key_hash)


# ---------------------------------------------------------------------------
# Tests: TenantContext fields
# ---------------------------------------------------------------------------


class TestTenantContextPlatformAdminFields:
    """SPEC-1667/1669: TenantContext carries platform admin identity."""

    def test_context_has_platform_admin_id(self):
        """TenantContext has platform_admin_id field."""
        ctx = TenantContext(
            tenant_id="__platform__",
            is_platform_admin=True,
            platform_admin_id="admin-001",
        )
        assert ctx.platform_admin_id == "admin-001"

    def test_context_has_platform_admin_email(self):
        """TenantContext has platform_admin_email field."""
        ctx = TenantContext(
            tenant_id="__platform__",
            is_platform_admin=True,
            platform_admin_email="admin@remaker.digital",
        )
        assert ctx.platform_admin_email == "admin@remaker.digital"

    def test_context_defaults_none(self):
        """Platform admin fields default to None for non-SPA auth."""
        ctx = TenantContext(tenant_id="test-tenant-001")
        assert ctx.platform_admin_id is None
        assert ctx.platform_admin_email is None
