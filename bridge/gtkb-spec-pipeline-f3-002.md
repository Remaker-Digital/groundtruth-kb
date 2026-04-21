# NO-GO: F3 Spec Quality Gate Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f3-001.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

Spec quality scoring is valuable, but this proposal currently incentivizes assertion types that GT-KB treats as non-executable, depends on unresolved F1 fields, and does not settle whether scores are stored even though later dashboard/provenance features rely on trends.

## Findings

### 1. Blocking: Dependency on unresolved F1 fields

**Evidence:** F3 declares an F1 dependency at bridge/gtkb-spec-pipeline-f3-001.md:7. Its completeness and isolation dimensions score `authority`, `constraints`, and `affected_by` at bridge/gtkb-spec-pipeline-f3-001.md:54 and bridge/gtkb-spec-pipeline-f3-001.md:64. F1 remains NO-GO in bridge/gtkb-spec-pipeline-f1-004.md.

**Risk/impact:** The scoring formula will churn if the F1 field names, defaults, or parsed output contract change.

**Required action:** Rebase F3 after F1 is approved, or explicitly allow scoring to degrade gracefully when F1 fields are absent.

### 2. Blocking: "Non-grep" scoring rewards non-executable assertion names

**Evidence:** F3 awards score for a "non-grep assertion (behavioral, functional, test_run)" at bridge/gtkb-spec-pipeline-f3-001.md:50. Current executable assertion types are `grep`, `glob`, `grep_absent`, `file_exists`, `count`, `json_path`, `all_of`, and `any_of` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:39. Non-machine assertion types are skipped at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:560.

**Risk/impact:** The score can reward assertions that never execute. That directly undermines F3's goal of preventing weak green tests.

**Required action:** Score against the current executable assertion taxonomy, or propose and test new executable assertion types before using them in the quality formula.

### 3. Major: Historical trends require a storage decision

**Evidence:** F3 says the score history would provide a trendline at bridge/gtkb-spec-pipeline-f3-001.md:100, and F7 consumes quality distribution at bridge/gtkb-spec-pipeline-f3-001.md:130. Current GT-KB has a `quality_scores` table keyed by `session_id` for aggregate session metrics at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:273, not per-spec quality results.

**Risk/impact:** If scores are computed only on demand, F7 cannot show historical trends. If stored, the proposal needs schema, retention, recomputation, and versioning semantics.

**Required action:** Decide whether `QualityScore` is persisted. If yes, define a table keyed by spec id/version or session/spec/version and update export/import. If no, remove trend claims and F7 dependency.

### 4. Major: Configurability is promised but not specified

**Evidence:** The proposal's mitigation says weights are configurable, but the API at bridge/gtkb-spec-pipeline-f3-001.md:102 only adds scoring methods and no weight/config API.

**Risk/impact:** Hard-coded subjective weights become product policy without an owner/project override path.

**Required action:** Either make the weights fixed and document that as a product decision, or define configuration storage and tests for per-project weighting.

## Conditions For GO

1. Resolve or explicitly degrade around the F1 dependency.
2. Align testability scoring with executable assertion types.
3. Decide and specify score persistence.
4. Define fixed-vs-configurable scoring weights.

