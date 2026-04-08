"""
Parameterized cost model calculator.

Implements WI #155: Cost model calculator — projects infrastructure and
AI costs at different tenant/volume scenarios. Used by operations team
for capacity planning and by the billing system for margin validation.

Cost basis (validated Jan 2026 architecture review):
    - Per-conversation AI cost: ~$0.0073
    - GPT-4o response generation: 94.5% of AI cost
    - Shared infrastructure (10+ tenants): ~$252-436/mo
    - Per-tenant marginal: ~$13-41/mo
    - Gross margin at list price: 76-90%

Pricing structure:
    - Starter:      $149/mo, 1,000 included, $0.04/conv overage
    - Professional:  $399/mo, 5,000 included, $0.025/conv overage
    - Enterprise:   $999/mo, 20,000 included, $0.015/conv overage

Architecture references:
    - Decision #27: Cost basis validation, margin analysis
    - WI #82: Parameterized cost model (Master Plan)
    - WI #155: Cost model calculator (Backlog — supersedes #82)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from src.multi_tenant.entitlement_service import FROZEN_ENTITLEMENTS, get_entitlement_service

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants — cost basis
# ---------------------------------------------------------------------------

# Per-conversation AI cost breakdown (validated Jan 2026)
AI_COST_PER_CONVERSATION = 0.0073
AI_COST_BREAKDOWN = {
    "response_generator_gpt4o": 0.0069,  # 94.5% of total
    "intent_classifier_gpt4o_mini": 0.00015,
    "knowledge_retrieval_embedding": 0.0001,
    "critic_supervisor_gpt4o_mini": 0.00015,
    "cosmos_db_ru": 0.0001,
}

# Shared infrastructure cost range (monthly, 10+ tenants)
INFRA_COST_LOW = 252.0
INFRA_COST_HIGH = 436.0

# Per-tenant marginal infrastructure cost range
PER_TENANT_MARGINAL_LOW = 13.0
PER_TENANT_MARGINAL_HIGH = 41.0

# Tier pricing — loaded from EntitlementService (data-driven via Cosmos DB).
# Falls back to frozen entitlements when backends are unavailable.

def _get_tier_pricing() -> dict[str, dict[str, Any]]:
    """Load tier pricing from EntitlementService (sync, LRU/frozen fallback)."""
    svc = get_entitlement_service()
    result: dict[str, dict[str, Any]] = {}
    for tier in ("starter", "professional", "enterprise"):
        result[tier] = svc.get_pricing_sync(tier)
    return result


def _get_pack_pricing() -> dict[int, float]:
    """Load pack pricing from EntitlementService (sync, LRU/frozen fallback)."""
    svc = get_entitlement_service()
    raw = svc.get_pack_pricing_sync()
    return {int(k): float(v) for k, v in raw.items()}

# Stripe processing fee
STRIPE_FEE_PCT = 0.029
STRIPE_FEE_FIXED = 0.30
STRIPE_TAX_FEE = 0.50  # Per Stripe Tax transaction

# Re-export from entitlement config for backward compat (used by performance tests)
TIER_PRICING: dict[str, dict] = FROZEN_ENTITLEMENTS["pricing"]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TenantCostProjection:
    """Cost and revenue projection for a single tenant."""

    tier: str
    billing_interval: str  # "monthly" or "annual"
    conversations_per_month: int
    included_conversations: int
    overage_conversations: int

    # Revenue
    platform_fee: float
    overage_revenue: float
    total_revenue: float

    # Costs
    ai_cost: float
    marginal_infra_cost: float
    stripe_fee: float
    stripe_tax_fee: float
    total_cost: float

    # Margin
    gross_profit: float
    gross_margin_pct: float


@dataclass(frozen=True)
class PlatformCostProjection:
    """Cost and revenue projection for the entire platform."""

    tenant_count: int
    tenant_mix: dict[str, int]  # tier -> count
    total_conversations: int

    # Revenue
    total_platform_fees: float
    total_overage_revenue: float
    total_pack_revenue: float
    total_revenue: float

    # Costs
    total_ai_cost: float
    shared_infra_cost: float
    total_marginal_infra_cost: float
    total_stripe_fees: float
    total_cost: float

    # Margin
    gross_profit: float
    gross_margin_pct: float

    # Per-tenant breakdown
    per_tenant: list[TenantCostProjection]

    # Break-even
    break_even_tenants: int


# ---------------------------------------------------------------------------
# CostModelCalculator
# ---------------------------------------------------------------------------


class CostModelCalculator:
    """Projects costs and revenue for capacity planning.

    All calculations use validated cost basis from the Jan 2026
    architecture review. Supports scenario modeling for different
    tenant counts, conversation volumes, and tier mixes.
    """

    def project_tenant(
        self,
        tier: str,
        conversations_per_month: int,
        billing_interval: str = "monthly",
    ) -> TenantCostProjection:
        """Project costs and revenue for a single tenant.

        Args:
            tier: Tenant tier (starter, professional, enterprise).
            conversations_per_month: Expected monthly conversation volume.
            billing_interval: "monthly" or "annual".

        Returns:
            TenantCostProjection with revenue, cost, and margin details.
        """
        tier_pricing = _get_tier_pricing()
        pricing = tier_pricing.get(tier, tier_pricing["starter"])

        if billing_interval == "annual":
            platform_fee = pricing["annual_monthly_fee"]
        else:
            platform_fee = pricing["monthly_fee"]

        included = pricing["included_conversations"]
        overage_convs = max(0, conversations_per_month - included)
        overage_revenue = overage_convs * pricing["overage_rate"]
        total_revenue = platform_fee + overage_revenue

        # Costs
        ai_cost = conversations_per_month * AI_COST_PER_CONVERSATION
        marginal_infra = (PER_TENANT_MARGINAL_LOW + PER_TENANT_MARGINAL_HIGH) / 2
        stripe_fee = total_revenue * STRIPE_FEE_PCT + STRIPE_FEE_FIXED
        tax_fee = STRIPE_TAX_FEE  # One Stripe Tax transaction per billing cycle
        total_cost = ai_cost + marginal_infra + stripe_fee + tax_fee

        gross_profit = total_revenue - total_cost
        margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

        return TenantCostProjection(
            tier=tier,
            billing_interval=billing_interval,
            conversations_per_month=conversations_per_month,
            included_conversations=included,
            overage_conversations=overage_convs,
            platform_fee=round(platform_fee, 2),
            overage_revenue=round(overage_revenue, 2),
            total_revenue=round(total_revenue, 2),
            ai_cost=round(ai_cost, 2),
            marginal_infra_cost=round(marginal_infra, 2),
            stripe_fee=round(stripe_fee, 2),
            stripe_tax_fee=round(tax_fee, 2),
            total_cost=round(total_cost, 2),
            gross_profit=round(gross_profit, 2),
            gross_margin_pct=round(margin_pct, 1),
        )

    def project_platform(
        self,
        tenant_mix: dict[str, int],
        avg_conversations: dict[str, int] | None = None,
        billing_interval: str = "monthly",
        pack_revenue: float = 0.0,
    ) -> PlatformCostProjection:
        """Project costs and revenue for the entire platform.

        Args:
            tenant_mix: Tier -> tenant count mapping.
            avg_conversations: Tier -> avg monthly conversations.
                Defaults to included allowance per tier.
            billing_interval: Default billing interval for all tenants.
            pack_revenue: Additional revenue from conversation pack sales.

        Returns:
            PlatformCostProjection with aggregate and per-tenant details.
        """
        tier_pricing = _get_tier_pricing()
        if avg_conversations is None:
            avg_conversations = {
                tier: tier_pricing.get(tier, tier_pricing["starter"])[
                    "included_conversations"
                ]
                for tier in tenant_mix
            }

        per_tenant: list[TenantCostProjection] = []
        total_convs = 0

        for tier, count in tenant_mix.items():
            convs = avg_conversations.get(
                tier,
                tier_pricing.get(tier, tier_pricing["starter"])[
                    "included_conversations"
                ],
            )
            for _ in range(count):
                projection = self.project_tenant(tier, convs, billing_interval)
                per_tenant.append(projection)
                total_convs += convs

        total_platform_fees = sum(t.platform_fee for t in per_tenant)
        total_overage_revenue = sum(t.overage_revenue for t in per_tenant)
        total_revenue = total_platform_fees + total_overage_revenue + pack_revenue

        total_ai_cost = sum(t.ai_cost for t in per_tenant)
        total_marginal = sum(t.marginal_infra_cost for t in per_tenant)
        shared_infra = (INFRA_COST_LOW + INFRA_COST_HIGH) / 2
        total_stripe = sum(t.stripe_fee for t in per_tenant)
        total_cost = total_ai_cost + total_marginal + shared_infra + total_stripe

        gross_profit = total_revenue - total_cost
        margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

        # Break-even: minimum Starter tenants to cover shared infra
        starter_pricing = tier_pricing["starter"]
        starter_fee = starter_pricing["monthly_fee"]
        starter_marginal = (PER_TENANT_MARGINAL_LOW + PER_TENANT_MARGINAL_HIGH) / 2
        net_per_starter = starter_fee - starter_marginal - (
            starter_fee * STRIPE_FEE_PCT + STRIPE_FEE_FIXED
        ) - (starter_pricing["included_conversations"] * AI_COST_PER_CONVERSATION)
        break_even = int(shared_infra / net_per_starter) + 1 if net_per_starter > 0 else 999

        return PlatformCostProjection(
            tenant_count=sum(tenant_mix.values()),
            tenant_mix=tenant_mix,
            total_conversations=total_convs,
            total_platform_fees=round(total_platform_fees, 2),
            total_overage_revenue=round(total_overage_revenue, 2),
            total_pack_revenue=round(pack_revenue, 2),
            total_revenue=round(total_revenue, 2),
            total_ai_cost=round(total_ai_cost, 2),
            shared_infra_cost=round(shared_infra, 2),
            total_marginal_infra_cost=round(total_marginal, 2),
            total_stripe_fees=round(total_stripe, 2),
            total_cost=round(total_cost, 2),
            gross_profit=round(gross_profit, 2),
            gross_margin_pct=round(margin_pct, 1),
            per_tenant=per_tenant,
            break_even_tenants=break_even,
        )

    def scenario_break_even(self) -> dict[str, Any]:
        """Calculate break-even scenarios for different tier mixes.

        Returns summary of break-even tenant counts for common scenarios.
        """
        scenarios: dict[str, Any] = {}

        # Scenario 1: All Starter
        for count in range(1, 20):
            proj = self.project_platform({"starter": count})
            if proj.gross_profit >= 0:
                scenarios["all_starter_break_even"] = count
                scenarios["all_starter_margin"] = proj.gross_margin_pct
                break

        # Scenario 2: Mixed (60% Starter, 30% Pro, 10% Enterprise)
        for total in range(1, 50):
            mix = {
                "starter": max(1, int(total * 0.6)),
                "professional": max(0, int(total * 0.3)),
                "enterprise": max(0, int(total * 0.1)),
            }
            if sum(mix.values()) == 0:
                continue
            proj = self.project_platform(mix)
            if proj.gross_profit >= 0:
                scenarios["mixed_break_even"] = total
                scenarios["mixed_margin"] = proj.gross_margin_pct
                scenarios["mixed_mix"] = mix
                break

        # Scenario 3: Revenue at 10, 25, 50, 100 tenants (mixed)
        for target in [10, 25, 50, 100]:
            mix = {
                "starter": int(target * 0.6),
                "professional": int(target * 0.3),
                "enterprise": int(target * 0.1),
            }
            proj = self.project_platform(mix)
            scenarios[f"revenue_at_{target}_tenants"] = {
                "monthly_revenue": proj.total_revenue,
                "monthly_cost": proj.total_cost,
                "gross_profit": proj.gross_profit,
                "gross_margin_pct": proj.gross_margin_pct,
            }

        return scenarios


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

_calculator: CostModelCalculator | None = None


def get_cost_calculator() -> CostModelCalculator:
    """Get or create the module-level CostModelCalculator singleton."""
    global _calculator
    if _calculator is None:
        _calculator = CostModelCalculator()
    return _calculator
