"""Trial expiry warning emails — sent at 7, 3, and 1 day(s) before trial end.

Follows the same dual-provider pattern as welcome_email.py and
widget_otp_verification.py (ACS primary, SMTP fallback, returns bool).

Called by the trial expiry warning background task in background.py.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Email body templates — one per urgency level
# ---------------------------------------------------------------------------

_EXPIRY_WARNING_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Your Trial {urgency_intro}</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  Your Agent Red trial has <strong>{days_remaining}</strong> remaining.
  {urgency_message}
</p>

<div style="text-align:center;margin:24px 0">
  <div style="display:inline-block;padding:12px 32px;background:{badge_bg};
       border:2px solid {badge_border};border-radius:8px;font-size:24px;
       font-weight:700;color:{badge_color}">
    {days_remaining} left
  </div>
</div>

<h3 style="margin:24px 0 12px;color:#111827;font-size:16px">What happens next?</h3>
<ul style="color:#374151;font-size:14px;line-height:1.8;margin:0;padding-left:20px">
  <li>When your trial ends, your widget will stop accepting new conversations</li>
  <li>Your configuration and conversation history are preserved</li>
  <li>Upgrade anytime to continue without interruption</li>
</ul>

<div style="text-align:center;margin:24px 0">
  <span style="display:inline-block;padding:12px 32px;background:#3B82F6;
       color:#ffffff;border-radius:6px;font-size:14px;font-weight:600;
       text-decoration:none">
    Upgrade Now
  </span>
</div>

<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:16px 0 0">
  Tenant ID: <code style="font-size:11px">{tenant_id}</code>
</p>
"""

# Per-tier urgency styling
_URGENCY_CONFIG = {
    "7d": {
        "urgency_intro": "Ends Soon",
        "urgency_message": "Consider upgrading to keep your customer experience running smoothly.",
        "badge_bg": "#eff6ff",
        "badge_border": "#93c5fd",
        "badge_color": "#1e40af",
        "subject": "Your Agent Red trial ends in 7 days",
    },
    "3d": {
        "urgency_intro": "Is Almost Over",
        "urgency_message": "Upgrade now to avoid any interruption to your customer conversations.",
        "badge_bg": "#fef3c7",
        "badge_border": "#fcd34d",
        "badge_color": "#92400e",
        "subject": "Your Agent Red trial ends in 3 days",
    },
    "1d": {
        "urgency_intro": "Ends Tomorrow",
        "urgency_message": "This is your final reminder. Your trial expires tomorrow.",
        "badge_bg": "#fee2e2",
        "badge_border": "#fca5a5",
        "badge_color": "#991b1b",
        "subject": "Your Agent Red trial ends tomorrow",
    },
}


# ---------------------------------------------------------------------------
# Send function
# ---------------------------------------------------------------------------


async def send_trial_expiry_warning(
    to_email: str,
    tenant_id: str,
    warning_tier: str,
) -> bool:
    """Send a trial expiry warning email.

    Args:
        to_email: Merchant's email address.
        tenant_id: The tenant ID.
        warning_tier: One of '7d', '3d', '1d'.

    Returns:
        True if sent successfully, False otherwise. Never raises.
    """
    if not to_email:
        logger.warning("No email — skipping trial warning for %s", tenant_id[:8])
        return False

    config = _URGENCY_CONFIG.get(warning_tier)
    if not config:
        logger.warning("Unknown warning tier %r for tenant %s", warning_tier, tenant_id[:8])
        return False

    from src.multi_tenant.alert_delivery import EmailAlertChannel, _EMAIL_WRAPPER

    days_label = {"7d": "7 days", "3d": "3 days", "1d": "1 day"}[warning_tier]

    html_body = _EXPIRY_WARNING_BODY.format(
        urgency_intro=config["urgency_intro"],
        urgency_message=config["urgency_message"],
        days_remaining=days_label,
        badge_bg=config["badge_bg"],
        badge_border=config["badge_border"],
        badge_color=config["badge_color"],
        tenant_id=tenant_id,
    )
    full_html = _EMAIL_WRAPPER.format(body=html_body)
    subject = config["subject"]

    # --- Provider 1: Azure Communication Services ---
    conn_str = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
    if conn_str:
        try:
            from azure.communication.email import EmailClient

            client = EmailClient.from_connection_string(conn_str)
            message = {
                "senderAddress": EmailAlertChannel.SENDER_ADDRESS,
                "recipients": {"to": [{"address": to_email}]},
                "content": {"subject": subject, "html": full_html},
            }
            poller = client.begin_send(message)
            import asyncio
            result = await asyncio.to_thread(poller.result)
            sent = getattr(result, "status", "") == "Succeeded"
            if sent:
                logger.info(
                    "Trial expiry warning sent via ACS: tenant=%s tier=%s email=%s",
                    tenant_id[:8], warning_tier, to_email,
                )
            return sent
        except Exception:
            logger.exception("ACS trial expiry email failed: tenant=%s", tenant_id[:8])
            return False

    # --- Provider 2: SMTP fallback ---
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
            msg.attach(MIMEText(full_html, "html"))

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

            logger.info(
                "Trial expiry warning sent via SMTP: tenant=%s tier=%s",
                tenant_id[:8], warning_tier,
            )
            return True
        except Exception:
            logger.exception("SMTP trial expiry email failed: tenant=%s", tenant_id[:8])
            return False

    logger.warning("No email provider — skipping trial expiry warning for %s", tenant_id[:8])
    return False
