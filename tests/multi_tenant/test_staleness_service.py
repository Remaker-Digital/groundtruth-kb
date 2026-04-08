"""Tests for Knowledge Base staleness detection service (WI #219-222).

Validates:
    - Staleness score computation (3-factor model)
    - Classification categories (fresh/aging/stale/very_stale)
    - StalenessService: score_entry, score_all, list_stale
    - Verification workflow (verify_entry)
    - Auto re-embedding (refresh_stale, refresh_changed)
    - Summary statistics
    - API endpoints (/staleness, /stale, /{entry_id}/verify)
    - Singleton pattern

Test IDs follow the pattern ST-XX for traceability.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.staleness_service import (
    AGING_THRESHOLD,
    AUTO_REEMBED_THRESHOLD,
    DEFAULT_FRESHNESS_DAYS,
    DEFAULT_FRESHNESS_WINDOWS,
    FRESH_THRESHOLD,
    MAX_REEMBED_BATCH,
    STALE_THRESHOLD,
    StalenessService,
    classify_staleness,
    compute_staleness_score,
    get_staleness_service,
)

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

TENANT_ID = "tenant-staleness-test-0001"
NOW = datetime(2026, 2, 5, 12, 0, 0, tzinfo=timezone.utc)


def _content_hash(title: str, content: str) -> str:
    """Compute content hash matching knowledge_vectorizer.compute_content_hash."""
    text = f"{title}\n---\n{content}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _make_entry(
    entry_id: str = "kb-001",
    entry_type: str = "faq",
    title: str = "Test Article",
    content: str = "Test content body",
    updated_at: str | None = None,
    created_at: str | None = None,
    last_verified_at: str | None = None,
    embedded_at: str | None = None,
    embedding: list[float] | None = None,
    content_hash: str | None = None,
    staleness_score: float | None = None,
    is_active: bool = True,
) -> dict[str, Any]:
    """Create a mock KB entry dict."""
    if updated_at is None:
        updated_at = NOW.isoformat()
    if created_at is None:
        created_at = updated_at

    entry: dict[str, Any] = {
        "id": entry_id,
        "tenant_id": TENANT_ID,
        "entry_type": entry_type,
        "title": title,
        "content": content,
        "status": "published",
        "is_active": is_active,
        "updated_at": updated_at,
        "created_at": created_at,
    }
    if last_verified_at is not None:
        entry["last_verified_at"] = last_verified_at
    if embedded_at is not None:
        entry["embedded_at"] = embedded_at
    if embedding is not None:
        entry["embedding"] = embedding
    if content_hash is not None:
        entry["content_hash"] = content_hash
    if staleness_score is not None:
        entry["staleness_score"] = staleness_score
    return entry


def _make_mock_repo() -> AsyncMock:
    """Create a mock KnowledgeBaseRepository."""
    repo = AsyncMock()
    repo.read = AsyncMock()
    repo.patch = AsyncMock()
    repo.list_filtered = AsyncMock(return_value=[])
    return repo


def _make_mock_vectorizer() -> MagicMock:
    """Create a mock KnowledgeVectorizer."""
    vec = MagicMock()
    vec.needs_reembedding = MagicMock(return_value=False)
    vec.embed_batch = AsyncMock(return_value=0)
    vec.embed_unembedded = AsyncMock(return_value=0)
    return vec


# ---------------------------------------------------------------------------
# ST-01 to ST-06: compute_staleness_score tests
# ---------------------------------------------------------------------------


class TestComputeStalenessScore:
    """Tests for the staleness score computation function."""

    def test_st01_fresh_entry(self):
        """ST-01: Recently updated entry with embedding and verification is fresh."""
        entry = _make_entry(
            updated_at=NOW.isoformat(),
            last_verified_at=NOW.isoformat(),
            embedding=[0.1] * 10,
            content_hash=_content_hash("Test Article", "Test content body"),
        )
        score = compute_staleness_score(entry, now=NOW)
        assert score < FRESH_THRESHOLD
        assert score >= 0.0

    def test_st02_aged_entry(self):
        """ST-02: Entry updated 40 days ago (within FAQ 60-day window) is aging."""
        old_date = (NOW - timedelta(days=40)).isoformat()
        entry = _make_entry(
            entry_type="faq",
            updated_at=old_date,
            last_verified_at=old_date,
            embedding=[0.1] * 10,
            content_hash=_content_hash("Test Article", "Test content body"),
        )
        score = compute_staleness_score(entry, now=NOW)
        assert FRESH_THRESHOLD <= score < STALE_THRESHOLD

    def test_st03_stale_entry(self):
        """ST-03: Product entry updated 30+ days ago becomes stale faster."""
        old_date = (NOW - timedelta(days=35)).isoformat()
        entry = _make_entry(
            entry_type="product",
            updated_at=old_date,
            embedding=[0.1] * 10,
            content_hash=_content_hash("Test Article", "Test content body"),
        )
        score = compute_staleness_score(entry, now=NOW)
        assert score >= AGING_THRESHOLD

    def test_st04_no_embedding_adds_drift(self):
        """ST-04: Entry without embedding gets maximum drift score (0.3)."""
        entry = _make_entry(
            updated_at=NOW.isoformat(),
            last_verified_at=NOW.isoformat(),
        )
        score = compute_staleness_score(entry, now=NOW)
        # Age factor ~0 + drift 0.3 + verification ~0 = ~0.3
        assert score >= 0.28

    def test_st05_content_hash_mismatch_adds_drift(self):
        """ST-05: Content changed since embedding triggers drift."""
        entry = _make_entry(
            updated_at=NOW.isoformat(),
            last_verified_at=NOW.isoformat(),
            embedding=[0.1] * 10,
            content_hash="old-hash-that-does-not-match",
        )
        score = compute_staleness_score(entry, now=NOW)
        # Drift = 0.3 because hash mismatch
        assert score >= 0.28

    def test_st06_no_verification_adds_score(self):
        """ST-06: Entry never verified gets full verification factor (0.2)."""
        entry = _make_entry(
            updated_at=NOW.isoformat(),
            embedding=[0.1] * 10,
            content_hash=_content_hash("Test Article", "Test content body"),
        )
        # No last_verified_at
        score = compute_staleness_score(entry, now=NOW)
        # Age ~0 + drift 0 + verification 0.2
        assert 0.18 <= score <= 0.22

    def test_st07_custom_freshness_window(self):
        """ST-07: Custom freshness windows override defaults."""
        old_date = (NOW - timedelta(days=10)).isoformat()
        entry = _make_entry(
            entry_type="custom",
            updated_at=old_date,
            last_verified_at=old_date,
            embedding=[0.1] * 10,
            content_hash=_content_hash("Test Article", "Test content body"),
        )
        # With a 10-day window, 10 days old = fully aged
        custom_windows = {"custom": 10}
        score = compute_staleness_score(entry, now=NOW, freshness_windows=custom_windows)
        assert score >= 0.5  # Age factor maxed out

    def test_st08_score_capped_at_one(self):
        """ST-08: Score never exceeds 1.0 even with all factors maxed."""
        very_old = (NOW - timedelta(days=365)).isoformat()
        entry = _make_entry(
            entry_type="product",
            updated_at=very_old,
            # No embedding, no verification — all factors maxed
        )
        score = compute_staleness_score(entry, now=NOW)
        assert score <= 1.0

    def test_st09_missing_dates_uses_now(self):
        """ST-09: Entry with no dates uses current time as reference."""
        entry = {
            "id": "kb-no-dates",
            "tenant_id": TENANT_ID,
            "title": "No dates",
            "content": "No dates content",
            "entry_type": "faq",
        }
        score = compute_staleness_score(entry, now=NOW)
        # Age factor = 0 (reference = now), drift = 0.3 (no embedding), verification = 0.2
        assert 0.4 <= score <= 0.55


# ---------------------------------------------------------------------------
# ST-10 to ST-13: classify_staleness tests
# ---------------------------------------------------------------------------


class TestClassifyStaleness:
    """Tests for the staleness classification function."""

    def test_st10_fresh_classification(self):
        assert classify_staleness(0.0) == "fresh"
        assert classify_staleness(0.15) == "fresh"
        assert classify_staleness(0.29) == "fresh"

    def test_st11_aging_classification(self):
        assert classify_staleness(0.3) == "aging"
        assert classify_staleness(0.45) == "aging"
        assert classify_staleness(0.59) == "aging"

    def test_st12_stale_classification(self):
        assert classify_staleness(0.6) == "stale"
        assert classify_staleness(0.7) == "stale"
        assert classify_staleness(0.79) == "stale"

    def test_st13_very_stale_classification(self):
        assert classify_staleness(0.8) == "very_stale"
        assert classify_staleness(0.9) == "very_stale"
        assert classify_staleness(1.0) == "very_stale"


# ---------------------------------------------------------------------------
# ST-14 to ST-20: StalenessService tests
# ---------------------------------------------------------------------------


class TestStalenessService:
    """Tests for the StalenessService class."""

    def _make_service(self, repo=None, vectorizer=None):
        svc = StalenessService()
        svc.configure(
            kb_repo=repo or _make_mock_repo(),
            vectorizer=vectorizer,
        )
        return svc

    @pytest.mark.asyncio
    async def test_st14_not_configured_raises(self):
        """ST-14: Service raises RuntimeError if used before configure()."""
        svc = StalenessService()
        with pytest.raises(RuntimeError, match="not configured"):
            await svc.score_entry(TENANT_ID, "kb-001")

    @pytest.mark.asyncio
    async def test_st15_score_entry(self):
        """ST-15: score_entry computes and persists score."""
        repo = _make_mock_repo()
        entry = _make_entry(
            embedding=[0.1] * 10,
            content_hash=_content_hash("Test Article", "Test content body"),
            last_verified_at=NOW.isoformat(),
        )
        repo.read.return_value = entry

        svc = self._make_service(repo=repo)
        result = await svc.score_entry(TENANT_ID, "kb-001")

        assert "staleness_score" in result
        assert "staleness_category" in result
        assert result["id"] == "kb-001"
        # Should have called patch to persist score
        repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_st16_score_entry_no_persist(self):
        """ST-16: score_entry with update=False skips persistence."""
        repo = _make_mock_repo()
        entry = _make_entry()
        repo.read.return_value = entry

        svc = self._make_service(repo=repo)
        result = await svc.score_entry(TENANT_ID, "kb-001", update=False)

        assert "staleness_score" in result
        repo.patch.assert_not_called()

    @pytest.mark.asyncio
    async def test_st17_score_all(self):
        """ST-17: score_all returns sorted scores for all entries."""
        repo = _make_mock_repo()
        entries = [
            _make_entry(entry_id="kb-fresh", updated_at=NOW.isoformat(),
                       embedding=[0.1], content_hash=_content_hash("Test Article", "Test content body"),
                       last_verified_at=NOW.isoformat()),
            _make_entry(entry_id="kb-old", updated_at=(NOW - timedelta(days=100)).isoformat(),
                       entry_type="product"),
        ]
        repo.list_filtered.return_value = entries

        svc = self._make_service(repo=repo)
        results = await svc.score_all(TENANT_ID)

        assert len(results) == 2
        # Should be sorted descending by score (stale first)
        assert results[0]["staleness_score"] >= results[1]["staleness_score"]

    @pytest.mark.asyncio
    async def test_st18_list_stale(self):
        """ST-18: list_stale returns only entries above threshold."""
        repo = _make_mock_repo()
        entries = [
            _make_entry(entry_id="kb-fresh", updated_at=NOW.isoformat(),
                       embedding=[0.1], content_hash=_content_hash("Test Article", "Test content body"),
                       last_verified_at=NOW.isoformat()),
            _make_entry(entry_id="kb-very-old", updated_at=(NOW - timedelta(days=200)).isoformat(),
                       entry_type="product"),
        ]
        repo.list_filtered.return_value = entries

        svc = self._make_service(repo=repo)
        stale = await svc.list_stale(TENANT_ID, threshold=0.5)

        # Only the very old entry should be above 0.5
        assert len(stale) >= 1
        assert all(e["staleness_score"] >= 0.5 for e in stale)

    @pytest.mark.asyncio
    async def test_st19_verify_entry(self):
        """ST-19: verify_entry updates last_verified_at and recomputes score."""
        repo = _make_mock_repo()
        # First read for setting last_verified_at
        # Second read after patching for recomputation
        entry_after = _make_entry(
            last_verified_at=NOW.isoformat(),
            embedding=[0.1] * 10,
            content_hash=_content_hash("Test Article", "Test content body"),
        )
        repo.read.return_value = entry_after

        svc = self._make_service(repo=repo)
        result = await svc.verify_entry(TENANT_ID, "kb-001")

        assert result["id"] == "kb-001"
        assert result["last_verified_at"] is not None
        assert result["staleness_category"] in ("fresh", "aging", "stale", "very_stale")
        # Should have called patch twice (once for last_verified_at, once for score)
        assert repo.patch.call_count == 2

    @pytest.mark.asyncio
    async def test_st20_get_summary(self):
        """ST-20: get_summary returns correct category counts."""
        repo = _make_mock_repo()
        entries = [
            # Fresh entry
            _make_entry(entry_id="kb-1", updated_at=NOW.isoformat(),
                       embedding=[0.1], content_hash=_content_hash("Test Article", "Test content body"),
                       last_verified_at=NOW.isoformat()),
            # Very stale entry
            _make_entry(entry_id="kb-2", updated_at=(NOW - timedelta(days=200)).isoformat(),
                       entry_type="product"),
        ]
        repo.list_filtered.return_value = entries

        svc = self._make_service(repo=repo)
        summary = await svc.get_summary(TENANT_ID)

        assert summary["total_entries"] == 2
        assert summary["fresh_count"] + summary["aging_count"] + summary["stale_count"] + summary["very_stale_count"] == 2
        assert summary["needs_attention"] == summary["stale_count"] + summary["very_stale_count"]
        assert 0.0 <= summary["avg_staleness_score"] <= 1.0


# ---------------------------------------------------------------------------
# ST-21 to ST-25: Re-embedding tests
# ---------------------------------------------------------------------------


class TestRefreshOperations:
    """Tests for auto re-embedding functionality."""

    def _make_service(self, repo=None, vectorizer=None):
        svc = StalenessService()
        svc.configure(
            kb_repo=repo or _make_mock_repo(),
            vectorizer=vectorizer or _make_mock_vectorizer(),
        )
        return svc

    @pytest.mark.asyncio
    async def test_st21_refresh_stale_no_vectorizer(self):
        """ST-21: refresh_stale returns 0 when no vectorizer configured."""
        svc = StalenessService()
        svc.configure(kb_repo=_make_mock_repo(), vectorizer=None)
        count = await svc.refresh_stale(TENANT_ID)
        assert count == 0

    @pytest.mark.asyncio
    async def test_st22_refresh_stale_re_embeds_changed(self):
        """ST-22: refresh_stale re-embeds entries with content changes above threshold."""
        repo = _make_mock_repo()
        vec = _make_mock_vectorizer()

        stale_entry = _make_entry(
            entry_id="kb-stale",
            updated_at=(NOW - timedelta(days=200)).isoformat(),
            entry_type="product",
        )
        repo.list_filtered.return_value = [stale_entry]
        vec.needs_reembedding.return_value = True
        vec.embed_batch.return_value = 1

        svc = self._make_service(repo=repo, vectorizer=vec)
        count = await svc.refresh_stale(TENANT_ID)

        assert count == 1
        vec.embed_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_st23_refresh_stale_skips_fresh(self):
        """ST-23: refresh_stale skips entries below threshold."""
        repo = _make_mock_repo()
        vec = _make_mock_vectorizer()

        fresh_entry = _make_entry(
            updated_at=NOW.isoformat(),
            embedding=[0.1],
            content_hash=_content_hash("Test Article", "Test content body"),
            last_verified_at=NOW.isoformat(),
        )
        repo.list_filtered.return_value = [fresh_entry]

        svc = self._make_service(repo=repo, vectorizer=vec)
        count = await svc.refresh_stale(TENANT_ID)

        assert count == 0
        vec.embed_batch.assert_not_called()

    @pytest.mark.asyncio
    async def test_st24_refresh_changed(self):
        """ST-24: refresh_changed re-embeds entries with content hash mismatch."""
        repo = _make_mock_repo()
        vec = _make_mock_vectorizer()

        changed_entry = _make_entry(
            embedding=[0.1] * 10,
            content_hash="old-hash-no-match",
        )
        repo.list_filtered.return_value = [changed_entry]
        vec.needs_reembedding.return_value = True
        vec.embed_unembedded.return_value = 0
        vec.embed_batch.return_value = 1

        svc = self._make_service(repo=repo, vectorizer=vec)
        count = await svc.refresh_changed(TENANT_ID)

        assert count == 1

    @pytest.mark.asyncio
    async def test_st25_refresh_changed_no_vectorizer(self):
        """ST-25: refresh_changed returns 0 when no vectorizer."""
        svc = StalenessService()
        svc.configure(kb_repo=_make_mock_repo(), vectorizer=None)
        count = await svc.refresh_changed(TENANT_ID)
        assert count == 0

    @pytest.mark.asyncio
    async def test_st26_refresh_stale_batch_limit(self):
        """ST-26: refresh_stale respects max_entries limit."""
        repo = _make_mock_repo()
        vec = _make_mock_vectorizer()

        # Create many stale entries
        entries = [
            _make_entry(
                entry_id=f"kb-{i}",
                updated_at=(NOW - timedelta(days=200)).isoformat(),
                entry_type="product",
            )
            for i in range(10)
        ]
        repo.list_filtered.return_value = entries
        vec.needs_reembedding.return_value = True
        vec.embed_batch.return_value = 3

        svc = self._make_service(repo=repo, vectorizer=vec)
        await svc.refresh_stale(TENANT_ID, max_entries=3)

        # embed_batch should have been called with at most 3 entries
        call_args = vec.embed_batch.call_args
        assert len(call_args[0][1]) <= 3


# ---------------------------------------------------------------------------
# ST-27 to ST-28: Singleton and constants tests
# ---------------------------------------------------------------------------


class TestSingletonAndConstants:
    """Tests for module-level patterns and constants."""

    def test_st27_singleton(self):
        """ST-27: get_staleness_service returns same instance."""
        svc1 = get_staleness_service()
        svc2 = get_staleness_service()
        assert svc1 is svc2

    def test_st28_constants(self):
        """ST-28: Module constants have expected values."""
        assert 0.0 < FRESH_THRESHOLD < AGING_THRESHOLD < STALE_THRESHOLD <= 1.0
        assert DEFAULT_FRESHNESS_DAYS > 0
        assert AUTO_REEMBED_THRESHOLD > 0
        assert MAX_REEMBED_BATCH > 0
        assert "product" in DEFAULT_FRESHNESS_WINDOWS
        assert "faq" in DEFAULT_FRESHNESS_WINDOWS
        assert "policy" in DEFAULT_FRESHNESS_WINDOWS

    def test_st29_freshness_windows_ordering(self):
        """ST-29: Products stale faster than policies (shorter window)."""
        assert DEFAULT_FRESHNESS_WINDOWS["product"] < DEFAULT_FRESHNESS_WINDOWS["policy"]
        assert DEFAULT_FRESHNESS_WINDOWS["product"] < DEFAULT_FRESHNESS_WINDOWS["faq"]


# ---------------------------------------------------------------------------
# ST-30 to ST-35: API endpoint tests
# ---------------------------------------------------------------------------


class TestStalenessAPIEndpoints:
    """Tests for staleness-related admin API endpoints."""

    @pytest.fixture
    def mock_staleness_service(self):
        """Mock staleness service for API tests."""
        from unittest.mock import AsyncMock
        svc = AsyncMock()
        svc.get_summary = AsyncMock(return_value={
            "total_entries": 10,
            "avg_staleness_score": 0.35,
            "fresh_count": 5,
            "aging_count": 3,
            "stale_count": 1,
            "very_stale_count": 1,
            "needs_attention": 2,
        })
        svc.list_stale = AsyncMock(return_value=[
            {
                "id": "kb-stale-1",
                "staleness_score": 0.85,
                "staleness_category": "very_stale",
                "last_verified_at": None,
                "embedded_at": None,
            }
        ])
        svc.verify_entry = AsyncMock(return_value={
            "id": "kb-001",
            "staleness_score": 0.1,
            "staleness_category": "fresh",
            "last_verified_at": NOW.isoformat(),
            "embedded_at": None,
        })
        return svc

    def test_st30_staleness_summary_model(self):
        """ST-30: StalenessSummary response model has all required fields."""
        from src.multi_tenant.admin_knowledge_api import StalenessSummaryResponse

        data = StalenessSummaryResponse(
            total_entries=10,
            avg_staleness_score=0.35,
            fresh_count=5,
            aging_count=3,
            stale_count=1,
            very_stale_count=1,
            needs_attention=2,
        )
        assert data.total_entries == 10
        assert data.needs_attention == 2

    def test_st31_staleness_score_model(self):
        """ST-31: StalenessScoreResponse model has all required fields."""
        from src.multi_tenant.admin_knowledge_api import StalenessScoreResponse

        data = StalenessScoreResponse(
            id="kb-001",
            staleness_score=0.45,
            staleness_category="aging",
            last_verified_at=None,
            embedded_at=None,
        )
        assert data.staleness_category == "aging"

    def test_st32_entry_response_includes_staleness(self):
        """ST-32: KnowledgeEntryResponse includes staleness fields."""
        from src.multi_tenant.admin_knowledge_api import KnowledgeEntryResponse

        data = KnowledgeEntryResponse(
            id="kb-001",
            tenant_id=TENANT_ID,
            entry_type="faq",
            title="Test",
            content="Body",
            created_at=NOW.isoformat(),
            updated_at=NOW.isoformat(),
            staleness_score=0.55,
            staleness_category="aging",
            last_verified_at=NOW.isoformat(),
            embedded_at=NOW.isoformat(),
        )
        assert data.staleness_score == 0.55
        assert data.staleness_category == "aging"

    def test_st33_entry_response_staleness_defaults_none(self):
        """ST-33: Staleness fields default to None when not provided."""
        from src.multi_tenant.admin_knowledge_api import KnowledgeEntryResponse

        data = KnowledgeEntryResponse(
            id="kb-001",
            tenant_id=TENANT_ID,
            entry_type="faq",
            title="Test",
            content="Body",
            created_at=NOW.isoformat(),
            updated_at=NOW.isoformat(),
        )
        assert data.staleness_score is None
        assert data.staleness_category is None
        assert data.last_verified_at is None
        assert data.embedded_at is None

    def test_st34_classify_boundary_values(self):
        """ST-34: Classification at exact boundary values."""
        assert classify_staleness(FRESH_THRESHOLD - 0.001) == "fresh"
        assert classify_staleness(FRESH_THRESHOLD) == "aging"
        assert classify_staleness(AGING_THRESHOLD - 0.001) == "aging"
        assert classify_staleness(AGING_THRESHOLD) == "stale"
        assert classify_staleness(STALE_THRESHOLD - 0.001) == "stale"
        assert classify_staleness(STALE_THRESHOLD) == "very_stale"

    def test_st35_entry_type_freshness_windows(self):
        """ST-35: Each entry type has a different freshness window."""
        windows = DEFAULT_FRESHNESS_WINDOWS
        # Verify ordering: product < custom < faq < policy
        assert windows["product"] < windows["custom"]
        assert windows["custom"] < windows["faq"]
        assert windows["faq"] < windows["policy"]
