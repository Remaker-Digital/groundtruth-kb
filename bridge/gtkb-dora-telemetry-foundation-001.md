NEW

# GTKB-DORA-001 — DORA Telemetry Foundation

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-DORA-001
**Author:** Prime Builder (Claude Opus 4.7, S307)

bridge_kind: proposal
work_item_ids: [GTKB-DORA-001]
spec_ids: []
target_project: agent-red
target_paths: ["scripts/gtkb_dashboard/schema.sql", "scripts/gtkb_dashboard/refresh_dashboard_db.py", "tests/scripts/test_gtkb_dashboard_dora_telemetry.py"]
implementation_scope: dashboard
requires_review: true
requires_verification: true

---

## Prior Deliberations

- `bridge/gtkb-dashboard-industry-alignment-slice1-002.md:82-110` — NO-GO Finding 3 that motivated this WI: live DB had 101 total events, 3 production rows, 0 with commit linkage, 1 rollback event, 0 hotfix events, no incidents table. Lead time, change failure rate, and MTTR not derivable from current schema.
- `bridge/gtkb-dashboard-industry-alignment-slice1-001.md:160-161` — DORA four keys explicitly out of scope for Slice 1; filed as `gtkb-dora-telemetry-foundation` follow-on.
- `memory/work_list.md:445-464` — backlog entry defining the WI scope (schema + linkage + ingest + backfill).
- `bridge/gtkb-dashboard-industry-alignment-slice2-001.md:93-97` — Slice 2 scoping proposal explicitly names DORA-001 as the prerequisite for any honest DORA panel (`GTKB-DORA-002`).
- No prior deliberations found searching `DORA telemetry` or `deployable_change` — this is the first review pass on the schema.

---

## 1. Problem Statement

The dashboard cannot compute the DORA four keys (deployment frequency, lead time for changes, change failure rate, mean time to restore) from the current schema. Live-DB evidence from Slice 1 NO-GO Finding 3:

- `delivery_timeline_events` has 101 rows, 3 production deployments, all with empty `commit_sha`.
- The three production deployments include a restore (`api-gateway-restore.yaml`), an upgrade (`upgrade.ps1`), and a rollback (`rollback.ps1`) — the stage is mixed, so even deployment frequency is ambiguous.
- There is no `incidents` table, no incident-to-deploy linkage, and no hotfix linkage.

Without a data model that distinguishes deployable changes, rollbacks, hotfixes, and incidents, any DORA panel would fabricate semantics. This foundation lands the data model first; `GTKB-DORA-002` consumes it later to compute the four keys honestly.

---

## 2. Scope

### 2.1 Schema additions (`scripts/gtkb_dashboard/schema.sql`)

**New columns on `delivery_timeline_events`:**

| Column | Type | Constraint | Meaning |
|---|---|---|---|
| `deployable_change_id` | TEXT | NOT NULL DEFAULT '' | Stable identity of the change shipping. For production events, a monotonic string like `<commit_sha_short>-<deploy_timestamp_unix>`; empty for non-deploy events. |
| `commit_range_start` | TEXT | NOT NULL DEFAULT '' | SHA of the first commit included in this change (inclusive). |
| `commit_range_end` | TEXT | NOT NULL DEFAULT '' | SHA of the last commit included in this change (inclusive). For a single-commit change, equal to `commit_range_start`. |
| `rollback_of_deploy_id` | TEXT | NOT NULL DEFAULT '' | `deployable_change_id` of the deployment this rollback reverses. Empty for non-rollback events. |
| `hotfix_of_deploy_id` | TEXT | NOT NULL DEFAULT '' | `deployable_change_id` of the deployment this hotfix patches. Empty for non-hotfix events. |
| `event_kind` | TEXT | NOT NULL DEFAULT 'change' | One of: `change`, `rollback`, `hotfix`, `restore`, `config`. Disambiguates the current mixed-stage mess. |

Rationale for all defaults empty/`'change'`: the refresh pipeline currently inserts via positional arguments; adding NOT-NULL-with-default columns keeps backward compatibility with the existing INSERT call at `refresh_dashboard_db.py:450`. Phase 1 implementation updates the INSERT to include the new columns explicitly; Phase 0 of the implementation bridge is a no-op schema migration that does not require a data rewrite.

**New table `incidents`:**

```sql
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    caused_by_deploy_id TEXT NOT NULL DEFAULT '',
    detected_at TEXT NOT NULL,
    mitigated_at TEXT,
    closed_at TEXT,
    description TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL
);
```

`caused_by_deploy_id` references `delivery_timeline_events.deployable_change_id` (FK enforcement deferred — SQLite, and the refresh pipeline rebuilds tables via `_replace_table()` at `refresh_dashboard_db.py:365`). `mitigated_at` / `closed_at` nullable because an open incident has neither. `severity` drawn from `{SEV1, SEV2, SEV3, SEV4}` (convention; not enforced at schema).

### 2.2 Refresh-pipeline ingest (`refresh_dashboard_db.py`)

**Insert signature change:** the existing `INSERT INTO delivery_timeline_events (...)` at `:450` is extended with the six new columns. Values are sourced as follows:

- `deployable_change_id`:
  - For events whose `stage == 'production_deployment'`: generated as `<commit_sha[:8]>-<unix_timestamp>` when `commit_sha` is non-empty; otherwise `'unlinked-<source>-<event_id>'` as a fallback that is clearly detectable by `GTKB-DORA-002` consumers.
  - For non-production events: empty string.
- `commit_range_start` / `commit_range_end`: initially equal to `commit_sha` for single-commit events. Multi-commit range parsing is a future refinement (explicit non-goal — see §4).
- `rollback_of_deploy_id`: parsed from `event` / `source` fields when the event is recognized as a rollback (heuristic table in §2.2a). Empty if unknown.
- `hotfix_of_deploy_id`: same heuristic applied to hotfix events.
- `event_kind`: classified per §2.2a.

**§2.2a — Event-kind classification heuristics:**

| Condition | `event_kind` |
|---|---|
| `event` contains `rollback` (case-insensitive) | `rollback` |
| `event` contains `hotfix` | `hotfix` |
| `event` contains `restore` | `restore` |
| `source` ends in `.yaml` and `event` starts with `apply_` | `config` |
| Otherwise | `change` |

These are deliberately simple; refinement lands as separate WIs if classifiers drift. The classifier is a single function in `refresh_dashboard_db.py` that is unit-tested fixture-by-fixture (§6).

**New `incidents` ingest:** the refresh pipeline gains a new `_load_incidents()` step that reads a declarative source (§2.3) and rebuilds the `incidents` table via `_replace_table()`. If the source is absent or empty, the table is rebuilt empty — no rows, no errors.

### 2.3 Incident data source

For this foundation slice, `incidents` ingest reads a declarative YAML file at `memory/incidents.yaml` with the schema:

```yaml
incidents:
  - incident_id: "INC-2026-04-22-01"
    title: "ACS SMS delivery delays"
    severity: "SEV3"
    caused_by_deploy_id: ""           # empty if unknown or not caused by a deploy
    detected_at: "2026-04-22T14:03:00Z"
    mitigated_at: "2026-04-22T16:41:00Z"
    closed_at: "2026-04-23T09:10:00Z"
    description: "Optional."
    source: "manual"
```

Rationale for YAML-first vs an external ingest (PagerDuty / Opsgenie / GitHub incidents):

- Current repo has zero production incidents tracked anywhere machine-readable.
- YAML lets the owner begin recording incidents retroactively without first selecting / provisioning an incident-management service.
- Swapping to an external source later is a `_load_incidents()` internal refactor, not a schema change.

The file is owner-maintained; the refresh pipeline treats it as read-only input.

### 2.4 Backfill

Two backfill passes, both idempotent and both invoked once on the first refresh after schema migration:

- **Production-deploy backfill:** for existing `production_deployment` rows, classify via §2.2a heuristics and populate `event_kind` + `deployable_change_id` where possible. Rows whose `commit_sha` is empty get the `unlinked-<source>-<event_id>` fallback so that DORA-002 consumers can compute counts without silent joins.
- **Rollback linkage backfill:** when a rollback event is adjacent (within 7 days) to a prior non-rollback production deploy of the same major version, set `rollback_of_deploy_id` to the earlier deploy's `deployable_change_id`. Heuristic, but clearly-bounded; marked in the new column as such via a `_backfill_heuristic_applied` companion column only if Codex requires.

Owner decision point if Codex requires backfill-heuristic-marker: see §8.

---

## 3. What This Slice Does NOT Deliver

- **No DORA panels, no four-key computation.** That is `GTKB-DORA-002` — strictly after this slice is VERIFIED.
- **No UI changes.** Dashboard landing page, Grafana dashboards, and alerts all unchanged.
- **No incident-management tool integration.** YAML file only. Future follow-ons can ingest PagerDuty / Opsgenie / GitHub.
- **No schema for lead-time-in-review** (PR open → merge time) — that is Slice 3 flow-metrics territory per `GTKB-DASHBOARD-003`.
- **No multi-commit range parsing** (`commit_range_start` / `commit_range_end` seeded with `commit_sha` only). Future refinement WI.
- **No retrospective incident population.** YAML starts empty; owner or follow-on tooling populates.

---

## 4. Files Touched

**New:**
- `tests/scripts/test_gtkb_dashboard_dora_telemetry.py` — schema migration, classifier, backfill, incident ingest fixtures.

**Modified:**
- `scripts/gtkb_dashboard/schema.sql` — 6 new columns on `delivery_timeline_events` + new `incidents` table.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` — extended INSERT; new `_classify_event_kind()`; new `_load_incidents()`; backfill passes.
- `memory/work_list.md` — `GTKB-DORA-001` entry updated: DONE pending VERIFIED; `GTKB-DORA-002` unblocks.

**New (optional, owner-maintained):**
- `memory/incidents.yaml` — created empty at first refresh; owner populates retroactively.

**Not touched:**
- `docs/gtkb-dashboard/**` — no UI changes.
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py` — no new panels.
- `src/**` — no application code.
- Production deployment — GOV-16 not triggered.

---

## 5. Implementation Sequence

**Phase 0 — Baseline sanity (no code change)**

1. Confirm Slice 1 baseline green:
   - `python -m pytest tests/scripts/test_gtkb_dashboard_alerting.py tests/scripts/test_gtkb_dashboard_grafana.py -q` → expect all pass.

**Phase 1 — Schema migration**

2. Add six new columns to `delivery_timeline_events` DDL + new `incidents` table in `schema.sql`.
3. Extend the existing migration smoke test (or add one) that loads an older schema copy and applies the new DDL; asserts columns present and `incidents` table created.

**Phase 2 — Refresh pipeline**

4. Add `_classify_event_kind(event, source)` pure function.
5. Extend INSERT at `refresh_dashboard_db.py:450` with the six new column values.
6. Add `_load_incidents()` step; wire into the refresh loop.
7. Add backfill passes (production-deploy classifier + rollback linkage).

**Phase 3 — Tests**

8. `tests/scripts/test_gtkb_dashboard_dora_telemetry.py`:
   - Schema columns present.
   - Classifier: 8 fixture cases covering each `event_kind`.
   - `deployable_change_id` generation: commit_sha present / absent cases.
   - Incident ingest: empty / absent / populated / malformed YAML (last raises `IncidentIngestError`).
   - Backfill idempotency: running refresh twice produces the same linkage.
   - Rollback-linkage heuristic: 3 fixtures (valid match, no match within 7 days, multiple candidates → most recent wins).

**Phase 4 — Verify and report**

9. Run all affected lanes:
   - `python -m pytest tests/scripts/test_gtkb_dashboard_dora_telemetry.py -q`
   - `python -m pytest tests/scripts/test_gtkb_dashboard_grafana.py -q`
   - `python -m pytest tests/scripts/test_gtkb_dashboard_alerting.py -q`
10. All three lanes must be green before filing post-impl report.
11. Refresh the live dashboard DB and inspect: `production_deployment` rows now have non-empty `event_kind` and `deployable_change_id`; `incidents` table exists (empty OK).
12. Post-implementation report filed; Loyal Opposition reviews for VERIFIED.

---

## 6. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Schema columns added with wrong types or missing defaults | DDL inspection test; `PRAGMA table_info('delivery_timeline_events')` returns the 6 new columns with correct types and defaults. |
| `incidents` table missing or wrong shape | DDL inspection; `PRAGMA table_info('incidents')` matches §2.1. |
| INSERT statement drift (positional args misaligned) | Test loads fixture events into a temp DB and round-trips all 22 columns (16 original + 6 new). |
| Classifier misclassification | Classifier called on 8 fixtures (one per `event_kind` branch + two ambiguous); asserts expected labels. |
| `deployable_change_id` non-deterministic | Same `(commit_sha, timestamp)` inputs produce identical IDs across runs. |
| `deployable_change_id` empty `commit_sha` fallback | `commit_sha == ''` → `deployable_change_id` starts with `'unlinked-'`. |
| Rollback-linkage heuristic wrong | 3 fixtures cover valid match, out-of-window, multiple candidates. |
| Incident YAML absent | `_load_incidents()` called with missing path → rebuilds table empty, no error. |
| Incident YAML malformed | Invalid YAML → `IncidentIngestError` raised with file+line context. |
| Incident ingest populates | 2 valid rows in YAML → 2 rows in `incidents` table after refresh. |
| Backfill idempotency | Run refresh twice, compare `deployable_change_id` column before/after second run → identical. |
| Backfill does not break Slice 1 | Slice 1 tests stay green after schema + ingest changes. |
| FK integrity check (advisory) | Incident with `caused_by_deploy_id` referencing nonexistent deploy ID → not blocked (SQLite no FK enforcement), but ingest logs warning (optional, see §8). |
| `event_kind` coverage on live data after refresh | Post-refresh, every `production_deployment` row has non-empty `event_kind`. |
| DORA-002 consumer-readiness | Fixture-level assertion: given a seeded set of events + incidents, the computable inputs to all four DORA keys (deploys/day, lead time samples, failure linkage pairs, detect-to-close durations) are present and non-null. |

---

## 7. Open Questions for Loyal Opposition Review

1. **Rollback-linkage heuristic** (7-day adjacency, same major version). Overly permissive? Overly restrictive? Alternative: require explicit `rollback_of_deploy_id` in the ingest source and reject implicit linkage. I chose the 7-day heuristic to unblock `GTKB-DORA-002` on current live data; if Codex prefers strict, I'll drop the heuristic and leave the column empty until an explicit source populates it.
2. **`_backfill_heuristic_applied` companion column.** Do we need to mark heuristically-derived linkages so DORA-002 can surface confidence? I omitted it to keep the schema narrow. Codex to accept or require.
3. **Incident source format — YAML vs SQLite staging table.** YAML is owner-friendly; a staging table would be more testable. I chose YAML for lower friction; Codex to accept.
4. **Incident ingest on refresh vs one-shot CLI.** Currently proposed as part of the refresh pipeline (runs every refresh). Alternative: a separate `scripts/gtkb_dashboard/load_incidents.py` invoked manually. Codex to accept or redirect.
5. **`event_kind` enum enforcement.** Currently schema-level `TEXT`; could be `CHECK (event_kind IN (...))`. SQLite honors CHECK constraints. Preferred if Codex wants stronger invariants.
6. **`commit_range_start` / `commit_range_end` single-commit seeding.** I seed both equal to `commit_sha`. Alternative: leave both empty until multi-commit parsing lands. I chose seeding to avoid breaking DORA-002's lead-time math on single-commit deploys. Codex to accept.

---

## 8. Decision Needed From Owner

None in this bridge. The rollback-linkage heuristic, `_backfill_heuristic_applied` column, and incident-source format are Codex review decisions (§7). The `memory/incidents.yaml` population is owner-initiated post-VERIFIED and non-blocking.

---

## 9. Out of Scope

- DORA four-key panels — `GTKB-DORA-002` after this slice VERIFIED.
- SLO / error budgets — `GTKB-DASHBOARD-003`.
- Flow metrics, PR/branch health, MTTA — `GTKB-DASHBOARD-003`.
- External incident-management integration (PagerDuty, Opsgenie, GitHub) — future follow-on.
- Multi-commit range parsing — future follow-on.
- Upstream `groundtruth-kb` DORA work — separate track.
- `src/` changes. Production deployment. GOV-16 not triggered.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
