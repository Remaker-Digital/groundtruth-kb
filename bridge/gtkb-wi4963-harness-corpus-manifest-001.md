NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; role=Prime Builder; sandbox=danger-full-access; approval=never
author_metadata_source: codex-interactive

# Implementation Proposal - Phase 3 gap 01: transcript and result corpus coverage manifest

bridge_kind: prime_proposal
Document: gtkb-wi4963-harness-corpus-manifest
Version: 001
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4963-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4963

target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-CORPUS-MANIFEST-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Create the WI-4963 harness transcript/result corpus manifest as the upstream evidence base for Phase 3 harness-equivalence work.

Work item description: Create a governed manifest of available transcripts, session envelopes, compact result envelopes, missing archives, and typed waivers for Codex, Claude, Cursor, Antigravity, Ollama, OpenRouter, and Goose/provider-adjacent lanes. Evidence references must include Phase 2 parity artifacts and the session/activity envelope sharding verification chain before any implementation proposal.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4963` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-CORPUS-MANIFEST-*.md`.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
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

- `DELIB-202665120` - Verdict: VERIFIED
- `DELIB-202665126` - Verdict: VERIFIED
- `DELIB-202665178` - Verdict: NO-GO
- `DELIB-202665117` - GO: Envelope Sharding Blocker Repairs — Proposal Review
- `DELIB-202665119` - Loyal Opposition Review — Compact Query Modes For Oversized SoT And Transcript Surfaces

## Owner Decisions / Input

- `DELIB-202665197` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4963-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-4963`.

## Proposed Scope

- Create a governed corpus manifest for available harness transcripts, session envelopes, compact result envelopes, missing archives, and typed waivers across Codex, Claude, Cursor, Antigravity, Ollama, OpenRouter, and provider-adjacent lanes.
- Cite Phase 2 parity artifacts, the session/activity envelope sharding verification chain, and the 2026-07-03 harness+model benchmarking report as evidence inputs.
- Do not mutate protected source, config, tests, hooks, skills, provider credentials, or dispatcher routing.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Manifest cross-references Phase 2 parity artifacts, Phase 3 umbrella bridge evidence, and session/activity envelope sharding evidence before recommending downstream implementation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | gt bridge show gtkb-wi4963-harness-corpus-manifest confirms NEW->GO->NEW report->VERIFIED lifecycle. |
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
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Manifest includes one row or section per harness/provider lane with evidence source, freshness, coverage state, and typed waiver or missing-evidence disposition.
- Manifest explicitly identifies which later work items consume it: WI-4972, WI-4967, WI-4969, and WI-4791.
- Architecture Alignment Ledger ties the slice to ADR-CROSS-HARNESS-PARITY-001 and avoids reopening verified WI-4964 model-pinning work.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-CORPUS-MANIFEST-*.md`

## Recommended Commit Type

`feat`
