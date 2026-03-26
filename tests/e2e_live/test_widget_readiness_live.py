"""
Live E2E tests for post-deploy widget readiness.

Verifies the widget is visible and functional in both the standalone
admin UI and the connected Shopify storefront. These are the browser-
based checks that cannot be done from a Python script (complement to
Phase-C checks C.36–C.41 in upgrade_verification.py).

Checks:
  1. Widget launcher visible in standalone admin UI
  2. Widget chat panel opens in admin UI
  3. Widget launcher visible on Shopify storefront
  4. Widget chat panel opens on storefront
  5. User can type and send a message on storefront
  6. AI response appears in the conversation

Run:
    pytest tests/e2e_live/test_widget_readiness_live.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import Page, expect

from tests.e2e_live.conftest import (
    LIVE_API_KEY,
    LIVE_SPA_BASE_URL,
    LIVE_TENANT_ID,
    _dismiss_onboarding_modal,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SHOPIFY_STORE_DOMAIN = "blanco-9939.myshopify.com"
SHOPIFY_STORE_PASSWORD = os.environ.get("SHOPIFY_STORE_PASSWORD", "")

# Production gateway — for storefront widget verification
API_GATEWAY_FQDN = os.environ.get(
    "API_GATEWAY_FQDN",
    os.environ.get(
        "CONTAINER_APP_FQDN",
        "agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
    ),
)

# Timeout for widget elements to appear (ms)
WIDGET_TIMEOUT = 15_000
# Timeout for AI response to appear (ms)
AI_RESPONSE_TIMEOUT = 45_000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bypass_shopify_password(page: Page, domain: str) -> None:
    """Submit the Shopify store password if the storefront is gated."""
    if not SHOPIFY_STORE_PASSWORD:
        pytest.skip(
            f"Storefront {domain} is password-protected but "
            f"SHOPIFY_STORE_PASSWORD is not set."
        )

    # Navigate to the password page and submit
    page.goto(f"https://{domain}/password", wait_until="load")
    pw_input = page.locator("input[type='password']")
    if pw_input.is_visible(timeout=5_000):
        pw_input.fill(SHOPIFY_STORE_PASSWORD)
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("load")


def _find_widget_launcher(page: Page, timeout: int = WIDGET_TIMEOUT) -> bool:
    """Check if the Agent Red widget launcher is visible on the page.

    The widget renders inside a closed Shadow DOM host element. We look
    for the host container or the launcher button that the widget creates.
    """
    # The widget creates a host div with id __agentred_host or similar
    # Also look for the SDK global and the launcher's circular button
    try:
        # The widget IIFE creates the launcher as a positioned fixed element.
        # Since it's in a Shadow DOM we can't query inside it, but we can
        # check for the host element's existence and the SDK global.
        result = page.evaluate("""() => {
            // Check 1: AgentRed SDK global exists
            if (!window.AgentRed) return { found: false, reason: 'no SDK global' };

            // Check 2: Find the shadow host element
            const hosts = document.querySelectorAll('[data-agentred-host]');
            if (hosts.length === 0) {
                // Try alternative selector — the widget creates a div with
                // specific styling (position:fixed, bottom/right)
                const fixed = Array.from(document.querySelectorAll('div'))
                    .filter(el => {
                        const s = getComputedStyle(el);
                        return s.position === 'fixed' && s.zIndex > '9000';
                    });
                if (fixed.length === 0) return { found: false, reason: 'no host element' };
            }
            return { found: true, reason: 'ok' };
        }""")
        return result.get("found", False)
    except Exception:
        return False


def _open_widget_panel(page: Page) -> bool:
    """Click the launcher to open the chat panel. Returns True if panel opened."""
    try:
        # Use the SDK to open the widget programmatically
        page.evaluate("window.AgentRed && window.AgentRed.open()")
        page.wait_for_timeout(1500)

        # The panel renders in an iframe. Check if it's visible.
        iframe = page.locator("iframe[data-agent-red-widget]")
        if iframe.is_visible(timeout=5_000):
            return True

        # Alternative: check via SDK
        is_open = page.evaluate(
            "window.AgentRed && window.AgentRed.isOpen()"
        )
        return bool(is_open)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Admin UI Widget Tests
# ---------------------------------------------------------------------------


@pytest.mark.timeout(120)
class TestAdminWidgetReadiness:
    """Verify the widget launcher and chat panel work in the standalone admin."""

    @pytest.fixture(autouse=True)
    def _setup_admin(self, page: Page):
        """Navigate to the admin SPA with auth."""
        if not LIVE_SPA_BASE_URL or not LIVE_API_KEY:
            pytest.skip("LIVE_SPA_BASE_URL or LIVE_API_KEY not set")

        page.add_init_script(f"""
            sessionStorage.setItem('agentred_api_key', '{LIVE_API_KEY}');
            sessionStorage.setItem('agentred-onboarding-dismissed', 'true');
        """)
        page.goto(
            f"{LIVE_SPA_BASE_URL}/?tenant={LIVE_TENANT_ID}",
            wait_until="load",
        )
        page.wait_for_timeout(3_000)  # Wait for activation status + widget injection
        _dismiss_onboarding_modal(page)
        self.page = page

    def test_widget_launcher_visible_in_admin(self):
        """The widget launcher (chat bubble) should be visible in the admin UI."""
        # Wait for the widget script to load and initialize
        self.page.wait_for_timeout(5_000)
        found = _find_widget_launcher(self.page)
        assert found, (
            "Widget launcher not visible in admin UI. "
            "Check: (1) activation status is_active=true, "
            "(2) widget_key present in config, "
            "(3) widget_key_hash set on tenant document, "
            "(4) no console errors on widget.js load."
        )

    def test_widget_chat_panel_opens_in_admin(self):
        """Clicking the launcher should open the chat panel."""
        self.page.wait_for_timeout(5_000)
        if not _find_widget_launcher(self.page):
            pytest.skip("Widget launcher not visible — cannot test panel open")

        opened = _open_widget_panel(self.page)
        assert opened, "Widget chat panel did not open in admin UI"


# ---------------------------------------------------------------------------
# Storefront Widget Tests
# ---------------------------------------------------------------------------


@pytest.mark.timeout(120)
class TestStorefrontWidgetReadiness:
    """Verify the widget is visible and functional on the Shopify storefront."""

    @pytest.fixture(autouse=True)
    def _setup_storefront(self, page: Page):
        """Navigate to the Shopify storefront, handling password gate."""
        self.page = page

        # First visit — check for password gate
        page.goto(f"https://{SHOPIFY_STORE_DOMAIN}/", wait_until="load")
        page.wait_for_timeout(2_000)

        # Detect password page
        if "/password" in page.url or page.locator("input[type='password']").is_visible(timeout=2_000):
            _bypass_shopify_password(page, SHOPIFY_STORE_DOMAIN)
            # Navigate to homepage after password
            page.goto(f"https://{SHOPIFY_STORE_DOMAIN}/", wait_until="load")

        page.wait_for_timeout(5_000)  # Wait for widget script to load

    def test_widget_launcher_visible_on_storefront(self):
        """The widget launcher should be visible on the Shopify storefront."""
        found = _find_widget_launcher(self.page)
        assert found, (
            f"Widget launcher not visible on {SHOPIFY_STORE_DOMAIN}. "
            "Check: (1) app embed is enabled in Shopify theme editor, "
            "(2) widget key is configured in the app embed settings, "
            "(3) widget.js is served by the API gateway."
        )

    def test_widget_chat_panel_opens_on_storefront(self):
        """Clicking the launcher should open the chat panel on the storefront."""
        if not _find_widget_launcher(self.page):
            pytest.skip("Widget launcher not visible — cannot test panel open")

        opened = _open_widget_panel(self.page)
        assert opened, "Widget chat panel did not open on storefront"

    def test_user_can_send_message_on_storefront(self):
        """A storefront user should be able to type and send a message."""
        if not _find_widget_launcher(self.page):
            pytest.skip("Widget launcher not visible")
        if not _open_widget_panel(self.page):
            pytest.skip("Widget panel did not open")

        # The panel is in an iframe — switch context
        iframe = self.page.frame_locator("iframe[data-agent-red-widget]")

        # Handle consent prompt if visible
        try:
            allow_btn = iframe.get_by_text("Allow", exact=True)
            if allow_btn.is_visible(timeout=3_000):
                allow_btn.click()
                self.page.wait_for_timeout(500)
        except Exception:
            pass

        # Type a message
        input_field = iframe.locator("textarea, input[type='text']").first
        input_field.wait_for(state="visible", timeout=10_000)
        input_field.fill("Hello, this is a readiness check.")

        # Click send button
        send_btn = iframe.locator("button[type='submit'], button[aria-label*='send' i]").first
        send_btn.click()

        # Verify the message appears in the conversation
        msg = iframe.get_by_text("Hello, this is a readiness check.")
        expect(msg).to_be_visible(timeout=5_000)

    def test_ai_response_received_on_storefront(self):
        """After sending a message, an AI response should appear."""
        if not _find_widget_launcher(self.page):
            pytest.skip("Widget launcher not visible")
        if not _open_widget_panel(self.page):
            pytest.skip("Widget panel did not open")

        iframe = self.page.frame_locator("iframe[data-agent-red-widget]")

        # Handle consent
        try:
            allow_btn = iframe.get_by_text("Allow", exact=True)
            if allow_btn.is_visible(timeout=2_000):
                allow_btn.click()
                self.page.wait_for_timeout(500)
        except Exception:
            pass

        # Send a message
        input_field = iframe.locator("textarea, input[type='text']").first
        input_field.wait_for(state="visible", timeout=10_000)
        input_field.fill("What products do you sell?")

        send_btn = iframe.locator("button[type='submit'], button[aria-label*='send' i]").first
        send_btn.click()

        # Wait for AI response — look for a message bubble that isn't ours
        # The AI response appears as a message with role="assistant" or
        # a different visual style. We wait up to 45s for the pipeline.
        self.page.wait_for_timeout(3_000)

        # Check for any text content that looks like an AI response
        # (longer than a short status message, not our original text)
        ai_responded = False
        for _ in range(9):  # 9 × 5s = 45s
            try:
                messages = iframe.locator("[data-role='assistant'], .agent-message, .assistant-message").all()
                for msg in messages:
                    text = msg.inner_text(timeout=2_000)
                    if len(text) > 20 and "readiness check" not in text.lower():
                        ai_responded = True
                        break
            except Exception:
                pass

            if ai_responded:
                break
            self.page.wait_for_timeout(5_000)

        assert ai_responded, (
            "No AI response received within 45 seconds. "
            "Check: (1) chat pipeline is healthy, "
            "(2) SSE connection is not blocked, "
            "(3) AI model is responding."
        )
