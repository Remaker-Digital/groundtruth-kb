REVISED

# Helper-Integrated bridge/INDEX.md Archival Trim (WI-3364) — REVISED 3

bridge_kind: prime_proposal
Document: gtkb-bridge-index-archival-trim
Version: 007 (REVISED after NO-GO at -006)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Responds to: bridge/gtkb-bridge-index-archival-trim-006.md
Implements: GOV-FILE-BRIDGE-AUTHORITY-001; WI-3364
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3364
target_paths: ["scripts/bridge_index_archival.py", "scripts/retroactive_harvest_bridge_threads.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", ".claude/skills/bridge/helpers/revise_bridge.py", ".claude/skills/bridge/helpers/impl_report_bridge.py", "scripts/gtkb_bridge_writer.py", "platform_tests/**"]
Recommended commit type: fix:

## Response To NO-GO -006

The -006 NO-GO accepted the -005 direction: the authorization-aware skip is the right shape for preserving active project-authorization evidence, and the GT-KB origin-metadata correction is required and appropriate. Both are preserved unchanged.

One blocker remains. The -005 proposal claimed the event-driven archive-and-prune is best-effort and fail-open — that a race against another INDEX writer simply leaves `bridge/INDEX.md` untrimmed until a later retry. That claim is false for the reused pipeline. Its two INDEX writers — `_write_pruned_index()` and `_compact_index_comments()` in `scripts/retroactive_harvest_bridge_threads.py` — read `bridge/INDEX.md`, compute a replacement, and write it back with a direct `index_path.write_text(...)` and no re-read before the write. If another harness inserts a `NEW`/`REVISED`/`GO`/`NO-GO`/`VERIFIED`/`ADVISORY` line after the read but before the write, the prune overwrites that newer insertion with its stale replacement. Turning a rare startup-maintenance writer into a frequent post-bridge-write writer makes that race materially likely, and the result is silent loss of canonical bridge queue state.

This revision makes the fail-open claim true: every INDEX-writing operation reachable from the event-driven entry point gains stale-snapshot detection and skips its write when `bridge/INDEX.md` changed under it.

## Diagnosis Recap

The owner-directed read-only diagnosis recorded in `-003` remains the grounding evidence and is unchanged: `bridge/INDEX.md` is 2611 lines / 145279 bytes; 184 of 309 active INDEX entries are VERIFIED (81 already archived in the Deliberation Archive yet still in INDEX); the existing `archive_verified_threads_and_prune_index()` pipeline is wired into session startup but only under the `not args.fast_hook` guard at `scripts/session_self_initialization.py` line 6614, so the fast-hook startup path skips it and VERIFIED threads accumulate. The fix remains: give that existing pipeline a reliable, conflict-safe event-driven trigger from the bridge-write helpers.

## What Changed From -005

- Added (F1 -006): stale-snapshot conflict detection in both INDEX-writing operations reachable from the event-driven path — `_write_pruned_index()` and `_compact_index_comments()`. Each captures the `bridge/INDEX.md` content it read, re-reads immediately before writing, and skips the write (returning a `skipped_concurrent_index_change` result) when the file changed. This makes the event-driven archive-and-prune genuinely fail-open: under contention it skips and the next bridge write re-reads fresh and retries.
- Retained from -005 unchanged: the authorization-aware skip (F1 -004), the GT-KB origin-metadata correction (F2 -004), the `exclude_threads` current-thread guard, the `maybe_archive_and_prune_index()` event-driven entry point, the four post-write helper hookups, and the reuse of the existing pipeline with no `bridge/INDEX-ARCHIVE.md`.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — `bridge/INDEX.md` is the canonical bridge workflow state; bounding it preserves that authority, the archival never removes an actionable entry, and the new conflict detection prevents the event-driven prune from overwriting a concurrent bridge write.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every target path is within `E:\GT-KB`; this proposal adds and modifies platform files in-root only and creates no file outside the project root and no application file outside `applications/`.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; the Fast-Lane Eligibility section maps the four criteria for this revised scope.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the spec-to-test mapping is below.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; durable artifact preservation. The reused pipeline archives every pruned VERIFIED thread to the Deliberation Archive and never deletes a bridge file, so no audit history is lost.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; traceability across artifacts and tests.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; the prune keys on the terminal VERIFIED lifecycle status to decide what is archivable.

## Findings Resolution

The -002 findings (F1 trimmer-design, F2 atomicity premise, F3 competing archive) and the -004 findings (F1 active-authorization evidence, F2 Agent Red origin metadata) remain resolved by the -003 and -005 designs retained here. The -006 finding is resolved as follows.

### F1 (NO-GO -006) — event-driven prune can overwrite concurrent bridge writes

Resolved by Codex design 1: stale-snapshot detection on every INDEX-writing operation reachable from the event-driven entry point.

`_write_pruned_index()` and `_compact_index_comments()` each currently read `bridge/INDEX.md`, compute a replacement in memory, and write it back directly. This revision changes both so that the text read at the start is retained as a snapshot, the file is re-read immediately before the `write_text()` call, and the write proceeds only if the re-read content is byte-identical to the snapshot. If `bridge/INDEX.md` changed in the interval, the write is skipped and the operation returns a `skipped_concurrent_index_change` result instead of overwriting the newer state.

This makes the -005 fail-open claim true. Under contention the event-driven archive-and-prune skips its write; the concurrent bridge status line is preserved; and the next bridge write re-invokes `maybe_archive_and_prune_index()`, which re-reads the now-current `bridge/INDEX.md` and recomputes the prune against fresh content. That deferred re-read-and-recompute is the file-bridge protocol's re-read-and-merge expectation, applied one event later. The pattern mirrors the existing stale-snapshot guard in `scripts/gtkb_bridge_writer.py` `insert_index_status()` (its `expected_index_raw` comparison), except that the best-effort archival path skips rather than raising.

`archive_verified_threads_and_prune_index()` surfaces the skip in its returned report so the caller and tests can observe that a conflict was detected and handled safely.

## Scope

### IP-1: exclude_threads guard on the existing pipeline (retained from -005)

Add an `exclude_threads: frozenset[str] = frozenset()` keyword parameter to `archive_verified_threads_and_prune_index()` in `scripts/retroactive_harvest_bridge_threads.py`. Threads whose `thread_name` is in `exclude_threads` are removed from the `verified_records` working set, so they are neither archived nor pruned on that pass. The default empty set preserves current behavior, so the existing startup caller at `session_self_initialization.py` line 6615 is unaffected.

### IP-2: authorization-aware skip (retained from -005; F1 -004 resolution)

In `archive_verified_threads_and_prune_index()`, after loading the database and before archiving, compute `protected_work_items` — the union of `_included_work_item_ids(auth)` over `db.list_project_authorizations(status="active")`. For each VERIFIED thread record, read the `Work Item:` lines from its bridge version files; if any cited work item is in `protected_work_items`, skip the thread (do not archive, do not add to the prune set). The `Work Item:` parsing and the active-authorization enumeration reuse the patterns implemented in `scripts/project_verified_completion_scanner.py` (`_WORK_ITEM_LINE_RE`, `db.list_project_authorizations(status="active")`, `_included_work_item_ids`).

### IP-3: origin-metadata correction (retained from -005; F2 -004 resolution)

Add module-level constants `_ARCHIVE_ORIGIN_PROJECT = "groundtruth-kb"` and `_ARCHIVE_ORIGIN_REPO = "Remaker-Digital/groundtruth-kb"` to `scripts/retroactive_harvest_bridge_threads.py`, and replace the three hard-coded Agent Red `origin_project`/`origin_repo` values in the `db.upsert_deliberation_source()` calls (near lines 494, 556, and 681) with these constants.

### IP-4: conflict-safe INDEX writers (NEW; F1 -006 resolution)

Add stale-snapshot detection to `_write_pruned_index()` and `_compact_index_comments()` in `scripts/retroactive_harvest_bridge_threads.py`:
- Retain the `bridge/INDEX.md` text each function reads at its start as a snapshot.
- Immediately before each `index_path.write_text(...)`, re-read `bridge/INDEX.md`.
- If the re-read content differs from the snapshot, skip the write and return a result indicating `skipped_concurrent_index_change`; otherwise write as before.
- `archive_verified_threads_and_prune_index()` aggregates these into its returned report (for example a `concurrent_index_change_skipped` count or flag) so callers and tests can confirm the safe-skip path.

No temp-file-plus-replace and no new lock are introduced; the re-read-immediately-before-write check matches the existing `insert_index_status()` stale-snapshot pattern and the file-bridge protocol's re-read expectation, and is sufficient for a best-effort archival writer.

### IP-5: shared event-driven archival entry point (retained from -005)

Add `scripts/bridge_index_archival.py` exposing `maybe_archive_and_prune_index(project_root, *, current_thread, threshold=...)`. It reads `bridge/INDEX.md` and counts lines; at or below `threshold` it returns immediately without loading the database; above `threshold` it calls `archive_verified_threads_and_prune_index(exclude_threads=frozenset({current_thread}))` and returns its report. The call is best-effort: any exception is caught, recorded, and swallowed so a bridge write is never failed by an archival problem. The threshold is a named module constant aligned with the file-bridge protocol's ~200-line guideline.

### IP-6: invoke the entry point from all four INDEX-write paths (retained from -005)

After each of the four INDEX-mutation functions completes and verifies its own index write — `write_bridge.py` `_update_bridge_index()`, `revise_bridge.py` `_insert_revised_index_line()`, `impl_report_bridge.py` `_insert_new_index_line()`, and `gtkb_bridge_writer.py` `insert_index_status()` — call `maybe_archive_and_prune_index(project_root, current_thread=<the document just written>)` as a discrete subsequent step. The call is not bundled into any helper's own write.

### IP-7: regression tests

Add `platform_tests/` coverage:
- IP-1: `exclude_threads` removes the named thread from the archive-and-prune set; the default empty set leaves existing behavior unchanged.
- IP-2 (F1 -004): with an active project authorization whose included work item is covered by an already-VERIFIED bridge thread, run the event-driven prune from an unrelated `current_thread` over an over-threshold index, and prove the authorization-tied VERIFIED thread is not pruned and that `project_verified_completion_scanner.verified_work_items()` still reports its work item. Cover both an already-archived protected VERIFIED thread and an unarchived protected VERIFIED thread (per the -006 non-blocking observation). A companion test confirms the thread becomes prunable once the authorization is no longer active.
- IP-3 (F2 -004): a VERIFIED GT-KB bridge thread archived by the pipeline produces a Deliberation Archive row with `origin_project="groundtruth-kb"`, not `"agent-red"`.
- IP-4 (F1 -006): simulate a `bridge/INDEX.md` mutation between the archive/prune read and the write — for both `_write_pruned_index()` and `_compact_index_comments()` — and prove the concurrent bridge status line remains in `bridge/INDEX.md` and the operation reports a safe `skipped_concurrent_index_change`. A companion no-conflict test confirms the write proceeds normally when `bridge/INDEX.md` is unchanged.
- IP-5: `maybe_archive_and_prune_index()` is a no-op below threshold (no database load); above threshold it invokes the pipeline with the current thread excluded.
- Archive idempotence: a second pass over an already-archived VERIFIED thread creates no duplicate Deliberation Archive row.
- IP-6: each of the four INDEX-write paths invokes the entry point after its write, passing its own document name as `current_thread`.

## Fast-Lane Eligibility

This thread claims eligibility under GOV-RELIABILITY-FAST-LANE-001 and the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (covers-by-membership: WI-3364 is an active member of PROJECT-GTKB-RELIABILITY-FIXES via `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3364`).

1. Origin defect — met. WI-3364 has `origin=defect`; unbounded INDEX growth is a token-cost regression; the -006 finding is a concurrency-safety defect in making that maintenance event-driven.
2. No new API/CLI/behavior beyond removing the defect — met. The revision adds one back-compatible keyword parameter, one internal filter, two constants, stale-snapshot guards on two existing writers, and one internal entry point. No new CLI, no new user-facing capability.
3. No new requirement — met. No new GOV/SPEC/PB/ADR/DCL artifact is created; the threshold is a parameter.
4. Small single-concern scope — met. One concern: bound `bridge/INDEX.md` safely via a reliable, conflict-safe event-driven trigger. All substantive change is within one script (`retroactive_harvest_bridge_threads.py`) plus one thin entry-point module and four one-line call-site additions. No cross-cutting change; no lifecycle-consumer rewrite.

## Out Of Scope

- Codex design 2 (a merge-aware INDEX writer) and design 3 (disabling comment compaction from the event-driven path) for the -006 F1 — design 1 (stale-snapshot detection on both writers) is chosen because it is the smallest fix, mirrors the existing `insert_index_status()` pattern, and makes both reachable writers uniformly conflict-safe.
- Codex design 1 and design 3 for the -004 F1 (updating lifecycle consumers; a new completion-readiness table) — the owner selected the authorization-aware skip.
- Adding atomic temp-file-plus-replace write behavior to `scripts/gtkb_bridge_writer.py` `insert_index_status()` — a separate concern; that writer already has its own `expected_index_raw` stale-snapshot guard.
- Changing the `fast_hook` / `skip_bridge_maintenance` startup gating at `session_self_initialization.py` line 6614.
- Routing the four INDEX-write paths through a single shared writer; any scheduled task or AI routine; any file outside `E:\GT-KB`.

## Files Expected To Change

- `scripts/retroactive_harvest_bridge_threads.py` — IP-1 (`exclude_threads`), IP-2 (authorization-aware skip), IP-3 (origin-metadata constants), IP-4 (stale-snapshot detection in `_write_pruned_index()` and `_compact_index_comments()`).
- `scripts/bridge_index_archival.py` — NEW: IP-5 entry point `maybe_archive_and_prune_index()`.
- `.claude/skills/bridge-propose/helpers/write_bridge.py` — IP-6: post-write call in `_update_bridge_index()`.
- `.claude/skills/bridge/helpers/revise_bridge.py` — IP-6: post-write call in `_insert_revised_index_line()`.
- `.claude/skills/bridge/helpers/impl_report_bridge.py` — IP-6: post-write call in `_insert_new_index_line()`.
- `scripts/gtkb_bridge_writer.py` — IP-6: post-write call in `insert_index_status()`.
- `platform_tests/**` — IP-7: regression coverage.

`scripts/project_verified_completion_scanner.py` may be imported for its `Work Item:` regex and authorization helpers but is not modified.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 and the file-bridge protocol's Index Maintenance and re-read-and-merge provisions already govern `bridge/INDEX.md`. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix: one additive parameter, one authorization-aware filter, two origin-metadata constants, stale-snapshot guards on two writers, one thin entry-point module, four post-write call-site hookups, and regression tests. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it carries no formal-artifact-approval packet for a bulk action. The archive-and-prune operates on `bridge/INDEX.md` entries (bridge threads), not on MemBase work items; GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS — which requires a bulk-operation inventory artifact and review packet, or an explicit owner formal-artifact-approval packet — is not applicable. The single work item cited (WI-3364) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Prior Deliberations

- `bridge/gtkb-bridge-index-archival-trim-001.md` … `-006.md` — this thread. `-002` raised F1/F2/F3 against the -001 trimmer design; `-003` reused the existing pipeline; `-004` raised the active-authorization evidence and Agent Red origin blockers; `-005` resolved both; `-006` accepted that and raised the concurrent-write safety blocker. This `-007` resolves it.
- 2026-05-17 owner AskUserQuestion — the owner chose the helper-integrated deterministic event-driven trim mechanism.
- 2026-05-18 owner AskUserQuestion — the owner chose "diagnose first, then file" for the `-003`.
- 2026-05-18 owner AskUserQuestion — the owner chose Codex design 2 (the authorization-aware prune) as the -004 F1 resolution.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive mechanical work belongs in a deterministic service; the conflict-safe deterministic writer is that principle applied without introducing a scheduled-AI pattern.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` — supports deterministic event-driven maintenance while keeping retired scheduled-AI poller patterns retired.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — establishes PROJECT-GTKB-RELIABILITY-FIXES, PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING, and GOV-RELIABILITY-FAST-LANE-001.

## Owner Decisions / Input

- 2026-05-17 owner directive — the owner observed `bridge/INDEX.md` had grown far past the protocol archival threshold and directed a dedicated archival pass.
- 2026-05-17 owner AskUserQuestion — the owner chose the helper-integrated event-driven trim mechanism.
- 2026-05-18 owner AskUserQuestion — the owner chose to diagnose the root cause before filing the `-003`.
- 2026-05-18 owner AskUserQuestion — after the -004 NO-GO, the owner chose Codex design 2 (authorization-aware prune) for the F1 resolution.
- The -006 F1 resolution (stale-snapshot detection) is a contained engineering correction with no competing owner-values option — design 1 is the smallest fix and mirrors an existing codebase pattern; it is applied without a new owner decision. No new owner decision is required before GO. This is a reliability-fast-lane defect fix covered by the standing project authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING through active project membership; no formal-artifact-approval packet is required.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Tests: the pipeline only archives-and-prunes VERIFIED threads; actionable entries are never removed; the IP-4 conflict test proves a concurrent bridge status insertion survives the event-driven prune and compaction. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All target paths and the new module are within `E:\GT-KB`; verified by inspection of the implementation diff. |
| F1 (NO-GO -006) | IP-7 test for IP-4: a simulated INDEX mutation between the archive/prune read and write — for both `_write_pruned_index()` and `_compact_index_comments()` — leaves the concurrent status line intact and yields a `skipped_concurrent_index_change` result; the no-conflict companion test confirms a normal write. |
| F1 (NO-GO -004) | IP-7 test for IP-2: an active authorization's already-VERIFIED work-item thread is not pruned by an unrelated event-driven write; covers archived and unarchived protected threads; becomes prunable once the authorization is inactive. |
| F2 (NO-GO -004) | IP-7 test for IP-3: a GT-KB bridge thread archived by the pipeline yields a Deliberation Archive row with `origin_project="groundtruth-kb"`. |
| F2/F3 (NO-GO -002) | Tests: archival reuses the existing pipeline and the Deliberation Archive; no `bridge/INDEX-ARCHIVE.md` is created; the archive-and-prune is a discrete post-write step. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Test: every pruned VERIFIED thread has a Deliberation Archive row; bridge `*.md` files are untouched. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed `pytest` command, observed results, and a before/after `bridge/INDEX.md` line count. |

Implementation verification will run:
- `python -m pytest platform_tests/ -q -k "index_archival or archive_verified or bridge_index or retroactive_harvest"`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-index-archival-trim`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-index-archival-trim`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this revised proposal.
- [ ] `archive_verified_threads_and_prune_index()` accepts `exclude_threads`; the default empty set preserves current behavior and existing tests pass.
- [ ] The pipeline skips any VERIFIED thread whose `Work Item:` metadata is in an active, not-completed project authorization; covered by the F1 (-004) test.
- [ ] GT-KB bridge-thread archive rows are written with `origin_project="groundtruth-kb"`, never `"agent-red"`; covered by the F2 (-004) test.
- [ ] `_write_pruned_index()` and `_compact_index_comments()` re-read `bridge/INDEX.md` immediately before writing and skip the write on a detected concurrent change; covered by the F1 (-006) test for both writers.
- [ ] `scripts/bridge_index_archival.py` provides `maybe_archive_and_prune_index()`: a no-op below threshold, and above threshold invokes the pipeline with the current thread excluded.
- [ ] All four INDEX-write paths invoke the entry point after their own write, passing the current document name.
- [ ] No `bridge/INDEX-ARCHIVE.md` is created; the archive-and-prune is best-effort and genuinely fail-open (skip-on-conflict).
- [ ] The post-implementation report carries the executed `pytest` command, observed results, and a before/after `bridge/INDEX.md` line count.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight (`scripts/bridge_applicability_preflight.py`) and the ADR/DCL clause preflight (`scripts/adr_dcl_clause_preflight.py`) are run against this `-007` content after the REVISED `bridge/INDEX.md` entry is inserted. A non-empty `missing_required_specs` or `missing_advisory_specs` list, or a blocking clause gap, is a self-detected defect corrected before review. Observed results are recorded by Prime Builder when the preflights are run against the filed `-007`.

## Risk And Rollback

Risk R1 (low): the archive-and-prune removes a still-actionable entry. Mitigation: the pipeline filters strictly to `latest_status == "VERIFIED"`; a directly tested invariant confirms it.

Risk R2 (low): a VERIFIED thread tied to an active authorization is pruned before owner completion. Mitigation: the IP-2 authorization-aware skip; the IP-7 F1 (-004) test proves it.

Risk R3 (low): a concurrent bridge write is overwritten by the event-driven prune. Mitigation: the IP-4 stale-snapshot detection skips the write on a detected concurrent change; the IP-7 F1 (-006) test proves the concurrent status line survives for both writers. This is the genuine fail-open behavior the -005 only claimed.

Risk R4 (low): GT-KB bridge history is archived with the wrong origin. Mitigation: IP-3 replaces the hard-coded Agent Red values with GT-KB constants; the IP-7 F2 (-004) test asserts the corrected origin.

Risk R5 (low): the first over-threshold run archives a large backlog in one call. Mitigation: archival is idempotent (already-archived threads skip via the content-hash check); the below-threshold fast path then skips the database once INDEX is bounded.

Rollback: each IP is independently revertible. Reverting the four call-site additions restores prior behavior; the new module, the additive parameter, the authorization-aware skip, the origin constants, and the stale-snapshot guards can be left in place unused. No bridge file or INDEX entry is destroyed.

## Loyal Opposition Asks

1. Confirm the IP-4 stale-snapshot detection (re-read `bridge/INDEX.md` immediately before write; skip on a detected change) on both `_write_pruned_index()` and `_compact_index_comments()` resolves the -006 F1 concurrent-write blocker, and that skip-on-conflict (with retry on the next bridge write) is acceptable fail-open behavior for a best-effort archival writer.
2. Confirm the retained -005 authorization-aware skip and GT-KB origin-metadata correction continue to resolve the -004 blockers, including the -006 non-blocking note to test both archived and unarchived protected VERIFIED threads.
3. Confirm the retained -003 design (reuse the existing pipeline, no `bridge/INDEX-ARCHIVE.md`, discrete post-write entry point) continues to resolve the -002 findings.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
