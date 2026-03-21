"""
Alert delivery mechanism for multi-tenant Agent Red platform.

Implements WI #192: Centralised alert routing and delivery. Currently,
ConversationMeter (billing thresholds), TenantUsageMonitor (escalation
levels), and SLAMonitoringService (compliance violations) all generate
alerts but have no delivery channel. This module provides:

    1. AlertDeliveryService — routes alerts to registered channels
    2. Three built-in channels:
       a. WebhookAlertChannel — POST JSON to merchant webhook URL
       b. DashboardAlertChannel — persist to Cosmos DB for admin UI
       c. LogAlertChannel — structured log output (always-on fallback)
    3. Convenience functions for common alert scenarios

Alert lifecycle:
    Source (ConversationMeter / UsageMonitor / SLA) creates an Alert →
    AlertDeliveryService.deliver_alert() iterates registered channels →
    each channel attempts delivery → DeliveryResult returned with
    per-channel success/failure.

Architecture references:
    - Decision #26: Proactive billing alerts (80%/100% thresholds)
    - Decision #17: Progressive throttling alerts (Watch→Warn→Throttle→Isolate)
    - WI #151: SLA monitoring dashboard (compliance violations)
    - WI #192: Alert delivery mechanism (this module)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared async-safe ACS email helper
# ---------------------------------------------------------------------------


SENDER_ADDRESS = "DoNotReply@7049c840-0df7-4d4c-ae36-6d00bfc459d4.us1.azurecomm.net"


def _send_acs_email_sync(
    conn_str: str,
    sender: str,
    to_email: str,
    subject: str,
    html_body: str,
) -> str:
    """Send an email via Azure Communication Services (synchronous).

    This function is designed to be called via ``asyncio.to_thread()``
    so that *none* of the blocking ACS SDK operations (client creation,
    begin_send, poller.result) starve the async event loop.

    Returns the delivery status string (e.g. "Succeeded").
    Raises RuntimeError for rate-limit (429) or other HTTP errors so
    callers can surface actionable messages instead of hanging.

    NOTE: The SDK's default retry policy honours the 429 ``retry-after``
    header, which ACS can set to 3600+ seconds.  This would block the
    entire request for over an hour.  We override the retry policy with
    a 10-second total retry budget so 429 fails fast instead of hanging.

    © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
    """
    from azure.communication.email import EmailClient
    from azure.core.exceptions import HttpResponseError
    from azure.core.pipeline.policies import RetryPolicy

    # Short retry budget: max 2 retries, 10s total — prevents 429 from
    # blocking the request for 60+ minutes (ACS hourly limit retry-after).
    retry_policy = RetryPolicy(
        retry_total=2,
        retry_backoff_factor=1,
        retry_backoff_max=5,
    )
    client = EmailClient.from_connection_string(
        conn_str,
        retry_policy=retry_policy,
    )
    message = {
        "senderAddress": sender,
        "recipients": {"to": [{"address": to_email}]},
        "content": {"subject": subject, "html": html_body},
    }
    try:
        poller = client.begin_send(message)
    except HttpResponseError as exc:
        # 429 should now surface here thanks to the short retry policy.
        if exc.status_code == 429:
            retry_after = getattr(exc, "retry_after", None) or "unknown"
            logger.warning(
                "ACS rate-limited (429): retry_after=%s to=%s",
                retry_after, to_email,
            )
            raise RuntimeError(
                f"Email rate limit exceeded — retry in {retry_after} seconds"
            ) from exc
        logger.error(
            "ACS begin_send HTTP error %s: %s", exc.status_code, exc.message,
        )
        raise RuntimeError(
            f"ACS email error ({exc.status_code}): {exc.message}"
        ) from exc
    result = poller.result(timeout=60)  # 60s max — prevent indefinite hang
    return getattr(result, "status", "unknown")


async def send_acs_email(
    conn_str: str,
    to_email: str,
    subject: str,
    html_body: str,
    *,
    sender: str = SENDER_ADDRESS,
) -> str:
    """Async wrapper for ACS email send — fully offloaded to thread pool.

    Returns the delivery status string (e.g. "Succeeded").
    """
    import asyncio

    return await asyncio.to_thread(
        _send_acs_email_sync, conn_str, sender, to_email, subject, html_body,
    )


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AlertType(str, Enum):
    """Types of alerts the platform can generate."""

    USAGE_80_PCT = "usage_80_pct"
    USAGE_100_PCT = "usage_100_pct"
    PACK_BALANCE_LOW = "pack_balance_low"
    VOLUME_SPIKE = "volume_spike"
    THROTTLE_ACTIVATED = "throttle_activated"
    SLA_VIOLATION = "sla_violation"
    TRIAL_EXPIRING = "trial_expiring"
    RETENTION_COMPLETE = "retention_complete"
    API_KEY_GENERATED = "api_key_generated"
    TEAM_INVITE = "team_invite"
    OUTAGE_NOTIFICATION = "outage_notification"
    ESCALATION = "escalation"


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# Map alert types to their default severity
_DEFAULT_SEVERITY: dict[AlertType, AlertSeverity] = {
    AlertType.USAGE_80_PCT: AlertSeverity.WARNING,
    AlertType.USAGE_100_PCT: AlertSeverity.CRITICAL,
    AlertType.PACK_BALANCE_LOW: AlertSeverity.WARNING,
    AlertType.VOLUME_SPIKE: AlertSeverity.WARNING,
    AlertType.THROTTLE_ACTIVATED: AlertSeverity.CRITICAL,
    AlertType.SLA_VIOLATION: AlertSeverity.CRITICAL,
    AlertType.TRIAL_EXPIRING: AlertSeverity.INFO,
    AlertType.RETENTION_COMPLETE: AlertSeverity.INFO,
    AlertType.API_KEY_GENERATED: AlertSeverity.INFO,
    AlertType.TEAM_INVITE: AlertSeverity.INFO,
    AlertType.OUTAGE_NOTIFICATION: AlertSeverity.CRITICAL,
    AlertType.ESCALATION: AlertSeverity.WARNING,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Alert:
    """An alert to be delivered to one or more channels.

    Attributes:
        alert_id: Unique identifier for this alert instance.
        tenant_id: Tenant that generated or is affected by this alert.
        alert_type: Category of the alert (from AlertType enum).
        severity: How urgent the alert is.
        title: Short human-readable summary (max ~120 chars).
        message: Detailed description of the alert condition.
        metadata: Arbitrary key-value data relevant to the alert.
        timestamp: ISO 8601 UTC timestamp when the alert was created.
    """

    alert_id: str
    tenant_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialise the alert to a plain dict (for JSON / Cosmos DB)."""
        return {
            "alert_id": self.alert_id,
            "tenant_id": self.tenant_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True)
class ChannelResult:
    """Delivery outcome for a single channel."""

    channel_name: str
    success: bool
    error: str | None = None


@dataclass(frozen=True)
class DeliveryResult:
    """Aggregate delivery outcome across all channels.

    Attributes:
        alert_id: The alert that was delivered (or attempted).
        channels_attempted: Number of channels that attempted delivery.
        channels_succeeded: Number of channels that succeeded.
        channels_failed: Number of channels that failed.
        errors: Per-channel error details for failed deliveries.
    """

    alert_id: str
    channels_attempted: int
    channels_succeeded: int
    channels_failed: int
    errors: list[ChannelResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# AlertChannel — abstract base for delivery channels
# ---------------------------------------------------------------------------


class AlertChannel(ABC):
    """Base class for alert delivery channels.

    Subclasses implement deliver() to send the alert via a specific
    transport (webhook, database, log, email, etc.).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable channel name (used in DeliveryResult)."""

    @abstractmethod
    async def deliver(self, alert: Alert) -> ChannelResult:
        """Attempt to deliver the alert via this channel.

        Returns:
            ChannelResult indicating success or failure.
        """


# ---------------------------------------------------------------------------
# Built-in channels
# ---------------------------------------------------------------------------


class LogAlertChannel(AlertChannel):
    """Structured log output channel (always-on fallback).

    Writes every alert to the Python logger at a level matching the
    alert severity: INFO → info, WARNING → warning, CRITICAL → error.
    """

    @property
    def name(self) -> str:
        return "log"

    async def deliver(self, alert: Alert) -> ChannelResult:
        """Write the alert to structured log output."""
        try:
            log_fn = {
                AlertSeverity.INFO: logger.info,
                AlertSeverity.WARNING: logger.warning,
                AlertSeverity.CRITICAL: logger.error,
            }.get(alert.severity, logger.info)

            log_fn(
                "ALERT [%s] tenant=%s severity=%s title=%s message=%s metadata=%s",
                alert.alert_type.value,
                alert.tenant_id,
                alert.severity.value,
                alert.title,
                alert.message,
                alert.metadata,
            )
            return ChannelResult(channel_name=self.name, success=True)

        except Exception as exc:
            return ChannelResult(
                channel_name=self.name,
                success=False,
                error=str(exc),
            )


class DashboardAlertChannel(AlertChannel):
    """Persist alerts to Cosmos DB for admin dashboard retrieval.

    Stores each alert as a document in the audit log (using
    AuditLogRepository) so merchants can view historical alerts in
    the admin UI. The alert payload is stored in the audit event's
    ``details`` field.

    Dependencies:
        audit_repo: AuditLogRepository (or any object with a
            ``log_event()`` async method matching the audit interface).
    """

    def __init__(self, audit_repo: Any) -> None:
        self._audit = audit_repo

    @property
    def name(self) -> str:
        return "dashboard"

    async def deliver(self, alert: Alert) -> ChannelResult:
        """Persist the alert to Cosmos DB via the audit log."""
        try:
            # Import here to avoid circular dependency at module load
            from src.multi_tenant.cosmos_schema import AuditEventType

            await self._audit.log_event(
                tenant_id=alert.tenant_id,
                event_type=AuditEventType.SUBSCRIPTION_CHANGED,
                actor="alert_delivery",
                actor_type="system",
                payload={
                    "alert_id": alert.alert_id,
                    "alert_type": alert.alert_type.value,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "message": alert.message,
                    "metadata": alert.metadata,
                },
            )
            return ChannelResult(channel_name=self.name, success=True)

        except Exception as exc:
            logger.exception(
                "DashboardAlertChannel delivery failed: alert_id=%s tenant=%s",
                alert.alert_id, alert.tenant_id,
            )
            return ChannelResult(
                channel_name=self.name,
                success=False,
                error=str(exc),
            )


class WebhookAlertChannel(AlertChannel):
    """POST JSON to the merchant's configured webhook URL.

    Uses httpx async client with a 5-second timeout and up to 2
    retries (3 total attempts). The webhook URL is resolved per
    tenant from the preferences repository.

    Dependencies:
        preferences_repo: Any repository with an async ``read()``
            method returning a dict with a ``webhook_url`` field.
    """

    # Connection / retry settings
    TIMEOUT_SECONDS = 5.0
    MAX_RETRIES = 2  # 2 retries = 3 total attempts

    def __init__(self, preferences_repo: Any) -> None:
        self._preferences = preferences_repo

    @property
    def name(self) -> str:
        return "webhook"

    async def deliver(self, alert: Alert) -> ChannelResult:
        """POST the alert payload to the tenant's webhook URL."""
        import httpx

        # Resolve webhook URL from tenant preferences
        webhook_url: str | None = None
        try:
            prefs = await self._preferences.read(
                alert.tenant_id, alert.tenant_id,
            )
            webhook_url = prefs.get("webhook_url") if prefs else None
        except Exception:
            logger.debug(
                "Could not read preferences for tenant=%s", alert.tenant_id,
            )

        if not webhook_url:
            return ChannelResult(
                channel_name=self.name,
                success=False,
                error="no webhook_url configured for tenant",
            )

        payload = alert.to_dict()
        last_error: str | None = None

        for attempt in range(1 + self.MAX_RETRIES):
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(self.TIMEOUT_SECONDS),
                ) as client:
                    response = await client.post(
                        webhook_url,
                        json=payload,
                        headers={
                            "Content-Type": "application/json",
                            "User-Agent": "AgentRed-AlertDelivery/1.0",
                            "X-Alert-Id": alert.alert_id,
                            "X-Alert-Type": alert.alert_type.value,
                        },
                    )
                    if response.status_code < 300:
                        return ChannelResult(
                            channel_name=self.name, success=True,
                        )
                    last_error = (
                        f"HTTP {response.status_code} from webhook"
                    )

            except httpx.TimeoutException:
                last_error = f"timeout after {self.TIMEOUT_SECONDS}s (attempt {attempt + 1})"
                logger.debug(
                    "Webhook timeout: tenant=%s url=%s attempt=%d",
                    alert.tenant_id, webhook_url, attempt + 1,
                )
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                logger.debug(
                    "Webhook delivery error: tenant=%s attempt=%d error=%s",
                    alert.tenant_id, attempt + 1, last_error,
                )

        logger.warning(
            "WebhookAlertChannel exhausted retries: alert_id=%s tenant=%s error=%s",
            alert.alert_id, alert.tenant_id, last_error,
        )
        return ChannelResult(
            channel_name=self.name,
            success=False,
            error=last_error,
        )


# ---------------------------------------------------------------------------
# Email templates (WI-G)
# ---------------------------------------------------------------------------

# Shared email wrapper with Agent Red branding
_EMAIL_WRAPPER = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#141414;font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#141414;padding:32px 0">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0">
<tr><td style="padding:24px 32px 16px">
  <img src="https://agentredcx.com/img/email-logo-light.png?v=2"
       alt="Agent Red Customer Experience" width="220" height="auto"
       style="display:block;max-width:220px;height:auto;border:0" />
</td></tr>
<tr><td>
<table width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;overflow:hidden">
<tr><td style="padding:32px">{body}</td></tr>
</table>
</td></tr>
<tr><td style="padding:16px 32px">
  <p style="margin:0;color:#9ca3af;font-size:12px;text-align:center">
    Agent Red Customer Experience &mdash; a product of <a href="https://remakerdigital.com" style="color:#ff3621;text-decoration:none">Remaker Digital</a>
  </p>
  <p style="margin:8px 0 0;color:#6b7280;font-size:11px;text-align:center">
    This is a system message. To unsubscribe, please
    <a href="{unsubscribe_url}" style="color:#ff3621;text-decoration:none">access your account</a>
    and change your system configuration.
  </p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""


def _resolve_admin_url(admin_url: str | None = None) -> str:
    """Resolve the admin console URL for unsubscribe links.

    Priority: explicit admin_url > STANDALONE_ADMIN_URL env > PROD_URL env > fallback.
    """
    import os

    if admin_url:
        return admin_url
    standalone = os.environ.get("STANDALONE_ADMIN_URL", "")
    if standalone:
        return standalone
    prod = os.environ.get("PROD_URL", "")
    if prod:
        return f"{prod.rstrip('/')}/admin/standalone/"
    # Derive from CONTAINER_APP_FQDN (set on all envs) — no hardcoded FQDN.
    fqdn = os.environ.get("CONTAINER_APP_FQDN", "")
    if fqdn:
        scheme = "" if fqdn.startswith("http") else "https://"
        return f"{scheme}{fqdn}/admin/standalone/"
    return "/admin/standalone/"  # relative fallback


def format_branded_email(body: str, admin_url: str | None = None) -> str:
    """Format email body into the branded HTML wrapper with unsubscribe link.

    Resolves the admin console URL for the unsubscribe link. Call sites
    that already have a tenant-specific admin URL can pass it explicitly;
    otherwise the generic admin login URL is resolved from environment.

    Args:
        body: Inner HTML content for the email.
        admin_url: Optional explicit admin URL for the unsubscribe link.

    Returns:
        Full HTML email string with branding and unsubscribe footer.
    """
    resolved_url = _resolve_admin_url(admin_url)
    return _EMAIL_WRAPPER.format(body=body, unsubscribe_url=resolved_url)


def _severity_color(severity: AlertSeverity) -> str:
    """Map alert severity to a hex color for email badges."""
    return {
        AlertSeverity.INFO: "#3b82f6",
        AlertSeverity.WARNING: "#f59e0b",
        AlertSeverity.CRITICAL: "#ef4444",
    }.get(severity, "#6b7280")


def _render_email(alert: Alert) -> tuple[str, str]:
    """Render an alert into (subject, html_body).

    Returns a plain subject line and full HTML email body using the
    branded wrapper template. Uses alert-type-specific body content
    with a generic fallback.
    """
    subject = f"[Agent Red] {alert.title}"
    badge_color = _severity_color(alert.severity)

    # Alert-type-specific body templates
    body_templates: dict[str, str] = {
        # Usage alerts
        AlertType.USAGE_80_PCT: (
            '<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Approaching Usage Limit</h2>'
            '<div style="display:inline-block;padding:4px 12px;'
            f'background:{badge_color};color:#fff;font-size:12px;font-weight:600">'
            '{severity}</div>'
            '<p style="color:#374151;line-height:1.6;margin:16px 0">{message}</p>'
            '<div style="background:#fef3c7;border:1px solid #fcd34d;padding:16px;margin:16px 0">'
            '<strong style="color:#92400e">Recommendation:</strong>'
            '<p style="color:#92400e;margin:8px 0 0">Purchase a conversation pack to avoid overage charges '
            'and ensure uninterrupted service.</p></div>'
        ),
        AlertType.USAGE_100_PCT: (
            '<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Conversation Allowance Exhausted</h2>'
            '<div style="display:inline-block;padding:4px 12px;'
            f'background:{badge_color};color:#fff;font-size:12px;font-weight:600">'
            '{severity}</div>'
            '<p style="color:#374151;line-height:1.6;margin:16px 0">{message}</p>'
            '<div style="background:#fee2e2;border:1px solid #fca5a5;padding:16px;margin:16px 0">'
            '<strong style="color:#991b1b">Action Required:</strong>'
            '<p style="color:#991b1b;margin:8px 0 0">Your included conversations are exhausted. '
            'Additional conversations will draw from pack balance or incur per-conversation overage charges.</p></div>'
        ),
        # Trial expiry
        AlertType.TRIAL_EXPIRING: (
            '<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Trial Expiring Soon</h2>'
            '<div style="display:inline-block;padding:4px 12px;'
            f'background:{badge_color};color:#fff;font-size:12px;font-weight:600">'
            '{severity}</div>'
            '<p style="color:#374151;line-height:1.6;margin:16px 0">{message}</p>'
            '<div style="background:#eff6ff;border:1px solid #93c5fd;padding:16px;margin:16px 0">'
            '<strong style="color:#1e40af">Upgrade to keep your setup:</strong>'
            '<p style="color:#1e40af;margin:8px 0 0">Your AI configuration, knowledge base, and conversation '
            'history will be preserved when you subscribe to any paid plan.</p></div>'
        ),
        # API key delivery
        AlertType.API_KEY_GENERATED: (
            '<h2 style="margin:0 0 16px;color:#111827;font-size:20px">API Key Generated</h2>'
            '<div style="display:inline-block;padding:4px 12px;'
            f'background:{badge_color};color:#fff;font-size:12px;font-weight:600">'
            '{severity}</div>'
            '<p style="color:#374151;line-height:1.6;margin:16px 0">{message}</p>'
            '<div style="background:#f3f4f6;border:1px solid #d1d5db;'
            'padding:16px;margin:16px 0;font-family:\'JetBrains Mono\',monospace">'
            '<code style="word-break:break-all;color:#111827;font-size:14px">{api_key}</code></div>'
            '<div style="background:#fef3c7;border:1px solid #fcd34d;padding:16px;margin:16px 0">'
            '<strong style="color:#92400e">Security Notice:</strong>'
            '<p style="color:#92400e;margin:8px 0 0">Store this key securely. It will not be shown again. '
            'If lost, generate a new key from the admin dashboard.</p></div>'
        ),
        # Team invite
        AlertType.TEAM_INVITE: (
            '<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Team Invitation</h2>'
            '<p style="color:#374151;line-height:1.6;margin:16px 0">{message}</p>'
            '{admin_link_block}'
            '<div style="background:#eff6ff;border:1px solid #93c5fd;padding:16px;margin:16px 0">'
            '<strong style="color:#1e40af">Getting Started:</strong>'
            '<p style="color:#1e40af;margin:8px 0 0">Log in with your '
            'email address to access your team workspace.</p></div>'
        ),
        # Escalation
        AlertType.ESCALATION: (
            '<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Customer Escalation</h2>'
            '<div style="display:inline-block;padding:4px 12px;'
            f'background:{badge_color};color:#fff;font-size:12px;font-weight:600">'
            '{severity}</div>'
            '<p style="color:#374151;line-height:1.6;margin:16px 0">{message}</p>'
            '<div style="background:#fef3c7;border:1px solid #fcd34d;padding:16px;margin:16px 0">'
            '<strong style="color:#92400e">Action Required:</strong>'
            '<p style="color:#92400e;margin:8px 0 0">A customer conversation has been escalated and needs your attention. '
            'Log in to the Agent Red admin dashboard to view the conversation.</p></div>'
        ),
        # Outage / SLA
        AlertType.OUTAGE_NOTIFICATION: (
            '<h2 style="margin:0 0 16px;color:#111827;font-size:20px">Service Notification</h2>'
            '<div style="display:inline-block;padding:4px 12px;'
            f'background:{badge_color};color:#fff;font-size:12px;font-weight:600">'
            '{severity}</div>'
            '<p style="color:#374151;line-height:1.6;margin:16px 0">{message}</p>'
            '<div style="background:#fee2e2;border:1px solid #fca5a5;padding:16px;margin:16px 0">'
            '<strong style="color:#991b1b">Status:</strong>'
            '<p style="color:#991b1b;margin:8px 0 0">Our team is actively investigating. '
            'You will receive a follow-up notification when the issue is resolved.</p></div>'
        ),
    }

    # Select body template or use generic fallback
    body_tmpl = body_templates.get(alert.alert_type, (
        '<h2 style="margin:0 0 16px;color:#111827;font-size:20px">{title}</h2>'
        '<div style="display:inline-block;padding:4px 12px;'
        f'background:{badge_color};color:#fff;font-size:12px;font-weight:600">'
        '{severity}</div>'
        '<p style="color:#374151;line-height:1.6;margin:16px 0">{message}</p>'
    ))

    # Build optional admin link block for team invites
    admin_url = alert.metadata.get("admin_url", "")
    if admin_url:
        admin_link_block = (
            '<div style="text-align:center;margin:24px 0">'
            f'<a href="{admin_url}" style="display:inline-block;padding:12px 32px;'
            'background:#3B82F6;color:#fff;text-decoration:none;font-weight:600;'
            'font-size:16px;border-radius:6px">Open Admin Dashboard</a></div>'
        )
    else:
        admin_link_block = ""

    # Format template with alert fields
    format_kwargs = {
        "title": alert.title,
        "severity": alert.severity.value.upper(),
        "message": alert.message,
        "api_key": alert.metadata.get("api_key", ""),
        "admin_link_block": admin_link_block,
    }
    body_html = body_tmpl.format(**format_kwargs)
    full_html = format_branded_email(body_html)

    return subject, full_html


class EmailAlertChannel(AlertChannel):
    """Send alert emails via Azure Communication Services or SMTP.

    Resolves the notification email from the tenant's preferences
    (``notification_email`` field) with fallback to the tenant's
    ``customer_email``. If neither is configured, delivery is skipped.

    Provider priority:
        1. Azure Communication Services (``AZURE_COMM_CONNECTION_STRING`` env var)
        2. SMTP (``SMTP_HOST`` env var) — SendGrid, Mailgun, etc.
        3. Skip delivery with informational log

    Dependencies:
        preferences_repo: For resolving per-tenant notification_email.
        tenant_repo: Fallback to customer_email from TenantDocument.

    © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
    """

    SENDER_ADDRESS = "DoNotReply@7049c840-0df7-4d4c-ae36-6d00bfc459d4.us1.azurecomm.net"
    TIMEOUT_SECONDS = 10.0

    def __init__(
        self,
        preferences_repo: Any,
        tenant_repo: Any,
    ) -> None:
        self._preferences = preferences_repo
        self._tenants = tenant_repo

    @property
    def name(self) -> str:
        return "email"

    async def _resolve_recipient(self, tenant_id: str) -> str | None:
        """Look up the notification email for a tenant.

        Checks preferences.notification_email first, then falls back
        to the tenant's customer_email.
        """
        # 1. Try preferences.notification_email
        try:
            prefs = await self._preferences.read(tenant_id, tenant_id)
            if prefs and prefs.get("notification_email"):
                return prefs["notification_email"]
        except Exception:
            logger.debug(
                "Could not read preferences for tenant=%s", tenant_id,
            )

        # 2. Fallback to tenant.customer_email
        try:
            tenant = await self._tenants.read(tenant_id, tenant_id)
            if tenant and tenant.get("customer_email"):
                return tenant["customer_email"]
        except Exception:
            logger.debug(
                "Could not read tenant for tenant=%s", tenant_id,
            )

        return None

    async def _send_via_azure_comm(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        alert: Alert,
    ) -> ChannelResult:
        """Send email using Azure Communication Services."""
        import os

        conn_str = os.environ.get("AZURE_COMM_CONNECTION_STRING", "")
        if not conn_str:
            return ChannelResult(
                channel_name=self.name,
                success=False,
                error="AZURE_COMM_CONNECTION_STRING not configured",
            )

        try:
            status = await send_acs_email(conn_str, to_email, subject, html_body)

            if status == "Succeeded":
                logger.info(
                    "Email sent via Azure Comm: alert_id=%s to=%s",
                    alert.alert_id, to_email,
                )
                return ChannelResult(channel_name=self.name, success=True)
            else:
                return ChannelResult(
                    channel_name=self.name,
                    success=False,
                    error=f"Azure Comm status: {status}",
                )

        except ImportError:
            return ChannelResult(
                channel_name=self.name,
                success=False,
                error="azure-communication-email package not installed",
            )
        except Exception as exc:
            return ChannelResult(
                channel_name=self.name,
                success=False,
                error=f"Azure Comm error: {type(exc).__name__}: {exc}",
            )

    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        alert: Alert,
    ) -> ChannelResult:
        """Send email using SMTP (SendGrid, Mailgun, generic SMTP)."""
        import os
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_host = os.environ.get("SMTP_HOST", "")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USERNAME", "")
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")

        if not smtp_host:
            return ChannelResult(
                channel_name=self.name,
                success=False,
                error="SMTP_HOST not configured",
            )

        smtp_from = os.environ.get("SMTP_FROM", smtp_user) or self.SENDER_ADDRESS

        try:
            import asyncio

            msg = MIMEMultipart("alternative")
            msg["From"] = f"Agent Red <{smtp_from}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg["X-Alert-Id"] = alert.alert_id
            msg["X-Alert-Type"] = alert.alert_type.value
            msg.attach(MIMEText(alert.message, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            timeout = self.TIMEOUT_SECONDS

            def _smtp_send() -> None:
                if smtp_port == 465:
                    with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=timeout) as server:
                        if smtp_user and smtp_pass:
                            server.login(smtp_user, smtp_pass)
                        server.send_message(msg)
                else:
                    with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout) as server:
                        server.ehlo()
                        if smtp_port != 25:
                            server.starttls()
                        if smtp_user and smtp_pass:
                            server.login(smtp_user, smtp_pass)
                        server.send_message(msg)

            await asyncio.to_thread(_smtp_send)  # SPEC-1622: non-blocking SMTP

            logger.info(
                "Email sent via SMTP: alert_id=%s to=%s host=%s",
                alert.alert_id, to_email, smtp_host,
            )
            return ChannelResult(channel_name=self.name, success=True)

        except smtplib.SMTPException as exc:
            return ChannelResult(
                channel_name=self.name,
                success=False,
                error=f"SMTP error: {type(exc).__name__}: {exc}",
            )
        except Exception as exc:
            return ChannelResult(
                channel_name=self.name,
                success=False,
                error=f"Email send error: {type(exc).__name__}: {exc}",
            )

    async def deliver(self, alert: Alert) -> ChannelResult:
        """Send an email notification for the alert.

        Provider selection: SMTP (Titan) > Azure Comm Services > skip.
        Recipient resolution: preferences.notification_email > tenant.customer_email.
        """
        import os

        # Route to specific recipients based on alert type:
        #   TEAM_INVITE  → invitee's email
        #   ESCALATION   → assigned agent / superadmin (via recipient_emails)
        #   Everything else → tenant notification_email / customer_email
        if (
            alert.alert_type == AlertType.TEAM_INVITE
            and alert.metadata.get("invitee_email")
        ):
            to_email = alert.metadata["invitee_email"]
        elif (
            alert.alert_type == AlertType.ESCALATION
            and alert.metadata.get("recipient_emails")
        ):
            to_email = alert.metadata["recipient_emails"][0]
        else:
            to_email = await self._resolve_recipient(alert.tenant_id)

        if not to_email:
            return ChannelResult(
                channel_name=self.name,
                success=False,
                error="no notification_email or customer_email for tenant",
            )

        # Render email content
        subject, html_body = _render_email(alert)

        # Try SMTP first (Titan or other SMTP provider)
        if os.environ.get("SMTP_HOST"):
            result = await self._send_via_smtp(
                to_email, subject, html_body, alert,
            )
            if result.success:
                return result
            logger.warning(
                "SMTP delivery failed, trying ACS fallback: alert_id=%s error=%s",
                alert.alert_id, result.error,
            )

        # Fall back to Azure Communication Services
        if os.environ.get("AZURE_COMM_CONNECTION_STRING"):
            return await self._send_via_azure_comm(
                to_email, subject, html_body, alert,
            )

        # No provider configured — log and skip
        logger.warning(
            "EmailAlertChannel: no email provider configured "
            "(set SMTP_HOST or AZURE_COMM_CONNECTION_STRING). "
            "alert_id=%s to=%s skipped.",
            alert.alert_id, to_email,
        )
        return ChannelResult(
            channel_name=self.name,
            success=False,
            error="no email provider configured (SMTP_HOST or AZURE_COMM_CONNECTION_STRING)",
        )


# ---------------------------------------------------------------------------
# AlertDeliveryService
# ---------------------------------------------------------------------------


class AlertDeliveryService:
    """Routes alerts to registered delivery channels.

    Always includes a LogAlertChannel as the fallback channel. Additional
    channels (webhook, dashboard, email) are registered at startup via
    register_channel().

    Usage:
        service = AlertDeliveryService()
        service.register_channel(DashboardAlertChannel(audit_repo))
        service.register_channel(WebhookAlertChannel(prefs_repo))

        result = await service.deliver_alert(alert)
    """

    def __init__(self) -> None:
        self._channels: list[AlertChannel] = []
        # Log channel is always present as the final fallback
        self._log_channel = LogAlertChannel()

    def register_channel(self, channel: AlertChannel) -> None:
        """Register a delivery channel.

        Channels are attempted in registration order, with the log
        channel always executed last as a fallback.

        Args:
            channel: An AlertChannel implementation to add.
        """
        # Avoid duplicate registration of the same channel type
        for existing in self._channels:
            if existing.name == channel.name:
                logger.warning(
                    "Alert channel '%s' already registered — replacing",
                    channel.name,
                )
                self._channels.remove(existing)
                break

        self._channels.append(channel)
        logger.info("Alert delivery channel registered: %s", channel.name)

    def get_registered_channels(self) -> list[str]:
        """Return the names of all registered channels (plus 'log')."""
        return [ch.name for ch in self._channels] + [self._log_channel.name]

    async def deliver_alert(self, alert: Alert) -> DeliveryResult:
        """Route an alert to all registered delivery channels.

        Each channel is attempted independently — a failure in one
        channel does not prevent delivery to others. The log channel
        is always invoked last as a guaranteed fallback.

        Args:
            alert: The alert to deliver.

        Returns:
            DeliveryResult with per-channel outcomes.
        """
        all_channels = list(self._channels) + [self._log_channel]
        results: list[ChannelResult] = []

        for channel in all_channels:
            try:
                result = await channel.deliver(alert)
                results.append(result)
            except Exception as exc:
                results.append(
                    ChannelResult(
                        channel_name=channel.name,
                        success=False,
                        error=f"unhandled: {type(exc).__name__}: {exc}",
                    ),
                )

        succeeded = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        errors = [r for r in results if not r.success]

        return DeliveryResult(
            alert_id=alert.alert_id,
            channels_attempted=len(results),
            channels_succeeded=succeeded,
            channels_failed=failed,
            errors=errors,
        )


# ---------------------------------------------------------------------------
# Alert factory helpers
# ---------------------------------------------------------------------------


def _make_alert_id() -> str:
    """Generate a unique alert identifier."""
    return f"alert_{uuid.uuid4().hex[:16]}"


def create_alert(
    tenant_id: str,
    alert_type: AlertType,
    title: str,
    message: str,
    severity: AlertSeverity | None = None,
    metadata: dict[str, Any] | None = None,
) -> Alert:
    """Create an Alert with auto-generated ID and timestamp.

    If severity is not provided, uses the default severity for the
    given alert_type.

    Args:
        tenant_id: Tenant generating the alert.
        alert_type: Category of alert.
        title: Short summary.
        message: Detailed description.
        severity: Override default severity (optional).
        metadata: Additional context (optional).

    Returns:
        A fully populated Alert instance.
    """
    if severity is None:
        severity = _DEFAULT_SEVERITY.get(alert_type, AlertSeverity.INFO)

    return Alert(
        alert_id=_make_alert_id(),
        tenant_id=tenant_id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        metadata=metadata or {},
    )


# ---------------------------------------------------------------------------
# Convenience functions for common alerts
# ---------------------------------------------------------------------------


async def send_usage_alert(
    tenant_id: str,
    pct_used: float,
    tier: str,
) -> DeliveryResult | None:
    """Create and deliver a USAGE_80_PCT or USAGE_100_PCT alert.

    Selects the appropriate alert type based on the usage percentage.

    Args:
        tenant_id: Tenant that crossed the threshold.
        pct_used: Usage percentage (0-100+). Values >= 100 produce
            a USAGE_100_PCT alert; values >= 80 produce USAGE_80_PCT.
        tier: Tenant tier (for metadata).

    Returns:
        DeliveryResult, or None if no service is configured.
    """
    service = get_alert_service()
    if service is None:
        return None

    if pct_used >= 100:
        alert_type = AlertType.USAGE_100_PCT
        title = "Included conversation allowance exhausted"
        message = (
            f"Usage has reached {pct_used:.0f}% of included allowance. "
            "Additional conversations will consume pack balance or incur overage charges."
        )
    else:
        alert_type = AlertType.USAGE_80_PCT
        title = "Approaching conversation allowance limit"
        message = (
            f"Usage has reached {pct_used:.0f}% of included allowance. "
            "Consider purchasing a conversation pack to avoid overage charges."
        )

    alert = create_alert(
        tenant_id=tenant_id,
        alert_type=alert_type,
        title=title,
        message=message,
        metadata={
            "pct_used": round(pct_used, 1),
            "tier": tier,
        },
    )

    return await service.deliver_alert(alert)


async def send_throttle_alert(
    tenant_id: str,
    level: str,
    tier: str,
) -> DeliveryResult | None:
    """Create and deliver a THROTTLE_ACTIVATED alert.

    Called when TenantUsageMonitor escalates a tenant to Throttle or
    Isolate level.

    Args:
        tenant_id: Tenant being throttled.
        level: Escalation level name (e.g. "throttle", "isolate").
        tier: Tenant tier (for metadata).

    Returns:
        DeliveryResult, or None if no service is configured.
    """
    service = get_alert_service()
    if service is None:
        return None

    severity = AlertSeverity.CRITICAL if level == "isolate" else AlertSeverity.WARNING

    alert = create_alert(
        tenant_id=tenant_id,
        alert_type=AlertType.THROTTLE_ACTIVATED,
        title=f"Rate limiting active — escalation level: {level}",
        message=(
            f"Tenant has been escalated to '{level}' due to elevated resource "
            "consumption. Request rate limits have been reduced to protect "
            "platform stability."
        ),
        severity=severity,
        metadata={
            "escalation_level": level,
            "tier": tier,
        },
    )

    return await service.deliver_alert(alert)


async def send_sla_alert(
    tenant_id: str,
    violation_type: str,
    details: dict[str, Any] | None = None,
) -> DeliveryResult | None:
    """Create and deliver an SLA_VIOLATION alert.

    Called when SLAMonitoringService detects a compliance violation
    (latency exceeding targets, uptime below threshold, etc.).

    Args:
        tenant_id: Affected tenant.
        violation_type: What was violated (e.g. "p95_latency", "uptime").
        details: Additional violation details (actual vs target values).

    Returns:
        DeliveryResult, or None if no service is configured.
    """
    service = get_alert_service()
    if service is None:
        return None

    alert = create_alert(
        tenant_id=tenant_id,
        alert_type=AlertType.SLA_VIOLATION,
        title=f"SLA violation detected — {violation_type}",
        message=(
            f"A service level agreement violation has been detected for "
            f"metric '{violation_type}'. Review the SLA monitoring dashboard "
            "for details."
        ),
        metadata={
            "violation_type": violation_type,
            **(details or {}),
        },
    )

    return await service.deliver_alert(alert)


async def send_api_key_alert(
    tenant_id: str,
    api_key: str,
    action: str = "generated",
) -> DeliveryResult | None:
    """Create and deliver an API_KEY_GENERATED alert.

    Sends the raw API key to the merchant's notification email so they
    have a recoverable copy (the key is not stored in plaintext).

    Args:
        tenant_id: Tenant the key belongs to.
        api_key: The raw API key string (shown once).
        action: "generated" or "rotated".

    Returns:
        DeliveryResult, or None if no service is configured.
    """
    service = get_alert_service()
    if service is None:
        return None

    alert = create_alert(
        tenant_id=tenant_id,
        alert_type=AlertType.API_KEY_GENERATED,
        title=f"API key {action}",
        message=(
            f"A new API key has been {action} for your Agent Red account. "
            "This key provides full access to the Agent Red API. "
            "Store it securely — it will not be displayed again."
        ),
        metadata={
            "api_key": api_key,
            "action": action,
        },
    )

    return await service.deliver_alert(alert)


async def send_team_invite_alert(
    tenant_id: str,
    invitee_email: str,
    inviter_name: str,
    role: str,
) -> DeliveryResult | None:
    """Create and deliver a TEAM_INVITE alert.

    Sends an invitation email to a new team member. Note: this alert
    is special — it should be sent to the *invitee_email*, not the
    tenant's notification email. The EmailAlertChannel's recipient
    resolution is bypassed by setting invitee_email in metadata.

    Args:
        tenant_id: Tenant issuing the invite.
        invitee_email: Email of the person being invited.
        inviter_name: Name of the person sending the invite.
        role: Role being assigned (e.g. "admin", "agent").

    Returns:
        DeliveryResult, or None if no service is configured.
    """
    import os

    service = get_alert_service()
    if service is None:
        return None

    # Resolve admin console URL using the canonical builder from welcome_email.
    # SPEC-1617: include ?tenant= slug so the link is globally unique.
    from src.multi_tenant.welcome_email import _build_admin_login_url, tenant_url_slug

    slug = tenant_url_slug(tenant_id=tenant_id)
    admin_url = _build_admin_login_url(tenant_slug=slug)

    message_parts = [
        f"{inviter_name} has invited you to join their Agent Red team "
        f"as a {role}.",
        f"Log in to the admin dashboard at {admin_url} with your "
        f"email address ({invitee_email}) to get started.",
    ]

    alert = create_alert(
        tenant_id=tenant_id,
        alert_type=AlertType.TEAM_INVITE,
        title="You've been invited to join a team",
        message=" ".join(message_parts),
        metadata={
            "invitee_email": invitee_email,
            "inviter_name": inviter_name,
            "role": role,
            "admin_url": admin_url,
        },
    )

    return await service.deliver_alert(alert)


async def send_outage_alert(
    tenant_id: str,
    affected_service: str,
    details: dict[str, Any] | None = None,
) -> DeliveryResult | None:
    """Create and deliver an OUTAGE_NOTIFICATION alert.

    Called when the platform detects a service degradation or outage
    affecting the tenant.

    Args:
        tenant_id: Affected tenant.
        affected_service: Name of the affected service component.
        details: Additional context (start time, impact, ETA).

    Returns:
        DeliveryResult, or None if no service is configured.
    """
    service = get_alert_service()
    if service is None:
        return None

    alert = create_alert(
        tenant_id=tenant_id,
        alert_type=AlertType.OUTAGE_NOTIFICATION,
        title=f"Service disruption — {affected_service}",
        message=(
            f"We have detected a service disruption affecting {affected_service}. "
            "Our team is investigating and working to restore normal operation. "
            "You will receive a follow-up notification when the issue is resolved."
        ),
        metadata={
            "affected_service": affected_service,
            **(details or {}),
        },
    )

    return await service.deliver_alert(alert)


async def send_escalation_alert(
    tenant_id: str,
    conversation_id: str,
    reason: str,
    urgency: str = "medium",
    context_summary: str = "",
    recipient_emails: list[str] | None = None,
    escalation_category: str | None = None,
    assigned_to: str | None = None,
) -> DeliveryResult | None:
    """Create and deliver an ESCALATION alert.

    Called by the chat pipeline when a conversation is escalated to
    a human agent. Optionally targets specific team member emails.

    Args:
        tenant_id: Tenant where the escalation occurred.
        conversation_id: The escalated conversation ID.
        reason: Why the conversation was escalated.
        urgency: Urgency level from escalation handler (low/medium/high).
        context_summary: Brief context for the human agent.
        recipient_emails: Specific team member emails to notify.
            If None, falls back to the tenant's notification email.
        escalation_category: AI-detected category (from ESCALATION_CATEGORIES).
        assigned_to: Auto-assigned team member ID.

    Returns:
        DeliveryResult, or None if no service is configured.
    """
    service = get_alert_service()
    if service is None:
        return None

    severity = {
        "high": AlertSeverity.CRITICAL,
        "medium": AlertSeverity.WARNING,
        "low": AlertSeverity.INFO,
    }.get(urgency, AlertSeverity.WARNING)

    alert = create_alert(
        tenant_id=tenant_id,
        alert_type=AlertType.ESCALATION,
        title=f"Customer escalation: {reason[:80]}",
        message=(
            f"{context_summary or reason}\n\n"
            f"Conversation: {conversation_id}\n"
            f"Urgency: {urgency}"
        ),
        severity=severity,
        metadata={
            "conversation_id": conversation_id,
            "escalation_reason": reason,
            "urgency": urgency,
            "context_summary": context_summary,
            "recipient_emails": recipient_emails or [],
            "escalation_category": escalation_category,
            "assigned_to": assigned_to,
        },
    )

    return await service.deliver_alert(alert)


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

_alert_service: AlertDeliveryService | None = None


def get_alert_service() -> AlertDeliveryService | None:
    """Get the module-level AlertDeliveryService singleton.

    Returns None if the service has not been configured via
    configure_alert_service(). Callers should handle None gracefully
    (alerts are silently dropped when no service is wired).
    """
    return _alert_service


def configure_alert_service(service: AlertDeliveryService) -> None:
    """Wire the alert delivery service at app startup.

    Typical usage in main.py:

        from src.multi_tenant.alert_delivery import (
            AlertDeliveryService,
            DashboardAlertChannel,
            WebhookAlertChannel,
            configure_alert_service,
        )

        service = AlertDeliveryService()
        service.register_channel(DashboardAlertChannel(audit_repo))
        service.register_channel(WebhookAlertChannel(preferences_repo))
        configure_alert_service(service)
    """
    global _alert_service
    _alert_service = service
    if service is not None:
        logger.info(
            "Alert delivery service configured with channels: %s",
            service.get_registered_channels(),
        )
    else:
        logger.info("Alert delivery service cleared")
