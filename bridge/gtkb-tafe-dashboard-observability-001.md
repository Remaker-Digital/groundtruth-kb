NEW

# WI-4506: TAFE Dashboard Observability Panels (read-only Grafana visualization)

bridge_kind: prime_proposal
Document: gtkb-tafe-dashboard-observability
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 869ade5b-58a4-4261-b2cb-98fcbecb8c0e
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE-WI-4504-4505-4506-4507-4511-CUTOVER-EXCLUDED
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4506

target_paths: ["scripts/gtkb_dashboard/generate_grafana_dashboard.py", "scripts/gtkb_dashboard/refresh_dashboard_db.py", "docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json", "platform_tests/scripts/test_gtkb_dashboard_grafana.py", "platform_tests/scripts/test_tafe_dashboard_refresh.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

---

## Summary

Implement WI-4506, the TAFE observability panel surface on the GT-KB Grafana dashboard. Add a "TAFE Observability" section to the generated dashboard with read-only panels surfacing the now-VERIFIED TAFE telemetry/runtime substrate (WI-4504 `stage_attempt_telemetry`, WI-4488 `flow_instances`/`stage_instances`, WI-4492 `stage_leases`, WI-4497 `agent_capability_snapshots`). Two-layer slice:

1. **Data export layer.** Extend the dashboard refresh pipeline (`scripts/gtkb_dashboard/refresh_dashboard_db.py`) to project the relevant TAFE tables from canonical `groundtruth.db` into the dashboard's `memory/gtkb-dashboard.sqlite` (the `gtkb-dashboard-sqlite` Grafana datasource), so the new panels have data to read.
2. **Panel layer.** Extend the dashboard generator (`scripts/gtkb_dashboard/generate_grafana_dashboard.py`) with a TAFE Observability row and ~5 panels (outcome distribution, failure-class breakdown, active flow instances, active stage leases, capability-snapshot readiness) reading the projected tables via the existing SQLite datasource.

Output: the regenerated `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` containing the new TAFE Observability section. This is the same pattern the VERIFIED dashboard generator already follows for the 32 existing panels (install/setup, action center, delivery timeline, release readiness, KPI history).

### Bounding (explicit out-of-scope)

This slice is bounded to **read-only visualization wiring** of already-VERIFIED TAFE state. It MUST NOT:

- Add **alert rules**, alert routing, or notification policy. Alerts are a separate concern (`docs/gtkb-dashboard/grafana/provisioning/alerting/` is out of scope here); a future slice can promote selected panels.
- Add **autonomous recovery actuation**, dispatch behavior, lease mutation, or flow mutation. This slice does not consume the WI-4505 stuck detector to **act**; it only **surfaces** the underlying telemetry/runtime state for the operator's eyes. WI-4505's findings are an in-flight, separately-VERIFIED surface and are not consumed here.
- Add **live metric capture**, in-product aggregation/rollup services, KPI calculation in the GT-KB source tree, or a metrics-collector daemon. SQL aggregates in the panel queries are computed inside Grafana by the SQLite datasource at render time; no aggregation lands in product code.
- Change **bridge authority**, perform a **cutover**, create a **dual-write** path, expand **pilot eligibility**, or introduce an **authoritative generated view**. The dashboard is and remains an advisory observability surface; `bridge/INDEX.md` and root `groundtruth.db` remain canonical per `GOV-FILE-BRIDGE-AUTHORITY-001` and `SPEC-TAFE-R7`. The PAUTH explicitly forbids `cutover`, `dual_write`, `live_dispatch_substrate`, `authoritative_generated_view`, and `kb_schema_change`; this slice respects all five.
- Change **TAFE schema** (no DDL against `groundtruth.db`). The dashboard SQLite schema gains TAFE-projection tables via the existing `_migrate_schema` path; this is a dashboard-internal schema, not the canonical TAFE schema.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — TAFE state must be observable; this slice adds the observability surface without changing canonical authority.
- `SPEC-TAFE-R6` — per-stage-attempt telemetry now exists (WI-4504 VERIFIED) and must be visible to operators; the outcome/failure-class panels render this directly.
- `SPEC-TAFE-R3` — failure classes recorded in telemetry are surfaced for visual diagnosis. The slice surfaces; it does not auto-diagnose or auto-recover (that is WI-4505, separately).
- `SPEC-TAFE-R4` — dispatch policy state (capability snapshots, WI-4497) is read to surface dispatch-readiness for visual inspection; this slice does not invoke the engine.
- `SPEC-TAFE-R2` — stage-lease state (WI-4492) is read for visualization; the lease-status panel surfaces single-claim contention context. No lease is created or mutated.
- `SPEC-TAFE-R7` — MemBase remains canonical for TAFE state; the dashboard reads via a projection into the dashboard SQLite and writes nothing back to `groundtruth.db`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this slice writes nothing to the live `bridge/INDEX.md`, and the dashboard surface is not authoritative.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — PAUTH, project, work item, target paths, and governing specs/rules are concretely linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable project-authorization metadata is present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps the TAFE export, panel generation, no-alert-rule guard, and the non-authoritative bound to executed tests.
- `GOV-STANDING-BACKLOG-001` — WI-4506 is the backlog authority for this slice; WI-4507 (compatibility-view generator, also tranche-3-authorized) remains a separate sibling and the cutover items (WI-4508/4509/4510) are explicitly excluded by the PAUTH.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds under the active bounded tranche-3 PAUTH (which explicitly includes WI-4506) plus the forthcoming Loyal Opposition GO and implementation-start packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all source, test, and regenerated dashboard JSON targets are inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the dashboard panel surface is durable governed artifact state with a preserved evidence trail; WI-4506 stays unresolved until terminal VERIFIED.

## Prior Deliberations

<!-- Reviewed and pruned by author. -->

- `DELIB-20263164` — owner decision backing the tranche-3 PAUTH that explicitly includes WI-4506.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` — owner approval promoting the TAFE R-specs (R2/R3/R4/R6/R7) to `specified`; this slice surfaces state defined by those specs.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` — owner choice of the TAFE overhaul direction that produced the R-specs the panels visualize.
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` — VERIFIED WI-4488 (`flow_instances` + `stage_instances` + `flow_events` + `flow_artifacts`); the runtime substrate the active-flow + active-stage panels read.
- `bridge/gtkb-tafe-stage-leases-schema-004.md` — VERIFIED WI-4492 (`stage_leases`); the lease-status panel reads this surface.
- `bridge/gtkb-tafe-agent-capability-snapshots-schema-004.md` — VERIFIED WI-4497 (`agent_capability_snapshots`); the dispatch-readiness panel reads this surface.
- `bridge/gtkb-tafe-stage-attempt-telemetry-004.md` — VERIFIED WI-4504 (`stage_attempt_telemetry`); the outcome + failure-class panels read this surface.
- `bridge/gtkb-tafe-dispatch-policy-engine-006.md` — VERIFIED WI-4498 (dispatch policy engine, pure module). This slice does not invoke the engine; it surfaces the inputs (capability snapshots) and the recorded outputs (`dispatch_decision` JSON in telemetry) without computing live decisions.
- `bridge/gtkb-tafe-dispatch-tick-health-003.md` — in-flight WI-4499 (R5 dispatch-tick/health). This slice does not consume the tick; it visualizes the *underlying* state directly, so it does not race the WI-4499 implementation and is not blocked by it.
- `bridge/gtkb-tafe-stuck-flow-detection-002.md` — GO'd WI-4505 (R3 stuck-flow detector, claimed and in-flight). This slice surfaces the substrate the detector reasons over; WI-4505's structured findings are a separate surface and are intentionally not consumed here.
- No prior deliberations found specifically for TAFE dashboard metrics: `search_deliberations("TAFE dashboard metrics panels grafana observability WI-4506")` returned no matches on 2026-06-13. This is the first TAFE observability panel slice, not a revisit of a rejected approach.

## Owner Decisions / Input

No new owner decision is required to file or implement this proposal.

- **Implementation authority:** the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE-WI-4504-4505-4506-4507-4511-CUTOVER-EXCLUDED`, backed by owner decision `DELIB-20263164`, whose `scope_summary` explicitly authorizes "WI-4506 dashboard metrics" under GT-KB platform code/tests with `bridge/INDEX.md` canonical and no cutover. The PAUTH's `allowed_mutation_classes: ["source", "test"]` covers the generator/refresh source plus tests; the regenerated dashboard JSON is the deterministic source-derived output of the generator and is tracked alongside it (the same pattern the existing 32 panels follow). No `kb_schema_change` (the slice touches no `groundtruth.db` schema).
- **Work selection:** the owner directed the autonomous TAFE drive; WI-4506 is the next tranche-3 unblocked item now that WI-4504 has reached VERIFIED.
- No expanded authorization is requested. The forbidden-operation bounds (no cutover, no dual-write, no live dispatch substrate, no authoritative generated view, no KB schema change) are all respected; the no-alert-rule and no-authoritative-view bounds are enforced by structural tests.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TAFE-R6`/`R3`/`R4`/`R2` specify the telemetry/state to be surfaced; `SPEC-TAFE-R7` and `GOV-FILE-BRIDGE-AUTHORITY-001` keep MemBase + `bridge/INDEX.md` canonical and bound the dashboard to advisory observability; the tranche-3 PAUTH owner decision `DELIB-20263164` enumerates WI-4506 with "dashboard metrics" scope. No new or revised requirement is needed because this slice implements the specified observability surface as a read-only visualization layer over already-VERIFIED state and excludes alerts, recovery actuation, live capture, and any authority change.

## Implementation Plan

### Layer 1 — Data export (dashboard SQLite projection)

In `scripts/gtkb_dashboard/refresh_dashboard_db.py`:

1. **Extend `_migrate_schema`** to create five additive TAFE-projection tables in the dashboard SQLite (`memory/gtkb-dashboard.sqlite`): `tafe_stage_attempt_telemetry`, `tafe_flow_instances`, `tafe_stage_instances`, `tafe_stage_leases`, `tafe_agent_capability_snapshots`. Columns are a narrowed projection of the canonical tables — only the columns the panels need, all NULL-tolerant. No PK/FK to the canonical store; the dashboard SQLite is a derived read-only cache. (Forbidden `kb_schema_change` is to `groundtruth.db`, not the dashboard SQLite — the dashboard SQLite's own schema already evolves through `_migrate_schema` for every existing dashboard table.)
2. **Add a `_refresh_tafe_projection(conn, kb_db)` helper** that reads the latest-version rows from each canonical TAFE table via the `groundtruth_kb` Python API (no raw SQL against `groundtruth.db`) and inserts a narrowed projection into the dashboard tables. Invoked from `refresh_database()` after the existing GT-KB project/work-item refresh blocks. Uses the existing `_replace_table` pattern (truncate + insert). Read-only against `groundtruth.db`.
3. **Graceful absence:** when a TAFE table is absent from `groundtruth.db` (fresh-install / pre-TAFE adopters), the projection helper records zero rows and continues. The panels render "No data" — never an error. A structural test asserts this.

### Layer 2 — Panel generation (Grafana dashboard JSON)

In `scripts/gtkb_dashboard/generate_grafana_dashboard.py`:

4. **Add a `_tafe_observability_row` builder** producing a row header "TAFE Observability" followed by ~5 panels using the existing builders (`_pie_panel`, `_table_panel`, `_stat_panel`):
   - Stage attempt outcome distribution (pie over `tafe_stage_attempt_telemetry.outcome`).
   - Failure-class breakdown (pie/bargauge over `tafe_stage_attempt_telemetry.failure_class WHERE outcome != 'success'`).
   - Active flow instances by state (table over `tafe_flow_instances`).
   - Active stage leases by status (table over `tafe_stage_leases WHERE status='active'`).
   - Capability-snapshot readiness by role (bargauge over `tafe_agent_capability_snapshots WHERE status='active'`).
5. Add a section call from the dashboard composer that places the new row after the existing "Release Readiness" section (or another natural insertion point identified from the generator's layout helpers). Panel IDs come from the existing `PanelBuilder.next_id()` (no hand-coded ids, monotonic).
6. Regenerate `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json`; commit the regenerated JSON alongside the generator change. The JSON is deterministically derived from the generator; future regenerations are idempotent on unchanged inputs (existing generator invariant).

### Layer 3 — Tests

In `platform_tests/scripts/test_gtkb_dashboard_grafana.py`:

7. Add tests asserting: the regenerated dashboard contains a "TAFE Observability" row; the five panel titles are present; each TAFE panel's query references the corresponding projection table; the panels use the `gtkb-dashboard-sqlite` datasource (not raw `groundtruth.db`); no panel's query mutates (`INSERT|UPDATE|DELETE|DROP|CREATE` absent); **no alert rule references a TAFE panel** (structural guard against alert-rule scope creep); panel IDs are monotonically allocated (no duplicates).

New `platform_tests/scripts/test_tafe_dashboard_refresh.py`:

8. Tests against a temp dashboard SQLite + temp `groundtruth.db` with seeded TAFE rows: the migration creates the five projection tables; `_refresh_tafe_projection` populates row counts equal to the seeded canonical state; rerun is idempotent (counts unchanged); absent TAFE tables in `groundtruth.db` yield zero projected rows without error; the helper performs only reads against `groundtruth.db` (structural test asserts the module source contains no `INSERT|UPDATE|DELETE` against the canonical store and no MemBase mutating API call).

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
python -m pytest platform_tests/scripts/test_tafe_dashboard_refresh.py platform_tests/scripts/test_gtkb_dashboard_grafana.py -q --tb=short
Expected: pass; exercises the migration, TAFE projection (idempotence + graceful absence), the no-canonical-mutation structural guard, panel presence/queries/datasource, the no-alert-rule guard, and panel-id monotonicity.

python -m pytest platform_tests/scripts/test_dashboard_subject_selector.py platform_tests/scripts/test_gtkb_dashboard_alerting.py platform_tests/scripts/test_gtkb_dashboard_control_plane.py platform_tests/scripts/test_rehearse_dashboard_regen.py -q --tb=short
Expected: pass; regression on the rest of the dashboard surface, confirming the additive TAFE section does not break existing panels, alerts, control plane, or regen rehearsal.

python -m ruff check scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/gtkb_dashboard/refresh_dashboard_db.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_tafe_dashboard_refresh.py
python -m ruff format --check scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/gtkb_dashboard/refresh_dashboard_db.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_tafe_dashboard_refresh.py
Expected: pass.

python scripts/gtkb_dashboard/generate_grafana_dashboard.py
Expected: regenerates docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json; running twice produces byte-identical output (idempotent generation).

git diff --check -- scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/gtkb_dashboard/refresh_dashboard_db.py docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_tafe_dashboard_refresh.py
Expected: no output, exit 0.
```

Spec mapping:

- `SPEC-TAFE-R6` — outcome + failure-class panel tests prove WI-4504 telemetry is surfaced.
- `SPEC-TAFE-R2` — active-stage-leases panel test proves WI-4492 state is surfaced read-only.
- `SPEC-TAFE-R4` — capability-readiness panel test proves WI-4497 state is surfaced.
- `SPEC-TAFE-R7` — the refresh test asserts MemBase remains canonical (read-only against `groundtruth.db`; structural no-mutation guard).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — panel tests assert no panel writes `bridge/INDEX.md` or causes a side effect on the bridge; the dashboard is non-authoritative.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — each linked spec maps to executed test evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets under `E:\GT-KB`.

## Risk / Rollback

Primary risk is scope creep into alerts, recovery actuation, or live capture. Mitigation: the slice ships read-only visualization only; structural tests assert no `INSERT|UPDATE|DELETE` against `groundtruth.db` in the refresh helper, no alert rule references the new panels, and the panel queries use only the dashboard SQLite datasource.

Secondary risk is dashboard regression — adding 5 panels and a row could break layout or break the existing test suite. Mitigation: a regression pass runs the full dashboard test set (`test_gtkb_dashboard_grafana`, `test_dashboard_subject_selector`, `test_gtkb_dashboard_alerting`, `test_gtkb_dashboard_control_plane`, `test_rehearse_dashboard_regen`) on the changed tree; panel IDs use `PanelBuilder.next_id()` so insertion does not collide with existing IDs; row-grid placement appends after an existing row so layout is additive.

Tertiary risk is dashboard SQLite migration breakage on existing installs that already have a populated dashboard SQLite. Mitigation: the migration is additive (CREATE TABLE IF NOT EXISTS), idempotent across runs, and reuses the existing `_migrate_schema` framework.

Rollback is a single-commit revert of the generator, refresh, regenerated JSON, and the two test files. No KB mutation, no schema change to `groundtruth.db`, no integration to unwind.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of a new `gtkb-tafe-dashboard-observability` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`, and this slice changes no bridge-authority behavior.

## Recommended Commit Type

`feat:` — adds a new TAFE Observability section to the generated dashboard (data export wiring + ~5 panels) with comprehensive tests; no behavior change to existing panels, alerts, or control plane; no canonical schema change; no recovery actuation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
