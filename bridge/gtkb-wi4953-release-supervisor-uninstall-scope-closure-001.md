NEW

# Defect-Fix Proposal - Release supervisor uninstall script scope closure

bridge_kind: prime_proposal
Document: gtkb-wi4953-release-supervisor-uninstall-scope-closure
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-01 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f18fc-3060-7b83-b9ab-297901b013c9
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder session; governed bridge-propose helper

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4953-SUPERVISOR-UNINSTALL
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4953

target_paths: ["scripts/uninstall_dispatcher_daemon_task.ps1", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "bridge/gtkb-wi4953-release-supervisor-uninstall-scope-closure-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The clean release worktree already has the scoped WI-4943 dispatcher supervisor source and tests staged for release-branch reconciliation, but `groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py` defines `UNINSTALL_SCRIPT = "scripts/uninstall_dispatcher_daemon_task.ps1"` and `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py` asserts that uninstall dry-run invokes that script. The script is absent from the clean release worktree and was not included in the WI-4943 target path list.

This proposal creates a narrow scope-closure lane for that missing script only. It does not broaden the release branch merge, does not reopen WI-4937 implementation, does not restore retired poller/hook automation, and does not create any deployment-provider binding. The authorization expires on `2026-07-02T00:00:00Z`; if this is not completed in the current release window, it must be renewed or re-deferred explicitly.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - the supervisor CLI uninstall path must point at an in-root script that exists on the release branch.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher lifecycle tooling must remain daemon-owned, bounded, and operational without restoring retired trigger or poller paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher supervisor persistence belongs to the dispatcher daemon substrate, not to transient IDE shells or hook-driven automation.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher persistence and removal must remain headless and task-scheduler based.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal, LO GO, implementation-start authorization, implementation report, and LO verification are required before the protected `scripts/` target is committed.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specs and maps them to verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, Work Item, and parseable `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry forward each linked specification and executed evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4953-SUPERVISOR-UNINSTALL` bounds this work item, expiry, allowed mutation classes, and forbidden operations.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must fail closed if the diff expands beyond the PAUTH and target paths.
- `GOV-STANDING-BACKLOG-001` - WI-4953 is the durable backlog authority for this release-scope closure defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decision, WI, PAUTH, proposal, implementation report, and verdict preserve the release decision trail.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the release gap is being handled through durable artifact linkage instead of scratch-state assumptions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the authorization carries an explicit expiry so the deferral/scope closure cannot decay indefinitely.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live artifacts remain inside `E:/GT-KB`; no Agent Red or external application repository participates in this scope.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-SUPERVISOR-UNINSTALL-AUTH` - owner authorized this scoped WI/PAUTH after the clean release worktree showed the uninstall script gap.
- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorized the parent WI-4943 release-branch dispatcher substrate reconciliation.
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md` - terminal VERIFIED evidence for dispatcher supervisor governance and headless scheduled-task behavior.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-002.md` - GO verdict for the clean release-branch dispatcher substrate reconciliation that surfaced this omitted path.
- `bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-003.md` - current adjacent implementation report awaiting LO verification for the release dispatcher LO dispatch unblock lane.

## Owner Decisions / Input

- `DELIB-20260701-ADHOC-RELEASE-SUPERVISOR-UNINSTALL-AUTH` captures the owner directive: "Authorize new scoped WI/PAUTH." The recorded scope is limited to `scripts/uninstall_dispatcher_daemon_task.ps1` and immediate bridge/test/evidence needed to make the clean release branch dispatcher supervisor substrate internally complete.
- PAUTH expiry is `2026-07-02T00:00:00Z`. If this scope is not completed by then, it must be renewed or explicitly re-deferred with a new trigger or time limit.

## Requirement Sufficiency

Existing requirements sufficient. The governing dispatcher-control, centralized-dispatch-service, dispatcher-architecture, Windows headless supervisor, project-authorization, bridge-authority, and spec-derived verification requirements already define the required behavior and evidence. No new or revised specification is needed before this scope-closure implementation.

## Spec-Derived Verification Plan

| Specification / Clause | Verification command or evidence | Expected result |
| --- | --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py -q --tb=short --no-header` from the clean release worktree | PASS; uninstall dry-run still invokes `scripts/uninstall_dispatcher_daemon_task.ps1`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Inspect `scripts/uninstall_dispatcher_daemon_task.ps1` and supervisor CLI behavior | The script removes only the `GTKB-DispatcherDaemon` scheduled task and does not restore retired trigger/poller/hook automation. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Focused test plus code inspection of `groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py` | Supervisor lifecycle remains under the dispatcher daemon substrate and scheduled-task controls. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Script inspection and dry-run behavior | Windows task uninstall path is headless PowerShell/task-scheduler based and does not open an interactive console requirement. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge proposal, GO, implementation-start packet, report, and VERIFIED chain | All protected-file mutation is backed by numbered bridge state and active PAUTH. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table forward with observed command results | LO can verify without guessing which requirement each command covers. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Compare `git diff --name-only` against `target_paths` and PAUTH scope | Only the uninstall script, scoped bridge file(s), and any justified immediate test evidence are included. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | PAUTH record and proposal Owner Decisions section | Expiry is explicit: `2026-07-02T00:00:00Z`. |

## Risk / Rollback

Risk is low but release-blocking: omitting the script leaves the release branch with a supervisor CLI path that references a non-existent file, while adding unrelated dispatcher work would violate release hygiene. Rollback is to remove the single added script and the WI-4953 bridge/report commit from the release branch before merge; no database migration, credential change, production deployment, or external provider state is involved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4953-release-supervisor-uninstall-scope-closure`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

Recommended commit type: `fix(dispatch):` because the diff closes a missing-file defect in the dispatcher supervisor release substrate.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
