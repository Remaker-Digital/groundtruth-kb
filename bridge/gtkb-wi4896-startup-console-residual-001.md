NEW

# gtkb-wi4896-startup-console-residual - Boot-time Windows console residual fix

bridge_kind: prime_proposal
Document: gtkb-wi4896-startup-console-residual
Version: 001
Author: Prime Builder Codex
Date: 2026-06-27T19:20:00Z

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-a-20260627-startup-console-residual
author_model: GPT-5
author_model_version: 2026-06-27
author_model_configuration: Codex desktop; danger-full-access; approval-policy never; interactive role Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4896

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "scripts/install_db_snapshot_task.ps1", "platform_tests/scripts/test_db_snapshot_launcher_in_root.py"]

implementation_scope: source,test,config-runtime-installer
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Mike restarted the workstation and observed the Windows console popup before starting any interactive harness. The first WI-4896 implementation covered repo-owned daemon start, ensure-alive, bridge launcher, and Codex Stop-hook launch surfaces, but the reboot evidence exposed two additional outside-harness residuals:

1. The live dispatcher daemon is now the active substrate (`harness-state/bridge-substrate.json` = `dispatcher_daemon`). On boot, the daemon can see the storm-watchdog heartbeat as dormant before the watchdog scheduled task has refreshed it, then call `schtasks.exe /Run /TN GTKB-HarnessStormWatchdog` from `_restart_storm_watchdog`. That subprocess currently lacks `CREATE_NO_WINDOW`, `stdin=DEVNULL`, and output suppression.
2. The installed `GTKB-DbSnapshot` scheduled task was stale despite WI-4512 being VERIFIED: it still used a console-subsystem `python.exe`, a temp-directory launcher outside the project root, `Hidden=False`, and `StartWhenAvailable=True`, so a missed 03:00 run can surface a console at startup/logon. Runtime repair has already re-registered the live task to use `pythonw.exe` with the in-root launcher `.gtkb-state/db-snapshot/gtkb_db_snapshot_task.py`, `Hidden=True`, and a manual hidden run completed with `LastTaskResult=0`; this proposal makes the installer preserve that no-console configuration on future reinstalls.

This is a narrow residual fix under WI-4896. It does not change dispatcher topology, target eligibility, ranking, credentials, deployment, database schema, or snapshot output location.

## Defect / Reproduction

Observed runtime facts after workstation restart:

- `GTKB-DispatcherDaemon` is a hidden Task Scheduler task using `pythonw.exe`, but the daemon runs in live mode and owns watchdog dormancy remediation.
- `scripts/gtkb_dispatcher_daemon.py` `_restart_storm_watchdog` invokes `subprocess.run(["schtasks.exe", "/Run", "/TN", task_name], capture_output=True, timeout=15)` with no Windows no-window creation flag. `schtasks.exe` is a console subsystem executable, so it can allocate or flash a console when spawned from a GUI-subsystem daemon at boot.
- `GTKB-DbSnapshot` was installed as `Hidden=False`, `LogonType=Interactive`, `StartWhenAvailable=True`, and a console-subsystem Python action against an out-of-root temp launcher before the runtime repair. That task was a confirmed outside-harness console risk and violated the already-VERIFIED WI-4512 in-root launcher contract at runtime.
- After runtime repair, `GTKB-DbSnapshot` action uses `pythonw.exe` with `.gtkb-state/db-snapshot/gtkb_db_snapshot_task.py`, `Hidden=True`, and manual `Start-ScheduledTask` completed with `LastTaskResult=0`.

## In-Root Placement Evidence

All source/test target paths are relative in-root paths: `scripts/gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, `scripts/install_db_snapshot_task.ps1`, and `platform_tests/scripts/test_db_snapshot_launcher_in_root.py`. The generated db-snapshot runtime launcher lives at `.gtkb-state/db-snapshot/gtkb_db_snapshot_task.py`, an in-root generated runtime path already accepted by WI-4512.

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Requires Windows dispatcher wake/background paths to run non-interactively without visible console windows; this fix applies that rule to daemon watchdog remediation and db snapshot scheduled-task installation.
- `ADR-DISPATCHER-ARCHITECTURE-001` - The dispatcher daemon is the black-box dispatch substrate; boot-time remediation behavior belongs in dispatcher-owned source and tests.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - The daemon composes and records dispatch/remediation work without user-facing UI; no-console subprocess discipline preserves that service boundary.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected `scripts/` and `platform_tests/` changes require bridge proposal, LO GO, implementation claim, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites the governing specs for the requested source/test changes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries Project Authorization, Project, Work Item, and target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation report must map the changed behavior to tests and runtime verification.
- `GOV-STANDING-BACKLOG-001` - WI-4896 is the active owner-reported dispatcher console-window regression item.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The db snapshot launcher is an active runtime dependency and must remain in-root, not under `%TEMP%`.

## Prior Deliberations

- `DELIB-20266297` - Owner directive and authorization for WI-4896 dispatcher console-window suppression.
- `DELIB-20266276` - Daemon resilience scope-lock and scheduled-supervisor context.
- `DELIB-20266192` - WI-4852 watchdog dormancy auto-restart authorization; this proposal repairs the no-console behavior of that remediation path.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-001.md` - first WI-4896 proposal, which did not include these residual target paths.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-003.md` - first WI-4896 implementation report, awaiting LO verification and explicitly scoped away from scheduled-task definitions.
- `bridge/gtkb-wi4512-db-snapshot-launcher-in-root-004.md` - VERIFIED db snapshot launcher-in-root fix; disclosed residual that existing scheduled-task installations need re-registration.

## Owner Decisions / Input

No new owner decision is required. The owner's current reboot report is additional defect evidence for the same WI-4896 objective: suppress Windows console windows from dispatcher/background GT-KB automation. `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION` authorizes bounded source, test, and hook/background launcher changes under `DELIB-20266297` and explicitly excludes topology, credential, and deployment changes, which remain out of scope here.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001` already cover no-console Windows background execution, dispatcher ownership, centralized service behavior, and in-root runtime dependency placement. No new or revised requirement is required before this implementation.

## Proposed Scope

- In `scripts/gtkb_dispatcher_daemon.py`, update `_restart_storm_watchdog` so the `schtasks.exe /Run` subprocess runs with `stdin=subprocess.DEVNULL`, suppressed stdout/stderr or captured handles as appropriate, and `CREATE_NO_WINDOW` on Windows.
- Add or extend `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` coverage proving the watchdog restart subprocess receives no-window flags on Windows while preserving success/failure return semantics.
- In `scripts/install_db_snapshot_task.ps1`, prefer `pythonw.exe` for the scheduled-task action and register/update the task with hidden settings while preserving the in-root launcher path from WI-4512, `StartWhenAvailable`, retention behavior, and snapshot output location.
- Extend `platform_tests/scripts/test_db_snapshot_launcher_in_root.py` so the installer contract asserts no `$env:TEMP`, an in-root launcher, `pythonw.exe` action discipline, and hidden scheduled-task settings.
- Leave existing runtime `GTKB-DbSnapshot` repair in place; implementation may re-run the installer only if needed to confirm the source contract matches runtime state.

## Specification-Derived Verification Plan

| Spec / requirement | Planned verification |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Focused tests assert daemon `schtasks.exe` restart uses `CREATE_NO_WINDOW` and db snapshot installer uses `pythonw.exe` plus hidden task settings. |
| `ADR-DISPATCHER-ARCHITECTURE-001` / `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Existing dispatcher daemon tests plus read-only `gt bridge dispatch daemon status --json` confirm no topology or selection behavior change. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Existing/extended db snapshot installer tests confirm launcher remains under `$ProjectRoot/.gtkb-state/db-snapshot`, not `%TEMP%`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implement only after latest bridge status is GO and a matching work-intent/implementation-start packet authorizes the target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report will map each linked spec to exact commands and observed results. |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_db_snapshot_launcher_in_root.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_db_snapshot_launcher_in_root.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_db_snapshot_launcher_in_root.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install_db_snapshot_task.ps1
Get-ScheduledTask -TaskName GTKB-DbSnapshot
Start-ScheduledTask -TaskName GTKB-DbSnapshot; Get-ScheduledTaskInfo -TaskName GTKB-DbSnapshot
```

## Acceptance Criteria

- [ ] Daemon watchdog auto-restart cannot allocate or flash a visible console when invoking `schtasks.exe` on Windows.
- [ ] The db snapshot installer writes the launcher in-root and registers the task with a GUI-subsystem Python (`pythonw.exe`) and hidden settings.
- [ ] The currently installed `GTKB-DbSnapshot` task remains hidden, points at the in-root launcher, and completes a manual run with result `0`.
- [ ] Focused regression tests and lint/format checks pass.
- [ ] No topology, dispatcher target eligibility, credential, deployment, database-schema, or snapshot-output-location changes are made.

## Risks / Rollback

Risk is low and localized to Windows process-launch configuration. Hiding `schtasks.exe` output could obscure command stdout/stderr, but `_restart_storm_watchdog` already returns only launch success/return code/error summary, and the scheduled task itself remains queryable through Task Scheduler. Switching db snapshot scheduling from `python.exe` to `pythonw.exe` hides console output; snapshot success remains observable through Task Scheduler `LastTaskResult` and snapshot files/logs.

Rollback is a single commit revert for the four source/test files plus, if needed, re-running the prior db snapshot installer. No database rollback, topology rollback, credential rotation, or deployment rollback is involved.

## Files Expected To Change

- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `scripts/install_db_snapshot_task.ps1`
- `platform_tests/scripts/test_db_snapshot_launcher_in_root.py`

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
