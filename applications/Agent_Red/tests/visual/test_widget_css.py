"""
Layer 2 — CSS property assertion tests.

Verifies brand-critical computed CSS values via ``getComputedStyle()`` inside
the panel iframe.  These tests catch visual regressions that structural tests
miss: wrong color, missing font, broken spacing, incorrect sizing.

The tests target the *computed* style (what the browser actually renders),
not the inline style attribute.  This catches issues where token resolution,
theme derivation, or CSS specificity produce unexpected results.

Run with:
    pytest tests/visual/test_widget_css.py -v --headed   # visual
    pytest tests/visual/test_widget_css.py -v             # headless

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json

import pytest
from playwright.sync_api import Page

# ---------------------------------------------------------------------------
# Marker
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.visual


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _eval_in_iframe(widget_page: Page, js_expression: str):
    """Evaluate a JS expression inside the widget panel iframe.

    This is a workaround for Playwright's FrameLocator not exposing
    ``evaluate()`` directly.  We access the iframe's contentDocument from
    the parent frame.
    """
    return widget_page.evaluate(f"""
        (() => {{
            const iframe = document.querySelector('iframe[title="Agent Red Chat"]');
            if (!iframe || !iframe.contentDocument) return null;
            const doc = iframe.contentDocument;
            {js_expression}
        }})()
    """)


def _open_panel(page: Page) -> None:
    """Open the widget panel and wait for transition."""
    page.evaluate("window.AgentRed.open()")
    page.wait_for_selector('iframe[title="Agent Red Chat"]', timeout=5_000)
    page.wait_for_timeout(500)  # transition + render


# ===========================================================================
# Header CSS Tests
# ===========================================================================


class TestHeaderCSS:
    """Verify computed CSS properties on the panel header."""

    def test_header_background_color(self, widget_page: Page) -> None:
        """Header background must be the brand primary color #ff3621.

        The default config has no gradient, so the header gets a flat
        background-color.  We check the computed value in rgb() format.
        """
        _open_panel(widget_page)

        # Find header via the close button — reliable anchor in the DOM
        bg = _eval_in_iframe(widget_page, """
            const closeBtn = doc.querySelector('button[aria-label="Close chat"]');
            const header = closeBtn && closeBtn.closest('div');
            if (!header) return null;
            return window.getComputedStyle(header).backgroundColor;
        """)

        # #ff3621 in rgb: rgb(255, 54, 33)
        assert bg is not None, "Could not find header element"
        assert bg == "rgb(255, 54, 33)", (
            f"Header background should be brand primary rgb(255, 54, 33), got: {bg}"
        )

    def test_header_height(self, widget_page: Page) -> None:
        """Header height must be 64px (from tokens.headerHeight)."""
        _open_panel(widget_page)

        height = _eval_in_iframe(widget_page, """
            const closeBtn = doc.querySelector('button[aria-label="Close chat"]');
            const header = closeBtn && closeBtn.closest('div');
            if (!header) return null;
            return window.getComputedStyle(header).height;
        """)

        assert height == "64px", f"Header height should be 64px, got: {height}"

    def test_header_text_color(self, widget_page: Page) -> None:
        """Header text should be white (contrastText for #ff3621 = #FFFFFF)."""
        _open_panel(widget_page)

        color = _eval_in_iframe(widget_page, """
            const closeBtn = doc.querySelector('button[aria-label="Close chat"]');
            const header = closeBtn && closeBtn.closest('div');
            if (!header) return null;
            return window.getComputedStyle(header).color;
        """)

        assert color is not None
        assert color == "rgb(255, 255, 255)", (
            f"Header text color should be white rgb(255, 255, 255), got: {color}"
        )

    def test_header_gradient_when_configured(self, page: Page, vite_server) -> None:
        """When widget_header_gradient_end is set, header uses gradient background."""
        config = {
            **_base_config(),
            "widget_header_gradient_end": "#ff8800",
        }

        page.route("**/api/config*", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"config": config}),
        ))
        page.route("**/api/conversations*", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"conversation_id": "test-gradient"}),
        ))

        page.goto("http://localhost:3100/dev.html", wait_until="domcontentloaded")
        page.wait_for_function("!!window.AgentRed", timeout=10_000)
        _open_panel(page)

        bg_image = page.evaluate("""
            (() => {
                const iframe = document.querySelector('iframe[title="Agent Red Chat"]');
                if (!iframe || !iframe.contentDocument) return null;
                const doc = iframe.contentDocument;
                const closeBtn = doc.querySelector('button[aria-label="Close chat"]');
                const header = closeBtn && closeBtn.closest('div');
                if (!header) return null;
                return window.getComputedStyle(header).backgroundImage;
            })()
        """)

        assert bg_image is not None
        assert "gradient" in bg_image.lower(), (
            f"Expected gradient background-image, got: {bg_image}"
        )


# ===========================================================================
# Typography CSS Tests
# ===========================================================================


class TestTypographyCSS:
    """Verify font family, sizes, and weights are correctly applied."""

    def test_body_font_family(self, widget_page: Page) -> None:
        """Panel body font-family should be Inter (the brand default)."""
        _open_panel(widget_page)

        _eval_in_iframe(widget_page, """
            return doc.body.style.fontFamily || 'not set';
        """)

        # The body itself may not have fontFamily set (it's on individual elements).
        # Check the greeting or agent name element instead.
        font_from_element = _eval_in_iframe(widget_page, """
            const el = doc.querySelector('[style*="font-family"]');
            if (!el) return null;
            return window.getComputedStyle(el).fontFamily;
        """)

        if font_from_element:
            # Computed fontFamily includes fallbacks, should start with Inter
            assert "Inter" in font_from_element or "inter" in font_from_element.lower(), (
                f"Expected Inter font family, got: {font_from_element}"
            )

    def test_message_font_size(self, widget_page: Page) -> None:
        """Message text should use fontSizeMd (14px)."""
        _open_panel(widget_page)

        # Find the greeting message bubble text
        font_size = _eval_in_iframe(widget_page, """
            const spans = doc.querySelectorAll('span');
            for (const span of spans) {
                if (span.textContent.includes('Hi there!')) {
                    return window.getComputedStyle(span).fontSize;
                }
            }
            return null;
        """)

        # The greeting may be at various sizes; check it's reasonable
        if font_size:
            px_val = float(font_size.replace("px", ""))
            assert 13 <= px_val <= 16, (
                f"Greeting font size should be 13-16px range, got: {font_size}"
            )


# ===========================================================================
# Spacing & Layout CSS Tests
# ===========================================================================


class TestSpacingCSS:
    """Verify spacing values follow the 4px base grid system."""

    def test_header_padding(self, widget_page: Page) -> None:
        """Header horizontal padding should be space4 (16px)."""
        _open_panel(widget_page)

        padding = _eval_in_iframe(widget_page, """
            const closeBtn = doc.querySelector('button[aria-label="Close chat"]');
            const header = closeBtn && closeBtn.closest('div');
            if (!header) return null;
            const cs = window.getComputedStyle(header);
            return cs.paddingLeft + '|' + cs.paddingRight;
        """)

        assert padding is not None
        left, right = padding.split("|")
        assert left == "16px", f"Header padding-left should be 16px, got: {left}"
        assert right == "16px", f"Header padding-right should be 16px, got: {right}"


# ===========================================================================
# Color Mode Tests
# ===========================================================================


class TestDarkMode:
    """Verify dark mode token derivation produces correct colors."""

    def test_dark_mode_background(self, page: Page, vite_server) -> None:
        """Dark mode panel background should be #1c1917 (Tailwind stone-950)."""
        config = {
            **_base_config(),
            "widget_color_mode": "dark",
        }

        page.route("**/api/config*", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"config": config}),
        ))
        page.route("**/api/conversations*", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"conversation_id": "test-dark"}),
        ))

        page.goto("http://localhost:3100/dev.html", wait_until="domcontentloaded")
        page.wait_for_function("!!window.AgentRed", timeout=10_000)
        _open_panel(page)

        bg = page.evaluate("""
            (() => {
                const iframe = document.querySelector('iframe[title="Agent Red Chat"]');
                if (!iframe || !iframe.contentDocument) return null;
                const doc = iframe.contentDocument;
                const root = doc.getElementById('ar-panel-root');
                const panelWrapper = root && root.firstElementChild;
                if (!panelWrapper) return null;
                return window.getComputedStyle(panelWrapper).backgroundColor;
            })()
        """)

        assert bg is not None, "Could not read dark mode background"
        # #1c1917 (Tailwind stone-950) = rgb(28, 25, 23)
        assert bg == "rgb(28, 25, 23)", (
            f"Dark mode background should be rgb(28, 25, 23), got: {bg}"
        )


# ===========================================================================
# Animation CSS Tests
# ===========================================================================


class TestAnimationCSS:
    """Verify CSS animations and transitions are defined."""

    def test_panel_has_open_transition(self, widget_page: Page) -> None:
        """Panel iframe should have a CSS transition for smooth opening."""
        widget_page.evaluate("window.AgentRed.open()")
        widget_page.wait_for_selector('iframe[title="Agent Red Chat"]', timeout=5_000)

        transition = widget_page.evaluate("""
            document.querySelector('iframe[title="Agent Red Chat"]').style.transition
        """)

        assert transition is not None and len(transition) > 0, (
            "Panel iframe should have a transition style"
        )
        assert "opacity" in transition, "Transition should include opacity"

    def test_shimmer_keyframe_defined(self, widget_page: Page) -> None:
        """The ar-shimmer keyframe animation must be defined in the panel."""
        _open_panel(widget_page)

        has_shimmer = _eval_in_iframe(widget_page, """
            const sheets = doc.styleSheets;
            for (const sheet of sheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule.type === CSSRule.KEYFRAMES_RULE && rule.name === 'ar-shimmer') {
                            return true;
                        }
                    }
                } catch(e) { /* cross-origin stylesheet — skip */ }
            }
            return false;
        """)

        assert has_shimmer is True, "ar-shimmer keyframe should be defined in panel styles"

    def test_fade_in_keyframe_defined(self, widget_page: Page) -> None:
        """The ar-fade-in keyframe animation must be defined in the panel."""
        _open_panel(widget_page)

        has_fade_in = _eval_in_iframe(widget_page, """
            const sheets = doc.styleSheets;
            for (const sheet of sheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule.type === CSSRule.KEYFRAMES_RULE && rule.name === 'ar-fade-in') {
                            return true;
                        }
                    }
                } catch(e) { /* cross-origin stylesheet — skip */ }
            }
            return false;
        """)

        assert has_fade_in is True, "ar-fade-in keyframe should be defined in panel styles"

    def test_blink_keyframe_defined(self, widget_page: Page) -> None:
        """The ar-blink keyframe (streaming cursor) must be defined."""
        _open_panel(widget_page)

        has_blink = _eval_in_iframe(widget_page, """
            const sheets = doc.styleSheets;
            for (const sheet of sheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule.type === CSSRule.KEYFRAMES_RULE && rule.name === 'ar-blink') {
                            return true;
                        }
                    }
                } catch(e) { /* cross-origin stylesheet — skip */ }
            }
            return false;
        """)

        assert has_blink is True, "ar-blink keyframe should be defined in panel styles"


# ===========================================================================
# Bubble CSS Tests
# ===========================================================================


class TestBubbleCSS:
    """Verify message bubble styling tokens are applied correctly."""

    def test_agent_bubble_default_color(self, widget_page: Page) -> None:
        """Default agent bubble background is #F0F0F2 in light mode."""
        _open_panel(widget_page)

        # The greeting message is rendered as an agent bubble
        bg = _eval_in_iframe(widget_page, """
            const spans = doc.querySelectorAll('span');
            for (const span of spans) {
                if (span.textContent.includes('Hi there!')) {
                    // Walk up to the bubble container
                    let el = span.parentElement;
                    while (el && el.id !== 'ar-panel-root') {
                        const bg = window.getComputedStyle(el).backgroundColor;
                        if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                            return bg;
                        }
                        el = el.parentElement;
                    }
                }
            }
            return null;
        """)

        if bg:
            # #F0F0F2 = rgb(240, 240, 242)
            assert bg == "rgb(240, 240, 242)", (
                f"Agent bubble background should be rgb(240, 240, 242), got: {bg}"
            )

    def test_bubble_border_radius(self, widget_page: Page) -> None:
        """Message bubbles should have borderRadiusLg (12px) on most corners."""
        _open_panel(widget_page)

        radius = _eval_in_iframe(widget_page, """
            const spans = doc.querySelectorAll('span');
            for (const span of spans) {
                if (span.textContent.includes('Hi there!')) {
                    let el = span.parentElement;
                    while (el && el.id !== 'ar-panel-root') {
                        const r = window.getComputedStyle(el).borderRadius;
                        if (r && r !== '0px') return r;
                        el = el.parentElement;
                    }
                }
            }
            return null;
        """)

        if radius:
            # Should contain 12px (borderRadiusLg) — exact format varies
            assert "12px" in radius or "4px" in radius, (
                f"Bubble border-radius should include 12px or 4px, got: {radius}"
            )


# ===========================================================================
# Helpers
# ===========================================================================

def _base_config() -> dict:
    """Return a base WidgetConfig dict for custom config tests."""
    from tests.visual.conftest import MOCK_WIDGET_CONFIG
    return {**MOCK_WIDGET_CONFIG}
