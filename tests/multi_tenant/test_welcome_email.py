"""Tests for WI-E2 + WI-CP2: Welcome email on tenant creation.

Verifies that:
    - Email body template renders all credential fields + admin URL
    - _build_admin_login_url() resolves correctly (explicit > env > fallback)
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

from src.multi_tenant.welcome_email import (
    _WELCOME_EMAIL_BODY,
    _build_admin_login_url,
    send_welcome_email,
)


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

_TEMPLATE_KWARGS = dict(
    tier="Starter",
    tenant_id="t-001",
    admin_login_url="https://example.com/admin/standalone/",
)


class TestWelcomeEmailTemplate:
    """Verify the HTML body template renders correctly."""

    def test_template_contains_all_fields(self):
        rendered = _WELCOME_EMAIL_BODY.format(**_TEMPLATE_KWARGS)
        assert "Starter" in rendered
        assert "t-001" in rendered
        assert "Next Steps" in rendered
        assert "Sign in to Dashboard" in rendered

    def test_template_does_not_contain_key_blocks(self):
        """Keys are no longer shown in welcome email (SPEC-1673)."""
        rendered = _WELCOME_EMAIL_BODY.format(**_TEMPLATE_KWARGS)
        assert "Admin API Key" not in rendered
        assert "Widget Key" not in rendered
        assert "Security Notice" not in rendered

    def test_template_directs_to_admin_console_for_keys(self):
        """Welcome email tells users to find keys in admin console."""
        rendered = _WELCOME_EMAIL_BODY.format(**_TEMPLATE_KWARGS)
        assert "admin dashboard" in rendered.lower()

    def test_template_contains_admin_login_url(self):
        """WI-CP2: Admin console URL must appear in the email body."""
        rendered = _WELCOME_EMAIL_BODY.format(**_TEMPLATE_KWARGS)
        assert "https://example.com/admin/standalone/" in rendered
        assert "Sign in to Dashboard" in rendered

    def test_template_admin_url_in_next_steps(self):
        """WI-CP2: Next Steps list item links to admin dashboard."""
        rendered = _WELCOME_EMAIL_BODY.format(**_TEMPLATE_KWARGS)
        assert 'href="https://example.com/admin/standalone/"' in rendered

    def test_template_admin_url_button(self):
        """WI-CP2: Prominent CTA button with admin URL."""
        rendered = _WELCOME_EMAIL_BODY.format(**_TEMPLATE_KWARGS)
        # The CTA button href
        assert 'href="https://example.com/admin/standalone/"' in rendered
        # Brand color on the button
        assert "#ff3621" in rendered


# ---------------------------------------------------------------------------
# _build_admin_login_url() — URL resolution
# ---------------------------------------------------------------------------


class TestBuildAdminLoginUrl:
    """WI-CP2: Verify URL resolution priority chain."""

    def test_explicit_url_takes_priority(self):
        with patch.dict("os.environ", {"STANDALONE_ADMIN_URL": "https://env.com/admin/"}):
            result = _build_admin_login_url("https://explicit.com/admin/")
        assert result == "https://explicit.com/admin/"

    def test_standalone_admin_url_env(self):
        with patch.dict("os.environ", {
            "STANDALONE_ADMIN_URL": "https://standalone.com/admin/standalone",
            "PROD_URL": "https://prod.com",
        }, clear=True):
            result = _build_admin_login_url()
        assert result == "https://standalone.com/admin/standalone"

    def test_prod_url_fallback(self):
        with patch.dict("os.environ", {
            "STANDALONE_ADMIN_URL": "",
            "PROD_URL": "https://myapp.azurecontainerapps.io",
        }, clear=True):
            result = _build_admin_login_url()
        assert result == "https://myapp.azurecontainerapps.io/admin/standalone/"

    def test_prod_url_trailing_slash_handled(self):
        with patch.dict("os.environ", {
            "STANDALONE_ADMIN_URL": "",
            "PROD_URL": "https://myapp.azurecontainerapps.io/",
        }, clear=True):
            result = _build_admin_login_url()
        assert result == "https://myapp.azurecontainerapps.io/admin/standalone/"

    def test_no_env_vars_returns_relative_fallback(self):
        """SPEC-0058: Without env vars, returns relative path (no hardcoded FQDN)."""
        with patch.dict("os.environ", {}, clear=True):
            result = _build_admin_login_url()
        assert "/admin/standalone/" in result

    def test_none_explicit_uses_env(self):
        with patch.dict("os.environ", {
            "STANDALONE_ADMIN_URL": "https://env.com/admin/",
        }, clear=True):
            result = _build_admin_login_url(None)
        assert result == "https://env.com/admin/"

    def test_empty_string_explicit_uses_env(self):
        """Empty string is falsy, should fall through to env."""
        with patch.dict("os.environ", {
            "STANDALONE_ADMIN_URL": "https://env.com/admin/",
        }, clear=True):
            result = _build_admin_login_url("")
        assert result == "https://env.com/admin/"


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

        # Use a cleaner approach: mock the import chain
        with (
            patch.dict("os.environ", {"AZURE_COMM_CONNECTION_STRING": "endpoint=test;key=test"}),
            patch("azure.communication.email.EmailClient") as mock_cls,
        ):
            mock_cls.from_connection_string.return_value = mock_client
            result = await send_welcome_email(
                to_email="merchant@example.com",
                tenant_id="t-acs",
                tier="starter",
            )

        assert result is True
        mock_client.begin_send.assert_called_once()
        msg = mock_client.begin_send.call_args[0][0]
        assert msg["recipients"]["to"][0]["address"] == "merchant@example.com"
        assert "Welcome to Agent Red" in msg["content"]["subject"]

    @pytest.mark.asyncio
    async def test_acs_email_contains_admin_url(self):
        """WI-CP2: ACS email body includes admin login URL."""
        mock_poller = MagicMock()
        mock_result = MagicMock()
        mock_result.status = "Succeeded"
        mock_poller.result.return_value = mock_result

        mock_client = MagicMock()
        mock_client.begin_send.return_value = mock_poller

        with (
            patch.dict("os.environ", {
                "AZURE_COMM_CONNECTION_STRING": "endpoint=test;key=test",
                "STANDALONE_ADMIN_URL": "",
                "PROD_URL": "https://myapp.test.io",
            }),
            patch("azure.communication.email.EmailClient") as mock_cls,
        ):
            mock_cls.from_connection_string.return_value = mock_client
            await send_welcome_email(
                to_email="merchant@example.com",
                tenant_id="t-url-test",
            )

        msg = mock_client.begin_send.call_args[0][0]
        html = msg["content"]["html"]
        assert "https://myapp.test.io/admin/standalone/" in html
        assert "Sign in to Dashboard" in html

    @pytest.mark.asyncio
    async def test_explicit_admin_url_overrides_env(self):
        """WI-CP2: Explicit admin_login_url param overrides env var."""
        mock_poller = MagicMock()
        mock_result = MagicMock()
        mock_result.status = "Succeeded"
        mock_poller.result.return_value = mock_result

        mock_client = MagicMock()
        mock_client.begin_send.return_value = mock_poller

        with (
            patch.dict("os.environ", {
                "AZURE_COMM_CONNECTION_STRING": "endpoint=test;key=test",
                "PROD_URL": "https://should-not-appear.test.io",
            }),
            patch("azure.communication.email.EmailClient") as mock_cls,
        ):
            mock_cls.from_connection_string.return_value = mock_client
            await send_welcome_email(
                to_email="merchant@example.com",
                tenant_id="t-explicit",
                admin_login_url="https://custom.example.com/admin/",
            )

        msg = mock_client.begin_send.call_args[0][0]
        html = msg["content"]["html"]
        assert "https://custom.example.com/admin/" in html
        assert "should-not-appear" not in html

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
    async def test_acs_rate_limit_propagates_runtime_error(self):
        """429 rate-limit from ACS raises RuntimeError, not swallowed.

        Regression test for S86: ACS 429 PerSubscriptionPerHourLimitExceeded
        caused SDK to hang for 60+ minutes. The fix makes begin_send() fail
        fast, raising RuntimeError that callers can surface to the user.
        """
        from azure.core.exceptions import HttpResponseError

        exc_429 = HttpResponseError(response=MagicMock(status_code=429))
        exc_429.status_code = 429

        mock_client = MagicMock()
        mock_client.begin_send.side_effect = exc_429

        with (
            patch.dict("os.environ", {"AZURE_COMM_CONNECTION_STRING": "endpoint=test;key=test"}),
            patch("azure.communication.email.EmailClient") as mock_cls,
            patch("azure.core.pipeline.policies.RetryPolicy"),
        ):
            mock_cls.from_connection_string.return_value = mock_client
            with pytest.raises(RuntimeError, match="rate limit exceeded"):
                await send_welcome_email(
                    to_email="merchant@example.com",
                    tenant_id="t-rate-limit",
                )

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
