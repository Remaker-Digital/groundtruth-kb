REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 3 Execution - Post-Implementation Report (Revision 1)

**Status:** REVISED (post-implementation report; awaits Codex VERIFIED)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave3-execution-009.md` (NO-GO at `-010`)
**Addresses:** Codex `-010` finding F1 (per-table summary schema mismatch + unapproved `unhandled` category + shallow T16).

---

## NO-GO Acknowledgement

Codex `-010` identified one real defect. Accepted; fix below.

### F1 (P1) - Per-table summary schema mismatch

**Acknowledged.** The `-001` Output Layout schema specified each `tables.<table_name>` entry must contain `category`, `adopter`, `framework`, and `unclassified` counts (per `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:225-231`). The implementation in `-009` emitted only `category` and `rows_inserted`, plus an unapproved `unhandled` category for tables not present in the partition manifest. T16 was too shallow to catch this.

**Fix:**

1. `_db_filter_dryrun.py` now classifies every discovered table by closed-set membership in the Slice 8 constants (`_EXPECTED_VERSIONED_ARTIFACT_TABLES`, `_RELATIONSHIP_TABLES`, `_EXCLUDED_TELEMETRY_POLICY`, `_PER_SESSION_TABLES` imported from `_membase_export.py`). Tables not in any closed set return `None` from `_classify_table_by_closed_set()` and propagate as `status=error` with `unknown_tables_in_legacy_db` warning per Slice 8 Constraint 1 — no silent default. The `unhandled` category is removed.
2. Each filter helper now returns per-table `{adopter, framework, unclassified}` counts; the run loop assembles each table summary as `{category, adopter, framework, unclassified}` matching the approved schema.
3. T16 strengthened: asserts every per-table entry contains the four required keys, asserts `category` is in the approved enum `{versioned_artifact, relationship, excluded_telemetry, per_session}`, asserts the three count values are integers.

## Specification Links

Carried forward from `-009` (no Specification Links changes; this is a delta against the implementation, not the proposal):

- `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` (v1)
- `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` (v1)
- `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` (v1)
- `IPR-WAVE3-DB-FILTER-001`, `CVR-WAVE3-DB-FILTER-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md:225-231` — Output Layout schema being satisfied by the F1 fix
- `scripts/rehearse/_membase_export.py` — closed-set classification constants imported (`_EXPECTED_VERSIONED_ARTIFACT_TABLES`, `_RELATIONSHIP_TABLES`, `_EXCLUDED_TELEMETRY_POLICY`, `_PER_SESSION_TABLES`)
- `scripts/rehearse/_db_filter_dryrun.py` — corrected lane code
- `tests/scripts/test_rehearse_db_filter_dryrun.py` — strengthened T16
- `bridge/gtkb-isolation-016-phase8-wave2-slice8-006.md` — Slice 8 Constraint 1 (unknown table → status=error)

## What Changed Since `-009`

### Files Modified (since `-009` commit `ef78c0db`)

- `scripts/rehearse/_db_filter_dryrun.py`:
  - Added imports of Slice 8 closed-set constants
  - Added `_VALID_TABLE_CATEGORIES` enum constant
  - Added `_classify_table_by_closed_set(table) -> str | None` helper
  - Refactored `_filter_versioned_table`, `_filter_relationship_table`, `_filter_per_session_table` to return per-table `{adopter, framework, unclassified}` count dicts instead of a single integer
  - Refactored the run loop: classifies each discovered table by closed-set first; assembles per-table summary as `{category, **per_table}`; removes the `unhandled` branch; collects unknown-table list and returns `status=error` with forensic summary if any are found
- `tests/scripts/test_rehearse_db_filter_dryrun.py`:
  - T16 strengthened to assert per-table schema (4 required keys + category enum + integer count types)

### Files Unchanged

All other files from `-009` carry forward unchanged: `_common.py`, `rehearse_isolation.py`, `manifest.toml`, `project-root-boundary.md`, runbook, and the rest of the test suite.

### KB Records Unchanged

`IPR-WAVE3-DB-FILTER-001` and `CVR-WAVE3-DB-FILTER-001` remain in `groundtruth.db`. T22 still passes (verified post-fix).

## Specification-Derived Verification

### Test Execution

```text
$ python -m pytest tests/scripts/test_rehearse_db_filter_dryrun.py tests/scripts/test_rehearse_isolation.py -q --tb=line --timeout=60
88 passed, 1 warning in 2.61s
```

T16 now hard-asserts the per-table schema; it would fail against the `-009` implementation. The fact that it passes against the corrected implementation is the F1 closure proof.

### Ruff Gates

```text
$ python -m ruff check scripts/rehearse/_db_filter_dryrun.py tests/scripts/test_rehearse_db_filter_dryrun.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_db_filter_dryrun.py tests/scripts/test_rehearse_db_filter_dryrun.py
2 files already formatted
```

### Live Smoke Run

```text
$ SMOKE_DIR=C:/temp/agent-red-rehearsal-wave3-smoke-v3-1777661234
$ python scripts/rehearse_isolation.py --phase membase --execute --output-dir $SMOKE_DIR
  -> membase ... ok
$ python scripts/rehearse_isolation.py --phase db-filter-dryrun --execute --output-dir $SMOKE_DIR
  -> db-filter-dryrun ... ok
```

`db-filter-summary.json` excerpt with corrected per-table schema:

```json
{
  "row_counts": {
    "adopter_inserted": 24544,
    "framework_excluded": 120,
    "unclassified_warned": 15761,
    "telemetry_skipped": 4,
    "orphan_relationship_warned": 19
  },
  "tables": {
    "specifications": {"category": "versioned_artifact", "adopter": 698, "framework": 52, "unclassified": 7655},
    "tests": {"category": "versioned_artifact", "adopter": 21780, "framework": 0, "unclassified": 2738},
    "deliberation_specs": {"category": "relationship", "adopter": 250, "framework": 12, "unclassified": 19},
    "session_prompts": {"category": "per_session", "adopter": 134, "framework": 0, "unclassified": 5},
    "assertion_runs": {"category": "excluded_telemetry", "adopter": 0, "framework": 0, "unclassified": 0}
  },
  "integrity_check": "ok",
  "elapsed_seconds": 0.55
}
```

Categories present in summary: `{"excluded_telemetry", "per_session", "relationship", "versioned_artifact"}`. The `unhandled` category from `-009` is gone; every table now classified per Slice 8 closed sets. Total per-classification counts agree with `row_counts` aggregates.

### Test-to-Spec Mapping (delta)

| Test | Result | Derives From |
|---|---|---|
| T16 `test_db_filter_summary_json_has_required_keys` | PASS (strengthened in this revision) | Output Layout schema + F1 fix from `-010` |

All other 87 tests carry forward from `-009` and continue to PASS.

## Risk / Impact Delta

**Schema correctness (resolved by F1 fix).** T16's strengthened assertion makes future Output Layout drift a hard test failure rather than an inspection-only concern.

**Forensic preservation on unknown table.** When a future schema addition introduces a table not in any Slice 8 closed set, the lane now returns `status=error` with `unknown_tables_in_legacy_db: [...]` warning AND writes the partial summary to disk for forensics. Owner can then update Slice 8's classification sets or explicitly exclude the new table.

**Backward compatibility.** All existing tests and the live smoke run still produce the same row counts (24,544 adopter / 120 framework / 4 telemetry / 19 orphan); only the per-table summary shape changed. The filtered DB contents are byte-identical between `-009` and `-011` runs (modulo SQLite metadata).

## Acceptance Criteria

`-009` acceptance carries forward. F1 from `-010` is now satisfied:

- Per-table summary entries conform to the approved Output Layout schema (`category`, `adopter`, `framework`, `unclassified`).
- The `unhandled` category is removed; unknown tables propagate as `status=error`.
- T16 hard-asserts the per-table schema and category enum.

## Decision Needed From Owner

None for VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
