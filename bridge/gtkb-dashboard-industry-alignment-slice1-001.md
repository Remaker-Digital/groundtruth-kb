NEW

# GTKB Dashboard Industry Alignment — Slice 1: Fast High-Value Fixes

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-DASHBOARD-001 (new)
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Prior deliberations:** S306 owner review of `docs/gtkb-dashboard/` surfaced
four classes of gap (missing DORA/SLO/flow metrics; bridge visualization
absent; usability/fragility issues; accessibility gaps). Owner directed
drafting Slice 1 covering the fast high-value subset independently of
GTKB-ISOLATION-015 Slice 2.

---

## 1. Background and Scope

The Agent Red / GT-KB dashboard lives under `docs/gtkb-dashboard/`:

- `index.html` — static landing page (currently a 0-second meta-refresh
  redirect to local Grafana at `127.0.0.1:3000`).
- `dashboard-data.json` — KPI history snapshots written every 3 minutes.
- `session-startup-report.md` / `session-wrapup-report.md` — text-rendered
  startup/wrapup reports.
- `grafana/` — provisioned Grafana assets (dashboards JSON, provisioning
  configs, SQLite datasource plugin hookup).

A full owner review against industry-standard engineering delivery dashboards
(DORA, SLO/SRE, flow metrics, SPACE framework, security posture, cost/FinOps,
accessibility/a11y) identified **three broad classes of gap**:

| Class | Examples |
|-------|---------|
| Missing industry-standard metrics | DORA four keys; SLO + error budgets; flow/WIP aging; coverage trend; security posture; branch/PR health; cost; incident/MTTA/MTTR. |
| Completeness gaps specific to this system | Bridge state swimlane; two-subject scoping; "what changed since last session"; CI workflow embed; KPI ownership; session-focus choices rendered in the dashboard, not only in Markdown. |
| Usability / fragility issues | `index.html` redirect breaks when Grafana is not running; `dashboard-data.json` grows unbounded; no per-panel freshness; no dark-mode / a11y / mobile consideration; `provisioning/alerting` folder empty; undated static PDF. |

Slice 1 (this bridge) covers the **fast, high-value, low-risk subset** that
delivers visible improvements without architectural change. Slice 2 and
Slice 3 are named at the end of this document but **filed as follow-on
bridges** (not in this scope).

---

## 2. Slice 1 Deliverables

### A. Progressive-enhancement landing page (`docs/gtkb-dashboard/index.html`)

**Current gap:** The landing page is `<meta http-equiv="refresh"
content="0; url=...">`. Any visitor without Grafana running locally on
`127.0.0.1:3000` sees a broken/frozen redirect loop.

**Proposed change:** Replace the meta-refresh with a static informational
page that:

- Renders the **most-recent KPI snapshot** from `dashboard-data.json` as
  progressive-enhancement HTML (read at page load via fetch; graceful
  fallback if the JSON is missing).
- Surfaces the **generated_at** timestamp of the snapshot (with age badge:
  green < 15 min, yellow 15–60 min, red > 60 min).
- Links to the live Grafana URL with an explicit "Open live dashboard"
  button (not automatic redirect).
- Shows the install command (`install_local_grafana.ps1`) and start command
  (`start_local_dashboard.ps1`) so a first-time visitor can act.
- Includes a dark-mode CSS fallback using `prefers-color-scheme`.

**Scope:** single HTML file. No new JS dependencies.

### B. Retention policy for `dashboard-data.json`

**Current gap:** `dashboard-data.json` currently contains 7,549 lines of
3-minute snapshots appended without bound. This will balloon git diffs and
pollute PR review over weeks.

**Proposed change:** Add a retention step to the snapshot writer:

- Keep snapshots from the last **7 days** in `dashboard-data.json` (rolling
  window).
- Older snapshots either rolled into the existing `memory/gtkb-dashboard.sqlite`
  aggregate or dropped (simpler; SQLite already has `kpi_snapshots` table).
- Add a `retention_days` config value readable from env
  (`GTKB_DASHBOARD_RETENTION_DAYS`, default 7).
- Add a regression test that proves retention trims correctly at the
  boundary.

**Scope:** `scripts/gtkb_dashboard/refresh_dashboard_db.py` (or wherever
`dashboard-data.json` writes happen) + a new test.

### C. Per-panel freshness on the Grafana dashboard

**Current gap:** A single global "Refresh Age" stat tells users when the
SQLite DB was last refreshed, but individual panels have no per-query
freshness signal. Industry convention (Grafana + most commercial
observability tools) is per-panel timestamp.

**Proposed change:** Extend Grafana panel queries to return a
`last_refreshed_at` column alongside the primary metric, and display it as
a subheader via Grafana's stat-panel secondary value or a unit-transform.
Where a panel already reads from a table with an `as_of` column, surface
that timestamp; where it doesn't, use the parent `dashboard_metadata`
timestamp.

**Scope:** `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` edits
to ~10 stat panels. No schema change.

### D. DORA Four-Keys panel from existing `delivery_timeline_events`

**Current gap:** The `delivery_timeline_events` table already captures
stages (commit, build, test, staging_deployment, production_deployment) with
timestamps. Those are the raw inputs for the DORA four keys but the
dashboard surfaces none of the computed metrics.

**Proposed change:** Add a **DORA Four Keys** row of 4 stat panels
computing:

1. **Deployment frequency** — count of `production_deployment` events over
   the last 30 days.
2. **Lead time for changes** — median interval (commit → production) over
   the last 30 deployed events.
3. **Change failure rate** — percentage of deployed changes that required a
   hotfix or rollback within 24 hours, over the last 90 days. (If the
   schema does not yet distinguish rollbacks, surface a "requires hotfix
   tagging" annotation and leave the value at null rather than fabricating.)
4. **Mean time to restore** — median interval from incident-detect to
   incident-close over the last 90 days. (If the schema does not yet
   capture incidents, leave null with a "requires incident table"
   annotation.)

**Scope:** `gtkb-dashboard.json` additions (4 new panels + 4 new SQL
queries); optional `schema.sql` addition for an `incidents` table (stub,
populated by future work).

### E. Alert-routing skeleton (`provisioning/alerting/`)

**Current gap:** `provisioning/alerting/` exists but is empty. Industry norm
is at least one alert per red-signal panel (release blockers, failing CI,
stale data).

**Proposed change:** Add three minimal Grafana alert-rule YAML files
(release-blockers > 0, failing CI integrations > 0, data-freshness age >
60 minutes). Provisioned without a notifier (the owner can wire email /
Slack / Teams later); alerts fire to the Grafana alert list only for now.

**Scope:** 3 YAML files under `docs/gtkb-dashboard/grafana/provisioning/alerting/`.

---

## 3. Out of Scope (Slice 2/3 Follow-on Bridges)

Filed as separate follow-on bridges after this thread VERIFIED:

- **Slice 2 (`gtkb-dashboard-industry-alignment-slice2`)**:
  - Bridge state swimlane panel (visualize every open thread's latest
    status + age-in-state).
  - Work-subject selector (toggle Application vs GT-KB scope).
  - Coverage trend panel (line + branch, over time; groundtruth-kb already
    tracks this).
  - Security posture panel (open CVEs, Dependabot, pip-audit, Scout).
  - CI workflow embed (GitHub Actions latest run results).
  - Alert-routing notifier wiring (email / Slack / Teams).
- **Slice 3 (`gtkb-dashboard-industry-alignment-slice3`)**:
  - SLO / error-budget model + burn-rate alerts.
  - Flow metrics with WIP aging.
  - Branch / PR health panel.
  - Incident / on-call / MTTA / MTTR panel (requires `incidents` table
    schema).
  - Remote read-only dashboard exposure path (snapshot URL or auth gateway).
  - WCAG 2.1 AA accessibility audit (apply the same bar already gated in
    the app's CI).

§F — upstream GT-KB package integration for dashboard (`gtkb dashboard
install/start/stop` entrypoints per `PACKAGE-INTEGRATION.md`) — remains in
the upstream `groundtruth-kb` backlog, separate from this Agent Red bridge.

---

## 4. Implementation Sequence

1. (A) Rewrite `index.html` as progressive-enhancement landing.
2. (A) Verify the page in Chrome and Edge with Grafana down and with
   Grafana up. Screenshot evidence in post-impl report.
3. (B) Add retention logic to dashboard snapshot writer; trim existing
   `dashboard-data.json` to 7-day window in the same commit.
4. (B) Regression test for retention-at-boundary.
5. (C) Add `last_refreshed_at` column surfacing to ~10 Grafana stat panels.
6. (D) Add DORA four-keys row with computed queries; nulls with annotation
   where the schema does not yet support the metric.
7. (E) Add 3 stub alert-rule YAML files under `provisioning/alerting/`.
8. Run all tests; post-impl report with screenshots and before/after
   snapshot-size comparison.

Steps are independent; failure at any step does not block the others from
landing. Can be implemented in parallel commits.

---

## 5. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Landing page breaks when Grafana absent | Page renders, shows KPI snapshot + Open-live button, no blank/frozen state. |
| Landing page freshness badge wrong | Age bucket thresholds (green/yellow/red) verified against synthetic timestamps. |
| Retention trims too aggressively | Test asserts snapshots within retention window preserved exactly. |
| Retention fails to trim | Test asserts snapshots older than retention cutoff removed. |
| DORA denominator null (no events) | Panels show "—" not "NaN" or "0" when the underlying table is empty. |
| DORA change-failure-rate fabrication | Null + annotation when rollback tagging absent; does not silently compute a false 0%. |
| Per-panel freshness missing on a panel | Spot-check: every stat panel with a metric also shows a timestamp. |
| Alert YAML parse error | `promtool`-equivalent or Grafana provisioning validator in the test. |

---

## 6. Files Touched

**New:**
- `docs/gtkb-dashboard/grafana/provisioning/alerting/release-blockers.yaml`
- `docs/gtkb-dashboard/grafana/provisioning/alerting/failing-ci.yaml`
- `docs/gtkb-dashboard/grafana/provisioning/alerting/stale-data.yaml`
- `tests/scripts/test_gtkb_dashboard_retention.py` (new)

**Modified:**
- `docs/gtkb-dashboard/index.html` (rewrite)
- `docs/gtkb-dashboard/dashboard-data.json` (trim to 7-day window)
- `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` (add DORA row
  + per-panel freshness)
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` (retention logic)
- `memory/work_list.md` (add `GTKB-DASHBOARD-001` entry)

**Not touched:**
- `src/`, `tests/integrations/`, upstream `groundtruth-kb/`.
- `scripts/gtkb_dashboard/control_plane_registry.py`.
- Any Phase 7 bridge/work-subject code.

---

## 7. Out of Scope for This Bridge

- Any Slice 2 / Slice 3 items.
- Upstream `groundtruth-kb` package entrypoints (`gtkb dashboard …`).
- Production deployment. No `src/` changes; GOV-16 not triggered.

---

## 8. Decision Needed From Owner

None. Awaiting Loyal Opposition review.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
