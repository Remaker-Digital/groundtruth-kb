NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-03T18-23-43Z
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop Prime Builder; reasoning effort Extra High

# Implementation Proposal - Classify deterministic impl-auth quarantine non-work as healthy dispatch state

bridge_kind: prime_proposal
Document: gtkb-wi5000-impl-auth-quarantine-health-pass
Version: 001
Date: 2026-07-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5000-IMPL-AUTH-HEALTH-PASS
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5000

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Fix the remaining dispatcher-stability false WARN: when all selected Prime Builder work is deterministically suppressed as all_impl_auth_quarantined before any worker launch, dispatch health should report healthy non-work instead of WARN, while status/report retain the blocked_non_activatable slug and reason.

Work item description: Current live dispatcher health reports WARN when Codex PB has exactly one deterministic all_impl_auth_quarantined non-launch for a GO whose Requirement Sufficiency blocks implementation. WI-4992 suppresses repeat launches correctly, but the health classifier still presents the known non-work state as unhealthy. Stable unattended bridge operation should surface the blocked_non_activatable item in status/report while returning PASS when there are no live workers, no runtime failures, and no repeat launch churn.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5000` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
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
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-202665145` - NO-GO: WI-4943 Implementation Report v007 — additional dependency gaps block release-branch completion
- `DELIB-202665154` - Verdict: NO-GO
- `DELIB-202665153` - NO-GO: WI-4944 — sandbox Git permissions prevent focused commit; environmental blocker sustained
- `DELIB-202665178` - Verdict: NO-GO
- `DELIB-202665228` - Verdict: NO-GO

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5000-IMPL-AUTH-HEALTH-PASS` - active project authorization covering `WI-5000`.

## Proposed Scope

- Change only dispatcher health/runtime classification for deterministic all_impl_auth_quarantined non-launch states; do not alter implementation authorization denial behavior.
- Preserve operator visibility of the blocked slug/reason in dispatch status/report and Prime Builder bridge scans.
- Update focused tests so stale subprocess_failure evidence is ignored without producing a health WARN for deterministic non-work.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused tests assert deterministic impl-auth quarantine is suppressed as non-work and no longer degrades dispatch health. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
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
| `ADR-DISPATCHER-ARCHITECTURE-001` | Implementation remains inside dispatcher health/config reporting code; no direct harness launch or fallback is added. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Tests preserve implementation authorization refusals as authoritative and only change health classification after denial. |

## Acceptance Criteria

- gt bridge dispatch health --json returns PASS when the only current Prime Builder condition is all_impl_auth_quarantined non-work with no live workers or real runtime failures.
- Prime Builder bridge scan still lists the blocked_non_activatable role-authority GO and its requirement-sufficiency reason.
- Focused pytest and ruff checks pass for bridge_dispatch_config health/report coverage.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

## Recommended Commit Type

`feat`
