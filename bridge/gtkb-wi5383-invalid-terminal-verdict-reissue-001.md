NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Require implementation and commit evidence before VERIFIED backlog closure

bridge_kind: prime_proposal
Document: gtkb-wi5383-invalid-terminal-verdict-reissue
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5383-VERIFIED-CLOSURE-EVIDENCE-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5383

target_paths: ["bridge/gtkb-wi5383-verified-closure-evidence-008.md", "independent-progress-assessments/WI-5383-invalid-terminal-verdict-008.finalization-diagnostic.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Archive and remove only the malformed untracked WI-5383 VERIFIED version 008, restore the source thread to its implementation report, and require independent Loyal Opposition to reissue version 008 through the canonical verified finalizer.

Work item description: At 2026-07-16T22:43Z the bridge VERIFIED backlog reconciler resolved WI-5230 because its latest bridge status was VERIFIED, even though version 004 only verified that the preceding NO-ACTION disposition was correct and explicitly stated the implementation never started and still requires a fresh GO. The same reconciler resolved WI-5361 although its verdict explicitly deferred atomic finalization and its source, test, and bridge chain were absent from HEAD. This conflates verdict token terminality with implementation completion and contradicts the work-item status evidence. Require typed verdict-purpose classification plus terminal commit coverage before closure: VERIFIED-on-NO-ACTION must remain traceability evidence without completing implementation, and source-bearing VERIFIED work must remain open until the exact implementation and verdict chain are present in a focused terminal commit. Candidate only; grants no backlog correction, source, dispatcher, TAFE, Git, or runtime mutation authority.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5383` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge/gtkb-wi5383-verified-closure-evidence-008.md`, `independent-progress-assessments/WI-5383-invalid-terminal-verdict-008.finalization-diagnostic.md`.

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666173` - Loyal Opposition Verdict: NO-GO (finalization-scoped) — WI-5210 Provider LO Governed Verdict Publication
- `DELIB-20265758` - Verdict
- `DELIB-20265570` - Owner waiver: finalize WI-4723 VERIFIED by reference to commit e9ffc26d5 (same-commit finalization gate waived, narrow)
- `DELIB-20265399` - Loyal Opposition Review - WI-4675 Scan-Bridge Token Parity Reconciliation
- `DELIB-20265510` - Owner waiver: finalize WI-4681 VERIFIED by reference to commit 9759c5cd9 (same-commit finalization gate waived, narrow)

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5383-VERIFIED-CLOSURE-EVIDENCE-20260716` - active project authorization covering `WI-5383`.

## Proposed Scope

- Record exact length, SHA-256, Git blob, Git status, canonical validator diagnostic, and byte equality for the malformed version 008 in the approved in-root diagnostic archive.
- After independent GO, a matching claim, and implementation-start authorization, remove only the byte-verified untracked malformed version 008 so the source thread returns to latest NEW implementation report version 007.
- Require independent Loyal Opposition to reissue version 008 through write_verdict.py --finalize-verified with the correct implementation-report reference and exact focused include set.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show the source thread before removal, after removal, and after independent helper-mediated reissue; Prime Builder never authors VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run validate_verified_body against the current and replacement verdicts and require the replacement to pass with report-linked spec-to-test evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Rerun the per-thread finalization planner and confirm the invalid-body blocker is absent after valid reissue/finalization. |
| `GOV-WORK-TREE-HYGIENE-001` | Compare exact length, SHA-256, Git blob, Git status, and byte equality before removal; inspect path-scoped Git status afterward. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Require a live matching claim and named implementation-start packet covering exactly the malformed verdict and diagnostic archive before mutation. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- The malformed version 008 bytes are durably archived and hash-verified before only that untracked bridge file is removed.
- The source thread returns to version 007 NEW until independent Loyal Opposition publishes a helper-valid replacement VERIFIED version 008.
- No source, test, database, dispatcher, TAFE, runtime, lease, harness, credential, shared-index, push, deployment, release, or unrelated path is mutated.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `bridge/gtkb-wi5383-verified-closure-evidence-008.md`
- `independent-progress-assessments/WI-5383-invalid-terminal-verdict-008.finalization-diagnostic.md`

## Recommended Commit Type

`feat`
