"""Tests for Email Change Request & Confirmation (SPEC-1682, SPEC-1683).

Covers:
    - Request endpoint authentication and validation
    - Rate limiting
    - Confirmation endpoint token consumption
    - Security notifications to old email
    - Auth exemption for confirm endpoint
    - Router registration
    - Communication capture integration

Run:
    pytest tests/multi_tenant/test_email_change.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Module structure tests
# ---------------------------------------------------------------------------


class TestModuleStructure:

    def test_router_exists(self):
        from src.multi_tenant.email_change import router
        assert router is not None

    def test_router_prefix(self):
        from src.multi_tenant.email_change import router
        route_paths = [r.path for r in router.routes]
        assert any("/api/admin/email" in p for p in route_paths)

    def test_router_has_request_and_confirm(self):
        from src.multi_tenant.email_change import router
        methods = set()
        for route in router.routes:
            if hasattr(route, "methods"):
                methods.update(route.methods)
        assert "POST" in methods  # /request
        assert "GET" in methods  # /confirm

    def test_router_registered_in_routers(self):
        from src.app.routers import email_change_router
        assert email_change_router is not None

    def test_confirm_path_is_auth_exempt(self):
        from src.multi_tenant.auth import AUTH_EXEMPT_PREFIXES
        assert any("/api/admin/email/confirm" in p for p in AUTH_EXEMPT_PREFIXES)

    def test_confirm_is_auth_exempt_via_function(self):
        from src.multi_tenant.auth import is_auth_exempt
        assert is_auth_exempt("/api/admin/email/confirm")
        assert is_auth_exempt("/api/admin/email/confirm?token=abc123")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TestModels:

    def test_email_change_request_model(self):
        from src.multi_tenant.email_change import EmailChangeRequest
        req = EmailChangeRequest(new_email="new@example.com")
        assert req.new_email == "new@example.com"

    def test_email_change_response_model(self):
        from src.multi_tenant.email_change import EmailChangeResponse
        resp = EmailChangeResponse(ok=True, message="Success")
        assert resp.ok is True
        assert resp.message == "Success"


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


class TestRateLimiting:

    def setup_method(self):
        from src.multi_tenant import email_change
        email_change._rate_limit.clear()

    def test_first_request_not_rate_limited(self):
        from src.multi_tenant.email_change import _is_rate_limited
        assert _is_rate_limited("192.168.1.1") is False

    def test_fourth_request_is_rate_limited(self):
        from src.multi_tenant.email_change import _is_rate_limited
        _is_rate_limited("10.0.0.1")
        _is_rate_limited("10.0.0.1")
        _is_rate_limited("10.0.0.1")
        assert _is_rate_limited("10.0.0.1") is True

    def test_different_ips_independent(self):
        from src.multi_tenant.email_change import _is_rate_limited
        for _ in range(3):
            _is_rate_limited("10.0.0.1")
        assert _is_rate_limited("10.0.0.1") is True
        assert _is_rate_limited("10.0.0.2") is False


# ---------------------------------------------------------------------------
# Request endpoint
# ---------------------------------------------------------------------------


class TestRequestEndpoint:

    def setup_method(self):
        from src.multi_tenant import email_change
        email_change._rate_limit.clear()

    @pytest.mark.asyncio
    async def test_non_platform_admin_rejected(self):
        from src.multi_tenant.email_change import (
            EmailChangeRequest,
            request_email_change,
        )
        from src.multi_tenant.auth import TenantContext

        ctx = TenantContext(tenant_id="t1", is_platform_admin=False)
        body = EmailChangeRequest(new_email="new@example.com")
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"

        result = await request_email_change(body, mock_request, ctx)
        assert result.ok is False
        assert "platform administrator" in result.message.lower()

    @pytest.mark.asyncio
    async def test_same_email_rejected(self):
        from src.multi_tenant.email_change import (
            EmailChangeRequest,
            request_email_change,
        )
        from src.multi_tenant.auth import TenantContext

        ctx = TenantContext(
            tenant_id="__platform__",
            is_platform_admin=True,
            platform_admin_email="admin@test.com",
        )
        body = EmailChangeRequest(new_email="admin@test.com")
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"

        result = await request_email_change(body, mock_request, ctx)
        assert result.ok is False
        assert "same" in result.message.lower()

    @pytest.mark.asyncio
    async def test_invalid_email_rejected(self):
        from src.multi_tenant.email_change import (
            EmailChangeRequest,
            request_email_change,
        )
        from src.multi_tenant.auth import TenantContext

        ctx = TenantContext(
            tenant_id="__platform__",
            is_platform_admin=True,
            platform_admin_email="admin@test.com",
        )
        body = EmailChangeRequest(new_email="not-an-email")
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"

        result = await request_email_change(body, mock_request, ctx)
        assert result.ok is False
        assert "invalid" in result.message.lower()

    @pytest.mark.asyncio
    async def test_rate_limit_returns_error(self):
        from src.multi_tenant.email_change import (
            EmailChangeRequest,
            request_email_change,
            _is_rate_limited,
        )
        from src.multi_tenant.auth import TenantContext

        # Exhaust rate limit
        for _ in range(3):
            _is_rate_limited("192.168.50.1")

        ctx = TenantContext(
            tenant_id="__platform__",
            is_platform_admin=True,
            platform_admin_email="admin@test.com",
        )
        body = EmailChangeRequest(new_email="new@test.com")
        mock_request = MagicMock()
        mock_request.client.host = "192.168.50.1"

        result = await request_email_change(body, mock_request, ctx)
        assert result.ok is False
        assert "too many" in result.message.lower()

    @pytest.mark.asyncio
    @patch("src.multi_tenant.email_change._send_email", new_callable=AsyncMock)
    async def test_successful_request_sends_emails(self, mock_send):
        from src.multi_tenant.email_change import (
            EmailChangeRequest,
            request_email_change,
        )
        from src.multi_tenant.auth import TenantContext

        mock_send.return_value = True

        # Mock the token repository
        mock_token_repo = MagicMock()
        mock_token_repo.create_token = AsyncMock()
        mock_token_repo._container = MagicMock()
        mock_token_repo._container.patch_item = AsyncMock()

        ctx = TenantContext(
            tenant_id="__platform__",
            is_platform_admin=True,
            platform_admin_email="old@test.com",
            platform_admin_id="admin-001",
        )
        body = EmailChangeRequest(new_email="new@test.com")
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}
        mock_request.url.scheme = "https"
        mock_request.url.hostname = "localhost"

        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            result = await request_email_change(body, mock_request, ctx)

        assert result.ok is True
        assert "confirmation" in result.message.lower()
        # Should send 2 emails: confirmation to new + alert to old
        assert mock_send.call_count == 2


# ---------------------------------------------------------------------------
# Confirm endpoint
# ---------------------------------------------------------------------------


class TestConfirmEndpoint:

    @pytest.mark.asyncio
    async def test_invalid_token_returns_400(self):
        from src.multi_tenant.email_change import confirm_email_change

        mock_token_repo = MagicMock()
        mock_token_repo.consume_token = AsyncMock(return_value=None)

        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo):
            result = await confirm_email_change(token="invalid-token")

        assert result.status_code == 400
        assert "invalid" in result.body.decode().lower()

    @pytest.mark.asyncio
    @patch("src.multi_tenant.email_change._send_email", new_callable=AsyncMock)
    async def test_valid_token_updates_email(self, mock_send):
        from src.multi_tenant.email_change import confirm_email_change

        mock_send.return_value = True

        mock_token_repo = MagicMock()
        mock_token_repo.consume_token = AsyncMock(return_value={
            "email": "new@test.com",
            "old_email": "old@test.com",
            "admin_id": "admin-001",
            "tenant_id": "__platform__",
        })

        mock_admin_repo = MagicMock()
        mock_admin_repo._container = MagicMock()
        mock_admin_repo._container.patch_item = AsyncMock()

        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),              patch("src.multi_tenant.repositories.PlatformAdminRepository", return_value=mock_admin_repo):
            result = await confirm_email_change(token="valid-token")

        assert result.status_code == 200
        assert "new@test.com" in result.body.decode()
        # Should have patched the admin document
        mock_admin_repo._container.patch_item.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.multi_tenant.email_change._send_email", new_callable=AsyncMock)
    async def test_confirmation_sends_completion_notification(self, mock_send):
        from src.multi_tenant.email_change import confirm_email_change

        mock_send.return_value = True

        mock_token_repo = MagicMock()
        mock_token_repo.consume_token = AsyncMock(return_value={
            "email": "new@test.com",
            "old_email": "old@test.com",
            "admin_id": "admin-001",
            "tenant_id": "__platform__",
        })

        mock_admin_repo = MagicMock()
        mock_admin_repo._container = MagicMock()
        mock_admin_repo._container.patch_item = AsyncMock()

        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),              patch("src.multi_tenant.repositories.PlatformAdminRepository", return_value=mock_admin_repo):
            await confirm_email_change(token="valid-token")

        # Completion notification sent to old email
        assert mock_send.called
        call_args = mock_send.call_args_list[0]
        assert call_args[0][0] == "old@test.com"  # recipient

    @pytest.mark.asyncio
    async def test_cosmos_update_failure_returns_500(self):
        from src.multi_tenant.email_change import confirm_email_change

        mock_token_repo = MagicMock()
        mock_token_repo.consume_token = AsyncMock(return_value={
            "email": "new@test.com",
            "old_email": "old@test.com",
            "admin_id": "admin-001",
            "tenant_id": "__platform__",
        })

        mock_admin_repo = MagicMock()
        mock_admin_repo._container = MagicMock()
        mock_admin_repo._container.patch_item = AsyncMock(side_effect=Exception("Cosmos error"))

        with patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),              patch("src.multi_tenant.repositories.PlatformAdminRepository", return_value=mock_admin_repo):
            result = await confirm_email_change(token="valid-token")

        assert result.status_code == 500


# ---------------------------------------------------------------------------
# Email templates
# ---------------------------------------------------------------------------


class TestEmailTemplates:

    def test_confirm_email_body_has_placeholders(self):
        from src.multi_tenant.email_change import _CONFIRM_EMAIL_BODY
        assert "{confirm_url}" in _CONFIRM_EMAIL_BODY

    def test_security_alert_body_has_placeholders(self):
        from src.multi_tenant.email_change import _SECURITY_ALERT_BODY
        assert "{old_email}" in _SECURITY_ALERT_BODY
        assert "{new_email}" in _SECURITY_ALERT_BODY
        assert "{timestamp}" in _SECURITY_ALERT_BODY

    def test_completion_alert_body_has_placeholders(self):
        from src.multi_tenant.email_change import _COMPLETION_ALERT_BODY
        assert "{old_email}" in _COMPLETION_ALERT_BODY
        assert "{new_email}" in _COMPLETION_ALERT_BODY

    def test_confirm_success_html_has_email_placeholder(self):
        from src.multi_tenant.email_change import _CONFIRM_SUCCESS_HTML
        assert "{email}" in _CONFIRM_SUCCESS_HTML

    def test_confirm_error_html_has_reason_placeholder(self):
        from src.multi_tenant.email_change import _CONFIRM_ERROR_HTML
        assert "{reason}" in _CONFIRM_ERROR_HTML


# ---------------------------------------------------------------------------
# Token type constant
# ---------------------------------------------------------------------------


class TestTokenConfig:

    def test_token_type_is_email_change(self):
        from src.multi_tenant.email_change import _TOKEN_TYPE
        assert _TOKEN_TYPE == "email_change"

    def test_token_ttl_is_15_minutes(self):
        from src.multi_tenant.email_change import _TOKEN_TTL
        assert _TOKEN_TTL == 900
