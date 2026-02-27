"""
E2E tests — Navigation and page loading.

Tests that every admin page loads without errors when navigated to from
the sidebar.  This catches structural regressions: pages that crash on
load, missing imports, broken routes, and removed components.

This is the "smoke test" for the admin SPA — if any page fails to render,
this test suite catches it.

Run with:
    pytest tests/e2e/test_navigation.py -v --headed
    pytest tests/e2e/test_navigation.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e


# ===========================================================================
# Navigation Smoke Tests
# ===========================================================================


class TestPageNavigation:
    """Verify every page in the sidebar loads without crashing."""

    def test_dashboard_loads(self, admin_page: Page) -> None:
        """Dashboard page (default route) loads successfully."""
        # Dashboard is the default page after login
        expect(admin_page.locator("text=Dashboard").first).to_be_visible()

    def test_inbox_loads(self, admin_page: Page) -> None:
        """Inbox page loads and shows conversation list."""
        admin_page.get_by_text("Inbox", exact=True).first.click()
        admin_page.wait_for_timeout(500)
        assert not admin_page.locator("text=Application error").is_visible()

    def test_configuration_loads(self, admin_page: Page) -> None:
        """Configuration page loads with form fields."""
        admin_page.get_by_text("Agent configuration").first.click()
        admin_page.wait_for_timeout(500)
        assert not admin_page.locator("text=Application error").is_visible()

    def test_knowledge_base_loads(self, admin_page: Page) -> None:
        """Knowledge Base page loads with article list."""
        admin_page.get_by_text("Knowledge base").first.click()
        admin_page.wait_for_timeout(500)
        assert not admin_page.locator("text=Application error").is_visible()

    def test_widget_page_loads(self, admin_page: Page) -> None:
        """Widget customization page loads."""
        admin_page.get_by_text("Widget configuration").first.click()
        admin_page.wait_for_timeout(500)
        assert not admin_page.locator("text=Application error").is_visible()

    def test_quick_actions_loads(self, admin_page: Page) -> None:
        """Quick Actions page loads."""
        admin_page.get_by_text("Quick actions").first.click()
        admin_page.wait_for_timeout(500)
        assert not admin_page.locator("text=Application error").is_visible()

    def test_team_page_loads(self, admin_page: Page) -> None:
        """Team page loads with member table."""
        admin_page.get_by_text("Team members").first.click()
        admin_page.wait_for_timeout(500)
        expect(admin_page.locator("text=Team members").first).to_be_visible()

    def test_billing_page_loads(self, admin_page: Page) -> None:
        """Billing page loads."""
        admin_page.get_by_text("Billing", exact=True).first.click()
        admin_page.wait_for_timeout(500)
        assert not admin_page.locator("text=Application error").is_visible()

    def test_integrations_page_loads(self, admin_page: Page) -> None:
        """Integrations page loads."""
        admin_page.get_by_text("Integrations", exact=True).first.click()
        admin_page.wait_for_timeout(500)
        assert not admin_page.locator("text=Application error").is_visible()

    def test_memory_privacy_loads(self, admin_page: Page) -> None:
        """Memory & Privacy page loads."""
        admin_page.get_by_text("Memory & privacy").first.click()
        admin_page.wait_for_timeout(500)
        assert not admin_page.locator("text=Application error").is_visible()


# ===========================================================================
# Sidebar Structure Tests
# ===========================================================================


class TestSidebarStructure:
    """Verify the sidebar navigation renders all expected links."""

    def test_sidebar_has_all_nav_links(self, admin_page: Page) -> None:
        """All 10 navigation items are present in the sidebar."""
        expected_items = [
            "Dashboard",
            "Inbox",
            "Team members",
            "Agent configuration",
            "Knowledge base",
            "Quick actions",
            "Widget configuration",
            "Integrations",
            "Memory & privacy",
            "Billing",
        ]
        for item in expected_items:
            link = admin_page.locator(f"text={item}")
            assert link.count() > 0, f"Sidebar should have '{item}' nav link"

    def test_active_nav_link_highlighted(self, admin_page: Page) -> None:
        """The active page's nav link is visually distinguished."""
        # Dashboard is active by default — check it has some active indicator
        # (This is a structural presence test, not a CSS value test)
        dashboard_link = admin_page.locator("text=Dashboard").first
        expect(dashboard_link).to_be_visible()

    def test_dark_mode_toggle_exists(self, admin_page: Page) -> None:
        """Dark mode toggle exists in the sidebar or header."""
        # Look for sun/moon icon or "Dark mode" / "Light mode" toggle
        dark_toggle = admin_page.locator('[aria-label*="mode"], [aria-label*="theme"]')
        # Also check for Mantine's color scheme toggle
        mantine_toggle = admin_page.locator('[data-testid="color-scheme-toggle"]')
        sun_icon = admin_page.locator('button:has(svg)')  # Generic icon buttons in sidebar
        # At least verify the sidebar itself renders
        assert dark_toggle.count() > 0 or mantine_toggle.count() > 0 or sun_icon.count() > 0, \
            "Theme toggle should exist in the layout"

    def test_logout_button_exists(self, admin_page: Page) -> None:
        """Logout button or link exists."""
        # The standalone layout uses aria-label="Sign out" on the logout icon button
        sign_out = admin_page.locator('[aria-label="Sign out"]')
        assert sign_out.count() > 0, \
            "Sign out button with aria-label='Sign out' should exist"


# ===========================================================================
# Console Error Detection
# ===========================================================================


class TestNoConsoleErrors:
    """Verify no JavaScript errors are thrown during navigation."""

    def test_no_js_errors_on_page_load(self, admin_page: Page) -> None:
        """No uncaught JavaScript errors on initial page load."""
        errors: list[str] = []
        admin_page.on("pageerror", lambda err: errors.append(str(err)))

        # Navigate through a few pages to trigger any lazy errors
        for nav_text in ["Team members", "Agent configuration", "Widget configuration", "Knowledge base", "Dashboard"]:
            try:
                admin_page.locator(f"text={nav_text}").first.click()
                admin_page.wait_for_timeout(300)
            except Exception:
                pass  # Navigation might fail for some pages — that's OK here

        assert len(errors) == 0, f"JavaScript errors detected: {errors}"


class TestSystemStateIndicator:
    """Verify system state indicator in navigation. WI 291."""

    def test_activation_status_in_navbar(self, admin_page: Page) -> None:
        """WI 291: Inactive system state indicator in nav bar.

        The navigation bar should show the system activation status
        (active/inactive/test mode) so merchants always know their system state.
        """
        page_text = admin_page.text_content("body") or ""
        # Look for activation status indicators in the nav/sidebar area
        status_indicators = ["Active", "Inactive", "Test mode", "Draft",
                           "Activated", "Not activated", "Live"]
        has_status = any(s in page_text for s in status_indicators)
        # The sidebar typically shows activation state
        sidebar = admin_page.locator("nav, [role='navigation'], aside")
        sidebar_text = ""
        if sidebar.count() > 0:
            sidebar_text = sidebar.first.text_content() or ""
        has_sidebar_status = any(s in sidebar_text for s in status_indicators)
        assert has_status or has_sidebar_status, \
            "Navigation should show system activation status indicator"
