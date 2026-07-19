NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; build envelope active; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Ops build capability issuance validation and audit for black-box access

bridge_kind: prime_proposal
Document: gtkb-wi5274-capability-issuance-audit
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5274-CAPABILITY-ISSUANCE-AUDIT-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5274

target_paths: ["groundtruth-kb/src/groundtruth_kb/blackbox_capability.py", "scripts/dispatch_blackbox_gate.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "scripts/protected_mutation_guard.py", "platform_tests/scripts/test_dispatch_blackbox_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_protected_mutation_guard.py", "platform_tests/scripts/test_worker_packet_authorization_envelope.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5274 proposes shared source/test capability issuance, validation, TTL, denial, and audit mechanics for protected black-box access, without granting live access or mutating dispatcher runtime/config state in this proposal.

Work item description: Implement recorded capability issuance, validation, denial, and audit for protected black-box access. Capability carriers must be scoped to session, activity envelope, surface, path or command family, action set, TTL, and case authorization where required. Ops capabilities cover black-box configuration mutation. Build capabilities cover direct internals mutation only when case-authorized. Denials, bypass attempts, expirations, and granted access must be audit-visible.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5274` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/blackbox_capability.py`, `scripts/dispatch_blackbox_gate.py`, `scripts/implementation_authorization.py`, `scripts/implementation_start_gate.py`, `scripts/protected_mutation_guard.py`, `platform_tests/scripts/test_dispatch_blackbox_gate.py`, `platform_tests/scripts/test_implementation_authorization.py`, `platform_tests/scripts/test_protected_mutation_guard.py`, `platform_tests/scripts/test_worker_packet_authorization_envelope.py`.

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
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20263358` - TAFE Agent Capability Snapshots Schema - VERIFIED
- `DELIB-202666247` - Loyal Opposition Verification Verdict - WI-5240 WI-5236 PAUTH Registered Vocabulary
- `DELIB-202666140` - Loyal Opposition Verdict — WI-5189 / WI-5195 Document-Authoritative GO-Claim Corrective Finalization (VERIFIED: the corrected single-patch commit collects and passes in isolation)
- `DELIB-S364-LO-ADVISORY-GRILLING-GATE-PROJECT-AUTH` - Owner decision: authorize PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001 for implementation (all 3 WIs)
- `DELIB-20260704-GTKB-OWNER-AUTHORITY-CHANNEL-PROOF-RECORD` - Owner-authority channel approvals require authenticated bound authority records

## Owner Decisions / Input

- `DELIB-20260715-DISPATCHER-BLACKBOX-CAPABILITY-TOKEN-ENFORCEMENT` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5274-CAPABILITY-ISSUANCE-AUDIT-20260717` - active project authorization covering `WI-5274`.

## Proposed Scope

- Add a shared capability carrier/validator for protected black-box access, scoped by session, activity envelope, surface/path/command family, action set, TTL, and case authorization where required.
- Wire capability validation and audit records into existing black-box, implementation-start, and protected-mutation guard paths without granting live access by default.
- Preserve ordinary-worker denial behavior and route denied ordinary access toward worker-safe packet surfaces; ops capabilities cover configuration mutation only and build capabilities cover direct internals only with case authorization.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run guard/authorization tests proving protected dispatcher/bridge/TAFE access remains governed and fail-closed. |
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
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Test capability matching for ordinary, ops, build, and case-authorized build paths including non-interchangeability. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Assert ordinary sessions receive denials and safe-packet guidance rather than raw internals access. |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | Assert denial/audit output preserves safe packet routing context without leaking protected internals. |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | Verify capability denial messages point ordinary workers to worker-context/mediated packet paths instead of raw bridge files. |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | Verify the implementation remains covered by the active WI-5274 PAUTH and foundation specs. |

## Acceptance Criteria

- Capability issuance fails closed when session, activity envelope, target surface, action set, TTL, or case authorization does not match the requested protected access.
- Granted access, denial, bypass attempt, expiry, and validation mismatch events are audit-visible in a deterministic JSONL/event shape usable by later scanners.
- Ops and build capabilities cannot satisfy each other; ordinary sessions cannot gain protected internals/config access without an initialized authorized activity envelope and matching case/PAUTH context.
- Tests cover valid grant, expired grant, wrong session, wrong envelope, wrong surface/action, missing case authorization, ordinary denial, and audit event shape.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/blackbox_capability.py`
- `scripts/dispatch_blackbox_gate.py`
- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `scripts/protected_mutation_guard.py`
- `platform_tests/scripts/test_dispatch_blackbox_gate.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `platform_tests/scripts/test_protected_mutation_guard.py`
- `platform_tests/scripts/test_worker_packet_authorization_envelope.py`

## Recommended Commit Type

`feat`
