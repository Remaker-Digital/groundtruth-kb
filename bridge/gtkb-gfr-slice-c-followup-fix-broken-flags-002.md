IMPLEMENTED

bridge_kind: implementation_report
Document: gtkb-gfr-slice-c-followup-fix-broken-flags
Version: 002
Date: 2026-07-21 UTC
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-07-21T08-15-00Z
Responds to: bridge/gtkb-gfr-slice-c-followup-fix-broken-flags-001.md

Project Authorization: PAUTH-GFR-SLICE-C-FOLLOWUP-20260721
Project: PROJECT-GTKB-GOVERNANCE-FRICTION-REDUCTION
Work Item: WI-5647

# Implementation Report — GFR Slice C Follow-up: Fix Broken CLI Flags + Missing Tests

## Summary

Two defects from Slice C (WI-5645) have been fixed and the two missing test files have been created:

1. **`--covers-path` (Finding 4.2): FIXED.** Added `covers_path: str | None` parameter to `projects_authorizations` function signature and implemented filtering logic using `classify_target`.
2. **`--project` (Finding 2.6): FIXED.** Added `project_work_item_memberships` insert in `add_work_item_with_test()` after the WI+test+phase commit, using `db.link_project_work_item()`.
3. **Test: `test_cli_projects_authorizations_covers_path.py`: CREATED.** 3 tests covering filtering, no-match message, and JSON output.
4. **Test: `test_cli_backlog_add_work_item_project_flag.py`: CREATED.** 3 tests covering membership creation, backward compat, and error on invalid project.

## Changes

### `groundtruth-kb/src/groundtruth_kb/cli.py`

- Added `covers_path: str | None` parameter to `projects_authorizations` function signature.
- When `covers_path` is set: imports `classify_target`, classifies the path, filters PAUTHs by `allowed_mutation_classes_parsed`, prints clear message when no match.

### `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`

- After `_commit_transaction(conn)` succeeds, if `request.project_id` is set: calls `db.link_project_work_item()` to create the `project_work_item_memberships` row.
- Linkage failure raises `AddWorkItemError` with descriptive message (fail-loud for linkage, fail-open for WI — WI already committed).
- Added `project_membership` to the return dict (None when no `--project` was used).

### `platform_tests/scripts/test_cli_projects_authorizations_covers_path.py` (new)

3 tests:
1. `test_covers_path_filters_to_matching_pauth` — `scripts/foo.py` (source class) returns only PAUTHs allowing `source`
2. `test_covers_path_no_match_clear_message` — `bridge/foo-001.md` (bridge class) with no matching PAUTH prints clear message
3. `test_covers_path_json_output` — `--json` output with `--covers-path` emits filtered JSON array

### `platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py` (new)

3 tests:
1. `test_project_flag_creates_membership` — `--project PROJECT-TEST` creates `project_work_item_memberships` row
2. `test_no_project_flag_no_membership` — without `--project`, no membership row created (backward compat)
3. `test_project_flag_invalid_project_error` — `--project PROJECT-NONEXISTENT` raises `AddWorkItemError` but WI still exists

## Verification Results

### Tests

```
python -m pytest platform_tests/scripts/test_cli_backlog_list_phases.py \
    platform_tests/scripts/test_cli_projects_authorizations_covers_path.py \
    platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py \
    -q --tb=short

8 passed, 1 warning in 5.02s
```

### Ruff

```
python -m ruff check <all 4 files> → All checks passed!
python -m ruff format --check <all 4 files> → 4 files already formatted
```

### Existing GFR tests

```
python -m pytest platform_tests/scripts/test_bridge_applicability_preflight_gfr_slice_a.py \
    platform_tests/scripts/test_implementation_authorization_gfr_slice_a.py \
    platform_tests/scripts/test_drift_hook_remediation_text.py \
    platform_tests/scripts/test_parity_strict_on_rename.py \
    -q --tb=short

13 passed in 0.74s
```

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| 1 | `--covers-path` filters without crashing | ✅ |
| 2 | `--covers-path --json` emits valid JSON | ✅ |
| 3 | No-match message printed | ✅ |
| 4 | `--project` creates `project_work_item_memberships` row | ✅ |
| 5 | Without `--project`, backward-compatible | ✅ |
| 6 | New test files pass | ✅ |
| 7 | All existing tests pass | ✅ |
| 8 | `ruff check` and `ruff format --check` pass | ✅ |
| 9 | No existing governance gate weakened | ✅ |

## Commit

`e9d71930` — `fix(gfr-c): fix broken --covers-path and --project flags + add missing tests (WI-5647)`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
