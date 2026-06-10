NEW

# Bridge-Mode Config Transactions - Slice 1 (Dispatch-Substrate Registration Transaction)

bridge_kind: prime_proposal
Document: gtkb-bridge-mode-config-transactions-slice-1
Version: 001
Author: Claude Code (harness B, Prime Builder)
Date: 2026-05-14 UTC
Session: S350
Source: WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001
Recommended commit type: feat

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/bridge_substrate.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_automation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py", "platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py", ".claude/rules/operating-role.md"]

## Summary

WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 directs Prime Builder to extend the deterministic transaction component (introduced for role/topology switches in the VERIFIED parent thread `bridge/gtkb-operating-mode-transaction-001-021.md`) to also cover bridge-configuration switches. The parent slice covered the role axis (`gt mode set-role`); this Slice 1 covers the first of the bridge-configuration axes: dispatch-substrate registration. After this slice, an agent that needs to change which bridge dispatch substrate is registered for the current install (cross-harness event-driven trigger versus single-harness dispatcher scheduled task) MUST route the request through `gt mode set-bridge-substrate` instead of ad-hoc edits to `.claude/settings.json`, `.codex/hooks.json`, or the `GTKB-SingleHarnessBridgeDispatcher` Windows scheduled task. The substrate-axis transaction reuses the parent slice's pre-write validator pattern, atomic write discipline, audit-record format, deferred-to-next-session queue, and `apply_pending` SessionStart drain. Subsequent slices (out of scope here) will extend the same transaction component to axis-2 surface registration (per `.claude/rules/bridge-essential.md` § Axis 2) and protocol-mode flags. No changes to formal artifact approval, bridge `GO`, or implementation-start authorization are introduced.

## Specification Links

- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 - primary spec being implemented; defines the deterministic transaction contract for bridge-configuration and operating-mode switch requests. Tests in this slice are derived directly from its acceptance criteria for the dispatch-substrate axis.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol authority; this proposal follows the standard NEW -> GO -> implement -> VERIFIED lifecycle and writes nothing to `bridge/INDEX.md` until Codex review and owner authorization.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this Specification Links section is mandatory and lists every cross-cutting spec the proposal touches.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Test Mapping section maps each acceptance criterion in the dispatch-substrate-axis subset of SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 to a concrete spec-derived test.
- GOV-STANDING-BACKLOG-001 - standing-backlog source-of-truth; this proposal implements one open WI from MemBase `work_items` and does not perform bulk operations on individual work items.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target_paths are within `E:\GT-KB`; no Agent Red commingling and no out-of-root dependencies.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the bridge-substrate transaction emits a durable audit-record artifact `applied/<timestamp>-<uuid>.json` so substrate changes are traceable across artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - audit records are governed artifacts; the bridge-substrate axis uses the same audit-trail directory pattern (`.gtkb-state/mode-switches/`) as the role-switch axis.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the pending-to-applied transition (queue file moves from `pending/` to `applied/` on success) is an explicit lifecycle trigger captured in the audit record.
- GOV-ARTIFACT-APPROVAL-001 - the only protected narrative-artifact edit in this slice is to `.claude/rules/operating-role.md` (the mode-switch transaction component section), which requires a formal-artifact-approval packet at implementation time.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - dispatch substrate is determined by role-set topology; this slice does NOT change topology semantics, only formalizes substrate registration as a transaction surface.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the single-harness dispatcher contract is referenced; this slice does not alter the dispatcher's runtime behavior, only how its scheduled-task registration is configured.
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - wake-substrate constraint; the substrate-axis transaction preserves the Windows-scheduled-task path for single-harness installs.
- `.claude/rules/operating-role.md` - canonical durable-role authority and current site of the mode-switch transaction component documentation; receives a new subsection for the bridge-substrate axis.
- `.claude/rules/file-bridge-protocol.md` - bridge file naming, mandatory subsections, and status vocabulary.
- `.claude/rules/codex-review-gate.md` - review gate and implementation-start authorization contract.
- `.claude/rules/bridge-essential.md` - operational mode and dual-substrate coexistence section; the bridge-substrate axis transaction targets the registration boundary described there.
- `.claude/rules/project-root-boundary.md` - root boundary; every target_paths entry is in-root.

## Prior Deliberations

- DELIB-1542 (VERIFIED parent thread bridge-poller event-driven replacement Slice 4) - smart-poller retirement context for current substrate choices.
- DELIB-1511 (Loyal Opposition Review - Single-Harness Bridge Dispatcher) - prior single-harness-substrate review context.
- DELIB-1568 (Loyal Opposition Verification - Bridge Poller Event-Driven Replacement Slice 1 + 2) - cross-harness trigger substrate verification history.
- DELIB-1533 (Loyal Opposition Review - Cross-Harness Trigger Active-Session Suppression REVISED-2 GO) - dispatch-state contract relevant to substrate registration.
- DELIB-1514 (Loyal Opposition Review - Canonical Init-Keyword Syntax REVISED-1) - init-keyword and substrate-dispatch coupling history.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION - project-scoped implementation authorization envelope, additive to per-proposal bridge GO.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - validator design tightens deterministic plumbing; the bridge-substrate axis follows this principle by replacing ad-hoc multi-file edits with one CLI surface.
- DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT - lifecycle-independence contract; the substrate-axis transaction respects single-application lifecycle semantics.
- DELIB-S324-OM-DELTA-0001-CHOICE - operating-model canonical authority for terminology used in this proposal.
- `bridge/gtkb-operating-mode-transaction-001-021.md` (VERIFIED) - parent transaction-component slice; this Slice 1 reuses its validator + atomic-write + audit-record + pending-queue pattern verbatim. Citation is the architectural anchor for "do not invent a new pattern".
- `bridge/gtkb-operating-mode-transaction-001-016.md` - parent approved proposal showing the implementation pattern this slice extends.

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" + "Please continue filing more backlog work" authorizes batch NEW filing of priority backlog proposals. Per-proposal Codex GO is still required before implementation. Channel: AskUserQuestion (DECISION-0583 - the AUQ-resolved batch authorization for proceeding with priority backlog filing this session).

No additional owner decision is required before Codex review of this proposal. Implementation gate items (formal-artifact-approval packet for the `.claude/rules/operating-role.md` edit; implementation-start authorization packet from the eventual GO) will be obtained at implementation time, not at proposal-filing time.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation on individual work items, MemBase rows, or the standing backlog. It implements one open priority backlog WI (`WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`) by adding one new transaction module, one new CLI subcommand, and one paragraph-scale documentation update to `.claude/rules/operating-role.md`. The implementation produces an inventory of one new spec-derived test suite under `platform_tests/groundtruth_kb/`, one new SessionStart-drain regression test, and one formal-artifact-approval packet for the rule-file edit. The standing-backlog state transition is the routine one-WI close path (open -> in_progress -> resolved on VERIFIED), not a bulk-ops sweep. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` therefore does not apply; the slice is a single schema/CLI addition with one-test-file, one-doc-section, and one-WI scope.

## Requirement Sufficiency

Existing requirements sufficient.

SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 already establishes the deterministic-transaction contract that covers both the role-switch axis (delivered in the VERIFIED parent thread) and the bridge-configuration axes. Acceptance criteria are stable. This slice consumes the bridge-configuration dispatch-substrate axis only; no new requirement, no requirement revision, and no clarification AUQ are needed. Subsequent slices (axis-2 surface registration; protocol-mode flags) will operate under the same spec.

## Implementation Plan

1. Add new module `groundtruth-kb/src/groundtruth_kb/mode_switch/bridge_substrate.py`. Exposes:
   - `BridgeSubstrate` enum-like literal: `cross_harness_trigger | single_harness_dispatcher | none`.
   - `BridgeSubstrateTransactionResult` dataclass: `previous_substrate`, `new_substrate`, `registration_diff`, `audit_record_path`, `applied_at`.
   - `BridgeSubstrateValidationError(RuntimeError)` (mirrors `TransactionValidationError` from the parent slice).
   - `apply_bridge_substrate_switch(project_root: Path, new_substrate: str, *, change_reason: str | None = None) -> BridgeSubstrateTransactionResult`.
   - `defer_bridge_substrate_switch(project_root: Path, new_substrate: str, *, change_reason: str | None = None) -> PendingBridgeSubstrateTransaction`.
   - Pre-write validators (run in order before any state mutation):
     a. role-artifact validator (re-uses `validate_role_artifact` from `mode_switch.validation`) - dispatch substrate must be consistent with role-set topology (cross-harness-trigger requires multi-harness; single-harness-dispatcher requires single-harness; `none` is always valid).
     b. substrate-artifact validator - probes registration health: `.claude/settings.json` PostToolUse+Stop hooks for `cross_harness_bridge_trigger.py`; Windows scheduled task `GTKB-SingleHarnessBridgeDispatcher` for the single-harness dispatcher.
     c. session-state-artifact validator - re-uses `validate_session_state_artifact`; substrate change does not invalidate session-state.
   - Atomic write of `harness-state/bridge-substrate.json` (NEW file) via tempfile + os.replace. Schema: `{"substrate": "<value>", "applied_at": "<iso>", "applied_by": "<harness_id>"}`.
   - Audit record written to `.gtkb-state/mode-switches/applied/<timestamp>-<uuid>.json` with `axis: "bridge_substrate"` field discriminating from the role axis.
2. Add `gt mode set-bridge-substrate --substrate <value> [--reason <text>] [--defer-to-next-session]` CLI subcommand in `groundtruth-kb/src/groundtruth_kb/cli.py`. Same flag shape as `gt mode set-role`.
3. Extend `gt mode list-pending` and `gt mode apply-pending` to surface and drain bridge-substrate pending entries alongside role-switch pending entries. Discriminator is the `axis` field in the pending JSON.
4. Update `scripts/cross_harness_bridge_trigger.py` and `scripts/single_harness_bridge_automation.py` to honor `harness-state/bridge-substrate.json` when present: each substrate's own activation code returns inert (no-op + audit-log entry) when `bridge-substrate.json` declares a different substrate as active. This is the registration-boundary enforcement.
5. Add subsection to `.claude/rules/operating-role.md` § Mode-Switch Transaction Component documenting `gt mode set-bridge-substrate`, the `--defer-to-next-session` flag, and the prohibition against ad-hoc edits to substrate registration files. The edit requires a formal-artifact-approval packet at implementation time.
6. Pre-write validators emit structured errors via `BridgeSubstrateValidationError` carrying `axis: "role" | "substrate" | "session-state"` to support downstream tooling.

State-file paths (all in-root):
- `harness-state/bridge-substrate.json` - durable substrate selection (NEW).
- `.gtkb-state/mode-switches/pending/<timestamp>-<uuid>.json` - pending transactions (shared dir with role-switch axis; discriminated by `axis` field).
- `.gtkb-state/mode-switches/applied/<timestamp>-<uuid>.json` - applied audit records (shared dir).
- `.gtkb-state/mode-switches/failed/<timestamp>-<uuid>.json` - validator-failure records, optional (parent slice does not use this; included here for symmetry with the parent audit pattern).

## Test Mapping

Each test maps to an acceptance criterion of `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` consumed by the dispatch-substrate axis.

1. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py::test_apply_writes_harness_state_atomically` - criterion: durable state is updated via atomic rename only after validators pass.
2. `test_mode_switch_bridge_substrate.py::test_apply_emits_audit_record_with_axis_field` - criterion: each applied transaction emits a durable audit record carrying the axis discriminator.
3. `test_mode_switch_bridge_substrate.py::test_apply_rejects_substrate_topology_mismatch` - criterion: validator REJECTS cross-harness-trigger on a single-harness role-map and vice versa (validator-first, no state mutation on failure).
4. `test_mode_switch_bridge_substrate.py::test_apply_is_idempotent_when_substrate_unchanged` - criterion: re-applying the same substrate is a no-op with `previous_substrate == new_substrate` and emits a "no-change" audit record.
5. `test_mode_switch_bridge_substrate_validation.py::test_substrate_artifact_validator_reports_missing_hook_registrations` - criterion: validator probes registration health and reports each missing registration as a discrete error string.
6. `test_mode_switch_bridge_substrate_validation.py::test_role_artifact_validator_required_before_substrate_write` - criterion: validator order is enforced and a missing role artifact halts the substrate switch before any substrate-side probe runs.
7. `test_mode_switch_bridge_substrate_pending.py::test_defer_writes_pending_file_with_axis_bridge_substrate` - criterion: deferred transactions land in the same pending queue as role-switch transactions and are discriminated by axis.
8. `test_mode_switch_bridge_substrate_pending.py::test_apply_pending_drains_bridge_substrate_entries` - criterion: shared `apply_pending` entry point applies both role and substrate pending entries in scheduled-at order.
9. `test_mode_switch_bridge_substrate_pending.py::test_apply_pending_records_failed_entries_with_error` - criterion: failed entries remain in `pending/` with an error log; successful entries move to `applied/`.
10. `platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py::test_session_start_drains_pending_before_role_resolution` - criterion: SessionStart drain runs before durable-role resolution so the next session sees the new substrate immediately.
11. `test_mode_switch_bridge_substrate.py::test_cli_set_bridge_substrate_invokes_apply_switch` - criterion: CLI surface maps to the transaction function and propagates `--reason` to the audit record.
12. `test_mode_switch_bridge_substrate.py::test_cli_set_bridge_substrate_defer_flag_queues_pending` - criterion: `--defer-to-next-session` queues the transaction without immediate apply.
13. `test_mode_switch_bridge_substrate.py::test_substrate_inert_path_when_disagrees_with_durable_selection` - criterion: when `harness-state/bridge-substrate.json` declares a different substrate as active, the disagreeing substrate code path returns inert and emits a durable audit-log entry.

## Risk and Rollback

Risk classes considered:

- R1 (low). Schema-rename collision with future axis-2 slice. Mitigation: axis field is explicit and namespaced (`bridge_substrate`); future axis-2 work uses its own axis token (`axis_2_surface`).
- R2 (low). Pending-queue ordering ambiguity. Mitigation: filenames are timestamp-prefixed; `apply_pending` orders by mtime then filename.
- R3 (medium). Substrate inert-path could mis-fire if `harness-state/bridge-substrate.json` is corrupted. Mitigation: validators run before write, atomic-rename prevents partial writes, fail-soft on read in the inert-path check.
- R4 (low). `.claude/rules/operating-role.md` edit collides with parallel-session approval packets. Mitigation: formal-artifact-approval packet is fetched at implementation time, not pre-fetched here; live state hash is rechecked at write.
- R5 (low). Audit-record dir grows unbounded. Mitigation: matches parent slice's behavior; rotation is a separate hygiene slice.

Rollback path: deleting `harness-state/bridge-substrate.json` reverts to the pre-Slice-1 behavior where both substrates self-activate based on topology. Pending queue files can be deleted manually if a queued transaction needs to be cancelled before SessionStart drain. The `.claude/rules/operating-role.md` edit is one paragraph; reverting is a single `Edit` operation. Existing role-switch transactions are unaffected.

## Acceptance Criteria

A. `gt mode set-bridge-substrate --substrate cross_harness_trigger` on a multi-harness install completes successfully, writes `harness-state/bridge-substrate.json` atomically, and emits an audit record with `axis: "bridge_substrate"`, `new_substrate: "cross_harness_trigger"`.
B. `gt mode set-bridge-substrate --substrate cross_harness_trigger` on a single-harness install raises `BridgeSubstrateValidationError(axis="role")` with a clear topology-mismatch message and writes nothing.
C. `gt mode set-bridge-substrate --defer-to-next-session` queues a pending file under `.gtkb-state/mode-switches/pending/` with `axis: "bridge_substrate"`.
D. `gt mode apply-pending` drains both role-switch and bridge-substrate pending entries; failed entries remain in `pending/` with an error log; succeeded entries move to `applied/`.
E. SessionStart drain hooks (Claude Code, Codex) apply pending bridge-substrate transactions before durable-role resolution.
F. When `harness-state/bridge-substrate.json` declares `single_harness_dispatcher` and `scripts/cross_harness_bridge_trigger.py` fires, the trigger returns inert and writes a durable audit-log entry.
G. `.claude/rules/operating-role.md` § Mode-Switch Transaction Component documents `gt mode set-bridge-substrate` with the same `--defer-to-next-session` and prohibition-on-ad-hoc-edits semantics as `gt mode set-role`.
H. All 13 spec-derived tests pass under `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate*.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py -q`.

## Verification Plan

Bridge-side preflights at proposal review and post-impl verification:

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-mode-config-transactions-slice-1` - expect `preflight_passed: true`, no missing required specs.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-mode-config-transactions-slice-1` - expect exit 0, no blocking gaps.

Implementation-side spec-derived tests:

3. `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py -q --tb=short` - expect all 13 tests pass.

Regression sweep:

4. `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_pending.py -q` - expect no regression of the parent slice's 39 tests.

Narrative-artifact evidence:

5. `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/operating-role.md` - expect PASS after formal-artifact-approval packet is filed.

Manual smoke test:

6. `python -m groundtruth_kb mode set-bridge-substrate --substrate cross_harness_trigger --reason "smoke test"` on a multi-harness install - expect success and audit record.
7. Inspect `.gtkb-state/mode-switches/applied/<latest>.json` - expect `axis: "bridge_substrate"`, `new_substrate: "cross_harness_trigger"`.

## Applicability Preflight

Preflight will be run against this proposal before INDEX update. The expected result is `preflight_passed: true` with no missing required or advisory specs. The result block will be embedded once the preflight tool can read the operative file (i.e., after the INDEX entry is created in a later step; the catch-22 handling per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection applies). The Specification Links above cites the full cross-cutting set the preflight registry expects for bridge-protocol proposals at paths `bridge/`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/project-root-boundary.md`, and `.claude/rules/operating-role.md`, and content-matches for `Specification Links`, `VERIFIED`, `verification`, `spec-to-test`, `owner decision`, `requirement`, `specification`, `ADR`, `DCL`, `backlog`, `inventory`, and `formal-artifact-approval`.

End of proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
