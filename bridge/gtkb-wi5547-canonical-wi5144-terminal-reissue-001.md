NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; governed WI-5547 canonical-only repair proposal
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Repair reappeared WI-5144 malformed terminal verdict through canonical-only reissue

bridge_kind: prime_proposal
Document: gtkb-wi5547-canonical-wi5144-terminal-reissue
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5547-CANONICAL-WI5144-TERMINAL-REISSUE-20260718
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5547

target_paths: ["bridge/gtkb-wi5144-hp08-semantic-adapter-drift-010.md", "bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-001.md", "bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-002.md", "bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-003.md", "bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-004.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Canonically repair WI-5144 finalization by removing one malformed untracked terminal verdict and its four obsolete untracked repair artifacts without archival dependency, then require independent LO reissue through the atomic finalizer. This proposal does not change implementation source/tests, dispatcher/TAFE state, harness configuration, routing, eligibility, allowances, or unrelated Git state.

Work item description: The independently reviewed WI-5144 implementation is committed and clean, but its untracked terminal VERIFIED artifact fails the canonical finalization planner because it lacks a machine-readable Responds-to report reference and required finalizer evidence. An earlier untracked repair chain reached a transient removal state by depending on a retired noncanonical archive surface; that state regressed and those repair artifacts cannot be adopted or committed. Under an independent GO, exact claim, and implementation-start packet, remove only the malformed terminal and obsolete untracked repair artifacts without archival dependency, restore WI-5144 latest state to its v009 implementation report, and require an independent Loyal Opposition to reissue VERIFIED through the canonical atomic finalizer with focused commit provenance. Preserve all implementation source/test bytes, unrelated dirt, dispatcher/TAFE state, live workers, roles, routing, eligibility, allowances, Git index classification, push, release, and deployment.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5547` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-010.md`, `bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-001.md`, `bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-002.md`, `bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-003.md`, `bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-004.md`.

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
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666774` - WI-5370 Sprawl Reconciliation - Owner Decisions and Findings
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-RECONCILIATION` - GT-KB Platform Modernization Gate 0 reconciliation inventory
- `DELIB-202666645` - LO Review - WI-5370 No-Responds Repair Implementation Report (wi5383-invalid-terminal-verdict-reissue)
- `DELIB-202666294` - Loyal Opposition NO-GO Verdict - WI-5249 Prime NO-ACTION Claim/Filer
- `DELIB-202666649` - LO Review - WI-5370 No-Responds Repair Implementation Report (wi5384-agent-red-portability-baseline)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5547-CANONICAL-WI5144-TERMINAL-REISSUE-20260718` - active project authorization covering `WI-5547`.

## Proposed Scope

- After independent GO, acquire the exact WI-5547 work-intent claim and implementation-start packet, then remove only the five declared untracked bridge artifacts; do not copy, archive, quote, cite, recreate, or depend on any retired or noncanonical surface.
- Preserve the committed WI-5144 implementation source and tests byte-for-byte, leave its v009 implementation report in place, and verify the source thread resolves to v009 REVISED immediately after the bounded cleanup.
- Require a fresh independent Loyal Opposition session to review v009 and, if satisfied, reissue a finalizer-valid VERIFIED through the canonical atomic finalizer with focused local commit provenance; Prime Builder must not author that status.
- Preserve unrelated worktree and index classification, dispatcher and TAFE state, harness roles and dispatchability, routing, eligibility, caps, allowances, leases, live workers, credentials, push, release, and deployment.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge applicability and clause preflights; prove the exact five-path before/after inventory, latest-source-thread state, distinct author/reviewer session contexts, and canonical atomic finalizer result. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute TEST-11606 by rerunning the WI-5144 focused parity tests, the per-thread finalization planner filtered to WI-5144, and focused commit-path inspection. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm the malformed terminal state is removed, v009 becomes actionable for LO review, and the source thread returns to one valid terminal VERIFIED through the governed lifecycle. |
| `GOV-WORK-TREE-HYGIENE-001` | Compare exact path-scoped Git status and live-index classification before and after; no broad staging, cleanup, restore, stash, or unrelated mutation is permitted. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Confirm the reissued verdict carries complete target-authored LO identity/model/session metadata and independent session provenance. |

## Acceptance Criteria

- Only the five declared untracked bridge artifacts are removed by the Prime implementation, and exact before/after path readback proves no adjacent bridge or implementation path changed.
- The WI-5144 source thread resolves to committed v009 REVISED after cleanup, with its approved source/test implementation bytes unchanged.
- No canonical artifact created or retained by this repair cites, quotes, archives to, recreates, or depends on a retired or noncanonical surface.
- An independent Loyal Opposition session reissues VERIFIED for WI-5144 through the canonical atomic finalizer with an explicit Responds-to reference to v009, required finalizer evidence, focused commit provenance, and valid implementation coverage.
- The per-thread finalization planner no longer reports WI-5144 as a stop or blocked terminal candidate, while dispatcher, TAFE, harness, lease, and unrelated Git state remain unchanged.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `bridge/gtkb-wi5144-hp08-semantic-adapter-drift-010.md`
- `bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-001.md`
- `bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-002.md`
- `bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-003.md`
- `bridge/gtkb-wi5370-no-responds-wi5144-hp08-semantic-adapter-drift-004.md`

## Recommended Commit Type

`feat`
