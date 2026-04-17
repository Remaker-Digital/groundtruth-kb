# F1-F8 Cross-Check Alignment Report

**Author:** Prime Builder (Opus 4.6)  
**Session:** S287  
**Date:** 2026-04-13  
**Type:** Part B — Cross-Check Analysis  
**Prior Deliberations:** DELIB-0709 (all 8 GO gate)  
**Baseline files:** F1-007, F2-011, F3-005, F4-003, F5-019, F6-003, F7-005, F8-013

## Executive Summary

All 8 proposals are **mutually consistent** with 6 interface issues requiring
resolution during implementation. No circular dependencies exist. The proposed
dependency order is confirmed with one refinement: F5 (Intake) moves to Phase 3
due to broader dependencies than originally scoped.

## Producer/Consumer Matrix

| Field | Defined by | Written by | Read by |
|-------|-----------|-----------|---------|
| `authority` | F1 | F1, F6 (`inferred`) | F2-B, F3, F5, F7, F8 |
| `provisional_until` | F1 | F1 | F8 (expiration check) |
| `constraints` (JSON) | F1 | F1, F4 | F3 (D3), F5 |
| `affected_by` (JSON) | F1 | F4-B (primary writer via `update_spec`) | F2-B, F5 |
| `testability` | F1 | F1 | F2-B, F3 (D2) |
| `affected_by_parsed` | F1 (computed) | F1 (at read time) | F2-B |
| `constraints_parsed` | F1 (computed) | F1 (at read time) | Advisory |
| `spec_quality_scores` table | F3 | F3 | F3 (history), export/import |
| `get_quality_distribution()` | F3 | F3 | F7 (snapshot) |
| `get_constraint_coverage()` | F4 | F4 | F7 (snapshot) |
| `check_constraints_for_spec()` | F4 | F4 | F5 (on confirm) |
| `compute_impact()` | F2 | F2 | F5 (impact preview) |
| `score_spec_quality()` | F3 | F3 | F5 (tier recommendation) |
| `session_snapshots` table | F7 | F7 | F8 (stale detection) |
| Deliberation records | F5 | F5 | Deliberation archive |
| Generated seed specs | F6 | F6 | F3, F4, F7, F8 |
| `ReconciliationReport` | F8 | F8 | Advisory (read-only) |

## Confirmed Dependency Order

```
Phase 1: F1 (Schema Enrichment)
         └─ No dependencies. All other features depend on F1.

Phase 2: F2 Phase A + F3 + F4 Phase A  (parallel)
         ├─ F2-A: uses existing fields only
         ├─ F3: soft F1 dependency (graceful degradation)
         └─ F4-A: read-only advisory, existing fields only

Phase 3: F2 Phase B + F4 Phase B + F5 + F7  (parallel after Phase 2)
         ├─ F2-B: requires F1 (affected_by_parsed, authority, testability)
         ├─ F4-B: requires F1 (writes affected_by via update_spec)
         ├─ F5: requires F1 (authority on confirm), F2 (impact), F3 (tier), F4 (constraints)
         └─ F7: requires F1 (distributions), F3 (quality), F4 (coverage)

Phase 4: F6 Phase B + F8  (after Phase 3)
         ├─ F6-B: requires F1 (authority='inferred'), F3 (quality validation)
         └─ F8: requires F1 (authority, provisional_until), F7 (snapshot history)
```

**Change from original plan:** F5 moved from Phase 3 (originally grouped with
F4+F7) to remain in Phase 3 but with explicit dependency on F2+F3+F4. The
original plan listed F5 as independent of F2/F3, but the GO'd proposal shows
F5 consumes F2's impact preview and F3's tier recommendation during confirm.

**No circular dependencies found.** All dependency arrows point downward.

## Interface Issues (6)

### Issue 1: F7 method name inconsistency [LOW]

**Finding:** F7's API section defines `render_health_dashboard()` but test
plan 4 references `render_health_text()`.

**Resolution:** Pick one name at implementation time. Recommend
`render_health_text()` since it returns a string, not a visual component.

### Issue 2: F2 and F4 duplicate constraint detection [LOW]

**Finding:** F2's `compute_impact()` finds `applicable_constraints` via
section/tag matching. F4's `check_constraints_for_spec()` does the same.
Two functions with overlapping query logic.

**Resolution:** Extract a shared private function
`_find_matching_constraints(section, scope, tags)` at implementation time.
Both F2 and F4 call it. Prevents drift.

### Issue 3: F6 Phase A → Phase B migration gap [MEDIUM]

**Finding:** Phase A generates specs WITHOUT `authority` field (F1 not yet
available). When F1 ships and Phase B activates, previously scaffolded specs
from Phase A lack `authority`. No retroactive addition path documented.

**Resolution:** F1's schema migration adds `authority` with NULL default to
ALL existing rows. Phase A specs get NULL authority, which F1's
`_normalize_provisional()` treats as legacy. F3 handles NULL via "adjusts
denominator" logic. No explicit migration needed — the existing NULL-handling
in F1 and F3 covers this. Document this as a known behavior.

### Issue 4: F7 session_snapshots PK constraint [MEDIUM]

**Finding:** `session_id` as PRIMARY KEY means exactly one snapshot per
session. If `capture_session_snapshot()` is called twice (start + end), the
second call violates the PK.

**Resolution options:**
- **(A)** Compound PK `(session_id, timestamp)` — allows multiple snapshots
- **(B)** UPSERT — second call replaces the first
- **(C)** Document single-capture-per-session as intentional

**Recommendation:** Option B (UPSERT via INSERT OR REPLACE). Session-end
snapshot is the most complete; replacing the start snapshot is correct
behavior. This aligns with the "one snapshot per session" semantic while
being resilient to double-capture.

### Issue 5: F8 stale detection bootstrap [LOW]

**Finding:** F8's `get_stale_specs()` depends on F7 snapshot history, which
only exists from F7's deployment forward. Historical staleness before F7
cannot be measured.

**Resolution:** F8 returns an empty list for stale specs when fewer than
`staleness_threshold_sessions` snapshots exist. This is correct behavior —
stale detection ramps up as snapshot history accumulates. Document in F8's
implementation that stale detection is a trailing indicator.

### Issue 6: F2 imports GT-KB private internals [LOW]

**Finding:** F2 imports `_normalize_assertion`, `_VALID_ASSERTION_TYPES`,
`_MAX_COMPOSITION_DEPTH`, `_FILE_ALIASES`, `_PATTERN_ALIASES` from
`assertions.py`. These are underscore-prefixed (private by convention).

**Resolution:** At implementation time, promote the 5 constants/functions to
public API (remove underscore prefix) or create a
`groundtruth_kb.assertion_internals` module. Since F2 and F8 both need
these, making them semi-public is justified. This is a local decision — does
not affect cross-feature interfaces.

## No Name Mismatches Found

All F1 field names are referenced consistently across consumers:

| Field | F1 definition | F2 reference | F3 reference | F4 reference | F5 reference | F7 reference | F8 reference |
|-------|--------------|-------------|-------------|-------------|-------------|-------------|-------------|
| `authority` | TEXT column | ✓ same name | ✓ same name | — | ✓ same name | ✓ same name | ✓ same name |
| `testability` | TEXT column | ✓ same name | ✓ same name | — | — | — | — |
| `affected_by` | TEXT (JSON) | ✓ `affected_by_parsed` | — | ✓ writes via `update_spec` | ✓ same name | — | — |
| `constraints` | TEXT (JSON) | — | ✓ same name | ✓ same name | ✓ same name | — | — |
| `provisional_until` | TEXT column | — | — | — | — | — | ✓ same name |

## Conclusion

The 8 proposals are aligned. The 6 issues are all resolvable at implementation
time without changing approved interfaces. No proposal contradicts another.
The dependency order is confirmed with the F5 placement refinement.

**Recommendation:** Proceed to F1 implementation.
