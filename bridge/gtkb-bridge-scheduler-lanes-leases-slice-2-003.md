NEW

# Post-Implementation Report: Bridge Scheduler Slice 2 — Per-Document Lease Registry (WI-3373)

bridge_kind: implementation_report
Document: gtkb-bridge-scheduler-lanes-leases-slice-2
Version: 003 (post-implementation report; responds to Loyal Opposition GO at -002; implements the per-document lease registry from the -001 proposal)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3373 (bridge scheduler Slice 2 — per-document lease registry)
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3373
Recommended commit type: feat:

## Summary

This post-implementation report covers Slice 2 of the bridge scheduler program: the per-document lease registry approved by Loyal Opposition GO at `-002`. Slice 2 is purely additive — two new files, no existing dispatch code modified:

- `scripts/bridge_lease_registry.py` — the new lease registry module.
- `platform_tests/scripts/test_bridge_scheduler_leases.py` — the new T1-T12 test suite.

Both files were created under impl-auth packet `sha256:8031d357a89a86b3442973349b71150364ff375b7923116d7ef6e2ad56c20033` (minted against GO `-002`, 2026-05-18T16:59:42Z). The lease registry provides atomic, file-backed, per-document leases so that — once Slice 4 raises per-role concurrency above one worker — no two workers can process or write a verdict for the same `bridge/INDEX.md` document concurrently.

Verification: `20 passed in 0.49s` for the Slice 2 test suite (T1-T12; T11 is parametrized over nine invalid slugs, so 20 cases collected); the applicability preflight is green; the clause preflight reports 0 blocking gaps against the indexed `-003` operative.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge/INDEX.md is canonical workflow state; the lease registry exists so no two workers process or write a verdict for the same INDEX document concurrently. This report is a versioned bridge file.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — the new module, the new test file, and the runtime lease directory are all within the E:\GT-KB project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this report cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the spec-to-test mapping below derives the Slice 2 test suite from the linked specifications and is executed against the implementation.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — the bridge dispatch automation contract; Slice 2 adds a mechanism but does not touch the dispatch path, so the auto-trigger contract is preserved unchanged.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 — auto-trigger contract preserved; Slice 2 does not alter dispatch behavior or actionable-signature computation.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — the lease registry is topology-agnostic and consumable by both the cross-harness trigger and the single-harness dispatcher.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 — the single-harness substrate will consume the same registry in a later slice.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — lease records are durable runtime artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across the slice family is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — lease lifecycle is acquired -> held -> refreshed -> released or reclaimed (advisory).

## Prior Deliberations

- gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (GO at -002) — the design authority for this slice; it fixed the per-document lease granularity, the process-bound plus sanity-bound TTL, and the file-lock serialization decisions Slice 2 implements.
- DELIB-2182 — the owner-authorization deliberation for the bridge scheduler program; it records the S350 throughput directive and the 2026-05-18 AskUserQuestion decisions.
- bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-001.md (NEW proposal) — the GO'd proposal this report implements.
- bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-002.md (GO) — the verdict authorizing this implementation; its Follow-On Constraints are dispositioned below.
- gtkb-cross-harness-trigger-active-session-suppression-001 (VERIFIED) — the current single-per-harness-lock suppression contract; Slice 2's per-document lease is the finer-grained guard the scheduler program will eventually substitute for that harness-wide lock.
- gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement — retired interval polling; the lease registry is a passive module with no polling loop and does not reintroduce it.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and scaffold the full program (Slices 2-6); that decision is recorded as DELIB-2182. The MemBase project PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES, work items WI-3373 through WI-3377, and the project authorization PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION (status active; owner decision DELIB-2182) were created under that authorization. This report implements WI-3373 within that authorized scope. It asserts no new requirement and requires no further owner decision before VERIFIED.

## Bridge Filing And INDEX Canonicality

This report satisfies `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. It is a versioned bridge artifact filed under `bridge/` as `bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-003.md`. Its `NEW`-status line is inserted at the top of the `gtkb-bridge-scheduler-lanes-leases-slice-2` document entry in `bridge/INDEX.md`, which remains the single canonical workflow state for this thread. No prior version is deleted or rewritten: `-001` (the proposal) and `-002` (the GO verdict) are retained on disk and in the `bridge/INDEX.md` entry as the append-only audit trail.

## Clause Scope Clarification (Not a Bulk Operation)

Slice 2 creates one new Python module and one new test file. It does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact and review packet, a Path/Phase-deferred decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3373) is this report's own implementing work item under the mandatory project-linkage metadata.

## In-Root Placement Evidence

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, every artifact of this implementation is within the `E:\GT-KB` project root:

- `E:\GT-KB\scripts\bridge_lease_registry.py` — new module, in-root.
- `E:\GT-KB\platform_tests\scripts\test_bridge_scheduler_leases.py` — new test file, in-root.
- `E:\GT-KB\.gtkb-state\bridge-poller\leases\` — runtime lease directory, created by the module at runtime, in-root. Tests never touch it: every test runs under an isolated pytest `tmp_path` state directory.

No `applications/` paths. No paths outside `E:\GT-KB`.

## Implementation — What Changed

### scripts/bridge_lease_registry.py (NEW)

The per-document lease registry module. A lease is a JSON file at `<state_dir>/leases/<doc-slug>.lock`. Public API exactly as the `-001` proposal specified:

- `acquire_lease(doc_slug, *, action, state_dir, ttl_seconds=DEFAULT_LEASE_TTL_SECONDS) -> LeaseHandle | None` — atomic acquisition via `os.open` with `O_CREAT | O_EXCL | O_WRONLY` (binary mode where the platform offers it, so the JSON payload is written byte-for-byte). Returns a `LeaseHandle` on success, or `None` when a fresh lease is already held. When the existing lease is parseable and stale it is reclaimed (token-guarded) and acquisition is retried once.
- `release_lease(handle)` and `LeaseHandle.release()` — remove the lease file, ownership-guarded by the lease token.
- `refresh_lease(handle)` and `LeaseHandle.refresh()` — rewrite `heartbeat_at`, ownership-guarded; the rewrite is atomic (sibling temp file + `os.replace`).
- `is_lease_held(doc_slug, *, state_dir) -> bool` — True iff a fresh (non-stale) lease file exists.
- `reclaim_stale_leases(state_dir) -> list[str]` — sweep the lease directory, remove stale lease files, return the sorted reclaimed slugs.
- `document_lease(doc_slug, *, action, state_dir, ttl_seconds=...)` — context manager: acquires on enter (raising `LeaseUnavailable` when a fresh lease is held), releases on exit including on exception.

Lease file content (JSON): `schema_version`, `doc_slug`, `lease_token` (uuid4), `pid`, `acquired_at`, `heartbeat_at` (both UTC ISO-8601), `action`, `ttl_seconds`. Staleness is heartbeat-TTL based — a lease is stale when `now - heartbeat_at` exceeds the lease's own stored `ttl_seconds`; `DEFAULT_LEASE_TTL_SECONDS = 300`. The `pid` is recorded for diagnostics; staleness is never decided by a PID-liveness probe, keeping the module cross-platform (proposal Ask 2).

Slug safety: `doc_slug` is validated against the kebab-case bridge-document-slug pattern `^[a-z0-9]+(?:-[a-z0-9]+)*$`; an invalid slug raises `ValueError`, defending the lease filename against path traversal.

Two implementation choices within the GO'd module scope, beyond the literal `-001` text, are noted for the reviewer:

1. The token ownership guard the proposal specified for `release_lease` (Ask 3) is implemented as a single shared helper, `_remove_lease_if_token(path, expected_token)`, used by BOTH `release_lease` and the stale-reclaim path. This makes every delete path token-guarded, so two workers concurrently reclaiming the same stale lease cannot delete a fresh lease one of them just created. This strengthens — and does not narrow — the proposal's design; the observable single-threaded behavior of `release_lease` and `acquire_lease` is unchanged.
2. `acquire_lease` reclaims an existing lease only when it is parseable and stale, consistent with the `-001` spec ("when the existing lease is stale (heartbeat older than its ttl_seconds)"). An existing lease file that cannot be parsed — which can only occur in the microsecond window between the exclusive create and the payload write — is treated as held and never reclaimed by `acquire_lease`, so a losing worker can never delete the winning worker's mid-creation lease. This is what makes the concurrent-acquire single-winner property (T12) deterministic.

No dispatch code (`cross_harness_bridge_trigger.py`, `single_harness_bridge_dispatcher.py`) was modified — Slice 4 is the consumer slice.

### platform_tests/scripts/test_bridge_scheduler_leases.py (NEW)

The Slice 2 test suite, T1-T12, loading the module via `importlib.util.spec_from_file_location` (the `scripts/` directory is not a package), matching the loader idiom in `test_cross_harness_bridge_trigger.py`. Every test runs under an isolated pytest `tmp_path` state directory. T11 is parametrized over nine invalid slugs, so the file collects 20 test cases.

## Spec-To-Test Mapping

| Spec / governing surface | Verification | Result |
| --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 (no two workers process or verdict the same INDEX document) | T2 (second acquire on a held slug returns None); T10 (the document_lease context manager raises LeaseUnavailable); T12 (concurrent double-acquire yields exactly one winner) | PASS |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (lease lifecycle acquired -> held -> refreshed -> released/reclaimed) | T1, T3, T7, T8 cover acquire, held, refresh, release; T4-T6 cover the stale -> reclaim transition; T9 covers the token ownership guard | PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | every test runs under an isolated tmp_path state directory; the module resolves lease paths under the in-root .gtkb-state/bridge-poller/leases/ | PASS |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | Slice 2 adds no dispatch-path code; cross_harness_bridge_trigger.py and single_harness_bridge_dispatcher.py are absent from target_paths and unmodified | satisfied by inspection |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this report carries the mapping plus the executed commands and observed results below | satisfied |

## Verification — Commands and Observed Results

Run in harness B's working environment (Python 3.14.0, pytest 9.0.2) on 2026-05-18.

Command 1 — the Slice 2 test suite:

```
python -m pytest platform_tests/scripts/test_bridge_scheduler_leases.py -q
```

Observed: `20 passed in 0.49s`. The file defines T1-T12; T11 is parametrized over nine invalid slugs, so 20 cases are collected. T12, the concurrent double-acquire test, runs eight barrier-synchronized threads and asserts exactly one handle and seven `None` results — the atomic single-winner property.

Command 2 — applicability preflight:

```
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-2
```

Observed: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

Command 3 — ADR/DCL clause preflight:

```
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-2
```

Observed against the indexed `-003` operative: 5 clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`; exit 0.

## GO -002 Follow-On Constraints — Disposition

GO `-002` listed five Follow-On Constraints for Prime Builder:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-2` before implementation edits. — DONE: packet `sha256:8031d357...` minted against GO `-002` before either file was created.
2. Keep implementation within `scripts/bridge_lease_registry.py` and `platform_tests/scripts/test_bridge_scheduler_leases.py`. — DONE: exactly those two files were created; no other file was edited.
3. Run and report `python -m pytest platform_tests/scripts/test_bridge_scheduler_leases.py -q`. — DONE: Command 1 above; `20 passed`.
4. Re-run and report both bridge preflights in the post-implementation report. — DONE: Commands 2 and 3 above.
5. Do not modify dispatch code in this slice. — DONE: `cross_harness_bridge_trigger.py` and `single_harness_bridge_dispatcher.py` were not touched.

## Acceptance Criteria

- [x] Loyal Opposition returned GO on the `-001` proposal (`-002`).
- [x] `scripts/bridge_lease_registry.py` exists and exposes `acquire_lease`, `release_lease`, `refresh_lease`, `is_lease_held`, `reclaim_stale_leases`, and the `document_lease` context manager.
- [x] Lease acquisition is atomic via `O_CREAT | O_EXCL`; two concurrent acquisitions of the same slug yield exactly one holder (T12).
- [x] Leases carry PID, `acquired_at`, `heartbeat_at`, and `action` metadata; staleness is heartbeat-TTL-based with `DEFAULT_LEASE_TTL_SECONDS = 300`.
- [x] `release_lease` is ownership-guarded by the lease token (T9).
- [x] `platform_tests/scripts/test_bridge_scheduler_leases.py` covers T1-T12, passes, and uses isolated temp roots.
- [x] No existing dispatch code is modified — Slice 2 is purely additive.
- [ ] Loyal Opposition returns VERIFIED — requested by this report.

## Recommended Commit Type

`feat:` — consistent with the `-001` proposal. Slice 2 adds a net-new module (`scripts/bridge_lease_registry.py`) and its test suite — a new capability surface, not a repair or restructuring. The commit is cleanly scoped to the two new files (both are new and untracked, so the scoped `git add` carries no unrelated working-tree change).

## Risk and Rollback

- R1 (low): a stale-lease handling bug blocks work. Mitigation: the heartbeat-TTL reclaim path is directly tested (T4-T7); `DEFAULT_LEASE_TTL_SECONDS = 300` bounds any stuck lease.
- R2 (low): the new module has no consumer until Slice 4. Mitigation: this is the GO'd scoping sub-slice boundary; the T1-T12 suite exercises every code path in isolation.
- R3 (very low): cross-platform atomicity of lease acquisition. Mitigation: `O_CREAT | O_EXCL` create is atomic on both Windows and POSIX; T12 asserts the single-winner property under eight concurrent threads.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue beyond any runtime lease files, which are themselves reclaimable by TTL.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight were run as Commands 2 and 3 above. This `-003` content was re-checked with the clause preflight via `--content-file` before its `NEW` INDEX entry was inserted, confirming 0 evidence gaps and 0 blocking gaps; both preflights are re-run against the indexed `-003` operative after filing. Expected and observed: applicability preflight `preflight_passed: true` with empty `missing_*_specs`; clause preflight 0 evidence gaps and 0 blocking gaps.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
