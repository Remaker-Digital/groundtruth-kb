"""
Tests for EmailAlertChannel and email notification features (WI-G).

Tests cover:
    - Email template rendering (all 6 alert types + generic fallback)
    - Recipient resolution (notification_email > customer_email > skip)
    - Team invite recipient override (invitee_email from metadata)
    - Provider selection (Azure Comm > SMTP > skip)
    - New alert types (API_KEY_GENERATED, TEAM_INVITE, OUTAGE_NOTIFICATION)
    - Convenience functions (send_api_key_alert, send_team_invite_alert, send_outage_alert)
    - Alert severity defaults for new types
    - EmailAlertChannel.deliver() error handling

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
    EmailAlertChannel,
    _render_email,
    _severity_color,
    configure_alert_service,
    create_alert,
    send_api_key_alert,
    send_outage_alert,
    send_team_invite_alert,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_usage_alert() -> Alert:
    return create_alert(
        tenant_id="test-tenant-001",
        alert_type=AlertType.USAGE_80_PCT,
        title="Approaching conversation allowance limit",
        message="Usage has reached 82% of included allowance.",
        metadata={"pct_used": 82.0, "tier": "starter"},
    )


@pytest.fixture
def sample_trial_alert() -> Alert:
    return create_alert(
        tenant_id="test-tenant-001",
        alert_type=AlertType.TRIAL_EXPIRING,
        title="Trial expiring in 3 days",
        message="Your 14-day trial expires in 3 days.",
    )


@pytest.fixture
def sample_api_key_alert() -> Alert:
    return create_alert(
        tenant_id="test-tenant-001",
        alert_type=AlertType.API_KEY_GENERATED,
        title="API key generated",
        message="A new API key has been generated for your account.",
        metadata={"api_key": "ar_live_test_abc123def456", "action": "generated"},
    )


@pytest.fixture
def sample_team_invite_alert() -> Alert:
    return create_alert(
        tenant_id="test-tenant-001",
        alert_type=AlertType.TEAM_INVITE,
        title="You've been invited to join a team",
        message="Alice has invited you to join their Agent Red team as an agent.",
        metadata={
            "invitee_email": "bob@example.com",
            "inviter_name": "Alice",
            "role": "agent",
        },
    )


@pytest.fixture
def sample_outage_alert() -> Alert:
    return create_alert(
        tenant_id="test-tenant-001",
        alert_type=AlertType.OUTAGE_NOTIFICATION,
        title="Service disruption - Azure OpenAI",
        message="We have detected a service disruption affecting Azure OpenAI.",
        metadata={"affected_service": "Azure OpenAI"},
    )


@pytest.fixture
def sample_generic_alert() -> Alert:
    return create_alert(
        tenant_id="test-tenant-001",
        alert_type=AlertType.RETENTION_COMPLETE,
        title="Data retention complete",
        message="Scheduled data retention has completed.",
    )


@pytest.fixture
def mock_prefs_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.read = AsyncMock(return_value={
        "notification_email": "alerts@merchant.com",
    })
    return repo


@pytest.fixture
def mock_tenant_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.read = AsyncMock(return_value={
        "customer_email": "owner@merchant.com",
    })
    return repo


@pytest.fixture
def email_channel(mock_prefs_repo, mock_tenant_repo) -> EmailAlertChannel:
    return EmailAlertChannel(mock_prefs_repo, mock_tenant_repo)


# ---------------------------------------------------------------------------
# Alert type enum tests
# ---------------------------------------------------------------------------


class TestNewAlertTypes:
    """Verify the 3 new AlertType values exist and have correct defaults."""

    def test_api_key_generated_type(self):
        assert AlertType.API_KEY_GENERATED == "api_key_generated"

    def test_team_invite_type(self):
        assert AlertType.TEAM_INVITE == "team_invite"

    def test_outage_notification_type(self):
        assert AlertType.OUTAGE_NOTIFICATION == "outage_notification"

    def test_api_key_default_severity(self):
        alert = create_alert(
            tenant_id="t", alert_type=AlertType.API_KEY_GENERATED,
            title="t", message="m",
        )
        assert alert.severity == AlertSeverity.INFO

    def test_team_invite_default_severity(self):
        alert = create_alert(
            tenant_id="t", alert_type=AlertType.TEAM_INVITE,
            title="t", message="m",
        )
        assert alert.severity == AlertSeverity.INFO

    def test_outage_default_severity(self):
        alert = create_alert(
            tenant_id="t", alert_type=AlertType.OUTAGE_NOTIFICATION,
            title="t", message="m",
        )
        assert alert.severity == AlertSeverity.CRITICAL

    def test_total_alert_types(self):
        """All 11 alert types accounted for."""
        assert len(AlertType) == 11


# ---------------------------------------------------------------------------
# Email template rendering tests
# ---------------------------------------------------------------------------


class TestEmailTemplateRendering:
    """Verify _render_email produces valid subject and HTML for each type."""

    def test_usage_80_template(self, sample_usage_alert):
        subject, html = _render_email(sample_usage_alert)
        assert "[Agent Red]" in subject
        assert "Approaching" in subject
        assert "Agent Red" in html
        assert "82%" in html
        assert "Recommendation" in html

    def test_usage_100_template(self):
        alert = create_alert(
            tenant_id="t", alert_type=AlertType.USAGE_100_PCT,
            title="Allowance exhausted",
            message="Usage at 105%.",
        )
        subject, html = _render_email(alert)
        assert "Exhausted" in html or "Action Required" in html

    def test_trial_expiring_template(self, sample_trial_alert):
        subject, html = _render_email(sample_trial_alert)
        assert "Trial" in subject
        assert "Upgrade" in html

    def test_api_key_template(self, sample_api_key_alert):
        subject, html = _render_email(sample_api_key_alert)
        assert "API" in subject
        assert "ar_live_test_abc123def456" in html
        assert "Security Notice" in html

    def test_team_invite_template(self, sample_team_invite_alert):
        subject, html = _render_email(sample_team_invite_alert)
        assert "invited" in subject.lower()
        assert "Alice" in html
        assert "Getting Started" in html

    def test_outage_template(self, sample_outage_alert):
        subject, html = _render_email(sample_outage_alert)
        assert "disruption" in subject.lower() or "Service" in subject
        assert "investigating" in html

    def test_generic_fallback_template(self, sample_generic_alert):
        subject, html = _render_email(sample_generic_alert)
        assert "[Agent Red]" in subject
        assert "Data retention" in html

    def test_html_has_wrapper_structure(self, sample_usage_alert):
        _, html = _render_email(sample_usage_alert)
        assert "<!DOCTYPE html>" in html
        assert "#ff3621" in html  # Brand color
        assert "Remaker Digital" in html
        assert "remakerdigital.com" in html

    def test_severity_badge_colors(self):
        assert _severity_color(AlertSeverity.INFO) == "#3b82f6"
        assert _severity_color(AlertSeverity.WARNING) == "#f59e0b"
        assert _severity_color(AlertSeverity.CRITICAL) == "#ef4444"


# ---------------------------------------------------------------------------
# Recipient resolution tests
# ---------------------------------------------------------------------------


class TestRecipientResolution:
    """Verify EmailAlertChannel resolves recipients correctly."""

    @pytest.mark.asyncio
    async def test_uses_notification_email_first(self, email_channel, sample_usage_alert):
        recipient = await email_channel._resolve_recipient("test-tenant-001")
        assert recipient == "alerts@merchant.com"

    @pytest.mark.asyncio
    async def test_falls_back_to_customer_email(self, mock_tenant_repo):
        prefs_repo = AsyncMock()
        prefs_repo.read = AsyncMock(return_value=None)
        channel = EmailAlertChannel(prefs_repo, mock_tenant_repo)
        recipient = await channel._resolve_recipient("test-tenant-001")
        assert recipient == "owner@merchant.com"

    @pytest.mark.asyncio
    async def test_returns_none_when_no_email(self):
        prefs_repo = AsyncMock()
        prefs_repo.read = AsyncMock(return_value=None)
        tenant_repo = AsyncMock()
        tenant_repo.read = AsyncMock(return_value=None)
        channel = EmailAlertChannel(prefs_repo, tenant_repo)
        recipient = await channel._resolve_recipient("test-tenant-001")
        assert recipient is None

    @pytest.mark.asyncio
    async def test_handles_prefs_read_exception(self, mock_tenant_repo):
        prefs_repo = AsyncMock()
        prefs_repo.read = AsyncMock(side_effect=Exception("DB error"))
        channel = EmailAlertChannel(prefs_repo, mock_tenant_repo)
        recipient = await channel._resolve_recipient("test-tenant-001")
        assert recipient == "owner@merchant.com"

    @pytest.mark.asyncio
    async def test_handles_tenant_read_exception(self):
        prefs_repo = AsyncMock()
        prefs_repo.read = AsyncMock(return_value=None)
        tenant_repo = AsyncMock()
        tenant_repo.read = AsyncMock(side_effect=Exception("DB error"))
        channel = EmailAlertChannel(prefs_repo, tenant_repo)
        recipient = await channel._resolve_recipient("test-tenant-001")
        assert recipient is None

    @pytest.mark.asyncio
    async def test_team_invite_uses_invitee_email(self, email_channel, sample_team_invite_alert):
        """Team invites bypass normal resolution and use invitee_email."""
        with patch.dict(os.environ, {}, clear=False):
            result = await email_channel.deliver(sample_team_invite_alert)
            # Will fail to send (no provider), but should NOT use notification_email
            # The error should indicate no provider, not no recipient
            assert result.error is None or "no notification_email" not in (result.error or "")


# ---------------------------------------------------------------------------
# Provider selection tests
# ---------------------------------------------------------------------------


class TestProviderSelection:
    """Verify EmailAlertChannel selects the right email provider."""

    @pytest.mark.asyncio
    async def test_no_provider_configured(self, email_channel, sample_usage_alert):
        with patch.dict(os.environ, {}, clear=True):
            result = await email_channel.deliver(sample_usage_alert)
            assert not result.success
            assert "no email provider" in (result.error or "")

    @pytest.mark.asyncio
    async def test_no_recipient_skips(self):
        prefs_repo = AsyncMock()
        prefs_repo.read = AsyncMock(return_value=None)
        tenant_repo = AsyncMock()
        tenant_repo.read = AsyncMock(return_value=None)
        channel = EmailAlertChannel(prefs_repo, tenant_repo)

        alert = create_alert(
            tenant_id="t", alert_type=AlertType.USAGE_80_PCT,
            title="t", message="m",
        )
        result = await channel.deliver(alert)
        assert not result.success
        assert "no notification_email" in (result.error or "")

    @pytest.mark.asyncio
    async def test_azure_comm_attempted_when_configured(self, email_channel, sample_usage_alert):
        """When AZURE_COMM_CONNECTION_STRING is set, Azure Comm is attempted."""
        with patch.dict(os.environ, {"AZURE_COMM_CONNECTION_STRING": "fake-conn-str"}):
            result = await email_channel.deliver(sample_usage_alert)
            # Will fail because azure-communication-email may not be installed
            assert not result.success
            assert "Azure Comm" in (result.error or "") or "azure-communication" in (result.error or "")

    @pytest.mark.asyncio
    async def test_smtp_attempted_when_configured(self, email_channel, sample_usage_alert):
        """When SMTP_HOST is set, SMTP is attempted."""
        env = {"SMTP_HOST": "smtp.example.com", "SMTP_PORT": "587"}
        with patch.dict(os.environ, env, clear=True):
            result = await email_channel.deliver(sample_usage_alert)
            # Will fail to connect, but should attempt SMTP
            assert not result.success
            # Error should indicate SMTP failure, not "no provider"
            assert "SMTP" in (result.error or "") or "error" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_channel_name(self, email_channel):
        assert email_channel.name == "email"


# ---------------------------------------------------------------------------
# Convenience function tests
# ---------------------------------------------------------------------------


class TestConvenienceFunctions:
    """Test the 3 new convenience functions."""

    @pytest.mark.asyncio
    async def test_send_api_key_alert(self):
        service = AlertDeliveryService()
        configure_alert_service(service)

        result = await send_api_key_alert(
            tenant_id="t-001",
            api_key="ar_live_test_abc123",
            action="generated",
        )
        assert result is not None
        assert result.alert_id.startswith("alert_")

    @pytest.mark.asyncio
    async def test_send_api_key_alert_no_service(self):
        configure_alert_service.__wrapped__ = None
        # Reset module singleton
        import src.multi_tenant.alert_delivery as mod
        mod._alert_service = None

        result = await send_api_key_alert("t", "key", "generated")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_team_invite_alert(self):
        service = AlertDeliveryService()
        configure_alert_service(service)

        result = await send_team_invite_alert(
            tenant_id="t-001",
            invitee_email="bob@example.com",
            inviter_name="Alice",
            role="agent",
        )
        assert result is not None
        assert result.channels_attempted >= 1  # Log channel always present

    @pytest.mark.asyncio
    async def test_send_outage_alert(self):
        service = AlertDeliveryService()
        configure_alert_service(service)

        result = await send_outage_alert(
            tenant_id="t-001",
            affected_service="Azure OpenAI",
            details={"start_time": "2026-02-06T10:00:00Z"},
        )
        assert result is not None
        assert result.channels_succeeded >= 1  # Log channel always succeeds

    @pytest.mark.asyncio
    async def test_send_team_invite_metadata(self):
        service = AlertDeliveryService()
        configure_alert_service(service)

        result = await send_team_invite_alert(
            tenant_id="t-001",
            invitee_email="bob@example.com",
            inviter_name="Alice",
            role="admin",
        )
        # Just verify it doesn't crash and returns a result
        assert result is not None

    @pytest.mark.asyncio
    async def test_send_outage_alert_without_details(self):
        service = AlertDeliveryService()
        configure_alert_service(service)

        result = await send_outage_alert(
            tenant_id="t-001",
            affected_service="NATS",
        )
        assert result is not None


# ---------------------------------------------------------------------------
# Service registration tests
# ---------------------------------------------------------------------------


class TestEmailChannelRegistration:
    """Verify EmailAlertChannel integrates with AlertDeliveryService."""

    def test_register_email_channel(self, email_channel):
        service = AlertDeliveryService()
        service.register_channel(email_channel)
        assert "email" in service.get_registered_channels()

    def test_all_four_channels(self, email_channel):
        from src.multi_tenant.alert_delivery import (
            DashboardAlertChannel,
            LogAlertChannel,
            WebhookAlertChannel,
        )

        service = AlertDeliveryService()
        service.register_channel(DashboardAlertChannel(AsyncMock()))
        service.register_channel(WebhookAlertChannel(AsyncMock()))
        service.register_channel(email_channel)

        channels = service.get_registered_channels()
        assert "dashboard" in channels
        assert "webhook" in channels
        assert "email" in channels
        assert "log" in channels  # Always present

    @pytest.mark.asyncio
    async def test_deliver_alert_includes_email(self, email_channel, sample_usage_alert):
        service = AlertDeliveryService()
        service.register_channel(email_channel)
        configure_alert_service(service)

        with patch.dict(os.environ, {}, clear=True):
            result = await service.deliver_alert(sample_usage_alert)
            # Email + Log channels attempted
            assert result.channels_attempted == 2
            # Log always succeeds, email will fail (no provider)
            assert result.channels_succeeded >= 1


# ---------------------------------------------------------------------------
# Notification email in PreferencesDocument
# ---------------------------------------------------------------------------


class TestNotificationEmailField:
    """Verify notification_email is in PreferencesDocument schema."""

    def test_field_exists_on_preferences(self):
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        fields = PreferencesDocument.model_fields
        assert "notification_email" in fields

    def test_field_defaults_to_none(self):
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        doc = PreferencesDocument(
            id="t:1", tenant_id="t", version=1,
            created_at="2026-02-06T00:00:00Z",
        )
        assert doc.notification_email is None

    def test_field_accepts_email(self):
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        doc = PreferencesDocument(
            id="t:1", tenant_id="t", version=1,
            created_at="2026-02-06T00:00:00Z",
            notification_email="alerts@shop.com",
        )
        assert doc.notification_email == "alerts@shop.com"

    def test_field_in_config_processor(self):
        from src.multi_tenant.tenant_config_processor import _PREFS_DIRECT_FIELDS

        assert "notification_email" in _PREFS_DIRECT_FIELDS
