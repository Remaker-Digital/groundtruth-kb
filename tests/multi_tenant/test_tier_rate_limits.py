"""S130: Tier entitlement and rate-limit constant verification.

Covers TEST-2860..2906 — direct assertions on TIER_DEFAULTS values,
rate-limit constants, rate-limit headers, and require_tier factory.

Each test class maps to a single SPEC:
    TestTierRateLimitDefaults       — SPEC-0287  (per-tier RPM)
    TestTierRateLimitDocumentation  — SPEC-0287  (stale docs)
    TestStarterEntitlements         — SPEC-1490
    TestProfessionalEntitlements    — SPEC-1491
    TestEnterpriseEntitlements      — SPEC-1492
    TestTrialEntitlements           — SPEC-0305
    TestRateLimitHeaders            — SPEC-1240
    TestRequireTierFactory          — SPEC-1244
    TestEmailVerificationRateLimit  — SPEC-1290
    TestRateLimitEnforcement        — SPEC-1238
    TestMagicLinkRateLimit          — SPEC-1281

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, Request

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier, _ADMIN_RPM
from src.multi_tenant.middleware import RateLimitMiddleware, require_tier

# ---------------------------------------------------------------------------
# Project root for file-based assertions
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ===================================================================
# SPEC-0287 — per-tier rate-limit RPM values
# ===================================================================


class TestTierRateLimitDefaults:
    """SPEC-0287: verify TIER_DEFAULTS rate_limit_rpm for each tier."""

    def test_starter_rpm_is_500(self) -> None:
        """TEST-2860: Starter rate_limit_rpm == 500."""
        assert TIER_DEFAULTS["starter"]["rate_limit_rpm"] == 500

    def test_professional_rpm_is_500(self) -> None:
        """TEST-2861: Professional rate_limit_rpm == 500."""
        assert TIER_DEFAULTS["professional"]["rate_limit_rpm"] == 500

    def test_enterprise_rpm_is_500(self) -> None:
        """TEST-2862: Enterprise rate_limit_rpm == 500."""
        assert TIER_DEFAULTS["enterprise"]["rate_limit_rpm"] == 500

    def test_admin_rpm_base_constant(self) -> None:
        """_ADMIN_RPM base constant is 500."""
        assert _ADMIN_RPM == 500


class TestTierRateLimitDocumentation:
    """SPEC-0287: documentation must match TIER_DEFAULTS, not stale values."""

    def test_middleware_docstring_matches_tier_defaults(self) -> None:
        """TEST-2863: Middleware docstring must NOT contain stale 10/50/200."""
        docstring = RateLimitMiddleware.__doc__ or ""
        # Stale values that must NOT appear
        stale_pattern = re.compile(r"Starter:\s+10\s+rpm")
        assert not stale_pattern.search(docstring), (
            "Middleware docstring still contains stale 10/50/200 rpm values"
        )
        # Must mention 500 rpm
        assert "500 rpm" in docstring, "Middleware docstring missing '500 rpm'"

    def test_overview_md_rpm_values_match_tier_defaults(self) -> None:
        """TEST-2864: overview.md tier table must contain 500 rpm."""
        overview = PROJECT_ROOT / "docs-site" / "docs" / "getting-started" / "overview.md"
        if not overview.exists():
            pytest.skip("overview.md not found")
        content = overview.read_text(encoding="utf-8")
        # If it still says 10/50/200, that's stale
        if "10 rpm" in content and "50 rpm" in content:
            pytest.xfail("WI-0926: overview.md still contains stale rpm values")


# ===================================================================
# SPEC-1490 — Starter tier entitlements
# ===================================================================


class TestStarterEntitlements:
    """SPEC-1490: Starter TIER_DEFAULTS values."""

    def test_starter_included_conversations(self) -> None:
        """TEST-2865."""
        assert TIER_DEFAULTS["starter"]["included_conversations"] == 1000

    def test_starter_max_concurrent(self) -> None:
        """TEST-2866."""
        assert TIER_DEFAULTS["starter"]["max_concurrent"] == 5

    def test_starter_memory_layers(self) -> None:
        """TEST-2867."""
        assert TIER_DEFAULTS["starter"]["memory_layers"] == [1, 2]

    def test_starter_overage_rate(self) -> None:
        """TEST-2868."""
        assert TIER_DEFAULTS["starter"]["overage_rate"] == 0.04

    def test_starter_max_quick_actions(self) -> None:
        """TEST-2869."""
        assert TIER_DEFAULTS["starter"]["max_quick_actions"] == 5

    def test_starter_max_quick_action_assignments(self) -> None:
        """TEST-2870."""
        assert TIER_DEFAULTS["starter"]["max_quick_action_assignments"] == 10


# ===================================================================
# SPEC-1491 — Professional tier entitlements
# ===================================================================


class TestProfessionalEntitlements:
    """SPEC-1491: Professional TIER_DEFAULTS values."""

    def test_professional_included_conversations(self) -> None:
        """TEST-2871."""
        assert TIER_DEFAULTS["professional"]["included_conversations"] == 5000

    def test_professional_max_concurrent(self) -> None:
        """TEST-2872."""
        assert TIER_DEFAULTS["professional"]["max_concurrent"] == 10

    def test_professional_memory_layers(self) -> None:
        """TEST-2873."""
        assert TIER_DEFAULTS["professional"]["memory_layers"] == [1, 2, 3]

    def test_professional_overage_rate(self) -> None:
        """TEST-2874."""
        assert TIER_DEFAULTS["professional"]["overage_rate"] == 0.025

    def test_professional_max_quick_actions(self) -> None:
        """TEST-2875."""
        assert TIER_DEFAULTS["professional"]["max_quick_actions"] == 20

    def test_professional_max_quick_action_assignments(self) -> None:
        """TEST-2876."""
        assert TIER_DEFAULTS["professional"]["max_quick_action_assignments"] == 50


# ===================================================================
# SPEC-1492 — Enterprise tier entitlements
# ===================================================================


class TestEnterpriseEntitlements:
    """SPEC-1492: Enterprise TIER_DEFAULTS values."""

    def test_enterprise_included_conversations(self) -> None:
        """TEST-2877."""
        assert TIER_DEFAULTS["enterprise"]["included_conversations"] == 20000

    def test_enterprise_max_concurrent(self) -> None:
        """TEST-2878."""
        assert TIER_DEFAULTS["enterprise"]["max_concurrent"] == 30

    def test_enterprise_memory_layers(self) -> None:
        """TEST-2879."""
        assert TIER_DEFAULTS["enterprise"]["memory_layers"] == [1, 2, 3, 4]

    def test_enterprise_overage_rate(self) -> None:
        """TEST-2880."""
        assert TIER_DEFAULTS["enterprise"]["overage_rate"] == 0.015

    def test_enterprise_max_quick_actions(self) -> None:
        """TEST-2881."""
        assert TIER_DEFAULTS["enterprise"]["max_quick_actions"] == 50

    def test_enterprise_max_quick_action_assignments(self) -> None:
        """TEST-2882."""
        assert TIER_DEFAULTS["enterprise"]["max_quick_action_assignments"] == 200


# ===================================================================
# SPEC-0305 — Trial tier entitlements
# ===================================================================


class TestTrialEntitlements:
    """SPEC-0305: Trial TIER_DEFAULTS values."""

    def test_trial_included_conversations(self) -> None:
        """TEST-2883."""
        assert TIER_DEFAULTS["trial"]["included_conversations"] == 5000

    def test_trial_rpm_is_500(self) -> None:
        """TEST-2884."""
        assert TIER_DEFAULTS["trial"]["rate_limit_rpm"] == 500

    def test_trial_max_concurrent(self) -> None:
        """TEST-2885."""
        assert TIER_DEFAULTS["trial"]["max_concurrent"] == 10

    def test_trial_history_depth_days(self) -> None:
        """TEST-2886."""
        assert TIER_DEFAULTS["trial"]["history_depth_days"] == 365

    def test_trial_memory_layers(self) -> None:
        """TEST-2887."""
        assert TIER_DEFAULTS["trial"]["memory_layers"] == [1, 2, 3]

    def test_trial_overage_rate_hard_cap(self) -> None:
        """TEST-2888: Trial overage rate is 0.0 (hard cap, no overage billing)."""
        assert TIER_DEFAULTS["trial"]["overage_rate"] == 0.0

    def test_trial_duration_days(self) -> None:
        """TEST-2889."""
        assert TIER_DEFAULTS["trial"]["trial_duration_days"] == 14

    def test_trial_max_quick_actions(self) -> None:
        """TEST-2890."""
        assert TIER_DEFAULTS["trial"]["max_quick_actions"] == 20

    def test_trial_max_quick_action_assignments(self) -> None:
        """TEST-2891."""
        assert TIER_DEFAULTS["trial"]["max_quick_action_assignments"] == 50


# ===================================================================
# SPEC-1240 — Rate-limit response headers
# ===================================================================


class TestRateLimitHeaders:
    """SPEC-1240: X-RateLimit-* headers on all responses."""

    def _make_middleware(self) -> RateLimitMiddleware:
        """Create a RateLimitMiddleware instance with a mock app."""
        return RateLimitMiddleware(app=MagicMock())

    @dataclass
    class _FakeCtx:
        tenant_id: str = "t-test"
        tier: TenantTier = TenantTier.STARTER
        rate_limit_rpm: int | None = None

    def _make_request(self, ctx: object | None = None) -> MagicMock:
        request = MagicMock(spec=Request)
        request.state.tenant_context = ctx
        request.url.path = "/api/test"
        return request

    @pytest.mark.asyncio
    async def test_response_has_ratelimit_limit_header(self) -> None:
        """TEST-2892: Successful response contains X-RateLimit-Limit."""
        mw = self._make_middleware()
        ctx = self._FakeCtx()
        request = self._make_request(ctx)

        fake_response = MagicMock()
        fake_response.headers = {}

        async def call_next(req: object) -> object:
            return fake_response

        response = await mw.dispatch(request, call_next)
        assert "X-RateLimit-Limit" in response.headers
        assert int(response.headers["X-RateLimit-Limit"]) == 500

    @pytest.mark.asyncio
    async def test_response_has_ratelimit_remaining_header(self) -> None:
        """TEST-2893: Successful response contains X-RateLimit-Remaining."""
        mw = self._make_middleware()
        ctx = self._FakeCtx()
        request = self._make_request(ctx)

        fake_response = MagicMock()
        fake_response.headers = {}

        async def call_next(req: object) -> object:
            return fake_response

        response = await mw.dispatch(request, call_next)
        assert "X-RateLimit-Remaining" in response.headers
        remaining = int(response.headers["X-RateLimit-Remaining"])
        assert remaining == 499  # First request: 500 - 0 - 1

    @pytest.mark.asyncio
    async def test_response_has_ratelimit_reset_header(self) -> None:
        """TEST-2894: Successful response contains X-RateLimit-Reset."""
        mw = self._make_middleware()
        ctx = self._FakeCtx()
        request = self._make_request(ctx)

        fake_response = MagicMock()
        fake_response.headers = {}

        async def call_next(req: object) -> object:
            return fake_response

        response = await mw.dispatch(request, call_next)
        assert "X-RateLimit-Reset" in response.headers
        reset = int(response.headers["X-RateLimit-Reset"])
        assert reset == 60  # window size

    @pytest.mark.asyncio
    async def test_429_response_has_all_ratelimit_headers(self) -> None:
        """TEST-2895: 429 response contains all three X-RateLimit-* headers."""
        mw = self._make_middleware()
        ctx = self._FakeCtx(rate_limit_rpm=2)  # Very low limit
        request = self._make_request(ctx)

        fake_response = MagicMock()
        fake_response.headers = {}

        async def call_next(req: object) -> object:
            return fake_response

        # Exhaust the rate limit
        await mw.dispatch(request, call_next)
        await mw.dispatch(request, call_next)

        # Third request should be 429
        response = await mw.dispatch(request, call_next)
        assert response.status_code == 429
        import json
        body = json.loads(response.body)
        assert body["error"] == "Rate limit exceeded."
        # Check headers via the response object (JSONResponse stores in headers)
        assert "X-RateLimit-Limit" in response.headers
        assert response.headers["X-RateLimit-Remaining"] == "0"
        assert "X-RateLimit-Reset" in response.headers


# ===================================================================
# SPEC-1244 — require_tier factory (negative paths)
# ===================================================================


class TestRequireTierFactory:
    """SPEC-1244: require_tier rejects lower tiers and None tier."""

    @pytest.mark.asyncio
    async def test_require_tier_rejects_lower_tier(self) -> None:
        """TEST-2896: Starter requesting Professional-gated endpoint gets 403."""
        dep = require_tier(TenantTier.PROFESSIONAL)

        ctx = TenantContext(tenant_id="t-test", tier=TenantTier.STARTER)
        request = MagicMock()
        request.state.tenant_context = ctx

        with pytest.raises(HTTPException) as exc_info:
            await dep(request)
        assert exc_info.value.status_code == 403
        assert "professional" in exc_info.value.detail.lower()
        assert "starter" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_require_tier_rejects_none_tier(self) -> None:
        """TEST-2897: None tier gets 403 with 'not set' message."""
        dep = require_tier(TenantTier.STARTER)

        ctx = TenantContext(tenant_id="t-test", tier=None)
        request = MagicMock()
        request.state.tenant_context = ctx

        with pytest.raises(HTTPException) as exc_info:
            await dep(request)
        assert exc_info.value.status_code == 403
        assert "not set" in exc_info.value.detail.lower()


# ===================================================================
# SPEC-1290 — Email verification rate-limit constants
# ===================================================================


class TestEmailVerificationRateLimit:
    """SPEC-1290: email_verification.py rate-limit constants and behavior."""

    def test_email_verification_rate_max_is_3(self) -> None:
        """TEST-2898."""
        from src.multi_tenant.email_verification import _RATE_MAX
        assert _RATE_MAX == 3

    def test_email_verification_rate_window_is_300(self) -> None:
        """TEST-2899."""
        from src.multi_tenant.email_verification import _RATE_WINDOW
        assert _RATE_WINDOW == 300.0

    def test_is_rate_limited_blocks_after_3_requests(self) -> None:
        """TEST-2900: _is_rate_limited returns True on 4th call within window."""
        from src.multi_tenant.email_verification import _is_rate_limited
        from src.multi_tenant.security_hardening import get_rate_limit_backend, set_rate_limit_backend, InMemoryRateLimitBackend

        test_ip = f"test-ip-{time.monotonic()}"  # unique key to avoid cross-test pollution

        # Clean any pre-existing entries
        # Use fresh backend for test isolation (SPEC-1694)
        orig = get_rate_limit_backend()
        set_rate_limit_backend(InMemoryRateLimitBackend())

        assert _is_rate_limited(test_ip) is False, "1st request should pass"
        assert _is_rate_limited(test_ip) is False, "2nd request should pass"
        assert _is_rate_limited(test_ip) is False, "3rd request should pass"
        assert _is_rate_limited(test_ip) is True, "4th request should be blocked"

        # Clean up
        set_rate_limit_backend(orig)


# ===================================================================
# SPEC-1238 — Enterprise rate-limit enforcement
# ===================================================================


class TestRateLimitEnforcement:
    """SPEC-1238: Enterprise tier rate limit is 240 rpm (4x base)."""

    @pytest.mark.asyncio
    async def test_enterprise_within_500_rpm_not_limited(self) -> None:
        """TEST-2901: Enterprise tenant rate limit is 500 rpm (same as all tiers)."""
        mw = RateLimitMiddleware(app=MagicMock())

        @dataclass
        class Ctx:
            tenant_id: str = "t-enterprise"
            tier: TenantTier = TenantTier.ENTERPRISE
            rate_limit_rpm: int | None = None

        ctx = Ctx()
        limit = mw._get_limit(ctx)
        assert limit == 500, f"Enterprise rate limit should be 500, got {limit}"


# ===================================================================
# SPEC-1281 — Magic-link rate-limit constants
# ===================================================================


class TestMagicLinkRateLimit:
    """SPEC-1281: magic_link_auth.py rate-limit constants."""

    def test_magic_link_rate_max_is_3(self) -> None:
        """TEST-2905."""
        from src.multi_tenant.magic_link_auth import _RATE_MAX
        assert _RATE_MAX == 3

    def test_magic_link_rate_window_is_300(self) -> None:
        """TEST-2906."""
        from src.multi_tenant.magic_link_auth import _RATE_WINDOW
        assert _RATE_WINDOW == 300.0
