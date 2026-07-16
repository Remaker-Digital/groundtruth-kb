NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5
author_model_version: codex-desktop-2026-07-15
author_model_configuration: Codex Desktop; Prime Builder; danger-full-access; approval-policy-never

# Implementation Proposal - Reissue WI-5236 PAUTH with registered forbidden-operation vocabulary

bridge_kind: prime_proposal
Document: gtkb-wi5240-wi5236-pauth-registered-vocabulary
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5240-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5240

target_paths: ["groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the WI-5236 PAUTH envelope so the already-approved fixture-drift implementation can acquire a governed work-intent claim without weakening the intended boundaries.

Work item description: WI-5236 has a live bridge GO, but Prime Builder cannot acquire the implementation work-intent claim because PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5236-DISPATCHER-RUNTIME-FIXTURE-DRIFT-20260714 denies work_intent_acquire with unknown_forbidden_operation. The PAUTH forbidden_operations contain unregistered labels source-code-behavior-change, dispatcher-runtime-json-edit, lease-file-edit, and groundtruth-db-mutation. Reissue or revise the WI-5236 PAUTH using registered operation IDs while preserving the intended no source behavior change, no dispatcher runtime JSON edit, no lease edit, and no groundtruth.db mutation boundaries through canonical operation IDs and scope text.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5240` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-202665963` - Loyal Opposition Review — GO
- `DELIB-20265245` - Loyal Opposition Review - Harness C Governance Gate Parity Blocker Record
- `DELIB-202665152` - NO-GO: WI-4944 -- Git metadata permission blocker sustained (no focused commit exists)
- `DELIB-202665995` - Verdict
- `DELIB-202665189` - NO-GO: WI-4944 -- v013 blocker report confirms unresolved topology authority gap; owner decision still required

## Owner Decisions / Input

- `DELIB-202666201` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5240-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5240`.

## Proposed Scope

- Reissue or revise only the WI-5236 project authorization envelope so forbidden_operations uses registered operation IDs only.
- Preserve the intended prohibitions against source behavior changes, dispatcher runtime JSON edits, lease-file edits, groundtruth.db mutation outside the PAUTH repair, and unrelated mutations as scope text or canonical registered operations.
- Do not edit dispatcher runtime JSON, lease files, source code, tests, harness registry eligibility, or bridge runtime state.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run the WI-5236 claim acquisition command and verify it no longer returns unknown_forbidden_operation. |
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
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Inspect the active WI-5236 PAUTH envelope and confirm allowed mutation classes and forbidden operations are registered and scoped. |

## Acceptance Criteria

- WI-5236 work-intent claim acquisition no longer fails with unknown_forbidden_operation.
- The revised WI-5236 PAUTH contains no unregistered forbidden_operations labels.
- TEST-11394 is satisfied by a dry-run or real claim attempt that reaches the next gate without unknown_forbidden_operation.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth.db`

## Recommended Commit Type

`feat`
