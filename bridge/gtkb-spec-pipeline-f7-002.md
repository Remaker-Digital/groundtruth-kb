# NO-GO: F7 Session Health Dashboard Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f7-001.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

Session health snapshots are a reasonable extension of existing lifecycle metrics, but the proposal depends on F3/F4 outputs without declaring those dependencies, and threshold persistence/configuration is not specified.

## Findings

### 1. Blocking: Dependencies are underdeclared and unresolved

**Evidence:** F7 declares only F1 as a dependency at bridge/gtkb-spec-pipeline-f7-001.md:7. The snapshot includes F3 quality distribution and F4 constraint coverage at bridge/gtkb-spec-pipeline-f7-001.md:36. The implementation sequence also calls F1/F3/F4 coverage queries at bridge/gtkb-spec-pipeline-f7-001.md:161. F1, F3, and F4 are currently NO-GO.

**Risk/impact:** The dashboard cannot produce the proposed snapshot shape until F3 and F4 APIs exist.

**Required action:** Add F3/F4 dependencies or define a degraded first version that snapshots only existing lifecycle metrics and summary stats.

### 2. Major: Existing dashboard and metric surfaces need an integration plan

**Evidence:** GT-KB already computes lifecycle metrics through `get_lifecycle_metrics()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3087 and serves a pipeline dashboard at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/web/app.py:283. F7 adds `render_health_dashboard()` text output at bridge/gtkb-spec-pipeline-f7-001.md:122.

**Risk/impact:** A second dashboard path can diverge from the web dashboard and lifecycle metric tests.

**Required action:** Specify whether F7 extends the existing `/pipeline` dashboard, adds a text-only API, or both. Include shared formatting/data-layer boundaries.

### 3. Major: Threshold configuration has no storage contract

**Evidence:** F7 proposes `get_alert_thresholds()` and `set_alert_thresholds()` at bridge/gtkb-spec-pipeline-f7-001.md:129, and says thresholds are configurable at bridge/gtkb-spec-pipeline-f7-001.md:93. The only new table is `session_snapshots` at bridge/gtkb-spec-pipeline-f7-001.md:141; no thresholds table or config-file location is specified.

**Risk/impact:** Alert behavior may be process-local and non-reproducible, or hidden in ad hoc JSON blobs.

**Required action:** Define where thresholds live: GT config, a new table, environment config, or specifications. Add export/import and test coverage for persistence.

### 4. Major: Session ownership is unclear

**Evidence:** F7 captures snapshots at session end and computes deltas at session start at bridge/gtkb-spec-pipeline-f7-001.md:27 and bridge/gtkb-spec-pipeline-f7-001.md:45, but implementation step 7 defers session-start integration to an Agent Red skill/hook at bridge/gtkb-spec-pipeline-f7-001.md:166.

**Risk/impact:** The core package may ship APIs that are never called consistently, making the trend data unreliable.

**Required action:** Define the GT-KB-owned trigger surface: CLI command, hook template, web action, or library-only API with explicit downstream adoption steps.

## Conditions For GO

1. Declare/resolve F1/F3/F4 dependencies or scope F7 to existing metrics.
2. Define integration with existing lifecycle metrics and web dashboard.
3. Specify threshold persistence.
4. Specify session boundary trigger ownership.

