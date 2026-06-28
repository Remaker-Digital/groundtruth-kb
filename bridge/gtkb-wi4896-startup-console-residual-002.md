REVISED

# gtkb-wi4896-startup-console-residual - Minute-cadence Windows console and focus-steal fix

bridge_kind: prime_proposal
Document: gtkb-wi4896-startup-console-residual
Version: 002
Author: Prime Builder Codex
Date: 2026-06-27T19:50:00Z

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-a-20260627-startup-console-residual-revised
author_model: GPT-5
author_model_version: 2026-06-27
author_model_configuration: Codex desktop; danger-full-access; approval-policy never; interactive role Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4896

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_ollama.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "scripts/ops/harness_storm_watchdog_launcher.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "scripts/install_db_snapshot_task.ps1", "platform_tests/scripts/test_db_snapshot_launcher_in_root.py"]

implementation_scope: source,test,config-runtime-installer,runtime-task-repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Mike observed a Windows console or dialog stealing keyboard focus roughly once per minute. Runtime mitigation has disabled the two minute-cadence tasks, `GTKB-DispatcherDaemon` and `GTKB-HarnessStormWatchdog`, and stopped live daemon processes so the workstation is usable while this reviewed fix proceeds. `GTKB-DbSnapshot` remains enabled because its repaired live task is hidden, uses `pythonw.exe`, and is not part of the minute-cadence focus steal.

The revised evidence narrowed the residual defect beyond the original boot-time theory:

1. The dispatcher daemon tick invokes the Ollama host-readiness/doctor autostart probe every minute through `groundtruth-kb/src/groundtruth_kb/project/doctor.py::_ollama_windows_autostart_finding`. That probe launches `powershell.exe` to run `Get-ScheduledTask` and `Get-Service` without `CREATE_NO_WINDOW` or `stdin=subprocess.DEVNULL`. A live process monitor caught this exact parent chain: daemon `pythonw.exe` to `powershell.exe` Ollama autostart probe to console host / terminal embedding.
2. The stale storm-watchdog VBS wrapper raised a Windows Script Host error dialog because it uses `Option Explicit` but assigns `pythonw = ...` without `Dim pythonw`. The currently registered `GTKB-HarnessStormWatchdog` action already points at `scripts/ops/harness_storm_watchdog_launcher.py` through `pythonw.exe`, so this proposal makes the Python launcher a tracked, tested replacement and prevents returning to a VBS or visible-PowerShell path.
3. The daemon watchdog restart path still needs no-window subprocess discipline for `schtasks.exe /Run`, and the db snapshot installer source still needs to preserve the live repaired `pythonw.exe` plus hidden task behavior on future reinstall.

This remains WI-4896 scope: suppress user-visible Windows console/dialog creation from dispatcher/background GT-KB automation. It does not change dispatcher topology, ranking, target eligibility, credentials, deployment, database schema, or snapshot output location.

## Runtime Safety Brake Already Applied

To stop active focus stealing before source repair, the live runtime state was changed as follows:

- `GTKB-DispatcherDaemon`: disabled and stopped; live daemon processes killed.
- `GTKB-HarnessStormWatchdog`: disabled and stopped; no live wrapper process remains.
- `GTKB-DbSnapshot`: left enabled; live task is hidden, uses `pythonw.exe`, points at `.gtkb-state/db-snapshot/gtkb_db_snapshot_task.py`, and last manual run returned `0`.

These runtime disables should remain in place until the reviewed implementation is applied and verified, then the corrected tasks can be re-enabled deliberately.

## Defect / Reproduction Evidence

Observed runtime facts:

- One-minute process monitor caught the daemon spawning `powershell.exe` for the Ollama autostart probe. The command queries Windows scheduled tasks and services and is parented by the dispatcher daemon `pythonw.exe` process.
- That process then allocated a console host / terminal embedding, matching the visible blank console window and the one-minute cadence.
- Mike supplied a screenshot of a Windows Script Host error dialog for the stale storm-watchdog VBS wrapper. The generated wrapper contains `Option Explicit`, declares `shell`, `scriptPath`, and `command`, but assigns `pythonw = ...` without declaring `pythonw`, producing `Variable is undefined: 'pythonw'`.
- The current `GTKB-HarnessStormWatchdog` task action is already a `pythonw.exe` invocation of `scripts/ops/harness_storm_watchdog_launcher.py`; that launcher must be tracked and tested so the system does not regress to the broken VBS or visible PowerShell wrapper.
- The current `GTKB-DispatcherDaemon` task is hidden and uses `pythonw.exe`, but it remains disabled by the safety brake until source repair is verified.

## In-Root Placement Evidence

All source/test targets are in-root relative paths: `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/tests/test_doctor_ollama.py`, `scripts/gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, `scripts/ops/harness_storm_watchdog_launcher.py`, `platform_tests/scripts/test_dispatcher_daemon_supervision.py`, `scripts/install_db_snapshot_task.ps1`, and `platform_tests/scripts/test_db_snapshot_launcher_in_root.py`.

The db snapshot runtime launcher remains `.gtkb-state/db-snapshot/gtkb_db_snapshot_task.py`, an in-root generated runtime path accepted by WI-4512. The stale storm-watchdog VBS file is generated runtime residue, not the intended durable launcher surface.

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Requires Windows dispatcher/background paths to run non-interactively without visible console windows; this fix applies that requirement to the daemon's doctor/Ollama PowerShell probe, watchdog restart, storm-watchdog launcher, and db snapshot task installer.
- `ADR-DISPATCHER-ARCHITECTURE-001` - The dispatcher daemon is the black-box dispatch substrate; daemon tick health/readiness probes and watchdog remediation belong in daemon-owned source and tests.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - The daemon composes and records dispatch/remediation work without user-facing UI; no-console subprocess discipline preserves that service boundary.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Runtime launchers that scheduled tasks execute must live in-root and not depend on temp paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected `groundtruth-kb/src/`, `scripts/`, `platform_tests/`, and `groundtruth-kb/tests/` changes require bridge proposal, LO GO, implementation claim, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites governing requirements for the source/test changes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal carries Project Authorization, Project, Work Item, and target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation report must map each changed behavior to exact tests and runtime verification.
- `GOV-STANDING-BACKLOG-001` - WI-4896 is the active owner-reported dispatcher console-window regression item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The owner-reported runtime defect and the safety-brake decision are preserved as durable bridge evidence instead of remaining only in chat.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The fix links defect evidence, source edits, tests, runtime verification, and implementation reporting as one traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - This REVISED proposal explicitly supersedes the earlier residual proposal version with newer runtime evidence and a corrected target path set.

## Prior Deliberations

- `DELIB-20266297` - Owner directive and authorization for WI-4896 dispatcher console-window suppression.
- `DELIB-20266276` - Daemon resilience scope-lock and scheduled-supervisor context.
- `DELIB-20266192` - WI-4852 watchdog dormancy auto-restart authorization; this proposal repairs no-console behavior of that remediation path.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-001.md` - first WI-4896 proposal for initial launcher surfaces.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-003.md` - first WI-4896 implementation report, awaiting LO verification and explicitly scoped away from scheduled-task definitions.
- `bridge/gtkb-wi4896-startup-console-residual-001.md` - earlier residual proposal, superseded by this revised evidence and expanded target set.
- `bridge/gtkb-wi4512-db-snapshot-launcher-in-root-004.md` - VERIFIED db snapshot launcher-in-root fix; disclosed residual that existing scheduled-task installations need re-registration.

## Owner Decisions / Input

No new owner decision is required. The owner asked to stop recurring Windows console/dialog popups from dispatcher/background automation, and the runtime focus-steal made immediate task disablement necessary as a safety brake. `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION` authorizes bounded source, test, and hook/background launcher changes under `DELIB-20266297`; topology, credential, deployment, and database schema changes remain out of scope.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001` already cover no-console Windows background execution, daemon ownership, centralized service behavior, and in-root runtime launchers. No new or revised requirement is needed before implementation.

## Proposed Scope

- In `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, update the Windows Ollama autostart probe subprocess call to use `stdin=subprocess.DEVNULL`, `CREATE_NO_WINDOW` on Windows, `-NonInteractive`, and captured output with the current timeout/check behavior preserved.
- In `groundtruth-kb/tests/test_doctor_ollama.py`, extend the Windows autostart test so it asserts the probe call includes no-window creation flags and detached stdin on Windows.
- In `scripts/gtkb_dispatcher_daemon.py`, update `_restart_storm_watchdog` so the `schtasks.exe /Run` subprocess runs with `stdin=subprocess.DEVNULL`, output suppression/capture as appropriate, and `CREATE_NO_WINDOW` on Windows.
- In `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, add or extend coverage proving the watchdog restart subprocess receives no-window flags and null stdin while preserving success/failure return semantics.
- Track and test `scripts/ops/harness_storm_watchdog_launcher.py` as the Python `pythonw.exe` Task Scheduler entrypoint that runs `scripts/ops/harness_storm_watchdog.ps1` with `CREATE_NO_WINDOW`, `-NonInteractive`, `-WindowStyle Hidden`, and null stdio.
- In `platform_tests/scripts/test_dispatcher_daemon_supervision.py`, add focused launcher coverage for that storm-watchdog entrypoint if this is the existing natural home for daemon/supervision subprocess contracts.
- In `scripts/install_db_snapshot_task.ps1`, prefer `pythonw.exe` for the scheduled-task action and register/update the task with hidden settings while preserving the in-root launcher path from WI-4512, `StartWhenAvailable`, retention behavior, and snapshot output location.
- In `platform_tests/scripts/test_db_snapshot_launcher_in_root.py`, extend the installer contract so it asserts no `$env:TEMP`, an in-root launcher, `pythonw.exe` action discipline, and hidden scheduled-task settings.
- After source verification, re-register or re-enable only the corrected runtime tasks needed to verify no-console behavior; keep topology and target eligibility unchanged.

## Out Of Scope

- Dispatcher topology, ranking weights, target eligibility, and harness role assignments.
- Credential, deployment, or database-schema changes.
- Snapshot output location changes.
- Retired OS poller or smart poller restoration.
- Any out-of-root GT-KB artifact dependency.

## Specification-Derived Verification Plan

| Spec / requirement | Planned verification |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Focused tests assert daemon/doctor/watchdog/db-snapshot subprocess paths use `pythonw.exe` or `CREATE_NO_WINDOW`, hidden task settings where applicable, `-NonInteractive` for PowerShell probes, and null stdin/stdio. |
| `ADR-DISPATCHER-ARCHITECTURE-001` / `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Existing dispatcher daemon tests plus daemon status inspection confirm no topology or selection behavior change. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Existing/extended db snapshot and storm-watchdog launcher tests confirm scheduled-task launchers remain in-root, not temp/runtime-only script bodies. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implement only after latest bridge status is GO and a matching work-intent/implementation-start packet authorizes the target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report will map each linked spec to exact commands and observed results. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge revision, implementation report, and verification evidence preserve the owner-observed defect, safety brake, supersession of `-001`, tests, and runtime repair as durable linked artifacts. |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_ollama.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_db_snapshot_launcher_in_root.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_ollama.py scripts/gtkb_dispatcher_daemon.py scripts/ops/harness_storm_watchdog_launcher.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_db_snapshot_launcher_in_root.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_ollama.py scripts/gtkb_dispatcher_daemon.py scripts/ops/harness_storm_watchdog_launcher.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_db_snapshot_launcher_in_root.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install_db_snapshot_task.ps1
Get-ScheduledTask -TaskName GTKB-DbSnapshot
Start-ScheduledTask -TaskName GTKB-DbSnapshot; Get-ScheduledTaskInfo -TaskName GTKB-DbSnapshot
```

Runtime verification after tests:

- Re-enable/start `GTKB-HarnessStormWatchdog` and `GTKB-DispatcherDaemon` only after source fixes are in place.
- Monitor at least one full minute-cadence boundary for absence of new visible Windows console, Windows Script Host, or focus-stealing terminal windows.
- Keep `GTKB-DbSnapshot` hidden and verify manual run result `0`.

## Pre-Filing Preflight Evidence

Draft content preflight:

- Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4896-startup-console-residual-002.md --json`
- Result: `preflight_passed=true`, `missing_required_specs=[]`, `missing_advisory_specs=[]`
- Packet hash: `sha256:2316051e71a95b5e7c86e90f0f4f8169570233143071f7d88178627975887f41`

Clause preflight:

- Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4896-startup-console-residual-002.md`
- Result: exit `0`; `must_apply=4`; evidence gaps in must-apply clauses `0`; blocking gaps `0`

## Acceptance Criteria

- [ ] The daemon Ollama autostart probe cannot allocate or flash a visible console when invoking PowerShell on Windows.
- [ ] Daemon watchdog auto-restart cannot allocate or flash a visible console when invoking `schtasks.exe` on Windows.
- [ ] The storm-watchdog scheduled-task entrypoint is a tracked, tested Python launcher suitable for `pythonw.exe` execution and does not depend on the broken VBS wrapper.
- [ ] The db snapshot installer writes the launcher in-root and registers the task with a GUI-subsystem Python (`pythonw.exe`) and hidden settings.
- [ ] The currently installed `GTKB-DbSnapshot` task remains hidden, points at the in-root launcher, and completes a manual run with result `0`.
- [ ] Focused regression tests and lint/format checks pass.
- [ ] No topology, dispatcher target eligibility, credential, deployment, database-schema, or snapshot-output-location changes are made.

## Risks / Rollback

Risk is low and localized to Windows process-launch configuration. Hiding/capturing subprocess output could obscure stdout/stderr, but the affected probes already return structured success/error summaries and remain observable through daemon status, logs, and Task Scheduler state. Switching db snapshot scheduling from `python.exe` to `pythonw.exe` hides console output; snapshot success remains observable through Task Scheduler `LastTaskResult` and snapshot files/logs.

Rollback is a single commit revert for the source/test files plus, if needed, disabling `GTKB-DispatcherDaemon` and `GTKB-HarnessStormWatchdog` again. No database rollback, topology rollback, credential rotation, or deployment rollback is involved.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor_ollama.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `scripts/ops/harness_storm_watchdog_launcher.py`
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`
- `scripts/install_db_snapshot_task.ps1`
- `platform_tests/scripts/test_db_snapshot_launcher_in_root.py`

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
