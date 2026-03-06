"""Tests for RedisRateLimitBackend — SPEC-1626 distributed rate limiting.

Covers:
    - Sliding window rate limiting via Redis sorted sets
    - Atomic pipeline operations (ZREMRANGEBYSCORE + ZCARD + ZADD)
    - Key expiry (TTL auto-cleanup)
    - Reset (key deletion)
    - Cleanup (no-op — Redis TTL handles expiry)
    - Health check (ping)
    - Backend swap via set_rate_limit_backend()
    - Startup wiring (_startup_redis_rate_limiter)

Uses fakeredis for isolated, in-process testing without a real Redis server.

Module under test: src/multi_tenant/security_hardening.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
import time
from unittest.mock import MagicMock, patch

import pytest

from src.multi_tenant.security_hardening import (
    InMemoryRateLimitBackend,
    RedisRateLimitBackend,
    get_rate_limit_backend,
    set_rate_limit_backend,
)


# ---------------------------------------------------------------------------
# Fake Redis client for testing (no external dependency on fakeredis)
# ---------------------------------------------------------------------------

class FakeRedisPipeline:
    """Minimal fake Redis pipeline that supports sorted set operations."""

    def __init__(self, store: dict):
        self._store = store
        self._commands: list[tuple] = []

    def zremrangebyscore(self, key: str, min_score, max_score):
        self._commands.append(("zremrangebyscore", key, min_score, max_score))
        return self

    def zcard(self, key: str):
        self._commands.append(("zcard", key))
        return self

    def zadd(self, key: str, mapping: dict):
        self._commands.append(("zadd", key, mapping))
        return self

    def expire(self, key: str, seconds: int):
        self._commands.append(("expire", key, seconds))
        return self

    def execute(self) -> list:
        results = []
        for cmd in self._commands:
            op = cmd[0]
            key = cmd[1]

            if op == "zremrangebyscore":
                min_score = cmd[2]
                max_score = cmd[3]
                if key in self._store:
                    before = len(self._store[key])
                    self._store[key] = {
                        m: s for m, s in self._store[key].items()
                        if not (
                            (min_score == "-inf" or s >= float(min_score))
                            and s <= float(max_score)
                        )
                    }
                    results.append(before - len(self._store[key]))
                else:
                    results.append(0)

            elif op == "zcard":
                results.append(len(self._store.get(key, {})))

            elif op == "zadd":
                mapping = cmd[2]
                if key not in self._store:
                    self._store[key] = {}
                self._store[key].update(mapping)
                results.append(len(mapping))

            elif op == "expire":
                results.append(True)

        self._commands.clear()
        return results


class FakeRedisClient:
    """Minimal fake Redis client for unit testing."""

    def __init__(self):
        self._store: dict[str, dict] = {}

    def pipeline(self, transaction: bool = True):
        return FakeRedisPipeline(self._store)

    def delete(self, key: str):
        self._store.pop(key, None)

    def ping(self) -> bool:
        return True

    @classmethod
    def from_url(cls, url: str, **kwargs):
        return cls()


# ---------------------------------------------------------------------------
# RedisRateLimitBackend tests
# ---------------------------------------------------------------------------

class TestRedisRateLimitBackend:
    """Test the Redis-backed rate limit backend."""

    def setup_method(self):
        self.client = FakeRedisClient()
        self.backend = RedisRateLimitBackend(self.client, key_prefix="test:rl:")

    def test_first_request_not_limited(self):
        """First request within window should pass."""
        assert not self.backend.is_limited("key1", max_requests=3, window_seconds=60)

    def test_requests_within_limit_pass(self):
        """Requests under the max should all pass."""
        for _ in range(3):
            assert not self.backend.is_limited("key1", max_requests=3, window_seconds=60)

    def test_request_exceeding_limit_blocked(self):
        """Request exceeding max_requests should be blocked."""
        for _ in range(3):
            self.backend.is_limited("key1", max_requests=3, window_seconds=60)
        assert self.backend.is_limited("key1", max_requests=3, window_seconds=60)

    def test_different_keys_independent(self):
        """Rate limits are per-key — different keys don't interfere."""
        for _ in range(3):
            self.backend.is_limited("key1", max_requests=3, window_seconds=60)

        # key1 is now limited
        assert self.backend.is_limited("key1", max_requests=3, window_seconds=60)
        # key2 is still fresh
        assert not self.backend.is_limited("key2", max_requests=3, window_seconds=60)

    def test_expired_requests_cleared(self):
        """Requests outside the sliding window should be cleared."""
        # Manually insert old entries
        redis_key = "test:rl:key1"
        old_time = time.time() - 120  # 2 minutes ago
        self.client._store[redis_key] = {
            f"{old_time}:1": old_time,
            f"{old_time}:2": old_time,
            f"{old_time}:3": old_time,
        }

        # With a 60-second window, old entries should be cleaned up
        assert not self.backend.is_limited("key1", max_requests=3, window_seconds=60)

    def test_reset_clears_key(self):
        """Reset should remove all rate limit state for a key."""
        for _ in range(3):
            self.backend.is_limited("key1", max_requests=3, window_seconds=60)
        assert self.backend.is_limited("key1", max_requests=3, window_seconds=60)

        self.backend.reset("key1")
        assert not self.backend.is_limited("key1", max_requests=3, window_seconds=60)

    def test_cleanup_is_noop(self):
        """Cleanup should return 0 — Redis TTL handles expiry."""
        assert self.backend.cleanup() == 0

    def test_health_check_success(self):
        """Health check should return True when Redis is reachable."""
        assert self.backend.health_check() is True

    def test_health_check_failure(self):
        """Health check should return False when Redis is unreachable."""
        self.client.ping = MagicMock(side_effect=ConnectionError("refused"))
        assert self.backend.health_check() is False

    def test_key_prefix_applied(self):
        """Keys should be prefixed with the configured prefix."""
        self.backend.is_limited("mykey", max_requests=5, window_seconds=60)
        assert "test:rl:mykey" in self.client._store

    def test_custom_key_prefix(self):
        """Custom key prefix should work."""
        backend = RedisRateLimitBackend(self.client, key_prefix="prod:")
        backend.is_limited("test", max_requests=5, window_seconds=60)
        assert "prod:test" in self.client._store

    def test_sorted_set_members_unique(self):
        """Each request should create a unique sorted set member."""
        for _ in range(3):
            self.backend.is_limited("key1", max_requests=5, window_seconds=60)

        redis_key = "test:rl:key1"
        assert len(self.client._store[redis_key]) == 3


# ---------------------------------------------------------------------------
# Backend swap tests
# ---------------------------------------------------------------------------

class TestBackendSwap:
    """Test swapping between in-memory and Redis backends."""

    def teardown_method(self):
        # Reset to default after each test
        set_rate_limit_backend(InMemoryRateLimitBackend())

    def test_swap_to_redis_backend(self):
        """set_rate_limit_backend should swap the global backend."""
        client = FakeRedisClient()
        redis_backend = RedisRateLimitBackend(client)
        set_rate_limit_backend(redis_backend)

        backend = get_rate_limit_backend()
        assert isinstance(backend, RedisRateLimitBackend)

    def test_swap_back_to_in_memory(self):
        """Should be able to swap back to in-memory."""
        client = FakeRedisClient()
        set_rate_limit_backend(RedisRateLimitBackend(client))
        set_rate_limit_backend(InMemoryRateLimitBackend())

        backend = get_rate_limit_backend()
        assert isinstance(backend, InMemoryRateLimitBackend)


# ---------------------------------------------------------------------------
# Startup wiring tests
# ---------------------------------------------------------------------------

class TestStartupRedisRateLimiter:
    """Test the lifecycle startup handler for Redis rate limiter."""

    def teardown_method(self):
        set_rate_limit_backend(InMemoryRateLimitBackend())

    @pytest.mark.asyncio
    async def test_no_redis_url_uses_in_memory(self):
        """Without REDIS_URL, should stay with in-memory backend."""
        from src.app.lifecycle import _startup_redis_rate_limiter

        with patch.dict("os.environ", {}, clear=True):
            await _startup_redis_rate_limiter()

        backend = get_rate_limit_backend()
        assert isinstance(backend, InMemoryRateLimitBackend)

    @pytest.mark.asyncio
    async def test_redis_url_connects(self):
        """With REDIS_URL set and Redis reachable, should swap to Redis backend."""
        from src.app.lifecycle import _startup_redis_rate_limiter

        fake_client = FakeRedisClient()

        # Create a mock redis module since the real one may not be installed
        mock_redis_mod = MagicMock()
        mock_redis_mod.Redis.from_url.return_value = fake_client

        with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}), \
             patch.dict("sys.modules", {"redis": mock_redis_mod}):
            await _startup_redis_rate_limiter()

        backend = get_rate_limit_backend()
        assert isinstance(backend, RedisRateLimitBackend)

    @pytest.mark.asyncio
    async def test_redis_connection_failure_falls_back(self):
        """If Redis connection fails, should fall back to in-memory."""
        from src.app.lifecycle import _startup_redis_rate_limiter

        # Create a mock redis module that raises on from_url
        mock_redis_mod = MagicMock()
        mock_redis_mod.Redis.from_url.side_effect = ConnectionError("refused")

        with patch.dict("os.environ", {"REDIS_URL": "redis://bad-host:6379/0"}), \
             patch.dict("sys.modules", {"redis": mock_redis_mod}):
            await _startup_redis_rate_limiter()

        backend = get_rate_limit_backend()
        assert isinstance(backend, InMemoryRateLimitBackend)

    @pytest.mark.asyncio
    async def test_redis_import_error_falls_back(self):
        """If redis package not installed, should fall back silently."""
        from src.app.lifecycle import _startup_redis_rate_limiter

        with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}), \
             patch.dict("sys.modules", {"redis": None}), \
             patch("builtins.__import__", side_effect=ImportError("no redis")):
            # The startup handler catches ImportError gracefully
            await _startup_redis_rate_limiter()

        backend = get_rate_limit_backend()
        assert isinstance(backend, InMemoryRateLimitBackend)
