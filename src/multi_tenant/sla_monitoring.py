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
from dataclasses import dataclass
from datetime import datetime, timezone
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


@dataclass(frozen=True)
class ErrorBudget:
    """Error budget status for a tier over a billing period."""

    tier: str
    period_days: int
    allowed_downtime_minutes: float
    actual_downtime_minutes: float
    budget_remaining: float  # 0.0 to 1.0 (1.0 = full budget, 0.0 = exhausted)
    budget_consumed_pct: float  # 0.0 to 100.0
    is_within_budget: bool


@dataclass(frozen=True)
class SLATrendPoint:
    """A single point in an SLA trend time series."""

    timestamp: str
    uptime_pct: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    total_requests: int


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

    # -------------------------------------------------------------------
    # Snapshot persistence (C-2)
    # -------------------------------------------------------------------

    def create_snapshot_data(self) -> dict[str, Any]:
        """Capture current metrics as a snapshot dict.

        Returns a dict with platform-wide and per-tenant metrics
        suitable for persisting to Cosmos DB.
        """
        latency = self.get_latency_percentiles()
        uptime = self.get_uptime_pct()

        now = time.monotonic()
        cutoff = now - LATENCY_WINDOW_SECONDS
        all_checks = [(ts, ok) for ts, ok in self._health_checks if ts >= cutoff]
        healthy_count = sum(1 for _, ok in all_checks if ok)

        platform_metrics = {
            "total_requests": latency.sample_count,
            "p50_ms": round(latency.p50_ms, 1),
            "p95_ms": round(latency.p95_ms, 1),
            "p99_ms": round(latency.p99_ms, 1),
            "health_checks_total": len(all_checks),
            "health_checks_healthy": healthy_count,
            "uptime_pct": round(uptime, 3),
        }

        per_tenant: dict[str, dict[str, Any]] = {}
        for tenant_id, samples in self._tenant_samples.items():
            tenant_latencies = sorted(
                lat for ts, lat in samples if ts >= cutoff
            )
            if not tenant_latencies:
                continue
            per_tenant[tenant_id] = {
                "requests": len(tenant_latencies),
                "p50_ms": round(_percentile(tenant_latencies, 50), 1),
                "p95_ms": round(_percentile(tenant_latencies, 95), 1),
                "p99_ms": round(_percentile(tenant_latencies, 99), 1),
            }

        return {
            "platform": platform_metrics,
            "per_tenant": per_tenant,
        }

    # -------------------------------------------------------------------
    # Hydration from persisted snapshots (C-2)
    # -------------------------------------------------------------------

    def hydrate_from_snapshots(
        self,
        snapshots: list[dict[str, Any]],
    ) -> int:
        """Restore in-memory state from persisted hourly snapshots.

        Injects synthetic samples into the deques so that percentile
        calculations produce reasonable results immediately after
        a container restart.

        Each snapshot's platform and per-tenant request counts are
        used to create evenly-spaced synthetic latency samples within
        the snapshot's time window.

        Args:
            snapshots: List of hourly snapshot documents (newest first).

        Returns:
            Number of synthetic samples injected.
        """
        if not snapshots:
            return 0

        now = time.monotonic()
        now_utc = datetime.now(timezone.utc)
        injected = 0

        for snap in reversed(snapshots):  # Process oldest first
            ts_str = snap.get("timestamp", "")
            try:
                snap_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                continue

            # Compute the monotonic offset for this snapshot's time
            age_seconds = (now_utc - snap_time).total_seconds()
            if age_seconds < 0:
                continue  # Future snapshot — skip
            mono_base = now - age_seconds

            # Inject platform-wide synthetic samples
            platform = snap.get("platform", {})
            p_count = platform.get("total_requests", 0)
            p50 = platform.get("p50_ms", 0.0)
            if p_count > 0 and p50 > 0:
                # Use the median as a representative latency for synthetics
                for i in range(min(p_count, 100)):
                    offset = (i / max(p_count, 1)) * 3600
                    self._platform_samples.append((mono_base + offset, p50))
                    injected += 1

            # Inject health check synthetics
            hc_total = platform.get("health_checks_total", 0)
            hc_healthy = platform.get("health_checks_healthy", 0)
            for i in range(hc_total):
                offset = (i / max(hc_total, 1)) * 3600
                healthy = i < hc_healthy
                self._health_checks.append((mono_base + offset, healthy))

            # Inject per-tenant synthetic samples
            per_tenant = snap.get("per_tenant", {})
            for tenant_id, metrics in per_tenant.items():
                t_count = metrics.get("requests", 0)
                t_p50 = metrics.get("p50_ms", 0.0)
                if t_count > 0 and t_p50 > 0:
                    if tenant_id not in self._tenant_samples:
                        self._tenant_samples[tenant_id] = deque(
                            maxlen=MAX_SAMPLES_PER_TENANT,
                        )
                    for i in range(min(t_count, 100)):
                        offset = (i / max(t_count, 1)) * 3600
                        self._tenant_samples[tenant_id].append(
                            (mono_base + offset, t_p50),
                        )
                        injected += 1

        logger.info(
            "SLA hydration: injected %d synthetic samples from %d snapshots",
            injected, len(snapshots),
        )
        return injected

    # -------------------------------------------------------------------
    # Error budget calculation (C-2)
    # -------------------------------------------------------------------

    @staticmethod
    def compute_error_budget(
        tier: str,
        daily_snapshots: list[dict[str, Any]],
        period_days: int = 30,
    ) -> ErrorBudget:
        """Compute error budget from daily rollup snapshots.

        Error budget = 1.0 - (actual_downtime / allowed_downtime).
        A budget_remaining of 1.0 means no downtime consumed.
        A budget_remaining of 0.0 means the SLA has been fully exhausted.

        Args:
            tier: Tenant tier to evaluate against.
            daily_snapshots: List of daily rollup documents.
            period_days: Billing period length in days.

        Returns:
            ErrorBudget with remaining budget and consumption metrics.
        """
        targets = SLA_TARGETS.get(tier, SLA_TARGETS[TenantTier.STARTER.value])
        target_uptime = targets["uptime_pct"]

        # Allowed downtime = (1 - target_uptime/100) * period_days * 24 * 60 minutes
        allowed_downtime_min = (1.0 - target_uptime / 100.0) * period_days * 24 * 60

        # Compute actual downtime from daily snapshots
        total_downtime_min = 0.0
        for snap in daily_snapshots:
            platform = snap.get("platform", {})
            uptime_pct = platform.get("uptime_pct", 100.0)
            # Each daily snapshot covers 24 hours = 1440 minutes
            daily_downtime = (1.0 - uptime_pct / 100.0) * 1440
            total_downtime_min += daily_downtime

        if allowed_downtime_min > 0:
            budget_remaining = max(
                0.0,
                1.0 - (total_downtime_min / allowed_downtime_min),
            )
            budget_consumed = min(
                100.0,
                (total_downtime_min / allowed_downtime_min) * 100.0,
            )
        else:
            # 100% uptime target — any downtime exhausts budget
            budget_remaining = 0.0 if total_downtime_min > 0 else 1.0
            budget_consumed = 100.0 if total_downtime_min > 0 else 0.0

        return ErrorBudget(
            tier=tier,
            period_days=period_days,
            allowed_downtime_minutes=round(allowed_downtime_min, 2),
            actual_downtime_minutes=round(total_downtime_min, 2),
            budget_remaining=round(budget_remaining, 4),
            budget_consumed_pct=round(budget_consumed, 2),
            is_within_budget=budget_remaining > 0,
        )

    @staticmethod
    def build_trend_series(
        snapshots: list[dict[str, Any]],
    ) -> list[SLATrendPoint]:
        """Convert snapshot documents into a time-series of SLA trend points.

        Args:
            snapshots: Hourly or daily snapshot documents (any order).

        Returns:
            List of SLATrendPoint sorted by timestamp ascending.
        """
        points: list[SLATrendPoint] = []
        for snap in snapshots:
            platform = snap.get("platform", {})
            points.append(SLATrendPoint(
                timestamp=snap.get("timestamp", ""),
                uptime_pct=platform.get("uptime_pct", 100.0),
                p50_ms=platform.get("p50_ms", 0.0),
                p95_ms=platform.get("p95_ms", 0.0),
                p99_ms=platform.get("p99_ms", 0.0),
                total_requests=platform.get("total_requests", 0),
            ))
        points.sort(key=lambda p: p.timestamp)
        return points

    @staticmethod
    def compute_daily_rollup(
        hourly_snapshots: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Aggregate hourly snapshots into a daily rollup.

        Args:
            hourly_snapshots: List of hourly snapshot documents for one day.

        Returns:
            Dict with "platform" and "per_tenant" aggregated metrics.
        """
        if not hourly_snapshots:
            return {
                "platform": {
                    "total_requests": 0,
                    "avg_p50_ms": 0.0,
                    "avg_p95_ms": 0.0,
                    "avg_p99_ms": 0.0,
                    "uptime_pct": 100.0,
                    "hourly_snapshots": 0,
                },
                "per_tenant": {},
            }

        total_requests = 0
        p50_sum = 0.0
        p95_sum = 0.0
        p99_sum = 0.0
        uptime_sum = 0.0
        count = len(hourly_snapshots)

        # Per-tenant accumulator
        tenant_accum: dict[str, dict[str, float]] = {}

        for snap in hourly_snapshots:
            platform = snap.get("platform", {})
            total_requests += platform.get("total_requests", 0)
            p50_sum += platform.get("p50_ms", 0.0)
            p95_sum += platform.get("p95_ms", 0.0)
            p99_sum += platform.get("p99_ms", 0.0)
            uptime_sum += platform.get("uptime_pct", 100.0)

            for tid, metrics in snap.get("per_tenant", {}).items():
                if tid not in tenant_accum:
                    tenant_accum[tid] = {
                        "requests": 0, "p50_sum": 0.0,
                        "p95_sum": 0.0, "p99_sum": 0.0, "count": 0,
                    }
                tenant_accum[tid]["requests"] += metrics.get("requests", 0)
                tenant_accum[tid]["p50_sum"] += metrics.get("p50_ms", 0.0)
                tenant_accum[tid]["p95_sum"] += metrics.get("p95_ms", 0.0)
                tenant_accum[tid]["p99_sum"] += metrics.get("p99_ms", 0.0)
                tenant_accum[tid]["count"] += 1

        per_tenant: dict[str, dict[str, Any]] = {}
        for tid, acc in tenant_accum.items():
            tc = acc["count"] or 1
            per_tenant[tid] = {
                "requests": int(acc["requests"]),
                "avg_p50_ms": round(acc["p50_sum"] / tc, 1),
                "avg_p95_ms": round(acc["p95_sum"] / tc, 1),
                "avg_p99_ms": round(acc["p99_sum"] / tc, 1),
            }

        return {
            "platform": {
                "total_requests": total_requests,
                "avg_p50_ms": round(p50_sum / count, 1),
                "avg_p95_ms": round(p95_sum / count, 1),
                "avg_p99_ms": round(p99_sum / count, 1),
                "uptime_pct": round(uptime_sum / count, 3),
                "hourly_snapshots": count,
            },
            "per_tenant": per_tenant,
        }


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
