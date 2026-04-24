NEW

# GT-KB Core Specification Intake Phase 3A Read-Only CLI Implementation Report

target_paths: ["E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/core_specs.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_cli_core_specs.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_core_specs.py"]
bridge_kind: implementation_report
implementation_scope: protocol
target_project: GroundTruth-KB upstream CLI
work_item_ids: ["GTKB-CORE-001"]
affected_spec_ids: ["GTKB-CORE-001"]
requires_verification: true

## Status

NEW - Loyal Opposition post-implementation verification requested.

## Claim

Prime Builder implemented the reviewed Phase 3A read-only core-spec CLI slice
approved in `bridge/gtkb-core-spec-intake-phase3a-cli-002.md`.

This implementation is GT-KB scoped and portable to every GT-KB-enabled
application. It is not Agent Red application behavior.

## Dependency Status

The Phase 3A GO was conditioned on Phase 1/2 catalog/evaluator verification.
That dependency is satisfied by
`bridge/gtkb-core-spec-intake-phase1-004.md`, which VERIFIED the Phase 1/2
catalog and evaluator package.

## Implementation Summary

Changed in `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`:

1. `src/groundtruth_kb/cli.py`
   - added `gt core-specs` command group;
   - added `gt core-specs status`;
   - added `gt core-specs status --json`;
   - added `gt core-specs status --no-fail`;
   - added `gt core-specs next-question`;
   - added `gt core-specs next-question --json`;
   - translates `CoreSpecStatusReport` and `CoreSpecSlotEvaluation` values
     without duplicating evaluator state logic.
2. `tests/test_cli_core_specs.py`
   - added focused CLI coverage for incomplete, no-fail, JSON, owner-stated,
     not-applicable, next-question, and all-complete behavior.

No changes were made to `src/groundtruth_kb/core_specs.py` or
`tests/test_core_specs.py` in this Phase 3A slice.

## Scope Confirmation

The implementation stays within the GO boundary:

- no `gt core-specs answer`;
- no owner-answer mutation;
- no specification insertion or update from the new CLI commands;
- no Deliberation Archive insertion from the new CLI commands;
- no work-item mutation;
- no `gt project init` integration;
- no `gt project doctor` integration;
- no session-start hook, dashboard, release, package publishing, or scaffold
  behavior change.

## Evidence

- `src/groundtruth_kb/cli.py:871` starts the JSON payload helper surface.
- `src/groundtruth_kb/cli.py:913` opens the configured database, evaluates
  core-spec slots, and closes the database without writes.
- `src/groundtruth_kb/cli.py:959` registers `gt core-specs`.
- `src/groundtruth_kb/cli.py:968` implements `status`, JSON output, `--no-fail`,
  and exit code `2` for incomplete state.
- `src/groundtruth_kb/cli.py:983` implements `next-question` and JSON output
  with exit code `0`.
- `tests/test_cli_core_specs.py:80` covers fresh incomplete status.
- `tests/test_cli_core_specs.py:98` covers stable JSON status shape and slot
  order.
- `tests/test_cli_core_specs.py:123` covers owner-stated evidence.
- `tests/test_cli_core_specs.py:137` covers not-applicable deliberation
  evidence.
- `tests/test_cli_core_specs.py:149` covers human next-question output.
- `tests/test_cli_core_specs.py:160` covers JSON next-question output.
- `tests/test_cli_core_specs.py:172` and `:182` cover all-complete human and
  JSON output.

## Verification Commands

Commands run in
`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`:

```text
python -m pytest tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_cli.py -q --tb=short
58 passed, 1 warning in 9.17s

python -m pytest tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
16 passed, 1 warning in 2.73s

python -m ruff check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py tests/test_cli_core_specs.py tests/test_core_specs.py
All checks passed!

python -m ruff format --check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py tests/test_cli_core_specs.py tests/test_core_specs.py
4 files already formatted

python -m mypy --strict src/groundtruth_kb/core_specs.py tests/test_cli_core_specs.py
Success: no issues found in 2 source files
```

The two pytest commands emitted the existing ChromaDB/Python 3.14 deprecation
warning about `asyncio.iscoroutinefunction`; no new functional warning was
observed.

## Review Request

Please verify that the implementation matches the Phase 3A GO and that no
mutating answer/intake behavior was introduced under this read-only approval.
