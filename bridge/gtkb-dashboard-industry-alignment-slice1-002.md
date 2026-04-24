NO-GO

# Loyal Opposition Review - GTKB Dashboard Industry Alignment Slice 1

**Date:** 2026-04-23
**Document:** `gtkb-dashboard-industry-alignment-slice1`
**Reviewed file:** `bridge/gtkb-dashboard-industry-alignment-slice1-001.md`
**Verdict:** NO-GO

## Rationale

Items A and E are grounded in the current repo state, but the bridge as written
bundles them with two incorrect assumptions:

1. the retention work is aimed at the wrong artifact; and
2. the DORA row is not supportable from the current delivery-event data model.

The Grafana panel work is also scoped against a generated JSON artifact instead
of the generator and tests that own it. Approving the slice as written would
send implementation into the wrong files and produce misleading metrics.

## Findings

### 1. Slice 1B targets the wrong retention owner

**Proposal claim:** `docs/gtkb-dashboard/dashboard-data.json` is the append-only
3-minute snapshot log that needs a 7-day retention policy.

**Evidence:**

- `scripts/session_self_initialization.py:64` sets
  `DEFAULT_HISTORY_PATH = PROJECT_ROOT / "memory" / "gtkb-dashboard-history.json"`.
- `scripts/session_self_initialization.py:70` sets `MAX_HISTORY = 200`.
- `scripts/session_self_initialization.py:4658-4664` writes
  `docs/gtkb-dashboard/dashboard-data.json` from
  `data = {"model": model, "history": history}` via `json.dumps(...)`; it is a
  regenerated composite output, not the authoritative append-only history file.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py:346-349` bounds history with
  `_append_snapshot(..., max_history=200)` and returns `filtered[-max_history:]`.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py:370` clears `kpi_snapshots`
  before re-inserting them, and `scripts/gtkb_dashboard/refresh_dashboard_db.py:539`
  repopulates from the bounded history rows.
- Live workspace check: `docs/gtkb-dashboard/dashboard-data.json` is currently
  322,701 bytes / 7,554 lines, but the file begins as a single JSON object with
  top-level `history` and `model` keys rather than an append-only ledger.

**Risk / impact:** A retention change implemented in
`scripts/gtkb_dashboard/refresh_dashboard_db.py` against
`docs/gtkb-dashboard/dashboard-data.json` will not necessarily affect the real
history owner and can create contradictory retention behavior between startup
generation and SQLite refresh.

**Required action:** Revise Slice 1B to identify one authoritative retention
path. If the goal is to bound dashboard history, scope the change around
`memory/gtkb-dashboard-history.json` / the startup history generator and then
state how SQLite refresh consumes that bounded set.

### 2. Slice 1C/1D propose editing a generated Grafana artifact

**Proposal claim:** modify `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json`
for per-panel freshness and DORA panels.

**Evidence:**

- `scripts/gtkb_dashboard/generate_grafana_dashboard.py:11` defines
  `DASHBOARD_PATH` as the JSON file under `docs/gtkb-dashboard/grafana/dashboards/`.
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py:298` builds the
  dashboard in code.
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py:731-734` writes the
  generated JSON to disk.
- `tests/scripts/test_gtkb_dashboard_grafana.py:138-182` asserts the current
  panel ordering and panel types from the generated dashboard JSON.

**Risk / impact:** Editing the JSON file directly is not durable. The next
generator run or test refresh will drift or overwrite the manual JSON edits.

**Required action:** Route all Grafana panel work through
`scripts/gtkb_dashboard/generate_grafana_dashboard.py` and update the pinned
dashboard tests in the same bridge revision.

### 3. Slice 1D overstates current DORA-readiness

**Proposal claim:** `delivery_timeline_events` already contains the raw inputs
needed for the DORA four keys.

**Evidence:**

- `scripts/gtkb_dashboard/schema.sql:58-73` defines
  `delivery_timeline_events`; there is no current `incidents` table in that
  schema.
- Live SQLite query against `memory/gtkb-dashboard.sqlite`:
  - `delivery_timeline_events_count = 101`
  - `production_count = 3`
  - `production_with_commit = 0`
  - `rollback_events = 1`
  - `hotfix_events = 0`
  - `incident_table_exists = 0`
- The recent production rows are:
  - `('production_deployment', 'api-gateway-restore.yaml', ..., 'v1.14.0', '', 'configured')`
  - `('production_deployment', 'upgrade.ps1', ..., 'v1.26.0', '', 'configured')`
  - `('production_deployment', 'rollback.ps1', ..., 'v1.12.0, v1.25.1', '', 'configured')`

**Risk / impact:** Lead time, change failure rate, and MTTR are not derivable
from the current data without fabricating semantics. Even deployment frequency
is ambiguous because restore/rollback/config artifacts are mixed into the same
stage.

**Required action:** Remove DORA item D from this slice, or first propose the
explicit telemetry/data-model work needed to capture deployable change identity,
rollback or hotfix linkage, and incidents.

## Conditions For GO

1. Keep the clearly supported items in the revised bridge: the progressive
   landing page (A), the alert-routing skeleton (E), and optionally per-panel
   freshness (C) if it is routed through the generator.
2. Re-scope retention around the actual history owner and name the exact file,
   function, and test changes.
3. Move DORA Four Keys to a follow-on bridge unless the revision first adds the
   missing data contract and storage plan.

## Decision Needed From Owner

None. Revise and resubmit through the bridge.
