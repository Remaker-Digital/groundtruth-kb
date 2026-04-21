# Proposal (Revised): Control Plane Spec Status Remediation

**Author:** Prime Builder (Sonnet 4.6, session S293)
**Date:** 2026-04-15
**Status:** REVISED — addresses NO-GO at `bridge/spec-hygiene-spa-remediation-002.md`
**Type:** Remediation proposal
**Prior art:** `bridge/spec-hygiene-spa-investigation-001..008.md` (VERIFIED at -008)
**NO-GO addressed:** `bridge/spec-hygiene-spa-remediation-002.md`

---

## Prior Deliberations

No DELIB-IDs for this remediation track. All prior deliberation is in the
investigation bridge thread: `bridge/spec-hygiene-spa-investigation-001..008.md`.

---

## NO-GO Findings Resolution

### Finding 1 — Proposal relied on a closure that was not VERIFIED

**Status: RESOLVED.** `bridge/spec-hygiene-spa-investigation-008.md` marks the
investigation VERIFIED. The closure WI (WI-3183 v2) was confirmed to include
the bridge thread reference `bridge/spec-hygiene-spa-investigation-001..006.md`.

### Finding 2 — Audit text did not match actual spec titles

**Status: RESOLVED.** The affected-spec table below uses exact current KB titles.
The cluster label has been changed from "SPA Console specs" to "control-plane
placeholder-test remediation cluster" — a neutral descriptor that applies accurately
to all 10 specs regardless of their individual scope. Per-spec change reasons in
§Recommended Action reference each spec's exact title.

---

## Background

The control-plane placeholder-test remediation cluster (10 specs) is currently
`verified` in the KB but has zero current test linkage. The S291 investigation
(VERIFIED at `bridge/spec-hygiene-spa-investigation-008.md`) confirmed root cause:
S198 created placeholder test rows for these specs; S200 recycled those test IDs
for SPEC-1837 (Log Retention). The specs were never backed by real executable tests
in this repository.

### Affected Specs (exact current KB titles)

| Spec ID | Current status | KB test links | Exact KB title |
|---------|---------------|---------------|----------------|
| SPEC-1816 | verified | 0 | Superadmin Entitlement Management API |
| SPEC-1818 | verified | 0 | SPA Console: Full Service Management |
| SPEC-1819 | verified | 0 | SPA Console: Code-Free Runtime Configuration |
| SPEC-1820 | verified | 0 | Allow/Block List Management |
| SPEC-1821 | verified | 0 | Back-off and Retry Configuration |
| SPEC-1822 | verified | 0 | Alert Threshold Configuration |
| SPEC-1823 | verified | 0 | Notification Channel Configuration |
| SPEC-1824 | verified | 0 | Feature Flag System |
| SPEC-1826 | verified | 0 | SPA Test Execution Trigger |
| SPEC-1827 | verified | 0 | Diagnostic Data Export for Claude Code |

### Preservation Constraint

All 35 current SPEC-1837 Test rows are a protected baseline and MUST NOT be
touched by this remediation:

```
TEST-10452..TEST-10454  (last_result=None, no file)
TEST-10475..TEST-10506  (last_result=pass, test_file present)
Total: 35 rows — must remain unchanged.
Baseline: current_rows=35, pass_count=32, with_file=32
```

---

## Options

### Option A — Revert to `implemented` + create hygiene WI (recommended)

**What:** Update each of the 10 specs from `verified` to `implemented` using
`db.update_spec()`. Create one bulk hygiene WI referencing all 10.

**Why recommended:** The `verified` status is factually incorrect — there is no
executable test evidence linked to these specs in the KB. `implemented` accurately
reflects that the features exist in code but lack KB-registered test evidence.
Consistent with GOV-08 (KB is truth).

**KB writes:**
- 10 spec updates (one new version row per spec, `status: verified → implemented`)
- 1 bulk hygiene WI

**Owner escalation required?** No — spec status downgrade from unsubstantiated
`verified` to `implemented` is within Prime's autonomous hygiene scope.

**Risk:** Low. Append-only versioning; the historical `verified` versions remain
in the DB. Reverts are recoverable via another status update.

### Option B — Register external Playwright evidence in KB

Deferred. Requires owner decision on Playwright suite registration. Not recommended
in this proposal.

---

## Recommended Action (Option A)

1. Call `db.update_spec()` for each of the 10 specs with exact per-spec change reasons:

   | Spec ID | `change_reason` |
   |---------|-----------------|
   | SPEC-1816 | `control-plane placeholder-test remediation: Superadmin Entitlement Management API — S198 placeholder recycled by S200; no current KB test linkage. bridge/spec-hygiene-spa-remediation-003.md` |
   | SPEC-1818 | `control-plane placeholder-test remediation: SPA Console: Full Service Management — S198 placeholder recycled by S200; no current KB test linkage. bridge/spec-hygiene-spa-remediation-003.md` |
   | SPEC-1819 | `control-plane placeholder-test remediation: SPA Console: Code-Free Runtime Configuration — S198 placeholder recycled by S200; no current KB test linkage. bridge/spec-hygiene-spa-remediation-003.md` |
   | SPEC-1820 | `control-plane placeholder-test remediation: Allow/Block List Management — S198 placeholder recycled by S200; no current KB test linkage. bridge/spec-hygiene-spa-remediation-003.md` |
   | SPEC-1821 | `control-plane placeholder-test remediation: Back-off and Retry Configuration — S198 placeholder recycled by S200; no current KB test linkage. bridge/spec-hygiene-spa-remediation-003.md` |
   | SPEC-1822 | `control-plane placeholder-test remediation: Alert Threshold Configuration — S198 placeholder recycled by S200; no current KB test linkage. bridge/spec-hygiene-spa-remediation-003.md` |
   | SPEC-1823 | `control-plane placeholder-test remediation: Notification Channel Configuration — S198 placeholder recycled by S200; no current KB test linkage. bridge/spec-hygiene-spa-remediation-003.md` |
   | SPEC-1824 | `control-plane placeholder-test remediation: Feature Flag System — S198 placeholder recycled by S200; no current KB test linkage. bridge/spec-hygiene-spa-remediation-003.md` |
   | SPEC-1826 | `control-plane placeholder-test remediation: SPA Test Execution Trigger — S198 placeholder recycled by S200; no current KB test linkage. bridge/spec-hygiene-spa-remediation-003.md` |
   | SPEC-1827 | `control-plane placeholder-test remediation: Diagnostic Data Export for Claude Code — S198 placeholder recycled by S200; no current KB test linkage. bridge/spec-hygiene-spa-remediation-003.md` |

   Common fields for all 10:
   - `status='implemented'`
   - `changed_by='Claude/S293'`

2. Create 1 bulk hygiene WI:
   - `title='control-plane placeholder-test remediation: revert 10 specs from verified to implemented — no KB test linkage after S200 placeholder recycling'`
   - `origin='hygiene'`
   - `component='knowledge-db'`
   - `source_spec_id='SPEC-1816'`
   - `description` includes all 10 spec IDs and exact titles, bridge reference

3. Write post-implementation report (`spec-hygiene-spa-remediation-004.md`) citing:
   - All 10 spec IDs, exact titles, old and new version/status
   - Bulk WI ID
   - Confirmation SPEC-1837 baseline unchanged (35 rows, 32 pass, 32 with file)
   - Assertion hook output

---

## Verification Conditions

1. 10 spec status updates written (`verified → implemented`), version incremented per spec.
2. 1 bulk hygiene WI created with correct origin/component/source_spec.
3. SPEC-1837 baseline unchanged: 35 current rows, pass_count=32, with_file=32.
4. DB hash changed (expected — writes occurred).
5. Assertion hook output reports no new unexpected failures.

---

## Out of Scope

- Modifying SPEC-1837 rows — forbidden.
- Creating test artifacts for these specs — deferred to separate testing WIs.
- Registering external Playwright evidence — deferred (Option B, owner decision required).
- The 38 `implemented` specs with historical-only evidence — separate proposal.
- The 943 phantom-passing tests — separate proposal.

---

## Decision Needed From Owner

**None for Option A.** The revert is hygiene-only: correcting status from
unsubstantiated `verified` to honest `implemented`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
