"""Unit tests for auth + middleware — tenant authentication, rate limiting, dependencies.

Covers:
    - auth.py: token extraction, domain validation, API key hashing, tenant status
    - middleware.py: get_tenant_context, require_tier, rate limit calculation,
      TenantAuthMiddleware dispatch, RateLimitMiddleware sliding window

Run:
    pytest tests/multi_tenant/test_auth_middleware.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.auth import (
    AUTH_EXEMPT_PREFIXES,
    AuthenticationError,
    TenantContext,
    TenantInactiveError,
    extract_bearer_token,
    extract_shop_domain,
    hash_api_key,
    is_auth_exempt,
    validate_tenant_status,
    verify_api_key,
)
from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TeamMemberRole, TenantStatus, TenantTier
from src.multi_tenant.middleware import (
    RateLimitMiddleware,
    TenantAuthMiddleware,
    configure_tenant_resolution,
    get_tenant_context,
    require_role,
    require_tier,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_request(
    path: str = "/api/data",
    tenant_context: TenantContext | None = None,
    headers: dict | None = None,
) -> MagicMock:
    """Build a mock Starlette/FastAPI Request."""
    req = MagicMock()
    req.url.path = path
    req.method = "GET"
    req.headers = headers or {}
    req.state = MagicMock()
    if tenant_context is not None:
        req.state.tenant_context = tenant_context
    else:
        # Simulate missing attribute
        del req.state.tenant_context
    return req


def _starter_context(tenant_id: str = "t-001") -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        tier=TenantTier.STARTER,
        status=TenantStatus.ACTIVE,
        auth_method="api_key",
    )


def _pro_context(tenant_id: str = "t-002") -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        tier=TenantTier.PROFESSIONAL,
        status=TenantStatus.ACTIVE,
        auth_method="api_key",
    )


def _enterprise_context(tenant_id: str = "t-003") -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        tier=TenantTier.ENTERPRISE,
        status=TenantStatus.ACTIVE,
        auth_method="shopify_session",
        shop_domain="myshop.myshopify.com",
    )


# ===================================================================
# auth.py — extract_bearer_token
# ===================================================================

class TestExtractBearerToken:
    """AUTH-01: Bearer token extraction from Authorization header."""

    def test_valid_bearer(self):
        assert extract_bearer_token("Bearer abc123") == "abc123"

    def test_lowercase_bearer(self):
        assert extract_bearer_token("bearer abc123") == "abc123"

    def test_none_header(self):
        assert extract_bearer_token(None) is None

    def test_empty_string(self):
        assert extract_bearer_token("") is None

    def test_basic_auth_ignored(self):
        assert extract_bearer_token("Basic dXNlcjpwYXNz") is None

    def test_bearer_no_token(self):
        # "Bearer " with no following token — split gives ["Bearer", ""]
        result = extract_bearer_token("Bearer ")
        assert result == ""

    def test_bearer_with_spaces_in_token(self):
        # Only splits on first space
        assert extract_bearer_token("Bearer abc def") == "abc def"


# ===================================================================
# auth.py — is_auth_exempt
# ===================================================================

class TestIsAuthExempt:
    """AUTH-02: Auth exemption for health, webhooks, docs, checkout callbacks."""

    def test_health_exempt(self):
        assert is_auth_exempt("/health") is True

    def test_ready_exempt(self):
        assert is_auth_exempt("/ready") is True

    def test_docs_exempt(self):
        assert is_auth_exempt("/docs") is True

    def test_redoc_exempt(self):
        assert is_auth_exempt("/redoc") is True

    def test_openapi_exempt(self):
        assert is_auth_exempt("/openapi.json") is True

    def test_webhooks_exempt(self):
        assert is_auth_exempt("/api/webhooks/stripe") is True

    def test_checkout_success_exempt(self):
        assert is_auth_exempt("/api/checkout/success") is True

    def test_checkout_cancel_exempt(self):
        assert is_auth_exempt("/api/checkout/cancel") is True

    def test_shopify_confirm_exempt(self):
        assert is_auth_exempt("/api/shopify/billing/confirm") is True

    def test_dashboard_not_exempt(self):
        assert is_auth_exempt("/api/dashboard/usage") is False

    def test_config_not_exempt(self):
        assert is_auth_exempt("/api/config") is False

    def test_admin_conversations_not_exempt(self):
        assert is_auth_exempt("/api/admin/conversations") is False


# ===================================================================
# auth.py — hash_api_key
# ===================================================================

class TestHashApiKey:
    """AUTH-03: SHA-256 API key hashing."""

    def test_deterministic(self):
        h1 = hash_api_key("my-secret-key")
        h2 = hash_api_key("my-secret-key")
        assert h1 == h2

    def test_sha256_format(self):
        h = hash_api_key("test")
        assert len(h) == 64  # SHA-256 hex digest is 64 chars
        assert all(c in "0123456789abcdef" for c in h)

    def test_matches_hashlib(self):
        key = "agent-red-api-key-12345"
        expected = hashlib.sha256(key.encode("utf-8")).hexdigest()
        assert hash_api_key(key) == expected

    def test_different_keys_differ(self):
        assert hash_api_key("key-a") != hash_api_key("key-b")

    def test_empty_key(self):
        # Should not raise — returns hash of empty string
        h = hash_api_key("")
        assert len(h) == 64


# ===================================================================
# auth.py — extract_shop_domain
# ===================================================================

class TestExtractShopDomain:
    """AUTH-04: Shop domain extraction from JWT payload."""

    def test_valid_iss(self):
        payload = {"iss": "https://myshop.myshopify.com/admin"}
        assert extract_shop_domain(payload) == "myshop.myshopify.com"

    def test_missing_iss(self):
        assert extract_shop_domain({}) == ""

    def test_empty_iss(self):
        assert extract_shop_domain({"iss": ""}) == ""

    def test_iss_without_path(self):
        payload = {"iss": "https://shop.myshopify.com"}
        assert extract_shop_domain(payload) == "shop.myshopify.com"


# ===================================================================
# auth.py — validate_tenant_status
# ===================================================================

class TestValidateTenantStatus:
    """AUTH-05: Tenant lifecycle status validation."""

    def test_active_allowed(self):
        validate_tenant_status("t-1", TenantStatus.ACTIVE)  # no exception

    def test_past_due_allowed(self):
        validate_tenant_status("t-1", TenantStatus.PAST_DUE)  # no exception

    def test_provisioning_rejected(self):
        with pytest.raises(TenantInactiveError) as exc_info:
            validate_tenant_status("t-1", TenantStatus.PROVISIONING)
        assert exc_info.value.status_code == 403
        assert "t-1" in exc_info.value.message

    def test_grace_period_rejected_by_default(self):
        with pytest.raises(TenantInactiveError):
            validate_tenant_status("t-1", TenantStatus.GRACE_PERIOD)

    def test_grace_period_allowed_when_readonly(self):
        validate_tenant_status(
            "t-1", TenantStatus.GRACE_PERIOD, allow_readonly=True,
        )  # no exception

    def test_deactivated_rejected(self):
        with pytest.raises(TenantInactiveError):
            validate_tenant_status("t-1", TenantStatus.DEACTIVATED)

    def test_deactivated_rejected_even_with_readonly(self):
        with pytest.raises(TenantInactiveError):
            validate_tenant_status(
                "t-1", TenantStatus.DEACTIVATED, allow_readonly=True,
            )


# ===================================================================
# auth.py — verify_api_key
# ===================================================================

class TestVerifyApiKey:
    """AUTH-06: API key verification with async lookup."""

    @pytest.mark.asyncio
    async def test_valid_key_returns_tenant(self):
        tenant_doc = {"tenant_id": "t-1", "tier": "starter", "status": "active"}
        lookup = AsyncMock(return_value=tenant_doc)
        result = await verify_api_key("my-key", lookup)
        assert result == tenant_doc
        lookup.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_no_match_raises(self):
        lookup = AsyncMock(return_value=None)
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            await verify_api_key("bad-key", lookup)

    @pytest.mark.asyncio
    async def test_empty_key_raises(self):
        lookup = AsyncMock()
        with pytest.raises(AuthenticationError, match="API key is required"):
            await verify_api_key("", lookup)
        lookup.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_lookup_receives_hash(self):
        lookup = AsyncMock(return_value={"tenant_id": "t-1"})
        await verify_api_key("test-key", lookup)
        expected_hash = hash_api_key("test-key")
        lookup.assert_awaited_once_with(expected_hash)


# ===================================================================
# middleware.py — get_tenant_context
# ===================================================================

class TestGetTenantContext:
    """MW-01: FastAPI dependency for TenantContext extraction."""

    @pytest.mark.asyncio
    async def test_returns_context_when_present(self):
        ctx = _starter_context()
        req = _make_request(tenant_context=ctx)
        result = await get_tenant_context(req)
        assert result is ctx

    @pytest.mark.asyncio
    async def test_raises_401_when_missing(self):
        req = _make_request()  # no tenant_context
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_tenant_context(req)
        assert exc_info.value.status_code == 401


# ===================================================================
# middleware.py — require_tier
# ===================================================================

class TestRequireTier:
    """MW-02: Tier enforcement dependency factory."""

    @pytest.mark.asyncio
    async def test_starter_meets_starter(self):
        dep = require_tier(TenantTier.STARTER)
        req = _make_request(tenant_context=_starter_context())
        result = await dep(req)
        assert result.tenant_id == "t-001"

    @pytest.mark.asyncio
    async def test_enterprise_meets_starter(self):
        dep = require_tier(TenantTier.STARTER)
        req = _make_request(tenant_context=_enterprise_context())
        result = await dep(req)
        assert result.tier == TenantTier.ENTERPRISE

    @pytest.mark.asyncio
    async def test_starter_fails_professional(self):
        from fastapi import HTTPException

        dep = require_tier(TenantTier.PROFESSIONAL)
        req = _make_request(tenant_context=_starter_context())
        with pytest.raises(HTTPException) as exc_info:
            await dep(req)
        assert exc_info.value.status_code == 403
        assert "professional" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_professional_meets_professional(self):
        dep = require_tier(TenantTier.PROFESSIONAL)
        req = _make_request(tenant_context=_pro_context())
        result = await dep(req)
        assert result.tier == TenantTier.PROFESSIONAL

    @pytest.mark.asyncio
    async def test_none_tier_raises_403(self):
        from fastapi import HTTPException

        ctx = TenantContext(tenant_id="t-x", tier=None, status=TenantStatus.ACTIVE)
        dep = require_tier(TenantTier.STARTER)
        req = _make_request(tenant_context=ctx)
        with pytest.raises(HTTPException) as exc_info:
            await dep(req)
        assert exc_info.value.status_code == 403


# ===================================================================
# middleware.py — require_role (Role-Based Access Control)
# ===================================================================


class TestRequireRole:
    """MW-04: Role enforcement dependency factory."""

    def _admin_user_context(self) -> TenantContext:
        return TenantContext(
            tenant_id="t-001",
            tier=TenantTier.STARTER,
            status=TenantStatus.ACTIVE,
            auth_method="user_api_key",
            team_member_role=TeamMemberRole.ADMIN,
            team_member_id="t-001:admin@test.com",
            team_member_email="admin@test.com",
        )

    def _superadmin_context(self) -> TenantContext:
        return TenantContext(
            tenant_id="t-001",
            tier=TenantTier.STARTER,
            status=TenantStatus.ACTIVE,
            auth_method="user_api_key",
            team_member_role=TeamMemberRole.SUPERADMIN,
            team_member_id="t-001:sa@test.com",
            team_member_email="sa@test.com",
        )

    def _escalation_agent_context(self) -> TenantContext:
        return TenantContext(
            tenant_id="t-001",
            tier=TenantTier.STARTER,
            status=TenantStatus.ACTIVE,
            auth_method="user_api_key",
            team_member_role=TeamMemberRole.ESCALATION_AGENT,
            team_member_id="t-001:agent@test.com",
            team_member_email="agent@test.com",
        )

    def _viewer_context(self) -> TenantContext:
        return TenantContext(
            tenant_id="t-001",
            tier=TenantTier.STARTER,
            status=TenantStatus.ACTIVE,
            auth_method="user_api_key",
            team_member_role=TeamMemberRole.VIEWER,
            team_member_id="t-001:viewer@test.com",
            team_member_email="viewer@test.com",
        )

    @pytest.mark.asyncio
    async def test_admin_allowed_for_admin_route(self):
        dep = require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)
        req = _make_request(tenant_context=self._admin_user_context())
        result = await dep(req)
        assert result.team_member_role == TeamMemberRole.ADMIN

    @pytest.mark.asyncio
    async def test_superadmin_allowed_for_admin_route(self):
        dep = require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)
        req = _make_request(tenant_context=self._superadmin_context())
        result = await dep(req)
        assert result.team_member_role == TeamMemberRole.SUPERADMIN

    @pytest.mark.asyncio
    async def test_viewer_blocked_for_admin_route(self):
        from fastapi import HTTPException

        dep = require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)
        req = _make_request(tenant_context=self._viewer_context())
        with pytest.raises(HTTPException) as exc_info:
            await dep(req)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_escalation_agent_blocked_for_admin_route(self):
        from fastapi import HTTPException

        dep = require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)
        req = _make_request(tenant_context=self._escalation_agent_context())
        with pytest.raises(HTTPException) as exc_info:
            await dep(req)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_escalation_agent_allowed_for_inbox_route(self):
        dep = require_role(
            TeamMemberRole.SUPERADMIN,
            TeamMemberRole.ADMIN,
            TeamMemberRole.ESCALATION_AGENT,
            TeamMemberRole.VIEWER,
        )
        req = _make_request(tenant_context=self._escalation_agent_context())
        result = await dep(req)
        assert result.team_member_role == TeamMemberRole.ESCALATION_AGENT

    @pytest.mark.asyncio
    async def test_tenant_key_treated_as_admin(self):
        """Legacy tenant API keys (no team_member_role) should be treated as admin."""
        dep = require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)
        ctx = _starter_context()  # No team_member_role set
        req = _make_request(tenant_context=ctx)
        result = await dep(req)
        assert result.tenant_id == "t-001"

    @pytest.mark.asyncio
    async def test_tenant_key_blocked_when_admin_not_allowed(self):
        """Tenant key should fail if ADMIN is not in the allowed set."""
        from fastapi import HTTPException

        dep = require_role(TeamMemberRole.ESCALATION_AGENT)
        ctx = _starter_context()
        req = _make_request(tenant_context=ctx)
        with pytest.raises(HTTPException) as exc_info:
            await dep(req)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_no_context_raises_401(self):
        from fastapi import HTTPException

        dep = require_role(TeamMemberRole.ADMIN)
        req = _make_request()  # No tenant context
        with pytest.raises(HTTPException) as exc_info:
            await dep(req)
        assert exc_info.value.status_code == 401


# ===================================================================
# middleware.py — RateLimitMiddleware._get_limit
# ===================================================================


class TestRateLimitGetLimit:
    """MW-03: Rate limit resolution from tenant tier (SPEC-1803)."""

    def _make_middleware(self) -> RateLimitMiddleware:
        return RateLimitMiddleware(app=MagicMock())

    def test_starter_limit(self):
        """MW-03: SPEC-1803 data-driven default 300 RPM for all tiers."""
        mw = self._make_middleware()
        ctx = _starter_context()
        assert mw._get_limit(ctx) == 300

    def test_professional_limit(self):
        """MW-03: SPEC-1803 data-driven default 300 RPM for all tiers."""
        mw = self._make_middleware()
        ctx = _pro_context()
        assert mw._get_limit(ctx) == 300

    def test_enterprise_limit(self):
        """MW-03: SPEC-1803 data-driven default 300 RPM for all tiers."""
        mw = self._make_middleware()
        ctx = _enterprise_context()
        assert mw._get_limit(ctx) == 300

    def test_none_tier_returns_default(self):
        """SPEC-1805: null tier still returns default (never None)."""
        mw = self._make_middleware()
        ctx = TenantContext(tenant_id="t-x", tier=None, status=TenantStatus.ACTIVE)
        assert mw._get_limit(ctx) == 300

    def test_per_tenant_override_takes_precedence(self):
        """MW-03b: Per-tenant rate_limit_rpm overrides tier default."""
        mw = self._make_middleware()
        ctx = TenantContext(
            tenant_id="t-override",
            tier=TenantTier.STARTER,
            status=TenantStatus.ACTIVE,
            rate_limit_rpm=120,
        )
        assert mw._get_limit(ctx) == 120

    def test_per_tenant_override_none_falls_through(self):
        """MW-03c: rate_limit_rpm=None falls through to tier default (300 RPM)."""
        mw = self._make_middleware()
        ctx = TenantContext(
            tenant_id="t-fallthrough",
            tier=TenantTier.PROFESSIONAL,
            status=TenantStatus.ACTIVE,
            rate_limit_rpm=None,
        )
        assert mw._get_limit(ctx) == 300

    def test_trial_gets_default_rpm(self):
        """MW-03d: SPEC-1803 Trial tier gets 300 RPM default."""
        mw = self._make_middleware()
        ctx = TenantContext(
            tenant_id="t-trial",
            tier=TenantTier.TRIAL,
            status=TenantStatus.ACTIVE,
        )
        assert mw._get_limit(ctx) == 300


# ===================================================================
# middleware.py — RateLimitMiddleware sliding window
# ===================================================================

class TestRateLimitSlidingWindow:
    """MW-04: Sliding window rate counter behavior."""

    def _make_middleware(self) -> RateLimitMiddleware:
        return RateLimitMiddleware(app=MagicMock())

    def test_window_records_requests(self):
        mw = self._make_middleware()
        tenant_id = "t-rate-01"
        shard = mw._get_shard(tenant_id)
        now = time.monotonic()
        shard.windows[tenant_id].append((now, 1))
        assert len(shard.windows[tenant_id]) == 1

    def test_expired_entries_cleaned(self):
        mw = self._make_middleware()
        tenant_id = "t-rate-02"
        shard = mw._get_shard(tenant_id)
        now = time.monotonic()
        # Add an entry 120 seconds ago — outside the 60s window
        shard.windows[tenant_id].append((now - 120.0, 1))
        shard.windows[tenant_id].append((now, 1))

        # Simulate the cleanup logic from dispatch
        cutoff = now - shard.window_size
        shard.windows[tenant_id] = [
            (ts, count) for ts, count in shard.windows[tenant_id] if ts > cutoff
        ]
        assert len(shard.windows[tenant_id]) == 1

    def test_count_accumulates(self):
        mw = self._make_middleware()
        tenant_id = "t-rate-03"
        shard = mw._get_shard(tenant_id)
        now = time.monotonic()
        for i in range(5):
            shard.windows[tenant_id].append((now + i * 0.1, 1))
        current_count = sum(count for _, count in shard.windows[tenant_id])
        assert current_count == 5


# ===================================================================
# middleware.py — configure_tenant_resolution
# ===================================================================

class TestConfigureTenantResolution:
    """MW-05: Module-level resolver injection."""

    def test_sets_resolvers(self):
        import src.multi_tenant.middleware as mw_mod

        mock_shop = AsyncMock()
        mock_key = AsyncMock()
        configure_tenant_resolution(mock_shop, mock_key)
        assert mw_mod._resolve_by_shop_domain is mock_shop
        assert mw_mod._resolve_by_api_key_hash is mock_key

        # Cleanup
        mw_mod._resolve_by_shop_domain = None
        mw_mod._resolve_by_api_key_hash = None


# ===================================================================
# auth.py — TenantContext frozen dataclass
# ===================================================================

class TestTenantContext:
    """AUTH-07: TenantContext data integrity."""

    def test_frozen(self):
        ctx = _starter_context()
        with pytest.raises(AttributeError):
            ctx.tenant_id = "different"  # type: ignore[misc]

    def test_defaults(self):
        ctx = TenantContext(tenant_id="t-1")
        assert ctx.tier is None
        assert ctx.status == TenantStatus.ACTIVE
        assert ctx.auth_method == "api_key"
        assert ctx.shop_domain is None
        assert ctx.user_id is None
        assert ctx.session_id is None

    def test_shopify_fields_populated(self):
        ctx = TenantContext(
            tenant_id="t-1",
            auth_method="shopify_session",
            shop_domain="store.myshopify.com",
            user_id="user-42",
            session_id="sid-abc",
        )
        assert ctx.shop_domain == "store.myshopify.com"
        assert ctx.user_id == "user-42"
        assert ctx.session_id == "sid-abc"


# ---------------------------------------------------------------------------
# WI #295 Phase 1: Magic link session with team member identity (MW-ML-1 to MW-ML-2)
# ---------------------------------------------------------------------------


class TestMagicLinkSessionMemberIdentity:
    """MW-ML-1 to MW-ML-2: _auth_magic_link_session resolves member identity."""

    @pytest.mark.asyncio
    async def test_mw_ml01_magic_link_session_populates_member_fields(self):
        """Session JWT with member_id + role → TenantContext carries them."""
        import jwt as _jwt
        from src.multi_tenant.magic_link_auth import _JWT_SECRET

        # Create a JWT with member_id and role claims
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "t-001",
            "email": "agent@test.com",
            "type": "magic_link_session",
            "member_id": "member-001",
            "role": "escalation_agent",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=8)).timestamp()),
        }
        session_token = _jwt.encode(payload, _JWT_SECRET, algorithm="HS256")

        # Mock tenant lookup via pooled resolver
        tenant_doc = {
            "id": "t-001",
            "tenant_id": "t-001",
            "status": "active",
            "tier": "professional",
        }
        mock_resolve_tenant = AsyncMock(return_value=tenant_doc)

        # Mock team member lookup for escalation categories
        mock_team_repo = AsyncMock()
        mock_team_repo.read.return_value = {
            "id": "member-001",
            "tenant_id": "t-001",
            "email": "agent@test.com",
            "role": "escalation_agent",
            "escalation_categories": ["billing", "returns"],
        }

        middleware = TenantAuthMiddleware(MagicMock())
        configure_tenant_resolution(
            resolve_by_shop_domain=AsyncMock(),
            resolve_by_api_key_hash=AsyncMock(),
            resolve_by_tenant_id=mock_resolve_tenant,
        )

        with patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo):
            ctx = await middleware._auth_magic_link_session(session_token)

        assert ctx.tenant_id == "t-001"
        assert ctx.auth_method == "magic_link_session"
        assert ctx.team_member_id == "member-001"
        assert ctx.team_member_email == "agent@test.com"
        assert ctx.team_member_role == TeamMemberRole.ESCALATION_AGENT
        assert ctx.escalation_categories == ("billing", "returns")

    @pytest.mark.asyncio
    async def test_mw_ml02_magic_link_session_owner_has_no_member_fields(self):
        """Owner session JWT (no member_id) → TenantContext has None member fields."""
        import jwt as _jwt
        from src.multi_tenant.magic_link_auth import _JWT_SECRET

        from datetime import timedelta
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "t-001",
            "email": "owner@test.com",
            "type": "magic_link_session",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=8)).timestamp()),
        }
        session_token = _jwt.encode(payload, _JWT_SECRET, algorithm="HS256")

        tenant_doc = {
            "id": "t-001",
            "tenant_id": "t-001",
            "status": "active",
            "tier": "professional",
        }
        mock_resolve_tenant = AsyncMock(return_value=tenant_doc)

        middleware = TenantAuthMiddleware(MagicMock())
        configure_tenant_resolution(
            resolve_by_shop_domain=AsyncMock(),
            resolve_by_api_key_hash=AsyncMock(),
            resolve_by_tenant_id=mock_resolve_tenant,
        )

        ctx = await middleware._auth_magic_link_session(session_token)

        assert ctx.tenant_id == "t-001"
        assert ctx.auth_method == "magic_link_session"
        assert ctx.team_member_email == "owner@test.com"
        assert ctx.team_member_id is None
        assert ctx.team_member_role is None
        assert ctx.escalation_categories == ()
