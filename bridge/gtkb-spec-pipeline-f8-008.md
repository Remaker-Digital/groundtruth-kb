# NO-GO: F8 Provenance Reconciliation v4 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f8-007.md
**Prior review:** bridge/gtkb-spec-pipeline-f8-006.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F8 v4 fixes the previous nested-`glob` composition bug by preserving each child target's assertion type. A more general orphan-detection mismatch remains: the proposal dispatches `grep`, `grep_absent`, and `count` targets only through `_safe_resolve()`, but current assertion execution treats those `file` fields as either literal files or glob patterns.

## Findings

### 1. Blocking: orphan detection still disagrees with runner behavior for grep-style file globs

**Claim:** F8 v4's orphan dispatch "matches the assertion runner."

**Evidence:**
- F8 v4 says `glob` targets use `_safe_glob()` and `grep`, `grep_absent`, `count`, `file_exists`, and `json_path` use `_safe_resolve()` at bridge/gtkb-spec-pipeline-f8-007.md:120-123.
- Its pseudocode sends every non-`glob` target through `_safe_resolve()` at bridge/gtkb-spec-pipeline-f8-007.md:95-117.
- Current assertion execution sends `grep` file targets containing `*` through `_safe_glob()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:214-226.
- Current assertion execution sends `grep_absent` file targets containing `*` through `_safe_glob()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:278-290.
- Current assertion execution sends `count` file targets containing `*` through `_safe_glob()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:352-364.
- Current docs define `grep.file` as a relative file path or glob at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/assertion-language.md:24-29.
- Current tests cover `grep` and `count` with `file="**/*.py"` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_assertions.py:96-101 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_assertions.py:580-588.
- F8 v4's revised tests cover the `glob` assertion type and nested `glob` composition, but not grep/count/grep_absent assertions whose `file` field is a glob pattern, at bridge/gtkb-spec-pipeline-f8-007.md:125-137.

**Risk/impact:** Reconciliation can falsely flag valid specs as orphaned when a `grep` or `count` assertion uses a matching file glob such as `**/*.py`, because `_safe_resolve("**/*.py")` checks a literal path instead of expanding the glob. It can also produce results inconsistent with `run_single_assertion()` and `run_all_assertions()`, undermining trust in F8 cleanup reports.

**Required action:** Dispatch file targets according to assertion-runner semantics, not only assertion type. For `grep`, `grep_absent`, and `count`, if the normalized file target contains glob syntax, use `_safe_glob()` and classify orphan status based on match count; otherwise use `_safe_resolve()`. Add direct and nested tests for grep/count/grep_absent file-glob targets.

### 2. Major: authority-conflict target overlap still uses literal `file` equality

**Evidence:**
- F8 v2 defines authority conflicts as same section/scope plus `_assertions_overlap()` at bridge/gtkb-spec-pipeline-f8-003.md:29-48.
- `_assertions_overlap` is then defined as any assertion from each spec targeting the same `file` value at bridge/gtkb-spec-pipeline-f8-003.md:51.
- Current assertion normalization accepts file aliases `file_pattern`, `target`, `path`, and `expected` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:132-160.
- Current execution recurses composition children through their own dispatch at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:472-483 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:502-516.

**Risk/impact:** The critical authority-conflict check can miss overlaps when one assertion uses a supported alias, a composition child, or a file glob. The orphan extractor in v4 is close to the right reusable primitive, but the proposal does not connect it back to authority conflicts.

**Required action:** Reuse the typed target extraction contract for authority-conflict overlap or define a separate normalized overlap algorithm with alias, composition, and file-glob behavior. Add tests proving authority conflicts are detected through `path`/`target` aliases, composition children, and file-glob overlap.

## Verification

- `python -m pytest tests/test_assertions.py tests/test_deliberations.py -q --tb=short` passed: `143 passed, 1 warning`.
- `python -m ruff check .` passed: `All checks passed!`.
- `python -m ruff format --check .` passed: `51 files already formatted`.

## Conditions For GO

1. Preserve the v4 typed target extraction fix for nested `glob` composition.
2. Match assertion-runner file-or-glob dispatch for `grep`, `grep_absent`, and `count`.
3. Normalize authority-conflict target overlap using the same alias/composition/file-glob semantics.
4. Add tests for direct and nested file-glob targets in orphan detection and authority conflicts.
