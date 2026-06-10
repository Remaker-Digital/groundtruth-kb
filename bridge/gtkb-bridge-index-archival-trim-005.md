REVISED

# Helper-Integrated bridge/INDEX.md Archival Trim (WI-3364) — REVISED 2

bridge_kind: prime_proposal
Document: gtkb-bridge-index-archival-trim
Version: 005 (REVISED after NO-GO at -004)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Responds to: bridge/gtkb-bridge-index-archival-trim-004.md
Implements: GOV-FILE-BRIDGE-AUTHORITY-001; WI-3364
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3364
target_paths: ["scripts/bridge_index_archival.py", "scripts/retroactive_harvest_bridge_threads.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", ".claude/skills/bridge/helpers/revise_bridge.py", ".claude/skills/bridge/helpers/impl_report_bridge.py", "scripts/gtkb_bridge_writer.py", "platform_tests/**"]
Recommended commit type: fix:

## Response To NO-GO -004

The -004 NO-GO accepted the -003 direction (drop `bridge/INDEX-ARCHIVE.md`, reuse the existing Deliberation Archive backed pipeline) and raised two new P1 blockers. Both are accepted.

F1 (-004): the `exclude_threads` guard protects only the thread being written. It does not protect an already-VERIFIED thread whose work item an active, not-yet-completed project authorization still depends on. If an unrelated bridge write triggers the prune and removes such a thread's INDEX block, `complete_project_authorization()` — which reads VERIFIED coverage from live INDEX — can fail for an implementation that was genuinely VERIFIED. The -003 attempt to defer this as a follow-on is withdrawn.

F2 (-004): the reused `archive_verified_threads_and_prune_index()` writes Deliberation Archive rows with hard-coded Agent Red origin metadata. Making it the event-driven archive path for GT-KB bridge threads would archive GT-KB bridge history as Agent Red history.

Per the owner AskUserQuestion of 2026-05-18, the F1 resolution is Codex design 2 — an authorization-aware prune. The F2 fix (origin-metadata correction) is bundled into the same revision.

## Diagnosis Recap

The owner-directed read-only diagnosis recorded in `-003` remains the grounding evidence and is unchanged: `bridge/INDEX.md` is 2611 lines / 145279 bytes; 184 of 309 active INDEX entries are VERIFIED (81 already archived in the Deliberation Archive yet still in INDEX); the existing `archive_verified_threads_and_prune_index()` pipeline is wired into session startup but only under the `not args.fast_hook` guard at `scripts/session_self_initialization.py` line 6614, so the fast-hook startup path skips it and VERIFIED threads accumulate. The fix remains: give that existing pipeline a reliable event-driven trigger from the bridge-write helpers.

## What Changed From -003

- Added (F1, Codex design 2): an authorization-aware skip inside `archive_verified_threads_and_prune_index()`. A VERIFIED thread whose `Work Item:` metadata is included in an active, not-completed project authorization is skipped — neither archived nor pruned — so its INDEX block survives until the owner completes the authorization.
- Added (F2): correction of the Deliberation Archive origin metadata in `scripts/retroactive_harvest_bridge_threads.py` from hard-coded Agent Red values to GT-KB values.
- Retained from -003: reuse of the existing pipeline (no `trim_index()`, no `bridge/INDEX-ARCHIVE.md`); the `exclude_threads` current-thread guard; the `maybe_archive_and_prune_index()` event-driven entry point; the four post-write helper hookups; the discrete best-effort post-write framing with no atomicity claim.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — `bridge/INDEX.md` is the canonical bridge workflow state; bounding it preserves that authority, and the archival never removes an actionable entry so the canonical queue is preserved.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every target path is within `E:\GT-KB`; this proposal adds and modifies platform files in-root only and creates no file outside the project root and no application file outside `applications/`.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; the Fast-Lane Eligibility section maps the four criteria for this revised scope.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the spec-to-test mapping is below.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; durable artifact preservation. The reused pipeline archives every pruned VERIFIED thread to the Deliberation Archive and never deletes a bridge file, so no audit history is lost.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; traceability across artifacts and tests.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; the prune keys on the terminal VERIFIED lifecycle status to decide what is archivable.

## Findings Resolution

The -002 findings F1, F2, and F3 remain resolved by the -003 design retained here: F2 (-002) by reusing the existing pipeline as a discrete best-effort post-write step with no atomicity claim; F3 (-002) by dropping `bridge/INDEX-ARCHIVE.md` and using the Deliberation Archive as the sole archive. The two -004 findings are resolved as follows.

### F1 (NO-GO -004) — event-driven pruning can erase VERIFIED evidence before authorization completion

Resolved by Codex design 2: an authorization-aware skip. `archive_verified_threads_and_prune_index()` already filters its working set to threads whose latest status is VERIFIED. This revision adds a second filter: before archiving and pruning, the pipeline computes the set of work items that belong to active, not-completed project authorizations, and skips any VERIFIED thread that cites a protected work item — that thread is neither archived nor pruned on this pass, so its INDEX block remains visible to the live-INDEX completion readers.

The "protected work items" set is computed with the same enumeration `scripts/project_verified_completion_scanner.py` already uses: `db.list_project_authorizations(status="active")` for the active, not-completed authorizations, and `_included_work_item_ids()` for each authorization's work items. Each VERIFIED thread's work items are read from its bridge version files using the same `Work Item:` metadata pattern (`_WORK_ITEM_LINE_RE`). The prune's notion of "an authorization still needs this evidence" is therefore identical to the completion scanner's notion of "what an authorization's work items are."

Once the owner completes a project authorization, it is no longer `status="active"`, its work items leave the protected set, and a later prune pass archives and prunes the now-unprotected threads normally. The `exclude_threads` current-thread guard from -003 is retained as a complementary protection for the just-written thread (which may not yet be tied to any authorization).

### F2 (NO-GO -004) — reused pipeline hard-codes Agent Red origin metadata

Resolved by correcting the origin metadata. `scripts/retroactive_harvest_bridge_threads.py` currently passes `origin_project="agent-red"` and `origin_repo="Remaker-Digital/agent-red-customer-engagement"` to `db.upsert_deliberation_source()` at three sites (the `_compact_index_comments` call near line 494, the `archive_verified_threads_and_prune_index()` call near line 556, and the `run_sweep` call near line 681). This script harvests GT-KB bridge threads, which are GT-KB platform artifacts, not Agent Red artifacts. The three hard-coded values are replaced with two module-level constants set to the GT-KB origin: `origin_project="groundtruth-kb"` and `origin_repo="Remaker-Digital/groundtruth-kb"` (the configured GT-KB repository). This corrects all archival paths in the file, not only the event-driven one, so the first over-threshold run cannot archive the backlog of VERIFIED GT-KB threads with the wrong origin.

## Scope

### IP-1: exclude_threads guard on the existing pipeline

Add an `exclude_threads: frozenset[str] = frozenset()` keyword parameter to `archive_verified_threads_and_prune_index()` in `scripts/retroactive_harvest_bridge_threads.py`. Threads whose `thread_name` is in `exclude_threads` are removed from the `verified_records` working set, so they are neither archived nor pruned on that pass. The default empty set preserves current behavior, so the existing startup caller at `session_self_initialization.py` line 6615 is unaffected.

### IP-2: authorization-aware skip (F1 resolution)

In `archive_verified_threads_and_prune_index()`, after loading the database and before archiving, compute `protected_work_items` — the union of `_included_work_item_ids(auth)` over `db.list_project_authorizations(status="active")`. For each VERIFIED thread record, read the `Work Item:` lines from its bridge version files; if any cited work item is in `protected_work_items`, skip the thread (do not archive, do not add to the prune set). The skipped count is recorded in the returned report. The `Work Item:` parsing and the active-authorization enumeration reuse the patterns already implemented in `scripts/project_verified_completion_scanner.py` (imported or replicated as a small regex; implementation detail). The default behavior when no active authorization exists is unchanged.

### IP-3: origin-metadata correction (F2 resolution)

Add module-level constants `_ARCHIVE_ORIGIN_PROJECT = "groundtruth-kb"` and `_ARCHIVE_ORIGIN_REPO = "Remaker-Digital/groundtruth-kb"` to `scripts/retroactive_harvest_bridge_threads.py`, and replace the three hard-coded `origin_project`/`origin_repo` Agent Red values in the `db.upsert_deliberation_source()` calls with these constants.

### IP-4: shared event-driven archival entry point

Add `scripts/bridge_index_archival.py` exposing `maybe_archive_and_prune_index(project_root, *, current_thread, threshold=...)`. It reads `bridge/INDEX.md` and counts lines; at or below `threshold` it returns immediately without loading the database (the steady-state fast path); above `threshold` it calls `archive_verified_threads_and_prune_index(exclude_threads=frozenset({current_thread}))` and returns its report. The call is best-effort: any exception is caught, recorded, and swallowed so a bridge write is never failed by an archival problem. The threshold is a named module constant aligned with the file-bridge protocol's ~200-line guideline.

### IP-5: invoke the entry point from all four INDEX-write paths

After each of the four INDEX-mutation functions completes and verifies its own index write — `write_bridge.py` `_update_bridge_index()`, `revise_bridge.py` `_insert_revised_index_line()`, `impl_report_bridge.py` `_insert_new_index_line()`, and `gtkb_bridge_writer.py` `insert_index_status()` — call `maybe_archive_and_prune_index(project_root, current_thread=<the document just written>)` as a discrete subsequent step. The call is not bundled into any helper's own write and makes no atomicity claim.

### IP-6: regression tests

Add `platform_tests/` coverage:
- IP-1: `exclude_threads` removes the named thread from the archive-and-prune set; the default empty set leaves existing behavior unchanged.
- IP-2 (the F1 test required by the -004 NO-GO): with an active project authorization whose included work item is covered by an already-VERIFIED bridge thread, run the event-driven prune from an unrelated `current_thread` over an over-threshold index, and prove the authorization-tied VERIFIED thread is not pruned and that `project_verified_completion_scanner.verified_work_items()` still reports its work item. A companion test confirms that once the authorization is no longer active, the same thread becomes prunable.
- IP-3 (F2): a VERIFIED GT-KB bridge thread archived by the pipeline produces a Deliberation Archive row with `origin_project="groundtruth-kb"`, not `"agent-red"`.
- IP-4: `maybe_archive_and_prune_index()` is a no-op below threshold (and does not load the database); above threshold it invokes the pipeline with the current thread excluded.
- Archive idempotence: a second pass over an already-archived VERIFIED thread creates no duplicate Deliberation Archive row.
- IP-5: each of the four INDEX-write paths invokes the entry point after its write, passing its own document name as `current_thread`.

## Fast-Lane Eligibility

This thread claims eligibility under GOV-RELIABILITY-FAST-LANE-001 and the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (covers-by-membership: WI-3364 is an active member of PROJECT-GTKB-RELIABILITY-FIXES via `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3364`, as confirmed in the -004 review).

1. Origin defect — met. WI-3364 has `origin=defect`. Unbounded INDEX growth is a token-cost regression; F2 is a latent classification defect in the reused pipeline.
2. No new API/CLI/behavior beyond removing the defect — met. The revision adds one back-compatible keyword parameter, one internal filter, two constants, and one internal entry point. No new CLI, no new user-facing capability. The archive-and-prune behavior already exists and is already accepted; only its trigger frequency and its origin metadata change, and the authorization-aware skip makes the prune strictly safer.
3. No new requirement — met. No new GOV/SPEC/PB/ADR/DCL artifact is created; the threshold is a parameter.
4. Small single-concern scope — met. One concern: bound `bridge/INDEX.md` safely via a reliable event-driven trigger. All substantive changes are within one script (`retroactive_harvest_bridge_threads.py`) plus one thin entry-point module and four one-line call-site additions. No cross-cutting change; no lifecycle-consumer rewrite (design 2 was chosen precisely to avoid that).

## Out Of Scope

- Codex design 1 (updating `project_verified_completion_scanner.py` and `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` to read VERIFIED coverage from the Deliberation Archive) and design 3 (a new durable completion-readiness table) — the owner selected design 2 at the 2026-05-18 AskUserQuestion.
- Adding atomic temp-file-plus-replace write behavior to `scripts/gtkb_bridge_writer.py` `insert_index_status()` — a separate concern; the archive-and-prune step is best-effort and does not depend on it.
- Changing the `fast_hook` / `skip_bridge_maintenance` startup gating at `session_self_initialization.py` line 6614 — the event-driven trigger remedies the rarely-runs problem without touching the startup token-economy gate.
- Routing the four INDEX-write paths through a single shared writer — a separate larger refactor.
- Any scheduled task, cron job, or AI routine; any file outside `E:\GT-KB`.

## Files Expected To Change

- `scripts/retroactive_harvest_bridge_threads.py` — IP-1 (`exclude_threads` parameter), IP-2 (authorization-aware skip), IP-3 (origin-metadata constants).
- `scripts/bridge_index_archival.py` — NEW: IP-4 entry point `maybe_archive_and_prune_index()`.
- `.claude/skills/bridge-propose/helpers/write_bridge.py` — IP-5: post-write call in `_update_bridge_index()`.
- `.claude/skills/bridge/helpers/revise_bridge.py` — IP-5: post-write call in `_insert_revised_index_line()`.
- `.claude/skills/bridge/helpers/impl_report_bridge.py` — IP-5: post-write call in `_insert_new_index_line()`.
- `scripts/gtkb_bridge_writer.py` — IP-5: post-write call in `insert_index_status()`.
- `platform_tests/**` — IP-6: regression coverage.

`scripts/project_verified_completion_scanner.py` may be imported for its `Work Item:` regex and authorization helpers but is not modified.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 and the file-bridge protocol's Index Maintenance provision already govern `bridge/INDEX.md` and provide for archival. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix: one additive parameter, one authorization-aware filter, two origin-metadata constants, one thin entry-point module, four post-write call-site hookups, and regression tests. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it carries no formal-artifact-approval packet for a bulk action. The archive-and-prune operates on `bridge/INDEX.md` entries (bridge threads), not on MemBase work items; GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS — which requires a bulk-operation inventory artifact and review packet, or an explicit owner formal-artifact-approval packet — is not applicable. The single work item cited (WI-3364) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Prior Deliberations

- `bridge/gtkb-bridge-index-archival-trim-001.md` … `-004.md` — this thread. `-002` raised F1/F2/F3 against the -001 trimmer design; `-003` reused the existing pipeline and addressed them; `-004` accepted that direction but raised two new P1 blockers (event-driven pruning vs active-authorization completion evidence; Agent Red origin metadata). This `-005` resolves both.
- 2026-05-17 owner AskUserQuestion — the owner chose the helper-integrated deterministic event-driven trim mechanism over a recurring AI routine and over a script-plus-OS-task.
- 2026-05-18 owner AskUserQuestion — the owner chose "diagnose first, then file" for the `-003`.
- 2026-05-18 owner AskUserQuestion — presented with the -004 NO-GO findings, the owner chose Codex design 2 (the authorization-aware prune) as the F1 resolution. This proposal implements that choice.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive mechanical work belongs in a deterministic service. The archive-and-prune is mechanical; a deterministic event-driven helper step is that principle applied.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` and the bridge-essential incident history — the retired pollers spawned AI sessions; this revision adds deterministic in-process code only and spawns nothing.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — establishes PROJECT-GTKB-RELIABILITY-FIXES, PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING, and GOV-RELIABILITY-FAST-LANE-001.

## Owner Decisions / Input

- 2026-05-17 owner directive — the owner observed `bridge/INDEX.md` had grown far past the protocol archival threshold and directed a dedicated archival pass.
- 2026-05-17 owner AskUserQuestion — the owner chose the helper-integrated event-driven trim mechanism.
- 2026-05-18 owner AskUserQuestion — the owner chose to diagnose the root cause before filing the `-003`.
- 2026-05-18 owner AskUserQuestion — after the -004 NO-GO, the owner chose Codex design 2 (authorization-aware prune) for the F1 resolution. The F2 origin-metadata fix is a required correction with no design choice and is bundled into this revision.
- No new owner decision is required before GO. This is a reliability-fast-lane defect fix covered by the standing project authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING through active project membership; no formal-artifact-approval packet is required.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Tests: the pipeline only archives-and-prunes threads whose latest status is VERIFIED; actionable entries are never removed; the authorization-aware skip keeps VERIFIED evidence for active authorizations in live INDEX. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All target paths and the new module are within `E:\GT-KB`; verified by inspection of the implementation diff. |
| F1 (NO-GO -004) | IP-6 test: an active authorization's already-VERIFIED work-item thread is not pruned by an unrelated event-driven write, and `verified_work_items()` still reports the work item; a companion test confirms it becomes prunable once the authorization is no longer active. |
| F2 (NO-GO -004) | IP-6 test: a GT-KB bridge thread archived by the pipeline yields a Deliberation Archive row with `origin_project="groundtruth-kb"`. |
| F2/F3 (NO-GO -002) | Tests: the archive-and-prune is a discrete best-effort post-write step with no atomicity assumption; archival uses the existing pipeline and the Deliberation Archive; no `bridge/INDEX-ARCHIVE.md` is created. |
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
- [ ] The pipeline skips (does not archive, does not prune) any VERIFIED thread whose `Work Item:` metadata is included in an active, not-completed project authorization; covered by the F1 test.
- [ ] GT-KB bridge-thread archive rows are written with `origin_project="groundtruth-kb"`, never `"agent-red"`; covered by the F2 test.
- [ ] `scripts/bridge_index_archival.py` provides `maybe_archive_and_prune_index()`: a no-op below threshold (no database load), and above threshold invokes the pipeline with the current thread excluded.
- [ ] All four INDEX-write paths invoke the entry point after their own write, passing the current document name; covered by tests.
- [ ] No `bridge/INDEX-ARCHIVE.md` is created; no atomicity claim is made or relied upon; the archive-and-prune is best-effort and fail-open.
- [ ] The post-implementation report carries the executed `pytest` command, observed results, and a before/after `bridge/INDEX.md` line count.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight (`scripts/bridge_applicability_preflight.py`) and the ADR/DCL clause preflight (`scripts/adr_dcl_clause_preflight.py`) are run against this `-005` content after the REVISED `bridge/INDEX.md` entry is inserted. A non-empty `missing_required_specs` or `missing_advisory_specs` list, or a blocking clause gap, is a self-detected defect corrected before review. Observed results are recorded by Prime Builder when the preflights are run against the filed `-005`.

## Risk And Rollback

Risk R1 (low): the archive-and-prune removes a still-actionable entry. Mitigation: the pipeline filters strictly to `latest_status == "VERIFIED"`; a directly tested invariant confirms GO/NO-GO/NEW/REVISED/ADVISORY are never in the working set.

Risk R2 (low): a VERIFIED thread tied to an active authorization is pruned before owner completion. Mitigation: the IP-2 authorization-aware skip removes such threads from the archive-and-prune set; the IP-6 F1 test proves it, including the unrelated-`current_thread` case the -004 NO-GO required.

Risk R3 (low): GT-KB bridge history is archived with the wrong origin. Mitigation: IP-3 replaces the hard-coded Agent Red values with GT-KB constants across all three archival call sites; the IP-6 F2 test asserts the corrected origin.

Risk R4 (low): the archive-and-prune step races a concurrent INDEX writer or the database is unavailable. Mitigation: the step is best-effort and fail-open — any exception is caught and swallowed; INDEX is left un-trimmed until the next bridge write retries.

Risk R5 (low): the first over-threshold run archives a large backlog in one call. Mitigation: archival is idempotent (already-archived threads are skipped via the content-hash check); the below-threshold fast path then skips the database entirely once INDEX is bounded.

Rollback: each IP is independently revertible. Reverting the four call-site additions restores prior behavior; the new module, the additive parameter, the authorization-aware skip, and the origin constants can be left in place unused. No bridge file or INDEX entry is destroyed; pruned entries are archived to the Deliberation Archive first.

## Loyal Opposition Asks

1. Confirm the IP-2 authorization-aware skip (Codex design 2) is a sufficient F1 resolution: a VERIFIED thread whose work item is in an active, not-completed project authorization is neither archived nor pruned, so live-INDEX completion readers still see it, and it becomes prunable only after the authorization is completed.
2. Confirm the IP-3 origin-metadata correction (GT-KB constants replacing the Agent Red hard-coding across all three `db.upsert_deliberation_source()` sites) resolves F2.
3. Confirm the retained -003 design (reuse the existing pipeline, `exclude_threads` guard, discrete best-effort post-write entry point, no `bridge/INDEX-ARCHIVE.md`, no atomicity claim) continues to resolve the -002 findings.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
