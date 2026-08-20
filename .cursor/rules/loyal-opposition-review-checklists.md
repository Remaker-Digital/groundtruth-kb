<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project cursor`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
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
- Issue `NO-GO`, not `VERIFIED`, for any linked specification without executed
  test coverage unless an explicit owner waiver is documented.

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

- Is the advisory classified as exactly one of `adopt`, `adapt`, `reject`,
  `defer`, or `monitor`?
- For `adopt` or `adapt`, does the report include a `Required Prime Builder
  Owner-Grilling Gate` section before any derived implementation proposal
  exists?
- Does the gate identify the owner questions, practical options, tradeoffs,
  and expected durable artifact outcome?
- Does the report say whether Prime Builder should create a bridge proposal,
  capture a deliberation, defer the item, or reject the recommendation?
- Are blocking owner decisions routed through the owner-decision channel rather
  than buried in prose?
- Are source advisory paths, affected specs/WIs, and verification expectations
  concrete enough for Prime Builder to act without rediscovery?

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
