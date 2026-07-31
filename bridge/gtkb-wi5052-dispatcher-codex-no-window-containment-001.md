NEW

# gtkb-wi5052-dispatcher-codex-no-window-containment — dispatcher Codex no-window containment

bridge_kind: prime_proposal
Document: gtkb-wi5052-dispatcher-codex-no-window-containment
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07T19:10:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-07-codex-pb-no-visible-console-windows
author_model: gpt-5
author_model_version: codex
author_model_configuration: interactive Codex desktop session, role override `::init gtkb pb`

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5052-DISPATCHER-NO-WINDOW-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5052

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py", "scripts/windows_no_window_spawn_audit.py", "platform_tests/scripts/test_windows_no_window_spawn_audit.py", "config/dispatcher/rules.toml", "harness-state/harness-registry.json"]

implementation_scope: source | configuration | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner reported that visible console windows were spawning relentlessly on the workstation for roughly 30 minutes, stealing focus and destabilizing input. Live process evidence showed auto-dispatched bridge workers launching `codex.EXE exec`; the worker process tree included a long-lived `pwsh.exe` child under Codex CLI command-safety handling. The workstation-local hider log simultaneously recorded repeated Windows Terminal/Cascadia windows hosting `C:\Program Files\PowerShell\7\pwsh.exe`. The spawning stopped immediately after the dispatcher worker tree was stopped and the dispatcher complex was placed under a guarded quiesce.

This proposal authorizes a bounded WI-5052 repair so dispatcher/Codex auto-dispatch cannot create visible Terminal/PowerShell/cmd windows on Windows. The implementation may keep Codex auto-dispatch quarantined on Windows until the launch path is proven no-window safe; add or tighten dispatcher source/config guards; expand focused audit/test coverage; and require monitor-backed no-visible-window evidence before the dispatcher complex is re-enabled.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this protected dispatcher/config change requires a bridge proposal, Loyal Opposition GO, and an implementation-start packet before source/config mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — WI-5052 is covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5052-DISPATCHER-NO-WINDOW-20260707`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the PAUTH does not bypass bridge review or implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal maps the implementation to governing requirements and verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the header includes Project Authorization, Project, and Work Item fields.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must include spec-derived tests and monitor evidence before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-5052 is the standing-backlog defect item surfaced by no-window audit repair.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — Windows dispatcher work must remain headless/no-window safe.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatcher changes must preserve the centralized bridge dispatch architecture while allowing guarded quiesce for unsafe launch paths.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` — dispatcher disable/enable and health state must flow through the governed dispatcher control surface.

## Prior Deliberations

- `INTAKE-8242840e` — Intake: Simple dispatcher retry and OPS-owned failed-workflow recovery
- `INTAKE-6554ff58` — Intake: Dispatcher daemon complex: harmonized management CLI + unified complex-health contract
- `INTAKE-37a7892d` — Intake: Minimal dispatcher quarantine state for lifecycle artifacts
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` — owner directive that no visible console windows may spawn on this workstation and that the dispatcher may remain quiesced until repaired and verified.
- `INTAKE-8242840e` is relevant because this repair must treat repeated worker launch failure as an operations-owned recovery case instead of allowing immediate respawn loops.
- `INTAKE-6554ff58` is relevant because the current containment uses the dispatcher complex stop/disable surface and its guarded disable state.
- `INTAKE-37a7892d` is relevant because the safe outcome is a minimal dispatcher quarantine for the unsafe Codex/Windows launch lane, not a replacement bridge runtime.

## Owner Decisions / Input

Owner authorization is `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS`, captured from the 2026-07-07 Prime Builder Codex session. It directs that no visible console windows may spawn on the workstation, with no exception, and authorizes identifying, verifying, and fixing all causes until a 120-consecutive-minute clean interval is achieved.

The resulting bounded PAUTH is `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5052-DISPATCHER-NO-WINDOW-20260707`. It explicitly forbids re-enabling the dispatcher without no-window verification.

## Requirement Sufficiency

Existing requirements are sufficient. The owner directive plus `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, and the bridge and PAUTH governance specs fully define the intended behavior: Windows dispatcher work must not spawn visible console windows, unsafe dispatch lanes may be quiesced through governed controls, and source/config mutation remains bridge-gated.

## Spec-Derived Verification Plan

The implementation report must include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_windows_no_window_spawn_audit.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe scripts/windows_no_window_spawn_audit.py --json
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch complex status --json
```

Expected result: dispatcher runtime tests cover the Windows Codex auto-dispatch no-window/quarantine behavior; the no-window audit remains release-ready with zero release-runtime violations; dispatcher complex status shows either guarded quiesce while unsafe or a re-enabled state only after no-window smoke evidence; no worker path is re-enabled merely because a scheduled task is healthy.

The implementation report must also include monitor evidence from a Windows visible-window probe showing no visible `WindowsTerminal`, `OpenConsole`, `powershell`, `pwsh`, `cmd`, `conhost`, or Codex-worker console surfaces during the post-fix validation window. If a bounded dispatcher smoke is attempted, it must run under that probe and must fail closed on any visible console window.

## Risk / Rollback

Main risk: keeping dispatcher auto-processing quiesced delays automatic bridge review/verification. That risk is lower than allowing repeated focus-stealing console windows. A second risk is over-broad Codex quarantine reducing dispatch capacity; implementation should prefer the narrowest Windows/Codex unsafe-lane guard that prevents visible windows.

Rollback is a single source/config commit revert, but the guarded dispatcher disable must remain active if any visible console window recurs after rollback or re-enable.

## Bridge Filing

This proposal is filed in the bridge directory as the next status-bearing numbered
bridge file for `gtkb-wi5052-dispatcher-codex-no-window-containment`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — this is a defect repair for a workstation-visible dispatcher/Codex auto-dispatch window-spawn failure.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
