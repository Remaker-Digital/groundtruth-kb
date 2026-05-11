"""Mutation tests — Superadmin Tenant Management endpoints.

Tests: tier override, tenant creation, welcome email resend, access expiry.
All endpoints require SPA platform admin authentication (SPEC-1667).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from unittest.mock import AsyncMock, patch


from tests.multi_tenant.conftest import MutationTestBase


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TENANT_ID = "test-tenant-mutation-001"

TENANT_DOC = {
    "id": TENANT_ID,
    "tenant_id": TENANT_ID,
    "tier": "starter",
    "status": "active",
    "billing_channel": "stripe",
    "customer_email": "tenant@example.com",
    "created_at": "2026-01-01T00:00:00+00:00",
    "updated_at": "2026-01-01T00:00:00+00:00",
    "expires_at": None,
}


@dataclass
class FakeProvisionResult:
    """Mimics SpaProvisionResult for mock returns."""

    tenant_id: str = "new-tenant-001"
    status: str = "active"
    tier: str = "starter"
    superadmin_email: str = "admin@newshop.com"
    superadmin_api_key: str | None = "ar_test_key"
    widget_key: str | None = "pk_live_test_widget"
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# TestTierOverride
# ---------------------------------------------------------------------------


class TestTierOverride(MutationTestBase):
    """PUT /api/superadmin/tenants/{tenant_id}/tier"""

    URL = f"/api/superadmin/tenants/{TENANT_ID}/tier"

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "put", self.URL, json={"tier": "professional"})

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "put", self.URL, json={"tier": "professional"})

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "put", self.URL, json={"tier": "professional"})

    def test_happy_path(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"].read = AsyncMock(return_value=dict(TENANT_DOC))
        superadmin_repos["tenant_repo"].patch = AsyncMock(return_value=None)

        resp = spa_client.put(self.URL, json={"tier": "professional"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["tenantId"] == TENANT_ID
        assert body["previousTier"] == "starter"
        assert body["newTier"] == "professional"
        assert "updatedAt" in body

    def test_invalid_tier_returns_400(self, spa_client, superadmin_repos):
        resp = spa_client.put(self.URL, json={"tier": "platinum"})
        assert resp.status_code == 400

    def test_tenant_not_found_returns_404(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"].read = AsyncMock(side_effect=Exception("NotFound"))

        resp = spa_client.put(self.URL, json={"tier": "professional"})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# TestCreateTenant
# ---------------------------------------------------------------------------


class TestCreateTenant(MutationTestBase):
    """POST /api/superadmin/tenants"""

    URL = "/api/superadmin/tenants"
    VALID_BODY = {
        "merchant_name": "New Shop",
        "superadmin_email": "admin@newshop.com",
        "tier": "starter",
    }

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.VALID_BODY)

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.VALID_BODY)

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.VALID_BODY)

    @patch("src.integrations.provisioning.spa_provision_tenant", new_callable=AsyncMock)
    def test_happy_path(self, mock_provision, spa_client, superadmin_repos):
        mock_provision.return_value = FakeProvisionResult()

        resp = spa_client.post(self.URL, json=self.VALID_BODY)
        assert resp.status_code == 201
        body = resp.json()
        assert body["tenantId"] == "new-tenant-001"
        assert body["status"] == "active"
        assert body["tier"] == "starter"
        assert body["superadminEmail"] == "admin@newshop.com"
        assert body["keysDeliveredViaEmail"] is True

    def test_invalid_tier_returns_400(self, spa_client, superadmin_repos):
        body = {**self.VALID_BODY, "tier": "platinum"}
        resp = spa_client.post(self.URL, json=body)
        assert resp.status_code == 400

    def test_invalid_email_returns_422(self, spa_client, superadmin_repos):
        body = {**self.VALID_BODY, "superadmin_email": "not-an-email"}
        self.assert_validation_error(spa_client, "post", self.URL, json=body)

    def test_missing_required_fields_returns_422(self, spa_client, superadmin_repos):
        self.assert_validation_error(spa_client, "post", self.URL, json={"tier": "starter"})


# ---------------------------------------------------------------------------
# TestResendWelcomeEmail
# ---------------------------------------------------------------------------


class TestResendWelcomeEmail(MutationTestBase):
    """POST /api/superadmin/tenants/{tenant_id}/resend-welcome-email"""

    URL = f"/api/superadmin/tenants/{TENANT_ID}/resend-welcome-email"

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "post", self.URL)

    @patch("src.multi_tenant.welcome_email.send_welcome_email", new_callable=AsyncMock)
    def test_happy_path(self, mock_send, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"].read = AsyncMock(return_value=dict(TENANT_DOC))
        superadmin_repos["prefs_repo"].get_active = AsyncMock(return_value=None)
        mock_send.return_value = True

        resp = spa_client.post(self.URL)
        assert resp.status_code == 200
        body = resp.json()
        assert body["tenantId"] == TENANT_ID
        assert body["sentTo"] == "tenant@example.com"
        assert body["sent"] is True

    def test_tenant_not_found_returns_404(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"].read = AsyncMock(return_value=None)

        resp = spa_client.post(self.URL)
        assert resp.status_code == 404

    def test_no_email_returns_422(self, spa_client, superadmin_repos):
        doc_no_email = {**TENANT_DOC, "customer_email": None}
        superadmin_repos["tenant_repo"].read = AsyncMock(return_value=doc_no_email)
        superadmin_repos["prefs_repo"].get_active = AsyncMock(return_value=None)

        resp = spa_client.post(self.URL)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# TestSetExpiry
# ---------------------------------------------------------------------------


class TestSetExpiry(MutationTestBase):
    """PATCH /api/superadmin/tenants/{tenant_id}/expiry"""

    URL = f"/api/superadmin/tenants/{TENANT_ID}/expiry"
    VALID_BODY = {"expires_at": "2027-06-01T00:00:00+00:00"}

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "patch", self.URL, json=self.VALID_BODY)

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "patch", self.URL, json=self.VALID_BODY)

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "patch", self.URL, json=self.VALID_BODY)

    def test_happy_path_set_expiry(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"].read = AsyncMock(return_value=dict(TENANT_DOC))
        superadmin_repos["tenant_repo"].patch = AsyncMock(return_value=None)

        resp = spa_client.patch(self.URL, json=self.VALID_BODY)
        assert resp.status_code == 200
        body = resp.json()
        assert body["tenantId"] == TENANT_ID
        assert body["previousExpiresAt"] is None
        assert body["newExpiresAt"] == "2027-06-01T00:00:00+00:00"
        assert "updatedAt" in body

    def test_clear_expiry_with_null(self, spa_client, superadmin_repos):
        doc_with_expiry = {**TENANT_DOC, "expires_at": "2027-01-01T00:00:00+00:00"}
        superadmin_repos["tenant_repo"].read = AsyncMock(return_value=doc_with_expiry)
        superadmin_repos["tenant_repo"].patch = AsyncMock(return_value=None)

        resp = spa_client.patch(self.URL, json={"expires_at": None})
        assert resp.status_code == 200
        body = resp.json()
        assert body["previousExpiresAt"] == "2027-01-01T00:00:00+00:00"
        assert body["newExpiresAt"] is None

    def test_tenant_not_found_returns_404(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"].read = AsyncMock(return_value=None)

        resp = spa_client.patch(self.URL, json=self.VALID_BODY)
        assert resp.status_code == 404

    def test_invalid_iso_format_returns_422(self, spa_client, superadmin_repos):
        self.assert_validation_error(
            spa_client, "patch", self.URL, json={"expires_at": "not-a-date"}
        )
