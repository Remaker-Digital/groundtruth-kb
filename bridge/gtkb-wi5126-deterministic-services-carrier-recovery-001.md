NEW
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-06T06-13-35Z
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::open build

# Implementation Proposal - Create deterministic-services GOV/DCL carrier and demote DELIB-S312 provenance (replacement for WI-5120)

bridge_kind: prime_proposal
Document: gtkb-wi5126-deterministic-services-carrier-recovery
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-CARRIER-RECOVERY
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5126

target_paths: ["groundtruth.db", ".claude/rules/acting-prime-builder.md", ".groundtruth/formal-artifact-approvals"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recover the deterministic-services carrier scope with explicit KB, narrative, packet, and verification targets.

Work item description: DELIB-202665933 recovery: replace WI-5120 because its GO proposal omitted the required groundtruth.db KB-mutation target. Create the canonical GOV/DCL carrier, formally approve it, and revise acting-prime-builder.md to cite the carrier while retaining DELIB-S312 as provenance.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5126` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth.db`, `.claude/rules/acting-prime-builder.md`, `.groundtruth/formal-artifact-approvals`.

## Specification Links

- `SPEC-INTAKE-bb25be` - auto-linked governing or work-item specification.
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
- `SPEC-INTAKE-fee587` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20263309` - Impl-Auth Packet Liveness Coupling + TTL Shrink Proposal Review
- `DELIB-20265390` - Verdict
- `DELIB-20260961` - Loyal Opposition Verification - WI-3326 Executable Packet Repair Corrected Report
- `DELIB-20261160` - Loyal Opposition Verification - WI-3326 Executable Packet Repair Corrected Report
- `DELIB-2499` - S365 Owner Decision: PROJECT-GTKB-PUSH-GATE PAUTH Standing Scope (Slice 0-11)

## Owner Decisions / Input

- `DELIB-202665933` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-CARRIER-RECOVERY` - active project authorization covering `WI-5126`.

## Proposed Scope

- Create the deterministic-services canonical GOV/DCL carrier in MemBase with owner-approved formal content.
- Update acting-prime-builder.md so the carrier is authority and DELIB-S312 is provenance only.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-bb25be` | Verify the carrier exists and the rule no longer treats DELIB-S312 as operative authority. |
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
| `SPEC-INTAKE-fee587` | Verify deterministic service authority is formalized in infrastructure rather than worker judgment. |

## Acceptance Criteria

- A canonical GOV/DCL record establishes the Deterministic Services Principle.
- The narrative rule cites the carrier and does not cite DELIB-S312 as sole authority.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth.db`
- `.claude/rules/acting-prime-builder.md`
- `.groundtruth/formal-artifact-approvals`

## Recommended Commit Type

`feat`
