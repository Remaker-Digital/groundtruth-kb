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
Document: gtkb-wi5370-wi5211-reappeared-invalid-terminal-cleanup
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: ["bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md", "independent-progress-assessments/WI-5370-wi5211-verdict-008.reappeared-invalid-finalizer.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Archive and remove the current reappeared invalid terminal VERIFIED artifact for gtkb-wi5211-df-governed-verdict-publication-parity without touching source/test implementation paths.

Work item description: Live umbrella work item for repairing residual failed file-only terminal VERIFIED verdicts and restoring per-thread finalization after the 2026-07-16 repo-wide uncommitted-file sprawl scan. This exists because several original WIs are already marked resolved while their bridge/source files remain dirty, causing dispatcher terminal-work-item reconciliation to suppress child repair review.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5370` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md`, `independent-progress-assessments/WI-5370-wi5211-verdict-008.reappeared-invalid-finalizer.md`.

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

- `DELIB-202666063` - Verification Verdict - WI-5107 bridge-helper no-window subprocess (NO-GO)
- `DELIB-20265752` - Loyal Opposition NO-GO Verification Verdict - WI-4718 Reverification
- `DELIB-20266204` - Owner reconciliation decision batch 2: resolve 2 verified-done drift WIs (WI-3405, WI-4566)
- `DELIB-20265884` - Owner decisions: supersede WI-4731 (dup of WI-4741) + new resolve-path actuation defect WI in hygiene project
- `DELIB-20266133` - Owner decision: re-home all open DISPATCHER-COMPLETION work and retire the project

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5370`.

## Proposed Scope

- Reconfirm bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md is an untracked terminal VERIFIED artifact and fails canonical finalizer body validation.
- Archive the current live bytes (2309 bytes, SHA-256 69E30C790BE250D0F1D13096AAA667B0DB25629757349849B0A64BADE080A871, Git blob 4a3605005295c4249c290e1888fde72b76513f33) to independent-progress-assessments/WI-5370-wi5211-verdict-008.reappeared-invalid-finalizer.md, verify byte/hash/blob equality, and remove only bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md.
- Do not overwrite older repair archives; this cleanup preserves the current reappeared version 008 bytes separately for auditability.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Run scoped git status before and after for the failed verdict and archive target; confirm no index/staged-path changes are made. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run gt bridge show before and after removal and confirm only the numbered terminal file is removed from the live chain. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run write_verdict.validate_verified_body against the current terminal body and record the canonical rejection; replacement VERIFIED remains independent LO finalizer work. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Compare source and archive byte length, SHA-256, Git blob hash, and byte sequence before removing the source file. |

## Acceptance Criteria

- The current invalid terminal verdict bytes are preserved exactly in the declared archive before deletion.
- gt bridge show gtkb-wi5211-df-governed-verdict-publication-parity --json --compact reports the pre-terminal implementation/report version after the invalid terminal file is removed.
- No source/test/rule/runbook files, staged index entries, dispatcher state, database rows, or active WI-5320/WI-5328/WI-5330 program files are modified.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md`
- `independent-progress-assessments/WI-5370-wi5211-verdict-008.reappeared-invalid-finalizer.md`

## Recommended Commit Type

`feat`
