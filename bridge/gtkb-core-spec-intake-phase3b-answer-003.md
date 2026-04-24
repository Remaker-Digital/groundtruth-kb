NEW

# GT-KB Core Specification Intake Phase 3B Answer Command Post-Implementation Report

**Status:** NEW
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Implementation scope:** `gt core-specs answer`
**Reviewed GO:** `bridge/gtkb-core-spec-intake-phase3b-answer-002.md`
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

Implemented the narrow Phase 3B mutating `gt core-specs answer` command under
the Loyal Opposition GO conditions.

This implementation does not add project-init prompting, doctor integration,
session-start integration, dashboard integration, package release, Agent Red
application behavior, deployment, push, merge, or automatic mutation from
`status` or `next-question`.

## Implemented Changes

- Added catalog-level `not_applicable_allowed` metadata to each core spec slot
  so not-applicable eligibility is machine-readable rather than inferred from
  prose.
- Added deterministic evidence ID helpers:
  - `core_spec_answer_spec_id(handle)`
  - `core_spec_not_applicable_deliberation_id(handle)`
- Added `gt core-specs answer <handle>` with:
  - `--text` for owner-stated answer capture;
  - `--not-applicable --reason` for explicit owner-decision deliberation
    capture;
  - `--force-not-applicable` for audited exceptions on normally required slots;
  - `--dry-run`;
  - `--json`.
- Persisted owner-stated answers as current specs with stable handle, slot tag,
  `authority="stated"`, deterministic spec ID, non-empty title/description,
  and `changed_by` / `change_reason` provenance identifying core-spec intake.
- Persisted not-applicable answers as canonical owner-decision deliberations
  using `core_spec_not_applicable_source_ref(handle)`, without creating fake
  requirement specs.
- Preserved read-only behavior for `gt core-specs status` and
  `gt core-specs next-question`.

## Files Changed In Target Checkout

- `src/groundtruth_kb/core_specs.py`
- `src/groundtruth_kb/cli.py`
- `tests/test_core_specs.py`
- `tests/test_cli_core_specs.py`

The target checkout already contained uncommitted Phase 3A/protocol work before
this implementation. This report describes only the Phase 3B additions made in
this pass.

## GO Condition Mapping

1. **Machine-readable not-applicable eligibility:** satisfied by
   `CoreSpecSlot.not_applicable_allowed` and tests proving `core-identity` is
   blocked by default while `core-ai` is allowed.
2. **Stable owner-stated answer evidence:** satisfied by deterministic
   `SPEC-{HANDLE}` IDs, update-on-repeat behavior, handle/tag preservation,
   `authority="stated"`, and provenance tests.
3. **Not-applicable remains deliberation evidence:** satisfied by deterministic
   `DELIB-{HANDLE}-NOT-APPLICABLE` IDs, canonical `source_ref`, and tests
   proving no fake spec is created.
4. **Dry-run and read-only commands remain non-mutating:** satisfied by dry-run
   no-write coverage plus explicit status/next-question read-only regression
   coverage.

## Verification

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m pytest tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_intake.py -q --tb=short
69 passed, 1 warning in 15.18s
```

```text
python -m pytest tests/test_cli.py tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
51 passed, 1 warning in 9.14s
```

```text
python -m ruff check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py src/groundtruth_kb/intake.py tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_intake.py
All checks passed!
```

```text
python -m ruff format --check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py src/groundtruth_kb/intake.py tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_intake.py
6 files already formatted
```

```text
python -m mypy --strict src/groundtruth_kb/core_specs.py tests/test_cli_core_specs.py
Success: no issues found in 2 source files
```

The warning in both pytest commands is the existing ChromaDB/Python
deprecation warning for `asyncio.iscoroutinefunction`; it is not specific to
this implementation.

## Decision Needed From Owner

None for this post-implementation verification request.

Loyal Opposition verification is requested for the implemented Phase 3B slice.
