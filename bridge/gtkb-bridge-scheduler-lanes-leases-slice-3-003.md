NEW

# Post-Implementation Report - Bridge Scheduler Slice 3: Serialized bridge/INDEX.md Writer (WI-3374)

bridge_kind: implementation_report
Document: gtkb-bridge-scheduler-lanes-leases-slice-3
Version: 003 (NEW; post-implementation report for the GO at bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-002.md)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3374 (bridge scheduler Slice 3 - serialized bridge/INDEX.md writer)
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3374
target_paths: ["scripts/bridge_index_writer.py", "platform_tests/scripts/test_bridge_index_writer.py"]
Recommended commit type: feat:

## Summary

The GO'd proposal at bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-001.md (Loyal Opposition GO at -002) is implemented. Two new files were added: scripts/bridge_index_writer.py (the serialized INDEX-writer module) and platform_tests/scripts/test_bridge_index_writer.py (its T1-T10 test suite). No existing file was modified - the slice is purely additive. The full test suite passes (10 passed), including the concurrent no-lost-update test (T4) and the serialized-observation test (T9).

## Recommended Commit Type

feat: - the change adds a new capability surface (the serialized bridge/INDEX.md writer module and its tests). It is net-new code, matching the GO'd proposal's recommended type.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is the canonical bridge workflow state; the serialized writer preserves that invariant under concurrent workers by serializing every read-modify-write of the file.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the new module, the new test file, and the runtime lock directory are all within the E:\GT-KB project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries forward every relevant governing specification from the proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the executed test suite from the linked specifications.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - the bridge dispatch automation contract; Slice 3 adds a mechanism but does not touch the dispatch path, so the auto-trigger contract is preserved unchanged.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 - auto-trigger contract preserved; Slice 3 does not alter dispatch behavior or actionable-signature computation.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the writer is topology-agnostic and consumable by both the cross-harness trigger and the single-harness dispatcher.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the single-harness substrate will consume the same writer in a later slice.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the lock record is a durable runtime artifact (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the slice family is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - lock lifecycle is acquired -> held -> released or reclaimed (advisory).

## Prior Deliberations

- gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (GO at -002) - the design authority; design decision 3 fixed "INDEX serialization = file lock, not in-memory queue". The implemented module is the file-lock primitive.
- DELIB-2182 - the owner-authorization deliberation for the bridge scheduler program.
- gtkb-bridge-scheduler-lanes-leases-slice-2 (VERIFIED at -004) - the sibling lease registry; Slice 3 follows the same O_CREAT|O_EXCL atomic-exclusive-create technique.
- bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-002.md - the GO on this slice; its two P4-INFO notes (keep mutate scoped to the in-memory transform; preserve T9) and its eight follow-on constraints are addressed in this report.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and scaffold the full program (Slices 2-6); that decision is recorded as DELIB-2182. The MemBase project PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES, work items WI-3373 through WI-3377, and the project authorization were created under that authorization. This Slice 3 implementation is within that authorized scope and asserts no new requirement.

## Clause Scope Clarification (Not a Bulk Operation)

This implementation creates one new Python module and one new test file. It does not resolve, retire, promote, batch-mutate, or produce an inventory of work items. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS is not applicable. The single work item cited (WI-3374) is this report's own implementing work item under the mandatory project-linkage metadata.

## What Was Implemented

scripts/bridge_index_writer.py - a standalone, stdlib-only module providing serialized atomic mutation of a bridge index file. It exposes the GO-approved public API names exactly:

- atomic_index_update(index_path, mutate, *, state_dir, timeout_seconds, ttl_seconds) -> str - acquires the exclusive INDEX-write lock, reads the index (a missing file is treated as empty), calls mutate(current_text) -> new_text inside the lock, writes new_text atomically, releases the lock, and returns the written text. mutate is the only caller-supplied operation in the critical section; the docstring states callers must do any expensive analysis before acquiring the lock (GO P4-INFO).
- index_write_lock(*, state_dir, timeout_seconds, ttl_seconds) - a context manager exposing the exclusive lock directly; acquires on enter, releases on exit including on exception.
- IndexWriteLockTimeout(RuntimeError) - raised when the lock is not acquired within timeout_seconds.

Mechanism: an exclusive lock file at <state_dir>/index-writer.lock created via os.open with O_CREAT | O_EXCL | O_WRONLY (the atomic-exclusive-create technique proven in the VERIFIED Slice 2 lease registry); the lock record carries lock_token (uuid4), pid, acquired_at, heartbeat_at. Bounded-wait acquisition retries on a ~50 ms poll-backoff until won or timeout_seconds; a lock whose heartbeat aged past ttl_seconds (default 30 s) is reclaimed by the next acquirer, token-guarded so two waiters racing to reclaim cannot delete a freshly re-acquired lock. INDEX writes are atomic via a sibling temp file plus os.replace.

platform_tests/scripts/test_bridge_index_writer.py - the T1-T10 test suite, all under an isolated pytest tmp_path; 10 passed.

Implementation notes for the reviewer (two concurrency defects were found by the T4 concurrent test during implementation and fixed before this report):

- Partial-write defect: os.write may write fewer bytes than requested; a partial write left truncated JSON in the lock file that no reader could parse, so the lock could never be released or reclaimed. Fixed: _try_create_lock loops os.write over a memoryview until the full payload lands.
- Windows delete-while-open defect: on Windows, os.remove of the lock file failed transiently when a bounded-wait poller had the lock file briefly open for its staleness read; the failure was an OSError that the release path suppressed, leaking the lock. Fixed two ways: (1) waiting acquirers re-read the lock file for the staleness check only every ~2 s rather than on every ~50 ms poll, so pollers almost never hold a handle; (2) _release retries os.remove on a short backoff, since a reader's handle is held only microseconds. The T4 concurrent test (which initially hung on this defect) now passes in under 2 s.

Both fixes are within the GO-approved design and target_paths; they are correctness fixes to the lock primitive, not scope changes.

## Spec-To-Test Mapping

| Spec / governing surface | Verification | Result |
| --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 (no two workers corrupt or lose an INDEX update) | T3 asserts a single atomic_index_update applies its mutation; T4 runs 20 barrier-synchronized concurrent atomic_index_update calls each appending a distinct line and asserts every line is present (no lost update); T9 asserts each serialized mutation observes the prior mutation's written result. | PASS - T3, T4, T9. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (lock lifecycle acquired -> held -> released/reclaimed) | T1 acquire+release; T2 held lock blocks a second acquirer to IndexWriteLockTimeout; T5 release on exception; T6 stale-lock reclaim; T7 fresh-lock retention; T8 release on a raising mutate. | PASS - T1, T2, T5, T6, T7, T8. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All tests run under an isolated tmp_path state directory; the module resolves the lock and temp paths under the in-root state dir. | PASS. |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | No dispatch-path code was added; cross_harness_bridge_trigger.py and single_harness_bridge_dispatcher.py are absent from target_paths and unmodified. | PASS - by inspection. |
| Atomic write / temp-file hygiene | T8 asserts a raising mutate leaves the index unchanged; T10 asserts no sibling temp file remains after a successful update. | PASS - T8, T10. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This report carries the mapping plus the executed pytest command and observed results below. | PASS. |

## Verification Commands And Observed Results

1. `python -m pytest platform_tests/scripts/test_bridge_index_writer.py -q`
   Result: 10 passed in 1.98s. All of T1-T10 pass, including T4 (20-thread concurrent no-lost-update) and T9 (serialized observation order).

2. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-3` - see the Applicability Preflight section below.

3. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-3` - see the Clause Applicability section below.

## Acceptance Criteria

- [x] Loyal Opposition returned GO on the proposal (-002).
- [x] scripts/bridge_index_writer.py exists and exposes atomic_index_update, the index_write_lock context manager, and IndexWriteLockTimeout.
- [x] The INDEX-write lock is mutually exclusive via O_CREAT | O_EXCL; concurrent atomic_index_update calls serialize with no lost update (T4, T9).
- [x] Acquisition is bounded-wait: it retries until the lock is won or timeout_seconds elapses, then raises IndexWriteLockTimeout (T2).
- [x] A stale lock (heartbeat older than DEFAULT_LOCK_TTL_SECONDS = 30) is reclaimed; reclamation is token-guarded (T6, T7).
- [x] atomic_index_update writes atomically via temp file + os.replace; a raising mutate leaves the file unchanged (T8); no temp file remains (T10).
- [x] platform_tests/scripts/test_bridge_index_writer.py covers T1-T10, passes, and uses isolated temp roots.
- [x] No existing dispatch code is modified - Slice 3 is purely additive.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Applicability Preflight

The applicability preflight was run against this -003 report via `--content-file` prior to filing the INDEX entry:

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-3 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-003.md`

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:c6f7c67e144c5dbb4699f4c9e8704c9349470360c3390891462c0e4a01fa67f9

All applicable required and advisory cross-cutting specs are cited in this report's Specification Links.

## Clause Applicability

The ADR/DCL clause preflight was run against this -003 report via `--content-file` prior to filing the INDEX entry:

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-3 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-003.md`

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

- R1 (low): a stale-lock handling bug blocks INDEX writes. Mitigation: the heartbeat-TTL reclaim path is directly tested (T6, T7); DEFAULT_LOCK_TTL_SECONDS = 30 bounds any stuck lock.
- R2 (low): the bounded wait adds latency. Mitigation: the critical section is a sub-millisecond read-modify-write; the T4 suite of 20 concurrent updates completes in under 2 s.
- R3 (low): the new module has no consumer until a later integration slice. Mitigation: this is the GO'd scoping sub-slice boundary; the T1-T10 suite exercises every code path in isolation.
- R4 (low, addressed): cross-platform correctness of the lock primitive. The implementation found and fixed two Windows/concurrency defects (partial os.write; delete-while-open) under the T4 concurrent test; both are now covered and passing.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue beyond any runtime lock file, which is itself reclaimable by TTL.

## Loyal Opposition Asks

1. Confirm scripts/bridge_index_writer.py implements the GO'd -001 design: O_CREAT|O_EXCL mutual exclusion, bounded-wait acquisition, token-guarded stale reclaim, and atomic os.replace writes, with the approved public API names.
2. Confirm the two implementation-phase concurrency fixes (loop os.write for full payload; periodic staleness re-read plus os.remove retry for the Windows delete-while-open case) are correctness fixes within the GO-approved design and target_paths, not scope changes.
3. Confirm the T1-T10 suite, including the T4 concurrent no-lost-update test and the T9 serialized-observation test, is adequate verification for VERIFIED.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
