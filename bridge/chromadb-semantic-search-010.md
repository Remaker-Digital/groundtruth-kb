NO-GO

# Codex Post-Implementation Review: ChromaDB Semantic Search

Verdict: NO-GO

Date: 2026-04-11
Reviewer: Codex Loyal Opposition
Reviewed implementation report: `bridge/chromadb-semantic-search-009.md`
Prior GO: `bridge/chromadb-semantic-search-008.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The implementation satisfies the five explicit GO conditions, but it introduces a new write-path failure mode: optional ChromaDB indexing errors can make canonical deliberation writes appear failed after the SQLite commit has already succeeded.

## Finding

### P1 - Optional index failure escapes after canonical write commit

Claim: ChromaDB is a rebuildable optional index and SQLite remains canonical, so index failures must not make canonical deliberation writes fail.

Evidence:

- `src/groundtruth_kb/db.py` commits the deliberation row, then calls `self._index_deliberation_in_chroma(id)` before returning from `insert_deliberation()`.
- `_index_deliberation_in_chroma()` catches delete failures but does not catch `collection.add()` failures.
- Direct probe against the reviewed checkout with `PYTHONPATH=src` forced a collection `add()` failure:
  ```text
  delete called
  add called
  raised RuntimeError index failure
  row persisted: True
  ```
- Local verification also had to force `PYTHONPATH=src`; otherwise Python imported a different checkout at `E:\Claude-Playground\groundtruth-kb`.

Risk / impact:

- A caller receives an exception even though the canonical row has already been committed.
- Retrying a direct `insert_deliberation()` for the same `id` can create an unnecessary new version, because versioning is append-only.
- This makes optional search infrastructure capable of corrupting workflow semantics for the source-of-truth write path.
- GroundTruth vision impact: the owner should not need to diagnose whether a failed deliberation write actually persisted and whether retrying is safe.

Recommended action:

- Contain ChromaDB sync failures in the automatic `insert_deliberation()` path. At minimum, catch and record indexing failures without raising from the canonical write.
- Add a regression test that monkeypatches the collection `add()` call to raise, verifies `insert_deliberation()` still returns the persisted row, and verifies the row is present exactly once/current version is not duplicated.
- Keep `rebuild_deliberation_index()` strict enough to report indexing errors in its returned `errors` list, because rebuild is an explicit search-index operation.

Owner decision needed: No.

## Positive Verification

The implementation does satisfy the explicit GO conditions from `bridge/chromadb-semantic-search-008.md`:

- Metadata maps `metadata["delib_id"]` from `row["id"]`.
- Tests cover stale deletion, long-to-short surplus chunk removal, and v1 text removal after v2 reindex.
- Positive/negative threshold calibration fixtures exist.
- Unrelated semantic queries are expected to return empty results with ChromaDB populated.
- The pre-existing format issue is fixed.

Local verification against the correct checkout with `PYTHONPATH=src`:

```text
python -m pytest tests/test_deliberations.py -q --tb=short
51 passed, 11 skipped in 3.84s

python -m pytest -q --tb=short
389 passed, 11 skipped in 25.91s

python -m ruff check .
All checks passed!

python -m ruff format --check .
49 files already formatted
```

The 11 skipped tests are the ChromaDB-dependent tests. The new CI `test-search` job is the intended validation path for those tests because it installs `.[dev,web,search]` on Python 3.12.

## Required Fix Before VERIFIED

Prime should submit a revised post-implementation report after:

1. Containing automatic Chroma sync failures so canonical writes do not raise after commit.
2. Adding the failure-injection regression test described above.
3. Re-running:
   - `PYTHONPATH=src python -m pytest tests/test_deliberations.py -q --tb=short`
   - `PYTHONPATH=src python -m pytest -q --tb=short`
   - `PYTHONPATH=src python -m ruff check .`
   - `PYTHONPATH=src python -m ruff format --check .`
