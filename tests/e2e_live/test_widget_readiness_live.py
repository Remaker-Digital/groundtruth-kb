"""
Live E2E tests for post-deploy widget readiness.

Verifies the widget is visible and functional in both the standalone
admin UI and the connected Shopify storefront. These are the browser-
based checks that cannot be done from a Python script (complement to
Phase-C checks C.36–C.41 in upgrade_verification.py).

CRITICAL INVARIANT (S257):
  If the configuration is Active, the widget launcher MUST be visible
  on both the Shopify storefront and the standalone admin UI.  A deployment
  that passes API checks but leaves the widget invisible is a failed
  deployment.  This file encodes that gate as browser-verified assertions.

Checks:
  0. Active config → widget key auth works (hash present on tenant doc)
  1. Active config → widget launcher visible in standalone admin UI
  2. Widget chat panel opens in admin UI
  3. Active config → widget launcher visible on Shopify storefront
  4. Widget chat panel opens on storefront
  5. User can type and send a message on storefront
  6. AI response appears in the conversation

Run:
    pytest tests/e2e_live/test_widget_readiness_live.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import os

import httpx
import pytest
from playwright.sync_api import Page, expect

from tests.e2e_live.conftest import (
    LIVE_API_KEY,
    LIVE_SPA_BASE_URL,
    LIVE_TENANT_ID,
    STAGING_FQDN,
    _dismiss_onboarding_modal,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# SPEC-0058: No hardcoded FQDNs — all URLs from env vars.
# Shopify domain and password are environment-specific.  The test pipeline
# sets these via _get_env_vars() or the runner exports them before launch.
SHOPIFY_STORE_DOMAIN = os.environ.get("SHOPIFY_STORE_DOMAIN", "")
SHOPIFY_STORE_PASSWORD = os.environ.get("SHOPIFY_STORE_PASSWORD", "")

# Gateway FQDN — resolved from the same env vars the rest of the live
# suite uses.  No hardcoded fallback to avoid staging/production confusion.
API_GATEWAY_FQDN = os.environ.get(
    "API_GATEWAY_FQDN",
    os.environ.get("CONTAINER_APP_FQDN", ""),
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

    The widget renders inside a closed Shadow DOM host element.  The
    shadow root is opaque to querySelectorAll, so we check:
      1. window.AgentRed SDK global exists (proves widget.js executed)
      2. #agent-red-widget host div exists with display:block
         (proves mountLauncherHost() created the shadow host)
      3. Fallback: any fixed-position div with high z-index
    """
    try:
        result = page.evaluate("""() => {
            // Check 1: AgentRed SDK global exists (widget.js ran init() to completion)
            if (!window.AgentRed) return { found: false, reason: 'no SDK global' };

            // Check 2: Find the shadow host element by its actual ID.
            // widget/src/index.ts mountLauncherHost() creates:
            //   div#agent-red-widget { display: block }
            // with a closed Shadow DOM containing the Preact Launcher.
            const host = document.getElementById('agent-red-widget');
            if (host && host.style.display !== 'none') {
                return { found: true, reason: 'host #agent-red-widget visible' };
            }

            // Check 3: Fallback — find any div with position:fixed + high z-index
            // (handles future host-ID changes or alternative widget configurations)
            const fixed = Array.from(document.querySelectorAll('div'))
                .filter(el => {
                    const s = getComputedStyle(el);
                    return s.position === 'fixed' && parseInt(s.zIndex, 10) > 9000;
                });
            if (fixed.length > 0) {
                return { found: true, reason: 'fixed-position launcher found' };
            }

            return { found: false, reason: 'no host element' };
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
# S257 Invariant: Active Config → Widget Visible
# ---------------------------------------------------------------------------


@pytest.mark.timeout(60)
class TestActiveConfigImpliesWidgetVisible:
    """CRITICAL GATE: If the configuration is Active, the widget MUST be visible.

    This test class verifies the prerequisite chain that makes widget
    visibility possible.  Each test targets a specific link in the chain
    so failures are immediately diagnosable:

      1. activation-status → is_active == true
      2. widget_key present in the active config
      3. widget_key_hash present on the tenant document (widget key auth
         returns 200, not 401 — the S254 CMK incident left hashes missing)

    If any of these fail, the widget launcher will be invisible regardless
    of whether the admin UI or storefront embed is correct.
    """

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Resolve the base URL for API calls."""
        self.base_url = STAGING_FQDN
        if not self.base_url:
            pytest.skip("STAGING_FQDN / STAGING_URL not set")
        if not LIVE_API_KEY:
            pytest.skip("LIVE_API_KEY not set")

    def test_activation_status_is_active(self):
        """The tenant configuration must report is_active=true."""
        with httpx.Client(timeout=30.0) as c:
            resp = c.get(
                f"{self.base_url}/api/config/activation-status"
                f"?tenant={LIVE_TENANT_ID}",
                headers={"X-API-Key": LIVE_API_KEY},
            )
        assert resp.status_code == 200, (
            f"activation-status returned HTTP {resp.status_code}"
        )
        data = resp.json()
        assert data.get("is_active") is True, (
            f"Configuration is NOT active: {data}. "
            "The widget will not be injected in the admin console."
        )

    def test_widget_key_present_in_config(self):
        """The active config must contain a non-empty widget_key."""
        with httpx.Client(timeout=30.0) as c:
            resp = c.get(
                f"{self.base_url}/api/config?page_type=all"
                f"&tenant={LIVE_TENANT_ID}",
                headers={"X-API-Key": LIVE_API_KEY},
            )
        assert resp.status_code == 200, (
            f"/api/config returned HTTP {resp.status_code}"
        )
        config = resp.json().get("config", {})
        widget_key = config.get("widget_key", "")
        assert widget_key and widget_key.startswith("pk_live_"), (
            f"widget_key is missing or invalid: '{widget_key[:20]}...'. "
            "The widget embed code has no key to authenticate with."
        )

    def test_widget_key_auth_works(self):
        """Widget key auth must return 200 — proves widget_key_hash exists.

        This is the exact check that would have caught the S254 defect:
        the hash was missing from the Cosmos tenant document, so widget
        key auth returned 401 even though the key was correct and the
        config was Active.
        """
        # First fetch the widget key from the admin config endpoint
        with httpx.Client(timeout=30.0) as c:
            admin_resp = c.get(
                f"{self.base_url}/api/config?page_type=all"
                f"&tenant={LIVE_TENANT_ID}",
                headers={"X-API-Key": LIVE_API_KEY},
            )
        if admin_resp.status_code != 200:
            pytest.skip("Could not fetch admin config to get widget key")

        config = admin_resp.json().get("config", {})
        widget_key = config.get("widget_key", "")
        if not widget_key:
            pytest.skip("No widget key in config")

        # Now test widget key auth directly — this is what the embedded
        # widget does when it loads on the storefront or admin console
        with httpx.Client(timeout=30.0) as c:
            widget_resp = c.get(
                f"{self.base_url}/api/config?page_type=index",
                headers={"X-Widget-Key": widget_key},
            )
        assert widget_resp.status_code == 200, (
            f"Widget key auth returned HTTP {widget_resp.status_code}. "
            f"This means widget_key_hash is MISSING or STALE on the "
            f"tenant document for {LIVE_TENANT_ID}. The widget launcher "
            f"will be invisible because its config fetch is rejected by "
            f"the auth middleware before reaching the config handler. "
            f"Fix: trigger config activation or run repair_widget_hash.py."
        )


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
        page.wait_for_timeout(5_000)  # Wait for activation status + widget injection
        _dismiss_onboarding_modal(page)
        self.page = page

    def test_widget_launcher_visible_in_admin(self):
        """CRITICAL GATE: Active config → widget launcher MUST be visible in admin.

        S257: This is the browser-verified assertion that the widget
        launcher renders in the standalone admin UI.  It is NOT sufficient
        to check API responses alone — the launcher must be a visible DOM
        element that a human user can see and click.
        """
        # Wait budget: activation-status poll (~3s) + widget injection + possible
        # 4s retry (self-heal race condition) + Preact render.  Total ~15s.
        self.page.wait_for_timeout(15_000)
        found = _find_widget_launcher(self.page)
        assert found, (
            "Widget launcher not visible in admin UI. "
            "Check: (1) activation status is_active=true, "
            "(2) widget_key present in config, "
            "(3) widget_key_hash set on tenant document, "
            "(4) no console errors on widget.js load. "
            "This is a CRITICAL deployment gate — the widget must be "
            "visible when the configuration is Active."
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
        if not SHOPIFY_STORE_DOMAIN:
            pytest.skip(
                "SHOPIFY_STORE_DOMAIN not set — storefront tests require an "
                "env-configured domain (no hardcoded fallback per SPEC-0058)"
            )

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
        """CRITICAL GATE: Active config → widget launcher MUST be visible on storefront.

        S257: This is the browser-verified assertion that the widget
        launcher renders on the Shopify storefront.  A deployment is NOT
        successful if this test fails.
        """
        found = _find_widget_launcher(self.page)
        assert found, (
            f"Widget launcher not visible on {SHOPIFY_STORE_DOMAIN}. "
            "Check: (1) app embed is enabled in Shopify theme editor, "
            "(2) widget key is configured in the app embed settings, "
            "(3) widget.js is served by the API gateway, "
            "(4) widget_key_hash exists on the tenant document. "
            "This is a CRITICAL deployment gate — the widget must be "
            "visible when the configuration is Active."
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
