# GO: GroundTruth-KB Phase 4B.2 Medium Config Defensiveness Review

**Document:** `gtkb-phase4b2-medium-defensiveness`
**Reviewed proposal:** `bridge/gtkb-phase4b2-medium-defensiveness-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14
**Verdict:** GO, with implementation conditions below

## Rationale

The proposal targets the three config-defensiveness findings that were
explicitly deferred from Phase 4B.1. The current GroundTruth-KB baseline at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` still exhibits all three
behaviors: `PermissionError` propagates raw, missing `[groundtruth]` is silent,
and unknown `[groundtruth]` keys are silently ignored. The proposed changes are
small, testable, and scoped to `config.py`, config docs, changelog, and
`tests/test_config.py`.

I found no blocking reason to split the work. Two warning-design details need
conditions so the fix does not introduce misleading warnings for valid config
shapes.

## Evidence

### Baseline and audit claims

GroundTruth-KB baseline reviewed:

```text
git rev-parse --short HEAD
-> b41ab8f
```

The source audit identifies the exact deferred findings:

- Finding 4: `docs/reports/v0.4-baseline/config-errors.md:56` says
  `open(config_path, "rb")` can raise uncaught `PermissionError`; line 61
  recommends wrapping it with a clearer config-file message.
- Finding 5: `docs/reports/v0.4-baseline/config-errors.md:63` covers a TOML
  file with no `[groundtruth]` section; line 70 recommends a one-line notice.
- Finding 6: `docs/reports/v0.4-baseline/config-errors.md:72` covers unknown
  `[groundtruth]` keys; lines 74-78 identify the silent drop as the issue.

Current code evidence:

- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\config.py:27`
  defines `GTConfigError`; lines 35-41 still say `PermissionError` is deferred
  to Phase 4B.2.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\config.py:130`
  opens the file and catches only `tomllib.TOMLDecodeError` at line 133.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\config.py:136`
  uses `data.get("groundtruth", {})`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\config.py:99`
  filters merged keys through `cls.__dataclass_fields__`, silently dropping
  unknown keys.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reference\configuration.md:191`
  documents `PermissionError` as pass-through, so docs must change with the
  implementation.

Behavior check against current `b41ab8f`:

```text
permission_exception_type= PermissionError
is_gtconfigerror= False
cause_type= None
missing_section_warning_count= 0
missing_section_title= GroundTruth KB
unknown_key_warning_count= 0
unknown_key_title= ok
unknown_key_brand_color= #2563eb
```

Existing config test baseline:

```text
python -B -m pytest tests/test_config.py -q --tb=short -p no:cacheprovider
-> 15 passed, 1 warning in 0.16s

python -B -c "import groundtruth_kb; print(len(groundtruth_kb.__all__))"
-> 16
```

### Proposal scope

The expected file touchpoints are appropriate:

- `tests/test_config.py` for tests-first coverage.
- `src/groundtruth_kb/config.py` for the exception and warning behavior.
- `docs/reference/configuration.md` for user-facing exception/warning docs.
- `CHANGELOG.md` for the Unreleased note.

No new public symbol is needed. `__all__` should remain at 16.

## Required Conditions

1. Preserve the tests-first sequence. The post-implementation report must
   include the red-state result for the four new tests or explicitly state if
   the red checkpoint was not run.

2. `PermissionError` must be wrapped in `GTConfigError` with the config path
   and a permissions hint in the message, and the original `PermissionError`
   must be chained via `__cause__`. Keep explicit missing paths as
   `FileNotFoundError`; do not broaden the catch into a generic `OSError`
   wrapper in this sub-round.

3. The missing `[groundtruth]` warning must not imply that the whole TOML file
   is ignored when supported non-core sections are present. `config.py`
   currently supports `[gates]` at
   `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\config.py:139`
   and `[search]` at
   `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\config.py:149`.
   Either suppress the missing-section warning when the file contains only
   recognized non-core sections, or use wording that says core `[groundtruth]`
   settings will fall back to defaults/env/overrides while `[gates]` and
   `[search]` remain honored.

4. Warning `stacklevel` should point at the external `GTConfig.load()` call
   site where practical. If the missing-section warning is emitted inside the
   `_load_toml()` helper, `stacklevel=2` points to the internal call in
   `config.py`; use a stacklevel or call location that makes the warning useful
   to library callers. The unknown-key warning emitted from `GTConfig.load()`
   can use `stacklevel=2`.

5. The unknown-key warning must name the ignored key or keys, and it must not
   warn for supported values routed from `[gates]`, `[gates.config.*]`, or
   `[search].chroma_path`. Those already map to dataclass fields and should
   remain legitimate config.

6. Update `docs/reference/configuration.md` so the Exceptions section no longer
   describes `PermissionError` as pass-through, and add a concise Warnings
   section documenting missing `[groundtruth]` and unknown-key behavior.

7. Preserve the proposed verification gate:

```text
python -m pytest tests/test_config.py -q --tb=short
python -m pytest -q --tb=short -p no:cacheprovider
python -m ruff check .
python -m ruff format --check .
python scripts/check_docs_cli_coverage.py
python -c "from groundtruth_kb import __all__; print(len(__all__))"
```

Expected final results: `tests/test_config.py` grows from 15 to 19 tests, full
suite grows from 632 to 636 passing tests, and `__all__` remains 16.

## Decision

GO. Prime may implement Phase 4B.2 under the conditions above. The only
material adjustments are warning wording/scope and warning stacklevel; neither
invalidates the proposed implementation direction.
