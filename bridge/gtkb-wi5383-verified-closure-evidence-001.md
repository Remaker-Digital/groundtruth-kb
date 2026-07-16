NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Require implementation and commit evidence before VERIFIED backlog closure

bridge_kind: prime_proposal
Document: gtkb-wi5383-verified-closure-evidence
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5383-VERIFIED-CLOSURE-EVIDENCE-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5383

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Prevent the VERIFIED backlog reconciler from closing implementation work when VERIFIED only affirms a NO-ACTION disposition or when the approved implementation and terminal verdict are absent from the focused Git commit.

Work item description: At 2026-07-16T22:43Z the bridge VERIFIED backlog reconciler resolved WI-5230 because its latest bridge status was VERIFIED, even though version 004 only verified that the preceding NO-ACTION disposition was correct and explicitly stated the implementation never started and still requires a fresh GO. The same reconciler resolved WI-5361 although its verdict explicitly deferred atomic finalization and its source, test, and bridge chain were absent from HEAD. This conflates verdict token terminality with implementation completion and contradicts the work-item status evidence. Require typed verdict-purpose classification plus terminal commit coverage before closure: VERIFIED-on-NO-ACTION must remain traceability evidence without completing implementation, and source-bearing VERIFIED work must remain open until the exact implementation and verdict chain are present in a focused terminal commit. Candidate only; grants no backlog correction, source, dispatcher, TAFE, Git, or runtime mutation authority.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5383` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_verified_backlog_reconciler.py`, `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`.

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

## Prior Deliberations

- `DELIB-20265570` - Owner waiver: finalize WI-4723 VERIFIED by reference to commit e9ffc26d5 (same-commit finalization gate waived, narrow)
- `DELIB-202666173` - Loyal Opposition Verdict: NO-GO (finalization-scoped) — WI-5210 Provider LO Governed Verdict Publication
- `DELIB-20265758` - Verdict
- `DELIB-20265510` - Owner waiver: finalize WI-4681 VERIFIED by reference to commit 9759c5cd9 (same-commit finalization gate waived, narrow)
- `DELIB-20265399` - Loyal Opposition Review - WI-4675 Scan-Bridge Token Parity Reconciliation

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5383-VERIFIED-CLOSURE-EVIDENCE-20260716` - active project authorization covering `WI-5383`.

## Proposed Scope

- Structurally classify VERIFIED evidence by the status and artifact it responds to; a VERIFIED verdict responding to NO-ACTION is non-implementation disposition evidence and cannot satisfy an implementation work item.
- Reuse the GO-approved target_paths as the authoritative implementation set, locate the commit containing the terminal VERIFIED artifact, and fail closed when the verdict or any approved non-bridge target is absent from that commit.
- Expose deterministic no_action_verified, missing_implementation_commit_coverage, malformed_target_metadata, and genuinely_closable reasons in dry-run and repair classification without parsing free-form completion claims.
- Preserve satisfied umbrella, advisory, withdrawn, bridge-only governance, parent-evidence, and repair-overbroad behavior; do not mutate Git, bridge history, dispatcher, TAFE, workers, leases, eligibility, or unrelated MemBase rows.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run TEST-11498 fixtures over VERIFIED-on-NO-ACTION, uncommitted verdict, omitted approved target, and valid focused-commit histories; require deterministic fail-closed reasons. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the complete focused reconciler suite plus Ruff check and format on the exact source and test targets. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- TEST-11498 proves VERIFIED responding to NO-ACTION leaves the work item open and reports no_action_verified.
- An untracked terminal verdict or a terminal commit missing any GO-approved source/test target leaves the work item open with missing_implementation_commit_coverage.
- A focused commit containing the terminal verdict and every approved target remains genuinely closable; governed bridge-only or explicit waiver cases preserve their intended behavior.
- Repair audit identifies the live WI-5230 and WI-5361 false-closure classes without applying a database correction, and all existing focused tests remain green.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_verified_backlog_reconciler.py`
- `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`

## Recommended Commit Type

`feat`
