# NO-GO: Phase 4 F6 + F8 Revised v4 Proposal Review

**Reviewed proposal:** bridge/gtkb-phase4-implementation-007.md
**Prior reviews read:** bridge/gtkb-phase4-implementation-006.md, bridge/gtkb-phase4-implementation-004.md, bridge/gtkb-phase4-implementation-002.md
**Full entry read:** bridge/gtkb-phase4-implementation-001.md through bridge/gtkb-phase4-implementation-007.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The v4 proposal resolves the two blockers from NO-GO -006 at the surface level:
it adds an explicit expired-provisional reconciliation detector and tightens
snapshot-backed stale detection to require same-section activity inside the
same evidence window.

One blocking field-contract mismatch remains. The new expired-provisional
detector describes the provisional spec using `spec.status == 'provisional'`,
but F1 and the current checkout define provisional status through
`authority='provisional'` plus `provisional_until`. If implemented literally,
the detector can miss every valid provisional spec.

## Findings

### 1. Blocking: Expired-provisional detection uses the wrong field for the provisional side

**Claim:** v4 restores the approved expired-provisional reconciliation surface.

**Evidence:**
- The active proposal defines `find_expired_provisionals(db)` at
  bridge/gtkb-phase4-implementation-007.md:42.
- Its docstring says a provisional spec is expired when
  `spec.status == 'provisional'` and `spec.provisional_until` references a
  replacement at bridge/gtkb-phase4-implementation-007.md:47-50.
- The same docstring later cites the correct F1 helper,
  `db.get_provisional_specs()`, at bridge/gtkb-phase4-implementation-007.md:57-59.
- The approved F8 proposal defined the detector by calling
  `kdb.get_provisional_specs()` and checking the replacement spec's lifecycle
  `status` for `implemented` or `verified` at
  bridge/gtkb-spec-pipeline-f8-003.md:75-83.
- Current F1 defines valid authorities as including `provisional` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:509.
- Current F1 normalization requires `provisional_until` to pair with
  `authority='provisional'`, not lifecycle `status='provisional'`, at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:520-527.
- Current `get_provisional_specs()` filters
  `authority = 'provisional' AND provisional_until IS NOT NULL` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1048-1054.
- Current F1 tests seed provisional specs with `status='specified'`,
  `authority='provisional'`, and `provisional_until=...` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_db.py:548-570.

**Risk/impact:** An implementation that follows the v4 docstring literally can
filter on the lifecycle status field and return no expired provisionals,
because valid provisional specs in the current schema are still lifecycle
`status='specified'` or similar while their authority is `provisional`. That
would make both `gt kb reconcile --provisionals` and `--all` produce false
negative reports for the F1/F8 cleanup path.

**Required action:** Revise the v4 proposal so the provisional side is defined
only as `authority='provisional'` with non-null `provisional_until`, preferably
by explicitly iterating `db.get_provisional_specs()`. Keep the replacement side
as lifecycle `status in {'implemented', 'verified'}`. Remove references to
`spec.status == 'provisional'` and to replacement `status='provisional'`, unless
a separate lifecycle status migration is being proposed.

Add or tighten the positive test so it seeds:

```python
db.insert_spec(
    id="SPEC-P",
    title="Provisional",
    status="specified",
    authority="provisional",
    provisional_until="SPEC-R",
    changed_by="test",
    change_reason="test",
)
db.insert_spec(
    id="SPEC-R",
    title="Replacement",
    status="implemented",
    authority="stated",
    changed_by="test",
    change_reason="test",
)
```

and verifies `find_expired_provisionals(db)` reports `SPEC-P`. Keep the
negative test for a replacement still at lifecycle `status='specified'`.

## Conditions To Preserve

- Keep the explicit `find_expired_provisionals(db)` surface, the
  `--provisionals` CLI flag, and documented inclusion in `--all`.
- Keep the v4 stale snapshot window rule: same-section activity must occur
  after `T_window_start`, the oldest selected snapshot in the N-session
  evidence window.
- Keep the stale fallback path with `section_activity_days` and both positive
  and negative same-section activity tests.
- Keep the F6 dry-run quality scoring fix: synthetic dry-run specs passed to
  `score_spec_quality()` must populate `assertions_parsed` or
  `_assertions_parsed`.
- Keep `ScaffoldOptions.spec_scaffold` optional and preserve default
  `gt project init` behavior.
- Keep generated scaffold specs at `authority='inferred'` until explicit owner
  promotion.
- Keep the shared `_extract_assertion_targets()` depth guard and the over-depth
  regression test.
- Keep F8 authority conflicts as stated-vs-inferred structural overlaps within
  the same section/scope.

## Verification

- Read the full active bridge entry:
  bridge/gtkb-phase4-implementation-001.md through
  bridge/gtkb-phase4-implementation-007.md.
- Read the relevant approved F6/F8/cross-check documents:
  bridge/gtkb-spec-pipeline-f6-003.md,
  bridge/gtkb-spec-pipeline-f6-004.md,
  bridge/gtkb-spec-pipeline-f8-003.md,
  bridge/gtkb-spec-pipeline-f8-013.md,
  bridge/gtkb-spec-pipeline-f8-014.md, and
  bridge/gtkb-f1f8-cross-check-002.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current
  scaffold, F1 provisional, F3 quality, F7 snapshot, CLI, and shared assertion
  extraction behavior.
- `rg -n "scaffold_specs|SpecScaffoldConfig|find_stale_specs|find_orphaned_assertions|find_authority_conflicts|find_duplicate_specs|find_expired_provisionals|class ReconciliationReport|_extract_file_targets" src tests docs`
  returned no matches in groundtruth-kb, confirming Phase 4 is not already
  implemented.
- `python -m pytest -q --tb=short -p no:cacheprovider` passed in
  groundtruth-kb: `561 passed, 1 warning in 71.70s`.
- `python -m ruff check . --no-cache` passed in groundtruth-kb:
  `All checks passed!`.
- `python -m ruff format --check . --no-cache` passed in groundtruth-kb:
  `61 files already formatted`.
- `python scripts/check_docs_cli_coverage.py` passed in groundtruth-kb:
  `All documentation checks passed.`

## Required Revision

Prime should revise only the expired-provisional field contract. A GO can be
reconsidered when `find_expired_provisionals()` is specified against
`authority='provisional'` / `db.get_provisional_specs()` for the provisional
side and lifecycle `status in {'implemented', 'verified'}` for the replacement
side.
