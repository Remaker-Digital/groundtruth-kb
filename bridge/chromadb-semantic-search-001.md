# Implementation Proposal: ChromaDB Semantic Search for Deliberation Archive

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Target:** groundtruth-kb v0.3.x
**Scope:** Add ChromaDB as optional dependency and implement semantic search over deliberations

---

## 1. Context

The deliberation archive SQLite layer is fully implemented in groundtruth-kb
(11 API functions, 41 tests, Codex GO). The `search_deliberations()` function
currently uses SQLite `LIKE` for text matching. The original proposal
(`docs/proposals/DELIBERATION-ARCHIVE-PROPOSAL.md`) specified ChromaDB semantic
search as a companion index — this was deferred as "Session B" and never
completed.

## 2. What This Proposal Covers

1. Add `chromadb` as an optional dependency in `pyproject.toml`
2. Implement ChromaDB collection management (create, sync, rebuild)
3. Upgrade `search_deliberations()` to use ChromaDB embeddings with SQLite LIKE
   fallback when ChromaDB is unavailable
4. Add `rebuild_deliberation_index()` for rebuilding ChromaDB from SQLite
5. Tests for semantic search, fallback behavior, and index rebuild

## 3. Architecture

### 3.1 Dependency

```toml
[project.optional-dependencies]
search = ["chromadb>=0.5.0,<0.7"]
```

ChromaDB is **optional**. All existing functionality works without it. The
SQLite table remains the canonical source of truth. ChromaDB is a rebuildable
search index only.

### 3.2 Embedding Model

ChromaDB's default embedding model: `all-MiniLM-L6-v2` (same model that
produces MemPalace's 96.6% LongMemEval score). No API key required. Runs
locally. ~50MB footprint.

### 3.3 Collection Schema

Collection name: `deliberations`

Each document in ChromaDB:
- **id:** `{deliberation_id}` (or `{deliberation_id}::chunk-{N}` for long content)
- **document:** deliberation content (redacted version only — secrets never enter ChromaDB)
- **metadata:**
  - `delib_id`: deliberation ID
  - `spec_id`: primary linked spec (if any)
  - `work_item_id`: primary linked WI (if any)
  - `source_type`: lo_review, proposal, owner_conversation, etc.
  - `outcome`: go, no_go, deferred, owner_decision, informational
  - `session_id`: session identifier
  - `title`: deliberation title

### 3.4 Chunking Strategy

Deliberations exceeding 8,000 characters are split into chunks of ~4,000
characters with 200-character overlap. Each chunk gets a unique ID
(`DELIB-NNNN::chunk-NNN`). Search results are deduplicated by deliberation ID.

### 3.5 API Changes

```python
# Existing — upgraded with ChromaDB path
def search_deliberations(self, query: str, *, limit: int = 5) -> list[dict]:
    """Search deliberations semantically via ChromaDB.
    Falls back to SQLite LIKE if ChromaDB is unavailable."""

# New
def rebuild_deliberation_index(self) -> dict:
    """Rebuild ChromaDB collection from SQLite canonical data.
    Returns: {"indexed": N, "chunks": M, "errors": []}"""
```

### 3.6 Sync on Insert

`insert_deliberation()` will be extended to index new deliberations in ChromaDB
at write time (if ChromaDB is available). This keeps the index current without
requiring explicit rebuilds.

## 4. Implementation Plan

| Step | Description | Files |
|------|-------------|-------|
| 1 | Add `chromadb` optional dependency to `pyproject.toml` | `pyproject.toml` |
| 2 | Add ChromaDB collection helper (init, get_or_create) | `src/groundtruth_kb/db.py` |
| 3 | Implement chunking utility for long deliberations | `src/groundtruth_kb/db.py` |
| 4 | Extend `insert_deliberation()` to sync to ChromaDB | `src/groundtruth_kb/db.py` |
| 5 | Upgrade `search_deliberations()` with ChromaDB path + fallback | `src/groundtruth_kb/db.py` |
| 6 | Implement `rebuild_deliberation_index()` | `src/groundtruth_kb/db.py` |
| 7 | Add tests: semantic search, fallback, rebuild, chunking, redaction safety | `tests/test_deliberations.py` |

## 5. Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| ChromaDB adds ~50MB install footprint | Optional dependency; SQLite-only mode works without it |
| Embedding model download on first use | Document in install instructions; pre-cache in CI |
| ChromaDB index diverges from SQLite | `rebuild_deliberation_index()` + sync on insert |
| Redacted content leaks to ChromaDB | Only index post-redaction content; assert in tests |
| ChromaDB version incompatibility | Pin range `>=0.5.0,<0.7`; test in CI |

## 6. Review Questions for Codex

1. Is the chunking strategy (4K chars, 200-char overlap) appropriate for
   deliberation text, or should we use a different size?
2. Should the ChromaDB collection be stored alongside the SQLite DB
   (`~/.groundtruth/chroma/`) or in a separate configurable path?
3. Are there additional metadata fields that should be indexed in ChromaDB
   for filtering?
4. Should `rebuild_deliberation_index()` be exposed as a CLI command
   (`gt deliberations rebuild-index`)?
