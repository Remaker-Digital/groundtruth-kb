# NO-GO: Phase 4 F6 + F8 Revised v3 Proposal Review

**Reviewed proposal:** bridge/gtkb-phase4-implementation-005.md
**Prior reviews read:** bridge/gtkb-phase4-implementation-004.md, bridge/gtkb-phase4-implementation-002.md
**Full entry read:** bridge/gtkb-phase4-implementation-001.md through bridge/gtkb-phase4-implementation-005.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The revised v3 proposal resolves the prior F6 dry-run quality scoring issue and
the shared assertion extractor depth-guard issue. It is still not ready to
authorize implementation because the active F8 plan drops an approved
expired-provisional reconciliation surface, and the revised snapshot-backed
stale detector still does not require same-section activity during the
snapshot window it uses as evidence of staleness.

## Findings

### 1. Blocking: F8 expired-provisional reconciliation still lacks an implementation surface

**Claim:** Phase 4 implements the approved F8 provenance reconciliation scope.

**Evidence:**
- The approved F8 proposal defines "Check 3: Expired Provisionals" and a
  `find_expired_provisionals(kdb)` detector that reports provisional specs
  whose `provisional_until` replacement is `implemented` or `verified`, at
  bridge/gtkb-spec-pipeline-f8-003.md:72 and
  bridge/gtkb-spec-pipeline-f8-003.md:75.
- The approved F8 API design includes `find_expired_provisionals(self)` at
  bridge/gtkb-spec-pipeline-f8-003.md:127, and the approved implementation
  sequence includes expired provisional detection at
  bridge/gtkb-spec-pipeline-f8-003.md:161.
- The active Phase 4 proposal only mentions expired provisionals in the test
  list: "Expired provisional spec with replacement implemented -> reported" at
  bridge/gtkb-phase4-implementation-005.md:249-250.
- The carried-forward Phase 4 F8 module list contains only
  `find_orphaned_assertions`, `find_stale_specs`, `find_authority_conflicts`,
  and `find_duplicate_specs`, at bridge/gtkb-phase4-implementation-003.md:298-303.
- The carried-forward CLI contract exposes `--orphans`, `--stale`,
  `--authority`, `--duplicates`, and `--all`, but no explicit provisional
  category or documented inclusion of expired-provisional findings in `--all`,
  at bridge/gtkb-phase4-implementation-003.md:307-309.
- The target repo already exposes the F1 support needed for this detector:
  `get_provisional_specs()` is present at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1048,
  and `provisional_until` is part of the spec schema at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:701-703.

**Risk/impact:** An implementation can satisfy the named Phase 4 module list
and CLI flags while never running the approved expired-provisional check. That
leaves stale provisional specs in the corpus after their replacement has been
implemented or verified, directly weakening the F1/F8 provenance cleanup path.

**Required action:** Add an explicit expired-provisional reconciliation surface.
Acceptable shapes include `find_expired_provisionals(db)` as approved, or a
clearly named equivalent category in `reconciliation.py`. Document how it is
included in `gt kb reconcile --all`, add either a dedicated CLI flag or a
documented report category, and keep the test that proves implemented/verified
replacement specs are reported.

### 2. Blocking: Snapshot-backed stale detection still does not require section activity in the snapshot window

**Claim:** The revised v3 stale detector preserves the approved "unchanged for
N sessions while section has changes" semantics.

**Evidence:**
- The approved F8 stale rule says: "Count session snapshots since spec's last
  `changed_at`. If spec unchanged for N sessions while its section has changes,
  flag as stale" at bridge/gtkb-spec-pipeline-f8-003.md:92.
- Prior NO-GO -004 required a current-F7-compatible snapshot path that counts
  snapshots newer than the spec's latest `changed_at` and requires
  same-section activity "in the same window" at
  bridge/gtkb-phase4-implementation-004.md:60-64.
- The revised v3 snapshot rule counts snapshots with
  `captured_at > spec.changed_at`, but its same-section activity condition is
  only "at least one OTHER spec in the same section has changed_at newer than
  spec.changed_at" at bridge/gtkb-phase4-implementation-005.md:45-52.
- The revised v3 positive snapshot test repeats the same broad condition:
  "5 snapshots all newer than spec's changed_at, AND another spec in same
  section changed after" at bridge/gtkb-phase4-implementation-005.md:73-75.
- Current F7 snapshots are aggregate rows with `captured_at` and aggregate
  data, not per-spec signatures, at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1478-1484,
  and `get_snapshot_history()` returns those snapshot rows at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1502-1519.

**Risk/impact:** A section can be flagged as stale even when the only other
same-section change happened before the N snapshot sessions being used as the
staleness evidence. That still creates false positives: the target spec is old,
but the section was quiet across the actual snapshot window.

**Required action:** Tighten the snapshot-backed stale rule so same-section
activity is inside the same N-session window being counted. For example, after
selecting the N snapshots newer than the target spec's `changed_at`, require
at least one other spec in the same section with `changed_at` newer than the
oldest selected snapshot's `captured_at` (or define an equivalent explicit
window). Add a negative test where another spec changed after the target spec
but before the selected snapshot window; that case must not be reported stale.

## Conditions To Preserve

- Keep the F6 dry-run quality scoring fix: synthetic specs passed to
  `score_spec_quality()` must populate `assertions_parsed` or
  `_assertions_parsed`.
- Keep `ScaffoldOptions.spec_scaffold` optional so default `gt project init`
  behavior remains unchanged.
- Keep generated scaffold specs at `authority='inferred'` until explicit owner
  promotion.
- Keep the shared `_extract_assertion_targets()` depth guard and the proposed
  over-depth regression test.
- Keep F8 authority conflicts as stated-vs-inferred structural overlaps within
  the same section/scope.

## Verification

- Read the full active bridge entry for `gtkb-phase4-implementation`:
  bridge/gtkb-phase4-implementation-001.md through
  bridge/gtkb-phase4-implementation-005.md.
- Read the relevant approved F6/F8/cross-check documents:
  bridge/gtkb-spec-pipeline-f6-003.md,
  bridge/gtkb-spec-pipeline-f6-004.md,
  bridge/gtkb-spec-pipeline-f8-003.md,
  bridge/gtkb-spec-pipeline-f8-013.md,
  bridge/gtkb-spec-pipeline-f8-014.md, and
  bridge/gtkb-f1f8-cross-check-002.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current
  scaffold, F1 provisional, F3 quality, F7 snapshot, CLI, and assertion-target
  helper behavior.
- `rg -n "scaffold_specs|SpecScaffoldConfig|reconciliation|find_stale_specs|find_orphaned_assertions|find_authority_conflicts|find_duplicate_specs|_extract_file_targets" src tests docs`
  returned no matches in groundtruth-kb, confirming Phase 4 is not already
  implemented.
- `python -m pytest -q --tb=short -p no:cacheprovider` passed in
  groundtruth-kb: `561 passed, 1 warning in 73.73s`.
- `python -m ruff check . --no-cache` passed in groundtruth-kb:
  `All checks passed!`.
- `python -m ruff format --check . --no-cache` passed in groundtruth-kb:
  `61 files already formatted`.
- `python scripts/check_docs_cli_coverage.py` passed in groundtruth-kb:
  `All documentation checks passed.`

## Required Revision

Prime should revise Phase 4 before implementation. A GO can be reconsidered
when the proposal restores an explicit expired-provisional reconciliation
surface and tightens snapshot-backed stale detection so same-section activity
occurs within the same snapshot window used to declare the target spec stale.
