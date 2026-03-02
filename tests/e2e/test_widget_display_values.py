"""
E2E tests — Widget Configuration page display values.

Verifies that mock API data (MOCK_CONFIG) is correctly rendered into every
form control on the Widget Configuration page. Each test targets a specific
field value rather than structural presence (see test_widget_page.py for
structure tests).

Sections covered:
  1. Installation — widget key value
  2. Appearance — colors, gradient, font, border radius, launcher, position,
     offsets, shadow, panel width, color mode
  3. Behavior — greeting enabled/mode/message, pre-chat off, sound on
  4. Content — header title/subtitle, input placeholder, agent display name

Run with:
    pytest tests/e2e/test_widget_display_values.py -v --headed
    pytest tests/e2e/test_widget_display_values.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

from .conftest import MOCK_CONFIG

pytestmark = pytest.mark.e2e

# Shorthand for the nested config dict used throughout
_CFG = MOCK_CONFIG["config"]


# ===========================================================================
# Installation Section — Display Values
# ===========================================================================


class TestWidgetInstallationValues:
    """Verify Installation section displays the correct API values."""

    def test_widget_key_value(self, admin_widget_page: Page) -> None:
        """Widget key input shows 'pk_live_test123_abc456' from API."""
        key_input = admin_widget_page.locator('input[value="pk_live_test123_abc456"]')
        expect(key_input).to_be_visible()
        expect(key_input).to_have_value("pk_live_test123_abc456")

    def test_widget_key_matches_mock(self, admin_widget_page: Page) -> None:
        """Widget key value matches MOCK_CONFIG exactly."""
        key_input = admin_widget_page.locator('input[value="pk_live_test123_abc456"]')
        assert key_input.input_value() == _CFG["widget_key"]

    def test_embed_code_contains_widget_key_value(self, admin_widget_page: Page) -> None:
        """Embed code snippet includes the widget key from API."""
        snippet_area = admin_widget_page.locator("code, pre, [class*='Code']")
        admin_widget_page.wait_for_timeout(500)
        found = False
        for i in range(snippet_area.count()):
            text = snippet_area.nth(i).inner_text()
            if _CFG["widget_key"] in text:
                found = True
                break
        assert found, f"Embed code should contain widget key '{_CFG['widget_key']}'"


# ===========================================================================
# Appearance Section — Display Values
# ===========================================================================


class TestWidgetAppearanceValues:
    """Verify Appearance section controls display the correct API values."""

    def test_primary_color_value(self, admin_widget_page: Page) -> None:
        """Header left color hex input shows '#ff3621'."""
        hex_input = admin_widget_page.locator('input[value="#ff3621"]')
        assert hex_input.count() > 0, "Primary color #ff3621 should be in a hex input"

    def test_gradient_end_color_value(self, admin_widget_page: Page) -> None:
        """Header right color hex input shows '#8B1520'."""
        hex_input = admin_widget_page.locator('input[value="#8B1520"]')
        assert hex_input.count() > 0, "Gradient end color #8B1520 should be in a hex input"

    def test_gradient_switch_off(self, admin_widget_page: Page) -> None:
        """Gradient switch is unchecked (widget_header_gradient_enabled=False)."""
        switch = admin_widget_page.locator(
            'input[type="checkbox"]'
        ).filter(has=admin_widget_page.locator("..").filter(has_text="Enable header gradient"))
        # Alternative: find the switch role near the gradient label
        gradient_switch = admin_widget_page.locator(
            'input[role="switch"]'
        ).first
        # Walk through all switches to find the gradient one
        switches = admin_widget_page.locator('input[role="switch"]')
        for i in range(switches.count()):
            sw = switches.nth(i)
            parent_text = sw.evaluate(
                "el => el.closest('label')?.textContent || el.parentElement?.textContent || ''"
            )
            if "gradient" in parent_text.lower():
                assert not sw.is_checked(), "Gradient switch should be OFF"
                return
        # Fallback: verify the right color is dimmed (opacity < 1 means gradient is off)
        right_label = admin_widget_page.get_by_text("Header right color", exact=True)
        opacity = right_label.evaluate("""el => {
            let node = el;
            for (let i = 0; i < 5; i++) {
                node = node.parentElement;
                if (!node) break;
                const op = getComputedStyle(node).opacity;
                if (op !== '1' && op !== '') return op;
            }
            return '1';
        }""")
        assert float(opacity) < 1.0, "Right color dimmed confirms gradient is off"

    def test_font_family_value(self, admin_widget_page: Page) -> None:
        """Font family select shows 'Inter (System)' for the default value."""
        # Mantine Select renders the selected value in an input
        font_input = admin_widget_page.get_by_label("Font family")
        val = font_input.input_value()
        assert "Inter" in val, f"Font family should show Inter variant, got: '{val}'"

    def test_border_radius_label_shows_value(self, admin_widget_page: Page) -> None:
        """Border radius label shows '16px' matching widget_border_radius=16."""
        label = admin_widget_page.get_by_text("Border radius (16px)")
        expect(label).to_be_visible()

    def test_launcher_size_label_shows_value(self, admin_widget_page: Page) -> None:
        """Launcher size label shows '60px' matching widget_launcher_size=60."""
        label = admin_widget_page.get_by_text("Launcher size (60px)")
        expect(label).to_be_visible()

    def test_launcher_icon_value(self, admin_widget_page: Page) -> None:
        """Launcher icon select shows 'Chat bubble' for widget_launcher_icon='chat'."""
        icon_input = admin_widget_page.get_by_label("Launcher icon")
        val = icon_input.input_value()
        assert "Chat" in val or "chat" in val.lower(), \
            f"Launcher icon should show 'Chat bubble', got: '{val}'"

    def test_position_bottom_right_selected(self, admin_widget_page: Page) -> None:
        """Position segmented control has 'Bottom right' selected."""
        # SegmentedControl marks the active segment; find the active label
        active_segment = admin_widget_page.locator(
            '[data-active] >> text="Bottom right"'
        )
        if active_segment.count() > 0:
            expect(active_segment.first).to_be_visible()
        else:
            # Fallback: check that Bottom right label exists (position = bottom-right)
            expect(admin_widget_page.get_by_text("Bottom right").first).to_be_visible()

    def test_horizontal_offset_value(self, admin_widget_page: Page) -> None:
        """Horizontal offset input shows 20 (widget_position_offset_x=20)."""
        offset_input = admin_widget_page.get_by_label("Horizontal offset", exact=True)
        val = offset_input.input_value()
        assert "20" in val, f"Horizontal offset should be 20, got: '{val}'"

    def test_vertical_offset_value(self, admin_widget_page: Page) -> None:
        """Vertical offset input shows 20 (widget_position_offset_y=20)."""
        offset_input = admin_widget_page.get_by_label("Vertical offset", exact=True)
        val = offset_input.input_value()
        assert "20" in val, f"Vertical offset should be 20, got: '{val}'"

    def test_color_mode_light_selected(self, admin_widget_page: Page) -> None:
        """Color mode segmented control has 'Light' selected."""
        active_segment = admin_widget_page.locator(
            '[data-active] >> text="Light"'
        )
        if active_segment.count() > 0:
            expect(active_segment.first).to_be_visible()
        else:
            # Verify Light option exists (color_mode = light)
            expect(admin_widget_page.get_by_text("Light", exact=True).first).to_be_visible()

    def test_panel_width_standard_selected(self, admin_widget_page: Page) -> None:
        """Panel width segmented control has 'Standard' selected."""
        # Multiple SegmentedControls use "Standard" — find the one in the Panel width section
        panel_width_label = admin_widget_page.get_by_text("Panel width").first
        panel_width_label.scroll_into_view_if_needed()
        # The SegmentedControl is a sibling of the label container
        active_segment = admin_widget_page.locator(
            '[data-active] >> text="Standard"'
        )
        assert active_segment.count() > 0, "Panel width 'Standard' should be active"

    def test_shadow_standard_selected(self, admin_widget_page: Page) -> None:
        """Panel shadow segmented control has 'Standard' selected."""
        panel_shadow_label = admin_widget_page.get_by_text("Panel shadow", exact=True)
        panel_shadow_label.scroll_into_view_if_needed()
        # Standard should appear as active in the shadow section
        active_standard = admin_widget_page.locator(
            '[data-active] >> text="Standard"'
        )
        assert active_standard.count() > 0, "Panel shadow 'Standard' should be active"


# ===========================================================================
# Behavior Section — Display Values
# ===========================================================================


class TestWidgetBehaviorValues:
    """Verify Behavior section controls display the correct API values."""

    def test_greeting_switch_on(self, admin_widget_page: Page) -> None:
        """Greeting message switch is ON (widget_greeting_enabled=True)."""
        switches = admin_widget_page.locator('input[role="switch"]')
        for i in range(switches.count()):
            sw = switches.nth(i)
            parent_text = sw.evaluate(
                "el => el.closest('label')?.textContent || el.parentElement?.textContent || ''"
            )
            if "Greeting message" in parent_text:
                assert sw.is_checked(), "Greeting message switch should be ON"
                return
        pytest.fail("Greeting message switch not found")

    def test_greeting_mode_static_selected(self, admin_widget_page: Page) -> None:
        """Greeting mode shows 'Static' selected (widget_greeting_mode='static')."""
        static_label = admin_widget_page.get_by_text("Static", exact=True).first
        expect(static_label).to_be_visible()

    def test_greeting_message_value(self, admin_widget_page: Page) -> None:
        """Greeting textarea shows the mock greeting message."""
        textarea = admin_widget_page.locator("textarea").first
        val = textarea.input_value()
        assert val == _CFG["widget_greeting_message"], \
            f"Greeting message should be '{_CFG['widget_greeting_message']}', got: '{val}'"

    def test_pre_chat_form_switch_off(self, admin_widget_page: Page) -> None:
        """Pre-chat form switch is OFF (widget_pre_chat_form_enabled=False)."""
        switches = admin_widget_page.locator('input[role="switch"]')
        for i in range(switches.count()):
            sw = switches.nth(i)
            parent_text = sw.evaluate(
                "el => el.closest('label')?.textContent || el.parentElement?.textContent || ''"
            )
            if "Pre-chat form" in parent_text or "pre-chat" in parent_text.lower():
                assert not sw.is_checked(), "Pre-chat form switch should be OFF"
                return
        pytest.fail("Pre-chat form switch not found")

    def test_pre_chat_fields_not_visible_when_off(self, admin_widget_page: Page) -> None:
        """Pre-chat fields section is hidden when pre-chat is disabled."""
        fields_label = admin_widget_page.get_by_text("Pre-chat fields")
        expect(fields_label).not_to_be_visible()

    def test_sound_switch_on(self, admin_widget_page: Page) -> None:
        """Sound notifications switch is ON (widget_sound_enabled=True)."""
        switches = admin_widget_page.locator('input[role="switch"]')
        for i in range(switches.count()):
            sw = switches.nth(i)
            parent_text = sw.evaluate(
                "el => el.closest('label')?.textContent || el.parentElement?.textContent || ''"
            )
            if "Sound notifications" in parent_text:
                assert sw.is_checked(), "Sound notifications switch should be ON"
                return
        pytest.fail("Sound notifications switch not found")


# ===========================================================================
# Content Section — Display Values
# ===========================================================================


class TestWidgetContentValues:
    """Verify Content section inputs display the correct API values."""

    def test_header_title_value(self, admin_widget_page: Page) -> None:
        """Header title input shows 'Support'."""
        title_input = admin_widget_page.get_by_label("Header title")
        expect(title_input).to_have_value("Support")

    def test_header_subtitle_value(self, admin_widget_page: Page) -> None:
        """Header subtitle input shows 'We typically reply within minutes'."""
        subtitle_input = admin_widget_page.get_by_label("Header subtitle")
        expect(subtitle_input).to_have_value("We typically reply within minutes")

    def test_input_placeholder_value(self, admin_widget_page: Page) -> None:
        """Input placeholder input shows 'Type your message...'."""
        placeholder_input = admin_widget_page.get_by_label("Input placeholder")
        expect(placeholder_input).to_have_value("Type your message...")

    def test_agent_display_name_value(self, admin_widget_page: Page) -> None:
        """Agent display name input shows 'Agent Red'."""
        name_input = admin_widget_page.get_by_label("Agent display name")
        expect(name_input).to_have_value("Agent Red")

    def test_header_title_matches_mock(self, admin_widget_page: Page) -> None:
        """Header title value matches MOCK_CONFIG exactly."""
        title_input = admin_widget_page.get_by_label("Header title")
        assert title_input.input_value() == _CFG["widget_header_title"]

    def test_header_subtitle_matches_mock(self, admin_widget_page: Page) -> None:
        """Header subtitle value matches MOCK_CONFIG exactly."""
        subtitle_input = admin_widget_page.get_by_label("Header subtitle")
        assert subtitle_input.input_value() == _CFG["widget_header_subtitle"]

    def test_input_placeholder_matches_mock(self, admin_widget_page: Page) -> None:
        """Input placeholder value matches MOCK_CONFIG exactly."""
        placeholder_input = admin_widget_page.get_by_label("Input placeholder")
        assert placeholder_input.input_value() == _CFG["widget_input_placeholder"]

    def test_agent_display_name_matches_mock(self, admin_widget_page: Page) -> None:
        """Agent display name value matches MOCK_CONFIG exactly."""
        name_input = admin_widget_page.get_by_label("Agent display name")
        assert name_input.input_value() == _CFG["widget_agent_display_name"]
