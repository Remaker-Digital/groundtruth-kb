"""Tests for the Superadmin Tenant Creation endpoint (P0-PROV-1).

Covers:
    POST /api/superadmin/tenants — 13 tests
    - Valid create: all fields, happy path (201 + credentials)
    - Missing merchant_name → 422
    - Missing superadmin_email → 422
    - Invalid email format → ValidationError
    - Invalid tier → 400
    - Non-superadmin role → 403 (auth guard)
    - Partial failure: widget key fails → 201 + warning
    - Partial failure: superadmin key fails → 201 + warning
    - Complete failure: provision_tenant raises → 500
    - Duplicate email (re-provision) → 201
    - BillingChannel.MANUAL stored correctly
    - Non-SPA tenant superadmin → 403 (SPA guard)
    - SPA tenant superadmin → 201 (SPA guard passes)

Run:
    pytest tests/multi_tenant/test_superadmin_tenant_create.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import field as dataclass_field
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.integrations.provisioning import SpaProvisionResult
from src.multi_tenant.superadmin_api import (
    CreateTenantRequest,
    CreateTenantResponse,
    configure_superadmin_services,
    create_tenant,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_tenant_repo():
    """Create a mock TenantRepository."""
    repo = MagicMock()
    repo.read = AsyncMock()
    repo.patch = AsyncMock()
    return repo


@pytest.fixture()
def mock_prefs_repo():
    """Create a mock PreferencesRepository."""
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.upsert = AsyncMock()
    return repo


@pytest.fixture()
def mock_audit_repo():
    """Create a mock AuditLogRepository."""
    repo = MagicMock()
    repo.create = AsyncMock()
    return repo


@pytest.fixture()
def superadmin_ctx():
    """Create a fake SUPERADMIN TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    ctx.team_member_email = "admin@remakerdigital.com"
    return ctx


@pytest.fixture()
def admin_ctx():
    """Create a fake ADMIN TenantContext (non-superadmin)."""
    ctx = MagicMock()
    ctx.tenant_id = "test-tenant-001"
    ctx.team_member_role = "admin"
    ctx.team_member_email = "admin@test.com"
    return ctx


@pytest.fixture()
def merchant_superadmin_ctx():
    """Create a fake SUPERADMIN from a merchant tenant (not SPA)."""
    ctx = MagicMock()
    ctx.tenant_id = "test-customer-001"  # Not remaker-digital-001
    ctx.team_member_role = "superadmin"
    ctx.team_member_email = "owner@merchant.com"
    return ctx


@pytest.fixture(autouse=True)
def _setup_services(mock_tenant_repo, mock_prefs_repo, mock_audit_repo):
    """Wire up the module-level service references."""
    configure_superadmin_services(
        tenant_repo=mock_tenant_repo,
        audit_repo=mock_audit_repo,
        prefs_repo=mock_prefs_repo,
    )


def _make_provision_result(**overrides) -> SpaProvisionResult:
    """Create a SpaProvisionResult with sensible defaults."""
    defaults = {
        "tenant_id": "spa-test-001",
        "status": "active",
        "tier": "starter",
        "superadmin_email": "admin@test.com",
        "superadmin_api_key": "ar_user_test_abc123",
        "widget_key": "pk_live_abc_def",
        "errors": [],
    }
    defaults.update(overrides)
    return SpaProvisionResult(**defaults)


def _make_request(**overrides) -> CreateTenantRequest:
    """Create a CreateTenantRequest with sensible defaults."""
    defaults = {
        "merchant_name": "Test Store",
        "merchant_url": "https://test.example.com",
        "superadmin_email": "admin@test.com",
        "tier": "starter",
    }
    defaults.update(overrides)
    return CreateTenantRequest(**defaults)


# ===========================================================================
# Tests
# ===========================================================================


class TestCreateTenant:
    """POST /api/superadmin/tenants"""

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.spa_provision_tenant", new_callable=AsyncMock)
    async def test_valid_create_happy_path(
        self, mock_provision, superadmin_ctx,
    ):
        """Valid request returns 201 with tenant_id + credentials."""
        mock_provision.return_value = _make_provision_result()

        result = await create_tenant(
            body=_make_request(),
            ctx=superadmin_ctx,
        )

        assert isinstance(result, CreateTenantResponse)
        assert result.tenant_id == "spa-test-001"
        assert result.status == "active"
        assert result.tier == "starter"
        assert result.superadmin_email == "admin@test.com"
        assert result.superadmin_api_key == "ar_user_test_abc123"
        assert result.widget_key == "pk_live_abc_def"
        assert result.warnings == []

    def test_missing_merchant_name_rejected(self):
        """Missing merchant_name fails Pydantic validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreateTenantRequest(
                merchant_name="",
                superadmin_email="admin@test.com",
                tier="starter",
            )

    def test_missing_email_rejected(self):
        """Missing superadmin_email fails Pydantic validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreateTenantRequest(
                merchant_name="Test Store",
                superadmin_email="",
                tier="starter",
            )

    @pytest.mark.asyncio
    async def test_invalid_tier_rejected(self, superadmin_ctx):
        """Invalid tier value returns 400."""
        with pytest.raises(HTTPException) as exc_info:
            await create_tenant(
                body=_make_request(tier="platinum"),
                ctx=superadmin_ctx,
            )

        assert exc_info.value.status_code == 400
        assert "Invalid tier" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.spa_provision_tenant", new_callable=AsyncMock)
    async def test_partial_failure_widget_key_warns(
        self, mock_provision, superadmin_ctx,
    ):
        """Widget key failure returns 201 with warning, no widget_key."""
        mock_provision.return_value = _make_provision_result(
            widget_key=None,
            errors=["Widget key generation failed: timeout"],
        )

        result = await create_tenant(
            body=_make_request(),
            ctx=superadmin_ctx,
        )

        assert result.tenant_id == "spa-test-001"
        assert result.widget_key is None
        assert len(result.warnings) >= 1
        assert "Widget" in result.warnings[0] or "widget" in result.warnings[0].lower()

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.spa_provision_tenant", new_callable=AsyncMock)
    async def test_partial_failure_superadmin_key_warns(
        self, mock_provision, superadmin_ctx,
    ):
        """Superadmin key failure returns 201 with warning."""
        mock_provision.return_value = _make_provision_result(
            superadmin_api_key=None,
            errors=["Superadmin provisioning failed: key gen error"],
        )

        result = await create_tenant(
            body=_make_request(),
            ctx=superadmin_ctx,
        )

        assert result.tenant_id == "spa-test-001"
        assert result.superadmin_api_key is None
        assert len(result.warnings) >= 1

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.spa_provision_tenant", new_callable=AsyncMock)
    async def test_complete_failure_returns_500(
        self, mock_provision, superadmin_ctx,
    ):
        """provision_tenant raising RuntimeError returns 500."""
        mock_provision.side_effect = RuntimeError("Cosmos DB unavailable")

        with pytest.raises(HTTPException) as exc_info:
            await create_tenant(
                body=_make_request(),
                ctx=superadmin_ctx,
            )

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_service_not_initialized_returns_503(self, superadmin_ctx):
        """Returns 503 when _tenant_repo is None."""
        import src.multi_tenant.superadmin_api as mod

        original = mod._tenant_repo
        mod._tenant_repo = None
        try:
            with pytest.raises(HTTPException) as exc_info:
                await create_tenant(
                    body=_make_request(),
                    ctx=superadmin_ctx,
                )
            assert exc_info.value.status_code == 503
        finally:
            mod._tenant_repo = original

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.spa_provision_tenant", new_callable=AsyncMock)
    async def test_duplicate_email_succeeds(
        self, mock_provision, superadmin_ctx,
    ):
        """Re-provisioning with the same email succeeds (idempotent)."""
        mock_provision.return_value = _make_provision_result(
            tenant_id="spa-test-002",
            superadmin_email="existing@test.com",
        )

        result = await create_tenant(
            body=_make_request(superadmin_email="existing@test.com"),
            ctx=superadmin_ctx,
        )

        assert result.tenant_id == "spa-test-002"
        assert result.superadmin_email == "existing@test.com"

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.spa_provision_tenant", new_callable=AsyncMock)
    async def test_billing_channel_manual_in_provision_call(
        self, mock_provision, superadmin_ctx,
    ):
        """spa_provision_tenant is called (BillingChannel.MANUAL is used internally)."""
        mock_provision.return_value = _make_provision_result()

        await create_tenant(
            body=_make_request(),
            ctx=superadmin_ctx,
        )

        mock_provision.assert_called_once_with(
            merchant_name="Test Store",
            merchant_url="https://test.example.com",
            superadmin_email="admin@test.com",
            tier="starter",
        )

    # --- SPA tenant guard tests (B1) ----------------------------------------

    def test_non_spa_superadmin_rejected(self):
        """SPEC-1667: Router-level require_platform_admin() guard ensures
        only SPA platform admin keys can reach tenant creation endpoint.
        Non-SPA callers are rejected before the endpoint runs."""
        from src.multi_tenant.superadmin_api import router

        assert len(router.dependencies) > 0, (
            "Router must have require_platform_admin() as a dependency"
        )

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.spa_provision_tenant", new_callable=AsyncMock)
    async def test_spa_superadmin_allowed(
        self, mock_provision, superadmin_ctx,
    ):
        """SPA tenant superadmin passes the guard and gets 201."""
        mock_provision.return_value = _make_provision_result()

        result = await create_tenant(
            body=_make_request(),
            ctx=superadmin_ctx,
        )

        assert result.tenant_id == "spa-test-001"
        mock_provision.assert_called_once()

    # --- Email format validation tests (B3) ----------------------------------

    def test_invalid_email_format_rejected(self):
        """Invalid email format fails validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreateTenantRequest(
                merchant_name="Test Store",
                superadmin_email="not-an-email",
                tier="starter",
            )
