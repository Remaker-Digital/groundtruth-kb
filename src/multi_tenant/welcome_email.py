"""Welcome email — sent once when a new tenant is provisioned.

Delivers the admin console URL and onboarding guidance. API keys are
NOT included in the email — merchants retrieve them from the admin
console after signing in (SPEC-1673).

Follows a dual-provider pattern: SMTP primary (Titan), ACS fallback.
Returns bool.

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
  Your account is ready. Sign in to your admin dashboard to get started.
</p>

<div style="background:#fff7ed;border:1px solid #fed7aa;padding:16px;margin:16px 0;text-align:center">
  <p style="margin:0 0 12px;color:#9a3412;font-size:13px;font-weight:600">
    Your Admin Dashboard
  </p>
  <a href="{admin_login_url}" style="display:inline-block;padding:10px 24px;
     background:#ff3621;color:#ffffff;font-size:14px;font-weight:600;
     text-decoration:none">
    Sign in to Dashboard
  </a>
  <p style="margin:8px 0 0;color:#9a3412;font-size:12px">
    {admin_login_url}
  </p>
</div>

<p style="color:#374151;font-size:14px;line-height:1.6;margin:16px 0">
  Your API key and widget key are available from your admin dashboard
  after signing in. Keys are never sent via email for your security.
</p>

<h3 style="margin:24px 0 12px;color:#111827;font-size:16px">Next Steps</h3>
<ol style="color:#374151;font-size:14px;line-height:1.8;margin:0;padding-left:20px">
  <li>Sign in to your <a href="{admin_login_url}" style="color:#ff3621;font-weight:600">Admin Dashboard</a></li>
  <li>Find your API key and widget key on the Account page</li>
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


def tenant_url_slug(
    shop_domain: str | None = None,
    brand_name: str | None = None,
    tenant_id: str | None = None,
) -> str:
    """Return the tenant ID as the URL slug for the ``?tenant=`` parameter.

    SPEC-1644: The URL must uniquely identify the tenant.  Tenant IDs
    (UUIDs) are globally unique by design.  Previous implementation
    derived slugs from shop_domain or brand_name, which caused collision
    issues when multiple tenants shared a brand name (WI-0993/WI-0994).

    The *shop_domain* and *brand_name* parameters are retained for
    call-site compatibility but are no longer used in slug generation.
    """
    return tenant_id or ""


def _build_admin_login_url(
    explicit_url: str | None = None,
    *,
    tenant_slug: str | None = None,
) -> str:
    """Build the admin console login URL.

    Priority: explicit_url > STANDALONE_ADMIN_URL env > PROD_URL env > fallback.
    If *tenant_slug* is provided, appends ``?tenant=<slug>`` (SPEC-1617).
    """
    if explicit_url:
        base = explicit_url
    else:
        standalone = os.environ.get("STANDALONE_ADMIN_URL", "")
        if standalone:
            base = standalone
        else:
            prod = os.environ.get("PROD_URL", "")
            if prod:
                base = f"{prod.rstrip('/')}/admin/standalone/"
            else:
                # Fallback: production API gateway admin console.
                # The FQDN is stable (Azure Container Apps environment-scoped).
                base = "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/admin/standalone/"
    if tenant_slug:
        sep = "&" if "?" in base else "?"
        return f"{base}{sep}tenant={tenant_slug}"
    return base


async def send_welcome_email(
    to_email: str,
    tenant_id: str,
    superadmin_key: str | None = None,
    widget_key: str | None = None,
    tier: str | None = None,
    admin_login_url: str | None = None,
    *,
    shop_domain: str | None = None,
    brand_name: str | None = None,
) -> bool:
    """Send a welcome email to the newly provisioned merchant.

    Uses ACS (primary) or SMTP (fallback). Returns True on success,
    False on any failure. Never raises — callers should not block
    provisioning on email delivery.

    Note: ``superadmin_key`` and ``widget_key`` parameters are retained
    for call-site compatibility but are no longer displayed in the email.
    Keys are accessible from the admin console after signing in.

    Args:
        to_email: Merchant's email address.
        tenant_id: The new tenant ID.
        superadmin_key: Deprecated — no longer shown in email.
        widget_key: Deprecated — no longer shown in email.
        tier: Subscription tier name.
        admin_login_url: Admin dashboard URL. If not provided, built from
            STANDALONE_ADMIN_URL or PROD_URL environment variables.

    Returns:
        True if the email was sent successfully, False otherwise.
    """
    if not to_email:
        logger.warning("No email address — skipping welcome email for %s", tenant_id[:8])
        return False

    from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

    slug = tenant_url_slug(shop_domain, brand_name, tenant_id)
    resolved_url = _build_admin_login_url(admin_login_url, tenant_slug=slug)

    html_body = _WELCOME_EMAIL_BODY.format(
        tier=(tier or "trial").capitalize(),
        tenant_id=tenant_id,
        admin_login_url=resolved_url,
    )
    full_html = _EMAIL_WRAPPER.format(body=html_body)
    subject = "Welcome to Agent Red — Your account is ready"

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
            msg.attach(MIMEText(full_html, "html"))
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

        try:
            await asyncio.to_thread(_smtp_send)  # SPEC-1622: non-blocking SMTP
            logger.info("Welcome email sent via SMTP: tenant=%s email=%s host=%s", tenant_id[:8], to_email, smtp_host)
            return True
        except Exception:
            logger.exception("SMTP welcome email send failed: tenant=%s — trying ACS fallback", tenant_id[:8])
            # Fall through to ACS provider

    # --- Provider 2: Azure Communication Services (fallback) ---
    conn_str = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
    if conn_str:
        try:
            from src.multi_tenant.alert_delivery import send_acs_email

            status = await send_acs_email(conn_str, to_email, subject, full_html)
            sent = status == "Succeeded"
            if sent:
                logger.info("Welcome email sent via ACS: tenant=%s email=%s", tenant_id[:8], to_email)
            else:
                logger.warning("ACS welcome email status=%s: tenant=%s", status, tenant_id[:8])
            return sent
        except RuntimeError as exc:
            # Rate-limit (429) or HTTP error from ACS — propagate so caller
            # can surface a user-friendly message instead of generic failure.
            logger.warning("ACS welcome email failed: tenant=%s error=%s", tenant_id[:8], exc)
            raise
        except Exception:
            logger.exception("ACS welcome email send failed: tenant=%s", tenant_id[:8])
            return False

    logger.warning("No email provider configured — skipping welcome email for %s", tenant_id[:8])
    return False
