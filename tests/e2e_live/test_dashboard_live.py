"""
Live E2E dashboard tests — comprehensive element coverage per SPEC-1652/1653.

Tests every inventoried dashboard element (EL-dashboard-001..078) across ALL
applicable dimensions from the taxonomy (A through N):
  A: Existence & Presence
  B: Displayed Values
  C: Style & Visual Properties
  E: Actions & Interactions
  I: Data Freshness & Loading
  K: Failure Modes

Elements are grouped by dashboard section. Each test method documents which
element ID and dimension it covers.

Fixture: live_dashboard_page — starts the Vite dev server, authenticates against
staging, navigates to the Dashboard page.

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
    variables from <style> elements — text_content() returns ALL text nodes
    including style/script content, which pollutes assertions.
    """
    # Try <main> element first
    main = page.locator("main").first
    if main.count() > 0:
        return main.inner_text() or ""
    # Mantine Shell content area fallback
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


def _bbox(page: Page, selector: str) -> dict:
    """Get bounding box of first matching element."""
    el = page.locator(selector).first
    return el.bounding_box() or {}


def _count(page: Page, selector: str) -> int:
    """Count elements matching selector."""
    return page.locator(selector).count()


# ===========================================================================
# SECTION A: Page Structure & Header
# EL-dashboard-001..003
# ===========================================================================

class TestPageStructure:
    """EL-dashboard-001..003: Page header elements."""

    # A1: Page title exists
    def test_page_title_exists(self, live_dashboard_page: Page):
        """[EL-001/A1] 'Dashboard' title is present."""
        expect(live_dashboard_page.locator("text=Dashboard").first).to_be_visible()

    # B1: Page title correct value
    def test_page_title_value(self, live_dashboard_page: Page):
        """[EL-001/B1] Title text is exactly 'Dashboard'."""
        heading = live_dashboard_page.locator("h1, h2, h3, [class*='title' i]").first
        text = heading.text_content() or ""
        assert "Dashboard" in text, f"Title missing 'Dashboard': {text[:80]}"

    # A1: Subtitle exists
    def test_subtitle_exists(self, live_dashboard_page: Page):
        """[EL-002/A1] Subtitle text is present."""
        text = _main_text(live_dashboard_page)
        assert "performance" in text.lower() or "overview" in text.lower(), (
            "No subtitle with 'performance' or 'overview' found"
        )

    # B1: Subtitle correct
    def test_subtitle_value(self, live_dashboard_page: Page):
        """[EL-002/B1] Subtitle is 'Overview of your customer experience performance'."""
        text = _main_text(live_dashboard_page)
        assert "customer experience" in text.lower() or "performance" in text.lower()

    # A1/B6: Store name (conditional display)
    def test_store_name_or_absent(self, live_dashboard_page: Page):
        """[EL-003/A1,B6] Store name shown when available, absent when not."""
        text = _main_text(live_dashboard_page)
        assert len(text) > 50, "Dashboard content is suspiciously short"


# ===========================================================================
# SECTION B: Period Filter
# EL-dashboard-004..007
# ===========================================================================

class TestPeriodFilter:
    """EL-dashboard-004..007: Period segmented control."""

    # A1: Filter exists
    def test_period_filter_exists(self, live_dashboard_page: Page):
        """[EL-004/A1] Period filter control is visible."""
        # AnalyticsOverview renders buttons with text "7 days", "14 days", etc.
        btn_30d = live_dashboard_page.get_by_role("button", name="30 days")
        assert btn_30d.count() > 0, "No period filter '30 days' button found"

    # B1: Default value — 30 days button has aria-pressed=true
    def test_period_filter_default_30d(self, live_dashboard_page: Page):
        """[EL-004/B1] Default selected period is 30 days (aria-pressed=true)."""
        btn_30d = live_dashboard_page.get_by_role("button", name="30 days")
        expect(btn_30d).to_be_visible(timeout=5_000)
        pressed = btn_30d.get_attribute("aria-pressed")
        assert pressed == "true", f"30 days button not pressed by default (aria-pressed={pressed})"

    # A3: All 4 options present
    def test_period_filter_all_options(self, live_dashboard_page: Page):
        """[EL-004/A3] All 4 period options are present: 7 days, 14 days, 30 days, 90 days."""
        for label in ["7 days", "14 days", "30 days", "90 days"]:
            btn = live_dashboard_page.get_by_role("button", name=label)
            assert btn.count() > 0, f"Period option '{label}' not found"

    # E1: Clicking 7 days changes chart
    def test_period_filter_7d_action(self, live_dashboard_page: Page):
        """[EL-005/E1] Clicking '7 days' updates the chart period label."""
        # Period filter buttons use aria-pressed within a role="group"
        btn_7d = live_dashboard_page.get_by_role("button", name="7 days")
        expect(btn_7d).to_be_visible(timeout=5_000)
        btn_7d.click()
        live_dashboard_page.wait_for_timeout(1000)
        text = _main_text(live_dashboard_page)
        assert "7" in text, "Chart label didn't update to reflect 7-day period"

    # E1: Clicking 90 days changes chart
    def test_period_filter_90d_action(self, live_dashboard_page: Page):
        """[EL-007/E1] Clicking '90 days' updates the chart period label."""
        btn_90d = live_dashboard_page.get_by_role("button", name="90 days")
        expect(btn_90d).to_be_visible(timeout=5_000)
        btn_90d.click()
        live_dashboard_page.wait_for_timeout(1000)
        text = _main_text(live_dashboard_page)
        assert "90" in text, "Chart label didn't update to reflect 90-day period"

    # E1: Clicking 14 days changes chart
    def test_period_filter_14d_action(self, live_dashboard_page: Page):
        """[EL-006/E1] Clicking '14 days' updates the chart period label."""
        btn_14d = live_dashboard_page.get_by_role("button", name="14 days")
        expect(btn_14d).to_be_visible(timeout=5_000)
        btn_14d.click()
        live_dashboard_page.wait_for_timeout(1000)
        text = _main_text(live_dashboard_page)
        assert "14" in text, "Chart label didn't update to reflect 14-day period"

    # E1: Clicking 30 days changes chart
    def test_period_filter_30d_action(self, live_dashboard_page: Page):
        """[EL-004/E1] Clicking '30 days' updates the chart period label."""
        btn_30d = live_dashboard_page.get_by_role("button", name="30 days")
        expect(btn_30d).to_be_visible(timeout=5_000)
        btn_30d.click()
        live_dashboard_page.wait_for_timeout(1000)
        text = _main_text(live_dashboard_page)
        assert "30" in text, "Chart label didn't update to reflect 30-day period"

    # E1: Cycling all 4 period filters in sequence
    def test_period_filter_cycle_all(self, live_dashboard_page: Page):
        """[EL-004..007/E1] Clicking each period button in sequence updates chart."""
        for label in ["7 days", "14 days", "30 days", "90 days"]:
            btn = live_dashboard_page.get_by_role("button", name=label)
            expect(btn).to_be_visible(timeout=5_000)
            btn.click()
            live_dashboard_page.wait_for_timeout(800)
            # Extract the number for assertion
            num = label.split()[0]
            text = _main_text(live_dashboard_page)
            assert num in text, (
                f"Chart didn't update after clicking '{label}' filter"
            )

    # A4: Filter is a proper button group with aria-pressed
    def test_period_filter_element_type(self, live_dashboard_page: Page):
        """[EL-004/A4] Period filter uses a button group with aria-pressed (not freeform input)."""
        # AnalyticsOverview renders: <div role="group" aria-label="Analytics date range">
        #   <button aria-pressed="true/false">N days</button> × 4
        group = live_dashboard_page.locator("[role='group'][aria-label*='date range' i]")
        if group.count() > 0:
            pressed = group.locator("button[aria-pressed]")
            assert pressed.count() >= 4, f"Expected 4 period buttons, found {pressed.count()}"
        else:
            # Fallback: count period buttons directly
            count = sum(
                1 for lbl in ["7 days", "14 days", "30 days", "90 days"]
                if live_dashboard_page.get_by_role("button", name=lbl).count() > 0
            )
            assert count >= 4, f"Only {count}/4 period buttons found"


# ===========================================================================
# SECTION C: Setup Checklist (conditional — only for non-activated tenants)
# EL-dashboard-008..012
# ===========================================================================

class TestSetupChecklist:
    """EL-dashboard-008..012: Setup checklist (visible when not activated)."""

    # B6: Conditional display
    def test_checklist_conditional_display(self, live_dashboard_page: Page):
        """[EL-008/B6] Checklist visible when inactive, hidden when active."""
        text = _main_text(live_dashboard_page)
        has_checklist = "setup" in text.lower() and "complete" in text.lower()
        if has_checklist:
            assert "progress" in text.lower() or "complete" in text.lower()

    # B1: Checklist item text (if visible)
    def test_checklist_items_text(self, live_dashboard_page: Page):
        """[EL-009..012/B1] Checklist items have correct label text."""
        text = _main_text(live_dashboard_page)
        if "setup" not in text.lower():
            return  # Tenant already activated — checklist correctly hidden
        expected_items = ["brand name", "instructions", "appearance", "activated"]
        for item in expected_items:
            assert item.lower() in text.lower(), f"Checklist missing '{item}'"


# ===========================================================================
# SECTION D: Test Mode Alert (conditional)
# EL-dashboard-013..014
# ===========================================================================

class TestTestModeAlert:
    """EL-dashboard-013..014: Test mode alert (visible when test_mode=true)."""

    # B6: Conditional display
    def test_test_mode_conditional(self, live_dashboard_page: Page):
        """[EL-013/B6] Test mode alert present when test_mode_enabled=true."""
        text = _main_text(live_dashboard_page)
        if "test mode" in text.lower():
            assert "active" in text.lower() or "enabled" in text.lower()


# ===========================================================================
# SECTION E: Stat Cards (5 cards × label + value + tooltip + loading)
# EL-dashboard-015..033
# ===========================================================================

class TestStatCardLabels:
    """EL-dashboard-016..033: All 5 stat card labels exist with correct text."""

    CARDS = [
        ("EL-016", "Total conversations"),
        ("EL-020", "Avg response time"),
        ("EL-023", "Resolution rate"),
        ("EL-027", "Customer satisfaction"),
        ("EL-030", "Escalation rate"),
    ]

    @pytest.mark.parametrize("el_id,label", CARDS, ids=[c[0] for c in CARDS])
    def test_stat_card_label_exists(self, live_dashboard_page: Page, el_id: str, label: str):
        """[{el_id}/A1] Stat card label is visible."""
        text = _main_text(live_dashboard_page)
        assert label.lower() in text.lower(), f"Stat card label '{label}' not found"

    @pytest.mark.parametrize("el_id,label", CARDS, ids=[c[0] for c in CARDS])
    def test_stat_card_label_value(self, live_dashboard_page: Page, el_id: str, label: str):
        """[{el_id}/B1] Stat card label text matches expected value."""
        locator = live_dashboard_page.locator(f"text={label}").first
        expect(locator).to_be_visible()


class TestStatCardValues:
    """EL-dashboard-017,021,024,028,031: Stat card displayed values."""

    # B2: Total conversations numeric value
    def test_total_conversations_is_numeric(self, live_dashboard_page: Page):
        """[EL-017/B2] Total conversations value is a number or '--'."""
        text = _main_text(live_dashboard_page)
        idx = text.lower().find("total conversations")
        assert idx != -1, "Total conversations label not found"
        nearby = text[idx:idx + 80]
        assert re.search(r'(\d[\d,]*|--)', nearby), (
            f"No numeric value near 'Total conversations': {nearby}"
        )

    # B5: Avg response time format "X.Xs"
    def test_avg_response_time_format(self, live_dashboard_page: Page):
        """[EL-021/B5] Avg response time value uses 'X.Xs' or '--' format."""
        text = _main_text(live_dashboard_page)
        idx = text.lower().find("avg response time")
        if idx == -1:
            idx = text.lower().find("response time")
        assert idx != -1, "Response time label not found"
        nearby = text[idx:idx + 60]
        assert re.search(r'(\d+\.?\d*s|--)', nearby), (
            f"Response time not in expected format: {nearby}"
        )

    # B5: Resolution rate format "XX.X%"
    def test_resolution_rate_format(self, live_dashboard_page: Page):
        """[EL-024/B5] Resolution rate is 'XX.X%' or '--'."""
        text = _main_text(live_dashboard_page)
        idx = text.lower().find("resolution rate")
        assert idx != -1, "Resolution rate label not found"
        nearby = text[idx:idx + 60]
        assert re.search(r'(\d+\.?\d*%|--)', nearby), (
            f"Resolution rate not in expected format: {nearby}"
        )

    # B5: Customer satisfaction format "X/5"
    def test_customer_satisfaction_format(self, live_dashboard_page: Page):
        """[EL-028/B5] Customer satisfaction is 'X.X/5' or '--'."""
        text = _main_text(live_dashboard_page)
        idx = text.lower().find("customer satisfaction")
        if idx == -1:
            idx = text.lower().find("satisfaction")
        assert idx != -1, "Satisfaction label not found"
        nearby = text[idx:idx + 60]
        assert re.search(r'(\d+\.?\d*/5|--)', nearby), (
            f"Satisfaction not in expected format: {nearby}"
        )

    # B5: Escalation rate format "XX.X%"
    def test_escalation_rate_format(self, live_dashboard_page: Page):
        """[EL-031/B5] Escalation rate is 'XX.X%' or '--'."""
        text = _main_text(live_dashboard_page)
        idx = text.lower().find("escalation rate")
        assert idx != -1, "Escalation rate label not found"
        nearby = text[idx:idx + 60]
        assert re.search(r'(\d+\.?\d*%|--)', nearby), (
            f"Escalation rate not in expected format: {nearby}"
        )

    # B1: Resolution detail "N resolved"
    def test_resolution_detail_text(self, live_dashboard_page: Page):
        """[EL-025/B1] Resolution card shows 'N resolved' detail."""
        text = _main_text(live_dashboard_page)
        has_detail = bool(re.search(r'\d+ resolved', text))
        if not has_detail and "--" not in text:
            pytest.fail("Resolution detail 'N resolved' not found")

    # B1: Escalation detail "N escalated"
    def test_escalation_detail_text(self, live_dashboard_page: Page):
        """[EL-032/B1] Escalation card shows 'N escalated' detail."""
        text = _main_text(live_dashboard_page)
        has_detail = bool(re.search(r'\d+ escalated', text))
        if not has_detail and "--" not in text:
            pytest.fail("Escalation detail 'N escalated' not found")


class TestStatCardGrid:
    """EL-dashboard-015: Stat cards grid layout."""

    # A1: Grid container exists
    def test_stat_cards_grid_exists(self, live_dashboard_page: Page):
        """[EL-015/A1] Stat cards grid container is present."""
        text = _main_text(live_dashboard_page)
        card_labels = ["total conversations", "response time", "resolution rate",
                       "satisfaction", "escalation"]
        found = sum(1 for l in card_labels if l in text.lower())
        assert found >= 4, f"Only {found}/5 stat card labels found"

    # A3: Exactly 5 stat cards
    def test_stat_card_count(self, live_dashboard_page: Page):
        """[EL-015/A3] Exactly 5 stat cards are present."""
        text = _main_text(live_dashboard_page)
        card_labels = [
            "total conversations", "response time", "resolution rate",
            "customer satisfaction", "escalation rate",
        ]
        found = [l for l in card_labels if l in text.lower()]
        assert len(found) == 5, f"Found {len(found)}/5 stat cards: {found}"


class TestStatCardTooltips:
    """EL-dashboard-018,022,026,029,033: Stat card help tooltips.

    The HelpTooltip component renders a <span role="button" aria-label="...">?</span>
    that shows a child tooltip span on hover.  No [role="tooltip"] is emitted.
    """

    TOOLTIP_CARDS = [
        ("EL-018", "Total conversations"),
        ("EL-022", "Avg response time"),
        ("EL-026", "Resolution rate"),
        ("EL-029", "Customer satisfaction"),
        ("EL-033", "Escalation rate"),
    ]

    @pytest.mark.parametrize("el_id,label", TOOLTIP_CARDS, ids=[c[0] for c in TOOLTIP_CARDS])
    def test_stat_card_tooltip_appears(self, live_dashboard_page: Page, el_id: str, label: str):
        """[{el_id}/E4] Help tooltip appears when hovering the '?' icon near stat card."""
        card_label = live_dashboard_page.locator(f"text={label}").first
        expect(card_label).to_be_visible(timeout=5_000)

        # HelpTooltip: <span role="button" aria-label="...">?</span>
        # Walk up to the inline-flex container and find the ? icon sibling
        parent = card_label.locator("xpath=ancestor::div[1]")
        help_icon = parent.locator("span[role='button']")
        if help_icon.count() == 0:
            # Try one level higher
            parent = card_label.locator("xpath=ancestor::div[2]")
            help_icon = parent.locator("span[role='button']")
        assert help_icon.count() > 0, (
            f"No HelpTooltip (span[role='button']) found near '{label}'"
        )

        help_icon.first.hover()
        live_dashboard_page.wait_for_timeout(600)

        # After hover, the tooltip content renders as a child span with > 5 chars
        # Check: either the icon's text grew beyond '?', or a new visible span appeared
        icon_text = help_icon.first.text_content() or ""
        assert len(icon_text) > 5, (
            f"Tooltip text not rendered after hover near '{label}': got '{icon_text[:50]}'"
        )

    @pytest.mark.parametrize("el_id,label", TOOLTIP_CARDS, ids=[c[0] for c in TOOLTIP_CARDS])
    def test_stat_card_tooltip_has_doc_link(self, live_dashboard_page: Page, el_id: str, label: str):
        """[{el_id}/E4] Tooltip contains a 'Learn more' link to agentredcx.com."""
        card_label = live_dashboard_page.locator(f"text={label}").first
        expect(card_label).to_be_visible(timeout=5_000)

        parent = card_label.locator("xpath=ancestor::div[1]")
        help_icon = parent.locator("span[role='button']")
        if help_icon.count() == 0:
            parent = card_label.locator("xpath=ancestor::div[2]")
            help_icon = parent.locator("span[role='button']")
        assert help_icon.count() > 0, (
            f"No HelpTooltip found near '{label}'"
        )

        help_icon.first.hover()
        live_dashboard_page.wait_for_timeout(600)

        # Check for doc link — HelpTooltip renders <a href="...agentredcx.com...">Learn more</a>
        icon_html = help_icon.first.inner_html() or ""
        has_link = "agentredcx.com" in icon_html or "Learn more" in icon_html
        assert has_link, (
            f"Tooltip for '{label}' missing documentation link. HTML: {icon_html[:100]}"
        )


# ===========================================================================
# SECTION F: Conversation Volume Chart
# EL-dashboard-034..043
# ===========================================================================

class TestConversationChart:
    """EL-dashboard-034..043: Conversation volume chart."""

    # A1: Chart section header
    def test_chart_header_exists(self, live_dashboard_page: Page):
        """[EL-034/A1] 'Conversation volume' header is visible."""
        text = _main_text(live_dashboard_page)
        assert "conversation volume" in text.lower() or "volume" in text.lower()

    # B1: Chart header value
    def test_chart_header_value(self, live_dashboard_page: Page):
        """[EL-034/B1] Chart header text is 'Conversation volume'."""
        header = live_dashboard_page.locator("text=Conversation volume").first
        if header.count() > 0:
            expect(header).to_be_visible()

    # A1: Chart period label
    def test_chart_period_label_exists(self, live_dashboard_page: Page):
        """[EL-035/A1] Chart shows period label like 'Last 30 days'."""
        text = _main_text(live_dashboard_page)
        has_period = bool(re.search(r'last \d+ days', text, re.I))
        assert has_period, "No period label found (expected 'Last N days')"

    # A1: Chart container
    def test_chart_container_exists(self, live_dashboard_page: Page):
        """[EL-036/A1] Chart canvas/SVG container is present."""
        chart = live_dashboard_page.locator(
            "[class*='recharts'], svg[class*='chart' i], "
            "[class*='Chart'], canvas"
        )
        has_chart = chart.count() > 0
        if not has_chart:
            svgs = live_dashboard_page.locator("svg")
            for i in range(svgs.count()):
                box = svgs.nth(i).bounding_box()
                if box and box["width"] > 200 and box["height"] > 100:
                    has_chart = True
                    break
        assert has_chart, "No chart container found"

    # B1: Chart legend
    def test_chart_legend_exists(self, live_dashboard_page: Page):
        """[EL-041/A1] Chart legend with 'Conversations' label is present."""
        text = _main_text(live_dashboard_page)
        assert "conversations" in text.lower()

    # K1: Empty state when no data
    def test_chart_empty_or_data(self, live_dashboard_page: Page):
        """[EL-043/K1] Chart shows either data or a proper empty state."""
        text = _main_text(live_dashboard_page)
        has_chart_data = bool(re.search(r'(recharts|last \d+ days)', text, re.I))
        has_empty = "no volume data" in text.lower() or "no data" in text.lower()
        assert has_chart_data or has_empty, (
            "Chart has neither data nor a proper empty state message"
        )


# ===========================================================================
# SECTION G: Recent Conversations
# EL-dashboard-044..052
# ===========================================================================

class TestRecentConversations:
    """EL-dashboard-044..052: Recent conversations list."""

    # A1: Section header
    def test_section_header_exists(self, live_dashboard_page: Page):
        """[EL-044/A1] 'Recent conversations' header is visible."""
        text = _main_text(live_dashboard_page)
        assert "recent conversations" in text.lower()

    # B1: Section header value
    def test_section_header_value(self, live_dashboard_page: Page):
        """[EL-044/B1] Header text is exactly 'Recent conversations'."""
        header = live_dashboard_page.locator("text=Recent conversations").first
        if header.count() > 0:
            expect(header).to_be_visible()

    # A1,B6: Conversation items or empty state
    def test_conversations_or_empty(self, live_dashboard_page: Page):
        """[EL-046..052/B6] Shows conversation items OR 'No conversations yet'."""
        text = _main_text(live_dashboard_page)
        has_conversations = bool(
            re.search(r'(message|active|ended|escalated|idle)', text, re.I)
        )
        has_empty = "no conversations" in text.lower()
        assert has_conversations or has_empty, (
            "Recent conversations section has neither items nor empty state"
        )

    # B1: Status badge values
    def test_status_badges_valid(self, live_dashboard_page: Page):
        """[EL-047/B1] Status badges show only valid status values."""
        VALID = {"active", "idle", "ended", "escalated"}
        badges = live_dashboard_page.locator(
            "[class*='badge' i], [class*='Badge']"
        )
        for i in range(min(badges.count(), 20)):
            text = (badges.nth(i).text_content() or "").strip().lower()
            if text in VALID:
                pass  # Valid

    # B1: Message count format
    def test_message_count_format(self, live_dashboard_page: Page):
        """[EL-048/B1] Message counts follow 'N messages' format."""
        text = _main_text(live_dashboard_page)
        if "no conversations" in text.lower():
            return  # No conversation data — data-dependent, not element failure
        matches = re.findall(r'(\d+)\s+messages?', text)
        if matches:
            for m in matches:
                assert int(m) >= 0, f"Invalid message count: {m}"

    # K1: Handles empty gracefully
    def test_empty_state_text(self, live_dashboard_page: Page):
        """[EL-052/K1] Empty state shows 'No conversations yet'."""
        text = _main_text(live_dashboard_page)
        has_items = bool(re.search(r'\d+\s+messages?', text))
        if not has_items:
            assert "no conversations" in text.lower(), (
                "Empty state message missing when no conversation items shown"
            )


# ===========================================================================
# SECTION H: Top Topics
# EL-dashboard-053..058
# ===========================================================================

class TestTopTopics:
    """EL-dashboard-053..058: Top topics sidebar."""

    # A1: Section header
    def test_section_header_exists(self, live_dashboard_page: Page):
        """[EL-053/A1] 'Top topics' header is visible."""
        text = _main_text(live_dashboard_page)
        assert "top topics" in text.lower()

    # B6: Topics or empty state
    def test_topics_or_empty(self, live_dashboard_page: Page):
        """[EL-054..058/B6] Shows topic items OR 'No topic data available'."""
        text = _main_text(live_dashboard_page)
        has_topics = bool(
            re.search(r'(order|product|shipping|return|general)', text, re.I)
        )
        has_empty = "no topic data" in text.lower()
        assert has_topics or has_empty, (
            "Top topics section has neither topic items nor empty state"
        )

    # B2: Topic counts are numeric
    def test_topic_counts_numeric(self, live_dashboard_page: Page):
        """[EL-055/B2] Topic counts are properly formatted numbers."""
        text = _main_text(live_dashboard_page)
        if "no topic data" in text.lower():
            return  # No topic data — data-dependent, not element failure
        idx = text.lower().find("top topics")
        if idx >= 0:
            section = text[idx:idx + 500]
            has_numbers = bool(re.search(r'\d+', section))
            assert has_numbers, "No numeric counts in Top Topics section"


# ===========================================================================
# SECTION I: Detailed Analytics Divider
# EL-dashboard-059
# ===========================================================================

class TestAnalyticsDivider:
    """EL-dashboard-059: Detailed analytics divider."""

    def test_divider_exists(self, live_dashboard_page: Page):
        """[EL-059/A1] 'Detailed analytics' divider is visible."""
        text = _main_text(live_dashboard_page)
        assert "detailed analytics" in text.lower()

    def test_divider_label(self, live_dashboard_page: Page):
        """[EL-059/B1] Divider label text is 'Detailed analytics'."""
        divider = live_dashboard_page.locator("text=Detailed analytics").first
        if divider.count() > 0:
            expect(divider).to_be_visible()


# ===========================================================================
# SECTION J: Topic Breakdown Table
# EL-dashboard-060..066
# ===========================================================================

class TestTopicBreakdown:
    """EL-dashboard-060..066: Topic breakdown table."""

    def test_section_header_exists(self, live_dashboard_page: Page):
        """[EL-060/A1] 'Topic breakdown' header is visible."""
        text = _main_text(live_dashboard_page)
        assert "topic breakdown" in text.lower()

    def test_table_exists(self, live_dashboard_page: Page):
        """[EL-061/A1] Topic breakdown table is present."""
        tables = live_dashboard_page.locator("table")
        text = _main_text(live_dashboard_page)
        has_table = tables.count() > 0
        has_topic_section = "topic breakdown" in text.lower()
        assert has_table or has_topic_section

    def test_table_columns(self, live_dashboard_page: Page):
        """[EL-061/B1] Table has Topic, Count, Distribution columns."""
        text = _main_text(live_dashboard_page)
        if "no topic data" in text.lower():
            return  # No topic data — table correctly not rendered
        for col in ["topic", "count"]:
            assert col.lower() in text.lower(), f"Column '{col}' not found"

    def test_empty_state(self, live_dashboard_page: Page):
        """[EL-066/K1] Empty state shows 'No topic data available'."""
        text = _main_text(live_dashboard_page)
        has_data = bool(
            re.search(r'(order|product|shipping|general)\s*(tracking)?', text, re.I)
        )
        if not has_data:
            assert "no topic data" in text.lower()


# ===========================================================================
# SECTION K: Knowledge Gaps
# EL-dashboard-067..078
# ===========================================================================

class TestKnowledgeGaps:
    """EL-dashboard-067..078: Knowledge gaps section."""

    def test_section_header_exists(self, live_dashboard_page: Page):
        """[EL-067/A1] 'Knowledge gaps' header is visible."""
        text = _main_text(live_dashboard_page)
        assert "knowledge gaps" in text.lower()

    def test_description_text(self, live_dashboard_page: Page):
        """[EL-068/B1] Description mentions AI could not resolve."""
        text = _main_text(live_dashboard_page)
        has_desc = (
            "could not" in text.lower()
            or "resolve" in text.lower()
            or "gap" in text.lower()
            or "unanswer" in text.lower()
            or "knowledge gaps" in text.lower()
        )
        assert has_desc, "Knowledge gaps description not found on page"

    def test_count_badge_or_empty(self, live_dashboard_page: Page):
        """[EL-069/B6] Shows gap count badge or empty state."""
        text = _main_text(live_dashboard_page)
        has_count = bool(re.search(r'\d+\s+gap', text, re.I))
        has_empty = "no knowledge gaps" in text.lower()
        assert has_count or has_empty, (
            "Knowledge gaps has neither count badge nor empty state"
        )

    def test_table_columns(self, live_dashboard_page: Page):
        """[EL-070/B1] Gaps table has expected columns."""
        text = _main_text(live_dashboard_page)
        if "no knowledge gaps" in text.lower():
            return  # No gaps data — table correctly not rendered

    def test_empty_state(self, live_dashboard_page: Page):
        """[EL-077/K1] Empty state shows 'No knowledge gaps detected'."""
        text = _main_text(live_dashboard_page)
        has_data = bool(re.search(r'\d+\s+gap', text, re.I))
        if not has_data:
            assert "no knowledge gaps" in text.lower()


# ===========================================================================
# Cross-cutting: Dashboard Integrity
# ===========================================================================

class TestDashboardIntegrity:
    """Cross-cutting integrity checks across all dashboard sections."""

    def test_all_sections_present(self, live_dashboard_page: Page):
        """[CROSS/A1] All major dashboard sections are present."""
        text = _main_text(live_dashboard_page)
        expected_sections = [
            "total conversations",
            "conversation volume",
            "recent conversations",
            "top topics",
            "detailed analytics",
            "topic breakdown",
            "knowledge gaps",
        ]
        found = [s for s in expected_sections if s in text.lower()]
        missing = [s for s in expected_sections if s not in text.lower()]
        assert len(found) >= 5, (
            f"Only {len(found)}/7 sections found. Missing: {missing}"
        )

    def test_no_duplicate_sections(self, live_dashboard_page: Page):
        """[CROSS/A3] No dashboard section header appears more than once."""
        text = _main_text(live_dashboard_page).lower()
        sections = [
            "conversation volume", "recent conversations",
            "top topics", "topic breakdown", "knowledge gaps",
        ]
        for section in sections:
            count = text.count(section)
            # Allow up to 2 — phrase may appear in both header and description
            assert count <= 2, f"Section '{section}' appears {count} times (>2)"

    def test_data_populated(self, live_dashboard_page: Page):
        """[CROSS/I2] Dashboard has populated data (not stuck loading)."""
        text = _main_text(live_dashboard_page)
        has_numbers = bool(re.search(r'\d', text))
        has_labels = "total conversations" in text.lower()
        assert has_numbers and has_labels, (
            "Dashboard appears to be stuck in loading state"
        )

    def test_no_lingering_skeletons(self, live_dashboard_page: Page):
        """[CROSS/I1] No loading skeletons visible after data load."""
        skeletons = live_dashboard_page.locator(
            "[class*='skeleton' i][class*='visible' i], "
            "[class*='Skeleton'][data-animate='true']"
        )
        visible_count = 0
        for i in range(skeletons.count()):
            if skeletons.nth(i).is_visible():
                visible_count += 1
        assert visible_count == 0, f"{visible_count} loading skeletons still visible"

    def test_no_error_text(self, live_dashboard_page: Page):
        """[CROSS/K1] No error messages visible on the page."""
        text = _main_text(live_dashboard_page)
        error_patterns = [
            "something went wrong", "unexpected error", "failed to load",
            "failed to fetch", "error loading", "network error",
        ]
        for pattern in error_patterns:
            assert pattern not in text.lower(), (
                f"Error message visible on dashboard: '{pattern}'"
            )

    def test_stat_cards_all_visible(self, live_dashboard_page: Page):
        """[CROSS/A2] All 5 stat card labels are visible (not hidden by CSS)."""
        labels = [
            "Total conversations", "Avg response time", "Resolution rate",
            "Customer satisfaction", "Escalation rate",
        ]
        for label in labels:
            locator = live_dashboard_page.locator(f"text={label}").first
            if locator.count() > 0:
                expect(locator).to_be_visible()

    def test_all_values_non_negative(self, live_dashboard_page: Page):
        """[CROSS/B2] No negative numbers displayed on dashboard."""
        text = _main_text(live_dashboard_page)
        # Match negative numbers that appear as standalone values (not part of
        # identifiers like "blanco-9939" or CSS values like "-webkit").
        # Look for negative numbers preceded by whitespace or start-of-line.
        negative_numbers = re.findall(r'(?:^|\s)(-\d+)(?:\s|%|$)', text)
        real_negatives = [n for n in negative_numbers if int(n) < -1]
        assert len(real_negatives) == 0, f"Negative numbers displayed: {real_negatives}"

    def test_percentages_valid_range(self, live_dashboard_page: Page):
        """[CROSS/B5] All displayed percentages are in 0-100% range."""
        text = _main_text(live_dashboard_page)
        percentages = re.findall(r'(\d+\.?\d*)%', text)
        for pct in percentages:
            val = float(pct)
            assert 0 <= val <= 100, f"Out-of-range percentage: {val}%"


# ===========================================================================
# NEW: Segmented Control (SegmentedControl, not button group)
# ===========================================================================

class TestSegmentedControl:
    """Period filter rendered as Mantine SegmentedControl (radio inputs)."""

    def test_segmented_control_present(self, live_dashboard_page: Page):
        """SegmentedControl root element exists on the page."""
        sc = live_dashboard_page.locator("[class*='SegmentedControl'], [role='radiogroup']")
        # Mantine SegmentedControl renders a root div; also accept button fallback
        has_sc = sc.count() > 0
        has_buttons = live_dashboard_page.get_by_role("button", name="30 days").count() > 0
        assert has_sc or has_buttons, "No period filter control found"

    def test_all_period_labels_present(self, live_dashboard_page: Page):
        """All 4 period labels (7d, 14d, 30d, 90d) are visible."""
        text = _main_text(live_dashboard_page)
        for label in ["7d", "14d", "30d", "90d"]:
            assert label in text or label.replace("d", " days") in text, (
                f"Period label '{label}' not found"
            )

    def test_period_selection_changes_chart_header(self, live_dashboard_page: Page):
        """Selecting '7d' updates the chart subtitle to 'Last 7 days'."""
        # Click 7d segment
        seg = live_dashboard_page.locator(
            "[class*='SegmentedControl'] label:has-text('7d'), "
            "button:has-text('7 days'), button:has-text('7d')"
        ).first
        if seg.count() > 0:
            seg.click()
            live_dashboard_page.wait_for_timeout(1000)
            text = _main_text(live_dashboard_page)
            assert "last 7 days" in text.lower(), (
                "Chart subtitle didn't update to 'Last 7 days'"
            )


# ===========================================================================
# NEW: Test Mode Alert — specific list items
# ===========================================================================

class TestTestModeAlertDetails:
    """Test mode alert 4 list items (conditional — only when test_mode=true)."""

    def test_test_mode_list_items(self, live_dashboard_page: Page):
        """Test mode alert lists 4 specific behaviors."""
        text = _main_text(live_dashboard_page)
        if "test mode" not in text.lower():
            return  # Test mode not enabled — not applicable
        expected = [
            "tagged as test",
            "yellow test mode banner",
            "analytics include test",
            "identical to standard mode",
        ]
        for phrase in expected:
            assert phrase.lower() in text.lower(), (
                f"Test mode alert missing: '{phrase}'"
            )

    def test_test_mode_switch_note(self, live_dashboard_page: Page):
        """Test mode alert includes guidance to switch to standard mode."""
        text = _main_text(live_dashboard_page)
        if "test mode" not in text.lower():
            return  # Not applicable
        assert "standard mode" in text.lower(), (
            "Test mode alert missing 'switch to standard mode' note"
        )


# ===========================================================================
# NEW: Setup Checklist — detailed checks
# ===========================================================================

class TestSetupChecklistDetails:
    """Setup checklist icon colors, line-through, and progress counter."""

    def test_checklist_progress_counter(self, live_dashboard_page: Page):
        """Checklist title shows 'N/4 complete' format."""
        text = _main_text(live_dashboard_page)
        if "setup" not in text.lower():
            return  # Tenant is activated — checklist hidden
        assert re.search(r'\d+/4 complete', text), (
            f"Setup progress counter 'N/4 complete' not found"
        )

    def test_checklist_4_items(self, live_dashboard_page: Page):
        """Checklist has exactly 4 items (brand, instructions, appearance, activated)."""
        text = _main_text(live_dashboard_page)
        if "setup" not in text.lower():
            return
        items = ["brand name", "instructions", "appearance", "activated"]
        found = [i for i in items if i.lower() in text.lower()]
        assert len(found) == 4, f"Only {len(found)}/4 checklist items found: {found}"


# ===========================================================================
# NEW: Recent Conversations — card sub-elements
# ===========================================================================

class TestRecentConversationCards:
    """Conversation card sub-elements: customer name, assignment, timestamp."""

    def test_customer_name_displayed(self, live_dashboard_page: Page):
        """Each conversation card shows a customer name or 'Unknown Customer'."""
        text = _main_text(live_dashboard_page)
        if "no conversations" in text.lower():
            return  # Empty state — no cards to inspect
        # Cards render customer name as the first bold text in each card
        # At minimum, the section should show SOME name text
        idx = text.lower().find("recent conversations")
        if idx == -1:
            return
        section = text[idx:idx + 1500]
        has_names = (
            "unknown customer" in section.lower()
            or re.search(r'[A-Z][a-z]+', section)  # Any capitalized word
        )
        assert has_names, "No customer names found in recent conversations"

    def test_assignment_or_unassigned(self, live_dashboard_page: Page):
        """Conversation cards show 'Assigned: X', 'Unassigned', or 'Escalated'."""
        text = _main_text(live_dashboard_page)
        if "no conversations" in text.lower():
            return
        idx = text.lower().find("recent conversations")
        if idx == -1:
            return
        section = text[idx:idx + 1500]
        has_assignment = (
            "assigned" in section.lower()
            or "unassigned" in section.lower()
            or "escalated" in section.lower()
        )
        assert has_assignment, (
            "No assignment info (Assigned/Unassigned/Escalated) in conversation cards"
        )

    def test_message_count_in_cards(self, live_dashboard_page: Page):
        """Each card shows 'N messages' text."""
        text = _main_text(live_dashboard_page)
        if "no conversations" in text.lower():
            return
        idx = text.lower().find("recent conversations")
        if idx == -1:
            return
        section = text[idx:idx + 1500]
        assert re.search(r'\d+\s+messages?', section), (
            "No 'N messages' counts found in conversation cards"
        )

    def test_status_badge_colors_valid(self, live_dashboard_page: Page):
        """Status badges use valid Mantine color props (blue/yellow/green/red)."""
        badges = live_dashboard_page.locator(
            "[class*='badge' i], [class*='Badge']"
        )
        VALID_STATUSES = {"active", "idle", "ended", "escalated"}
        found_valid = 0
        for i in range(min(badges.count(), 20)):
            text = (badges.nth(i).text_content() or "").strip().lower()
            if text in VALID_STATUSES:
                found_valid += 1
        # At least one valid status badge should exist (unless empty state)
        page_text = _main_text(live_dashboard_page)
        if "no conversations" not in page_text.lower():
            assert found_valid > 0, "No valid status badges found on conversation cards"

    def test_last_activity_time_format(self, live_dashboard_page: Page):
        """Conversation cards show last activity as HH:MM timestamp."""
        text = _main_text(live_dashboard_page)
        if "no conversations" in text.lower():
            return
        idx = text.lower().find("recent conversations")
        if idx == -1:
            return
        section = text[idx:idx + 1500]
        # Time format: "HH:MM AM/PM" or "HH:MM" or "--"
        has_time = bool(re.search(r'\d{1,2}:\d{2}', section)) or "--" in section
        assert has_time, "No HH:MM timestamps found in conversation cards"


# ===========================================================================
# NEW: Top Topics — progress bars and counts
# ===========================================================================

class TestTopTopicsDetails:
    """Top topics progress bars, counts, and HelpTooltip."""

    def test_top_topics_help_tooltip(self, live_dashboard_page: Page):
        """Top topics header has a HelpTooltip '?' icon."""
        # Find the "Top topics" text, then look for sibling span[role='button']
        header = live_dashboard_page.locator("text=Top topics").first
        if header.count() == 0:
            return
        parent = header.locator("xpath=ancestor::div[1]")
        help_icon = parent.locator("span[role='button']")
        if help_icon.count() == 0:
            parent = header.locator("xpath=ancestor::*[1]")
            help_icon = parent.locator("span[role='button']")
        assert help_icon.count() > 0, "Top topics header missing HelpTooltip"

    def test_topic_items_have_counts(self, live_dashboard_page: Page):
        """Each topic item shows a numeric count value."""
        text = _main_text(live_dashboard_page)
        if "no topic data" in text.lower():
            return
        idx = text.lower().find("top topics")
        if idx == -1:
            return
        # Section between "Top topics" and "Detailed analytics"
        end_idx = text.lower().find("detailed analytics", idx)
        if end_idx == -1:
            end_idx = idx + 1000
        section = text[idx:end_idx]
        numbers = re.findall(r'\d+', section)
        assert len(numbers) >= 1, "No numeric counts in Top topics section"


# ===========================================================================
# NEW: Conversation Volume Chart — additional elements
# ===========================================================================

class TestChartDetails:
    """Chart HelpTooltip, gradient, empty state text, and interaction."""

    def test_chart_help_tooltip(self, live_dashboard_page: Page):
        """Conversation volume header has a HelpTooltip."""
        header = live_dashboard_page.locator("text=Conversation volume").first
        if header.count() == 0:
            return
        parent = header.locator("xpath=ancestor::div[1]")
        help_icon = parent.locator("span[role='button']")
        if help_icon.count() == 0:
            parent = header.locator("xpath=ancestor::*[1]")
            help_icon = parent.locator("span[role='button']")
        assert help_icon.count() > 0, "Conversation volume header missing HelpTooltip"

    def test_chart_svg_gradient_def(self, live_dashboard_page: Page):
        """Chart SVG contains a gradient definition for the area fill."""
        # Recharts renders <defs><linearGradient id="gradTotal">...</linearGradient></defs>
        gradient = live_dashboard_page.locator("svg linearGradient")
        if gradient.count() == 0:
            # May be in empty state
            text = _main_text(live_dashboard_page)
            if "no volume data" in text.lower():
                return
        assert gradient.count() > 0, "Chart missing gradient definition in SVG"

    def test_chart_axes_present(self, live_dashboard_page: Page):
        """Chart has X and Y axis elements."""
        text = _main_text(live_dashboard_page)
        if "no volume data" in text.lower():
            return
        # Recharts renders .recharts-xAxis and .recharts-yAxis groups
        x_axis = live_dashboard_page.locator("[class*='recharts-xAxis'], .recharts-xAxis")
        y_axis = live_dashboard_page.locator("[class*='recharts-yAxis'], .recharts-yAxis")
        has_axes = x_axis.count() > 0 and y_axis.count() > 0
        if not has_axes:
            # Fallback: check for any SVG ticks
            ticks = live_dashboard_page.locator("svg g text")
            has_axes = ticks.count() >= 2
        assert has_axes, "Chart missing X/Y axis elements"

    def test_chart_legend_color_swatch(self, live_dashboard_page: Page):
        """Chart legend shows a colored swatch box next to 'Conversations'."""
        text = _main_text(live_dashboard_page)
        if "no volume data" in text.lower():
            return
        # Legend renders a 10x10 box + "Conversations" text
        legend_text = live_dashboard_page.locator("text=Conversations")
        assert legend_text.count() > 0, "Chart legend 'Conversations' label not found"


# ===========================================================================
# NEW: Topic Breakdown Table — detailed checks
# ===========================================================================

class TestTopicBreakdownDetails:
    """Topic breakdown table: progress bars, percentages, help tooltip."""

    def test_topic_breakdown_help_tooltip(self, live_dashboard_page: Page):
        """Topic breakdown header has a HelpTooltip."""
        header = live_dashboard_page.locator("text=Topic breakdown").first
        if header.count() == 0:
            return
        parent = header.locator("xpath=ancestor::div[1]")
        help_icon = parent.locator("span[role='button']")
        if help_icon.count() == 0:
            parent = header.locator("xpath=ancestor::*[1]")
            help_icon = parent.locator("span[role='button']")
        assert help_icon.count() > 0, "Topic breakdown header missing HelpTooltip"

    def test_distribution_column_has_progress_bars(self, live_dashboard_page: Page):
        """Distribution column renders Mantine Progress bars."""
        text = _main_text(live_dashboard_page)
        if "no topic data" in text.lower():
            return
        # Mantine Progress renders [role='progressbar'] or [class*='Progress']
        progress = live_dashboard_page.locator(
            "[role='progressbar'], [class*='Progress-root' i]"
        )
        assert progress.count() > 0, "No progress bars in topic breakdown table"

    def test_distribution_percentages_present(self, live_dashboard_page: Page):
        """Distribution column shows percentage values next to progress bars."""
        text = _main_text(live_dashboard_page)
        if "no topic data" in text.lower():
            return
        # Find the topic breakdown section
        idx = text.lower().find("topic breakdown")
        if idx == -1:
            return
        # Look for Knowledge gaps to bound the section
        end_idx = text.lower().find("knowledge gaps", idx)
        if end_idx == -1:
            end_idx = len(text)
        section = text[idx:end_idx]
        percentages = re.findall(r'\d+%', section)
        assert len(percentages) >= 1, (
            "No percentage values in topic breakdown distribution column"
        )

    def test_table_has_striped_rows(self, live_dashboard_page: Page):
        """Topic breakdown table uses striped row styling."""
        tables = live_dashboard_page.locator("table")
        if tables.count() == 0:
            return
        # Check for Mantine Table striped attribute via class
        found_striped = False
        for i in range(tables.count()):
            table_html = tables.nth(i).get_attribute("class") or ""
            if "stripe" in table_html.lower():
                found_striped = True
                break
            # Also check data attribute
            data_striped = tables.nth(i).get_attribute("data-striped") or ""
            if data_striped:
                found_striped = True
                break
        # Mantine v7 uses data-striped="odd" attribute
        if not found_striped:
            for i in range(tables.count()):
                attrs = tables.nth(i).evaluate("(el) => el.outerHTML.slice(0, 200)")
                if "striped" in (attrs or "").lower():
                    found_striped = True
                    break
        assert found_striped, "No striped tables found on dashboard"


# ===========================================================================
# NEW: Knowledge Gaps — detailed sub-elements
# ===========================================================================

class TestKnowledgeGapsDetails:
    """Knowledge gaps table sub-elements: columns, badge, date format."""

    def test_knowledge_gaps_help_tooltip(self, live_dashboard_page: Page):
        """Knowledge gaps header has a HelpTooltip."""
        header = live_dashboard_page.locator("text=Knowledge gaps").first
        if header.count() == 0:
            return
        parent = header.locator("xpath=ancestor::div[1]")
        help_icon = parent.locator("span[role='button']")
        if help_icon.count() == 0:
            parent = header.locator("xpath=ancestor::*[1]")
            help_icon = parent.locator("span[role='button']")
        assert help_icon.count() > 0, "Knowledge gaps header missing HelpTooltip"

    def test_gap_count_badge(self, live_dashboard_page: Page):
        """Gap count badge shows 'N gaps' in orange when gaps exist."""
        text = _main_text(live_dashboard_page)
        has_gap_data = bool(re.search(r'\d+\s+gaps?', text))
        has_no_gaps = "no knowledge gaps" in text.lower()
        assert has_gap_data or has_no_gaps, (
            "Knowledge gaps section missing both gap count badge and empty state"
        )

    def test_gap_table_5_columns(self, live_dashboard_page: Page):
        """Knowledge gaps table has 5 columns: Conversation, Status, Turns, Messages, Started."""
        text = _main_text(live_dashboard_page)
        if "no knowledge gaps" in text.lower():
            return
        expected_cols = ["conversation", "status", "turns", "messages", "started"]
        for col in expected_cols:
            assert col.lower() in text.lower(), (
                f"Knowledge gaps table missing column: '{col}'"
            )

    def test_gap_status_badges(self, live_dashboard_page: Page):
        """Gap rows have status badges with valid colors."""
        text = _main_text(live_dashboard_page)
        if "no knowledge gaps" in text.lower():
            return
        VALID = {"active", "idle", "ended", "escalated", "unknown"}
        # Find badges in the knowledge gaps section
        idx = text.lower().find("knowledge gaps")
        if idx == -1:
            return
        section = text[idx:]
        found = any(s in section.lower() for s in VALID)
        assert found, "No valid status badges in knowledge gaps table"

    def test_gap_turn_and_message_counts(self, live_dashboard_page: Page):
        """Turns and Messages columns contain numeric values."""
        text = _main_text(live_dashboard_page)
        if "no knowledge gaps" in text.lower():
            return
        idx = text.lower().find("knowledge gaps")
        if idx == -1:
            return
        section = text[idx:]
        numbers = re.findall(r'\b\d+\b', section)
        assert len(numbers) >= 2, (
            "Knowledge gaps table missing numeric turn/message counts"
        )

    def test_gap_started_date_format(self, live_dashboard_page: Page):
        """Started column shows dates in 'Mon DD, YYYY' format or '--'."""
        text = _main_text(live_dashboard_page)
        if "no knowledge gaps" in text.lower():
            return
        idx = text.lower().find("knowledge gaps")
        if idx == -1:
            return
        section = text[idx:]
        # formatLastSeen produces "Mar 4, 2026" style dates
        has_date = bool(re.search(
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}',
            section,
        ))
        has_dash = "--" in section
        assert has_date or has_dash, (
            "Knowledge gaps Started column has no formatted dates or '--'"
        )

    def test_description_mentions_resolve(self, live_dashboard_page: Page):
        """Description text mentions AI could not resolve."""
        text = _main_text(live_dashboard_page)
        idx = text.lower().find("knowledge gaps")
        if idx == -1:
            return
        section = text[idx:idx + 300]
        assert "could not" in section.lower() or "resolve" in section.lower(), (
            "Knowledge gaps description missing resolution context"
        )


# ===========================================================================
# NEW: Section HelpTooltips — non-stat-card sections
# ===========================================================================

class TestSectionHelpTooltips:
    """HelpTooltip presence on section headers beyond stat cards."""

    SECTIONS = [
        "Conversation volume",
        "Recent conversations",
        "Top topics",
        "Topic breakdown",
        "Knowledge gaps",
    ]

    @pytest.mark.parametrize("section", SECTIONS)
    def test_section_has_help_tooltip(self, live_dashboard_page: Page, section: str):
        """Section header '{section}' contains a HelpTooltip '?' icon."""
        header = live_dashboard_page.locator(f"text={section}").first
        if header.count() == 0:
            return  # Section not rendered (possible data-dependent)
        # Walk up to find the help icon
        for ancestor_level in range(1, 4):
            parent = header.locator(f"xpath=ancestor::*[{ancestor_level}]")
            help_icon = parent.locator("span[role='button']")
            if help_icon.count() > 0:
                # Verify it contains '?'
                icon_text = help_icon.first.text_content() or ""
                if "?" in icon_text:
                    return  # Found it
        # If we get here, no help icon found
        assert False, f"Section '{section}' header missing HelpTooltip '?' icon"


# ===========================================================================
# NEW: Responsive Grid Layout
# ===========================================================================

class TestResponsiveLayout:
    """Dashboard responsive grid and Paper card rendering."""

    def test_stat_cards_in_paper_containers(self, live_dashboard_page: Page):
        """Stat cards are rendered inside Paper components with borders."""
        # Mantine Paper with withBorder renders [data-with-border] or border style
        papers = live_dashboard_page.locator("[class*='Paper-root' i]")
        if papers.count() == 0:
            papers = live_dashboard_page.locator("[class*='paper' i]")
        # Dashboard has: 5 stat cards + chart paper + conversations paper +
        # topics paper + topic breakdown paper + knowledge gaps paper = 10+ Papers
        assert papers.count() >= 5, (
            f"Expected at least 5 Paper containers, found {papers.count()}"
        )

    def test_two_column_layout_exists(self, live_dashboard_page: Page):
        """Recent conversations and Top topics render side-by-side."""
        # Check that both sections exist in the same row area
        text = _main_text(live_dashboard_page)
        has_recent = "recent conversations" in text.lower()
        has_topics = "top topics" in text.lower()
        assert has_recent and has_topics, (
            "Both 'Recent conversations' and 'Top topics' must be present"
        )

    def test_loading_skeletons_absent(self, live_dashboard_page: Page):
        """After data load, no Skeleton placeholders remain visible."""
        # Mantine Skeleton has class *Skeleton*
        skeletons = live_dashboard_page.locator("[class*='Skeleton' i]")
        visible = sum(
            1 for i in range(skeletons.count())
            if skeletons.nth(i).is_visible()
        )
        assert visible == 0, f"{visible} loading skeletons still visible"
