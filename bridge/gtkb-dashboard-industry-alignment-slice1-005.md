REVISED

# GTKB Dashboard Industry Alignment — Slice 1 (REVISED-2)

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-DASHBOARD-001 (new, this bridge)
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Responds to:** NO-GO at `bridge/gtkb-dashboard-industry-alignment-slice1-004.md`

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`. Prior DA context for this
thread:

- `DELIB-0840` — fresh-session self-initialization dashboard KPI coverage
  (scope parent).
- `DELIB-GTKB-IDP-TERMINOLOGY` (2026-04-24) — GT-KB IDP categorization;
  dashboard is the IDP's observability surface.
- No prior deliberation exists for alert-rule anchoring or DORA
  telemetry. This thread remains net-new.

---

## Cross-NO-GO Discipline

| Finding | Required action | This revision |
|---------|----------------|--------------|
| -002 Finding 1 — Slice 1B targets regenerated composite, not real history owner | Drop or re-scope around authoritative path | Dropped in `-003`; retention already bounded by `MAX_HISTORY=200` at `refresh_dashboard_db.py:346-349`. |
| -002 Finding 2 — Slice 1C/1D edit generated JSON | Route through generator + pinned tests | Re-scoped in `-003`. |
| -002 Finding 3 — Slice 1D DORA not derivable from current telemetry | Remove or add data-model work first | Removed in `-003`. Filed as follow-on bridge `gtkb-dora-telemetry-foundation`. |
| **-004 Finding 1** — Slice 1E alert rules named `release_blocker_count`, `failing_ci_count`, `data_freshness_age_minutes` which the refresh pipeline does not emit | Either route alerts to existing keys/queries, or add + test the missing metric names in `refresh_dashboard_db.py` before proposing alerts that depend on them | **Done (Option 1).** Alert rules now anchor to the authoritative keys emitted by `scripts/gtkb_dashboard/refresh_dashboard_db.py:594-600` and the inline `refresh_runs` SQL used by the generator's Refresh Age panel. Each rule's SQL/metric anchor is specified below and will be asserted by the validator test. |

---

## 1. Slice 1 Deliverables (REVISED-2)

### A. Progressive-enhancement landing page (`docs/gtkb-dashboard/index.html`) — unchanged

- Replace meta-refresh with a static page that `fetch()`es
  `dashboard-data.json` and shows the most-recent KPI snapshot + `generated_at`
  with age badge (green < 15 min, yellow 15–60 min, red > 60 min).
- Explicit "Open live dashboard" button to the Grafana URL (no auto redirect).
- Documents `install_local_grafana.ps1` / `start_local_dashboard.ps1` inline.
- `prefers-color-scheme: dark` CSS fallback.
- Semantic headings + button-element anchors + sufficient color contrast.

### C. Per-panel freshness surfacing — via the generator — unchanged

- Modify `scripts/gtkb_dashboard/generate_grafana_dashboard.py` so stat-panel
  builders include `last_refreshed_at` secondary value.
- Run the generator; commit regenerated
  `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` in the same
  commit.
- Update `tests/scripts/test_gtkb_dashboard_grafana.py` to assert the new
  secondary value on at least 3 representative panels.

### E. Alert-routing skeleton (`provisioning/alerting/`) — REVISED anchoring

Each alert rule names the **exact authoritative source** it reads.

**`release-blockers.yaml`** — fires when there is any release blocker.
- Source: `current_metrics` table, key `release_blockers` (emitted at
  `scripts/gtkb_dashboard/refresh_dashboard_db.py:596`).
- Grafana query: `SELECT value FROM current_metrics WHERE metric_key =
  'release_blockers';` (integer).
- Condition: `value > 0`.

**`failing-ci.yaml`** — fires when CI / testing failing count is non-zero.
- Source: `current_metrics` table, key `ci_testing_failing` (emitted at
  `scripts/gtkb_dashboard/refresh_dashboard_db.py:597`).
- Grafana query: `SELECT value FROM current_metrics WHERE metric_key =
  'ci_testing_failing';` (integer).
- Condition: `value > 0`.

**`stale-data.yaml`** — fires when data freshness exceeds 60 minutes.
- Source: computed from `refresh_runs` via the same SQL pattern already used
  by the generator's Refresh Age panel at
  `scripts/gtkb_dashboard/generate_grafana_dashboard.py:338-354`.
- Grafana query:
  ```sql
  SELECT COALESCE(
      CAST((julianday('now') - julianday(MAX(COALESCE(completed_at, started_at)))) * 24 * 60 AS INTEGER),
      9999
  ) AS value
  FROM refresh_runs;
  ```
- Condition: `value > 60`.

Alerts route to the Grafana alert list only (no external notifier wiring;
that is Slice 2 scope).

**Validator test** (`tests/scripts/test_gtkb_dashboard_alerting.py`):
1. Each alert YAML file parses via `PyYAML` without error.
2. Each rule has required keys: `uid`, `title`, `condition`, `data[0].model.rawSql`.
3. The `rawSql` of each rule references **only** tables/columns that exist
   in `scripts/gtkb_dashboard/schema.sql`. Implementation: parse the SQL to
   extract table names; assert every referenced table is in the set parsed
   from `schema.sql`. This prevents future alert drift against schema
   changes.
4. The `release-blockers` and `failing-ci` rules reference `current_metrics`
   rows that the refresh pipeline actually emits — asserted by running a
   fixture refresh (via `refresh_dashboard_db.refresh_database` against an
   in-memory SQLite) and confirming the alert's metric key is present in
   the resulting `current_metrics` rows.

This closes the Codex -004 concern that a passing PyYAML test could coexist
with signals that never fire.

---

## 2. Out of Scope for This Bridge

Filed as separate follow-on bridges after this thread VERIFIED:

- **`gtkb-dora-telemetry-foundation`** (prerequisite for any DORA panel).
- **`gtkb-dora-panels`** (consumer, after foundation lands).
- **`gtkb-dashboard-retention-policy`** (revisit iff `MAX_HISTORY=200` proves
  insufficient).
- **`gtkb-dashboard-industry-alignment-slice2`** — bridge swimlane, subject
  selector, coverage/security/CI panels, alert notifier wiring.
- **`gtkb-dashboard-industry-alignment-slice3`** — SLO/error budget, flow
  metrics, PR/branch health, incident/MTTR (depends on DORA foundation),
  remote exposure, WCAG audit.

---

## 3. Implementation Sequence

1. (A) Rewrite `docs/gtkb-dashboard/index.html`; verify in Chromium + Edge
   with Grafana down and up.
2. (C) Extend generator panel builders with `last_refreshed_at` secondary
   value. Regenerate JSON; commit in same change.
3. (C) Update pinned `test_gtkb_dashboard_grafana.py` assertions.
4. (E) Add 3 YAML alert rules with the SQL/metric anchors specified above.
5. (E) Add `test_gtkb_dashboard_alerting.py` with schema-anchored validator
   that parses YAML, validates structure, and verifies each `rawSql`'s table
   references exist in `schema.sql`. For the two `current_metrics`-sourced
   rules, run a fixture refresh against in-memory SQLite and assert the
   rule's `metric_key` appears in the `current_metrics` rows the pipeline
   emits.
6. Run test lanes; confirm GREEN.
7. Post-implementation report.

---

## 4. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Landing page breaks when Grafana absent | Page renders, shows KPI snapshot + Open-live button. |
| Age badge thresholds wrong | Synthetic-timestamp test asserts green/yellow/red boundaries. |
| §C edits bypass generator | Generator + regenerated JSON + test updates land in the same commit. |
| Generator output drifts from tests | Pinned panel assertions updated for every panel with the new secondary value. |
| **Alert rules target non-existent metrics** | **Validator test parses each rule's `rawSql` and asserts every referenced table exists in `schema.sql`; for `current_metrics` rules, fixture-refresh asserts the metric_key is emitted by the pipeline.** |
| §E YAML files malformed | `PyYAML` parse + required-keys check. |
| Alert notifier silently missing | Explicitly out of scope; Slice 2 wires notifier. |
| DORA metrics fabricated | No DORA panel; filed as `gtkb-dora-telemetry-foundation` follow-on. |

---

## 5. Files Touched

**New:**
- `docs/gtkb-dashboard/grafana/provisioning/alerting/release-blockers.yaml`
- `docs/gtkb-dashboard/grafana/provisioning/alerting/failing-ci.yaml`
- `docs/gtkb-dashboard/grafana/provisioning/alerting/stale-data.yaml`
- `tests/scripts/test_gtkb_dashboard_alerting.py`

**Modified:**
- `docs/gtkb-dashboard/index.html` (rewrite)
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py`
  (`last_refreshed_at` secondary value)
- `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json`
  (regenerated)
- `tests/scripts/test_gtkb_dashboard_grafana.py` (assertions)
- `memory/work_list.md` (add `GTKB-DASHBOARD-001` entry + follow-on
  bridge names)

**Not touched:**
- `memory/gtkb-dashboard-history.json` / `_append_snapshot` (retention
  already bounded; no work needed).
- `schema.sql` / `delivery_timeline_events` / any telemetry schema (no
  DORA work this slice).
- `src/`, integration code, upstream `groundtruth-kb/`.

---

## 6. Decision Needed From Owner

None. Awaiting Loyal Opposition review.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
