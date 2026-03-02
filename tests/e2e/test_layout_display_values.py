"""
E2E display-value tests — Layout (sidebar + footer).

Validates every visible element in the StandaloneLayout shell that wraps all
admin pages: sidebar navigation items, tier badge, brand name, AI Configuration
status badge, footer copyright text, and version display.

Uses the ``admin_page`` fixture which lands on the Dashboard — the layout
chrome (sidebar, header, footer) is always visible regardless of which page
is active.

Mock data sources:
  - MOCK_TENANT_CONTEXT: tier="professional" -> header badge "Professional"
  - MOCK_CONFIG: brand_name="TestCo" -> header brand display
  - activation-status mock: is_active=True -> sidebar "Active" badge
  - Footer: hardcoded in StandaloneLayout.tsx

Run with:
    pytest tests/e2e/test_layout_display_values.py -v --headed
    pytest tests/e2e/test_layout_display_values.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e


# ===========================================================================
# TestLayoutDisplayValues — sidebar, header, footer element verification
# ===========================================================================


class TestLayoutDisplayValues:
    """Verify every layout chrome element displays the correct value."""

    # -- Header elements --------------------------------------------------

    def test_tier_badge_shows_professional(self, admin_page: Page) -> None:
        """Tier badge in header reads 'Professional' (from MOCK_TENANT_CONTEXT)."""
        badge = admin_page.locator("[class*='badge'], [class*='Badge']").filter(
            has_text="Professional"
        )
        expect(badge.first).to_be_visible()

    def test_brand_name_in_header(self, admin_page: Page) -> None:
        """Brand name 'TestCo' appears in the header area (from MOCK_CONFIG)."""
        # The layout reads brand_name from tenantContext.brandName or the
        # config endpoint.  With mock data brand_name="TestCo", the header
        # may show it as a storefront link or plain text.
        brand = admin_page.get_by_text("TestCo")
        expect(brand.first).to_be_visible()

    def test_customer_experience_wordmark(self, admin_page: Page) -> None:
        """Header shows 'Customer Experience' wordmark next to logo."""
        wordmark = admin_page.get_by_text("Customer Experience")
        expect(wordmark.first).to_be_visible()

    # -- AI Configuration status badge ------------------------------------

    def test_ai_config_status_badge_active(self, admin_page: Page) -> None:
        """AI Configuration sidebar group shows 'Active' badge (is_active=True)."""
        badge = admin_page.locator("[class*='badge'], [class*='Badge']").filter(
            has_text="Active"
        )
        expect(badge.first).to_be_visible()

    def test_ai_config_group_label(self, admin_page: Page) -> None:
        """Sidebar shows 'AI Configuration' group label."""
        label = admin_page.get_by_text("AI Configuration")
        expect(label.first).to_be_visible()

    # -- Sidebar navigation items -----------------------------------------

    def test_nav_dashboard(self, admin_page: Page) -> None:
        """Sidebar has 'Dashboard' navigation link."""
        link = admin_page.get_by_text("Dashboard", exact=True)
        expect(link.first).to_be_visible()

    def test_nav_inbox(self, admin_page: Page) -> None:
        """Sidebar has 'Inbox' navigation link."""
        link = admin_page.get_by_text("Inbox", exact=True)
        expect(link.first).to_be_visible()

    def test_nav_team_members(self, admin_page: Page) -> None:
        """Sidebar has 'Team members' navigation link."""
        link = admin_page.get_by_text("Team members", exact=True)
        expect(link.first).to_be_visible()

    def test_nav_agent_configuration(self, admin_page: Page) -> None:
        """Sidebar has 'Agent configuration' navigation link."""
        link = admin_page.get_by_text("Agent configuration", exact=True)
        expect(link.first).to_be_visible()

    def test_nav_knowledge_base(self, admin_page: Page) -> None:
        """Sidebar has 'Knowledge base' navigation link."""
        link = admin_page.get_by_text("Knowledge base", exact=True)
        expect(link.first).to_be_visible()

    def test_nav_quick_actions(self, admin_page: Page) -> None:
        """Sidebar has 'Quick actions' navigation link."""
        link = admin_page.get_by_text("Quick actions", exact=True)
        expect(link.first).to_be_visible()

    def test_nav_widget_configuration(self, admin_page: Page) -> None:
        """Sidebar has 'Widget configuration' navigation link."""
        link = admin_page.get_by_text("Widget configuration", exact=True)
        expect(link.first).to_be_visible()

    def test_nav_integrations(self, admin_page: Page) -> None:
        """Sidebar has 'Integrations' navigation link."""
        link = admin_page.get_by_text("Integrations", exact=True)
        expect(link.first).to_be_visible()

    def test_nav_memory_and_privacy(self, admin_page: Page) -> None:
        """Sidebar has 'Memory & privacy' navigation link."""
        link = admin_page.get_by_text("Memory & privacy", exact=True)
        expect(link.first).to_be_visible()

    def test_nav_billing(self, admin_page: Page) -> None:
        """Sidebar has 'Billing' navigation link."""
        link = admin_page.get_by_text("Billing", exact=True)
        expect(link.first).to_be_visible()

    # -- Footer -----------------------------------------------------------

    def test_footer_product_name(self, admin_page: Page) -> None:
        """Footer shows 'Agent Red Customer Experience' product name."""
        footer_text = admin_page.get_by_text("Agent Red Customer Experience")
        expect(footer_text.first).to_be_visible()

    def test_footer_version_element_present(self, admin_page: Page) -> None:
        """Footer shows a version string (v... or '...' fallback).

        The mock API does not set X-Product-Version response headers, so the
        layout falls back to displaying '...' as the version.  We verify the
        version text element is present (starts with 'v').
        """
        # The footer renders <Text>v{productVersion || '...'}</Text>
        # In the mock environment, productVersion may be empty string → 'v...'
        version_el = admin_page.locator("text=/^v/")
        expect(version_el.first).to_be_visible()

    def test_footer_copyright_text(self, admin_page: Page) -> None:
        """Footer contains '2026 Remaker Digital' copyright notice."""
        copyright_text = admin_page.get_by_text("2026 Remaker Digital")
        expect(copyright_text.first).to_be_visible()

    def test_footer_legal_entity(self, admin_page: Page) -> None:
        """Footer contains 'VanDusen & Palmeter, LLC' legal entity."""
        entity = admin_page.get_by_text("VanDusen & Palmeter, LLC")
        expect(entity.first).to_be_visible()
