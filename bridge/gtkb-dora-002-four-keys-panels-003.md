NEW

# Implementation Report - GTKB-DORA-002 DORA four-keys panels

bridge_kind: implementation_report
Document: gtkb-dora-002-four-keys-panels
Version: 003
Date: 2026-07-09 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d996d358-1413-4577-bc13-dbeac0ca82f9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless autonomous Prime Builder (keep-working-pb); resolved role prime-builder via durable registry

Project Authorization: PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-DASHBOARD-OBSERVABILITY
Work Item: GTKB-DORA-002

Responds-To: bridge/gtkb-dora-002-four-keys-panels-002.md (GO)
Implementation Commit: 70adc5f5

target_paths: ["scripts/gtkb_dashboard/refresh_dashboard_db.py", "scripts/gtkb_dashboard/generate_grafana_dashboard.py", "platform_tests/scripts/test_gtkb_dashboard_grafana.py", "platform_tests/scripts/test_dora_four_keys_panels.py", "docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implemented the DORA four-keys dashboard consumer of the DORA-001 telemetry
foundation, per the GO at `-002`. The refresh layer now computes four
`current_metrics` rows (deployment frequency, lead time for changes, change
failure rate, MTTR) from the authoritative `delivery_timeline_events` +
`incidents` telemetry, and the generator emits four Grafana stat panels in a new
collapsed "DORA Four Keys (Delivery Performance)" row appended after the TAFE
Observability row. Insufficient telemetry renders null/annotated states rather
than fabricated values (`GOV-SESSION-SELF-INITIALIZATION-001`).

Scope was held strictly to the five GO'd `target_paths`. Local commit
`70adc5f5` contains exactly those five files (847 insertions, 0 deletions; no
unrelated worktree changes captured — committed via pathspec-limited
`git commit -- <paths>`).

## Changes By File

- `scripts/gtkb_dashboard/refresh_dashboard_db.py` — added `_dora_deployment_frequency`,
  `_dora_change_failure_rate`, `_dora_mttr_hours`, and `_dora_four_keys_metric_rows`
  (reusing the DORA-001 `_DORA_DEPLOYMENT_EVENT_KINDS` / `_is_deployment_event`
  contract and `_timestamp_unix`); wired a second `current_metrics` insert after
  `_ingest_canonical_pipeline_manifests` so the metrics derive from authoritative
  post-ingestion deploy rows.
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py` — added
  `_DORA_INFORMATIONAL_THRESHOLDS`, `_dora_four_keys_panels`, and an appended
  collapsed "DORA Four Keys (Delivery Performance)" row (y=74). Appended (not
  inserted) so the existing top-of-dashboard panel order and the strict
  `panels[:10]` / `panels[1:13]` test pins are unchanged. Panels carry the
  standard freshness secondary target `F` like every other value stat panel.
- `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` — regenerated
  (purely additive: +454 lines; no reorder/deletion of existing panels).
- `platform_tests/scripts/test_dora_four_keys_panels.py` — new suite: null-when-no-
  telemetry, computed-from-seeded-telemetry, zero-failure-rate, and generator
  panel presence/datasource/query assertions.
- `platform_tests/scripts/test_gtkb_dashboard_grafana.py` — extended the
  provisioning test to pin the four DORA panel titles + SQLite datasource + per-panel
  `current_metrics` query from the generated JSON file.

## Metric Definitions (honest, telemetry-bounded)

- **Deployment Frequency** — count of authoritative `canonical_deploy` events in
  the retained delivery timeline; `NULL` when no deployment telemetry exists.
- **Lead Time for Changes** — `NULL`/annotated: the DORA-001 foundation persists
  commit SHAs (`commit_range_start`/`commit_range_end`) but not per-commit
  authored timestamps, so lead time is not yet computable. Emitted null with an
  explanatory annotation rather than a fabricated value.
- **Change Failure Rate (%)** — percent of distinct deployed `deployable_change_id`
  values linked to a rollback, hotfix, or caused incident; `NULL` when no
  attributable deployment telemetry exists.
- **MTTR (h)** — mean hours from incident detection to mitigation (falls back to
  closure); `NULL` when no resolved incidents exist.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH did not bypass GO or implementation-start; a live impl-start packet was created from the GO.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-governed implementation flow preserved.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project linkage metadata carried above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete spec links carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test evidence below.
- `GOV-SESSION-SELF-INITIALIZATION-001` — insufficient telemetry renders null/annotated, never fabricated metrics (asserted by tests).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — dashboard evidence and test outputs are governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory specs cited to close the `-002` P3 advisory-linkage gap.

## Specification-Derived Verification (Spec-to-Test Mapping)

| Specification | Test / command | Result |
| --- | --- | --- |
| `GOV-SESSION-SELF-INITIALIZATION-001` (no fabricated telemetry) | `test_dora_four_keys_panels.py::test_dora_rows_null_when_no_telemetry` — all four keys null + yellow + annotated when tables empty. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (metrics compute correctly) | `test_dora_four_keys_panels.py::test_dora_metrics_computed_from_seeded_telemetry` — deployment_frequency=3, change_failure_rate=66.7, mttr=3.0, lead_time null; `::test_change_failure_rate_zero_when_no_failures`. | PASS |
| Grafana panels exist + pin titles/datasource | `test_dora_four_keys_panels.py::test_generated_dashboard_exposes_dora_four_keys_panels`; `test_gtkb_dashboard_grafana.py::test_grafana_provisioning_targets_sqlite_database` (pins the four titles + `frser-sqlite-datasource` + `current_metrics` queries). | PASS |
| No regression of existing dashboard behavior | `test_gtkb_dashboard_grafana.py` full suite incl. strict `panels[:10]`/`panels[1:13]` order + per-panel freshness secondary target. | PASS |

Command evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dora_four_keys_panels.py platform_tests/scripts/test_gtkb_dashboard_grafana.py -q
# => 29 passed

groundtruth-kb/.venv/Scripts/python.exe -m ruff check <4 changed .py>
# => All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <4 changed .py>
# => 4 files already formatted
```

Note: the `-002` GO required BOTH `ruff check` AND `ruff format --check`; both were run and are green.

## Acceptance Criteria Check

- Four stat panels for deployment frequency, lead time, change failure rate, MTTR — DONE (collapsed "DORA Four Keys" row).
- Seeded refresh tests verify each metric's computed shape — DONE.
- Grafana JSON tests pin the four panel titles + data sources — DONE.
- Insufficient telemetry displays null/annotated states, not fabricated values — DONE (null-telemetry test + lead-time null-by-design).

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` — dashboard observability batch approval.
- `DELIB-20265586` — snapshot-bound dashboard-observability implementation authorization (this PAUTH's owner decision).
- DORA-001 foundation of record: `bridge/gtkb-dora-001b-track2-implementation-003.md`, `bridge/gtkb-dora-001b-authoritative-deployment-source-005.md` (the `canonical_deploy` telemetry this consumer reads). Note: the `gtkb-dora-telemetry-foundation` thread is WITHDRAWN (superseded by the dora-001b threads); the foundation is genuinely present in `refresh_dashboard_db.py`.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BOUNDED-IMPLEMENTATION-2026-06-23` (owner decision `DELIB-20265586`) — active authorization covering `GTKB-DORA-002`. No new owner decision was required for this implementation; scope was fully covered by the existing PAUTH and the `-002` GO.

## Recommended Commit Type

Recommended commit type: feat — new dashboard capability (four DORA-keys metrics + panels). Commit `70adc5f5` used this type.

## Risk / Rollback

Low. Additive only; existing panels/tests unchanged. Lead-time null-by-design is documented and asserted. Rollback = single-commit revert of `70adc5f5`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
