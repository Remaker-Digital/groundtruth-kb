NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: codex-desktop
author_model_configuration: Codex desktop interactive Prime Builder session; WI-4896 release hardening

# GT-KB Bridge Implementation Report - gtkb-wi4896-codex-desktop-antigravity-console-residual - 004

bridge_kind: implementation_report
Document: gtkb-wi4896-codex-desktop-antigravity-console-residual
Version: 004 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4896-codex-desktop-antigravity-console-residual-003.md
Approved proposal: bridge/gtkb-wi4896-codex-desktop-antigravity-console-residual-002.md
Recommended commit type: fix:

## Implementation Claim

Implemented the WI-4896 no-window release-runtime audit and corrected the GT-KB-owned Python launch surfaces it found. Project Codex containment is restored with `.codex/config.toml` `hooks = false`, `shell_snapshot = false`, and inert `.codex/hooks.json`.

Added `scripts/windows_no_window_spawn_audit.py`, which scans Python launch surfaces and classifies each finding as compliant no-window, interactive allowlist, non-release-runtime, or violation. The scanner recognizes direct `creationflags` / `startupinfo`, kwargs dictionaries, `typing.cast(..., kwargs)`, and the scoped no-window helper functions used by this fix.

Patched release-runtime launch sites in:

- `.claude/hooks/bridge-compliance-gate.py`
- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`
- `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`
- `.codex/gtkb-hooks/document_author_provenance_gate.py`
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py`
- `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`
- `.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py`
- `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/launcher.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher/scheduler.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Owner Decisions / Input

No new owner decision is required for this implementation report. The owner directive carried forward is: no GT-KB-controlled background work should spawn visible console windows, and Python subprocess launch sites should be found and fixed programmatically.

## Prior Deliberations

- `bridge/gtkb-wi4896-codex-desktop-antigravity-console-residual-002.md` - approved implementation proposal.
- `bridge/gtkb-wi4896-codex-desktop-antigravity-console-residual-003.md` - Loyal Opposition GO verdict.
- `DELIB-20266297` - WI-4896 console-window suppression authorization.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - dispatcher issues are release blockers.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| Spawn audit / no-window release runtime | `python scripts\windows_no_window_spawn_audit.py` -> `release_ready: true`, `violation_count: 0`, `total_findings: 633` |
| Untracked approved wait helper | `python scripts\windows_no_window_spawn_audit.py groundtruth-kb\src\groundtruth_kb\bridge\wait_commands.py` -> `release_ready: true`, `violation_count: 0`, `total_findings: 1` |
| Spec-derived focused tests | `python -m pytest platform_tests\scripts\test_windows_no_window_spawn_audit.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py -q --tb=short` -> `156 passed in 27.70s` |
| Lint | scoped `python -m ruff check ...` -> `All checks passed!` |
| Format | scoped `python -m ruff format --check ...` -> `15 files already formatted` |
| Codex containment | `.codex/config.toml` contains `hooks = false` and `shell_snapshot = false`; `.codex/hooks.json` is `{"hooks":{}}` after verification |
| Live no-storm classification | 75-second refined watcher: exact screenshot `PYTHONPATH` probe samples `0`; GT-KB runtime process matches only stale CIM PIDs 8228/17524, both absent from `Get-Process`; scheduled `GTKB-*` tasks remain disabled |

## Commands Run

- `python scripts\windows_no_window_spawn_audit.py`
- `python scripts\windows_no_window_spawn_audit.py groundtruth-kb\src\groundtruth_kb\bridge\wait_commands.py`
- `python -m ruff check scripts\windows_no_window_spawn_audit.py platform_tests\scripts\test_windows_no_window_spawn_audit.py platform_tests\scripts\test_cross_harness_bridge_trigger.py .claude\hooks\bridge-compliance-gate.py .codex\gtkb-hooks\bridge-compliance-gate-apply-patch-adapter.py .codex\gtkb-hooks\bridge-compliance-gate-bash-adapter.py .codex\gtkb-hooks\document_author_provenance_gate.py .codex\gtkb-hooks\lo-file-safety-gate-bash-adapter.py .codex\gtkb-hooks\session_wrapup_trigger_dispatch.py .codex\gtkb-hooks\sot-read-discipline-bash-adapter.py .codex\gtkb-hooks\wi-id-collision-gate-bash-adapter.py groundtruth-kb\src\groundtruth_kb\bridge\launcher.py groundtruth-kb\src\groundtruth_kb\bridge\wait_commands.py groundtruth-kb\src\groundtruth_kb\dispatcher\scheduler.py groundtruth-kb\src\groundtruth_kb\cli.py`
- `python -m ruff format --check scripts\windows_no_window_spawn_audit.py platform_tests\scripts\test_windows_no_window_spawn_audit.py platform_tests\scripts\test_cross_harness_bridge_trigger.py .claude\hooks\bridge-compliance-gate.py .codex\gtkb-hooks\bridge-compliance-gate-apply-patch-adapter.py .codex\gtkb-hooks\bridge-compliance-gate-bash-adapter.py .codex\gtkb-hooks\document_author_provenance_gate.py .codex\gtkb-hooks\lo-file-safety-gate-bash-adapter.py .codex\gtkb-hooks\session_wrapup_trigger_dispatch.py .codex\gtkb-hooks\sot-read-discipline-bash-adapter.py .codex\gtkb-hooks\wi-id-collision-gate-bash-adapter.py groundtruth-kb\src\groundtruth_kb\bridge\launcher.py groundtruth-kb\src\groundtruth_kb\bridge\wait_commands.py groundtruth-kb\src\groundtruth_kb\dispatcher\scheduler.py groundtruth-kb\src\groundtruth_kb\cli.py`
- `python -m pytest platform_tests\scripts\test_windows_no_window_spawn_audit.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py -q --tb=short`
- 90-second broad process watcher, then 75-second refined process watcher.
- `Get-Process -Id 8228,17524 -ErrorAction SilentlyContinue`
- `Get-ScheduledTask | Where-Object {$_.TaskName -like 'GTKB*' -or $_.TaskName -like 'GroundTruth*'}`

## Observed Results

- Static tracked-file audit: `{"counts": {"compliant_no_window": 47, "interactive_allowlist": 128, "non_release_runtime": 458}, "release_ready": true, "total_findings": 633, "violation_count": 0}`.
- Explicit untracked wait-helper audit: `{"counts": {"compliant_no_window": 1}, "release_ready": true, "total_findings": 1, "violation_count": 0}`.
- Focused tests: `156 passed in 27.70s`.
- Lint: `All checks passed!`.
- Format: `15 files already formatted`.
- `.codex/hooks.json` was re-observed as `{"hooks":{}}` after the test run.
- The refined live watcher recorded `exact_pythonpath_probe_samples: 0`.
- The refined watcher recorded `new_console_hosts: 152`, grouped as `conhost.exe` under `git.exe` (116), `powershell.exe` (31), empty parent (3), and `cmd.exe` (2). Samples show Codex/Desktop-owned git status/diff/hash-object and PowerShell process-probe commands, not GT-KB hook/daemon launchers.
- The only GT-KB-pattern runtime matches were CIM records for `pwsh.exe` PIDs 8228 and 17524 from prior Codex hook commands. `Get-Process -Id 8228,17524` returned no live processes, and parent PID 24620 was also absent, so these are stale CIM command-line records rather than live GT-KB children.
- `GTKB-DbSnapshot`, `GTKB-DispatcherDaemon`, `GTKB-HarnessStormWatchdog`, and two `GTKB-SingleHarness-E2E-Test-*` scheduled tasks remain disabled (`State: 1`).

## Files Changed

WI-4896 implementation files:

- `.codex/config.toml`
- `.codex/hooks.json`
- `scripts/windows_no_window_spawn_audit.py`
- `platform_tests/scripts/test_windows_no_window_spawn_audit.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `.claude/hooks/bridge-compliance-gate.py`
- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`
- `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`
- `.codex/gtkb-hooks/document_author_provenance_gate.py`
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py`
- `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`
- `.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py`
- `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/launcher.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher/scheduler.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`

Pre-existing dirty files outside this WI remain in the worktree and are not claimed by this report.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: this change fixes the Windows visible-console release blocker for GT-KB-owned release-runtime launch paths and adds a regression audit.

## Acceptance Criteria Status

- [x] Scanner is tracked and tested.
- [x] GT-KB-owned release-runtime Python launcher violations found by the scanner are fixed or classified.
- [x] Codex hooks remain disabled by config and active hooks JSON is inert.
- [x] Live evidence separates GT-KB-controlled behavior from Codex/Desktop-owned git and PowerShell probe churn.
- [x] Daemon and scheduled GT-KB tasks remain stopped/disabled during validation.

## Risk And Rollback

Residual risk: Codex Desktop itself continues creating many `conhost.exe` children for git and PowerShell probes during ordinary app operation. The refined watcher did not observe the screenshot's exact `PYTHONPATH` probe during the 75-second interval, but the app-owned probe class remains outside this GT-KB code fix. Treat it as a separate release-readiness environment/app issue if visible windows continue after this containment.

Rollback: revert the WI-4896 files listed above. The safe incident fallback is to keep `.codex/config.toml` hooks disabled and `.codex/hooks.json` inert while dispatcher/daemon work proceeds through non-Codex or manually verified paths.

## Loyal Opposition Asks

1. Verify that the scanner and tests satisfy the no-window release-runtime requirement.
2. Verify that the GT-KB-owned hook/daemon/bridge/scheduler launch paths no longer contain release-runtime no-window violations.
3. Decide whether the residual Codex/Desktop git and PowerShell `conhost.exe` churn should be tracked as a separate release blocker outside WI-4896.
