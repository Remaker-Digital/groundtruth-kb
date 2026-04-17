# Phase 3 Dry-Run Status: DA Harvest Coverage Implementation

**Status:** PHASE-3-OWNER-GATE (informational; not a NEW/REVISED proposal)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**GO reference:** `bridge/gtkb-da-harvest-coverage-implementation-005.md`
**Approved proposal:** `bridge/gtkb-da-harvest-coverage-implementation-004.md`

This file is an **interim Phase 3 checkpoint**. It is NOT a new proposal, NOT
a revised proposal, and NOT a post-implementation report. It exists so that
the owner can review the Phase 3 dry-run output before authorizing the
Phase 4 live `--execute` run, as required by Codex GO condition 1.

**No DA mutation has been performed. No commit has been made.**

## What Was Done This Spawn

**Phase 1 — Spec recording: COMPLETE.**

7 specs inserted into KB at `groundtruth.db` with
`type='requirement'`, `tags=['da-coverage','governance','harvest']`,
`status='specified'`:

| ID | Title | Testability |
|----|-------|------------|
| SPEC-DA-HARVEST-INCLUSION | DA harvest inclusion criteria | automatable |
| SPEC-DA-HARVEST-EXCLUSION | DA harvest exclusion criteria | structural |
| SPEC-DA-THREAD-COMPRESSION | DA MUST store one DELIB per bridge thread | automatable |
| SPEC-DA-MECHANICAL-ENFORCE | Session-wrap fails LOUD on harvest failure | automatable |
| SPEC-DA-COVERAGE-METRIC | DA bridge-thread coverage metric | automatable |
| SPEC-DA-RETROACTIVE-SWEEP | Retroactive back-harvest idempotence | automatable |
| SPEC-DA-DOCTOR-CHECK | `gt project doctor` bridge-thread coverage check | automatable |

**Phase 2a — Retroactive script: COMPLETE.**

New file: `scripts/retroactive_harvest_bridge_threads.py` (uncommitted).

Implements:
- `extract_thread_stem()` — full filename stem before final `-NNN` segment.
- `group_orphans_by_strict_stem()` — no prefix merging; retired parent scope
  threads stay distinct from child implementation/editplan threads.
- `parse_active_index()` — structured INDEX.md parse.
- `collect_compressed_bridge_threads()` — INDEX Phase-1 + strict-stem
  Phase-2 orphan grouping.
- `compute_active_bridge_thread_coverage()` — distinct-thread-name-set
  formula (numerator and denominator both sets). Cannot exceed 100%.
- `build_thread_summary()` — per-thread summary content with version trail.
- `run_sweep()` — end-to-end dry-run/execute with JSON output schema
  matching `-004`.

Default mode: `--dry-run` (no DB mutation). `--execute` required for
Phase 4. Exit code 1 if execute-mode inserts produce warnings.

**Phase 2b — Tests: COMPLETE.**

New files (uncommitted):
- `tests/scripts/__init__.py`
- `tests/scripts/conftest.py`
- `tests/scripts/test_retroactive_harvest_bridge_threads.py`

24/24 tests pass. Coverage:
- 4 parametrized prefix-pair collision tests (the 4 real pairs from Codex
  `-003` addendum).
- Coverage-formula tests: empty index, zero coverage, full coverage,
  duplicate wildcard DELIBs counted as one, >100% impossible, legacy
  file-level rows not counted as canonical coverage, partial coverage.
- Idempotence test (stub DB): second `run_sweep(execute=True)` produces
  zero new inserts; exactly one canonical wildcard row ends up in the DB.
- Raw transcript exclusion test (source inspection): script contains no
  reference to `.claude/projects/` or `.jsonl`.
- INDEX parsing, thread-stem extraction edge cases.

**Phase 3a — Dry-run: COMPLETE.**

Command:
```
python scripts/retroactive_harvest_bridge_threads.py --sample 8 \
  --output independent-progress-assessments/bridge-automation/dry-runs/da-harvest-coverage-dryrun-2026-04-17.json
```

Full JSON output saved at:
`independent-progress-assessments/bridge-automation/dry-runs/da-harvest-coverage-dryrun-2026-04-17.json`

## Dry-Run Summary (for owner review)

```
mode:                                dry-run
candidate_threads:                   96
  active_threads:                    82
  orphan_threads:                    14
existing_canonical_wildcard_matches: 0    (no existing row has matching content_hash)
existing_legacy_file_level_matches:  56   (untouched; not counted in coverage)
new_compressed_inserts_planned:      96
new_compressed_inserts_applied:      0    (dry-run)
skip_reasons:                        {}
warning_count:                       0
coverage_before_pct:                 0.0   (active VERIFIED threads with canonical wildcard DELIB)
coverage_after_pct_projected:        100.0
```

Legacy file-level coverage (informational, not used by doctor metric):
- 9 threads have any legacy file-level row.
- 9 threads have legacy rows but no canonical wildcard row.
  (Expected — all 56 legacy rows predate this workstream.)

Coverage math (distinct thread-name SETS per Codex Finding 1):
- Denominator = 79 active-VERIFIED threads (82 active minus 3 with
  latest_status != VERIFIED).
- Numerator before = 0 (the 3 pre-existing wildcard rows — DELIB-0716,
  0717, 0718 — map to threads that are either retired from INDEX or not
  currently VERIFIED, so they don't intersect the denominator).
- Numerator after projected = 79 (every active-VERIFIED thread gets its
  own canonical wildcard row).

Sample inserts (first 8, showing heterogeneous thread sizes and statuses):
- `gtkb-da-harvest-coverage-implementation` — 5 versions, GO, active
- `gtkb-canonical-terminology-surface-implementation` — 11 versions, REVISED, active
- `gtkb-start-here-adopter-rewrite-implementation` — 8 versions, NO-GO, active
- `gtkb-managed-artifact-registry` — 10 versions, VERIFIED, active
- `agent-red-cto-cleanup` — 10 versions, VERIFIED, active
- `bridge-spawn-revalidation` — 10 versions, VERIFIED, active
- `post-phase-a-prioritization` — 6 versions, VERIFIED, active
- `gtkb-azure-enterprise-readiness-taxonomy` — 8 versions, VERIFIED, active

## Evidence Against Codex GO Conditions

| Condition | Evidence |
|-----------|----------|
| 1. Dry-run JSON + owner approval before `--execute` | Dry-run JSON saved; **awaiting owner approval**. |
| 2. Raw `*.jsonl` transcripts not read | Source inspection test `TestTranscriptExclusion` passes; grep of `scripts/retroactive_harvest_bridge_threads.py` confirms no `.claude/projects/` or `.jsonl` references. |
| 3a. Orphan prefix-pair separation (4 real pairs) | `TestOrphanGrouping.test_prefix_pairs_remain_distinct` parametrized over the 4 real pairs; all pass. |
| 3b. Legacy file-level rows not counted as canonical | `TestCoverageFormula.test_legacy_file_level_rows_do_not_count_as_covered` passes. |
| 3c. Duplicate wildcard DELIBs count as one thread | `TestCoverageFormula.test_duplicate_wildcard_delibs_count_as_one` passes. |
| 3d. Idempotent second retroactive run = 0 new inserts | `TestIdempotence.test_second_run_inserts_zero_rows` passes. |
| 3e. Warning-above-baseline ALARM behavior | DEFERRED to Phase 7 (flag-gated loud-wrap rollout). Not exercised in this spawn. |
| 3f. Doctor threshold behavior (WARN/ERROR) | DEFERRED to Phase 6 (GT-KB doctor extension). Not exercised in this spawn — GT-KB is on a dirty feature branch. |
| 4. Post-run coverage evidence | Will be produced by Phase 4 `--execute` run JSON. |
| 5. `gt project doctor` on Agent Red | DEFERRED to Phase 6. |

## What Is NOT Yet Done

- **Phase 4 — Live `--execute`:** requires **owner approval of this dry-run**
  output. Running `--execute` mutates Agent Red DA by inserting 96
  canonical wildcard rows.
- **Phase 5 — Ongoing harvest extension:** modifying
  `scripts/harvest_session_deliberations.py` to emit thread-level rows
  going forward (with flag-gated rollout).
- **Phase 6 — GT-KB doctor + coverage helper:** adding
  `compute_active_bridge_thread_coverage()` to the product and
  `_check_da_harvest_coverage()` to `run_doctor()`. **Blocked** because
  GT-KB worktree is on branch `feat/start-here-adopter-rewrite` with
  uncommitted changes; Phase 6 work should land on GT-KB `main` via a
  separate commit sequence after that branch lands or is parked.
- **Phase 7 — Loud-wrap rollout.**
- **Phase 8 — Post-implementation report + Codex VERIFIED.**

## Owner Gate — Required Decision

Before Phase 4 executes, the owner must decide:

1. **Approve:** "Proceed with `--execute`" — Prime runs
   `python scripts/retroactive_harvest_bridge_threads.py --execute` and
   inserts 96 canonical wildcard rows into Agent Red DA.
2. **Request changes:** adjust any of (a) scope of inserts (e.g. exclude
   orphan threads from this first run), (b) summary content format,
   (c) sample inserts, (d) warning handling.
3. **Defer:** hold `--execute` until GT-KB Phase 6 doctor check lands so
   coverage can be measured by the product path rather than a local helper.

## Verification Commands Used

```
python scripts/retroactive_harvest_bridge_threads.py --sample 8 --output <path>
python -m pytest tests/scripts/test_retroactive_harvest_bridge_threads.py -q
python -c "import sys; sys.path.insert(0, 'tools/knowledge-db'); from db import KnowledgeDB; ..."
```

## Uncommitted Files

- `scripts/retroactive_harvest_bridge_threads.py` (new, 320 lines)
- `tests/scripts/__init__.py` (new)
- `tests/scripts/conftest.py` (new)
- `tests/scripts/test_retroactive_harvest_bridge_threads.py` (new, 24 tests)
- `independent-progress-assessments/bridge-automation/dry-runs/da-harvest-coverage-dryrun-2026-04-17.json` (new, dry-run artifact)
- `bridge/gtkb-da-harvest-coverage-implementation-006.md` (this file)

These will be committed together as a single Phase 1-3 commit after owner
approves the dry-run and `--execute` completes cleanly (or as part of the
post-implementation commit that also includes Phases 4-8).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
