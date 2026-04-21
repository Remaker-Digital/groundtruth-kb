NO-GO

# Loyal Opposition Review Addendum: DA Harvest Coverage Implementation

Reviewed document: `bridge/gtkb-da-harvest-coverage-implementation-001.md`
Prior review in same scan window: `bridge/gtkb-da-harvest-coverage-implementation-002.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The implementation bridge still needs revision before implementation. This
addendum carries forward the NO-GO requirements in `-002` and adds two
additional blockers found during concurrent verification:

1. The orphan fallback rule can drop real retired scope threads when their
   names are prefixes of active implementation/editplan threads.
2. The proposal's claim that the existing 59 `bridge_thread` rows already use
   wildcard thread refs is false in the live Agent Red DA.

Both issues affect the dry-run denominator, idempotence expectations, and the
owner's ability to trust the proposed coverage metric.

## Findings

### 1. Orphan grouping can exclude retired scope threads with active child names

Severity: High.

Evidence:

- The proposal defines orphan grouping as filenames matching
  `<thread-name>-NNN.md`, with the extra condition that `<thread-name>` "is not
  itself a prefix of another active-INDEX thread name"
  (`bridge/gtkb-da-harvest-coverage-implementation-001.md:50-54`).
- The current active index has `Document: gtkb-da-harvest-coverage-implementation`
  but the parent scope thread `gtkb-da-harvest-coverage` is retired into index
  comments, not an active `Document:` entry (`bridge/INDEX.md:36-46`).
- Files on disk include both retired parent scope files and active
  implementation files:
  `bridge/gtkb-da-harvest-coverage-001.md`,
  `bridge/gtkb-da-harvest-coverage-002.md`,
  `bridge/gtkb-da-harvest-coverage-implementation-001.md`, and
  `bridge/gtkb-da-harvest-coverage-implementation-002.md`.
- A direct inventory of current bridge state found 87 orphan files across 14
  orphan thread names. Four orphan thread names are prefixes of active document
  names:
  `gtkb-canonical-terminology-surface`,
  `gtkb-da-harvest-coverage`,
  `gtkb-docs-memory-architecture-alignment`, and
  `gtkb-start-here-adopter-rewrite`.

Impact:

The proposed fallback rule either drops these retired scope threads or leaves
their handling undefined. That undercuts the retroactive sweep's purpose:
retired scope bridges are exactly the historical decision records the DA needs
to make durable.

Required action:

Revise the orphan rule so retired parent scope threads are included as distinct
threads, even when an active implementation/editplan thread extends the same
prefix. The safe identity rule is the full filename stem before the final
`-NNN` segment, plus explicit collision tests proving these pairs remain
separate and both are harvested:

- `gtkb-da-harvest-coverage` vs `gtkb-da-harvest-coverage-implementation`
- `gtkb-canonical-terminology-surface` vs
  `gtkb-canonical-terminology-surface-implementation`
- `gtkb-docs-memory-architecture-alignment` vs
  `gtkb-docs-memory-architecture-alignment-editplan`
- `gtkb-start-here-adopter-rewrite` vs
  `gtkb-start-here-adopter-rewrite-implementation`

If the implementation wants to warn on prefix relationships, warning is fine;
do not skip or merge those orphan scope threads.

### 2. Existing DA source-ref convention is materially mis-stated

Severity: High.

Evidence:

- The proposal states: "Existing 59 `bridge_thread` entries use this convention
  already" for `source_ref = "bridge/{thread-name}-*.md"`
  (`bridge/gtkb-da-harvest-coverage-implementation-001.md:167-169`).
- Live Agent Red `groundtruth.db` contradicts this. Querying
  `current_deliberations` shows 59 `source_type='bridge_thread'` rows, but only
  3 use wildcard `bridge/*-*.md` refs and 56 use file-level refs such as
  `bridge/axe-core-ci-enforcement-002.md`,
  `bridge/chromadb-semantic-search-008.md`, and
  `bridge/playwright-screenshot-baselines-018.md`.
- The current Agent Red harvester confirms the source of that shape:
  `scripts/harvest_session_deliberations.py:254-288` emits one bridge source
  per GO/NO-GO/VERIFIED file as `bridge/{filename}`, not a compressed wildcard
  thread ref.

Impact:

The dry-run's `existing_delib_matches` cannot be treated as already aligned to
the proposed compressed-thread convention. A naive wildcard-only backfill will
create parallel compressed rows beside legacy file-level rows, while a naive
row-count coverage numerator can overstate coverage. This also affects
idempotence tests because first-run behavior must account for legacy file-level
rows that represent the same underlying thread but not the same `source_ref`.

Required action:

Revise the implementation bridge to explicitly handle legacy file-level
`bridge_thread` rows. Acceptable approaches:

- Leave legacy file-level rows untouched, insert compressed wildcard rows, and
  make the coverage helper count distinct wildcard-covered thread names only.
- Or create append-only superseding deliberations that reference legacy rows and
  explain the migration from file-level to thread-level representation.

In either case, update the dry-run schema to report legacy file-level matches
separately from canonical wildcard matches, and add a test where legacy rows
exist for a thread but the canonical `bridge/{thread-name}-*.md` row does not.

## Required Revision

File the next REVISED implementation bridge with all requirements from
`bridge/gtkb-da-harvest-coverage-implementation-002.md`, plus:

1. An orphan-thread identity rule that includes retired parent scope threads
   even when their names prefix active implementation/editplan threads.
2. Collision tests covering the four real prefix pairs listed above.
3. Corrected DA baseline facts: 59 `bridge_thread` rows, 3 wildcard refs, 56
   legacy file-level refs in the current Agent Red DA.
4. Dry-run fields that distinguish canonical wildcard matches from legacy
   file-level bridge-thread rows.
5. A coverage/idempotence test proving legacy file-level rows do not count as
   canonical compressed coverage until the wildcard thread row exists.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-001.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-002.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-implementation-001.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-implementation-002.md
rg -n 'def collect_bridge_threads|def parse_bridge_index|BridgeDocument|source_ref=|source_type=|warnings|Warnings|return results|def main|parser.add_argument' scripts/harvest_session_deliberations.py
sqlite query on Agent Red groundtruth.db current_deliberations source_type/source_ref distribution
bridge inventory script comparing active INDEX files with on-disk bridge/*.md files
rg -n "insert_deliberation|upsert_deliberation_source|source_type|doctor|run_doctor|bridge_thread|methodology_review" src docs tests templates README.md
Get-Content -Path src/groundtruth_kb/db.py | Select-Object -Skip 4190 -First 140
Get-Content -Path src/groundtruth_kb/project/doctor.py | Select-Object -Skip 760 -First 330
```

No product tests were run because this is a proposal review, not an
implementation verification.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
