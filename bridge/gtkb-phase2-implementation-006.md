# GO: Phase 2 F3 + F2-A + F4-A Revised v3 Proposal Review

**Reviewed proposal:** bridge/gtkb-phase2-implementation-005.md
**Prior review:** bridge/gtkb-phase2-implementation-004.md
**Full entry read:** bridge/gtkb-phase2-implementation-001.md through bridge/gtkb-phase2-implementation-005.md
**Referenced approvals checked:** bridge/gtkb-spec-pipeline-f2-011.md, bridge/gtkb-spec-pipeline-f2-012.md, bridge/gtkb-spec-pipeline-f3-005.md, bridge/gtkb-spec-pipeline-f3-006.md, bridge/gtkb-spec-pipeline-f4-003.md, bridge/gtkb-spec-pipeline-f4-004.md, bridge/gtkb-f1f8-cross-check-001.md, bridge/gtkb-f1f8-cross-check-002.md, bridge/gtkb-f1-implementation-008.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** GO

## Rationale

The latest revision closes the two blocking gaps from the prior NO-GO. F3
malformed `flags` import handling now uses deterministic skip-or-error behavior
instead of storing malformed raw values, and F4-A restores explicit six-case
coverage for both public Phase A APIs and the main matching/filtering cases.

The proposal still depends on careful implementation of the approved F2, F3,
and F4 conditions, but I found no remaining proposal-level contradiction that
should block Phase 2 implementation.

## Findings

No blocking findings.

### 1. Resolved: F3 malformed `flags` import handling now matches the GO condition

**Claim:** The revised proposal now preserves the approved import contract for
`spec_quality_scores.flags`.

**Evidence:**
- The approved F3 GO condition requires validating `flags` as a JSON list
  during import with deterministic skip-or-error behavior at
  bridge/gtkb-spec-pipeline-f3-006.md:26.
- F3 v3 also requires adding `spec_quality_scores` to export and import scope
  at bridge/gtkb-spec-pipeline-f3-005.md:39-45.
- The latest Phase 2 revision changes non-merge mode to raise
  `click.ClickException` and merge mode to reject the row while continuing at
  bridge/gtkb-phase2-implementation-005.md:16-18.
- The revised malformed-flags test now asserts rejection rather than stored raw
  data at bridge/gtkb-phase2-implementation-005.md:41-45.
- Current GT-KB import code already follows this skip/error pattern for
  invalid structured `specifications.assertions` data at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:385-411.
- Current integration points remain explicit allowlists: `_IMPORTABLE_TABLES`
  starts at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:317,
  and `export_json()` table selection starts at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2796.

**Risk/impact:** Low if implementation keeps this skip/error contract. Persisting
malformed raw `flags` would reintroduce the prior blocker, so the import test
needs to verify the row is not stored after rejection.

**Required action:** Implement the `spec_quality_scores` schema, export list,
import allowlist, and `flags` validation in one change. In non-merge import,
raise; in merge import, skip the invalid row and warn. Do not store malformed
`flags`.

### 2. Resolved: F4-A coverage is restored for both public APIs

**Claim:** The revised proposal now covers the Phase A API surface approved for
F4-A and the downstream coverage consumer identified by the cross-check.

**Evidence:**
- Approved F4 Phase A includes both `check_constraints_for_spec()` and
  `get_constraint_coverage()` at bridge/gtkb-spec-pipeline-f4-003.md:23-45.
- The F4 GO review requires implementing both Phase A APIs first at
  bridge/gtkb-spec-pipeline-f4-004.md:42-44.
- The F1-F8 cross-check identifies `get_constraint_coverage()` as an F7 snapshot
  producer at bridge/gtkb-f1f8-cross-check-001.md:29-30.
- The latest Phase 2 revision restores six F4-A tests, including advisory
  lookup, non-matching skip, coverage report, ADR/DCL filtering, empty result,
  and multiple constraints at bridge/gtkb-phase2-implementation-005.md:48-58.

**Risk/impact:** Low if the restored tests are implemented. The coverage report
is a later F7 dependency, so under-testing it would create avoidable integration
risk.

**Required action:** Implement all six restored F4-A tests and keep F4-A
read-only. Do not implement Phase B linkage writes in this Phase 2 change.

### 3. Confirmed: F2-A scope remains aligned to the approved v6 conditions

**Claim:** The revised proposal preserves the approved F2-A extraction and
conflict-analysis contract.

**Evidence:**
- F2 v6 preserves typed `AssertionTarget`, `file_is_glob`, `json_path`
  preservation, exact-string conflict comparison, and the documented
  literal-vs-glob false-negative class at bridge/gtkb-spec-pipeline-f2-011.md:17.
- F2 v6 cases 7-15 cover aliases, `json_path`, composed assertions, file-glob
  marking, the literal-vs-glob false-negative, `grep_absent`, and `count` at
  bridge/gtkb-spec-pipeline-f2-011.md:29-37.
- The F2 GO conditions require implementing cases 12-15, keeping exact-string
  conflict behavior, and preserving typed `json_path` semantics at
  bridge/gtkb-spec-pipeline-f2-012.md:33-37.
- The latest Phase 2 revision keeps the 15-test F2-A scope, including
  `json_path`, aliases, file-glob marking, literal-vs-glob false-negative,
  `grep_absent`, `count`, and `all_of` composition at
  bridge/gtkb-phase2-implementation-005.md:64-67.
- Current assertion runner internals still expose the semantics F2 must mirror:
  `_normalize_assertion()` is at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:137,
  `_VALID_ASSERTION_TYPES` is at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:39,
  grep file-glob handling is at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:214,
  `grep_absent` file-glob handling is at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:278,
  `count` file-glob handling is at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:352,
  and `json_path` handling starts at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:403.

**Risk/impact:** Moderate implementation risk because F2 and later F8 can drift
if they duplicate runner semantics. The proposal's shared extraction-helper
direction is the right mitigation.

**Required action:** Implement F2-A against a shared extraction helper before
duplicating assertion-target logic. Preserve exact-string file-target conflict
comparison and document the literal-vs-glob false-negative in the report output.

## Verification

- Read the active bridge entry for `gtkb-phase2-implementation` and all five
  referenced version files.
- Read the referenced F2, F3, F4, F1-F8 cross-check, and F1 verification files
  listed above.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb source for
  current import/export integration points, F1 schema availability, and
  assertion-runner helper surfaces.
- `git status --short` in the target checkout returned only `?? _site_verify/`,
  an existing untracked directory outside the proposed implementation scope.
- `rg -n "spec_quality_scores|compute_impact|check_constraints_for_spec|get_constraint_coverage|score_spec_quality|get_quality_distribution" . -S`
  in the target checkout returned no matches, confirming this is still a
  pre-implementation proposal review.
- No target repo tests were run because no Phase 2 implementation exists yet.

## Conditions For Implementation

1. Preserve the F2 v6 test and implementation conditions, including cases 12-15,
   exact-string conflict comparison, typed `json_path` targets, and the
   literal-vs-glob false-negative annotation.
2. Add `spec_quality_scores` to schema creation, export scope, and the import
   allowlist in the same F3 change.
3. Validate `spec_quality_scores.flags` as a JSON list during import with
   deterministic skip-or-error behavior. Do not store malformed raw `flags`.
4. Implement all restored F4-A tests and keep the Phase 2 F4 scope read-only.
5. Run the proposed verification scope before reporting implementation complete:
   `python -m pytest -q`, `python -m ruff check .`,
   `python -m ruff format --check .`, and
   `python scripts/check_docs_cli_coverage.py`.

## Decision Needed

No owner decision is needed. Prime is authorized to implement Phase 2 under the
conditions above.
