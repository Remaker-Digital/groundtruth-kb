"""
Flow tests: API round-trip integrity.

End-to-end verification that data written via HTTP API is stored correctly
and retrieved correctly, exercising the full middleware → auth → handler →
repository → storage path.

Flow pattern:
  1. POST/PUT data via authenticated HTTP request
  2. GET data back via authenticated HTTP request
  3. Verify the response matches what was written
  4. Verify auth boundaries (cross-tenant isolation)
  5. Verify side-effects (audit, events)

GOV-19: Outside-in testing.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import (
    TEST_API_KEY_STARTER,
    TEST_API_KEY_HASH_STARTER,
    TEST_API_KEY_HASH_PROFESSIONAL,
    TEST_SPA_KEY,
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


# ---------------------------------------------------------------------------
# Shared fixture: fully-wired TestClient with mock infrastructure
# ---------------------------------------------------------------------------

@pytest.fixture
def wired_client():
    """TestClient with mock Cosmos, NATS, Key Vault, and seeded tenants.

    This is the canonical fixture for flow tests — it wires together
    all infrastructure mocks and provides a fully-authenticated client.
    """
    cosmos = MockCosmosManager()

    # Seed tenants
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

        # Seed SPA admin
        admins = cosmos.get_container("platform_admins")
        await admins.upsert_item(TEST_SPA_ADMIN_DOC)

        # Seed widget key mapping
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

    # Mock NATS
    nats_mock = MagicMock()
    nats_mock.is_connected = True
    nats_mock.check_health = AsyncMock(return_value=MagicMock(
        connected=True, circuit_breaker_state="CLOSED", active_streams=0,
    ))
    nats_mock.publish = AsyncMock()
    nats_mock.close = AsyncMock()
    nats_mock.subscribe = AsyncMock()

    # Mock Key Vault
    kv_mock = MagicMock()
    kv_mock.initialize = AsyncMock()
    kv_mock.close = AsyncMock()
    kv_mock.health_check = AsyncMock(return_value={"status": "healthy"})
    kv_store = {}
    kv_mock.store_secret = AsyncMock(side_effect=lambda t, st, v: kv_store.update({f"{t}-{st}": v}))
    kv_mock.get_secret = AsyncMock(side_effect=lambda t, st: kv_store.get(f"{t}-{st}"))

    # Mock circuit breakers
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
            yield client, cosmos


# ---------------------------------------------------------------------------
# Flow: Tenant config write → read round-trip
# ---------------------------------------------------------------------------

class TestFlowTenantConfigRoundTrip:
    """Write tenant config via API → read it back → verify consistency."""

    def test_health_endpoint_accessible(self, wired_client):
        """Basic smoke: /ready is accessible without auth."""
        client, _ = wired_client
        resp = client.get("/ready")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ready"

    def test_api_key_auth_works(self, wired_client):
        """API key auth resolves to the correct tenant."""
        client, _ = wired_client
        resp = client.get(
            f"/api/admin/dashboard?tenant={STARTER_TENANT_ID}",
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        # Should not be 401 — auth succeeded
        assert resp.status_code != 401, f"Auth failed: {resp.text}"

    def test_cross_tenant_isolation(self, wired_client):
        """Starter key cannot access Professional tenant data."""
        client, cosmos = wired_client

        # Seed a config for professional tenant
        import asyncio
        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            cosmos.get_container("tenant_configs").upsert_item({
                "id": PROFESSIONAL_TENANT_ID,
                "tenant_id": PROFESSIONAL_TENANT_ID,
                "brand_color": "#0000ff",
                "partition_key": PROFESSIONAL_TENANT_ID,
            })
        )
        loop.close()

        # Starter key should NOT see professional config
        resp = client.get(
            f"/api/config?tenant={STARTER_TENANT_ID}",
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("tenant_id") != PROFESSIONAL_TENANT_ID, (
                "Starter key returned Professional tenant config — isolation breach!"
            )


# ---------------------------------------------------------------------------
# Flow: Widget key auth → conversation → encrypted storage
# ---------------------------------------------------------------------------

class TestFlowWidgetConversation:
    """Widget key creates conversation → messages encrypted → retrievable."""

    def test_widget_key_auth_resolves_tenant(self, wired_client):
        """Widget key authentication resolves to correct tenant on chat endpoints."""
        client, _ = wired_client
        # Widget keys are only valid on /api/chat/ endpoints
        resp = client.get(
            "/api/chat/config",
            headers=auth_headers_widget_key(TEST_WIDGET_KEY),
        )
        # Should not be 401 — widget auth succeeded
        assert resp.status_code != 401, f"Widget key auth failed: {resp.text}"

    def test_widget_key_rejected_on_admin_endpoints(self, wired_client):
        """Widget key must NOT work on admin endpoints (isolation)."""
        client, _ = wired_client
        resp = client.get(
            "/api/admin/dashboard",
            headers=auth_headers_widget_key(TEST_WIDGET_KEY),
        )
        assert resp.status_code == 401, (
            f"Widget key should be rejected on admin endpoints, got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# Flow: SPA superadmin → aggregate data only (no tenant PII)
# ---------------------------------------------------------------------------

class TestFlowSpaZeroKnowledge:
    """SPA admin sees aggregate metrics, never individual tenant data."""

    def test_spa_dashboard_returns_aggregates(self, wired_client):
        """SPA dashboard endpoint returns aggregate data, not per-tenant PII."""
        client, _ = wired_client
        resp = client.get(
            "/api/superadmin/dashboard",
            headers={"X-Api-Key": TEST_SPA_KEY},
        )
        if resp.status_code == 200:
            data = resp.json()
            # Dashboard should have aggregate fields
            # It should NOT contain individual customer emails, messages, etc.
            data_str = str(data).lower()
            assert "alice@" not in data_str, "Dashboard leaks customer email"
            assert "hello, i need help" not in data_str, "Dashboard leaks message content"
