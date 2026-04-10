# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""MCP credential cache — in-memory TTL cache for per-tenant MCP credentials.

Wraps Key Vault credential retrieval with a 5-minute TTL cache to avoid
~200ms latency and throttling on every MCP server connection. Per-tenant
isolation ensures no cross-tenant credential leakage.

Design:
    - Cache key: ``(tenant_id, secret_type)``
    - TTL: 5 minutes (300 seconds), configurable at construction
    - Invalidate-on-error: call ``invalidate()`` on 401/403 from MCP server
    - Double-check locking: ``asyncio.Lock`` prevents thundering herd on cache miss
    - Fetcher-agnostic: caller passes an ``async fetcher()`` callable that
      wraps ``TenantSecretService.get_secret()``

Integration:
    - Created once per application lifetime (module-level singleton)
    - Used by ``create_tenant_mcp_client()`` in ``mcp_client.py``
    - Assertion 3.9: Credential stored in Key Vault, retrieved via cache

AGNTCY Phase 3B (Cycle 5) — credential cache for Stripe MCP.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TTL_SECONDS = 300  # 5 minutes


# ---------------------------------------------------------------------------
# Cache entry
# ---------------------------------------------------------------------------

class _CacheEntry:
    """A single cached credential with expiry timestamp."""

    __slots__ = ("value", "expires_at")

    def __init__(self, value: str, ttl_seconds: float) -> None:
        self.value = value
        self.expires_at = time.monotonic() + ttl_seconds

    @property
    def is_expired(self) -> bool:
        return time.monotonic() >= self.expires_at


# ---------------------------------------------------------------------------
# McpCredentialCache
# ---------------------------------------------------------------------------

# Type alias for the async fetcher callable
CredentialFetcher = Callable[[], Awaitable[str | None]]


class McpCredentialCache:
    """In-memory credential cache with TTL and per-tenant isolation.

    Caches credentials fetched from Key Vault (or any async source) to
    avoid repeated ~200ms round-trips. Thread-safe via ``asyncio.Lock``
    with double-check locking to prevent thundering herd.

    Args:
        ttl_seconds: Time-to-live for cached entries. Default: 300 (5 min).
        max_entries: Maximum total cached entries across all tenants.
            Evicts oldest entries when exceeded. Default: 500.

    Usage::

        cache = McpCredentialCache()

        async def fetch_stripe_key():
            svc = get_secret_service()
            return await svc.get_secret("tenant-123", TenantSecretType.STRIPE_API_KEY)

        api_key = await cache.get("tenant-123", "stripe-api-key", fetch_stripe_key)
    """

    def __init__(
        self,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        max_entries: int = 500,
    ) -> None:
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._cache: dict[tuple[str, str], _CacheEntry] = {}
        self._lock = asyncio.Lock()
        # Metrics
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    async def get(
        self,
        tenant_id: str,
        secret_type: str,
        fetcher: CredentialFetcher,
    ) -> str | None:
        """Get a credential, returning from cache if valid or fetching on miss.

        Double-check locking pattern:
        1. Check cache without lock → return if valid
        2. Acquire lock, re-check → return if valid (another coroutine may have filled it)
        3. Call fetcher → cache result → return

        Args:
            tenant_id: The tenant identifier.
            secret_type: The secret type string (e.g. ``"stripe-api-key"``).
            fetcher: Async callable that returns the credential value or None.

        Returns:
            The credential string, or ``None`` if the fetcher returns None.
        """
        key = (tenant_id, secret_type)

        # Fast path: check without lock
        entry = self._cache.get(key)
        if entry is not None and not entry.is_expired:
            self._hits += 1
            logger.debug(
                "Credential cache HIT: tenant=%s type=%s",
                tenant_id, secret_type,
            )
            return entry.value

        # Slow path: acquire lock and double-check
        async with self._lock:
            # Re-check after lock acquisition
            entry = self._cache.get(key)
            if entry is not None and not entry.is_expired:
                self._hits += 1
                return entry.value

            # Cache miss — fetch from source
            self._misses += 1
            logger.debug(
                "Credential cache MISS: tenant=%s type=%s — fetching",
                tenant_id, secret_type,
            )

            try:
                value = await fetcher()
            except Exception as exc:
                logger.warning(
                    "Credential fetch failed: tenant=%s type=%s error=%s",
                    tenant_id, secret_type, exc,
                )
                # Remove stale entry if present
                self._cache.pop(key, None)
                raise

            if value is None:
                # Fetcher returned None — don't cache, remove stale
                self._cache.pop(key, None)
                return None

            # Evict oldest if at capacity
            self._maybe_evict()

            # Cache the result
            self._cache[key] = _CacheEntry(value, self._ttl_seconds)
            logger.debug(
                "Credential cached: tenant=%s type=%s ttl=%ds",
                tenant_id, secret_type, self._ttl_seconds,
            )
            return value

    def invalidate(self, tenant_id: str, secret_type: str) -> bool:
        """Invalidate a specific cached credential.

        Call this on 401/403 from the MCP server to force a re-fetch
        on the next ``get()`` call.

        Args:
            tenant_id: The tenant identifier.
            secret_type: The secret type string.

        Returns:
            ``True`` if an entry was removed, ``False`` if not cached.
        """
        key = (tenant_id, secret_type)
        removed = self._cache.pop(key, None) is not None
        if removed:
            logger.info(
                "Credential invalidated: tenant=%s type=%s",
                tenant_id, secret_type,
            )
        return removed

    def clear_tenant(self, tenant_id: str) -> int:
        """Clear ALL cached credentials for a tenant.

        Used during tenant deprovisioning or credential rotation.

        Args:
            tenant_id: The tenant identifier.

        Returns:
            Number of entries removed.
        """
        keys_to_remove = [
            key for key in self._cache if key[0] == tenant_id
        ]
        for key in keys_to_remove:
            del self._cache[key]

        if keys_to_remove:
            logger.info(
                "Tenant credentials cleared: tenant=%s count=%d",
                tenant_id, len(keys_to_remove),
            )
        return len(keys_to_remove)

    def clear_all(self) -> int:
        """Clear the entire cache. Returns number of entries removed."""
        count = len(self._cache)
        self._cache.clear()
        if count:
            logger.info("Credential cache cleared: %d entries", count)
        return count

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    @property
    def size(self) -> int:
        """Current number of cached entries (including expired)."""
        return len(self._cache)

    @property
    def hits(self) -> int:
        """Total cache hits since creation."""
        return self._hits

    @property
    def misses(self) -> int:
        """Total cache misses since creation."""
        return self._misses

    @property
    def evictions(self) -> int:
        """Total evictions due to max_entries limit."""
        return self._evictions

    @property
    def hit_rate(self) -> float:
        """Cache hit rate as a fraction (0.0–1.0)."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    def stats(self) -> dict[str, Any]:
        """Return cache statistics for monitoring.

        Returns:
            Dict with size, hits, misses, evictions, hit_rate, ttl.
        """
        return {
            "size": self.size,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": round(self.hit_rate, 3),
            "ttl_seconds": self._ttl_seconds,
            "max_entries": self._max_entries,
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _maybe_evict(self) -> None:
        """Evict expired entries and then oldest entries if still over capacity."""
        # Phase 1: Remove expired entries
        expired_keys = [
            key for key, entry in self._cache.items() if entry.is_expired
        ]
        for key in expired_keys:
            del self._cache[key]
            self._evictions += 1

        # Phase 2: If still at capacity, remove oldest by expiry time
        if len(self._cache) >= self._max_entries:
            # Sort by expires_at ascending (oldest first)
            sorted_keys = sorted(
                self._cache.keys(),
                key=lambda k: self._cache[k].expires_at,
            )
            # Remove oldest 10% or at least 1
            count_to_remove = max(1, len(sorted_keys) // 10)
            for key in sorted_keys[:count_to_remove]:
                del self._cache[key]
                self._evictions += 1


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_credential_cache: McpCredentialCache | None = None


def get_credential_cache() -> McpCredentialCache:
    """Get the module-level credential cache singleton.

    Returns:
        The global ``McpCredentialCache`` instance.
    """
    global _credential_cache
    if _credential_cache is None:
        _credential_cache = McpCredentialCache()
    return _credential_cache
