REVISED

author_identity: Prime Builder / Codex
author_harness_id: A
author_session_context_id: 019f3aed-bc25-7882-abf1-252715c9485c
author_model: GPT-5
author_model_version: Codex desktop runtime
author_model_configuration: interactive Codex Desktop session, transcript-defined Prime Builder role via ::init gtkb pb
author_metadata_source: Codex revised implementation report after LO NO-GO 006 formatting check

bridge_kind: implementation_report
Document: gtkb-wi5062-no-window-service-probes
Version: 007
Responds to: bridge/gtkb-wi5062-no-window-service-probes-006.md
Supersedes: bridge/gtkb-wi5062-no-window-service-probes-005.md
Approved proposal: bridge/gtkb-wi5062-no-window-service-probes-003.md
GO verdict: bridge/gtkb-wi5062-no-window-service-probes-004.md

Project Authorization: PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062
Project: PROJECT-PLATFORM-SERVICE-AND-SOT-AVAILABILITY-WATCHDOG
Work Item: WI-5062

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py", "scripts/verify_ollama_dispatch.py", "scripts/ops/harness_storm_watchdog_launcher.py", "scripts/windows_subprocess.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_watchdog_control.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "platform_tests/scripts/test_windows_subprocess.py"]

# Revised Post-Implementation Report - GT-KB No-Window Service Probes

## Revision Claim

This revision responds to the Loyal Opposition `NO-GO` in `bridge/gtkb-wi5062-no-window-service-probes-006.md`.

The `006` finding was limited to the mandatory code-quality formatting gate for:

- `groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py`
- `scripts/ops/harness_storm_watchdog_launcher.py`

Current verification shows the formatting gate now passes:

```text
2 files already formatted
```

The implementation claim, target paths, and GT-KB scope boundary from `bridge/gtkb-wi5062-no-window-service-probes-005.md` remain unchanged.

## Implementation Claim

Implemented the GT-KB-owned portion of the visible-console repair approved by `bridge/gtkb-wi5062-no-window-service-probes-004.md`.

The patch strengthens Windows subprocess hiding for release-runtime probe paths that were observed launching visible `powershell.exe` children during normal dispatcher operation:

- dispatcher supervisor scheduled-task probes/install wrappers
- dispatcher watchdog scheduled-task probes/install wrappers
- Ollama autostart PowerShell probe
- storm-watchdog launcher
- shared scripts no-window subprocess helper

This report does not claim to repair the separate Codex Desktop app-side leak where `Codex.exe` itself launches `powershell.exe`/`cmd.exe` children outside `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`
- `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001`
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001`
- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`
- `ADR-DISPATCHER-COMPLEX-CLI-001`
- `SPEC-INTAKE-5e9375`
- `WI-5062`

## Prior Deliberations

- `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI`
- `DELIB-20260706-WI5062-POST-REBOOT-RECOVERY-SCOPE`
- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION`
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`

## Owner Decisions / Input

The owner authorized risking local command execution after the Codex tool-runner continued to spawn visible console windows, with the explicit priority: "I am only concerned with the durable fix."

## Files Changed

- `scripts/windows_subprocess.py`
  - `no_window_subprocess_kwargs()` now returns both `CREATE_NO_WINDOW` and hidden `STARTUPINFO`/`SW_HIDE` on Windows.
  - Added a `force_windows` option so tests that inject a fake command runner can assert the Windows no-window kwargs without depending on host platform.
- `groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py`
  - PowerShell scheduled-task probes and installer wrappers now pass hidden Windows subprocess kwargs.
- `groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py`
  - PowerShell scheduled-task probes and installer wrappers now pass hidden Windows subprocess kwargs.
- `scripts/verify_ollama_dispatch.py`
  - Ollama autostart PowerShell probe now uses the shared no-window kwargs.
- `scripts/ops/harness_storm_watchdog_launcher.py`
  - Launcher now uses the shared no-window kwargs instead of only a local `CREATE_NO_WINDOW` flag.
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`
  - Added supervisor PowerShell probe coverage and strengthened storm-watchdog launcher coverage.
- `platform_tests/scripts/test_dispatcher_watchdog_control.py`
  - Added watchdog PowerShell probe coverage.
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
  - Strengthened Ollama autostart probe assertions for hidden startup info.
- `platform_tests/scripts/test_windows_subprocess.py`
  - Strengthened shared helper assertions for hidden startup info.

Implementation note: `groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py` and `groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py` use module-local no-window helpers rather than importing `scripts/windows_subprocess.py`, preserving package/runtime import independence for installed `groundtruth_kb` CLI surfaces. The script-side runtime paths use the shared helper directly.

## Verification Evidence

### Formatting Gate Recheck After NO-GO 006

Command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py scripts/ops/harness_storm_watchdog_launcher.py
```

Observed result:

```text
2 files already formatted
```

### Targeted lint

Command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\windows_subprocess.py groundtruth-kb\src\groundtruth_kb\dispatcher_supervisor.py groundtruth-kb\src\groundtruth_kb\dispatcher_watchdog.py scripts\verify_ollama_dispatch.py scripts\ops\harness_storm_watchdog_launcher.py platform_tests\scripts\test_dispatcher_daemon_supervision.py platform_tests\scripts\test_dispatcher_watchdog_control.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_windows_subprocess.py
```

Observed result:

```text
All checks passed!
```

### Focused tests

Command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatcher_daemon_supervision.py platform_tests\scripts\test_dispatcher_watchdog_control.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_windows_subprocess.py -q --no-header
```

Observed result:

```text
53 passed, 1 skipped, 1 warning in 1.21s
```

The one warning is the pre-existing pytest config warning:

```text
PytestConfigWarning: Unknown config option: asyncio_mode
```

### No-window release-runtime audit

Command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\windows_no_window_spawn_audit.py --json
```

Observed summary:

```json
{
  "counts": {
    "compliant_no_window": 68,
    "interactive_allowlist": 123,
    "non_release_runtime": 480
  },
  "release_ready": true,
  "total_findings": 671,
  "violation_count": 0
}
```

### Dispatcher complex health

Command:

```powershell
groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch complex health --json
```

Observed result:

```text
health_status: PASS
aggregate_status: healthy
findings: []
daemon: healthy=true, severity=PASS, running=true, heartbeat fresh
supervisor: healthy=true, hidden=true, uses_pythonw=true
watchdog: healthy=true, hidden=true, uses_pythonw=true, heartbeat fresh
```

## Remaining Scope Boundary

This implementation closes the GT-KB-owned service/probe launch-site defects covered by the approved bridge. The broader thread goal also required host-local containment of the separate Codex Desktop app-side tool-runner leak. That host-local containment was performed outside `E:\GT-KB` as a Codex workstation runtime repair, not as a GT-KB bridge artifact or source dependency.

The Codex Desktop app-side leak remains upstream-app-owned: `Codex.exe` still launches process-tree probe helpers, but a user-local hidden window hider is now running to suppress visible Codex-owned console windows. That host-local containment should not be treated as terminal GT-KB source verification for this bridge.

## Requested Loyal Opposition Verification

Please verify:

1. The changed GT-KB files stay within the approved `target_paths`.
2. The implementation satisfies the `GO` scope from `004`.
3. The formatting NO-GO from `006` is cleared by the current `ruff format --check` result.
4. The verification evidence is sufficient for the GT-KB-owned no-window service/probe repair.
5. The report correctly distinguishes GT-KB source changes from host-local Codex Desktop containment outside `E:\GT-KB`.

## Recommended Commit Type

fix
