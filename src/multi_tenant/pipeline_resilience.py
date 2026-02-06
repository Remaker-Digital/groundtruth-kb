"""
Pipeline resilience — concurrency control, timeout orchestration, circuit breakers.

Implements Decisions #14-15 and Work Items #44-46. Provides the noisy-neighbor
prevention layer ensuring no single tenant can monopolize shared infrastructure.

1. TenantConcurrencyMiddleware (Decision #14, WI #44):
   Per-tenant concurrency limiter using asyncio.Semaphore with queue depth.
   Rejects requests with HTTP 429 when both the active slots and the
   waiting queue are full.

   Limits (from TIER_DEFAULTS):
       Starter:      3 concurrent,  5 queue
       Professional: 10 concurrent, 20 queue
       Enterprise:   30 concurrent, 50 queue

2. PipelineTimeoutBudget (Decision #15, WI #45):
   Layered timeout enforcement across the 6-agent pipeline. Each stage
   gets a fixed budget from the 8-second hard deadline:

       ┌──────────────────────────────────────────────────────────────┐
       │  8,000 ms total pipeline deadline                           │
       │  ┌─────┐ ┌──────┐ ┌──────────┐ ┌─────┐ ┌────────┐ ┌─────┐ │
       │  │ 800 │ │ 1000 │ │   3000   │ │ 800 │ │  1400  │ │ 800 │ │
       │  │ ms  │ │  ms  │ │    ms    │ │ ms  │ │   ms   │ │ ms  │ │
       │  │ IC  │ │  KR  │ │    RG    │ │ CR  │ │  ESC   │ │ AN  │ │
       │  └─────┘ └──────┘ └──────────┘ └─────┘ └────────┘ └─────┘ │
       │  Intent  Knowl.   Response     Critic  Escalation Analytics│
       └──────────────────────────────────────────────────────────────┘

   The budget tracker enforces wall-clock deadlines per stage and
   terminates processing if the total budget is exhausted.

3. ServiceCircuitBreaker (Decision #15, WI #46):
   Circuit breakers for external dependencies:
       - Azure OpenAI: 5 failures / 30s window, 15s recovery
       - Cosmos DB:    3 failures / 15s window, 10s recovery
       - NATS:         3 failures / 10s window,  5s recovery (already in nats_isolation.py)

   Registry pattern: ServiceCircuitBreakerRegistry manages named breakers
   and provides a global health summary.

Architecture references:
    - Decision #14: Per-tenant concurrency limits + queue depth
    - Decision #15: Layered timeouts + circuit breakers
    - Decision #16: Option B+ (min=2 replicas on 7 critical components)
    - TIER_DEFAULTS: max_concurrent, queue_depth per tier

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantTier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants — timeout budget (Decision #15)
# ---------------------------------------------------------------------------

# Total pipeline hard deadline (milliseconds)
# Decision #15 originally specified 8,000ms. Increased to 30,000ms for
# production Azure OpenAI latency (cold-start model endpoints can take
# 3-8s on first request). The SLA P95 target of 2,000ms is measured
# end-to-end at the HTTP layer, not at the pipeline budget layer.
PIPELINE_DEADLINE_MS = 30_000

# Per-stage timeout budgets (milliseconds)
# Increased from original Decision #15 values to accommodate real Azure
# OpenAI latency. Cold-start calls to GPT-4o-mini take 2-5s, GPT-4o
# streaming takes 3-10s. These budgets are generous to avoid false
# timeouts — actual SLA compliance is measured by sla_monitoring.py.
STAGE_BUDGETS_MS: dict[str, int] = {
    "intent-classifier":   5_000,
    "knowledge-retrieval": 10_000,
    "response-generator": 15_000,
    "critic-supervisor":   5_000,
    "escalation-handler":  5_000,
    "analytics-collector": 3_000,
}

# Circuit breaker configurations per service (Decision #15)
CIRCUIT_BREAKER_CONFIGS: dict[str, dict[str, int | float]] = {
    "azure-openai": {
        "failure_threshold": 5,
        "window_seconds": 30,
        "recovery_seconds": 15,
    },
    "cosmos-db": {
        "failure_threshold": 3,
        "window_seconds": 15,
        "recovery_seconds": 10,
    },
    # NATS circuit breaker is in nats_isolation.py (3/10s/5s)
    # Listed here for registry completeness but managed there
    "nats": {
        "failure_threshold": 3,
        "window_seconds": 10,
        "recovery_seconds": 5,
    },
}


# ---------------------------------------------------------------------------
# Per-tenant concurrency control (Decision #14, Work Item #44)
# ---------------------------------------------------------------------------


class _TenantGate:
    """Concurrency gate for a single tenant.

    Combines an asyncio.Semaphore (active slot limiter) with a counter
    for the waiting queue. When both active slots and queue slots are
    full, new requests are immediately rejected.
    """

    def __init__(self, max_concurrent: int, queue_depth: int) -> None:
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._max_concurrent = max_concurrent
        self._queue_depth = queue_depth
        self._waiting = 0
        self._active = 0

    @property
    def active(self) -> int:
        return self._active

    @property
    def waiting(self) -> int:
        return self._waiting

    @property
    def is_full(self) -> bool:
        """Whether both active and queue slots are exhausted."""
        return self._waiting >= self._queue_depth

    async def acquire(self) -> bool:
        """Try to acquire a concurrency slot.

        Returns True if acquired (caller must release). Returns False
        if the gate is full (caller should reject the request).
        """
        # Check if the queue is full before waiting
        if self._semaphore.locked() and self._waiting >= self._queue_depth:
            return False

        self._waiting += 1
        try:
            await self._semaphore.acquire()
        finally:
            self._waiting -= 1

        self._active += 1
        return True

    def release(self) -> None:
        """Release a concurrency slot."""
        self._active = max(0, self._active - 1)
        self._semaphore.release()


class TenantConcurrencyMiddleware(BaseHTTPMiddleware):
    """Per-tenant concurrency limiter (Decision #14).

    Enforces max_concurrent active requests and queue_depth waiting
    requests per tenant. When both are full, returns HTTP 429.

    Limits are read from TIER_DEFAULTS based on the tenant's tier,
    or from the TenantDocument.max_concurrent override if set.

    This middleware must be installed AFTER TenantAuthMiddleware so
    that request.state.tenant_context is available.

    Usage:
        app.add_middleware(TenantConcurrencyMiddleware)
    """

    def __init__(self, app: Any, **kwargs: Any) -> None:
        super().__init__(app, **kwargs)
        # {tenant_id: _TenantGate}
        self._gates: dict[str, _TenantGate] = {}

    def _get_gate(self, ctx: TenantContext) -> _TenantGate:
        """Get or create the concurrency gate for a tenant."""
        if ctx.tenant_id in self._gates:
            return self._gates[ctx.tenant_id]

        # Determine limits from tier defaults
        tier_config = {}
        if ctx.tier:
            tier_config = TIER_DEFAULTS.get(ctx.tier.value, {})

        max_concurrent = tier_config.get("max_concurrent", 3)
        queue_depth = tier_config.get("queue_depth", 5)

        gate = _TenantGate(max_concurrent, queue_depth)
        self._gates[ctx.tenant_id] = gate
        return gate

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ) -> Response:
        # Only limit authenticated requests
        ctx: TenantContext | None = getattr(request.state, "tenant_context", None)
        if ctx is None:
            return await call_next(request)

        gate = self._get_gate(ctx)

        # Try to acquire a slot
        if gate.is_full:
            # Immediate rejection — both active and queue slots are exhausted
            logger.warning(
                "Concurrency limit exceeded: tenant=%s tier=%s "
                "active=%d waiting=%d",
                ctx.tenant_id, ctx.tier, gate.active, gate.waiting,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many concurrent requests.",
                    "active": gate.active,
                    "waiting": gate.waiting,
                    "retry_after": 2,
                },
                headers={"Retry-After": "2"},
            )

        acquired = await gate.acquire()
        if not acquired:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many concurrent requests.",
                    "retry_after": 2,
                },
                headers={"Retry-After": "2"},
            )

        try:
            return await call_next(request)
        finally:
            gate.release()

    def get_tenant_stats(self, tenant_id: str) -> dict[str, int] | None:
        """Get concurrency stats for a tenant (for monitoring)."""
        gate = self._gates.get(tenant_id)
        if gate is None:
            return None
        return {
            "active": gate.active,
            "waiting": gate.waiting,
        }


# ---------------------------------------------------------------------------
# Pipeline timeout budget (Decision #15, Work Item #45)
# ---------------------------------------------------------------------------


class PipelineTimeoutError(Exception):
    """Raised when a pipeline stage or the total deadline is exceeded."""

    def __init__(self, stage: str, budget_ms: int, elapsed_ms: float) -> None:
        self.stage = stage
        self.budget_ms = budget_ms
        self.elapsed_ms = elapsed_ms
        super().__init__(
            f"Timeout in {stage}: budget={budget_ms}ms, elapsed={elapsed_ms:.0f}ms"
        )


@dataclass
class StageResult:
    """Result of a single pipeline stage execution."""

    stage: str
    succeeded: bool
    elapsed_ms: float
    error: str | None = None


class PipelineTimeoutBudget:
    """Layered timeout enforcement across the 6-agent pipeline.

    Tracks wall-clock time consumed by each stage and enforces both
    per-stage budgets and the overall 8-second hard deadline.

    The budget is created once per conversation pipeline invocation
    and passed through the stages. Each stage calls execute_with_budget()
    which wraps the stage's async callable with asyncio.wait_for().

    Usage:
        budget = PipelineTimeoutBudget()

        # Execute each stage with its budget
        intent = await budget.execute_with_budget(
            "intent-classifier",
            classify_intent(message),
        )

        knowledge = await budget.execute_with_budget(
            "knowledge-retrieval",
            retrieve_knowledge(intent),
        )

        response = await budget.execute_with_budget(
            "response-generator",
            generate_response(knowledge),
        )

        # Check remaining budget
        remaining = budget.remaining_ms
        if remaining <= 0:
            # Pipeline deadline exceeded
            ...

        # Get execution trace
        trace = budget.execution_trace()
    """

    def __init__(
        self,
        total_deadline_ms: int = PIPELINE_DEADLINE_MS,
        stage_budgets_ms: dict[str, int] | None = None,
    ) -> None:
        self._total_deadline_ms = total_deadline_ms
        self._stage_budgets = stage_budgets_ms or STAGE_BUDGETS_MS
        self._start_time = time.monotonic()
        self._stage_results: list[StageResult] = []

    @property
    def elapsed_ms(self) -> float:
        """Total elapsed time since pipeline start."""
        return (time.monotonic() - self._start_time) * 1000

    @property
    def remaining_ms(self) -> float:
        """Remaining time before the hard deadline."""
        return max(0, self._total_deadline_ms - self.elapsed_ms)

    @property
    def is_expired(self) -> bool:
        """Whether the total pipeline deadline has been exceeded."""
        return self.remaining_ms <= 0

    @property
    def stages(self) -> list[StageResult]:
        """Public access to the recorded stage results."""
        return self._stage_results

    async def execute_with_budget(
        self,
        stage: str,
        coroutine: Any,
    ) -> Any:
        """Execute a pipeline stage with its timeout budget.

        Applies the lesser of the stage's budget or the remaining
        pipeline time as the timeout for asyncio.wait_for().

        Args:
            stage: Stage name (e.g., "intent-classifier").
            coroutine: The async callable to execute.

        Returns:
            The result of the coroutine.

        Raises:
            PipelineTimeoutError: If the stage or pipeline deadline is exceeded.
        """
        if self.is_expired:
            raise PipelineTimeoutError(
                stage=stage,
                budget_ms=0,
                elapsed_ms=self.elapsed_ms,
            )

        # Budget = min(stage budget, remaining pipeline time)
        stage_budget_ms = self._stage_budgets.get(stage, 1000)
        effective_budget_ms = min(stage_budget_ms, self.remaining_ms)
        effective_budget_s = effective_budget_ms / 1000

        stage_start = time.monotonic()

        try:
            result = await asyncio.wait_for(
                coroutine,
                timeout=effective_budget_s,
            )
            elapsed = (time.monotonic() - stage_start) * 1000

            self._stage_results.append(StageResult(
                stage=stage,
                succeeded=True,
                elapsed_ms=elapsed,
            ))

            logger.debug(
                "Pipeline stage complete: stage=%s elapsed=%.0fms budget=%dms",
                stage, elapsed, stage_budget_ms,
            )

            return result

        except asyncio.TimeoutError:
            elapsed = (time.monotonic() - stage_start) * 1000

            self._stage_results.append(StageResult(
                stage=stage,
                succeeded=False,
                elapsed_ms=elapsed,
                error="timeout",
            ))

            logger.warning(
                "Pipeline stage timeout: stage=%s elapsed=%.0fms budget=%dms "
                "total_elapsed=%.0fms",
                stage, elapsed, stage_budget_ms, self.elapsed_ms,
            )

            raise PipelineTimeoutError(
                stage=stage,
                budget_ms=int(effective_budget_ms),
                elapsed_ms=elapsed,
            ) from None

        except Exception as exc:
            elapsed = (time.monotonic() - stage_start) * 1000

            self._stage_results.append(StageResult(
                stage=stage,
                succeeded=False,
                elapsed_ms=elapsed,
                error=str(exc),
            ))

            raise

    def execution_trace(self) -> dict[str, Any]:
        """Get the full execution trace for this pipeline invocation.

        Useful for the response explainability framework (Decision #28)
        and operational debugging.

        Returns:
            Dict with total elapsed, remaining, and per-stage details.
        """
        return {
            "total_elapsed_ms": round(self.elapsed_ms, 1),
            "total_deadline_ms": self._total_deadline_ms,
            "remaining_ms": round(self.remaining_ms, 1),
            "is_expired": self.is_expired,
            "stages": [
                {
                    "stage": r.stage,
                    "succeeded": r.succeeded,
                    "elapsed_ms": round(r.elapsed_ms, 1),
                    "budget_ms": self._stage_budgets.get(r.stage, 0),
                    "error": r.error,
                }
                for r in self._stage_results
            ],
        }


# ---------------------------------------------------------------------------
# Service circuit breaker (Decision #15, Work Item #46)
# ---------------------------------------------------------------------------


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ServiceCircuitBreaker:
    """Circuit breaker for an external service dependency.

    Tracks failure/success rates and opens the circuit when failures
    exceed the threshold within the time window. When open, all calls
    are immediately rejected without attempting the service.

    State machine:
        CLOSED    → (failures >= threshold in window) → OPEN
        OPEN      → (recovery_seconds elapsed)        → HALF_OPEN
        HALF_OPEN → (next call succeeds)              → CLOSED
        HALF_OPEN → (next call fails)                 → OPEN

    Usage:
        breaker = ServiceCircuitBreaker(
            service_name="azure-openai",
            failure_threshold=5,
            window_seconds=30,
            recovery_seconds=15,
        )

        if breaker.is_open:
            raise ServiceUnavailableError("azure-openai circuit breaker open")

        try:
            result = await call_openai(prompt)
            breaker.record_success()
        except Exception:
            breaker.record_failure()
            raise
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        window_seconds: float = 30,
        recovery_seconds: float = 15,
    ) -> None:
        self.service_name = service_name
        self._failure_threshold = failure_threshold
        self._window_seconds = window_seconds
        self._recovery_seconds = recovery_seconds
        self._state = CircuitBreakerState.CLOSED
        self._failures: list[float] = []
        self._opened_at: float | None = None
        self._total_opens = 0
        self._total_failures = 0
        self._total_successes = 0

    @property
    def state(self) -> CircuitBreakerState:
        if self._state == CircuitBreakerState.OPEN:
            if (
                self._opened_at is not None
                and time.monotonic() - self._opened_at >= self._recovery_seconds
            ):
                self._state = CircuitBreakerState.HALF_OPEN
        return self._state

    @property
    def is_open(self) -> bool:
        return self.state == CircuitBreakerState.OPEN

    @property
    def is_closed(self) -> bool:
        return self.state == CircuitBreakerState.CLOSED

    def record_success(self) -> None:
        self._state = CircuitBreakerState.CLOSED
        self._failures.clear()
        self._opened_at = None
        self._total_successes += 1

    def record_failure(self) -> None:
        now = time.monotonic()
        self._failures.append(now)
        self._total_failures += 1

        # Prune old failures outside the window
        cutoff = now - self._window_seconds
        self._failures = [t for t in self._failures if t > cutoff]

        if len(self._failures) >= self._failure_threshold:
            if self._state != CircuitBreakerState.OPEN:
                self._total_opens += 1
            self._state = CircuitBreakerState.OPEN
            self._opened_at = now
            logger.warning(
                "%s circuit breaker OPENED: %d failures in %.0fs window "
                "(threshold=%d)",
                self.service_name, len(self._failures),
                self._window_seconds, self._failure_threshold,
            )

    def reset(self) -> None:
        """Force-reset to CLOSED (admin operation)."""
        self._state = CircuitBreakerState.CLOSED
        self._failures.clear()
        self._opened_at = None
        logger.info("%s circuit breaker manually reset to CLOSED", self.service_name)

    def status(self) -> dict[str, Any]:
        """Get circuit breaker status for monitoring."""
        return {
            "service": self.service_name,
            "state": self.state.value,
            "recent_failures": len(self._failures),
            "failure_threshold": self._failure_threshold,
            "window_seconds": self._window_seconds,
            "recovery_seconds": self._recovery_seconds,
            "total_opens": self._total_opens,
            "total_failures": self._total_failures,
            "total_successes": self._total_successes,
        }


# ---------------------------------------------------------------------------
# Circuit breaker registry
# ---------------------------------------------------------------------------


class ServiceCircuitBreakerRegistry:
    """Registry of circuit breakers for all external service dependencies.

    Provides centralized management and health reporting for circuit
    breakers. Initialized at application startup with breakers for
    each external dependency.

    Usage:
        registry = ServiceCircuitBreakerRegistry()
        registry.register_defaults()

        # Get a breaker
        openai_breaker = registry.get("azure-openai")
        if openai_breaker.is_open:
            # Fallback or reject

        # Health summary
        health = registry.health_summary()
    """

    def __init__(self) -> None:
        self._breakers: dict[str, ServiceCircuitBreaker] = {}

    def register(self, breaker: ServiceCircuitBreaker) -> None:
        """Register a circuit breaker."""
        self._breakers[breaker.service_name] = breaker
        logger.debug(
            "Circuit breaker registered: service=%s threshold=%d window=%.0fs",
            breaker.service_name, breaker._failure_threshold,
            breaker._window_seconds,
        )

    def get(self, service_name: str) -> ServiceCircuitBreaker | None:
        """Get a circuit breaker by service name."""
        return self._breakers.get(service_name)

    def register_defaults(self) -> None:
        """Register circuit breakers for all known external dependencies.

        Uses configurations from CIRCUIT_BREAKER_CONFIGS.
        """
        for service_name, config in CIRCUIT_BREAKER_CONFIGS.items():
            breaker = ServiceCircuitBreaker(
                service_name=service_name,
                failure_threshold=int(config["failure_threshold"]),
                window_seconds=float(config["window_seconds"]),
                recovery_seconds=float(config["recovery_seconds"]),
            )
            self.register(breaker)

        logger.info(
            "Default circuit breakers registered: %s",
            list(self._breakers.keys()),
        )

    def health_summary(self) -> dict[str, Any]:
        """Get health summary for all circuit breakers.

        Returns:
            Dict with overall health status and per-service detail.
        """
        all_closed = all(b.is_closed for b in self._breakers.values())
        any_open = any(b.is_open for b in self._breakers.values())

        return {
            "healthy": all_closed,
            "any_open": any_open,
            "services": {
                name: breaker.status()
                for name, breaker in self._breakers.items()
            },
        }

    def reset_all(self) -> None:
        """Force-reset all circuit breakers (admin operation)."""
        for breaker in self._breakers.values():
            breaker.reset()
        logger.info("All circuit breakers reset to CLOSED")

    @property
    def service_names(self) -> list[str]:
        """List registered service names."""
        return list(self._breakers.keys())


# ---------------------------------------------------------------------------
# Service unavailable error
# ---------------------------------------------------------------------------


class ServiceUnavailableError(Exception):
    """Raised when a service circuit breaker is open."""

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        super().__init__(
            f"Service {service_name} is unavailable (circuit breaker open)."
        )


# ---------------------------------------------------------------------------
# Protected call helper
# ---------------------------------------------------------------------------


async def call_with_breaker(
    breaker: ServiceCircuitBreaker,
    coroutine: Any,
) -> Any:
    """Execute an async call protected by a circuit breaker.

    Checks the breaker state before calling, records success/failure
    after, and raises ServiceUnavailableError if the circuit is open.

    Args:
        breaker: The circuit breaker for the target service.
        coroutine: The async callable to execute.

    Returns:
        The result of the coroutine.

    Raises:
        ServiceUnavailableError: If the circuit breaker is open.
        Any exception from the coroutine (after recording failure).
    """
    if breaker.is_open:
        raise ServiceUnavailableError(breaker.service_name)

    try:
        result = await coroutine
        breaker.record_success()
        return result
    except Exception:
        breaker.record_failure()
        raise


# ---------------------------------------------------------------------------
# Module-level singleton registry
# ---------------------------------------------------------------------------

_registry: ServiceCircuitBreakerRegistry | None = None


def get_circuit_breaker_registry() -> ServiceCircuitBreakerRegistry:
    """Get the module-level circuit breaker registry singleton."""
    global _registry
    if _registry is None:
        _registry = ServiceCircuitBreakerRegistry()
        _registry.register_defaults()
    return _registry


def get_circuit_breaker(service_name: str) -> ServiceCircuitBreaker | None:
    """Shortcut: get a specific circuit breaker from the global registry."""
    return get_circuit_breaker_registry().get(service_name)
