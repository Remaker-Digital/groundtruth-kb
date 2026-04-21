# NO-GO: F8 Provenance Reconciliation v2 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f8-003.md  
**Prior review:** bridge/gtkb-spec-pipeline-f8-002.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The revision fixes the major dependency problems: it uses `authority`, makes F7 optional with a timestamp fallback, adds `project_root`, and avoids depending on F2 for authority overlap. One orphan-detection blocker remains: the proposed logic skips assertions without a literal `file` field, but current GT-KB assertion execution supports file aliases such as `path`, `target`, and `file_pattern`.

## Findings

### 1. Blocking: orphan detection would miss valid assertion file aliases

**Claim:** F8 v2 orphan detection is consistent with the current assertion runner because it accepts `project_root` and uses `_safe_resolve()`.

**Evidence:**
- F8 v2 adds `project_root` and says orphan detection uses `_safe_resolve()` at bridge/gtkb-spec-pipeline-f8-003.md:56-67.
- It exempts "Assertions without a `file` field" at bridge/gtkb-spec-pipeline-f8-003.md:68-72.
- Current assertion normalization maps `file_pattern`, `target`, `path`, and `expected` to canonical `file` before dispatch at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:132-160 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:551-570.
- Current docs show `file_exists` with `path` as a supported shape at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/assertion-language.md:13-14 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/assertion-language.md:66-77.
- Current tests preserve that legacy `path` shape at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_assertions.py:475-490.

**Risk/impact:** Orphan detection can falsely report a spec as not checkable, or miss a deleted file, whenever the assertion uses an accepted alias instead of a literal `file` key. That undermines the main F8 cleanup path for existing KB data.

**Required action:** Specify that orphan detection normalizes assertions with the same alias behavior as execution before deciding whether a file target exists. Add tests for `file_exists` with `path`, `grep` with `target`, `grep` with `query`, and direct `file`.

### 2. Major: composition behavior is not specified for orphan detection

**Evidence:**
- Current executable assertion types include `all_of` and `any_of` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:39-48.
- Current dispatch recurses through composition assertions during execution at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:540-548.
- F8 v2 orphan detection exemptions and test plan do not say whether `all_of`/`any_of` children are traversed at bridge/gtkb-spec-pipeline-f8-003.md:68-72 and bridge/gtkb-spec-pipeline-f8-003.md:148-155.

**Risk/impact:** Orphan detection can miss file targets nested inside current executable composition assertions.

**Required action:** Either recurse into `all_of`/`any_of` children using the same assertion normalization path or explicitly skip composition in Phase A and document the blind spot.

## Verification

- `python -m pytest tests/test_db.py -q --tb=short` passed: `25 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.

## Conditions For GO

1. Normalize assertion aliases before orphan target checks.
2. Specify composition traversal or explicitly defer it.
3. Add orphan tests for alias-backed file targets and nested executable assertions.
