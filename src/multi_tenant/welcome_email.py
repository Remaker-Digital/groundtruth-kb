"""Welcome email — sent once when a new tenant is provisioned.

Delivers the merchant's initial credentials (superadmin API key, widget key),
admin console URL, and onboarding guidance. Follows the same dual-provider
pattern as widget_otp_verification.py (ACS primary, SMTP fallback, returns bool).

Call sites:
    - stripe_webhooks.handle_checkout_completed()  (Stripe checkout)
    - shopify_billing.confirm_subscription()        (Shopify billing)
    - provisioning.provision_trial_tenant()          (trial signup)
    - provisioning.spa_provision_tenant()            (SPA manual)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Email body template
# ---------------------------------------------------------------------------

_WELCOME_EMAIL_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Welcome to Agent Red</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 24px">
  Your account is ready. Here are your credentials to get started.
</p>

<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:6px;
     padding:16px;margin:16px 0;text-align:center">
  <p style="margin:0 0 12px;color:#9a3412;font-size:13px;font-weight:600">
    Your Admin Dashboard
  </p>
  <a href="{admin_login_url}" style="display:inline-block;padding:10px 24px;
     background:#ff3621;color:#ffffff;font-size:14px;font-weight:600;
     text-decoration:none;border-radius:6px">
    Sign in to Dashboard
  </a>
  <p style="margin:8px 0 0;color:#9a3412;font-size:12px">
    {admin_login_url}
  </p>
</div>

<div style="background:#f3f4f6;border:1px solid #d1d5db;border-radius:6px;
     padding:16px;margin:16px 0">
  <p style="margin:0 0 8px;color:#6b7280;font-size:12px;font-weight:600;
       text-transform:uppercase;letter-spacing:0.05em">Admin API Key</p>
  <code style="word-break:break-all;color:#111827;font-size:14px;
       font-family:'JetBrains Mono',SFMono-Regular,ui-monospace,monospace">{superadmin_key}</code>
</div>

<div style="background:#f3f4f6;border:1px solid #d1d5db;border-radius:6px;
     padding:16px;margin:16px 0">
  <p style="margin:0 0 8px;color:#6b7280;font-size:12px;font-weight:600;
       text-transform:uppercase;letter-spacing:0.05em">Widget Key</p>
  <code style="word-break:break-all;color:#111827;font-size:14px;
       font-family:'JetBrains Mono',SFMono-Regular,ui-monospace,monospace">{widget_key}</code>
</div>

<div style="background:#fef3c7;border:1px solid #fcd34d;border-radius:6px;
     padding:16px;margin:16px 0">
  <strong style="color:#92400e">Security Notice</strong>
  <p style="color:#92400e;margin:8px 0 0;font-size:13px">
    Store these keys securely. They will not be shown again.
    If lost, you can regenerate them from the admin dashboard.
  </p>
</div>

<h3 style="margin:24px 0 12px;color:#111827;font-size:16px">Next Steps</h3>
<ol style="color:#374151;font-size:14px;line-height:1.8;margin:0;padding-left:20px">
  <li>Sign in to your <a href="{admin_login_url}" style="color:#ff3621;font-weight:600">Admin Dashboard</a> using your API key</li>
  <li>Configure your brand name, voice, and AI agent personality</li>
  <li>Add your widget key to your website to start chatting with customers</li>
  <li>Invite team members to handle escalated conversations</li>
</ol>

<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:24px 0 0">
  Plan: <strong>{tier}</strong>
  &nbsp;&middot;&nbsp;
  Tenant ID: <code style="font-size:11px">{tenant_id}</code>
</p>
"""


# ---------------------------------------------------------------------------
# Send function
# ---------------------------------------------------------------------------


def _build_admin_login_url(explicit_url: str | None = None) -> str:
    """Build the admin console login URL.

    Priority: explicit_url > STANDALONE_ADMIN_URL env > PROD_URL env > fallback.
    """
    if explicit_url:
        return explicit_url
    standalone = os.environ.get("STANDALONE_ADMIN_URL", "")
    if standalone:
        return standalone
    prod = os.environ.get("PROD_URL", "")
    if prod:
        return f"{prod.rstrip('/')}/admin/standalone/"
    return "https://agentredcx.com/docs/getting-started"


async def send_welcome_email(
    to_email: str,
    tenant_id: str,
    superadmin_key: str | None = None,
    widget_key: str | None = None,
    tier: str | None = None,
    admin_login_url: str | None = None,
) -> bool:
    """Send a welcome email to the newly provisioned merchant.

    Uses ACS (primary) or SMTP (fallback). Returns True on success,
    False on any failure. Never raises — callers should not block
    provisioning on email delivery.

    Args:
        to_email: Merchant's email address.
        tenant_id: The new tenant ID.
        superadmin_key: Raw superadmin API key (shown once).
        widget_key: Raw widget key (shown once).
        tier: Subscription tier name.
        admin_login_url: Admin dashboard URL. If not provided, built from
            STANDALONE_ADMIN_URL or PROD_URL environment variables.

    Returns:
        True if the email was sent successfully, False otherwise.
    """
    if not to_email:
        logger.warning("No email address — skipping welcome email for %s", tenant_id[:8])
        return False

    from src.multi_tenant.alert_delivery import EmailAlertChannel, _EMAIL_WRAPPER

    resolved_url = _build_admin_login_url(admin_login_url)

    html_body = _WELCOME_EMAIL_BODY.format(
        superadmin_key=superadmin_key or "(not generated)",
        widget_key=widget_key or "(not generated)",
        tier=(tier or "trial").capitalize(),
        tenant_id=tenant_id,
        admin_login_url=resolved_url,
    )
    full_html = _EMAIL_WRAPPER.format(body=html_body)
    subject = "Welcome to Agent Red — Your account is ready"

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
            result = poller.result()
            sent = getattr(result, "status", "") == "Succeeded"
            if sent:
                logger.info("Welcome email sent via ACS: tenant=%s email=%s", tenant_id[:8], to_email)
            else:
                logger.warning("ACS welcome email status=%s: tenant=%s", getattr(result, "status", "unknown"), tenant_id[:8])
            return sent
        except Exception:
            logger.exception("ACS welcome email send failed: tenant=%s", tenant_id[:8])
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

            logger.info("Welcome email sent via SMTP: tenant=%s email=%s", tenant_id[:8], to_email)
            return True
        except Exception:
            logger.exception("SMTP welcome email send failed: tenant=%s", tenant_id[:8])
            return False

    logger.warning("No email provider configured — skipping welcome email for %s", tenant_id[:8])
    return False
