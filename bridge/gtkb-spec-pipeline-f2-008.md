# NO-GO: F2 Change Impact Analysis v4 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f2-007.md
**Prior review:** bridge/gtkb-spec-pipeline-f2-006.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F2 v4 fixes the prior `json_path` blocker by preserving the JSON path expression in a typed target. A remaining assertion-schema gap keeps the conflict detector from being implementation-ready: the proposal treats grep-style `file_target` values as literal canonical files, while current GT-KB execution allows those same fields to be glob patterns.

## Findings

### 1. Blocking: grep-style file globs have no conflict semantics

**Claim:** F2 v4 defines typed target extraction for current executable assertion types and uses those targets for conflict detection.

**Evidence:**
- F2 v4 extracts `file_target = normalized.get("file")` and then treats `grep`, `grep_absent`, `count`, and `file_exists` as a standard `(file, pattern)` pairing at bridge/gtkb-spec-pipeline-f2-007.md:49-80.
- Its conflict table says `grep`, `grep_absent`, and `count` use the canonical file plus pattern for conflict signals at bridge/gtkb-spec-pipeline-f2-007.md:85-92.
- Current assertion docs define `grep.file` as a "Relative file path or glob" at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/assertion-language.md:24-29.
- Current execution branches `grep` file targets containing `*` through `_safe_glob()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:214-226.
- Current execution does the same for `grep_absent` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:278-290 and for `count` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:352-364.
- Current tests explicitly cover `grep` with `file="**/*.py"` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_assertions.py:96-101 and `count` with `file="**/*.py"` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_assertions.py:580-588.
- F2 v4's revised test plan covers the `glob` assertion type and aliases, but not grep/count/grep_absent assertions whose `file` field is itself a glob, at bridge/gtkb-spec-pipeline-f2-007.md:99-111.

**Risk/impact:** Conflict detection can miss real overlap between a direct file assertion and a grep/count file-glob assertion, for example `file="src/api.py"` versus `file="src/**/*.py"` with the same pattern. That weakens the pre-mutation impact report in exactly the cases where one broad assertion governs many files.

**Required action:** Define target semantics for grep-style file fields that contain glob syntax. At minimum, choose and document one of:

1. Add a typed file target kind such as `literal_file`, `file_glob`, and `assertion_glob`, then compare literal-vs-glob and glob-vs-glob overlap reproducibly.
2. Require `compute_impact()` to accept `project_root` when conflict expansion needs filesystem-backed `_safe_glob()` behavior.
3. Explicitly limit Phase A conflict detection to exact target-string equality and document the file-glob false-negative class.

Add synthetic tests for `grep`, `grep_absent`, and `count` using file globs, including at least one direct-file versus file-glob overlap case.

## Verification

- `python -m pytest tests/test_assertions.py tests/test_deliberations.py -q --tb=short` passed: `143 passed, 1 warning`.
- `python -m ruff check .` passed: `All checks passed!`.
- `python -m ruff format --check .` passed: `51 files already formatted`.

## Conditions For GO

1. Preserve the v4 typed `json_path` target fix.
2. Define grep-style file-glob conflict behavior against current assertion execution semantics.
3. Add tests for grep/count/grep_absent file-glob targets and direct-file overlap.
