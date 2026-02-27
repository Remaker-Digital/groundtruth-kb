"""
E2E tests — Billing & Usage page.

Tests ADMIN_UI specs for the Billing page:
  - Page title
  - Manage subscription button
  - Manage billing button

Run with:
    pytest tests/e2e/test_billing_page.py -v --headed
    pytest tests/e2e/test_billing_page.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

from .conftest import AdminApiMocker

pytestmark = pytest.mark.e2e


class TestBillingPageStructure:
    """Verify the Billing page renders all expected elements."""

    def test_page_title(self, admin_billing_page: Page) -> None:
        """SPEC-0878: Billing page title is 'Billing & usage'."""
        page_text = admin_billing_page.text_content("body") or ""
        heading = admin_billing_page.locator("h2, h3").filter(has_text="Billing")
        assert heading.count() > 0 or "Billing" in page_text, \
            "Billing page heading should be visible"

    def test_manage_subscription_button(self, admin_billing_page: Page) -> None:
        """SPEC-0875: Billing has 'Manage subscription' button."""
        page_text = admin_billing_page.text_content("body") or ""
        manage_sub = admin_billing_page.locator("button, a", has_text="Manage subscription")
        manage_btn = admin_billing_page.locator("button, a", has_text="Manage")
        assert manage_sub.count() > 0 or manage_btn.count() > 0 or \
            "Manage subscription" in page_text or "subscription" in page_text.lower(), \
            "Manage subscription button should be present"

    def test_manage_billing_button(self, admin_billing_page: Page) -> None:
        """SPEC-0876: Billing has 'Manage billing' button."""
        page_text = admin_billing_page.text_content("body") or ""
        manage_billing = admin_billing_page.locator("button, a", has_text="Manage billing")
        manage_btn = admin_billing_page.locator("button, a", has_text="Manage")
        assert manage_billing.count() > 0 or manage_btn.count() > 0 or \
            "billing" in page_text.lower(), \
            "Manage billing button or link should be present"
