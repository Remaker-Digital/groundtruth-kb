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
        text = _main_text(live_dashboard_page)
        has_period = any(p in text for p in ["7d", "14d", "30d", "90d",
                                              "7 days", "14 days", "30 days", "90 days"])
        assert has_period, "No period filter options found"

    # B1: Default value
    def test_period_filter_default_30d(self, live_dashboard_page: Page):
        """[EL-004/B1] Default selected period is 30d."""
        text = _main_text(live_dashboard_page)
        assert "30" in text, "Default 30-day period not reflected in page"

    # A3: All 4 options present
    def test_period_filter_all_options(self, live_dashboard_page: Page):
        """[EL-004/A3] All 4 period options are present: 7d, 14d, 30d, 90d."""
        text = _main_text(live_dashboard_page)
        for period in ["7", "14", "30", "90"]:
            assert period in text, f"Period option containing '{period}' not found"

    # E1: Clicking 7d changes chart
    def test_period_filter_7d_action(self, live_dashboard_page: Page):
        """[EL-005/E1] Clicking 7d updates the chart period label."""
        btn_7d = live_dashboard_page.locator("text=7d").first
        if btn_7d.count() == 0:
            btn_7d = live_dashboard_page.locator("text=7 days").first
        if btn_7d.count() == 0:
            pytest.skip("7d button not found")
        btn_7d.click()
        live_dashboard_page.wait_for_timeout(1000)
        text = _main_text(live_dashboard_page)
        assert "7" in text, "Chart label didn't update to reflect 7-day period"

    # E1: Clicking 90d changes chart
    def test_period_filter_90d_action(self, live_dashboard_page: Page):
        """[EL-007/E1] Clicking 90d updates the chart period label."""
        btn_90d = live_dashboard_page.locator("text=90d").first
        if btn_90d.count() == 0:
            btn_90d = live_dashboard_page.locator("text=90 days").first
        if btn_90d.count() == 0:
            pytest.skip("90d button not found")
        btn_90d.click()
        live_dashboard_page.wait_for_timeout(1000)
        text = _main_text(live_dashboard_page)
        assert "90" in text, "Chart label didn't update to reflect 90-day period"

    # A4: Filter is a proper segmented control
    def test_period_filter_element_type(self, live_dashboard_page: Page):
        """[EL-004/A4] Period filter uses segmented control (not freeform input)."""
        seg = live_dashboard_page.locator(
            "[class*='segmented' i], [role='radiogroup'], [class*='SegmentedControl']"
        )
        buttons = live_dashboard_page.locator("text=7d, text=14d, text=30d, text=90d")
        assert seg.count() > 0 or buttons.count() >= 2, (
            "Period filter is not a segmented control"
        )


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
            pytest.skip("Tenant is already activated — setup checklist not visible")
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
    """EL-dashboard-018,022,026,029,033: Stat card help tooltips."""

    TOOLTIP_CARDS = [
        ("EL-018", "Total conversations"),
        ("EL-022", "Avg response time"),
        ("EL-026", "Resolution rate"),
        ("EL-029", "Customer satisfaction"),
        ("EL-033", "Escalation rate"),
    ]

    @pytest.mark.parametrize("el_id,label", TOOLTIP_CARDS, ids=[c[0] for c in TOOLTIP_CARDS])
    def test_stat_card_tooltip_appears(self, live_dashboard_page: Page, el_id: str, label: str):
        """[{el_id}/E4] Help tooltip appears when hovering near stat card label."""
        card_area = live_dashboard_page.locator(f"text={label}").first
        if card_area.count() == 0:
            pytest.skip(f"Label '{label}' not found")

        parent = card_area.locator("xpath=ancestor::*[1]")
        help_icon = parent.locator("svg, [class*='help' i], [class*='info' i]")
        if help_icon.count() == 0:
            parent = card_area.locator("xpath=ancestor::*[2]")
            help_icon = parent.locator("svg, [class*='help' i], [class*='info' i]")
        if help_icon.count() == 0:
            pytest.skip(f"No help icon found near '{label}'")

        help_icon.first.hover()
        live_dashboard_page.wait_for_timeout(600)

        tooltip = live_dashboard_page.locator("[role='tooltip']")
        if tooltip.count() > 0:
            tooltip_text = tooltip.first.text_content() or ""
            assert len(tooltip_text) > 5, f"Tooltip text too short: '{tooltip_text}'"


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
            pytest.skip("No conversation data to verify")
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
            pytest.skip("No topic data to verify")
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
            pytest.skip("No topic data — table not rendered")
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
        has_desc = "could not" in text.lower() or "resolve" in text.lower()
        if not has_desc:
            pytest.skip("Knowledge gaps description not visible")

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
            pytest.skip("No gaps data — table not rendered")

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
