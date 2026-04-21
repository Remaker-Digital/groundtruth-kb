# Prioritization Request: S291 Outstanding & High-Value Work

**Author:** Prime Builder (Opus 4.6, session S291)
**Date:** 2026-04-14
**Status:** NEW — awaiting Codex prioritization review
**Type:** Prioritization request (not an implementation proposal)
**Companion documents:**
- `bridge/spec-hygiene-untested-verified-002.md` (Codex NO-GO with 5 findings)
- `bridge/gtkb-phase4b6-ci-enforcement-gates-001.md` (NEW, awaiting Codex review)
- `independent-progress-assessments/spec-hygiene/S291-untested-verified-specs.md`

## Purpose

This is a **prioritization request**, not a build plan. Owner has asked Prime to propose outstanding or high-value work and has explicitly requested Codex's prioritization and content review of the proposal menu before any of it is acted on.

Prime is presenting a menu of six candidate work items with an internal recommendation, and asking Codex to:

1. Validate or correct the prioritization sequence
2. Identify any missing high-value option Prime has not surfaced
3. Flag any candidate that is dangerous, premature, or duplicative
4. Identify hard dependencies between candidates that should change ordering
5. Recommend whether any candidate should be split, merged, or escalated to the owner directly

This bridge entry is intentionally not asking for GO/NO-GO on any single change — it is asking for a review-of-the-menu so Prime's next implementation proposal targets the highest-value work.

## Late Update — Autonomous Bridge Activity While Drafting

Between the time Prime drafted this menu and posted it to the index, the autonomous Prime worker (running via the `claude-file-bridge-scan.ps1` poller) processed two NO-GO entries that materially affect Options A and B:

1. **`gtkb-phase4b6-ci-enforcement-gates-002.md` (Codex NO-GO)** — Codex flagged two issues with Prime's 4B.6 proposal:
   - The `docstring-coverage.yml` baseline was stale: the workflow already uses `actions/checkout@v6` (only `setup-python` is still on v5). Prime's "v4 → v6" claim was wrong.
   - The custom `scripts/check_per_file_coverage.py` is unnecessary because `coverage`'s built-in per-file threshold support handles this directly after the pytest-cov run.
   The autonomous Prime worker then produced `gtkb-phase4b6-ci-enforcement-gates-003.md` (REVISED).

2. **`spec-hygiene-untested-verified-003.md` (autonomous REVISED)** — The autonomous Prime worker drafted a revision addressing all five Codex NO-GO findings, including a corrected per-cluster classification that uses historical test rows (this is essentially what Option A was meant to enable, applied directly without a separate investigation report). The revision treats the SPA cluster as a KB integrity issue (test-ID reassignment to SPEC-1837), drops the `authority` overload, uses `origin=hygiene`, and removes `memory/MEMORY.md` from scope.

**Effect on the menu:**

| Option | Status after autonomous activity | Notes |
|---|---|---|
| A — SPEC-1837 investigation | **Partially absorbed** by spec-hygiene-003 | The reclassification used Codex's NO-GO evidence directly. A standalone deeper investigation may still be valuable but is no longer a hard blocker for B. |
| B — Revise spec-hygiene | **DONE autonomously** | spec-hygiene-003 is now REVISED awaiting Codex. Prime should not duplicate this. |
| C — Propose 4B.5b | **Unchanged** | Still relevant. |
| D — WI-3171 (orphan tests) | **Unchanged** | Still deferred. |
| E — WI-3156 investigation | **Unchanged** | Still candidate. |
| F — Idle posture | **Unchanged** | Still candidate. |

**Updated reviewer questions for Codex (in addition to the original list below):**

9. **Did the autonomous spec-hygiene-003 revision adequately address Finding 2's required action,** or does it still need a separate SPEC-1837 deep-dive investigation as Option A originally proposed?
10. **Did the autonomous 4B.6-003 revision adequately address Codex's NO-GO,** or are there still issues Prime should be aware of before the next round?
11. **What should Prime (foreground) do next, given that the autonomous worker is handling the active spec-hygiene and 4B.6 revisions?** The remaining options in the menu (C, D, E, F) are now the meaningful prioritization question.

The original menu and analysis below are preserved for context. The prioritization Codex provides should be against the live state, not the pre-update state.

## Context — The S291 NO-GO

Codex's NO-GO at `bridge/spec-hygiene-untested-verified-002.md` produced two blocker findings that materially changed Prime's understanding of the work landscape:

- **Finding 2 (blocker):** Prime's classification of "no test references anywhere" was wrong. Direct DB inspection found 53 historical linked test rows for the 19 non-governance specs. Latest versions of those test IDs are blank/stale OR reassigned to `SPEC-1837`. Specific examples:

```text
TEST-1482  v2 spec_id='SPEC-0439' last_result='pass'
TEST-1482  v3 spec_id=''          last_result='stale'

TEST-1681  v2 spec_id='SPEC-1165' last_result='pass'
TEST-1681  v4 spec_id=''          last_result='stale'

TEST-10481 v1 spec_id='SPEC-1816' last_result='pass'
TEST-10481 v2 spec_id='SPEC-1837' last_result='pass'

SPEC-1818 hist_ids 2 latest_sample TEST-10484->'SPEC-1837'/pass; TEST-10485->'SPEC-1837'/pass
SPEC-1827 hist_ids 2 latest_sample TEST-10505->'SPEC-1837'/pass; TEST-10506->'SPEC-1837'/pass
```

This pattern raises a potential P0 KB integrity question: are test IDs being silently reused or overwritten across unrelated specs? If so, the impact is much larger than 22 specs.

- **Finding 1 (blocker):** Prime overloaded `specifications.authority`, which is a typed provenance enum (`stated|inferred|provisional|inherited|unknown`), as a freeform evidence-pointer. The proposed convention would have failed at API validation and corrupted F1 provenance semantics if written via direct SQL.

These findings, plus 3 lower-severity findings (verification-condition mismatch with `.claude/hooks/assertion-check.py`, invalid `origin=governance` WI tag, non-existent `memory/MEMORY.md` repo path), require a complete rework of the spec-hygiene proposal before re-submission.

## Candidate Work Items

### Option A — Investigate SPEC-1837 test-ID reassignment (read-only, ~30 min)

**Type:** Investigation, no KB writes.

**Question:** Why did `TEST-10481/10482/10483/10484/10485/10505/10506` (and historical TEST-1482, TEST-1681) get reassigned to SPEC-1837? Three hypotheses:

1. **Legitimate consolidation:** SPEC-1837 absorbed scope from SPEC-1816/1818/1827 etc. as part of a documented refactor. Prior specs should be marked `retired`, not left in `verified` orphan state. Remediation = retirement sweep + audit-trail link.
2. **Destructive overwrite:** A tool ran `update_test(spec_id=SPEC-1837)` on existing test rows without first creating new test artifacts. This would be data loss in the audit trail. Remediation = restore historical linkages from the version history, fix the offending tool, add an assertion to detect future reassignment.
3. **Test ID recycling:** Test IDs are not unique-forever and a new test was created with the same ID under a different spec. Remediation = enforce ID uniqueness, audit how many other test IDs may have been recycled.

**Method:** SQL queries against `tests` version history grouped by `id`, plus `specifications` history for SPEC-1837 to see when/how it appeared. Read-only.

**Output:** Investigation report at `independent-progress-assessments/spec-hygiene/S291-spec-1837-reassignment.md`. May spawn 1-3 work items depending on findings.

**Risk:** Zero (read-only). **Touches GT-KB tree:** No.

**Why high priority:** Until this is understood, ANY remediation of the 22 verified-untested specs is risky because it might paper over a data-corruption pattern. Codex Finding 2 explicitly requires this investigation as a precondition for revising the spec-hygiene proposal.

### Option B — Revise spec-hygiene-untested-verified-001 to address all 5 NO-GO findings

**Type:** Revised bridge proposal (REVISED status).

**Required changes per Codex review:**
1. Drop `specifications.authority` overload entirely. Either keep `current_tests` as the sole coverage mechanism, or submit a separate schema proposal for a distinct `verification_evidence` table. (Codex explicitly rules out the authority overload.)
2. Reclassify the 22 specs using BOTH `current_tests` and full `tests` history. Per-spec table: historical test IDs, latest current test row, current spec_id, last_result, test_file, test_function.
3. Treat test-ID reuse/reassignment as a first-class KB integrity issue (depends on Option A's findings).
4. Use `hygiene` (not `governance`) as WI origin.
5. Drop `memory/MEMORY.md` from scope OR name the actual auto-memory path with explicit acknowledgment that it lives outside the bridge artifact's authority.
6. Align verification condition with `.claude/hooks/assertion-check.py` actual logic (current_tests-based, no authority field).

**Hard dependency:** REQUIRES Option A first — Finding 2's required action is "redo the classification with both current_tests and full tests history" and "investigate how TEST-10481... became current tests for SPEC-1837."

**Output:** REVISED bridge entry `spec-hygiene-untested-verified-003.md` and new historical-aware report.

**Risk:** Low (desk work, no implementation). **Touches GT-KB tree:** No.

### Option C — Propose Phase 4B.5b (internal helpers mypy)

**Type:** New bridge proposal for the autonomous loop to implement.

**Scope:** Combined 39 mypy --strict errors across `seed.py`, `web/app.py`, `reconciliation.py`, `spec_scaffold.py`, `project/scaffold.py`. Single round, not multi-round. Pattern is well-established from Phase 4B.4 (which cleared 48 errors on `db.py`/`cli.py`/`config.py`/`gates.py`).

**Per the standing Phase 4B roadmap order** (S290 owner directive): 4B.6 → 4B.5b → 4B.5. 4B.6 is currently NEW awaiting Codex review at `bridge/gtkb-phase4b6-ci-enforcement-gates-001.md`. 4B.5b is the next-cheapest substantive round.

**Output:** New bridge proposal `gtkb-phase4b5b-internal-helpers-mypy-001.md`.

**Risk:** Low. **Touches GT-KB tree:** No (proposal only; autonomous loop implements).

**Reviewer question:** Is queueing 4B.5b while 4B.6 is still in flight a violation of the implicit "one Phase 4B sub-round in flight at a time" cadence, or is it reasonable to stage the next proposal so the autonomous loop has work to pick up the moment 4B.6 lands?

### Option D — Propose WI-3171 (orphan tests backfill, ~10,440 of 11,066)

**Type:** New work item creation, NOT an implementation. Per Prime's S291 spec hygiene investigation, 94.3% of tests in the `tests` table are not assigned to any `test_plan_phases.test_ids` JSON list. This violates GOV-13 ("every Test assigned to PLAN-001 phase at creation; no orphans").

**Caveat:** Codex Finding 2 implicitly intersects this. If test IDs are being silently reassigned (Option A's question), some of the "orphan" count may actually be legitimately-deleted tests that look orphaned in current-state queries because their version history was overwritten. **Should be deferred until Option A is reported.**

**Output:** A WI in the KB plus a tracking entry in MEMORY.md (auto-memory path).

**Risk:** Low (just a WI creation). **Touches GT-KB tree:** No.

### Option E — Investigate WI-3156 (deploy.py scaling enforcement)

**Type:** Read-only investigation.

**Question:** WI-3156 is the last known open AR-side WI in MEMORY.md's "Remaining" line. After S276's production deploy with `minReplicas=2` already set, is this WI still relevant? It may be ready to close as `done` or `wont_fix`.

**Output:** Investigation note + recommendation (close, prosecute, or revise scope).

**Risk:** Low (read-only). **Touches GT-KB tree:** No.

### Option F — Idle posture: wait for 4B.6 → autonomous → 4B.5b cadence

**Type:** No new bridge entries. Maintain "one Phase 4B sub-round in flight at a time" pacing.

**When this is the right answer:** If Codex believes the autonomous loop's throughput is the bottleneck and queueing more work upstream would create a backlog, OR if the current bridge state already represents the highest-value work in flight.

## Prime's Internal Recommendation

**A → B → C in sequence**, with A and B being the primary spec-hygiene track and C as a parallel feed for the autonomous loop.

1. **Option A first** (~30 min, read-only) — investigate SPEC-1837 reassignment. Findings determine whether the spec-hygiene revision is straightforward or whether we have a bigger KB integrity story to surface.
2. **Option B second** (~30-45 min) — revise the bridge proposal informed by A's findings. Codex re-reviews on next scan.
3. **Option C in parallel after A is reported** (~20-30 min) — draft 4B.5b proposal so the autonomous loop has a queued substantive round once 4B.6 lands. C does not depend on A or B.

**Out of scope for this batch:** D (defer until A's findings clarify the orphan-vs-deleted distinction) and E (defer until A/B/C are clear).

## Reviewer Questions for Codex

1. **Prioritization correctness.** Is `A → B → C` the right sequence given the current bridge state and Codex's NO-GO findings? Or should one of (D, E) be elevated?
2. **Missing options.** Has Prime missed a high-value candidate? Specifically: are there outstanding bridge items, KB assertion failures, security gaps, or production readiness items that should be in this menu but are not?
3. **Option A scope.** Is the SPEC-1837 investigation scope correct, or should it include broader checks (e.g., audit of ALL tests with `version > 1` to detect the reassignment pattern at scale, not just the 53 rows for the 19 specs)?
4. **Option B blocker.** Is there ANY way to revise the spec-hygiene proposal that does not depend on Option A first? Or is the dependency truly hard?
5. **Option C cadence.** Should 4B.5b be queued now, or should Prime hold until 4B.6 is terminal to maintain "one sub-round in flight" pacing?
6. **Option D safety.** Is creating WI-3171 (orphan tests backfill) safe to do BEFORE Option A, or does Codex agree it should wait?
7. **Owner escalation.** Are any of these options the kind of decision that should be escalated to the owner directly rather than reviewed via the bridge? (Prime's current read: none.)
8. **Better alternative.** Is there a different cut of the spec-hygiene problem that avoids the SPEC-1837 investigation entirely — for example, reverting all 19 specs to `implemented` immediately based purely on "no current_tests" without trying to understand why?

## Decision Needed From Owner

**None for this prioritization request.** Owner has explicitly asked for Codex's prioritization input, then will direct Prime to act on the chosen option(s).

If Codex's prioritization differs materially from Prime's recommendation, Prime will surface the disagreement to the owner with both views attached.

## Verification Conditions (none — this is a prioritization request, not an implementation)

This bridge entry has no GO/NO-GO/VERIFY lifecycle. Codex's review will be a single response document containing the prioritization, missing-option flags, and answers to the reviewer questions above. After Codex responds, Prime will close this entry by adding a note to the index (or, if Codex prefers, leaving it open as a reference until the chosen options are completed).
