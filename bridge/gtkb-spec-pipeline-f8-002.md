# NO-GO: F8 Provenance Reconciliation Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f8-001.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The reconciliation engine addresses a real corpus-maintenance gap, but the proposal depends on unresolved schema/dashboard work and has API contracts that do not provide the context needed by existing assertion infrastructure.

## Findings

### 1. Blocking: Schema dependency is inconsistent and unresolved

**Evidence:** F8 says it depends on `authority_tier` and `provisional_until` at bridge/gtkb-spec-pipeline-f8-001.md:7. The F1 proposal uses `authority`, not `authority_tier`, and F1 remains NO-GO in bridge/gtkb-spec-pipeline-f1-004.md.

**Risk/impact:** Implementers can create the wrong column or write reconciliation code against a field name that does not exist.

**Required action:** Align F8 terminology with the approved F1 schema after F1 receives GO.

### 2. Blocking: Staleness check depends on F7 but F7 is not declared as a dependency

**Evidence:** F8 proposes stale-spec checks by "N sessions" at bridge/gtkb-spec-pipeline-f8-001.md:47, and implementation step 4 says stale detection uses session snapshot history from F7 at bridge/gtkb-spec-pipeline-f8-001.md:150. F7 is currently NO-GO and is not listed in F8 dependencies.

**Risk/impact:** The staleness API cannot be implemented as proposed without a session history source.

**Required action:** Add F7 as a dependency or redefine stale detection using existing `changed_at`/`pipeline_events` data.

### 3. Major: Orphan detection API lacks `project_root`

**Evidence:** F8 adds `get_orphaned_specs(self) -> list[dict]` at bridge/gtkb-spec-pipeline-f8-001.md:113. Current assertion execution requires a project root in `run_all_assertions(db, project_root, ...)` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:646.

**Risk/impact:** Orphan detection will depend on current working directory or hidden configuration, producing false positives for valid relative assertion paths.

**Required action:** Add `project_root` or explicit config resolution to orphan detection APIs and tests.

### 4. Major: Authority conflict detection is underspecified

**Evidence:** F8 proposes finding inferred specs that "conflict" with stated specs at bridge/gtkb-spec-pipeline-f8-001.md:32. No conflict algorithm is specified; F2 separately proposes heuristic conflict detection and is currently NO-GO.

**Risk/impact:** Authority conflict findings can become arbitrary semantic judgments rather than reproducible review evidence.

**Required action:** Define conflict detection mechanics or explicitly depend on an approved F2 conflict engine.

## Conditions For GO

1. Align field names with approved F1.
2. Add/resolve the F7 dependency or use existing event timestamps instead.
3. Add project-root handling for orphan detection.
4. Define reproducible conflict detection or depend on F2.

