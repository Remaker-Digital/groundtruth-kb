GO

# Loyal Opposition Review - GTKB Dashboard Industry Alignment Slice 1

**Date:** 2026-04-24
**Document:** `gtkb-dashboard-industry-alignment-slice1`
**Reviewed file:** `bridge/gtkb-dashboard-industry-alignment-slice1-005.md`
**Verdict:** GO

## Claim

`-005` resolves the prior blocker from `-004`. The slice is now scoped to repo
owners and signals that actually exist: the landing page remains local to
`docs/gtkb-dashboard/index.html`, per-panel freshness stays routed through the
Grafana generator and pinned tests, and alert rules are anchored to the live
SQLite schema and refresh pipeline rather than placeholder metric names.

## Rationale

No blocking findings remain.

## Findings

No blocking findings.

**Evidence:**

- `bridge/gtkb-dashboard-industry-alignment-slice1-005.md:64-90` now anchors
  the three alert rules to `current_metrics.release_blockers`,
  `current_metrics.ci_testing_failing`, and the existing refresh-age SQL over
  `refresh_runs`.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py:594-600` emits
  `release_blockers` and `ci_testing_failing` into `current_metrics`, matching
  the revised proposal's alert inputs.
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py:294-295` already uses
  the same `SELECT value FROM current_metrics WHERE metric_key = '...'`
  pattern for stat panels, and
  `scripts/gtkb_dashboard/generate_grafana_dashboard.py:337-347` already uses
  the same `refresh_runs` SQL pattern the revised `stale-data.yaml` proposal
  cites.
- `scripts/gtkb_dashboard/schema.sql:3-9` defines `refresh_runs(started_at,
  completed_at, ...)`, and `scripts/gtkb_dashboard/schema.sql:124-130` defines
  `current_metrics(metric_key, value, ...)`, so the proposed alert queries are
  schema-valid against the current repo.
- Live SQLite probe against `memory/gtkb-dashboard.sqlite` on 2026-04-24
  returned rows for both current-metric keys and a valid refresh-age result:
  - `select metric_key, value from current_metrics where metric_key in ('release_blockers','ci_testing_failing') order by metric_key`
    -> `('ci_testing_failing', 0.0)`, `('release_blockers', 0.0)`
  - `SELECT COALESCE(CAST((julianday('now') - julianday(MAX(COALESCE(completed_at, started_at)))) * 24 * 60 AS INTEGER), 9999) AS value FROM refresh_runs`
    -> `(6,)`
- `tests/scripts/test_gtkb_dashboard_grafana.py:123-135` already exercises
  `refresh_dashboard_db.refresh_database(...)` against a temporary SQLite
  database, so the revised alert-validator plan has an existing fixture pattern
  to reuse for proving those metric keys are emitted.
- `tests/scripts/test_gtkb_dashboard_grafana.py:157-182` already pins the
  generated dashboard structure, which matches `-005`'s requirement to land the
  generator change, regenerated JSON, and test updates together.

## Implementation Conditions

1. Keep the alert YAML rules bound to the exact authoritative sources named in
   `-005`; do not reintroduce alias metric names such as the rejected
   `release_blocker_count`, `failing_ci_count`, or
   `data_freshness_age_minutes`.
2. Make `tests/scripts/test_gtkb_dashboard_alerting.py` assert the exact
   `metric_key` literals for the two `current_metrics`-backed rules in addition
   to table-level schema anchoring, so future edits cannot silently drift back
   to placeholder names.
3. Land the generator change, regenerated
   `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json`, and
   `tests/scripts/test_gtkb_dashboard_grafana.py` updates in the same change as
   proposed.

## Decision Needed From Owner

None. Proposal may proceed to implementation under the conditions above.
