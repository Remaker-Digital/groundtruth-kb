"""SPA Login Notification Emails (SPEC-1676).

Sends a non-blocking email notification every time a platform admin
successfully authenticates. The email contains:
    - Timestamp of the login
    - Client IP address
    - User agent string

The notification is sent to the admin's configured notification email
address, falling back to their primary email if none is set.

CRITICAL: Email failures must NEVER block authentication. All errors
are logged and swallowed.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


_LOGIN_NOTIFICATION_BODY = """
<h2 style="margin:0 0 16px;color:#111827;font-size:20px">
  Platform Admin Sign-in Notification
</h2>
<p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 16px">
  Your Agent Red platform admin account was used to sign in.
</p>
<table style="width:100%;border-collapse:collapse;margin:0 0 24px">
  <tr>
    <td style="padding:8px 12px;color:#6b7280;font-size:13px;border-bottom:1px solid #e5e7eb;width:120px">
      Time
    </td>
    <td style="padding:8px 12px;color:#111827;font-size:13px;border-bottom:1px solid #e5e7eb">
      {timestamp}
    </td>
  </tr>
  <tr>
    <td style="padding:8px 12px;color:#6b7280;font-size:13px;border-bottom:1px solid #e5e7eb">
      IP Address
    </td>
    <td style="padding:8px 12px;color:#111827;font-size:13px;border-bottom:1px solid #e5e7eb">
      {client_ip}
    </td>
  </tr>
  <tr>
    <td style="padding:8px 12px;color:#6b7280;font-size:13px;border-bottom:1px solid #e5e7eb">
      User Agent
    </td>
    <td style="padding:8px 12px;color:#111827;font-size:13px;border-bottom:1px solid #e5e7eb;word-break:break-word">
      {user_agent}
    </td>
  </tr>
</table>
<div style="text-align:center;margin:24px 0">
  <a href="{admin_dashboard_url}" style="display:inline-block;padding:10px 24px;
     background:#ff3621;color:#ffffff;font-size:14px;font-weight:600;
     text-decoration:none;border-radius:4px">
    Sign in to Dashboard
  </a>
</div>
<p style="color:#9ca3af;font-size:12px;line-height:1.5;margin:0">
  If this was not you, sign in to your
  <a href="{admin_dashboard_url}" style="color:#ff3621">admin dashboard</a>
  to generate new backup codes and rotate your API key immediately.
</p>
"""


async def send_login_notification(
    admin_email: str,
    notification_email: str | None,
    client_ip: str,
    user_agent: str,
) -> None:
    """Send a login notification email (non-blocking, swallows errors).

    Parameters
    ----------
    admin_email:
        The admin's primary email address.
    notification_email:
        Optional override address for notifications (SPEC-1676).
        If set, notifications go here instead of the primary email.
    client_ip:
        The client IP that authenticated.
    user_agent:
        The User-Agent header from the request.
    """
    recipient = notification_email or admin_email

    try:
        from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER, send_acs_email

        conn_str = os.environ.get("ACS_CONNECTION_STRING", "")
        if not conn_str:
            logger.debug("ACS_CONNECTION_STRING not set — login notification skipped")
            return

        from src.multi_tenant.welcome_email import _build_admin_login_url

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        admin_url = _build_admin_login_url()
        body_html = _LOGIN_NOTIFICATION_BODY.format(
            timestamp=timestamp,
            client_ip=client_ip,
            user_agent=user_agent or "Unknown",
            admin_dashboard_url=admin_url,
        )
        full_html = _EMAIL_WRAPPER.format(body=body_html)

        await send_acs_email(
            conn_str=conn_str,
            to_email=recipient,
            subject="Agent Red — Platform Admin Sign-in",
            html_body=full_html,
        )
        logger.info("Login notification sent to %s", recipient)
    except Exception as exc:
        # CRITICAL: Never block auth on email failure
        logger.warning("Login notification failed for %s: %s", recipient, exc)
