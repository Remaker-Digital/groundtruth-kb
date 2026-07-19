NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Worker-context full assigned-content packet CLI

bridge_kind: prime_proposal
Document: gtkb-wi5270-worker-context-full-assigned-content-packet
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5270-WORKER-CONTEXT-PACKET-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5270

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_worker_context.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement the first worker-safe facade slice for the dispatcher black-box hardening project: a read-only gt bridge dispatch worker-context command that gives ordinary workers full assigned content without exposing dispatcher/TAFE/harness internals.

Work item description: Add a worker-context CLI facade, such as gt bridge dispatch worker-context --self --dispatch-id <id> --json or an equivalent governed command, that returns the complete assigned proposal/verdict/report/review packet content, governing spec links, target paths, allowed actions, blockers, preflight state, and citations/provenance needed by an ordinary worker. The output must omit raw queue, ranking, dispatcher runtime, TAFE, harness registry, lock, process, and configuration internals.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5270` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_worker_context.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py`.

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
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET` - Dispatcher Black Box Worker Context Packet CLI
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT` - Dispatcher Black Box Full Assigned-Content Safe Packet
- `DELIB-202666122` - Verdict
- `DELIB-20265026` - Loyal Opposition Review - WI-4556 Ollama Provider Failure Fallback And Backoff
- `DELIB-20265736` - Loyal Opposition Verification Verdict - WI-4700 Harness Metadata Freshness Guard

## Owner Decisions / Input

- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5270-WORKER-CONTEXT-PACKET-20260717` - active project authorization covering `WI-5270`.

## Proposed Scope

- Add a read-only worker-context facade command under gt bridge dispatch, supporting --self and explicit --dispatch-id lookup for the acting worker.
- Return exact assigned proposal/verdict/report/review content plus governing specs, target paths, allowed actions, blockers, preflight state, citations, and provenance needed for ordinary bridge work.
- Omit raw queue mechanics, ranking inputs, dispatcher runtime state, TAFE internals, harness registry internals, locks, process details, configuration internals, and other-harness state from the public packet.
- Reuse existing bridge/versioned-file and dispatcher report helpers where possible; do not mutate dispatcher, TAFE, lease, runtime, config, database, Git, release, deployment, credential, or external-system state.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
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
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | Run platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py to prove assigned-content packet completeness. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Run the same CLI tests to assert forbidden internal keys and raw internal values are absent from ordinary-worker packet output. |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | Run focused CLI tests covering --self/--dispatch-id behavior and deterministic JSON schema. |

## Acceptance Criteria

- gt bridge dispatch worker-context --self --dispatch-id <id> --json emits a deterministic full assigned-content packet for a synthetic dispatched worker.
- The packet includes assigned_content, governing_specs, target_paths, allowed_actions, blockers, preflight_state, citations, and provenance fields.
- Regression tests assert the packet omits raw queue, ranking, runtime, TAFE, harness-registry, lock, process, configuration, and other-harness internals.
- The implementation is read-only and does not change dispatcher routing, selected targets, leases, runtime state, database rows, or bridge status.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_worker_context.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py`

## Recommended Commit Type

`feat`
