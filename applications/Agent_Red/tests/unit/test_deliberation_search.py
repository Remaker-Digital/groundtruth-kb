"""
Known-answer validation for deliberation semantic search.

SPEC-2098 Phase C2: 10 curated queries with expected deliberation matches.
Asserts >= 80% top-3 success rate.

Requires:
  - groundtruth.db with backfilled deliberations (at repo root)
  - .groundtruth-chroma/ with rebuilt index (at repo root)
  - groundtruth-kb[search] installed (chromadb available)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
KB_PATH = REPO_ROOT / "groundtruth.db"
CHROMA_PATH = REPO_ROOT / ".groundtruth-chroma"

# Skip entire module if preconditions not met
pytestmark = pytest.mark.skipif(
    not KB_PATH.exists() or not CHROMA_PATH.exists(),
    reason="Requires groundtruth.db and .groundtruth-chroma index at repo root",
)


@pytest.fixture(scope="module")
def db():
    """Load the KnowledgeDB with search support."""
    sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))
    from db import KnowledgeDB

    return KnowledgeDB()


@pytest.fixture(scope="module")
def has_chromadb():
    """Check if ChromaDB is available."""
    try:
        import chromadb  # noqa: F401

        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Curated known-answer queries
# ---------------------------------------------------------------------------

# Each tuple: (query, list of expected SPEC/WI/keyword patterns in top-3 titles)
KNOWN_ANSWER_QUERIES = [
    (
        "phone OTP before escalation",
        ["SPEC-1879", "OTP", "phone"],
    ),
    (
        "credential scanner false positives",
        ["WI-3142", "credential", "scan"],
    ),
    (
        "Chromatic visual regression CI",
        ["WI-3165", "Chromatic", "visual"],
    ),
    (
        "production deploy approval gate",
        ["deploy", "production", "gate"],
    ),
    (
        "bridge protocol file-based migration",
        ["bridge", "protocol"],
    ),
    (
        "axe-core accessibility WCAG enforcement",
        ["axe", "accessibility", "WCAG"],
    ),
    (
        "tenant provisioning seed script",
        ["tenant", "provision", "seed"],
    ),
    (
        "Playwright screenshot baseline testing",
        ["Playwright", "screenshot", "baseline"],
    ),
    (
        "Cosmos database persistence layer",
        ["Cosmos", "persistence", "database"],
    ),
    (
        "SonarCloud code quality analysis",
        ["SonarCloud", "quality", "code"],
    ),
]


def _matches_pattern(title: str, patterns: list[str]) -> bool:
    """Check if any pattern appears in the title (case-insensitive)."""
    title_lower = title.lower()
    return any(p.lower() in title_lower for p in patterns)


class TestDeliberationSearch:
    """Known-answer retrieval validation for semantic search."""

    def test_chromadb_available(self, has_chromadb):
        """ChromaDB must be importable for semantic search."""
        assert has_chromadb, "chromadb not installed — run pip install groundtruth-kb[search]"

    def test_chroma_index_exists(self):
        """ChromaDB index directory must exist."""
        assert CHROMA_PATH.exists(), f"Missing ChromaDB index at {CHROMA_PATH}"
        chroma_db = CHROMA_PATH / "chroma.sqlite3"
        assert chroma_db.exists(), "ChromaDB sqlite3 file not found"

    def test_deliberation_count(self, db):
        """KB must have deliberations to search."""
        conn = sqlite3.connect(str(KB_PATH))
        count = conn.execute("SELECT COUNT(*) FROM current_deliberations").fetchone()[0]
        conn.close()
        assert count >= 649, f"Expected >= 649 deliberations, got {count}"

    @pytest.mark.parametrize(
        "query,patterns",
        KNOWN_ANSWER_QUERIES,
        ids=[q[0][:40] for q in KNOWN_ANSWER_QUERIES],
    )
    def test_known_answer_query(self, db, query, patterns):
        """Each curated query should return relevant results in top 3."""
        results = db.search_deliberations(query, limit=3)
        assert len(results) > 0, f"No results for '{query}'"

        titles = [r.get("title", "") for r in results]
        matched = any(_matches_pattern(t, patterns) for t in titles)
        # Collect evidence for assertion message
        title_list = "\n".join(f"  [{i+1}] {t}" for i, t in enumerate(titles))
        assert matched, (
            f"No top-3 result matched patterns {patterns} for '{query}'.\n"
            f"Got:\n{title_list}"
        )

    def test_overall_success_rate(self, db):
        """At least 80% of curated queries must match in top 3."""
        hits = 0
        for query, patterns in KNOWN_ANSWER_QUERIES:
            results = db.search_deliberations(query, limit=3)
            titles = [r.get("title", "") for r in results]
            if any(_matches_pattern(t, patterns) for t in titles):
                hits += 1

        rate = hits / len(KNOWN_ANSWER_QUERIES)
        assert rate >= 0.80, (
            f"Only {hits}/{len(KNOWN_ANSWER_QUERIES)} ({rate:.0%}) queries matched. "
            f"Required >= 80%."
        )

    def test_negative_query_limited(self, db):
        """An unrelated query should return few or no highly-scored results."""
        results = db.search_deliberations(
            "quantum entanglement photon interference pattern", limit=3
        )
        if results:
            scores = [r.get("score", 0) for r in results]
            # Semantic search may return low-relevance results;
            # just verify scores are below high-confidence threshold
            max_score = max(scores) if scores else 0
            assert max_score < 0.95, (
                f"Unrelated query got suspiciously high score: {max_score:.3f}"
            )

    def test_search_returns_semantic_method(self, db):
        """When ChromaDB is active, search should use semantic method."""
        results = db.search_deliberations("credential scanner", limit=1)
        if results:
            method = results[0].get("search_method", "unknown")
            assert method == "semantic", (
                f"Expected semantic search method, got '{method}'"
            )
