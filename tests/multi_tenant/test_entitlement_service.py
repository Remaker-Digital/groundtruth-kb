"""Tests for the EntitlementService (SPEC-1815, WI-1407).

Validates:
  - Frozen fallback returns correct values for all tiers
  - Tier ordering and gate resolution
  - Cache layering (LRU → Redis → Cosmos)
  - Field gate and integration gate lookups
  - Feature allowed checks
  - Cache invalidation
  - Singleton lifecycle

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.entitlement_service import (
    FROZEN_ENTITLEMENTS,
    TIER_ORDER,
    EntitlementService,
    _resolve_gate,
    get_entitlement_service,
    reset_entitlement_service,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def svc() -> EntitlementService:
    """Fresh EntitlementService instance (no Cosmos/Redis)."""
    return EntitlementService()


@pytest.fixture
async def initialized_svc() -> EntitlementService:
    """EntitlementService with initialize() called (no external deps)."""
    svc = EntitlementService()
    await svc.initialize()
    return svc


@pytest.fixture
def mock_redis() -> MagicMock:
    """Mock Redis client with basic get/set/delete/scan/publish."""
    client = MagicMock()
    client.get.return_value = None
    client.ping.return_value = True
    client.scan.return_value = (0, [])
    return client


@pytest.fixture
def mock_cosmos_repo() -> AsyncMock:
    """Mock PlatformConfigRepository."""
    repo = AsyncMock()
    repo.get_config.return_value = None
    repo.set_config.return_value = {}
    repo.list_by_type.return_value = []
    return repo


# ---------------------------------------------------------------------------
# SPEC-1815: Frozen fallback
# ---------------------------------------------------------------------------


class TestFrozenFallback:
    """SPEC-1815: Frozen entitlements provide correct fallback values."""

    @pytest.mark.asyncio
    async def test_frozen_has_all_tiers(self, svc: EntitlementService):
        """SPEC-1814: All 4 tiers present in frozen snapshot."""
        for tier in ("trial", "starter", "professional", "enterprise"):
            config = await svc.get_tier_config(tier)
            assert config is not None, f"Missing frozen config for {tier}"
            assert "included_conversations" in config
            assert "memory_layers" in config
            assert "rate_limit_rpm" in config

    @pytest.mark.asyncio
    async def test_frozen_tier_conversations(self, svc: EntitlementService):
        """SPEC-1814: Frozen tier conversation limits match hardcoded values."""
        expected = {
            "trial": 5_000,
            "starter": 1_000,
            "professional": 5_000,
            "enterprise": 20_000,
        }
        for tier, count in expected.items():
            config = await svc.get_tier_config(tier)
            assert config["included_conversations"] == count, (
                f"{tier}: expected {count}, got {config['included_conversations']}"
            )

    @pytest.mark.asyncio
    async def test_frozen_memory_layers(self, svc: EntitlementService):
        """SPEC-1814: Frozen memory layers match tier entitlements."""
        expected = {
            "trial": [1, 2, 3],
            "starter": [1, 2],
            "professional": [1, 2, 3],
            "enterprise": [1, 2, 3, 4],
        }
        for tier, layers in expected.items():
            config = await svc.get_tier_config(tier)
            assert config["memory_layers"] == layers

    @pytest.mark.asyncio
    async def test_frozen_rate_limits(self, svc: EntitlementService):
        """SPEC-1803: All tiers have 300 RPM rate limit."""
        for tier in ("trial", "starter", "professional", "enterprise"):
            rpm = await svc.get_rate_limit(tier)
            assert rpm == 300

    @pytest.mark.asyncio
    async def test_frozen_pricing(self, svc: EntitlementService):
        """SPEC-1814: Frozen pricing matches canonical TIER_PRICING."""
        pricing = await svc.get_pricing("starter")
        assert pricing["monthly_fee"] == 149.0
        assert pricing["annual_monthly_fee"] == 124.0
        assert pricing["overage_rate"] == 0.04

        pricing = await svc.get_pricing("enterprise")
        assert pricing["monthly_fee"] == 999.0
        assert pricing["included_conversations"] == 20_000

    @pytest.mark.asyncio
    async def test_frozen_sla_targets(self, svc: EntitlementService):
        """SPEC-1814: SLA targets available via frozen fallback."""
        sla = await svc.get_sla_targets("professional")
        assert sla["uptime_pct"] == 99.9
        assert sla["rto_hours"] == 8

        sla = await svc.get_sla_targets("enterprise")
        assert sla["uptime_pct"] == 99.95
        assert sla["rto_hours"] == 4

    @pytest.mark.asyncio
    async def test_frozen_website_limits(self, svc: EntitlementService):
        """SPEC-1814: Website crawl limits per tier."""
        limits = await svc.get_website_limits("starter")
        assert limits["max_sources"] == 3
        assert limits["max_pages"] == 25

        limits = await svc.get_website_limits("enterprise")
        assert limits["max_sources"] == 25
        assert limits["max_pages"] == 100

    @pytest.mark.asyncio
    async def test_frozen_global_config(self, svc: EntitlementService):
        """SPEC-1814: Global config values accessible."""
        config = await svc.get_global_config()
        assert config["rate_limit_rpm_default"] == 300
        assert config["rate_limit_rpm_floor"] == 10
        assert config["stripe_fee_pct"] == 0.029

    @pytest.mark.asyncio
    async def test_frozen_pack_pricing(self, svc: EntitlementService):
        """SPEC-1814: Conversation pack pricing."""
        packs = await svc.get_pack_pricing()
        assert packs["1000"] == 29.0
        assert packs["5000"] == 99.0
        assert packs["20000"] == 249.0

    @pytest.mark.asyncio
    async def test_unknown_tier_returns_starter(self, svc: EntitlementService):
        """Unknown tiers fall back to starter defaults."""
        config = await svc.get_tier_config("nonexistent")
        assert config["included_conversations"] == 1_000  # starter default


# ---------------------------------------------------------------------------
# SPEC-1815: Tier ordering and gate resolution
# ---------------------------------------------------------------------------


class TestTierOrdering:
    """SPEC-1815: Tier ordering and gate resolution."""

    def test_tier_order_values(self):
        """Tier ordering: trial < starter < professional < enterprise."""
        assert TIER_ORDER["trial"] < TIER_ORDER["starter"]
        assert TIER_ORDER["starter"] < TIER_ORDER["professional"]
        assert TIER_ORDER["professional"] < TIER_ORDER["enterprise"]

    def test_resolve_gate_aliases(self):
        """Gate aliases resolve correctly."""
        assert _resolve_gate("pro+") == "professional"
        assert _resolve_gate("all") == "trial"
        assert _resolve_gate("enterprise") == "enterprise"
        assert _resolve_gate("starter") == "starter"

    def test_tier_meets_minimum(self, svc: EntitlementService):
        """tier_meets_minimum correctly compares tier levels."""
        # Enterprise meets everything
        assert svc.tier_meets_minimum("trial", "enterprise")
        assert svc.tier_meets_minimum("starter", "enterprise")
        assert svc.tier_meets_minimum("professional", "enterprise")
        assert svc.tier_meets_minimum("enterprise", "enterprise")

        # Starter doesn't meet professional
        assert not svc.tier_meets_minimum("professional", "starter")
        assert not svc.tier_meets_minimum("enterprise", "starter")

        # Trial meets only trial
        assert svc.tier_meets_minimum("trial", "trial")
        assert not svc.tier_meets_minimum("starter", "trial")

    def test_tier_meets_minimum_with_aliases(self, svc: EntitlementService):
        """Gate aliases work in tier_meets_minimum."""
        assert svc.tier_meets_minimum("pro+", "enterprise")
        assert svc.tier_meets_minimum("all", "starter")
        assert not svc.tier_meets_minimum("pro+", "starter")


# ---------------------------------------------------------------------------
# SPEC-1815: Integration and field gates
# ---------------------------------------------------------------------------


class TestGates:
    """SPEC-1815: Integration and field gate lookups."""

    @pytest.mark.asyncio
    async def test_integration_gates(self, svc: EntitlementService):
        """Integration gates return correct minimum tiers."""
        assert await svc.get_integration_gate("shopify") == "trial"
        assert await svc.get_integration_gate("zendesk") == "professional"
        assert await svc.get_integration_gate("stripe") == "professional"

    @pytest.mark.asyncio
    async def test_field_gates(self, svc: EntitlementService):
        """Field gates return correct minimum tiers."""
        assert await svc.get_field_gate("dedicated_model_enabled") == "enterprise"
        assert await svc.get_field_gate("pattern_learning_enabled") == "professional"
        assert await svc.get_field_gate("unknown_field") == "trial"

    @pytest.mark.asyncio
    async def test_is_feature_allowed(self, svc: EntitlementService):
        """is_feature_allowed combines integration and field gates."""
        # Shopify available to all
        assert await svc.is_feature_allowed("shopify", "trial")
        assert await svc.is_feature_allowed("shopify", "starter")

        # Zendesk requires professional
        assert not await svc.is_feature_allowed("zendesk", "starter")
        assert await svc.is_feature_allowed("zendesk", "professional")
        assert await svc.is_feature_allowed("zendesk", "enterprise")

        # Dedicated model requires enterprise
        assert not await svc.is_feature_allowed("dedicated_model_enabled", "professional")
        assert await svc.is_feature_allowed("dedicated_model_enabled", "enterprise")


# ---------------------------------------------------------------------------
# SPEC-1815: Cache layering
# ---------------------------------------------------------------------------


class TestCacheLayering:
    """SPEC-1815: Three-tier cache (LRU → Redis → Cosmos)."""

    @pytest.mark.asyncio
    async def test_lru_cache_hit(self, svc: EntitlementService):
        """LRU cache returns value without hitting Redis/Cosmos."""
        svc._lru_set("tier_config:professional", {"rate_limit_rpm": 999})
        value = await svc._get_cached("tier_config", "professional")
        assert value == {"rate_limit_rpm": 999}

    @pytest.mark.asyncio
    async def test_redis_cache_hit(self, svc: EntitlementService, mock_redis: MagicMock):
        """Redis hit populates LRU and returns value."""
        svc._redis_client = mock_redis
        mock_redis.get.return_value = json.dumps({"rate_limit_rpm": 500})

        value = await svc._get_cached("tier_config", "professional")
        assert value == {"rate_limit_rpm": 500}

        # LRU should now be populated
        assert svc._lru_get("tier_config:professional") == {"rate_limit_rpm": 500}

    @pytest.mark.asyncio
    async def test_cosmos_cache_hit(
        self,
        svc: EntitlementService,
        mock_redis: MagicMock,
        mock_cosmos_repo: AsyncMock,
    ):
        """Cosmos hit populates both Redis and LRU."""
        svc._redis_client = mock_redis
        svc._cosmos_repo = mock_cosmos_repo
        mock_cosmos_repo.get_config.return_value = {
            "value": {"rate_limit_rpm": 400},
        }

        value = await svc._get_cached("tier_config", "professional")
        assert value == {"rate_limit_rpm": 400}

        # Both caches populated
        assert svc._lru_get("tier_config:professional") == {"rate_limit_rpm": 400}
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_all_miss_returns_none(
        self,
        svc: EntitlementService,
        mock_redis: MagicMock,
        mock_cosmos_repo: AsyncMock,
    ):
        """All three tiers miss → returns None."""
        svc._redis_client = mock_redis
        svc._cosmos_repo = mock_cosmos_repo

        value = await svc._get_cached("nonexistent", "key")
        assert value is None


# ---------------------------------------------------------------------------
# SPEC-1815: Cache invalidation
# ---------------------------------------------------------------------------


class TestCacheInvalidation:
    """SPEC-1815: Cache invalidation clears LRU and Redis."""

    def test_invalidate_lru_full(self, svc: EntitlementService):
        """Full flush clears all LRU entries."""
        svc._lru_set("a", 1)
        svc._lru_set("b", 2)
        svc.invalidate_cache()
        assert svc._lru_get("a") is None
        assert svc._lru_get("b") is None

    def test_invalidate_lru_specific(self, svc: EntitlementService):
        """Specific key invalidation only clears matching entries."""
        svc._lru_set("tier_config:starter", 1)
        svc._lru_set("tier_config:professional", 2)
        svc._lru_set("entitlements:pricing", 3)

        svc.invalidate_cache("tier_config")
        assert svc._lru_get("tier_config:starter") is None
        assert svc._lru_get("tier_config:professional") is None
        assert svc._lru_get("entitlements:pricing") == 3

    @pytest.mark.asyncio
    async def test_invalidate_redis_publishes(self, svc: EntitlementService, mock_redis: MagicMock):
        """Redis invalidation publishes to invalidation channel."""
        svc._redis_client = mock_redis

        await svc.invalidate_redis("tier_config:starter")
        mock_redis.delete.assert_called_once()
        mock_redis.publish.assert_called_once()


# ---------------------------------------------------------------------------
# SPEC-1815: Singleton lifecycle
# ---------------------------------------------------------------------------


class TestSingleton:
    """EntitlementService singleton lifecycle."""

    def test_get_returns_same_instance(self):
        """get_entitlement_service returns the same singleton."""
        reset_entitlement_service()
        a = get_entitlement_service()
        b = get_entitlement_service()
        assert a is b
        reset_entitlement_service()

    def test_reset_clears_instance(self):
        """reset_entitlement_service creates a new instance."""
        a = get_entitlement_service()
        reset_entitlement_service()
        b = get_entitlement_service()
        assert a is not b
        reset_entitlement_service()

    @pytest.mark.asyncio
    async def test_initialized_flag(self, svc: EntitlementService):
        """is_initialized tracks initialization state."""
        assert not svc.is_initialized
        await svc.initialize()
        assert svc.is_initialized


# ---------------------------------------------------------------------------
# SPEC-1814: Entitlement document schema completeness
# ---------------------------------------------------------------------------


class TestEntitlementDocumentSchema:
    """SPEC-1814: Entitlement document schema v1 is complete."""

    def test_frozen_has_required_sections(self):
        """All required sections present in FROZEN_ENTITLEMENTS."""
        required_keys = [
            "schema_version",
            "tier_order",
            "tiers",
            "pricing",
            "pack_pricing",
            "sla_targets",
            "website_limits",
            "integration_gates",
            "field_gates",
            "global_config",
        ]
        for key in required_keys:
            assert key in FROZEN_ENTITLEMENTS, f"Missing required key: {key}"

    def test_schema_version_is_1(self):
        """Schema version is 1."""
        assert FROZEN_ENTITLEMENTS["schema_version"] == 1

    def test_tiers_have_consistent_fields(self):
        """All tier configs have the same set of fields."""
        tiers = FROZEN_ENTITLEMENTS["tiers"]
        # Get field sets (exclude trial-specific fields)
        common_fields = {"label", "description", "included_conversations",
                         "memory_layers", "overage_rate", "rate_limit_rpm",
                         "token_exhaustion_limit"}

        for tier_name, tier_data in tiers.items():
            tier_fields = set(tier_data.keys())
            missing = common_fields - tier_fields
            assert not missing, (
                f"Tier {tier_name} missing fields: {missing}"
            )

    def test_pricing_consistent_with_tiers(self):
        """Pricing tiers align with main tiers (excluding trial)."""
        paid_tiers = {"starter", "professional", "enterprise"}
        pricing_tiers = set(FROZEN_ENTITLEMENTS["pricing"].keys())
        assert pricing_tiers == paid_tiers

    def test_sla_targets_have_required_metrics(self):
        """SLA targets include uptime, latency, and RTO."""
        required_metrics = {"uptime_pct", "p50_ms", "p95_ms", "p99_ms", "rto_hours"}
        for tier, targets in FROZEN_ENTITLEMENTS["sla_targets"].items():
            missing = required_metrics - set(targets.keys())
            assert not missing, f"SLA {tier} missing: {missing}"

    def test_website_limits_have_required_fields(self):
        """Website limits include sources, pages, refresh."""
        required_fields = {"max_sources", "max_pages", "min_refresh_hours"}
        for tier, limits in FROZEN_ENTITLEMENTS["website_limits"].items():
            missing = required_fields - set(limits.keys())
            assert not missing, f"Website limits {tier} missing: {missing}"

    def test_integration_gates_match_known_integrations(self):
        """Integration gates cover all known integrations."""
        known = {"shopify", "zendesk", "mailchimp", "google_analytics", "stripe"}
        gates = set(FROZEN_ENTITLEMENTS["integration_gates"].keys())
        assert gates == known

    def test_field_gates_match_known_gated_fields(self):
        """Field gates cover all known tier-gated fields."""
        known = {
            "zendesk_escalation_enabled",
            "mailchimp_segment_sync",
            "google_analytics_enabled",
            "pattern_learning_enabled",
            "dedicated_model_enabled",
        }
        gates = set(FROZEN_ENTITLEMENTS["field_gates"].keys())
        assert gates == known
