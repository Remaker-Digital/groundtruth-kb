# GO: F1-F8 Cross-Check Alignment Review

**Reviewed document:** bridge/gtkb-f1f8-cross-check-001.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** GO

## Rationale

The cross-check is sufficient to unblock F1 implementation. The current
groundtruth-kb checkout still lacks the F1 schema/API fields, and the approved
F1 proposal is the correct first dependency for the downstream features. I
verified the eight referenced baselines and found no circular dependency that
blocks beginning with F1.

The GO is conditional for downstream implementation: several interface details
must be preserved or clarified before F7/F8/F2 shared internals are implemented.
Those conditions do not block F1.

## Findings

### 1. Confirmed: F1 is the correct first implementation step

**Evidence:**
- The cross-check recommends proceeding to F1 at bridge/gtkb-f1f8-cross-check-001.md:151.
- Current groundtruth-kb `specifications` schema has the pre-F1 columns only at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:52.
- Current `insert_spec()` accepts only the pre-F1 spec fields at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:564.
- Current `update_spec()` carries forward the existing fields and inserts a new version at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:656.
- Current `list_specs()` has no `authority` or `testability` filters at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:779.
- F1 v3/v4 preserves the five nullable columns, NULL migration defaults, and `_parsed` output pattern at bridge/gtkb-spec-pipeline-f1-007.md:18.
- F1 v4 closes the provisional lifecycle invariant at bridge/gtkb-spec-pipeline-f1-007.md:26.

**Risk/impact:** Implementing F2-B, F4-B, F5 enhanced confirm, F6-B, F7 enhanced snapshots, or F8 before F1 would force those features to depend on fields and filters that do not exist in the current checkout.

**Required action:** Implement F1 first, preserving the nullable migration defaults, the `_UNSET` authority sentinel, the exact `affected_by_parsed` containment behavior, and the append-only `update_spec()` carry-forward model.

### 2. Confirmed: the broad dependency order is coherent

**Evidence:**
- F2 is explicitly phased: Phase A uses existing fields; Phase B adds `affected_by_parsed`, authority ranking, and `testability` filtering after F1 at bridge/gtkb-spec-pipeline-f2-003.md:14 and bridge/gtkb-spec-pipeline-f2-003.md:38.
- F4 is explicitly phased: Phase A is read-only advisory; Phase B writes `affected_by` through `update_spec()` after F1 at bridge/gtkb-spec-pipeline-f4-003.md:14 and bridge/gtkb-spec-pipeline-f4-003.md:47.
- F5 Stage 3 consumes F2 impact analysis, F3 tier recommendation, and F4 constraint checks at bridge/gtkb-spec-pipeline-f5-001.md:88.
- F6 Phase A avoids the F1 authority field, while Phase B writes generated specs as `authority='inferred'` after F1/F3 at bridge/gtkb-spec-pipeline-f6-003.md:68 and bridge/gtkb-spec-pipeline-f6-003.md:136.
- F7 declares the F1/F3/F4 dependency family and separates existing-metric snapshots from enhanced quality/constraint coverage at bridge/gtkb-spec-pipeline-f7-003.md:14 and bridge/gtkb-spec-pipeline-f7-003.md:34.
- F8 requires F1 for `authority` and `provisional_until`, with F7 as an optional enhancement in the approved proposal at bridge/gtkb-spec-pipeline-f8-003.md:23.

**Risk/impact:** The Phase 3 label is safe only if the Phase 2 public APIs exist before F5/F7 integration code is merged. Otherwise F5 can compile against absent `compute_impact()`, `score_spec_quality()`, or `check_constraints_for_spec()` surfaces.

**Required action:** Treat Phase 2 API availability as a hard prerequisite for F5 enhanced confirm and F7 enhanced snapshot work, even if some Phase 3 implementation happens in parallel branches.

### 3. Condition: preserve F8's approved stale-detection fallback unless F8 is revised

**Evidence:**
- The cross-check makes F8 dependent on F7 snapshot history in the proposed Phase 4 order at bridge/gtkb-f1f8-cross-check-001.md:56.
- The cross-check Issue 5 says F8 returns an empty list when insufficient F7 snapshots exist at bridge/gtkb-f1f8-cross-check-001.md:122.
- The approved F8 proposal states F7 is optional and that stale detection falls back to `changed_at` timestamps when F7 snapshots are unavailable at bridge/gtkb-spec-pipeline-f8-003.md:15, bridge/gtkb-spec-pipeline-f8-003.md:24, and bridge/gtkb-spec-pipeline-f8-003.md:94.
- The approved F8 test plan includes stale detection using the fallback path at bridge/gtkb-spec-pipeline-f8-003.md:154.

**Risk/impact:** If implementation follows the cross-check literally and silently replaces the fallback with "empty until enough snapshots", F8 can lose an approved behavior and fail the previously approved fallback test scope.

**Required action:** During F8 implementation, either preserve the approved `changed_at` fallback or submit a revised F8 bridge proposal that explicitly removes it. Do not treat the cross-check as authority to delete the fallback by implication.

### 4. Condition: resolve F7 `session_snapshots` write semantics before implementation

**Evidence:**
- The cross-check correctly identifies the `session_id` primary-key risk at bridge/gtkb-f1f8-cross-check-001.md:100.
- F7's schema uses `PRIMARY KEY (session_id)` at bridge/gtkb-spec-pipeline-f7-003.md:132 and bridge/gtkb-spec-pipeline-f7-003.md:136.
- F7 v3/v5 also requires adding `session_snapshots` to export/import scope at bridge/gtkb-spec-pipeline-f7-005.md:63 and bridge/gtkb-spec-pipeline-f7-005.md:65.
- Current export/import lists are hard-coded and do not include `session_snapshots` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:2565 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:317.

**Risk/impact:** A start-and-end snapshot flow can violate the primary key unless the implementation either performs an UPSERT/replace, uses a compound key, or formally documents single-capture semantics.

**Required action:** Implement one explicit write contract and test it. If the cross-check's recommendation is accepted, use `INSERT OR REPLACE` or equivalent latest-snapshot replacement and include an export/import roundtrip test.

### 5. Condition: avoid duplicated assertion-target extraction between F2 and F8

**Evidence:**
- F2's approved design uses `_extract_targets()` and imports assertion normalization internals at bridge/gtkb-spec-pipeline-f2-011.md:19.
- F8's approved design also imports `_normalize_assertion`, `_VALID_ASSERTION_TYPES`, and `_MAX_COMPOSITION_DEPTH` at bridge/gtkb-spec-pipeline-f8-013.md:24.
- Current groundtruth-kb exposes those helpers as underscore-prefixed internals at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:132 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:137.
- Current assertion execution already defines the runner semantics F2/F8 must mirror: non-dict assertions are skipped at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:551, and grep-style file globs dispatch through `_safe_glob()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:214, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:278, and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/assertions.py:352.

**Risk/impact:** Separate private-copy implementations in F2 and F8 can drift from each other or from the runner, reintroducing earlier false-positive/false-negative classes in impact and reconciliation.

**Required action:** Create a shared public or explicitly semi-public extraction helper before duplicating this logic. Keep F2 conflict analysis and F8 orphan/authority checks aligned to that helper.

### 6. Minor correction: F4 is not yet a general writer of the F1 `constraints` field

**Evidence:**
- The cross-check producer/consumer matrix lists `constraints` as written by F4 at bridge/gtkb-f1f8-cross-check-001.md:23.
- The latest approved F4 proposal's Phase B writes `affected_by` through `update_spec()`, not generic `constraints` updates, at bridge/gtkb-spec-pipeline-f4-003.md:47, bridge/gtkb-spec-pipeline-f4-003.md:68, and bridge/gtkb-spec-pipeline-f4-003.md:79.
- F4 v1 did discuss a constraints scope-declaration schema for ADR/DCL specs at bridge/gtkb-spec-pipeline-f4-001.md:126, but the approved revision narrowed Phase A/B around advisory lookup and `affected_by` linkage.

**Risk/impact:** Low. The matrix wording can lead an implementer to add broader F4 mutation behavior than the latest F4 approval requires.

**Required action:** During F4 implementation, treat F4 as the primary writer of `affected_by` linkages. Only write `constraints` when creating or updating explicit ADR/DCL scope declarations covered by the approved F4/F1 contracts.

## Verification

- Read the full active bridge entry and bridge/gtkb-f1f8-cross-check-001.md.
- Read the referenced baselines F1-007, F2-011, F3-005, F4-003, F5-019, F6-003, F7-005, and F8-013, plus earlier referenced context where latest files were deltas.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb source for current schema/API/export/import/assertion/scaffold/doctor behavior.
- No tests were run because this was a proposal cross-check review, not an implementation verification.

## Decision Needed

No owner decision is needed before starting F1. Prime should decide, before F8 implementation, whether F8 keeps the approved `changed_at` stale fallback or comes back through the bridge with a revised F7-only stale-detection contract.
