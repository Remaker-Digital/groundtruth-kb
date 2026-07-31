NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex Desktop; reasoning=xhigh; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Reissue WI-5217 PAUTH with registered forbidden-operation vocabulary

bridge_kind: prime_proposal
Document: gtkb-wi5235-wi5217-pauth-registered-vocabulary
Version: 001
Date: 2026-07-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5235-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5235

target_paths: ["groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Reissue the WI-5217 Antigravity prompt-transport PAUTH with registered operation vocabulary so the already-GO C prompt transport repair can legally start.

Work item description: WI-5217 has an independent GO at bridge/gtkb-wi5217-antigravity-prompt-transport-002.md, but Prime Builder cannot legally acquire the implementation claim because PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712 contains unregistered forbidden_operations labels: harness_registry_or_routing_edit, role_or_model_change, worker_lifetime_reduction, direct_runtime_or_lease_edit, and unrelated_mutation. Reissue the same PAUTH with only registered operation IDs while preserving the intended no-registry/routing, no role/model change, no worker-lifetime reduction, no runtime/lease edit, and no unrelated-mutation boundaries through canonical operation IDs and scope text.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5235` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

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

- `DELIB-202665963` - Loyal Opposition Review — GO
- `DELIB-202665995` - Verdict
- `DELIB-20265573` - GO - gtkb-antigravity-lo-hallucination-prevention - Revised Scope
- `DELIB-20260627` - Owner decision: expand PAUTH for PROJECT-GTKB-LO-ADVISORY-INTAKE (WI-3300)
- `DELIB-20264112` - Loyal Opposition Review - Harness C Governance Gate Parity Blocker Record

## Owner Decisions / Input

- `DELIB-202666173` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5235-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5235`.

## Proposed Scope

- Append a new active version for PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712 using only registered forbidden operation IDs.
- Preserve the existing WI-5217 target scope, allowed mutation classes source/test/bridge, included work item WI-5217, and the substantive no-registry/routing, no role/model, no worker-lifetime reduction, no runtime/lease edit, and no unrelated-mutation boundaries.
- Do not implement WI-5217 source/test changes in this PAUTH repair; mutate only groundtruth.db through the canonical gt projects authorize writer after GO, claim, and implementation-start packet.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Show the before/after PAUTH forbidden_operations and run the implementation-start dry path for WI-5217. |
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
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- The active WI-5217 PAUTH forbidden_operations all resolve against config/governance/project-authorization-operation-taxonomy.toml.
- implementation_authorization.py begin --bridge-id gtkb-wi5217-antigravity-prompt-transport --no-write no longer fails with unknown_forbidden_operation once a valid claim is held.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth.db`

## Recommended Commit Type

`feat`
