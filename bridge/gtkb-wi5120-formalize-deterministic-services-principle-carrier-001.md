NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8ae8ee16-629f-4328-a797-47cb3e7a3293
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Formalize the Deterministic Services Principle as a canonical GOV/DCL; demote DELIB-S312 to provenance

bridge_kind: prime_proposal
Document: gtkb-wi5120-formalize-deterministic-services-principle-carrier
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5120

target_paths: [".claude/rules/acting-prime-builder.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Finding B1 of DELIB-202665929: the Deterministic Services Principle is established solely by DELIB-S312 (a DELIB is not rule authority). Formalize it as a canonical GOV/DCL carrier and demote the DELIB to provenance in acting-prime-builder.md. Carrier creation (KB mutation) plus a narrative-rule edit requiring a formal-artifact approval packet at implement time.

Work item description: Finding B1. acting-prime-builder.md:245 makes DELIB-S312 the sole authority for a live operational mandate with no canonical carrier. Create the GOV/DCL, then rewrite the rule to cite the spec as authority and the DELIB as provenance.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5120` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/rules/acting-prime-builder.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `SPEC-INTAKE-bb25be` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20261606` - Loyal Opposition Review - LO Advisory Intake Inventory REVISED-2
- `DELIB-2725` - Loyal Opposition Review - LO Advisory Intake Inventory REVISED-2
- `DELIB-20261605` - Verification Verdict - LO Advisory Intake Inventory
- `DELIB-2724` - Verification Verdict - LO Advisory Intake Inventory
- `DELIB-20261498` - Loyal Opposition Verdict - Project Completion Scanner Addressing-Thread Fix Implementation - 002

## Owner Decisions / Input

- `DELIB-202665930` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION` - active project authorization covering `WI-5120`.

## Proposed Scope

- Create a new canonical carrier (GOV or DCL) that formalizes the Deterministic Services Principle (repetitive AI work is a defect; deterministic plumbing belongs in services) currently established only by DELIB-S312 in acting-prime-builder.md:245.
- Edit .claude/rules/acting-prime-builder.md to cite the new canonical carrier as the authority for the principle and demote DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE to provenance (owner-decision paper trail), not sole authority.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-INTAKE-bb25be` | The principle now has a canonical carrier; the rule file no longer presents a DELIB as the sole authority for the operating mandate. |

## Acceptance Criteria

- The Deterministic Services Principle is represented in MemBase as a canonical GOV/DCL spec.
- acting-prime-builder.md cites the canonical carrier as authority; DELIB-S312 appears only as provenance, not as the establishing artifact.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/rules/acting-prime-builder.md`

## Recommended Commit Type

`feat`
