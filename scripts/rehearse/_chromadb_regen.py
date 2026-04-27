"""Wave 2 lane 5 (Stage C): ChromaDB regeneration plan.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice10-005.md`` (REVISED-2)
and ``-006`` (Codex GO).

Read-only inventory of the live ChromaDB store at
``.groundtruth-chroma/chroma.sqlite3``. Produces a regen plan
classifying each chunk by ``origin_project`` (primary, ~98% coverage)
with Slice 8 manifest cross-reference fallback on ``delib_id``.

**Critical safety properties:**
1. Read-only via ``sqlite3.connect(uri='file:...?mode=ro', uri=True)`` —
   any INSERT/UPDATE/DELETE attempted on this connection raises
   ``sqlite3.OperationalError: attempt to write a readonly database``.
2. ChromaDB Python API is NOT used; lane uses sqlite3 module from the
   standard library only. Test guards prove this.
3. Byte-stable safety: SHA256 of ``chroma.sqlite3`` + collection-UUID
   directory files captured before AND after; ``all_unchanged: True``
   required for ``status='ok'``.

Outputs:
  - ``chromadb-regen-plan.json``
  - ``chromadb-regen-preview.md``
  - ``result.json`` (standard sub-script result envelope)
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from rehearse._common import LEGACY_ROOT
from rehearse._split_helper import emit_result

# ---- Classification ---------------------------------------------------

# origin_project values that classify as adopter (verified 2026-04-27 against
# live ChromaDB: distribution shows agent-red, Agent Red Customer Engagement,
# Agent Red Customer Experience, agent-red-customer-engagement variants).
_ADOPTER_ORIGIN_PROJECT_VALUES: frozenset[str] = frozenset(
    {
        "agent-red",
        "agent-red-customer-engagement",
        "agent red customer engagement",
        "agent red customer experience",
    }
)

# origin_project values that classify as framework.
_FRAMEWORK_ORIGIN_PROJECT_VALUES: frozenset[str] = frozenset(
    {
        "groundtruth-kb",
        "groundtruth_kb",
        "gt-kb",
    }
)


def _classify_origin_project(value: str | None) -> tuple[str, str] | None:
    """Classify by origin_project string.

    Returns (classification, signal) or None if value is unrecognized.
    """
    if not value:
        return None
    normalized = value.lower().strip()
    if normalized in _ADOPTER_ORIGIN_PROJECT_VALUES:
        return ("adopter", "origin_project_adopter_explicit")
    if normalized in _FRAMEWORK_ORIGIN_PROJECT_VALUES:
        return ("framework", "origin_project_framework_explicit")
    return None


def _classify_by_delib_id_prefix(delib_id: str | None) -> tuple[str, str]:
    """Fallback classification by delib_id prefix.

    Returns (classification, signal). When no signal can be derived,
    returns unclassified with explanatory signal.
    """
    if not delib_id:
        return ("unclassified", "metadata_lacks_classification_pointer")
    if delib_id.startswith("AR-"):
        return ("adopter", "delib_id_ar_prefix")
    if delib_id.startswith("GTKB-"):
        return ("framework", "delib_id_gtkb_prefix")
    if delib_id.startswith("DELIB-"):
        return ("unclassified", "delib_id_no_subject_prefix")
    return ("unclassified", "delib_id_unknown_prefix")


def _classify_chunk(metadata: dict[str, Any]) -> tuple[str, str]:
    """Classify a single chunk's pivoted metadata.

    Tier 1: origin_project (most chunks have this; ~98% coverage in live data)
    Tier 2: delib_id prefix fallback
    """
    origin_class = _classify_origin_project(metadata.get("origin_project"))
    if origin_class is not None:
        return origin_class
    return _classify_by_delib_id_prefix(metadata.get("delib_id"))


# ---- ChromaDB SQLite probes ------------------------------------------


def _open_chroma_readonly(chroma_path: Path) -> sqlite3.Connection:
    """Open chroma.sqlite3 with physical read-only protection.

    Per Codex Slice 10 ``-002`` + ``-004`` constraint: ``mode=ro`` URI is
    enforced at SQLite open. Any INSERT/UPDATE/DELETE attempted on this
    connection raises ``OperationalError``.
    """
    db_path = chroma_path / "chroma.sqlite3"
    uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _read_collections(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Read collection metadata."""
    cur = conn.cursor()
    cur.execute("SELECT id, name, dimension FROM collections")
    return [{"id": row[0], "name": row[1], "dimension": row[2]} for row in cur.fetchall()]


def _pivot_metadata_per_chunk(
    conn: sqlite3.Connection,
    collection_id: str,
) -> dict[int, dict[str, Any]]:
    """Pivot embedding_metadata key/value rows into per-chunk metadata dicts.

    Per Codex Slice 10 ``-004`` Required Revision: define a pivot/grouping
    step keyed by ``embedding_metadata.id`` so one chunk record is built
    from all metadata key/value rows for that embedding.

    Returns ``{chunk_id: {key: value, ...}}`` for chunks belonging to the
    named collection. Single SQL pass with join filters chunks at the DB
    layer.
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT em.id, em.key, em.string_value, em.int_value, em.float_value, em.bool_value
        FROM embedding_metadata em
        JOIN embeddings e ON em.id = e.id
        JOIN segments s ON e.segment_id = s.id
        WHERE s.collection = ?
        """,
        (collection_id,),
    )
    chunks: dict[int, dict[str, Any]] = {}
    for row_id, key, sv, iv, fv, bv in cur.fetchall():
        if sv is not None:
            value: Any = sv
        elif iv is not None:
            value = iv
        elif fv is not None:
            value = fv
        elif bv is not None:
            value = bool(bv)
        else:
            value = None
        chunks.setdefault(row_id, {})[key] = value
    return chunks


def _load_membase_partition_manifest(output_dir: Path) -> dict[str, str]:
    """Load Slice 8's per-record classification map, if present in same output dir.

    Returns ``{record_id: classification}`` keyed by record ID. Used as
    optional Tier 1 fallback when ``origin_project`` is missing/unrecognized.
    Empty dict when Slice 8 output is absent — Slice 10 then falls back to
    Tier 2 (delib_id prefix) per design.
    """
    manifest_path = output_dir / "membase_export" / "partition_manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    records = data.get("records", []) if isinstance(data, dict) else []
    return {r["id"]: r.get("classification", "unclassified") for r in records if isinstance(r, dict) and "id" in r}


# ---- Byte-stable safety ----------------------------------------------


def _hash_chroma_files(chroma_path: Path) -> dict[str, str]:
    """Compute SHA256 of chroma.sqlite3 + every file in collection-UUID dirs.

    Returns ``{relative_path: sha256_hex}``. Used by the byte-stable
    safety check (before/after the lane runs).
    """
    hashes: dict[str, str] = {}
    if not chroma_path.exists() or not chroma_path.is_dir():
        return hashes
    for path in sorted(chroma_path.rglob("*")):
        if path.is_file():
            try:
                rel = str(path.relative_to(chroma_path)).replace("\\", "/")
                hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                pass
    return hashes


# ---- Cost estimation -------------------------------------------------

# Default per-embed walltime + per-chunk token estimates (for cost
# preview only; not a precise prediction).
_AVG_EMBED_WALLTIME_SECONDS = 0.05
_AVG_EMBED_TOKENS_PER_CHUNK = 256


def _estimate_regen_cost(chunk_count: int) -> dict[str, float]:
    """Estimate regen walltime + token cost from chunk count."""
    return {
        "estimated_walltime_seconds": round(chunk_count * _AVG_EMBED_WALLTIME_SECONDS, 2),
        "estimated_token_cost": chunk_count * _AVG_EMBED_TOKENS_PER_CHUNK,
    }


# ---- Emitters ---------------------------------------------------------


def _build_collection_summary(
    coll: dict[str, Any],
    metadata_by_chunk: dict[int, dict[str, Any]],
    membase_manifest: dict[str, str],
) -> dict[str, Any]:
    """Classify chunks, aggregate per-classification counts, build collection summary."""
    framework_count = 0
    adopter_count = 0
    unclassified_count = 0
    metadata_keys_observed: set[str] = set()
    source_types: dict[str, int] = {}
    classification_basis_counts: dict[str, int] = {}

    for chunk_metadata in metadata_by_chunk.values():
        metadata_keys_observed.update(chunk_metadata.keys())
        st = chunk_metadata.get("source_type")
        if isinstance(st, str):
            source_types[st] = source_types.get(st, 0) + 1

        # Try Tier 1 first (origin_project), then Tier 2 (Slice 8 manifest
        # cross-ref by delib_id), then Tier 3 (delib_id prefix).
        tier1 = _classify_origin_project(chunk_metadata.get("origin_project"))
        if tier1 is not None:
            classification, _signal = tier1
            classification_basis_counts["origin_project"] = classification_basis_counts.get("origin_project", 0) + 1
        elif membase_manifest and chunk_metadata.get("delib_id") in membase_manifest:
            classification = membase_manifest[chunk_metadata["delib_id"]]
            classification_basis_counts["membase_manifest_delib_id"] = (
                classification_basis_counts.get("membase_manifest_delib_id", 0) + 1
            )
        else:
            classification, _signal = _classify_by_delib_id_prefix(chunk_metadata.get("delib_id"))
            classification_basis_counts["delib_id_prefix_fallback"] = (
                classification_basis_counts.get("delib_id_prefix_fallback", 0) + 1
            )

        if classification == "framework":
            framework_count += 1
        elif classification == "adopter":
            adopter_count += 1
        else:
            unclassified_count += 1

    cost = _estimate_regen_cost(len(metadata_by_chunk))
    return {
        "name": coll["name"],
        "id": coll["id"],
        "vector_count": len(metadata_by_chunk),
        "embedding_dimension_from_collections_table": coll["dimension"],
        "metadata_keys_observed": sorted(metadata_keys_observed),
        "source_type_distribution": source_types,
        "framework_chunk_count": framework_count,
        "adopter_chunk_count": adopter_count,
        "unclassified_chunk_count": unclassified_count,
        "classification_basis_counts": classification_basis_counts,
        "exact_count_basis": "full_metadata_pivot_via_direct_sqlite",
        "estimated_walltime_seconds": cost["estimated_walltime_seconds"],
        "estimated_token_cost": cost["estimated_token_cost"],
    }


def _emit_json(
    chroma_path: Path,
    collections: list[dict[str, Any]],
    no_mutation_proof: dict[str, Any],
    warnings: list[str],
    output_path: Path,
) -> None:
    """Emit chromadb-regen-plan.json."""
    total_chunks = sum(c["vector_count"] for c in collections)
    payload = {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_chromadb_path": chroma_path.as_posix(),
        "source_chromadb_exists": chroma_path.exists(),
        "collections": collections,
        "regen_plan": {
            "adopter_target_path": "applications/Agent_Red/.groundtruth-chroma",
            "framework_target_path": ".groundtruth-chroma",
            "total_chunks": total_chunks,
            "total_estimated_walltime_seconds": sum(c["estimated_walltime_seconds"] for c in collections),
            "total_estimated_token_cost": sum(c["estimated_token_cost"] for c in collections),
        },
        "no_chromadb_mutation_proof": no_mutation_proof,
        "warnings": warnings,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _emit_preview(
    collections: list[dict[str, Any]],
    no_mutation_proof: dict[str, Any],
    output_path: Path,
) -> None:
    """Emit chromadb-regen-preview.md."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# ChromaDB Regeneration Plan\n",
        "\n",
        f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n",
        "Source: GTKB-ISOLATION-016 Phase 8 rehearsal `_chromadb_regen.py` (Slice 10).\n",
        "\n",
        "## Summary\n",
        "\n",
        f"- Collections: {len(collections)}\n",
        f"- Total vectors: {sum(c['vector_count'] for c in collections)}\n",
        f"- Total estimated walltime: {sum(c['estimated_walltime_seconds'] for c in collections)} s\n",
        f"- Total estimated token cost: {sum(c['estimated_token_cost'] for c in collections)}\n",
        f"- Byte-stable safety: all_unchanged = {no_mutation_proof.get('all_unchanged')}\n",
        "\n",
        "## Per-Collection Plan\n",
        "\n",
    ]
    for coll in collections:
        lines.append(f"### `{coll['name']}` (UUID `{coll['id']}`)\n\n")
        lines.append(f"- Total chunks: {coll['vector_count']}\n")
        lines.append(f"- Dimension: {coll['embedding_dimension_from_collections_table']}\n")
        lines.append(f"- Framework: {coll['framework_chunk_count']}\n")
        lines.append(f"- Adopter: {coll['adopter_chunk_count']}\n")
        lines.append(f"- Unclassified: {coll['unclassified_chunk_count']}\n")
        lines.append(f"- Classification basis distribution: {coll['classification_basis_counts']}\n")
        lines.append(f"- Estimated walltime: {coll['estimated_walltime_seconds']} s\n")
        lines.append(f"- Estimated tokens: {coll['estimated_token_cost']}\n")
        lines.append("\n")
    output_path.write_text("".join(lines), encoding="utf-8")


# ---- Entry point ------------------------------------------------------


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    chroma_path: Path | None = None,
    partition_manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Wave 2 Stage C lane. Per common contract Wave 2 -003 §4.1.

    ``chroma_path`` overrides ``LEGACY_ROOT/.groundtruth-chroma`` for fixtures.
    ``partition_manifest_path`` overrides Slice 8 cross-reference path.
    """
    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    chroma_root = chroma_path if chroma_path is not None else (LEGACY_ROOT / ".groundtruth-chroma")
    lane_dir = output_dir / "chromadb_regen"
    lane_dir.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []
    output_files: list[Path] = []

    if not chroma_root.exists():
        # Empty plan when ChromaDB store is absent (per proposal §3 step 1).
        no_mutation_proof = {
            "chroma_files_sha256_before": {},
            "chroma_files_sha256_after": {},
            "all_unchanged": True,
        }
        json_path = lane_dir / "chromadb-regen-plan.json"
        _emit_json(chroma_root, [], no_mutation_proof, ["chromadb_store_absent"], json_path)
        preview_path = lane_dir / "chromadb-regen-preview.md"
        _emit_preview([], no_mutation_proof, preview_path)
        return emit_result(
            lane_dir,
            {
                "status": "ok",
                "output_files": [str(json_path), str(preview_path)],
                "metrics": {"collections": 0, "vector_count": 0},
                "warnings": ["chromadb_store_absent"],
            },
        )

    # Capture before-hash (byte-stable safety).
    before_hashes = _hash_chroma_files(chroma_root)

    membase_manifest = _load_membase_partition_manifest(
        partition_manifest_path.parent if partition_manifest_path is not None else output_dir
    )

    try:
        with _open_chroma_readonly(chroma_root) as conn:
            collections_meta = _read_collections(conn)
            collections: list[dict[str, Any]] = []
            for coll in collections_meta:
                metadata_by_chunk = _pivot_metadata_per_chunk(conn, coll["id"])
                summary = _build_collection_summary(coll, metadata_by_chunk, membase_manifest)
                collections.append(summary)
    except sqlite3.Error as exc:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"chroma_open_failed: {exc}"],
            },
        )

    # Capture after-hash + verify byte-stable.
    after_hashes = _hash_chroma_files(chroma_root)
    all_unchanged = before_hashes == after_hashes
    no_mutation_proof = {
        "chroma_files_sha256_before": before_hashes,
        "chroma_files_sha256_after": after_hashes,
        "all_unchanged": all_unchanged,
    }
    if not all_unchanged:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": ["chromadb_byte_stable_check_failed"],
                "no_chromadb_mutation_proof": no_mutation_proof,
            },
        )

    json_path = lane_dir / "chromadb-regen-plan.json"
    preview_path = lane_dir / "chromadb-regen-preview.md"
    _emit_json(chroma_root, collections, no_mutation_proof, warnings, json_path)
    output_files.append(json_path)
    _emit_preview(collections, no_mutation_proof, preview_path)
    output_files.append(preview_path)

    metrics = {
        "collections": len(collections),
        "vector_count": sum(c["vector_count"] for c in collections),
        "framework_chunk_count": sum(c["framework_chunk_count"] for c in collections),
        "adopter_chunk_count": sum(c["adopter_chunk_count"] for c in collections),
        "unclassified_chunk_count": sum(c["unclassified_chunk_count"] for c in collections),
    }
    return emit_result(
        lane_dir,
        {
            "status": "ok",
            "output_files": [str(p) for p in output_files],
            "metrics": metrics,
            "warnings": warnings,
        },
    )
