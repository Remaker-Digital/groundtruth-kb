REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 019f3d48-b886-7be2-a656-99678002edf1
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Deterministic-Services Carrier Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5126-deterministic-services-carrier-recovery
Version: 003
Date: 2026-07-10 UTC
Responds to: bridge/gtkb-wi5126-deterministic-services-carrier-recovery-002.md

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-CARRIER-RECOVERY
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5126

target_paths: ["groundtruth.db", ".claude/rules/acting-prime-builder.md", ".groundtruth/formal-artifact-approvals"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Create a canonical carrier for the Deterministic Services Principle and demote DELIB-S312 to provenance. This REVISED proposal corrects WI-5120's missing-KB-scope defect by declaring both `groundtruth.db` and `kb_mutation_in_scope: true`.

## Claim

Prime Builder proposes one bounded recovery slice for WI-5126. The intended carrier is provisional `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`; its final content and identifier remain subject to an owner-approved formal-artifact packet before creation.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-INTAKE-bb25be` requires a canonical carrier for operating rules, and `SPEC-INTAKE-fee587` requires deterministic infrastructure rather than worker-held operating judgment. No authority is claimed from DELIB-S312 itself.

## In-Root Placement Evidence

Every target is inside the project root: MemBase in `groundtruth.db`, the active Prime Builder rule, and the formal-artifact approval-packet directory.

## Specification Links

- `SPEC-INTAKE-bb25be` - an operating rule requires a canonical carrier.
- `SPEC-INTAKE-fee587` - deterministic services belong in infrastructure, not worker judgment.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the numbered bridge chain governs this recovery and independent review.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the principle is promoted into a durable governed artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal carries concrete governing links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification will be tied to carrier, citation, and packet evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, authorization, work item, and target paths are explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all mutation surfaces remain in the platform root.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the carrier, approval packet, bridge report, and verification evidence remain durable project artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this revision advances the owner-authorized recovery lifecycle.

## Prior Deliberations

- `DELIB-202665929` - diagnosed the DELIB-sole-authority carrier gap.
- `DELIB-202665930` - authorized the initial canonical-authority remediation project.
- `DELIB-202665933` - retired WI-5120 and ordered this successor to include every actual mutation surface, including the KB mutation.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - provenance for the principle being promoted; it will not remain the rule's establishing authority.
- This proposal differs from withdrawn WI-5120 by declaring the KB mutation in both target paths and scope metadata, naming the intended carrier, and committing carrier-specific verification.

## Owner Decisions / Input

- `DELIB-202665933` authorizes the recovery and requires the successor to eliminate WI-5120's incomplete KB-mutation scope.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-CARRIER-RECOVERY` actively covers WI-5126.
- The final formal carrier content will be presented in its approval packet before any specification record is created.

## Proposed Scope

- Create provisional `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` in MemBase after owner approval of the formal-artifact packet.
- Update `.claude/rules/acting-prime-builder.md` to cite the GOV carrier as authority and retain DELIB-S312 only as provenance.
- Record the approval packet in the governed packet directory and preserve its content hash with the created record.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-bb25be` | Query the created GOV carrier by id and verify the rule cites that carrier rather than a DELIB as its sole authority. |
| `SPEC-INTAKE-fee587` | Verify the carrier states deterministic-service ownership in governed infrastructure and the active rule points to it. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify the revised proposal and post-implementation report are numbered bridge versions with independent LO verdicts. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify the principle exists as a MemBase GOV record rather than only in DELIB provenance. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability preflight on the REVISED body and confirm no required links are missing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | File an implementation report containing the exact carrier lookup, rule-citation, packet-hash, test, and lint evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm the live proposal carries the active PAUTH, project, WI-5126, and all three actual mutation targets. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify each changed path remains inside the project root and no adopter repository is touched. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verify the prior WI-5120 withdrawal, this REVISED successor, packet approval, implementation report, and LO verification form an auditable lifecycle. |

## Acceptance Criteria

- A canonical GOV record establishes the Deterministic Services Principle in MemBase.
- `.claude/rules/acting-prime-builder.md` cites the GOV carrier as authority and does not treat DELIB-S312 as sole authority.
- A formal-artifact packet is present, owner-approved before carrier creation, and its recorded content hash matches the created carrier.

## Risks / Rollback

Risk is moderate because the change creates a durable governance carrier. Rollback reverts the rule citation and retires or supersedes the created carrier only through its governed lifecycle; bridge files, approval packets, and deliberation evidence remain append-only audit records.

## Files Expected To Change

- `groundtruth.db`
- `.claude/rules/acting-prime-builder.md`
- `.groundtruth/formal-artifact-approvals`

## Recommended Commit Type

`fix`
