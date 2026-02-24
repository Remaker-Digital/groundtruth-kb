"""Access expiry warning emails — sent at 7, 3, and 1 day(s) before expiry.

Follows the same dual-provider pattern as trial_expiry_email.py and
welcome_email.py (ACS primary, SMTP fallback, returns bool).

Called by the access expiry warning background task in background.py.

Unlike trial expiry emails (which say "upgrade to a paid plan"), these
messages reference contacting the service provider to renew access.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Email body templates — one per urgency level
# ---------------------------------------------------------------------------

_ACCESS_EXPIRY_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Your Access {urgency_intro}</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  Your Agent Red access has <strong>{days_remaining}</strong> remaining.
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
  <li>When your access expires, your widget will stop accepting new conversations</li>
  <li>Your configuration and conversation history are preserved</li>
  <li>Contact your service provider to renew or extend access</li>
</ul>

<div style="text-align:center;margin:24px 0">
  <a href="{admin_login_url}" style="display:inline-block;padding:12px 32px;background:#3B82F6;
       color:#ffffff;border-radius:6px;font-size:14px;font-weight:600;
       text-decoration:none">
    Sign in to Dashboard
  </a>
</div>

<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:16px 0 0">
  Tenant ID: <code style="font-size:11px">{tenant_id}</code>
</p>
"""

# Per-tier urgency styling
_URGENCY_CONFIG = {
    "7d": {
        "urgency_intro": "Expires Soon",
        "urgency_message": "Please contact your service provider to renew your access.",
        "badge_bg": "#eff6ff",
        "badge_border": "#93c5fd",
        "badge_color": "#1e40af",
        "subject": "Your Agent Red access expires in 7 days",
    },
    "3d": {
        "urgency_intro": "Is Almost Over",
        "urgency_message": "Renew now to avoid any interruption to your customer conversations.",
        "badge_bg": "#fef3c7",
        "badge_border": "#fcd34d",
        "badge_color": "#92400e",
        "subject": "Your Agent Red access expires in 3 days",
    },
    "1d": {
        "urgency_intro": "Ends Tomorrow",
        "urgency_message": "This is your final reminder. Your access expires tomorrow.",
        "badge_bg": "#fee2e2",
        "badge_border": "#fca5a5",
        "badge_color": "#991b1b",
        "subject": "Your Agent Red access expires tomorrow",
    },
}


# ---------------------------------------------------------------------------
# Send function
# ---------------------------------------------------------------------------


async def send_access_expiry_warning(
    to_email: str,
    tenant_id: str,
    warning_tier: str,
) -> bool:
    """Send an access expiry warning email.

    Args:
        to_email: Merchant's email address.
        tenant_id: The tenant ID.
        warning_tier: One of '7d', '3d', '1d'.

    Returns:
        True if sent successfully, False otherwise. Never raises.
    """
    if not to_email:
        logger.warning("No email — skipping access expiry warning for %s", tenant_id[:8])
        return False

    config = _URGENCY_CONFIG.get(warning_tier)
    if not config:
        logger.warning("Unknown warning tier %r for tenant %s", warning_tier, tenant_id[:8])
        return False

    from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER
    from src.multi_tenant.welcome_email import _build_admin_login_url

    days_label = {"7d": "7 days", "3d": "3 days", "1d": "1 day"}[warning_tier]

    html_body = _ACCESS_EXPIRY_BODY.format(
        urgency_intro=config["urgency_intro"],
        urgency_message=config["urgency_message"],
        days_remaining=days_label,
        badge_bg=config["badge_bg"],
        badge_border=config["badge_border"],
        badge_color=config["badge_color"],
        tenant_id=tenant_id,
        admin_login_url=_build_admin_login_url(),
    )
    full_html = _EMAIL_WRAPPER.format(body=html_body)
    subject = config["subject"]

    # --- Provider 1: SMTP (Titan or other SMTP provider) ---
    smtp_host = os.environ.get("SMTP_HOST", "")
    if smtp_host:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USERNAME", "")
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")
        smtp_from = os.environ.get("SMTP_FROM", smtp_user)

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"Agent Red <{smtp_from}>"
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
                "Access expiry warning sent via SMTP: tenant=%s tier=%s host=%s",
                tenant_id[:8], warning_tier, smtp_host,
            )
            return True
        except Exception:
            logger.exception("SMTP access expiry email failed: tenant=%s — trying ACS fallback", tenant_id[:8])
            # Fall through to ACS provider

    # --- Provider 2: Azure Communication Services (fallback) ---
    conn_str = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
    if conn_str:
        try:
            from src.multi_tenant.alert_delivery import send_acs_email

            status = await send_acs_email(conn_str, to_email, subject, full_html)
            sent = status == "Succeeded"
            if sent:
                logger.info(
                    "Access expiry warning sent via ACS: tenant=%s tier=%s email=%s",
                    tenant_id[:8], warning_tier, to_email,
                )
            return sent
        except Exception:
            logger.exception("ACS access expiry email failed: tenant=%s", tenant_id[:8])
            return False

    logger.warning("No email provider — skipping access expiry warning for %s", tenant_id[:8])
    return False
