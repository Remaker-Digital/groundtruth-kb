"""Tests for two-stage 2FA authentication (2FA-01 to 2FA-20).

Covers:
    - Pending 2FA token creation and verification
    - requires_2fa role/opt-out/enrollment logic
    - TOTP verification endpoint
    - Backup code verification endpoint
    - SMS OTP request and verification endpoints
    - Brute-force mitigation (5 attempts)
    - Magic link verify → pending_2fa response for admins

Test plan reference: §5.11 (2FA Auth — WI #295 Phase 2)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest

from src.multi_tenant.admin_mfa_auth import (
    _MAX_FAILED_ATTEMPTS,
    _failed_attempts,
    TotpVerifyRequest,
    BackupVerifyRequest,
    SmsRequestBody,
    SmsVerifyRequest,
    configure_2fa_services,
    create_pending_2fa_token,
    requires_2fa,
    verify_pending_2fa_token,
    verify_totp_2fa,
    verify_backup_2fa,
    request_sms_otp,
    verify_sms_otp,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_state():
    """Reset failed attempts and service config between tests."""
    _failed_attempts.clear()
    configure_2fa_services(None, None, None)
    yield
    _failed_attempts.clear()
    configure_2fa_services(None, None, None)


@pytest.fixture()
def admin_member():
    """Admin team member with MFA enrolled."""
    return {
        "id": "member-admin",
        "tenant_id": "t-001",
        "email": "admin@test.com",
        "role": "admin",
        "mfa_enabled": True,
        "mfa_enrolled_at": "2026-01-15T00:00:00Z",
        "mfa_backup_code_hashes": ["hash1", "hash2", "hash3"],
    }


@pytest.fixture()
def agent_member():
    """Escalation agent team member (no MFA)."""
    return {
        "id": "member-agent",
        "tenant_id": "t-001",
        "email": "agent@test.com",
        "role": "escalation_agent",
        "mfa_enabled": False,
    }


@pytest.fixture()
def pending_token():
    """Create a valid pending 2FA token."""
    token, _ = create_pending_2fa_token("t-001", "admin@test.com", "member-admin", "admin")
    return token


# ---------------------------------------------------------------------------
# requires_2fa logic (2FA-01 to 2FA-05)
# ---------------------------------------------------------------------------


class TestRequires2fa:
    """2FA-01 to 2FA-05: Role-based 2FA requirement logic."""

    def test_2fa01_admin_with_mfa_enabled_requires_2fa(self, admin_member):
        assert requires_2fa("admin", admin_member) is True

    def test_2fa02_superadmin_with_mfa_enabled_requires_2fa(self):
        member = {"mfa_enabled": True, "mfa_opt_out": False}
        assert requires_2fa("superadmin", member) is True

    def test_2fa03_escalation_agent_does_not_require_2fa(self, agent_member):
        assert requires_2fa("escalation_agent", agent_member) is False

    def test_2fa04_viewer_does_not_require_2fa(self):
        assert requires_2fa("viewer", {"mfa_enabled": True}) is False

    def test_2fa05_admin_with_opt_out_skips_2fa(self):
        member = {"mfa_enabled": True, "mfa_opt_out": True}
        assert requires_2fa("admin", member) is False

    def test_2fa06_admin_without_mfa_enrolled_skips_2fa(self):
        """New admin (no MFA enrolled yet) — cannot challenge."""
        member = {"mfa_enabled": False}
        assert requires_2fa("admin", member) is False


# ---------------------------------------------------------------------------
# Pending 2FA token (2FA-07 to 2FA-09)
# ---------------------------------------------------------------------------


class TestPending2faToken:
    """2FA-07 to 2FA-09: Pending JWT creation and verification."""

    def test_2fa07_creates_valid_pending_token(self):
        token, expires_at = create_pending_2fa_token(
            "t-001", "admin@test.com", "member-admin", "admin",
        )
        payload = verify_pending_2fa_token(token)
        assert payload is not None
        assert payload["sub"] == "t-001"
        assert payload["email"] == "admin@test.com"
        assert payload["member_id"] == "member-admin"
        assert payload["role"] == "admin"
        assert payload["type"] == "pending_2fa_session"

    def test_2fa08_expired_pending_token_returns_none(self):
        from src.multi_tenant.admin_mfa_auth import _PENDING_JWT_SECRET
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "t-001", "email": "a@b.com", "member_id": "m1",
            "role": "admin", "type": "pending_2fa_session",
            "iat": int((now - timedelta(minutes=15)).timestamp()),
            "exp": int((now - timedelta(minutes=5)).timestamp()),
        }
        token = jwt.encode(payload, _PENDING_JWT_SECRET, algorithm="HS256")
        assert verify_pending_2fa_token(token) is None

    def test_2fa09_wrong_type_returns_none(self):
        from src.multi_tenant.admin_mfa_auth import _PENDING_JWT_SECRET
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "t-001", "email": "a@b.com", "member_id": "m1",
            "role": "admin", "type": "magic_link_session",  # wrong type
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
        }
        token = jwt.encode(payload, _PENDING_JWT_SECRET, algorithm="HS256")
        assert verify_pending_2fa_token(token) is None


# ---------------------------------------------------------------------------
# TOTP verify endpoint (2FA-10 to 2FA-12)
# ---------------------------------------------------------------------------


class TestTotpVerify:
    """2FA-10 to 2FA-12: POST /api/auth/2fa/totp/verify."""

    @pytest.mark.asyncio
    async def test_2fa10_valid_totp_issues_full_session(self, pending_token, admin_member):
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)

        mock_secret_svc = AsyncMock()
        mock_secret_svc.get_secret = AsyncMock(return_value="JBSWY3DPEHPK3PXP")

        mock_totp_svc = MagicMock()
        mock_totp_svc._secret_service = mock_secret_svc

        configure_2fa_services(
            mfa_totp_service=mock_totp_svc,
            team_repo=mock_team,
        )

        with patch("src.multi_tenant.mfa_totp.verify_totp", return_value=True):
            resp = await verify_totp_2fa(TotpVerifyRequest(
                pending_token=pending_token, code="123456",
            ))

        import json
        body = json.loads(resp.body)
        assert resp.status_code == 200
        assert "session_token" in body
        assert body["tenant_id"] == "t-001"

    @pytest.mark.asyncio
    async def test_2fa11_invalid_totp_returns_401(self, pending_token, admin_member):
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)

        mock_secret_svc = AsyncMock()
        mock_secret_svc.get_secret = AsyncMock(return_value="JBSWY3DPEHPK3PXP")

        mock_totp_svc = MagicMock()
        mock_totp_svc._secret_service = mock_secret_svc

        configure_2fa_services(
            mfa_totp_service=mock_totp_svc,
            team_repo=mock_team,
        )

        with patch("src.multi_tenant.mfa_totp.verify_totp", return_value=False):
            resp = await verify_totp_2fa(TotpVerifyRequest(
                pending_token=pending_token, code="000000",
            ))

        import json
        body = json.loads(resp.body)
        assert resp.status_code == 401
        assert body["error"] == "invalid_code"

    @pytest.mark.asyncio
    async def test_2fa12_expired_pending_token_returns_401(self):
        resp = await verify_totp_2fa(TotpVerifyRequest(
            pending_token="invalid.jwt.token", code="123456",
        ))
        import json
        body = json.loads(resp.body)
        assert resp.status_code == 401
        assert body["error"] == "invalid_token"


# ---------------------------------------------------------------------------
# Brute-force mitigation (2FA-13 to 2FA-14)
# ---------------------------------------------------------------------------


class TestBruteForce:
    """2FA-13 to 2FA-14: Attempt limiting."""

    @pytest.mark.asyncio
    async def test_2fa13_brute_force_lockout_after_5_attempts(self, pending_token, admin_member):
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)

        mock_secret_svc = AsyncMock()
        mock_secret_svc.get_secret = AsyncMock(return_value="JBSWY3DPEHPK3PXP")

        mock_totp_svc = MagicMock()
        mock_totp_svc._secret_service = mock_secret_svc

        configure_2fa_services(
            mfa_totp_service=mock_totp_svc,
            team_repo=mock_team,
        )

        # Exhaust attempts with wrong codes
        with patch("src.multi_tenant.mfa_totp.verify_totp", return_value=False):
            for _ in range(_MAX_FAILED_ATTEMPTS):
                await verify_totp_2fa(TotpVerifyRequest(
                    pending_token=pending_token, code="000000",
                ))

        # 6th attempt should be locked out immediately
        resp = await verify_totp_2fa(TotpVerifyRequest(
            pending_token=pending_token, code="123456",
        ))
        import json
        body = json.loads(resp.body)
        assert resp.status_code == 429
        assert body["error"] == "too_many_attempts"

    @pytest.mark.asyncio
    async def test_2fa14_remaining_attempts_decrements(self, pending_token, admin_member):
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)

        mock_secret_svc = AsyncMock()
        mock_secret_svc.get_secret = AsyncMock(return_value="JBSWY3DPEHPK3PXP")

        mock_totp_svc = MagicMock()
        mock_totp_svc._secret_service = mock_secret_svc

        configure_2fa_services(
            mfa_totp_service=mock_totp_svc,
            team_repo=mock_team,
        )

        with patch("src.multi_tenant.mfa_totp.verify_totp", return_value=False):
            resp = await verify_totp_2fa(TotpVerifyRequest(
                pending_token=pending_token, code="000000",
            ))

        import json
        body = json.loads(resp.body)
        assert "4 attempts remaining" in body["message"]


# ---------------------------------------------------------------------------
# Backup code verify (2FA-15 to 2FA-16)
# ---------------------------------------------------------------------------


class TestBackupCodeVerify:
    """2FA-15 to 2FA-16: POST /api/auth/2fa/totp/backup-verify."""

    @pytest.mark.asyncio
    async def test_2fa15_valid_backup_code_issues_session(self, pending_token, admin_member):
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)
        mock_team.update_member_fields = AsyncMock()

        configure_2fa_services(team_repo=mock_team)

        with patch(
            "src.multi_tenant.mfa_totp.verify_backup_code",
            return_value=(True, ["hash2", "hash3"]),
        ):
            resp = await verify_backup_2fa(BackupVerifyRequest(
                pending_token=pending_token, code="ABCD1234",
            ))

        import json
        body = json.loads(resp.body)
        assert resp.status_code == 200
        assert "session_token" in body

        # Verify used code hash was removed
        mock_team.update_member_fields.assert_called_once()
        update_call = mock_team.update_member_fields.call_args
        assert update_call.args[2] == {"mfa_backup_code_hashes": ["hash2", "hash3"]}

    @pytest.mark.asyncio
    async def test_2fa16_invalid_backup_code_returns_401(self, pending_token, admin_member):
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)

        configure_2fa_services(team_repo=mock_team)

        with patch(
            "src.multi_tenant.mfa_totp.verify_backup_code",
            return_value=(False, ["hash1", "hash2", "hash3"]),
        ):
            resp = await verify_backup_2fa(BackupVerifyRequest(
                pending_token=pending_token, code="WRONG123",
            ))

        import json
        body = json.loads(resp.body)
        assert resp.status_code == 401
        assert body["error"] == "invalid_code"


# ---------------------------------------------------------------------------
# SMS OTP (2FA-17 to 2FA-20)
# ---------------------------------------------------------------------------


class TestSmsOtp:
    """2FA-17 to 2FA-20: SMS OTP request and verification."""

    @pytest.mark.asyncio
    async def test_2fa17_sms_request_sends_to_verified_phone(self, pending_token):
        member = {
            "id": "member-admin",
            "phone_number": "+12125551234",
            "phone_verified": True,
        }
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=member)

        mock_sms = AsyncMock()
        mock_sms.send_code = AsyncMock(return_value=True)

        configure_2fa_services(sms_mfa_service=mock_sms, team_repo=mock_team)

        resp = await request_sms_otp(SmsRequestBody(pending_token=pending_token))
        import json
        body = json.loads(resp.body)
        assert resp.status_code == 200
        assert "Verification code sent" in body["message"]
        assert body["phone_hint"] == "+12***34"

    @pytest.mark.asyncio
    async def test_2fa18_sms_request_rejects_unverified_phone(self, pending_token):
        member = {
            "id": "member-admin",
            "phone_number": "+12125551234",
            "phone_verified": False,
        }
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=member)
        mock_sms = AsyncMock()

        configure_2fa_services(sms_mfa_service=mock_sms, team_repo=mock_team)

        resp = await request_sms_otp(SmsRequestBody(pending_token=pending_token))
        import json
        body = json.loads(resp.body)
        assert resp.status_code == 400
        assert body["error"] == "phone_not_verified"

    @pytest.mark.asyncio
    async def test_2fa19_sms_verify_valid_code(self, pending_token):
        mock_sms = AsyncMock()
        mock_sms.verify_code = AsyncMock(return_value=True)

        configure_2fa_services(sms_mfa_service=mock_sms)

        resp = await verify_sms_otp(SmsVerifyRequest(
            pending_token=pending_token, code="654321",
        ))
        import json
        body = json.loads(resp.body)
        assert resp.status_code == 200
        assert "session_token" in body

    @pytest.mark.asyncio
    async def test_2fa20_sms_verify_invalid_code(self, pending_token):
        mock_sms = AsyncMock()
        mock_sms.verify_code = AsyncMock(return_value=False)

        configure_2fa_services(sms_mfa_service=mock_sms)

        resp = await verify_sms_otp(SmsVerifyRequest(
            pending_token=pending_token, code="000000",
        ))
        import json
        body = json.loads(resp.body)
        assert resp.status_code == 401
        assert body["error"] == "invalid_code"


# ---------------------------------------------------------------------------
# SPEC-1289: Return available MFA methods when 2FA required
# ---------------------------------------------------------------------------


class TestSpec1289MfaMethods:
    """SPEC-1289: Return available MFA methods when 2FA required."""

    @pytest.mark.asyncio
    async def test_spec1289_admin_with_totp_gets_totp_method(
        self, admin_member,
    ):
        """SPEC-1289: Admin with mfa_enabled gets 'totp' in methods."""
        from src.multi_tenant.magic_link_auth import _get_available_mfa_methods
        methods = _get_available_mfa_methods(admin_member)
        assert "totp" in methods

    @pytest.mark.asyncio
    async def test_spec1289_admin_with_backup_codes_gets_backup_method(
        self, admin_member,
    ):
        """SPEC-1289: Admin with backup code hashes gets 'backup' in methods."""
        from src.multi_tenant.magic_link_auth import _get_available_mfa_methods
        methods = _get_available_mfa_methods(admin_member)
        assert "backup" in methods

    @pytest.mark.asyncio
    async def test_spec1289_admin_with_phone_gets_sms_method(self):
        """SPEC-1289: Admin with verified phone + SMS available gets 'sms' in methods."""
        from src.multi_tenant.magic_link_auth import _get_available_mfa_methods
        member = {
            "mfa_enabled": True,
            "mfa_backup_code_hashes": [],
            "phone_number": "+12125551234",
            "phone_verified": True,
        }
        with patch("src.multi_tenant.sms_mfa_service.is_sms_available", return_value=True):
            methods = _get_available_mfa_methods(member)
        assert "sms" in methods

    @pytest.mark.asyncio
    async def test_spec1289_admin_without_phone_no_sms(self):
        """SPEC-1289: Admin without verified phone does not get 'sms'."""
        from src.multi_tenant.magic_link_auth import _get_available_mfa_methods
        member = {
            "mfa_enabled": True,
            "mfa_backup_code_hashes": [],
            "phone_number": None,
            "phone_verified": False,
        }
        methods = _get_available_mfa_methods(member)
        assert "sms" not in methods

    @pytest.mark.asyncio
    async def test_spec1289_no_member_doc_returns_empty(self):
        """SPEC-1289: None member_doc returns empty methods list."""
        from src.multi_tenant.magic_link_auth import _get_available_mfa_methods
        methods = _get_available_mfa_methods(None)
        assert methods == []

    @pytest.mark.asyncio
    async def test_spec1289_verify_endpoint_returns_mfa_methods(self):
        """SPEC-1289: Magic link verify returns mfa_methods in 2FA response."""
        from src.multi_tenant.magic_link_auth import verify_magic_link

        mock_token_repo = AsyncMock()
        mock_token_repo.consume_token = AsyncMock(return_value={
            "tenant_id": "t-001",
            "email": "admin@test.com",
            "member_id": "member-admin",
        })

        mock_team_repo = AsyncMock()
        mock_team_repo.read = AsyncMock(return_value={
            "id": "member-admin",
            "tenant_id": "t-001",
            "email": "admin@test.com",
            "role": "admin",
            "mfa_enabled": True,
            "mfa_backup_code_hashes": ["hash1"],
            "phone_number": None,
            "phone_verified": False,
        })

        with (
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
        ):
            resp = await verify_magic_link(token="valid-token")

        import json
        body = json.loads(resp.body)
        assert resp.status_code == 200
        assert body["requires_2fa"] is True
        assert "mfa_methods" in body
        assert "totp" in body["mfa_methods"]
        assert "backup" in body["mfa_methods"]


# ---------------------------------------------------------------------------
# S130: Pending 2FA JWT constant verification (TEST-2907..2908)
# ---------------------------------------------------------------------------


class TestPending2faJwt:
    """SPEC-1252: pending 2FA JWT lifetime and algorithm constants."""

    def test_pending_2fa_lifetime_is_10_minutes(self) -> None:
        """TEST-2907: _PENDING_TOKEN_LIFETIME_MINUTES == 10."""
        from src.multi_tenant.admin_mfa_auth import _PENDING_TOKEN_LIFETIME_MINUTES
        assert _PENDING_TOKEN_LIFETIME_MINUTES == 10

    def test_pending_2fa_uses_hs256(self) -> None:
        """TEST-2908: create_pending_2fa_token encodes with HS256."""
        token, _ = create_pending_2fa_token(
            tenant_id="t-test",
            email="test@example.com",
            member_id="m-test",
            role="admin",
        )
        # Decode without verification to inspect the header
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS256"
