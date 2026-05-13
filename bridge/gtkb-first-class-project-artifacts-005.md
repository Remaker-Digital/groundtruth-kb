NEW

# Implementation Report - First-Class Project Artifacts

bridge_kind: implementation_report
Document: gtkb-first-class-project-artifacts
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Implements: `bridge/gtkb-first-class-project-artifacts-003.md`
GO verdict: `bridge/gtkb-first-class-project-artifacts-004.md`
Recommended commit type: `feat:`

## Claim

First-class project artifacts are implemented as an append-friendly MemBase project layer over canonical `work_items` / `current_work_items`. The implementation does not create `backlog_items`, `backlog_entries`, a wrapper backlog queue, or a `subjects` table.

## Bridge INDEX Evidence

This implementation report is filed under `bridge/` as `bridge/gtkb-first-class-project-artifacts-005.md`. The `bridge/INDEX.md` update inserts `NEW: bridge/gtkb-first-class-project-artifacts-005.md` at the top of the existing document entry above the prior `GO`, `REVISED`, `NO-GO`, and `NEW` history. No prior bridge version is deleted or rewritten.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/canonical-terminology.md`

## Implementation Summary

- Added versioned `projects`, `project_work_item_memberships`, `project_dependencies`, and `project_artifact_links` tables plus current views.
- Added deterministic idempotent backfill from `current_work_items.project_name` and `subproject_name`.
- Added project read/write APIs that keep work-item details sourced from `current_work_items`.
- Added `gt projects list` and `gt projects show` read surfaces.
- Extended summary/export counts for project-layer records.
- Added tests covering schema, authority preservation, many-to-many work-item membership, dependencies, artifact links, compatibility backfill, project summary counts, and CLI reporting.

## Backfill Inventory / Review Packet

Inventory artifact: the backfill reads only live `current_work_items` rows where `project_name` is non-empty, ordered deterministically by project/subproject/order/id. It creates root project records from `project_name`, subproject records from `subproject_name`, and membership rows linking those project records back to the existing canonical work-item IDs.

Review packet: the migration is idempotent, append-only, and non-destructive. It does not update or delete `work_items`, does not create `backlog_items`, does not create `backlog_entries`, and does not create `subjects`. Compatibility fields remain on `work_items` and remain readable during migration.

DECISION DEFERRED: future write-oriented project CLI, dashboard project rollups, subject-schema terminology work, and any retirement of `work_items.project_name` / `subproject_name` compatibility fields are deferred to future governed bridge slices. No unresolved conversion decision is executed in this slice.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_project_artifacts.py`

## Spec-to-Test Mapping

| Proposal Test ID | Evidence |
|---|---|
| T-project-schema | `test_project_schema_preserves_work_item_authority` |
| T-work-items-authority | `test_project_schema_preserves_work_item_authority` asserts `work_items` / `current_work_items` remain and no `backlog_items` / `backlog_entries` exists. |
| T-many-to-many | `test_work_item_can_belong_to_multiple_projects_without_duplication` |
| T-project-dependencies | `test_project_dependencies_are_queryable_independently` |
| T-artifact-links | `test_project_artifact_links_cover_bridge_deliberation_and_spec` |
| T-compat-migration | `test_compatibility_backfill_maps_project_strings_to_project_memberships` |
| T-no-subject-table | `test_project_schema_preserves_work_item_authority` asserts no `subjects` table. |
| T-reporting | `test_projects_cli_show_reports_members_from_current_work_items` |

## Verification

Commands executed:

```text
python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_project_artifacts.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_operating_state.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_hook_registration_parity.py scripts/implementation_authorization.py scripts/implementation_start_gate.py .claude/hooks/implementation-start-gate.py
```

Observed results:

- `7 passed, 1 warning`
- `52 passed, 1 warning`
- Targeted ruff check: `All checks passed!`

Additional observation:

- Broad `python -m ruff check groundtruth-kb/src groundtruth-kb/tests ...` and broad `ruff format --check groundtruth-kb/src groundtruth-kb/tests` are not clean in the current dirty worktree because of unrelated pre-existing/parallel findings in `mcp_surface`, `project/doctor.py`, `project/scaffold.py`, and unrelated tests. I did not run a broad formatter over those unrelated files.

## Known Gaps

No known functional gap in the selected Slice 1 project-artifacts scope. CLI support is read-only (`list`/`show`); write-oriented project CLI can remain a later slice.
