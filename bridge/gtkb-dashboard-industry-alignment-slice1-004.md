NO-GO

# Loyal Opposition Review - GTKB Dashboard Industry Alignment Slice 1

**Date:** 2026-04-24
**Document:** `gtkb-dashboard-industry-alignment-slice1`
**Reviewed file:** `bridge/gtkb-dashboard-industry-alignment-slice1-003.md`
**Verdict:** NO-GO

## Rationale

The revision correctly removed the retention and DORA issues, and items A and C
are now routed through the right owners. Item E is still scoped against alert
signal names that the refresh pipeline and live SQLite dashboard database do
not produce. Approving the slice as written would allow syntactically valid
alert YAML and a passing validator test to land while pointing at non-existent
signals.

## Findings

### 1. Slice 1E still targets non-existent alert metrics

**Proposal claim:** add alert rules firing on `release_blocker_count`,
`failing_ci_count`, and `data_freshness_age_minutes`.

**Evidence:**

- `bridge/gtkb-dashboard-industry-alignment-slice1-003.md:108-111` names those
  three rule conditions.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py:594-600` only persists
  `project_health_issues`, `release_blockers`, `ci_testing_failing`,
  `security_scan_posture`, `governance_bridge_items`, and `data_freshness` into
  `current_metrics`.
- `scripts/gtkb_dashboard/schema.sql:114-118` defines `current_metrics`
  payloads around stored metric keys/labels/values; there is no
  `release_blocker_count` or `failing_ci_count` alias emitted by the refresh
  path.
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py:339-347` computes the
  "Refresh Age" panel directly from `refresh_runs`; there is no persisted
  `data_freshness_age_minutes` row in `data_freshness`.
- Live SQLite probe against `memory/gtkb-dashboard.sqlite` returned:
  - `select count(*) from current_metrics where metric_key='release_blocker_count'` -> `0`
  - `select count(*) from current_metrics where metric_key='failing_ci_count'` -> `0`
  - `select count(*) from data_freshness where key='data_freshness_age_minutes'` -> `0`

**Risk / impact:** Implementation can produce structurally valid alert-rule
YAML and a passing PyYAML parse test while wiring alerts to signals the
dashboard never emits. That creates silent no-op alerting rather than the
intended release-blocker, failing-CI, and stale-data coverage.

**Required action:** Revise Slice 1E against authoritative sources. Either:

1. route alerts to existing keys/queries (`release_blockers`,
   `ci_testing_failing`, and the existing refresh-age SQL over `refresh_runs`);
   or
2. explicitly add and test the missing persisted metric names in
   `refresh_dashboard_db.py` / schema before proposing alert rules that depend
   on them.

## Conditions For GO

1. Keep A and C as currently revised.
2. Rewrite E so each alert rule names the exact authoritative SQL query or
   persisted metric key it will evaluate, using the current repo schema and
   test fixtures.
3. Add the alert-validator test only after the rule inputs are anchored to
   real fields or queries, not placeholder names.

## Decision Needed From Owner

None. Revise and resubmit through the bridge.
