NEW

# gtkb-wi4924-daemon-recipient-state-migration-dedup-repair - Prevent daemon duplicate spawns from unsuffixed inert-state migration

bridge_kind: prime_proposal
Document: gtkb-wi4924-daemon-recipient-state-migration-dedup-repair
Version: 001
Author: Codex Prime Builder
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop interactive session; Prime Builder; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4924-DAEMON-DEDUP-MIGRATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4924

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the release-blocking duplicate-spawn path observed after restarting `dispatcher_daemon` on 2026-06-29. The daemon launched repeated Codex Prime Builder workers for the same two selected bridge entries on successive ticks, even though the recipient state had just recorded the selected batch signature.

Canonical runtime evidence shows the cause. While the daemon substrate is active, dispatched Codex workers still run the cross-harness trigger hooks. The hook correctly goes inert because `harness-state/bridge-substrate.json` selects `dispatcher_daemon`, but `_record_substrate_mismatch_skip` writes unsuffixed role records (`prime-builder`, `loyal-opposition`) into the shared dispatch-state file. On the next daemon tick, `_load_dispatch_state(..., project_root)` migrates unsuffixed role records to active suffixed recipients. Because `_migrate_recipients_state_keys` currently lets a newer unsuffixed record replace an existing explicit `prime-builder:A` record, the inert placeholder can erase `prime-builder:A.last_dispatched_signature`. The daemon then re-enters `_execute_live_spawns` and launches the same selected batch again.

This proposal authorizes a narrow state-migration guard and regression tests. Explicit recipient-suffixed dispatch state must win over unsuffixed substrate-mismatch placeholders when both map to the same active recipient. The daemon must not spawn a second worker for an unchanged selected signature merely because a newer unsuffixed inert record exists.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected dispatcher source/test changes require this proposal, LO GO, and implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the dispatcher, bridge, and release-readiness requirements constraining the repair.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the work is tied to active project authorization and exact target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map every linked requirement to focused verification evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4924 is the controlling backlog item for this release-blocking dispatcher regression.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the dispatcher daemon must provide centralized, bounded, observable dispatch behavior.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - selected workers must not be relaunched repeatedly for unchanged work while prior work is in flight.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher health/status must reflect stale or saturated runtime state truthfully.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch envelopes and state transitions must remain deterministic and auditable.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher/background paths must avoid visible console-window storms.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` - process cleanup remains bounded to explicit dispatcher worker sidecars; this repair does not broaden kill behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the runtime release blocker is preserved as an append-only bridge artifact rather than scratch diagnosis.

## Prior Deliberations

- `DELIB-20266276` - owner scope-lock for daemon/dispatcher resilience and release-blocking dispatcher hardening.
- `DELIB-20266297` - no visible console-window direction for dispatcher and watchdog operations.
- `bridge/gtkb-wi4893-dispatcher-release-readiness-hardening-001.md` through `-004.md` - prior WI-4893 release-readiness implementation and VERIFIED chain.
- `bridge/gtkb-wi4893-lo-dispatch-readiness-gate-001.md` through `-004.md` - VERIFIED LO dispatch readiness gate repair that exposed the need for truthful runtime health.
- `bridge/gtkb-wi4893-daemon-hook-storm-hardening-001.md` through `-004.md` - VERIFIED daemon hook-storm hardening context.
- `bridge/gtkb-wi4894-develop-release-integration-drift-repair-001.md` through `-004.md` - VERIFIED watchdog output-file repair used to remove a separate console-window storm source.
- `WI-4924` / `TEST-11240` - new gap work item and linked regression test created from the 2026-06-29 runtime evidence.

## Owner Decisions / Input

No new owner decision is required. Mike has made dispatcher release health and harness parity release readiness the active top priority, and `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4924-DAEMON-DEDUP-MIGRATION` authorizes this bounded source/test repair. It does not require credential changes, production deployment, release-branch mutation, or formal requirement changes.

## Requirement Sufficiency

Existing requirements are sufficient. The observed defect is a direct violation of centralized dispatcher boundedness and truthful health: an inert placeholder record must not erase a concrete recipient launch signature, and the daemon must not relaunch unchanged work every tick.

## Proposed Implementation

1. Update dispatch-state recipient migration so explicit suffixed recipient records (for example `prime-builder:A`) are not overwritten by unsuffixed role placeholder records (for example `prime-builder`) when both map to the same active recipient.
2. Preserve legacy migration behavior when no explicit suffixed recipient exists, so older role-level state files still migrate forward.
3. Add a daemon regression test that seeds an explicit `prime-builder:A` launch signature, then adds a newer unsuffixed `prime-builder` substrate-mismatch record, and proves `_execute_live_spawns` returns `unchanged` without calling `_spawn_harness`.
4. Add or adjust cross-harness trigger migration coverage proving explicit suffixed recipient state wins over newer unsuffixed substrate-mismatch placeholder state.
5. After verification, soft-reset stale runtime runs as needed, restart the daemon, and prove a full tick does not duplicate-spawn the same Prime Builder batch.

Out of scope:

- Changing provider eligibility, OpenRouter/Cursor/Ollama behavior, dispatcher ranking, worker prompts, release merge policy, or credential lifecycle.
- Rewriting prior VERIFIED bridge files.
- Deleting unrelated dirty worktree changes.

## Spec-Derived Verification Plan

| Spec / requirement | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | After LO GO, run `scripts/implementation_authorization.py begin` and `validate` for exactly the authorized target paths. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001` | Run focused daemon/cross-harness tests proving an unchanged selected batch is not relaunched when a newer unsuffixed substrate-mismatch record exists. |
| `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run daemon status/health after reset and restart; verify no duplicate same-signature spawn on the next tick, and any remaining WARN findings correspond to real pending/failure state. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Process snapshot after daemon tick must not show repeated duplicate worker bursts for the same selected batch. |
| Python quality gate | Run Ruff check and format check on the changed source/test files. |

Expected commands:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py --project-root E:\GT-KB begin --bridge-id gtkb-wi4924-daemon-recipient-state-migration-dedup-repair --session-id 019f09c9-2db0-7b00-a337-40f998b07e56
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py --project-root E:\GT-KB validate --target scripts/cross_harness_bridge_trigger.py --target platform_tests/scripts/test_gtkb_dispatcher_daemon.py --target platform_tests/scripts/test_cross_harness_bridge_trigger.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch reset --soft --json
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon start
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch daemon status --json
```

## Acceptance Criteria

- [ ] Explicit suffixed recipient state cannot be overwritten by a newer unsuffixed substrate-mismatch placeholder during migration.
- [ ] Legacy unsuffixed state still migrates when no explicit suffixed recipient state exists.
- [ ] The daemon live-spawn path returns `unchanged` and performs no spawn for a same-signature batch under the reproduced mixed-state condition.
- [ ] Focused pytest, Ruff check, and Ruff format check pass for the authorized target paths.
- [ ] Runtime smoke after soft reset and daemon restart shows no repeated same-signature Prime Builder worker bursts across successive ticks.
- [ ] No unrelated source, test, provider, credential, bridge-history, or release-merge files are changed.

## Recommended Commit Type

fix: prevent dispatcher daemon duplicate spawns caused by role-placeholder state migration drift

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
