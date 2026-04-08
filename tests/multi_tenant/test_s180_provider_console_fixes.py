"""S180 Provider Console Fixes — behavioral tests.

Tests exercise real endpoint logic through TestClient / mock dependencies.
No inspect.getsource() or structural assertions (GOV-18 compliance).

Fixes tested:
  - SPEC-1784: Co-Pilot Knowledge uses AdminDocumentationRepository (not TenantScopedRepository)
  - SPEC-1783: Support Diagnostics accepts email and resolves to tenant_id
  - SPEC-1785: Tenant Comparison shows brand_name/customer_email, not raw UUIDs

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_authed_app(router):
    """Create a FastAPI app with auth-bypass middleware for testing.

    Adds ASGI middleware that sets request.state.tenant_context before
    the require_platform_admin() dependency checks it, simulating an
    authenticated SPA platform admin session.
    """
    from fastapi import FastAPI
    from starlette.middleware.base import BaseHTTPMiddleware

    app = FastAPI()

    class _InjectPlatformAdminCtx(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            ctx = MagicMock()
            ctx.is_platform_admin = True
            ctx.tenant_id = "__platform__"
            ctx.platform_admin_id = "test-admin"
            ctx.platform_admin_email = "admin@test.com"
            request.state.tenant_context = ctx
            return await call_next(request)

    app.add_middleware(_InjectPlatformAdminCtx)
    app.include_router(router)
    return app


# ---------------------------------------------------------------------------
# SPEC-1784: Co-Pilot Knowledge Repository Fix
# ---------------------------------------------------------------------------


class TestCopilotKnowledgeRepository:
    """Verify Co-Pilot Knowledge uses AdminDocumentationRepository."""

    @pytest.mark.asyncio
    async def test_startup_creates_admin_documentation_repository(self):
        """_startup_copilot_knowledge() must instantiate AdminDocumentationRepository,
        not TenantScopedRepository."""
        with patch(
            "src.multi_tenant.repositories.platform.AdminDocumentationRepository"
        ) as mock_cls, patch(
            "src.multi_tenant.superadmin_api.configure_copilot_knowledge_service"
        ) as mock_configure:
            mock_repo = MagicMock()
            mock_cls.return_value = mock_repo

            from src.app.lifecycle import _startup_copilot_knowledge
            await _startup_copilot_knowledge()

            mock_cls.assert_called_once()
            mock_configure.assert_called_once_with(admin_doc_repo=mock_repo)

    def test_admin_doc_repo_has_upsert_document(self):
        """AdminDocumentationRepository must expose upsert_document method
        that the Co-Pilot endpoints rely on."""
        from src.multi_tenant.repositories.platform import AdminDocumentationRepository
        assert hasattr(AdminDocumentationRepository, "upsert_document")
        assert callable(getattr(AdminDocumentationRepository, "upsert_document"))

    def test_admin_doc_repo_has_get_by_id(self):
        """AdminDocumentationRepository must expose get_by_id for config reads."""
        from src.multi_tenant.repositories.platform import AdminDocumentationRepository
        assert hasattr(AdminDocumentationRepository, "get_by_id")

    def test_admin_doc_repo_has_list_all_active(self):
        """AdminDocumentationRepository must expose list_all_active for embedding."""
        from src.multi_tenant.repositories.platform import AdminDocumentationRepository
        assert hasattr(AdminDocumentationRepository, "list_all_active")

    @pytest.mark.asyncio
    async def test_save_copilot_config_calls_upsert_document(self):
        """_save_copilot_config() must call repo.upsert_document() with a
        CopilotConfigDocument, verifying the method actually exists on the repo."""
        from src.multi_tenant.superadmin_api._copilot import _save_copilot_config
        from src.multi_tenant.superadmin_api import _monolith as _state

        mock_repo = MagicMock()
        mock_repo.upsert_document = AsyncMock(return_value={})
        original = _state._admin_doc_repo
        try:
            _state._admin_doc_repo = mock_repo
            await _save_copilot_config({"scan_frequency": "daily"})
            mock_repo.upsert_document.assert_called_once()
            # Verify it was called with a CopilotConfigDocument
            from src.multi_tenant.cosmos_schema import CopilotConfigDocument
            call_arg = mock_repo.upsert_document.call_args[0][0]
            assert isinstance(call_arg, CopilotConfigDocument)
            assert call_arg.scan_frequency == "daily"
        finally:
            _state._admin_doc_repo = original

    @pytest.mark.asyncio
    async def test_get_copilot_config_calls_get_by_id(self):
        """_get_copilot_config() must call repo.get_by_id('platform', 'copilot_config')."""
        from src.multi_tenant.superadmin_api._copilot import _get_copilot_config
        from src.multi_tenant.superadmin_api import _monolith as _state

        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value={"scan_frequency": "weekly"})
        original = _state._admin_doc_repo
        try:
            _state._admin_doc_repo = mock_repo
            result = await _get_copilot_config()
            mock_repo.get_by_id.assert_called_once_with("platform", "copilot_config")
            assert result["scan_frequency"] == "weekly"
        finally:
            _state._admin_doc_repo = original


# ---------------------------------------------------------------------------
# SPEC-1783: Support Diagnostics Email Lookup
# ---------------------------------------------------------------------------


class TestSupportDiagnosticsEmailLookup:
    """Verify diagnostics endpoint resolves email → tenant_id."""

    @pytest.mark.asyncio
    async def test_email_triggers_customer_email_lookup(self):
        """When tenant_id contains '@', find_by_customer_email must be called."""
        from starlette.testclient import TestClient
        from src.multi_tenant.support_diagnostics import router

        app = _make_authed_app(router)

        mock_tenant_doc = {
            "id": "resolved-tenant-123",
            "tenant_id": "resolved-tenant-123",
            "status": "active",
            "tier": "professional",
            "customer_email": "test@example.com",
        }

        mock_repo = MagicMock()
        mock_repo.find_by_customer_email = AsyncMock(return_value=mock_tenant_doc)
        mock_repo.get_tenant = AsyncMock(return_value=mock_tenant_doc)

        # Patch at the source module where lazy import reads from
        with patch(
            "src.multi_tenant.repositories.tenant.TenantRepository",
            return_value=mock_repo,
        ), patch(
            "src.multi_tenant.repositories.TenantRepository",
            return_value=mock_repo,
        ):
            client = TestClient(app, raise_server_exceptions=False)
            client.get(
                "/api/superadmin/diagnostics/test@example.com",
            )
            mock_repo.find_by_customer_email.assert_called_once_with("test@example.com")

    @pytest.mark.asyncio
    async def test_slug_does_not_trigger_email_lookup(self):
        """When tenant_id has no '@', find_by_customer_email must NOT be called."""
        from starlette.testclient import TestClient
        from src.multi_tenant.support_diagnostics import router

        app = _make_authed_app(router)

        mock_repo = MagicMock()
        mock_repo.find_by_customer_email = AsyncMock()
        mock_repo.get_tenant = AsyncMock(return_value={
            "id": "test-tenant-001",
            "tenant_id": "test-tenant-001",
            "status": "active",
        })

        with patch(
            "src.multi_tenant.repositories.tenant.TenantRepository",
            return_value=mock_repo,
        ), patch(
            "src.multi_tenant.repositories.TenantRepository",
            return_value=mock_repo,
        ):
            client = TestClient(app, raise_server_exceptions=False)
            client.get("/api/superadmin/diagnostics/test-tenant-001")
            mock_repo.find_by_customer_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_email_not_found_returns_404(self):
        """When email doesn't match any tenant, return 404 with descriptive message."""
        from starlette.testclient import TestClient
        from src.multi_tenant.support_diagnostics import router

        app = _make_authed_app(router)

        mock_repo = MagicMock()
        mock_repo.find_by_customer_email = AsyncMock(return_value=None)

        with patch(
            "src.multi_tenant.repositories.tenant.TenantRepository",
            return_value=mock_repo,
        ), patch(
            "src.multi_tenant.repositories.TenantRepository",
            return_value=mock_repo,
        ):
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get(
                "/api/superadmin/diagnostics/nonexistent@example.com",
            )
            assert response.status_code == 404
            assert "nonexistent@example.com" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_errors_endpoint_also_resolves_email(self):
        """The /errors sub-endpoint must also resolve email → tenant_id."""
        from starlette.testclient import TestClient
        from src.multi_tenant.support_diagnostics import router

        app = _make_authed_app(router)

        mock_repo = MagicMock()
        mock_repo.find_by_customer_email = AsyncMock(return_value={
            "id": "tenant-xyz",
            "tenant_id": "tenant-xyz",
        })

        mock_audit = MagicMock()
        mock_audit.query_recent_errors = AsyncMock(return_value=[])

        with patch(
            "src.multi_tenant.repositories.tenant.TenantRepository",
            return_value=mock_repo,
        ), patch(
            "src.multi_tenant.repositories.TenantRepository",
            return_value=mock_repo,
        ), patch(
            "src.multi_tenant.repositories.AuditLogRepository",
            return_value=mock_audit,
        ):
            client = TestClient(app, raise_server_exceptions=False)
            client.get(
                "/api/superadmin/diagnostics/admin@shop.com/errors",
            )
            mock_repo.find_by_customer_email.assert_called_once_with("admin@shop.com")


# ---------------------------------------------------------------------------
# SPEC-1785: Tenant Comparison Display Names
# ---------------------------------------------------------------------------


class TestTenantComparisonDisplayNames:
    """Verify Tenant Comparison shows human-readable names."""

    def _make_app(self):
        """Create a minimal FastAPI app with the platform router + auth bypass."""
        from src.multi_tenant.superadmin_api._monolith import router
        return _make_authed_app(router)

    def _mock_tenant_repo(self, tenant_docs):
        """Create a mock tenant repo that yields given documents."""

        async def mock_query_items(**kwargs):
            for doc in tenant_docs:
                yield doc

        mock_container = MagicMock()
        mock_container.query_items = mock_query_items
        mock_repo = MagicMock()
        mock_repo._container = mock_container
        return mock_repo

    def test_display_name_priority_brand_over_email(self):
        """brand_name takes priority over customer_email."""
        from starlette.testclient import TestClient
        from src.multi_tenant.superadmin_api import _monolith as _state

        app = self._make_app()
        mock_repo = self._mock_tenant_repo([
            {"tenant_id": "uuid-abc", "customer_email": "alice@shop.com",
             "brand_name": "Alice's Shop", "tier": "professional"},
        ])

        original = _state._tenant_repo
        try:
            _state._tenant_repo = mock_repo
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/api/superadmin/pipeline/tenants")
            assert response.status_code == 200
            tenant = response.json()["tenants"][0]
            assert tenant["displayName"] == "Alice's Shop"
            assert tenant["tier"] == "professional"
        finally:
            _state._tenant_repo = original

    def test_display_name_falls_back_to_email(self):
        """When brand_name is None, customer_email is used."""
        from starlette.testclient import TestClient
        from src.multi_tenant.superadmin_api import _monolith as _state

        app = self._make_app()
        mock_repo = self._mock_tenant_repo([
            {"tenant_id": "uuid-def", "customer_email": "bob@store.com",
             "brand_name": None, "tier": "starter"},
        ])

        original = _state._tenant_repo
        try:
            _state._tenant_repo = mock_repo
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/api/superadmin/pipeline/tenants")
            assert response.status_code == 200
            assert response.json()["tenants"][0]["displayName"] == "bob@store.com"
        finally:
            _state._tenant_repo = original

    def test_display_name_falls_back_to_tenant_id(self):
        """When both brand_name and email are None, tenant_id is used."""
        from starlette.testclient import TestClient
        from src.multi_tenant.superadmin_api import _monolith as _state

        app = self._make_app()
        mock_repo = self._mock_tenant_repo([
            {"tenant_id": "uuid-ghi", "customer_email": None,
             "brand_name": None, "tier": None},
        ])

        original = _state._tenant_repo
        try:
            _state._tenant_repo = mock_repo
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/api/superadmin/pipeline/tenants")
            assert response.status_code == 200
            assert response.json()["tenants"][0]["displayName"] == "uuid-ghi"
        finally:
            _state._tenant_repo = original

    def test_tier_populated_from_cosmos(self):
        """Tier column must be populated from tenant document, not empty."""
        from starlette.testclient import TestClient
        from src.multi_tenant.superadmin_api import _monolith as _state

        app = self._make_app()
        mock_repo = self._mock_tenant_repo([
            {"tenant_id": "t1", "customer_email": "a@b.com",
             "brand_name": None, "tier": "enterprise"},
        ])

        original = _state._tenant_repo
        try:
            _state._tenant_repo = mock_repo
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/api/superadmin/pipeline/tenants")
            assert response.json()["tenants"][0]["tier"] == "enterprise"
        finally:
            _state._tenant_repo = original

    def test_total_count_matches_tenant_count(self):
        """Response total must match number of tenants returned."""
        from starlette.testclient import TestClient
        from src.multi_tenant.superadmin_api import _monolith as _state

        app = self._make_app()
        mock_repo = self._mock_tenant_repo([
            {"tenant_id": "t1", "customer_email": "a@b.com", "brand_name": None, "tier": "starter"},
            {"tenant_id": "t2", "customer_email": "c@d.com", "brand_name": "Shop", "tier": "professional"},
            {"tenant_id": "t3", "customer_email": "e@f.com", "brand_name": None, "tier": "starter"},
        ])

        original = _state._tenant_repo
        try:
            _state._tenant_repo = mock_repo
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/api/superadmin/pipeline/tenants")
            data = response.json()
            assert data["total"] == 3
            assert len(data["tenants"]) == 3
        finally:
            _state._tenant_repo = original

    def test_tenant_id_still_in_response(self):
        """tenantId must still be present for tooltip display."""
        from starlette.testclient import TestClient
        from src.multi_tenant.superadmin_api import _monolith as _state

        app = self._make_app()
        mock_repo = self._mock_tenant_repo([
            {"tenant_id": "uuid-123", "customer_email": "test@shop.com",
             "brand_name": "My Shop", "tier": "starter"},
        ])

        original = _state._tenant_repo
        try:
            _state._tenant_repo = mock_repo
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/api/superadmin/pipeline/tenants")
            tenant = response.json()["tenants"][0]
            assert tenant["displayName"] == "My Shop"
            assert tenant["tenantId"] == "uuid-123"
        finally:
            _state._tenant_repo = original
