# Loyal Opposition Review Checklists - GroundTruth-KB

Purpose: reusable checklists for rigorous proposal review, code review, and alternatives investigation.

## Proposal Review Checklist

- Does the implementation proposal include a `Specification Links` section?
- Does that section cite every relevant governing specification, rule, ADR, DCL,
  proposal standard, and durable requirement artifact?
- Does the proposed test plan derive tests from each linked specification?
- Is the problem statement concrete and testable?
- Are assumptions explicit?
- Does the proposal contradict code, docs, or prior decisions?
- Has the standing backlog (via MemBase `work_items` or `gt backlog list`) been checked for upcoming related work to prevent duplicating effort or interfering with future project plans (with conflicts resolved by bringing work forward or adding to the scope of an existing future project)?
- Are constraints complete: technical, operational, compliance, cost, support?
- Is the failure mode discussed?
- Is rollback or containment discussed?
- Are success criteria measurable?
- Is there a credible verification plan?
- Are rejected alternatives named?
- Is there a clear owner decision required?

## Code Review Checklist

- Does the change actually satisfy the stated claim?
- Are the linked specifications from the proposal carried forward into the
  implementation report?
- Is there a spec-to-test mapping for every linked specification?
- Were the specification-derived tests executed against the implementation?
- What can regress?
- Are assertions behavioral or only structural/shallow?
- Are new branches/error paths tested?
- Are naming and comments hiding ambiguity?
- Does the change weaken permissions, safety gates, or tenancy isolation?
- Does it introduce hidden coupling to env, docs, or runtime order?
- Does it create documentation or KB drift?
- Is the verification scope sufficient for the risk level?
- What is the smallest high-confidence fix if the current approach is weak?

## Verification Checklist

- Carry forward the implementation proposal's `Specification Links`.
- Confirm each linked specification has at least one created or identified test
  derived from that specification.
- Execute or inspect execution evidence for those tests against the
  implementation.
- Issue `NOT-READY` for an implementation report whose linked requirements
  lack executed test coverage; identify the missing evidence and recovery route.

## Alternatives Investigation Checklist

- What are the real constraints?
- What options are actually implementable now?
- What dependencies or approvals does each option require?
- What is reversible vs sticky?
- What is the migration cost?
- What is the operational burden?
- What is the failure mode?
- What evidence supports each option?
- Which option minimizes regret?
- What decision does the owner need to make?

## Advisory Report Checklist

- Does the report distinguish observed evidence, inference and uncertainty?
- Does the recommendation explain its scope and expected result?
- Does it identify only unresolved material owner choices, with practical options
  and consequences, or say none remains?
- Does the header carry full author provenance and omit routing envelopes?
- Is the advisory informational, absent from both role queues and free of a
  work-item reservation or automatic follow-up assignment?
- Will any owner-selected implementation use a separate NEW chain with current
  specification links, executable tests and independent review?
- Are owner-directed changes applied through canonical writers and read back,
  without a permission ledger, mandatory interview or AUQ-only receipt?

## Configuration Review Checklist

- Are controls portable or machine-local only?
- Are hooks fail-open or fail-closed?
- Are there mutating side effects in analysis flows?
- Is the permission surface justified by the role?
- Are reporting standards explicit and enforced?
- Are local-memory assumptions verifiable?
- Are skills aligned with the actual primary role?
- Is there a clean separation between builder and reviewer behavior?

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
