NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; build envelope active; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Dispatcher ordinary ops build activity-envelope authority validators

bridge_kind: prime_proposal
Document: gtkb-wi5269-activity-envelope-authority-validators
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5269-ACTIVITY-ENVELOPE-AUTHORITY-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5269

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/activity/profiles.py", "scripts/dispatch_blackbox_gate.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_dispatch_blackbox_gate.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5269 proposes source/test validators for the ordinary/ops/build activity-envelope authority split: ordinary sessions stay on worker-safe packets, ops can govern configuration-only mutation, and build can touch internals only with case-specific bridge/PAUTH/start authorization.

Work item description: Implement the activity-envelope authority model for the black-box boundary. A session envelope without an initialized activity envelope is an ordinary worker. An ops activity envelope may mutate only black-box configuration surfaces for the bridge/TAFE/harness complex. A build activity envelope may directly mutate black-box internals only when a case-specific authorization is present. Validators must prevent ops/build authority from being interchangeable and must leave ordinary workers on worker-safe packet surfaces.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5269` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/session/envelope.py`, `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`, `scripts/dispatch_blackbox_gate.py`, `scripts/implementation_authorization.py`, `scripts/implementation_start_gate.py`, `platform_tests/scripts/test_session_envelope_runtime.py`, `platform_tests/scripts/test_dispatch_blackbox_gate.py`, `platform_tests/scripts/test_implementation_authorization.py`.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
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
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES` - Dispatcher black-box ops/build envelope authority
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION` - Dispatcher Black Box Ordinary Worker Definition
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT` - Dispatcher Black Box Full Assigned-Content Safe Packet
- `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE` - Approve runtime interfaces and exclude dispatcher role mapping from worker context
- `DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY` - Dispatcher Black Box Activity Envelope Authority

## Owner Decisions / Input

- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5269-ACTIVITY-ENVELOPE-AUTHORITY-20260717` - active project authorization covering `WI-5269`.

## Proposed Scope

- Add executable validators for the dispatcher black-box authority model: a session envelope with no initialized activity envelope is ordinary, ops activity permits black-box configuration mutation only through governed ops surfaces, and build activity permits direct internals mutation only when the bridge/PAUTH/implementation-start case authorization is present.
- Keep this WI to source/test validation and gate classification. It must not mutate black-box configuration, dispatcher/TAFE runtime state, harness registry state, hook registrations, or config/agent-control files from the current build envelope.
- Wire the authority check into implementation-start and black-box gate paths only to the extent needed to prevent ops/build interchangeability and to leave ordinary workers on worker-safe packet surfaces.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run focused session envelope, black-box gate, and implementation authorization tests showing dispatcher internals remain service-owned and source/internal mutation remains gated. |
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
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Add regression cases for ordinary, ops, build, missing-case, and case-authorized build behavior with explicit denial reasons for authority mismatch. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Assert no activity-envelope or ordinary session output grants raw bridge/dispatcher/TAFE/harness internals access by default. |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | Assert ordinary workers are routed to worker-safe packet surfaces when protected internals/config are requested without authority. |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | Run the proposal/implementation-start authorization tests that prove child implementation remains tied to the active black-box foundation specs and PAUTH. |

## Acceptance Criteria

- Ordinary sessions are detected mechanically from envelope state, not from role label, harness label, or worker prompt text, and are denied protected black-box internals/config mutation except through worker-safe packet reads.
- Ops-envelope authority and build-envelope authority are distinct: ops configuration mutation cannot satisfy direct internals mutation, and build internals authorization cannot satisfy black-box configuration mutation.
- Case-specific build internals access is validated against the active bridge GO, PAUTH, work-intent claim, implementation-start packet, and approved target paths before protected source/internal mutation is allowed.
- Tests cover ordinary, ops, build-without-case, build-with-case, and cross-authority-confusion scenarios without requiring direct edits to black-box configuration or dispatcher runtime state.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`
- `scripts/dispatch_blackbox_gate.py`
- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`
- `platform_tests/scripts/test_dispatch_blackbox_gate.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`feat`
