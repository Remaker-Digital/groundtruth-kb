NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-02T13-15Z-pb
author_model: GPT-5
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; dual-role authority active

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3262

# Defect-Fix Proposal - Discoverability CLI Status Scanner API Regression

bridge_kind: prime_proposal
Document: gtkb-discoverability-cli-status-scanner-api-regression
Version: 001 (NEW)
Date: 2026-06-02 UTC

## Claim

Fix the `gt backlog status` scanner-backed flags after the project-completion scanner reached VERIFIED with a project-scoped API. The current backlog status service and its tests still call the removed global `verified_work_items()` helper, so `--with-retire-ready` and `--with-verified-coverage` fail before they can return scanner-backed output.

## Defect / Reproduction

Fresh verification of the already-VERIFIED `gtkb-discoverability-cli-slice-2-implementation` surface found three failing tests in `platform_tests/scripts/test_cli_backlog_status.py`:

- `test_status_retire_ready_uses_scanner`
- `test_status_verified_coverage_annotation`
- `test_status_scanner_caveat_present_when_flags_set`

Observed cause: `scripts/project_verified_completion_scanner.py` no longer exports `verified_work_items`; the VERIFIED scanner thread replaced it with `verified_work_items_by_project(project_root) -> dict[project_id, set[wi]]`.

Reproduction command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts	est_cli_backlog_status.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-discoverability-status-0602
```

Observed result before this proposal: `3 failed, 7 passed`; failures are `AttributeError: module 'scripts.project_verified_completion_scanner' has no attribute 'verified_work_items'`.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py`
- `platform_tests/scripts/test_cli_backlog_status.py`

No `applications/**`, out-of-root, credential, deployment, production, schema migration, or MemBase mutation path is in scope.

## Specification Links

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the backlog status CLI is a deterministic service replacing recurring ad-hoc status reconstruction.
- `WI-3262` - original discoverability work item whose verified CLI surface is regressed by the scanner API removal; resolved status is historical closure, but the active PAUTH still includes the WI and the code surface remains live.
- `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI` - active project authorization; includes WI-3262 and allows `cli_extension` plus `test_addition`.
- `bridge/gtkb-discoverability-cli-slice-2-implementation-006.md` - the original VERIFIED `gt backlog status` implementation and 10-test acceptance matrix this fix preserves.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md` - VERIFIED scanner API source; documents removal of `verified_work_items()` and replacement with `verified_work_items_by_project()`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge/INDEX.md is canonical workflow state; this proposal and its later report/verdict stay append-only in bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specs, PAUTH, prior VERIFIED implementation, and scanner API source.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - required `Project Authorization`, `Project`, and `Work Item` header lines are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each behavior to executable tests and live smoke commands.
- `GOV-STANDING-BACKLOG-001` - the command reads backlog/project state and must remain visible/read-only; this fix performs no backlog mutation.
- `GOV-CODE-QUALITY-BASELINE-001` - touched Python files must stay within the existing ruff/format baseline; this proposal adds no quality waiver.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves traceability between the verified scanner design, the verified CLI surface, and executable regression coverage.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - treats this failing verified surface as lifecycle drift requiring a durable bridge artifact rather than a silent patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - closes a regression in a verified implementation without creating new lifecycle transitions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work is in the GT-KB root and does not affect adopter applications.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - recurring AI status reconstruction belongs in deterministic services.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase work_items/project state is canonical backlog data.
- `DELIB-2646` - Loyal Opposition verdict for the discoverability CLI slice 2 implementation.
- `DELIB-2652` - Loyal Opposition verdict for discoverability CLI slice 2 scoping.
- `DELIB-2503` - owner AUQ chain for the D3/D4 project-completion scanner fix.
- `bridge/gtkb-discoverability-cli-slice-2-implementation-006.md` - VERIFIED source implementation for `gt backlog status`.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md` - VERIFIED scanner API change that makes the current backlog status code stale.

## Owner Decisions / Input

No new owner decision is required. This is a bounded regression repair to a previously VERIFIED WI-3262 deterministic-service surface, using an existing active owner-approved PAUTH that includes WI-3262. The implementation does not mutate formal specs, MemBase, credentials, deployment state, or production systems.

## Requirement Sufficiency

Existing requirements are sufficient. The relevant requirements are already established by WI-3262, the original discoverability CLI implementation proposal, and the VERIFIED project-completion scanner API change. The repair is a compatibility update from the removed global scanner helper to the current project-scoped scanner helper.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py`
- `platform_tests/scripts/test_cli_backlog_status.py`

No other source, test, database, generated fixture, hook, or bridge file is authorized as implementation scope. Bridge report/verdict files and `bridge/INDEX.md` updates are protocol artifacts, not implementation target paths.

## Proposed Scope

1. In `cli_backlog_status.py`, replace the lazy import/use of `verified_work_items()` with `verified_work_items_by_project()`.
2. Keep `completion_ready(project_root)` behavior unchanged for `--with-retire-ready`.
3. Update verified coverage annotation to use the set for each project row's own project id: `verified_by_project.get(project_id, set())`.
4. Update the scanner caveat text so it references the canonical scanner thread's VERIFIED state rather than the stale pre-VERIFIED latest-GO/in-flight wording.
5. Update focused tests to monkeypatch `verified_work_items_by_project()` and assert project-scoped coverage behavior.
6. Run formatting on the two target files if required by repo tooling.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Source and tests contain no secrets or environment values. | Helper credential scan plus diff review. | |
| CQ-PATHS-001 | Yes | Mutate only the two approved in-root target paths. | `git diff --name-only -- groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py platform_tests/scripts/test_cli_backlog_status.py`. | |
| CQ-COMPLEXITY-001 | Yes | Keep the change to a direct API migration and project-row lookup. | Focused source review and full status test suite. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing scanner thread constants and project id fields; avoid parallel helper names. | Source review and `rg verified_work_items`. | |
| CQ-SECURITY-001 | Yes | Preserve read-only CLI behavior and avoid credential, auth, deployment, or network changes. | `test_status_makes_no_db_writes` plus diff review. | |
| CQ-DOCS-001 | Yes | Update user-facing scanner caveat to current VERIFIED scanner state. | `test_status_scanner_caveat_present_when_flags_set`. | |
| CQ-TESTS-001 | Yes | Update focused tests for `verified_work_items_by_project` and project-scoped coverage. | `python -m pytest platform_tests/scripts/test_cli_backlog_status.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | No runtime logging surface changes. | N/A. | This CLI status repair does not add or change logging. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, ruff check, ruff format-check, and live CLI smoke. | Commands listed in the implementation report. | |

## Specification-Derived Verification Plan

- `gt backlog status --with-retire-ready` still uses canonical scanner readiness: verify with `test_status_retire_ready_uses_scanner` using monkeypatched `completion_ready` and project-scoped coverage helper.
- `gt backlog status --with-verified-coverage` uses project-scoped VERIFIED coverage: verify with `test_status_verified_coverage_annotation` using `verified_work_items_by_project` returning coverage only for `PROJECT-GTKB-X`.
- Scanner caveat references the canonical scanner-fix thread and current VERIFIED state: verify with `test_status_scanner_caveat_present_when_flags_set`, including absence of withdrawn duplicate and stale in-flight wording.
- Base command remains scanner-import independent: verify with `test_status_base_has_no_scanner_dependency`.
- Read-only backlog behavior is preserved: verify with `test_status_makes_no_db_writes`.
- Full WI-3262 status matrix is preserved: run full `platform_tests/scripts/test_cli_backlog_status.py`.
- Code quality baseline for touched files is preserved: run ruff check and ruff format-check on the two target files.
- Live smoke for canonical DB proves no scanner import crash: run `gt backlog status --json` and `gt backlog status --with-verified-coverage --json`.

## Acceptance Criteria

- The focused `test_cli_backlog_status.py` suite returns all tests passing.
- `gt backlog status --with-retire-ready --json` and `gt backlog status --with-verified-coverage --json` no longer crash on the removed scanner helper.
- Coverage annotation uses project-scoped scanner results and does not reintroduce the removed global helper.
- Ruff check and format-check pass for the two target files.
- No MemBase, spec, bridge INDEX outside protocol, generated fixture, credential, or deployment mutation is performed by implementation code.

## Risks / Rollback

Risk: If callers expected global verified coverage, project-scoped coverage may appear narrower. That is intentional and matches the VERIFIED scanner fix at `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md`.

Rollback: revert the two target-file edits; the bridge artifacts remain append-only evidence of the attempted regression repair.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py`
- `platform_tests/scripts/test_cli_backlog_status.py`

## Recommended Commit Type

`fix`
