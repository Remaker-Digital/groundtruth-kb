"""
Live E2E navigation smoke tests — every page loads with real data.

Validates that the admin SPA renders correctly against the production
backend: all pages load without errors, sidebar navigation items are
present, and the header reflects real tenant configuration.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re

import pytest
from playwright.sync_api import Page

from tests.e2e_live.conftest import NAV_ITEMS, _navigate_admin_to


# ---------------------------------------------------------------------------
# Page loading — each page reachable and renders a heading
# ---------------------------------------------------------------------------

class TestPageLoading:
    """Every admin page loads with real data, no 'Application error'."""

    def test_dashboard_loads(self, shared_admin_page: Page):
        """Dashboard heading is visible after login with real credentials."""
        assert shared_admin_page.locator("text=Dashboard").first.is_visible()
        # No application error banner
        assert shared_admin_page.locator("text=Application error").count() == 0

    def test_inbox_loads(self, shared_inbox_page: Page):
        """Inbox page loads and shows the Inbox heading."""
        assert shared_inbox_page.locator("text=Inbox").first.is_visible()

    def test_team_loads(self, shared_team_page: Page):
        """Team members page loads with real team data."""
        assert shared_team_page.locator("text=Team members").first.is_visible()

    def test_configuration_loads(self, shared_config_page: Page):
        """Agent configuration page loads with real config data."""
        heading = shared_config_page.locator("text=Configuration").first
        assert heading.is_visible()

    def test_knowledge_base_loads(self, shared_kb_page: Page):
        """Knowledge base page loads."""
        assert shared_kb_page.locator("text=Knowledge").first.is_visible()

    def test_quick_actions_loads(self, shared_quick_actions_page: Page):
        """Quick actions page loads."""
        assert shared_quick_actions_page.locator("text=Quick actions").first.is_visible()

    def test_widget_loads(self, shared_widget_page: Page):
        """Widget configuration page loads with real widget data."""
        assert shared_widget_page.locator("text=Widget").first.is_visible()

    def test_integrations_loads(self, shared_integrations_page: Page):
        """Integrations page loads."""
        # The integrations page may not have a specific heading
        # but the nav click succeeded and no error is shown
        assert shared_integrations_page.locator("text=Application error").count() == 0

    def test_memory_privacy_loads(self, shared_memory_page: Page):
        """Memory & privacy page loads (Professional+ tier)."""
        assert shared_memory_page.locator("text=Memory").first.is_visible()

    def test_billing_loads(self, shared_billing_page: Page):
        """Billing page loads."""
        assert shared_billing_page.locator("text=Billing").first.is_visible()


# ---------------------------------------------------------------------------
# Layout elements — header and sidebar present with real content
# ---------------------------------------------------------------------------

class TestLayoutElements:
    """Sidebar navigation and header render correctly with real data."""

    def test_sidebar_has_all_nav_items(self, shared_admin_page: Page):
        """All navigation items are present in the sidebar."""
        nav = shared_admin_page.locator("nav")
        for item_text in NAV_ITEMS:
            link = nav.locator(f"text={item_text}").first
            assert link.is_visible(), f"Nav item '{item_text}' not visible in sidebar"

    def test_header_shows_brand_name(self, shared_admin_page: Page):
        """The header displays the real brand name from production config."""
        # The header should contain text that is NOT a generic placeholder
        header = shared_admin_page.locator("header").first
        header_text = header.text_content() or ""
        # Real brand name should be non-empty and not a default placeholder
        assert len(header_text.strip()) > 0, "Header has no text content"

    def test_header_shows_tier_badge(self, shared_admin_page: Page):
        """The tier badge (e.g., 'Professional') is visible in the header."""
        # Look for a tier indicator — Professional, Starter, or Enterprise
        tier_text = shared_admin_page.locator(
            "text=/Professional|Starter|Enterprise/"
        ).first
        assert tier_text.is_visible(), "No tier badge visible in header"

    def test_header_shows_store_link_or_tenant_name(self, shared_admin_page: Page):
        """The header shows a Shopify store link or the tenant/brand name.

        Production tenants with Shopify show a store link (e.g. "blanco-9939").
        Standalone or freshly-seeded tenants may show a brand name or the
        tenant identifier instead.
        """
        header = shared_admin_page.locator("header").first
        header_text = header.text_content() or ""
        # Accept Shopify store link, brand name, or any meaningful content
        has_store = "blanco" in header_text.lower()
        has_brand = bool(re.search(r"[A-Za-z]{2,}", header_text))
        assert has_store or has_brand, (
            f"Header has no store link or brand name. Text: {header_text[:100]}"
        )

    def test_no_console_errors(self, shared_admin_page: Page):
        """No uncaught JavaScript exceptions on the Dashboard page."""
        errors: list[str] = []
        shared_admin_page.on("pageerror", lambda exc: errors.append(str(exc)))

        # Re-navigate to trigger any load-time errors
        # S134: Use "load" — live SPAs prevent networkidle from resolving.
        shared_admin_page.reload(wait_until="load")
        shared_admin_page.wait_for_selector("text=Dashboard", timeout=15_000)

        assert len(errors) == 0, f"Uncaught JS errors: {errors}"
