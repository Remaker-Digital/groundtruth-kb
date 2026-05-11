"""Tests for SPA Emergency Key Recovery (SPEC-1678).

Covers:
    POST /api/auth/spa-recovery/recover — recover SPA API key via backup code
    Rate limiting (3 per 15 min per IP)
    Backup code consumption after use
    Enumeration prevention (always returns 200)
    Email delivery on valid recovery
    Audit event logging

Run:
    pytest tests/multi_tenant/test_spa_recovery.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.auth import hash_api_key
from src.multi_tenant.cosmos_schema import AuditEventType
from src.multi_tenant.security_hardening import get_rate_limit_backend
from src.multi_tenant.spa_recovery import (
    RecoveryRequest,
    RecoveryResponse,
    _is_rate_limited,
    configure_spa_recovery,
    recover_spa_key,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

BACKUP_CODE_1 = "a1b2c3d4"
BACKUP_CODE_2 = "e5f6a7b8"
BACKUP_CODE_HASH_1 = hash_api_key(BACKUP_CODE_1)
BACKUP_CODE_HASH_2 = hash_api_key(BACKUP_CODE_2)


def _admin_doc() -> dict:
    """Sample platform admin document with backup codes."""
    return {
        "id": "admin-001",
        "admin_id": "admin-001",
        "email": "super@remaker.digital",
        "display_name": "Super Admin",
        "role": "superadmin",
        "is_active": True,
        "api_key_hash": "old_hash_value",
        "backup_recovery_code_hashes": [BACKUP_CODE_HASH_1, BACKUP_CODE_HASH_2],
        "backup_codes_remaining": 2,
        "notification_email_address": None,
    }


def _mock_request(client_ip: str = "10.0.0.1") -> MagicMock:
    """Create a mock FastAPI Request."""
    request = MagicMock()
    request.scope = {"client": (client_ip, 12345)}
    return request


@pytest.fixture()
def mock_pa_repo():
    repo = MagicMock()
    repo.find_by_email = AsyncMock(return_value=_admin_doc())
    repo.update_api_key_hash = AsyncMock()
    repo.consume_backup_code = AsyncMock()
    return repo


@pytest.fixture()
def mock_audit_repo():
    repo = MagicMock()
    repo.log_event = AsyncMock()
    return repo


@pytest.fixture(autouse=True)
def _wire_repos(mock_pa_repo, mock_audit_repo):
    configure_spa_recovery(
        platform_admin_repo=mock_pa_repo,
        audit_repo=mock_audit_repo,
    )
    yield
    configure_spa_recovery(
        platform_admin_repo=None,
        audit_repo=None,
    )


@pytest.fixture(autouse=True)
def _clear_rate_limit():
    """Clear rate limit state between tests via shared backend."""
    backend = get_rate_limit_backend()
    if hasattr(backend, "_windows"):
        backend._windows.clear()
    yield
    if hasattr(backend, "_windows"):
        backend._windows.clear()


# ---------------------------------------------------------------------------
# Valid recovery
# ---------------------------------------------------------------------------


class TestValidRecovery:

    @pytest.mark.asyncio
    async def test_recovery_returns_200_with_valid_code(self, mock_pa_repo):
        body = RecoveryRequest(email="super@remaker.digital", backup_code=BACKUP_CODE_1)
        result = await recover_spa_key(body=body, request=_mock_request())
        assert isinstance(result, RecoveryResponse)
        assert "email" in result.message.lower()

    @pytest.mark.asyncio
    async def test_recovery_generates_new_key(self, mock_pa_repo):
        body = RecoveryRequest(email="super@remaker.digital", backup_code=BACKUP_CODE_1)
        await recover_spa_key(body=body, request=_mock_request())
        mock_pa_repo.update_api_key_hash.assert_called_once()
        call_kwargs = mock_pa_repo.update_api_key_hash.call_args.kwargs
        assert call_kwargs["admin_id"] == "admin-001"
        assert len(call_kwargs["new_key_hash"]) == 64  # SHA-256

    @pytest.mark.asyncio
    async def test_recovery_consumes_backup_code(self, mock_pa_repo):
        body = RecoveryRequest(email="super@remaker.digital", backup_code=BACKUP_CODE_1)
        await recover_spa_key(body=body, request=_mock_request())
        mock_pa_repo.consume_backup_code.assert_called_once()
        call_kwargs = mock_pa_repo.consume_backup_code.call_args.kwargs
        remaining = call_kwargs["remaining_hashes"]
        assert BACKUP_CODE_HASH_1 not in remaining
        assert BACKUP_CODE_HASH_2 in remaining
        assert call_kwargs["new_count"] == 1

    @pytest.mark.asyncio
    @patch("src.multi_tenant.spa_recovery._send_recovery_email", new_callable=AsyncMock)
    async def test_recovery_sends_email(self, mock_send_email, mock_pa_repo):
        body = RecoveryRequest(email="super@remaker.digital", backup_code=BACKUP_CODE_1)
        await recover_spa_key(body=body, request=_mock_request())
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert call_args[0][0] == "super@remaker.digital"
        assert call_args[0][1].startswith("ar_spa_plat_")

    @pytest.mark.asyncio
    async def test_recovery_logs_audit_event(self, mock_audit_repo):
        body = RecoveryRequest(email="super@remaker.digital", backup_code=BACKUP_CODE_1)
        await recover_spa_key(body=body, request=_mock_request())
        mock_audit_repo.log_event.assert_called_once()
        call_kwargs = mock_audit_repo.log_event.call_args.kwargs
        assert call_kwargs["event_type"] == AuditEventType.SECURITY_EVENT
        assert "spa_key_recovery" in str(call_kwargs["payload"])


# ---------------------------------------------------------------------------
# Enumeration prevention
# ---------------------------------------------------------------------------


class TestEnumerationPrevention:

    @pytest.mark.asyncio
    async def test_invalid_email_returns_200(self, mock_pa_repo):
        mock_pa_repo.find_by_email.return_value = None
        body = RecoveryRequest(email="nonexistent@test.com", backup_code="aaaabbbb")
        result = await recover_spa_key(body=body, request=_mock_request())
        assert isinstance(result, RecoveryResponse)
        # Key should NOT be regenerated
        mock_pa_repo.update_api_key_hash.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_code_returns_200(self, mock_pa_repo):
        body = RecoveryRequest(email="super@remaker.digital", backup_code="invalidcode")
        result = await recover_spa_key(body=body, request=_mock_request())
        assert isinstance(result, RecoveryResponse)
        mock_pa_repo.update_api_key_hash.assert_not_called()
        mock_pa_repo.consume_backup_code.assert_not_called()

    @pytest.mark.asyncio
    async def test_same_message_for_valid_and_invalid(self, mock_pa_repo):
        # Valid request
        valid_body = RecoveryRequest(
            email="super@remaker.digital", backup_code=BACKUP_CODE_1,
        )
        valid_result = await recover_spa_key(body=valid_body, request=_mock_request("10.0.0.2"))

        # Invalid request
        mock_pa_repo.find_by_email.return_value = None
        invalid_body = RecoveryRequest(email="nobody@test.com", backup_code="ffffffff")
        invalid_result = await recover_spa_key(body=invalid_body, request=_mock_request("10.0.0.3"))

        assert valid_result.message == invalid_result.message


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


class TestRateLimiting:

    @pytest.mark.asyncio
    async def test_rate_limit_after_3_attempts(self, mock_pa_repo):
        mock_pa_repo.find_by_email.return_value = None
        body = RecoveryRequest(email="test@test.com", backup_code="aaaabbbb")
        ip = "192.168.1.100"

        # 3 attempts should succeed (200)
        for _ in range(3):
            result = await recover_spa_key(body=body, request=_mock_request(ip))
            assert isinstance(result, RecoveryResponse)

        # 4th attempt should be rate limited (429)
        result = await recover_spa_key(body=body, request=_mock_request(ip))
        # Rate limited returns JSONResponse with 429
        assert hasattr(result, "status_code")
        assert result.status_code == 429

    @pytest.mark.asyncio
    async def test_different_ips_not_affected(self, mock_pa_repo):
        mock_pa_repo.find_by_email.return_value = None
        body = RecoveryRequest(email="test@test.com", backup_code="aaaabbbb")

        # Exhaust rate limit on IP1
        for _ in range(3):
            await recover_spa_key(body=body, request=_mock_request("10.0.0.10"))

        # IP2 should still work
        result = await recover_spa_key(body=body, request=_mock_request("10.0.0.11"))
        assert isinstance(result, RecoveryResponse)

    def test_rate_limit_function_directly(self):
        ip = "10.0.0.50"
        assert not _is_rate_limited(ip)
        assert not _is_rate_limited(ip)
        assert not _is_rate_limited(ip)
        assert _is_rate_limited(ip)  # 4th attempt blocked

    def test_rate_limit_window_expires(self):
        ip = "10.0.0.60"
        # Manually add old timestamps to the shared backend
        backend = get_rate_limit_backend()
        key = f"spa_recovery:{ip}"
        backend._windows[key] = [time.time() - 1000, time.time() - 1000, time.time() - 1000]
        # Should NOT be rate limited (all entries older than 15 min)
        assert not _is_rate_limited(ip)


# ---------------------------------------------------------------------------
# Backup code consumed
# ---------------------------------------------------------------------------


class TestBackupCodeConsumption:

    @pytest.mark.asyncio
    async def test_consumed_code_not_in_remaining(self, mock_pa_repo):
        body = RecoveryRequest(email="super@remaker.digital", backup_code=BACKUP_CODE_1)
        await recover_spa_key(body=body, request=_mock_request())
        call_kwargs = mock_pa_repo.consume_backup_code.call_args.kwargs
        assert BACKUP_CODE_HASH_1 not in call_kwargs["remaining_hashes"]

    @pytest.mark.asyncio
    async def test_other_codes_preserved(self, mock_pa_repo):
        body = RecoveryRequest(email="super@remaker.digital", backup_code=BACKUP_CODE_1)
        await recover_spa_key(body=body, request=_mock_request())
        call_kwargs = mock_pa_repo.consume_backup_code.call_args.kwargs
        assert BACKUP_CODE_HASH_2 in call_kwargs["remaining_hashes"]


# ---------------------------------------------------------------------------
# Repo not configured
# ---------------------------------------------------------------------------


class TestRepoNotConfigured:

    @pytest.mark.asyncio
    async def test_returns_200_when_repo_not_configured(self):
        configure_spa_recovery(platform_admin_repo=None, audit_repo=None)
        body = RecoveryRequest(email="test@test.com", backup_code="aaaabbbb")
        result = await recover_spa_key(body=body, request=_mock_request())
        assert isinstance(result, RecoveryResponse)


# ---------------------------------------------------------------------------
# Auth-exempt path
# ---------------------------------------------------------------------------


class TestAuthExempt:

    def test_spa_recovery_path_is_auth_exempt(self):
        from src.multi_tenant.auth import AUTH_EXEMPT_PREFIXES
        assert any("/api/auth/spa-recovery" in p for p in AUTH_EXEMPT_PREFIXES)


# ---------------------------------------------------------------------------
# Router registration
# ---------------------------------------------------------------------------


class TestRouterRegistration:

    def test_spa_recovery_router_exists(self):
        from src.multi_tenant.spa_recovery import router
        assert router.prefix == "/api/auth/spa-recovery"
        routes = [r.path for r in router.routes]
        assert any("recover" in r for r in routes)
