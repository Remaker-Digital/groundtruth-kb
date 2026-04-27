NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 8 REVISED-1

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice8-003.md`
Scope: MemBase export rehearsal lane proposal for `scripts/rehearse/_membase_export.py`

## Claim

NO-GO. The revised design moves in the right direction by using physical read-only SQLite and version arrays, but its proposed table roster does not match the live `groundtruth.db` schema.

## Evidence

- The revision proposes `_VERSIONED_TABLES` containing `specs`, `op_procedures`, `design_constraints`, `implementation_proposals`, `constraint_verifications`, `env_config`, and `events`.
- Live `groundtruth.db` does not contain those table names. The corresponding live tables include `specifications`, `operational_procedures`, `environment_config`, and `pipeline_events`.
- Live schema includes additional tables the revised proposal does not account for, including `deliberation_specs`, `deliberation_work_items`, `quality_scores`, `session_snapshots`, `spec_quality_scores`, and `test_coverage`.
- Some live tables do not have the proposed `(id, version)` shape, for example `pipeline_events`, `test_coverage`, `deliberation_specs`, and `deliberation_work_items`.
- The revision still claims every artifact table has `(id, version)` with a `UNIQUE(id, version)` constraint, which is not true for the live schema.

## Risk / Impact

Implementing the proposal as written would fail against the live database or silently omit relationship/telemetry tables that may be needed to preserve KB semantics. This would reintroduce the same cutover-risk class as the original sparse-manifest design, just one layer lower.

## Required Revision

- Discover the live table roster from `sqlite_master` and classify tables by shape:
  - versioned artifact tables with `id` and `version`;
  - relationship tables such as `deliberation_specs` and `deliberation_work_items`;
  - telemetry/score tables;
  - explicitly excluded tables with row counts and rationale.
- Use live table names: for example `specifications`, `operational_procedures`, `environment_config`, and `pipeline_events`.
- For non-versioned tables, define preservation/exclusion policy explicitly instead of forcing the version-array schema.
- Add schema-introspection tests using table names that match the current database.

## Decision Needed From Owner

None. Prime needs to revise against the actual `groundtruth.db` schema.
