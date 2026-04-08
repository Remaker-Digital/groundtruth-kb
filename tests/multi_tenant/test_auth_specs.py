"""Tests for auth.py and middleware.py specifications (SPEC-1228, 1232, 1243, 1244, 1245).

Covers:
    - SPEC-1228: Shopify JWT HS256 with 10s leeway and 9 required claims
    - SPEC-1232: User API keys format ar_user_{prefix}_{random}
    - SPEC-1243: Check access expiry and block expired tenants
    - SPEC-1244: require_tier() dependency factory
    - SPEC-1245: require_role() dependency factory

Run:
    pytest tests/multi_tenant/test_auth_specs.py -v

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest

from src.multi_tenant.auth import (
    JWT_ALGORITHM,
    JWT_LEEWAY_SECONDS,
    JWT_REQUIRED_CLAIMS,
    USER_API_KEY_PREFIX,
    AuthenticationError,
    TenantContext,
    TenantInactiveError,
    generate_user_api_key,
    is_user_api_key,
    validate_tenant_status,
    verify_shopify_session_token,
    verify_user_api_key,
)
from src.multi_tenant.cosmos_schema import TeamMemberRole, TenantStatus, TenantTier
from src.multi_tenant.middleware import (
    TenantAuthMiddleware,
    require_role,
    require_tier,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TEST_API_SECRET = "test-shopify-api-secret-for-jwt"
_TEST_API_KEY = "test-shopify-api-key"


def _make_shopify_jwt(
    claims: dict | None = None,
    secret: str = _TEST_API_SECRET,
    algorithm: str = "HS256",
    **overrides,
) -> str:
    """Build a valid Shopify session token JWT for testing."""
    now = datetime.now(timezone.utc)
    base = {
        "iss": "https://testshop.myshopify.com/admin",
        "dest": "https://testshop.myshopify.com",
        "sub": "shop-user-42",
        "jti": "abc-jti-123",
        "sid": "sid-abc-456",
        "aud": _TEST_API_KEY,
        "exp": int((now + timedelta(minutes=5)).timestamp()),
        "nbf": int(now.timestamp()),
        "iat": int(now.timestamp()),
    }
    if claims:
        base.update(claims)
    base.update(overrides)
    return jwt.encode(base, secret, algorithm=algorithm)


def _make_request(
    path: str = "/api/data",
    tenant_context: TenantContext | None = None,
) -> MagicMock:
    """Build a mock FastAPI Request with optional TenantContext."""
    req = MagicMock()
    req.url.path = path
    req.method = "GET"
    req.headers = {}
    req.state = MagicMock()
    if tenant_context is not None:
        req.state.tenant_context = tenant_context
    else:
        del req.state.tenant_context
    return req


# ===========================================================================
# SPEC-1228: Shopify JWT HS256 with 10s leeway and 9 required claims
# ===========================================================================


class TestSpec1228ShopifyJwtVerification:
    """SPEC-1228: Shopify JWT HS256 with 10s leeway and 9 required claims."""

    @patch.dict(
        "os.environ",
        {"SHOPIFY_API_KEY": _TEST_API_KEY, "SHOPIFY_API_SECRET": _TEST_API_SECRET},
    )
    def test_spec1228_valid_jwt_decodes_successfully(self):
        """SPEC-1228: A valid JWT with all 9 required claims decodes."""
        token = _make_shopify_jwt()
        with (
            patch("src.multi_tenant.auth.SHOPIFY_API_KEY", _TEST_API_KEY),
            patch("src.multi_tenant.auth.SHOPIFY_API_SECRET", _TEST_API_SECRET),
        ):
            payload = verify_shopify_session_token(token)
        assert payload["sub"] == "shop-user-42"
        assert payload["iss"] == "https://testshop.myshopify.com/admin"

    def test_spec1228_algorithm_is_hs256(self):
        """SPEC-1228: JWT_ALGORITHM must be HS256."""
        assert JWT_ALGORITHM == "HS256"

    def test_spec1228_leeway_is_10_seconds(self):
        """SPEC-1228: JWT_LEEWAY_SECONDS must be 10."""
        assert JWT_LEEWAY_SECONDS == 10

    def test_spec1228_nine_required_claims(self):
        """SPEC-1228: Exactly 9 claims are required."""
        expected = {"iss", "dest", "sub", "jti", "sid", "exp", "nbf", "iat", "aud"}
        assert set(JWT_REQUIRED_CLAIMS) == expected
        assert len(JWT_REQUIRED_CLAIMS) == 9

    @patch.dict(
        "os.environ",
        {"SHOPIFY_API_KEY": _TEST_API_KEY, "SHOPIFY_API_SECRET": _TEST_API_SECRET},
    )
    def test_spec1228_missing_claim_raises(self):
        """SPEC-1228: Missing a required claim raises AuthenticationError."""
        now = datetime.now(timezone.utc)
        payload = {
            "iss": "https://shop.myshopify.com/admin",
            "dest": "https://shop.myshopify.com",
            "sub": "user-1",
            # Missing jti, sid
            "aud": _TEST_API_KEY,
            "exp": int((now + timedelta(minutes=5)).timestamp()),
            "nbf": int(now.timestamp()),
            "iat": int(now.timestamp()),
        }
        token = jwt.encode(payload, _TEST_API_SECRET, algorithm="HS256")
        with (
            patch("src.multi_tenant.auth.SHOPIFY_API_KEY", _TEST_API_KEY),
            patch("src.multi_tenant.auth.SHOPIFY_API_SECRET", _TEST_API_SECRET),
        ):
            with pytest.raises(AuthenticationError, match="missing required claim"):
                verify_shopify_session_token(token)

    @patch.dict(
        "os.environ",
        {"SHOPIFY_API_KEY": _TEST_API_KEY, "SHOPIFY_API_SECRET": _TEST_API_SECRET},
    )
    def test_spec1228_expired_token_raises(self):
        """SPEC-1228: Expired token (past leeway) raises AuthenticationError."""
        now = datetime.now(timezone.utc)
        token = _make_shopify_jwt(
            exp=int((now - timedelta(minutes=5)).timestamp()),
            nbf=int((now - timedelta(minutes=10)).timestamp()),
            iat=int((now - timedelta(minutes=10)).timestamp()),
        )
        with (
            patch("src.multi_tenant.auth.SHOPIFY_API_KEY", _TEST_API_KEY),
            patch("src.multi_tenant.auth.SHOPIFY_API_SECRET", _TEST_API_SECRET),
        ):
            with pytest.raises(AuthenticationError, match="expired"):
                verify_shopify_session_token(token)

    @patch.dict(
        "os.environ",
        {"SHOPIFY_API_KEY": _TEST_API_KEY, "SHOPIFY_API_SECRET": _TEST_API_SECRET},
    )
    def test_spec1228_wrong_audience_raises(self):
        """SPEC-1228: Wrong audience raises AuthenticationError."""
        token = _make_shopify_jwt(aud="wrong-api-key")
        with (
            patch("src.multi_tenant.auth.SHOPIFY_API_KEY", _TEST_API_KEY),
            patch("src.multi_tenant.auth.SHOPIFY_API_SECRET", _TEST_API_SECRET),
        ):
            with pytest.raises(AuthenticationError, match="audience"):
                verify_shopify_session_token(token)

    @patch.dict(
        "os.environ",
        {"SHOPIFY_API_KEY": _TEST_API_KEY, "SHOPIFY_API_SECRET": _TEST_API_SECRET},
    )
    def test_spec1228_wrong_secret_raises(self):
        """SPEC-1228: Token signed with wrong secret raises AuthenticationError."""
        token = _make_shopify_jwt(secret="wrong-secret")
        with (
            patch("src.multi_tenant.auth.SHOPIFY_API_KEY", _TEST_API_KEY),
            patch("src.multi_tenant.auth.SHOPIFY_API_SECRET", _TEST_API_SECRET),
        ):
            with pytest.raises(AuthenticationError, match="malformed|signature"):
                verify_shopify_session_token(token)

    @patch.dict(
        "os.environ",
        {"SHOPIFY_API_KEY": _TEST_API_KEY, "SHOPIFY_API_SECRET": _TEST_API_SECRET},
    )
    def test_spec1228_leeway_accepts_recently_expired(self):
        """SPEC-1228: Token expired <10s ago is accepted due to leeway."""
        now = datetime.now(timezone.utc)
        # Token expired 5 seconds ago (within 10s leeway)
        token = _make_shopify_jwt(
            exp=int((now - timedelta(seconds=5)).timestamp()),
            nbf=int((now - timedelta(minutes=5)).timestamp()),
            iat=int((now - timedelta(minutes=5)).timestamp()),
        )
        with (
            patch("src.multi_tenant.auth.SHOPIFY_API_KEY", _TEST_API_KEY),
            patch("src.multi_tenant.auth.SHOPIFY_API_SECRET", _TEST_API_SECRET),
        ):
            payload = verify_shopify_session_token(token)
        assert payload is not None

    def test_spec1228_no_credentials_raises_500(self):
        """SPEC-1228: Missing API credentials raises 500."""
        with (
            patch("src.multi_tenant.auth.SHOPIFY_API_KEY", ""),
            patch("src.multi_tenant.auth.SHOPIFY_API_SECRET", ""),
            patch.dict("os.environ", {"SHOPIFY_API_KEY": "", "SHOPIFY_API_SECRET": ""}),
        ):
            with pytest.raises(AuthenticationError) as exc_info:
                verify_shopify_session_token("any-token")
            assert exc_info.value.status_code == 500

    @patch.dict(
        "os.environ",
        {"SHOPIFY_API_KEY": _TEST_API_KEY, "SHOPIFY_API_SECRET": _TEST_API_SECRET},
    )
    def test_spec1228_non_shopify_iss_raises(self):
        """SPEC-1228: Non-.myshopify.com iss domain raises AuthenticationError."""
        token = _make_shopify_jwt(
            iss="https://evil.com/admin",
            dest="https://evil.com",
        )
        with (
            patch("src.multi_tenant.auth.SHOPIFY_API_KEY", _TEST_API_KEY),
            patch("src.multi_tenant.auth.SHOPIFY_API_SECRET", _TEST_API_SECRET),
        ):
            with pytest.raises(AuthenticationError, match="not a valid Shopify domain"):
                verify_shopify_session_token(token)


# ===========================================================================
# SPEC-1232: User API keys format ar_user_{prefix}_{random}
# ===========================================================================


class TestSpec1232UserApiKeyFormat:
    """SPEC-1232: User API keys format ar_user_{prefix}_{random}."""

    def test_spec1232_prefix_is_ar_user(self):
        """SPEC-1232: USER_API_KEY_PREFIX is 'ar_user_'."""
        assert USER_API_KEY_PREFIX == "ar_user_"

    def test_spec1232_generated_key_starts_with_prefix(self):
        """SPEC-1232: Generated key starts with ar_user_."""
        key = generate_user_api_key("remaker-digital-001")
        assert key.startswith("ar_user_")

    def test_spec1232_generated_key_contains_tenant_prefix(self):
        """SPEC-1232: Key contains first 4 chars of tenant_id (sans hyphens)."""
        key = generate_user_api_key("remaker-digital-001")
        # After "ar_user_" should have "rema" (first 4 chars)
        after_prefix = key[len("ar_user_"):]
        assert after_prefix.startswith("rema_")

    def test_spec1232_key_format_pattern(self):
        """SPEC-1232: Key matches pattern ar_user_{4chars}_{urlsafe_random}."""
        key = generate_user_api_key("test-tenant-abc")
        pattern = r"^ar_user_[a-zA-Z0-9]{4}_[A-Za-z0-9_-]+$"
        assert re.match(pattern, key), f"Key {key!r} does not match expected pattern"

    def test_spec1232_keys_are_unique(self):
        """SPEC-1232: Successive key generation produces unique keys."""
        keys = {generate_user_api_key("tenant-1") for _ in range(50)}
        assert len(keys) == 50

    def test_spec1232_is_user_api_key_detects_format(self):
        """SPEC-1232: is_user_api_key correctly identifies user keys."""
        user_key = generate_user_api_key("test-tenant")
        assert is_user_api_key(user_key) is True
        assert is_user_api_key("ar_live_other_key") is False
        assert is_user_api_key("not-a-key") is False

    @pytest.mark.asyncio
    async def test_spec1232_verify_user_api_key_checks_is_active(self):
        """SPEC-1232: verify_user_api_key rejects inactive members."""
        lookup = AsyncMock(return_value={
            "team_member": {"email": "user@test.com", "is_active": False},
            "tenant": {"tenant_id": "t-1"},
        })
        with pytest.raises(AuthenticationError, match="disabled"):
            await verify_user_api_key("ar_user_test_abc123", lookup)

    @pytest.mark.asyncio
    async def test_spec1232_verify_user_api_key_accepts_active_member(self):
        """SPEC-1232: verify_user_api_key returns result for active members."""
        expected = {
            "team_member": {"email": "user@test.com", "is_active": True},
            "tenant": {"tenant_id": "t-1"},
        }
        lookup = AsyncMock(return_value=expected)
        result = await verify_user_api_key("ar_user_test_abc123", lookup)
        assert result == expected


# ===========================================================================
# SPEC-1243: Check access expiry and block expired tenants
# ===========================================================================


class TestSpec1243AccessExpiry:
    """SPEC-1243: Check access expiry and block expired tenants."""

    def test_spec1243_active_status_passes(self):
        """SPEC-1243: ACTIVE tenant status is allowed."""
        validate_tenant_status("t-1", TenantStatus.ACTIVE)

    def test_spec1243_past_due_passes(self):
        """SPEC-1243: PAST_DUE tenant status is allowed."""
        validate_tenant_status("t-1", TenantStatus.PAST_DUE)

    def test_spec1243_deactivated_blocked(self):
        """SPEC-1243: DEACTIVATED tenant is blocked with 403."""
        with pytest.raises(TenantInactiveError) as exc_info:
            validate_tenant_status("t-1", TenantStatus.DEACTIVATED)
        assert exc_info.value.status_code == 403

    def test_spec1243_provisioning_blocked(self):
        """SPEC-1243: PROVISIONING tenant is blocked."""
        with pytest.raises(TenantInactiveError):
            validate_tenant_status("t-1", TenantStatus.PROVISIONING)

    def test_spec1243_trial_expired_blocked(self):
        """SPEC-1243: TRIAL_EXPIRED tenant is blocked."""
        with pytest.raises(TenantInactiveError):
            validate_tenant_status("t-1", TenantStatus.TRIAL_EXPIRED)

    def test_spec1243_check_access_expiry_blocks_expired(self):
        """SPEC-1243: _check_access_expiry blocks expired tenants (403)."""
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        with pytest.raises(AuthenticationError) as exc_info:
            TenantAuthMiddleware._check_access_expiry("t-1", past)
        assert exc_info.value.status_code == 403
        assert "expired" in exc_info.value.message.lower()

    def test_spec1243_check_access_expiry_allows_future(self):
        """SPEC-1243: _check_access_expiry passes for future dates."""
        future = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        TenantAuthMiddleware._check_access_expiry("t-1", future)  # no exception

    def test_spec1243_check_access_expiry_none_passes(self):
        """SPEC-1243: _check_access_expiry passes when expires_at is None."""
        TenantAuthMiddleware._check_access_expiry("t-1", None)  # no exception

    def test_spec1243_check_trial_expiry_blocks_expired_trial(self):
        """SPEC-1243: _check_trial_expiry blocks expired trial tenants (403)."""
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        with pytest.raises(AuthenticationError) as exc_info:
            TenantAuthMiddleware._check_trial_expiry("t-1", TenantTier.TRIAL, past)
        assert exc_info.value.status_code == 403

    def test_spec1243_check_trial_expiry_skips_non_trial(self):
        """SPEC-1243: _check_trial_expiry is no-op for non-trial tiers."""
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        # Should NOT raise for STARTER even with expired date
        TenantAuthMiddleware._check_trial_expiry("t-1", TenantTier.STARTER, past)


# ===========================================================================
# SPEC-1244: require_tier() dependency factory
# ===========================================================================


class TestSpec1244RequireTier:
    """SPEC-1244: require_tier() dependency factory."""

    @pytest.mark.asyncio
    async def test_spec1244_starter_meets_starter_requirement(self):
        """SPEC-1244: Starter tenant passes starter-level check."""
        dep = require_tier(TenantTier.STARTER)
        ctx = TenantContext(
            tenant_id="t-1", tier=TenantTier.STARTER, status=TenantStatus.ACTIVE,
        )
        req = _make_request(tenant_context=ctx)
        result = await dep(req)
        assert result.tier == TenantTier.STARTER

    @pytest.mark.asyncio
    async def test_spec1244_professional_meets_starter_requirement(self):
        """SPEC-1244: Professional tenant passes starter-level check."""
        dep = require_tier(TenantTier.STARTER)
        ctx = TenantContext(
            tenant_id="t-1", tier=TenantTier.PROFESSIONAL, status=TenantStatus.ACTIVE,
        )
        req = _make_request(tenant_context=ctx)
        result = await dep(req)
        assert result.tier == TenantTier.PROFESSIONAL

    @pytest.mark.asyncio
    async def test_spec1244_starter_fails_professional_requirement(self):
        """SPEC-1244: Starter tenant fails professional-level check with 403."""
        from fastapi import HTTPException

        dep = require_tier(TenantTier.PROFESSIONAL)
        ctx = TenantContext(
            tenant_id="t-1", tier=TenantTier.STARTER, status=TenantStatus.ACTIVE,
        )
        req = _make_request(tenant_context=ctx)
        with pytest.raises(HTTPException) as exc_info:
            await dep(req)
        assert exc_info.value.status_code == 403
        assert "professional" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_spec1244_enterprise_meets_all(self):
        """SPEC-1244: Enterprise tenant passes all tier checks."""
        for required in [TenantTier.STARTER, TenantTier.PROFESSIONAL, TenantTier.ENTERPRISE]:
            dep = require_tier(required)
            ctx = TenantContext(
                tenant_id="t-1", tier=TenantTier.ENTERPRISE, status=TenantStatus.ACTIVE,
            )
            req = _make_request(tenant_context=ctx)
            result = await dep(req)
            assert result.tier == TenantTier.ENTERPRISE

    @pytest.mark.asyncio
    async def test_spec1244_none_tier_raises_403(self):
        """SPEC-1244: None tier raises 403."""
        from fastapi import HTTPException

        dep = require_tier(TenantTier.STARTER)
        ctx = TenantContext(tenant_id="t-1", tier=None, status=TenantStatus.ACTIVE)
        req = _make_request(tenant_context=ctx)
        with pytest.raises(HTTPException) as exc_info:
            await dep(req)
        assert exc_info.value.status_code == 403


# ===========================================================================
# SPEC-1245: require_role() dependency factory
# ===========================================================================


class TestSpec1245RequireRole:
    """SPEC-1245: require_role() dependency factory."""

    def _ctx_with_role(self, role: TeamMemberRole) -> TenantContext:
        return TenantContext(
            tenant_id="t-1",
            tier=TenantTier.STARTER,
            status=TenantStatus.ACTIVE,
            auth_method="user_api_key",
            team_member_role=role,
            team_member_id=f"t-1:{role.value}@test.com",
            team_member_email=f"{role.value}@test.com",
        )

    @pytest.mark.asyncio
    async def test_spec1245_admin_allowed_for_admin_route(self):
        """SPEC-1245: Admin role passes admin-required check."""
        dep = require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)
        req = _make_request(tenant_context=self._ctx_with_role(TeamMemberRole.ADMIN))
        result = await dep(req)
        assert result.team_member_role == TeamMemberRole.ADMIN

    @pytest.mark.asyncio
    async def test_spec1245_viewer_blocked_for_admin_route(self):
        """SPEC-1245: Viewer role fails admin-required check with 403."""
        from fastapi import HTTPException

        dep = require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)
        req = _make_request(tenant_context=self._ctx_with_role(TeamMemberRole.VIEWER))
        with pytest.raises(HTTPException) as exc_info:
            await dep(req)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_spec1245_superadmin_allowed_everywhere(self):
        """SPEC-1245: Superadmin role passes any role check."""
        dep = require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)
        req = _make_request(tenant_context=self._ctx_with_role(TeamMemberRole.SUPERADMIN))
        result = await dep(req)
        assert result.team_member_role == TeamMemberRole.SUPERADMIN

    @pytest.mark.asyncio
    async def test_spec1245_legacy_tenant_key_treated_as_admin(self):
        """SPEC-1245: Tenant-level API key (no role) treated as admin when ADMIN in allowed."""
        dep = require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)
        ctx = TenantContext(
            tenant_id="t-1", tier=TenantTier.STARTER, status=TenantStatus.ACTIVE,
        )
        req = _make_request(tenant_context=ctx)
        result = await dep(req)
        assert result.tenant_id == "t-1"

    @pytest.mark.asyncio
    async def test_spec1245_legacy_key_blocked_when_admin_not_allowed(self):
        """SPEC-1245: Tenant key fails if ADMIN not in allowed roles."""
        from fastapi import HTTPException

        dep = require_role(TeamMemberRole.ESCALATION_AGENT)
        ctx = TenantContext(
            tenant_id="t-1", tier=TenantTier.STARTER, status=TenantStatus.ACTIVE,
        )
        req = _make_request(tenant_context=ctx)
        with pytest.raises(HTTPException) as exc_info:
            await dep(req)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_spec1245_escalation_agent_allowed_for_own_role(self):
        """SPEC-1245: Escalation agent allowed when their role is listed."""
        dep = require_role(
            TeamMemberRole.SUPERADMIN,
            TeamMemberRole.ADMIN,
            TeamMemberRole.ESCALATION_AGENT,
        )
        req = _make_request(
            tenant_context=self._ctx_with_role(TeamMemberRole.ESCALATION_AGENT),
        )
        result = await dep(req)
        assert result.team_member_role == TeamMemberRole.ESCALATION_AGENT
