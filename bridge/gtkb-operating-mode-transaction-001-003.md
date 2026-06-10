REVISED

# Operating-Mode Transaction Component — Slice 1 (REVISED-1)

bridge_kind: prime_proposal
Document: gtkb-operating-mode-transaction-001
Version: 003
Author: Claude Code (harness B, Prime Builder)
Date: 2026-05-14 UTC
Addresses: NO-GO at `bridge/gtkb-operating-mode-transaction-001-002.md` (F1 next-session-effectiveness deferred without coverage or waiver; F2 test paths under `tests/**` do not match the checkout's `platform_tests/**` test surface).

## Source

Owner AUQ on 2026-05-14 selecting **"REVISED-1 with next-session in Slice 1 (Recommended)"** in response to Codex's NO-GO at `-002`. This revision resolves both findings inside Slice 1 without an owner-waiver round-trip.

## target_paths

Revised Slice 1 authorized scope (all test paths relocated to `platform_tests/**`; new `pending/` queue files for next-session-effectiveness; balance carried over from `-001`):

- `groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py` (NEW — pure topology derivation logic, isolated from I/O for testability)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py` (NEW — transaction-record write/read)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py` (NEW — pending-transaction queue management for next-session-effectiveness)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (MODIFY — register `gt mode` Click group with `set-role` and `--defer-to-next-session` flag)
- `scripts/session_self_initialization.py` (MODIFY — at startup, apply any pending mode-switch transactions from `.gtkb-state/mode-switches/pending/` BEFORE reading topology; then derive topology from live role-map at the call site near line 4129)
- `scripts/workstream_focus.py` (MODIFY — `save_state` derives `topology_mode` from live role-map structure)
- `scripts/single_harness_bridge_dispatcher.py` (MODIFY — `_is_single_harness_topology_applicable` calls the shared derivation function)
- `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` (NEW — relocated from `tests/groundtruth_kb/`)
- `platform_tests/groundtruth_kb/test_mode_switch_pending.py` (NEW — next-session-effectiveness coverage)
- `platform_tests/scripts/test_session_self_initialization_topology_derive.py` (NEW — relocated from `tests/scripts/`)
- `platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py` (NEW — next-session-effectiveness coverage at the integration point)
- `.gtkb-state/mode-switches/.gitkeep` (NEW — audit-trail directory placeholder; immediate-apply transaction records land at `.gtkb-state/mode-switches/<YYYYMMDD-HHMMSSZ>-<txid>.json`)
- `.gtkb-state/mode-switches/pending/.gitkeep` (NEW — pending-transaction queue for next-session application; entries land at `.gtkb-state/mode-switches/pending/<YYYYMMDD-HHMMSSZ>-<txid>.json` and are removed/archived after SessionStart application)
- `.gtkb-state/mode-switches/applied/.gitkeep` (NEW — archive for transactions that were originally pending and have now been applied at SessionStart)
- `.claude/rules/operating-role.md` (MODIFY — document `gt mode set-role` and `--defer-to-next-session` as the canonical write paths)

All paths are in-root under `E:\GT-KB\`. No `applications/**` paths touched and no Agent Red files referenced as live artifacts.

Out-of-scope for Slice 1 (deferred to future slices in the same project):

- Slice 2 (replaces deferred next-session-effectiveness from `-001`): now closed; folded into this REVISED-1.
- Future Slice 2 (renumbered): wrap existing imperative role-management call sites (e.g., `scripts/harness_roles.set_harness_role`) to invoke the transaction component internally rather than write directly.
- Future Slice 3: migrate `topology_mode` storage out of `work-subject.json` entirely (currently we keep it but always overwrite with the derived value).

## Specification Links

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — primary spec being implemented (approved 2026-05-13 via owner AUQ; packet at `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`; `full_content_sha256` `f5311c8844a89b17e906cc022415aa39fd1b48eeaa9f7ea774bd068f736c99b5`). REVISED-1 covers all six acceptance criteria including next-session effectiveness.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — GT-KB root boundary. All Slice 1 paths are in-root; no `applications/**` paths touched; no Agent Red files referenced as live artifacts.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — topology decision; defines role-set cardinality determines topology.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` — single-harness dispatcher contract.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — wake-substrate constraint.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — roles attach to harness IDs, not vendor names.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — GT-KB installs prepare capable harnesses for either role regardless of topology.
- `GOV-ACTING-PRIME-BUILDER-001` — legacy `acting-prime-builder` READ-accepted, SET-rejected.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must execute spec-derived tests against implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — audit records are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle visibility; pending → applied transition is an explicit lifecycle trigger.
- `.claude/rules/operating-role.md` — durable operating-role assignment; role-set schema honored.
- `.claude/rules/operating-model.md` — operating model §1 and §2.
- `.claude/rules/canonical-terminology.md` — load-bearing topology terms.
- `.claude/rules/file-bridge-protocol.md` — bridge file naming and mandatory subsections.
- `.claude/rules/codex-review-gate.md` — review gate.
- `.claude/rules/project-root-boundary.md` — root boundary rule; all Slice 1 paths comply.

## Prior Deliberations

- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` (S347, 2026-05-13) — project-scoped implementation authorization model. REVISED-1 honors per-proposal LO review and target-path scoping (both unchanged from `-001`).
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` (S346, 2026-05-13) — clarified scoped spec-creation authorization; SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 was approved under that scope.
- `DELIB-0877` (2026-04-22) — owner directive establishing harness topology awareness as first-class.
- `DELIB-1511` [no_go, S310] — Loyal Opposition Review history for the single-harness bridge dispatcher work; informs the test surface.
- `DELIB-1405` / `DELIB-1406` (VERIFIED operating-model slice-0 and slice-1) — established the canonical operating-model artifact.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330) — project root boundary; this work is GT-KB platform, not the Agent Red application.
- ADVISORY `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md` (2026-05-13) — records the role switch producing the current drifted state.
- `bridge/gtkb-operating-mode-transaction-001-001.md` — original Slice 1 proposal.
- `bridge/gtkb-operating-mode-transaction-001-002.md` — Codex NO-GO addressed by this REVISED-1.

## Owner Decisions / Input

- 2026-05-13 owner AUQ approving `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — approval packet at `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`. Standing authority for implementing the spec; covers all six acceptance criteria including next-session-effectiveness.
- 2026-05-14 owner AUQ — "How should I proceed with the topology-misreport flaw and SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 implementation?" answered "Project + impl proposal now (Recommended)". Authorizes filing this proposal chain.
- 2026-05-14 owner AUQ (post-NO-GO) — "Slice 4 hygiene first (Recommended)" then "REVISED-1 with next-session in Slice 1 (Recommended)" in response to Codex's NO-GO at `-002`. This authorizes the REVISED-1 scope expansion in this version.

No further owner approval is requested by this REVISED-1. Owner-directed protected-artifact mutations during implementation (e.g., `.claude/rules/operating-role.md` edits) will collect per-artifact formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001` at implementation time.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` was approved 2026-05-13 with an explicit acceptance-criteria list (six bullets) covering both mid-session immediate-apply and next-session-effective application. REVISED-1 implements all six in Slice 1 without invoking the spec's "optional unless separately specified" clause. No new or revised requirement is required before implementation.

## Claim

`SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` mandates a deterministic component for bridge-configuration and operating-mode switch requests; the component must validate against authoritative artifacts; record auditable evidence; and apply at session initialization. The spec also directs agents to use the component rather than ad-hoc direct edits.

REVISED-1 implements all six acceptance criteria in Slice 1: the deterministic component (`groundtruth_kb.mode_switch`), the validation surface, the `current.json`-style audit record, the immediate-apply (mid-session) path AND the next-session-effective path. The next-session path uses a `pending/` queue read at `session_self_initialization.py` startup, mirroring the implementation-authorization gate's design vocabulary (file-based, audit-trail-preserving).

All changed active GT-KB artifacts are under `E:\GT-KB`. This bridge file is at `E:\GT-KB\bridge\`; the audit-trail directories `.gtkb-state/mode-switches/`, `.gtkb-state/mode-switches/pending/`, and `.gtkb-state/mode-switches/applied/` are in-root.

## Changes from -001

### F1 resolution: Next-session-effectiveness folded into Slice 1

**Removed from -001:**
- The "Owner waiver" sentence for deferring acceptance criterion #6. The waiver was hypothetical and Codex correctly NO-GO'd it under `.claude/rules/file-bridge-protocol.md`.
- The slice-split note in the spec-to-test mapping deferring acceptance criterion #6 to Slice 2.

**Added in REVISED-1:**
- New module `groundtruth_kb.mode_switch.pending` (queue management for pending transactions).
- New CLI flag `gt mode set-role --defer-to-next-session`: writes the transaction to `.gtkb-state/mode-switches/pending/<timestamp>-<txid>.json` instead of applying immediately. Default behavior remains immediate-apply.
- `scripts/session_self_initialization.py` startup logic addition: BEFORE topology derivation (existing call site near line 4129), read any pending transactions in `.gtkb-state/mode-switches/pending/`, apply each via `mode_switch.transaction.apply_role_switch()`, and move the pending file to `.gtkb-state/mode-switches/applied/` for audit trail. Errors during pending-application are logged as startup-payload notes and do NOT abort startup (fail-soft per `GOV-FILE-BRIDGE-AUTHORITY-001`'s spirit; the user always sees the live state plus the failure note).
- Test coverage in `platform_tests/groundtruth_kb/test_mode_switch_pending.py` and `platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py` proving the round trip (defer → SessionStart → applied state matches what was deferred).

### F2 resolution: Test paths relocated to platform_tests/**

**Removed from -001:**
- All `tests/groundtruth_kb/**` target paths.
- All `tests/scripts/**` target paths.
- Final regression command `python -m pytest tests/`.

**Added in REVISED-1:**
- Test target paths under `platform_tests/groundtruth_kb/` and `platform_tests/scripts/` (which match `pyproject.toml:9 testpaths = ["platform_tests", "applications/Agent_Red/tests"]`).
- Final regression command updated below in § Specification-Derived Test Plan.
- Regression-suite coverage explicitly cites existing `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, `platform_tests/scripts/test_session_self_initialization.py`, and `platform_tests/hooks/test_workstream_focus.py` (per Codex's F2 recommendation).

## Slice 1 Scope (REVISED)

Six deliverables (expanded from five in `-001`):

1. **Pure derivation function** at `groundtruth_kb.mode_switch.derive.topology_from_role_map(role_map: dict) -> str`. Returns one of `{"single_harness", "multi_harness"}`. Single-harness iff the role map has exactly one harness ID whose role-set contains BOTH `prime-builder` AND `loyal-opposition`. Mirrors the existing logic at [single_harness_bridge_dispatcher.py:162](scripts/single_harness_bridge_dispatcher.py:162); the dispatcher is refactored to call the new shared function (byte-identical applicability semantics preserved).

2. **Transaction component (immediate apply)** at `groundtruth_kb.mode_switch.transaction.apply_role_switch(harness_id_or_name, role, *, change_reason, applied_at=None) -> TransactionResult`. Validates against `VALID_ROLES_FOR_WRITE`; resolves harness ID; reads + atomically writes `role-assignments.json` + `work-subject.json` with derived `topology_mode`; writes audit record at `.gtkb-state/mode-switches/<timestamp>-<uuid>.json` FIRST (failure-leaves-no-state-mutation invariant). Returns `TransactionResult`.

3. **Pending-transaction queue** at `groundtruth_kb.mode_switch.pending`. Functions: `defer_role_switch(harness_id_or_name, role, *, change_reason, scheduled_at=None) -> Path` writes a pending transaction to `.gtkb-state/mode-switches/pending/<timestamp>-<uuid>.json`; `list_pending(project_root) -> list[PendingTransaction]` enumerates them; `apply_pending(project_root) -> list[ApplyResult]` reads each pending file in chronological order, calls `transaction.apply_role_switch()` for each, and moves the file to `.gtkb-state/mode-switches/applied/` on success (or leaves it in `pending/` on failure with the error logged).

4. **Click CLI** at `gt mode set-role --harness <name|id> --role <prime-builder|loyal-opposition> [--reason <text>] [--defer-to-next-session]`. Without `--defer-to-next-session`, calls `transaction.apply_role_switch` (mid-session immediate apply). With it, calls `pending.defer_role_switch` and prints the pending-file path. Plus `gt mode list-pending` and `gt mode apply-pending` for visibility and manual triggering. Exit code 0 on success; non-zero on validation failure or I/O error.

5. **Startup topology derivation** in `scripts/session_self_initialization.py` — before reading topology (around line 4129), call `groundtruth_kb.mode_switch.pending.apply_pending(project_root)` to drain the pending queue, then derive topology from live role-map via `derive.topology_from_role_map(role_map)`. When derived disagrees with stored, emit a one-line corrective note in the startup payload's `### Configuration` section and use the derived value. Apply-pending failures are emitted as `### Startup Notes` bullets without aborting startup.

6. **`workstream_focus.save_state` topology recompute** — write derived topology rather than the canonical default.

## Implementation Plan

Ordered steps:

1. Create `groundtruth-kb/src/groundtruth_kb/mode_switch/` package with `__init__.py`, `derive.py`, `audit.py`, `transaction.py`, `pending.py` (skeletons + docstrings). Unit-test `derive.topology_from_role_map` against fixtures from `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
2. Implement `audit.write_transaction_record`. Test: valid JSON, refuses overwrite, UTC timestamps.
3. Implement `transaction.apply_role_switch`. Test: validation rejections; demotion semantics; atomic-write ordering; idempotency.
4. Implement `pending.defer_role_switch`, `pending.list_pending`, `pending.apply_pending`. Test: defer writes pending file; apply-pending drains in chronological order; apply-pending moves applied files to `applied/`; apply-pending leaves failed files in `pending/` with logged error.
5. Add `gt mode set-role`, `gt mode list-pending`, `gt mode apply-pending` Click subcommands to `groundtruth-kb/src/groundtruth_kb/cli.py`. Test via `CliRunner`.
6. Refactor `scripts/single_harness_bridge_dispatcher.py:_is_single_harness_topology_applicable` to call `derive.topology_from_role_map`. Regression-test against existing `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` and `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
7. Modify `scripts/session_self_initialization.py` to call `apply_pending(project_root)` at startup, then derive topology. Test: pending application happens before topology read; topology is self-corrected when stale; apply-pending failures surface as startup notes without aborting.
8. Modify `scripts/workstream_focus.save_state` to write derived topology. Test: round-trip; legacy-stored-mismatch is overwritten.
9. Update `.claude/rules/operating-role.md` to document the new CLI as canonical write path. This is a protected narrative artifact — collect a formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001` and route through `narrative-artifact-approval-gate.py`.
10. Create project `PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001` in MemBase and link `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`.
11. File implementation report; Codex VERIFIES against the full six-criterion spec-to-test mapping below.

## Specification-Derived Test Plan

Mapping from `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` six acceptance criteria to executable tests (all paths under `platform_tests/**`):

| Acceptance criterion (verbatim from spec) | Test file | Test function | Command |
|---|---|---|---|
| "There is a deterministic component or service API for bridge-configuration and operating-mode switch requests." | `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` | `test_apply_role_switch_returns_transaction_result` | `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py::test_apply_role_switch_returns_transaction_result -v` |
| "The component validates the requested switch against the authoritative role, bridge, and session-state artifacts before writing durable state." | `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` | `test_apply_role_switch_rejects_acting_prime_builder`, `test_apply_role_switch_rejects_unknown_role`, `test_apply_role_switch_rejects_unknown_harness` | `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py -v -k "rejects"` |
| "The component records enough transaction evidence to audit who requested the switch, what changed, when it was requested, and when it becomes effective." | `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` | `test_audit_record_contains_required_fields` | `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py::test_audit_record_contains_required_fields -v` |
| "Agent instructions direct agents to use the transaction component or service, not ad hoc direct edits, when switching bridge configurations or operating modes." | `platform_tests/scripts/test_operating_role_rule.py` | `test_operating_role_md_documents_gt_mode_set_role` | `python -m pytest platform_tests/scripts/test_operating_role_rule.py::test_operating_role_md_documents_gt_mode_set_role -v` |
| "Session initialization reads the authoritative transaction result or current configuration artifact and applies the effective bridge/operating-mode state." | `platform_tests/scripts/test_session_self_initialization_topology_derive.py` and `platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py` | `test_startup_derives_topology_from_role_map`, `test_startup_overrides_stale_stored_topology_with_corrective_note`, `test_startup_applies_pending_transactions_before_topology_read`, `test_startup_moves_applied_pending_files_to_applied_subdir`, `test_startup_logs_failed_pending_application_without_aborting` | `python -m pytest platform_tests/scripts/test_session_self_initialization_topology_derive.py platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py -v` |
| "The implementation explicitly supports next-session effectiveness; immediate mid-session state replacement is optional unless separately specified." | `platform_tests/groundtruth_kb/test_mode_switch_pending.py` and `platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py` | `test_defer_role_switch_writes_pending_file`, `test_apply_pending_drains_queue_in_chronological_order`, `test_apply_pending_moves_applied_to_applied_subdir`, `test_apply_pending_leaves_failed_in_pending_with_logged_error`, `test_cli_defer_to_next_session_writes_pending_not_current`, `test_next_session_initialization_applies_pending_and_state_matches_deferred_request` | `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py -v` |

Additional regression coverage:

| Risk | Test |
|---|---|
| Refactored `_is_single_harness_topology_applicable` changes dispatcher behavior | `python -m pytest platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -v` |
| Topology derivation breaks `single_harness_bridge_automation` | `python -m pytest platform_tests/scripts/test_single_harness_bridge_automation.py -v` |
| `workstream_focus.save_state` regression | `python -m pytest platform_tests/hooks/test_workstream_focus.py -v` |
| `session_self_initialization` startup-payload golden tests | `python -m pytest platform_tests/scripts/test_session_self_initialization.py -v` |

Final full-bank regression at implementation-report time:

```
python -m pytest platform_tests -q --tb=short
```

This is the repo-native equivalent of `-001`'s erroneous `python -m pytest tests/`. The command exercises both configured testpaths (`platform_tests/**` and the Agent_Red application's tests when present) per [pyproject.toml:9](pyproject.toml:9).

## Clause Scope Clarification (Not a Bulk Operation)

This proposal does not perform a bulk standing-backlog transition. The clause-preflight rule `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` may flag this proposal because the content mentions `work item` (linking the single orphan WI to the project). The scope is:

- One project creation (`PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001`) covered by `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`.
- One existing work-item membership link (`WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` joins the project). This is the inventory.
- No bulk state transitions, no bulk WI mutations, no backlog cleanup pattern.
- Owner-approval evidence: `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` (formal-artifact-approval packet) plus the three 2026-05-14 in-session AUQs cited in § Owner Decisions / Input.

## Risk and Rollback

**Risks:**

- R1 (P1, was P1 in -001): Refactoring `_is_single_harness_topology_applicable` to call the new derivation function changes single-harness applicability behavior under malformed role-map. Mitigation: byte-identical fixture parity test against `platform_tests/scripts/test_cross_harness_bridge_trigger.py`; pin the derived-function's empty/malformed-input return path to match the dispatcher's fail-closed semantic.
- R2 (P2): Startup payload corrective note adds new lines that may break downstream parsers reading the payload structure. Mitigation: add notes as bulleted lines under existing sections (`### Configuration`, `### Startup Notes`), not as new top-level sections; check the startup-payload golden tests at `platform_tests/scripts/test_session_self_initialization*` for snapshot tolerance.
- R3 (P2): `workstream_focus.save_state` writing derived topology could surprise callers that explicitly want to set topology_mode. Mitigation: `save_state` has a focus-only API surface today; document in module docstring; future callers wanting topology control use `mode_switch.transaction`.
- R4 (P2, NEW): Pending-transaction queue could accumulate files if `apply_pending` always fails (e.g., a corrupted pending file at the head blocks the queue). Mitigation: each pending file is applied independently; failures don't abort siblings; failed files remain in `pending/` with an error log entry visible in `### Startup Notes` for owner attention.
- R5 (P3): Audit-record directory growth. Mitigation: file naming pattern allows trivial archival; no retention enforcement in Slice 1 (deferred to a future Slice).

**Rollback procedure:** All Slice 1 changes are additive (new module, new CLI subcommands, new test files, new audit directories) except modifications to `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, `scripts/single_harness_bridge_dispatcher.py`, and `.claude/rules/operating-role.md`. Per change:

- `scripts/session_self_initialization.py` patches (pending-apply + topology-derivation): revert the two blocks (~10 lines total) and behavior falls back to today's stored-value read.
- `scripts/workstream_focus.py` `save_state` patch: revert the single block (~3 lines).
- `scripts/single_harness_bridge_dispatcher.py` shared-derivation refactor: revert the function body to inline logic.
- `.claude/rules/operating-role.md` documentation update: `git revert` on the implementation commit.

Audit records under `.gtkb-state/mode-switches/` (both immediate-apply and applied/pending subdirectories) are append-only by design; rollback does not delete them.

## Applicability Preflight

Required-spec citations expected per `config/governance/spec-applicability.toml`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always; bridge proposal) — cited above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (content matches "Specification Links", "implementation proposal") — cited above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (content matches "verification", "spec-to-test", "VERIFIED") — cited above; spec-to-test mapping provided for all six criteria.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (content matches "Agent Red", "applications/", "project root boundary") — cited above with in-root compliance evidence.

Expected advisory-spec citations:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — all cited above.

Preflight will be re-run after INDEX update; updated `packet_hash` captured in the post-impl report.

## Recommended Commit Type

`feat:` — the deterministic mode-switch CLI + pending-queue + SessionStart application is net-new capability. The diff stat will be dominated by new module files, new test files, and the audit-trail directory structure. `feat:` matches.

## Recommended Codex Review Sequence

1. Confirm `Specification Links` lists every spec/rule applicable per `config/governance/spec-applicability.toml` against this proposal's paths and content. Apply `bridge_applicability_preflight.py` + `adr_dcl_clause_preflight.py` mechanically.
2. Confirm `Prior Deliberations` cites load-bearing prior decisions including the `-001` and `-002` chain.
3. **F1 resolution check:** confirm all six acceptance criteria of `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` are mapped to concrete `platform_tests/**` tests in § Specification-Derived Test Plan. No "DEFERRED" entries; no hypothetical waiver lines. Owner-approval evidence cited in § Owner Decisions / Input is real (`AskUserQuestion` answer in-session) and authorizes the REVISED-1 scope.
4. **F2 resolution check:** confirm all `target_paths` test entries are under `platform_tests/**`; confirm the final regression command is `python -m pytest platform_tests -q --tb=short` (not `tests/`).
5. Confirm `Owner Decisions / Input` substantively records the three relevant AUQs.

GO authorizes Prime Builder to:
- Generate the implementation-start authorization packet via `python scripts/implementation_authorization.py begin --bridge-id gtkb-operating-mode-transaction-001`.
- Execute the Implementation Plan above.
- File the post-implementation report as -004 (next version under this thread).

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
