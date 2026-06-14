"""WI-4519: always-on SQLite-LIKE merge in ``search_deliberations``.

These tests prove that ``KnowledgeDB.search_deliberations`` runs the SQLite
LIKE pass on EVERY call (not only as a fallback) and merges it with the
ChromaDB semantic results, deduped by deliberation ``id``. This closes the
S437 freshness gap: a recently-inserted deliberation whose ChromaDB index step
was deferred (e.g. by the already-VERIFIED WI-4453 embedding-timeout guard)
must still be surfaced by the very next search, protecting the mandatory
pre-proposal/pre-review Deliberation Archive search contract
(``.claude/rules/deliberation-protocol.md``).

The tests are hermetic: they monkeypatch ``_get_chroma_collection`` with a
configurable stub and never load a real embedding model, so they run
regardless of whether ChromaDB is installed.

Acceptance specs: GOV-STANDING-BACKLOG-001 (WI-4519 backlog authority),
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (spec-derived coverage),
GOV-FILE-BRIDGE-AUTHORITY-001, and the deliberation-protocol read-surface
contract this fix restores.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import time
from typing import Any

import groundtruth_kb.db as db_mod


class _StubCollection:
    """Configurable ChromaDB-collection stand-in for the search path.

    ``matches`` is a list of ``(delib_id, distance, chunk_text)`` tuples that
    the stub reports as semantic hits. ``count()`` reflects whether any matches
    are configured so ``_chroma_query_matches`` proceeds to ``query()``.
    """

    def __init__(self, matches: list[tuple[str, float, str]] | None = None) -> None:
        self.matches = matches or []

    def add(self, **_kwargs: Any) -> None:
        # Never reached in these tests (insert patches collection to None), but
        # present so the stub is a faithful collection stand-in.
        return None

    def count(self) -> int:
        return len(self.matches)

    def query(self, *, query_texts: list[str], n_results: int) -> dict[str, Any]:  # noqa: ARG002
        ids = [[f"{delib_id}::0" for delib_id, _dist, _txt in self.matches]]
        distances = [[dist for _delib_id, dist, _txt in self.matches]]
        documents = [[txt for _delib_id, _dist, txt in self.matches]]
        metadatas = [[{"delib_id": delib_id} for delib_id, _dist, _txt in self.matches]]
        return {"ids": ids, "distances": distances, "documents": documents, "metadatas": metadatas}


def _insert(db: db_mod.KnowledgeDB, monkeypatch, delib_id: str, content: str) -> None:
    """Commit a canonical SQLite deliberation row without touching real Chroma.

    During insert ``_get_chroma_collection`` is forced to ``None`` so the
    on-insert index step is a fast no-op and never loads an embedding model.
    """
    monkeypatch.setattr(db, "_get_chroma_collection", lambda: None)
    db.insert_deliberation(
        id=delib_id,
        source_type="report",
        title=f"{delib_id} fixture",
        summary="Fixture deliberation for WI-4519 always-on LIKE merge tests.",
        content=content,
        changed_by="test",
        change_reason="WI-4519 always-on LIKE merge test fixture",
    )


class TestAlwaysOnLikeMerge:
    """Acceptance criteria for WI-4519 (always-on SQLite-LIKE merge)."""

    def test_unindexed_delib_surfaces_via_like(self, db, monkeypatch):
        """Fresh-but-unindexed DELIB is found via LIKE alongside semantic hits.

        S437 repro: DELIB-FRESH was persisted to SQLite but its index step was
        deferred, so the semantic pass only returns DELIB-INDEXED. The always-on
        LIKE pass must still surface DELIB-FRESH.

        Acceptance: WI-4519 core defect; deliberation-protocol read surface.
        """
        _insert(db, monkeypatch, "DELIB-INDEXED", "Shared keyword apexmerge in indexed row.")
        _insert(db, monkeypatch, "DELIB-FRESH", "Shared keyword apexmerge in fresh unindexed row.")

        # Semantic pass only knows about the indexed row (the fresh one's index
        # step was deferred); LIKE must recover the fresh row.
        stub = _StubCollection(matches=[("DELIB-INDEXED", 0.10, "indexed chunk")])
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: stub)

        results = db.search_deliberations("apexmerge", limit=5)
        ids = [r["id"] for r in results]

        assert "DELIB-FRESH" in ids  # the core WI-4519 guarantee
        assert "DELIB-INDEXED" in ids
        fresh = next(r for r in results if r["id"] == "DELIB-FRESH")
        assert fresh["search_method"] == "text_match"  # recovered via LIKE

    def test_semantic_results_preserved(self, db, monkeypatch):
        """Existing semantic results are preserved (no FAB-17 regression).

        Acceptance: semantic path unchanged; row carries search_method=semantic.
        """
        _insert(db, monkeypatch, "DELIB-SEM", "Semantic keyword betamerge content here.")

        stub = _StubCollection(matches=[("DELIB-SEM", 0.20, "semantic chunk preview")])
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: stub)

        results = db.search_deliberations("betamerge", limit=5)

        sem = next(r for r in results if r["id"] == "DELIB-SEM")
        assert sem["search_method"] == "semantic"
        assert sem["score"] == 0.20
        assert sem["matched_chunk_id"] == "DELIB-SEM::0"
        assert results[0]["id"] == "DELIB-SEM"  # semantic head

    def test_dedupe_prefers_semantic_for_overlap(self, db, monkeypatch):
        """A DELIB matched by BOTH paths appears once; semantic ordering wins.

        Acceptance: dedupe by id; semantic representation preferred on overlap.
        """
        _insert(db, monkeypatch, "DELIB-BOTH", "Overlap keyword gammamerge in row body.")

        # Semantic returns DELIB-BOTH; LIKE also matches it on the same keyword.
        stub = _StubCollection(matches=[("DELIB-BOTH", 0.15, "overlap chunk")])
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: stub)

        results = db.search_deliberations("gammamerge", limit=5)

        both = [r for r in results if r["id"] == "DELIB-BOTH"]
        assert len(both) == 1  # appears exactly once (deduped)
        assert both[0]["search_method"] == "semantic"  # semantic representation wins

    def test_result_order_semantic_first_then_like(self, db, monkeypatch):
        """Order: semantic head (by distance), then LIKE-only tail (rowid DESC).

        Acceptance: deliberation-protocol ordering gate + cap to limit.
        """
        # Insertion order fixes rowid ascending: S1 < S2 < L1 < L2.
        _insert(db, monkeypatch, "DELIB-S1", "Order keyword deltamerge s1.")
        _insert(db, monkeypatch, "DELIB-S2", "Order keyword deltamerge s2.")
        _insert(db, monkeypatch, "DELIB-L1", "Order keyword deltamerge l1.")
        _insert(db, monkeypatch, "DELIB-L2", "Order keyword deltamerge l2.")

        # Semantic returns S1 (closer) then S2; LIKE returns all 4 by rowid DESC.
        stub = _StubCollection(matches=[("DELIB-S1", 0.10, "s1 chunk"), ("DELIB-S2", 0.20, "s2 chunk")])
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: stub)

        results = db.search_deliberations("deltamerge", limit=5)
        ids = [r["id"] for r in results]

        # Semantic head in relevance order, then LIKE-only rows newest-first.
        assert ids == ["DELIB-S1", "DELIB-S2", "DELIB-L2", "DELIB-L1"]
        assert results[0]["search_method"] == "semantic"
        assert results[1]["search_method"] == "semantic"
        assert results[2]["search_method"] == "text_match"
        assert results[3]["search_method"] == "text_match"

        # Cap to limit: a tighter limit truncates the merged list deterministically.
        capped = db.search_deliberations("deltamerge", limit=2)
        assert [r["id"] for r in capped] == ["DELIB-S1", "DELIB-S2"]

    def test_like_only_when_no_semantic(self, db, monkeypatch):
        """LIKE-only path still works when ChromaDB is unavailable.

        Acceptance: FAB-17 fallback preserved (no semantic -> text_match rows).
        """
        _insert(db, monkeypatch, "DELIB-LIKEONLY", "Fallback keyword epsilonmerge body.")

        # No collection at all -> semantic set empty; LIKE must carry the result.
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: None)

        results = db.search_deliberations("epsilonmerge", limit=5)

        assert len(results) == 1
        assert results[0]["id"] == "DELIB-LIKEONLY"
        assert results[0]["search_method"] == "text_match"
        assert results[0]["score"] is None

    def test_like_pass_does_not_hang(self, db, monkeypatch):
        """The always-on LIKE merge adds no latency/hang path (smoke).

        Acceptance: LIKE is in-process SQLite; a normal search returns promptly.
        """
        _insert(db, monkeypatch, "DELIB-FAST", "Smoke keyword zetamerge content.")

        stub = _StubCollection(matches=[("DELIB-FAST", 0.10, "fast chunk")])
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: stub)

        start = time.monotonic()
        results = db.search_deliberations("zetamerge", limit=5)
        elapsed = time.monotonic() - start

        assert elapsed < 1.0  # no new hang/latency path introduced by the merge
        assert any(r["id"] == "DELIB-FAST" for r in results)
