"""Email verification endpoints.

Provides endpoints to request and confirm email verification for
tenant notification addresses. Uses the ``verification_tokens``
Cosmos DB collection with TTL-based auto-expiry.

Endpoints:
    POST /api/auth/verify-email/request  — Send verification email (public)
    GET  /api/auth/verify-email/confirm  — Confirm token and mark verified

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import secrets
import time
from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from src.multi_tenant.alert_delivery import EmailAlertChannel, _EMAIL_WRAPPER

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth/verify-email",
    tags=["Email Verification"],
)

# ---------------------------------------------------------------------------
# Rate limiting (in-memory, per-instance)
# ---------------------------------------------------------------------------

_RATE_WINDOW = 300.0  # 5 minutes
_RATE_MAX = 3  # max 3 requests per window per IP

_rate_limit: dict[str, list[float]] = {}


def _is_rate_limited(client_ip: str) -> bool:
    """Check if IP has exceeded verification request rate limit."""
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


class VerifyEmailRequest(BaseModel):
    """Request body for email verification."""
    tenant_id: str = Field(description="Tenant ID requesting verification")
    email: str = Field(description="Email address to verify")


class VerifyEmailResponse(BaseModel):
    """Uniform response — never reveals whether the email exists."""
    message: str = Field(
        default="If this email is associated with a tenant, a verification "
        "link has been sent. Please check your inbox.",
    )


# ---------------------------------------------------------------------------
# Email template
# ---------------------------------------------------------------------------

_VERIFY_EMAIL_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Verify Your Email Address</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  Click the button below to verify your email address for Agent Red Customer Experience.
  This link will expire in 10 minutes.
</p>
<div style="text-align:center;margin:24px 0">
  <a href="{verify_url}" style="display:inline-block;padding:12px 32px;background:#ff3621;
     color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;border-radius:6px">
    Verify Email
  </a>
</div>
<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:16px 0 0">
  If you did not request this verification, you can safely ignore this email.
</p>
"""


# ---------------------------------------------------------------------------
# Confirmation page template
# ---------------------------------------------------------------------------

_CONFIRM_SUCCESS_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Email Verified — Agent Red</title>
<style>
  body {{ margin:0; padding:0; background:#141414; font-family:Inter,-apple-system,sans-serif;
         display:flex; align-items:center; justify-content:center; min-height:100vh; }}
  .card {{ background:#1f1f1f; border-radius:12px; padding:48px; max-width:440px;
           text-align:center; box-shadow:0 4px 24px rgba(0,0,0,.3); }}
  .check {{ width:64px; height:64px; margin:0 auto 24px; background:#0D7C3E;
            border-radius:50%; display:flex; align-items:center; justify-content:center; }}
  .check svg {{ width:32px; height:32px; fill:#fff; }}
  h1 {{ color:#f5f5f5; font-size:24px; margin:0 0 12px; }}
  p {{ color:#a0a0a0; font-size:14px; line-height:1.6; margin:0; }}
  .brand {{ color:#ff3621; font-weight:600; }}
</style>
</head>
<body>
<div class="card">
  <div class="check"><svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg></div>
  <h1>Email Verified</h1>
  <p>Your email address <strong>{email}</strong> has been verified for
     <span class="brand">Agent Red</span> Customer Experience.</p>
</div>
</body>
</html>"""

_CONFIRM_ERROR_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Verification Failed — Agent Red</title>
<style>
  body {{ margin:0; padding:0; background:#141414; font-family:Inter,-apple-system,sans-serif;
         display:flex; align-items:center; justify-content:center; min-height:100vh; }}
  .card {{ background:#1f1f1f; border-radius:12px; padding:48px; max-width:440px;
           text-align:center; box-shadow:0 4px 24px rgba(0,0,0,.3); }}
  .icon {{ width:64px; height:64px; margin:0 auto 24px; background:#D32F2F;
           border-radius:50%; display:flex; align-items:center; justify-content:center; }}
  .icon svg {{ width:32px; height:32px; fill:#fff; }}
  h1 {{ color:#f5f5f5; font-size:24px; margin:0 0 12px; }}
  p {{ color:#a0a0a0; font-size:14px; line-height:1.6; margin:0; }}
</style>
</head>
<body>
<div class="card">
  <div class="icon"><svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/></svg></div>
  <h1>Verification Failed</h1>
  <p>{reason}</p>
</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/request",
    response_model=VerifyEmailResponse,
    summary="Request email verification (public)",
    description="Sends a verification email with a 10-minute link. "
    "Rate-limited to 3 requests per 5 minutes per IP.",
)
async def request_verification(
    body: VerifyEmailRequest,
    request: Request,
) -> VerifyEmailResponse:
    """Send a verification email to the specified address.

    This is a PUBLIC endpoint — no authentication required.
    Always returns the same message regardless of success or failure
    to prevent email enumeration.
    """
    client_ip = request.client.host if request.client else "unknown"

    if _is_rate_limited(client_ip):
        logger.warning(
            "Email verification rate limit exceeded: ip=%s", client_ip,
        )
        return VerifyEmailResponse()

    try:
        from src.multi_tenant.repositories import (
            PreferencesRepository,
            TenantRepository,
            VerificationTokenRepository,
        )

        token_repo = VerificationTokenRepository()
        tenant_repo = TenantRepository()

        # Verify tenant exists (silently fail if not)
        try:
            tenant = await tenant_repo.read(body.tenant_id, body.tenant_id)
            if not tenant:
                return VerifyEmailResponse()
        except Exception:
            return VerifyEmailResponse()

        # Generate token
        token_id = secrets.token_urlsafe(32)

        await token_repo.create_token(
            token_id=token_id,
            token_type="email_verification",
            tenant_id=body.tenant_id,
            email=body.email,
        )

        # Build verification URL
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("host", request.url.hostname or "localhost")
        verify_url = (
            f"{scheme}://{host}/api/auth/verify-email/confirm"
            f"?token={token_id}"
        )

        # Render and send email
        html_body = _VERIFY_EMAIL_BODY.format(verify_url=verify_url)
        full_html = _EMAIL_WRAPPER.format(body=html_body)
        subject = "[Agent Red] Verify Your Email Address"

        await _send_verification_email(body.email, subject, full_html)

        logger.info(
            "Verification email sent: tenant=%s email=%s",
            body.tenant_id, body.email,
        )

    except Exception:
        # Never reveal errors to the caller
        logger.exception("Error in email verification request")

    return VerifyEmailResponse()


@router.get(
    "/confirm",
    response_class=HTMLResponse,
    summary="Confirm email verification",
    description="Validates the token and marks the email as verified. "
    "Renders a branded confirmation page.",
)
async def confirm_verification(
    token: str = Query(description="Verification token from email link"),
) -> HTMLResponse:
    """Validate verification token and mark email as verified.

    Returns an HTML page showing success or failure — this endpoint
    is opened directly by the user clicking the email link.
    """
    try:
        from src.multi_tenant.repositories import (
            PreferencesRepository,
            VerificationTokenRepository,
        )

        token_repo = VerificationTokenRepository()
        prefs_repo = PreferencesRepository()

        # Consume token (single-use)
        doc = await token_repo.consume_token(
            token_id=token,
            token_type="email_verification",
        )
        if not doc:
            return HTMLResponse(
                content=_CONFIRM_ERROR_HTML.format(
                    reason="This verification link is invalid, has already "
                    "been used, or has expired. Please request a new one.",
                ),
                status_code=400,
            )

        tenant_id = doc["tenant_id"]
        email = doc["email"]

        # Update tenant preferences with verified email
        try:
            prefs = await prefs_repo.read(tenant_id, tenant_id)
            if prefs:
                await prefs_repo.patch(
                    tenant_id=tenant_id,
                    document_id=tenant_id,
                    operations=[
                        {"op": "set", "path": "/notification_email", "value": email},
                        {"op": "set", "path": "/email_verified", "value": True},
                    ],
                )
            else:
                # Create preferences document if it doesn't exist
                from datetime import datetime, timezone

                await prefs_repo.upsert(
                    tenant_id=tenant_id,
                    document={
                        "id": tenant_id,
                        "tenant_id": tenant_id,
                        "notification_email": email,
                        "email_verified": True,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
        except Exception:
            logger.exception(
                "Failed to update preferences after verification: tenant=%s",
                tenant_id,
            )
            return HTMLResponse(
                content=_CONFIRM_ERROR_HTML.format(
                    reason="Verification succeeded but we couldn't update "
                    "your settings. Please try again or contact support.",
                ),
                status_code=500,
            )

        logger.info(
            "Email verified: tenant=%s email=%s", tenant_id, email,
        )

        return HTMLResponse(
            content=_CONFIRM_SUCCESS_HTML.format(email=email),
        )

    except Exception:
        logger.exception("Error in email verification confirm")
        return HTMLResponse(
            content=_CONFIRM_ERROR_HTML.format(
                reason="An unexpected error occurred. Please try again.",
            ),
            status_code=500,
        )


# ---------------------------------------------------------------------------
# Email sending helper
# ---------------------------------------------------------------------------


async def _send_verification_email(
    to_email: str,
    subject: str,
    html_body: str,
) -> bool:
    """Send a verification email using ACS or SMTP.

    Reuses the same provider selection logic as EmailAlertChannel.
    """
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
            logger.exception("ACS email send failed for verification")
            return False

    smtp_host = os.environ.get("SMTP_HOST", "")
    if smtp_host:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USERNAME", "")
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"Agent Red <{EmailAlertChannel.SENDER_ADDRESS}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(html_body, "html"))

            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                    if smtp_user and smtp_pass:
                        server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.ehlo()
                    if smtp_port != 25:
                        server.starttls()
                    if smtp_user and smtp_pass:
                        server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            return True
        except Exception:
            logger.exception("SMTP email send failed for verification")
            return False

    logger.warning("No email provider configured for verification email")
    return False
