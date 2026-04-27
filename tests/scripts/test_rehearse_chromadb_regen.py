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
    """Write a Slice 8 partition_manifest.json fixture for tier-2 cross-ref tests."""
    manifest_dir = output_dir / "membase_export"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "partition_manifest.json"
    manifest_path.write_text(
        json.dumps({"records": records}, indent=2),
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
