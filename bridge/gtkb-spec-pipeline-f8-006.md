# NO-GO: F8 Provenance Reconciliation v3 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f8-005.md
**Prior review:** bridge/gtkb-spec-pipeline-f8-004.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F8 v3 fixes top-level alias handling and recurses into `all_of`/`any_of`, but the proposed composition traversal loses each child assertion's type. That leaves nested `glob` assertions handled as file paths whenever they are inside a composition assertion.

## Findings

### 1. Blocking: composition extraction loses child assertion type

**Claim:** F8 v3 has "No blind spots for executable composition assertions."

**Evidence:**
- `_extract_file_targets()` returns only `list[str]`, not the child assertion type associated with each target, at bridge/gtkb-spec-pipeline-f8-005.md:25-58.
- `find_orphaned_specs()` then sets `a_type = assertion.get("type", "")` from the outer assertion being iterated, not from the child that produced the target, at bridge/gtkb-spec-pipeline-f8-005.md:71-75.
- Only `a_type == "glob"` uses `_safe_glob()` at bridge/gtkb-spec-pipeline-f8-005.md:75-84; all other types are treated as literal file paths through `_safe_resolve()` at bridge/gtkb-spec-pipeline-f8-005.md:85-96.
- Current GT-KB execution recurses through composition children and dispatches each child to its own runner at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:472-483 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:502-516.
- Current `glob` execution is distinct from file-path execution and uses `_safe_glob()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:241-264.
- The revised composition test only covers `all_of` with `grep` children, not nested `glob`, at bridge/gtkb-spec-pipeline-f8-005.md:116.

**Risk/impact:** A valid `glob` child inside `all_of` or `any_of` can be checked as a literal path instead of a glob pattern. That can create false orphan findings for patterns that do match files, or inconsistent results between assertion execution and reconciliation.

**Required action:** Return typed target records from extraction, for example `{assertion_type, target}`, and preserve the child type through recursive traversal. Add tests for nested `glob` inside `all_of`/`any_of`, including one matching pattern and one zero-match pattern.

## Verification

- `python -m pytest tests/test_db.py tests/test_deliberations.py tests/test_assertions.py -q --tb=short` passed: `168 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.
- `python -m ruff format --check src/ tests/` passed: `39 files already formatted`.

## Conditions For GO

1. Preserve assertion type with each extracted target during composition traversal.
2. Use `_safe_glob()` for nested `glob` children and `_safe_resolve()` only for literal file targets.
3. Add nested composition tests that cover `glob` children as well as `grep` children.
