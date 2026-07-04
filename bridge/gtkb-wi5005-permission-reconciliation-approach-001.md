NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; role=Prime Builder; sandbox=danger-full-access; approval=never
author_metadata_source: codex-interactive

# Implementation Proposal - Produce implementation approach and work-item list proposal for permission reconciliation and harmonization

bridge_kind: prime_proposal
Document: gtkb-wi5005-permission-reconciliation-approach
Version: 001
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION-WI-5005-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION
Work Item: WI-5005

target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/PERMISSION-RECONCILIATION-IMPLEMENTATION-APPROACH-*.md", "groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Create the WI-5005 implementation-approach and downstream work-item list for the permission reconciliation/harmonization umbrella.

Work item description: Produce a bridge-ready implementation approach and normalized work-item list proposal for GT-KB/application mutation permission reconciliation. The proposal must cover durable for-cause dispatch quiesce that survives autonomous re-enable; activity-window-scoped mutation authority; adversarial-diligence requirements for operational and configuration mutations; emergency/single-harness exception handling; audit/evidence requirements; rollback/cancel semantics; branch/dispatch constraints; relationship to WI-4997; and sequencing for creating approved downstream work items only after LO GO.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5005` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/PERMISSION-RECONCILIATION-IMPLEMENTATION-APPROACH-*.md`, `groundtruth.db`.

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-20260703-GTKB-MUTATION-PERMISSION-GENERAL-PRIMITIVE-FIRST` - General mutation-permission primitive first
- `DELIB-20260703-GTKB-PREMISSION-RECONCILIATION-DIRECTIVE` - Permission reconciliation and harmonization umbrella directive
- `DELIB-202665173` - Verdict Summary
- `DELIB-20260702-ROLE-AUTHORITY-SCOPED-APPROVAL-A` - Approve scoped role-authority boundary program
- `DELIB-202665137` - Loyal Opposition Verdict — Umbrella Proposal: Session/Activity Envelope Sharding Program

## Owner Decisions / Input

- `DELIB-20260703-GTKB-MUTATION-PERMISSION-GENERAL-PRIMITIVE-FIRST` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION-WI-5005-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5005`.

## Proposed Scope

- Produce a governed implementation-approach report for a general mutation-permission/control-plane primitive, using dispatcher quiesce as the first implementation case.
- Define ordered downstream work items but do not create them until the proposal receives GO and the implementation report executes the approved scope.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | gt bridge show gtkb-wi5005-permission-reconciliation-approach confirms a complete NEW->GO->NEW report->VERIFIED lifecycle. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report includes the approach report path and ordered downstream work-item list evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Report cites owner decisions and distinguishes dispatcher quiesce from the general permission primitive.
- Downstream WI list is ordered, bounded, and mapped to mutation/risk/environment classes.
- No source/config/test mutation occurs in this slice.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/PERMISSION-RECONCILIATION-IMPLEMENTATION-APPROACH-*.md`
- `groundtruth.db`

## Recommended Commit Type

`feat`
