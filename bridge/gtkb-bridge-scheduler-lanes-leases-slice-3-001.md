NEW

# Bridge Scheduler Slice 3: Serialized bridge/INDEX.md Writer

bridge_kind: prime_proposal
Document: gtkb-bridge-scheduler-lanes-leases-slice-3
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3374 (bridge scheduler Slice 3 - serialized bridge/INDEX.md writer); sub-slice 3 of the GO'd gtkb-bridge-scheduler-lanes-leases-slice-1-scoping plan
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3374
target_paths: ["scripts/bridge_index_writer.py", "platform_tests/scripts/test_bridge_index_writer.py"]
Recommended commit type: feat:

## Summary

This is Slice 3 of the bridge scheduler program. The GO'd scoping thread `gtkb-bridge-scheduler-lanes-leases-slice-1-scoping` (Loyal Opposition GO at `-002`) approved a five-sub-slice plan; sub-slice 3 is the serialized `bridge/INDEX.md` writer. Its scoping design decision 3 fixed the mechanism: "INDEX serialization = file lock, not in-memory queue. Reasoning: must work across subprocesses."

Slice 3 delivers a standalone module — `scripts/bridge_index_writer.py` — that wraps every `bridge/INDEX.md` mutation in a process-exclusive file lock plus an atomic read-modify-write. Once Slice 4 raises per-role dispatch concurrency above one worker, this writer guarantees two workers can never interleave `bridge/INDEX.md` updates and corrupt the canonical workflow state.

Slice 3 is purely additive: one new module plus its test suite. No existing dispatch code is modified. Wiring the writer into `cross_harness_bridge_trigger.py`, `single_harness_bridge_dispatcher.py`, and the interactive Prime INDEX-edit path is integration work deferred to a later slice, consistent with the Slice 2 boundary (the lease registry was delivered and proven in isolation before any consumer adopted it).

## Background

`bridge/INDEX.md` is the canonical bridge workflow state (`GOV-FILE-BRIDGE-AUTHORITY-001`). Today INDEX mutations are unguarded: every writer reads the file, edits it, and writes it back with no mutual exclusion. With the fixed `DEFAULT_MAX_ITEMS = 2` dispatch cap and a single per-harness active-session lock, concurrent INDEX writes are rare enough to have escaped notice. Slice 4 removes that constraint by raising per-role concurrency, at which point two workers reading-then-writing INDEX can produce a lost update — one worker's new version line silently overwritten. The serialized writer is the load-bearing safety mechanism that makes Slice 4's concurrency raise safe.

The scoping thread's risk note (R3) anticipated this slice would measure lock-hold latency: INDEX writes are small and infrequent, so the critical section is sub-millisecond and the bounded wait is short.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is the canonical bridge workflow state; the serialized writer preserves that invariant under concurrent workers by serializing every read-modify-write of the file.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the new module, the new test file, and the runtime lock directory are all within the E:\GT-KB project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the Slice 3 test suite from the linked specifications.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - the bridge dispatch automation contract; Slice 3 adds a mechanism but does not touch the dispatch path, so the auto-trigger contract is preserved unchanged.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 - auto-trigger contract preserved; Slice 3 does not alter dispatch behavior or actionable-signature computation.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the writer is topology-agnostic and consumable by both the cross-harness trigger and the single-harness dispatcher.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the single-harness substrate will consume the same writer in a later slice.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the lock record is a durable runtime artifact (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the slice family is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - lock lifecycle is acquired -> held -> released or reclaimed (advisory).

## Prior Deliberations

- gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (GO at -002) - the design authority for this slice; design decision 3 fixed "INDEX serialization = file lock, not in-memory queue", and the Follow-On Constraints require "Serialize final bridge/INDEX.md writes even if review analysis runs in parallel."
- DELIB-2182 - the owner-authorization deliberation for the bridge scheduler program; it records the S350 throughput directive and the 2026-05-18 AskUserQuestion decisions.
- gtkb-bridge-scheduler-lanes-leases-slice-2 (VERIFIED at -004) - the sibling Slice 2 lease registry; Slice 3 follows the same standalone-primitive shape and the same atomic-create plus token-guard discipline.
- gtkb-cross-harness-trigger-active-session-suppression-001 (VERIFIED) - the current single-per-harness-lock suppression contract; the serialized INDEX writer is a finer-grained guard the scheduler program substitutes for that coarse lock.
- gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement - retired interval polling; the writer is a passive module with no polling loop and does not reintroduce it.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and scaffold the full program (Slices 2-6); that decision is recorded as DELIB-2182. The MemBase project PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES, work items WI-3373 through WI-3377, and the project authorization PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION (status active; owner decision DELIB-2182) were created under that authorization. This Slice 3 proposal implements WI-3374 within that authorized scope. It asserts no new requirement and requires no further owner decision before GO; the design boundary it implements was fixed by the scoping thread's GO.

## Requirement Sufficiency

Existing requirements sufficient. The serialized writer operates within the existing bridge workflow contract (GOV-FILE-BRIDGE-AUTHORITY-001) and the bridge dispatch contract (ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001, DCL-SMART-POLLER-AUTO-TRIGGER-001); it introduces a mechanism, not a new behavior contract. The scoping thread established that the scheduler program needs no new GOV/SPEC/ADR/DCL artifact. No new or revised requirement is required before implementing Slice 3.

## Clause Scope Clarification (Not a Bulk Operation)

Slice 3 creates one new Python module and one new test file. It does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` - which requires a bulk-operation inventory artifact and review packet, a Path/Phase-deferred decision marker, or an explicit owner-approval packet for a bulk action - is not applicable. The single work item cited (WI-3374) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## In-Root Placement Evidence

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, every artifact of this slice is within the `E:\GT-KB` project root:

- `E:\GT-KB\scripts\bridge_index_writer.py` - new module, in-root.
- `E:\GT-KB\platform_tests\scripts\test_bridge_index_writer.py` - new test file, in-root.
- `E:\GT-KB\.gtkb-state\bridge-poller\index-writer.lock` - runtime lock file, created by the module at runtime, in-root. Tests never touch it: every test runs under an isolated pytest `tmp_path` state directory.

No `applications/` paths. No paths outside `E:\GT-KB`.

## Scope

### New module: scripts/bridge_index_writer.py

A standalone, stdlib-only module providing serialized atomic mutation of a bridge index file. Public API:

- `atomic_index_update(index_path, mutate, *, state_dir, timeout_seconds=DEFAULT_LOCK_TIMEOUT_SECONDS, ttl_seconds=DEFAULT_LOCK_TTL_SECONDS) -> str` - the primary entry point. Acquires the exclusive INDEX-write lock, reads `index_path`, calls `mutate(current_text) -> new_text`, writes `new_text` atomically, releases the lock, and returns the written text. The entire read-modify-write runs inside the lock so two workers' updates serialize and neither is lost.
- `index_write_lock(*, state_dir, timeout_seconds=..., ttl_seconds=...)` - a context manager exposing the exclusive lock directly for callers that need to perform a multi-step INDEX mutation. Acquires on enter, releases on exit including on exception.
- `IndexWriteLockTimeout(RuntimeError)` - raised when the lock cannot be acquired within `timeout_seconds`.

Lock mechanism: an exclusive lock file at `<state_dir>/index-writer.lock`, created via `os.open` with `O_CREAT | O_EXCL | O_WRONLY` (binary mode where the platform offers it). The atomic exclusive create is the mutual-exclusion primitive - exactly one caller wins; this is the same cross-platform technique proven in the VERIFIED Slice 2 lease registry. The lock file records `pid`, `acquired_at`, and `heartbeat_at` (UTC ISO-8601) for diagnostics and stale detection.

Bounded-wait acquisition: unlike the Slice 2 lease registry's fail-fast `acquire_lease`, the INDEX writer WAITS for the lock. An INDEX mutation is a brief, expected-to-complete critical section, not a skippable unit of work. Acquisition retries on a short poll-backoff (`_POLL_INTERVAL_SECONDS`, ~50 ms) until the lock is won or `timeout_seconds` (default `DEFAULT_LOCK_TIMEOUT_SECONDS = 10`) elapses, at which point it raises `IndexWriteLockTimeout`.

Stale-lock reclamation: a lock whose `heartbeat_at` has aged past `ttl_seconds` (`DEFAULT_LOCK_TTL_SECONDS = 30`, a short sanity bound - the scoping risk note records that INDEX writes are sub-millisecond) is reclaimed by the next acquirer. Reclamation is token-guarded: the lock file carries a uuid4 `lock_token` and is removed only when the on-disk token still matches the token observed as stale, so two waiters racing to reclaim cannot delete a lock another waiter just acquired.

Atomic write: `new_text` is written to a sibling temp file and then `os.replace`-d over `index_path`. `os.replace` is atomic on both Windows and POSIX, so a crash mid-write never leaves a truncated or partial `bridge/INDEX.md`.

Self-contained: stdlib only (`os`, `json`, `time`, `uuid`, `contextlib`, `datetime`, `pathlib`). No import of dispatch code or `bridge_lease_registry`. Slice 3 delivers the primitive in isolation; coupling it to the lease registry or the dispatch path is deferred.

Not in Slice 3: wiring `atomic_index_update` into `cross_harness_bridge_trigger.py`, `single_harness_bridge_dispatcher.py`, or any interactive INDEX-edit path. Per the GO'd scoping sub-slice plan, integration is deferred; Slice 3 delivers and proves the mechanism in isolation, keeping it a pure addition with zero regression surface on the live dispatch path.

## Files Expected To Change

- `scripts/bridge_index_writer.py` - NEW. The serialized INDEX writer module described above.
- `platform_tests/scripts/test_bridge_index_writer.py` - NEW. The Slice 3 test suite (T1-T10 below).
- Runtime artifact, not a Write/Edit-tool target: the `<state_dir>/index-writer.lock` file, created by the module at runtime. Tests use an isolated `tmp_path` state directory so the real lock file is never touched.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 (no two workers corrupt or lose an INDEX update) | T3 asserts a single `atomic_index_update` applies its mutation; T4 runs many barrier-synchronized concurrent `atomic_index_update` calls each appending a distinct line and asserts the final file contains every line with none lost; T9 asserts each concurrent mutation observes the prior mutation's result (no lost update). |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (lock lifecycle acquired -> held -> released/reclaimed) | T1 covers acquire and release; T2 covers a held lock blocking a second acquirer to `IndexWriteLockTimeout`; T5/T8 cover release on exception; T6/T7 cover the stale -> reclaim transition and fresh-lock retention. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All tests run under an isolated `tmp_path` state directory; the module resolves the lock and temp paths under the in-root `.gtkb-state/bridge-poller/`. |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | Slice 3 adds no dispatch-path code; verification is by inspection that `cross_harness_bridge_trigger.py` and `single_harness_bridge_dispatcher.py` are absent from `target_paths` and unmodified. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed pytest command and observed results. |

Slice 3 test suite (`platform_tests/scripts/test_bridge_index_writer.py`), all under an isolated `tmp_path`:

- T1 - `index_write_lock` creates the lock file on enter and removes it on exit.
- T2 - while the lock is held, a second acquisition with a short `timeout_seconds` blocks then raises `IndexWriteLockTimeout`.
- T3 - `atomic_index_update` applies the `mutate` function; the file content equals the mutated text.
- T4 - many barrier-synchronized concurrent `atomic_index_update` calls, each appending a unique line, all succeed; the final file contains every appended line (no lost update, no corruption).
- T5 - the lock is released when the body of `index_write_lock` raises.
- T6 - a stale lock (heartbeat older than `ttl_seconds`) is reclaimed: a subsequent acquisition succeeds.
- T7 - a fresh lock is NOT reclaimed by a subsequent acquisition (it times out instead).
- T8 - when the `mutate` callable raises, `atomic_index_update` releases the lock and leaves `index_path` unchanged.
- T9 - serialized `atomic_index_update` calls compose: each mutation observes the previous mutation's written result.
- T10 - on a successful `atomic_index_update` no sibling temp file remains in the directory.

Verification command for the post-implementation report: `python -m pytest platform_tests/scripts/test_bridge_index_writer.py -q`, plus `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-3` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-3`.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/bridge_index_writer.py` exists and exposes `atomic_index_update`, the `index_write_lock` context manager, and `IndexWriteLockTimeout`.
- [ ] The INDEX-write lock is mutually exclusive via `O_CREAT | O_EXCL`; concurrent `atomic_index_update` calls serialize with no lost update (T4, T9).
- [ ] Acquisition is bounded-wait: it retries until the lock is won or `timeout_seconds` elapses, then raises `IndexWriteLockTimeout`.
- [ ] A stale lock (heartbeat older than `DEFAULT_LOCK_TTL_SECONDS = 30`) is reclaimed; reclamation is token-guarded.
- [ ] `atomic_index_update` writes atomically via temp file + `os.replace`; a raising `mutate` leaves the file unchanged.
- [ ] `platform_tests/scripts/test_bridge_index_writer.py` covers T1-T10, passes, and uses isolated temp roots.
- [ ] No existing dispatch code (`cross_harness_bridge_trigger.py`, `single_harness_bridge_dispatcher.py`) is modified - Slice 3 is purely additive.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this `-001` draft via `--content-file` before the live INDEX entry is inserted, and re-run against the indexed operative file after filing.

Expected and observed results:

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: exit 0; five clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

- R1 (low): a stale-lock handling bug blocks INDEX writes. Mitigation: the heartbeat-TTL reclaim path is directly tested (T6, T7); `DEFAULT_LOCK_TTL_SECONDS = 30` bounds any stuck lock to a short window.
- R2 (low): the bounded wait adds latency to INDEX writes. Mitigation: the critical section is a sub-millisecond read-modify-write per the scoping risk note; `_POLL_INTERVAL_SECONDS` is ~50 ms and `DEFAULT_LOCK_TIMEOUT_SECONDS = 10` is a generous ceiling reached only under genuine contention or a crashed holder.
- R3 (low): the new module has no consumer until a later integration slice. Mitigation: this is the GO'd scoping sub-slice boundary; the T1-T10 suite exercises every code path in isolation.
- R4 (very low): cross-platform atomicity. Mitigation: `O_CREAT | O_EXCL` create and `os.replace` are atomic on both Windows and POSIX; T4 asserts the no-lost-update property under concurrency.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue beyond any runtime lock file, which is itself reclaimable by TTL.

## Loyal Opposition Asks

1. Confirm that scoping Slice 3 as a standalone serialized-writer module - with no dispatch-path wiring, integration deferred - matches the GO'd sub-slice plan in `gtkb-bridge-scheduler-lanes-leases-slice-1-scoping`.
2. Confirm that bounded-wait acquisition (retry until won or timeout, then raise) is the correct semantics for the INDEX-write critical section, versus the Slice 2 lease registry's fail-fast `acquire_lease`.
3. Confirm the token-guarded stale-lock reclamation adequately closes the two-waiters-racing-to-reclaim race.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
