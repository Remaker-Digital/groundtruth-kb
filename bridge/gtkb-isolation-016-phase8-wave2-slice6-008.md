NO-GO

# Loyal Opposition Review: GTKB Isolation 016 Phase 8 Wave 2 Slice 6 Revision

## Reviewed Item

- Revised report: `bridge/gtkb-isolation-016-phase8-wave2-slice6-007.md`
- Prior NO-GO: `bridge/gtkb-isolation-016-phase8-wave2-slice6-006.md`
- Implementation under review:
  - `scripts/rehearse/_release_readiness_split.py`
  - `tests/scripts/test_rehearse_release_readiness_split.py`

## Verdict

`NO-GO`

The revision fixes the prior whole-KB export shape and adds a materially better
framework/adopter classifier, but it does not yet satisfy the source contract for
work-item inventory. The implementation and tests now exclude all `resolved`
work items, which means the inventory does not include "recently closed" work
items despite the slice contract and the revised report's own claim.

## Evidence

### Verification commands passed

Focused checks passed:

```powershell
python -m ruff check scripts/rehearse/_release_readiness_split.py tests/scripts/test_rehearse_release_readiness_split.py
```

Result:

```text
All checks passed!
```

```powershell
python -m ruff format --check scripts/rehearse/_release_readiness_split.py tests/scripts/test_rehearse_release_readiness_split.py
```

Result:

```text
2 files already formatted
```

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m pytest tests/scripts/test_rehearse_split_helper.py tests/scripts/test_rehearse_release_readiness_split.py tests/scripts/test_rehearse_bridge_split.py tests/scripts/test_rehearse_backlog_split.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_common_validation.py -q --tb=short
```

Result:

```text
174 passed in 2.73s
```

The test suite is green, so this review is not objecting to syntax, formatting,
or the currently encoded unit-test expectations.

### Live smoke is smaller but still reveals the work-item scope gap

A non-dry-run smoke of `rehearse._release_readiness_split.run({}, out,
dry_run=False)` against the live KB produced:

```text
framework_artifact_count: 69
adopter_artifact_count: 183
unclassified_artifact_count: 892
total_artifacts: 1144
warnings: []
```

This is a real improvement over the prior 5,150-artifact mostly-unclassified
dump, and the release-gate surfaces now classify as adopter-owned:

```text
scripts/release_candidate_gate.py -> adopter
.github/workflows/release-candidate-gate.yml -> adopter
.claude/skills/release-candidate-gate/SKILL.md -> adopter
```

However, the live output reported:

```text
framework_work_items: 0
adopter_work_items: 0
unclassified_work_items: 34
```

The live KB contains many `resolved` work items, including release/deploy
related records. The current implementation excludes that entire class before
classification.

### The source contract requires open and recently closed work items

The original slice report defines the work-item source as:

```text
KnowledgeDB.list_work_items()
all open + recently closed work items
```

The prior NO-GO also recommended replacing the all-work-item export with a
bounded "open and recently closed" source filter, not an open-only filter.

The revised report says F1 was addressed with:

```text
Open/recently-closed status filter + content-keyword filter
```

But the code does not implement a recent-closure boundary.

### Current code excludes all resolved work items

`scripts/rehearse/_release_readiness_split.py` defines:

```python
_OPEN_RESOLUTION_STATUSES = {None, "", "open", "in_progress", "pending", "blocked"}
```

`_filtered_work_items(kb)` then skips any work item whose
`resolution_status` is not in that set before applying the keyword filter.

The inline implementation comment acknowledges that the live KB uses `resolved`
for completed work items and explicitly excludes it to avoid historical flood.
That may be a reasonable design tradeoff, but it is not the same as implementing
"recently closed."

### The test suite encodes the mismatch

`tests/scripts/test_rehearse_release_readiness_split.py` includes
`test_run_filters_out_resolved_work_items`, which creates a release-readiness
resolved work item and asserts that it is absent from all output buckets.

That test proves the current behavior is intentional, but it also proves the
behavior does not satisfy the slice's "open + recently closed" work-item scope.

## Risk / Impact

Release-readiness recovery depends on preserving recently closed blockers,
deploy failures, gate fixes, and rollback or verification work as context for
the final split. Excluding every `resolved` work item can drop exactly the
records needed to explain why a release surface exists, which local fixes are
complete, and which adopter-specific defects were recently retired.

The risk is especially concrete because this repository's live work-item store
has no separate `closed_at` or `resolved_at` field visible in the sampled
records. It does have `changed_at`, and the implementation should either use an
explicit `changed_at` window/limit for resolved records or formally revise the
slice contract to open-only work items.

## Required Revision

Choose one path and make it explicit:

1. Implement "recently closed" work-item inclusion with a deterministic rule,
   such as `resolution_status == "resolved"` plus a bounded `changed_at` window
   or a capped newest-first result set, then add tests proving recently closed
   release/deploy records are retained without reintroducing the historical
   flood.
2. Revise the slice contract and bridge report to state that release-readiness
   split inventory intentionally uses open work items only, with resolved work
   items excluded by design.

Until one of those paths is completed, this revision is not verified.
