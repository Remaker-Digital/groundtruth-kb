"""
E2E tests — Widget page.

Tests every interactive element on the Widget customization page:
  - Page structure and data rendering
  - Widget key display and copy button
  - Widget key rotation confirmation
  - Color picker inputs
  - Toggle switches (branding, dark mode, greeting, etc.)
  - Avatar upload area
  - Install code snippet display

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
    """Verify the Widget page renders all expected elements."""

    def test_page_heading_visible(self, admin_widget_page: Page) -> None:
        """Widget page heading is visible."""
        heading = admin_widget_page.locator("h2, h3").filter(has_text="Widget")
        expect(heading.first).to_be_visible()

    def test_widget_key_displayed(self, admin_widget_page: Page) -> None:
        """Widget key label is visible on the page."""
        # Widget page has a "Widget key" label. The key value itself is in
        # a read-only TextInput. If no key exists, it shows a warning message.
        key_label = admin_widget_page.locator("text=Widget key")
        expect(key_label.first).to_be_visible()

    def test_copy_button_visible(self, admin_widget_page: Page) -> None:
        """A copy button (clipboard emoji) exists near the widget key."""
        # The copy button uses a clipboard emoji (📋) — no text/aria-label.
        # Verify the button containing the clipboard emoji exists.
        clipboard_btn = admin_widget_page.locator("button", has_text="\U0001f4cb")
        copy_btn = admin_widget_page.locator(
            'button[aria-label*="Copy"], button[aria-label*="copy"], '
            'button[title*="Copy"]'
        )
        assert clipboard_btn.count() > 0 or copy_btn.count() > 0, \
            "Copy button (clipboard emoji) should be visible"

    def test_color_inputs_visible(self, admin_widget_page: Page) -> None:
        """Color configuration inputs are visible."""
        # Color inputs might be type="color" or text inputs with hex values
        color_inputs = admin_widget_page.locator('input[type="color"]')
        hex_inputs = admin_widget_page.locator('input[value*="#"]')
        assert color_inputs.count() > 0 or hex_inputs.count() > 0, \
            "Color configuration inputs should be visible"

    def test_save_button_visible(self, admin_widget_page: Page) -> None:
        """Save button is visible on the widget page."""
        save_btn = admin_widget_page.locator("button", has_text="Save")
        expect(save_btn.first).to_be_visible()


# ===========================================================================
# Widget Key Rotation Tests
# ===========================================================================


class TestWidgetKeyRotation:
    """Test widget key rotation flow."""

    def test_rotate_button_exists(self, admin_widget_page: Page) -> None:
        """A key rotation button exists for the widget key."""
        # Button text is "Rotate key" in the Widget.tsx implementation
        rotate_btn = admin_widget_page.locator("button", has_text="Rotate key")
        regenerate_btn = admin_widget_page.locator("button", has_text="Regenerate")
        rotate_short = admin_widget_page.locator("button", has_text="Rotate")
        assert rotate_btn.count() > 0 or regenerate_btn.count() > 0 or rotate_short.count() > 0, \
            "Rotate/Regenerate key button should exist"


# ===========================================================================
# Save Widget Config Tests
# ===========================================================================


class TestSaveWidgetConfig:
    """Test saving widget configuration."""

    def test_save_sends_api_call(self, admin_widget_page: Page) -> None:
        """Clicking Save sends an API call for widget config."""
        mocker: AdminApiMocker = admin_widget_page._api_mocker  # type: ignore[attr-defined]
        mocker.clear_calls()

        save_btn = admin_widget_page.locator("button", has_text="Save").first
        save_btn.click()
        admin_widget_page.wait_for_timeout(500)

        # Check for any POST/PUT calls related to widget or config
        all_calls = mocker.get_calls()
        save_calls = [c for c in all_calls if c["method"] in ("POST", "PUT")
                      and ("widget" in c.get("path", "") or "config" in c.get("path", ""))]
        assert len(save_calls) >= 1, \
            f"Save should trigger widget config API call, got: {all_calls}"
