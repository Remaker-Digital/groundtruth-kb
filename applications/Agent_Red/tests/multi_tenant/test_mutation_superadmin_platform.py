"""Mutation tests — Superadmin Platform Admin Management endpoints.

Tests: operator CRUD, backup codes, key regeneration, service messages.
All endpoints require SPA platform admin authentication (SPEC-1667).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch


from src.multi_tenant.middleware import configure_tenant_resolution
from tests.conftest import (
    TEST_SPA_KEY_HASH,
    _build_tenant_lookup_table,
)
from tests.multi_tenant.conftest import MutationTestBase


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# The SPA admin ID assigned by the root conftest (TEST_SPA_ADMIN_DOC).
SPA_ADMIN_ID = "spa-admin-001"


class FakeAsyncIterator:
    """Simulate async iteration over Cosmos query results."""

    def __init__(self, items: list[Any]):
        self._items = items
        self._index = 0

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._index]
        self._index += 1
        return item


OPERATOR_DOC = {
    "id": "op-001",
    "admin_id": "op-001",
    "email": "operator@example.com",
    "display_name": "Test Operator",
    "role": "operator",
    "is_active": True,
    "created_at": "2026-01-01T00:00:00+00:00",
    "created_by": SPA_ADMIN_ID,
}

SUPERADMIN_DOC = {
    "id": "superadmin-002",
    "admin_id": "superadmin-002",
    "email": "admin2@platform.com",
    "display_name": "Super Admin 2",
    "role": "superadmin",
    "is_active": True,
}

TENANT_ITEMS = [
    {
        "tenant_id": "t-001",
        "customer_email": "owner1@shop.com",
        "tier": "starter",
        "status": "active",
    },
    {
        "tenant_id": "t-002",
        "customer_email": "owner2@shop.com",
        "tier": "professional",
        "status": "active",
    },
]


def _swap_spa_admin_role(role: str):
    """Reconfigure tenant resolution so the SPA key resolves to the given role.

    The root conftest wires TEST_SPA_ADMIN_DOC with role='superadmin'.
    This helper temporarily rebuilds the resolver lookup table using a
    modified admin document. Callers must restore original resolvers after.
    """
    operator_admin_doc = {
        "id": SPA_ADMIN_ID,
        "admin_id": SPA_ADMIN_ID,
        "email": "admin@platform.test",
        "api_key_hash": TEST_SPA_KEY_HASH,
        "is_active": True,
        "role": role,
        "notification_email_address": "admin@platform.test",
        "partition_key": "__platform__",
    }

    resolvers = _build_tenant_lookup_table()

    # Override only the SPA resolver
    async def resolve_by_spa_key_hash(key_hash: str) -> dict[str, Any] | None:
        if key_hash == TEST_SPA_KEY_HASH:
            return operator_admin_doc
        return None

    configure_tenant_resolution(
        resolve_by_shop_domain=resolvers["resolve_by_shop_domain"],
        resolve_by_api_key_hash=resolvers["resolve_by_api_key_hash"],
        resolve_by_spa_key_hash=AsyncMock(side_effect=resolve_by_spa_key_hash),
        resolve_by_widget_key_hash=resolvers["resolve_by_widget_key_hash"],
        resolve_by_user_api_key_hash=resolvers["resolve_by_user_api_key_hash"],
    )


def _restore_spa_admin_role():
    """Restore default resolvers (superadmin role)."""
    resolvers = _build_tenant_lookup_table()
    configure_tenant_resolution(
        resolve_by_shop_domain=resolvers["resolve_by_shop_domain"],
        resolve_by_api_key_hash=resolvers["resolve_by_api_key_hash"],
        resolve_by_spa_key_hash=resolvers["resolve_by_spa_key_hash"],
        resolve_by_widget_key_hash=resolvers["resolve_by_widget_key_hash"],
        resolve_by_user_api_key_hash=resolvers["resolve_by_user_api_key_hash"],
    )


# ---------------------------------------------------------------------------
# TestCreateOperator
# ---------------------------------------------------------------------------


class TestCreateOperator(MutationTestBase):
    """POST /api/superadmin/platform-admin/users (201)"""

    URL = "/api/superadmin/platform-admin/users"
    VALID_BODY = {"email": "newop@example.com", "display_name": "New Op"}

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.VALID_BODY)

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.VALID_BODY)

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.VALID_BODY)

    @patch("src.multi_tenant.auth.generate_spa_api_key", return_value="ar_spa_test_key")
    def test_happy_path(self, mock_gen, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].find_by_email = AsyncMock(return_value=None)
        superadmin_repos["platform_admin_repo"].create_admin = AsyncMock(return_value=None)

        resp = spa_client.post(self.URL, json=self.VALID_BODY)
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "newop@example.com"
        assert body["displayName"] == "New Op"
        assert body["role"] == "operator"
        assert body["apiKey"] == "ar_spa_test_key"
        assert "adminId" in body

    def test_duplicate_email_returns_409(self, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].find_by_email = AsyncMock(
            return_value=OPERATOR_DOC
        )

        resp = spa_client.post(self.URL, json=self.VALID_BODY)
        assert resp.status_code == 409

    def test_operator_role_cannot_create(self, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].find_by_email = AsyncMock(return_value=None)

        try:
            _swap_spa_admin_role("operator")
            resp = spa_client.post(self.URL, json=self.VALID_BODY)
            assert resp.status_code == 403
        finally:
            _restore_spa_admin_role()

    def test_missing_fields_returns_422(self, spa_client, superadmin_repos):
        self.assert_validation_error(spa_client, "post", self.URL, json={"email": "x@y.com"})


# ---------------------------------------------------------------------------
# TestDeactivateOperator
# ---------------------------------------------------------------------------


class TestDeactivateOperator(MutationTestBase):
    """DELETE /api/superadmin/platform-admin/users/{admin_id}"""

    URL = "/api/superadmin/platform-admin/users/op-001"

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "delete", self.URL)

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "delete", self.URL)

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "delete", self.URL)

    def test_happy_path(self, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].find_by_admin_id = AsyncMock(
            return_value=dict(OPERATOR_DOC)
        )
        superadmin_repos["platform_admin_repo"].deactivate_admin = AsyncMock(return_value=None)

        resp = spa_client.delete(self.URL)
        assert resp.status_code == 200
        body = resp.json()
        assert "deactivated" in body["message"].lower()

    def test_not_found_returns_404(self, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].find_by_admin_id = AsyncMock(return_value=None)

        resp = spa_client.delete(self.URL)
        assert resp.status_code == 404

    def test_cannot_deactivate_self(self, spa_client, superadmin_repos):
        """URL admin_id matches ctx.platform_admin_id (spa-admin-001) -> 400."""
        resp = spa_client.delete(f"/api/superadmin/platform-admin/users/{SPA_ADMIN_ID}")
        assert resp.status_code == 400

    def test_cannot_deactivate_superadmin_account(self, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].find_by_admin_id = AsyncMock(
            return_value=dict(SUPERADMIN_DOC)
        )

        resp = spa_client.delete("/api/superadmin/platform-admin/users/superadmin-002")
        assert resp.status_code == 403

    def test_operator_role_cannot_deactivate(self, spa_client, superadmin_repos):
        try:
            _swap_spa_admin_role("operator")
            resp = spa_client.delete(self.URL)
            assert resp.status_code == 403
        finally:
            _restore_spa_admin_role()


# ---------------------------------------------------------------------------
# TestUpdateNotificationEmail
# ---------------------------------------------------------------------------


class TestUpdateNotificationEmail(MutationTestBase):
    """PUT /api/superadmin/platform-admin/users/notification-email"""

    URL = "/api/superadmin/platform-admin/users/notification-email"

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "put", self.URL, json={"email": "x@y.com"})

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "put", self.URL, json={"email": "x@y.com"})

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "put", self.URL, json={"email": "x@y.com"})

    def test_set_notification_email(self, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].update_notification_email = AsyncMock(
            return_value=None
        )

        resp = spa_client.put(self.URL, json={"email": "alerts@platform.com"})
        assert resp.status_code == 200
        body = resp.json()
        assert "set" in body["message"].lower()

    def test_clear_notification_email(self, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].update_notification_email = AsyncMock(
            return_value=None
        )

        resp = spa_client.put(self.URL, json={"email": None})
        assert resp.status_code == 200
        body = resp.json()
        assert "cleared" in body["message"].lower()


# ---------------------------------------------------------------------------
# TestGenerateBackupCodes
# ---------------------------------------------------------------------------


class TestGenerateBackupCodes(MutationTestBase):
    """POST /api/superadmin/platform-admin/users/backup-codes"""

    URL = "/api/superadmin/platform-admin/users/backup-codes"

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "post", self.URL)

    def test_returns_eight_codes(self, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].update_backup_code_hashes = AsyncMock(
            return_value=None
        )

        resp = spa_client.post(self.URL)
        assert resp.status_code == 200
        body = resp.json()
        assert body["count"] == 8
        assert len(body["codes"]) == 8
        # Each code should be a hex string (8 chars from token_hex(4))
        for code in body["codes"]:
            assert len(code) == 8
            assert all(c in "0123456789abcdef" for c in code)

    def test_replaces_existing_codes(self, spa_client, superadmin_repos):
        mock_update = AsyncMock(return_value=None)
        superadmin_repos["platform_admin_repo"].update_backup_code_hashes = mock_update

        spa_client.post(self.URL)
        mock_update.assert_awaited_once()
        call_kwargs = mock_update.call_args
        # Verify 8 hashes were stored
        assert len(call_kwargs.kwargs.get("hashes", call_kwargs[1].get("hashes", []))) == 8


# ---------------------------------------------------------------------------
# TestRegenerateKey
# ---------------------------------------------------------------------------


class TestRegenerateKey(MutationTestBase):
    """POST /api/superadmin/platform-admin/regenerate-key"""

    URL = "/api/superadmin/platform-admin/regenerate-key"

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "post", self.URL)

    @patch("src.multi_tenant.auth.generate_spa_api_key", return_value="ar_spa_new_key_12345")
    def test_happy_path(self, mock_gen, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].update_api_key_hash = AsyncMock(
            return_value=None
        )

        resp = spa_client.post(self.URL)
        assert resp.status_code == 200
        body = resp.json()
        assert body["newApiKey"] == "ar_spa_new_key_12345"
        assert body["adminId"] == SPA_ADMIN_ID
        assert "email" in body
        assert "regeneratedAt" in body

    def test_repo_failure_returns_500(self, spa_client, superadmin_repos):
        superadmin_repos["platform_admin_repo"].update_api_key_hash = AsyncMock(
            side_effect=Exception("Cosmos write failed")
        )

        resp = spa_client.post(self.URL)
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# TestServiceMessagePreview
# ---------------------------------------------------------------------------


class TestServiceMessagePreview(MutationTestBase):
    """POST /api/superadmin/service-messages/preview"""

    URL = "/api/superadmin/service-messages/preview"

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "post", self.URL)

    def test_returns_recipients(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"]._container = MagicMock()
        superadmin_repos["tenant_repo"]._container.query_items = MagicMock(
            return_value=FakeAsyncIterator(TENANT_ITEMS)
        )

        resp = spa_client.post(self.URL)
        assert resp.status_code == 200
        body = resp.json()
        assert body["totalCount"] == 2
        assert len(body["recipients"]) == 2
        emails = [r["email"] for r in body["recipients"]]
        assert "owner1@shop.com" in emails

    def test_with_status_filter(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"]._container = MagicMock()
        superadmin_repos["tenant_repo"]._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([TENANT_ITEMS[0]])
        )

        resp = spa_client.post(self.URL + "?filter_status=active")
        assert resp.status_code == 200
        body = resp.json()
        assert body["totalCount"] == 1


# ---------------------------------------------------------------------------
# TestServiceMessageSend
# ---------------------------------------------------------------------------


class TestServiceMessageSend(MutationTestBase):
    """POST /api/superadmin/service-messages/send"""

    URL = "/api/superadmin/service-messages/send"
    VALID_BODY = {
        "subject": "Maintenance Notice",
        "body": "<p>Scheduled downtime at 2am UTC.</p>",
    }

    def test_requires_auth(self, app_client):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.VALID_BODY)

    def test_rejects_widget_key(self, widget_client):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.VALID_BODY)

    def test_spa_isolation(self, starter_client):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.VALID_BODY)

    @patch("src.multi_tenant.service_message_delivery.send_service_message", new_callable=AsyncMock)
    @patch("src.multi_tenant.service_message_delivery.render_service_message_body", return_value="<html>rendered</html>")
    def test_happy_path(self, mock_render, mock_send, spa_client, superadmin_repos):
        # Wire up tenant query to return recipients
        superadmin_repos["tenant_repo"]._container = MagicMock()
        superadmin_repos["tenant_repo"]._container.query_items = MagicMock(
            return_value=FakeAsyncIterator(TENANT_ITEMS)
        )

        mock_send.return_value = MagicMock(
            total_recipients=2,
            sent_count=2,
            failed_count=0,
            errors=[],
            success=True,
        )

        resp = spa_client.post(self.URL, json=self.VALID_BODY)
        assert resp.status_code == 200
        body = resp.json()
        assert body["totalRecipients"] == 2
        assert body["sentCount"] == 2
        assert body["success"] is True
        mock_render.assert_called_once()
        mock_send.assert_awaited_once()

    def test_no_recipients_returns_422(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"]._container = MagicMock()
        superadmin_repos["tenant_repo"]._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )

        resp = spa_client.post(self.URL, json=self.VALID_BODY)
        assert resp.status_code == 422

    def test_missing_subject_returns_422(self, spa_client, superadmin_repos):
        self.assert_validation_error(
            spa_client, "post", self.URL, json={"body": "<p>content</p>"}
        )

    def test_missing_body_returns_422(self, spa_client, superadmin_repos):
        self.assert_validation_error(
            spa_client, "post", self.URL, json={"subject": "Test"}
        )
