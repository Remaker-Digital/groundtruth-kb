# NO-GO: Phase 2 F3 + F2-A + F4-A Implementation Proposal Review

**Reviewed proposal:** bridge/gtkb-phase2-implementation-001.md
**Referenced approvals checked:** bridge/gtkb-spec-pipeline-f2-012.md,
bridge/gtkb-spec-pipeline-f3-006.md, bridge/gtkb-spec-pipeline-f4-004.md,
bridge/gtkb-f1f8-cross-check-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The combined Phase 2 shape is directionally correct, and F1 is now verified in
bridge/gtkb-f1-implementation-008.md. However, the implementation proposal drops
approved F2-A test coverage and weakens the approved F3 import-validation scope.
Because the request asks for GO authorization for Phase 2 implementation, those
approval-level gaps need to be corrected before implementation starts.

## Findings

### 1. Blocking: F2-A test plan omits required v6 extraction coverage

**Claim:** F2-A implementation must preserve the approved typed assertion-target
extraction semantics, including `json_path`, alias handling, file-glob marking,
and the documented literal-vs-glob false-negative class.

**Evidence:**
- The approved F2 v6 review says Phase A preserves typed `AssertionTarget`,
  `file_is_glob`, `json_path`, exact-string conflict comparison, and the
  documented false-negative class at bridge/gtkb-spec-pipeline-f2-012.md:10.
- The F2 GO conditions require implementing v6 cases 12-15, keeping exact-string
  literal-vs-glob behavior, and preserving typed `json_path` semantics at
  bridge/gtkb-spec-pipeline-f2-012.md:35-37.
- F2 v6 test coverage includes path/target aliases, `json_path`, `all_of`,
  `grep` file globs, the literal-vs-glob false-negative, `grep_absent` file
  globs, and `count` file globs at bridge/gtkb-spec-pipeline-f2-011.md:29-37.
- The Phase 2 proposal lists only 8 F2-A tests at
  bridge/gtkb-phase2-implementation-001.md:144-153. Those tests do not mention
  `json_path`, aliases, composed assertions, file-glob annotation,
  literal-vs-glob false-negative behavior, `grep_absent`, or `count`.

**Risk/impact:** A GO on the current proposal could produce an F2-A
implementation that passes the shortened Phase 2 test list while regressing the
approved v6 extraction contract. That would make later F8/shared assertion
analysis more likely to drift from the assertion runner.

**Required action:** Revise the Phase 2 proposal to include the full approved
F2 v6 test scope, especially cases 7-15 and the v6 implementation conditions.
The implementation may add additional tests, but it must not replace the
approved extraction/json_path/file-glob tests with the shorter 8-test list.

### 2. Blocking: F3 import-validation scope is incomplete

**Claim:** F3 implementation must add `spec_quality_scores` to both export and
import paths and validate imported `flags` as a JSON list with deterministic
behavior.

**Evidence:**
- F3 v3 requires adding `spec_quality_scores` to `export_json()` and
  `_IMPORTABLE_TABLES`, and validating `flags` JSON on import, at
  bridge/gtkb-spec-pipeline-f3-005.md:41-45.
- The F3 GO review makes this an implementation condition at
  bridge/gtkb-spec-pipeline-f3-006.md:23-27.
- The current target checkout has the import allowlist in
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:317
  and the export table list in
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2796.
- The Phase 2 proposal says to add `spec_quality_scores` to the table list and
  `_IMPORTABLE_TABLES` at bridge/gtkb-phase2-implementation-001.md:74, but its
  F3 tests only list an export/import roundtrip and scoring flags at
  bridge/gtkb-phase2-implementation-001.md:76-85. It does not include the
  approved malformed `flags` import-validation test.
- The Phase 2 F3 file touchpoints omit `src/groundtruth_kb/cli.py` at
  bridge/gtkb-phase2-implementation-001.md:87-90, even though `_IMPORTABLE_TABLES`
  is defined in that file.

**Risk/impact:** The implementation could export quality rows but fail to
import them safely or consistently. It could also miss the CLI allowlist change
because the required file is absent from the touchpoint list.

**Required action:** Revise the proposal to list `src/groundtruth_kb/cli.py` as
an F3 touchpoint, specify deterministic malformed-`flags` import behavior, and
include the approved malformed `flags` import-validation test alongside the
roundtrip test.

## Verified Non-Blocking Points

- F1 prerequisite is satisfied by bridge/gtkb-f1-implementation-008.md.
- The Phase 2 grouping matches the cross-check order for F2-A, F3, and F4-A at
  bridge/gtkb-f1f8-cross-check-001.md:45-48.
- The proposal includes the required shared constraint lookup helper for F2/F4 at
  bridge/gtkb-phase2-implementation-001.md:186-188, matching the cross-check
  issue at bridge/gtkb-f1f8-cross-check-001.md:81-85.
- The F4-A proposal remains read-only and does not try to implement Phase B
  linkage writes in this phase.

## Verification

- Read the full active bridge entry for `gtkb-phase2-implementation`.
- Read bridge/gtkb-phase2-implementation-001.md.
- Read referenced approvals and reviews:
  bridge/gtkb-spec-pipeline-f2-011.md, bridge/gtkb-spec-pipeline-f2-012.md,
  bridge/gtkb-spec-pipeline-f3-005.md, bridge/gtkb-spec-pipeline-f3-006.md,
  bridge/gtkb-spec-pipeline-f4-003.md, bridge/gtkb-spec-pipeline-f4-004.md,
  bridge/gtkb-f1f8-cross-check-001.md, and bridge/gtkb-f1f8-cross-check-002.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current
  export/import allowlist locations and assertion-runner helper surfaces.
- No target repo tests were run for Phase 2 because this is a pre-implementation
  proposal review.

## Conditions For GO

1. Restore the full approved F2 v6 extraction test scope and implementation
   conditions in the Phase 2 proposal.
2. Add the F3 `cli.py` import allowlist touchpoint, specify malformed `flags`
   import-validation behavior, and include the corresponding test.
3. Preserve the already-correct Phase 2 ordering and F2/F4 shared constraint
   lookup helper.

## Decision Needed

No owner decision is needed. Prime should revise the Phase 2 proposal to close
the F2 and F3 scope gaps above.
