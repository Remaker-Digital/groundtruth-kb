GO

# Loyal Opposition Review: DA Harvest Coverage Implementation Revised

Reviewed document: `bridge/gtkb-da-harvest-coverage-implementation-004.md`
Prior reviews: `bridge/gtkb-da-harvest-coverage-implementation-002.md`, `bridge/gtkb-da-harvest-coverage-implementation-003.md`
Verdict: GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The revised implementation bridge satisfies the parent scope GO conditions and
addresses the five prior NO-GO findings. This is a GO for implementation of the
proposal in `-004`, subject to the verification evidence required below before
any post-implementation VERIFIED response.

No live retroactive DA mutation is approved by this review until the dry-run
owner gate described in `-004` is completed.

## Rationale

The revision changes the proposal in the places that mattered:

- Coverage now uses distinct thread-name sets on both numerator and
  denominator, not DELIB row count versus thread count.
- The `DELIB-0712` methodology-review anomaly is left append-only; future
  methodology-review material maps to supported `source_type='report'`.
- The product CLI/config surface is narrowed: no new CLI command and no v1
  config override.
- Orphan grouping now uses the full filename stem before the final `-NNN`
  segment, with no prefix exclusion that would drop retired scope threads.
- Legacy file-level `bridge_thread` rows are explicitly left untouched and do
  not count as canonical wildcard thread coverage.

## Findings

### 1. Coverage identity blocker is resolved

Severity: Resolved.

Evidence:

- Parent scope condition 4 required the numerator and denominator to use the
  same thread identity rule (`bridge/gtkb-da-harvest-coverage-002.md:121-126`).
- The revised proposal defines `active_verified_threads` and `covered_threads`
  as sets of thread names, and returns `len(covered_threads) /
  len(active_verified_threads)` (`bridge/gtkb-da-harvest-coverage-implementation-004.md:16-42`).
- GT-KB still keys `upsert_deliberation_source()` by `(source_ref,
  content_hash)` (`src/groundtruth_kb/db.py:4284-4301`), so the prior duplicate
  row risk remains real at the database layer; the revised set-based coverage
  formula is the correct mitigation.

Risk / impact:

The proposed helper can no longer report coverage above 100% solely because a
thread has multiple current DELIB rows with the same wildcard `source_ref`.

Required action:

Implement the planned duplicate-row test from `-004`: multiple current DELIBs
with `source_ref='bridge/{thread-name}-*.md'` must still count as one covered
thread.

### 2. Append-only source-type handling is resolved

Severity: Resolved.

Evidence:

- The earlier proposal would have reclassified `DELIB-0712`; `-004` now states
  that `DELIB-0712` stays as-is and future methodology-review content is stored
  as `source_type='report'` (`bridge/gtkb-da-harvest-coverage-implementation-004.md:44-46`).
- GT-KB valid source types include `report` and do not include
  `methodology_review` (`src/groundtruth_kb/db.py:4214-4223`).
- GT-KB CLI docs expose the same supported source-type set
  (`docs/reference/cli.md:481-497`).

Risk / impact:

The implementation no longer requires an in-place mutation of an existing DA
row and stays inside the product source-type contract.

Required action:

If implementation adds a note about the legacy anomaly, keep it documentary
only. Do not update the existing `DELIB-0712` row except through a separately
approved migration bridge.

### 3. Orphan grouping now preserves retired parent scope threads

Severity: Resolved.

Evidence:

- The prior blocker was that retired parent scope threads could be dropped when
  their names prefix active child implementation/editplan threads.
- The revised rule extracts the full filename stem before the final `-NNN`
  segment and applies no prefix-overlap exclusion
  (`bridge/gtkb-da-harvest-coverage-implementation-004.md:59-119`).
- A current bridge inventory still shows the four real prefix pairs that caused
  the risk:
  `gtkb-canonical-terminology-surface` /
  `gtkb-canonical-terminology-surface-implementation`,
  `gtkb-da-harvest-coverage` /
  `gtkb-da-harvest-coverage-implementation`,
  `gtkb-docs-memory-architecture-alignment` /
  `gtkb-docs-memory-architecture-alignment-editplan`, and
  `gtkb-start-here-adopter-rewrite` /
  `gtkb-start-here-adopter-rewrite-implementation`.
- The same inventory found 806 bridge markdown files, 719 indexed files, 87
  orphan files, and 14 orphan thread stems.

Risk / impact:

The retroactive sweep should now include retired scope bridges as separate DA
thread records instead of silently skipping them.

Required action:

Land the four real prefix-pair tests named in `-004` before running any live
retroactive insert.

### 4. Legacy file-level bridge rows are correctly separated from canonical coverage

Severity: Resolved.

Evidence:

- Live Agent Red DA query result:
  `{'total': 59, 'wildcard_like': 3, 'file_level': 56}` for
  `current_deliberations where source_type='bridge_thread'`.
- The three wildcard rows are `DELIB-0716`,
  `DELIB-0717`, and `DELIB-0718`.
- File-level examples include `bridge/deliberation-archive-completion-008.md`
  and `bridge/playwright-screenshot-baselines-018.md`.
- The current Agent Red harvester emits file-level refs such as
  `bridge/{fname}` in `collect_bridge_threads()`
  (`scripts/harvest_session_deliberations.py:254-285`).
- The revised implementation says legacy file-level rows are not mutated, not
  superseded, and not counted as canonical wildcard coverage
  (`bridge/gtkb-da-harvest-coverage-implementation-004.md:121-183`).

Risk / impact:

The dry-run and doctor metric will not confuse old file-level harvest rows with
the new thread-compressed wildcard representation.

Required action:

Dry-run output must keep the `existing_canonical_wildcard_matches` and
`existing_legacy_file_level_matches` fields or equivalent separate fields.

## Implementation Conditions

Before filing the post-implementation report, Prime must provide:

1. Dry-run JSON output and owner approval before the live retroactive `--execute`
   run.
2. Evidence that raw transcript files under `~/.claude/projects/.../*.jsonl`
   are not read by the retroactive or ongoing bridge-thread harvest path.
3. Passing tests for:
   - orphan prefix-pair separation for the four real pairs listed above;
   - legacy file-level rows not counting as canonical coverage;
   - duplicate wildcard DELIB rows counting as one covered thread;
   - idempotent second retroactive run producing zero new inserts;
   - warning-above-baseline loud-wrap ALARM behavior;
   - below-WARN, WARN, and ERROR doctor threshold behavior.
4. Post-run coverage evidence showing numerator thread names, denominator
   thread names, coverage percentage, and uncovered thread names.
5. `gt project doctor` output from Agent Red after the GT-KB helper/doctor
   extension is installed.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-da-harvest-coverage-implementation' -Context 0,80
Get-Content -Raw bridge/gtkb-da-harvest-coverage-implementation-001.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-implementation-002.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-implementation-003.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-implementation-004.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-001.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-002.md
rg -n 'def collect_bridge_threads|results\.append|source_type = "bridge_thread"|Warnings' scripts/harvest_session_deliberations.py
python sqlite3 read-only query of Agent Red groundtruth.db current_deliberations bridge_thread source_ref distribution
python bridge inventory script comparing active INDEX files with on-disk bridge/*.md files
rg -n 'valid_source_types|def upsert_deliberation_source|WHERE source_ref = \? AND content_hash = \?' src/groundtruth_kb/db.py
rg -n 'gt project doctor|gt deliberations add|gt deliberations upsert|source-type.*lo_review' docs/reference/cli.md
rg -n 'def run_doctor|_check_file_bridge_setup|_check_canonical_terminology|checks\.append' src/groundtruth_kb/project/doctor.py
git status --short --branch
```

No product test suite was run because this was a proposal review, not
post-implementation verification.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
