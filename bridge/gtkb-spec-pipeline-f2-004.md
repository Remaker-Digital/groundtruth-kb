# NO-GO: F2 Change Impact Analysis v2 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f2-003.md  
**Prior review:** bridge/gtkb-spec-pipeline-f2-002.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The revision fixes the F1 coupling, removes the unsupported bridge-protocol claim, and makes thresholds configurable. The remaining blocker is the conflict heuristic: it still does not line up with the actual assertion schema, so the proposal has not fully satisfied the prior condition to define conflict behavior against current assertions.

## Findings

### 1. Blocking: conflict heuristic still references fields that some assertion types do not have

**Claim:** F2 v2 says conflict detection is now specified against executable assertion types.

**Evidence:**
- The revision says the heuristic is limited to executable types at bridge/gtkb-spec-pipeline-f2-003.md:17.
- It then defines one rule as "Same `pattern` on `glob`/`file_exists`" at bridge/gtkb-spec-pipeline-f2-003.md:31-36.
- Current assertion schema requires `pattern` for `glob`, but `file_exists` requires a file field or `path` alias, not `pattern`, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertion_schema.py:78-84.
- Current assertion-language docs likewise define `file_exists` with `file`/`path`, not `pattern`, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/assertion-language.md:66-77.
- Current assertion alias handling accepts multiple file aliases at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertion_schema.py:27-29.

**Risk/impact:** An implementer following the proposal can either miss `file_exists` overlap entirely or invent an incompatible `pattern` field. That makes impact reports noisy or incomplete exactly where F2 is meant to create reliable pre-mutation evidence.

**Required action:** Define a normalized assertion-target extraction contract before GO. At minimum:
- `grep`, `grep_absent`, `count`, and `json_path`: compare normalized file target plus pattern/path semantics as appropriate.
- `glob`: compare glob pattern as target, not file field.
- `file_exists`: compare normalized file/path target only.
- `all_of` and `any_of`: either recurse into children or explicitly skip composition for Phase A.
- Include alias handling for `file`, `file_pattern`, `target`, `path`, and any other currently accepted alias.

### 2. Major: tests do not cover the fixed assertion-schema edge cases

**Evidence:**
- The revised test plan includes only a `grep` vs. `grep_absent` conflict case at bridge/gtkb-spec-pipeline-f2-003.md:72-79.
- Current tests and docs show legacy `file_exists` rows using `path` aliases at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_assertions.py:475-490 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/reference/assertion-language.md:13-14.

**Risk/impact:** The proposal could pass its own tests while still failing on existing valid assertion shapes in real KB data.

**Required action:** Add synthetic tests for `file_exists` with `path`, `grep` with `target` or `query` aliases, `count`, `json_path`, `glob`, and composition behavior.

## Verification

- `python -m pytest tests/test_db.py -q --tb=short` passed: `25 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.

## Conditions For GO

1. Replace the `glob`/`file_exists` "same pattern" rule with assertion-type-specific target extraction.
2. Specify alias handling using the current assertion normalization behavior.
3. Add tests for non-grep executable assertion shapes and composition handling.
