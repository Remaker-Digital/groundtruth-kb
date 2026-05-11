"""Mutation tests — Admin API Key Management endpoints.

Tests: metadata, generate, rotate, revoke, reset (public).

Exercises GET/POST/DELETE on /api/admin/api-keys through the full middleware
stack using the ``apikey_repos`` fixture from ``tests/multi_tenant/conftest.py``.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch


from tests.conftest import STARTER_TENANT_ID
from tests.multi_tenant.conftest import MutationTestBase
from src.multi_tenant.security_hardening import get_rate_limit_backend


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE = "/api/admin/api-keys"


def _tenant_doc_with_key() -> dict:
    """Tenant document that already has an API key."""
    return {
        "id": STARTER_TENANT_ID,
        "tenant_id": STARTER_TENANT_ID,
        "api_key_hash": "existing_hash_abc123",
        "api_key_prefix": "ar_live_t-sta",
        "api_key_created_at": "2026-01-15T10:00:00Z",
        "api_key_last_rotated_at": None,
        "status": "active",
        "tier": "starter",
    }


def _tenant_doc_without_key() -> dict:
    """Tenant document with no API key set."""
    return {
        "id": STARTER_TENANT_ID,
        "tenant_id": STARTER_TENANT_ID,
        "api_key_hash": None,
        "api_key_prefix": None,
        "api_key_created_at": None,
        "api_key_last_rotated_at": None,
        "status": "active",
        "tier": "starter",
    }


# ---------------------------------------------------------------------------
# GET /api/admin/api-keys — metadata
# ---------------------------------------------------------------------------


class TestApiKeyMetadata(MutationTestBase):
    """GET /api/admin/api-keys — auth guards + happy path."""

    def test_requires_auth(self, app_client, apikey_repos):
        self.assert_requires_auth(app_client, "get", BASE)

    def test_rejects_widget_key(self, widget_client, apikey_repos):
        self.assert_rejects_widget_key(widget_client, "get", BASE)

    def test_returns_metadata_with_key(self, starter_client, apikey_repos):
        apikey_repos["tenant_repo"].read = AsyncMock(
            return_value=_tenant_doc_with_key(),
        )
        resp = starter_client.get(BASE)
        assert resp.status_code == 200
        data = resp.json()
        assert data["hasKey"] is True
        assert data["keyPrefix"] == "ar_live_t-sta"
        assert data["createdAt"] == "2026-01-15T10:00:00Z"
        assert data["lastRotatedAt"] is None

    def test_returns_metadata_without_key(self, starter_client, apikey_repos):
        apikey_repos["tenant_repo"].read = AsyncMock(
            return_value=_tenant_doc_without_key(),
        )
        resp = starter_client.get(BASE)
        assert resp.status_code == 200
        data = resp.json()
        assert data["hasKey"] is False
        assert data["keyPrefix"] is None

    def test_returns_503_when_not_initialized(self, starter_client):
        """Service not wired — should return 503."""
        from src.multi_tenant.admin_apikey_api import configure_apikey_services
        configure_apikey_services(tenant_repo=None)
        try:
            resp = starter_client.get(BASE)
            assert resp.status_code == 503
        finally:
            # Restore — cleanup happens via fixture teardown anyway,
            # but be explicit.
            configure_apikey_services(tenant_repo=None)


# ---------------------------------------------------------------------------
# POST /api/admin/api-keys — generate
# ---------------------------------------------------------------------------


class TestApiKeyGenerate(MutationTestBase):
    """POST /api/admin/api-keys — auth, 409 conflict, happy path."""

    def test_requires_auth(self, app_client, apikey_repos):
        self.assert_requires_auth(app_client, "post", BASE)

    def test_rejects_widget_key(self, widget_client, apikey_repos):
        self.assert_rejects_widget_key(widget_client, "post", BASE)

    def test_409_when_key_already_exists(self, starter_client, apikey_repos):
        apikey_repos["tenant_repo"].read = AsyncMock(
            return_value=_tenant_doc_with_key(),
        )
        resp = starter_client.post(BASE)
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"].lower()

    def test_generates_key_when_none_exists(self, starter_client, apikey_repos):
        apikey_repos["tenant_repo"].read = AsyncMock(
            return_value=_tenant_doc_without_key(),
        )
        apikey_repos["tenant_repo"].patch = AsyncMock(return_value=None)
        resp = starter_client.post(BASE)
        assert resp.status_code == 201
        data = resp.json()
        assert data["apiKey"].startswith("ar_live_")
        assert len(data["keyPrefix"]) == 12
        assert "createdAt" in data
        # Verify patch was called to persist the hash
        apikey_repos["tenant_repo"].patch.assert_awaited_once()

    def test_404_when_tenant_not_found(self, starter_client, apikey_repos):
        apikey_repos["tenant_repo"].read = AsyncMock(return_value=None)
        resp = starter_client.post(BASE)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/admin/api-keys/rotate
# ---------------------------------------------------------------------------


class TestApiKeyRotate(MutationTestBase):
    """POST /api/admin/api-keys/rotate — auth, no-key-404, happy path."""

    ROTATE_URL = f"{BASE}/rotate"

    def test_requires_auth(self, app_client, apikey_repos):
        self.assert_requires_auth(app_client, "post", self.ROTATE_URL)

    def test_rejects_widget_key(self, widget_client, apikey_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.ROTATE_URL)

    def test_rotates_existing_key(self, starter_client, apikey_repos):
        apikey_repos["tenant_repo"].read = AsyncMock(
            return_value=_tenant_doc_with_key(),
        )
        apikey_repos["tenant_repo"].patch = AsyncMock(return_value=None)
        resp = starter_client.post(self.ROTATE_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["apiKey"].startswith("ar_live_")
        assert "rotated" in data["message"].lower()
        # Verify patch included last_rotated_at
        call_kwargs = apikey_repos["tenant_repo"].patch.call_args
        ops = call_kwargs.kwargs.get("operations", call_kwargs[1].get("operations", []))
        paths = [op["path"] for op in ops]
        assert "/api_key_last_rotated_at" in paths


# ---------------------------------------------------------------------------
# DELETE /api/admin/api-keys — revoke
# ---------------------------------------------------------------------------


class TestApiKeyRevoke(MutationTestBase):
    """DELETE /api/admin/api-keys — auth, happy path."""

    def test_requires_auth(self, app_client, apikey_repos):
        self.assert_requires_auth(app_client, "delete", BASE)

    def test_rejects_widget_key(self, widget_client, apikey_repos):
        self.assert_rejects_widget_key(widget_client, "delete", BASE)

    def test_revokes_existing_key(self, starter_client, apikey_repos):
        apikey_repos["tenant_repo"].read = AsyncMock(
            return_value=_tenant_doc_with_key(),
        )
        apikey_repos["tenant_repo"].patch = AsyncMock(return_value=None)
        resp = starter_client.delete(BASE)
        assert resp.status_code == 200
        data = resp.json()
        assert data["revoked"] is True
        assert "revokedAt" in data

    def test_404_when_no_key_to_revoke(self, starter_client, apikey_repos):
        apikey_repos["tenant_repo"].read = AsyncMock(
            return_value=_tenant_doc_without_key(),
        )
        resp = starter_client.delete(BASE)
        assert resp.status_code == 404
        assert "no api key" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# POST /api/admin/api-keys/reset — public endpoint
# ---------------------------------------------------------------------------


class TestApiKeyReset(MutationTestBase):
    """POST /api/admin/api-keys/reset — public, rate limit, enumeration prevention."""

    RESET_URL = f"{BASE}/reset"

    def setup_method(self):
        """Clear rate limiter state before each test."""
        get_rate_limit_backend()._windows.clear()

    @patch("src.multi_tenant.admin_apikey_api._send_api_key_email", new_callable=AsyncMock)
    @patch("src.multi_tenant.admin_apikey_api._tenant_repo")
    def test_returns_200_with_generic_message_for_known_email(
        self, mock_repo, mock_send_email, app_client, apikey_repos,
    ):
        mock_repo.find_by_customer_email = AsyncMock(return_value={
            "id": "tenant-abc",
            "tenant_id": "tenant-abc",
            "api_key_hash": "old_hash",
            "status": "active",
            "customer_email": "merchant@example.com",
        })
        mock_repo.patch = AsyncMock(return_value=None)
        mock_send_email.return_value = True

        resp = app_client.post(self.RESET_URL, json={"email": "merchant@example.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert "if an account" in data["message"].lower()
        mock_send_email.assert_awaited_once()

    @patch("src.multi_tenant.admin_apikey_api._send_api_key_email", new_callable=AsyncMock)
    @patch("src.multi_tenant.admin_apikey_api._tenant_repo")
    def test_returns_200_for_unknown_email(
        self, mock_repo, mock_send_email, app_client, apikey_repos,
    ):
        """Enumeration prevention: unknown emails get the same 200 response."""
        mock_repo.find_by_customer_email = AsyncMock(return_value=None)

        resp = app_client.post(self.RESET_URL, json={"email": "nobody@example.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert "if an account" in data["message"].lower()
        mock_send_email.assert_not_awaited()

    @patch("src.multi_tenant.admin_apikey_api._tenant_repo")
    def test_rate_limits_after_3_requests(self, mock_repo, app_client, apikey_repos):
        mock_repo.find_by_customer_email = AsyncMock(return_value=None)

        for _ in range(3):
            resp = app_client.post(self.RESET_URL, json={"email": "test@example.com"})
            assert resp.status_code == 200

        resp = app_client.post(self.RESET_URL, json={"email": "test@example.com"})
        assert resp.status_code == 429
        assert "too many" in resp.json()["detail"].lower()

    @patch("src.multi_tenant.admin_apikey_api._tenant_repo")
    def test_invalid_email_format_returns_200(self, mock_repo, app_client, apikey_repos):
        """Invalid email format still returns generic 200 — no info leak."""
        resp = app_client.post(self.RESET_URL, json={"email": "not-an-email"})
        assert resp.status_code == 200
        data = resp.json()
        assert "if an account" in data["message"].lower()

    def test_returns_503_when_not_initialized(self, app_client):
        from src.multi_tenant.admin_apikey_api import configure_apikey_services
        configure_apikey_services(tenant_repo=None)
        try:
            resp = app_client.post(self.RESET_URL, json={"email": "x@y.com"})
            assert resp.status_code == 503
        finally:
            configure_apikey_services(tenant_repo=None)
