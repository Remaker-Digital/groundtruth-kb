NEW

# POR Step 16.D — Phantom Spec-Link Cleanup + Baseline Correction (F2 Phase 1)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Backlog Slot:** F2 (POR 16.D orphan test rationalization), Phase 1 of 2
**Prior POR reference:** `docs/plans/PLAN-OF-RECORD-production-readiness.md:184-213` (Step 16.D)

## Why this is a 2-phase bridge (not deferral)

Per `memory/feedback_no_deferrals_ever.md`, work is never deferred; only
dependency-ordered. Phantom-link cleanup is a **precondition** for manual
triage: you cannot triage a test when its `spec_id` column is a deterministic
lie. Phase 1 converts phantom links to real orphan state; Phase 2 triages the
resulting unified orphan pool. Each phase is a distinct, verifiable unit;
Phase 2 filed as a follow-on bridge after Phase 1 VERIFIED.

## Owner pre-approval basis

`memory/work_list.md` POR Step 16.D ownership note: "Phase 16.D (orphan
tests) may be delegated to a subagent or scripted where the linkage inference
is tractable." Owner S302 work-through approval covers F2.

## Observed Baseline Discrepancy

POR §Step 16.D states "10,440 orphan tests of 11,066 total (94.3%)." Live
KB query (run 2026-04-18) shows dramatically different numbers:

```sql
-- All on latest-version tests only (11,142 total).
empty_spec_id         = 254   tests (2.3%)
phantom_spec_id       = 2,068 tests (18.6%)   -- spec_id set but spec doesn't exist in KB (any version)
valid_spec_link       = 8,820 tests (79.2%)   -- spec_id resolves to current-version spec
```

Sum of "needs reconciliation": **254 + 2,068 = 2,322 tests (20.8%)** — far
from the 10,440 figure in POR Step 16.D. This discrepancy arose from the
16.A/16.B/16.C remediation streams landing in S297 which updated test
linkages but left the POR text unchanged.

**Hypothesis about the 10,440:** the number predates S297 test-spec linking
work AND may have used "test on disk" as the denominator (vs KB's tracked
tests). Empirical verification of this hypothesis is out of scope — the new
baseline from the live KB is authoritative going forward.

## Proposed Scope (Phase 1)

### §1 — Null out phantom `spec_id` values

Identify all 2,068 latest-version tests with `spec_id` set to a value that
does NOT resolve to any version of any spec in `specifications`. Set their
`spec_id` to NULL (append-only via `insert_test` with `changed_by =
"por_step16d_phase1"` and a clear `change_reason`).

Special case: 5 of the 2,068 have `spec_id` prefixed `WI-` (work items).
These are protocol errors (tests must link to specs, not WIs). Treat
identically: null them out with an explanatory `change_reason`.

**Why null, not delete:** `tests` is append-only; deletion is not permitted.
The new row version replaces the stale `spec_id` with NULL, making the test
visibly an orphan in subsequent queries.

### §2 — Corrected POR baseline

Update `docs/plans/PLAN-OF-RECORD-production-readiness.md:193` +
surrounding lines with accurate post-16.C numbers:

- "**10,440 orphan tests of 11,066 total (94.3%)**" → "**254 empty +
  2,068 phantom-linked = 2,322 tests needing reconciliation (20.8%)**
  (corrected baseline 2026-04-18 via live KB query)."
- Add a brief note explaining the prior 10,440 figure is stale (pre-S297).
- Update exit criterion (16.E) cross-reference if needed (the "≤ 100"
  remains appropriate).

### §3 — Post-cleanup verification query

Add a one-off verification script at `tools/knowledge-db/verify_post_16d_phase1.py`:

- Asserts that no latest-version test has `spec_id` pointing to a
  non-existent spec AFTER this phase runs. Outputs the new orphan count
  (should equal 254 + 2,068 = 2,322 immediately after the run; this
  becomes Phase 2's triage queue).
- Script is run-once, not a permanent CI gate. Not a regression harness.

### §4 — Archive decision in Deliberation Archive

Per `.claude/rules/deliberation-protocol.md` §Owner decisions: archive the
baseline-correction decision as a deliberation with
`source_type = "prime_methodology_correction"`, linked to POR Step 16.

## Files Touched

| File | Change kind | Est. delta |
|---|---|---|
| `tools/knowledge-db/verify_post_16d_phase1.py` (new) | One-off verification + cleanup script | +~120 lines |
| `docs/plans/PLAN-OF-RECORD-production-readiness.md` | Baseline-correction text at §Step 16.D | +~20 / -~5 lines |
| `groundtruth.db` | Data mutation: 2,068 test rows get new version with `spec_id = NULL` | (binary, not counted in diff) |
| Deliberation archive via KB (DELIB-xxxx) | 1 row in `deliberations` | (binary) |

**Total: 2 text files + KB data mutation. Approx +140 lines text.**

## Non-scope (Phase 1 exclusions)

- **Manual triage of the 2,322 orphans.** That's Phase 2 (follow-on
  bridge `por-step16d-phantom-link-cleanup-triage-001` or similar).
- **Retiring or modifying tests on disk.** No `.py` test files are edited in Phase 1.
- **Creating new specs.** Tests currently linked to phantom specs are not
  assigned to any replacement spec in Phase 1 — they simply become orphans
  of the "empty spec_id" class, ready for Phase 2 triage.
- **POR §Step 16.E exit verification.** That runs after Phase 2 is complete.
- **CI gate for orphan count.** Future work (maybe Phase 3 or separate bridge).

## Verification Plan

```text
$ python tools/knowledge-db/verify_post_16d_phase1.py --dry-run
# Expect: reports 2,068 phantom links found; no mutation.

$ python tools/knowledge-db/verify_post_16d_phase1.py --apply
# Expect: inserts 2,068 new test row versions with spec_id = NULL;
# reports "Final orphan count: 2322 (254 pre-existing + 2068 newly nulled)".

$ python tools/knowledge-db/verify_post_16d_phase1.py --verify
# Expect: "PASS: no latest-version test has phantom spec_id".

# Spec assertions + test counts remain unchanged:
$ python tools/knowledge-db/db.py assert
# Expect: no new failures.
```

No pytest or mypy implications — pure KB data operation with a documentary
POR text update.

## Implementation Sequence

1. Create `tools/knowledge-db/verify_post_16d_phase1.py` with three modes: `--dry-run`, `--apply`, `--verify`.
2. Run `--dry-run`, capture output, attach to post-impl report.
3. Run `--apply`, capture output showing exact phantom→null transitions.
4. Run `--verify`, confirm PASS.
5. Update POR §Step 16.D text.
6. Archive DELIB-xxxx for the baseline-correction decision.
7. Commit `feat(por): Step 16.D Phase 1 — phantom spec-link cleanup + baseline correction`.
8. Push to Agent Red `develop` (this is Agent Red work, not GT-KB).
9. File post-impl report at `bridge/por-step16d-phantom-link-cleanup-002.md`.

## Prior Deliberations

- `DELIB-0711`, `DELIB-0712`, `DELIB-0713`, `DELIB-0714` — the 16.A/16.B/16.C
  decision archive. Phase 1 extends this thread.
- No prior bridge has addressed the phantom-link class specifically; 16.A/B/C
  focused on spec-side remediation (verified/implemented spec status),
  not on stale test→spec pointers.

## Owner Decisions Required

None. Scope is data-correction driven by live KB evidence. Defaults pinned:

- **Cleanup method = null-out (not retry-match).** Rationale: all 2,068
  phantom spec_ids resolve to specs that don't exist in ANY version. There's
  no target to recover to. Null-out makes the orphan state honest.
- **Branch = `develop`** (Agent Red, not GT-KB; POR is Agent Red-owned).
- **Baseline-correction text in POR** kept short; the detailed breakdown
  lives in this bridge and the post-impl report.

## Requested Verdict

**GO** to implement §1 + §2 + §3 + §4 per the sequence, or **NO-GO** with
specific findings to revise.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
