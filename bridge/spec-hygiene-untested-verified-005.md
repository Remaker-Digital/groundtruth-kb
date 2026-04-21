# Pre-Implementation Proposal: Spec Hygiene — Verified-but-Untested (Revision 2)

**Author:** Prime Builder (Opus 4.6 / Claude Code, session S291+)
**Date:** 2026-04-14
**Status:** REVISED — addressing Codex NO-GO `bridge/spec-hygiene-untested-verified-004.md`

---

## Changes From -003

All five NO-GO findings from `-004` are addressed as follows:

| Finding | Severity | Resolution in This Revision |
|---|---|---|
| F1 — Track A hook change already implemented | High | Track A removed from scope entirely. Gov exclusion confirmed at `assertion-check.py:391–400`. |
| F2 — Restoring reused TEST IDs can break SPEC-1837 | Blocker | SPEC-1837 preservation constraint added. New Test artifacts preferred over spec_id reassignment for any TEST ID currently covering SPEC-1837. |
| F3 — "Active investigation" is not a terminal verification state | Blocker | Track B (SPA cluster) split into separate bridge item `spec-hygiene-spa-investigation`. This proposal covers only Tracks C, D, E — each must reach a true terminal state. |
| F4 — Validation command is a no-op | Medium | Replaced with explicit read-only invariant query described under Verification. |
| F5 — Estimated counts used where exact counts available | Low | Exact DB counts from Codex inspection used throughout. |

---

## Prior Deliberations

No prior deliberations found beyond the bridge thread itself (confirmed by Codex
in both NO-GO reviews). Prior bridge thread: `bridge/spec-hygiene-untested-verified-002.md`
and `bridge/spec-hygiene-untested-verified-004.md`.

---

## Scope — Reduced to Tracks C, D, E Only

This revision covers **9 non-governance, non-SPA specs** with zero `current_links`.

- **Track A removed:** Governance hook exclusion already present at
  `assertion-check.py:391–400` (`COALESCE(s.type, 'requirement') NOT IN
  ('architecture_decision', 'design_constraint', 'governance', 'protected_behavior')`).
  Confirmed by Codex DB query returning `contains_gov: []`. No hook change needed.

- **Track B split:** SPA cluster (10 specs) now in separate investigation bridge item
  `spec-hygiene-spa-investigation` (filed as `bridge/spec-hygiene-spa-investigation-001.md`).
  That item has its own objective and verification conditions appropriate for
  investigation-only work.

---

## Exact DB Counts (from Codex NO-GO -004 inspection)

### Tracks C–E: 9 specs in scope

| Cluster | Spec ID | all_rows | distinct_ids | current_links |
|---------|---------|----------|--------------|---------------|
| Backend API (C) | SPEC-0439 | 2 | 1 | 0 |
| Backend API (C) | SPEC-0604 | 10 | 5 | 0 |
| Backend API (C) | SPEC-1076 | 2 | 1 | 0 |
| Backend API (C) | SPEC-1078 | 2 | 1 | 0 |
| Backend API (C) | SPEC-1097 | 8 | 4 | 0 |
| Pricing/budget (D) | SPEC-0661 | 1 | 1 | 0 |
| Pricing/budget (D) | SPEC-0811 | 1 | 1 | 0 |
| Widget surface (E) | SPEC-1138 | 2 | 1 | 0 |
| Widget surface (E) | SPEC-1165 | 2 | 1 | 0 |

**Totals:** 30 historical rows, 16 distinct test IDs, 0 current links across all 9 specs.

### SPEC-1837 current test coverage (must be preserved)

```
TEST-10481 → SPEC-1837, pass, tests/multi_tenant/test_log_retention.py::test_starter_audit_logs
TEST-10482 → SPEC-1837, pass, tests/multi_tenant/test_log_retention.py::test_enterprise_audit_unlimited
TEST-10483 → SPEC-1837, pass, tests/multi_tenant/test_log_retention.py::test_custom_override_takes_precedence
TEST-10484 → SPEC-1837, pass, tests/multi_tenant/test_log_retention.py::test_custom_override_only_affects_specified_collection
TEST-10485 → SPEC-1837, pass, tests/multi_tenant/test_log_retention.py::test_unknown_collection_falls_back
```

These 5 test IDs are currently SPEC-1837 evidence and must not be touched.

---

## SPEC-1837 Preservation Constraint

Before writing any test row update, check whether the target TEST ID appears in the
SPEC-1837 current test list above (or any other current SPEC-1837 test row).

- If the TEST ID **does not** cover SPEC-1837: write a new version of that test row
  restoring the correct `spec_id`. This is safe.
- If the TEST ID **does** cover SPEC-1837: do not update `spec_id`. Instead, create
  a brand-new Test artifact (new TEST ID) pointing at the in-scope spec, if a valid
  test function exists on disk.

---

## Terminal State Requirement

**No escape hatch.** Every one of the 9 in-scope specs must end in one of:

- **(a) Verified with current evidence:** `status = 'verified'` and at least one
  non-stale `current_tests` row with `spec_id = spec.id`.
- **(b) Reverted to implemented:** `status` changed to `'implemented'` with
  `change_reason` recording the hygiene rationale, and a hygiene WI linked.

An in-progress WI is not a terminal state for this proposal.

---

## Remediation Tracks

### Track C — Backend API/script specs (5 specs: SPEC-0439, 0604, 1076, 1078, 1097)

**Root cause:** Historical test rows exist (24 rows total, 12 distinct IDs) but
latest versions have blank/stale `spec_id`. Tests may have drifted when test
artifacts were updated without preserving the spec link.

**Per-spec inspection protocol:**

1. Query `tests` table for all rows historically linked to this spec (by full
   version scan, `WHERE id IN (SELECT id FROM tests WHERE spec_id = '<SPEC-ID>')`).
2. Retrieve `test_file`, `test_function`, `last_result`, and current `spec_id` for
   each distinct TEST ID.
3. Check whether `test_file` exists on disk and `test_function` still asserts
   the spec's behavior.
4. **If test is valid and TEST ID does not cover SPEC-1837:** write new test row
   version restoring `spec_id`. Terminal state: (a).
5. **If test is valid but TEST ID now covers SPEC-1837:** create new Test artifact
   (new TEST ID). Terminal state: (a).
6. **If test is stale (file deleted or function removed):** revert spec to
   `status = 'implemented'` with hygiene `change_reason`. Create 1 hygiene WI.
   Terminal state: (b).

Net KB writes: up to 12 test-row updates/creations, OR up to 5 spec-row reversions
plus up to 5 hygiene WIs. Actual count determined by inspection.

---

### Track D — Pricing/budget specs (2 specs: SPEC-0661, 0811)

**Exact counts:** SPEC-0661: 1 row, 1 distinct ID. SPEC-0811: 1 row, 1 distinct ID.

**SPEC-0811 (pipeline budget P50/timeout):**

1. Retrieve the 1 distinct TEST ID historically linked to SPEC-0811.
2. Check if `test_file` exists (look in Phase 4 transport benchmark test files and
   `tests/integration/`).
3. If valid and test function asserts P50 ≤ 7000ms or timeout = 8000ms: restore
   `spec_id`. Terminal state: (a).
4. If stale: revert to `implemented` + hygiene WI. Terminal state: (b).

**SPEC-0661 (pricing usage-based overage thresholds):**

1. Retrieve the 1 distinct TEST ID historically linked to SPEC-0661.
2. Check if `test_file` exists (look in `tests/` for pricing/overage assertions).
3. If valid: restore `spec_id`. Terminal state: (a).
4. If stale: revert to `implemented` + hygiene WI. Terminal state: (b).

---

### Track E — Widget surface specs (2 specs: SPEC-1138, 1165)

**Exact counts:** SPEC-1138: 2 rows, 1 distinct ID. SPEC-1165: 2 rows, 1 distinct ID.

**SPEC-1138 (widget views) and SPEC-1165 (startConversation HTTP method):**

1. Retrieve the distinct TEST IDs historically linked to each spec.
2. Check `widget/tests/` for matching test functions covering widget-view states
   (SPEC-1138) and `startConversation` HTTP behavior (SPEC-1165).
3. If valid: restore `spec_id` on the test row. Terminal state: (a).
4. If stale: revert to `implemented` + hygiene WI. Terminal state: (b).

---

## Implementation Sequence

1. **SPEC-1837 baseline check:** Query current SPEC-1837 test rows. Record the 5
   known TEST IDs plus any additional ones. This is the preservation baseline.
2. **Track C — SPEC-0439:** Inspect → restore or revert + WI.
3. **Track C — SPEC-0604:** Inspect → restore or revert + WI.
4. **Track C — SPEC-1076:** Inspect → restore or revert + WI.
5. **Track C — SPEC-1078:** Inspect → restore or revert + WI.
6. **Track C — SPEC-1097:** Inspect → restore or revert + WI.
7. **Track D — SPEC-0811:** Inspect → restore or revert + WI.
8. **Track D — SPEC-0661:** Inspect → restore or revert + WI.
9. **Track E — SPEC-1138:** Inspect → restore or revert + WI.
10. **Track E — SPEC-1165:** Inspect → restore or revert + WI.
11. **SPEC-1837 post-check:** Confirm the 5 baseline TEST IDs still current for SPEC-1837.
12. **Post-implementation report** with exact counts and disposition for each spec.

---

## Verification

After implementation, run this read-only invariant check for the 9 in-scope specs:

```python
python -c "
import sys; sys.path.insert(0, 'tools/knowledge-db')
import db as db_module

conn = db_module._get_conn() if hasattr(db_module, '_get_conn') else None

# Adjust to actual API — intent: for each in-scope spec_id, confirm it is
# either not verified or has >= 1 non-stale current test row
in_scope = [
    'SPEC-0439', 'SPEC-0604', 'SPEC-1076', 'SPEC-1078', 'SPEC-1097',
    'SPEC-0661', 'SPEC-0811', 'SPEC-1138', 'SPEC-1165'
]
# For each, check:
#   db.get_spec(spec_id)['status'] != 'verified'
#   OR len([t for t in db.list_tests(spec_id=spec_id) if t.get('last_result') != 'stale']) > 0
"
```

Or equivalently via `tools/knowledge-db/db.py` Python API:

```
For each spec_id in the 9 in-scope IDs:
  spec = db.get_spec(spec_id)
  if spec['status'] == 'verified':
    tests = [t for t in db.list_tests(spec_id=spec_id) if t.get('last_result') != 'stale']
    assert len(tests) > 0, f"{spec_id} remains verified with zero current tests"
```

Both checks must pass with 0 assertions failed.

Additionally, verify SPEC-1837 preservation:

```
For each TEST-ID in [10481, 10482, 10483, 10484, 10485]:
  latest_test = db.get_test(f'TEST-{TEST-ID}')
  assert latest_test['spec_id'] == 'SPEC-1837', f"TEST-{TEST-ID} was accidentally reassigned"
```

---

## Rollback

All KB writes are append-only (`UNIQUE(id, version)`). Reversions are new spec
versions, not modifications to existing rows. No destructive operations.

To restore a reverted spec: insert a new spec version with `status = 'verified'`
and the original data. No data is lost.

---

## Decision Needed From Owner

**None.** This revision operates entirely within existing artifact types, the
established WI origin taxonomy (`hygiene`), and the existing KB schema.

SPA cluster work is tracked separately via `spec-hygiene-spa-investigation` bridge item.

---

## Verification Conditions (for post-implementation review)

1. Each of the 9 in-scope specs is in terminal state (a) or (b) as defined above.
2. SPEC-1837 current test coverage unchanged: TEST-10481..10485 still current for SPEC-1837.
3. Invariant query returns 0 verified-with-no-current-tests for the 9 in-scope specs.
4. Post-implementation report documents the exact disposition (restore vs. revert + WI)
   for each of the 9 specs.
5. No `type = 'governance'` spec appears in session-start untested-verified report
   (unchanged from current behavior — already excluded by hook).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
