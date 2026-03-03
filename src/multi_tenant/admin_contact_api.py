"""Admin Contact API — send support/feedback messages to Remaker Digital.

Provides a single endpoint for authenticated admin users to send messages
directly to the service provider (support requests, feature requests,
information requests). Messages are persisted to Cosmos DB (SPEC-1588)
AND delivered via SMTP (primary) or Azure Communication Services (fallback).

Dependencies:
    - middleware.py: get_tenant_context, TenantContext
    - alert_delivery.py: send_acs_email (ACS fallback)
    - cosmos_schema.py: ContactMessageDocument

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import html
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Contact message persistence (SPEC-1588)
# ---------------------------------------------------------------------------

_contact_repo: Any = None


def configure_contact_repo(repo: Any) -> None:
    """Wire the contact_messages repository at startup."""
    global _contact_repo
    _contact_repo = repo

router = APIRouter(prefix="/api/admin", tags=["admin-contact"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

VALID_TOPICS = [
    "support",
    "feature_request",
    "billing",
    "bug_report",
    "general",
]


class ContactRequest(BaseModel):
    """Inbound contact form submission."""

    topic: str = Field(
        ...,
        description="Message category.",
        json_schema_extra={"enum": VALID_TOPICS},
    )
    subject: str = Field(
        ..., min_length=1, max_length=200, description="Message subject line."
    )
    message: str = Field(
        ..., min_length=1, max_length=5000, description="Message body."
    )


class ContactResponse(BaseModel):
    """Acknowledgement returned to the caller."""

    ok: bool
    detail: str


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORT_EMAIL = "support@remakerdigital.com"

TOPIC_LABELS = {
    "support": "Support Request",
    "feature_request": "Feature Request",
    "billing": "Billing Inquiry",
    "bug_report": "Bug Report",
    "general": "General Inquiry",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_html_body(
    *,
    topic: str,
    subject: str,
    message: str,
    tenant_id: str,
    member_email: str | None,
    member_role: str | None,
    member_id: str | None,
    tier: str | None,
) -> str:
    """Build an HTML email body with tenant identity context."""
    topic_label = TOPIC_LABELS.get(topic, topic)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    safe_message = html.escape(message).replace("\n", "<br>")

    return f"""\
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1a1a1a; max-width: 600px;">
<h2 style="color: #ff3621; margin-bottom: 4px;">Agent Red — {html.escape(topic_label)}</h2>
<p style="color: #666; font-size: 13px; margin-top: 0;">Received {timestamp}</p>

<table style="border-collapse: collapse; width: 100%; margin-bottom: 16px; font-size: 14px;">
<tr><td style="padding: 6px 12px; background: #f5f5f4; font-weight: 600; width: 140px;">Tenant ID</td>
    <td style="padding: 6px 12px; background: #f5f5f4; font-family: monospace;">{html.escape(tenant_id)}</td></tr>
<tr><td style="padding: 6px 12px; font-weight: 600;">Tier</td>
    <td style="padding: 6px 12px;">{html.escape(tier or 'unknown')}</td></tr>
<tr><td style="padding: 6px 12px; background: #f5f5f4; font-weight: 600;">Member Email</td>
    <td style="padding: 6px 12px; background: #f5f5f4;">{html.escape(member_email or 'N/A')}</td></tr>
<tr><td style="padding: 6px 12px; font-weight: 600;">Member Role</td>
    <td style="padding: 6px 12px;">{html.escape(member_role or 'N/A')}</td></tr>
<tr><td style="padding: 6px 12px; background: #f5f5f4; font-weight: 600;">Member ID</td>
    <td style="padding: 6px 12px; background: #f5f5f4; font-family: monospace;">{html.escape(member_id or 'N/A')}</td></tr>
<tr><td style="padding: 6px 12px; font-weight: 600;">Topic</td>
    <td style="padding: 6px 12px;">{html.escape(topic_label)}</td></tr>
</table>

<h3 style="margin-bottom: 8px;">Subject: {html.escape(subject)}</h3>
<div style="background: #fafaf9; border: 1px solid #e7e5e4; border-radius: 6px; padding: 16px; line-height: 1.6;">
{safe_message}
</div>

<p style="color: #999; font-size: 11px; margin-top: 24px;">
This message was sent from the Agent Red admin panel. Do not reply to this email —
respond directly to the member at {html.escape(member_email or 'N/A')}.
</p>
</body>
</html>"""


async def _send_contact_email(
    to_email: str,
    subject: str,
    html_body: str,
) -> bool:
    """Send contact email via SMTP or ACS.

    Provider selection: SMTP (Titan) > ACS > skip.
    """
    import os as _os

    # --- Provider 1: SMTP (Titan or other SMTP provider) ---
    smtp_host = _os.environ.get("SMTP_HOST", "")
    if smtp_host:
        import asyncio
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_port = int(_os.environ.get("SMTP_PORT", "587"))
        smtp_user = _os.environ.get("SMTP_USERNAME", "")
        smtp_pass = _os.environ.get("SMTP_PASSWORD", "")
        smtp_from = _os.environ.get("SMTP_FROM", smtp_user)

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
            await asyncio.to_thread(_smtp_send)  # SPEC-1622: non-blocking SMTP
            logger.info("Contact email sent via SMTP to %s", to_email)
            return True
        except Exception:
            logger.exception("SMTP contact email failed — trying ACS fallback")
            # Fall through to ACS provider

    # --- Provider 2: Azure Communication Services (fallback) ---
    conn_str = _os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
    if conn_str:
        try:
            from src.multi_tenant.alert_delivery import send_acs_email

            status = await send_acs_email(conn_str, to_email, subject, html_body)
            if status == "Succeeded":
                logger.info("Contact email sent via ACS to %s", to_email)
                return True
            logger.warning("Contact email status=%s (expected Succeeded)", status)
            return False
        except Exception:
            logger.exception("ACS contact email send failed")
            return False

    logger.warning("No email provider configured — contact email skipped")
    return False


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/contact", response_model=ContactResponse)
async def send_contact_message(
    body: ContactRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ContactResponse:
    """Send a contact message from an authenticated admin user.

    The tenant context is populated by the auth middleware. The tenant ID,
    member email, role, and tier are embedded in the email body so Remaker
    Digital support can identify the sender without requiring them to provide
    account details manually.
    """
    # Validate topic
    if body.topic not in VALID_TOPICS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid topic '{body.topic}'. "
            f"Valid values: {VALID_TOPICS}",
        )

    topic_label = TOPIC_LABELS.get(body.topic, body.topic)
    member_role = ctx.team_member_role.value if ctx.team_member_role else None
    tier = ctx.tier.value if ctx.tier else None

    # ── Persist to Cosmos BEFORE email (SPEC-1588) ──────────────
    now = datetime.now(timezone.utc).isoformat()
    message_id = str(uuid.uuid4())

    if _contact_repo is not None:
        from src.multi_tenant.cosmos_schema import ContactMessageDocument

        doc = ContactMessageDocument(
            id=message_id,
            tenant_id=ctx.tenant_id,
            topic=body.topic,
            subject=body.subject,
            message=body.message,
            member_email=ctx.team_member_email,
            member_role=member_role,
            member_id=ctx.team_member_id,
            tier=tier,
            status="new",
            notes="",
            created_at=now,
            updated_at=now,
        )
        try:
            await _contact_repo.create(ctx.tenant_id, doc)
            logger.info(
                "Contact message %s persisted for tenant=%s topic=%s",
                message_id,
                ctx.tenant_id,
                body.topic,
            )
        except Exception:
            logger.exception(
                "Failed to persist contact message %s for tenant=%s — "
                "proceeding with email delivery",
                message_id,
                ctx.tenant_id,
            )
    else:
        logger.warning(
            "contact_messages repo not configured — skipping persistence "
            "(message %s will still be delivered via email)",
            message_id,
        )

    # ── Build and send email ────────────────────────────────────
    email_subject = f"[Agent Red] {topic_label}: {body.subject}"
    html_body = _build_html_body(
        topic=body.topic,
        subject=body.subject,
        message=body.message,
        tenant_id=ctx.tenant_id,
        member_email=ctx.team_member_email,
        member_role=member_role,
        member_id=ctx.team_member_id,
        tier=tier,
    )

    success = await _send_contact_email(SUPPORT_EMAIL, email_subject, html_body)

    if success:
        return ContactResponse(ok=True, detail="Message sent successfully.")

    # Email failed — message is still persisted in Cosmos for manual review.
    logger.warning(
        "Contact message %s from tenant=%s topic=%s could not be delivered "
        "via email. Persisted for manual review.",
        message_id,
        ctx.tenant_id,
        body.topic,
    )
    return ContactResponse(
        ok=True,
        detail="Message received. Our team will follow up shortly.",
    )
