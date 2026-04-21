# NO-GO: F2 Change Impact Analysis v3 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f2-005.md
**Prior review:** bridge/gtkb-spec-pipeline-f2-004.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

F2 v3 fixes most of the prior assertion-alignment problem: it uses the current assertion normalization path, names the accepted aliases, and adds coverage for several non-grep shapes. One blocker remains. The proposal still does not define an implementable `json_path` target extraction contract even though `json_path` was explicitly part of the prior GO condition.

## Findings

### 1. Blocking: `json_path` conflict extraction is contradictory and under-tested

**Claim:** F2 v3 defines type-specific target extraction for current executable assertion types, including `json_path`.

**Evidence:**
- F2 v3's sample `_extract_target()` returns only `(file_target, pattern)` after `_normalize_assertion()` at bridge/gtkb-spec-pipeline-f2-005.md:23-35.
- The same proposal says `json_path` conflict detection should use "Same file + same JSON path" at bridge/gtkb-spec-pipeline-f2-005.md:47.
- The revised test plan says `count/json_path`, but the concrete test text only describes a `count` assertion with `file` and `pattern`; it does not require a `json_path` assertion with `file` and `path` at bridge/gtkb-spec-pipeline-f2-005.md:63.
- Current GT-KB `json_path` execution reads the file target from `file` and the JSON path expression from `path` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:403-413.
- Current `_normalize_assertion()` only maps `pattern`/`query` to canonical `pattern` and file aliases to canonical `file`; it does not map `path` into `pattern` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:137-160.

**Risk/impact:** An implementer following the sample extraction function will represent valid `json_path` assertions as `(file, None)`. That can either over-flag unrelated JSON path assertions in the same file or fail to detect path-specific conflicts. This keeps the impact report unreliable for one of the current executable assertion types.

**Required action:** Replace the two-tuple extraction contract with a typed target object, for example `{type, file_target, match_target}`, where `json_path` stores the JSON path expression from `path`. Add a synthetic test with a valid `json_path` assertion containing both `file` and `path`, and verify same-file/different-path cases are not collapsed.

## Verification

- `python -m pytest tests/test_db.py tests/test_deliberations.py tests/test_assertions.py -q --tb=short` passed: `168 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.
- `python -m ruff format --check src/ tests/` passed: `39 files already formatted`.

## Conditions For GO

1. Define typed extraction semantics for `json_path` instead of relying on `(file, pattern)`.
2. Add a `json_path` test that proves the JSON path expression is preserved and compared.
3. Keep the existing alias and composition handling from v3.
