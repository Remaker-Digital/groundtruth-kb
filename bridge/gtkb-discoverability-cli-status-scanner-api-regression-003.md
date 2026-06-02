NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-02T13-27Z-pb
author_model: GPT-5
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; dual-role authority active

bridge_kind: implementation_report
Document: gtkb-discoverability-cli-status-scanner-api-regression
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-discoverability-cli-status-scanner-api-regression-002.md
Approved proposal: bridge/gtkb-discoverability-cli-status-scanner-api-regression-001.md
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3262
Recommended commit type: fix
Date: 2026-06-02 UTC

# Discoverability CLI Status Scanner API Regression - Implementation Report

## Implementation Claim

Implemented the bounded scanner API compatibility repair for `gt backlog status`.
The backlog status service now uses the VERIFIED project-scoped scanner helper
`verified_work_items_by_project(project_root)` instead of the removed global
`verified_work_items()` helper, and verified-coverage annotation is scoped to
each project row's own project id.

## Authorization Evidence

- command: `python scripts/implementation_authorization.py begin --bridge-id gtkb-discoverability-cli-status-scanner-api-regression`
- packet_hash: `sha256:1ec773ffd615eecbdfe096d3415068a7cb8b215f2b8cf14a4b21e7bd74db68c5`
- latest GO: `bridge/gtkb-discoverability-cli-status-scanner-api-regression-002.md`
- approved proposal: `bridge/gtkb-discoverability-cli-status-scanner-api-regression-001.md`
- target path validation:
  - `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py` authorized: true
  - `platform_tests/scripts/test_cli_backlog_status.py` authorized: true

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py`
- `platform_tests/scripts/test_cli_backlog_status.py`

No MemBase, `groundtruth.db`, generated fixture, credential, deployment,
application, or out-of-root files were intentionally modified by the
implementation.

## Specification Links

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `WI-3262`
- `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI`
- `bridge/gtkb-discoverability-cli-slice-2-implementation-006.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-CODE-QUALITY-BASELINE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Implementation Details

- Replaced the lazy scanner import of `verified_work_items()` with
  `verified_work_items_by_project()`.
- Changed `_annotate_verified_coverage()` to accept a mapping of
  `project_id -> set[work_item_id]`, and to annotate each project row from its
  own set only.
- Updated scanner caveat text from stale "in flight" wording to the current
  VERIFIED scanner-fix thread and verdict path.
- Updated focused tests to monkeypatch the project-scoped helper and prove that
  coverage for `PROJECT-GTKB-X` does not leak to `PROJECT-PROJECT-GTKB-Y`.
- Preserved the base command's no-scanner-import behavior.

## Specification-Derived Verification Mapping

| Requirement / Spec Link | Verification |
|---|---|
| `bridge/gtkb-discoverability-cli-slice-2-implementation-006.md` preserves the `gt backlog status` behavior matrix. | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cli_backlog_status.py -q --tb=short --basetemp=.gtkb-state/pytest-tmp-discoverability-status-commit` |
| `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md` establishes `verified_work_items_by_project(project_root)` as the current API. | `test_status_verified_coverage_annotation` monkeypatches and asserts project-scoped coverage. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires behavior-to-test mapping. | The focused test file covers retire-ready, verified coverage, caveat wording, base command import independence, and read-only behavior. |
| `GOV-CODE-QUALITY-BASELINE-001` requires no quality regression. | Ruff check and format-check passed for both target files. |
| `GOV-STANDING-BACKLOG-001` requires the backlog status surface remain read-only and visible. | `test_status_makes_no_db_writes` passed; live CLI smokes exited 0. |

## Verification Commands

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cli_backlog_status.py -q --tb=short --basetemp=.gtkb-state/pytest-tmp-discoverability-status-commit
```

Result: `10 passed in 3.34s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py platform_tests/scripts/test_cli_backlog_status.py
```

Result: `All checks passed!`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py platform_tests/scripts/test_cli_backlog_status.py
```

Result: `2 files already formatted`.

```text
groundtruth-kb\.venv\Scripts\gt.exe backlog status --json
groundtruth-kb\.venv\Scripts\gt.exe backlog status --with-verified-coverage --json
groundtruth-kb\.venv\Scripts\gt.exe backlog status --with-retire-ready --json
```

Result: all three commands exited `0` and emitted JSON beginning with
`{"projects": [...]}`.

## Code Quality Baseline

| Rule ID | Result |
|---|---|
| CQ-SECRETS-001 | No secrets or credential values were added. |
| CQ-PATHS-001 | Only the two authorized in-root target files were edited. |
| CQ-COMPLEXITY-001 | Change is a direct helper migration plus project-row lookup. |
| CQ-CONSTANTS-001 | Reused existing scanner thread constants; updated the verdict-file constant. |
| CQ-SECURITY-001 | CLI remains read-only and does not add network, auth, or deployment behavior. |
| CQ-DOCS-001 | Scanner caveat now references the VERIFIED scanner source. |
| CQ-TESTS-001 | Focused tests updated and passed. |
| CQ-LOGGING-001 | No logging surface was changed. |
| CQ-VERIFICATION-001 | Focused pytest, ruff, format-check, and live smokes passed. |

## Owner Action

No owner action required.

File bridge scan contribution: 1 entry processed.
