# NO-GO: Phase 2 F3 + F2-A + F4-A Revised Proposal Review

**Reviewed proposal:** bridge/gtkb-phase2-implementation-003.md
**Prior review:** bridge/gtkb-phase2-implementation-002.md
**Full entry read:** bridge/gtkb-phase2-implementation-001.md through bridge/gtkb-phase2-implementation-003.md
**Referenced approvals checked:** bridge/gtkb-spec-pipeline-f2-011.md, bridge/gtkb-spec-pipeline-f2-012.md, bridge/gtkb-spec-pipeline-f3-005.md, bridge/gtkb-spec-pipeline-f3-006.md, bridge/gtkb-spec-pipeline-f4-003.md, bridge/gtkb-spec-pipeline-f4-004.md, bridge/gtkb-f1f8-cross-check-001.md, bridge/gtkb-f1f8-cross-check-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The revision fixes the prior F2-A scope gap and adds the missing F3 `cli.py`
touchpoint. It does not yet preserve the approved F3 import-validation contract.
The revised proposal says malformed `spec_quality_scores.flags` values should
be warned about and stored raw, but the approved F3 GO condition requires
validation as a JSON list with deterministic skip-or-error behavior.

Because this bridge item asks for GO authorization for implementation, the
proposal should not authorize a behavior that weakens an already-approved data
integrity condition.

## Findings

### 1. Blocking: F3 malformed `flags` import handling contradicts the approved GO condition

**Claim:** F3 implementation must validate `spec_quality_scores.flags` as a JSON
list on import, and malformed values must be handled by a deterministic skip or
error path.

**Evidence:**
- F3 v3 requires `spec_quality_scores` import validation where the `flags`
  column is validated as a JSON list on import at
  bridge/gtkb-spec-pipeline-f3-005.md:39-45.
- The F3 GO review makes this explicit as an implementation condition:
  "Validate `flags` as a JSON list during import, with deterministic
  skip-or-error behavior" at bridge/gtkb-spec-pipeline-f3-006.md:23-27.
- The revised Phase 2 proposal instead says malformed `flags` should log a
  warning and store the raw value at
  bridge/gtkb-phase2-implementation-003.md:43-48.
- The revised Phase 2 malformed-flags test expects `flags="not json"` to be
  stored and readable at bridge/gtkb-phase2-implementation-003.md:60-62,
  which is neither a skip nor an error.
- The current GT-KB import path already uses a skip/error pattern for invalid
  structured JSON in `specifications.assertions`: invalid values raise in
  non-merge mode or are rejected in merge mode at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:385-411.
- Current import/export integration points are explicit allowlists:
  `_IMPORTABLE_TABLES` is at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:317-335
  and `export_json()` table selection is at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2796-2816.

**Risk/impact:** Storing malformed `flags` preserves invalid data inside a table
whose only approved flag semantics are JSON-list semantics. That can make
`get_quality_history()` and later reporting code handle a third state that the
approved F3 proposal did not authorize: persisted malformed raw text.

**Required action:** Revise the F3 section so malformed `flags` import behavior
matches the approved skip-or-error contract. A compatible option is: in
non-merge mode, raise a `click.ClickException`; in merge mode, reject the row
and emit a warning, matching the existing assertion-validation pattern. Update
the malformed-flags test to assert the chosen skip-or-error behavior rather
than "stored and readable".

### 2. Blocking: F4-A test scope regressed from the Phase 2 proposal without explanation

**Claim:** F4-A implementation should keep automated coverage for both public
Phase A APIs and the main matching/filtering cases.

**Evidence:**
- Phase 2 v1 proposed six F4-A tests, including constraint coverage,
  ADR-vs-DCL filtering, empty results, and multiple matching constraints at
  bridge/gtkb-phase2-implementation-001.md:190-197.
- The revised proposal labels F4-A as "Unchanged from -001" at
  bridge/gtkb-phase2-implementation-003.md:75, but then reduces F4-A to two
  tests at bridge/gtkb-phase2-implementation-003.md:84-89 and summarizes the
  total as two F4-A tests at bridge/gtkb-phase2-implementation-003.md:101-104.
- The approved F4 Phase A API includes both `check_constraints_for_spec()` and
  `get_constraint_coverage()` at bridge/gtkb-spec-pipeline-f4-003.md:23-45.
- The F4 GO review requires Phase A to implement both
  `check_constraints_for_spec()` and `get_constraint_coverage()` at
  bridge/gtkb-spec-pipeline-f4-004.md:42-44.
- The cross-check identifies `get_constraint_coverage()` as a producer consumed
  by F7 snapshots at bridge/gtkb-f1f8-cross-check-001.md:28.

**Risk/impact:** A GO on the revised two-test scope could leave
`get_constraint_coverage()` and key matching edge cases under-tested even though
they are part of the approved Phase A API and later F7 integration depends on
the coverage output.

**Required action:** Restore the F4-A test scope from the Phase 2 v1 proposal,
or revise it with an equivalent explicit test set that covers
`get_constraint_coverage()`, ADR and DCL filtering, empty results, and multiple
matching constraints. If only two F4-A tests are intentional, explain why that
is sufficient despite the two public APIs and F7 consumer dependency.

## Verified Resolved Points

- F2-A now restores the approved 15-test scope, including aliases, `json_path`,
  composed assertions, file-glob marking, the literal-vs-glob false-negative,
  `grep_absent`, and `count` at bridge/gtkb-phase2-implementation-003.md:13-36.
- The revised proposal preserves the F2 GO implementation conditions from
  bridge/gtkb-spec-pipeline-f2-012.md:33-37.
- The F3 `src/groundtruth_kb/cli.py` touchpoint is now listed at
  bridge/gtkb-phase2-implementation-003.md:65-71.
- F4-A remains read-only and does not attempt Phase B linkage writes at
  bridge/gtkb-phase2-implementation-003.md:84-89.
- F1 prerequisite remains satisfied by
  bridge/gtkb-f1-implementation-008.md.

## Verification

- Read the active bridge entry for `gtkb-phase2-implementation` and all three
  referenced version files.
- Read the referenced F2, F3, F4, and F1-F8 cross-check approvals listed above.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current
  import/export integration points and existing structured JSON validation
  behavior.
- `rg -n "spec_quality_scores" .` in the target checkout returned no matches,
  confirming this is still a proposal review rather than an implementation
  verification.
- `rg -n "_IMPORTABLE_TABLES|def export_json|spec_quality_scores|flags" src/groundtruth_kb -S`
  located the current import allowlist at `src/groundtruth_kb/cli.py:317` and
  export function at `src/groundtruth_kb/db.py:2779`.
- No target repo tests were run because this was a pre-implementation proposal
  review. The blocker is in the proposal contract, not in implemented code.

## Conditions For GO

1. Change F3 malformed `flags` import handling from "warn and store raw" to a
   deterministic skip-or-error behavior, and update the test plan accordingly.
2. Restore or equivalently specify F4-A tests that cover both Phase A APIs and
   the main constraint matching/filtering cases.
3. Preserve the resolved F2-A v6 test scope and F3 `cli.py` touchpoint.

## Decision Needed

No owner decision is needed. Prime should revise the Phase 2 proposal to close
the F3 import-validation contradiction and the F4-A test-scope regression.
