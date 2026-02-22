"""Tests for WI-E2: Welcome email on tenant creation.

Verifies that:
    - Email body template renders all credential fields
    - ACS provider path sends successfully
    - SMTP fallback sends when ACS is not configured
    - Graceful failure when no provider configured
    - Missing email address returns False immediately
    - Provisioning call sites invoke welcome email

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.welcome_email import _WELCOME_EMAIL_BODY, send_welcome_email


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------


class TestWelcomeEmailTemplate:
    """Verify the HTML body template renders correctly."""

    def test_template_contains_all_fields(self):
        rendered = _WELCOME_EMAIL_BODY.format(
            superadmin_key="ar_user_test_abc123",
            widget_key="pk_live_abc123_def456",
            tier="Starter",
            tenant_id="t-001",
        )
        assert "ar_user_test_abc123" in rendered
        assert "pk_live_abc123_def456" in rendered
        assert "Starter" in rendered
        assert "t-001" in rendered
        assert "Admin API Key" in rendered
        assert "Widget Key" in rendered
        assert "Security Notice" in rendered
        assert "Next Steps" in rendered

    def test_template_handles_missing_keys(self):
        rendered = _WELCOME_EMAIL_BODY.format(
            superadmin_key="(not generated)",
            widget_key="(not generated)",
            tier="Trial",
            tenant_id="t-002",
        )
        assert "(not generated)" in rendered


# ---------------------------------------------------------------------------
# send_welcome_email() — provider routing
# ---------------------------------------------------------------------------


class TestSendWelcomeEmail:
    """Tests for the send_welcome_email() async function."""

    @pytest.mark.asyncio
    async def test_returns_false_for_empty_email(self):
        result = await send_welcome_email(
            to_email="",
            tenant_id="t-001",
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_for_none_email(self):
        result = await send_welcome_email(
            to_email=None,
            tenant_id="t-001",
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_acs_provider_success(self):
        """ACS path sends when connection string is configured."""
        mock_poller = MagicMock()
        mock_result = MagicMock()
        mock_result.status = "Succeeded"
        mock_poller.result.return_value = mock_result

        mock_client = MagicMock()
        mock_client.begin_send.return_value = mock_poller

        with (
            patch.dict("os.environ", {"AZURE_COMM_CONNECTION_STRING": "endpoint=test;key=test"}),
            patch(
                "src.multi_tenant.welcome_email.EmailClient",
                create=True,
            ) as mock_email_cls,
        ):
            # Patch the lazy import
            import src.multi_tenant.welcome_email as mod

            with patch.object(mod, "__builtins__", mod.__builtins__, create=True):
                with patch(
                    "azure.communication.email.EmailClient.from_connection_string",
                    return_value=mock_client,
                ):
                    # Simpler approach: mock at the os.environ level and
                    # patch the EmailClient import inside the function
                    pass

        # Use a cleaner approach: mock the import chain
        with (
            patch.dict("os.environ", {"AZURE_COMM_CONNECTION_STRING": "endpoint=test;key=test"}),
            patch("azure.communication.email.EmailClient") as mock_cls,
        ):
            mock_cls.from_connection_string.return_value = mock_client
            result = await send_welcome_email(
                to_email="merchant@example.com",
                tenant_id="t-acs",
                superadmin_key="ar_user_test_key",
                widget_key="pk_live_test_key",
                tier="starter",
            )

        assert result is True
        mock_client.begin_send.assert_called_once()
        msg = mock_client.begin_send.call_args[0][0]
        assert msg["recipients"]["to"][0]["address"] == "merchant@example.com"
        assert "Welcome to Agent Red" in msg["content"]["subject"]

    @pytest.mark.asyncio
    async def test_acs_failure_returns_false(self):
        """ACS exception returns False, doesn't raise."""
        with (
            patch.dict("os.environ", {"AZURE_COMM_CONNECTION_STRING": "endpoint=test;key=test"}),
            patch("azure.communication.email.EmailClient") as mock_cls,
        ):
            mock_cls.from_connection_string.side_effect = Exception("ACS unavailable")
            result = await send_welcome_email(
                to_email="merchant@example.com",
                tenant_id="t-fail",
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_no_provider_returns_false(self):
        """Returns False when neither ACS nor SMTP is configured."""
        with patch.dict("os.environ", {}, clear=True):
            result = await send_welcome_email(
                to_email="merchant@example.com",
                tenant_id="t-none",
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_smtp_fallback_when_no_acs(self):
        """SMTP path is used when ACS connection string is empty."""
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)

        env = {
            "AZURE_COMM_CONNECTION_STRING": "",
            "SMTP_HOST": "smtp.test.com",
            "SMTP_PORT": "587",
            "SMTP_USERNAME": "user",
            "SMTP_PASSWORD": "pass",
        }
        with (
            patch.dict("os.environ", env, clear=True),
            patch("smtplib.SMTP", return_value=mock_smtp),
        ):
            result = await send_welcome_email(
                to_email="merchant@example.com",
                tenant_id="t-smtp",
                superadmin_key="ar_user_test_key",
                tier="professional",
            )

        assert result is True
        mock_smtp.send_message.assert_called_once()


# ---------------------------------------------------------------------------
# Integration with provisioning call sites
# ---------------------------------------------------------------------------


class TestWelcomeEmailIntegration:
    """Verify welcome email is called from provisioning flows."""

    @pytest.mark.asyncio
    async def test_trial_provisioning_sends_welcome(self):
        """provision_trial_tenant() calls send_welcome_email."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        fake_prefs_repo = AsyncMock()

        with (
            patch("src.integrations.provisioning._tenant_repo", fake_repo),
            patch(
                "src.multi_tenant.repository.PreferencesRepository",
                return_value=fake_prefs_repo,
            ),
            patch(
                "src.multi_tenant.welcome_email.send_welcome_email",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_send,
        ):
            from src.integrations.provisioning import provision_trial_tenant

            record = await provision_trial_tenant(
                customer_email="trial@example.com",
                trial_duration_days=14,
            )

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["to_email"] == "trial@example.com"
        assert call_kwargs["tier"] == "trial"
        assert call_kwargs["widget_key"] is not None

    @pytest.mark.asyncio
    async def test_trial_provisioning_no_email_skips_welcome(self):
        """provision_trial_tenant() skips welcome email when no email given."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        fake_prefs_repo = AsyncMock()

        with (
            patch("src.integrations.provisioning._tenant_repo", fake_repo),
            patch(
                "src.multi_tenant.repository.PreferencesRepository",
                return_value=fake_prefs_repo,
            ),
            patch(
                "src.multi_tenant.welcome_email.send_welcome_email",
                new_callable=AsyncMock,
            ) as mock_send,
        ):
            from src.integrations.provisioning import provision_trial_tenant

            record = await provision_trial_tenant(customer_email=None)

        mock_send.assert_not_called()
