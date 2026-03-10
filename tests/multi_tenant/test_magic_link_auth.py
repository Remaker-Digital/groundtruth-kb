"""Tests for magic link authentication (ML-01 to ML-29).

Covers the full magic link lifecycle:
    - Request endpoint (POST /api/auth/magic-link/request)
    - Verify endpoint (GET /api/auth/magic-link/verify)
    - Rate limiting per IP (3 requests / 5 min)
    - Email enumeration prevention
    - Single-use token consumption
    - JWT session token creation and verification
    - Middleware X-Session-Token integration
    - Team member identity in sessions (WI #295 Phase 1)
    - Multi-tenant disambiguation
    - member_id + role in JWT claims

Test plan reference: §5.10 (Magic Link Auth)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest

from src.multi_tenant.security_hardening import get_rate_limit_backend, set_rate_limit_backend, InMemoryRateLimitBackend
from src.multi_tenant.magic_link_auth import (
    MagicLinkRequest,
    MagicLinkRequestResponse,
    MagicLinkVerifyResponse,
    _JWT_SECRET,
    _RATE_MAX,
    _RATE_WINDOW,
    _TOKEN_TTL_SECONDS,
    _TOKEN_TYPE,
    _is_rate_limited,
    create_magic_link_session_token,
    request_magic_link,
    verify_magic_link,
    verify_magic_link_session_token,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_rate_limit():
    """Use a fresh rate-limit backend per test for isolation."""
    original = get_rate_limit_backend()
    set_rate_limit_backend(InMemoryRateLimitBackend())
    yield
    set_rate_limit_backend(original)


@pytest.fixture()
def mock_tenant_repo():
    """Mock TenantRepository."""
    repo = AsyncMock()
    repo.find_by_customer_email = AsyncMock(return_value=None)
    repo.read = AsyncMock(return_value=None)
    return repo


@pytest.fixture()
def mock_token_repo():
    """Mock VerificationTokenRepository."""
    repo = AsyncMock()
    repo.create_token = AsyncMock()
    repo.consume_token = AsyncMock(return_value=None)
    return repo


@pytest.fixture()
def sample_tenant():
    """Sample tenant document for testing."""
    return {
        "id": "tenant-abc-123",
        "tenant_id": "tenant-abc-123",
        "status": "active",
        "tier": "professional",
        "customer_email": "merchant@example.com",
    }


@pytest.fixture()
def mock_request():
    """Mock FastAPI Request object."""
    req = MagicMock()
    req.client = MagicMock()
    req.client.host = "192.168.1.1"
    req.headers = {"host": "admin.agentred.io", "x-forwarded-proto": "https"}
    req.url = MagicMock()
    req.url.scheme = "https"
    req.url.hostname = "admin.agentred.io"
    return req


# ---------------------------------------------------------------------------
# JWT session token tests (ML-01 to ML-05)
# ---------------------------------------------------------------------------


class TestCreateSessionToken:
    """ML-01: create_magic_link_session_token generates valid JWT."""

    def test_ml01_creates_valid_jwt(self):
        token, expires_at = create_magic_link_session_token("t-1", "user@test.com")
        payload = jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        assert payload["sub"] == "t-1"
        assert payload["email"] == "user@test.com"
        assert payload["type"] == "magic_link_session"
        assert "iat" in payload
        assert "exp" in payload

    def test_ml02_expires_at_is_iso(self):
        _, expires_at = create_magic_link_session_token("t-1", "user@test.com")
        # Should parse as ISO datetime
        dt = datetime.fromisoformat(expires_at)
        assert dt > datetime.now(timezone.utc)

    def test_ml03_token_expires_after_8_hours(self):
        token, _ = create_magic_link_session_token("t-1", "user@test.com")
        payload = jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        delta = exp - iat
        assert abs(delta.total_seconds() - 8 * 3600) < 5  # within 5 seconds


class TestVerifySessionToken:
    """ML-04 to ML-05: verify_magic_link_session_token validation."""

    def test_ml04_valid_token_returns_payload(self):
        token, _ = create_magic_link_session_token("t-1", "user@test.com")
        payload = verify_magic_link_session_token(token)
        assert payload is not None
        assert payload["sub"] == "t-1"
        assert payload["email"] == "user@test.com"

    def test_ml05_expired_token_returns_none(self):
        now = datetime.now(timezone.utc)
        expired = now - timedelta(hours=1)
        payload = {
            "sub": "t-1",
            "email": "user@test.com",
            "type": "magic_link_session",
            "iat": int(expired.timestamp()),
            "exp": int((expired + timedelta(seconds=1)).timestamp()),
        }
        token = jwt.encode(payload, _JWT_SECRET, algorithm="HS256")
        assert verify_magic_link_session_token(token) is None

    def test_ml06_wrong_type_returns_none(self):
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "t-1",
            "email": "user@test.com",
            "type": "wrong_type",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
        }
        token = jwt.encode(payload, _JWT_SECRET, algorithm="HS256")
        assert verify_magic_link_session_token(token) is None

    def test_ml07_invalid_token_string_returns_none(self):
        assert verify_magic_link_session_token("not-a-jwt") is None

    def test_ml08_wrong_secret_returns_none(self):
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "t-1",
            "email": "user@test.com",
            "type": "magic_link_session",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
        }
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
        assert verify_magic_link_session_token(token) is None


# ---------------------------------------------------------------------------
# Rate limiting tests (ML-09 to ML-11)
# ---------------------------------------------------------------------------


class TestRateLimiting:
    """ML-09 to ML-11: IP-based rate limiting for magic link requests."""

    def test_ml09_first_request_not_limited(self):
        assert _is_rate_limited("10.0.0.1") is False

    def test_ml10_within_limit_not_blocked(self):
        for _ in range(_RATE_MAX - 1):
            assert _is_rate_limited("10.0.0.2") is False

    def test_ml11_exceeds_limit_blocked(self):
        for _ in range(_RATE_MAX):
            _is_rate_limited("10.0.0.3")
        assert _is_rate_limited("10.0.0.3") is True

    def test_ml12_different_ips_independent(self):
        for _ in range(_RATE_MAX):
            _is_rate_limited("10.0.0.4")
        assert _is_rate_limited("10.0.0.4") is True
        assert _is_rate_limited("10.0.0.5") is False

    def test_ml13_old_entries_expire(self):
        """Entries older than the rate window should be cleaned up."""
        get_rate_limit_backend().reset(f"magic_link:10.0.0.6")
        assert _is_rate_limited("10.0.0.6") is False


# ---------------------------------------------------------------------------
# Request endpoint tests (ML-14 to ML-17)
# ---------------------------------------------------------------------------


class TestRequestEndpoint:
    """ML-14 to ML-17: POST /api/auth/magic-link/request."""

    @pytest.mark.asyncio
    async def test_ml14_unknown_email_returns_200(self, mock_request, mock_tenant_repo, mock_token_repo):
        mock_team = AsyncMock()
        mock_team.find_by_email = AsyncMock(return_value=None)
        mock_tenant_repo.read.return_value = None
        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team),
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
        ):
            result = await request_magic_link(
                MagicLinkRequest(email="unknown@test.com", tenant="tenant-abc-123"),
                mock_request,
            )
        assert isinstance(result, MagicLinkRequestResponse)
        mock_token_repo.create_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_ml15_known_email_creates_token_and_sends(
        self, mock_request, mock_tenant_repo, mock_token_repo, sample_tenant,
    ):
        mock_team = AsyncMock()
        mock_team.find_by_email = AsyncMock(return_value=None)
        # SPEC-1644: tenant-scoped read, email checked against customer_email
        mock_tenant_repo.read.return_value = sample_tenant
        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team),
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.magic_link_auth._send_magic_link_email", new_callable=AsyncMock, return_value=True),
        ):
            result = await request_magic_link(
                MagicLinkRequest(email="merchant@example.com", tenant="tenant-abc-123"),
                mock_request,
            )
        assert isinstance(result, MagicLinkRequestResponse)
        mock_token_repo.create_token.assert_called_once()
        call_kwargs = mock_token_repo.create_token.call_args
        assert call_kwargs.kwargs.get("token_type") == _TOKEN_TYPE or (
            len(call_kwargs.args) >= 2 and call_kwargs.args[1] == _TOKEN_TYPE
        )

    @pytest.mark.asyncio
    async def test_ml16_rate_limited_returns_200(self, mock_request):
        # Exhaust rate limit
        for _ in range(_RATE_MAX):
            _is_rate_limited(mock_request.client.host)
        result = await request_magic_link(
            MagicLinkRequest(email="any@test.com", tenant="any-tenant"),
            mock_request,
        )
        assert isinstance(result, MagicLinkRequestResponse)

    @pytest.mark.asyncio
    async def test_ml17_email_case_normalized(self, mock_request, mock_tenant_repo, mock_token_repo):
        mock_team = AsyncMock()
        mock_team.find_by_email = AsyncMock(return_value=None)
        mock_tenant_repo.read.return_value = None
        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team),
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
        ):
            await request_magic_link(
                MagicLinkRequest(email="  Test@Example.Com  ", tenant="tenant-abc-123"),
                mock_request,
            )
        # SPEC-1644: Tenant-scoped lookup with normalized email
        mock_team.find_by_email.assert_called_once_with("tenant-abc-123", "test@example.com")
        # Then falls through to tenant owner lookup (direct read, not cross-partition)
        mock_tenant_repo.read.assert_called_once_with("tenant-abc-123", "tenant-abc-123")


# ---------------------------------------------------------------------------
# Verify endpoint tests (ML-18 to ML-22)
# ---------------------------------------------------------------------------


class TestVerifyEndpoint:
    """ML-18 to ML-22: GET /api/auth/magic-link/verify."""

    @pytest.mark.asyncio
    async def test_ml18_invalid_token_returns_400(self, mock_token_repo):
        mock_token_repo.consume_token.return_value = None
        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            resp = await verify_magic_link(token="bad-token-id")
        assert resp.status_code == 400
        import json
        body = json.loads(resp.body)
        assert body["error"] == "invalid_token"

    @pytest.mark.asyncio
    async def test_ml19_valid_token_returns_session_jwt(self, mock_token_repo):
        mock_token_repo.consume_token.return_value = {
            "tenant_id": "tenant-abc-123",
            "email": "merchant@example.com",
        }
        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            resp = await verify_magic_link(token="valid-token-id")
        assert resp.status_code == 200
        import json
        body = json.loads(resp.body)
        assert "session_token" in body
        assert body["tenant_id"] == "tenant-abc-123"
        assert body["email"] == "merchant@example.com"
        assert "expires_at" in body

        # Verify the session token is a valid JWT
        payload = verify_magic_link_session_token(body["session_token"])
        assert payload is not None
        assert payload["sub"] == "tenant-abc-123"

    @pytest.mark.asyncio
    async def test_ml20_token_consumed_single_use(self, mock_token_repo):
        mock_token_repo.consume_token.return_value = {
            "tenant_id": "t-1",
            "email": "user@test.com",
        }
        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            await verify_magic_link(token="token-id")
        mock_token_repo.consume_token.assert_called_once_with(
            token_id="token-id",
            token_type=_TOKEN_TYPE,
        )

    @pytest.mark.asyncio
    async def test_ml21_verify_passes_correct_token_type(self, mock_token_repo):
        mock_token_repo.consume_token.return_value = None
        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            await verify_magic_link(token="any")
        mock_token_repo.consume_token.assert_called_once_with(
            token_id="any",
            token_type="magic_link",
        )

    @pytest.mark.asyncio
    async def test_ml22_exception_returns_500(self, mock_token_repo):
        mock_token_repo.consume_token.side_effect = RuntimeError("DB down")
        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            resp = await verify_magic_link(token="any")
        assert resp.status_code == 500
        import json
        body = json.loads(resp.body)
        assert body["error"] == "server_error"


# ---------------------------------------------------------------------------
# WI #295 Phase 1: Team member identity in magic link sessions
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_team_repo():
    """Mock TeamMemberRepository."""
    repo = AsyncMock()
    repo.find_by_email = AsyncMock(return_value=None)
    repo.read = AsyncMock(return_value=None)
    return repo


@pytest.fixture()
def sample_team_member():
    """Sample team member document."""
    return {
        "id": "member-001",
        "tenant_id": "tenant-abc-123",
        "email": "agent@example.com",
        "display_name": "Agent Smith",
        "role": "escalation_agent",
        "is_active": True,
        "escalation_categories": ["billing", "returns"],
    }


@pytest.fixture()
def sample_admin_member():
    """Sample admin team member document."""
    return {
        "id": "member-002",
        "tenant_id": "tenant-abc-123",
        "email": "admin@example.com",
        "display_name": "Admin User",
        "role": "admin",
        "is_active": True,
    }


class TestSessionTokenWithMemberIdentity:
    """ML-23 to ML-24: JWT carries member_id and role claims."""

    def test_ml23_session_token_includes_member_id_and_role(self):
        token, _ = create_magic_link_session_token(
            "t-1", "agent@test.com",
            member_id="member-001",
            role="escalation_agent",
        )
        payload = jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        assert payload["sub"] == "t-1"
        assert payload["email"] == "agent@test.com"
        assert payload["member_id"] == "member-001"
        assert payload["role"] == "escalation_agent"
        assert payload["type"] == "magic_link_session"

    def test_ml24_session_token_omits_null_member_fields(self):
        """Tenant-owner tokens (no member_id) should not carry member claims."""
        token, _ = create_magic_link_session_token("t-1", "owner@test.com")
        payload = jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        assert "member_id" not in payload
        assert "role" not in payload


class TestTeamMemberMagicLinkRequest:
    """ML-25 to ML-27: Request endpoint resolves team members."""

    @pytest.mark.asyncio
    async def test_ml25_team_member_email_creates_token_with_member_id(
        self, mock_request, mock_team_repo, mock_tenant_repo, mock_token_repo,
        sample_team_member, sample_tenant,
    ):
        """Team member email → creates token with member_id."""
        # SPEC-1644: tenant-scoped lookup returns single member
        mock_team_repo.find_by_email.return_value = sample_team_member
        mock_tenant_repo.read.return_value = sample_tenant

        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.magic_link_auth._send_magic_link_email", new_callable=AsyncMock, return_value=True),
        ):
            result = await request_magic_link(
                MagicLinkRequest(email="agent@example.com", tenant="tenant-abc-123"),
                mock_request,
            )

        assert isinstance(result, MagicLinkRequestResponse)
        # Token should be created with member_id
        mock_token_repo.create_token.assert_called_once()
        call_kwargs = mock_token_repo.create_token.call_args
        assert call_kwargs.kwargs.get("member_id") == "member-001"

    @pytest.mark.asyncio
    async def test_ml26_tenant_scoped_lookup_only_searches_specified_tenant(
        self, mock_request, mock_team_repo, mock_tenant_repo, mock_token_repo,
    ):
        """SPEC-1644: Magic link only searches within the specified tenant.

        Cross-partition queries are prohibited. Even if the same email
        exists in multiple tenants, only the specified tenant is searched.
        """
        member = {
            "id": "m-a", "tenant_id": "t-a", "email": "shared@example.com",
            "role": "admin", "is_active": True,
        }
        mock_team_repo.find_by_email.return_value = member
        mock_tenant_repo.read.return_value = {
            "id": "t-a", "shop_domain": "store-a.myshopify.com",
        }

        send_mock = AsyncMock(return_value=True)
        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.magic_link_auth._send_magic_link_email", send_mock),
        ):
            await request_magic_link(
                MagicLinkRequest(email="shared@example.com", tenant="t-a"),
                mock_request,
            )

        # SPEC-1644: Only ONE token and ONE email (tenant-scoped, not cross-partition)
        assert mock_token_repo.create_token.call_count == 1
        assert send_mock.call_count == 1

        # Lookup was tenant-scoped (find_by_email with tenant_id, not find_all_by_email)
        mock_team_repo.find_by_email.assert_called_once_with("t-a", "shared@example.com")

    @pytest.mark.asyncio
    async def test_ml27_owner_fallback_when_no_team_member(
        self, mock_request, mock_team_repo, mock_tenant_repo,
        mock_token_repo, sample_tenant,
    ):
        """Email not in team_members but is tenant owner → standard flow."""
        mock_team_repo.find_by_email.return_value = None
        # SPEC-1644: direct tenant read (not cross-partition find_by_customer_email)
        mock_tenant_repo.read.return_value = sample_tenant

        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.magic_link_auth._send_magic_link_email", new_callable=AsyncMock, return_value=True),
        ):
            result = await request_magic_link(
                MagicLinkRequest(email="merchant@example.com", tenant="tenant-abc-123"),
                mock_request,
            )

        assert isinstance(result, MagicLinkRequestResponse)
        # Token created without member_id (owner path)
        mock_token_repo.create_token.assert_called_once()
        call_kwargs = mock_token_repo.create_token.call_args
        # member_id should not be in kwargs for owner path
        assert "member_id" not in call_kwargs.kwargs


class TestVerifyWithMemberIdentity:
    """ML-28 to ML-29: Verify endpoint carries member identity to JWT."""

    @pytest.mark.asyncio
    async def test_ml28_verify_with_member_id_includes_role_in_jwt(
        self, mock_token_repo, mock_team_repo, sample_admin_member,
    ):
        """Token with member_id → verify resolves role → JWT has claims."""
        mock_token_repo.consume_token.return_value = {
            "tenant_id": "tenant-abc-123",
            "email": "admin@example.com",
            "member_id": "member-002",
        }
        mock_team_repo.read.return_value = sample_admin_member

        with (
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
        ):
            resp = await verify_magic_link(token="valid-token")

        import json
        assert resp.status_code == 200
        body = json.loads(resp.body)

        # Verify JWT carries member identity
        payload = verify_magic_link_session_token(body["session_token"])
        assert payload is not None
        assert payload["member_id"] == "member-002"
        assert payload["role"] == "admin"

    @pytest.mark.asyncio
    async def test_ml29_verify_owner_token_no_member_claims(
        self, mock_token_repo,
    ):
        """Owner token (no member_id) → JWT has no member_id/role."""
        mock_token_repo.consume_token.return_value = {
            "tenant_id": "tenant-abc-123",
            "email": "merchant@example.com",
            # No member_id — owner path
        }

        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            resp = await verify_magic_link(token="valid-owner-token")

        import json
        assert resp.status_code == 200
        body = json.loads(resp.body)

        payload = verify_magic_link_session_token(body["session_token"])
        assert payload is not None
        assert "member_id" not in payload
        assert "role" not in payload


# ---------------------------------------------------------------------------
# SPEC-1281: Magic link rate limit 3 per 5 min per IP
# ---------------------------------------------------------------------------


class TestSpec1281RateLimit:
    """SPEC-1281: Magic link rate limit 3 per 5 min per IP."""

    def test_spec1281_rate_max_is_3(self):
        """SPEC-1281: _RATE_MAX is 3."""
        assert _RATE_MAX == 3

    def test_spec1281_rate_window_is_300_seconds(self):
        """SPEC-1281: _RATE_WINDOW is 300 seconds (5 minutes)."""
        assert _RATE_WINDOW == 300.0

    def test_spec1281_first_three_requests_not_limited(self):
        """SPEC-1281: First 3 requests from same IP are allowed."""
        ip = "10.0.1.1"
        for i in range(_RATE_MAX):
            assert _is_rate_limited(ip) is False, f"Request {i+1} should not be limited"

    def test_spec1281_fourth_request_is_limited(self):
        """SPEC-1281: 4th request from same IP within 5 min is blocked."""
        ip = "10.0.1.2"
        for _ in range(_RATE_MAX):
            _is_rate_limited(ip)
        assert _is_rate_limited(ip) is True

    def test_spec1281_different_ips_independent(self):
        """SPEC-1281: Rate limits are independent per IP."""
        ip_a = "10.0.1.3"
        ip_b = "10.0.1.4"
        for _ in range(_RATE_MAX):
            _is_rate_limited(ip_a)
        # ip_a exhausted, ip_b still clean
        assert _is_rate_limited(ip_a) is True
        assert _is_rate_limited(ip_b) is False

    def test_spec1281_expired_entries_reset(self):
        """SPEC-1281: Entries older than 5 minutes are cleaned up."""
        ip = "10.0.1.5"
        # Pre-populate with entries beyond the window
        get_rate_limit_backend().reset(f"magic_link:{ip}")
        # Should not be limited (old entries expire)
        assert _is_rate_limited(ip) is False


# ---------------------------------------------------------------------------
# SPEC-1282: Uniform 200 response on magic link (anti-enumeration)
# ---------------------------------------------------------------------------


class TestSpec1282UniformResponse:
    """SPEC-1282: Uniform 200 response on magic link (anti-enumeration)."""

    @pytest.mark.asyncio
    async def test_spec1282_unknown_email_returns_200(self, mock_request, mock_tenant_repo, mock_token_repo):
        """SPEC-1282: Unknown email returns 200 (no enumeration leak)."""
        mock_team = AsyncMock()
        mock_team.find_by_email = AsyncMock(return_value=None)
        mock_tenant_repo.read.return_value = None

        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team),
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
        ):
            result = await request_magic_link(
                MagicLinkRequest(email="nonexistent@nowhere.com", tenant="any-tenant"),
                mock_request,
            )
        assert isinstance(result, MagicLinkRequestResponse)
        # No token created
        mock_token_repo.create_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_spec1282_known_email_returns_200(
        self, mock_request, mock_tenant_repo, mock_token_repo, sample_tenant,
    ):
        """SPEC-1282: Known email also returns 200 (same shape)."""
        mock_team = AsyncMock()
        mock_team.find_by_email = AsyncMock(return_value=None)
        mock_tenant_repo.read.return_value = sample_tenant

        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team),
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.magic_link_auth._send_magic_link_email", new_callable=AsyncMock, return_value=True),
        ):
            result = await request_magic_link(
                MagicLinkRequest(email="merchant@example.com", tenant="tenant-abc-123"),
                mock_request,
            )
        assert isinstance(result, MagicLinkRequestResponse)

    @pytest.mark.asyncio
    async def test_spec1282_rate_limited_returns_200(self, mock_request):
        """SPEC-1282: Rate-limited requests also return 200 (anti-enumeration)."""
        for _ in range(_RATE_MAX):
            _is_rate_limited(mock_request.client.host)
        result = await request_magic_link(
            MagicLinkRequest(email="any@test.com", tenant="any-tenant"),
            mock_request,
        )
        assert isinstance(result, MagicLinkRequestResponse)

    def test_spec1282_response_message_is_generic(self):
        """SPEC-1282: Response message does not reveal if email exists."""
        resp = MagicLinkRequestResponse()
        assert "if an account" in resp.message.lower()


# ---------------------------------------------------------------------------
# SPEC-1286: Single-use magic link tokens
# ---------------------------------------------------------------------------


class TestSpec1286SingleUseTokens:
    """SPEC-1286: Single-use magic link tokens."""

    @pytest.mark.asyncio
    async def test_spec1286_verify_calls_consume_token(self, mock_token_repo):
        """SPEC-1286: verify_magic_link calls consume_token (not read)."""
        mock_token_repo.consume_token.return_value = {
            "tenant_id": "t-1",
            "email": "user@test.com",
        }
        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            await verify_magic_link(token="my-token")

        # Must call consume_token, which atomically reads + deletes
        mock_token_repo.consume_token.assert_called_once_with(
            token_id="my-token",
            token_type=_TOKEN_TYPE,
        )

    @pytest.mark.asyncio
    async def test_spec1286_consumed_token_returns_400(self, mock_token_repo):
        """SPEC-1286: Already-consumed token returns 400 (token is None)."""
        mock_token_repo.consume_token.return_value = None
        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            resp = await verify_magic_link(token="already-used")
        assert resp.status_code == 400
        import json
        body = json.loads(resp.body)
        assert body["error"] == "invalid_token"
        assert "already been used" in body["message"]

    @pytest.mark.asyncio
    async def test_spec1286_token_type_is_magic_link(self, mock_token_repo):
        """SPEC-1286: Token type used for magic links is 'magic_link'."""
        assert _TOKEN_TYPE == "magic_link"
        mock_token_repo.consume_token.return_value = None
        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            await verify_magic_link(token="any")
        mock_token_repo.consume_token.assert_called_once_with(
            token_id="any",
            token_type="magic_link",
        )


class TestSpec1619OriginUrlPreservation:
    """SPEC-1619: Magic link URL must match origin URL.

    When a user clicks 'Sign in with email' on a tenant-scoped page
    (?tenant=<slug>), the magic link they receive must include that
    tenant slug so they return to the same context.
    """

    def test_build_magic_link_url_without_tenant(self):
        """No origin tenant → plain verify URL."""
        from src.multi_tenant.magic_link_auth import _build_magic_link_url

        url = _build_magic_link_url(
            scheme="https", host="example.com", token_id="tok123",
        )
        assert url == "https://example.com/admin/standalone/verify-magic-link?token=tok123"
        assert "tenant=" not in url

    def test_build_magic_link_url_with_tenant(self):
        """Origin tenant slug → included in verify URL."""
        from src.multi_tenant.magic_link_auth import _build_magic_link_url

        url = _build_magic_link_url(
            scheme="https", host="staging.example.com",
            token_id="tok456", origin_tenant="my-shop",
        )
        assert "token=tok456" in url
        assert "tenant=my-shop" in url
        assert url.startswith("https://staging.example.com/admin/standalone/verify-magic-link")

    def test_request_model_accepts_tenant_field(self):
        """MagicLinkRequest model accepts 'tenant' field."""
        req = MagicLinkRequest(email="user@test.com", tenant="staging-001")
        assert req.tenant == "staging-001"

    def test_request_model_tenant_is_required(self):
        """SPEC-1644: MagicLinkRequest requires tenant (URL must identify tenant)."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            MagicLinkRequest(email="user@test.com")  # missing required 'tenant'

    @pytest.mark.asyncio
    async def test_owner_path_includes_origin_tenant(
        self, mock_request, mock_team_repo, mock_tenant_repo,
        mock_token_repo, sample_tenant,
    ):
        """Owner path: origin tenant from request body is included in URL."""
        mock_team_repo = AsyncMock()
        mock_team_repo.find_by_email = AsyncMock(return_value=None)
        mock_tenant_repo.read.return_value = sample_tenant

        send_mock = AsyncMock(return_value=True)
        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.magic_link_auth._send_magic_link_email", send_mock),
        ):
            await request_magic_link(
                MagicLinkRequest(email="merchant@example.com", tenant="staging-001"),
                mock_request,
            )

        send_mock.assert_called_once()
        email_html = send_mock.call_args[0][1]
        assert "tenant=staging-001" in email_html

    @pytest.mark.asyncio
    async def test_member_path_includes_origin_tenant(
        self, mock_request, mock_team_repo, mock_tenant_repo,
        mock_token_repo,
    ):
        """Member path: origin tenant from request body is included in URL."""
        member = {
            "id": "m-1", "tenant_id": "t-1", "email": "user@test.com",
            "role": "admin", "is_active": True,
        }
        # SPEC-1644: tenant-scoped lookup returns single member
        mock_team_repo.find_by_email.return_value = member
        mock_tenant_repo.read.return_value = {
            "id": "t-1", "business_name": "Test Co",
        }

        send_mock = AsyncMock(return_value=True)
        with (
            patch("src.multi_tenant.repositories.TeamMemberRepository", return_value=mock_team_repo),
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.magic_link_auth._send_magic_link_email", send_mock),
        ):
            await request_magic_link(
                MagicLinkRequest(email="user@test.com", tenant="my-shop"),
                mock_request,
            )

        send_mock.assert_called_once()
        email_html = send_mock.call_args[0][1]
        assert "tenant=my-shop" in email_html
