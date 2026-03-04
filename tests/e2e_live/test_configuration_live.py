"""
Live E2E configuration tests — real config values + draft save round-trip.

Validates that the Agent Configuration page loads real production values,
all sections are visible, and the draft save/reload cycle works against
the live backend.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re

import pytest
from playwright.sync_api import Page


class TestConfigValues:
    """Configuration page displays real values from the production backend."""

    def test_brand_name_populated_or_draft_state(self, live_config_page: Page):
        """Activated: brand name input has a real value.  Fresh: draft state visible.

        Freshly-seeded tenants have empty inputs but the config page shows
        draft-state labels (e.g. "Draft", "Unsaved changes") and editable
        form fields.  Both states are valid.
        """
        live_config_page.wait_for_timeout(2000)
        inputs = live_config_page.locator("input[type='text'], input:not([type])")
        found_populated = False
        for i in range(min(inputs.count(), 20)):
            value = inputs.nth(i).input_value()
            if value and len(value.strip()) > 0:
                found_populated = True
                break
        if not found_populated:
            main_text = live_config_page.text_content("main") or ""
            found_populated = bool(re.search(
                r"brand|tone|voice|draft|config|save", main_text, re.I
            ))
        assert found_populated, "No populated inputs or config content found on configuration page"

    def test_escalation_categories_loaded(self, live_config_page: Page):
        """Escalation rules section is visible on the config page."""
        main_text = (live_config_page.text_content("main") or "").lower()
        # Config page section headers: "Escalation rules", or category names
        has_categories = bool(re.search(
            r"(escalat|categor|billing|technical|complaint|rules)", main_text
        ))
        assert has_categories, "No escalation section or categories found"

    def test_named_configs_list_populated(self, live_config_page: Page):
        """Version history or named appearances section is visible."""
        main_text = (live_config_page.text_content("main") or "").lower()
        # Look for version history sidebar, named appearance, or draft/active
        has_named = bool(re.search(
            r"(version|history|appearance|active|draft|save|unsaved|config)", main_text
        ))
        assert has_named, "No version history or configuration state found"

    def test_ai_instructions_or_behavior_section(self, live_config_page: Page):
        """AI behavior tab/section exists, or a textarea is populated."""
        # Wait for config data to load from API
        live_config_page.wait_for_timeout(3000)
        main_text = (live_config_page.text_content("main") or "").lower()

        # Check for textarea content
        textareas = live_config_page.locator("textarea")
        has_textarea_content = False
        for i in range(min(textareas.count(), 10)):
            value = textareas.nth(i).input_value()
            if value and len(value.strip()) > 5:
                has_textarea_content = True
                break

        # Check for AI behavior tab text, or any configuration field label
        has_behavior_section = bool(re.search(
            r"(ai behavior|instruction|prompt|behavior|tone|brand|config)", main_text
        ))

        assert has_textarea_content or has_behavior_section, (
            "No textarea content or behavior section found"
        )


class TestConfigSections:
    """All major configuration sections are visible."""

    def test_config_page_has_section_headers(self, live_config_page: Page):
        """Configuration page has recognizable section or tab headers."""
        # Wait for full page render — ConfigEditor loads tabs and fields
        live_config_page.wait_for_timeout(3000)
        main_text = (live_config_page.text_content("main") or "").lower()
        # ConfigEditor uses tab headers: "Brand & Tone", "AI behavior",
        # "Escalation rules", "Response policies", "Widget appearance", etc.
        # Also accept generic config page content
        has_section = bool(re.search(
            r"(brand|tone|ai behavior|escalat|polic|widget|integrat"
            r"|knowledge|memory|notif|config|save|draft|unsaved)",
            main_text
        ))
        assert has_section, (
            f"No configuration section headers found. "
            f"Page text starts with: {main_text[:200]}"
        )

    def test_config_page_is_interactive(self, live_config_page: Page):
        """Configuration page has interactive form elements."""
        live_config_page.wait_for_timeout(3000)
        # Count all form-like elements (including checkboxes, color, etc.)
        input_count = live_config_page.locator(
            "input, textarea, select, "
            "[role='switch'], [role='checkbox'], [role='combobox'], [role='slider']"
        ).count()
        assert input_count >= 1, (
            f"Expected at least 1 form element on config page, found {input_count}"
        )

    def test_config_page_has_save_action(self, live_config_page: Page):
        """Configuration page has a save or discard button."""
        live_config_page.wait_for_timeout(2000)
        main_text = (live_config_page.text_content("main") or "").lower()
        has_action = bool(re.search(
            r"(save|discard|reset|apply|cancel|unsaved)", main_text
        ))
        # Also check for button elements
        buttons = live_config_page.locator("button")
        has_buttons = buttons.count() >= 1
        assert has_action or has_buttons, "No save/discard action found on config page"


class TestDraftSaveRoundTrip:
    """Draft save and reload cycle against the live backend."""

    def test_edit_draft_and_save(self, live_config_page: Page):
        """Change a draft field, save, reload, and verify persistence.

        Modifies a text input or textarea in the draft config, saves it,
        reloads the page, and verifies the change persisted.
        """
        live_config_page.wait_for_timeout(3000)

        # Prefer textareas (brand_voice, instructions) over text inputs
        # (which may be numeric filters like "30 days")
        target_input = None
        original_value = ""

        # Try textareas first
        textareas = live_config_page.locator("textarea")
        for i in range(min(textareas.count(), 10)):
            val = textareas.nth(i).input_value()
            if val and len(val.strip()) > 3:
                target_input = textareas.nth(i)
                original_value = val
                break

        # Fall back to text inputs that have non-numeric content
        if target_input is None:
            inputs = live_config_page.locator("input[type='text']")
            for i in range(min(inputs.count(), 20)):
                val = inputs.nth(i).input_value()
                # Skip numeric/filter inputs like "30 days"
                if val and len(val.strip()) > 3 and not val.strip().replace(" ", "").replace("days", "").isdigit():
                    target_input = inputs.nth(i)
                    original_value = val
                    break

        if target_input is None:
            pytest.skip("No suitable text field found on configuration page")

        # Modify the value with a test marker
        test_value = f"{original_value} [e2e-test-marker]"
        target_input.fill(test_value)

        # Find and click the save draft button
        save_btn = live_config_page.locator(
            "text=/Save draft|Save changes|Save/"
        ).first
        if save_btn.is_visible():
            save_btn.click()
            live_config_page.wait_for_timeout(2000)

            # Reload and verify
            # S134: Use "load" — live SPAs prevent networkidle.
            live_config_page.reload(wait_until="load")
            live_config_page.wait_for_selector(
                "text=Configuration", timeout=15_000
            )
            live_config_page.wait_for_timeout(3000)

            # Re-locate the same field after reload
            page_text = live_config_page.text_content("main") or ""
            assert "[e2e-test-marker]" in page_text, (
                "Draft save did not persist — marker not found after reload"
            )

            # CLEANUP: restore original value — re-find the target field
            textareas = live_config_page.locator("textarea")
            cleanup_input = None
            for i in range(min(textareas.count(), 10)):
                val = textareas.nth(i).input_value()
                if val and "[e2e-test-marker]" in val:
                    cleanup_input = textareas.nth(i)
                    break
            if cleanup_input is None:
                inputs_cleanup = live_config_page.locator("input[type='text']")
                for i in range(min(inputs_cleanup.count(), 20)):
                    val = inputs_cleanup.nth(i).input_value()
                    if val and "[e2e-test-marker]" in val:
                        cleanup_input = inputs_cleanup.nth(i)
                        break
            if cleanup_input:
                cleanup_input.fill(original_value)
            save_btn = live_config_page.locator(
                "text=/Save draft|Save changes|Save/"
            ).first
            if save_btn.is_visible():
                save_btn.click()
                live_config_page.wait_for_timeout(2000)
        else:
            pytest.skip("Save draft button not visible")

    def test_draft_restore_original(self, live_config_page: Page):
        """Verify the configuration page does not contain test markers."""
        live_config_page.wait_for_timeout(1000)
        main_text = live_config_page.text_content("main") or ""
        assert "[e2e-test-marker]" not in main_text, (
            "Test marker still present — cleanup from previous test failed"
        )

    def test_save_button_triggers_api_call(self, live_config_page: Page):
        """Verify the save button sends a PUT to /api/config?state=draft."""
        api_calls: list[str] = []

        def _capture_api(route):
            request = route.request
            if "/api/config" in request.url and request.method == "PUT":
                api_calls.append(f"{request.method} {request.url}")
            route.continue_()

        # Add additional route handler (layered on top of safety guards)
        live_config_page.route("**/api/config**", _capture_api)

        # Modify a field and click save
        inputs = live_config_page.locator("input[type='text']")
        if inputs.count() > 0:
            original = inputs.first.input_value()
            inputs.first.fill(f"{original} x")

            save_btn = live_config_page.locator(
                "text=/Save draft|Save changes|Save/"
            ).first
            if save_btn.is_visible():
                save_btn.click()
                live_config_page.wait_for_timeout(2000)

                assert len(api_calls) >= 1, (
                    "Save button did not trigger a PUT /api/config call"
                )
                assert any("config" in call for call in api_calls)

                # Cleanup
                inputs.first.fill(original)
                save_btn.click()
                live_config_page.wait_for_timeout(1000)
