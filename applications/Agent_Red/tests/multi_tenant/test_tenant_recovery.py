"""Tests for Tenant Account Recovery by SPA (SPEC-1677).

Covers:
    POST /api/superadmin/tenant-recovery/activate
    POST /api/superadmin/tenant-recovery/send-auth-link
    GET  /api/superadmin/tenant-recovery/status/{tenant_id}
    GET  /api/auth/account-recovery/verify
    Token consumption (single-use)
    Expired/invalid token rejection
    Audit event logging
    Auth-exempt path registration

Run:
    pytest tests/multi_tenant/test_tenant_recovery.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import AuditEventType, TenantStatus
from src.multi_tenant.tenant_recovery import (
    ActivateRecoveryRequest,
    RecoveryStatusResponse,
    SendAuthLinkRequest,
    activate_recovery_address,
    configure_tenant_recovery,
    get_recovery_status,
    send_recovery_auth_link,
    verify_recovery_token,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _spa_ctx() -> TenantContext:
    return TenantContext(
        tenant_id="__platform__",
        is_platform_admin=True,
        auth_method="spa_api_key",
        status=TenantStatus.ACTIVE,
        platform_admin_id="admin-001",
        platform_admin_email="super@remaker.digital",
        platform_admin_role="superadmin",
    )


def _mock_request(ctx: TenantContext | None = None) -> MagicMock:
    request = MagicMock()
    request.state.tenant_context = ctx or _spa_ctx()
    request.headers = {"host": "localhost:8000", "x-forwarded-proto": "https"}
    return request


@pytest.fixture()
def mock_tenant_repo():
    repo = MagicMock()
    repo.update_recovery_address = AsyncMock()
    repo.get_recovery_address = AsyncMock(return_value={
        "recovery_address": "recover@tenant.com",
        "recovery_address_enabled": True,
        "recovery_address_activated_by": "admin-001",
        "recovery_address_activated_at": "2026-03-08T00:00:00Z",
    })
    return repo


@pytest.fixture()
def mock_verification_repo():
    repo = MagicMock()
    repo.create_token = AsyncMock()
    repo.consume_token = AsyncMock(return_value={
        "id": "test-token-123",
        "token_type": "account_recovery",
        "tenant_id": "tenant-001",
        "email": "recover@tenant.com",
        "used": False,
    })
    return repo


@pytest.fixture()
def mock_audit_repo():
    repo = MagicMock()
    repo.log_event = AsyncMock()
    return repo


@pytest.fixture(autouse=True)
def _wire_repos(mock_tenant_repo, mock_verification_repo, mock_audit_repo):
    configure_tenant_recovery(
        tenant_repo=mock_tenant_repo,
        verification_repo=mock_verification_repo,
        audit_repo=mock_audit_repo,
    )
    yield
    configure_tenant_recovery(
        tenant_repo=None,
        verification_repo=None,
        audit_repo=None,
    )


# ---------------------------------------------------------------------------
# Activate recovery address
# ---------------------------------------------------------------------------


class TestActivateRecoveryAddress:

    @pytest.mark.asyncio
    async def test_activate_sets_recovery_address(self, mock_tenant_repo):
        body = ActivateRecoveryRequest(
            tenant_id="tenant-001", recovery_email="recover@tenant.com",
        )
        result = await activate_recovery_address(body=body, request=_mock_request())
        assert "activated" in result.message.lower()
        mock_tenant_repo.update_recovery_address.assert_called_once()
        call_kwargs = mock_tenant_repo.update_recovery_address.call_args.kwargs
        assert call_kwargs["tenant_id"] == "tenant-001"
        assert call_kwargs["recovery_email"] == "recover@tenant.com"
        assert call_kwargs["enabled"] is True

    @pytest.mark.asyncio
    async def test_activate_audit_logged(self, mock_audit_repo):
        body = ActivateRecoveryRequest(
            tenant_id="tenant-001", recovery_email="recover@test.com",
        )
        await activate_recovery_address(body=body, request=_mock_request())
        mock_audit_repo.log_event.assert_called_once()
        call_kwargs = mock_audit_repo.log_event.call_args.kwargs
        assert call_kwargs["event_type"] == AuditEventType.SECURITY_EVENT
        assert "recovery_address_activated" in str(call_kwargs["payload"])

    @pytest.mark.asyncio
    async def test_activate_returns_503_when_not_configured(self):
        configure_tenant_recovery(tenant_repo=None, verification_repo=None, audit_repo=None)
        body = ActivateRecoveryRequest(
            tenant_id="tenant-001", recovery_email="recover@test.com",
        )
        result = await activate_recovery_address(body=body, request=_mock_request())
        assert result.status_code == 503


# ---------------------------------------------------------------------------
# Send auth link
# ---------------------------------------------------------------------------


class TestSendAuthLink:

    @pytest.mark.asyncio
    @patch("src.multi_tenant.tenant_recovery._send_recovery_auth_email", new_callable=AsyncMock)
    async def test_send_auth_link_creates_token(
        self, mock_send_email, mock_verification_repo,
    ):
        body = SendAuthLinkRequest(tenant_id="tenant-001")
        result = await send_recovery_auth_link(body=body, request=_mock_request())
        assert "sent" in result.message.lower()
        mock_verification_repo.create_token.assert_called_once()
        call_kwargs = mock_verification_repo.create_token.call_args.kwargs
        assert call_kwargs["token_type"] == "account_recovery"
        assert call_kwargs["tenant_id"] == "tenant-001"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.tenant_recovery._send_recovery_auth_email", new_callable=AsyncMock)
    async def test_send_auth_link_sends_email(self, mock_send_email):
        body = SendAuthLinkRequest(tenant_id="tenant-001")
        await send_recovery_auth_link(body=body, request=_mock_request())
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        assert call_args[0] == "recover@tenant.com"
        assert "recovery_token=" in call_args[1]

    @pytest.mark.asyncio
    async def test_send_auth_link_fails_when_no_recovery_address(self, mock_tenant_repo):
        mock_tenant_repo.get_recovery_address.return_value = {
            "recovery_address": None,
            "recovery_address_enabled": False,
        }
        body = SendAuthLinkRequest(tenant_id="tenant-001")
        result = await send_recovery_auth_link(body=body, request=_mock_request())
        assert result.status_code == 400

    @pytest.mark.asyncio
    async def test_send_auth_link_audit_logged(self, mock_audit_repo):
        with patch(
            "src.multi_tenant.tenant_recovery._send_recovery_auth_email",
            new_callable=AsyncMock,
        ):
            body = SendAuthLinkRequest(tenant_id="tenant-001")
            await send_recovery_auth_link(body=body, request=_mock_request())
            mock_audit_repo.log_event.assert_called_once()
            assert "recovery_auth_link_sent" in str(
                mock_audit_repo.log_event.call_args.kwargs["payload"],
            )


# ---------------------------------------------------------------------------
# Recovery status
# ---------------------------------------------------------------------------


class TestRecoveryStatus:

    @pytest.mark.asyncio
    async def test_get_status_returns_recovery_info(self):
        result = await get_recovery_status(
            tenant_id="tenant-001", request=_mock_request(),
        )
        assert isinstance(result, RecoveryStatusResponse)
        assert result.tenant_id == "tenant-001"
        assert result.recovery_address == "recover@tenant.com"
        assert result.recovery_address_enabled is True

    @pytest.mark.asyncio
    async def test_get_status_tenant_not_found(self, mock_tenant_repo):
        mock_tenant_repo.get_recovery_address.return_value = None
        result = await get_recovery_status(
            tenant_id="nonexistent", request=_mock_request(),
        )
        assert result.status_code == 404


# ---------------------------------------------------------------------------
# Verify recovery token
# ---------------------------------------------------------------------------


class TestVerifyRecoveryToken:

    @pytest.mark.asyncio
    async def test_verify_valid_token_returns_session_jwt(self):
        result = await verify_recovery_token(
            token="test-token-123", tenant="tenant-001",
        )
        assert "session_token" in result
        assert result["tenant_id"] == "tenant-001"
        assert result["email"] == "recover@tenant.com"
        assert result["expires_in"] == 8 * 3600

    @pytest.mark.asyncio
    async def test_verify_consumed_token_fails(self, mock_verification_repo):
        mock_verification_repo.consume_token.return_value = None
        result = await verify_recovery_token(
            token="consumed-token", tenant="tenant-001",
        )
        assert result.status_code == 400

    @pytest.mark.asyncio
    async def test_verify_token_tenant_mismatch(self, mock_verification_repo):
        mock_verification_repo.consume_token.return_value = {
            "id": "test-token-123",
            "token_type": "account_recovery",
            "tenant_id": "tenant-001",
            "email": "recover@tenant.com",
        }
        result = await verify_recovery_token(
            token="test-token-123", tenant="different-tenant",
        )
        assert result.status_code == 400

    @pytest.mark.asyncio
    async def test_verify_audit_logged(self, mock_audit_repo):
        await verify_recovery_token(
            token="test-token-123", tenant="tenant-001",
        )
        mock_audit_repo.log_event.assert_called_once()
        assert "account_recovery_verified" in str(
            mock_audit_repo.log_event.call_args.kwargs["payload"],
        )


# ---------------------------------------------------------------------------
# Auth-exempt path
# ---------------------------------------------------------------------------


class TestAuthExemptPath:

    def test_account_recovery_path_is_auth_exempt(self):
        from src.multi_tenant.auth import AUTH_EXEMPT_PREFIXES
        assert any(
            "/api/auth/account-recovery" in p for p in AUTH_EXEMPT_PREFIXES
        )


# ---------------------------------------------------------------------------
# Router registration
# ---------------------------------------------------------------------------


class TestRouterRegistration:

    def test_tenant_recovery_router_exists(self):
        from src.multi_tenant.tenant_recovery import router
        assert router.prefix == "/api/superadmin/tenant-recovery"

    def test_recovery_verify_router_exists(self):
        from src.multi_tenant.tenant_recovery import recovery_verify_router
        assert recovery_verify_router.prefix == "/api/auth/account-recovery"

    def test_spa_facing_routes(self):
        from src.multi_tenant.tenant_recovery import router
        routes = [r.path for r in router.routes]
        assert any("activate" in r for r in routes)
        assert any("send-auth-link" in r for r in routes)
        assert any("status" in r for r in routes)

    def test_public_verify_route(self):
        from src.multi_tenant.tenant_recovery import recovery_verify_router
        routes = [r.path for r in recovery_verify_router.routes]
        assert any("verify" in r for r in routes)
