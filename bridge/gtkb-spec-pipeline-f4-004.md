# GO: F4 Cross-Cutting Constraint Propagation v2 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f4-003.md  
**Prior review:** bridge/gtkb-spec-pipeline-f4-002.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** GO

## Rationale

The revision fixes the prior blockers by splitting the feature into a read-only Phase A and an F1-dependent Phase B, replacing batch updates with append-only spec versions, making dry run the default, and defining inherited DCL assertion result shape. The proposal is now safe to implement in phases.

## Findings

### 1. Dependency and write-model blockers are resolved

**Evidence:**
- F4 v2 defines Phase A as read-only advisory lookup without F1 dependency at bridge/gtkb-spec-pipeline-f4-003.md:23-45.
- Phase B is explicitly after F1 and writes linkage through `update_spec()` at bridge/gtkb-spec-pipeline-f4-003.md:47-83.
- The proposal says no direct SQL UPDATE and creates one new version per affected spec at bridge/gtkb-spec-pipeline-f4-003.md:14-15.
- Current `update_spec()` creates a new versioned row and carries fields forward at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:656-760.

**Risk/impact:** Low if Phase B waits for F1 implementation. The audit trail is preserved.

**Required action:** Keep `dry_run=True` as the default and route all linkage changes through `update_spec()` or an equivalent append-only helper.

### 2. Inherited assertion output is now reviewable

**Evidence:**
- Current `validate_dcl_constraints()` returns DCL-level results at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1219-1268.
- F4 v2 defines `InheritedAssertionResult` with DCL source, affected spec, assertion, status, and detail at bridge/gtkb-spec-pipeline-f4-003.md:86-103.
- Tests now include inherited assertion result coverage at bridge/gtkb-spec-pipeline-f4-003.md:114-121.

**Risk/impact:** Moderate implementation complexity, but the result contract is now specific enough to test.

**Required action:** Add tests for DCL-only results, affected-spec results, and skipped non-machine assertions before shipping Phase B.

## Verification

- `python -m pytest tests/test_db.py -q --tb=short` passed: `25 passed, 1 warning`.
- `python -m ruff check src/ tests/` passed: `All checks passed!`.

## Conditions For Implementation

1. Implement Phase A independently first: `check_constraints_for_spec()` and `get_constraint_coverage()`.
2. Do not implement Phase B writes until F1 `affected_by` is present and tested.
3. Preserve audit evidence in `change_reason` for both link additions and removals.
4. Keep propagation reports explicit about `affected_specs`, `already_linked`, `removed`, and `dry_run`.
