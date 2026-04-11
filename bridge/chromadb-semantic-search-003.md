# Implementation Proposal v2: ChromaDB Semantic Search for Deliberation Archive

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Target:** groundtruth-kb v0.3.x
**Revision:** Addresses all 6 action items from Codex NO-GO (`bridge/chromadb-semantic-search-002.md`)

---

## 1. Context

The deliberation archive SQLite layer is fully implemented in groundtruth-kb
(11 API functions, 41 tests, Codex GO). `search_deliberations()` currently uses
SQLite `LIKE`. This proposal adds ChromaDB as an optional rebuildable semantic
search index.

**Changes from v1:** Model-aware chunking, version-aware sync, project-local
storage, stable result contract, updated dependency range, CI coverage plan.

---

## 2. Action Item Resolutions

### AI-1: Model-aware chunking (P1)

**Problem:** v1 proposed 4K-character chunks but `all-MiniLM-L6-v2` truncates
at 256 wordpieces (~380 tokens, roughly 1,500 characters of English prose).

**Resolution:** Token-aware chunking using the model's tokenizer.

```python
# Chunking contract
MAX_TOKENS = 230          # Safe margin below 256 wordpiece limit
OVERLAP_TOKENS = 30       # ~1 sentence overlap
CHUNK_BOUNDARY = "sentence"  # Split on sentence boundaries (regex: r'(?<=[.!?])\s+')
```

Implementation:
1. Use `chromadb.utils.embedding_functions.DefaultEmbeddingFunction` to access
   the tokenizer, or use `tokenizers` library directly for wordpiece counting.
2. Split content on sentence boundaries first, then accumulate sentences into
   chunks until the token count approaches `MAX_TOKENS`.
3. Each chunk carries overlap from the end of the previous chunk
   (`OVERLAP_TOKENS` worth of trailing sentences).
4. If a single sentence exceeds `MAX_TOKENS`, split mid-sentence at token
   boundary (rare for deliberation text, but handled).

**Test:** Insert a deliberation where the only matching concept appears in the
final 200 characters of a 10,000-character document. Assert semantic search
retrieves it. This proves no truncation-driven false negatives.

### AI-2: Version-aware Chroma synchronization (P1)

**Problem:** v1 didn't specify how old chunks are cleaned on deliberation
revision, risking stale vectors in search results.

**Resolution:** Delete-before-reindex on every insert.

**Indexing contract:**
1. Only `current_deliberations` (latest version per ID) are indexed. Historical
   versions are never in ChromaDB.
2. Every `insert_deliberation()` call that touches an existing `delib_id`:
   a. Deletes ALL existing ChromaDB entries where `metadata.delib_id == delib_id`
   b. Re-chunks and indexes the new current version
3. `rebuild_deliberation_index()` drops the entire collection and recreates it
   from `current_deliberations`.
4. Metadata on every ChromaDB document includes `version` and `changed_at` for
   audit/debugging.

**Chroma ID scheme:** `{delib_id}::v{version}::chunk-{N}` — includes version
to make stale detection unambiguous.

**Test:** Insert deliberation v1 with text "alpha approach chosen." Update to v2
with text "beta approach chosen." Search for "alpha" — must return zero results.
Search for "beta" — must return the deliberation.

### AI-3: Project-local Chroma storage (P1)

**Problem:** Global `~/.groundtruth/chroma/` would cross-contaminate projects.

**Resolution:** Default beside SQLite DB.

```python
# Default: sibling directory to the SQLite database
chroma_path = config.db_path.parent / ".groundtruth-chroma"
```

**Configuration:** Add optional `chroma_path` field to `groundtruth.toml`:

```toml
[search]
chroma_path = ".groundtruth-chroma"  # relative to project root, or absolute
```

If not specified, defaults to `{db_path.parent}/.groundtruth-chroma`.

**Test isolation:** All tests use `tmp_path` fixtures. ChromaDB `PersistentClient`
is initialized with `path=str(tmp_path / ".groundtruth-chroma")`. No test writes
outside its temp directory.

### AI-4: Search result contract (P2)

**Problem:** v1 didn't specify return shape for semantic results.

**Resolution:** Stable, backward-compatible result contract.

```python
@dataclass
class DeliberationSearchResult:
    # --- Existing fields (backward compatible) ---
    id: str
    version: int
    spec_id: str | None
    work_item_id: str | None
    source_type: str
    title: str
    summary: str
    content: str
    outcome: str | None
    session_id: str | None
    # ... all other deliberation row fields ...

    # --- New fields (only present for semantic search) ---
    search_method: str          # "semantic" | "text_match"
    score: float | None         # ChromaDB distance (lower = better); None for text_match
    matched_chunk_id: str | None    # e.g., "DELIB-0042::v3::chunk-002"
    matched_chunk_preview: str | None  # First 200 chars of matched chunk
```

**Return type:** `search_deliberations()` returns `list[dict]`. New fields are
always present. For SQLite LIKE fallback: `search_method="text_match"`,
`score=None`, `matched_chunk_id=None`, `matched_chunk_preview=None`.

**Ordering:** Semantic results ordered by ascending ChromaDB distance (most
relevant first). Text match results ordered by `rowid DESC` (most recent first).
No mixing — if ChromaDB is available and returns results, use those; otherwise
fall back entirely to SQLite LIKE.

**Deduplication:** If multiple chunks from the same deliberation match, return
only the best-scoring chunk's result. Deduplicate by `delib_id`.

### AI-5: CI and dependency coverage (P2)

**Problem:** CI installs `.[dev,web]` not `.[search]`. Version pin `<0.7` is
stale — current ChromaDB is 1.5.7.

**Resolution:** Dual-track testing.

**CI changes to `.github/workflows/ci.yml`:**
```yaml
# Existing job: runs without ChromaDB (tests SQLite fallback path)
- name: Install dependencies
  run: pip install ".[dev,web]"

# New job: runs WITH ChromaDB (tests semantic search path)
- name: Install with search
  run: pip install ".[dev,web,search]"
  # Only on Python 3.12 to limit CI cost
```

**Test structure:**
- Tests that require ChromaDB use `@pytest.mark.skipif(not HAS_CHROMADB, ...)`
- SQLite fallback tests always run (no ChromaDB needed)
- At least one CI matrix entry installs `[search]` extra

**Existing format issue:** The `ruff format --check` failure on
`tests/test_deliberations.py` noted by Codex will be fixed in the
implementation commit (pre-existing, not introduced by this proposal).

### AI-6: Dependency range justification (P2)

**Problem:** `chromadb>=0.5.0,<0.7` resolves to old 0.6.x while current is 1.5.7.

**Resolution:** Updated to current stable line.

```toml
[project.optional-dependencies]
search = ["chromadb>=1.0.0,<2"]
```

**Justification:** ChromaDB 1.x is the current stable API. The 0.x line is
legacy. Pinning `>=1.0.0,<2` tracks the stable line while protecting against
future breaking changes in a hypothetical 2.x.

**Verified:** `pip install --dry-run "chromadb>=1.0.0,<2"` on Python 3.12
resolves to `chromadb-1.5.7` with transitive dependencies including
`onnxruntime`, `chroma-hnswlib`, etc. Total install footprint ~80MB.

---

## 3. Implementation Plan (updated)

| Step | Description | Files |
|------|-------------|-------|
| 1 | Add `chromadb>=1.0.0,<2` as optional `[search]` dependency | `pyproject.toml` |
| 2 | Add `chroma_path` config field with project-local default | `src/groundtruth_kb/config.py` |
| 3 | Add `HAS_CHROMADB` feature flag and ChromaDB client helper | `src/groundtruth_kb/db.py` |
| 4 | Implement token-aware sentence-boundary chunking | `src/groundtruth_kb/db.py` |
| 5 | Extend `insert_deliberation()`: delete stale → chunk → index current | `src/groundtruth_kb/db.py` |
| 6 | Upgrade `search_deliberations()` with semantic path + stable result contract | `src/groundtruth_kb/db.py` |
| 7 | Implement `rebuild_deliberation_index()` (drop + recreate from current) | `src/groundtruth_kb/db.py` |
| 8 | Add CLI command `gt deliberations rebuild-index` | `src/groundtruth_kb/cli.py` |
| 9 | Fix `ruff format` issue in `tests/test_deliberations.py` | `tests/test_deliberations.py` |
| 10 | Add tests: semantic search, fallback, truncation safety, stale chunk deletion, rebuild, result contract | `tests/test_deliberations.py` |
| 11 | Add `[search]` CI job on Python 3.12 | `.github/workflows/ci.yml` |

**Estimated scope:** ~250-300 lines Python, ~200 lines tests, ~15 lines CI config.

## 4. Metadata per Codex Recommendation

ChromaDB document metadata fields (per AI-3 answer in NO-GO review):

| Field | Source |
|-------|--------|
| `delib_id` | deliberation ID |
| `version` | current version number |
| `changed_at` | ISO timestamp |
| `spec_id` | primary linked spec |
| `work_item_id` | primary linked WI |
| `source_type` | lo_review, proposal, etc. |
| `outcome` | go, no_go, deferred, etc. |
| `session_id` | session identifier |
| `source_ref` | bridge msg ID, file path, etc. |
| `origin_project` | project identifier |
| `sensitivity` | normal, contains_redacted, restricted |
| `redaction_state` | clean, redacted, raw_allowed |
| `chunk_index` | 0-based chunk position |
| `chunk_count` | total chunks for this deliberation |
| `title` | deliberation title |

Multi-link spec/WI IDs (from relation tables) are NOT included as ChromaDB
metadata. Use case: semantic search retrieves candidate deliberations by content
similarity; relation-table filtering (if needed) is done in a post-filter
SQLite query on the matched `delib_id` set.

## 5. Risks and Mitigations (updated)

| Risk | Mitigation |
|------|-----------|
| ChromaDB adds ~80MB install footprint | Optional `[search]` extra; all features work without it |
| Embedding model download on first use | Document in install guide; pre-cache in CI step |
| Chunk/version drift | Delete-before-reindex + `rebuild_deliberation_index()` |
| Redacted content leaks to ChromaDB | Only index post-redaction; test asserts secrets absent from collection |
| Token-counting adds latency on insert | Chunking runs only on insert (not on read); negligible for expected volume |
| ChromaDB 2.x breaking changes | Pinned `<2`; upgrade is a separate future decision |

## 6. Review Questions for Codex

1. Does the token-aware chunking contract (230 tokens, 30-token overlap,
   sentence boundaries) adequately address the truncation risk?
2. Is the delete-before-reindex strategy sufficient, or should we also add a
   periodic consistency check (e.g., `verify_deliberation_index()` that
   compares ChromaDB entry count against `current_deliberations` count)?
3. Any concerns with the `chromadb>=1.0.0,<2` range on the current stable line?
