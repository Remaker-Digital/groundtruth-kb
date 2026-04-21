# Implementation Proposal: SPEC-2101 Pipeline Dashboard

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Target:** groundtruth-kb
**Spec:** SPEC-2101 (Pipeline dashboard: lifecycle metrics visualization)
**Work Item:** WI-3160

---

## 1. What This Implements

A `/pipeline` page in the groundtruth-kb web UI that visualizes the 9 lifecycle
metrics from SPEC-2100's `get_lifecycle_metrics()`. Pure HTML/CSS with the
existing dark theme — no external charting libraries.

## 2. Files Changed

| File | Change |
|------|--------|
| `src/groundtruth_kb/web/app.py` | Added `/pipeline` route handler |
| `src/groundtruth_kb/web/templates/pipeline.html` | New template: 9 metric cards in 4 groups |
| `src/groundtruth_kb/web/templates/base.html` | Added "Pipeline" nav link |
| `src/groundtruth_kb/web/static/style.css` | Added metric card CSS (~100 lines) |
| `tests/test_web_pipeline.py` | 9 tests: route, content, empty DB, M18 drilldown |

## 3. Design

### Route
```python
@app.get("/pipeline", response_class=HTMLResponse)
async def pipeline_dashboard(request: Request):
    metrics = db.get_lifecycle_metrics()
    summary = db.get_summary()
    return templates.TemplateResponse(...)
```

### Layout
- Summary strip: total specs, test procedures, work items, pipeline events
- 4 metric groups in responsive 3-column grid:
  - **Throughput:** M2 (revision rounds), M4 (spec-to-implemented duration)
  - **Quality:** M6 (defect injection rate), M10 (defect resolution time), M11 (regression rate)
  - **Coverage:** M16 (verified with passing tests), M17 (stale test ratio), M18 (specs without tests)
  - **Lifecycle:** M12 (retirement rate)

### Each Metric Card
- Metric ID badge (e.g., "M2")
- Human-readable title
- Current value (ratios as %, durations in hours, counts as integers)
- Health indicator dot (green/amber/red) based on thresholds
- Supporting detail line (e.g., "5 of 325 specs")
- M18 includes collapsible drill-down with spec ID links

### Health Thresholds
All hardcoded as tunable constants:
- M2: green <=3, amber <=5, red >5
- M4: green <=72h, amber <=168h, red >168h
- M6: green <=0.1, amber <=0.3, red >0.3
- M10: green <=48h, amber <=168h, red >168h
- M11: green <=0.05, amber <=0.15, red >0.15
- M12: green <=0.2, amber <=0.4, red >0.4
- M16: green >=0.8, amber >=0.5, red <0.5
- M17: green <=0.1, amber <=0.3, red >0.3
- M18: green =0, amber <=5, red >5

### Empty DB Handling
All metrics show "N/A" with neutral health dots when `value is None`.

## 4. Test Results

```
Pipeline tests: 9 passed in 1.75s
Full suite: 399 passed, 11 skipped in 26.72s
Lint: ruff check . — All checks passed
Format: ruff format --check . — All files formatted
```

## 5. Review Questions for Codex

1. Are the health thresholds reasonable starting points?
2. Should the thresholds be configurable via `groundtruth.toml` rather than
   hardcoded in the Jinja2 template?
3. Any concerns with the CSS approach (no charting library)?
