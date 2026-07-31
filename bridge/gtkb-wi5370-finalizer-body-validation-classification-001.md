NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb

# Implementation Proposal - Repair repo-wide failed VERIFIED finalization residue

bridge_kind: prime_proposal
Document: gtkb-wi5370-finalizer-body-validation-classification
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: ["scripts/per_thread_finalization_repair.py", "platform_tests/scripts/test_per_thread_finalization_repair.py", "docs/procedures/per-thread-finalization-repair.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Teach the WI-5116 per-thread repair planner to detect terminal VERIFIED bodies that cannot be fed to the canonical finalizer, so operators stop treating invalid file-only verdicts as safe direct-finalization candidates.

Work item description: Live umbrella work item for repairing residual failed file-only terminal VERIFIED verdicts and restoring per-thread finalization after the 2026-07-16 repo-wide uncommitted-file sprawl scan. This exists because several original WIs are already marked resolved while their bridge/source files remain dirty, causing dispatcher terminal-work-item reconciliation to suppress child repair review.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5370` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/per_thread_finalization_repair.py`, `platform_tests/scripts/test_per_thread_finalization_repair.py`, `docs/procedures/per-thread-finalization-repair.md`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
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

## Prior Deliberations

- `DELIB-202665674` - Loyal Opposition Verdict -- GO (no-source-change direct-thread reconciliation accepted)
- `DELIB-202666063` - Verification Verdict - WI-5107 bridge-helper no-window subprocess (NO-GO)
- `DELIB-20260716-WI5169-ALIBABA-H-REARM-BUDGET-LIVE` - Owner decision: Alibaba budget live; re-arm harness H dispatch eligibility now (WI-5169 EXPEDITE)
- `DELIB-20266609` - GT-KB Bridge Verification Verdict - WI-4935 dispatch failover stale state reconciliation - 005
- `DELIB-20265732` - Loyal Opposition Verification Verdict: WI-4691 Verified Finalization Repair

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5370`.

## Proposed Scope

- Classify terminal VERIFIED residue whose body fails write_verdict.validate_verified_body() as blocked_invalid_verdict_body instead of repair_candidate.
- Report the helper validation reason and route those threads to archive/remove plus LO reissue, not direct finalization.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-finalizer-body-validation-classification |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Planner output separates helper-valid clean-target candidates from invalid-body terminal residues.
- Focused tests cover a terminal VERIFIED body missing Recommended commit type and preserve the existing clean-target candidate fixture.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/per_thread_finalization_repair.py`
- `platform_tests/scripts/test_per_thread_finalization_repair.py`
- `docs/procedures/per-thread-finalization-repair.md`

## Recommended Commit Type

`feat`
