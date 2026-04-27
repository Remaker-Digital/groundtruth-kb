NO-GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 6 Post-Implementation

Status: NO-GO

## Claim

Slice 6 is not verified. The implementation satisfies the narrow fixture tests and the focused gates pass, but a live run against the local KnowledgeDB shows the lane does not yet produce a meaningful release-readiness split: it inventories nearly the entire KB and routes almost all KB records to `unclassified`.

## Evidence

- Focused verification commands passed:
  - `python -m ruff check scripts/rehearse/_split_helper.py scripts/rehearse/_release_readiness_split.py tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_release_readiness_split.py` -> `All checks passed!`
  - `python -m ruff format --check scripts/rehearse/_split_helper.py scripts/rehearse/_release_readiness_split.py tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_release_readiness_split.py` -> `4 files already formatted`
  - `PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_release_readiness_split.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_common_validation.py -q --tb=short` -> `166 passed in 2.56s`
- The implementation reads all specs, all work items, and all deliberations without the source filters described in the original Slice 6 source contract: `scripts/rehearse/_release_readiness_split.py:284-300`.
- The original proposal scoped those sources more narrowly: specs filtered by type / release-readiness relevance, work items open plus recently closed, and deliberations filtered to owner decisions or release-readiness mentions (`bridge/gtkb-isolation-016-phase8-wave2-slice6-001.md:61-72`).
- A live run of `_release_readiness_split.run()` against the local KB returned `framework_artifact_count: 1`, `adopter_artifact_count: 10`, `unclassified_artifact_count: 5139`, `total_artifacts: 5150`, with no warnings.
- The live KB ID prefixes explain the result: specs are mostly `SPEC-*`, plus `GOV-*`, `PB-*`, `ADR-*`, `DCL-*`; work items are `WI-*`; deliberations are `DELIB-*`. The new helper only positively classifies `GTKB-*` and `AR-*`, so real formal artifacts collapse to `unknown_prefix` / `unclassified`.
- The content blob helpers also miss common real KB fields: specs use fields such as `title`, `description`, and `rationale`, but `_spec_content_blob()` only checks `summary` and `content`; work items and deliberations are similarly narrow (`scripts/rehearse/_release_readiness_split.py:173-181`).
- The tests use synthetic IDs such as `GTKB-MIXED-001`, `GTKB-FRAMEWORK-001`, and `AR-WI-001`, so they do not cover the real KnowledgeDB ID shapes (`tests/scripts/test_rehearse_release_readiness_split.py:327-407`).

## Blocking Findings

### F1 - The lane over-inventories KB records instead of release-readiness-bearing records

`_release_readiness_split.py` currently calls `list_specs()`, `list_work_items()`, and `list_deliberations()` and partitions every returned row. That turns the lane into a whole-KB dump rather than a release-readiness split. The live output proves the blast radius: 5,150 artifacts emitted, 5,139 unclassified.

The fix should apply source filters before classification:

1. Specs: include the governed artifact types and release-readiness-relevant records named by the proposal, but do not blindly include all `SPEC-*` rows unless that is an explicit design choice with a usable classifier.
2. Work items: include open and recently closed items per the proposal, not every historical `WI-*` row.
3. Deliberations: keep `list_deliberations()` uncapped, but filter to `outcome == owner_decision` and/or release-readiness matching before partitioning.

### F2 - The classifier/test fixtures do not match real KnowledgeDB ID shapes

The new helper is fine for `GTKB-*` / `AR-*` records, but the live KB uses `SPEC-*`, `GOV-*`, `PB-*`, `ADR-*`, `DCL-*`, `WI-*`, and `DELIB-*` for the sources this lane consumes. Because the implementation treats those as `unknown_prefix`, the split loses ownership signal for nearly all real records.

The fix should either:

1. add release-readiness-lane classifiers for the actual formal artifact ID families, with conflict-preserving handling where subject is ambiguous; or
2. narrow the source filters so only records that carry a reliable subject signal enter the split.

Add regression tests using real-shaped IDs such as `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, `PB-*`, `ADR-*`, `WI-*`, and `DELIB-*`, not only synthetic `GTKB-*` / `AR-*` IDs.

## Non-Blocking Notes

- The release-gate surface classification is correct: adopter bucket with `mechanism_origin`.
- The DOC classifier is correctly separate from the prefix helper and covers `DOC-release-readiness-recovery`.
- The `list_deliberations()` rather than `search_deliberations()` guard is correct and should be preserved.
- `_backlog_split.py` was not refactored, satisfying the Slice 6 GO condition.

## Recommended Action

Revise the lane to filter KB sources before partitioning and classify real KnowledgeDB artifact IDs. Then rerun the focused gates plus a live smoke that reports a plausible release-readiness inventory, not a mostly unclassified whole-KB export.

## Decision Needed From Owner

None.
