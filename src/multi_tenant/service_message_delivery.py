"""Service message delivery — bulk BCC email to tenant superadmins.

Sends service messages (system announcements, update notices) from the
"Agent Red Service Administrator" to filtered sets of tenant superadmins.
Uses BCC delivery so that recipient email addresses are not disclosed
to each other.

Delivery pattern:
    SMTP primary (Titan) → ACS fallback.  Large recipient lists (>50)
    are batched to stay within provider limits.

Specifications: SPEC-1646, SPEC-1647, SPEC-1648.
Work items: WI-1000 (delivery), WI-0998 (API), WI-0999 (UI).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Maximum recipients per BCC batch — keeps within SMTP provider limits.
_BCC_BATCH_SIZE = 50

# Service administrator display name (SPEC-1647).
_SERVICE_SENDER_NAME = "Agent Red Service Administrator"


@dataclass
class ServiceMessageResult:
    """Result of a service message delivery attempt."""

    total_recipients: int = 0
    sent_count: int = 0
    failed_count: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.sent_count > 0 and self.failed_count == 0


async def send_service_message(
    subject: str,
    body_html: str,
    recipient_emails: list[str],
) -> ServiceMessageResult:
    """Send a service message to multiple superadmins via BCC.

    Uses the branded _EMAIL_WRAPPER template.  The ``To`` header is set to
    the SMTP_FROM address (service address) — all actual recipients are
    envelope-only (BCC).  This ensures no recipient can see another's
    email address (SPEC-1648).

    Args:
        subject: Email subject line.
        body_html: HTML body content (inner, without wrapper).
        recipient_emails: De-duplicated list of superadmin emails.

    Returns:
        ServiceMessageResult with delivery statistics.
    """
    if not recipient_emails:
        return ServiceMessageResult()

    from src.multi_tenant.alert_delivery import format_branded_email

    full_html = format_branded_email(body_html)
    result = ServiceMessageResult(total_recipients=len(recipient_emails))

    # Batch recipients to stay within provider limits
    batches = [
        recipient_emails[i : i + _BCC_BATCH_SIZE]
        for i in range(0, len(recipient_emails), _BCC_BATCH_SIZE)
    ]

    for batch in batches:
        sent = await _send_bcc_batch(subject, full_html, batch)
        if sent:
            result.sent_count += len(batch)
        else:
            result.failed_count += len(batch)
            result.errors.append(
                f"Batch of {len(batch)} failed (first: {batch[0][:20]}...)"
            )

    return result


async def _send_bcc_batch(
    subject: str,
    full_html: str,
    recipients: list[str],
) -> bool:
    """Send a single BCC batch via SMTP primary / ACS fallback.

    Returns True on success, False on failure.
    """
    # --- Provider 1: SMTP (Titan or other) ---
    smtp_host = os.environ.get("SMTP_HOST", "")
    if smtp_host:
        try:
            sent = await _smtp_bcc_send(smtp_host, subject, full_html, recipients)
            if sent:
                logger.info(
                    "Service message sent via SMTP: %d recipients, subject=%s",
                    len(recipients),
                    subject[:60],
                )
                return True
        except Exception:
            logger.exception(
                "SMTP service message failed (%d recipients) — trying ACS",
                len(recipients),
            )

    # --- Provider 2: ACS fallback (individual sends — ACS lacks BCC) ---
    conn_str = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
    if conn_str:
        try:
            sent = await _acs_individual_send(conn_str, subject, full_html, recipients)
            if sent:
                logger.info(
                    "Service message sent via ACS: %d recipients, subject=%s",
                    len(recipients),
                    subject[:60],
                )
                return True
        except Exception:
            logger.exception(
                "ACS service message failed (%d recipients)", len(recipients),
            )

    logger.warning("No email provider configured — service message not sent")
    return False


async def _smtp_bcc_send(
    smtp_host: str,
    subject: str,
    full_html: str,
    recipients: list[str],
) -> bool:
    """Send via SMTP with BCC — ``To`` set to service address, recipients
    receive via envelope-only addressing (SPEC-1648)."""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USERNAME", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    smtp_from = os.environ.get("SMTP_FROM", smtp_user)

    def _send() -> None:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{_SERVICE_SENDER_NAME} <{smtp_from}>"
        msg["To"] = smtp_from  # Service address only — no recipient disclosure
        msg["Subject"] = subject
        msg.attach(MIMEText(full_html, "html"))

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30) as server:
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                # sendmail envelope includes all BCC recipients
                server.sendmail(smtp_from, recipients, msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                server.ehlo()
                if smtp_port != 25:
                    server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_from, recipients, msg.as_string())

    await asyncio.to_thread(_send)
    return True


async def _acs_individual_send(
    conn_str: str,
    subject: str,
    full_html: str,
    recipients: list[str],
) -> bool:
    """ACS fallback — send individually (ACS does not support BCC).

    Each recipient gets their own email. This is slower but preserves
    the no-disclosure guarantee (SPEC-1648).
    """
    from src.multi_tenant.alert_delivery import send_acs_email

    all_ok = True
    for email_addr in recipients:
        try:
            status = await send_acs_email(conn_str, email_addr, subject, full_html)
            if status != "Succeeded":
                logger.warning(
                    "ACS service message status=%s for %s", status, email_addr[:20],
                )
                all_ok = False
        except Exception:
            logger.exception("ACS service message failed for %s", email_addr[:20])
            all_ok = False

    return all_ok


def render_service_message_body(body_text: str) -> str:
    """Render the inner HTML for a service message.

    Wraps the provider-authored body text in the standard service message
    styling.  The outer branded wrapper (_EMAIL_WRAPPER) is applied
    separately by send_service_message().

    Args:
        body_text: HTML body content authored by the provider.

    Returns:
        Formatted inner HTML string.
    """
    return (
        '<h2 style="margin:0 0 16px;color:#111827;font-size:20px">'
        "Service Message</h2>\n"
        '<div style="background:#f8fafc;border:1px solid #e2e8f0;'
        'padding:16px;margin:16px 0">\n'
        f"  {body_text}\n"
        "</div>\n"
        '<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:16px 0 0">'
        "This is a service message from your Agent Red platform provider. "
        "Please do not reply to this email."
        "</p>"
    )
