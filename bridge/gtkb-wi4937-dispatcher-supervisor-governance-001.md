NEW

# gtkb-wi4937-dispatcher-supervisor-governance — Govern headless Windows dispatcher supervisor CLI and doctor checks

bridge_kind: prime_proposal
Document: gtkb-wi4937-dispatcher-supervisor-governance
Version: 001
Author: Prime Builder Cursor
Date: 2026-06-30T20:00:00Z

author_identity: Cursor Prime Builder
author_harness_id: E
author_session_context_id: cursor-e-s520-wi4937-impl
author_model: Composer
author_model_version: 2.5
author_model_configuration: Cursor interactive; session role Prime Builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4937-SUPERVISOR-GOVERNANCE
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4937

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/install_dispatcher_daemon_task.ps1", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "groundtruth-kb/docs/method/12-file-bridge-automation.md"]

implementation_scope: source,test,docs
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4882 delivered the headless Windows supervisor scripts (`scripts/install_dispatcher_daemon_task.ps1`, `scripts/ensure_dispatcher_daemon.py`) but left installation as a manual PowerShell-only path. On the live host the `GTKB-DispatcherDaemon` scheduled task is registered yet **Disabled**, while agents still treat `gt bridge dispatch daemon start` from transient IDE shells as the primary persistence mechanism. The doctor checks daemon heartbeat but not supervisor registration/enabled state.

This proposal wires supervisor install/enable/status into governed `gt bridge dispatch daemon supervisor` CLI commands, adds a doctor WARN when the `dispatcher_daemon` substrate lacks a healthy supervisor, enables the task at install time, documents the production vs diagnostic-fallback operator contract, and deprecates IDE-shell `daemon start` as the production path.

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — Windows dispatcher/background paths must run headlessly without visible consoles; supervisor uses `pythonw.exe` and hidden Task Scheduler settings.
- `ADR-DISPATCHER-ARCHITECTURE-001` — The dispatcher daemon is the reliability boundary; supervisor governance makes that boundary survive IDE/terminal closure.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — All repair targets remain in-root under the GT-KB platform tree.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — Dispatch service lifecycle belongs in governed platform tooling, not tribal PowerShell knowledge.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — Protected `groundtruth-kb/src/`, `scripts/`, and `platform_tests/` edits require bridge proposal, LO GO, implementation claim, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Governing specs cited above for the source/test/doc changes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization, Project, Work Item, and concrete target paths are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Implementation report maps behavior to executed pytest targets.
- `GOV-STANDING-BACKLOG-001` — WI-4937 is the active defect work item for supervisor governance.

## Prior Deliberations

- `DELIB-20266276` — Daemon resilience scope-lock (D3 dedicated idempotent ensure-alive supervisor) and program authorization source for `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION`.
- `bridge/gtkb-wi4882-dispatcher-daemon-supervision-001.md` (and successors) — Original WI-4882 supervisor delivery; manual PS1 install path only.
- S520 owner investigation — Dispatcher daemon does not persist across IDE/terminal closure when supervisor task is disabled; owner requested permanent governed fix.

## Owner Decisions / Input

No new owner decision is required. Mike directed Prime Builder to investigate dispatcher persistence (S520) and to continue implementation of WI-4937 under the dispatcher reliability program. The work item acceptance criteria are already captured in MemBase backlog `WI-4937`.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and WI-4937 acceptance criteria already require headless unattended daemon supervision on Windows. No new specification is needed before implementation.

## Spec-Derived Verification Plan

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_daemon_supervision.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py
```

Expected: all tests PASS; doctor emits supervisor WARN when task disabled on Windows `dispatcher_daemon` substrate; `gt bridge dispatch daemon supervisor status --json` reports `healthy` after `supervisor install`.

## Implementation Plan

1. Add `groundtruth_kb.dispatcher_supervisor` module wrapping install/uninstall PS1 scripts and PowerShell task probes.
2. Add `gt bridge dispatch daemon supervisor {status,install,enable,disable,uninstall}` CLI subgroup.
3. Update `daemon start` docstring to mark diagnostic-fallback-only semantics.
4. Call `Enable-ScheduledTask` in `install_dispatcher_daemon_task.ps1` after registration.
5. Add `_check_dispatcher_daemon_supervisor_task` doctor WARN for unhealthy/missing supervisor on Windows.
6. Extend WI-4882 supervision tests and add CLI unit tests.
7. Document production vs fallback operator contract in `groundtruth-kb/docs/method/12-file-bridge-automation.md`.

## Risk / Rollback

Risk is low: changes are additive CLI/doctor surfaces atop existing WI-4882 scripts. Rollback is a single revert commit; uninstall remains available via `gt bridge dispatch daemon supervisor uninstall`.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4937-dispatcher-supervisor-governance`; no prior version is deleted or rewritten (append-only).

## Recommended Commit Type

fix — closes supervisor governance gap (WI-4937 defect) without changing dispatch topology.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
