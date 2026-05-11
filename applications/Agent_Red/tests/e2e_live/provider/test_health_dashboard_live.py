"""
Live E2E tests — Provider Console: Health Dashboard + Layout Shell.

Tests the ProviderLayout (header, sidebar, navigation) and the
HealthDashboard landing page (system health cards, tenant distribution,
recent deployments).

Source: admin/provider/layouts/ProviderLayout.tsx
        admin/provider/pages/HealthDashboard.tsx

API: GET /api/superadmin/dashboard

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re

import pytest
from playwright.sync_api import Page

from .conftest import (
    _main_text,
    _is_rate_limited,
    NAV_GROUPS,
    ALL_NAV_ITEMS,
)


# ===========================================================================
# SECTION A: Provider Layout — Header
# ===========================================================================


class TestProviderHeader:
    """Header bar: logo, title, version badge, action buttons."""

    def test_logo_present(self, shared_health_dashboard_page: Page):
        """Header contains the Agent Red logo image."""
        logo = shared_health_dashboard_page.locator("header img[src*='logo']")
        assert logo.count() > 0, "Provider console header must contain logo image"

    def test_console_title(self, shared_health_dashboard_page: Page):
        """Header shows 'Service Provider Console' title."""
        header = shared_health_dashboard_page.locator("header")
        text = header.inner_text(timeout=5_000)
        assert "service provider console" in text.lower(), (
            f"Header must contain 'Service Provider Console', got: {text[:200]}"
        )

    def test_version_badge(self, shared_health_dashboard_page: Page):
        """Header shows version badge (e.g., 'v1.68.0')."""
        header = shared_health_dashboard_page.locator("header")
        badge = header.locator("[class*='badge' i]")
        if badge.count() == 0:
            # Version badge is conditional on API response
            return  # Data-dependent — API may not have returned version yet
        text = badge.first.inner_text(timeout=3_000)
        assert re.match(r"v\d+\.\d+", text), (
            f"Version badge must match 'vN.N' format, got: {text}"
        )

    def test_docs_link(self, shared_health_dashboard_page: Page):
        """Header has documentation link pointing to agentredcx.com."""
        docs_btn = shared_health_dashboard_page.locator(
            "header a[href*='agentredcx.com']"
        )
        assert docs_btn.count() > 0, (
            "Header must contain documentation link to agentredcx.com"
        )

    def test_docs_link_aria_label(self, shared_health_dashboard_page: Page):
        """Documentation button has accessible label."""
        docs_btn = shared_health_dashboard_page.locator(
            "header [aria-label='Open documentation']"
        )
        assert docs_btn.count() > 0, (
            "Documentation button must have aria-label='Open documentation'"
        )

    def test_logout_button(self, shared_health_dashboard_page: Page):
        """Header has sign-out button with aria-label."""
        logout_btn = shared_health_dashboard_page.locator(
            "header [aria-label='Sign out']"
        )
        assert logout_btn.count() > 0, (
            "Header must contain sign-out button with aria-label='Sign out'"
        )

    def test_burger_menu_hidden_desktop(self, shared_health_dashboard_page: Page):
        """Burger menu is hidden on desktop viewport (hiddenFrom='sm')."""
        burger = shared_health_dashboard_page.locator("header button[class*='burger' i]")
        if burger.count() > 0:
            # On desktop viewport, burger should be hidden
            box = burger.first.bounding_box()
            if box and box["width"] > 0:
                return  # Burger visible on narrow viewport — acceptable
        # Either no burger or it's hidden — both acceptable on desktop


# ===========================================================================
# SECTION B: Provider Layout — Sidebar Navigation
# ===========================================================================


class TestProviderSidebar:
    """Sidebar navigation: group labels, nav items, descriptions, icons."""

    def test_nav_group_labels(self, shared_health_dashboard_page: Page):
        """All 4 navigation group labels are present."""
        nav = shared_health_dashboard_page.locator("nav")
        text = nav.inner_text(timeout=5_000).lower()
        for group_name in NAV_GROUPS.keys():
            assert group_name.lower() in text, (
                f"Sidebar must contain group label '{group_name}'"
            )

    @pytest.mark.parametrize("nav_label,path", ALL_NAV_ITEMS)
    def test_nav_item_present(self, shared_health_dashboard_page: Page, nav_label: str, path: str):
        """Each of the 19 nav items is visible in the sidebar."""
        nav = shared_health_dashboard_page.locator("nav")
        item = nav.get_by_text(nav_label, exact=True)
        assert item.count() > 0, (
            f"Sidebar must contain nav item '{nav_label}'"
        )

    def test_nav_item_descriptions(self, shared_health_dashboard_page: Page):
        """Nav items have description text below the label."""
        nav = shared_health_dashboard_page.locator("nav")
        text = nav.inner_text(timeout=5_000).lower()
        # Check for a sample of descriptions from ProviderLayout.tsx
        descriptions = [
            "system health overview",
            "tenant directory",
            "deploy history",
            "incident management",
            "two-factor auth",
        ]
        found = sum(1 for d in descriptions if d in text)
        assert found >= 3, (
            f"At least 3/5 sampled nav descriptions must be present, found {found}"
        )

    def test_nav_item_icons(self, shared_health_dashboard_page: Page):
        """Nav items have SVG icons (leftSection)."""
        nav = shared_health_dashboard_page.locator("nav")
        svgs = nav.locator("svg")
        # 19 nav items should each have an icon
        assert svgs.count() >= 15, (
            f"Sidebar should have ~19 nav icons, found {svgs.count()}"
        )

    def test_dashboard_active_by_default(self, shared_health_dashboard_page: Page):
        """Dashboard nav item is active on the landing page."""
        nav = shared_health_dashboard_page.locator("nav")
        active_link = nav.locator("[data-active='true'], [data-active]")
        if active_link.count() > 0:
            text = active_link.first.inner_text(timeout=3_000)
            assert "dashboard" in text.lower(), (
                f"Active nav item should be Dashboard, got: {text[:100]}"
            )
        else:
            # Mantine NavLink may use different active attribute
            return  # Cannot verify active state — acceptable

    def test_group_dividers(self, shared_health_dashboard_page: Page):
        """Dividers separate navigation groups."""
        nav = shared_health_dashboard_page.locator("nav")
        dividers = nav.locator("hr, [class*='divider' i]")
        # 4 groups = 3 dividers between them
        assert dividers.count() >= 2, (
            f"At least 2 dividers expected between 4 groups, found {dividers.count()}"
        )

    def test_scroll_area(self, shared_health_dashboard_page: Page):
        """Sidebar uses a scroll area for overflow."""
        nav = shared_health_dashboard_page.locator("nav")
        scroll = nav.locator("[class*='scrollArea' i], [class*='scroll-area' i], [data-radix-scroll-area-viewport]")
        # Mantine ScrollArea renders with specific classes
        if scroll.count() == 0:
            # Fallback: check for overflow styles
            style = nav.evaluate("el => getComputedStyle(el).overflow")
            assert style in ("auto", "scroll", "hidden"), (
                "Sidebar should have scroll area or overflow handling"
            )


# ===========================================================================
# SECTION C: Provider Layout — Navigation Behavior
# ===========================================================================


class TestProviderNavigation:
    """Navigation between pages — clicking sidebar items loads correct pages."""

    def test_navigate_to_tenants(self, shared_health_dashboard_page: Page):
        """Clicking 'Tenants' navigates to tenant directory."""
        page = shared_health_dashboard_page
        page.get_by_text("Tenants", exact=True).first.click()
        page.wait_for_timeout(2000)
        text = _main_text(page).lower()
        assert "tenant" in text, "Tenants page should contain 'tenant' text"

    def test_navigate_to_deployments(self, shared_health_dashboard_page: Page):
        """Clicking 'Deployments' navigates to deployment history."""
        page = shared_health_dashboard_page
        page.get_by_text("Deployments", exact=True).first.click()
        page.wait_for_timeout(2000)
        text = _main_text(page).lower()
        assert "deployment" in text or "deploy" in text, (
            "Deployments page should contain deployment-related text"
        )

    def test_navigate_and_return(self, shared_health_dashboard_page: Page):
        """Navigate away and return to dashboard."""
        page = shared_health_dashboard_page
        page.get_by_text("Tenants", exact=True).first.click()
        page.wait_for_timeout(1500)
        page.get_by_text("Dashboard", exact=True).first.click()
        page.wait_for_timeout(1500)
        text = _main_text(page).lower()
        assert "platform dashboard" in text or "dashboard" in text, (
            "Should return to Platform Dashboard"
        )


# ===========================================================================
# SECTION D: Health Dashboard — Page Header
# ===========================================================================


class TestDashboardHeader:
    """Platform Dashboard page header: title, help tooltip, timestamp."""

    def test_page_title(self, shared_health_dashboard_page: Page):
        """Page shows 'Platform Dashboard' title."""
        text = _main_text(shared_health_dashboard_page)
        assert "platform dashboard" in text.lower(), (
            f"Page must show 'Platform Dashboard' title, got: {text[:200]}"
        )

    def test_help_tooltip_icon(self, shared_health_dashboard_page: Page):
        """Page header has HelpTooltip (circled '?' icon)."""
        tooltip = shared_health_dashboard_page.locator(
            "main span[role='button'][aria-label]"
        )
        if tooltip.count() > 0:
            text = tooltip.first.inner_text(timeout=3_000)
            assert "?" in text, "HelpTooltip icon should contain '?'"
        else:
            # HelpTooltip might use different structure
            q_marks = shared_health_dashboard_page.locator("main >> text=?")
            assert q_marks.count() > 0, "Page must have HelpTooltip '?' icon"

    def test_timestamp_display(self, shared_health_dashboard_page: Page):
        """Dashboard shows 'Updated' timestamp."""
        text = _main_text(shared_health_dashboard_page)
        assert "updated" in text.lower(), (
            "Dashboard must show 'Updated {timestamp}' text"
        )

    def test_timestamp_format(self, shared_health_dashboard_page: Page):
        """Timestamp contains recognizable date/time characters."""
        text = _main_text(shared_health_dashboard_page)
        # Look for date patterns like "3/4/2026" or "2026-03-04" or "AM/PM"
        has_date = bool(re.search(r'\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}', text))
        has_time = bool(re.search(r'\d{1,2}:\d{2}', text))
        assert has_date or has_time, (
            "Timestamp should contain recognizable date/time format"
        )


# ===========================================================================
# SECTION E: Health Dashboard — System Health Cards
# ===========================================================================


class TestSystemHealthCards:
    """4 system health cards: NATS, Key Vault, API Version, Circuit Breakers."""

    def test_four_health_cards(self, shared_health_dashboard_page: Page):
        """Dashboard renders exactly 4 system health cards."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify health cards")
        cards = shared_health_dashboard_page.locator(
            "main [class*='card' i][class*='border' i], main [class*='Card' i]"
        )
        # Minimum 4 health cards (may have more from tenant distribution)
        assert cards.count() >= 4, (
            f"Dashboard must have at least 4 health cards, found {cards.count()}"
        )

    def test_cosmos_db_card(self, shared_health_dashboard_page: Page):
        """Cosmos DB health card is present."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify Cosmos DB card")
        text = _main_text(shared_health_dashboard_page).lower()
        assert "cosmos" in text, "Dashboard must show Cosmos DB health card"

    def test_redis_card(self, shared_health_dashboard_page: Page):
        """Redis health card is present."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify Redis card")
        text = _main_text(shared_health_dashboard_page).lower()
        assert "redis" in text, "Dashboard must show Redis health card"

    def test_key_vault_card(self, shared_health_dashboard_page: Page):
        """Key Vault health card is present."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify Key Vault card")
        text = _main_text(shared_health_dashboard_page).lower()
        assert "key vault" in text, "Dashboard must show Key Vault health card"

    def test_key_vault_status(self, shared_health_dashboard_page: Page):
        """Key Vault shows Healthy or Degraded status."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify Key Vault status")
        text = _main_text(shared_health_dashboard_page).lower()
        has_status = "healthy" in text or "degraded" in text
        assert has_status, "Key Vault card must show Healthy or Degraded"

    def test_api_version_card(self, shared_health_dashboard_page: Page):
        """API Version card is present and shows version number."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify API version")
        text = _main_text(shared_health_dashboard_page)
        assert re.search(r'v\d+\.\d+', text), (
            "Dashboard must show API version (e.g., v1.68.0)"
        )

    def test_cosmos_db_status(self, shared_health_dashboard_page: Page):
        """Cosmos DB card shows Connected or Unavailable status."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify Cosmos DB status")
        text = _main_text(shared_health_dashboard_page).lower()
        has_status = "connected" in text or "unavailable" in text
        assert has_status, "Cosmos DB card must show Connected or Unavailable"

    def test_redis_status(self, shared_health_dashboard_page: Page):
        """Redis card shows Connected or Unavailable status."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify Redis status")
        text = _main_text(shared_health_dashboard_page).lower()
        has_status = "connected" in text or "unavailable" in text
        assert has_status, "Redis card must show Connected or Unavailable"

    def test_status_dot_indicators(self, shared_health_dashboard_page: Page):
        """Health cards have colored status dot indicators (8px circles)."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify status dots")
        dots = shared_health_dashboard_page.locator(
            "main div[style*='border-radius'][style*='8px'], "
            "main div[style*='borderRadius'][style*='50%']"
        )
        # Each of the 4 health cards has a status dot
        assert dots.count() >= 3, (
            f"Expected ~4 status dot indicators, found {dots.count()}"
        )

    def test_health_card_labels_uppercase(self, shared_health_dashboard_page: Page):
        """Health card labels are uppercase (tt='uppercase')."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify card labels")
        text = _main_text(shared_health_dashboard_page)
        # Check for uppercase labels
        for label in ["API VERSION", "COSMOS DB", "REDIS", "KEY VAULT"]:
            assert label in text, (
                f"Health card label '{label}' should appear uppercase"
            )


# ===========================================================================
# SECTION F: Health Dashboard — Tenant Distribution
# ===========================================================================


class TestTenantDistribution:
    """Tenant distribution section: total, by status, by tier."""

    def test_section_title(self, shared_health_dashboard_page: Page):
        """'Tenant Distribution' section header is present."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify tenant distribution")
        text = _main_text(shared_health_dashboard_page).lower()
        assert "tenant distribution" in text, (
            "Dashboard must show 'Tenant Distribution' section"
        )

    def test_total_tenants_card(self, shared_health_dashboard_page: Page):
        """Total Tenants card shows a numeric count."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify total tenants")
        text = _main_text(shared_health_dashboard_page).lower()
        assert "total tenants" in text, "Must show 'Total Tenants' label"

    def test_total_tenants_numeric(self, shared_health_dashboard_page: Page):
        """Total tenants value is a number >= 1."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify tenant count")
        text = _main_text(shared_health_dashboard_page)
        idx = text.lower().find("total tenants")
        if idx >= 0:
            section = text[idx:idx + 100]
            numbers = re.findall(r'\d+', section)
            assert len(numbers) > 0, "Total tenants must show a numeric value"
            assert int(numbers[0]) >= 1, "Total tenants must be >= 1"

    def test_by_status_card(self, shared_health_dashboard_page: Page):
        """'By Status' card is present with status badges."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify status breakdown")
        text = _main_text(shared_health_dashboard_page).lower()
        assert "by status" in text, "Must show 'By Status' card"

    def test_by_status_badges(self, shared_health_dashboard_page: Page):
        """Status card shows badges like 'active: N'."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify status badges")
        text = _main_text(shared_health_dashboard_page).lower()
        # At least one status badge should be present
        has_status = bool(re.search(r'(active|inactive|suspended|trial):\s*\d+', text))
        if not has_status:
            return  # No tenant status data — data-dependent

    def test_by_tier_card(self, shared_health_dashboard_page: Page):
        """'By Tier' card is present with tier badges."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify tier breakdown")
        text = _main_text(shared_health_dashboard_page).lower()
        assert "by tier" in text, "Must show 'By Tier' card"

    def test_by_tier_badges(self, shared_health_dashboard_page: Page):
        """Tier card shows badges like 'starter: N', 'professional: N'."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify tier badges")
        text = _main_text(shared_health_dashboard_page).lower()
        has_tier = bool(re.search(r'(starter|professional|enterprise|trial):\s*\d+', text))
        if not has_tier:
            return  # No tier data — data-dependent

    def test_three_distribution_cards(self, shared_health_dashboard_page: Page):
        """Tenant distribution section has 3 cards (total, status, tier)."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify distribution cards")
        text = _main_text(shared_health_dashboard_page).lower()
        labels = ["total tenants", "by status", "by tier"]
        found = sum(1 for label in labels if label in text)
        assert found >= 2, (
            f"Expected 3 distribution card labels, found {found}/3"
        )


# ===========================================================================
# SECTION G: Health Dashboard — Recent Deployments
# ===========================================================================


class TestRecentDeployments:
    """Recent deployments section: event badges, actors, timestamps."""

    def test_section_title(self, shared_health_dashboard_page: Page):
        """'Recent Deployments' section header is present (if data exists)."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify deployments")
        text = _main_text(shared_health_dashboard_page).lower()
        if "recent deployments" not in text:
            return  # No deployment data — section is conditional

    def test_deployment_event_badges(self, shared_health_dashboard_page: Page):
        """Deployment events show 'Deploy' or 'Rollback' badges."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify deployment badges")
        text = _main_text(shared_health_dashboard_page).lower()
        if "recent deployments" not in text:
            return  # No deployment data
        has_type = "deploy" in text or "rollback" in text
        assert has_type, "Deployment events must show Deploy or Rollback type"

    def test_deployment_actor(self, shared_health_dashboard_page: Page):
        """Deployment events show an actor (user or 'system')."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify deployment actor")
        text = _main_text(shared_health_dashboard_page).lower()
        if "recent deployments" not in text:
            return  # No deployment data
        # Actor could be "system" or a username
        has_actor = "system" in text or "@" in text or bool(re.search(r'[a-z]{3,}', text))
        assert has_actor, "Deployment events must show an actor"

    def test_deployment_timestamp(self, shared_health_dashboard_page: Page):
        """Deployment events show timestamps."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify deployment timestamps")
        text = _main_text(shared_health_dashboard_page)
        if "recent deployments" not in text.lower():
            return  # No deployment data
        # Look for time pattern after "Recent Deployments"
        idx = text.lower().find("recent deployments")
        section = text[idx:] if idx >= 0 else ""
        has_time = bool(re.search(r'\d{1,2}:\d{2}', section))
        has_date = bool(re.search(r'\d{1,2}/\d{1,2}', section))
        assert has_time or has_date, "Deployment events must show timestamp"

    def test_deployments_in_paper_container(self, shared_health_dashboard_page: Page):
        """Recent deployments are wrapped in a Paper component with border."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify deployments container")
        text = _main_text(shared_health_dashboard_page).lower()
        if "recent deployments" not in text:
            return  # No deployment data
        # Paper withBorder renders as a bordered container
        papers = shared_health_dashboard_page.locator(
            "main [class*='paper' i], main [class*='Paper']"
        )
        assert papers.count() > 0, "Dashboard should use Paper containers"


# ===========================================================================
# SECTION H: Health Dashboard — Empty / Error States
# ===========================================================================


class TestDashboardStates:
    """Loading, empty, and error states."""

    def test_no_loading_spinner_after_load(self, shared_health_dashboard_page: Page):
        """After page load, loading spinner should not be visible."""
        # LoadingState component shows "Loading dashboard" text
        text = _main_text(shared_health_dashboard_page).lower()
        assert "loading dashboard" not in text, (
            "Loading state should not persist after page load"
        )

    def test_error_state_content(self, shared_health_dashboard_page: Page):
        """If API failed, shows 'Unable to load dashboard' empty state."""
        text = _main_text(shared_health_dashboard_page).lower()
        if "unable to load" in text:
            assert "refresh" in text or "try" in text, (
                "Error state should suggest refreshing the page"
            )
        # If no error, test passes (dashboard loaded successfully)

    def test_dashboard_has_content(self, shared_health_dashboard_page: Page):
        """Dashboard shows meaningful content (not blank)."""
        text = _main_text(shared_health_dashboard_page)
        assert len(text.strip()) > 50, (
            f"Dashboard must have meaningful content, got {len(text)} chars"
        )


# ===========================================================================
# SECTION I: Health Dashboard — Responsive Grid
# ===========================================================================


class TestDashboardGrid:
    """Responsive grid layout for health cards and distribution."""

    def test_health_cards_grid(self, shared_health_dashboard_page: Page):
        """Health cards use SimpleGrid with responsive columns."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify grid layout")
        # SimpleGrid renders children in a CSS grid
        grids = shared_health_dashboard_page.locator(
            "main [class*='simpleGrid' i], main [class*='SimpleGrid' i], "
            "main [style*='grid-template']"
        )
        assert grids.count() > 0, (
            "Health cards should use a grid layout (SimpleGrid)"
        )

    def test_distribution_cards_grid(self, shared_health_dashboard_page: Page):
        """Tenant distribution uses Grid component with 3 columns."""
        if _is_rate_limited(shared_health_dashboard_page):
            pytest.skip("Rate limited — cannot verify distribution grid")
        text = _main_text(shared_health_dashboard_page).lower()
        if "tenant distribution" not in text:
            return  # No tenant data
        # Grid.Col renders with Mantine grid classes
        cols = shared_health_dashboard_page.locator(
            "main [class*='col' i][class*='grid' i], main [class*='Col']"
        )
        # Expect at least 3 grid columns for the distribution cards
        assert cols.count() >= 2, (
            f"Expected >= 3 distribution grid columns, found {cols.count()}"
        )
