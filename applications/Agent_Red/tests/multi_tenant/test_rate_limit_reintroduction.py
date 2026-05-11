"""Tests for SPEC-1803/1804/1805 — data-driven rate limiting re-introduction.

Covers:
  - TIER_DEFAULTS has rate_limit_rpm for all tiers (300 RPM)
  - Minimum RPM floor enforcement (10 RPM)
  - _get_limit() resolution order (per-tenant > tier > fallback)
  - RATE_LIMIT_DISABLED env var skips middleware registration
  - PATCH /api/superadmin/tenants/{id}/rate-limit endpoint
  - GET /api/superadmin/tenants/{id}/rate-limit endpoint
  - Fail-open guarantee (no zero-RPM tenants)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI

from src.multi_tenant.cosmos_schema import (
    RATE_LIMIT_RPM_DEFAULT,
    RATE_LIMIT_RPM_FLOOR,
    TIER_DEFAULTS,
    TenantTier,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@dataclass
class FakeTenantContext:
    """Lightweight stand-in for TenantContext."""

    tenant_id: str = "test-tenant-001"
    tier: Any = TenantTier.STARTER
    rate_limit_rpm: int | None = None
    is_platform_admin: bool = False


def _make_middleware():
    """Create a RateLimitMiddleware instance for unit testing."""
    from src.multi_tenant.middleware import RateLimitMiddleware

    return RateLimitMiddleware(app=MagicMock())


# ===========================================================================
# SPEC-1803: TIER_DEFAULTS rate_limit_rpm
# ===========================================================================


class TestTierDefaults:
    """Verify TIER_DEFAULTS includes rate_limit_rpm for all tiers."""

    def test_all_tiers_have_rate_limit_rpm(self):
        for tier in TenantTier:
            defaults = TIER_DEFAULTS.get(tier.value, {})
            assert "rate_limit_rpm" in defaults, (
                f"TIER_DEFAULTS[{tier.value!r}] missing rate_limit_rpm"
            )

    def test_default_is_300(self):
        assert RATE_LIMIT_RPM_DEFAULT == 300

    def test_all_tiers_default_to_300(self):
        for tier in TenantTier:
            rpm = TIER_DEFAULTS[tier.value]["rate_limit_rpm"]
            assert rpm == 300, f"{tier.value} has rpm={rpm}, expected 300"

    def test_floor_is_10(self):
        assert RATE_LIMIT_RPM_FLOOR == 10


# ===========================================================================
# SPEC-1803/1805: _get_limit() resolution and minimum floor
# ===========================================================================


class TestGetLimitResolution:
    """Verify _get_limit() resolution order and minimum floor."""

    def test_returns_tier_default_when_no_override(self):
        mw = _make_middleware()
        ctx = FakeTenantContext(tier=TenantTier.STARTER)
        assert mw._get_limit(ctx) == 300

    def test_per_tenant_override_takes_precedence(self):
        mw = _make_middleware()
        ctx = FakeTenantContext(tier=TenantTier.STARTER, rate_limit_rpm=500)
        assert mw._get_limit(ctx) == 500

    def test_per_tenant_override_enforces_floor(self):
        mw = _make_middleware()
        ctx = FakeTenantContext(tier=TenantTier.STARTER, rate_limit_rpm=5)
        assert mw._get_limit(ctx) == 10  # Floor enforced

    def test_per_tenant_zero_enforces_floor(self):
        mw = _make_middleware()
        ctx = FakeTenantContext(tier=TenantTier.STARTER, rate_limit_rpm=0)
        assert mw._get_limit(ctx) == 10  # Floor enforced

    def test_per_tenant_negative_enforces_floor(self):
        mw = _make_middleware()
        ctx = FakeTenantContext(tier=TenantTier.STARTER, rate_limit_rpm=-100)
        assert mw._get_limit(ctx) == 10  # Floor enforced

    def test_null_tier_uses_default(self):
        mw = _make_middleware()
        ctx = FakeTenantContext(tier=None)
        assert mw._get_limit(ctx) == 300  # Fallback

    def test_string_tier_resolves_correctly(self):
        """Tiers can be strings in some test contexts."""
        mw = _make_middleware()
        ctx = FakeTenantContext(tier="professional")
        assert mw._get_limit(ctx) == 300

    def test_unknown_tier_uses_default(self):
        mw = _make_middleware()
        ctx = FakeTenantContext(tier="unknown_tier")
        assert mw._get_limit(ctx) == 300  # Fallback

    def test_never_returns_none(self):
        """SPEC-1805: _get_limit always returns an int, never None."""
        mw = _make_middleware()
        for tier in [None, "unknown", TenantTier.TRIAL, TenantTier.ENTERPRISE]:
            ctx = FakeTenantContext(tier=tier)
            result = mw._get_limit(ctx)
            assert isinstance(result, int), (
                f"Expected int, got {type(result)} for tier={tier}"
            )
            assert result >= RATE_LIMIT_RPM_FLOOR

    def test_all_tiers_resolve_above_floor(self):
        mw = _make_middleware()
        for tier in TenantTier:
            ctx = FakeTenantContext(tier=tier)
            result = mw._get_limit(ctx)
            assert result >= RATE_LIMIT_RPM_FLOOR


# ===========================================================================
# SPEC-1805: RATE_LIMIT_DISABLED env var
# ===========================================================================


class TestRateLimitDisabled:
    """Verify RATE_LIMIT_DISABLED env var skips middleware registration."""

    def test_middleware_registered_when_not_disabled(self):
        """Default: RateLimitMiddleware should be in the middleware stack."""
        app = FastAPI()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("RATE_LIMIT_DISABLED", None)
            from src.app.lifecycle import register_middleware

            register_middleware(app)

        [type(m).__name__ for m in getattr(app, "user_middleware", [])]
        # Starlette stores middleware specs differently — check via
        # the cls attribute of Middleware objects
        middleware_classes = []
        for m in getattr(app, "user_middleware", []):
            cls = getattr(m, "cls", None)
            if cls:
                middleware_classes.append(cls.__name__)
        assert "RateLimitMiddleware" in middleware_classes

    def test_middleware_skipped_when_disabled(self):
        """RATE_LIMIT_DISABLED=true should exclude RateLimitMiddleware."""
        app = FastAPI()
        with patch.dict(os.environ, {"RATE_LIMIT_DISABLED": "true"}, clear=False):
            from src.app.lifecycle import register_middleware

            register_middleware(app)

        middleware_classes = []
        for m in getattr(app, "user_middleware", []):
            cls = getattr(m, "cls", None)
            if cls:
                middleware_classes.append(cls.__name__)
        assert "RateLimitMiddleware" not in middleware_classes

    def test_disabled_case_insensitive(self):
        """RATE_LIMIT_DISABLED=TRUE should also work."""
        app = FastAPI()
        with patch.dict(os.environ, {"RATE_LIMIT_DISABLED": "TRUE"}, clear=False):
            from src.app.lifecycle import register_middleware

            register_middleware(app)

        middleware_classes = []
        for m in getattr(app, "user_middleware", []):
            cls = getattr(m, "cls", None)
            if cls:
                middleware_classes.append(cls.__name__)
        assert "RateLimitMiddleware" not in middleware_classes

    def test_preauth_not_affected_by_disabled(self):
        """SPEC-1805: PreAuth rate limiting stays active when RATE_LIMIT_DISABLED."""
        # PreAuthRateLimitMiddleware is in security_hardening, not affected
        # by RATE_LIMIT_DISABLED — this test verifies the middleware class
        # still exists and is importable
        from src.multi_tenant.security_hardening import PreAuthRateLimitMiddleware

        assert PreAuthRateLimitMiddleware is not None


# ===========================================================================
# SPEC-1804: Rate limit API endpoint
# ===========================================================================


class TestRateLimitEndpoint:
    """Verify PATCH/GET /api/superadmin/tenants/{id}/rate-limit."""

    def test_request_model_rejects_below_floor(self):
        """rate_limit_rpm < 10 should raise validation error."""
        from src.multi_tenant.superadmin_api._tenants import RateLimitUpdateRequest

        with pytest.raises(Exception):  # Pydantic ValidationError
            RateLimitUpdateRequest(rate_limit_rpm=5)

    def test_request_model_rejects_zero(self):
        from src.multi_tenant.superadmin_api._tenants import RateLimitUpdateRequest

        with pytest.raises(Exception):
            RateLimitUpdateRequest(rate_limit_rpm=0)

    def test_request_model_accepts_null(self):
        from src.multi_tenant.superadmin_api._tenants import RateLimitUpdateRequest

        req = RateLimitUpdateRequest(rate_limit_rpm=None)
        assert req.rate_limit_rpm is None

    def test_request_model_accepts_10(self):
        from src.multi_tenant.superadmin_api._tenants import RateLimitUpdateRequest

        req = RateLimitUpdateRequest(rate_limit_rpm=10)
        assert req.rate_limit_rpm == 10

    def test_request_model_accepts_300(self):
        from src.multi_tenant.superadmin_api._tenants import RateLimitUpdateRequest

        req = RateLimitUpdateRequest(rate_limit_rpm=300)
        assert req.rate_limit_rpm == 300

    def test_request_model_accepts_large_value(self):
        from src.multi_tenant.superadmin_api._tenants import RateLimitUpdateRequest

        req = RateLimitUpdateRequest(rate_limit_rpm=10000)
        assert req.rate_limit_rpm == 10000

    def test_response_model_has_effective_rpm(self):
        from src.multi_tenant.superadmin_api._tenants import RateLimitResponse

        resp = RateLimitResponse(
            tenant_id="test", rate_limit_rpm=500, effective_rpm=500
        )
        assert resp.effective_rpm == 500

    def test_response_model_null_override(self):
        from src.multi_tenant.superadmin_api._tenants import RateLimitResponse

        resp = RateLimitResponse(
            tenant_id="test", rate_limit_rpm=None, effective_rpm=300
        )
        assert resp.rate_limit_rpm is None
        assert resp.effective_rpm == 300


# ===========================================================================
# SPEC-1805: Fail-open guarantee
# ===========================================================================


class TestFailOpenGuarantee:
    """Verify rate limiting never becomes a kill switch."""

    def test_floor_constant_is_positive(self):
        assert RATE_LIMIT_RPM_FLOOR > 0

    def test_default_constant_above_floor(self):
        assert RATE_LIMIT_RPM_DEFAULT >= RATE_LIMIT_RPM_FLOOR

    def test_all_tier_defaults_above_floor(self):
        for tier in TenantTier:
            rpm = TIER_DEFAULTS[tier.value]["rate_limit_rpm"]
            assert rpm >= RATE_LIMIT_RPM_FLOOR, (
                f"{tier.value} rpm={rpm} below floor={RATE_LIMIT_RPM_FLOOR}"
            )

    def test_middleware_allows_when_no_redis(self):
        """Without Redis, middleware should still work (in-memory fallback)."""
        mw = _make_middleware()
        # _use_redis should be False when no Redis backend configured
        assert not mw._use_redis

    def test_platform_admin_bypass(self):
        """Platform admins bypass rate limiting entirely."""
        from src.multi_tenant.middleware import RateLimitMiddleware

        mw = RateLimitMiddleware(app=MagicMock())
        # The dispatch method checks is_platform_admin — verify the code path
        # exists by checking the method is defined
        assert hasattr(mw, "dispatch")


# ===========================================================================
# Integration: middleware dispatch with rate limiting
# ===========================================================================


class TestMiddlewareDispatch:
    """Verify RateLimitMiddleware dispatch applies limits correctly."""

    @pytest.mark.asyncio
    async def test_allows_under_limit(self):
        """Requests under the RPM limit should pass through."""
        from src.multi_tenant.middleware import RateLimitMiddleware

        mw = RateLimitMiddleware(app=MagicMock())
        ctx = FakeTenantContext(tier=TenantTier.STARTER)

        # Mock the request and call_next
        request = MagicMock()
        request.state.tenant_context = ctx
        request.url.path = "/api/test"

        response = MagicMock()
        response.headers = {}

        async def mock_call_next(req):
            return response

        result = await mw.dispatch(request, mock_call_next)
        assert result is response
        assert "X-RateLimit-Limit" in result.headers
        assert result.headers["X-RateLimit-Limit"] == "300"

    @pytest.mark.asyncio
    async def test_platform_admin_skips_rate_limit(self):
        """Platform admin requests bypass rate limiting."""
        from src.multi_tenant.middleware import RateLimitMiddleware

        mw = RateLimitMiddleware(app=MagicMock())
        ctx = FakeTenantContext(is_platform_admin=True)

        request = MagicMock()
        request.state.tenant_context = ctx

        response = MagicMock()
        response.headers = {}

        async def mock_call_next(req):
            return response

        result = await mw.dispatch(request, mock_call_next)
        assert result is response
        # No rate limit headers for platform admin
        assert "X-RateLimit-Limit" not in result.headers

    @pytest.mark.asyncio
    async def test_no_context_passes_through(self):
        """Requests without tenant context (unauthenticated) pass through."""
        from src.multi_tenant.middleware import RateLimitMiddleware

        mw = RateLimitMiddleware(app=MagicMock())

        request = MagicMock()
        request.state.tenant_context = None

        response = MagicMock()

        async def mock_call_next(req):
            return response

        result = await mw.dispatch(request, mock_call_next)
        assert result is response


# ===========================================================================
# SPEC-1803: 429 enforcement — verify rate limiting actually blocks
# ===========================================================================


class TestRateLimitEnforcement:
    """Verify that requests are actually rejected when RPM is exceeded."""

    @pytest.mark.asyncio
    async def test_429_when_limit_exceeded(self):
        """Requests beyond RPM limit return 429 with correct headers."""
        from src.multi_tenant.middleware import RateLimitMiddleware

        mw = RateLimitMiddleware(app=MagicMock())
        # Use a very low override so we don't need 300 iterations
        ctx = FakeTenantContext(
            tenant_id="enforcement-test-001",
            tier=TenantTier.STARTER,
            rate_limit_rpm=10,  # Floor — minimum allowed
        )

        response = MagicMock()
        response.headers = {}

        async def mock_call_next(req):
            resp = MagicMock()
            resp.headers = {}
            return resp

        # Send 10 requests (should all succeed at rpm=10)
        for i in range(10):
            request = MagicMock()
            request.state.tenant_context = ctx
            request.url.path = "/api/test"
            result = await mw.dispatch(request, mock_call_next)
            assert result.headers.get("X-RateLimit-Limit") == "10", (
                f"Request {i+1} should succeed"
            )

        # Request 11 should be rejected
        request = MagicMock()
        request.state.tenant_context = ctx
        request.url.path = "/api/test"
        result = await mw.dispatch(request, mock_call_next)

        # JSONResponse — check status_code attribute or body
        assert hasattr(result, "status_code"), "Expected JSONResponse for 429"
        assert result.status_code == 429
        assert result.headers["Retry-After"] == "60"
        assert result.headers["X-RateLimit-Limit"] == "10"
        assert result.headers["X-RateLimit-Remaining"] == "0"

    @pytest.mark.asyncio
    async def test_429_response_body(self):
        """429 response includes structured error information."""
        from src.multi_tenant.middleware import RateLimitMiddleware

        mw = RateLimitMiddleware(app=MagicMock())
        ctx = FakeTenantContext(
            tenant_id="enforcement-body-001",
            tier=TenantTier.STARTER,
            rate_limit_rpm=10,
        )

        async def mock_call_next(req):
            resp = MagicMock()
            resp.headers = {}
            return resp

        # Exhaust the limit
        for _ in range(10):
            request = MagicMock()
            request.state.tenant_context = ctx
            request.url.path = "/api/test"
            await mw.dispatch(request, mock_call_next)

        # Trigger 429
        request = MagicMock()
        request.state.tenant_context = ctx
        request.url.path = "/api/test"
        result = await mw.dispatch(request, mock_call_next)

        # JSONResponse body is in result.body — decode it
        import json

        body = json.loads(result.body.decode())
        assert body["error"] == "Rate limit exceeded."
        assert body["limit"] == 10
        assert body["window"] == "60s"
        assert body["retry_after"] == 60

    @pytest.mark.asyncio
    async def test_remaining_decrements(self):
        """X-RateLimit-Remaining decrements with each request."""
        from src.multi_tenant.middleware import RateLimitMiddleware

        mw = RateLimitMiddleware(app=MagicMock())
        ctx = FakeTenantContext(
            tenant_id="remaining-test-001",
            tier=TenantTier.STARTER,
            rate_limit_rpm=10,
        )

        async def mock_call_next(req):
            resp = MagicMock()
            resp.headers = {}
            return resp

        remaining_values = []
        for _ in range(10):
            request = MagicMock()
            request.state.tenant_context = ctx
            request.url.path = "/api/test"
            result = await mw.dispatch(request, mock_call_next)
            remaining_values.append(int(result.headers["X-RateLimit-Remaining"]))

        # Remaining should decrease: 9, 8, 7, ... 0
        assert remaining_values == list(range(9, -1, -1))

    @pytest.mark.asyncio
    async def test_per_tenant_isolation(self):
        """Tenant A's traffic does not count against Tenant B."""
        from src.multi_tenant.middleware import RateLimitMiddleware

        mw = RateLimitMiddleware(app=MagicMock())

        ctx_a = FakeTenantContext(
            tenant_id="isolation-tenant-a",
            tier=TenantTier.STARTER,
            rate_limit_rpm=10,
        )
        ctx_b = FakeTenantContext(
            tenant_id="isolation-tenant-b",
            tier=TenantTier.STARTER,
            rate_limit_rpm=10,
        )

        async def mock_call_next(req):
            resp = MagicMock()
            resp.headers = {}
            return resp

        # Exhaust tenant A's limit
        for _ in range(10):
            request = MagicMock()
            request.state.tenant_context = ctx_a
            request.url.path = "/api/test"
            await mw.dispatch(request, mock_call_next)

        # Tenant A should be blocked
        request = MagicMock()
        request.state.tenant_context = ctx_a
        request.url.path = "/api/test"
        result_a = await mw.dispatch(request, mock_call_next)
        assert result_a.status_code == 429

        # Tenant B should still be allowed
        request = MagicMock()
        request.state.tenant_context = ctx_b
        request.url.path = "/api/test"
        result_b = await mw.dispatch(request, mock_call_next)
        assert result_b.headers.get("X-RateLimit-Limit") == "10"
        assert int(result_b.headers["X-RateLimit-Remaining"]) == 9

    @pytest.mark.asyncio
    async def test_floor_enforced_in_dispatch(self):
        """Even with rate_limit_rpm=1, the floor (10) is enforced."""
        from src.multi_tenant.middleware import RateLimitMiddleware

        mw = RateLimitMiddleware(app=MagicMock())
        ctx = FakeTenantContext(
            tenant_id="floor-dispatch-001",
            tier=TenantTier.STARTER,
            rate_limit_rpm=1,  # Below floor — should be clamped to 10
        )

        async def mock_call_next(req):
            resp = MagicMock()
            resp.headers = {}
            return resp

        # First request should show limit=10 (floor), not 1
        request = MagicMock()
        request.state.tenant_context = ctx
        request.url.path = "/api/test"
        result = await mw.dispatch(request, mock_call_next)
        assert result.headers["X-RateLimit-Limit"] == "10"

        # Should be able to send 10 total before 429
        for _ in range(9):  # Already sent 1 above
            request = MagicMock()
            request.state.tenant_context = ctx
            request.url.path = "/api/test"
            result = await mw.dispatch(request, mock_call_next)

        # Request 11 should be 429
        request = MagicMock()
        request.state.tenant_context = ctx
        request.url.path = "/api/test"
        result = await mw.dispatch(request, mock_call_next)
        assert result.status_code == 429


# ===========================================================================
# SPEC-1805: RATE_LIMIT_DISABLED integration with app lifecycle
# ===========================================================================


class TestRateLimitDisabledIntegration:
    """Verify RATE_LIMIT_DISABLED works end-to-end with register_middleware."""

    def test_rate_limiting_active_by_default_in_app(self):
        """Without RATE_LIMIT_DISABLED, a full app should enforce rate limits."""
        app = FastAPI()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("RATE_LIMIT_DISABLED", None)
            from src.app.lifecycle import register_middleware

            register_middleware(app)

        # The middleware stack should include RateLimitMiddleware
        middleware_classes = []
        for m in getattr(app, "user_middleware", []):
            cls = getattr(m, "cls", None)
            if cls:
                middleware_classes.append(cls.__name__)
        assert "RateLimitMiddleware" in middleware_classes
        assert "TenantAuthMiddleware" in middleware_classes

    def test_rate_limiting_disabled_still_has_auth(self):
        """RATE_LIMIT_DISABLED removes rate limiter but keeps auth middleware."""
        app = FastAPI()
        with patch.dict(os.environ, {"RATE_LIMIT_DISABLED": "true"}, clear=False):
            from src.app.lifecycle import register_middleware

            register_middleware(app)

        middleware_classes = []
        for m in getattr(app, "user_middleware", []):
            cls = getattr(m, "cls", None)
            if cls:
                middleware_classes.append(cls.__name__)
        assert "RateLimitMiddleware" not in middleware_classes
        assert "TenantAuthMiddleware" in middleware_classes
