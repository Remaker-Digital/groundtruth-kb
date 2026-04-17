# NO-GO: F4 Cross-Cutting Constraint Propagation Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f4-001.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

Constraint propagation is the right problem to solve, but the current proposal conflicts with GT-KB's append-only artifact model and depends on F1/F2 work that is not approved.

## Findings

### 1. Blocking: Dependencies are unresolved

**Evidence:** F4 declares dependencies on F1 and F2 at bridge/gtkb-spec-pipeline-f4-001.md:7. It relies on F1 `constraints` and `affected_by` at bridge/gtkb-spec-pipeline-f4-001.md:29 and bridge/gtkb-spec-pipeline-f4-001.md:50. F1 remains NO-GO in bridge/gtkb-spec-pipeline-f1-004.md, and F2 is NO-GO in bridge/gtkb-spec-pipeline-f2-002.md.

**Risk/impact:** Implementing F4 now would bind propagation to unstable metadata and impact-analysis behavior.

**Required action:** Wait for F1 and F2 GO, or propose an F4 phase that only reports applicable constraints without writing linkage.

### 2. Blocking: Propagation write model conflicts with append-only versioning

**Evidence:** F4 says propagation updates `affected_by` fields at bridge/gtkb-spec-pipeline-f4-001.md:50 and says performance mitigation is "Batch UPDATE with single query" at bridge/gtkb-spec-pipeline-f4-001.md:139. Current GT-KB states core artifacts use append-only versioning and every mutation creates a new versioned record at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4. Current `update_spec()` inserts a new specification version rather than updating the current row at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:721.

**Risk/impact:** A batch UPDATE would silently rewrite historical spec rows and violate the core audit trail.

**Required action:** Propagation must create new spec versions via `update_spec()` or an equivalent append-only batch-version helper with `changed_by`, `change_reason`, and dry-run parity. No direct UPDATE against current spec rows.

### 3. Major: Link removal semantics are not audit-safe

**Evidence:** F4 says specs are removed from linkage when scope narrows at bridge/gtkb-spec-pipeline-f4-001.md:51 and retirement triggers unlinking at bridge/gtkb-spec-pipeline-f4-001.md:140.

**Risk/impact:** Removing linkage can erase why an old implementation decision was made unless the previous version remains queryable and the change reason is explicit.

**Required action:** Specify link removal as a new versioned spec mutation and include prior-link evidence in the propagation report.

### 4. Major: Assertion inheritance output contract is underspecified

**Evidence:** F4 says DCL assertion failures should be reported against functional specs at bridge/gtkb-spec-pipeline-f4-001.md:63. Current `validate_dcl_constraints()` returns DCL-level results only at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1219.

**Risk/impact:** Callers will not know whether a violation belongs to a DCL, a functional spec, or both.

**Required action:** Define the result schema for per-functional-spec inherited assertion failures and add tests for DCL-only, affected-spec, and skipped cases.

## Conditions For GO

1. Resolve F1/F2 dependencies.
2. Replace batch UPDATE with append-only version creation.
3. Specify audit-safe link removal.
4. Define inherited assertion result shape and tests.

