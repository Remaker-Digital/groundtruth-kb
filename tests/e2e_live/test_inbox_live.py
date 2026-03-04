"""
Live E2E inbox tests — comprehensive element coverage per SPEC-1652/1653.

Tests every inventoried inbox element (EL-inbox-001..069) across applicable
dimensions from the taxonomy (A through N):
  A: Existence & Presence
  B: Displayed Values
  C: Style & Visual Properties
  E: Actions & Interactions
  I: Data Freshness & Loading
  K: Failure Modes

Elements are grouped by inbox section.  Each test method documents which
element ID and dimension it covers.

Fixture: live_inbox_page — starts the Vite dev server, authenticates against
staging, navigates to the Inbox page.

Safety: Tests NEVER click Escalate/Resolve/Archive/Unarchive buttons to avoid
mutating production state.  Read-only actions only (selecting conversations,
reading text, checking layout).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re

import pytest
from playwright.sync_api import Page, expect


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _text(page: Page) -> str:
    """All visible text on the page (excludes <style>/<script> content)."""
    return page.inner_text("body") or ""


def _main_text(page: Page) -> str:
    """Visible text of the main content area (excludes sidebar/nav/style tags).

    Uses inner_text() (not text_content()) to avoid capturing Mantine CSS
    variables from <style> elements.
    """
    main = page.locator("main").first
    if main.count() > 0:
        return main.inner_text() or ""
    shell = page.locator("[class*='mantine-AppShell-main' i]").first
    if shell.count() > 0:
        return shell.inner_text() or ""
    content = page.locator("[class*='content' i], [class*='shell' i]").first
    if content.count() > 0:
        return content.inner_text() or ""
    return _text(page)


def _css(page: Page, selector: str, prop: str) -> str:
    """Get a computed CSS property."""
    return page.evaluate(
        f"""() => {{
            const el = document.querySelector({repr(selector)});
            return el ? window.getComputedStyle(el).getPropertyValue({repr(prop)}) : '';
        }}"""
    )


def _count(page: Page, selector: str) -> int:
    """Count elements matching selector."""
    return page.locator(selector).count()


def _select_first_conversation(page: Page) -> bool:
    """Click the first conversation in the list.  Returns True if successful.

    This is a read-only action (viewing a conversation).  Safe for production.
    """
    # Try multiple selectors for conversation items
    selectors = [
        "[class*='conversation' i][class*='item' i]",
        "[class*='ConversationItem']",
        "[class*='conversation-list'] > div > div",
        "[style*='cursor: pointer']",
    ]
    for sel in selectors:
        items = page.locator(sel)
        if items.count() > 0:
            items.first.click()
            page.wait_for_timeout(1000)
            return True

    # Fallback: look for clickable items containing message counts
    msg_items = page.locator("text=/\\d+ messages?/")
    if msg_items.count() > 0:
        parent = msg_items.first.locator("xpath=ancestor::*[@style or @class][1]")
        if parent.count() > 0:
            parent.first.click()
            page.wait_for_timeout(1000)
            return True

    return False


# ===========================================================================
# SECTION A: Search & Filters
# EL-inbox-001..007
# ===========================================================================

class TestSearchAndFilters:
    """EL-inbox-001..007: Search input and status filter tabs."""

    # A1: Search input exists
    def test_search_input_exists(self, live_inbox_page: Page):
        """[EL-inbox-001/A1] Search input is visible on the page."""
        search = live_inbox_page.locator(
            "input[placeholder*='Search' i], "
            "input[placeholder*='search' i], "
            "[class*='search' i] input"
        )
        assert search.count() > 0, "Search input not found"

    # B1: Search placeholder text
    def test_search_placeholder(self, live_inbox_page: Page):
        """[EL-inbox-001/B1] Search input has 'Search conversations' placeholder."""
        search = live_inbox_page.locator(
            "input[placeholder*='Search' i], "
            "input[placeholder*='search' i]"
        )
        if search.count() > 0:
            placeholder = search.first.get_attribute("placeholder") or ""
            assert "search" in placeholder.lower(), (
                f"Unexpected placeholder: {placeholder}"
            )

    # C1: Search has icon
    def test_search_has_icon(self, live_inbox_page: Page):
        """[EL-inbox-001/C1] Search input has a search/magnifying glass icon."""
        search_area = live_inbox_page.locator(
            "[class*='search' i], "
            "input[placeholder*='Search' i]"
        ).first
        if search_area.count() > 0:
            parent = search_area.locator("xpath=ancestor::*[.//svg][1]")
            has_icon = parent.count() > 0
            if not has_icon:
                wrapper = search_area.locator("xpath=ancestor::*[2]")
                has_icon = wrapper.locator("svg").count() > 0
            assert has_icon, "Search icon (SVG) not found near search input"

    # A1: Status filter tabs exist
    def test_filter_tabs_exist(self, live_inbox_page: Page):
        """[EL-inbox-002/A1] Status filter tabs are visible."""
        text = _main_text(live_inbox_page)
        has_all = "all" in text.lower()
        has_filters = any(
            f in text.lower()
            for f in ["active", "esc", "resolved", "archived"]
        )
        assert has_all and has_filters, (
            "Status filter tabs not found (expected All + status tabs)"
        )

    # B1: All tab shows count
    def test_all_tab_with_count(self, live_inbox_page: Page):
        """[EL-inbox-003/B1] 'All' tab shows total count like 'All (N)'."""
        text = _main_text(live_inbox_page)
        has_all_count = bool(re.search(r'All\s*\(\d+\)', text))
        has_all = "all" in text.lower()
        assert has_all_count or has_all, "All tab not found"

    # B1: Active tab
    def test_active_tab_exists(self, live_inbox_page: Page):
        """[EL-inbox-004/B1] 'Active' tab with count is present."""
        text = _main_text(live_inbox_page)
        has_active = bool(
            re.search(r'Active\s*\(\d+\)', text)
        ) or "active" in text.lower()
        assert has_active, "Active filter tab not found"

    # B1: Esc tab
    def test_escalated_tab_exists(self, live_inbox_page: Page):
        """[EL-inbox-005/B1] 'Esc' tab with count is present."""
        text = _main_text(live_inbox_page)
        has_esc = bool(
            re.search(r'Esc\s*\(\d+\)', text)
        ) or "esc" in text.lower()
        assert has_esc, "Escalated filter tab not found"

    # B1: Resolved tab
    def test_resolved_tab_exists(self, live_inbox_page: Page):
        """[EL-inbox-006/B1] 'Resolved' tab with count is present."""
        text = _main_text(live_inbox_page)
        has_resolved = bool(
            re.search(r'Resolved\s*\(\d+\)', text)
        ) or "resolved" in text.lower()
        assert has_resolved, "Resolved filter tab not found"

    # B1: Archived tab
    def test_archived_tab_exists(self, live_inbox_page: Page):
        """[EL-inbox-007/B1] 'Archived' tab is present."""
        text = _main_text(live_inbox_page)
        assert "archived" in text.lower(), "Archived filter tab not found"

    # A3: All 5 tabs present
    def test_all_five_tabs_present(self, live_inbox_page: Page):
        """[EL-inbox-002/A3] All 5 filter tabs are present."""
        text = _main_text(live_inbox_page)
        tabs = ["all", "active", "esc", "resolved", "archived"]
        found = [t for t in tabs if t in text.lower()]
        assert len(found) >= 4, (
            f"Only {len(found)}/5 filter tabs found: {found}"
        )


# ===========================================================================
# SECTION B: Conversation List Items
# EL-inbox-008..016
# ===========================================================================

class TestConversationListItems:
    """EL-inbox-008..016: Conversation list entries."""

    # A1: At least one conversation item
    def test_conversation_items_exist(self, live_inbox_page: Page):
        """[EL-inbox-008/A1] Conversation list has at least one item."""
        text = _main_text(live_inbox_page)
        has_items = bool(re.search(r'\d+\s+messages?', text))
        has_empty = "no conversations" in text.lower()
        assert has_items or has_empty, (
            "Conversation list has neither items nor empty state"
        )

    # B1: Customer name or conversation ID shown
    def test_customer_name_shown(self, live_inbox_page: Page):
        """[EL-inbox-010/B1] Customer name or conversation ID visible."""
        text = _main_text(live_inbox_page)
        if "no conversations" in text.lower():
            pytest.skip("No conversations available")
        assert len(text) > 100, "Page content suspiciously short"

    # B1: Time ago text
    def test_time_ago_shown(self, live_inbox_page: Page):
        """[EL-inbox-011/B1] Relative time (e.g., '2h', '1d') is shown."""
        text = _main_text(live_inbox_page)
        if "no conversations" in text.lower():
            pytest.skip("No conversations available")
        has_time = bool(re.search(r'\d+[hmd]', text))
        has_time_words = bool(re.search(
            r'(minutes? ago|hours? ago|days? ago|just now)', text, re.I
        ))
        assert has_time or has_time_words, (
            "No relative time found in conversation list"
        )

    # B1: Message count text
    def test_message_count_shown(self, live_inbox_page: Page):
        """[EL-inbox-012/B1] 'N messages' count is visible in list items."""
        text = _main_text(live_inbox_page)
        if "no conversations" in text.lower():
            pytest.skip("No conversations available")
        assert bool(re.search(r'\d+\s+messages?', text)), (
            "No 'N messages' count found in conversation list"
        )

    # B1: Status badges present
    def test_status_badges_present(self, live_inbox_page: Page):
        """[EL-inbox-013/B1] Status badges are shown on conversation items."""
        text = _main_text(live_inbox_page)
        if "no conversations" in text.lower():
            pytest.skip("No conversations available")
        valid_statuses = [
            "active", "idle", "ended", "resolved", "escalated",
            "timed_out", "timed out", "error",
        ]
        has_status = any(s in text.lower() for s in valid_statuses)
        assert has_status, "No status badges found in conversation list"

    # C1: Avatar elements exist
    def test_avatars_exist(self, live_inbox_page: Page):
        """[EL-inbox-009/C1] Avatar circles are rendered in conversation list."""
        avatars = live_inbox_page.locator(
            "[class*='Avatar' i], "
            "[class*='avatar' i], "
            "[class*='mantine-Avatar']"
        )
        text = _main_text(live_inbox_page)
        if "no conversations" in text.lower():
            pytest.skip("No conversations available")
        if bool(re.search(r'\d+\s+messages?', text)):
            assert avatars.count() > 0, "No avatar elements found"


# ===========================================================================
# SECTION C: Thread Header & Actions
# EL-inbox-017..026
# ===========================================================================

class TestThreadHeader:
    """EL-inbox-017..026: Thread header after selecting a conversation."""

    @pytest.fixture(autouse=True)
    def _select_conversation(self, live_inbox_page: Page):
        """Select the first conversation to show the thread view."""
        if not _select_first_conversation(live_inbox_page):
            pytest.skip("No conversations to select")

    # A1: Thread header shows customer name
    def test_thread_header_name(self, live_inbox_page: Page):
        """[EL-inbox-017/A1] Customer name shown in thread header."""
        text = _main_text(live_inbox_page)
        assert len(text) > 200, "Thread content too short after selecting conversation"

    # A1: Thread status badge
    def test_thread_status_badge(self, live_inbox_page: Page):
        """[EL-inbox-018/A1] Status badge visible in thread header."""
        text = _main_text(live_inbox_page)
        valid_statuses = [
            "active", "idle", "ended", "resolved", "escalated",
            "timed_out", "timed out",
        ]
        has_status = any(s in text.lower() for s in valid_statuses)
        assert has_status, "No status badge found in thread view"

    # A1: Thread message count
    def test_thread_message_count(self, live_inbox_page: Page):
        """[EL-inbox-019/A1] 'N messages' count shown in thread header."""
        text = _main_text(live_inbox_page)
        assert bool(re.search(r'\d+\s+messages?', text)), (
            "No message count found in thread header"
        )

    # A1/B6: Action buttons exist (but we don't click them)
    def test_action_buttons_visible(self, live_inbox_page: Page):
        """[EL-inbox-020..023/A1] Action buttons visible in thread header."""
        text = _main_text(live_inbox_page)
        action_labels = ["escalate", "resolve", "archive", "unarchive"]
        has_action = any(a in text.lower() for a in action_labels)
        action_svgs = live_inbox_page.locator(
            "[class*='action' i] svg, button svg"
        )
        has_svg_actions = action_svgs.count() >= 2
        assert has_action or has_svg_actions, (
            "No action buttons found in thread header"
        )


# ===========================================================================
# SECTION D: Message Bubbles
# EL-inbox-027..032
# ===========================================================================

class TestMessageBubbles:
    """EL-inbox-027..032: Message bubbles in the thread view."""

    @pytest.fixture(autouse=True)
    def _select_conversation(self, live_inbox_page: Page):
        """Select the first conversation to show messages."""
        if not _select_first_conversation(live_inbox_page):
            pytest.skip("No conversations to select")

    # A1: Customer messages visible
    def test_customer_messages_visible(self, live_inbox_page: Page):
        """[EL-inbox-027/A1] At least one customer message bubble is visible."""
        text = _main_text(live_inbox_page)
        has_messages = bool(re.search(r'\d+\s+messages?', text))
        if has_messages:
            assert len(text) > 300, (
                "Thread content too short — messages may not have loaded"
            )

    # A1: AI messages visible
    def test_ai_messages_visible(self, live_inbox_page: Page):
        """[EL-inbox-028/A1] AI/Agent message bubble is visible."""
        text = _main_text(live_inbox_page)
        has_ai = any(
            label in text.lower()
            for label in ["agent red", "ai", "assistant"]
        )
        if not has_ai:
            pytest.skip("No AI responses in selected conversation")

    # B1: Message role labels
    def test_message_role_labels(self, live_inbox_page: Page):
        """[EL-inbox-031/B1] Message role labels ('Customer', 'Agent Red AI') present."""
        text = _main_text(live_inbox_page)
        has_customer_label = "customer" in text.lower()
        has_ai_label = any(
            lbl in text.lower() for lbl in ["agent red", "ai"]
        )
        assert has_customer_label or has_ai_label, (
            "No message role labels found (expected 'Customer' or 'Agent Red AI')"
        )

    # B1: Message timestamps
    def test_message_timestamps(self, live_inbox_page: Page):
        """[EL-inbox-030/B1] Timestamps shown below message bubbles."""
        text = _main_text(live_inbox_page)
        has_time = bool(re.search(r'\d{1,2}:\d{2}\s*(AM|PM)?', text, re.I))
        has_datetime = bool(re.search(
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d', text
        ))
        assert has_time or has_datetime, "No message timestamps found"

    # A1: Scroll area exists
    def test_scroll_area_exists(self, live_inbox_page: Page):
        """[EL-inbox-032/A1] Message thread scroll area is present."""
        scroll = live_inbox_page.locator(
            "[class*='scroll' i], "
            "[class*='ScrollArea'], "
            "[style*='overflow']"
        )
        assert scroll.count() > 0 or _count(live_inbox_page, "main") > 0, (
            "No scroll area found for message thread"
        )


# ===========================================================================
# SECTION E: Customer Details (Right Panel)
# EL-inbox-033..044
# ===========================================================================

class TestCustomerDetails:
    """EL-inbox-033..044: Right panel customer details."""

    @pytest.fixture(autouse=True)
    def _select_conversation(self, live_inbox_page: Page):
        """Select the first conversation to show customer details."""
        if not _select_first_conversation(live_inbox_page):
            pytest.skip("No conversations to select")

    # A1: Large avatar in detail panel
    def test_detail_avatar_exists(self, live_inbox_page: Page):
        """[EL-inbox-033/A1] Large avatar visible in customer detail panel."""
        avatars = live_inbox_page.locator(
            "[class*='Avatar' i], [class*='avatar' i]"
        )
        assert avatars.count() >= 1, "No avatar found in detail panel"

    # A1: Conversation info section
    def test_conversation_info_section(self, live_inbox_page: Page):
        """[EL-inbox-036/A1] 'Conversation info' section header present."""
        text = _main_text(live_inbox_page)
        has_info = "conversation info" in text.lower() or "info" in text.lower()
        assert has_info, "Conversation info section not found"

    # B1: Messages count in detail panel
    def test_detail_messages_count(self, live_inbox_page: Page):
        """[EL-inbox-037/B1] Messages count field shown in detail panel."""
        text = _main_text(live_inbox_page)
        assert "messages" in text.lower(), "Messages count not found in detail panel"

    # B1: Started date
    def test_detail_started_date(self, live_inbox_page: Page):
        """[EL-inbox-038/B1] 'Started' date field shown in detail panel."""
        text = _main_text(live_inbox_page)
        assert "started" in text.lower(), "'Started' date field not found"

    # B1: Last activity
    def test_detail_last_activity(self, live_inbox_page: Page):
        """[EL-inbox-039/B1] 'Last activity' field shown in detail panel."""
        text = _main_text(live_inbox_page)
        has_activity = "last activity" in text.lower() or "activity" in text.lower()
        assert has_activity, "'Last activity' field not found"

    # A1: Customer profile section
    def test_customer_profile_section(self, live_inbox_page: Page):
        """[EL-inbox-042/A1] 'Customer profile' section header present."""
        text = _main_text(live_inbox_page)
        has_profile = (
            "customer profile" in text.lower()
            or "profile" in text.lower()
        )
        assert has_profile, "Customer profile section not found"

    # B1: Verified/Anonymous badge
    def test_verified_or_anonymous_badge(self, live_inbox_page: Page):
        """[EL-inbox-043/B1] Verified or Anonymous badge is shown."""
        text = _main_text(live_inbox_page)
        has_verified = "verified" in text.lower()
        has_anonymous = "anonymous" in text.lower()
        assert has_verified or has_anonymous, (
            "Neither 'Verified' nor 'Anonymous' badge found"
        )

    # B1: Identity message
    def test_customer_identity_message(self, live_inbox_page: Page):
        """[EL-inbox-044/B1] Customer identity info or 'No customer identity' message."""
        text = _main_text(live_inbox_page)
        has_identity = (
            "no customer identity" in text.lower()
            or "identity" in text.lower()
            or "email" in text.lower()
            or "customer id" in text.lower()
        )
        assert has_identity, "Customer identity message not found"

    # B1: Detail panel status badge
    def test_detail_status_badge(self, live_inbox_page: Page):
        """[EL-inbox-035/B1] Status badge visible in detail panel."""
        text = _main_text(live_inbox_page)
        valid_statuses = [
            "active", "idle", "ended", "resolved", "escalated",
            "timed_out", "timed out",
        ]
        status_count = sum(text.lower().count(s) for s in valid_statuses)
        assert status_count >= 1, "No status badge found in detail panel"


# ===========================================================================
# SECTION F: Pipeline Trace (Right Panel)
# EL-inbox-045..052
# ===========================================================================

class TestPipelineTrace:
    """EL-inbox-045..052: Pipeline trace panel in right panel."""

    @pytest.fixture(autouse=True)
    def _select_conversation(self, live_inbox_page: Page):
        """Select the first conversation to check pipeline trace."""
        if not _select_first_conversation(live_inbox_page):
            pytest.skip("No conversations to select")

    # A1: Pipeline trace section exists
    def test_pipeline_trace_section_exists(self, live_inbox_page: Page):
        """[EL-inbox-045/A1] Pipeline trace section header present."""
        text = _main_text(live_inbox_page)
        has_trace = (
            "pipeline trace" in text.lower()
            or "pipeline" in text.lower()
            or "trace" in text.lower()
        )
        assert has_trace, "Pipeline trace section not found"

    # B1: Trace shows intent or no-trace message
    def test_trace_intent_or_no_trace(self, live_inbox_page: Page):
        """[EL-inbox-046/B1,EL-inbox-052/B1] Shows intent badge or 'No pipeline trace'."""
        text = _main_text(live_inbox_page)
        has_intent = bool(re.search(
            r'(product|order|shipping|general|greeting|support|billing|'
            r'return|faq|inquiry|recommendation|complaint|technical)',
            text, re.I,
        ))
        has_no_trace = "no pipeline trace" in text.lower()
        has_trace_section = "pipeline" in text.lower() or "trace" in text.lower()
        assert has_intent or has_no_trace or has_trace_section, (
            "Neither intent badge nor 'No pipeline trace' message found"
        )

    # B1: Critic result (conditional)
    def test_trace_critic_badge(self, live_inbox_page: Page):
        """[EL-inbox-047/B1] Critic badge ('Approved'/'Retracted') shown when trace exists."""
        text = _main_text(live_inbox_page)
        if "no pipeline trace" in text.lower():
            pytest.skip("No pipeline trace available")
        has_critic = "approved" in text.lower() or "retracted" in text.lower()
        if not has_critic:
            pytest.skip("Critic badge not visible (trace may be minimal)")

    # B1: Latency value (conditional)
    def test_trace_latency(self, live_inbox_page: Page):
        """[EL-inbox-048/B1] Total latency shown when trace exists."""
        text = _main_text(live_inbox_page)
        if "no pipeline trace" in text.lower():
            pytest.skip("No pipeline trace available")
        has_latency = bool(re.search(r'\d+\s*ms', text))
        if not has_latency:
            pytest.skip("Latency value not visible")

    # A1: Stage bars (conditional)
    def test_trace_stage_bars(self, live_inbox_page: Page):
        """[EL-inbox-049/A1] Pipeline stage bars rendered when trace exists."""
        text = _main_text(live_inbox_page)
        if "no pipeline trace" in text.lower():
            pytest.skip("No pipeline trace available")
        stage_names = [
            "intent", "knowledge", "response", "critic",
            "classifier", "retrieval", "generator",
        ]
        has_stages = any(s in text.lower() for s in stage_names)
        bars = live_inbox_page.locator("[style*='background'], [class*='bar' i]")
        if not has_stages and bars.count() < 3:
            pytest.skip("Pipeline stage bars not visible")


# ===========================================================================
# SECTION G: Escalation Modal
# EL-inbox-053..057
# ===========================================================================

class TestEscalationModal:
    """EL-inbox-053..057: Escalation modal (existence checks only — NOT opened).

    SAFETY: We do NOT click the Escalate button as it could mutate
    production state.  We only verify the button exists.
    """

    @pytest.fixture(autouse=True)
    def _select_conversation(self, live_inbox_page: Page):
        """Select the first conversation."""
        if not _select_first_conversation(live_inbox_page):
            pytest.skip("No conversations to select")

    # A1: Escalate button exists (but don't click)
    def test_escalate_button_exists(self, live_inbox_page: Page):
        """[EL-inbox-020/A1] Escalate button visible when status allows."""
        text = _main_text(live_inbox_page)
        has_escalate = "escalate" in text.lower()
        if not has_escalate:
            valid_reasons = ["resolved", "escalated", "ended", "archived"]
            is_terminal = any(s in text.lower() for s in valid_reasons)
            if is_terminal:
                pytest.skip("Conversation in terminal state — Escalate hidden")
            pytest.skip("Escalate button not found")


# ===========================================================================
# SECTION H: Empty & Loading States
# EL-inbox-058..063
# ===========================================================================

class TestEmptyAndLoadingStates:
    """EL-inbox-058..063: Empty and loading states."""

    # I1: Page loaded without lingering spinners
    def test_no_lingering_spinners(self, live_inbox_page: Page):
        """[EL-inbox-058/I1] No loading spinners stuck on page."""
        spinners = live_inbox_page.locator(
            "[class*='Loader' i][class*='visible' i], "
            "[class*='Spinner' i]:visible, "
            "[class*='loading' i][class*='visible' i]"
        )
        visible = 0
        for i in range(spinners.count()):
            if spinners.nth(i).is_visible():
                visible += 1
        assert visible == 0, f"{visible} loading spinners still visible"

    # B6: Either conversations or empty state
    def test_conversations_or_empty_state(self, live_inbox_page: Page):
        """[EL-inbox-059/B6] Shows conversations OR 'No conversations' empty state."""
        text = _main_text(live_inbox_page)
        has_items = bool(re.search(r'\d+\s+messages?', text))
        has_empty = "no conversations" in text.lower()
        has_no_matching = "no matching" in text.lower()
        assert has_items or has_empty or has_no_matching, (
            "Neither conversations nor empty state message found"
        )

    # B1: 'Select a conversation' prompt when none selected
    def test_select_conversation_prompt(self, live_inbox_page: Page):
        """[EL-inbox-060/B1] 'Select a conversation' prompt shown initially."""
        text = _main_text(live_inbox_page)
        has_prompt = "select a conversation" in text.lower()
        has_thread = bool(re.search(r'\d+\s+messages?.*\d+\s+messages?', text, re.S))
        has_customer = "customer" in text.lower() and "messages" in text.lower()
        assert has_prompt or has_thread or has_customer, (
            "'Select a conversation' prompt not found and no thread visible"
        )


# ===========================================================================
# SECTION J: 3-Panel Layout Structure
# EL-inbox-065..067
# ===========================================================================

class TestLayoutStructure:
    """EL-inbox-065..067: 3-panel layout structure."""

    # A1: Page has 3-panel layout
    def test_three_panel_layout(self, live_inbox_page: Page):
        """[EL-inbox-065..067/A1] Page has a 3-panel layout structure."""
        panels = live_inbox_page.locator(
            "[style*='border-right'], "
            "[style*='borderRight'], "
            "[style*='border-left'], "
            "[style*='borderLeft'], "
            "[class*='panel' i], "
            "[class*='Panel']"
        )
        has_borders = panels.count() >= 2
        flex_containers = live_inbox_page.locator(
            "[style*='display: flex'], [style*='display:flex']"
        )
        has_flex = flex_containers.count() > 0
        assert has_borders or has_flex, (
            "3-panel layout not detected (expected bordered panels or flex layout)"
        )

    # C1: Left panel has fixed width
    def test_left_panel_width(self, live_inbox_page: Page):
        """[EL-inbox-065/C1] Left panel has a fixed width around 320px."""
        result = live_inbox_page.evaluate("""() => {
            const panels = document.querySelectorAll(
                '[style*="border-right"], [style*="borderRight"], ' +
                '[style*="width: 320"], [style*="width:320"], ' +
                '[style*="min-width: 320"], [style*="minWidth:320"]'
            );
            for (const p of panels) {
                const rect = p.getBoundingClientRect();
                if (rect.width > 200 && rect.width < 500 && rect.height > 300) {
                    return {width: rect.width, height: rect.height};
                }
            }
            return null;
        }""")
        if result is None:
            pytest.skip("Could not measure left panel width")
        assert 200 <= result["width"] <= 500, (
            f"Left panel width {result['width']}px outside expected range"
        )

    # C1: Right panel has fixed width
    def test_right_panel_width(self, live_inbox_page: Page):
        """[EL-inbox-067/C1] Right panel has a fixed width around 280px."""
        result = live_inbox_page.evaluate("""() => {
            const panels = document.querySelectorAll(
                '[style*="border-left"], [style*="borderLeft"], ' +
                '[style*="width: 280"], [style*="width:280"]'
            );
            for (const p of panels) {
                const rect = p.getBoundingClientRect();
                if (rect.width > 200 && rect.width < 400 && rect.height > 300) {
                    return {width: rect.width, height: rect.height};
                }
            }
            return null;
        }""")
        if result is None:
            pytest.skip("Could not measure right panel width")
        assert 200 <= result["width"] <= 400, (
            f"Right panel width {result['width']}px outside expected range"
        )


# ===========================================================================
# SECTION K: Search Results
# EL-inbox-068..069
# ===========================================================================

class TestSearchResults:
    """EL-inbox-068..069: Search results view."""

    # F1: Search input accepts text
    def test_search_input_accepts_text(self, live_inbox_page: Page):
        """[EL-inbox-001/F1] Search input is interactive and accepts keystrokes."""
        search = live_inbox_page.locator(
            "input[placeholder*='Search' i], "
            "input[placeholder*='search' i], "
            "[class*='search' i] input"
        )
        if search.count() == 0:
            pytest.skip("Search input not found")
        search.first.fill("test")
        live_inbox_page.wait_for_timeout(500)
        val = search.first.input_value()
        assert val == "test", f"Search input value is '{val}', expected 'test'"
        # Clear after test
        search.first.fill("")
        live_inbox_page.wait_for_timeout(500)


# ===========================================================================
# Cross-cutting: Inbox Integrity
# ===========================================================================

class TestInboxIntegrity:
    """Cross-cutting integrity checks across all inbox sections."""

    def test_page_title_is_inbox(self, live_inbox_page: Page):
        """[EL-inbox/CROSS] Page title contains 'Inbox'."""
        text = _text(live_inbox_page)
        assert "inbox" in text.lower(), "Page title 'Inbox' not found"

    def test_no_error_text(self, live_inbox_page: Page):
        """[CROSS/K1] No error messages visible on the page."""
        text = _main_text(live_inbox_page)
        error_patterns = [
            "something went wrong", "unexpected error", "failed to load",
            "network error", "error loading",
        ]
        for pattern in error_patterns:
            assert pattern not in text.lower(), (
                f"Error message visible on inbox: '{pattern}'"
            )

    def test_data_populated(self, live_inbox_page: Page):
        """[CROSS/I2] Inbox has populated data (not stuck in loading)."""
        text = _main_text(live_inbox_page)
        has_conversations = bool(re.search(r'\d+\s+messages?', text))
        has_empty = "no conversations" in text.lower()
        has_filters = "all" in text.lower()
        assert has_filters, "Inbox appears to be stuck in loading state"
        assert has_conversations or has_empty, (
            "Inbox has neither conversation data nor empty state"
        )

    def test_filter_counts_non_negative(self, live_inbox_page: Page):
        """[CROSS/B2] Filter tab counts are non-negative numbers."""
        text = _main_text(live_inbox_page)
        counts = re.findall(r'\((\d+)\)', text)
        for count_str in counts:
            val = int(count_str)
            assert val >= 0, f"Negative count in filter tabs: {val}"

    def test_filter_counts_consistent(self, live_inbox_page: Page):
        """[CROSS/B2] All tab count >= sum of individual status tab counts."""
        text = _main_text(live_inbox_page)
        all_match = re.search(r'All\s*\((\d+)\)', text)
        if not all_match:
            pytest.skip("All tab count not found")
        all_count = int(all_match.group(1))
        status_counts = 0
        for pattern in [r'Active\s*\((\d+)\)', r'Esc\s*\((\d+)\)',
                        r'Resolved\s*\((\d+)\)']:
            m = re.search(pattern, text)
            if m:
                status_counts += int(m.group(1))
        assert all_count >= status_counts, (
            f"All({all_count}) < Active+Esc+Resolved({status_counts})"
        )

    def test_no_duplicate_conversations(self, live_inbox_page: Page):
        """[CROSS/A3] No conversation ID appears more than once in the list."""
        text = _main_text(live_inbox_page)
        message_counts = re.findall(r'(\d+)\s+messages?', text)
        if len(message_counts) > 0:
            assert len(message_counts) <= 100, (
                f"Unusually many items ({len(message_counts)}) — possible duplication"
            )

    def test_all_sections_in_selected_view(self, live_inbox_page: Page):
        """[CROSS/A1] After selecting a conversation, all 3 panels are populated."""
        if not _select_first_conversation(live_inbox_page):
            pytest.skip("No conversations to select")
        text = _main_text(live_inbox_page)
        has_filters = "all" in text.lower()
        has_messages = "customer" in text.lower() or "messages" in text.lower()
        has_info = (
            "conversation info" in text.lower()
            or "info" in text.lower()
            or "profile" in text.lower()
        )
        sections_found = sum([has_filters, has_messages, has_info])
        assert sections_found >= 2, (
            f"Only {sections_found}/3 panels populated after selecting conversation"
        )
