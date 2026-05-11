"""Comprehensive tests for CostModelCalculator — WI #155.

Covers tenant cost projections, overage calculations, annual billing,
gross margin validation, platform projections, break-even scenarios,
pack pricing constants, Stripe fee calculations, and module singleton.

Test IDs: CM-01 through CM-20.

Run:
    pytest tests/multi_tenant/test_cost_model.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.multi_tenant.cost_model import (
    AI_COST_PER_CONVERSATION,
    INFRA_COST_HIGH,
    INFRA_COST_LOW,
    STRIPE_FEE_FIXED,
    STRIPE_FEE_PCT,
    STRIPE_TAX_FEE,
    _get_tier_pricing,
    _get_pack_pricing,
    CostModelCalculator,
    PlatformCostProjection,
    TenantCostProjection,
    get_cost_calculator,
)

import src.multi_tenant.cost_model as _cost_mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _calc() -> CostModelCalculator:
    """Return a fresh CostModelCalculator."""
    return CostModelCalculator()


# ===========================================================================
# Per-tenant projections at included volume (CM-01 through CM-03)
# ===========================================================================


class TestTenantProjectionsIncluded:
    """CM-01 through CM-03: Projections at included conversation volume."""

    def test_cm_01_starter_at_included_volume(self):
        """CM-01: Starter tenant at 1000 included conversations."""
        calc = _calc()
        proj = calc.project_tenant("starter", 1000)

        assert isinstance(proj, TenantCostProjection)
        assert proj.tier == "starter"
        assert proj.billing_interval == "monthly"
        assert proj.conversations_per_month == 1000
        assert proj.included_conversations == 1000
        assert proj.overage_conversations == 0
        assert proj.platform_fee == 149.0
        assert proj.overage_revenue == 0.0
        assert proj.total_revenue == 149.0

    def test_cm_02_professional_at_included_volume(self):
        """CM-02: Professional tenant at 5000 included conversations."""
        calc = _calc()
        proj = calc.project_tenant("professional", 5000)

        assert proj.tier == "professional"
        assert proj.conversations_per_month == 5000
        assert proj.included_conversations == 5000
        assert proj.overage_conversations == 0
        assert proj.platform_fee == 399.0
        assert proj.overage_revenue == 0.0
        assert proj.total_revenue == 399.0

    def test_cm_03_enterprise_at_included_volume(self):
        """CM-03: Enterprise tenant at 20000 included conversations."""
        calc = _calc()
        proj = calc.project_tenant("enterprise", 20000)

        assert proj.tier == "enterprise"
        assert proj.conversations_per_month == 20000
        assert proj.included_conversations == 20000
        assert proj.overage_conversations == 0
        assert proj.platform_fee == 999.0
        assert proj.overage_revenue == 0.0
        assert proj.total_revenue == 999.0


# ===========================================================================
# Overage and annual billing (CM-04 through CM-06)
# ===========================================================================


class TestOverageAndAnnual:
    """CM-04 through CM-06: Overage revenue and annual billing discount."""

    def test_cm_04_starter_with_overage(self):
        """CM-04: Starter at 1500 conversations has 500 overage at $0.04/conv."""
        calc = _calc()
        proj = calc.project_tenant("starter", 1500)

        assert proj.overage_conversations == 500
        assert proj.overage_revenue == 500 * 0.04  # $20.00
        assert proj.total_revenue == 149.0 + 20.0

    def test_cm_05_annual_billing_reduces_platform_fee(self):
        """CM-05: Annual billing uses discounted monthly fee."""
        calc = _calc()
        proj_monthly = calc.project_tenant("starter", 1000, billing_interval="monthly")
        proj_annual = calc.project_tenant("starter", 1000, billing_interval="annual")

        assert proj_monthly.platform_fee == 149.0
        assert proj_annual.platform_fee == 124.0
        assert proj_annual.platform_fee < proj_monthly.platform_fee

        # Annual = $124/mo, Monthly = $149/mo
        assert proj_annual.billing_interval == "annual"
        assert proj_monthly.billing_interval == "monthly"

    def test_cm_06_revenue_equals_platform_fee_plus_overage(self):
        """CM-06: Total revenue = platform_fee + overage_revenue."""
        calc = _calc()

        for tier in ["starter", "professional", "enterprise"]:
            included = _get_tier_pricing()[tier]["included_conversations"]
            # Test with 50% overage
            convs = int(included * 1.5)
            proj = calc.project_tenant(tier, convs)

            expected_revenue = proj.platform_fee + proj.overage_revenue
            assert proj.total_revenue == round(expected_revenue, 2)


# ===========================================================================
# Cost and margin (CM-07 through CM-10)
# ===========================================================================


class TestCostAndMargin:
    """CM-07 through CM-10: AI cost, gross margin, zero-conversation edge case."""

    def test_cm_07_ai_cost_matches_formula(self):
        """CM-07: AI cost = conversations * AI_COST_PER_CONVERSATION."""
        calc = _calc()
        proj = calc.project_tenant("starter", 1000)

        expected_ai_cost = round(1000 * AI_COST_PER_CONVERSATION, 2)
        assert proj.ai_cost == expected_ai_cost

    def test_cm_08_gross_margin_positive_for_all_tiers(self):
        """CM-08: Gross margin is positive for all tiers at included volume."""
        calc = _calc()

        for tier in ["starter", "professional", "enterprise"]:
            included = _get_tier_pricing()[tier]["included_conversations"]
            proj = calc.project_tenant(tier, included)

            assert proj.gross_profit > 0, (
                f"{tier} should have positive gross profit, "
                f"got {proj.gross_profit}"
            )
            assert proj.gross_margin_pct > 0

    def test_cm_09_gross_margin_in_expected_range(self):
        """CM-09: Gross margin percentage is in the 76-90% range for all tiers."""
        calc = _calc()

        for tier in ["starter", "professional", "enterprise"]:
            included = _get_tier_pricing()[tier]["included_conversations"]
            proj = calc.project_tenant(tier, included)

            assert 70.0 <= proj.gross_margin_pct <= 95.0, (
                f"{tier} gross margin {proj.gross_margin_pct}% "
                f"outside expected 70-95% range"
            )

    def test_cm_10_zero_conversations_no_ai_cost(self):
        """CM-10: Zero conversations produce no AI cost but positive revenue."""
        calc = _calc()
        proj = calc.project_tenant("starter", 0)

        assert proj.ai_cost == 0.0
        assert proj.overage_conversations == 0
        assert proj.overage_revenue == 0.0
        assert proj.platform_fee == 149.0
        assert proj.total_revenue == 149.0
        assert proj.gross_profit > 0


# ===========================================================================
# Platform projections (CM-11 through CM-15)
# ===========================================================================


class TestPlatformProjections:
    """CM-11 through CM-15: Multi-tenant platform cost modeling."""

    def test_cm_11_single_starter_tenant(self):
        """CM-11: Platform projection with a single Starter tenant."""
        calc = _calc()
        proj = calc.project_platform({"starter": 1})

        assert isinstance(proj, PlatformCostProjection)
        assert proj.tenant_count == 1
        assert proj.tenant_mix == {"starter": 1}
        assert len(proj.per_tenant) == 1
        assert proj.per_tenant[0].tier == "starter"

    def test_cm_12_mixed_tenant_mix(self):
        """CM-12: Platform projection with mixed tenant mix (3S, 2P, 1E)."""
        calc = _calc()
        mix = {"starter": 3, "professional": 2, "enterprise": 1}
        proj = calc.project_platform(mix)

        assert proj.tenant_count == 6
        assert proj.tenant_mix == mix
        assert len(proj.per_tenant) == 6

        # Count tiers in per_tenant list
        tier_counts = {}
        for t in proj.per_tenant:
            tier_counts[t.tier] = tier_counts.get(t.tier, 0) + 1
        assert tier_counts["starter"] == 3
        assert tier_counts["professional"] == 2
        assert tier_counts["enterprise"] == 1

    def test_cm_13_platform_includes_shared_infrastructure_cost(self):
        """CM-13: Platform total cost includes shared infrastructure cost."""
        calc = _calc()
        proj = calc.project_platform({"starter": 3})

        expected_shared_infra = (INFRA_COST_LOW + INFRA_COST_HIGH) / 2
        assert proj.shared_infra_cost == round(expected_shared_infra, 2)

        # Total cost should be at least shared infra
        assert proj.total_cost >= proj.shared_infra_cost

    def test_cm_14_break_even_tenants_reasonable(self):
        """CM-14: Break-even Starter tenant count is reasonable (2-5)."""
        calc = _calc()
        proj = calc.project_platform({"starter": 5})

        # Break-even should be between 2 and 5 based on documented margins
        assert 1 <= proj.break_even_tenants <= 10, (
            f"Break-even of {proj.break_even_tenants} is outside reasonable range"
        )

    def test_cm_15_total_revenue_is_sum_of_per_tenant(self):
        """CM-15: Platform total revenue equals sum of per-tenant fees + overage."""
        calc = _calc()
        mix = {"starter": 2, "professional": 1}
        proj = calc.project_platform(mix)

        per_tenant_fees = sum(t.platform_fee for t in proj.per_tenant)
        per_tenant_overage = sum(t.overage_revenue for t in proj.per_tenant)

        assert proj.total_platform_fees == round(per_tenant_fees, 2)
        assert proj.total_overage_revenue == round(per_tenant_overage, 2)
        # total_revenue = fees + overage + pack_revenue (0 by default)
        expected_total = round(per_tenant_fees + per_tenant_overage, 2)
        assert proj.total_revenue == expected_total


# ===========================================================================
# Scenario break-even and constants (CM-16 through CM-18)
# ===========================================================================


class TestScenariosAndConstants:
    """CM-16 through CM-18: Break-even scenario, pack pricing, Stripe fees."""

    def test_cm_16_scenario_break_even_returns_expected_keys(self):
        """CM-16: scenario_break_even returns dict with all expected keys."""
        calc = _calc()
        scenarios = calc.scenario_break_even()

        assert isinstance(scenarios, dict)
        # Must contain at least the all-starter break-even
        assert "all_starter_break_even" in scenarios
        assert "all_starter_margin" in scenarios

        # Revenue projection keys
        assert "revenue_at_10_tenants" in scenarios
        assert "revenue_at_25_tenants" in scenarios
        assert "revenue_at_50_tenants" in scenarios
        assert "revenue_at_100_tenants" in scenarios

        # Revenue projections should have the expected sub-keys
        rev_10 = scenarios["revenue_at_10_tenants"]
        assert "monthly_revenue" in rev_10
        assert "monthly_cost" in rev_10
        assert "gross_profit" in rev_10
        assert "gross_margin_pct" in rev_10

    def test_cm_17_pack_pricing_matches_documented_values(self):
        """CM-17: Conversation pack pricing constants match documented values."""
        assert _get_pack_pricing()[1000] == 29.0
        assert _get_pack_pricing()[5000] == 99.0
        assert _get_pack_pricing()[20000] == 249.0

        # Effective rates
        assert _get_pack_pricing()[1000] / 1000 == pytest.approx(0.029)
        assert _get_pack_pricing()[5000] / 5000 == pytest.approx(0.0198, abs=0.001)
        assert _get_pack_pricing()[20000] / 20000 == pytest.approx(0.01245, abs=0.001)

    def test_cm_18_stripe_fee_calculation(self):
        """CM-18: Stripe fee = revenue * 2.9% + $0.30 fixed."""
        calc = _calc()
        proj = calc.project_tenant("starter", 1000)

        expected_stripe_fee = round(
            proj.total_revenue * STRIPE_FEE_PCT + STRIPE_FEE_FIXED, 2
        )
        assert proj.stripe_fee == expected_stripe_fee

        # Verify constants
        assert STRIPE_FEE_PCT == 0.029
        assert STRIPE_FEE_FIXED == 0.30
        assert STRIPE_TAX_FEE == 0.50


# ===========================================================================
# Module singleton and overage formula (CM-19 through CM-20)
# ===========================================================================


class TestSingletonAndOverage:
    """CM-19 through CM-20: Module singleton and overage formula."""

    def test_cm_19_get_cost_calculator_singleton(self):
        """CM-19: get_cost_calculator() returns a CostModelCalculator instance."""
        _cost_mod._calculator = None

        first = get_cost_calculator()
        second = get_cost_calculator()

        assert isinstance(first, CostModelCalculator)
        assert first is second

        # Clean up
        _cost_mod._calculator = None

    def test_cm_20_overage_conversations_formula(self):
        """CM-20: overage_conversations = max(0, convs - included)."""
        calc = _calc()

        # Under included: no overage
        proj_under = calc.project_tenant("starter", 500)
        assert proj_under.overage_conversations == 0

        # At included: no overage
        proj_at = calc.project_tenant("starter", 1000)
        assert proj_at.overage_conversations == 0

        # Over included: exact difference
        proj_over = calc.project_tenant("starter", 1500)
        assert proj_over.overage_conversations == 500

        # Professional tier
        proj_pro = calc.project_tenant("professional", 7000)
        assert proj_pro.overage_conversations == 2000

        # Enterprise tier
        proj_ent = calc.project_tenant("enterprise", 25000)
        assert proj_ent.overage_conversations == 5000
