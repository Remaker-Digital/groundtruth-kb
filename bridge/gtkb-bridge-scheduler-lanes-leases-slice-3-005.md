REVISED

# Post-Implementation Report (REVISED) - Bridge Scheduler Slice 3: Serialized bridge/INDEX.md Writer (WI-3374)

bridge_kind: implementation_report
Document: gtkb-bridge-scheduler-lanes-leases-slice-3
Version: 005 (REVISED; post-implementation report addressing the NO-GO at bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-004.md)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3374 (bridge scheduler Slice 3 - serialized bridge/INDEX.md writer)
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3374
target_paths: ["scripts/bridge_index_writer.py", "platform_tests/scripts/test_bridge_index_writer.py"]
Recommended commit type: feat:

## Summary

The post-implementation report at bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-003.md received NO-GO at bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-004.md for a single P1 finding: a malformed or truncated index-writer.lock file was not reclaimed, because the acquisition path attempted stale reclamation only when the lock record parsed successfully. This revision fixes that defect in scripts/bridge_index_writer.py and adds two regression tests (T11, T12) in platform_tests/scripts/test_bridge_index_writer.py. The full suite now passes 12/12, including the original T1-T10 and the new malformed-lock coverage. Both changes remain within the GO-approved design and the proposal's target_paths; no other behavior changed.

## Recommended Commit Type

feat: - Slice 3 as a whole adds a new capability surface (the serialized bridge/INDEX.md writer module and its tests). The malformed-lock fix in this revision is a correctness fix within that in-flight feature, before VERIFIED; the eventual single commit of Slice 3 remains net-new code, so feat: is the correct type. This matches the GO'd proposal's recommended type and the -003 report.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is the canonical bridge workflow state; the serialized writer preserves that invariant under concurrent workers, and the malformed-lock fix removes a bridge-liveness risk where one unparseable lock file could block every future INDEX writer.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the module, the test file, and the runtime lock directory are all within the E:\GT-KB project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries forward every relevant governing specification from the proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the executed test suite, including the new malformed-lock tests, from the linked specifications.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - the bridge dispatch automation contract; Slice 3 adds a mechanism but does not touch the dispatch path, so the auto-trigger contract is preserved unchanged.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 - auto-trigger contract preserved; Slice 3 does not alter dispatch behavior or actionable-signature computation.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the writer is topology-agnostic and consumable by both the cross-harness trigger and the single-harness dispatcher.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the single-harness substrate will consume the same writer in a later slice.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the lock record is a durable runtime artifact (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the slice family is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - lock lifecycle is acquired -> held -> released or reclaimed; the fix ensures a malformed lock also reaches the reclaimed state (advisory).

## Prior Deliberations

- bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-004.md - the NO-GO this revision responds to; its single P1 finding and four required revisions are addressed in the Response To NO-GO section below.
- bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-003.md - the prior post-implementation report; its What Was Implemented content is carried forward and extended here.
- bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-002.md - the GO on this slice; its design constraints remain satisfied.
- gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (GO at -002) - the design authority; design decision 3 fixed "INDEX serialization = file lock, not in-memory queue".
- DELIB-2182 - the owner-authorization deliberation for the bridge scheduler program.
- gtkb-bridge-scheduler-lanes-leases-slice-2 (VERIFIED at -004) - the sibling lease registry; Slice 3 follows the same O_CREAT|O_EXCL atomic-exclusive-create technique and the same token-guarded stale-reclaim discipline.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and scaffold the full program (Slices 2-6); that decision is recorded as DELIB-2182. The MemBase project PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES, work items WI-3373 through WI-3377, and the project authorization PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION were created under that authorization. This Slice 3 revision is within that authorized scope, addresses a Loyal Opposition NO-GO, asserts no new requirement, and requires no further owner decision before re-verification.

## Clause Scope Clarification (Not a Bulk Operation)

This revision modifies one existing Python module and its existing test file. It does not resolve, retire, promote, or batch-mutate work items, and it produces no work-item inventory and requests no formal-artifact-approval packet for a bulk action. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS is not applicable. The single work item cited (WI-3374) is this report's own implementing work item under the mandatory project-linkage metadata.

## Response To NO-GO bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-004.md

The NO-GO recorded one P1 finding and four required revisions. Each is addressed.

P1 - Malformed lock files are not reclaimed, so INDEX writes can remain blocked.

Root cause confirmed: _read_lock_record returned None for both "file absent" and "file present but unparseable JSON", and _acquire's staleness check ran reclamation only on the `record is not None` branch. A malformed lock therefore survived until acquisition timeout and remained on disk, so the heartbeat-TTL stale bound no longer bounded a stuck writer.

Fix in scripts/bridge_index_writer.py:

1. New function _reclaim_malformed_lock(lock_path, ttl_seconds). It os.stat()s the lock file: a FileNotFoundError/OSError means the file is absent and there is nothing to reclaim - this is how "file absent" is now distinguished from "file present but malformed", with the absent case a self-guarding no-op. When the file is present it re-confirms the content is still unparseable (a parseable record means a fresh acquirer wrote a valid lock, which is left intact), then uses the lock file mtime as the fallback staleness signal: the malformed file is removed only when time.time() - mtime > ttl_seconds.

2. _acquire's staleness check now branches: when _read_lock_record returns a dict it uses the existing _is_stale + _reclaim_stale_lock path; when it returns None it calls _reclaim_malformed_lock. A malformed lock is therefore reclaimed via mtime once it has aged past ttl_seconds, exactly as the NO-GO recommended.

3. Docstring/comment alignment: _is_stale's docstring now states it only sees parsed dict records and that fully-unparseable files are handled by _reclaim_malformed_lock; the _try_create_lock comment now states that a crash between create and a complete write is the residual malformed-lock case handled by the new path.

Required revision 1 (fix malformed/truncated lock recovery): done - see above.
Required revision 2 (regression coverage for stale malformed reclamation and fresh malformed retention): done - T11 and T12 below.
Required revision 3 (rerun T1-T10 plus the new malformed-lock tests): done - 12 passed; see Verification Commands.
Required revision 4 (rerun both bridge preflights and carry results into the revised report): done - see Applicability Preflight and Clause Applicability.

The malformed file is removed only after ttl_seconds has elapsed, so a create still in progress is never deleted out from under its legitimate owner; T12 proves a fresh malformed lock is retained. The change is confined to scripts/bridge_index_writer.py and platform_tests/scripts/test_bridge_index_writer.py, within the proposal's target_paths.

## What Was Implemented

scripts/bridge_index_writer.py - the serialized INDEX-writer module, unchanged from the -003 report except for the malformed-lock fix above. It exposes the GO-approved public API names exactly: atomic_index_update, the index_write_lock context manager, and IndexWriteLockTimeout. Mechanism: an exclusive lock file at <state_dir>/index-writer.lock created via os.open with O_CREAT | O_EXCL | O_WRONLY; the lock record carries lock_token (uuid4), pid, acquired_at, heartbeat_at. Bounded-wait acquisition retries on a ~50 ms poll-backoff until won or timeout_seconds; a valid lock whose heartbeat aged past ttl_seconds (default 30 s) is token-guarded-reclaimed; a malformed lock aged past ttl_seconds (by mtime) is reclaimed via the new path. INDEX writes are atomic via a sibling temp file plus os.replace.

The two concurrency defects found and fixed during the -003 implementation (partial-write looping os.write; Windows delete-while-open os.remove retry) remain in place and are unchanged.

platform_tests/scripts/test_bridge_index_writer.py - the test suite, extended from T1-T10 to T1-T12; 12 passed. T11 and T12 are the new malformed-lock coverage:

- T11 - test_t11_stale_malformed_lock_is_reclaimed: writes a truncated, unparseable lock file, sets its mtime one hour into the past, then calls index_write_lock with ttl_seconds=30. The abandoned malformed lock is reclaimed, a fresh valid lock is acquired, and the lock file is removed on exit.
- T12 - test_t12_fresh_malformed_lock_not_reclaimed: writes a truncated, unparseable lock file with a current mtime, then attempts index_write_lock with timeout_seconds=0.3, ttl_seconds=30. Acquisition raises IndexWriteLockTimeout and the fresh malformed lock file is left on disk unchanged - it is not deleted out from under a possible create-in-progress.

## Spec-To-Test Mapping

| Spec / governing surface | Verification | Result |
| --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 (no two workers corrupt or lose an INDEX update) | T3 single atomic update; T4 20 barrier-synchronized concurrent updates with no lost update; T9 serialized observation order. | PASS - T3, T4, T9. |
| GOV-FILE-BRIDGE-AUTHORITY-001 (a malformed lock must not block INDEX writers indefinitely - the NO-GO -004 P1 liveness risk) | T11 asserts a stale malformed lock is reclaimed so a new writer acquires; T12 asserts a fresh malformed lock is retained, so reclamation is bounded by ttl. | PASS - T11, T12. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (lock lifecycle acquired -> held -> released/reclaimed, including the malformed case) | T1 acquire+release; T2 held lock blocks; T5 release on exception; T6 valid stale-lock reclaim; T7 fresh-lock retention; T8 release on raising mutate; T11 malformed stale-lock reclaim; T12 malformed fresh-lock retention. | PASS - T1, T2, T5, T6, T7, T8, T11, T12. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All tests run under an isolated tmp_path state directory; the module resolves lock and temp paths under the in-root state dir. | PASS. |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | No dispatch-path code was added or modified; cross_harness_bridge_trigger.py and single_harness_bridge_dispatcher.py are absent from target_paths and unmodified. | PASS - by inspection. |
| Atomic write / temp-file hygiene | T8 a raising mutate leaves the index unchanged; T10 no sibling temp file remains. | PASS - T8, T10. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This report carries the mapping plus the executed pytest command and observed results below. | PASS. |

## Verification Commands And Observed Results

1. `python -m pytest platform_tests/scripts/test_bridge_index_writer.py -q`
   Result: 12 passed in 2.34s. All of T1-T12 pass, including T4 (20-thread concurrent no-lost-update), T9 (serialized observation order), T11 (stale malformed lock reclaimed), and T12 (fresh malformed lock retained).

2. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-3 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-005.md` - see the Applicability Preflight section.

3. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-3 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-005.md` - see the Clause Applicability section.

## Acceptance Criteria

- [x] Loyal Opposition returned GO on the proposal (-002).
- [x] scripts/bridge_index_writer.py exists and exposes atomic_index_update, the index_write_lock context manager, and IndexWriteLockTimeout.
- [x] The INDEX-write lock is mutually exclusive via O_CREAT | O_EXCL; concurrent atomic_index_update calls serialize with no lost update (T4, T9).
- [x] Acquisition is bounded-wait: it retries until the lock is won or timeout_seconds elapses, then raises IndexWriteLockTimeout (T2).
- [x] A stale valid lock (heartbeat older than DEFAULT_LOCK_TTL_SECONDS = 30) is reclaimed; reclamation is token-guarded (T6, T7).
- [x] A malformed lock file is reclaimed once aged past ttl_seconds (by mtime) and retained while fresh (T11, T12) - the NO-GO -004 P1 fix.
- [x] atomic_index_update writes atomically via temp file + os.replace; a raising mutate leaves the file unchanged (T8); no temp file remains (T10).
- [x] platform_tests/scripts/test_bridge_index_writer.py covers T1-T12, passes, and uses isolated temp roots.
- [x] No existing dispatch code is modified - Slice 3 is purely additive.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Applicability Preflight

The applicability preflight was run against this -005 report via `--content-file` prior to filing the INDEX entry:

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-3 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-005.md`

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:db87e565bb1b402ec8cd2c45642d48c233596ffbd683338fe32c0731b5f66192

All applicable required and advisory cross-cutting specs are cited in this report's Specification Links.

## Clause Applicability

The ADR/DCL clause preflight was run against this -005 report via `--content-file` prior to filing the INDEX entry:

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-3 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-005.md`

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

- R1 (low): a stale-lock handling bug blocks INDEX writes. Mitigation: both the valid-stale path (T6, T7) and the malformed-lock path (T11, T12) are directly tested; DEFAULT_LOCK_TTL_SECONDS = 30 bounds any stuck lock, malformed or not.
- R2 (low): the bounded wait adds latency. Mitigation: the critical section is a sub-millisecond read-modify-write; the T4 suite of 20 concurrent updates completes in ~2 s.
- R3 (low): the new module has no consumer until a later integration slice. Mitigation: this is the GO'd scoping sub-slice boundary; the T1-T12 suite exercises every code path in isolation.
- R4 (low, addressed): cross-platform correctness of the lock primitive. The -003 implementation found and fixed two Windows/concurrency defects; this revision fixes the malformed-lock recovery gap. All are covered by the passing suite.
- R5 (very low): the malformed-lock mtime guard has the same minimal two-syscall reclaim window as the already-VERIFIED Slice 2 / GO'd Slice 3 valid-stale token guard. Mitigation: removal is gated on the file still being malformed at re-confirm and on the file having aged past ttl; the pattern matches the accepted sibling code.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue beyond any runtime lock file, which is itself reclaimable by TTL.

## Loyal Opposition Asks

1. Confirm the malformed-lock fix - distinguishing "file absent" from "file present but malformed" in _acquire, and reclaiming a malformed lock via its mtime once aged past ttl_seconds - resolves the -004 P1 finding.
2. Confirm T11 and T12 are adequate regression coverage for stale malformed-lock reclamation and fresh malformed-lock retention.
3. Confirm the fix is a correctness fix within the GO-approved design and target_paths, not a scope change.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
