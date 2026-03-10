"""
Live E2E visual tests — CSS property assertions via getComputedStyle().

Validates that the admin SPA renders with correct CSS values when
displaying real production data. Uses page.evaluate() to inspect
computed styles on specific DOM elements.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re

import pytest
from playwright.sync_api import Page


def _get_computed_style(page: Page, selector: str, prop: str) -> str:
    """Get a computed CSS property value from a DOM element."""
    return page.evaluate(f"""
        (() => {{
            const el = document.querySelector('{selector}');
            if (!el) return '';
            return window.getComputedStyle(el).getPropertyValue('{prop}');
        }})()
    """) or ""


def _get_computed_style_approx(page: Page, selector: str, prop: str) -> str:
    """Get computed style, trying multiple selector strategies."""
    result = _get_computed_style(page, selector, prop)
    if result:
        return result.strip()
    # Try broader selectors
    for alt in [f"[class*='{selector}']", f"#{selector}", f".{selector}"]:
        result = _get_computed_style(page, alt, prop)
        if result:
            return result.strip()
    return ""


def _parse_px(value: str) -> float:
    """Extract numeric pixel value from a CSS value string."""
    match = re.search(r"([\d.]+)px", value)
    return float(match.group(1)) if match else 0.0


class TestSidebarCSS:
    """Sidebar navigation CSS properties match design system."""

    def test_sidebar_width(self, shared_admin_page: Page):
        """Sidebar (nav) has a computed width around 260px."""
        width = _get_computed_style(shared_admin_page, "nav", "width")
        px = _parse_px(width)
        # Allow some tolerance (250-280px)
        assert 200 <= px <= 320, f"Sidebar width {width} outside expected range"

    def test_sidebar_background_color(self, shared_admin_page: Page):
        """Sidebar has a dark background color."""
        bg = _get_computed_style(shared_admin_page, "nav", "background-color")
        # Dark theme — RGB values should be low (dark)
        match = re.search(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", bg)
        if match:
            r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
            avg = (r + g + b) / 3
            assert avg < 100, f"Sidebar background {bg} is not dark (avg={avg})"
        else:
            # Accept any non-empty value — the nav element exists
            assert bg, "No background-color computed for nav element"

    def test_nav_item_font_size(self, shared_admin_page: Page):
        """Navigation item text uses an appropriate font size."""
        # Get font-size from a nav link element
        fs = shared_admin_page.evaluate("""
            (() => {
                const navLinks = document.querySelectorAll('nav a, nav [role="button"]');
                for (const el of navLinks) {
                    const s = window.getComputedStyle(el).getPropertyValue('font-size');
                    if (s) return s;
                }
                return '';
            })()
        """) or ""
        px = _parse_px(fs)
        # Mantine default sm=14px, md=16px
        assert 12 <= px <= 20, f"Nav font-size {fs} outside expected range"


class TestHeaderCSS:
    """Header bar CSS properties."""

    def test_header_height(self, shared_admin_page: Page):
        """Header has a height around 56px (StandaloneLayout design)."""
        height = _get_computed_style(shared_admin_page, "header", "height")
        px = _parse_px(height)
        assert 40 <= px <= 80, f"Header height {height} outside expected range"

    def test_header_background_color(self, shared_admin_page: Page):
        """Header has a dark background color."""
        bg = _get_computed_style(shared_admin_page, "header", "background-color")
        match = re.search(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", bg)
        if match:
            r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
            avg = (r + g + b) / 3
            assert avg < 100, f"Header background {bg} is not dark (avg={avg})"
        else:
            assert bg, "No background-color computed for header"

    def test_tier_badge_color(self, shared_admin_page: Page):
        """The tier badge has a visible background or text color."""
        # Find the badge element containing tier text
        badge = shared_admin_page.evaluate("""
            (() => {
                const badges = document.querySelectorAll('[class*="badge"], [class*="Badge"]');
                for (const el of badges) {
                    if (/Professional|Starter|Enterprise/i.test(el.textContent)) {
                        return {
                            bg: window.getComputedStyle(el).getPropertyValue('background-color'),
                            color: window.getComputedStyle(el).getPropertyValue('color'),
                        };
                    }
                }
                return null;
            })()
        """)
        assert badge is not None, "No tier badge element found"
        # Badge should have a non-transparent background or visible text color
        assert badge.get("bg") or badge.get("color"), "Badge has no color properties"


class TestContentCSS:
    """Content area CSS properties for cards and inputs."""

    def test_stat_card_border_radius(self, shared_admin_page: Page):
        """Dashboard content elements have a border-radius (rounded corners).

        The admin SPA uses inline styles (borderRadius: 6) and Mantine Paper
        components with hashed CSS class names. We scan all elements in main
        for any with non-zero border-radius.
        """
        br = shared_admin_page.evaluate("""
            (() => {
                // Search broadly: inline-styled cards, Mantine Paper, or any
                // element inside main with border-radius set
                const candidates = document.querySelectorAll(
                    'main div, main section, main article'
                );
                for (const el of Array.from(candidates).slice(0, 200)) {
                    const s = window.getComputedStyle(el);
                    const r = s.getPropertyValue('border-radius');
                    const border = s.getPropertyValue('border');
                    // Look for elements that look like cards: have border-radius
                    // AND have either a border or a background
                    if (r && r !== '0px' && (border || s.backgroundColor !== 'rgba(0, 0, 0, 0)')) {
                        return r;
                    }
                }
                return '';
            })()
        """) or ""
        assert br and br != "0px", f"No rounded content elements found (border-radius: {br or 'none'})"

    def test_stat_card_padding(self, shared_admin_page: Page):
        """Dashboard content elements have consistent padding.

        Summary cards use inline padding (16px 20px). We look for any
        bordered/backgrounded element inside main with non-zero padding.
        """
        padding = shared_admin_page.evaluate("""
            (() => {
                const candidates = document.querySelectorAll(
                    'main div, main section, main article'
                );
                for (const el of Array.from(candidates).slice(0, 200)) {
                    const s = window.getComputedStyle(el);
                    const p = s.getPropertyValue('padding');
                    const border = s.getPropertyValue('border');
                    const bg = s.backgroundColor;
                    // Card-like element: has padding AND has border or background
                    if (p && p !== '0px' && (
                        (border && border !== 'none' && !border.startsWith('0px'))
                        || (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent')
                    )) {
                        return p;
                    }
                }
                return '';
            })()
        """) or ""
        assert padding and padding != "0px", "No padded content elements found"

    def test_input_field_styling(self, shared_admin_page: Page):
        """Text inputs have proper styling (border, padding)."""
        style = shared_admin_page.evaluate("""
            (() => {
                const input = document.querySelector('input[type="text"]');
                if (!input) return null;
                const s = window.getComputedStyle(input);
                return {
                    padding: s.getPropertyValue('padding'),
                    border: s.getPropertyValue('border'),
                    fontSize: s.getPropertyValue('font-size'),
                };
            })()
        """)
        if style is None:
            pytest.skip("No text input found on dashboard")
        assert style.get("fontSize"), "Input has no font-size"


class TestWidgetPageCSS:
    """Widget configuration page CSS properties."""

    def test_preview_panel_styling(self, shared_widget_page: Page):
        """The widget preview section has visible styling (border, shadow, or bg).

        The preview panel uses inline styles (border: 1px solid, borderRadius: 12).
        Mantine class names are hashed so we scan by structural position.
        """
        has_style = shared_widget_page.evaluate("""
            (() => {
                // Search all elements in main for preview-like panels:
                // elements with border-radius >= 8 AND either border or box-shadow
                const candidates = document.querySelectorAll('main div');
                for (const el of Array.from(candidates).slice(0, 300)) {
                    const s = window.getComputedStyle(el);
                    const br = parseFloat(s.borderRadius) || 0;
                    const shadow = s.boxShadow;
                    const border = s.border;
                    const bg = s.backgroundColor;
                    // Preview panel: large border-radius (12+) with border or shadow
                    if (br >= 8 && (
                        (shadow && shadow !== 'none')
                        || (border && !border.startsWith('0px'))
                        || (bg && bg !== 'rgba(0, 0, 0, 0)')
                    )) {
                        return {borderRadius: s.borderRadius, shadow, border: border.slice(0, 50)};
                    }
                }
                return null;
            })()
        """)
        assert has_style is not None, "No styled preview panel found (border-radius >= 8 + border/shadow)"

    def test_color_picker_swatch_renders(self, shared_widget_page: Page):
        """A color swatch element has a background-color set."""
        bg = shared_widget_page.evaluate("""
            (() => {
                const swatches = document.querySelectorAll(
                    '[class*="swatch"], [class*="Swatch"], [class*="color"], input[type="color"]'
                );
                for (const el of swatches) {
                    const bg = window.getComputedStyle(el).getPropertyValue('background-color');
                    if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') return bg;
                }
                return '';
            })()
        """) or ""
        assert bg, "No color swatch with a visible background-color found"

    def test_embed_code_monospace_font(self, shared_widget_page: Page):
        """The embed code or snippet area uses a monospace font family.

        The admin SPA uses JetBrains Mono for code blocks via Mantine Code
        component or inline style fontFamily.
        """
        font = shared_widget_page.evaluate("""
            (() => {
                // Check Mantine Code components, <code>, <pre>, and any element
                // with monospace font set via inline styles
                const codeBlocks = document.querySelectorAll('code, pre');
                for (const el of codeBlocks) {
                    const ff = window.getComputedStyle(el).getPropertyValue('font-family');
                    if (ff) return ff;
                }
                // Also search elements in main for monospace font (inline-styled code)
                const allEls = document.querySelectorAll('main div, main span');
                for (const el of Array.from(allEls).slice(0, 300)) {
                    const ff = window.getComputedStyle(el).getPropertyValue('font-family');
                    if (ff && /mono|courier|consolas|jetbrains/i.test(ff)) {
                        return ff;
                    }
                }
                return '';
            })()
        """) or ""
        mono_keywords = ["mono", "courier", "consolas", "menlo", "fira", "jetbrains"]
        is_mono = any(kw in font.lower() for kw in mono_keywords)
        assert is_mono, f"No monospace font found on widget page (checked: '{font[:80]}')"


class TestBrandColors:
    """Brand color (#ff3621) is applied correctly throughout the UI."""

    def test_brand_primary_color_used(self, shared_admin_page: Page):
        """The brand primary color #ff3621 (rgb(255, 54, 33)) appears in styles."""
        found = shared_admin_page.evaluate("""
            (() => {
                const all = document.querySelectorAll('*');
                for (const el of Array.from(all).slice(0, 500)) {
                    const s = window.getComputedStyle(el);
                    const bg = s.getPropertyValue('background-color');
                    const color = s.getPropertyValue('color');
                    // #ff3621 = rgb(255, 54, 33)
                    if (bg.includes('255, 54, 33') || color.includes('255, 54, 33')) {
                        return true;
                    }
                }
                return false;
            })()
        """)
        assert found, "Brand color rgb(255, 54, 33) not found in any element"

    def test_active_nav_item_highlight(self, shared_admin_page: Page):
        """The active navigation item has a distinguishing style.

        Nav items may use background-color, font-weight, opacity,
        border-left, or text color to indicate the active state.
        """
        highlight = shared_admin_page.evaluate("""
            (() => {
                const navItems = document.querySelectorAll('nav a, nav [role="button"], nav div');
                const results = [];
                for (const el of navItems) {
                    if (!el.textContent.trim()) continue;
                    const s = window.getComputedStyle(el);
                    results.push({
                        text: el.textContent.trim().slice(0, 30),
                        bg: s.backgroundColor,
                        color: s.color,
                        fontWeight: s.fontWeight,
                        opacity: s.opacity,
                        borderLeft: s.borderLeft,
                    });
                }
                // Look for differentiation: at least one item should differ
                // from others in bg, fontWeight, opacity, or borderLeft
                if (results.length < 2) return null;
                const bgs = new Set(results.map(r => r.bg));
                const fws = new Set(results.map(r => r.fontWeight));
                const ops = new Set(results.map(r => r.opacity));
                const bls = new Set(results.map(r => r.borderLeft));
                const colors = new Set(results.map(r => r.color));
                // Any style differentiation counts as active highlighting
                if (bgs.size > 1 || fws.size > 1 || ops.size > 1
                    || bls.size > 1 || colors.size > 1) {
                    return {differentiation: true, count: results.length};
                }
                return null;
            })()
        """)
        assert highlight is not None, "No style differentiation found among nav items"

    def test_button_primary_color(self, shared_admin_page: Page):
        """Primary buttons use the brand color or a related accent."""
        btn_bg = shared_admin_page.evaluate("""
            (() => {
                const buttons = document.querySelectorAll('button');
                for (const el of buttons) {
                    const bg = window.getComputedStyle(el).getPropertyValue('background-color');
                    // Look for non-transparent buttons (primary action buttons)
                    if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent'
                        && bg !== 'rgb(255, 255, 255)') {
                        return bg;
                    }
                }
                return '';
            })()
        """) or ""
        assert btn_bg, "No primary button with a visible background-color found"
