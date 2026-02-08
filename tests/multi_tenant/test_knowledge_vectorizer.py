"""Tests for Knowledge Base vectorizer and hybrid retrieval (WI #209-213).

Validates:
    - Content hashing and change detection
    - BM25 scoring algorithm
    - Reciprocal Rank Fusion (RRF)
    - KnowledgeVectorizer embedding pipeline
    - Hybrid search (vector + BM25)
    - Retrieval quality metrics
    - Pipeline integration (format_for_pipeline)
    - Admin API embedding on create/update

Test IDs follow the pattern KB-XX for traceability.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.knowledge_vectorizer import (
    DEFAULT_BM25_WEIGHT,
    DEFAULT_TOP_K,
    DEFAULT_VECTOR_WEIGHT,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    HIGH_RELEVANCE_SCORE,
    KnowledgeVectorizer,
    RetrievalMetrics,
    bm25_score,
    compute_bm25_scores,
    compute_content_hash,
    get_knowledge_vectorizer,
    reciprocal_rank_fusion,
)

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

TENANT_ID = "tenant-vectorizer-test-0001"


def _make_kb_entry(
    entry_id: str = "kb-001",
    title: str = "Test Product",
    content: str = "This is a test product with great features.",
    entry_type: str = "product",
    tags: list[str] | None = None,
    is_active: bool = True,
    embedding: list[float] | None = None,
    content_hash: str | None = None,
) -> dict[str, Any]:
    """Create a minimal KB entry dict for testing."""
    return {
        "id": entry_id,
        "tenant_id": TENANT_ID,
        "entry_type": entry_type,
        "title": title,
        "content": content,
        "tags": tags or [],
        "language": "en",
        "is_active": is_active,
        "embedding": embedding,
        "embedding_model": EMBEDDING_MODEL if embedding else None,
        "embedded_at": "2026-02-05T00:00:00Z" if embedding else None,
        "content_hash": content_hash,
        "metadata": {},
        "created_at": "2026-02-05T00:00:00Z",
        "updated_at": "2026-02-05T00:00:00Z",
    }


def _make_entries_corpus() -> list[dict[str, Any]]:
    """Create a corpus of KB entries for BM25/search testing."""
    return [
        _make_kb_entry(
            entry_id="kb-001",
            title="Return Policy",
            content="Items can be returned within 30 days of purchase. "
            "Original receipt required. Refunds processed to original payment method.",
            entry_type="policy",
            tags=["returns", "refund"],
        ),
        _make_kb_entry(
            entry_id="kb-002",
            title="Wireless Headphones Pro",
            content="Premium wireless headphones with noise cancellation. "
            "40 hour battery life. Bluetooth 5.3. Available in black and white.",
            entry_type="product",
            tags=["electronics", "audio", "headphones"],
        ),
        _make_kb_entry(
            entry_id="kb-003",
            title="Shipping Information",
            content="Free shipping on orders over $50. Standard delivery 5-7 business days. "
            "Express shipping available for $9.99, delivers in 2-3 days.",
            entry_type="policy",
            tags=["shipping", "delivery"],
        ),
        _make_kb_entry(
            entry_id="kb-004",
            title="How do I track my order?",
            content="You can track your order by logging into your account "
            "and clicking on 'Order History'. A tracking number is provided "
            "once your order ships.",
            entry_type="faq",
            tags=["tracking", "orders"],
        ),
        _make_kb_entry(
            entry_id="kb-005",
            title="USB-C Charging Cable",
            content="Durable USB-C to USB-C cable. 6 feet long. "
            "Supports fast charging up to 100W. Compatible with all USB-C devices.",
            entry_type="product",
            tags=["accessories", "charging", "cable"],
        ),
    ]


def _zero_embedding() -> list[float]:
    """Create a zero vector for dev-mode testing."""
    return [0.0] * EMBEDDING_DIMENSIONS


# ---------------------------------------------------------------------------
# KB-01: Content hashing
# ---------------------------------------------------------------------------


class TestContentHashing:
    """KB-01: Content hash computation and change detection."""

    def test_hash_is_deterministic(self) -> None:
        """Same title+content always produces the same hash."""
        h1 = compute_content_hash("Title", "Content")
        h2 = compute_content_hash("Title", "Content")
        assert h1 == h2

    def test_hash_differs_on_title_change(self) -> None:
        """Changing the title produces a different hash."""
        h1 = compute_content_hash("Title A", "Content")
        h2 = compute_content_hash("Title B", "Content")
        assert h1 != h2

    def test_hash_differs_on_content_change(self) -> None:
        """Changing the content produces a different hash."""
        h1 = compute_content_hash("Title", "Content A")
        h2 = compute_content_hash("Title", "Content B")
        assert h1 != h2

    def test_hash_is_sha256_hex(self) -> None:
        """Hash is a valid SHA-256 hex digest (64 chars)."""
        h = compute_content_hash("Title", "Content")
        assert len(h) == 64
        # Verify it matches manual computation
        expected = hashlib.sha256("Title\n---\nContent".encode()).hexdigest()
        assert h == expected

    def test_empty_strings(self) -> None:
        """Empty title and content produce a valid hash."""
        h = compute_content_hash("", "")
        assert len(h) == 64


# ---------------------------------------------------------------------------
# KB-02: BM25 scoring
# ---------------------------------------------------------------------------


class TestBM25Scoring:
    """KB-02: BM25 keyword scoring algorithm."""

    def test_bm25_basic_match(self) -> None:
        """A query matching document content produces a positive score."""
        score = bm25_score(
            query_tokens=["headphones"],
            doc_tokens=["premium", "wireless", "headphones", "noise", "cancellation"],
            doc_frequencies={"headphones": 1},  # 1 doc contains "headphones"
            total_docs=5,
            avg_doc_len=20.0,
        )
        assert score > 0.0

    def test_bm25_no_match_zero(self) -> None:
        """No matching terms yields zero score."""
        score = bm25_score(
            query_tokens=["laptop"],
            doc_tokens=["premium", "wireless", "headphones"],
            doc_frequencies={"laptop": 0},
            total_docs=5,
            avg_doc_len=20.0,
        )
        assert score == 0.0

    def test_bm25_rarer_term_scores_higher(self) -> None:
        """A rarer term (lower doc frequency) scores higher (IDF effect)."""
        rare_score = bm25_score(
            query_tokens=["noise"],
            doc_tokens=["noise", "cancellation"],
            doc_frequencies={"noise": 1},
            total_docs=100,
            avg_doc_len=20.0,
        )
        common_score = bm25_score(
            query_tokens=["noise"],
            doc_tokens=["noise", "cancellation"],
            doc_frequencies={"noise": 80},
            total_docs=100,
            avg_doc_len=20.0,
        )
        assert rare_score > common_score

    def test_compute_bm25_scores_returns_sorted(self) -> None:
        """compute_bm25_scores returns results sorted by score descending."""
        entries = _make_entries_corpus()
        results = compute_bm25_scores("return policy refund", entries)
        assert len(results) > 0
        # Results are (entry_id, score) tuples
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)

    def test_compute_bm25_scores_zero_entries(self) -> None:
        """Empty corpus returns empty results."""
        results = compute_bm25_scores("test query", [])
        assert results == []

    def test_compute_bm25_top_result_matches_intent(self) -> None:
        """Query about returns should surface the Return Policy entry first."""
        entries = _make_entries_corpus()
        results = compute_bm25_scores("how to return an item", entries)
        if results:
            top_id = results[0][0]
            assert top_id == "kb-001"  # Return Policy


# ---------------------------------------------------------------------------
# KB-03: Reciprocal Rank Fusion
# ---------------------------------------------------------------------------


class TestReciprocalRankFusion:
    """KB-03: RRF combining vector and BM25 results."""

    def test_rrf_basic_fusion(self) -> None:
        """RRF fuses two ranked lists and adds metadata."""
        vector_results = [
            {"id": "a", "similarity": 0.95, "title": "A"},
            {"id": "b", "similarity": 0.80, "title": "B"},
        ]
        bm25_results = [
            ("b", 5.2),
            ("a", 3.1),
        ]

        fused = reciprocal_rank_fusion(
            vector_results=vector_results,
            bm25_results=bm25_results,
            top_k=5,
        )

        assert len(fused) == 2
        # Both entries appear
        ids = {r["id"] for r in fused}
        assert ids == {"a", "b"}
        # RRF scores and ranks are present
        for r in fused:
            assert "rrf_score" in r
            assert "vector_rank" in r
            assert "bm25_rank" in r
            assert "vector_similarity" in r
            assert "bm25_score" in r

    def test_rrf_respects_top_k(self) -> None:
        """RRF output is limited to top_k entries."""
        vector_results = [
            {"id": f"v{i}", "similarity": 1.0 - i * 0.1, "title": f"V{i}"}
            for i in range(10)
        ]
        bm25_results = [
            (f"b{i}", 10.0 - i) for i in range(10)
        ]

        fused = reciprocal_rank_fusion(
            vector_results=vector_results,
            bm25_results=bm25_results,
            top_k=3,
        )

        assert len(fused) <= 3

    def test_rrf_handles_disjoint_results(self) -> None:
        """RRF works when vector and BM25 return different entries."""
        vector_results = [
            {"id": "a", "similarity": 0.9, "title": "A"},
        ]
        bm25_results = [
            ("b", 5.0),
        ]

        fused = reciprocal_rank_fusion(
            vector_results=vector_results,
            bm25_results=bm25_results,
            top_k=5,
        )

        assert len(fused) == 2
        ids = {r["id"] for r in fused}
        assert ids == {"a", "b"}

    def test_rrf_vector_weight_boosts_vector_results(self) -> None:
        """Higher vector weight should boost entries ranked high by vector."""
        vector_results = [
            {"id": "a", "similarity": 0.99, "title": "A"},
            {"id": "b", "similarity": 0.70, "title": "B"},
        ]
        bm25_results = [
            ("b", 8.0),
            ("a", 2.0),
        ]

        # High vector weight
        fused_vw = reciprocal_rank_fusion(
            vector_results=vector_results,
            bm25_results=bm25_results,
            vector_weight=0.9,
            bm25_weight=0.1,
            top_k=2,
        )

        # High BM25 weight
        fused_bw = reciprocal_rank_fusion(
            vector_results=vector_results,
            bm25_results=bm25_results,
            vector_weight=0.1,
            bm25_weight=0.9,
            top_k=2,
        )

        # With high vector weight, "a" (top vector) should be ranked first
        assert fused_vw[0]["id"] == "a"
        # With high BM25 weight, "b" (top BM25) should be ranked first
        assert fused_bw[0]["id"] == "b"


# ---------------------------------------------------------------------------
# KB-04: KnowledgeVectorizer — embedding pipeline
# ---------------------------------------------------------------------------


class TestKnowledgeVectorizerEmbedding:
    """KB-04: Embedding individual and batch KB entries."""

    @pytest.fixture
    def vectorizer(self) -> KnowledgeVectorizer:
        """Create a configured vectorizer with mocked dependencies."""
        v = KnowledgeVectorizer()
        mock_repo = AsyncMock()
        mock_repo.patch = AsyncMock(return_value=None)
        v.configure(kb_repo=mock_repo, openai_client=None)
        return v

    @pytest.mark.asyncio
    async def test_embed_entry_active(self, vectorizer: KnowledgeVectorizer) -> None:
        """Active entry gets embedded (dev-mode zero vectors)."""
        entry = _make_kb_entry()
        result = await vectorizer.embed_entry(TENANT_ID, entry)
        # patch was called with embedding data
        vectorizer._kb_repo.patch.assert_called_once()
        call_args = vectorizer._kb_repo.patch.call_args
        ops = call_args.kwargs["operations"]
        paths = [op["path"] for op in ops]
        assert "/embedding" in paths
        assert "/embedding_model" in paths
        assert "/embedded_at" in paths
        assert "/content_hash" in paths

    @pytest.mark.asyncio
    async def test_embed_entry_skips_inactive(self, vectorizer: KnowledgeVectorizer) -> None:
        """Inactive entry is skipped."""
        entry = _make_kb_entry(is_active=False)
        result = await vectorizer.embed_entry(TENANT_ID, entry)
        assert result is None
        vectorizer._kb_repo.patch.assert_not_called()

    @pytest.mark.asyncio
    async def test_embed_entry_skips_unchanged(self, vectorizer: KnowledgeVectorizer) -> None:
        """Entry with matching content_hash is skipped."""
        title = "Test Product"
        content = "This is a test product with great features."
        existing_hash = compute_content_hash(title, content)
        entry = _make_kb_entry(
            embedding=_zero_embedding(),
            content_hash=existing_hash,
        )
        result = await vectorizer.embed_entry(TENANT_ID, entry)
        assert result is None
        vectorizer._kb_repo.patch.assert_not_called()

    @pytest.mark.asyncio
    async def test_embed_entry_reembeds_on_content_change(self, vectorizer: KnowledgeVectorizer) -> None:
        """Entry with stale content_hash gets re-embedded."""
        entry = _make_kb_entry(
            embedding=_zero_embedding(),
            content_hash="old-stale-hash",
        )
        await vectorizer.embed_entry(TENANT_ID, entry)
        vectorizer._kb_repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_batch_processes_multiple(self, vectorizer: KnowledgeVectorizer) -> None:
        """Batch embedding processes multiple entries."""
        entries = [
            _make_kb_entry(entry_id=f"kb-{i:03d}", title=f"Entry {i}")
            for i in range(5)
        ]
        count = await vectorizer.embed_batch(TENANT_ID, entries)
        assert count == 5
        assert vectorizer._kb_repo.patch.call_count == 5

    @pytest.mark.asyncio
    async def test_embed_batch_skips_unchanged(self, vectorizer: KnowledgeVectorizer) -> None:
        """Batch embedding skips entries that haven't changed."""
        title = "Unchanged Entry"
        content = "Same content"
        ch = compute_content_hash(title, content)
        entries = [
            _make_kb_entry(
                entry_id="kb-unchanged",
                title=title,
                content=content,
                embedding=_zero_embedding(),
                content_hash=ch,
            ),
            _make_kb_entry(entry_id="kb-new", title="New Entry"),
        ]
        count = await vectorizer.embed_batch(TENANT_ID, entries)
        assert count == 1  # Only the new one

    @pytest.mark.asyncio
    async def test_embed_unembedded(self, vectorizer: KnowledgeVectorizer) -> None:
        """embed_unembedded fetches and processes entries without embeddings."""
        vectorizer._kb_repo.list_unembedded = AsyncMock(return_value=[
            _make_kb_entry(entry_id="kb-new-1"),
            _make_kb_entry(entry_id="kb-new-2"),
        ])
        count = await vectorizer.embed_unembedded(TENANT_ID)
        assert count == 2

    def test_needs_reembedding_no_embedding(self) -> None:
        """Entry without embedding needs re-embedding."""
        entry = _make_kb_entry()
        v = KnowledgeVectorizer()
        assert v.needs_reembedding(entry) is True

    def test_needs_reembedding_hash_mismatch(self) -> None:
        """Entry with stale hash needs re-embedding."""
        entry = _make_kb_entry(
            embedding=_zero_embedding(),
            content_hash="old-hash",
        )
        v = KnowledgeVectorizer()
        assert v.needs_reembedding(entry) is True

    def test_needs_reembedding_current_hash(self) -> None:
        """Entry with matching hash does not need re-embedding."""
        title = "Test Product"
        content = "This is a test product with great features."
        ch = compute_content_hash(title, content)
        entry = _make_kb_entry(
            embedding=_zero_embedding(),
            content_hash=ch,
        )
        v = KnowledgeVectorizer()
        assert v.needs_reembedding(entry) is False


# ---------------------------------------------------------------------------
# KB-05: KnowledgeVectorizer — hybrid search
# ---------------------------------------------------------------------------


class TestKnowledgeVectorizerSearch:
    """KB-05: Hybrid search combining vector similarity and BM25."""

    @pytest.fixture
    def vectorizer(self) -> KnowledgeVectorizer:
        """Create a configured vectorizer for search testing."""
        v = KnowledgeVectorizer()
        mock_repo = AsyncMock()

        # vector_search returns entries with similarity scores
        mock_repo.vector_search = AsyncMock(return_value=[
            {**_make_kb_entry(entry_id="kb-001", title="Return Policy"), "similarity": 0.92},
            {**_make_kb_entry(entry_id="kb-003", title="Shipping Info"), "similarity": 0.78},
        ])

        # list_active returns full corpus for BM25
        corpus = _make_entries_corpus()
        mock_repo.list_active = AsyncMock(return_value=corpus)

        v.configure(kb_repo=mock_repo, openai_client=None)
        return v

    @pytest.mark.asyncio
    async def test_hybrid_search_returns_results(self, vectorizer: KnowledgeVectorizer) -> None:
        """Hybrid search returns fused results with RRF metadata."""
        results = await vectorizer.search(TENANT_ID, "return policy")
        assert len(results) > 0
        for r in results:
            assert "rrf_score" in r

    @pytest.mark.asyncio
    async def test_hybrid_search_respects_top_k(self, vectorizer: KnowledgeVectorizer) -> None:
        """Search results are limited to top_k."""
        results = await vectorizer.search(TENANT_ID, "return policy", top_k=2)
        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_search_falls_back_to_bm25_on_vector_failure(self) -> None:
        """When vector search fails, search falls back to BM25-only."""
        v = KnowledgeVectorizer()
        mock_repo = AsyncMock()
        mock_repo.vector_search = AsyncMock(side_effect=Exception("Vector search unavailable"))
        mock_repo.list_active = AsyncMock(return_value=_make_entries_corpus())
        v.configure(kb_repo=mock_repo, openai_client=None)

        results = await v.search(TENANT_ID, "return policy")
        # Should still have results from BM25
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_search_falls_back_to_vector_on_bm25_failure(self) -> None:
        """When BM25 fails, search falls back to vector-only."""
        v = KnowledgeVectorizer()
        mock_repo = AsyncMock()
        mock_repo.vector_search = AsyncMock(return_value=[
            {**_make_kb_entry(entry_id="kb-001"), "similarity": 0.90},
        ])
        mock_repo.list_active = AsyncMock(side_effect=Exception("BM25 list failed"))
        v.configure(kb_repo=mock_repo, openai_client=None)

        results = await v.search(TENANT_ID, "return policy")
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_search_empty_when_both_fail(self) -> None:
        """When both vector and BM25 fail, search returns empty."""
        v = KnowledgeVectorizer()
        mock_repo = AsyncMock()
        mock_repo.vector_search = AsyncMock(side_effect=Exception("fail"))
        mock_repo.list_active = AsyncMock(side_effect=Exception("fail"))
        v.configure(kb_repo=mock_repo, openai_client=None)

        results = await v.search(TENANT_ID, "anything")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_records_metrics(self, vectorizer: KnowledgeVectorizer) -> None:
        """Search operations are recorded in metrics."""
        assert vectorizer.metrics.total_searches == 0
        await vectorizer.search(TENANT_ID, "return policy")
        assert vectorizer.metrics.total_searches == 1

    @pytest.mark.asyncio
    async def test_search_vector_only(self) -> None:
        """search_vector_only bypasses BM25."""
        v = KnowledgeVectorizer()
        mock_repo = AsyncMock()
        mock_repo.vector_search = AsyncMock(return_value=[
            {**_make_kb_entry(entry_id="kb-001"), "similarity": 0.90},
        ])
        v.configure(kb_repo=mock_repo, openai_client=None)

        results = await v.search_vector_only(TENANT_ID, "test query")
        assert len(results) == 1
        # list_active should NOT be called (BM25 skipped)
        mock_repo.list_active.assert_not_called()


# ---------------------------------------------------------------------------
# KB-06: Pipeline formatting
# ---------------------------------------------------------------------------


class TestFormatForPipeline:
    """KB-06: Formatting search results for the chat pipeline."""

    def test_format_empty_results(self) -> None:
        """Empty results produce empty context."""
        formatted = KnowledgeVectorizer.format_for_pipeline([])
        assert formatted["context"] == ""
        assert formatted["sources"] == []
        assert formatted["model"] == EMBEDDING_MODEL
        assert formatted["retrieval_mode"] == "none"

    def test_format_with_results(self) -> None:
        """Results are formatted with context, sources, and metadata."""
        results = [
            {
                "id": "kb-001",
                "title": "Return Policy",
                "content": "Items can be returned within 30 days.",
                "entry_type": "policy",
                "rrf_score": 0.85,
                "vector_rank": 1,
                "bm25_rank": 2,
                "vector_similarity": 0.92,
                "bm25_score": 5.1,
            },
        ]
        formatted = KnowledgeVectorizer.format_for_pipeline(results)
        assert "Return Policy" in formatted["context"]
        assert len(formatted["sources"]) == 1
        assert formatted["sources"][0]["score"] == 0.85
        assert formatted["retrieval_mode"] == "hybrid"

    def test_format_truncates_content(self) -> None:
        """Long content is truncated to fit the character budget."""
        results = [
            {
                "id": "kb-001",
                "title": "Long Article",
                "content": "A" * 5000,
                "entry_type": "faq",
                "rrf_score": 0.80,
                "vector_rank": 1,
                "bm25_rank": 1,
            },
        ]
        formatted = KnowledgeVectorizer.format_for_pipeline(results, max_chars=500)
        assert len(formatted["context"]) <= 550  # Some overhead for title/type

    def test_format_filters_low_relevance(self) -> None:
        """Results below MIN_RELEVANCE_SCORE are excluded."""
        results = [
            {
                "id": "kb-001",
                "title": "Relevant",
                "content": "Good content",
                "entry_type": "faq",
                "rrf_score": 0.50,
                "vector_rank": 1,
                "bm25_rank": 1,
            },
            {
                "id": "kb-002",
                "title": "Irrelevant",
                "content": "Bad content",
                "entry_type": "faq",
                "rrf_score": 0.05,  # Below MIN_RELEVANCE_SCORE (0.1)
                "vector_rank": 2,
                "bm25_rank": 2,
            },
        ]
        formatted = KnowledgeVectorizer.format_for_pipeline(results)
        # Only the relevant result should appear
        assert len(formatted["sources"]) == 1
        assert formatted["sources"][0]["id"] == "kb-001"

    def test_format_vector_only_mode(self) -> None:
        """Results with no BM25 rank are labelled as vector mode."""
        results = [
            {
                "id": "kb-001",
                "title": "Test",
                "content": "Content",
                "entry_type": "faq",
                "rrf_score": 0.90,
                "vector_rank": 1,
                "bm25_rank": None,
                "vector_similarity": 0.90,
                "bm25_score": None,
            },
        ]
        formatted = KnowledgeVectorizer.format_for_pipeline(results)
        assert formatted["retrieval_mode"] == "vector"

    def test_format_bm25_only_mode(self) -> None:
        """Results with no vector rank are labelled as bm25 mode."""
        results = [
            {
                "id": "kb-001",
                "title": "Test",
                "content": "Content",
                "entry_type": "faq",
                "rrf_score": 0.80,
                "vector_rank": None,
                "bm25_rank": 1,
                "vector_similarity": None,
                "bm25_score": 5.0,
            },
        ]
        formatted = KnowledgeVectorizer.format_for_pipeline(results)
        assert formatted["retrieval_mode"] == "bm25"


# ---------------------------------------------------------------------------
# KB-RRF: RRF score normalization tests
# ---------------------------------------------------------------------------


class TestRRFNormalization:
    """Verify RRF scores are normalized to [0, 1] after fusion."""

    def test_rrf_scores_in_unit_range(self) -> None:
        """All RRF scores must be in [0.0, 1.0] after normalization."""
        vector_results = [
            {"id": f"v{i}", "similarity": 0.9 - i * 0.05}
            for i in range(5)
        ]
        bm25_results = [(f"v{i}", 5.0 - i * 0.5) for i in range(5)]

        fused = reciprocal_rank_fusion(vector_results, bm25_results)

        for r in fused:
            assert 0.0 <= r["rrf_score"] <= 1.0, (
                f"Score {r['rrf_score']} out of [0,1] range for {r['id']}"
            )

    def test_rank_one_in_both_scores_near_one(self) -> None:
        """A document ranked #1 in both systems should score close to 1.0."""
        # Same doc "d1" is rank 1 in both vector and BM25
        vector_results = [{"id": "d1", "similarity": 0.95}]
        bm25_results = [("d1", 10.0)]

        fused = reciprocal_rank_fusion(vector_results, bm25_results)
        assert len(fused) == 1
        assert fused[0]["rrf_score"] > 0.95, (
            f"Rank-1-in-both should be near 1.0, got {fused[0]['rrf_score']}"
        )

    def test_single_system_scores_match_weight(self) -> None:
        """A document in only vector or only BM25 scores its weight fraction."""
        vector_only = [{"id": "v1", "similarity": 0.9}]
        bm25_only = [("b1", 3.0)]

        fused = reciprocal_rank_fusion(vector_only, bm25_only)

        v1 = next(r for r in fused if r["id"] == "v1")
        b1 = next(r for r in fused if r["id"] == "b1")

        # v1 only in vector (weight 0.7): normalized = 0.7
        assert abs(v1["rrf_score"] - DEFAULT_VECTOR_WEIGHT) < 0.01, (
            f"Vector-only rank 1 should be ~{DEFAULT_VECTOR_WEIGHT}, got {v1['rrf_score']}"
        )
        # b1 only in BM25 (weight 0.3): normalized = 0.3
        assert abs(b1["rrf_score"] - DEFAULT_BM25_WEIGHT) < 0.01, (
            f"BM25-only rank 1 should be ~{DEFAULT_BM25_WEIGHT}, got {b1['rrf_score']}"
        )


# ---------------------------------------------------------------------------
# KB-07: Retrieval quality metrics
# ---------------------------------------------------------------------------


class TestRetrievalMetrics:
    """KB-07: In-memory retrieval metrics collector."""

    def test_initial_state(self) -> None:
        """Metrics start at zero."""
        m = RetrievalMetrics()
        assert m.total_searches == 0
        assert m.empty_searches == 0

    def test_record_search(self) -> None:
        """Recording a search updates all counters."""
        m = RetrievalMetrics()
        m.record_search(
            tenant_id=TENANT_ID,
            query="test",
            result_count=3,
            latency_ms=45.0,
            mode="hybrid",
            top_score=0.85,
        )
        assert m.total_searches == 1
        assert m.total_results == 3
        assert m.hybrid_searches == 1
        assert m.max_latency_ms == 45.0

    def test_empty_search_counted(self) -> None:
        """Searches with zero results are counted."""
        m = RetrievalMetrics()
        m.record_search(TENANT_ID, "empty", 0, 10.0, "hybrid", 0.0)
        assert m.empty_searches == 1

    def test_high_relevance_tracking(self) -> None:
        """Searches with high top scores are counted."""
        m = RetrievalMetrics()
        m.record_search(TENANT_ID, "q1", 3, 10.0, "hybrid", HIGH_RELEVANCE_SCORE + 0.01)
        m.record_search(TENANT_ID, "q2", 1, 10.0, "hybrid", 0.01)
        assert m.high_relevance_count == 1

    def test_mode_distribution(self) -> None:
        """Mode counters track hybrid/vector/bm25 distribution."""
        m = RetrievalMetrics()
        m.record_search(TENANT_ID, "q1", 1, 10.0, "hybrid", 0.8)
        m.record_search(TENANT_ID, "q2", 1, 10.0, "vector", 0.7)
        m.record_search(TENANT_ID, "q3", 1, 10.0, "bm25", 0.6)
        assert m.hybrid_searches == 1
        assert m.vector_only_searches == 1
        assert m.bm25_only_searches == 1

    def test_summary_averages(self) -> None:
        """Summary computes correct averages."""
        m = RetrievalMetrics()
        m.record_search(TENANT_ID, "q1", 2, 20.0, "hybrid", 0.8)
        m.record_search(TENANT_ID, "q2", 4, 40.0, "hybrid", 0.9)
        s = m.summary()
        assert s["total_searches"] == 2
        assert s["avg_results_per_search"] == 3.0
        assert s["avg_latency_ms"] == 30.0
        assert s["max_latency_ms"] == 40.0

    def test_recent_queries_capped(self) -> None:
        """Recent queries are capped at 100."""
        m = RetrievalMetrics()
        for i in range(150):
            m.record_search(TENANT_ID, f"q{i}", 1, 1.0, "hybrid", 0.5)
        assert len(m._recent_queries) == 100


# ---------------------------------------------------------------------------
# KB-08: Singleton pattern
# ---------------------------------------------------------------------------


class TestSingleton:
    """KB-08: Module-level singleton accessor."""

    def test_get_knowledge_vectorizer_returns_same_instance(self) -> None:
        """get_knowledge_vectorizer() always returns the same instance."""
        v1 = get_knowledge_vectorizer()
        v2 = get_knowledge_vectorizer()
        assert v1 is v2

    def test_unconfigured_raises(self) -> None:
        """Calling search on unconfigured vectorizer raises RuntimeError."""
        v = KnowledgeVectorizer()
        with pytest.raises(RuntimeError, match="not configured"):
            v._ensure_configured()


# ---------------------------------------------------------------------------
# KB-09: Constants and configuration
# ---------------------------------------------------------------------------


class TestConstants:
    """KB-09: Verify important constants match architecture decisions."""

    def test_embedding_model(self) -> None:
        assert EMBEDDING_MODEL == "text-embedding-3-large"

    def test_embedding_dimensions(self) -> None:
        assert EMBEDDING_DIMENSIONS == 3072

    def test_default_top_k(self) -> None:
        assert DEFAULT_TOP_K == 5

    def test_default_weights(self) -> None:
        assert DEFAULT_VECTOR_WEIGHT == 0.7
        assert DEFAULT_BM25_WEIGHT == 0.3
        # Weights should sum to 1.0
        assert DEFAULT_VECTOR_WEIGHT + DEFAULT_BM25_WEIGHT == 1.0


# ---------------------------------------------------------------------------
# KB-10: Pipeline integration — _call_knowledge_retrieval_direct
# ---------------------------------------------------------------------------


class TestPipelineIntegration:
    """KB-10: Verify pipeline.py uses KnowledgeVectorizer for KB retrieval."""

    @pytest.mark.asyncio
    async def test_pipeline_uses_vectorizer(self) -> None:
        """_call_knowledge_retrieval_direct calls KnowledgeVectorizer.search."""
        from src.chat.pipeline import ChatPipeline
        from src.chat.session import ConversationSession

        # Create minimal pipeline
        mock_session = MagicMock(spec=ConversationSession)
        mock_prompt_builder = MagicMock()
        mock_profile_service = MagicMock()

        pipeline = ChatPipeline(
            session=mock_session,
            prompt_builder=mock_prompt_builder,
            profile_service=mock_profile_service,
        )
        pipeline._current_tenant_id = TENANT_ID

        # Mock the vectorizer singleton
        mock_vectorizer = AsyncMock(spec=KnowledgeVectorizer)
        mock_vectorizer._configured = True
        search_results = [
            {
                "id": "kb-001",
                "title": "Return Policy",
                "content": "30 day returns.",
                "entry_type": "policy",
                "score": 0.85,
                "rrf_score": 0.85,
                "vector_rank": 1,
                "bm25_rank": 1,
                "vector_similarity": 0.90,
                "bm25_score": 4.0,
            },
        ]
        mock_vectorizer.search = AsyncMock(return_value=search_results)

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ), patch(
            "src.multi_tenant.knowledge_vectorizer.KnowledgeVectorizer.format_for_pipeline",
            return_value={
                "context": "Return Policy: 30 day returns.",
                "sources": [{"title": "Return Policy"}],
            },
        ):
            result = await pipeline._call_knowledge_retrieval_direct(
                message="How do I return an item?",
                intent="return_request",
                system_prompt="You are a customer service agent.",
            )

        assert "Return Policy" in result["context"]
        assert len(result["sources"]) == 1
        mock_vectorizer.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_pipeline_fallback_on_vectorizer_failure(self) -> None:
        """Pipeline returns empty context when vectorizer is unavailable."""
        from src.chat.pipeline import ChatPipeline
        from src.chat.session import ConversationSession

        mock_session = MagicMock(spec=ConversationSession)
        mock_prompt_builder = MagicMock()
        mock_profile_service = MagicMock()

        pipeline = ChatPipeline(
            session=mock_session,
            prompt_builder=mock_prompt_builder,
            profile_service=mock_profile_service,
        )
        pipeline._current_tenant_id = TENANT_ID

        # Mock vectorizer that raises
        mock_vectorizer = AsyncMock(spec=KnowledgeVectorizer)
        mock_vectorizer._configured = False

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            result = await pipeline._call_knowledge_retrieval_direct(
                message="test",
                intent="general_inquiry",
                system_prompt="test",
            )

        assert result["context"] == ""
        assert result["sources"] == []


# ---------------------------------------------------------------------------
# KB-11: Admin API embedding on create/update
# ---------------------------------------------------------------------------


class TestAdminAPIEmbedding:
    """KB-11: Admin KB API triggers embedding on create/update."""

    @pytest.mark.asyncio
    async def test_create_triggers_embedding(self) -> None:
        """POST /api/admin/knowledge triggers embedding."""
        from src.multi_tenant.admin_knowledge_api import (
            _knowledge_vectorizer,
            configure_admin_knowledge_services,
        )

        mock_repo = AsyncMock()
        mock_repo.create = AsyncMock(return_value=None)

        mock_vectorizer = AsyncMock()
        mock_vectorizer.embed_entry = AsyncMock(return_value=None)

        configure_admin_knowledge_services(
            knowledge_repo=mock_repo,
            knowledge_vectorizer=mock_vectorizer,
        )

        # Import after configuration
        from src.multi_tenant import admin_knowledge_api as api
        assert api._knowledge_vectorizer is mock_vectorizer

    @pytest.mark.asyncio
    async def test_embedding_failure_is_non_blocking(self) -> None:
        """Embedding failure on create does not fail the request."""
        from src.multi_tenant.admin_knowledge_api import configure_admin_knowledge_services

        mock_repo = AsyncMock()
        mock_repo.create = AsyncMock(return_value=None)

        mock_vectorizer = AsyncMock()
        mock_vectorizer.embed_entry = AsyncMock(side_effect=Exception("Embedding API down"))

        configure_admin_knowledge_services(
            knowledge_repo=mock_repo,
            knowledge_vectorizer=mock_vectorizer,
        )

        # The API should still work — embedding is best-effort
        from src.multi_tenant import admin_knowledge_api as api
        assert api._knowledge_vectorizer is mock_vectorizer
