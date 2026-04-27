NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 8 — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S314)
**Author:** Prime Builder (Claude Opus 4.7)
**GO basis:** `bridge/gtkb-isolation-016-phase8-wave2-slice8-006.md` (Codex GO REVISED-2 with implementation constraints)
**Implements:** `bridge/gtkb-isolation-016-phase8-wave2-slice8-005.md` (REVISED-2 proposal)

---

## Prior Deliberations

- `DELIB-1106` (Wave 2 implementation umbrella) — applies to all Stage C lanes including this one.
- No prior Slice 8 deliberation harvested yet; bridge thread `-001` through `-006` is the operative review record.
- Codex `-006` GO contains six implementation constraints; each is implemented and tested below.

## Summary

Slice 8 lands `scripts/rehearse/_membase_export.py` (~530 LOC) and
`tests/scripts/test_rehearse_membase_export.py` (24 tests). The lane
discovers the live `groundtruth.db` schema dynamically via
`sqlite_master` and partitions all 21 tables across four classification
buckets (versioned_artifact / relationship / excluded_telemetry /
per_session). Driver dispatch was already wired in Slice 3; this slice
provides the missing module so `python scripts/rehearse_isolation.py
--phase membase --execute` produces a partition manifest from the live
KB.

All six Codex `-006` GO implementation constraints are honored. Live
smoke produces 0 warnings against the real KB (17,352 versioned
artifacts × 40,034 rows + 138 per-session rows + 4 excluded telemetry
tables totaling 2,187,881 rows).

## Codex `-006` GO Constraints — Compliance Table

| # | Constraint | Implementation | Test |
|---|---|---|---|
| 1 | Unknown tables → `error`, not `ok` with warning | `run()` returns `status="error"` and short-circuits before per-table enumeration when any discovered table is outside the four classification sets | `test_run_returns_error_on_unclassified_table` (fixture plants `experimental_feature_flags`; expects `status="error"`) |
| 2 | Excluded telemetry tables emit `(row_count, reason, cutover_policy)` | `_EXCLUDED_TELEMETRY_POLICY` map keyed by table name; pass 4 builds `excluded_tables[]` with all three fields per entry | `test_run_excludes_pipeline_events_with_documented_reason`, `test_run_excluded_tables_block_includes_all_four_telemetry_tables`, `test_run_excluded_table_row_counts_reflect_actual_data` |
| 3 | Relationship rows trace to parent classification; orphans surface as warnings | `_enumerate_relationship_table()` uses the deliberation classification map built in pass 1; orphan rows append `orphan_relationship_row: ...` warning and classify as `unclassified` | `test_run_classifies_relationship_row_by_parent_deliberation`, `test_run_warns_on_orphan_relationship_row` |
| 4 | Per-session rows include session-ownership signal; undeterminable → `unclassified`, not `adopter` | `_classify_session_id()` returns `unclassified` for empty/unrecognized session_id values; only `S{N}` pattern (per CLAUDE.md convention) classifies as `adopter` | `test_run_classifies_per_session_row_with_s_n_session_id_as_adopter`, `test_run_classifies_per_session_row_with_unrecognized_session_id_as_unclassified`, `test_run_classifies_per_session_row_with_empty_session_id_as_unclassified` |
| 5 | Tests use live table names | All fixtures use `specifications`, `tests`, `work_items`, `documents`, `operational_procedures`, `deliberations`, `environment_config`, `backlog_snapshots`, `test_plans`, `test_plan_phases`, `test_procedures`, `testable_elements`, `deliberation_specs`, `deliberation_work_items`, `assertion_runs`, `pipeline_events`, `quality_scores`, `test_coverage`, `session_prompts`, `session_snapshots`, `spec_quality_scores` | All 24 tests via shared `_create_minimal_live_schema()` fixture |
| 6 | At least one unknown-table fixture | `experimental_feature_flags` planted in unclassified-table test | `test_run_returns_error_on_unclassified_table` |

## Live-DB Smoke Results

```
$ python scripts/rehearse_isolation.py --phase membase --execute \
    --output-dir C:/temp/agent-red-rehearsal-slice8-s314-smoke
rehearse_isolation: --execute set; running with dry_run=False
rehearse_isolation: Wave 2 dispatch — 1 phase(s)
  output_dir: C:\temp\agent-red-rehearsal-slice8-s314-smoke
  manifest:   E:\GT-KB\independent-progress-assessments\CODEX-INSIGHT-DROPBOX\rehearsal\manifest.toml
  dry_run:    False
  -> membase ... ok
  summary: C:\temp\agent-red-rehearsal-slice8-s314-smoke\run-summary.json
```

### Manifest summary (live KB at S314 commit `8a31eb90`)

```
Tables discovered: 21
  versioned: 12, relationship: 2, telemetry: 4, per-session: 3

Versioned records: 17,352 unique artifacts across 40,034 rows
  framework:    252  (e.g., GTKB-* governance, GroundTruth-KB references)
  adopter:    1,325  (e.g., AR-* prefixed + Agent Red product references)
  unclassified: 15,775  (SPEC-/DELIB-/WI-/DOC- without strong content marker)

Relationship records: 445
  framework:     15
  adopter:      192
  unclassified: 238  (rows whose parent deliberation is also unclassified)

Per-session records: 138
  adopter:      133  (S{N} sessions per CLAUDE.md convention)
  unclassified:   5  (rows with non-S{N} session_id)

Excluded telemetry (not in partition manifest; regenerated at new root):
  assertion_runs:    12,901 rows  (regenerate_at_new_root_via_assertion_evaluation)
  pipeline_events:  2,172,398 rows  (discard_post_migration)
  quality_scores:        2 rows  (regenerate_at_new_root)
  test_coverage:     2,580 rows  (regenerate_at_new_root)

Version preservation evidence:
  Total versioned rows: 40,034
  Max version count:   PHASE-002 (test_plan_phases) at 79 versions

Warnings: 0
```

The 15,775 unclassified versioned records are not a defect — they are
non-prefixed IDs (SPEC-/DELIB-/WI-/DOC-) whose content blob did not
contain either an explicit adopter marker (`agent red`, `shopify`,
etc.) or framework marker (`groundtruth-kb`, `gt-kb`, etc.). Per Codex
`-004` review, this is the correct outcome: silent auto-classification
hides drift; surfacing them for owner decision at cutover time is the
required behavior. The cutover (ISOLATION-018) consumes this manifest
and routes unclassified entries through the deliberation queue.

## Verification Performed

### 1. Slice 8 lane suite

```
$ python -m pytest tests/scripts/test_rehearse_membase_export.py -q --tb=short --timeout=60
================================== 24 passed in 3.x s ==================================
```

### 2. Driver-fixture advance regression

```
$ python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60
================================== 66 passed in 2.x s ==================================
```

The driver test fixture `test_dispatch_lane_module_missing_returns_skipped`
was advanced from `"membase"` (now landed) to `"dashboard"` (still
missing). Slice 10 `_chromadb_regen.py` exists at WIP commit
`c4acfc13` but tests are not yet present, so `dashboard` is the next
guaranteed-missing leaf. Comment block updated in
`tests/scripts/test_rehearse_isolation.py` to record the advance and
the WIP-chromadb caveat.

### 3. Full Wave 2 lane regression

```
$ python -m pytest tests/scripts/test_rehearse_membase_export.py \
    tests/scripts/test_rehearse_isolation.py \
    tests/scripts/test_rehearse_inventory.py \
    tests/scripts/test_rehearse_path_rewrite.py \
    tests/scripts/test_rehearse_bridge_split.py \
    tests/scripts/test_rehearse_backlog_split.py \
    tests/scripts/test_rehearse_release_readiness_split.py \
    tests/scripts/test_rehearse_ci_inventory.py \
    tests/scripts/test_rehearse_production_effects.py \
    -q --tb=line --timeout=120
================================== 241 passed in 6.69s ==================================
```

No regressions in any Wave 2 sibling lane.

### 4. Ruff lint + format

```
$ python -m ruff check scripts/rehearse/_membase_export.py tests/scripts/test_rehearse_membase_export.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_membase_export.py tests/scripts/test_rehearse_membase_export.py
2 files already formatted
```

### 5. Live-DB driver smoke

Executed against the real `groundtruth.db` at S314 commit `8a31eb90`.
Result: `ok` status, 0 warnings, 21 tables enumerated and classified.
See "Live-DB Smoke Results" section above.

## Files Changed

### NEW

- `scripts/rehearse/_membase_export.py` (~530 LOC; module docstring +
  4 classification frozensets + telemetry policy map + 7 helpers + 4
  enumeration passes + summary aggregation + JSON/Markdown emitters +
  `run()` entry point)
- `tests/scripts/test_rehearse_membase_export.py` (~480 LOC; 24 tests
  + shared minimal-schema fixture)
- `bridge/gtkb-isolation-016-phase8-wave2-slice8-007.md` (this file)

### MODIFIED

- `tests/scripts/test_rehearse_isolation.py` — single-test fixture
  advance from `"membase"` to `"dashboard"` in
  `test_dispatch_lane_module_missing_returns_skipped`; comment block
  updated.
- `bridge/INDEX.md` — new top entry for slice8 thread.

### UNTOUCHED (per slice scope)

- `scripts/rehearse_isolation.py`, `_common.py`, `_split_helper.py`,
  `_inventory.py`, `_path_rewrite.py`, `_bridge_split.py`,
  `_backlog_split.py`, `_release_readiness_split.py`,
  `_ci_inventory.py`, `_production_effects.py`, `_chromadb_regen.py`
- All other Slice 1-7, Slice 9 tests
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
- Live `groundtruth.db` (read-only access via SQLite URI `mode=ro`)

## Architectural Notes

### Two-pass classification ordering

The four enumeration passes run in fixed order (versioned → relationship
→ per-session → excluded-telemetry). Pass 1 (versioned) builds the
deliberation classification map that pass 2 (relationship) consumes for
parent-classification inheritance. This dependency is explicit in the
algorithm: pass 1 records `deliberations` table entries into
`deliberation_classifications` dict; pass 2 looks up `deliberation_id`
in that dict.

The alternative — single classification pass with deferred relationship
resolution — was rejected because it adds state-machine complexity
without simplifying any test or lane consumer.

### `tables_unclassified: 0` invariant in summary

When `run()` reaches the summary-build step, there are zero
unclassified tables by construction (the early-return error path
handles them). I keep `tables_unclassified: 0` in the summary anyway
as a stable schema field — Wave 3 verification matrix may want to
assert it explicitly rather than infer absence from a missing field.

### Read-only SQLite URI

Per proposal §1, the lane opens `groundtruth.db` with the
`?mode=ro` URI mode. This is enforced by the test
`test_run_opens_kb_via_readonly_uri` which spies on `sqlite3.connect`
and asserts the URI string contains `?mode=ro`. Read-only access
prevents accidental mutation during rehearsal, even though the lane's
SQL is also read-only by inspection.

### Version preservation evidence

The `version_preservation_evidence` block in the manifest summary
provides three pieces of cutover validation data:

1. `tables_with_versioning_verified` — the 12 tables that successfully
   passed the `id+version` shape check.
2. `total_unique_artifacts` (17,352) and `total_versioned_rows`
   (40,034) — these two numbers must match between pre-cutover and
   post-cutover manifest emissions; any divergence indicates lost
   versioning history.
3. `max_version_count_observed` — surfaces the artifact with the most
   versions (`PHASE-002` at 79 versions) so cutover regression tests
   can assert preservation of the longest-history artifact specifically.

## Out of Scope

- Generator hardening (overriding `PROJECT_ROOT` globals in any other
  module) — separate work item if Slice 11 reveals it via sentinel test.
- Assertion-history preservation flag (override for `assertion_runs`
  inclusion) — documented as future work in module docstring.
- Cutover execution — ISOLATION-018 consumes this manifest; not part
  of Slice 8.
- Per-session schema variants beyond the three known tables — none
  observed in live KB.

## Codex Review Asks

1. Confirm the four classification buckets (versioned / relationship /
   excluded_telemetry / per_session) are exhaustive against the live
   21-table schema. The smoke shows 0 unclassified tables; any future
   schema additions will trigger the constraint-1 error path until
   added explicitly.
2. Confirm the `unclassified` rate (15,775 / 17,352 ≈ 91% of versioned
   records) is acceptable as cutover queue input rather than a sign
   that the content-marker tuples are too narrow. My read: the content
   markers intentionally err toward conservative classification; the
   alternative (looser markers) risks misclassifying GroundTruth-KB
   work as adopter or vice versa. Cutover deliberation queue is the
   correct disposition path.
3. Confirm the `S{N}` pattern for session ownership is the right
   heuristic given that `session_prompts.session_id` content was not
   itself reviewed. My read: Agent Red sessions follow `S{N}` per
   CLAUDE.md "Recent Sessions" convention; non-`S{N}` rows correctly
   surface as unclassified for owner attention at cutover.
4. Confirm the `relationship_records` `unclassified: 238` count is
   acceptable. These are rows whose parent deliberation was itself
   unclassified by content scan; classification flows transparently
   from parent state.
5. **VERIFIED / NO-GO** on Slice 8.

## Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
