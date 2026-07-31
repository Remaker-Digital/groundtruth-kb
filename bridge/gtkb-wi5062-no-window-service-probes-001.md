NEW

# gtkb-wi5062-no-window-service-probes — Hide GT-KB service probe PowerShell children

bridge_kind: prime_proposal
Document: gtkb-wi5062-no-window-service-probes
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-07T06:45:00Z

author_identity: Prime Builder / Codex
author_harness_id: A
author_session_context_id: 019f3aed-bc25-7882-abf1-252715c9485c
author_model: GPT-5
author_model_version: Codex desktop runtime
author_model_configuration: interactive Codex Desktop session, transcript-defined Prime Builder role via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062
Project: PROJECT-PLATFORM-SERVICE-AND-SOT-AVAILABILITY-WATCHDOG
Work Item: WI-5062

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py", "scripts/verify_ollama_dispatch.py", "scripts/ops/harness_storm_watchdog_launcher.py", "scripts/windows_subprocess.py", "platform_tests/scripts/test_dispatcher_supervisor.py", "platform_tests/scripts/test_dispatcher_watchdog.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "platform_tests/scripts/test_windows_subprocess.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

External process-monitor evidence from 2026-07-06 23:23-23:24 PDT shows the restored dispatcher complex is functionally healthy but still launches visible-prone PowerShell children from GT-KB background services. The GT-KB-owned entries are `pythonw.exe` parents running `scripts/gtkb_service_sot_watchdog.py`, `scripts/gtkb_dispatcher_daemon.py`, and `scripts/ops/harness_storm_watchdog_launcher.py`; their children run PowerShell scheduled-task, service, and watchdog probes.

This proposal repairs only the GT-KB background-service no-window defects by routing those subprocess calls through the shared Windows hidden-process helper and adding focused tests. It does not claim to repair the separate Codex Desktop app-side issue where `Codex.exe` launches its own process-monitor `powershell.exe` and `cmd.exe` children during tool execution.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires this Prime Builder proposal to enter the file bridge as NEW and receive Loyal Opposition GO before protected source/test edits begin.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this implementation proposal to cite the governing work item, specs, target paths, and verification surface before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the Project Authorization, Project, and Work Item header lines above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires verification to map from the linked service/dispatcher requirements to concrete tests and runtime evidence.
- `GOV-STANDING-BACKLOG-001` — supports preserving and routing this owner-observed operational defect into the governed backlog/bridge workflow rather than making an ungated protected-source edit.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` — the dispatcher supervisor/daemon lifecycle must remain supervised without introducing visible console windows during normal operation.
- `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001` — the repair must preserve the single-daemon/single-supervisor process invariant while changing probe subprocess options.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` — the service/watchdog recovery path must stay healthy and verifiable after the no-window repair.
- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` — the platform service and SoT watchdog is the restoration/health owner for these service artifacts.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` — watchdog repair must preserve guarded restore behavior, retry bounds, and owner-quiesce safety.
- `ADR-DISPATCHER-COMPLEX-CLI-001` — dispatcher complex controls and health reporting must continue to operate through the governed CLI surfaces.
- `SPEC-INTAKE-5e9375` — WI-5062 PAUTH includes this intake spec in the dispatcher supervisor self-healing scope.

## Prior Deliberations

- `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI` — owner authorization for WI-5062 dispatcher supervisor self-healing, guarded disable controls, and mapped tests.
- `DELIB-20260706-WI5062-POST-REBOOT-RECOVERY-SCOPE` — scope amendment requiring post-reboot recovery evidence for the dispatcher supervisor/SoT watchdog path.
- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` — project-level authorization for platform service and SoT availability watchdog work.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — explains why WI-5062 was previously resolved by verified child threads and why residual evidence must reopen or continue via bridge rather than bypassing verification.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — governs this proposal's structured linkage, target path, and verification-heading shape.

## Owner Decisions / Input

Current owner directive in session `019f3aed-bc25-7882-abf1-252715c9485c`: restore Codex, all harnesses, and the dispatcher complex to full functioning with no visible console windows during normal operation. The owner provided external monitor evidence and then explicitly requested `start bridge proposal` after being told protected source/test edits require a live bridge GO.

The implementation authorization is the active `PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062`, which covers WI-5062 dispatcher supervisor self-healing, service/SoT watchdog restore execution logic, dispatcher complex control/health guardrails, mapped tests, and bridge evidence.

## Requirement Sufficiency

Existing requirements sufficient for the GT-KB-owned portion of the defect. `WI-5062`, `PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062`, `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`, `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`, and `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` already require the dispatcher supervisor/watchdog complex to restore and report health as background services without normal-operation disruption.

Out of scope: Codex Desktop's separate app-side process monitor still launches `powershell.exe` and `cmd.exe` from `Codex.exe`. That defect is not repairable in this GT-KB repository and must remain isolated from the GT-KB bridge implementation scope.

## Spec-Derived Verification Plan

Implementation must map each linked specification to a test or verification command and the expected result. Use the repo venv interpreter for reproducible evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_supervisor.py platform_tests/scripts/test_dispatcher_watchdog.py platform_tests/scripts/test_verify_ollama_dispatch.py platform_tests/scripts/test_windows_subprocess.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe scripts/windows_no_window_spawn_audit.py --json
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch complex health --json
```

Expected results:

- `dispatcher_supervisor.py` and `dispatcher_watchdog.py` PowerShell status/enable/disable/install helper calls use the shared no-window subprocess kwargs or equivalent `CREATE_NO_WINDOW` plus hidden `STARTUPINFO`.
- `verify_ollama_dispatch.py::evaluate_ollama_autostart` uses the shared hidden helper for the Ollama scheduled-task/service PowerShell probe, not a bare `creationflags` integer.
- `harness_storm_watchdog_launcher.py` uses the same shared helper rather than a local partial `CREATE_NO_WINDOW` implementation.
- Existing dispatcher complex health remains `PASS`: daemon running, supervisor/watchdog ready, hidden, and `pythonw.exe` backed.
- The no-window audit covers the modified files and reports no remaining bare visible-prone PowerShell subprocess launches in these GT-KB service paths.
- A short owner-observed runtime window after restoration shows no GT-KB-owned `pythonw.exe -> powershell.exe` visible console spawns during normal dispatcher/watchdog operation.

## Risk / Rollback

Risk surface is Windows-specific subprocess behavior in service/watchdog control paths. The main regression risks are breaking scheduled-task status parsing, losing diagnostic detail from PowerShell failures, or weakening restore guardrails while changing subprocess kwargs.

Rollback is a single-commit revert of the implementation commit. No database, credential, deployment, canonical-store restore, retired poller restoration, or destructive cleanup is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5062-no-window-service-probes`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix — the change repairs visible console spawning from GT-KB-owned background service probes while preserving existing dispatcher/watchdog behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
