"""Tests for Wave 2 Slice 10 ``_chromadb_regen.py``.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice10-005.md`` (REVISED-2)
and ``-006`` (Codex GO with implementation constraint: do NOT treat
``DELIB-*`` as a framework/adopter prefix; missing-manifest fallback
must classify as unclassified or apply tested content-scan rules).

Fixture-based per the Slice 4-9 / Slice 11 pattern. Tests construct a
synthetic ChromaDB SQLite store under ``tmp_path`` matching the live
schema (``collections``, ``segments``, ``embeddings``,
``embedding_metadata``).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import _chromadb_regen  # noqa: E402

# ---- Fixtures ---------------------------------------------------------


def _build_chroma_fixture(
    chroma_dir: Path,
    *,
    collection_name: str = "deliberations",
    dimension: int = 384,
    chunks: list[dict[str, Any]] | None = None,
) -> str:
    """Build a synthetic chroma.sqlite3 fixture with key/value-shape metadata.

    Returns the collection_id. Each chunk dict has shape:
    ``{"id": int, "metadata": {key: value, ...}}``. Metadata values are
    stored in the appropriate typed column (string_value / int_value /
    float_value / bool_value) per the live ChromaDB schema.
    """
    chroma_dir.mkdir(parents=True, exist_ok=True)
    db_path = chroma_dir / "chroma.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE collections (id TEXT, name TEXT, dimension INTEGER)")
    cur.execute("CREATE TABLE segments (id TEXT, collection TEXT)")
    cur.execute("CREATE TABLE embeddings (id INTEGER, segment_id TEXT)")
    cur.execute(
        "CREATE TABLE embedding_metadata "
        "(id INTEGER, key TEXT, string_value TEXT, "
        "int_value INTEGER, float_value REAL, bool_value INTEGER)"
    )
    collection_id = "test-collection-uuid"
    segment_id = "test-segment-uuid"
    cur.execute(
        "INSERT INTO collections VALUES (?, ?, ?)",
        (collection_id, collection_name, dimension),
    )
    cur.execute("INSERT INTO segments VALUES (?, ?)", (segment_id, collection_id))

    for chunk in chunks or []:
        cur.execute("INSERT INTO embeddings VALUES (?, ?)", (chunk["id"], segment_id))
        for key, value in chunk["metadata"].items():
            # bool must come BEFORE int because bool is subclass of int.
            if isinstance(value, bool):
                cur.execute(
                    "INSERT INTO embedding_metadata (id, key, bool_value) VALUES (?, ?, ?)",
                    (chunk["id"], key, int(value)),
                )
            elif isinstance(value, str):
                cur.execute(
                    "INSERT INTO embedding_metadata (id, key, string_value) VALUES (?, ?, ?)",
                    (chunk["id"], key, value),
                )
            elif isinstance(value, int):
                cur.execute(
                    "INSERT INTO embedding_metadata (id, key, int_value) VALUES (?, ?, ?)",
                    (chunk["id"], key, value),
                )
            elif isinstance(value, float):
                cur.execute(
                    "INSERT INTO embedding_metadata (id, key, float_value) VALUES (?, ?, ?)",
                    (chunk["id"], key, value),
                )
    conn.commit()
    conn.close()
    return collection_id


def _write_membase_manifest(output_dir: Path, records: list[dict[str, Any]]) -> Path:
    """Write a Slice 8 ``membase-partition-manifest.json`` fixture in producer shape.

    Per ``-008`` Codex NO-GO + ``-009`` REVISED-1 §1.1-1.2: filename and
    schema must match what ``_membase_export.py:854-865`` actually emits.
    Tests pass minimum-shape records (``{"id": ..., "classification": ...}``);
    helper enriches each entry with the audit fields a real Slice 8 entry
    carries (``table_name``, ``version_count``, ``max_version``,
    ``classification_signal``) so the fixture is shape-identical to producer
    output.
    """
    manifest_dir = output_dir / "membase_export"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "membase-partition-manifest.json"
    enriched_records = [
        {
            "id": r["id"],
            "table_name": r.get("table_name", "deliberations"),
            "version_count": r.get("version_count", 1),
            "max_version": r.get("max_version", 1),
            "classification": r["classification"],
            "classification_signal": r.get("classification_signal", "fixture"),
        }
        for r in records
    ]
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_at": "2026-04-27T00:00:00Z",
                "kb_path": "fixture",
                "summary": {
                    "tables_discovered": 1,
                    "versioned_records_count": len(enriched_records),
                },
                "versioned_records": enriched_records,
                "relationship_records": [],
                "per_session_records": [],
                "warnings": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return manifest_path


def _read_plan(output_dir: Path) -> dict[str, Any]:
    return json.loads((output_dir / "chromadb_regen" / "chromadb-regen-plan.json").read_text(encoding="utf-8"))


# =====================================================================
# Common contract
# =====================================================================


def test_run_dry_run_returns_skipped(tmp_path: Path) -> None:
    """Dry-run never reads ChromaDB."""
    result = _chromadb_regen.run({}, tmp_path / "output", dry_run=True)
    assert result["status"] == "skipped"
    assert result["metrics"] == {"reason": "dry_run"}


def test_run_returns_ok_when_chromadb_store_absent(tmp_path: Path) -> None:
    """Absent ChromaDB store → status='ok' with empty plan + warning."""
    result = _chromadb_regen.run({}, tmp_path / "output", chroma_path=tmp_path / "missing")
    assert result["status"] == "ok"
    assert any("chromadb_store_absent" in w for w in result["warnings"])


# =====================================================================
# Read-only access (proposal §1)
# =====================================================================


def test_run_opens_chroma_via_readonly_uri(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Per Codex `-002`/`-004`: lane opens chroma.sqlite3 with mode=ro URI."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(chroma_dir, chunks=[])

    captured_uris: list[str] = []
    real_connect = sqlite3.connect

    def _spy_connect(*args: object, **kwargs: object) -> sqlite3.Connection:
        if args:
            captured_uris.append(str(args[0]))
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(_chromadb_regen.sqlite3, "connect", _spy_connect)
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)

    ro_uris = [u for u in captured_uris if "?mode=ro" in u]
    assert ro_uris, "expected at least one mode=ro sqlite URI"


def test_run_attempt_to_write_chroma_via_lane_connection_raises_operationalerror(tmp_path: Path) -> None:
    """Verify physical read-only protection: a write on a mode=ro connection raises."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(chroma_dir, chunks=[])
    db_path = chroma_dir / "chroma.sqlite3"
    uri = f"file:{db_path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        conn.execute("INSERT INTO collections VALUES (?, ?, ?)", ("x", "y", 1))
    conn.close()


# =====================================================================
# Metadata pivot (proposal §1 Fix 1)
# =====================================================================


def test_run_pivots_metadata_per_chunk_id(tmp_path: Path) -> None:
    """Each chunk's key/value rows pivot into a single per-chunk dict."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[
            {
                "id": 1,
                "metadata": {
                    "delib_id": "DELIB-001",
                    "source_type": "owner_conversation",
                    "origin_project": "agent-red",
                    "chunk_index": 0,
                    "version": 1,
                },
            },
            {
                "id": 2,
                "metadata": {
                    "delib_id": "DELIB-002",
                    "source_type": "lo_review",
                    "origin_project": "agent-red",
                },
            },
        ],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["vector_count"] == 2
    keys = set(coll["metadata_keys_observed"])
    assert "delib_id" in keys
    assert "source_type" in keys
    assert "origin_project" in keys


def test_run_handles_metadata_with_typed_values_string_int_float_bool(tmp_path: Path) -> None:
    """Metadata pivot dispatches across all four typed value columns."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[
            {
                "id": 1,
                "metadata": {
                    "delib_id": "DELIB-001",  # string_value
                    "origin_project": "agent-red",  # string_value
                    "chunk_index": 5,  # int_value
                    "embedding_score": 0.92,  # float_value
                    "is_redacted": False,  # bool_value
                },
            },
        ],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    keys = set(coll["metadata_keys_observed"])
    # All 5 keys present despite different value types.
    assert {"delib_id", "origin_project", "chunk_index", "embedding_score", "is_redacted"}.issubset(keys)


# =====================================================================
# Classification — Tier 1: origin_project (proposal §2)
# =====================================================================


def test_run_classifies_chunk_via_origin_project_agent_red(tmp_path: Path) -> None:
    """origin_project=agent-red → adopter via Tier 1."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-001", "origin_project": "agent-red"}}],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["adopter_chunk_count"] == 1
    assert coll["framework_chunk_count"] == 0
    assert coll["classification_basis_counts"].get("origin_project") == 1


def test_run_classifies_chunk_via_origin_project_groundtruth_kb(tmp_path: Path) -> None:
    """origin_project=groundtruth-kb → framework via Tier 1."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-001", "origin_project": "groundtruth-kb"}}],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["framework_chunk_count"] == 1
    assert coll["adopter_chunk_count"] == 0


def test_run_does_not_classify_unrecognized_origin_project(tmp_path: Path) -> None:
    """origin_project='unknown-org' → falls through to Tier 2/3."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-001", "origin_project": "unknown-org"}}],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    # No origin_project Tier-1 hit; falls through. delib_id_prefix_fallback should fire.
    assert coll["classification_basis_counts"].get("origin_project", 0) == 0
    assert coll["classification_basis_counts"].get("delib_id_prefix_fallback", 0) == 1


# =====================================================================
# Classification — Tier 2: membase manifest cross-ref by delib_id
# =====================================================================


def test_run_classifies_chunk_via_membase_manifest_delib_id_lookup(tmp_path: Path) -> None:
    """Tier 2: chunk with no origin_project but matching delib_id in Slice 8 manifest."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-S313-001"}}],
    )
    _write_membase_manifest(
        tmp_path / "output",
        [{"id": "DELIB-S313-001", "classification": "adopter"}],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["adopter_chunk_count"] == 1
    assert coll["classification_basis_counts"].get("membase_manifest_delib_id") == 1


# =====================================================================
# Classification — Tier 3: delib_id prefix fallback (Codex `-006` constraint)
# =====================================================================


def test_run_classifies_chunk_via_delib_id_ar_prefix_fallback(tmp_path: Path) -> None:
    """delib_id starts with AR- → adopter (Tier 3 prefix fallback)."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"delib_id": "AR-001"}}],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["adopter_chunk_count"] == 1
    assert coll["classification_basis_counts"].get("delib_id_prefix_fallback") == 1


def test_run_classifies_chunk_via_delib_id_gtkb_prefix_fallback(tmp_path: Path) -> None:
    """delib_id starts with GTKB- → framework (Tier 3 prefix fallback)."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"delib_id": "GTKB-GOV-001"}}],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["framework_chunk_count"] == 1


def test_run_classifies_delib_prefixed_id_as_unclassified(tmp_path: Path) -> None:
    """Codex `-006` implementation constraint: DELIB-* is NOT a framework/adopter prefix.

    Per the GO: "Do not treat DELIB-* as a framework/adopter prefix.
    `classify_by_id_prefix()` only recognizes GTKB-* and AR-*."

    A DELIB-* id with no origin_project and no membase manifest entry must
    fall to unclassified, NOT silently route to framework or adopter.
    """
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-S313-UNKNOWN"}}],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["unclassified_chunk_count"] == 1
    assert coll["adopter_chunk_count"] == 0
    assert coll["framework_chunk_count"] == 0


def test_run_classifies_chunk_unclassified_when_no_pointer_found(tmp_path: Path) -> None:
    """Chunk with no delib_id and no origin_project → unclassified."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"chunk_index": 0}}],  # no delib_id, no origin_project
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["unclassified_chunk_count"] == 1


# =====================================================================
# Byte-stable safety (proposal §3.2)
# =====================================================================


def test_run_records_chroma_sqlite3_sha256_before_and_after(tmp_path: Path) -> None:
    """Byte-stable proof: SHA256 of chroma files captured before + after run."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(chroma_dir, chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-001"}}])
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    proof = plan["no_chromadb_mutation_proof"]
    assert "chroma_files_sha256_before" in proof
    assert "chroma_files_sha256_after" in proof
    assert proof["all_unchanged"] is True
    # SHA256 should be a 64-hex-char string per file.
    for h in proof["chroma_files_sha256_before"].values():
        assert len(h) == 64


def test_run_returns_error_when_chromadb_byte_stable_check_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If lane somehow mutates chroma files, byte-stable check fails → status='error'."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(chroma_dir, chunks=[])
    real_hash = _chromadb_regen._hash_chroma_files
    call_count = {"n": 0}

    def _diverging_hash(path: Path) -> dict[str, str]:
        call_count["n"] += 1
        # Simulate divergence on the second call (after-run hash).
        result = real_hash(path)
        if call_count["n"] >= 2:
            return {k: hashlib.sha256(b"DIFFERENT").hexdigest() for k in result}
        return result

    monkeypatch.setattr(_chromadb_regen, "_hash_chroma_files", _diverging_hash)
    result = _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    assert result["status"] == "error"
    assert any("chromadb_byte_stable_check_failed" in w for w in result["warnings"])


# =====================================================================
# Schema audit fields (proposal §3 Fix 3)
# =====================================================================


def test_run_exact_count_basis_is_full_metadata_pivot_via_direct_sqlite(tmp_path: Path) -> None:
    """Audit field name proves the pivot path was used."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-001", "origin_project": "agent-red"}}],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["exact_count_basis"] == "full_metadata_pivot_via_direct_sqlite"


def test_run_reads_embedding_dimension_from_collections_table_not_hardcoded(tmp_path: Path) -> None:
    """Codex `-004` Fix 3: dimension comes from `collections.dimension`, not hardcoded.

    Fixture sets dimension=512 (not 384, not 1536); plan must record 512.
    """
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(chroma_dir, dimension=512, chunks=[{"id": 1, "metadata": {}}])
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["embedding_dimension_from_collections_table"] == 512


# =====================================================================
# Safety regression: no ChromaDB Python API
# =====================================================================


def test_run_does_not_call_chromadb_python_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Lane uses sqlite3 stdlib only; never imports chromadb."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(chroma_dir, chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-001"}}])

    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__
    forbidden_imports: list[str] = []

    def _trap_import(name: str, *args: object, **kwargs: object) -> Any:
        if name == "chromadb" or name.startswith("chromadb."):
            forbidden_imports.append(name)
            raise AssertionError(f"Lane attempted to import {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _trap_import)
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    assert forbidden_imports == [], f"Lane imported: {forbidden_imports}"


# =====================================================================
# Output artifacts
# =====================================================================


def test_run_writes_chromadb_regen_plan_json(tmp_path: Path) -> None:
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(chroma_dir, chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-001"}}])
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    json_path = tmp_path / "output" / "chromadb_regen" / "chromadb-regen-plan.json"
    assert json_path.exists()
    plan = json.loads(json_path.read_text(encoding="utf-8"))
    assert plan["schema_version"] == 1
    assert "collections" in plan
    assert "regen_plan" in plan
    assert "no_chromadb_mutation_proof" in plan


def test_run_writes_preview_markdown(tmp_path: Path) -> None:
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(chroma_dir, chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-001"}}])
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    md_path = tmp_path / "output" / "chromadb_regen" / "chromadb-regen-preview.md"
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "# ChromaDB Regeneration Plan" in content
    assert "## Summary" in content


def test_run_writes_result_json_on_ok_path(tmp_path: Path) -> None:
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(chroma_dir, chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-001"}}])
    result = _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    assert result["status"] == "ok"
    result_path = tmp_path / "output" / "chromadb_regen" / "result.json"
    assert result_path.exists()


def test_run_estimates_walltime_and_token_cost(tmp_path: Path) -> None:
    """Cost estimation: chunk count × per-embed walltime + per-chunk tokens."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[
            {"id": 1, "metadata": {"delib_id": "DELIB-001"}},
            {"id": 2, "metadata": {"delib_id": "DELIB-002"}},
            {"id": 3, "metadata": {"delib_id": "DELIB-003"}},
        ],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["estimated_walltime_seconds"] > 0
    assert coll["estimated_token_cost"] > 0
    # 3 chunks × 0.05s = 0.15s; 3 × 256 tokens = 768.
    assert coll["estimated_walltime_seconds"] == pytest.approx(0.15, abs=0.01)
    assert coll["estimated_token_cost"] == 768


def test_run_emits_classification_basis_counts(tmp_path: Path) -> None:
    """Classification basis counts segregate Tier 1 / Tier 2 / Tier 3 fallback paths."""
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[
            # Tier 1: origin_project hit
            {"id": 1, "metadata": {"delib_id": "DELIB-001", "origin_project": "agent-red"}},
            # Tier 2: membase manifest hit (no origin_project)
            {"id": 2, "metadata": {"delib_id": "DELIB-S313-002"}},
            # Tier 3: prefix fallback (AR-)
            {"id": 3, "metadata": {"delib_id": "AR-100"}},
        ],
    )
    _write_membase_manifest(
        tmp_path / "output",
        [{"id": "DELIB-S313-002", "classification": "adopter"}],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["classification_basis_counts"].get("origin_project") == 1
    assert coll["classification_basis_counts"].get("membase_manifest_delib_id") == 1
    assert coll["classification_basis_counts"].get("delib_id_prefix_fallback") == 1


# =====================================================================
# Source type distribution (per Codex `-006` review ask 3)
# =====================================================================


def test_run_records_source_type_distribution(tmp_path: Path) -> None:
    """source_type distribution recorded for operator review (lo_review,
    bridge_thread, owner_conversation, etc.).
    """
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[
            {"id": 1, "metadata": {"delib_id": "DELIB-001", "source_type": "lo_review"}},
            {"id": 2, "metadata": {"delib_id": "DELIB-002", "source_type": "lo_review"}},
            {"id": 3, "metadata": {"delib_id": "DELIB-003", "source_type": "bridge_thread"}},
        ],
    )
    _chromadb_regen.run({}, tmp_path / "output", chroma_path=chroma_dir)
    plan = _read_plan(tmp_path / "output")
    coll = plan["collections"][0]
    assert coll["source_type_distribution"] == {"lo_review": 2, "bridge_thread": 1}


# =====================================================================
# REVISED-1 (S315): Slice 8 producer-shape compatibility
# Per bridge/gtkb-isolation-016-phase8-wave2-slice10-008.md NO-GO +
# bridge/gtkb-isolation-016-phase8-wave2-slice10-009.md REVISED-1.
# =====================================================================


def test_load_membase_partition_manifest_uses_real_producer_filename(tmp_path: Path) -> None:
    """Default path must be ``membase-partition-manifest.json`` (the real
    Slice 8 producer filename), not the test-only ``partition_manifest.json``.

    Regression guard for the `-008` NO-GO finding.
    """
    output_dir = tmp_path / "output"
    _write_membase_manifest(
        output_dir,
        [{"id": "DELIB-PRODUCER-FILENAME-001", "classification": "framework"}],
    )
    # Helper writes the real producer filename; if the loader looked at the
    # old test-only filename, this map would be empty.
    result = _chromadb_regen._load_membase_partition_manifest(output_dir)
    assert result == {"DELIB-PRODUCER-FILENAME-001": "framework"}


def test_load_membase_partition_manifest_parses_versioned_records_key(tmp_path: Path) -> None:
    """Loader must consume ``versioned_records[*]``, not the test-only ``records[*]`` key.

    Regression guard: explicitly write a manifest with both keys; only
    ``versioned_records`` should produce entries.
    """
    output_dir = tmp_path / "output"
    manifest_dir = output_dir / "membase_export"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / "membase-partition-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "versioned_records": [
                    {"id": "DELIB-VR-001", "classification": "adopter"},
                ],
                "records": [
                    # Old test-only key — must be ignored.
                    {"id": "DELIB-OLD-KEY-002", "classification": "framework"},
                ],
            }
        ),
        encoding="utf-8",
    )
    result = _chromadb_regen._load_membase_partition_manifest(output_dir)
    assert result == {"DELIB-VR-001": "adopter"}
    assert "DELIB-OLD-KEY-002" not in result


def test_load_membase_partition_manifest_skips_invalid_classifications(tmp_path: Path) -> None:
    """Records carrying unrecognized classifications are skipped (defense-in-depth).

    Only ``framework``, ``adopter``, ``unclassified`` are accepted.
    """
    output_dir = tmp_path / "output"
    manifest_dir = output_dir / "membase_export"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / "membase-partition-manifest.json").write_text(
        json.dumps(
            {
                "versioned_records": [
                    {"id": "DELIB-OK-001", "classification": "adopter"},
                    {"id": "DELIB-BAD-002", "classification": "MALFORMED"},
                    {"id": "DELIB-NONE-003", "classification": None},
                    {"classification": "framework"},  # missing id
                ],
            }
        ),
        encoding="utf-8",
    )
    result = _chromadb_regen._load_membase_partition_manifest(output_dir)
    assert result == {"DELIB-OK-001": "adopter"}


def test_run_honors_explicit_partition_manifest_path_verbatim(tmp_path: Path) -> None:
    """Per `-008` NO-GO §3 + `-009` REVISED-1 §1.3: the explicit
    ``partition_manifest_path`` keyword must be honored as a full path,
    not stripped to its parent and rejoined with a hard-coded filename.

    Test writes a manifest at a non-default custom location and proves the
    chunk gets classified from THAT manifest (not from anything under
    ``output_dir/membase_export/``).
    """
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"delib_id": "DELIB-CUSTOM-PATH-001"}}],
    )
    custom_dir = tmp_path / "elsewhere" / "nested"
    custom_dir.mkdir(parents=True, exist_ok=True)
    custom_manifest = custom_dir / "renamed-manifest.json"
    custom_manifest.write_text(
        json.dumps(
            {
                "versioned_records": [
                    {"id": "DELIB-CUSTOM-PATH-001", "classification": "framework"},
                ],
            }
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "output"
    # Note: NO manifest is written under output_dir/membase_export/ — the
    # only manifest is at the custom path. If the override-handling bug
    # were still present, the loader would look for
    # output_dir/membase_export/<old-name> and find nothing.
    _chromadb_regen.run({}, output_dir, chroma_path=chroma_dir, partition_manifest_path=custom_manifest)
    plan = _read_plan(output_dir)
    coll = plan["collections"][0]
    assert coll["framework_chunk_count"] == 1
    assert coll["classification_basis_counts"].get("membase_manifest_delib_id") == 1


def test_run_classifies_via_real_membase_partition_manifest_when_slice8_lane_runs_first(
    tmp_path: Path,
) -> None:
    """Coordinated integration test per `-008` NO-GO §"Required Revision" item 4.

    Drives the real ``_membase_export.run()`` against the live ``groundtruth.db``,
    then drives ``_chromadb_regen.run()`` against the same output directory
    using a synthetic ChromaDB fixture seeded with one DELIB-* id pulled
    from the just-emitted manifest. Asserts the cross-reference path
    actually fires (``classification_basis_counts["membase_manifest_delib_id"] >= 1``).

    Skipped when the live KB is not present (keeps suite hermetic).
    """
    from rehearse import _common, _membase_export

    live_kb = _common.LEGACY_ROOT / "groundtruth.db"
    if not live_kb.exists():
        pytest.skip(f"live KB not present at {live_kb}; integration test requires it")

    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: real Slice 8 emits the producer-shape manifest into output_dir.
    membase_result = _membase_export.run({}, output_dir)
    assert membase_result["status"] == "ok", f"Slice 8 lane failed: {membase_result}"
    manifest_path = output_dir / "membase_export" / "membase-partition-manifest.json"
    assert manifest_path.exists(), "Slice 8 did not emit manifest at expected path"

    # Step 2: pull one real DELIB-* id from the manifest's versioned_records.
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    deliberation_entries = [
        r
        for r in manifest_data["versioned_records"]
        if r.get("table_name") == "deliberations" and isinstance(r.get("id"), str) and r["id"].startswith("DELIB-")
    ]
    if not deliberation_entries:
        pytest.skip("live KB has no deliberations table entries; cannot exercise cross-ref path")
    sample_entry = deliberation_entries[0]
    sample_id = sample_entry["id"]
    sample_classification = sample_entry["classification"]

    # Step 3: build a synthetic ChromaDB fixture with one chunk that
    # references the real DELIB-* id (no origin_project so Tier 1 misses
    # and Tier 2 manifest cross-ref must fire).
    chroma_dir = tmp_path / "chroma"
    _build_chroma_fixture(
        chroma_dir,
        chunks=[{"id": 1, "metadata": {"delib_id": sample_id}}],
    )

    # Step 4: real Slice 10 reads the same output_dir, pulling in Slice 8's manifest.
    chromadb_result = _chromadb_regen.run({}, output_dir, chroma_path=chroma_dir)
    assert chromadb_result["status"] == "ok", f"Slice 10 lane failed: {chromadb_result}"

    plan = _read_plan(output_dir)
    coll = plan["collections"][0]
    # The proof shape Codex `-008` reported as missing.
    assert coll["classification_basis_counts"].get("membase_manifest_delib_id", 0) >= 1, (
        f"Tier 2 manifest cross-ref did not fire; basis_counts={coll['classification_basis_counts']}"
    )
    # The chunk's classification must match the manifest's recorded value.
    if sample_classification == "framework":
        assert coll["framework_chunk_count"] == 1
    elif sample_classification == "adopter":
        assert coll["adopter_chunk_count"] == 1
    else:
        assert coll["unclassified_chunk_count"] == 1
