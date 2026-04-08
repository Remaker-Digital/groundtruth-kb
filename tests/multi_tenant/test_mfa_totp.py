"""Tests for MFA/TOTP service — enrollment, verification, backup codes, session tokens.

Test IDs: MFA-01 → MFA-22

Validates:
    - TOTP secret generation and provisioning URIs
    - QR code data URL generation
    - TOTP code verification (valid + invalid)
    - Backup code generation, hashing, and verification
    - MFA session token creation and verification (round-trip, expired, invalid)
    - MfaTotpService enrollment, confirmation, verification, backup, disable flows
    - Module-level singleton lifecycle

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
import time
from unittest.mock import AsyncMock, MagicMock

import jwt
import pyotp
import pytest

from src.multi_tenant.mfa_totp import (
    MfaTotpService,
    _MFA_JWT_SECRET,
    _TOTP_DIGITS,
    _TOTP_INTERVAL,
    _TOTP_ISSUER,
    configure_mfa_service,
    create_mfa_session_token,
    generate_backup_codes,
    generate_provisioning_uri,
    generate_qr_code_data_url,
    generate_totp_secret,
    get_mfa_service,
    hash_backup_code,
    verify_backup_code,
    verify_mfa_session_token,
    verify_totp,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MEMBER_ID = "mem-abc-123"
_TENANT_ID = "tenant-xyz-789"
_EMAIL = "admin@example.com"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_member(
    *,
    mfa_enabled: bool = False,
    backup_hashes: list[str] | None = None,
    enrolled_at: str | None = None,
) -> dict:
    """Build a minimal team member document for testing."""
    member = {
        "id": _MEMBER_ID,
        "tenant_id": _TENANT_ID,
        "email": _EMAIL,
        "mfa_enabled": mfa_enabled,
    }
    if enrolled_at is not None:
        member["mfa_enrolled_at"] = enrolled_at
    if backup_hashes is not None:
        member["mfa_backup_code_hashes"] = backup_hashes
    return member


def _generate_valid_code(secret: str) -> str:
    """Generate a currently-valid TOTP code for the given secret."""
    totp = pyotp.TOTP(secret, digits=_TOTP_DIGITS, interval=_TOTP_INTERVAL)
    return totp.now()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_secret_service() -> AsyncMock:
    """Mock TenantSecretService with Key Vault operations."""
    svc = AsyncMock()
    svc.set_secret_raw = AsyncMock()
    svc.get_secret_raw = AsyncMock()
    svc.delete_secret_raw = AsyncMock()
    return svc


@pytest.fixture()
def mock_team_repo() -> AsyncMock:
    """Mock team repository with update_member_fields."""
    repo = AsyncMock()
    repo.update_member_fields = AsyncMock()
    return repo


@pytest.fixture()
def mfa_service(mock_secret_service, mock_team_repo) -> MfaTotpService:
    """MfaTotpService wired to mock dependencies."""
    return MfaTotpService(
        secret_service=mock_secret_service,
        team_repo=mock_team_repo,
    )


@pytest.fixture(autouse=True)
def _reset_singleton():
    """Reset module-level singleton between tests."""
    import src.multi_tenant.mfa_totp as mod

    original = mod._mfa_service
    yield
    mod._mfa_service = original


# ---------------------------------------------------------------------------
# MFA-01: generate_totp_secret
# ---------------------------------------------------------------------------


class TestGenerateTotpSecret:
    """TOTP secret generation."""

    def test_mfa_01_returns_32_char_base32_string(self):
        """MFA-01: generate_totp_secret returns a 32-character base32 string."""
        secret = generate_totp_secret()

        assert len(secret) == 32
        assert re.fullmatch(r"[A-Z2-7]+", secret), (
            f"Secret must be base32 (A-Z, 2-7), got: {secret}"
        )

    def test_mfa_01b_secrets_are_unique(self):
        """MFA-01b: Successive calls produce distinct secrets."""
        secrets = {generate_totp_secret() for _ in range(10)}
        assert len(secrets) == 10


# ---------------------------------------------------------------------------
# MFA-02: generate_provisioning_uri
# ---------------------------------------------------------------------------


class TestGenerateProvisioningUri:
    """Provisioning URI construction."""

    def test_mfa_02_uri_format(self):
        """MFA-02: Provisioning URI contains otpauth scheme, issuer, and email."""
        secret = generate_totp_secret()
        uri = generate_provisioning_uri(secret, _EMAIL)

        assert uri.startswith("otpauth://totp/")
        assert _TOTP_ISSUER in uri
        # Email may be URL-encoded (@ → %40)
        assert _EMAIL in uri or _EMAIL.replace("@", "%40") in uri
        assert f"secret={secret}" in uri


# ---------------------------------------------------------------------------
# MFA-03: generate_qr_code_data_url
# ---------------------------------------------------------------------------


class TestGenerateQrCodeDataUrl:
    """QR code data URL generation."""

    def test_mfa_03_data_url_prefix(self):
        """MFA-03: QR code output starts with data:image/png;base64, prefix."""
        uri = "otpauth://totp/AgentRed:test@example.com?secret=JBSWY3DPEHPK3PXP"
        data_url = generate_qr_code_data_url(uri)

        assert data_url.startswith("data:image/png;base64,")
        # Ensure there is actual base64 content after the prefix
        b64_part = data_url.split(",", 1)[1]
        assert len(b64_part) > 100


# ---------------------------------------------------------------------------
# MFA-04 / MFA-05: verify_totp
# ---------------------------------------------------------------------------


class TestVerifyTotp:
    """TOTP code verification."""

    def test_mfa_04_valid_code_passes(self):
        """MFA-04: A currently-valid TOTP code verifies successfully."""
        secret = generate_totp_secret()
        code = _generate_valid_code(secret)

        assert verify_totp(secret, code) is True

    def test_mfa_05_wrong_code_fails(self):
        """MFA-05: An incorrect TOTP code is rejected."""
        secret = generate_totp_secret()

        assert verify_totp(secret, "000000") is False


# ---------------------------------------------------------------------------
# MFA-06: generate_backup_codes
# ---------------------------------------------------------------------------


class TestGenerateBackupCodes:
    """Backup code generation."""

    def test_mfa_06_default_count_and_format(self):
        """MFA-06: Generates 10 codes, each 8 chars, uppercase+digits only (no I/O/0/1)."""
        codes = generate_backup_codes()

        assert len(codes) == 10
        forbidden = set("IO01")
        allowed = re.compile(r"^[ABCDEFGHJKLMNPQRSTUVWXYZ23456789]{8}$")
        for code in codes:
            assert len(code) == 8
            assert allowed.match(code), f"Code {code} contains forbidden characters"
            assert not (set(code) & forbidden), (
                f"Code {code} uses ambiguous characters"
            )

    def test_mfa_06b_custom_count(self):
        """MFA-06b: Custom count parameter is respected."""
        codes = generate_backup_codes(count=5)
        assert len(codes) == 5


# ---------------------------------------------------------------------------
# MFA-07: hash_backup_code
# ---------------------------------------------------------------------------


class TestHashBackupCode:
    """Backup code hashing."""

    def test_mfa_07_sha256_hex(self):
        """MFA-07: hash_backup_code returns a 64-char SHA-256 hex digest."""
        h = hash_backup_code("ABCD1234")

        assert len(h) == 64
        assert re.fullmatch(r"[0-9a-f]{64}", h)

    def test_mfa_07b_case_insensitive(self):
        """MFA-07b: Hashing is case-insensitive (uppercases before hashing)."""
        assert hash_backup_code("abcd1234") == hash_backup_code("ABCD1234")


# ---------------------------------------------------------------------------
# MFA-08: verify_backup_code
# ---------------------------------------------------------------------------


class TestVerifyBackupCode:
    """Backup code verification and consumption."""

    def test_mfa_08_valid_code_consumed(self):
        """MFA-08: Valid backup code is accepted and removed from hash list."""
        codes = generate_backup_codes(count=3)
        hashes = [hash_backup_code(c) for c in codes]

        valid, remaining = verify_backup_code(codes[1], hashes)

        assert valid is True
        assert len(remaining) == 2
        assert hash_backup_code(codes[1]) not in remaining

    def test_mfa_08b_invalid_code_rejected(self):
        """MFA-08b: Invalid code is rejected; hash list unchanged."""
        codes = generate_backup_codes(count=3)
        hashes = [hash_backup_code(c) for c in codes]

        valid, remaining = verify_backup_code("ZZZZZZZZ", hashes)

        assert valid is False
        assert remaining == hashes


# ---------------------------------------------------------------------------
# MFA-09 → MFA-12: MFA session tokens
# ---------------------------------------------------------------------------


class TestMfaSessionToken:
    """MFA session JWT creation and verification."""

    def test_mfa_09_round_trip(self):
        """MFA-09: create + verify round-trips correctly."""
        token = create_mfa_session_token(_MEMBER_ID, _EMAIL)
        payload = verify_mfa_session_token(token)

        assert payload is not None
        assert payload["sub"] == _MEMBER_ID
        assert payload["email"] == _EMAIL
        assert payload["type"] == "mfa_session"

    def test_mfa_10_expired_token_returns_none(self):
        """MFA-10: An expired MFA session token returns None."""
        expired_payload = {
            "sub": _MEMBER_ID,
            "email": _EMAIL,
            "type": "mfa_session",
            "iat": int(time.time()) - 36000,
            "exp": int(time.time()) - 1,
        }
        token = jwt.encode(expired_payload, _MFA_JWT_SECRET, algorithm="HS256")

        assert verify_mfa_session_token(token) is None

    def test_mfa_11_invalid_token_returns_none(self):
        """MFA-11: A tampered/invalid token returns None."""
        assert verify_mfa_session_token("not.a.jwt") is None

    def test_mfa_12_wrong_type_returns_none(self):
        """MFA-12: A JWT with type != 'mfa_session' returns None."""
        wrong_type_payload = {
            "sub": _MEMBER_ID,
            "email": _EMAIL,
            "type": "access_token",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        token = jwt.encode(wrong_type_payload, _MFA_JWT_SECRET, algorithm="HS256")

        assert verify_mfa_session_token(token) is None


# ---------------------------------------------------------------------------
# MFA-13 / MFA-14: MfaTotpService.get_enrollment_status
# ---------------------------------------------------------------------------


class TestGetEnrollmentStatus:
    """Service enrollment status queries."""

    @pytest.mark.asyncio
    async def test_mfa_13_enabled_member(self, mfa_service):
        """MFA-13: Returns mfa_enabled=True with enrollment details."""
        hashes = [hash_backup_code("CODE0001")]
        member = _make_member(
            mfa_enabled=True,
            enrolled_at="2026-02-17T10:00:00Z",
            backup_hashes=hashes,
        )

        status = await mfa_service.get_enrollment_status(member)

        assert status["mfa_enabled"] is True
        assert status["enrolled_at"] == "2026-02-17T10:00:00Z"
        assert status["backup_codes_remaining"] == 1

    @pytest.mark.asyncio
    async def test_mfa_14_not_enabled_member(self, mfa_service):
        """MFA-14: Returns mfa_enabled=False for unenrolled member."""
        member = _make_member(mfa_enabled=False)

        status = await mfa_service.get_enrollment_status(member)

        assert status["mfa_enabled"] is False
        assert status["enrolled_at"] is None
        assert status["backup_codes_remaining"] == 0


# ---------------------------------------------------------------------------
# MFA-15: MfaTotpService.start_enrollment
# ---------------------------------------------------------------------------


class TestStartEnrollment:
    """Service enrollment initiation."""

    @pytest.mark.asyncio
    async def test_mfa_15_returns_all_artifacts(self, mfa_service, mock_secret_service):
        """MFA-15: start_enrollment returns secret, QR code, URI, and backup codes."""
        member = _make_member()

        result = await mfa_service.start_enrollment(member)

        assert len(result["secret"]) == 32
        assert result["qr_code_data_url"].startswith("data:image/png;base64,")
        assert result["provisioning_uri"].startswith("otpauth://totp/")
        assert len(result["backup_codes"]) == 10
        assert len(result["backup_code_hashes"]) == 10

        # Verify Key Vault storage
        kv_name = f"user-{_MEMBER_ID}-totp-seed"
        mock_secret_service.set_secret_raw.assert_awaited_once_with(
            kv_name, result["secret"]
        )


# ---------------------------------------------------------------------------
# MFA-16 / MFA-17: MfaTotpService.confirm_enrollment
# ---------------------------------------------------------------------------


class TestConfirmEnrollment:
    """Service enrollment confirmation."""

    @pytest.mark.asyncio
    async def test_mfa_16_valid_code_confirms(
        self, mfa_service, mock_secret_service, mock_team_repo
    ):
        """MFA-16: Valid TOTP code confirms enrollment and updates member."""
        secret = generate_totp_secret()
        mock_secret_service.get_secret_raw.return_value = secret
        code = _generate_valid_code(secret)
        backup_hashes = ["hash1", "hash2"]
        member = _make_member()

        result = await mfa_service.confirm_enrollment(member, code, backup_hashes)

        assert result is True
        mock_team_repo.update_member_fields.assert_awaited_once()
        call_kwargs = mock_team_repo.update_member_fields.call_args.kwargs
        assert call_kwargs["updates"]["mfa_enabled"] is True
        assert call_kwargs["updates"]["mfa_backup_code_hashes"] == backup_hashes
        assert "mfa_enrolled_at" in call_kwargs["updates"]

    @pytest.mark.asyncio
    async def test_mfa_17_invalid_code_rejects(
        self, mfa_service, mock_secret_service, mock_team_repo
    ):
        """MFA-17: Invalid TOTP code returns False, no member update."""
        secret = generate_totp_secret()
        mock_secret_service.get_secret_raw.return_value = secret
        member = _make_member()

        result = await mfa_service.confirm_enrollment(member, "000000", ["hash1"])

        assert result is False
        mock_team_repo.update_member_fields.assert_not_awaited()


# ---------------------------------------------------------------------------
# MFA-18 / MFA-19: MfaTotpService.verify_code
# ---------------------------------------------------------------------------


class TestVerifyCode:
    """Service TOTP code verification at login."""

    @pytest.mark.asyncio
    async def test_mfa_18_valid_code_returns_token(
        self, mfa_service, mock_secret_service
    ):
        """MFA-18: Valid code returns dict with mfa_token JWT."""
        secret = generate_totp_secret()
        mock_secret_service.get_secret_raw.return_value = secret
        code = _generate_valid_code(secret)
        member = _make_member(mfa_enabled=True)

        result = await mfa_service.verify_code(member, code)

        assert result is not None
        assert "mfa_token" in result
        # Verify the returned token is a valid JWT
        payload = verify_mfa_session_token(result["mfa_token"])
        assert payload is not None
        assert payload["sub"] == _MEMBER_ID

    @pytest.mark.asyncio
    async def test_mfa_19_invalid_code_returns_none(
        self, mfa_service, mock_secret_service
    ):
        """MFA-19: Invalid code returns None."""
        secret = generate_totp_secret()
        mock_secret_service.get_secret_raw.return_value = secret
        member = _make_member(mfa_enabled=True)

        result = await mfa_service.verify_code(member, "000000")

        assert result is None


# ---------------------------------------------------------------------------
# MFA-20: MfaTotpService.verify_backup
# ---------------------------------------------------------------------------


class TestVerifyBackup:
    """Service backup code verification at login."""

    @pytest.mark.asyncio
    async def test_mfa_20_valid_backup_consumes_code(
        self, mfa_service, mock_team_repo
    ):
        """MFA-20: Valid backup code returns token + remaining count, updates repo."""
        codes = generate_backup_codes(count=3)
        hashes = [hash_backup_code(c) for c in codes]
        member = _make_member(mfa_enabled=True, backup_hashes=hashes)

        result = await mfa_service.verify_backup(member, codes[0])

        assert result is not None
        assert "mfa_token" in result
        assert result["backup_codes_remaining"] == 2

        # Verify repo was updated with remaining hashes
        mock_team_repo.update_member_fields.assert_awaited_once()
        call_kwargs = mock_team_repo.update_member_fields.call_args.kwargs
        remaining = call_kwargs["updates"]["mfa_backup_code_hashes"]
        assert len(remaining) == 2

    @pytest.mark.asyncio
    async def test_mfa_20b_invalid_backup_returns_none(self, mfa_service):
        """MFA-20b: Invalid backup code returns None."""
        hashes = [hash_backup_code("VALIDCODE")]
        member = _make_member(mfa_enabled=True, backup_hashes=hashes)

        result = await mfa_service.verify_backup(member, "BADCODE1")

        assert result is None


# ---------------------------------------------------------------------------
# MFA-21: MfaTotpService.disable_mfa
# ---------------------------------------------------------------------------


class TestDisableMfa:
    """Service MFA disable flow."""

    @pytest.mark.asyncio
    async def test_mfa_21_valid_code_disables(
        self, mfa_service, mock_secret_service, mock_team_repo
    ):
        """MFA-21: Valid code deletes KV seed and clears member MFA fields."""
        secret = generate_totp_secret()
        mock_secret_service.get_secret_raw.return_value = secret
        code = _generate_valid_code(secret)
        member = _make_member(mfa_enabled=True)

        result = await mfa_service.disable_mfa(member, code)

        assert result is True

        # Key Vault seed deleted
        kv_name = f"user-{_MEMBER_ID}-totp-seed"
        mock_secret_service.delete_secret_raw.assert_awaited_once_with(kv_name)

        # Member fields cleared
        call_kwargs = mock_team_repo.update_member_fields.call_args.kwargs
        assert call_kwargs["updates"]["mfa_enabled"] is False
        assert call_kwargs["updates"]["mfa_enrolled_at"] is None
        assert call_kwargs["updates"]["mfa_backup_code_hashes"] == []

    @pytest.mark.asyncio
    async def test_mfa_21b_invalid_code_rejects(
        self, mfa_service, mock_secret_service, mock_team_repo
    ):
        """MFA-21b: Invalid code returns False, no deletion occurs."""
        secret = generate_totp_secret()
        mock_secret_service.get_secret_raw.return_value = secret
        member = _make_member(mfa_enabled=True)

        result = await mfa_service.disable_mfa(member, "000000")

        assert result is False
        mock_secret_service.delete_secret_raw.assert_not_awaited()
        mock_team_repo.update_member_fields.assert_not_awaited()


# ---------------------------------------------------------------------------
# MFA-22: Module-level singleton
# ---------------------------------------------------------------------------


class TestSingleton:
    """Module-level configure/get lifecycle."""

    def test_mfa_22_configure_and_get(self):
        """MFA-22: configure_mfa_service creates singleton retrievable via get."""
        svc = configure_mfa_service(
            secret_service=MagicMock(),
            team_repo=MagicMock(),
        )

        assert svc is get_mfa_service()
        assert isinstance(svc, MfaTotpService)

    def test_mfa_22b_get_without_configure_raises(self):
        """MFA-22b: get_mfa_service raises RuntimeError before configure."""
        import src.multi_tenant.mfa_totp as mod

        mod._mfa_service = None

        with pytest.raises(RuntimeError, match="not configured"):
            get_mfa_service()
