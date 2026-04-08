"""Semantic caching for Knowledge Base retrieval and AI responses.

Work Items #223-225: Multi-layer caching system that reduces Azure OpenAI
API costs and improves response latency by caching:

    1. Query embeddings — avoid re-computing embeddings for repeated queries
    2. Search results — cache hybrid retrieval results for identical queries
    3. Response fragments — cache formatted knowledge context for similar queries

Architecture:
    - Per-tenant isolation (cache keys include tenant_id)
    - TTL-based expiration with configurable durations
    - LRU eviction when cache exceeds capacity
    - Cosine similarity matching for semantic deduplication
    - Thread-safe via asyncio (single-event-loop, per-process)

Integration points:
    - knowledge_vectorizer.py: search() calls check cache before embedding
    - pipeline.py: knowledge context check before full retrieval
    - RetrievalMetrics: cache hit/miss recording

Dependencies:
    - No external packages (stdlib only)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import logging
import math
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Embedding cache
EMBEDDING_CACHE_TTL_SECONDS = 3600  # 1 hour — embeddings are deterministic
EMBEDDING_CACHE_MAX_ENTRIES = 500  # Per tenant

# Search result cache
SEARCH_CACHE_TTL_SECONDS = 300  # 5 minutes — KB can change
SEARCH_CACHE_MAX_ENTRIES = 200  # Per tenant

# Response cache (formatted knowledge context)
RESPONSE_CACHE_TTL_SECONDS = 300  # 5 minutes — aligned with search cache
RESPONSE_CACHE_MAX_ENTRIES = 100  # Per tenant

# Semantic similarity threshold for cache hits
SEMANTIC_SIMILARITY_THRESHOLD = 0.95  # Very high — only near-identical queries

# Cost constants (for metrics)
EMBEDDING_COST_PER_1K_TOKENS = 0.00013  # text-embedding-3-large
CHARS_PER_TOKEN = 4


# ---------------------------------------------------------------------------
# Cache entry dataclasses
# ---------------------------------------------------------------------------


@dataclass
class EmbeddingCacheEntry:
    """A cached embedding vector."""

    embedding: list[float]
    created_at: float  # time.monotonic()
    ttl: float = EMBEDDING_CACHE_TTL_SECONDS


@dataclass
class SearchCacheEntry:
    """Cached search results."""

    results: list[dict[str, Any]]
    query: str
    created_at: float
    ttl: float = SEARCH_CACHE_TTL_SECONDS


@dataclass
class ResponseCacheEntry:
    """Cached formatted knowledge context."""

    context: str
    query: str
    created_at: float
    ttl: float = RESPONSE_CACHE_TTL_SECONDS


# ---------------------------------------------------------------------------
# Cache metrics
# ---------------------------------------------------------------------------


@dataclass
class CacheMetrics:
    """Per-cache-type metrics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    total_entries: int = 0
    estimated_cost_saved: float = 0.0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hit_rate, 4),
            "total_lookups": total,
            "evictions": self.evictions,
            "expirations": self.expirations,
            "total_entries": self.total_entries,
            "estimated_cost_saved_usd": round(self.estimated_cost_saved, 6),
        }


# ---------------------------------------------------------------------------
# LRU cache with TTL
# ---------------------------------------------------------------------------


class TTLCache:
    """Bounded LRU cache with per-entry TTL expiration.

    Uses OrderedDict for O(1) LRU eviction. Each entry has an
    independent TTL based on its creation time.
    """

    def __init__(self, max_entries: int, default_ttl: float) -> None:
        self._max_entries = max_entries
        self._default_ttl = default_ttl
        self._store: OrderedDict[str, tuple[Any, float, float]] = OrderedDict()
        # Tuple: (value, created_at_monotonic, ttl_seconds)

    def get(self, key: str) -> Any | None:
        """Get a value by key, returning None if missing or expired."""
        entry = self._store.get(key)
        if entry is None:
            return None

        value, created_at, ttl = entry
        if time.monotonic() - created_at > ttl:
            del self._store[key]
            return None  # Expired

        # Move to end (most recently used)
        self._store.move_to_end(key)
        return value

    def put(self, key: str, value: Any, ttl: float | None = None) -> int:
        """Store a value, evicting LRU entries if at capacity.

        Returns the number of entries evicted.
        """
        evicted = 0
        actual_ttl = ttl if ttl is not None else self._default_ttl

        # Remove existing entry if present
        if key in self._store:
            del self._store[key]

        # Evict LRU entries if at capacity
        while len(self._store) >= self._max_entries:
            self._store.popitem(last=False)  # Remove oldest
            evicted += 1

        self._store[key] = (value, time.monotonic(), actual_ttl)
        return evicted

    def remove(self, key: str) -> bool:
        """Remove a specific entry. Returns True if found."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> int:
        """Clear all entries. Returns count cleared."""
        count = len(self._store)
        self._store.clear()
        return count

    def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        now = time.monotonic()
        expired_keys = [
            k for k, (_, created_at, ttl) in self._store.items()
            if now - created_at > ttl
        ]
        for k in expired_keys:
            del self._store[k]
        return len(expired_keys)

    def __len__(self) -> int:
        return len(self._store)

    def keys(self) -> list[str]:
        return list(self._store.keys())


# ---------------------------------------------------------------------------
# Cache key helpers
# ---------------------------------------------------------------------------


def _embedding_cache_key(tenant_id: str, text: str) -> str:
    """Cache key for an embedding: hash of tenant + text."""
    raw = f"emb:{tenant_id}:{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _search_cache_key(
    tenant_id: str,
    query: str,
    top_k: int,
    entry_type: str | None,
    language: str | None,
) -> str:
    """Cache key for search results: hash of all search parameters."""
    raw = f"search:{tenant_id}:{query}:{top_k}:{entry_type}:{language}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _response_cache_key(tenant_id: str, query: str) -> str:
    """Cache key for formatted response context."""
    raw = f"resp:{tenant_id}:{query}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Cosine similarity for semantic matching
# ---------------------------------------------------------------------------


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Returns value in [-1, 1]. Identical vectors return 1.0.
    """
    if len(a) != len(b) or not a:
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# SemanticCache service
# ---------------------------------------------------------------------------


class SemanticCache:
    """Multi-layer semantic caching for Knowledge Base retrieval.

    Three cache tiers:
        1. Embedding cache — avoids Azure OpenAI embedding API calls
        2. Search cache — avoids full hybrid retrieval (vector + BM25)
        3. Response cache — avoids formatting pipeline context

    All caches are per-tenant (cache keys include tenant_id).
    Thread-safe within a single asyncio event loop.

    Usage:
        cache = SemanticCache()

        # Check embedding cache before calling Azure OpenAI
        embedding = cache.get_embedding(tenant_id, text)
        if embedding is None:
            embedding = await openai.embeddings.create(...)
            cache.put_embedding(tenant_id, text, embedding)

        # Check search cache before running hybrid retrieval
        results = cache.get_search_results(tenant_id, query, top_k)
        if results is None:
            results = await vectorizer.search(...)
            cache.put_search_results(tenant_id, query, top_k, results)
    """

    def __init__(
        self,
        *,
        embedding_max_entries: int = EMBEDDING_CACHE_MAX_ENTRIES,
        embedding_ttl: float = EMBEDDING_CACHE_TTL_SECONDS,
        search_max_entries: int = SEARCH_CACHE_MAX_ENTRIES,
        search_ttl: float = SEARCH_CACHE_TTL_SECONDS,
        response_max_entries: int = RESPONSE_CACHE_MAX_ENTRIES,
        response_ttl: float = RESPONSE_CACHE_TTL_SECONDS,
        similarity_threshold: float = SEMANTIC_SIMILARITY_THRESHOLD,
    ) -> None:
        self._embedding_cache = TTLCache(embedding_max_entries, embedding_ttl)
        self._search_cache = TTLCache(search_max_entries, search_ttl)
        self._response_cache = TTLCache(response_max_entries, response_ttl)
        self._similarity_threshold = similarity_threshold

        # Per-cache metrics
        self._embedding_metrics = CacheMetrics()
        self._search_metrics = CacheMetrics()
        self._response_metrics = CacheMetrics()

        # Semantic index: tenant -> list of (query_text, embedding, cache_key)
        self._semantic_index: dict[str, list[tuple[str, list[float], str]]] = {}

        logger.info(
            "SemanticCache initialized: embedding=%d/%ds, search=%d/%ds, "
            "response=%d/%ds, similarity=%.2f",
            embedding_max_entries, int(embedding_ttl),
            search_max_entries, int(search_ttl),
            response_max_entries, int(response_ttl),
            similarity_threshold,
        )

    # ------------------------------------------------------------------
    # Embedding cache (WI #223)
    # ------------------------------------------------------------------

    def get_embedding(self, tenant_id: str, text: str) -> list[float] | None:
        """Look up a cached embedding for the given text.

        Returns the embedding vector if cached and not expired, else None.
        """
        key = _embedding_cache_key(tenant_id, text)
        entry: EmbeddingCacheEntry | None = self._embedding_cache.get(key)

        if entry is not None:
            self._embedding_metrics.hits += 1
            # Estimate cost saved: embedding API call avoided
            tokens = len(text) / CHARS_PER_TOKEN
            self._embedding_metrics.estimated_cost_saved += (
                tokens / 1000 * EMBEDDING_COST_PER_1K_TOKENS
            )
            return entry.embedding

        self._embedding_metrics.misses += 1
        return None

    def put_embedding(
        self, tenant_id: str, text: str, embedding: list[float],
    ) -> None:
        """Store an embedding in the cache."""
        key = _embedding_cache_key(tenant_id, text)
        entry = EmbeddingCacheEntry(
            embedding=embedding,
            created_at=time.monotonic(),
        )
        evicted = self._embedding_cache.put(key, entry)
        self._embedding_metrics.evictions += evicted
        self._embedding_metrics.total_entries = len(self._embedding_cache)

    def get_embedding_batch(
        self, tenant_id: str, texts: list[str],
    ) -> tuple[list[list[float] | None], list[int]]:
        """Look up cached embeddings for a batch of texts.

        Returns:
            - List of embeddings (None for cache misses)
            - List of indices that need embedding (cache misses)
        """
        results: list[list[float] | None] = []
        miss_indices: list[int] = []

        for i, text in enumerate(texts):
            emb = self.get_embedding(tenant_id, text)
            results.append(emb)
            if emb is None:
                miss_indices.append(i)

        return results, miss_indices

    def put_embedding_batch(
        self, tenant_id: str, texts: list[str], embeddings: list[list[float]],
    ) -> None:
        """Store a batch of embeddings in the cache."""
        for text, emb in zip(texts, embeddings):
            self.put_embedding(tenant_id, text, emb)

    # ------------------------------------------------------------------
    # Search result cache (WI #224)
    # ------------------------------------------------------------------

    def get_search_results(
        self,
        tenant_id: str,
        query: str,
        top_k: int = 5,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]] | None:
        """Look up cached search results for the given query.

        Returns cached results if available and not expired, else None.
        """
        key = _search_cache_key(tenant_id, query, top_k, entry_type, language)
        entry: SearchCacheEntry | None = self._search_cache.get(key)

        if entry is not None:
            self._search_metrics.hits += 1
            return entry.results

        self._search_metrics.misses += 1
        return None

    def put_search_results(
        self,
        tenant_id: str,
        query: str,
        results: list[dict[str, Any]],
        top_k: int = 5,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> None:
        """Store search results in the cache."""
        key = _search_cache_key(tenant_id, query, top_k, entry_type, language)
        entry = SearchCacheEntry(
            results=results,
            query=query,
            created_at=time.monotonic(),
        )
        evicted = self._search_cache.put(key, entry)
        self._search_metrics.evictions += evicted
        self._search_metrics.total_entries = len(self._search_cache)

    # ------------------------------------------------------------------
    # Semantic search result cache (WI #224)
    # ------------------------------------------------------------------

    def get_semantic_search_results(
        self,
        tenant_id: str,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]] | None:
        """Find cached results for a semantically similar query.

        Uses cosine similarity on query embeddings to find near-identical
        queries that have cached results. Only returns a hit if similarity
        exceeds SEMANTIC_SIMILARITY_THRESHOLD (default 0.95).

        This is more expensive than exact-match cache lookup but catches
        paraphrased queries like "What's your return policy?" vs
        "How do returns work?"
        """
        tenant_index = self._semantic_index.get(tenant_id, [])
        if not tenant_index:
            return None

        best_sim = 0.0
        best_key: str | None = None

        for _query_text, cached_embedding, cache_key in tenant_index:
            sim = cosine_similarity(query_embedding, cached_embedding)
            if sim > best_sim:
                best_sim = sim
                best_key = cache_key

        if best_sim >= self._similarity_threshold and best_key:
            entry: SearchCacheEntry | None = self._search_cache.get(best_key)
            if entry is not None:
                self._search_metrics.hits += 1
                logger.debug(
                    "Semantic cache hit: similarity=%.4f tenant=%s",
                    best_sim, tenant_id[:8],
                )
                return entry.results

        return None

    def put_semantic_search_results(
        self,
        tenant_id: str,
        query: str,
        query_embedding: list[float],
        results: list[dict[str, Any]],
        top_k: int = 5,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> None:
        """Store search results with semantic index for similarity matching."""
        # Store in exact-match cache
        key = _search_cache_key(tenant_id, query, top_k, entry_type, language)
        entry = SearchCacheEntry(
            results=results,
            query=query,
            created_at=time.monotonic(),
        )
        evicted = self._search_cache.put(key, entry)
        self._search_metrics.evictions += evicted
        self._search_metrics.total_entries = len(self._search_cache)

        # Add to semantic index
        if tenant_id not in self._semantic_index:
            self._semantic_index[tenant_id] = []

        tenant_index = self._semantic_index[tenant_id]
        tenant_index.append((query, query_embedding, key))

        # Limit semantic index size per tenant
        max_semantic = SEARCH_CACHE_MAX_ENTRIES
        if len(tenant_index) > max_semantic:
            self._semantic_index[tenant_id] = tenant_index[-max_semantic:]

    # ------------------------------------------------------------------
    # Response context cache (WI #224)
    # ------------------------------------------------------------------

    def get_response_context(
        self, tenant_id: str, query: str,
    ) -> str | None:
        """Look up cached formatted knowledge context.

        Returns the formatted context string if cached, else None.
        """
        key = _response_cache_key(tenant_id, query)
        entry: ResponseCacheEntry | None = self._response_cache.get(key)

        if entry is not None:
            self._response_metrics.hits += 1
            return entry.context

        self._response_metrics.misses += 1
        return None

    def put_response_context(
        self, tenant_id: str, query: str, context: str,
    ) -> None:
        """Store a formatted knowledge context in the cache."""
        key = _response_cache_key(tenant_id, query)
        entry = ResponseCacheEntry(
            context=context,
            query=query,
            created_at=time.monotonic(),
        )
        evicted = self._response_cache.put(key, entry)
        self._response_metrics.evictions += evicted
        self._response_metrics.total_entries = len(self._response_cache)

    # ------------------------------------------------------------------
    # Cache invalidation
    # ------------------------------------------------------------------

    def invalidate_tenant(self, tenant_id: str) -> int:
        """Invalidate all cache entries for a tenant.

        Called when a tenant's KB content changes (article create/update/delete).
        Embedding cache is NOT invalidated (embeddings are content-addressable).

        Returns total entries removed.
        """
        removed = 0

        # Clear search and response caches (they depend on KB content)
        # We need to check all keys since cache keys are hashed
        for cache, prefix in [
            (self._search_cache, f"search:{tenant_id}:"),
            (self._response_cache, f"resp:{tenant_id}:"),
        ]:
            keys_to_remove = []
            for key in cache.keys():
                # Keys are SHA-256 hashes, so we can't filter by prefix
                # Instead, just clear the semantic index and let TTL handle it
                pass
            removed += len(keys_to_remove)

        # Clear semantic index for this tenant
        if tenant_id in self._semantic_index:
            removed += len(self._semantic_index[tenant_id])
            del self._semantic_index[tenant_id]

        # For search/response caches, we do a full clear per tenant
        # since keys are hashed. This is acceptable because invalidation
        # only happens on KB content changes (infrequent).
        search_cleared = self._search_cache.clear()
        response_cleared = self._response_cache.clear()
        removed += search_cleared + response_cleared

        if removed > 0:
            logger.info(
                "Cache invalidated for tenant %s: %d entries removed",
                tenant_id[:8], removed,
            )

        return removed

    def cleanup(self) -> dict[str, int]:
        """Remove all expired entries across all caches.

        Should be called periodically (e.g., every 60 seconds).

        Returns count of expired entries removed per cache type.
        """
        embedding_expired = self._embedding_cache.cleanup_expired()
        search_expired = self._search_cache.cleanup_expired()
        response_expired = self._response_cache.cleanup_expired()

        self._embedding_metrics.expirations += embedding_expired
        self._search_metrics.expirations += search_expired
        self._response_metrics.expirations += response_expired

        # Update entry counts
        self._embedding_metrics.total_entries = len(self._embedding_cache)
        self._search_metrics.total_entries = len(self._search_cache)
        self._response_metrics.total_entries = len(self._response_cache)

        # Clean up semantic index (remove entries whose cache key is expired)
        for tenant_id in list(self._semantic_index.keys()):
            entries = self._semantic_index[tenant_id]
            valid = [
                (q, e, k) for q, e, k in entries
                if self._search_cache.get(k) is not None
            ]
            if valid:
                self._semantic_index[tenant_id] = valid
            else:
                del self._semantic_index[tenant_id]

        return {
            "embedding": embedding_expired,
            "search": search_expired,
            "response": response_expired,
        }

    def clear_all(self) -> int:
        """Clear all caches. Returns total entries cleared."""
        total = 0
        total += self._embedding_cache.clear()
        total += self._search_cache.clear()
        total += self._response_cache.clear()
        self._semantic_index.clear()

        # Reset entry counts
        self._embedding_metrics.total_entries = 0
        self._search_metrics.total_entries = 0
        self._response_metrics.total_entries = 0

        return total

    # ------------------------------------------------------------------
    # Monitoring and health (WI #225)
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return comprehensive cache metrics.

        Used by the /ready health endpoint and operational dashboards.
        """
        return {
            "embedding_cache": self._embedding_metrics.to_dict(),
            "search_cache": self._search_metrics.to_dict(),
            "response_cache": self._response_metrics.to_dict(),
            "semantic_index_tenants": len(self._semantic_index),
            "semantic_index_entries": sum(
                len(v) for v in self._semantic_index.values()
            ),
            "overall_hit_rate": self._overall_hit_rate(),
            "total_estimated_savings_usd": round(
                self._embedding_metrics.estimated_cost_saved
                + self._search_metrics.estimated_cost_saved
                + self._response_metrics.estimated_cost_saved,
                6,
            ),
        }

    def health(self) -> dict[str, Any]:
        """Compact health status for /ready endpoint."""
        return {
            "status": "healthy",
            "embedding_entries": len(self._embedding_cache),
            "search_entries": len(self._search_cache),
            "response_entries": len(self._response_cache),
            "overall_hit_rate": round(self._overall_hit_rate(), 4),
        }

    def _overall_hit_rate(self) -> float:
        """Compute aggregate hit rate across all cache tiers."""
        total_hits = (
            self._embedding_metrics.hits
            + self._search_metrics.hits
            + self._response_metrics.hits
        )
        total_lookups = (
            self._embedding_metrics.hits + self._embedding_metrics.misses
            + self._search_metrics.hits + self._search_metrics.misses
            + self._response_metrics.hits + self._response_metrics.misses
        )
        return total_hits / total_lookups if total_lookups > 0 else 0.0


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_semantic_cache: SemanticCache | None = None


def get_semantic_cache() -> SemanticCache:
    """Get the singleton SemanticCache instance."""
    global _semantic_cache
    if _semantic_cache is None:
        _semantic_cache = SemanticCache()
    return _semantic_cache


def reset_semantic_cache() -> None:
    """Reset the singleton (for testing)."""
    global _semantic_cache
    _semantic_cache = None
