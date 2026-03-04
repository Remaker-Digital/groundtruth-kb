"""
Live E2E Integrations page tests — real data from staging/production.

Validates that the Integrations admin page renders correctly with
integration status from the live backend.

SPEC-1649: All tests use only live external interfaces.
WI-1023: Expand tests/e2e_live/ to cover all admin pages.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page


class TestIntegrationsPageStructure:
    """Verify the Integrations page renders with real data."""

    def test_int_live_01_page_loads(self, live_integrations_page: Page):
        """INT-LIVE-01: Integrations page loads without error."""
        live_integrations_page.wait_for_timeout(1000)
        main_text = live_integrations_page.text_content("main") or ""
        # Should have meaningful content (not just an error page)
        assert len(main_text) > 20, "Integrations page has no content"

    def test_int_live_02_has_integration_items(self, live_integrations_page: Page):
        """INT-LIVE-02: Page shows integration entries or configuration options."""
        live_integrations_page.wait_for_timeout(1000)
        main_text = (live_integrations_page.text_content("main") or "").lower()
        # Look for common integration-related terms
        has_integrations = any(
            term in main_text
            for term in [
                "shopify", "stripe", "webhook", "api",
                "connect", "integration", "configure",
                "mcp", "email", "smtp",
            ]
        )
        assert has_integrations, (
            "No integration-related content found on Integrations page"
        )

    def test_int_live_03_no_error_state(self, live_integrations_page: Page):
        """INT-LIVE-03: No error messages displayed on Integrations page."""
        live_integrations_page.wait_for_timeout(500)
        main_text = (live_integrations_page.text_content("main") or "").lower()
        error_markers = ["something went wrong", "failed to load", "error occurred"]
        for marker in error_markers:
            assert marker not in main_text, (
                f"Error message found on Integrations page: '{marker}'"
            )
