NEW
author_identity: codex
author_harness_id: A
author_session_context_id: codex-auto-builder-20260630T051717Z
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex Desktop automation; Prime Builder; Auto-builder; reasoning default

# Implementation Proposal - Build a first-class gap-state formal-artifact MemBase capture lane

bridge_kind: prime_proposal
Document: gtkb-wi3378-gap-state-formal-artifact-capture-lane
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3378

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_spec_record.py", "groundtruth-kb/src/groundtruth_kb/cli_deliberations_record.py", "groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py", "platform_tests/groundtruth_kb/cli/test_spec_record.py", "platform_tests/groundtruth_kb/cli/test_deliberations_record.py", "platform_tests/groundtruth_kb/governance/test_approval_packet.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Build the governed formal-artifact MemBase capture lane needed when a bridge proposal is intentionally in requirement-sufficiency gap state.

Work item description: GT-KB has no mechanically-valid execution path for a bridge proposal classified gap-state (Requirement Sufficiency of New or revised requirement required before implementation) to perform a formal-artifact MemBase insert: a gap-state proposal cannot obtain an implementation-start authorization packet, so formal-artifact capture in gap-state has no governed lane. Surfaced by Codex in bridge gtkb-s358-w2-agent-red-gov-trio-v2 -006 as Option B and Opportunity Radar. W2 worked around it by adopting first-state Requirement Sufficiency per -006 Option A; the general gap-state capture lane remains unbuilt.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-3378` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli_spec_record.py`, `groundtruth-kb/src/groundtruth_kb/cli_deliberations_record.py`, `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py`, `platform_tests/groundtruth_kb/cli/test_spec_record.py`, `platform_tests/groundtruth_kb/cli/test_deliberations_record.py`, `platform_tests/groundtruth_kb/governance/test_approval_packet.py`.

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
- `GOV-ARTIFACT-APPROVAL-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266131` - Cursor LO Bridge Auto-Process — Session S481
- `DELIB-20265903` - Verdict
- `DELIB-20266139` - Owner decision: WI-4838 reliability fast-lane authorization
- `DELIB-20266319` - Separation Check
- `DELIB-20266042` - Loyal Opposition Review - WI-4779 Session-Context Review Independence Startup Rationale

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-3378`.

## Proposed Scope

- Add a governed gap-state capture lane for formal-artifact MemBase inserts that have owner approval evidence but cannot obtain implementation-start authority because the bridge proposal itself is parked in requirement-sufficiency gap state.
- Extend the existing spec and deliberation record services to accept an explicit gap-state capture context without relaxing owner-presented, AUQ, approval-packet, packet-hash, or project-root validation.
- Keep the lane narrow: no production deployment, no credential changes, no spec deletion, and no bypass of ordinary implementation-start packets for source mutations.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | python scripts/implementation_authorization.py begin --bridge-id gtkb-wi3378-gap-state-formal-artifact-capture-lane |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | python -m pytest platform_tests/groundtruth_kb/cli/test_spec_record.py platform_tests/groundtruth_kb/cli/test_deliberations_record.py -q --tb=short |
| `GOV-ARTIFACT-APPROVAL-001` | python -m pytest platform_tests/groundtruth_kb/governance/test_approval_packet.py platform_tests/groundtruth_kb/cli/test_spec_record.py -q --tb=short |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | python -m pytest platform_tests/groundtruth_kb/cli/test_spec_record.py platform_tests/groundtruth_kb/cli/test_deliberations_record.py -q --tb=short |

## Acceptance Criteria

- A gap-state capture request can dry-run and persist a formal approval packet plus the intended MemBase operation only when owner-presented AUQ evidence and approved packet content are valid.
- The normal governed record paths still reject missing owner-presented evidence, missing AUQ evidence, content outside the project root, duplicate artifact IDs, and malformed approval packets.
- Tests cover success and fail-closed behavior for both spec and deliberation capture surfaces plus approval-packet validation.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_spec_record.py`
- `groundtruth-kb/src/groundtruth_kb/cli_deliberations_record.py`
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py`
- `platform_tests/groundtruth_kb/cli/test_spec_record.py`
- `platform_tests/groundtruth_kb/cli/test_deliberations_record.py`
- `platform_tests/groundtruth_kb/governance/test_approval_packet.py`

## Recommended Commit Type

`feat`
