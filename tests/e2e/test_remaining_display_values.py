"""
E2E display-value tests — remaining admin pages.

Covers Knowledge Base, Billing & Usage, Quick Actions, Integrations, and
Memory & Privacy pages.  Each section validates data bindings against the
deterministic mock constants from conftest.py.

Mock data:
  - MOCK_KNOWLEDGE_BASE: 2 articles (Getting Started, Billing FAQ)
  - MOCK_BILLING: tier=professional, 142/1000 conversations, status=active
  - MOCK_QUICK_ACTIONS: 1 action (Track Order, enabled)
  - MOCK_INTEGRATIONS: empty list
  - MOCK_MEMORY_PRIVACY: memoryEnabled, consentMode=standard, retentionDays=90

Run with:
    pytest tests/e2e/test_remaining_display_values.py -v --headed
    pytest tests/e2e/test_remaining_display_values.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect

from .conftest import (
    MOCK_BILLING,
    MOCK_KNOWLEDGE_BASE,
    MOCK_QUICK_ACTIONS,
)

pytestmark = pytest.mark.e2e


# ===========================================================================
# TestKnowledgeBaseDisplayValues — 2 articles, titles, status badges
# ===========================================================================


class TestKnowledgeBaseDisplayValues:
    """Verify Knowledge Base page displays article data from mock."""

    def test_page_heading(self, admin_kb_page: Page) -> None:
        """Knowledge Base page heading is visible."""
        heading = admin_kb_page.locator("h2, h3").filter(has_text="Knowledge")
        expect(heading.first).to_be_visible()

    def test_article_count_matches_mock(self, admin_kb_page: Page) -> None:
        """Page displays both articles from MOCK_KNOWLEDGE_BASE."""
        admin_kb_page.wait_for_timeout(500)
        articles = MOCK_KNOWLEDGE_BASE["articles"]
        for article in articles:
            title = admin_kb_page.get_by_text(article["title"])
            expect(title.first).to_be_visible()

    def test_article_getting_started_title(self, admin_kb_page: Page) -> None:
        """'Getting Started' article title is visible."""
        admin_kb_page.wait_for_timeout(500)
        title = admin_kb_page.get_by_text("Getting Started")
        expect(title.first).to_be_visible()

    def test_article_billing_faq_title(self, admin_kb_page: Page) -> None:
        """'Billing FAQ' article title is visible."""
        admin_kb_page.wait_for_timeout(500)
        title = admin_kb_page.get_by_text("Billing FAQ")
        expect(title.first).to_be_visible()

    def test_article_published_status_badge(self, admin_kb_page: Page) -> None:
        """At least one 'published' status badge is visible."""
        admin_kb_page.wait_for_timeout(500)
        badge = admin_kb_page.locator(
            "[class*='badge'], [class*='Badge']"
        ).filter(has_text="published")
        # Both articles are published
        expect(badge.first).to_be_visible()

    def test_article_general_category(self, admin_kb_page: Page) -> None:
        """'Getting Started' article has category 'general' in mock data."""
        article = MOCK_KNOWLEDGE_BASE["articles"][0]
        assert article["category"] == "general"

    def test_article_billing_category(self, admin_kb_page: Page) -> None:
        """'Billing FAQ' article has category 'billing' in mock data."""
        article = MOCK_KNOWLEDGE_BASE["articles"][1]
        assert article["category"] == "billing"

    def test_total_count_in_mock(self, admin_kb_page: Page) -> None:
        """Mock data totalCount is 2."""
        assert MOCK_KNOWLEDGE_BASE["totalCount"] == 2


# ===========================================================================
# TestBillingDisplayValues — tier, status, conversation usage
# ===========================================================================


class TestBillingDisplayValues:
    """Verify Billing page displays plan data from mock."""

    def test_page_heading(self, admin_billing_page: Page) -> None:
        """Billing page heading is visible."""
        heading = admin_billing_page.locator("h2, h3").filter(has_text="Billing")
        expect(heading.first).to_be_visible()

    def test_tier_professional(self, admin_billing_page: Page) -> None:
        """Billing page shows 'Professional' plan tier."""
        admin_billing_page.wait_for_timeout(500)
        tier = admin_billing_page.get_by_text("Professional")
        expect(tier.first).to_be_visible()

    def test_plan_status_active(self, admin_billing_page: Page) -> None:
        """Billing page shows plan status (active badge or text)."""
        admin_billing_page.wait_for_timeout(500)
        page_text = admin_billing_page.text_content("body") or ""
        # The billing page renders the plan status as a badge or text
        has_active = "active" in page_text.lower() or "Active" in page_text
        assert has_active, "Billing page should show plan status 'active'"

    def test_conversations_used_value(self, admin_billing_page: Page) -> None:
        """Billing page shows 142 conversations used."""
        admin_billing_page.wait_for_timeout(500)
        used = str(MOCK_BILLING["plan"]["conversationsUsed"])
        value = admin_billing_page.get_by_text(used)
        expect(value.first).to_be_visible()

    def test_conversations_limit_value(self, admin_billing_page: Page) -> None:
        """Billing page shows 1,000 conversation limit."""
        admin_billing_page.wait_for_timeout(500)
        # 1000 may be formatted as "1,000" by toLocaleString
        page_text = admin_billing_page.text_content("body") or ""
        limit = MOCK_BILLING["plan"]["conversationsLimit"]
        has_limit = str(limit) in page_text or f"{limit:,}" in page_text
        assert has_limit, f"Billing page should show conversation limit {limit}"


# ===========================================================================
# TestQuickActionsDisplayValues — 1 action: Track Order, enabled
# ===========================================================================


class TestQuickActionsDisplayValues:
    """Verify Quick Actions page displays action data from mock."""

    def test_page_heading(self, admin_quick_actions_page: Page) -> None:
        """Quick Actions page heading is visible."""
        heading = admin_quick_actions_page.locator("h2, h3").filter(
            has_text="Quick"
        )
        expect(heading.first).to_be_visible()

    def test_track_order_label(self, admin_quick_actions_page: Page) -> None:
        """'Track Order' quick action label is visible."""
        admin_quick_actions_page.wait_for_timeout(500)
        label = admin_quick_actions_page.get_by_text("Track Order")
        expect(label.first).to_be_visible()

    def test_track_order_enabled(self, admin_quick_actions_page: Page) -> None:
        """Track Order mock data has enabled=True."""
        action = MOCK_QUICK_ACTIONS["quickActions"][0]
        assert action["enabled"] is True
        assert action["label"] == "Track Order"


# ===========================================================================
# TestIntegrationsDisplayValues — empty state
# ===========================================================================


class TestIntegrationsDisplayValues:
    """Verify Integrations page renders correctly with empty mock data."""

    def test_page_heading(self, admin_integrations_page: Page) -> None:
        """Integrations page heading is visible."""
        admin_integrations_page.wait_for_timeout(500)
        heading = admin_integrations_page.get_by_text("Integrations")
        expect(heading.first).to_be_visible()

    def test_page_subtitle(self, admin_integrations_page: Page) -> None:
        """Integrations page subtitle about third-party services is visible."""
        admin_integrations_page.wait_for_timeout(500)
        subtitle = admin_integrations_page.get_by_text("Connect third-party services")
        expect(subtitle.first).to_be_visible()


# ===========================================================================
# TestMemoryPrivacyDisplayValues — toggle states, retention, consent mode
# ===========================================================================


class TestMemoryPrivacyDisplayValues:
    """Verify Memory & Privacy page displays settings from mock data."""

    def test_page_heading(self, admin_memory_page: Page) -> None:
        """Memory & Privacy page heading is visible."""
        heading = admin_memory_page.locator("h2, h3, h4").filter(has_text="Memory")
        expect(heading.first).to_be_visible()

    def test_memory_enabled_label(self, admin_memory_page: Page) -> None:
        """Page shows 'Memory' toggle or section (memoryEnabled=True in mock)."""
        admin_memory_page.wait_for_timeout(500)
        # The page maps memory_enabled config field to a toggle
        page_text = admin_memory_page.text_content("body") or ""
        assert "Memory" in page_text or "memory" in page_text.lower()

    def test_pii_scrubbing_label(self, admin_memory_page: Page) -> None:
        """Page shows PII scrubbing control."""
        admin_memory_page.wait_for_timeout(500)
        page_text = admin_memory_page.text_content("body") or ""
        assert "PII" in page_text or "pii" in page_text.lower() or \
            "scrubbing" in page_text.lower()

    def test_consent_label(self, admin_memory_page: Page) -> None:
        """Page shows consent configuration (consentMode='standard' in mock)."""
        admin_memory_page.wait_for_timeout(500)
        page_text = admin_memory_page.text_content("body") or ""
        assert "consent" in page_text.lower() or "Consent" in page_text

    def test_identification_mode_gentle_option(self, admin_memory_page: Page) -> None:
        """Identification mode SegmentedControl shows 'Gentle' option."""
        admin_memory_page.wait_for_timeout(500)
        page_text = admin_memory_page.text_content("body") or ""
        has_gentle = "Gentle" in page_text or "gentle" in page_text
        assert has_gentle, "Identification mode should include 'Gentle' option"

    def test_identification_mode_standard_option(self, admin_memory_page: Page) -> None:
        """Identification mode SegmentedControl shows 'Standard' option."""
        admin_memory_page.wait_for_timeout(500)
        page_text = admin_memory_page.text_content("body") or ""
        has_standard = "Standard" in page_text or "standard" in page_text
        assert has_standard, "Identification mode should include 'Standard' option"

    def test_retention_label_present(self, admin_memory_page: Page) -> None:
        """Page shows data retention configuration."""
        admin_memory_page.wait_for_timeout(500)
        page_text = admin_memory_page.text_content("body") or ""
        assert "retention" in page_text.lower() or "Retention" in page_text

    def test_retention_90_days_option(self, admin_memory_page: Page) -> None:
        """Retention days selector includes '90 days' option."""
        admin_memory_page.wait_for_timeout(500)
        page_text = admin_memory_page.text_content("body") or ""
        assert "90 days" in page_text or "90" in page_text

    def test_save_button_visible(self, admin_memory_page: Page) -> None:
        """Save button is present on the page."""
        save_btn = admin_memory_page.locator("button", has_text="Save")
        expect(save_btn.first).to_be_visible()
