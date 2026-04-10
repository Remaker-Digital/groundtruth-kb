# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tenant Account Recovery by SPA (SPEC-1677).

Allows the Service Provider Administrator to:
    1. Activate a recovery email address for any tenant
    2. Send a one-time auth link to that address
    3. Check recovery address status

The recovery link generates a temporary token (15-min TTL, single-use)
stored in the verification_tokens collection. When verified, a session
JWT is issued for the tenant's superadmin.

Guard: require_platform_admin() — any SPA user (superadmin or operator).

Endpoints:
    POST /api/superadmin/tenant-recovery/activate
    POST /api/superadmin/tenant-recovery/send-auth-link
    GET  /api/superadmin/tenant-recovery/status/{tenant_id}
    GET  /api/auth/account-recovery/verify

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.multi_tenant.api_models import CamelCaseModel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SPA-facing router (authenticated — require_platform_admin)
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/superadmin/tenant-recovery",
    tags=["Tenant Recovery"],
)

# ---------------------------------------------------------------------------
# Public recovery verification router (unauthenticated)
# ---------------------------------------------------------------------------

recovery_verify_router = APIRouter(
    prefix="/api/auth/account-recovery",
    tags=["Account Recovery"],
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_RECOVERY_TOKEN_TYPE = "account_recovery"
_RECOVERY_TOKEN_TTL = 900  # 15 minutes
_SESSION_TTL_HOURS = 8

_JWT_SECRET = os.environ.get(
    "MAGIC_LINK_JWT_SECRET",
    os.environ.get("SHOPIFY_API_SECRET", "agent-red-magic-link-default-secret"),
)

# ---------------------------------------------------------------------------
# Module-level service references (set at startup)
# ---------------------------------------------------------------------------

_tenant_repo = None
_verification_repo = None
_audit_repo = None


def configure_tenant_recovery(
    tenant_repo=None,
    verification_repo=None,
    audit_repo=None,
) -> None:
    """Wire repositories at startup."""
    global _tenant_repo, _verification_repo, _audit_repo
    _tenant_repo = tenant_repo
    _verification_repo = verification_repo
    _audit_repo = audit_repo


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class ActivateRecoveryRequest(BaseModel):
    """Request to activate a recovery address for a tenant."""

    tenant_id: str = Field(description="Target tenant ID")
    recovery_email: str = Field(description="Recovery email address")


class SendAuthLinkRequest(BaseModel):
    """Request to send a one-time auth link to a tenant's recovery address."""

    tenant_id: str = Field(description="Target tenant ID")


class RecoveryStatusResponse(BaseModel):
    """Recovery address status for a tenant."""

    tenant_id: str
    recovery_address: str | None = None
    recovery_address_enabled: bool = False
    activated_by: str | None = None
    activated_at: str | None = None


# ---------------------------------------------------------------------------
# SPA-facing endpoints
# ---------------------------------------------------------------------------


class RecoveryActionResponse(CamelCaseModel):
    """Generic response for recovery actions."""

    message: str


@router.post(
    "/activate",
    response_model=RecoveryActionResponse,
    summary="Set recovery address for a tenant (SPEC-1677)",
)
async def activate_recovery_address(
    body: ActivateRecoveryRequest,
    request: Request,
) -> RecoveryActionResponse:
    """Activate or update the recovery address for a tenant."""
    ctx = getattr(request.state, "tenant_context", None)

    if _tenant_repo is None:
        return JSONResponse(status_code=503, content={"error": "Service not configured"})

    now_iso = datetime.now(UTC).isoformat()
    admin_id = getattr(ctx, "platform_admin_id", "unknown") if ctx else "unknown"

    await _tenant_repo.update_recovery_address(
        tenant_id=body.tenant_id,
        recovery_email=body.recovery_email,
        enabled=True,
        activated_by=admin_id,
        activated_at=now_iso,
    )

    # Audit log
    if _audit_repo:
        try:
            from src.multi_tenant.cosmos_schema import AuditEventType
            await _audit_repo.log_event(
                event_type=AuditEventType.SECURITY_EVENT,
                tenant_id=body.tenant_id,
                actor=getattr(ctx, "platform_admin_email", "unknown") if ctx else "unknown",
                actor_type="admin",
                payload={
                    "action": "recovery_address_activated",
                    "recovery_email": body.recovery_email,
                    "activated_by": admin_id,
                },
            )
        except Exception as exc:
            logger.warning("Audit log for recovery activation failed: %s", exc)

    return RecoveryActionResponse(message=f"Recovery address activated for tenant {body.tenant_id}")


@router.post(
    "/send-auth-link",
    response_model=RecoveryActionResponse,
    summary="Send one-time auth link to tenant's recovery address (SPEC-1677)",
)
async def send_recovery_auth_link(
    body: SendAuthLinkRequest,
    request: Request,
) -> RecoveryActionResponse:
    """Send a one-time auth link to the tenant's recovery address."""
    ctx = getattr(request.state, "tenant_context", None)

    if _tenant_repo is None or _verification_repo is None:
        return JSONResponse(status_code=503, content={"error": "Service not configured"})

    # Check recovery address status
    recovery_info = await _tenant_repo.get_recovery_address(body.tenant_id)
    if not recovery_info or not recovery_info.get("recovery_address_enabled"):
        return JSONResponse(
            status_code=400,
            content={"error": "No active recovery address for this tenant"},
        )

    recovery_email = recovery_info["recovery_address"]
    if not recovery_email:
        return JSONResponse(
            status_code=400,
            content={"error": "Recovery address not set"},
        )

    # Generate recovery token
    token_id = secrets.token_urlsafe(32)
    await _verification_repo.create_token(
        token_id=token_id,
        token_type=_RECOVERY_TOKEN_TYPE,
        tenant_id=body.tenant_id,
        email=recovery_email,
        ttl=_RECOVERY_TOKEN_TTL,
    )

    # Build recovery link
    admin_url = os.environ.get("ADMIN_BASE_URL", "")
    if not admin_url:
        # Derive from request
        scheme = request.headers.get("x-forwarded-proto", "https")
        host = request.headers.get("host", "localhost")
        admin_url = f"{scheme}://{host}"

    recovery_link = (
        f"{admin_url}/admin/standalone/"
        f"?tenant={body.tenant_id}&recovery_token={token_id}"
    )

    # Send email
    await _send_recovery_auth_email(recovery_email, recovery_link, body.tenant_id)

    # Audit log
    if _audit_repo:
        try:
            from src.multi_tenant.cosmos_schema import AuditEventType
            await _audit_repo.log_event(
                event_type=AuditEventType.SECURITY_EVENT,
                tenant_id=body.tenant_id,
                actor=getattr(ctx, "platform_admin_email", "unknown") if ctx else "unknown",
                actor_type="admin",
                payload={
                    "action": "recovery_auth_link_sent",
                    "tenant_id": body.tenant_id,
                    "recovery_email": recovery_email,
                },
            )
        except Exception as exc:
            logger.warning("Audit log for auth link send failed: %s", exc)

    return RecoveryActionResponse(message=f"Recovery auth link sent to {recovery_email}")


@router.get(
    "/status/{tenant_id}",
    response_model=RecoveryStatusResponse,
    summary="Check recovery address status for a tenant (SPEC-1677)",
)
async def get_recovery_status(
    tenant_id: str,
    request: Request,
) -> RecoveryStatusResponse:
    """Get the recovery address status for a tenant."""
    if _tenant_repo is None:
        return JSONResponse(status_code=503, content={"error": "Service not configured"})

    recovery_info = await _tenant_repo.get_recovery_address(tenant_id)
    if recovery_info is None:
        return JSONResponse(status_code=404, content={"error": "Tenant not found"})

    return RecoveryStatusResponse(
        tenant_id=tenant_id,
        recovery_address=recovery_info.get("recovery_address"),
        recovery_address_enabled=recovery_info.get("recovery_address_enabled", False),
        activated_by=recovery_info.get("recovery_address_activated_by"),
        activated_at=recovery_info.get("recovery_address_activated_at"),
    )


# ---------------------------------------------------------------------------
# Public verification endpoint (unauthenticated)
# ---------------------------------------------------------------------------


@recovery_verify_router.get(
    "/verify",
    summary="Verify account recovery token and issue session JWT (SPEC-1677)",
)
async def verify_recovery_token(
    token: str = Query(description="Recovery token from the email link"),
    tenant: str = Query(description="Tenant ID"),
) -> dict:
    """Verify recovery token and issue a session JWT for the tenant."""
    if _verification_repo is None:
        return JSONResponse(status_code=503, content={"error": "Service not configured"})

    # Consume the token (single-use)
    try:
        doc = await _verification_repo.consume_token(
            token_id=token,
            token_type=_RECOVERY_TOKEN_TYPE,
        )
    except Exception:
        doc = None  # Treat repo errors as invalid token

    if doc is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid or expired recovery token."},
        )

    # Verify tenant matches
    if doc.get("tenant_id") != tenant:
        return JSONResponse(
            status_code=400,
            content={"error": "Token does not match the requested tenant."},
        )

    # Issue session JWT (same format as magic link sessions)
    now = datetime.now(UTC)
    payload = {
        "sub": tenant,
        "email": doc.get("email", ""),
        "type": "account_recovery",
        "iat": now,
        "exp": now + timedelta(hours=_SESSION_TTL_HOURS),
    }
    session_token = jwt.encode(payload, _JWT_SECRET, algorithm="HS256")

    logger.info(
        "Account recovery session issued: tenant=%s email=%s",
        tenant, doc.get("email"),
    )

    # Audit log
    if _audit_repo:
        try:
            from src.multi_tenant.cosmos_schema import AuditEventType
            await _audit_repo.log_event(
                event_type=AuditEventType.SECURITY_EVENT,
                tenant_id=tenant,
                actor=doc.get("email", "unknown"),
                actor_type="admin",
                payload={
                    "action": "account_recovery_verified",
                    "tenant_id": tenant,
                },
            )
        except Exception as exc:
            logger.warning("Audit log for recovery verification failed: %s", exc)

    return {
        "session_token": session_token,
        "tenant_id": tenant,
        "email": doc.get("email", ""),
        "expires_in": _SESSION_TTL_HOURS * 3600,
    }


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

_RECOVERY_AUTH_EMAIL_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">
  Account Recovery Access
</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 16px">
  Your Agent Red platform administrator has initiated account recovery
  for tenant <strong>{tenant_id}</strong>.
</p>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  Click the link below to access the admin dashboard. This link expires
  in 15 minutes and can only be used once.
</p>
<div style="text-align:center;margin:0 0 24px">
  <a href="{recovery_link}"
     style="display:inline-block;padding:12px 32px;background:#ff3621;
            color:#ffffff;text-decoration:none;border-radius:6px;
            font-size:14px;font-weight:600">
    Access Admin Dashboard
  </a>
</div>
<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:0 0 8px">
  If you did not request this, you can safely ignore this email.
</p>
<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:0">
  Link: {recovery_link}
</p>
"""


async def _send_recovery_auth_email(
    to_email: str, recovery_link: str, tenant_id: str,
) -> None:
    """Send the recovery auth link email."""
    try:
        from src.multi_tenant.alert_delivery import format_branded_email, send_acs_email

        conn_str = os.environ.get("ACS_CONNECTION_STRING", "")
        if not conn_str:
            logger.warning("ACS_CONNECTION_STRING not set — recovery auth email not sent")
            return

        body_html = _RECOVERY_AUTH_EMAIL_BODY.format(
            recovery_link=recovery_link,
            tenant_id=tenant_id,
        )
        full_html = format_branded_email(body_html)

        await send_acs_email(
            conn_str=conn_str,
            to_email=to_email,
            subject="Agent Red — Account Recovery Access",
            html_body=full_html,
        )
        logger.info("Recovery auth email sent to %s for tenant %s", to_email, tenant_id)
    except Exception as exc:
        logger.error(
            "Failed to send recovery auth email to %s: %s", to_email, exc,
        )
