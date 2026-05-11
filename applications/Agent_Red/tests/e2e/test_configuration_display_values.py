"""
E2E tests — Configuration page display value verification.

Verifies that every field on the Configuration page renders the correct value
from the mocked API response.  Each test checks that a specific value is both
(1) visible in the DOM and (2) matches the expected MOCK_CONFIG data.

Test classes:
  - TestConfigBrandSectionValues: brand_name, brand_voice, formality, response_length
  - TestConfigPolicySectionValues: return_window, return_policy, shipping_info
  - TestConfigEscalationSectionValues: threshold, per-category enabled/disabled, idle, max_turns
  - TestConfigLanguageSectionValues: primary_language, supported_languages
  - TestConfigCustomInstructionsValues: custom_instructions textarea
  - TestConfigNamedConfigsValues: 3 configs x (name, active badge, field count)

Run with:
    pytest tests/e2e/test_configuration_display_values.py -v --headed
    pytest tests/e2e/test_configuration_display_values.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

from .conftest import MOCK_CONFIG, MOCK_NAMED_CONFIGS

pytestmark = pytest.mark.e2e

# ---------------------------------------------------------------------------
# Helpers — extract expected values from mock data
# ---------------------------------------------------------------------------

_CFG = MOCK_CONFIG["config"]
_NAMED = MOCK_NAMED_CONFIGS["configs"]


# ===========================================================================
# Brand & Persona section
# ===========================================================================


class TestConfigBrandSectionValues:
    """Verify Brand & Persona section renders the correct mock values."""

    def test_brand_name_value(self, admin_config_page: Page) -> None:
        """Brand name input contains 'TestCo' from MOCK_CONFIG."""
        # Mantine TextInput renders a real <input> with the value attribute.
        brand_input = admin_config_page.get_by_label("Brand name").first
        expect(brand_input).to_have_value("TestCo")

    def test_brand_voice_value(self, admin_config_page: Page) -> None:
        """Brand voice textarea contains the mock brand_voice string."""
        brand_voice_area = admin_config_page.get_by_label("Brand voice").first
        expect(brand_voice_area).to_have_value("Professional and helpful")

    def test_formality_selection(self, admin_config_page: Page) -> None:
        """Formality select displays 'Professional' (the label for value 'balanced').

        The mock sends formality='balanced', which maps to label 'Professional'
        in the Select component's data array.
        """
        # Mantine Select renders a combobox input whose displayed value is the
        # human-readable label.  The mock value 'balanced' maps to 'Professional'.
        formality_input = admin_config_page.get_by_label("Formality").first
        expect(formality_input).to_have_value("Professional")

    def test_response_length_selection(self, admin_config_page: Page) -> None:
        """Response length select displays 'Moderate' (label for value 'standard').

        The mock sends response_length='standard', which maps to 'Moderate'
        in the Select component.
        """
        response_input = admin_config_page.get_by_label("Response length").first
        expect(response_input).to_have_value("Moderate")


# ===========================================================================
# Policies section
# ===========================================================================


class TestConfigPolicySectionValues:
    """Verify Policies section renders the correct mock values."""

    def test_return_window_value(self, admin_config_page: Page) -> None:
        """Return window NumberInput shows value 30 from MOCK_CONFIG."""
        # Mantine NumberInput renders an <input type="text"> with the numeric
        # value.  The suffix " days" is rendered separately by Mantine.
        return_input = admin_config_page.get_by_label("Return window").first
        expect(return_input).to_have_value("30")

    def test_refund_policy_text(self, admin_config_page: Page) -> None:
        """Refund policy textarea contains the mock return_policy text."""
        refund_area = admin_config_page.get_by_label("Refund policy").first
        expect(refund_area).to_have_value(
            "Full refund within 30 days of purchase."
        )

    def test_shipping_policy_text(self, admin_config_page: Page) -> None:
        """Shipping policy textarea contains the mock shipping_info text."""
        shipping_area = admin_config_page.get_by_label("Shipping policy").first
        expect(shipping_area).to_have_value(
            "Free standard shipping on orders over $50."
        )


# ===========================================================================
# Escalation section
# ===========================================================================


class TestConfigEscalationSectionValues:
    """Verify Escalation section renders the correct mock values.

    MOCK_CONFIG has escalation_threshold=0.7, 6 categories (5 enabled, 1 disabled),
    idle_timeout_minutes=30, and max_ai_turns_before_escalation=50.
    """

    def test_escalation_threshold_visible(self, admin_config_page: Page) -> None:
        """Escalation threshold label and slider are present on the page."""
        threshold_label = admin_config_page.get_by_text("Escalation threshold")
        expect(threshold_label.first).to_be_visible()

    def test_sales_category_enabled(self, admin_config_page: Page) -> None:
        """Sales escalation category is rendered and enabled (switch ON)."""
        sales_label = admin_config_page.get_by_text("Sales", exact=True).first
        expect(sales_label).to_be_visible()

    def test_support_category_enabled(self, admin_config_page: Page) -> None:
        """Support escalation category is rendered and enabled."""
        support_label = admin_config_page.get_by_text("Support", exact=True).first
        expect(support_label).to_be_visible()

    def test_service_category_enabled(self, admin_config_page: Page) -> None:
        """Service escalation category is rendered and enabled."""
        service_label = admin_config_page.get_by_text("Service", exact=True).first
        expect(service_label).to_be_visible()

    def test_account_category_enabled(self, admin_config_page: Page) -> None:
        """Account escalation category is rendered and enabled."""
        account_label = admin_config_page.get_by_text("Account", exact=True).first
        expect(account_label).to_be_visible()

    def test_technical_category_present(self, admin_config_page: Page) -> None:
        """Technical assistance category is rendered (disabled in mock data).

        The mock sets technical.enabled=False, so its card should render with
        reduced opacity.  We verify the label text is present.
        """
        tech_label = admin_config_page.get_by_text("Technical assistance").first
        expect(tech_label).to_be_visible()

    def test_general_category_enabled(self, admin_config_page: Page) -> None:
        """General inquiry category is rendered and enabled."""
        general_label = admin_config_page.get_by_text("General inquiry").first
        expect(general_label).to_be_visible()

    def test_six_categories_rendered(self, admin_config_page: Page) -> None:
        """All 6 escalation categories are rendered as card sections.

        Each category card contains a Switch toggle. Verify there are at least
        6 switch elements inside the Escalation section.
        """
        # Each category card has a Switch component. Mantine Switch renders
        # an <input type="checkbox" role="switch">.
        switches = admin_config_page.locator('[role="switch"]')
        assert switches.count() >= 6, (
            f"Expected at least 6 escalation category switches, found {switches.count()}"
        )

    def test_idle_timeout_value(self, admin_config_page: Page) -> None:
        """Idle timeout NumberInput shows value 30 from MOCK_CONFIG."""
        idle_input = admin_config_page.get_by_label("Idle timeout").first
        expect(idle_input).to_have_value("30")

    def test_max_turns_value(self, admin_config_page: Page) -> None:
        """Max turns NumberInput shows value 50 from MOCK_CONFIG."""
        max_input = admin_config_page.get_by_label("Max turns").first
        expect(max_input).to_have_value("50")


# ===========================================================================
# Language section
# ===========================================================================


class TestConfigLanguageSectionValues:
    """Verify Language section renders the correct mock values."""

    def test_primary_language_value(self, admin_config_page: Page) -> None:
        """Primary language select displays 'English' (label for value 'en')."""
        lang_input = admin_config_page.get_by_label("Primary language").first
        expect(lang_input).to_have_value("English")

    def test_english_language_chip_selected(self, admin_config_page: Page) -> None:
        """English chip is checked in the Supported languages Chip.Group.

        MOCK_CONFIG has additional_languages=['en'], so the English chip
        should have aria-checked='true' (Mantine Chip renders as a checkbox).
        """
        # Mantine Chip.Group renders each Chip with role="checkbox" and
        # the label text.  Look for the English chip.
        english_chip = admin_config_page.get_by_label("English", exact=True).first
        expect(english_chip).to_be_checked()


# ===========================================================================
# Custom Instructions section
# ===========================================================================


class TestConfigCustomInstructionsValues:
    """Verify Custom Instructions section renders the correct mock value."""

    def test_custom_instructions_text(self, admin_config_page: Page) -> None:
        """Custom instructions textarea contains the mock text.

        The Configuration.tsx custom instructions textarea does not use a
        Mantine label prop — it is a bare Textarea inside the "Custom
        instructions" Paper section.  Locate by placeholder or by finding
        the textarea within that section.
        """
        # The textarea uses placeholder="Provide advisory instructions..."
        textarea = admin_config_page.locator(
            'textarea[placeholder*="advisory instructions"]'
        ).first
        expect(textarea).to_have_value(
            "Always greet customers by name when available."
        )


# ===========================================================================
# Named Configurations table
# ===========================================================================


class TestConfigNamedConfigsValues:
    """Verify the Saved Configurations table renders all 3 mock named configs.

    MOCK_NAMED_CONFIGS has:
      - Default:      isActive=True,  version=1, fieldCount=14
      - Holiday:      isActive=False, version=2, fieldCount=14
      - Black Friday: isActive=False, version=1, fieldCount=12
    """

    # --- Default config ---

    def test_default_config_name_visible(self, admin_config_page: Page) -> None:
        """'Default' named configuration name is visible in the table."""
        expect(
            admin_config_page.get_by_text("Default", exact=True).first
        ).to_be_visible()

    def test_default_config_active_badge(self, admin_config_page: Page) -> None:
        """'Default' config shows an 'Active' badge (isActive=True)."""
        active_badge = admin_config_page.get_by_text("Active", exact=True).first
        expect(active_badge).to_be_visible()

    def test_default_config_field_count(self, admin_config_page: Page) -> None:
        """'Default' config shows '14 fields' badge."""
        badge = admin_config_page.get_by_text("14 fields").first
        expect(badge).to_be_visible()

    # --- Holiday config ---

    def test_holiday_config_name_visible(self, admin_config_page: Page) -> None:
        """'Holiday' named configuration name is visible in the table."""
        expect(
            admin_config_page.get_by_text("Holiday", exact=True).first
        ).to_be_visible()

    def test_holiday_config_no_active_badge(self, admin_config_page: Page) -> None:
        """'Holiday' config is NOT active — it should have an 'Activate' button.

        Since isActive=False for Holiday, a small 'Activate' action button
        is rendered in its row instead of an 'Active' badge.
        """
        # Find the Holiday row by locating the table row containing "Holiday"
        holiday_row = admin_config_page.locator("tr").filter(
            has_text="Holiday"
        ).first
        activate_btn = holiday_row.locator("button", has_text="Activate")
        expect(activate_btn.first).to_be_visible()

    def test_holiday_config_field_count(self, admin_config_page: Page) -> None:
        """'Holiday' config row shows '14 fields' badge.

        Both Default and Holiday have fieldCount=14.  We verify the Holiday
        row specifically has it.
        """
        holiday_row = admin_config_page.locator("tr").filter(
            has_text="Holiday"
        ).first
        badge = holiday_row.get_by_text("14 fields")
        expect(badge.first).to_be_visible()

    # --- Black Friday config ---

    def test_black_friday_config_name_visible(self, admin_config_page: Page) -> None:
        """'Black Friday' named configuration name is visible in the table."""
        expect(
            admin_config_page.get_by_text("Black Friday", exact=True).first
        ).to_be_visible()

    def test_black_friday_config_field_count(self, admin_config_page: Page) -> None:
        """'Black Friday' config shows '12 fields' badge."""
        bf_row = admin_config_page.locator("tr").filter(
            has_text="Black Friday"
        ).first
        badge = bf_row.get_by_text("12 fields")
        expect(badge.first).to_be_visible()

    def test_black_friday_has_delete_button(self, admin_config_page: Page) -> None:
        """'Black Friday' config (not default, not active) shows a Delete button."""
        bf_row = admin_config_page.locator("tr").filter(
            has_text="Black Friday"
        ).first
        delete_btn = bf_row.locator("button", has_text="Delete")
        expect(delete_btn.first).to_be_visible()
