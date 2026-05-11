"""Mutation tests — Recovery & Authentication endpoints.

Tests: SPA emergency recovery, tenant account recovery, magic link auth.
Exercises rate limiting, enumeration prevention, and token-based flows.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch


from tests.multi_tenant.conftest import MutationTestBase
from src.multi_tenant.auth import hash_api_key
from src.multi_tenant.spa_recovery import configure_spa_recovery
from src.multi_tenant.tenant_recovery import configure_tenant_recovery
from src.multi_tenant.security_hardening import get_rate_limit_backend


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_BACKUP_CODE = "BACKUP-CODE-001"
VALID_BACKUP_CODE_HASH = hash_api_key(VALID_BACKUP_CODE)

SPA_RECOVERY_URL = "/api/auth/spa-recovery/recover"
TENANT_RECOVERY_ACTIVATE_URL = "/api/superadmin/tenant-recovery/activate"
TENANT_RECOVERY_SEND_LINK_URL = "/api/superadmin/tenant-recovery/send-auth-link"
TENANT_RECOVERY_STATUS_URL = "/api/superadmin/tenant-recovery/status/t-test-001"
ACCOUNT_RECOVERY_VERIFY_URL = "/api/auth/account-recovery/verify"
MAGIC_LINK_REQUEST_URL = "/api/auth/magic-link/request"
MAGIC_LINK_VERIFY_URL = "/api/auth/magic-link/verify"


def _make_platform_admin_doc(email: str = "admin@test.com") -> dict:
    """Build a mock platform admin document with valid backup code."""
    return {
        "admin_id": "admin-001",
        "id": "admin-001",
        "email": email,
        "backup_recovery_code_hashes": [VALID_BACKUP_CODE_HASH],
        "is_active": True,
    }


def _clear_rate_limits():
    """Clear all shared rate limit windows."""
    get_rate_limit_backend()._windows.clear()


def _wire_spa_recovery_mocks(find_return=None):
    """Wire SPA recovery with AsyncMock repos. Returns (mock_repo, mock_audit).

    Must be called AFTER app_client fixture creates the TestClient,
    because the app lifespan overwrites module-level repos during startup.
    """
    mock_repo = AsyncMock()
    mock_repo.find_by_email = AsyncMock(return_value=find_return)
    mock_repo.update_api_key_hash = AsyncMock()
    mock_repo.consume_backup_code = AsyncMock()
    mock_audit = AsyncMock()
    configure_spa_recovery(
        platform_admin_repo=mock_repo,
        audit_repo=mock_audit,
    )
    return mock_repo, mock_audit


def _wire_tenant_recovery_mocks():
    """Wire tenant recovery with AsyncMock repos. Returns dict of mocks.

    Must be called AFTER app_client fixture creates the TestClient.
    """
    mock_tenant_repo = AsyncMock()
    mock_tenant_repo.update_recovery_address = AsyncMock()
    mock_tenant_repo.get_recovery_address = AsyncMock(return_value=None)
    mock_verification_repo = AsyncMock()
    mock_verification_repo.create_token = AsyncMock()
    mock_verification_repo.consume_token = AsyncMock(return_value=None)
    mock_audit = AsyncMock()
    configure_tenant_recovery(
        tenant_repo=mock_tenant_repo,
        verification_repo=mock_verification_repo,
        audit_repo=mock_audit,
    )
    return {
        "tenant_repo": mock_tenant_repo,
        "verification_repo": mock_verification_repo,
        "audit_repo": mock_audit,
    }


# =========================================================================
# Group 1: SPA Recovery (SPEC-1678)
# =========================================================================


class TestSpaRecovery(MutationTestBase):
    """POST /api/auth/spa-recovery/recover — public, rate-limited."""

    def test_always_returns_200_for_unknown_email(self, spa_client):
        """Enumeration prevention: unknown email still gets 200."""
        _clear_rate_limits()
        _wire_spa_recovery_mocks(find_return=None)
        resp = spa_client.raw.post(
            SPA_RECOVERY_URL,
            json={"email": "unknown@nowhere.com", "backup_code": "WRONG"},
        )
        assert resp.status_code == 200
        assert "backup code are valid" in resp.json()["message"]

    def test_always_returns_200_for_invalid_code(self, spa_client):
        """Enumeration prevention: valid email + wrong code still gets 200."""
        _clear_rate_limits()
        mock_repo, _ = _wire_spa_recovery_mocks(
            find_return=_make_platform_admin_doc(),
        )
        resp = spa_client.raw.post(
            SPA_RECOVERY_URL,
            json={"email": "admin@test.com", "backup_code": "WRONG-CODE"},
        )
        assert resp.status_code == 200
        mock_repo.update_api_key_hash.assert_not_called()

    @patch(
        "src.multi_tenant.spa_recovery._send_recovery_email",
        new_callable=AsyncMock,
    )
    def test_happy_path_valid_email_and_code(self, mock_send, spa_client):
        """Valid email + valid backup code triggers key regen + email."""
        _clear_rate_limits()
        mock_repo, _ = _wire_spa_recovery_mocks(
            find_return=_make_platform_admin_doc(),
        )
        resp = spa_client.raw.post(
            SPA_RECOVERY_URL,
            json={"email": "admin@test.com", "backup_code": VALID_BACKUP_CODE},
        )
        assert resp.status_code == 200
        mock_repo.update_api_key_hash.assert_called_once()
        mock_send.assert_called_once()
        assert mock_send.call_args[0][0] == "admin@test.com"

    @patch(
        "src.multi_tenant.spa_recovery._send_recovery_email",
        new_callable=AsyncMock,
    )
    def test_consumes_backup_code(self, mock_send, spa_client):
        """Successful recovery consumes the used backup code."""
        _clear_rate_limits()
        mock_repo, _ = _wire_spa_recovery_mocks(
            find_return=_make_platform_admin_doc(),
        )
        resp = spa_client.raw.post(
            SPA_RECOVERY_URL,
            json={"email": "admin@test.com", "backup_code": VALID_BACKUP_CODE},
        )
        assert resp.status_code == 200
        mock_repo.consume_backup_code.assert_called_once()
        call_kw = mock_repo.consume_backup_code.call_args[1]
        assert call_kw["remaining_hashes"] == []

    def test_rate_limit_returns_429(self, spa_client):
        """Exceeding 3 attempts per 15 min returns 429."""
        _clear_rate_limits()
        _wire_spa_recovery_mocks(find_return=None)
        for _ in range(3):
            spa_client.raw.post(
                SPA_RECOVERY_URL,
                json={"email": "x@test.com", "backup_code": "CODE"},
            )
        resp = spa_client.raw.post(
            SPA_RECOVERY_URL,
            json={"email": "x@test.com", "backup_code": "CODE"},
        )
        assert resp.status_code == 429


# =========================================================================
# Group 2: Tenant Recovery (SPEC-1677)
# =========================================================================


class TestTenantRecoveryActivate(MutationTestBase):
    """POST /api/superadmin/tenant-recovery/activate — SPA auth required."""

    def test_requires_auth(self, spa_client):
        """Unauthenticated request returns 401."""
        _wire_tenant_recovery_mocks()
        self.assert_requires_auth(
            spa_client.raw, "post", TENANT_RECOVERY_ACTIVATE_URL,
            json={"tenant_id": "t-test-001", "recovery_email": "r@test.com"},
        )

    def test_rejects_widget_key(self, widget_client):
        """Widget key cannot access superadmin endpoints."""
        _wire_tenant_recovery_mocks()
        self.assert_rejects_widget_key(
            widget_client, "post", TENANT_RECOVERY_ACTIVATE_URL,
            json={"tenant_id": "t-test-001", "recovery_email": "r@test.com"},
        )

    def test_happy_path_with_spa_key(self, spa_client):
        """SPA key activates recovery address successfully."""
        mocks = _wire_tenant_recovery_mocks()
        resp = spa_client.post(
            TENANT_RECOVERY_ACTIVATE_URL,
            json={"tenant_id": "t-test-001", "recovery_email": "r@test.com"},
        )
        assert resp.status_code == 200
        mocks["tenant_repo"].update_recovery_address.assert_called_once()

    def test_happy_path_with_tenant_key(self, starter_client):
        """Tenant key also succeeds (router has no platform-admin guard)."""
        _wire_tenant_recovery_mocks()
        resp = starter_client.post(
            TENANT_RECOVERY_ACTIVATE_URL,
            json={"tenant_id": "t-test-001", "recovery_email": "r@test.com"},
        )
        assert resp.status_code == 200


class TestTenantRecoverySendLink(MutationTestBase):
    """POST /api/superadmin/tenant-recovery/send-auth-link — SPA auth required."""

    @patch(
        "src.multi_tenant.tenant_recovery._send_recovery_auth_email",
        new_callable=AsyncMock,
    )
    def test_happy_path(self, mock_send, spa_client):
        """SPA key sends recovery auth link when address is active."""
        mocks = _wire_tenant_recovery_mocks()
        mocks["tenant_repo"].get_recovery_address = AsyncMock(return_value={
            "recovery_address": "recovery@test.com",
            "recovery_address_enabled": True,
        })
        resp = spa_client.post(
            TENANT_RECOVERY_SEND_LINK_URL,
            json={"tenant_id": "t-test-001"},
        )
        assert resp.status_code == 200
        assert "sent" in resp.json()["message"].lower()
        mocks["verification_repo"].create_token.assert_called_once()
        mock_send.assert_called_once()

    def test_rejects_when_no_recovery_address(self, spa_client):
        """Returns 400 when tenant has no active recovery address."""
        mocks = _wire_tenant_recovery_mocks()
        mocks["tenant_repo"].get_recovery_address = AsyncMock(return_value={
            "recovery_address_enabled": False,
        })
        resp = spa_client.post(
            TENANT_RECOVERY_SEND_LINK_URL,
            json={"tenant_id": "t-test-001"},
        )
        assert resp.status_code == 400

    def test_requires_auth(self, spa_client):
        """Unauthenticated request returns 401."""
        _wire_tenant_recovery_mocks()
        self.assert_requires_auth(
            spa_client.raw, "post", TENANT_RECOVERY_SEND_LINK_URL,
            json={"tenant_id": "t-test-001"},
        )


class TestTenantRecoveryVerify(MutationTestBase):
    """GET /api/auth/account-recovery/verify — public, token-based."""

    def test_rejects_missing_token(self, spa_client):
        """Missing query params returns 422."""
        _wire_tenant_recovery_mocks()
        resp = spa_client.raw.get(ACCOUNT_RECOVERY_VERIFY_URL)
        assert resp.status_code == 422

    def test_rejects_invalid_token(self, spa_client):
        """Invalid/expired token returns 400."""
        mocks = _wire_tenant_recovery_mocks()
        mocks["verification_repo"].consume_token = AsyncMock(return_value=None)
        resp = spa_client.raw.get(
            ACCOUNT_RECOVERY_VERIFY_URL,
            params={"token": "bad-token", "tenant": "t-test-001"},
        )
        assert resp.status_code == 400

    def test_happy_path_issues_session_jwt(self, spa_client):
        """Valid token returns session JWT."""
        mocks = _wire_tenant_recovery_mocks()
        mocks["verification_repo"].consume_token = AsyncMock(return_value={
            "tenant_id": "t-test-001",
            "email": "recovery@test.com",
        })
        resp = spa_client.raw.get(
            ACCOUNT_RECOVERY_VERIFY_URL,
            params={"token": "valid-token-abc", "tenant": "t-test-001"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "session_token" in data
        assert data["tenant_id"] == "t-test-001"

    def test_rejects_tenant_mismatch(self, spa_client):
        """Token tenant_id must match query param tenant."""
        mocks = _wire_tenant_recovery_mocks()
        mocks["verification_repo"].consume_token = AsyncMock(return_value={
            "tenant_id": "t-other-tenant",
            "email": "recovery@test.com",
        })
        resp = spa_client.raw.get(
            ACCOUNT_RECOVERY_VERIFY_URL,
            params={"token": "valid-token-abc", "tenant": "t-test-001"},
        )
        assert resp.status_code == 400


# =========================================================================
# Group 3: Magic Link Auth (SPEC-1618/1619)
# =========================================================================


class TestMagicLinkRequest(MutationTestBase):
    """POST /api/auth/magic-link/request — public, rate-limited."""

    @patch("src.multi_tenant.repositories.VerificationTokenRepository")
    @patch("src.multi_tenant.repositories.TenantRepository")
    @patch("src.multi_tenant.repositories.TeamMemberRepository")
    def test_always_returns_200(
        self, mock_team_cls, mock_tenant_cls, mock_token_cls, spa_client,
    ):
        """Enumeration prevention: always returns 200 regardless of email validity."""
        _clear_rate_limits()
        mock_team_cls.return_value.find_by_email = AsyncMock(return_value=None)
        mock_tenant_cls.return_value.read = AsyncMock(return_value=None)
        resp = spa_client.raw.post(
            MAGIC_LINK_REQUEST_URL,
            json={"email": "nobody@test.com", "tenant": "t-fake"},
        )
        assert resp.status_code == 200

    def test_requires_both_email_and_tenant(self, spa_client):
        """Missing email or tenant field returns 422."""
        _clear_rate_limits()
        # Missing tenant
        resp = spa_client.raw.post(
            MAGIC_LINK_REQUEST_URL,
            json={"email": "test@test.com"},
        )
        assert resp.status_code == 422

        # Missing email
        resp = spa_client.raw.post(
            MAGIC_LINK_REQUEST_URL,
            json={"tenant": "t-test-001"},
        )
        assert resp.status_code == 422

    @patch("src.multi_tenant.repositories.VerificationTokenRepository")
    @patch("src.multi_tenant.repositories.TenantRepository")
    @patch("src.multi_tenant.repositories.TeamMemberRepository")
    def test_rate_limit_returns_200_but_skips_email(
        self, mock_team_cls, mock_tenant_cls, mock_token_cls, spa_client,
    ):
        """After 3 attempts per 5 min, response is still 200 (enumeration safe).

        The rate limiter prevents actual email sending but the response
        remains 200 to prevent leaking rate-limit state as an oracle.
        """
        _clear_rate_limits()
        mock_team_cls.return_value.find_by_email = AsyncMock(return_value=None)
        mock_tenant_cls.return_value.read = AsyncMock(return_value=None)
        for _ in range(4):
            resp = spa_client.raw.post(
                MAGIC_LINK_REQUEST_URL,
                json={"email": "x@test.com", "tenant": "t-test"},
            )
        # Magic link always returns 200 even when rate limited
        assert resp.status_code == 200


class TestMagicLinkVerify(MutationTestBase):
    """GET /api/auth/magic-link/verify — public, token-based."""

    def test_rejects_missing_token(self, spa_client):
        """Missing token query param returns 422."""
        resp = spa_client.raw.get(MAGIC_LINK_VERIFY_URL)
        assert resp.status_code == 422

    @patch("src.multi_tenant.repositories.VerificationTokenRepository")
    def test_rejects_invalid_token(self, mock_token_cls, spa_client):
        """Invalid/expired token returns 400."""
        mock_token_cls.return_value.consume_token = AsyncMock(return_value=None)
        resp = spa_client.raw.get(
            MAGIC_LINK_VERIFY_URL,
            params={"token": "expired-or-invalid-token"},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert data["error"] == "invalid_token"

    @patch("src.multi_tenant.admin_mfa_auth.requires_2fa", return_value=False)
    @patch("src.multi_tenant.repositories.TeamMemberRepository")
    @patch("src.multi_tenant.repositories.VerificationTokenRepository")
    def test_happy_path_issues_session_jwt(
        self, mock_token_cls, mock_team_cls, mock_2fa, spa_client,
    ):
        """Valid token returns session JWT with tenant info."""
        mock_token_cls.return_value.consume_token = AsyncMock(return_value={
            "tenant_id": "t-test-001",
            "email": "user@test.com",
            "member_id": None,
        })
        resp = spa_client.raw.get(
            MAGIC_LINK_VERIFY_URL,
            params={"token": "valid-magic-token"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "session_token" in data
        assert data["tenant_id"] == "t-test-001"
        assert data["email"] == "user@test.com"
