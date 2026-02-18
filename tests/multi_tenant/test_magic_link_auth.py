"""Tests for magic link authentication (ML-01 to ML-22).

Covers the full magic link lifecycle:
    - Request endpoint (POST /api/auth/magic-link/request)
    - Verify endpoint (GET /api/auth/magic-link/verify)
    - Rate limiting per IP (3 requests / 5 min)
    - Email enumeration prevention
    - Single-use token consumption
    - JWT session token creation and verification
    - Middleware X-Session-Token integration

Test plan reference: §5.10 (Magic Link Auth)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest

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
    _rate_limit,
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
    """Clear the in-memory rate limit dict before each test."""
    _rate_limit.clear()
    yield
    _rate_limit.clear()


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
        _rate_limit["10.0.0.6"] = [time.time() - _RATE_WINDOW - 10] * _RATE_MAX
        assert _is_rate_limited("10.0.0.6") is False


# ---------------------------------------------------------------------------
# Request endpoint tests (ML-14 to ML-17)
# ---------------------------------------------------------------------------


class TestRequestEndpoint:
    """ML-14 to ML-17: POST /api/auth/magic-link/request."""

    @pytest.mark.asyncio
    async def test_ml14_unknown_email_returns_200(self, mock_request, mock_tenant_repo, mock_token_repo):
        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
        ):
            result = await request_magic_link(MagicLinkRequest(email="unknown@test.com"), mock_request)
        assert isinstance(result, MagicLinkRequestResponse)
        mock_token_repo.create_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_ml15_known_email_creates_token_and_sends(
        self, mock_request, mock_tenant_repo, mock_token_repo, sample_tenant,
    ):
        mock_tenant_repo.find_by_customer_email.return_value = sample_tenant
        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.magic_link_auth._send_magic_link_email", new_callable=AsyncMock, return_value=True),
        ):
            result = await request_magic_link(
                MagicLinkRequest(email="merchant@example.com"), mock_request,
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
        result = await request_magic_link(MagicLinkRequest(email="any@test.com"), mock_request)
        assert isinstance(result, MagicLinkRequestResponse)

    @pytest.mark.asyncio
    async def test_ml17_email_case_normalized(self, mock_request, mock_tenant_repo, mock_token_repo):
        mock_tenant_repo.find_by_customer_email.return_value = None
        with (
            patch("src.multi_tenant.repositories.TenantRepository", return_value=mock_tenant_repo),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
        ):
            await request_magic_link(MagicLinkRequest(email="  Test@Example.Com  "), mock_request)
        mock_tenant_repo.find_by_customer_email.assert_called_once_with("test@example.com")


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
