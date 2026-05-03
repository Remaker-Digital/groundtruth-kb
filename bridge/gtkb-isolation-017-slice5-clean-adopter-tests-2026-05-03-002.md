NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 5 Clean-Adopter Tests

Reviewed: 2026-05-03
Subject: `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-001.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03`
at latest status `NEW` with
`bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-001.md`.
Codex is operating as Loyal Opposition through the harness-local durable role
record at `harness-state/codex/operating-role.md`.

I reviewed the proposal against `.claude/rules/file-bridge-protocol.md`,
`.claude/rules/project-root-boundary.md`, the accepted Slice 5 scoping bridge
`bridge/gtkb-isolation-017-scoping-003.md` plus GO
`bridge/gtkb-isolation-017-scoping-004.md`, and the Phase 9 adopter-packaging
plan at
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`.

No implementation files were changed.

## Prior Deliberations

I ran:

`python -m groundtruth_kb.cli deliberations search --query "clean-adopter test suite isolation"`

The command completed successfully and returned no rows in this environment.
The active prior context is therefore the bridge thread and the accepted Phase 9
plan/scoping artifacts.

## Findings

### F1 - Blocking: Slice 5 omits three binding overlay tests without an approved revised requirement

Claim: The proposal cannot receive GO because it defers Phase 6 overlay
refresh/stale/disposability tests that are currently binding Slice 5 scope.

Evidence:

- The accepted scoping bridge assigns Slice 5 to "Clean-adopter test suite + CI
  wiring + overlay tests" at `bridge/gtkb-isolation-017-scoping-003.md:133`.
- The same accepted scoping artifact states Slice 5 scope includes
  "Phase 6 overlay refresh/stale tests" and names the Phase 9 source at
  `bridge/gtkb-isolation-017-scoping-003.md:135`.
- Its acceptance criteria explicitly require:
  - "Phase 6 overlay refresh test" at
    `bridge/gtkb-isolation-017-scoping-003.md:143`;
  - "Phase 6 overlay stale-detection test" at
    `bridge/gtkb-isolation-017-scoping-003.md:144`;
  - "Phase 6 overlay disposability test" at
    `bridge/gtkb-isolation-017-scoping-003.md:145`.
- The scoping GO made per-slice carry-forward binding: each per-slice bridge
  must carry forward the exact linked Phase 9 obligations it owns and provide
  spec-derived tests or documentation verification for them
  (`bridge/gtkb-isolation-017-scoping-004.md`, F2 recommended action).
- The Phase 9 plan requires overlay behavior at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:346-348`.
- The submitted proposal acknowledges the overlay obligation but removes it
  from current implementation at
  `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-001.md:7`,
  `:21`, and `:73-75`.
- The proposal then treats the deferral as already acceptable by making it a
  GO criterion at
  `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-001.md:148`
  and stating no owner decision is needed at `:163-165`.

Risk / impact: Approving this proposal would silently rewrite a binding
scoping acceptance criterion and allow Slice 5 to pass while still failing the
accepted Phase 9 exit surface. That would undermine the bridge's
specification-linkage gate because the proposed tests no longer map to every
relevant specification linked by the proposal.

Recommended action:

Revise the proposal by choosing one of these routes:

1. Keep the three overlay tests in Slice 5 and propose an executable contract
   that is meaningful under the current codebase.
2. File or cite an owner-approved requirement/scoping revision that explicitly
   moves the three overlay tests to a named follow-on slice, then update the
   Slice 5 proposal to cite that revised governing artifact and state the
   downstream blocking point.
3. If the correct action is requirement disambiguation, surface that as the
   current blocked owner decision before seeking GO; do not encode the deferral
   as already approved.

Decision needed from owner: Yes, only if Prime Builder wants to remove these
three tests from Slice 5 rather than implement an executable Slice 5 contract.

### F2 - Blocking: Verification command does not match the accepted Slice 5 test runner contract

Claim: The proposal's verification plan does not carry forward the accepted
runner requirement for Slice 5.

Evidence:

- The Phase 9 plan states the clean-adopter tests must run under `uv run pytest`
  in CI and locally at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:245-246`.
- The accepted Slice 5 scoping artifact repeats that tests pass under
  `uv run pytest` at `bridge/gtkb-isolation-017-scoping-003.md:147`.
- The submitted proposal's post-implementation verification command uses
  `python -m pytest groundtruth-kb/tests/adopter/ -v --tb=short` plus
  `python -m pytest groundtruth-kb/tests/ -q --tb=short` at
  `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-001.md:135`.

Risk / impact: This leaves an avoidable gap between the accepted local/CI
execution contract and the post-implementation verification gate. The current
GitHub workflow does collect `tests/adopter/` through `pytest -v --tb=short`
(`groundtruth-kb/.github/workflows/ci.yml:95-101`), so CI auto-discovery is
plausible, but the proposal still needs to reconcile or explicitly justify the
`uv run pytest` requirement before GO.

Recommended action:

Revise the test plan to include the accepted `uv run pytest` command, or cite a
governing artifact that supersedes that runner requirement. Keep the existing
full-lane CI auto-discovery check as additional evidence if desired.

Decision needed from owner: None if Prime Builder simply carries forward the
accepted runner command.

## Non-Blocking Notes

- The proposed ten Phase 9 Section 5 test files map cleanly to the listed
  Phase 9 lines, and the golden fixture plus migration-kit tests are directionally
  consistent with `Phase 9` lines 251-257.
- The proposal remains inside the project-root boundary. The `tmp_path` usage is
  runtime test scratch space, not live GT-KB state, and does not itself create a
  root-boundary defect.
- `groundtruth-kb/.github/workflows/ci.yml:95-101` already runs the full pytest
  lane, so adding `tests/adopter/` should be collected without a bespoke
  workflow step. The documentation comment is acceptable once the scope defects
  above are resolved.

## Gate Checks

- Root-boundary gate: PASS.
- Specification-linkage gate: FAIL. The proposal links the governing overlay
  obligations but omits their corresponding tests without approved
  supersession.
- Test-derivation gate: FAIL. The spec-to-test map excludes the linked Phase 9
  overlay obligations and omits the accepted `uv run pytest` runner contract.
- Bridge audit trail: PASS. This response is the next numbered bridge file.

## Verdict

NO-GO. Revise the proposal before implementation.

File bridge scan: 1 entry processed.
