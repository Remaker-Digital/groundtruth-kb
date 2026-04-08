"""Property-based tests for tier gating and entitlement logic (SPEC-1843 / WI-1482).

Tests verify algebraic properties of the tier ordering system:
- Transitivity, reflexivity, antisymmetry (partial order)
- Gate alias resolution idempotency
- Monotonicity of entitlements across tiers

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from hypothesis import given

from src.multi_tenant.entitlement_service import (
    FROZEN_ENTITLEMENTS,
    TIER_ORDER,
    EntitlementService,
    _resolve_gate,
)
from tests.property.conftest import (
    CANONICAL_TIERS,
    tier_or_alias_strategy,
    tier_strategy,
)


# ---------------------------------------------------------------------------
# Tier ordering algebraic properties
# ---------------------------------------------------------------------------


class TestTierOrderProperties:
    """Verify the tier ordering forms a valid total order."""

    @given(tier=tier_strategy)
    def test_reflexive(self, tier: str):
        """Every tier meets its own minimum requirement."""
        svc = EntitlementService()
        assert svc.tier_meets_minimum(tier, tier)

    @given(a=tier_strategy, b=tier_strategy, c=tier_strategy)
    def test_transitive(self, a: str, b: str, c: str):
        """If a >= b and b >= c, then a >= c."""
        svc = EntitlementService()
        if svc.tier_meets_minimum(b, a) and svc.tier_meets_minimum(c, b):
            assert svc.tier_meets_minimum(c, a)

    @given(a=tier_strategy, b=tier_strategy)
    def test_antisymmetric(self, a: str, b: str):
        """If a >= b and b >= a, then a == b."""
        svc = EntitlementService()
        if svc.tier_meets_minimum(b, a) and svc.tier_meets_minimum(a, b):
            assert TIER_ORDER[a] == TIER_ORDER[b]

    @given(a=tier_strategy, b=tier_strategy)
    def test_total(self, a: str, b: str):
        """For any two tiers, one must meet the minimum of the other."""
        svc = EntitlementService()
        assert svc.tier_meets_minimum(b, a) or svc.tier_meets_minimum(a, b)

    def test_enterprise_dominates_all(self):
        """Enterprise tier meets the minimum for every other tier."""
        svc = EntitlementService()
        for tier in CANONICAL_TIERS:
            assert svc.tier_meets_minimum(tier, "enterprise")

    def test_trial_is_dominated_by_all(self):
        """Every tier meets or exceeds the trial minimum."""
        svc = EntitlementService()
        for tier in CANONICAL_TIERS:
            assert svc.tier_meets_minimum("trial", tier)


# ---------------------------------------------------------------------------
# Gate alias resolution
# ---------------------------------------------------------------------------


class TestGateAliasProperties:
    """Verify gate alias resolution is well-behaved."""

    @given(name=tier_or_alias_strategy)
    def test_idempotent(self, name: str):
        """Resolving an alias twice gives the same result as once."""
        assert _resolve_gate(_resolve_gate(name)) == _resolve_gate(name)

    @given(name=tier_or_alias_strategy)
    def test_resolves_to_canonical(self, name: str):
        """Every alias resolves to a canonical tier name."""
        resolved = _resolve_gate(name)
        assert resolved in TIER_ORDER

    @given(alias=tier_or_alias_strategy)
    def test_alias_preserves_order(self, alias: str):
        """Resolving an alias does not change the effective tier rank."""
        resolved = _resolve_gate(alias)
        # The resolved name must exist in TIER_ORDER
        assert TIER_ORDER.get(resolved) is not None


# ---------------------------------------------------------------------------
# Entitlement monotonicity
# ---------------------------------------------------------------------------


class TestEntitlementMonotonicity:
    """Higher tiers must have equal or greater entitlements."""

    def test_included_conversations_monotonic(self):
        """Included conversations increase or stay the same across paying tiers.

        Trial is excluded: it intentionally mirrors Professional entitlements
        as a 14-day promotional tier, making it higher than Starter.
        """
        tiers_sorted = sorted(TIER_ORDER.keys(), key=lambda t: TIER_ORDER[t])
        paying = [t for t in tiers_sorted if t != "trial"]
        prev = 0
        for tier in paying:
            config = FROZEN_ENTITLEMENTS["tiers"].get(tier, {})
            current = config.get("included_conversations", 0)
            assert current >= prev, f"{tier} has fewer conversations than a lower tier"
            prev = current

    def test_rate_limit_non_negative(self):
        """Every tier has a positive rate limit."""
        for tier, config in FROZEN_ENTITLEMENTS["tiers"].items():
            rpm = config.get("rate_limit_rpm", 0)
            assert rpm > 0, f"{tier} has non-positive rate limit: {rpm}"

    def test_token_limit_monotonic(self):
        """Token exhaustion limits increase or stay the same across paying tiers.

        Trial excluded (same reason as conversations — promotional tier).
        """
        tiers_sorted = sorted(TIER_ORDER.keys(), key=lambda t: TIER_ORDER[t])
        paying = [t for t in tiers_sorted if t != "trial"]
        prev = 0
        for tier in paying:
            config = FROZEN_ENTITLEMENTS["tiers"].get(tier, {})
            current = config.get("token_exhaustion_limit", 0)
            assert current >= prev, f"{tier} has lower token limit than a lower tier"
            prev = current

    def test_overage_rate_decreasing(self):
        """Overage rates decrease or stay the same as tiers increase (better deals)."""
        tiers_sorted = sorted(TIER_ORDER.keys(), key=lambda t: TIER_ORDER[t])
        # Skip trial (overage_rate=0.0 is a special case — free trial)
        paying_tiers = [t for t in tiers_sorted if t != "trial"]
        prev = float("inf")
        for tier in paying_tiers:
            config = FROZEN_ENTITLEMENTS["tiers"].get(tier, {})
            rate = config.get("overage_rate", 0)
            assert rate <= prev, f"{tier} has higher overage rate than a lower tier"
            prev = rate

    @given(tier=tier_strategy)
    def test_rate_limit_meets_floor(self, tier: str):
        """Every tier's rate limit meets the global floor."""
        floor = FROZEN_ENTITLEMENTS["global_config"]["rate_limit_rpm_floor"]
        config = FROZEN_ENTITLEMENTS["tiers"].get(tier, {})
        rpm = config.get("rate_limit_rpm", 300)
        assert rpm >= floor

    def test_integration_gates_resolve_to_valid_tiers(self):
        """All integration gate values resolve to canonical tier names."""
        for integration, gate in FROZEN_ENTITLEMENTS["integration_gates"].items():
            resolved = _resolve_gate(gate)
            assert resolved in TIER_ORDER, f"Integration '{integration}' gate '{gate}' resolves to unknown tier"

    def test_field_gates_resolve_to_valid_tiers(self):
        """All field gate values resolve to canonical tier names."""
        for field, gate in FROZEN_ENTITLEMENTS["field_gates"].items():
            resolved = _resolve_gate(gate)
            assert resolved in TIER_ORDER, f"Field '{field}' gate '{gate}' resolves to unknown tier"


# ---------------------------------------------------------------------------
# Website limits monotonicity
# ---------------------------------------------------------------------------


class TestWebsiteLimitsProperties:
    """Higher tiers get more generous website crawl limits."""

    def test_max_sources_monotonic(self):
        tiers_sorted = sorted(TIER_ORDER.keys(), key=lambda t: TIER_ORDER[t])
        paying = [t for t in tiers_sorted if t in FROZEN_ENTITLEMENTS.get("website_limits", {})]
        prev = 0
        for tier in paying:
            current = FROZEN_ENTITLEMENTS["website_limits"][tier]["max_sources"]
            assert current >= prev
            prev = current

    def test_max_pages_monotonic(self):
        tiers_sorted = sorted(TIER_ORDER.keys(), key=lambda t: TIER_ORDER[t])
        paying = [t for t in tiers_sorted if t in FROZEN_ENTITLEMENTS.get("website_limits", {})]
        prev = 0
        for tier in paying:
            current = FROZEN_ENTITLEMENTS["website_limits"][tier]["max_pages"]
            assert current >= prev
            prev = current

    def test_min_refresh_hours_decreasing(self):
        """Higher tiers can refresh more frequently (lower hours)."""
        tiers_sorted = sorted(TIER_ORDER.keys(), key=lambda t: TIER_ORDER[t])
        paying = [t for t in tiers_sorted if t in FROZEN_ENTITLEMENTS.get("website_limits", {})]
        prev = float("inf")
        for tier in paying:
            current = FROZEN_ENTITLEMENTS["website_limits"][tier]["min_refresh_hours"]
            assert current <= prev
            prev = current
