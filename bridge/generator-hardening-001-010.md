VERIFIED

# GENERATOR-HARDENING-001 - Codex Verification of REVISED-2

**Status:** VERIFIED
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-001-009.md`

## Claim

VERIFIED.

GH-001 can close because the original `-004` gate is now satisfied through the
original Type A-D implementation plus the two verified follow-on bridges that
closed the residual audit-hook classes.

The original GH-001 code at commit `80e16ba8` removed the targeted
`PROJECT_ROOT` output/read fallback problems and added the public CLI
partial-argument regression test. The remaining violation classes that blocked
terminal verification were handled by:

- `bridge/generator-hardening-cross-repo-009.md` for the cross-repo git
  subprocess class.
- `bridge/harness-state-preferences-path-cli-2026-04-28-006.md` for the
  harness-state preferences / role-record / lifecycle-guard read cascade.

## Evidence

- `bridge/generator-hardening-001-004.md` required `PROJECT_ROOT` to remain
  only as the CLI fallback for `--project-root`, not as an internal
  output/read-path fallback after `project_root` resolution.
- Current source scan shows `DEFAULT_DASHBOARD_DIR` and `DEFAULT_HISTORY_PATH`
  are removed, `--dashboard-dir` and `--history-path` are derived after
  argument parsing, and the public regression test exists.
- `bridge/generator-hardening-cross-repo-009.md` is VERIFIED.
- `bridge/harness-state-preferences-path-cli-2026-04-28-006.md` is VERIFIED.
- Prime Builder's `-009` report provides the current lane evidence:
  `status: ok`, `violations: 0`, `returncode: 0`, and `violations.json` as
  `[]`.

## Local Verification

Focused pytest passed:

```text
python -m pytest tests/scripts/test_session_self_initialization.py::test_main_with_only_project_root_writes_under_that_root tests/scripts/test_session_self_initialization.py::test_git_checkout_info_returns_degraded_when_outside_project_root tests/hooks/test_workstream_focus.py::test_harness_state_records_for_project_returns_sandbox_relative_paths tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_uses_project_root_paths_when_provided tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_falls_back_to_canonical_when_project_root_omitted tests/scripts/test_session_self_initialization.py::test_user_preferences_path_cli_arg_sets_env_when_unset tests/scripts/test_session_self_initialization.py::test_user_preferences_path_existing_env_var_wins_over_cli tests/scripts/test_session_self_initialization.py::test_user_preferences_path_omitted_falls_back_to_default tests/scripts/test_rehearse_dashboard_regen.py::test_run_subprocess_command_passes_user_preferences_path_to_generator -q --tb=short --timeout=90
```

Result: `9 passed`.

Focused ruff passed:

```text
python -m ruff check scripts/session_self_initialization.py scripts/workstream_focus.py scripts/rehearse/_dashboard_regen.py tests/scripts/test_session_self_initialization.py tests/hooks/test_workstream_focus.py tests/scripts/test_rehearse_dashboard_regen.py --select E,F
```

Result: `All checks passed!`.

## Lane Evidence Note

Codex did not rerun the full Slice 11 M2 lane locally in this review. The lane
requires the established outside-`LEGACY_ROOT` ephemeral sandbox mechanism.
This verification relies on the lane result reported in `-009` and on the
separately verified follow-on bridge chain that closed the previously observed
violation classes.

## Closure Effect

GH-001 is terminally closed. Future audit-hook leaks should open distinct bridge
threads with their own evidence rather than reopening GH-001 unless they
directly regress the `PROJECT_ROOT` fallback behavior this thread was created
to harden.

## Decision Needed From Owner

None.

