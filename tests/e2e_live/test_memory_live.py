"""
Live E2E Memory & Privacy page tests — real data from staging/production.

Validates that the Memory & Privacy admin page renders with real settings.
Note: This page may only be available on Professional+ tiers.

SPEC-1649: All tests use only live external interfaces.
WI-1023: Expand tests/e2e_live/ to cover all admin pages.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page


class TestMemoryPageStructure:
    """Verify the Memory & Privacy page renders with real data."""

    def test_mem_live_01_page_heading(self, live_memory_page: Page):
        """MEM-LIVE-01: Memory page shows heading."""
        main_text = live_memory_page.text_content("main") or ""
        assert "Memory" in main_text or "Privacy" in main_text, (
            "No Memory or Privacy heading found"
        )

    def test_mem_live_02_has_settings(self, live_memory_page: Page):
        """MEM-LIVE-02: Memory page displays settings or configuration."""
        live_memory_page.wait_for_timeout(1000)
        main_text = (live_memory_page.text_content("main") or "").lower()
        # Look for memory/privacy related terms
        has_settings = any(
            term in main_text
            for term in [
                "retention", "consent", "data", "privacy",
                "memory", "customer", "profile", "layer",
                "enable", "disable", "days",
            ]
        )
        assert has_settings, "No memory/privacy settings found on page"

    def test_mem_live_03_has_toggle_or_input(self, live_memory_page: Page):
        """MEM-LIVE-03: Page has at least one toggle switch or input."""
        live_memory_page.wait_for_timeout(500)
        toggles = live_memory_page.locator(
            "input[type='checkbox'], [role='switch'], input[type='number']"
        )
        assert toggles.count() >= 1, (
            "No toggle switches or numeric inputs found on Memory page"
        )
