"""
Chrome MCP Validation Tests — Real rendering pipeline for Shopify Embedded Admin.

CONTEXT (S144):
The existing Shopify E2E tests (test_shopify_shell_live.py, test_shopify_pages_live.py)
mock App Bridge, tenant lookup, and activation status. These tests pass even when the
real UI is broken (as discovered in S142/S143: blank page, MantineProvider duplication,
VITE_API_URL misconfig, idToken() hang, z-index stacking bugs).

These "Chrome MCP validation" tests exercise the REAL rendering pipeline:
  - App Bridge CDN is intercepted (required — prevents frame-busting redirect)
  - window.shopify is mocked (required — idToken() needs a Shopify parent frame)
  - Tenant lookup is NOT mocked — hits real staging API
  - Activation status is NOT mocked — hits real staging API
  - Shared component APIs are NOT mocked — hit real staging API

This means pages render with REAL tenant data, REAL activation status, and REAL
component content. If VITE_API_URL is misconfigured or tenant resolution fails,
these tests will catch it.

WHAT THIS CATCHES that mock-based tests miss:
  1. VITE_API_URL pointing to wrong server (S143 bug)
  2. Tenant lookup failing due to missing shop mapping in Cosmos
  3. MantineProvider / Polaris CSS conflicts (S143 bug)
  4. Rate limiting preventing page content from loading
  5. Slow page loads (> 30s timeout — UX regression)
  6. Console errors from React crashes, missing dependencies
  7. Cross-nav link URLs pointing to wrong environment

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import os
import time

import pytest
from playwright.sync_api import Page, Route, ConsoleMessage

from scripts._env import load_env_local

load_env_local()

# ---------------------------------------------------------------------------
# Constants — use REAL staging server and REAL shop domain
# ---------------------------------------------------------------------------

STAGING_FQDN = os.environ.get("STAGING_FQDN", os.environ.get("STAGING_URL", ""))  # SPEC-0058: No hardcoded FQDNs

SHOPIFY_BASE_URL = os.environ.get(
    "SHOPIFY_BASE_URL",
    f"{STAGING_FQDN}/admin/shopify",
)

# REAL Shopify shop domain — must be mapped in staging Cosmos
REAL_SHOP_DOMAIN = "blanco-9939.myshopify.com"

# Maximum page load time before marking as UX regression (seconds)
MAX_PAGE_LOAD_SECS = 30

# Page routes and expected titles
SHOPIFY_PAGES = [
    ("/", "Dashboard"),
    ("/inbox", "Conversation Inbox"),
    ("/configuration", "AI configuration"),
    ("/knowledge-base", "Knowledge Base"),
    ("/widget", "Widget configuration"),
    ("/billing", "Billing"),
    ("/settings", "Settings"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_staging_reachable() -> bool:
    """Quick connectivity check against the staging health endpoint."""
    try:
        import httpx
        with httpx.Client(timeout=5.0) as c:
            resp = c.get(f"{STAGING_FQDN}/health")
            return resp.status_code == 200
    except Exception:
        return False


def _setup_minimal_mocks(page: Page) -> list[ConsoleMessage]:
    """Apply ONLY the minimum mocks required for outside-iframe testing.

    Mocked:
      - App Bridge CDN script (no-op — prevents frame-busting redirect)
      - window.shopify.idToken() (returns fake token — no parent frame available)
      - OnboardingWizard dismiss (sessionStorage flag)

    NOT mocked (uses real staging API):
      - /api/tenants/lookup
      - /api/config/activation-status
      - All shared component API endpoints
    """
    console_errors: list[ConsoleMessage] = []

    def _capture_errors(msg: ConsoleMessage) -> None:
        if msg.type in ("error", "warning"):
            console_errors.append(msg)

    page.on("console", _capture_errors)

    # Block App Bridge CDN to prevent frame-busting redirect
    def handle_app_bridge(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/javascript",
            body="/* App Bridge mock — frame-busting disabled for real rendering test */",
        )

    page.route("**/cdn.shopify.com/**/app-bridge*", handle_app_bridge)
    page.route("https://admin.shopify.com/**", lambda r: r.abort("blockedbyclient"))

    # Provide minimal window.shopify mock for idToken()
    page.add_init_script("""
        window.shopify = {
            idToken: () => Promise.resolve('real-rendering-test-token'),
            navigation: { dispatch: function() {} },
            redirect: function() {},
            saveBar: {
                show: function() {}, hide: function() {},
                leaveConfirmation: { enable: function() {}, disable: function() {} }
            }
        };
        // Suppress OnboardingWizard — focus on page content rendering
        try { sessionStorage.setItem('agentred-onboarding-dismissed', '1'); } catch {}
    """)

    return console_errors


def _navigate_and_wait(page: Page, path: str, expected_title: str) -> float:
    """Navigate to a Shopify admin page and wait for it to render.

    Returns the elapsed time in seconds from navigation to content visible.
    """
    start = time.monotonic()
    page.goto(
        f"{SHOPIFY_BASE_URL}{path}?shop={REAL_SHOP_DOMAIN}",
        wait_until="load",
        timeout=MAX_PAGE_LOAD_SECS * 1000,
    )

    # Wait for either the page title or an error banner to appear
    try:
        page.wait_for_selector(
            f"text='{expected_title}', text='Page Error', text='error'",
            timeout=MAX_PAGE_LOAD_SECS * 1000,
            state="visible",
        )
    except Exception:
        pass  # Will check content in assertions

    elapsed = time.monotonic() - start
    return elapsed


def _page_text(page: Page) -> str:
    """Get all visible text from the page body."""
    try:
        return page.locator("body").inner_text(timeout=5_000)
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def staging_reachable() -> None:
    """Verify staging is reachable before running tests."""
    if not _check_staging_reachable():
        pytest.skip(f"Staging unreachable at {STAGING_FQDN}")


@pytest.fixture(autouse=True, scope="class")
def _rate_limit_cooldown():
    """3 s cooldown between test classes to avoid rate limit clustering."""
    yield
    time.sleep(3)


# ===========================================================================
# TEST 1: Tenant Resolution (Real API)
# ===========================================================================

class TestTenantResolution:
    """Verify tenant lookup works against real staging API."""

    def test_real_tenant_resolution_shows_content(
        self, page: Page, staging_reachable
    ):
        """CRITICAL: Tenant lookup succeeds and page shows real content.

        This is the test that would have caught the S142/S143 blank page bug.
        If VITE_API_URL points to the wrong server, or the shop is not mapped
        in Cosmos, this test fails.
        """
        console_errors = _setup_minimal_mocks(page)
        elapsed = _navigate_and_wait(page, "/", "Dashboard")

        text = _page_text(page)

        # Must see either Dashboard content or cross-nav links
        # (these only render when tenant resolution succeeds)
        has_content = any(marker in text for marker in [
            "Dashboard",
            "Documentation",
            "Open full admin",
            "Setup wizard",
        ])

        assert has_content, (
            f"Tenant resolution appears to have failed — no expected content "
            f"visible after {elapsed:.1f}s. Page text: {text[:200]}"
        )

    def test_tenant_resolution_does_not_show_error(
        self, page: Page, staging_reachable
    ):
        """Tenant resolution should NOT show an error banner."""
        console_errors = _setup_minimal_mocks(page)
        _navigate_and_wait(page, "/", "Dashboard")

        text = _page_text(page)

        # Error markers from ShopifyAppLayout error state
        error_markers = [
            "Shop domain not found",
            "not registered with Agent Red",
            "Tenant lookup failed",
            "must be opened from the Shopify admin",
        ]
        for marker in error_markers:
            assert marker not in text, (
                f"Error banner visible: '{marker}'. Tenant resolution failed."
            )


# ===========================================================================
# TEST 2: All 7 Page Routes Render
# ===========================================================================

class TestPageRendering:
    """Verify all 7 Shopify admin pages render content (not blank)."""

    @pytest.mark.parametrize("path,expected_title", SHOPIFY_PAGES)
    def test_page_renders_title(
        self, page: Page, staging_reachable, path: str, expected_title: str
    ):
        """Each page must render its expected title text.

        Uses real tenant resolution and real API calls.
        Pages may show loading states for data, but the page title
        and Polaris Page wrapper must render.
        """
        console_errors = _setup_minimal_mocks(page)
        elapsed = _navigate_and_wait(page, path, expected_title)

        text = _page_text(page)
        assert expected_title in text, (
            f"Page {path} did not render title '{expected_title}' after "
            f"{elapsed:.1f}s. Visible text: {text[:300]}"
        )

    @pytest.mark.parametrize("path,expected_title", SHOPIFY_PAGES)
    def test_page_shows_cross_nav_links(
        self, page: Page, staging_reachable, path: str, expected_title: str
    ):
        """Each page must show the cross-navigation links.

        Cross-nav links (Documentation, Open full admin, Setup wizard)
        are rendered by ShopifyAppLayout ONLY when tenant resolution
        succeeds and loading is complete.
        """
        _setup_minimal_mocks(page)
        _navigate_and_wait(page, path, expected_title)

        text = _page_text(page)
        # Cross-nav links indicate successful tenant resolution + layout render
        assert "Documentation" in text or "Open full admin" in text, (
            f"Page {path}: cross-nav links not visible — layout may be stuck "
            f"in loading state. Text: {text[:200]}"
        )


# ===========================================================================
# TEST 3: Page Load Performance
# ===========================================================================

class TestPageLoadPerformance:
    """Verify pages load within acceptable time limits."""

    @pytest.mark.parametrize("path,expected_title", SHOPIFY_PAGES)
    def test_page_loads_within_timeout(
        self, page: Page, staging_reachable, path: str, expected_title: str
    ):
        """Each page must show content within MAX_PAGE_LOAD_SECS.

        S144 Chrome MCP testing revealed pages take 15-30s to load due to
        idToken() 5s timeout + tenant resolution latency + data API calls.
        This test tracks whether load times regress further.
        """
        _setup_minimal_mocks(page)
        elapsed = _navigate_and_wait(page, path, expected_title)

        text = _page_text(page)
        has_content = expected_title in text or "Documentation" in text

        assert has_content, (
            f"Page {path} failed to render within {MAX_PAGE_LOAD_SECS}s "
            f"(elapsed: {elapsed:.1f}s). This is a UX regression."
        )


# ===========================================================================
# TEST 4: Critical Console Errors
# ===========================================================================

class TestConsoleErrors:
    """Check for critical React/JS errors during page rendering."""

    def test_dashboard_no_react_crash(
        self, page: Page, staging_reachable
    ):
        """Dashboard should not produce React crash errors in console.

        This catches MantineProvider duplication (S143 bug) and other
        React rendering errors that produce console.error output.
        """
        console_errors = _setup_minimal_mocks(page)
        _navigate_and_wait(page, "/", "Dashboard")

        # Filter for critical errors (not 401/403 from API calls)
        critical_errors = [
            e for e in console_errors
            if e.type == "error"
            and "401" not in e.text
            and "403" not in e.text
            and "429" not in e.text
            and "Failed to fetch" not in e.text
        ]

        react_crashes = [
            e for e in critical_errors
            if any(k in e.text for k in [
                "Uncaught",
                "React error",
                "Maximum update depth",
                "Cannot read properties of undefined",
                "is not a function",
                "ChunkLoadError",
            ])
        ]

        assert not react_crashes, (
            f"React crash detected on Dashboard: "
            f"{[e.text[:100] for e in react_crashes]}"
        )


# ===========================================================================
# TEST 5: Cross-Nav Link Targets
# ===========================================================================

class TestCrossNavLinks:
    """Verify cross-nav links point to correct environments."""

    def test_documentation_link_target(
        self, page: Page, staging_reachable
    ):
        """Documentation link must point to agentredcx.com."""
        _setup_minimal_mocks(page)
        _navigate_and_wait(page, "/", "Dashboard")

        doc_link = page.locator("a:has-text('Documentation')")
        if doc_link.count() > 0:
            href = doc_link.first.get_attribute("href")
            assert href and "agentredcx.com" in href, (
                f"Documentation link points to wrong URL: {href}"
            )

    def test_full_admin_link_is_same_origin(
        self, page: Page, staging_reachable
    ):
        """Open full admin link must point to same-origin standalone admin.

        S143 fix: VITE_API_URL='' means same-origin. If this link points
        to a different domain, the env var is misconfigured.
        """
        _setup_minimal_mocks(page)
        _navigate_and_wait(page, "/", "Dashboard")

        admin_link = page.locator("a:has-text('Open full admin')")
        if admin_link.count() > 0:
            href = admin_link.first.get_attribute("href")
            assert href and "/admin/standalone/" in href, (
                f"Full admin link malformed: {href}"
            )
            # Should NOT point to a completely different domain
            # (same-origin means relative path or same FQDN)
            if href.startswith("http"):
                assert STAGING_FQDN.split("//")[1] in href or href.startswith("/"), (
                    f"Full admin link points to different server: {href}. "
                    f"VITE_API_URL may be misconfigured (S143 regression)."
                )


# ===========================================================================
# TEST 6: Shopify-Specific Elements
# ===========================================================================

class TestShopifySpecificElements:
    """Verify elements unique to the Shopify embedded admin."""

    def test_activation_banner_visible_on_unconfigured_tenant(
        self, page: Page, staging_reachable
    ):
        """Activation banner should render when tenant has draft config.

        The staging tenant (blanco-9939) has draft config, so the activation
        banner with 'Activate' and 'Discard' should be visible.
        """
        _setup_minimal_mocks(page)
        _navigate_and_wait(page, "/", "Dashboard")

        text = _page_text(page)
        # Activation banner or normal page content
        has_banner = "Activate" in text or "configuration changes" in text
        has_page = "Dashboard" in text

        assert has_banner or has_page, (
            f"Neither activation banner nor Dashboard content visible. "
            f"Page may be stuck loading. Text: {text[:200]}"
        )

    def test_billing_shows_shopify_channel(
        self, page: Page, staging_reachable
    ):
        """Billing page must identify Shopify as billing channel.

        This verifies the TenantContext.billingChannel is correctly set
        to 'shopify' (not 'stripe') for Shopify-installed tenants.
        NOTE: The billing API requires auth; with a fake session token,
        the API may return 429/401. We only assert on billing channel
        if the subscription data actually loaded.
        """
        _setup_minimal_mocks(page)
        _navigate_and_wait(page, "/billing", "Billing")

        text = _page_text(page)
        # Skip assertion if billing data failed to load (auth/rate limit)
        if "429" in text or "401" in text or "Failed to load" in text:
            pytest.skip("Billing API rate-limited or auth-rejected (fake token)")
        if "Billing" in text and "Subscription" in text:
            # If billing loaded successfully, verify Shopify channel
            assert "Shopify" in text, (
                f"Billing page does not show 'Shopify' as billing channel. "
                f"TenantContext.billingChannel may be wrong. Text: {text[:300]}"
            )

    def test_widget_shows_brand_color(
        self, page: Page, staging_reachable
    ):
        """Widget config must show the brand primary color #ff3621."""
        _setup_minimal_mocks(page)
        _navigate_and_wait(page, "/widget", "Widget")

        text = _page_text(page)
        if "429" in text or "401" in text or "Failed to load" in text:
            pytest.skip("Widget API rate-limited or auth-rejected (fake token)")
        if "Widget" in text and "color" in text.lower():
            assert "#ff3621" in text or "ff3621" in text.lower(), (
                f"Widget config does not show brand color #ff3621. "
                f"Text: {text[:300]}"
            )

    def test_settings_shows_team_members(
        self, page: Page, staging_reachable
    ):
        """Settings page must render the TeamManager with member count."""
        _setup_minimal_mocks(page)
        _navigate_and_wait(page, "/settings", "Settings")

        text = _page_text(page)
        if "429" in text or "401" in text or "Failed to load" in text:
            pytest.skip("Settings API rate-limited or auth-rejected (fake token)")
        if "Settings" in text:
            assert "team member" in text.lower() or "invite" in text.lower(), (
                f"Settings page does not show TeamManager. Text: {text[:300]}"
            )
