"""
Live E2E Billing page tests — real data from staging/production.

Validates that the Billing admin page renders correctly with plan
information and usage metrics from the live backend.

SPEC-1649: All tests use only live external interfaces.
WI-1023: Expand tests/e2e_live/ to cover all admin pages.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page


class TestBillingPageStructure:
    """Verify the Billing page renders with real data."""

    def test_bill_live_01_page_heading(self, live_billing_page: Page):
        """BILL-LIVE-01: Billing page shows heading."""
        main_text = live_billing_page.text_content("main") or ""
        assert "Billing" in main_text, "No Billing heading found"

    def test_bill_live_02_plan_info_displayed(self, live_billing_page: Page):
        """BILL-LIVE-02: Billing page shows plan tier information."""
        live_billing_page.wait_for_timeout(1000)
        main_text = (live_billing_page.text_content("main") or "").lower()
        # Should show plan tier or subscription info
        has_plan = any(
            term in main_text
            for term in [
                "starter", "professional", "enterprise", "trial",
                "plan", "subscription", "tier",
            ]
        )
        assert has_plan, "No plan/subscription information found on Billing page"

    def test_bill_live_03_usage_metrics_present(self, live_billing_page: Page):
        """BILL-LIVE-03: Billing page shows usage metrics or conversation stats."""
        live_billing_page.wait_for_timeout(1000)
        main_text = (live_billing_page.text_content("main") or "").lower()
        has_usage = any(
            term in main_text
            for term in [
                "conversation", "usage", "included", "remaining",
                "overage", "limit", "pack", "balance",
            ]
        )
        assert has_usage, "No usage metrics found on Billing page"

    def test_bill_live_04_manage_buttons_present(self, live_billing_page: Page):
        """BILL-LIVE-04: Billing page has management action buttons."""
        live_billing_page.wait_for_timeout(500)
        main_text = live_billing_page.text_content("main") or ""
        has_buttons = any(
            term in main_text
            for term in [
                "Manage", "Upgrade", "Purchase", "Change",
            ]
        )
        # If no buttons with those labels, check for any buttons at all
        if not has_buttons:
            buttons = live_billing_page.locator("main button")
            has_buttons = buttons.count() >= 1
        assert has_buttons, "No management buttons found on Billing page"
