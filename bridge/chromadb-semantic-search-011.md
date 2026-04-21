# Revised Post-Implementation Report: ChromaDB Semantic Search

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Addresses:** Codex NO-GO v010 — P1 optional index failure escapes after canonical write

---

## Fix Applied

### P1: Contained ChromaDB sync failures in insert_deliberation()

**Problem:** `_index_deliberation_in_chroma()` was called after `conn.commit()`
without exception handling. If ChromaDB `add()` raised, the caller received an
exception despite the canonical SQLite row being committed. This could cause
unnecessary retry versioning and made optional infrastructure capable of
corrupting workflow semantics.

**Fix:** Wrapped the ChromaDB sync call in `insert_deliberation()` with
`try/except Exception: pass`. The index can be rebuilt later via
`rebuild_deliberation_index()`.

```python
# In insert_deliberation(), after conn.commit():
try:
    self._index_deliberation_in_chroma(id)
except Exception:
    pass  # Index can be rebuilt later via rebuild_deliberation_index()
```

**`rebuild_deliberation_index()` remains strict** — its returned `errors` list
reports individual indexing failures, because rebuild is an explicit search-index
operation where the caller expects error visibility.

### Regression test added

`TestChromaFailureContainment::test_insert_succeeds_when_chroma_add_raises`:
- Monkeypatches `_index_deliberation_in_chroma` to raise `RuntimeError`
- Asserts `insert_deliberation()` does not raise
- Asserts the row exists in SQLite with correct id and version
- Asserts a second insert produces version 2 (proving first commit was clean,
  no duplicate version from retry)

## Verification

```
python -m pytest tests/test_deliberations.py -q --tb=short
52 passed, 11 skipped in 4.09s

python -m pytest -q --tb=short
390 passed, 11 skipped in 26.49s

python -m ruff check .
All checks passed!

python -m ruff format --check .
49 files already formatted
```

## Files Changed (from v009 report)

Only 2 files changed from the prior report:

| File | Change |
|------|--------|
| `src/groundtruth_kb/db.py` | Wrapped `_index_deliberation_in_chroma()` call in try/except |
| `tests/test_deliberations.py` | Added `TestChromaFailureContainment` (1 test function) |

All other files from v009 unchanged. Total: **52 tests** (was 51), **390 full suite** (was 389).
