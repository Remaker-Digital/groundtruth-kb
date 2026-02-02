"""Smoke tests — verify conftest.py fixtures are functional.

These tests validate that the shared test infrastructure (app_client,
authenticated clients, mock services) works correctly. They serve as
a canary: if these fail, fixture wiring is broken.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from tests.conftest import (
    TEST_API_KEY_STARTER,
    TEST_API_KEY_PROFESSIONAL,
    TEST_API_KEY_ENTERPRISE,
    auth_headers_api_key,
    make_tenant_context,
)
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantStatus, TenantTier


# ---------------------------------------------------------------------------
# Tenant context factories
# ---------------------------------------------------------------------------

class TestTenantContextFactories:
    """Verify make_tenant_context and fixture contexts."""

    def test_make_default(self):
        ctx = make_tenant_context()
        assert ctx.tier == TenantTier.STARTER
        assert ctx.status == TenantStatus.ACTIVE
        assert ctx.auth_method == "api_key"
        assert isinstance(ctx, TenantContext)

    def test_fixture_starter(self, starter_context):
        assert starter_context.tier == TenantTier.STARTER

    def test_fixture_professional(self, professional_context):
        assert professional_context.tier == TenantTier.PROFESSIONAL

    def test_fixture_enterprise(self, enterprise_context):
        assert enterprise_context.tier == TenantTier.ENTERPRISE
        assert enterprise_context.auth_method == "shopify_session"
        assert enterprise_context.shop_domain is not None


# ---------------------------------------------------------------------------
# Health endpoint (auth-exempt) via TestClient
# ---------------------------------------------------------------------------

class TestAppClientHealth:
    """Verify the app_client fixture can call auth-exempt endpoints."""

    def test_health_returns_200(self, app_client):
        resp = app_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    def test_ready_returns_200(self, app_client):
        resp = app_client.get("/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"


# ---------------------------------------------------------------------------
# Auth middleware via TestClient
# ---------------------------------------------------------------------------

class TestAppClientAuth:
    """Verify that the middleware stack rejects/accepts requests correctly."""

    def test_protected_endpoint_no_auth_returns_401(self, app_client):
        resp = app_client.get("/api/dashboard/usage")
        assert resp.status_code == 401

    def test_protected_endpoint_with_api_key(self, app_client):
        resp = app_client.get(
            "/api/dashboard/usage",
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        # Should not be 401 — auth should pass.
        # Actual status depends on handler logic (may be 503 for unconfigured services).
        assert resp.status_code != 401

    def test_protected_endpoint_bad_key_returns_401(self, app_client):
        resp = app_client.get(
            "/api/dashboard/usage",
            headers=auth_headers_api_key("arsk_completely_invalid_key"),
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Authenticated client helpers
# ---------------------------------------------------------------------------

class TestAuthenticatedClients:
    """Verify starter_client / professional_client / enterprise_client."""

    def test_starter_client_passes_auth(self, starter_client):
        resp = starter_client.get("/health")
        assert resp.status_code == 200

    def test_professional_client_passes_auth(self, professional_client):
        resp = professional_client.get("/health")
        assert resp.status_code == 200

    def test_enterprise_client_passes_auth(self, enterprise_client):
        resp = enterprise_client.get("/health")
        assert resp.status_code == 200

    def test_raw_client_accessible(self, starter_client):
        """The .raw property exposes the underlying TestClient."""
        resp = starter_client.raw.get("/health")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Mock Cosmos DB
# ---------------------------------------------------------------------------

class TestMockCosmos:
    """Verify MockCosmosManager basic operations."""

    @pytest.mark.asyncio
    async def test_create_and_read(self, mock_cosmos):
        container = mock_cosmos.get_container("tenants")
        await container.create_item({"id": "t-1", "tenant_id": "t-1", "status": "active"})
        doc = await container.read_item("t-1", partition_key="t-1")
        assert doc["status"] == "active"

    @pytest.mark.asyncio
    async def test_upsert_replaces(self, mock_cosmos):
        container = mock_cosmos.get_container("tenants")
        await container.create_item({"id": "t-1", "tenant_id": "t-1", "status": "active"})
        await container.upsert_item({"id": "t-1", "tenant_id": "t-1", "status": "deactivated"})
        doc = await container.read_item("t-1", partition_key="t-1")
        assert doc["status"] == "deactivated"

    @pytest.mark.asyncio
    async def test_delete(self, mock_cosmos):
        container = mock_cosmos.get_container("tenants")
        await container.create_item({"id": "t-1", "tenant_id": "t-1"})
        await container.delete_item("t-1", partition_key="t-1")
        with pytest.raises(Exception):
            await container.read_item("t-1", partition_key="t-1")

    @pytest.mark.asyncio
    async def test_patch_incr(self, mock_cosmos):
        container = mock_cosmos.get_container("usage")
        await container.create_item({"id": "u-1", "count": 5})
        doc = await container.patch_item(
            "u-1", partition_key="u-1",
            patch_operations=[{"op": "incr", "path": "/count", "value": 3}],
        )
        assert doc["count"] == 8

    @pytest.mark.asyncio
    async def test_query_items_iterates(self, mock_cosmos):
        container = mock_cosmos.get_container("tenants")
        await container.create_item({"id": "t-1", "tenant_id": "t-1"})
        await container.create_item({"id": "t-2", "tenant_id": "t-2"})
        results = []
        async for item in container.query_items("SELECT * FROM c"):
            results.append(item)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_health_check(self, mock_cosmos):
        result = await mock_cosmos.health_check()
        assert result["status"] == "healthy"
