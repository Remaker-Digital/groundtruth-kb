"""Tests for MFA/TOTP specifications (SPEC-1252 through SPEC-1276).

Covers:
    - SPEC-1252: Pending_2fa JWT with 10-min lifetime
    - SPEC-1257: Full 8-hour session JWT after 2FA
    - SPEC-1258: TOTP verify endpoint consuming pending JWT
    - SPEC-1259: Backup code verify endpoint consuming used codes
    - SPEC-1263: Brute-force tracking in-memory per fingerprint
    - SPEC-1265: SMS OTP as SHA-256 hashes with 10-min TTL
    - SPEC-1268: Graceful degradation when ACS_SMS_FROM not configured
    - SPEC-1272: TOTP 6 digits, 30s interval, +/-1 window
    - SPEC-1273: 10 backup codes, 8-char alphanumeric, no I/O/0/1
    - SPEC-1276: TOTP seeds in Key Vault as user-{member_id}-totp-seed

Run:
    pytest tests/multi_tenant/test_mfa_totp_specs.py -v

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pyotp
import pytest

from src.multi_tenant.admin_mfa_auth import (
    _MAX_FAILED_ATTEMPTS,
    _PENDING_TOKEN_LIFETIME_MINUTES,
    _failed_attempts,
    BackupVerifyRequest,
    TotpVerifyRequest,
    configure_2fa_services,
    create_pending_2fa_token,
    verify_backup_2fa,
    verify_pending_2fa_token,
    verify_totp_2fa,
)
from src.multi_tenant.mfa_totp import (
    _BACKUP_CODE_COUNT,
    _BACKUP_CODE_LENGTH,
    _TOTP_DIGITS,
    _TOTP_INTERVAL,
    _TOTP_VALID_WINDOW,
    MfaTotpService,
    generate_backup_codes,
    generate_totp_secret,
    hash_backup_code,
    verify_backup_code,
    verify_totp,
)
from src.multi_tenant.sms_mfa_service import (
    _SMS_CODE_DIGITS,
    _SMS_CODE_TTL,
    SmsMfaService,
    _generate_otp,
    _hash_otp,
    is_sms_available,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_mfa_state():
    """Reset brute-force tracking and services between tests."""
    _failed_attempts.clear()
    configure_2fa_services(None, None, None)
    yield
    _failed_attempts.clear()
    configure_2fa_services(None, None, None)


@pytest.fixture()
def pending_token():
    """Create a valid pending 2FA token for testing."""
    token, _ = create_pending_2fa_token("t-001", "admin@test.com", "member-admin", "admin")
    return token


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


# ===========================================================================
# SPEC-1252: Pending_2fa JWT with 10-min lifetime
# ===========================================================================


class TestSpec1252Pending2faJwt:
    """SPEC-1252: Pending_2fa JWT with 10-min lifetime."""

    def test_spec1252_pending_token_lifetime_is_10_minutes(self):
        """SPEC-1252: _PENDING_TOKEN_LIFETIME_MINUTES is 10."""
        assert _PENDING_TOKEN_LIFETIME_MINUTES == 10

    def test_spec1252_pending_token_has_correct_type(self):
        """SPEC-1252: Pending token has type 'pending_2fa_session'."""
        token, _ = create_pending_2fa_token("t-1", "a@b.com", "m1", "admin")
        payload = verify_pending_2fa_token(token)
        assert payload is not None
        assert payload["type"] == "pending_2fa_session"

    def test_spec1252_pending_token_expires_in_10_minutes(self):
        """SPEC-1252: exp - iat delta is 10 minutes."""
        token, _ = create_pending_2fa_token("t-1", "a@b.com", "m1", "admin")
        payload = verify_pending_2fa_token(token)
        assert payload is not None
        delta = payload["exp"] - payload["iat"]
        assert abs(delta - 600) < 5  # 600 seconds = 10 minutes, allow 5s tolerance

    def test_spec1252_pending_token_uses_hs256(self):
        """SPEC-1252: Pending token is HS256 signed."""
        from src.multi_tenant.admin_mfa_auth import _PENDING_JWT_SECRET
        token, _ = create_pending_2fa_token("t-1", "a@b.com", "m1", "admin")
        # Should decode with HS256
        payload = jwt.decode(token, _PENDING_JWT_SECRET, algorithms=["HS256"])
        assert payload["sub"] == "t-1"

    def test_spec1252_pending_token_carries_member_identity(self):
        """SPEC-1252: Pending token carries tenant_id, email, member_id, role."""
        token, _ = create_pending_2fa_token("t-1", "admin@co.com", "mem-1", "admin")
        payload = verify_pending_2fa_token(token)
        assert payload["sub"] == "t-1"
        assert payload["email"] == "admin@co.com"
        assert payload["member_id"] == "mem-1"
        assert payload["role"] == "admin"

    def test_spec1252_expired_pending_token_rejected(self):
        """SPEC-1252: Expired pending token returns None."""
        from src.multi_tenant.admin_mfa_auth import _PENDING_JWT_SECRET
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "t-1", "email": "a@b.com", "member_id": "m1",
            "role": "admin", "type": "pending_2fa_session",
            "iat": int((now - timedelta(minutes=20)).timestamp()),
            "exp": int((now - timedelta(minutes=10)).timestamp()),
        }
        token = jwt.encode(payload, _PENDING_JWT_SECRET, algorithm="HS256")
        assert verify_pending_2fa_token(token) is None


# ===========================================================================
# SPEC-1257: Full 8-hour session JWT after 2FA
# ===========================================================================


class TestSpec1257FullSessionAfter2fa:
    """SPEC-1257: Full 8-hour session JWT after 2FA."""

    @pytest.mark.asyncio
    async def test_spec1257_totp_success_issues_8_hour_session(self, pending_token, admin_member):
        """SPEC-1257: Successful TOTP verification issues an 8-hour session JWT."""
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)
        mock_secret_svc = AsyncMock()
        mock_secret_svc.get_secret = AsyncMock(return_value="JBSWY3DPEHPK3PXP")
        mock_totp_svc = MagicMock()
        mock_totp_svc._secret_service = mock_secret_svc
        configure_2fa_services(mfa_totp_service=mock_totp_svc, team_repo=mock_team)

        with patch("src.multi_tenant.mfa_totp.verify_totp", return_value=True):
            resp = await verify_totp_2fa(TotpVerifyRequest(
                pending_token=pending_token, code="123456",
            ))

        body = json.loads(resp.body)
        assert resp.status_code == 200
        assert "session_token" in body

        # Verify the session token is 8 hours
        from src.multi_tenant.magic_link_auth import _JWT_SECRET
        session_payload = jwt.decode(body["session_token"], _JWT_SECRET, algorithms=["HS256"])
        delta_seconds = session_payload["exp"] - session_payload["iat"]
        assert abs(delta_seconds - 8 * 3600) < 10  # 8 hours, 10s tolerance

    @pytest.mark.asyncio
    async def test_spec1257_session_token_has_magic_link_type(self, pending_token, admin_member):
        """SPEC-1257: Session JWT after 2FA has type magic_link_session."""
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)
        mock_secret_svc = AsyncMock()
        mock_secret_svc.get_secret = AsyncMock(return_value="JBSWY3DPEHPK3PXP")
        mock_totp_svc = MagicMock()
        mock_totp_svc._secret_service = mock_secret_svc
        configure_2fa_services(mfa_totp_service=mock_totp_svc, team_repo=mock_team)

        with patch("src.multi_tenant.mfa_totp.verify_totp", return_value=True):
            resp = await verify_totp_2fa(TotpVerifyRequest(
                pending_token=pending_token, code="123456",
            ))

        body = json.loads(resp.body)
        from src.multi_tenant.magic_link_auth import _JWT_SECRET
        payload = jwt.decode(body["session_token"], _JWT_SECRET, algorithms=["HS256"])
        assert payload["type"] == "magic_link_session"


# ===========================================================================
# SPEC-1258: TOTP verify endpoint consuming pending JWT
# ===========================================================================


class TestSpec1258TotpVerifyEndpoint:
    """SPEC-1258: TOTP verify endpoint consuming pending JWT."""

    @pytest.mark.asyncio
    async def test_spec1258_valid_totp_consumes_pending_jwt(self, pending_token, admin_member):
        """SPEC-1258: Valid TOTP code + pending JWT → full session."""
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)
        mock_secret_svc = AsyncMock()
        mock_secret_svc.get_secret = AsyncMock(return_value="JBSWY3DPEHPK3PXP")
        mock_totp_svc = MagicMock()
        mock_totp_svc._secret_service = mock_secret_svc
        configure_2fa_services(mfa_totp_service=mock_totp_svc, team_repo=mock_team)

        with patch("src.multi_tenant.mfa_totp.verify_totp", return_value=True):
            resp = await verify_totp_2fa(TotpVerifyRequest(
                pending_token=pending_token, code="123456",
            ))

        body = json.loads(resp.body)
        assert resp.status_code == 200
        assert body["tenant_id"] == "t-001"
        assert body["email"] == "admin@test.com"

    @pytest.mark.asyncio
    async def test_spec1258_invalid_pending_jwt_returns_401(self):
        """SPEC-1258: Invalid pending JWT returns 401."""
        resp = await verify_totp_2fa(TotpVerifyRequest(
            pending_token="invalid.jwt.token", code="123456",
        ))
        body = json.loads(resp.body)
        assert resp.status_code == 401
        assert body["error"] == "invalid_token"

    @pytest.mark.asyncio
    async def test_spec1258_service_unavailable_returns_503(self, pending_token):
        """SPEC-1258: Missing services returns 503."""
        # Services not configured — default None
        resp = await verify_totp_2fa(TotpVerifyRequest(
            pending_token=pending_token, code="123456",
        ))
        json.loads(resp.body)
        assert resp.status_code == 503


# ===========================================================================
# SPEC-1259: Backup code verify endpoint consuming used codes
# ===========================================================================


class TestSpec1259BackupCodeVerify:
    """SPEC-1259: Backup code verify endpoint consuming used codes."""

    @pytest.mark.asyncio
    async def test_spec1259_valid_backup_code_issues_session(self, pending_token, admin_member):
        """SPEC-1259: Valid backup code → session + code consumed."""
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

        body = json.loads(resp.body)
        assert resp.status_code == 200
        assert "session_token" in body

        # Verify the consumed hash was removed
        mock_team.update_member_fields.assert_called_once()
        update_args = mock_team.update_member_fields.call_args
        assert update_args.args[2] == {"mfa_backup_code_hashes": ["hash2", "hash3"]}

    @pytest.mark.asyncio
    async def test_spec1259_invalid_backup_code_returns_401(self, pending_token, admin_member):
        """SPEC-1259: Invalid backup code returns 401."""
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)
        configure_2fa_services(team_repo=mock_team)

        with patch(
            "src.multi_tenant.mfa_totp.verify_backup_code",
            return_value=(False, admin_member["mfa_backup_code_hashes"]),
        ):
            resp = await verify_backup_2fa(BackupVerifyRequest(
                pending_token=pending_token, code="WRONG123",
            ))

        body = json.loads(resp.body)
        assert resp.status_code == 401
        assert body["error"] == "invalid_code"

    def test_spec1259_verify_backup_code_removes_used_hash(self):
        """SPEC-1259: verify_backup_code removes matching hash from list."""
        code = "ABCD1234"
        code_hash = hash_backup_code(code)
        hashes = [code_hash, "other_hash1", "other_hash2"]
        valid, remaining = verify_backup_code(code, hashes)
        assert valid is True
        assert code_hash not in remaining
        assert len(remaining) == 2

    def test_spec1259_verify_backup_code_case_insensitive(self):
        """SPEC-1259: Backup code verification is case-insensitive (uppercased)."""
        code = "abcd1234"
        code_hash = hash_backup_code(code.upper())
        hashes = [code_hash]
        valid, remaining = verify_backup_code(code, hashes)
        assert valid is True


# ===========================================================================
# SPEC-1263: Brute-force tracking in-memory per fingerprint
# ===========================================================================


class TestSpec1263BruteForceTracking:
    """SPEC-1263: Brute-force tracking in-memory per fingerprint."""

    def test_spec1263_max_failed_attempts_is_5(self):
        """SPEC-1263: _MAX_FAILED_ATTEMPTS is 5."""
        assert _MAX_FAILED_ATTEMPTS == 5

    @pytest.mark.asyncio
    async def test_spec1263_lockout_after_5_failed_attempts(self, pending_token, admin_member):
        """SPEC-1263: After 5 failed attempts, returns 429."""
        mock_team = AsyncMock()
        mock_team.read = AsyncMock(return_value=admin_member)
        mock_secret_svc = AsyncMock()
        mock_secret_svc.get_secret = AsyncMock(return_value="JBSWY3DPEHPK3PXP")
        mock_totp_svc = MagicMock()
        mock_totp_svc._secret_service = mock_secret_svc
        configure_2fa_services(mfa_totp_service=mock_totp_svc, team_repo=mock_team)

        with patch("src.multi_tenant.mfa_totp.verify_totp", return_value=False):
            for _ in range(_MAX_FAILED_ATTEMPTS):
                await verify_totp_2fa(TotpVerifyRequest(
                    pending_token=pending_token, code="000000",
                ))

        # 6th attempt — locked out
        resp = await verify_totp_2fa(TotpVerifyRequest(
            pending_token=pending_token, code="123456",
        ))
        body = json.loads(resp.body)
        assert resp.status_code == 429
        assert body["error"] == "too_many_attempts"

    def test_spec1263_tracking_is_per_fingerprint(self):
        """SPEC-1263: Different fingerprints have independent counters."""
        from src.multi_tenant.admin_mfa_auth import _record_failed_attempt, _check_brute_force

        # Fingerprint A — exhaust attempts
        for _ in range(_MAX_FAILED_ATTEMPTS):
            _record_failed_attempt("fingerprint-A")
        assert _check_brute_force("fingerprint-A") is True

        # Fingerprint B — still clean
        assert _check_brute_force("fingerprint-B") is False

    def test_spec1263_successful_2fa_clears_attempts(self):
        """SPEC-1263: Successful 2FA clears the attempt counter."""
        from src.multi_tenant.admin_mfa_auth import (
            _clear_attempts,
            _record_failed_attempt,
            _check_brute_force,
        )

        fp = "fingerprint-clear"
        for _ in range(3):
            _record_failed_attempt(fp)
        _clear_attempts(fp)
        assert _check_brute_force(fp) is False


# ===========================================================================
# SPEC-1265: SMS OTP as SHA-256 hashes with 10-min TTL
# ===========================================================================


class TestSpec1265SmsOtpStorage:
    """SPEC-1265: SMS OTP as SHA-256 hashes with 10-min TTL."""

    def test_spec1265_sms_code_is_6_digits(self):
        """SPEC-1265: _SMS_CODE_DIGITS is 6."""
        assert _SMS_CODE_DIGITS == 6

    def test_spec1265_sms_ttl_is_10_minutes(self):
        """SPEC-1265: _SMS_CODE_TTL is 600 seconds (10 min)."""
        assert _SMS_CODE_TTL == 600

    def test_spec1265_generate_otp_is_6_digits(self):
        """SPEC-1265: Generated OTP is exactly 6 digits."""
        for _ in range(20):
            code = _generate_otp()
            assert len(code) == 6
            assert code.isdigit()

    def test_spec1265_hash_otp_uses_sha256(self):
        """SPEC-1265: OTP hash is SHA-256 of the code string."""
        code = "123456"
        expected = hashlib.sha256(code.encode()).hexdigest()
        assert _hash_otp(code) == expected

    @pytest.mark.asyncio
    async def test_spec1265_send_code_stores_hash_not_plaintext(self):
        """SPEC-1265: SmsMfaService.send_code stores SHA-256 hash, not plaintext."""
        mock_repo = AsyncMock()
        mock_repo.create_token = AsyncMock()

        service = SmsMfaService(token_repo=mock_repo)

        # Create a mock SmsClient module to avoid azure SDK import issues
        mock_sms_module = MagicMock()
        mock_sms_client = MagicMock()
        mock_sms_module.SmsClient.from_connection_string.return_value = mock_sms_client

        import sys
        with (
            patch("src.multi_tenant.sms_mfa_service.is_sms_available", return_value=True),
            patch("src.multi_tenant.sms_mfa_service._generate_otp", return_value="654321"),
            patch.dict(sys.modules, {"azure.communication.sms": mock_sms_module}),
        ):
            await service.send_code("t-1", "m-1", "+12125551234")

        # Verify create_token was called with hash (in 'email' field)
        mock_repo.create_token.assert_called_once()
        call_kwargs = mock_repo.create_token.call_args.kwargs
        stored_hash = call_kwargs["email"]
        expected_hash = hashlib.sha256(b"654321").hexdigest()
        assert stored_hash == expected_hash

    @pytest.mark.asyncio
    async def test_spec1265_verify_code_compares_hash(self):
        """SPEC-1265: SmsMfaService.verify_code compares SHA-256 hashes."""
        code = "654321"
        code_hash = hashlib.sha256(code.encode()).hexdigest()

        mock_repo = AsyncMock()
        mock_repo.consume_token = AsyncMock(return_value={"email": code_hash})

        service = SmsMfaService(token_repo=mock_repo)
        result = await service.verify_code("m-1", code)
        assert result is True

    @pytest.mark.asyncio
    async def test_spec1265_verify_code_rejects_wrong_code(self):
        """SPEC-1265: Wrong code fails hash comparison."""
        mock_repo = AsyncMock()
        mock_repo.consume_token = AsyncMock(return_value={
            "email": hashlib.sha256(b"654321").hexdigest(),
        })

        service = SmsMfaService(token_repo=mock_repo)
        result = await service.verify_code("m-1", "000000")
        assert result is False


# ===========================================================================
# SPEC-1268: Graceful degradation when ACS_SMS_FROM not configured
# ===========================================================================


class TestSpec1268GracefulSmsDegradation:
    """SPEC-1268: Graceful degradation when ACS_SMS_FROM not configured."""

    def test_spec1268_is_sms_available_false_when_not_configured(self):
        """SPEC-1268: is_sms_available returns False when ACS_SMS_FROM is empty."""
        with patch("src.multi_tenant.sms_mfa_service._ACS_SMS_FROM", ""):
            assert is_sms_available() is False

    def test_spec1268_is_sms_available_false_when_no_connection_string(self):
        """SPEC-1268: is_sms_available returns False when connection string is empty."""
        with (
            patch("src.multi_tenant.sms_mfa_service._ACS_SMS_FROM", "+12125551234"),
            patch("src.multi_tenant.sms_mfa_service._ACS_CONNECTION_STRING", ""),
        ):
            assert is_sms_available() is False

    def test_spec1268_is_sms_available_true_when_configured(self):
        """SPEC-1268: is_sms_available returns True when both are set."""
        with (
            patch("src.multi_tenant.sms_mfa_service._ACS_SMS_FROM", "+12125551234"),
            patch("src.multi_tenant.sms_mfa_service._ACS_CONNECTION_STRING", "endpoint=fake"),
        ):
            assert is_sms_available() is True

    @pytest.mark.asyncio
    async def test_spec1268_send_code_returns_false_when_unavailable(self):
        """SPEC-1268: send_code returns False gracefully when SMS not configured."""
        service = SmsMfaService(token_repo=AsyncMock())
        with patch("src.multi_tenant.sms_mfa_service.is_sms_available", return_value=False):
            result = await service.send_code("t-1", "m-1", "+12125551234")
        assert result is False


# ===========================================================================
# SPEC-1272: TOTP 6 digits, 30s interval, +/-1 window
# ===========================================================================


class TestSpec1272TotpParameters:
    """SPEC-1272: TOTP 6 digits, 30s interval, +/-1 window."""

    def test_spec1272_totp_digits_is_6(self):
        """SPEC-1272: _TOTP_DIGITS is 6."""
        assert _TOTP_DIGITS == 6

    def test_spec1272_totp_interval_is_30(self):
        """SPEC-1272: _TOTP_INTERVAL is 30 seconds."""
        assert _TOTP_INTERVAL == 30

    def test_spec1272_totp_valid_window_is_1(self):
        """SPEC-1272: _TOTP_VALID_WINDOW is 1 (accept +/-1 interval)."""
        assert _TOTP_VALID_WINDOW == 1

    def test_spec1272_verify_totp_accepts_current_code(self):
        """SPEC-1272: verify_totp accepts the current time-step code."""
        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret, digits=6, interval=30)
        code = totp.now()
        assert verify_totp(secret, code) is True

    def test_spec1272_verify_totp_rejects_wrong_code(self):
        """SPEC-1272: verify_totp rejects an obviously wrong code."""
        secret = generate_totp_secret()
        assert verify_totp(secret, "000000") is False

    def test_spec1272_verify_totp_accepts_previous_interval(self):
        """SPEC-1272: verify_totp accepts code from previous 30s interval (+/-1 window)."""
        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret, digits=6, interval=30)
        # Generate code for 30 seconds ago (previous interval)
        prev_code = totp.at(datetime.now(timezone.utc) - timedelta(seconds=30))
        assert verify_totp(secret, prev_code) is True


# ===========================================================================
# SPEC-1273: 10 backup codes, 8-char alphanumeric, no I/O/0/1
# ===========================================================================


class TestSpec1273BackupCodes:
    """SPEC-1273: 10 backup codes, 8-char alphanumeric, no I/O/0/1."""

    def test_spec1273_default_count_is_10(self):
        """SPEC-1273: _BACKUP_CODE_COUNT is 10."""
        assert _BACKUP_CODE_COUNT == 10

    def test_spec1273_default_length_is_8(self):
        """SPEC-1273: _BACKUP_CODE_LENGTH is 8."""
        assert _BACKUP_CODE_LENGTH == 8

    def test_spec1273_generates_10_codes(self):
        """SPEC-1273: generate_backup_codes() produces 10 codes by default."""
        codes = generate_backup_codes()
        assert len(codes) == 10

    def test_spec1273_each_code_is_8_chars(self):
        """SPEC-1273: Each backup code is exactly 8 characters."""
        codes = generate_backup_codes()
        for code in codes:
            assert len(code) == 8

    def test_spec1273_no_ambiguous_characters(self):
        """SPEC-1273: Codes exclude I, O, 0, 1 (ambiguity avoidance)."""
        excluded = set("IO01")
        codes = generate_backup_codes()
        for code in codes:
            assert not excluded.intersection(code), f"Code {code!r} contains excluded chars"

    def test_spec1273_alphanumeric_uppercase_and_digits(self):
        """SPEC-1273: Codes use uppercase letters (sans I/O) and digits (sans 0/1)."""
        allowed = set("ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
        codes = generate_backup_codes()
        for code in codes:
            assert set(code).issubset(allowed), f"Code {code!r} has invalid chars"

    def test_spec1273_codes_are_unique(self):
        """SPEC-1273: All 10 codes in a batch are unique."""
        codes = generate_backup_codes()
        assert len(set(codes)) == len(codes)

    def test_spec1273_hash_backup_code_is_sha256(self):
        """SPEC-1273: hash_backup_code uses SHA-256."""
        code = "ABCD2345"
        expected = hashlib.sha256(code.upper().encode()).hexdigest()
        assert hash_backup_code(code) == expected


# ===========================================================================
# SPEC-1276: TOTP seeds in Key Vault as user-{member_id}-totp-seed
# ===========================================================================


class TestSpec1276TotpKeyVaultStorage:
    """SPEC-1276: TOTP seeds in Key Vault as user-{member_id}-totp-seed."""

    @pytest.mark.asyncio
    async def test_spec1276_enrollment_stores_seed_in_key_vault(self):
        """SPEC-1276: start_enrollment stores TOTP seed as user-{member_id}-totp-seed."""
        mock_secret_svc = AsyncMock()
        mock_secret_svc.set_secret_raw = AsyncMock()
        service = MfaTotpService(secret_service=mock_secret_svc)

        member = {"id": "mem-abc-123", "email": "admin@test.com", "tenant_id": "t-1"}
        await service.start_enrollment(member)

        mock_secret_svc.set_secret_raw.assert_called_once()
        call_args = mock_secret_svc.set_secret_raw.call_args
        kv_name = call_args.args[0]
        assert kv_name == "user-mem-abc-123-totp-seed"

    @pytest.mark.asyncio
    async def test_spec1276_get_totp_secret_uses_correct_key_name(self):
        """SPEC-1276: _get_totp_secret uses user-{member_id}-totp-seed key name."""
        mock_secret_svc = AsyncMock()
        mock_secret_svc.get_secret_raw = AsyncMock(return_value="BASE32SECRET")
        service = MfaTotpService(secret_service=mock_secret_svc)

        result = await service._get_totp_secret("mem-xyz-789")

        mock_secret_svc.get_secret_raw.assert_called_once_with("user-mem-xyz-789-totp-seed")
        assert result == "BASE32SECRET"

    @pytest.mark.asyncio
    async def test_spec1276_disable_mfa_deletes_seed(self):
        """SPEC-1276: disable_mfa deletes the TOTP seed from Key Vault."""
        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret, digits=6, interval=30)
        code = totp.now()

        mock_secret_svc = AsyncMock()
        mock_secret_svc.get_secret_raw = AsyncMock(return_value=secret)
        mock_secret_svc.delete_secret_raw = AsyncMock()
        mock_team_repo = AsyncMock()
        mock_team_repo.update_member_fields = AsyncMock()

        service = MfaTotpService(
            secret_service=mock_secret_svc,
            team_repo=mock_team_repo,
        )
        member = {"id": "mem-del", "email": "del@test.com", "tenant_id": "t-1"}
        result = await service.disable_mfa(member, code)

        assert result is True
        mock_secret_svc.delete_secret_raw.assert_called_once_with("user-mem-del-totp-seed")

    @pytest.mark.asyncio
    async def test_spec1276_enrollment_returns_backup_codes(self):
        """SPEC-1276: start_enrollment returns backup codes and their hashes."""
        mock_secret_svc = AsyncMock()
        mock_secret_svc.set_secret_raw = AsyncMock()
        service = MfaTotpService(secret_service=mock_secret_svc)

        member = {"id": "mem-1", "email": "admin@test.com", "tenant_id": "t-1"}
        result = await service.start_enrollment(member)

        assert "backup_codes" in result
        assert "backup_code_hashes" in result
        assert len(result["backup_codes"]) == 10
        assert len(result["backup_code_hashes"]) == 10
        # Verify hashes match the codes
        for code, h in zip(result["backup_codes"], result["backup_code_hashes"]):
            assert hash_backup_code(code) == h
