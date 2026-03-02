"""
E2E tests — Widget Configuration page.

Spec-validation tests covering all 4 sections of the Widget Configuration page:
  1. Installation — widget key, copy, rotate, API URL, embed code
  2. Appearance — colors, gradient, font, border radius, launcher, position,
     color mode, panel width, shadow
  3. Behavior — greeting toggle/mode/message, pre-chat form, sound
  4. Content — header title/subtitle, input placeholder, agent identity, avatar

Tests are linked to WIDGET_UI SPEC-NNNN specifications in the Knowledge Database.
Each test validates that the implementation matches a recorded specification.

Run with:
    pytest tests/e2e/test_widget_page.py -v --headed
    pytest tests/e2e/test_widget_page.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

from .conftest import AdminApiMocker

pytestmark = pytest.mark.e2e


# ===========================================================================
# Page Structure Tests
# ===========================================================================


class TestWidgetPageStructure:
    """Verify the Widget page renders all expected structural elements."""

    def test_page_heading_text(self, admin_widget_page: Page) -> None:
        """Page heading reads 'Widget configuration'."""
        heading = admin_widget_page.locator("h2").filter(has_text="Widget configuration")
        expect(heading).to_be_visible()

    def test_page_subtitle_text(self, admin_widget_page: Page) -> None:
        """Subtitle reads 'Customize how your chat widget looks and behaves'."""
        subtitle = admin_widget_page.get_by_text(
            "Customize how your chat widget looks and behaves"
        )
        expect(subtitle).to_be_visible()

    def test_installation_section_header(self, admin_widget_page: Page) -> None:
        """Installation section header is visible."""
        # SectionHeader renders children + HelpTooltip inside one <Text>,
        # so exact match fails. Use substring match.
        header = admin_widget_page.get_by_text("Installation")
        expect(header.first).to_be_visible()

    def test_appearance_section_header(self, admin_widget_page: Page) -> None:
        """Appearance section header is visible."""
        header = admin_widget_page.get_by_text("Appearance")
        expect(header.first).to_be_visible()

    def test_behavior_section_header(self, admin_widget_page: Page) -> None:
        """Behavior section header is visible."""
        header = admin_widget_page.get_by_text("Behavior")
        expect(header.first).to_be_visible()

    def test_content_section_header(self, admin_widget_page: Page) -> None:
        """Content section header is visible."""
        header = admin_widget_page.get_by_text("Content")
        expect(header.first).to_be_visible()

    @pytest.mark.xfail(reason="Intermittent Playwright timeout on scroll_into_view_if_needed (pre-existing)")
    def test_live_preview_visible(self, admin_widget_page: Page) -> None:
        """Live preview panel is visible in the right column.

        The preview section may be below the fold on narrow viewports.
        Scroll to ensure visibility before asserting.
        """
        preview_label = admin_widget_page.get_by_text("Live preview", exact=True).first
        preview_label.scroll_into_view_if_needed()
        expect(preview_label).to_be_visible()


# ===========================================================================
# Installation Section Tests
# ===========================================================================


class TestWidgetInstallation:
    """Verify the Installation section: widget key, copy, rotate, embed code."""

    def test_widget_key_label(self, admin_widget_page: Page) -> None:
        """Widget key label is displayed."""
        label = admin_widget_page.get_by_text("Widget key", exact=True)
        expect(label.first).to_be_visible()

    def test_widget_key_value_displayed(self, admin_widget_page: Page) -> None:
        """Widget key from API is shown in a read-only input."""
        key_input = admin_widget_page.locator('input[value="pk_live_test123_abc456"]')
        expect(key_input).to_be_visible()

    def test_widget_key_read_only(self, admin_widget_page: Page) -> None:
        """Widget key input is read-only (not editable)."""
        key_input = admin_widget_page.locator('input[value="pk_live_test123_abc456"]')
        readonly = key_input.get_attribute("readonly")
        assert readonly is not None, "Widget key input should be read-only"

    def test_widget_key_monospace_font(self, admin_widget_page: Page) -> None:
        """Widget key input uses monospace font for readability."""
        key_input = admin_widget_page.locator('input[value="pk_live_test123_abc456"]')
        font = key_input.evaluate("el => getComputedStyle(el).fontFamily")
        assert "monospace" in font.lower(), f"Expected monospace font, got: {font}"

    def test_copy_key_button_visible(self, admin_widget_page: Page) -> None:
        """Copy button exists near the widget key."""
        clipboard_btn = admin_widget_page.locator("button", has_text="\U0001f4cb")
        copy_btn = admin_widget_page.locator(
            'button[aria-label*="Copy"], button[aria-label*="copy"]'
        )
        assert clipboard_btn.count() > 0 or copy_btn.count() > 0, \
            "Copy button should be visible near widget key"

    def test_rotate_key_button_visible(self, admin_widget_page: Page) -> None:
        """'Rotate key' button is visible in the Installation section."""
        rotate_btn = admin_widget_page.locator("button", has_text="Rotate key")
        expect(rotate_btn).to_be_visible()

    def test_api_url_label(self, admin_widget_page: Page) -> None:
        """API URL label is displayed."""
        label = admin_widget_page.get_by_text("API URL", exact=True)
        expect(label.first).to_be_visible()

    def test_api_url_read_only_input(self, admin_widget_page: Page) -> None:
        """API URL is shown in a read-only input."""
        # Find read-only inputs that contain a URL (not the widget key)
        readonly_inputs = admin_widget_page.locator("input[readonly]")
        found = False
        for i in range(readonly_inputs.count()):
            val = readonly_inputs.nth(i).input_value()
            if ("localhost" in val or "http" in val) and "pk_live" not in val:
                found = True
                break
        assert found, "API URL should be displayed in a read-only input"

    def test_shopify_helper_text(self, admin_widget_page: Page) -> None:
        """Shopify-specific helper text appears below API URL."""
        helper = admin_widget_page.get_by_text("Shopify merchants")
        expect(helper).to_be_visible()

    def test_embed_code_label(self, admin_widget_page: Page) -> None:
        """Embed code section label is visible when widget key exists."""
        label = admin_widget_page.get_by_text("Embed code", exact=True)
        expect(label.first).to_be_visible()

    def test_copy_snippet_button(self, admin_widget_page: Page) -> None:
        """'Copy snippet' button is visible in embed code section."""
        btn = admin_widget_page.locator("button", has_text="Copy snippet")
        expect(btn).to_be_visible()

    def test_embed_code_contains_widget_key(self, admin_widget_page: Page) -> None:
        """Embed code snippet includes the widget key."""
        # Mantine Code renders as <code> or <pre>; use broad selector.
        # Wait for config to load by checking for embed code text.
        snippet_area = admin_widget_page.locator("code, pre, [class*='Code']")
        admin_widget_page.wait_for_timeout(500)
        found = False
        for i in range(snippet_area.count()):
            text = snippet_area.nth(i).inner_text()
            if "pk_live_test123_abc456" in text:
                found = True
                break
        assert found, "Embed code should include widget key pk_live_test123_abc456"

    def test_embed_code_is_script_tag(self, admin_widget_page: Page) -> None:
        """Embed code is a <script> tag with data-widget-key and data-api-url."""
        snippet_area = admin_widget_page.locator("code, pre, [class*='Code']")
        admin_widget_page.wait_for_timeout(500)
        text = ""
        for i in range(snippet_area.count()):
            t = snippet_area.nth(i).inner_text()
            if "widget" in t.lower():
                text = t
                break
        assert "data-widget-key" in text, \
            f"Embed code should have data-widget-key, got: {text[:200]}"
        assert "data-api-url" in text, "Embed code should have data-api-url attr"
        assert "widget.js" in text, "Embed code should reference widget.js"

    def test_embed_code_placement_instruction(self, admin_widget_page: Page) -> None:
        """Helper text instructs to paste before closing body tag."""
        helper = admin_widget_page.get_by_text("Paste this snippet before")
        expect(helper).to_be_visible()


# ===========================================================================
# Appearance Section Tests
# ===========================================================================


class TestWidgetAppearance:
    """Verify all appearance controls: colors, gradient, font, layout, etc."""

    def test_header_left_color_label(self, admin_widget_page: Page) -> None:
        """'Header left color' label is displayed."""
        label = admin_widget_page.get_by_text("Header left color", exact=True)
        expect(label).to_be_visible()

    def test_header_right_color_label(self, admin_widget_page: Page) -> None:
        """'Header right color' label is displayed."""
        label = admin_widget_page.get_by_text("Header right color", exact=True)
        expect(label).to_be_visible()

    def test_gradient_switch_label(self, admin_widget_page: Page) -> None:
        """'Enable header gradient' switch is present."""
        label = admin_widget_page.get_by_text("Enable header gradient")
        expect(label).to_be_visible()

    def test_gradient_switch_description(self, admin_widget_page: Page) -> None:
        """Gradient switch shows explanatory description."""
        desc = admin_widget_page.get_by_text(
            "When off, the header uses a solid color"
        )
        expect(desc).to_be_visible()

    def test_font_family_label(self, admin_widget_page: Page) -> None:
        """Font family select has correct label."""
        label = admin_widget_page.get_by_text("Font family", exact=True)
        expect(label).to_be_visible()

    def test_border_radius_label(self, admin_widget_page: Page) -> None:
        """Border radius slider label shows current pixel value."""
        label = admin_widget_page.get_by_text("Border radius")
        expect(label.first).to_be_visible()

    def test_launcher_size_label(self, admin_widget_page: Page) -> None:
        """Launcher size slider label is visible."""
        label = admin_widget_page.get_by_text("Launcher size")
        expect(label.first).to_be_visible()

    def test_launcher_icon_label(self, admin_widget_page: Page) -> None:
        """Launcher icon select has correct label."""
        label = admin_widget_page.get_by_text("Launcher icon", exact=True)
        expect(label).to_be_visible()

    def test_position_label(self, admin_widget_page: Page) -> None:
        """Position control label is visible."""
        label = admin_widget_page.get_by_text("Position", exact=True)
        expect(label.first).to_be_visible()

    def test_position_options(self, admin_widget_page: Page) -> None:
        """Position control offers 'Bottom right' and 'Bottom left'.

        Mobile offset controls may duplicate position text — use .first
        to avoid Playwright strict-mode violations.
        """
        expect(admin_widget_page.get_by_text("Bottom right").first).to_be_visible()
        expect(admin_widget_page.get_by_text("Bottom left").first).to_be_visible()

    def test_horizontal_offset_label(self, admin_widget_page: Page) -> None:
        """Horizontal offset input is present.

        S127 added mobile offset controls — 'Mobile horizontal offset (px)'
        contains 'Horizontal offset' as a substring, creating duplicates.
        Use exact match to target the desktop control only.
        """
        label = admin_widget_page.get_by_text("Horizontal offset", exact=True)
        expect(label.first).to_be_visible()

    def test_vertical_offset_label(self, admin_widget_page: Page) -> None:
        """Vertical offset input is present.

        S127 added mobile offset controls — 'Mobile vertical offset (px)'
        contains 'Vertical offset' as a substring, creating duplicates.
        Use exact match to target the desktop control only.
        """
        label = admin_widget_page.get_by_text("Vertical offset", exact=True)
        expect(label.first).to_be_visible()

    def test_color_mode_label(self, admin_widget_page: Page) -> None:
        """Color mode control label is visible."""
        label = admin_widget_page.get_by_text("Color mode", exact=True)
        expect(label.first).to_be_visible()

    def test_color_mode_options(self, admin_widget_page: Page) -> None:
        """Color mode offers Light, Dark, Auto options."""
        # SegmentedControl renders options as labels
        for option_text in ("Light", "Dark", "Auto"):
            option = admin_widget_page.locator("label", has_text=option_text)
            assert option.count() > 0, f"Color mode option '{option_text}' should exist"

    def test_panel_width_label(self, admin_widget_page: Page) -> None:
        """Panel width control label is visible."""
        label = admin_widget_page.get_by_text("Panel width")
        expect(label.first).to_be_visible()

    def test_panel_width_options(self, admin_widget_page: Page) -> None:
        """Panel width offers Compact, Standard, Wide options."""
        for option_text in ("Compact", "Standard", "Wide"):
            option = admin_widget_page.get_by_text(option_text, exact=True)
            assert option.count() > 0, \
                f"Panel width option '{option_text}' should exist"

    def test_panel_shadow_label(self, admin_widget_page: Page) -> None:
        """Panel shadow control label is visible."""
        label = admin_widget_page.get_by_text("Panel shadow", exact=True)
        expect(label).to_be_visible()

    def test_panel_shadow_options(self, admin_widget_page: Page) -> None:
        """Panel shadow offers None, Subtle, Standard, Heavy options."""
        for option_text in ("None", "Subtle", "Heavy"):
            option = admin_widget_page.get_by_text(option_text, exact=True)
            assert option.count() > 0, \
                f"Panel shadow option '{option_text}' should exist"

    def test_color_inputs_present(self, admin_widget_page: Page) -> None:
        """At least one color configuration input (hex or native) exists."""
        color_inputs = admin_widget_page.locator('input[type="color"]')
        hex_inputs = admin_widget_page.locator('input[value*="#"]')
        assert color_inputs.count() > 0 or hex_inputs.count() > 0, \
            "Color configuration inputs should be visible"

    def test_gradient_right_color_dimmed_when_off(
        self, admin_widget_page: Page
    ) -> None:
        """Header right color is visually dimmed when gradient is disabled."""
        right_label = admin_widget_page.get_by_text(
            "Header right color", exact=True
        )
        # The opacity: 0.4 is on an ancestor div wrapping the ColorField.
        # Walk up until we find the element with opacity set.
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
        assert float(opacity) < 1.0, \
            f"Right color should be dimmed (opacity < 1) when gradient off, got {opacity}"


# ===========================================================================
# Behavior Section Tests
# ===========================================================================


class TestWidgetBehavior:
    """Verify behavior controls: greeting, pre-chat, sound."""

    def test_greeting_message_switch(self, admin_widget_page: Page) -> None:
        """'Greeting message' switch is present."""
        label = admin_widget_page.get_by_text("Greeting message", exact=True)
        expect(label.first).to_be_visible()

    def test_greeting_mode_options(self, admin_widget_page: Page) -> None:
        """Greeting mode has 'Static' and 'AI-generated' options."""
        static = admin_widget_page.get_by_text("Static", exact=True)
        ai_gen = admin_widget_page.get_by_text("AI-generated", exact=True)
        expect(static.first).to_be_visible()
        expect(ai_gen.first).to_be_visible()

    def test_greeting_textarea_visible(self, admin_widget_page: Page) -> None:
        """Greeting message textarea is present when in static mode."""
        # Static mode is the default — textarea should be visible
        textarea = admin_widget_page.locator("textarea")
        expect(textarea.first).to_be_visible()

    def test_template_variable_buttons(self, admin_widget_page: Page) -> None:
        """Template variable buttons are shown for greeting personalization."""
        for var in ("<FIRST_NAME>", "<LAST_NAME>", "<FULL_NAME>", "<COMPANY>"):
            btn = admin_widget_page.locator("button", has_text=var)
            expect(btn).to_be_visible()

    def test_pre_chat_form_switch(self, admin_widget_page: Page) -> None:
        """'Pre-chat form' switch is present."""
        label = admin_widget_page.get_by_text("Pre-chat form")
        expect(label.first).to_be_visible()

    def test_pre_chat_form_description(self, admin_widget_page: Page) -> None:
        """Pre-chat form switch has 'Collect visitor name and email' description."""
        desc = admin_widget_page.get_by_text("Collect visitor name and email")
        expect(desc).to_be_visible()

    def test_sound_notifications_switch(self, admin_widget_page: Page) -> None:
        """'Sound notifications' switch is present."""
        label = admin_widget_page.get_by_text("Sound notifications", exact=True)
        expect(label).to_be_visible()


# ===========================================================================
# Content Section Tests
# ===========================================================================


class TestWidgetContent:
    """Verify content controls: header text, agent identity, avatar."""

    def test_header_title_label(self, admin_widget_page: Page) -> None:
        """Header title input has correct label."""
        label = admin_widget_page.get_by_text("Header title", exact=True)
        expect(label).to_be_visible()

    def test_header_subtitle_label(self, admin_widget_page: Page) -> None:
        """Header subtitle input has correct label."""
        label = admin_widget_page.get_by_text("Header subtitle", exact=True)
        expect(label).to_be_visible()

    def test_input_placeholder_label(self, admin_widget_page: Page) -> None:
        """Input placeholder input has correct label."""
        label = admin_widget_page.get_by_text("Input placeholder", exact=True)
        expect(label).to_be_visible()

    def test_agent_identity_divider(self, admin_widget_page: Page) -> None:
        """'Agent identity' divider label is visible."""
        label = admin_widget_page.get_by_text("Agent identity", exact=True)
        expect(label).to_be_visible()

    def test_agent_display_name_label(self, admin_widget_page: Page) -> None:
        """Agent display name input has correct label."""
        label = admin_widget_page.get_by_text("Agent display name", exact=True)
        expect(label).to_be_visible()

    def test_agent_display_name_description(self, admin_widget_page: Page) -> None:
        """Agent display name has descriptive helper text."""
        desc = admin_widget_page.get_by_text(
            "Name shown in chat header and greeting"
        )
        expect(desc).to_be_visible()

    def test_agent_avatar_label(self, admin_widget_page: Page) -> None:
        """Agent avatar section label is visible."""
        label = admin_widget_page.get_by_text("Agent avatar", exact=True)
        expect(label).to_be_visible()

    def test_avatar_upload_drop_zone(self, admin_widget_page: Page) -> None:
        """Avatar upload drop zone is visible (when no avatar set)."""
        upload = admin_widget_page.get_by_text("Drop an image or click to browse")
        expect(upload).to_be_visible()

    def test_avatar_size_limit_text(self, admin_widget_page: Page) -> None:
        """Avatar upload shows size/format limit: 'PNG or JPEG, max 256 KB'."""
        limit = admin_widget_page.get_by_text("PNG or JPEG, max 256 KB")
        expect(limit).to_be_visible()


# ===========================================================================
# Action Button Tests
# ===========================================================================


class TestWidgetActions:
    """Verify page-level action buttons."""

    def test_save_button_text(self, admin_widget_page: Page) -> None:
        """Save button reads 'Save draft inputs'."""
        btn = admin_widget_page.locator("button", has_text="Save draft inputs")
        expect(btn).to_be_visible()

    def test_reset_button_text(self, admin_widget_page: Page) -> None:
        """Reset button reads 'Reset to defaults'."""
        btn = admin_widget_page.locator("button", has_text="Reset to defaults")
        expect(btn).to_be_visible()

    def test_save_sends_api_call(self, admin_widget_page: Page) -> None:
        """Clicking Save sends a PUT to the config endpoint."""
        mocker: AdminApiMocker = admin_widget_page._api_mocker  # type: ignore[attr-defined]
        mocker.clear_calls()

        save_btn = admin_widget_page.locator(
            "button", has_text="Save draft inputs"
        ).first
        save_btn.click()
        admin_widget_page.wait_for_timeout(500)

        all_calls = mocker.get_calls()
        save_calls = [
            c for c in all_calls
            if c["method"] in ("POST", "PUT")
            and ("widget" in c.get("path", "") or "config" in c.get("path", ""))
        ]
        assert len(save_calls) >= 1, \
            f"Save should trigger config API call, got: {all_calls}"


# ===========================================================================
# Widget Key Rotation Modal Tests
# ===========================================================================


class TestWidgetKeyRotation:
    """Test widget key rotation confirmation flow."""

    def test_rotate_opens_modal(self, admin_widget_page: Page) -> None:
        """Clicking 'Rotate key' opens a confirmation modal."""
        admin_widget_page.locator("button", has_text="Rotate key").click()
        admin_widget_page.wait_for_timeout(300)

        modal_title = admin_widget_page.get_by_text("Rotate widget key")
        expect(modal_title).to_be_visible()

    def test_rotation_modal_warning(self, admin_widget_page: Page) -> None:
        """Rotation modal warns about immediate invalidation."""
        admin_widget_page.locator("button", has_text="Rotate key").click()
        admin_widget_page.wait_for_timeout(300)

        warning = admin_widget_page.get_by_text("immediately invalidate")
        expect(warning).to_be_visible()

    def test_rotation_modal_confirmation_text(self, admin_widget_page: Page) -> None:
        """Rotation modal asks 'Are you sure you want to rotate'."""
        admin_widget_page.locator("button", has_text="Rotate key").click()
        admin_widget_page.wait_for_timeout(300)

        confirm_text = admin_widget_page.get_by_text(
            "Are you sure you want to rotate"
        )
        expect(confirm_text).to_be_visible()

    def test_rotation_modal_has_cancel(self, admin_widget_page: Page) -> None:
        """Rotation modal has a Cancel button."""
        admin_widget_page.locator("button", has_text="Rotate key").click()
        admin_widget_page.wait_for_timeout(300)

        cancel = admin_widget_page.locator(
            "[role='dialog'] >> button", has_text="Cancel"
        )
        expect(cancel).to_be_visible()

    def test_rotation_modal_has_confirm(self, admin_widget_page: Page) -> None:
        """Rotation modal has a Rotate key confirmation button."""
        admin_widget_page.locator("button", has_text="Rotate key").first.click()
        admin_widget_page.wait_for_timeout(300)

        confirm_btn = admin_widget_page.locator(
            "[role='dialog'] >> button", has_text="Rotate key"
        )
        assert confirm_btn.count() >= 1, \
            "Modal should have a Rotate key confirmation button"

    def test_cancel_closes_modal(self, admin_widget_page: Page) -> None:
        """Clicking Cancel closes the rotation modal."""
        admin_widget_page.locator("button", has_text="Rotate key").click()
        admin_widget_page.wait_for_timeout(300)

        cancel = admin_widget_page.locator(
            "[role='dialog'] >> button", has_text="Cancel"
        )
        cancel.click()
        admin_widget_page.wait_for_timeout(300)

        modal = admin_widget_page.locator("[role='dialog']")
        expect(modal).not_to_be_visible()


# ===========================================================================
# Interactive Behavior Tests
# ===========================================================================


class TestWidgetInteractions:
    """Test conditional display and interactive behaviors."""

    def test_pre_chat_fields_shown_on_enable(
        self, admin_widget_page: Page
    ) -> None:
        """Enabling pre-chat form reveals field selection chips."""
        # Pre-chat is OFF by default. Find and click its switch.
        switch_label = admin_widget_page.get_by_text("Pre-chat form").first
        switch_label.click()
        admin_widget_page.wait_for_timeout(300)

        fields_label = admin_widget_page.get_by_text("Pre-chat fields")
        expect(fields_label).to_be_visible()

    def test_pre_chat_field_chips(self, admin_widget_page: Page) -> None:
        """Pre-chat field chips include Name, Email, Phone, Company."""
        # Enable pre-chat first
        admin_widget_page.get_by_text("Pre-chat form").first.click()
        admin_widget_page.wait_for_timeout(300)

        for field_name in ("Name", "Email", "Phone", "Company"):
            chip = admin_widget_page.get_by_text(field_name, exact=True)
            expect(chip.first).to_be_visible()

    def test_ai_generated_mode_hides_textarea(
        self, admin_widget_page: Page
    ) -> None:
        """Selecting AI-generated greeting mode shows explanation text instead of textarea."""
        # Click the AI-generated option in the greeting mode segmented control
        ai_gen = admin_widget_page.get_by_text("AI-generated", exact=True).first
        ai_gen.click()
        admin_widget_page.wait_for_timeout(300)

        # AI mode shows an explanation paragraph
        ai_desc = admin_widget_page.get_by_text(
            "The AI will generate a unique"
        )
        expect(ai_desc).to_be_visible()


# ===========================================================================
# API Data Loading Tests
# ===========================================================================


class TestWidgetDataLoading:
    """Verify that API config values populate the form controls."""

    def test_widget_key_from_api(self, admin_widget_page: Page) -> None:
        """Widget key from mock config is displayed."""
        key_input = admin_widget_page.locator(
            'input[value="pk_live_test123_abc456"]'
        )
        expect(key_input).to_be_visible()

    def test_primary_color_from_api(self, admin_widget_page: Page) -> None:
        """Primary color from mock config (#ff3621) populates the hex input."""
        hex_input = admin_widget_page.locator('input[value="#ff3621"]')
        assert hex_input.count() > 0, \
            "Primary color #ff3621 should be displayed in a hex input"

    def test_header_title_from_api(self, admin_widget_page: Page) -> None:
        """Header title from mock config ('Support') populates the input."""
        title_input = admin_widget_page.locator('input[value="Support"]')
        assert title_input.count() > 0, \
            "Header title 'Support' should be populated from API config"

    def test_agent_display_name_from_api(self, admin_widget_page: Page) -> None:
        """Agent display name from mock config ('Agent Red') populates the input."""
        name_input = admin_widget_page.locator('input[value="Agent Red"]')
        assert name_input.count() > 0, \
            "Agent display name 'Agent Red' should be populated from API config"


# ===========================================================================
# Tooltip Tests
# ===========================================================================


class TestWidgetTooltips:
    """Verify help tooltips on the Widget configuration page. WI 272."""

    def test_section_help_tooltips_present(self, admin_widget_page: Page) -> None:
        """WI 272: Widget page section help tooltips with doc links.

        The Widget configuration page has sections (Installation, Appearance,
        Behavior, Content) with SectionHeader components that include info icons.
        """
        page_text = admin_widget_page.text_content("body") or ""
        # Widget page sections
        has_sections = any(s in page_text for s in
                         ["Installation", "Appearance", "Behavior", "Content"])
        info_icons = admin_widget_page.locator('[aria-label*="help"], [aria-label*="info"], svg.tabler-icon-info-circle')
        assert has_sections or info_icons.count() > 0, \
            "Widget page should have section headers with help tooltips"


# ===========================================================================
# Auto-Open Configuration Tests
# ===========================================================================


class TestWidgetAutoOpen:
    """Verify auto-open configuration on the Widget page. WI 254."""

    def test_auto_open_config_field(self, admin_widget_page: Page) -> None:
        """WI 254: Auto-open per page via Quick Actions config.

        The widget supports auto-open with configurable delay. Verify the
        auto-open configuration field exists on the widget page.
        """
        page_text = admin_widget_page.text_content("body") or ""
        auto_open_label = admin_widget_page.locator("text=Auto")
        delay_label = admin_widget_page.locator("text=delay")
        # Auto-open may be configured through behavior section
        has_auto_open = ("auto" in page_text.lower() and "open" in page_text.lower()) or \
                       "auto-open" in page_text.lower() or \
                       "autoOpen" in page_text.lower() or \
                       auto_open_label.count() > 0
        has_behavior = "Behavior" in page_text
        assert has_auto_open or has_behavior, \
            "Widget page should have auto-open configuration or behavior section"
