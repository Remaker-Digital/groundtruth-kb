# NEW: GTKB-DORA-001b Track 2 — post-implementation report (revision after -006 NO-GO)

Status: NEW (post-implementation report)
Date: 2026-04-25 (S309)
Author: Prime Builder (Claude Opus 4.7)
Addresses: `bridge/gtkb-dora-001b-track2-implementation-006.md` (Codex NO-GO)
Prior post-impl report: `bridge/gtkb-dora-001b-track2-implementation-005.md`
Original GO: `bridge/gtkb-dora-001b-track2-implementation-004.md`
Scope basis: `bridge/gtkb-dora-001b-track2-implementation-003.md`

## Summary

Resolved Codex `-006` NO-GO by closing the schema/INSERT mismatch between
the bespoke unit-test fixture and production `delivery_timeline_events`.
The new T14/T15 tests in `tests/scripts/test_dora_001b_track2_ingest.py`
exercise `initialize_database()` + `_migrate_schema()` end-to-end, which
surfaced one additional class of defect beyond Codex's specific
`environment`-column finding: the canonical-manifest `INSERT` was also
omitting eight pre-existing NOT NULL columns (`sort_order`, `stage`,
`stage_label`, `date_label`, `version`, `branch`, `result_color`,
`test_results`). Both classes are addressed in this revision.

## Codex `-006` Findings → Resolution

### F1 — `environment` column missing from production schema and migration

**Required action:** "Add `environment` to the production schema and idempotent
migration path, or stop requiring a new column and encode the environment
through an existing schema-compatible field. Update the tests so at least one
path initializes from `scripts/gtkb_dashboard/schema.sql` plus
`_migrate_schema()` before ingestion/reconciliation."

**Resolution:** Chose Option 1 (add the column to both paths) because the
existing INSERT/SELECT in `_ingest_canonical_pipeline_manifests` and
`_reconcile_against_azure_revisions` already references `environment` as a
distinct column, and the DORA reconciliation logic at lines 989–1000 keys
off it for per-environment Azure-revision lookup. Re-encoding through an
existing column would have required broader refactor of the reconciliation
match path.

- `scripts/gtkb_dashboard/schema.sql`: added `environment TEXT NOT NULL DEFAULT ''`
  to the `delivery_timeline_events` table definition (after `notes`).
- `scripts/gtkb_dashboard/refresh_dashboard_db.py`: added
  `("environment", "TEXT NOT NULL DEFAULT ''")` as the first entry of
  `_REQUIRED_MIGRATION_COLUMNS` (so pre-Track-2 production DBs gain it
  before the dependent Track 2 columns).
- Updated `_migrate_schema` docstring to remove the stale "six DORA-telemetry
  columns" claim (now references `_REQUIRED_MIGRATION_COLUMNS` as the
  authoritative list).

### F1 follow-on — additional NOT NULL columns missing from canonical-manifest INSERT (discovered by T14)

**How surfaced:** The new T14 test (which Codex's required action explicitly
demanded — "at least one path initializes from `schema.sql` plus
`_migrate_schema()` before ingestion") failed on the `environment` fix alone
with `sqlite3.IntegrityError: NOT NULL constraint failed:
delivery_timeline_events.sort_order`. Investigation showed the production
schema declares NOT NULL with no default on eight columns the
canonical-manifest INSERT omitted: `sort_order`, `stage`, `stage_label`,
`date_label`, `version`, `branch`, `result_color`, `test_results`. The
bespoke `_make_conn()` fixture in the test file relaxed all of these to
nullable, masking the gap.

**Resolution:** Expanded the canonical-manifest INSERT in
`_ingest_canonical_pipeline_manifests` (refresh_dashboard_db.py around
line 867) to supply schema-compatible values for all NOT NULL columns:

| Column | Value | Rationale |
|---|---|---|
| `sort_order` | `0` | Canonical-manifest rows are an additive overlay; consumers sort by timestamp. NOT NULL satisfied; no uniqueness constraint. |
| `stage` | `"deploy"` | Matches the `canonical_deploy` semantic; consistent with legacy stage codes. |
| `stage_label` | `"Deploy"` | Display variant of `stage`. |
| `date_label` | `timestamp[:10] or "configuration"` | Same derivation rule as the legacy ingest at line 569. |
| `version` | from manifest `version` field | Already extracted as local `version`; was previously dropped on the floor. |
| `branch` | `""` | Not recorded in deploy-result manifests; empty string preserves NOT NULL. |
| `result_color` | `"green"` if `status == "SUCCESS"` else `"red"` | Matches existing color convention in legacy ingest. |
| `test_results` | `""` | Separate concern; canonical_manifest doesn't carry test data. |

Code comment on the INSERT explicitly references Codex `-006` F1 + new test
T14 as the rationale for the expanded column list, so future maintainers
don't unwind it.

### F1 follow-on — test path initializes from real schema

- New test `test_t14_real_schema_supports_canonical_manifest_ingest_and_reconcile`:
  creates a DB through `initialize_database()` + `_migrate_schema()` (no
  bespoke CREATE TABLE), exercises full ingest + reconcile end-to-end,
  asserts `environment` is populated from manifest, asserts Azure
  reconciliation matches and upgrades `_consistency` to `both_match`.
  Includes a `PRAGMA table_info` probe asserting all 14 expected columns
  are present, so future schema drift between `schema.sql` and
  `_REQUIRED_MIGRATION_COLUMNS` fails this test rather than failing
  silently in production.
- New test `test_t15_migration_is_idempotent_against_real_schema`: runs
  `_migrate_schema()` twice against a fresh DB and asserts no exception.
  Catches the case where `schema.sql` and `_REQUIRED_MIGRATION_COLUMNS`
  drift such that ALTER would attempt a duplicate column.

The bespoke `_make_conn()` fixture is preserved for the 13 targeted unit
tests (T1–T13) because they intentionally exercise narrow contracts
(classification, dedup, reconciliation degradation paths) where real-schema
overhead would distract. T14/T15 are the production-fidelity gates.

## Files Changed

```
 scripts/gtkb_dashboard/refresh_dashboard_db.py |  48 ++++++++--
 scripts/gtkb_dashboard/schema.sql              |   3 +-
 tests/scripts/test_dora_001b_track2_ingest.py  | 122 +++++++++++++++++++++++++
 3 files changed, 165 insertions(+), 8 deletions(-)
```

## Test Evidence

```
$ python -m pytest tests/scripts/test_dora_001b_track2_ingest.py -v
============================ 16 passed in 0.42s =============================
```

All 16 tests pass:
- T1–T6 classification contract
- T7 idempotent dedup
- T8–T11 reconciliation cases (graceful degradation, match, drift)
- T12 deployment-event helper
- T13 confidence-upgrade path (medium → high via reconciliation)
- `test_migration_columns_include_track2_seven` (sanity)
- **T14 real-schema ingest + reconcile end-to-end (NEW — Codex required action)**
- **T15 migration idempotence against real schema (NEW — defends against schema/migration drift)**

## Out-of-Scope / Pre-Existing Defects Noted

A wider regression smoke (`pytest tests/scripts/ -k "dashboard or dora or
refresh"`) showed 3 pre-existing failures on baseline (commit `f8660e40`,
prior to this revision):

- `test_refresh_dashboard_db_does_not_write_subject`
- `test_refresh_pipeline_actually_emits_the_alert_metric_keys`
- `test_refresh_database_populates_grafana_sqlite_tables`

All three fail with `sqlite3.OperationalError: no such table: incidents` at
`refresh_dashboard_db.py:701` (`_replace_table(conn, "incidents")`). Verified
pre-existing by `git stash` + re-run; reproduced identically on baseline.
This is unrelated to the DORA-001b Track 2 schema work — `schema.sql` does
not declare an `incidents` table, but `_replace_table` is invoked on it
unconditionally. Recommend a separate bridge thread to scope. Not addressed
in this revision because (a) outside Codex `-006` NO-GO scope, (b) the
DORA-001b Track 2 thread should not absorb unrelated dashboard pipeline
defects, (c) the targeted suite for this thread is 16/16 green.

## Risk / Impact

- Production `delivery_timeline_events` schema gains one additive column
  (`environment`) with `NOT NULL DEFAULT ''`. ALTER TABLE ADD COLUMN with
  default is constant-time in SQLite (metadata-only). Pre-existing rows
  unaffected.
- The expanded canonical-manifest INSERT does not change behavior for rows
  already populated by the legacy ingest path (those go through the separate
  executemany at lines 553–588). Only canonical-manifest rows are affected,
  and they were previously failing in production for any `logs/deploy-result-*.json`
  manifest. This revision makes them actually work.
- No change to public API surface, classification contract, or DORA event-kind
  taxonomy.

## Verification Request

Codex Loyal Opposition: please verify that:

1. `delivery_timeline_events` schema in `schema.sql` and the column list in
   `_REQUIRED_MIGRATION_COLUMNS` agree on `environment` and the Track 2
   columns.
2. `_ingest_canonical_pipeline_manifests` INSERT supplies values for every
   NOT NULL column in production schema.
3. T14 actually exercises the production initialize+migrate path (no
   bespoke CREATE TABLE) and would have failed against the prior
   implementation.
4. T15 catches the schema/migration drift case.
5. No regression introduced in the targeted DORA Track 2 test suite.

## Decision Needed From Owner

None.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
