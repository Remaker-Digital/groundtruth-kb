"""TenantUsageMonitor — progressive throttling for noisy neighbor prevention (WI #51).

Monitors per-tenant resource consumption in a rolling window and applies
progressive escalation when a tenant exceeds their fair share:

    Watch → Warn → Throttle → Isolate

This complements:
    - RateLimitMiddleware (WI #28): per-tenant request rate limits
    - TenantConcurrencyMiddleware (WI #44): per-tenant active request limits
    - ConversationMeter (WI #72): billable conversation tracking

The monitor tracks these per-tenant metrics in a 5-minute rolling window:
    - Request count and error count
    - Total latency (ms) contributed across all requests
    - Estimated AI token consumption (prompt + completion)
    - Estimated Cosmos DB RU consumption

Escalation levels:
    NORMAL  — no action, tenant is within thresholds
    WATCH   — metrics elevated, logging increased, no throttling
    WARN    — alert logged, dashboard notification queued
    THROTTLE — rate limit reduced to 50% of tier allowance
    ISOLATE — rate limit reduced to 10% of tier allowance (extreme)

Architecture references:
    - Decision #17: TenantUsageMonitor — progressive throttling
    - TIER_DEFAULTS: per-tier rate and concurrency limits
    - pipeline_resilience.py: concurrency + circuit breakers (complementary)
    - conversation_meter.py: billable conversation tracking (complementary)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Rolling window duration (seconds)
WINDOW_SECONDS = 300  # 5 minutes

# Evaluation interval — how often to recalculate escalation level (seconds)
EVALUATION_INTERVAL_SECONDS = 30

# Escalation thresholds — multipliers of the tier's rate_limit_rpm.
# If a tenant's 5-min request count exceeds rate_limit_rpm * WINDOW_MINUTES * multiplier,
# they escalate to the next level.
WINDOW_MINUTES = WINDOW_SECONDS / 60  # 5

WARN_MULTIPLIER = 0.8      # 80% of theoretical 5-min capacity
THROTTLE_MULTIPLIER = 1.0  # 100% of theoretical 5-min capacity
ISOLATE_MULTIPLIER = 2.0   # 200% — sustained abuse

# Error rate thresholds (errors / total requests in window)
WARN_ERROR_RATE = 0.10      # 10% errors → watch/warn
THROTTLE_ERROR_RATE = 0.25  # 25% errors → throttle

# Latency spike threshold — if average request latency in window exceeds
# this many ms, it may indicate the tenant is causing pipeline congestion.
LATENCY_WARN_MS = 3000      # 3 seconds average
LATENCY_THROTTLE_MS = 5000  # 5 seconds average

# Throttle/isolate rate limit reduction factors
THROTTLE_RATE_FACTOR = 0.50  # Reduce to 50% of tier RPM
ISOLATE_RATE_FACTOR = 0.10   # Reduce to 10% of tier RPM


# ---------------------------------------------------------------------------
# Escalation levels
# ---------------------------------------------------------------------------


class EscalationLevel(str, Enum):
    """Progressive escalation levels for noisy tenant detection."""

    NORMAL = "normal"
    WATCH = "watch"
    WARN = "warn"
    THROTTLE = "throttle"
    ISOLATE = "isolate"


# Severity ordering for comparison
_LEVEL_ORDER = {
    EscalationLevel.NORMAL: 0,
    EscalationLevel.WATCH: 1,
    EscalationLevel.WARN: 2,
    EscalationLevel.THROTTLE: 3,
    EscalationLevel.ISOLATE: 4,
}


# ---------------------------------------------------------------------------
# Per-tenant usage snapshot
# ---------------------------------------------------------------------------


@dataclass
class TenantUsageSnapshot:
    """Aggregated usage metrics for a tenant within the rolling window."""

    tenant_id: str
    tier: str = "starter"
    window_seconds: float = WINDOW_SECONDS

    # Counters within the window
    request_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    estimated_ai_tokens: int = 0
    estimated_cosmos_rus: float = 0.0

    # Computed
    escalation_level: EscalationLevel = EscalationLevel.NORMAL
    effective_rate_limit_rpm: int | None = None
    reasons: list[str] = field(default_factory=list)

    @property
    def avg_latency_ms(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.total_latency_ms / self.request_count

    @property
    def error_rate(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count


# ---------------------------------------------------------------------------
# Usage event — lightweight record appended per request
# ---------------------------------------------------------------------------


@dataclass
class UsageEvent:
    """A single request's resource consumption."""

    timestamp: float  # time.monotonic()
    latency_ms: float = 0.0
    is_error: bool = False
    ai_tokens: int = 0
    cosmos_rus: float = 0.0


# ---------------------------------------------------------------------------
# TenantUsageMonitor
# ---------------------------------------------------------------------------


class TenantUsageMonitor:
    """Monitors per-tenant resource consumption and applies progressive throttling.

    Usage:
        monitor = TenantUsageMonitor()

        # Record a request's resource usage
        monitor.record_event(
            tenant_id="abc123",
            tier="professional",
            latency_ms=1200,
            is_error=False,
            ai_tokens=850,
            cosmos_rus=4.2,
        )

        # Evaluate current escalation level
        snapshot = monitor.evaluate(tenant_id="abc123", tier="professional")
        if snapshot.escalation_level == EscalationLevel.THROTTLE:
            # Apply reduced rate limit
            effective_rpm = snapshot.effective_rate_limit_rpm

        # Get all tenant statuses for dashboard
        all_statuses = monitor.get_all_statuses()
    """

    def __init__(
        self,
        window_seconds: float = WINDOW_SECONDS,
        evaluation_interval: float = EVALUATION_INTERVAL_SECONDS,
    ) -> None:
        self._window_seconds = window_seconds
        self._evaluation_interval = evaluation_interval

        # {tenant_id: [UsageEvent, ...]}
        self._events: dict[str, list[UsageEvent]] = defaultdict(list)

        # {tenant_id: TenantUsageSnapshot} — last evaluated snapshot
        self._snapshots: dict[str, TenantUsageSnapshot] = {}

        # {tenant_id: float} — last evaluation time (monotonic)
        self._last_evaluated: dict[str, float] = {}

        # {tenant_id: EscalationLevel} — sticky escalation (doesn't drop instantly)
        self._current_levels: dict[str, EscalationLevel] = {}

    def record_event(
        self,
        tenant_id: str,
        tier: str = "starter",
        latency_ms: float = 0.0,
        is_error: bool = False,
        ai_tokens: int = 0,
        cosmos_rus: float = 0.0,
    ) -> None:
        """Record a single request's resource consumption.

        Called after each request completes (or fails). Lightweight —
        just appends to the event list. Evaluation happens lazily on
        the next evaluate() call or when enough time has passed.
        """
        event = UsageEvent(
            timestamp=time.monotonic(),
            latency_ms=latency_ms,
            is_error=is_error,
            ai_tokens=ai_tokens,
            cosmos_rus=cosmos_rus,
        )
        self._events[tenant_id].append(event)

    def evaluate(
        self,
        tenant_id: str,
        tier: str = "starter",
    ) -> TenantUsageSnapshot:
        """Evaluate the current escalation level for a tenant.

        Prunes old events, aggregates the rolling window, compares
        against tier thresholds, and returns the snapshot with the
        computed escalation level.
        """
        now = time.monotonic()

        # Check if we recently evaluated (debounce)
        last = self._last_evaluated.get(tenant_id, 0)
        if now - last < self._evaluation_interval and tenant_id in self._snapshots:
            return self._snapshots[tenant_id]

        # Prune old events
        cutoff = now - self._window_seconds
        events = self._events.get(tenant_id, [])
        events = [e for e in events if e.timestamp > cutoff]
        self._events[tenant_id] = events

        # Aggregate
        request_count = len(events)
        error_count = sum(1 for e in events if e.is_error)
        total_latency = sum(e.latency_ms for e in events)
        total_tokens = sum(e.ai_tokens for e in events)
        total_rus = sum(e.cosmos_rus for e in events)

        # Determine tier thresholds
        tier_config = TIER_DEFAULTS.get(tier, TIER_DEFAULTS.get("starter", {}))
        base_rpm = tier_config.get("rate_limit_rpm", 10)

        # Theoretical max requests in the window
        window_capacity = base_rpm * WINDOW_MINUTES

        # Compute escalation
        level = EscalationLevel.NORMAL
        reasons: list[str] = []

        # Request volume check
        if request_count >= window_capacity * ISOLATE_MULTIPLIER:
            level = EscalationLevel.ISOLATE
            reasons.append(
                f"request_volume={request_count} >= {window_capacity * ISOLATE_MULTIPLIER:.0f} "
                f"(isolate threshold)"
            )
        elif request_count >= window_capacity * THROTTLE_MULTIPLIER:
            level = EscalationLevel.THROTTLE
            reasons.append(
                f"request_volume={request_count} >= {window_capacity * THROTTLE_MULTIPLIER:.0f} "
                f"(throttle threshold)"
            )
        elif request_count >= window_capacity * WARN_MULTIPLIER:
            level = EscalationLevel.WARN
            reasons.append(
                f"request_volume={request_count} >= {window_capacity * WARN_MULTIPLIER:.0f} "
                f"(warn threshold)"
            )

        # Error rate check (can escalate further)
        error_rate = error_count / request_count if request_count > 0 else 0.0
        if error_rate >= THROTTLE_ERROR_RATE:
            candidate = EscalationLevel.THROTTLE
            if _LEVEL_ORDER[candidate] > _LEVEL_ORDER[level]:
                level = candidate
            reasons.append(f"error_rate={error_rate:.1%} >= {THROTTLE_ERROR_RATE:.0%}")
        elif error_rate >= WARN_ERROR_RATE:
            candidate = EscalationLevel.WARN
            if _LEVEL_ORDER[candidate] > _LEVEL_ORDER[level]:
                level = candidate
            reasons.append(f"error_rate={error_rate:.1%} >= {WARN_ERROR_RATE:.0%}")

        # Latency check (can escalate further)
        avg_latency = total_latency / request_count if request_count > 0 else 0.0
        if avg_latency >= LATENCY_THROTTLE_MS:
            candidate = EscalationLevel.THROTTLE
            if _LEVEL_ORDER[candidate] > _LEVEL_ORDER[level]:
                level = candidate
            reasons.append(
                f"avg_latency={avg_latency:.0f}ms >= {LATENCY_THROTTLE_MS}ms"
            )
        elif avg_latency >= LATENCY_WARN_MS:
            candidate = EscalationLevel.WARN
            if _LEVEL_ORDER[candidate] > _LEVEL_ORDER[level]:
                level = candidate
            reasons.append(
                f"avg_latency={avg_latency:.0f}ms >= {LATENCY_WARN_MS}ms"
            )

        # Apply sticky escalation — don't drop more than one level at a time
        previous_level = self._current_levels.get(tenant_id, EscalationLevel.NORMAL)
        if _LEVEL_ORDER[level] < _LEVEL_ORDER[previous_level]:
            # De-escalate by at most one step
            prev_order = _LEVEL_ORDER[previous_level]
            new_order = max(_LEVEL_ORDER[level], prev_order - 1)
            for lvl, order in _LEVEL_ORDER.items():
                if order == new_order:
                    level = lvl
                    break

        self._current_levels[tenant_id] = level

        # Compute effective rate limit
        effective_rpm: int | None = None
        if level == EscalationLevel.THROTTLE:
            effective_rpm = max(1, int(base_rpm * THROTTLE_RATE_FACTOR))
        elif level == EscalationLevel.ISOLATE:
            effective_rpm = max(1, int(base_rpm * ISOLATE_RATE_FACTOR))

        # If the level was WATCH but no reasons triggered it, set to NORMAL
        if level == EscalationLevel.NORMAL and not reasons:
            pass  # Already NORMAL

        # Build snapshot
        snapshot = TenantUsageSnapshot(
            tenant_id=tenant_id,
            tier=tier,
            window_seconds=self._window_seconds,
            request_count=request_count,
            error_count=error_count,
            total_latency_ms=total_latency,
            estimated_ai_tokens=total_tokens,
            estimated_cosmos_rus=total_rus,
            escalation_level=level,
            effective_rate_limit_rpm=effective_rpm,
            reasons=reasons,
        )

        self._snapshots[tenant_id] = snapshot
        self._last_evaluated[tenant_id] = now

        # Log escalation changes
        if level != previous_level:
            log_fn = logger.info if _LEVEL_ORDER[level] <= 1 else logger.warning
            log_fn(
                "Tenant usage escalation: tenant=%s %s → %s reasons=%s",
                tenant_id[:8] if len(tenant_id) > 8 else tenant_id,
                previous_level.value,
                level.value,
                reasons,
            )

        return snapshot

    def get_effective_rate_limit(
        self,
        tenant_id: str,
        tier: str = "starter",
    ) -> int | None:
        """Get the effective rate limit for a tenant.

        Returns None if no throttling is active (use tier default).
        Returns a reduced RPM value if the tenant is being throttled.

        This method is designed to be called by RateLimitMiddleware to
        override the tier default when a tenant is escalated.
        """
        snapshot = self._snapshots.get(tenant_id)
        if snapshot is None:
            return None

        # Re-evaluate if stale
        now = time.monotonic()
        last = self._last_evaluated.get(tenant_id, 0)
        if now - last >= self._evaluation_interval:
            snapshot = self.evaluate(tenant_id, tier)

        return snapshot.effective_rate_limit_rpm

    def get_tenant_status(self, tenant_id: str) -> dict[str, Any]:
        """Get the current monitoring status for a tenant.

        Returns a dict suitable for dashboard display or API response.
        """
        snapshot = self._snapshots.get(tenant_id)
        if snapshot is None:
            return {
                "tenant_id": tenant_id,
                "escalation_level": EscalationLevel.NORMAL.value,
                "request_count": 0,
                "error_count": 0,
                "error_rate": 0.0,
                "avg_latency_ms": 0.0,
                "effective_rate_limit_rpm": None,
                "reasons": [],
            }

        return {
            "tenant_id": tenant_id,
            "escalation_level": snapshot.escalation_level.value,
            "request_count": snapshot.request_count,
            "error_count": snapshot.error_count,
            "error_rate": round(snapshot.error_rate, 4),
            "avg_latency_ms": round(snapshot.avg_latency_ms, 1),
            "estimated_ai_tokens": snapshot.estimated_ai_tokens,
            "estimated_cosmos_rus": round(snapshot.estimated_cosmos_rus, 2),
            "effective_rate_limit_rpm": snapshot.effective_rate_limit_rpm,
            "reasons": snapshot.reasons,
        }

    def get_all_statuses(self) -> dict[str, dict[str, Any]]:
        """Get monitoring status for all tracked tenants."""
        return {
            tenant_id: self.get_tenant_status(tenant_id)
            for tenant_id in self._events
        }

    def get_escalated_tenants(self) -> list[dict[str, Any]]:
        """Get only tenants with escalation level above NORMAL.

        Useful for operational dashboards and alerting.
        """
        results = []
        for tenant_id, level in self._current_levels.items():
            if level != EscalationLevel.NORMAL:
                results.append(self.get_tenant_status(tenant_id))
        return results

    def reset_tenant(self, tenant_id: str) -> None:
        """Reset monitoring state for a tenant (admin operation).

        Clears all events, snapshots, and escalation history.
        """
        self._events.pop(tenant_id, None)
        self._snapshots.pop(tenant_id, None)
        self._last_evaluated.pop(tenant_id, None)
        self._current_levels.pop(tenant_id, None)
        logger.info("Tenant usage monitor reset: tenant=%s", tenant_id)

    def health_summary(self) -> dict[str, Any]:
        """Get a health summary for the /ready endpoint."""
        total_tracked = len(self._events)
        escalated = len([
            l for l in self._current_levels.values()
            if l != EscalationLevel.NORMAL
        ])
        throttled = len([
            l for l in self._current_levels.values()
            if l in (EscalationLevel.THROTTLE, EscalationLevel.ISOLATE)
        ])

        return {
            "tenants_tracked": total_tracked,
            "tenants_escalated": escalated,
            "tenants_throttled": throttled,
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_monitor: TenantUsageMonitor | None = None


def get_usage_monitor() -> TenantUsageMonitor:
    """Get the module-level TenantUsageMonitor singleton."""
    global _monitor
    if _monitor is None:
        _monitor = TenantUsageMonitor()
    return _monitor
