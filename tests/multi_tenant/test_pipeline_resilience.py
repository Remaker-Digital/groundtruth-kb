"""Pipeline resilience tests — P1 pre-launch (§5.3).

Test IDs: PR-01 through PR-20.

Validates:
    - PipelineTimeoutBudget: 8,000ms hard deadline, per-stage budgets for all
      6 agents (IC 800ms, KR 1000ms, RG 3000ms, CR 800ms, ESC 1400ms, AN 800ms),
      PipelineTimeoutError on excess, StageResult tracking, execution trace
    - ServiceCircuitBreaker: Azure OpenAI (5/30s/15s) and Cosmos DB (3/15s/10s)
      configs, full state machine (CLOSED → OPEN → HALF_OPEN → CLOSED)
    - call_with_breaker(): success passthrough, OPEN rejection
    - ServiceCircuitBreakerRegistry: register, get, health_summary, reset_all
    - get_circuit_breaker_registry() singleton

Module under test: src/multi_tenant/pipeline_resilience.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock

import pytest

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
    _TenantGate,
    call_with_breaker,
    get_circuit_breaker_registry,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _fast_coroutine(result: str = "ok") -> str:
    """Coroutine that completes instantly."""
    return result


async def _slow_coroutine(delay_s: float) -> str:
    """Coroutine that takes a specific amount of time."""
    await asyncio.sleep(delay_s)
    return "slow_ok"


async def _failing_coroutine() -> None:
    """Coroutine that raises an exception."""
    raise RuntimeError("stage_failure")


# ===========================================================================
# PR-01 to PR-09: PipelineTimeoutBudget
# ===========================================================================


class TestPipelineTimeoutBudget:
    """PR-01 through PR-09: Timeout budget enforcement."""

    def test_pr_01_hard_deadline(self) -> None:
        """PR-01: PipelineTimeoutBudget defaults to 8,000ms hard deadline."""
        budget = PipelineTimeoutBudget()
        assert budget._total_deadline_ms == PIPELINE_DEADLINE_MS
        assert PIPELINE_DEADLINE_MS == 8_000

    def test_pr_02_ic_stage_budget(self) -> None:
        """PR-02: Intent-classifier stage budget is 800ms."""
        assert STAGE_BUDGETS_MS["intent-classifier"] == 800

    def test_pr_03_kr_stage_budget(self) -> None:
        """PR-03: Knowledge-retrieval stage budget is 1,000ms."""
        assert STAGE_BUDGETS_MS["knowledge-retrieval"] == 1_000

    def test_pr_04_rg_stage_budget(self) -> None:
        """PR-04: Response-generator stage budget is 3,000ms."""
        assert STAGE_BUDGETS_MS["response-generator"] == 3_000

    def test_pr_05_cr_stage_budget(self) -> None:
        """PR-05: Critic-supervisor stage budget is 800ms."""
        assert STAGE_BUDGETS_MS["critic-supervisor"] == 800

    def test_pr_06_esc_stage_budget(self) -> None:
        """PR-06: Escalation-handler stage budget is 1,400ms."""
        assert STAGE_BUDGETS_MS["escalation-handler"] == 1_400

    def test_pr_07_an_stage_budget(self) -> None:
        """PR-07: Analytics-collector stage budget is 800ms."""
        assert STAGE_BUDGETS_MS["analytics-collector"] == 800

    def test_pr_01_all_stages_sum(self) -> None:
        """PR-01 supplement: All stage budgets sum to 7,800ms (200ms headroom)."""
        total = sum(STAGE_BUDGETS_MS.values())
        assert total == 7_800
        assert total < PIPELINE_DEADLINE_MS

    @pytest.mark.asyncio
    async def test_pr_08_exceeding_total_raises(self) -> None:
        """PR-08: Exceeding total deadline raises PipelineTimeoutError."""
        # Create a budget with very short deadline
        budget = PipelineTimeoutBudget(
            total_deadline_ms=50,
            stage_budgets_ms={"stage-a": 100, "stage-b": 100},
        )

        # First stage takes long enough to exhaust the total budget
        with pytest.raises(PipelineTimeoutError) as exc_info:
            await budget.execute_with_budget("stage-a", _slow_coroutine(0.1))

        assert exc_info.value.stage == "stage-a"

    @pytest.mark.asyncio
    async def test_pr_08_expired_budget_immediate_reject(self) -> None:
        """PR-08 supplement: Already-expired budget rejects without executing."""
        budget = PipelineTimeoutBudget(total_deadline_ms=1)
        # Ensure the budget expires
        await asyncio.sleep(0.01)

        assert budget.is_expired

        coro = _fast_coroutine()
        with pytest.raises(PipelineTimeoutError) as exc_info:
            await budget.execute_with_budget("stage-late", coro)
        coro.close()

        assert exc_info.value.stage == "stage-late"
        assert exc_info.value.budget_ms == 0

    @pytest.mark.asyncio
    async def test_pr_09_stage_result_tracking(self) -> None:
        """PR-09: StageResult tracks per-stage duration and success/failure."""
        budget = PipelineTimeoutBudget()

        result = await budget.execute_with_budget(
            "intent-classifier", _fast_coroutine("classified"),
        )
        assert result == "classified"

        trace = budget.execution_trace()
        assert len(trace["stages"]) == 1

        stage = trace["stages"][0]
        assert stage["stage"] == "intent-classifier"
        assert stage["succeeded"] is True
        assert stage["elapsed_ms"] >= 0
        assert stage["budget_ms"] == 800
        assert stage["error"] is None

    @pytest.mark.asyncio
    async def test_pr_09_failed_stage_recorded(self) -> None:
        """PR-09 supplement: Failed stages are recorded in the trace."""
        budget = PipelineTimeoutBudget()

        with pytest.raises(RuntimeError, match="stage_failure"):
            await budget.execute_with_budget(
                "response-generator", _failing_coroutine(),
            )

        trace = budget.execution_trace()
        assert len(trace["stages"]) == 1

        stage = trace["stages"][0]
        assert stage["stage"] == "response-generator"
        assert stage["succeeded"] is False
        assert "stage_failure" in stage["error"]

    @pytest.mark.asyncio
    async def test_pr_09_multiple_stages(self) -> None:
        """PR-09 supplement: Multiple stages tracked sequentially in trace."""
        budget = PipelineTimeoutBudget()

        await budget.execute_with_budget("intent-classifier", _fast_coroutine())
        await budget.execute_with_budget("knowledge-retrieval", _fast_coroutine())
        await budget.execute_with_budget("response-generator", _fast_coroutine())

        trace = budget.execution_trace()
        assert len(trace["stages"]) == 3
        assert trace["stages"][0]["stage"] == "intent-classifier"
        assert trace["stages"][1]["stage"] == "knowledge-retrieval"
        assert trace["stages"][2]["stage"] == "response-generator"
        assert trace["total_deadline_ms"] == PIPELINE_DEADLINE_MS
        assert trace["remaining_ms"] > 0
        assert trace["is_expired"] is False

    def test_remaining_ms(self) -> None:
        """Supplement: remaining_ms decreases from total deadline."""
        budget = PipelineTimeoutBudget()
        assert budget.remaining_ms <= PIPELINE_DEADLINE_MS
        assert budget.remaining_ms > 0
        assert budget.elapsed_ms >= 0


# ===========================================================================
# PR-10 to PR-14: ServiceCircuitBreaker
# ===========================================================================


class TestServiceCircuitBreaker:
    """PR-10 through PR-14: Circuit breaker state machine and configs."""

    def test_pr_10_azure_openai_config(self) -> None:
        """PR-10: Azure OpenAI breaker config: 5 failures/30s, 15s recovery."""
        config = CIRCUIT_BREAKER_CONFIGS["azure-openai"]
        assert config["failure_threshold"] == 5
        assert config["window_seconds"] == 30
        assert config["recovery_seconds"] == 15

    def test_pr_11_cosmos_db_config(self) -> None:
        """PR-11: Cosmos DB breaker config: 3 failures/15s, 10s recovery."""
        config = CIRCUIT_BREAKER_CONFIGS["cosmos-db"]
        assert config["failure_threshold"] == 3
        assert config["window_seconds"] == 15
        assert config["recovery_seconds"] == 10

    def test_pr_11_nats_config(self) -> None:
        """PR-11 supplement: NATS breaker config: 3 failures/10s, 5s recovery."""
        config = CIRCUIT_BREAKER_CONFIGS["nats"]
        assert config["failure_threshold"] == 3
        assert config["window_seconds"] == 10
        assert config["recovery_seconds"] == 5

    def test_pr_12_closed_to_open(self) -> None:
        """PR-12: CLOSED → OPEN when failures reach threshold within window."""
        breaker = ServiceCircuitBreaker(
            service_name="test-service",
            failure_threshold=3,
            window_seconds=10,
            recovery_seconds=5,
        )
        assert breaker.state == CircuitBreakerState.CLOSED

        for _ in range(3):
            breaker.record_failure()

        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.is_open

    def test_pr_12_fewer_failures_stay_closed(self) -> None:
        """PR-12 supplement: Fewer than threshold failures keeps CLOSED."""
        breaker = ServiceCircuitBreaker(
            service_name="test",
            failure_threshold=5,
        )
        for _ in range(4):
            breaker.record_failure()

        assert breaker.state == CircuitBreakerState.CLOSED

    def test_pr_13_open_to_half_open(self) -> None:
        """PR-13: OPEN → HALF_OPEN after recovery_seconds elapsed."""
        breaker = ServiceCircuitBreaker(
            service_name="test",
            failure_threshold=2,
            recovery_seconds=5,
        )

        # Trip the breaker
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN

        # Simulate recovery time passing
        breaker._opened_at = time.monotonic() - 6
        assert breaker.state == CircuitBreakerState.HALF_OPEN

    def test_pr_14_half_open_to_closed(self) -> None:
        """PR-14: HALF_OPEN → CLOSED on success."""
        breaker = ServiceCircuitBreaker(
            service_name="test",
            failure_threshold=2,
            recovery_seconds=5,
        )
        breaker.record_failure()
        breaker.record_failure()
        breaker._opened_at = time.monotonic() - 6
        assert breaker.state == CircuitBreakerState.HALF_OPEN

        breaker.record_success()
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.is_closed

    def test_pr_14_half_open_failure_reopens(self) -> None:
        """PR-14 supplement: HALF_OPEN → OPEN on failure."""
        breaker = ServiceCircuitBreaker(
            service_name="test",
            failure_threshold=2,
            recovery_seconds=5,
        )
        breaker.record_failure()
        breaker.record_failure()
        breaker._opened_at = time.monotonic() - 6
        assert breaker.state == CircuitBreakerState.HALF_OPEN

        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN

    def test_status_report(self) -> None:
        """Supplement: status() returns monitoring data."""
        breaker = ServiceCircuitBreaker(
            service_name="azure-openai",
            failure_threshold=5,
            window_seconds=30,
            recovery_seconds=15,
        )
        breaker.record_success()
        breaker.record_failure()

        status = breaker.status()
        assert status["service"] == "azure-openai"
        assert status["state"] == "closed"
        assert status["failure_threshold"] == 5
        assert status["total_successes"] == 1
        assert status["total_failures"] == 1
        assert status["recent_failures"] == 1

    def test_reset(self) -> None:
        """Supplement: reset() returns breaker to CLOSED."""
        breaker = ServiceCircuitBreaker("test", failure_threshold=1)
        breaker.record_failure()
        assert breaker.is_open

        breaker.reset()
        assert breaker.is_closed
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_total_opens_tracked(self) -> None:
        """Supplement: total_opens increments each time breaker opens."""
        breaker = ServiceCircuitBreaker("test", failure_threshold=2, recovery_seconds=0.001)
        assert breaker._total_opens == 0

        # First open
        breaker.record_failure()
        breaker.record_failure()
        assert breaker._total_opens == 1

        # Recover and open again
        breaker.record_success()
        breaker.record_failure()
        breaker.record_failure()
        assert breaker._total_opens == 2


# ===========================================================================
# PR-15 to PR-16: call_with_breaker()
# ===========================================================================


class TestCallWithBreaker:
    """PR-15 and PR-16: Protected call helper."""

    @pytest.mark.asyncio
    async def test_pr_15_success_passes_through(self) -> None:
        """PR-15: call_with_breaker passes through on success."""
        breaker = ServiceCircuitBreaker("test", failure_threshold=5)

        result = await call_with_breaker(breaker, _fast_coroutine("success"))

        assert result == "success"
        assert breaker._total_successes == 1

    @pytest.mark.asyncio
    async def test_pr_15_failure_recorded(self) -> None:
        """PR-15 supplement: Failure in coroutine is recorded on breaker."""
        breaker = ServiceCircuitBreaker("test", failure_threshold=5)

        with pytest.raises(RuntimeError, match="stage_failure"):
            await call_with_breaker(breaker, _failing_coroutine())

        assert breaker._total_failures == 1

    @pytest.mark.asyncio
    async def test_pr_16_open_raises_unavailable(self) -> None:
        """PR-16: call_with_breaker raises ServiceUnavailableError when OPEN."""
        breaker = ServiceCircuitBreaker("test-svc", failure_threshold=1)
        breaker.record_failure()
        assert breaker.is_open

        coro = _fast_coroutine()
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await call_with_breaker(breaker, coro)
        coro.close()

        assert exc_info.value.service_name == "test-svc"


# ===========================================================================
# PR-17 to PR-20: ServiceCircuitBreakerRegistry
# ===========================================================================


class TestCircuitBreakerRegistry:
    """PR-17 through PR-20: Registry management."""

    def test_pr_17_named_breaker_management(self) -> None:
        """PR-17: Register and retrieve named breakers."""
        registry = ServiceCircuitBreakerRegistry()
        breaker = ServiceCircuitBreaker("my-service", failure_threshold=3)

        registry.register(breaker)

        retrieved = registry.get("my-service")
        assert retrieved is breaker
        assert "my-service" in registry.service_names

    def test_pr_17_get_missing_returns_none(self) -> None:
        """PR-17 supplement: get() for unknown service returns None."""
        registry = ServiceCircuitBreakerRegistry()
        assert registry.get("nonexistent") is None

    def test_pr_17_register_defaults(self) -> None:
        """PR-17 supplement: register_defaults() creates all configured breakers."""
        registry = ServiceCircuitBreakerRegistry()
        registry.register_defaults()

        for service_name in CIRCUIT_BREAKER_CONFIGS:
            breaker = registry.get(service_name)
            assert breaker is not None
            assert breaker.service_name == service_name

    def test_pr_18_health_summary(self) -> None:
        """PR-18: health_summary() reports overall and per-service status."""
        registry = ServiceCircuitBreakerRegistry()
        registry.register_defaults()

        health = registry.health_summary()

        assert health["healthy"] is True
        assert health["any_open"] is False
        assert "azure-openai" in health["services"]
        assert "cosmos-db" in health["services"]
        assert health["services"]["azure-openai"]["state"] == "closed"

    def test_pr_18_health_summary_with_open(self) -> None:
        """PR-18 supplement: health_summary reflects OPEN breakers."""
        registry = ServiceCircuitBreakerRegistry()
        breaker = ServiceCircuitBreaker("failing-svc", failure_threshold=1)
        breaker.record_failure()
        registry.register(breaker)

        health = registry.health_summary()

        assert health["healthy"] is False
        assert health["any_open"] is True
        assert health["services"]["failing-svc"]["state"] == "open"

    def test_pr_19_reset_all(self) -> None:
        """PR-19: reset_all() returns all breakers to CLOSED."""
        registry = ServiceCircuitBreakerRegistry()
        for name in ("svc-a", "svc-b"):
            b = ServiceCircuitBreaker(name, failure_threshold=1)
            b.record_failure()
            registry.register(b)

        # Verify both are open
        assert registry.get("svc-a").is_open
        assert registry.get("svc-b").is_open

        registry.reset_all()

        assert registry.get("svc-a").is_closed
        assert registry.get("svc-b").is_closed
        assert registry.health_summary()["healthy"] is True

    def test_pr_20_singleton(self) -> None:
        """PR-20: get_circuit_breaker_registry() returns consistent singleton."""
        import src.multi_tenant.pipeline_resilience as mod

        original = mod._registry
        try:
            mod._registry = None
            reg1 = get_circuit_breaker_registry()
            reg2 = get_circuit_breaker_registry()
            assert reg1 is reg2
            # Defaults should be registered
            assert len(reg1.service_names) == len(CIRCUIT_BREAKER_CONFIGS)
        finally:
            mod._registry = original


# ===========================================================================
# Supplement: _TenantGate concurrency control
# ===========================================================================


class TestTenantGate:
    """Supplement: _TenantGate concurrency and queue depth."""

    @pytest.mark.asyncio
    async def test_acquire_release(self) -> None:
        """Basic acquire and release cycle."""
        gate = _TenantGate(max_concurrent=2, queue_depth=3)
        assert gate.active == 0
        assert gate.waiting == 0

        acquired = await gate.acquire()
        assert acquired is True
        assert gate.active == 1

        gate.release()
        assert gate.active == 0

    @pytest.mark.asyncio
    async def test_is_full_when_queue_exhausted(self) -> None:
        """Gate reports full when queue depth is reached."""
        gate = _TenantGate(max_concurrent=1, queue_depth=0)

        # Acquire the only slot
        await gate.acquire()
        assert gate.active == 1

        # Now the semaphore is locked and queue_depth is 0
        assert gate.is_full is True

    @pytest.mark.asyncio
    async def test_multiple_concurrent(self) -> None:
        """Multiple acquisitions up to max_concurrent succeed."""
        gate = _TenantGate(max_concurrent=3, queue_depth=5)

        for _ in range(3):
            ok = await gate.acquire()
            assert ok is True

        assert gate.active == 3
