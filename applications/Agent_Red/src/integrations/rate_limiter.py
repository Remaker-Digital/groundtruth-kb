# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Adaptive Rate Limiter for External APIs (SPEC-1774).

Outbound rate limiting to protect against 429 bans from external APIs.
Separate from inbound rate limiting (SPEC-1745 / tenant RPM limits).

Components:
1. AdaptiveRateLimiter — per-vendor token bucket with dynamic backoff
2. RetryExecutor — exponential backoff with jitter for retryable errors

Per-vendor defaults (RPM unless noted):
    Zendesk:   700/min
    Intercom:  1000/min
    Freshdesk: 50/min
    Shopify:   40/sec (= 2400/min)
    Slack:     50/min

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

from src.integrations.models import IntegrationError, RateLimitError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Per-vendor rate limit defaults (requests per minute)
# ---------------------------------------------------------------------------

VENDOR_RATE_LIMITS: dict[str, int] = {
    "zendesk": 700,
    "intercom": 1000,
    "freshdesk": 50,
    "shopify": 2400,   # 40/sec * 60
    "slack": 50,
    "google_docs": 300,
    "stripe": 100,
}

DEFAULT_RATE_LIMIT_RPM = 60  # conservative default for unknown vendors

# Retry configuration
MAX_RETRIES = 3
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
BASE_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0
JITTER_FACTOR = 0.5  # ±50% jitter


# ---------------------------------------------------------------------------
# Token Bucket
# ---------------------------------------------------------------------------


@dataclass
class TokenBucket:
    """Token bucket rate limiter.

    Tokens refill at a steady rate. Each request consumes one token.
    When tokens are exhausted, requests must wait.
    """

    capacity: float
    refill_rate: float  # tokens per second
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.monotonic)
    _adaptive_factor: float = 1.0  # reduced on 429s, recovered over time

    def __post_init__(self):
        self.tokens = self.capacity

    def _refill(self) -> None:
        """Add tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        effective_rate = self.refill_rate * self._adaptive_factor
        self.tokens = min(self.capacity, self.tokens + elapsed * effective_rate)
        self.last_refill = now

    def try_acquire(self) -> bool:
        """Try to acquire a token. Returns True if acquired."""
        self._refill()
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

    def wait_time(self) -> float:
        """Seconds to wait before a token is available."""
        self._refill()
        if self.tokens >= 1.0:
            return 0.0
        effective_rate = self.refill_rate * self._adaptive_factor
        if effective_rate <= 0:
            return MAX_BACKOFF_SECONDS
        deficit = 1.0 - self.tokens
        return deficit / effective_rate

    def record_429(self) -> None:
        """Reduce effective rate on receiving a 429 response."""
        self._adaptive_factor = max(0.1, self._adaptive_factor * 0.5)
        logger.warning(
            "Rate limiter adaptive factor reduced to %.2f",
            self._adaptive_factor,
        )

    def record_success(self) -> None:
        """Gradually recover rate after successful requests."""
        if self._adaptive_factor < 1.0:
            self._adaptive_factor = min(1.0, self._adaptive_factor * 1.05)

    @property
    def adaptive_factor(self) -> float:
        return self._adaptive_factor


# ---------------------------------------------------------------------------
# Adaptive Rate Limiter
# ---------------------------------------------------------------------------


class AdaptiveRateLimiter:
    """Per-vendor adaptive rate limiter using token buckets.

    Usage:
        limiter = AdaptiveRateLimiter()
        await limiter.acquire("zendesk")  # blocks until token available
        try:
            result = await call_zendesk_api()
            limiter.record_success("zendesk")
        except RateLimitError:
            limiter.record_429("zendesk")
            raise
    """

    def __init__(
        self,
        vendor_limits: dict[str, int] | None = None,
        default_rpm: int = DEFAULT_RATE_LIMIT_RPM,
    ) -> None:
        self._limits = vendor_limits or dict(VENDOR_RATE_LIMITS)
        self._default_rpm = default_rpm
        self._buckets: dict[str, TokenBucket] = {}

    def _get_bucket(self, vendor: str) -> TokenBucket:
        """Get or create a token bucket for a vendor."""
        if vendor not in self._buckets:
            rpm = self._limits.get(vendor, self._default_rpm)
            rps = rpm / 60.0
            # Burst capacity = 10% of per-minute limit (min 5)
            capacity = max(5.0, rpm * 0.1)
            self._buckets[vendor] = TokenBucket(
                capacity=capacity,
                refill_rate=rps,
            )
        return self._buckets[vendor]

    async def acquire(self, vendor: str) -> None:
        """Acquire a rate limit token, waiting if necessary."""
        bucket = self._get_bucket(vendor)

        if bucket.try_acquire():
            return

        wait = bucket.wait_time()
        if wait > 0:
            logger.debug(
                "Rate limiter: waiting %.2fs for %s token",
                wait, vendor,
            )
            await asyncio.sleep(wait)
            bucket.try_acquire()  # should succeed after waiting

    def try_acquire(self, vendor: str) -> bool:
        """Try to acquire a token without waiting."""
        return self._get_bucket(vendor).try_acquire()

    def record_429(self, vendor: str) -> None:
        """Record a 429 response — reduces effective rate."""
        self._get_bucket(vendor).record_429()

    def record_success(self, vendor: str) -> None:
        """Record a success — gradually recovers rate."""
        self._get_bucket(vendor).record_success()

    def get_stats(self, vendor: str) -> dict[str, Any]:
        """Get current rate limiter stats for a vendor."""
        bucket = self._get_bucket(vendor)
        bucket._refill()
        return {
            "vendor": vendor,
            "rpm_limit": self._limits.get(vendor, self._default_rpm),
            "tokens_available": round(bucket.tokens, 2),
            "capacity": bucket.capacity,
            "adaptive_factor": round(bucket.adaptive_factor, 3),
            "refill_rate_rps": round(bucket.refill_rate, 3),
        }

    def reset(self, vendor: str | None = None) -> None:
        """Reset rate limiter state. If vendor is None, reset all."""
        if vendor:
            self._buckets.pop(vendor, None)
        else:
            self._buckets.clear()


# ---------------------------------------------------------------------------
# Retry Executor
# ---------------------------------------------------------------------------


class RetryExecutor:
    """Executes async callables with retry logic for transient errors.

    Retries on: 429, 500, 502, 503, 504.
    Uses exponential backoff with jitter and respects Retry-After headers.
    """

    def __init__(
        self,
        rate_limiter: AdaptiveRateLimiter | None = None,
        *,
        max_retries: int = MAX_RETRIES,
        base_backoff: float = BASE_BACKOFF_SECONDS,
        max_backoff: float = MAX_BACKOFF_SECONDS,
    ) -> None:
        self._limiter = rate_limiter
        self._max_retries = max_retries
        self._base_backoff = base_backoff
        self._max_backoff = max_backoff

    async def execute(
        self,
        fn: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        vendor: str = "",
        **kwargs: Any,
    ) -> Any:
        """Execute an async function with retry logic.

        Args:
            fn: Async callable to execute.
            *args: Positional args for fn.
            vendor: Vendor name for rate limiting.
            **kwargs: Keyword args for fn.

        Returns:
            Result of fn.

        Raises:
            IntegrationError: After all retries exhausted.
        """
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            # Rate limit check
            if self._limiter and vendor:
                await self._limiter.acquire(vendor)

            try:
                result = await fn(*args, **kwargs)

                # Record success for adaptive rate limiting
                if self._limiter and vendor:
                    self._limiter.record_success(vendor)

                return result

            except RateLimitError as exc:
                last_error = exc
                if self._limiter and vendor:
                    self._limiter.record_429(vendor)

                if attempt >= self._max_retries:
                    break

                # Use Retry-After if available, otherwise backoff
                wait = exc.retry_after_seconds
                if wait <= 0:
                    wait = self._compute_backoff(attempt)

                logger.warning(
                    "Rate limited (429) on attempt %d/%d for %s, waiting %.1fs",
                    attempt + 1, self._max_retries + 1, vendor, wait,
                )
                await asyncio.sleep(wait)

            except IntegrationError as exc:
                last_error = exc
                if not exc.retryable or exc.status_code not in RETRYABLE_STATUS_CODES:
                    raise

                if attempt >= self._max_retries:
                    break

                wait = self._compute_backoff(attempt)
                logger.warning(
                    "Retryable error (status=%s) on attempt %d/%d for %s, waiting %.1fs",
                    exc.status_code, attempt + 1, self._max_retries + 1, vendor, wait,
                )
                await asyncio.sleep(wait)

            except Exception:
                # Non-retryable errors propagate immediately
                raise

        # All retries exhausted
        raise IntegrationError(
            f"All {self._max_retries + 1} attempts failed for {vendor}: {last_error}",
            integration_id=vendor,
            retryable=False,
        )

    def _compute_backoff(self, attempt: int) -> float:
        """Compute exponential backoff with jitter."""
        base = self._base_backoff * (2 ** attempt)
        capped = min(base, self._max_backoff)
        jitter = capped * JITTER_FACTOR * (2 * random.random() - 1)
        return max(0.1, capped + jitter)
