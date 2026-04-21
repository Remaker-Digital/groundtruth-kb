# POR Step 16.C — Implemented-Untested Spec Remediation (Umbrella Proposal)

**Status:** NEW (umbrella proposal for Codex review)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-16
**Session:** S297
**Repo:** Agent Red Customer Engagement (groundtruth.db)
**Bridge thread:** por-step16c-implemented-untested-remediation

## Prior Deliberations

- `DELIB-0711` (S297): SPEC-GTKB-SCOPE owner-approved exception from test-evidence invariant.
- `DELIB-0712` (S297): Methodology review pending (auto-archived by 16.B VERIFIED flow).
- `DELIB-0713` (S297): **Owner decisions on 16.C scope** — Option B (multi-stream), Stream E dissolved into D, parallel execution.

Relevant bridge precedent:
- `bridge/por-step16a-verified-spec-closure-010.md` (VERIFIED): Phase 16.A pattern for evidence + invariant closure.
- `bridge/por-step16b-methodology-review-006.md` (VERIFIED): classification producing this proposal's scope.

## Objective

Execute POR Step 16.C — remediate the 193 implemented-untested requirements
identified by the 16.B methodology review. Per `DELIB-0713`, the work runs
as **four parallel sub-streams**, each with its own bridge proposal and
GO/VERIFY cycle. This umbrella proposal:

1. Establishes the shared exit criteria for 16.C as a whole
2. Defines the boundaries between streams (no double-counting)
3. Sequences the sub-bridge proposals (A/B/C/D)
4. Records the expected post-16.C state

## Scope Source

All 193 specs and their categories come from the machine-generated inventory:
`independent-progress-assessments/spec-hygiene/S297-phase16b-target-inventory.json`.

Category totals from `DELIB-0713`:
- α' (alpha_prime): 151 → Stream A
- β' (beta_prime): 4 → Stream C
- γ' (gamma_prime): 19 → Stream D (base)
- δ' (delta_prime): 15 → Stream D (expanded per Decision 2)
- ζ' (zeta_prime): 4 → Stream B

Stream D total: 19 + 15 = **34 specs**.

## Stream Definitions

### Stream A — α' test refresh (151 specs)

**Goal:** Specs have real, running tests that went stale. Re-run them and
clear stale flags so the specs regain "tested" status.

**Key action:** For each α' spec, locate the linked historical test by
`test_file` path, confirm it exists on disk, run it, and if it passes,
update the test row's `last_result` from `stale` to `pass`.

**Bridge thread:** `por-step16c-stream-a-alpha-refresh`

**Effort:** 1 session (mostly mechanical via classifier output + pytest
loop).

**Risk:** Some tests may have bit-rotted silently (passed when added but
fail against current code). Those specs need re-classification: pass
stays at implemented+tested; fail moves to Stream C-like repair queue.

### Stream B — ζ' test-ID reassignment triage (4 specs)

**Goal:** Specs whose linked tests had their `spec_id` rewritten to point
elsewhere. Determine root cause (legitimate refactor vs. corruption) and
re-link or retire.

**Key action:** For each of the 4 ζ' specs, inspect the history of each
reassigned test row and decide: re-link spec to current test, create new
test, or retire the spec.

**Bridge thread:** `por-step16c-stream-b-zeta-triage`

**Effort:** 0.5 session (manual triage).

**Ancillary:** The 16.B review proposed a schema invariant forbidding
`spec_id` changes in test rows (force new `test_id` instead). That schema
work is **out of scope for 16.C** but should be spun off as a WI.

### Stream C — β' broken-path triage (4 specs)

**Goal:** Specs whose linked tests reference `test_file` paths that no
longer exist on disk. Repair or retire.

**Key action:** For each β' spec, search the repo for the test (may have
moved), or create a new test per GOV-10, or retire the spec.

**Bridge thread:** `por-step16c-stream-c-beta-triage`

**Effort:** 0.5 session (manual triage).

### Stream D — γ' + δ' bulk WI creation (34 specs)

**Goal:** Specs with no legitimate test evidence ever (γ'), plus specs the
owner decided not to grant assertion-only verification policy to (δ',
per DELIB-0713 Decision 2). Create hygiene WIs for each requiring real
test coverage per GOV-10.

**Key action:** Bulk-create 34 hygiene WIs following the Phase 1.5 β
pattern (see `spec-hygiene-untested-verified-008` VERIFIED). Each WI
sourced to its spec with `origin=hygiene`.

**Bridge thread:** `por-step16c-stream-d-phantom-wi-creation`

**Effort:** 0.5 session (scriptable via classifier JSON).

**Note:** These specs remain at `implemented` status (no status change).
The WI creation records the test-coverage gap for future remediation.

## Coordination & Exit Criteria

### Umbrella-level exit criteria

1. All four sub-stream bridges have VERIFIED post-impl reports.
2. Per-category remediation counts reconcile against DELIB-0713:
   - Stream A: 151 α' specs have refreshed test evidence OR are escalated
     to Stream C (moved count reported).
   - Stream B: 4 ζ' specs have a terminal decision (re-linked, new test,
     or retired).
   - Stream C: Final count = 4 β' + α'-escalations, all with terminal
     decisions.
   - Stream D: 34 hygiene WIs open, 1:1 linkage to source specs.
3. DELIB-0714+ archives the consolidated 16.C results and any ancillary
   WIs spun off (schema invariant proposal, case-inconsistency fix).
4. `docs/plans/PLAN-OF-RECORD-production-readiness.md` updated: Phase
   16.C marked COMPLETE with per-stream summary.

### Count reconciliation invariant

After 16.C:
- Implemented-untested requirement count ≤ 193 − 151 + (α'-escalation
  count) = reported in post-impl report.
- In the ideal case (all α' refresh cleanly), count drops to 193 − 151 =
  42 (4 β' + 4 ζ' + 34 D).
- Stream A + Stream C + Stream B + Stream D combined resolution must
  cover all 193 original specs.

### Parallel execution protocol

Each sub-stream proceeds independently:
1. Prime drafts sub-stream proposal (`por-step16c-stream-{x}-*-001.md`).
2. Codex reviews → GO.
3. Prime implements → post-impl report.
4. Codex reviews → VERIFIED.
5. Sub-stream done.

Umbrella thread updates after each VERIFIED:
- Prime posts a REVISED version of THIS proposal noting which sub-streams
  are complete and their counts.
- After all four are VERIFIED, Prime posts a NEW post-impl umbrella
  report consolidating results.
- Codex VERIFIES the umbrella.
- POR Step 16.C marked COMPLETE.

## Sub-Stream Proposal Sequencing

Even though execution is parallel, proposals can't all be posted
simultaneously without overwhelming Codex. Recommended posting order:

1. **Stream D first** (most mechanical, batch WI creation) — posted
   alongside this umbrella.
2. **Stream A second** (largest scope, batch test refresh) — posted
   after Stream D GO.
3. **Streams B and C** (small, manual triage) — posted after A GO or
   in parallel if Codex has capacity.

Umbrella GO must land before any sub-stream GO can be honored, so the
effective order is:

```
Umbrella NEW → Codex GO
              ↓
Stream D NEW → Stream A NEW → Streams B/C NEW
   ↓              ↓              ↓
  GO             GO             GO
   ↓              ↓              ↓
Impl           Impl           Impl
   ↓              ↓              ↓
VERIFIED       VERIFIED       VERIFIED
                  ↓
            Umbrella post-impl → VERIFIED
```

## Files Changed (umbrella-level)

This umbrella proposal itself is read-only. Sub-streams will modify:

| Scope | Files | Change |
|-------|-------|--------|
| Stream A | `tests/**` + `groundtruth.db` | Re-run tests; update `last_result` for refreshed test rows |
| Stream B | `groundtruth.db` | Spec status + test linkage updates |
| Stream C | `tests/**` + `groundtruth.db` | Path repairs, new tests, or spec status updates |
| Stream D | `groundtruth.db` | 34 new WIs inserted with `origin=hygiene` |
| Umbrella | `docs/plans/PLAN-OF-RECORD-production-readiness.md` + DELIB | Mark 16.C complete, archive results |

## Risks (umbrella-level)

- **Low:** All sub-streams are scoped from machine-generated classifier
  output (16.B); no double-counting between streams.
- **Low:** α'-to-C escalation (bit-rotted tests) has a clear handoff
  path; Stream C tracks the expanded count.
- **Medium:** Parallel execution means Prime coordinates four concurrent
  bridge threads. Mitigation: umbrella thread acts as index; each
  sub-stream's proposal cites the umbrella as context.
- **Medium:** Stream A's test-refresh may reveal production bugs (tests
  fail, not pass). Escalation: such specs move to Stream C, and the
  post-impl report flags each as a new finding (not a regression since
  the test was already stale).

## Exit Criteria (umbrella)

1. All four sub-stream bridges VERIFIED.
2. Reconciled per-stream counts reported in umbrella post-impl.
3. DELIB archives consolidated 16.C results + ancillary WIs.
4. POR file updated marking 16.C COMPLETE.
5. Any α'-to-C escalations documented with root cause (bit-rot, env
   drift, etc.).

## Ancillary WIs Spun Off (expected)

These are NOT 16.C deliverables but are surfaced by the work:

1. **Schema invariant: forbid `spec_id` changes on test rows** — emerged
   from 16.B's ζ' finding. Would prevent future drift.
2. **Case-normalization for `last_result` values** — `stale`/`STALE`,
   `PASS`/`pass` inconsistency noted in 16.B.
3. **Production bug WIs** — any Stream A test-refresh failures that
   reveal real regressions (one WI per failure).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
