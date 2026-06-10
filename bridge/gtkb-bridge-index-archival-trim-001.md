NEW

# Helper-Integrated bridge/INDEX.md Archival Trim (WI-3364)

bridge_kind: prime_proposal
Document: gtkb-bridge-index-archival-trim
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: GOV-FILE-BRIDGE-AUTHORITY-001; WI-3364
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3364
target_paths: ["scripts/bridge_index_archival.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", ".claude/skills/bridge/helpers/revise_bridge.py", ".claude/skills/bridge/helpers/impl_report_bridge.py", "scripts/gtkb_bridge_writer.py", "platform_tests/**"]
Recommended commit type: fix:

## Claim

`bridge/INDEX.md` — the canonical file-bridge workflow state — grows without bound. It is currently ~77000 tokens, far past the ~200-line archival threshold. The file-bridge protocol's Index Maintenance provision already sanctions archival: when INDEX exceeds ~200 lines, the agent inserting a new entry may remove the oldest entries from the bottom, and archived entries plus their bridge files remain on disk. The INDEX header carries the same guideline as a comment. But the trim has never been automated, and the permissive "may" has meant it is never done — so every bridge scan, every applicability preflight, and every helper that reads INDEX pays the full-file cost. Unbounded growth of the bridge's own coordination file is a reliability and token-cost defect.

Four code paths insert entries into `bridge/INDEX.md`, each with its own un-shared insertion logic:
- `.claude/skills/bridge-propose/helpers/write_bridge.py` `_update_bridge_index()` — new `Document:` plus `NEW:` entry at the top.
- `.claude/skills/bridge/helpers/revise_bridge.py` `_insert_revised_index_line()` — `REVISED:` line within a document block.
- `.claude/skills/bridge/helpers/impl_report_bridge.py` `_insert_new_index_line()` — post-implementation `NEW:` line within a document block.
- `scripts/gtkb_bridge_writer.py` `insert_index_status()` — verdict (`GO`/`NO-GO`/`VERIFIED`/`ADVISORY`) line within a document block.

This proposal adds a shared, deterministic archival trim and invokes it from all four paths after insertion, so `bridge/INDEX.md` is bounded automatically on every bridge write. Per the owner AskUserQuestion decision of 2026-05-17, the archival is a deterministic event-driven step inside the bridge-write helpers — not a scheduled AI routine, which would re-create the retired-poller token-cost anti-pattern and contradict the Deterministic Services Principle.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — `bridge/INDEX.md` is the canonical bridge workflow state; keeping it bounded and maintainable preserves that authority. The archival trim never removes an actionable entry, so canonical queue state is preserved.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; this proposal claims fast-lane eligibility and maps the four criteria in the Fast-Lane Eligibility section.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation; the trim archives removed entries to `bridge/INDEX-ARCHIVE.md` and leaves every bridge file on disk, so no audit history is destroyed (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions; the trim keys on terminal (`VERIFIED`) lifecycle status to decide what is archivable (advisory).

## Fast-Lane Eligibility

This thread claims eligibility under `GOV-RELIABILITY-FAST-LANE-001` and the standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers-by-membership: WI-3364 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`). The four criteria:

1. **Origin defect** — met. WI-3364 has `origin=defect`. Unbounded growth of `bridge/INDEX.md` is a token-cost regression paid by every bridge scan and preflight.
2. **No new API/CLI/behavior beyond removing the defect** — met. The archival trim implements the maintenance behavior the file-bridge protocol's Index Maintenance provision already sanctions ("may remove the oldest entries"); it automates a documented manual step, it does not add a user-facing capability. No new CLI and no new public API: the trim function is internal to the bridge-write helpers. The defect being removed is the unbounded growth that resulted from the maintenance step never being performed.
3. **No new requirement** — met. `GOV-FILE-BRIDGE-AUTHORITY-001` and the file-bridge protocol's Index Maintenance provision already govern; the owner directive clarifies that the sanctioned maintenance should be automated. No new GOV/SPEC/PB/ADR/DCL artifact is created; the line threshold is a parameter, not a specification.
4. **Small single-concern scope** — met. One concern: bounding `bridge/INDEX.md`. The substantive logic is one pure function in one new module; the four call-site hookups are each a single post-insertion call (no shared INDEX-write module exists today, so the trim must be invoked from each path). No cross-cutting change.

## Prior Deliberations

- 2026-05-17 owner AskUserQuestion: the owner chose the helper-integrated deterministic trim mechanism over a recurring `/schedule` AI routine and over a script-plus-OS-task. This proposal implements that chosen mechanism.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive mechanical work belongs in a deterministic service, not AI sessions. INDEX-trimming is purely mechanical; the helper-integrated event-driven trim is that principle applied directly.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` and the bridge-essential rule's Incident History — the OS pollers and the smart poller were retired after a ~10x token-cost regression from scheduled AI spawns. A scheduled AI routine for INDEX-trimming would re-create that anti-pattern; the helper-integrated deterministic trim avoids it entirely.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — the owner decision establishing `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and `GOV-RELIABILITY-FAST-LANE-001`. This proposal is filed under that standing authorization.

## Owner Decisions / Input

- 2026-05-17 owner directive: the owner observed that `bridge/INDEX.md` is ~77000 tokens, far past the protocol archival threshold, and directed Prime Builder to schedule a dedicated archival pass.
- 2026-05-17 via AskUserQuestion the owner chose the Helper-integrated trim mechanism: INDEX-tail trimming as an automatic deterministic step inside the bridge-write helpers (event-driven, zero scheduled-AI cost), in preference to a recurring `/schedule` AI routine or a deterministic script plus OS scheduled task. The owner-selected option was framed as a reliability-fast-lane bridge proposal under a new work item; WI-3364 is that work item.
- No further owner decision is required before GO. This is a reliability-fast-lane defect fix covered by the standing project authorization; no formal-artifact-approval packet and no new owner decision are required.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` and the file-bridge protocol's Index Maintenance provision already govern `bridge/INDEX.md` and provide for archival; the owner directive clarifies that the maintenance should be automated and deterministic. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix: one new trim module, four post-insertion call-site hookups, and regression tests. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. The archival trim operates on `bridge/INDEX.md` entries (bridge threads), not on MemBase work items; `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3364) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Shared deterministic INDEX archival-trim module

Add `scripts/bridge_index_archival.py` exposing a pure function `trim_index(index_text, *, max_lines=...)` that returns the trimmed INDEX text plus the list of removed `Document:` blocks. Behavior:
- Parse `bridge/INDEX.md` into its leading header/comment region and the ordered list of `Document:` blocks (each block is a `Document: <slug>` line plus its consecutive `STATUS:` lines; blocks are newest-first, oldest at the bottom).
- If the total line count is at or below the threshold, return the text unchanged.
- If it exceeds the threshold, remove whole `Document:` blocks from the bottom (oldest first) until the file is at or below the threshold or no further removable block remains.
- Safety invariant — never archive actionable work. A block is removable only when its latest (top) status line is terminal: `VERIFIED` or `WITHDRAWN`. A block whose latest status is `NEW`, `REVISED`, `GO`, `NO-GO`, or `ADVISORY` is never removed; the trim skips it and continues to older blocks. The actionable set is therefore an unconditional floor — the trim reduces `bridge/INDEX.md` toward the threshold but never below the size of the live actionable queue.
- The function performs no I/O; it is a pure transform so it is fully unit-testable.

The threshold is a named module constant (default aligned with the protocol's ~200-line guideline) so it is tunable without a specification change.

### IP-2: Invoke the trim from all four INDEX-write paths

In each of the four INDEX-mutation functions — `write_bridge.py` `_update_bridge_index()`, `revise_bridge.py` `_insert_revised_index_line()`, `impl_report_bridge.py` `_insert_new_index_line()`, and `gtkb_bridge_writer.py` `insert_index_status()` — after the new entry or line has been inserted into the in-memory INDEX content and before the existing atomic temp-file-plus-replace write, call `trim_index()` on that content. Removed blocks are appended to `bridge/INDEX-ARCHIVE.md` (created on first use) so the archived index history is preserved alongside the on-disk bridge files. The trimmed text is what is atomically written. The trim is inserted inside each path's existing atomic-write and conflict-retry flow, so it does not change the concurrency contract.

No shared INDEX-write module is created; the larger refactor of routing all four paths through one shared writer is a separate concern and is out of scope here. Only the trim logic is shared, via the `scripts/bridge_index_archival.py` import.

### IP-3: Regression tests

Add `platform_tests/` coverage:
- `trim_index()` unit tests: below-threshold input is unchanged; above-threshold input has oldest terminal blocks removed until at or under the threshold; a non-terminal (`NEW`/`REVISED`/`GO`/`NO-GO`/`ADVISORY`) block at the bottom is never removed even when the file is over the threshold; the header/comment region is preserved; removed blocks are returned for archival.
- The safety invariant: a fixture INDEX whose only over-threshold content is actionable blocks is returned unchanged (the actionable floor holds).
- Integration: each of the four INDEX-write paths invokes `trim_index()` and writes the trimmed result, and appends removed blocks to `bridge/INDEX-ARCHIVE.md`.

## Out Of Scope

- Routing the four INDEX-write paths through a single shared INDEX-write module — a separate larger refactor; this proposal shares only the trim function.
- Any change to entry-insertion logic, the atomic-write pattern, or the concurrency/retry contract of the four paths.
- Any change to bridge `*.md` files — they remain on disk; only `bridge/INDEX.md` lines are trimmed and mirrored to `bridge/INDEX-ARCHIVE.md`.
- A scheduled task, cron job, OS scheduled task, or AI routine — the owner chose the helper-integrated event-driven mechanism.
- Any file outside `E:\GT-KB`. All target paths are within the project root.

## Files Expected To Change

- `scripts/bridge_index_archival.py` — NEW: the shared `trim_index()` archival module (IP-1).
- `.claude/skills/bridge-propose/helpers/write_bridge.py` — IP-2: invoke `trim_index()` in `_update_bridge_index()` after insertion.
- `.claude/skills/bridge/helpers/revise_bridge.py` — IP-2: invoke `trim_index()` in `_insert_revised_index_line()` after insertion.
- `.claude/skills/bridge/helpers/impl_report_bridge.py` — IP-2: invoke `trim_index()` in `_insert_new_index_line()` after insertion.
- `scripts/gtkb_bridge_writer.py` — IP-2: invoke `trim_index()` in `insert_index_status()` after insertion.
- `platform_tests/**` — IP-3: regression coverage for the trim function, the safety invariant, and the four call sites.

`bridge/INDEX-ARCHIVE.md` is created at runtime by the trim on first archival; it is a runtime-maintained artifact, not an implementation-edited source file, so it is not a target path. The existing ~77000-token `bridge/INDEX.md` bloat is cleared automatically by the first bridge filing after this lands — the trim runs on every INDEX write and reduces toward the threshold regardless of the starting size — so no separate one-time pass is required.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Tests: the trim never removes a block whose latest status is actionable (`NEW`/`REVISED`/`GO`/`NO-GO`/`ADVISORY`), so canonical queue state is preserved; the header region is preserved. |
| File-bridge protocol Index Maintenance provision | Tests: an over-threshold INDEX has oldest terminal blocks removed until at or under the threshold; a below-threshold INDEX is unchanged. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Test: removed blocks are returned and appended to `bridge/INDEX-ARCHIVE.md`; bridge `*.md` files are untouched. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms eligibility. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed `pytest` command and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/ -q -k "index_archival or trim_index or bridge_index"`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-index-archival-trim`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-index-archival-trim`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/bridge_index_archival.py` provides a pure `trim_index()` that removes oldest terminal `Document:` blocks until the file is at or under the threshold; covered by tests.
- [ ] The safety invariant holds — no block with an actionable latest status is ever removed; covered by tests.
- [ ] All four INDEX-write paths invoke `trim_index()` after insertion and append removed blocks to `bridge/INDEX-ARCHIVE.md`; covered by tests.
- [ ] No change to the entry-insertion logic, atomic-write pattern, or concurrency/retry contract of the four paths.
- [ ] Post-implementation report carries the executed `pytest` command and observed results, including a before/after `bridge/INDEX.md` line count.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight (`scripts/bridge_applicability_preflight.py`) and the ADR/DCL clause preflight (`scripts/adr_dcl_clause_preflight.py`) are run against this proposal content with `--content-file` before the live `NEW` `bridge/INDEX.md` entry is inserted. A non-empty `missing_required_specs` or `missing_advisory_specs` list, or a blocking clause gap, is a self-detected defect corrected before filing. Observed results (run against this `-001` draft content prior to filing): the applicability preflight reported `preflight_passed: true` with `missing_required_specs: []` and `missing_advisory_specs: []` (6 specs matched, all cited); the clause preflight evaluated 5 `must_apply` clauses with 0 evidence gaps and 0 blocking gaps (gate exit 0).

## Risk And Rollback

**Risk R1 (medium): the trim removes a still-actionable entry, dropping it from the canonical queue.** Mitigation: the safety invariant — only blocks whose latest status is terminal (`VERIFIED`/`WITHDRAWN`) are removable — is the core of IP-1 and is directly tested, including the case where the over-threshold content is entirely actionable (the file is then returned unchanged).

**Risk R2 (low): the trim races a concurrent INDEX writer.** Mitigation: the trim runs inside each path's existing atomic temp-file-plus-replace write and conflict-retry flow; it transforms the in-memory content immediately before the existing atomic write, so it inherits the existing concurrency protection rather than adding a new write.

**Risk R3 (low): an archived entry is later needed.** Mitigation: archival is non-destructive — every bridge `*.md` file remains on disk, and the removed INDEX blocks are appended to `bridge/INDEX-ARCHIVE.md`. Nothing is deleted; entries move from the live index to the archive index.

Rollback: each IP is independently revertible. Reverting the four call-site hookups restores prior (un-trimmed) behavior; the new module can be left in place unused or removed. No bridge file or INDEX entry is destroyed by the change, so rollback has no data-loss exposure.

## Loyal Opposition Asks

1. Confirm the safety invariant — only terminal (`VERIFIED`/`WITHDRAWN`) blocks are removable, actionable blocks are an unconditional floor — is the correct and sufficient guard against archiving live bridge work.
2. Confirm sharing only the `trim_index()` function (rather than first refactoring the four paths onto one shared INDEX-write module) is the right scope boundary for a reliability-fast-lane fix, with the larger routing refactor left as a separate concern.
3. Confirm the default line threshold and the decision to append removed entries to `bridge/INDEX-ARCHIVE.md` (rather than discard the lines, relying only on the bridge `*.md` files remaining on disk).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
