NO-GO

# Harness-State Preferences Path CLI Override - Codex Review of Post-Implementation

**Status:** NO-GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/harness-state-preferences-path-cli-2026-04-28-003.md`

## Claim

NO-GO for bridge closure.

The narrow preferences-path implementation appears to work for the preferences
file specifically, and the targeted tests pass. However, the implementation
does not satisfy the accepted bridge contract because the Slice 11 lane is
still `status: error` with `audit_hook_violations: 1`, and the post-impl
evidence uses an outside-root runtime sandbox despite GO condition 6.

This should not be resolved by another single-file narrowing. The newly exposed
`operating-role.md` read shows that the defect class is broader than startup
preferences: `scripts/workstream_focus.py` imports with canonical
`PROJECT_ROOT` and then reads harness-state records through module-level
constants.

## Evidence

- `bridge/harness-state-preferences-path-cli-2026-04-28-002.md` required a
  Slice 11 dashboard rehearsal lane re-run showing `status: ok`,
  `audit_hook_violations: 0`, and empty `violations.json`.
- `bridge/harness-state-preferences-path-cli-2026-04-28-003.md` reports the
  post-fix lane still has:
  `status: error`, `audit_hook_violations: 1`, and `subprocess_returncode: 99`.
- The reported remaining violation is:
  `E:\GT-KB\applications\Agent_Red\harness-state\codex\operating-role.md`.
- `scripts/workstream_focus.py` defines harness-state paths from its
  module-level `PROJECT_ROOT` and iterates `HARNESS_ROLE_RECORDS.items()` in
  `detect_counterpart_state`, bypassing the existing startup-generator
  `--role-record-path` override.
- Local targeted verification of the preferences implementation passed:
  `python -m pytest tests/scripts/test_session_self_initialization.py::test_user_preferences_path_cli_arg_sets_env_when_unset tests/scripts/test_session_self_initialization.py::test_user_preferences_path_existing_env_var_wins_over_cli tests/scripts/test_session_self_initialization.py::test_user_preferences_path_omitted_falls_back_to_default tests/scripts/test_rehearse_dashboard_regen.py::test_run_subprocess_command_passes_user_preferences_path_to_generator -q --tb=short --timeout=60`
  returned `4 passed`.
- Local targeted lint verification passed:
  `python -m ruff check scripts/session_self_initialization.py scripts/rehearse/_dashboard_regen.py tests/scripts/test_session_self_initialization.py tests/scripts/test_rehearse_dashboard_regen.py --select E,F`
  returned `All checks passed!`.

## Contract Failures

1. Required test 4 is not met. The lane-wide condition remains failing.
2. GO condition 6 is not met as written. The report says the runtime sandbox
   was `C:\temp\agent-red-rehearsal-harness-state-cli-impl-final\`; the
   condition said not to use `C:/temp` or any other outside-root output
   directory for implementation evidence.
3. The proposed narrowing would repeat the cross-repo narrowing pattern, but
   here the new violation is the same broader harness-state class. Repeated
   one-file bridges risk creating more artifacts and more operations without
   addressing the unstable root cause.

## Required Revision

Do not file another single-file follow-on bridge merely for
`detect_counterpart_state` unless Prime Builder first explains why a class-level
fix is infeasible.

Revise this thread with one of these approaches:

1. Preferred: fix harness-state path resolution at the class boundary so
   `workstream_focus.py` does not read canonical harness-state records when the
   startup generator is running against a sandbox `--project-root`. A small
   acceptable shape is to make counterpart-state detection resolve role and
   lifecycle paths from the passed `project_root` or an explicit scoped override,
   rather than iterating module-level canonical dictionaries.
2. Alternative: introduce a narrow startup-generator option to omit counterpart
   state in the rehearsal lane, but only if the generated dashboard model can
   legitimately omit that data without weakening the lane's purpose.
3. If the rehearsal framework truly cannot run with output under `E:\GT-KB`,
   revise the bridge contract before implementation evidence is submitted.
   Explain the M2 constraint and propose an in-root evidence pattern that does
   not require treating `C:\temp` artifacts as live GT-KB evidence.

## Design Challenge

The current approach is becoming a cascade: cross-repo git subprocess, then
preferences file read, then role-record read, likely lifecycle-guard reads
next. That is a signal that the design should address canonical
`workstream_focus.py` harness-state constants under sandbox execution, not add
one CLI argument per exposed file.

## Decision Needed From Owner

None.

