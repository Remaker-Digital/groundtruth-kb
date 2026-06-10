REVISED

# Implementation Report Revision - First-Class Project Artifacts

bridge_kind: implementation_report
Document: gtkb-first-class-project-artifacts
Version: 008
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Responds to: `bridge/gtkb-first-class-project-artifacts-007.md`
Implements: `bridge/gtkb-first-class-project-artifacts-003.md`
GO verdict: `bridge/gtkb-first-class-project-artifacts-004.md`
Recommended commit type: `feat:`

## Claim

The `-007` formatter blocker is resolved in the current worktree. First-class
project artifacts remain implemented as a project layer over canonical
`work_items` / `current_work_items`; the implementation does not introduce
`backlog_items`, `backlog_entries`, a wrapper backlog queue, or a `subjects`
table.

No additional source edit was needed during this dispatch; the exact touched
project-artifact files now pass formatter verification.

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

## Prior Deliberations

Carried forward from the proposal and verification chain:
`DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT`,
`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`, `DELIB-1791`,
`DELIB-1790`, `DELIB-0838`, `DELIB-0839`, `DELIB-0874`,
`DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE`, and
`DELIB-1583`, plus prior bridge verdicts
`bridge/gtkb-first-class-project-artifacts-002.md`, `-004.md`, `-006.md`,
and `-007.md`.

## Owner Decisions / Input

No new owner decision was requested. This revision responds only to the
formatter verification blocker in `-007`.

## Finding Addressed

### F1 - Touched project-artifact source file is not formatter clean

Response: resolved. Exact changed-file ruff check and ruff format check now
pass for `groundtruth-kb/src/groundtruth_kb/db.py`,
`groundtruth-kb/src/groundtruth_kb/cli.py`, and
`groundtruth-kb/tests/test_project_artifacts.py`.

## Files Changed

No additional source/test files were changed by this dispatch. This report
updates the bridge audit trail with current verification evidence for the
previously changed files:

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
| Formatter cleanliness | Exact ruff format check listed below. |

## Verification

Commands executed:

```text
python -m pytest groundtruth-kb/tests/test_project_artifacts.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_operating_state.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py
```

Observed results:

- Project-artifact test lane: `52 passed, 1 warning`.
- Exact changed-file ruff check: `All checks passed!`.
- Exact changed-file ruff format check: `3 files already formatted`.

## Known Gaps

No known remaining selected gap for the first-class project artifacts
implementation.
