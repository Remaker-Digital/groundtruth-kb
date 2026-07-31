NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Repair repo-wide failed VERIFIED finalization residue

bridge_kind: prime_proposal
Document: gtkb-wi5370-missing-targets-wi5316-failed-verified-finalization-repair
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: ["bridge/gtkb-wi5316-failed-verified-finalization-repair-007.md", "independent-progress-assessments/WI-5370-gtkb-wi5316-failed-verified-finalization-repair-007.missing-targets-terminal.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Archive and remove the malformed terminal VERIFIED artifact for gtkb-wi5316-failed-verified-finalization-repair whose prior report/proposal lacks parseable target_paths.

Work item description: Live umbrella work item for repairing residual failed file-only terminal VERIFIED verdicts and restoring per-thread finalization after the 2026-07-16 repo-wide uncommitted-file sprawl scan. This exists because several original WIs are already marked resolved while their bridge/source files remain dirty, causing dispatcher terminal-work-item reconciliation to suppress child repair review.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5370` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge/gtkb-wi5316-failed-verified-finalization-repair-007.md`, `independent-progress-assessments/WI-5370-gtkb-wi5316-failed-verified-finalization-repair-007.missing-targets-terminal.md`.

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
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265893` - Resolve WI-4772 + WI-4775 as covered by VERIFIED gtkb-verified-finalization-validation-hardening (may29-hygiene retirement)
- `DELIB-20266609` - GT-KB Bridge Verification Verdict - WI-4935 dispatch failover stale state reconciliation - 005
- `DELIB-20260716-WI5169-ALIBABA-H-REARM-BUDGET-LIVE` - Owner decision: Alibaba budget live; re-arm harness H dispatch eligibility now (WI-5169 EXPEDITE)
- `DELIB-202665674` - Loyal Opposition Verdict -- GO (no-source-change direct-thread reconciliation accepted)
- `DELIB-20265752` - Loyal Opposition NO-GO Verification Verdict - WI-4718 Reverification

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5370`.

## Proposed Scope

- Reconfirm bridge/gtkb-wi5316-failed-verified-finalization-repair-007.md is an untracked terminal VERIFIED artifact and fails canonical finalization because the prior report/proposal lacks concrete target_paths or Files Expected To Change evidence.
- Archive the current live bytes (2103 bytes, SHA-256 6D8462E61E5D658100A90439021E6096AEFEA9D59584756F536A86664F2429D2, Git blob 4a153bb0928414b543dfb0c9e74b69bac5922099) to independent-progress-assessments/WI-5370-gtkb-wi5316-failed-verified-finalization-repair-007.missing-targets-terminal.md, verify byte/hash/blob equality, and remove only bridge/gtkb-wi5316-failed-verified-finalization-repair-007.md.
- Leave all implementation source/test/rule/runbook paths untouched; this repair only restores the source thread to a non-terminal reviewable state for a separate scope-correction or finalizer-policy disposition.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Run scoped git status before and after for the failed verdict and archive target; confirm no index/staged-path changes are made. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run gt bridge show before and after removal and confirm only the numbered terminal file is removed from the live chain. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Record the planner/finalizer rejection caused by missing concrete target path scope; replacement or disposition remains separate independent bridge work. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Compare source and archive byte length, SHA-256, Git blob hash, and byte sequence before removing the source file. |

## Acceptance Criteria

- The malformed terminal verdict bytes are preserved exactly in the declared archive before deletion.
- gt bridge show gtkb-wi5316-failed-verified-finalization-repair --json --compact no longer reports bridge/gtkb-wi5316-failed-verified-finalization-repair-007.md as the latest path after removal.
- No source/test/rule/runbook files, staged index entries, dispatcher state, database rows, or active WI-5320/WI-5328/WI-5330 program files are modified.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `bridge/gtkb-wi5316-failed-verified-finalization-repair-007.md`
- `independent-progress-assessments/WI-5370-gtkb-wi5316-failed-verified-finalization-repair-007.missing-targets-terminal.md`

## Recommended Commit Type

`feat`
