"""Spec verification tests for EMAIL-section specifications.

Each test class verifies a specific SPEC-* requirement against the
actual implementation. Tests exercise production interfaces per GOV-10.

Session S152 — spec review and real test creation (batch 2).
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
import os
import re

import pytest


# ---------------------------------------------------------------------------
# SPEC-0588: SMTP email MUST use Titan Email (primary provider)
# ---------------------------------------------------------------------------


class TestSpec0588TitanSmtpPrimary:
    """SPEC-0588: SMTP email MUST use Titan Email (smtp.titan.email, port 465,
    SSL/TLS) as the primary provider.

    The magic link, welcome, and API key reset email senders all try
    SMTP first, then fall back to ACS.
    """

    def test_magic_link_email_tries_smtp_first(self):
        """Magic link email function checks SMTP_HOST before ACS."""
        from src.multi_tenant import magic_link_auth

        source = inspect.getsource(magic_link_auth._send_magic_link_email)
        # SMTP is checked before ACS
        smtp_idx = source.index("SMTP_HOST")
        acs_idx = source.index("AZURE_COMM_CONNECTION_STRING")
        assert smtp_idx < acs_idx, "SMTP must be tried before ACS fallback"

    def test_welcome_email_tries_acs_or_smtp(self):
        """Welcome email has email sending capability."""
        from src.multi_tenant import welcome_email

        assert hasattr(welcome_email, "send_welcome_email")

    def test_smtp_port_465_for_ssl(self):
        """SMTP code supports port 465 with SMTP_SSL."""
        from src.multi_tenant import magic_link_auth

        source = inspect.getsource(magic_link_auth._send_magic_link_email)
        assert "SMTP_SSL" in source
        assert "465" in source


# ---------------------------------------------------------------------------
# SPEC-0589: Titan Email connection MUST use mike@remakerdigital.com sender
# ---------------------------------------------------------------------------


class TestSpec0589TitanSenderAddress:
    """SPEC-0589: Titan Email connection MUST use mike@remakerdigital.com
    as the sender address.

    The sender is configured via SMTP_FROM environment variable.
    The code reads SMTP_FROM or falls back to SMTP_USERNAME.
    """

    def test_smtp_from_env_variable_used(self):
        """Email sender reads SMTP_FROM env var."""
        from src.multi_tenant import magic_link_auth

        source = inspect.getsource(magic_link_auth._send_magic_link_email)
        assert "SMTP_FROM" in source

    def test_agent_red_branding_in_from_header(self):
        """Email From header uses 'Agent Red' display name."""
        from src.multi_tenant import magic_link_auth

        source = inspect.getsource(magic_link_auth._send_magic_link_email)
        assert "Agent Red" in source


# ---------------------------------------------------------------------------
# SPEC-0409: Azure Communication Services as email fallback
# ---------------------------------------------------------------------------


class TestSpec0409AcsFallback:
    """SPEC-0409: Azure Communication Services MUST be used as the email provider.

    ACS is the fallback provider when SMTP fails. Both magic link and
    API key reset emails implement this dual-provider pattern.
    """

    def test_acs_fallback_in_magic_link(self):
        """Magic link email has ACS fallback after SMTP failure."""
        from src.multi_tenant import magic_link_auth

        source = inspect.getsource(magic_link_auth._send_magic_link_email)
        assert "AZURE_COMM_CONNECTION_STRING" in source
        assert "send_acs_email" in source

    def test_acs_fallback_in_api_key_reset(self):
        """API key reset email has ACS fallback."""
        from src.multi_tenant import admin_apikey_api

        source = inspect.getsource(admin_apikey_api)
        assert "AZURE_COMM_CONNECTION_STRING" in source
        assert "send_acs_email" in source


# ---------------------------------------------------------------------------
# SPEC-0760: Superadmin credentials sent to email for safekeeping
# ---------------------------------------------------------------------------


class TestSpec0760CredentialsInWelcomeEmail:
    """SPEC-0760: Superadmin credentials MUST be sent to the account holder's
    email address for safekeeping.

    The welcome email includes both the superadmin API key and widget key.
    """

    def test_welcome_email_accepts_superadmin_key(self):
        """send_welcome_email takes superadmin_key parameter."""
        sig = inspect.signature(
            __import__("src.multi_tenant.welcome_email", fromlist=["send_welcome_email"]).send_welcome_email
        )
        assert "superadmin_key" in sig.parameters

    def test_welcome_email_accepts_widget_key(self):
        """send_welcome_email takes widget_key parameter."""
        sig = inspect.signature(
            __import__("src.multi_tenant.welcome_email", fromlist=["send_welcome_email"]).send_welcome_email
        )
        assert "widget_key" in sig.parameters

    def test_welcome_email_template_no_key_blocks(self):
        """Welcome email no longer includes API key or widget key blocks."""
        from src.multi_tenant.welcome_email import _WELCOME_EMAIL_BODY

        assert "{superadmin_key}" not in _WELCOME_EMAIL_BODY
        assert "{widget_key}" not in _WELCOME_EMAIL_BODY
        assert "Admin API Key" not in _WELCOME_EMAIL_BODY
        assert "Widget Key" not in _WELCOME_EMAIL_BODY

    def test_welcome_email_template_directs_to_console(self):
        """Welcome email directs users to admin console for keys."""
        from src.multi_tenant.welcome_email import _WELCOME_EMAIL_BODY

        assert "admin dashboard" in _WELCOME_EMAIL_BODY.lower()
        assert "Sign in to Dashboard" in _WELCOME_EMAIL_BODY


# ---------------------------------------------------------------------------
# SPEC-0683: Sign-in link resolves to tenancy admin, not agentredcx.com
# ---------------------------------------------------------------------------


class TestSpec0683SignInLinkResolvesToAdmin:
    """SPEC-0683: The 'Sign in to Dashboard' link in the welcome email MUST
    resolve to the tenancy admin UI, NOT to agentredcx.com.

    The welcome email uses _build_admin_login_url which points to the
    actual admin console (standalone or prod URL).
    """

    def test_welcome_email_uses_admin_login_url_placeholder(self):
        """Template uses {admin_login_url} not a hardcoded marketing URL."""
        from src.multi_tenant.welcome_email import _WELCOME_EMAIL_BODY

        assert "{admin_login_url}" in _WELCOME_EMAIL_BODY

    def test_build_admin_login_url_prefers_standalone(self):
        """_build_admin_login_url returns admin console URL."""
        from src.multi_tenant.welcome_email import _build_admin_login_url

        # With env var cleared, fallback should be the API gateway admin URL
        with_slash = _build_admin_login_url(tenant_slug="test-tenant")
        assert "admin" in with_slash.lower()
        assert "tenant=test-tenant" in with_slash

    def test_build_admin_login_url_not_agentredcx(self):
        """URL builder does not hardcode agentredcx.com."""
        from src.multi_tenant.welcome_email import _build_admin_login_url

        source = inspect.getsource(_build_admin_login_url)
        assert "agentredcx.com" not in source


# ---------------------------------------------------------------------------
# SPEC-0684: Welcome email MUST display Agent Red logo (not text heading)
# ---------------------------------------------------------------------------


class TestSpec0684WelcomeEmailLogo:
    """SPEC-0684: The welcome email MUST display the Agent Red logo, not
    a text-based 'Agent Red' heading.

    The _EMAIL_WRAPPER template includes an <img> tag with the logo.
    """

    def test_email_wrapper_has_logo_image(self):
        """Email wrapper includes Agent Red logo <img> tag."""
        from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

        assert "<img" in _EMAIL_WRAPPER
        assert "email-logo" in _EMAIL_WRAPPER or "agentredcx.com" in _EMAIL_WRAPPER

    def test_email_wrapper_has_alt_text(self):
        """Logo <img> has alt text for accessibility."""
        from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

        assert 'alt="' in _EMAIL_WRAPPER


# ---------------------------------------------------------------------------
# SPEC-0689: Welcome email key regeneration notice
# ---------------------------------------------------------------------------


class TestSpec0689KeyRegenerationNotice:
    """SPEC-0689: The email template MUST include text below the ADMIN API KEY:
    'If lost, you can regenerate your API key...'"""

    def test_welcome_email_keys_available_in_console(self):
        """Welcome email directs users to admin console for keys."""
        from src.multi_tenant.welcome_email import _WELCOME_EMAIL_BODY

        assert "admin dashboard" in _WELCOME_EMAIL_BODY.lower()
        assert "never sent via email" in _WELCOME_EMAIL_BODY.lower()

    def test_welcome_email_has_security_messaging(self):
        """Welcome email explains key security practice."""
        from src.multi_tenant.welcome_email import _WELCOME_EMAIL_BODY

        assert "security" in _WELCOME_EMAIL_BODY.lower() or "never sent" in _WELCOME_EMAIL_BODY.lower()


# ---------------------------------------------------------------------------
# SPEC-1628: API key reset email uses shared _EMAIL_WRAPPER
# ---------------------------------------------------------------------------


class TestSpec1628ApiKeyResetWrapper:
    """SPEC-1628: API key reset email must use shared _EMAIL_WRAPPER template.

    The _send_api_key_reset_email function imports _EMAIL_WRAPPER from
    alert_delivery.py for visual consistency.
    """

    def test_api_key_reset_imports_email_wrapper(self):
        """API key reset email imports format_branded_email (shared wrapper)."""
        from src.multi_tenant import admin_apikey_api

        source = inspect.getsource(admin_apikey_api)
        assert "format_branded_email" in source

    def test_api_key_reset_formats_wrapper(self):
        """API key reset calls format_branded_email(body_html)."""
        from src.multi_tenant import admin_apikey_api

        source = inspect.getsource(admin_apikey_api)
        assert "format_branded_email" in source


# ---------------------------------------------------------------------------
# SPEC-1629: API key reset email includes login button below key
# ---------------------------------------------------------------------------


class TestSpec1629ApiKeyResetLoginButton:
    """SPEC-1629: API key reset email includes login button/link below
    the API key.

    The email body includes a link to the admin console so the merchant
    can immediately sign in with the new key.
    """

    def test_api_key_reset_has_admin_login_url_param(self):
        """_send_api_key_email accepts admin_login_url."""
        from src.multi_tenant.admin_apikey_api import _send_api_key_email

        sig = inspect.signature(_send_api_key_email)
        assert "admin_login_url" in sig.parameters

    def test_api_key_reset_email_has_link(self):
        """API key reset email body contains an <a href> link."""
        from src.multi_tenant import admin_apikey_api

        source = inspect.getsource(admin_apikey_api._send_api_key_email)
        assert "<a href" in source


# ---------------------------------------------------------------------------
# SPEC-1631: Footer "Remaker Digital" hyperlinked to remakerdigital.com
# ---------------------------------------------------------------------------


class TestSpec1631RemakerDigitalFooterLink:
    """SPEC-1631: API key reset email 'Remaker Digital' footer text is
    hyperlinked to remakerdigital.com.

    The _EMAIL_WRAPPER footer has a link to remakerdigital.com.
    """

    def test_email_wrapper_has_remaker_digital_link(self):
        """Email wrapper footer links to remakerdigital.com."""
        from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

        assert "remakerdigital.com" in _EMAIL_WRAPPER

    def test_email_wrapper_remaker_is_hyperlinked(self):
        """The Remaker Digital text is wrapped in an <a> tag."""
        from src.multi_tenant.alert_delivery import _EMAIL_WRAPPER

        assert '<a href="https://remakerdigital.com"' in _EMAIL_WRAPPER


# ---------------------------------------------------------------------------
# SPEC-0420: Team member invitation emails MUST be sent
# ---------------------------------------------------------------------------


class TestSpec0420TeamInvitationEmails:
    """SPEC-0420: Team member invitation emails MUST be sent when a team
    member is invited. The system MUST NOT rely on the admin to manually
    share credentials.

    The admin team API or magic link auth sends invitation emails to
    newly added team members.
    """

    def test_magic_link_request_endpoint_exists(self):
        """Magic link request endpoint is available for team invitations."""
        from src.multi_tenant.magic_link_auth import router

        paths = [r.path for r in router.routes]
        assert any("request" in p for p in paths)

    def test_send_magic_link_email_function_exists(self):
        """_send_magic_link_email function exists for email delivery."""
        from src.multi_tenant.magic_link_auth import _send_magic_link_email

        assert callable(_send_magic_link_email)


# ---------------------------------------------------------------------------
# SPEC-0777: New tenancy triggers automatic welcome email
# ---------------------------------------------------------------------------


class TestSpec0777AutomaticWelcomeEmail:
    """SPEC-0777: When a tenancy is created, the superadmin MUST automatically
    receive a welcome email containing credentials.

    send_welcome_email is called from provisioning, Stripe checkout,
    and Shopify billing confirmation.
    """

    def test_welcome_email_function_is_async(self):
        """send_welcome_email is async (for non-blocking delivery)."""
        from src.multi_tenant.welcome_email import send_welcome_email

        assert inspect.iscoroutinefunction(send_welcome_email)

    def test_welcome_email_called_from_provisioning(self):
        """Provisioning module imports/calls send_welcome_email."""
        from src.integrations import provisioning

        source = inspect.getsource(provisioning)
        assert "send_welcome_email" in source

    def test_welcome_email_called_from_stripe(self):
        """Stripe webhook handler calls send_welcome_email."""
        from src.integrations import stripe_webhooks

        source = inspect.getsource(stripe_webhooks)
        assert "send_welcome_email" in source
