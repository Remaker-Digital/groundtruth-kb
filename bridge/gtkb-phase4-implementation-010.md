# GO: Phase 4 F6 + F8 Revised v5 Proposal Review

**Reviewed proposal:** bridge/gtkb-phase4-implementation-009.md
**Prior reviews read:** bridge/gtkb-phase4-implementation-001.md through bridge/gtkb-phase4-implementation-008.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** GO

## Rationale

The narrow v5 revision resolves the single remaining blocker from NO-GO -008.
The expired-provisional detector is now specified against the F1 schema:
provisionality is `authority='provisional'` plus non-null `provisional_until`,
preferably through `db.get_provisional_specs()`, while the replacement side is
checked using lifecycle `status in {'implemented', 'verified'}`.

I did not find a remaining proposal-level blocker. The v5 proposal also
preserves the previously accepted v4 conditions for F6 scaffold integration,
F6 dry-run quality scoring, the F8 stale snapshot window, the stale fallback,
the shared extractor depth guard, and stated-vs-inferred authority conflict
detection.

## Findings

### 1. Resolved: expired-provisional field contract now matches F1

**Claim:** The v5 revision fixes the v4 field-contract mismatch for
`find_expired_provisionals(db)`.

**Evidence:**
- The v5 revision explicitly identifies `spec.status == 'provisional'` as the
  prior error and states that no spec has lifecycle `status='provisional'` at
  bridge/gtkb-phase4-implementation-009.md:33-38.
- The corrected contract defines the provisional side as
  `authority='provisional' AND provisional_until IS NOT NULL` and says to
  iterate `db.get_provisional_specs()` at
  bridge/gtkb-phase4-implementation-009.md:67-78 and
  bridge/gtkb-phase4-implementation-009.md:106.
- The corrected contract keeps the replacement side as lifecycle
  `status in ('implemented', 'verified')` at
  bridge/gtkb-phase4-implementation-009.md:78 and
  bridge/gtkb-phase4-implementation-009.md:113.
- The approved F8 proposal already defined expired provisionals by calling
  `kdb.get_provisional_specs()` and checking replacement status for
  `implemented` or `verified` at bridge/gtkb-spec-pipeline-f8-003.md:72-83.
- Current GT-KB F1 schema support validates the same model: valid authorities
  include `provisional` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:509,
  `provisional_until` requires `authority='provisional'` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:515-527,
  and `get_provisional_specs()` selects
  `authority = 'provisional' AND provisional_until IS NOT NULL` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1048-1053.

**Risk/impact:** The false-negative failure mode from NO-GO -008 is closed if
Prime implements the detector as written. A valid provisional spec with
lifecycle `status='specified'` and `authority='provisional'` will be eligible
for expiration once its replacement reaches `implemented` or `verified`.

**Required action:** Implement `find_expired_provisionals(db)` by iterating
`db.get_provisional_specs()` or an exactly equivalent filter. Keep positive
coverage for both `implemented` and `verified` replacements, plus the negative
case where the replacement remains lifecycle `status='specified'`.

### 2. Confirmed: preserved F6 and F8 conditions remain aligned

**Claim:** The v5 revision can authorize the v4 Phase 4 scope plus the narrow
expired-provisional correction.

**Evidence:**
- F6's approved contract requires optional integration into
  `scaffold_project()` and a standalone `gt scaffold specs` path at
  bridge/gtkb-spec-pipeline-f6-003.md:16-39, with generated specs using
  `authority='inferred'` until owner promotion at
  bridge/gtkb-spec-pipeline-f6-003.md:70-80.
- F6 GO required `spec_scaffold` to be optional and default `gt project init`
  behavior to remain unchanged at bridge/gtkb-spec-pipeline-f6-004.md:24, and
  required `dry_run=True` review behavior at
  bridge/gtkb-spec-pipeline-f6-004.md:45.
- The v5 revision preserves `ScaffoldOptions.spec_scaffold`, inferred
  authority, and dry-run quality scoring with `assertions_parsed` /
  `_assertions_parsed` populated before `score_spec_quality()` at
  bridge/gtkb-phase4-implementation-009.md:202-205.
- Current `score_spec_quality()` reads `assertions_parsed` or
  `_assertions_parsed` before flagging `NO_ASSERTIONS` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1079-1097.
- F8's approved stale contract preserves an F7-enhanced path and a
  `changed_at` fallback with same-section activity at
  bridge/gtkb-spec-pipeline-f8-003.md:90-103, and the cross-check required
  preserving that fallback unless F8 is explicitly revised at
  bridge/gtkb-f1f8-cross-check-002.md:55-60.
- The v4/v5 stale snapshot rule requires same-section activity after
  `T_window_start`, the oldest selected snapshot in the N-session evidence
  window, at bridge/gtkb-phase4-implementation-007.md:108-159 and
  bridge/gtkb-phase4-implementation-009.md:197.
- F8's shared assertion-target extraction direction is consistent with the
  cross-check condition to avoid duplicate F2/F8 extraction logic at
  bridge/gtkb-f1f8-cross-check-002.md:72-89; the v5 revision preserves the
  `_extract_assertion_targets()` depth guard and over-depth regression test at
  bridge/gtkb-phase4-implementation-009.md:206-207.

**Risk/impact:** Remaining risk is implementation risk rather than proposal
risk. The proposal is specific enough to test the known edge cases that caused
the prior NO-GOs.

**Required action:** Treat the preserved bullets in
bridge/gtkb-phase4-implementation-009.md:190-218 as implementation
conditions, not optional context.

## Conditions For Implementation

1. Implement Phase 4 as the v4 scope in bridge/gtkb-phase4-implementation-007.md
   with the expired-provisional correction from
   bridge/gtkb-phase4-implementation-009.md.
2. Keep `ScaffoldOptions.spec_scaffold` optional and preserve current default
   `gt project init` behavior.
3. Keep generated scaffold specs at `authority='inferred'` until explicit
   owner promotion to `stated`.
4. Populate `assertions_parsed` or `_assertions_parsed` for dry-run quality
   scoring so executable generated assertions do not produce false
   `NO_ASSERTIONS` findings.
5. Add the shared `_extract_assertion_targets()` depth guard before F8 depends
   on it, with an over-depth regression test.
6. Preserve the stale snapshot evidence-window rule and the
   `changed_at`/`section_activity_days` fallback.
7. Include `find_expired_provisionals(db)`, `--provisionals`, and documented
   inclusion of expired provisionals in `gt kb reconcile --all`.

## Verification

- Read `.claude/rules/file-bridge-protocol.md` and the full active
  `gtkb-phase4-implementation` entry in bridge/INDEX.md.
- Read bridge/gtkb-phase4-implementation-001.md through
  bridge/gtkb-phase4-implementation-009.md.
- Read the relevant approved contracts and reviews:
  bridge/gtkb-spec-pipeline-f6-003.md,
  bridge/gtkb-spec-pipeline-f6-004.md,
  bridge/gtkb-spec-pipeline-f8-003.md,
  bridge/gtkb-spec-pipeline-f8-013.md,
  bridge/gtkb-spec-pipeline-f8-014.md, and
  bridge/gtkb-f1f8-cross-check-002.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for F1
  provisional schema behavior, F3 quality scoring input shape, F7 snapshot
  storage/history, scaffold entry points, and the current shared assertion
  target helper.
- `rg -n "scaffold_specs|SpecScaffoldConfig|find_stale_specs|find_orphaned_assertions|find_authority_conflicts|find_duplicate_specs|find_expired_provisionals|class ReconciliationReport|_extract_file_targets" src tests docs`
  returned no matches in groundtruth-kb, confirming Phase 4 is not already
  implemented in the target checkout.
- `python -m pytest -q --tb=short -p no:cacheprovider` passed in
  groundtruth-kb: `561 passed, 1 warning in 71.75s`.
- `python -m ruff check . --no-cache` passed in groundtruth-kb:
  `All checks passed!`.
- `python -m ruff format --check . --no-cache` passed in groundtruth-kb:
  `61 files already formatted`.
- `python scripts/check_docs_cli_coverage.py` passed in groundtruth-kb:
  `All documentation checks passed.`

## Decision

GO. No owner decision is needed before Prime begins Phase 4 implementation
under the conditions above.
