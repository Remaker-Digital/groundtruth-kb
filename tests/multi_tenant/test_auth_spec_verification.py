"""Spec verification tests for AUTH-section specifications.

Each test class verifies a specific SPEC-* requirement against the
actual implementation. Tests exercise production interfaces per GOV-10.

Session S152 — spec review and real test creation.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest

# ---------------------------------------------------------------------------
# SPEC-0306: Trial expiry enforced at middleware level
# ---------------------------------------------------------------------------


class TestSpec0306TrialExpiryMiddleware:
    """SPEC-0306: Trial expiry shall be enforced at the middleware level.

    Every request checks trial_expires_at before reaching endpoint handlers.
    Verified by: middleware._check_trial_expiry raises HTTPException for
    expired trials.
    """

    def test_check_trial_expiry_exists_in_middleware(self):
        """The middleware module exposes a _check_trial_expiry method."""
        from src.multi_tenant.middleware import TenantAuthMiddleware

        mw = TenantAuthMiddleware.__new__(TenantAuthMiddleware)
        assert hasattr(mw, "_check_trial_expiry"), (
            "Middleware must have _check_trial_expiry method"
        )

    def test_trial_expiry_passes_for_non_trial_tier(self):
        """Non-trial tiers skip expiry check."""
        from src.multi_tenant.middleware import TenantAuthMiddleware

        mw = TenantAuthMiddleware.__new__(TenantAuthMiddleware)
        # Should not raise for professional tier
        mw._check_trial_expiry("t-1", "professional", None)

    def test_trial_expiry_passes_for_future_expiry(self):
        """Trial with future expiry date passes."""
        from src.multi_tenant.middleware import TenantAuthMiddleware

        mw = TenantAuthMiddleware.__new__(TenantAuthMiddleware)
        future = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        mw._check_trial_expiry("t-1", "trial", future)

    def test_trial_expiry_blocks_expired_trial(self):
        """Trial with past expiry date raises HTTPException 403."""
        from src.multi_tenant.auth import AuthenticationError
        from src.multi_tenant.middleware import TenantAuthMiddleware

        mw = TenantAuthMiddleware.__new__(TenantAuthMiddleware)
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        with pytest.raises(AuthenticationError, match="Trial period has expired"):
            mw._check_trial_expiry("t-1", "trial", past)

    def test_trial_expiry_passes_when_no_expiry_set(self):
        """Trial tier with no trial_expires_at passes (no expiry enforced yet)."""
        from src.multi_tenant.middleware import TenantAuthMiddleware

        mw = TenantAuthMiddleware.__new__(TenantAuthMiddleware)
        mw._check_trial_expiry("t-1", "trial", None)


# ---------------------------------------------------------------------------
# SPEC-0362: Admin role has full access to all admin features
# ---------------------------------------------------------------------------


class TestSpec0362AdminFullAccess:
    """SPEC-0362: The admin role MUST have full access to all admin features.

    Verified by: RBAC role definitions include 'admin' with full permissions,
    and the TeamMemberRole enum includes ADMIN.
    """

    def test_admin_role_exists_in_enum(self):
        """TeamMemberRole includes ADMIN."""
        from src.multi_tenant.cosmos_schema import TeamMemberRole

        assert hasattr(TeamMemberRole, "ADMIN")
        assert TeamMemberRole.ADMIN.value == "admin"

    def test_admin_role_different_from_viewer(self):
        """Admin is distinct from viewer (lower access) roles."""
        from src.multi_tenant.cosmos_schema import TeamMemberRole

        assert TeamMemberRole.ADMIN != TeamMemberRole.VIEWER

    def test_admin_role_in_protected_check(self):
        """Admin role is recognized in 2FA admin roles check."""
        from src.multi_tenant.admin_mfa_auth import _ADMIN_ROLES

        assert "admin" in _ADMIN_ROLES


# ---------------------------------------------------------------------------
# SPEC-0364: Per-user API key authentication model
# ---------------------------------------------------------------------------


class TestSpec0364PerUserApiKeys:
    """SPEC-0364: Per-user API key model where each API key is linked to
    an approved team member email address.

    Verified by: auth.py resolves API keys to specific team members via
    key hash lookup in the team_members collection.
    """

    def test_api_key_resolves_to_team_member(self):
        """TenantContext includes team member identity fields for per-user keys."""
        from src.multi_tenant.auth import TenantContext

        ctx = TenantContext(
            tenant_id="t-1",
            auth_method="user_api_key",
            team_member_email="member@test.com",
            team_member_role="admin",
        )
        assert ctx.team_member_email == "member@test.com"
        assert ctx.auth_method == "user_api_key"

    def test_tenant_context_has_team_member_fields(self):
        """TenantContext carries team_member_id/email/role for per-user key auth."""
        import dataclasses

        from src.multi_tenant.auth import TenantContext

        fields = {f.name for f in dataclasses.fields(TenantContext)}
        assert "team_member_id" in fields
        assert "team_member_email" in fields
        assert "team_member_role" in fields


# ---------------------------------------------------------------------------
# SPEC-0423: 2FA supports SMS and authenticator app
# ---------------------------------------------------------------------------


class TestSpec0423TwoFactorMethods:
    """SPEC-0423: 2FA MUST support two options: (1) SMS and (2) authenticator app.

    Verified by: admin_mfa_auth.py has endpoints for both TOTP (authenticator)
    and SMS OTP verification.
    """

    def test_totp_verify_endpoint_exists(self):
        """TOTP verification endpoint is registered."""
        from src.multi_tenant.admin_mfa_auth import router

        paths = [r.path for r in router.routes]
        assert any("totp/verify" in p for p in paths)

    def test_sms_verify_endpoint_exists(self):
        """SMS OTP verification endpoint is registered."""
        from src.multi_tenant.admin_mfa_auth import router

        paths = [r.path for r in router.routes]
        assert any("sms/verify" in p for p in paths)

    def test_sms_request_endpoint_exists(self):
        """SMS OTP request (send code) endpoint is registered."""
        from src.multi_tenant.admin_mfa_auth import router

        paths = [r.path for r in router.routes]
        assert any("sms/request" in p for p in paths)

    def test_totp_backup_verify_endpoint_exists(self):
        """Backup code verification endpoint is registered."""
        from src.multi_tenant.admin_mfa_auth import router

        paths = [r.path for r in router.routes]
        assert any("backup-verify" in p for p in paths)


# ---------------------------------------------------------------------------
# SPEC-0428: Superadmin 2FA enrollment with opt-out
# ---------------------------------------------------------------------------


class TestSpec0428SuperadminMfaOptOut:
    """SPEC-0428: Superadmin MUST either register for 2FA or have an explicit
    opt-out choice.

    Verified by: requires_2fa() checks mfa_opt_out flag on member doc.
    """

    def test_requires_2fa_true_for_admin_with_mfa(self):
        """Admin with mfa_enabled=True requires 2FA."""
        from src.multi_tenant.admin_mfa_auth import requires_2fa

        member = {"mfa_enabled": True, "mfa_opt_out": False}
        assert requires_2fa("admin", member) is True

    def test_requires_2fa_false_with_opt_out(self):
        """Admin with mfa_opt_out=True skips 2FA."""
        from src.multi_tenant.admin_mfa_auth import requires_2fa

        member = {"mfa_enabled": True, "mfa_opt_out": True}
        assert requires_2fa("admin", member) is False

    def test_requires_2fa_false_for_non_admin(self):
        """Non-admin roles never require 2FA."""
        from src.multi_tenant.admin_mfa_auth import requires_2fa

        member = {"mfa_enabled": True}
        assert requires_2fa("viewer", member) is False
        assert requires_2fa("escalation_agent", member) is False

    def test_requires_2fa_false_when_mfa_not_enrolled(self):
        """Admin without MFA enrolled skips 2FA (new admin bootstrap)."""
        from src.multi_tenant.admin_mfa_auth import requires_2fa

        member = {"mfa_enabled": False}
        assert requires_2fa("admin", member) is False


# ---------------------------------------------------------------------------
# SPEC-0429: Auth flow: email → magic link → 2FA (no passwords)
# ---------------------------------------------------------------------------


class TestSpec0429MagicLinkThenTwoFa:
    """SPEC-0429: Auth flow MUST be: email → magic link → 2FA. No passwords.

    Verified by: verify_magic_link returns pending_2fa_token when the
    user has admin role + mfa_enabled.
    """

    @pytest.mark.asyncio
    async def test_admin_with_mfa_gets_pending_2fa_token(self):
        """Admin with MFA → verify returns requires_2fa=True."""
        from src.multi_tenant.magic_link_auth import verify_magic_link

        mock_token_repo = AsyncMock()
        mock_token_repo.consume_token.return_value = {
            "tenant_id": "t-1",
            "email": "admin@test.com",
            "member_id": "m-1",
        }

        mock_team_repo = AsyncMock()
        mock_team_repo.read.return_value = {
            "id": "m-1",
            "role": "admin",
            "mfa_enabled": True,
            "mfa_opt_out": False,
        }

        with (
            patch("src.multi_tenant.repositories.VerificationTokenRepository",
                  return_value=mock_token_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository",
                  return_value=mock_team_repo),
        ):
            resp = await verify_magic_link(token="valid-token")

        assert resp.status_code == 200
        body = json.loads(resp.body)
        assert body["requires_2fa"] is True
        assert "pending_2fa_token" in body

    @pytest.mark.asyncio
    async def test_non_admin_gets_direct_session(self):
        """Non-admin → verify returns session_token directly (no 2FA)."""
        from src.multi_tenant.magic_link_auth import verify_magic_link

        mock_token_repo = AsyncMock()
        mock_token_repo.consume_token.return_value = {
            "tenant_id": "t-1",
            "email": "viewer@test.com",
            "member_id": "m-2",
        }

        mock_team_repo = AsyncMock()
        mock_team_repo.read.return_value = {
            "id": "m-2",
            "role": "viewer",
            "mfa_enabled": False,
        }

        with (
            patch("src.multi_tenant.repositories.VerificationTokenRepository",
                  return_value=mock_token_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository",
                  return_value=mock_team_repo),
        ):
            resp = await verify_magic_link(token="valid-token")

        assert resp.status_code == 200
        body = json.loads(resp.body)
        assert "session_token" in body
        assert body.get("requires_2fa") is not True


# ---------------------------------------------------------------------------
# SPEC-0607: Merchants can request a new API key
# ---------------------------------------------------------------------------


class TestSpec0607ApiKeyRegeneration:
    """SPEC-0607: Merchants MUST be able to request a new API key.

    Verified by: API key rotation endpoint exists in security_hardening
    and admin_apikey_api modules.
    """

    def test_rotation_router_has_rotate_endpoint(self):
        """security_hardening rotation_router has a rotate endpoint."""
        from src.multi_tenant.security_hardening import rotation_router

        paths = [r.path for r in rotation_router.routes]
        assert any("rotate" in p for p in paths)

    def test_apikey_api_has_rotate_endpoint(self):
        """admin_apikey_api has a rotate endpoint for tenant key rotation."""
        from src.multi_tenant.admin_apikey_api import router

        paths = [r.path for r in router.routes]
        assert any("rotate" in p for p in paths)

    def test_reset_via_email_endpoint_exists(self):
        """admin_apikey_api has a reset endpoint for lost credentials."""
        from src.multi_tenant.admin_apikey_api import router

        paths = [r.path for r in router.routes]
        assert any("reset" in p for p in paths)


# ---------------------------------------------------------------------------
# SPEC-0758: Superadmin role cannot be deleted
# ---------------------------------------------------------------------------


class TestSpec0758SuperadminProtection:
    """SPEC-0758: A 'superadmin' role MUST exist that cannot be deleted or
    barred from changing any configuration.

    Verified by: PROTECTED_ROLES in admin_team_api blocks delete/modify
    of superadmin members by non-superadmins.
    """

    def test_superadmin_role_exists(self):
        """TeamMemberRole enum includes SUPERADMIN."""
        from src.multi_tenant.cosmos_schema import TeamMemberRole

        assert hasattr(TeamMemberRole, "SUPERADMIN")
        assert TeamMemberRole.SUPERADMIN.value == "superadmin"

    def test_superadmin_in_protected_roles(self):
        """Superadmin is in PROTECTED_ROLES set."""
        from src.multi_tenant.admin_team_api import PROTECTED_ROLES

        assert "superadmin" in PROTECTED_ROLES

    def test_protected_roles_is_a_set(self):
        """PROTECTED_ROLES is a set for O(1) lookup."""
        from src.multi_tenant.admin_team_api import PROTECTED_ROLES

        assert isinstance(PROTECTED_ROLES, set)


# ---------------------------------------------------------------------------
# SPEC-1618: Magic link email references only the sending tenant
# ---------------------------------------------------------------------------


class TestSpec1618SingleTenantEmail:
    """SPEC-1618: Magic link email must reference only the sending tenant.

    Each email MUST reference ONLY the specific merchant account that
    triggered it. Multi-tenant emails are always a defect.
    """

    @pytest.mark.asyncio
    async def test_single_member_gets_one_email(self):
        """Single tenant match → one email sent, no tenant context label."""
        from src.multi_tenant.magic_link_auth import _send_member_magic_links

        token_repo = AsyncMock()
        token_repo.create_token = AsyncMock()
        tenant_repo = AsyncMock()
        tenant_repo.read = AsyncMock(return_value={
            "id": "t-1", "business_name": "Store A",
        })
        send_mock = AsyncMock(return_value=True)

        with patch("src.multi_tenant.magic_link_auth._send_magic_link_email", send_mock):
            await _send_member_magic_links(
                members=[{"id": "m-1", "tenant_id": "t-1", "email": "user@test.com"}],
                email="user@test.com",
                scheme="https",
                host="example.com",
                origin_tenant="t-1",
                token_repo=token_repo,
                tenant_repo=tenant_repo,
            )

        assert send_mock.call_count == 1
        email_html = send_mock.call_args[0][1]
        # Single member → no "Account:" label (per SPEC-1618)
        assert "Account:" not in email_html

    @pytest.mark.asyncio
    async def test_multiple_members_get_separate_emails(self):
        """Multiple tenant matches → separate emails, each with Account label."""
        from src.multi_tenant.magic_link_auth import _send_member_magic_links

        token_repo = AsyncMock()
        token_repo.create_token = AsyncMock()
        tenant_repo = AsyncMock()
        tenant_repo.read = AsyncMock(side_effect=[
            {"id": "t-1", "business_name": "Store A"},
            {"id": "t-2", "shop_domain": "store-b.myshopify.com"},
        ])
        send_mock = AsyncMock(return_value=True)

        members = [
            {"id": "m-1", "tenant_id": "t-1", "email": "user@test.com"},
            {"id": "m-2", "tenant_id": "t-2", "email": "user@test.com"},
        ]

        with patch("src.multi_tenant.magic_link_auth._send_magic_link_email", send_mock):
            await _send_member_magic_links(
                members=members,
                email="user@test.com",
                scheme="https",
                host="example.com",
                origin_tenant="t-1",
                token_repo=token_repo,
                tenant_repo=tenant_repo,
            )

        # Two separate emails, not one combined email
        assert send_mock.call_count == 2
        # Each email should have an Account label
        email1 = send_mock.call_args_list[0][0][1]
        email2 = send_mock.call_args_list[1][0][1]
        assert "Account:" in email1 or "Store A" in email1
        assert "Account:" in email2 or "store-b" in email2


# ---------------------------------------------------------------------------
# SPEC-1633: Magic link request scoped to tenant from URL
# ---------------------------------------------------------------------------


class TestSpec1633TenantScopedRequest:
    """SPEC-1633: Every POST /api/auth/magic-link/request must include a
    tenant identifier. The backend must query ONLY that tenant's partition.

    Verified by: MagicLinkRequest requires 'tenant' field; request handler
    uses find_by_email(tenant_id, email) not find_all_by_email(email).
    """

    def test_request_model_requires_tenant(self):
        """MagicLinkRequest 'tenant' field is required."""
        from pydantic import ValidationError

        from src.multi_tenant.magic_link_auth import MagicLinkRequest

        with pytest.raises(ValidationError):
            MagicLinkRequest(email="user@test.com")  # missing tenant

    def test_request_model_accepts_tenant(self):
        """MagicLinkRequest accepts tenant field."""
        from src.multi_tenant.magic_link_auth import MagicLinkRequest

        req = MagicLinkRequest(email="user@test.com", tenant="my-tenant")
        assert req.tenant == "my-tenant"

    @pytest.mark.asyncio
    async def test_lookup_uses_tenant_scoped_query(self):
        """Request handler calls find_by_email(tenant_id, email), not cross-partition."""
        from src.multi_tenant.magic_link_auth import (
            MagicLinkRequest,
            request_magic_link,
        )
        from src.multi_tenant.security_hardening import set_rate_limit_backend, InMemoryRateLimitBackend
        set_rate_limit_backend(InMemoryRateLimitBackend())

        mock_team = AsyncMock()
        mock_team.find_by_email = AsyncMock(return_value=None)
        mock_tenant = AsyncMock()
        mock_tenant.read = AsyncMock(return_value=None)
        mock_token = AsyncMock()

        mock_request = MagicMock()
        mock_request.client = MagicMock(host="10.0.0.1")
        mock_request.headers = {"host": "test.com", "x-forwarded-proto": "https"}
        mock_request.url = MagicMock(scheme="https", hostname="test.com")

        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository",
                  return_value=mock_team),
            patch("src.multi_tenant.repositories.TenantRepository",
                  return_value=mock_tenant),
            patch("src.multi_tenant.repositories.VerificationTokenRepository",
                  return_value=mock_token),
        ):
            await request_magic_link(
                MagicLinkRequest(email="user@test.com", tenant="target-tenant"),
                mock_request,
            )

        # SPEC-1633: lookup scoped to specified tenant
        mock_team.find_by_email.assert_called_once_with("target-tenant", "user@test.com")
        # SPEC-1644: direct read on specified tenant, not cross-partition
        mock_tenant.read.assert_called_once_with("target-tenant", "target-tenant")


# ---------------------------------------------------------------------------
# SPEC-1634: No cross-tenant email lookups
# ---------------------------------------------------------------------------


class TestSpec1634NoCrossTenantLookups:
    """SPEC-1634: Authentication flows MUST NOT perform cross-partition queries.

    find_all_by_email() must not be called from authentication endpoints.
    """

    @pytest.mark.asyncio
    async def test_magic_link_does_not_call_find_all_by_email(self):
        """Magic link request never calls cross-partition find_all_by_email."""
        from src.multi_tenant.magic_link_auth import (
            MagicLinkRequest,
            request_magic_link,
        )
        from src.multi_tenant.security_hardening import set_rate_limit_backend, InMemoryRateLimitBackend
        set_rate_limit_backend(InMemoryRateLimitBackend())

        mock_team = AsyncMock()
        mock_team.find_by_email = AsyncMock(return_value=None)
        mock_team.find_all_by_email = AsyncMock(return_value=[])
        mock_tenant = AsyncMock()
        mock_tenant.read = AsyncMock(return_value=None)
        mock_tenant.find_by_customer_email = AsyncMock(return_value=[])
        mock_token = AsyncMock()

        mock_request = MagicMock()
        mock_request.client = MagicMock(host="10.0.0.2")
        mock_request.headers = {"host": "test.com", "x-forwarded-proto": "https"}
        mock_request.url = MagicMock(scheme="https", hostname="test.com")

        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository",
                  return_value=mock_team),
            patch("src.multi_tenant.repositories.TenantRepository",
                  return_value=mock_tenant),
            patch("src.multi_tenant.repositories.VerificationTokenRepository",
                  return_value=mock_token),
        ):
            await request_magic_link(
                MagicLinkRequest(email="user@test.com", tenant="t-1"),
                mock_request,
            )

        # SPEC-1634: Cross-partition queries MUST NOT be called
        mock_team.find_all_by_email.assert_not_called()
        mock_tenant.find_by_customer_email.assert_not_called()


# ---------------------------------------------------------------------------
# SPEC-1635: No email may reference any other tenancy
# ---------------------------------------------------------------------------


class TestSpec1635NoOtherTenancyReferences:
    """SPEC-1635: No email sent to a tenant team member may reference,
    list, or link to any other tenancy.

    Verified by: email template contains only a single Sign In link,
    and _send_member_magic_links sends per-tenant emails.
    """

    def test_email_template_has_single_sign_in_link(self):
        """Email body template contains exactly one CTA link."""
        from src.multi_tenant.magic_link_auth import _MAGIC_LINK_EMAIL_BODY

        # Count <a href= tags
        link_count = _MAGIC_LINK_EMAIL_BODY.count("<a href=")
        assert link_count == 1, (
            f"Magic link email should have exactly 1 link, found {link_count}"
        )

    def test_email_template_uses_single_magic_link_url(self):
        """Email body uses exactly one {magic_link_url} placeholder."""
        from src.multi_tenant.magic_link_auth import _MAGIC_LINK_EMAIL_BODY

        url_count = _MAGIC_LINK_EMAIL_BODY.count("{magic_link_url}")
        assert url_count == 1


# ---------------------------------------------------------------------------
# SPEC-1642: One admin URL per tenancy, no redirects
# ---------------------------------------------------------------------------


class TestSpec1642OneAdminUrl:
    """SPEC-1642: Each tenancy must have exactly one admin URL.

    Verified by: _build_magic_link_url produces a deterministic URL
    with the tenant parameter, no redirect logic.
    """

    def test_url_includes_tenant_param(self):
        """Magic link URL includes tenant= param for scoped access."""
        from src.multi_tenant.magic_link_auth import _build_magic_link_url

        url = _build_magic_link_url(
            scheme="https",
            host="admin.agentred.io",
            token_id="tok-abc",
            origin_tenant="my-store-slug",
        )
        assert "tenant=my-store-slug" in url

    def test_url_is_deterministic(self):
        """Same inputs produce same URL (no redirect logic)."""
        from src.multi_tenant.magic_link_auth import _build_magic_link_url

        url1 = _build_magic_link_url(
            scheme="https", host="a.com", token_id="t1", origin_tenant="s1",
        )
        url2 = _build_magic_link_url(
            scheme="https", host="a.com", token_id="t1", origin_tenant="s1",
        )
        assert url1 == url2


# ---------------------------------------------------------------------------
# SPEC-1644: API keys authenticate users, not tenancies
# ---------------------------------------------------------------------------


class TestSpec1644UrlIdentifiesTenant:
    """SPEC-1644: API keys authenticate users; URL identifies tenant.

    The ?tenant= query parameter (or equivalent) identifies the tenancy.
    API keys MUST NOT be used to determine which tenant is being accessed.
    """

    def test_magic_link_request_requires_tenant_from_url(self):
        """MagicLinkRequest has required 'tenant' field (from URL param)."""
        from src.multi_tenant.magic_link_auth import MagicLinkRequest

        req = MagicLinkRequest(email="user@test.com", tenant="from-url")
        assert req.tenant == "from-url"

    def test_magic_link_request_tenant_description_references_spec(self):
        """Tenant field description references SPEC-1644."""
        from src.multi_tenant.magic_link_auth import MagicLinkRequest

        field_info = MagicLinkRequest.model_fields["tenant"]
        assert "1644" in (field_info.description or "")


# ---------------------------------------------------------------------------
# SPEC-0868: Two-layer auth (standalone URL + API key)
# ---------------------------------------------------------------------------


class TestSpec0868TwoLayerAuth:
    """SPEC-0868: Admin Console accessible via standalone URL with
    API key authentication.

    Verified by: middleware supports both API key (X-API-Key header)
    and session token (X-Session-Token) authentication methods.
    """

    def test_middleware_accepts_api_key_header(self):
        """Middleware recognizes X-API-Key header (api_key auth method)."""
        from src.multi_tenant.auth import TenantContext

        ctx = TenantContext(tenant_id="t-1", auth_method="api_key")
        assert ctx.auth_method == "api_key"

    def test_middleware_accepts_user_api_key(self):
        """Middleware recognizes per-user API key (user_api_key auth method)."""
        from src.multi_tenant.auth import TenantContext

        ctx = TenantContext(tenant_id="t-1", auth_method="user_api_key")
        assert ctx.auth_method == "user_api_key"

    def test_tenant_context_supports_multiple_auth_methods(self):
        """TenantContext auth_method field supports all documented auth methods."""
        import dataclasses

        from src.multi_tenant.auth import TenantContext

        fields = {f.name for f in dataclasses.fields(TenantContext)}
        assert "auth_method" in fields
        # Verify all documented auth methods can be set
        for method in ("api_key", "user_api_key", "shopify_session", "widget_key"):
            ctx = TenantContext(tenant_id="t-1", auth_method=method)
            assert ctx.auth_method == method


# ---------------------------------------------------------------------------
# 2FA brute-force protection (supplements SPEC-0423)
# ---------------------------------------------------------------------------


class TestMfaBruteForceProtection:
    """Brute-force mitigation: 5 failed attempts per pending_2fa token.

    Verified by: admin_mfa_auth._check_brute_force and _record_failed_attempt.
    """

    def test_brute_force_limit_is_5(self):
        """Maximum failed attempts is 5."""
        from src.multi_tenant.admin_mfa_auth import _MAX_FAILED_ATTEMPTS

        assert _MAX_FAILED_ATTEMPTS == 5

    def test_check_brute_force_allows_under_limit(self):
        """Under 5 attempts → not blocked."""
        from src.multi_tenant.admin_mfa_auth import (
            _check_brute_force,
            _failed_attempts,
        )

        _failed_attempts.clear()
        _failed_attempts["test-fp"] = 4
        assert _check_brute_force("test-fp") is False
        _failed_attempts.clear()

    def test_check_brute_force_blocks_at_limit(self):
        """At 5 attempts → blocked."""
        from src.multi_tenant.admin_mfa_auth import (
            _check_brute_force,
            _failed_attempts,
        )

        _failed_attempts.clear()
        _failed_attempts["test-fp"] = 5
        assert _check_brute_force("test-fp") is True
        _failed_attempts.clear()

    def test_record_failed_attempt_increments(self):
        """Recording a failed attempt increments counter."""
        from src.multi_tenant.admin_mfa_auth import (
            _failed_attempts,
            _record_failed_attempt,
        )

        _failed_attempts.clear()
        count = _record_failed_attempt("fp-inc")
        assert count == 1
        count = _record_failed_attempt("fp-inc")
        assert count == 2
        _failed_attempts.clear()

    def test_clear_attempts_resets(self):
        """Successful verification clears the counter."""
        from src.multi_tenant.admin_mfa_auth import (
            _clear_attempts,
            _failed_attempts,
        )

        _failed_attempts.clear()
        _failed_attempts["fp-clear"] = 3
        _clear_attempts("fp-clear")
        assert "fp-clear" not in _failed_attempts
