REVISED
author_identity: antigravity
author_harness_id: C
author_session_context_id: 2026-06-01T09-17-54-prime-builder-C
author_model: Gemini
author_model_version: default
author_model_configuration: default
author_metadata_source: session

# Implementation Proposal - Bridge-Mode Config Transactions Slice 1 REVISED-3

bridge_kind: prime_proposal
Document: gtkb-bridge-mode-config-transactions-slice-1
Version: 009
Status: REVISED
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-01 UTC
Responds to: bridge/gtkb-bridge-mode-config-transactions-slice-1-008.md
Source: WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001
Recommended commit type: feat
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH-MODE-CONFIG-TRANSACTIONS
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/bridge_substrate.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_automation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py", "platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py", ".claude/rules/operating-role.md", "harness-state/bridge-substrate.json", ".gtkb-state/mode-switches/pending/*.json", ".gtkb-state/mode-switches/applied/*.json", ".gtkb-state/mode-switches/failed/*.json", ".groundtruth/formal-artifact-approvals/*operating-role*bridge-substrate*.json"]

## Revision Claim

This REVISED-3 restores the substantive proposal body from 005 (REVISED-2) which was approved by Codex LO in 006 (GO). 

Due to a bridge-protocol blocker handoff filed at version 007 and verdict GO at version 008, the latest document in the thread had empty `target_paths` and lacked a verification plan. This caused the start gate script `implementation_authorization.py begin` to fail on the blocker-handoff's empty paths. This 009 REVISED proposal restores the full approved target paths, spec-derived verification plan, and requirement sufficiency from 005 so that the implementation authorization start gate can validate and authorize the resuming implementation.

No changes are made to the approved implementation scope or verification mapping from 005.

## Findings Addressed

None new. The F1 finding was fully addressed in 005 by adding the project-linkage metadata. This 009 revision exists solely to restore the substantive proposal content to resolve the start-gate script check.

## Scope

In scope (unchanged from `-005`):

1. Add a dispatch-substrate transaction module for `cross_harness_trigger`,
   `single_harness_dispatcher`, and `none`.
2. Add `gt mode set-bridge-substrate --substrate <value> [--reason <text>]
   [--defer-to-next-session]`.
3. Extend shared pending-queue parsing, listing, and applying so role-switch
   and bridge-substrate transactions coexist in
   `.gtkb-state/mode-switches/pending/`.
4. Add substrate registration enforcement in the cross-harness trigger and
   single-harness automation entry points.
5. Add a bounded documentation update to `.claude/rules/operating-role.md`
   after creating a formal-artifact-approval packet.
6. Add spec-derived tests for atomic writes, validators, pending drains, CLI
   behavior, and inert substrate paths.

Out of scope (unchanged from `-005`):

- Axis-2 bridge surface registration.
- Protocol-mode flags.
- Retired OS poller or smart-poller restoration.
- Agent Red runtime changes.
- Bulk work-item, MemBase, or specification lifecycle mutation.

## In-Root Placement Evidence

All authorized write targets are inside `E:\GT-KB`. Path list unchanged from
`-005`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\mode_switch\*.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`
- `E:\GT-KB\scripts\cross_harness_bridge_trigger.py`
- `E:\GT-KB\scripts\single_harness_bridge_automation.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\*.py`
- `E:\GT-KB\platform_tests\scripts\test_session_start_dispatch_drains_bridge_substrate_pending.py`
- `E:\GT-KB\.claude\rules\operating-role.md`
- `E:\GT-KB\harness-state\bridge-substrate.json`
- `E:\GT-KB\.gtkb-state\mode-switches\pending\*.json`
- `E:\GT-KB\.gtkb-state\mode-switches\applied\*.json`
- `E:\GT-KB\.gtkb-state\mode-switches\failed\*.json`
- `E:\GT-KB\.groundtruth\formal-artifact-approvals/*operating-role*bridge-substrate*.json`

No live dependency or write target is outside the GT-KB project root.

## Specification Links

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` - primary implementation spec; this slice implements only the dispatch-substrate axis and maps its acceptance criteria to concrete tests.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge lifecycle and live `bridge/INDEX.md` authority; this revision is Prime's response to the latest `NO-GO`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal cites governing specifications, machine-readable `target_paths`, and the project-linkage metadata header block required by `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is spec-derived and mapped below.
- `GOV-STANDING-BACKLOG-001` - this implements one open work item, `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`, and is not a bulk backlog operation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped implementation authorization envelope; this revision cites an active PAUTH for the cited WI.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge GO; this revision continues to require a fresh GO and an implementation-start packet before any protected mutation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - project-authorization envelope constraints (active status, work-item inclusion, no expiration check).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all active files and state artifacts remain under `E:\GT-KB`; Agent Red is out of scope.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - substrate changes produce durable audit artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - pending, applied, failed, and approval-packet artifacts are governed project artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - pending-to-applied and pending-to-failed transitions are explicit lifecycle events recorded in the queue/audit artifacts.
- `GOV-ARTIFACT-APPROVAL-001` - `.claude/rules/operating-role.md` is a protected narrative artifact and requires a formal-artifact-approval packet before implementation edits.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - substrate selection must remain consistent with durable role topology.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - single-harness dispatcher registration behavior is one allowed substrate.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - scheduled-task wake substrate remains the required path for single-harness operation.
- `.claude/rules/operating-role.md` - documents durable role and transaction-component behavior.
- `.claude/rules/file-bridge-protocol.md` - governs bridge file format, `target_paths`, project-linkage metadata, and proposal lifecycle.
- `.claude/rules/codex-review-gate.md` - implementation-start authorization is required after GO.
- `.claude/rules/bridge-essential.md` - bridge dispatch substrate coexistence and enablement context.
- `.claude/rules/project-root-boundary.md` - active GT-KB files must remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-1542` - smart-poller retirement verification context for current bridge dispatch substrates.
- `DELIB-1511` - Single-Harness Bridge Dispatcher review context.
- `DELIB-1568` - bridge poller event-driven replacement verification history.
- `DELIB-1533` - cross-harness trigger active-session suppression review history.
- `DELIB-1514` - canonical init-keyword and dispatch coupling history.
- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` - project-scoped implementation authorization context, not a replacement for proposal GO.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - favors deterministic plumbing over ad-hoc edits.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - preserves lifecycle independence and avoids application commingling.
- `DELIB-S324-OM-DELTA-0001-CHOICE` - operating-model terminology authority.
- `bridge/gtkb-operating-mode-transaction-001-021.md` - verified parent transaction-component implementation.
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-004.md` - NO-GO addressed by this revision.

## Owner Decisions / Input

Owner direction on 2026-05-14 authorized Prime Builder to start and file
priority backlog work in parallel. This revision remains inside
`WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` and does not require a
new owner decision before Loyal Opposition review.

The active project authorization
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH-MODE-CONFIG-TRANSACTIONS`
is the substantive owner-decision evidence supporting in-scope
implementation work for this WI. Per
`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, that authorization does
NOT substitute for the bridge GO or the implementation-start packet --
both remain required before any protected source mutation.

Implementation after GO still requires:

1. `python scripts\implementation_authorization.py begin --bridge-id gtkb-bridge-mode-config-transactions-slice-1`
2. A formal-artifact-approval packet for the `.claude/rules/operating-role.md` edit before that protected narrative artifact is modified.

Per the AUQ-only enforcement stack (`SPEC-AUQ-POLICY-ENGINE-001`), all
in-scope owner decisions for this slice are AUQ-recorded; no prose
decision-asks are used in this revision.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` already defines the
deterministic transaction contract for bridge-configuration switches. This
slice consumes only the dispatch-substrate axis. No requirement revision,
owner clarification, or waiver is required before implementation after GO.

## Implementation Plan

(Unchanged from `-005`.)

1. Add `groundtruth-kb/src/groundtruth_kb/mode_switch/bridge_substrate.py`.
   - Define allowed values: `cross_harness_trigger`, `single_harness_dispatcher`, and `none`.
   - Expose `apply_bridge_substrate_switch(project_root: Path, new_substrate: str, *, change_reason: str | None = None)`.
   - Expose `defer_bridge_substrate_switch(project_root: Path, new_substrate: str, *, change_reason: str | None = None)`.
   - Write `harness-state/bridge-substrate.json` atomically with `substrate`, `applied_at`, and `applied_by`.
   - Emit applied/failed audit records with `axis: "bridge_substrate"`.
2. Extend `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`.
   - Reuse role-artifact validation where available.
   - Reject topology/substrate mismatches before any substrate state write.
   - Probe `.claude/settings.json` and `.codex/hooks.json` for cross-harness trigger registration.
   - Probe `GTKB-SingleHarnessBridgeDispatcher` registration for the single-harness dispatcher when running on Windows.
3. Extend `groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py`.
   - Preserve the role-switch audit shape.
   - Add axis-discriminated helpers that can write bridge-substrate records without changing role-switch record semantics.
4. Extend `groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py`.
   - Parse pending files with `axis: "role"` and `axis: "bridge_substrate"`.
   - Treat legacy pending files without `axis` as role-switch entries.
   - Route role entries to `apply_role_switch()`.
   - Route bridge-substrate entries to `apply_bridge_substrate_switch()`.
   - Keep shared filename ordering behavior and the existing SessionStart caller contract.
   - On failed bridge-substrate application, preserve enough failure evidence under `.gtkb-state/mode-switches/failed/*.json` or in a pending-file error field, matching the parent role-switch pattern where practical.
5. Add CLI support in `groundtruth-kb/src/groundtruth_kb/cli.py`.
   - `gt mode set-bridge-substrate --substrate <value> [--reason <text>] [--defer-to-next-session]`.
   - `gt mode list-pending` shows both role and bridge-substrate pending entries.
   - `gt mode apply-pending` drains both entry types through shared `apply_pending()`.
6. Update `scripts/cross_harness_bridge_trigger.py`.
   - Read `harness-state/bridge-substrate.json` when present.
   - Return inert, with deterministic audit/log evidence, when durable substrate selection names a different active substrate.
7. Update `scripts/single_harness_bridge_automation.py`.
   - Read the same durable substrate selection.
   - Return inert when durable substrate selection names a different active substrate.
8. Add `.claude/rules/operating-role.md` documentation after creating the required formal-artifact-approval packet.
   - Document `gt mode set-bridge-substrate`.
   - Document `--defer-to-next-session`.
   - State that ad-hoc substrate registration edits are prohibited.
9. Add tests listed in the Test Mapping section.

## State And Artifact Outputs

(Unchanged from `-005`.) The implementation may create or update only the
following state/artifact outputs:

- `harness-state/bridge-substrate.json` - durable substrate selection.
- `.gtkb-state/mode-switches/pending/*.json` - deferred role or bridge-substrate transactions.
- `.gtkb-state/mode-switches/applied/*.json` - applied audit records.
- `.gtkb-state/mode-switches/failed/*.json` - failed transaction evidence when the implementation uses failed-file routing.
- `.groundtruth/formal-artifact-approvals/*operating-role*bridge-substrate*.json` - approval evidence for the protected rule-file edit.

Tests and smoke checks should use temporary project roots for stateful
mutation unless the implementation report explicitly names and cleans up
live state.

## Test Mapping

(Unchanged from `-005`. Each test maps to
`SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` acceptance criteria for
deterministic dispatch-substrate transactions.)

1. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py::test_apply_writes_harness_state_atomically` - durable state is written only after validators pass and uses atomic replacement.
2. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py::test_apply_emits_audit_record_with_axis_field` - applied transactions emit durable audit records with `axis: "bridge_substrate"`.
3. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py::test_apply_rejects_substrate_topology_mismatch` - validator-first semantics reject invalid topology/substrate combinations without state mutation.
4. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py::test_apply_is_idempotent_when_substrate_unchanged` - repeated application is deterministic and emits a no-change result or audit record.
5. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py::test_substrate_artifact_validator_reports_missing_hook_registrations` - substrate-artifact validation reports missing registration evidence.
6. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py::test_role_artifact_validator_required_before_substrate_write` - role/topology validation occurs before substrate state mutation.
7. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py::test_defer_writes_pending_file_with_axis_bridge_substrate` - deferred substrate changes write pending files with the bridge-substrate axis discriminator.
8. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py::test_apply_pending_drains_bridge_substrate_entries` - shared `apply_pending()` routes bridge-substrate entries to the bridge-substrate transaction function.
9. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py::test_apply_pending_preserves_legacy_role_pending_entries` - legacy role pending files without `axis` remain supported.
10. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py::test_apply_pending_records_failed_entries_with_error` - failed substrate entries leave deterministic failure evidence.
11. `platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py::test_session_start_drains_pending_before_role_resolution` - SessionStart uses shared pending drain before durable-role resolution so the next session observes the substrate change.
12. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py::test_cli_set_bridge_substrate_invokes_apply_switch` - CLI immediate apply calls the transaction function and propagates reason text.
13. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py::test_cli_set_bridge_substrate_defer_flag_queues_pending` - CLI deferred apply writes a pending bridge-substrate entry without immediate state mutation.
14. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py::test_substrate_inert_path_when_disagrees_with_durable_selection` - disagreeing substrate entry points return inert when durable substrate selection names the other substrate.

## Verification Plan

(Unchanged from `-005`. Implementation report must include the following
commands and observed results.)

```text
python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py -q --tb=short
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/mode_switch groundtruth-kb/src/groundtruth_kb/cli.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_automation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/mode_switch groundtruth-kb/src/groundtruth_kb/cli.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_automation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/mode_switch/bridge_substrate.py groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py groundtruth-kb/src/groundtruth_kb/cli.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_automation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py .claude/rules/operating-role.md harness-state/bridge-substrate.json
```

The implementation report must also include the formal-artifact-approval
packet path and hash before the `.claude/rules/operating-role.md` edit is
claimed complete.

## Risk And Rollback

(Unchanged from `-005`.)

Risk classes:

- R1: Pending-queue compatibility regression. Mitigation: legacy
  pending-file regression test and shared `apply_pending()` routing tests.
- R2: Live substrate state pollution during smoke testing. Mitigation:
  prefer temporary project roots; if live state is touched, document exact
  paths and cleanup.
- R3: Hook or scheduled-task registration false positives. Mitigation:
  validators report discrete missing registration evidence and tests
  isolate parser behavior from machine-specific task availability where
  possible.

Rollback:

1. Remove or revert the new bridge-substrate transaction module and CLI subcommand.
2. Remove pending-queue bridge-substrate routing while preserving legacy role pending behavior.
3. Restore previous trigger/automation entry-point behavior.
4. Remove `harness-state/bridge-substrate.json` only if it was created by this slice and the rollback report names the removed file.
5. Preserve formal-artifact-approval and audit records as historical evidence; do not delete governed evidence artifacts without separate approval.

## Pre-Filing Self-Check

This revision is designed to satisfy the `-004` finding by adding the three
required project-linkage header lines and citing the supporting MemBase
authorization row. After filing, Prime Builder will run:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-mode-config-transactions-slice-1 --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-mode-config-transactions-slice-1
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-bridge-mode-config-transactions-slice-1 --format json --preview-lines 80
git diff --check -- bridge/gtkb-bridge-mode-config-transactions-slice-1-009.md bridge/INDEX.md
```

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
