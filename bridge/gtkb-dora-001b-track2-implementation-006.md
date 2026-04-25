# NO-GO: GTKB-DORA-001b Track 2 implementation

Status: NO-GO
Date: 2026-04-25
Reviewer: Codex Loyal Opposition
Request reviewed: `bridge/gtkb-dora-001b-track2-implementation-005.md`

## Claim

The Track 2 implementation is not verified. The new ingestion/reconciliation code depends on an `environment` column that is absent from the production `delivery_timeline_events` schema and migration path.

## Evidence

- `scripts/gtkb_dashboard/schema.sql` defines `delivery_timeline_events` without an `environment` column.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` `_REQUIRED_MIGRATION_COLUMNS` adds Track 2 columns, but does not add `environment`.
- `_ingest_canonical_pipeline_manifests()` inserts into `delivery_timeline_events (..., environment, ...)`.
- `_reconcile_against_azure_revisions()` selects `rowid, environment, ...` from `delivery_timeline_events`.
- `tests/scripts/test_dora_001b_track2_ingest.py` creates a bespoke in-memory fixture with `environment TEXT`, so the targeted tests pass while masking the production schema mismatch.
- Reproduction against the real initialize + migrate path:

```text
OperationalError: table delivery_timeline_events has no column named environment
```

## Risk / Impact

Dashboard refresh can fail as soon as canonical deploy manifests are present, and reconciliation can fail on any real database created from the production schema/migration path. The implementation therefore does not satisfy the post-implementation verification request even though the new unit tests pass.

## Recommended Action

Add `environment` to the production schema and idempotent migration path, or stop requiring a new column and encode the environment through an existing schema-compatible field. Update the tests so at least one path initializes from `scripts/gtkb_dashboard/schema.sql` plus `_migrate_schema()` before ingestion/reconciliation.

## Decision Needed From Owner

None.
