NEW

# Bridge Scheduler Slice 4: Per-Role Dispatch Concurrency

bridge_kind: implementation_proposal
Document: gtkb-bridge-scheduler-lanes-leases-slice-4
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3375 (bridge scheduler Slice 4 - per-role dispatch concurrency); sub-slice 4 of the GO'd gtkb-bridge-scheduler-lanes-leases-slice-1-scoping plan
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3375
target_paths: ["scripts/bridge_dispatch_concurrency.py", "platform_tests/scripts/test_bridge_dispatch_concurrency.py"]
Recommended commit type: feat:

## Summary

This is Slice 4 of the bridge scheduler program. The GO'd scoping thread `gtkb-bridge-scheduler-lanes-leases-slice-1-scoping` (Loyal Opposition GO at `-002`) approved a five-sub-slice plan; sub-slice 4 is per-role dispatch concurrency. Its scoping bullet: "Replace `DEFAULT_MAX_ITEMS = 2` with `GTKB_DISPATCH_CONCURRENCY` env or config (default: LO=3, Prime=2 per owner hints). Scheduler tracks in-flight worker count per role."

Slice 4 delivers a standalone module — `scripts/bridge_dispatch_concurrency.py` — that resolves a per-role concurrency limit and tracks in-flight workers as a bounded pool of atomically-acquired slot files. It exposes the decision API (`available_slots`, `register_worker`, the `worker_slot` context manager) the dispatch path will consult, once integrated, instead of the flat `DEFAULT_MAX_ITEMS = 2` cap.

Slice 4 is purely additive: one new module plus its test suite. No existing dispatch code is modified. The replacement of `DEFAULT_MAX_ITEMS` in `cross_harness_bridge_trigger.py` and `single_harness_bridge_dispatcher.py`, and the wiring of the Slice 2 lease registry and Slice 3 serialized writer into the dispatch loop, is integration work — see Loyal Opposition Ask 1 on the deferral.

## Background

The cross-harness event-driven trigger dispatches at most `DEFAULT_MAX_ITEMS = 2` bridge threads to a single worker, processed serially (`scripts/cross_harness_bridge_trigger.py`; a parallel cap in `scripts/single_harness_bridge_dispatcher.py`). The scoping thread recorded the owner's S350 throughput directive: "Replace 'cap of 2' with a real worker scheduler... per-role concurrency limits, for example LO review workers 2-4, Prime implementation workers 1-3." Live dispatch-state at S350 showed 27 pending items being serviced two at a time — the fixed cap is the visible bottleneck.

Per-role concurrency means the limit differs by role: Loyal Opposition review workers can run more in parallel (review analysis parallelizes well) than Prime Builder implementation workers (implementation must serialize where target paths and MemBase mutations overlap). Slice 4 makes the limit a per-role property and tracks how many workers are in flight per role so the dispatch path can stop dispatching a role once its limit is reached.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is the canonical bridge workflow state; per-role concurrency raises throughput against that queue, and the Slice 2 lease registry plus Slice 3 serialized writer keep concurrent workers from corrupting it.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the new module, the new test file, and the runtime worker-slot directory are all within the E:\GT-KB project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the Slice 4 test suite from the linked specifications.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - the bridge dispatch automation contract; Slice 4 adds a mechanism but does not touch the dispatch path, so the auto-trigger contract is preserved unchanged.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 - auto-trigger contract preserved; Slice 4 does not alter dispatch behavior or actionable-signature computation.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the concurrency module is topology-agnostic; both the cross-harness trigger and the single-harness dispatcher will consume per-role limits.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the single-harness substrate will consume the same module in the integration step.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - worker-slot records are durable runtime artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the slice family is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - worker-slot lifecycle is registered -> held -> refreshed -> released or reclaimed (advisory).

## Prior Deliberations

- gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (GO at -002) - the design authority for this slice; its Slice 4 bullet fixed per-role concurrency with the owner's LO=3 / Prime=2 hint, and design decision 4 noted the scheduler tracks worker state.
- DELIB-2182 - the owner-authorization deliberation for the bridge scheduler program; it records the S350 throughput directive (including the explicit per-role hints "LO review workers 2-4, Prime implementation workers 1-3") and the 2026-05-18 AskUserQuestion decisions.
- gtkb-bridge-scheduler-lanes-leases-slice-2 (VERIFIED at -004) - the per-document lease registry; Slice 4's worker-slot pool reuses the same atomic `O_CREAT | O_EXCL` create, heartbeat-TTL staleness, and token-guarded delete discipline.
- gtkb-bridge-scheduler-lanes-leases-slice-3 (NEW at -001) - the serialized INDEX writer; Slices 2, 3, and 4 are the three safety primitives the dispatch-path integration consumes together.
- gtkb-cross-harness-trigger-active-session-suppression-001 (VERIFIED) - the current single-per-harness-lock suppression contract; per-role concurrency is the finer-grained capacity model the scheduler program substitutes for that coarse one-at-a-time lock.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and scaffold the full program (Slices 2-6); that decision is recorded as DELIB-2182. The owner gave explicit per-role concurrency hints in S350: "LO review workers 2-4, Prime implementation workers 1-3"; the Slice 4 defaults (LO=3, Prime=2) sit inside those ranges. The MemBase project PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES, work items WI-3373 through WI-3377, and the project authorization PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION (status active; owner decision DELIB-2182) were created under that authorization. This Slice 4 proposal implements WI-3375 within that authorized scope. It asserts no new requirement and requires no further owner decision before GO; the default limits sit within the owner-stated ranges.

## Requirement Sufficiency

Existing requirements sufficient. The per-role concurrency module operates within the existing bridge dispatch contract (ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001, DCL-SMART-POLLER-AUTO-TRIGGER-001, GOV-FILE-BRIDGE-AUTHORITY-001); it introduces a mechanism, not a new behavior contract. The scoping thread established that the scheduler program needs no new GOV/SPEC/ADR/DCL artifact. No new or revised requirement is required before implementing Slice 4.

## Clause Scope Clarification (Not a Bulk Operation)

Slice 4 creates one new Python module and one new test file. It does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` - which requires a bulk-operation inventory artifact and review packet, a Path/Phase-deferred decision marker, or an explicit owner-approval packet for a bulk action - is not applicable. The single work item cited (WI-3375) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## In-Root Placement Evidence

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, every artifact of this slice is within the `E:\GT-KB` project root:

- `E:\GT-KB\scripts\bridge_dispatch_concurrency.py` - new module, in-root.
- `E:\GT-KB\platform_tests\scripts\test_bridge_dispatch_concurrency.py` - new test file, in-root.
- `E:\GT-KB\.gtkb-state\bridge-poller\workers\<role>\` - runtime worker-slot directory, created by the module at runtime, in-root. Tests never touch it: every test runs under an isolated pytest `tmp_path` state directory.

No `applications/` paths. No paths outside `E:\GT-KB`.

## Scope

### New module: scripts/bridge_dispatch_concurrency.py

A standalone, stdlib-only module providing per-role dispatch concurrency limits and in-flight worker tracking. Public API:

- `role_limit(role) -> int` - resolves the concurrency limit for a dispatch role. Reads the per-role environment override `GTKB_DISPATCH_CONCURRENCY_<ROLE>` (e.g. `GTKB_DISPATCH_CONCURRENCY_PRIME_BUILDER`) when set to a positive integer, otherwise the default from `DEFAULT_ROLE_LIMITS` (`loyal-opposition` = 3, `prime-builder` = 2 - inside the owner's stated LO 2-4 / Prime 1-3 ranges).
- `register_worker(role, *, state_dir, ttl_seconds=DEFAULT_WORKER_TTL_SECONDS) -> WorkerSlot | None` - atomically claims one of the role's bounded slots. Returns a `WorkerSlot` on success, or `None` when the role is already at `role_limit(role)` fresh workers.
- `release_worker(slot)` and `WorkerSlot.release()` - free the slot, token-guarded by the slot's uuid4 token.
- `refresh_worker(slot)` and `WorkerSlot.refresh()` - rewrite the slot's heartbeat so a long-running worker is not reclaimed; ownership-guarded; atomic temp + `os.replace`.
- `in_flight_count(role, *, state_dir) -> int` - the count of fresh (non-stale) worker slots for the role.
- `available_slots(role, *, state_dir) -> int` - `max(0, role_limit(role) - in_flight_count(role, ...))`.
- `reclaim_stale_workers(state_dir) -> list[str]` - sweep all role directories and remove stale slot files; return the reclaimed slot identifiers.
- `worker_slot(role, *, state_dir, ttl_seconds=...)` - a context manager that registers on enter (raising `DispatchCapacityExhausted` when the role is at capacity) and releases on exit including on exception.

Bounded-slot mechanism: each role's in-flight workers are tracked as files `<state_dir>/workers/<role>/slot-<n>.lock` for `n` in `0 .. role_limit(role) - 1`. `register_worker` walks the slot indices and atomically creates the first free one via `os.open` with `O_CREAT | O_EXCL | O_WRONLY`; the bounded index range caps registration at exactly `role_limit(role)` regardless of how many callers race. A slot index whose file exists but is stale (heartbeat aged past `ttl_seconds`) is token-guarded-reclaimed and reused. When every slot index is held fresh, `register_worker` returns `None`. Slot files record `schema_version`, `role`, `slot_index`, `worker_token` (uuid4), `pid`, `acquired_at`, `heartbeat_at`, and `ttl_seconds`.

`DEFAULT_WORKER_TTL_SECONDS = 1800` - a dispatched worker is a whole counterpart-harness session that may run many minutes; the staleness bound is generous so a genuinely-running worker is not falsely reclaimed, and long workers call `refresh_worker`. Staleness is heartbeat-TTL based, never a PID-liveness probe, keeping the module cross-platform - the same choice the Slice 2 lease registry made.

Per-role independence: each role has its own slot directory and its own limit; filling Prime Builder's slots never blocks Loyal Opposition registration.

Self-contained: stdlib only (`os`, `json`, `re`, `uuid`, `contextlib`, `datetime`, `pathlib`). No import of dispatch code, the Slice 2 lease registry, or the Slice 3 writer. Slice 4 delivers the primitive in isolation; coupling it to its siblings or the dispatch path is the integration step.

Not in Slice 4: replacing `DEFAULT_MAX_ITEMS` in `cross_harness_bridge_trigger.py` or `single_harness_bridge_dispatcher.py`, and wiring the Slice 2 lease registry / Slice 3 writer / Slice 4 concurrency module into the live dispatch loop. See Loyal Opposition Ask 1.

## Files Expected To Change

- `scripts/bridge_dispatch_concurrency.py` - NEW. The per-role dispatch concurrency module described above.
- `platform_tests/scripts/test_bridge_dispatch_concurrency.py` - NEW. The Slice 4 test suite (T1-T13 below).
- Runtime artifact, not a Write/Edit-tool target: the `<state_dir>/workers/<role>/slot-<n>.lock` files, created by the module at runtime. Tests use an isolated `tmp_path` state directory so the real worker directory is never touched.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| Scoping Slice 4 (per-role concurrency limit with owner-hinted defaults) | T1 asserts `role_limit` defaults (LO=3, Prime=2); T2 asserts the per-role env override is honored. |
| Scoping Slice 4 (scheduler tracks in-flight worker count per role; the limit holds) | T3-T7 cover register, at-capacity `None`, per-role independence, release, and `in_flight_count` / `available_slots`; T12 runs barrier-synchronized concurrent `register_worker` calls and asserts exactly `role_limit` slots are granted under the race. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (slot lifecycle registered -> held -> refreshed -> released/reclaimed) | T8 covers stale -> reclaim; T9 covers refresh; T10 covers the token ownership guard on release; T11 covers `reclaim_stale_workers`; T13 covers the `worker_slot` context manager including `DispatchCapacityExhausted` and release-on-exception. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All tests run under an isolated `tmp_path` state directory; the module resolves slot paths under the in-root `.gtkb-state/bridge-poller/workers/`. |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | Slice 4 adds no dispatch-path code; verification is by inspection that `cross_harness_bridge_trigger.py` and `single_harness_bridge_dispatcher.py` are absent from `target_paths` and unmodified. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed pytest command and observed results. |

Slice 4 test suite (`platform_tests/scripts/test_bridge_dispatch_concurrency.py`), all under an isolated `tmp_path`:

- T1 - `role_limit` returns the defaults: `loyal-opposition` = 3, `prime-builder` = 2.
- T2 - `role_limit` honors a per-role `GTKB_DISPATCH_CONCURRENCY_<ROLE>` environment override.
- T3 - `register_worker` returns a `WorkerSlot` and creates the slot file when capacity is available.
- T4 - `register_worker` returns `None` once the role holds `role_limit(role)` fresh workers.
- T5 - per-role independence: filling `prime-builder` to capacity does not block `loyal-opposition` registration.
- T6 - `release_worker` frees a slot; a subsequent `register_worker` for the role then succeeds.
- T7 - `in_flight_count` and `available_slots` track register and release correctly.
- T8 - a stale worker slot (heartbeat older than `ttl_seconds`) is reclaimed and reused by `register_worker`.
- T9 - `refresh_worker` extends freshness: a slot near expiry, once refreshed, is no longer stale.
- T10 - `release_worker` is token-guarded: a handle whose token no longer matches the on-disk slot does not free it.
- T11 - `reclaim_stale_workers` removes only stale slots and returns their identifiers.
- T12 - concurrent registration: with `role_limit(role) = L`, N barrier-synchronized threads calling `register_worker` yield exactly `L` `WorkerSlot` results and `N - L` `None` results.
- T13 - the `worker_slot` context manager registers on enter, releases on exit, releases on exception, and raises `DispatchCapacityExhausted` when the role is at capacity.

Verification command for the post-implementation report: `python -m pytest platform_tests/scripts/test_bridge_dispatch_concurrency.py -q`, plus `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-4` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-4`.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/bridge_dispatch_concurrency.py` exists and exposes `role_limit`, `register_worker`, `release_worker`, `refresh_worker`, `in_flight_count`, `available_slots`, `reclaim_stale_workers`, and the `worker_slot` context manager.
- [ ] `role_limit` defaults to LO=3 / Prime=2 and honors the per-role environment override.
- [ ] Worker registration is a bounded atomic slot pool via `O_CREAT | O_EXCL`; concurrent registration grants exactly `role_limit(role)` slots and no more (T12).
- [ ] Slots carry PID, `acquired_at`, `heartbeat_at`, and a uuid4 token; staleness is heartbeat-TTL-based; `release_worker` is token-guarded.
- [ ] `platform_tests/scripts/test_bridge_dispatch_concurrency.py` covers T1-T13, passes, and uses isolated temp roots.
- [ ] No existing dispatch code is modified - Slice 4 is purely additive.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this `-001` draft via `--content-file` before the live INDEX entry is inserted, and re-run against the indexed operative file after filing.

Expected and observed results:

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: exit 0; five clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

- R1 (low): a stale-slot handling bug permanently consumes a role's capacity. Mitigation: the heartbeat-TTL reclaim path is directly tested (T8, T11); `DEFAULT_WORKER_TTL_SECONDS = 1800` bounds any stuck slot, and long workers refresh.
- R2 (low): the new module has no consumer until the integration step. Mitigation: this is the GO'd scoping sub-slice boundary; the T1-T13 suite exercises every code path in isolation.
- R3 (low): a worker TTL set too short would falsely reclaim a slot held by a still-running worker, letting an extra worker dispatch. Mitigation: the 1800 s default is generous for a counterpart-harness session, the value is configurable, and `refresh_worker` lets long workers extend their heartbeat.
- R4 (very low): cross-platform atomicity. Mitigation: `O_CREAT | O_EXCL` create and `os.replace` are atomic on both Windows and POSIX; T12 asserts the limit holds under concurrent registration.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue beyond any runtime slot files, which are themselves reclaimable by TTL.

## Loyal Opposition Asks

1. Confirm that scoping Slice 4 as a standalone per-role concurrency module - with no dispatch-path wiring, and the `DEFAULT_MAX_ITEMS` replacement plus the Slice 2/3/4 dispatch-loop integration deferred to a distinct integration step - is the correct disposition. Slice 2 explicitly deferred its dispatch wiring and Slice 3 deferred its; Slice 4 follows that established pattern. If the GO'd scoping plan should instead be read as requiring Slice 4 to modify `cross_harness_bridge_trigger.py` directly, NO-GO with that direction and Prime will re-scope.
2. Confirm the bounded-slot-pool design (`slot-<n>.lock` for `n` in `0 .. limit-1`, atomic `O_CREAT | O_EXCL` per slot) correctly caps concurrent registration at exactly `role_limit(role)`.
3. Confirm `DEFAULT_WORKER_TTL_SECONDS = 1800` with a `refresh_worker` heartbeat is the right staleness model for a worker slot (versus the 300 s the Slice 2 lease registry used for a per-document lease).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
