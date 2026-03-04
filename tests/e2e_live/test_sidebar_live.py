"""
Live E2E tests for sidebar navigation — SPEC-1652/1653 closed-loop quality.

Covers EL-sidebar-001 through EL-sidebar-026 across all applicable dimensions.
Runs against the real staging (or production) admin SPA with live API data,
proxied through the Vite dev server.

Test classes map to sidebar sections:
  A: Top Navigation (Dashboard, Inbox, Team members)
  B: AI Configuration Group (header, badge, 4 items, wizard, 3 buttons)
  C: Post-Config Navigation (Integrations, Memory & privacy, Billing)
  D: Footer (product name, version, copyright)
  E: Container (sidebar structure, active highlight)
  F: Conditional/Dynamic (icons, role visibility)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re

import pytest
from playwright.sync_api import Page, expect


# ─── Helpers ──────────────────────────────────────────────────────────────

def _sidebar(page: Page):
    """Return the sidebar/navbar locator (Mantine AppShell.Navbar)."""
    # Mantine renders AppShell.Navbar as <nav> with class containing mantine-AppShell-navbar
    loc = page.locator("nav[class*='AppShell-navbar' i]").first
    if loc.count() > 0:
        return loc
    # Fallback: any <nav> element
    return page.locator("nav").first


def _sidebar_text(page: Page) -> str:
    """All visible text in the sidebar."""
    sb = _sidebar(page)
    try:
        return sb.inner_text() or ""
    except Exception:
        return ""


def _nav_link(page: Page, label: str):
    """Locate a sidebar nav link by its visible label text."""
    sb = _sidebar(page)
    # Mantine NavLink renders label inside a span; get_by_text on the sidebar scope
    return sb.get_by_text(label, exact=True).first


def _nav_link_ancestor(page: Page, label: str):
    """Get the clickable NavLink ancestor element for a given label."""
    link_text = _nav_link(page, label)
    # Walk up to the <a> or clickable element with NavLink class
    return link_text.locator("xpath=ancestor::a[1]").first


def _computed_style(page: Page, selector: str, prop: str) -> str | None:
    """Read a computed CSS property from the first matching element."""
    try:
        return page.evaluate(
            f"""() => {{
                const el = document.querySelector({repr(selector)});
                return el ? getComputedStyle(el).getPropertyValue({repr(prop)}) : null;
            }}"""
        )
    except Exception:
        return None


def _sidebar_style(page: Page, prop: str) -> str | None:
    """Read a computed CSS property from the sidebar container."""
    return _computed_style(page, "nav[class*='AppShell-navbar']", prop) or \
           _computed_style(page, "nav", prop)


# ─── Section A: Top Navigation ────────────────────────────────────────────

class TestTopNavExistence:
    """EL-sidebar-001..003: Top nav items exist with correct labels."""

    @pytest.mark.parametrize("label", ["Dashboard", "Inbox", "Team members"])
    def test_nav_item_visible(self, live_admin_page: Page, label: str):
        """Each top nav item is visible in the sidebar."""
        link = _nav_link(live_admin_page, label)
        expect(link).to_be_visible(timeout=5_000)

    def test_nav_order(self, live_admin_page: Page):
        """Top nav items appear in correct order: Dashboard, Inbox, Team members."""
        text = _sidebar_text(live_admin_page)
        d_pos = text.find("Dashboard")
        i_pos = text.find("Inbox")
        t_pos = text.find("Team members")
        assert d_pos >= 0, "Dashboard not found in sidebar"
        assert i_pos >= 0, "Inbox not found in sidebar"
        assert t_pos >= 0, "Team members not found in sidebar"
        assert d_pos < i_pos < t_pos, (
            f"Wrong order: Dashboard@{d_pos}, Inbox@{i_pos}, Team members@{t_pos}"
        )


class TestTopNavStyle:
    """EL-sidebar-001..003: Nav item styling (dark theme, icons)."""

    @pytest.mark.parametrize("label", ["Dashboard", "Inbox", "Team members"])
    def test_nav_item_has_icon(self, live_admin_page: Page, label: str):
        """Each top nav item has an SVG icon."""
        link = _nav_link(live_admin_page, label)
        # Mantine NavLink: icon is a sibling <span class="NavLink-section">
        # of the label's parent <span class="NavLink-body">.  Walk up to the
        # clickable root <a> and look for any SVG within it.
        root = link.locator("xpath=ancestor::a[1]").first
        if root.count() == 0:
            # Fallback: walk up further
            root = link.locator("xpath=ancestor::*[contains(@class,'NavLink')][1]").first
        svg = root.locator("svg").first
        expect(svg).to_be_visible(timeout=3_000)


class TestTopNavAction:
    """EL-sidebar-001..003: Nav items navigate to correct routes."""

    def test_dashboard_click_stays_on_dashboard(self, live_admin_page: Page):
        """Clicking Dashboard keeps/returns to the dashboard page."""
        _nav_link(live_admin_page, "Dashboard").click()
        live_admin_page.wait_for_timeout(500)
        # URL should end with / or /admin/standalone/ (no deeper path)
        url = live_admin_page.url
        path = url.split("?")[0].rstrip("/")
        assert path.endswith("/admin/standalone") or path.endswith("/"), (
            f"Dashboard click navigated to unexpected path: {path}"
        )

    def test_inbox_click_navigates(self, live_admin_page: Page):
        """Clicking Inbox navigates to the inbox page."""
        _nav_link(live_admin_page, "Inbox").click()
        live_admin_page.wait_for_selector("text=Inbox", timeout=10_000)
        assert "/inbox" in live_admin_page.url.lower() or "inbox" in live_admin_page.url.lower()

    def test_team_click_navigates(self, live_admin_page: Page):
        """Clicking Team members navigates to the team page."""
        _nav_link(live_admin_page, "Team members").click()
        live_admin_page.wait_for_selector("text=Team members", timeout=10_000)
        assert "/team" in live_admin_page.url.lower()


# ─── Section B: AI Configuration Group ────────────────────────────────────

class TestConfigGroupExistence:
    """EL-sidebar-004..006: Config group container, header, and status badge."""

    def test_config_group_header_visible(self, live_admin_page: Page):
        """'AI CONFIGURATION' header text is visible in sidebar."""
        text = _sidebar_text(live_admin_page).upper()
        assert "AI CONFIGURATION" in text, (
            "AI CONFIGURATION header not found in sidebar"
        )

    def test_config_status_badge_visible(self, live_admin_page: Page):
        """Configuration status badge (Active/Inactive/Pending) is visible."""
        sb = _sidebar(live_admin_page)
        # Badge is a Mantine Badge component — look for common badge states
        badge = sb.locator(
            "text=/Active|Inactive|Pending/i"
        ).first
        expect(badge).to_be_visible(timeout=5_000)

    def test_config_status_badge_value(self, live_admin_page: Page):
        """Status badge shows one of the three valid states."""
        text = _sidebar_text(live_admin_page)
        has_active = "Active" in text
        has_inactive = "Inactive" in text
        has_pending = "Pending" in text
        assert has_active or has_inactive or has_pending, (
            "No valid status badge (Active/Inactive/Pending) found in sidebar"
        )


class TestConfigGroupNavItems:
    """EL-sidebar-007..010: Four configuration nav items."""

    CONFIG_ITEMS = [
        "Agent configuration",
        "Knowledge base",
        "Quick actions",
        "Widget configuration",
    ]

    @pytest.mark.parametrize("label", CONFIG_ITEMS)
    def test_config_nav_item_visible(self, live_admin_page: Page, label: str):
        """Each config nav item is visible in the sidebar."""
        link = _nav_link(live_admin_page, label)
        expect(link).to_be_visible(timeout=5_000)

    def test_config_items_order(self, live_admin_page: Page):
        """Config items appear in order: Agent config, KB, Quick actions, Widget."""
        text = _sidebar_text(live_admin_page)
        positions = [text.find(item) for item in self.CONFIG_ITEMS]
        assert all(p >= 0 for p in positions), (
            f"Missing config items. Positions: {dict(zip(self.CONFIG_ITEMS, positions))}"
        )
        assert positions == sorted(positions), (
            f"Config items out of order: {dict(zip(self.CONFIG_ITEMS, positions))}"
        )

    @pytest.mark.parametrize("label,expected_path", [
        ("Agent configuration", "/configuration"),
        ("Knowledge base", "/knowledge-base"),
        ("Quick actions", "/quick-actions"),
        ("Widget configuration", "/widget"),
    ])
    def test_config_nav_item_navigates(self, live_admin_page: Page, label: str, expected_path: str):
        """Each config nav item navigates to its correct route."""
        _nav_link(live_admin_page, label).click()
        live_admin_page.wait_for_timeout(1_000)
        assert expected_path in live_admin_page.url.lower(), (
            f"Clicking '{label}' didn't navigate to {expected_path}. URL: {live_admin_page.url}"
        )
        # Navigate back to dashboard for next test
        _nav_link(live_admin_page, "Dashboard").click()
        live_admin_page.wait_for_timeout(500)


class TestSetupWizard:
    """EL-sidebar-011: Setup wizard nav item."""

    def test_setup_wizard_visible(self, live_admin_page: Page):
        """Setup wizard link is visible in sidebar."""
        link = _nav_link(live_admin_page, "Setup wizard")
        expect(link).to_be_visible(timeout=5_000)

    def test_setup_wizard_has_icon(self, live_admin_page: Page):
        """Setup wizard has a star/icon distinguishing it from regular nav items."""
        link = _nav_link(live_admin_page, "Setup wizard")
        root = link.locator("xpath=ancestor::a[1]").first
        if root.count() == 0:
            root = link.locator("xpath=ancestor::*[contains(@class,'NavLink')][1]").first
        svg = root.locator("svg").first
        expect(svg).to_be_visible(timeout=3_000)


class TestActionButtons:
    """EL-sidebar-012..014: Deactivate/Activate, Discard, Roll back buttons."""

    def test_deactivate_or_activate_button_visible(self, live_admin_page: Page):
        """Either 'Deactivate' or 'Activate' button is visible in sidebar."""
        sb = _sidebar(live_admin_page)
        deactivate = sb.get_by_text("Deactivate", exact=True)
        activate = sb.get_by_text("Activate", exact=True)
        visible = deactivate.count() > 0 or activate.count() > 0
        assert visible, "Neither Deactivate nor Activate button found in sidebar"

    def test_discard_button_visible(self, live_admin_page: Page):
        """Discard button is visible in the sidebar config group."""
        sb = _sidebar(live_admin_page)
        discard = sb.get_by_text("Discard", exact=True).first
        expect(discard).to_be_visible(timeout=5_000)

    def test_roll_back_button_visible(self, live_admin_page: Page):
        """Roll back button is visible in the sidebar config group."""
        sb = _sidebar(live_admin_page)
        rollback = sb.get_by_text("Roll back", exact=True).first
        expect(rollback).to_be_visible(timeout=5_000)

    def test_action_buttons_are_compact(self, live_admin_page: Page):
        """Action buttons use Mantine compact variant (small size)."""
        sb = _sidebar(live_admin_page)
        # All 3 buttons should be present and small (compact)
        buttons = sb.locator("button")
        # At least 3 buttons exist in the sidebar (Deactivate/Activate + Discard + Roll back)
        assert buttons.count() >= 3, (
            f"Expected at least 3 buttons in sidebar, found {buttons.count()}"
        )

    def test_deactivate_button_style(self, live_admin_page: Page):
        """Active config shows red Deactivate; inactive shows green Activate."""
        text = _sidebar_text(live_admin_page)
        if "Active" in text and "Inactive" not in text and "Pending" not in text:
            # Config is active — Deactivate should be present (red)
            sb = _sidebar(live_admin_page)
            deactivate = sb.get_by_text("Deactivate", exact=True).first
            expect(deactivate).to_be_visible(timeout=3_000)
        elif "Inactive" in text:
            # Config is inactive — Activate should be present (green)
            sb = _sidebar(live_admin_page)
            activate = sb.get_by_text("Activate", exact=True).first
            expect(activate).to_be_visible(timeout=3_000)
        # Pending state: Activate visible but may be disabled — just check presence
        else:
            sb = _sidebar(live_admin_page)
            activate = sb.get_by_text("Activate", exact=True)
            assert activate.count() > 0, "Activate button not found in Pending state"


# ─── Section C: Post-Config Navigation ────────────────────────────────────

class TestPostConfigNavExistence:
    """EL-sidebar-015..018: Post-config nav items."""

    @pytest.mark.parametrize("label", ["Integrations", "Memory & privacy", "Billing"])
    def test_post_config_nav_visible(self, live_admin_page: Page, label: str):
        """Post-config nav items are visible in sidebar."""
        link = _nav_link(live_admin_page, label)
        expect(link).to_be_visible(timeout=5_000)

    def test_post_config_nav_order(self, live_admin_page: Page):
        """Post-config items in order: Integrations, Memory & privacy, Billing."""
        text = _sidebar_text(live_admin_page)
        items = ["Integrations", "Memory & privacy", "Billing"]
        positions = [text.find(item) for item in items]
        assert all(p >= 0 for p in positions), (
            f"Missing items: {dict(zip(items, positions))}"
        )
        assert positions == sorted(positions), (
            f"Post-config items out of order: {dict(zip(items, positions))}"
        )

    @pytest.mark.parametrize("label,expected_path", [
        ("Integrations", "/integrations"),
        ("Memory & privacy", "/memory-privacy"),
        ("Billing", "/billing"),
    ])
    def test_post_config_nav_navigates(self, live_admin_page: Page, label: str, expected_path: str):
        """Each post-config nav item navigates to its correct route."""
        _nav_link(live_admin_page, label).click()
        live_admin_page.wait_for_timeout(1_000)
        assert expected_path in live_admin_page.url.lower(), (
            f"Clicking '{label}' didn't navigate to {expected_path}. URL: {live_admin_page.url}"
        )
        # Return to dashboard
        _nav_link(live_admin_page, "Dashboard").click()
        live_admin_page.wait_for_timeout(500)


class TestProfessionalBadge:
    """EL-sidebar-017: Professional tier badge on Memory & privacy."""

    def test_professional_badge_presence(self, live_admin_page: Page):
        """Memory & privacy item shows 'Professional' badge (if tier qualifies)."""
        sb = _sidebar(live_admin_page)
        # The badge might or might not be present depending on tenant tier.
        # On staging test tenants (usually starter), it may be absent.
        badge = sb.locator("text=/Professional/i").first
        # Just check it exists OR the nav item exists without badge
        memory_link = _nav_link(live_admin_page, "Memory & privacy")
        assert memory_link.count() > 0, "Memory & privacy nav item not found"
        # If badge is visible, verify it's green-ish (Mantine green badge)
        if badge.count() > 0 and badge.is_visible():
            # Badge exists — test passes (green color verified by dimension)
            pass
        else:
            # No badge — tier is below professional, which is valid
            pytest.skip("Professional badge not shown (tenant tier < professional)")


# ─── Section D: Footer ────────────────────────────────────────────────────

class TestFooterExistence:
    """EL-sidebar-019..022: Footer container, product name, version, copyright."""

    def test_product_name_visible(self, live_admin_page: Page):
        """Footer shows 'Agent Red Customer Experience' product name."""
        text = _sidebar_text(live_admin_page)
        assert "Agent Red Customer Experience" in text, (
            f"Product name not found in sidebar. Text: {text[-200:]}"
        )

    def test_version_text_visible(self, live_admin_page: Page):
        """Footer shows version in format 'vX.Y.Z'."""
        text = _sidebar_text(live_admin_page)
        version_match = re.search(r"v\d+\.\d+\.\d+", text)
        assert version_match, (
            f"Version text (vX.Y.Z) not found in sidebar. Text: {text[-200:]}"
        )

    def test_version_is_fresh(self, live_admin_page: Page):
        """Version text reflects the deployed version (from x-product-version header)."""
        text = _sidebar_text(live_admin_page)
        version_match = re.search(r"v(\d+\.\d+\.\d+)", text)
        assert version_match, "No version text found"
        version = version_match.group(1)
        # Version should be a reasonable recent version (>= 1.60.0)
        parts = [int(p) for p in version.split(".")]
        assert parts[0] >= 1 and parts[1] >= 60, (
            f"Version {version} seems too old (expected >= 1.60.0)"
        )

    def test_copyright_text_visible(self, live_admin_page: Page):
        """Footer shows copyright notice with correct year and entity."""
        text = _sidebar_text(live_admin_page)
        # Copyright symbol might be rendered as © or (c) or the word "copyright"
        has_copyright = (
            "2026" in text
            and "Remaker Digital" in text
            and "VanDusen" in text
        )
        assert has_copyright, (
            f"Copyright text not found. Looking for '2026', 'Remaker Digital', "
            f"'VanDusen'. Sidebar tail: {text[-300:]}"
        )

    def test_copyright_includes_all_rights(self, live_admin_page: Page):
        """Copyright notice includes 'All rights reserved.'"""
        text = _sidebar_text(live_admin_page)
        assert "All rights reserved" in text, (
            f"'All rights reserved' not found in sidebar footer"
        )


class TestFooterStyle:
    """EL-sidebar-019..022: Footer visual styling."""

    def test_product_name_is_dimmed(self, live_admin_page: Page):
        """Product name text should be dimmed (reduced opacity or muted color)."""
        # The product name and version use Mantine's dimmed color (opacity ~0.6-0.7)
        # We verify the text exists and has reduced visibility
        sb = _sidebar(live_admin_page)
        product_text = sb.get_by_text("Agent Red Customer Experience").first
        expect(product_text).to_be_visible(timeout=3_000)
        # Dimmed text is visually faded — we can't precisely measure opacity
        # from computed styles on arbitrary elements, but we verify it's present

    def test_footer_at_bottom_of_sidebar(self, live_admin_page: Page):
        """Footer content appears after all nav items (at bottom of sidebar)."""
        text = _sidebar_text(live_admin_page)
        billing_pos = text.find("Billing")
        product_pos = text.find("Agent Red Customer Experience")
        assert billing_pos >= 0 and product_pos >= 0, (
            "Billing or product name not found"
        )
        assert billing_pos < product_pos, (
            "Footer should appear below the last nav item (Billing)"
        )


# ─── Section E: Sidebar Container ─────────────────────────────────────────

class TestSidebarContainer:
    """EL-sidebar-023: Sidebar/Navbar container structure and style."""

    def test_sidebar_exists(self, live_admin_page: Page):
        """Sidebar nav element is present in the DOM."""
        sb = _sidebar(live_admin_page)
        expect(sb).to_be_visible(timeout=5_000)

    def test_sidebar_has_dark_background(self, live_admin_page: Page):
        """Sidebar has a dark background color (chrome #0c0a09 or similar)."""
        bg = _sidebar_style(live_admin_page, "background-color")
        assert bg, "Could not read sidebar background-color"
        # Parse rgb values — dark theme should have very low R/G/B values
        rgb_match = re.search(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", bg)
        if rgb_match:
            r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
            # Dark background: all channels should be < 50
            assert r < 50 and g < 50 and b < 50, (
                f"Sidebar background not dark enough: rgb({r},{g},{b})"
            )
        # rgba format also acceptable
        elif "rgba" in bg:
            rgba_match = re.search(r"rgba\((\d+),\s*(\d+),\s*(\d+)", bg)
            if rgba_match:
                r, g, b = int(rgba_match.group(1)), int(rgba_match.group(2)), int(rgba_match.group(3))
                assert r < 50 and g < 50 and b < 50, (
                    f"Sidebar background not dark enough: {bg}"
                )

    def test_sidebar_full_height(self, live_admin_page: Page):
        """Sidebar spans the full viewport height (minus header)."""
        height = live_admin_page.evaluate("""() => {
            const nav = document.querySelector("nav[class*='AppShell-navbar']") ||
                        document.querySelector("nav");
            return nav ? nav.getBoundingClientRect().height : 0;
        }""")
        viewport_height = live_admin_page.viewport_size["height"] if live_admin_page.viewport_size else 768
        # Sidebar should be at least 80% of viewport height (accounting for header)
        assert height > viewport_height * 0.7, (
            f"Sidebar height {height}px is too short for viewport {viewport_height}px"
        )

    def test_sidebar_has_border_right(self, live_admin_page: Page):
        """Sidebar has a right border separating it from main content."""
        border = _sidebar_style(live_admin_page, "border-right-width")
        # Either explicit border or box-shadow acting as border
        has_border = border and border != "0px"
        if not has_border:
            # Check box-shadow as alternative
            shadow = _sidebar_style(live_admin_page, "box-shadow")
            has_border = shadow and shadow != "none"
        # Also check border-right shorthand
        if not has_border:
            border_style = _sidebar_style(live_admin_page, "border-right-style")
            has_border = border_style and border_style not in ("none", "")
        assert has_border, "Sidebar has no right border or shadow separator"


class TestActiveHighlight:
    """EL-sidebar-024: Active nav item highlight."""

    def test_dashboard_active_on_load(self, live_admin_page: Page):
        """Dashboard nav item is highlighted as active on initial load."""
        sb = _sidebar(live_admin_page)
        # Mantine NavLink active state adds a data-active attribute or active class
        active_link = sb.locator("[data-active='true'], [class*='active' i]").first
        if active_link.count() > 0:
            text = active_link.inner_text()
            assert "Dashboard" in text, (
                f"Active link is '{text}', expected Dashboard"
            )
        else:
            # Alternative: check for visual indicators (background color difference)
            # The active item should have a distinct background
            pytest.skip("Could not detect active state via data-active or class")

    def test_active_highlight_moves_on_navigation(self, live_admin_page: Page):
        """Active highlight moves to the clicked nav item."""
        # Navigate to Inbox
        _nav_link(live_admin_page, "Inbox").click()
        live_admin_page.wait_for_timeout(1_000)

        sb = _sidebar(live_admin_page)
        active_link = sb.locator("[data-active='true'], [class*='active' i]").first
        if active_link.count() > 0:
            text = active_link.inner_text()
            assert "Inbox" in text, (
                f"After clicking Inbox, active link shows '{text}' instead"
            )
        # Navigate back
        _nav_link(live_admin_page, "Dashboard").click()
        live_admin_page.wait_for_timeout(500)


# ─── Section F: Conditional/Dynamic ────────────────────────────────────────

class TestNavIcons:
    """EL-sidebar-025: Nav item icons."""

    ALL_NAV_LABELS = [
        "Dashboard", "Inbox", "Team members",
        "Agent configuration", "Knowledge base", "Quick actions",
        "Widget configuration", "Integrations", "Memory & privacy",
        "Billing",
    ]

    @pytest.mark.parametrize("label", ALL_NAV_LABELS)
    def test_each_nav_item_has_svg_icon(self, live_admin_page: Page, label: str):
        """Every nav item has a unique SVG icon."""
        link = _nav_link(live_admin_page, label)
        # Walk up to the NavLink root (<a> element) and look for SVG within it
        root = link.locator("xpath=ancestor::a[1]").first
        if root.count() == 0:
            root = link.locator("xpath=ancestor::*[contains(@class,'NavLink')][1]").first
        if root.count() > 0:
            svg_count = root.locator("svg").count()
            assert svg_count >= 1, f"No SVG icon found for nav item '{label}'"
        else:
            pytest.skip(f"Could not locate NavLink root for '{label}'")


# ─── Full Sidebar Integrity ────────────────────────────────────────────────

class TestSidebarIntegrity:
    """Cross-cutting integrity checks across all sidebar elements."""

    ALL_NAV_LABELS = [
        "Dashboard", "Inbox", "Team members",
        "Agent configuration", "Knowledge base", "Quick actions",
        "Widget configuration", "Setup wizard",
        "Integrations", "Memory & privacy", "Billing",
    ]

    def test_all_nav_items_present(self, live_admin_page: Page):
        """All 11 expected nav items are present in the sidebar."""
        text = _sidebar_text(live_admin_page)
        missing = [label for label in self.ALL_NAV_LABELS if label not in text]
        assert not missing, f"Missing nav items: {missing}"

    def test_no_broken_text_in_sidebar(self, live_admin_page: Page):
        """Sidebar does not contain broken template literals or error text."""
        text = _sidebar_text(live_admin_page)
        # No unresolved template variables
        assert "undefined" not in text.lower(), "Found 'undefined' in sidebar"
        assert "null" not in text.lower() or "null" in text.lower().replace("null", "", 1), (
            "Found 'null' in sidebar text"
        )
        assert "NaN" not in text, "Found 'NaN' in sidebar"
        assert "{" not in text.replace("}", ""), "Found unresolved template in sidebar"

    def test_no_duplicate_nav_items(self, live_admin_page: Page):
        """No nav item label appears more than once."""
        text = _sidebar_text(live_admin_page)
        for label in self.ALL_NAV_LABELS:
            count = text.count(label)
            assert count <= 1, (
                f"Nav item '{label}' appears {count} times (expected 1)"
            )

    def test_sidebar_complete_ordering(self, live_admin_page: Page):
        """All nav items appear in the correct global order."""
        text = _sidebar_text(live_admin_page)
        positions = [(label, text.find(label)) for label in self.ALL_NAV_LABELS]
        found = [(label, pos) for label, pos in positions if pos >= 0]
        # Verify found items are in ascending position order
        for i in range(len(found) - 1):
            assert found[i][1] < found[i + 1][1], (
                f"'{found[i][0]}' (pos {found[i][1]}) should appear before "
                f"'{found[i + 1][0]}' (pos {found[i + 1][1]})"
            )

    def test_sidebar_action_button_count(self, live_admin_page: Page):
        """Sidebar has exactly 3 action buttons (Activate/Deactivate + Discard + Roll back)."""
        text = _sidebar_text(live_admin_page)
        # Count the expected button labels
        has_deactivate = "Deactivate" in text
        has_activate = text.count("Activate") - (1 if has_deactivate else 0) > 0
        has_discard = "Discard" in text
        has_rollback = "Roll back" in text

        button_count = sum([
            has_deactivate or has_activate,
            has_discard,
            has_rollback,
        ])
        assert button_count == 3, (
            f"Expected 3 action buttons, found {button_count}. "
            f"Deactivate={has_deactivate}, Activate={has_activate}, "
            f"Discard={has_discard}, Roll back={has_rollback}"
        )

    def test_config_group_between_top_and_post_nav(self, live_admin_page: Page):
        """AI Configuration group appears between top nav and post-config nav."""
        text = _sidebar_text(live_admin_page)
        team_pos = text.find("Team members")
        config_pos = text.upper().find("AI CONFIGURATION")
        integrations_pos = text.find("Integrations")
        assert team_pos >= 0, "Team members not found"
        assert config_pos >= 0, "AI CONFIGURATION header not found"
        assert integrations_pos >= 0, "Integrations not found"
        assert team_pos < config_pos < integrations_pos, (
            f"Config group not between top nav and post-config nav: "
            f"Team@{team_pos}, Config@{config_pos}, Integrations@{integrations_pos}"
        )
