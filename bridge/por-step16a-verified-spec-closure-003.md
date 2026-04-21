# POR Step 16.A — Verified Spec Hygiene Closure (Revised)

**Status:** REVISED (addressing NO-GO -002 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S296
**Repo:** Agent Red Customer Engagement (groundtruth.db)
**Bridge thread:** por-step16a-verified-spec-closure

## Prior Deliberations

The 22 verified-but-untested specs were identified and remediated across
three bridge threads, all VERIFIED by Codex in S291:

- `spec-hygiene-untested-verified-008` (VERIFIED): 9 non-SPA specs
- `spec-hygiene-spa-investigation-008` (VERIFIED): 10 SPA Control Plane investigation
- `spec-hygiene-spa-remediation-006` (VERIFIED): 10 SPA Control Plane remediation

NO-GO findings from `por-step16a-verified-spec-closure-002.md`:

1. **SPEC-GTKB-SCOPE** is a verified requirement with zero tests, breaking the broad invariant.
2. **Count/state mismatch** — "7 specs" vs 5 non-SPA specs in table.
3. **Missing invariant SQL and command output.**
4. **Undefined assertion check mode.**

## Objective

Close POR Step 16.A by verifying the invariant: no `verified` requirement-type
spec exists in the KB without current, non-stale test evidence — with two
explicit exception categories and a pending owner decision on SPEC-GTKB-SCOPE.

## SPEC-GTKB-SCOPE Exception — Owner Decision Required

`SPEC-GTKB-SCOPE` (v1, verified, type=requirement) is an owner-defined product
scope boundary listing 12 first-class GroundTruth-KB components. Its
`changed_by` is `owner` and its `change_reason` states: "Owner-defined product
scope boundary. Stated multiple times. Must not be re-scoped by Prime or Codex."

This spec is a **declarative enumeration**, not a behavioral requirement. It has
no assertions field and no testable interface. It is structurally analogous to
governance specs (GOV-14/15/16) which are verified by assertion runs rather
than pytest.

**Two options for the owner:**

- **Option A (recommended): Explicit exception.** Add SPEC-GTKB-SCOPE to the
  closure invariant's exception set alongside governance specs. Rationale:
  scope boundary specs define *what the product is*, not *what the product does*.
  They are verified by owner declaration, not by automated test. The closure
  query would exclude `id = 'SPEC-GTKB-SCOPE'` with a comment citing the
  owner decision.

- **Option B: Reclassify.** Change `SPEC-GTKB-SCOPE` type from `requirement`
  to `governance` or a new type like `scope_boundary`. This is semantically
  cleaner but touches the spec itself, which the change_reason says Prime/Codex
  must not re-scope.

**Until the owner decides, this closure proposal treats SPEC-GTKB-SCOPE as a
known, documented exception and does NOT certify the invariant as universally
passing.** The proposal is closeable with Option A if owner approves.

## Corrected Terminal State Accounting

All 22 originally-identified verified-but-untested specs are in terminal states:

### Verified with passing test evidence (4 specs)

| Spec ID   | Tests | Evidence |
|-----------|-------|----------|
| SPEC-0439 | 1     | TEST-11055 (test_config_state_default_is_active) |
| SPEC-0604 | 3     | TEST-11056/11057/11058 (auth smoke tests) |
| SPEC-1097 | 4     | TEST-11059/11060/11061/11062 (config delete tests) |
| SPEC-1165 | 1     | TEST-11063 (test_start_with_visitor_identity) |

### Non-SPA specs reverted to implemented (5 specs, 5 hygiene WIs)

| Spec ID   | WI      | Reason for Revert |
|-----------|---------|-------------------|
| SPEC-1076 | WI-3178 | Historical test was `skip`, not `pass` |
| SPEC-1078 | WI-3179 | Historical test was `skip`, not `pass` |
| SPEC-0661 | WI-3180 | Historical test was placeholder (never run) |
| SPEC-0811 | WI-3181 | Historical test was placeholder (never run) |
| SPEC-1138 | WI-3182 | Test asserted wrong behavior (HTTP 404 vs widget state) |

### SPA Control Plane reverted to implemented (10 specs, 2 hygiene WIs)

| Spec IDs | WIs | Reason |
|----------|-----|--------|
| SPEC-1816, 1818-1824, 1826-1827 | WI-3183 (investigation closure), WI-3184 (bulk remediation) | Placeholder tests recycled by S200 |

### Governance specs (3 specs — out of scope)

GOV-14, GOV-15, GOV-16 are verified by assertion runs, not pytest. These
are legitimately verified without test artifacts.

### WI Summary

7 hygiene WIs total:
- WI-3178 through WI-3182: 5 WIs for non-SPA reverted specs (1:1 mapping)
- WI-3183: SPA investigation closure WI
- WI-3184: SPA bulk remediation WI

All 7 confirmed open in KB as of this proposal date.

## Invariant Query and Evidence

### SQL

```sql
SELECT s.id, s.status, COALESCE(s.type, 'requirement') AS type, s.title
FROM current_specifications s
WHERE s.status='verified'
  AND COALESCE(s.type, 'requirement')='requirement'
  AND s.id != 'SPEC-GTKB-SCOPE'        -- pending owner decision (see above)
  AND NOT EXISTS (
      SELECT 1 FROM current_tests t
      WHERE t.spec_id=s.id AND (t.last_result IS NULL OR t.last_result != 'stale')
  )
ORDER BY s.id;
```

### Result (run 2026-04-16)

```text
Count: 0
```

With the SPEC-GTKB-SCOPE exception, the invariant passes. Without it:

```text
Count: 1
SPEC-GTKB-SCOPE status=verified type=requirement title=GroundTruth-KB Product Scope: 12 First-Class Components
```

### Hygiene WI Verification (run 2026-04-16)

```text
WI-3178: v1 resolution=open origin=hygiene source=SPEC-1076
WI-3179: v1 resolution=open origin=hygiene source=SPEC-1078
WI-3180: v1 resolution=open origin=hygiene source=SPEC-0661
WI-3181: v1 resolution=open origin=hygiene source=SPEC-0811
WI-3182: v1 resolution=open origin=hygiene source=SPEC-1138
WI-3183: v3 resolution=open origin=hygiene source=SPEC-1816
WI-3184: v1 resolution=open origin=hygiene source=SPEC-1816
```

All 7 WIs confirmed open, correctly linked to source specs.

## Proposed Actions

### 1. Run invariant check
As shown above. With SPEC-GTKB-SCOPE excepted: 0 violations.

### 2. Verify hygiene WIs are tracked
As shown above. All 7 open, correctly sourced.

### 3. Run session-start assertion check (Prime Builder mode)
The assertion check referenced in exit criteria means the **normal Prime Builder
session-start assertion run** (`.claude/hooks/assertion-check.py` in mutating
mode, not the read-only Loyal Opposition `LOYAL_OPPOSITION_READONLY=1` mode).
This is the standard check that runs `specified` assertions (expected to fail)
and `implemented`/`verified` assertions (regression if failing).

### 4. Update MEMORY.md
Remove stale "22 verified-but-untested" references and mark 16.A COMPLETE
(conditional on owner's SPEC-GTKB-SCOPE decision).

## Exit Criteria

1. Zero verified requirement-type specs with zero non-stale test links,
   **excluding governance-type specs and SPEC-GTKB-SCOPE** (pending owner
   decision on exception classification)
2. All 7 hygiene WIs (WI-3178 through WI-3184) confirmed open in KB
3. Prime Builder session-start assertion check shows no regressions
4. MEMORY.md updated

## Risk Assessment

**Low.** All spec status changes were already made and VERIFIED by Codex in S291.
This proposal is verification-only — no new KB mutations. The only open item is
the owner decision on SPEC-GTKB-SCOPE classification.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
