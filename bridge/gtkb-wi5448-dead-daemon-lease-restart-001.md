NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; approval_policy=never

# Implementation Proposal - Prevent dead-daemon document leases from blocking supervised restart

bridge_kind: prime_proposal
Document: gtkb-wi5448-dead-daemon-lease-restart
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5448-DEAD-DAEMON-LEASE-RESTART-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5448

target_paths: ["scripts/ensure_dispatcher_daemon.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Correct the supervised dead-daemon restart path so unexpired document leases
provably owned by a dead daemon cannot deadlock the only process capable of
reconciling them. The correction must remain fail-closed for every
provenance-valid live worker, live-worker-backed lease, and unknown or
unverifiable lease, preserve lease evidence without deleting or rewriting it,
and start exactly one hidden successor through the existing canonical
supervisor path.

The live incident occurred after dispatcher daemon PID 21664 exited while no
worker remained live. Seven unexpired document leases retained PID 21664.
`scripts/ensure_dispatcher_daemon.py` called `dispatch_quiescence`, counted the
seven lease TTLs as active work, and repeatedly returned
`generation_handoff_deferred`, `running=false`, and
`reason=dispatch_work_active`. The scheduled supervisor returned exit 0 on
every cycle, but the absent daemon was the only normal actor able to reconcile
those leases. A canonical `gt bridge dispatch reset --soft` recovery removed
exactly the seven dead-owner lease locks and related recipient/provenance state,
after which the scheduled supervisor immediately restored a healthy daemon.
That operational recovery proves the circular liveness failure; it is not the
durable source correction proposed here.

## Claim

Prime Builder proposes a bounded successor correction for `WI-5448`. It does
not amend or adopt the unverified WI-5427 candidate. Any implementation must
preserve WI-5427-owned source and test bytes, add only attributable WI-5448
hunks after independent GO and implementation-start authorization, and remain
independently finalizable.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`ADR-DISPATCHER-ARCHITECTURE-001`, and
`DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` require one supervised,
recoverable dispatcher daemon. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
requires the repair to preserve live work and dispatchability. TEST-11552
defines the linked regression outcome. No requirement revision is needed
before implementation.

## In-Root Placement Evidence

All four authorized target paths are inside `E:\GT-KB`. No adopter,
out-of-root, credential, deployment, or release surface is in scope.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires the centralized dispatch service to recover without an alternate queue, poller, or daemon.
- `ADR-DISPATCHER-ARCHITECTURE-001` - keeps restart ownership in the existing scheduled supervisor and persistent daemon architecture.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - governs dead-daemon detection, provenance-safe restart, hidden process launch, and exact-once supervision.
- `GOV-SESSION-ROLE-AUTHORITY-001` - requires worker and dispatch provenance to remain authoritative when deciding whether work is live.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - forbids terminating workers, disabling harnesses, or impairing active dispatch to repair the liveness defect.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct proposal, GO, implementation-report, and verification authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps the incident, defect, test, authorization, proposal, implementation evidence, and verdict as durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires traceability across the incident evidence, WI-5448, TEST-11552, source hunks, tests, and independent verdict.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit proposal, implementation, verification, and terminal states rather than treating operational recovery as implementation closure.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the dispatcher repair within the GT-KB platform root and outside adopter application scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to carry the concrete governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the exact PAUTH, project, work item, and target-path tuple.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-derived tests before independent VERIFIED.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded PAUTH carriers and governed proposals for newly discovered bridge, TAFE, dispatcher, and harness defects while preserving every downstream gate.
- `INTAKE-a815f782` - established per-document leases as the canonical cross-target dispatch suppression mechanism; this proposal preserves that role and narrows only dead-daemon restart classification.
- `INTAKE-6554ff58` - established the harmonized dispatcher-daemon complex and management surface that remains the sole restart path.
- `DELIB-20266201` - authorized earlier daemon process-lifecycle hardening on which the current supervisor contract builds.
- `bridge/gtkb-wi5427-daemon-generation-handoff-001.md` and `bridge/gtkb-wi5427-daemon-generation-handoff-003.md` - define the predecessor generation-handoff candidate whose dirty four-file bytes must remain foreign and intact until independent disposition.

## Owner Decisions / Input

No new owner decision is required.
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` expressly permits
this bounded carrier and proposal. Active authorization
`PAUTH-DISPATCHER-BLACK-BOX-WI5448-DEAD-DAEMON-LEASE-RESTART-20260717`
permits bridge, metadata, governance-evidence, source, and test work while
forbidding dispatcher/TAFE/runtime mutation, eligibility changes, credentials,
destructive cleanup, Git staging/commit/push, deployment, and release. Source
and test work remains blocked until independent GO, an exact matching claim,
and implementation-start authorization all exist.

## Proposed Scope

- Add a deterministic, read-only dead-daemon restart classification that separates provenance-valid live workers, live-worker-backed leases, proven orphaned dead-owner leases, and unknown or unverifiable lease ownership.
- Apply that classification only after canonical status proves the supervised daemon is not running. A proven orphaned lease may cease to count as restart-blocking work on this dead-daemon path; no lease file, recipient record, provenance ledger, claim, bridge document, or TAFE state may be deleted, rewritten, or renewed by the classifier.
- Keep unknown liveness or ownership fail-closed. Any provenance-valid live worker or live-worker-backed lease must return a stable deferred result without signaling, terminating, reaping, or replacing a process.
- Preserve the stricter existing active-daemon generation-handoff behavior. This proposal does not authorize ignoring leases while a daemon is alive or performing a live generation handoff.
- Reuse the existing supervisor lock and hidden `pythonw`/no-window launch path so concurrent cycles start at most one successor. Require successor generation and PID provenance attestation before reporting `running=true`.
- Report enough structured diagnostics to distinguish restart-blocking live work from preserved orphan lease evidence, including stable counts and reasons suitable for dispatcher health reporting.
- Prefer a focused correction in `scripts/ensure_dispatcher_daemon.py` and its supervision tests. Touch `scripts/gtkb_dispatcher_daemon.py` or its daemon tests only if read-only provenance classification cannot be expressed correctly from the current quiescence payload.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5448; TEST-11552; live daemon PID 21664 absent with zero workers and seven unexpired leases retaining the dead PID; supervised ensure returned dispatch_work_active until canonical soft reset",
  "canonical_authority": "SPEC-CENTRALIZED-DISPATCH-SERVICE-001; ADR-DISPATCHER-ARCHITECTURE-001; DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "The existing GTKB-DispatcherDaemon scheduled supervisor performs read-only provenance classification and starts one hidden successor through the canonical ensure path",
  "before_behavior": "Any unexpired document lease blocks restart even when its owning daemon PID is dead and no worker is live, so the absent daemon cannot be restored to reconcile its own residue",
  "after_behavior": "Only proven dead-owner orphan leases are non-blocking on the dead-daemon path; live or unknown work remains fail-closed and one attested hidden successor restores normal canonical reconciliation",
  "self_descriptive_naming": "restart_blocking_worker_count, restart_blocking_lease_count, orphaned_dead_owner_lease_count, lease_owner_unknown, and dead_daemon_restart_deferred expose the decision",
  "obsolete_guidance_disposition": "The existing any-live-lease handoff rule remains unchanged for a running daemon; only dead-daemon supervised recovery receives the provenance-aware classification",
  "history_preservation": "Lease files, recipient state, provenance ledgers, bridge documents, claims, TAFE records, daemon logs, and dispatch-run evidence remain untouched by classification and restart admission",
  "baseline": "Daemon PID 21664 was absent; live_worker_count was 0; live_document_lease_count was 7; ensure remained running=false with dispatch_work_active until canonical soft reset removed the dead-owner residue",
  "expected_result": "The same fixture starts exactly one hidden successor without deleting lease evidence, while a live worker, live-backed lease, unknown owner, failed provenance check, or concurrent supervisor cycle prevents spawn",
  "rollback": "A separately governed focused revert removes only attributable WI-5448 source and test hunks; bridge and project records remain append-only and no live state rollback is performed",
  "hard_invariants": "Never terminate or reap a worker; never ignore a live-backed or unknown lease; never mutate lease or TAFE state; never start more than one successor; never change roles, eligibility, ranking, caps, routes, credentials, Git history, deployment, or release state",
  "fail_closed_conditions": "Unknown quiescence, unreadable lease provenance, any live worker, any live-backed lease, supervisor-lock contention, unknown current generation, spawn failure, successor PID/generation mismatch, missing GO/claim/start, or failed test prevents restart acceptance or implementation completion",
  "essential_context_preservation": "Diagnostics retain worker and lease identities, owner PID evidence, dead-owner classification, supervisor lock outcome, successor PID/generation attestation, and exact nonmutation assertions"
}
```

## Spec-Derived Verification Plan

| Spec / governing surface | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run focused supervision tests proving a dead daemon with only proven orphan leases recovers through the existing centralized service and no alternate dispatcher substrate is introduced. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Assert restart still uses the registered scheduled supervisor, its serialization lock, and the existing hidden daemon spawn helper exactly once. |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Execute TEST-11552 plus focused tests for dead-owner orphan leases, live workers, live-backed leases, unknown ownership, concurrent cycles, spawn failure, and successor attestation. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Build fixtures with provenance-valid and mismatched worker identities; only matching live-worker evidence may classify work as live-backed, while ambiguous evidence fails closed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Assert no worker termination/reap helper, lease writer/remover, dispatcher config writer, eligibility writer, TAFE writer, or alternate spawn path is called in any classification or defer branch. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify latest bridge GO, exact work-intent claim, and implementation-start authorization before source edits, then require a fresh dispatcher-produced independent LO verdict. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm WI-5448, TEST-11552, PAUTH, proposal, command evidence, implementation report, and verdict remain linked durable artifacts and no scratch/runtime record is treated as authority. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Verify the implementation report maps exact attributable hunks and executed tests back to WI-5448 and preserves WI-5427 predecessor ownership. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm operational reset evidence remains incident recovery only and the work item advances through GO, start, implementation report, independent VERIFIED, focused commit, and terminal MemBase state. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run in-root target checks and assert no Agent Red, adopter, archive, or out-of-root path is read as a dependency or modified. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and mandatory-clause preflights against this exact bridge thread with zero blocking gaps. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Verify the PAUTH/project/WI tuple and all four inline-JSON target paths against current MemBase membership and authorization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest, Ruff check, Ruff format check, `py_compile`, and `git diff --check`, and map exact command results in the implementation report. |

## Acceptance Criteria

- With no live worker and one or more unexpired leases proven to be owned by the dead supervised daemon, one ensure cycle does not return `dispatch_work_active`; it preserves every lease byte and starts exactly one hidden successor.
- Any provenance-valid live worker or live-worker-backed lease blocks restart without process termination, lease mutation, eligibility/configuration mutation, or alternate dispatch.
- Unknown or unreadable worker/lease provenance fails closed with deterministic diagnostics and no spawn.
- Active-daemon generation handoff continues to defer on every live lease; the new classification is unreachable on that path.
- Concurrent supervisor cycles remain serialized, and success requires exact successor PID provenance plus loaded/current generation equality.
- Focused source and tests preserve the complete WI-5427 candidate as foreign predecessor bytes and are attributable to WI-5448 independently.
- Focused pytest, Ruff check, Ruff format check, `py_compile`, and `git diff --check` pass without stopping or restarting the live daemon.

## Risk / Rollback

Risk is high around false-negative liveness classification because an unsafe
restart could create overlapping dispatchers or duplicate work. The
implementation therefore discounts only leases whose dead ownership is
positively proven, leaves all ambiguity fail-closed, and does not mutate the
evidence it classifies.

Rollback is a focused revert of attributable WI-5448 hunks after independent
governance. The WI-5427 predecessor candidate and all bridge, MemBase, lease,
runtime, and dispatch evidence remain unchanged.

## Files Expected To Change

- `scripts/ensure_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`
- `scripts/gtkb_dispatcher_daemon.py` only if focused evidence proves the current read-only quiescence payload is insufficient
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` only when the daemon payload changes

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
file for `gtkb-wi5448-dead-daemon-lease-restart`; no prior bridge version or
WI-5427 artifact is deleted or rewritten. Dispatcher/TAFE state plus the
numbered file chain remain the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the eventual focused change corrects a supervised restart liveness
defect without adding an alternate dispatcher capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
