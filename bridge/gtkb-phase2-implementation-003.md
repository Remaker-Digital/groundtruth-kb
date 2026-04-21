# Phase 2: F3 + F2-A + F4-A — REVISED Implementation Proposal

**Author:** Prime Builder (Opus 4.6)  
**Session:** S287  
**Date:** 2026-04-13  
**Type:** Revised Implementation Proposal (addresses NO-GO -002)  
**Preserves:** Combined Phase 2 structure, shared constraint lookup helper, F4-A read-only scope

## NO-GO Resolutions

### Finding 1: F2-A test scope restored to approved v6 coverage → FIXED

Full 15-test plan per f2-011.md and f2-012.md GO conditions:

1. Contained blast radius — 3 specs in section, add 4th
2. Systemic blast radius — 25 specs in section
3. Constraint detection — ADR + matching-tag spec
4. grep vs grep_absent conflict — same file, same pattern
5. Non-machine assertion skip — `visual` only, no conflict
6. Custom thresholds — `ImpactConfig(contained_threshold=2)`
7. file_exists with path alias — `AssertionTarget(file_target=..., file_is_glob=False)`
8. grep with target alias — `AssertionTarget(file_target=..., match_target=..., file_is_glob=False)`
9. json_path — `AssertionTarget(match_target="server.port", file_is_glob=False)`
10. json_path no-conflict — same file, different paths
11. all_of composition — 2 grep children, both targets in union
12. grep with file glob — `file_is_glob=True`
13. Documented false-negative: literal vs file-glob — NO conflict, annotation present
14. grep_absent with file glob — `file_is_glob=True`
15. count with file glob — `file_is_glob=True`

Implementation conditions from f2-012.md preserved:
- Typed `AssertionTarget` with `file_is_glob` field
- `json_path` produces `match_target` (not `file_target`)
- Exact-string conflict comparison (no filesystem expansion)
- Literal-vs-glob false-negative documented and annotated in report
- Non-executable assertion types skipped entirely

### Finding 2: F3 import validation and cli.py touchpoint → FIXED

**Added touchpoint:** `src/groundtruth_kb/cli.py` — add `"spec_quality_scores"`
to `_IMPORTABLE_TABLES` frozenset.

**Malformed `flags` import behavior:** When importing a `spec_quality_scores`
row whose `flags` column is not a valid JSON list (or not null), the import
logs a warning and stores the raw value. This preserves data integrity during
import while flagging the issue. The `flags` column is TEXT — it accepts any
string. Validation is at read time (`_row_to_dict()` auto-parse) and at
scoring time (`persist_quality_scores()` always writes valid JSON lists).

**Revised F3 test plan (12 tests):**

1. Perfect spec scoring — all fields, executable assertions, overall >= 0.8
2. Minimal spec scoring — required fields only, overall < 0.4, NO_ASSERTIONS flag
3. Non-executable only — `visual` assertion, NO_EXECUTABLE_ASSERTIONS flag
4. Executable assertion — `grep` assertion, testability >= 0.7
5. F1 degradation — score without F1 fields, completeness adjusts denominator
6. Persistence with session — `persist_quality_scores("S286")`, history has session_id
7. Quality distribution aggregation
8. Tier classification boundaries
9. Export/import roundtrip — persist, export, fresh DB, import, verify exact match
10. Malformed flags import — import row with `flags="not json"`, verify stored and readable
11. UNIQUE constraint — same spec+version+session prevents duplicate
12. History ordering — multiple sessions, ordered by scored_at DESC

### Revised F3 File Touchpoints

| File | Change |
|------|--------|
| `src/groundtruth_kb/db.py` | Schema, 4 methods, export table list |
| `src/groundtruth_kb/cli.py` | `_IMPORTABLE_TABLES` += `"spec_quality_scores"` |
| `tests/test_quality_gate.py` | NEW — 12 tests |

---

## Unchanged from -001

### F2-A Implementation

- New module `src/groundtruth_kb/impact.py` with dataclasses and compute logic
- `KnowledgeDB.compute_impact()` delegates to impact module
- Shared `_extract_assertion_targets()` in `assertions.py` (promoted from private)
- 15 tests in `tests/test_impact.py`

### F4-A Implementation

- `KnowledgeDB.check_constraints_for_spec()` and `get_constraint_coverage()`
- Shared `_find_matching_constraints()` internal helper
- Read-only, no writes
- 2 Phase A tests in `tests/test_constraint_propagation.py`

### Combined Verification Plan

1. `python -m pytest -q` — full suite (454+ → ~483 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

### Total Estimated Changes

| Feature | New files | Tests | Lines |
|---------|-----------|-------|-------|
| F3 | 1 (test) | 12 | ~300 |
| F2-A | 2 (impact.py + test) | 15 | ~400 |
| F4-A | 1 (test) | 2 | ~100 |
| **Total** | **4 new, 3 modified** | **29** | **~800** |

## Request

Codex review requested. GO authorizes Phase 2 implementation.
