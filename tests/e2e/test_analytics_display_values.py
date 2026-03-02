"""
E2E display-value tests — Analytics page.

Validates every visible data binding on the Analytics page against
deterministic mock data from conftest.py.

Stat cards (from MOCK_ANALYTICS_SUMMARY):
  - Total conversations: 142 (detail: "Billable: 128")
  - Avg response time: 2.3s
  - Resolution rate: 90.1% (detail: "128 resolved")
  - Customer satisfaction: 4.2/5
  - Escalation rate: 12.7% (detail: "18 escalated")

Topic breakdown table (from MOCK_INTENT_BREAKDOWN):
  - 5 intents with agent name, invocation count, and percentage

Uses the ``admin_page`` fixture and navigates to Analytics via sidebar.

Run with:
    pytest tests/e2e/test_analytics_display_values.py -v --headed
    pytest tests/e2e/test_analytics_display_values.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

from .conftest import (
    MOCK_ANALYTICS_SUMMARY,
    MOCK_INTENT_BREAKDOWN,
    _navigate_admin_to,
)

pytestmark = pytest.mark.e2e


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _go_to_analytics(page: Page) -> Page:
    """Navigate from Dashboard to Analytics page."""
    return _navigate_admin_to(page, "Analytics", "Analytics")


def _wait_for_analytics_data(page: Page) -> None:
    """Wait for stat cards to populate from API."""
    page.wait_for_timeout(500)


# ---------------------------------------------------------------------------
# Fixture: analytics page
# ---------------------------------------------------------------------------

@pytest.fixture()
def admin_analytics_page(admin_page: Page) -> Page:
    """Navigate to the Analytics page and wait for data."""
    _go_to_analytics(admin_page)
    _wait_for_analytics_data(admin_page)
    return admin_page


# ===========================================================================
# TestAnalyticsStatCardValues — 5 stat cards with labels, values, details
# ===========================================================================


class TestAnalyticsStatCardValues:
    """Verify each Analytics stat card displays the correct value."""

    def test_total_conversations_label(self, admin_analytics_page: Page) -> None:
        """Total conversations stat card label is visible."""
        label = admin_analytics_page.get_by_text("Total conversations")
        expect(label.first).to_be_visible()

    def test_total_conversations_value(self, admin_analytics_page: Page) -> None:
        """Total conversations value is 142 (from MOCK_ANALYTICS_SUMMARY)."""
        expected = str(MOCK_ANALYTICS_SUMMARY["totalConversations"])
        value = admin_analytics_page.get_by_text(expected)
        expect(value.first).to_be_visible()

    def test_billable_conversations_detail(self, admin_analytics_page: Page) -> None:
        """Total conversations card shows 'Billable: 128' detail."""
        expected_billable = str(MOCK_ANALYTICS_SUMMARY["billableConversations"])
        detail = admin_analytics_page.get_by_text(f"Billable: {expected_billable}")
        expect(detail.first).to_be_visible()

    def test_avg_response_time_label(self, admin_analytics_page: Page) -> None:
        """Avg response time stat card label is visible."""
        label = admin_analytics_page.get_by_text("Avg response time")
        expect(label.first).to_be_visible()

    def test_avg_response_time_value(self, admin_analytics_page: Page) -> None:
        """Avg response time value is '2.3s'."""
        expected = f"{MOCK_ANALYTICS_SUMMARY['avgResponseTime']}s"
        value = admin_analytics_page.get_by_text(expected)
        expect(value.first).to_be_visible()

    def test_resolution_rate_label(self, admin_analytics_page: Page) -> None:
        """Resolution rate stat card label is visible."""
        label = admin_analytics_page.get_by_text("Resolution rate")
        expect(label.first).to_be_visible()

    def test_resolution_rate_value(self, admin_analytics_page: Page) -> None:
        """Resolution rate value is '90.1%' (0.901 * 100)."""
        pct = MOCK_ANALYTICS_SUMMARY["resolutionRate"] * 100
        expected = f"{pct:.1f}%"
        value = admin_analytics_page.get_by_text(expected)
        expect(value.first).to_be_visible()

    def test_resolution_rate_detail_resolved_count(self, admin_analytics_page: Page) -> None:
        """Resolution rate detail shows resolved count ('128 resolved')."""
        total = MOCK_ANALYTICS_SUMMARY["totalConversations"]
        rate = MOCK_ANALYTICS_SUMMARY["resolutionRate"]
        resolved = round(total * rate)
        detail = admin_analytics_page.get_by_text(f"{resolved} resolved")
        expect(detail.first).to_be_visible()

    def test_customer_satisfaction_value(self, admin_analytics_page: Page) -> None:
        """Customer satisfaction value is '4.2/5'."""
        expected = f"{MOCK_ANALYTICS_SUMMARY['customerSatisfaction']}/5"
        value = admin_analytics_page.get_by_text(expected)
        expect(value.first).to_be_visible()

    def test_escalation_rate_value(self, admin_analytics_page: Page) -> None:
        """Escalation rate value is '12.7%' (0.127 * 100)."""
        pct = MOCK_ANALYTICS_SUMMARY["escalationRate"] * 100
        expected = f"{pct:.1f}%"
        value = admin_analytics_page.get_by_text(expected)
        expect(value.first).to_be_visible()

    def test_escalation_count_detail(self, admin_analytics_page: Page) -> None:
        """Escalation rate detail shows '18 escalated'."""
        count = MOCK_ANALYTICS_SUMMARY["escalationCount"]
        detail = admin_analytics_page.get_by_text(f"{count} escalated")
        expect(detail.first).to_be_visible()


# ===========================================================================
# TestAnalyticsTopicValues — Topic breakdown table with 5 intents
# ===========================================================================


class TestAnalyticsTopicValues:
    """Verify the topic breakdown table displays all intent data."""

    def test_topic_breakdown_heading(self, admin_analytics_page: Page) -> None:
        """Topic breakdown section heading is visible."""
        heading = admin_analytics_page.get_by_text("Topic breakdown")
        expect(heading.first).to_be_visible()

    def test_table_header_topic(self, admin_analytics_page: Page) -> None:
        """Table has 'Topic' column header."""
        header = admin_analytics_page.locator("th").filter(has_text="Topic")
        expect(header.first).to_be_visible()

    def test_table_header_count(self, admin_analytics_page: Page) -> None:
        """Table has 'Count' column header."""
        header = admin_analytics_page.locator("th").filter(has_text="Count")
        expect(header.first).to_be_visible()

    def test_table_header_distribution(self, admin_analytics_page: Page) -> None:
        """Table has 'Distribution' column header."""
        header = admin_analytics_page.locator("th").filter(has_text="Distribution")
        expect(header.first).to_be_visible()

    def test_topic_order_tracking_label(self, admin_analytics_page: Page) -> None:
        """First topic 'Order Tracking' (agent: order-tracking) is visible."""
        label = admin_analytics_page.get_by_text("Order Tracking")
        expect(label.first).to_be_visible()

    def test_topic_order_tracking_count(self, admin_analytics_page: Page) -> None:
        """Order Tracking count is 45."""
        count = admin_analytics_page.get_by_text("45")
        expect(count.first).to_be_visible()

    def test_topic_order_tracking_percentage(self, admin_analytics_page: Page) -> None:
        """Order Tracking percentage is 31.7%."""
        pct = admin_analytics_page.get_by_text("31.7%")
        expect(pct.first).to_be_visible()

    def test_topic_product_inquiry_label(self, admin_analytics_page: Page) -> None:
        """Second topic 'Product Inquiry' is visible."""
        label = admin_analytics_page.get_by_text("Product Inquiry")
        expect(label.first).to_be_visible()

    def test_topic_product_inquiry_count(self, admin_analytics_page: Page) -> None:
        """Product Inquiry count is 38."""
        count = admin_analytics_page.get_by_text("38")
        expect(count.first).to_be_visible()

    def test_topic_return_refund_label(self, admin_analytics_page: Page) -> None:
        """Third topic 'Return Refund' is visible."""
        label = admin_analytics_page.get_by_text("Return Refund")
        expect(label.first).to_be_visible()

    def test_topic_billing_support_label(self, admin_analytics_page: Page) -> None:
        """Fourth topic 'Billing Support' is visible."""
        label = admin_analytics_page.get_by_text("Billing Support")
        expect(label.first).to_be_visible()

    def test_topic_general_faq_label(self, admin_analytics_page: Page) -> None:
        """Fifth topic 'General Faq' is visible."""
        label = admin_analytics_page.get_by_text("General Faq")
        expect(label.first).to_be_visible()

    def test_all_five_topic_rows(self, admin_analytics_page: Page) -> None:
        """Table body contains 5 rows for the 5 intents."""
        rows = admin_analytics_page.locator(
            "table tbody tr, [class*='Table'] tbody tr"
        )
        # There may be multiple tables (topic + gaps); verify at least 5 rows
        assert rows.count() >= 5, (
            f"Expected at least 5 topic rows, found {rows.count()}"
        )

    def test_all_topic_percentages_present(self, admin_analytics_page: Page) -> None:
        """All 5 percentage values from mock data are displayed."""
        for intent in MOCK_INTENT_BREAKDOWN["intents"]:
            pct_text = f"{intent['percentage']}%"
            pct = admin_analytics_page.get_by_text(pct_text)
            expect(pct.first).to_be_visible()
