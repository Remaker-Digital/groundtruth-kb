VERIFIED

# Loyal Opposition Verification: GTKB Isolation 016 Phase 8 Wave 2 Slice 6 Revision 2

## Reviewed Item

- Revised report: `bridge/gtkb-isolation-016-phase8-wave2-slice6-009.md`
- Prior NO-GO: `bridge/gtkb-isolation-016-phase8-wave2-slice6-008.md`
- Implementation under review:
  - `scripts/rehearse/_release_readiness_split.py`
  - `tests/scripts/test_rehearse_release_readiness_split.py`

## Verdict

`VERIFIED`

The REVISED-2 implementation addresses the blocking finding from `-008`.
Release-readiness work-item inventory now includes open records plus a
deterministic, bounded set of recently resolved records, using the live KB's
available `changed_at` timestamp as the recency signal.

## Evidence

### Code implements the missing recent-closure rule

`scripts/rehearse/_release_readiness_split.py` now defines:

- `_RECENT_CLOSURE_WINDOW_DAYS = 90`
- `_is_recently_changed(...)` for ISO-8601 `changed_at` parsing
- `_filtered_work_items(...)` inclusion of:
  - open statuses in `_OPEN_RESOLUTION_STATUSES`
  - `resolution_status == "resolved"` when `changed_at` falls inside the
    90-day window

This satisfies the prior review requirement to implement "recently closed" with
a deterministic boundary rather than excluding every resolved work item.

### Tests encode the corrected contract

`tests/scripts/test_rehearse_release_readiness_split.py` now includes tests that:

- include a recent resolved release-readiness work item
- exclude an old resolved release-readiness work item
- exclude resolved records with missing or malformed `changed_at`
- verify both `Z` and `+00:00` ISO timestamp parsing

The prior contradictory test that asserted all resolved work items should be
excluded is no longer present.

### Verification commands

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
177 passed in 2.99s
```

### Live KB probe

A fresh non-dry-run probe of `rehearse._release_readiness_split.run({}, out,
dry_run=False)` against the live KB produced:

```text
summary.framework_artifact_count: 71
summary.adopter_artifact_count: 187
summary.unclassified_artifact_count: 1269
summary.total_artifacts: 1527
warnings: []
```

Work-item buckets changed from the prior open-only result to:

```text
framework_work_items: 2
adopter_work_items: 4
unclassified_work_items: 411
```

The output now includes recent resolved records, including:

```text
framework_work_items WI-3164 resolved 2026-04-11T15:29:01+00:00
adopter_work_items WI-0312 resolved 2026-02-28T02:23:32+00:00
adopter_work_items WI-0918 resolved 2026-03-02T08:59:34+00:00
```

Release-gate surfaces remain classified as adopter-local application surfaces:

```text
scripts/release_candidate_gate.py -> application_release_gate_surface, agent_red_local, exists=True
.github/workflows/release-candidate-gate.yml -> application_release_gate_surface, agent_red_local, exists=True
.claude/skills/release-candidate-gate/SKILL.md -> application_release_gate_surface, agent_red_local, exists=True
```

## Residual Notes

The live probe still produces a large unclassified inventory, including 411
unclassified work items and 1,269 unclassified artifacts overall. That is not a
blocking issue for this revision because the previous blocker was the absence of
any recently closed work-item inclusion, and the implementation now bounds that
scope with an explicit 90-day rule. Wave 3 or a follow-up slice should decide
whether additional content signals, source-spec joins, or narrower release-key
filters are needed to reduce the unclassified bucket further.

The `_is_recently_changed()` helper treats future timestamps as within the
window because `current - dt` is negative. No future-dated live records were
observed in the probe, so this is not blocking, but a defensive follow-up could
require `dt <= current`.

## Decision Needed From Owner

None.
