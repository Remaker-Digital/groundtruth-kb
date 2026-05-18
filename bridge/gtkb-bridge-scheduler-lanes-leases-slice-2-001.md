NEW

# Bridge Scheduler Slice 2: Per-Document Lease Registry

bridge_kind: implementation_proposal
Document: gtkb-bridge-scheduler-lanes-leases-slice-2
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3373 (bridge scheduler Slice 2 - per-document lease registry); sub-slice 2 of the GO'd gtkb-bridge-scheduler-lanes-leases-slice-1-scoping plan
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3373
target_paths: ["scripts/bridge_lease_registry.py", "platform_tests/scripts/test_bridge_scheduler_leases.py"]
Recommended commit type: feat:

## Summary

This is Slice 2 of the bridge scheduler program. The GO'd scoping thread `gtkb-bridge-scheduler-lanes-leases-slice-1-scoping` (Loyal Opposition GO at `-002`) approved a five-sub-slice plan to replace the fixed `DEFAULT_MAX_ITEMS = 2` dispatch cap in `scripts/cross_harness_bridge_trigger.py` with a lease-based worker scheduler. The approved sequence is: Slice 2 per-document lease registry, Slice 3 serialized INDEX writer, Slice 4 per-role concurrency limits, Slice 5 lane classification, Slice 6 aging and priority.

Slice 2 delivers the foundation: a per-document lease registry — a standalone, atomic lease-acquisition mechanism keyed on `bridge/INDEX.md` document slugs. Once per-role concurrency rises above one worker (Slice 4), the registry guarantees two workers can never process or write verdicts for the same bridge thread simultaneously.

Slice 2 is purely additive: one new module (`scripts/bridge_lease_registry.py`) plus its test suite (`platform_tests/scripts/test_bridge_scheduler_leases.py`). No existing dispatch code is modified. The dispatch path consumes the registry in Slice 4, where raising concurrency above one worker per role makes leasing load-bearing.

## Background

The cross-harness event-driven trigger currently dispatches at most `DEFAULT_MAX_ITEMS` (= 2) bridge threads to a single worker, processed serially. The scoping thread recorded the owner's S350 (2026-05-14) throughput directive, points 2-3, and fixed the sub-slice boundaries. The leases are the load-bearing safety mechanism: with more than one concurrent worker per role, an unguarded design would let two workers grab the same NEW or REVISED entry — the duplicate-work hazard the single per-harness active-session lock currently prevents crudely. The lease registry replaces that crude harness-wide guard with a precise per-document one, so Slice 4 can raise concurrency without reintroducing the S308 blind-spawn-storm failure mode or `bridge/INDEX.md` write races.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — `bridge/INDEX.md` is canonical workflow state; the lease registry exists so no two workers process or write a verdict for the same INDEX document concurrently.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — the new module, the new test file, and the runtime lease directory are all within the `E:\GT-KB` project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the spec-to-test mapping below derives the Slice 2 test suite from the linked specifications.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — the bridge dispatch automation contract; Slice 2 adds a mechanism but does not touch the dispatch path, so the auto-trigger contract is preserved unchanged.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 — auto-trigger contract preserved; Slice 2 does not alter dispatch behavior or actionable-signature computation.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — the lease registry is topology-agnostic and consumable by both the cross-harness trigger and the single-harness dispatcher.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 — the single-harness substrate will consume the same registry in a later slice.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — lease records are durable runtime artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across the slice family is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — lease lifecycle is acquired -> held -> refreshed -> released or reclaimed (advisory).

## Prior Deliberations

- `gtkb-bridge-scheduler-lanes-leases-slice-1-scoping` (GO at `-002`) — the design authority for this slice. It approved the five-sub-slice plan and the design decisions Slice 2 implements: per-document lease granularity, process-bound plus sanity-bound TTL, and file-lock (not in-memory) serialization. Its GO `-002` carried the program's deliberation search and cited DELIB-1568, DELIB-1550, DELIB-1496, and DELIB-1522; those are carried forward here.
- DELIB-2182 — the owner-authorization deliberation for the bridge scheduler program. It records the S350 throughput directive and the 2026-05-18 AskUserQuestion decisions, and is the owner decision the project authorization envelope references.
- `gtkb-cross-harness-trigger-active-session-suppression-001` (VERIFIED) — the current single-per-harness-lock suppression contract. Slice 2's per-document lease registry is the finer-grained guard the scheduler program will eventually substitute for that harness-wide lock.
- `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement` — retired interval polling. Slice 2 must not reintroduce it; the lease registry is a passive module with no polling loop.
- The S308 incident recorded in the bridge-essential rule — the blind-spawn-storm lesson. The lease registry is part of the safety foundation that lets Slice 4 raise concurrency without repeating activity-independent duplicate work.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and to scaffold the full program (Slices 2-6). That decision is recorded as DELIB-2182. The MemBase project `PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES`, work items WI-3373 through WI-3377, and the project authorization `PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION` (status active; owner decision DELIB-2182) were created under that authorization. This Slice 2 proposal implements WI-3373 within that authorized scope. It asserts no new requirement and requires no further owner decision before GO; the design boundary it implements was fixed by the scoping thread's GO.

## Requirement Sufficiency

Existing requirements sufficient. The lease registry operates within the existing bridge dispatch contract (ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001, DCL-SMART-POLLER-AUTO-TRIGGER-001, GOV-FILE-BRIDGE-AUTHORITY-001); it introduces a mechanism, not a new behavior contract. The scoping thread established that the scheduler program needs no new GOV/SPEC/ADR/DCL artifact. No new or revised requirement is required before implementing Slice 2.

## Clause Scope Clarification (Not a Bulk Operation)

Slice 2 creates one new Python module and one new test file. It does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact and review packet, or an explicit owner-approval packet for a bulk action — is not applicable. The scoping thread's clause preflight classified this clause `may_apply`; for this code slice it is not applicable. The single work item cited (WI-3373) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## In-Root Placement Evidence

- `E:\GT-KB\scripts\bridge_lease_registry.py` — new module, in-root.
- `E:\GT-KB\platform_tests\scripts\test_bridge_scheduler_leases.py` — new test file, in-root.
- `E:\GT-KB\.gtkb-state\bridge-poller\leases\` — runtime lease directory, created by the module at runtime, in-root.

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`.

## Scope

### New module: scripts/bridge_lease_registry.py

The module provides per-document advisory leases for bridge thread processing. A lease is a small JSON file at `.gtkb-state/bridge-poller/leases/<doc-slug>.lock`.

Public API:

- `acquire_lease(doc_slug, *, action, state_dir, ttl_seconds=DEFAULT_LEASE_TTL_SECONDS) -> LeaseHandle | None` — atomically creates the lease file. Returns a `LeaseHandle` on success, or `None` when a fresh lease is already held. Atomicity is provided by `os.open(path, O_CREAT | O_EXCL | O_WRONLY)`: if the file already exists the call raises `FileExistsError`, which the function catches. When the existing lease is stale (heartbeat older than its `ttl_seconds`), the stale file is reclaimed and acquisition is retried once.
- `release_lease(handle) -> None` and `LeaseHandle.release()` — remove the lease file. Ownership-guarded: the file is removed only when its on-disk `lease_token` still matches the handle's token, so a worker cannot delete a lease that went stale, was reclaimed, and is now held by another worker.
- `refresh_lease(handle) -> None` and `LeaseHandle.refresh()` — rewrite the lease's `heartbeat_at` so a long-running holder does not go stale.
- `is_lease_held(doc_slug, *, state_dir) -> bool` — True iff a fresh (non-stale) lease file exists for the slug.
- `reclaim_stale_leases(state_dir) -> list[str]` — sweep the lease directory, remove all stale lease files, and return the reclaimed slugs.
- `document_lease(doc_slug, *, action, state_dir, ttl_seconds=...)` — a context manager that acquires on enter (raising `LeaseUnavailable` when a fresh lease is held), and releases on exit, including on exception.

Lease file content (JSON): `schema_version`, `doc_slug`, `lease_token` (uuid4 generated at acquisition), `pid`, `acquired_at` (UTC ISO-8601), `heartbeat_at` (UTC ISO-8601), `action`, and `ttl_seconds`.

Staleness: a lease is stale when `now - heartbeat_at > ttl_seconds`. `DEFAULT_LEASE_TTL_SECONDS = 300`, per the scoping thread's design decision (process-bound plus sanity-bound TTL). The `pid` is recorded for diagnostics and audit; staleness is determined by the heartbeat timestamp and TTL, not by a PID-liveness probe — this keeps the module cross-platform and consistent with the existing `check_counterpart_active` mtime-TTL pattern in `cross_harness_bridge_trigger.py`.

Slug safety: `doc_slug` is validated against the kebab-case bridge-document-slug pattern; a slug that fails validation raises `ValueError`, defending the lease filename against path traversal.

Not in Slice 2: wiring the registry into `cross_harness_bridge_trigger.py` or `single_harness_bridge_dispatcher.py`. Per the GO'd scoping sub-slice plan, the dispatch path consumes the registry in Slice 4 (per-role concurrency), where more than one concurrent worker per role makes leasing load-bearing. Slice 2 delivers and proves the mechanism in isolation, keeping it a pure addition with zero regression surface on the live dispatch path.

## Files Expected To Change

- `scripts/bridge_lease_registry.py` — NEW. The per-document lease registry module described above.
- `platform_tests/scripts/test_bridge_scheduler_leases.py` — NEW. The Slice 2 test suite (T1-T12 below).
- Runtime artifact, not a Write/Edit-tool target: the `.gtkb-state/bridge-poller/leases/` directory and `<doc-slug>.lock` files, created by the module at runtime. Tests use an isolated `tmp_path` state directory so the real lease directory is never touched.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 (no two workers process or verdict the same INDEX document) | T2 asserts a second `acquire_lease` for a held slug returns `None`; T10 asserts the `document_lease` context manager raises `LeaseUnavailable`; T12 asserts a concurrent double-acquire yields exactly one winner. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (lease lifecycle acquired -> held -> refreshed -> released/reclaimed) | T1, T3, T7, T8 cover acquire, held, refresh, release; T4-T6 cover the stale -> reclaim transition. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All tests run under an isolated `tmp_path` state directory; the module resolves lease paths under the in-root `.gtkb-state/bridge-poller/leases/`. |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | Slice 2 adds no dispatch-path code; verification is by inspection that `cross_harness_bridge_trigger.py` and `single_harness_bridge_dispatcher.py` are absent from `target_paths` and unmodified. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed pytest command and observed results. |

Slice 2 test suite (`platform_tests/scripts/test_bridge_scheduler_leases.py`), all under an isolated `tmp_path`:

- T1 — `acquire_lease` creates the lease file with correct metadata (slug, pid, token, acquired_at, action, ttl).
- T2 — a second `acquire_lease` on a held fresh slug returns `None`.
- T3 — `release_lease` removes the file; a subsequent `acquire_lease` then succeeds.
- T4 — a stale lease (heartbeat older than ttl) is reclaimed: `acquire_lease` succeeds and replaces it.
- T5 — a fresh lease is NOT reclaimed by `reclaim_stale_leases`.
- T6 — `reclaim_stale_leases` removes only stale leases and returns their slugs.
- T7 — `refresh_lease` extends freshness: a lease near expiry, once refreshed, is no longer stale.
- T8 — `is_lease_held` is true when fresh, false when absent, false when stale.
- T9 — `release_lease` is ownership-guarded: a handle whose token no longer matches the on-disk lease does not delete it.
- T10 — the `document_lease` context manager acquires on enter, releases on exit, and releases on exception.
- T11 — an invalid `doc_slug` (path-unsafe characters) raises `ValueError`.
- T12 — concurrent double-acquire: two `acquire_lease` calls before either releases yield exactly one handle and one `None`.

Verification command for the post-implementation report: `python -m pytest platform_tests/scripts/test_bridge_scheduler_leases.py -q`, plus `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-2` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-2`.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/bridge_lease_registry.py` exists and exposes `acquire_lease`, `release_lease`, `refresh_lease`, `is_lease_held`, `reclaim_stale_leases`, and the `document_lease` context manager.
- [ ] Lease acquisition is atomic via `O_CREAT | O_EXCL`; two concurrent acquisitions of the same slug yield exactly one holder.
- [ ] Leases carry PID, `acquired_at`, `heartbeat_at`, and `action` metadata; staleness is heartbeat-TTL-based with `DEFAULT_LEASE_TTL_SECONDS = 300`.
- [ ] `release_lease` is ownership-guarded by the lease token.
- [ ] `platform_tests/scripts/test_bridge_scheduler_leases.py` covers T1-T12, passes, and uses isolated temp roots.
- [ ] No existing dispatch code (`cross_harness_bridge_trigger.py`, `single_harness_bridge_dispatcher.py`) is modified — Slice 2 is purely additive.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this `-001` draft via `--content-file` before the live INDEX entry is inserted, and re-run against the indexed operative file after filing.

Expected and observed results:

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. The generated packet hash is recorded in the Loyal Opposition GO verdict.
- Clause preflight: exit 0; five clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

- R1 (low): a stale-lease handling bug blocks work. Mitigation: the heartbeat-TTL reclaim path is directly tested (T4-T7); `DEFAULT_LEASE_TTL_SECONDS = 300` bounds any stuck lease.
- R2 (low): the new module has no consumer until Slice 4. Mitigation: this is the GO'd scoping sub-slice boundary; Slice 2 proves the mechanism in isolation and its test suite exercises every code path. Slice 4 is the consumer.
- R3 (very low): cross-platform atomicity of lease acquisition. Mitigation: `O_CREAT | O_EXCL` create is atomic on both Windows and POSIX; T12 asserts the single-winner property.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue beyond any runtime lease files, which are themselves reclaimable by TTL.

## Loyal Opposition Asks

1. Confirm that scoping Slice 2 as a standalone lease-registry module — with no dispatch-path wiring, the registry consumed by Slice 4 — matches the GO'd sub-slice plan in `gtkb-bridge-scheduler-lanes-leases-slice-1-scoping`.
2. Confirm that heartbeat-TTL staleness (no cross-platform PID-liveness probe; PID recorded for diagnostics only) is the right call, consistent with the existing `check_counterpart_active` mtime-TTL pattern.
3. Confirm the lease-token ownership guard on `release_lease` adequately closes the stale-reclaim-then-wrong-release race.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
