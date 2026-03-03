"""Admin API Key Management API — generate, rotate, revoke, reset API keys.

Provides REST endpoints for merchant API key lifecycle management:

    GET    /api/admin/api-keys        — Get current API key metadata (prefix, created)
    POST   /api/admin/api-keys        — Generate a new API key (only if none exists)
    POST   /api/admin/api-keys/rotate — Rotate: generate new key, invalidate old
    DELETE /api/admin/api-keys        — Revoke the current API key
    POST   /api/admin/api-keys/reset  — PUBLIC: Reset key via email verification

API keys are the primary authentication mechanism for direct-channel (Stripe)
merchants. Shopify merchants use session tokens but may also use API keys for
programmatic access.

Security properties:
    - Keys are never stored in plaintext (SHA-256 hash only in Cosmos DB)
    - The raw key is returned ONCE at generation time and never again
    - Key format: ar_live_{tenant_prefix}_{random} (40 chars)
    - Rotation creates new key + updates hash atomically
    - All operations logged to audit trail (SECURITY_EVENT)
    - Reset endpoint is rate-limited and always returns 200 (email enumeration prevention)

Architecture references:
    - Decision #4: Triple auth (Shopify JWT + API key + widget key)
    - Decision #13: Audit logging for security events
    - WI #159: API key rotation endpoint

Dependencies:
    - auth.py: hash_api_key()
    - repository.py: TenantRepository
    - cosmos_schema.py: TenantDocument, AuditEventType

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import re
import secrets
import string
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel

from src.multi_tenant.auth import TenantContext, hash_api_key
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_KEY_PREFIX = "ar_live_"
API_KEY_RANDOM_LENGTH = 32  # 32 chars of randomness
API_KEY_ALPHABET = string.ascii_letters + string.digits


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ApiKeyMetadataResponse(CamelCaseModel):
    """API key metadata (never includes the raw key)."""


    has_key: bool = Field(description="Whether an API key is currently set")
    key_prefix: str | None = Field(
        default=None, description="First 12 chars of the key (for identification)"
    )
    created_at: str | None = Field(
        default=None, description="ISO 8601 timestamp when the key was created"
    )
    last_rotated_at: str | None = Field(
        default=None, description="ISO 8601 timestamp of last rotation"
    )


class ApiKeyGeneratedResponse(CamelCaseModel):
    """Response returned when a new API key is generated.

    The raw key is returned ONCE and never stored or retrievable again.
    """


    api_key: str = Field(description="The raw API key — save this, it cannot be retrieved again")
    key_prefix: str = Field(description="First 12 chars for future identification")
    created_at: str = Field(description="ISO 8601 timestamp")
    message: str = Field(
        default="Save this API key securely. It will not be shown again.",
    )


class ApiKeyRevokedResponse(CamelCaseModel):
    """Confirmation of key revocation."""


    revoked: bool = True
    revoked_at: str = Field(description="ISO 8601 timestamp")


class ApiKeyResetRequest(CamelCaseModel):
    """Request body for the public API key reset endpoint."""


    email: str = Field(description="Registered merchant email address")


class ApiKeyResetResponse(CamelCaseModel):
    """Response for the API key reset endpoint.

    Always returns the same message regardless of whether the email
    was found, to prevent email enumeration attacks.
    """


    message: str = Field(
        default="If an account with that email exists, a new API key has been sent.",
    )


# ---------------------------------------------------------------------------
# Key generation
# ---------------------------------------------------------------------------


def generate_api_key(tenant_id: str) -> str:
    """Generate a new API key with tenant-specific prefix.

    Format: ar_live_{tenant_prefix}_{random}
    Example: ar_live_tn8f3c_AbCdEf...

    The tenant prefix aids visual identification without revealing the
    full tenant_id.
    """
    tenant_prefix = tenant_id[:6] if len(tenant_id) >= 6 else tenant_id
    random_part = "".join(
        secrets.choice(API_KEY_ALPHABET) for _ in range(API_KEY_RANDOM_LENGTH)
    )
    return f"{API_KEY_PREFIX}{tenant_prefix}_{random_part}"


# ---------------------------------------------------------------------------
# In-memory rate limiter for public reset endpoint
# ---------------------------------------------------------------------------

_reset_rate_limit: dict[str, list[float]] = {}  # IP -> list of timestamps
RESET_RATE_WINDOW = 300.0  # 5 minutes
RESET_RATE_MAX = 3  # max 3 requests per window per IP

# Email validation regex
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _is_rate_limited(client_ip: str) -> bool:
    """Check if a client IP has exceeded the reset rate limit."""
    import time

    now = time.time()
    window_start = now - RESET_RATE_WINDOW

    # Clean old entries
    if client_ip in _reset_rate_limit:
        _reset_rate_limit[client_ip] = [
            ts for ts in _reset_rate_limit[client_ip] if ts > window_start
        ]

    requests = _reset_rate_limit.get(client_ip, [])
    if len(requests) >= RESET_RATE_MAX:
        return True

    # Record this request
    _reset_rate_limit.setdefault(client_ip, []).append(now)
    return False


async def _send_api_key_email(
    to_email: str,
    raw_key: str,
    tenant_name: str | None = None,
    admin_login_url: str | None = None,
) -> bool:
    """Send the new API key to the merchant via SMTP primary, ACS fallback.

    Uses the shared ``_EMAIL_WRAPPER`` from alert_delivery.py for visual
    consistency across all Agent Red transactional emails (WI-0988).
    Returns True if sent successfully via either provider, False otherwise.
    """
    from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

    name_display = f" ({tenant_name})" if tenant_name else ""
    subject = "Your Agent Red API Key Has Been Reset"

    body_html = f"""\
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">API Key Reset</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  A new API key was generated for your account{name_display}. Your previous key
  has been invalidated and will no longer work.
</p>

<div style="background:#f3f4f6;border:1px solid #d1d5db;padding:16px;margin:16px 0">
  <p style="margin:0 0 8px;color:#6b7280;font-size:12px;font-weight:600;
       text-transform:uppercase;letter-spacing:0.05em">Your New API Key</p>
  <code style="word-break:break-all;color:#111827;font-size:14px;
       font-family:'JetBrains Mono',SFMono-Regular,ui-monospace,monospace">{raw_key}</code>
  <p style="margin:8px 0 0;color:#6b7280;font-size:12px;line-height:1.4">
    Copy this key and use it to sign in to your admin dashboard.
    This key will not be shown again.
  </p>
</div>

<div style="background:#fef3c7;border:1px solid #fcd34d;padding:16px;margin:16px 0">
  <strong style="color:#92400e">Did not request this?</strong>
  <p style="color:#92400e;margin:8px 0 0;font-size:13px">
    If you did not request a key reset, someone may have access to your email.
    <a href="{admin_login_url or 'mailto:support@agentred.com'}"
       style="color:#ff3621;font-weight:600">Request a new API key</a>
    immediately to invalidate this one and secure your account.
  </p>
</div>"""

    full_html = _EMAIL_WRAPPER.format(body=body_html)

    # --- Provider 1: SMTP (Titan or other SMTP provider) ---
    smtp_host = os.environ.get("SMTP_HOST", "")
    if smtp_host:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USERNAME", "")
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")
        smtp_from = os.environ.get("SMTP_FROM", smtp_user) or "noreply@agentred.com"

        try:
            import asyncio

            msg = MIMEMultipart("alternative")
            msg["From"] = f"Agent Red <{smtp_from}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(full_html, "html"))

            def _smtp_send() -> None:
                if smtp_port == 465:
                    with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                        if smtp_user and smtp_pass:
                            server.login(smtp_user, smtp_pass)
                        server.send_message(msg)
                else:
                    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                        server.ehlo()
                        if smtp_port != 25:
                            server.starttls()
                        if smtp_user and smtp_pass:
                            server.login(smtp_user, smtp_pass)
                        server.send_message(msg)

            await asyncio.to_thread(_smtp_send)  # SPEC-1622: non-blocking SMTP
            logger.info("API key reset email sent via SMTP to %s", to_email)
            return True

        except Exception:
            logger.exception("SMTP API key reset email failed — trying ACS fallback")
            # Fall through to ACS provider

    # --- Provider 2: Azure Communication Services (fallback) ---
    conn_str = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
    if conn_str:
        try:
            from src.multi_tenant.alert_delivery import send_acs_email

            status = await send_acs_email(conn_str, to_email, subject, full_html)
            sent = status == "Succeeded"
            if sent:
                logger.info("API key reset email sent via ACS to %s", to_email)
            else:
                logger.warning("ACS API key reset email status=%s for %s", status, to_email)
            return sent
        except Exception:
            logger.exception("ACS API key reset email failed for %s", to_email)
            return False

    logger.warning("No email provider configured — cannot send API key reset email")
    return False


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/admin/api-keys",
    tags=["API Key Management"],
)

# Service injection (wired at startup)
_tenant_repo: Any = None
_audit_repo: Any = None


def configure_apikey_services(
    tenant_repo: Any,
    audit_repo: Any | None = None,
) -> None:
    """Inject repository dependencies at app startup."""
    global _tenant_repo, _audit_repo
    _tenant_repo = tenant_repo
    _audit_repo = audit_repo


async def _log_audit(
    tenant_id: str,
    event_type: str,
    details: dict[str, Any],
) -> None:
    """Log a security event to the audit trail."""
    if _audit_repo is None:
        return
    try:
        from src.multi_tenant.cosmos_schema import AuditEventType

        # Map string event type to enum
        audit_event = AuditEventType(event_type)
        await _audit_repo.log_event(
            event_type=audit_event,
            tenant_id=tenant_id,
            actor="admin",
            actor_type="admin",
            payload=details,
        )
    except Exception:
        logger.warning("Failed to write audit log for API key operation", exc_info=True)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=ApiKeyMetadataResponse,
    summary="Get API key metadata",
    description="Returns metadata about the current API key without exposing the key itself.",
)
async def get_api_key_metadata(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ApiKeyMetadataResponse:
    """Return metadata about the tenant's current API key."""
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    tenant = await _tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    has_key = bool(tenant.get("api_key_hash"))
    key_prefix = tenant.get("api_key_prefix")
    created_at = tenant.get("api_key_created_at")
    last_rotated = tenant.get("api_key_last_rotated_at")

    return ApiKeyMetadataResponse(
        has_key=has_key,
        key_prefix=key_prefix,
        created_at=created_at,
        last_rotated_at=last_rotated,
    )


@router.post(
    "",
    response_model=ApiKeyGeneratedResponse,
    status_code=201,
    summary="Generate a new API key",
    description="Generate a new API key. Fails if one already exists (use rotate instead).",
)
async def generate_new_api_key(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ApiKeyGeneratedResponse:
    """Generate a new API key for the tenant.

    Fails with 409 if a key already exists — use POST /rotate instead.
    """
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    tenant = await _tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if tenant.get("api_key_hash"):
        raise HTTPException(
            status_code=409,
            detail="API key already exists. Use POST /api/admin/api-keys/rotate to rotate.",
        )

    raw_key = generate_api_key(ctx.tenant_id)
    key_hash = hash_api_key(raw_key)
    now = datetime.now(timezone.utc).isoformat()
    key_prefix = raw_key[:12]

    # Update tenant document with new key hash + metadata
    await _tenant_repo.patch(
        tenant_id=ctx.tenant_id,
        document_id=ctx.tenant_id,
        operations=[
            {"op": "set", "path": "/api_key_hash", "value": key_hash},
            {"op": "set", "path": "/api_key_prefix", "value": key_prefix},
            {"op": "set", "path": "/api_key_created_at", "value": now},
        ],
    )

    await _log_audit(
        ctx.tenant_id,
        "security.event",
        {"action": "api_key_generated", "key_prefix": key_prefix},
    )

    logger.info(
        "API key generated for tenant %s (prefix: %s)",
        ctx.tenant_id,
        key_prefix,
    )

    return ApiKeyGeneratedResponse(
        api_key=raw_key,
        key_prefix=key_prefix,
        created_at=now,
    )


@router.post(
    "/rotate",
    response_model=ApiKeyGeneratedResponse,
    summary="Rotate API key",
    description="Generate a new API key, invalidating the old one immediately.",
)
async def rotate_api_key(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ApiKeyGeneratedResponse:
    """Rotate the tenant's API key.

    Generates a new key and immediately invalidates the old one.
    The new raw key is returned once and cannot be retrieved again.
    """
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    tenant = await _tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    old_prefix = tenant.get("api_key_prefix", "none")

    raw_key = generate_api_key(ctx.tenant_id)
    key_hash = hash_api_key(raw_key)
    now = datetime.now(timezone.utc).isoformat()
    key_prefix = raw_key[:12]

    # Atomically update with new key hash
    await _tenant_repo.patch(
        tenant_id=ctx.tenant_id,
        document_id=ctx.tenant_id,
        operations=[
            {"op": "set", "path": "/api_key_hash", "value": key_hash},
            {"op": "set", "path": "/api_key_prefix", "value": key_prefix},
            {"op": "set", "path": "/api_key_created_at", "value": now},
            {"op": "set", "path": "/api_key_last_rotated_at", "value": now},
        ],
    )

    await _log_audit(
        ctx.tenant_id,
        "security.event",
        {
            "action": "api_key_rotated",
            "old_prefix": old_prefix,
            "new_prefix": key_prefix,
        },
    )

    logger.info(
        "API key rotated for tenant %s (old: %s → new: %s)",
        ctx.tenant_id,
        old_prefix,
        key_prefix,
    )

    return ApiKeyGeneratedResponse(
        api_key=raw_key,
        key_prefix=key_prefix,
        created_at=now,
        message="API key rotated. The old key is immediately invalid. Save this new key securely.",
    )


@router.delete(
    "",
    response_model=ApiKeyRevokedResponse,
    summary="Revoke API key",
    description="Permanently revoke the current API key. A new one must be generated to restore access.",
)
async def revoke_api_key(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ApiKeyRevokedResponse:
    """Revoke the tenant's API key.

    After revocation, API key authentication will fail until a new key
    is generated.
    """
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    tenant = await _tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if not tenant.get("api_key_hash"):
        raise HTTPException(status_code=404, detail="No API key to revoke")

    old_prefix = tenant.get("api_key_prefix", "unknown")
    now = datetime.now(timezone.utc).isoformat()

    # Clear key hash and metadata
    await _tenant_repo.patch(
        tenant_id=ctx.tenant_id,
        document_id=ctx.tenant_id,
        operations=[
            {"op": "set", "path": "/api_key_hash", "value": None},
            {"op": "set", "path": "/api_key_prefix", "value": None},
            {"op": "set", "path": "/api_key_created_at", "value": None},
            {"op": "set", "path": "/api_key_last_rotated_at", "value": None},
        ],
    )

    await _log_audit(
        ctx.tenant_id,
        "security.event",
        {"action": "api_key_revoked", "revoked_prefix": old_prefix},
    )

    logger.info(
        "API key revoked for tenant %s (prefix: %s)",
        ctx.tenant_id,
        old_prefix,
    )

    return ApiKeyRevokedResponse(revoked_at=now)


# ---------------------------------------------------------------------------
# Public endpoint: API key reset (no auth required)
# ---------------------------------------------------------------------------


@router.post(
    "/reset",
    response_model=ApiKeyResetResponse,
    summary="Reset API key via email (public)",
    description=(
        "Public endpoint for merchants who lost their API key. "
        "Looks up the account by email, generates a new key, and sends it via email. "
        "Always returns 200 regardless of whether the email was found (prevents enumeration)."
    ),
)
async def reset_api_key_via_email(
    body: ApiKeyResetRequest,
    request: Request,
) -> ApiKeyResetResponse:
    """Reset a merchant's API key via email verification.

    This is a PUBLIC endpoint — no authentication required.  The merchant
    provides their registered email address; if it matches a tenant, a new
    API key is generated and emailed to them.

    Security:
        - Rate limited: 3 requests per 5-minute window per IP
        - Always returns the same message (prevents email enumeration)
        - Audit logged as SECURITY_EVENT
        - Old key immediately invalidated on reset
    """
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Rate limit by client IP
    client_ip = request.client.host if request.client else "unknown"
    if _is_rate_limited(client_ip):
        logger.warning(
            "API key reset rate limited: ip=%s email=%s",
            client_ip, body.email,
        )
        raise HTTPException(
            status_code=429,
            detail="Too many reset requests. Please try again in a few minutes.",
        )

    # Validate email format
    email = body.email.strip().lower()
    if not _EMAIL_RE.match(email):
        # Return generic message to avoid leaking validation details
        return ApiKeyResetResponse()

    # Look up tenant by email
    tenant = await _tenant_repo.find_by_customer_email(email)
    if tenant is None:
        # No tenant found — return the same message (no enumeration)
        logger.info(
            "API key reset requested for unknown email: ip=%s", client_ip,
        )
        return ApiKeyResetResponse()

    tenant_id = tenant.get("id", tenant.get("tenant_id", ""))
    tenant_name = tenant.get("company_name") or tenant.get("tenant_name")

    # Generate new key and update tenant
    raw_key = generate_api_key(tenant_id)
    key_hash = hash_api_key(raw_key)
    now = datetime.now(timezone.utc).isoformat()
    key_prefix = raw_key[:12]

    await _tenant_repo.patch(
        tenant_id=tenant_id,
        document_id=tenant_id,
        operations=[
            {"op": "set", "path": "/api_key_hash", "value": key_hash},
            {"op": "set", "path": "/api_key_prefix", "value": key_prefix},
            {"op": "set", "path": "/api_key_created_at", "value": now},
            {"op": "set", "path": "/api_key_last_rotated_at", "value": now},
        ],
    )

    # Build self-service re-reset URL for the security notification in the email.
    # SPEC-1617: include ?tenant= slug so the link is globally unique.
    from src.multi_tenant.welcome_email import _build_admin_login_url, tenant_url_slug

    shop_domain = tenant.get("shopify_shop_domain")
    slug = tenant_url_slug(shop_domain, tenant_name, tenant_id)
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", request.url.hostname or "localhost")
    admin_login_url = f"{scheme}://{host}/admin/standalone/"
    if slug:
        admin_login_url += f"?tenant={slug}"

    # Send the new key via email
    email_sent = await _send_api_key_email(email, raw_key, tenant_name, admin_login_url)

    await _log_audit(
        tenant_id,
        "security.event",
        {
            "action": "api_key_reset_via_email",
            "key_prefix": key_prefix,
            "email_sent": email_sent,
            "client_ip": client_ip,
        },
    )

    logger.info(
        "API key reset for tenant %s via email (prefix: %s, email_sent: %s)",
        tenant_id, key_prefix, email_sent,
    )

    return ApiKeyResetResponse()
