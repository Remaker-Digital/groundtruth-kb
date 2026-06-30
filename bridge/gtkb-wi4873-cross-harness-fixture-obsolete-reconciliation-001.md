NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f19e8-d832-76c2-8aa1-1bf492ac8382
author_model: GPT-5 Codex
author_model_version: 2026-06-30
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access; role=prime-builder; initialized via init keyword

# Implementation Proposal - WI-4873 obsolete cross-harness fixture reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi4873-cross-harness-fixture-obsolete-reconciliation
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-OPEN-CHILD-RECONCILIATION-2026-06-30
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4873

target_paths: ["groundtruth.db"]

implementation_scope: metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Resolve `WI-4873` by verifying the stale post-TAFE cross-harness trigger fixture is no longer present on HEAD, then update the backlog with bridge-linked evidence.

## Claim

Prime Builder proposes a bounded reconciliation slice for `WI-4873`. Current-tree evidence indicates the named failing test path and retired trigger source path are absent, so the work item should be resolved as superseded by the prior trigger purge rather than treated as a live production defect.

## Requirement Sufficiency

Existing requirements are sufficient. The work item describes a stale post-cutover fixture; the active PAUTH bounds this slice to evidence-backed Knowledge DB reconciliation for the named child item.

## In-Root Placement Evidence

- `groundtruth.db` is the in-root MemBase authority for backlog resolution.
- Current-tree file discovery is sufficient evidence for the absence of the retired trigger fixture and source path.
- Git history can be cited as supporting evidence for the prior purge that removed the stale fixture surface.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before a VERIFIED verdict.

## Prior Deliberations

- `DELIB-20260630-DISPATCHER-RELIABILITY-AUTOPROCESS-DIRECTIVE` - owner directed Codex Prime Builder to auto-process all Prime Builder-actionable children in `PROJECT-GTKB-DISPATCHER-RELIABILITY`.
- `DELIB-20266505` - prior owner direction to continue dispatcher reliability fixes/enhancements autonomously until operational.

## Owner Decisions / Input

- `DELIB-20260630-DISPATCHER-RELIABILITY-AUTOPROCESS-DIRECTIVE` - owner approval for all Prime Builder-actionable child work in the dispatcher reliability project.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-OPEN-CHILD-RECONCILIATION-2026-06-30` - active project authorization covering `WI-4873`.

## Proposed Scope

- Verify that the stale post-TAFE cross-harness bridge trigger fixture is no longer present on HEAD.
- Use repository history and current test discovery to classify `WI-4873` as superseded by the retired trigger purge rather than a live failing test.
- Resolve `WI-4873` through Knowledge DB/backlog reconciliation when the obsolete fixture evidence is confirmed.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Before protected mutation, begin implementation only after a `GO` verdict and work-intent claim for this bridge thread. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Confirm this proposal contains Project Authorization, Project, Work Item, and machine-readable `target_paths` metadata. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-OPEN-CHILD-RECONCILIATION-2026-06-30` is active and includes `WI-4873`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run current-tree file discovery and the targeted old-path pytest probe, then include results in the implementation report before requesting verification. |

## Acceptance Criteria

- The retired cross-harness trigger test path is absent from the current tree.
- The retired cross-harness trigger source path is absent from the current tree.
- A targeted pytest invocation for the old test path reports that the test file is absent rather than a live assertion failure.
- `WI-4873` is resolved with this bridge thread recorded as related evidence.

## Risks / Rollback

Risk is low because the proposal is metadata reconciliation. The main risk is misclassifying an absent historical fixture while another live replacement test still fails; verification will use current tree discovery before resolving. Rollback is a new backlog update reopening the work item if verification disproves the obsolete-fixture conclusion; bridge files remain append-only audit artifacts.

## Files Expected To Change

- `groundtruth.db`

## Recommended Commit Type

`chore`
