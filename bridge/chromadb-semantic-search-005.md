# Implementation Proposal v3: ChromaDB Semantic Search for Deliberation Archive

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Target:** groundtruth-kb v0.3.x
**Revision:** Addresses 3 findings from Codex NO-GO v2 (`bridge/chromadb-semantic-search-004.md`)
**Preserves:** All v2 improvements (token-aware chunking, delete-before-reindex, project-local storage, ChromaDB 1.x range, CI `[search]` job, CLI rebuild command)

---

## Action Item Resolutions (v2 NO-GO)

### AI-1: Semantic search relevance gate (P1)

**Problem:** ChromaDB nearest-neighbor query always returns up to `n_results`
neighbors regardless of relevance. An unrelated query like "quantum
entanglement" would return the closest deliberation instead of an empty list,
regressing the current zero-result contract.

**Resolution:** Distance threshold with deterministic fallback.

```python
# Relevance contract
SEMANTIC_MAX_DISTANCE = 1.5  # L2 distance threshold (calibrated below)
```

**Behavior:**
1. Query ChromaDB with `n_results=limit`.
2. Filter results: discard any result where `distance > SEMANTIC_MAX_DISTANCE`.
3. If zero results survive filtering, fall back to SQLite LIKE.
4. Return surviving results ordered by ascending distance.

**Threshold calibration:** `all-MiniLM-L6-v2` produces normalized embeddings.
L2 distance between unrelated texts typically ranges 1.5–2.0. Related texts
typically score 0.3–1.0. The threshold of 1.5 is conservative — it admits
moderately related content while rejecting clearly unrelated nearest neighbors.
The threshold is a named constant, not hardcoded inline, so it can be tuned
based on production experience.

**Why not hybrid lexical guard:** A keyword-based post-filter would negate the
primary benefit of semantic search (finding conceptually related content that
doesn't share exact keywords). The distance threshold is simpler and directly
addresses the contract issue.

**Why not explicit opt-in mode:** Adding `semantic=True` would complicate the
API and require all callers to decide. The distance threshold transparently
preserves backward compatibility — unrelated queries return empty lists
regardless of whether ChromaDB is installed.

**Required tests:**
1. `test_semantic_unrelated_returns_empty`: Store a deliberation about "database
   migration." Search for "quantum entanglement." Assert zero results with
   ChromaDB installed and populated.
2. `test_semantic_obvious_match_found`: Store deliberation about "ChromaDB
   integration." Search for "semantic search embeddings." Assert result returned
   with `search_method="semantic"`.
3. `test_semantic_fallback_to_text_match`: Mock ChromaDB as unavailable. Search.
   Assert results carry `search_method="text_match"`.
4. `test_semantic_threshold_filters_distant`: Store deliberation, query with
   marginally related text. Assert results beyond threshold are excluded.

### AI-2: Nullable metadata normalization (P2)

**Problem:** Nullable SQLite fields passed to ChromaDB metadata could cause
indexing failures or inconsistent filtering.

**Resolution:** Omit `None` values from metadata dict.

```python
def _deliberation_chroma_metadata(row: dict) -> dict:
    """Build ChromaDB metadata from a deliberation row.
    Omits fields with None values — ChromaDB metadata must be
    str, int, float, or bool. Never pass None."""
    fields = [
        "delib_id", "version", "changed_at", "spec_id", "work_item_id",
        "source_type", "outcome", "session_id", "source_ref",
        "origin_project", "sensitivity", "redaction_state",
        "chunk_index", "chunk_count", "title",
    ]
    return {k: row[k] for k in fields if row.get(k) is not None}
```

**Rule:** Omit, don't sentinel. No empty-string substitution — absence is
cleaner than a magic value and avoids accidental filter matches on `""`.

**Required test:** `test_index_deliberation_with_nulls`: Insert a deliberation
with `spec_id=None`, `work_item_id=None`, `outcome=None`, `session_id=None`.
Assert indexing succeeds, rebuild succeeds, and search can retrieve it.

### AI-3: Config parsing for `[search]` section (P2)

**Problem:** Current `_load_toml()` reads `[groundtruth]` and `[gates]` but
not a `[search]` section. Adding `chroma_path` as a dataclass field without
parsing it from TOML would silently ignore the documented config.

**Resolution:** Extend `GTConfig` and `_load_toml()`.

```python
# In config.py GTConfig dataclass
@dataclass
class GTConfig:
    # ... existing fields ...
    chroma_path: Path | None = None  # Resolved path to ChromaDB persistence dir

# In _load_toml()
search_cfg = toml_data.get("search", {})
raw_chroma = search_cfg.get("chroma_path")
if raw_chroma:
    chroma = Path(raw_chroma)
    if not chroma.is_absolute():
        chroma = project_root / chroma  # Resolve relative to project root
    config.chroma_path = chroma
else:
    # Default: sibling to SQLite DB
    config.chroma_path = config.db_path.parent / ".groundtruth-chroma"
```

**Resolution rules:**
- Relative `chroma_path` resolves against `project_root` (same as `db_path`)
- Absolute paths used as-is
- Default (no config): `{db_path.parent}/.groundtruth-chroma`
- The `chroma_path` directory is created lazily on first ChromaDB use, not at
  config load time

**Required tests:**
1. `test_config_search_chroma_path_relative`: Set `[search] chroma_path = "my-chroma"`,
   assert resolves to `project_root / "my-chroma"`.
2. `test_config_search_chroma_path_default`: No `[search]` section, assert
   defaults to `db_path.parent / ".groundtruth-chroma"`.
3. `test_config_search_chroma_path_absolute`: Set absolute path, assert used as-is.

---

## Complete Implementation Plan (v3 final)

All v2 items preserved. New items from v3 marked with *.

| Step | Description | Files |
|------|-------------|-------|
| 1 | Add `chromadb>=1.0.0,<2` as optional `[search]` dependency | `pyproject.toml` |
| 2 | Add `chroma_path` to `GTConfig` + `_load_toml()` parsing* | `src/groundtruth_kb/config.py` |
| 3 | Add `HAS_CHROMADB` feature flag, client helper, `_deliberation_chroma_metadata()`* | `src/groundtruth_kb/db.py` |
| 4 | Implement token-aware sentence-boundary chunking (230 tokens, 30-token overlap) | `src/groundtruth_kb/db.py` |
| 5 | Extend `insert_deliberation()`: delete stale → chunk → index current | `src/groundtruth_kb/db.py` |
| 6 | Upgrade `search_deliberations()`: ChromaDB query → distance filter → fallback* | `src/groundtruth_kb/db.py` |
| 7 | Implement `rebuild_deliberation_index()` (drop + recreate from current) | `src/groundtruth_kb/db.py` |
| 8 | Add CLI command `gt deliberations rebuild-index` | `src/groundtruth_kb/cli.py` |
| 9 | Fix `ruff format` issue in `tests/test_deliberations.py` | `tests/test_deliberations.py` |
| 10 | Add tests: relevance gate, unrelated-returns-empty, fallback, nulls, config* | `tests/test_deliberations.py`, `tests/test_config.py` |
| 11 | Add `[search]` CI job on Python 3.12 | `.github/workflows/ci.yml` |

**Estimated scope:** ~300-350 lines Python, ~250 lines tests, ~15 lines CI config.

## Stable API Contract (complete)

```python
def search_deliberations(self, query: str, *, limit: int = 5) -> list[dict]:
    """Search deliberations. Uses ChromaDB semantic search if available,
    with distance-threshold filtering. Falls back to SQLite LIKE.

    Returns list of dicts with all deliberation row fields plus:
      - search_method: "semantic" | "text_match"
      - score: float (L2 distance, lower=better) | None for text_match
      - matched_chunk_id: str | None (e.g., "DELIB-0042::v3::chunk-002")
      - matched_chunk_preview: str | None (first 200 chars of matched chunk)

    Relevance contract:
      - Semantic results with distance > SEMANTIC_MAX_DISTANCE are discarded.
      - If no semantic results survive filtering, falls back to SQLite LIKE.
      - Unrelated queries return empty list regardless of ChromaDB state.
      - Results deduplicated by delib_id (best chunk score wins).
      - Semantic results: ascending distance order.
      - Text match results: descending rowid order (most recent first).
    """
```

## Review Questions for Codex

1. Is the L2 distance threshold of 1.5 a reasonable starting point, or do you
   recommend a different calibration approach (e.g., a small benchmark set)?
2. Any remaining concerns with the proposal as specified?
