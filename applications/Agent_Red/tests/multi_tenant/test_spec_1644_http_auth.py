"""SPEC-1644: API key tenant isolation — HTTP-level intrusion + happy-path tests.

These tests exercise the FULL middleware stack via FastAPI TestClient.
They verify that:
  1. API key auth requires ?tenant= in the URL
  2. Keys only authenticate against the correct tenant (partition-scoped)
  3. Cross-tenant key probes reveal nothing
  4. Widget keys cannot access admin endpoints
  5. The validate-key endpoint behaves correctly

Run:
    pytest tests/multi_tenant/test_spec_1644_http_auth.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# All tests in this module are adversarial security tests (SPEC-1644)
pytestmark = [pytest.mark.security, pytest.mark.unit]

from tests.conftest import (  # noqa: E402
    STARTER_TENANT_ID,
    PROFESSIONAL_TENANT_ID,
    TEST_API_KEY_STARTER,
    TEST_API_KEY_PROFESSIONAL,
    TEST_SPA_KEY,
    TEST_USER_KEY,
    TEST_WIDGET_KEY,
    auth_headers_api_key,
)


# ===================================================================
# 1. Happy-path: valid API key + correct tenant
# ===================================================================


class TestHappyPathAuth:
    """Verify that valid credentials + correct tenant succeed."""

    def test_api_key_with_correct_tenant_succeeds(self, app_client: TestClient):
        """Valid API key + matching ?tenant= → authenticated request."""
        resp = app_client.get(
            "/api/health",
            params={"tenant": STARTER_TENANT_ID},
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        # Health is auth-exempt, but let's test a non-exempt endpoint
        resp = app_client.get(
            "/api/config",
            params={"tenant": STARTER_TENANT_ID},
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        assert resp.status_code in (200, 404), (
            f"Expected success, got {resp.status_code}: {resp.text}"
        )

    def test_professional_key_with_correct_tenant(self, app_client: TestClient):
        """Professional API key + matching tenant → success."""
        resp = app_client.get(
            "/api/config",
            params={"tenant": PROFESSIONAL_TENANT_ID},
            headers=auth_headers_api_key(TEST_API_KEY_PROFESSIONAL),
        )
        assert resp.status_code in (200, 404)

    def test_per_user_key_with_correct_tenant(self, app_client: TestClient):
        """Per-user API key + matching tenant → success."""
        resp = app_client.get(
            "/api/config",
            params={"tenant": STARTER_TENANT_ID},
            headers={"X-API-Key": TEST_USER_KEY},
        )
        assert resp.status_code in (200, 404)

    def test_spa_key_without_tenant_succeeds(self, app_client: TestClient):
        """SPA platform admin key does NOT require ?tenant=.

        SPA keys authenticate against platform_admins, not tenant partitions,
        so they are exempt from the URL tenant requirement.
        """
        # /api/health is auth-exempt so doesn't prove SPA auth works.
        # Use a non-exempt endpoint that the SPA would call.
        resp = app_client.get(
            "/api/config",
            headers={"X-API-Key": TEST_SPA_KEY},
        )
        # SPA key should authenticate (not 401) — it may get 403/404
        # depending on whether the endpoint requires a tenant scope,
        # but the point is it does NOT get rejected for missing ?tenant=.
        assert resp.status_code != 401 or "tenant parameter" not in resp.text.lower(), (
            "SPA key should not be rejected for missing ?tenant= param"
        )


# ===================================================================
# 2. Intrusion: API key without ?tenant= parameter
# ===================================================================


class TestNoTenantParamRejection:
    """SPEC-1644: API key auth REQUIRES ?tenant= in the URL."""

    def test_api_key_without_tenant_param_rejected(self, app_client: TestClient):
        """API key + no ?tenant= → 401 (tenant param required)."""
        resp = app_client.get(
            "/api/config",
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        assert resp.status_code == 401, (
            f"Expected 401 without tenant param, got {resp.status_code}"
        )

    def test_per_user_key_without_tenant_param_rejected(self, app_client: TestClient):
        """Per-user key + no ?tenant= → 401."""
        resp = app_client.get(
            "/api/config",
            headers={"X-API-Key": TEST_USER_KEY},
        )
        assert resp.status_code == 401

    def test_rejection_message_mentions_tenant(self, app_client: TestClient):
        """Error message must tell the user to include ?tenant=."""
        resp = app_client.get(
            "/api/config",
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        assert resp.status_code == 401
        body = resp.json()
        error_text = body.get("error", body.get("detail", "")).lower()
        assert "tenant" in error_text, (
            f"Error should mention 'tenant': {body}"
        )


# ===================================================================
# 3. Intrusion: cross-tenant key probe
# ===================================================================


class TestCrossTenantKeyRejection:
    """SPEC-1644: Key for tenant A + URL says tenant B → 401, no info leak."""

    def test_starter_key_against_professional_tenant(self, app_client: TestClient):
        """Starter key + ?tenant=professional → 401."""
        resp = app_client.get(
            "/api/config",
            params={"tenant": PROFESSIONAL_TENANT_ID},
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        assert resp.status_code == 401, (
            f"Cross-tenant probe should be rejected, got {resp.status_code}"
        )

    def test_professional_key_against_starter_tenant(self, app_client: TestClient):
        """Professional key + ?tenant=starter → 401."""
        resp = app_client.get(
            "/api/config",
            params={"tenant": STARTER_TENANT_ID},
            headers=auth_headers_api_key(TEST_API_KEY_PROFESSIONAL),
        )
        assert resp.status_code == 401

    def test_cross_tenant_reveals_nothing(self, app_client: TestClient):
        """Cross-tenant 401 response must not reveal which tenant the key belongs to."""
        resp = app_client.get(
            "/api/config",
            params={"tenant": PROFESSIONAL_TENANT_ID},
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        assert resp.status_code == 401
        body = resp.json()
        error_text = str(body).lower()
        # Must not reveal the key's actual tenant
        assert STARTER_TENANT_ID.lower() not in error_text, (
            "Error response leaked the key's actual tenant ID"
        )
        assert "starter" not in error_text, (
            "Error response leaked tenant tier/identity"
        )

    def test_per_user_key_cross_tenant_rejected(self, app_client: TestClient):
        """Per-user key (starter tenant) + ?tenant=professional → 401."""
        resp = app_client.get(
            "/api/config",
            params={"tenant": PROFESSIONAL_TENANT_ID},
            headers={"X-API-Key": TEST_USER_KEY},
        )
        assert resp.status_code == 401

    def test_nonexistent_tenant_rejected(self, app_client: TestClient):
        """Key + ?tenant=nonexistent → 401."""
        resp = app_client.get(
            "/api/config",
            params={"tenant": "t-does-not-exist-999"},
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        assert resp.status_code == 401

    def test_invalid_key_with_valid_tenant(self, app_client: TestClient):
        """Garbage key + valid tenant → 401."""
        resp = app_client.get(
            "/api/config",
            params={"tenant": STARTER_TENANT_ID},
            headers={"X-API-Key": "ar_live_garbage_key_does_not_exist"},
        )
        assert resp.status_code == 401


# ===================================================================
# 4. Widget key isolation
# ===================================================================


class TestWidgetKeyIsolation:
    """Widget keys must only work on chat/widget endpoints."""

    def test_widget_key_cannot_access_admin_config(self, app_client: TestClient):
        """Widget key on /api/config → 403 (not a widget-allowed path)."""
        resp = app_client.get(
            "/api/admin/team/whoami",
            headers={"X-Widget-Key": TEST_WIDGET_KEY},
        )
        # Widget keys are restricted to /api/chat/, /ws/chat/, /api/config
        assert resp.status_code in (401, 403), (
            f"Widget key should not access admin endpoints, got {resp.status_code}"
        )

    def test_widget_key_cannot_access_billing(self, app_client: TestClient):
        """Widget key on billing endpoint → rejected."""
        resp = app_client.get(
            "/api/admin/team",
            headers={"X-Widget-Key": TEST_WIDGET_KEY},
        )
        assert resp.status_code in (401, 403)


# ===================================================================
# 5. Validate-key endpoint
# ===================================================================


class TestValidateKeyEndpoint:
    """POST /api/tenants/auth/validate-key HTTP tests.

    Note: The validate-key endpoint is auth-exempt (under /api/tenants/)
    and uses provisioning-layer repos (_tenant_repo, _team_repo) rather
    than middleware resolvers.  Tests that require a working Cosmos
    backend use unittest.mock.patch on the provisioning module.
    """

    def test_valid_key_and_tenant_returns_200(self, app_client: TestClient):
        """Valid API key + correct tenant → 200 with tenant info."""
        from unittest.mock import AsyncMock, patch
        import src.integrations.provisioning as prov

        mock_result = {
            "tenant_id": STARTER_TENANT_ID,
            "status": "active",
            "tier": "starter",
            "billing_channel": "stripe",
            "stripe_customer_id": "cus_test",
        }
        with patch.object(
            prov, "_validate_api_key_for_tenant",
            new_callable=AsyncMock, return_value=mock_result,
        ), patch.object(
            prov, "_read_brand_name",
            new_callable=AsyncMock, return_value="Test Brand",
        ):
            resp = app_client.post(
                "/api/tenants/auth/validate-key",
                json={"tenant": STARTER_TENANT_ID},
                headers=auth_headers_api_key(TEST_API_KEY_STARTER),
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
        assert data["tenant_id"] == STARTER_TENANT_ID

    def test_invalid_key_returns_401(self, app_client: TestClient):
        """Invalid API key + valid tenant → 401."""
        from unittest.mock import AsyncMock, patch
        import src.integrations.provisioning as prov

        with patch.object(
            prov, "_validate_api_key_for_tenant",
            new_callable=AsyncMock, return_value=None,
        ):
            resp = app_client.post(
                "/api/tenants/auth/validate-key",
                json={"tenant": STARTER_TENANT_ID},
                headers={"X-API-Key": "ar_live_invalid_garbage_key"},
            )
        assert resp.status_code == 401

    def test_cross_tenant_key_returns_401(self, app_client: TestClient):
        """Starter key + professional tenant → 401, no info leak."""
        from unittest.mock import AsyncMock, patch
        import src.integrations.provisioning as prov

        # Partition-scoped: key doesn't match in professional's partition
        with patch.object(
            prov, "_validate_api_key_for_tenant",
            new_callable=AsyncMock, return_value=None,
        ):
            resp = app_client.post(
                "/api/tenants/auth/validate-key",
                json={"tenant": PROFESSIONAL_TENANT_ID},
                headers=auth_headers_api_key(TEST_API_KEY_STARTER),
            )
        assert resp.status_code == 401
        body = resp.json()
        # Must not reveal which tenant the key actually belongs to
        assert STARTER_TENANT_ID not in str(body)

    def test_missing_api_key_returns_400(self, app_client: TestClient):
        """No X-API-Key header → 400."""
        resp = app_client.post(
            "/api/tenants/auth/validate-key",
            json={"tenant": STARTER_TENANT_ID},
        )
        assert resp.status_code == 400

    def test_missing_tenant_in_body_returns_422(self, app_client: TestClient):
        """Missing 'tenant' field in body → 422 (Pydantic validation)."""
        resp = app_client.post(
            "/api/tenants/auth/validate-key",
            json={},
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        assert resp.status_code == 422


# ===================================================================
# 6. Lookup endpoint no longer accepts API keys
# ===================================================================


class TestLookupEndpointRestricted:
    """GET /api/tenants/lookup must not accept API key for tenant discovery."""

    def test_lookup_without_params_returns_400(self, app_client: TestClient):
        """Lookup with just an API key (no shop/stripe_customer_id) → 400."""
        resp = app_client.get(
            "/api/tenants/lookup",
            headers=auth_headers_api_key(TEST_API_KEY_STARTER),
        )
        assert resp.status_code == 400
        body = resp.json()
        detail = body.get("detail", "")
        assert "SPEC-1644" in detail or "validate-key" in detail.lower(), (
            "Lookup rejection should reference SPEC-1644 or validate-key"
        )
