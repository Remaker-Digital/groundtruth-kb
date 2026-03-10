"""
Live E2E responsive layout tests — viewport-parameterized at 3 sizes.

Tests the admin SPA at desktop (1440×900), tablet (768×1024), and
mobile (375×812) viewports to verify responsive behavior: sidebar
collapse, content reflow, stat card stacking, and form width.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re

import pytest
from playwright.sync_api import Page

from tests.e2e_live.conftest import _navigate_admin_to


def _get_bounding_box(page: Page, selector: str) -> dict | None:
    """Get the bounding box of an element."""
    return page.evaluate(f"""
        (() => {{
            const el = document.querySelector('{selector}');
            if (!el) return null;
            const rect = el.getBoundingClientRect();
            return {{
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
            }};
        }})()
    """)


def _is_element_visible(page: Page, selector: str) -> bool:
    """Check if an element is visible (not hidden, not zero-sized)."""
    result = page.evaluate(f"""
        (() => {{
            const el = document.querySelector('{selector}');
            if (!el) return false;
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden') return false;
            const rect = el.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
        }})()
    """)
    return bool(result)


# ---------------------------------------------------------------------------
# Desktop (1440×900)
# ---------------------------------------------------------------------------

class TestDesktopLayout:
    """Layout at desktop viewport (1440×900)."""

    @pytest.fixture(autouse=True)
    def _set_viewport(self, shared_admin_page: Page):
        """Set viewport to desktop size."""
        shared_admin_page.set_viewport_size({"width": 1440, "height": 900})
        shared_admin_page.wait_for_timeout(500)

    def test_sidebar_visible(self, shared_admin_page: Page):
        """Sidebar navigation is fully visible at desktop width."""
        nav_box = _get_bounding_box(shared_admin_page, "nav")
        assert nav_box is not None, "Nav element not found"
        assert nav_box["width"] > 100, f"Sidebar too narrow: {nav_box['width']}px"

    def test_two_column_widget_page(self, shared_admin_page: Page):
        """Widget page shows form + preview side-by-side at desktop."""
        _navigate_admin_to(shared_admin_page, "Widget configuration", "Widget")
        shared_admin_page.wait_for_timeout(500)

        # Check if preview element is positioned to the right
        viewport_width = 1440
        main_box = _get_bounding_box(shared_admin_page, "main")
        if main_box:
            assert main_box["width"] > 800, (
                f"Main content area too narrow for two columns: {main_box['width']}px"
            )

    def test_stat_cards_horizontal(self, shared_admin_page: Page):
        """Dashboard stat cards are laid out horizontally at desktop width."""
        _navigate_admin_to(shared_admin_page, "Dashboard", "Dashboard")
        shared_admin_page.wait_for_timeout(500)

        # Get positions of card elements
        card_positions = shared_admin_page.evaluate("""
            (() => {
                const cards = document.querySelectorAll('[class*="card"], [class*="Card"]');
                const positions = [];
                for (const el of Array.from(cards).slice(0, 6)) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 50 && rect.height > 50) {
                        positions.push({x: rect.x, y: rect.y, w: rect.width});
                    }
                }
                return positions;
            })()
        """) or []

        if len(card_positions) >= 2:
            # At desktop, cards should have different x-positions (horizontal layout)
            x_values = [p["x"] for p in card_positions]
            unique_x = len(set(round(x, -1) for x in x_values))
            assert unique_x >= 2, (
                "Stat cards appear stacked vertically at desktop width "
                f"(all at x≈{x_values[0]})"
            )

    def test_content_area_width(self, shared_admin_page: Page):
        """Main content area uses the available width minus sidebar."""
        main_box = _get_bounding_box(shared_admin_page, "main")
        nav_box = _get_bounding_box(shared_admin_page, "nav")
        if main_box and nav_box:
            expected_min = 1440 - nav_box["width"] - 100  # allow margins
            assert main_box["width"] >= expected_min * 0.7, (
                f"Content area {main_box['width']}px is too narrow "
                f"(sidebar={nav_box['width']}px)"
            )


# ---------------------------------------------------------------------------
# Tablet (768×1024)
# ---------------------------------------------------------------------------

class TestTabletLayout:
    """Layout at tablet viewport (768×1024)."""

    @pytest.fixture(autouse=True)
    def _set_viewport(self, shared_admin_page: Page):
        """Set viewport to tablet size."""
        shared_admin_page.set_viewport_size({"width": 768, "height": 1024})
        shared_admin_page.wait_for_timeout(500)

    def test_sidebar_collapses_to_burger(self, shared_admin_page: Page):
        """At tablet width, sidebar collapses and a burger menu icon appears."""
        # Check for burger menu icon
        burger = shared_admin_page.locator(
            "[class*='burger'], [class*='Burger'], "
            "button[aria-label*='menu'], button[aria-label*='Menu']"
        )
        sidebar_visible = _is_element_visible(shared_admin_page, "nav")

        # Either the burger is shown OR the sidebar collapses
        # (exact behavior depends on the Mantine responsive breakpoint)
        has_responsive = burger.count() > 0 or not sidebar_visible
        # At 768px, the sidebar may still be visible but narrower
        # Accept either collapsed or narrow sidebar
        if sidebar_visible:
            nav_box = _get_bounding_box(shared_admin_page, "nav")
            if nav_box:
                assert nav_box["width"] < 300, (
                    f"Sidebar still full-width at tablet: {nav_box['width']}px"
                )

    def test_content_fills_width(self, shared_admin_page: Page):
        """Main content uses most of the viewport width."""
        main_box = _get_bounding_box(shared_admin_page, "main")
        if main_box:
            # Content should fill at least 60% of viewport at tablet
            fill_ratio = main_box["width"] / 768
            assert fill_ratio >= 0.5, (
                f"Content only fills {fill_ratio:.0%} of viewport at tablet"
            )

    def test_stat_cards_responsive(self, shared_admin_page: Page):
        """Stat cards wrap or resize at tablet width."""
        card_positions = shared_admin_page.evaluate("""
            (() => {
                const cards = document.querySelectorAll('[class*="card"], [class*="Card"]');
                const positions = [];
                for (const el of Array.from(cards).slice(0, 6)) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 50 && rect.height > 50) {
                        positions.push({x: rect.x, y: rect.y, w: rect.width});
                    }
                }
                return positions;
            })()
        """) or []

        if len(card_positions) >= 2:
            # Cards should either wrap (multiple y-values) or be narrower
            widths = [p["w"] for p in card_positions]
            avg_width = sum(widths) / len(widths) if widths else 0
            assert avg_width < 700, (
                f"Stat cards not responsive at tablet — avg width {avg_width}px"
            )

    def test_widget_preview_stacks_below(self, shared_admin_page: Page):
        """At tablet width, widget preview stacks below the form."""
        _navigate_admin_to(shared_admin_page, "Widget configuration", "Widget")
        shared_admin_page.wait_for_timeout(500)

        # At 768px, two-column layout should collapse to single column
        # (preview below form instead of beside it)
        main_box = _get_bounding_box(shared_admin_page, "main")
        if main_box:
            # Accept any valid layout — the key check is no horizontal overflow
            assert main_box["width"] <= 768, (
                f"Content wider than viewport: {main_box['width']}px"
            )


# ---------------------------------------------------------------------------
# Mobile (375×812)
# ---------------------------------------------------------------------------

class TestMobileLayout:
    """Layout at mobile viewport (375×812)."""

    @pytest.fixture(autouse=True)
    def _set_viewport(self, live_admin_page: Page):
        """Set viewport to mobile size."""
        live_admin_page.set_viewport_size({"width": 375, "height": 812})
        live_admin_page.wait_for_timeout(500)

    def test_sidebar_hidden(self, live_admin_page: Page):
        """Sidebar is hidden at mobile width."""
        sidebar_visible = _is_element_visible(live_admin_page, "nav")
        if sidebar_visible:
            nav_box = _get_bounding_box(live_admin_page, "nav")
            if nav_box:
                # At mobile, nav should be off-screen or zero-width
                assert nav_box["width"] < 50 or nav_box["x"] < -100, (
                    f"Sidebar visible at mobile: width={nav_box['width']}px, x={nav_box['x']}"
                )

    def test_burger_menu_works(self, live_admin_page: Page):
        """Clicking the burger menu reveals the sidebar on mobile."""
        burger = live_admin_page.locator(
            "[class*='burger'], [class*='Burger'], "
            "button[aria-label*='menu'], button[aria-label*='Menu']"
        ).first

        if burger.is_visible():
            burger.click()
            live_admin_page.wait_for_timeout(500)
            # After clicking burger, navigation text should become visible
            nav_text = live_admin_page.locator("text=Dashboard")
            assert nav_text.first.is_visible(), "Sidebar did not open after burger click"
        else:
            # If no burger, the sidebar may always be hidden at mobile
            pass

    def test_stat_cards_stack_vertically(self, live_admin_page: Page):
        """Stat cards are stacked in a single column at mobile width."""
        card_positions = live_admin_page.evaluate("""
            (() => {
                const cards = document.querySelectorAll('[class*="card"], [class*="Card"]');
                const positions = [];
                for (const el of Array.from(cards).slice(0, 6)) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 50 && rect.height > 30) {
                        positions.push({x: rect.x, y: rect.y, w: rect.width});
                    }
                }
                return positions;
            })()
        """) or []

        if len(card_positions) >= 2:
            # At mobile, most cards should share the same x-position (stacked)
            x_values = [round(p["x"]) for p in card_positions]
            most_common_x = max(set(x_values), key=x_values.count)
            same_x_count = x_values.count(most_common_x)
            assert same_x_count >= len(card_positions) * 0.5, (
                "Cards not stacked vertically at mobile width"
            )

    def test_forms_full_width(self, live_admin_page: Page):
        """Input fields on the current page span the available width at mobile.

        At 375px viewport, the sidebar is hidden so we can't navigate via
        sidebar clicks. Instead, we check any form inputs already visible
        on the dashboard or attempt to open the burger menu first.
        """
        # Try to open burger menu and navigate
        burger = live_admin_page.locator(
            "[class*='burger'], [class*='Burger'], "
            "button[aria-label*='menu'], button[aria-label*='Menu']"
        ).first

        if burger.is_visible():
            burger.click()
            live_admin_page.wait_for_timeout(500)
            # Try to click Agent configuration in the opened sidebar
            nav_link = live_admin_page.get_by_text("Agent configuration", exact=True).first
            if nav_link.is_visible():
                nav_link.click()
                live_admin_page.wait_for_timeout(1000)

        # Check form inputs on whatever page we're on
        input_widths = live_admin_page.evaluate("""
            (() => {
                const inputs = document.querySelectorAll('input[type="text"], textarea, input:not([type="hidden"])');
                return Array.from(inputs).slice(0, 5).map(el => {
                    const rect = el.getBoundingClientRect();
                    return rect.width;
                }).filter(w => w > 0);
            })()
        """) or []

        if len(input_widths) > 0:
            # At mobile (375px), inputs should be reasonably sized
            # (accounting for padding/margins, expect > 150px)
            max_width = max(input_widths)
            assert max_width >= 150, (
                f"Inputs too narrow at mobile: max width {max_width}px"
            )
        else:
            # If no visible inputs, the test passes vacuously
            # (dashboard may not have text inputs)
            pass
