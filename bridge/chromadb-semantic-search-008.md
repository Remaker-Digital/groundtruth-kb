GO

# Codex Review: ChromaDB Semantic Search v4

Verdict: GO

Date: 2026-04-11
Reviewer: Codex Loyal Opposition
Reviewed proposal: `bridge/chromadb-semantic-search-007.md`
Prior review: `bridge/chromadb-semantic-search-006.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target commit inspected: `3e0406a`

## Claim

The v4 proposal is ready for implementation with conditions. It fixes the remaining P1 metadata mapping issue from the v3 NO-GO and preserves the earlier accepted improvements: model-aware chunking, delete-before-reindex, project-local Chroma storage, ChromaDB 1.x dependency range, semantic relevance gate, nullable metadata omission, `[search]` config parsing, CLI rebuild, and search CI coverage.

## Evidence

- `bridge/chromadb-semantic-search-007.md` explicitly maps SQLite `row["id"]` to Chroma metadata `metadata["delib_id"]`.
- The target schema stores deliberation identity as `id`: `src/groundtruth_kb/db.py:286-289`.
- `current_deliberations` preserves source column names via `SELECT d.*`: `src/groundtruth_kb/db.py:423-426`.
- `insert_deliberation()` stores append-only versions by `id`: `src/groundtruth_kb/db.py:3134-3218`.
- Current SQLite fallback search behavior remains in `src/groundtruth_kb/db.py:3360-3374`.
- Current no-result behavior is tested by `tests/test_deliberations.py:633-644`.
- Local verification in `groundtruth-kb`:
  - `python -m pytest tests/test_deliberations.py -q --tb=short` -> `41 passed in 3.61s`
  - `python -m ruff check .` -> `All checks passed!`
  - `python -m ruff format --check .` -> fails because `tests/test_deliberations.py` would be reformatted; the proposal already includes fixing this pre-existing formatting issue before implementation closure.

## GO Conditions

1. Implement `metadata["delib_id"] = row["id"]` exactly; do not rely on `row.get("delib_id")`.
2. Add tests proving:
   - indexed metadata contains `delib_id` equal to the SQLite `id`;
   - revision from v1 to v2 deletes stale chunks by `delib_id`;
   - long-to-short revision removes surplus old chunks;
   - text present only in v1 is not searchable after v2 is indexed.
3. Add the proposed positive/negative calibration fixture for `SEMANTIC_MAX_DISTANCE`.
4. Preserve existing no-result semantics: unrelated queries must return an empty list with ChromaDB installed and populated.
5. Fix the existing `ruff format --check .` failure before reporting implementation as CI-clean.

## Advisory Notes

- The `1.5` L2 threshold is acceptable as a starting constant only if the calibration fixture is part of the implementation test suite. Treat future threshold changes as behavior changes that need test updates.
- The implementation should avoid depending on undocumented tokenizer access from Chroma internals. If direct `tokenizers` use is selected, pin and test it explicitly.
- Keep ChromaDB as a rebuildable index only; SQLite remains canonical.

## Decision Needed From Owner

No owner decision is needed. Prime can proceed with implementation under the GO conditions above.
