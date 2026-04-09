# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Centralized entitlement accessor — single source of truth for all tier config (SPEC-1815).

Replaces all hardcoded TIER_DEFAULTS, TIER_PRICING, _TIER_PRICING, TIER_FEATURES,
SLA_TARGETS, TIER_LIMITS, and tier_allowances with a data-driven system backed by
Cosmos DB ``platform_config`` container and cached via Redis (60s TTL) + in-process
LRU (5s TTL for hot paths).

Usage::

    from src.multi_tenant.entitlement_service import get_entitlement_service

    svc = get_entitlement_service()
    config = await svc.get_tier_config("professional")
    allowed = await svc.is_feature_allowed("zendesk", "starter")

When Cosmos and Redis are both unavailable, the service falls back to a frozen
snapshot (``FROZEN_ENTITLEMENTS``) compiled from the codebase values at the time
this module was written. This ensures the system never crashes due to missing
entitlement data — it degrades gracefully to known-good defaults.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tier ordering (canonical — single definition)
# ---------------------------------------------------------------------------

TIER_ORDER: dict[str, int] = {
    "trial": 0,
    "starter": 1,
    "professional": 2,
    "enterprise": 3,
}

# Gate aliases: "pro+" → "professional", "enterprise" → "enterprise", "all" → "trial"
_GATE_ALIASES: dict[str, str] = {
    "pro+": "professional",
    "all": "trial",
}


def _resolve_gate(gate: str) -> str:
    """Resolve gate alias to canonical tier name."""
    return _GATE_ALIASES.get(gate, gate)


# ---------------------------------------------------------------------------
# Frozen fallback — compiled from codebase hardcoded values
# ---------------------------------------------------------------------------

FROZEN_ENTITLEMENTS: dict[str, Any] = {
    "schema_version": 1,
    "tier_order": TIER_ORDER,

    "tiers": {
        "trial": {
            "label": "Trial",
            "description": "Full professional-grade entitlements for 14 days",
            "included_conversations": 5_000,
            "memory_layers": [1, 2, 3],
            "overage_rate": 0.0,
            "trial_duration_days": 14,
            "rate_limit_rpm": 300,
            "token_exhaustion_limit": 500_000,
        },
        "starter": {
            "label": "Starter",
            "description": "Essential AI support for growing businesses",
            "included_conversations": 1_000,
            "memory_layers": [1, 2],
            "overage_rate": 0.04,
            "rate_limit_rpm": 300,
            "token_exhaustion_limit": 100_000,
        },
        "professional": {
            "label": "Professional",
            "description": "Advanced AI with integrations and analytics",
            "included_conversations": 5_000,
            "memory_layers": [1, 2, 3],
            "overage_rate": 0.025,
            "rate_limit_rpm": 300,
            "token_exhaustion_limit": 500_000,
        },
        "enterprise": {
            "label": "Enterprise",
            "description": "Full platform with dedicated support",
            "included_conversations": 20_000,
            "memory_layers": [1, 2, 3, 4],
            "overage_rate": 0.015,
            "rate_limit_rpm": 300,
            "token_exhaustion_limit": 2_000_000,
        },
    },

    "pricing": {
        "starter": {
            "monthly_fee": 149.0,
            "annual_monthly_fee": 124.0,
            "annual_total": 1490.0,
            "overage_rate": 0.04,
            "included_conversations": 1_000,
            "capped_amount": 500.0,
        },
        "professional": {
            "monthly_fee": 399.0,
            "annual_monthly_fee": 332.0,
            "annual_total": 3990.0,
            "overage_rate": 0.025,
            "included_conversations": 5_000,
            "capped_amount": 1000.0,
        },
        "enterprise": {
            "monthly_fee": 999.0,
            "annual_monthly_fee": 832.0,
            "annual_total": 9990.0,
            "overage_rate": 0.015,
            "included_conversations": 20_000,
            "capped_amount": 2000.0,
        },
    },

    "pack_pricing": {
        "1000": 29.0,
        "5000": 99.0,
        "20000": 249.0,
    },

    "sla_targets": {
        "starter": {
            "uptime_pct": 99.5,
            "p50_ms": 1500,
            "p95_ms": 2000,
            "p99_ms": 5000,
            "rto_hours": 24,
        },
        "professional": {
            "uptime_pct": 99.9,
            "p50_ms": 1500,
            "p95_ms": 2000,
            "p99_ms": 5000,
            "rto_hours": 8,
        },
        "enterprise": {
            "uptime_pct": 99.95,
            "p50_ms": 1500,
            "p95_ms": 2000,
            "p99_ms": 5000,
            "rto_hours": 4,
        },
    },

    "website_limits": {
        "starter": {"max_sources": 3, "max_pages": 25, "min_refresh_hours": 24},
        "professional": {"max_sources": 10, "max_pages": 50, "min_refresh_hours": 12},
        "enterprise": {"max_sources": 25, "max_pages": 100, "min_refresh_hours": 6},
    },

    "integration_gates": {
        "shopify": "trial",
        "zendesk": "professional",
        "mailchimp": "professional",
        "google_analytics": "professional",
        "stripe": "professional",
    },

    "field_gates": {
        "zendesk_escalation_enabled": "professional",
        "mailchimp_segment_sync": "professional",
        "google_analytics_enabled": "professional",
        "pattern_learning_enabled": "professional",
        "dedicated_model_enabled": "enterprise",
    },

    "global_config": {
        "rate_limit_rpm_default": 300,
        "rate_limit_rpm_floor": 10,
        "stripe_fee_pct": 0.029,
        "per_tenant_marginal_low": 13.0,
        "per_tenant_marginal_high": 41.0,
    },
}


# ---------------------------------------------------------------------------
# Cache entry with TTL
# ---------------------------------------------------------------------------

class _CacheEntry:
    """In-process cache entry with expiry timestamp."""

    __slots__ = ("value", "expires_at")

    def __init__(self, value: Any, ttl_seconds: float) -> None:
        self.value = value
        self.expires_at = time.monotonic() + ttl_seconds

    @property
    def is_valid(self) -> bool:
        return time.monotonic() < self.expires_at


# ---------------------------------------------------------------------------
# EntitlementService
# ---------------------------------------------------------------------------

# Redis key prefix and TTL
_REDIS_KEY_PREFIX = "agentred:entitlements:"
_REDIS_TTL_SECONDS = 60
_LRU_TTL_SECONDS = 5.0

# Redis pub/sub channel for entitlement invalidation
ENTITLEMENT_INVALIDATION_CHANNEL = "agentred:entitlements:invalidate"


class EntitlementService:
    """Centralized entitlement accessor (SPEC-1815).

    Layered cache strategy:
      1. In-process LRU dict (5s TTL) — zero-cost for hot paths
      2. Redis cache (60s TTL) — shared across replicas
      3. Cosmos DB platform_config — source of truth
      4. Frozen fallback — hardcoded snapshot, used only when 1-3 fail

    Cache invalidation:
      - Superadmin PUT /entitlements publishes to Redis pub/sub
      - Subscriber clears both Redis keys and in-process cache
    """

    def __init__(self) -> None:
        self._lru: dict[str, _CacheEntry] = {}
        self._redis_client: Any | None = None
        self._cosmos_repo: Any | None = None
        self._using_fallback = False
        self._initialized = False

    async def initialize(
        self,
        redis_client: Any | None = None,
    ) -> None:
        """Initialize the service with Redis client and Cosmos repository.

        Called from app lifecycle startup. Both backends are optional —
        the service degrades gracefully.
        """
        self._redis_client = redis_client

        try:
            from src.multi_tenant.repositories.platform import (
                PlatformConfigRepository,
            )
            self._cosmos_repo = PlatformConfigRepository()
        except Exception:
            logger.warning(
                "Could not initialize PlatformConfigRepository — "
                "entitlements will use frozen fallback",
                exc_info=True,
            )

        self._initialized = True
        logger.info(
            "EntitlementService initialized: redis=%s cosmos=%s",
            self._redis_client is not None,
            self._cosmos_repo is not None,
        )

    # ------------------------------------------------------------------
    # Internal cache helpers
    # ------------------------------------------------------------------

    def _lru_get(self, key: str) -> Any | None:
        """Get from in-process LRU if not expired."""
        entry = self._lru.get(key)
        if entry is not None and entry.is_valid:
            return entry.value
        if entry is not None:
            del self._lru[key]
        return None

    def _lru_set(self, key: str, value: Any) -> None:
        """Set in-process LRU with default TTL."""
        self._lru[key] = _CacheEntry(value, _LRU_TTL_SECONDS)

    async def _redis_get(self, key: str) -> Any | None:
        """Get from Redis cache."""
        if self._redis_client is None:
            return None
        try:
            raw = self._redis_client.get(f"{_REDIS_KEY_PREFIX}{key}")
            if raw is not None:
                return json.loads(raw)
        except Exception:
            logger.debug("Redis cache miss for %s", key, exc_info=True)
        return None

    async def _redis_set(self, key: str, value: Any) -> None:
        """Set in Redis cache with TTL."""
        if self._redis_client is None:
            return
        try:
            self._redis_client.setex(
                f"{_REDIS_KEY_PREFIX}{key}",
                _REDIS_TTL_SECONDS,
                json.dumps(value, default=str),
            )
        except Exception:
            logger.debug("Redis cache write failed for %s", key, exc_info=True)

    async def _cosmos_get(self, config_type: str, config_key: str) -> Any | None:
        """Get from Cosmos DB platform_config container."""
        if self._cosmos_repo is None:
            return None
        try:
            doc = await self._cosmos_repo.get_config(config_type, config_key)
            if doc is not None:
                return doc.get("value")
        except Exception:
            logger.warning(
                "Cosmos read failed for %s:%s", config_type, config_key,
                exc_info=True,
            )
        return None

    async def _get_cached(self, config_type: str, config_key: str) -> Any | None:
        """Three-tier cache lookup: LRU → Redis → Cosmos.

        Populates lower tiers on cache miss.
        """
        cache_key = f"{config_type}:{config_key}"

        # 1. In-process LRU
        value = self._lru_get(cache_key)
        if value is not None:
            return value

        # 2. Redis
        value = await self._redis_get(cache_key)
        if value is not None:
            self._lru_set(cache_key, value)
            return value

        # 3. Cosmos
        value = await self._cosmos_get(config_type, config_key)
        if value is not None:
            self._lru_set(cache_key, value)
            await self._redis_set(cache_key, value)
            return value

        return None

    def _frozen_get(self, *keys: str) -> Any | None:
        """Navigate into FROZEN_ENTITLEMENTS by key path."""
        result: Any = FROZEN_ENTITLEMENTS
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
            else:
                return None
        return result

    # ------------------------------------------------------------------
    # Public API (SPEC-1815)
    # ------------------------------------------------------------------

    async def get_tier_config(self, tier: str) -> dict[str, Any]:
        """Get full entitlement configuration for a tier.

        Returns tier entitlements (conversations, memory layers, rates, etc.).
        """
        value = await self._get_cached("tier_config", tier)
        if value is not None:
            return value

        # Frozen fallback
        frozen = self._frozen_get("tiers", tier)
        if frozen is not None:
            self._using_fallback = True
            return dict(frozen)

        # Unknown tier — return starter defaults
        logger.warning("Unknown tier %r — returning starter defaults", tier)
        return dict(self._frozen_get("tiers", "starter") or {})

    async def get_field_gate(self, field_name: str) -> str:
        """Get the minimum tier required for a field.

        Returns a canonical tier name (e.g., "professional", "enterprise").
        Fields not in the gate map default to "trial" (all tiers).
        """
        gates = await self._get_cached("entitlements", "field_gates")
        if gates is not None:
            gate = gates.get(field_name, "trial")
            return _resolve_gate(gate)

        # Frozen fallback
        frozen = self._frozen_get("field_gates")
        if frozen is not None:
            return _resolve_gate(frozen.get(field_name, "trial"))

        return "trial"

    async def get_integration_gate(self, integration_name: str) -> str:
        """Get the minimum tier required for an integration.

        Returns a canonical tier name.
        """
        gates = await self._get_cached("entitlements", "integration_gates")
        if gates is not None:
            gate = gates.get(integration_name, "trial")
            return _resolve_gate(gate)

        # Frozen fallback
        frozen = self._frozen_get("integration_gates")
        if frozen is not None:
            return _resolve_gate(frozen.get(integration_name, "trial"))

        return "trial"

    async def get_website_limits(self, tier: str) -> dict[str, int]:
        """Get website crawl source limits for a tier."""
        value = await self._get_cached("entitlements", "website_limits")
        if value is not None and tier in value:
            return value[tier]

        frozen = self._frozen_get("website_limits", tier)
        if frozen is not None:
            return dict(frozen)

        # Default to starter limits
        return dict(self._frozen_get("website_limits", "starter") or {})

    async def get_pricing(self, tier: str) -> dict[str, Any]:
        """Get pricing configuration for a tier."""
        value = await self._get_cached("entitlements", "pricing")
        if value is not None and tier in value:
            return value[tier]

        frozen = self._frozen_get("pricing", tier)
        if frozen is not None:
            return dict(frozen)

        return {}

    async def get_rate_limit(self, tier: str) -> int:
        """Get rate limit RPM for a tier."""
        config = await self.get_tier_config(tier)
        return int(config.get("rate_limit_rpm", 300))

    async def get_global_config(self) -> dict[str, Any]:
        """Get global platform configuration."""
        value = await self._get_cached("entitlements", "global_config")
        if value is not None:
            return value

        frozen = self._frozen_get("global_config")
        if frozen is not None:
            return dict(frozen)

        return {}

    async def get_sla_targets(self, tier: str) -> dict[str, Any]:
        """Get SLA targets for a tier."""
        value = await self._get_cached("entitlements", "sla_targets")
        if value is not None and tier in value:
            return value[tier]

        frozen = self._frozen_get("sla_targets", tier)
        if frozen is not None:
            return dict(frozen)

        return {}

    async def get_pack_pricing(self) -> dict[str, float]:
        """Get conversation pack pricing."""
        value = await self._get_cached("entitlements", "pack_pricing")
        if value is not None:
            return value

        frozen = self._frozen_get("pack_pricing")
        if frozen is not None:
            return dict(frozen)

        return {}

    async def is_feature_allowed(self, feature_name: str, tier: str) -> bool:
        """Check if a feature (integration or field) is allowed for a tier.

        Checks integration gates first, then field gates.
        """
        # Check integration gates
        int_gate = await self.get_integration_gate(feature_name)
        if int_gate != "trial":
            return self.tier_meets_minimum(int_gate, tier)

        # Check field gates
        field_gate = await self.get_field_gate(feature_name)
        return self.tier_meets_minimum(field_gate, tier)

    async def is_feature_enabled(
        self, flag_name: str, tenant_id: str, tier: str = "starter",
    ) -> bool:
        """Evaluate a feature flag for a specific tenant (SPEC-1824).

        Reads the feature_flags document from the 3-tier cache and evaluates
        the flag using scope rules: global → per_tier → per_tenant.

        Returns False if the flag does not exist or is disabled.
        """
        flags_value = await self._get_cached("feature_flags", "flags")
        if flags_value is None:
            return False

        flag_data = flags_value.get(flag_name)
        if flag_data is None or not isinstance(flag_data, dict):
            return False

        # Master kill switch
        if not flag_data.get("enabled", True):
            return False

        scope = flag_data.get("scope", "global")

        if scope == "global":
            return True

        if scope == "per_tier":
            allowed_tiers = flag_data.get("tiers", [])
            return tier in allowed_tiers

        if scope == "per_tenant":
            allowed_tenants = flag_data.get("tenant_ids", [])
            return tenant_id in allowed_tenants

        return False

    def tier_meets_minimum(self, required_tier: str, actual_tier: str) -> bool:
        """Check if actual_tier meets or exceeds required_tier.

        This is a synchronous method — tier ordering is always available
        from the frozen fallback.
        """
        required = _resolve_gate(required_tier)
        actual = _resolve_gate(actual_tier)
        return TIER_ORDER.get(actual, 0) >= TIER_ORDER.get(required, 0)

    # ------------------------------------------------------------------
    # Cache management
    # ------------------------------------------------------------------

    def invalidate_cache(self, config_key: str | None = None) -> None:
        """Invalidate in-process cache entries.

        Args:
            config_key: Specific key to invalidate, or None for full flush.
        """
        if config_key is None:
            self._lru.clear()
            logger.debug("Entitlement LRU cache flushed")
        else:
            keys_to_remove = [
                k for k in self._lru if config_key in k
            ]
            for k in keys_to_remove:
                del self._lru[k]
            logger.debug("Entitlement LRU cache invalidated: %s", config_key)

    async def invalidate_redis(self, config_key: str | None = None) -> None:
        """Invalidate Redis cache entries and publish invalidation event."""
        if self._redis_client is None:
            return

        try:
            if config_key is None:
                # Flush all entitlement keys — scan and delete
                cursor = 0
                while True:
                    cursor, keys = self._redis_client.scan(
                        cursor=cursor,
                        match=f"{_REDIS_KEY_PREFIX}*",
                        count=100,
                    )
                    if keys:
                        self._redis_client.delete(*keys)
                    if cursor == 0:
                        break
            else:
                self._redis_client.delete(f"{_REDIS_KEY_PREFIX}{config_key}")

            # Publish invalidation event for other replicas
            self._redis_client.publish(
                ENTITLEMENT_INVALIDATION_CHANNEL,
                config_key or "__all__",
            )
        except Exception:
            logger.warning(
                "Redis entitlement invalidation failed for %s",
                config_key or "(all)",
                exc_info=True,
            )

    @property
    def is_using_fallback(self) -> bool:
        """True if the service has fallen back to frozen entitlements."""
        return self._using_fallback

    @property
    def is_initialized(self) -> bool:
        """True if initialize() has been called."""
        return self._initialized

    # ------------------------------------------------------------------
    # Sync convenience accessors (use LRU or frozen fallback)
    # ------------------------------------------------------------------

    def get_tier_config_sync(self, tier: str) -> dict[str, Any]:
        """Synchronous tier config lookup — LRU cache or frozen fallback.

        Use this in synchronous code paths where ``await`` is not available.
        Returns cached data if populated by a prior async call, otherwise
        falls back to FROZEN_ENTITLEMENTS.
        """
        cache_key = f"tier_config:{tier}"
        value = self._lru_get(cache_key)
        if value is not None:
            return value

        frozen = self._frozen_get("tiers", tier)
        if frozen is not None:
            return dict(frozen)

        return dict(self._frozen_get("tiers", "starter") or {})

    def get_global_config_sync(self) -> dict[str, Any]:
        """Synchronous global config lookup."""
        cache_key = "entitlements:global_config"
        value = self._lru_get(cache_key)
        if value is not None:
            return value

        frozen = self._frozen_get("global_config")
        return dict(frozen) if frozen else {}

    def get_pricing_sync(self, tier: str) -> dict[str, Any]:
        """Synchronous pricing lookup — LRU cache or frozen fallback."""
        cache_key = f"entitlements:pricing:{tier}"
        value = self._lru_get(cache_key)
        if value is not None:
            return value

        frozen = self._frozen_get("pricing", tier)
        if frozen is not None:
            return dict(frozen)

        return {}

    def get_pack_pricing_sync(self) -> dict[str, float]:
        """Synchronous pack pricing lookup — LRU cache or frozen fallback."""
        cache_key = "entitlements:pack_pricing"
        value = self._lru_get(cache_key)
        if value is not None:
            return value

        frozen = self._frozen_get("pack_pricing")
        return dict(frozen) if frozen else {}


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_instance: EntitlementService | None = None


def get_entitlement_service() -> EntitlementService:
    """Get the module-level EntitlementService singleton."""
    global _instance
    if _instance is None:
        _instance = EntitlementService()
    return _instance


def reset_entitlement_service() -> None:
    """Reset the singleton (for testing only)."""
    global _instance
    _instance = None
