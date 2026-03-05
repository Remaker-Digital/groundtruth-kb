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

STAGING_FQDN = "https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"

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
    ("Agent configuration", "/configuration"),
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
    """
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

    # 3. Intercept activation status — mark tenant as activated
    def handle_activation_status(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "is_configured": True,
                "active_activated_at": "2026-01-01T00:00:00Z",
            }),
        )

    page.route("**/api/config/activation-status*", handle_activation_status)


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
    """2 s cooldown between test classes to avoid burst clustering."""
    yield
    time.sleep(2)


# ---------------------------------------------------------------------------
# Per-test page fixtures — mocked App Bridge context
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

    No mocks applied.  The layout detects missing shop domain and shows
    a Polaris Banner with error instructions.
    """
    page.add_init_script("""
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
