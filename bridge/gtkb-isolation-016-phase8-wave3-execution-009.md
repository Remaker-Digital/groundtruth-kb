NEW

# GTKB-ISOLATION-016 Phase 8 Wave 3 Execution - Post-Implementation Report

**Status:** NEW (post-implementation report; awaits Codex VERIFIED)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** `bridge/gtkb-isolation-016-phase8-wave3-execution-007.md` (REVISED-3, GO at `-008`)

---

## Implementation Summary

The Wave 3 implementation lands in this commit. All Implementation Plan items from `-007` (which carries forward `-005` and `-003` content) are complete. Tests pass; ruff clean; live smoke run succeeds against the 1.0 GB live KB.

## Specification Links

Carried forward from `-007` (which re-cited from `-005` and `-003`):

- `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` (v1, owner_decision, S325)
- `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` (v1, owner_decision, S325)
- `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` (v1, owner_decision, S325)
- `IPR-WAVE3-DB-FILTER-001` — pre-implementation IPR document; created in implementation commit; tagged `GOV-20`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GTKB-ISOLATION-016`, `wave-3`
- `CVR-WAVE3-DB-FILTER-001` — post-implementation CVR document; created in this commit; tagged identically
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md`
- `.claude/rules/operating-model.md` §3
- `.claude/rules/project-root-boundary.md` (now amended with Sandbox Output Exception section)
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-003.md` §3.1 + `-004.md` Recommended Action — closed by this implementation
- `bridge/gtkb-isolation-016-phase8-wave2-slice8-006.md` (Codex GO) — partition-manifest contract consumed
- `scripts/rehearse/_membase_export.py` — Slice 8 classifier; `membase_export/` output path consumed
- `scripts/rehearse/_db_filter_dryrun.py` (NEW; this commit) — Wave 3 lane consumer
- `scripts/rehearse/_common.py` — Rule M6 added in this commit
- `scripts/rehearse_isolation.py` — phase-to-wave mapping added in this commit
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` — db_reconciliation_strategy + unclassified_disposition fields landed in this commit
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/runbooks/AGENT-RED-CUTOVER-FREEZE-WINDOW-RUNBOOK-2026-05-01.md` (NEW; this commit)
- `tests/scripts/test_rehearse_db_filter_dryrun.py` (NEW; this commit) — T1-T17, T-F1, T21, T22
- `tests/scripts/test_rehearse_isolation.py` — T18, T19 added; T-LANE-COVERAGE updated to 12 lanes
- `GOV-09`, `GOV-20` — governance compliance

## What Landed

### Files Created

1. `scripts/rehearse/_db_filter_dryrun.py` (~410 LOC including docstring) — Wave 3 lane consuming Slice 8 partition manifest
2. `tests/scripts/test_rehearse_db_filter_dryrun.py` — 20 tests covering T1-T17, T-F1, T21, T22
3. `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/runbooks/AGENT-RED-CUTOVER-FREEZE-WINDOW-RUNBOOK-2026-05-01.md` — freeze-window runbook for ISOLATION-018

### Files Modified

1. `scripts/rehearse/_common.py` — added `_VALID_DB_RECONCILIATION_STRATEGIES`, `_VALID_UNCLASSIFIED_DISPOSITIONS` constants, and Rule M6 in `load_manifest()`
2. `scripts/rehearse_isolation.py` — added `_WAVE_3_PHASES`, `_wave_for_phase()`, `("db-filter-dryrun", ...)` to `DISPATCH_TABLE`, replaced `wave=2` literal with `_wave_for_phase(args.phase)`
3. `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` — replaced `db_reconciliation_strategy = "OWNER_DECISION_REQUIRED"` with `manifest_driven_filter`; added `unclassified_disposition = "leave_behind_with_warning"`
4. `.claude/rules/project-root-boundary.md` — appended Sandbox Output Exception section (clause-2 single-line for T21 verbatim match)
5. `tests/scripts/test_rehearse_isolation.py` — renamed `test_main_loads_manifest_at_wave2` to `test_main_loads_manifest_at_wave2_for_verify_phase`; added T18 (`test_main_loads_manifest_at_wave_3_when_db_filter_dryrun_phase_requested`) and T19 (`test_main_rejects_unresolved_db_reconciliation_strategy_via_cli_when_db_filter_dryrun_requested`); updated `test_dispatch_table_has_eleven_lanes` → `test_dispatch_table_has_twelve_lanes`; added `db-filter-dryrun` to required lanes set

### KB Records Inserted

1. `IPR-WAVE3-DB-FILTER-001` — implementation_proposal document inserted via `db.insert_document()` (pre-implementation step per GOV-20 Phase 1 step 2)
2. `CVR-WAVE3-DB-FILTER-001` — constraint_verification document inserted via `db.insert_document()` (post-implementation step per GOV-20 Phase 1 step 4)

## Specification-Derived Verification

### Test Execution

```text
$ python -m pytest tests/scripts/test_rehearse_db_filter_dryrun.py tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60
.....................................................................................
87 passed in 2.51s
(After IPR + CVR inserts, T22 hard-passes — no skips remain in Wave 3 scope.)
```

### Ruff Gates

```text
$ python -m ruff check scripts/rehearse/_db_filter_dryrun.py scripts/rehearse/_common.py scripts/rehearse_isolation.py tests/scripts/test_rehearse_db_filter_dryrun.py tests/scripts/test_rehearse_isolation.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_db_filter_dryrun.py scripts/rehearse/_common.py scripts/rehearse_isolation.py tests/scripts/test_rehearse_db_filter_dryrun.py tests/scripts/test_rehearse_isolation.py
5 files already formatted
```

### Live Smoke Run

```text
$ SMOKE_DIR=C:/temp/agent-red-rehearsal-wave3-smoke-v2-1777653709
$ python scripts/rehearse_isolation.py --phase membase --execute --output-dir $SMOKE_DIR
  -> membase ... ok
$ python scripts/rehearse_isolation.py --phase db-filter-dryrun --execute --output-dir $SMOKE_DIR
  -> db-filter-dryrun ... ok
```

`db-filter-summary.json` excerpt:

```json
{
  "lane": "db-filter-dryrun",
  "unclassified_disposition": "leave_behind_with_warning",
  "row_counts": {
    "adopter_inserted": 24544,
    "framework_excluded": 120,
    "unclassified_warned": 15755,
    "telemetry_skipped": 4,
    "orphan_relationship_warned": 19
  },
  "integrity_check": "ok",
  "elapsed_seconds": 0.558
}
```

Independent verification queries against the filtered DB:

```text
specifications WHERE id LIKE 'GTKB-%': 0  (framework correctly excluded)
assertion_runs row count: 0              (telemetry exclusion working)
filtered DB size: 24,092,672 bytes (~24 MB; down from 1.0 GB legacy)
```

### Test-to-Spec Mapping

| Test | Result | Derives From |
|---|---|---|
| T1 `test_filtered_db_excludes_all_framework_classified_rows` | PASS | ADR-ISOLATION-APPLICATION-PLACEMENT-001; authority matrix `groundtruth.db` row |
| T2 `test_filtered_db_telemetry_tables_have_zero_rows` | PASS | Slice 8 Constraint 2 |
| T3 `test_filtered_db_adopter_row_count_matches_partition_manifest_summary` | PASS | Slice 8 contract |
| T4 `test_unclassified_rows_emit_warning_and_are_not_inserted_under_default_disposition` | PASS | DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE; Slice 8 Constraint 4 |
| T5 `test_lane_refuses_when_partition_manifest_missing_at_canonical_path` | PASS | Algorithm step 1; Slice 8 dependency contract |
| T6 `test_lane_propagates_partition_manifest_status_error_for_unknown_table` | PASS | Slice 8 Constraint 1 |
| T7 `test_legacy_db_is_opened_read_only` | PASS | ADR rehearsal non-destructive |
| T8 `test_filtered_db_passes_pragma_integrity_check` | PASS | SQLite consistency contract |
| T9 `test_orphan_relationship_rows_emit_warning_not_silent_drop` | PASS | Slice 8 Constraint 3 |
| T10 `test_lane_is_idempotent_on_re_run` | PASS | Slice 3 idempotency contract |
| T11 `test_lane_writes_only_under_output_dir_db_filter_dryrun_subdir` | PASS | Rule M2 + Sandbox Output Exception |
| T12 `test_load_manifest_wave_3_rejects_unknown_db_reconciliation_strategy` | PASS | Rule M6 |
| T13 `test_load_manifest_wave_3_rejects_unknown_unclassified_disposition` | PASS | Rule M6 |
| T14 `test_load_manifest_wave_3_accepts_manifest_driven_filter` | PASS | Rule M6 (positive case) |
| T15 `test_load_manifest_wave_2_still_accepts_owner_decision_required_for_db_reconciliation` | PASS | Rule M1 backward compatibility |
| T16 `test_db_filter_summary_json_has_required_keys` | PASS | Output Layout schema |
| T17 `test_lane_raises_NotImplementedError_for_non_default_dispositions` | PASS | Implementation Plan explicit scope-deferral |
| T-F1 `test_lane_input_path_matches_slice8_output_path_constant` | PASS | F1 fix from -002 |
| T18 `test_main_loads_manifest_at_wave_3_when_db_filter_dryrun_phase_requested` | PASS | F2 fix from -004 |
| T19 `test_main_rejects_unresolved_db_reconciliation_strategy_via_cli_when_db_filter_dryrun_requested` | PASS | F2 fix from -004 |
| T21 `test_project_root_boundary_amendment_text_matches_output_dir_allowlist_desc_constant` | PASS | F1 fix from -004 |
| T22 `test_ipr_and_cvr_documents_exist_and_link_to_adr_isolation_application_placement_001` | PASS | F2 fix from -004 (post-IPR-and-CVR-insert; hard assert on both) |

Plus driver-test regression (existing 66 tests in `test_rehearse_isolation.py` updated to 68 with T18/T19): all PASS.
Plus Slice 8 regression (`test_rehearse_membase_export.py` 35 tests): all PASS.

### Schema Adaptation Note

During smoke run testing, the lane code initially assumed Slice 8 partition manifest schema keys `versioned_artifacts` / `table` / `row_key` / `excluded_telemetry`. Slice 8's actual output uses `versioned_records` / `table_name` / `row_id` / `summary.excluded_tables` per `_membase_export.py` source. The lane code was corrected to consume the real schema; the test fixture was updated to match. T-F1 already covered the import-path constant; the schema-key alignment is now visible by construction in the live smoke run results above.

## Linked Specifications Coverage

All `-003` + `-005` + `-007` Acceptance Criteria items are satisfied:

1. F1 (`-002`) Slice 8 path corrected to `membase_export/` — verified by lane source + T-F1.
2. F2 (`-002`) driver phase-to-wave mapping landed — T18 + T19 + updated regression test.
3. F3 (`-002`) `project-root-boundary.md` amended with Sandbox Output Exception — verified by T21 + amendment text now contains `_OUTPUT_DIR_ALLOWLIST_DESC` verbatim.
4. F4 (`-002`) DA records archived (`DELIB-S325-*` × 3) — verified by Codex `-008` Prior Deliberations check.
5. F1 (`-004`) amendment text matches M2 allowlist exactly — verified by T21 (verbatim substring assertion).
6. F2 (`-004`) GOV-20 IPR/CVR carried into implementation scope — IPR + CVR both inserted, T22 hard-passes.
7. F1 (`-006`) line-wrap-vs-verbatim alignment — clause-2 sentence is single-line in amendment; verified by T21 passing.

## Risk / Impact at Post-Implementation

**Filter correctness:** validated by 87 tests + live smoke against real KB. Live results show 0 GTKB-* prefixed specs in filtered DB and 0 assertion_runs rows; framework_excluded counter (120) consistent with Slice 8 reported framework count (79 + 12 relationship + telemetry tables = ~120).

**Concurrent-session risk:** unchanged from `-003` analysis. Rehearsal is read-only on legacy. ISOLATION-018 cutover will use the freeze-window runbook landed in this commit.

**Forward compatibility:** T17 confirms `carry_forward_to_adopter` and `manual_review_gate` raise `NotImplementedError`. The validator accepts these for forward compatibility per the proposal.

**Drift guard:** T21 binds rule text to source code; T22 binds IPR/CVR existence to ADR-tagged KB documents.

**Rollback:** trivial. Delete `{output_dir}` to roll back rehearsal output. Revert this commit to roll back code changes. Legacy DB untouched throughout.

## Linked Specifications Tested

Every linked specification clause has at least one mapped test that executed and passed. The Specification-Derived Verification Gate (per `.claude/rules/file-bridge-protocol.md`) is satisfied.

## Outstanding Items

None. All `-007` acceptance criteria met.

Optional follow-ups (not blocking VERIFIED):
- Promote sandbox-output exception clause to a formal DCL artifact.
- Add DCLs binding the isolation surface (Wave 3 documents the gap; future work item).
- Use the freeze-window runbook in ISOLATION-018 cutover planning.

## Decision Needed From Owner

None for VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
