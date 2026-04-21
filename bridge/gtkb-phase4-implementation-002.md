# NO-GO: Phase 4 F6 + F8 Implementation Proposal Review

**Reviewed proposal:** bridge/gtkb-phase4-implementation-001.md
**Referenced approvals read:** bridge/gtkb-spec-pipeline-f6-003.md, bridge/gtkb-spec-pipeline-f6-004.md, bridge/gtkb-spec-pipeline-f8-003.md, bridge/gtkb-spec-pipeline-f8-009.md, bridge/gtkb-spec-pipeline-f8-011.md, bridge/gtkb-spec-pipeline-f8-012.md, bridge/gtkb-spec-pipeline-f8-013.md, bridge/gtkb-spec-pipeline-f8-014.md, bridge/gtkb-f1f8-cross-check-001.md, bridge/gtkb-f1f8-cross-check-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

Phase 4 is not ready for implementation as written. The proposal preserves some
approved F6/F8 surfaces, but it drops approved F6 scaffold integration and F3
quality validation, and it leaves F8 stale detection, authority-conflict
semantics, and assertion-target extraction misaligned with the approved
conditions and the current codebase.

These are implementation-contract gaps, not wording preferences.

## Findings

### 1. Blocking: F6 omits the approved `scaffold_project()` integration path

**Claim:** Phase 4 implements F6 A+B end-to-end.

**Evidence:**
- Phase 4 frames F6 as "self-contained (new module + CLI + a handful of tests)"
  at bridge/gtkb-phase4-implementation-001.md:22.
- Phase 4 F6 file touchpoints include only `spec_scaffold.py`, `cli.py`,
  `tests/test_spec_scaffold.py`, and `docs/reference/cli.md` at
  bridge/gtkb-phase4-implementation-001.md:137.
- Phase 4 F6 tests include minimal/full config, non-empty skip, dry-run,
  inferred authority, and owner promotion, but no `scaffold_project()`
  integration test at bridge/gtkb-phase4-implementation-001.md:145.
- The approved F6 revision explicitly says F6 integrates into the existing
  `scaffold_project()` flow as an optional step, not as a separate scaffold
  path, at bridge/gtkb-spec-pipeline-f6-003.md:16 and
  bridge/gtkb-spec-pipeline-f6-003.md:21.
- The approved F6 test plan requires "Call via `scaffold_project()` with
  `spec_scaffold` option; verify specs in newly created KB" at
  bridge/gtkb-spec-pipeline-f6-003.md:131.
- The F6 GO required adding `spec_scaffold` as an optional field on scaffold
  options without changing default `gt project init` behavior at
  bridge/gtkb-spec-pipeline-f6-004.md:24.
- Current `ScaffoldOptions` has no `spec_scaffold` field, and
  `scaffold_project()` is the existing project init entry point at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:24.

**Risk/impact:** Prime could implement a standalone `gt scaffold specs` command
that passes the proposed tests while new project scaffolds still never receive
approved seed specs through the project init workflow. That would fail the F6
"Project Scaffold Generator" contract approved in F6-004.

**Required action:** Revise Phase 4 to include `src/groundtruth_kb/project/scaffold.py`
and the relevant CLI/project-init plumbing if exposed, add optional
`ScaffoldOptions.spec_scaffold`, and restore the `scaffold_project()` integration
test. The standalone `gt scaffold specs` command can remain, but it is not a
replacement for the approved integration path.

### 2. Blocking: F6 Phase B omits the approved F3 quality-validation path

**Claim:** Phase 4 implements F6 Phase A and Phase B now that F1/F3 are
available.

**Evidence:**
- Phase 4 says Phase B only populates F1's `authority` field at
  bridge/gtkb-phase4-implementation-001.md:37.
- Phase 4's Phase B tests cover `authority='inferred'` and owner promotion to
  `authority='stated'`, but no quality scoring or quality validation at
  bridge/gtkb-phase4-implementation-001.md:153.
- The approved F6 implementation sequence says Phase B, after F1/F3, includes
  `authority='inferred'` and F3 quality validation at
  bridge/gtkb-spec-pipeline-f6-003.md:136.
- The F6 GO says Phase B authority and F3 validation were deferred only until
  those feature contracts existed at bridge/gtkb-spec-pipeline-f6-004.md:47.
- The F1-F8 cross-check places F6-B after Phase 3 because it requires F1
  `authority='inferred'` and F3 quality validation at
  bridge/gtkb-f1f8-cross-check-001.md:57.
- The current target repo exposes `score_spec_quality()` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1079.

**Risk/impact:** Generated seed specs could be written as inferred requirements
without the approved quality/tier validation loop. That weakens F6's role as a
safe seed-spec generator and can let low-quality generated templates enter the
KB without the F3 gate that Phase B was supposed to add.

**Required action:** Add the F3 quality-validation behavior to the F6 plan.
At minimum, state when generated specs are scored, how failures/warnings are
reported in dry-run and apply modes, and add tests proving
`score_spec_quality()` or an equivalent F3 API is exercised for generated
specs.

### 3. Blocking: F8 stale detection is contradictory and has no tests

**Claim:** Phase 4 implements F8 stale-spec detection and exposes it through
`gt kb reconcile --stale N`.

**Evidence:**
- Phase 4 lists stale specs as one of F8's four reconciliation categories at
  bridge/gtkb-phase4-implementation-001.md:18 and
  bridge/gtkb-phase4-implementation-001.md:252.
- Phase 4 defines `find_stale_specs()` and says bootstrap behavior returns an
  empty list when fewer than `staleness_threshold_sessions` snapshots exist at
  bridge/gtkb-phase4-implementation-001.md:274.
- The next paragraph says it falls back to `specifications.changed_at` when
  snapshot history is insufficient at bridge/gtkb-phase4-implementation-001.md:285.
- Phase 4 exposes `--stale N` in the CLI at
  bridge/gtkb-phase4-implementation-001.md:303.
- Phase 4's 20 F8 tests cover orphan detection, plain-text assertion safety,
  authority conflicts, expired provisional specs, and duplicates, but no stale
  detection path at bridge/gtkb-phase4-implementation-001.md:321.
- The cross-check GO explicitly required preserving the approved `changed_at`
  fallback or submitting a revised F8 bridge proposal that removes it at
  bridge/gtkb-f1f8-cross-check-002.md:50.
- The approved F8 proposal includes a stale detection fallback test at
  bridge/gtkb-spec-pipeline-f8-003.md:154.

**Risk/impact:** The implementation can ship a `--stale` flag and
`find_stale_specs()` with ambiguous bootstrap behavior and no regression
coverage. It can also silently lose the approved `changed_at` fallback despite
the cross-check explicitly warning against that.

**Required action:** Revise the stale contract before implementation. Choose
one precise behavior:

1. Preserve the approved `changed_at` fallback when F7 snapshots are absent or
   insufficient, and add tests for fallback and snapshot-backed stale detection.
2. Or submit an explicit revised F8 scope that removes fallback behavior and
   explains why the prior F8/cross-check condition is being changed.

The CLI `--stale` path must have at least one test.

### 4. Blocking: F8 authority-conflict semantics drift from the approved structural overlap model

**Claim:** Phase 4 implements F8 authority-conflict detection.

**Evidence:**
- The approved F8 revision defines authority conflicts as stated-vs-inferred
  specs with same section, same scope, and overlapping assertion file targets at
  bridge/gtkb-spec-pipeline-f8-003.md:17 and
  bridge/gtkb-spec-pipeline-f8-003.md:29.
- Later F8 revisions preserve typed assertion-target extraction for both specs
  and exact target comparison at bridge/gtkb-spec-pipeline-f8-009.md:138 and
  bridge/gtkb-spec-pipeline-f8-011.md:155.
- The final F8 approved test plan carries alias overlap, composition overlap,
  and glob-string overlap for authority conflicts at
  bridge/gtkb-spec-pipeline-f8-013.md:109.
- Phase 4 instead describes authority conflicts as "the same spec has
  inconsistent authority signals across aliases" and mentions `affected_by`
  conflicts and `_find_matching_constraints()` at
  bridge/gtkb-phase4-implementation-001.md:289.
- Phase 4's own authority-conflict tests still refer to two specs with the same
  assertion target and different authority values at
  bridge/gtkb-phase4-implementation-001.md:342.

**Risk/impact:** The implementation guidance and the test list point at
different detectors. An implementer could follow the prose and build an
`affected_by`/constraint-style checker that misses the approved
stated-vs-inferred structural target conflicts.

**Required action:** Restore the approved F8 authority-conflict algorithm in the
proposal: compare pairs of specs with different authority values, preserve the
same-section/same-scope gate unless explicitly revised, and use normalized
assertion-target overlap for aliases, composition children, and exact glob
strings. If `affected_by` conflicts are desired, define them as an additional
separate detector with tests.

### 5. Blocking: F8 proposes duplicate assertion-target extraction despite the current shared helper

**Claim:** Phase 4 should add a separate F8 `_extract_file_targets()` helper
because F2 and F8 have different target-record types.

**Evidence:**
- Phase 4 explicitly proposes a separate helper from F2's
  `_extract_assertion_targets()` at bridge/gtkb-phase4-implementation-001.md:168.
- Phase 4 says both helpers can live next to each other and import the same
  private internals at bridge/gtkb-phase4-implementation-001.md:177.
- The cross-check GO required avoiding duplicated assertion-target extraction,
  creating a shared public or semi-public helper before duplicating the logic,
  and keeping F2/F8 aligned to that helper at
  bridge/gtkb-f1f8-cross-check-002.md:74.
- Current `AssertionTarget` is already documented as "Used by F2 (Change Impact
  Analysis) and F8 (Provenance Reconciliation)" at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:60.
- Current `_extract_assertion_targets()` already skips non-dict assertions,
  recurses into `all_of`/`any_of`, distinguishes `glob`, `file_exists`,
  `json_path`, and grep-style targets, and carries `file_is_glob` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:73.

**Risk/impact:** A second extractor duplicates the exact drift-prone logic that
multiple earlier F8 NO-GOs were trying to stabilize. The current checkout now
has a shared helper that already matches the needed runner semantics, so adding
another helper increases maintenance risk without a demonstrated need.

**Required action:** Revise F8 to reuse `_extract_assertion_targets()` or first
promote/adapt it into an explicitly shared public or semi-public API. If F8
still needs a view model such as `TypedFileTarget`, derive it from
`AssertionTarget` instead of reimplementing normalization and dispatch.

## Conditions To Preserve

The next revision should keep the parts that are aligned:

- F6 generated specs use `authority='inferred'` until explicit owner promotion
  to `authority='stated'`.
- F6 preserves `dry_run=True` as the default and never overwrites existing specs.
- F8 preserves v7 non-dict/plain-text assertion skip behavior.
- F8 preserves type-specific glob dispatch: `glob` always uses glob dispatch;
  `grep`, `grep_absent`, and `count` use glob dispatch only when the file target
  contains `*`; `file_exists` and `json_path` remain literal.
- F8 preserves alias and composition coverage for orphan and authority-conflict
  checks.

## Verification

- Read the full active bridge entry for `gtkb-phase4-implementation` and
  bridge/gtkb-phase4-implementation-001.md.
- Read referenced approvals and relevant history:
  bridge/gtkb-spec-pipeline-f6-003.md,
  bridge/gtkb-spec-pipeline-f6-004.md,
  bridge/gtkb-spec-pipeline-f8-003.md,
  bridge/gtkb-spec-pipeline-f8-009.md,
  bridge/gtkb-spec-pipeline-f8-011.md,
  bridge/gtkb-spec-pipeline-f8-012.md,
  bridge/gtkb-spec-pipeline-f8-013.md,
  bridge/gtkb-spec-pipeline-f8-014.md,
  bridge/gtkb-f1f8-cross-check-001.md, and
  bridge/gtkb-f1f8-cross-check-002.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current
  scaffold, CLI, F1/F3 APIs, and assertion-target helper behavior.
- `rg -n "scaffold_specs|reconciliation|_extract_file_targets" src tests docs`
  returned no matches in groundtruth-kb, confirming Phase 4 is not already
  implemented.
- `python -m pytest -q --tb=short -p no:cacheprovider` passed in
  groundtruth-kb: `561 passed, 1 warning in 72.50s`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb:
  `61 files already formatted`.
- `python scripts/check_docs_cli_coverage.py` passed in groundtruth-kb:
  `All documentation checks passed.`

## Required Revision

Prime should revise Phase 4 before implementation. A GO can be reconsidered
when the proposal restores F6 `scaffold_project()` integration and F3 quality
validation, clarifies and tests F8 stale detection/fallback behavior, restores
the approved F8 authority-conflict detector, and reuses or promotes the current
shared assertion-target helper instead of adding a parallel extractor.
