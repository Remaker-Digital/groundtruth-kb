ADVISORY

bridge_kind: advisory_proposal
Document: gtkb-gfr-slice-c-missing-tests
Version: 001
Date: 2026-07-21 UTC
author_identity: loyal-opposition/goose
author_harness_id: G
author_session_context_id: goose-20260720-lo-skillrename-review

target_paths: (read-only advisory; no mutation targets. Implementation proposal to follow under authorized envelope.)

# Advisory: Missing Slice C test files

## Claim

Slice C (WI-5645) was VERIFIED in `bridge/gtkb-gfr-slice-c-cli-affordances-004.md` with a non-blocking note that two of three proposed test files were not committed:

- `platform_tests/scripts/test_cli_projects_authorizations_covers_path.py` — MISSING
- `platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py` — MISSING

The `--covers-path` flag (Finding 4.2) and `--project` flag (Finding 2.6) are implemented in `groundtruth-kb/src/groundtruth_kb/cli.py` and `cli_backlog_add_work_item.py`, but lack dedicated test coverage.

## Evidence

- `bridge/gtkb-gfr-slice-c-cli-affordances-001.md` (proposal) committed to 5 target_paths including 3 test files
- `bridge/gtkb-gfr-slice-c-cli-affordances-004.md` (LO VERIFIED) notes: "Two of three proposed test files are missing"
- `test_cli_backlog_list_phases.py` EXISTS (2 tests, passing)
- `test_cli_projects_authorizations_covers_path.py` MISSING (verified by `Test-Path`)
- `test_cli_backlog_add_work_item_project_flag.py` MISSING (verified by `Test-Path`)

## Risk/Impact

- **Low severity, P2:** The features are functional and ruff-clean, but untested. Future regressions to `--covers-path` or `--project` will not be caught by CI.
- The acceptance criteria in the GO'd proposal (criteria 7: "New test files pass") were only partially met.

## Recommended Action

1. Prime Builder creates a MemBase work item (requires authorized session envelope for `resolve_changed_by`).
2. Implement the two missing test files per the test plans in `bridge/gtkb-gfr-slice-c-cli-affordances-001.md`:
   - `test_cli_projects_authorizations_covers_path.py`: test PAUTH filtering by mutation class, empty result with clear message, JSON output
   - `test_cli_backlog_add_work_item_project_flag.py`: test `project_members` row creation, backward compat without `--project`, error on invalid project id
3. Run `python -m pytest platform_tests/scripts/test_cli_projects_authorizations_covers_path.py platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py -q --tb=short`
4. Run `ruff check` and `ruff format --check` on new files.

## Decision Needed from Owner

None. This is an advisory for a follow-up work item. The implementing PB should create the WI under an authorized session envelope and implement the two test files.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
