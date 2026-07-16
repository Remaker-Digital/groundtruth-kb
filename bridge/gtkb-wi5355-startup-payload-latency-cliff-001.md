NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f68b0-30a8-7843-867b-6f37d981a975
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Remove the 60-second cliff from direct startup payload verification

bridge_kind: prime_proposal
Document: gtkb-wi5355-startup-payload-latency-cliff
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5355-STARTUP-PAYLOAD-LATENCY-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5355

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_startup_payload_latency.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the independently reproduced startup payload timing cliff: LO timed out at 60 seconds and a fresh isolated PB rerun passed in 59.32 seconds. Preserve the real direct execution contract while adding bounded diagnostics and material latency headroom. Implementation is sequenced after WI-5328 terminal verification.

Work item description: Independent WI-5328 verification timed out platform_tests/scripts/test_session_self_initialization.py::test_direct_script_execution_emits_startup_payload at its hardcoded 60-second subprocess limit. A fresh isolated PB rerun passed in 59.32 seconds, leaving less than one second of margin and reproducing the underlying timing cliff. Diagnose the direct scripts/session_self_initialization.py --emit-startup-service-payload --fast-hook path, preserve the real direct-execution import and JSON-shape coverage, expose bounded phase timing/timeout diagnostics, and make repeated execution complete with material headroom under normal concurrent fleet load. Do not paper over the defect solely by raising the test timeout, disable startup intelligence, terminate unrelated workers, or reconfigure dispatcher/TAFE state.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5355` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/session_self_initialization.py`, `platform_tests/scripts/test_session_startup_payload_latency.py`.

## Specification Links

- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - auto-linked governing or work-item specification.
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

- `DELIB-202666166` - WI-5206 - Dedicated minimal fast-wrapup path - Loyal Opposition Proposal Review
- `DELIB-20263466` - Loyal Opposition Advisory - WI-4443 Implementation Authorization Current Pointer Disposition
- `DELIB-20266136` - Owner decision: fix WI-4845 via configurable worker-lifetime cap plus LO-review budget
- `DELIB-20263378` - Owner decision: startup-service timeout fix scope (WI-4564, A+C)
- `DELIB-0110` - S227 Tier 3/4 Batch Review (463f989c)

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5355-STARTUP-PAYLOAD-LATENCY-20260716` - active project authorization covering `WI-5355`.

## Proposed Scope

- After WI-5328 reaches an independent terminal verdict, instrument the direct fast-hook startup payload path with bounded phase-level latency evidence sufficient to identify the slow operation without exposing secrets or unbounded payload growth.
- Bound or eliminate the diagnosed slow fast-hook operation while preserving the real scripts/session_self_initialization.py direct execution, SessionStart JSON shape, required startup intelligence, and fail-soft behavior.
- Add isolated repeated-run and injected-delay coverage in a new focused test module; retain the existing direct execution integration test as a production-interface guard.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Run repeated real direct-script payload executions plus injected-delay focused tests and report per-phase and end-to-end latency with a documented headroom threshold. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the new focused module, the existing direct-execution test, and the complete session-self-initialization target file before independent verification. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- The implementation must not resolve the defect solely by raising the 60-second test timeout, skipping all startup intelligence, killing unrelated processes, disabling hooks, or mutating dispatcher/TAFE eligibility.
- Repeated direct fast-hook payload executions complete with material documented headroom below the production allowance during ordinary concurrent fleet work.
- A delayed internal phase terminates within its own bound and reports a named sanitized phase diagnostic instead of surfacing only subprocess.TimeoutExpired.
- Valid output remains parseable SessionStart JSON and existing startup/session-envelope suites do not regress.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_startup_payload_latency.py`

## Recommended Commit Type

`feat`
