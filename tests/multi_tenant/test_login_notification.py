"""Tests for SPA Login Notification Emails (SPEC-1676).

Covers:
    send_login_notification() function
    Notification email override (notification_email_address)
    Email failure doesn't block auth
    Email content includes IP and user agent

Run:
    pytest tests/multi_tenant/test_login_notification.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.login_notification import send_login_notification


# ---------------------------------------------------------------------------
# Email sent on SPA login
# ---------------------------------------------------------------------------


class TestLoginNotificationSent:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.alert_delivery.send_acs_email", new_callable=AsyncMock)
    @patch.dict("os.environ", {"ACS_CONNECTION_STRING": "fake-conn-str"})
    async def test_sends_email_on_login(self, mock_send_email):
        await send_login_notification(
            admin_email="admin@remaker.digital",
            notification_email=None,
            client_ip="10.0.0.1",
            user_agent="Mozilla/5.0",
        )
        mock_send_email.assert_called_once()
        call_kwargs = mock_send_email.call_args.kwargs
        assert call_kwargs["to_email"] == "admin@remaker.digital"
        assert "Sign-in" in call_kwargs["subject"]

    @pytest.mark.asyncio
    @patch("src.multi_tenant.alert_delivery.send_acs_email", new_callable=AsyncMock)
    @patch.dict("os.environ", {"ACS_CONNECTION_STRING": "fake-conn-str"})
    async def test_email_contains_ip(self, mock_send_email):
        await send_login_notification(
            admin_email="admin@remaker.digital",
            notification_email=None,
            client_ip="192.168.1.42",
            user_agent="Chrome/120",
        )
        call_kwargs = mock_send_email.call_args.kwargs
        assert "192.168.1.42" in call_kwargs["html_body"]

    @pytest.mark.asyncio
    @patch("src.multi_tenant.alert_delivery.send_acs_email", new_callable=AsyncMock)
    @patch.dict("os.environ", {"ACS_CONNECTION_STRING": "fake-conn-str"})
    async def test_email_contains_user_agent(self, mock_send_email):
        await send_login_notification(
            admin_email="admin@remaker.digital",
            notification_email=None,
            client_ip="10.0.0.1",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        )
        call_kwargs = mock_send_email.call_args.kwargs
        assert "Mozilla/5.0" in call_kwargs["html_body"]


# ---------------------------------------------------------------------------
# Notification email override
# ---------------------------------------------------------------------------


class TestNotificationEmailOverride:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.alert_delivery.send_acs_email", new_callable=AsyncMock)
    @patch.dict("os.environ", {"ACS_CONNECTION_STRING": "fake-conn-str"})
    async def test_notification_email_overrides_admin_email(self, mock_send_email):
        await send_login_notification(
            admin_email="admin@remaker.digital",
            notification_email="alerts@remaker.digital",
            client_ip="10.0.0.1",
            user_agent="Chrome",
        )
        call_kwargs = mock_send_email.call_args.kwargs
        assert call_kwargs["to_email"] == "alerts@remaker.digital"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.alert_delivery.send_acs_email", new_callable=AsyncMock)
    @patch.dict("os.environ", {"ACS_CONNECTION_STRING": "fake-conn-str"})
    async def test_falls_back_to_admin_email_when_no_override(self, mock_send_email):
        await send_login_notification(
            admin_email="admin@remaker.digital",
            notification_email=None,
            client_ip="10.0.0.1",
            user_agent="Chrome",
        )
        call_kwargs = mock_send_email.call_args.kwargs
        assert call_kwargs["to_email"] == "admin@remaker.digital"


# ---------------------------------------------------------------------------
# Email failure doesn't block auth
# ---------------------------------------------------------------------------


class TestEmailFailureHandling:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.alert_delivery.send_acs_email", new_callable=AsyncMock)
    @patch.dict("os.environ", {"ACS_CONNECTION_STRING": "fake-conn-str"})
    async def test_email_failure_does_not_raise(self, mock_send_email):
        mock_send_email.side_effect = Exception("SMTP connection failed")
        # Should not raise — swallows errors
        await send_login_notification(
            admin_email="admin@remaker.digital",
            notification_email=None,
            client_ip="10.0.0.1",
            user_agent="Chrome",
        )

    @pytest.mark.asyncio
    async def test_no_acs_connection_string_skips_silently(self):
        # ACS_CONNECTION_STRING not set → should skip without error
        with patch.dict("os.environ", {"ACS_CONNECTION_STRING": ""}):
            await send_login_notification(
                admin_email="admin@remaker.digital",
                notification_email=None,
                client_ip="10.0.0.1",
                user_agent="Chrome",
            )


# ---------------------------------------------------------------------------
# Middleware integration
# ---------------------------------------------------------------------------


class TestMiddlewareIntegration:

    def test_notification_task_set_exists(self):
        from src.multi_tenant.middleware import _spa_notification_tasks
        assert isinstance(_spa_notification_tasks, set)

    def test_tenant_context_has_notification_email_field(self):
        from src.multi_tenant.auth import TenantContext
        ctx = TenantContext(
            tenant_id="__platform__",
            is_platform_admin=True,
            platform_admin_email="admin@test.com",
            platform_admin_notification_email="alerts@test.com",
        )
        assert ctx.platform_admin_notification_email == "alerts@test.com"

    def test_notification_email_defaults_to_none(self):
        from src.multi_tenant.auth import TenantContext
        ctx = TenantContext(tenant_id="t1")
        assert ctx.platform_admin_notification_email is None
