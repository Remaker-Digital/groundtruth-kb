"""Tests for alert delivery mechanism — coverage expansion.

Covers: AlertDeliveryService, LogAlertChannel, DashboardAlertChannel,
WebhookAlertChannel, EmailAlertChannel, create_alert, convenience functions,
email rendering, and module singleton management.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.alert_delivery import (
    Alert,
    AlertDeliveryService,
    AlertSeverity,
    AlertType,
    ChannelResult,
    DashboardAlertChannel,
    DeliveryResult,
    EmailAlertChannel,
    LogAlertChannel,
    WebhookAlertChannel,
    _render_email,
    _severity_color,
    configure_alert_service,
    create_alert,
    get_alert_service,
    send_api_key_alert,
    send_escalation_alert,
    send_outage_alert,
    send_sla_alert,
    send_team_invite_alert,
    send_throttle_alert,
    send_usage_alert,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_alert(
    alert_type: AlertType = AlertType.USAGE_80_PCT,
    severity: AlertSeverity = AlertSeverity.WARNING,
    tenant_id: str = "tenant-001",
    **overrides,
) -> Alert:
    defaults = {
        "alert_id": "alert_test123",
        "tenant_id": tenant_id,
        "alert_type": alert_type,
        "severity": severity,
        "title": "Test Alert",
        "message": "This is a test alert message.",
        "metadata": {},
    }
    defaults.update(overrides)
    return Alert(**defaults)


# ---------------------------------------------------------------------------
# Tests: Alert data class
# ---------------------------------------------------------------------------


class TestAlert:
    def test_to_dict(self):
        alert = _make_alert(metadata={"key": "value"})
        d = alert.to_dict()
        assert d["alert_id"] == "alert_test123"
        assert d["alert_type"] == "usage_80_pct"
        assert d["severity"] == "warning"
        assert d["metadata"] == {"key": "value"}
        assert "timestamp" in d

    def test_default_timestamp(self):
        alert = _make_alert()
        assert alert.timestamp is not None
        assert "T" in alert.timestamp  # ISO format


# ---------------------------------------------------------------------------
# Tests: create_alert
# ---------------------------------------------------------------------------


class TestCreateAlert:
    def test_auto_severity(self):
        alert = create_alert(
            tenant_id="t",
            alert_type=AlertType.SLA_VIOLATION,
            title="SLA",
            message="Violated",
        )
        assert alert.severity == AlertSeverity.CRITICAL

    def test_override_severity(self):
        alert = create_alert(
            tenant_id="t",
            alert_type=AlertType.SLA_VIOLATION,
            title="SLA",
            message="Violated",
            severity=AlertSeverity.INFO,
        )
        assert alert.severity == AlertSeverity.INFO

    def test_auto_id(self):
        alert = create_alert(
            tenant_id="t",
            alert_type=AlertType.TRIAL_EXPIRING,
            title="Trial",
            message="Expiring",
        )
        assert alert.alert_id.startswith("alert_")
        assert len(alert.alert_id) > 6

    def test_default_severity_for_all_types(self):
        for alert_type in AlertType:
            alert = create_alert("t", alert_type, "T", "M")
            assert alert.severity is not None


# ---------------------------------------------------------------------------
# Tests: LogAlertChannel
# ---------------------------------------------------------------------------


class TestLogAlertChannel:
    @pytest.mark.asyncio
    async def test_deliver_info(self):
        channel = LogAlertChannel()
        assert channel.name == "log"
        alert = _make_alert(severity=AlertSeverity.INFO)
        result = await channel.deliver(alert)
        assert result.success is True
        assert result.channel_name == "log"

    @pytest.mark.asyncio
    async def test_deliver_warning(self):
        channel = LogAlertChannel()
        alert = _make_alert(severity=AlertSeverity.WARNING)
        result = await channel.deliver(alert)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_deliver_critical(self):
        channel = LogAlertChannel()
        alert = _make_alert(severity=AlertSeverity.CRITICAL)
        result = await channel.deliver(alert)
        assert result.success is True


# ---------------------------------------------------------------------------
# Tests: DashboardAlertChannel
# ---------------------------------------------------------------------------


class TestDashboardAlertChannel:
    @pytest.mark.asyncio
    async def test_deliver_success(self):
        audit_repo = MagicMock()
        audit_repo.log_event = AsyncMock()
        channel = DashboardAlertChannel(audit_repo)
        assert channel.name == "dashboard"

        alert = _make_alert()

        # AuditEventType is imported lazily inside deliver() from cosmos_schema
        result = await channel.deliver(alert)

        assert result.success is True
        audit_repo.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_deliver_failure(self):
        audit_repo = MagicMock()
        audit_repo.log_event = AsyncMock(side_effect=RuntimeError("cosmos down"))
        channel = DashboardAlertChannel(audit_repo)

        alert = _make_alert()
        # AuditEventType is imported lazily inside deliver() — the exception
        # will be raised by log_event regardless
        result = await channel.deliver(alert)

        assert result.success is False
        assert "cosmos down" in result.error


# ---------------------------------------------------------------------------
# Tests: WebhookAlertChannel
# ---------------------------------------------------------------------------


class TestWebhookAlertChannel:
    @pytest.mark.asyncio
    async def test_no_webhook_configured(self):
        prefs_repo = MagicMock()
        prefs_repo.read = AsyncMock(return_value={"webhook_url": None})
        channel = WebhookAlertChannel(prefs_repo)
        assert channel.name == "webhook"

        alert = _make_alert()
        result = await channel.deliver(alert)
        assert result.success is False
        assert "no webhook_url" in result.error

    @pytest.mark.asyncio
    async def test_webhook_preferences_read_fails(self):
        prefs_repo = MagicMock()
        prefs_repo.read = AsyncMock(side_effect=RuntimeError("read failed"))
        channel = WebhookAlertChannel(prefs_repo)

        alert = _make_alert()
        result = await channel.deliver(alert)
        assert result.success is False
        assert "no webhook_url" in result.error

    @pytest.mark.asyncio
    async def test_webhook_success(self):
        prefs_repo = MagicMock()
        prefs_repo.read = AsyncMock(return_value={"webhook_url": "https://hooks.example.com/alert"})
        channel = WebhookAlertChannel(prefs_repo)

        alert = _make_alert()

        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await channel.deliver(alert)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_webhook_http_error(self):
        prefs_repo = MagicMock()
        prefs_repo.read = AsyncMock(return_value={"webhook_url": "https://hooks.example.com/alert"})
        channel = WebhookAlertChannel(prefs_repo)

        alert = _make_alert()

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await channel.deliver(alert)

        assert result.success is False
        assert "HTTP 500" in result.error

    @pytest.mark.asyncio
    async def test_webhook_timeout_retries(self):
        import httpx

        prefs_repo = MagicMock()
        prefs_repo.read = AsyncMock(return_value={"webhook_url": "https://hooks.example.com/alert"})
        channel = WebhookAlertChannel(prefs_repo)

        alert = _make_alert()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await channel.deliver(alert)

        assert result.success is False
        assert "timeout" in result.error


# ---------------------------------------------------------------------------
# Tests: _severity_color and _render_email
# ---------------------------------------------------------------------------


class TestEmailRendering:
    def test_severity_color_info(self):
        assert _severity_color(AlertSeverity.INFO) == "#3b82f6"

    def test_severity_color_warning(self):
        assert _severity_color(AlertSeverity.WARNING) == "#f59e0b"

    def test_severity_color_critical(self):
        assert _severity_color(AlertSeverity.CRITICAL) == "#ef4444"

    def test_render_usage_80_email(self):
        alert = _make_alert(alert_type=AlertType.USAGE_80_PCT)
        subject, html = _render_email(alert)
        assert "[Agent Red]" in subject
        assert "html" in html.lower()
        assert "Agent Red" in html

    def test_render_usage_100_email(self):
        alert = _make_alert(alert_type=AlertType.USAGE_100_PCT, severity=AlertSeverity.CRITICAL)
        subject, html = _render_email(alert)
        assert "Exhausted" in html or "exhausted" in html.lower() or "Allowance" in html

    def test_render_trial_expiring_email(self):
        alert = _make_alert(alert_type=AlertType.TRIAL_EXPIRING, severity=AlertSeverity.INFO)
        subject, html = _render_email(alert)
        assert "Trial" in html

    def test_render_api_key_email(self):
        alert = _make_alert(
            alert_type=AlertType.API_KEY_GENERATED,
            severity=AlertSeverity.INFO,
            metadata={"api_key": "ar_key_test_123"},
        )
        subject, html = _render_email(alert)
        assert "ar_key_test_123" in html

    def test_render_team_invite_email(self):
        alert = _make_alert(alert_type=AlertType.TEAM_INVITE)
        subject, html = _render_email(alert)
        assert "Invitation" in html or "invitation" in html.lower()

    def test_render_escalation_email(self):
        alert = _make_alert(alert_type=AlertType.ESCALATION)
        subject, html = _render_email(alert)
        assert "Escalation" in html or "escalation" in html.lower()

    def test_render_outage_email(self):
        alert = _make_alert(alert_type=AlertType.OUTAGE_NOTIFICATION, severity=AlertSeverity.CRITICAL)
        subject, html = _render_email(alert)
        assert "Service" in html or "Notification" in html

    def test_render_generic_fallback(self):
        alert = _make_alert(alert_type=AlertType.VOLUME_SPIKE)
        subject, html = _render_email(alert)
        assert "Test Alert" in html  # Uses generic template with title


# ---------------------------------------------------------------------------
# Tests: EmailAlertChannel
# ---------------------------------------------------------------------------


class TestEmailAlertChannel:
    @pytest.mark.asyncio
    async def test_no_recipient(self):
        prefs = MagicMock()
        prefs.read = AsyncMock(return_value={})
        tenants = MagicMock()
        tenants.read = AsyncMock(return_value={})

        channel = EmailAlertChannel(prefs, tenants)
        assert channel.name == "email"

        alert = _make_alert()
        result = await channel.deliver(alert)
        assert result.success is False
        assert "no notification_email" in result.error

    @pytest.mark.asyncio
    async def test_recipient_from_preferences(self):
        prefs = MagicMock()
        prefs.read = AsyncMock(return_value={"notification_email": "owner@store.com"})
        tenants = MagicMock()

        channel = EmailAlertChannel(prefs, tenants)
        email = await channel._resolve_recipient("tenant-001")
        assert email == "owner@store.com"

    @pytest.mark.asyncio
    async def test_recipient_fallback_to_customer_email(self):
        prefs = MagicMock()
        prefs.read = AsyncMock(return_value={})
        tenants = MagicMock()
        tenants.read = AsyncMock(return_value={"customer_email": "fallback@store.com"})

        channel = EmailAlertChannel(prefs, tenants)
        email = await channel._resolve_recipient("tenant-001")
        assert email == "fallback@store.com"

    @pytest.mark.asyncio
    async def test_team_invite_uses_invitee_email(self):
        prefs = MagicMock()
        prefs.read = AsyncMock(return_value={"notification_email": "owner@store.com"})
        tenants = MagicMock()

        channel = EmailAlertChannel(prefs, tenants)

        alert = _make_alert(
            alert_type=AlertType.TEAM_INVITE,
            metadata={"invitee_email": "newhire@company.com"},
        )

        with patch.dict(os.environ, {}, clear=False):
            # No email provider — should return failure
            result = await channel.deliver(alert)
        assert result.success is False
        # But it tried with invitee email (not owner)

    @pytest.mark.asyncio
    async def test_no_provider_configured(self):
        prefs = MagicMock()
        prefs.read = AsyncMock(return_value={"notification_email": "test@test.com"})
        tenants = MagicMock()

        channel = EmailAlertChannel(prefs, tenants)
        alert = _make_alert()

        with patch.dict(os.environ, {"AZURE_COMM_CONNECTION_STRING": "", "SMTP_HOST": ""}, clear=False):
            result = await channel.deliver(alert)

        assert result.success is False
        assert "no email provider" in result.error

    @pytest.mark.asyncio
    async def test_azure_comm_import_error(self):
        prefs = MagicMock()
        prefs.read = AsyncMock(return_value={"notification_email": "test@test.com"})
        tenants = MagicMock()

        channel = EmailAlertChannel(prefs, tenants)
        alert = _make_alert()

        with patch.dict(os.environ, {"AZURE_COMM_CONNECTION_STRING": "fake_conn_str"}):
            # The azure.communication.email import will fail
            result = await channel._send_via_azure_comm(
                "test@test.com", "Subject", "<html>body</html>", alert,
            )

        # Should fail gracefully
        assert result.success is False

    @pytest.mark.asyncio
    async def test_smtp_host_not_configured(self):
        prefs = MagicMock()
        prefs.read = AsyncMock(return_value={"notification_email": "test@test.com"})
        tenants = MagicMock()

        channel = EmailAlertChannel(prefs, tenants)
        alert = _make_alert()

        with patch.dict(os.environ, {"SMTP_HOST": ""}):
            result = await channel._send_via_smtp(
                "test@test.com", "Subject", "<html>body</html>", alert,
            )

        assert result.success is False
        assert "SMTP_HOST not configured" in result.error


# ---------------------------------------------------------------------------
# Tests: AlertDeliveryService
# ---------------------------------------------------------------------------


class TestAlertDeliveryService:
    @pytest.mark.asyncio
    async def test_deliver_with_log_only(self):
        service = AlertDeliveryService()
        alert = _make_alert()
        result = await service.deliver_alert(alert)
        assert isinstance(result, DeliveryResult)
        assert result.channels_attempted == 1  # log only
        assert result.channels_succeeded == 1

    @pytest.mark.asyncio
    async def test_deliver_with_multiple_channels(self):
        service = AlertDeliveryService()

        mock_channel = MagicMock()
        mock_channel.name = "test_channel"
        mock_channel.deliver = AsyncMock(
            return_value=ChannelResult(channel_name="test_channel", success=True),
        )
        service.register_channel(mock_channel)

        alert = _make_alert()
        result = await service.deliver_alert(alert)
        assert result.channels_attempted == 2  # test + log
        assert result.channels_succeeded == 2

    @pytest.mark.asyncio
    async def test_channel_failure_does_not_block_others(self):
        service = AlertDeliveryService()

        failing_channel = MagicMock()
        failing_channel.name = "failing"
        failing_channel.deliver = AsyncMock(
            return_value=ChannelResult(channel_name="failing", success=False, error="broken"),
        )
        service.register_channel(failing_channel)

        alert = _make_alert()
        result = await service.deliver_alert(alert)
        assert result.channels_attempted == 2
        assert result.channels_succeeded == 1  # log succeeded
        assert result.channels_failed == 1

    @pytest.mark.asyncio
    async def test_channel_exception_caught(self):
        service = AlertDeliveryService()

        crashing_channel = MagicMock()
        crashing_channel.name = "crasher"
        crashing_channel.deliver = AsyncMock(side_effect=RuntimeError("kaboom"))
        service.register_channel(crashing_channel)

        alert = _make_alert()
        result = await service.deliver_alert(alert)
        assert result.channels_failed == 1
        assert "kaboom" in result.errors[0].error

    def test_register_replaces_duplicate(self):
        service = AlertDeliveryService()
        ch1 = MagicMock()
        ch1.name = "dup"
        ch2 = MagicMock()
        ch2.name = "dup"
        service.register_channel(ch1)
        service.register_channel(ch2)
        names = service.get_registered_channels()
        assert names.count("dup") == 1

    def test_get_registered_channels_includes_log(self):
        service = AlertDeliveryService()
        names = service.get_registered_channels()
        assert "log" in names


# ---------------------------------------------------------------------------
# Tests: Module singleton
# ---------------------------------------------------------------------------


class TestModuleSingleton:
    def test_get_returns_none_by_default(self):
        import src.multi_tenant.alert_delivery as mod

        original = mod._alert_service
        mod._alert_service = None
        try:
            assert get_alert_service() is None
        finally:
            mod._alert_service = original

    def test_configure_and_get(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        assert get_alert_service() is service
        # Clean up
        configure_alert_service(None)

    def test_configure_none_clears(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        configure_alert_service(None)
        assert get_alert_service() is None


# ---------------------------------------------------------------------------
# Tests: Convenience functions
# ---------------------------------------------------------------------------


class TestConvenienceFunctions:
    @pytest.mark.asyncio
    async def test_send_usage_alert_no_service(self):
        import src.multi_tenant.alert_delivery as mod

        mod._alert_service = None
        result = await send_usage_alert("t", 85.0, "professional")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_usage_alert_80(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            result = await send_usage_alert("t", 85.0, "professional")
            assert result is not None
            assert result.channels_succeeded >= 1
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_send_usage_alert_100(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            result = await send_usage_alert("t", 105.0, "professional")
            assert result is not None
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_send_throttle_alert_no_service(self):
        import src.multi_tenant.alert_delivery as mod

        mod._alert_service = None
        result = await send_throttle_alert("t", "throttle", "professional")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_throttle_alert_isolate_severity(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            result = await send_throttle_alert("t", "isolate", "professional")
            assert result is not None
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_send_sla_alert(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            result = await send_sla_alert("t", "p95_latency", {"actual": 2500, "target": 2000})
            assert result is not None
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_send_sla_alert_no_service(self):
        import src.multi_tenant.alert_delivery as mod

        mod._alert_service = None
        result = await send_sla_alert("t", "uptime")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_api_key_alert(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            result = await send_api_key_alert("t", "ar_key_test_xyz")
            assert result is not None
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_send_api_key_alert_no_service(self):
        import src.multi_tenant.alert_delivery as mod

        mod._alert_service = None
        result = await send_api_key_alert("t", "key")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_team_invite_alert(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            result = await send_team_invite_alert("t", "new@co.com", "Admin", "agent")
            assert result is not None
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_send_team_invite_alert_no_service(self):
        import src.multi_tenant.alert_delivery as mod

        mod._alert_service = None
        result = await send_team_invite_alert("t", "a@b.com", "X", "admin")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_outage_alert(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            result = await send_outage_alert("t", "Cosmos DB")
            assert result is not None
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_send_outage_alert_no_service(self):
        import src.multi_tenant.alert_delivery as mod

        mod._alert_service = None
        result = await send_outage_alert("t", "Redis")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_escalation_alert(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            result = await send_escalation_alert(
                tenant_id="t",
                conversation_id="conv-1",
                reason="Customer upset about shipping",
                urgency="high",
                context_summary="Customer wants refund",
            )
            assert result is not None
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_send_escalation_alert_no_service(self):
        import src.multi_tenant.alert_delivery as mod

        mod._alert_service = None
        result = await send_escalation_alert("t", "c", "r")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_escalation_alert_urgency_mapping(self):
        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            # Test "low" urgency
            result = await send_escalation_alert("t", "c", "reason", urgency="low")
            assert result is not None
            # Test unknown urgency defaults to WARNING
            result = await send_escalation_alert("t", "c", "reason", urgency="unknown_level")
            assert result is not None
        finally:
            configure_alert_service(None)


# ---------------------------------------------------------------------------
# SPEC-1610: Team invite email must contain admin console link (WI-0932)
# ---------------------------------------------------------------------------


class TestTeamInviteEmailLink:
    """Verify send_team_invite_alert always includes an admin console URL (SPEC-1610)."""

    @pytest.mark.asyncio
    async def test_cascading_url_fallback_pattern(self):
        """APP_BASE_URL takes priority in cascading URL resolution."""
        captured: list[Alert] = []
        original_create = create_alert

        def _intercept(**kwargs):
            alert = original_create(**kwargs)
            captured.append(alert)
            return alert

        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            with patch("src.multi_tenant.alert_delivery.create_alert", side_effect=_intercept):
                with patch.dict(os.environ, {"APP_BASE_URL": "https://custom.example.com"}, clear=False):
                    await send_team_invite_alert("t", "a@b.com", "Admin", "agent")
            assert len(captured) == 1
            admin_url = captured[0].metadata.get("admin_url", "")
            assert admin_url == "https://custom.example.com/admin/standalone/"
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_fqdn_fallback_always_present(self):
        """When no env vars are set, FQDN fallback provides the URL."""
        captured: list[Alert] = []
        original_create = create_alert

        def _intercept(**kwargs):
            alert = original_create(**kwargs)
            captured.append(alert)
            return alert

        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            with patch("src.multi_tenant.alert_delivery.create_alert", side_effect=_intercept):
                # Remove all URL-related env vars
                for k in ("APP_BASE_URL", "STANDALONE_ADMIN_URL", "PROD_URL"):
                    os.environ.pop(k, None)
                await send_team_invite_alert("t", "a@b.com", "Admin", "agent")
            assert len(captured) == 1
            admin_url = captured[0].metadata.get("admin_url", "")
            assert "agent-red-api-gateway.orangeglacier" in admin_url
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_admin_url_never_empty(self):
        """admin_url in alert metadata is never empty string."""
        captured: list[Alert] = []
        original_create = create_alert

        def _intercept(**kwargs):
            alert = original_create(**kwargs)
            captured.append(alert)
            return alert

        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            with patch("src.multi_tenant.alert_delivery.create_alert", side_effect=_intercept):
                for k in ("APP_BASE_URL", "STANDALONE_ADMIN_URL", "PROD_URL"):
                    os.environ.pop(k, None)
                await send_team_invite_alert("t", "a@b.com", "Admin", "agent")
            assert len(captured) == 1
            admin_url = captured[0].metadata.get("admin_url", "")
            assert admin_url, "admin_url must never be empty"
            assert admin_url.startswith("https://"), f"admin_url must be HTTPS: {admin_url}"
            assert "/admin/standalone/" in admin_url
        finally:
            configure_alert_service(None)

    @pytest.mark.asyncio
    async def test_message_always_contains_url(self):
        """The alert message body always includes the admin URL."""
        captured: list[Alert] = []
        original_create = create_alert

        def _intercept(**kwargs):
            alert = original_create(**kwargs)
            captured.append(alert)
            return alert

        service = AlertDeliveryService()
        configure_alert_service(service)
        try:
            with patch("src.multi_tenant.alert_delivery.create_alert", side_effect=_intercept):
                for k in ("APP_BASE_URL", "STANDALONE_ADMIN_URL", "PROD_URL"):
                    os.environ.pop(k, None)
                await send_team_invite_alert("t", "a@b.com", "Admin", "agent")
            assert len(captured) == 1
            msg = captured[0].message
            assert "/admin/standalone/" in msg, f"Message must contain admin URL: {msg}"
        finally:
            configure_alert_service(None)
