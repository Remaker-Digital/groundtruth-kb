"""Tests for superadmin alert threshold and notification channel endpoints.

Validates SPEC-1822 (Alert Threshold Configuration) and
SPEC-1823 (Notification Channel Configuration).

Endpoints tested:
  GET  /api/superadmin/alert-thresholds
  GET  /api/superadmin/alert-thresholds/{metric}
  PUT  /api/superadmin/alert-thresholds/{metric}
  GET  /api/superadmin/alert-thresholds/history
  GET  /api/superadmin/notification-channels
  GET  /api/superadmin/notification-channels/{channel_type}
  PUT  /api/superadmin/notification-channels/{channel_type}
  POST /api/superadmin/notification-channels/{channel_type}/test
  GET  /api/superadmin/notification-channels/history

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api._alerts import (
    AlertThresholdListResponse,
    AlertThresholdWriteRequest,
    AlertThresholdWriteResponse,
    EmailChannelConfig,
    ErrorRateThreshold,
    NotificationChannelListResponse,
    NotificationChannelWriteRequest,
    NotificationTestRequest,
    QueueDepthThreshold,
    ResourceUtilizationThreshold,
    ResponseTimeThreshold,
    TrafficVolumeThreshold,
    WebhookChannelConfig,
    VALID_CHANNEL_TYPES,
    VALID_METRICS,
    _DEFAULT_THRESHOLDS,
    compute_webhook_signature,
    get_alert_threshold,
    get_notification_channel,
    list_alert_thresholds,
    list_notification_channels,
    put_alert_threshold,
    put_notification_channel,
    send_test_notification,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_platform_repo() -> AsyncMock:
    """Mock PlatformConfigRepository."""
    repo = AsyncMock()
    repo.get_config.return_value = None
    repo.set_config.return_value = {}
    return repo


@pytest.fixture
def mock_audit_repo() -> AsyncMock:
    """Mock AuditLogRepository."""
    repo = AsyncMock()
    repo.log_event.return_value = {}
    return repo


@pytest.fixture
def mock_tenant_ctx() -> MagicMock:
    """Mock TenantContext for SPA admin."""
    ctx = MagicMock()
    ctx.tenant_id = "__platform__"
    ctx.team_member_email = "admin@remaker.digital"
    ctx.tier = "enterprise"
    ctx.api_key_type = "PLATFORM_ADMIN"
    return ctx


@pytest.fixture
def sample_threshold_doc() -> dict[str, Any]:
    """Sample alert threshold document from Cosmos."""
    return {
        "id": "alert_thresholds:error_rate",
        "config_type": "alert_thresholds",
        "config_key": "error_rate",
        "value": {
            "config": {"warning_per_minute": 20, "critical_per_minute": 100, "window_seconds": 60},
            "evaluation_interval_s": 30,
            "enabled": True,
        },
        "version": 2,
        "updated_at": "2026-03-16T10:00:00+00:00",
        "updated_by": "admin@remaker.digital",
    }


@pytest.fixture
def sample_email_channel_doc() -> dict[str, Any]:
    """Sample email notification channel document."""
    return {
        "id": "notification_channels:email",
        "config_type": "notification_channels",
        "config_key": "email",
        "value": {
            "enabled": True,
            "recipients": ["ops@remaker.digital"],
            "severity_filter": ["warning", "critical"],
        },
        "version": 1,
        "updated_at": "2026-03-16T10:00:00+00:00",
        "updated_by": "admin@remaker.digital",
    }


# ---------------------------------------------------------------------------
# Alert Threshold Model Tests
# ---------------------------------------------------------------------------


class TestAlertThresholdModels:
    """Test Pydantic model validation for alert threshold configs."""

    def test_error_rate_defaults(self):
        """ErrorRateThreshold has expected defaults."""
        t = ErrorRateThreshold()
        assert t.warning_per_minute == 10
        assert t.critical_per_minute == 50
        assert t.window_seconds == 60

    def test_traffic_volume_defaults(self):
        """TrafficVolumeThreshold has expected defaults."""
        t = TrafficVolumeThreshold()
        assert t.high_watermark_rpm == 1000
        assert t.low_watermark_rpm == 5

    def test_response_time_defaults(self):
        """ResponseTimeThreshold has expected defaults."""
        t = ResponseTimeThreshold()
        assert t.p50_warning_ms == 1500
        assert t.p95_warning_ms == 3000
        assert t.p99_critical_ms == 5000

    def test_queue_depth_defaults(self):
        """QueueDepthThreshold has expected defaults."""
        t = QueueDepthThreshold()
        assert t.warning_depth == 100
        assert t.critical_depth == 500

    def test_resource_utilization_defaults(self):
        """ResourceUtilizationThreshold has expected defaults."""
        t = ResourceUtilizationThreshold()
        assert t.cpu_warning_pct == 70.0
        assert t.cpu_critical_pct == 90.0

    def test_valid_metrics(self):
        """All expected metric types are present."""
        expected = {"error_rate", "traffic_volume", "response_time", "queue_depth", "resource_utilization"}
        assert VALID_METRICS == expected

    def test_default_thresholds_all_metrics(self):
        """Every valid metric has a default threshold config."""
        for metric in VALID_METRICS:
            assert metric in _DEFAULT_THRESHOLDS


# ---------------------------------------------------------------------------
# Alert Threshold GET Tests
# ---------------------------------------------------------------------------


class TestListAlertThresholds:
    """Tests for GET /api/superadmin/alert-thresholds."""

    @pytest.mark.asyncio
    async def test_list_returns_defaults(self, mock_platform_repo):
        """Returns default thresholds when no Cosmos docs exist."""
        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_alert_thresholds()

        assert isinstance(result, AlertThresholdListResponse)
        assert result.total == len(VALID_METRICS)
        for threshold in result.thresholds:
            assert threshold.version == 0

    @pytest.mark.asyncio
    async def test_list_returns_live_doc(self, mock_platform_repo, sample_threshold_doc):
        """Returns live values when Cosmos doc exists."""
        async def get_config(config_type, config_key):
            if config_key == "error_rate":
                return sample_threshold_doc
            return None

        mock_platform_repo.get_config.side_effect = get_config

        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_alert_thresholds()

        err_rate = next(t for t in result.thresholds if t.metric == "error_rate")
        assert err_rate.config["warning_per_minute"] == 20
        assert err_rate.evaluation_interval_s == 30
        assert err_rate.version == 2


class TestGetAlertThreshold:
    """Tests for GET /api/superadmin/alert-thresholds/{metric}."""

    @pytest.mark.asyncio
    async def test_get_valid_metric_default(self, mock_platform_repo):
        """Valid metric with no doc returns default config."""
        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_alert_threshold("error_rate")

        assert result.metric == "error_rate"
        assert result.version == 0
        assert "warning_per_minute" in result.config

    @pytest.mark.asyncio
    async def test_get_invalid_metric_returns_400(self, mock_platform_repo):
        """Invalid metric returns HTTP 400."""
        from fastapi import HTTPException

        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_alert_threshold("nonexistent")
            assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Alert Threshold PUT Tests
# ---------------------------------------------------------------------------


class TestPutAlertThreshold:
    """Tests for PUT /api/superadmin/alert-thresholds/{metric}."""

    @pytest.mark.asyncio
    async def test_put_creates_new_threshold(self, mock_platform_repo, mock_audit_repo, mock_tenant_ctx):
        """PUT to a metric without existing doc creates version 1."""
        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            return_value=MagicMock(invalidate_cache=MagicMock(), invalidate_redis=AsyncMock()),
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit_repo,
        ):
            body = AlertThresholdWriteRequest(
                config={"warning_per_minute": 25, "critical_per_minute": 75},
                evaluation_interval_s=30,
                enabled=True,
                change_reason="Tighten error rate thresholds",
            )
            result = await put_alert_threshold("error_rate", body, mock_tenant_ctx)

        assert isinstance(result, AlertThresholdWriteResponse)
        assert result.metric == "error_rate"
        assert result.version == 1
        mock_platform_repo.set_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_put_invalid_metric_returns_400(self, mock_tenant_ctx):
        """PUT to invalid metric returns HTTP 400."""
        from fastapi import HTTPException

        body = AlertThresholdWriteRequest(config={})
        with pytest.raises(HTTPException) as exc_info:
            await put_alert_threshold("invalid", body, mock_tenant_ctx)
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Notification Channel Model Tests
# ---------------------------------------------------------------------------


class TestNotificationChannelModels:
    """Test Pydantic model validation for notification channel configs."""

    def test_email_channel_defaults(self):
        """EmailChannelConfig has expected defaults."""
        cfg = EmailChannelConfig()
        assert cfg.enabled is True
        assert cfg.recipients == []
        assert cfg.severity_filter == ["warning", "critical"]

    def test_webhook_channel_defaults(self):
        """WebhookChannelConfig has expected defaults."""
        cfg = WebhookChannelConfig()
        assert cfg.enabled is True
        assert cfg.url == ""
        assert cfg.hmac_secret == ""
        assert cfg.timeout_ms == 5000

    def test_valid_channel_types(self):
        """Valid channel types include email and webhook."""
        assert VALID_CHANNEL_TYPES == {"email", "webhook"}


# ---------------------------------------------------------------------------
# Notification Channel GET Tests
# ---------------------------------------------------------------------------


class TestListNotificationChannels:
    """Tests for GET /api/superadmin/notification-channels."""

    @pytest.mark.asyncio
    async def test_list_returns_defaults(self, mock_platform_repo):
        """Returns default channels when no Cosmos docs exist."""
        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_notification_channels()

        assert isinstance(result, NotificationChannelListResponse)
        assert result.total == 2
        types = [c.channel_type for c in result.channels]
        assert "email" in types
        assert "webhook" in types


class TestGetNotificationChannel:
    """Tests for GET /api/superadmin/notification-channels/{channel_type}."""

    @pytest.mark.asyncio
    async def test_get_email_default(self, mock_platform_repo):
        """Email channel without doc returns default."""
        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_notification_channel("email")

        assert result.channel_type == "email"
        assert result.version == 0

    @pytest.mark.asyncio
    async def test_get_invalid_channel_returns_400(self, mock_platform_repo):
        """Invalid channel type returns HTTP 400."""
        from fastapi import HTTPException

        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_notification_channel("slack")
            assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Notification Channel PUT Tests
# ---------------------------------------------------------------------------


class TestPutNotificationChannel:
    """Tests for PUT /api/superadmin/notification-channels/{channel_type}."""

    @pytest.mark.asyncio
    async def test_put_email_channel(self, mock_platform_repo, mock_audit_repo, mock_tenant_ctx):
        """PUT email channel creates version 1."""
        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.entitlement_service.get_entitlement_service",
            return_value=MagicMock(invalidate_cache=MagicMock(), invalidate_redis=AsyncMock()),
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
            return_value=mock_audit_repo,
        ):
            body = NotificationChannelWriteRequest(
                config={"enabled": True, "recipients": ["ops@remaker.digital"]},
                change_reason="Configure email alerting",
            )
            result = await put_notification_channel("email", body, mock_tenant_ctx)

        assert result.channel_type == "email"
        assert result.version == 1

    @pytest.mark.asyncio
    async def test_put_invalid_channel_returns_400(self, mock_tenant_ctx):
        """PUT to invalid channel type returns HTTP 400."""
        from fastapi import HTTPException

        body = NotificationChannelWriteRequest(config={})
        with pytest.raises(HTTPException) as exc_info:
            await put_notification_channel("pagerduty", body, mock_tenant_ctx)
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Notification Test Endpoint Tests
# ---------------------------------------------------------------------------


class TestTestNotificationChannel:
    """Tests for POST /api/superadmin/notification-channels/{channel_type}/test."""

    @pytest.mark.asyncio
    async def test_email_no_recipients(self, mock_platform_repo, sample_email_channel_doc):
        """Email test with no recipients returns sent=False."""
        no_recipients = {**sample_email_channel_doc}
        no_recipients["value"] = {**no_recipients["value"], "recipients": []}
        mock_platform_repo.get_config.return_value = no_recipients

        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await send_test_notification(
                "email", NotificationTestRequest(message="Test"),
            )

        assert result.sent is False
        assert "No recipients" in result.detail

    @pytest.mark.asyncio
    async def test_webhook_no_url(self, mock_platform_repo):
        """Webhook test with no URL returns sent=False."""
        mock_platform_repo.get_config.return_value = {
            "value": {"enabled": True, "url": ""},
        }

        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await send_test_notification(
                "webhook", NotificationTestRequest(message="Test"),
            )

        assert result.sent is False
        assert "No webhook URL" in result.detail

    @pytest.mark.asyncio
    async def test_disabled_channel(self, mock_platform_repo):
        """Disabled channel returns sent=False."""
        mock_platform_repo.get_config.return_value = {
            "value": {"enabled": False},
        }

        with patch(
            "src.multi_tenant.superadmin_api._alerts._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await send_test_notification(
                "email", NotificationTestRequest(),
            )

        assert result.sent is False
        assert "disabled" in result.detail.lower()

    @pytest.mark.asyncio
    async def test_invalid_channel_returns_400(self):
        """Invalid channel type returns HTTP 400."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await send_test_notification(
                "slack", NotificationTestRequest(),
            )
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# HMAC Signature Tests
# ---------------------------------------------------------------------------


class TestWebhookHMAC:
    """Tests for HMAC webhook signing utility."""

    def test_compute_signature_deterministic(self):
        """Same payload + secret produces same signature."""
        payload = b'{"event":"test"}'
        secret = "my-secret-key"
        sig1 = compute_webhook_signature(payload, secret)
        sig2 = compute_webhook_signature(payload, secret)
        assert sig1 == sig2
        assert sig1.startswith("sha256=")

    def test_different_secrets_produce_different_signatures(self):
        """Different secrets produce different signatures."""
        payload = b'{"event":"test"}'
        sig1 = compute_webhook_signature(payload, "secret-a")
        sig2 = compute_webhook_signature(payload, "secret-b")
        assert sig1 != sig2

    def test_different_payloads_produce_different_signatures(self):
        """Different payloads produce different signatures."""
        secret = "same-secret"
        sig1 = compute_webhook_signature(b'{"a":1}', secret)
        sig2 = compute_webhook_signature(b'{"b":2}', secret)
        assert sig1 != sig2
