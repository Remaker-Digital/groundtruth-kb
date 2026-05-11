NEW

# Peer Solution Owner Gate DCL - NEW

bridge_kind: implementation_proposal
Document: gtkb-peer-solution-owner-gate-dcl
Version: 001 (NEW; Slice 1 — candidate DCL filing)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` (Codex GO at `-004`).

## Claim

This proposal authors a **candidate DCL for human approval gates mapping to GT-KB owner-action protocol** as MemBase row `DCL-PEER-SOLUTION-OWNER-GATE-001` (status `candidate` -> `specified` upon Codex GO + owner approval-packet). The DCL formalizes the machine-checkable constraint that peer-solution adoption decisions must route through the established `AskUserQuestion` (AUQ) channel, NOT inferred-action shortcuts.

The Slice-0 GO explicitly named this as follow-on (c): "Human-gate candidate DCL proposal" (`bridge/gtkb-peer-solution-advisory-loop-conversion-003.md:138`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/prime-builder-role.md`
- `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`

## Prior Deliberations

- `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` - parent Slice-0 REVISED-1.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-004.md` - parent Slice-0 GO.
- `bridge/gtkb-peer-solution-advisory-loop-procedure-001.md` - sibling Slice-1 follow-on (procedure document).
- `bridge/gtkb-peer-solution-workflow-contract-adr-001.md` - sibling Slice-1 follow-on (workflow-contract ADR).
- `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md` - source LO advisory.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED) - AUQ-only enforcement precedent; this DCL extends to the peer-solution adoption gate.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog ... Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this Slice-1 follow-on filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the formal-artifact-approval packet for `DCL-PEER-SOLUTION-OWNER-GATE-001` MemBase insertion is produced at implementation time per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`.

## Scope (Slice 1)

### IN SCOPE

**IP-1: Author `DCL-PEER-SOLUTION-OWNER-GATE-001` as a MemBase row** with `type='design_constraint'`, `status='specified'`. DCL contents:

1. **Constraint statement:** "Peer-solution adoption decisions (adopt / adapt / reject / defer / monitor classifications per the peer-solution-advisory-loop procedure) MUST be collected via `AskUserQuestion` when they cross the in-scope decision class threshold defined in `prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel."
2. **In-scope decision classes for this DCL:** (a) classifying a peer-solution recommendation as `adopt` (Prime files implementation proposal); (b) classifying as `adapt` (Prime files modified implementation proposal); (c) classifying as `reject` with specification impact; (d) deferring with a defer-trigger condition. The `monitor` and `reject-with-no-spec-impact` classifications are NOT in scope (they're observational, not decision-class).
3. **Assertions field:** machine-checkable predicates the DCL enforces. Example pattern: `assert (peer_solution_classification in {"adopt", "adapt", "reject_with_spec_impact", "defer"}) -> auq_evidence_present`.
4. **Enforcement mode:** `advisory` initially (Phase 1 advisory pilot per `GOV-20` workflow); promotion to `blocking` deferred to future bridge thread once empirical adoption data is available.
5. **Rationale:** preserves `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded-to-decisions; aligns with the existing AUQ-only enforcement stack.

**IP-2: Approval packet for `DCL-PEER-SOLUTION-OWNER-GATE-001`.** At implementation time, Prime authors the approval packet at `.groundtruth/formal-artifact-approvals/<date>-dcl-peer-solution-owner-gate-001.json`.

**IP-3: MemBase regression test.** Add `platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py` asserting the DCL row exists with required fields (constraint / assertions / enforcement_mode='advisory'). Public `groundtruth_kb.db` API; no direct SQLite access.

### OUT OF SCOPE

- Procedure document (sibling thread).
- Workflow-contract ADR (sibling thread).
- Promotion from `advisory` to `blocking` enforcement (deferred to future bridge thread with empirical data).
- Runtime AUQ gate enforcement code (existing `owner-decision-tracker.py` already covers the AUQ-only floor for the general decision class; peer-solution-specific routing is documented but not separately enforced in this slice).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-owner-gate-dcl` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-owner-gate-dcl` - exit 0 expected.

### Implementation tests

3. `pytest platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py -v` - PASS expected (IP-3).

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + Step 3. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | DCL MemBase row + approval packet inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | Approval packet per IP-2. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Approval-gate hook validates DCL insert. |
| SPEC-AUQ-POLICY-ENGINE-001 | This DCL extends the AUQ-only enforcement to the peer-solution adoption gate. |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | DCL's classification vocabulary is deterministic (no LLM classifier required). |
| `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded | DCL preserves the owner role as decisions, not inferred actions. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS on `-001`.
- [ ] Codex GO on this Slice-1 NEW.
- [ ] `DCL-PEER-SOLUTION-OWNER-GATE-001` inserted in MemBase with constraint / assertions / enforcement_mode='advisory'.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-dcl-peer-solution-owner-gate-001.json` produced at implementation time.
- [ ] `platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py` PASS.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-peer-solution-owner-gate-dcl-001.md` with a corresponding `bridge/INDEX.md` entry (insert at top of doc list); no prior versions are deleted or rewritten — the version chain is append-only per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 follow-on adds one new bridge entry. NOT a bulk operation.

- **inventory artifact:** IP-1 to IP-3 enumeration above.
- **review packet:** this `-001` NEW.
- **DECISION DEFERRED markers:** promotion from `advisory` to `blocking` is deferred to a future bridge thread; runtime enforcement code is out of scope.
- **formal-artifact-approval packet:** produced at implementation time per IP-2.

## Risk + Rollback

**Risk R1 (Low):** The classification vocabulary may not cover all real-world peer-solution edge cases. Mitigation: DCL `enforcement_mode='advisory'` means non-matching cases generate a warning, not a block; vocabulary is extensible via future ADR/DCL amendments.

**Risk R2 (Low):** Conflict with existing AUQ-only enforcement (`prime-builder-role.md` § AUQ as the Only Valid Owner-Decision Channel). Mitigation: this DCL is a specialization of the AUQ-only rule for peer-solution adoption; it explicitly cites the general rule rather than contradicting it.

**Risk R3 (Low):** Advisory-mode constraint may be perceived as unenforceable. Mitigation: Phase 1 advisory-pilot pattern is the canonical GT-KB approach (`GOV-20`); promotion to `blocking` after empirical data is the established path.

**Rollback:** `git revert <commit-sha>`. MemBase row reverts via append-only `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` — new MemBase DCL is a net-new design constraint. Subordinate `docs:` shape for the bridge proposal artifact itself.

## Loyal Opposition Asks

1. Confirm the IP-1 constraint-statement framing (peer-solution adoption decisions route through AUQ when they cross the in-scope threshold) is the right machine-checkable predicate.
2. Confirm the in-scope decision-class enumeration (adopt / adapt / reject-with-spec-impact / defer) covers the actionable adoption paths.
3. Confirm `advisory` enforcement mode (vs `blocking`) is the right Phase-1 default per `GOV-20`.
4. Confirm the assertions-field pattern (`peer_solution_classification in {...} -> auq_evidence_present`) is machine-checkable per existing DCL precedent.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
