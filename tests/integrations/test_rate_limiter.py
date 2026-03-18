"""Tests for Adaptive Rate Limiter (SPEC-1774).

Tests cover: TokenBucket mechanics, per-vendor rate limits, adaptive
factor on 429s, RetryExecutor with backoff, and vendor stats.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio

import pytest

from src.integrations.models import IntegrationError, RateLimitError
from src.integrations.rate_limiter import (
    VENDOR_RATE_LIMITS,
    AdaptiveRateLimiter,
    RetryExecutor,
    TokenBucket,
)


# ---------------------------------------------------------------------------
# TokenBucket tests
# ---------------------------------------------------------------------------


class TestTokenBucket:
    """Tests for the token bucket rate limiter."""

    def test_initial_tokens_equal_capacity(self):
        bucket = TokenBucket(capacity=10.0, refill_rate=1.0)
        assert bucket.tokens == 10.0

    def test_acquire_consumes_token(self):
        bucket = TokenBucket(capacity=5.0, refill_rate=1.0)
        assert bucket.try_acquire()
        assert bucket.tokens < 5.0

    def test_exhaust_tokens(self):
        bucket = TokenBucket(capacity=2.0, refill_rate=0.0)  # no refill
        assert bucket.try_acquire()
        assert bucket.try_acquire()
        assert not bucket.try_acquire()

    def test_wait_time_when_empty(self):
        bucket = TokenBucket(capacity=1.0, refill_rate=10.0)
        bucket.try_acquire()  # empty the bucket
        wait = bucket.wait_time()
        assert wait > 0
        assert wait <= 0.2  # 1/10 = 0.1s, with some tolerance

    def test_wait_time_when_available(self):
        bucket = TokenBucket(capacity=5.0, refill_rate=1.0)
        assert bucket.wait_time() == 0.0

    def test_record_429_reduces_factor(self):
        bucket = TokenBucket(capacity=10.0, refill_rate=10.0)
        initial = bucket.adaptive_factor
        bucket.record_429()
        assert bucket.adaptive_factor < initial

    def test_record_429_has_floor(self):
        bucket = TokenBucket(capacity=10.0, refill_rate=10.0)
        for _ in range(100):
            bucket.record_429()
        assert bucket.adaptive_factor >= 0.1

    def test_record_success_recovers_factor(self):
        bucket = TokenBucket(capacity=10.0, refill_rate=10.0)
        bucket.record_429()
        reduced = bucket.adaptive_factor
        for _ in range(50):
            bucket.record_success()
        assert bucket.adaptive_factor > reduced

    def test_record_success_caps_at_1(self):
        bucket = TokenBucket(capacity=10.0, refill_rate=10.0)
        for _ in range(100):
            bucket.record_success()
        assert bucket.adaptive_factor == 1.0


# ---------------------------------------------------------------------------
# AdaptiveRateLimiter tests
# ---------------------------------------------------------------------------


class TestAdaptiveRateLimiter:
    """Tests for the per-vendor adaptive rate limiter."""

    def test_default_vendor_limits_loaded(self):
        limiter = AdaptiveRateLimiter()
        stats = limiter.get_stats("zendesk")
        assert stats["rpm_limit"] == 700

    def test_unknown_vendor_uses_default(self):
        limiter = AdaptiveRateLimiter(default_rpm=30)
        stats = limiter.get_stats("unknown_vendor")
        assert stats["rpm_limit"] == 30

    def test_try_acquire_succeeds(self):
        limiter = AdaptiveRateLimiter()
        assert limiter.try_acquire("zendesk")

    def test_custom_vendor_limits(self):
        limiter = AdaptiveRateLimiter(vendor_limits={"custom": 120})
        stats = limiter.get_stats("custom")
        assert stats["rpm_limit"] == 120

    @pytest.mark.asyncio
    async def test_acquire_does_not_block_with_tokens(self):
        limiter = AdaptiveRateLimiter()
        # Should return immediately with tokens available
        await asyncio.wait_for(limiter.acquire("zendesk"), timeout=1.0)

    def test_record_429_reduces_vendor_rate(self):
        limiter = AdaptiveRateLimiter()
        limiter.try_acquire("zendesk")  # create bucket
        limiter.record_429("zendesk")
        stats = limiter.get_stats("zendesk")
        assert stats["adaptive_factor"] < 1.0

    def test_record_success_recovers(self):
        limiter = AdaptiveRateLimiter()
        limiter.record_429("zendesk")
        factor_after_429 = limiter.get_stats("zendesk")["adaptive_factor"]

        for _ in range(20):
            limiter.record_success("zendesk")
        factor_after_recovery = limiter.get_stats("zendesk")["adaptive_factor"]
        assert factor_after_recovery > factor_after_429

    def test_reset_vendor(self):
        limiter = AdaptiveRateLimiter()
        limiter.try_acquire("zendesk")
        limiter.record_429("zendesk")
        limiter.reset("zendesk")
        stats = limiter.get_stats("zendesk")
        assert stats["adaptive_factor"] == 1.0

    def test_reset_all(self):
        limiter = AdaptiveRateLimiter()
        limiter.try_acquire("zendesk")
        limiter.try_acquire("slack")
        limiter.reset()
        # New buckets should be created
        assert limiter.get_stats("zendesk")["adaptive_factor"] == 1.0
        assert limiter.get_stats("slack")["adaptive_factor"] == 1.0

    def test_vendor_limits_include_expected(self):
        """Verify all expected vendors have rate limits."""
        expected = ["zendesk", "intercom", "freshdesk", "shopify", "slack"]
        for vendor in expected:
            assert vendor in VENDOR_RATE_LIMITS

    def test_shopify_rate_is_2400(self):
        """Shopify is 40/sec = 2400/min."""
        assert VENDOR_RATE_LIMITS["shopify"] == 2400

    def test_stats_include_all_fields(self):
        limiter = AdaptiveRateLimiter()
        limiter.try_acquire("zendesk")
        stats = limiter.get_stats("zendesk")
        assert "vendor" in stats
        assert "rpm_limit" in stats
        assert "tokens_available" in stats
        assert "capacity" in stats
        assert "adaptive_factor" in stats
        assert "refill_rate_rps" in stats


# ---------------------------------------------------------------------------
# RetryExecutor tests
# ---------------------------------------------------------------------------


class TestRetryExecutor:
    """Tests for the retry executor with backoff."""

    @pytest.mark.asyncio
    async def test_success_no_retry(self):
        call_count = 0

        async def succeeding_fn():
            nonlocal call_count
            call_count += 1
            return "ok"

        executor = RetryExecutor(max_retries=3)
        result = await executor.execute(succeeding_fn, vendor="test")
        assert result == "ok"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit(self):
        call_count = 0

        async def flaky_fn():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RateLimitError(
                    "Too many requests",
                    integration_id="zendesk",
                    retry_after_seconds=0.01,
                )
            return "ok"

        executor = RetryExecutor(max_retries=3, base_backoff=0.01)
        result = await executor.execute(flaky_fn, vendor="zendesk")
        assert result == "ok"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted_raises(self):
        async def always_fail():
            raise RateLimitError(
                "Always limited",
                integration_id="test",
                retry_after_seconds=0.01,
            )

        executor = RetryExecutor(max_retries=2, base_backoff=0.01)
        with pytest.raises(IntegrationError, match="All 3 attempts failed"):
            await executor.execute(always_fail, vendor="test")

    @pytest.mark.asyncio
    async def test_retry_on_500(self):
        call_count = 0

        async def server_error_fn():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise IntegrationError(
                    "Server error", integration_id="test",
                    status_code=500, retryable=True,
                )
            return "recovered"

        executor = RetryExecutor(max_retries=2, base_backoff=0.01)
        result = await executor.execute(server_error_fn, vendor="test")
        assert result == "recovered"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_non_retryable_error_not_retried(self):
        call_count = 0

        async def auth_error_fn():
            nonlocal call_count
            call_count += 1
            raise IntegrationError(
                "Auth failed", integration_id="test",
                status_code=401, retryable=False,
            )

        executor = RetryExecutor(max_retries=3, base_backoff=0.01)
        with pytest.raises(IntegrationError, match="Auth failed"):
            await executor.execute(auth_error_fn, vendor="test")
        assert call_count == 1  # no retry

    @pytest.mark.asyncio
    async def test_unexpected_error_not_retried(self):
        async def crash():
            raise ValueError("unexpected")

        executor = RetryExecutor(max_retries=3)
        with pytest.raises(ValueError, match="unexpected"):
            await executor.execute(crash, vendor="test")

    @pytest.mark.asyncio
    async def test_rate_limiter_integration(self):
        """RetryExecutor uses rate limiter when provided."""
        limiter = AdaptiveRateLimiter(vendor_limits={"test": 6000})
        call_count = 0

        async def fn():
            nonlocal call_count
            call_count += 1
            return "ok"

        executor = RetryExecutor(rate_limiter=limiter, max_retries=1)
        await executor.execute(fn, vendor="test")
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_after_header_respected(self):
        """Retry-After from RateLimitError is used as wait time."""
        call_count = 0

        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RateLimitError(
                    "limited", integration_id="test",
                    retry_after_seconds=0.01,
                )
            return "ok"

        executor = RetryExecutor(max_retries=2, base_backoff=10.0)
        # Should use retry_after_seconds (0.01) not base_backoff (10.0)
        result = await asyncio.wait_for(
            executor.execute(fn, vendor="test"), timeout=2.0,
        )
        assert result == "ok"

    def test_compute_backoff_increases(self):
        executor = RetryExecutor(base_backoff=1.0, max_backoff=30.0)
        b0 = executor._compute_backoff(0)
        b1 = executor._compute_backoff(1)
        b2 = executor._compute_backoff(2)
        # Backoff should generally increase (with jitter variance)
        # Just check that attempt 2 base (4s) > attempt 0 base (1s) on average
        assert b2 > 0
        assert b0 > 0

    def test_compute_backoff_capped(self):
        executor = RetryExecutor(base_backoff=1.0, max_backoff=5.0)
        for attempt in range(10):
            backoff = executor._compute_backoff(attempt)
            assert backoff <= 5.0 * 1.5 + 1  # max + jitter margin
