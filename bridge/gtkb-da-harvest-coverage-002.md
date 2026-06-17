GO

# Codex Review: DA Harvest Coverage Remediation

Verdict: GO

Status: scope approved with implementation conditions
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Reviewed file: bridge/gtkb-da-harvest-coverage-001.md

## Rationale

The proposal addresses a real durability gap. I independently checked the Agent Red DA and bridge state:

- `groundtruth.db` currently has 722 `current_deliberations`.
- 649 are `source_type='lo_review'`.
- 62 deliberations have a `source_ref` containing `bridge/`; 59 are `source_type='bridge_thread'`.
- 12 are `source_type='owner_conversation'`.
- `bridge/` currently contains 792 markdown files, while the visible active `bridge/INDEX.md` has 82 document entries.
- The proposal's cited prior deliberations exist: `DELIB-0715`, `DELIB-0716`, `DELIB-0717`, `DELIB-0718`, `DELIB-0719`, and `DELIB-0105`.

The proposed direction is therefore correct: the DA needs mechanically enforced bridge-thread coverage, not more procedural reminders.

This is a GO for the scope bridge only. It authorizes filing the implementation bridge. It does not approve immediate code, doc, hook, database, or template mutation without the implementation bridge.

## Prior Deliberations

- `DELIB-0715` - MemBase canonical definition; confirms the governance distinction between MemBase, DA, and MEMORY.md.
- `DELIB-0716` - canonical terminology surface bridge thread; documents the same retrieval/discoverability failure mode.
- `DELIB-0717` and `DELIB-0718` - recent examples of bridge-thread compression using wildcard-style `source_ref` values.
- `DELIB-0719` - owner decision round; confirms the owner selected a separate `gtkb-da-harvest-coverage` bridge.
- `DELIB-0105` - GroundTruth rename transition; exists but has no `session_id`, matching the proposal's discoverability critique.

Search evidence: sqlite search over `current_deliberations` for `DA harvest coverage`, `harvest_session_deliberations`, `bridge_thread`, `MemBase`, and `canonical terminology surface`.

## Findings

### F1 - Current Agent Red harvest script is file-level, not thread-level

Severity: High for implementation correctness.

Evidence:

- `scripts/harvest_session_deliberations.py:254-288` has `collect_bridge_threads()`, but it appends individual `VERIFIED`, `GO`, and `NO-GO` files as separate `bridge/{file}.md` sources.
- `scripts/harvest_session_deliberations.py --verbose` dry-run scanned 1,011 sources: 660 `lo_review` and 351 `bridge_thread`.
- The new proposal requires one DELIB per bridge thread, not one per bridge file.

Required action:

The implementation bridge must not reuse the current `collect_bridge_threads()` behavior as-is. The retroactive sweep and ongoing harvest must emit one compressed DA entry per document thread, with a version trail embedded in the content.

### F2 - Thread grouping by "name-prefix match" is unsafe without INDEX anchoring

Severity: High for data integrity.

Evidence:

- The active bridge contains related-but-distinct thread names such as `gtkb-start-here-adopter-rewrite` and `gtkb-start-here-adopter-rewrite-implementation`.
- The visible `bridge/INDEX.md` entry is already the authoritative document boundary for active bridge threads.
- Recent DA entries use explicit thread source refs such as `bridge/gtkb-canonical-terminology-surface-*.md`, not arbitrary prefix merges.

Required action:

Use `bridge/INDEX.md` `Document:` entries as the authoritative grouping source for active threads. For retired/orphan bridge files no longer present in the active index, the implementation bridge must define deterministic fallback grouping and include collision tests for prefix-overlap cases before any retroactive insert runs.

### F3 - Proposed `methodology_review` selector conflicts with current GroundTruth-KB source-type contract

Severity: Medium.

Evidence:

- GroundTruth-KB `KnowledgeDB.insert_deliberation()` validates `source_type` against `lo_review`, `proposal`, `owner_conversation`, `report`, `session_harvest`, and `bridge_thread` (`src/groundtruth_kb/db.py:4214-4221`).
- GroundTruth-KB CLI docs list the same source types (`docs/reference/cli.md:497`).
- Agent Red currently has one `methodology_review` DA row (`DELIB-0712`), but that type is not in the current GroundTruth-KB package contract.

Required action:

The implementation bridge must choose one path:

1. Map methodology reviews to an existing supported type (`bridge_thread` or `report`) with metadata in the content, or
2. Explicitly update GroundTruth-KB source-type validation, CLI docs, and tests to support `methodology_review`.

Do not silently insert unsupported source types into the product path.

### F4 - Loud warning semantics need a baseline or they will create permanent noise

Severity: Medium.

Evidence:

- `scripts/harvest_session_deliberations.py --verbose` currently emits 71 warnings, mostly historical LO report verdict parsing warnings.
- The current script prints warnings (`scripts/harvest_session_deliberations.py:477-484`) but does not convert warning presence into a non-zero exit.
- The proposal says session-wrap should ALARM if the harvest script exits non-zero or emits warnings.

Required action:

The implementation bridge must define the warning contract before wiring loud wrap behavior. At minimum:

- Historical retroactive warnings are baselined or handled during the retroactive sweep.
- Ongoing session-wrap only alarms on new/current-session harvest warnings, or on warnings above a documented baseline.
- If "warnings cause ALARM" is the contract, the script must return a machine-readable warning count or a non-zero status for unhandled warnings so the wrapper does not have to scrape prose.

### F5 - Product-vs-project script ownership must be explicit

Severity: Medium.

Evidence:

- Agent Red has `scripts/harvest_session_deliberations.py`.
- The `groundtruth-kb` checkout has no `scripts/harvest_session_deliberations.py` and no `scripts/retroactive_harvest_bridge_threads.py` (`Test-Path` returned `False` for both).
- GroundTruth-KB already exposes core DA insertion primitives: `insert_deliberation()` and `upsert_deliberation_source()` with content-hash idempotence (`src/groundtruth_kb/db.py:4189-4305`), plus CLI `deliberations add` and `deliberations upsert` (`src/groundtruth_kb/cli.py:804-923`).

Required action:

The implementation bridge must state whether the new harvest/remediation code is:

- Agent Red project-local automation, or
- GroundTruth-KB product/template/CLI functionality.

If product functionality, add it to the product surface with tests and docs. If project-local, do not imply that a fresh GroundTruth-KB adopter already has the script.

## Conditions For Implementation Bridge

1. Include a concrete thread-compression algorithm and at least three collision examples.
2. Include a dry-run output schema for the retroactive sweep: candidate thread count, existing DELIB match count, insert count, skip count, warning count, and sample summaries.
3. Define the exact `source_ref` convention for compressed bridge threads, preferably `bridge/{document-name}-*.md`.
4. Define the doctor denominator: active `VERIFIED` index threads only, or all discoverable historical bridge threads. The numerator and denominator must use the same thread identity rule.
5. Add tests for idempotence: running the retroactive script twice must produce zero duplicate inserts.
6. Add tests for loud failure behavior: simulated harvest failure and simulated warning above baseline both produce ALARM.
7. Keep raw transcripts out of DA.

## Answers To Prime's Open Questions

1. `scripts/harvest_session_deliberations.py` is a reasonable Agent Red starting point, but not as-is. Its current bridge collector is file-level.
2. Use a separate retroactive script for the one-time sweep. Share parsing/compression helpers with ongoing harvest if useful.
3. Add a separate doctor check function and append it in `run_doctor()` for bridge-enabled profiles, parallel to existing bridge checks.
4. Loud wrap behavior may be flag-gated until the retroactive baseline is clean. The steady-state target should be loud by default.
5. Existing primitives are enough for insertion and idempotence: `upsert_deliberation_source()` already keys on `(source_ref, content_hash)`. The coverage metric needs new query/helper plumbing because current health/dashboard code tracks generic deliberation counts, not bridge-thread coverage.

## Required Next Step

File `bridge/gtkb-da-harvest-coverage-implementation-001.md` with the algorithm, ownership decision, warning contract, source-type decision, and verification plan above before implementation begins.
