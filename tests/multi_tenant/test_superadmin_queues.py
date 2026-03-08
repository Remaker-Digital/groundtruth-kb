"""Tests for C-1: Queue Depth endpoint (GET /api/superadmin/queues).

Covers:
    - Happy path with multiple tenants
    - Empty queues (no messages)
    - Single tenant with messages
    - NATS disconnected → 503
    - NATS manager not configured → 503
    - Tenant repo not configured → 503
    - Partial failures (per-tenant errors in errors[])
    - Aggregate totals correctness
    - CamelCase serialization
    - Auth enforcement (SUPERADMIN-only)

Total: 22 tests

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.superadmin_api import (
    QueueDepthResponse,
    TenantQueueInfo,
    configure_superadmin_services,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_nats_mgr():
    """Create a mock NATS manager with is_connected=True."""
    mgr = MagicMock()
    mgr.is_connected = True
    mgr.get_tenant_stream_info = AsyncMock()
    return mgr


@pytest.fixture()
def mock_tenant_repo():
    """Create a mock TenantRepository."""
    repo = MagicMock()
    repo.list_active_tenant_ids = AsyncMock(return_value=["t-001", "t-002", "t-003"])
    return repo


@pytest.fixture()
def superadmin_ctx():
    """Create a fake SUPERADMIN TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    return ctx


STREAM_INFO_T001 = {
    "stream_name": "AGENT_RED_t-001",
    "messages": 42,
    "bytes": 8192,
    "consumer_count": 2,
    "first_seq": 1,
    "last_seq": 42,
}

STREAM_INFO_T002 = {
    "stream_name": "AGENT_RED_t-002",
    "messages": 100,
    "bytes": 20480,
    "consumer_count": 1,
    "first_seq": 1,
    "last_seq": 100,
}

STREAM_INFO_T003 = {
    "stream_name": "AGENT_RED_t-003",
    "messages": 0,
    "bytes": 0,
    "consumer_count": 0,
    "first_seq": 0,
    "last_seq": 0,
}


# ---------------------------------------------------------------------------
# Happy Path Tests
# ---------------------------------------------------------------------------


class TestQueueDepthHappyPath:
    """Happy path tests for GET /api/superadmin/queues."""

    @pytest.mark.asyncio
    async def test_returns_all_tenants(self, mock_nats_mgr, mock_tenant_repo, superadmin_ctx):
        """Returns queue info for all active tenants."""
        mock_nats_mgr.get_tenant_stream_info.side_effect = [
            STREAM_INFO_T001, STREAM_INFO_T002, STREAM_INFO_T003,
        ]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
        )
        from src.multi_tenant.superadmin_api import queue_depth
        result = await queue_depth()

        assert isinstance(result, QueueDepthResponse)
        assert result.total_tenants == 3
        assert len(result.tenants) == 3
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_aggregate_totals(self, mock_nats_mgr, mock_tenant_repo, superadmin_ctx):
        """Total messages and bytes are correctly aggregated."""
        mock_nats_mgr.get_tenant_stream_info.side_effect = [
            STREAM_INFO_T001, STREAM_INFO_T002, STREAM_INFO_T003,
        ]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
        )
        from src.multi_tenant.superadmin_api import queue_depth
        result = await queue_depth()

        assert result.total_messages == 42 + 100 + 0
        assert result.total_bytes == 8192 + 20480 + 0

    @pytest.mark.asyncio
    async def test_per_tenant_details(self, mock_nats_mgr, mock_tenant_repo, superadmin_ctx):
        """Per-tenant queue info is correctly populated."""
        mock_nats_mgr.get_tenant_stream_info.side_effect = [
            STREAM_INFO_T001, STREAM_INFO_T002, STREAM_INFO_T003,
        ]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
        )
        from src.multi_tenant.superadmin_api import queue_depth
        result = await queue_depth()

        t1 = result.tenants[0]
        assert t1.tenant_id == "t-001"
        assert t1.stream_name == "AGENT_RED_t-001"
        assert t1.messages == 42
        assert t1.bytes == 8192
        assert t1.consumer_count == 2

    @pytest.mark.asyncio
    async def test_empty_queues(self, mock_nats_mgr, mock_tenant_repo, superadmin_ctx):
        """All queues empty returns zero totals."""
        mock_tenant_repo.list_active_tenant_ids.return_value = ["t-001"]
        mock_nats_mgr.get_tenant_stream_info.return_value = STREAM_INFO_T003
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
        )
        from src.multi_tenant.superadmin_api import queue_depth
        result = await queue_depth()

        assert result.total_messages == 0
        assert result.total_bytes == 0
        assert result.total_tenants == 1

    @pytest.mark.asyncio
    async def test_no_active_tenants(self, mock_nats_mgr, mock_tenant_repo, superadmin_ctx):
        """No active tenants returns empty response."""
        mock_tenant_repo.list_active_tenant_ids.return_value = []
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
        )
        from src.multi_tenant.superadmin_api import queue_depth
        result = await queue_depth()

        assert result.total_tenants == 0
        assert result.tenants == []
        assert result.total_messages == 0

    @pytest.mark.asyncio
    async def test_none_stream_info_skipped(self, mock_nats_mgr, mock_tenant_repo, superadmin_ctx):
        """Tenant with None stream info is skipped (not in tenants list)."""
        mock_tenant_repo.list_active_tenant_ids.return_value = ["t-001", "t-002"]
        mock_nats_mgr.get_tenant_stream_info.side_effect = [STREAM_INFO_T001, None]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
        )
        from src.multi_tenant.superadmin_api import queue_depth
        result = await queue_depth()

        assert result.total_tenants == 1
        assert len(result.tenants) == 1
        assert result.tenants[0].tenant_id == "t-001"


# ---------------------------------------------------------------------------
# Error Handling Tests
# ---------------------------------------------------------------------------


class TestQueueDepthErrors:
    """Error handling tests for GET /api/superadmin/queues."""

    @pytest.mark.asyncio
    async def test_nats_disconnected_returns_not_deployed(self, mock_nats_mgr, mock_tenant_repo, superadmin_ctx):
        """NATS disconnected returns 200 with nats_deployed=False (decommissioned)."""
        mock_nats_mgr.is_connected = False
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
        )
        from src.multi_tenant.superadmin_api import queue_depth

        result = await queue_depth()
        assert result.nats_deployed is False
        assert result.total_tenants == 0
        assert result.tenants == []

    @pytest.mark.asyncio
    async def test_nats_not_deployed_returns_empty(self, mock_tenant_repo, superadmin_ctx):
        """NATS manager None returns 200 with nats_deployed=False."""
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=None,
        )
        from src.multi_tenant.superadmin_api import queue_depth

        result = await queue_depth()
        assert result.nats_deployed is False
        assert result.total_tenants == 0
        assert result.total_messages == 0
        assert result.tenants == []

    @pytest.mark.asyncio
    async def test_tenant_repo_not_configured_503(self, mock_nats_mgr, superadmin_ctx):
        """Tenant repo None returns 503."""
        configure_superadmin_services(
            tenant_repo=None,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
        )
        from fastapi import HTTPException
        from src.multi_tenant.superadmin_api import queue_depth

        with pytest.raises(HTTPException) as exc_info:
            await queue_depth()
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_partial_failure_in_errors(self, mock_nats_mgr, mock_tenant_repo, superadmin_ctx):
        """Per-tenant failures go into errors[] without crashing."""
        mock_nats_mgr.get_tenant_stream_info.side_effect = [
            STREAM_INFO_T001,
            RuntimeError("Connection lost"),
            STREAM_INFO_T003,
        ]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
        )
        from src.multi_tenant.superadmin_api import queue_depth
        result = await queue_depth()

        assert result.total_tenants == 2
        assert len(result.errors) == 1
        assert result.errors[0]["tenant_id"] == "t-002"
        assert "Connection lost" in result.errors[0]["message"]

    @pytest.mark.asyncio
    async def test_all_tenants_fail(self, mock_nats_mgr, mock_tenant_repo, superadmin_ctx):
        """All tenants failing returns empty tenants with all errors."""
        mock_nats_mgr.get_tenant_stream_info.side_effect = RuntimeError("NATS error")
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=MagicMock(),
            nats_mgr=mock_nats_mgr,
        )
        from src.multi_tenant.superadmin_api import queue_depth
        result = await queue_depth()

        assert result.total_tenants == 0
        assert len(result.errors) == 3
        assert result.total_messages == 0


# ---------------------------------------------------------------------------
# Serialization Tests
# ---------------------------------------------------------------------------


class TestQueueDepthSerialization:
    """CamelCase serialization and model tests."""

    def test_response_model_camel_case(self):
        """QueueDepthResponse serializes to camelCase."""
        resp = QueueDepthResponse(
            total_tenants=1,
            total_messages=42,
            total_bytes=8192,
            tenants=[TenantQueueInfo(
                tenant_id="t-001",
                stream_name="AGENT_RED_t-001",
                messages=42,
                bytes=8192,
                consumer_count=2,
            )],
        )
        data = resp.model_dump(by_alias=True)
        assert "totalTenants" in data
        assert "totalMessages" in data
        assert "totalBytes" in data
        assert data["tenants"][0]["tenantId"] == "t-001"
        assert data["tenants"][0]["streamName"] == "AGENT_RED_t-001"
        assert data["tenants"][0]["consumerCount"] == 2

    def test_empty_response_model(self):
        """Empty response serializes correctly."""
        resp = QueueDepthResponse()
        data = resp.model_dump(by_alias=True)
        assert data["totalTenants"] == 0
        assert data["totalMessages"] == 0
        assert data["tenants"] == []
        assert data["errors"] == []

    def test_errors_in_response(self):
        """Errors list serializes correctly."""
        resp = QueueDepthResponse(
            errors=[{"tenant_id": "t-001", "message": "fail"}],
        )
        data = resp.model_dump(by_alias=True)
        assert len(data["errors"]) == 1
        assert data["errors"][0]["tenant_id"] == "t-001"


# ---------------------------------------------------------------------------
# Auth Tests
# ---------------------------------------------------------------------------


class TestQueueDepthAuth:
    """Authentication enforcement tests."""

    def test_requires_platform_admin(self):
        """SPEC-1667: Endpoint protected by router-level require_platform_admin()."""
        from src.multi_tenant.superadmin_api import router

        assert len(router.dependencies) > 0, (
            "Router must have require_platform_admin() as a dependency"
        )

    def test_router_prefix(self):
        """Endpoint is mounted under /api/superadmin."""
        from src.multi_tenant.superadmin_api import router
        routes = [r.path for r in router.routes]
        assert "/api/superadmin/queues" in routes
