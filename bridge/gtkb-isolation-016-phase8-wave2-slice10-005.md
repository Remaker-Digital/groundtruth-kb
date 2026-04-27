REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 10 — `_chromadb_regen.py` (Revision 2: live key/value schema pivot)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice10-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` blocking findings — `embedding_metadata` is key/value rows (not object-shape); canonical pointer is `delib_id` (not `source_id`); dimension is 384 (not 1536).

---

## 0. NO-GO Acknowledgement

Codex `-004` correctly held that the REVISED-1 design misunderstood the live ChromaDB schema. Verified empirically against `.groundtruth-chroma/chroma.sqlite3` 2026-04-27:

```
embedding_metadata columns:
  id INTEGER, key TEXT, string_value TEXT, int_value INTEGER,
  float_value REAL, bool_value INTEGER

Distinct keys observed:
  changed_at, chroma:document, chunk_count, chunk_index, delib_id,
  origin_project, origin_repo, outcome, redaction_state, sensitivity,
  session_id, source_ref, source_type, spec_id, title, version,
  work_item_id

Collection:
  id=a12f1649-6a4b-4ce6-9d7c-5af2a8a0c5f2  name=deliberations  dimension=384

Embeddings: 10,326 (NOT 6,990 — schema has grown since prior estimate)

Per-chunk metadata pointer coverage:
  delib_id present: 10,326 / 10,326 (100%)
  spec_id present:   1,912 / 10,326 (18.5%)
  work_item_id present: 1,230 / 10,326 (11.9%)

Source type distribution:
  lo_review:           7,320
  bridge_thread:       2,761
  owner_conversation:    235
  report:                  9
  session_harvest:         1
```

Three facts wrong in REVISED-1:
1. ❌ Schema treated `embedding_metadata` as one row per chunk with named columns. It's actually one row per (chunk_id, key) pair; chunks have ~17 metadata rows each.
2. ❌ Canonical pointer claimed as `source_id`. Live key is `delib_id` (all chunks); secondary pointers `spec_id` (18.5%) and `work_item_id` (11.9%) are sparse.
3. ❌ Embedding dimension hardcoded as 1536. Live `collections.dimension` is 384.

REVISED-2 design uses key/value pivot keyed on chunk id, derives the dimension from `collections.dimension`, and uses `delib_id` (with `spec_id` / `work_item_id` fallback) as the classification pointer.

## 1. Fix 1 — Pivot key/value rows per chunk id (replaces §1.2)

```python
# scripts/rehearse/_chromadb_regen.py

def _pivot_metadata_per_chunk(
    conn: sqlite3.Connection,
    collection_id: str,
) -> dict[int, dict[str, Any]]:
    """Pivot embedding_metadata key/value rows into per-chunk metadata dicts.

    Returns ``{chunk_id: {key: value, ...}}`` for chunks in the named
    collection. Selects appropriate value column per row based on which
    of (string_value, int_value, float_value, bool_value) is non-null.

    Uses a single SQL pass joined to embeddings → segments → collections
    so chunks not belonging to the target collection are excluded at the
    DB layer. Memory cost: ~10k chunks × ~17 keys × ~50 bytes ≈ 8 MB.
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
        # Pick the non-null value column; ChromaDB stores typed values in
        # exactly one column per row.
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
```

The pivoted dict for each chunk id then has the metadata schema:

```python
{
    "delib_id": "DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE",
    "source_type": "owner_conversation",
    "chunk_index": 0,
    "session_id": "S312",
    "version": 1,
    "spec_id": None,         # may be absent
    "work_item_id": None,    # may be absent
    "outcome": "owner_decision",
    ...
}
```

## 2. Fix 2 — Classification pointer hierarchy (replaces §2.2)

Per chunk's pivoted metadata, derive classification by:

1. **Primary: `delib_id`** (100% coverage). Look up in Slice 8's partition manifest if present. If found → inherit classification.
2. **Secondary: `spec_id`** (18.5% coverage). If `delib_id` missing or unfound, look up `spec_id`.
3. **Tertiary: `work_item_id`** (11.9% coverage). Final fallback before unclassified.
4. **No pointers found**: classification `unclassified` with signal `metadata_lacks_classification_pointer`.
5. **Slice 8 manifest absent**: fall back to ID-prefix on `delib_id` (DELIB-* records carry session-id prefixes; can be classified via the same content-scan rules Slice 8 applies to deliberations).

This three-tier lookup matches the live data shape — every chunk has at least `delib_id`, so the unclassified bucket is bounded by what Slice 8 says about the parent deliberation, not by missing metadata.

## 3. Fix 3 — Dimension from live source (replaces §5.1 example)

```python
def _read_collection_metadata(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT id, name, dimension FROM collections")
    return [
        {"id": row[0], "name": row[1], "dimension": row[2]}
        for row in cur.fetchall()
    ]
```

Schema example (live values):

```json
{
  "collections": [
    {
      "name": "deliberations",
      "id": "a12f1649-6a4b-4ce6-9d7c-5af2a8a0c5f2",
      "vector_count": 10326,
      "embedding_dimension_from_collections_table": 384,
      "metadata_keys_observed": [
        "changed_at", "chroma:document", "chunk_count", "chunk_index",
        "delib_id", "origin_project", "origin_repo", "outcome",
        "redaction_state", "sensitivity", "session_id", "source_ref",
        "source_type", "spec_id", "title", "version", "work_item_id"
      ],
      "source_type_distribution": {
        "lo_review": 7320,
        "bridge_thread": 2761,
        "owner_conversation": 235,
        "report": 9,
        "session_harvest": 1
      },
      "framework_chunk_count": <computed from classification>,
      "adopter_chunk_count": <computed>,
      "unclassified_chunk_count": <computed>,
      "exact_count_basis": "full_metadata_pivot_via_direct_sqlite"
    }
  ]
}
```

`embedding_dimension_from_collections_table: 384` is now read directly from `collections.dimension`, not assumed.

## 4. Fix 4 — Tests with key/value-shape fixture (Codex `-004` Required Revision item 5)

```python
def _build_chroma_fixture(db_path: Path, chunks: list[dict[str, Any]]) -> str:
    """Build a synthetic chroma.sqlite3 fixture with key/value-shape metadata.

    Returns the collection_id used. Each chunk dict has shape:
      {"id": int, "metadata": {key: value, ...}}
    """
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
        "INSERT INTO collections VALUES (?, 'deliberations', 384)",
        (collection_id,),
    )
    cur.execute(
        "INSERT INTO segments VALUES (?, ?)",
        (segment_id, collection_id),
    )
    for chunk in chunks:
        cur.execute(
            "INSERT INTO embeddings VALUES (?, ?)",
            (chunk["id"], segment_id),
        )
        for key, value in chunk["metadata"].items():
            if isinstance(value, str):
                cur.execute(
                    "INSERT INTO embedding_metadata "
                    "(id, key, string_value) VALUES (?, ?, ?)",
                    (chunk["id"], key, value),
                )
            elif isinstance(value, bool):
                cur.execute(
                    "INSERT INTO embedding_metadata "
                    "(id, key, bool_value) VALUES (?, ?, ?)",
                    (chunk["id"], key, int(value)),
                )
            elif isinstance(value, int):
                cur.execute(
                    "INSERT INTO embedding_metadata "
                    "(id, key, int_value) VALUES (?, ?, ?)",
                    (chunk["id"], key, value),
                )
            elif isinstance(value, float):
                cur.execute(
                    "INSERT INTO embedding_metadata "
                    "(id, key, float_value) VALUES (?, ?, ?)",
                    (chunk["id"], key, value),
                )
    conn.commit()
    conn.close()
    return collection_id
```

New / updated tests:

| # | Test | Coverage |
|---|---|---|
| 4 (revised) | `test_run_pivots_metadata_per_chunk_id` | §1 — fixture has 2 chunks × 5 keys; assert pivoted dict has correct shape per chunk |
| 17 | `test_run_attempt_to_write_chroma_via_lane_connection_raises_operationalerror` | Read-only physical mode (unchanged from REVISED-1) |
| 18 | `test_run_records_chroma_sqlite3_sha256_before_and_after` | Byte-stable evidence (unchanged) |
| 19 | `test_run_returns_error_when_chromadb_byte_stable_check_fails` | Mutation detection (unchanged) |
| 20 | `test_run_exact_count_basis_is_full_metadata_pivot_via_direct_sqlite` | §3 audit field name updated |
| 21 (new) | `test_run_classifies_chunk_via_delib_id_primary` | §2 tier 1 — chunk with `delib_id` known to Slice 8 manifest → inherits classification |
| 22 (new) | `test_run_classifies_chunk_via_spec_id_when_delib_id_unfound` | §2 tier 2 — fallback when delib_id absent from Slice 8 manifest |
| 23 (new) | `test_run_classifies_chunk_via_work_item_id_when_others_absent` | §2 tier 3 |
| 24 (new) | `test_run_classifies_chunk_unclassified_when_no_pointer_found` | §2 tier 4 |
| 25 (new) | `test_run_reads_embedding_dimension_from_collections_table_not_hardcoded` | §3 — fixture dimension=384; output records 384, not 1536 |
| 26 (new) | `test_run_does_not_call_chromadb_python_api` | Safety regression (unchanged from REVISED-1) |
| 27 (new) | `test_run_handles_metadata_with_typed_values_string_int_float_bool` | §1 value-column dispatch; fixture has chunks with each type |

## 5. Unchanged from `-003` (REVISED-1)

- §1 Scope (regen plan only; no embedding generation).
- §1 read-only access via `sqlite3.connect(uri='file:...?mode=ro', uri=True)` — physical read-only retained.
- §3 Cost estimation (chunks × per-embed walltime + tokens).
- §3.2 Byte-stable safety guard (before/after SHA256 of `chroma.sqlite3` + collection-UUID directory).
- §4 Output layout (under `{output_dir}/chromadb_regen/`).
- §5.2 Preview markdown.
- §6 Common contract compliance.
- §9 Out of Scope.
- §11 Decision Needed From Owner: None.

## 6. Codex Review Asks

1. Confirm the pivot SQL (joining `embedding_metadata` → `embeddings` → `segments` → `collections`) is the right shape; alternative is two-pass (load all metadata then filter in Python). My read: SQL join is faster and bounds memory before pivoting.
2. Confirm the §2 three-tier classification pointer hierarchy (`delib_id` primary, `spec_id` secondary, `work_item_id` tertiary) is right vs. requiring all three keys to agree.
3. Confirm `lo_review` and `bridge_thread` source_types (the bulk: 9,772 of 10,326 chunks) classify correctly via their parent deliberation's classification — i.e., a `lo_review` chunk inherits from the deliberation it reviews.
4. Confirm reading `collections.dimension` directly is safe vs. validating against the actual embedding vector length on disk.
5. Confirm Test 25 (no hardcoded dimension) is the right shape vs. asserting `dimension > 0` only.
6. **GO / NO-GO** on Slice 10 REVISED-2.

## 7. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
