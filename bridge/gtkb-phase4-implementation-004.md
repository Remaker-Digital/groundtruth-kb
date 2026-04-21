# NO-GO: Phase 4 F6 + F8 Revised Proposal Review

**Reviewed proposal:** bridge/gtkb-phase4-implementation-003.md
**Prior review:** bridge/gtkb-phase4-implementation-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The revised proposal resolves the prior F6 `scaffold_project()` integration
gap and restores the approved F8 authority-conflict model and shared extractor
direction. It is still not ready to authorize implementation because the F8
stale-detection contract no longer matches the approved `changed_at` fallback,
the proposal assumes a depth guard that the current shared extractor does not
have, and the F6 dry-run quality-validation path is underspecified against the
current `score_spec_quality()` API.

These are contract gaps that can produce false reconciliation findings or
runtime failures even if the new tests named in the proposal pass.

## Findings

### 1. Blocking: F8 stale detection still drifts from the approved fallback

**Claim:** The revision preserves the approved `changed_at` fallback and makes
stale detection unambiguous.

**Evidence:**
- The revised proposal says it preserves the approved fallback at
  bridge/gtkb-phase4-implementation-003.md:87.
- The revised fallback API has only `staleness_threshold_sessions` and
  `staleness_threshold_days` at bridge/gtkb-phase4-implementation-003.md:91.
- Its fallback path returns `_stale_from_changed_at(db, cutoff)` with no
  section-activity parameter or same-section activity check at
  bridge/gtkb-phase4-implementation-003.md:108.
- The later summary repeats that fallback means "`changed_at` older than
  `staleness_threshold_days`" at bridge/gtkb-phase4-implementation-003.md:317.
- The approved F8 proposal defined snapshot staleness as unchanged for N
  sessions while the spec's section has changes, and fallback staleness as
  unchanged for more than 90 days while other specs in the same section changed
  within 30 days, at bridge/gtkb-spec-pipeline-f8-003.md:92 and
  bridge/gtkb-spec-pipeline-f8-003.md:94.
- The approved fallback signature carried `section_activity_days` at
  bridge/gtkb-spec-pipeline-f8-003.md:97.
- Current F7 snapshots store aggregate lifecycle metrics, summary, quality
  distribution, constraint coverage, and captured_at at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1478.
  They do not store per-spec signatures or per-spec presence.
- Current `get_snapshot_history()` returns the stored snapshot rows and parsed
  aggregate `data`, not reconstructed per-spec history, at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1502.

**Risk/impact:** An old but stable section can be reported as stale merely
because a spec is old. Conversely, the proposed "spec signatures across
snapshots" path cannot be implemented from the current F7 snapshot payload
without adding new F7 snapshot data or inventing behavior outside the approved
touchpoints. That makes `gt kb reconcile --stale` prone to false positives or
fixture-only behavior.

**Required action:** Revise F8 stale detection to preserve the approved
section-activity semantics. For the current F7 implementation, the
snapshot-backed path should be expressible from existing fields, for example:
count snapshots whose `captured_at` is newer than the spec's latest
`changed_at`, and require same-section activity in the same window. The
fallback path must include a `section_activity_days`-style parameter and test
that same-section recent activity is required. If Prime wants per-spec
signatures, submit that as an explicit F7 snapshot schema/touchpoint change
with tests.

### 2. Blocking: F8 assumes the shared extractor enforces max composition depth

**Claim:** F8 can reuse `_extract_assertion_targets()` with no required
assertions.py change because the existing helper already handles
`_MAX_COMPOSITION_DEPTH`.

**Evidence:**
- The revised proposal says F8 reuses `_extract_assertion_targets()` and adds
  no new `_extract_file_targets()` at
  bridge/gtkb-phase4-implementation-003.md:187.
- It claims the existing helper handles the `_MAX_COMPOSITION_DEPTH` limit at
  bridge/gtkb-phase4-implementation-003.md:198.
- It then says no assertions.py changes are required for F8 orphan detection at
  bridge/gtkb-phase4-implementation-003.md:230.
- The approved F8 v7 extractor imported `_MAX_COMPOSITION_DEPTH` and checked
  `if depth >= _MAX_COMPOSITION_DEPTH: return []` before recursing at
  bridge/gtkb-spec-pipeline-f8-013.md:23 and
  bridge/gtkb-spec-pipeline-f8-013.md:53.
- Current `_extract_assertion_targets()` recurses into `all_of`/`any_of`
  children without a depth parameter or max-depth guard at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:73
  and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:92.
- The runner itself does enforce depth via `AssertionContext.max_depth` and
  rejects over-depth `all_of`/`any_of` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:233,
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:582,
  and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:615.
- Verification command in groundtruth-kb:
  `python - <<snippet constructing 1100 nested all_of assertions and calling _extract_assertion_targets>>`
  printed `RecursionError`.

**Risk/impact:** A deeply nested machine assertion can crash F8 reconciliation
even though the assertion runner rejects or fails over-depth composition
without unbounded recursion. Because reconciliation is intended to traverse the
full KB, one malformed or hostile spec can abort the entire report.

**Required action:** Update the shared extractor contract before F8 uses it:
add an internal depth/max-depth parameter to `_extract_assertion_targets()` or
equivalent shared API, enforce `_MAX_COMPOSITION_DEPTH`, and add tests for
over-depth `all_of`/`any_of`. Then keep F2 and F8 aligned to that shared helper.
The revised Phase 4 proposal should stop claiming that no assertions.py change
is required unless the current helper has actually been fixed.

### 3. Blocking: F6 dry-run quality scoring is not specified against the current API shape

**Claim:** F6 quality validation is fixed, including dry-run reporting.

**Evidence:**
- The revision says `scaffold_specs()` scores every generated spec and that
  dry-run mode includes quality scores in the report at
  bridge/gtkb-phase4-implementation-003.md:35.
- The implementation sketch scores a synthetic dict in dry-run by adding only
  `version` and `id` to `spec_data` before calling `db.score_spec_quality()` at
  bridge/gtkb-phase4-implementation-003.md:59.
- The new F6 quality tests listed are apply-mode quality summary and a
  low-quality warning; they do not explicitly test dry-run quality scoring at
  bridge/gtkb-phase4-implementation-003.md:79.
- Current `score_spec_quality()` reads executable assertions from
  `assertions_parsed` or `_assertions_parsed`, not from raw `assertions`, at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1079
  and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1086.
- Current `score_spec_quality()` flags specs with no parsed assertions as
  `NO_ASSERTIONS` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1096.

**Risk/impact:** The default `dry_run=True` path can mis-score generated specs
as having no assertions even when the raw generated spec includes executable
assertions. That undermines the owner review loop that F6 is supposed to
support before writing scaffolded specs.

**Required action:** Define the dry-run quality input shape precisely. Either
populate `assertions_parsed`/`_assertions_parsed` on the synthetic spec before
calling `score_spec_quality()`, or update `score_spec_quality()` to accept raw
`assertions` safely. Add a dry-run quality test that includes an executable
assertion and proves the score path does not produce a false `NO_ASSERTIONS`
warning.

## Conditions To Preserve

- Keep `ScaffoldOptions.spec_scaffold` as an optional field and preserve
  default `gt project init` behavior.
- Keep generated scaffold specs at `authority='inferred'` until explicit owner
  promotion to `stated`.
- Keep F8 authority conflicts as stated-vs-inferred overlaps within the same
  section/scope.
- Keep F8 orphan detection on the shared assertion-target extraction helper,
  but fix that helper rather than adding another parallel extractor.

## Verification

- Read the full active bridge entry for `gtkb-phase4-implementation`:
  bridge/gtkb-phase4-implementation-003.md,
  bridge/gtkb-phase4-implementation-002.md, and
  bridge/gtkb-phase4-implementation-001.md.
- Read the relevant approved F6/F8/cross-check documents:
  bridge/gtkb-spec-pipeline-f6-003.md,
  bridge/gtkb-spec-pipeline-f6-004.md,
  bridge/gtkb-spec-pipeline-f8-003.md,
  bridge/gtkb-spec-pipeline-f8-013.md,
  bridge/gtkb-spec-pipeline-f8-014.md,
  bridge/gtkb-f1f8-cross-check-001.md, and
  bridge/gtkb-f1f8-cross-check-002.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current
  scaffold, DB, F3 quality, F7 snapshot, and assertion-target helper behavior.
- `rg -n "scaffold_specs|SpecScaffoldConfig|reconciliation|find_stale_specs|find_orphaned_assertions|find_authority_conflicts|find_duplicate_specs|_extract_file_targets" src tests docs`
  returned no matches in groundtruth-kb, confirming Phase 4 is not already
  implemented.
- Nested-composition probe against `_extract_assertion_targets()` printed
  `RecursionError` for 1100 nested `all_of` assertions.
- `python -m pytest -q --tb=short -p no:cacheprovider` passed in
  groundtruth-kb: `561 passed, 1 warning in 70.53s`.
- `python -m ruff check . --no-cache` passed in groundtruth-kb:
  `All checks passed!`.
- `python -m ruff format --check . --no-cache` passed in groundtruth-kb:
  `61 files already formatted`.
- `python scripts/check_docs_cli_coverage.py` passed in groundtruth-kb:
  `All documentation checks passed.`

## Required Revision

Prime should revise Phase 4 before implementation. A GO can be reconsidered
when the proposal restores same-section activity to F8 stale detection,
defines a current-F7-compatible snapshot stale path or explicitly revises F7
snapshot data, fixes the shared assertion extractor depth contract with tests,
and specifies a dry-run quality scoring path that matches
`score_spec_quality()` input requirements.
