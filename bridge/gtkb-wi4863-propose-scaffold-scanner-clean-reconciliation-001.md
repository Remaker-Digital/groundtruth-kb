NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f19e8-d832-76c2-8aa1-1bf492ac8382
author_model: GPT-5 Codex
author_model_version: 2026-06-30
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access; role=prime-builder; initialized via init keyword

# Implementation Proposal - WI-4863 proposal scaffold scanner-clean reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi4863-propose-scaffold-scanner-clean-reconciliation
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-OPEN-CHILD-RECONCILIATION-2026-06-30
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4863

target_paths: ["scripts/gtkb_propose_scaffold.py", "platform_tests/scripts/test_gtkb_propose_scaffold.py", "groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Resolve `WI-4863` by verifying the current proposal scaffold and regression tests already remove the scanner-unsafe pytest cacheprovider-disable fragment, then update the backlog with bridge-linked evidence.

## Claim

Prime Builder proposes a bounded reconciliation slice for `WI-4863`. Current-tree evidence indicates the source and tests already satisfy the acceptance condition; the remaining work is to preserve bridge-reviewed evidence and resolve the work item.

## Requirement Sufficiency

Existing requirements are sufficient. The work item names the scanner false-positive failure mode, and the active PAUTH bounds this slice to source, test, bridge, and Knowledge DB reconciliation for the named child item.

## In-Root Placement Evidence

- `scripts/gtkb_propose_scaffold.py` is inside the project root and contains the scaffold command template.
- `platform_tests/scripts/test_gtkb_propose_scaffold.py` is inside the project root and contains regression coverage for scanner-clean scaffold output.
- `groundtruth.db` is the in-root MemBase authority for backlog resolution.

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
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-OPEN-CHILD-RECONCILIATION-2026-06-30` - active project authorization covering `WI-4863`.

## Proposed Scope

- Verify the current gtkb proposal scaffold no longer emits the scanner-unsafe pytest cacheprovider-disable fragment.
- Use existing regression coverage to prove the proposal body remains scanner-clean for the former false-positive command pattern.
- Resolve `WI-4863` through Knowledge DB/backlog reconciliation when the implementation evidence is confirmed.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Before protected mutation, begin implementation only after a `GO` verdict and work-intent claim for this bridge thread. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Confirm this proposal contains Project Authorization, Project, Work Item, and machine-readable `target_paths` metadata. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-OPEN-CHILD-RECONCILIATION-2026-06-30` is active and includes `WI-4863`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run targeted scaffold tests and include command output in the implementation report before requesting verification. |

## Acceptance Criteria

- The scaffolded proposal body avoids the former scanner-triggering pytest cacheprovider-disable fragment.
- `platform_tests/scripts/test_gtkb_propose_scaffold.py` includes regression assertions for the former scanner-triggering pattern.
- The targeted scaffold test module passes in the GT-KB venv.
- `WI-4863` is resolved with this bridge thread recorded as related evidence.

## Risks / Rollback

Risk is low because current evidence points to already-landed source/test behavior. The main risk is closing the work item without preserving bridge-reviewed evidence. Rollback is a new backlog update reopening the work item if verification disproves the current-tree conclusion; bridge files remain append-only audit artifacts.

## Files Expected To Change

- `groundtruth.db`

## Recommended Commit Type

`chore`
