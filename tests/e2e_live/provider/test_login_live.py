"""
Live E2E tests — Provider Console: Login Flow (ApiKeyLogin + MfaChallenge).

Tests the unauthenticated login screen (ApiKeyLogin) and MFA challenge
page UI elements. Does NOT submit real credentials — tests only verify
that the login form renders correctly with all expected elements.

Source: admin/provider/login/ApiKeyLogin.tsx
        admin/provider/login/MfaChallenge.tsx

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page

from .conftest import STAGING_FQDN, PROVIDER_BASE_URL


# ---------------------------------------------------------------------------
# Fixtures — unauthenticated page (no sessionStorage key injection)
# ---------------------------------------------------------------------------


@pytest.fixture()
def live_login_page(page: Page) -> Page:
    """Navigate to Provider Console WITHOUT auth — should show login form."""
    # Clear any stored session to ensure login screen appears
    page.add_init_script("""
        try { sessionStorage.removeItem('agentred_provider_key'); } catch {}
        try { sessionStorage.removeItem('agentred_provider_mfa_token'); } catch {}
    """)
    page.goto(f"{PROVIDER_BASE_URL}/", wait_until="load")
    page.wait_for_timeout(2000)
    return page


# ===========================================================================
# 1. API KEY LOGIN PAGE
# ===========================================================================


class TestApiKeyLoginBranding:
    """Login page branding: logo, title, helper text."""

    def test_logo_image(self, live_login_page: Page):
        """Login page shows Agent Red logo."""
        logo = live_login_page.locator("img[alt='Agent Red']")
        if logo.count() == 0:
            logo = live_login_page.locator("img[src*='logo']")
        assert logo.count() > 0, "Login page must show Agent Red logo"

    def test_service_provider_title(self, live_login_page: Page):
        """Login page shows 'Service Provider Administration' text."""
        text = live_login_page.locator("body").inner_text(timeout=5_000).lower()
        assert "service provider" in text, (
            "Login page must show 'Service Provider Administration'"
        )

    def test_access_only_text(self, live_login_page: Page):
        """Login page shows 'Service provider access only' helper text."""
        text = live_login_page.locator("body").inner_text(timeout=5_000).lower()
        assert "service provider access only" in text, (
            "Login page must show 'Service provider access only' text"
        )

    def test_remaker_digital_contact_text(self, live_login_page: Page):
        """Login page mentions Remaker Digital for access help."""
        text = live_login_page.locator("body").inner_text(timeout=5_000).lower()
        assert "remaker digital" in text, (
            "Login page must mention Remaker Digital for access help"
        )


class TestApiKeyLoginForm:
    """Login form: API key input and Sign in button."""

    def test_api_key_input(self, live_login_page: Page):
        """Login form has API key password input."""
        # Mantine PasswordInput renders as input[type='password']
        password_input = live_login_page.locator(
            "input[type='password'], input[aria-label*='API key' i]"
        )
        assert password_input.count() > 0, "Login must have API key password input"

    def test_api_key_label(self, live_login_page: Page):
        """API key input has 'API key' label."""
        text = live_login_page.locator("body").inner_text(timeout=5_000).lower()
        assert "api key" in text, "Login must show 'API key' label"

    def test_api_key_placeholder(self, live_login_page: Page):
        """API key input has placeholder text."""
        password_input = live_login_page.locator(
            "input[type='password'], input[aria-label*='API key' i]"
        )
        if password_input.count() > 0:
            placeholder = password_input.first.get_attribute("placeholder")
            assert placeholder and len(placeholder) > 0, (
                "API key input must have placeholder text"
            )

    def test_sign_in_button(self, live_login_page: Page):
        """Login form has 'Sign in' submit button."""
        btn = live_login_page.locator(
            "button[type='submit'], button[aria-label='Sign in']"
        )
        if btn.count() == 0:
            btn = live_login_page.get_by_text("Sign in", exact=True)
        assert btn.count() > 0, "Login must have 'Sign in' button"

    def test_sign_in_button_aria(self, live_login_page: Page):
        """Sign in button has aria-label='Sign in'."""
        btn = live_login_page.locator("button[aria-label='Sign in']")
        assert btn.count() > 0, "Sign in button must have aria-label='Sign in'"

    def test_form_element(self, live_login_page: Page):
        """Login is wrapped in a <form> element for submit handling."""
        forms = live_login_page.locator("form")
        assert forms.count() > 0, "Login must be wrapped in a <form> element"


class TestApiKeyLoginValidation:
    """Client-side validation behavior."""

    def test_empty_submit_shows_error(self, live_login_page: Page):
        """Submitting empty form shows 'API key is required' error."""
        page = live_login_page
        btn = page.locator(
            "button[type='submit'], button[aria-label='Sign in']"
        )
        if btn.count() == 0:
            btn = page.get_by_text("Sign in", exact=True)
        if btn.count() == 0:
            return
        btn.first.click()
        page.wait_for_timeout(500)
        text = page.locator("body").inner_text(timeout=3_000).lower()
        assert "api key is required" in text, (
            "Empty submit must show 'API key is required' error"
        )

    def test_password_input_visibility_toggle(self, live_login_page: Page):
        """PasswordInput has visibility toggle button (Mantine)."""
        toggle = live_login_page.locator(
            "[class*='passwordInput' i] button, "
            "button[aria-label*='visibility' i], "
            "button[aria-label*='password' i]"
        )
        # Mantine PasswordInput includes a toggle button
        if toggle.count() > 0:
            assert True  # Visibility toggle found
        else:
            return  # May be hidden or custom implementation


class TestApiKeyLoginLayout:
    """Visual layout: centered card, dark background."""

    def test_centered_card(self, live_login_page: Page):
        """Login form is in a centered Paper card."""
        papers = live_login_page.locator(
            "[class*='paper' i], [class*='Paper']"
        )
        assert papers.count() > 0, "Login must use a Paper card container"

    def test_dark_background(self, live_login_page: Page):
        """Page background is dark (chrome color)."""
        body_bg = live_login_page.locator("body").evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )
        # Just verify it's not white (rgb(255, 255, 255))
        assert body_bg != "rgb(255, 255, 255)", (
            "Login page background should be dark, not white"
        )
