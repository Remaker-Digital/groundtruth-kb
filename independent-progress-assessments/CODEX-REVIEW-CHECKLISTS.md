# Codex Review Checklists - GroundTruth-KB

Purpose: reusable checklists for rigorous proposal review, code review, and alternatives investigation.

## Proposal Review Checklist

- Is the problem statement concrete and testable?
- Are assumptions explicit?
- Does the proposal contradict code, docs, or prior decisions?
- Are constraints complete: technical, operational, compliance, cost, support?
- Is the failure mode discussed?
- Is rollback or containment discussed?
- Are success criteria measurable?
- Is there a credible verification plan?
- Are rejected alternatives named?
- Is there a clear owner decision required?

## Code Review Checklist

- Does the change actually satisfy the stated claim?
- What can regress?
- Are assertions behavioral or only structural/shallow?
- Are new branches/error paths tested?
- Are naming and comments hiding ambiguity?
- Does the change weaken permissions, safety gates, or tenancy isolation?
- Does it introduce hidden coupling to env, docs, or runtime order?
- Does it create documentation or KB drift?
- Is the verification scope sufficient for the risk level?
- What is the smallest high-confidence fix if the current approach is weak?

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
