# Implementation Proposal v4: ChromaDB Semantic Search for Deliberation Archive

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Target:** groundtruth-kb v0.3.x
**Revision:** Fixes metadata mapping from Codex NO-GO v3 (`bridge/chromadb-semantic-search-006.md`)
**Preserves:** All v2+v3 improvements

---

## Changes from v3

### AI-1: Metadata builder maps `row["id"]` to `metadata["delib_id"]` (P1)

**Problem:** v3's `_deliberation_chroma_metadata()` listed `"delib_id"` in the
fields list, but the SQLite schema stores the deliberation identifier as `id`.
Since `row.get("delib_id")` returns `None`, it was silently omitted, breaking
the delete-before-reindex contract which filters by `metadata.delib_id`.

**Resolution:** Explicit mapping with required/optional field separation per
Codex's recommended code:

```python
def _deliberation_chroma_metadata(
    row: dict, *, chunk_index: int, chunk_count: int
) -> dict:
    """Build ChromaDB metadata from a deliberation row.
    Maps SQLite 'id' to Chroma 'delib_id'. Omits optional fields with None values."""
    metadata = {
        "delib_id": row["id"],          # Required: maps SQLite id -> Chroma delib_id
        "version": row["version"],       # Required: for audit/stale detection
        "changed_at": row["changed_at"], # Required: temporal context
        "source_type": row["source_type"],  # Required: always present
        "sensitivity": row["sensitivity"],  # Required: has DEFAULT 'normal'
        "redaction_state": row["redaction_state"],  # Required: has DEFAULT 'clean'
        "chunk_index": chunk_index,      # Required: passed by caller
        "chunk_count": chunk_count,      # Required: passed by caller
        "title": row["title"],           # Required: always present
    }
    optional_fields = [
        "spec_id",
        "work_item_id",
        "outcome",
        "session_id",
        "source_ref",
        "origin_project",
        "origin_repo",
    ]
    metadata.update({k: row[k] for k in optional_fields if row.get(k) is not None})
    return metadata
```

**Required tests:**
1. `test_metadata_contains_delib_id`: Index a deliberation, inspect ChromaDB
   metadata, assert `metadata["delib_id"] == row["id"]`.
2. `test_stale_deletion_by_delib_id`: Insert DELIB-0001 v1 with text "alpha."
   Update to v2 with text "beta." Assert search for "alpha" returns zero
   results (proves delete-before-reindex used `delib_id` filter correctly).
3. `test_stale_chunks_removed_on_revision`: Insert long deliberation (5 chunks)
   as v1. Update to short deliberation (2 chunks) as v2. Assert ChromaDB
   contains exactly 2 entries for that `delib_id` (old chunks 3-5 gone).

### AI-2: Threshold calibration fixture (P2)

**Resolution:** Add deterministic calibration test using the pinned embedding
function:

```python
def test_threshold_calibration():
    """Prove SEMANTIC_MAX_DISTANCE separates known positive/negative pairs."""
    # Positive pairs (should score below threshold)
    positives = [
        ("database migration strategy", "migrating SQL tables to new schema"),
        ("ChromaDB semantic search integration", "embedding-based vector retrieval"),
    ]
    # Negative pairs (should score above threshold)
    negatives = [
        ("database migration strategy", "chocolate cake recipe"),
        ("ChromaDB semantic search integration", "quantum entanglement theory"),
    ]
    for query, doc in positives:
        # Index doc, search query, assert distance < SEMANTIC_MAX_DISTANCE
    for query, doc in negatives:
        # Index doc, search query, assert no results (filtered by threshold)
```

This validates the 1.5 threshold for the `all-MiniLM-L6-v2` model. If the
model or distance metric changes, this test fails loudly.

---

## Complete Specification (unchanged from v3 except metadata builder)

All prior accepted improvements are preserved:

- **Dependency:** `chromadb>=1.0.0,<2` as `[search]` optional extra
- **Chunking:** Token-aware, 230 tokens max, 30-token overlap, sentence boundaries
- **Sync:** Delete-before-reindex on every `insert_deliberation()` using
  `metadata.delib_id` filter (now correctly mapped from `row["id"]`)
- **Storage:** Project-local `{db_path.parent}/.groundtruth-chroma`, configurable
  via `[search].chroma_path` in `groundtruth.toml`
- **Config:** `GTConfig.chroma_path` parsed from `[search]` TOML section,
  relative paths resolve against project root
- **Search:** ChromaDB query → L2 distance filter (threshold 1.5) → discard
  distant results → fall back to SQLite LIKE if none survive
- **Result contract:** `search_method`, `score`, `matched_chunk_id`,
  `matched_chunk_preview` fields; deduplicated by `delib_id`
- **Metadata normalization:** Required fields always present, optional fields
  omitted when `None`
- **Chroma ID scheme:** `{delib_id}::v{version}::chunk-{N}`
- **CLI:** `gt deliberations rebuild-index`
- **CI:** `[search]` job on Python 3.12
- **Ruff format fix:** Pre-existing `tests/test_deliberations.py` formatting

## Implementation Plan (unchanged)

| Step | Description | Files |
|------|-------------|-------|
| 1 | Add `chromadb>=1.0.0,<2` as optional `[search]` dependency | `pyproject.toml` |
| 2 | Add `chroma_path` to `GTConfig` + `_load_toml()` parsing | `src/groundtruth_kb/config.py` |
| 3 | Add `HAS_CHROMADB` feature flag, client helper, `_deliberation_chroma_metadata()` | `src/groundtruth_kb/db.py` |
| 4 | Implement token-aware sentence-boundary chunking | `src/groundtruth_kb/db.py` |
| 5 | Extend `insert_deliberation()`: delete stale by `delib_id` → chunk → index | `src/groundtruth_kb/db.py` |
| 6 | Upgrade `search_deliberations()`: ChromaDB → distance filter → fallback | `src/groundtruth_kb/db.py` |
| 7 | Implement `rebuild_deliberation_index()` (drop + recreate from current) | `src/groundtruth_kb/db.py` |
| 8 | Add CLI command `gt deliberations rebuild-index` | `src/groundtruth_kb/cli.py` |
| 9 | Fix `ruff format` in `tests/test_deliberations.py` | `tests/test_deliberations.py` |
| 10 | Add all tests (metadata, stale deletion, calibration, relevance, fallback, nulls, config) | `tests/test_deliberations.py`, `tests/test_config.py` |
| 11 | Add `[search]` CI job on Python 3.12 | `.github/workflows/ci.yml` |
