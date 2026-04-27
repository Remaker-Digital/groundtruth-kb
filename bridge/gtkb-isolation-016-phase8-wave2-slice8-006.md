GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 8 REVISED-2

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice8-005.md`
Scope: MemBase export rehearsal lane proposal for `scripts/rehearse/_membase_export.py`

## Claim

GO, with implementation constraints. The revised proposal corrects the prior live-schema mismatch by discovering tables from `sqlite_master`, using the actual table names, and separating versioned artifacts, relationship rows, telemetry exclusions, and per-session tables.

## Evidence

- Live `groundtruth.db` has 21 non-`sqlite_%` tables, matching the proposal's categories:
  - 12 versioned artifact tables with `id` and `version`: `specifications`, `tests`, `work_items`, `documents`, `operational_procedures`, `deliberations`, `environment_config`, `backlog_snapshots`, `test_plans`, `test_plan_phases`, `test_procedures`, `testable_elements`.
  - 2 relationship tables: `deliberation_specs`, `deliberation_work_items`.
  - 4 telemetry/score tables: `assertion_runs`, `pipeline_events`, `quality_scores`, `test_coverage`.
  - 3 per-session tables: `session_prompts`, `session_snapshots`, `spec_quality_scores`.
- Live high-volume `pipeline_events` has 2,170,976 rows and is appropriately treated as telemetry/excluded with documented policy rather than expanded into the partition manifest.
- The revision retains physical read-only SQLite access and version arrays for versioned artifact tables.

## Required Implementation Constraints

- Unknown discovered tables should produce at least status `error` unless there is a clear, documented reason that `ok` with warning is safe. A cutover partition manifest should not silently proceed past an unclassified database table.
- For each excluded telemetry table, emit `row_count`, `reason`, and `cutover_policy` exactly as proposed.
- Relationship rows must be traceable to parent classification evidence, not just table-level policy. If a relationship row references a missing parent, surface it as a warning or error with row evidence.
- Per-session rows must include the session ownership signal used for classification. If session ownership cannot be determined, classify as `unclassified`, not adopter by default.
- Tests must use live table names (`specifications`, `operational_procedures`, `environment_config`, `pipeline_events`) and include at least one unknown-table fixture.

## Risk / Impact

Moderate but acceptable with constraints. This lane is now pointed at the real database shape; the remaining risk is ensuring unknown or parentless rows do not become silent cutover omissions.

## Decision Needed From Owner

None.
