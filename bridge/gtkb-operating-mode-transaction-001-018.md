NEW

# Implementation Report - Operating-Mode Transaction Component Slice 1

bridge_kind: implementation_report
Document: gtkb-operating-mode-transaction-001
Version: 018
Author: Claude Code (harness B, Prime Builder)
Date: 2026-05-14 UTC
Session: S350 (continuation)
Reviewed proposal (GO'd at -017): `bridge/gtkb-operating-mode-transaction-001-016.md`
GO verdict file: `bridge/gtkb-operating-mode-transaction-001-017.md`

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/session_self_initialization.py", "scripts/workstream_focus.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/cross_harness_bridge_trigger.py", ".codex/gtkb-hooks/session_start_dispatch.py", ".claude/hooks/session_start_dispatch.py", "platform_tests/groundtruth_kb/test_mode_switch_transaction.py", "platform_tests/groundtruth_kb/test_mode_switch_pending.py", "platform_tests/groundtruth_kb/test_mode_switch_validation.py", "platform_tests/scripts/test_session_self_initialization_topology_derive.py", "platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py", "platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py", ".claude/rules/operating-role.md"]

## Summary

Slice 1 implementation complete except for the protected-narrative rule update (deferred pending owner-AUQ approval packet — see § Deferred Items). All 38 new tests pass. Six core mode_switch modules delivered; four apply_pending call sites wired before role/recipient resolution; the single-harness dispatcher refactored to delegate topology to `derive.topology_from_role_map`; `workstream_focus.save_state` now derives `topology_mode` from the live role map; `gt mode set-role` / `list-pending` / `apply-pending` CLI subcommands added to the gt CLI.

## Specification Links

Carried forward from `-016` (REVISED-7), substantively GO'd at `-017`:

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this report follows the standard lifecycle.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all written paths in-root under `E:\GT-KB`.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - topology decision honored.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - dispatcher contract preserved.
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - wake-substrate constraint respected.
- GOV-HARNESS-ROLE-PORTABILITY-001 - roles attach to harness IDs.
- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 - configuration model unchanged.
- GOV-ACTING-PRIME-BUILDER-001 - legacy `acting-prime-builder` READ-accepted, SET-rejected in transaction.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - all governing specs cited.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - 38 spec-derived tests executed and PASS.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - audit records under `.gtkb-state/mode-switches/` are durable artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability preserved.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the queued-to-applied transition is an explicit lifecycle trigger materialized via `pending.apply_pending`.
- GOV-STANDING-BACKLOG-001 - F3 disposition retained: no MemBase mutation in this slice.
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 - primary spec; five of six acceptance criteria covered by passing tests (see § Verification Plan Execution); criterion #4 (agent instructions documentation) is the deferred item below.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - implementation moves recurring mode-switch friction behind the deterministic transaction component.
- `.claude/rules/operating-role.md` - target of the deferred rule update.
- `.claude/rules/operating-model.md` - operating model §1 and §2.
- `.claude/rules/file-bridge-protocol.md` - bridge file naming + mandatory subsections.
- `.claude/rules/codex-review-gate.md` - review gate.
- `.claude/rules/project-root-boundary.md` - root boundary rule.
- `scripts/bridge_applicability_preflight.py` - canonical bridge parser; validation.py mirrors its status vocabulary.
- `bridge/gtkb-operating-mode-transaction-001-017.md` - Codex GO authorizing this implementation.
- `bridge/gtkb-operating-mode-transaction-001-016.md` - REVISED-7 proposal whose contract this report fulfills.

Advisory / cross-cutting:

- `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` - approval packet authorizing the underlying spec.

## Prior Deliberations

- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION (S347).
- DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION (S346).
- DELIB-0877 (2026-04-22) - harness topology as first-class.
- DELIB-1511 - single-harness dispatcher review history.
- DELIB-1405 / DELIB-1406 - operating-model slice-0 and slice-1 (VERIFIED).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - addressed by this implementation.
- ADVISORY `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md` - records the role switch that motivated this thread.
- `bridge/gtkb-operating-mode-transaction-001-001.md` through `-017.md` - complete version chain (NEW → NO-GO → REVISED-1 through REVISED-7 → multiple GO/NO-GO cycles → final GO@017).

## Owner Decisions / Input

- 2026-05-13 owner AUQ approving SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.
- 2026-05-14 owner AUQ chain (S349/S350) approving the original proposal chain.
- 2026-05-14 owner direction this session: "Continue with priority items from the backlog. Please parallelize work whenever possible and work independently for as long as possible."
- 2026-05-14 owner AUQ "Operating-mode-transaction (impl GO)" — authorized starting implementation.
- 2026-05-14 owner directive: "When you find a problem, fix it" — authorized the inline auth-gate accumulate-failures fix to `scripts/implementation_authorization.py` (the owner applied that change manually, unblocking the seven-version REVISED chain to reach this report).

No new owner decision required for review of this report. The deferred rule update awaits a separate AUQ (see § Deferred Items).

## Requirement Sufficiency

Existing requirements sufficient.

This report executes the GO'd proposal at `-016` (REVISED-7) and `-017` (GO). The five-of-six acceptance criteria coverage is complete and tested; the sixth (criterion #4: agent-instructions documentation) is mechanically straightforward but requires an owner-approval packet that is out of session-budget scope (see § Deferred Items).

## Clause Scope Clarification (Not a Bulk Operation)

This report covers one implementation slice with substantively-unchanged target_paths. Zero MemBase mutations (F3 disposition retained); zero bulk backlog operations; one bridge thread close-out filing (this `-018`).

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (MODIFIED — gt mode subcommands)
- `scripts/session_self_initialization.py` (MODIFIED — apply_pending call before topology derivation)
- `scripts/workstream_focus.py` (MODIFIED — save_state derives topology_mode)
- `scripts/single_harness_bridge_dispatcher.py` (MODIFIED — delegate to derive.topology_from_role_map)
- `scripts/cross_harness_bridge_trigger.py` (MODIFIED — apply_pending call before topology check + recipient resolution)
- `.codex/gtkb-hooks/session_start_dispatch.py` (MODIFIED — apply_pending call before role-resolution)
- `.claude/hooks/session_start_dispatch.py` (MODIFIED — apply_pending call before role-resolution)
- `platform_tests/groundtruth_kb/test_mode_switch_validation.py` (NEW — 10 tests)
- `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` (NEW — 8 tests)
- `platform_tests/groundtruth_kb/test_mode_switch_pending.py` (NEW — 6 tests)
- `platform_tests/scripts/test_session_self_initialization_topology_derive.py` (NEW — 6 tests)
- `platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py` (NEW — 2 tests)
- `platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py` (NEW — 4 tests)
- `platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py` (NEW — 2 tests)

## Verification Plan

(Section heading retained per auth gate's accepted vocabulary.)

### Spec-derived test execution

```
$ python -m pytest \
    platform_tests/groundtruth_kb/test_mode_switch_validation.py \
    platform_tests/groundtruth_kb/test_mode_switch_transaction.py \
    platform_tests/groundtruth_kb/test_mode_switch_pending.py \
    platform_tests/scripts/test_session_start_dispatch_drains_pending_before_role_resolution.py \
    platform_tests/scripts/test_cross_harness_bridge_trigger_drains_pending_before_recipient_resolution.py \
    platform_tests/scripts/test_session_self_initialization_topology_derive.py \
    platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py \
    -q --tb=short
============================== 38 passed, 1 warning in 1.94s ==============================
```

### Spec-to-test mapping

| Acceptance criterion | Tests | Status |
|---|---|---|
| #1: Deterministic component or service API for mode switches | `test_apply_role_switch_returns_transaction_result`, `test_audit_record_contains_required_fields` | PASS |
| #2: Validates requested switch against role + bridge + session-state artifacts before durable write | `test_validate_role_artifact_*` (3), `test_validate_bridge_artifact_*` (4 incl. WITHDRAWN regression), `test_validate_session_state_artifact_*` (2), `test_apply_role_switch_refuses_*` (2), `test_apply_role_switch_rejects_*` (3) | PASS |
| #3: Audit evidence (who, what, when, effective-when) | `test_audit_record_contains_required_fields` | PASS |
| #4: Agent instructions direct agents to use the component (not ad-hoc edits) | Deferred — see § Deferred Items | DEFERRED |
| #5: Session initialization applies the effective bridge/operating-mode state | `test_session_self_initialization_apply_pending_in_main`, `test_session_self_initialization_imports_apply_pending`, `test_topology_*` (5) | PASS |
| #6: Next-session-effectiveness; immediate mid-session apply is optional | `test_defer_role_switch_writes_pending_file`, `test_apply_pending_drains_and_archives`, `test_next_session_initialization_applies_pending_and_state_matches_deferred_request`, `test_apply_pending_leaves_failed_in_pending_with_logged_error`, `test_session_start_dispatch_apply_pending_precedes_role_resolution` (codex + claude), `test_cross_harness_trigger_apply_pending_precedes_topology_check` | PASS |

### Regression check on touched surfaces

```
$ python -m pytest platform_tests/scripts/test_single_harness_bridge_dispatcher.py \
                    platform_tests/scripts/test_cross_harness_bridge_trigger.py \
                    platform_tests/hooks/test_workstream_focus.py \
                    -q --tb=line
============= 1 failed, 78 passed, 3 skipped, 1 warning in 5.69s ==============
```

One regression: `test_save_state_persists_topology_mode_default` in `platform_tests/hooks/test_workstream_focus.py`. The test asserts that `save_state` writes the canonical `single_harness` default. My change correctly derives the topology from the live role map per the GO'd proposal (REVISED-3 deliverable 7: "workstream_focus.save_state topology recompute — write derived topology rather than the canonical default"). The live workspace's role-map has two singleton harness records, which my `derive.topology_from_role_map` correctly maps to `multi_harness`. The test's expectation predates the proposal-defined behavior and is now incompatible with the spec.

Disposition: this test needs to be updated to use a tmp_path role-map fixture (mirroring the spec-derived test pattern). The test file `platform_tests/hooks/test_workstream_focus.py` is NOT in this slice's `target_paths`, so the update is out-of-scope for this report and should be filed as a separate hygiene bridge thread (or addressed at slice-2 if a future slice expands scope).

This regression was anticipated by the proposal's Risk R3: "workstream_focus.save_state writing derived topology could surprise callers that explicitly want to set topology_mode." Mitigation per the proposal: "documented in module docstring." The docstring has been updated to reflect the derivation behavior.

## Deferred Items

### Rule update: `.claude/rules/operating-role.md`

Per IP-step 13 in `-008` (carried through `-016`): "Update `.claude/rules/operating-role.md` to document `gt mode set-role` and `--defer-to-next-session` as the canonical write paths. Protected narrative artifact — formal-artifact-approval packet collected at implementation time per `GOV-ARTIFACT-APPROVAL-001`."

Status: NOT applied in this session. The protected-narrative-artifact-approval gate requires a packet with `approved_by: owner` bound to the exact post-edit content via SHA256, which in turn requires an AUQ presenting the proposed text. Filing the AUQ-and-apply round is straightforward but consumed session-budget pressure prevented completing it cleanly this turn.

Proposed text to add to `.claude/rules/operating-role.md` (would be presented to owner via AUQ when this slice's follow-on round picks up):

> ## Mode-Switch Transaction Component (Slice 1 of gtkb-operating-mode-transaction-001)
>
> Agents MUST use the deterministic mode-switch transaction component for role/topology changes rather than ad-hoc direct edits to `harness-state/role-assignments.json`. The CLI surface is `gt mode set-role --harness <id|name> --role <prime-builder|loyal-opposition> [--reason <text>] [--defer-to-next-session]`. `--defer-to-next-session` queues the transaction in `.gtkb-state/mode-switches/pending/` for SessionStart-time application; the default is immediate apply. Direct edits to `harness-state/role-assignments.json` are still possible but bypass the validators (role/bridge/session-state artifact validation) and the audit-trail record; the transaction component is the supported path.

This text would be inserted as a new section after the existing role-assignment guidance.

Codex disposition options:
1. NO-GO this report pending the rule update + matching test (`platform_tests/scripts/test_operating_role_rule.py::test_operating_role_md_documents_gt_mode_set_role`) — I would then file the AUQ + apply the rule edit + write the new test + re-file the report.
2. VERIFIED the report with the rule update tracked as an open follow-on item — Codex could file a NEW bridge entry for the deferred work, or it can become Slice 1.5.
3. Owner intervention — owner can apply the rule update manually (similar to the auth-gate fix this session) and signal Codex to VERIFIED.

## Implementation Notes

### Authorization re-activation friction

During implementation, the active authorization packet was repeatedly displaced by parallel-window auth packet mints for other threads (visible at `.gtkb-state/implementation-authorizations/current.json`). Each displacement required a `python scripts/implementation_authorization.py activate --bridge-id gtkb-operating-mode-transaction-001` to restore my packet. The named-cache pattern at `.gtkb-state/implementation-authorizations/by-bridge/` made re-activation possible without re-deriving the packet, but the pattern of automatic displacement is itself a deterministic-services-principle observation worth surfacing for a follow-on (multi-active-packet semantics, or packet-scoping by tool-invoking-session).

### Auth-gate accumulate-failures fix

Per owner directive 2026-05-14 S350 "When you find a problem, fix it," the gate's serial-check architecture in `scripts/implementation_authorization.py` was repaired to accumulate all format failures in a single pass rather than fail-fast. The owner applied the patch manually (the gate's own `PROTECTED_PREFIXES` precluded me from editing `scripts/implementation_authorization.py` from within this session's authorization scope). The fix is now in production and benefits future bridge-cycle iterations across all threads.

## Recommended Commit Type

`feat:` - net-new deterministic mode-switch CLI plus queued-transaction queue plus multi-call-site SessionStart application plus canonical-vocabulary bridge-artifact validation. The diff stat is dominated by new module files and new test files. `feat:` matches.

## Bridge-Compliance Self-Check

- Plain `## Specification Links` heading, flat bullets, no `###` sub-headings inside, no parenthetical heading qualifier.
- `## Prior Deliberations` non-empty.
- `## Owner Decisions / Input` non-empty.
- Inline `target_paths: [...]` JSON header at top of file.
- `## Files Expected To Change` section listing the same paths (redundant coverage of auth-gate fallback).
- `## Requirement Sufficiency` exactly one operative state.
- `## Verification Plan` section heading (auth-gate accepted vocabulary).
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section present.
- All paths under `E:\GT-KB\`.
- 38 new spec-derived tests PASS.
- 1 documented regression on a pre-existing test that's now incompatible with the spec-defined behavior (out-of-scope for this slice).
- 1 deferred item (rule update) clearly identified with disposition options.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
