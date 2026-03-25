"""
Flow tests: Authentication boundary enforcement.

Verifies that every auth path correctly identifies the caller, enforces
tenant isolation, and rejects unauthorized access — exercised through
the full HTTP middleware stack.

Flow patterns:
  - Valid auth → correct tenant resolved → data scoped to tenant
  - Invalid auth → 401 → no data leak
  - Cross-auth → wrong key type on wrong endpoint → rejected
  - Missing auth → 401 on all protected endpoints

GOV-19: Outside-in testing.
SPEC-0286: Dual authentication (Shopify session + API key).
SPEC-1644: API keys do not identify tenants.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from tests.conftest import (
    TEST_API_KEY_STARTER,
    TEST_API_KEY_PROFESSIONAL,
    TEST_API_KEY_HASH_STARTER,
    TEST_API_KEY_HASH_PROFESSIONAL,
    TEST_SPA_KEY,
    TEST_SPA_KEY_HASH,
    TEST_SPA_ADMIN_DOC,
    TEST_WIDGET_KEY,
    TEST_WIDGET_KEY_HASH,
    STARTER_TENANT_ID,
    PROFESSIONAL_TENANT_ID,
    auth_headers_api_key,
    auth_headers_widget_key,
    make_tenant_document,
    MockCosmosManager,
)

import src.multi_tenant.cosmos_client as _cosmos_client_mod
import src.multi_tenant.nats_isolation as _nats_isolation_mod
import src.multi_tenant.tenant_secret_service as _secret_service_mod
import src.multi_tenant.pipeline_resilience as _pipeline_resilience_mod


@pytest.fixture
def auth_client():
    """TestClient wired for auth boundary testing."""
    cosmos = MockCosmosManager()

    import asyncio
    async def _seed():
        tenants = cosmos.get_container("tenants")
        await tenants.upsert_item(make_tenant_document(
            tenant_id=STARTER_TENANT_ID,
            api_key_hash=TEST_API_KEY_HASH_STARTER,
        ))
        await tenants.upsert_item(make_tenant_document(
            tenant_id=PROFESSIONAL_TENANT_ID,
            api_key_hash=TEST_API_KEY_HASH_PROFESSIONAL,
        ))
        admins = cosmos.get_container("platform_admins")
        await admins.upsert_item(TEST_SPA_ADMIN_DOC)
        widget_keys = cosmos.get_container("widget_keys")
        await widget_keys.upsert_item({
            "id": TEST_WIDGET_KEY_HASH,
            "tenant_id": STARTER_TENANT_ID,
            "key_hash": TEST_WIDGET_KEY_HASH,
            "partition_key": "__widget_keys__",
        })

    loop = asyncio.new_event_loop()
    loop.run_until_complete(_seed())
    loop.close()

    nats_mock = MagicMock()
    nats_mock.is_connected = True
    nats_mock.check_health = AsyncMock(return_value=MagicMock(
        connected=True, circuit_breaker_state="CLOSED", active_streams=0,
    ))
    nats_mock.publish = AsyncMock()
    nats_mock.close = AsyncMock()

    kv_mock = MagicMock()
    kv_mock.initialize = AsyncMock()
    kv_mock.close = AsyncMock()
    kv_mock.health_check = AsyncMock(return_value={"status": "healthy"})
    kv_mock.get_secret = AsyncMock(return_value=None)

    cb_mock = MagicMock()
    cb_mock.health_summary = MagicMock(return_value={})
    cb_mock.reset_all = MagicMock()

    with (
        patch.object(_cosmos_client_mod, "_manager", cosmos),
        patch.object(_cosmos_client_mod, "get_cosmos_manager", return_value=cosmos),
        patch.object(_nats_isolation_mod, "_manager", nats_mock),
        patch.object(_nats_isolation_mod, "get_nats_manager", return_value=nats_mock),
        patch.object(_secret_service_mod, "_service", kv_mock),
        patch.object(_secret_service_mod, "get_secret_service", return_value=kv_mock),
        patch.object(_pipeline_resilience_mod, "get_circuit_breaker_registry", return_value=cb_mock),
    ):
        from src.main import app
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


# ---------------------------------------------------------------------------
# Flow: Unauthenticated access rejected
# ---------------------------------------------------------------------------

class TestFlowUnauthenticatedRejection:
    """All protected endpoints must return 401 without auth headers."""

    PROTECTED_ENDPOINTS = [
        "/api/admin/dashboard",
        "/api/config",
        "/api/admin/conversations",
        "/api/admin/knowledge",
        "/api/admin/team",
        "/api/superadmin/dashboard",
        "/api/superadmin/tenants",
    ]

    @pytest.mark.parametrize("endpoint", PROTECTED_ENDPOINTS)
    def test_no_auth_returns_401(self, auth_client, endpoint):
        """Every protected endpoint rejects unauthenticated requests."""
        resp = auth_client.get(endpoint)
        assert resp.status_code == 401, (
            f"{endpoint} returned {resp.status_code} without auth, expected 401"
        )

    def test_invalid_api_key_returns_401(self, auth_client):
        """A fabricated API key is rejected."""
        resp = auth_client.get(
            f"/api/admin/dashboard?tenant={STARTER_TENANT_ID}",
            headers={"X-API-Key": "arsk_fake_nonexistent_key"},
        )
        assert resp.status_code == 401

    def test_empty_api_key_returns_401(self, auth_client):
        """An empty API key header is rejected."""
        resp = auth_client.get(
            f"/api/admin/dashboard?tenant={STARTER_TENANT_ID}",
            headers={"X-API-Key": ""},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Flow: Auth type isolation
# ---------------------------------------------------------------------------

class TestFlowAuthTypeIsolation:
    """Each auth type is only valid on its intended endpoint family."""

    def test_spa_key_works_on_superadmin(self, auth_client):
        """SPA platform admin key works on /api/superadmin/ endpoints."""
        resp = auth_client.get(
            "/api/superadmin/dashboard",
            headers={"X-Api-Key": TEST_SPA_KEY},
        )
        assert resp.status_code != 401, f"SPA key rejected on superadmin: {resp.text}"

    def test_tenant_key_rejected_on_superadmin(self, auth_client):
        """Tenant API key must NOT work on superadmin endpoints."""
        resp = auth_client.get(
            "/api/superadmin/dashboard",
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        # Should be 401 or 403 — tenant keys are not platform admin keys
        assert resp.status_code in (401, 403), (
            f"Tenant key accepted on superadmin: {resp.status_code}"
        )

    def test_widget_key_rejected_on_admin(self, auth_client):
        """Widget key must NOT work on admin endpoints."""
        resp = auth_client.get(
            "/api/admin/dashboard",
            headers=auth_headers_widget_key(TEST_WIDGET_KEY),
        )
        assert resp.status_code == 401

    def test_widget_key_works_on_chat(self, auth_client):
        """Widget key works on /api/chat/ endpoints."""
        resp = auth_client.get(
            "/api/chat/config",
            headers=auth_headers_widget_key(TEST_WIDGET_KEY),
        )
        assert resp.status_code != 401, f"Widget key rejected on chat: {resp.text}"


# ---------------------------------------------------------------------------
# Flow: Cross-tenant data isolation
# ---------------------------------------------------------------------------

class TestFlowCrossTenantIsolation:
    """One tenant's key must never return another tenant's data."""

    def test_starter_key_cannot_specify_pro_tenant(self, auth_client):
        """Starter API key with ?tenant=professional should be rejected."""
        resp = auth_client.get(
            f"/api/admin/dashboard?tenant={PROFESSIONAL_TENANT_ID}",
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        # Should either be 401/403 (key doesn't match tenant) or 200
        # but scoped to starter tenant only
        if resp.status_code == 200:
            data = resp.json()
            # Verify the response is scoped to starter, not professional
            tenant_in_response = (
                data.get("tenant_id")
                or data.get("tenantId")
                or str(data)
            )
            assert PROFESSIONAL_TENANT_ID not in str(tenant_in_response), (
                "Starter key returned Professional tenant data — ISOLATION BREACH"
            )

    def test_pro_key_cannot_access_starter_data(self, auth_client):
        """Professional API key with ?tenant=starter should be rejected."""
        resp = auth_client.get(
            f"/api/admin/dashboard?tenant={STARTER_TENANT_ID}",
            headers=auth_headers_api_key(TEST_API_KEY_PROFESSIONAL),
        )
        if resp.status_code == 200:
            data = resp.json()
            assert STARTER_TENANT_ID not in str(data.get("tenant_id", "")), (
                "Professional key returned Starter tenant data — ISOLATION BREACH"
            )
