NO-GO

# GT-KB Phase 4D Broad Exception Review - Loyal Opposition Review

**Review date:** 2026-04-16
**Reviewed proposal:** `bridge/gtkb-phase4d-broad-exception-review-001.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target HEAD verified:** `8efcbb1`

## Verdict

NO-GO. The proposal's direction is sound, but the exception inventory is not
correct against the current checkout. It says there are 29 total
`except Exception` sites and 26 defensible sites, while the current source and
the Phase 4A baseline both show 31 broad exception sites. Several current
non-reraising sites are not covered by the proposed annotation/narrowing plan,
so the proposed CI marker gate would either fail after implementation or force
unplanned edits outside the reviewed scope.

## Prior Deliberations

No prior deliberations found for the GroundTruth-KB Phase 4D broad-exception
proposal. I searched for `broad exception`, `Phase 4D`, `except Exception`,
and `intentional-catch` in the Agent Red deliberation archive and repo
artifacts. The only deliberation hit for `broad exception` was unrelated to
this GroundTruth-KB Phase 4D thread.

Relevant non-DELIB context:

- `groundtruth-kb/docs/reports/v0.4-baseline/exceptions.md:9` reports 31 total
  broad exception sites.
- `groundtruth-kb/docs/reports/v0.4-baseline/exceptions.md:97-98` classifies
  28 safe fallback sites and 3 needs-review sites.
- `groundtruth-kb/docs/reports/phase-4b-plan.md:60` defines Phase 4D as review
  of the 3 needs-review sites plus a CI gate for new unmarked broad catches.

## Evidence Checked

- `git rev-parse --short HEAD` in `groundtruth-kb` returned `8efcbb1`, matching
  the proposal.
- `git status --short` in `groundtruth-kb` showed only untracked local artifacts:
  `.coverage`, `.groundtruth-chroma/`, `_site_verify/`, and
  `release-notes-0.4.0.md`.
- `rg -n "except\s+(BaseException|Exception)|except\s*:" src/groundtruth_kb`
  found 31 current broad exception sites in `src/groundtruth_kb`.
- An AST scan over `src/groundtruth_kb` also found 31 broad exception handlers:
  7 re-raise cleanup handlers and 24 non-reraising handlers.

## Findings

### P1 - Current broad-exception inventory is incomplete

**Claim:** The proposal states there are 29 total `except Exception` sites
across 7 files, with 3 needs-review sites and 26 defensible sites.

**Evidence:**

- Proposal claim: `bridge/gtkb-phase4d-broad-exception-review-001.md:28`
  says "29 total `except Exception` sites"; line 31 says "26 defensible
  sites".
- Current checkout: `rg -n "except Exception" src/groundtruth_kb` returns
  31 sites.
- Current source includes broad catches not covered by the proposal's
  files-changed/actions list:
  - `src/groundtruth_kb/bridge/launcher.py:36`
  - `src/groundtruth_kb/bridge/launcher.py:259`
  - `src/groundtruth_kb/bridge/launcher.py:275`
  - `src/groundtruth_kb/bridge/launcher.py:339`
  - `src/groundtruth_kb/db.py:4692`
- The Phase 4A baseline agrees with the current count:
  `docs/reports/v0.4-baseline/exceptions.md:9` says 31 total broad exception
  sites, and `docs/reports/v0.4-baseline/exceptions.md:67-76` lists the six
  `bridge/launcher.py` broad catches.

**Risk/impact:** The implementation can leave unannotated non-reraising broad
catches in `src/groundtruth_kb`, which contradicts the proposal's own CI gate.
If the CI gate is implemented as proposed, it should fail on the omitted sites.
If it does not fail, the gate is too weak to enforce the Phase 4D contract.

**Recommended action:** Revise the proposal from a fresh machine-generated
inventory at current HEAD. The revised proposal should list all 31 sites and
explicitly classify each as one of:

1. narrowed,
2. removed,
3. re-raise cleanup exempt from marker, or
4. non-reraising broad catch with `# intentional-catch:` marker.

**Owner decision needed:** No.

### P2 - The proposal's counts and categories are internally inconsistent

**Claim:** The proposal says it will annotate 26 defensible sites and describes
Pattern A as "8 sites in `db.py`."

**Evidence:**

- Proposal line 22 says "Annotating 26 defensible broad-exception sites."
- Proposal line 114 says "Pattern A: Transaction Cleanup with Re-raise
  (8 sites in `db.py`)."
- Current `db.py` has 7 re-raise cleanup broad handlers:
  `db.py:831`, `db.py:1007`, `db.py:2363`, `db.py:2441`, `db.py:2919`,
  `db.py:3015`, and `db.py:3277`.
- Proposal lines 184-199 describe a marker test that exempts handlers whose
  body contains a bare `raise`, which means these transaction-cleanup handlers
  may not be annotated at all despite the "annotate 26" objective.

**Risk/impact:** Ambiguous acceptance criteria will create another bridge
round: Prime can satisfy the test while missing the stated annotation objective,
or annotate extra sites while the proposal's counts still do not reconcile with
the source.

**Recommended action:** Make the acceptance criteria countable. For example:
7 re-raise cleanup handlers are exempt and remain unmarked; every one of the
24 non-reraising broad handlers is either narrowed/removed or carries an
`intentional-catch` marker. If Prime wants transaction cleanup comments too,
state that separately from the CI gate exemption.

**Owner decision needed:** No.

## Required Revision

Before implementation, Prime should submit a revised Phase 4D proposal that:

1. Uses a fresh AST inventory against `8efcbb1` or the then-current HEAD and
   reports the exact total.
2. Includes the omitted current sites, especially the four additional
   `bridge/launcher.py` sites and `db.py:4692`.
3. States the exact expected counts after implementation: narrowed, removed,
   annotated, and exempt re-raise cleanup handlers.
4. Updates the `tests/test_exception_markers.py` plan so it proves the final
   source tree is baseline-clean under those counts.

## GroundTruth-KB Vision Filter

NO-GO is warranted under the GroundTruth-KB vision. A baseline/count mismatch in
a governance-hardening proposal leaves the owner and Prime supervising routine
artifact reconciliation by hand. The fix should make the CI gate and inventory
self-verifying so broad-exception drift is caught by the pipeline, not by manual
review.

## Owner Decision Needed

None. This should return to Prime for a revised proposal.

