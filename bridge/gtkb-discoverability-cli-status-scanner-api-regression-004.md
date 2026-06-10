VERIFIED
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: keep-working-2026-06-02T13-30Z-lo
author_model: GPT-5
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; dual-role authority active

bridge_kind: lo_verdict
Document: gtkb-discoverability-cli-status-scanner-api-regression
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-02 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-discoverability-cli-status-scanner-api-regression-003.md
Recommended commit type: fix

# Discoverability CLI Status Scanner API Regression - Verification Verdict

## Verdict

VERIFIED.

The implementation report is supported by fresh source review and command
evidence. The change is limited to the two approved target paths, migrates the
verified-coverage path from the removed `verified_work_items()` helper to the
current `verified_work_items_by_project(project_root)` API, and preserves the
base command's no-scanner-import behavior.

## Applicability Preflight

- command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-discoverability-cli-status-scanner-api-regression`
- exit: 0
- packet_hash: `sha256:d48de2c0d143de1b13a02218f79937ebc33ed73328199f02496393fce4954cdf`
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

- command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-discoverability-cli-status-scanner-api-regression`
- exit: 0
- clauses evaluated: 5
- must_apply: 3
- evidence gaps in must_apply clauses: 0
- blocking gaps: 0

## Spec-Derived Verification

| Requirement / Spec Link | Verification Result |
|---|---|
| `bridge/gtkb-discoverability-cli-slice-2-implementation-006.md` behavior matrix remains intact. | Focused pytest passed: `10 passed in 3.34s`. |
| `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md` current API is project-scoped. | Source now imports `verified_work_items_by_project`; tests monkeypatch project-scoped coverage. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` mapping is explicit. | Implementation report includes behavior-to-test mapping and the tested paths cover retire-ready, verified coverage, caveat, no-scanner base path, and read-only behavior. |
| `GOV-CODE-QUALITY-BASELINE-001` remains satisfied. | Ruff check passed and ruff format-check reported `2 files already formatted`. |
| `GOV-STANDING-BACKLOG-001` read-only status behavior is preserved. | `test_status_makes_no_db_writes` passed and live CLI smokes exited 0. |

## Commands Rerun Or Reviewed

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

Result: all three commands exited `0` when output was captured before preview.

## Source Review

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py` now calls
  `verified_work_items_by_project(project_root)`.
- `_annotate_verified_coverage()` now looks up coverage by the current
  project row's id, preventing coverage leakage across projects.
- `platform_tests/scripts/test_cli_backlog_status.py` asserts the covered
  canonical project row and uncovered doubled-prefix row separately.
- The scanner caveat now references the VERIFIED scanner-fix verdict path and
  no longer describes the scanner repair as in flight.

## Live Thread Check

- command: `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-discoverability-cli-status-scanner-api-regression --format json --preview-lines 5`
- exit: 0
- drift: []

No owner action required.

File bridge scan contribution: 1 entry processed.
