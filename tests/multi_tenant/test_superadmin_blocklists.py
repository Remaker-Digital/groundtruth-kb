"""Tests for superadmin block/allow list and maintenance mode endpoints.

Validates SPEC-1820 (Allow/Block Lists) and SPEC-1829 (Maintenance Mode).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api._blocklists import (
    VALID_LIST_TYPES,
    BlocklistCheckRequest,
    BlocklistCheckResponse,
    BlocklistDocument,
    BlocklistEntry,
    BlocklistResponse,
    BlocklistWriteResponse,
    MaintenanceResponse,
    MaintenanceState,
    MaintenanceWriteResponse,
    check_blocklist,
    is_maintenance_active,
    list_blocklists,
    get_blocklist,
    put_blocklist,
    check_blocklist_value,
    get_maintenance,
    put_maintenance,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_platform_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.get_config.return_value = None
    repo.set_config.return_value = {}
    return repo


@pytest.fixture
def mock_tenant_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.tenant_id = "__platform__"
    ctx.team_member_email = "admin@remaker.digital"
    ctx.tier = "enterprise"
    ctx.api_key_type = "PLATFORM_ADMIN"
    return ctx


@pytest.fixture
def sample_ip_blocklist_doc() -> dict[str, Any]:
    return {
        "id": "blocklists:ip",
        "config_type": "blocklists",
        "config_key": "ip",
        "value": {
            "entries": [
                {"value": "10.0.0.1", "action": "block", "reason": "Known bad actor"},
                {"value": "192.168.", "action": "block", "reason": "Internal network prefix"},
                {"value": "203.0.113.50", "action": "allow", "reason": "Monitoring service"},
            ],
            "default_action": "allow",
        },
        "version": 1,
        "updated_at": "2026-03-16T00:00:00+00:00",
        "updated_by": "admin@remaker.digital",
    }


@pytest.fixture
def sample_domain_blocklist_doc() -> dict[str, Any]:
    return {
        "id": "blocklists:email_domain",
        "config_type": "blocklists",
        "config_key": "email_domain",
        "value": {
            "entries": [
                {"value": ".spam.com", "action": "block", "reason": "Spam domain"},
                {"value": "trusted.org", "action": "allow", "reason": "Trusted partner"},
            ],
            "default_action": "allow",
        },
        "version": 2,
        "updated_at": "2026-03-16T12:00:00+00:00",
        "updated_by": "admin@remaker.digital",
    }


@pytest.fixture
def sample_maintenance_doc() -> dict[str, Any]:
    return {
        "id": "maintenance:mode",
        "config_type": "maintenance",
        "config_key": "mode",
        "value": {
            "enabled": True,
            "message": "Scheduled maintenance in progress.",
            "retry_after_seconds": 600,
            "scheduled_start": None,
            "scheduled_end": None,
            "exempt_ips": ["98.210.223.74"],
        },
        "version": 1,
        "updated_at": "2026-03-16T00:00:00+00:00",
        "updated_by": "admin@remaker.digital",
    }


# ---------------------------------------------------------------------------
# SPEC-1820: check_blocklist() unit logic
# ---------------------------------------------------------------------------


class TestCheckBlocklist:
    """SPEC-1820: Blocklist evaluation logic."""

    def test_exact_match_blocks(self):
        data = {
            "entries": [{"value": "10.0.0.1", "action": "block", "reason": "bad"}],
            "default_action": "allow",
        }
        action, matched, reason = check_blocklist(data, "10.0.0.1")
        assert action == "block"
        assert matched == "10.0.0.1"

    def test_exact_match_case_insensitive(self):
        data = {
            "entries": [{"value": "BadBot/1.0", "action": "block"}],
            "default_action": "allow",
        }
        action, _, _ = check_blocklist(data, "badbot/1.0")
        assert action == "block"

    def test_prefix_match_ip(self):
        """IP prefix '192.168.' matches '192.168.1.1'."""
        data = {
            "entries": [{"value": "192.168.", "action": "block", "reason": "internal"}],
            "default_action": "allow",
        }
        action, _, _ = check_blocklist(data, "192.168.1.1")
        assert action == "block"

    def test_prefix_no_match(self):
        data = {
            "entries": [{"value": "192.168.", "action": "block"}],
            "default_action": "allow",
        }
        action, matched, _ = check_blocklist(data, "10.0.0.1")
        assert action == "allow"
        assert matched is None

    def test_suffix_match_domain(self):
        """Domain suffix '.spam.com' matches 'test.spam.com'."""
        data = {
            "entries": [{"value": ".spam.com", "action": "block"}],
            "default_action": "allow",
        }
        action, _, _ = check_blocklist(data, "test.spam.com")
        assert action == "block"

    def test_suffix_match_exact_domain(self):
        """Domain suffix '.spam.com' also matches 'spam.com'."""
        data = {
            "entries": [{"value": ".spam.com", "action": "block"}],
            "default_action": "allow",
        }
        action, _, _ = check_blocklist(data, "spam.com")
        assert action == "block"

    def test_allow_entry(self):
        data = {
            "entries": [{"value": "trusted.org", "action": "allow"}],
            "default_action": "block",
        }
        action, _, _ = check_blocklist(data, "trusted.org")
        assert action == "allow"

    def test_default_action_when_no_match(self):
        data = {"entries": [], "default_action": "block"}
        action, matched, _ = check_blocklist(data, "unknown.example.com")
        assert action == "block"
        assert matched is None

    def test_empty_entries(self):
        data = {"entries": [], "default_action": "allow"}
        action, _, _ = check_blocklist(data, "anything")
        assert action == "allow"

    def test_first_match_wins(self):
        """When multiple entries match, first one wins."""
        data = {
            "entries": [
                {"value": "10.0.0.1", "action": "allow", "reason": "exception"},
                {"value": "10.0.0.", "action": "block", "reason": "subnet"},
            ],
            "default_action": "allow",
        }
        action, _, reason = check_blocklist(data, "10.0.0.1")
        assert action == "allow"
        assert reason == "exception"


# ---------------------------------------------------------------------------
# SPEC-1820: Blocklist CRUD endpoints
# ---------------------------------------------------------------------------


class TestBlocklistCRUD:
    """SPEC-1820: Block/allow list CRUD API."""

    @pytest.mark.asyncio
    async def test_list_all_blocklists(self, mock_platform_repo, sample_ip_blocklist_doc):
        mock_platform_repo.get_config.side_effect = lambda ct, ck: (
            sample_ip_blocklist_doc if ck == "ip" else None
        )
        with patch(
            "src.multi_tenant.superadmin_api._blocklists._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await list_blocklists()

        assert len(result.lists) == len(VALID_LIST_TYPES)
        ip_list = [l for l in result.lists if l.list_type == "ip"]
        assert len(ip_list) == 1
        assert len(ip_list[0].entries) == 3

    @pytest.mark.asyncio
    async def test_get_existing_blocklist(self, mock_platform_repo, sample_ip_blocklist_doc):
        mock_platform_repo.get_config.return_value = sample_ip_blocklist_doc
        with patch(
            "src.multi_tenant.superadmin_api._blocklists._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_blocklist("ip")

        assert result.list_type == "ip"
        assert len(result.entries) == 3
        assert result.version == 1

    @pytest.mark.asyncio
    async def test_get_empty_blocklist(self, mock_platform_repo):
        mock_platform_repo.get_config.return_value = None
        with patch(
            "src.multi_tenant.superadmin_api._blocklists._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_blocklist("email_domain")

        assert result.list_type == "email_domain"
        assert result.entries == []

    @pytest.mark.asyncio
    async def test_get_invalid_list_type_400(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_blocklist("invalid_type")
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_put_blocklist(self, mock_platform_repo, mock_tenant_ctx):
        mock_platform_repo.get_config.return_value = None

        with patch(
            "src.multi_tenant.superadmin_api._blocklists._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
        ):
            body = BlocklistDocument(entries=[
                BlocklistEntry(value="10.0.0.1", action="block", reason="test"),
            ])
            result = await put_blocklist("ip", body, mock_tenant_ctx)

        assert isinstance(result, BlocklistWriteResponse)
        assert result.version == 1
        assert result.entry_count == 1
        mock_platform_repo.set_config.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_check_value_against_blocklist(
        self, mock_platform_repo, sample_ip_blocklist_doc,
    ):
        mock_platform_repo.get_config.return_value = sample_ip_blocklist_doc
        with patch(
            "src.multi_tenant.superadmin_api._blocklists._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await check_blocklist_value(
                "ip", BlocklistCheckRequest(value="10.0.0.1"),
            )

        assert result.action == "block"
        assert result.matched_entry == "10.0.0.1"


# ---------------------------------------------------------------------------
# SPEC-1829: Maintenance mode logic
# ---------------------------------------------------------------------------


class TestMaintenanceModeLogic:
    """SPEC-1829: Maintenance mode activation logic."""

    def test_disabled_is_not_active(self):
        state = MaintenanceState(enabled=False)
        assert is_maintenance_active(state) is False

    def test_enabled_no_schedule_is_active(self):
        state = MaintenanceState(enabled=True)
        assert is_maintenance_active(state) is True

    def test_scheduled_future_start_not_active(self):
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        state = MaintenanceState(enabled=True, scheduled_start=future)
        assert is_maintenance_active(state) is False

    def test_scheduled_past_start_is_active(self):
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        state = MaintenanceState(enabled=True, scheduled_start=past)
        assert is_maintenance_active(state) is True

    def test_scheduled_past_end_not_active(self):
        past_start = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        past_end = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        state = MaintenanceState(
            enabled=True, scheduled_start=past_start, scheduled_end=past_end,
        )
        assert is_maintenance_active(state) is False

    def test_within_schedule_window_is_active(self):
        past_start = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        future_end = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        state = MaintenanceState(
            enabled=True, scheduled_start=past_start, scheduled_end=future_end,
        )
        assert is_maintenance_active(state) is True

    def test_exempt_ips_field_preserved(self):
        state = MaintenanceState(enabled=True, exempt_ips=["1.2.3.4"])
        assert "1.2.3.4" in state.exempt_ips


# ---------------------------------------------------------------------------
# SPEC-1829: Maintenance mode CRUD endpoints
# ---------------------------------------------------------------------------


class TestMaintenanceModeCRUD:
    """SPEC-1829: Maintenance mode API."""

    @pytest.mark.asyncio
    async def test_get_default_state(self, mock_platform_repo):
        mock_platform_repo.get_config.return_value = None
        with patch(
            "src.multi_tenant.superadmin_api._blocklists._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_maintenance()

        assert isinstance(result, MaintenanceResponse)
        assert result.is_active is False
        assert result.state.enabled is False

    @pytest.mark.asyncio
    async def test_get_active_maintenance(self, mock_platform_repo, sample_maintenance_doc):
        mock_platform_repo.get_config.return_value = sample_maintenance_doc
        with patch(
            "src.multi_tenant.superadmin_api._blocklists._get_platform_repo",
            return_value=mock_platform_repo,
        ):
            result = await get_maintenance()

        assert result.is_active is True
        assert result.state.message == "Scheduled maintenance in progress."
        assert result.state.retry_after_seconds == 600

    @pytest.mark.asyncio
    async def test_put_enable_maintenance(self, mock_platform_repo, mock_tenant_ctx):
        mock_platform_repo.get_config.return_value = None

        with patch(
            "src.multi_tenant.superadmin_api._blocklists._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
        ):
            body = MaintenanceState(
                enabled=True, message="Going down for upgrade.",
                retry_after_seconds=120,
            )
            result = await put_maintenance(body, mock_tenant_ctx)

        assert isinstance(result, MaintenanceWriteResponse)
        assert result.is_active is True
        assert result.version == 1

    @pytest.mark.asyncio
    async def test_put_disable_maintenance(self, mock_platform_repo, mock_tenant_ctx):
        mock_platform_repo.get_config.return_value = None

        with patch(
            "src.multi_tenant.superadmin_api._blocklists._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
        ):
            body = MaintenanceState(enabled=False)
            result = await put_maintenance(body, mock_tenant_ctx)

        assert result.is_active is False

    @pytest.mark.asyncio
    async def test_put_schedule_maintenance(self, mock_platform_repo, mock_tenant_ctx):
        """Schedule maintenance for a future window."""
        mock_platform_repo.get_config.return_value = None
        future_start = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        future_end = (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat()

        with patch(
            "src.multi_tenant.superadmin_api._blocklists._get_platform_repo",
            return_value=mock_platform_repo,
        ), patch(
            "src.multi_tenant.repositories.platform.AuditLogRepository",
        ):
            body = MaintenanceState(
                enabled=True,
                scheduled_start=future_start,
                scheduled_end=future_end,
            )
            result = await put_maintenance(body, mock_tenant_ctx)

        # Not yet active because scheduled_start is in the future
        assert result.is_active is False
