"""
SLA monitoring and compliance tracking service.

Implements WI #151: SLA monitoring dashboard — tracks P50/P95/P99 latency,
uptime, and per-tenant metrics against contractual SLA commitments.

SLA commitments (from Master Plan Review):
    - Uptime: Starter 99.5%, Professional 99.9%, Enterprise 99.95%
    - API latency: P50 < 1,500ms, P95 < 2,000ms, P99 < 5,000ms
    - Backup: 7-day PITR + 90-day warm archive + 7+ year cold archive
    - RTO: Enterprise 4hr, Professional 8hr, Starter 24hr

This service collects latency samples, computes percentile metrics,
tracks uptime via health-check results, and reports SLA compliance
status per tenant tier.

Should be queried by the /ready endpoint and the admin analytics API.

Architecture references:
    - Decision #24-27: SLA validation, metering, transparency
    - WI #79: SLA monitoring dashboard (Master Plan)
    - WI #151: SLA monitoring dashboard (Backlog — supersedes #79)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from src.multi_tenant.cosmos_schema import TenantTier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# SLA targets per tier
SLA_TARGETS: dict[str, dict[str, Any]] = {
    TenantTier.STARTER.value: {
        "uptime_pct": 99.5,
        "p50_ms": 1500,
        "p95_ms": 2000,
        "p99_ms": 5000,
        "rto_hours": 24,
    },
    TenantTier.PROFESSIONAL.value: {
        "uptime_pct": 99.9,
        "p50_ms": 1500,
        "p95_ms": 2000,
        "p99_ms": 5000,
        "rto_hours": 8,
    },
    TenantTier.ENTERPRISE.value: {
        "uptime_pct": 99.95,
        "p50_ms": 1500,
        "p95_ms": 2000,
        "p99_ms": 5000,
        "rto_hours": 4,
    },
}

# Default window for latency samples (1 hour of data)
LATENCY_WINDOW_SECONDS = 3600

# Max samples to retain per tenant (cap memory usage)
MAX_SAMPLES_PER_TENANT = 10_000

# Health check interval for uptime tracking (seconds)
HEALTH_CHECK_INTERVAL = 60


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LatencyPercentiles:
    """Computed latency percentiles for a measurement window."""

    p50_ms: float
    p95_ms: float
    p99_ms: float
    sample_count: int
    window_seconds: int


@dataclass(frozen=True)
class SLAComplianceResult:
    """SLA compliance status for a tenant or the platform."""

    tier: str
    uptime_pct: float
    latency: LatencyPercentiles
    uptime_compliant: bool
    p50_compliant: bool
    p95_compliant: bool
    p99_compliant: bool
    overall_compliant: bool
    targets: dict[str, Any]


@dataclass(frozen=True)
class PlatformSLASummary:
    """Aggregate SLA compliance across all tenants."""

    total_requests: int
    total_health_checks: int
    healthy_checks: int
    uptime_pct: float
    latency: LatencyPercentiles
    per_tier_compliance: dict[str, SLAComplianceResult]
    overall_compliant: bool


# ---------------------------------------------------------------------------
# SLAMonitoringService
# ---------------------------------------------------------------------------


class SLAMonitoringService:
    """Tracks latency, uptime, and SLA compliance metrics.

    Collects latency samples per tenant and platform-wide. Tracks
    uptime via periodic health check results. Computes percentile
    latencies and checks against tier-specific SLA targets.

    Thread-safe: uses deques for sample storage (atomic append).
    """

    def __init__(self) -> None:
        self._tenant_samples: dict[str, deque[tuple[float, float]]] = {}
        self._platform_samples: deque[tuple[float, float]] = deque(
            maxlen=MAX_SAMPLES_PER_TENANT * 10,
        )
        self._health_checks: deque[tuple[float, bool]] = deque(maxlen=100_000)
        self._start_time = time.monotonic()

    def record_latency(
        self,
        tenant_id: str,
        latency_ms: float,
    ) -> None:
        """Record a request latency sample.

        Args:
            tenant_id: The tenant that generated this request.
            latency_ms: End-to-end latency in milliseconds.
        """
        now = time.monotonic()
        sample = (now, latency_ms)

        # Platform-wide
        self._platform_samples.append(sample)

        # Per-tenant
        if tenant_id not in self._tenant_samples:
            self._tenant_samples[tenant_id] = deque(
                maxlen=MAX_SAMPLES_PER_TENANT,
            )
        self._tenant_samples[tenant_id].append(sample)

    def record_health_check(self, healthy: bool) -> None:
        """Record a health check result for uptime tracking.

        Args:
            healthy: Whether the health check passed.
        """
        self._health_checks.append((time.monotonic(), healthy))

    def get_latency_percentiles(
        self,
        tenant_id: str | None = None,
        window_seconds: int = LATENCY_WINDOW_SECONDS,
    ) -> LatencyPercentiles:
        """Compute latency percentiles for a tenant or platform-wide.

        Args:
            tenant_id: Specific tenant, or None for platform-wide.
            window_seconds: Look-back window in seconds.

        Returns:
            LatencyPercentiles with P50, P95, P99.
        """
        now = time.monotonic()
        cutoff = now - window_seconds

        if tenant_id:
            samples = self._tenant_samples.get(tenant_id, deque())
        else:
            samples = self._platform_samples

        # Filter to window
        latencies = sorted(
            lat for ts, lat in samples if ts >= cutoff
        )

        if not latencies:
            return LatencyPercentiles(
                p50_ms=0.0,
                p95_ms=0.0,
                p99_ms=0.0,
                sample_count=0,
                window_seconds=window_seconds,
            )

        return LatencyPercentiles(
            p50_ms=_percentile(latencies, 50),
            p95_ms=_percentile(latencies, 95),
            p99_ms=_percentile(latencies, 99),
            sample_count=len(latencies),
            window_seconds=window_seconds,
        )

    def get_uptime_pct(
        self,
        window_seconds: int = LATENCY_WINDOW_SECONDS,
    ) -> float:
        """Compute uptime percentage from health check results.

        Args:
            window_seconds: Look-back window in seconds.

        Returns:
            Uptime percentage (0.0-100.0). Returns 100.0 if no checks.
        """
        now = time.monotonic()
        cutoff = now - window_seconds

        checks = [(ts, ok) for ts, ok in self._health_checks if ts >= cutoff]
        if not checks:
            return 100.0

        healthy_count = sum(1 for _, ok in checks if ok)
        return (healthy_count / len(checks)) * 100.0

    def check_sla_compliance(
        self,
        tier: str,
        tenant_id: str | None = None,
        window_seconds: int = LATENCY_WINDOW_SECONDS,
    ) -> SLAComplianceResult:
        """Check SLA compliance for a tier.

        Args:
            tier: The tenant tier to check against.
            tenant_id: Specific tenant, or None for platform-wide.
            window_seconds: Look-back window.

        Returns:
            SLAComplianceResult with per-metric compliance flags.
        """
        targets = SLA_TARGETS.get(tier, SLA_TARGETS[TenantTier.STARTER.value])
        latency = self.get_latency_percentiles(tenant_id, window_seconds)
        uptime = self.get_uptime_pct(window_seconds)

        p50_ok = latency.p50_ms <= targets["p50_ms"] or latency.sample_count == 0
        p95_ok = latency.p95_ms <= targets["p95_ms"] or latency.sample_count == 0
        p99_ok = latency.p99_ms <= targets["p99_ms"] or latency.sample_count == 0
        uptime_ok = uptime >= targets["uptime_pct"]

        return SLAComplianceResult(
            tier=tier,
            uptime_pct=uptime,
            latency=latency,
            uptime_compliant=uptime_ok,
            p50_compliant=p50_ok,
            p95_compliant=p95_ok,
            p99_compliant=p99_ok,
            overall_compliant=all([p50_ok, p95_ok, p99_ok, uptime_ok]),
            targets=targets,
        )

    def get_platform_summary(
        self,
        window_seconds: int = LATENCY_WINDOW_SECONDS,
    ) -> PlatformSLASummary:
        """Get platform-wide SLA compliance summary.

        Returns compliance status broken down by tier.
        """
        now = time.monotonic()
        cutoff = now - window_seconds

        total_requests = sum(
            1 for ts, _ in self._platform_samples if ts >= cutoff
        )
        all_checks = [(ts, ok) for ts, ok in self._health_checks if ts >= cutoff]
        healthy_checks = sum(1 for _, ok in all_checks if ok)
        uptime = self.get_uptime_pct(window_seconds)
        latency = self.get_latency_percentiles(window_seconds=window_seconds)

        per_tier: dict[str, SLAComplianceResult] = {}
        for tier_name in SLA_TARGETS:
            per_tier[tier_name] = self.check_sla_compliance(
                tier=tier_name, window_seconds=window_seconds,
            )

        overall = all(r.overall_compliant for r in per_tier.values())

        return PlatformSLASummary(
            total_requests=total_requests,
            total_health_checks=len(all_checks),
            healthy_checks=healthy_checks,
            uptime_pct=uptime,
            latency=latency,
            per_tier_compliance=per_tier,
            overall_compliant=overall,
        )

    def health_summary(self) -> dict[str, Any]:
        """Return a dict suitable for the /ready endpoint."""
        latency = self.get_latency_percentiles()
        uptime = self.get_uptime_pct()
        return {
            "uptime_pct": round(uptime, 3),
            "p50_ms": round(latency.p50_ms, 1),
            "p95_ms": round(latency.p95_ms, 1),
            "p99_ms": round(latency.p99_ms, 1),
            "sample_count": latency.sample_count,
            "tenants_tracked": len(self._tenant_samples),
        }

    def cleanup_old_samples(self, max_age_seconds: int = 7200) -> int:
        """Remove samples older than max_age_seconds.

        Returns count of tenants cleaned up (empty sample queues removed).
        """
        now = time.monotonic()
        cutoff = now - max_age_seconds
        cleaned = 0

        # Clean per-tenant samples
        empty_tenants: list[str] = []
        for tid, samples in self._tenant_samples.items():
            while samples and samples[0][0] < cutoff:
                samples.popleft()
            if not samples:
                empty_tenants.append(tid)

        for tid in empty_tenants:
            del self._tenant_samples[tid]
            cleaned += 1

        # Clean health checks
        while self._health_checks and self._health_checks[0][0] < cutoff:
            self._health_checks.popleft()

        return cleaned


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _percentile(sorted_values: list[float], pct: int) -> float:
    """Compute the pth percentile from a sorted list of values."""
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * pct / 100.0
    f = int(k)
    c = f + 1
    if c >= len(sorted_values):
        return sorted_values[-1]
    return sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f])


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

_sla_monitor: SLAMonitoringService | None = None


def get_sla_monitor() -> SLAMonitoringService:
    """Get or create the module-level SLAMonitoringService singleton."""
    global _sla_monitor
    if _sla_monitor is None:
        _sla_monitor = SLAMonitoringService()
    return _sla_monitor


def configure_sla_monitor(service: SLAMonitoringService) -> None:
    """Wire a custom SLAMonitoringService at app startup."""
    global _sla_monitor
    _sla_monitor = service
