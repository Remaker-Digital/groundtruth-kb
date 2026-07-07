REVISED

# gtkb-wi5062-no-window-service-probes - Hide GT-KB service probe PowerShell children

bridge_kind: prime_proposal
Document: gtkb-wi5062-no-window-service-probes
Version: 003
Author: Prime Builder (Codex A)
Date: 2026-07-07T06:58:00Z

author_identity: Prime Builder / Codex
author_harness_id: A
author_session_context_id: 019f3aed-bc25-7882-abf1-252715c9485c
author_model: GPT-5
author_model_version: Codex desktop runtime
author_model_configuration: interactive Codex Desktop session, transcript-defined Prime Builder role via ::init gtkb pb
author_metadata_source: direct Codex apply_patch emergency path after Codex tool-runner console-window leak

Project Authorization: PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062
Project: PROJECT-PLATFORM-SERVICE-AND-SOT-AVAILABILITY-WATCHDOG
Work Item: WI-5062

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py", "scripts/verify_ollama_dispatch.py", "scripts/ops/harness_storm_watchdog_launcher.py", "scripts/windows_subprocess.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_watchdog_control.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "platform_tests/scripts/test_windows_subprocess.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Notes

This revision responds to `bridge/gtkb-wi5062-no-window-service-probes-002.md` (`NO-GO`).

The only proposal correction is the target path mismatch identified by Loyal Opposition:

- `platform_tests/scripts/test_dispatcher_supervisor.py` is replaced with `platform_tests/scripts/test_dispatcher_daemon_supervision.py`.
- `platform_tests/scripts/test_dispatcher_watchdog.py` is replaced with `platform_tests/scripts/test_dispatcher_watchdog_control.py`.

The bridge-propose Python helper was not used for this revision because the active incident is a Codex Desktop/tool-runner console-window leak: the helper path requires spawning a local Python child, and the owner observed four visible console windows from the immediately preceding hidden-wrapper diagnostic. This direct patch is limited to the status-bearing bridge revision needed to unblock Loyal Opposition review; protected implementation targets remain untouched until `GO`.

## Proposal Summary

GT-KB currently has background service/probe paths that can still launch visible PowerShell console windows during normal dispatcher operation even when the scheduled tasks themselves use `pythonw.exe` and hidden Task Scheduler settings.

External process-monitor evidence showed GT-KB-owned background processes launching visible-prone PowerShell children from:

- `groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py`
- `scripts/verify_ollama_dispatch.py`
- `scripts/ops/harness_storm_watchdog_launcher.py`

The implementation will route those Windows child-process calls through the shared `scripts/windows_subprocess.py` no-window helpers, strengthening the common helper where needed so subprocess calls carry both `CREATE_NO_WINDOW` and hidden `STARTUPINFO`/`SW_HIDE` on Windows.

This proposal is scoped to GT-KB-owned service/probe launch paths. It does not claim to repair the separate Codex Desktop app-side console-window leak where `Codex.exe` itself launches `powershell.exe`/`cmd.exe` children.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - status-bearing bridge file authority and role eligibility.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete implementation proposal linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project and work-item linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map to cited requirements and changed behavior.
- `GOV-STANDING-BACKLOG-001` - visible operational reliability defects are tracked work.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - dispatcher supervision must be reliable and diagnosable.
- `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001` - daemon supervision must not multiply unsafe launch surfaces.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` - recovery path must be normal-operation safe.
- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - platform service/SoT watchdog owns restoration checks.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - restoration and probe behavior must be safe.
- `ADR-DISPATCHER-COMPLEX-CLI-001` - dispatcher complex control surfaces must operate through governed CLI/runtime paths.
- `SPEC-INTAKE-5e9375` - no visible console windows during normal operation.

## Prior Deliberations

- `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI`
- `DELIB-20260706-WI5062-POST-REBOOT-RECOVERY-SCOPE`
- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION`
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`

## Owner Decisions / Input

The owner directly reported visible console windows spawning every few seconds during Codex and dispatcher operation, authorized diagnosis and repair of Codex/all harnesses/the dispatcher complex, and directed Prime Builder to start the bridge proposal after emergency containment.

## Requirement Sufficiency

Existing requirements are sufficient for the GT-KB-owned portion: normal dispatcher operation must not spawn visible console windows, and the dispatcher complex must remain healthy and governed. The separate Codex Desktop app-side leak is out of this implementation scope because it originates from `Codex.exe` outside the `E:/GT-KB` project root.

## Implementation Plan

1. Strengthen `scripts/windows_subprocess.py::no_window_subprocess_kwargs()` so Windows subprocess callers get both `CREATE_NO_WINDOW` and hidden `STARTUPINFO`/`SW_HIDE`.
2. Update dispatcher supervisor PowerShell probes/install/enable/disable paths to consume the shared helper.
3. Update dispatcher watchdog PowerShell probes/install/enable/disable/uninstall paths to consume the shared helper.
4. Update the Ollama autostart PowerShell probe in `scripts/verify_ollama_dispatch.py` to consume the shared helper, including test assertions for hidden startup info.
5. Update `scripts/ops/harness_storm_watchdog_launcher.py` to consume the shared helper instead of only setting a local `CREATE_NO_WINDOW` flag.
6. Add/update focused tests for each changed launch site.

## Mandatory Spec-Derived Verification Plan

Run the focused no-window and dispatcher control tests:

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_dispatcher_watchdog_control.py platform_tests/scripts/test_verify_ollama_dispatch.py platform_tests/scripts/test_windows_subprocess.py -q --no-header
```

Run the release-runtime no-window spawn audit:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/windows_no_window_spawn_audit.py --json
```

Run dispatcher complex health:

```powershell
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch complex health --json
```

Expected results:

- Focused tests pass.
- The no-window audit reports `release_ready: true` and zero violations for the changed launch paths.
- Dispatcher complex health remains `PASS`.
- Owner runtime observation shows no GT-KB-owned visible PowerShell windows during normal dispatcher operation.

## Risk / Rollback

Risk is limited to Windows subprocess launch configuration. Rollback is the file-level revert of the changed helper/call sites if tests or runtime health regress. The implementation must not restore retired poller paths, mutate credentials, perform destructive cleanup, or alter production deployment configuration.

## Requested Loyal Opposition Review

Please verify that the corrected `target_paths` list is accurate, that the direct revision filing is acceptable under the console-window incident constraints, and that the proposed scope is sufficient for the GT-KB-owned console-window leak while correctly excluding the external Codex Desktop app-side leak.

## Commit Type

fix
