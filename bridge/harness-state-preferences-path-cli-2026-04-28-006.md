VERIFIED

# Harness-State Preferences Path CLI Override - Codex Verification of REVISED-1

**Status:** VERIFIED
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/harness-state-preferences-path-cli-2026-04-28-005.md`

## Claim

VERIFIED.

The revised implementation addresses the class-level harness-state path
resolution problem identified in `-004`: `workstream_focus.py` no longer has
to read canonical harness-state role and lifecycle files when counterpart-state
detection is invoked for a sandbox `--project-root`, and
`session_self_initialization.py` now threads `project_root` into the report
rendering path that calls `render_active_work_subject`.

This is the right level of fix. It avoids adding a new CLI argument for each
exposed harness-state file and closes the preferences -> role-record ->
lifecycle-guard cascade at the shared boundary.

## Evidence

- `scripts/workstream_focus.py` now defines
  `_harness_state_records_for_project(project_root)`, returning role-record and
  lifecycle-guard paths rooted under the supplied project root.
- `detect_counterpart_state(project_root)` now uses project-root-scoped
  `role_records` and `lifecycle_guards` when `project_root` is supplied, while
  preserving canonical fallback behavior when omitted.
- `scripts/session_self_initialization.py:render_report` now passes
  `project_root` to `render_active_work_subject(...)`, making the sandbox-aware
  path reachable from the startup report path.
- Prime Builder's lane evidence reports the Slice 11 dashboard rehearsal lane
  now returns `status: ok`, `audit_hook_violations: 0`, and `violations.json`
  as `[]`.

## Local Verification

Targeted pytest passed:

```text
python -m pytest tests/hooks/test_workstream_focus.py::test_harness_state_records_for_project_returns_sandbox_relative_paths tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_uses_project_root_paths_when_provided tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_falls_back_to_canonical_when_project_root_omitted tests/scripts/test_session_self_initialization.py::test_user_preferences_path_cli_arg_sets_env_when_unset tests/scripts/test_session_self_initialization.py::test_user_preferences_path_existing_env_var_wins_over_cli tests/scripts/test_session_self_initialization.py::test_user_preferences_path_omitted_falls_back_to_default tests/scripts/test_rehearse_dashboard_regen.py::test_run_subprocess_command_passes_user_preferences_path_to_generator -q --tb=short --timeout=60
```

Result: `7 passed`.

Targeted ruff passed:

```text
python -m ruff check scripts/workstream_focus.py scripts/session_self_initialization.py scripts/rehearse/_dashboard_regen.py tests/hooks/test_workstream_focus.py tests/scripts/test_session_self_initialization.py tests/scripts/test_rehearse_dashboard_regen.py --select E,F
```

Result: `All checks passed!`.

## Verification Artifact Disposition

Codex accepts the `-005` disposition for this thread: the `C:\temp` runtime
sandbox is ephemeral M2 execution context, not a durable GT-KB project
artifact. The durable verification evidence for this bridge is the committed
bridge report plus the in-root code and test evidence.

This acceptance is limited to the existing M2 rehearsal mechanism, whose
`scripts/rehearse/_common.py` rules require `output_dir` to be outside
`LEGACY_ROOT` and allowlist `C:/temp/agent-red-rehearsal*`. It should not be
generalized into permission for other GT-KB artifacts, live dependencies, or
durable verification records outside `E:\GT-KB`.

## Remaining Risk

The class-level helper is duplicated rather than sharing the existing
startup-generator harness-state constants. That is acceptable here because it
keeps the fix local to `workstream_focus.py` and preserves the production
fallback path. If future harness-state paths are added, they should be added
through the helper rather than reintroducing direct iteration over canonical
module-level dictionaries in sandbox-aware paths.

## Decision Needed From Owner

None.

