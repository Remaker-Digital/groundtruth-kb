# NO-GO: F2 Change Impact Analysis Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f2-001.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The impact-analysis concept is useful, but the proposal is not ready to implement. It depends on F1 fields that are still not approved, assumes bridge-protocol behavior that does not exist, and hard-codes Agent Red scale/section assumptions into a reusable GT-KB feature.

## Findings

### 1. Blocking: Dependency on unresolved F1 fields

**Evidence:** F2 declares an F1 dependency at bridge/gtkb-spec-pipeline-f2-001.md:7, uses `affected_by` for dependents at bridge/gtkb-spec-pipeline-f2-001.md:69, and lists dependent lookup as depending on F1 at bridge/gtkb-spec-pipeline-f2-001.md:143. F1 remains NO-GO in bridge/gtkb-spec-pipeline-f1-004.md.

**Risk/impact:** Implementing F2 before F1's metadata contract is stable will lock impact analysis to a moving schema and likely require rework.

**Required action:** Rebase F2 on the accepted F1 schema after F1 receives GO, or split out a smaller F2 phase that only uses existing `section`, `scope`, `tags`, and `type`.

### 2. Major: Bridge integration claim is not in the file bridge protocol

**Evidence:** F2 says "The bridge protocol requires impact reports in proposals" at bridge/gtkb-spec-pipeline-f2-001.md:155. The active protocol only defines scanning, reading, saving the next version, and inserting GO/NO-GO/VERIFIED lines at .claude/rules/file-bridge-protocol.md:71.

**Risk/impact:** The proposal makes impact reports advisory in code but mandatory in coordination without updating the coordination contract. Prime and Codex will disagree about what is required for future proposals.

**Required action:** Either remove that claim or propose a separate protocol/template update that makes impact reports a documented bridge requirement.

### 3. Major: Thresholds and tests are Agent Red-specific, not GT-KB-general

**Evidence:** Blast-radius thresholds are fixed at 5 and 20 related specs at bridge/gtkb-spec-pipeline-f2-001.md:73. The test plan expects `ADMIN_UI (356 existing specs)` at bridge/gtkb-spec-pipeline-f2-001.md:132.

**Risk/impact:** A reusable package feature will behave differently across small and large projects. Tests tied to Agent Red corpus size cannot live in GT-KB's generic test suite without fixture pollution.

**Required action:** Make thresholds configurable per project and rewrite tests around synthetic fixtures, not Agent Red corpus counts.

### 4. Major: Conflict detection is underspecified against the current assertion model

**Evidence:** F2 proposes comparing assertion targets and "different behaviors for the same file/pattern" at bridge/gtkb-spec-pipeline-f2-001.md:71. Current executable assertion types are the fixed set in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:39, and non-machine types are skipped at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:560.

**Risk/impact:** Without a formal conflict algorithm, the feature can produce noisy or misleading "conflicts" and train reviewers to ignore impact reports.

**Required action:** Define exact conflict heuristics per assertion type, include false-positive expectations, and add tests for non-machine assertion handling.

## Conditions For GO

1. Resolve or decouple the F1 dependency.
2. Remove or separately approve bridge-protocol changes.
3. Replace Agent Red-specific thresholds/tests with configurable thresholds and isolated fixtures.
4. Specify conflict detection behavior against the actual assertion schema.

