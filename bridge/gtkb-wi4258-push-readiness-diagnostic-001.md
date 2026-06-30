NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f17c3-3df4-7141-a6bd-43a6356ae28e
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Read-only push readiness diagnostic

bridge_kind: prime_proposal
Document: gtkb-wi4258-push-readiness-diagnostic
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE
Work Item: WI-4258

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/governance/push_readiness.py", "platform_tests/groundtruth_kb/governance/test_push_readiness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement WI-4258 by adding a read-only push readiness diagnostic that reports credential-helper, GitHub CLI auth, remote reachability, and interactive prompt risk without mutating credentials or remotes.

Work item description: Add a read-only diagnostic for non-interactive push readiness that inspects credential helper chain, GitHub CLI authentication state, remote access, and GUI prompt or hang risk without creating, deleting, rotating, or editing credentials.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4258` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/governance/push_readiness.py`, `platform_tests/groundtruth_kb/governance/test_push_readiness.py`.

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-20266470` - Separation Check
- `DELIB-20266436` - Separation Check
- `DELIB-20265887` - Owner approval: close WI-4755 as covered (v6 alignment already exists)
- `DELIB-20266078` - Loyal Opposition Review - WI-4760 Make the cross-harness trigger kill-switch loud
- `DELIB-20266133` - Owner decision: re-home all open DISPATCHER-COMPLETION work and retire the project

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-4258`.

## Proposed Scope

- Add a read-only gt push readiness diagnostic that reports Git credential-helper configuration, GitHub CLI authentication status, remote access reachability, and likely interactive prompt or hang risk.
- Classify credential or auth problems as evidence for owner action only; do not create, delete, rotate, edit, refresh, or upload credentials.
- Keep all external checks read-only and bounded with deterministic subprocess timeouts so the diagnostic cannot hang an automation run.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge applicability and ADR/DCL clause preflights before filing and after implementation reporting. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Focused tests prove the Windows/Codex-oriented diagnostic is usable from the repo CLI without Bash-only behavior. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | The implementation remains inside the active WI-4258 project authorization and excludes credential lifecycle mutation. |

## Acceptance Criteria

- The diagnostic emits machine-readable and human-readable evidence for healthy gh-helper state, missing or invalid gh auth, multiple-helper ambiguity, inaccessible remote, and likely GUI prompt risk.
- Credential lifecycle changes are never attempted; credential issues are surfaced as owner-action evidence only.
- Focused tests use mocked subprocess results and perform no real network, credential, or remote mutation.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/governance/push_readiness.py`
- `platform_tests/groundtruth_kb/governance/test_push_readiness.py`

## Recommended Commit Type

`feat`
