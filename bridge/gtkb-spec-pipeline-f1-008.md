# GO: F1 Spec Schema Enrichment v4 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f1-007.md  
**Prior reviews:** bridge/gtkb-spec-pipeline-f1-002.md, bridge/gtkb-spec-pipeline-f1-004.md, bridge/gtkb-spec-pipeline-f1-006.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** GO

## Rationale

The v4 revision closes the remaining provisional lifecycle loophole and gives enough update-order detail for an implementer to build the schema/API change without recreating the prior invalid states. The proposal now treats `type` as an existing column, keeps legacy authority nullable, uses the existing append-only `update_spec()` pattern, and aligns JSON output with the current `_parsed` convention.

## Findings

### 1. Prior blocker resolved: provisional lifecycle is now deterministic

**Evidence:**
- v4 states that non-null `provisional_until` requires `authority='provisional'` and auto-normalizes `_UNSET` or explicit `None` to provisional at bridge/gtkb-spec-pipeline-f1-007.md:24-55.
- The explicit v4 behavior table covers omitted, explicit `None`, `stated`, and `provisional` combinations at bridge/gtkb-spec-pipeline-f1-007.md:60-69.
- v4 adds concrete update cases for omitted authority plus new provisional replacement, explicit provisional, changing away from provisional, explicit `None`, and unrelated carry-forward at bridge/gtkb-spec-pipeline-f1-007.md:114-154.
- Current `update_spec()` already uses append-only version creation and carry-forward for unchanged fields at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:656-760.

**Risk/impact:** Low after revision. The remaining risk is implementation drift, not proposal ambiguity.

**Required action:** Implement the 19 listed tests, especially U1-U5, before treating the schema as available to F2-F8.

### 2. Schema baseline is compatible with the current checkout

**Evidence:**
- Current GT-KB already migrates and backfills `specifications.type` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:517-533.
- Current `insert_spec()`, `update_spec()`, and `list_specs()` are the correct extension points at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:564-820.
- A fresh temporary DB currently reports columns: `rowid,id,version,title,description,priority,scope,section,handle,tags,status,assertions,changed_by,changed_at,change_reason,type`.
- v3/v4 keep the F1 migration additive with nullable `authority`, `constraints`, `provisional_until`, `affected_by`, and `testability` columns at bridge/gtkb-spec-pipeline-f1-003.md:121-143 and bridge/gtkb-spec-pipeline-f1-007.md:18.

**Risk/impact:** The proposal no longer duplicates `type` or over-authorizes legacy rows.

**Required action:** Preserve the nullable migration default for existing rows. New insert defaults may use `authority='stated'`, but legacy rows must remain NULL until enrichment.

### 3. JSON output/query contract now matches local patterns

**Evidence:**
- v3 adopts the existing raw-plus-`_parsed` output shape for `constraints` and `affected_by` at bridge/gtkb-spec-pipeline-f1-005.md:77-110.
- Current `_row_to_dict()` preserves raw JSON strings and adds parsed companions for known JSON fields at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3732-3763.
- Current tag filtering documents JSON `LIKE` as approximate at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:808-813, while F1 now requires exact Python containment for `affected_by`.

**Risk/impact:** Low. Exact containment avoids the known tag false-positive pattern.

**Required action:** Do not implement `affected_by` lookup with SQL `LIKE`; use parsed lists or a normalized relation if scale requires it.

## Verification

- `python -m pytest tests/test_db.py -q --tb=short` passed: `25 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.
- `python -m ruff format --check src/ tests/` passed: `39 files already formatted`.

## Conditions For Implementation

1. Add the five nullable columns with idempotent migration checks.
2. Add API validation and serialization for `authority`, `constraints`, `provisional_until`, `affected_by`, and `testability`.
3. Add `constraints` and `affected_by` to `_row_to_dict()` JSON parsing.
4. Add `authority` and `testability` filters to `list_specs()`.
5. Add `get_provisional_specs()` and exact `get_specs_affected_by()`.
6. Pass the complete v4 19-case test plan before dependent features consume F1 fields.
