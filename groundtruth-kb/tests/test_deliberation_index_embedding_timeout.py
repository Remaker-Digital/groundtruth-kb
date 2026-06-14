"""WI-4453: bound the ChromaDB deliberation-index embedding step.

These tests prove that ``_index_deliberation_in_chroma`` (the record/propose
write path) cannot hang on the ChromaDB embedding step. They extend the
already-VERIFIED FAB-17 search-path timeout pattern to the index/add path:
``collection.add`` is wrapped in ``_call_with_timeout`` with a new,
env-overridable ``_CHROMA_INDEX_TIMEOUT_SECONDS``, and degrades to a deferred
(rebuildable) semantic index on timeout without losing the canonical SQLite
deliberation row.

The tests are hermetic: they monkeypatch ``_get_chroma_collection`` with a
stub collection and never load a real embedding model, so they run regardless
of whether ChromaDB is installed.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import importlib
import time
from typing import Any

import groundtruth_kb.db as db_mod


class _StubCollection:
    """Minimal ChromaDB-collection stand-in for index + search paths.

    ``add_delay`` / ``query_delay`` simulate the unbounded first-embed model
    load on the write (``add``) and read (``query`` / ``count``) paths.
    """

    def __init__(self, *, add_delay: float = 0.0, query_delay: float = 0.0) -> None:
        self.add_delay = add_delay
        self.query_delay = query_delay
        self.added_batches: list[dict[str, Any]] = []

    def delete(self, *, where: dict[str, Any] | None = None) -> None:  # noqa: ARG002
        # Metadata-filter delete never embeds text; a fast no-op here.
        return None

    def add(self, *, ids: list[str], documents: list[str], metadatas: list[dict[str, Any]]) -> None:
        if self.add_delay:
            time.sleep(self.add_delay)
        self.added_batches.append({"ids": ids, "documents": documents, "metadatas": metadatas})

    def count(self) -> int:
        if self.query_delay:
            time.sleep(self.query_delay)
        return 1

    def query(self, *, query_texts: list[str], n_results: int) -> dict[str, Any]:  # noqa: ARG002
        if self.query_delay:
            time.sleep(self.query_delay)
        return {"ids": [[]], "distances": [[]], "documents": [[]], "metadatas": [[]]}


class _StubClient:
    """Stand-in for ``self._chroma_client`` used by rebuild_deliberation_index."""

    def delete_collection(self, name: str) -> None:  # noqa: ARG002
        return None


def _insert_without_indexing(db: db_mod.KnowledgeDB, monkeypatch, delib_id: str, content: str) -> None:
    """Commit a canonical SQLite deliberation row without touching real Chroma.

    During the insert we force ``_get_chroma_collection`` to return ``None`` so
    the on-insert index step is a fast no-op and never loads a model. Callers
    then install a stub collection before exercising the index path directly.
    """
    monkeypatch.setattr(db, "_get_chroma_collection", lambda: None)
    db.insert_deliberation(
        id=delib_id,
        source_type="report",
        title="WI-4453 fixture",
        summary="Fixture deliberation for index-timeout tests.",
        content=content,
        changed_by="test",
        change_reason="WI-4453 index-timeout test fixture",
    )


class TestIndexEmbeddingTimeout:
    """Acceptance criteria for WI-4453 (bounded index embedding)."""

    def test_index_add_times_out_and_degrades(self, db, monkeypatch):
        """Index add cannot hang: a slow add degrades to sentinel 0 within bound.

        Acceptance: GOV-FILE-BRIDGE-AUTHORITY-001, WI-4453.
        """
        _insert_without_indexing(db, monkeypatch, "DELIB-WI4453-01", "Bounded index content.")

        slow = _StubCollection(add_delay=5.0)
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: slow)
        monkeypatch.setattr(db_mod, "_CHROMA_INDEX_TIMEOUT_SECONDS", 0.2)

        start = time.monotonic()
        result = db._index_deliberation_in_chroma("DELIB-WI4453-01")
        elapsed = time.monotonic() - start

        assert result == 0  # degraded sentinel: semantic index deferred
        assert elapsed < 2.0  # returned promptly; did NOT wait for the 5s add
        assert slow.added_batches == []  # the abandoned add never completed in-band

    def test_sqlite_row_intact_after_index_timeout(self, db, monkeypatch):
        """Canonical DA row survives an index timeout.

        Acceptance: GOV-SOURCE-OF-TRUTH-FRESHNESS-001.
        """
        _insert_without_indexing(db, monkeypatch, "DELIB-WI4453-02", "Canonical content must persist.")

        slow = _StubCollection(add_delay=5.0)
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: slow)
        monkeypatch.setattr(db_mod, "_CHROMA_INDEX_TIMEOUT_SECONDS", 0.2)

        assert db._index_deliberation_in_chroma("DELIB-WI4453-02") == 0

        row = db.get_deliberation("DELIB-WI4453-02")
        assert row is not None
        assert row["id"] == "DELIB-WI4453-02"
        assert row["content"] == "Canonical content must persist."

    def test_index_timeout_env_override(self, monkeypatch):
        """The index timeout is sourced from GTKB_CHROMA_INDEX_TIMEOUT_SECONDS.

        Acceptance: timeout is env-overridable.
        """
        try:
            monkeypatch.setenv("GTKB_CHROMA_INDEX_TIMEOUT_SECONDS", "0.05")
            importlib.reload(db_mod)
            assert db_mod._CHROMA_INDEX_TIMEOUT_SECONDS == 0.05
        finally:
            monkeypatch.delenv("GTKB_CHROMA_INDEX_TIMEOUT_SECONDS", raising=False)
            importlib.reload(db_mod)

        # Default restored after reload without the override present.
        assert db_mod._CHROMA_INDEX_TIMEOUT_SECONDS == 15.0

    def test_fast_index_path_still_indexes(self, db, monkeypatch):
        """A fast add still returns the real chunk count (no behavior change).

        Acceptance: normal (fast) index path unchanged.
        """
        _insert_without_indexing(db, monkeypatch, "DELIB-WI4453-03", "Short content indexes as one chunk.")

        fast = _StubCollection(add_delay=0.0)
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: fast)

        result = db._index_deliberation_in_chroma("DELIB-WI4453-03")

        assert result == 1  # short content -> single chunk, indexed normally
        assert len(fast.added_batches) == 1
        assert fast.added_batches[0]["ids"][0].startswith("DELIB-WI4453-03::")

    def test_search_still_bounded(self, db, monkeypatch):
        """FAB-17 preserved: a slow query degrades to the SQLite-LIKE fallback.

        Acceptance: search path regression guard.
        """
        _insert_without_indexing(db, monkeypatch, "DELIB-WI4453-04", "Append-only versioning discipline note.")

        slow = _StubCollection(query_delay=5.0)
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: slow)
        monkeypatch.setattr(db_mod, "_CHROMA_QUERY_TIMEOUT_SECONDS", 0.2)

        start = time.monotonic()
        results = db.search_deliberations("Append-only", limit=5)
        elapsed = time.monotonic() - start

        assert elapsed < 2.0  # bounded; did not hang on the 5s query
        assert len(results) >= 1
        assert results[0]["search_method"] == "text_match"  # degraded to SQLite LIKE

    def test_rebuild_degrades_per_record_on_index_timeout(self, db, monkeypatch):
        """Rebuild hardening: a slow add degrades per-record instead of hanging.

        Bounding ``_index_deliberation_in_chroma`` also hardens
        ``rebuild_deliberation_index``: each record's add is bounded, so an
        offline rebuild degrades (0 chunks, no error) rather than hanging on
        the first record. (GO condition 3 — rebuild path covered in this slice.)
        """
        _insert_without_indexing(db, monkeypatch, "DELIB-WI4453-05", "First rebuild record.")
        _insert_without_indexing(db, monkeypatch, "DELIB-WI4453-06", "Second rebuild record.")

        slow = _StubCollection(add_delay=5.0)
        monkeypatch.setattr(db, "_get_chroma_collection", lambda: slow)
        monkeypatch.setattr(db, "_chroma_client", _StubClient(), raising=False)
        monkeypatch.setattr(db_mod, "HAS_CHROMADB", True)
        monkeypatch.setattr(db_mod, "_CHROMA_INDEX_TIMEOUT_SECONDS", 0.2)

        start = time.monotonic()
        report = db.rebuild_deliberation_index()
        elapsed = time.monotonic() - start

        assert elapsed < 3.0  # per-record bound (~0.2s x 2), not an unbounded hang
        assert report["indexed"] == 2  # both records processed (degraded, not failed)
        assert report["chunks"] == 0  # semantic index deferred for both
        assert report["errors"] == []  # degradation is not an error
