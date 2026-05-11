# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPA Emergency Key Recovery (SPEC-1678).

Provides an *unauthenticated* endpoint for platform admins who have lost
their API key. Recovery requires a valid backup code (generated via
SPEC-1675). On success, a new key is generated and emailed to the admin —
the key is NEVER returned in the HTTP response.

Endpoint:
    POST /api/auth/spa-recovery/recover

Security properties:
    - Rate-limited: 3 attempts per 15 min per IP
    - Always returns 200 (prevents email/code enumeration)
    - Backup code is single-use (consumed on success)
    - New key delivered only via email
    - Audit logged as SECURITY_EVENT

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth/spa-recovery",
    tags=["SPA Recovery"],
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_RATE_WINDOW = 900.0  # 15 minutes
_RATE_MAX = 3

_GENERIC_RESPONSE = (
    "If your email and backup code are valid, a new API key has been "
    "sent to your registered email address."
)


# ---------------------------------------------------------------------------
# Module-level service references (set at startup)
# ---------------------------------------------------------------------------

_platform_admin_repo = None
_audit_repo = None


def configure_spa_recovery(
    platform_admin_repo=None,
    audit_repo=None,
) -> None:
    """Wire repositories at startup."""
    global _platform_admin_repo, _audit_repo
    _platform_admin_repo = platform_admin_repo
    _audit_repo = audit_repo


# ---------------------------------------------------------------------------
# Rate limiting (SPEC-1691: uses shared RateLimitBackend)
# ---------------------------------------------------------------------------


def _is_rate_limited(client_ip: str) -> bool:
    """Check if IP has exceeded recovery attempt rate limit."""
    from src.multi_tenant.security_hardening import get_rate_limit_backend

    return get_rate_limit_backend().is_limited(
        f"spa_recovery:{client_ip}",
        max_requests=_RATE_MAX,
        window_seconds=_RATE_WINDOW,
    )


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class RecoveryRequest(BaseModel):
    """Request body for SPA key recovery."""

    email: str = Field(description="Platform admin email address")
    backup_code: str = Field(description="One of the 8 backup recovery codes")


class RecoveryResponse(BaseModel):
    """Always-success response to prevent enumeration."""

    message: str = _GENERIC_RESPONSE


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/recover",
    response_model=RecoveryResponse,
    summary="Recover SPA API key using a backup code (SPEC-1678)",
    description=(
        "Unauthenticated endpoint. If the email and backup code are valid, "
        "a new API key is generated and emailed to the admin. The old key "
        "is immediately invalidated. Always returns 200 to prevent enumeration."
    ),
)
async def recover_spa_key(
    body: RecoveryRequest,
    request: Request,
) -> RecoveryResponse:
    """Recover SPA API key using a backup code."""
    client = request.scope.get("client")
    client_ip = client[0] if client else "unknown"

    # Rate limit check
    if _is_rate_limited(client_ip):
        logger.warning("SPA recovery rate-limited: ip=%s", client_ip)
        from starlette.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={"message": "Too many recovery attempts. Try again later."},
        )

    if _platform_admin_repo is None:
        logger.error("SPA recovery: platform admin repo not configured")
        return RecoveryResponse()

    # Look up admin by email
    admin = await _platform_admin_repo.find_by_email(body.email)
    if not admin:
        logger.info("SPA recovery: no admin found for email=%s", body.email)
        return RecoveryResponse()

    # Check backup code against stored hashes
    from src.multi_tenant.auth import hash_api_key

    code_hash = hash_api_key(body.backup_code)
    stored_hashes = admin.get("backup_recovery_code_hashes", [])

    if code_hash not in stored_hashes:
        logger.info(
            "SPA recovery: invalid backup code for email=%s", body.email,
        )
        return RecoveryResponse()

    # Valid backup code — generate new key
    from src.multi_tenant.auth import generate_spa_api_key

    admin_id = admin.get("admin_id", admin.get("id"))
    new_raw_key = generate_spa_api_key()
    new_key_hash = hash_api_key(new_raw_key)
    now_iso = datetime.now(UTC).isoformat()

    # Update key hash
    await _platform_admin_repo.update_api_key_hash(
        admin_id=admin_id,
        new_key_hash=new_key_hash,
        updated_at=now_iso,
    )

    # Consume the backup code
    remaining_hashes = [h for h in stored_hashes if h != code_hash]
    await _platform_admin_repo.consume_backup_code(
        admin_id=admin_id,
        remaining_hashes=remaining_hashes,
        new_count=len(remaining_hashes),
        updated_at=now_iso,
    )

    # Email the new key to the admin
    await _send_recovery_email(admin["email"], new_raw_key)

    # Audit log
    logger.info(
        "SPA key recovered via backup code: admin_id=%s email=%s",
        admin_id, admin["email"],
    )
    if _audit_repo:
        try:
            from src.multi_tenant.cosmos_schema import AuditEventType
            await _audit_repo.log_event(
                event_type=AuditEventType.SECURITY_EVENT,
                tenant_id="__platform__",
                actor=admin["email"],
                actor_type="admin",
                payload={
                    "action": "spa_key_recovery",
                    "admin_id": admin_id,
                    "backup_codes_remaining": len(remaining_hashes),
                    "client_ip": client_ip,
                },
            )
        except Exception as exc:
            logger.warning("Audit log for SPA recovery failed: %s", exc)

    return RecoveryResponse()


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

_RECOVERY_EMAIL_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">
  SPA API Key Recovery
</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 16px">
  Your Agent Red platform admin API key has been recovered using a backup
  code. Your previous key has been invalidated immediately.
</p>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 8px">
  <strong>Your new API key:</strong>
</p>
<div style="background:#f3f4f6;padding:12px 16px;border-radius:6px;margin:0 0 24px">
  <code style="font-size:13px;word-break:break-all;color:#111827">{new_key}</code>
</div>
<p style="color:#ef4444;font-size:13px;line-height:1.5;margin:0 0 16px">
  <strong>Save this key immediately.</strong> It will not be shown again.
  One of your backup codes has been consumed.
</p>
<div style="text-align:center;margin:24px 0">
  <a href="{admin_dashboard_url}" style="display:inline-block;padding:10px 24px;
     background:#ff3621;color:#ffffff;font-size:14px;font-weight:600;
     text-decoration:none;border-radius:4px">
    Sign in to Dashboard
  </a>
</div>
<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:16px 0 0">
  If you did not initiate this recovery, your backup codes may be
  compromised. Sign in to your
  <a href="{admin_dashboard_url}" style="color:#ff3621">admin dashboard</a>
  and generate new backup codes immediately.
</p>
"""


async def _send_recovery_email(to_email: str, new_key: str) -> None:
    """Send the recovery email with the new API key."""
    try:
        from src.multi_tenant.alert_delivery import format_branded_email, send_acs_email

        conn_str = os.environ.get("ACS_CONNECTION_STRING", "")
        if not conn_str:
            logger.warning("ACS_CONNECTION_STRING not set — recovery email not sent")
            return

        from src.multi_tenant.welcome_email import _build_admin_login_url

        admin_url = _build_admin_login_url()
        body_html = _RECOVERY_EMAIL_BODY.format(
            new_key=new_key,
            admin_dashboard_url=admin_url,
        )
        full_html = format_branded_email(body_html, admin_url=admin_url)

        await send_acs_email(
            conn_str=conn_str,
            to_email=to_email,
            subject="Agent Red — SPA API Key Recovery",
            html_body=full_html,
        )
        logger.info("Recovery email sent to %s", to_email)
    except Exception as exc:
        logger.error("Failed to send recovery email to %s: %s", to_email, exc)
