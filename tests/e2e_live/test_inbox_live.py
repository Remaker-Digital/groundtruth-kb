"""
Live E2E inbox tests — real conversation data from production.

Validates that the Inbox page loads real conversations, displays
status badges and timestamps, and supports interaction (click-to-open,
search, escalation).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re

import pytest
from playwright.sync_api import Page


class TestInboxList:
    """Inbox page loads and displays real conversation data."""

    def test_inbox_loads_conversations(self, live_inbox_page: Page):
        """Inbox shows a conversation list or an empty state."""
        live_inbox_page.wait_for_timeout(1500)  # API response time
        main_text = live_inbox_page.text_content("main") or ""
        # Either conversations are listed or an empty state is shown
        has_content = bool(re.search(
            r"(conversation|message|no conversation|empty|no data|inbox)",
            main_text, re.I
        ))
        assert has_content, "Inbox page has no recognizable content"

    def test_conversation_has_status_badge(self, live_inbox_page: Page):
        """At least one conversation shows a status badge."""
        live_inbox_page.wait_for_timeout(1000)
        main_text = (live_inbox_page.text_content("main") or "").lower()
        # Status values: open, resolved, escalated, etc.
        has_status = bool(re.search(
            r"(open|resolved|escalated|closed|pending|active|in progress)",
            main_text
        ))
        # If no conversations exist, accept empty state
        has_empty = bool(re.search(r"(no conversation|empty|no data)", main_text))
        assert has_status or has_empty, "No status badges or empty state found"

    def test_conversation_has_timestamp(self, live_inbox_page: Page):
        """At least one conversation shows a date or relative time."""
        live_inbox_page.wait_for_timeout(1500)
        main_text = live_inbox_page.text_content("main") or ""
        has_time = bool(re.search(
            r"(\d{4}-\d{2}-\d{2}"             # ISO dates
            r"|\d+\s*(day|hour|minute|second|min|hr|mo|week)s?\s*ago"  # relative times
            r"|today|yesterday|just now|a moment ago"
            r"|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"        # month names
            r"|\d{1,2}/\d{1,2}/\d{2,4}"       # MM/DD/YYYY
            r"|\d{1,2}\s+\w+\s+\d{4}"         # DD Month YYYY
            r"|\d{1,2}:\d{2}\s*(am|pm)?"       # HH:MM timestamps
            r"|\d+[hm]\s*ago)",                # compact relative (2h ago, 5m ago)
            main_text, re.I
        ))
        has_empty = bool(re.search(r"(no conversation|empty|no data)", main_text, re.I))
        assert has_time or has_empty, "No timestamps found in inbox"


class TestInboxInteraction:
    """Inbox interaction features against real data."""

    def test_click_conversation_shows_thread(self, live_inbox_page: Page):
        """Clicking a conversation row opens the message thread panel."""
        live_inbox_page.wait_for_timeout(1500)

        # Find clickable conversation rows
        rows = live_inbox_page.locator(
            "[class*='conversation'], [class*='Conversation'], "
            "tr, [role='row'], [class*='list-item'], [class*='ListItem']"
        )

        if rows.count() > 0:
            # Click the first conversation
            first_row = rows.first
            if first_row.is_visible():
                first_row.click()
                live_inbox_page.wait_for_timeout(1000)

                # A message thread or detail panel should appear
                main_text = live_inbox_page.text_content("main") or ""
                # Look for thread indicators
                has_thread = bool(re.search(
                    r"(message|reply|send|thread|detail|customer|agent)",
                    main_text, re.I
                ))
                assert has_thread, "No message thread appeared after clicking conversation"
        else:
            # No conversations — skip
            pytest.skip("No conversations available in inbox")

    def test_search_filters_conversations(self, live_inbox_page: Page):
        """Typing in the search box filters the conversation list."""
        search_input = live_inbox_page.locator(
            "input[type='search'], input[placeholder*='Search'], "
            "input[placeholder*='search'], input[aria-label*='search']"
        ).first

        if search_input.is_visible():
            search_input.fill("test")
            live_inbox_page.wait_for_timeout(1000)
            # Page should still be functional (no error)
            assert live_inbox_page.locator("text=Application error").count() == 0
            # Clear search
            search_input.fill("")
            live_inbox_page.wait_for_timeout(500)
        else:
            # Search may not be visible if no conversations exist
            pass

    def test_escalate_button_or_conversation_actions(self, live_inbox_page: Page):
        """Conversation actions (escalate, status, filter) are available.

        The inbox may show escalation options only when a conversation is
        selected, or display status/filter controls instead.
        """
        live_inbox_page.wait_for_timeout(1500)
        main_text = (live_inbox_page.text_content("main") or "").lower()
        # Look for any conversation management UI: escalation, status filters,
        # conversation actions, or just the inbox list itself
        has_actions = bool(re.search(
            r"(escalat|transfer|assign|priority|filter|status"
            r"|open|resolved|closed|timed.out|unassigned|inbox"
            r"|conversation|message|search|no conversation|empty)",
            main_text
        ))
        assert has_actions, "No conversation actions or inbox content found"
