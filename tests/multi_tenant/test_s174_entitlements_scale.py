"""S174: Tests for 680-tenant scale entitlements improvements.

Covers:
    WI-1265: Sharded rate limiting (SPEC-1745)
    WI-1266: Trial tier level mapping (SPEC-1746)
    WI-1267: Atomic reservation / TOCTOU fix (SPEC-1747)
    WI-1268: Tier re-validation in activate() (SPEC-1748)
    WI-1269: Tier gate on import_knowledge_from_url() (SPEC-1749)
    WI-1270: Null tier guard (SPEC-1750)
    WI-1271: Extended cache TTLs (SPEC-1751)
    WI-1272: Per-tier caps (SPEC-1752)
    WI-1273: History depth enforcement (SPEC-1753)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import asyncio
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# WI-1266: Trial tier level mapping (SPEC-1746)
# ---------------------------------------------------------------------------

class TestTrialTierMapping:
    """SPEC-1746: Trial maps to Professional level (1), not Starter (0).

    The tier ordering dict is local to require_tier(), so we verify the
    mapping via TIER_DEFAULTS: Trial gets the same caps as Professional.
    """

    def test_trial_mirrors_professional_defaults(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS

        trial = TIER_DEFAULTS["trial"]
        pro = TIER_DEFAULTS["professional"]
        # Trial should match Professional on key caps
        assert trial["max_kb_articles"] == pro["max_kb_articles"]
        assert trial["max_team_members"] == pro["max_team_members"]

    def test_trial_exceeds_starter(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS

        trial = TIER_DEFAULTS["trial"]
        starter = TIER_DEFAULTS["starter"]
        assert trial["max_kb_articles"] > starter["max_kb_articles"]
        assert trial["max_team_members"] > starter["max_team_members"]

    def test_trial_below_enterprise(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS

        trial = TIER_DEFAULTS["trial"]
        enterprise = TIER_DEFAULTS["enterprise"]
        assert trial["max_kb_articles"] < enterprise["max_kb_articles"]
        assert trial["max_team_members"] < enterprise["max_team_members"]

    @pytest.mark.asyncio
    async def test_require_tier_trial_allows_professional_features(self):
        """Trial tier passes Professional-level tier gate (both map to level 1)."""
        from fastapi import FastAPI, Depends, Request
        from starlette.testclient import TestClient
        from src.multi_tenant.middleware import require_tier
        from src.multi_tenant.cosmos_schema import TenantTier

        app = FastAPI()

        @app.get("/test-pro-feature")
        async def pro_feature(request: Request):
            return {"ok": True}

        # Directly test the tier ordering logic
        from src.multi_tenant.middleware import require_tier
        dep = require_tier(TenantTier.PROFESSIONAL)
        # The dependency is a closure — we can inspect the tier_order dict
        # by calling the inner function with a mocked request
        mock_request = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.tier = TenantTier.TRIAL
        with patch("src.multi_tenant.middleware.get_tenant_context", new=AsyncMock(return_value=mock_ctx)):
            # Trial (level 1) >= Professional (level 1), so this should NOT raise
            result = await dep(mock_request)
            assert result.tier == TenantTier.TRIAL


# ---------------------------------------------------------------------------
# WI-1270: Null tier guard (SPEC-1750)
# ---------------------------------------------------------------------------

class TestNullTierGuard:
    """SPEC-1750: Admin endpoints reject requests when ctx.tier is None."""

    @pytest.mark.asyncio
    async def test_null_tier_rejected_on_admin_path(self):
        from fastapi import HTTPException
        from src.multi_tenant.middleware import get_tenant_context
        from src.multi_tenant.auth import TenantContext

        ctx = TenantContext(
            tenant_id="test-tenant",
            tier=None,
            status="ACTIVE",
            auth_method="api_key",
        )

        request = MagicMock()
        request.state.tenant_context = ctx
        request.url.path = "/api/admin/team"

        with pytest.raises(HTTPException) as exc_info:
            await get_tenant_context(request)
        assert exc_info.value.status_code == 403
        assert "tier not configured" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_null_tier_allowed_for_platform_admin(self):
        from src.multi_tenant.middleware import get_tenant_context
        from src.multi_tenant.auth import TenantContext

        ctx = TenantContext(
            tenant_id="__platform__",
            tier=None,
            status="ACTIVE",
            auth_method="api_key",
            is_platform_admin=True,
        )

        request = MagicMock()
        request.state.tenant_context = ctx
        # Platform admins only access /api/superadmin/* (SPEC-1667).
        # The null-tier guard at SPEC-1750 should NOT block them.
        request.url.path = "/api/superadmin/tenants"

        result = await get_tenant_context(request)
        assert result.is_platform_admin is True

    @pytest.mark.asyncio
    async def test_null_tier_allowed_on_widget_path(self):
        """Widget/chat paths exempt from null tier guard."""
        from src.multi_tenant.middleware import get_tenant_context
        from src.multi_tenant.auth import TenantContext

        ctx = TenantContext(
            tenant_id="test-tenant",
            tier=None,
            status="ACTIVE",
            auth_method="widget_key",
        )

        request = MagicMock()
        request.state.tenant_context = ctx
        request.url.path = "/api/chat/start"

        result = await get_tenant_context(request)
        assert result.tenant_id == "test-tenant"


# ---------------------------------------------------------------------------
# WI-1265: Sharded rate limiting (SPEC-1745)
# ---------------------------------------------------------------------------

class TestShardedRateLimiting:
    """SPEC-1745: Rate limiter uses sharded locks instead of single lock."""

    def test_rate_limit_middleware_has_shards(self):
        from src.multi_tenant.middleware import RateLimitMiddleware

        app = MagicMock()
        mw = RateLimitMiddleware(app, num_shards=16)
        assert len(mw._shards) == 16

    def test_different_tenants_can_get_different_shards(self):
        from src.multi_tenant.middleware import RateLimitMiddleware

        app = MagicMock()
        mw = RateLimitMiddleware(app, num_shards=16)

        # With 16 shards and different tenant IDs, we should get
        # different shards for at least some tenants
        shards = set()
        for i in range(32):
            shard = mw._get_shard(f"tenant-{i}")
            shards.add(id(shard))
        # With 32 tenants across 16 shards, we must have >1 distinct shard
        assert len(shards) > 1

    def test_same_tenant_always_gets_same_shard(self):
        from src.multi_tenant.middleware import RateLimitMiddleware

        app = MagicMock()
        mw = RateLimitMiddleware(app, num_shards=16)

        shard1 = mw._get_shard("tenant-abc")
        shard2 = mw._get_shard("tenant-abc")
        assert shard1 is shard2

    @pytest.mark.asyncio
    async def test_shard_check_and_record_allows_under_limit(self):
        from src.multi_tenant.middleware import _RateLimitShard

        shard = _RateLimitShard()
        allowed, remaining = await shard.check_and_record("t1", 500)
        assert allowed is True
        assert remaining == 499

    @pytest.mark.asyncio
    async def test_shard_check_and_record_blocks_at_limit(self):
        from src.multi_tenant.middleware import _RateLimitShard

        shard = _RateLimitShard()
        # Fill up to limit
        for _ in range(10):
            await shard.check_and_record("t1", 10)
        # 11th request should be blocked
        allowed, remaining = await shard.check_and_record("t1", 10)
        assert allowed is False
        assert remaining == 0

    @pytest.mark.asyncio
    async def test_shards_isolate_tenants(self):
        """Two tenants in the same shard don't interfere."""
        from src.multi_tenant.middleware import _RateLimitShard

        shard = _RateLimitShard()
        for _ in range(5):
            await shard.check_and_record("tenant-a", 5)

        # tenant-a is at limit, but tenant-b should be fine
        allowed, _ = await shard.check_and_record("tenant-a", 5)
        assert allowed is False

        allowed, remaining = await shard.check_and_record("tenant-b", 5)
        assert allowed is True
        assert remaining == 4

    def test_default_shard_count_is_16(self):
        from src.multi_tenant.middleware import _NUM_RATE_LIMIT_SHARDS
        assert _NUM_RATE_LIMIT_SHARDS == 16


# ---------------------------------------------------------------------------
# WI-1271: Extended cache TTLs (SPEC-1751)
# ---------------------------------------------------------------------------

class TestExtendedCacheTTLs:
    """SPEC-1751: ConfigProcessor cache 60s->300s, tenant metadata cache."""

    def test_config_cache_ttl_is_300(self):
        from src.multi_tenant.config.cache import CACHE_TTL_SECONDS
        assert CACHE_TTL_SECONDS == 300

    def test_tenant_meta_cache_ttl_is_120(self):
        from src.multi_tenant.middleware import _TENANT_META_CACHE_TTL
        assert _TENANT_META_CACHE_TTL == 120

    def test_tenant_meta_cache_max_is_1000(self):
        from src.multi_tenant.middleware import _TENANT_META_CACHE_MAX
        assert _TENANT_META_CACHE_MAX == 1_000

    def test_get_cached_returns_none_for_missing(self):
        from src.multi_tenant.middleware import _get_cached_tenant_meta
        assert _get_cached_tenant_meta("nonexistent-key") is None

    def test_set_and_get_cached_tenant_meta(self):
        from src.multi_tenant.middleware import (
            _get_cached_tenant_meta,
            _set_cached_tenant_meta,
            _tenant_meta_cache,
        )
        # Clean up
        _tenant_meta_cache.clear()

        _set_cached_tenant_meta("test:tid:abc", {"tier": "professional"})
        result = _get_cached_tenant_meta("test:tid:abc")
        assert result == {"tier": "professional"}

        # Cleanup
        _tenant_meta_cache.clear()

    def test_invalidate_single_tenant(self):
        from src.multi_tenant.middleware import (
            _get_cached_tenant_meta,
            _set_cached_tenant_meta,
            invalidate_tenant_meta_cache,
            _tenant_meta_cache,
        )
        _tenant_meta_cache.clear()

        _set_cached_tenant_meta("tid:tenant-1", {"tier": "starter"})
        _set_cached_tenant_meta("tid:tenant-2", {"tier": "pro"})

        invalidate_tenant_meta_cache("tenant-1")
        assert _get_cached_tenant_meta("tid:tenant-1") is None
        assert _get_cached_tenant_meta("tid:tenant-2") is not None

        _tenant_meta_cache.clear()

    def test_invalidate_all(self):
        from src.multi_tenant.middleware import (
            _set_cached_tenant_meta,
            invalidate_tenant_meta_cache,
            _tenant_meta_cache,
        )
        _tenant_meta_cache.clear()

        _set_cached_tenant_meta("tid:t1", {"a": 1})
        _set_cached_tenant_meta("tid:t2", {"a": 2})

        invalidate_tenant_meta_cache(None)
        assert len(_tenant_meta_cache) == 0


# ---------------------------------------------------------------------------
# WI-1272: Per-tier caps in TIER_DEFAULTS (SPEC-1752)
# ---------------------------------------------------------------------------

class TestPerTierCaps:
    """SPEC-1752: max_kb_articles, max_website_sources, etc. in TIER_DEFAULTS."""

    def test_starter_caps(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        starter = TIER_DEFAULTS[TenantTier.STARTER.value]
        assert starter["max_kb_articles"] == 50
        assert starter["max_website_sources"] == 5
        assert starter["max_escalation_categories"] == 3
        assert starter["max_team_members"] == 5

    def test_professional_caps(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        pro = TIER_DEFAULTS[TenantTier.PROFESSIONAL.value]
        assert pro["max_kb_articles"] == 200
        assert pro["max_website_sources"] == 20
        assert pro["max_escalation_categories"] == 10
        assert pro["max_team_members"] == 20

    def test_enterprise_caps(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        ent = TIER_DEFAULTS[TenantTier.ENTERPRISE.value]
        assert ent["max_kb_articles"] == 1_000
        assert ent["max_website_sources"] == 100
        assert ent["max_escalation_categories"] == 25
        assert ent["max_team_members"] == 100

    def test_trial_mirrors_professional(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        trial = TIER_DEFAULTS[TenantTier.TRIAL.value]
        pro = TIER_DEFAULTS[TenantTier.PROFESSIONAL.value]
        assert trial["max_kb_articles"] == pro["max_kb_articles"]
        assert trial["max_website_sources"] == pro["max_website_sources"]
        assert trial["max_escalation_categories"] == pro["max_escalation_categories"]
        assert trial["max_team_members"] == pro["max_team_members"]

    def test_caps_increase_with_tier(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        s = TIER_DEFAULTS[TenantTier.STARTER.value]
        p = TIER_DEFAULTS[TenantTier.PROFESSIONAL.value]
        e = TIER_DEFAULTS[TenantTier.ENTERPRISE.value]
        for key in ("max_kb_articles", "max_website_sources",
                     "max_escalation_categories", "max_team_members"):
            assert s[key] <= p[key] <= e[key], f"{key} doesn't increase with tier"


# ---------------------------------------------------------------------------
# WI-1268: Tier re-validation in activate() (SPEC-1748)
# ---------------------------------------------------------------------------

class TestTierRevalidation:
    """SPEC-1748: ActivationService validates tier entitlements before activation."""

    def test_starter_rejects_custom_instructions(self):
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {"custom_instructions": "Do something special"}
        errors = svc._validate_tier_entitlements(draft, TenantTier.STARTER)
        assert len(errors) == 1
        assert errors[0]["field"] == "custom_instructions"

    def test_professional_allows_custom_instructions(self):
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {"custom_instructions": "Do something special"}
        errors = svc._validate_tier_entitlements(draft, TenantTier.PROFESSIONAL)
        assert len(errors) == 0

    def test_starter_rejects_layer_3(self):
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {"memory_layers": [1, 2, 3]}
        errors = svc._validate_tier_entitlements(draft, TenantTier.STARTER)
        assert len(errors) == 1
        assert errors[0]["field"] == "memory_layers"

    def test_professional_allows_layer_3(self):
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {"memory_layers": [1, 2, 3]}
        errors = svc._validate_tier_entitlements(draft, TenantTier.PROFESSIONAL)
        assert len(errors) == 0

    def test_starter_allows_layers_1_2(self):
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {"memory_layers": [1, 2]}
        errors = svc._validate_tier_entitlements(draft, TenantTier.STARTER)
        assert len(errors) == 0

    def test_quick_action_count_over_limit(self):
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {"quick_actions": [{"id": str(i)} for i in range(6)]}
        errors = svc._validate_tier_entitlements(draft, TenantTier.STARTER)
        assert len(errors) == 1
        assert errors[0]["field"] == "quick_actions"

    def test_quick_action_count_within_limit(self):
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {"quick_actions": [{"id": str(i)} for i in range(5)]}
        errors = svc._validate_tier_entitlements(draft, TenantTier.STARTER)
        assert len(errors) == 0

    def test_empty_custom_instructions_ok_for_starter(self):
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {"custom_instructions": ""}
        errors = svc._validate_tier_entitlements(draft, TenantTier.STARTER)
        assert len(errors) == 0

    def test_trial_allows_professional_features(self):
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {
            "custom_instructions": "Be helpful",
            "memory_layers": [1, 2, 3],
            "quick_actions": [{"id": str(i)} for i in range(20)],
        }
        errors = svc._validate_tier_entitlements(draft, TenantTier.TRIAL)
        assert len(errors) == 0


# ---------------------------------------------------------------------------
# WI-1273: History depth enforcement (SPEC-1753)
# ---------------------------------------------------------------------------

class TestHistoryDepthEnforcement:
    """SPEC-1753: Conversation list enforces tier-based history depth."""

    def test_starter_history_depth_days(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        assert TIER_DEFAULTS[TenantTier.STARTER.value]["history_depth_days"] == 90

    def test_professional_history_depth_days(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        assert TIER_DEFAULTS[TenantTier.PROFESSIONAL.value]["history_depth_days"] == 365

    def test_enterprise_unlimited_history(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        assert TIER_DEFAULTS[TenantTier.ENTERPRISE.value]["history_depth_days"] is None


# ---------------------------------------------------------------------------
# WI-1267: Atomic reservation (SPEC-1747)
# ---------------------------------------------------------------------------

class TestAtomicReservation:
    """SPEC-1747: Per-tenant locks prevent TOCTOU in count-limited operations."""

    def test_tenant_lock_created_on_demand(self):
        from src.multi_tenant.admin_quick_action_api import (
            _get_tenant_lock,
            _tenant_qa_locks,
        )
        _tenant_qa_locks.clear()
        lock = _get_tenant_lock("test-tenant-lock")
        assert isinstance(lock, asyncio.Lock)
        _tenant_qa_locks.clear()

    def test_same_tenant_gets_same_lock(self):
        from src.multi_tenant.admin_quick_action_api import (
            _get_tenant_lock,
            _tenant_qa_locks,
        )
        _tenant_qa_locks.clear()
        lock1 = _get_tenant_lock("t1")
        lock2 = _get_tenant_lock("t1")
        assert lock1 is lock2
        _tenant_qa_locks.clear()

    def test_different_tenants_get_different_locks(self):
        from src.multi_tenant.admin_quick_action_api import (
            _get_tenant_lock,
            _tenant_qa_locks,
        )
        _tenant_qa_locks.clear()
        lock1 = _get_tenant_lock("t1")
        lock2 = _get_tenant_lock("t2")
        assert lock1 is not lock2
        _tenant_qa_locks.clear()


# ---------------------------------------------------------------------------
# WI-1269: Tier gate on import_knowledge_from_url() (SPEC-1749)
# ---------------------------------------------------------------------------

class TestImportKnowledgeTierGate:
    """SPEC-1749: import_knowledge_from_url() checks tier-based source limits."""

    def test_max_website_sources_in_tier_defaults(self):
        """The cap field exists in TIER_DEFAULTS for all tiers."""
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier

        for tier in TenantTier:
            td = TIER_DEFAULTS.get(tier.value, {})
            assert "max_website_sources" in td, f"Missing max_website_sources for {tier.value}"

    def test_starter_website_source_limit(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        assert TIER_DEFAULTS[TenantTier.STARTER.value]["max_website_sources"] == 5
