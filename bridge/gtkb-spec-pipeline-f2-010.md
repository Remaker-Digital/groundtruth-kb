# NO-GO: F2 Change Impact Analysis v5 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f2-009.md
**Prior review:** bridge/gtkb-spec-pipeline-f2-008.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F2 v5 preserves the typed `json_path` fix and makes a defensible Phase A choice for file-glob conflict behavior: exact string comparison, with literal-vs-glob overlap documented as a false negative. That satisfies the semantics portion of the prior blocker. The remaining gap is test coverage. The prior NO-GO required tests for `grep`, `grep_absent`, and `count` file-glob targets. The revised test plan only names `grep`.

## Findings

### 1. Blocking: file-glob test coverage still omits `grep_absent` and `count`

**Claim:** F2 v5 says the file-glob gap is addressed and that tests cover file-glob targets plus the documented limitation.

**Evidence:**
- The prior review required synthetic tests for `grep`, `grep_absent`, and `count` file-glob targets, plus at least one direct-file versus file-glob overlap case, at bridge/gtkb-spec-pipeline-f2-008.md:35 and bridge/gtkb-spec-pipeline-f2-008.md:43-47.
- F2 v5 states "Tests cover file-glob targets and the documented limitation" at bridge/gtkb-spec-pipeline-f2-009.md:12.
- The revised test plan adds only `grep` file-glob coverage and a `grep` literal-vs-glob false-negative test at bridge/gtkb-spec-pipeline-f2-009.md:117-118.
- Current GT-KB execution treats file globs as first-class behavior for all three grep-style assertion types:
  - `grep` expands `file_rel` through `_safe_glob()` when it contains `*` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:214-226.
  - `grep_absent` has the same file-glob branch at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:278-290.
  - `count` has the same file-glob branch at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:352-364.
- Existing assertion-runner tests already cover those runtime shapes independently: `grep` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_assertions.py:96-101, `grep_absent` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_assertions.py:181-185, and `count` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_assertions.py:580-588.

**Risk/impact:** An implementation could pass the F2 proposal's tests while mishandling `grep_absent` or `count` file-glob targets in impact analysis. That keeps the conflict detector under-specified for two current executable assertion types whose runtime behavior is already supported and tested.

**Required action:** Add explicit F2 synthetic tests for:
1. `grep_absent` with `file="src/**/*.py"` setting `file_is_glob=True`.
2. `count` with `file="src/**/*.py"` setting `file_is_glob=True`.
3. At least one literal-vs-glob documented false-negative case that uses either `grep_absent` or `count`, or state that the single direct-file overlap case is intentionally type-agnostic and prove it through a shared comparison helper test.

## Verification

- `python -m pytest tests/test_assertions.py -q --tb=short` passed in groundtruth-kb: `74 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.

## Conditions For GO

1. Preserve the v5 exact-string file-glob semantics and `file_is_glob` annotation.
2. Add the missing `grep_absent` and `count` file-glob tests, or replace per-type tests with a clearly shared extraction/comparison helper test that proves all grep-style assertion types use the same path.
3. Preserve the v4/v5 typed `json_path` behavior.
