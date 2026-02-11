"""Tests for API key public reset endpoint and email delivery (AKR-01 to AKR-25).

Covers the full merchant API key reset lifecycle:
    - Public reset endpoint (POST /api/admin/api-keys/reset)
    - Rate limiting per IP (3 requests / 5 min)
    - Email enumeration prevention (identical response for found/not-found)
    - Email dispatch via SMTP (branded HTML + plain-text fallback)
    - Key rotation on reset (old key invalidated, new key generated)
    - Auth exemption for public endpoint
    - Widget.js auth exemption

Test plan reference: §5.9 (COMPREHENSIVE-TEST-PLAN.md)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_apikey_api import (
    ApiKeyResetRequest,
    ApiKeyResetResponse,
    RESET_RATE_MAX,
    RESET_RATE_WINDOW,
    _is_rate_limited,
    _reset_rate_limit,
    _send_api_key_email,
    configure_apikey_services,
    generate_api_key,
    reset_api_key_via_email,
)
from src.multi_tenant.auth import hash_api_key


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_rate_limit():
    """Clear the in-memory rate limit dict before each test."""
    _reset_rate_limit.clear()
    yield
    _reset_rate_limit.clear()


@pytest.fixture()
def mock_tenant_repo():
    """Mock TenantRepository with find_by_customer_email."""
    repo = AsyncMock()
    repo.find_by_customer_email = AsyncMock(return_value=None)
    repo.read = AsyncMock(return_value=None)
    repo.patch = AsyncMock()
    return repo


@pytest.fixture()
def mock_audit_repo():
    return AsyncMock()


@pytest.fixture()
def _wire_repos(mock_tenant_repo, mock_audit_repo):
    """Inject mock repos into the API key service."""
    configure_apikey_services(mock_tenant_repo, mock_audit_repo)
    yield
    configure_apikey_services(None, None)


@pytest.fixture()
def mock_request():
    """Fake Starlette Request with configurable client IP."""
    req = MagicMock()
    req.client = MagicMock()
    req.client.host = "10.0.0.1"
    return req


def _make_tenant(
    tenant_id: str = "tenant-abc123",
    email: str = "merchant@example.com",
    company: str = "Test Corp",
    existing_key_hash: str | None = None,
) -> dict:
    doc = {
        "id": tenant_id,
        "tenant_id": tenant_id,
        "customer_email": email,
        "company_name": company,
    }
    if existing_key_hash:
        doc["api_key_hash"] = existing_key_hash
        doc["api_key_prefix"] = "ar_live_tena"
    return doc


# ---------------------------------------------------------------------------
# AKR-01: Valid email → 200 + generic message
# ---------------------------------------------------------------------------


class TestResetEndpointResponses:
    """AKR-01 through AKR-03: Response identity regardless of email match."""

    @pytest.mark.asyncio
    async def test_akr01_valid_email_returns_200(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """AKR-01: Known email returns 200 with generic message."""
        tenant = _make_tenant()
        mock_tenant_repo.find_by_customer_email.return_value = tenant

        body = ApiKeyResetRequest(email="merchant@example.com")
        resp = await reset_api_key_via_email(body, mock_request)

        assert isinstance(resp, ApiKeyResetResponse)
        assert "If an account" in resp.message

    @pytest.mark.asyncio
    async def test_akr02_unknown_email_same_response(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """AKR-02: Unknown email returns identical 200 response."""
        mock_tenant_repo.find_by_customer_email.return_value = None

        body = ApiKeyResetRequest(email="nobody@example.com")
        resp = await reset_api_key_via_email(body, mock_request)

        assert isinstance(resp, ApiKeyResetResponse)
        assert "If an account" in resp.message

    @pytest.mark.asyncio
    async def test_akr03_invalid_email_format_same_response(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """AKR-03: Malformed email returns same generic 200 (no enumeration)."""
        body = ApiKeyResetRequest(email="not-an-email")
        resp = await reset_api_key_via_email(body, mock_request)

        assert isinstance(resp, ApiKeyResetResponse)
        assert "If an account" in resp.message
        # Should NOT have attempted a DB lookup
        mock_tenant_repo.find_by_customer_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_sec20b_response_identical(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """SEC-20b: Found vs not-found email → byte-identical response."""
        # First: known email
        mock_tenant_repo.find_by_customer_email.return_value = _make_tenant()
        body1 = ApiKeyResetRequest(email="known@example.com")
        with patch(
            "src.multi_tenant.admin_apikey_api._send_api_key_email",
            new_callable=AsyncMock,
            return_value=True,
        ):
            resp1 = await reset_api_key_via_email(body1, mock_request)

        # Clear rate limit between
        _reset_rate_limit.clear()

        # Second: unknown email
        mock_tenant_repo.find_by_customer_email.return_value = None
        body2 = ApiKeyResetRequest(email="unknown@example.com")
        resp2 = await reset_api_key_via_email(body2, mock_request)

        assert resp1.message == resp2.message


# ---------------------------------------------------------------------------
# AKR-04 through AKR-06: Rate limiting
# ---------------------------------------------------------------------------


class TestResetRateLimiting:
    """AKR-04 through AKR-06: IP-based rate limiting on reset endpoint."""

    def test_akr04_rate_limited_after_max_requests(self):
        """AKR-04: 4th request from same IP within window → rate limited."""
        ip = "192.168.1.1"
        for _ in range(RESET_RATE_MAX):
            assert _is_rate_limited(ip) is False
        assert _is_rate_limited(ip) is True

    def test_akr05_window_resets_after_expiry(self):
        """AKR-05: Rate limit clears after RESET_RATE_WINDOW seconds."""
        ip = "192.168.1.2"
        # Exhaust the limit
        for _ in range(RESET_RATE_MAX):
            _is_rate_limited(ip)

        # Manually age the timestamps past the window
        _reset_rate_limit[ip] = [
            time.time() - RESET_RATE_WINDOW - 1.0
            for _ in _reset_rate_limit[ip]
        ]
        assert _is_rate_limited(ip) is False

    def test_akr06_different_ips_independent(self):
        """AKR-06: Each IP has its own rate limit budget."""
        for _ in range(RESET_RATE_MAX):
            _is_rate_limited("10.0.0.1")

        assert _is_rate_limited("10.0.0.1") is True
        assert _is_rate_limited("10.0.0.2") is False

    def test_sec25a_fourth_request_returns_429(self):
        """SEC-25a: 4th reset request → rate limited."""
        assert _is_rate_limited("1.1.1.1") is False
        assert _is_rate_limited("1.1.1.1") is False
        assert _is_rate_limited("1.1.1.1") is False
        assert _is_rate_limited("1.1.1.1") is True

    def test_sec25b_different_ips_are_independent(self):
        """SEC-25b: Different IPs each get full budget."""
        for i in range(5):
            ip = f"10.0.0.{i}"
            for _ in range(RESET_RATE_MAX):
                assert _is_rate_limited(ip) is False
            assert _is_rate_limited(ip) is True


# ---------------------------------------------------------------------------
# AKR-07 through AKR-09: Key replacement on reset
# ---------------------------------------------------------------------------


class TestResetKeyReplacement:
    """AKR-07 through AKR-09: Reset generates new key, invalidates old."""

    @pytest.mark.asyncio
    async def test_akr07_reset_updates_key_hash(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """AKR-07: Reset calls patch with new api_key_hash."""
        old_key = generate_api_key("tenant-abc123")
        old_hash = hash_api_key(old_key)
        tenant = _make_tenant(existing_key_hash=old_hash)
        mock_tenant_repo.find_by_customer_email.return_value = tenant

        body = ApiKeyResetRequest(email="merchant@example.com")
        with patch(
            "src.multi_tenant.admin_apikey_api._send_api_key_email",
            new_callable=AsyncMock,
            return_value=True,
        ):
            await reset_api_key_via_email(body, mock_request)

        # Verify patch was called with new hash
        mock_tenant_repo.patch.assert_called_once()
        call_kwargs = mock_tenant_repo.patch.call_args
        operations = call_kwargs.kwargs.get("operations") or call_kwargs[1].get("operations") or call_kwargs[0][2]
        hash_op = next(op for op in operations if op["path"] == "/api_key_hash")
        assert hash_op["value"] != old_hash
        assert hash_op["value"] is not None

    @pytest.mark.asyncio
    async def test_akr08_old_key_invalidated(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """AKR-08: After reset, old key hash no longer matches."""
        old_key = generate_api_key("tenant-abc123")
        old_hash = hash_api_key(old_key)
        tenant = _make_tenant(existing_key_hash=old_hash)
        mock_tenant_repo.find_by_customer_email.return_value = tenant

        body = ApiKeyResetRequest(email="merchant@example.com")
        with patch(
            "src.multi_tenant.admin_apikey_api._send_api_key_email",
            new_callable=AsyncMock,
            return_value=True,
        ):
            await reset_api_key_via_email(body, mock_request)

        # The new hash must differ from the old hash
        operations = mock_tenant_repo.patch.call_args.kwargs.get("operations") or mock_tenant_repo.patch.call_args[0][2]
        new_hash = next(op for op in operations if op["path"] == "/api_key_hash")["value"]
        assert new_hash != old_hash

    @pytest.mark.asyncio
    async def test_akr09_sets_last_rotated_timestamp(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """AKR-09: Reset sets api_key_last_rotated_at."""
        tenant = _make_tenant()
        mock_tenant_repo.find_by_customer_email.return_value = tenant

        body = ApiKeyResetRequest(email="merchant@example.com")
        with patch(
            "src.multi_tenant.admin_apikey_api._send_api_key_email",
            new_callable=AsyncMock,
            return_value=True,
        ):
            await reset_api_key_via_email(body, mock_request)

        operations = mock_tenant_repo.patch.call_args.kwargs.get("operations") or mock_tenant_repo.patch.call_args[0][2]
        rotated_op = next(
            op for op in operations if op["path"] == "/api_key_last_rotated_at"
        )
        assert rotated_op["value"] is not None
        assert "T" in rotated_op["value"]  # ISO 8601


# ---------------------------------------------------------------------------
# AKR-10 through AKR-11: Email dispatch and audit
# ---------------------------------------------------------------------------


class TestResetEmailAndAudit:
    """AKR-10 through AKR-11: Email call args, audit logging."""

    @pytest.mark.asyncio
    async def test_akr10_email_called_with_correct_args(
        self, mock_tenant_repo, mock_audit_repo, mock_request, _wire_repos,
    ):
        """AKR-10: _send_api_key_email receives (email, raw_key, tenant_name)."""
        tenant = _make_tenant(company="Acme Inc")
        mock_tenant_repo.find_by_customer_email.return_value = tenant

        with patch(
            "src.multi_tenant.admin_apikey_api._send_api_key_email",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_send:
            body = ApiKeyResetRequest(email="merchant@example.com")
            await reset_api_key_via_email(body, mock_request)

            mock_send.assert_called_once()
            args = mock_send.call_args[0]
            assert args[0] == "merchant@example.com"  # to_email
            assert args[1].startswith("ar_live_")  # raw_key
            assert args[2] == "Acme Inc"  # tenant_name

    @pytest.mark.asyncio
    async def test_akr11_audit_logged_on_reset(
        self, mock_tenant_repo, mock_audit_repo, mock_request, _wire_repos,
    ):
        """AKR-11: SECURITY_EVENT audit entry with key_prefix + email_sent."""
        tenant = _make_tenant()
        mock_tenant_repo.find_by_customer_email.return_value = tenant

        with patch(
            "src.multi_tenant.admin_apikey_api._send_api_key_email",
            new_callable=AsyncMock,
            return_value=True,
        ):
            body = ApiKeyResetRequest(email="merchant@example.com")
            await reset_api_key_via_email(body, mock_request)

        mock_audit_repo.log_event.assert_called_once()
        audit_call = mock_audit_repo.log_event.call_args
        from src.multi_tenant.cosmos_schema import AuditEventType
        assert audit_call.kwargs["event_type"] == AuditEventType.SECURITY_EVENT
        audit_payload = audit_call.kwargs["payload"]
        assert "api_key_reset_via_email" in str(audit_payload)
        assert "key_prefix" in audit_payload
        assert "email_sent" in audit_payload


# ---------------------------------------------------------------------------
# AKR-12: Auth exemption
# ---------------------------------------------------------------------------


class TestAuthExemption:
    """AKR-12, AKR-25: Public endpoints are auth-exempt."""

    def test_akr12_reset_path_is_auth_exempt(self):
        """AKR-12: /api/admin/api-keys/reset is in AUTH_EXEMPT_PREFIXES."""
        from src.multi_tenant.auth import AUTH_EXEMPT_PREFIXES

        # The path must start with one of the exempt prefixes
        path = "/api/admin/api-keys/reset"
        assert any(path.startswith(p) for p in AUTH_EXEMPT_PREFIXES)

    def test_akr25_widget_js_is_auth_exempt(self):
        """AKR-25: /widget.js is in AUTH_EXEMPT_PREFIXES."""
        from src.multi_tenant.auth import AUTH_EXEMPT_PREFIXES

        path = "/widget.js"
        assert any(path.startswith(p) for p in AUTH_EXEMPT_PREFIXES)


# ---------------------------------------------------------------------------
# AKR-13 through AKR-17: Email sending
# ---------------------------------------------------------------------------


class TestEmailSending:
    """AKR-13 through AKR-17: SMTP email delivery and content."""

    @pytest.mark.asyncio
    async def test_akr14_missing_smtp_host_returns_false(self):
        """AKR-14: No SMTP_HOST → returns False gracefully."""
        with patch.dict("os.environ", {}, clear=False):
            # Ensure SMTP_HOST is not set
            import os
            orig = os.environ.pop("SMTP_HOST", None)
            try:
                result = await _send_api_key_email(
                    "test@example.com", "ar_live_test_key123", "Test Corp",
                )
                assert result is False
            finally:
                if orig is not None:
                    os.environ["SMTP_HOST"] = orig

    @pytest.mark.asyncio
    async def test_akr15_smtp_failure_returns_false(self):
        """AKR-15: SMTP connection error → returns False, doesn't raise."""
        with patch.dict(
            "os.environ",
            {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "587"},
        ):
            with patch("smtplib.SMTP", side_effect=ConnectionRefusedError):
                result = await _send_api_key_email(
                    "test@example.com", "ar_live_test_key123", "Test Corp",
                )
                assert result is False

    @pytest.mark.asyncio
    async def test_akr13_smtp_success_returns_true(self):
        """AKR-13: Successful SMTP send → returns True."""
        with patch.dict(
            "os.environ",
            {
                "SMTP_HOST": "mail.example.com",
                "SMTP_PORT": "587",
                "SMTP_USERNAME": "user",
                "SMTP_PASSWORD": "pass",
            },
        ):
            mock_smtp = MagicMock()
            mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
            mock_smtp.__exit__ = MagicMock(return_value=False)
            with patch("smtplib.SMTP", return_value=mock_smtp):
                result = await _send_api_key_email(
                    "test@example.com", "ar_live_test_key123", "Test Corp",
                )
                assert result is True
                mock_smtp.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_akr16_email_html_contains_key(self):
        """AKR-16: HTML email body contains the raw API key and branding."""
        with patch.dict(
            "os.environ",
            {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "587"},
        ):
            mock_smtp = MagicMock()
            mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
            mock_smtp.__exit__ = MagicMock(return_value=False)

            with patch("smtplib.SMTP", return_value=mock_smtp):
                await _send_api_key_email(
                    "test@example.com", "ar_live_test_MYKEY123", "Test Corp",
                )

            msg = mock_smtp.send_message.call_args[0][0]
            # Get the HTML part
            html_part = None
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_part = part.get_payload(decode=True).decode()
                    break
            assert html_part is not None
            assert "ar_live_test_MYKEY123" in html_part
            assert "Agent Red" in html_part

    @pytest.mark.asyncio
    async def test_akr17_email_plaintext_contains_key(self):
        """AKR-17: Plain-text email body contains the raw API key."""
        with patch.dict(
            "os.environ",
            {"SMTP_HOST": "mail.example.com", "SMTP_PORT": "587"},
        ):
            mock_smtp = MagicMock()
            mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
            mock_smtp.__exit__ = MagicMock(return_value=False)

            with patch("smtplib.SMTP", return_value=mock_smtp):
                await _send_api_key_email(
                    "test@example.com", "ar_live_test_MYKEY123", None,
                )

            msg = mock_smtp.send_message.call_args[0][0]
            plain_part = None
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    plain_part = part.get_payload(decode=True).decode()
                    break
            assert plain_part is not None
            assert "ar_live_test_MYKEY123" in plain_part


# ---------------------------------------------------------------------------
# AKR-18 through AKR-19: End-to-end key lifecycle
# ---------------------------------------------------------------------------


class TestResetE2EKeyLifecycle:
    """AKR-18 through AKR-19: Reset + authentication validation."""

    @pytest.mark.asyncio
    async def test_akr18_new_key_authenticates(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """AKR-18: After reset, new key's hash matches generated hash."""
        tenant = _make_tenant()
        mock_tenant_repo.find_by_customer_email.return_value = tenant

        captured_key: str | None = None

        async def _capture_email(to: str, key: str, name: str | None = None, admin_login_url: str | None = None) -> bool:
            nonlocal captured_key
            captured_key = key
            return True

        with patch(
            "src.multi_tenant.admin_apikey_api._send_api_key_email",
            side_effect=_capture_email,
        ):
            body = ApiKeyResetRequest(email="merchant@example.com")
            await reset_api_key_via_email(body, mock_request)

        assert captured_key is not None
        new_hash = hash_api_key(captured_key)

        # Verify the hash stored in Cosmos DB matches
        operations = mock_tenant_repo.patch.call_args.kwargs.get("operations") or mock_tenant_repo.patch.call_args[0][2]
        stored_hash = next(op for op in operations if op["path"] == "/api_key_hash")["value"]
        assert stored_hash == new_hash

    @pytest.mark.asyncio
    async def test_akr19_old_key_rejected_after_reset(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """AKR-19: After reset, old key hash does not match new stored hash."""
        old_key = generate_api_key("tenant-abc123")
        old_hash = hash_api_key(old_key)
        tenant = _make_tenant(existing_key_hash=old_hash)
        mock_tenant_repo.find_by_customer_email.return_value = tenant

        with patch(
            "src.multi_tenant.admin_apikey_api._send_api_key_email",
            new_callable=AsyncMock,
            return_value=True,
        ):
            body = ApiKeyResetRequest(email="merchant@example.com")
            await reset_api_key_via_email(body, mock_request)

        operations = mock_tenant_repo.patch.call_args.kwargs.get("operations") or mock_tenant_repo.patch.call_args[0][2]
        new_stored_hash = next(op for op in operations if op["path"] == "/api_key_hash")["value"]
        assert old_hash != new_stored_hash  # Old key no longer valid


# ---------------------------------------------------------------------------
# AKR-20 through AKR-24: Edge cases
# ---------------------------------------------------------------------------


class TestResetEdgeCases:
    """AKR-20 through AKR-24: Input sanitization, concurrency, errors."""

    @pytest.mark.asyncio
    async def test_akr20_email_case_insensitive(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """AKR-20: Email is lowercased before lookup."""
        mock_tenant_repo.find_by_customer_email.return_value = None
        body = ApiKeyResetRequest(email="Merchant@EXAMPLE.com")
        await reset_api_key_via_email(body, mock_request)

        mock_tenant_repo.find_by_customer_email.assert_called_once_with(
            "merchant@example.com",
        )

    @pytest.mark.asyncio
    async def test_akr21_email_whitespace_trimmed(
        self, mock_tenant_repo, mock_request, _wire_repos,
    ):
        """AKR-21: Leading/trailing whitespace stripped from email."""
        mock_tenant_repo.find_by_customer_email.return_value = None
        body = ApiKeyResetRequest(email="  merchant@example.com  ")
        await reset_api_key_via_email(body, mock_request)

        mock_tenant_repo.find_by_customer_email.assert_called_once_with(
            "merchant@example.com",
        )

    @pytest.mark.asyncio
    async def test_akr22_service_not_initialized_503(self):
        """AKR-22: Reset returns 503 when _tenant_repo is None."""
        configure_apikey_services(None, None)
        body = ApiKeyResetRequest(email="test@example.com")
        req = MagicMock()
        req.client = MagicMock()
        req.client.host = "10.0.0.1"

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await reset_api_key_via_email(body, req)
        assert exc_info.value.status_code == 503

    def test_akr23_missing_email_field_schema_validation(self):
        """AKR-23: Missing email field → Pydantic ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ApiKeyResetRequest()  # type: ignore[call-arg]

    def test_sec20a_xss_in_email_sanitized(self):
        """SEC-20a: XSS payload in email field → invalid email format."""
        from src.multi_tenant.admin_apikey_api import _EMAIL_RE

        xss_payloads = [
            '<script>alert("xss")</script>@example.com',
            "test@example.com<script>",
            'test" onmouseover="alert(1)"@example.com',
        ]
        for payload in xss_payloads:
            assert not _EMAIL_RE.match(payload), f"XSS payload matched: {payload}"


# ---------------------------------------------------------------------------
# Constants and models
# ---------------------------------------------------------------------------


class TestResetConstants:
    """Verify rate limit constants are reasonable."""

    def test_rate_max_is_3(self):
        assert RESET_RATE_MAX == 3

    def test_rate_window_is_300_seconds(self):
        assert RESET_RATE_WINDOW == 300.0

    def test_reset_response_model(self):
        resp = ApiKeyResetResponse()
        assert "If an account" in resp.message

    def test_reset_request_model(self):
        req = ApiKeyResetRequest(email="test@example.com")
        assert req.email == "test@example.com"
