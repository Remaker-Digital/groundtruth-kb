NEW

# Peer Solution Workflow Contract ADR - NEW

bridge_kind: implementation_proposal
Document: gtkb-peer-solution-workflow-contract-adr
Version: 001 (NEW; Slice 1 — candidate ADR filing)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` (Codex GO at `-004`).

## Claim

This proposal authors a **candidate ADR for the GT-KB-native declarative workflow contract** as MemBase row `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` (status `candidate` -> `specified` upon Codex GO + owner approval-packet). The ADR captures the architectural decision to borrow Archon's DAG execution language without importing Archon runtime authority, and to keep MemBase + bridge + Deliberation Archive as the authoritative substrate.

The Slice-0 GO explicitly named this as follow-on (b): "Workflow-contract candidate ADR/spec proposal" (`bridge/gtkb-peer-solution-advisory-loop-conversion-003.md:138`).

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
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/operating-model.md`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`

## Prior Deliberations

- `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` - parent Slice-0 REVISED-1.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-004.md` - parent Slice-0 GO.
- `bridge/gtkb-peer-solution-advisory-loop-procedure-001.md` - sibling Slice-1 follow-on (procedure document).
- `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md` - source LO advisory.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-10-22-25-PEER-SOLUTION-ADVISORY-REPORT.md` - LO insight defining the workflow-contract candidate analysis.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog ... Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this Slice-1 follow-on filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the formal-artifact-approval packet for `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` MemBase insertion is produced at implementation time per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`.

## Scope (Slice 1)

### IN SCOPE

**IP-1: Author `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` as a MemBase row** with `type='architecture_decision'`, `status='specified'`. ADR contents:

1. **Context:** GT-KB encounters peer-system solutions (Archon, BMAD, GSD, Symphony) that propose declarative workflow contracts. Without a governed decision, individual sessions may ad-hoc adopt or reject these patterns.
2. **Decision:** GT-KB adopts a declarative workflow contract vocabulary modeled on Archon's DAG execution language (nodes, edges, gates, evaluators), but does NOT import Archon as a runtime authority. MemBase remains the authoritative spec/work-item store; the bridge remains the authoritative review surface; the Deliberation Archive remains the authoritative reasoning record. The workflow contract is a vocabulary for describing multi-step GT-KB processes (e.g., release-readiness gates, multi-slice implementation sequences), not a parallel execution authority.
3. **Failed approaches considered:** (a) Adopt Archon runtime authority directly — rejected because it creates parallel-source-of-truth conflict with MemBase + bridge. (b) Reject all peer-system vocabulary — rejected because peer-systems have real insights worth borrowing. (c) Ad-hoc per-session adoption — rejected because it produces inconsistent vocabulary across the project.
4. **Consequences:** Future GT-KB workflows can be described with the new vocabulary; existing workflows can be retroactively annotated; the bridge/MemBase/DA boundary stays clean; peer-system advisories can be evaluated against a stable vocabulary baseline.
5. **Rejected alternatives:** (preserved separately in `failed_approaches` field).

**IP-2: Approval packet for `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001`.** At implementation time, Prime authors the approval packet at `.groundtruth/formal-artifact-approvals/<date>-adr-peer-solution-workflow-contract-001.json` per the formal-artifact-approval-gate schema.

**IP-3: MemBase regression test.** Add `platform_tests/groundtruth_kb/specs/test_adr_peer_solution_workflow_contract.py` asserting the ADR row exists in MemBase with the required fields populated (context / decision / failed_approaches / consequences). The test uses the public `groundtruth_kb.db` API; no direct SQLite access.

### OUT OF SCOPE

- Procedure document (sibling thread `gtkb-peer-solution-advisory-loop-procedure-001`).
- Owner-gate DCL (sibling thread `gtkb-peer-solution-owner-gate-dcl-001`).
- Runtime workflow execution code (deferred to a future slice after the ADR is durable).
- Archon installation (out of parent Slice-0 scope).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr` - exit 0 expected.

### Implementation tests

3. `pytest platform_tests/groundtruth_kb/specs/test_adr_peer_solution_workflow_contract.py -v` - PASS expected (IP-3).

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping + Step 3. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | ADR MemBase row + approval packet inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | Approval packet per IP-2. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Approval-gate hook validates ADR insert at write time. |
| `CODEX-WAY-OF-WORKING.md` § advisory-capture | ADR Context section cites the advisory-capture pattern. |
| `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded | ADR Decision section preserves owner role as specifications + clarifications + tradeoffs. |
| `CODEX-REVIEW-CHECKLISTS.md` § spec-linkage | This thread cites every relevant governing surface. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS on `-001`.
- [ ] Codex GO on this Slice-1 NEW.
- [ ] `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` inserted in MemBase with all 5 required ADR sections.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-adr-peer-solution-workflow-contract-001.json` produced at implementation time.
- [ ] `platform_tests/groundtruth_kb/specs/test_adr_peer_solution_workflow_contract.py` PASS.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-peer-solution-workflow-contract-adr-001.md` with a corresponding `bridge/INDEX.md` entry (insert at top of doc list); no prior versions are deleted or rewritten — the version chain is append-only per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 follow-on adds one new bridge entry. NOT a bulk operation.

- **inventory artifact:** IP-1 to IP-3 enumeration above.
- **review packet:** this `-001` NEW.
- **DECISION DEFERRED markers:** sibling-thread follow-ons (procedure / owner-gate) and runtime execution code are deferred to their own bridge proposals.
- **formal-artifact-approval packet:** produced at implementation time per IP-2.

## Risk + Rollback

**Risk R1 (Low):** The chosen DAG vocabulary may conflict with future MemBase schema changes. Mitigation: ADR records the decision but does not bind MemBase schema; the schema remains flexible.

**Risk R2 (Low):** Future readers may conflate the ADR (vocabulary) with a runtime authority claim. Mitigation: ADR Decision section is explicit that MemBase + bridge + DA remain authoritative; vocabulary is descriptive, not executive.

**Rollback:** `git revert <commit-sha>`. MemBase row reverts via append-only `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` — new MemBase ADR is a net-new architectural decision record. Subordinate `docs:` shape for the bridge proposal artifact itself.

## Loyal Opposition Asks

1. Confirm the IP-1 ADR section structure (Context / Decision / Failed approaches / Consequences / Rejected alternatives) matches existing GT-KB ADR precedent.
2. Confirm the Decision section's "borrow vocabulary, don't import authority" framing is the right line between adoption and rejection of peer-system patterns.
3. Confirm the failed-approaches enumeration covers the main rejected paths (full adoption / full rejection / ad-hoc).
4. Confirm the IP-3 regression-test scope (presence + field structure, no semantic checks) is the right gate.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
