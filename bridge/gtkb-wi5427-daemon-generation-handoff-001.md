NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; system-declared GPT-5 family; reasoning configuration not exposed; approval_policy=never

# Implementation Proposal - Roll the live dispatcher daemon forward to the current runtime generation without interrupting workers

bridge_kind: prime_proposal
Document: gtkb-wi5427-daemon-generation-handoff
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5427-DAEMON-GENERATION-HANDOFF-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5427

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/ensure_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Add deterministic dispatcher generation attestation and a supervisor-owned quiescent handoff so approved runtime updates become live without interrupting workers or changing fleet routing.

Work item description: The live dispatcher daemon PID 9564 acquired its lock at 2026-07-16T02:07:27Z, about fourteen hours before current HEAD 42a252ab was committed at 2026-07-16T16:07:12-07:00. That commit added dispatcher-created worker session envelopes and trusted worker context. Repeated genuine Cursor E LO dispatches therefore ran under a stale in-memory dispatcher generation: dispatch 2026-07-17T03-42-31Z-loyal-opposition-E-16bc35 reached governed publication, but no harness-state/cursor/session-envelopes/<dispatch-id>.json existed and publication failed closed because worker-role provenance belonged to another session. Dispatcher status does not expose loaded code generation or automatically hand off after an approved runtime update. Add deterministic loaded-generation identity to daemon status/reporting and a supervisor-owned quiescent generation handoff that defers while any worker or lease is live, preserves all eligibility and routing state, never terminates a worker, and restarts only through canonical daemon controls. Prove that the successor generation creates the exact Cursor worker envelope before spawn and that governed LO publication validates it. Do not disable any harness or bridge, reconfigure TAFE, mutate leases/runtime JSON directly, or infer failure from worker silence.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5427` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_dispatcher_daemon.py`, `scripts/ensure_dispatcher_daemon.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_dispatcher_daemon_supervision.py`.

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
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - auto-linked governing or work-item specification.
- `GOV-SESSION-ROLE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266268` - Owner decision: clear daemon residue WIs (WI-4859, WI-4861) before PHASE-Y
- `DELIB-20266272` - Owner decision: PHASE-Y full daemon go-live
- `DELIB-20266201` - Owner authorization: WI-4855 daemon process-lifecycle hardening
- `DELIB-20266642` - Verdict
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` - Dispatcher daemon Claude+Cursor headless collaboration: harden-first, go-live-later

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5427-DAEMON-GENERATION-HANDOFF-20260717` - active project authorization covering `WI-5427`.

## Proposed Scope

- Compute a deterministic dispatcher runtime generation from the exact daemon, supervisor, and dispatch-runtime source generation loaded by the process; atomically persist the loaded generation at daemon start and expose loaded_generation, current_generation, generation_match, and explicit unknown/error diagnostics through canonical daemon status/report surfaces.
- Extend the idempotent supervisor so an alive matching daemon remains a pure no-op, an unknown generation fails closed without termination, and a stale generation records a deferred handoff while any dispatched worker or document lease is live.
- At the first genuinely quiescent supervisor cycle, perform one bounded canonical daemon-process handoff: terminate only the provenance-verified daemon PID, wait for lock/process exit, start the successor through the existing pythonw/DETACHED_PROCESS/CREATE_NEW_PROCESS_GROUP/CREATE_NO_WINDOW path, and require the successor to report the expected loaded generation before success.
- Preserve all harness roles, eligibility, ranking, caps, route selection, operator-quiesce state, bridge documents, work-intent claims, TAFE state, and lease records; never terminate, reap, or otherwise disturb a worker during generation handoff.
- Prove the current-generation daemon executes the already-committed dispatcher worker-session preparation path so Cursor E receives harness-state/cursor/session-envelopes/<dispatch-id>.json before spawn and governed LO publication can validate the exact session provenance.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5427 and TEST-11538; live daemon PID 9564 generation predates current HEAD 42a252ab; repeated Cursor E publication failures lacked the current dispatcher-created worker-session envelope",
  "canonical_authority": "SPEC-CENTRALIZED-DISPATCH-SERVICE-001; ADR-DISPATCHER-ARCHITECTURE-001; DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "The existing GTKB-DispatcherDaemon scheduled supervisor compares deterministic loaded/current generations, defers while work is live, and performs one canonical hidden-process handoff only when quiescent",
  "before_behavior": "An alive daemon is an unconditional supervisor no-op, so approved dispatcher runtime changes can remain inactive indefinitely and fresh Cursor workers can execute without the current worker-session authority path",
  "after_behavior": "Generation mismatch is explicit; live workers and document leases block handoff; the first quiescent cycle replaces only the provenance-verified daemon and requires successor-generation attestation before success",
  "self_descriptive_naming": "loaded_generation, current_generation, generation_match, generation_handoff_deferred, generation_handoff_failed, and generation_handoff_completed expose the state and action",
  "obsolete_guidance_disposition": "The prior alive-equals-noop rule remains valid only when loaded_generation equals current_generation; stale or unknown generation behavior is governed by the new fail-closed handoff contract",
  "history_preservation": "Existing bridge chains, claims, TAFE documents, leases, eligibility, routing configuration, daemon logs, and dispatch-run evidence remain append-only and are not rewritten by comparison or handoff",
  "baseline": "Daemon PID 9564 acquired its lock at 2026-07-16T02:07:27Z before HEAD 42a252ab; dispatch 2026-07-17T03-42-31Z-loyal-opposition-E-16bc35 failed governed publication because its exact Cursor worker-session envelope was absent",
  "expected_result": "Current status reports exact generation equality; mismatch defers with any worker or lease live; a quiescent stale daemon is handed off once through pythonw/DETACHED_PROCESS/CREATE_NEW_PROCESS_GROUP/CREATE_NO_WINDOW and the successor attests the expected generation",
  "rollback": "A separately governed source/test rollback restores the prior supervisor behavior; no live rollback, daemon stop, routing change, eligibility change, bridge deletion, TAFE mutation, or lease rewrite is permitted by this proposal",
  "hard_invariants": "Never terminate or reap a live worker; never hand off with a live or unexpired document lease; never target an unverified PID; never change roles, eligibility, ranking, caps, routes, quiesce, claims, TAFE state, credentials, Git history, deployment, or release state",
  "fail_closed_conditions": "Unknown loaded/current generation, PID provenance mismatch, any live worker, any live lease, lock-release timeout, successor spawn failure, successor generation mismatch, preflight gap, missing GO/claim/start, or failed test prevents handoff or implementation acceptance",
  "essential_context_preservation": "Status and tests retain daemon PID/lock provenance, worker and lease counts, old/new generation identities, headless launch flags, registry/config equality, exact Cursor dispatch session id, and governed publication outcome"
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run focused daemon and supervisor tests covering deterministic generation identity, stale/current/unknown classification, quiescent-only handoff, exact-once successor start, and unchanged routing/eligibility state. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify no bridge file, TAFE document, claim, lease, or dispatcher configuration mutation occurs in generation comparison/defer logic and that implementation remains behind GO/claim/start. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and mandatory-clause preflights against all cited specifications and the exact four target paths with zero blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute TEST-11538 plus focused pytest, Ruff, and format checks, then require a fresh substantive dispatcher-produced independent LO verdict before VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Prove the persistent daemon remains the sole dispatch substrate, the scheduled supervisor remains the sole generation-handoff owner, and no alternate queue, poller, or daemon is introduced. |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Test alive-current no-op, dead spawn, stale-active defer, stale-quiescent handoff, provenance mismatch fail-closed, bounded wait failure, and hidden Windows successor launch. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Test that the successor generation creates the exact dispatch-id worker session envelope before Cursor E spawn and that publication accepts only matching worker-role provenance. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Snapshot harness registry/config and canonical dispatcher selection before and after simulated handoff; assert byte/semantic equality and assert active workers and leases are never disturbed. |

## Acceptance Criteria

- Daemon status deterministically reports both the generation loaded by the running process and the generation represented by current approved source, with generation_match true only for exact equality and explicit fail-closed diagnostics when either side is unavailable.
- Supervisor does not stop, signal, spawn, or mutate runtime/configuration state while any live worker or unexpired document lease exists; repeated blocked cycles are idempotent and diagnostically report generation_handoff_deferred.
- A quiescent stale daemon is handed off exactly once through the hidden canonical process path; only the provenance-verified daemon PID is terminated, the old lock is observed released, and the successor must attest the expected loaded generation before handoff is accepted.
- Handoff preserves harness registry/config bytes, selected targets, max-item caps, operator quiesce, claims, TAFE documents, and lease records; tests prove no worker-termination helper is called on any non-quiescent path.
- A successor-generation Cursor E dispatch creates the exact worker-session envelope before subprocess spawn and a governed LO verdict resolves matching worker-role provenance rather than failing with session-id mismatch.
- Focused daemon and supervision tests pass without starting or stopping the live daemon; Ruff and format checks pass for the four authorized paths; post-implementation review remains independent and dispatcher-produced.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/ensure_dispatcher_daemon.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`

## Recommended Commit Type

`feat`
