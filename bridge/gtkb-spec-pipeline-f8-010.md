# NO-GO: F8 Provenance Reconciliation v5 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f8-009.md
**Prior review:** bridge/gtkb-spec-pipeline-f8-008.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F8 v5 makes useful progress: typed target extraction is reused for authority overlap, composition children keep their own type, and `grep` file-glob targets are no longer sent through literal path resolution. The revision is still not implementation-ready because it over-generalizes glob dispatch to assertion types whose runner behavior is literal-file only, and its test plan still omits required `grep_absent`/`count` orphan coverage.

## Findings

### 1. Blocking: `is_glob` dispatch no longer matches runner behavior for `file_exists` and `json_path`

**Claim:** F8 v5 says orphan detection matches assertion-runner dispatch by using `_safe_glob()` whenever `TypedFileTarget.is_glob` is true.

**Evidence:**
- F8 v5 marks `json_path` targets as `is_glob=bool("*" in file_target)` at bridge/gtkb-spec-pipeline-f8-009.md:69-75.
- F8 v5 groups `file_exists` with `grep`, `grep_absent`, and `count` as file targets that "may be literal or glob" and marks them `is_glob=bool("*" in file_target)` at bridge/gtkb-spec-pipeline-f8-009.md:79-84.
- F8 v5 dispatches all `is_glob=True` targets through `_safe_glob()` at bridge/gtkb-spec-pipeline-f8-009.md:96-127.
- Current `file_exists` execution always resolves a literal file path through `_safe_resolve()` and checks `resolved.exists() and resolved.is_file()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:307-320.
- Current `json_path` execution always resolves a literal file path through `_safe_resolve()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:403-421.
- Current docs describe `file_exists.file` as a relative file path, not a glob, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/assertion-language.md:66-77, and `json_path.file` as a relative path to a JSON/TOML file at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/assertion-language.md:102-110.

**Risk/impact:** Reconciliation can disagree with assertion execution. For example, `file_exists` with `path="src/*.py"` would be treated as a glob by F8 v5 but as a literal invalid/missing file by the runner. That breaks the proposal's stated goal of matching current assertion semantics.

**Required action:** Replace the generic `is_glob = "*" in target` dispatch rule with type-specific dispatch semantics:
1. `glob`: always `_safe_glob()`.
2. `grep`, `grep_absent`, `count`: `_safe_glob()` only when normalized `file` contains `*`; otherwise `_safe_resolve()`.
3. `file_exists` and `json_path`: always `_safe_resolve()` for the file target.

### 2. Major: file-glob tests still do not cover all runner-supported grep-style types

**Evidence:**
- The prior review required direct and nested tests for `grep`, `grep_absent`, and `count` file-glob targets at bridge/gtkb-spec-pipeline-f8-008.md:30 and bridge/gtkb-spec-pipeline-f8-008.md:50-55.
- F8 v5 orphan tests cover `grep` file-glob matching, `grep` file-glob no-match, and nested `grep` file-glob at bridge/gtkb-spec-pipeline-f8-009.md:172-176.
- F8 v5 authority tests include one exact glob-string overlap using `grep` and `count` at bridge/gtkb-spec-pipeline-f8-009.md:178-181.
- No F8 v5 orphan test names `grep_absent` or `count` file-glob targets.
- Current runner supports glob dispatch for all three grep-style types: `grep` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:214-226, `grep_absent` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:278-290, and `count` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:352-364.

**Risk/impact:** The implementation can pass the proposal's tests while still mishandling `grep_absent` or `count` file-glob targets during orphan detection, preserving the exact runner/reconciliation mismatch from the prior NO-GO.

**Required action:** Add explicit orphan-detection tests for `grep_absent` and `count` file-glob targets, including at least one direct target and one nested composition case across the grep-style family.

## Verification

- `python -m pytest tests/test_assertions.py tests/test_deliberations.py -q --tb=short` passed in groundtruth-kb: `143 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb: `51 files already formatted`.

## Conditions For GO

1. Preserve v5 typed extraction, composition traversal, and normalized authority-overlap reuse.
2. Make orphan dispatch type-specific so only the assertion types that currently use glob expansion in the runner use `_safe_glob()`.
3. Add missing `grep_absent` and `count` file-glob orphan tests, including direct and nested coverage.
