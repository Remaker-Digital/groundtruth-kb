GO

# GTKB Work Subject And Root Enforcement - Foundation Review Revision 6

**Status:** GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-work-subject-root-enforcement-implementation-011.md`

## Verdict

GO on Revision 5 with the conditions below.

Revision 5 fixes the two blockers from `-010` by making the baseline-retirement
claim precise instead of overstated. The live repository still has a retired
Claude-side `workstream-focus.py` contract scattered across the exact files now
named in the proposal, and the proposal now treats the unrelated startup-reports
documentation failure as a separate bridge concern instead of pretending this
slice will clear it.

## Findings

### F1 - No blocking scope drift remains in the workstream-focus retirement package

Severity: None (approval basis)

Evidence:

- The live parity checker still fails because it requires the missing Claude
  wrapper file and Claude-side settings registrations:
  `scripts/check_codex_hook_parity.py:214-248`.
- Live command result:
  `python scripts/check_codex_hook_parity.py --project-root .`
  -> `Codex hook parity: FAIL`
  -> `missing required file: .claude/hooks/workstream-focus.py`
- The three current `tests/hooks/test_workstream_focus.py` failures are the
  wrapper-execution tests that shell through the missing hook path:
  `tests/hooks/test_workstream_focus.py:14`, `:26-40`, `:63-67`, `:123-167`.
- Live command result:
  `python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short`
  -> `3 failed, 9 passed`
- The current startup-model failure is the stale hook-file assertion only:
  `tests/scripts/test_session_self_initialization.py:92-96`.
- Live command result:
  `python -m pytest tests/scripts/test_session_self_initialization.py::test_startup_model_contains_role_governance_and_kpi_inventory -q --tb=short`
  -> failed at line 93 (`"workstream-focus.py" in model["directives"]["hook_files"]`).
- The model is built from the live `.claude/hooks/*.py` glob, while the
  workstream-focus labels still come from the separate state snapshot:
  `scripts/session_self_initialization.py:2364-2366`, `:2441-2446`, `:3055-3057`.
- Live inspection confirms the current model omits `workstream-focus.py` from
  `hook_files` but still reports `Application Focus` labels.
- The governed-lane test failures split exactly as Revision 5 now claims:
  two workstream-focus retirement assertions plus one separate startup-reports
  docs-sync failure:
  `tests/scripts/test_groundtruth_governance_adoption.py:91`, `:160-161`,
  `:774-777`.
- Live command result:
  `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
  -> `3 failed, 27 passed`
  -> failures at the required-artifact assertion, the settings-registration
  assertion, and `test_bridge_authority_is_loaded_by_startup_rules`.

Risk/impact:

The proposal now matches the real failing baseline. That removes the prior
attribution ambiguity and gives Prime a coherent first step before the actual
Phase 7 work-subject/root-boundary behavior change.

Recommended action:

Approve the revision and hold Prime to the conditions below.

## Conditions

1. `BN-2` must retire only Claude-side expectations from
   `tests/scripts/test_codex_hook_parity.py`; do not weaken the Codex-side
   `workstream-focus.cmd` intent checks that still back
   `scripts/check_codex_hook_parity.py:295-339` and
   `tests/scripts/test_codex_hook_parity.py:42-58`, `:89-163`.
2. `BN-3` must be limited to the three wrapper-execution tests that invoke
   `HOOK_PATH`; do not skip the direct module/state/guard tests in
   `tests/hooks/test_workstream_focus.py`.
3. Post-BN verification must show the remaining full-module failure in
   `tests/scripts/test_groundtruth_governance_adoption.py` is only the
   explicitly scoped-out startup-reports docs gap at `:774-777`. This bridge
   does not authorize a claim that the governed release-gate lane is green.
4. The plan/backlog supersede must land exactly as proposed because the current
   accepted authority still points at `.groundtruth/session/work-subject.json`:
   `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:120-124`
   and `memory/work_list.md:139-144`.

## Decision Needed From Owner

None for this GO.
