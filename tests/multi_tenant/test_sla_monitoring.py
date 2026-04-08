"""Comprehensive tests for SLAMonitoringService — WI #151.

Covers latency recording, percentile computation, uptime tracking,
SLA compliance checks, platform summary, health reporting, cleanup,
memory caps, and module singleton management.

Test IDs: SLA-01 through SLA-25.

Run:
    pytest tests/multi_tenant/test_sla_monitoring.py -v

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time


from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.sla_monitoring import (
    LATENCY_WINDOW_SECONDS,
    MAX_SAMPLES_PER_TENANT,
    SLA_TARGETS,
    PlatformSLASummary,
    SLAComplianceResult,
    SLAMonitoringService,
    configure_sla_monitor,
    get_sla_monitor,
)

# Re-import the private module-level variable indirectly through configure/get
import src.multi_tenant.sla_monitoring as _sla_mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TENANT_A = "t-sla-aaa"
_TENANT_B = "t-sla-bbb"


def _fresh_service() -> SLAMonitoringService:
    """Return a new SLAMonitoringService with no prior state."""
    return SLAMonitoringService()


# ===========================================================================
# Latency recording (SLA-01 through SLA-03)
# ===========================================================================


class TestLatencyRecording:
    """SLA-01 through SLA-03: Record and isolate latency samples."""

    def test_sla_01_record_latency_samples_and_verify_storage(self):
        """SLA-01: Record latency samples and verify they are stored."""
        svc = _fresh_service()

        svc.record_latency(_TENANT_A, 100.0)
        svc.record_latency(_TENANT_A, 200.0)
        svc.record_latency(_TENANT_A, 300.0)

        # Per-tenant samples exist
        assert _TENANT_A in svc._tenant_samples
        assert len(svc._tenant_samples[_TENANT_A]) == 3

        # Platform-wide samples also recorded
        assert len(svc._platform_samples) == 3

    def test_sla_02_platform_wide_latency_samples(self):
        """SLA-02: Record platform-wide latency samples from multiple tenants."""
        svc = _fresh_service()

        svc.record_latency(_TENANT_A, 100.0)
        svc.record_latency(_TENANT_B, 200.0)
        svc.record_latency(_TENANT_A, 300.0)

        # Platform aggregates all
        assert len(svc._platform_samples) == 3

        # Per-tenant separation
        assert len(svc._tenant_samples[_TENANT_A]) == 2
        assert len(svc._tenant_samples[_TENANT_B]) == 1

    def test_sla_03_per_tenant_latency_isolation(self):
        """SLA-03: Tenant A samples do not affect Tenant B percentiles."""
        svc = _fresh_service()

        # Tenant A: high latency
        for _ in range(20):
            svc.record_latency(_TENANT_A, 5000.0)

        # Tenant B: low latency
        for _ in range(20):
            svc.record_latency(_TENANT_B, 100.0)

        percentiles_a = svc.get_latency_percentiles(tenant_id=_TENANT_A)
        percentiles_b = svc.get_latency_percentiles(tenant_id=_TENANT_B)

        assert percentiles_a.p50_ms == 5000.0
        assert percentiles_b.p50_ms == 100.0
        assert percentiles_a.sample_count == 20
        assert percentiles_b.sample_count == 20


# ===========================================================================
# Percentile calculations (SLA-04 through SLA-08)
# ===========================================================================


class TestPercentileCalculations:
    """SLA-04 through SLA-08: Percentile accuracy and edge cases."""

    def test_sla_04_p50_percentile_accuracy(self):
        """SLA-04: P50 (median) calculation is accurate."""
        svc = _fresh_service()

        # 100 samples: 1..100
        for i in range(1, 101):
            svc.record_latency(_TENANT_A, float(i))

        p = svc.get_latency_percentiles(tenant_id=_TENANT_A)

        # Median of 1..100 should be ~50.5
        assert 49.0 <= p.p50_ms <= 52.0

    def test_sla_05_p95_percentile_accuracy(self):
        """SLA-05: P95 calculation is accurate."""
        svc = _fresh_service()

        for i in range(1, 101):
            svc.record_latency(_TENANT_A, float(i))

        p = svc.get_latency_percentiles(tenant_id=_TENANT_A)

        # P95 of 1..100 should be ~95.05
        assert 94.0 <= p.p95_ms <= 96.0

    def test_sla_06_p99_percentile_accuracy(self):
        """SLA-06: P99 calculation is accurate."""
        svc = _fresh_service()

        for i in range(1, 101):
            svc.record_latency(_TENANT_A, float(i))

        p = svc.get_latency_percentiles(tenant_id=_TENANT_A)

        # P99 of 1..100 should be ~99.01
        assert 98.0 <= p.p99_ms <= 100.0

    def test_sla_07_empty_samples_return_zeros(self):
        """SLA-07: Empty samples return 0.0 for all percentiles."""
        svc = _fresh_service()

        p = svc.get_latency_percentiles(tenant_id=_TENANT_A)

        assert p.p50_ms == 0.0
        assert p.p95_ms == 0.0
        assert p.p99_ms == 0.0
        assert p.sample_count == 0

        # Platform-wide also empty
        p_platform = svc.get_latency_percentiles()
        assert p_platform.p50_ms == 0.0
        assert p_platform.sample_count == 0

    def test_sla_08_window_filtering_excludes_old_samples(self):
        """SLA-08: Old samples outside the window are excluded."""
        svc = _fresh_service()

        # Simulate old timestamps by directly appending to the deque
        # with a timestamp far in the past
        old_ts = time.monotonic() - (LATENCY_WINDOW_SECONDS + 100)
        svc._tenant_samples[_TENANT_A] = __import__("collections").deque(
            maxlen=MAX_SAMPLES_PER_TENANT,
        )
        svc._tenant_samples[_TENANT_A].append((old_ts, 9999.0))
        svc._platform_samples.append((old_ts, 9999.0))

        # Record one recent sample
        svc.record_latency(_TENANT_A, 100.0)

        p = svc.get_latency_percentiles(tenant_id=_TENANT_A)

        # Only the recent sample should be in the window
        assert p.sample_count == 1
        assert p.p50_ms == 100.0


# ===========================================================================
# Health check / uptime (SLA-09 through SLA-13)
# ===========================================================================


class TestUptimeTracking:
    """SLA-09 through SLA-13: Health check recording and uptime calculation."""

    def test_sla_09_record_healthy_checks(self):
        """SLA-09: Record healthy health checks."""
        svc = _fresh_service()

        svc.record_health_check(True)
        svc.record_health_check(True)
        svc.record_health_check(True)

        assert len(svc._health_checks) == 3

    def test_sla_10_record_mixed_health_checks(self):
        """SLA-10: Record mixed healthy/unhealthy health checks."""
        svc = _fresh_service()

        svc.record_health_check(True)
        svc.record_health_check(False)
        svc.record_health_check(True)
        svc.record_health_check(False)

        assert len(svc._health_checks) == 4

    def test_sla_11_uptime_100_percent_all_healthy(self):
        """SLA-11: Uptime percentage is 100% when all checks pass."""
        svc = _fresh_service()

        for _ in range(50):
            svc.record_health_check(True)

        uptime = svc.get_uptime_pct()
        assert uptime == 100.0

    def test_sla_12_uptime_partial_failures(self):
        """SLA-12: Uptime percentage reflects partial failures."""
        svc = _fresh_service()

        # 80 healthy, 20 unhealthy = 80% uptime
        for _ in range(80):
            svc.record_health_check(True)
        for _ in range(20):
            svc.record_health_check(False)

        uptime = svc.get_uptime_pct()
        assert uptime == 80.0

    def test_sla_13_uptime_empty_checks_returns_100(self):
        """SLA-13: Uptime with no health checks returns 100%."""
        svc = _fresh_service()

        uptime = svc.get_uptime_pct()
        assert uptime == 100.0


# ===========================================================================
# SLA compliance checks (SLA-14 through SLA-17)
# ===========================================================================


class TestSLAComplianceCheck:
    """SLA-14 through SLA-17: SLA compliance evaluation per tier."""

    def test_sla_14_starter_tier_compliant(self):
        """SLA-14: Starter tier is compliant when all metrics are within targets."""
        svc = _fresh_service()

        # Record latencies under all SLA thresholds
        for _ in range(100):
            svc.record_latency(_TENANT_A, 500.0)  # Well under 1500ms P50
        for _ in range(50):
            svc.record_health_check(True)

        result = svc.check_sla_compliance(
            tier=TenantTier.STARTER.value,
            tenant_id=_TENANT_A,
        )

        assert isinstance(result, SLAComplianceResult)
        assert result.tier == TenantTier.STARTER.value
        assert result.overall_compliant is True
        assert result.p50_compliant is True
        assert result.p95_compliant is True
        assert result.p99_compliant is True
        assert result.uptime_compliant is True

    def test_sla_15_starter_non_compliant_p50_exceeded(self):
        """SLA-15: Starter tier is non-compliant when P50 exceeds 1500ms."""
        svc = _fresh_service()

        # Record latencies above P50 threshold (1500ms)
        # If more than half are above 1500, P50 will exceed
        for _ in range(100):
            svc.record_latency(_TENANT_A, 2000.0)

        for _ in range(50):
            svc.record_health_check(True)

        result = svc.check_sla_compliance(
            tier=TenantTier.STARTER.value,
            tenant_id=_TENANT_A,
        )

        assert result.overall_compliant is False
        assert result.p50_compliant is False
        # P50 should be 2000 which exceeds the 1500ms target
        assert result.latency.p50_ms > SLA_TARGETS[TenantTier.STARTER.value]["p50_ms"]

    def test_sla_16_enterprise_tier_targets(self):
        """SLA-16: Enterprise tier has stricter uptime but same latency targets."""
        svc = _fresh_service()

        for _ in range(100):
            svc.record_latency(_TENANT_A, 800.0)

        # 99.95% uptime requirement for Enterprise
        # 9999 healthy, 1 unhealthy => 99.99% > 99.95% => compliant
        for _ in range(9999):
            svc.record_health_check(True)
        svc.record_health_check(False)

        result = svc.check_sla_compliance(
            tier=TenantTier.ENTERPRISE.value,
            tenant_id=_TENANT_A,
        )

        assert result.tier == TenantTier.ENTERPRISE.value
        assert result.targets["uptime_pct"] == 99.95
        assert result.targets["rto_hours"] == 4
        assert result.overall_compliant is True

    def test_sla_17_compliance_with_no_samples_is_compliant(self):
        """SLA-17: SLA compliance with no latency samples defaults to compliant."""
        svc = _fresh_service()

        # No latency samples, but healthy uptime
        for _ in range(10):
            svc.record_health_check(True)

        result = svc.check_sla_compliance(
            tier=TenantTier.STARTER.value,
            tenant_id=_TENANT_A,
        )

        assert result.overall_compliant is True
        assert result.p50_compliant is True
        assert result.p95_compliant is True
        assert result.p99_compliant is True
        assert result.latency.sample_count == 0


# ===========================================================================
# Platform summary (SLA-18 through SLA-19)
# ===========================================================================


class TestPlatformSummary:
    """SLA-18 through SLA-19: Platform-wide SLA summary."""

    def test_sla_18_platform_summary_overall_compliant(self):
        """SLA-18: Platform summary reports overall compliant when all tiers pass."""
        svc = _fresh_service()

        # Record enough good data
        for _ in range(200):
            svc.record_latency(_TENANT_A, 400.0)
        for _ in range(100):
            svc.record_health_check(True)

        summary = svc.get_platform_summary()

        assert isinstance(summary, PlatformSLASummary)
        assert summary.total_requests == 200
        assert summary.total_health_checks == 100
        assert summary.healthy_checks == 100
        assert summary.uptime_pct == 100.0
        assert summary.overall_compliant is True

    def test_sla_19_platform_summary_includes_per_tier_breakdown(self):
        """SLA-19: Platform summary includes compliance results for all defined tiers."""
        svc = _fresh_service()

        # Record some data so results are non-trivial
        for _ in range(50):
            svc.record_latency(_TENANT_A, 500.0)
        for _ in range(20):
            svc.record_health_check(True)

        summary = svc.get_platform_summary()

        # All three tiers should be present in per_tier_compliance
        assert TenantTier.STARTER.value in summary.per_tier_compliance
        assert TenantTier.PROFESSIONAL.value in summary.per_tier_compliance
        assert TenantTier.ENTERPRISE.value in summary.per_tier_compliance

        for tier_name, compliance in summary.per_tier_compliance.items():
            assert isinstance(compliance, SLAComplianceResult)
            assert compliance.tier == tier_name


# ===========================================================================
# Health summary (SLA-20)
# ===========================================================================


class TestHealthSummary:
    """SLA-20: health_summary() for the /ready endpoint."""

    def test_sla_20_health_summary_returns_correct_structure(self):
        """SLA-20: health_summary() returns a dict with all expected keys."""
        svc = _fresh_service()

        svc.record_latency(_TENANT_A, 150.0)
        svc.record_latency(_TENANT_B, 250.0)
        svc.record_health_check(True)

        result = svc.health_summary()

        assert isinstance(result, dict)
        expected_keys = {
            "uptime_pct",
            "p50_ms",
            "p95_ms",
            "p99_ms",
            "sample_count",
            "tenants_tracked",
        }
        assert set(result.keys()) == expected_keys

        assert result["uptime_pct"] == 100.0
        assert result["sample_count"] == 2
        assert result["tenants_tracked"] == 2
        # Verify rounded values (numeric types)
        assert isinstance(result["p50_ms"], float)
        assert isinstance(result["p95_ms"], float)
        assert isinstance(result["p99_ms"], float)


# ===========================================================================
# Cleanup (SLA-21 through SLA-22)
# ===========================================================================


class TestCleanup:
    """SLA-21 through SLA-22: cleanup_old_samples behavior."""

    def test_sla_21_cleanup_removes_expired_data(self):
        """SLA-21: cleanup_old_samples removes samples older than max_age_seconds."""
        svc = _fresh_service()

        # Inject old samples manually
        old_ts = time.monotonic() - 10_000  # 10,000 seconds ago
        from collections import deque as _deque

        svc._tenant_samples[_TENANT_A] = _deque(maxlen=MAX_SAMPLES_PER_TENANT)
        svc._tenant_samples[_TENANT_A].append((old_ts, 500.0))
        svc._health_checks.append((old_ts, True))

        cleaned = svc.cleanup_old_samples(max_age_seconds=7200)

        # Tenant A's deque was emptied and removed
        assert cleaned == 1
        assert _TENANT_A not in svc._tenant_samples
        # Old health check should also be removed
        assert len(svc._health_checks) == 0

    def test_sla_22_cleanup_preserves_recent_data(self):
        """SLA-22: cleanup_old_samples preserves samples within max_age_seconds."""
        svc = _fresh_service()

        # Record recent samples via the normal API
        svc.record_latency(_TENANT_A, 100.0)
        svc.record_latency(_TENANT_A, 200.0)
        svc.record_health_check(True)

        cleaned = svc.cleanup_old_samples(max_age_seconds=7200)

        # Nothing should be cleaned
        assert cleaned == 0
        assert _TENANT_A in svc._tenant_samples
        assert len(svc._tenant_samples[_TENANT_A]) == 2
        assert len(svc._health_checks) == 1


# ===========================================================================
# Memory cap (SLA-23)
# ===========================================================================


class TestMemoryCap:
    """SLA-23: MAX_SAMPLES_PER_TENANT caps deque size."""

    def test_sla_23_max_samples_per_tenant_caps_memory(self):
        """SLA-23: Per-tenant deque does not exceed MAX_SAMPLES_PER_TENANT."""
        svc = _fresh_service()

        # Record more than MAX_SAMPLES_PER_TENANT samples
        for i in range(MAX_SAMPLES_PER_TENANT + 500):
            svc.record_latency(_TENANT_A, float(i))

        assert len(svc._tenant_samples[_TENANT_A]) == MAX_SAMPLES_PER_TENANT

        # The deque's maxlen enforces the cap
        assert svc._tenant_samples[_TENANT_A].maxlen == MAX_SAMPLES_PER_TENANT


# ===========================================================================
# Module singleton (SLA-24 through SLA-25)
# ===========================================================================


class TestModuleSingleton:
    """SLA-24 through SLA-25: Module-level singleton management."""

    def test_sla_24_get_sla_monitor_returns_same_instance(self):
        """SLA-24: get_sla_monitor() returns the same instance on repeated calls."""
        # Reset module state
        _sla_mod._sla_monitor = None

        first = get_sla_monitor()
        second = get_sla_monitor()

        assert first is second
        assert isinstance(first, SLAMonitoringService)

        # Clean up
        _sla_mod._sla_monitor = None

    def test_sla_25_configure_sla_monitor_replaces_singleton(self):
        """SLA-25: configure_sla_monitor() replaces the module singleton."""
        _sla_mod._sla_monitor = None

        original = get_sla_monitor()
        replacement = SLAMonitoringService()

        assert original is not replacement

        configure_sla_monitor(replacement)
        current = get_sla_monitor()

        assert current is replacement
        assert current is not original

        # Clean up
        _sla_mod._sla_monitor = None
