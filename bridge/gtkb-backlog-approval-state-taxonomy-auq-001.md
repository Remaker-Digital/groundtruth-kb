NEW

# Implementation Proposal - Backlog Approval-State Taxonomy + AUQ Gate (WI-3271)

bridge_kind: prime_proposal
Document: gtkb-backlog-approval-state-taxonomy-auq
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-CAPTURE-COMMAND-APPROVAL-STATE-TAXONOMY
Project: PROJECT-GTKB-BACKLOG-CAPTURE-001
Work Item: WI-3271

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli.py", ".claude/rules/backlog-approval-state.md", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_cli_backlog.py"]

This NEW proposal lands the approval-state taxonomy on `work_items` and an AUQ-gated promotion path: a backlog item moves from `awaiting_approval` to `approved_for_implementation` only via owner AUQ evidence. Cites `GOV-STANDING-BACKLOG-001`.

## Claim

Add an `approval_state` enum column (or compatibility field) to `work_items` with values {`awaiting_approval`, `approved_for_implementation`, `deferred`, `rejected`}. New WIs default to `awaiting_approval`. State-promotion transition `awaiting_approval → approved_for_implementation` requires `change_reason` to cite an AUQ-evidence marker per the AUQ-only enforcement stack. Bridge proposal Write that cites a WI in `awaiting_approval` state is rejected by bridge-compliance-gate (sibling gate addition, deferred to follow-on slice if scope-tight).

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - source spec; taxonomy is the operationalization of "approved for implementation" the spec requires.
- `SPEC-AUQ-POLICY-ENGINE-001` - AUQ gate compliance.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - deterministic state machine.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; downstream gate hook.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" - explicit authorization.

## Requirement Sufficiency

Existing requirements sufficient. WI-3271 description + GOV-STANDING-BACKLOG-001 + SPEC-AUQ-* fully specify the surface.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. WI-3271 is a schema + state-machine feature; member of PROJECT-GTKB-BACKLOG-CAPTURE-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`. Review-packet inventory: IP-1 (schema) + IP-2 (state-machine validation) + IP-3 (rule doc) + IP-4 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-backlog-approval-state-taxonomy-auq-001.md`; new top entry prepended.

## Proposed Scope

### IP-1: Schema additions

In `groundtruth-kb/src/groundtruth_kb/db.py`, add nullable `approval_state TEXT` column to `work_items` (additive schema, idempotent migration). Default for new inserts: `awaiting_approval` when not provided. Allowed values: enum constant in module.

### IP-2: State-machine validation in `update_work_item()`

When `approval_state` mutates:
- `awaiting_approval → approved_for_implementation`: change_reason MUST contain regex `(?i)auq|askuserquestion|owner.approved` OR a `formal-artifact-approval` packet path reference; else raise ValueError.
- `awaiting_approval → deferred`: requires reason citing deferral context (no AUQ required).
- `awaiting_approval → rejected`: requires reason citing rejection rationale.
- Once `approved_for_implementation`, transitions back are forbidden (append-only intent preserved by versioning; promotion is one-way).

### IP-3: Rule documentation

In `.claude/rules/backlog-approval-state.md`, document the taxonomy + state-machine + AUQ-promotion contract. This is a narrative artifact; requires `narrative-artifact-approval` packet (the batch-2 packet covers it).

### IP-4: Tests + spec promotion

Tests + (no spec promotion: GOV-STANDING-BACKLOG-001 already implemented; this WI extends it but doesn't promote it).

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Default state on new insert | `test_insert_work_item_default_state_awaiting_approval` |
| Promotion without AUQ evidence raises | `test_promote_without_auq_evidence_raises` |
| Promotion with AUQ evidence succeeds | `test_promote_with_auq_evidence_succeeds` |
| Defer transition | `test_defer_transition_succeeds` |
| Reject transition | `test_reject_transition_succeeds` |
| Backwards transition forbidden | `test_approved_to_awaiting_forbidden` |
| Existing rows unchanged (null approval_state) | `test_existing_rows_grandfathered` |

Run: `python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_backlog.py -v`.

## Acceptance Criteria

- IP-1 schema landed; column present.
- IP-2 state-machine validation landed; 7 tests PASS.
- IP-3 rule doc landed with narrative-artifact-approval packet.
- Both preflights PASS.

## Risks / Rollback

- Risk: existing 127 open WIs land with NULL approval_state; the bridge-compliance-gate sibling check (deferred to follow-on) must grandfather NULL state. Mitigation: explicit NULL handling.
- Rollback: revert schema column (ALTER TABLE DROP); state-machine code reverts cleanly.

## Recommended Commit Type

`feat` - new schema + state-machine. ~90 LOC.
