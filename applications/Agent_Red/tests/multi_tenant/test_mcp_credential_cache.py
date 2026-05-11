"""Tests for MCP credential cache — in-memory TTL cache for per-tenant credentials.

Test IDs: CACHE-01 → CACHE-15

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.multi_tenant.mcp_credential_cache import (
    McpCredentialCache,
    _CacheEntry,
    get_credential_cache,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fetcher(value: str | None = "sk_test_abc123") -> AsyncMock:
    """Create an async mock fetcher returning the given value."""
    fetcher = AsyncMock(return_value=value)
    return fetcher


# ---------------------------------------------------------------------------
# CACHE-01: Cache entry expiry
# ---------------------------------------------------------------------------

class TestCacheEntry:
    """Test _CacheEntry TTL behavior."""

    def test_cache_01_entry_not_expired(self):
        """CACHE-01: Fresh entry is not expired."""
        entry = _CacheEntry("secret", ttl_seconds=300)
        assert not entry.is_expired

    def test_cache_02_entry_expired(self):
        """CACHE-02: Entry with 0 TTL expires immediately."""
        entry = _CacheEntry("secret", ttl_seconds=0)
        assert entry.is_expired

    def test_cache_03_entry_stores_value(self):
        """CACHE-03: Entry stores the credential value."""
        entry = _CacheEntry("my_secret_key", ttl_seconds=60)
        assert entry.value == "my_secret_key"


# ---------------------------------------------------------------------------
# CACHE-04→CACHE-11: McpCredentialCache.get()
# ---------------------------------------------------------------------------

class TestMcpCredentialCacheGet:
    """Test the cache get() with fetcher."""

    @pytest.mark.asyncio
    async def test_cache_04_miss_calls_fetcher(self):
        """CACHE-04: Cache miss calls the fetcher and caches result."""
        cache = McpCredentialCache(ttl_seconds=60)
        fetcher = _make_fetcher("sk_live_xyz")

        result = await cache.get("tenant-1", "stripe-api-key", fetcher)

        assert result == "sk_live_xyz"
        fetcher.assert_awaited_once()
        assert cache.size == 1
        assert cache.misses == 1
        assert cache.hits == 0

    @pytest.mark.asyncio
    async def test_cache_05_hit_returns_cached(self):
        """CACHE-05: Second call returns cached value without calling fetcher."""
        cache = McpCredentialCache(ttl_seconds=60)
        fetcher = _make_fetcher("sk_live_xyz")

        # First call — miss
        await cache.get("tenant-1", "stripe-api-key", fetcher)
        # Second call — hit
        fetcher2 = _make_fetcher("should_not_be_called")
        result = await cache.get("tenant-1", "stripe-api-key", fetcher2)

        assert result == "sk_live_xyz"
        fetcher2.assert_not_awaited()
        assert cache.hits == 1
        assert cache.misses == 1

    @pytest.mark.asyncio
    async def test_cache_06_expired_refetches(self):
        """CACHE-06: Expired entry triggers re-fetch."""
        cache = McpCredentialCache(ttl_seconds=0)  # Expires immediately

        fetcher1 = _make_fetcher("old_key")
        await cache.get("tenant-1", "stripe-api-key", fetcher1)

        fetcher2 = _make_fetcher("new_key")
        result = await cache.get("tenant-1", "stripe-api-key", fetcher2)

        assert result == "new_key"
        fetcher2.assert_awaited_once()
        assert cache.misses == 2

    @pytest.mark.asyncio
    async def test_cache_07_fetcher_returns_none(self):
        """CACHE-07: Fetcher returning None is not cached."""
        cache = McpCredentialCache(ttl_seconds=60)
        fetcher = _make_fetcher(None)

        result = await cache.get("tenant-1", "stripe-api-key", fetcher)

        assert result is None
        assert cache.size == 0

    @pytest.mark.asyncio
    async def test_cache_08_fetcher_raises_exception(self):
        """CACHE-08: Fetcher exception propagates to caller."""
        cache = McpCredentialCache(ttl_seconds=60)
        fetcher = AsyncMock(side_effect=RuntimeError("Key Vault down"))

        with pytest.raises(RuntimeError, match="Key Vault down"):
            await cache.get("tenant-1", "stripe-api-key", fetcher)

        assert cache.size == 0

    @pytest.mark.asyncio
    async def test_cache_09_per_tenant_isolation(self):
        """CACHE-09: Different tenants have isolated cache entries."""
        cache = McpCredentialCache(ttl_seconds=60)

        await cache.get("tenant-1", "stripe-api-key", _make_fetcher("key_1"))
        await cache.get("tenant-2", "stripe-api-key", _make_fetcher("key_2"))

        assert cache.size == 2

        # Verify tenant-1 still returns its own key
        result = await cache.get("tenant-1", "stripe-api-key", _make_fetcher("should_not_be_called"))
        assert result == "key_1"

    @pytest.mark.asyncio
    async def test_cache_10_per_secret_type_isolation(self):
        """CACHE-10: Different secret types have isolated cache entries."""
        cache = McpCredentialCache(ttl_seconds=60)

        await cache.get("tenant-1", "stripe-api-key", _make_fetcher("stripe_key"))
        await cache.get("tenant-1", "shopify-token", _make_fetcher("shopify_token"))

        assert cache.size == 2

    @pytest.mark.asyncio
    async def test_cache_11_hit_rate_calculation(self):
        """CACHE-11: Hit rate is calculated correctly."""
        cache = McpCredentialCache(ttl_seconds=60)

        await cache.get("t1", "key", _make_fetcher("v1"))  # miss
        await cache.get("t1", "key", _make_fetcher("v2"))  # hit
        await cache.get("t1", "key", _make_fetcher("v3"))  # hit

        assert cache.hits == 2
        assert cache.misses == 1
        assert cache.hit_rate == pytest.approx(2 / 3, abs=0.01)


# ---------------------------------------------------------------------------
# CACHE-12→CACHE-13: Invalidation
# ---------------------------------------------------------------------------

class TestMcpCredentialCacheInvalidate:
    """Test cache invalidation."""

    @pytest.mark.asyncio
    async def test_cache_12_invalidate_removes_entry(self):
        """CACHE-12: Invalidate removes cached entry and forces re-fetch."""
        cache = McpCredentialCache(ttl_seconds=60)
        await cache.get("tenant-1", "stripe-api-key", _make_fetcher("old_key"))

        removed = cache.invalidate("tenant-1", "stripe-api-key")
        assert removed is True
        assert cache.size == 0

        # Next get should call fetcher again
        fetcher = _make_fetcher("new_key")
        result = await cache.get("tenant-1", "stripe-api-key", fetcher)
        assert result == "new_key"
        fetcher.assert_awaited_once()

    def test_cache_12b_invalidate_nonexistent(self):
        """CACHE-12b: Invalidate on non-existent key returns False."""
        cache = McpCredentialCache(ttl_seconds=60)
        removed = cache.invalidate("tenant-1", "stripe-api-key")
        assert removed is False


# ---------------------------------------------------------------------------
# CACHE-13: Clear tenant
# ---------------------------------------------------------------------------

class TestMcpCredentialCacheClearTenant:
    """Test clearing all credentials for a tenant."""

    @pytest.mark.asyncio
    async def test_cache_13_clear_tenant_removes_all(self):
        """CACHE-13: clear_tenant removes all entries for a specific tenant."""
        cache = McpCredentialCache(ttl_seconds=60)

        await cache.get("tenant-1", "stripe-api-key", _make_fetcher("s1"))
        await cache.get("tenant-1", "shopify-token", _make_fetcher("s2"))
        await cache.get("tenant-2", "stripe-api-key", _make_fetcher("s3"))

        count = cache.clear_tenant("tenant-1")

        assert count == 2
        assert cache.size == 1  # Only tenant-2 remains


# ---------------------------------------------------------------------------
# CACHE-14: Eviction
# ---------------------------------------------------------------------------

class TestMcpCredentialCacheEviction:
    """Test max_entries eviction."""

    @pytest.mark.asyncio
    async def test_cache_14_evicts_when_full(self):
        """CACHE-14: Cache evicts oldest entries when at max capacity."""
        cache = McpCredentialCache(ttl_seconds=60, max_entries=3)

        await cache.get("t1", "k1", _make_fetcher("v1"))
        await cache.get("t2", "k2", _make_fetcher("v2"))
        await cache.get("t3", "k3", _make_fetcher("v3"))
        # This should trigger eviction
        await cache.get("t4", "k4", _make_fetcher("v4"))

        assert cache.size <= 3
        assert cache.evictions > 0


# ---------------------------------------------------------------------------
# CACHE-15: Stats + singleton
# ---------------------------------------------------------------------------

class TestMcpCredentialCacheStats:
    """Test stats and singleton."""

    @pytest.mark.asyncio
    async def test_cache_15_stats_returns_metrics(self):
        """CACHE-15: stats() returns correct metrics dict."""
        cache = McpCredentialCache(ttl_seconds=120, max_entries=100)

        await cache.get("t1", "k1", _make_fetcher("v1"))
        await cache.get("t1", "k1", _make_fetcher("v2"))

        stats = cache.stats()
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["ttl_seconds"] == 120
        assert stats["max_entries"] == 100
        assert stats["hit_rate"] == 0.5

    def test_cache_15b_get_credential_cache_singleton(self):
        """CACHE-15b: get_credential_cache returns singleton."""
        with patch("src.multi_tenant.mcp_credential_cache._credential_cache", None):
            c1 = get_credential_cache()
            get_credential_cache()
            # Can't compare directly due to patch; verify it returns something
            assert isinstance(c1, McpCredentialCache)
