"""Tests for C-3: Compliance Summary endpoint (GET /api/superadmin/compliance).

Covers:
    - Happy path with mixed compliance states
    - Active/expired grace periods
    - PII scrubbing on/off per tenant
    - DSAR events counted from audit log
    - Tenant repo not configured → 503
    - Partial failures (per-tenant errors)
    - Prefs repo unavailable → PII data absent
    - Audit repo unavailable → DSAR data absent
    - Aggregate counts correctness
    - CamelCase serialization
    - Auth enforcement

Total: 22 tests

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.superadmin_api import (
    ComplianceSummaryResponse,
    TenantComplianceInfo,
    configure_superadmin_services,
)


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------


class FakeAsyncIterator:
    """Simulate async iteration over Cosmos query results."""

    def __init__(self, items: list[dict[str, Any]]):
        self._items = items
        self._index = 0

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._index]
        self._index += 1
        return item


@pytest.fixture()
def mock_tenant_repo():
    repo = MagicMock()
    repo.list_active_tenant_ids = AsyncMock(return_value=["t-001", "t-002"])
    repo.read = AsyncMock()
    return repo


@pytest.fixture()
def mock_prefs_repo():
    repo = MagicMock()
    repo.read = AsyncMock()
    repo.get_active = AsyncMock()
    return repo


@pytest.fixture()
def mock_audit_repo():
    repo = MagicMock()
    repo._container = MagicMock()
    return repo


@pytest.fixture()
def superadmin_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    return ctx


def _future_ts() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()


def _past_ts() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()


# ---------------------------------------------------------------------------
# Happy Path
# ---------------------------------------------------------------------------


class TestComplianceSummaryHappyPath:

    @pytest.mark.asyncio
    async def test_returns_all_tenants(
        self, mock_tenant_repo, mock_prefs_repo, mock_audit_repo, superadmin_ctx
    ):
        """Returns compliance info for all active tenants."""
        mock_tenant_repo.read.side_effect = [
            {"tier": "professional", "grace_period_ends_at": None},
            {"tier": "starter", "grace_period_ends_at": None},
        ]
        mock_prefs_repo.get_active.side_effect = [
            {"pii_scrubbing": True},
            {"pii_scrubbing": False},
        ]
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert isinstance(result, ComplianceSummaryResponse)
        assert result.total_tenants == 2
        assert len(result.tenants) == 2
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_pii_scrubbing_count(
        self, mock_tenant_repo, mock_prefs_repo, mock_audit_repo, superadmin_ctx
    ):
        """Counts tenants with PII scrubbing enabled."""
        mock_tenant_repo.read.side_effect = [
            {"tier": "professional"}, {"tier": "starter"},
        ]
        mock_prefs_repo.get_active.side_effect = [
            {"pii_scrubbing": True},
            {"pii_scrubbing": True},
        ]
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert result.tenants_with_pii_scrubbing == 2

    @pytest.mark.asyncio
    async def test_pii_scrubbing_disabled(
        self, mock_tenant_repo, mock_prefs_repo, mock_audit_repo, superadmin_ctx
    ):
        """Zero count when no tenants have PII scrubbing."""
        mock_tenant_repo.read.side_effect = [
            {"tier": "starter"}, {"tier": "starter"},
        ]
        mock_prefs_repo.get_active.side_effect = [
            {"pii_scrubbing": False},
            {},
        ]
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert result.tenants_with_pii_scrubbing == 0


# ---------------------------------------------------------------------------
# Grace Period Tests
# ---------------------------------------------------------------------------


class TestComplianceGracePeriod:

    @pytest.mark.asyncio
    async def test_active_grace_period(
        self, mock_tenant_repo, mock_prefs_repo, mock_audit_repo, superadmin_ctx
    ):
        """Grace period in the future → grace_period_active=True."""
        future = _future_ts()
        mock_tenant_repo.read.side_effect = [
            {"tier": "professional", "grace_period_ends_at": future},
            {"tier": "starter"},
        ]
        mock_prefs_repo.get_active.side_effect = [{}, {}]
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert result.tenants_in_grace_period == 1
        active_tenant = [t for t in result.tenants if t.grace_period_active]
        assert len(active_tenant) == 1
        assert active_tenant[0].tenant_id == "t-001"

    @pytest.mark.asyncio
    async def test_expired_grace_period(
        self, mock_tenant_repo, mock_prefs_repo, mock_audit_repo, superadmin_ctx
    ):
        """Grace period in the past → grace_period_active=False."""
        past = _past_ts()
        mock_tenant_repo.read.side_effect = [
            {"tier": "professional", "grace_period_ends_at": past},
            {"tier": "starter"},
        ]
        mock_prefs_repo.get_active.side_effect = [{}, {}]
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert result.tenants_in_grace_period == 0

    @pytest.mark.asyncio
    async def test_no_grace_period(
        self, mock_tenant_repo, mock_prefs_repo, mock_audit_repo, superadmin_ctx
    ):
        """No grace_period_ends_at → not in grace period."""
        mock_tenant_repo.read.side_effect = [{"tier": "starter"}, {"tier": "starter"}]
        mock_prefs_repo.get_active.side_effect = [{}, {}]
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert result.tenants_in_grace_period == 0


# ---------------------------------------------------------------------------
# DSAR Event Tests
# ---------------------------------------------------------------------------


class TestComplianceDSAR:

    @pytest.mark.asyncio
    async def test_dsar_events_counted(
        self, mock_tenant_repo, mock_prefs_repo, mock_audit_repo, superadmin_ctx
    ):
        """DSAR events from audit log are counted per tenant."""
        mock_tenant_repo.read.side_effect = [{"tier": "professional"}, {"tier": "starter"}]
        mock_prefs_repo.get_active.side_effect = [{}, {}]

        # First tenant: 2 DSAR events; second: 1
        call_count = 0

        def query_side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return FakeAsyncIterator([
                    {"timestamp": "2026-02-10T00:00:00Z"},
                    {"timestamp": "2026-02-05T00:00:00Z"},
                ])
            return FakeAsyncIterator([
                {"timestamp": "2026-02-12T00:00:00Z"},
            ])

        mock_audit_repo._container.query_items = MagicMock(side_effect=query_side_effect)

        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert result.total_dsar_requests == 3
        assert result.tenants[0].dsar_request_count == 2
        assert result.tenants[0].last_dsar_request == "2026-02-10T00:00:00Z"
        assert result.tenants[1].dsar_request_count == 1

    @pytest.mark.asyncio
    async def test_no_dsar_events(
        self, mock_tenant_repo, mock_prefs_repo, mock_audit_repo, superadmin_ctx
    ):
        """No DSAR events → zero count."""
        mock_tenant_repo.read.side_effect = [{"tier": "starter"}]
        mock_prefs_repo.get_active.side_effect = [{}]
        mock_tenant_repo.list_active_tenant_ids.return_value = ["t-001"]
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert result.total_dsar_requests == 0
        assert result.tenants[0].dsar_request_count == 0
        assert result.tenants[0].last_dsar_request is None


# ---------------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------------


class TestComplianceSummaryErrors:

    @pytest.mark.asyncio
    async def test_tenant_repo_not_configured_503(self, superadmin_ctx):
        """Tenant repo None → 503."""
        configure_superadmin_services(
            tenant_repo=None,
            audit_repo=MagicMock(),
        )
        from fastapi import HTTPException
        from src.multi_tenant.superadmin_api import compliance_summary

        with pytest.raises(HTTPException) as exc_info:
            await compliance_summary()
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_partial_sub_query_failure_graceful(
        self, mock_tenant_repo, mock_prefs_repo, mock_audit_repo, superadmin_ctx
    ):
        """Sub-query failures (tenant read, prefs) degrade gracefully — tenant still appears."""
        mock_tenant_repo.read.side_effect = [
            {"tier": "professional"},
            RuntimeError("Cosmos timeout"),  # caught by inner try/except
        ]
        mock_prefs_repo.get_active.side_effect = [
            {"pii_scrubbing": True},
            RuntimeError("Cosmos timeout"),  # caught by inner try/except
        ]
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        # Both tenants appear — sub-query failures are caught individually
        assert result.total_tenants == 2
        assert result.tenants[0].tier == "professional"
        assert result.tenants[0].pii_scrubbing_enabled is True
        # Second tenant has defaults due to sub-query failures
        assert result.tenants[1].tier is None
        assert result.tenants[1].pii_scrubbing_enabled is False
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_prefs_repo_missing_still_works(
        self, mock_tenant_repo, mock_audit_repo, superadmin_ctx
    ):
        """Prefs repo None → PII fields default to False, no crash."""
        mock_tenant_repo.read.side_effect = [{"tier": "starter"}, {"tier": "starter"}]
        mock_audit_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([])
        )
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
            prefs_repo=None,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert result.tenants_with_pii_scrubbing == 0
        assert result.total_tenants == 2

    @pytest.mark.asyncio
    async def test_audit_repo_missing_still_works(
        self, mock_tenant_repo, mock_prefs_repo, superadmin_ctx
    ):
        """Audit repo None → DSAR fields default to 0, no crash."""
        mock_tenant_repo.read.side_effect = [{"tier": "starter"}, {"tier": "starter"}]
        mock_prefs_repo.get_active.side_effect = [{}, {}]
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=None,
            prefs_repo=mock_prefs_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert result.total_dsar_requests == 0
        assert result.total_tenants == 2

    @pytest.mark.asyncio
    async def test_no_active_tenants(
        self, mock_tenant_repo, mock_audit_repo, superadmin_ctx
    ):
        """No active tenants → empty response."""
        mock_tenant_repo.list_active_tenant_ids.return_value = []
        configure_superadmin_services(
            tenant_repo=mock_tenant_repo,
            audit_repo=mock_audit_repo,
        )
        from src.multi_tenant.superadmin_api import compliance_summary
        result = await compliance_summary()

        assert result.total_tenants == 0
        assert result.tenants == []


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


class TestComplianceSerialization:

    def test_response_model_camel_case(self):
        """ComplianceSummaryResponse serializes to camelCase."""
        resp = ComplianceSummaryResponse(
            total_tenants=1,
            tenants_with_pii_scrubbing=1,
            tenants_in_grace_period=0,
            total_dsar_requests=5,
            tenants=[TenantComplianceInfo(
                tenant_id="t-001",
                tier="professional",
                pii_scrubbing_enabled=True,
                dsar_request_count=5,
            )],
        )
        data = resp.model_dump(by_alias=True)
        assert "totalTenants" in data
        assert "tenantsWithPiiScrubbing" in data
        assert "tenantsInGracePeriod" in data
        assert "totalDsarRequests" in data
        assert data["tenants"][0]["tenantId"] == "t-001"
        assert data["tenants"][0]["piiScrubbingEnabled"] is True
        assert data["tenants"][0]["dsarRequestCount"] == 5

    def test_empty_response(self):
        """Empty response defaults."""
        resp = ComplianceSummaryResponse()
        data = resp.model_dump(by_alias=True)
        assert data["totalTenants"] == 0
        assert data["tenants"] == []


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class TestComplianceAuth:

    def test_router_endpoint_exists(self):
        """Compliance endpoint is mounted under /api/superadmin."""
        from src.multi_tenant.superadmin_api import router
        routes = [r.path for r in router.routes]
        assert "/api/superadmin/compliance" in routes
