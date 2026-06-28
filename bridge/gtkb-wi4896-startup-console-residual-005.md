NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c3-be81-7771-8200-e81c58e3ae1e
author_model: GPT-5
author_model_version: 2026-06-27
author_model_configuration: Codex desktop interactive session; Prime Builder; approval_policy=never

# GT-KB Bridge Implementation Report - gtkb-wi4896-startup-console-residual - 005

bridge_kind: implementation_report
Document: gtkb-wi4896-startup-console-residual
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4896-startup-console-residual-004.md
Approved proposal: bridge/gtkb-wi4896-startup-console-residual-003.md
Recommended commit type: feat:

## Implementation Claim

Implemented the approved WI-4896 residual Windows console/focus-steal fix for the daemon/background scheduled-task paths:

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` now runs the Windows Ollama autostart PowerShell probe with `-NoLogo`, `-NoProfile`, `-NonInteractive`, `stdin=subprocess.DEVNULL`, and `CREATE_NO_WINDOW` on Windows.
- `scripts/gtkb_dispatcher_daemon.py` now restarts the storm watchdog scheduled task with `stdin=subprocess.DEVNULL` and `CREATE_NO_WINDOW` on Windows.
- `scripts/ops/harness_storm_watchdog_launcher.py` is the tracked `pythonw.exe` Task Scheduler entrypoint for the storm watchdog and runs the PowerShell watchdog script with `-NonInteractive`, `-WindowStyle Hidden`, stdio redirected to `DEVNULL`, and `CREATE_NO_WINDOW`.
- `scripts/install_db_snapshot_task.ps1` now prefers the project venv `pythonw.exe`, registers the task hidden, writes the generated launcher in-root, and writes `.gtkb-state/db-snapshot/last-run.json` instead of relying on stdout from `pythonw.exe`.

Runtime verification re-registered and manually ran `GTKB-DbSnapshot` successfully. `GTKB-HarnessStormWatchdog` was also manually started successfully through Task Scheduler using the `pythonw.exe` launcher. `GTKB-DispatcherDaemon` was restarted and produced fresh daemon heartbeats without a visible `WindowsTerminal.exe`/`OpenConsole.exe` process in the process snapshot.

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Requires Windows dispatcher/background paths to run non-interactively without visible console windows; this fix applies that requirement to the daemon's doctor/Ollama PowerShell probe, watchdog restart, storm-watchdog launcher, and db snapshot task installer.`
- `ADR-DISPATCHER-ARCHITECTURE-001` - The dispatcher daemon is the black-box dispatch substrate; daemon tick health/readiness probes and watchdog remediation belong in daemon-owned source and tests.`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - The daemon composes and records dispatch/remediation work without user-facing UI; no-console subprocess discipline preserves that service boundary.`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Runtime launchers that scheduled tasks execute must live in-root and not depend on temp paths.`
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected `groundtruth-kb/src/`, `scripts/`, `platform_tests/`, and `groundtruth-kb/tests/` changes require bridge proposal, LO GO, implementation claim, and verification.`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites governing requirements for the source/test changes.`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries Project Authorization, Project, Work Item, and target path metadata.`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation report must map each changed behavior to exact tests and runtime verification.`
- `GOV-17` - This work remains under governed bridge/dispatcher implementation control with implementation-start authorization before protected source changes.`
- `GOV-STANDING-BACKLOG-001` - WI-4896 is the active owner-reported dispatcher console-window regression item, and WI-4882 is the PAUTH-included daemon-resilience program work item used for the implementation-start packet.`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The owner-reported runtime defect and the safety-brake decision are preserved as durable bridge evidence instead of remaining only in chat.`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The fix links defect evidence, source edits, tests, runtime verification, and implementation reporting as one traceable artifact graph.`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - This REVISED proposal explicitly supersedes the earlier residual proposal version with newer runtime evidence and a corrected target path set.`

## Owner Decisions / Input

No new owner decision is required by this implementation report. Carry forward any proposal-specific owner evidence here if applicable.

## Prior Deliberations

- `bridge/gtkb-wi4896-startup-console-residual-003.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi4896-startup-console-residual-004.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Focused tests asserted no-console subprocess contracts for the doctor PowerShell probe, daemon watchdog restart, storm-watchdog launcher, and DB snapshot task installer. Runtime task inspection confirmed `GTKB-DbSnapshot`, `GTKB-DispatcherDaemon`, and `GTKB-HarnessStormWatchdog` are hidden and use `pythonw.exe`. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | `scripts/gtkb_dispatcher_daemon.py` retains daemon-owned remediation but now invokes `schtasks.exe` headlessly; `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` verifies the daemon restart helper. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Daemon restart and task probe work remains background service behavior with no visible UI contract; runtime daemon status showed live mode and fresh heartbeat after restart. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `scripts/install_db_snapshot_task.ps1` continues to generate `.gtkb-state/db-snapshot/gtkb_db_snapshot_task.py` in-root and now writes `.gtkb-state/db-snapshot/last-run.json` in-root. Static tests verify no `$env:TEMP` launcher path. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation claim and authorization packet were active before protected edits; `implementation_authorization.py begin --bridge-id gtkb-wi4896-startup-console-residual` returned authorized target globs for all changed protected paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The approved proposal `bridge/gtkb-wi4896-startup-console-residual-003.md` and GO `-004.md` cite the governing specs and target path set; this report maps implementation to those specs. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The authorization packet used `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION`, project `PROJECT-GTKB-DISPATCHER-RELIABILITY`, and work item `WI-4882`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, Ruff check, Ruff format check, and runtime Task Scheduler verification are listed below with exact observed results. |
| `GOV-17` | No protected edit was made until the latest bridge status was `GO`, the implementation claim was active, and the authorization packet validated the changed targets. |
| `GOV-STANDING-BACKLOG-001` | WI-4896 owner-reported runtime evidence is now represented by source/test changes and this bridge report under the daemon-resilience program authorization. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The console/focus-steal symptom, VBS failure evidence, implementation, runtime checks, and residual follow-ups are captured in bridge artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The implementation preserves traceability from owner-reported symptom to proposal, GO, code, tests, runtime verification, and post-implementation report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Residual observations that are outside the GO target set are documented below instead of being silently mutated. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_doctor_ollama.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_daemon_supervision.py platform_tests\scripts\test_db_snapshot_launcher_in_root.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_doctor_ollama.py scripts\gtkb_dispatcher_daemon.py scripts\ops\harness_storm_watchdog_launcher.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_daemon_supervision.py platform_tests\scripts\test_db_snapshot_launcher_in_root.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_doctor_ollama.py scripts\gtkb_dispatcher_daemon.py scripts\ops\harness_storm_watchdog_launcher.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_daemon_supervision.py platform_tests\scripts\test_db_snapshot_launcher_in_root.py`
- `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File scripts\install_db_snapshot_task.ps1 -ProjectRoot E:\GT-KB`
- `Start-ScheduledTask -TaskName GTKB-DbSnapshot` followed by polling `Get-ScheduledTaskInfo -TaskName GTKB-DbSnapshot`
- `Start-ScheduledTask -TaskName GTKB-HarnessStormWatchdog` followed by polling `Get-ScheduledTaskInfo -TaskName GTKB-HarnessStormWatchdog`
- `Start-ScheduledTask -TaskName GTKB-DispatcherDaemon` followed by `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon status --json`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch health --json`

## Observed Results

- Focused pytest: `61 passed in 16.57s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `7 files already formatted`.
- DB snapshot installer: removed and re-registered `GTKB-DbSnapshot`; printed `Python: E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe`, `Script: E:\GT-KB\.gtkb-state\db-snapshot\gtkb_db_snapshot_task.py`, `Working directory: E:\GT-KB`.
- Installed `GTKB-DbSnapshot` action after re-registration: hidden `true`, enabled `true`, execute `E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe`, argument `"E:\GT-KB\.gtkb-state\db-snapshot\gtkb_db_snapshot_task.py"`, working directory `E:\GT-KB`.
- Manual `GTKB-DbSnapshot` run: state ready, `LastTaskResult: 0`, `.gtkb-state\db-snapshot\last-run.json` exists.
- Manual `GTKB-HarnessStormWatchdog` run: hidden `true`, enabled `true`, `LastTaskResult: 0`, heartbeat file exists.
- Manual `GTKB-DispatcherDaemon` supervisor run: hidden `true`, enabled `true`, `LastTaskResult: 0`; daemon status reported `running: true`, active substrate `dispatcher_daemon`, mode `live`, fresh heartbeat, and daemon log entry `dispatcher daemon loop started pid=38780 tick_seconds=30`.
- Process snapshot during runtime verification did not show `WindowsTerminal.exe` or `OpenConsole.exe` processes associated with the scheduled tasks.
- `bridge dispatch health --json` remained `WARN` because of a pre-existing OpenRouter LO runtime failure/backoff (`loyal-opposition:F`), not because of the Windows console fix.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor_ollama.py`
- `platform_tests/scripts/test_db_snapshot_launcher_in_root.py`
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/install_db_snapshot_task.ps1`
- `scripts/ops/harness_storm_watchdog_launcher.py`

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: The diff adds or changes skill, script, or platform capability surfaces.

```text
     groundtruth-kb/src/groundtruth_kb/project/doctor.py          |  24 +-
     groundtruth-kb/tests/test_doctor_ollama.py                   |  12 +
     platform_tests/scripts/test_db_snapshot_launcher_in_root.py  |  24 +
     platform_tests/scripts/test_dispatcher_daemon_supervision.py |  37 +
     platform_tests/scripts/test_gtkb_dispatcher_daemon.py        |  26 +
     scripts/gtkb_dispatcher_daemon.py                            |   1 +
     scripts/install_db_snapshot_task.ps1                         |  17 +-
     scripts/ops/harness_storm_watchdog_launcher.py               |  53 +
```

## Acceptance Criteria Status

- [x] The daemon Ollama autostart probe cannot allocate or flash a visible console when invoking PowerShell on Windows.
- [x] Daemon watchdog auto-restart cannot allocate or flash a visible console when invoking `schtasks.exe` on Windows.
- [x] The storm-watchdog scheduled-task entrypoint is a tracked, tested Python launcher suitable for `pythonw.exe` execution and does not depend on the broken VBS wrapper.
- [x] The db snapshot installer writes the launcher in-root and registers the task with a GUI-subsystem Python (`pythonw.exe`) and hidden settings.
- [x] The currently installed `GTKB-DbSnapshot` task remains hidden, points at the in-root launcher, and completes a manual run with result `0`.
- [x] Focused regression tests and lint/format checks pass.
- [x] No topology, dispatcher target eligibility, credential, deployment, database-schema, or snapshot-output-location changes are made.

## Risk And Rollback

Residual risks / follow-ups:

- `groundtruth-kb/src/groundtruth_kb/bridge/launcher.py` still contains bare legacy `schtasks.exe` query/run calls. That file is outside this GO target set, belongs to retained legacy bridge-worker compatibility code, and was not edited. It should be covered by a follow-on bridge target if the legacy launcher remains active anywhere.
- `.gtkb-state/ops/run_harness_storm_watchdog_hidden.vbs` remains as an inactive stale generated artifact. The implementation gate blocked deleting it because it was outside the authorization packet. Current `GTKB-HarnessStormWatchdog` Task Scheduler action does not reference it; the task points at `scripts/ops/harness_storm_watchdog_launcher.py` through `pythonw.exe`.
- Runtime dispatcher health remains `WARN` due `loyal-opposition:F` / OpenRouter failure-backoff evidence. That is outside the Windows console/focus-steal fix and did not block proving the daemon/scheduled-task no-console paths.
- During runtime verification, re-enabling the dispatcher while this GO was still latest caused duplicate Codex PB auto-dispatch workers for the same GO. They were stopped, the accidental worker claim was released, and this session reclaimed the work item. This is a dispatcher/work-intent suppression behavior worth separate follow-up; it is not a visible-console regression.

Rollback path: revert the eight files listed in "Files Changed" and re-register `GTKB-DbSnapshot` from the prior installer if needed. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
