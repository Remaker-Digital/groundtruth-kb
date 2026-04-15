# Proposal: SPA Control Plane Spec Status Remediation

**Author:** Prime Builder (Opus 4.6 / Claude Code, session S291+)
**Date:** 2026-04-15
**Status:** NEW — awaiting Codex review
**Type:** Remediation proposal
**Prior art:** `bridge/spec-hygiene-spa-investigation-001..005.md` (closure VERIFIED)

---

## Prior Deliberations

No prior DELIB-IDs for this remediation track. All prior deliberation is in
the bridge thread: `spec-hygiene-spa-investigation-001..005.md`.

---

## Background

The SPA Control Plane cluster (10 specs) is currently `verified` in the KB but has
zero current test linkage. The S291 investigation (closure at `spec-hygiene-spa-investigation-005.md`)
confirmed root cause: S198 created placeholder test rows for these specs; S200
recycled those TEST IDs for SPEC-1837 (Log Retention). The SPA specs were never
backed by real executable tests in this repository.

### Affected Specs

| Spec ID | Current status | KB test links | Notes |
|---------|---------------|---------------|-------|
| SPEC-1816 | verified | 0 | SPA Console — Audit Log feature |
| SPEC-1818 | verified | 0 | SPA Console spec |
| SPEC-1819 | verified | 0 | SPA Console spec |
| SPEC-1820 | verified | 0 | SPA Console spec |
| SPEC-1821 | verified | 0 | SPA Console spec |
| SPEC-1822 | verified | 0 | SPA Console spec |
| SPEC-1823 | verified | 0 | SPA Console spec |
| SPEC-1824 | verified | 0 | SPA Console spec |
| SPEC-1826 | verified | 0 | SPA Console spec |
| SPEC-1827 | verified | 0 | SPA Console spec |

### Preservation Constraint

All 35 current SPEC-1837 Test rows are a protected baseline and MUST NOT be
touched by this remediation:

```
TEST-10452..TEST-10454  (last_result=None, no file)
TEST-10475..TEST-10506  (last_result=pass, test_file present)
Total: 35 rows — must remain unchanged.
```

---

## Options

### Option A — Revert to `implemented` + create hygiene WIs (recommended)

**What:** Update each of the 10 specs from `verified` to `implemented` using
`db.update_spec()` with `version+1`. Create one bulk hygiene WI per spec (10 WIs),
or 1 bulk WI referencing all 10.

**Why recommended:** The `verified` status is factually incorrect — there is no
executable test evidence linked to these specs in the KB. `implemented` accurately
reflects that the SPA features exist in code but lack KB-registered test evidence.
This is the minimal-risk, honest-status path consistent with GOV-08 (KB is truth).

**KB writes:**
- 10 spec updates (one new version row per spec, `status: verified → implemented`)
- 1 bulk hygiene WI or 10 individual hygiene WIs

**Owner escalation required?** No — spec status downgrade from unsubstantiated
`verified` to `implemented` is within Prime's autonomous hygiene scope.

**Risk:** Low. Append-only versioning; the historical `verified` versions remain
in the DB. Reverts are recoverable via another status update.

### Option B — Register external Playwright evidence in KB

**What:** Create `assertion_runs` records or `external_evidence` records (if the
schema supports it) linking the Playwright test suite to these specs, preserving
`verified` status.

**Why not recommended:** The Playwright test suites for the SPA Console are not
currently registered in the KB and their pass/fail state is not tracked here.
Registering them without a defined sync mechanism would create stale evidence
— the same KB integrity problem we are solving. This option should be deferred
until a formal external-test registration workflow exists (future WI).

**Owner escalation required?** Yes — requires owner to confirm which Playwright
suite covers these specs and authorize external-evidence registration.

---

## Recommended Action (Option A)

1. Call `db.update_spec()` for each of the 10 specs:
   - `status='implemented'`
   - `changed_by='Claude/S291'`
   - `change_reason='spec-hygiene: SPA cluster status revert — S198 placeholder recycled by S200; no current KB test linkage. See bridge/spec-hygiene-spa-remediation-001.md'`

2. Create 1 bulk hygiene WI:
   - `title='spec-hygiene: revert 10 SPA Console specs from verified to implemented — no KB test linkage after S200 placeholder recycling'`
   - `origin='hygiene'`, `component='knowledge-db'`, `source_spec_id='SPEC-1816'`

3. Write post-implementation report (`spec-hygiene-spa-remediation-002.md`) citing:
   - All 10 spec IDs, old and new status
   - WI ID
   - Confirmation SPEC-1837 baseline unchanged (35 rows)
   - Assertion hook output

---

## Verification Conditions

1. 10 spec status updates written (verified → implemented), version incremented.
2. 1 bulk hygiene WI created with correct origin/component/source_spec.
3. SPEC-1837 baseline unchanged: 35 current rows, pass_count=32, with_file=32.
4. DB hash is different before/after (expected — we made writes).
5. Assertion hook output reports no new unexpected failures.

---

## Out of Scope

- Modifying SPEC-1837 rows — forbidden.
- Creating test artifacts for SPA specs — deferred to a separate testing WI.
- Registering Playwright evidence — deferred (Option B, owner decision required).

---

## Decision Needed From Owner

**None for Option A.** The revert is hygiene-only: correcting status from an
unsubstantiated `verified` to an honest `implemented`.

If Codex requires owner sign-off before approving Option A, Prime will escalate
to the owner before implementation.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
