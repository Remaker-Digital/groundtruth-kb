"""Email Change Request & Confirmation (SPEC-1682, SPEC-1683).

Two-phase email change flow for platform admins:

1. **Request** (authenticated): Admin submits new email address.
   - Confirmation email sent to NEW address (single-use 15-min token).
   - Security notification sent to OLD address.
   - Pending change stored in preferences.

2. **Confirm** (public): Recipient clicks link in confirmation email.
   - Token consumed (single-use, auto-expires via Cosmos TTL).
   - Auth email updated on the platform admin document.
   - Completion notification sent to OLD address.

Endpoints:
    POST /api/admin/email/request  -- Authenticated (requires platform admin)
    GET  /api/admin/email/confirm   -- Public (token-based)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import secrets
import time
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin/email",
    tags=["Email Change"],
)

# ---------------------------------------------------------------------------
# Rate limiting (in-memory, per-instance)
# ---------------------------------------------------------------------------

_RATE_WINDOW = 900.0  # 15 minutes
_RATE_MAX = 3  # max 3 requests per window per IP

_rate_limit: dict[str, list[float]] = {}


def _is_rate_limited(client_ip: str) -> bool:
    """Check if IP has exceeded email change request rate limit."""
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
# Token type constant
# ---------------------------------------------------------------------------

_TOKEN_TYPE = "email_change"
_TOKEN_TTL = 900  # 15 minutes


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class EmailChangeRequest(BaseModel):
    """Request body for email change."""
    new_email: str = Field(description="New email address to change to")


class EmailChangeResponse(BaseModel):
    """Response for email change request."""
    ok: bool
    message: str


# ---------------------------------------------------------------------------
# Email templates
# ---------------------------------------------------------------------------

_CONFIRM_EMAIL_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">
  Confirm Your New Email Address
</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 16px">
  A request was made to change your Agent Red platform admin email
  address to this address.
</p>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  Click the button below to confirm. This link expires in 15 minutes.
</p>
<div style="text-align:center;margin:24px 0">
  <a href="{confirm_url}" style="display:inline-block;padding:12px 32px;background:#ff3621;
     color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;border-radius:6px">
    Confirm Email Change
  </a>
</div>
<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:16px 0 0">
  If you did not request this change, you can safely ignore this email.
  Your current email will remain unchanged.
</p>
<p style="color:#9ca3af;font-size:11px;line-height:1.5;margin:8px 0 0">
  Or paste this URL into your browser:<br/>
  <span style="word-break:break-all">{confirm_url}</span>
</p>
"""

_SECURITY_ALERT_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">
  Email Change Requested
</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 16px">
  A request was made to change the email address on your Agent Red
  platform admin account from <strong>{old_email}</strong> to
  <strong>{new_email}</strong>.
</p>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  If you did not make this request, rotate your API key and
  generate new backup codes immediately.
</p>
<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:0">
  Time: {timestamp}
</p>
"""

_COMPLETION_ALERT_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">
  Email Address Changed
</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 16px">
  Your Agent Red platform admin email has been changed from
  <strong>{old_email}</strong> to <strong>{new_email}</strong>.
</p>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  If you did not authorize this change, contact support immediately.
</p>
"""


# ---------------------------------------------------------------------------
# Confirmation page templates (reuse pattern from email_verification.py)
# ---------------------------------------------------------------------------

_CONFIRM_SUCCESS_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Email Changed — Agent Red</title>
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
  <h1>Email Address Updated</h1>
  <p>Your <span class="brand">Agent Red</span> platform admin email has been
     changed to <strong>{email}</strong>. You can close this tab.</p>
</div>
</body>
</html>"""

_CONFIRM_ERROR_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Email Change Failed — Agent Red</title>
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
  <h1>Email Change Failed</h1>
  <p>{reason}</p>
</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Email sending helper (SMTP > ACS fallback)
# ---------------------------------------------------------------------------


async def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send an email using SMTP or ACS (same pattern as email_verification.py)."""
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

        try:
            await asyncio.to_thread(_smtp_send)
            return True
        except Exception:
            logger.exception("SMTP send failed for email change -- trying ACS")

    # --- Provider 2: Azure Communication Services (fallback) ---
    conn_str = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
    if conn_str:
        try:
            from src.multi_tenant.alert_delivery import send_acs_email

            status = await send_acs_email(conn_str, to_email, subject, html_body)
            return status == "Succeeded"
        except Exception:
            logger.exception("ACS send failed for email change")
            return False

    logger.warning("No email provider configured for email change")
    return False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/request",
    response_model=EmailChangeResponse,
    summary="Request email change (authenticated)",
    description="Sends confirmation to NEW email, security alert to OLD email. "
    "Rate-limited to 3 per 15 minutes per IP.",
)
async def request_email_change(
    body: EmailChangeRequest,
    request: Request,
    ctx: TenantContext = Depends(get_tenant_context),
) -> EmailChangeResponse:
    """Request an email address change for the current platform admin.

    Requires authentication. Sends:
    1. Confirmation email to the NEW address (with 15-min single-use token).
    2. Security notification to the OLD address.
    """
    client_ip = request.client.host if request.client else "unknown"

    if _is_rate_limited(client_ip):
        logger.warning("Email change rate limit: ip=%s", client_ip)
        return EmailChangeResponse(
            ok=False,
            message="Too many requests. Please wait before trying again.",
        )

    # Must be a platform admin
    if not ctx.is_platform_admin:
        return EmailChangeResponse(
            ok=False,
            message="Only platform administrators can change their email.",
        )

    old_email = ctx.platform_admin_email or ""
    new_email = body.new_email.strip().lower()

    if not new_email or "@" not in new_email:
        return EmailChangeResponse(ok=False, message="Invalid email address.")

    if new_email == old_email:
        return EmailChangeResponse(
            ok=False, message="New email is the same as your current email.",
        )

    try:
        from src.multi_tenant.repositories import (
            PlatformAdminRepository,
            VerificationTokenRepository,
        )

        token_repo = VerificationTokenRepository()

        # Generate single-use token
        token_id = secrets.token_urlsafe(32)
        await token_repo.create_token(
            token_id=token_id,
            token_type=_TOKEN_TYPE,
            tenant_id="__platform__",
            email=new_email,
            ttl=_TOKEN_TTL,
        )

        # Store old email in token metadata for the confirm step
        # We patch the token doc to include the old_email
        try:
            await token_repo._container.patch_item(
                item=token_id,
                partition_key=_TOKEN_TYPE,
                patch_operations=[
                    {"op": "add", "path": "/old_email", "value": old_email},
                    {"op": "add", "path": "/admin_id", "value": ctx.platform_admin_id or ""},
                ],
            )
        except Exception:
            logger.warning("Could not patch token with old_email metadata")

        # Build confirmation URL
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("host", request.url.hostname or "localhost")
        confirm_url = f"{scheme}://{host}/api/admin/email/confirm?token={token_id}"

        from datetime import datetime, timezone

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # 1. Send confirmation email to NEW address
        confirm_html = _CONFIRM_EMAIL_BODY.format(confirm_url=confirm_url)
        full_confirm = _EMAIL_WRAPPER.format(body=confirm_html)
        await _send_email(
            new_email,
            "[Agent Red] Confirm Your New Email Address",
            full_confirm,
        )

        # 2. Send security alert to OLD address
        if old_email:
            alert_html = _SECURITY_ALERT_BODY.format(
                old_email=old_email,
                new_email=new_email,
                timestamp=timestamp,
            )
            full_alert = _EMAIL_WRAPPER.format(body=alert_html)
            await _send_email(
                old_email,
                "[Agent Red] Email Change Requested",
                full_alert,
            )

        # 3. Emit communication events (SPEC-1687)
        try:
            from src.multi_tenant.communication_capture import emit_communication_event

            emit_communication_event(
                event_type="email_change_confirmation",
                recipient=new_email,
                channel="email",
                subject="Confirm Your New Email Address",
                body=full_confirm,
                token=token_id,
                ttl_minutes=15,
                metadata={"old_email": old_email},
            )
            if old_email:
                emit_communication_event(
                    event_type="email_change_security_alert",
                    recipient=old_email,
                    channel="email",
                    subject="Email Change Requested",
                    body=full_alert,
                    metadata={"new_email": new_email},
                )
        except Exception:
            logger.debug("Communication capture not available")

        logger.info(
            "Email change requested: old=%s new=%s admin=%s",
            old_email, new_email, ctx.platform_admin_id,
        )

        return EmailChangeResponse(
            ok=True,
            message="A confirmation email has been sent to your new address. "
            "Please check your inbox and click the link to complete the change.",
        )

    except Exception:
        logger.exception("Error in email change request")
        return EmailChangeResponse(
            ok=False,
            message="An error occurred. Please try again later.",
        )


@router.get(
    "/confirm",
    response_class=HTMLResponse,
    summary="Confirm email change (public)",
    description="Validates the token and updates the platform admin email. "
    "Renders a branded confirmation page.",
)
async def confirm_email_change(
    token: str = Query(description="Email change token from confirmation email"),
) -> HTMLResponse:
    """Validate email change token and update the admin email.

    This is a PUBLIC endpoint (token-based auth). The user clicks the
    link in the confirmation email, which opens this endpoint directly.

    On success:
    1. Updates the platform admin email in Cosmos.
    2. Sends a completion notification to the OLD address.
    3. Returns a branded success page.
    """
    try:
        from src.multi_tenant.repositories import (
            PlatformAdminRepository,
            VerificationTokenRepository,
        )

        token_repo = VerificationTokenRepository()

        # Consume token (single-use, atomic)
        doc = await token_repo.consume_token(
            token_id=token,
            token_type=_TOKEN_TYPE,
        )
        if not doc:
            return HTMLResponse(
                content=_CONFIRM_ERROR_HTML.format(
                    reason="This link is invalid, has already been used, or has "
                    "expired. Please request a new email change.",
                ),
                status_code=400,
            )

        new_email = doc["email"]
        old_email = doc.get("old_email", "")
        admin_id = doc.get("admin_id", "")

        # Update the platform admin email in Cosmos
        admin_repo = PlatformAdminRepository()
        try:
            if admin_id:
                # Patch the platform admin document with new email
                await admin_repo._container.patch_item(
                    item=admin_id,
                    partition_key="__platform__",
                    patch_operations=[
                        {"op": "set", "path": "/email", "value": new_email},
                    ],
                )
            else:
                logger.warning(
                    "Email change confirmed but no admin_id in token: email=%s",
                    new_email,
                )
        except Exception:
            logger.exception(
                "Failed to update admin email: admin_id=%s new=%s",
                admin_id, new_email,
            )
            return HTMLResponse(
                content=_CONFIRM_ERROR_HTML.format(
                    reason="Your email change was verified but we could not "
                    "update your account. Please contact support.",
                ),
                status_code=500,
            )

        # Send completion notification to OLD address
        if old_email:
            try:
                completion_html = _COMPLETION_ALERT_BODY.format(
                    old_email=old_email,
                    new_email=new_email,
                )
                full_html = _EMAIL_WRAPPER.format(body=completion_html)
                await _send_email(
                    old_email,
                    "[Agent Red] Email Address Changed",
                    full_html,
                )

                # Emit communication event (SPEC-1687)
                try:
                    from src.multi_tenant.communication_capture import emit_communication_event

                    emit_communication_event(
                        event_type="email_change_completed",
                        recipient=old_email,
                        channel="email",
                        subject="Email Address Changed",
                        body=full_html,
                        metadata={"new_email": new_email, "admin_id": admin_id},
                    )
                except Exception:
                    pass
            except Exception:
                # Non-critical -- log but don't fail the change
                logger.warning("Completion notification failed: old=%s", old_email)

        logger.info(
            "Email change confirmed: admin=%s old=%s new=%s",
            admin_id, old_email, new_email,
        )

        return HTMLResponse(
            content=_CONFIRM_SUCCESS_HTML.format(email=new_email),
        )

    except Exception:
        logger.exception("Error in email change confirmation")
        return HTMLResponse(
            content=_CONFIRM_ERROR_HTML.format(
                reason="An unexpected error occurred. Please try again.",
            ),
            status_code=500,
        )
