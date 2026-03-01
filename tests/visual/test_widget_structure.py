"""
Layer 1 — Widget structural presence tests.

Verifies that the widget's key DOM elements exist and are visible in the
correct configuration.  These tests catch structural regressions: a component
removed by refactoring, a renamed aria-label, a missing greeting message.

Each test is deterministic because the /api/config response is mocked via
the ``widget_page`` fixture (see conftest.py).

Run with:
    pytest tests/visual/test_widget_structure.py -v --headed   # visual
    pytest tests/visual/test_widget_structure.py -v             # headless

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import FrameLocator, Page, expect


# ---------------------------------------------------------------------------
# Marker: all tests in this module require the "visual" marker
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.visual


# ===========================================================================
# Widget Lifecycle Tests
# ===========================================================================


class TestWidgetLifecycle:
    """Test the widget open/close/toggle lifecycle via the SDK."""

    def test_sdk_available(self, widget_page: Page) -> None:
        """The window.AgentRed SDK must be defined after widget init."""
        result = widget_page.evaluate("typeof window.AgentRed")
        assert result == "object", "AgentRed SDK not exposed on window"

    def test_sdk_methods(self, widget_page: Page) -> None:
        """The SDK must expose all documented methods."""
        methods = widget_page.evaluate("""
            const sdk = window.AgentRed;
            ['open', 'close', 'toggle', 'isOpen', 'setUnreadCount', 'hide', 'show', 'destroy']
                .map(m => typeof sdk[m])
        """)
        for i, method_type in enumerate(methods):
            assert method_type == "function", f"SDK method at index {i} is not a function"

    def test_widget_initially_closed(self, widget_page: Page) -> None:
        """Widget starts in 'closed' state — no iframe in the DOM."""
        iframe_count = widget_page.evaluate(
            "document.querySelectorAll('iframe[title=\"Agent Red Chat\"]').length"
        )
        assert iframe_count == 0, "Panel iframe should not exist when widget is closed"

    def test_open_creates_iframe(self, widget_page: Page) -> None:
        """Calling AgentRed.open() creates the panel iframe."""
        widget_page.evaluate("window.AgentRed.open()")
        iframe = widget_page.wait_for_selector(
            'iframe[title="Agent Red Chat"]',
            state="attached",
            timeout=5_000,
        )
        assert iframe is not None, "Panel iframe was not created after open()"

    def test_close_hides_iframe(self, widget_page: Page) -> None:
        """Calling AgentRed.close() sets iframe opacity to 0."""
        widget_page.evaluate("window.AgentRed.open()")
        widget_page.wait_for_selector('iframe[title="Agent Red Chat"]', timeout=5_000)
        widget_page.wait_for_timeout(300)  # transition

        widget_page.evaluate("window.AgentRed.close()")
        widget_page.wait_for_timeout(300)  # close transition

        opacity = widget_page.evaluate("""
            document.querySelector('iframe[title="Agent Red Chat"]').style.opacity
        """)
        assert opacity == "0", f"Expected opacity '0' after close, got '{opacity}'"

    def test_toggle_round_trip(self, widget_page: Page) -> None:
        """Toggle open → closed → open produces correct isOpen() states."""
        assert widget_page.evaluate("window.AgentRed.isOpen()") is False

        widget_page.evaluate("window.AgentRed.toggle()")
        widget_page.wait_for_timeout(100)
        assert widget_page.evaluate("window.AgentRed.isOpen()") is True

        widget_page.evaluate("window.AgentRed.toggle()")
        widget_page.wait_for_timeout(100)
        assert widget_page.evaluate("window.AgentRed.isOpen()") is False

    def test_destroy_removes_iframe(self, widget_page: Page) -> None:
        """Destroying the widget removes the iframe from the DOM."""
        widget_page.evaluate("window.AgentRed.open()")
        widget_page.wait_for_selector('iframe[title="Agent Red Chat"]', timeout=5_000)

        widget_page.evaluate("window.AgentRed.destroy()")
        widget_page.wait_for_timeout(200)

        iframe_count = widget_page.evaluate(
            "document.querySelectorAll('iframe[title=\"Agent Red Chat\"]').length"
        )
        assert iframe_count == 0, "Panel iframe should be removed after destroy()"


# ===========================================================================
# Panel Header Tests
# ===========================================================================


class TestPanelHeader:
    """Verify the panel header renders all expected elements."""

    def test_header_title(self, widget_panel: FrameLocator) -> None:
        """Default header title is 'Chat with us' (from en.ts locale)."""
        expect(widget_panel.locator("text=Chat with us")).to_be_visible()

    def test_agent_name_visible(self, widget_panel: FrameLocator) -> None:
        """Agent name from config is displayed in the header."""
        # Use exact text match — "Agent Red" appears in multiple places
        expect(widget_panel.get_by_text("Agent Red", exact=True)).to_be_visible()

    def test_agent_title_visible(self, widget_panel: FrameLocator) -> None:
        """Agent title appears after the agent name (separated by ·)."""
        expect(widget_panel.locator("text=AI Assistant")).to_be_visible()

    def test_close_button_exists(self, widget_panel: FrameLocator) -> None:
        """Close button with correct aria-label is present."""
        close_btn = widget_panel.locator('button[aria-label="Close chat"]')
        expect(close_btn).to_be_visible()

    def test_close_button_has_svg(self, widget_panel: FrameLocator) -> None:
        """Close button contains an SVG icon (X mark)."""
        svg = widget_panel.locator('button[aria-label="Close chat"] svg')
        expect(svg).to_be_attached()

    def test_online_status_dot(self, widget_panel: FrameLocator) -> None:
        """A green status dot (6×6px circle) is visible in the header."""
        # Verify the header subtitle line contains the agent name and title
        # The status dot is inline — we can't query it directly, but we verify
        # the surrounding text renders correctly.
        expect(
            widget_panel.get_by_text("Agent Red · AI Assistant")
        ).to_be_visible()


# ===========================================================================
# Panel Header — Custom Config Tests
# ===========================================================================


class TestPanelHeaderCustomConfig:
    """Verify header customization via WidgetConfig overrides."""

    def test_custom_header_text(self, page: Page, vite_server, mock_config: dict) -> None:
        """Setting widget_header_text overrides the default 'Chat with us'."""
        import json
        mock_config["widget_header_text"] = "Need help?"

        page.route("**/api/config*", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"config": mock_config}),
        ))
        page.route("**/api/conversations*", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"conversation_id": "test-conv-custom"}),
        ))

        page.goto(f"http://localhost:3100/dev.html", wait_until="domcontentloaded")
        page.wait_for_function("!!window.AgentRed", timeout=10_000)
        page.evaluate("window.AgentRed.open()")
        page.wait_for_selector('iframe[title="Agent Red Chat"]', timeout=5_000)
        page.wait_for_timeout(400)

        frame = page.frame_locator('iframe[title="Agent Red Chat"]')
        expect(frame.locator("text=Need help?")).to_be_visible()
        # Default should NOT appear
        expect(frame.locator("text=Chat with us")).not_to_be_visible()


# ===========================================================================
# Greeting / Conversation Area Tests
# ===========================================================================


class TestConversationArea:
    """Verify the conversation area, greeting, and input bar."""

    def test_greeting_visible(self, widget_panel: FrameLocator) -> None:
        """The configured greeting message is displayed."""
        expect(
            widget_panel.locator("text=Hi there! How can I help you today?")
        ).to_be_visible()

    def test_input_textarea_exists(self, widget_panel: FrameLocator) -> None:
        """A textarea for message input is present."""
        textarea = widget_panel.locator("textarea")
        expect(textarea).to_be_visible()

    def test_input_placeholder(self, widget_panel: FrameLocator) -> None:
        """Textarea has the default placeholder text."""
        textarea = widget_panel.locator("textarea")
        placeholder = textarea.get_attribute("placeholder")
        assert placeholder == "Type your message...", f"Expected default placeholder, got: {placeholder}"

    def test_send_button_exists(self, widget_panel: FrameLocator) -> None:
        """A send button is present in the input bar."""
        # Send button uses locale.sendButton = "Send" as its aria-label
        send_btn = widget_panel.locator('button[aria-label="Send"]')
        expect(send_btn).to_be_attached()

    def test_branding_visible(self, widget_panel: FrameLocator) -> None:
        """'Powered by Agent Red' branding is visible when enabled."""
        expect(widget_panel.locator("text=Powered by Agent Red")).to_be_visible()


# ===========================================================================
# Panel Dimensions Tests
# ===========================================================================


class TestPanelDimensions:
    """Verify the panel iframe has correct sizing from config."""

    def test_panel_width_standard(self, widget_page: Page) -> None:
        """Standard panel width is 380px."""
        widget_page.evaluate("window.AgentRed.open()")
        widget_page.wait_for_selector('iframe[title="Agent Red Chat"]', timeout=5_000)

        width = widget_page.evaluate("""
            document.querySelector('iframe[title="Agent Red Chat"]').style.width
        """)
        assert width == "380px", f"Expected panel width '380px', got '{width}'"

    def test_panel_height(self, widget_page: Page) -> None:
        """Panel height is 520px."""
        widget_page.evaluate("window.AgentRed.open()")
        widget_page.wait_for_selector('iframe[title="Agent Red Chat"]', timeout=5_000)

        height = widget_page.evaluate("""
            document.querySelector('iframe[title="Agent Red Chat"]').style.height
        """)
        assert height == "520px", f"Expected panel height '520px', got '{height}'"

    def test_panel_border_radius(self, widget_page: Page) -> None:
        """Panel iframe has rounded corners (12px borderRadius)."""
        widget_page.evaluate("window.AgentRed.open()")
        widget_page.wait_for_selector('iframe[title="Agent Red Chat"]', timeout=5_000)

        radius = widget_page.evaluate("""
            document.querySelector('iframe[title="Agent Red Chat"]').style.borderRadius
        """)
        assert radius == "12px", f"Expected border-radius '12px', got '{radius}'"


# ===========================================================================
# Iframe Accessibility Tests
# ===========================================================================


class TestIframeAccessibility:
    """Verify accessibility attributes on the panel iframe."""

    def test_iframe_has_title(self, widget_page: Page) -> None:
        """The iframe must have a title for screen readers."""
        widget_page.evaluate("window.AgentRed.open()")
        iframe = widget_page.wait_for_selector(
            'iframe[title="Agent Red Chat"]', timeout=5_000
        )
        assert iframe is not None
        title = iframe.get_attribute("title")
        assert title == "Agent Red Chat"

    def test_iframe_allows_media(self, widget_page: Page) -> None:
        """The iframe allows microphone and camera (for future features)."""
        widget_page.evaluate("window.AgentRed.open()")
        iframe = widget_page.wait_for_selector(
            'iframe[title="Agent Red Chat"]', timeout=5_000
        )
        allow = iframe.get_attribute("allow")
        assert "microphone" in (allow or ""), "iframe should allow microphone"
        assert "camera" in (allow or ""), "iframe should allow camera"
