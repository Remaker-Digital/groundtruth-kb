NEW

# gtkb-dispatcher-complex-watchdog-cli-parity — Slice 1: Storm watchdog governed CLI parity

bridge_kind: prime_proposal
Document: gtkb-dispatcher-complex-watchdog-cli-parity
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-07-05 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f128ea1d-e645-49bf-93a5-72661ec0d0c7
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5023

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/install_storm_watchdog_task.ps1", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py", "platform_tests/scripts/test_dispatcher_watchdog_control.py"]

implementation_scope: code
requires_review: true
requires_verification: true

## Summary

Slice 1 of PROJECT-GTKB-DISPATCHER-COMPLEX-CLI (ADR-DISPATCHER-COMPLEX-CLI-001). The storm watchdog (GTKB-HarnessStormWatchdog scheduled task) is the only member of the dispatcher daemon complex with no governed `gt` CLI — it is managed only via raw Task Scheduler. This slice adds governed watchdog CLI parity so the watchdog can be driven the same way as the supervisor, which is the load-bearing prerequisite for the later `complex` group (slice 2) and the `health` rollup (slice 3).

Deliverables:
1. A governed watchdog-control API (`dispatcher_watchdog.py`) paralleling `dispatcher_supervisor.py`: `collect_watchdog_status`, `install_watchdog`, `enable_watchdog`, `disable_watchdog`, `uninstall_watchdog`, plus a `DispatcherWatchdogError` type.
2. A `gt bridge dispatch daemon watchdog {status, install, enable, disable, uninstall}` command group in `cli.py`, mirroring the existing `daemon supervisor` group.
3. A doctor watchdog-task check in `doctor.py` that reports GTKB-HarnessStormWatchdog registration/enabled/hidden/uses-pythonw health (structurally identical to the supervisor check).
4. Governed install of the watchdog task via a PowerShell installer paralleling `install_dispatcher_daemon_task.ps1`.

Runtime isolation is preserved: this adds a governed control surface for the watchdog task only; it does not merge the watchdog with the supervisor or daemon (ADR-DISPATCHER-ARCHITECTURE-001 fault isolation).

## Specification Links

- SPEC-INTAKE-5e9375 — the requirement this project implements (harmonized complex CLI + complex health).
- ADR-DISPATCHER-COMPLEX-CLI-001 — the architecture decision; decision 2 (watchdog CLI parity) and the fault-isolation constraint govern this slice.
- ADR-DISPATCHER-ARCHITECTURE-001 — the persistent-daemon / harness-isolation architecture; the watchdog and supervisor remain deliberately-separate runtime tasks.
- DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001 — the supervision contract the watchdog complements.
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 — the centralized dispatch service.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites all governing specs.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — satisfied by the Project + Work Item header lines above.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps tests to the slice deliverables.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — the doctor.py and package changes stay under groundtruth-kb/src/groundtruth_kb/ (platform placement).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact-oriented governance (advisory).

## Prior Deliberations

- INTAKE-6554ff58 — the requirement candidate captured for this project.
- DELIB-202665470 — the dispatch resume decision whose investigation surfaced the watchdog CLI gap.
- Owner design grill (this session, via AskUserQuestion) that settled CLI shape = complex rollup + watchdog parity.
- ADR-DISPATCHER-ARCHITECTURE-001 daemon-resilience lineage (DELIB-20266276) established the watchdog as a separate resilience task.

## Requirement Sufficiency

Existing requirements sufficient. SPEC-INTAKE-5e9375 and ADR-DISPATCHER-COMPLEX-CLI-001 (decision 2) define the watchdog-parity requirement and the fault-isolation constraint. No new requirement is required before implementation.

## Specification-Derived Verification Plan

| Specification / Acceptance clause | Test / verification |
| --- | --- |
| ADR-DISPATCHER-COMPLEX-CLI-001 decision 2 (watchdog CLI parity) | `test_bridge_dispatch_daemon_watchdog.py`: asserts the `gt bridge dispatch daemon watchdog {status,install,enable,disable,uninstall}` verbs exist and dispatch to the control API; parity with the supervisor group's command set. |
| Watchdog-control API | `test_dispatcher_watchdog_control.py`: unit tests for install/enable/disable/uninstall/status against a nonce-suffixed task (mirrors test_dispatcher_daemon_supervision.py). |
| Doctor watchdog check | doctor test asserts the GTKB-HarnessStormWatchdog check reports registered/enabled/hidden/uses-pythonw. |
| Fault-isolation constraint (ADR-DISPATCHER-ARCHITECTURE-001) | assert the watchdog control path does not touch the supervisor/daemon task or the daemon lock. |
| Code quality | `ruff check` and `ruff format --check` on changed Python files. |

Commands: `pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py platform_tests/scripts/test_dispatcher_watchdog_control.py -q`; `ruff check <changed.py>`; `ruff format --check <changed.py>`; `gt bridge dispatch daemon watchdog status --json`.

## Owner Decisions / Input

- Owner approved ADR-DISPATCHER-COMPLEX-CLI-001 and the 4-slice project via AskUserQuestion (this session): "Approve — land it all".
- Owner settled the design (CLI shape = complex rollup + watchdog parity) via the design-grill AskUserQuestion (this session).
- No further owner decision is required to review this slice-1 proposal.

## Risk / Rollback

Risk: the watchdog installer/control could misconfigure the task (wrong launcher, console flash). Mitigation: mirror the VERIFIED supervisor installer (pythonw, hidden) and the WI-4896 console-residual fix; the doctor check asserts uses-pythonw. Rollback: `gt bridge dispatch daemon watchdog uninstall` (new) or leaving the pre-existing Task Scheduler management in place; no runtime merge is performed, so the daemon and supervisor are unaffected.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-dispatcher-complex-watchdog-cli-parity` (`bridge/gtkb-dispatcher-complex-watchdog-cli-parity-001.md`); no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered bridge files are the canonical workflow state per GOV-FILE-BRIDGE-AUTHORITY-001.

## Recommended Commit Type

feat(dispatch) — net-new governed watchdog control API + CLI group + doctor check.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
