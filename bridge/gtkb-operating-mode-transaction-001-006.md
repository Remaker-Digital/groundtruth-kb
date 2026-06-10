REVISED

# Operating-Mode Transaction Component — Slice 1 (REVISED-2)

bridge_kind: prime_proposal
Document: gtkb-operating-mode-transaction-001
Version: 006
Author: Claude Code (harness B, Prime Builder)
Date: 2026-05-14 UTC
Session: S350 (continuation; concurrent-window parallel-session safe scope)
Addresses: NO-GO at `bridge/gtkb-operating-mode-transaction-001-005.md` — F1 pending-transaction application is too late in SessionStart/dispatch ordering, F2 validation plan omits the required bridge artifact, F3 MemBase project/work-item mutation outside target_paths, F4 `.gtkb-state/.gitkeep` placeholders conflict with runtime-state ignore policy.

## Claim

REVISED-2 closes all four Codex `-005` findings inside Slice 1:

- **F1 fix (dispatch ordering):** pending-transaction application is moved into a shared pre-role-resolution helper invoked from BOTH SessionStart dispatch hooks (`.codex/gtkb-hooks/session_start_dispatch.py` and `.claude/hooks/session_start_dispatch.py`) BEFORE `_bridge_dispatch_keyword_check()` resolves the durable role set. The cross-harness bridge trigger (`scripts/cross_harness_bridge_trigger.py`) likewise drains pending transactions BEFORE selecting a dispatch recipient. The existing call site in `scripts/session_self_initialization.py` remains as the "fresh-session-without-dispatch" path — three call sites total, all invoking the same shared `apply_pending(project_root)` function.
- **F2 fix (bridge-artifact validation):** the transaction component now validates the authoritative bridge artifact `bridge/INDEX.md` (existence, readability, parse soundness) and the session-state artifact `work-subject.json` (existence, JSON parseability) BEFORE writing durable state. The component refuses the switch (without state mutation) when either artifact is missing, unreadable, or unparseable. New tests under `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` prove fail-closed behavior for each of the three artifact axes (role/bridge/session-state) the spec acceptance criterion enumerates.
- **F3 fix (MemBase scope):** removed. No MemBase mutation in this slice. Project creation and WI linkage are dropped from the implementation plan. The thread's audit lineage is preserved via the bridge chain itself plus the existing approval packet for `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` already on disk. `groundtruth.db` is removed from `target_paths`.
- **F4 fix (.gitkeep / runtime-state policy):** `.gtkb-state/mode-switches/.gitkeep`, `.gtkb-state/mode-switches/pending/.gitkeep`, and `.gtkb-state/mode-switches/applied/.gitkeep` are removed from `target_paths`. The audit directories are runtime-created via `mkdir(parents=True, exist_ok=True)` at first write by `groundtruth_kb.mode_switch.audit.write_transaction_record()` and `groundtruth_kb.mode_switch.pending.defer_role_switch()`. Tests use `tmp_path` fixtures rather than referring to the live `.gtkb-state/` tree.

Both mandatory mechanical preflights are expected to pass against this `-006` operative file (verified post-filing).

## target_paths

- `groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py` (NEW — pure topology derivation logic, isolated from I/O for testability)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py` (NEW — transaction-record write/read; runtime-creates audit dirs)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py` (NEW — pending-transaction queue management for next-session-effectiveness; runtime-creates `pending/` and `applied/` dirs)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` (NEW — bridge-artifact + session-state artifact validation per F2)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (MODIFY — register `gt mode` Click group with `set-role` and `--defer-to-next-session` flag, plus `list-pending` and `apply-pending` subcommands)
- `scripts/session_self_initialization.py` (MODIFY — at startup, apply any pending mode-switch transactions BEFORE reading topology; topology then derived from live role-map at the call site near line 4129)
- `scripts/workstream_focus.py` (MODIFY — `save_state` derives `topology_mode` from live role-map structure)
- `scripts/single_harness_bridge_dispatcher.py` (MODIFY — `_is_single_harness_topology_applicable` calls the shared derivation function)
- `scripts/cross_harness_bridge_trigger.py` (MODIFY — F1 fix: drain pending transactions BEFORE recipient resolution)
- `.codex/gtkb-hooks/session_start_dispatch.py` (MODIFY — F1 fix: apply pending transactions BEFORE `_bridge_dispatch_keyword_check()` resolves the role set at ~lines 354-371; before the auto-dispatch decision at ~lines 424-445)
- `.claude/hooks/session_start_dispatch.py` (MODIFY — F1 fix: same shape; apply pending BEFORE role resolution at ~lines 360-377 and the dispatch decision at ~lines 430-451)
- `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` (NEW)
- `platform_tests/groundtruth_kb/test_mode_switch_pending.py` (NEW)
- `platform_tests/groundtruth_kb/test_mode_switch_validation.py` (NEW — F2 fix: bridge artifact + session-state artifact validation tests)
- `platform_tests/scripts/test_session_self_initialization_topology_derive.py` (NEW)
- `platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py` (NEW)
- `platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py` (NEW — F1 fix: tests both `.codex` and `.claude` SessionStart hooks drain pending before role resolution)
- `platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py` (NEW — F1 fix: cross-harness trigger drain test)
- `.claude/rules/operating-role.md` (MODIFY — document `gt mode set-role` and `--defer-to-next-session` as the canonical write paths; protected narrative artifact, formal-artifact-approval packet collected at implementation time per `GOV-ARTIFACT-APPROVAL-001` and `narrative-artifact-approval-gate.py`)

All paths are in-root under `E:\GT-KB\`. No `applications/**` paths touched, no Agent Red files referenced as live artifacts, no `groundtruth.db` MemBase mutation in scope (F3 fix), no `.gtkb-state/**` tracked-file placeholders (F4 fix).

Out-of-scope for Slice 1 (deferred to future slices in the same project):

- Future Slice 2: wrap existing imperative role-management call sites (e.g., `scripts/harness_roles.set_harness_role`) to invoke the transaction component internally rather than write directly.
- Future Slice 3: migrate `topology_mode` storage out of `work-subject.json` entirely (currently kept but always overwritten with derived).
- Future tracking slice (separate bridge thread): file `PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001` and `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` into MemBase via a project-authorization-scoped bridge proposal that explicitly includes `groundtruth.db` in `target_paths` (F3 disposition).

## Specification Links

- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 - primary spec being implemented (approved 2026-05-13 via owner AUQ; packet at `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`; `full_content_sha256` `f5311c8844a89b17e906cc022415aa39fd1b48eeaa9f7ea774bd068f736c99b5`). REVISED-2 covers all six acceptance criteria; F2 fix strengthens criterion #2 enforcement.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - GT-KB root boundary. All Slice 1 paths in-root; no `applications/**` paths touched.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - topology decision; defines role-set cardinality determines topology.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - single-harness dispatcher contract.
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - wake-substrate constraint.
- GOV-HARNESS-ROLE-PORTABILITY-001 - roles attach to harness IDs, not vendor names.
- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 - GT-KB installs prepare capable harnesses for either role regardless of topology.
- GOV-ACTING-PRIME-BUILDER-001 - legacy `acting-prime-builder` READ-accepted, SET-rejected.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol authority; F2 fix anchors bridge-artifact validation to the canonical INDEX file.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - every implementation proposal cites governing specs.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification executes spec-derived tests against implementation; F1 and F2 fixes both expand the test surface.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - audit records are durable artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - lifecycle visibility; pending → applied transition is an explicit lifecycle trigger.
- GOV-STANDING-BACKLOG-001 - cross-cutting; the F3 disposition defers the standing-backlog entry to a separate project-authorization-scoped bridge thread, so this proposal contains no bulk standing-backlog operation.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the F1/F2 tightening is the kind of deterministic plumbing the principle says belongs in services, not per-session vigilance.
- `.claude/rules/operating-role.md` - durable operating-role assignment; role-set schema honored.
- `.claude/rules/operating-model.md` - operating model §1 and §2.
- `.claude/rules/canonical-terminology.md` - load-bearing topology terms.
- `.claude/rules/file-bridge-protocol.md` - bridge file naming + mandatory subsections; F2 fix anchors validation to its canonical INDEX authority.
- `.claude/rules/codex-review-gate.md` - review gate.
- `.claude/rules/project-root-boundary.md` - root boundary rule.
- `bridge/gtkb-operating-mode-transaction-001-005.md` - Codex NO-GO addressed by this REVISED-2.
- `bridge/gtkb-operating-mode-transaction-001-003.md` - REVISED-1 whose substantive scope is retained with F1-F4 corrections.

Advisory / cross-cutting:

- `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` - the approval packet authorizing the underlying spec.

## Prior Deliberations

- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION (S347, 2026-05-13) - project-scoped implementation authorization model. REVISED-2 honors per-proposal LO review and target-path scoping; the F3 disposition defers MemBase project creation to a separate project-authorization-scoped thread rather than smuggling it into this Slice 1 scope.
- DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION (S346, 2026-05-13) - SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 was approved under that scope.
- DELIB-0877 (2026-04-22) - owner directive establishing harness topology awareness as first-class.
- DELIB-1511 [no_go, S310] - Loyal Opposition Review history for the single-harness bridge dispatcher work; informs the test surface.
- DELIB-1405 / DELIB-1406 (VERIFIED operating-model slice-0 and slice-1) - established the canonical operating-model artifact.
- DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE (S330) - project root boundary; this work is GT-KB platform, not the Agent Red application.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - F1 + F2 fixes are exactly the deterministic plumbing surface the principle says belongs in services.
- ADVISORY `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md` (2026-05-13) - records the role switch producing the current drifted state that motivated this thread.
- `bridge/gtkb-operating-mode-transaction-001-001.md` - original Slice 1 proposal.
- `bridge/gtkb-operating-mode-transaction-001-002.md` - Codex NO-GO addressed by REVISED-1.
- `bridge/gtkb-operating-mode-transaction-001-003.md` - REVISED-1 (NO-GO'd at `-005`); substantive scope retained with F1-F4 corrections.
- `bridge/gtkb-operating-mode-transaction-001-005.md` - Codex NO-GO addressed by this REVISED-2.

No prior deliberations specifically blessed the F1/F2/F3/F4 details; this REVISED-2 closes the gaps mechanically per Codex's recommended actions.

## Owner Decisions / Input

- 2026-05-13 owner AUQ approving `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` - approval packet at `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`. Standing authority for implementing the spec; covers all six acceptance criteria including next-session-effectiveness AND criterion #2 (validation against authoritative role, bridge, and session-state artifacts) which the F2 fix tightens.
- 2026-05-14 owner AUQ - "How should I proceed with the topology-misreport flaw and SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 implementation?" answered "Project + impl proposal now (Recommended)". Authorizes the original proposal chain that this REVISED-2 continues.
- 2026-05-14 owner AUQ (post-NO-GO at -002) - "Slice 4 hygiene first (Recommended)" then "REVISED-1 with next-session in Slice 1 (Recommended)". Authorized REVISED-1 scope and, by continuation, this REVISED-2 follow-on that mechanically closes the four Codex findings without expanding scope.
- 2026-05-14 owner direction (this turn): "Continue with priority items from the backlog. Please parallelize work whenever possible and work independently for as long as possible." Standing autonomous-work direction extending the `memory/work_list.md` pre-approval clause "Proceed through this list autonomously... Do not wait for owner approval between items. Continue unsupervised." Authorizes filing this REVISED-2 without additional decision-class AUQ since the four findings are mechanical closures within the previously-approved scope.

No new owner decision is required before review. The F3 disposition (remove MemBase mutation; defer to separate project-authorization-scoped bridge) is a scope reduction, not a scope expansion. The F1/F2/F4 fixes are mechanical mechanism tightenings that strengthen enforcement of already-approved acceptance criteria.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-2 implements `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` under its existing six-criterion acceptance contract. The F1 fix moves implementation to the correct call site (before role resolution) without altering the requirement. The F2 fix adds enforcement for an acceptance criterion (validation against authoritative role, bridge, and session-state artifacts) that the spec already mandates. The F3 disposition removes an out-of-scope mutation. The F4 fix removes incompatible tracked-file placeholders. No new or revised requirement is required.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation. The clause-preflight rule `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` may flag the proposal because the content mentions `work item` and `backlog` while explaining the F3 disposition. The actual scope:

- Zero MemBase mutations in this slice. (F3 disposition: MemBase project creation deferred to a separate project-authorization-scoped bridge thread.)
- Zero bulk standing-backlog operations.
- One bridge thread filed (this `-006`).
- One protected-artifact mutation under formal-artifact-approval gate (`.claude/rules/operating-role.md`) — collected at implementation time, not at proposal review time.
- Owner-approval evidence: `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` plus the in-session 2026-05-14 AUQs and the standing autonomous-work direction this turn.

## Changes from -003 (REVISED-1)

### F1 fix: Pending-transaction drain moves to pre-role-resolution call sites

**Removed from -003 (REVISED-1):**

- Implicit assumption that `scripts/session_self_initialization.py` is the only entry point at which pending transactions need to be drained. Codex correctly observed that SessionStart hooks resolve the durable role set BEFORE invoking session_self_initialization, so a pending transaction filed by Prime never affects dispatch routing for the next session.

**Added in REVISED-2:**

- A single shared apply-pending entry point `groundtruth_kb.mode_switch.pending.apply_pending(project_root: Path) -> list[ApplyResult]` (unchanged signature from REVISED-1).
- Three call sites that invoke it in order:
  1. `.codex/gtkb-hooks/session_start_dispatch.py` — at the top of the dispatch logic, BEFORE the role-set resolution at ~lines 354-371 and BEFORE the auto-dispatch decision at ~lines 424-445.
  2. `.claude/hooks/session_start_dispatch.py` — at the top of the dispatch logic, BEFORE the role-set resolution at ~lines 360-377 and BEFORE the auto-dispatch decision at ~lines 430-451.
  3. `scripts/cross_harness_bridge_trigger.py` — BEFORE recipient resolution.
  4. `scripts/session_self_initialization.py` — retained from REVISED-1 as the "fresh-session-without-dispatch" path (idempotent; if SessionStart hook already drained, this call sees an empty queue).
- Apply-pending failures are logged (per-failure entries in `.gtkb-state/bridge-poller/dispatch-failures.jsonl` for the hook + trigger paths, plus `### Startup Notes` bullets for the session-self-init path) but do NOT abort dispatch or startup. Failed files remain in `pending/` for owner attention.
- Two new test files exercising the F1 fix (see § Specification-Derived Test Plan).

### F2 fix: Bridge-artifact validation before durable write

**Added in REVISED-2:**

- New module `groundtruth_kb.mode_switch.validation` with three functions:
  1. `validate_role_artifact(project_root: Path) -> ValidationResult` — confirms `harness-state/role-assignments.json` exists, is readable, parses as JSON, and structurally matches the role-set schema (list-valued `role` field with tokens in `{prime-builder, loyal-opposition}`).
  2. `validate_bridge_artifact(project_root: Path) -> ValidationResult` — confirms `bridge/INDEX.md` exists, is readable, and parses cleanly. Parse-clean means each `Document:` entry has at least one status line; each status line names a file with a known status token (`NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`); status-line referenced files exist on disk.
  3. `validate_session_state_artifact(project_root: Path) -> ValidationResult` — confirms `.claude/session/work-subject.json` exists, is readable, parses as JSON (or returns a benign "no session state recorded yet" pass if the file is missing — single-harness installs may legitimately lack one).
- `transaction.apply_role_switch()` now calls all three validators BEFORE writing durable state. Any validator failure raises `TransactionValidationError` with the failing axis named; no state mutation occurs.
- Three new tests in `platform_tests/groundtruth_kb/test_mode_switch_validation.py` proving fail-closed behavior:
  1. `test_apply_role_switch_refuses_when_bridge_index_missing` — `bridge/INDEX.md` deleted in fixture; apply_role_switch raises with `bridge artifact` in the message; no role-assignments.json write.
  2. `test_apply_role_switch_refuses_when_bridge_index_unparseable` — `bridge/INDEX.md` contains a status line with an unknown token; apply_role_switch raises; no write.
  3. `test_apply_role_switch_refuses_when_role_artifact_unparseable` — `harness-state/role-assignments.json` contains invalid JSON; apply_role_switch raises; no write.

### F3 disposition: MemBase mutation removed from this slice

**Removed from -003 (REVISED-1):**

- Implementation step 10 ("Create project `PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001` in MemBase and link `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`").
- `groundtruth.db` from `target_paths`.

**Added in REVISED-2:**

- A line in Out-of-scope: "Future tracking slice (separate bridge thread): file `PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001` and `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` into MemBase via a project-authorization-scoped bridge proposal that explicitly includes `groundtruth.db` in `target_paths`."
- The thread's audit lineage continues to be preserved by the bridge chain itself (this thread `-001` through eventual VERIFIED) plus the existing approval packet for `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`.

### F4 disposition: Runtime-created audit dirs replace tracked .gitkeep

**Removed from -003 (REVISED-1):**

- `.gtkb-state/mode-switches/.gitkeep` from `target_paths`.
- `.gtkb-state/mode-switches/pending/.gitkeep` from `target_paths`.
- `.gtkb-state/mode-switches/applied/.gitkeep` from `target_paths`.

**Added in REVISED-2:**

- `groundtruth_kb.mode_switch.audit.write_transaction_record()` and `groundtruth_kb.mode_switch.pending.defer_role_switch()` runtime-create their parent directories via `Path.mkdir(parents=True, exist_ok=True)` at first write. No tracked placeholder files.
- All tests under `platform_tests/groundtruth_kb/test_mode_switch_*.py` use `tmp_path` fixtures rather than referring to the live `.gtkb-state/` tree.
- The repository's `.gitignore` policy for `.gtkb-state/` is preserved as written; no governance-exception proposal is required.

## Slice 1 Scope (REVISED-2)

Seven deliverables (one more than REVISED-1's six, reflecting the new validation module + the moved hook call sites consolidated under shared functions):

1. **Pure derivation function** at `groundtruth_kb.mode_switch.derive.topology_from_role_map(role_map: dict) -> str`. Returns one of `{"single_harness", "multi_harness"}`. Single-harness iff exactly one harness ID's role-set contains BOTH `prime-builder` AND `loyal-opposition`. Refactored from `scripts/single_harness_bridge_dispatcher.py:_is_single_harness_topology_applicable` (byte-identical applicability semantics preserved).
2. **Validation module** at `groundtruth_kb.mode_switch.validation`. Three validator functions per F2 fix above. `ValidationResult` dataclass: `is_valid: bool`, `axis: str` ("role" / "bridge" / "session-state"), `errors: tuple[str, ...]`.
3. **Transaction component (immediate apply)** at `groundtruth_kb.mode_switch.transaction.apply_role_switch(harness_id_or_name, role, *, change_reason, applied_at=None) -> TransactionResult`. Calls all three validators FIRST (F2 fix). On any failure, raises `TransactionValidationError` with the failing axis; no state mutation. On all-pass, validates against `VALID_ROLES_FOR_WRITE`, resolves harness ID, writes audit record FIRST, then atomically writes `role-assignments.json` and `work-subject.json` with derived `topology_mode`.
4. **Pending-transaction queue** at `groundtruth_kb.mode_switch.pending`. Same shape as REVISED-1: `defer_role_switch`, `list_pending`, `apply_pending`. The shared apply-pending entry point is invoked from four call sites (F1 fix).
5. **Click CLI** at `gt mode set-role --harness <name|id> --role <prime-builder|loyal-opposition> [--reason <text>] [--defer-to-next-session]` plus `gt mode list-pending` and `gt mode apply-pending`. Exit codes per validation result.
6. **Pre-role-resolution apply-pending call sites (F1 fix)** in four files: both SessionStart hooks (`.codex/`, `.claude/`), the cross-harness trigger, and `session_self_initialization.py`. Each call site is wrapped in a fail-soft try/except: failure is logged but does NOT abort dispatch or startup.
7. **Topology derivation at startup** in `scripts/session_self_initialization.py` — AFTER pending is drained, derive topology from live role-map via `derive.topology_from_role_map(role_map)`. When derived disagrees with stored, emit a one-line corrective note in `### Configuration` and use derived. Plus `workstream_focus.save_state` writes derived topology.

## Implementation Plan

Ordered steps:

1. Create `groundtruth-kb/src/groundtruth_kb/mode_switch/` package with `__init__.py`, `derive.py`, `audit.py`, `transaction.py`, `pending.py`, `validation.py` (skeletons + docstrings). Unit-test `derive.topology_from_role_map` against fixtures from `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
2. Implement `validation.validate_role_artifact`, `validation.validate_bridge_artifact`, `validation.validate_session_state_artifact`. Test: valid → pass; missing file → fail; unreadable → fail; unparseable → fail; bridge INDEX with unknown status token → fail.
3. Implement `audit.write_transaction_record`. Runtime-creates `.gtkb-state/mode-switches/` via `mkdir(parents=True, exist_ok=True)`. Test: valid JSON; refuses overwrite; UTC timestamps; directory auto-created.
4. Implement `transaction.apply_role_switch`. Validators called FIRST. Test: each validator's failure axis raises `TransactionValidationError`; demotion semantics; atomic-write ordering; idempotency.
5. Implement `pending.defer_role_switch`, `pending.list_pending`, `pending.apply_pending`. Runtime-create `pending/` and `applied/` dirs. Test: defer writes pending file; apply-pending drains in chronological order; apply-pending moves applied → `applied/`; apply-pending leaves failed in `pending/` with error log; idempotent on empty queue.
6. Add `gt mode set-role`, `gt mode list-pending`, `gt mode apply-pending` Click subcommands to `groundtruth-kb/src/groundtruth_kb/cli.py`. Test via `CliRunner`.
7. Refactor `scripts/single_harness_bridge_dispatcher.py:_is_single_harness_topology_applicable` to call `derive.topology_from_role_map`. Regression-test against existing `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` and `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
8. **F1 fix call site 1**: `.codex/gtkb-hooks/session_start_dispatch.py` — add try-wrapped `apply_pending(project_root)` BEFORE the role-set resolution block at ~lines 354-371. Failure-log to `.gtkb-state/bridge-poller/dispatch-failures.jsonl`. Test: pending file present → applied before role resolution; observable evidence is the role-assignments.json mtime preceding `_bridge_dispatch_keyword_check()`'s resolved value.
9. **F1 fix call site 2**: `.claude/hooks/session_start_dispatch.py` — same shape at ~lines 360-377. Same fail-soft semantic. Same test.
10. **F1 fix call site 3**: `scripts/cross_harness_bridge_trigger.py` — add try-wrapped `apply_pending(project_root)` BEFORE recipient resolution. Test: pending file changes role-set → trigger dispatches to the updated recipient, not the stale one.
11. **F1 fix call site 4 (carried from REVISED-1)**: `scripts/session_self_initialization.py` — apply pending BEFORE topology derivation at the existing call site near line 4129. Idempotent against earlier drains by the dispatch hooks. Test: pending drained → topology derived from updated role-map.
12. Modify `scripts/workstream_focus.save_state` to write derived topology. Test: round-trip; legacy-stored mismatch is overwritten.
13. Update `.claude/rules/operating-role.md` to document `gt mode set-role` and `--defer-to-next-session`. Protected narrative artifact — collect a formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001` at edit time and route through `narrative-artifact-approval-gate.py`.
14. File implementation report; Codex VERIFIES against the full six-criterion spec-to-test mapping below.

(Steps from REVISED-1's "step 10: create project / link WI" REMOVED per F3 disposition.)

## Specification-Derived Test Plan

Mapping from `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` six acceptance criteria to executable tests (all paths under `platform_tests/**`):

| Acceptance criterion | Test file | Test function | Command |
|---|---|---|---|
| "There is a deterministic component or service API for bridge-configuration and operating-mode switch requests." | `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` | `test_apply_role_switch_returns_transaction_result` | `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py::test_apply_role_switch_returns_transaction_result -v` |
| "The component validates the requested switch against the authoritative role, bridge, and session-state artifacts before writing durable state." | `platform_tests/groundtruth_kb/test_mode_switch_validation.py` + `test_mode_switch_transaction.py` | `test_apply_role_switch_refuses_when_bridge_index_missing`, `test_apply_role_switch_refuses_when_bridge_index_unparseable`, `test_apply_role_switch_refuses_when_role_artifact_unparseable`, `test_apply_role_switch_refuses_when_session_state_artifact_unparseable`, `test_apply_role_switch_rejects_acting_prime_builder`, `test_apply_role_switch_rejects_unknown_role`, `test_apply_role_switch_rejects_unknown_harness` | `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py -v -k "refuses or rejects"` |
| "The component records enough transaction evidence to audit who requested the switch, what changed, when it was requested, and when it becomes effective." | `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` | `test_audit_record_contains_required_fields` | `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py::test_audit_record_contains_required_fields -v` |
| "Agent instructions direct agents to use the transaction component or service, not ad hoc direct edits, when switching bridge configurations or operating modes." | `platform_tests/scripts/test_operating_role_rule.py` | `test_operating_role_md_documents_gt_mode_set_role` | `python -m pytest platform_tests/scripts/test_operating_role_rule.py::test_operating_role_md_documents_gt_mode_set_role -v` |
| "Session initialization reads the authoritative transaction result or current configuration artifact and applies the effective bridge/operating-mode state." | `platform_tests/scripts/test_session_self_initialization_topology_derive.py` + `test_session_self_initialization_applies_pending_mode_switches.py` + `test_session_start_dispatch_drains_pending_before_role_resolution.py` + `test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py` | `test_startup_derives_topology_from_role_map`, `test_startup_overrides_stale_stored_topology_with_corrective_note`, `test_startup_applies_pending_transactions_before_topology_read`, `test_startup_moves_applied_pending_files_to_applied_subdir`, `test_codex_session_start_dispatch_drains_pending_before_role_resolution`, `test_claude_session_start_dispatch_drains_pending_before_role_resolution`, `test_cross_harness_trigger_drains_pending_before_recipient_resolution` | `python -m pytest platform_tests/scripts/test_session_self_initialization_topology_derive.py platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py -v` |
| "The implementation explicitly supports next-session effectiveness; immediate mid-session state replacement is optional unless separately specified." | `platform_tests/groundtruth_kb/test_mode_switch_pending.py` + `test_session_self_initialization_applies_pending_mode_switches.py` + `test_session_start_dispatch_drains_pending_before_role_resolution.py` | `test_defer_role_switch_writes_pending_file`, `test_apply_pending_drains_queue_in_chronological_order`, `test_apply_pending_moves_applied_to_applied_subdir`, `test_apply_pending_leaves_failed_in_pending_with_logged_error`, `test_cli_defer_to_next_session_writes_pending_not_current`, `test_next_session_initialization_applies_pending_and_state_matches_deferred_request`, `test_codex_session_start_dispatch_drains_pending_before_role_resolution`, `test_claude_session_start_dispatch_drains_pending_before_role_resolution` | (same as criterion #5 command + the pending-specific tests) |

Additional regression coverage:

| Risk | Test |
|---|---|
| Refactored `_is_single_harness_topology_applicable` changes dispatcher behavior | `python -m pytest platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -v` |
| Topology derivation breaks `single_harness_bridge_automation` | `python -m pytest platform_tests/scripts/test_single_harness_bridge_automation.py -v` |
| `workstream_focus.save_state` regression | `python -m pytest platform_tests/hooks/test_workstream_focus.py -v` |
| `session_self_initialization` startup-payload golden tests | `python -m pytest platform_tests/scripts/test_session_self_initialization.py -v` |
| SessionStart dispatch hooks themselves (existing coverage) | `python -m pytest platform_tests/scripts/test_session_start_dispatch.py -v` if extant, otherwise add a smoke-import test |

Final full-bank regression at implementation-report time:

```
python -m pytest platform_tests -q --tb=short
```

## Risk and Rollback

**Risks:**

- R1 (P1, carried from REVISED-1): Refactoring `_is_single_harness_topology_applicable` to call the new derivation function changes single-harness applicability under malformed role-map. Mitigation: byte-identical fixture parity test against `platform_tests/scripts/test_cross_harness_bridge_trigger.py`; pin the derived-function's empty/malformed-input return path to match the dispatcher's fail-closed semantic.
- R2 (P1, NEW): The F1 fix adds I/O at hook startup. A persistently failing apply-pending could surface noise in every session. Mitigation: fail-soft per-call-site (logs + continues); failed files remain in `pending/` for owner attention; `### Startup Notes` bullet surfaces the issue without aborting.
- R3 (P2, carried): Startup payload corrective note adds new lines that may break downstream parsers. Mitigation: notes as bullets under existing sections (`### Configuration`, `### Startup Notes`); check golden-tests for snapshot tolerance.
- R4 (P2, carried): `workstream_focus.save_state` writing derived topology could surprise callers wanting explicit topology control. Mitigation: documented in module docstring; future callers wanting topology control use `mode_switch.transaction`.
- R5 (P2, NEW): The F2 fix raises validation strictness. A bridge `INDEX.md` with a previously-tolerated minor parse defect would now refuse mode switches. Mitigation: the parse rule accepts the existing INDEX vocabulary; the tests use fixtures that include both well-formed and well-known edge-case shapes; if a real-world INDEX edge case is discovered, it is filed as a separate hygiene bridge rather than absorbed into this slice.
- R6 (P3): Audit-record directory growth. Mitigation: file naming pattern allows trivial archival; no retention enforcement in Slice 1 (deferred).

**Rollback procedure:**

All Slice 1 changes are additive (new module, new CLI subcommands, new test files) except modifications to four scripts/hooks and one rule file. Per change:

- `scripts/session_self_initialization.py` patches: revert two blocks (~10 lines).
- `scripts/workstream_focus.py` `save_state` patch: revert single block (~3 lines).
- `scripts/single_harness_bridge_dispatcher.py` shared-derivation refactor: revert function body to inline logic.
- `scripts/cross_harness_bridge_trigger.py` apply-pending patch: revert single block (~6 lines).
- `.codex/gtkb-hooks/session_start_dispatch.py` apply-pending patch: revert single block (~6 lines).
- `.claude/hooks/session_start_dispatch.py` apply-pending patch: revert single block (~6 lines).
- `.claude/rules/operating-role.md` documentation update: `git revert` on the implementation commit.

Audit records under `.gtkb-state/mode-switches/` are runtime-created and append-only; rollback does not delete them.

## Applicability Preflight

Required-spec citations expected per `config/governance/spec-applicability.toml`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` - always; bridge proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - content matches "Specification Links", "implementation proposal".
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - content matches "verification", "spec-to-test", "VERIFIED".
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - content matches "Agent Red", "applications/", "project root boundary".
- `GOV-STANDING-BACKLOG-001` - content mentions "work item" / "backlog" (in F3 disposition explanation); clause-scope clarification provided.

Expected advisory-spec citations:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

Preflight will be re-run after INDEX update; updated `packet_hash` captured in the review.

## Recommended Commit Type

`feat:` - the deterministic mode-switch CLI + pending-queue + multi-call-site SessionStart application + bridge-artifact validation is net-new capability. The diff stat is dominated by new module files (`groundtruth_kb/mode_switch/` package with six submodules) and new test files. `feat:` matches.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` with plain heading, flat bullets, no `###` sub-headings inside, no parenthetical heading qualifier.
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the prior AUQs plus this turn's standing autonomous-work direction.
- `target_paths` consistent with all planned writes; `groundtruth.db` removed (F3); `.gtkb-state/*.gitkeep` removed (F4); SessionStart hooks added (F1); validation module added (F2).
- `## Requirement Sufficiency` exactly one operative state.
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section present.
- explicit `## Changes from -003 (REVISED-1)` section with one subsection per F1/F2/F3/F4 finding.
- All paths under `E:\GT-KB\`.
- F1 fix: pending-transaction drain at four call sites (both SessionStart hooks + cross-harness trigger + session_self_initialization).
- F2 fix: validation module asserts role + bridge + session-state artifacts BEFORE durable write; three new fail-closed tests.
- F3 fix: MemBase mutation removed from slice; deferred to a separate project-authorization-scoped bridge thread.
- F4 fix: `.gtkb-state/*.gitkeep` removed; directories runtime-created.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
