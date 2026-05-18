NEW

# Post-Implementation Report - Bridge Scheduler Slice 4: Per-Role Dispatch Concurrency (WI-3375)

bridge_kind: implementation_report
Document: gtkb-bridge-scheduler-lanes-leases-slice-4
Version: 003 (NEW; post-implementation report for the GO at bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-002.md)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3375 (bridge scheduler Slice 4 - per-role dispatch concurrency)
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3375
target_paths: ["scripts/bridge_dispatch_concurrency.py", "platform_tests/scripts/test_bridge_dispatch_concurrency.py"]
Recommended commit type: feat:

## Summary

The GO'd proposal at bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md (Loyal Opposition GO at -002) is implemented. Two new files were added: scripts/bridge_dispatch_concurrency.py (the per-role dispatch concurrency module) and platform_tests/scripts/test_bridge_dispatch_concurrency.py (its test suite). No existing file was modified - the slice is purely additive. The full suite passes 16/16: the proposal's T1-T13, the GO -002 P3-CONSTRAINT invalid-role coverage (T14), and malformed-slot coverage (T15-T16). The module is the standalone per-role concurrency primitive; it is not wired into the dispatch path, so live dispatch behavior is unchanged.

One scope point requires Loyal Opposition adjudication: the implementation extends the GO'd -001 reclaim design to also reclaim malformed slot files (a crash mid-create), applying the Slice 3 INDEX-writer NO-GO -004 lesson to the sibling slot pool. This is disclosed in full in the "Malformed-Slot Reclamation" section below and surfaced as Loyal Opposition Ask 4.

## Recommended Commit Type

feat: - the change adds a new capability surface (the per-role dispatch concurrency module and its test suite). It is net-new code, matching the GO'd proposal's recommended type.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is the canonical bridge workflow state; per-role concurrency raises throughput against that queue, and the bounded slot pool keeps the in-flight worker count correct under concurrent registration.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the new module, the new test file, and the runtime worker-slot directory are all within the E:\GT-KB project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries forward every relevant governing specification from the proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the executed test suite from the linked specifications.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - the bridge dispatch automation contract; Slice 4 adds a mechanism but does not touch the dispatch path, so the auto-trigger contract is preserved unchanged.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 - auto-trigger contract preserved; Slice 4 does not alter dispatch behavior or actionable-signature computation.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the concurrency module is topology-agnostic; both the cross-harness trigger and the single-harness dispatcher will consume per-role limits.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the single-harness substrate will consume the same module in the integration step.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - worker-slot records are durable runtime artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the slice family is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - worker-slot lifecycle is registered -> held -> refreshed -> released or reclaimed (advisory).

## Prior Deliberations

- bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-002.md - the GO on this slice; its P3-CONSTRAINT (role-label validation) and P4-INFO (standalone-primitive boundary) and its ten follow-on constraints are addressed in this report.
- bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md - the GO'd proposal; this report implements its scope.
- gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (GO at -002) - the design authority; its Slice 4 bullet fixed per-role concurrency with the owner's LO=3 / Prime=2 hint.
- DELIB-2182 - the owner-authorization deliberation for the bridge scheduler program.
- gtkb-bridge-scheduler-lanes-leases-slice-2 (VERIFIED at -004) - the sibling lease registry; Slice 4 reuses its atomic O_CREAT|O_EXCL create, heartbeat-TTL staleness, and token-guarded delete discipline.
- bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-004.md - the NO-GO on the sibling Slice 3 INDEX writer; its malformed-lock P1 finding is the precedent for this slice's malformed-slot reclamation (see the dedicated section below).
- bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-005.md - the REVISED Slice 3 report that landed the malformed-lock fix; Slice 4 applies the same correctness pattern to the slot pool.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and scaffold the full program (Slices 2-6); that decision is recorded as DELIB-2182. The owner gave explicit per-role concurrency hints in S350: "LO review workers 2-4, Prime implementation workers 1-3"; the Slice 4 defaults (LO=3, Prime=2) sit inside those ranges. The MemBase project PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES, work items WI-3373 through WI-3377, and the project authorization PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION were created under that authorization. This Slice 4 implementation is within that authorized scope, asserts no new requirement, and requires no further owner decision before verification.

## Clause Scope Clarification (Not a Bulk Operation)

This implementation creates one new Python module and one new test file. It does not resolve, retire, promote, or batch-mutate work items, and it produces no work-item inventory and requests no formal-artifact-approval packet for a bulk action. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS is not applicable. The single work item cited (WI-3375) is this report's own implementing work item under the mandatory project-linkage metadata.

## What Was Implemented

scripts/bridge_dispatch_concurrency.py - a standalone, stdlib-only module providing per-role dispatch concurrency limits and bounded in-flight worker tracking. It exposes the GO-approved public API names exactly: role_limit, register_worker, release_worker, refresh_worker, in_flight_count, available_slots, reclaim_stale_workers, the worker_slot context manager, the WorkerSlot handle class, and the DispatchCapacityExhausted exception.

- role_limit(role) resolves the per-role limit: the per-role environment override GTKB_DISPATCH_CONCURRENCY_<ROLE> (a positive integer) wins, otherwise DEFAULT_ROLE_LIMITS (loyal-opposition=3, prime-builder=2).
- register_worker(role, *, state_dir, ttl_seconds) walks slot indices 0 .. role_limit(role)-1 and atomically creates the first free slot file <state_dir>/workers/<role>/slot-<n>.lock via os.open with O_CREAT | O_EXCL | O_WRONLY. The bounded index range caps concurrent registration at exactly role_limit(role). It returns a WorkerSlot or None at capacity.
- Slot files record schema_version, role, slot_index, worker_token (uuid4), pid, acquired_at, heartbeat_at, ttl_seconds. Staleness is heartbeat-TTL based against the slot's own recorded ttl, never a PID-liveness probe, keeping the module cross-platform.
- release_worker is token-guarded; refresh_worker is ownership-guarded and rewrites the heartbeat atomically via a sibling temp file plus os.replace; reclaim_stale_workers sweeps every canonical role directory; the worker_slot context manager registers on enter (raising DispatchCapacityExhausted at capacity) and releases on exit including on exception.
- DEFAULT_WORKER_TTL_SECONDS = 1800 - generous for a counterpart-harness session; long workers call refresh_worker.
- Self-contained: stdlib only (contextlib, json, os, time, uuid, datetime, pathlib). No import of dispatch code, the Slice 2 lease registry, or the Slice 3 writer.

GO -002 P3-CONSTRAINT (role-label validation) is implemented: _validate_role accepts only the two canonical scheduler roles (prime-builder, loyal-opposition) and raises ValueError for empty strings, path separators, dots, and unknown roles, before any role value reaches a filesystem path or an environment-variable name. _env_override_name derives the env suffix deterministically by uppercasing and replacing hyphens with underscores. Every public entry point validates the role first.

Two implementation choices apply the bridge scheduler Slice 3 concurrency lessons (proposal -001 cites Slice 3 as a sibling): _write_all loops os.write until the full slot payload lands so an ordinary short write cannot truncate a record; _remove_with_retry retries os.remove on a short backoff for the Windows delete-while-open case.

platform_tests/scripts/test_bridge_dispatch_concurrency.py - the test suite, 16 tests, all under an isolated pytest tmp_path; 16 passed.

## Malformed-Slot Reclamation - Extension Beyond the -001 Design

This section discloses the one place the implementation goes beyond the literal GO'd -001 design, and asks Loyal Opposition to adjudicate the scope (Loyal Opposition Ask 4).

The -001 design (proposal section "Scope") says: "A slot index whose file exists but is stale (heartbeat aged past ttl_seconds) is token-guarded-reclaimed and reused." That describes reclamation of a *valid* slot record with an aged heartbeat. It does not mention a malformed slot file.

A malformed slot file is a real, reachable state: _write_all loops os.write so an ordinary short write cannot truncate the record, but a process that crashes between the O_EXCL create and completing the write leaves an empty or truncated slot file. That file has no parseable heartbeat. If reclamation handled only valid-heartbeat-stale slots, a malformed slot file would never be reclaimed by register_worker or reclaim_stale_workers: it would permanently consume one slot index, silently lowering the role's real concurrency limit - a bridge-throughput regression.

This is the identical hazard class Loyal Opposition NO-GO'd the sibling Slice 3 INDEX writer for, at bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-004.md (P1: "Malformed lock files are not reclaimed, so INDEX writes can remain blocked"). The Slice 3 REVISED report at -005 fixed it by distinguishing "file absent" from "file present but malformed" and using the lock file mtime as the fallback staleness signal.

The implementation applies the same correctness pattern here. _classify_slot returns absent / fresh / reclaimable: a malformed file aged past DEFAULT_WORKER_TTL_SECONDS (by mtime) is reclaimable; a malformed file younger than the ttl is treated as fresh (a create may be in progress) and is left intact. register_worker, in_flight_count, available_slots, and reclaim_stale_workers all consume _classify_slot, so the malformed case is handled consistently everywhere.

Why this was implemented rather than deferred: shipping Slice 4 without it would knowingly ship the exact P1 defect class that Loyal Opposition NO-GO'd on Slice 3 one review cycle earlier. The malformed-slot handling does not add capacity or change the bounded-pool cap; it completes the GO'd "an abandoned slot is reclaimed" intent so the bounded pool self-heals. It is confined to the two target_paths and adds no new public API.

Loyal Opposition Ask 4 invites an explicit verdict: if this extension is acceptable, VERIFIED; if Loyal Opposition judges it out of scope for the -001 GO and wants it removed or split into a separate thread, NO-GO with that direction and Prime will re-scope.

## Spec-To-Test Mapping

| Spec / governing surface | Verification | Result |
| --- | --- | --- |
| Scoping Slice 4 - per-role concurrency limit with owner-hinted defaults | T1 asserts role_limit defaults (LO=3, Prime=2); T2 asserts the per-role env override is honored and that a non-positive / non-integer override falls back to the default. | PASS - T1, T2. |
| Scoping Slice 4 - scheduler tracks in-flight worker count per role; the limit holds | T3 register creates a slot; T4 returns None at capacity; T5 per-role independence; T6 release frees a slot; T7 in_flight_count / available_slots track register and release; T12 runs 16 barrier-synchronized concurrent register_worker calls and asserts exactly role_limit slots are granted with distinct indices. | PASS - T3, T4, T5, T6, T7, T12. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - slot lifecycle registered -> held -> refreshed -> released/reclaimed | T8 stale-slot reclaim and index reuse; T9 refresh extends freshness; T10 token-guarded release; T11 reclaim_stale_workers removes only stale slots and returns their identifiers; T13 the worker_slot context manager including DispatchCapacityExhausted and release-on-exception. | PASS - T8, T9, T10, T11, T13. |
| GO -002 P3-CONSTRAINT - validate role labels before deriving paths or env-var names | T14 asserts role_limit, register_worker, in_flight_count, and available_slots each raise ValueError for empty strings, forward- and back-slash path separators, dot traversal, a dotted label, a wrong-case label, and an unknown role; and that no stray worker directory is created. | PASS - T14. |
| GOV-FILE-BRIDGE-AUTHORITY-001 - a malformed slot file must not permanently consume a slot index (the Slice 3 NO-GO -004 hazard class) | T15 a stale malformed slot is reclaimed by register_worker and by reclaim_stale_workers; T16 a fresh malformed slot is retained (register_worker lands on the next index; reclaim_stale_workers leaves it). | PASS - T15, T16. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All tests run under an isolated tmp_path state directory; the module resolves slot paths under the in-root .gtkb-state/bridge-poller/workers/. No applications/ paths. | PASS. |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | No dispatch-path code was added or modified; cross_harness_bridge_trigger.py and single_harness_bridge_dispatcher.py are absent from target_paths and unmodified. | PASS - by inspection. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This report carries the mapping plus the executed pytest command and observed results below. | PASS. |

## Verification Commands And Observed Results

1. `python -m pytest platform_tests/scripts/test_bridge_dispatch_concurrency.py -q`
   Result: 16 passed in 0.44s. T1-T13 (proposal), T14 (invalid-role validation), T15-T16 (malformed-slot reclaim/retain). The default pytest temp root was accessible in the harness B project environment, so no TMP/TEMP override was needed (GO follow-on constraint 8).

2. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-4 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-003.md` - see the Applicability Preflight section.

3. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-4 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-003.md` - see the Clause Applicability section.

## Live Dispatch Behavior Unchanged

Per GO -002 P4-INFO and follow-on constraint 10: Slice 4 adds no dispatch-path code. The fixed DEFAULT_MAX_ITEMS caps remain in scripts/cross_harness_bridge_trigger.py and scripts/single_harness_bridge_dispatcher.py, unmodified. Live bridge dispatch behavior is unchanged by this slice. A later integration proposal must consume the Slice 2 lease registry, the Slice 3 serialized INDEX writer, and this Slice 4 concurrency module together before the flat cap is actually retired; that proposal must cite this deferral.

## Acceptance Criteria

- [x] Loyal Opposition returned GO on the proposal (-002).
- [x] scripts/bridge_dispatch_concurrency.py exists and exposes role_limit, register_worker, release_worker, refresh_worker, in_flight_count, available_slots, reclaim_stale_workers, and the worker_slot context manager.
- [x] role_limit defaults to LO=3 / Prime=2 and honors the per-role environment override.
- [x] Worker registration is a bounded atomic slot pool via O_CREAT | O_EXCL; concurrent registration grants exactly role_limit(role) slots and no more (T12).
- [x] Slots carry PID, acquired_at, heartbeat_at, and a uuid4 token; staleness is heartbeat-TTL-based; release_worker is token-guarded.
- [x] Role-label normalization/validation rejects path separators, dots, empty strings, and unknown roles before path/env use (GO P3-CONSTRAINT; T14).
- [x] platform_tests/scripts/test_bridge_dispatch_concurrency.py covers T1-T13 plus invalid-role coverage, passes, and uses isolated temp roots.
- [x] No existing dispatch code is modified - Slice 4 is purely additive; live dispatch behavior is unchanged.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete (and adjudicates the malformed-slot extension per Loyal Opposition Ask 4).

## Applicability Preflight

The applicability preflight was run against this -003 report via `--content-file` prior to filing the INDEX entry:

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-4 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-003.md`

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:5d4d21ab86ceccffcfeb4756273845d6535bda71ece7ec6bc7f81d315165a6c0

All applicable required and advisory cross-cutting specs are cited in this report's Specification Links.

## Clause Applicability

The ADR/DCL clause preflight was run against this -003 report via `--content-file` prior to filing the INDEX entry:

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-4 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-003.md`

- Clauses evaluated: 5 (must_apply: 5, may_apply: 0, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0 (pass)

| Clause | Applicability | Evidence found |
|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | must_apply | yes |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | must_apply | yes |

## Risk And Rollback

- R1 (low): a stale-slot handling bug permanently consumes a role's capacity. Mitigation: the heartbeat-TTL reclaim path (T8, T11) and the malformed-slot reclaim path (T15, T16) are both directly tested; DEFAULT_WORKER_TTL_SECONDS = 1800 bounds any stuck slot, and long workers refresh.
- R2 (low): the new module has no consumer until the integration step. Mitigation: this is the GO'd scoping sub-slice boundary; the 16-test suite exercises every code path in isolation.
- R3 (low): a worker TTL set too short would falsely reclaim a slot held by a still-running worker. Mitigation: the 1800 s default is generous, the value is configurable per registration, and refresh_worker lets long workers extend their heartbeat.
- R4 (very low): cross-platform atomicity. Mitigation: O_CREAT | O_EXCL create and os.replace are atomic on Windows and POSIX; T12 asserts the limit holds under 16-way concurrent registration.
- R5 (very low): the token-guarded reclaim and the mtime-guarded malformed reclaim each have the same minimal two-syscall window as the VERIFIED Slice 2 lease registry and the Slice 3 writer. Mitigation: the pattern matches the accepted sibling code; a 1800 s ttl makes the window practically unreachable.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue beyond any runtime slot files, which are themselves reclaimable by TTL.

## Loyal Opposition Asks

1. Confirm scripts/bridge_dispatch_concurrency.py implements the GO'd -001 design: per-role limits with the env override, the bounded O_CREAT|O_EXCL slot pool capping concurrent registration at exactly role_limit, heartbeat-TTL staleness, token-guarded release/reclaim, and atomic os.replace refresh, with the approved public API names.
2. Confirm the GO -002 P3-CONSTRAINT is satisfied: _validate_role rejects path separators, dots, empty strings, and unknown roles before any role reaches a path or env-var name, and T14 covers it across the public API.
3. Confirm the two Slice-3 concurrency lessons (loop os.write for the full payload; retry os.remove for the Windows delete-while-open case) are correctly applied.
4. Adjudicate the malformed-slot reclamation extension described in the "Malformed-Slot Reclamation" section: it goes beyond the literal -001 design but applies the Slice 3 NO-GO -004 P1 lesson to the sibling slot pool. Confirm it is acceptable in-scope robustness for this slice, or NO-GO with direction to remove or split it.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
