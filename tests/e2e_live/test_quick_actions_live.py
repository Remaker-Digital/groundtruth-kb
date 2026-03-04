"""
Live E2E Quick Actions page tests — real data from staging/production.

Validates that the Quick Actions admin page renders with real action
entries from the live backend.

SPEC-1649: All tests use only live external interfaces.
WI-1023: Expand tests/e2e_live/ to cover all admin pages.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page


class TestQuickActionsPageStructure:
    """Verify the Quick Actions page renders with real data."""

    def test_qa_live_01_page_heading(self, live_quick_actions_page: Page):
        """QA-LIVE-01: Quick actions page shows heading."""
        heading = live_quick_actions_page.get_by_text("Quick actions", exact=False).first
        assert heading.is_visible(), "Quick actions heading not visible"

    def test_qa_live_02_action_list_or_empty(self, live_quick_actions_page: Page):
        """QA-LIVE-02: Action list or empty state renders."""
        live_quick_actions_page.wait_for_timeout(1000)
        main_text = live_quick_actions_page.text_content("main") or ""
        # Either actions are listed or there's an empty state / add button
        has_content = len(main_text) > 50
        assert has_content, "Quick actions page has no visible content"

    def test_qa_live_03_add_action_button(self, live_quick_actions_page: Page):
        """QA-LIVE-03: Add action button is present."""
        live_quick_actions_page.wait_for_timeout(500)
        # Try multiple possible button texts
        for text in ["Add", "New", "Create"]:
            btn = live_quick_actions_page.get_by_role("button", name=text).first
            if btn.is_visible():
                return  # Found it
        # Also check for icon-only add buttons
        add_btns = live_quick_actions_page.locator("button:has-text('Add'), button:has-text('New')")
        assert add_btns.count() > 0, "No Add/New button found on Quick Actions page"
