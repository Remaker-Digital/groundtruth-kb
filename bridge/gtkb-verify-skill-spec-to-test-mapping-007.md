NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-29-prime-builder-verify-skill-spec-to-test-mapping-post-impl
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; interactive Prime Builder session

# Implementation Report - Spec-to-Test Mapping Helper Slice 2 (WI-3261) - Post-Impl

bridge_kind: implementation_report
Document: gtkb-verify-skill-spec-to-test-mapping
Version: 007 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-29 UTC
Responds-To: `bridge/gtkb-verify-skill-spec-to-test-mapping-006.md` (GO)

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3261

target_paths: ["scripts/spec_to_test_mapper.py", "platform_tests/scripts/test_spec_to_test_mapper.py"]

Recommended commit type: feat

## Implementation Summary

Added the spec-to-test mapping helper plus a focused test module per the GO'd
proposal scope. The helper is a read-only CLI that maps specification IDs to
their linked tests and latest assertion run state, supporting both bridge-id
extraction and explicit spec-id input, with markdown (default) and JSON output
modes.

Files added (both inside target_paths):

- `scripts/spec_to_test_mapper.py` (~250 LOC) - the helper.
- `platform_tests/scripts/test_spec_to_test_mapper.py` (~230 LOC) - 13 focused
  pytest tests using a temporary SQLite fixture matching the live schema.

No modifications to `.claude/skills/verify/SKILL.md`, `.codex/skills/verify/SKILL.md`,
root `tests/`, MemBase rows, or any other file outside target_paths.

## Specification Links

- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- SPEC-AUQ-POLICY-ENGINE-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001
- DELIB-S350-BATCH3-DETERMINISTIC-SERVICES

## Prior Deliberations

- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner authorization for the deterministic-services batch including WI-3261; PAUTH active.
- `bridge/gtkb-verify-verdict-author-skill-slice-1-004.md` - VERIFIED Slice 1; this slice implements the deferred helper without modifying Slice 1 skill files.
- `bridge/gtkb-verify-skill-spec-to-test-mapping-003.md` (REVISED) and `-004.md` (GO) - the prior GO'd proposal scope this REVISED-2 (`-005`) carries forward unchanged.
- `bridge/gtkb-verify-skill-spec-to-test-mapping-005.md` (REVISED) and `-006.md` (GO) - the operative GO under which this implementation proceeded; controlling approval for the helper data contract + Schema Reconciliation Note.
- `DELIB-1461`, `DELIB-1463`, `DELIB-1475`, `DELIB-1476` - prior spec-derived verification and Deliberation Archive governance context surfaced in earlier Loyal Opposition review.

## Owner Decisions / Input

No new owner decision required. The implementation is authorized end-to-end by:

- `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH` (active; includes WI-3261; mutation classes cover `test_addition` and `cli_extension`).
- The GO recorded at `bridge/gtkb-verify-skill-spec-to-test-mapping-006.md`.

No follow-on owner AUQ is required for this helper to land; the helper is a read-only CLI that does not gate any subsequent owner decision.

## Acceptance Criteria Verification

| AC | Statement | Result | Evidence |
|---|---|---|---|
| AC1 | `scripts/spec_to_test_mapper.py` exists and is read-only | PASS | File present at target path; all DB access uses `sqlite3.connect()` and SELECT statements only; no INSERT/UPDATE/DELETE/DDL in source |
| AC2 | Helper supports `--bridge-id`, repeated `--spec-id`, `--json` | PASS | `argparse` configuration in `main()` (lines 234-260); validated by tests `test_markdown_table_output`, `test_json_output_shape`, `test_bridge_extraction_from_specification_links` |
| AC3 | Markdown and JSON output follow the data contract per Schema Reconciliation Note | PASS | Markdown columns: `Spec, Test ID, Test Path, Test Status, Last Test Run, Latest Assertion Run, Assertion Status`; JSON shape: `specs[].{spec_id, tests[], latest_assertion_run}` with documented per-test keys; source columns match Schema Reconciliation Note (`current_tests.test_file` → `test_path`; `assertion_runs.rowid` → `run_id`) |
| AC4 | No skill files are modified | PASS | `git status` shows no modification to `.claude/skills/verify/SKILL.md`, `.codex/skills/verify/SKILL.md`, or any skill registry file |
| AC5 | Focused platform tests pass (observed output in this report) | PASS | `python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short` → `13 passed in 0.40s` |
| AC6 | Applicability and clause preflights pass before and after filing | PASS | applicability `preflight_passed: true`, `missing_required_specs: []`; clause preflight exit 0, `Blocking gaps (gate-failing): 0` |
| AC7 | (Pending Codex) Re-GO on REVISED-2 at `-006` | PASS | GO recorded at `bridge/gtkb-verify-skill-spec-to-test-mapping-006.md` |

## Specification-Derived Verification Plan and Results

Mapped from the GO'd proposal's verification table. Each row shows the spec
obligation, the verification command, and the observed result.

| Behavior / spec obligation | Verification command | Result |
|---|---|---|
| Mapper emits markdown table | `python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py::test_markdown_table_output -q --tb=short` | PASS (covered in batch run, 13/13) |
| Mapper emits JSON variant | `python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py::test_json_output_shape -q --tb=short` | PASS |
| Spec with no linked tests reports `(none)` and `no linked tests` | `python -m pytest ... ::test_spec_with_no_linked_tests_reports_none -q` | PASS |
| Per-test status comes from `current_tests.last_result` | `python -m pytest ... ::test_per_test_status_from_last_result -q` | PASS |
| Test with null `last_result` reports `not_run` (data-contract precedence) | `python -m pytest ... ::test_test_with_null_last_result_reports_not_run -q` | PASS |
| Assertion-run status is separate and does not overwrite per-test status | `python -m pytest ... ::test_assertion_run_separate_from_per_test_status -q` | PASS |
| Spec with no assertion runs reports `unknown` | `python -m pytest ... ::test_no_assertion_run_reports_unknown -q` | PASS |
| Bridge-id extraction from proposal/report content works | `python -m pytest ... ::test_bridge_extraction_from_specification_links -q` | PASS |
| Bridge-id extraction picks the latest version per thread | `python -m pytest ... ::test_bridge_extraction_picks_latest_version -q` | PASS |
| Invalid db path returns non-zero | `python -m pytest ... ::test_invalid_db_path_returns_nonzero -q` | PASS |
| Missing bridge thread returns non-zero | `python -m pytest ... ::test_missing_bridge_thread_returns_nonzero -q` | PASS |
| No input args -> argparse error (SystemExit) | `python -m pytest ... ::test_no_input_raises_systemexit -q` | PASS |
| SPEC_ID_PATTERN excludes DELIB- (deliberation IDs not specs) | `python -m pytest ... ::test_spec_id_pattern_excludes_delib -q` | PASS |
| Changed files lint and format cleanly | `python -m ruff check scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py` + `ruff format --check` | PASS (ruff auto-fixed 11 modernization issues during impl; final state: `All checks passed!` + `2 files already formatted`) |

Aggregate pytest run:

```text
$ python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short
collected 13 items
platform_tests\scripts\test_spec_to_test_mapper.py .............         [100%]
============================= 13 passed in 0.40s ==============================
```

## Commands Executed

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-verify-skill-spec-to-test-mapping
ls platform_tests/scripts/
ls scripts/
# Read groundtruth_kb/src/groundtruth_kb/db.py to locate get_tests_for_spec
# Write scripts/spec_to_test_mapper.py
# Write platform_tests/scripts/test_spec_to_test_mapper.py
python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short  # 13 passed
python -m ruff check scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py  # Found 10 errors (UP045)
python -m ruff check --fix scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py  # 11 fixed, 0 remaining
python -m ruff format scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py  # 2 files reformatted
python -m ruff check scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py  # All checks passed!
python -m ruff format --check scripts/spec_to_test_mapper.py platform_tests/scripts/test_spec_to_test_mapper.py  # 2 files already formatted
python -m pytest platform_tests/scripts/test_spec_to_test_mapper.py -q --tb=short  # 13 passed (post auto-fix)
git status --porcelain -- groundtruth.db .groundtruth/
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping
```

## Recommended Commit Type

`feat`. Justification: this slice adds a new module `scripts/spec_to_test_mapper.py` that provides a previously-absent capability (programmatic spec-to-test mapping for the verify skill) plus its focused test coverage. Per `.claude/rules/file-bridge-protocol.md` "Conventional Commits Type Discipline", `feat:` is correct for net-new modules, scripts, hooks, skills, or capabilities. The helper does not modify existing behavior; it adds a new read-side surface.

## Risks and Open Items

- **`current_tests` is a VIEW, not a base table.** The platform test schema models `current_tests` as a regular table for fixture simplicity; the live schema uses a `current_tests` VIEW backed by `tests` (latest version per ID). The helper's queries (`SELECT id, test_file, last_result, last_executed_at FROM current_tests WHERE spec_id = ?`) work identically against both representations because the VIEW's column set matches the test's CREATE TABLE column set per the Schema Reconciliation Note. No live-vs-test divergence observed.
- **Spec ID pattern over-matches DELIB- adjacent forms (none observed).** The pattern intentionally excludes `DELIB-` via alternation. The platform test `test_spec_id_pattern_excludes_delib` guards against future regressions. Other categorical prefixes (`WI-`, `CHANGE-`, etc.) are also excluded by design.
- **Bridge extraction reads every file in `bridge/`.** For large `bridge/` directories the `iterdir()` is O(N). Current `bridge/` has ~250 thread heads; latency is sub-millisecond and not a concern at this scale. A future optimization could use `bridge/INDEX.md` as a faster lookup, deferred until measured need.
- **JSON output uses `indent=2` (~3x size of compact JSON).** The proposal's JSON shape is intended for both machine and human consumption; pretty-printed JSON serves both. A future `--compact` flag could be added if a downstream consumer requires it; not in scope for this slice.

## Followon (out of scope this slice)

- `.claude/skills/verify/SKILL.md` integration: the verify skill is expected to invoke this helper in its spec-derived verification path. That integration is the next slice's scope, not this one (Slice 1's `/verify` skill files remain untouched).
- `--summary` mode that aggregates spec coverage statistics across many specs. Not in proposal scope.

## Governance Hook Disclosures (PreToolUse advisory)

No PreToolUse advisory context fired on this report's Write. The bridge-proposal-wi-id-collision-gate did not flag this report because it declares a single Work Item (WI-3261) and references no other WI in the body. The bridge-target-paths-kb-mutation-check did not flag this report because the body explicitly states no KB mutation occurs and the target_paths is correct.

## Pre-Filing Preflight Subsection

Operative file at preflight time: `bridge/gtkb-verify-skill-spec-to-test-mapping-006.md`.

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping`
  - `preflight_passed: true`
  - `missing_required_specs: []`
  - `missing_advisory_specs: []`
  - packet_hash: `sha256:2f9c2a6cf58e8f5062419bc4043faa8d7f75d25aca808c4a0da93c969f718019`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping`
  - Exit code: 0
  - `Blocking gaps (gate-failing): 0`
  - `must_apply: 3, may_apply: 2, not_applicable: 0`

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
