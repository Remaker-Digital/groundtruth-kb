GO

# Loyal Opposition Review: SPEC-2101 Pipeline Dashboard Revision

Review target: bridge/pipeline-dashboard-003.md
Prior bridge context read: bridge/pipeline-dashboard-001.md, bridge/pipeline-dashboard-002.md
Target checkout: E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
Date: 2026-04-11

## Verdict

GO.

The revised implementation addresses the prior blocking M18 drilldown defect.
The backend now returns the complete affected spec ID list, the template caps
display at 20 while computing the omitted-count notice from the full list, and
deterministic tests cover both the affected-spec link and the >20 truncation
case.

## Evidence

- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\web\app.py:283` registers `GET /pipeline`, and `app.py:285` through `app.py:290` passes lifecycle metrics and summary data to `pipeline.html`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\web\templates\base.html:26` adds the Pipeline navigation link.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\web\static\style.css:328` begins the dashboard CSS, with the responsive metric grid at `style.css:338` through `style.css:342` and metric cards at `style.css:345` through `style.css:350`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3072` defines `compute_m18_implemented_without_test_count()`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:3085` now returns `spec_ids=[r["id"] for r in rows]`, not the prior pre-truncated `rows[:20]` list.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\web\templates\pipeline.html:150` displays only the first 20 M18 spec IDs, and `pipeline.html:153` through `pipeline.html:154` renders the omitted-count notice from the full `m18.spec_ids|length`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_web_pipeline.py:134` through `test_web_pipeline.py:138` deterministically asserts the affected SPEC-001 drilldown link.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_web_pipeline.py:140` through `test_web_pipeline.py:165` seeds 22 implemented specs without linked tests and asserts the "and 2 more" truncation notice plus spec links.

## Verification Commands

All commands were run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`.

```text
python -m pytest tests/test_web_pipeline.py -q --tb=short
10 passed in 1.66s

python -m pytest tests/test_lifecycle_metrics.py -q --tb=short
36 passed in 3.81s

python -m pytest -q --tb=short
400 passed, 11 skipped in 26.20s

python -m ruff check .
All checks passed!

python -m ruff format --check .
50 files already formatted
```

## Findings

No blocking findings remain for SPEC-2101 approval.

The prior NO-GO issue is fixed: with more than 20 implemented/verified specs
lacking linked tests, the metric payload retains the full affected set, the
dashboard still limits rendered links to 20, and the omitted-count notice is now
reachable.

## Required Action Items Or Conditions

None for approval.

Non-blocking follow-up: keep the health thresholds documented as heuristic UI
defaults. Do not promote them to validated operating targets unless the owner
explicitly accepts those values as policy.
