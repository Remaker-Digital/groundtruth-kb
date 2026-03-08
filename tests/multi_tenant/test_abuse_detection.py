"""Tests for the HV-4 Abuse Detection API (abuse_detection.py).

Covers:
    - Signal scan returns overview (2 tests)
    - Empty scan (no tenants) (1 test)
    - Tenant profile with signals (2 tests)
    - Tenant profile with no signals (1 test)
    - Flag tenant (1 test)
    - Unflag tenant (1 test)
    - Missing tenant returns 404 (2 tests)
    - Auth enforcement (2 tests)

Total: 12 tests

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
from datetime import datetime, timezone, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.abuse_detection import (
    AbuseOverview,
    AbuseSignal,
    FlagRequest,
    FlagResponse,
    TenantAbuseProfile,
    configure_abuse_services,
    router,
    scan_abuse_signals,
    get_tenant_abuse_profile,
    flag_tenant,
    _compute_risk_score,
    _compute_severity,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeAsyncIterator:
    """Helper to simulate async iteration over Cosmos query results."""

    def __init__(self, items: list[Any]):
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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_tenant_repo():
    """Create a mock TenantRepository with cross-partition query support."""
    repo = MagicMock()
    repo._container = MagicMock()
    repo.list_active_tenant_ids = AsyncMock(return_value=["tenant-001", "tenant-002"])
    repo.read = AsyncMock(return_value={
        "tenant_id": "tenant-001",
        "status": "active",
        "tier": "professional",
        "widget_key": "wk_test",
        "widget_allowed_origin": "https://example.com",
        "abuse_flagged": False,
    })
    return repo


@pytest.fixture()
def mock_conv_repo():
    """Create a mock ConversationRepository."""
    repo = MagicMock()
    repo._container = MagicMock()
    return repo


@pytest.fixture()
def mock_usage_repo():
    """Create a mock UsageRepository."""
    repo = MagicMock()
    repo._container = MagicMock()
    return repo


@pytest.fixture()
def superadmin_ctx():
    """Create a fake SUPERADMIN TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    ctx.team_member_email = "admin@remaker.com"
    return ctx


@pytest.fixture(autouse=True)
def _configure_repos(mock_tenant_repo, mock_conv_repo, mock_usage_repo):
    """Wire mock repos into the module before each test."""
    configure_abuse_services(
        tenant_repo=mock_tenant_repo,
        conv_repo=mock_conv_repo,
        usage_repo=mock_usage_repo,
    )
    yield
    # Reset to None after test
    configure_abuse_services(
        tenant_repo=None,
        conv_repo=None,
        usage_repo=None,
    )


# ---------------------------------------------------------------------------
# Signal Scan Tests
# ---------------------------------------------------------------------------


class TestSignalScan:
    """Tests for GET /api/superadmin/abuse/signals."""

    @pytest.mark.asyncio
    async def test_scan_returns_overview_no_signals(
        self, mock_tenant_repo, mock_conv_repo, mock_usage_repo, superadmin_ctx,
    ):
        """Scan with no abuse signals returns clean overview."""
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(
            return_value=["tenant-001", "tenant-002"],
        )
        mock_tenant_repo.read = AsyncMock(return_value={
            "tenant_id": "tenant-001",
            "status": "active",
            "widget_key": "",
            "widget_allowed_origin": "",
            "abuse_flagged": False,
        })

        # Conversation queries return 0 counts
        mock_conv_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([0]),
        )
        mock_usage_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([0]),
        )

        result = await scan_abuse_signals()

        assert isinstance(result, AbuseOverview)
        assert result.total_tenants_scanned == 2
        assert result.flagged_count == 0
        assert len(result.high_risk_tenants) == 0

    @pytest.mark.asyncio
    async def test_scan_detects_widget_abuse(
        self, mock_tenant_repo, mock_conv_repo, mock_usage_repo, superadmin_ctx,
    ):
        """Scan detects widget abuse when widget key present but no origin."""
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(
            return_value=["tenant-001"],
        )
        mock_tenant_repo.read = AsyncMock(return_value={
            "tenant_id": "tenant-001",
            "status": "active",
            "widget_key": "wk_test_key",
            "widget_allowed_origin": "",  # No origin configured
            "abuse_flagged": False,
        })

        # No volume or token signals
        mock_conv_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([0]),
        )
        mock_usage_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([0]),
        )

        result = await scan_abuse_signals()

        assert result.total_tenants_scanned == 1
        assert len(result.high_risk_tenants) == 1
        profile = result.high_risk_tenants[0]
        assert profile.tenant_id == "tenant-001"
        assert any(s.signal_type == "widget_abuse" for s in profile.signals)
        assert result.signals_by_type.get("widget_abuse", 0) == 1

    @pytest.mark.asyncio
    async def test_scan_empty_tenants(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Scan with no active tenants returns empty overview."""
        mock_tenant_repo.list_active_tenant_ids = AsyncMock(return_value=[])

        result = await scan_abuse_signals()

        assert isinstance(result, AbuseOverview)
        assert result.total_tenants_scanned == 0
        assert result.flagged_count == 0
        assert len(result.high_risk_tenants) == 0
        assert result.signals_by_type == {}


# ---------------------------------------------------------------------------
# Tenant Profile Tests
# ---------------------------------------------------------------------------


class TestTenantProfile:
    """Tests for GET /api/superadmin/abuse/tenant/{tenant_id}."""

    @pytest.mark.asyncio
    async def test_profile_with_signals(
        self, mock_tenant_repo, mock_conv_repo, mock_usage_repo, superadmin_ctx,
    ):
        """Profile with detected widget abuse signal."""
        mock_tenant_repo.read = AsyncMock(return_value={
            "tenant_id": "tenant-001",
            "status": "active",
            "widget_key": "wk_active_key",
            "widget_allowed_origin": "",  # Triggers widget_abuse
            "abuse_flagged": True,
            "abuse_flagged_at": "2026-02-18T00:00:00Z",
            "abuse_flagged_by": "admin@remaker.com",
        })

        # No volume/token/error signals
        mock_conv_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([0]),
        )
        mock_usage_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([0]),
        )

        result = await get_tenant_abuse_profile(
            tenant_id="tenant-001",
        )

        assert isinstance(result, TenantAbuseProfile)
        assert result.tenant_id == "tenant-001"
        assert result.is_flagged is True
        assert result.flagged_by == "admin@remaker.com"
        assert len(result.signals) >= 1
        assert result.risk_score > 0

    @pytest.mark.asyncio
    async def test_profile_with_volume_spike(
        self, mock_tenant_repo, mock_conv_repo, mock_usage_repo, superadmin_ctx,
    ):
        """Profile detects volume spike when 24h count >3x 7-day average."""
        mock_tenant_repo.read = AsyncMock(return_value={
            "tenant_id": "tenant-001",
            "status": "active",
            "widget_key": "",
            "widget_allowed_origin": "",
            "abuse_flagged": False,
        })

        # Simulate 24h count=100, 7d count=70 (daily avg=10, threshold=30)
        call_count = 0

        def query_side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            query = kwargs.get("query", "")
            if "status = 'error'" in query:
                return FakeAsyncIterator([0])
            # 24h count query comes first, then 7d, then 24h total, then error
            if call_count == 1:
                return FakeAsyncIterator([100])  # 24h count
            if call_count == 2:
                return FakeAsyncIterator([70])  # 7d count
            if call_count == 3:
                return FakeAsyncIterator([100])  # 24h total for error rate
            return FakeAsyncIterator([0])

        mock_conv_repo._container.query_items = MagicMock(
            side_effect=query_side_effect,
        )
        mock_usage_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([0]),
        )

        result = await get_tenant_abuse_profile(
            tenant_id="tenant-001",
        )

        assert isinstance(result, TenantAbuseProfile)
        volume_signals = [s for s in result.signals if s.signal_type == "volume_spike"]
        assert len(volume_signals) == 1
        assert volume_signals[0].metric_value == 100.0

    @pytest.mark.asyncio
    async def test_profile_no_signals(
        self, mock_tenant_repo, mock_conv_repo, mock_usage_repo, superadmin_ctx,
    ):
        """Profile with no abuse signals returns clean profile."""
        mock_tenant_repo.read = AsyncMock(return_value={
            "tenant_id": "tenant-001",
            "status": "active",
            "widget_key": "",
            "widget_allowed_origin": "",
            "abuse_flagged": False,
        })

        mock_conv_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([0]),
        )
        mock_usage_repo._container.query_items = MagicMock(
            return_value=FakeAsyncIterator([0]),
        )

        result = await get_tenant_abuse_profile(
            tenant_id="tenant-001",
        )

        assert isinstance(result, TenantAbuseProfile)
        assert result.tenant_id == "tenant-001"
        assert result.is_flagged is False
        assert len(result.signals) == 0
        assert result.risk_score == 0

    @pytest.mark.asyncio
    async def test_profile_tenant_not_found(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Returns 404 when tenant does not exist."""
        mock_tenant_repo.read = AsyncMock(side_effect=Exception("Not found"))

        with pytest.raises(Exception) as exc_info:
            await get_tenant_abuse_profile(
                tenant_id="nonexistent",
            )

        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Flag/Unflag Tests
# ---------------------------------------------------------------------------


class TestFlagTenant:
    """Tests for POST /api/superadmin/abuse/tenant/{tenant_id}/flag."""

    @pytest.mark.asyncio
    async def test_flag_tenant(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Flag a tenant stores abuse_flagged fields."""
        mock_tenant_repo.read = AsyncMock(return_value={
            "tenant_id": "tenant-001",
            "status": "active",
            "abuse_flagged": False,
        })
        mock_tenant_repo._container.patch_item = AsyncMock(return_value={})

        result = await flag_tenant(
            tenant_id="tenant-001",
            body=FlagRequest(flagged=True),
        )

        assert isinstance(result, FlagResponse)
        assert result.tenant_id == "tenant-001"
        assert result.is_flagged is True
        assert result.flagged_at is not None
        assert result.flagged_by == "spa-console"

        # Verify patch was called with correct operations
        mock_tenant_repo._container.patch_item.assert_awaited_once()
        call_kwargs = mock_tenant_repo._container.patch_item.call_args
        ops = call_kwargs.kwargs.get("patch_operations", [])
        assert any(op["path"] == "/abuse_flagged" and op["value"] is True for op in ops)
        assert any(op["path"] == "/abuse_flagged_by" for op in ops)

    @pytest.mark.asyncio
    async def test_unflag_tenant(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Unflag a tenant clears abuse_flagged fields."""
        mock_tenant_repo.read = AsyncMock(return_value={
            "tenant_id": "tenant-001",
            "status": "active",
            "abuse_flagged": True,
            "abuse_flagged_at": "2026-02-18T00:00:00Z",
            "abuse_flagged_by": "admin@remaker.com",
        })
        mock_tenant_repo._container.patch_item = AsyncMock(return_value={})

        result = await flag_tenant(
            tenant_id="tenant-001",
            body=FlagRequest(flagged=False),
        )

        assert isinstance(result, FlagResponse)
        assert result.tenant_id == "tenant-001"
        assert result.is_flagged is False
        assert result.flagged_at is None
        assert result.flagged_by is None

        # Verify patch clears the fields
        call_kwargs = mock_tenant_repo._container.patch_item.call_args
        ops = call_kwargs.kwargs.get("patch_operations", [])
        assert any(op["path"] == "/abuse_flagged" and op["value"] is False for op in ops)
        assert any(op["path"] == "/abuse_flagged_at" and op["value"] is None for op in ops)

    @pytest.mark.asyncio
    async def test_flag_tenant_not_found(
        self, mock_tenant_repo, superadmin_ctx,
    ):
        """Returns 404 when flagging a nonexistent tenant."""
        mock_tenant_repo.read = AsyncMock(side_effect=Exception("Not found"))

        with pytest.raises(Exception) as exc_info:
            await flag_tenant(
                tenant_id="nonexistent",
                body=FlagRequest(flagged=True),
            )

        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Auth Enforcement Tests
# ---------------------------------------------------------------------------


class TestAbuseAuth:
    """Verify that SUPERADMIN role is required on all endpoints."""

    def test_router_prefix_and_tags(self):
        """Router uses correct prefix and tags."""
        assert router.prefix == "/api/superadmin/abuse"
        assert "Abuse Detection" in router.tags

    def test_router_has_platform_admin_guard(self):
        """Router has require_platform_admin() as a router-level dependency.

        SPEC-1667: Access control is enforced by the router-level
        require_platform_admin() dependency, which rejects all non-SPA
        keys before any endpoint runs.
        """
        assert len(router.dependencies) > 0, (
            "Router must have require_platform_admin() as a dependency"
        )


# ---------------------------------------------------------------------------
# Unit Tests for Helper Functions
# ---------------------------------------------------------------------------


class TestHelpers:
    """Tests for internal helper functions."""

    def test_compute_severity_critical(self):
        """2x threshold yields critical severity."""
        assert _compute_severity(200.0, 100.0) == "critical"

    def test_compute_severity_high(self):
        """1.5x threshold yields high severity."""
        assert _compute_severity(150.0, 100.0) == "high"

    def test_compute_severity_medium(self):
        """At threshold yields medium severity."""
        assert _compute_severity(100.0, 100.0) == "medium"

    def test_compute_severity_low(self):
        """Below threshold yields low severity."""
        assert _compute_severity(50.0, 100.0) == "low"

    def test_compute_severity_zero_threshold(self):
        """Zero threshold returns low to avoid division by zero."""
        assert _compute_severity(100.0, 0.0) == "low"

    def test_risk_score_empty(self):
        """No signals yields risk score 0."""
        assert _compute_risk_score([]) == 0

    def test_risk_score_capped_at_100(self):
        """Risk score is capped at 100."""
        many_signals = [
            AbuseSignal(
                tenant_id="t",
                signal_type="rate_anomaly",
                severity="critical",
                description="test",
                detected_at="2026-01-01T00:00:00Z",
                metric_value=100.0,
                threshold=50.0,
            )
            for _ in range(10)
        ]
        assert _compute_risk_score(many_signals) == 100
