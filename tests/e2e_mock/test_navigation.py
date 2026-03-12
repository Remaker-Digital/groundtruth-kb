# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1706 Navigation E2E tests -- routing, query param preservation, deep links, sidebar active state.

Tests cross-page navigation against the mock Vite dev server (npm run dev:mock).
Verifies React Router integration, useQueryPreservingNavigate hook (SPEC-1654),
deep link resolution, and Mantine NavLink active state indicator.

Routes under test (BrowserRouter basename=/admin/standalone/):
  /              -> Dashboard
  /inbox         -> Inbox
  /team          -> Team members
  /configuration -> Agent configuration
  /knowledge-base-> Knowledge base
  /quick-actions -> Quick actions
  /widget        -> Widget configuration
  /billing       -> Account and billing
  /memory-privacy-> Memory & privacy
  /integrations  -> Integrations
  /analytics     -> Redirects to / (Dashboard)
  /*             -> Catch-all redirects to /
"""

import pytest
from playwright.sync_api import Page

from tests.e2e_mock.conftest import (
    MOCK_TENANT,
    dismiss_onboarding_if_present,
    main_text,
    navigate_and_settle,
    navigate_to,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_AUTH_INIT_SCRIPT = (
    "sessionStorage.setItem('agentred_api_key', 'ar_mock_key_for_e2e_navigation');"
    "sessionStorage.setItem('agentred-onboarding-dismissed', 'true');"
)


def _inject_auth_and_go(page: Page, mock_base_url: str, path: str = "/"):
    """Inject mock auth into sessionStorage, then navigate with tenant param."""
    page.add_init_script(_AUTH_INIT_SCRIPT)
    navigate_and_settle(page, path, mock_base_url)
    dismiss_onboarding_if_present(page)


def _has_tenant_param(page: Page) -> bool:
    """Check that a tenant query param is present in the current URL.
    The SPA may rewrite the tenant param to a slug (e.g., mock-store)."""
    return f"tenant={MOCK_TENANT}" in page.url or "tenant=mock-store" in page.url


def _click_sidebar_link(page: Page, label: str):
    """Click a sidebar NavLink by its visible label text."""
    sidebar = page.locator(".mantine-AppShell-navbar")
    link = sidebar.locator(f"text={label}").first
    link.click()
    page.wait_for_timeout(500)


def _get_active_nav_labels(page: Page) -> list[str]:
    """Return the text of all sidebar NavLinks that have data-active attribute."""
    sidebar = page.locator(".mantine-AppShell-navbar")
    active_links = sidebar.locator("[data-active='true'], [data-active]")
    count = active_links.count()
    labels = []
    for i in range(count):
        text = active_links.nth(i).inner_text().strip()
        if text:
            labels.append(text)
    return labels


def _page_has_heading(page: Page, expected: str) -> bool:
    """Check whether the page contains the expected heading text in main content."""
    content = main_text(page)
    return expected in content


# ---------------------------------------------------------------------------
# Test Class 1: Routing
# ---------------------------------------------------------------------------

class TestRouting:
    """Verify each admin route resolves to the correct page content."""

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, mock_base_url: str):
        self._page = page
        self._url = mock_base_url
        page.add_init_script(_AUTH_INIT_SCRIPT)

    def test_dashboard_route(self):
        """/ resolves to the Dashboard page."""
        navigate_and_settle(self._page, "/", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Dashboard")

    def test_inbox_route(self):
        """/inbox renders the Inbox page with conversation UI."""
        navigate_and_settle(self._page, "/inbox", self._url)
        dismiss_onboarding_if_present(self._page)
        text = main_text(self._page)
        assert "conversation" in text.lower() or "Inbox" in text

    def test_team_route(self):
        """/team renders the Team members page."""
        navigate_and_settle(self._page, "/team", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Team members")

    def test_configuration_route(self):
        """/configuration renders the Agent configuration page."""
        navigate_and_settle(self._page, "/configuration", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Agent configuration")

    def test_knowledge_base_route(self):
        """/knowledge-base renders the Knowledge base page."""
        navigate_and_settle(self._page, "/knowledge-base", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Knowledge base")

    def test_widget_route(self):
        """/widget renders the Widget configuration page."""
        navigate_and_settle(self._page, "/widget", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Widget configuration")

    def test_billing_route(self):
        """/billing renders the Account and billing page."""
        navigate_and_settle(self._page, "/billing", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Account and billing")

    def test_quick_actions_route(self):
        """/quick-actions renders the Quick actions page."""
        navigate_and_settle(self._page, "/quick-actions", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Quick actions")

    def test_memory_privacy_route(self):
        """/memory-privacy renders the Memory & privacy page."""
        navigate_and_settle(self._page, "/memory-privacy", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Memory")

    def test_integrations_route(self):
        """/integrations renders the Integrations page."""
        navigate_and_settle(self._page, "/integrations", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Integrations")

    def test_default_route_shows_dashboard(self):
        """Navigating to the base path / shows the Dashboard."""
        navigate_and_settle(self._page, "/", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Dashboard")

    def test_analytics_redirects_to_dashboard(self):
        """/analytics redirects to / (Dashboard) via NavigateWithQuery."""
        navigate_and_settle(self._page, "/analytics", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Dashboard")
        assert "/analytics" not in self._page.url

    def test_unknown_route_redirects_to_dashboard(self):
        """An unknown route (catch-all *) redirects to Dashboard."""
        navigate_and_settle(self._page, "/nonexistent-page-xyz", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Dashboard")


# ---------------------------------------------------------------------------
# Test Class 2: Query Param Preservation (SPEC-1654)
# ---------------------------------------------------------------------------

class TestQueryParamPreservation:
    """Verify ?tenant= param is preserved across all navigation types."""

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, mock_base_url: str):
        self._page = page
        self._url = mock_base_url
        _inject_auth_and_go(page, mock_base_url, "/")

    def test_tenant_param_present_on_initial_load(self):
        """Initial navigation includes ?tenant= in the URL."""
        assert _has_tenant_param(self._page), (
            f"Expected tenant={MOCK_TENANT} in URL: {self._page.url}"
        )

    def test_sidebar_click_preserves_tenant_param(self):
        """Clicking a sidebar link preserves ?tenant= via useQueryPreservingNavigate."""
        _click_sidebar_link(self._page, "Inbox")
        assert _has_tenant_param(self._page), (
            f"Tenant param lost after sidebar click to Inbox: {self._page.url}"
        )

    def test_multiple_navigations_preserve_tenant_param(self):
        """Navigating through multiple pages in sequence preserves ?tenant= throughout."""
        for label in ["Inbox", "Team members", "Dashboard"]:
            _click_sidebar_link(self._page, label)
            assert _has_tenant_param(self._page), (
                f"Tenant param lost after navigating to {label}: {self._page.url}"
            )

    def test_direct_url_navigation_maintains_tenant_param(self):
        """Direct URL navigation with ?tenant= keeps the param."""
        navigate_and_settle(self._page, "/team", self._url)
        assert _has_tenant_param(self._page), (
            f"Tenant param lost on direct navigation to /team: {self._page.url}"
        )

    def test_browser_back_preserves_tenant_param(self):
        """Browser back button preserves ?tenant= param."""
        _click_sidebar_link(self._page, "Inbox")
        assert _has_tenant_param(self._page)
        _click_sidebar_link(self._page, "Team members")
        assert _has_tenant_param(self._page)
        self._page.go_back()
        self._page.wait_for_timeout(500)
        assert _has_tenant_param(self._page), (
            f"Tenant param lost after browser back: {self._page.url}"
        )

    def test_analytics_redirect_preserves_tenant_param(self):
        """/analytics redirect to Dashboard preserves ?tenant= param."""
        navigate_and_settle(self._page, "/analytics", self._url)
        assert _has_tenant_param(self._page), (
            f"Tenant param lost after /analytics redirect: {self._page.url}"
        )


# ---------------------------------------------------------------------------
# Test Class 3: Deep Links
# ---------------------------------------------------------------------------

class TestDeepLinks:
    """Verify direct URL access to specific pages loads the correct content."""

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, mock_base_url: str):
        self._page = page
        self._url = mock_base_url
        page.add_init_script(_AUTH_INIT_SCRIPT)

    def test_deep_link_inbox(self):
        """Direct URL to /inbox loads the inbox page with conversation UI."""
        navigate_and_settle(self._page, "/inbox", self._url)
        dismiss_onboarding_if_present(self._page)
        text = main_text(self._page)
        assert "conversation" in text.lower(), (
            f"Inbox deep link did not render conversation UI. Page text: {text[:200]}"
        )
        assert _has_tenant_param(self._page)

    def test_deep_link_team(self):
        """Direct URL to /team loads the Team members page."""
        navigate_and_settle(self._page, "/team", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Team members")
        assert _has_tenant_param(self._page)

    def test_deep_link_configuration(self):
        """Direct URL to /configuration loads the Agent configuration page."""
        navigate_and_settle(self._page, "/configuration", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Agent configuration")
        assert _has_tenant_param(self._page)

    def test_deep_link_knowledge_base(self):
        """Direct URL to /knowledge-base loads the Knowledge base page."""
        navigate_and_settle(self._page, "/knowledge-base", self._url)
        dismiss_onboarding_if_present(self._page)
        assert _page_has_heading(self._page, "Knowledge base")
        assert _has_tenant_param(self._page)


# ---------------------------------------------------------------------------
# Test Class 4: Sidebar Active State
# ---------------------------------------------------------------------------

class TestSidebarActiveState:
    """Verify the sidebar NavLink active indicator tracks the current route."""

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, mock_base_url: str):
        self._page = page
        self._url = mock_base_url
        _inject_auth_and_go(page, mock_base_url, "/")

    def test_dashboard_active_on_initial_load(self):
        """Dashboard nav item has data-active attribute when on / route."""
        active = _get_active_nav_labels(self._page)
        assert any("Dashboard" in label for label in active), (
            f"Expected Dashboard to be active, got: {active}"
        )

    def test_active_state_changes_on_navigation(self):
        """Clicking Inbox moves the active indicator from Dashboard to Inbox."""
        _click_sidebar_link(self._page, "Inbox")
        active = _get_active_nav_labels(self._page)
        assert any("Inbox" in label for label in active), (
            f"Expected Inbox to be active after click, got: {active}"
        )

    def test_only_one_item_active_at_a_time(self):
        """Only one sidebar NavLink has data-active at any given time."""
        _click_sidebar_link(self._page, "Team members")
        active = _get_active_nav_labels(self._page)
        assert len(active) == 1, (
            f"Expected exactly 1 active nav item, found {len(active)}: {active}"
        )

    def test_active_state_matches_current_page(self):
        """Active nav label matches the page content after multiple navigations."""
        _click_sidebar_link(self._page, "Widget configuration")
        active = _get_active_nav_labels(self._page)
        assert any("Widget" in label for label in active), (
            f"Expected Widget configuration to be active, got: {active}"
        )
        _click_sidebar_link(self._page, "Integrations")
        active = _get_active_nav_labels(self._page)
        assert any("Integrations" in label for label in active), (
            f"Expected Integrations to be active, got: {active}"
        )

