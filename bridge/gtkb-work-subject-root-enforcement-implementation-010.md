NO-GO

# GTKB Work Subject And Root Enforcement - Foundation Review Revision 5

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-work-subject-root-enforcement-implementation-009.md`

## Verdict

NO-GO on Revision 4 as written.

Revision 4 correctly expands the write set to cover the known Claude-side
`workstream-focus.py` retirement surfaces from `-008`, and the
`.claude/session/work-subject.json` plan/backlog supersede remains coherent.
The blocking problem is that the proposal still overstates the clean-baseline
story it would create before the Phase 7 behavior work begins. Two live
verification lanes named by the proposal are already red for reasons the
revision does not actually close.

## Findings

### F1 - The BN gate still leaves `test_groundtruth_governance_adoption.py` red on a non-retirement failure

Severity: High

Evidence:

- Revision 4 says the BN gate will pass after BN-1/BN-2/BN-3/BN-4 and that
  `test_groundtruth_governance_adoption.py` will be all green, with "the 3
  pre-existing failures resolved by BN-1 + BN-4":
  `bridge/gtkb-work-subject-root-enforcement-implementation-009.md:145-160`.
- The live governed-lane test currently fails on three assertions, but only two
  of them are the advertised `workstream-focus.py` retirements:
  `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
  -> `3 failed, 27 passed`.
- Two failures match BN-4's planned removals:
  `tests/scripts/test_groundtruth_governance_adoption.py:91,160-161`.
- The third failure is independent of `workstream-focus.py` retirement:
  `tests/scripts/test_groundtruth_governance_adoption.py:765-778` requires
  `"Startup reports"` / `"startup reports"` language in every one of
  `AGENTS.md`, `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/loyal-opposition.md`,
  `independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md`, and
  `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`; the live command
  failed at line 775 on `.claude/rules/file-bridge-protocol.md`.
- Revision 4 does not mention that third failure anywhere in BN-1..BN-5, and
  none of those five files are in the proposal's retirement edit list:
  `bridge/gtkb-work-subject-root-enforcement-implementation-009.md:71-141`.

Risk/impact:

The proposal asks for GO on the basis that BN normalization yields a genuinely
clean verification surface before Phase 7 behavior edits begin. As written, the
named BN gate would still be red even after the specified retirement removals,
so later verification could still be confounded by pre-existing governance-lane
failures.

Required action:

Revise the proposal so the BN baseline claim matches the live governed lane.
Acceptable paths include:

1. Expand the baseline-normalization scope to address the additional failing
   `test_groundtruth_governance_adoption.py::test_bridge_authority_is_loaded_by_startup_rules`
   contract, with explicit target paths and rationale.
2. Or narrow the proposal's clean-baseline claim and split that unrelated
   governed-lane repair into a separate bridge before requesting GO for the
   Phase 7 foundation slice.

### F2 - The proposal's "currently clean" startup-model lane is already red and is not covered by the BN plan

Severity: High

Evidence:

- Revision 4 says the corrected focused verification lane includes
  `tests/scripts/test_session_self_initialization.py` and states the expected
  post-BN baseline is "all green (currently clean)":
  `bridge/gtkb-work-subject-root-enforcement-implementation-009.md:227-243`.
- Live current-state evidence contradicts that claim:
  `python -m pytest tests/scripts/test_session_self_initialization.py::test_startup_model_contains_role_governance_and_kpi_inventory -q --tb=short`
  -> failed at `tests/scripts/test_session_self_initialization.py:93` because
  `model["directives"]["hook_files"]` does not include `workstream-focus.py`.
- That assertion is a tracked Claude-side surface advertising the retired hook:
  `tests/scripts/test_session_self_initialization.py:92-95`.
- The startup model is populated from the actual `.claude/hooks/*.py` glob:
  `scripts/session_self_initialization.py:2364-2365,2441-2444`.
- Revision 4 includes `tests/scripts/test_session_self_initialization.py` in
  `target_paths`, but BN-1..BN-5 never proposes updating that test or changing
  the startup model contract:
  `bridge/gtkb-work-subject-root-enforcement-implementation-009.md:14,71-141`.

Risk/impact:

Even if the BN gate were repaired, the proposal's own stated focused lane would
still start red before any work-subject/root-guard changes are applied. That
breaks the revision's central claim that baseline retirement produces a clean
attribution surface for the subsequent Phase 7 behavior work.

Required action:

Revise the retirement package so the startup-model surface is handled
explicitly. Acceptable paths include:

1. Retire the `workstream-focus.py` expectation from
   `tests/scripts/test_session_self_initialization.py` and any corresponding
   startup-model language in the same bridge as the Claude-side retirement.
2. Or, if the startup model is supposed to keep advertising a workstream-focus
   hook artifact, explain and implement the replacement surface that satisfies
   that contract without recreating the deleted wrapper.

## Passing Evidence

- Revision 4 does fix the `-008` scope gap by adding
  `tests/scripts/test_groundtruth_governance_adoption.py` to `target_paths`:
  `bridge/gtkb-work-subject-root-enforcement-implementation-009.md:14,220-221`.
- The plan/backlog supersede from `.groundtruth/session/work-subject.json` to
  `.claude/session/work-subject.json` remains explicit and internally coherent:
  `bridge/gtkb-work-subject-root-enforcement-implementation-009.md:165-205`,
  `memory/work_list.md:139-144`, and
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:120-147`.

## Required Action Items Or Conditions

1. Correct the BN baseline story so it accounts for all live failures in
   `tests/scripts/test_groundtruth_governance_adoption.py`, not just the two
   `workstream-focus.py` assertions.
2. Correct the startup-model retirement story so
   `tests/scripts/test_session_self_initialization.py` is either explicitly
   updated or explicitly scoped out before claiming it is currently clean.
3. Preserve the coherent `.claude/session/work-subject.json` authority
   supersede once the clean-baseline story is made accurate end-to-end.

## Decision Needed From Owner

None for this NO-GO.
