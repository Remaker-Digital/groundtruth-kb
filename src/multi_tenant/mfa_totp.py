"""
MFA/TOTP service — RFC 6238 time-based one-time password authentication.

Provides TOTP enrollment, verification, backup codes, and MFA session
token management for the Provider SPA Console (SUPERADMIN role).

TOTP seeds are stored per-user in Azure Key Vault via TenantSecretService
with the naming convention ``user-{team_member_id}-totp-seed``.

MFA session tokens are JWTs signed with HS256 using a per-deployment
secret from the MFA_JWT_SECRET environment variable.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import base64
import hashlib
import io
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import pyotp
import qrcode
import qrcode.constants

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# JWT secret for MFA session tokens — MUST be set in production
_MFA_JWT_SECRET = os.environ.get("MFA_JWT_SECRET", "dev-mfa-secret-change-in-production")

# MFA session token lifetime: 8 hours
_MFA_TOKEN_LIFETIME_HOURS = 8

# TOTP parameters
_TOTP_ISSUER = "AgentRed"
_TOTP_DIGITS = 6
_TOTP_INTERVAL = 30  # seconds
_TOTP_VALID_WINDOW = 1  # accept codes ±1 interval (30s tolerance)

# Backup code parameters
_BACKUP_CODE_COUNT = 10
_BACKUP_CODE_LENGTH = 8  # characters


# ---------------------------------------------------------------------------
# TOTP operations
# ---------------------------------------------------------------------------


def generate_totp_secret() -> str:
    """Generate a 32-byte base32 TOTP secret suitable for authenticator apps."""
    return pyotp.random_base32(length=32)


def generate_provisioning_uri(secret: str, email: str) -> str:
    """Build an ``otpauth://`` URI for authenticator app enrollment.

    Args:
        secret: Base32-encoded TOTP secret.
        email: User's email address (displayed in authenticator app).

    Returns:
        An ``otpauth://totp/AgentRed:{email}?...`` URI.
    """
    totp = pyotp.TOTP(
        secret,
        digits=_TOTP_DIGITS,
        interval=_TOTP_INTERVAL,
    )
    return totp.provisioning_uri(
        name=email,
        issuer_name=_TOTP_ISSUER,
    )


def generate_qr_code_data_url(uri: str) -> str:
    """Generate a QR code PNG as a base64 data URL.

    Args:
        uri: The ``otpauth://`` URI to encode.

    Returns:
        A ``data:image/png;base64,...`` string for ``<img src=...>``.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against the given secret.

    Accepts codes within ±1 interval window (±30s tolerance).

    Args:
        secret: Base32-encoded TOTP secret.
        code: 6-digit TOTP code from the authenticator app.

    Returns:
        True if the code is valid.
    """
    totp = pyotp.TOTP(
        secret,
        digits=_TOTP_DIGITS,
        interval=_TOTP_INTERVAL,
    )
    return totp.verify(code, valid_window=_TOTP_VALID_WINDOW)


# ---------------------------------------------------------------------------
# Backup codes
# ---------------------------------------------------------------------------


def generate_backup_codes(count: int = _BACKUP_CODE_COUNT) -> list[str]:
    """Generate a list of single-use backup codes.

    Each code is an 8-character alphanumeric string (uppercase + digits).

    Args:
        count: Number of codes to generate.

    Returns:
        List of plaintext backup codes.
    """
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no I/O/0/1 for clarity
    return [
        "".join(secrets.choice(alphabet) for _ in range(_BACKUP_CODE_LENGTH))
        for _ in range(count)
    ]


def hash_backup_code(code: str) -> str:
    """SHA-256 hash a backup code for storage.

    Args:
        code: Plaintext backup code.

    Returns:
        Hex-encoded SHA-256 hash.
    """
    return hashlib.sha256(code.upper().encode()).hexdigest()


def verify_backup_code(
    code: str,
    hashes: list[str],
) -> tuple[bool, list[str]]:
    """Verify a backup code and remove it from the hash list.

    Args:
        code: Plaintext backup code to verify.
        hashes: List of SHA-256 hashes of remaining valid codes.

    Returns:
        Tuple of (valid, remaining_hashes). If valid, the matched hash
        is removed from the returned list.
    """
    code_hash = hash_backup_code(code)
    if code_hash in hashes:
        remaining = [h for h in hashes if h != code_hash]
        return True, remaining
    return False, hashes


# ---------------------------------------------------------------------------
# MFA session token (JWT)
# ---------------------------------------------------------------------------


def create_mfa_session_token(
    team_member_id: str,
    email: str,
) -> str:
    """Create an 8-hour MFA session JWT.

    The token is returned to the frontend after successful TOTP verification
    and must be included in subsequent requests as ``X-MFA-Token``.

    Args:
        team_member_id: Team member's document ID.
        email: Team member's email address.

    Returns:
        Signed JWT string.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": team_member_id,
        "email": email,
        "type": "mfa_session",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=_MFA_TOKEN_LIFETIME_HOURS)).timestamp()),
    }
    return jwt.encode(payload, _MFA_JWT_SECRET, algorithm="HS256")


def verify_mfa_session_token(token: str) -> dict[str, Any] | None:
    """Verify an MFA session JWT.

    Args:
        token: The JWT string from the ``X-MFA-Token`` header.

    Returns:
        Decoded payload dict if valid, None if expired or invalid.
    """
    try:
        payload = jwt.decode(
            token,
            _MFA_JWT_SECRET,
            algorithms=["HS256"],
        )
        if payload.get("type") != "mfa_session":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("MFA session token expired")
        return None
    except jwt.InvalidTokenError:
        logger.debug("MFA session token invalid")
        return None


# ---------------------------------------------------------------------------
# MFA service (orchestrates Key Vault + team member ops)
# ---------------------------------------------------------------------------


class MfaTotpService:
    """Orchestrates MFA enrollment, verification, and session management.

    Combines TOTP operations with Key Vault storage for TOTP seeds
    and team member document updates for enrollment state.
    """

    def __init__(
        self,
        secret_service: Any | None = None,
        team_repo: Any | None = None,
    ) -> None:
        self._secret_service = secret_service
        self._team_repo = team_repo

    async def get_enrollment_status(self, member: dict[str, Any]) -> dict[str, Any]:
        """Get MFA enrollment status for a team member.

        Args:
            member: Team member document.

        Returns:
            Dict with mfa_enabled, enrolled_at, backup_codes_remaining.
        """
        return {
            "mfa_enabled": member.get("mfa_enabled", False),
            "enrolled_at": member.get("mfa_enrolled_at"),
            "backup_codes_remaining": len(member.get("mfa_backup_code_hashes", [])),
        }

    async def start_enrollment(
        self,
        member: dict[str, Any],
    ) -> dict[str, Any]:
        """Start MFA enrollment — generate secret, QR code, and backup codes.

        The secret is stored in Key Vault immediately. The enrollment is not
        confirmed until the user provides their first valid TOTP code via
        ``confirm_enrollment()``.

        Args:
            member: Team member document.

        Returns:
            Dict with secret, qr_code_data_url, provisioning_uri, backup_codes.
        """
        member_id = member.get("id", "")
        email = member.get("email", "unknown")

        # Generate TOTP secret and store in Key Vault
        secret = generate_totp_secret()

        if self._secret_service:
            kv_name = f"user-{member_id}-totp-seed"
            await self._secret_service.set_secret_raw(kv_name, secret)
            logger.info("TOTP seed stored in Key Vault for member %s", email)

        # Generate enrollment artifacts
        uri = generate_provisioning_uri(secret, email)
        qr_data_url = generate_qr_code_data_url(uri)
        backup_codes = generate_backup_codes()

        return {
            "secret": secret,
            "qr_code_data_url": qr_data_url,
            "provisioning_uri": uri,
            "backup_codes": backup_codes,
            "backup_code_hashes": [hash_backup_code(c) for c in backup_codes],
        }

    async def confirm_enrollment(
        self,
        member: dict[str, Any],
        code: str,
        backup_code_hashes: list[str],
    ) -> bool:
        """Confirm MFA enrollment with the first valid TOTP code.

        Updates the team member document with mfa_enabled=True,
        enrollment timestamp, and hashed backup codes.

        Args:
            member: Team member document.
            code: 6-digit TOTP code from the authenticator app.
            backup_code_hashes: SHA-256 hashes of the backup codes
                generated during start_enrollment.

        Returns:
            True if the code is valid and enrollment is confirmed.
        """
        member_id = member.get("id", "")
        secret = await self._get_totp_secret(member_id)
        if not secret:
            return False

        if not verify_totp(secret, code):
            return False

        # Update team member document
        if self._team_repo:
            now = datetime.now(timezone.utc).isoformat()
            await self._team_repo.update_member_fields(
                tenant_id=member["tenant_id"],
                member_id=member_id,
                updates={
                    "mfa_enabled": True,
                    "mfa_enrolled_at": now,
                    "mfa_backup_code_hashes": backup_code_hashes,
                },
            )
            logger.info("MFA enrollment confirmed for %s", member.get("email"))

        return True

    async def verify_code(
        self,
        member: dict[str, Any],
        code: str,
    ) -> dict[str, Any] | None:
        """Verify a TOTP code at login time.

        If valid, returns an MFA session token.

        Args:
            member: Team member document.
            code: 6-digit TOTP code.

        Returns:
            Dict with mfa_token if valid, None if invalid.
        """
        member_id = member.get("id", "")
        secret = await self._get_totp_secret(member_id)
        if not secret:
            return None

        if not verify_totp(secret, code):
            return None

        token = create_mfa_session_token(member_id, member.get("email", ""))
        return {"mfa_token": token}

    async def verify_backup(
        self,
        member: dict[str, Any],
        code: str,
    ) -> dict[str, Any] | None:
        """Verify a backup code at login time.

        Consumes the backup code (removes its hash). Returns an MFA
        session token if valid.

        Args:
            member: Team member document.
            code: 8-character backup code.

        Returns:
            Dict with mfa_token and backup_codes_remaining, or None.
        """
        hashes = member.get("mfa_backup_code_hashes", [])
        valid, remaining = verify_backup_code(code, hashes)
        if not valid:
            return None

        # Update remaining hashes
        if self._team_repo:
            await self._team_repo.update_member_fields(
                tenant_id=member["tenant_id"],
                member_id=member.get("id", ""),
                updates={"mfa_backup_code_hashes": remaining},
            )

        token = create_mfa_session_token(
            member.get("id", ""),
            member.get("email", ""),
        )
        return {
            "mfa_token": token,
            "backup_codes_remaining": len(remaining),
        }

    async def disable_mfa(
        self,
        member: dict[str, Any],
        code: str,
    ) -> bool:
        """Disable MFA for a team member (requires valid TOTP code).

        Removes the TOTP seed from Key Vault and clears MFA fields
        on the team member document.

        Args:
            member: Team member document.
            code: 6-digit TOTP code to confirm identity.

        Returns:
            True if MFA was successfully disabled.
        """
        member_id = member.get("id", "")
        secret = await self._get_totp_secret(member_id)
        if not secret:
            return False

        if not verify_totp(secret, code):
            return False

        # Delete seed from Key Vault
        if self._secret_service:
            kv_name = f"user-{member_id}-totp-seed"
            try:
                await self._secret_service.delete_secret_raw(kv_name)
            except Exception:
                logger.warning("Failed to delete TOTP seed from Key Vault for %s", member_id)

        # Clear MFA fields on team member
        if self._team_repo:
            await self._team_repo.update_member_fields(
                tenant_id=member["tenant_id"],
                member_id=member_id,
                updates={
                    "mfa_enabled": False,
                    "mfa_enrolled_at": None,
                    "mfa_backup_code_hashes": [],
                },
            )
            logger.info("MFA disabled for %s", member.get("email"))

        return True

    async def _get_totp_secret(self, member_id: str) -> str | None:
        """Retrieve TOTP secret from Key Vault."""
        if not self._secret_service:
            return None

        kv_name = f"user-{member_id}-totp-seed"
        try:
            return await self._secret_service.get_secret_raw(kv_name)
        except Exception:
            logger.debug("TOTP secret not found for member %s", member_id[:8])
            return None


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_mfa_service: MfaTotpService | None = None


def configure_mfa_service(
    secret_service: Any | None = None,
    team_repo: Any | None = None,
) -> MfaTotpService:
    """Create and store the module-level MfaTotpService singleton."""
    global _mfa_service  # noqa: PLW0603
    _mfa_service = MfaTotpService(
        secret_service=secret_service,
        team_repo=team_repo,
    )
    logger.info("MfaTotpService configured")
    return _mfa_service


def get_mfa_service() -> MfaTotpService:
    """Get the module-level MfaTotpService singleton."""
    if _mfa_service is None:
        raise RuntimeError("MfaTotpService not configured — call configure_mfa_service() first")
    return _mfa_service
