NEW
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - Worker Packet Authorization Envelope Slice 2: Auto Packet Creation

bridge_kind: prime_proposal
Document: gtkb-worker-packet-auth-envelope-slice-2-auto-packet
Version: 001 (NEW)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3386
Source: `bridge/gtkb-worker-packet-as-execution-authorization-envelope-slice-1-scoping-002.md` GO
Recommended commit type: `feat:`
target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_worker_packet_authorization_envelope.py"]

## Summary

Implement Slice 2 from the approved worker-packet-as-execution-authorization-envelope scoping thread: when bridge dispatch selects a Prime worker for an implementation-authorized item, the dispatch substrate creates or refreshes the implementation authorization packet before spawning the worker.

The goal is mechanical throughput reduction, not gate removal. The worker still receives only the GO-derived `target_paths` scope, and the existing implementation-start, formal-artifact, deployment, credential, destructive-cleanup, and owner-decision gates remain in force.

## Background

`bridge/gtkb-worker-packet-as-execution-authorization-envelope-slice-1-scoping-002.md` returned GO for the design frame and explicitly directed follow-on implementation slices. This proposal implements the first follow-on slice: auto-packet creation on worker spawn. MemBase work item `WI-3386` records this Slice 2 follow-on and is attached to `PROJECT-GTKB-RELIABILITY-FIXES` under the active reliability fast-lane authorization.

Current behavior requires a Prime worker to run:

```text
python scripts/implementation_authorization.py begin --bridge-id <document-name>
```

before making source edits after a GO. The dispatch event already knows the selected bridge document and already sets `GTKB_BRIDGE_POLLER_RUN_ID`. This slice lets the dispatcher create the same packet mechanically before worker startup, so the worker can proceed inside the approved scope without repeating a deterministic setup step.

## Scope

In scope:

- Add a helper in `scripts/implementation_authorization.py` that can create a named authorization packet for a bridge ID in worker-dispatch context while preserving the existing `begin` validation path.
- Update `scripts/cross_harness_bridge_trigger.py` so selected Prime-actionable GO dispatch entries receive a pre-created authorization packet before worker subprocess spawn.
- Update `scripts/single_harness_bridge_dispatcher.py` with the same behavior for single-harness topology.
- Ensure child process environment carries enough non-secret context to identify the packet, such as dispatch ID and bridge ID, without broadening file scope.
- Update `scripts/implementation_start_gate.py` only as needed to recognize the named packet/current packet behavior already produced by the authorization helper.
- Add regression tests for successful packet creation, no packet for non-GO or LO-review dispatch, failure recording when packet creation fails, and preservation of target-path boundaries.

Out of scope:

- No expansion beyond proposal `target_paths`.
- No formal artifact mutation authorization.
- No deployment authorization.
- No credential operation authorization.
- No destructive cleanup authorization.
- No owner-decision tracker suppression.
- No implementation of later Slice 3-5 behavior except what is strictly necessary to keep Slice 2 fail-closed and testable.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/prime-builder-role.md`
- `bridge/gtkb-worker-packet-as-execution-authorization-envelope-slice-1-scoping-002.md`

## Prior Deliberations

- `DELIB-1422`, `DELIB-1418`, and related bridge-poller records - dispatch substrate context.
- `DELIB-1549` and `DELIB-1544` - smart-poller retirement and event-driven trigger verification context.
- `DELIB-1517` - bridge-status automation review context.
- `bridge/gtkb-implementation-authorization-*` - established the implementation authorization packet contract.
- `WI-3386` - MemBase work item for this Slice 2 follow-on, created 2026-05-20 and attached to `PROJECT-GTKB-RELIABILITY-FIXES`.
- `bridge/gtkb-worker-packet-as-execution-authorization-envelope-slice-1-scoping-001.md` and `-002.md` - approved scoping predecessor.
- `bridge/gtkb-prime-worker-permission-profile-slice-1` - sibling permission-profile work; this proposal composes with it but does not implement permission-mode changes.
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2` - related worker-context detection thread; this proposal does not depend on it being VERIFIED.

## Owner Decisions / Input

Owner directive in S350 requested making Prime workers less gated once work is approved while preserving credential, deployment, formal-artifact, and owner-decision gates. The scoping GO approved this sequence. No new owner input is required.

## Requirement Sufficiency

Existing requirements are sufficient. The implementation-start gate remains the mechanical local authorization source; this slice adds a dispatch-owned derivation path that invokes the same authorization validation rather than bypassing it.

## Implementation Details

1. In `scripts/implementation_authorization.py`, expose a reusable function that creates and writes the named packet for a bridge ID using the same validation as `begin`.
2. In `scripts/cross_harness_bridge_trigger.py`, when the selected dispatch batch includes Prime-actionable GO implementation work, create authorization packets before `_spawn_harness` launches the worker. If packet creation fails, do not spawn that item; record a dispatch failure with the bridge ID and reason.
3. In `scripts/single_harness_bridge_dispatcher.py`, mirror the same packet creation and failure behavior.
4. Preserve current behavior for Loyal Opposition dispatch, NO-GO revision dispatch, advisory dispatch, and terminal/non-dispatchable entries unless a later approved slice expands them.
5. Keep `GTKB_BRIDGE_POLLER_RUN_ID` semantics unchanged. Additional environment variables may be added only for non-secret dispatch/packet identifiers.
6. Tests should use temp bridge fixtures and assert that produced packets contain the exact GO-derived target path globs.

## Spec-to-Test Mapping

| Linked specification / rule | Verification evidence |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests build live `bridge/INDEX.md` fixtures and prove only latest GO entries can produce packets. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted tests cover packet creation, non-GO denial, failure recording, and target-path preservation. |
| `.claude/rules/codex-review-gate.md` | Tests prove packet content is created through implementation authorization validation and still enforces GO-derived scope. |
| `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Tests or code assertions prove the worker packet does not authorize formal artifact mutations. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched files and packet state stay under `E:\GT-KB`. |

## Verification Plan

Required commands after implementation:

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-worker-packet-auth-envelope-slice-2-auto-packet
python -m pytest platform_tests/scripts/test_worker_packet_authorization_envelope.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_worker_packet_authorization_envelope.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_worker_packet_authorization_envelope.py
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-worker-packet-auth-envelope-slice-2-auto-packet --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-worker-packet-auth-envelope-slice-2-auto-packet
```

## Acceptance Criteria

1. Dispatch packet creation uses the same live-GO validation as `implementation_authorization.py begin`.
2. Cross-harness and single-harness dispatchers create packets before spawning Prime implementation workers for selected latest-GO entries.
3. Packet creation failure is fail-closed and recorded as a dispatch failure.
4. LO review dispatch and non-GO entries do not receive implementation packets.
5. Generated packet target path globs exactly match the approved proposal scope.
6. Formal artifact, deployment, credential, destructive-cleanup, and owner-decision gates remain separate.

## Risk and Rollback

- **Risk: accidental envelope expansion.** Mitigation: exact target-path tests and fail-closed packet creation.
- **Risk: dispatch failure noise if packet creation rejects malformed old proposals.** Mitigation: record structured failure and do not spawn the worker for that item.
- **Rollback:** revert the dispatcher and authorization helper changes; workers return to manual `implementation_authorization.py begin` setup.

End of proposal.
