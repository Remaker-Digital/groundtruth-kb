# POR Step 16.A — Verified Spec Hygiene Closure (Revised)

**Status:** REVISED (addressing NO-GO -004: owner decision now obtained)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** Agent Red Customer Engagement (groundtruth.db)
**Bridge thread:** por-step16a-verified-spec-closure

## Prior Deliberations

The 22 verified-but-untested specs were identified and remediated across
three bridge threads, all VERIFIED by Codex in S291:

- `spec-hygiene-untested-verified-008` (VERIFIED): 9 non-SPA specs
- `spec-hygiene-spa-investigation-008` (VERIFIED): 10 SPA Control Plane investigation
- `spec-hygiene-spa-remediation-006` (VERIFIED): 10 SPA Control Plane remediation

NO-GO history:
- `-002`: Count/state mismatch, missing invariant SQL, undefined assertion mode.
- `-004`: Closure depends on uncited owner decision for SPEC-GTKB-SCOPE.

## Owner Decision: SPEC-GTKB-SCOPE Exception (S297)

**Decision:** Option A — Grant explicit exception.
**Decision maker:** Mike (owner), via interactive prompt in session S297.
**Date:** 2026-04-16
**Context:** Owner was presented three options (A: grant exception, B: add
structural assertion, C: revert to implemented) and chose Option A.

`SPEC-GTKB-SCOPE` (v1, verified, type=requirement, changed_by=owner) is an
owner-defined product scope boundary listing 12 first-class GroundTruth-KB
components. Its `change_reason` states: "Owner-defined product scope boundary.
Stated multiple times. Must not be re-scoped by Prime or Codex."

**Rationale for exception:** This spec is a declarative enumeration defining
*what the product is*, not *what the product does*. It has no assertions field
and no testable interface. It is structurally analogous to governance specs
(GOV-14/15/16) which are verified by assertion runs rather than pytest. Scope
boundary specs are verified by owner declaration, not by automated test.

The invariant SQL permanently excludes `SPEC-GTKB-SCOPE` with a comment citing
this owner decision. This resolves the sole NO-GO -004 blocker.

## Objective

Close POR Step 16.A by verifying the invariant: no `verified` requirement-type
spec exists in the KB without current, non-stale test evidence — with two
explicit exception categories:

1. **Governance specs** (GOV-14/15/16): verified by assertion runs, not pytest.
2. **SPEC-GTKB-SCOPE**: owner-approved exception (scope boundary declaration,
   not behavioral requirement). Decision obtained S297.

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

### Owner-approved exception (1 spec)

SPEC-GTKB-SCOPE: Owner-defined scope boundary. Exception granted S297.
No testable assertions; verified by owner declaration.

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
  AND s.id != 'SPEC-GTKB-SCOPE'        -- owner-approved exception (S297)
  AND NOT EXISTS (
      SELECT 1 FROM current_tests t
      WHERE t.spec_id=s.id AND (t.last_result IS NULL OR t.last_result != 'stale')
  )
ORDER BY s.id;
```

### Result (verified by Codex -004)

With owner-approved exception: **0 violations.**

### Hygiene WI Verification (verified by Codex -004)

All 7 WIs (WI-3178 through WI-3184) confirmed open and correctly linked.

## Proposed Actions

### 1. Run invariant check
With SPEC-GTKB-SCOPE excepted (owner-approved S297): 0 violations.

### 2. Verify hygiene WIs are tracked
All 7 open, correctly sourced. Re-verify at execution time.

### 3. Update SPEC-GTKB-SCOPE change_reason
Append exception citation: "Exception from test-evidence invariant granted
by owner in S297 (scope boundary declaration, not behavioral requirement)."

### 4. Run session-start assertion check (Prime Builder mode)
Normal Prime Builder assertion run (`.claude/hooks/assertion-check.py` in
mutating mode). Confirm no regressions from `implemented`/`verified` assertions.

### 5. Update MEMORY.md
Remove stale "22 verified-but-untested" references. Mark 16.A COMPLETE.

## Exit Criteria

1. Zero verified requirement-type specs with zero non-stale test links,
   excluding governance-type specs and SPEC-GTKB-SCOPE (owner-approved
   exception, S297)
2. All 7 hygiene WIs (WI-3178 through WI-3184) confirmed open in KB
3. SPEC-GTKB-SCOPE change_reason updated with exception citation
4. Prime Builder assertion check shows no regressions
5. MEMORY.md updated

## Risk Assessment

**Low.** All spec status changes were made and VERIFIED by Codex in S291.
This proposal is primarily verification-only — the only KB mutation is
updating SPEC-GTKB-SCOPE's change_reason with the exception citation.
The owner decision has been obtained and is cited above.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
