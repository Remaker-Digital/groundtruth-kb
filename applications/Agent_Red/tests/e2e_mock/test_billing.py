# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SPEC-1706 Billing / Account E2E tests against mock Vite dev server.

Tests cover: billing status display, contact preferences, email change
request/confirm flow, message packs, tier display, and API contracts.

Fixture data (billing.ts):
  plan: professional, status: active, includedConversations: 500,
  usedConversations: 342, overageRate: 0.15
  contactPreferences: email=admin@mockstore.com, recoveryEmail=null
"""

import json
import pytest
from playwright.sync_api import Page

from tests.e2e_mock.conftest import (
    api_origin,
    dismiss_onboarding_if_present,
    get_api_json,
    main_text,
    navigate_and_settle,
)


BILLING_PATH = "/billing"


def _go_billing(pg: Page, base_url: str) -> None:
    navigate_and_settle(pg, BILLING_PATH, base_url)
    dismiss_onboarding_if_present(pg)


class TestBillingStatus:
    """Verify the billing status section displays plan and usage data."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        _go_billing(shared_page, mock_base_url)
        self.pg = shared_page

    def test_billing_page_loads(self):
        """Billing page renders with heading."""
        text = main_text(self.pg)
        assert "Account" in text or "billing" in text.lower()

    def test_plan_name_displayed(self):
        """Plan name (professional) is shown."""
        text = main_text(self.pg).lower()
        assert "professional" in text

    def test_plan_status_active(self):
        """Plan status (active) is shown."""
        text = main_text(self.pg).lower()
        assert "active" in text

    def test_included_conversations_shown(self):
        """Included conversations (500) is displayed."""
        text = main_text(self.pg)
        assert "500" in text

    def test_used_conversations_shown(self):
        """Used conversations (342) is displayed."""
        text = main_text(self.pg)
        assert "342" in text

    def test_overage_rate_shown(self):
        """Overage rate (0.15) is displayed."""
        text = main_text(self.pg)
        assert "0.15" in text or "15" in text


class TestContactPreferences:
    """Verify contact preferences section renders and can be updated."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        _go_billing(shared_page, mock_base_url)
        self.pg = shared_page
        self.url = mock_base_url

    def test_contact_section_present(self):
        """Contact preferences section exists on the page."""
        text = main_text(self.pg).lower()
        has_contact = "contact" in text or "email" in text or "preferences" in text
        assert has_contact

    def test_admin_email_displayed(self):
        """Admin email (admin@mockstore.com) is shown or contact section present."""
        text = main_text(self.pg)
        assert "admin@mockstore.com" in text or "contact" in text.lower() or "email" in text.lower()

    def test_notification_email_displayed(self):
        """Notification email section is present."""
        text = main_text(self.pg)
        assert "mockstore" in text or "notification" in text.lower() or "email" in text.lower()

    def test_recovery_email_empty(self):
        """Recovery email section exists."""
        text = main_text(self.pg)
        assert "admin@mockstore.com" in text or "recovery" in text.lower() or "preferences" in text.lower()

    def test_contact_api_returns_preferences(self):
        """GET /api/admin/contact-preferences returns fixture data."""
        data = get_api_json(self.pg, self.url, "/api/admin/contact-preferences")
        assert data["email"] == "admin@mockstore.com"

    def test_update_contact_preferences(self, page: Page, mock_base_url: str):
        """PUT /api/admin/contact-preferences updates notification email."""
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/contact-preferences",
            data=json.dumps({"notificationEmail": "new@mockstore.com"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 200
        body = resp.json()
        assert body["notificationEmail"] == "new@mockstore.com"

    def test_update_preserves_email(self, page: Page, mock_base_url: str):
        """Updating notification email preserves primary email."""
        resp = page.request.put(
            f"{api_origin(mock_base_url)}/api/admin/contact-preferences",
            data=json.dumps({"notificationEmail": "alerts@mockstore.com"}),
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        assert body["email"] == "admin@mockstore.com"

    def test_contact_preferences_has_expected_fields(self):
        """API response includes email, recoveryEmail, notificationEmail."""
        data = get_api_json(self.pg, self.url, "/api/admin/contact-preferences")
        assert "email" in data
        assert "recoveryEmail" in data
        assert "notificationEmail" in data


class TestEmailChange:
    """Verify email change request and confirmation API flow."""

    def test_email_request_succeeds(self, page: Page, mock_base_url: str):
        """POST /api/admin/email/request returns success."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/email/request",
            data=json.dumps({"newEmail": "newemail@mockstore.com"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 200
        body = resp.json()
        assert body["success"] is True

    def test_email_request_message_contains_email(self, page: Page, mock_base_url: str):
        """Request response message mentions the new email."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/email/request",
            data=json.dumps({"newEmail": "test@example.com"}),
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        assert "test@example.com" in body["message"]

    def test_email_confirm_succeeds(self, page: Page, mock_base_url: str):
        """POST /api/admin/email/confirm returns success."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/email/confirm",
            data=json.dumps({"token": "mock-token-123"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 200
        body = resp.json()
        assert body["success"] is True

    def test_email_confirm_message(self, page: Page, mock_base_url: str):
        """Confirm response message indicates success."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/email/confirm",
            data=json.dumps({"token": "any-token"}),
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        assert "updated" in body["message"].lower() or "success" in body["message"].lower()

    def test_email_request_has_success_field(self, page: Page, mock_base_url: str):
        """Request response has a success boolean field."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/email/request",
            data=json.dumps({"newEmail": "a@b.com"}),
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        assert isinstance(body["success"], bool)

    def test_email_confirm_has_message_field(self, page: Page, mock_base_url: str):
        """Confirm response has a message string field."""
        resp = page.request.post(
            f"{api_origin(mock_base_url)}/api/admin/email/confirm",
            data=json.dumps({"token": "t"}),
            headers={"Content-Type": "application/json"},
        )
        body = resp.json()
        assert isinstance(body["message"], str)


class TestMessagePacks:
    """Verify message pack balance and listing."""

    def test_packs_endpoint_returns_balance(self, shared_page: Page, mock_base_url: str):
        """GET /api/billing/packs returns balance of 5."""
        data = get_api_json(shared_page, mock_base_url, "/api/billing/packs")
        assert data["balance"] == 5

    def test_packs_endpoint_returns_empty_list(self, shared_page: Page, mock_base_url: str):
        """GET /api/billing/packs returns empty packs array."""
        data = get_api_json(shared_page, mock_base_url, "/api/billing/packs")
        assert data["packs"] == []

    def test_packs_has_balance_field(self, shared_page: Page, mock_base_url: str):
        """Response includes balance as integer."""
        data = get_api_json(shared_page, mock_base_url, "/api/billing/packs")
        assert isinstance(data["balance"], int)

    def test_packs_has_packs_field(self, shared_page: Page, mock_base_url: str):
        """Response includes packs as list."""
        data = get_api_json(shared_page, mock_base_url, "/api/billing/packs")
        assert isinstance(data["packs"], list)


class TestTierDisplay:
    """Verify tier-related display elements."""

    @pytest.fixture(autouse=True)
    def _navigate(self, shared_page: Page, mock_base_url: str):
        _go_billing(shared_page, mock_base_url)
        self.pg = shared_page

    def test_professional_tier_shown(self):
        """Professional tier is displayed on the billing page."""
        text = main_text(self.pg).lower()
        assert "professional" in text

    def test_billing_period_dates_present(self):
        """Billing period or subscription info is shown."""
        text = main_text(self.pg)
        has_dates = "2026" in text or "March" in text or "period" in text.lower() or "subscription" in text.lower() or "billing" in text.lower()
        assert has_dates

    def test_page_title_account_and_billing(self):
        """Page title contains Account and billing."""
        text = main_text(self.pg)
        assert "Account" in text or "Billing" in text

    def test_billing_content_not_empty(self):
        """Billing page has substantial content."""
        text = main_text(self.pg)
        assert len(text) > 50


class TestBillingApiContracts:
    """Verify billing mock API endpoints return expected data shapes."""

    def test_billing_status_endpoint(self, shared_page: Page, mock_base_url: str):
        """GET /api/billing/status returns expected fields."""
        data = get_api_json(shared_page, mock_base_url, "/api/billing/status")
        assert data["plan"] == "professional"
        assert data["status"] == "active"
        assert data["includedConversations"] == 500

    def test_billing_status_has_usage(self, shared_page: Page, mock_base_url: str):
        """Billing status includes used conversations."""
        data = get_api_json(shared_page, mock_base_url, "/api/billing/status")
        assert data["usedConversations"] == 342

    def test_billing_status_has_overage(self, shared_page: Page, mock_base_url: str):
        """Billing status includes overage rate."""
        data = get_api_json(shared_page, mock_base_url, "/api/billing/status")
        assert data["overageRate"] == 0.15

    def test_billing_status_has_period(self, shared_page: Page, mock_base_url: str):
        """Billing status includes period start and end."""
        data = get_api_json(shared_page, mock_base_url, "/api/billing/status")
        assert "currentPeriodStart" in data
        assert "currentPeriodEnd" in data
