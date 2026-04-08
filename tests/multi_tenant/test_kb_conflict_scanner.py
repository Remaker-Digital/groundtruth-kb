"""Tests for KB conflict and duplication scanner.

Covers:
    - Text processing helpers (title normalization, trigrams, sentence extraction)
    - Title similarity (trigram Jaccard: exact, near, unrelated)
    - Content overlap (sentence Jaccard: high/medium/low/zero)
    - Factual conflict detection (duration, price, percentage, email, boolean)
    - Conflict classification (all 4 types with correct severity)
    - Resolution text generation
    - Full scan with mock KB entries (duplicates, conflicts, clean)
    - Edge cases (empty KB, single entry, no embeddings, cache behaviour)
    - Module-level singleton

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import time
from unittest.mock import AsyncMock, patch

import pytest

from src.multi_tenant.kb_conflict_scanner import (
    CONFLICT_SIMILARITY,
    LARGE_KB_THRESHOLD,
    MAX_CONFLICTS_REPORTED,
    NEAR_DUPLICATE_OVERLAP,
    NEAR_DUPLICATE_SIMILARITY,
    SCAN_CACHE_TTL,
    TITLE_SIMILARITY_THRESHOLD,
    ConflictPair,
    ConflictSeverity,
    ConflictType,
    KBConflictScanner,
    ScanResult,
    _detect_factual_conflicts,
    _extract_sentences,
    _generate_resolution,
    _normalize_title,
    _sentence_jaccard,
    _trigram_jaccard,
    _trigrams,
    get_conflict_scanner,
)


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _make_entry(
    entry_id: str = "e1",
    title: str = "Test Article",
    content: str = "This is test content for the article.",
    entry_type: str = "faq",
    language: str = "en",
    embedding: list[float] | None = None,
) -> dict:
    """Create a mock KB entry dict."""
    entry = {
        "id": entry_id,
        "title": title,
        "content": content,
        "entry_type": entry_type,
        "language": language,
    }
    if embedding is not None:
        entry["embedding"] = embedding
    return entry


def _make_embedding(seed: float, dim: int = 8) -> list[float]:
    """Create a deterministic mock embedding vector."""
    import math

    return [math.sin(seed * (i + 1)) for i in range(dim)]


def _make_similar_embedding(base: list[float], noise: float = 0.01) -> list[float]:
    """Create an embedding very similar to base (high cosine similarity)."""
    return [v + noise * (i % 3 - 1) for i, v in enumerate(base)]


def _make_orthogonal_embedding(base: list[float]) -> list[float]:
    """Create an embedding dissimilar to base (low cosine similarity)."""
    return [-v + 0.5 for v in base]


# ---------------------------------------------------------------------------
# Test: Constants
# ---------------------------------------------------------------------------


class TestConstants:
    """Verify constant values haven't drifted from plan."""

    def test_near_duplicate_similarity_threshold(self):
        assert NEAR_DUPLICATE_SIMILARITY == 0.92

    def test_conflict_similarity_threshold(self):
        assert CONFLICT_SIMILARITY == 0.85

    def test_title_similarity_threshold(self):
        assert TITLE_SIMILARITY_THRESHOLD == 0.6

    def test_near_duplicate_overlap(self):
        assert NEAR_DUPLICATE_OVERLAP == 0.70

    def test_scan_cache_ttl(self):
        assert SCAN_CACHE_TTL == 300

    def test_large_kb_threshold(self):
        assert LARGE_KB_THRESHOLD == 200

    def test_max_conflicts_reported(self):
        assert MAX_CONFLICTS_REPORTED == 100


# ---------------------------------------------------------------------------
# Test: Enums and data classes
# ---------------------------------------------------------------------------


class TestEnumsAndDataClasses:
    """Verify enums and dataclass construction."""

    def test_conflict_type_values(self):
        assert ConflictType.NEAR_DUPLICATE == "near_duplicate"
        assert ConflictType.CONFLICTING == "conflicting"
        assert ConflictType.TOPICAL_OVERLAP == "topical_overlap"
        assert ConflictType.SIMILAR_TITLES == "similar_titles"

    def test_conflict_severity_values(self):
        assert ConflictSeverity.HIGH == "high"
        assert ConflictSeverity.MEDIUM == "medium"
        assert ConflictSeverity.LOW == "low"

    def test_conflict_pair_defaults(self):
        pair = ConflictPair(
            entry_a_id="a",
            entry_a_title="Title A",
            entry_b_id="b",
            entry_b_title="Title B",
            conflict_type=ConflictType.NEAR_DUPLICATE,
            severity=ConflictSeverity.HIGH,
            embedding_similarity=0.95,
            content_overlap=0.80,
            title_similarity=0.90,
        )
        assert pair.conflicting_facts == []
        assert pair.resolution == ""

    def test_scan_result_defaults(self):
        result = ScanResult(
            tenant_id="t1",
            scanned_at="2026-01-01T00:00:00Z",
            total_entries_scanned=10,
            entries_with_embeddings=8,
            entries_without_embeddings=2,
        )
        assert result.conflicts == []
        assert result.high_count == 0
        assert result.medium_count == 0
        assert result.low_count == 0
        assert result.scan_duration_ms == 0


# ---------------------------------------------------------------------------
# Test: Title normalization
# ---------------------------------------------------------------------------


class TestNormalizeTitle:
    """Test _normalize_title helper."""

    def test_lowercase(self):
        assert _normalize_title("Return Policy") == "return policy"

    def test_strip_punctuation(self):
        assert _normalize_title("Return's Policy!") == "return s policy"

    def test_collapse_whitespace(self):
        assert _normalize_title("Return   Policy") == "return policy"

    def test_strip_edges(self):
        assert _normalize_title("  Return Policy  ") == "return policy"

    def test_empty_string(self):
        assert _normalize_title("") == ""


# ---------------------------------------------------------------------------
# Test: Trigrams
# ---------------------------------------------------------------------------


class TestTrigrams:
    """Test _trigrams helper."""

    def test_basic(self):
        result = _trigrams("abcde")
        assert result == {"abc", "bcd", "cde"}

    def test_short_string(self):
        assert _trigrams("ab") == {"ab"}

    def test_single_char(self):
        assert _trigrams("a") == {"a"}

    def test_empty(self):
        assert _trigrams("") == set()


# ---------------------------------------------------------------------------
# Test: Trigram Jaccard title similarity
# ---------------------------------------------------------------------------


class TestTitleSimilarity:
    """Test _trigram_jaccard for title comparison."""

    def test_exact_match(self):
        sim = _trigram_jaccard("Return Policy", "Return Policy")
        assert sim == 1.0

    def test_case_insensitive(self):
        sim = _trigram_jaccard("Return Policy", "return policy")
        assert sim == 1.0

    def test_near_match(self):
        sim = _trigram_jaccard("Return Policy", "Returns Policy")
        assert sim > 0.6  # Very similar titles

    def test_plural_variant(self):
        sim = _trigram_jaccard("Return Policy", "Our Return Policy")
        assert sim > 0.5  # Overlapping, above threshold

    def test_unrelated(self):
        sim = _trigram_jaccard("Return Policy", "Shipping Guide")
        assert sim < 0.3  # Very different

    def test_empty_a(self):
        assert _trigram_jaccard("", "Return Policy") == 0.0

    def test_empty_b(self):
        assert _trigram_jaccard("Return Policy", "") == 0.0

    def test_both_empty(self):
        assert _trigram_jaccard("", "") == 0.0


# ---------------------------------------------------------------------------
# Test: Sentence extraction
# ---------------------------------------------------------------------------


class TestExtractSentences:
    """Test _extract_sentences helper."""

    def test_basic_split(self):
        text = "This is sentence one. This is sentence two. This is sentence three."
        sentences = _extract_sentences(text)
        assert len(sentences) >= 2

    def test_skips_short_fragments(self):
        text = "OK. This is a proper sentence with enough length."
        sentences = _extract_sentences(text)
        # "OK" is <= 10 chars, should be filtered out
        assert all(len(s) > 10 for s in sentences)

    def test_newline_split(self):
        text = "First paragraph here\nSecond paragraph here"
        sentences = _extract_sentences(text)
        assert len(sentences) == 2

    def test_empty_string(self):
        assert _extract_sentences("") == set()


# ---------------------------------------------------------------------------
# Test: Sentence Jaccard content overlap
# ---------------------------------------------------------------------------


class TestContentOverlap:
    """Test _sentence_jaccard for content overlap measurement."""

    def test_identical_content(self):
        content = "This is a complete sentence about returns. We accept returns within thirty days."
        assert _sentence_jaccard(content, content) == 1.0

    def test_no_overlap(self):
        a = "We offer free shipping on all orders over fifty dollars."
        b = "Returns must be initiated within fourteen business days."
        sim = _sentence_jaccard(a, b)
        assert sim == 0.0

    def test_partial_overlap(self):
        a = "We offer free shipping. Returns accepted within 30 days. Contact support for help."
        b = "We offer free shipping. International orders may take longer. Contact support for help."
        sim = _sentence_jaccard(a, b)
        assert 0.0 < sim < 1.0

    def test_high_overlap(self):
        a = "We offer free shipping. Returns accepted within 30 days. Contact support for help."
        b = "We offer free shipping. Returns accepted within 30 days. See our policy page for details."
        sim = _sentence_jaccard(a, b)
        assert sim > 0.3

    def test_empty_a(self):
        assert _sentence_jaccard("", "Something here.") == 0.0

    def test_empty_b(self):
        assert _sentence_jaccard("Something here.", "") == 0.0


# ---------------------------------------------------------------------------
# Test: Factual conflict detection
# ---------------------------------------------------------------------------


class TestFactualConflictDetection:
    """Test _detect_factual_conflicts regex-based conflict finder."""

    def test_duration_conflict(self):
        a = "Returns must be made within 30 days of purchase."
        b = "Returns must be made within 14 days of purchase."
        conflicts = _detect_factual_conflicts(a, b)
        assert len(conflicts) >= 1
        assert any("day" in c.lower() for c in conflicts)

    def test_same_duration_no_conflict(self):
        a = "Returns must be made within 30 days."
        b = "You have 30 days to return items."
        conflicts = _detect_factual_conflicts(a, b)
        # Same duration value — no conflict
        duration_conflicts = [c for c in conflicts if "Duration" in c]
        assert len(duration_conflicts) == 0

    def test_price_conflict(self):
        a = "Shipping costs $5.99 for standard delivery."
        b = "Shipping costs $9.99 for standard delivery."
        conflicts = _detect_factual_conflicts(a, b)
        assert any("price" in c.lower() or "Price" in c for c in conflicts)

    def test_percentage_conflict(self):
        a = "We offer a 10% discount on first orders."
        b = "New customers get 15% off their first order."
        conflicts = _detect_factual_conflicts(a, b)
        assert any("percent" in c.lower() or "Percent" in c for c in conflicts)

    def test_email_conflict(self):
        a = "Contact us at support@example.com for returns."
        b = "Email returns@example.com for return requests."
        conflicts = _detect_factual_conflicts(a, b)
        assert any("email" in c.lower() or "Email" in c for c in conflicts)

    def test_boolean_contradiction_free_shipping(self):
        a = "We provide free shipping on all orders."
        b = "Shipping cost applies to all orders."
        conflicts = _detect_factual_conflicts(a, b)
        assert any("contradiction" in c.lower() or "Contradiction" in c for c in conflicts)

    def test_boolean_contradiction_no_returns(self):
        a = "This item has no returns allowed."
        b = "Returns accepted for this item within 7 days."
        conflicts = _detect_factual_conflicts(a, b)
        assert any("contradiction" in c.lower() or "Contradiction" in c for c in conflicts)

    def test_no_conflicts(self):
        a = "We sell high-quality widgets made in the USA."
        b = "Our customer support team is available 24/7."
        conflicts = _detect_factual_conflicts(a, b)
        assert len(conflicts) == 0

    def test_multiple_conflicts(self):
        a = "Returns within 30 days. Shipping costs $5.99. Contact support@shop.com."
        b = "Returns within 14 days. Shipping costs $9.99. Contact help@shop.com."
        conflicts = _detect_factual_conflicts(a, b)
        assert len(conflicts) >= 3  # duration, price, email


# ---------------------------------------------------------------------------
# Test: Resolution text generation
# ---------------------------------------------------------------------------


class TestResolutionGeneration:
    """Test _generate_resolution template rendering."""

    def test_near_duplicate_resolution(self):
        text = _generate_resolution(ConflictType.NEAR_DUPLICATE, [])
        assert "merge" in text.lower() or "Merge" in text

    def test_conflicting_resolution_with_facts(self):
        facts = ["Duration (day): 30 vs 14"]
        text = _generate_resolution(ConflictType.CONFLICTING, facts)
        assert "authoritative" in text.lower() or "Duration" in text

    def test_conflicting_resolution_includes_facts(self):
        facts = ["Duration (day): 30 vs 14", "Prices differ: $5.99 vs $9.99"]
        text = _generate_resolution(ConflictType.CONFLICTING, facts)
        assert "Specific conflicts found" in text
        assert "Duration" in text

    def test_topical_overlap_resolution(self):
        text = _generate_resolution(ConflictType.TOPICAL_OVERLAP, [])
        assert "similar topics" in text.lower() or "intentionally" in text.lower()

    def test_similar_titles_resolution(self):
        text = _generate_resolution(ConflictType.SIMILAR_TITLES, [])
        assert "title" in text.lower() or "renaming" in text.lower()

    def test_facts_truncated_at_5(self):
        facts = [f"Fact {i}" for i in range(10)]
        text = _generate_resolution(ConflictType.CONFLICTING, facts)
        # Should include at most 5 facts in the appended line
        assert "Fact 0" in text
        assert "Fact 4" in text
        # Fact 5 should NOT appear
        assert "Fact 5" not in text


# ---------------------------------------------------------------------------
# Test: Conflict classification
# ---------------------------------------------------------------------------


class TestClassifyConflict:
    """Test KBConflictScanner._classify_conflict."""

    def setup_method(self):
        self.scanner = KBConflictScanner()

    def _entry_a(self, **kwargs):
        return _make_entry(entry_id="a", title="Return Policy", **kwargs)

    def _entry_b(self, **kwargs):
        return _make_entry(entry_id="b", title="Returns Policy", **kwargs)

    def test_near_duplicate(self):
        """High embedding sim + high content overlap = near duplicate."""
        pair = self.scanner._classify_conflict(
            self._entry_a(), self._entry_b(),
            embedding_sim=0.95,
            content_overlap=0.80,
            title_sim=0.0,
            conflicting_facts=[],
        )
        assert pair is not None
        assert pair.conflict_type == ConflictType.NEAR_DUPLICATE
        assert pair.severity == ConflictSeverity.HIGH

    def test_conflicting(self):
        """High embedding sim + medium overlap + factual conflicts = conflicting."""
        pair = self.scanner._classify_conflict(
            self._entry_a(), self._entry_b(),
            embedding_sim=0.90,
            content_overlap=0.55,
            title_sim=0.0,
            conflicting_facts=["Duration (day): 30 vs 14"],
        )
        assert pair is not None
        assert pair.conflict_type == ConflictType.CONFLICTING
        assert pair.severity == ConflictSeverity.HIGH

    def test_topical_overlap_medium(self):
        """High embedding sim + medium overlap + no facts = topical overlap (medium)."""
        pair = self.scanner._classify_conflict(
            self._entry_a(), self._entry_b(),
            embedding_sim=0.88,
            content_overlap=0.50,
            title_sim=0.0,
            conflicting_facts=[],
        )
        assert pair is not None
        assert pair.conflict_type == ConflictType.TOPICAL_OVERLAP
        assert pair.severity == ConflictSeverity.MEDIUM

    def test_topical_overlap_low(self):
        """High embedding sim + low content overlap = low severity."""
        pair = self.scanner._classify_conflict(
            self._entry_a(), self._entry_b(),
            embedding_sim=0.87,
            content_overlap=0.20,
            title_sim=0.0,
            conflicting_facts=[],
        )
        assert pair is not None
        assert pair.conflict_type == ConflictType.TOPICAL_OVERLAP
        assert pair.severity == ConflictSeverity.LOW

    def test_below_threshold_returns_none(self):
        """Below CONFLICT_SIMILARITY threshold returns None."""
        pair = self.scanner._classify_conflict(
            self._entry_a(), self._entry_b(),
            embedding_sim=0.70,
            content_overlap=0.50,
            title_sim=0.0,
            conflicting_facts=[],
        )
        assert pair is None

    def test_title_similarity_computed_when_zero(self):
        """Title sim=0.0 triggers internal calculation."""
        pair = self.scanner._classify_conflict(
            self._entry_a(), self._entry_b(),
            embedding_sim=0.95,
            content_overlap=0.80,
            title_sim=0.0,
            conflicting_facts=[],
        )
        assert pair is not None
        assert pair.title_similarity > 0.0  # Should be computed

    def test_conflicting_facts_included(self):
        """Factual conflicts are preserved in the pair."""
        facts = ["Duration (day): 30 vs 14", "Prices differ: $5 vs $10"]
        pair = self.scanner._classify_conflict(
            self._entry_a(), self._entry_b(),
            embedding_sim=0.90,
            content_overlap=0.55,
            title_sim=0.0,
            conflicting_facts=facts,
        )
        assert pair is not None
        assert pair.conflicting_facts == facts


# ---------------------------------------------------------------------------
# Test: Full scan — mocked repository
# ---------------------------------------------------------------------------


class TestFullScan:
    """Test KBConflictScanner.scan() with mocked KB repository."""

    def setup_method(self):
        self.scanner = KBConflictScanner()
        self.mock_repo = AsyncMock()
        self.scanner.configure(kb_repo=self.mock_repo)

    @pytest.mark.asyncio
    async def test_empty_kb(self):
        """Empty knowledge base returns zero conflicts."""
        self.mock_repo.list_active = AsyncMock(return_value=[])
        result = await self.scanner.scan("tenant-1")
        assert result.total_entries_scanned == 0
        assert result.conflicts == []
        assert result.high_count == 0

    @pytest.mark.asyncio
    async def test_single_entry(self):
        """Single entry cannot have conflicts."""
        self.mock_repo.list_active = AsyncMock(return_value=[
            _make_entry("e1", "Return Policy", "Content here.", embedding=[1.0, 0.0, 0.0]),
        ])
        result = await self.scanner.scan("tenant-1")
        assert result.total_entries_scanned == 1
        assert len(result.conflicts) == 0

    @pytest.mark.asyncio
    async def test_no_embeddings(self):
        """Entries without embeddings skip Phase 1, may still match on Phase 2."""
        entries = [
            _make_entry("e1", "Return Policy", "Content A."),
            _make_entry("e2", "Returns Policy", "Different content B."),
        ]
        self.mock_repo.list_active = AsyncMock(return_value=entries)
        result = await self.scanner.scan("tenant-1")
        assert result.entries_without_embeddings == 2
        # Phase 2 should catch the similar titles
        title_conflicts = [c for c in result.conflicts if c.conflict_type == ConflictType.SIMILAR_TITLES]
        assert len(title_conflicts) >= 1

    @pytest.mark.asyncio
    async def test_near_duplicate_detection(self):
        """Two nearly identical entries with similar embeddings are flagged as near-duplicates."""
        base_emb = _make_embedding(1.0, dim=16)
        similar_emb = _make_similar_embedding(base_emb, noise=0.001)
        shared_content = (
            "Our return policy allows returns within 30 days of purchase. "
            "Items must be in original condition. Contact support for assistance. "
            "Refunds are processed within 5 business days."
        )
        entries = [
            _make_entry("e1", "Return Policy", shared_content, embedding=base_emb),
            _make_entry("e2", "Return Policy Copy", shared_content, embedding=similar_emb),
        ]
        self.mock_repo.list_active = AsyncMock(return_value=entries)

        with patch("src.multi_tenant.semantic_cache.cosine_similarity", return_value=0.98):
            result = await self.scanner.scan("tenant-1", force=True)

        assert result.high_count >= 1
        near_dupes = [c for c in result.conflicts if c.conflict_type == ConflictType.NEAR_DUPLICATE]
        assert len(near_dupes) >= 1

    @pytest.mark.asyncio
    async def test_conflicting_entries_detected(self):
        """Entries with same topic but different facts are flagged as conflicting."""
        base_emb = _make_embedding(2.0, dim=16)
        similar_emb = _make_similar_embedding(base_emb, noise=0.002)
        # Content shares 5 of 8 unique sentences (62.5% overlap) — within the 40-70% CONFLICTING range.
        # The 3 differing sentences contain factual conflicts (duration, price, email).
        content_a = (
            "Our store has a comprehensive return policy for all customers. "
            "Returns must be made within 30 days of purchase. "
            "Shipping costs $5.99 for standard delivery. "
            "Items must be in original packaging. "
            "Receipts are required for all returns. "
            "We process refunds within five business days. "
            "Free exchanges are available for all items. "
            "Contact support@shop.com for help with any issues."
        )
        content_b = (
            "Our store has a comprehensive return policy for all customers. "
            "Returns must be made within 14 days of purchase. "
            "Shipping costs $9.99 for standard delivery. "
            "Items must be in original packaging. "
            "Receipts are required for all returns. "
            "We process refunds within five business days. "
            "Free exchanges are available for all items. "
            "Contact help@shop.com for assistance with any issues."
        )
        entries = [
            _make_entry("e1", "Return Policy", content_a, embedding=base_emb),
            _make_entry("e2", "Refund Policy", content_b, embedding=similar_emb),
        ]
        self.mock_repo.list_active = AsyncMock(return_value=entries)

        with patch("src.multi_tenant.semantic_cache.cosine_similarity", return_value=0.90):
            result = await self.scanner.scan("tenant-1", force=True)

        # Should find conflicting entries with factual differences (HIGH severity)
        high_conflicts = [c for c in result.conflicts if c.severity == ConflictSeverity.HIGH]
        assert len(high_conflicts) >= 1
        # Verify factual conflicts were detected
        conflicting = [c for c in high_conflicts if c.conflict_type == ConflictType.CONFLICTING]
        assert len(conflicting) >= 1
        assert len(conflicting[0].conflicting_facts) >= 1

    @pytest.mark.asyncio
    async def test_clean_kb_no_conflicts(self):
        """Completely different entries produce no conflicts."""
        entries = [
            _make_entry("e1", "Return Policy", "Returns within 30 days.",
                        embedding=_make_embedding(1.0)),
            _make_entry("e2", "Shipping Guide", "We ship worldwide via USPS.",
                        embedding=_make_orthogonal_embedding(_make_embedding(1.0))),
        ]
        self.mock_repo.list_active = AsyncMock(return_value=entries)

        with patch("src.multi_tenant.semantic_cache.cosine_similarity", return_value=0.20):
            result = await self.scanner.scan("tenant-1", force=True)

        assert result.high_count == 0
        assert result.medium_count == 0
        # May have title-based low matches, but no embedding-based

    @pytest.mark.asyncio
    async def test_cross_type_not_compared_phase1(self):
        """Entries of different entry_types are not compared in Phase 1 embedding check."""
        base_emb = _make_embedding(3.0, dim=16)
        # Same entry_type group has 1 entry each — no pairwise comparison possible within group
        entries = [
            _make_entry("e1", "Widget Guide", "Details about widgets.",
                        entry_type="product", embedding=base_emb),
            _make_entry("e2", "Widget FAQ", "Frequently asked questions about widgets.",
                        entry_type="faq", embedding=base_emb),
        ]
        self.mock_repo.list_active = AsyncMock(return_value=entries)

        # Track cosine_similarity calls — should NOT be called since each group has only 1 entry
        call_count = [0]
        try:
            from src.multi_tenant.semantic_cache import cosine_similarity as _orig  # noqa: F401
        except ImportError:
            pass

        def tracking_cos(a, b):
            call_count[0] += 1
            return 0.30  # Low similarity

        with patch("src.multi_tenant.semantic_cache.cosine_similarity", side_effect=tracking_cos):
            await self.scanner.scan("tenant-1", force=True)
            # cosine_similarity should not be called — each entry_type group has only 1 entry
            assert call_count[0] == 0

    @pytest.mark.asyncio
    async def test_cross_language_not_compared(self):
        """Entries in different languages are not compared in Phase 2."""
        entries = [
            _make_entry("e1", "Return Policy", "Returns within 30 days.", language="en"),
            _make_entry("e2", "Politique de retour", "Retours dans 30 jours.", language="fr"),
        ]
        self.mock_repo.list_active = AsyncMock(return_value=entries)
        result = await self.scanner.scan("tenant-1", force=True)
        assert len(result.conflicts) == 0

    @pytest.mark.asyncio
    async def test_scan_result_fields(self):
        """Verify all ScanResult fields are populated."""
        entries = [
            _make_entry("e1", "Article A", "Content A.", embedding=[1.0]),
            _make_entry("e2", "Article B", "Content B."),
        ]
        self.mock_repo.list_active = AsyncMock(return_value=entries)
        result = await self.scanner.scan("tenant-1", force=True)

        assert result.tenant_id == "tenant-1"
        assert result.scanned_at  # Non-empty ISO timestamp
        assert result.total_entries_scanned == 2
        assert result.entries_with_embeddings == 1
        assert result.entries_without_embeddings == 1
        assert result.scan_duration_ms >= 0

    @pytest.mark.asyncio
    async def test_severity_sorting(self):
        """Conflicts are sorted by severity (high first), then by embedding similarity descending."""
        base_emb = _make_embedding(4.0, dim=16)
        entries = [
            _make_entry("e1", "Policy A", "Returns within 30 days. Contact support@a.com.",
                        embedding=base_emb),
            _make_entry("e2", "Policy B", "Returns within 14 days. Contact support@b.com.",
                        embedding=_make_similar_embedding(base_emb, 0.001)),
            _make_entry("e3", "Policy C", "Completely different topic about widgets.",
                        embedding=_make_similar_embedding(base_emb, 0.005)),
        ]
        self.mock_repo.list_active = AsyncMock(return_value=entries)

        # Mock cosine_similarity to return different values for different pairs
        call_count = [0]
        def mock_cosine(a, b):
            call_count[0] += 1
            if call_count[0] == 1:
                return 0.90  # e1-e2: high (conflicting)
            return 0.86  # other pairs: medium or low

        with patch("src.multi_tenant.semantic_cache.cosine_similarity", side_effect=mock_cosine):
            result = await self.scanner.scan("tenant-1", force=True)

        if len(result.conflicts) >= 2:
            # First conflict should be higher severity
            severity_order = {"high": 0, "medium": 1, "low": 2}
            for i in range(len(result.conflicts) - 1):
                curr = severity_order[result.conflicts[i].severity.value]
                nxt = severity_order[result.conflicts[i + 1].severity.value]
                assert curr <= nxt


# ---------------------------------------------------------------------------
# Test: Scan cache behaviour
# ---------------------------------------------------------------------------


class TestScanCache:
    """Test scan result caching."""

    def setup_method(self):
        self.scanner = KBConflictScanner()
        self.mock_repo = AsyncMock()
        self.scanner.configure(kb_repo=self.mock_repo)

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """Second scan returns cached result without calling list_active again."""
        self.mock_repo.list_active = AsyncMock(return_value=[])
        await self.scanner.scan("tenant-1")
        await self.scanner.scan("tenant-1")  # Should hit cache
        assert self.mock_repo.list_active.call_count == 1

    @pytest.mark.asyncio
    async def test_force_bypasses_cache(self):
        """force=True bypasses cache."""
        self.mock_repo.list_active = AsyncMock(return_value=[])
        await self.scanner.scan("tenant-1")
        await self.scanner.scan("tenant-1", force=True)
        assert self.mock_repo.list_active.call_count == 2

    def test_get_cached_result_miss(self):
        """get_cached_result returns None when no scan has run."""
        assert self.scanner.get_cached_result("unknown-tenant") is None

    @pytest.mark.asyncio
    async def test_cache_expiry(self):
        """Cached result expires after TTL."""
        self.mock_repo.list_active = AsyncMock(return_value=[])
        await self.scanner.scan("tenant-1")

        # Manually expire the cache
        if "tenant-1" in self.scanner._scan_cache:
            result, _ = self.scanner._scan_cache["tenant-1"]
            self.scanner._scan_cache["tenant-1"] = (result, time.time() - SCAN_CACHE_TTL - 1)

        assert self.scanner.get_cached_result("tenant-1") is None

    @pytest.mark.asyncio
    async def test_different_tenants_independent_cache(self):
        """Cache is per-tenant."""
        self.mock_repo.list_active = AsyncMock(return_value=[])
        await self.scanner.scan("tenant-1")
        await self.scanner.scan("tenant-2")
        assert self.scanner.get_cached_result("tenant-1") is not None
        assert self.scanner.get_cached_result("tenant-2") is not None


# ---------------------------------------------------------------------------
# Test: Scanner configuration
# ---------------------------------------------------------------------------


class TestScannerConfiguration:
    """Test scanner configuration lifecycle."""

    def test_unconfigured_raises(self):
        scanner = KBConflictScanner()
        with pytest.raises(RuntimeError, match="not configured"):
            scanner._ensure_configured()

    @pytest.mark.asyncio
    async def test_scan_unconfigured_raises(self):
        scanner = KBConflictScanner()
        with pytest.raises(RuntimeError, match="not configured"):
            await scanner.scan("tenant-1")

    def test_configure_sets_flag(self):
        scanner = KBConflictScanner()
        scanner.configure(kb_repo=AsyncMock())
        assert scanner._configured is True

    def test_health_unconfigured(self):
        scanner = KBConflictScanner()
        health = scanner.health()
        assert health["configured"] is False
        assert health["cached_tenants"] == 0

    def test_health_configured(self):
        scanner = KBConflictScanner()
        scanner.configure(kb_repo=AsyncMock())
        health = scanner.health()
        assert health["configured"] is True

    @pytest.mark.asyncio
    async def test_health_with_cached_scan(self):
        scanner = KBConflictScanner()
        mock_repo = AsyncMock()
        mock_repo.list_active = AsyncMock(return_value=[])
        scanner.configure(kb_repo=mock_repo)
        await scanner.scan("tenant-1")
        health = scanner.health()
        assert health["cached_tenants"] == 1


# ---------------------------------------------------------------------------
# Test: Module-level singleton
# ---------------------------------------------------------------------------


class TestSingleton:
    """Test get_conflict_scanner singleton."""

    def test_returns_same_instance(self):
        s1 = get_conflict_scanner()
        s2 = get_conflict_scanner()
        assert s1 is s2

    def test_is_scanner_instance(self):
        scanner = get_conflict_scanner()
        assert isinstance(scanner, KBConflictScanner)


# ---------------------------------------------------------------------------
# Test: Pair deduplication across phases
# ---------------------------------------------------------------------------


class TestPairDeduplication:
    """Ensure the same pair is not reported twice across Phase 1 and Phase 2."""

    def setup_method(self):
        self.scanner = KBConflictScanner()
        self.mock_repo = AsyncMock()
        self.scanner.configure(kb_repo=self.mock_repo)

    @pytest.mark.asyncio
    async def test_pair_reported_once(self):
        """A pair caught by Phase 1 is not also caught by Phase 2."""
        base_emb = _make_embedding(5.0, dim=16)
        entries = [
            _make_entry("e1", "Return Policy", "Returns within 30 days.",
                        embedding=base_emb),
            _make_entry("e2", "Returns Policy", "Returns within 30 days.",
                        embedding=_make_similar_embedding(base_emb, 0.001)),
        ]
        self.mock_repo.list_active = AsyncMock(return_value=entries)

        with patch("src.multi_tenant.semantic_cache.cosine_similarity", return_value=0.95):
            result = await self.scanner.scan("tenant-1", force=True)

        # Both phases could match this pair, but it should appear only once
        pair_ids = [(c.entry_a_id, c.entry_b_id) for c in result.conflicts]
        unique_pairs = set(tuple(sorted(p)) for p in pair_ids)
        assert len(unique_pairs) == len(result.conflicts)


# ---------------------------------------------------------------------------
# Test: MAX_CONFLICTS_REPORTED trim
# ---------------------------------------------------------------------------


class TestMaxConflictsLimit:
    """Verify that results are trimmed when exceeding MAX_CONFLICTS_REPORTED."""

    def setup_method(self):
        self.scanner = KBConflictScanner()
        self.mock_repo = AsyncMock()
        self.scanner.configure(kb_repo=self.mock_repo)

    @pytest.mark.asyncio
    async def test_trim_at_max(self):
        """Scan trims results to MAX_CONFLICTS_REPORTED."""
        # Create enough entries to generate >100 pairs
        # With 15 entries of the same type, we get 15*14/2 = 105 pairs
        entries = []
        base_emb = _make_embedding(6.0, dim=16)
        for i in range(15):
            entries.append(
                _make_entry(
                    f"e{i}",
                    f"Policy {i}",
                    f"Content about returns and policy number {i}.",
                    embedding=_make_similar_embedding(base_emb, noise=0.001 * (i + 1)),
                )
            )
        self.mock_repo.list_active = AsyncMock(return_value=entries)

        with patch("src.multi_tenant.semantic_cache.cosine_similarity", return_value=0.90):
            result = await self.scanner.scan("tenant-1", force=True)

        assert len(result.conflicts) <= MAX_CONFLICTS_REPORTED
