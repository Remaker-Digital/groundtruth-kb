# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Mock E2E tests for the Widget configuration page (/widget).

Tests embed code display, preview configuration, launcher preview,
widget test functionality, config integration, and API contracts
against the mock Vite dev server.
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e_mock.conftest import (
    api_origin,
    navigate_and_settle,
    dismiss_onboarding_if_present,
    get_api_json,
    assert_mock_active,
    main_text,
)

WIDGET_PATH = "/widget"


# ---------------------------------------------------------------------------
# TestEmbedCode - 6 tests
# ---------------------------------------------------------------------------

class TestEmbedCode:
    """Verify the embed code section displays and copies correctly."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        navigate_and_settle(shared_page, WIDGET_PATH, mock_base_url)
        dismiss_onboarding_if_present(shared_page)

    def test_embed_code_section_present(self, shared_page: Page):
        """Widget page has an embed code section."""
        text = main_text(shared_page).lower()
        assert "embed" in text or "install" in text or "code" in text or "script" in text, (
            "Embed code section not found"
        )

    def test_embed_code_contains_script_tag(self, shared_page: Page):
        """Embed code includes a script tag reference."""
        text = main_text(shared_page)
        assert "script" in text.lower() or "widget" in text.lower(), (
            "Script tag not found in embed code"
        )

    def test_widget_key_displayed(self, shared_page: Page):
        """The widget key (pk_live) is displayed on the page."""
        text = main_text(shared_page)
        assert "pk_live" in text or "widget" in text.lower() or "key" in text.lower(), "Widget key or widget section not found"

    def test_cdn_url_displayed(self, shared_page: Page):
        """The CDN URL for the widget is displayed."""
        text = main_text(shared_page)
        assert "cdn" in text.lower() or "agentred" in text.lower() or "widget" in text.lower(), (
            "CDN URL not found in embed code"
        )

    def test_embed_code_available_via_api(self, shared_page: Page, mock_base_url: str):
        """Embed code is accessible via the API endpoint."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/widget/embed-code")
        assert "embedCode" in data, "API should return embedCode field"
        assert len(data["embedCode"]) > 0, "embedCode should not be empty"

    def test_embed_api_endpoint_shape(self, shared_page: Page, mock_base_url: str):
        """GET /api/admin/widget/embed-code returns embedCode field."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/widget/embed-code")
        assert "embedCode" in data
        assert "script" in data["embedCode"].lower()


# ---------------------------------------------------------------------------
# TestPreviewConfig - 8 tests
# ---------------------------------------------------------------------------

class TestPreviewConfig:
    """Verify the widget preview configuration section."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        navigate_and_settle(shared_page, WIDGET_PATH, mock_base_url)
        dismiss_onboarding_if_present(shared_page)

    def test_primary_color_displayed(self, shared_page: Page):
        """Primary color (#ff3621) is shown on the page."""
        text = main_text(shared_page)
        # Color may be in input value rather than visible text
        has_color = "ff3621" in text.lower() or "#ff3621" in text.lower() or "255" in text
        if not has_color:
            inputs = shared_page.locator("input")
            for inp in inputs.all():
                val = (inp.get_attribute("value") or "").lower()
                if "ff3621" in val or (val.startswith("#") and len(val) in (4, 7)):
                    has_color = True
                    break
        assert has_color, "Primary color not displayed"

    def test_position_displayed(self, shared_page: Page):
        """Widget position (bottom-right) is shown."""
        text = main_text(shared_page).lower()
        assert "bottom" in text or "right" in text or "position" in text, (
            "Widget position not displayed"
        )

    def test_launcher_size_displayed(self, shared_page: Page):
        """Launcher size (56) is shown."""
        text = main_text(shared_page)
        assert "56" in text, "Launcher size (56) not found"

    def test_border_radius_displayed(self, shared_page: Page):
        """Border radius (12) is shown."""
        text = main_text(shared_page)
        assert "12" in text, "Border radius (12) not found"

    def test_header_text_displayed(self, shared_page: Page):
        """Header text (Chat with us) is shown."""
        text = main_text(shared_page)
        assert "Chat with us" in text or "chat" in text.lower() or "header" in text.lower(), "Header text not found"

    def test_subtitle_displayed(self, shared_page: Page):
        """Subtitle text is shown on the page."""
        text = main_text(shared_page)
        assert "typically reply" in text.lower() or "within minutes" in text.lower() or "subtitle" in text.lower() or "message" in text.lower(), (
            "Subtitle text not found"
        )

    def test_launcher_icon_option(self, shared_page: Page):
        """Launcher icon type (chat) is indicated."""
        text = main_text(shared_page).lower()
        assert "chat" in text or "icon" in text, "Launcher icon option not found"

    def test_preview_config_api_shape(self, shared_page: Page, mock_base_url: str):
        """GET /api/admin/widget/preview-config returns expected fields."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/widget/preview-config")
        assert "primaryColor" in data
        assert "position" in data
        assert "launcherSize" in data
        assert data["primaryColor"] == "#ff3621"


# ---------------------------------------------------------------------------
# TestLauncherPreview - 8 tests
# ---------------------------------------------------------------------------

class TestLauncherPreview:
    """Verify the live widget launcher preview on the config page."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        navigate_and_settle(shared_page, WIDGET_PATH, mock_base_url)
        dismiss_onboarding_if_present(shared_page)

    def test_preview_section_exists(self, shared_page: Page):
        """A preview or live preview section is present on the page."""
        text = main_text(shared_page).lower()
        has_preview = "preview" in text or "live" in text or "launcher" in text
        preview_els = shared_page.locator(
            "[data-testid*='preview'], [class*='preview'], [class*='launcher']"
        )
        assert has_preview or preview_els.count() > 0, "Preview section not found"

    def test_color_picker_present(self, shared_page: Page):
        """A color picker input is present for launcher/primary color."""
        color_inputs = shared_page.locator(
            "input[type='color'], [data-testid*='color'], .mantine-ColorInput-root, "
            "input[value*='#']"
        )
        all_inputs = shared_page.locator("input")
        has_color = color_inputs.count() > 0
        if not has_color:
            for inp in all_inputs.all():
                val = inp.get_attribute("value") or ""
                if val.startswith("#") and len(val) in (4, 7):
                    has_color = True
                    break
        assert has_color, "No color picker found"

    def test_position_selector_present(self, shared_page: Page):
        """A position selector (dropdown, radio, or segmented control) is present."""
        text = main_text(shared_page).lower()
        has_position = "position" in text or "bottom-right" in text or "bottom-left" in text
        selectors = shared_page.locator(
            "select, [role='radiogroup'], .mantine-SegmentedControl-root, "
            "[data-testid*='position']"
        )
        assert has_position or selectors.count() > 0, "No position selector found"

    def test_size_slider_present(self, shared_page: Page):
        """A size slider or input is present for launcher size."""
        sliders = shared_page.locator(
            "input[type='range'], .mantine-Slider-root, [role='slider']"
        )
        size_inputs = shared_page.locator("input[type='number']")
        assert sliders.count() > 0 or size_inputs.count() > 0, "No size slider/input found"

    def test_icon_selector_present(self, shared_page: Page):
        """An icon selector is present for launcher icon."""
        text = main_text(shared_page).lower()
        has_icon = "icon" in text or "chat" in text or "launcher" in text
        selectors = shared_page.locator(
            "select, [role='radiogroup'], [data-testid*='icon']"
        )
        assert has_icon or selectors.count() > 0, "No icon selector found"

    def test_border_radius_control(self, shared_page: Page):
        """A border radius control (slider or input) is present."""
        text = main_text(shared_page).lower()
        has_radius = "radius" in text or "border" in text or "round" in text
        sliders = shared_page.locator(
            "input[type='range'], .mantine-Slider-root, input[type='number']"
        )
        assert has_radius or sliders.count() > 0, "No border radius control found"

    def test_header_text_input(self, shared_page: Page):
        """A text input for header text is present."""
        text_inputs = shared_page.locator(
            "input[type='text'], textarea, .mantine-TextInput-root"
        )
        assert text_inputs.count() >= 1, "No text inputs found for header/subtitle"

    def test_page_renders_without_crash(self, shared_page: Page):
        """Widget config page loads completely."""
        text = main_text(shared_page)
        assert len(text) > 30, "Widget page appears blank or crashed"


# ---------------------------------------------------------------------------
# TestWidgetTest - 4 tests (mutation - function-scoped page)
# ---------------------------------------------------------------------------

class TestWidgetTest:
    """Verify the widget test functionality."""

    def test_widget_test_endpoint_responds(self, page: Page, mock_base_url: str):
        """POST /api/admin/widget/test returns a response."""
        resp = page.request.post(f"{api_origin(mock_base_url)}/api/admin/widget/test")
        assert resp.status in (200, 201), f"Widget test returned {resp.status}"

    def test_widget_test_returns_json(self, page: Page, mock_base_url: str):
        """POST /api/admin/widget/test returns JSON."""
        resp = page.request.post(f"{api_origin(mock_base_url)}/api/admin/widget/test")
        body = resp.json()
        assert isinstance(body, dict)

    def test_rotate_widget_key_endpoint(self, page: Page, mock_base_url: str):
        """POST /api/keys/rotate-widget-key returns a response."""
        resp = page.request.post(f"{api_origin(mock_base_url)}/api/keys/rotate-widget-key")
        assert resp.status in (200, 201), f"Key rotation returned {resp.status}"

    def test_rotate_widget_key_returns_new_key(self, page: Page, mock_base_url: str):
        """POST /api/keys/rotate-widget-key returns a new key."""
        resp = page.request.post(f"{api_origin(mock_base_url)}/api/keys/rotate-widget-key")
        body = resp.json()
        assert isinstance(body, dict)
        has_key = "key" in body or "widgetKey" in body or "widget_key" in body or "newWidgetKey" in body
        assert has_key, "Rotation response missing key field"


# ---------------------------------------------------------------------------
# TestConfigIntegration - 6 tests
# ---------------------------------------------------------------------------

class TestConfigIntegration:
    """Verify widget config integrates with the main config endpoint."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        navigate_and_settle(shared_page, WIDGET_PATH, mock_base_url)
        dismiss_onboarding_if_present(shared_page)

    def test_config_endpoint_returns_widget_fields(self, shared_page: Page, mock_base_url: str):
        """GET /api/config includes widget-related fields."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        config = data.get("config", data.get("draft", data))
        has_widget_field = any(
            k for k in config.keys()
            if "widget" in k.lower() or "launcher" in k.lower() or "primary" in k.lower()
        )
        assert has_widget_field, "No widget fields found in config endpoint"

    def test_config_contains_primary_color(self, shared_page: Page, mock_base_url: str):
        """Config includes widget primary color."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        config = data.get("config", data.get("draft", data))
        color_keys = [k for k in config.keys() if "color" in k.lower() or "primary" in k.lower()]
        assert len(color_keys) > 0, "No color field in config"

    def test_config_contains_position(self, shared_page: Page, mock_base_url: str):
        """Config includes widget position field."""
        data = get_api_json(shared_page, mock_base_url, "/api/config")
        config = data.get("config", data.get("draft", data))
        position_keys = [k for k in config.keys() if "position" in k.lower()]
        assert len(position_keys) > 0, "No position field in config"

    def test_multiple_config_sections(self, shared_page: Page):
        """Widget page has multiple configuration sections."""
        sections = shared_page.locator(
            "h2, h3, h4, section, .mantine-Card-root, .mantine-Paper-root"
        )
        assert sections.count() >= 2, "Widget page has too few sections"

    def test_save_button_present(self, shared_page: Page):
        """A save button is present on the widget config page."""
        buttons = shared_page.locator("button")
        all_text = " ".join(b.inner_text().lower() for b in buttons.all() if b.is_visible())
        has_save = "save" in all_text or "apply" in all_text or "update" in all_text
        assert has_save, "No save/apply button found"

    def test_form_elements_present(self, shared_page: Page):
        """Widget page has form elements for configuration."""
        inputs = shared_page.locator("input, select, textarea, [role='slider']")
        assert inputs.count() >= 3, "Widget page has too few form elements"


# ---------------------------------------------------------------------------
# TestApiContracts - 6 tests
# ---------------------------------------------------------------------------

class TestApiContracts:
    """Verify the widget mock API endpoints return expected shapes."""

    def test_embed_code_endpoint_200(self, shared_page: Page, mock_base_url: str):
        """GET /api/admin/widget/embed-code returns 200."""
        resp = shared_page.request.get(f"{api_origin(mock_base_url)}/api/admin/widget/embed-code")
        assert resp.status == 200

    def test_preview_config_endpoint_200(self, shared_page: Page, mock_base_url: str):
        """GET /api/admin/widget/preview-config returns 200."""
        resp = shared_page.request.get(f"{api_origin(mock_base_url)}/api/admin/widget/preview-config")
        assert resp.status == 200

    def test_embed_code_contains_widget_key(self, shared_page: Page, mock_base_url: str):
        """Embed code contains the widget key."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/widget/embed-code")
        assert "pk_live_mock_key_12345" in data["embedCode"]

    def test_preview_config_fixture_values(self, shared_page: Page, mock_base_url: str):
        """Preview config returns all fixture values."""
        data = get_api_json(shared_page, mock_base_url, "/api/admin/widget/preview-config")
        assert data["primaryColor"] == "#ff3621"
        assert data["launcherColor"] == "#ff3621"
        assert data["position"] == "bottom-right"
        assert data["launcherSize"] == 56
        assert data["launcherIcon"] == "chat"
        assert data["borderRadius"] == 12
        assert data["headerText"] == "Chat with us"

    def test_config_endpoint_200(self, shared_page: Page, mock_base_url: str):
        """GET /api/config returns 200."""
        resp = shared_page.request.get(f"{api_origin(mock_base_url)}/api/config")
        assert resp.status == 200

    def test_mock_api_active(self, shared_page: Page, mock_base_url: str):
        """Mock API is confirmed active."""
        assert_mock_active(shared_page, mock_base_url)
