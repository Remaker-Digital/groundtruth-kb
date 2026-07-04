NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; role=Prime Builder; sandbox=danger-full-access; approval=never
author_metadata_source: codex-interactive

# Implementation Proposal - Phase 3 gap 10: prioritization, release gating, and duplicate-work control

bridge_kind: prime_proposal
Document: gtkb-wi4972-phase3-prioritization-release-gating
Version: 001
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4972-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4972

target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-PRIORITY-GATING-2026-07-04.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a documentation/governance-only WI-4972 proposal to turn the VERIFIED WI-4963 corpus manifest and benchmark report into a Phase 3 release-gating/duplicate-work-control classification artifact before launching further child implementation.

Work item description: Classify Phase 3 gaps as release-blocking, advisory, or typed-waiver candidates; avoid duplicating active Phase 2 and envelope-sharding work by requiring child proposals to link, reuse, supersede, or explicitly exclude existing covered work.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4972` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-PRIORITY-GATING-2026-07-04.md`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
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
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202665175` - Verdict Summary
- `DELIB-202665180` - Verdict Summary
- `DELIB-202665283` - LO Review: gtkb-headless-dispatch-model-pinning REVISED
- `DELIB-202665176` - Verdict Summary
- `DELIB-202665127` - Loyal Opposition Verdict — Session/Activity Envelope Sharding Taxonomy and Global Baseline

## Owner Decisions / Input

- `DELIB-202665197` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4972-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-4972`.

## Proposed Scope

- Create a governed Phase 3 prioritization and release-gating report using the VERIFIED WI-4963 corpus manifest plus the July 3 harness/model benchmark report.
- Classify open Phase 3 child WIs as release-blocking, advisory, typed-waiver, superseded, deferred, or implementable, with evidence and downstream routing.
- Identify overlap with Phase 2 parity, envelope-sharding, WI-4516, WI-4975, WI-5002, WI-5005, WI-4969, and WI-4791 so follow-on child proposals must link, reuse, supersede, or explicitly exclude covered work.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm bridge chain latest status and target_paths authorize only the additive report artifact before implementation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm missing_required_specs is empty. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry forward the spec-to-verification mapping and exact read-only commands in the post-implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Use gt backlog/project reads to confirm classifications derive from MemBase current state and do not create a competing backlog authority. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CROSS-HARNESS-PARITY-001` | Inspect the report table for all active Phase 3 harness-equivalence lanes and verify each has a classification and evidence route. |

## Acceptance Criteria

- The report includes a per-WI classification table for Phase 3 WIs and linked strategic benchmark/disposition WIs.
- Each classification cites evidence from verified bridge threads, live backlog/project state, or the requested benchmark insight file.
- The report includes an Architecture Alignment Ledger covering OPS consolidation, dispatcher daemon architecture, lifecycle-first/scoring-last precedence, and portfolio reconciliation findings.
- No protected source, config, hook, test, credential, provider-route, dispatcher-topology, or durable-role mutation occurs in this slice.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-PRIORITY-GATING-2026-07-04.md`

## Recommended Commit Type

`feat`
