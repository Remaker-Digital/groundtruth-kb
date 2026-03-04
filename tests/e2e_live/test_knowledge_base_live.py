"""
Live E2E Knowledge Base page tests — real data from staging/production.

Validates that the Knowledge Base admin page renders correctly with real
KB entries fetched from the live backend. No mocked API responses.

SPEC-1649: All tests use only live external interfaces.
WI-1023: Expand tests/e2e_live/ to cover all admin pages.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page


class TestKnowledgeBasePageStructure:
    """Verify the Knowledge Base page renders with real data."""

    def test_kb_live_01_page_heading(self, live_kb_page: Page):
        """KB-LIVE-01: Knowledge base page shows 'Knowledge' heading."""
        heading = live_kb_page.get_by_text("Knowledge", exact=False).first
        assert heading.is_visible(), "Knowledge heading not visible"

    def test_kb_live_02_article_list_present(self, live_kb_page: Page):
        """KB-LIVE-02: Article list or empty state renders."""
        live_kb_page.wait_for_timeout(1000)
        main_text = live_kb_page.text_content("main") or ""
        # Either articles are listed or there's an empty state
        has_content = (
            "article" in main_text.lower()
            or "entry" in main_text.lower()
            or "Add" in main_text
            or "No" in main_text  # "No articles" empty state
            or len(main_text) > 100
        )
        assert has_content, "Knowledge base page has no visible content"

    def test_kb_live_03_add_button_visible(self, live_kb_page: Page):
        """KB-LIVE-03: Add article/entry button is present."""
        live_kb_page.wait_for_timeout(500)
        add_btn = live_kb_page.get_by_role("button", name="Add").first
        # Button might use different text
        if not add_btn.is_visible():
            add_btn = live_kb_page.locator("button:has-text('Add')").first
        if not add_btn.is_visible():
            add_btn = live_kb_page.locator("button:has-text('New')").first
        assert add_btn.is_visible(), "No Add/New button found on Knowledge Base page"

    def test_kb_live_04_search_input_present(self, live_kb_page: Page):
        """KB-LIVE-04: Search input is present on Knowledge Base page."""
        search = live_kb_page.locator("input[placeholder*='earch']").first
        if not search.is_visible():
            search = live_kb_page.locator("input[type='search']").first
        if not search.is_visible():
            search = live_kb_page.get_by_placeholder("Search").first
        assert search.is_visible(), "No search input found on Knowledge Base page"
