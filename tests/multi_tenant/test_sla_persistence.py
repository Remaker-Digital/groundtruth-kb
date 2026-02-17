"""Tests for C-2 SLA persistence — snapshots, hydration, error budget, trends.

Covers:
    - Snapshot data creation from in-memory metrics
    - Hydration from persisted snapshots
    - Error budget calculation
    - Daily rollup computation
    - Trend series building
    - SLA snapshot repository CRUD (mocked Cosmos)
    - SLA trends API endpoint
    - Background task registration

Test IDs: SLAP-01 through SLAP-30.

Run:
    pytest tests/multi_tenant/test_sla_persistence.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.sla_monitoring import (
    ErrorBudget,
    SLAMonitoringService,
    SLATrendPoint,
    SLA_TARGETS,
    LATENCY_WINDOW_SECONDS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TENANT_A = "t-slap-aaa"
_TENANT_B = "t-slap-bbb"


def _fresh_service() -> SLAMonitoringService:
    """Return a new SLAMonitoringService with no prior state."""
    return SLAMonitoringService()


def _seeded_service(
    platform_requests: int = 100,
    tenant_a_requests: int = 40,
    tenant_b_requests: int = 60,
) -> SLAMonitoringService:
    """Return a service pre-loaded with latency and health data."""
    svc = _fresh_service()
    for i in range(platform_requests):
        tid = _TENANT_A if i < tenant_a_requests else _TENANT_B
        svc.record_latency(tid, 200.0 + (i % 50) * 10)
    for i in range(60):
        svc.record_health_check(i < 58)  # 58/60 healthy = 96.67%
    return svc


def _make_hourly_snapshot(
    timestamp: str,
    total_requests: int = 500,
    p50_ms: float = 300.0,
    p95_ms: float = 1200.0,
    p99_ms: float = 2800.0,
    uptime_pct: float = 99.95,
    health_checks_total: int = 60,
    health_checks_healthy: int = 60,
    per_tenant: dict | None = None,
) -> dict:
    """Build an hourly snapshot document for testing."""
    return {
        "id": f"hourly-{timestamp}",
        "snapshot_type": "hourly",
        "timestamp": timestamp,
        "period_start": timestamp,
        "period_end": timestamp,
        "platform": {
            "total_requests": total_requests,
            "p50_ms": p50_ms,
            "p95_ms": p95_ms,
            "p99_ms": p99_ms,
            "health_checks_total": health_checks_total,
            "health_checks_healthy": health_checks_healthy,
            "uptime_pct": uptime_pct,
        },
        "per_tenant": per_tenant or {
            _TENANT_A: {"requests": 200, "p50_ms": 280.0, "p95_ms": 1100.0, "p99_ms": 2500.0},
            _TENANT_B: {"requests": 300, "p50_ms": 320.0, "p95_ms": 1300.0, "p99_ms": 3000.0},
        },
    }


def _make_daily_snapshot(
    date: str,
    total_requests: int = 12000,
    uptime_pct: float = 99.90,
) -> dict:
    """Build a daily rollup document for testing."""
    return {
        "id": f"daily-{date}",
        "snapshot_type": "daily",
        "timestamp": f"{date}T00:00:00Z",
        "date": date,
        "platform": {
            "total_requests": total_requests,
            "avg_p50_ms": 310.0,
            "avg_p95_ms": 1250.0,
            "avg_p99_ms": 2900.0,
            "uptime_pct": uptime_pct,
            "hourly_snapshots": 24,
        },
        "per_tenant": {},
    }


# ===========================================================================
# Snapshot creation (SLAP-01 through SLAP-05)
# ===========================================================================


class TestSnapshotCreation:
    """SLAP-01 through SLAP-05: Create snapshot data from in-memory metrics."""

    def test_slap_01_snapshot_includes_platform_metrics(self):
        svc = _seeded_service()
        data = svc.create_snapshot_data()
        platform = data["platform"]
        assert "total_requests" in platform
        assert "p50_ms" in platform
        assert "p95_ms" in platform
        assert "p99_ms" in platform
        assert "health_checks_total" in platform
        assert "health_checks_healthy" in platform
        assert "uptime_pct" in platform

    def test_slap_02_snapshot_includes_per_tenant_data(self):
        svc = _seeded_service()
        data = svc.create_snapshot_data()
        per_tenant = data["per_tenant"]
        assert _TENANT_A in per_tenant
        assert _TENANT_B in per_tenant
        assert per_tenant[_TENANT_A]["requests"] > 0
        assert per_tenant[_TENANT_B]["requests"] > 0

    def test_slap_03_snapshot_empty_service_returns_zero_metrics(self):
        svc = _fresh_service()
        data = svc.create_snapshot_data()
        assert data["platform"]["total_requests"] == 0
        assert data["per_tenant"] == {}

    def test_slap_04_snapshot_platform_request_count_matches_samples(self):
        svc = _seeded_service(platform_requests=50)
        data = svc.create_snapshot_data()
        assert data["platform"]["total_requests"] == 50

    def test_slap_05_snapshot_uptime_reflects_health_checks(self):
        svc = _seeded_service()
        data = svc.create_snapshot_data()
        # 58/60 healthy = 96.67%
        assert 96.0 <= data["platform"]["uptime_pct"] <= 97.0


# ===========================================================================
# Hydration (SLAP-06 through SLAP-12)
# ===========================================================================


class TestHydration:
    """SLAP-06 through SLAP-12: Restore state from persisted snapshots."""

    def test_slap_06_hydrate_empty_snapshots_returns_zero(self):
        svc = _fresh_service()
        injected = svc.hydrate_from_snapshots([])
        assert injected == 0

    def test_slap_07_hydrate_injects_platform_samples(self):
        svc = _fresh_service()
        now = datetime.now(timezone.utc)
        snap = _make_hourly_snapshot(
            timestamp=(now - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            total_requests=50,
        )
        injected = svc.hydrate_from_snapshots([snap])
        assert injected > 0
        assert len(svc._platform_samples) > 0

    def test_slap_08_hydrate_injects_tenant_samples(self):
        svc = _fresh_service()
        now = datetime.now(timezone.utc)
        snap = _make_hourly_snapshot(
            timestamp=(now - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        svc.hydrate_from_snapshots([snap])
        assert _TENANT_A in svc._tenant_samples
        assert _TENANT_B in svc._tenant_samples
        assert len(svc._tenant_samples[_TENANT_A]) > 0

    def test_slap_09_hydrate_injects_health_checks(self):
        svc = _fresh_service()
        now = datetime.now(timezone.utc)
        snap = _make_hourly_snapshot(
            timestamp=(now - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            health_checks_total=60,
            health_checks_healthy=58,
        )
        svc.hydrate_from_snapshots([snap])
        assert len(svc._health_checks) == 60

    def test_slap_10_hydrate_from_multiple_snapshots(self):
        svc = _fresh_service()
        now = datetime.now(timezone.utc)
        snaps = [
            _make_hourly_snapshot(
                timestamp=(now - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                total_requests=100,
            )
            for i in range(3)
        ]
        injected = svc.hydrate_from_snapshots(snaps)
        # 3 snapshots × (100 platform + 200+300 tenant) capped at 100 each
        assert injected > 0
        assert len(svc._platform_samples) > 100

    def test_slap_11_hydrate_skips_future_timestamps(self):
        svc = _fresh_service()
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        snap = _make_hourly_snapshot(
            timestamp=future.strftime("%Y-%m-%dT%H:%M:%SZ"),
            total_requests=50,
        )
        injected = svc.hydrate_from_snapshots([snap])
        assert injected == 0

    def test_slap_12_hydrate_produces_nonzero_percentiles(self):
        svc = _fresh_service()
        now = datetime.now(timezone.utc)
        snap = _make_hourly_snapshot(
            timestamp=(now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            total_requests=200,
            p50_ms=350.0,
        )
        svc.hydrate_from_snapshots([snap])
        latency = svc.get_latency_percentiles()
        # Should have nonzero percentiles from synthetic samples
        assert latency.sample_count > 0
        assert latency.p50_ms > 0


# ===========================================================================
# Error budget calculation (SLAP-13 through SLAP-19)
# ===========================================================================


class TestErrorBudget:
    """SLAP-13 through SLAP-19: Error budget computation from daily snapshots."""

    def test_slap_13_full_uptime_gives_full_budget(self):
        dailies = [
            _make_daily_snapshot(f"2026-02-{d:02d}", uptime_pct=100.0)
            for d in range(1, 31)
        ]
        eb = SLAMonitoringService.compute_error_budget(
            tier=TenantTier.STARTER.value,
            daily_snapshots=dailies,
            period_days=30,
        )
        assert eb.budget_remaining == 1.0
        assert eb.actual_downtime_minutes == 0.0
        assert eb.is_within_budget is True

    def test_slap_14_some_downtime_consumes_budget(self):
        dailies = [
            _make_daily_snapshot(f"2026-02-{d:02d}", uptime_pct=99.0)
            for d in range(1, 31)
        ]
        eb = SLAMonitoringService.compute_error_budget(
            tier=TenantTier.STARTER.value,  # 99.5% target
            daily_snapshots=dailies,
            period_days=30,
        )
        assert eb.actual_downtime_minutes > 0
        # 99.0% uptime vs 99.5% target → budget exhausted
        assert eb.budget_remaining == 0.0
        assert eb.is_within_budget is False

    def test_slap_15_enterprise_tighter_budget(self):
        # Enterprise requires 99.95% — 99.9% should consume significant budget
        dailies = [
            _make_daily_snapshot(f"2026-02-{d:02d}", uptime_pct=99.9)
            for d in range(1, 31)
        ]
        eb_enterprise = SLAMonitoringService.compute_error_budget(
            tier=TenantTier.ENTERPRISE.value,
            daily_snapshots=dailies,
            period_days=30,
        )
        eb_starter = SLAMonitoringService.compute_error_budget(
            tier=TenantTier.STARTER.value,
            daily_snapshots=dailies,
            period_days=30,
        )
        # Enterprise should consume more budget than starter
        assert eb_enterprise.budget_consumed_pct > eb_starter.budget_consumed_pct

    def test_slap_16_empty_snapshots_full_budget(self):
        eb = SLAMonitoringService.compute_error_budget(
            tier=TenantTier.PROFESSIONAL.value,
            daily_snapshots=[],
            period_days=30,
        )
        assert eb.budget_remaining == 1.0
        assert eb.actual_downtime_minutes == 0.0

    def test_slap_17_allowed_downtime_scales_with_period(self):
        dailies = [_make_daily_snapshot("2026-02-01", uptime_pct=99.0)]
        eb_30 = SLAMonitoringService.compute_error_budget(
            tier=TenantTier.STARTER.value,
            daily_snapshots=dailies,
            period_days=30,
        )
        eb_7 = SLAMonitoringService.compute_error_budget(
            tier=TenantTier.STARTER.value,
            daily_snapshots=dailies,
            period_days=7,
        )
        assert eb_30.allowed_downtime_minutes > eb_7.allowed_downtime_minutes

    def test_slap_18_returns_correct_dataclass(self):
        eb = SLAMonitoringService.compute_error_budget(
            tier=TenantTier.STARTER.value,
            daily_snapshots=[],
            period_days=30,
        )
        assert isinstance(eb, ErrorBudget)
        assert eb.tier == TenantTier.STARTER.value
        assert eb.period_days == 30

    def test_slap_19_budget_remaining_between_zero_and_one(self):
        dailies = [
            _make_daily_snapshot(f"2026-02-{d:02d}", uptime_pct=99.4)
            for d in range(1, 31)
        ]
        eb = SLAMonitoringService.compute_error_budget(
            tier=TenantTier.STARTER.value,  # 99.5% target
            daily_snapshots=dailies,
            period_days=30,
        )
        assert 0.0 <= eb.budget_remaining <= 1.0
        assert 0.0 <= eb.budget_consumed_pct <= 100.0


# ===========================================================================
# Daily rollup (SLAP-20 through SLAP-23)
# ===========================================================================


class TestDailyRollup:
    """SLAP-20 through SLAP-23: Daily rollup computation from hourly snapshots."""

    def test_slap_20_empty_hourlies_returns_zero_rollup(self):
        rollup = SLAMonitoringService.compute_daily_rollup([])
        assert rollup["platform"]["total_requests"] == 0
        assert rollup["platform"]["hourly_snapshots"] == 0

    def test_slap_21_single_hourly_rollup(self):
        snap = _make_hourly_snapshot("2026-02-17T14:00:00Z", total_requests=500)
        rollup = SLAMonitoringService.compute_daily_rollup([snap])
        assert rollup["platform"]["total_requests"] == 500
        assert rollup["platform"]["hourly_snapshots"] == 1
        assert rollup["platform"]["avg_p50_ms"] == 300.0

    def test_slap_22_multiple_hourlies_averaged(self):
        snaps = [
            _make_hourly_snapshot(
                f"2026-02-17T{h:02d}:00:00Z",
                total_requests=100,
                p50_ms=200.0 + h * 10,
                uptime_pct=100.0 if h < 23 else 95.0,
            )
            for h in range(24)
        ]
        rollup = SLAMonitoringService.compute_daily_rollup(snaps)
        assert rollup["platform"]["total_requests"] == 2400
        assert rollup["platform"]["hourly_snapshots"] == 24
        # Average uptime: (23*100 + 95) / 24 ≈ 99.79
        assert 99.7 < rollup["platform"]["uptime_pct"] < 99.9

    def test_slap_23_rollup_aggregates_per_tenant(self):
        snaps = [
            _make_hourly_snapshot(
                f"2026-02-17T{h:02d}:00:00Z",
                per_tenant={
                    _TENANT_A: {"requests": 50, "p50_ms": 200.0, "p95_ms": 900.0, "p99_ms": 2000.0},
                },
            )
            for h in range(3)
        ]
        rollup = SLAMonitoringService.compute_daily_rollup(snaps)
        assert _TENANT_A in rollup["per_tenant"]
        assert rollup["per_tenant"][_TENANT_A]["requests"] == 150


# ===========================================================================
# Trend series (SLAP-24 through SLAP-25)
# ===========================================================================


class TestTrendSeries:
    """SLAP-24 through SLAP-25: Trend time-series from snapshots."""

    def test_slap_24_build_trend_series_sorted(self):
        snaps = [
            _make_hourly_snapshot("2026-02-17T14:00:00Z"),
            _make_hourly_snapshot("2026-02-17T12:00:00Z"),
            _make_hourly_snapshot("2026-02-17T16:00:00Z"),
        ]
        series = SLAMonitoringService.build_trend_series(snaps)
        assert len(series) == 3
        assert series[0].timestamp < series[1].timestamp < series[2].timestamp

    def test_slap_25_trend_points_have_correct_fields(self):
        snaps = [_make_hourly_snapshot("2026-02-17T10:00:00Z", total_requests=999)]
        series = SLAMonitoringService.build_trend_series(snaps)
        assert len(series) == 1
        point = series[0]
        assert isinstance(point, SLATrendPoint)
        assert point.total_requests == 999
        assert point.uptime_pct == 99.95


# ===========================================================================
# Repository (SLAP-26 through SLAP-28 — mocked Cosmos)
# ===========================================================================


class FakeAsyncIterator:
    """Helper to simulate Cosmos DB async iteration."""

    def __init__(self, items: list):
        self._items = items
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._index]
        self._index += 1
        return item


class TestSLASnapshotRepository:
    """SLAP-26 through SLAP-28: Repository CRUD operations."""

    @pytest.mark.asyncio
    async def test_slap_26_save_hourly_snapshot(self):
        with patch("src.multi_tenant.repositories.sla_snapshots.get_cosmos_manager") as mock_mgr:
            mock_container = MagicMock()
            mock_container.upsert_item = AsyncMock(return_value={"id": "hourly-test"})
            mock_mgr.return_value.get_container.return_value = mock_container

            from src.multi_tenant.repositories.sla_snapshots import SLASnapshotRepository
            repo = SLASnapshotRepository()

            now = datetime.now(timezone.utc)
            result = await repo.save_hourly_snapshot(
                timestamp=now,
                period_start=now,
                period_end=now,
                platform_metrics={"total_requests": 100},
                per_tenant={},
            )
            assert result["id"] == "hourly-test"
            mock_container.upsert_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_slap_27_save_daily_rollup(self):
        with patch("src.multi_tenant.repositories.sla_snapshots.get_cosmos_manager") as mock_mgr:
            mock_container = MagicMock()
            mock_container.upsert_item = AsyncMock(return_value={"id": "daily-2026-02-17"})
            mock_mgr.return_value.get_container.return_value = mock_container

            from src.multi_tenant.repositories.sla_snapshots import SLASnapshotRepository
            repo = SLASnapshotRepository()

            result = await repo.save_daily_rollup(
                date="2026-02-17",
                platform_metrics={"total_requests": 12000},
                per_tenant={},
            )
            assert result["id"] == "daily-2026-02-17"

    @pytest.mark.asyncio
    async def test_slap_28_get_recent_hourly(self):
        snaps = [
            _make_hourly_snapshot(f"2026-02-17T{h:02d}:00:00Z")
            for h in range(5)
        ]
        with patch("src.multi_tenant.repositories.sla_snapshots.get_cosmos_manager") as mock_mgr:
            mock_container = MagicMock()
            mock_container.query_items.return_value = FakeAsyncIterator(snaps)
            mock_mgr.return_value.get_container.return_value = mock_container

            from src.multi_tenant.repositories.sla_snapshots import SLASnapshotRepository
            repo = SLASnapshotRepository()

            result = await repo.get_recent_hourly(hours=5)
            assert len(result) == 5


# ===========================================================================
# Trends API endpoint (SLAP-29 through SLAP-30)
# ===========================================================================


class TestSLATrendsEndpoint:
    """SLAP-29 through SLAP-30: SLA trends API endpoint."""

    @pytest.mark.asyncio
    async def test_slap_29_trends_endpoint_returns_response(self):
        snaps = [
            _make_hourly_snapshot(f"2026-02-17T{h:02d}:00:00Z")
            for h in range(24)
        ]
        dailies = [
            _make_daily_snapshot(f"2026-02-{d:02d}")
            for d in range(1, 8)
        ]

        mock_repo = MagicMock()
        mock_repo.get_recent_hourly = AsyncMock(return_value=snaps)
        mock_repo.get_recent_daily = AsyncMock(return_value=dailies)

        from src.multi_tenant.superadmin_api import sla_trends, SLATrendsResponse

        # The endpoint does a lazy import: from ...sla_snapshots import SLASnapshotRepository
        # then calls SLASnapshotRepository(). We patch the class at the source module.
        with patch(
            "src.multi_tenant.repositories.sla_snapshots.SLASnapshotRepository",
            return_value=mock_repo,
        ):
            ctx = MagicMock()
            result = await sla_trends(_ctx=ctx, range_days=1, period_days=30)
            assert isinstance(result, SLATrendsResponse)
            assert result.range_days == 1
            assert len(result.trend_points) == 24
            assert len(result.error_budgets) == 3  # 3 tiers

    @pytest.mark.asyncio
    async def test_slap_30_trends_endpoint_503_on_failure(self):
        from src.multi_tenant.superadmin_api import sla_trends
        from fastapi import HTTPException

        # Patch the import to raise an exception
        with patch(
            "src.multi_tenant.repositories.sla_snapshots.get_cosmos_manager",
            side_effect=RuntimeError("Cosmos unavailable"),
        ):
            ctx = MagicMock()
            with pytest.raises(HTTPException) as exc_info:
                await sla_trends(_ctx=ctx, range_days=7, period_days=30)
            assert exc_info.value.status_code == 503
