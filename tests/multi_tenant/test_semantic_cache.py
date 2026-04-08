"""Tests for semantic cache (WI #223-225).

Covers:
    - TTLCache: LRU eviction, TTL expiration, CRUD
    - SemanticCache: embedding cache, search cache, response cache
    - Semantic similarity matching for cache hits
    - Cache invalidation on KB changes
    - Cache metrics and monitoring
    - Integration with KnowledgeVectorizer

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.semantic_cache import (
    EMBEDDING_CACHE_MAX_ENTRIES,
    EMBEDDING_CACHE_TTL_SECONDS,
    RESPONSE_CACHE_TTL_SECONDS,
    SEARCH_CACHE_TTL_SECONDS,
    SEMANTIC_SIMILARITY_THRESHOLD,
    CacheMetrics,
    EmbeddingCacheEntry,
    ResponseCacheEntry,
    SearchCacheEntry,
    SemanticCache,
    TTLCache,
    _embedding_cache_key,
    _response_cache_key,
    _search_cache_key,
    cosine_similarity,
    get_semantic_cache,
    reset_semantic_cache,
)


# ---------------------------------------------------------------------------
# TTLCache tests
# ---------------------------------------------------------------------------


class TestTTLCache:
    """Tests for the TTLCache LRU eviction + TTL expiration logic."""

    def test_put_and_get(self) -> None:
        cache = TTLCache(max_entries=10, default_ttl=300)
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self) -> None:
        cache = TTLCache(max_entries=10, default_ttl=300)
        assert cache.get("nonexistent") is None

    def test_lru_eviction(self) -> None:
        cache = TTLCache(max_entries=3, default_ttl=300)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # a is LRU — adding d should evict a
        evicted = cache.put("d", 4)
        assert evicted == 1
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("d") == 4

    def test_lru_access_order(self) -> None:
        cache = TTLCache(max_entries=3, default_ttl=300)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # Access 'a' to make it recently used
        cache.get("a")
        # Now 'b' is LRU
        cache.put("d", 4)
        assert cache.get("b") is None  # evicted
        assert cache.get("a") == 1  # still present

    def test_ttl_expiration(self) -> None:
        cache = TTLCache(max_entries=10, default_ttl=0.01)  # 10ms TTL
        cache.put("key", "value")
        time.sleep(0.02)
        assert cache.get("key") is None

    def test_custom_ttl_per_entry(self) -> None:
        cache = TTLCache(max_entries=10, default_ttl=300)
        cache.put("short", "val", ttl=0.01)
        cache.put("long", "val", ttl=300)
        time.sleep(0.02)
        assert cache.get("short") is None
        assert cache.get("long") == "val"

    def test_remove(self) -> None:
        cache = TTLCache(max_entries=10, default_ttl=300)
        cache.put("key", "value")
        assert cache.remove("key") is True
        assert cache.get("key") is None
        assert cache.remove("key") is False

    def test_clear(self) -> None:
        cache = TTLCache(max_entries=10, default_ttl=300)
        cache.put("a", 1)
        cache.put("b", 2)
        cleared = cache.clear()
        assert cleared == 2
        assert len(cache) == 0

    def test_cleanup_expired(self) -> None:
        cache = TTLCache(max_entries=10, default_ttl=300)
        cache.put("expired", "val", ttl=0.01)
        cache.put("fresh", "val", ttl=300)
        time.sleep(0.02)
        removed = cache.cleanup_expired()
        assert removed == 1
        assert cache.get("fresh") == "val"

    def test_update_existing_key(self) -> None:
        cache = TTLCache(max_entries=10, default_ttl=300)
        cache.put("key", "v1")
        cache.put("key", "v2")
        assert cache.get("key") == "v2"
        assert len(cache) == 1

    def test_len(self) -> None:
        cache = TTLCache(max_entries=10, default_ttl=300)
        assert len(cache) == 0
        cache.put("a", 1)
        cache.put("b", 2)
        assert len(cache) == 2

    def test_keys(self) -> None:
        cache = TTLCache(max_entries=10, default_ttl=300)
        cache.put("a", 1)
        cache.put("b", 2)
        keys = cache.keys()
        assert set(keys) == {"a", "b"}


# ---------------------------------------------------------------------------
# Cache key tests
# ---------------------------------------------------------------------------


class TestCacheKeys:
    """Tests for cache key generation."""

    def test_embedding_key_deterministic(self) -> None:
        key1 = _embedding_cache_key("tenant1", "hello world")
        key2 = _embedding_cache_key("tenant1", "hello world")
        assert key1 == key2

    def test_embedding_key_tenant_isolation(self) -> None:
        key1 = _embedding_cache_key("tenant1", "hello")
        key2 = _embedding_cache_key("tenant2", "hello")
        assert key1 != key2

    def test_embedding_key_text_sensitivity(self) -> None:
        key1 = _embedding_cache_key("t1", "hello")
        key2 = _embedding_cache_key("t1", "world")
        assert key1 != key2

    def test_search_key_includes_params(self) -> None:
        key1 = _search_cache_key("t1", "query", 5, None, None)
        key2 = _search_cache_key("t1", "query", 10, None, None)
        assert key1 != key2

    def test_search_key_includes_entry_type(self) -> None:
        key1 = _search_cache_key("t1", "q", 5, "faq", None)
        key2 = _search_cache_key("t1", "q", 5, "policy", None)
        assert key1 != key2

    def test_response_key_deterministic(self) -> None:
        key1 = _response_cache_key("t1", "q1")
        key2 = _response_cache_key("t1", "q1")
        assert key1 == key2


# ---------------------------------------------------------------------------
# Cosine similarity tests
# ---------------------------------------------------------------------------


class TestCosineSimilarity:
    """Tests for cosine similarity computation."""

    def test_identical_vectors(self) -> None:
        v = [1.0, 2.0, 3.0]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_empty_vectors(self) -> None:
        assert cosine_similarity([], []) == 0.0

    def test_zero_vector(self) -> None:
        a = [0.0, 0.0]
        b = [1.0, 2.0]
        assert cosine_similarity(a, b) == 0.0

    def test_different_lengths(self) -> None:
        a = [1.0, 2.0]
        b = [1.0, 2.0, 3.0]
        assert cosine_similarity(a, b) == 0.0

    def test_similar_vectors(self) -> None:
        a = [1.0, 2.0, 3.0]
        b = [1.1, 2.0, 3.0]
        sim = cosine_similarity(a, b)
        assert 0.99 < sim < 1.0  # Very similar but not identical


# ---------------------------------------------------------------------------
# CacheMetrics tests
# ---------------------------------------------------------------------------


class TestCacheMetrics:
    """Tests for cache metrics tracking."""

    def test_hit_rate_empty(self) -> None:
        m = CacheMetrics()
        assert m.hit_rate == 0.0

    def test_hit_rate_all_hits(self) -> None:
        m = CacheMetrics(hits=10, misses=0)
        assert m.hit_rate == 1.0

    def test_hit_rate_mixed(self) -> None:
        m = CacheMetrics(hits=3, misses=7)
        assert m.hit_rate == pytest.approx(0.3)

    def test_to_dict(self) -> None:
        m = CacheMetrics(hits=5, misses=10, evictions=2, expirations=1)
        d = m.to_dict()
        assert d["hits"] == 5
        assert d["misses"] == 10
        assert d["hit_rate"] == pytest.approx(0.3333, abs=0.001)
        assert d["total_lookups"] == 15
        assert d["evictions"] == 2
        assert d["expirations"] == 1


# ---------------------------------------------------------------------------
# SemanticCache — Embedding cache (WI #223)
# ---------------------------------------------------------------------------


class TestEmbeddingCache:
    """Tests for query embedding caching."""

    def setup_method(self) -> None:
        self.cache = SemanticCache(
            embedding_max_entries=10,
            embedding_ttl=300,
        )

    def test_put_and_get_embedding(self) -> None:
        emb = [0.1, 0.2, 0.3]
        self.cache.put_embedding("t1", "hello", emb)
        result = self.cache.get_embedding("t1", "hello")
        assert result == emb

    def test_get_missing_embedding(self) -> None:
        assert self.cache.get_embedding("t1", "missing") is None

    def test_tenant_isolation(self) -> None:
        emb = [0.1, 0.2, 0.3]
        self.cache.put_embedding("t1", "hello", emb)
        assert self.cache.get_embedding("t2", "hello") is None

    def test_embedding_cache_metrics(self) -> None:
        emb = [0.1, 0.2, 0.3]
        self.cache.put_embedding("t1", "hello", emb)
        self.cache.get_embedding("t1", "hello")  # hit
        self.cache.get_embedding("t1", "missing")  # miss

        metrics = self.cache._embedding_metrics
        assert metrics.hits == 1
        assert metrics.misses == 1

    def test_cost_savings_tracked(self) -> None:
        emb = [0.1] * 100
        self.cache.put_embedding("t1", "a" * 400, emb)  # ~100 tokens
        self.cache.get_embedding("t1", "a" * 400)  # hit

        assert self.cache._embedding_metrics.estimated_cost_saved > 0

    def test_batch_get(self) -> None:
        self.cache.put_embedding("t1", "a", [0.1])
        self.cache.put_embedding("t1", "c", [0.3])

        results, misses = self.cache.get_embedding_batch(
            "t1", ["a", "b", "c"],
        )
        assert results[0] == [0.1]
        assert results[1] is None
        assert results[2] == [0.3]
        assert misses == [1]

    def test_batch_put(self) -> None:
        self.cache.put_embedding_batch(
            "t1", ["a", "b"], [[0.1], [0.2]],
        )
        assert self.cache.get_embedding("t1", "a") == [0.1]
        assert self.cache.get_embedding("t1", "b") == [0.2]


# ---------------------------------------------------------------------------
# SemanticCache — Search result cache (WI #224)
# ---------------------------------------------------------------------------


class TestSearchCache:
    """Tests for search result caching."""

    def setup_method(self) -> None:
        self.cache = SemanticCache(
            search_max_entries=10,
            search_ttl=300,
        )

    def test_put_and_get_search_results(self) -> None:
        results = [{"id": "1", "rrf_score": 0.9}]
        self.cache.put_search_results("t1", "query", results)
        cached = self.cache.get_search_results("t1", "query")
        assert cached == results

    def test_search_params_matter(self) -> None:
        results = [{"id": "1", "rrf_score": 0.9}]
        self.cache.put_search_results("t1", "q", results, top_k=5)
        # Same query, different top_k → cache miss
        assert self.cache.get_search_results("t1", "q", top_k=10) is None

    def test_entry_type_filter(self) -> None:
        results = [{"id": "1", "rrf_score": 0.9}]
        self.cache.put_search_results(
            "t1", "q", results, entry_type="faq",
        )
        # Different entry_type → cache miss
        assert self.cache.get_search_results(
            "t1", "q", entry_type="policy",
        ) is None

    def test_search_cache_metrics(self) -> None:
        results = [{"id": "1", "rrf_score": 0.9}]
        self.cache.put_search_results("t1", "q", results)
        self.cache.get_search_results("t1", "q")  # hit
        self.cache.get_search_results("t1", "miss")  # miss

        metrics = self.cache._search_metrics
        assert metrics.hits == 1
        assert metrics.misses == 1


# ---------------------------------------------------------------------------
# SemanticCache — Semantic similarity matching (WI #224)
# ---------------------------------------------------------------------------


class TestSemanticSimilarityCache:
    """Tests for semantic similarity-based cache matching."""

    def setup_method(self) -> None:
        self.cache = SemanticCache(
            search_max_entries=50,
            search_ttl=300,
            similarity_threshold=0.95,
        )

    def test_identical_embedding_matches(self) -> None:
        emb = [1.0, 0.0, 0.0]
        results = [{"id": "1", "rrf_score": 0.9}]
        self.cache.put_semantic_search_results(
            "t1", "original query", emb, results,
        )
        # Same embedding → should match
        cached = self.cache.get_semantic_search_results("t1", emb)
        assert cached == results

    def test_similar_embedding_matches(self) -> None:
        emb1 = [1.0, 0.0, 0.0]
        emb2 = [0.99, 0.01, 0.0]  # Very similar
        results = [{"id": "1", "rrf_score": 0.9}]
        self.cache.put_semantic_search_results(
            "t1", "query 1", emb1, results,
        )
        sim = cosine_similarity(emb1, emb2)
        if sim >= 0.95:
            cached = self.cache.get_semantic_search_results("t1", emb2)
            assert cached == results

    def test_dissimilar_embedding_no_match(self) -> None:
        emb1 = [1.0, 0.0, 0.0]
        emb2 = [0.0, 1.0, 0.0]  # Orthogonal
        results = [{"id": "1", "rrf_score": 0.9}]
        self.cache.put_semantic_search_results(
            "t1", "query", emb1, results,
        )
        cached = self.cache.get_semantic_search_results("t1", emb2)
        assert cached is None

    def test_tenant_isolation_semantic(self) -> None:
        emb = [1.0, 0.0, 0.0]
        results = [{"id": "1", "rrf_score": 0.9}]
        self.cache.put_semantic_search_results(
            "t1", "query", emb, results,
        )
        # Different tenant → no match
        cached = self.cache.get_semantic_search_results("t2", emb)
        assert cached is None

    def test_empty_index_returns_none(self) -> None:
        emb = [1.0, 0.0, 0.0]
        cached = self.cache.get_semantic_search_results("t1", emb)
        assert cached is None


# ---------------------------------------------------------------------------
# SemanticCache — Response context cache (WI #224)
# ---------------------------------------------------------------------------


class TestResponseCache:
    """Tests for formatted knowledge context caching."""

    def setup_method(self) -> None:
        self.cache = SemanticCache(
            response_max_entries=10,
            response_ttl=300,
        )

    def test_put_and_get_response(self) -> None:
        self.cache.put_response_context("t1", "q", "context text")
        cached = self.cache.get_response_context("t1", "q")
        assert cached == "context text"

    def test_response_miss(self) -> None:
        assert self.cache.get_response_context("t1", "missing") is None

    def test_response_metrics(self) -> None:
        self.cache.put_response_context("t1", "q", "ctx")
        self.cache.get_response_context("t1", "q")  # hit
        self.cache.get_response_context("t1", "miss")  # miss

        metrics = self.cache._response_metrics
        assert metrics.hits == 1
        assert metrics.misses == 1


# ---------------------------------------------------------------------------
# Cache invalidation
# ---------------------------------------------------------------------------


class TestCacheInvalidation:
    """Tests for cache invalidation on KB changes."""

    def test_invalidate_tenant_clears_search_cache(self) -> None:
        cache = SemanticCache()
        cache.put_search_results("t1", "q", [{"id": "1", "rrf_score": 0.9}])
        cache.invalidate_tenant("t1")
        assert cache.get_search_results("t1", "q") is None

    def test_invalidate_tenant_clears_response_cache(self) -> None:
        cache = SemanticCache()
        cache.put_response_context("t1", "q", "context")
        cache.invalidate_tenant("t1")
        assert cache.get_response_context("t1", "q") is None

    def test_invalidate_tenant_clears_semantic_index(self) -> None:
        cache = SemanticCache()
        emb = [1.0, 0.0, 0.0]
        cache.put_semantic_search_results(
            "t1", "q", emb, [{"id": "1", "rrf_score": 0.9}],
        )
        cache.invalidate_tenant("t1")
        assert cache.get_semantic_search_results("t1", emb) is None

    def test_invalidate_preserves_embedding_cache(self) -> None:
        cache = SemanticCache()
        cache.put_embedding("t1", "text", [0.1, 0.2])
        cache.invalidate_tenant("t1")
        # Embedding cache is NOT invalidated (content-addressable)
        assert cache.get_embedding("t1", "text") == [0.1, 0.2]

    def test_clear_all(self) -> None:
        cache = SemanticCache()
        cache.put_embedding("t1", "text", [0.1])
        cache.put_search_results("t1", "q", [{"id": "1"}])
        cache.put_response_context("t1", "q", "ctx")
        cleared = cache.clear_all()
        assert cleared == 3

    def test_cleanup_expired(self) -> None:
        cache = SemanticCache(
            embedding_ttl=0.01,
            search_ttl=0.01,
            response_ttl=0.01,
        )
        cache.put_embedding("t1", "text", [0.1])
        cache.put_search_results("t1", "q", [{"id": "1"}])
        cache.put_response_context("t1", "q", "ctx")
        time.sleep(0.02)

        result = cache.cleanup()
        assert result["embedding"] >= 1
        assert result["search"] >= 1
        assert result["response"] >= 1


# ---------------------------------------------------------------------------
# Monitoring and health (WI #225)
# ---------------------------------------------------------------------------


class TestCacheMonitoring:
    """Tests for cache monitoring and health reporting."""

    def test_summary_structure(self) -> None:
        cache = SemanticCache()
        s = cache.summary()
        assert "embedding_cache" in s
        assert "search_cache" in s
        assert "response_cache" in s
        assert "overall_hit_rate" in s
        assert "total_estimated_savings_usd" in s
        assert "semantic_index_tenants" in s

    def test_health_structure(self) -> None:
        cache = SemanticCache()
        h = cache.health()
        assert h["status"] == "healthy"
        assert "embedding_entries" in h
        assert "search_entries" in h
        assert "response_entries" in h
        assert "overall_hit_rate" in h

    def test_overall_hit_rate(self) -> None:
        cache = SemanticCache()
        # Put + get from each cache
        cache.put_embedding("t1", "a", [0.1])
        cache.put_search_results("t1", "q", [{"id": "1"}])
        cache.put_response_context("t1", "q", "ctx")

        cache.get_embedding("t1", "a")  # hit
        cache.get_embedding("t1", "b")  # miss
        cache.get_search_results("t1", "q")  # hit
        cache.get_search_results("t1", "x")  # miss
        cache.get_response_context("t1", "q")  # hit
        cache.get_response_context("t1", "x")  # miss

        # 3 hits, 3 misses = 0.5 hit rate
        assert cache._overall_hit_rate() == pytest.approx(0.5)

    def test_overall_hit_rate_empty(self) -> None:
        cache = SemanticCache()
        assert cache._overall_hit_rate() == 0.0

    def test_entry_counts_in_health(self) -> None:
        cache = SemanticCache()
        cache.put_embedding("t1", "a", [0.1])
        cache.put_embedding("t1", "b", [0.2])
        cache.put_search_results("t1", "q", [{"id": "1"}])

        h = cache.health()
        assert h["embedding_entries"] == 2
        assert h["search_entries"] == 1
        assert h["response_entries"] == 0


# ---------------------------------------------------------------------------
# Singleton management
# ---------------------------------------------------------------------------


class TestSingleton:
    """Tests for module-level singleton lifecycle."""

    def test_get_returns_same_instance(self) -> None:
        reset_semantic_cache()
        c1 = get_semantic_cache()
        c2 = get_semantic_cache()
        assert c1 is c2

    def test_reset_creates_new_instance(self) -> None:
        reset_semantic_cache()
        c1 = get_semantic_cache()
        reset_semantic_cache()
        c2 = get_semantic_cache()
        assert c1 is not c2


# ---------------------------------------------------------------------------
# Integration with KnowledgeVectorizer
# ---------------------------------------------------------------------------


class TestVectorizerCacheIntegration:
    """Tests for SemanticCache integration in KnowledgeVectorizer."""

    @pytest.fixture
    def vectorizer(self) -> Any:
        """Create a KnowledgeVectorizer with mocked dependencies."""
        from src.multi_tenant.knowledge_vectorizer import KnowledgeVectorizer

        v = KnowledgeVectorizer()

        # Mock KB repo
        mock_repo = MagicMock()
        mock_repo.vector_search = AsyncMock(return_value=[
            {"id": "kb1", "title": "FAQ", "content": "Answer", "similarity": 0.85},
        ])
        mock_repo.list_active = AsyncMock(return_value=[
            {"id": "kb1", "title": "FAQ", "content": "Answer about topic"},
        ])

        # Mock OpenAI client
        mock_embedding_response = MagicMock()
        mock_embedding_item = MagicMock()
        mock_embedding_item.embedding = [0.1] * 3072
        mock_embedding_response.data = [mock_embedding_item]

        mock_openai = AsyncMock()
        mock_openai.embeddings = MagicMock()
        mock_openai.embeddings.create = AsyncMock(
            return_value=mock_embedding_response,
        )

        v.configure(kb_repo=mock_repo, openai_client=mock_openai)

        # Reset the cache for isolation
        reset_semantic_cache()

        return v

    @pytest.mark.asyncio
    async def test_search_populates_cache(self, vectorizer: Any) -> None:
        """First search should populate the cache."""
        results = await vectorizer.search("tenant1", "test query")
        assert len(results) > 0

        # Second call should hit cache
        cache = get_semantic_cache()
        cached = cache.get_search_results("tenant1", "test query")
        assert cached is not None

    @pytest.mark.asyncio
    async def test_cached_search_avoids_api_call(self, vectorizer: Any) -> None:
        """Cached search should not call embedding API again."""
        # First call
        await vectorizer.search("tenant1", "test query")

        # Get call count after first call
        embed_calls = vectorizer._openai_client.embeddings.create.call_count

        # Second identical call
        await vectorizer.search("tenant1", "test query")

        # Should not have called embedding API again
        assert vectorizer._openai_client.embeddings.create.call_count == embed_calls

    @pytest.mark.asyncio
    async def test_embed_entry_invalidates_cache(self, vectorizer: Any) -> None:
        """Embedding a KB entry should invalidate search cache."""
        # Populate cache
        await vectorizer.search("tenant1", "test query")

        cache = get_semantic_cache()
        assert cache.get_search_results("tenant1", "test query") is not None

        # embed_entry takes a dict, not an ID
        vectorizer._kb_repo.patch = AsyncMock(return_value={"id": "entry1"})

        entry_doc = {
            "id": "entry1",
            "title": "New Entry",
            "content": "New content",
            "is_active": True,
        }
        await vectorizer.embed_entry("tenant1", entry_doc)

        # Cache should be invalidated
        assert cache.get_search_results("tenant1", "test query") is None

    @pytest.mark.asyncio
    async def test_embedding_cache_hit(self, vectorizer: Any) -> None:
        """Query embedding should be cached on first call."""
        await vectorizer.search("tenant1", "test query")

        cache = get_semantic_cache()
        emb = cache.get_embedding("tenant1", "test query")
        assert emb is not None
        assert len(emb) == 3072


# ---------------------------------------------------------------------------
# Dataclass tests
# ---------------------------------------------------------------------------


class TestDataclasses:
    """Tests for cache entry dataclasses."""

    def test_embedding_cache_entry(self) -> None:
        entry = EmbeddingCacheEntry(
            embedding=[0.1, 0.2],
            created_at=time.monotonic(),
        )
        assert entry.embedding == [0.1, 0.2]
        assert entry.ttl == EMBEDDING_CACHE_TTL_SECONDS

    def test_search_cache_entry(self) -> None:
        entry = SearchCacheEntry(
            results=[{"id": "1"}],
            query="hello",
            created_at=time.monotonic(),
        )
        assert entry.results == [{"id": "1"}]
        assert entry.ttl == SEARCH_CACHE_TTL_SECONDS

    def test_response_cache_entry(self) -> None:
        entry = ResponseCacheEntry(
            context="knowledge context",
            query="hello",
            created_at=time.monotonic(),
        )
        assert entry.context == "knowledge context"
        assert entry.ttl == RESPONSE_CACHE_TTL_SECONDS


# ---------------------------------------------------------------------------
# Constants validation
# ---------------------------------------------------------------------------


class TestConstants:
    """Validate cache constants are sensible."""

    def test_embedding_ttl_reasonable(self) -> None:
        assert EMBEDDING_CACHE_TTL_SECONDS >= 300  # At least 5 minutes
        assert EMBEDDING_CACHE_TTL_SECONDS <= 86400  # At most 24 hours

    def test_search_ttl_shorter_than_embedding(self) -> None:
        # Search results depend on KB content, which can change
        assert SEARCH_CACHE_TTL_SECONDS <= EMBEDDING_CACHE_TTL_SECONDS

    def test_similarity_threshold_high(self) -> None:
        # Should be high to avoid false positives
        assert SEMANTIC_SIMILARITY_THRESHOLD >= 0.9

    def test_max_entries_reasonable(self) -> None:
        assert EMBEDDING_CACHE_MAX_ENTRIES >= 100
        assert EMBEDDING_CACHE_MAX_ENTRIES <= 10000
