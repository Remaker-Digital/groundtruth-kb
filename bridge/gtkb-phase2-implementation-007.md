# Phase 2 Post-Implementation Report: F3 + F2-A + F4-A

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Post-Implementation Report
**GO reference:** bridge/gtkb-phase2-implementation-006.md
**Commits:** a21fa19 (F3+F4-A, S287), 35514fe (F2-A, S288)

## Implementation Summary

All three Phase 2 features are implemented and committed on groundtruth-kb main:

| Feature | Commit | Tests | Lines | Status |
|---------|--------|-------|-------|--------|
| F3: Spec Quality Gate | a21fa19 | 12 | ~300 | Committed S287 |
| F4-A: Constraint Propagation (Phase A) | a21fa19 | 6 | ~150 | Committed S287 |
| F2-A: Change Impact Analysis (Phase A) | 35514fe | 15 | 612 | Committed S288 |
| **Total** | — | **33** | **~1,062** | — |

## GO Condition Compliance

### Condition 1: F2 v6 test and implementation conditions

**Status: MET**

All 15 tests from the approved v6 test plan implemented:
1. Contained blast radius (3 related < 5 threshold) ✓
2. Systemic blast radius (25 related >= 20 threshold) ✓
3. Constraint detection via F4-A check_constraints_for_spec() ✓
4. grep vs grep_absent conflict detection ✓
5. Non-machine (visual) assertion skip ✓
6. Custom thresholds via ImpactConfig(contained_threshold=2) ✓
7. file_exists with path alias ✓
8. grep with target alias ✓
9. json_path extraction (match_target = dotted path) ✓
10. json_path no-conflict (same file, different paths) ✓
11. all_of composition (recurse into children) ✓
12. grep with file glob (file_is_glob=True) ✓
13. Literal-vs-glob false-negative documented with annotation ✓
14. grep_absent with file glob ✓
15. count with file glob ✓

Cases 12-15 cover all grep-style file-glob extraction per GO condition 1.
Exact-string conflict comparison preserved per GO condition 2.
Typed json_path targets preserved per GO condition 3.

### Condition 2: spec_quality_scores in schema, export, import

**Status: MET** (committed a21fa19, S287)

- Schema: CREATE TABLE IF NOT EXISTS spec_quality_scores (db.py:289-303)
- Export: added to export_json() table list (db.py:3083)
- Import: added to _IMPORTABLE_TABLES (cli.py:334)
- Flags validation: JSON list validation in import path (cli.py:414-425)

### Condition 3: flags validation with skip-or-error

**Status: MET** (committed a21fa19, S287)

- Non-merge mode: raises click.ClickException (cli.py:422-423)
- Merge mode: rejects row, emits warning, continues (cli.py:419-420)
- Test verifies malformed flags are not stored after import rejection

### Condition 4: F4-A tests and read-only scope

**Status: MET** (committed a21fa19, S287)

All 6 F4-A tests implemented:
1. Advisory lookup (ADR in matching section)
2. Non-matching skip (different section)
3. Coverage report (sections with/without constraint coverage)
4. ADR vs DCL filtering
5. Empty result (no ADR/DCL specs)
6. Multiple constraints overlapping same section

F4-A methods are read-only: check_constraints_for_spec() and
get_constraint_coverage(). No Phase B linkage writes.

### Condition 5: Verification scope

**Status: MET**

```
python -m pytest -q                          → 487 passed
python -m ruff check .                       → All checks passed
python -m ruff format --check .              → 55 files already formatted
python scripts/check_docs_cli_coverage.py    → All documentation checks passed
```

## F2-A Implementation Details

### New files

- `src/groundtruth_kb/impact.py` (145 lines): ImpactConfig dataclass,
  _targets_for_spec(), _detect_conflicts(), _classify_blast_radius(),
  compute_impact_analysis()
- `tests/test_impact.py` (280 lines): 15 tests in 2 classes

### Modified files

- `src/groundtruth_kb/assertions.py`: Added AssertionTarget dataclass (frozen),
  _GREP_STYLE_TYPES constant, _extract_assertion_targets() shared helper (105 lines)
- `src/groundtruth_kb/db.py`: Added compute_impact() delegation method (19 lines)

### Architecture decisions

1. **Shared extraction in assertions.py:** _extract_assertion_targets() reuses
   _normalize_assertion() for alias resolution, preventing F2/F8 divergence.
2. **Lazy import in db.py:** compute_impact() uses deferred import to avoid
   circular dependency (db → impact → assertions).
3. **ImpactConfig dataclass:** Defaults (contained=5, systemic=20) match proposal.
   Custom thresholds verified by test 6.
4. **Conflict annotations:** Literal-vs-glob false-negative produces an annotation
   in the output dict rather than silently skipping.

## Request

Codex review requested. VERIFIED authorizes Phase 2 completion and advancement
to Phase 2B (F2-B + F4-B).
