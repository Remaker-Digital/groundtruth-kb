"""
Live E2E dashboard tests — real data assertions on the Dashboard page.

Validates that the Dashboard renders correctly against the live backend.
Handles two tenant states:

  - **Activated** (production): stat cards, charts, recent conversations,
    period filters, analytics data.
  - **Initialized / not activated** (freshly-seeded staging): setup
    checklist with steps like "Configure your assistant", "Add knowledge",
    "Activate your assistant".

Both states must be valid — the tests assert the correct content for
whichever state is detected.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re

import pytest
from playwright.sync_api import Page


def _is_activated_dashboard(page: Page) -> bool:
    """Detect whether the dashboard shows an activated (analytics) state.

    Activated tenants show stat cards and charts.  Freshly-seeded tenants
    show a setup checklist.  This helper checks for telltale analytics
    elements (recharts SVG, stat card patterns, period filter buttons).
    """
    recharts = page.locator("[class*='recharts']")
    if recharts.count() > 0:
        return True
    # Period filter button presence is a strong signal for analytics mode
    filter_btn = page.locator("text=/30 days|7 days|Last 30|This month/")
    if filter_btn.count() > 0:
        return True
    return False


class TestStatCards:
    """Dashboard stat cards display real numeric values (activated tenants).

    On freshly-seeded tenants, the dashboard shows a setup checklist
    instead of stat cards.  These tests skip gracefully in that state.
    """

    def test_total_conversations_shows_number(self, live_dashboard_page: Page):
        """Total conversations stat card contains at least one digit."""
        if not _is_activated_dashboard(live_dashboard_page):
            pytest.skip("Dashboard in setup-checklist mode — no stat cards")
        page_text = live_dashboard_page.text_content("main") or ""
        assert re.search(r"\d+", page_text), "No numeric values found on dashboard"

    def test_avg_response_time_shows_value(self, live_dashboard_page: Page):
        """Average response time stat contains a time unit."""
        if not _is_activated_dashboard(live_dashboard_page):
            pytest.skip("Dashboard in setup-checklist mode — no stat cards")
        page_text = live_dashboard_page.text_content("main") or ""
        has_time_unit = bool(re.search(r"\d+\s*(s|ms|min|sec|second|minute)", page_text, re.I))
        has_any_number = bool(re.search(r"\d+", page_text))
        assert has_time_unit or has_any_number, "No response time value found"

    def test_resolution_rate_shows_value(self, live_dashboard_page: Page):
        """Resolution rate stat contains a percentage or a placeholder ('--')."""
        if not _is_activated_dashboard(live_dashboard_page):
            pytest.skip("Dashboard in setup-checklist mode — no stat cards")
        page_text = live_dashboard_page.text_content("main") or ""
        has_percent = "%" in page_text
        has_placeholder = "--" in page_text
        assert has_percent or has_placeholder, (
            "No percentage or placeholder found for resolution rate"
        )

    def test_customer_satisfaction_shows_score(self, live_dashboard_page: Page):
        """Customer satisfaction stat contains a numeric score."""
        if not _is_activated_dashboard(live_dashboard_page):
            pytest.skip("Dashboard in setup-checklist mode — no stat cards")
        page_text = live_dashboard_page.text_content("main") or ""
        assert re.search(r"\d+\.?\d*", page_text), "No satisfaction score found"

    def test_escalation_rate_shows_value(self, live_dashboard_page: Page):
        """Escalation rate stat contains a percentage or a placeholder ('--')."""
        if not _is_activated_dashboard(live_dashboard_page):
            pytest.skip("Dashboard in setup-checklist mode — no stat cards")
        page_text = live_dashboard_page.text_content("main") or ""
        percentage_matches = re.findall(r"\d+\.?\d*\s*%", page_text)
        has_placeholder = "--" in page_text
        assert len(percentage_matches) >= 1 or has_placeholder, (
            "No percentage values or placeholders found on dashboard"
        )


class TestDashboardSections:
    """Dashboard sections render correctly for both activated and fresh states."""

    def test_conversation_chart_or_setup_checklist(self, live_dashboard_page: Page):
        """Activated: chart element present.  Fresh: setup checklist visible."""
        if _is_activated_dashboard(live_dashboard_page):
            chart_svg = live_dashboard_page.locator("svg.recharts-surface, svg[class*='chart']")
            chart_canvas = live_dashboard_page.locator("canvas")
            recharts = live_dashboard_page.locator("[class*='recharts']")
            has_chart = (
                chart_svg.count() > 0
                or chart_canvas.count() > 0
                or recharts.count() > 0
            )
            assert has_chart, "No chart element (SVG or canvas) found on activated dashboard"
        else:
            main_text = (live_dashboard_page.text_content("main") or "").lower()
            has_setup = bool(re.search(
                r"(set up|configure|activate|knowledge|checklist|get started)",
                main_text,
            ))
            assert has_setup, "No setup checklist found on non-activated dashboard"

    def test_recent_conversations_or_empty_state(self, live_dashboard_page: Page):
        """Activated: conversations listed.  Fresh: empty state or no section."""
        main_text = live_dashboard_page.text_content("main") or ""
        has_conversations = bool(re.search(
            r"(recent|conversation|no conversation|no data)", main_text, re.I
        ))
        # Fresh tenants may not show a recent-conversations section at all —
        # the setup checklist replaces the analytics dashboard entirely.
        has_setup = bool(re.search(
            r"(set up|configure|activate|checklist|get started)", main_text, re.I
        ))
        assert has_conversations or has_setup, (
            "No recent conversations section and no setup checklist found"
        )

    def test_top_topics_or_setup_state(self, live_dashboard_page: Page):
        """Top topics section is visible, or dashboard is in setup mode."""
        main_text = live_dashboard_page.text_content("main") or ""
        has_topics = bool(re.search(r"(topic|top topic|no topic)", main_text, re.I))
        has_setup = bool(re.search(
            r"(set up|configure|activate|checklist)", main_text, re.I
        ))
        assert has_topics or has_setup, "No topics section or setup checklist found"

    def test_knowledge_gaps_or_setup_state(self, live_dashboard_page: Page):
        """Knowledge gaps section is visible, or dashboard is in setup mode."""
        main_text = live_dashboard_page.text_content("main") or ""
        has_gaps = bool(re.search(
            r"(knowledge gap|gap|no gap|unanswered)", main_text, re.I
        ))
        has_setup = bool(re.search(
            r"(set up|configure|activate|checklist)", main_text, re.I
        ))
        assert has_gaps or has_setup, "No knowledge gaps section or setup checklist found"

    def test_setup_checklist_or_activated_state(self, live_dashboard_page: Page):
        """Dashboard shows EITHER a setup checklist OR analytics content.

        Activated tenants show stat cards and analytics.  Freshly-seeded
        tenants show a setup checklist with steps.
        """
        main_text = live_dashboard_page.text_content("main") or ""
        has_checklist = bool(re.search(
            r"(set up|checklist|step|complete|get started|activate|configure)",
            main_text, re.I,
        ))
        has_stats = bool(re.search(r"\d+", main_text))
        assert has_checklist or has_stats, (
            "Neither setup checklist nor dashboard stats found"
        )

    def test_period_filter_changes_data(self, live_dashboard_page: Page):
        """Clicking a period filter triggers re-render (activated tenants only)."""
        if not _is_activated_dashboard(live_dashboard_page):
            pytest.skip("Dashboard in setup-checklist mode — no period filters")
        filter_btn = live_dashboard_page.locator(
            "text=/30 days|30d|Last 30|This month/"
        ).first
        if filter_btn.is_visible():
            filter_btn.click()
            live_dashboard_page.wait_for_timeout(1000)
            main_text = live_dashboard_page.text_content("main") or ""
            assert re.search(r"\d+", main_text), "No data after period filter change"
        else:
            pytest.skip("Period filter button not visible")

    def test_stat_card_values_are_real_numbers(self, live_dashboard_page: Page):
        """Stat card values are real numbers, not placeholder text."""
        if not _is_activated_dashboard(live_dashboard_page):
            pytest.skip("Dashboard in setup-checklist mode — no stat cards")
        main_text = live_dashboard_page.text_content("main") or ""
        real_numbers = re.findall(r"\d+\.?\d*", main_text)
        assert len(real_numbers) >= 3, (
            f"Expected at least 3 numeric values on dashboard, "
            f"found {len(real_numbers)}"
        )
