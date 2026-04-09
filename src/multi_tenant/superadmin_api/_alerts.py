# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Superadmin API -- Alert thresholds and notification channel configuration.

Domain sub-module for SPEC-1822 (Alert Threshold Configuration) and
SPEC-1823 (Notification Channel Configuration). Endpoints are registered
on the shared router from _monolith.

Alert Thresholds:
  GET  /alert-thresholds                — List all alert threshold configs
  GET  /alert-thresholds/{metric}       — Read alert thresholds for a metric
  PUT  /alert-thresholds/{metric}       — Write alert thresholds for a metric
  GET  /alert-thresholds/history        — Audit history for threshold changes

Notification Channels:
  GET  /notification-channels               — List all notification channels
  GET  /notification-channels/{channel_type} — Read a channel config
  PUT  /notification-channels/{channel_type} — Write a channel config
  POST /notification-channels/{channel_type}/test — Send a test notification
  GET  /notification-channels/history       — Audit history for channel changes

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    PlatformConfigDocument,
)
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.superadmin_api import _monolith as _state

router = _state.router

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _get_platform_repo():
    """Get the PlatformConfigRepository, lazy import to avoid circular deps."""
    from src.multi_tenant.repositories.platform import PlatformConfigRepository
    return PlatformConfigRepository()


# ---------------------------------------------------------------------------
# Alert threshold models (SPEC-1822 / WI-1420)
# ---------------------------------------------------------------------------

_AT_CONFIG_TYPE = "alert_thresholds"

VALID_METRICS = {
    "error_rate",
    "traffic_volume",
    "response_time",
    "queue_depth",
    "resource_utilization",
}


class ErrorRateThreshold(CamelCaseModel):
    """Thresholds for error/fault rate alerting."""

    warning_per_minute: int = Field(default=10, ge=0, description="Errors/min for warning")
    critical_per_minute: int = Field(default=50, ge=0, description="Errors/min for critical")
    window_seconds: int = Field(default=60, ge=10, le=600, description="Evaluation window")


class TrafficVolumeThreshold(CamelCaseModel):
    """Thresholds for traffic volume alerting (high/low watermarks)."""

    high_watermark_rpm: int = Field(default=1000, ge=0, description="RPM above this triggers alert")
    low_watermark_rpm: int = Field(default=5, ge=0, description="RPM below this triggers alert")
    window_seconds: int = Field(default=60, ge=10, le=600, description="Evaluation window")


class ResponseTimeThreshold(CamelCaseModel):
    """Thresholds for response latency alerting (percentile-based)."""

    p50_warning_ms: int = Field(default=1500, ge=0, description="p50 latency warning threshold")
    p95_warning_ms: int = Field(default=3000, ge=0, description="p95 latency warning threshold")
    p99_critical_ms: int = Field(default=5000, ge=0, description="p99 latency critical threshold")
    window_seconds: int = Field(default=60, ge=10, le=600, description="Evaluation window")


class QueueDepthThreshold(CamelCaseModel):
    """Thresholds for message/job queue depth alerting."""

    warning_depth: int = Field(default=100, ge=0, description="Queue depth for warning")
    critical_depth: int = Field(default=500, ge=0, description="Queue depth for critical")
    stale_seconds: int = Field(default=300, ge=30, le=3600, description="Message age for stale alert")


class ResourceUtilizationThreshold(CamelCaseModel):
    """Thresholds for CPU/memory utilization alerting."""

    cpu_warning_pct: float = Field(default=70.0, ge=0, le=100, description="CPU warning %")
    cpu_critical_pct: float = Field(default=90.0, ge=0, le=100, description="CPU critical %")
    memory_warning_pct: float = Field(default=75.0, ge=0, le=100, description="Memory warning %")
    memory_critical_pct: float = Field(default=90.0, ge=0, le=100, description="Memory critical %")
    window_seconds: int = Field(default=60, ge=10, le=600, description="Evaluation window")


class AlertThresholdResponse(CamelCaseModel):
    """Response from reading an alert threshold config."""

    metric: str
    config: dict[str, Any]
    evaluation_interval_s: int = Field(default=60, description="Alert evaluation loop interval")
    enabled: bool = True
    version: int = 0
    updated_at: str | None = None
    updated_by: str | None = None


class AlertThresholdListResponse(CamelCaseModel):
    """Response listing all alert threshold configs."""

    thresholds: list[AlertThresholdResponse]
    total: int


class AlertThresholdWriteRequest(CamelCaseModel):
    """Request body for writing an alert threshold config."""

    config: dict[str, Any] = Field(
        ..., description="Threshold configuration (schema varies by metric type)",
    )
    evaluation_interval_s: int = Field(
        default=60, ge=10, le=600,
        description="Alert evaluation loop interval in seconds",
    )
    enabled: bool = Field(default=True, description="Whether this alert type is active")
    change_reason: str = Field(
        default="",
        description="Optional reason for this change (SPEC-1828 audit trail)",
    )


class AlertThresholdWriteResponse(CamelCaseModel):
    """Response after writing an alert threshold config."""

    metric: str
    version: int
    updated_at: str
    cache_invalidated: bool = False


# Default threshold configs per metric
_DEFAULT_THRESHOLDS: dict[str, dict[str, Any]] = {
    "error_rate": ErrorRateThreshold().model_dump(),
    "traffic_volume": TrafficVolumeThreshold().model_dump(),
    "response_time": ResponseTimeThreshold().model_dump(),
    "queue_depth": QueueDepthThreshold().model_dump(),
    "resource_utilization": ResourceUtilizationThreshold().model_dump(),
}


# ---------------------------------------------------------------------------
# Alert threshold endpoints (SPEC-1822 / WI-1420)
# ---------------------------------------------------------------------------


@router.get(
    "/alert-thresholds",
    response_model=AlertThresholdListResponse,
    summary="List all alert threshold configurations (SPEC-1822)",
    description=(
        "Returns alert threshold configuration for all metric types. "
        "Missing configs return sensible defaults."
    ),
    status_code=200,
)
async def list_alert_thresholds() -> AlertThresholdListResponse:
    """List alert threshold configurations for all metrics."""
    repo = _get_platform_repo()
    thresholds: list[AlertThresholdResponse] = []

    for metric in sorted(VALID_METRICS):
        doc = await repo.get_config(_AT_CONFIG_TYPE, metric)
        if doc is not None:
            value = doc.get("value", {})
            thresholds.append(AlertThresholdResponse(
                metric=metric,
                config=value.get("config", value),
                evaluation_interval_s=value.get("evaluation_interval_s", 60),
                enabled=value.get("enabled", True),
                version=doc.get("version", 1),
                updated_at=doc.get("updated_at"),
                updated_by=doc.get("updated_by"),
            ))
        else:
            thresholds.append(AlertThresholdResponse(
                metric=metric,
                config=_DEFAULT_THRESHOLDS.get(metric, {}),
                version=0,
            ))

    return AlertThresholdListResponse(thresholds=thresholds, total=len(thresholds))


@router.get(
    "/alert-thresholds/history",
    summary="Alert threshold change audit history (SPEC-1822)",
    description="Returns audit log entries for alert threshold configuration changes.",
    status_code=200,
)
async def alert_threshold_history(
    limit: int = Query(50, ge=1, le=200, description="Page size"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
) -> dict[str, Any]:
    """Get audit trail of alert threshold configuration changes."""
    from src.multi_tenant.repositories.platform import AuditLogRepository

    audit_repo = AuditLogRepository()

    query = (
        "SELECT * FROM c "
        "WHERE c.event_type = @event_type "
        "AND STARTSWITH(c.payload.action, 'alert_threshold_') "
        "ORDER BY c.timestamp DESC "
        "OFFSET @skip LIMIT @limit"
    )
    params = [
        {"name": "@event_type", "value": AuditEventType.CONFIG_CHANGE.value},
        {"name": "@skip", "value": skip},
        {"name": "@limit", "value": limit},
    ]

    items: list[dict[str, Any]] = []
    try:
        async for item in audit_repo._container.query_items(
            query=query,
            parameters=params,
        ):
            payload = item.get("payload", {})
            items.append({
                "id": item.get("id"),
                "action": payload.get("action"),
                "metric": payload.get("config_key"),
                "actor": item.get("actor"),
                "timestamp": item.get("timestamp"),
                "previous_version": payload.get("previous_version"),
                "new_version": payload.get("new_version"),
                "change_reason": payload.get("change_reason", ""),
                "diff_summary": payload.get("diff_summary", []),
            })
    except Exception:
        logger.warning("Audit log query failed for alert threshold history", exc_info=True)

    return {"entries": items, "total": len(items), "skip": skip, "limit": limit}


@router.get(
    "/alert-thresholds/{metric}",
    response_model=AlertThresholdResponse,
    summary="Read alert threshold for a metric (SPEC-1822)",
    description="Read the alert threshold configuration for a specific metric type.",
    responses={400: {"description": "Invalid metric name"}},
    status_code=200,
)
async def get_alert_threshold(metric: str) -> AlertThresholdResponse:
    """Read alert threshold configuration for a specific metric."""
    if metric not in VALID_METRICS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric '{metric}'. Valid: {sorted(VALID_METRICS)}",
        )

    repo = _get_platform_repo()
    doc = await repo.get_config(_AT_CONFIG_TYPE, metric)

    if doc is not None:
        value = doc.get("value", {})
        return AlertThresholdResponse(
            metric=metric,
            config=value.get("config", value),
            evaluation_interval_s=value.get("evaluation_interval_s", 60),
            enabled=value.get("enabled", True),
            version=doc.get("version", 1),
            updated_at=doc.get("updated_at"),
            updated_by=doc.get("updated_by"),
        )

    return AlertThresholdResponse(
        metric=metric,
        config=_DEFAULT_THRESHOLDS.get(metric, {}),
        version=0,
    )


@router.put(
    "/alert-thresholds/{metric}",
    response_model=AlertThresholdWriteResponse,
    summary="Write alert threshold for a metric (SPEC-1822)",
    description=(
        "Create or update alert threshold configuration for a metric type. "
        "Increments version. Invalidates caches."
    ),
    responses={400: {"description": "Invalid metric name"}},
    status_code=200,
)
async def put_alert_threshold(
    metric: str,
    body: AlertThresholdWriteRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> AlertThresholdWriteResponse:
    """Write alert threshold configuration for a specific metric."""
    if metric not in VALID_METRICS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric '{metric}'. Valid: {sorted(VALID_METRICS)}",
        )

    repo = _get_platform_repo()
    now_iso = datetime.now(UTC).isoformat()
    actor = ctx.team_member_email or "spa-console"

    # Read existing to get current version
    existing = await repo.get_config(_AT_CONFIG_TYPE, metric)
    previous_version = existing.get("version", 0) if existing else 0
    new_version = previous_version + 1

    # Build value envelope with config + metadata
    value = {
        "config": body.config,
        "evaluation_interval_s": body.evaluation_interval_s,
        "enabled": body.enabled,
    }

    doc = PlatformConfigDocument(
        id=f"{_AT_CONFIG_TYPE}:{metric}",
        config_type=_AT_CONFIG_TYPE,
        config_key=metric,
        value=value,
        version=new_version,
        updated_at=now_iso,
        updated_by=actor,
    )
    await repo.set_config(doc)

    # Invalidate caches
    cache_invalidated = False
    try:
        from src.multi_tenant.entitlement_service import get_entitlement_service
        svc = get_entitlement_service()
        svc.invalidate_cache(f"alert_thresholds:{metric}")
        await svc.invalidate_redis(f"alert_thresholds:{metric}")
        cache_invalidated = True
    except Exception:
        logger.warning("Cache invalidation failed for alert_thresholds:%s", metric, exc_info=True)

    # Audit log (SPEC-1828)
    try:
        from src.multi_tenant.repositories.platform import AuditLogRepository
        audit = AuditLogRepository()

        old_value = existing.get("value", {}) if existing else {}
        diff_summary: list[str] = []
        if old_value.get("enabled") != body.enabled:
            diff_summary.append(f"enabled: {old_value.get('enabled')} → {body.enabled}")
        if old_value.get("evaluation_interval_s") != body.evaluation_interval_s:
            diff_summary.append(
                f"evaluation_interval_s: {old_value.get('evaluation_interval_s')} "
                f"→ {body.evaluation_interval_s}"
            )

        await audit.log_event(
            event_type=AuditEventType.CONFIG_CHANGE,
            tenant_id="__platform__",
            actor=actor,
            actor_type="admin",
            payload={
                "action": "alert_threshold_updated",
                "config_type": _AT_CONFIG_TYPE,
                "config_key": metric,
                "previous_version": previous_version,
                "new_version": new_version,
                "change_reason": body.change_reason,
                "diff_summary": diff_summary,
            },
        )
    except Exception:
        logger.warning("Audit log failed for alert threshold write", exc_info=True)

    logger.info(
        "Alert threshold updated: %s v%d→v%d (by %s)%s",
        metric, previous_version, new_version, actor,
        f" reason={body.change_reason}" if body.change_reason else "",
    )

    return AlertThresholdWriteResponse(
        metric=metric,
        version=new_version,
        updated_at=now_iso,
        cache_invalidated=cache_invalidated,
    )


# ---------------------------------------------------------------------------
# Notification channel models (SPEC-1823 / WI-1421)
# ---------------------------------------------------------------------------

_NC_CONFIG_TYPE = "notification_channels"

VALID_CHANNEL_TYPES = {"email", "webhook"}


class EmailChannelConfig(CamelCaseModel):
    """Email notification channel configuration."""

    enabled: bool = True
    recipients: list[str] = Field(default_factory=list, description="Email addresses")
    severity_filter: list[str] = Field(
        default_factory=lambda: ["warning", "critical"],
        description="Severities to send (info, warning, critical)",
    )


class WebhookChannelConfig(CamelCaseModel):
    """Webhook notification channel configuration."""

    enabled: bool = True
    url: str = Field(default="", description="Webhook endpoint URL")
    hmac_secret: str = Field(
        default="",
        description="HMAC-SHA256 secret for signing payloads (empty = unsigned)",
    )
    severity_filter: list[str] = Field(
        default_factory=lambda: ["warning", "critical"],
        description="Severities to send",
    )
    event_filter: list[str] = Field(
        default_factory=list,
        description="Event types to send (empty = all)",
    )
    timeout_ms: int = Field(default=5000, ge=1000, le=30000, description="Request timeout")


class NotificationChannelResponse(CamelCaseModel):
    """Response from reading a notification channel config."""

    channel_type: str
    config: dict[str, Any]
    version: int = 0
    updated_at: str | None = None
    updated_by: str | None = None


class NotificationChannelListResponse(CamelCaseModel):
    """Response listing all notification channels."""

    channels: list[NotificationChannelResponse]
    total: int


class NotificationChannelWriteRequest(CamelCaseModel):
    """Request body for writing a notification channel config."""

    config: dict[str, Any] = Field(
        ..., description="Channel configuration (schema varies by channel type)",
    )
    change_reason: str = Field(
        default="",
        description="Optional reason for this change (SPEC-1828 audit trail)",
    )


class NotificationChannelWriteResponse(CamelCaseModel):
    """Response after writing a notification channel config."""

    channel_type: str
    version: int
    updated_at: str
    cache_invalidated: bool = False


class NotificationTestRequest(CamelCaseModel):
    """Request body for sending a test notification."""

    message: str = Field(
        default="Test notification from Agent Red SPA Console",
        description="Test message content",
    )
    severity: str = Field(
        default="info",
        description="Test severity level (info, warning, critical)",
    )


class NotificationTestResponse(CamelCaseModel):
    """Response from a test notification."""

    channel_type: str
    sent: bool
    detail: str = ""


# ---------------------------------------------------------------------------
# Notification channel endpoints (SPEC-1823 / WI-1421)
# ---------------------------------------------------------------------------


@router.get(
    "/notification-channels",
    response_model=NotificationChannelListResponse,
    summary="List all notification channels (SPEC-1823)",
    description="Returns notification channel configuration for all channel types.",
    status_code=200,
)
async def list_notification_channels() -> NotificationChannelListResponse:
    """List notification channel configurations."""
    repo = _get_platform_repo()
    channels: list[NotificationChannelResponse] = []

    for ch_type in sorted(VALID_CHANNEL_TYPES):
        doc = await repo.get_config(_NC_CONFIG_TYPE, ch_type)
        if doc is not None:
            channels.append(NotificationChannelResponse(
                channel_type=ch_type,
                config=doc.get("value", {}),
                version=doc.get("version", 1),
                updated_at=doc.get("updated_at"),
                updated_by=doc.get("updated_by"),
            ))
        else:
            # Return unconfigured default
            if ch_type == "email":
                channels.append(NotificationChannelResponse(
                    channel_type=ch_type,
                    config=EmailChannelConfig().model_dump(),
                    version=0,
                ))
            else:
                channels.append(NotificationChannelResponse(
                    channel_type=ch_type,
                    config=WebhookChannelConfig().model_dump(),
                    version=0,
                ))

    return NotificationChannelListResponse(channels=channels, total=len(channels))


@router.get(
    "/notification-channels/history",
    summary="Notification channel change audit history (SPEC-1823)",
    description="Returns audit log entries for notification channel configuration changes.",
    status_code=200,
)
async def notification_channel_history(
    limit: int = Query(50, ge=1, le=200, description="Page size"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
) -> dict[str, Any]:
    """Get audit trail of notification channel configuration changes."""
    from src.multi_tenant.repositories.platform import AuditLogRepository

    audit_repo = AuditLogRepository()

    query = (
        "SELECT * FROM c "
        "WHERE c.event_type = @event_type "
        "AND STARTSWITH(c.payload.action, 'notification_channel_') "
        "ORDER BY c.timestamp DESC "
        "OFFSET @skip LIMIT @limit"
    )
    params = [
        {"name": "@event_type", "value": AuditEventType.CONFIG_CHANGE.value},
        {"name": "@skip", "value": skip},
        {"name": "@limit", "value": limit},
    ]

    items: list[dict[str, Any]] = []
    try:
        async for item in audit_repo._container.query_items(
            query=query,
            parameters=params,
        ):
            payload = item.get("payload", {})
            items.append({
                "id": item.get("id"),
                "action": payload.get("action"),
                "channel_type": payload.get("config_key"),
                "actor": item.get("actor"),
                "timestamp": item.get("timestamp"),
                "previous_version": payload.get("previous_version"),
                "new_version": payload.get("new_version"),
                "change_reason": payload.get("change_reason", ""),
                "diff_summary": payload.get("diff_summary", []),
            })
    except Exception:
        logger.warning("Audit log query failed for notification channel history", exc_info=True)

    return {"entries": items, "total": len(items), "skip": skip, "limit": limit}


@router.get(
    "/notification-channels/{channel_type}",
    response_model=NotificationChannelResponse,
    summary="Read notification channel config (SPEC-1823)",
    description="Read the notification channel configuration for a specific type.",
    responses={400: {"description": "Invalid channel type"}},
    status_code=200,
)
async def get_notification_channel(channel_type: str) -> NotificationChannelResponse:
    """Read notification channel configuration."""
    if channel_type not in VALID_CHANNEL_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid channel type '{channel_type}'. Valid: {sorted(VALID_CHANNEL_TYPES)}",
        )

    repo = _get_platform_repo()
    doc = await repo.get_config(_NC_CONFIG_TYPE, channel_type)

    if doc is not None:
        return NotificationChannelResponse(
            channel_type=channel_type,
            config=doc.get("value", {}),
            version=doc.get("version", 1),
            updated_at=doc.get("updated_at"),
            updated_by=doc.get("updated_by"),
        )

    # Unconfigured default
    if channel_type == "email":
        default_config = EmailChannelConfig().model_dump()
    else:
        default_config = WebhookChannelConfig().model_dump()
    return NotificationChannelResponse(
        channel_type=channel_type,
        config=default_config,
        version=0,
    )


@router.put(
    "/notification-channels/{channel_type}",
    response_model=NotificationChannelWriteResponse,
    summary="Write notification channel config (SPEC-1823)",
    description=(
        "Create or update notification channel configuration. "
        "Increments version. Invalidates caches."
    ),
    responses={400: {"description": "Invalid channel type"}},
    status_code=200,
)
async def put_notification_channel(
    channel_type: str,
    body: NotificationChannelWriteRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> NotificationChannelWriteResponse:
    """Write notification channel configuration."""
    if channel_type not in VALID_CHANNEL_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid channel type '{channel_type}'. Valid: {sorted(VALID_CHANNEL_TYPES)}",
        )

    repo = _get_platform_repo()
    now_iso = datetime.now(UTC).isoformat()
    actor = ctx.team_member_email or "spa-console"

    # Read existing to get current version
    existing = await repo.get_config(_NC_CONFIG_TYPE, channel_type)
    previous_version = existing.get("version", 0) if existing else 0
    new_version = previous_version + 1

    doc = PlatformConfigDocument(
        id=f"{_NC_CONFIG_TYPE}:{channel_type}",
        config_type=_NC_CONFIG_TYPE,
        config_key=channel_type,
        value=body.config,
        version=new_version,
        updated_at=now_iso,
        updated_by=actor,
    )
    await repo.set_config(doc)

    # Invalidate caches
    cache_invalidated = False
    try:
        from src.multi_tenant.entitlement_service import get_entitlement_service
        svc = get_entitlement_service()
        svc.invalidate_cache(f"notification_channels:{channel_type}")
        await svc.invalidate_redis(f"notification_channels:{channel_type}")
        cache_invalidated = True
    except Exception:
        logger.warning(
            "Cache invalidation failed for notification_channels:%s",
            channel_type, exc_info=True,
        )

    # Audit log (SPEC-1828)
    try:
        from src.multi_tenant.repositories.platform import AuditLogRepository
        audit = AuditLogRepository()

        old_value = existing.get("value", {}) if existing else {}
        diff_summary: list[str] = []
        for k in set(list(old_value.keys()) + list(body.config.keys())):
            old_v = old_value.get(k)
            new_v = body.config.get(k)
            if old_v != new_v:
                # Redact HMAC secret from audit
                if k == "hmac_secret":
                    diff_summary.append(f"{k}: [redacted] → [redacted]")
                else:
                    diff_summary.append(f"{k}: {old_v} → {new_v}")

        await audit.log_event(
            event_type=AuditEventType.CONFIG_CHANGE,
            tenant_id="__platform__",
            actor=actor,
            actor_type="admin",
            payload={
                "action": "notification_channel_updated",
                "config_type": _NC_CONFIG_TYPE,
                "config_key": channel_type,
                "previous_version": previous_version,
                "new_version": new_version,
                "change_reason": body.change_reason,
                "diff_summary": diff_summary,
            },
        )
    except Exception:
        logger.warning("Audit log failed for notification channel write", exc_info=True)

    logger.info(
        "Notification channel updated: %s v%d→v%d (by %s)%s",
        channel_type, previous_version, new_version, actor,
        f" reason={body.change_reason}" if body.change_reason else "",
    )

    return NotificationChannelWriteResponse(
        channel_type=channel_type,
        version=new_version,
        updated_at=now_iso,
        cache_invalidated=cache_invalidated,
    )


@router.post(
    "/notification-channels/{channel_type}/test",
    response_model=NotificationTestResponse,
    summary="Send a test notification (SPEC-1823)",
    description=(
        "Sends a test notification through the specified channel to verify "
        "configuration is correct. Does not require a real alert."
    ),
    responses={400: {"description": "Invalid channel type or unconfigured channel"}},
    status_code=200,
)
async def send_test_notification(
    channel_type: str,
    body: NotificationTestRequest,
) -> NotificationTestResponse:
    """Send a test notification through a channel."""
    if channel_type not in VALID_CHANNEL_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid channel type '{channel_type}'. Valid: {sorted(VALID_CHANNEL_TYPES)}",
        )

    repo = _get_platform_repo()
    doc = await repo.get_config(_NC_CONFIG_TYPE, channel_type)
    config = doc.get("value", {}) if doc else {}

    if not config.get("enabled", True):
        return NotificationTestResponse(
            channel_type=channel_type,
            sent=False,
            detail="Channel is disabled",
        )

    if channel_type == "email":
        recipients = config.get("recipients", [])
        if not recipients:
            return NotificationTestResponse(
                channel_type=channel_type,
                sent=False,
                detail="No recipients configured",
            )

        try:
            from src.multi_tenant.email_service import send_platform_notification
            await send_platform_notification(
                recipients=recipients,
                subject=f"[Agent Red Test] {body.severity.upper()}: {body.message[:50]}",
                body=body.message,
            )
            return NotificationTestResponse(
                channel_type=channel_type,
                sent=True,
                detail=f"Test email sent to {len(recipients)} recipient(s)",
            )
        except Exception as exc:
            logger.warning("Test email failed", exc_info=True)
            return NotificationTestResponse(
                channel_type=channel_type,
                sent=False,
                detail=f"Email send failed: {exc}",
            )

    elif channel_type == "webhook":
        url = config.get("url", "")
        if not url:
            return NotificationTestResponse(
                channel_type=channel_type,
                sent=False,
                detail="No webhook URL configured",
            )

        try:
            import httpx

            payload = {
                "event": "test_notification",
                "severity": body.severity,
                "message": body.message,
                "timestamp": datetime.now(UTC).isoformat(),
                "source": "agent-red-spa-console",
            }

            headers: dict[str, str] = {"Content-Type": "application/json"}
            hmac_secret = config.get("hmac_secret", "")
            if hmac_secret:
                import json
                payload_bytes = json.dumps(payload, sort_keys=True).encode()
                signature = hmac.new(
                    hmac_secret.encode(),
                    payload_bytes,
                    hashlib.sha256,
                ).hexdigest()
                headers["X-AgentRed-Signature"] = f"sha256={signature}"

            timeout_ms = config.get("timeout_ms", 5000)
            async with httpx.AsyncClient(timeout=timeout_ms / 1000) as client:
                resp = await client.post(url, json=payload, headers=headers)

            return NotificationTestResponse(
                channel_type=channel_type,
                sent=resp.status_code < 400,
                detail=f"Webhook responded {resp.status_code}",
            )
        except Exception as exc:
            logger.warning("Test webhook failed", exc_info=True)
            return NotificationTestResponse(
                channel_type=channel_type,
                sent=False,
                detail=f"Webhook request failed: {exc}",
            )

    return NotificationTestResponse(
        channel_type=channel_type,
        sent=False,
        detail=f"Unsupported channel type: {channel_type}",
    )


# ---------------------------------------------------------------------------
# HMAC signing utility (exported for notification dispatch service)
# ---------------------------------------------------------------------------


def compute_webhook_signature(payload_bytes: bytes, secret: str) -> str:
    """Compute HMAC-SHA256 signature for a webhook payload.

    Returns the signature in format 'sha256={hex_digest}'.
    """
    return "sha256=" + hmac.new(
        secret.encode(),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()
