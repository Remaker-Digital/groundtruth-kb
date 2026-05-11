"""Tests for Admin GDPR API endpoint specifications.

Covers:
    - Router prefix verification
    - export_data handler (tenant scope)
    - delete_data handler (customer scope)
    - get_consent_status handler (reads from tenant_repo)
    - update_consent handler (delegates to consent_manager)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_gdpr_api import (
    configure_admin_gdpr_services,
    router,
    ExportRequest,
    DeleteRequest,
    UpdateConsentRequest,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _ctx(**overrides):
    ctx = MagicMock()
    ctx.tenant_id = overrides.get("tenant_id", "test-tenant-001")
    ctx.tier = overrides.get("tier", "professional")
    ctx.user_id = overrides.get("user_id", "user-001")
    ctx.team_member_email = overrides.get("team_member_email", "admin@test.com")
    ctx.team_member_role = overrides.get("team_member_role", None)
    ctx.team_member_id = overrides.get("team_member_id", "member-001")
    ctx.auth_method = overrides.get("auth_method", "tenant_api_key")
    return ctx


# ---------------------------------------------------------------------------
# GDPR-01: Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """Verify the GDPR router is mounted at /api/gdpr."""

    def test_router_prefix_is_api_gdpr(self):
        assert router.prefix == "/api/gdpr"


# ---------------------------------------------------------------------------
# GDPR-02: export_data
# ---------------------------------------------------------------------------


class TestExportData:
    """POST /api/gdpr/export delegates to export_service."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        self.export_service = MagicMock()
        self.deletion_service = MagicMock()
        self.consent_manager = MagicMock()
        self.tenant_repo = AsyncMock()
        configure_admin_gdpr_services(
            self.export_service,
            self.deletion_service,
            self.consent_manager,
            self.tenant_repo,
        )
        yield
        configure_admin_gdpr_services(None, None, None, None)

    @pytest.mark.asyncio
    async def test_export_tenant_scope(self):
        """export_data with scope=tenant calls export_service.export_tenant."""
        from src.multi_tenant.admin_gdpr_api import export_data

        result_obj = MagicMock()
        result_obj.export_id = "exp-001"
        result_obj.tenant_id = "test-tenant-001"
        result_obj.customer_id = None
        result_obj.export_type = "tenant"
        result_obj.stores_exported = ["conversations", "profiles"]
        result_obj.data = {"conversations": [], "profiles": []}
        result_obj.exported_at = "2026-02-20T12:00:00Z"
        result_obj.errors = []

        self.export_service.export_tenant = AsyncMock(return_value=result_obj)

        request = ExportRequest(scope="tenant")
        ctx = _ctx()
        response = await export_data(request, ctx=ctx)

        self.export_service.export_tenant.assert_called_once_with("test-tenant-001")
        assert response.export_id == "exp-001"
        assert response.tenant_id == "test-tenant-001"
        assert response.export_type == "tenant"
        assert len(response.stores_exported) == 2


# ---------------------------------------------------------------------------
# GDPR-03: delete_data
# ---------------------------------------------------------------------------


class TestDeleteData:
    """POST /api/gdpr/delete delegates to deletion_service."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        self.export_service = MagicMock()
        self.deletion_service = MagicMock()
        self.consent_manager = MagicMock()
        self.tenant_repo = AsyncMock()
        configure_admin_gdpr_services(
            self.export_service,
            self.deletion_service,
            self.consent_manager,
            self.tenant_repo,
        )
        yield
        configure_admin_gdpr_services(None, None, None, None)

    @pytest.mark.asyncio
    async def test_delete_customer_scope(self):
        """delete_data with scope=customer calls deletion_service.delete_customer."""
        from src.multi_tenant.admin_gdpr_api import delete_data

        result_obj = MagicMock()
        result_obj.deletion_id = "del-001"
        result_obj.tenant_id = "test-tenant-001"
        result_obj.customer_id = "cust-abc"
        result_obj.deletion_type = "customer"
        result_obj.stores_deleted = ["profiles"]
        result_obj.details = {"profiles": {"deleted": 1}}
        result_obj.deleted_at = "2026-02-20T12:00:00Z"
        result_obj.errors = []

        self.deletion_service.delete_customer = AsyncMock(return_value=result_obj)

        request = DeleteRequest(scope="customer", customer_id="cust-abc")
        ctx = _ctx()
        response = await delete_data(request, ctx=ctx)

        self.deletion_service.delete_customer.assert_called_once_with(
            "test-tenant-001", "cust-abc",
        )
        assert response.deletion_id == "del-001"
        assert response.customer_id == "cust-abc"
        assert response.deletion_type == "customer"


# ---------------------------------------------------------------------------
# GDPR-04: get_consent_status
# ---------------------------------------------------------------------------


class TestGetConsentStatus:
    """GET /api/gdpr/consent reads consent_status from tenant document."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        self.export_service = MagicMock()
        self.deletion_service = MagicMock()
        self.consent_manager = MagicMock()
        self.tenant_repo = AsyncMock()
        configure_admin_gdpr_services(
            self.export_service,
            self.deletion_service,
            self.consent_manager,
            self.tenant_repo,
        )
        yield
        configure_admin_gdpr_services(None, None, None, None)

    @pytest.mark.asyncio
    async def test_consent_status_from_tenant_doc(self):
        """get_consent_status reads consent_status from the tenant document."""
        from src.multi_tenant.admin_gdpr_api import get_consent_status

        self.tenant_repo.read = AsyncMock(return_value={
            "tenant_id": "test-tenant-001",
            "consent_status": "granted",
        })

        ctx = _ctx()
        response = await get_consent_status(ctx=ctx)

        self.tenant_repo.read.assert_called_once_with(
            "test-tenant-001", "test-tenant-001",
        )
        assert response.tenant_id == "test-tenant-001"
        assert response.consent_status == "granted"


# ---------------------------------------------------------------------------
# GDPR-05: update_consent
# ---------------------------------------------------------------------------


class TestUpdateConsent:
    """PUT /api/gdpr/consent delegates to consent_manager."""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        self.export_service = MagicMock()
        self.deletion_service = MagicMock()
        self.consent_manager = MagicMock()
        self.tenant_repo = AsyncMock()
        configure_admin_gdpr_services(
            self.export_service,
            self.deletion_service,
            self.consent_manager,
            self.tenant_repo,
        )
        yield
        configure_admin_gdpr_services(None, None, None, None)

    @pytest.mark.asyncio
    async def test_update_consent_granted(self):
        """update_consent delegates to consent_manager.update_tenant_consent."""
        from src.multi_tenant.admin_gdpr_api import update_consent

        self.consent_manager.update_tenant_consent = AsyncMock(return_value={
            "previous_status": "not_asked",
            "new_status": "granted",
        })

        # Patch ConsentStatus at the import location in admin_gdpr_api
        mock_consent_status = MagicMock()
        mock_consent_status.return_value = "granted"

        with patch("src.multi_tenant.cosmos_schema.ConsentStatus", mock_consent_status):
            request = UpdateConsentRequest(consent_status="granted")
            ctx = _ctx()
            response = await update_consent(request, ctx=ctx)

        self.consent_manager.update_tenant_consent.assert_called_once()
        call_kwargs = self.consent_manager.update_tenant_consent.call_args.kwargs
        assert call_kwargs["tenant_id"] == "test-tenant-001"
        assert response.previous_status == "not_asked"
        assert response.new_status == "granted"
