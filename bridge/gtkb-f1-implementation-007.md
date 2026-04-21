# F1 Post-Implementation Report

**Author:** Prime Builder (Opus 4.6)  
**Session:** S287  
**Date:** 2026-04-13  
**Commit:** 1e1e965 (groundtruth-kb main)  
**Type:** Post-Implementation Report

## Summary

F1 (Spec Schema Enrichment) is implemented, tested, and pushed. 2 files
changed, 755 insertions, 7 deletions. All verification checks pass.

## Implementation Details

### Files Changed

| File | Change |
|------|--------|
| `src/groundtruth_kb/db.py` | Migration (5 columns), sentinels, 6 validators, `_normalize_provisional()`, `insert_spec()` extended, `update_spec()` 8-step carry-forward, `_row_to_dict()` extended, `list_specs()` 2 new filters, `get_provisional_specs()`, `get_specs_affected_by()` |
| `tests/test_db.py` | 33 new test functions in `TestF1SchemaEnrichment` class |

### GO Conditions Addressed

1. **Invalid decision_authority test** — `test_f1_insert_invalid_decision_authority_raises` (line 288)
2. **Update-path constraints validation test** — `test_f1_update_new_constraints_validated` (line 429)
3. **excluded_approaches=None rejected** — `_validate_constraints()` rejects `None` for `excluded_approaches` (must be `list[str]`)
4. **Raw JSON preserved in _row_to_dict()** — `constraints` and `affected_by` added to parse list, raw keys preserved
5. **get_specs_affected_by() uses parsed list containment** — no SQL LIKE

### Key Implementation Choices

- `_UNSET` promoted to module scope (replaced 3 local definitions)
- Insert order: `_normalize_provisional()` → default `"stated"` → validate
- Update: raw JSON carry-forward via `current.get("constraints")` (not `_constraints_raw`)
- `get_specs_affected_by()`: loads all non-null rows, parses JSON, Python `in` check

## Verification

```
$ python -m pytest -q
454 passed, 1 warning in 52.82s

$ python -m ruff check .
All checks passed!

$ python -m ruff format --check .
51 files already formatted

$ python scripts/check_docs_cli_coverage.py
All documentation checks passed.
```

## Next: Phase 2

F1 is the foundation. Phase 2 features (F2-A, F3, F4-A) can now begin.
