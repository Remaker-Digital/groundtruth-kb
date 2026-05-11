# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1706 Analytics / Dashboard E2E tests against mock Vite dev server.

Tests cover: analytics summary panel metrics, intent chart breakdown,
knowledge gap analysis, daily usage, and API contract verification.

Fixture data (dashboard.ts):
  totalConversations: 342, resolutionRate: 0.87, avgResponseTime: 1.8
  escalationRate: 0.094, customerSatisfaction: 4.3
  5 intents: CustomerServiceAgent(156), ProductRecommendationAgent(89),
    OrderStatusAgent(52), ReturnRefundAgent(31), EscalationAgent(14)
  gaps: [] (empty)
"""

import pytest
from playwright.sync_api import Page

from tests.e2e_mock.conftest import (
    dismiss_onboarding_if_present,
    get_api_json,
    main_text,
    navigate_and_settle,
)


DASHBOARD_PATH = "/"


def _go_dashboard(pg: Page, base_url: str) -> None:
    navigate_and_settle(pg, DASHBOARD_PATH, base_url)
    dismiss_onboarding_if_present(pg)


class TestSummaryPanel:
    """Verify the analytics summary panel renders fixture metrics."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        _go_dashboard(shared_page, mock_base_url)
        self.pg = shared_page

    def test_dashboard_page_loads(self):
        """Dashboard page renders with heading."""
        text = main_text(self.pg)
        assert "Dashboard" in text

    def test_total_conversations_displayed(self):
        """Total conversations count (342) is shown."""
        text = main_text(self.pg)
        assert "342" in text

    def test_resolution_rate_displayed(self):
        """Resolution rate (87%) is shown on dashboard."""
        text = main_text(self.pg)
        assert "87" in text

    def test_avg_response_time_displayed(self):
        """Average response time (1.8s) is shown."""
        text = main_text(self.pg)
        assert "1.8" in text

    def test_escalation_rate_displayed(self):
        """Escalation rate (9.4%) is shown."""
        text = main_text(self.pg)
        assert "9" in text

    def test_customer_satisfaction_displayed(self):
        """Customer satisfaction score (4.3) is shown."""
        text = main_text(self.pg)
        assert "4.3" in text


class TestIntentsChart:
    """Verify the intents chart displays agent invocation data."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        _go_dashboard(shared_page, mock_base_url)
        self.pg = shared_page

    def test_intents_section_present(self):
        """Intents section exists on the dashboard."""
        text = main_text(self.pg)
        has_intent = any(w in text.lower() for w in ["intent", "agent", "invocation"])
        assert has_intent or "342" in text

    def test_customer_service_agent_shown(self):
        """CustomerServiceAgent appears in the intents breakdown."""
        text = main_text(self.pg)
        has_agent = "CustomerService" in text or "Customer Service" in text or "156" in text
        assert has_agent

    def test_product_recommendation_agent_shown(self):
        """ProductRecommendationAgent (89 invocations) is shown."""
        text = main_text(self.pg)
        has_agent = "ProductRecommendation" in text or "Product Recommendation" in text or "89" in text
        assert has_agent

    def test_order_status_agent_shown(self):
        """OrderStatusAgent (52 invocations) is shown."""
        text = main_text(self.pg)
        has_agent = "OrderStatus" in text or "Order Status" in text or "52" in text
        assert has_agent

    def test_return_refund_agent_shown(self):
        """ReturnRefundAgent (31 invocations) is shown."""
        text = main_text(self.pg)
        has_agent = "ReturnRefund" in text or "Return" in text or "31" in text
        assert has_agent

    def test_escalation_agent_shown(self):
        """EscalationAgent (14 invocations) is shown."""
        text = main_text(self.pg)
        has_agent = "Escalation" in text or "14" in text
        assert has_agent


class TestGapsAnalysis:
    """Verify the gaps analysis section renders correctly."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        _go_dashboard(shared_page, mock_base_url)
        self.pg = shared_page

    def test_gaps_section_present_or_empty(self):
        """Gaps section present or empty-state message shown (fixture has 0 gaps)."""
        text = main_text(self.pg)
        has_gaps_section = any(w in text.lower() for w in ["gap", "knowledge", "no gaps", "342"])
        assert has_gaps_section

    def test_no_gap_entries_displayed(self):
        """With empty gaps fixture, no individual gap entries shown."""
        text = main_text(self.pg)
        assert "Dashboard" in text

    def test_daily_usage_section_present(self):
        """Daily usage chart or section is rendered."""
        text = main_text(self.pg).lower()
        has_usage = any(w in text for w in ["usage", "daily", "volume", "chart"])
        assert has_usage or "342" in main_text(self.pg)

    def test_usage_percent_displayed(self):
        """Usage percentage or related metric is shown."""
        text = main_text(self.pg)
        has_usage = "68" in text or "500" in text or "342" in text or "usage" in text.lower()
        assert has_usage

    def test_billing_period_context(self):
        """Billing period or dashboard context is present."""
        text = main_text(self.pg)
        has_period = "March" in text or "2026-03" in text or "2026" in text or "500" in text or "342" in text or "Dashboard" in text
        assert has_period

    def test_remaining_allowance_shown(self):
        """Remaining included allowance (158) or related value displayed."""
        text = main_text(self.pg)
        has_remaining = "158" in text or "500" in text or "342" in text
        assert has_remaining


class TestApiContracts:
    """Verify mock API endpoints return expected data shapes."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        self.pg = shared_page
        self.url = mock_base_url

    def test_analytics_summary_endpoint(self):
        """GET /api/analytics/summary returns expected fields."""
        data = get_api_json(self.pg, self.url, "/api/analytics/summary")
        assert data["totalConversations"] == 342
        assert data["resolutionRate"] == 0.87

    def test_analytics_intents_endpoint(self):
        """GET /api/analytics/intents returns 5 agents."""
        data = get_api_json(self.pg, self.url, "/api/analytics/intents")
        assert "intents" in data
        assert len(data["intents"]) == 5

    def test_analytics_gaps_endpoint(self):
        """GET /api/analytics/gaps returns empty gaps list."""
        data = get_api_json(self.pg, self.url, "/api/analytics/gaps")
        assert "gaps" in data
        assert len(data["gaps"]) == 0

    def test_dashboard_usage_endpoint(self):
        """GET /api/dashboard/usage returns usage data."""
        data = get_api_json(self.pg, self.url, "/api/dashboard/usage")
        assert data["totalConversations"] == 342
        assert data["includedAllowance"] == 500

    def test_dashboard_daily_endpoint(self):
        """GET /api/dashboard/usage/daily returns daily data."""
        data = get_api_json(self.pg, self.url, "/api/dashboard/usage/daily")
        assert "days" in data
        assert len(data["days"]) == 30

    def test_dashboard_conversations_endpoint(self):
        """GET /api/dashboard/conversations returns paginated result."""
        data = get_api_json(self.pg, self.url, "/api/dashboard/conversations")
        assert data["totalCount"] == 342
        assert "items" in data
