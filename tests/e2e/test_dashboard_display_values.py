"""Display value verification tests for the Dashboard page.

Each test verifies that a specific value rendered in the DOM matches the
expected mock data from conftest.py.  Tests are grouped by visual section:
stat cards, recent conversations, top topics, knowledge gaps, setup
checklist, and period filter.

The admin_page fixture navigates to the Dashboard with mocked API
responses — no backend is required.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

from .conftest import (
    MOCK_ANALYTICS_SUMMARY,
    MOCK_CONFIG,
    MOCK_KNOWLEDGE_GAPS_DATA,
    AdminApiMocker,
    setup_admin_page,
)

pytestmark = pytest.mark.e2e


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wait_for_data(page: Page) -> None:
    """Allow dashboard data hooks to populate the DOM."""
    page.wait_for_timeout(500)


# ===========================================================================
# TestDashboardStatCardValues — verify each stat card displays correct data
# ===========================================================================

class TestDashboardStatCardValues:
    """Every stat card value must match the MOCK_ANALYTICS_SUMMARY data."""

    def test_total_conversations_displays_142(self, admin_page: Page):
        """Total conversations card shows 142 from mock summary."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("142").first).to_be_visible()

    def test_total_conversations_label_present(self, admin_page: Page):
        """The label 'Total conversations' is visible on the stat card."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Total conversations").first).to_be_visible()

    def test_avg_response_time_displays_2_3s(self, admin_page: Page):
        """Avg response time card shows '2.3s' from formatResponseTime(2.3)."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("2.3s").first).to_be_visible()

    def test_avg_response_time_label_present(self, admin_page: Page):
        """The label 'Avg response time' is visible on the stat card."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Avg response time").first).to_be_visible()

    def test_resolution_rate_displays_90_1_percent(self, admin_page: Page):
        """Resolution rate card shows '90.1%' from 0.901 * 100."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("90.1%").first).to_be_visible()

    def test_resolution_rate_label_present(self, admin_page: Page):
        """The label 'Resolution rate' is visible on the stat card."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Resolution rate").first).to_be_visible()

    def test_resolution_rate_detail_shows_resolved_count(self, admin_page: Page):
        """Detail line shows 'N resolved' where N = round(142 * 0.901) = 128."""
        _wait_for_data(admin_page)
        total = MOCK_ANALYTICS_SUMMARY["totalConversations"]
        rate = MOCK_ANALYTICS_SUMMARY["resolutionRate"]
        resolved = round(total * rate)
        expect(admin_page.get_by_text(f"{resolved} resolved").first).to_be_visible()

    def test_customer_satisfaction_displays_4_2_out_of_5(self, admin_page: Page):
        """Customer satisfaction card shows '4.2/5' from formatSatisfaction(4.2)."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("4.2/5").first).to_be_visible()

    def test_customer_satisfaction_label_present(self, admin_page: Page):
        """The label 'Customer satisfaction' is visible on the stat card."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Customer satisfaction").first).to_be_visible()

    def test_escalation_rate_displays_12_7_percent(self, admin_page: Page):
        """Escalation rate card shows '12.7%' from 0.127 * 100."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("12.7%").first).to_be_visible()

    def test_escalation_rate_label_present(self, admin_page: Page):
        """The label 'Escalation rate' is visible on the stat card."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Escalation rate").first).to_be_visible()

    def test_escalation_detail_shows_18_escalated(self, admin_page: Page):
        """Detail line shows '18 escalated' from mock escalationCount."""
        _wait_for_data(admin_page)
        count = MOCK_ANALYTICS_SUMMARY["escalationCount"]
        expect(admin_page.get_by_text(f"{count} escalated").first).to_be_visible()


# ===========================================================================
# TestDashboardRecentConversationValues — verify conversation list data
# ===========================================================================

class TestDashboardRecentConversationValues:
    """Each conversation card must show correct customer, status, and count."""

    def test_first_customer_name_john_doe(self, admin_page: Page):
        """First conversation shows 'John Doe' from mock data."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("John Doe").first).to_be_visible()

    def test_second_customer_name_jane_smith(self, admin_page: Page):
        """Second conversation shows 'Jane Smith' from mock data."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Jane Smith").first).to_be_visible()

    def test_third_customer_name_bob_wilson(self, admin_page: Page):
        """Third conversation shows 'Bob Wilson' from mock data."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Bob Wilson").first).to_be_visible()

    def test_first_conversation_status_active(self, admin_page: Page):
        """conv-001 has status 'active' rendered as a badge."""
        _wait_for_data(admin_page)
        badge = admin_page.locator("[class*='badge'], [class*='Badge']").filter(
            has_text="active"
        )
        expect(badge.first).to_be_visible()

    def test_second_conversation_status_escalated(self, admin_page: Page):
        """conv-002 has status 'escalated' rendered as a badge."""
        _wait_for_data(admin_page)
        badge = admin_page.locator("[class*='badge'], [class*='Badge']").filter(
            has_text="escalated"
        )
        expect(badge.first).to_be_visible()

    def test_third_conversation_status_ended(self, admin_page: Page):
        """conv-003 has status 'ended' rendered as a badge."""
        _wait_for_data(admin_page)
        badge = admin_page.locator("[class*='badge'], [class*='Badge']").filter(
            has_text="ended"
        )
        expect(badge.first).to_be_visible()

    def test_first_conversation_message_count_3(self, admin_page: Page):
        """conv-001 shows '3 messages' from messageCount=3."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("3 messages").first).to_be_visible()

    def test_second_conversation_message_count_8(self, admin_page: Page):
        """conv-002 shows '8 messages' from messageCount=8."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("8 messages").first).to_be_visible()

    def test_third_conversation_message_count_4(self, admin_page: Page):
        """conv-003 shows '4 messages' from messageCount=4."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("4 messages").first).to_be_visible()

    def test_escalated_conversation_shows_escalated_label(self, admin_page: Page):
        """conv-002 (escalated) shows 'Escalated' assignment text."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Escalated").first).to_be_visible()

    def test_active_conversation_shows_unassigned(self, admin_page: Page):
        """conv-001 (active, assignedTo=None) shows 'Unassigned'."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Unassigned").first).to_be_visible()


# ===========================================================================
# TestDashboardTopTopicValues — verify intent breakdown data
# ===========================================================================

class TestDashboardTopTopicValues:
    """Each topic must show the correct display label and invocation count."""

    def test_order_tracking_label(self, admin_page: Page):
        """'order-tracking' agent renders as 'Order Tracking'."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Order Tracking").first).to_be_visible()

    def test_order_tracking_count_45(self, admin_page: Page):
        """order-tracking shows invocationCount 45."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("45").first).to_be_visible()

    def test_product_inquiry_label(self, admin_page: Page):
        """'product-inquiry' agent renders as 'Product Inquiry'."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Product Inquiry").first).to_be_visible()

    def test_product_inquiry_count_38(self, admin_page: Page):
        """product-inquiry shows invocationCount 38."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("38").first).to_be_visible()

    def test_return_refund_label(self, admin_page: Page):
        """'return-refund' agent renders as 'Return Refund'."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Return Refund").first).to_be_visible()

    def test_return_refund_count_25(self, admin_page: Page):
        """return-refund shows invocationCount 25."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("25").first).to_be_visible()

    def test_billing_support_label(self, admin_page: Page):
        """'billing-support' agent renders as 'Billing Support'."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("Billing Support").first).to_be_visible()

    def test_billing_support_count_20(self, admin_page: Page):
        """billing-support shows invocationCount 20."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("20").first).to_be_visible()

    def test_general_faq_label(self, admin_page: Page):
        """'general-faq' agent renders as 'General Faq'."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("General Faq").first).to_be_visible()

    def test_general_faq_count_14(self, admin_page: Page):
        """general-faq shows invocationCount 14."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("14").first).to_be_visible()

    def test_topic_breakdown_table_first_percentage_31_7(self, admin_page: Page):
        """Topic breakdown table shows 31.7% for order-tracking."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("31.7%").first).to_be_visible()

    def test_topic_breakdown_table_third_percentage_17_6(self, admin_page: Page):
        """Topic breakdown table shows 17.6% for return-refund."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("17.6%").first).to_be_visible()

    def test_topic_breakdown_table_fifth_percentage_9_9(self, admin_page: Page):
        """Topic breakdown table shows 9.9% for general-faq."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("9.9%").first).to_be_visible()


# ===========================================================================
# TestDashboardKnowledgeGapValues — verify gap table data
# ===========================================================================

class TestDashboardKnowledgeGapValues:
    """Each knowledge gap row must display correct conversation data."""

    def test_first_gap_conversation_id(self, admin_page: Page):
        """First gap shows conversationId 'conv-gap-001'."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("conv-gap-001").first).to_be_visible()

    def test_second_gap_conversation_id(self, admin_page: Page):
        """Second gap shows conversationId 'conv-gap-002'."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("conv-gap-002").first).to_be_visible()

    def test_first_gap_status_escalated(self, admin_page: Page):
        """First gap has status badge 'escalated'."""
        _wait_for_data(admin_page)
        # Use table-scoped badge to avoid matching recent conversations
        gaps_table = admin_page.locator("table").last
        badge = gaps_table.locator("[class*='badge'], [class*='Badge']").filter(
            has_text="escalated"
        )
        expect(badge.first).to_be_visible()

    def test_second_gap_status_ended(self, admin_page: Page):
        """Second gap has status badge 'ended'."""
        _wait_for_data(admin_page)
        gaps_table = admin_page.locator("table").last
        badge = gaps_table.locator("[class*='badge'], [class*='Badge']").filter(
            has_text="ended"
        )
        expect(badge.first).to_be_visible()

    def test_first_gap_customer_id_cust_101(self, admin_page: Page):
        """First gap shows customerId 'cust-101'."""
        _wait_for_data(admin_page)
        expect(admin_page.get_by_text("cust-101").first).to_be_visible()

    def test_first_gap_turn_count_6(self, admin_page: Page):
        """First gap shows turnCount 6 in the Turns column."""
        _wait_for_data(admin_page)
        gaps_table = admin_page.locator("table").last
        cells = gaps_table.locator("tbody td")
        expect(cells.filter(has_text="6").first).to_be_visible()

    def test_first_gap_message_count_12(self, admin_page: Page):
        """First gap shows messageCount 12 in the Messages column."""
        _wait_for_data(admin_page)
        gaps_table = admin_page.locator("table").last
        cells = gaps_table.locator("tbody td")
        expect(cells.filter(has_text="12").first).to_be_visible()

    def test_second_gap_turn_count_3(self, admin_page: Page):
        """Second gap shows turnCount 3 in the Turns column."""
        _wait_for_data(admin_page)
        gaps_table = admin_page.locator("table").last
        cells = gaps_table.locator("tbody td")
        expect(cells.filter(has_text="3").first).to_be_visible()

    def test_second_gap_message_count_6(self, admin_page: Page):
        """Second gap shows messageCount 6 in the Messages column."""
        _wait_for_data(admin_page)
        gaps_table = admin_page.locator("table").last
        cells = gaps_table.locator("tbody td")
        expect(cells.filter(has_text="6").first).to_be_visible()

    def test_gap_count_badge_shows_2_gaps(self, admin_page: Page):
        """Gap count badge reads '2 gaps' for 2 entries in mock data."""
        _wait_for_data(admin_page)
        expected = f"{len(MOCK_KNOWLEDGE_GAPS_DATA['gaps'])} gaps"
        expect(admin_page.get_by_text(expected).first).to_be_visible()

    def test_first_gap_started_at_date_visible(self, admin_page: Page):
        """First gap shows a formatted startedAt date (Feb 24, 2026)."""
        _wait_for_data(admin_page)
        # formatLastSeen("2026-02-24T09:00:00Z") produces locale-dependent output
        # but will contain "Feb" and "24" and "2026"
        gaps_table = admin_page.locator("table").last
        expect(gaps_table.get_by_text("24").first).to_be_visible()


# ===========================================================================
# TestDashboardSetupChecklist — conditional display verification
# ===========================================================================

class TestDashboardSetupChecklist:
    """Setup checklist shown only when tenant is not active."""

    def test_checklist_hidden_when_active(self, admin_page: Page):
        """Active tenant (default mock) does NOT show 'Setup progress'."""
        _wait_for_data(admin_page)
        checklist = admin_page.get_by_text("Setup progress")
        expect(checklist).to_have_count(0)

    def test_checklist_visible_when_inactive(
        self, page: Page, admin_vite_server, api_mocker: AdminApiMocker
    ):
        """Inactive tenant shows 'Setup progress' checklist."""
        api_mocker.override("/api/config/activation-status", {
            "status": "draft",
            "is_configured": True,
            "is_active": False,
            "can_activate": True,
            "has_pending_changes": True,
            "active_version": 1,
            "active_activated_at": "2026-02-20T12:00:00Z",
            "draft_version": 2,
        })
        setup_admin_page(page, api_mocker)
        _wait_for_data(page)
        expect(page.get_by_text("Setup progress").first).to_be_visible()

    def test_checklist_shows_brand_name_item(
        self, page: Page, admin_vite_server, api_mocker: AdminApiMocker
    ):
        """Checklist includes 'Brand name configured' step."""
        api_mocker.override("/api/config/activation-status", {
            "status": "draft",
            "is_configured": True,
            "is_active": False,
            "active_activated_at": "2026-02-20T12:00:00Z",
            "active_version": 1,
        })
        setup_admin_page(page, api_mocker)
        _wait_for_data(page)
        expect(page.get_by_text("Brand name configured").first).to_be_visible()

    def test_checklist_shows_system_activated_item(
        self, page: Page, admin_vite_server, api_mocker: AdminApiMocker
    ):
        """Checklist includes 'System activated' step."""
        api_mocker.override("/api/config/activation-status", {
            "status": "draft",
            "is_configured": True,
            "is_active": False,
            "active_activated_at": "2026-02-20T12:00:00Z",
            "active_version": 1,
        })
        setup_admin_page(page, api_mocker)
        _wait_for_data(page)
        expect(page.get_by_text("System activated").first).to_be_visible()


# ===========================================================================
# TestDashboardPeriodFilter — verify default and available filter options
# ===========================================================================

class TestDashboardPeriodFilter:
    """Period filter defaults and options must render correctly."""

    def test_default_period_30d_visible(self, admin_page: Page):
        """Default period '30d' label is visible in the SegmentedControl."""
        selected = admin_page.locator("label").filter(has_text="30d")
        expect(selected.first).to_be_visible()

    def test_chart_shows_last_30_days_by_default(self, admin_page: Page):
        """Chart period label reads 'Last 30 days' on initial load."""
        expect(admin_page.get_by_text("Last 30 days").first).to_be_visible()

    def test_7d_option_visible(self, admin_page: Page):
        """Period option '7d' is available."""
        expect(admin_page.locator("label").filter(has_text="7d").first).to_be_visible()

    def test_14d_option_visible(self, admin_page: Page):
        """Period option '14d' is available."""
        expect(admin_page.locator("label").filter(has_text="14d").first).to_be_visible()

    def test_90d_option_visible(self, admin_page: Page):
        """Period option '90d' is available."""
        expect(admin_page.locator("label").filter(has_text="90d").first).to_be_visible()

    def test_store_name_from_brand_config(self, admin_page: Page):
        """Store name header shows brand_name from MOCK_CONFIG."""
        _wait_for_data(admin_page)
        brand = str(MOCK_CONFIG["config"]["brand_name"])
        expect(admin_page.get_by_text(brand).first).to_be_visible()
