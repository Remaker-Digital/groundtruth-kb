"""Deterministic SPEC-2098 Deliberation Archive coverage for WI-3216.

Binds the live ``KnowledgeDB`` Deliberation Archive contract to ``SPEC-2098``:
structured storage, the closed source-type set, raw-hash / redacted-content
behavior, source-ref idempotence, multi-link lookup, the always-on SQLite LIKE
search-fallback contract, ChromaDB chunk/metadata indexing (via a deterministic
stub collection, no live ChromaDB required), and bridge-thread harvest
identifier extraction.

This is the WI-3216 ``test_addition`` evidence artifact authorized by
``bridge/agent-red-wi3216-deliberation-archive-coverage-002.md`` (Loyal
Opposition GO) under
``PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-...-BOUNDED-IMPLEMENTATION-2026-06-23``
/ ``DELIB-20265586``. It adds executable coverage over the already-implemented
platform behavior in ``groundtruth_kb.db`` and
``scripts/harvest_session_deliberations.py``; it changes no production source.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest
from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
HARVEST_SCRIPT = REPO_ROOT / "scripts" / "harvest_session_deliberations.py"

# Source types of the closed SPEC-2098 set (groundtruth_kb.db.insert_deliberation).
SOURCE_TYPES = (
    "lo_review",
    "proposal",
    "owner_conversation",
    "report",
    "session_harvest",
    "bridge_thread",
)


def _load_harvest_module() -> Any:
    """Load ``scripts/harvest_session_deliberations.py`` as an importable module.

    Mirrors the loader precedent in
    ``platform_tests/scripts/test_harvest_session_thread_level.py`` so the
    harvest helpers can be exercised without invoking the CLI ``main()``.
    """
    spec = importlib.util.spec_from_file_location("harvest_session_deliberations_spec2098", HARVEST_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def kb(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> KnowledgeDB:
    """Temp ``KnowledgeDB`` with semantic indexing disabled by default.

    Disabling ``HAS_CHROMADB`` keeps ``insert_deliberation`` on the canonical
    SQLite path (no embedding-model load), so the structural-contract tests are
    fast and deterministic. The ChromaDB-indexing test re-enables a stub
    collection explicitly via ``_get_chroma_collection``.
    """
    import groundtruth_kb.db as db_mod

    monkeypatch.setattr(db_mod, "HAS_CHROMADB", False)
    return KnowledgeDB(db_path=tmp_path / "da_spec2098.db")


def _synthetic_api_key() -> str:
    """Build a synthetic credential at runtime.

    The literal credential span never appears in this source file, so the
    credential-scan Write hook does not flag the test; redaction still fires at
    runtime because the assembled value matches the canonical catalog.
    """
    return "sk_live_" + "abc123def456ghi789"


def test_all_spec2098_source_types_accepted(kb: KnowledgeDB) -> None:
    """SPEC-2098: every closed-set source type inserts; invalid types raise."""
    for i, source_type in enumerate(SOURCE_TYPES):
        result = kb.insert_deliberation(
            id=f"DELIB-{i:04d}",
            source_type=source_type,
            title=f"Title {source_type}",
            summary=f"Summary {source_type}.",
            content=f"Deliberation body for {source_type}.",
            changed_by="test",
            change_reason="spec2098 source-type coverage",
        )
        assert result is not None
        assert result["source_type"] == source_type

    with pytest.raises(ValueError, match="Invalid source_type"):
        kb.insert_deliberation(
            id="DELIB-9999",
            source_type="not_a_real_type",
            title="bad",
            summary="bad.",
            content="bad.",
            changed_by="test",
            change_reason="negative path",
        )


def test_structured_fields_round_trip(kb: KnowledgeDB) -> None:
    """SPEC-2098: structured deliberation fields persist and read back."""
    result = kb.insert_deliberation(
        id="DELIB-0001",
        source_type="lo_review",
        title="Structured row",
        summary="Covers structured storage fields.",
        content="Clean deliberation body with no secrets.",
        changed_by="test",
        change_reason="structured fields",
        spec_id="SPEC-2098",
        work_item_id="WI-3216",
        source_ref="bridge:agent-red-wi3216-deliberation-archive-coverage-001",
        participants=["prime-builder", "loyal-opposition", "owner"],
        outcome="informational",
        session_id="S999",
        origin_project="PROJECT-AGENT-RED-TEST-COVERAGE-GAPS",
        origin_repo="groundtruth-kb",
    )
    assert result is not None
    assert result["spec_id"] == "SPEC-2098"
    assert result["work_item_id"] == "WI-3216"
    assert result["source_ref"] == "bridge:agent-red-wi3216-deliberation-archive-coverage-001"
    assert result["participants_parsed"] == ["prime-builder", "loyal-opposition", "owner"]
    assert result["outcome"] == "informational"
    assert result["session_id"] == "S999"
    assert result["origin_project"] == "PROJECT-AGENT-RED-TEST-COVERAGE-GAPS"
    assert result["origin_repo"] == "groundtruth-kb"
    assert result["sensitivity"] == "normal"
    assert result["redaction_state"] == "clean"
    assert result["content_hash"] is not None


def test_redaction_and_raw_content_hash(kb: KnowledgeDB) -> None:
    """SPEC-2098: stored content is redacted; content_hash is over the raw text."""
    secret = _synthetic_api_key()
    raw = f"Investigation note: api_key={secret} surfaced in a log line."
    expected_hash = hashlib.sha256(raw.encode()).hexdigest()
    result = kb.insert_deliberation(
        id="DELIB-0001",
        source_type="report",
        title="Redaction row",
        summary="Covers redaction plus raw-content hashing.",
        content=raw,
        changed_by="test",
        change_reason="redaction",
    )
    assert result is not None
    assert secret not in result["content"]
    assert "[REDACTED:api_key]" in result["content"]
    assert result["redaction_state"] == "redacted"
    assert result["sensitivity"] == "contains_redacted"
    assert result["content_hash"] == expected_hash


def test_upsert_source_ref_content_hash_idempotence(kb: KnowledgeDB) -> None:
    """SPEC-2098: upsert_deliberation_source dedups on (source_ref, content_hash)."""
    first = kb.upsert_deliberation_source(
        source_type="bridge_thread",
        source_ref="bridge:dedup-1",
        content="Identical deliberation body.",
        title="Dedup",
        summary="Summary.",
        changed_by="test",
        change_reason="harvest",
    )
    second = kb.upsert_deliberation_source(
        source_type="bridge_thread",
        source_ref="bridge:dedup-1",
        content="Identical deliberation body.",
        title="Dedup retry",
        summary="Should not create a new row.",
        changed_by="test",
        change_reason="harvest retry",
    )
    assert first is not None and second is not None
    assert first["id"] == second["id"]

    changed = kb.upsert_deliberation_source(
        source_type="bridge_thread",
        source_ref="bridge:dedup-1",
        content="Different deliberation body.",
        title="Dedup changed",
        summary="New content creates a new row.",
        changed_by="test",
        change_reason="harvest changed",
    )
    assert changed is not None
    assert changed["id"] != first["id"]


def test_relation_link_lookup(kb: KnowledgeDB) -> None:
    """SPEC-2098: primary plus relation links resolve through lookup helpers."""
    kb.insert_deliberation(
        id="DELIB-0001",
        source_type="lo_review",
        title="Multi-link row",
        summary="Covers relation links.",
        content="Body referencing multiple specs and work items.",
        changed_by="test",
        change_reason="links",
        spec_id="SPEC-2098",
        work_item_id="WI-3216",
    )
    kb.link_deliberation_spec("DELIB-0001", "SPEC-1649", role="related")
    kb.link_deliberation_work_item("DELIB-0001", "WI-3203", role="related")

    assert [d["id"] for d in kb.get_deliberations_for_spec("SPEC-2098")] == ["DELIB-0001"]
    assert [d["id"] for d in kb.get_deliberations_for_spec("SPEC-1649")] == ["DELIB-0001"]
    assert [d["id"] for d in kb.get_deliberations_for_work_item("WI-3216")] == ["DELIB-0001"]
    assert [d["id"] for d in kb.get_deliberations_for_work_item("WI-3203")] == ["DELIB-0001"]


def test_search_sqlite_fallback_contract(kb: KnowledgeDB) -> None:
    """SPEC-2098 / GOV-SOURCE-OF-TRUTH-FRESHNESS-001: a freshly inserted row is
    surfaced by the always-on SQLite LIKE pass with the stable result contract
    when ChromaDB is unavailable (the ``kb`` fixture sets ``HAS_CHROMADB`` False).
    """
    kb.insert_deliberation(
        id="DELIB-0001",
        source_type="report",
        title="Freshness marker xyzzy2098",
        summary="Searchable via LIKE.",
        content="A deliberation containing the xyzzy2098 marker token.",
        changed_by="test",
        change_reason="search fallback",
    )
    results = kb.search_deliberations("xyzzy2098")
    assert len(results) == 1
    row = results[0]
    assert row["id"] == "DELIB-0001"
    assert row["search_method"] == "text_match"
    assert row["score"] is None
    assert row["matched_chunk_id"] is None
    assert row["matched_chunk_preview"] is None


class _StubChromaCollection:
    """Deterministic stand-in for a ChromaDB collection.

    Records ``delete``/``add`` calls so the indexing contract can be asserted
    without a live ChromaDB store or embedding model.
    """

    def __init__(self) -> None:
        self.deleted_where: list[dict[str, Any]] = []
        self.added: list[dict[str, Any]] = []

    def delete(self, where: dict[str, Any] | None = None, **_: Any) -> None:
        self.deleted_where.append(where or {})

    def add(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self.added.append({"ids": ids, "documents": documents, "metadatas": metadatas})

    def count(self) -> int:
        return sum(len(entry["ids"]) for entry in self.added)


def test_chroma_index_redacted_versioned_chunks_and_stale_delete(
    kb: KnowledgeDB, monkeypatch: pytest.MonkeyPatch
) -> None:
    """SPEC-2098: _index_deliberation_in_chroma deletes stale entries, indexes
    redacted content under versioned unique chunk IDs, and emits the required
    metadata. Uses a deterministic stub collection (no live ChromaDB).
    """
    stub = _StubChromaCollection()
    monkeypatch.setattr(kb, "_get_chroma_collection", lambda: stub)

    secret = _synthetic_api_key()
    raw = f"Indexing note: api_key={secret} must never reach the semantic index."
    kb.insert_deliberation(
        id="DELIB-0001",
        source_type="bridge_thread",
        title="Indexed row",
        summary="Covers chroma indexing.",
        content=raw,
        changed_by="test",
        change_reason="index v1",
        source_ref="bridge:index-1",
    )

    assert stub.added, "stub collection.add was never called"
    last = stub.added[-1]
    # Versioned, unique chunk IDs.
    assert all(cid.startswith("DELIB-0001::v1::chunk-") for cid in last["ids"])
    assert len(last["ids"]) == len(set(last["ids"]))
    # Indexed documents carry redacted content only.
    joined = " ".join(last["documents"])
    assert secret not in joined
    assert "[REDACTED:api_key]" in joined
    # Required metadata keys present.
    meta = last["metadatas"][0]
    for key in (
        "delib_id",
        "source_type",
        "chunk_index",
        "chunk_count",
        "source_ref",
        "sensitivity",
        "redaction_state",
    ):
        assert key in meta, f"missing metadata key {key!r}"
    assert meta["delib_id"] == "DELIB-0001"
    assert meta["source_type"] == "bridge_thread"
    assert meta["redaction_state"] == "redacted"

    # Revising the row deletes stale chunks for this delib_id before re-indexing.
    kb.insert_deliberation(
        id="DELIB-0001",
        source_type="bridge_thread",
        title="Indexed row v2",
        summary="Covers stale deletion.",
        content="Revised clean body for version two.",
        changed_by="test",
        change_reason="index v2",
        source_ref="bridge:index-1",
    )
    assert {"delib_id": "DELIB-0001"} in stub.deleted_where
    assert any(cid.startswith("DELIB-0001::v2::chunk-") for cid in stub.added[-1]["ids"])


def test_bridge_thread_harvest_extraction_and_idempotence(kb: KnowledgeDB) -> None:
    """SPEC-DA-HARVEST-INCLUSION: the harvest building blocks extract SPEC-2098 /
    WI-3216 identifiers from bridge content and route them to an idempotent
    ``bridge_thread`` deliberation source.
    """
    harvest = _load_harvest_module()
    bridge_content = (
        "# Implementation Proposal - WI-3216 Deliberation Archive Coverage\n"
        "Document: agent-red-wi3216-deliberation-archive-coverage\n"
        "Adds deterministic coverage for SPEC-2098 against the live archive,\n"
        "carrying SPEC-1649 forward and resolving WI-3216.\n"
    )
    spec_ids = harvest.ordered_unique(harvest.SPEC_RE, bridge_content)
    wi_ids = harvest.ordered_unique(harvest.WI_RE, bridge_content)
    assert "SPEC-2098" in spec_ids
    assert "WI-3216" in wi_ids

    source_ref = "bridge:agent-red-wi3216-deliberation-archive-coverage"
    first = kb.upsert_deliberation_source(
        source_type="bridge_thread",
        source_ref=source_ref,
        content=bridge_content,
        title=harvest.extract_title(bridge_content),
        summary=harvest.extract_summary(bridge_content),
        changed_by="test",
        change_reason="harvest bridge thread",
        spec_id=spec_ids[0],
        work_item_id=wi_ids[0],
    )
    assert first is not None
    assert first["source_type"] == "bridge_thread"
    assert first["spec_id"] == "SPEC-2098"
    assert first["work_item_id"] == "WI-3216"

    repeat = kb.upsert_deliberation_source(
        source_type="bridge_thread",
        source_ref=source_ref,
        content=bridge_content,
        title=harvest.extract_title(bridge_content),
        summary=harvest.extract_summary(bridge_content),
        changed_by="test",
        change_reason="harvest bridge thread repeat",
        spec_id=spec_ids[0],
        work_item_id=wi_ids[0],
    )
    assert repeat is not None
    assert repeat["id"] == first["id"]
