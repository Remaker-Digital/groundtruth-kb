NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop Prime Builder interactive session, ::init gtkb pb

# Implementation Proposal - Doctor dispatch liveness treats empty-queue stale recipients as false ALARM

bridge_kind: prime_proposal
Document: gtkb-wi4898-empty-queue-dispatch-liveness-false-alarm
Version: 001
Date: 2026-06-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4898

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair gt project doctor bridge-dispatch liveness false alarm by treating stale recipient rows with pending_count=0 and a fresh top-level dispatch-state heartbeat as an empty-queue non-failure, while preserving ALARM/FAIL for stale recipient rows with pending actionable work.

Work item description: gt project doctor can report FAIL for Claude/Codex bridge dispatch liveness when a recipient row updated_at is older than 10 minutes even though the dispatch-state top-level heartbeat is fresh and the recipient has no pending actionable queue. The LO empty-queue doctor audit at independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-28-05-15-lo-empty-queue-doctor-audit.md classifies this as alarm fatigue: inactive empty queues should not fail liveness solely because there was no new dispatch to refresh recipient state.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4898` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py`.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - auto-linked governing or work-item specification.
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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-0101` - Bridge Poller Staleness And Wake Churn Review
- `DELIB-20266140` - Owner decision: WI-4804 kill-switch handling - visibility (doctor warning), not auto-clear
- `DELIB-0132` - Untitled LO Report
- `DELIB-0100` - Bridge Operational Signals Note
- `DELIB-0121` - Bridge Ops / Reporting Proposal Using Codex Automations

## Owner Decisions / Input

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-4898`.

## Proposed Scope

- Update _check_bridge_dispatch_liveness so stale per-recipient updated_at is non-failing only when pending_count is zero and the top-level dispatch-state heartbeat is fresh.
- Keep missing or unparseable recipient updated_at failures, stale pending queue failures, and stale top-level dispatch-state warnings intact.
- Add public run_doctor regression coverage for the empty-queue non-failure and the stale-pending failure path.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | New TEST-11239 regression: test_run_doctor_passes_stale_empty_queue_when_top_level_dispatch_state_is_fresh covers stale recipient + pending_count=0 + fresh top-level heartbeat as non-failing. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation begins only after LO GO plus matching claim and implementation authorization packet. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Existing stale-over-10-minute and recipient-mapping tests are updated to include pending work, preserving fail/ALARM when queued work is stale. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- gt project doctor bridge-dispatch checks do not fail solely because an empty queue has no recent dispatch timestamp when dispatch-state.json itself is fresh.
- A stale recipient with pending_count greater than zero still reports fail/ALARM.
- The targeted doctor bridge-dispatch liveness test suite and ruff checks pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py`

## Recommended Commit Type

`feat`
