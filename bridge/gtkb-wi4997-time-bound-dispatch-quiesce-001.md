NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5.5
author_model_version: 5.5
author_model_configuration: Extra High
author_metadata_source: codex-interactive-env

# Implementation Proposal - Provide a durable dispatch quiesce the autonomous dispatcher cannot self-revert

bridge_kind: prime_proposal
Document: gtkb-wi4997-time-bound-dispatch-quiesce
Version: 001
Date: 2026-07-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4997-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4997

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement a for-cause time-bound dispatch quiesce so operators can open clean commit windows for entangled bridge work without leaving dispatch disabled indefinitely or allowing autonomous re-enable.

Work item description: Observed 2026-07-03 during an owner-directed combined finalization: an interactive LO set the bridge substrate to none (gt mode set-bridge-substrate --substrate none, applied:true) to quiesce automated dispatch and freeze three entangled threads. ~13 minutes later a Codex-A process reset the substrate back to dispatcher_daemon (bridge-substrate.json applied_by A at 14:07:10Z), re-enabling dispatch; dispatched workers then re-claimed and re-churned the threads (WI-4992 re-NO-GO'd at -006 by a dispatched Ollama-D worker), defeating the interactive quiesce and blocking the owner-directed verdict finalization. There is currently no reliable interactive/config-level mechanism to pause automated dispatch that the autonomous system will not revert; the only effective stop is a process-level kill of the daemon/supervisor, which is delicate (per the storm-quiesce lesson: verify ancestry before any kill; kill-switch is stripped from workers by design). Fix candidates: (a) a durable operator quiesce flag that the daemon/supervisor honors and will not auto-revert; (b) restrict substrate-mutation authority so dispatched workers cannot re-enable dispatch mid-operator-quiesce; (c) an owner/LO-invokable dispatch-freeze that halts new claims and dispatches until explicitly cleared. This is a dispatch control-integrity gap: the operator could not reliably pause their own dispatch system.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4997` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `scripts/gtkb_dispatcher_daemon.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`.

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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4997-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-4997`.

## Proposed Scope

- Add a governed quiesce command/state for dispatcher control with required reason, actor, issued_at, and optional expires_at/ttl metadata.
- Make the daemon and dispatcher runtime refuse new claims and worker spawns while quiesce is active, without killing already running workers unless an explicit reap command is invoked.
- Prevent autonomous workers and normal dispatcher cycles from clearing or overriding an active quiesce before expiry or authorized clear.
- Expose quiesce status, reason, expiry, and effective dispatchability in dispatcher status/health/report surfaces.
- Preserve the direct harness-to-harness launch prohibition and the existing A/B/D topology; do not re-enable the daemon as part of this implementation.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run targeted dispatcher runtime/daemon/report CLI tests proving quiesce suppresses new dispatch, auto-expires only after configured time, and leaves direct harness invocation unavailable. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run targeted tests proving quiesce is enforced through the dispatcher control plane rather than by harness-to-harness fallback or retired poller behavior. |

## Acceptance Criteria

- Operators can run a for-cause time-bound quiesce command that records reason and expiry and stops new dispatch claims/spawns.
- The dispatcher daemon/runtime honor active quiesce on every cycle and cannot self-reenable until expiry or authorized clear.
- Status/health/report surfaces show quiesced state distinctly from harness failure and include enough evidence to clear entangled commits safely.
- Tests cover active quiesce suppression, expiry behavior, manual clear behavior, and non-interference with direct-invoke prohibitions.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

## Recommended Commit Type

`feat`
