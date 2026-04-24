NO-GO

# GTKB Work Subject And Root Enforcement - Foundation Review Revision 4

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-work-subject-root-enforcement-implementation-007.md`

## Verdict

NO-GO on Revision 3 as written.

Revision 3 correctly removes the nonexistent wrapper from `target_paths` and
keeps the `.claude/session/work-subject.json` supersede coherent. The blocker is
that the new baseline-normalization plan still does not produce the clean
baseline it claims. The BN verification gate cannot pass with the currently
proposed edits, and the governed release-gate lane still contains
workstream-focus contract failures outside the proposal's target set.

## Findings

### F1 - BN verification gate cannot pass with the proposed BN-1/BN-2/BN-3 changes alone

Severity: High

Evidence:

- Revision 3 says BN-1 removes `workstream-focus.py` from the parity
  requirements, BN-2 updates `tests/scripts/test_codex_hook_parity.py`, BN-3
  skips the three failing hook-wrapper tests, and the resulting BN gate must
  pass before implementation:
  `bridge/gtkb-work-subject-root-enforcement-implementation-007.md:56-98`.
- The live parity checker still requires Claude-side workstream-focus hook
  registration independently of the required-file list:
  `scripts/check_codex_hook_parity.py:243-248`.
- The live tracked `.claude/settings.json` does not register any
  `workstream-focus.py` command in `PreToolUse` or `UserPromptSubmit`; it only
  registers `formal-artifact-approval-gate.py`,
  `session_self_initialization.py`, and `poller-freshness.py`:
  `.claude/settings.json:5-45`.
- Current baseline proof:
  - `python scripts/check_codex_hook_parity.py --project-root .` ->
    `Codex hook parity: FAIL` with `missing required file: .claude/hooks/workstream-focus.py`.
  - Disposable temp-copy proof with a stub `.claude/hooks/workstream-focus.py`
    added still fails:
    - `.claude/settings.json does not register the workstream focus PreToolUse hook`
    - `.claude/settings.json does not register the workstream focus UserPromptSubmit hook`

Risk/impact:

The proposal asks for GO on the basis that the baseline can be normalized before
implementation, but the named normalization edits do not actually make the
parity gate green. Prime would still be implementing against a red pre-existing
baseline, so later failures could not be cleanly attributed.

Required action:

Revise the baseline-normalization plan so it closes the full parity contract,
not just the missing-file check. Acceptable options include:

1. Explicitly retire the Claude-side project hook contract by updating
   `scripts/check_codex_hook_parity.py`, `.claude/settings.json`, and the
   affected governance tests together.
2. Restore or replace the tracked Claude hook surface and explain why that will
   not reintroduce the S304 spawn failure mode.

### F2 - The claimed clean verification surface remains red in the governed release-gate lane, and the necessary fixes are outside `target_paths`

Severity: High

Evidence:

- Revision 3 asks for GO to implement the slice "against the updated authority
  with a clean verification surface":
  `bridge/gtkb-work-subject-root-enforcement-implementation-007.md:18-21`.
- The live governance-adoption regression still requires the missing wrapper
  artifact and the removed Claude hook registrations:
  - required artifact list includes `.claude/hooks/workstream-focus.py`:
    `tests/scripts/test_groundtruth_governance_adoption.py:91`
  - settings assertions require `workstream-focus.py` in both prompt and
    pre-tool hook commands:
    `tests/scripts/test_groundtruth_governance_adoption.py:159-161`
- That governed lane is part of the release-candidate gate:
  `scripts/release_candidate_gate.py:89,103-114`.
- Live command result:
  - `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
    -> 3 failed, including:
    - missing `.claude/hooks/workstream-focus.py`
    - `.claude/settings.json` missing workstream-focus hook registration
- Revision 3 `target_paths` do not include `.claude/settings.json` or
  `tests/scripts/test_groundtruth_governance_adoption.py`:
  `bridge/gtkb-work-subject-root-enforcement-implementation-007.md:12-14`.

Risk/impact:

Even if the focused BN lane were repaired, the governed verification lane that
release gating relies on would stay red. That is not a clean verification
surface, and the current proposal does not authorize the files that must be
updated to make it one.

Required action:

Either:

1. expand the proposal scope and `target_paths` to include
   `.claude/settings.json`, `tests/scripts/test_groundtruth_governance_adoption.py`,
   and any other tracked startup/governance surfaces that still advertise
   `workstream-focus.py`; or
2. split baseline realignment into a separate bridge that lands a green governed
   baseline before the Phase 7 behavior migration requests GO.

## Passing Evidence

- Revision 3 fixes the specific `target_paths` drift from `-006` by removing
  `.claude/hooks/workstream-focus.py` from the reviewed write set:
  `bridge/gtkb-work-subject-root-enforcement-implementation-007.md:14,152-155`.
- The `.claude/session/work-subject.json` plan/backlog supersede remains
  coherent and is not the blocking issue in this review.

## Decision Needed From Owner

None for this NO-GO.
