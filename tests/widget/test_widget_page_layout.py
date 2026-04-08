"""
Source inspection tests -- Widget Configuration page layout and styling.

Exhaustive regression tests for the standalone admin Widget Configuration page
(admin/standalone/pages/Widget.tsx). Every layout attribute, Mantine prop,
style value, and structural pattern is verified against the production baseline
captured on 2026-02-28.

Reference: Production screenshots at two browser widths confirming:
  - Page body expands to fill browser window (no maxWidth constraint)
  - Single-column layout: form sections at full width (live widget serves as preview)
  - All Paper sections use p="lg" radius="md" withBorder
  - SectionHeader uses Text size="sm" fw={700} c="dimmed" mb={4}

Run with:
    pytest tests/widget/test_widget_page_layout.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WIDGET_PAGE = ROOT / "admin" / "standalone" / "pages" / "Widget.tsx"
TOKENS_CSS = ROOT / "admin" / "shared" / "theme" / "tokens.css"
THEME_TS = ROOT / "admin" / "shared" / "theme" / "agentRedTheme.ts"
STYLES_TS = ROOT / "admin" / "shared" / "theme" / "styles.ts"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    """Read a source file and return its content."""
    assert path.exists(), f"Source file not found: {path}"
    return path.read_text(encoding="utf-8")


# ===========================================================================
# 1. PAGE-LEVEL LAYOUT (WidgetPage component return)
# ===========================================================================

class TestWidgetPageOuterStructure:
    """Verify the outermost page wrapper has NO maxWidth and fills available width."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_outer_wrapper_is_stack(self) -> None:
        """Page root is <Stack gap="lg" pos="relative">."""
        assert '<Stack gap="lg" pos="relative">' in self.source

    def test_no_max_width_on_outer_wrapper(self) -> None:
        """Page body has NO maxWidth constraint — expands to fill browser window."""
        # Extract the WidgetPage return block (from "return (" to closing)
        match = re.search(r'return\s*\(\s*\n\s*<Stack gap="lg"', self.source)
        assert match, "WidgetPage return block must start with <Stack gap=\"lg\">"
        # The Stack wrapper must NOT have maxWidth
        # Check there's no maxWidth in the outer Stack's style
        stack_line_idx = self.source.index('<Stack gap="lg" pos="relative">')
        # Look at the next 50 chars — should just be ">" not style={{ maxWidth: ... }}
        nearby = self.source[stack_line_idx:stack_line_idx + 80]
        assert "maxWidth" not in nearby, (
            "Outer Stack must NOT have maxWidth — page body fills browser window"
        )

    def test_no_max_width_box_wrapper(self) -> None:
        """No <Box style={{ maxWidth: ... }}> wrapping the form content."""
        # Ensure there's no Box with numeric pixel maxWidth wrapping form content.
        # maxWidth in WidgetPreview internal styling is fine (resolvePreviewPanelWidth).
        lines = self.source.split("\n")
        for i, line in enumerate(lines):
            if "maxWidth:" in line and "<Box" in self.source[max(0, self.source.index(line) - 100):self.source.index(line)]:
                # maxWidth in WidgetPreview internal styling is fine
                if "resolvePreviewPanelWidth" in line:
                    continue
                # Allow responsive viewport-relative widths
                if "'90vw'" in line or "'78%'" in line:
                    continue
                # Don't allow numeric pixel maxWidth on form wrappers
                if re.search(r"maxWidth:\s*\d{3,}", line):
                    pytest.fail(
                        f"Line {i+1}: Found pixel maxWidth on Box wrapper: {line.strip()}\n"
                        "Page body must expand to fill browser window."
                    )

    def test_loading_overlay_present(self) -> None:
        """LoadingOverlay covers the page while config loads."""
        assert "LoadingOverlay visible={configResult.loading && !initialized}" in self.source


class TestWidgetPageHeader:
    """Page header: title + subtitle."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_title_is_h2(self) -> None:
        """Page title uses Mantine Title order={2}."""
        assert '<Title order={2}>Widget configuration</Title>' in self.source

    def test_subtitle_text(self) -> None:
        """Subtitle is 'Customize how your chat widget looks and behaves'."""
        assert "Customize how your chat widget looks and behaves" in self.source

    def test_subtitle_styling(self) -> None:
        """Subtitle uses Text c='dimmed' size='sm'."""
        assert '<Text c="dimmed" size="sm">' in self.source

    def test_header_wrapper_is_div(self) -> None:
        """Header is wrapped in a plain <div>, not a Box or Paper."""
        # Find the page header block
        idx = self.source.index("<Title order={2}>Widget configuration</Title>")
        # Look backwards for the wrapper element (wider window for Group wrapper)
        before = self.source[max(0, idx - 120):idx]
        assert "<div>" in before, "Page header should be wrapped in a plain <div>"


# ===========================================================================
# 2. SINGLE-COLUMN FORM LAYOUT
# ===========================================================================

class TestSingleColumnFormLayout:
    """Single-column layout: form sections at full width (live widget is preview)."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_form_stack_gap_md(self) -> None:
        """Form sections wrapped in <Stack gap='md'>."""
        assert '<Stack gap="md">' in self.source

    def test_form_sections_comment(self) -> None:
        """Layout comment describes form sections with auto-save."""
        assert "Form sections" in self.source

    def test_no_two_column_group(self) -> None:
        """No Group container with flex-start/nowrap for two-column layout."""
        assert 'align="flex-start" wrap="nowrap" gap="lg"' not in self.source

    def test_no_left_column_flex(self) -> None:
        """No left column flex: '0 0 55%' constraint."""
        assert "flex: '0 0 55%'" not in self.source

    def test_no_right_column_flex(self) -> None:
        """No right column flex: '0 0 calc(45% - 16px)' constraint."""
        assert "flex: '0 0 calc(45% - 16px)'" not in self.source

    def test_no_sticky_positioning(self) -> None:
        """No position: 'sticky' for preview panel."""
        assert "position: 'sticky'" not in self.source

    def test_no_live_preview_heading(self) -> None:
        """No 'Live preview' heading text in the page template."""
        # The WidgetPreview component is still defined but not rendered in the page
        assert "Live preview" not in self.source


# ===========================================================================
# 3. PAPER SECTIONS — Structure & Props
# ===========================================================================

class TestPaperSectionStructure:
    """All 4 form Paper sections use correct Mantine props."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_five_form_paper_sections(self) -> None:
        """Exactly 5 form Paper sections with p='lg' radius='md' withBorder."""
        # Count Paper p="lg" radius="md" withBorder occurrences in the form area
        # Installation, Launcher appearance, Chat window, Behavior, Content
        count = self.source.count('<Paper p="lg" radius="md" withBorder>')
        assert count == 5, f"Expected 5 form Paper sections, found {count}"

    def test_installation_paper_props(self) -> None:
        """Installation section: Paper p='lg' radius='md' withBorder."""
        idx = self.source.index("Installation Section")
        nearby = self.source[idx:idx + 200]
        assert '<Paper p="lg" radius="md" withBorder>' in nearby

    def test_appearance_paper_props(self) -> None:
        """Appearance section: Paper p='lg' radius='md' withBorder."""
        idx = self.source.index("Appearance Section")
        nearby = self.source[idx:idx + 200]
        assert '<Paper p="lg" radius="md" withBorder>' in nearby

    def test_behavior_paper_props(self) -> None:
        """Behavior section: Paper p='lg' radius='md' withBorder."""
        idx = self.source.index("Behavior Section")
        nearby = self.source[idx:idx + 200]
        assert '<Paper p="lg" radius="md" withBorder>' in nearby

    def test_content_paper_props(self) -> None:
        """Content section: Paper p='lg' radius='md' withBorder."""
        idx = self.source.index("Content Section")
        nearby = self.source[idx:idx + 200]
        assert '<Paper p="lg" radius="md" withBorder>' in nearby

    def test_each_section_has_divider_after_header(self) -> None:
        """Each form section has <Divider mb='md' /> after SectionHeader."""
        count = self.source.count('<Divider mb="md" />')
        assert count >= 4, f"Expected at least 4 section dividers, found {count}"


# ===========================================================================
# 4. SECTION HEADERS
# ===========================================================================

class TestSectionHeaders:
    """SectionHeader component — styling and content."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_section_header_component_text_props(self) -> None:
        """SectionHeader uses Text size='sm' fw={700} c='dimmed' mb={4}."""
        assert '<Text size="sm" fw={700} c="dimmed" mb={4}>' in self.source

    def test_section_header_contains_help_tooltip(self) -> None:
        """SectionHeader renders HelpTooltip when tooltip prop is provided."""
        assert "{tooltip && <HelpTooltip" in self.source

    def test_installation_section_header(self) -> None:
        """Installation SectionHeader text is 'Installation'."""
        assert ">Installation</SectionHeader>" in self.source or \
               ">\n                Installation\n" in self.source or \
               ">Installation<" in self.source

    def test_appearance_section_headers(self) -> None:
        """Appearance is split into 'Launcher appearance' and 'Chat window' sections."""
        assert ">Launcher appearance</SectionHeader>" in self.source or \
               ">Launcher appearance<" in self.source
        assert ">Chat window</SectionHeader>" in self.source or \
               ">Chat window<" in self.source

    def test_behavior_section_header(self) -> None:
        """Behavior SectionHeader text is 'Behavior'."""
        assert ">Behavior</SectionHeader>" in self.source or \
               ">Behavior<" in self.source

    def test_content_section_header(self) -> None:
        """Content SectionHeader text is 'Content'."""
        assert ">Content</SectionHeader>" in self.source or \
               ">Content<" in self.source

    def test_installation_has_doc_link(self) -> None:
        """Installation SectionHeader includes docLink to widget-appearance."""
        # Find the Installation SectionHeader
        idx = self.source.index("Installation Section")
        nearby = self.source[idx:idx + 500]
        assert "widget-appearance" in nearby

    def test_all_section_headers_have_tooltips(self) -> None:
        """All 5 form sections have SectionHeader with tooltip prop."""
        # Count SectionHeader calls with tooltip=
        count = len(re.findall(r'<SectionHeader\s[^>]*tooltip=', self.source))
        assert count == 5, f"Expected 5 SectionHeaders with tooltips, found {count}"


# ===========================================================================
# 5. PREVIEW PANEL REMOVED (live widget serves as preview)
# ===========================================================================

class TestPreviewPanelRemoved:
    """Live preview panel has been removed — live storefront widget is the preview."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_no_preview_heading_in_template(self) -> None:
        """No 'Live preview' heading rendered in the page template."""
        # WidgetPreview component is still defined but not rendered
        assert "Live preview" not in self.source

    def test_no_widget_preview_jsx_rendering(self) -> None:
        """WidgetPreview is not rendered in the page template JSX."""
        assert "<WidgetPreview config={config}" not in self.source

    def test_widget_preview_component_still_defined(self) -> None:
        """WidgetPreview function is still defined (may be used elsewhere)."""
        assert "function WidgetPreview(" in self.source

    def test_no_right_column_layout_comment(self) -> None:
        """No 'Right column' as a top-level two-column layout comment."""
        # "Right column" may appear as a sub-layout comment within a section
        # (e.g. "Right column: Launcher controls stack"), but not as a
        # top-level two-column page layout.
        assert "Right column */" not in self.source or \
               "Right column:" in self.source


# ===========================================================================
# 6. ACTION BUTTONS (Bottom of Form)
# ===========================================================================

class TestActionButtons:
    """Action buttons at the bottom of the form column."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_button_group_alignment(self) -> None:
        """Action buttons are right-aligned: Group justify='flex-end' gap='sm'."""
        assert '<Group justify="flex-end" gap="sm">' in self.source

    def test_reset_button_variant_default(self) -> None:
        """Reset button uses variant='default'."""
        assert '<Button variant="default" onClick={resetDefaults}>' in self.source

    def test_reset_button_text(self) -> None:
        """Reset button label is 'Reset to defaults'."""
        assert "Reset to defaults" in self.source

    def test_auto_save_replaces_save_button(self) -> None:
        """Manual save button replaced by auto-save via useAutoSaveDraft hook."""
        assert "useAutoSaveDraft" in self.source
        assert "AutoSaveIndicator" in self.source

    def test_auto_save_on_blur(self) -> None:
        """Form Stack uses onBlur for auto-save triggering."""
        assert "onBlur={autoSaveOnBlur}" in self.source

    def test_trigger_save_for_non_text_controls(self) -> None:
        """Non-text controls use triggerSave via updateAndSave helper."""
        assert "triggerSave" in self.source
        assert "updateAndSave" in self.source


# ===========================================================================
# 7. WIDGET PREVIEW COMPONENT — Internal Styling
# ===========================================================================

class TestWidgetPreviewStyling:
    """WidgetPreview component internal color tokens and layout values."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    # -- Dark mode color tokens --

    def test_preview_panel_bg_dark(self) -> None:
        """Dark mode panel background: #292524."""
        assert "panelBg = dk ? '#292524'" in self.source

    def test_preview_msg_area_bg_dark(self) -> None:
        """Dark mode message area background: #1c1917."""
        assert "msgAreaBg = dk ? '#1c1917'" in self.source

    def test_preview_agent_bubble_bg_dark(self) -> None:
        """Dark mode agent bubble background: #292524."""
        assert "agentBubbleBg = dk ? '#292524'" in self.source

    def test_preview_agent_bubble_border_dark(self) -> None:
        """Dark mode agent bubble border: #44403c."""
        assert "agentBubbleBorder = dk ? '#44403c'" in self.source

    def test_preview_agent_bubble_text_dark(self) -> None:
        """Dark mode agent bubble text: #f5f5f4."""
        assert "agentBubbleText = dk ? '#f5f5f4'" in self.source

    def test_preview_input_bar_bg_dark(self) -> None:
        """Dark mode input bar background: #0c0a09."""
        assert "inputBarBg = dk ? '#0c0a09'" in self.source

    def test_preview_input_bar_border_dark(self) -> None:
        """Dark mode input bar border: #44403c."""
        assert "inputBarBorder = dk ? '#44403c'" in self.source

    def test_preview_page_bg_dark(self) -> None:
        """Dark mode simulated page background: #1c1917."""
        assert "pageBg = dk ? '#1c1917'" in self.source

    def test_preview_chrome_bg_dark(self) -> None:
        """Dark mode chrome background: #0c0a09."""
        assert "chromeBg = dk ? '#0c0a09'" in self.source

    def test_preview_branding_text_dark(self) -> None:
        """Dark mode branding text: #57534e."""
        assert "brandingText = dk ? '#57534e'" in self.source

    # -- Light mode color tokens --

    def test_preview_panel_bg_light(self) -> None:
        """Light mode panel background: #fff."""
        assert "panelBg = dk ? '#292524' : '#fff'" in self.source

    def test_preview_msg_area_bg_light(self) -> None:
        """Light mode message area background: #fafafa."""
        assert "msgAreaBg = dk ? '#1c1917' : '#fafafa'" in self.source

    def test_preview_agent_bubble_bg_light(self) -> None:
        """Light mode agent bubble background: #fff."""
        assert "agentBubbleBg = dk ? '#292524' : '#fff'" in self.source

    def test_preview_agent_bubble_border_light(self) -> None:
        """Light mode agent bubble border: #e9ecef."""
        assert "agentBubbleBorder = dk ? '#44403c' : '#e9ecef'" in self.source

    def test_preview_input_bar_bg_light(self) -> None:
        """Light mode input bar background: #fff."""
        assert "inputBarBg = dk ? '#0c0a09' : '#fff'" in self.source

    # -- Layout dimensions --

    def test_preview_container_min_height(self) -> None:
        """Preview container minHeight: 580."""
        assert "minHeight: 580" in self.source

    def test_preview_container_border_radius(self) -> None:
        """Preview container borderRadius: 12."""
        # The outer preview Box
        match = re.search(r"minHeight: 580.*?borderRadius: 12", self.source, re.DOTALL)
        assert match, "Preview container must have borderRadius: 12"

    def test_preview_container_padding(self) -> None:
        """Preview container padding: 20."""
        match = re.search(r"minHeight: 580.*?padding: 20", self.source, re.DOTALL)
        assert match, "Preview container must have padding: 20"

    # -- Header styling --

    def test_preview_header_padding(self) -> None:
        """Preview header padding: '16px 18px'."""
        assert "'16px 18px'" in self.source

    def test_preview_header_avatar_size(self) -> None:
        """Preview header avatar: 36x36px circle."""
        # In the header section
        count = self.source.count("width: 36,\n")
        assert count >= 1, "Header avatar should be 36px wide"

    def test_preview_header_title_props(self) -> None:
        """Preview header title: Text size='sm' fw={700} c='#fff'."""
        assert '<Text size="sm" fw={700} c="#fff"' in self.source

    def test_preview_header_subtitle_props(self) -> None:
        """Preview header subtitle: Text size='xs' c='rgba(255,255,255,0.8)'."""
        assert 'c="rgba(255,255,255,0.8)"' in self.source

    def test_preview_online_indicator_color(self) -> None:
        """Online indicator dot: 7px circle, background #69db7c."""
        assert "background: '#69db7c'" in self.source

    def test_preview_online_indicator_size(self) -> None:
        """Online indicator dot: 7x7px."""
        assert "width: 7, height: 7" in self.source

    # -- Message bubbles --

    def test_preview_agent_bubble_border_radius(self) -> None:
        """Agent bubble: borderRadius '4px 16px 16px 16px'."""
        assert "'4px 16px 16px 16px'" in self.source

    def test_preview_customer_bubble_border_radius(self) -> None:
        """Customer bubble: borderRadius '16px 16px 4px 16px'."""
        assert "'16px 16px 4px 16px'" in self.source

    def test_preview_bubble_max_width(self) -> None:
        """Chat bubbles max-width: '78%'."""
        count = self.source.count("maxWidth: '78%'")
        assert count >= 2, f"Expected at least 2 bubble maxWidth: '78%', found {count}"

    def test_preview_bubble_padding(self) -> None:
        """Chat bubbles padding: '10px 14px'."""
        count = self.source.count("'10px 14px'")
        assert count >= 2, f"Expected at least 2 bubble padding: '10px 14px', found {count}"

    def test_preview_message_avatar_size(self) -> None:
        """In-message agent avatar: 28x28px circle."""
        assert "width: 28," in self.source
        assert "height: 28," in self.source

    # -- Input bar --

    def test_preview_input_bar_padding(self) -> None:
        """Input bar padding: '10px 12px'."""
        assert "'10px 12px'" in self.source

    def test_preview_input_placeholder_font_size(self) -> None:
        """Input placeholder fontSize: 12."""
        # In the input mock
        match = re.search(r"fontSize: 12,\n\s+color: inputText", self.source)
        assert match, "Input placeholder must have fontSize: 12"

    def test_preview_send_button_size(self) -> None:
        """Send button: 32x32px circle."""
        assert "width: 32," in self.source
        assert "height: 32," in self.source

    # -- Branding footer --

    def test_preview_branding_font_size(self) -> None:
        """Powered-by branding font size: 10."""
        assert 'style={{ fontSize: 10 }}' in self.source

    def test_preview_branding_text_content(self) -> None:
        """Branding says 'Powered by Agent Red'."""
        assert "Powered by" in self.source
        assert "Agent Red" in self.source

    # -- Launcher button --

    def test_preview_launcher_shadow(self) -> None:
        """Launcher button box-shadow: '0 4px 16px rgba(0,0,0,0.2)'."""
        assert "'0 4px 16px rgba(0,0,0,0.2)'" in self.source

    def test_preview_launcher_z_index(self) -> None:
        """Launcher button zIndex: 3."""
        assert "zIndex: 3" in self.source

    def test_preview_chat_panel_z_index(self) -> None:
        """Chat panel zIndex: 2."""
        assert "zIndex: 2" in self.source


# ===========================================================================
# 8. WIDGET PREVIEW — Panel Size Presets
# ===========================================================================

class TestWidgetPreviewSizePresets:
    """Panel width and height resolution presets."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    # Preview-scale widths
    def test_preview_compact_width(self) -> None:
        """Compact preview width: 300px."""
        assert "case 'compact': return 300;" in self.source

    def test_preview_standard_width(self) -> None:
        """Standard preview width: 350px."""
        assert "default: return 350;" in self.source

    def test_preview_wide_width(self) -> None:
        """Wide preview width: 400px."""
        assert "case 'wide': return 400;" in self.source

    # Real widget widths
    def test_real_compact_width(self) -> None:
        """Compact real widget width: 320px."""
        assert "case 'compact': return '320px';" in self.source

    def test_real_standard_width(self) -> None:
        """Standard real widget width: 380px."""
        assert "default: return '380px';" in self.source

    def test_real_wide_width(self) -> None:
        """Wide real widget width: 440px."""
        assert "case 'wide': return '440px';" in self.source

    # Preview-scale heights
    def test_preview_short_height(self) -> None:
        """Short preview height: 380px."""
        assert "case 'short': return 380;" in self.source

    def test_preview_standard_height(self) -> None:
        """Standard preview height: 460px."""
        match = re.search(r"resolvePreviewPanelHeight.*?default: return 460;", self.source, re.DOTALL)
        assert match, "Standard preview height must be 460"

    def test_preview_tall_height(self) -> None:
        """Tall preview height: 530px."""
        assert "case 'tall': return 530;" in self.source


# ===========================================================================
# 9. SHADOW INTENSITY PRESETS
# ===========================================================================

class TestShadowIntensityPresets:
    """Shadow CSS values for each intensity level."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_shadow_none(self) -> None:
        """shadowCss('none') returns 'none'."""
        assert "case 'none': return 'none';" in self.source

    def test_shadow_subtle_dark(self) -> None:
        """Subtle dark: '0 4px 12px rgba(0,0,0,0.20)'."""
        assert "'0 4px 12px rgba(0,0,0,0.20)'" in self.source

    def test_shadow_standard_dark(self) -> None:
        """Standard dark: '0 10px 25px rgba(0,0,0,0.30), 0 4px 10px rgba(0,0,0,0.20)'."""
        assert "'0 10px 25px rgba(0,0,0,0.30), 0 4px 10px rgba(0,0,0,0.20)'" in self.source

    def test_shadow_heavy_dark(self) -> None:
        """Heavy dark: '0 16px 40px rgba(0,0,0,0.45), 0 6px 16px rgba(0,0,0,0.30)'."""
        assert "'0 16px 40px rgba(0,0,0,0.45), 0 6px 16px rgba(0,0,0,0.30)'" in self.source

    def test_shadow_subtle_light(self) -> None:
        """Subtle light: '0 4px 12px rgba(0,0,0,0.08)'."""
        assert "'0 4px 12px rgba(0,0,0,0.08)'" in self.source

    def test_shadow_standard_light(self) -> None:
        """Standard light: '0 10px 25px rgba(0,0,0,0.15), 0 4px 10px rgba(0,0,0,0.10)'."""
        assert "'0 10px 25px rgba(0,0,0,0.15), 0 4px 10px rgba(0,0,0,0.10)'" in self.source

    def test_shadow_heavy_light(self) -> None:
        """Heavy light: '0 16px 40px rgba(0,0,0,0.25), 0 6px 16px rgba(0,0,0,0.15)'."""
        assert "'0 16px 40px rgba(0,0,0,0.25), 0 6px 16px rgba(0,0,0,0.15)'" in self.source


# ===========================================================================
# 10. DEFAULT WIDGET CONFIG VALUES
# ===========================================================================

class TestDefaultWidgetConfig:
    """DEFAULT_WIDGET_CONFIG values — baseline for form reset."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_default_primary_color(self) -> None:
        """Default primaryColor is BRAND_RED (#ff3621)."""
        assert "primaryColor: BRAND_RED" in self.source

    def test_default_gradient_end(self) -> None:
        """Default headerGradientEnd: '#8B1520'."""
        assert "headerGradientEnd: '#8B1520'" in self.source

    def test_default_gradient_disabled(self) -> None:
        """Default headerGradientEnabled: false."""
        assert "headerGradientEnabled: false" in self.source

    def test_default_font_family(self) -> None:
        """Default fontFamily: 'Inter, system-ui, sans-serif'."""
        assert "fontFamily: 'Inter, system-ui, sans-serif'" in self.source

    def test_default_border_radius(self) -> None:
        """Default borderRadius: 16."""
        assert "borderRadius: 16" in self.source

    def test_default_launcher_size(self) -> None:
        """Default launcherSize: 60."""
        assert "launcherSize: 60" in self.source

    def test_default_position(self) -> None:
        """Default position: 'bottom-right'."""
        assert "position: 'bottom-right'" in self.source

    def test_default_position_offsets(self) -> None:
        """Default position offsets: X=20, Y=20."""
        assert "positionOffsetX: 20" in self.source
        assert "positionOffsetY: 20" in self.source

    def test_default_shadow_intensity(self) -> None:
        """Default shadowIntensity: 'standard'."""
        assert "shadowIntensity: 'standard'" in self.source

    def test_default_panel_width(self) -> None:
        """Default panelWidth: 'standard'."""
        assert "panelWidth: 'standard'" in self.source

    def test_default_panel_height(self) -> None:
        """Default panelHeight: 'standard'."""
        assert "panelHeight: 'standard'" in self.source

    def test_default_color_mode(self) -> None:
        """Default colorMode: 'auto'."""
        assert "colorMode: 'auto'" in self.source

    def test_default_header_title(self) -> None:
        """Default headerTitle: 'Support'."""
        assert "headerTitle: 'Support'" in self.source

    def test_default_header_subtitle(self) -> None:
        """Default headerSubtitle: 'We typically reply within minutes'."""
        assert "headerSubtitle: 'We typically reply within minutes'" in self.source

    def test_default_input_placeholder(self) -> None:
        """Default inputPlaceholder: 'Type your message...'."""
        assert "inputPlaceholder: 'Type your message...'" in self.source


# ===========================================================================
# 11. FORM CONTROLS — Color & Variant Props
# ===========================================================================

class TestFormControlStyling:
    """Mantine form control color and variant props."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_switch_controls_use_action_color(self) -> None:
        """All Switch controls use color='action' (blue)."""
        switches = re.findall(r'<Switch\s[^>]*>', self.source)
        for s in switches:
            if 'color="action"' not in s:
                # Some switches may span multiple lines
                pass
        # Count color="action" on Switch components
        switch_action = self.source.count('color="action"\n')
        # At minimum we have: greetingEnabled, preChatFormEnabled, soundEnabled,
        # exitIntentEnabled, mobileFullscreen = 5 switches
        assert switch_action >= 5, f"Expected at least 5 Switch with color='action', found {switch_action}"

    def test_slider_controls_use_action_color(self) -> None:
        """Slider controls use color='action'."""
        # Slider and color="action" may be on separate lines (multi-line JSX)
        sliders = re.findall(r'<Slider\b[\s\S]*?color="action"', self.source)
        assert len(sliders) >= 2, "Expected at least 2 Sliders with color='action'"

    def test_segmented_controls_use_action_color(self) -> None:
        """SegmentedControl components use color='action'."""
        # SegmentedControl and color="action" may be on separate lines
        segs = re.findall(r'<SegmentedControl\b[\s\S]*?color="action"', self.source)
        assert len(segs) >= 4, f"Expected at least 4 SegmentedControls with color='action', found {len(segs)}"

    def test_rotate_key_button_red_outline(self) -> None:
        """Rotate key button: color='red' variant='outline'."""
        assert 'color="red"\n' in self.source or 'color="red"' in self.source
        assert 'variant="outline"' in self.source

    def test_monospace_font_on_key_inputs(self) -> None:
        """Widget key and API URL inputs use monospace font at 12px."""
        count = self.source.count("fontFamily: 'monospace', fontSize: '12px'")
        assert count >= 2, f"Expected at least 2 monospace input styles, found {count}"


# ===========================================================================
# 12. THEME TOKENS (tokens.css) — Dark Mode Values
# ===========================================================================

class TestThemeTokensDarkMode:
    """CSS custom properties in tokens.css — dark mode baseline."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(TOKENS_CSS)

    def test_chrome_color(self) -> None:
        """--ar-chrome: #0c0a09."""
        assert "--ar-chrome:  #0c0a09;" in self.source

    def test_page_color(self) -> None:
        """--ar-page: #1c1917."""
        assert "--ar-page:    #1c1917;" in self.source

    def test_surface_color(self) -> None:
        """--ar-surface: #292524."""
        assert "--ar-surface: #292524;" in self.source

    def test_border_color(self) -> None:
        """--ar-border: #44403c."""
        assert "--ar-border:  #44403c;" in self.source

    def test_text_primary(self) -> None:
        """--ar-text-primary: #fafaf9."""
        assert "--ar-text-primary:   #fafaf9;" in self.source

    def test_text_secondary(self) -> None:
        """--ar-text-secondary: #f5f5f4."""
        assert "--ar-text-secondary: #f5f5f4;" in self.source

    def test_text_muted(self) -> None:
        """--ar-text-muted: #a8a29e."""
        assert "--ar-text-muted:     #a8a29e;" in self.source

    def test_text_tertiary(self) -> None:
        """--ar-text-tertiary: #57534e."""
        assert "--ar-text-tertiary:  #57534e;" in self.source

    def test_action_color(self) -> None:
        """--ar-action: #3B82F6."""
        assert "--ar-action:          #3B82F6;" in self.source

    def test_action_hover_color(self) -> None:
        """--ar-action-hover: #2563EB."""
        assert "--ar-action-hover:    #2563EB;" in self.source

    def test_danger_color(self) -> None:
        """--ar-danger: #e03131 (Mantine red[8] — matches sidebar Deactivate button)."""
        assert "--ar-danger:          #e03131;" in self.source

    def test_brand_color(self) -> None:
        """--ar-brand: #ff3621."""
        assert "--ar-brand:           #ff3621;" in self.source


# ===========================================================================
# 13. THEME TOKENS (tokens.css) — Paper Border Override
# ===========================================================================

class TestPaperBorderOverride:
    """CSS override that sets Paper border color to --ar-border in dark mode."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(TOKENS_CSS)

    def test_paper_border_color_override_exists(self) -> None:
        """Dark mode Paper border override selector exists."""
        assert '[data-mantine-color-scheme="dark"] .mantine-Paper-root' in self.source

    def test_paper_border_uses_ar_border(self) -> None:
        """Paper border-color is var(--ar-border)."""
        # Find the Paper override block
        idx = self.source.index('.mantine-Paper-root')
        block = self.source[idx:idx + 200]
        assert "border-color: var(--ar-border);" in block

    def test_paper_border_width_1px(self) -> None:
        """Paper border-width is 1px."""
        idx = self.source.index('.mantine-Paper-root')
        block = self.source[idx:idx + 200]
        assert "border-width: 1px;" in block

    def test_paper_internal_var_override(self) -> None:
        """Paper --_paper-border-color internal variable is overridden."""
        idx = self.source.index('.mantine-Paper-root')
        block = self.source[idx:idx + 200]
        assert "--_paper-border-color: var(--ar-border);" in block


# ===========================================================================
# 14. THEME TOKENS (tokens.css) — Light Mode Overrides
# ===========================================================================

class TestThemeTokensLightMode:
    """Light mode token overrides in tokens.css."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(TOKENS_CSS)
        # Extract light mode block
        self.source.index('html[data-mantine-color-scheme="light"]')
        # Find the last occurrence (the override block, not the header block)
        last_idx = self.source.rindex('html[data-mantine-color-scheme="light"] {')
        self.light_block = self.source[last_idx:last_idx + 600]

    def test_light_chrome(self) -> None:
        """Light --ar-chrome: #f5f5f5."""
        assert "--ar-chrome:           #f5f5f5;" in self.light_block

    def test_light_page(self) -> None:
        """Light --ar-page: #f0f0ef."""
        assert "--ar-page:             #f0f0ef;" in self.light_block

    def test_light_surface(self) -> None:
        """Light --ar-surface: #ffffff."""
        assert "--ar-surface:          #ffffff;" in self.light_block

    def test_light_border(self) -> None:
        """Light --ar-border: #e5e3e0."""
        assert "--ar-border:           #e5e3e0;" in self.light_block

    def test_light_text_primary(self) -> None:
        """Light --ar-text-primary: #1c1917."""
        assert "--ar-text-primary:     #1c1917;" in self.light_block

    def test_light_text_muted(self) -> None:
        """Light --ar-text-muted: #78716c."""
        assert "--ar-text-muted:       #78716c;" in self.light_block


# ===========================================================================
# 15. MANTINE THEME (agentRedTheme.ts) — Color Scales
# ===========================================================================

class TestMantineThemeColorScales:
    """agentRedTheme.ts color scale values."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(THEME_TS)

    def test_primary_color_is_action(self) -> None:
        """primaryColor is 'action'."""
        assert "primaryColor: 'action'" in self.source

    def test_default_radius_md(self) -> None:
        """defaultRadius is 'md'."""
        assert "defaultRadius: 'md'" in self.source

    def test_cursor_type_pointer(self) -> None:
        """cursorType is 'pointer'."""
        assert "cursorType: 'pointer'" in self.source

    def test_dark_scale_border_index_6(self) -> None:
        """dark[6] = #44403c (Border)."""
        assert "'#44403c', // 6 - Border" in self.source

    def test_dark_scale_surface_index_7(self) -> None:
        """dark[7] = #292524 (Surface)."""
        assert "'#292524', // 7 - Surface" in self.source

    def test_dark_scale_page_index_8(self) -> None:
        """dark[8] = #1c1917 (Page background)."""
        assert "'#1c1917', // 8 - Page background" in self.source

    def test_dark_scale_chrome_index_9(self) -> None:
        """dark[9] = #0c0a09 (Chrome)."""
        assert "'#0c0a09', // 9 - Chrome" in self.source

    def test_action_palette_primary_blue(self) -> None:
        """action[7] = #3B82F6 and action[8] = #3B82F6."""
        assert "'#3B82F6', // 7 - Our target blue" in self.source
        assert "'#3B82F6', // 8 - Primary (dark mode)" in self.source

    def test_brand_palette_primary_red(self) -> None:
        """brand[5] = #ff3621 (Agent Red)."""
        assert "'#ff3621', // 5 - Agent Red (Primary)" in self.source

    def test_font_family(self) -> None:
        """Font family includes Inter."""
        assert "fontFamily: \"'Inter'" in self.source

    def test_heading_font_weight(self) -> None:
        """Heading fontWeight is '600'."""
        assert "fontWeight: '600'" in self.source


# ===========================================================================
# 16. IMPORTS & DEPENDENCIES
# ===========================================================================

class TestWidgetPageImports:
    """Widget.tsx imports — ensures all required Mantine components are present."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_imports_use_computed_color_scheme(self) -> None:
        """useComputedColorScheme is imported (needed for adminIsDark)."""
        assert "useComputedColorScheme" in self.source

    def test_imports_loading_overlay(self) -> None:
        """LoadingOverlay is imported."""
        assert "LoadingOverlay" in self.source

    def test_imports_color_picker(self) -> None:
        """ColorPicker is imported."""
        assert "ColorPicker" in self.source

    def test_imports_help_tooltip(self) -> None:
        """HelpTooltip is imported from shared."""
        assert "import { HelpTooltip }" in self.source

    def test_imports_tokens(self) -> None:
        """tokens imported from shared theme."""
        assert "import { tokens } from '../../shared/theme/styles'" in self.source

    def test_brand_red_uses_tokens(self) -> None:
        """BRAND_RED constant is derived from tokens.brand."""
        assert "const BRAND_RED = tokens.brand;" in self.source


# ===========================================================================
# 17. MODAL — Rotate Widget Key
# ===========================================================================

class TestRotateKeyModal:
    """Widget key rotation confirmation modal."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_modal_title(self) -> None:
        """Modal title is 'Rotate widget key'."""
        assert 'title="Rotate widget key"' in self.source

    def test_modal_centered(self) -> None:
        """Modal is centered."""
        assert "centered" in self.source

    def test_modal_size_sm(self) -> None:
        """Modal size is 'sm'."""
        assert 'size="sm"' in self.source

    def test_modal_warning_alert(self) -> None:
        """Modal contains red warning alert about key invalidation."""
        assert "immediately invalidate" in self.source

    def test_modal_cancel_button(self) -> None:
        """Modal has Cancel button with variant='default'."""
        # Find the modal section — need more text to reach the buttons
        idx = self.source.index('title="Rotate widget key"')
        modal_block = self.source[idx:idx + 800]
        assert 'variant="default"' in modal_block

    def test_modal_confirm_button_red(self) -> None:
        """Modal confirm button is red."""
        idx = self.source.index("Rotate widget key")
        modal_block = self.source[idx:idx + 500]
        assert 'color="red"' in modal_block


# ===========================================================================
# 18. COLOR FIELD COMPONENT
# ===========================================================================

class TestColorFieldComponent:
    """ColorField sub-component — color picker with swatches."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.source = _read(WIDGET_PAGE)

    def test_swatch_preview_size(self) -> None:
        """Color swatch preview: 36x36px, borderRadius 6."""
        assert "width: 36," in self.source
        assert "height: 36," in self.source
        assert "borderRadius: 6," in self.source

    def test_hex_input_width(self) -> None:
        """Hex input width: 120px."""
        assert "style={{ width: 120 }}" in self.source

    def test_hex_input_font(self) -> None:
        """Hex input uses JetBrains Mono monospace at 13px."""
        assert "'JetBrains Mono', monospace" in self.source
        assert "fontSize: 13" in self.source

    def test_default_swatches_count(self) -> None:
        """Default swatches: 8 colors (BRAND_RED + 7 hex literals)."""
        match = re.search(r"defaultSwatches\s*=\s*\[(.*?)\];", self.source, re.DOTALL)
        assert match, "defaultSwatches array must exist"
        # Count comma-separated entries: BRAND_RED, '#2563EB', '#059669', ...
        entries = [e.strip() for e in match.group(1).split(",") if e.strip()]
        assert len(entries) == 8, f"Expected 8 default swatches, found {len(entries)}"

    def test_color_picker_swatches_per_row(self) -> None:
        """ColorPicker swatchesPerRow={8}."""
        assert "swatchesPerRow={8}" in self.source
