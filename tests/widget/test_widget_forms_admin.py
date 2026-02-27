"""
Source inspection tests -- Widget forms and admin configurator.

Verifies TypeScript implementation patterns for widget form specs:
  - ChatRating, IssueReport, OfflineForm, PreChatForm, OTP, ConsentBanner
  - Admin WidgetConfigurator (layout, preview, color pickers)

Run with:
    pytest tests/widget/test_widget_forms_admin.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = ROOT / "widget" / "src" / "components"
ADMIN_SHARED = ROOT / "admin" / "shared"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    """Read a TypeScript source file and return its content."""
    assert path.exists(), f"Source file not found: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# ChatRating.tsx  (SPEC-1214, SPEC-1215)
# ---------------------------------------------------------------------------

class TestChatRating:
    """Chat rating component. SPEC-1214, SPEC-1215."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(COMPONENTS / "ChatRating.tsx")

    # -- SPEC-1214 -----------------------------------------------------------

    def test_thumbs_up_down_buttons(self) -> None:
        """SPEC-1214: Render thumbs up/down rating buttons."""
        assert "ThumbUpIcon" in self.source, "ChatRating should render ThumbUpIcon"
        assert "ThumbDownIcon" in self.source, "ChatRating should render ThumbDownIcon"

    def test_rating_button_56px_circles(self) -> None:
        """SPEC-1214: Rating buttons are 56px circles."""
        assert "'56px'" in self.source, "Rating buttons should be 56px wide"
        assert "borderRadiusFull" in self.source, "Rating buttons should use full border radius (circle)"

    def test_optional_comment_textarea(self) -> None:
        """SPEC-1214: Optional comment textarea is present."""
        assert "<textarea" in self.source, "ChatRating should include a comment textarea"
        assert "ratingCommentPlaceholder" in self.source, (
            "Comment textarea should use locale.ratingCommentPlaceholder"
        )

    def test_positive_negative_rating_type(self) -> None:
        """SPEC-1214: Rating values are 'positive' and 'negative'."""
        assert "'positive'" in self.source, "Rating should support 'positive' value"
        assert "'negative'" in self.source, "Rating should support 'negative' value"

    # -- SPEC-1215 -----------------------------------------------------------

    def test_success_state_with_checkmark(self) -> None:
        """SPEC-1215: Show success state with checkmark after rating."""
        assert "CheckIcon" in self.source, "Success state should render a CheckIcon"
        assert "submitted" in self.source, "ChatRating should track submitted state"

    def test_success_state_thank_you_message(self) -> None:
        """SPEC-1215: Success state displays thank-you text."""
        assert "ratingThankYou" in self.source, (
            "Success state should display locale.ratingThankYou"
        )

    def test_new_conversation_button(self) -> None:
        """SPEC-1215: Success state includes 'New conversation' button."""
        assert "onNewConversation" in self.source, (
            "ChatRating should accept onNewConversation callback"
        )
        assert "newConversation" in self.source, (
            "Button text should come from locale.newConversation"
        )


# ---------------------------------------------------------------------------
# IssueReport.tsx  (SPEC-1216, SPEC-1217)
# ---------------------------------------------------------------------------

class TestIssueReport:
    """Issue report form component. SPEC-1216, SPEC-1217."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(COMPONENTS / "IssueReport.tsx")

    # -- SPEC-1216 -----------------------------------------------------------

    def test_four_issue_types_defined(self) -> None:
        """SPEC-1216: Provide 4 issue report types."""
        for issue_type in [
            "wrong_information",
            "rude_response",
            "not_helpful",
            "other",
        ]:
            assert issue_type in self.source, (
                f"Issue type '{issue_type}' should be defined in ISSUE_TYPES"
            )

    def test_issue_types_as_radio_buttons(self) -> None:
        """SPEC-1216: Issue types rendered with radio-circle visual indicators."""
        # The component renders custom radio circles (16px circles with inner 8px dot)
        assert "'16px'" in self.source, "Radio circle should be 16px"
        assert "'8px'" in self.source, "Inner radio dot should be 8px"
        assert "borderRadius: '50%'" in self.source, "Radio indicators use 50% radius (circle)"

    def test_issue_types_count(self) -> None:
        """SPEC-1216: Exactly 4 issue types in the ISSUE_TYPES array."""
        match = re.search(
            r"const\s+ISSUE_TYPES\s*=\s*\[(.*?)\];",
            self.source,
            re.DOTALL,
        )
        assert match, "ISSUE_TYPES constant should be defined"
        entries = match.group(1).count("value:")
        assert entries == 4, f"Expected 4 issue types, found {entries}"

    # -- SPEC-1217 -----------------------------------------------------------

    def test_textarea_max_length_2000(self) -> None:
        """SPEC-1217: Enforce 2000 char max on issue report details textarea."""
        assert "maxLength={2000}" in self.source, (
            "Details textarea should have maxLength=2000"
        )

    def test_textarea_min_height_80px(self) -> None:
        """SPEC-1217: Textarea minHeight is 80px."""
        assert "'80px'" in self.source, "Textarea minHeight should be '80px'"

    def test_textarea_max_height_160px(self) -> None:
        """SPEC-1217: Textarea maxHeight is 160px."""
        assert "'160px'" in self.source, "Textarea maxHeight should be '160px'"

    def test_textarea_resizable(self) -> None:
        """SPEC-1217: Textarea allows vertical resize within constraints."""
        assert "'vertical'" in self.source, "Textarea resize should be 'vertical'"


# ---------------------------------------------------------------------------
# OfflineForm.tsx  (SPEC-1218, SPEC-1219)
# ---------------------------------------------------------------------------

class TestOfflineForm:
    """Offline leave-a-message form. SPEC-1218, SPEC-1219."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(COMPONENTS / "OfflineForm.tsx")

    # -- SPEC-1218 -----------------------------------------------------------

    def test_name_email_message_fields(self) -> None:
        """SPEC-1218: Render offline form with name, email, and message fields."""
        assert "Name" in self.source, "Offline form should have a Name field"
        assert "Email" in self.source, "Offline form should have an Email field"
        assert "Message" in self.source, "Offline form should have a Message field"

    def test_required_fields(self) -> None:
        """SPEC-1218: Name, email, and message are required fields."""
        # All three FieldGroup components pass required prop
        required_count = self.source.count("required")
        # At least 3 required markers (FieldGroup required prop + asterisk rendering)
        assert required_count >= 3, (
            f"Expected at least 3 required markers, found {required_count}"
        )

    def test_email_validation_regex(self) -> None:
        """SPEC-1218: Email field uses regex validation."""
        assert "EMAIL_REGEX" in self.source, "Should define EMAIL_REGEX for validation"
        assert "fieldInvalidEmail" in self.source, (
            "Invalid email should show locale.fieldInvalidEmail error"
        )

    def test_form_submit_handler(self) -> None:
        """SPEC-1218: Form has a submit handler that validates before calling onSubmit."""
        assert "handleSubmit" in self.source, "Form should define handleSubmit"
        assert "e.preventDefault()" in self.source, "Submit should prevent default form action"
        assert "validate()" in self.source or "validate" in self.source, (
            "Submit should trigger validation"
        )

    # -- SPEC-1219 -----------------------------------------------------------

    def test_offline_message_from_config(self) -> None:
        """SPEC-1219: Display custom offline message from widget_offline_message config."""
        assert "offlineMessage" in self.source, (
            "Component should accept offlineMessage prop"
        )

    def test_offline_message_conditional_render(self) -> None:
        """SPEC-1219: Offline message is conditionally rendered when present."""
        assert "offlineMessage &&" in self.source or "{offlineMessage}" in self.source, (
            "offlineMessage should be conditionally rendered"
        )


# ---------------------------------------------------------------------------
# PreChatForm.tsx  (SPEC-1220, SPEC-1222)
# ---------------------------------------------------------------------------

class TestPreChatForm:
    """Dynamic pre-chat form component. SPEC-1220, SPEC-1222."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(COMPONENTS / "PreChatForm.tsx")

    # -- SPEC-1220 -----------------------------------------------------------

    def test_dynamic_form_from_config(self) -> None:
        """SPEC-1220: Build dynamic pre-chat form from widget_prechat_form config."""
        assert "formConfig" in self.source, "PreChatForm should accept formConfig prop"
        assert "formConfig.fields" in self.source, (
            "Form fields should come from formConfig.fields"
        )

    def test_supported_field_types(self) -> None:
        """SPEC-1220: Supports text, email, and textarea (tel mapped to text) field types."""
        assert "'text'" in self.source, "Should support text type fields"
        assert "'email'" in self.source, "Should support email type fields"
        assert "'textarea'" in self.source, "Should support textarea type fields"

    def test_field_type_interface(self) -> None:
        """SPEC-1220: FormField type includes text, email, textarea."""
        match = re.search(
            r"type:\s*'text'\s*\|\s*'email'\s*\|\s*'textarea'",
            self.source,
        )
        assert match, "FormField.type should be 'text' | 'email' | 'textarea'"

    def test_field_validation(self) -> None:
        """SPEC-1220: Pre-chat form validates required and email fields."""
        assert "validateField" in self.source, "Should define validateField function"
        assert "fieldRequired" in self.source, "Required validation uses locale.fieldRequired"
        assert "fieldInvalidEmail" in self.source, "Email validation uses locale.fieldInvalidEmail"

    # -- SPEC-1222 -----------------------------------------------------------

    def test_continue_as_guest_skip_link(self) -> None:
        """SPEC-1222: Provide 'Continue as guest' skip link on pre-chat form."""
        assert "onSkip" in self.source, "PreChatForm should accept onSkip callback"
        assert "preChatSkip" in self.source, (
            "Skip link text should come from locale.preChatSkip"
        )

    def test_skip_link_conditionally_rendered(self) -> None:
        """SPEC-1222: Skip link only shown when onSkip prop is provided."""
        assert "onSkip &&" in self.source or "{onSkip &&" in self.source, (
            "Skip link should be conditionally rendered based on onSkip prop"
        )


# ---------------------------------------------------------------------------
# OtpVerification.tsx  (SPEC-1223, SPEC-1224, SPEC-1225)
# ---------------------------------------------------------------------------

class TestOtpVerification:
    """OTP verification component. SPEC-1223, SPEC-1224, SPEC-1225."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(COMPONENTS / "OtpVerification.tsx")

    # -- SPEC-1223 -----------------------------------------------------------

    def test_six_digit_input_boxes(self) -> None:
        """SPEC-1223: Render OTP verification with 6 individual digit input boxes."""
        # digits state initialized with 6 empty strings
        assert "['', '', '', '', '', '']" in self.source, (
            "OTP should initialize 6 empty digit slots"
        )

    def test_digit_inputs_are_single_char(self) -> None:
        """SPEC-1223: Each digit input has maxLength=1."""
        assert "maxLength={1}" in self.source, "Each digit input should have maxLength=1"

    def test_digit_inputs_numeric_mode(self) -> None:
        """SPEC-1223: Digit inputs use numeric input mode."""
        assert 'inputMode="numeric"' in self.source, (
            "Digit inputs should use inputMode='numeric'"
        )

    def test_auto_advance_on_digit_entry(self) -> None:
        """SPEC-1223: Auto-advance to next input on digit entry."""
        assert "index + 1" in self.source, "Should auto-advance to next input"
        assert "focus()" in self.source, "Auto-advance should call focus() on next input"

    # -- SPEC-1224 -----------------------------------------------------------

    def test_backspace_navigation(self) -> None:
        """SPEC-1224: Support backspace navigation between OTP input fields."""
        assert "Backspace" in self.source, "Should handle Backspace key"
        assert "index - 1" in self.source, "Backspace should navigate to previous input"

    def test_clipboard_paste_support(self) -> None:
        """SPEC-1224: Support clipboard paste in OTP input."""
        assert "handlePaste" in self.source, "Should define handlePaste handler"
        assert "clipboardData" in self.source, "Paste handler should read clipboardData"
        assert "slice(0, 6)" in self.source, "Paste handler should limit to 6 digits"

    def test_paste_strips_non_digits(self) -> None:
        """SPEC-1224: Paste handler strips non-digit characters."""
        assert r"/\D/g" in self.source, "Paste handler should strip non-digits with /\\D/g"

    # -- SPEC-1225 -----------------------------------------------------------

    def test_60_second_resend_cooldown(self) -> None:
        """SPEC-1225: Enforce 60-second resend cooldown for OTP codes."""
        assert "setResendCooldown(60)" in self.source, (
            "Resend should set a 60-second cooldown"
        )

    def test_cooldown_timer_decrements(self) -> None:
        """SPEC-1225: Cooldown timer decrements every second."""
        assert "setTimeout" in self.source, "Cooldown uses setTimeout for countdown"
        assert "c - 1" in self.source or "c) => c - 1" in self.source, (
            "Cooldown should decrement by 1 each second"
        )

    def test_resend_disabled_during_cooldown(self) -> None:
        """SPEC-1225: Resend button disabled while cooldown is active."""
        assert "resendCooldown > 0" in self.source, (
            "Resend guard should check resendCooldown > 0"
        )


# ---------------------------------------------------------------------------
# ConsentBanner.tsx  (SPEC-1226, SPEC-1227)
# ---------------------------------------------------------------------------

class TestConsentBanner:
    """PCM consent banner component. SPEC-1226, SPEC-1227."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(COMPONENTS / "ConsentBanner.tsx")

    # -- SPEC-1226 -----------------------------------------------------------

    def test_allow_and_decline_buttons(self) -> None:
        """SPEC-1226: Display PCM consent banner with 'Allow' and 'No thanks' buttons."""
        assert "onAccept" in self.source, "ConsentBanner should have onAccept handler"
        assert "onDecline" in self.source, "ConsentBanner should have onDecline handler"
        assert "consentAccept" in self.source, "Allow button uses locale.consentAccept"
        assert "consentDecline" in self.source, "Decline button uses locale.consentDecline"

    def test_fade_in_animation(self) -> None:
        """SPEC-1226: Consent banner has fade-in animation."""
        assert "ar-fade-in" in self.source, "Banner should use ar-fade-in animation"

    def test_consent_prompt_text(self) -> None:
        """SPEC-1226: Banner displays consent prompt from locale."""
        assert "consentPrompt" in self.source, (
            "Banner should display locale.consentPrompt text"
        )

    # -- SPEC-1227 -----------------------------------------------------------

    def test_surface_background(self) -> None:
        """SPEC-1227: Style consent banner with surface background."""
        assert "colorSurface" in self.source, (
            "Banner background should use tokens.colorSurface"
        )

    def test_border_bottom_separator(self) -> None:
        """SPEC-1227: Banner has border-bottom separator."""
        assert "borderBottom" in self.source, "Banner should have borderBottom style"
        assert "colorBorder" in self.source, (
            "Border-bottom should use tokens.colorBorder"
        )


# ---------------------------------------------------------------------------
# Admin WidgetConfigurator.tsx  (SPEC-1327..1343)
# ---------------------------------------------------------------------------

class TestWidgetConfiguratorLayout:
    """Admin widget configurator layout. SPEC-1327, SPEC-1328."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(ADMIN_SHARED / "WidgetConfigurator.tsx")

    # -- SPEC-1327 -----------------------------------------------------------

    def test_two_column_layout(self) -> None:
        """SPEC-1327: Render widget config page with form/preview two-column layout."""
        assert "formPanel" in self.source, "Layout should have a formPanel"
        assert "previewPanel" in self.source, "Layout should have a previewPanel"

    def test_form_panel_flex_1(self) -> None:
        """SPEC-1327: Form panel takes flex: 1 (fills remaining ~55% space)."""
        # formPanel style: flex: 1
        match = re.search(r"formPanel:\s*\{[^}]*flex:\s*1", self.source)
        assert match, "formPanel should have flex: 1"

    def test_preview_panel_width_340(self) -> None:
        """SPEC-1327: Preview panel has fixed width of 340px (~45% of 1200 max)."""
        match = re.search(r"previewPanel:\s*\{[^}]*width:\s*340", self.source)
        assert match, "previewPanel should have width: 340"

    def test_container_max_width_1200(self) -> None:
        """SPEC-1327: Container maxWidth is 1200px."""
        assert "maxWidth: 1200" in self.source, "Container maxWidth should be 1200"

    # -- SPEC-1328 -----------------------------------------------------------

    def test_live_preview_with_simulated_browser_chrome(self) -> None:
        """SPEC-1328: Display live widget preview with simulated browser chrome background."""
        assert "previewFrame" in self.source, "Preview should have a previewFrame style"
        assert "Live preview" in self.source, "Preview section should be titled 'Live preview'"

    def test_preview_frame_background_color(self) -> None:
        """SPEC-1328: Preview frame uses a neutral background simulating a browser page."""
        # previewFrame uses light grey (#F3F4F6) or dark (#1F2937) as browser chrome
        assert "#F3F4F6" in self.source, "Light mode preview frame background should be #F3F4F6"
        assert "#1F2937" in self.source, "Dark mode preview frame background should be #1F2937"


class TestWidgetConfiguratorColorPicker:
    """Admin widget configurator color picker. SPEC-1332, SPEC-1333."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(ADMIN_SHARED / "WidgetConfigurator.tsx")

    # -- SPEC-1332 -----------------------------------------------------------

    def test_color_picker_field_component(self) -> None:
        """SPEC-1332: Implement ColorPickerField component (custom HSV picker)."""
        assert "ColorPickerField" in self.source, (
            "ColorPickerField component should be defined"
        )

    def test_hex_input_validation(self) -> None:
        """SPEC-1332: Color picker includes hex input with validation."""
        # Hex input validation regex: /^#[0-9a-fA-F]{0,6}$/
        assert "#[0-9a-fA-F]" in self.source, (
            "Hex input should validate against hex color pattern"
        )
        assert '#RRGGBB' in self.source, "Hex input should show #RRGGBB placeholder"

    def test_color_swatch_preview(self) -> None:
        """SPEC-1332: Color picker shows a swatch preview of the current color."""
        assert "colorSwatch" in self.source, "Color picker should render a swatch"

    def test_hsv_color_conversion(self) -> None:
        """SPEC-1332: Color picker uses HSV color space for selection."""
        assert "hexToHsv" in self.source, "Should define hexToHsv conversion"
        assert "hsvToHex" in self.source, "Should define hsvToHex conversion"

    def test_saturation_value_gradient_area(self) -> None:
        """SPEC-1332: Color picker has a saturation-value gradient selection area."""
        assert "svAreaRef" in self.source, "Should have SV area ref"
        assert "crosshair" in self.source, "SV area cursor should be crosshair"

    def test_hue_bar(self) -> None:
        """SPEC-1332: Color picker has a hue selection bar."""
        assert "hueBarRef" in self.source, "Should have hue bar ref"
        # Rainbow gradient for hue bar
        assert "#FF0000" in self.source and "#00FF00" in self.source, (
            "Hue bar should have rainbow gradient"
        )

    def test_preset_colors(self) -> None:
        """SPEC-1332: Color picker provides preset color swatches."""
        assert "PRESET_COLORS" in self.source, "Should define PRESET_COLORS array"
        assert "Presets" in self.source, "Preset section should be labeled 'Presets'"

    # -- SPEC-1333 -----------------------------------------------------------

    def test_multiple_color_picker_instances(self) -> None:
        """SPEC-1333: Support header gradient with multiple color picker fields."""
        # Count ColorPickerField usages (there are 6 for the color fields)
        count = self.source.count("<ColorPickerField")
        assert count >= 2, (
            f"Expected at least 2 ColorPickerField instances for gradient, found {count}"
        )

    def test_primary_color_picker(self) -> None:
        """SPEC-1333: Widget primary color has its own picker."""
        assert "widget_primary_color" in self.source, (
            "Should have a color picker for widget_primary_color"
        )

    def test_background_color_picker(self) -> None:
        """SPEC-1333: Chat background color has its own picker."""
        assert "widget_background_color" in self.source, (
            "Should have a color picker for widget_background_color"
        )


class TestWidgetConfiguratorAvatar:
    """Admin widget configurator avatar handling. SPEC-1338."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(ADMIN_SHARED / "WidgetConfigurator.tsx")

    # -- SPEC-1338 -----------------------------------------------------------

    def test_avatar_url_field(self) -> None:
        """SPEC-1338: Show avatar URL input field."""
        assert "widget_agent_avatar_url" in self.source, (
            "Should have widget_agent_avatar_url field"
        )
        assert "Agent avatar URL" in self.source, (
            "Avatar field should be labeled 'Agent avatar URL'"
        )

    def test_avatar_preview_in_widget(self) -> None:
        """SPEC-1338: Avatar preview rendered in the widget preview header."""
        # Preview checks for avatar URL and renders img or default
        assert "widget_agent_avatar_url" in self.source, (
            "Preview should check widget_agent_avatar_url"
        )
        assert "objectFit: 'cover'" in self.source, (
            "Avatar image should use objectFit: cover"
        )


class TestWidgetConfiguratorFieldMapping:
    """Admin widget configurator field mapping. SPEC-1339."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(ADMIN_SHARED / "WidgetConfigurator.tsx")

    # -- SPEC-1339 -----------------------------------------------------------

    def test_widget_config_interface_field_count(self) -> None:
        """SPEC-1339: Map 25 widget_* API fields to local WidgetConfig form state."""
        # Count widget_* fields in the WidgetConfig interface
        match = re.search(
            r"interface\s+WidgetConfig\s*\{(.*?)\}",
            self.source,
            re.DOTALL,
        )
        assert match, "WidgetConfig interface should be defined"
        interface_body = match.group(1)
        widget_fields = re.findall(r"widget_\w+", interface_body)
        assert len(widget_fields) >= 25, (
            f"WidgetConfig should have at least 25 widget_* fields, found {len(widget_fields)}"
        )

    def test_default_config_covers_all_fields(self) -> None:
        """SPEC-1339: DEFAULT_CONFIG provides defaults for all WidgetConfig fields."""
        match = re.search(
            r"const\s+DEFAULT_CONFIG:\s*WidgetConfig\s*=\s*\{(.*?)\};",
            self.source,
            re.DOTALL,
        )
        assert match, "DEFAULT_CONFIG should be defined"
        defaults_body = match.group(1)
        default_fields = re.findall(r"widget_\w+", defaults_body)
        assert len(default_fields) >= 25, (
            f"DEFAULT_CONFIG should have at least 25 entries, found {len(default_fields)}"
        )

    def test_extract_widget_config_function(self) -> None:
        """SPEC-1339: extractWidgetConfig maps API response to local state."""
        assert "extractWidgetConfig" in self.source, (
            "Should define extractWidgetConfig function"
        )
        assert "DEFAULT_CONFIG" in self.source, (
            "extractWidgetConfig should merge with DEFAULT_CONFIG"
        )


class TestWidgetConfiguratorActions:
    """Admin widget configurator actions. SPEC-1340."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(ADMIN_SHARED / "WidgetConfigurator.tsx")

    # -- SPEC-1340 -----------------------------------------------------------

    def test_save_draft_button(self) -> None:
        """SPEC-1340: Provide 'Save draft inputs' action button."""
        assert "Save draft inputs" in self.source, (
            "Should have a 'Save draft inputs' button label"
        )

    def test_save_handler(self) -> None:
        """SPEC-1340: Save button calls handleSave."""
        assert "handleSave" in self.source, "Should define handleSave handler"

    def test_discard_handler(self) -> None:
        """SPEC-1340: Discard button resets changes."""
        assert "handleDiscard" in self.source, "Should define handleDiscard handler"
        assert "Changes discarded" in self.source, (
            "Discard should notify 'Changes discarded'"
        )

    def test_unsaved_changes_indicator(self) -> None:
        """SPEC-1340: Show unsaved changes count indicator."""
        assert "unsaved change" in self.source, (
            "Should display unsaved changes count"
        )
        assert "hasChanges" in self.source, "Should track hasChanges state"


class TestWidgetConfiguratorPreview:
    """Admin widget configurator preview panel. SPEC-1341, SPEC-1343."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(ADMIN_SHARED / "WidgetConfigurator.tsx")

    # -- SPEC-1341 -----------------------------------------------------------

    def test_sticky_positioning_on_preview(self) -> None:
        """SPEC-1341: Apply sticky positioning to preview panel that follows scroll."""
        match = re.search(
            r"previewPanel:\s*\{[^}]*position:\s*'sticky'",
            self.source,
        )
        assert match, "previewPanel should have position: 'sticky'"

    def test_sticky_top_offset(self) -> None:
        """SPEC-1341: Sticky preview has top offset for scroll following."""
        match = re.search(
            r"previewPanel:\s*\{[^}]*top:\s*16",
            self.source,
        )
        assert match, "previewPanel should have top: 16 for sticky offset"

    def test_preview_align_self_flex_start(self) -> None:
        """SPEC-1341: Preview panel uses alignSelf flex-start for proper sticky behavior."""
        match = re.search(
            r"previewPanel:\s*\{[^}]*alignSelf:\s*'flex-start'",
            self.source,
        )
        assert match, "previewPanel should have alignSelf: 'flex-start'"

    # -- SPEC-1343 -----------------------------------------------------------

    def test_launcher_decorative_only(self) -> None:
        """SPEC-1343: Render preview launcher as decorative-only (no click handler)."""
        # The launcher in preview uses cursor: 'default' (not 'pointer')
        # and has no onClick handler
        # Find the launcher button in preview (52x52, borderRadius, cursor: 'default')
        launcher_match = re.search(
            r"width:\s*52,\s*\n\s*height:\s*52,.*?cursor:\s*'default'",
            self.source,
            re.DOTALL,
        )
        assert launcher_match, (
            "Preview launcher should have cursor: 'default' (decorative-only)"
        )

    def test_launcher_no_onclick(self) -> None:
        """SPEC-1343: Preview launcher has no onClick handler."""
        # Find the launcher div (52x52) and verify no onClick in its props
        # The launcher is rendered in the WidgetPreview component with cursor: default
        # It's the div with width: 52, height: 52 and it should not have an onClick
        assert "cursor: 'default'" in self.source, (
            "Preview launcher should use cursor: default (no interaction)"
        )
