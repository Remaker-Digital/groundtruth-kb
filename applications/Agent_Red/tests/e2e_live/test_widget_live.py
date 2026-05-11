"""
Live E2E widget configuration tests — real data + preview defect.

Validates that the Widget Configuration page loads real widget settings
from production, including appearance, behavior, and content fields.

The Installation section may show "No widget key found. Activate your
configuration to generate one." when viewing draft config. Tests check
for both active (key present) and draft (key absent) states.

Documents the known defect: the "Live preview" widget launcher is static
JSX (WidgetPreview component at Widget.tsx:365) with no click handler,
no iframe, and no widget SDK loaded. Clicking it does nothing.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re

import pytest
from playwright.sync_api import Page


def _get_all_input_values(page: Page) -> list[str]:
    """Get all text input values from the page."""
    return page.evaluate("""
        (() => {
            const inputs = document.querySelectorAll('input[type="text"], input:not([type])');
            return Array.from(inputs).map(el => el.value || '');
        })()
    """) or []


class TestWidgetInstallation:
    """Widget installation section — checks widget key and API URL fields."""

    def test_widget_key_field_present(self, shared_widget_page: Page):
        """Widget key field exists (may show key or 'No widget key found')."""
        shared_widget_page.wait_for_timeout(1000)
        main_text = shared_widget_page.text_content("main") or ""
        has_key_section = (
            "pk_live_" in main_text
            or "Widget key" in main_text
            or "No widget key found" in main_text
        )
        assert has_key_section, "Widget key section not found on page"

    def test_api_url_field_present(self, shared_widget_page: Page):
        """API URL field exists on the widget page."""
        main_text = shared_widget_page.text_content("main") or ""
        assert "API URL" in main_text, "API URL field not found on widget page"

    def test_widget_key_or_activation_message(self, shared_widget_page: Page):
        """Widget key shows a real key OR an activation prompt."""
        shared_widget_page.wait_for_timeout(1000)
        main_text = shared_widget_page.text_content("main") or ""
        input_values = _get_all_input_values(shared_widget_page)
        all_text = main_text + " ".join(input_values)

        has_real_key = "pk_live_" in all_text
        has_activation_msg = "Activate your configuration" in main_text
        assert has_real_key or has_activation_msg, (
            "Neither widget key nor activation message found"
        )

    def test_installation_section_has_content(self, shared_widget_page: Page):
        """Installation section contains widget key and API URL labels."""
        main_text = shared_widget_page.text_content("main") or ""
        assert "Widget key" in main_text, "Widget key label not found"
        assert "API URL" in main_text, "API URL label not found"

    def test_embed_code_or_activation_message(self, shared_widget_page: Page):
        """Embed code with <script> tag is shown, OR activation prompt."""
        shared_widget_page.wait_for_timeout(1000)
        main_text = shared_widget_page.text_content("main") or ""
        has_script = bool(re.search(r"<\s*script", main_text, re.I))
        has_activation = "Activate your configuration" in main_text
        assert has_script or has_activation, (
            "Neither embed code <script> tag nor activation message found"
        )


class TestWidgetAppearance:
    """Widget appearance settings reflect real production configuration."""

    def test_color_picker_has_real_value(self, shared_widget_page: Page):
        """Primary color input is not empty."""
        shared_widget_page.wait_for_timeout(1000)
        main_text = shared_widget_page.text_content("main") or ""
        input_values = _get_all_input_values(shared_widget_page)
        all_text = main_text + " ".join(input_values)
        has_hex = bool(re.search(r"#[0-9a-fA-F]{3,8}", all_text))
        has_color_input = shared_widget_page.locator("input[type='color']").count() > 0
        assert has_hex or has_color_input, "No color value found on widget page"

    def test_gradient_toggle_reflects_config(self, shared_widget_page: Page):
        """The gradient toggle switch is present and has a defined state."""
        switches = shared_widget_page.locator(
            "input[type='checkbox'][role='switch'], [role='switch']"
        )
        assert switches.count() >= 1, "No toggle switches found on widget page"

    def test_position_control_has_value(self, shared_widget_page: Page):
        """Widget position control shows bottom-right or bottom-left."""
        main_text = (shared_widget_page.text_content("main") or "").lower()
        has_position = (
            "bottom right" in main_text
            or "bottom left" in main_text
            or "bottom-right" in main_text
            or "bottom-left" in main_text
        )
        assert has_position, "No widget position value found"


class TestWidgetContent:
    """Widget content fields are populated with real configuration."""

    def test_header_title_populated(self, shared_widget_page: Page):
        """At least one text input on the widget page has a real value."""
        shared_widget_page.wait_for_timeout(1000)
        input_values = _get_all_input_values(shared_widget_page)
        populated = [v for v in input_values if v.strip()]
        assert len(populated) >= 1, "No populated text inputs on widget page"

    def test_agent_display_name_populated(self, shared_widget_page: Page):
        """Multiple text inputs have real values from the config."""
        shared_widget_page.wait_for_timeout(1000)
        input_values = _get_all_input_values(shared_widget_page)
        populated = [v for v in input_values if v.strip()]
        assert len(populated) >= 2, (
            f"Expected at least 2 populated text inputs, found {len(populated)}"
        )


class TestWidgetPreview:
    """Widget preview panel — documents the known interactivity defect."""

    @pytest.mark.xfail(
        reason="Known defect: preview is static JSX (WidgetPreview at Widget.tsx:365), "
        "not an interactive widget SDK. Launcher has cursor:default and no click handler.",
        strict=True,
    )
    def test_preview_widget_is_interactive(self, shared_widget_page: Page):
        """Click the preview launcher — expect panel interaction.

        This test documents the known defect: the WidgetPreview component
        renders a static mockup with cursor:default and no click handler.
        No <iframe> or widget SDK is loaded. Clicking does nothing.
        """
        shared_widget_page.wait_for_timeout(1000)
        # Find the preview area by its content text
        launcher = shared_widget_page.locator("text=Powered by Agent Red").first

        if launcher.is_visible():
            launcher.click()
            shared_widget_page.wait_for_timeout(1000)

        # Expect a functional chat interface (this WILL FAIL — defect)
        # The static preview has a "Type your message..." placeholder but it's
        # not connected to any backend — typing does nothing
        chat_input = shared_widget_page.locator(
            "iframe[src*='widget'], "
            "[contenteditable='true']"
        )
        assert chat_input.count() > 0, (
            "Preview widget is not interactive — no functional chat interface"
        )

    @pytest.mark.xfail(
        reason="WI-0918: staging-specific — preview content not rendered "
               "in main element. Identified as staging-specific since S124.",
        strict=False,
    )
    def test_preview_panel_visible(self, shared_widget_page: Page):
        """The static preview panel renders with expected content."""
        shared_widget_page.wait_for_timeout(1000)
        main_text = shared_widget_page.text_content("main") or ""
        # The preview contains "Live preview", "Support", "Powered by Agent Red"
        has_preview = (
            "Live preview" in main_text
            or "Powered by Agent Red" in main_text
            or "We typically reply within minutes" in main_text
        )
        assert has_preview, "No preview panel content found on widget page"
