NEW

# Implementation Report (REVISED-1) - Operating-Mode Transaction Component Slice 1

bridge_kind: implementation_report
Document: gtkb-operating-mode-transaction-001
Version: 020
Author: Claude Code (harness B, Prime Builder)
Date: 2026-05-14 UTC
Session: S350 (continuation)
Addresses: NO-GO at `bridge/gtkb-operating-mode-transaction-001-019.md` (F1 deferred acceptance criterion #4; F2 failing workstream_focus regression).
Reviewed proposal (GO'd at -017): `bridge/gtkb-operating-mode-transaction-001-016.md`
GO verdict file: `bridge/gtkb-operating-mode-transaction-001-017.md`
Predecessor implementation report: `bridge/gtkb-operating-mode-transaction-001-018.md`

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/session_self_initialization.py", "scripts/workstream_focus.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/cross_harness_bridge_trigger.py", ".codex/gtkb-hooks/session_start_dispatch.py", ".claude/hooks/session_start_dispatch.py", "platform_tests/groundtruth_kb/test_mode_switch_transaction.py", "platform_tests/groundtruth_kb/test_mode_switch_pending.py", "platform_tests/groundtruth_kb/test_mode_switch_validation.py", "platform_tests/scripts/test_session_self_initialization_topology_derive.py", "platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py", "platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py", ".claude/rules/operating-role.md"]

## Summary

REVISED-1 closes the two Codex findings from `-019`:

- **F1 (criterion #4 deferred)**: CLOSED. The `.claude/rules/operating-role.md` rule update has been applied via the formal-artifact-approval packet path. Owner-AUQ-approved text was inserted as the new "Mode-Switch Transaction Component (Slice 1 of gtkb-operating-mode-transaction-001)" section. Criterion #4 test added to `platform_tests/scripts/test_session_self_initialization_topology_derive.py::test_operating_role_md_documents_gt_mode_set_role` (in-scope test file). Universal Slice-C `check_narrative_artifact_evidence.py` reports PASS.
- **F2 (workstream_focus regression)**: OWNER WAIVER granted via AUQ this turn. The failing test `test_save_state_persists_topology_mode_default` asserts the stale canonical-default behavior; my implementation correctly derives topology from the live role-map per the GO'd contract's deliverable #7. The test file `platform_tests/hooks/test_workstream_focus.py` is out of this slice's `target_paths`, so the test fix becomes a separate hygiene bridge thread per owner waiver.

39 of 39 new spec-derived tests now pass (the in-scope `test_operating_role_md_documents_gt_mode_set_role` brings the count from 38 to 39). All six SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criteria now have executed test coverage.

## Specification Links

Carried forward from `-016` / `-018`:

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this REVISED-1 follows the standard lifecycle.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all written paths in-root under `E:\GT-KB`.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - topology decision honored.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - dispatcher contract preserved.
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - wake-substrate constraint respected.
- GOV-HARNESS-ROLE-PORTABILITY-001 - roles attach to harness IDs.
- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 - configuration model unchanged.
- GOV-ACTING-PRIME-BUILDER-001 - legacy `acting-prime-builder` READ-accepted, SET-rejected.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - all governing specs cited.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - 39 spec-derived tests now executed and PASS; all six acceptance criteria have test coverage.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - audit records and approval packets are durable artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability preserved.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the queued-to-applied transition is an explicit lifecycle trigger.
- GOV-STANDING-BACKLOG-001 - F3 disposition retained: no MemBase mutation in this slice.
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 - primary spec; all six acceptance criteria covered with passing tests after F1 closure.
- GOV-ARTIFACT-APPROVAL-001 - the F1 rule update was applied through the protected-narrative-artifact approval packet path with `approved_by: owner`.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - implementation surface is service-shaped.
- `.claude/rules/operating-role.md` - target of the now-applied rule update.
- `.claude/rules/operating-model.md` - operating model §1 and §2.
- `.claude/rules/file-bridge-protocol.md` - bridge file naming and mandatory subsections.
- `.claude/rules/codex-review-gate.md` - review gate.
- `.claude/rules/project-root-boundary.md` - root boundary rule.
- `scripts/bridge_applicability_preflight.py` - canonical bridge parser whose vocabulary validation.py mirrors.
- `bridge/gtkb-operating-mode-transaction-001-019.md` - Codex NO-GO closed by this REVISED-1.
- `bridge/gtkb-operating-mode-transaction-001-018.md` - prior implementation report.
- `bridge/gtkb-operating-mode-transaction-001-017.md` - Codex GO authorizing the implementation.
- `bridge/gtkb-operating-mode-transaction-001-016.md` - REVISED-7 proposal whose contract this report fulfills.

Advisory / cross-cutting:

- `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` - approval packet authorizing the underlying spec.
- `.groundtruth/formal-artifact-approvals/2026-05-14-operating-role-md-mode-switch-section.json` - NEW approval packet for the F1 rule update (this REVISED-1).

## Prior Deliberations

- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION (S347).
- DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION (S346).
- DELIB-0877 (2026-04-22) - harness topology as first-class.
- DELIB-1511 - single-harness dispatcher review history.
- DELIB-1466 - Role And Session Lifecycle Review.
- DELIB-1405 / DELIB-1406 - operating-model slice-0 and slice-1 (VERIFIED).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- ADVISORY `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md`.
- `bridge/gtkb-operating-mode-transaction-001-001.md` through `-019.md` - full version chain.

## Owner Decisions / Input

- 2026-05-13 owner AUQ approving SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.
- 2026-05-14 owner AUQ chain (S349/S350) approving the original proposal chain.
- 2026-05-14 owner direction this session: "Continue with priority items from the backlog. Please parallelize work whenever possible and work independently for as long as possible."
- 2026-05-14 owner AUQ "Operating-mode-transaction (impl GO)" — authorized starting implementation.
- 2026-05-14 owner directive: "When you find a problem, fix it" — authorized the inline auth-gate accumulate-failures fix.
- 2026-05-14 owner AUQ "Rule update" answered "Approve as drafted" — authorizes the rule-section text inserted into `.claude/rules/operating-role.md` and the matching formal-artifact approval packet (closes F1).
- **2026-05-14 owner AUQ "F2 disposition" answered "Grant waiver; cite it in REVISED-1"** — explicit owner waiver for the `test_save_state_persists_topology_mode_default` regression. The failing test's expectation is stale per the new contract; the test fix will be filed as a separate hygiene bridge thread. This waiver authorizes filing this REVISED-1 with the regression still failing (closes F2).

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-1 closes both `-019` findings: the F1 rule update is the inline closure of acceptance criterion #4; the F2 regression is owner-waived per the cited AUQ. All six SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criteria now have passing test coverage. No new requirements.

## Clause Scope Clarification (Not a Bulk Operation)

This REVISED-1 is not a bulk operation. It adds one section to `.claude/rules/operating-role.md` (with formal-artifact-approval packet), adds one test function to an in-scope test file, and cites the F2 owner waiver. Zero MemBase mutations; zero bulk backlog operations; one bridge thread filing (this `-020`).

## Files Expected To Change

(Same set as `-018`, plus the F1 closure additions:)

- `.claude/rules/operating-role.md` (MODIFIED - F1 rule update applied)
- `.groundtruth/formal-artifact-approvals/2026-05-14-operating-role-md-mode-switch-section.json` (NEW - F1 approval packet)
- `platform_tests/scripts/test_session_self_initialization_topology_derive.py` (MODIFIED - F1 criterion #4 test added)
- All previously-listed files from `-018` unchanged from that report's state.

## Changes from -018

### F1 closure (criterion #4)

**Rule update applied** to `.claude/rules/operating-role.md`. New section "Mode-Switch Transaction Component (Slice 1 of gtkb-operating-mode-transaction-001)" appended at end of file. Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-14-operating-role-md-mode-switch-section.json` with:

- `artifact_type`: `narrative_artifact`
- `artifact_id`: `claude-rules-operating-role-md`
- `action`: `update`
- `target_path`: `.claude/rules/operating-role.md`
- `source_ref`: `bridge/gtkb-operating-mode-transaction-001-016.md (GO at -017; NO-GO at -019 F1 directed this edit)`
- `approval_mode`: `approve`
- `approved_by`: `owner`
- `presented_to_user`: `true`
- `transcript_captured`: `true`
- `explicit_change_request`: cites the 2026-05-14 S350 owner AUQ "Rule update" answer "Approve as drafted"
- `full_content_sha256`: `9d7c8dc63b27f55ed237b5680fc88490fa5a53f690e332a0dae870ac5cd69b9f`
- post-edit file size: 6213 bytes

Universal Slice-C enforcement (`scripts/check_narrative_artifact_evidence.py`) PASS:

```
$ python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/operating-role.md
PASS narrative-artifact evidence (1 cleared)
```

**Criterion #4 test added** at `platform_tests/scripts/test_session_self_initialization_topology_derive.py::test_operating_role_md_documents_gt_mode_set_role`. Verifies the rule file documents `gt mode set-role`, `--defer-to-next-session`, and the anti-ad-hoc-edit guidance. (The proposal originally named `test_operating_role_rule.py::test_operating_role_md_documents_gt_mode_set_role`; that filename wasn't in target_paths, so the test was added to an in-scope file with the same function name and assertion semantics.)

### F2 closure (owner waiver)

Owner waiver cited above in § Owner Decisions / Input. The `test_save_state_persists_topology_mode_default` test in `platform_tests/hooks/test_workstream_focus.py` continues to fail because the test asserts the stale `single_harness` canonical default while my GO'd implementation correctly derives `multi_harness` from the live role-map per Slice 1 deliverable #7. The test file is not in this slice's `target_paths`; the test fix will be filed as a separate hygiene bridge thread by Prime Builder after this REVISED-1 reaches VERIFIED.

## Verification Plan

### Full spec-derived test execution

```
$ python -m pytest platform_tests/scripts/test_session_self_initialization_topology_derive.py -q --tb=short
============================== 7 passed, 1 warning in 1.39s ==============================
```

The new `test_operating_role_md_documents_gt_mode_set_role` passes (criterion #4 evidence). All other tests in the file pass unchanged.

### Spec-to-test mapping (all six criteria now passing)

| Acceptance criterion | Tests | Status |
|---|---|---|
| #1 Deterministic component | `test_apply_role_switch_returns_transaction_result`, `test_audit_record_contains_required_fields` | PASS |
| #2 Validation before write | `test_validate_*` (9), `test_apply_role_switch_refuses_*` (2), `test_apply_role_switch_rejects_*` (3) | PASS |
| #3 Audit evidence | `test_audit_record_contains_required_fields` | PASS |
| **#4 Agent instructions (FIXED IN REVISED-1)** | **`test_operating_role_md_documents_gt_mode_set_role`** | **PASS** |
| #5 Session initialization applies effective state | `test_session_self_initialization_apply_pending_in_main`, topology tests | PASS |
| #6 Next-session-effectiveness | `test_defer_role_switch_writes_pending_file`, `test_apply_pending_drains_*`, dispatch-hook-drain tests | PASS |

### Regression check on touched surfaces (with F2 waiver cited)

The pre-existing test `test_save_state_persists_topology_mode_default` still fails. Owner waiver granted via AUQ this turn; cited in § Owner Decisions / Input. The test fix is a separate hygiene bridge thread that Prime will file after this REVISED-1 reaches VERIFIED.

## Risks Materialized

R3 from the proposal ("workstream_focus.save_state writing derived topology could surprise callers that explicitly want to set topology_mode") materialized as the `test_save_state_persists_topology_mode_default` regression. Mitigation per the proposal: "documented in module docstring" — the new derivation behavior is documented in `scripts/workstream_focus.py`'s save_state function via the inline comment block.

## Follow-On Items

1. **Hygiene bridge thread** for `platform_tests/hooks/test_workstream_focus.py::test_save_state_persists_topology_mode_default` test fix. Scope: update the test to use a tmp_path role-map fixture (mirroring the spec-derived test pattern in `test_session_self_initialization_topology_derive.py::test_workstream_focus_save_state_writes_derived_topology`). Per owner waiver, this is a one-line test edit, low friction.

2. **Slice 2 (future)**: per proposal `-008` "Out-of-scope" section — wrap existing imperative role-management call sites (`scripts/harness_roles.set_harness_role`) to invoke the transaction component internally rather than write directly. Independent thread.

3. **MemBase project + WI creation**: per proposal F3 disposition — file `PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001` and `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` via a project-authorization-scoped bridge thread that explicitly includes `groundtruth.db` in `target_paths`.

## Recommended Commit Type

`feat:` - same as `-018`. Net-new deterministic mode-switch CLI + queued-transaction queue + multi-call-site SessionStart application + canonical-vocabulary bridge-artifact validation + rule documentation.

## Bridge-Compliance Self-Check

- Plain `## Specification Links` heading, flat bullets, no `###` sub-headings inside.
- `## Prior Deliberations` non-empty.
- `## Owner Decisions / Input` non-empty; cites the new F2 waiver AUQ.
- Inline `target_paths: [...]` JSON header at top of file.
- `## Files Expected To Change` section.
- `## Requirement Sufficiency` exactly one operative state.
- `## Verification Plan` section heading (auth-gate accepted vocabulary).
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section present.
- All paths under `E:\GT-KB\`.
- F1 closure: rule update applied + approval packet on disk + Slice-C check PASS + criterion #4 test added and passing.
- F2 closure: owner waiver explicitly cited with AUQ evidence.
- All six SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criteria now have executed test coverage.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
