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
        # Trial should match Professional on remaining entitlements
        assert trial["included_conversations"] == pro["included_conversations"]
        assert trial["memory_layers"] == pro["memory_layers"]

    def test_trial_exceeds_starter(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS

        trial = TIER_DEFAULTS["trial"]
        starter = TIER_DEFAULTS["starter"]
        assert trial["included_conversations"] > starter["included_conversations"]

    def test_trial_below_enterprise(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS

        trial = TIER_DEFAULTS["trial"]
        enterprise = TIER_DEFAULTS["enterprise"]
        assert trial["included_conversations"] < enterprise["included_conversations"]

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
# WI-1272: Per-tier caps REMOVED from TIER_DEFAULTS
# ---------------------------------------------------------------------------

class TestPerTierCapsRemoved:
    """SPEC-1752: Per-tier cap keys have been removed from TIER_DEFAULTS."""

    def test_caps_not_in_tier_defaults(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        removed_keys = [
            "max_kb_articles", "max_website_sources",
            "max_escalation_categories", "max_team_members",
        ]
        for tier in TenantTier:
            td = TIER_DEFAULTS.get(tier.value, {})
            for key in removed_keys:
                assert key not in td, f"{key} should not be in {tier.value}"


# ---------------------------------------------------------------------------
# WI-1268: Tier re-validation in activate() (SPEC-1748)
# ---------------------------------------------------------------------------

class TestTierRevalidation:
    """SPEC-1748: ActivationService validates tier entitlements before activation."""

    def test_starter_allows_custom_instructions(self):
        """S186: custom_instructions gate removed — all tiers can set them."""
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {"custom_instructions": "Do something special"}
        errors = svc._validate_tier_entitlements(draft, TenantTier.STARTER)
        assert len(errors) == 0

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

    def test_quick_actions_no_longer_validated_by_tier(self):
        """Quick action caps removed — any count passes tier validation."""
        from src.multi_tenant.activation_service import ActivationService
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = ActivationService.__new__(ActivationService)
        draft = {"quick_actions": [{"id": str(i)} for i in range(100)]}
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
# WI-1273: History depth keys REMOVED from TIER_DEFAULTS
# ---------------------------------------------------------------------------

class TestHistoryDepthRemoved:
    """history_depth_days has been removed from TIER_DEFAULTS."""

    def test_history_depth_days_not_in_tier_defaults(self):
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
        for tier in TenantTier:
            td = TIER_DEFAULTS.get(tier.value, {})
            assert "history_depth_days" not in td, f"history_depth_days should not be in {tier.value}"


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

class TestImportKnowledgeTierGateRemoved:
    """SPEC-1749: max_website_sources cap has been removed from TIER_DEFAULTS."""

    def test_max_website_sources_not_in_tier_defaults(self):
        """The cap field no longer exists in TIER_DEFAULTS."""
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier

        for tier in TenantTier:
            td = TIER_DEFAULTS.get(tier.value, {})
            assert "max_website_sources" not in td, f"max_website_sources should not be in {tier.value}"
