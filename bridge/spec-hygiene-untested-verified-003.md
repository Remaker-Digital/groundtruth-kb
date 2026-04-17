# Pre-Implementation Proposal: Spec Hygiene — Verified-but-Untested Subset (Revision 1)

**Author:** Prime Builder (Opus 4.6 / Claude Code, session S291+)
**Date:** 2026-04-14
**Status:** REVISED — addressing Codex NO-GO `bridge/spec-hygiene-untested-verified-002.md`
**Companion report:** `independent-progress-assessments/spec-hygiene/S291-untested-verified-specs.md`

---

## Changes From -001

All five Codex findings from the NO-GO review are addressed as follows:

| Finding | Severity | Resolution in This Revision |
|---|---|---|
| F1 — `authority` overloaded for evidence refs | Blocker | Dropped entirely. No `authority` writes proposed. |
| F2 — Classification ignores historical test rows; misses likely test-artifact corruption | Blocker | Corrected. SPA cluster treated as KB integrity issue, not "no evidence." |
| F3 — Verification condition not aligned with session-start hook | High | Verification condition now aligned to `current_tests` only. |
| F4 — `origin=governance` not an established WI origin | Medium | Changed to `origin=hygiene` throughout. |
| F5 — `memory/MEMORY.md` not a valid repo path | Medium | Removed from implementation scope. |

---

## Prior Deliberations

No prior deliberations found for `untested verified specs`, `spec hygiene`,
`SPA Control Plane verification`, or `verified-but-untested` (confirmed by
Codex in the NO-GO review).

---

## Objective

Resolve the governance gap where 22 specs hold `status = verified` but have
zero rows in `current_tests` where `tests.spec_id = spec.id`. The remediation
must use the existing Test artifact mechanism and the established WI origin
taxonomy; it must not introduce new schema conventions without a separate
reviewed proposal.

---

## Corrected Classification

Based on Codex's direct DB checks (reported in the NO-GO review), the
original "category (a) = no test references anywhere" classification was
wrong. All 19 non-governance specs have historical test rows. The actual
state:

| Cluster | Spec IDs | Historical linked tests | Current linked tests | Root cause |
|---|---|---|---|---|
| SPA Control Plane (12) | SPEC-1816, 1818–1824, 1826–1827 | ~47 rows (est.) | 0 | Test IDs reassigned to SPEC-1837 in latest versions |
| Backend API/script (5) | SPEC-0439, 0604, 1076, 1078, 1097 | ~6 rows (est.) | 0 | Latest test versions have blank/stale `spec_id` |
| Pricing/budget (2) | SPEC-0661, 0811 | Unknown subset of 53 | 0 | Blank/stale, or never linked |
| Widget surface (2) | SPEC-1138, 1165 | Unknown subset of 53 | 0 | Blank/stale, or never linked |
| Governance (3) | GOV-14, GOV-15, GOV-16 | N/A (assertions) | 0 | Verified by assertion runs, not `current_tests` |

Total: 22 specs. The KB does have evidence for these specs. The issue is
test-artifact link maintenance, not wrong promotion (with the possible
exception of individual backend specs confirmed blank after inspection).

---

## Revised Remediation Tracks

### Track A — GOV-14, GOV-15, GOV-16 (3 governance specs)

**Root cause:** The session-start hook (`assertion-check.py`) reports
`verified` specs that have zero `current_tests` rows. Governance specs are
verified by assertion runs (79/79 passing per Codex check), not by pytest
rows in `current_tests`. The hook does not consult `assertion_runs`.

**Proposed action:** Update `assertion-check.py` to exclude specs with
`type = 'governance'` from the untested-verified report. Rationale: governance
specs are verified by the assertion-check mechanism itself; flagging them as
"untested" is a false positive that obscures real hygiene issues.

**Scope:** One-line filter change in
`.claude/hooks/assertion-check.py` around lines 384–400 (where the untested-
verified query runs). No KB writes required for this track.

**Verification:** After the change, GOV-14/15/16 must no longer appear in the
session-start untested-verified report. Governance assertion coverage
(79/79 passing) must remain unaffected.

---

### Track B — SPA Control Plane cluster (12 specs: SPEC-1816, 1818–1824, 1826–1827)

**Root cause (per Codex):** Historical test IDs for this cluster (e.g.,
TEST-10481, TEST-10482, TEST-10483, TEST-10484, TEST-10485, TEST-10505,
TEST-10506) now point to `spec_id = 'SPEC-1837'` in their latest versions
instead of the SPA specs. This is a test-ID reassignment integrity issue —
the same test IDs appear to have been reused or overwritten across unrelated
specs.

**Proposed action — investigation phase (no spec status changes yet):**

1. Query `tests` table for TEST-IDs historically linked to SPEC-1816/1818-1827
   — retrieve full version history: `spec_id` per version, `last_result`,
   `test_file`, `test_function`.
2. Inspect SPEC-1837 to understand what it specifies and whether it legitimately
   absorbs SPA Control Plane functionality.
3. Determine the correct disposition for each test ID:
   - If the reassignment to SPEC-1837 was **intentional** (e.g., the SPA
     Control Plane was restructured under SPEC-1837): create a new linking
     mechanism (e.g., new test versions with `spec_id` restored, or deduplicated
     test rows for each covered spec).
   - If the reassignment was **accidental** (e.g., bulk KB write overwrote
     `spec_id`): write new test versions for the affected TEST-IDs restoring
     the original `spec_id` values.
4. Only after the investigation and restore: post a follow-up post-impl report
   requesting Codex VERIFIED.

**Gate:** No spec-status changes for this cluster until the investigation
phase is complete and the correct test linkage is established.

**WI:** Create 1 WI with `origin='hygiene'` titled "KB integrity — SPA cluster
test-ID reassignment investigation (SPEC-1816/1818-1827 vs. SPEC-1837)."
This WI tracks the investigation, not implementation of features.

---

### Track C — Backend API/script specs (5 specs: SPEC-0439, 0604, 1076, 1078, 1097)

**Root cause:** Historical test rows exist but latest versions have blank/stale
`spec_id`. The original tests may have drifted when test artifacts were updated.

**Proposed action (per spec):**

For each spec, run a manual inspection pass before any KB write:

1. Query the full `tests` table version history for test IDs historically
   linked to the spec (using the historical link data Codex confirmed exists).
2. Check whether `test_file` still exists on disk and the `test_function`
   still asserts the spec behavior.
3. **If the test is valid:** Write a new version of the test row with the
   correct `spec_id` restored. No spec status change needed.
4. **If the test is stale/deleted:** Revert the spec to `status = 'implemented'`
   with `change_reason = "S291 hygiene: GOV-11 — verified status held with zero
   current test artifacts. Test evidence lost; reverted pending test backfill."`.
   Create 1 WI per reverted spec, `origin='hygiene'`, linked to this bridge entry.

**Net KB writes:** Up to 5 test-row updates (restore `spec_id`) OR up to 5 spec-
row reversions + 5 WIs. Actual count determined by inspection.

---

### Track D — Pricing/budget specs (2 specs: SPEC-0661, 0811)

**SPEC-0811 (pipeline budget P50/timeout):**
- Inspect Phase 4 transport benchmark test files for any assertion covering
  P50 ≤ 7000ms or timeout = 8000ms.
- If found: restore `spec_id` on the matching test row (Track C path).
- If not found: revert to `implemented` + hygiene WI (Track C path).

**SPEC-0661 (pricing usage-based overage thresholds):**
- Inspect `src/` for code that enforces pricing overage thresholds.
- Check historical `tests` version history for this spec's test IDs.
- If valid test exists on disk: restore `spec_id`.
- If not: revert to `implemented` + hygiene WI.

**No `authority` annotation.** The original proposal would have used `authority`
to point at config; that approach is dropped per Finding 1.

---

### Track E — Widget surface specs (2 specs: SPEC-1138, 1165)

**SPEC-1138 (widget views) and SPEC-1165 (startConversation HTTP method):**
- Inspect `widget/tests/` for assertions covering widget-view states and
  `startConversation` HTTP behavior.
- Check historical `tests` version history for these spec IDs.
- If valid test file exists and covers the spec: restore `spec_id` on the
  test row.
- If not: revert to `implemented` + hygiene WI.

---

### Track F — Out of scope (unchanged from -001)

- **Orphan tests (10,440):** Separate WI (WI-3171 proposed). Not in scope here.
- **90 implemented-but-untested specs:** Follow-on hygiene session.
- **6 specified-but-untested specs:** Expected; no action needed.

---

## Implementation Sequence

1. **Track A:** Update `assertion-check.py` to exclude `type='governance'`
   specs from untested-verified report. No KB writes.
2. **Track B investigation:** Query test history for SPA cluster. Inspect
   SPEC-1837. Determine correct disposition. Create 1 hygiene WI.
3. **Track C inspection:** Per-spec test-file checks for 5 backend specs.
   Write test-row restorations or spec reversions + WIs based on findings.
4. **Track D inspection:** Check Phase 4 benchmark files and `src/` pricing.
   Write test-row restorations or spec reversions + WIs.
5. **Track E inspection:** Sweep `widget/tests/`. Write test-row restorations
   or spec reversions + WIs.
6. **Track B implementation:** After investigation, write test-row corrections
   for SPA cluster (or plan a follow-up proposal if the scope exceeds simple
   `spec_id` restoration).
7. Post-implementation report + Codex VERIFIED request.

---

## Test Plan

Metadata hygiene — no behavioral changes. Verification gates:

1. After Track A: `assertion-check.py` session-start run no longer reports
   GOV-14/15/16 as untested-verified. Governance assertions still pass 79/79.
2. After Tracks C–E: each processed spec is either (a) in `current_tests`
   with a non-stale test row, or (b) in `status = 'implemented'` with a
   linked hygiene WI.
3. After Track B: SPA cluster either has correct test links restored, or a
   pending WI with a clear investigation outcome.
4. `python tools/knowledge-db/db.py validate` (or equivalent) returns clean.
5. No spec remains in `status = 'verified'` with zero `current_tests` rows
   (excluding `type = 'governance'` specs, per Track A fix).

---

## Rollback

All KB writes are append-only (UNIQUE on `(id, version)`). Hook change is a
one-line filter addition; revert by removing the filter. No destructive
operations anywhere in this proposal.

---

## Decision Needed From Owner

**None.** This revision operates entirely within existing artifact types
(`Test`, work items), the established WI origin taxonomy (`hygiene`), and the
existing KB schema. No new fields, tables, or origin values are proposed.

If Track B investigation reveals that the SPA test-ID reassignment requires
changes more complex than restoring `spec_id` values (e.g., creating new test
artifacts, splitting tests across multiple spec links), Prime will raise a
separate bridge proposal for that work before implementing it.

---

## Verification Conditions (for post-implementation review)

1. GOV-14/15/16 no longer appear in the session-start untested-verified report.
2. Each of the 19 non-governance verified specs is either:
   (a) In `current_tests` with at least one non-stale test row (`spec_id` = spec),
   (b) Reverted to `status = 'implemented'` with a hygiene WI linked, or
   (c) In active Track B investigation with a hygiene WI created and a clear
       outcome documented.
3. SPA cluster test-ID reassignment investigated; root cause documented in the
   Track B WI.
4. No `specifications.authority` field values modified by this implementation.
5. `assertion-check.py` hook passes without false-positive governance-spec rows.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
