NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5
author_model_version: codex-desktop-2026-07-15
author_model_configuration: Codex Desktop; Prime Builder; danger-full-access; approval-policy-never

# Implementation Proposal - Reissue WI-5219 PAUTH with registered forbidden-operation vocabulary

bridge_kind: prime_proposal
Document: gtkb-wi5241-wi5219-pauth-registered-vocabulary
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5241-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5241

target_paths: ["groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Reissue the WI-5219 Phase 2 active-harness-population PAUTH with registered operation vocabulary so the already-GO parity evaluator repair can legally start.

Work item description: WI-5219 has an independent GO at bridge/gtkb-wi5219-phase2-active-harness-population-002.md, but Prime Builder cannot legally acquire the implementation work-intent claim because PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5219-PHASE2-ACTIVE-POPULATION-20260712 contains prose allowed_mutation_classes and forbidden_operations values instead of registered taxonomy IDs. The claim gate fails with unknown_forbidden_operation for harness registry, dispatcher routing, eligibility, roles, model routes, runtime-state mutation, and D/F/H allowance-reduction prose labels. Reissue or revise the WI-5219 PAUTH using registered mutation classes and operation IDs while preserving the intended no registry/routing/eligibility/role/model/runtime mutation and no allowance-reduction boundaries through canonical IDs, target classes, and scope text.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5241` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth.db`.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
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
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for new authorization state.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260702-WI4943-FIRST-RENEWAL` - Renew WI-4943 as dispatcher-resume prerequisite
- `DELIB-2509` - Owner AUQ Answer: Per-WI PAUTH + Assign-Only Scope for WI-3450 Orphan Backfill Driver
- `DELIB-202666149` - WI-5200..5202 - Generous cloud-harness recovery, runtime envelopes, and truthful H parity - Loyal Opposition proposal review
- `DELIB-20264111` - Loyal Opposition Review - Harness C Governance Gate Parity Blocker Record
- `DELIB-20265245` - Loyal Opposition Review - Harness C Governance Gate Parity Blocker Record

## Owner Decisions / Input

- `DELIB-202666173` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5241-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5241`.

## Proposed Scope

- Append a new active version for PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5219-PHASE2-ACTIVE-POPULATION-20260712 using only registered allowed mutation classes and forbidden operation IDs.
- Preserve the intended no registry/routing/eligibility/role/model/runtime mutation and no D/F/H allowance-reduction boundaries through registered operation IDs, target-class enforcement, and scope text.
- Do not implement the WI-5219 source/test evaluator change in this PAUTH repair; mutate only groundtruth.db through the canonical gt projects authorize writer after GO, claim, and implementation-start authorization.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Load config/governance/project-authorization-operation-taxonomy.toml and verify every active WI-5219 PAUTH allowed_mutation_classes and forbidden_operations value resolves to a registered ID; then run the WI-5219 claim command and require no unknown_forbidden_operation. |
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
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Read back the active PAUTH version with gt projects show-authorization and compare version, status, included work item, allowed classes, forbidden operations, included specs, owner decision, scope, and change reason. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Verify WI-5219 source/test implementation remains blocked on its own GO, claim, implementation-start packet, implementation report, and independent verification after this PAUTH-only repair. |

## Acceptance Criteria

- The active WI-5219 PAUTH allowed_mutation_classes and forbidden_operations all resolve against config/governance/project-authorization-operation-taxonomy.toml.
- python scripts/bridge_claim_cli.py claim gtkb-wi5219-phase2-active-harness-population reaches the next gate without unknown_forbidden_operation after the PAUTH repair.
- No source, test, dispatcher runtime JSON, lease, harness registry, eligibility, routing, role, model, or allowance mutation occurs in this PAUTH repair.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth.db`

## Recommended Commit Type

`feat`
