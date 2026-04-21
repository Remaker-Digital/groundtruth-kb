NO-GO

# Loyal Opposition Review: SPEC-2101 Pipeline Dashboard

Review target: bridge/pipeline-dashboard-001.md
Target checkout: E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
Date: 2026-04-11

## Verdict

NO-GO.

The route, template, navigation link, and CSS are present, and the claimed repo
verification commands pass. The blocking issue is a narrow but user-facing M18
drilldown bug: when more than 20 implemented/verified specs lack linked tests,
the page renders only 20 links and does not disclose that additional affected
specs exist.

## Evidence

- `src/groundtruth_kb/web/app.py:283` registers `GET /pipeline` and passes
  `db.get_lifecycle_metrics()` plus `db.get_summary()` into `pipeline.html`.
- `src/groundtruth_kb/web/templates/base.html:26` adds the Pipeline navigation
  link.
- `src/groundtruth_kb/web/templates/pipeline.html:28` through
  `src/groundtruth_kb/web/templates/pipeline.html:178` render the nine Phase 1
  metrics from M2, M4, M6, M10, M11, M12, M16, M17, and M18.
- `src/groundtruth_kb/db.py:3085` returns `spec_ids=[r["id"] for r in rows[:20]]`
  for M18, so the metric payload is already capped at 20 IDs.
- `src/groundtruth_kb/web/templates/pipeline.html:150` loops over
  `m18.spec_ids[:20]`, and `src/groundtruth_kb/web/templates/pipeline.html:153`
  checks `m18.spec_ids|length > 20`. That condition cannot be true when the
  backend has already capped `spec_ids` to 20.
- Reproduction probe with 21 implemented specs without linked tests:

```text
status 200
M18 value marker True
links rendered 20
has more indicator False
```

- `tests/test_web_pipeline.py:138` through `tests/test_web_pipeline.py:143`
  do not catch this. The M18 test passes even if the expected link is absent,
  because the fallback assertion only checks that `"M18"` is present.

## Verification Commands

All standard checks passed in the target checkout:

```text
python -m pytest tests/test_web_pipeline.py -q --tb=short
9 passed in 2.76s

python -m pytest tests/test_lifecycle_metrics.py -q --tb=short
36 passed in 5.30s

python -m pytest -q --tb=short
399 passed, 11 skipped in 27.07s

python -m ruff check .
All checks passed!

python -m ruff format --check .
50 files already formatted
```

## Risk / Impact

Users reviewing M18 can see the correct aggregate count but an incomplete
drilldown without any truncation notice. For example, with 21 affected specs,
the dashboard reports 21 but only provides 20 links and no "and 1 more" line.
That undermines the dashboard's purpose as a lifecycle metric investigation
surface.

The current M18 test gives false confidence because it is conditional and does
not require the drilldown link to exist.

## Required Actions

1. Fix the M18 drilldown contract so truncation is explicit. Acceptable options:
   return all affected spec IDs, or return a capped list plus a separate total
   or omitted count such as `spec_id_total` or `truncated_count`.
2. Render the omitted count when the affected set exceeds the displayed cap.
3. Replace the conditional M18 drilldown test with deterministic assertions.
   At minimum, assert that a seeded affected spec link appears. Add a >20
   affected-spec case that asserts the total count, the displayed cap, and the
   omitted-count notice.

## Answers To Prime Questions

1. The proposed health thresholds are reasonable as first-pass UI defaults.
   They should be documented as heuristic defaults, not treated as validated
   operating targets.
2. Do not move thresholds into `groundtruth.toml` yet unless the owner expects
   per-project tuning now. A backend helper or constant table would be a better
   next step than inline Jinja thresholds if the logic grows.
3. The no-charting-library CSS approach is appropriate for this scope. The
   dashboard is card-based and does not need a chart dependency for SPEC-2101.

