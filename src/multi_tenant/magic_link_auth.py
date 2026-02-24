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

from src.multi_tenant.alert_delivery import EmailAlertChannel, _EMAIL_WRAPPER

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


# ---------------------------------------------------------------------------
# Email template
# ---------------------------------------------------------------------------

_MAGIC_LINK_EMAIL_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Sign In to Agent Red</h2>
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


def create_magic_link_session_token(tenant_id: str, email: str) -> tuple[str, str]:
    """Create an 8-hour session JWT for magic link authentication.

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
    """Send magic link email via ACS or SMTP."""
    subject = "[Agent Red] Sign In Link"
    conn_str = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
    if conn_str:
        try:
            from azure.communication.email import EmailClient

            client = EmailClient.from_connection_string(conn_str)
            message = {
                "senderAddress": EmailAlertChannel.SENDER_ADDRESS,
                "recipients": {"to": [{"address": to_email}]},
                "content": {"subject": subject, "html": html_body},
            }
            poller = client.begin_send(message)
            import asyncio
            result = await asyncio.to_thread(poller.result)
            return getattr(result, "status", "") == "Succeeded"
        except Exception:
            logger.exception("ACS email send failed for magic link")
            return False

    smtp_host = os.environ.get("SMTP_HOST", "")
    if smtp_host:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USERNAME", "")
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")
        from_addr = os.environ.get(
            "SMTP_FROM_ADDRESS", EmailAlertChannel.SENDER_ADDRESS,
        )

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"Agent Red <{from_addr}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(html_body, "html"))

            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                    if smtp_user:
                        server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    if smtp_port == 587:
                        server.starttls()
                    if smtp_user:
                        server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            return True
        except Exception:
            logger.exception("SMTP email send failed for magic link")
            return False

    logger.warning("No email provider configured for magic link delivery")
    return False


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
    """Send a magic link to the specified email address."""
    client_ip = request.client.host if request.client else "unknown"

    if _is_rate_limited(client_ip):
        logger.warning("Magic link rate limit exceeded: ip=%s", client_ip)
        return MagicLinkRequestResponse()

    try:
        from src.multi_tenant.repositories import (
            TenantRepository,
            VerificationTokenRepository,
        )

        tenant_repo = TenantRepository()
        token_repo = VerificationTokenRepository()

        email = body.email.strip().lower()

        # Look up tenant by customer email
        tenant = await tenant_repo.find_by_customer_email(email)
        if not tenant:
            # Silent failure — prevent email enumeration
            logger.info("Magic link request for unknown email: %s", email)
            return MagicLinkRequestResponse()

        tenant_id = tenant["id"]

        # Generate single-use token
        token_id = secrets.token_urlsafe(32)
        await token_repo.create_token(
            token_id=token_id,
            token_type=_TOKEN_TYPE,
            tenant_id=tenant_id,
            email=email,
            ttl=_TOKEN_TTL_SECONDS,
        )

        # Build magic link URL
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("host", request.url.hostname or "localhost")
        magic_link_url = (
            f"{scheme}://{host}/admin/standalone/verify-magic-link"
            f"?token={token_id}"
        )

        # Render and send email
        html_body = _MAGIC_LINK_EMAIL_BODY.format(magic_link_url=magic_link_url)
        full_html = _EMAIL_WRAPPER.format(body=html_body)
        await _send_magic_link_email(email, full_html)

        logger.info(
            "Magic link sent: tenant=%s email=%s", tenant_id, email,
        )
    except Exception:
        logger.exception("Error processing magic link request")

    return MagicLinkRequestResponse()


@router.get(
    "/verify",
    summary="Verify magic link token and return session JWT",
    description="Validates the single-use token and returns an 8-hour "
    "session JWT for frontend authentication.",
)
async def verify_magic_link(
    token: str = Query(description="Magic link token from email"),
) -> JSONResponse:
    """Verify token and issue session JWT."""
    try:
        from src.multi_tenant.repositories import VerificationTokenRepository

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

        # Generate session JWT
        session_token, expires_at = create_magic_link_session_token(
            tenant_id, email,
        )

        logger.info(
            "Magic link verified: tenant=%s email=%s", tenant_id, email,
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
