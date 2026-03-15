"""Performance & load tests — latency validation, throughput, streaming,
pipeline budget enforcement, and SLA compliance.

Test IDs: PERF-01 through PERF-30 per §9 of docs/COMPREHENSIVE-TEST-PLAN.md.

These tests validate performance contracts that exist in the implemented
code: SLA percentile calculations, pipeline timeout budgets, circuit
breaker state machines, SSE connection management, rate limit enforcement
timing, and cost model calculations.

Tests that require deployed Azure infrastructure (KEDA auto-scale, actual
AI agent latency) are marked with explanatory comments and use synthetic
data to validate the enforcement logic.

Run:
    pytest tests/performance/test_performance.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import TenantTier, TIER_DEFAULTS
from src.multi_tenant.pipeline_resilience import (
    CIRCUIT_BREAKER_CONFIGS,
    PIPELINE_DEADLINE_MS,
    STAGE_BUDGETS_MS,
    CircuitBreakerState,
    PipelineTimeoutBudget,
    PipelineTimeoutError,
    ServiceCircuitBreaker,
    ServiceCircuitBreakerRegistry,
    ServiceUnavailableError,
    StageResult,
    call_with_breaker,
)
from src.multi_tenant.sla_monitoring import (
    LATENCY_WINDOW_SECONDS,
    MAX_SAMPLES_PER_TENANT,
    SLA_TARGETS,
    LatencyPercentiles,
    PlatformSLASummary,
    SLAComplianceResult,
    SLAMonitoringService,
    _percentile,
)
from src.chat.sse_manager import (
    BUFFER_EXPIRY_SECONDS,
    KEEPALIVE_INTERVAL_SECONDS,
    MAX_BUFFERED_EVENTS,
    EventBuffer,
    SSEConnectionManager,
)


# ===========================================================================
# §9.1: Latency Validation (PERF-01 through PERF-10)
# ===========================================================================


class TestLatencyValidation:
    """PERF-01 through PERF-10: SLA latency metrics and compliance."""

    def test_perf_01_p50_calculation_under_sla(self):
        """PERF-01: P50 latency < 1,500ms when most requests are fast."""
        svc = SLAMonitoringService()
        # Simulate 100 requests with realistic distribution:
        # 60% at 800ms, 30% at 1200ms, 10% at 3000ms
        now = time.monotonic()
        for i in range(60):
            svc._platform_samples.append((now, 800.0))
            svc._tenant_samples.setdefault("t-1", deque(maxlen=MAX_SAMPLES_PER_TENANT))
            svc._tenant_samples["t-1"].append((now, 800.0))
        for i in range(30):
            svc._platform_samples.append((now, 1200.0))
            svc._tenant_samples["t-1"].append((now, 1200.0))
        for i in range(10):
            svc._platform_samples.append((now, 3000.0))
            svc._tenant_samples["t-1"].append((now, 3000.0))

        percentiles = svc.get_latency_percentiles("t-1")
        assert percentiles.p50_ms < 1500  # SLA target
        assert percentiles.sample_count == 100

    def test_perf_02_p95_calculation_under_sla(self):
        """PERF-02: P95 latency < 2,000ms with realistic distribution."""
        svc = SLAMonitoringService()
        now = time.monotonic()
        # 95% of requests at 1500ms, 5% at 4000ms
        for _ in range(95):
            svc._platform_samples.append((now, 1500.0))
        for _ in range(5):
            svc._platform_samples.append((now, 4000.0))

        percentiles = svc.get_latency_percentiles()
        assert percentiles.p95_ms <= 2000  # SLA target

    def test_perf_03_p99_calculation_under_sla(self):
        """PERF-03: P99 latency < 5,000ms with outlier tolerance."""
        svc = SLAMonitoringService()
        now = time.monotonic()
        # 99% at 2000ms, 1% at 4500ms (under SLA)
        for _ in range(99):
            svc._platform_samples.append((now, 2000.0))
        for _ in range(1):
            svc._platform_samples.append((now, 4500.0))

        percentiles = svc.get_latency_percentiles()
        assert percentiles.p99_ms < 5000  # SLA target

    def test_perf_04_intent_classifier_budget(self):
        """PERF-04: Intent Classifier stage budget is 5,000ms (Azure OpenAI)."""
        assert STAGE_BUDGETS_MS["intent-classifier"] == 5_000

    def test_perf_05_knowledge_retrieval_budget(self):
        """PERF-05: Knowledge Retrieval stage budget is 10,000ms (hybrid search cold-start)."""
        assert STAGE_BUDGETS_MS["knowledge-retrieval"] == 10_000

    def test_perf_06_response_generator_budget(self):
        """PERF-06: Response Generator stage budget is 15,000ms (streaming)."""
        assert STAGE_BUDGETS_MS["response-generator"] == 15_000

    def test_perf_07_critic_budget(self):
        """PERF-07: Critic stage budget is 5,000ms."""
        assert STAGE_BUDGETS_MS["critic-supervisor"] == 5_000

    async def test_perf_08_pipeline_budget_enforces_deadline(self):
        """PERF-08: PipelineTimeoutBudget enforces the 8s hard deadline."""
        budget = PipelineTimeoutBudget(total_deadline_ms=100)  # 100ms for test speed

        # Fast stage succeeds
        async def fast_stage():
            return "ok"

        result = await budget.execute_with_budget("fast", fast_stage())
        assert result == "ok"

        # Wait for budget to expire
        await asyncio.sleep(0.15)
        assert budget.is_expired is True

    def test_perf_09_health_check_latency_contract(self):
        """PERF-09: Health endpoint should be pure in-memory — no external calls."""
        svc = SLAMonitoringService()
        svc.record_latency("t-1", 500.0)
        svc.record_health_check(True)

        start = time.monotonic()
        summary = svc.health_summary()
        elapsed_ms = (time.monotonic() - start) * 1000

        assert elapsed_ms < 50  # In-memory operation should be < 50ms
        assert "p50_ms" in summary
        assert "uptime_pct" in summary

    def test_perf_10_config_cache_contract(self):
        """PERF-10: Config endpoint uses 60s cache — validated in TenantConfigProcessor."""
        # SPEC-1748: Config cache TTL increased from 60s to 300s for scale.
        from src.multi_tenant.tenant_config_processor import CACHE_TTL_SECONDS
        assert CACHE_TTL_SECONDS == 300

    def test_perf_percentile_empty_list(self):
        """Percentile function returns 0 for empty list."""
        assert _percentile([], 50) == 0.0

    def test_perf_percentile_single_value(self):
        """Percentile function returns the value for a single-element list."""
        assert _percentile([500.0], 50) == 500.0
        assert _percentile([500.0], 99) == 500.0

    def test_perf_percentile_linear_interpolation(self):
        """Percentile function performs linear interpolation."""
        values = [100.0, 200.0, 300.0, 400.0, 500.0]
        p50 = _percentile(values, 50)
        assert p50 == 300.0  # Exact midpoint

        p25 = _percentile(values, 25)
        assert p25 == 200.0  # Exact quartile

    def test_perf_sla_compliance_all_tiers(self):
        """SLA compliance check works for all tier targets."""
        svc = SLAMonitoringService()
        now = time.monotonic()

        # All requests well within SLA
        for _ in range(100):
            svc._platform_samples.append((now, 500.0))
        for _ in range(10):
            svc._health_checks.append((now, True))

        for tier in [TenantTier.STARTER.value, TenantTier.PROFESSIONAL.value, TenantTier.ENTERPRISE.value]:
            result = svc.check_sla_compliance(tier)
            assert result.overall_compliant is True
            assert result.p50_compliant is True
            assert result.p95_compliant is True
            assert result.p99_compliant is True
            assert result.uptime_compliant is True

    def test_perf_sla_violation_detected(self):
        """SLA violation is detected when latencies exceed targets."""
        svc = SLAMonitoringService()
        now = time.monotonic()

        # All requests above P50 target (1500ms)
        for _ in range(100):
            svc._platform_samples.append((now, 2000.0))

        result = svc.check_sla_compliance(TenantTier.STARTER.value)
        assert result.p50_compliant is False
        assert result.overall_compliant is False

    def test_perf_uptime_calculation(self):
        """Uptime percentage calculated correctly from health checks."""
        svc = SLAMonitoringService()
        now = time.monotonic()

        # 95 healthy + 5 unhealthy = 95% uptime
        for _ in range(95):
            svc._health_checks.append((now, True))
        for _ in range(5):
            svc._health_checks.append((now, False))

        uptime = svc.get_uptime_pct()
        assert abs(uptime - 95.0) < 0.1

    def test_perf_window_filtering(self):
        """Samples outside the window are excluded from percentile calculations."""
        svc = SLAMonitoringService()
        now = time.monotonic()
        old = now - LATENCY_WINDOW_SECONDS - 100  # Outside window

        # Old samples (outside window) — should be excluded
        for _ in range(50):
            svc._platform_samples.append((old, 10000.0))
        # Recent samples (inside window)
        for _ in range(50):
            svc._platform_samples.append((now, 500.0))

        percentiles = svc.get_latency_percentiles()
        assert percentiles.sample_count == 50  # Only recent samples
        assert percentiles.p50_ms == 500.0  # Only recent data

    def test_perf_cleanup_removes_old_samples(self):
        """cleanup_old_samples removes expired data and empty tenant queues."""
        svc = SLAMonitoringService()
        now = time.monotonic()
        old = now - 10000  # Very old

        svc._tenant_samples["old-tenant"] = deque(maxlen=MAX_SAMPLES_PER_TENANT)
        svc._tenant_samples["old-tenant"].append((old, 1000.0))

        svc._tenant_samples["recent-tenant"] = deque(maxlen=MAX_SAMPLES_PER_TENANT)
        svc._tenant_samples["recent-tenant"].append((now, 500.0))

        cleaned = svc.cleanup_old_samples(max_age_seconds=5000)
        assert cleaned == 1  # old-tenant removed
        assert "old-tenant" not in svc._tenant_samples
        assert "recent-tenant" in svc._tenant_samples

    def test_perf_platform_summary(self):
        """Platform summary aggregates all tier compliance."""
        svc = SLAMonitoringService()
        now = time.monotonic()

        for _ in range(100):
            svc._platform_samples.append((now, 500.0))
        for _ in range(10):
            svc._health_checks.append((now, True))

        summary = svc.get_platform_summary()
        assert isinstance(summary, PlatformSLASummary)
        assert summary.total_requests == 100
        assert summary.overall_compliant is True
        assert len(summary.per_tier_compliance) == 3


# ===========================================================================
# §9.2: Throughput & Concurrency (PERF-11 through PERF-20)
# ===========================================================================


class TestThroughputConcurrency:
    """PERF-11 through PERF-20: Concurrency limits, circuit breakers, rate limiting."""

    def test_perf_11_tier_concurrency_limits_removed(self):
        """PERF-11: max_concurrent removed from TIER_DEFAULTS."""
        for tier in ["trial", "starter", "professional", "enterprise"]:
            assert "max_concurrent" not in TIER_DEFAULTS[tier]

    def test_perf_12_tier_rate_limits_data_driven(self):
        """PERF-12: SPEC-1803 rate_limit_rpm restored at 300 RPM (data-driven)."""
        for tier in ["trial", "starter", "professional", "enterprise"]:
            assert TIER_DEFAULTS[tier]["rate_limit_rpm"] == 300

    def test_perf_14_multi_tenant_isolation_in_sse(self):
        """PERF-14: SSE connections tracked independently per tenant."""
        mgr = SSEConnectionManager()
        mgr.connect("tenant-a", "conv-1")
        mgr.connect("tenant-a", "conv-2")
        mgr.connect("tenant-b", "conv-3")

        assert mgr.get_active_count("tenant-a") == 2
        assert mgr.get_active_count("tenant-b") == 1
        assert mgr.get_active_count("tenant-c") == 0

        # Disconnect tenant-a doesn't affect tenant-b
        mgr.disconnect("tenant-a", "conv-1")
        assert mgr.get_active_count("tenant-a") == 1
        assert mgr.get_active_count("tenant-b") == 1

    def test_perf_15_noisy_neighbor_sse_enforcement(self):
        """PERF-15: Per-tenant max_concurrent SSE cap removed; global limit only."""
        mgr = SSEConnectionManager()
        # Per-tenant max_concurrent removed; SSE only enforces global limit
        for i in range(10):
            mgr.connect("noisy-starter", f"conv-{i}")

        # No per-tenant limit — can_connect still returns True (global limit not hit)
        assert mgr.can_connect("noisy-starter", "starter")

        # Other tenants also unaffected
        assert mgr.can_connect("other-tenant", "starter")
        assert mgr.can_connect("enterprise-tenant", "enterprise")

    async def test_perf_16_pipeline_budget_tracks_elapsed(self):
        """PERF-16: PipelineTimeoutBudget tracks per-stage elapsed time."""
        budget = PipelineTimeoutBudget(total_deadline_ms=5000)

        async def stage_50ms():
            await asyncio.sleep(0.05)
            return "done"

        result = await budget.execute_with_budget("test-stage", stage_50ms())
        assert result == "done"

        trace = budget.execution_trace()
        assert len(trace["stages"]) == 1
        assert trace["stages"][0]["stage"] == "test-stage"
        assert trace["stages"][0]["succeeded"] is True
        assert trace["stages"][0]["elapsed_ms"] >= 40  # At least 40ms (allowing timing jitter)

    async def test_perf_17_pipeline_budget_stage_timeout(self):
        """PERF-17: Stage exceeding its budget raises timeout error."""
        budget = PipelineTimeoutBudget(
            total_deadline_ms=5000,
            stage_budgets_ms={"slow-stage": 50},  # 50ms budget
        )

        async def slow_stage():
            await asyncio.sleep(1.0)  # Way over budget
            return "too slow"

        with pytest.raises((PipelineTimeoutError, asyncio.TimeoutError)):
            await budget.execute_with_budget("slow-stage", slow_stage())

    def test_perf_18_pipeline_deadline_constant(self):
        """PERF-18: Pipeline hard deadline is 30,000ms (production Azure OpenAI)."""
        assert PIPELINE_DEADLINE_MS == 30_000

    def test_perf_19_stage_budgets_reasonable(self):
        """PERF-19: Stage budgets accommodate real Azure OpenAI latency."""
        total = sum(STAGE_BUDGETS_MS.values())
        assert total == 43_000  # Stages can overlap (IC+KR parallel)
        assert PIPELINE_DEADLINE_MS == 30_000

    def test_perf_20_circuit_breaker_state_machine(self):
        """PERF-20: Circuit breaker transitions CLOSED -> OPEN -> HALF_OPEN."""
        cb = ServiceCircuitBreaker(
            service_name="test-cb",
            failure_threshold=3,
            window_seconds=60,
            recovery_seconds=0.05,  # 50ms for fast test
        )
        assert cb.state == CircuitBreakerState.CLOSED

        # Record failures to trip the breaker
        for _ in range(3):
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        # Wait for recovery window
        time.sleep(0.06)
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Success resets to CLOSED
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_perf_circuit_breaker_failure_in_half_open_reopens(self):
        """Circuit breaker failure in HALF_OPEN returns to OPEN."""
        cb = ServiceCircuitBreaker(
            service_name="test-reopen",
            failure_threshold=2,
            window_seconds=60,
            recovery_seconds=0.05,
        )

        # Trip the breaker
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        # Wait for HALF_OPEN
        time.sleep(0.06)
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Failure in HALF_OPEN reopens
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_perf_circuit_breaker_configs_correct(self):
        """Pre-configured circuit breaker settings match Decision #15."""
        assert "azure-openai" in CIRCUIT_BREAKER_CONFIGS
        assert "cosmos-db" in CIRCUIT_BREAKER_CONFIGS

        aoai = CIRCUIT_BREAKER_CONFIGS["azure-openai"]
        assert aoai["failure_threshold"] == 5
        assert aoai["window_seconds"] == 30

        cosmos = CIRCUIT_BREAKER_CONFIGS["cosmos-db"]
        assert cosmos["failure_threshold"] == 3
        assert cosmos["window_seconds"] == 15

    async def test_perf_call_with_breaker_open_raises(self):
        """call_with_breaker raises ServiceUnavailableError when breaker is OPEN."""
        cb = ServiceCircuitBreaker(
            service_name="test-open-svc",
            failure_threshold=1,
            window_seconds=60,
        )
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        # Use a future that would resolve — but breaker rejects before awaiting
        fut = asyncio.get_event_loop().create_future()
        fut.set_result("nope")

        with pytest.raises(ServiceUnavailableError):
            await call_with_breaker(cb, fut)

    def test_perf_registry_health_summary(self):
        """Circuit breaker registry provides health summary."""
        registry = ServiceCircuitBreakerRegistry()
        cb_a = ServiceCircuitBreaker(service_name="svc-a", failure_threshold=3, window_seconds=60)
        cb_b = ServiceCircuitBreaker(service_name="svc-b", failure_threshold=3, window_seconds=60)
        registry.register(cb_a)
        registry.register(cb_b)

        summary = registry.health_summary()
        assert "svc-a" in summary["services"]
        assert "svc-b" in summary["services"]
        assert summary["services"]["svc-a"]["state"] == "closed"


# ===========================================================================
# §9.3: Streaming & SSE Management (PERF-21 through PERF-30)
# ===========================================================================


class TestStreamingSSE:
    """PERF-21 through PERF-30: SSE streaming, buffering, and reconnection."""

    def test_perf_21_keepalive_interval_under_gateway_timeout(self):
        """PERF-21: Keepalive interval (15s) is under Azure App Gateway timeout (60s)."""
        assert KEEPALIVE_INTERVAL_SECONDS == 15
        assert KEEPALIVE_INTERVAL_SECONDS < 60  # Azure App Gateway timeout

    def test_perf_22_event_buffer_append_and_replay(self):
        """PERF-22: EventBuffer appends events and replays after a given ID."""
        buf = EventBuffer()

        seq1 = buf.append("event: token\ndata: Hello\n\n")
        seq2 = buf.append("event: token\ndata: World\n\n")
        seq3 = buf.append("event: done\ndata: {}\n\n")

        assert seq1 == 1
        assert seq2 == 2
        assert seq3 == 3

        # Replay after seq1 returns seq2 and seq3
        replayed = buf.replay_after(1)
        assert len(replayed) == 2

        # Replay after seq3 returns nothing
        replayed = buf.replay_after(3)
        assert len(replayed) == 0

    def test_perf_23_event_buffer_max_size(self):
        """PERF-23: EventBuffer trims to MAX_BUFFERED_EVENTS."""
        buf = EventBuffer()

        for i in range(MAX_BUFFERED_EVENTS + 50):
            buf.append(f"event: token\ndata: {i}\n\n")

        assert len(buf.events) == MAX_BUFFERED_EVENTS
        assert buf.last_sequence == MAX_BUFFERED_EVENTS + 50

    def test_perf_24_sse_connection_limits_per_tier_removed(self):
        """PERF-24: Per-tier SSE connection caps removed; global limit only."""
        mgr = SSEConnectionManager()

        # Per-tier max_concurrent removed; any number of connections allowed
        # up to the global limit (GLOBAL_SSE_MAX_CONNECTIONS)
        for i in range(15):
            assert mgr.can_connect("starter-t", "starter")
            mgr.connect("starter-t", f"conv-{i}")

        # Still allowed — no per-tenant cap
        assert mgr.can_connect("starter-t", "starter")

    def test_perf_25_buffer_expiry(self):
        """PERF-25: Event buffers expire after BUFFER_EXPIRY_SECONDS of inactivity."""
        assert BUFFER_EXPIRY_SECONDS == 300  # 5 minutes

        buf = EventBuffer()
        buf.append("test")
        # Manually set old activity timestamp
        buf.last_activity = time.monotonic() - BUFFER_EXPIRY_SECONDS - 1

        assert buf.is_expired is True

    def test_perf_26_cleanup_expired_buffers(self):
        """PERF-26: cleanup_expired_buffers removes stale buffers."""
        mgr = SSEConnectionManager()
        mgr.connect("t-1", "conv-active")
        mgr.connect("t-1", "conv-stale")

        # Make one buffer stale
        mgr._buffers["conv-stale"].last_activity = (
            time.monotonic() - BUFFER_EXPIRY_SECONDS - 1
        )

        removed = mgr.cleanup_expired_buffers()
        assert removed == 1
        assert "conv-active" in mgr._buffers
        assert "conv-stale" not in mgr._buffers

    def test_perf_27_reconnection_replay(self):
        """PERF-27: Reconnection replays missed events via Last-Event-ID."""
        mgr = SSEConnectionManager()
        mgr.connect("t-1", "conv-1")

        # Buffer some events
        buf = mgr._buffers["conv-1"]
        seq1 = buf.append("event: token\ndata: A\n\n")
        seq2 = buf.append("event: token\ndata: B\n\n")
        seq3 = buf.append("event: done\ndata: {}\n\n")

        # Client disconnects and reconnects with Last-Event-ID = seq1
        events = mgr.get_replay_events("conv-1", seq1)
        assert len(events) == 2  # B and done

        # Unknown conversation returns empty
        events = mgr.get_replay_events("unknown-conv", 0)
        assert len(events) == 0

    def test_perf_28_sse_health_summary(self):
        """PERF-28: SSE health summary reports correct counts."""
        mgr = SSEConnectionManager()
        mgr.connect("t-1", "conv-1")
        mgr.connect("t-1", "conv-2")
        mgr.connect("t-2", "conv-3")

        summary = mgr.health_summary()
        assert summary["active_connections"] == 3
        assert summary["tenants_streaming"] == 2
        assert summary["event_buffers"] == 3

    def test_perf_29_disconnect_cleanup(self):
        """PERF-29: Disconnecting all conversations removes tenant from tracking."""
        mgr = SSEConnectionManager()
        mgr.connect("t-1", "conv-1")
        mgr.connect("t-1", "conv-2")

        mgr.disconnect("t-1", "conv-1")
        assert mgr.get_active_count("t-1") == 1

        mgr.disconnect("t-1", "conv-2")
        assert mgr.get_active_count("t-1") == 0
        assert "t-1" not in mgr._connections  # Cleaned up

    def test_perf_30_sla_targets_match_contract(self):
        """PERF-30: SLA targets match documented contractual values."""
        # Verify SLA targets match the commitments in CLAUDE.md
        for tier in ["starter", "professional", "enterprise"]:
            targets = SLA_TARGETS[tier]
            assert targets["p50_ms"] == 1500
            assert targets["p95_ms"] == 2000
            assert targets["p99_ms"] == 5000

        # Tier-specific uptime
        assert SLA_TARGETS["starter"]["uptime_pct"] == 99.5
        assert SLA_TARGETS["professional"]["uptime_pct"] == 99.9
        assert SLA_TARGETS["enterprise"]["uptime_pct"] == 99.95

        # RTO
        assert SLA_TARGETS["starter"]["rto_hours"] == 24
        assert SLA_TARGETS["professional"]["rto_hours"] == 8
        assert SLA_TARGETS["enterprise"]["rto_hours"] == 4


# ===========================================================================
# Cost Model Validation (supplements §9 — validates cost projections)
# ===========================================================================


class TestCostModelPerformance:
    """Cost model calculations are pure math — validate accuracy."""

    def test_cost_model_per_conversation_ai_cost(self):
        """AI cost per conversation matches documented $0.0073."""
        from src.multi_tenant.cost_model import AI_COST_PER_CONVERSATION
        assert abs(AI_COST_PER_CONVERSATION - 0.0073) < 0.001

    def test_cost_model_tier_pricing(self):
        """Tier pricing matches documented rates."""
        from src.multi_tenant.cost_model import TIER_PRICING

        assert TIER_PRICING["starter"]["monthly_fee"] == 149
        assert TIER_PRICING["professional"]["monthly_fee"] == 399
        assert TIER_PRICING["enterprise"]["monthly_fee"] == 999

    def test_cost_model_overage_rates(self):
        """Overage rates match documented rates."""
        from src.multi_tenant.cost_model import TIER_PRICING

        assert TIER_PRICING["starter"]["overage_rate"] == 0.04
        assert TIER_PRICING["professional"]["overage_rate"] == 0.025
        assert TIER_PRICING["enterprise"]["overage_rate"] == 0.015

    def test_cost_model_included_conversations(self):
        """Included conversation allowances match documented values."""
        from src.multi_tenant.cost_model import TIER_PRICING

        assert TIER_PRICING["starter"]["included_conversations"] == 1000
        assert TIER_PRICING["professional"]["included_conversations"] == 5000
        assert TIER_PRICING["enterprise"]["included_conversations"] == 20000

    def test_cost_model_margin_positive(self):
        """Gross margin is positive for all tiers at included volume."""
        from src.multi_tenant.cost_model import CostModelCalculator, TIER_PRICING

        calc = CostModelCalculator()
        for tier in ["starter", "professional", "enterprise"]:
            included = TIER_PRICING[tier]["included_conversations"]
            result = calc.project_tenant(tier, conversations_per_month=included)
            assert result.gross_margin_pct > 50, (
                f"{tier} margin {result.gross_margin_pct}% is below 50%"
            )
