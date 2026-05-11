# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Two-stage 2FA authentication endpoints for admin console.

After magic link verification, admins face a 2FA challenge (TOTP or SMS)
before receiving a full session JWT.

Flow:
    1. Magic link verify → pending_2fa JWT (10-min, type "pending_2fa_session")
    2. POST /api/auth/2fa/totp/verify → consumes pending JWT + TOTP code
       → issues full 8-hour session JWT
    3. Non-admins (escalation_agent, viewer) skip 2FA entirely.
    4. Admins with mfa_opt_out skip 2FA.

Endpoints:
    POST /api/auth/2fa/totp/verify       — Verify TOTP code
    POST /api/auth/2fa/totp/backup-verify — Verify backup code
    POST /api/auth/2fa/sms/request        — Request SMS OTP
    POST /api/auth/2fa/sms/verify         — Verify SMS OTP code

Brute-force mitigation:
    5 failed attempts per pending_2fa token. The token has a 10-minute
    lifetime, so after exhaustion the user must request a new magic link.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.multi_tenant.cosmos_schema import TeamMemberRole

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth/2fa",
    tags=["2FA Auth"],
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_PENDING_JWT_SECRET = os.environ.get(
    "MAGIC_LINK_JWT_SECRET",
    os.environ.get("SHOPIFY_API_SECRET", "agent-red-magic-link-default-secret"),
)

_PENDING_TOKEN_LIFETIME_MINUTES = 10
_MAX_FAILED_ATTEMPTS = 5

# In-memory failed attempt tracking (per pending token)
_failed_attempts: dict[str, int] = {}

# Admin-level roles that require 2FA
_ADMIN_ROLES = {
    TeamMemberRole.SUPERADMIN.value,
    TeamMemberRole.ADMIN.value,
    "superadmin",
    "admin",
}

# Service dependencies (injected during app startup)
_mfa_totp_service: Any = None
_sms_mfa_service: Any = None
_team_repo: Any = None


def configure_2fa_services(
    mfa_totp_service: Any = None,
    sms_mfa_service: Any = None,
    team_repo: Any = None,
) -> None:
    """Inject service dependencies. Called once at app startup."""
    global _mfa_totp_service, _sms_mfa_service, _team_repo
    _mfa_totp_service = mfa_totp_service
    _sms_mfa_service = sms_mfa_service
    _team_repo = team_repo


# ---------------------------------------------------------------------------
# Pending 2FA JWT helpers
# ---------------------------------------------------------------------------


def requires_2fa(role: str | None, member_doc: dict | None = None) -> bool:
    """Determine if a role requires 2FA challenge.

    Admin-level roles require 2FA unless:
      - The member has mfa_opt_out=True (granted by superadmin)
      - The member has no MFA enrolled (new admin bootstrap)

    Non-admin roles never require 2FA.
    """
    if role not in _ADMIN_ROLES:
        return False

    if member_doc:
        # Superadmin-controlled opt-out
        if member_doc.get("mfa_opt_out", False):
            return False
        # No MFA enrolled → can't challenge (new admin bootstrap)
        if not member_doc.get("mfa_enabled", False):
            return False

    return True


def create_pending_2fa_token(
    tenant_id: str,
    email: str,
    member_id: str,
    role: str,
) -> tuple[str, str]:
    """Create a short-lived pending 2FA JWT (10 minutes).

    Returns (token, expires_at_iso).
    """
    now = datetime.now(UTC)
    exp = now + timedelta(minutes=_PENDING_TOKEN_LIFETIME_MINUTES)
    payload = {
        "sub": tenant_id,
        "email": email,
        "member_id": member_id,
        "role": role,
        "type": "pending_2fa_session",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, _PENDING_JWT_SECRET, algorithm="HS256")
    return token, exp.isoformat()


def verify_pending_2fa_token(token: str) -> dict | None:
    """Verify a pending 2FA JWT. Returns payload or None."""
    try:
        payload = jwt.decode(token, _PENDING_JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "pending_2fa_session":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("Pending 2FA token expired")
        return None
    except jwt.InvalidTokenError:
        logger.debug("Invalid pending 2FA token")
        return None


def _check_brute_force(token_fingerprint: str) -> bool:
    """Return True if brute-force limit is exceeded."""
    count = _failed_attempts.get(token_fingerprint, 0)
    return count >= _MAX_FAILED_ATTEMPTS


def _record_failed_attempt(token_fingerprint: str) -> int:
    """Record a failed 2FA attempt. Returns new count."""
    count = _failed_attempts.get(token_fingerprint, 0) + 1
    _failed_attempts[token_fingerprint] = count
    return count


def _clear_attempts(token_fingerprint: str) -> None:
    """Clear failed attempts on successful verification."""
    _failed_attempts.pop(token_fingerprint, None)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class TotpVerifyRequest(BaseModel):
    """TOTP verification request."""
    pending_token: str = Field(description="Pending 2FA session JWT")
    code: str = Field(description="6-digit TOTP code from authenticator app")


class BackupVerifyRequest(BaseModel):
    """Backup code verification request."""
    pending_token: str = Field(description="Pending 2FA session JWT")
    code: str = Field(description="8-character backup code")


class SmsRequestBody(BaseModel):
    """Request SMS OTP delivery."""
    pending_token: str = Field(description="Pending 2FA session JWT")


class SmsVerifyRequest(BaseModel):
    """SMS OTP verification request."""
    pending_token: str = Field(description="Pending 2FA session JWT")
    code: str = Field(description="6-digit SMS OTP code")


class TwoFaSessionResponse(BaseModel):
    """Full session response after successful 2FA."""
    session_token: str
    tenant_id: str
    email: str
    expires_at: str


# ---------------------------------------------------------------------------
# Helper: issue full session after 2FA
# ---------------------------------------------------------------------------


def _issue_full_session(payload: dict) -> JSONResponse:
    """Issue a full 8-hour session JWT from a verified pending 2FA payload."""
    from src.multi_tenant.magic_link_auth import create_magic_link_session_token

    session_token, expires_at = create_magic_link_session_token(
        tenant_id=payload["sub"],
        email=payload["email"],
        member_id=payload.get("member_id"),
        role=payload.get("role"),
    )

    _clear_attempts(payload["sub"] + payload.get("member_id", ""))

    return JSONResponse(content={
        "session_token": session_token,
        "tenant_id": payload["sub"],
        "email": payload["email"],
        "expires_at": expires_at,
    })


def _error_response(status_code: int, error: str, message: str) -> JSONResponse:
    """Standard error response."""
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "message": message},
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/totp/verify",
    summary="Verify TOTP code and issue full session",
)
async def verify_totp_2fa(body: TotpVerifyRequest) -> JSONResponse:
    """Verify a TOTP code against the admin's enrolled secret."""
    payload = verify_pending_2fa_token(body.pending_token)
    if not payload:
        return _error_response(401, "invalid_token",
            "Pending 2FA session expired or invalid. Please request a new sign-in link.")

    fingerprint = payload["sub"] + payload.get("member_id", "")
    if _check_brute_force(fingerprint):
        return _error_response(429, "too_many_attempts",
            "Too many failed attempts. Please request a new sign-in link.")

    if not _mfa_totp_service or not _team_repo:
        return _error_response(503, "service_unavailable",
            "2FA service not configured.")

    member_id = payload.get("member_id")
    if not member_id:
        return _error_response(400, "invalid_request",
            "Pending token missing member identity.")

    try:
        member_doc = await _team_repo.read(payload["sub"], member_id)
        if not member_doc or not member_doc.get("mfa_enabled"):
            return _error_response(400, "mfa_not_enrolled",
                "MFA is not enrolled for this account.")

        # Get TOTP secret from Key Vault
        from src.multi_tenant.mfa_totp import verify_totp
        secret = await _mfa_totp_service._secret_service.get_secret(
            payload["sub"], f"user-{member_id}-totp-seed",
        )
        if not secret:
            return _error_response(500, "secret_not_found",
                "TOTP secret not found. Please re-enroll.")

        if verify_totp(secret, body.code):
            logger.info("TOTP 2FA verified: member=%s", member_id)
            return _issue_full_session(payload)
        else:
            remaining = _MAX_FAILED_ATTEMPTS - _record_failed_attempt(fingerprint)
            logger.warning("TOTP 2FA failed: member=%s remaining=%d", member_id, remaining)
            return _error_response(401, "invalid_code",
                f"Invalid verification code. {remaining} attempts remaining.")

    except Exception:
        logger.exception("Error during TOTP 2FA verification")
        return _error_response(500, "server_error",
            "An unexpected error occurred. Please try again.")


@router.post(
    "/totp/backup-verify",
    summary="Verify backup code and issue full session",
)
async def verify_backup_2fa(body: BackupVerifyRequest) -> JSONResponse:
    """Verify a backup code and consume it."""
    payload = verify_pending_2fa_token(body.pending_token)
    if not payload:
        return _error_response(401, "invalid_token",
            "Pending 2FA session expired or invalid. Please request a new sign-in link.")

    fingerprint = payload["sub"] + payload.get("member_id", "")
    if _check_brute_force(fingerprint):
        return _error_response(429, "too_many_attempts",
            "Too many failed attempts. Please request a new sign-in link.")

    if not _team_repo:
        return _error_response(503, "service_unavailable",
            "2FA service not configured.")

    member_id = payload.get("member_id")
    if not member_id:
        return _error_response(400, "invalid_request",
            "Pending token missing member identity.")

    try:
        member_doc = await _team_repo.read(payload["sub"], member_id)
        if not member_doc:
            return _error_response(400, "member_not_found",
                "Team member not found.")

        from src.multi_tenant.mfa_totp import verify_backup_code
        hashes = member_doc.get("mfa_backup_code_hashes", [])
        valid, remaining_hashes = verify_backup_code(body.code, hashes)

        if valid:
            # Update the member doc to remove the used backup code
            await _team_repo.update_member_fields(
                payload["sub"], member_id,
                {"mfa_backup_code_hashes": remaining_hashes},
            )
            logger.info(
                "Backup code 2FA verified: member=%s remaining=%d",
                member_id, len(remaining_hashes),
            )
            return _issue_full_session(payload)
        else:
            remaining = _MAX_FAILED_ATTEMPTS - _record_failed_attempt(fingerprint)
            logger.warning("Backup code 2FA failed: member=%s remaining=%d", member_id, remaining)
            return _error_response(401, "invalid_code",
                f"Invalid backup code. {remaining} attempts remaining.")

    except Exception:
        logger.exception("Error during backup code 2FA verification")
        return _error_response(500, "server_error",
            "An unexpected error occurred. Please try again.")


@router.post(
    "/sms/request",
    summary="Request SMS OTP delivery",
)
async def request_sms_otp(body: SmsRequestBody) -> JSONResponse:
    """Send a 6-digit OTP code to the admin's verified phone number."""
    payload = verify_pending_2fa_token(body.pending_token)
    if not payload:
        return _error_response(401, "invalid_token",
            "Pending 2FA session expired or invalid. Please request a new sign-in link.")

    if not _sms_mfa_service or not _team_repo:
        return _error_response(503, "sms_unavailable",
            "SMS verification is not available.")

    member_id = payload.get("member_id")
    if not member_id:
        return _error_response(400, "invalid_request",
            "Pending token missing member identity.")

    try:
        member_doc = await _team_repo.read(payload["sub"], member_id)
        if not member_doc:
            return _error_response(400, "member_not_found",
                "Team member not found.")

        phone = member_doc.get("phone_number")
        if not phone or not member_doc.get("phone_verified"):
            return _error_response(400, "phone_not_verified",
                "No verified phone number on file. Use TOTP instead.")

        sent = await _sms_mfa_service.send_code(
            tenant_id=payload["sub"],
            member_id=member_id,
            phone_number=phone,
        )
        if sent:
            return JSONResponse(content={
                "message": "Verification code sent.",
                "phone_hint": phone[:3] + "***" + phone[-2:],
            })
        else:
            return _error_response(503, "sms_send_failed",
                "Failed to send SMS. Please try TOTP instead.")

    except Exception:
        logger.exception("Error sending SMS OTP")
        return _error_response(500, "server_error",
            "An unexpected error occurred. Please try again.")


@router.post(
    "/sms/verify",
    summary="Verify SMS OTP code and issue full session",
)
async def verify_sms_otp(body: SmsVerifyRequest) -> JSONResponse:
    """Verify a 6-digit SMS OTP code."""
    payload = verify_pending_2fa_token(body.pending_token)
    if not payload:
        return _error_response(401, "invalid_token",
            "Pending 2FA session expired or invalid. Please request a new sign-in link.")

    fingerprint = payload["sub"] + payload.get("member_id", "")
    if _check_brute_force(fingerprint):
        return _error_response(429, "too_many_attempts",
            "Too many failed attempts. Please request a new sign-in link.")

    if not _sms_mfa_service:
        return _error_response(503, "sms_unavailable",
            "SMS verification is not available.")

    member_id = payload.get("member_id")
    if not member_id:
        return _error_response(400, "invalid_request",
            "Pending token missing member identity.")

    try:
        valid = await _sms_mfa_service.verify_code(member_id, body.code)

        if valid:
            logger.info("SMS OTP 2FA verified: member=%s", member_id)
            return _issue_full_session(payload)
        else:
            remaining = _MAX_FAILED_ATTEMPTS - _record_failed_attempt(fingerprint)
            logger.warning("SMS OTP 2FA failed: member=%s remaining=%d", member_id, remaining)
            return _error_response(401, "invalid_code",
                f"Invalid verification code. {remaining} attempts remaining.")

    except Exception:
        logger.exception("Error during SMS OTP 2FA verification")
        return _error_response(500, "server_error",
            "An unexpected error occurred. Please try again.")
