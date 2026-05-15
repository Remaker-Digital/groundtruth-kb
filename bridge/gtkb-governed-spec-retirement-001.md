# Implementation Proposal - Governed Spec Retirement

bridge_kind: implementation_proposal
Document: gtkb-governed-spec-retirement
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S349 (continuation)
target_paths: ["scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_retirement_workflow.py", "config/governance/governed-spec-retirement.toml", "groundtruth.db"]

## Claim

Implement governed spec retirement as the follow-on to Slice 3 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE. Slice 3 REVISED-4 (`bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-011.md`) defers the `retire` decision path to this bridge thread per owner AskUserQuestion (2026-05-14 UTC, "Defer retire to follow-on bridge").

The Slice 3 implementation makes `apply-decision --decision retire` refuse with an explicit governance-gap error. This thread restores the `retire` path through the governed `db.update_specification()` API plus a formal-artifact-approval packet at execution time, replacing the raw-SQL `INSERT INTO specifications` that Codex's NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-010.md` (FINDING-F1) correctly flagged as unsafe.

Detailed scope is intentionally lightweight at this NEW filing because the specific governed-retirement design (e.g., which DB API methods to invoke, what additional packet fields beyond the existing formal-artifact-approval schema are required, what test coverage to add for governance edge cases) will be refined during the proposal lifecycle in dialogue with Codex. The thread's purpose at NEW is to durably mark the deferred-but-tracked work in the bridge audit trail.

## Why Now

The S349 self-diagnostic surface (`INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM`) identified 1,463 currently-failing assertions, of which the `chronic_noise` category needs the `retire` decision path to clear. Owner has chosen to defer the governed implementation rather than ship the raw-SQL path; this thread is that deferred work made durable.

The Slice 3 REVISED-4 `apply-decision` refusal message names this thread by ID (`gtkb-governed-spec-retirement-001`). Codex's NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-012.md` (FINDING-F1) correctly required this bridge thread to exist before Slice 3 REVISED-5 can receive `GO`.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed; this is a NEW filing under the standard lifecycle. `bridge/INDEX.md` will be updated with the `NEW: bridge/gtkb-governed-spec-retirement-001.md` entry at the top of the new document's version list.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - target paths inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites the governing specifications.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the verification plan will map governing specs to tests at the REVISED-1 stage; this NEW filing carries the linkage forward as a placeholder commitment.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - this thread completes the retirement-decision path for chronic-noise assertions identified under SPEC-1662.
- GOV-15 TEST-FIX-GATE - retirement decisions for chronic-noise assertions require owner AUQ; this thread preserves the gate while adding governance-compliant execution.
- GOV-ARTIFACT-APPROVAL-001 - the governed-retirement path requires formal-artifact-approval packet evidence; the implementation will validate that packet shape per the spec.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - extended (via GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001) for the canonical-terminology surface; this thread reuses the formal-artifact path for spec-status mutations.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - retirement is a spec lifecycle transition; this thread implements the trigger.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - retirement decisions and their evidence are durable artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - artifact-oriented development; retirement-decision artifacts (packets + post-retirement spec rows) preserve traceability across the implementation lineage.
- GOV-STANDING-BACKLOG-001 - the thread creates one tracking WI for itself at REVISED-1.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - retirement-execution should be deterministic service; this thread builds toward that.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - the Slice 3 GO under which the deferral scope was established.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-010.md - Codex NO-GO on Slice 3 implementation report; FINDING-F1 motivates this thread.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-011.md - Slice 3 REVISED-4 that defers `retire` to this thread.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-012.md - Codex NO-GO on Slice 3 REVISED-4 requiring this thread to exist.

Advisory / cross-cutting:

- `.claude/rules/codex-review-gate.md` - bridge gate that this thread's tests will satisfy.
- `.claude/rules/file-bridge-protocol.md` - the proposal protocol followed.
- `tools/knowledge-db/db.py` - the `db.update_specification()` API to be invoked by the governed `_retire_spec` replacement.
- `.groundtruth/formal-artifact-approvals/` - the directory where governed-retirement approval packets will live.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-14 UTC).
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "Defer retire to follow-on bridge (Recommended)" - chose this thread as the deferred-implementation path.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "Slice 4 REVISED-1 (Recommended)" - chose Slice 4 as the next-priority work (this thread is sequenced after Slice 4 land).
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- DELIB-1469 - GT-KB Self-Measurement and Self-Improvement Advisory.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.

## Owner Decisions / Input

- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "How should REVISED-1 of Slice 3 handle the `retire` mutation path (Codex F1)?" Answer: "Defer retire to follow-on bridge (Recommended)". Authorizes this thread's filing.

No additional owner decision is required before review at NEW.

## Requirement Sufficiency

Existing requirements sufficient.

This thread does not propose new requirements. It implements the governed-retirement path that Slice 3 originally scoped but did not safely deliver. The governing specs (SPEC-1662 / GOV-18, GOV-15, GOV-ARTIFACT-APPROVAL-001) are unchanged.

## Clause Scope Clarification (Not a Bulk Operation)

This thread is not a bulk operation against the standing backlog. It creates exactly one tracking `work_item` (origin='hygiene', source_spec_id='SPEC-1662') at REVISED-1, identical in shape to the tracking WIs created by other GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE slices. No formal-artifact-approval packet is required for the proposal/report files; the governed-retirement code path that this thread implements will produce its OWN formal-artifact-approval packets at execution time, per spec.

## Proposed Scope (Outline; refined at REVISED-1)

- **IP-1: Reintroduce `_retire_spec` using `db.update_specification()`.** Replace the removed `_retire_spec` function in `scripts/assertion_retirement_workflow.py` with a governed implementation that:
  1. Validates an extended approval packet that includes the formal-artifact-approval schema (`artifact_type='spec_status_mutation'` or equivalent; final field set decided at REVISED-1).
  2. Reads current spec state via the KnowledgeDB API.
  3. Computes the post-mutation row with `status='retired'`, `changed_by='assertion-retirement-workflow@2.0'`, and the cited approval-packet hash.
  4. Invokes `db.update_specification()` (or the equivalent governed API method) to apply the mutation.
  5. Refuses if the packet is missing required fields, expired, hash-mismatched, or not owner-approved.
- **IP-2: Update `apply-decision`.** Change the retire-refused error to invoke the new governed path; on success, write the decision record exactly as the accept/keep paths do.
- **IP-3: Tests.** Add governance-edge-case tests: missing packet, malformed packet, target-spec mismatch, expired packet, hash mismatch, non-owner approver. Plus a positive-path test that asserts `db.update_specification()` was invoked and the spec row carries the expected new state.
- **IP-4: Optional config.** `config/governance/governed-spec-retirement.toml` (if needed) for retirement-specific gate parameters (e.g., max packet age, required approver identity). Decided at REVISED-1.
- **IP-5: Tracking work_item.** Insert one `work_items` row in MemBase for this thread's implementation lineage.

The above outline is the NEW-stage commitment; REVISED-1 will tighten the scope after Codex's first review.

## Tests (placeholder for REVISED-1)

To be itemized at REVISED-1. Coverage targets:

- Positive path: `apply-decision --decision retire` with a valid packet promotes the spec to retired and writes the decision record.
- Negative paths: packet missing, malformed, expired, mismatched assertion_id, mismatched spec_id, non-owner approver, hash mismatch.
- Regression: the existing 15 retirement-workflow tests continue to pass (refused path remains for invalid input).

## Verification Plan

For Loyal Opposition verification of the eventual post-implementation report:

1. `python -m pytest platform_tests/scripts/test_assertion_retirement_workflow.py -v` - all tests including new governance-edge-case tests PASS.
2. End-to-end demonstration: a valid packet promotes a fixture spec to retired through the workflow; reads from MemBase confirm the new state.
3. End-to-end demonstration: each invalid-packet case is refused with the documented error.
4. Targeted Ruff on touched files clean.
5. Both mandatory bridge preflights pass against the implementation report.

## Risks and Rollback

- Risk: `db.update_specification()` API may not have the exact shape needed for status='retired' transitions. Mitigation: REVISED-1 examines the API and proposes adjustments if needed (either to `db.py` or to the workflow's wrapping logic).
- Risk: formal-artifact-approval packet schema may need extension for `spec_status_mutation` artifact type. Mitigation: REVISED-1 specifies the exact field set after reading the existing schema definitions.
- Rollback: revert the governed `_retire_spec` reintroduction; the refused-retire behavior from Slice 3 REVISED-4 remains as the safe default.

## Sequenced Dependencies

This thread is sequenced AFTER Slice 4 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE lands (auth-packet thrashing fix). Implementing this thread under the current packet-thrashing condition would be repeatedly disrupted by parallel `begin --bridge-id` calls overwriting the active packet. After Slice 4's named-packet cache + activate substrate is in place, this thread's implementation proceeds safely.

## Recommended Commit Type

`feat:` - governed-retirement is a net-new capability replacing the deferred (refused) retire path with a safety-compliant implementation.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` with flat bullets; no `###` sub-headings inside; no parenthetical heading.
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the AskUserQuestion exchanges.
- `target_paths` consistent with all planned writes.
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type`.
- `## Clause Scope Clarification (Not a Bulk Operation)` section.
- All paths under `E:\GT-KB`.
- NEW filing acknowledged; full scope refinement deferred to REVISED-1 per standard bridge-protocol practice.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
