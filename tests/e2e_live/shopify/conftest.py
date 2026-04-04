"""
Live E2E test fixtures for the Shopify Embedded Admin against staging.

The Shopify Embedded Admin is the merchant-facing interface at /admin/shopify.
It uses Shopify Polaris + App Bridge and renders shared components (same as
standalone admin) wrapped in Polaris Page/Layout.

Architecture:
  - Auth: Shopify App Bridge session token (Bearer auth, NOT sessionStorage)
  - Navigation: App Bridge NavMenu API (NOT sidebar links in DOM)
  - Tenant resolution: /api/tenants/lookup?shop=xxx (unauthenticated fallback)
  - Shared components: same AnalyticsOverview, ConversationInbox, ConfigEditor,
    KnowledgeBaseManager, WidgetConfigurator, BillingPortal, TeamManager

Testing strategy:
  Since App Bridge is unavailable outside Shopify, we mock:
    1. window.shopify (idToken, navigation, redirect, saveBar)
    2. /api/tenants/lookup — returns a mock tenant
    3. /api/config/activation-status — marks tenant as activated
  Shared component API calls return 401 (invalid token) — components show
  error/loading states.  This is acceptable because shared component behavior
  is already tested by the standalone admin suite (576 tests).  These tests
  focus on Shopify-SPECIFIC shell elements: Polaris Frame, cross-nav links,
  page titles, GDPR section, error states, and routing.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import time

import pytest
from playwright.sync_api import Page, Route

# ---------------------------------------------------------------------------
# Auto-load .env.local
# ---------------------------------------------------------------------------
from scripts._env import load_env_local

load_env_local()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# SPEC-0058: No hardcoded FQDNs — all URLs from env vars.
STAGING_FQDN = os.environ.get("STAGING_FQDN", os.environ.get("STAGING_URL", ""))

SHOPIFY_BASE_URL = os.environ.get(
    "SHOPIFY_BASE_URL",
    f"{STAGING_FQDN}/admin/shopify",
)

PROD_URL = os.environ.get("PROD_URL", STAGING_FQDN)

# Mock shop domain — does not need to resolve to a real Shopify store.
# Tenant lookup is intercepted via Playwright route mock.
TEST_SHOP_DOMAIN = "test-store.myshopify.com"

# Navigation items (must match ShopifyAppLayout.tsx navItems array)
SHOPIFY_NAV_ITEMS = [
    ("Dashboard", "/"),
    ("Inbox", "/inbox"),
    ("AI configuration", "/configuration"),
    ("Knowledge Base", "/knowledge-base"),
    ("Widget configuration", "/widget"),
    ("Billing", "/billing"),
    ("Settings", "/settings"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_staging_reachable() -> bool:
    """Quick connectivity check against the staging health endpoint."""
    try:
        import httpx
        with httpx.Client(timeout=5.0) as c:
            resp = c.get(f"{PROD_URL}/health")
            return resp.status_code == 200
    except Exception:
        return False


def _main_text(page: Page) -> str:
    """Extract visible text from the main content area."""
    try:
        main = page.locator("main").first
        if main.count() > 0:
            return main.inner_text(timeout=5_000)
    except Exception:
        pass
    return page.locator("body").inner_text(timeout=5_000)


def _body_text(page: Page) -> str:
    """Extract visible text from the entire body."""
    return page.locator("body").inner_text(timeout=5_000)


def _setup_shopify_mocks(page: Page) -> None:
    """Inject App Bridge mock and API route interceptions.

    This must be called BEFORE page.goto() because add_init_script runs
    before any page JS executes, and route() intercepts network requests.

    Critical: The Shopify App Bridge CDN script (app-bridge.js) performs
    "frame-busting" — it detects non-iframe context via
    ``window.top !== window.self`` and redirects to admin.shopify.com
    BEFORE React renders.  We intercept this CDN script and replace it
    with a no-op so our ``window.shopify`` mock survives.
    """
    # 0. Intercept App Bridge CDN script — replace with no-op to prevent
    #    frame-busting redirect.  Our add_init_script mock below provides
    #    the window.shopify object that React/App Bridge hooks expect.
    def handle_app_bridge(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/javascript",
            body="/* App Bridge mock — frame-busting disabled for E2E */",
        )

    page.route("**/cdn.shopify.com/**/app-bridge*", handle_app_bridge)

    # Also block any redirect attempts to admin.shopify.com
    def block_shopify_redirect(route: Route) -> None:
        route.abort("blockedbyclient")

    page.route("https://admin.shopify.com/**", block_shopify_redirect)

    # 1. Mock window.shopify (App Bridge 4.x) — must exist before React renders
    page.add_init_script("""
        window.shopify = {
            idToken: () => Promise.resolve('test-e2e-session-token'),
            navigation: {
                dispatch: function() {}
            },
            redirect: function(url) {
                console.log('[E2E Mock] Redirect:', url);
            },
            saveBar: {
                show: function() {},
                hide: function() {},
                leaveConfirmation: {
                    enable: function() {},
                    disable: function() {}
                }
            }
        };
        // Suppress OnboardingWizard auto-open
        try { sessionStorage.setItem('agentred-onboarding-dismissed', '1'); } catch {}
    """)

    # 2. Intercept tenant lookup — return a mock tenant
    def handle_tenant_lookup(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "found": True,
                "tenant_id": "staging-001",
                "tier": "starter",
                "status": "active",
            }),
        )

    page.route("**/api/tenants/lookup*", handle_tenant_lookup)

    # 3. Intercept activation status — mark tenant as activated.
    #    Must include is_active: true (SPA widget injection depends on it)
    #    and all fields the layout polls for status display.
    def handle_activation_status(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "has_pending_changes": False,
                "active_version": 1,
                "active_activated_at": "2026-01-01T00:00:00Z",
                "draft_version": None,
                "is_configured": True,
                "is_active": True,
                "can_activate": False,
            }),
        )

    page.route("**/api/config/activation-status*", handle_activation_status)

    # 4. Intercept /api/config — return a minimal valid config.
    #    Without this, the SPA's Bearer token auth fails (401) and triggers
    #    window.location.reload() → infinite reload loop → empty page.
    def handle_config(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "tenant_id": "staging-001",
                "tier": "starter",
                "version": 1,
                "config": {
                    "brand_name": "Test Store",
                    "brand_voice": "friendly",
                    "widget_primary_color": "#ff3621",
                    "widget_position": "bottom-right",
                    "widget_key": "pk_live_mock_test_key_for_e2e",
                },
                "state": "active",
            }),
        )

    page.route("**/api/config?*", handle_config)
    page.route("**/api/config", handle_config)

    # 5. Intercept remaining /api/admin/* calls — return empty-but-valid
    #    responses to prevent 401→reload cycle.  Shared components show
    #    empty/loading states which is acceptable (component behavior is
    #    tested by the standalone admin suite).
    def handle_admin_api(route: Route) -> None:
        url = route.request.url
        # Return appropriate empty structures based on endpoint pattern
        if "/conversations" in url:
            body = {"conversations": [], "total": 0}
        elif "/team" in url and "/whoami" in url:
            body = {"role": "superadmin", "email": "test@example.com"}
        elif "/team" in url:
            body = {"members": []}
        elif "/quality" in url:
            body = {"score": 0, "factors": []}
        elif "/quick-actions" in url:
            body = {"actions": []}
        elif "/knowledge" in url:
            body = {"sources": [], "total": 0}
        else:
            body = {}
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(body),
        )

    page.route("**/api/admin/**", handle_admin_api)


def _create_shopify_page(page: Page, path: str = "/") -> Page:
    """Set up mocks and navigate to a Shopify admin path.

    Args:
        page: Playwright Page instance.
        path: Route path within the Shopify admin (e.g. "/inbox").

    Returns:
        Page with mocks applied and navigated to the specified route.
    """
    _setup_shopify_mocks(page)
    page.goto(
        f"{SHOPIFY_BASE_URL}{path}?shop={TEST_SHOP_DOMAIN}",
        wait_until="load",
    )
    # Wait for React + Polaris to render
    page.wait_for_timeout(3_000)
    return page


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def staging_reachable() -> None:
    """Verify staging is reachable before running Shopify admin tests."""
    if not _check_staging_reachable():
        pytest.skip(f"Staging unreachable at {PROD_URL} — skipping Shopify E2E tests")


# ---------------------------------------------------------------------------
# Class-scoped rate limit cooldown
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True, scope="class")
def _rate_limit_cooldown():
    """0.5 s cooldown between test classes.  (S164: reduced from 2 s.)"""
    yield
    time.sleep(0.5)


# ---------------------------------------------------------------------------
# Class-scoped shared fixtures (S164 -- page reuse across read-only tests)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="class")
def shared_browser_context(browser):
    """Class-scoped BrowserContext for Shopify admin tests."""
    ctx = browser.new_context()
    yield ctx
    ctx.close()


def _setup_shared_shopify_page(context, page, path="/"):
    """Set up mocks on a class-scoped BrowserContext and navigate."""
    # Intercept App Bridge CDN
    def handle_app_bridge(route):
        route.fulfill(status=200, content_type="application/javascript",
                      body="/* App Bridge mock */")
    page.route("**/cdn.shopify.com/**/app-bridge*", handle_app_bridge)
    page.route("https://admin.shopify.com/**", lambda r: r.abort("blockedbyclient"))

    # Mock window.shopify via context-level init script
    context.add_init_script("""
        window.shopify = {
            idToken: () => Promise.resolve('test-e2e-session-token'),
            navigation: { dispatch: function() {} },
            redirect: function() {},
            saveBar: { show: function() {}, hide: function() {},
                leaveConfirmation: { enable: function() {}, disable: function() {} } }
        };
        try { sessionStorage.setItem('agentred-onboarding-dismissed', '1'); } catch {}
    """)

    # Intercept tenant lookup + activation status
    import json as _json
    def handle_tenant_lookup(route):
        route.fulfill(status=200, content_type="application/json",
                      body=_json.dumps({"found": True, "tenant_id": "staging-001",
                                        "tier": "starter", "status": "active"}))
    page.route("**/api/tenants/lookup*", handle_tenant_lookup)

    def handle_activation_status(route):
        route.fulfill(status=200, content_type="application/json",
                      body=_json.dumps({
                          "has_pending_changes": False, "active_version": 1,
                          "active_activated_at": "2026-01-01T00:00:00Z",
                          "draft_version": None, "is_configured": True,
                          "is_active": True, "can_activate": False,
                      }))
    page.route("**/api/config/activation-status*", handle_activation_status)

    # Mock /api/config to prevent 401→reload cycle (Bearer token is fake)
    def handle_config(route):
        route.fulfill(status=200, content_type="application/json",
                      body=_json.dumps({
                          "tenant_id": "staging-001", "tier": "starter", "version": 1,
                          "config": {"brand_name": "Test Store", "brand_voice": "friendly",
                                     "widget_primary_color": "#ff3621",
                                     "widget_key": "pk_live_mock_test_key_for_e2e"},
                          "state": "active",
                      }))
    page.route("**/api/config?*", handle_config)
    page.route("**/api/config", handle_config)

    # Mock /api/admin/* to prevent 401→reload cycle
    def handle_admin_api(route):
        url = route.request.url
        if "/conversations" in url:
            body = {"conversations": [], "total": 0}
        elif "/team" in url and "/whoami" in url:
            body = {"role": "superadmin", "email": "test@example.com"}
        elif "/team" in url:
            body = {"members": []}
        elif "/quality" in url:
            body = {"score": 0, "factors": []}
        elif "/quick-actions" in url:
            body = {"actions": []}
        elif "/knowledge" in url:
            body = {"sources": [], "total": 0}
        else:
            body = {}
        route.fulfill(status=200, content_type="application/json",
                      body=_json.dumps(body))
    page.route("**/api/admin/**", handle_admin_api)

    page.goto(f"{SHOPIFY_BASE_URL}{path}?shop={TEST_SHOP_DOMAIN}", wait_until="load")
    page.wait_for_timeout(3_000)
    return page


@pytest.fixture(scope="class")
def shared_shopify_page(shared_browser_context, staging_reachable) -> Page:
    """Class-scoped Shopify admin shell with mocked App Bridge."""
    page = shared_browser_context.new_page()
    _setup_shared_shopify_page(shared_browser_context, page, "/")
    yield page
    page.close()


@pytest.fixture(scope="class")
def shared_shopify_dashboard(shared_browser_context, staging_reachable) -> Page:
    """Class-scoped Shopify Dashboard."""
    page = shared_browser_context.new_page()
    _setup_shared_shopify_page(shared_browser_context, page, "/")
    yield page
    page.close()


@pytest.fixture(scope="class")
def shared_shopify_inbox(shared_browser_context, staging_reachable) -> Page:
    """Class-scoped Shopify Inbox."""
    page = shared_browser_context.new_page()
    _setup_shared_shopify_page(shared_browser_context, page, "/inbox")
    yield page
    page.close()


@pytest.fixture(scope="class")
def shared_shopify_configuration(shared_browser_context, staging_reachable) -> Page:
    """Class-scoped Shopify Configuration."""
    page = shared_browser_context.new_page()
    _setup_shared_shopify_page(shared_browser_context, page, "/configuration")
    yield page
    page.close()


@pytest.fixture(scope="class")
def shared_shopify_knowledge_base(shared_browser_context, staging_reachable) -> Page:
    """Class-scoped Shopify Knowledge Base."""
    page = shared_browser_context.new_page()
    _setup_shared_shopify_page(shared_browser_context, page, "/knowledge-base")
    yield page
    page.close()


@pytest.fixture(scope="class")
def shared_shopify_widget(shared_browser_context, staging_reachable) -> Page:
    """Class-scoped Shopify Widget Configuration."""
    page = shared_browser_context.new_page()
    _setup_shared_shopify_page(shared_browser_context, page, "/widget")
    yield page
    page.close()


@pytest.fixture(scope="class")
def shared_shopify_billing(shared_browser_context, staging_reachable) -> Page:
    """Class-scoped Shopify Billing."""
    page = shared_browser_context.new_page()
    _setup_shared_shopify_page(shared_browser_context, page, "/billing")
    yield page
    page.close()


@pytest.fixture(scope="class")
def shared_shopify_settings(shared_browser_context, staging_reachable) -> Page:
    """Class-scoped Shopify Settings."""
    page = shared_browser_context.new_page()
    _setup_shared_shopify_page(shared_browser_context, page, "/settings")
    yield page
    page.close()


# ---------------------------------------------------------------------------
# Per-test page fixtures (for mutation test classes)
# ---------------------------------------------------------------------------

@pytest.fixture()
def live_shopify_page(page: Page, staging_reachable) -> Page:
    """Navigate to the Shopify admin shell with mocked App Bridge.

    App Bridge, tenant lookup, and activation status are mocked.
    Shared component API calls will get 401 (invalid session token) —
    components show error/loading states.  The SHELL (Polaris Frame,
    cross-nav links, page titles) renders correctly.
    """
    return _create_shopify_page(page, "/")


@pytest.fixture()
def live_shopify_error_page(page: Page, staging_reachable) -> Page:
    """Navigate to the Shopify admin WITHOUT shop param — triggers error state.

    App Bridge CDN is still intercepted (no-op) to prevent frame-busting
    redirect, but tenant lookup and activation status are NOT mocked.
    The layout detects missing shop domain and shows a Polaris Banner
    with error instructions.
    """
    # Block App Bridge CDN to prevent redirect
    def handle_app_bridge(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/javascript",
            body="/* App Bridge mock — frame-busting disabled for E2E */",
        )

    page.route("**/cdn.shopify.com/**/app-bridge*", handle_app_bridge)
    page.route("https://admin.shopify.com/**", lambda r: r.abort("blockedbyclient"))

    page.add_init_script("""
        window.shopify = {
            idToken: () => Promise.resolve('test-e2e-session-token'),
            navigation: { dispatch: function() {} },
            redirect: function() {},
            saveBar: { show: function() {}, hide: function() {},
                leaveConfirmation: { enable: function() {}, disable: function() {} } }
        };
        try { sessionStorage.setItem('agentred-onboarding-dismissed', '1'); } catch {}
    """)
    page.goto(f"{SHOPIFY_BASE_URL}/", wait_until="load")
    page.wait_for_timeout(3_000)
    return page


# ---------------------------------------------------------------------------
# Page-specific fixtures (each navigates to a specific route)
# ---------------------------------------------------------------------------

@pytest.fixture()
def live_shopify_dashboard(page: Page, staging_reachable) -> Page:
    """Shopify admin — Dashboard page (landing)."""
    return _create_shopify_page(page, "/")


@pytest.fixture()
def live_shopify_inbox(page: Page, staging_reachable) -> Page:
    """Shopify admin — Inbox page."""
    return _create_shopify_page(page, "/inbox")


@pytest.fixture()
def live_shopify_configuration(page: Page, staging_reachable) -> Page:
    """Shopify admin — Agent Configuration page."""
    return _create_shopify_page(page, "/configuration")


@pytest.fixture()
def live_shopify_knowledge_base(page: Page, staging_reachable) -> Page:
    """Shopify admin — Knowledge Base page."""
    return _create_shopify_page(page, "/knowledge-base")


@pytest.fixture()
def live_shopify_widget(page: Page, staging_reachable) -> Page:
    """Shopify admin — Widget Configuration page."""
    return _create_shopify_page(page, "/widget")


@pytest.fixture()
def live_shopify_billing(page: Page, staging_reachable) -> Page:
    """Shopify admin — Billing & Usage page."""
    return _create_shopify_page(page, "/billing")


@pytest.fixture()
def live_shopify_settings(page: Page, staging_reachable) -> Page:
    """Shopify admin — Settings page."""
    return _create_shopify_page(page, "/settings")
