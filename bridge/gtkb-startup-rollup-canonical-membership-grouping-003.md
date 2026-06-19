NEW

# GT-KB Bridge Implementation Report - gtkb-startup-rollup-canonical-membership-grouping - 003

bridge_kind: implementation_report
Document: gtkb-startup-rollup-canonical-membership-grouping
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-startup-rollup-canonical-membership-grouping-002.md
Approved proposal: bridge/gtkb-startup-rollup-canonical-membership-grouping-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3500
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-18T20-45-53Z-prime-builder-A-7c4b93
author_model: gpt-5
author_model_version: GPT-5 Codex runtime (exact backend snapshot not exposed)
author_model_configuration: Codex headless bridge auto-dispatch; approval_policy=never; sandbox=workspace-write; network disabled
author_metadata_source: dispatch prompt plus runtime environment
Recommended commit type: fix:

## Implementation Claim

Implemented the approved startup rollup correction. The scoped dashboard summary
payload now enriches each `current_work_items` row with its deterministic
primary active canonical project membership from
`current_project_work_item_memberships`, preserving the legacy `project_name`
field as compatibility data. The session startup Project State Rollup now groups
non-terminal work items by `current_project_work_item_memberships.project_id`
and counts a row as ungrouped only when no active canonical membership exists.

The fix uses `membership_order` as the deterministic primary-membership tiebreak
with null order sorted last, then `project_id` for stable ordering. Project
display labels come from `current_projects.name` when available and fall back to
the canonical project id.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - WI-3500 is a defect-origin, single-concern
  reliability fix covered by the active standing reliability-fixes PAUTH.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the rollup grouping now derives from the
  canonical active membership source instead of the legacy compatibility field.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps the
  linked governing surfaces to executed verification evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries
  forward the proposal's governing specification links.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation proceeded from the live GO
  bridge entry and this report is filed as the next numbered bridge version.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) - the defect, fix, tests,
  and verification evidence are preserved as durable artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - the implementation record
  preserves the approved plan, evidence, and residual risk.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - the startup rollup behavior
  change is captured in a bridge implementation report.

## Owner Decisions / Input

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner decision establishing the
  reliability fast lane used by the cited standing PAUTH.
- No new owner decision or waiver was required during implementation.

## Prior Deliberations

- `bridge/gtkb-startup-rollup-canonical-membership-grouping-001.md` - approved
  implementation proposal carried forward.
- `bridge/gtkb-startup-rollup-canonical-membership-grouping-002.md` - Loyal
  Opposition GO verdict authorizing implementation.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane
  authorization context.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-startup-rollup-canonical-membership-grouping` passed and produced packet `sha256:fc6f3a496755f5077b9bed1ed71a242d89b21e1635946e3a5a0c11dde42c84c9`; diff is limited to the three GO-authorized files. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_project_state_rollup_matches_canonical_membership_orphan_count` creates a fixture DB and asserts the rollup ungrouped count equals a direct `NOT EXISTS` query against active `current_project_work_item_memberships`; full startup test file passed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps every carried-forward linked surface to executed command evidence; pytest, scoped boundary, ruff lint, and ruff format checks all passed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The implementation stayed inside the GO proposal's `target_paths` and carries the proposal's linked specifications into this report. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live latest status was checked as `GO`; implementation-start authorization passed; work-intent claim row `9983` was acquired for this report. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The report records implementation claim, files changed, executed evidence, and rollback path. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The bridge audit chain preserves proposal, GO verdict, implementation report, and verification-ready evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Startup surface behavior and test coverage changes are captured here for Loyal Opposition verification. |

## Commands Run

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-startup-rollup-canonical-membership-grouping`
- `python scripts\bridge_claim_cli.py claim gtkb-startup-rollup-canonical-membership-grouping`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp .gtkb-tmp\pytest-startup-rollup-lf-final platform_tests\scripts\test_session_self_initialization.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\check_scoped_service_boundary.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\gtkb_scoped_client.py scripts\session_self_initialization.py platform_tests\scripts\test_session_self_initialization.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\gtkb_scoped_client.py scripts\session_self_initialization.py platform_tests\scripts\test_session_self_initialization.py`
- `git diff --check -- scripts\gtkb_scoped_client.py scripts\session_self_initialization.py platform_tests\scripts\test_session_self_initialization.py`

## Observed Results

- Implementation-start authorization passed with latest status `GO`, proposal
  `bridge/gtkb-startup-rollup-canonical-membership-grouping-001.md`, GO verdict
  `bridge/gtkb-startup-rollup-canonical-membership-grouping-002.md`, and target
  paths matching the three files changed by this implementation.
- Work-intent claim acquired: rowid `9983`, session
  `2026-06-18T20-45-53Z-prime-builder-A-7c4b93`.
- Pytest: `73 passed, 2 warnings in 150.46s`. Warnings were pre-existing
  environment/config warnings: unknown `asyncio_mode` option and pytest cache
  path creation warning.
- Scoped-service boundary: `PASS`; allowed read operations
  `['dashboard.summary.read']`; summary path file
  `E:\GT-KB\scripts\session_self_initialization.py`.
- Ruff lint: `All checks passed!`
- Ruff format check: `3 files already formatted`.
- Git whitespace check on changed files: clean exit.

## Files Changed

- `scripts/gtkb_scoped_client.py`
  - Enriches `current_work_items` payload rows with
    `canonical_project_id`, `canonical_project_name`,
    `canonical_project_membership_id`, `canonical_project_membership_role`, and
    `canonical_project_membership_order` from active canonical membership rows.
  - Preserves legacy `project_name` unchanged for compatibility.
- `scripts/session_self_initialization.py`
  - Groups Project State Rollup by `canonical_project_id` instead of
    `project_name`.
  - Reports source/grouping labels as membership-derived and updates the Loyal
    Opposition startup project-state rule text accordingly.
- `platform_tests/scripts/test_session_self_initialization.py`
  - Updates the rollup unit test to prove legacy project names no longer drive
    grouping.
  - Adds a fixture-DB regression test proving ungrouped count parity against a
    direct active-membership orphan query.

Unrelated dirty worktree entries existed before and during this dispatch; they
were not modified for this bridge implementation and are not part of this
report's changed-file scope.

## Acceptance Criteria Status

- [x] Scoped-service payload carries active canonical membership alongside the
  legacy compatibility `project_name` field.
- [x] `_project_state_rollup` groups non-terminal work items by canonical active
  membership and counts genuinely membership-less non-terminal rows as
  ungrouped.
- [x] Rollup source and grouping labels no longer claim `project_name` authority.
- [x] Regression coverage asserts fixture-DB count parity with the canonical
  membership table.
- [x] Scoped-service boundary remains intact; no direct `groundtruth.db` read was
  added to `session_self_initialization.py`.
- [x] Ruff lint and format gates pass on changed Python files.

## Risk And Rollback

Residual risk is limited to downstream consumers that may inspect the additive
`canonical_project_*` payload fields. Existing consumers of `project_name` keep
the same field and value. The startup rollup intentionally no longer treats
legacy-only `project_name` as authoritative grouping evidence.

Rollback is straightforward: revert the three changed files. No schema change,
data migration, or canonical MemBase mutation was performed.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: repairs a reporting-surface data-correctness defect
  without adding a new user-facing capability or schema.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed
   command evidence.
2. Return `VERIFIED` if the report and implementation satisfy the approved
   proposal; otherwise return `NO-GO` with findings.
