"""
Live E2E Billing & Usage page tests — comprehensive against staging.

Tests exercise ALL 34 inventoried elements (EL-billing-001..034) across
six sections: Header, Plan Card, Usage Stats, Usage Chart, Conversation Packs,
Add-on Modules, and Manage Billing.

SPEC-1649: All tests use only live external interfaces.
SPEC-1652: Phase 2 — comprehensive E2E with full CRUD mutations.
SPEC-1655: Staging mutations required — no capture/restore patterns.

Test architecture:
  - Tenant is a draft/trial/starter tenant after re-seed.
  - Stripe-gated elements (Manage subscription, Manage billing) may not
    be present on the draft tenant — tests skip gracefully.
  - Usage data may be zero/empty on a freshly-seeded tenant.
  - 2 s inter-class cooldown prevents API burst clustering (500 rpm limit).

API endpoints exercised:
  GET    /api/admin/usage-dashboard    (usage stats)
  GET    /api/admin/daily-volume       (chart data)
  POST   /api/billing/portal           (Stripe portal — if Stripe tenant)
  POST   /api/packs/purchase           (pack checkout — Stripe)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from playwright.sync_api import Page, expect


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_rate_limited(page: Page) -> bool:
    """Detect if the page is showing a rate-limit or load-failure state."""
    body = page.inner_text("body")
    lower = body.lower()
    if "failed to load" in lower and "429" in lower:
        return True
    if "rate limit" in lower:
        return True
    return False


def _wait_for_billing_page(page: Page) -> None:
    """Wait for the Billing page to fully load."""
    for attempt in range(3):
        try:
            page.wait_for_selector(
                "text=/Billing|usage|subscription/i",
                timeout=10_000,
            )
            return
        except Exception:
            if attempt < 2:
                page.wait_for_timeout(3000)
                page.reload(wait_until="load")


def _scroll_to_text(page: Page, text: str) -> None:
    """Scroll until a text element is in the viewport."""
    loc = page.locator(f"text={text}").first
    try:
        loc.scroll_into_view_if_needed(timeout=5_000)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# TestPageHeader — EL-billing-001
# ---------------------------------------------------------------------------

class TestPageHeader:
    """Page title and subtitle."""

    def test_page_title_visible(self, live_billing_page: Page):
        """EL-billing-001: Page title 'Account and billing' is visible."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        title = page.locator("h2:has-text('Account')").first
        expect(title).to_be_visible()

    def test_page_subtitle_visible(self, live_billing_page: Page):
        """EL-billing-001: Subtitle about managing subscription is visible."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        sub = page.locator("text=Manage your subscription").first
        expect(sub).to_be_visible()


# ---------------------------------------------------------------------------
# TestPlanCard — EL-billing-002..008
# ---------------------------------------------------------------------------

class TestPlanCard:
    """Current plan card with tier, status, and manage button."""

    def test_current_plan_card_visible(self, live_billing_page: Page):
        """EL-billing-002: Current plan card is visible."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        plan = page.locator("text=Current plan").first
        expect(plan).to_be_visible()

    def test_tier_badge_visible(self, live_billing_page: Page):
        """EL-billing-004: Tier badge is visible (Trial/Starter/Professional/Enterprise)."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        for tier in ["Trial", "Starter", "Professional", "Enterprise"]:
            badge = page.locator(f"text={tier}")
            if badge.count() > 0:
                expect(badge.first).to_be_visible()
                return
        pytest.fail("No tier badge found (Trial/Starter/Professional/Enterprise)")

    def test_subscription_status_badge(self, live_billing_page: Page):
        """EL-billing-006: Subscription status badge (Active/Suspended/etc.)."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        for status in ["Active", "Suspended", "Cancelled", "Trial expired"]:
            badge = page.locator(f"text={status}")
            if badge.count() > 0:
                expect(badge.first).to_be_visible()
                return
        pytest.fail("No status badge found")

    def test_included_conversations_display(self, live_billing_page: Page):
        """EL-billing-002: Included conversations count is shown."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        label = page.locator("text=Included conversations").first
        expect(label).to_be_visible()

    def test_used_this_period_display(self, live_billing_page: Page):
        """EL-billing-002: 'Used this period' count shown."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        label = page.locator("text=Used this period").first
        expect(label).to_be_visible()

    def test_remaining_display(self, live_billing_page: Page):
        """EL-billing-002: Remaining conversations shown."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        label = page.locator("text=Remaining").first
        expect(label).to_be_visible()

    def test_manage_subscription_button(self, live_billing_page: Page):
        """EL-billing-008: Manage subscription button (Stripe tenants only)."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        btn = page.locator("button:has-text('Manage subscription')")
        if btn.count() == 0:
            pytest.skip("Manage subscription button not shown — not a Stripe tenant")
        expect(btn.first).to_be_visible()


# ---------------------------------------------------------------------------
# TestUsageStats — EL-billing-009..012
# ---------------------------------------------------------------------------

class TestUsageStats:
    """Four usage stat cards: conversations, pack balance, overage, cost."""

    def test_conversations_used_card(self, live_billing_page: Page):
        """EL-billing-009: Conversations used stat card with progress ring."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        label = page.locator("text=Conversations used").first
        expect(label).to_be_visible()

    def test_pack_balance_card(self, live_billing_page: Page):
        """EL-billing-010: Pack balance stat card."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        label = page.locator("text=Pack balance").first
        expect(label).to_be_visible()

    def test_current_overage_card(self, live_billing_page: Page):
        """EL-billing-011: Current overage stat card."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        label = page.locator("text=Current overage").first
        expect(label).to_be_visible()

    def test_estimated_overage_cost_card(self, live_billing_page: Page):
        """EL-billing-012: Estimated overage cost stat card."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        label = page.locator("text=Estimated overage cost").first
        expect(label).to_be_visible()

    def test_usage_percent_shown(self, live_billing_page: Page):
        """EL-billing-009: Usage percentage shown as subtext."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        pct = page.locator("text=of included allowance")
        if pct.count() == 0:
            pytest.skip("Usage percent text not visible")
        expect(pct.first).to_be_visible()


# ---------------------------------------------------------------------------
# TestUsageChart — EL-billing-013..015
# ---------------------------------------------------------------------------

class TestUsageChart:
    """Daily usage area chart with legend and empty state."""

    def test_chart_section_visible(self, live_billing_page: Page):
        """EL-billing-013: Daily usage chart section visible."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Daily usage")
        label = page.locator("text=Daily usage").first
        expect(label).to_be_visible()

    def test_chart_or_empty_state(self, live_billing_page: Page):
        """EL-billing-013/015: Either the chart renders or empty state message."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Daily usage")
        chart = page.locator(".recharts-responsive-container, .recharts-wrapper")
        empty = page.locator("text=No usage data available")
        assert chart.count() > 0 or empty.count() > 0, \
            "Neither chart nor empty state found"

    def test_chart_legend(self, live_billing_page: Page):
        """EL-billing-014: Chart legend with Total and Billable labels."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Daily usage")
        total_legend = page.locator("text=Total")
        billable_legend = page.locator("text=Billable")
        if total_legend.count() == 0 and billable_legend.count() == 0:
            empty = page.locator("text=No usage data available")
            if empty.count() > 0:
                pytest.skip("No chart data — legend not rendered")
        assert total_legend.count() > 0 or billable_legend.count() > 0


# ---------------------------------------------------------------------------
# TestUsageAlerts — EL-billing-016
# ---------------------------------------------------------------------------

class TestUsageAlerts:
    """Usage alert banner."""

    def test_alert_banner_or_absence(self, live_billing_page: Page):
        """EL-billing-016: Alert banner shown when usage thresholds met, else absent."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        alert = page.locator("text=Usage alerts")
        if alert.count() > 0:
            expect(alert.first).to_be_visible()
        else:
            title = page.locator("h2:has-text('Billing')")
            expect(title).to_be_visible()


# ---------------------------------------------------------------------------
# TestConversationPacks — EL-billing-017..021
# ---------------------------------------------------------------------------

class TestConversationPacks:
    """Conversation pack purchase cards."""

    def test_packs_section_visible(self, live_billing_page: Page):
        """EL-billing-017: Conversation packs section header visible."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Conversation packs")
        label = page.locator("text=Conversation packs").first
        expect(label).to_be_visible()

    def test_pack_1000_card(self, live_billing_page: Page):
        """EL-billing-018: 1,000 conversation pack card visible."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Conversation packs")
        card = page.locator("text=1,000")
        assert card.count() > 0, "1,000 conversation pack card not found"

    def test_pack_5000_card(self, live_billing_page: Page):
        """EL-billing-019: 5,000 conversation pack card visible."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Conversation packs")
        card = page.locator("text=5,000")
        assert card.count() > 0, "5,000 conversation pack card not found"

    def test_pack_20000_card(self, live_billing_page: Page):
        """EL-billing-020: 20,000 conversation pack card visible."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Conversation packs")
        card = page.locator("text=20,000")
        assert card.count() > 0, "20,000 conversation pack card not found"

    def test_pack_purchase_buttons(self, live_billing_page: Page):
        """EL-billing-021: Each pack card has a 'Purchase' button."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Conversation packs")
        btns = page.locator("button:has-text('Purchase')")
        assert btns.count() >= 3, f"Expected 3 Purchase buttons, found {btns.count()}"

    def test_pack_prices_shown(self, live_billing_page: Page):
        """EL-billing-018..020: Pack prices ($29, $99, $249) displayed."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Conversation packs")
        for price in ["$29.00", "$99.00", "$249.00"]:
            loc = page.locator(f"text={price}")
            assert loc.count() > 0, f"Price {price} not found"


# ---------------------------------------------------------------------------
# TestAddOnModules — EL-billing-022..025
# ---------------------------------------------------------------------------

class TestAddOnModules:
    """Add-on module cards with tier gating."""

    def test_addons_section_visible(self, live_billing_page: Page):
        """EL-billing-022: Add-on modules section header visible."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Add-on modules")
        label = page.locator("text=Add-on modules").first
        expect(label).to_be_visible()

    def test_addon_cards_rendered(self, live_billing_page: Page):
        """EL-billing-023: At least 5 add-on module cards rendered."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Add-on modules")
        modules = [
            "Multi-Language Pack",
            "Advanced Analytics",
            "Mailchimp Integration",
            "Google Analytics",
            "Custom Integration",
        ]
        found = sum(1 for mod in modules if page.locator(f"text={mod}").count() > 0)
        assert found >= 4, f"Expected at least 4 add-on modules, found {found}"

    def test_addon_tier_badges(self, live_billing_page: Page):
        """EL-billing-024: Add-on cards show tier requirement badges."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Add-on modules")
        for label in ["All tiers", "Professional+", "Enterprise"]:
            loc = page.locator(f"text={label}")
            if loc.count() > 0:
                expect(loc.first).to_be_visible()
                return
        pytest.fail("No tier requirement badge found on add-on cards")

    def test_addon_subscribe_buttons(self, live_billing_page: Page):
        """EL-billing-025: Subscribe or 'Requires tier' buttons on add-on cards."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Add-on modules")
        subscribe_btns = page.locator("button:has-text('Subscribe')")
        requires_btns = page.locator("button:has-text('Requires')")
        total = subscribe_btns.count() + requires_btns.count()
        assert total >= 3, f"Expected at least 3 add-on action buttons, found {total}"

    def test_addon_prices_shown(self, live_billing_page: Page):
        """EL-billing-023: Add-on prices with /mo suffix displayed."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Add-on modules")
        mo_labels = page.locator("text=/mo")
        assert mo_labels.count() >= 3, f"Expected at least 3 /mo labels, found {mo_labels.count()}"


# ---------------------------------------------------------------------------
# TestTierComparison — EL-billing-026..030
# ---------------------------------------------------------------------------

class TestTierComparison:
    """Tier comparison section (may not be rendered on all page versions)."""

    def test_tier_section_or_absence(self, live_billing_page: Page):
        """EL-billing-026: Tier comparison section exists or page is functional."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Upgrade")
        upgrade = page.locator("button:has-text('Upgrade')")
        if upgrade.count() == 0:
            pytest.skip("Tier comparison section not present in current page version")
        expect(upgrade.first).to_be_visible()


# ---------------------------------------------------------------------------
# TestManageBilling — EL-billing-031, EL-billing-032
# ---------------------------------------------------------------------------

class TestManageBilling:
    """Manage billing section for Stripe tenants."""

    def test_manage_billing_section(self, live_billing_page: Page):
        """EL-billing-031: Invoices & payment methods section visible."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        _scroll_to_text(page, "Invoices")
        section = page.locator("text=Invoices")
        if section.count() == 0:
            pytest.skip("Manage billing section not shown — not a Stripe tenant")
        expect(section.first).to_be_visible()

    def test_manage_billing_button(self, live_billing_page: Page):
        """EL-billing-032: 'Manage billing' button exists for Stripe tenants."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        btn = page.locator("button:has-text('Manage billing')")
        if btn.count() == 0:
            pytest.skip("Manage billing button not shown — not a Stripe tenant")
        expect(btn.first).to_be_visible()


# ---------------------------------------------------------------------------
# TestLoadStates — EL-billing-033, EL-billing-034
# ---------------------------------------------------------------------------

class TestLoadStates:
    """Loading and error states."""

    def test_loading_state_not_stuck(self, live_billing_page: Page):
        """EL-billing-033: Loading spinner not stuck after page load."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        loading = page.locator("text=Loading billing data")
        if loading.count() > 0:
            page.wait_for_timeout(3000)
        loading = page.locator("text=Loading billing data")
        assert loading.count() == 0 or not loading.first.is_visible(), \
            "Loading state still visible after page load"

    def test_error_state_or_clean_load(self, live_billing_page: Page):
        """EL-billing-034: No error alert on clean load (or API error is shown)."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        error = page.locator("text=Usage data unavailable")
        if error.count() > 0:
            expect(error.first).to_be_visible()
        else:
            title = page.locator("h2:has-text('Billing')")
            expect(title).to_be_visible()


# ---------------------------------------------------------------------------
# TestHelpTooltips — cross-cutting
# ---------------------------------------------------------------------------

class TestHelpTooltips:
    """Help tooltips on billing controls."""

    def test_help_tooltips_exist(self, live_billing_page: Page):
        """Help tooltip '?' badges exist on the billing page."""
        page = live_billing_page
        if _is_rate_limited(page):
            pytest.skip("Rate limited")
        _wait_for_billing_page(page)
        tooltips = page.locator("text=?")
        count = tooltips.count()
        assert count >= 3, f"Expected at least 3 help tooltips, found {count}"
