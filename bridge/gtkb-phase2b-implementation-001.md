# Phase 2B: F4-B + F2-B — Implementation Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Implementation Proposal
**Prerequisite:** Phase 2 VERIFIED (012). F1 fields (authority, affected_by, testability) available.
**Approved designs:** F4-003 (GO: F4-004), F2-011 (GO: F2-012)
**Cross-check:** gtkb-f1f8-cross-check-001 (GO: -002)

## Rationale

Phase 2B implements the write side of constraint propagation (F4-B) and the
dependency-chain traversal for impact analysis (F2-B). F4-B is implemented
first because it writes `affected_by` linkages that F2-B then reads.

Both features depend on F1's `affected_by` column and `update_spec()`, which
are already committed (1e1e965) and VERIFIED.

---

## F4-B: Constraint Propagation (Phase B — Linkage Writes)

### No New Tables/Columns

F4-B writes to the existing `affected_by` JSON column (F1) via `update_spec()`.
Each propagation creates a new spec version (append-only).

### Methods

```python
KnowledgeDB.propagate_constraint(
    constraint_id: str,
    *,
    dry_run: bool = True,
) -> dict[str, Any]
```

**Behavior:**
1. Look up the ADR/DCL spec by `constraint_id`.
2. Find matching functional specs via `_find_matching_constraints()` (already
   shared from F4-A).
3. For each matching spec, check if `constraint_id` is already in its
   `affected_by_parsed` list.
4. If not already linked and `dry_run=False`: call `update_spec()` with
   the updated `affected_by` list, `changed_by="constraint-propagation"`,
   and `change_reason` documenting the linkage.
5. Return a report dict.

**Return shape:**
```python
{
    "constraint_id": str,
    "constraint_title": str,
    "dry_run": bool,
    "affected_specs": [{"id": str, "title": str, "action": "linked"|"already_linked"}],
    "newly_linked": int,
    "already_linked": int,
}
```

**Link removal:**

```python
KnowledgeDB.remove_constraint_link(
    spec_id: str,
    constraint_id: str,
    *,
    changed_by: str = "constraint-propagation",
) -> dict[str, Any]
```

Removes `constraint_id` from the spec's `affected_by` list via `update_spec()`.
Returns `{"spec_id", "constraint_id", "removed": bool}`.

### Tests (8)

1. **Dry-run propagation** — ADR + 2 matching specs; dry_run=True; no spec versions created; report shows 2 affected
2. **Write propagation** — dry_run=False; both specs get new version with constraint in affected_by
3. **Already-linked skip** — run propagation twice; second run shows already_linked=2, newly_linked=0
4. **Non-matching skip** — spec in different section; not in affected_specs
5. **Link removal** — remove constraint from one spec; verify affected_by no longer contains it
6. **Link removal idempotent** — remove constraint not in affected_by; removed=False
7. **Append-only versioning** — after propagation, spec has version N+1; original version preserved
8. **Changed_by audit** — new version has changed_by="constraint-propagation"

### File Touchpoints

- `src/groundtruth_kb/db.py`: 2 new methods
- `tests/test_constraint_propagation.py`: 8 new tests (extend existing file)

---

## F2-B: Change Impact Analysis (Phase B — Dependency Chain)

### No New Tables/Columns

F2-B reads F1's `affected_by_parsed` and `authority` fields.

### Changes to compute_impact_analysis()

1. **Dependents field populated:** After finding related specs, traverse
   `affected_by_parsed` across all specs to find specs that list the target
   spec (or its related specs) in their `affected_by`. These are the
   dependents — specs that would be impacted by changes to the target.

2. **Authority-weighted blast radius:** When authority information is available,
   weight the blast radius classification. Specs with `authority="stated"` or
   `authority="inherited"` carry more weight than `"provisional"` or
   `"inferred"`.

3. **Testability filtering:** The report includes a `testability_summary`
   showing the distribution of testability values among related specs
   (automatable, observable, structural, untestable).

### Updated Return Shape

Adds to existing return dict:
```python
{
    # ... existing fields ...
    "dependents": [{"id": str, "title": str, "via": str}],  # populated (was empty)
    "testability_summary": {"automatable": int, "observable": int, ...},
    "authority_distribution": {"stated": int, "provisional": int, ...},
}
```

### Tests (7)

1. **Dependents populated** — SPEC-A has affected_by=[ADR-001]; ADR-001 impact shows SPEC-A as dependent
2. **Transitive dependents** — SPEC-A affected_by SPEC-B; SPEC-B affected_by SPEC-C; SPEC-C impact shows SPEC-A (depth=2, Phase B cap)
3. **No dependents** — spec with no affected_by references; dependents=[]
4. **Authority distribution** — 3 specs: stated, provisional, inferred; report shows distribution
5. **Testability summary** — 3 specs: automatable, observable, untestable; report shows distribution
6. **Authority affects recommendation** — systemic blast radius with all provisional specs gets softer recommendation
7. **Dependents deduplication** — same spec appears via multiple paths; listed once

### File Touchpoints

- `src/groundtruth_kb/impact.py`: enhance compute_impact_analysis()
- `tests/test_impact.py`: 7 new tests

---

## Implementation Order

1. F4-B first (8 tests) — writes affected_by linkages
2. F2-B second (7 tests) — reads affected_by for dependents

## Combined Verification Plan

1. `python -m pytest -q` — full suite (494 → ~509 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Total Estimated Changes

| Feature | New files | Tests | Lines |
|---------|-----------|-------|-------|
| F4-B | 0 | 8 | ~200 |
| F2-B | 0 | 7 | ~150 |
| **Total** | **0 new, 3 modified** | **15** | **~350** |

## Request

Codex review requested. GO authorizes Phase 2B implementation.
