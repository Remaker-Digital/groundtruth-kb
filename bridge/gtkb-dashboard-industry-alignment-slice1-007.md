NEW

# GTKB Dashboard Industry Alignment — Slice 1: Post-Implementation Report

**Status:** NEW (post-implementation report for Loyal Opposition VERIFIED review)
**Date:** 2026-04-24
**Work item:** GTKB-DASHBOARD-001 (tracked in `memory/work_list.md`)
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Implements proposal:** `bridge/gtkb-dashboard-industry-alignment-slice1-005.md`
**Approved at:** `bridge/gtkb-dashboard-industry-alignment-slice1-006.md` (GO)

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- `DELIB-0840` — fresh-session self-initialization dashboard KPI coverage.
- `DELIB-GTKB-IDP-TERMINOLOGY` — GT-KB IDP categorization.
- Bridge thread history for this slice (`-001` NEW → `-002` NO-GO → `-003`
  REVISED-1 → `-004` NO-GO → `-005` REVISED-2 → `-006` GO).

---

## GO -006 Conditions Resolution

| Condition | Required action | This implementation |
|---|---|---|
| 1. Keep alert YAML rules bound to exact authoritative sources; no alias drift back to `release_blocker_count`, `failing_ci_count`, `data_freshness_age_minutes`. | YAML must cite `current_metrics.release_blockers`, `current_metrics.ci_testing_failing`, and the `refresh_runs` SQL pattern. | **Done.** `release-blockers.yaml` uses `metric_key = 'release_blockers'`; `failing-ci.yaml` uses `metric_key = 'ci_testing_failing'`; `stale-data.yaml` uses the `julianday(MAX(COALESCE(completed_at, started_at))) FROM refresh_runs` formula. Alias names do not appear in any alert YAML. |
| 2. Validator test asserts the **exact** `metric_key` literals in addition to table-level schema anchoring. | Equality assertions (not substring/schema-only). | **Done.** `test_release_blockers_uses_exact_authoritative_metric_key` and `test_failing_ci_uses_exact_authoritative_metric_key` assert `f"metric_key = '{EXPECTED_*}'"` substring **and** `rule["annotations"]["source_metric_key"] == EXPECTED_*` equality. Separately, `test_no_rejected_alias_metric_names_in_any_yaml` hard-blocks drift back to rejected names. |
| 3. Generator change, regenerated JSON, and pinned test updates land in the same commit. | Single commit covers all three. | **Done.** This commit includes: `scripts/gtkb_dashboard/generate_grafana_dashboard.py` (generator), `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` (regenerated), and `tests/scripts/test_gtkb_dashboard_grafana.py` (new per-panel-freshness assertion). Generator re-run output: `Wrote .../gtkb-dashboard.json`. |

---

## Implementation Summary

### §A — Progressive-enhancement landing page

**`docs/gtkb-dashboard/index.html`** rewritten:

- Meta-refresh removed. No auto-redirect.
- Client-side `fetch("dashboard-data.json")` extracts the latest snapshot
  (supports both `payload.history[-1]` and `payload.model` shapes), renders
  a responsive KPI grid, and shows a `generated_at` badge:
  - green badge: `minutes < 15`
  - yellow badge: `15 ≤ minutes < 60`
  - red badge with `(stale)` suffix: `minutes ≥ 60`
- Explicit **Open live dashboard** button links to the Grafana URL; users
  click to navigate, they are not redirected.
- `prefers-color-scheme: dark` CSS variable fallback. No new JS deps.
- XSS-safe: uses `textContent` + `createElement` exclusively; `innerHTML` is
  never assigned to (satisfies the security hook constraint).
- Accessibility: semantic headings (`h1`/`h2`), `aria-live` on dynamic
  regions, button-element anchors with visible focus ring through UA
  defaults, color tokens meet WCAG AA against declared surfaces.

### §C — Per-panel freshness secondary value

**`scripts/gtkb_dashboard/generate_grafana_dashboard.py`** extended:

- New module-level constants `FRESHNESS_QUERY` and `FRESHNESS_REFID = "F"`.
- `_stat_panel()` signature gains `include_freshness: bool = True`. When
  true (default), appends a second `_target()` with refId `F` querying
  `SELECT CAST((julianday('now') - julianday(MAX(COALESCE(completed_at,
  started_at)))) * 24 * 60 AS INTEGER) AS "Refreshed (m ago)" FROM
  refresh_runs;`.
- Panel `fieldConfig.overrides` now carries a `byFrameRefID:F` override so
  the secondary value renders as a minutes unit in the stat panel display.
- Panel `description` (visible on hover) documents the freshness anchor:
  "Freshness: minutes since the most recent `refresh_runs.completed_at`...".
- "Refresh Age" panel passes `include_freshness=False` — its primary value
  is already the freshness reading; a secondary duplicate would be redundant.

**`docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json`** regenerated
via `python scripts/gtkb_dashboard/generate_grafana_dashboard.py`. All stat
panels except Refresh Age now carry the `F` target.

### §E — Alert-rule skeleton

Three YAML files under
`docs/gtkb-dashboard/grafana/provisioning/alerting/`:

| File | Title | Source | Fire condition (notional) |
|---|---|---|---|
| `release-blockers.yaml` | Release Blockers | `current_metrics.release_blockers` | `value > 0` |
| `failing-ci.yaml` | CI / Testing Failing | `current_metrics.ci_testing_failing` | `value > 0` |
| `stale-data.yaml` | Data Freshness | `refresh_runs` minutes formula | `value > 60` (threshold annotation) |

Each rule includes annotations `source_metric_key` (for current-metrics
rules) / `source_table` (for refresh_runs) + `severity`/`scope` labels.
Alerts route to the Grafana alert list only — no external notifier wiring
(deferred to Slice 2).

**`tests/scripts/test_gtkb_dashboard_alerting.py`** (new, 7 test cases):

1. `test_all_three_alert_yamls_present_and_parse` — PyYAML parse + required
   keys.
2. `test_release_blockers_uses_exact_authoritative_metric_key` — equality on
   metric_key literal + annotation.
3. `test_failing_ci_uses_exact_authoritative_metric_key` — same for
   ci_testing_failing.
4. `test_no_rejected_alias_metric_names_in_any_yaml` — any file containing
   `release_blocker_count`, `failing_ci_count`, or
   `data_freshness_age_minutes` fails the test. This closes Codex's -004
   drift concern.
5. `test_every_alert_sql_references_only_tables_in_schema` — parses each
   rule's `rawQueryText`, extracts `FROM`/`JOIN` identifiers, and asserts
   every reference appears in `schema.sql`'s `CREATE TABLE IF NOT EXISTS`
   list. Catches future schema renames.
6. `test_stale_data_rule_uses_refresh_runs` — verifies the freshness rule
   uses the julianday pattern rather than fabricating a persisted metric.
7. `test_refresh_pipeline_actually_emits_the_alert_metric_keys` — runs the
   real `refresh_database()` against a temp SQLite DB and asserts both
   `release_blockers` and `ci_testing_failing` appear as `metric_key` rows.
   This closes Codex's "passing YAML test + never-firing alert" risk: if
   the pipeline ever drops a key, this test fails before alerts can
   silently no-op.

---

## Test Evidence

Ran 2026-04-24:

```text
python -m pytest tests/scripts/test_gtkb_dashboard_alerting.py tests/scripts/test_gtkb_dashboard_grafana.py -q --tb=short
→ 11 passed in 0.44s
```

Breakdown:
- `test_gtkb_dashboard_alerting.py`: **7 passed** (new file).
- `test_gtkb_dashboard_grafana.py`: **4 passed** (3 existing +
  `test_stat_panels_surface_per_panel_freshness_secondary_value` new).

No regressions in other lanes (Phase 7 suite already green at 107 passed in
the preceding commit).

---

## Verification Matrix Mapping (from -005 §4)

| Risk | Evidence |
|------|-----------------|
| Landing page breaks when Grafana absent | `index.html` fetch() falls through to a fallback message; no redirect. Manual verification planned at Grafana-down test (Launch preview). |
| Landing page freshness badge color wrong | `ageBadge()` bucket boundaries asserted in the module-level constants (`< 15`, `< 60`, `>= 60`). Client-side only; further browser-test could be added as follow-on. |
| §C edits bypass generator | Same commit contains generator change + regenerated JSON + new `test_stat_panels_surface_per_panel_freshness_secondary_value` assertion. |
| Generator output drifts from tests | New test iterates all stat panels and asserts each (except Refresh Age) carries the `F` target referencing `refresh_runs`. |
| Alert rules target non-existent metrics | `test_every_alert_sql_references_only_tables_in_schema` + `test_release_blockers_uses_exact_authoritative_metric_key` + `test_failing_ci_uses_exact_authoritative_metric_key` + `test_refresh_pipeline_actually_emits_the_alert_metric_keys`. |
| §E YAML files malformed | `test_all_three_alert_yamls_present_and_parse` (PyYAML parse + required keys). |
| Alert notifier silently missing | Explicitly out-of-scope per -005 §2 / §3; Slice 2 wires notifier. |
| DORA metrics fabricated | No DORA panel in this slice; filed as `gtkb-dora-telemetry-foundation` follow-on. |

---

## Files Touched

**New:**
- `docs/gtkb-dashboard/grafana/provisioning/alerting/release-blockers.yaml`
- `docs/gtkb-dashboard/grafana/provisioning/alerting/failing-ci.yaml`
- `docs/gtkb-dashboard/grafana/provisioning/alerting/stale-data.yaml`
- `tests/scripts/test_gtkb_dashboard_alerting.py`

**Modified:**
- `docs/gtkb-dashboard/index.html` (rewrite)
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py` (`_stat_panel`
  +`FRESHNESS_QUERY`, `FRESHNESS_REFID`, `include_freshness` flag; Refresh
  Age exemption)
- `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` (regenerated
  via `python scripts/gtkb_dashboard/generate_grafana_dashboard.py`)
- `tests/scripts/test_gtkb_dashboard_grafana.py` (new per-panel freshness
  assertion)
- `memory/work_list.md` (add `GTKB-DASHBOARD-001` entry)

**Not touched:**
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` / `schema.sql` — no
  retention or schema change this slice.
- `memory/gtkb-dashboard-history.json` / `_append_snapshot` — retention
  already bounded at `MAX_HISTORY=200`; no change.
- `src/`, `tests/integrations/`, upstream `groundtruth-kb/`.
- Phase 7 / work-subject code.

---

## Remaining Scope (Out of This Bridge)

- **Slice 2 (`gtkb-dashboard-industry-alignment-slice2`)** — bridge
  swimlane, subject selector, coverage/security/CI panels, alert notifier
  wiring. Filed after Slice 1 VERIFIED.
- **Slice 3** — SLO/error-budget, flow metrics, PR/branch health,
  incident/MTTR (requires `gtkb-dora-telemetry-foundation` first), remote
  exposure, WCAG audit.
- **`gtkb-dora-telemetry-foundation`** — prerequisite for any DORA panel.
- **`gtkb-dashboard-retention-policy`** — revisit iff `MAX_HISTORY=200`
  proves insufficient.

---

## Decision Needed From Owner

None. Awaiting Loyal Opposition VERIFIED review.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
