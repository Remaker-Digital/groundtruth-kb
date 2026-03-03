"""Magic link authentication for standalone (Stripe-direct) merchants.

Provides passwordless sign-in via emailed magic links. An alternative
to API key authentication for human users — API keys remain available
for programmatic access.

Endpoints:
    POST /api/auth/magic-link/request  — Send magic link email (public)
    GET  /api/auth/magic-link/verify   — Verify token, return session JWT

Flow:
    1. Merchant enters email → POST /request
    2. Server looks up tenant by customer_email
    3. If found, create verification token + send branded email
    4. Always return 200 (prevent email enumeration)
    5. Merchant clicks link → GET /verify?token=...
    6. Server consumes token (single-use), generates 8-hour JWT
    7. Return JSON with session_token + tenant metadata
    8. Frontend stores JWT in sessionStorage, uses as auth header

Security properties:
    - Rate-limited: 3 requests per 5 min per IP
    - Tokens are single-use (consumed on verify)
    - Tokens auto-expire via Cosmos DB TTL (15 minutes)
    - JWT session tokens expire after 8 hours
    - No email enumeration (always returns 200 on request)
    - JWT secret derived from environment variable

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import secrets
import time
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth/magic-link",
    tags=["Magic Link Auth"],
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_TOKEN_TYPE = "magic_link"
_TOKEN_TTL_SECONDS = 900  # 15 minutes
_SESSION_TTL_HOURS = 8

# JWT secret — falls back to a derived value if not explicitly set
_JWT_SECRET = os.environ.get(
    "MAGIC_LINK_JWT_SECRET",
    os.environ.get("SHOPIFY_API_SECRET", "agent-red-magic-link-default-secret"),
)

# ---------------------------------------------------------------------------
# Rate limiting (in-memory, per-instance)
# ---------------------------------------------------------------------------

_RATE_WINDOW = 300.0  # 5 minutes
_RATE_MAX = 3

_rate_limit: dict[str, list[float]] = {}


def _is_rate_limited(client_ip: str) -> bool:
    """Check if IP has exceeded magic link request rate limit."""
    now = time.time()
    window_start = now - _RATE_WINDOW
    if client_ip in _rate_limit:
        _rate_limit[client_ip] = [
            ts for ts in _rate_limit[client_ip] if ts > window_start
        ]
    requests = _rate_limit.get(client_ip, [])
    if len(requests) >= _RATE_MAX:
        return True
    _rate_limit.setdefault(client_ip, []).append(now)
    return False


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class MagicLinkRequest(BaseModel):
    """Request body for magic link."""

    email: str = Field(description="Email address associated with the tenant account")
    tenant: str = Field(
        description="Tenant ID from the origin URL query parameter (SPEC-1644). "
        "Required — the URL must identify the tenant.  The magic link verify "
        "URL will include ?tenant=<id> for tenant-scoped authentication.",
    )


class MagicLinkRequestResponse(BaseModel):
    """Always-success response to prevent email enumeration."""

    message: str = Field(
        default="If an account with this email exists, a sign-in link has been sent. "
        "Please check your inbox.",
    )


class MagicLinkVerifyResponse(BaseModel):
    """Successful verification returns a session token."""

    session_token: str
    tenant_id: str
    email: str
    expires_at: str
    requires_2fa: bool = False
    pending_2fa_token: str | None = None


# ---------------------------------------------------------------------------
# Email template
# ---------------------------------------------------------------------------

_MAGIC_LINK_EMAIL_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Sign In to Agent Red</h2>
{tenant_context}
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  Click the button below to sign in to your Agent Red admin dashboard.
  This link will expire in 15 minutes.
</p>
<div style="text-align:center;margin:24px 0">
  <a href="{magic_link_url}" style="display:inline-block;padding:12px 32px;background:#ff3621;
     color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;border-radius:6px">
    Sign In
  </a>
</div>
<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:16px 0 0">
  If you did not request this link, you can safely ignore this email.
  Someone may have entered your email address by mistake.
</p>
"""

# ---------------------------------------------------------------------------
# JWT session token
# ---------------------------------------------------------------------------


def create_magic_link_session_token(
    tenant_id: str,
    email: str,
    *,
    member_id: str | None = None,
    role: str | None = None,
) -> tuple[str, str]:
    """Create an 8-hour session JWT for magic link authentication.

    Args:
        tenant_id: Tenant partition key.
        email: Authenticated user's email.
        member_id: Team member document ID (None = tenant owner).
        role: Team member role string (None = admin-level access).

    Returns (token, expires_at_iso).
    """
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=_SESSION_TTL_HOURS)
    payload = {
        "sub": tenant_id,
        "email": email,
        "type": "magic_link_session",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    if member_id is not None:
        payload["member_id"] = member_id
    if role is not None:
        payload["role"] = role
    token = jwt.encode(payload, _JWT_SECRET, algorithm="HS256")
    return token, exp.isoformat()


def verify_magic_link_session_token(token: str) -> dict | None:
    """Verify a magic link session JWT. Returns payload or None."""
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "magic_link_session":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("Magic link session token expired")
        return None
    except jwt.InvalidTokenError:
        logger.debug("Invalid magic link session token")
        return None


# ---------------------------------------------------------------------------
# Email sending (reuses ACS/SMTP infrastructure)
# ---------------------------------------------------------------------------


async def _send_magic_link_email(to_email: str, html_body: str) -> bool:
    """Send magic link email via SMTP or ACS.

    Provider selection: SMTP (Titan) > ACS > skip.
    """
    subject = "[Agent Red] Sign In Link"

    # --- Provider 1: SMTP (Titan or other SMTP provider) ---
    smtp_host = os.environ.get("SMTP_HOST", "")
    if smtp_host:
        import asyncio
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USERNAME", "")
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")
        smtp_from = os.environ.get("SMTP_FROM", smtp_user)

        def _smtp_send() -> None:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"Agent Red <{smtp_from}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(html_body, "html"))

            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                    if smtp_user:
                        server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.ehlo()
                    if smtp_port != 25:
                        server.starttls()
                    if smtp_user:
                        server.login(smtp_user, smtp_pass)
                    server.send_message(msg)

        try:
            await asyncio.to_thread(_smtp_send)  # SPEC-1622: non-blocking SMTP
            return True
        except Exception:
            logger.exception("SMTP email send failed for magic link — trying ACS fallback")
            # Fall through to ACS provider

    # --- Provider 2: Azure Communication Services (fallback) ---
    conn_str = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
    if conn_str:
        try:
            from src.multi_tenant.alert_delivery import send_acs_email

            status = await send_acs_email(conn_str, to_email, subject, html_body)
            return status == "Succeeded"
        except Exception:
            logger.exception("ACS email send failed for magic link")
            return False

    logger.warning("No email provider configured for magic link delivery")
    return False


# ---------------------------------------------------------------------------
# URL builder (SPEC-1619)
# ---------------------------------------------------------------------------


def _build_magic_link_url(
    *,
    scheme: str,
    host: str,
    token_id: str,
    origin_tenant: str | None = None,
) -> str:
    """Build the magic link verify URL, preserving origin tenant context.

    SPEC-1619: When the user clicked "Sign in with email" on a
    tenant-scoped page (?tenant=<slug>), the verify URL must include
    the same tenant parameter so the frontend can restore the correct
    tenant context after verification.
    """
    url = f"{scheme}://{host}/admin/standalone/verify-magic-link?token={token_id}"
    if origin_tenant:
        url += f"&tenant={origin_tenant}"
    return url


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/request",
    response_model=MagicLinkRequestResponse,
    summary="Request a magic sign-in link (public)",
    description="Sends a magic link email to the specified address. "
    "Rate-limited to 3 requests per 5 minutes per IP. "
    "Always returns 200 to prevent email enumeration.",
)
async def request_magic_link(
    body: MagicLinkRequest,
    request: Request,
) -> MagicLinkRequestResponse:
    """Send a magic link to the specified email address.

    Resolution order (tenant-scoped per SPEC-1644):
      1. Search team_members within the specified tenant for matching email.
      2. Fall back to tenant owner (customer_email) on the tenant document.
      3. If no match, silently return 200 (no enumeration).

    SPEC-1618: Each email references only the specific merchant account.
    SPEC-1619: Magic link URL preserves the origin tenant ID.
    SPEC-1644: No cross-partition queries — tenant ID from URL scopes all lookups.
    """
    client_ip = request.client.host if request.client else "unknown"

    if _is_rate_limited(client_ip):
        logger.warning("Magic link rate limit exceeded: ip=%s", client_ip)
        return MagicLinkRequestResponse()

    try:
        from src.multi_tenant.repositories import (
            TeamMemberRepository,
            TenantRepository,
            VerificationTokenRepository,
        )

        team_repo = TeamMemberRepository()
        tenant_repo = TenantRepository()
        token_repo = VerificationTokenRepository()

        email = body.email.strip().lower()
        origin_tenant = body.tenant  # SPEC-1644: tenant ID from URL

        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("host", request.url.hostname or "localhost")

        # ---- Step 1: Search team member within the specified tenant ----
        # SPEC-1644: Tenant-scoped lookup only — no cross-partition queries.
        member = await team_repo.find_by_email(origin_tenant, email)

        if member:
            await _send_member_magic_links(
                members=[member],
                email=email,
                scheme=scheme,
                host=host,
                origin_tenant=origin_tenant,
                token_repo=token_repo,
                tenant_repo=tenant_repo,
            )
            return MagicLinkRequestResponse()

        # ---- Step 2: Fall back to tenant owner (customer_email) ----
        # SPEC-1644: Read tenant document directly (no cross-partition).
        tenant = await tenant_repo.read(origin_tenant, origin_tenant)
        if not tenant or tenant.get("customer_email", "").lower() != email:
            logger.info("Magic link: no match in tenant=%s email=%s", origin_tenant, email)
            return MagicLinkRequestResponse()

        tenant_id = tenant["id"]
        token_id = secrets.token_urlsafe(32)
        await token_repo.create_token(
            token_id=token_id,
            token_type=_TOKEN_TYPE,
            tenant_id=tenant_id,
            email=email,
            ttl=_TOKEN_TTL_SECONDS,
        )

        magic_link_url = _build_magic_link_url(
            scheme=scheme, host=host, token_id=token_id,
            origin_tenant=origin_tenant,
        )
        html_body = _MAGIC_LINK_EMAIL_BODY.format(
            magic_link_url=magic_link_url, tenant_context="",
        )
        full_html = _EMAIL_WRAPPER.format(body=html_body)
        await _send_magic_link_email(email, full_html)

        logger.info(
            "Magic link sent (owner): tenant=%s email=%s", tenant_id, email,
        )
    except Exception:
        logger.exception("Error processing magic link request")

    return MagicLinkRequestResponse()


async def _send_member_magic_links(
    *,
    members: list[dict],
    email: str,
    scheme: str,
    host: str,
    origin_tenant: str | None = None,
    token_repo: Any,
    tenant_repo: Any,
) -> None:
    """Create tokens and send one magic link email PER tenant match.

    SPEC-1618: Each email must reference ONLY the specific merchant account
    that triggered it. Sending an email containing links to multiple
    tenancies is always a defect. When an email address matches team members
    in multiple tenants, we send separate emails — one per tenant.

    SPEC-1619: origin_tenant is forwarded to _build_magic_link_url so the
    verify URL preserves the tenant slug from the page the user was on.
    """
    for member in members:
        tid = member["tenant_id"]
        mid = member["id"]

        # Resolve a human-readable label for the tenant
        try:
            tenant_doc = await tenant_repo.read(tid, tid)
            label = (
                tenant_doc.get("shop_domain")
                or tenant_doc.get("business_name")
                or tid[:8]
            )
        except Exception:
            label = tid[:8]

        # Create a unique verification token for this tenant
        token_id = secrets.token_urlsafe(32)
        await token_repo.create_token(
            token_id=token_id,
            token_type=_TOKEN_TYPE,
            tenant_id=tid,
            email=email,
            ttl=_TOKEN_TTL_SECONDS,
            member_id=mid,
        )

        magic_link_url = _build_magic_link_url(
            scheme=scheme, host=host, token_id=token_id,
            origin_tenant=origin_tenant,
        )

        # Tenant context line — shown only when the user has multiple accounts
        if len(members) > 1:
            tenant_context = (
                f'<p style="color:#6b7280;font-size:13px;margin:0 0 8px">'
                f"Account: <strong>{label}</strong></p>"
            )
        else:
            tenant_context = ""

        html_body = _MAGIC_LINK_EMAIL_BODY.format(
            magic_link_url=magic_link_url,
            tenant_context=tenant_context,
        )
        full_html = _EMAIL_WRAPPER.format(body=html_body)
        await _send_magic_link_email(email, full_html)

        logger.info(
            "Magic link sent (member): tenant=%s email=%s",
            tid, email,
        )


@router.get(
    "/verify",
    summary="Verify magic link token and return session JWT",
    description="Validates the single-use token and returns an 8-hour "
    "session JWT for frontend authentication. If the user is an admin "
    "with 2FA enabled, returns a pending_2fa token instead.",
)
async def verify_magic_link(
    token: str = Query(description="Magic link token from email"),
) -> JSONResponse:
    """Verify token and issue session JWT (or pending 2FA challenge).

    Resolution logic:
      - If the token carries a member_id, look up the team member
        to get their current role. Include member_id + role in JWT.
      - If the member has an admin-level role and MFA is required,
        issue a short-lived pending_2fa token instead of a full session.
      - Non-admins and tenant owners get a full session immediately.
    """
    try:
        from src.multi_tenant.repositories import (
            TeamMemberRepository,
            VerificationTokenRepository,
        )

        token_repo = VerificationTokenRepository()

        doc = await token_repo.consume_token(
            token_id=token,
            token_type=_TOKEN_TYPE,
        )
        if not doc:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_token",
                    "message": "This sign-in link is invalid, has already been "
                    "used, or has expired. Please request a new one.",
                },
            )

        tenant_id = doc["tenant_id"]
        email = doc["email"]
        member_id = doc.get("member_id")  # None for tenant-owner magic links

        # Resolve team member role if token carries member_id
        role: str | None = None
        member_doc: dict | None = None
        if member_id:
            team_repo = TeamMemberRepository()
            try:
                member_doc = await team_repo.read(tenant_id, member_id)
                role = member_doc.get("role")
            except Exception:
                logger.warning(
                    "Team member lookup failed during verify: "
                    "tenant=%s member=%s",
                    tenant_id, member_id,
                )
                # Fall through — issue token without role (treated as admin)

        # Check if 2FA is required for this user
        from src.multi_tenant.admin_mfa_auth import (
            create_pending_2fa_token,
            requires_2fa,
        )
        if member_id and role and requires_2fa(role, member_doc):
            # Issue short-lived pending 2FA token instead of full session
            pending_token, pending_expires = create_pending_2fa_token(
                tenant_id, email, member_id, role,
            )
            logger.info(
                "Magic link verified (pending 2FA): tenant=%s email=%s "
                "member=%s role=%s",
                tenant_id, email, member_id, role,
            )
            return JSONResponse(
                content={
                    "requires_2fa": True,
                    "pending_2fa_token": pending_token,
                    "tenant_id": tenant_id,
                    "email": email,
                    "mfa_methods": _get_available_mfa_methods(member_doc),
                },
            )

        # Non-admin or no 2FA required — issue full session
        session_token, expires_at = create_magic_link_session_token(
            tenant_id, email,
            member_id=member_id,
            role=role,
        )

        logger.info(
            "Magic link verified: tenant=%s email=%s member=%s role=%s",
            tenant_id, email, member_id, role,
        )

        return JSONResponse(
            content={
                "session_token": session_token,
                "tenant_id": tenant_id,
                "email": email,
                "expires_at": expires_at,
            },
        )

    except Exception:
        logger.exception("Error verifying magic link")
        return JSONResponse(
            status_code=500,
            content={
                "error": "server_error",
                "message": "An unexpected error occurred. Please try again.",
            },
        )


def _get_available_mfa_methods(member_doc: dict | None) -> list[str]:
    """Determine which MFA methods are available for the user.

    Returns a list of available method strings: "totp", "sms", "backup".
    """
    methods: list[str] = []
    if not member_doc:
        return methods

    if member_doc.get("mfa_enabled"):
        methods.append("totp")

    if member_doc.get("mfa_backup_code_hashes"):
        methods.append("backup")

    if member_doc.get("phone_number") and member_doc.get("phone_verified"):
        from src.multi_tenant.sms_mfa_service import is_sms_available
        if is_sms_available():
            methods.append("sms")

    return methods
