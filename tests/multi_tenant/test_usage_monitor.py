"""P3 TenantUsageMonitor unit tests — progressive throttling state machine.

Tests the TenantUsageMonitor's 5-level escalation (NORMAL → WATCH → WARN →
THROTTLE → ISOLATE), metric tracking (latency, error rate, AI tokens,
Cosmos RUs), rolling window pruning, sticky de-escalation, multi-tenant
isolation, effective rate limit calculation, and health summary.

Test IDs: TUM-01 through TUM-15 per §7.2 of
docs/COMPREHENSIVE-TEST-PLAN.md.

Work Item: P3 post-launch tests.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier
from src.multi_tenant.tenant_usage_monitor import (
    ISOLATE_MULTIPLIER,
    ISOLATE_RATE_FACTOR,
    LATENCY_THROTTLE_MS,
    LATENCY_WARN_MS,
    THROTTLE_ERROR_RATE,
    THROTTLE_MULTIPLIER,
    THROTTLE_RATE_FACTOR,
    WARN_ERROR_RATE,
    WARN_MULTIPLIER,
    WINDOW_MINUTES,
    WINDOW_SECONDS,
    EscalationLevel,
    TenantUsageMonitor,
    TenantUsageSnapshot,
    UsageEvent,
    get_usage_monitor,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TENANT_A = "t-monitor-001"
_TENANT_B = "t-monitor-002"
_STARTER = TenantTier.STARTER.value
_PROFESSIONAL = TenantTier.PROFESSIONAL.value
_ENTERPRISE = TenantTier.ENTERPRISE.value


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _starter_rpm() -> int:
    """Get the Starter tier's rate_limit_rpm — falls back to 10 (monitor default)."""
    return TIER_DEFAULTS.get(_STARTER, {}).get("rate_limit_rpm", 10)


def _pro_rpm() -> int:
    return TIER_DEFAULTS.get(_PROFESSIONAL, {}).get("rate_limit_rpm", 10)


def _window_capacity(rpm: int) -> float:
    """Theoretical max requests in the 5-minute window."""
    return rpm * WINDOW_MINUTES


def _make_monitor(window_seconds: float = WINDOW_SECONDS) -> TenantUsageMonitor:
    """Create a fresh TenantUsageMonitor with zero evaluation debounce."""
    return TenantUsageMonitor(
        window_seconds=window_seconds,
        evaluation_interval=0,  # disable debounce for deterministic tests
    )


def _fill_events(
    monitor: TenantUsageMonitor,
    tenant_id: str,
    count: int,
    tier: str = _STARTER,
    latency_ms: float = 100.0,
    is_error: bool = False,
    ai_tokens: int = 500,
    cosmos_rus: float = 3.0,
) -> None:
    """Record `count` events for a tenant."""
    for _ in range(count):
        monitor.record_event(
            tenant_id=tenant_id,
            tier=tier,
            latency_ms=latency_ms,
            is_error=is_error,
            ai_tokens=ai_tokens,
            cosmos_rus=cosmos_rus,
        )


# ===========================================================================
# TUM-01: NORMAL state — usage within thresholds
# ===========================================================================


class TestNormalState:
    """TUM-01: Tenant with usage well below thresholds stays NORMAL."""

    def test_tum_01_normal_usage_stays_normal(self):
        """TUM-01: Low usage results in NORMAL escalation level."""
        monitor = _make_monitor()

        # Record a small number of events (well below warn threshold)
        _fill_events(monitor, _TENANT_A, count=2, tier=_STARTER)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level == EscalationLevel.NORMAL
        assert snapshot.effective_rate_limit_rpm is None
        assert snapshot.request_count == 2
        assert snapshot.reasons == []

    def test_tum_01b_zero_events_is_normal(self):
        """TUM-01b: No events recorded results in NORMAL."""
        monitor = _make_monitor()
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level == EscalationLevel.NORMAL
        assert snapshot.request_count == 0


# ===========================================================================
# TUM-02: WARN state — threshold exceeded
# ===========================================================================


class TestWarnState:
    """TUM-02: Tenant exceeding warn threshold escalates to WARN."""

    def test_tum_02_warn_on_volume_threshold(self):
        """TUM-02: Request volume at 80% of window capacity triggers WARN."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)
        warn_count = int(capacity * WARN_MULTIPLIER)

        _fill_events(monitor, _TENANT_A, count=warn_count, tier=_STARTER)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level == EscalationLevel.WARN
        assert any("warn" in r.lower() for r in snapshot.reasons)

    def test_tum_02b_warn_on_error_rate(self):
        """TUM-02b: Error rate at 10% triggers at least WARN."""
        monitor = _make_monitor()

        # 10 requests, 1 error = 10% error rate = WARN_ERROR_RATE
        _fill_events(monitor, _TENANT_A, count=9, is_error=False)
        _fill_events(monitor, _TENANT_A, count=1, is_error=True)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level.value in ("warn", "throttle", "isolate")
        assert any("error_rate" in r for r in snapshot.reasons)

    def test_tum_02c_warn_on_high_latency(self):
        """TUM-02c: Average latency >= 3000ms triggers at least WARN."""
        monitor = _make_monitor()

        _fill_events(
            monitor, _TENANT_A, count=5,
            latency_ms=LATENCY_WARN_MS,
        )

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level.value in ("warn", "throttle", "isolate")
        assert any("latency" in r for r in snapshot.reasons)


# ===========================================================================
# TUM-03: THROTTLE state — rate reduced to 50%
# ===========================================================================


class TestThrottleState:
    """TUM-03: Tenant exceeding throttle threshold gets rate reduced."""

    def test_tum_03_throttle_on_volume(self):
        """TUM-03: Request volume at 100% of window capacity triggers THROTTLE."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)
        throttle_count = int(capacity * THROTTLE_MULTIPLIER)

        _fill_events(monitor, _TENANT_A, count=throttle_count, tier=_STARTER)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level == EscalationLevel.THROTTLE
        # Effective RPM should be 50% of tier RPM
        expected_rpm = max(1, int(rpm * THROTTLE_RATE_FACTOR))
        assert snapshot.effective_rate_limit_rpm == expected_rpm

    def test_tum_03b_throttle_on_error_rate(self):
        """TUM-03b: Error rate at 25% triggers THROTTLE."""
        monitor = _make_monitor()

        # 8 requests, 2 errors = 25% = THROTTLE_ERROR_RATE
        good = int(8 * (1 - THROTTLE_ERROR_RATE) / (1 - THROTTLE_ERROR_RATE))
        error = int(THROTTLE_ERROR_RATE * 8)
        _fill_events(monitor, _TENANT_A, count=6, is_error=False)
        _fill_events(monitor, _TENANT_A, count=2, is_error=True)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level.value in ("throttle", "isolate")

    def test_tum_03c_throttle_on_latency(self):
        """TUM-03c: Average latency >= 5000ms triggers THROTTLE."""
        monitor = _make_monitor()

        _fill_events(
            monitor, _TENANT_A, count=5,
            latency_ms=LATENCY_THROTTLE_MS,
        )

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level.value in ("throttle", "isolate")
        assert any("latency" in r for r in snapshot.reasons)


# ===========================================================================
# TUM-04: ISOLATE state — rate reduced to 10%
# ===========================================================================


class TestIsolateState:
    """TUM-04: Tenant at extreme abuse level gets isolated."""

    def test_tum_04_isolate_on_extreme_volume(self):
        """TUM-04: Request volume at 200% of window capacity triggers ISOLATE."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)
        isolate_count = int(capacity * ISOLATE_MULTIPLIER)

        _fill_events(monitor, _TENANT_A, count=isolate_count, tier=_STARTER)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level == EscalationLevel.ISOLATE
        expected_rpm = max(1, int(rpm * ISOLATE_RATE_FACTOR))
        assert snapshot.effective_rate_limit_rpm == expected_rpm
        assert any("isolate" in r.lower() for r in snapshot.reasons)


# ===========================================================================
# TUM-05: Full progressive escalation path
# ===========================================================================


class TestProgressiveEscalation:
    """TUM-05: Watch → Warn → Throttle → Isolate progression."""

    def test_tum_05_full_escalation_path(self):
        """TUM-05: Progressive escalation from NORMAL to ISOLATE."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)

        # Start NORMAL
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        assert snapshot.escalation_level == EscalationLevel.NORMAL

        # Add enough events for WARN (80% capacity)
        warn_count = int(capacity * WARN_MULTIPLIER)
        _fill_events(monitor, _TENANT_A, count=warn_count, tier=_STARTER)
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        assert snapshot.escalation_level == EscalationLevel.WARN

        # Add more to reach THROTTLE (100% capacity)
        additional = int(capacity * THROTTLE_MULTIPLIER) - warn_count
        if additional > 0:
            _fill_events(monitor, _TENANT_A, count=additional, tier=_STARTER)
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        assert snapshot.escalation_level == EscalationLevel.THROTTLE

        # Add more to reach ISOLATE (200% capacity)
        more = int(capacity * ISOLATE_MULTIPLIER) - int(capacity * THROTTLE_MULTIPLIER)
        _fill_events(monitor, _TENANT_A, count=more, tier=_STARTER)
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        assert snapshot.escalation_level == EscalationLevel.ISOLATE


# ===========================================================================
# TUM-06: De-escalation (sticky — at most one level at a time)
# ===========================================================================


class TestDeEscalation:
    """TUM-06: De-escalation drops by at most one level per evaluation."""

    def test_tum_06_sticky_deescalation(self):
        """TUM-06: Tenant at ISOLATE de-escalates one step at a time."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)

        # Push to ISOLATE
        isolate_count = int(capacity * ISOLATE_MULTIPLIER)
        _fill_events(monitor, _TENANT_A, count=isolate_count, tier=_STARTER)
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        assert snapshot.escalation_level == EscalationLevel.ISOLATE

        # Clear all events (simulate time passing — usage normalises)
        monitor._events[_TENANT_A].clear()

        # First evaluation after clearing: should drop to THROTTLE (not NORMAL)
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        assert snapshot.escalation_level == EscalationLevel.THROTTLE

        # Second evaluation: THROTTLE → WARN
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        assert snapshot.escalation_level == EscalationLevel.WARN

        # Third: WARN → WATCH (or NORMAL depending on _LEVEL_ORDER mapping)
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        # WATCH is level 1
        assert snapshot.escalation_level == EscalationLevel.WATCH

        # Fourth: WATCH → NORMAL
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        assert snapshot.escalation_level == EscalationLevel.NORMAL


# ===========================================================================
# TUM-07: Latency tracking
# ===========================================================================


class TestLatencyTracking:
    """TUM-07: Average latency is computed correctly in snapshot."""

    def test_tum_07_latency_metric_tracked(self):
        """TUM-07: Snapshot reflects total and average latency correctly."""
        monitor = _make_monitor()

        monitor.record_event(_TENANT_A, _STARTER, latency_ms=200.0)
        monitor.record_event(_TENANT_A, _STARTER, latency_ms=400.0)
        monitor.record_event(_TENANT_A, _STARTER, latency_ms=600.0)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.total_latency_ms == 1200.0
        assert snapshot.request_count == 3
        assert snapshot.avg_latency_ms == pytest.approx(400.0, abs=0.1)


# ===========================================================================
# TUM-08: Cosmos RU consumption tracking
# ===========================================================================


class TestCosmosRuTracking:
    """TUM-08: Estimated Cosmos DB RU consumption is aggregated."""

    def test_tum_08_cosmos_ru_aggregated(self):
        """TUM-08: Cosmos RU consumption is summed across events."""
        monitor = _make_monitor()

        monitor.record_event(_TENANT_A, _STARTER, cosmos_rus=4.2)
        monitor.record_event(_TENANT_A, _STARTER, cosmos_rus=3.8)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.estimated_cosmos_rus == pytest.approx(8.0, abs=0.1)


# ===========================================================================
# TUM-09: OpenAI token consumption tracking
# ===========================================================================


class TestAiTokenTracking:
    """TUM-09: Estimated AI token consumption is aggregated."""

    def test_tum_09_ai_tokens_aggregated(self):
        """TUM-09: AI token consumption is summed across events."""
        monitor = _make_monitor()

        monitor.record_event(_TENANT_A, _STARTER, ai_tokens=500)
        monitor.record_event(_TENANT_A, _STARTER, ai_tokens=700)
        monitor.record_event(_TENANT_A, _STARTER, ai_tokens=300)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.estimated_ai_tokens == 1500


# ===========================================================================
# TUM-10: Error rate tracking
# ===========================================================================


class TestErrorRateTracking:
    """TUM-10: Error rate is computed correctly."""

    def test_tum_10_error_rate_correct(self):
        """TUM-10: Error rate = error_count / request_count."""
        monitor = _make_monitor()

        _fill_events(monitor, _TENANT_A, count=8, is_error=False)
        _fill_events(monitor, _TENANT_A, count=2, is_error=True)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.error_count == 2
        assert snapshot.request_count == 10
        assert snapshot.error_rate == pytest.approx(0.2, abs=0.01)

    def test_tum_10b_zero_requests_zero_error_rate(self):
        """TUM-10b: Error rate is 0 when no requests recorded."""
        monitor = _make_monitor()
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        assert snapshot.error_rate == 0.0


# ===========================================================================
# TUM-11: Payload size tracking (via event count as proxy)
# ===========================================================================


class TestPayloadSizeTracking:
    """TUM-11: Payload size is indirectly tracked via event aggregation."""

    def test_tum_11_all_metrics_aggregated(self):
        """TUM-11: All metric fields are correctly populated in snapshot."""
        monitor = _make_monitor()

        monitor.record_event(
            _TENANT_A, _STARTER,
            latency_ms=150.0,
            is_error=False,
            ai_tokens=800,
            cosmos_rus=5.5,
        )
        monitor.record_event(
            _TENANT_A, _STARTER,
            latency_ms=250.0,
            is_error=True,
            ai_tokens=200,
            cosmos_rus=2.0,
        )

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.request_count == 2
        assert snapshot.error_count == 1
        assert snapshot.total_latency_ms == 400.0
        assert snapshot.estimated_ai_tokens == 1000
        assert snapshot.estimated_cosmos_rus == pytest.approx(7.5, abs=0.1)
        assert snapshot.tenant_id == _TENANT_A
        assert snapshot.tier == _STARTER


# ===========================================================================
# TUM-12: 5-minute rolling window
# ===========================================================================


class TestRollingWindow:
    """TUM-12: Old events outside the window are pruned."""

    def test_tum_12_old_events_pruned(self):
        """TUM-12: Events older than the window are excluded from evaluation."""
        monitor = _make_monitor(window_seconds=300)

        # Inject old events directly with timestamps in the past
        now = time.monotonic()
        old_event = UsageEvent(
            timestamp=now - 400,  # 400 seconds ago — outside 300s window
            latency_ms=100.0,
            is_error=False,
            ai_tokens=500,
            cosmos_rus=3.0,
        )
        recent_event = UsageEvent(
            timestamp=now - 10,  # 10 seconds ago — inside window
            latency_ms=200.0,
            is_error=True,
            ai_tokens=700,
            cosmos_rus=4.0,
        )

        monitor._events[_TENANT_A] = [old_event, recent_event]

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        # Only the recent event should be counted
        assert snapshot.request_count == 1
        assert snapshot.error_count == 1
        assert snapshot.estimated_ai_tokens == 700
        assert snapshot.total_latency_ms == 200.0

    def test_tum_12b_all_events_pruned_when_expired(self):
        """TUM-12b: All events outside the window results in empty snapshot."""
        monitor = _make_monitor(window_seconds=300)

        now = time.monotonic()
        old_event = UsageEvent(
            timestamp=now - 600,
            latency_ms=100.0,
        )
        monitor._events[_TENANT_A] = [old_event]

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.request_count == 0
        assert snapshot.escalation_level == EscalationLevel.NORMAL


# ===========================================================================
# TUM-13: Multiple tenants — independent monitors
# ===========================================================================


class TestMultiTenantIsolation:
    """TUM-13: Each tenant's monitor is independent."""

    def test_tum_13_independent_monitors(self):
        """TUM-13: Events for tenant A do not affect tenant B's evaluation."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)

        # Push tenant A to THROTTLE
        throttle_count = int(capacity * THROTTLE_MULTIPLIER)
        _fill_events(monitor, _TENANT_A, count=throttle_count, tier=_STARTER)

        # Tenant B has low usage
        _fill_events(monitor, _TENANT_B, count=2, tier=_STARTER)

        snapshot_a = monitor.evaluate(_TENANT_A, _STARTER)
        snapshot_b = monitor.evaluate(_TENANT_B, _STARTER)

        assert snapshot_a.escalation_level == EscalationLevel.THROTTLE
        assert snapshot_b.escalation_level == EscalationLevel.NORMAL

    def test_tum_13b_get_all_statuses_returns_both(self):
        """TUM-13b: get_all_statuses() returns independent status per tenant."""
        monitor = _make_monitor()

        _fill_events(monitor, _TENANT_A, count=5)
        _fill_events(monitor, _TENANT_B, count=3)

        # Evaluate both to populate snapshots
        monitor.evaluate(_TENANT_A, _STARTER)
        monitor.evaluate(_TENANT_B, _STARTER)

        statuses = monitor.get_all_statuses()

        assert _TENANT_A in statuses
        assert _TENANT_B in statuses
        assert statuses[_TENANT_A]["request_count"] == 5
        assert statuses[_TENANT_B]["request_count"] == 3


# ===========================================================================
# TUM-14: Throttled tenant can still access health endpoints
# ===========================================================================


class TestPartialAccess:
    """TUM-14: Throttled tenants still have reduced access (not zero)."""

    def test_tum_14_throttled_has_nonzero_rate_limit(self):
        """TUM-14: Throttled tenant's effective rate limit is > 0."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)

        # Push to THROTTLE
        throttle_count = int(capacity * THROTTLE_MULTIPLIER)
        _fill_events(monitor, _TENANT_A, count=throttle_count, tier=_STARTER)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level == EscalationLevel.THROTTLE
        assert snapshot.effective_rate_limit_rpm is not None
        assert snapshot.effective_rate_limit_rpm >= 1  # Never zero

    def test_tum_14b_isolated_has_nonzero_rate_limit(self):
        """TUM-14b: Even isolated tenant gets at least 1 RPM (for health checks)."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)

        # Push to ISOLATE
        isolate_count = int(capacity * ISOLATE_MULTIPLIER)
        _fill_events(monitor, _TENANT_A, count=isolate_count, tier=_STARTER)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level == EscalationLevel.ISOLATE
        assert snapshot.effective_rate_limit_rpm is not None
        assert snapshot.effective_rate_limit_rpm >= 1

    def test_tum_14c_normal_has_no_override(self):
        """TUM-14c: Normal tenant has no effective rate limit override."""
        monitor = _make_monitor()
        _fill_events(monitor, _TENANT_A, count=2)

        snapshot = monitor.evaluate(_TENANT_A, _STARTER)

        assert snapshot.escalation_level == EscalationLevel.NORMAL
        assert snapshot.effective_rate_limit_rpm is None


# ===========================================================================
# TUM-15: Isolation creates audit log entry (via logging)
# ===========================================================================


class TestAuditLogging:
    """TUM-15: Escalation changes are logged for operational visibility."""

    def test_tum_15_escalation_change_logged(self):
        """TUM-15: Escalation level changes produce log messages."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)

        throttle_count = int(capacity * THROTTLE_MULTIPLIER)
        _fill_events(monitor, _TENANT_A, count=throttle_count, tier=_STARTER)

        with patch("src.multi_tenant.tenant_usage_monitor.logger") as mock_logger:
            monitor.evaluate(_TENANT_A, _STARTER)

            # Should have logged the escalation from NORMAL → THROTTLE
            assert mock_logger.warning.called or mock_logger.info.called
            # Check the log message includes "escalation"
            all_calls = mock_logger.warning.call_args_list + mock_logger.info.call_args_list
            log_messages = [str(c) for c in all_calls]
            assert any("escalation" in msg.lower() for msg in log_messages)


# ===========================================================================
# Additional coverage: get_effective_rate_limit, get_tenant_status,
# get_escalated_tenants, reset_tenant, health_summary, module singleton
# ===========================================================================


class TestHelperMethods:
    """Additional tests for helper/query methods."""

    def test_get_effective_rate_limit_none_for_unknown(self):
        """get_effective_rate_limit returns None for unknown tenant."""
        monitor = _make_monitor()
        result = monitor.get_effective_rate_limit("unknown-tenant")
        assert result is None

    def test_get_effective_rate_limit_returns_reduced_rpm(self):
        """get_effective_rate_limit returns reduced RPM for throttled tenant."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)

        throttle_count = int(capacity * THROTTLE_MULTIPLIER)
        _fill_events(monitor, _TENANT_A, count=throttle_count, tier=_STARTER)
        monitor.evaluate(_TENANT_A, _STARTER)

        result = monitor.get_effective_rate_limit(_TENANT_A, _STARTER)
        expected = max(1, int(rpm * THROTTLE_RATE_FACTOR))
        assert result == expected

    def test_get_tenant_status_unknown_tenant(self):
        """get_tenant_status returns default dict for unknown tenant."""
        monitor = _make_monitor()
        status = monitor.get_tenant_status("unknown")

        assert status["escalation_level"] == "normal"
        assert status["request_count"] == 0
        assert status["effective_rate_limit_rpm"] is None

    def test_get_tenant_status_reflects_snapshot(self):
        """get_tenant_status returns correct dict for evaluated tenant."""
        monitor = _make_monitor()
        monitor.record_event(_TENANT_A, _STARTER, latency_ms=100, ai_tokens=500, cosmos_rus=3.0)
        monitor.evaluate(_TENANT_A, _STARTER)

        status = monitor.get_tenant_status(_TENANT_A)

        assert status["tenant_id"] == _TENANT_A
        assert status["request_count"] == 1
        assert status["estimated_ai_tokens"] == 500
        assert status["estimated_cosmos_rus"] == 3.0

    def test_get_escalated_tenants_empty_when_all_normal(self):
        """get_escalated_tenants returns empty list when all tenants normal."""
        monitor = _make_monitor()
        _fill_events(monitor, _TENANT_A, count=2)
        monitor.evaluate(_TENANT_A, _STARTER)

        result = monitor.get_escalated_tenants()
        assert result == []

    def test_get_escalated_tenants_returns_escalated_only(self):
        """get_escalated_tenants only returns tenants above NORMAL."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)

        # Tenant A: normal
        _fill_events(monitor, _TENANT_A, count=2)
        monitor.evaluate(_TENANT_A, _STARTER)

        # Tenant B: throttled
        throttle_count = int(capacity * THROTTLE_MULTIPLIER)
        _fill_events(monitor, _TENANT_B, count=throttle_count)
        monitor.evaluate(_TENANT_B, _STARTER)

        result = monitor.get_escalated_tenants()
        assert len(result) == 1
        assert result[0]["tenant_id"] == _TENANT_B

    def test_reset_tenant_clears_all_state(self):
        """reset_tenant removes all state for that tenant."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)

        # Push to throttle
        throttle_count = int(capacity * THROTTLE_MULTIPLIER)
        _fill_events(monitor, _TENANT_A, count=throttle_count)
        monitor.evaluate(_TENANT_A, _STARTER)
        assert monitor._current_levels[_TENANT_A] == EscalationLevel.THROTTLE

        # Reset
        monitor.reset_tenant(_TENANT_A)

        assert _TENANT_A not in monitor._events
        assert _TENANT_A not in monitor._snapshots
        assert _TENANT_A not in monitor._last_evaluated
        assert _TENANT_A not in monitor._current_levels

        # Fresh evaluate returns NORMAL
        snapshot = monitor.evaluate(_TENANT_A, _STARTER)
        assert snapshot.escalation_level == EscalationLevel.NORMAL

    def test_health_summary_counts(self):
        """health_summary returns correct count of tracked/escalated/throttled."""
        monitor = _make_monitor()
        rpm = _starter_rpm()
        capacity = _window_capacity(rpm)

        # Tenant A: normal
        _fill_events(monitor, _TENANT_A, count=2)
        monitor.evaluate(_TENANT_A, _STARTER)

        # Tenant B: throttle
        throttle_count = int(capacity * THROTTLE_MULTIPLIER)
        _fill_events(monitor, _TENANT_B, count=throttle_count)
        monitor.evaluate(_TENANT_B, _STARTER)

        summary = monitor.health_summary()

        assert summary["tenants_tracked"] == 2
        assert summary["tenants_escalated"] == 1
        assert summary["tenants_throttled"] == 1

    def test_module_singleton(self):
        """get_usage_monitor returns a singleton instance."""
        import src.multi_tenant.tenant_usage_monitor as tum_mod
        original = tum_mod._monitor
        try:
            tum_mod._monitor = None
            m1 = get_usage_monitor()
            m2 = get_usage_monitor()
            assert m1 is m2
        finally:
            tum_mod._monitor = original


class TestTenantUsageSnapshot:
    """Unit tests for TenantUsageSnapshot properties."""

    def test_avg_latency_zero_requests(self):
        """avg_latency_ms is 0 when request_count is 0."""
        snap = TenantUsageSnapshot(tenant_id="t-1", request_count=0, total_latency_ms=0)
        assert snap.avg_latency_ms == 0.0

    def test_avg_latency_computed(self):
        """avg_latency_ms computes total / count."""
        snap = TenantUsageSnapshot(
            tenant_id="t-1",
            request_count=4,
            total_latency_ms=800.0,
        )
        assert snap.avg_latency_ms == pytest.approx(200.0)

    def test_error_rate_zero_requests(self):
        """error_rate is 0 when request_count is 0."""
        snap = TenantUsageSnapshot(tenant_id="t-1", request_count=0, error_count=0)
        assert snap.error_rate == 0.0

    def test_error_rate_computed(self):
        """error_rate computes error_count / request_count."""
        snap = TenantUsageSnapshot(
            tenant_id="t-1",
            request_count=10,
            error_count=3,
        )
        assert snap.error_rate == pytest.approx(0.3)


class TestProfessionalTier:
    """Verify tier-specific thresholds for Professional tier."""

    def test_professional_same_rpm_as_starter(self):
        """All tiers share uniform admin RPM; differentiation is via other entitlements."""
        pro_rpm = _pro_rpm()
        starter_rpm = _starter_rpm()

        # Uniform admin RPM: professional == starter
        assert pro_rpm == starter_rpm

        # max_concurrent removed from TIER_DEFAULTS — tiers now differ
        # only on included_conversations, memory_layers, overage_rate
        from src.multi_tenant.cosmos_schema import TIER_DEFAULTS
        assert "max_concurrent" not in TIER_DEFAULTS["professional"]
        assert "max_concurrent" not in TIER_DEFAULTS["starter"]
