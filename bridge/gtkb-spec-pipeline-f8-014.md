# GO: F8 Provenance Reconciliation v7 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f8-013.md
**Prior review:** bridge/gtkb-spec-pipeline-f8-012.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** GO

## Rationale

F8 v7 addresses the remaining plain-text assertion blocker while preserving the v6 type-specific dispatch model. The proposal now mirrors the current assertion runner's skip behavior for non-dict assertions and retains the earlier alignment for aliases, composition traversal, glob-capable assertion types, literal-only assertion types, authority overlap, and orphan detection.

## Findings

### 1. Resolved: plain-text assertions are now safely skipped

**Evidence:**
- The prior NO-GO required non-dict guards because current assertion validation treats plain-text assertions as valid human notes and current execution skips them at bridge/gtkb-spec-pipeline-f8-012.md:47-51.
- F8 v7 adds `if not isinstance(assertion, dict): return []` before reading assertion fields at bridge/gtkb-spec-pipeline-f8-013.md:39-46.
- F8 v7's composition recursion sends children back through `_extract_file_targets()`, so plain-text children hit the same guard at bridge/gtkb-spec-pipeline-f8-013.md:53-61.
- Current GT-KB assertion validation returns no errors for non-dict assertions at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertion_schema.py:52-62.
- Current assertion execution skips non-dict assertions at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:551-554.

**Impact:** Reconciliation can traverse mixed machine and human assertion lists without aborting the full report.

### 2. Preserved: orphan dispatch matches current runner file-target semantics

**Evidence:**
- F8 v7 keeps `_GLOB_CAPABLE_TYPES = {"grep", "grep_absent", "count"}` and sets `use_glob` only for those types when `*` appears in the normalized file target at bridge/gtkb-spec-pipeline-f8-013.md:29 and bridge/gtkb-spec-pipeline-f8-013.md:86-93.
- F8 v7 keeps `glob` assertions on glob dispatch at bridge/gtkb-spec-pipeline-f8-013.md:63-71.
- F8 v7 keeps `json_path` and `file_exists` on literal resolution at bridge/gtkb-spec-pipeline-f8-013.md:74-84.
- Current runner dispatches `grep`, `grep_absent`, and `count` through `_safe_glob()` only when the file target contains `*` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:214-226, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:278-290, and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:352-364.
- Current runner always resolves `file_exists` and `json_path` as literal files at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:305-320 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:403-421.

**Impact:** The proposal is implementation-ready for Phase A reconciliation without the earlier runner/reconciliation mismatch.

## Required Implementation Conditions

1. Implement the v7 non-dict guard exactly at the extractor entry point.
2. Preserve the v6/v7 type-specific `use_glob` rules for `glob`, `grep`, `grep_absent`, `count`, `file_exists`, and `json_path`.
3. Add the 20 proposed tests, including top-level plain-text, composition plain-text child, non-machine dict, direct and nested grep-style file-glob coverage, and authority-overlap coverage.

## Verification

- `python -m pytest tests/test_assertions.py tests/test_deliberations.py tests/test_cli.py -q --tb=short` passed in groundtruth-kb: `177 passed, 1 warning`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb: `51 files already formatted`.
