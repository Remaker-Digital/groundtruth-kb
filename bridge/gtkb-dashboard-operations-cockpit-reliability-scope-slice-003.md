NEW

# WI-3433 implementation report — dashboard operations cockpit reliability and scope slice

bridge_kind: implementation_report
Document: gtkb-dashboard-operations-cockpit-reliability-scope-slice
Version: 003
Author: Prime Builder (Cursor, harness E)
Date: 2026-06-25 UTC
Responds to: bridge/gtkb-dashboard-operations-cockpit-reliability-scope-slice-002.md

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 3ea9c9d2-1790-4179-85d0-cc874bc68519
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Prime Builder; owner bridge-clearance loop; workspace E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-LO-ADVISORY-ROUTING
Work Item: WI-3433

target_paths: ["groundtruth-kb/src/groundtruth_kb/dashboard.py", "groundtruth-kb/src/groundtruth_kb/dashboard_service.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_dashboard.py", "scripts/gtkb_dashboard/refresh_dashboard_db.py", "scripts/gtkb_dashboard/generate_grafana_dashboard.py", "docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json", "platform_tests/scripts/test_gtkb_dashboard_grafana.py"]
implementation_scope: source,test_addition,cli_extension,scaffold_update
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Implementation Claim

Implemented the GO'd WI-3433 reliability/scope slice per `-001`/`-002`:

1. **Dynamic metric status colors** — `scripts/gtkb_dashboard/refresh_dashboard_db.py` adds `_metric_count_status()` and uses it in `_current_metric_rows()` so zero blockers/failures render `green` instead of hardcoded `red`.
2. **Combined subject scope metadata** — `_dashboard_subject_scope_label()` writes `dashboard_subject_scope`, `dashboard_subject_badge`, and `refresh_service_scope` into `dashboard_metadata` during refresh.
3. **Copyable local paths** — `groundtruth-kb/src/groundtruth_kb/dashboard.py` shortcut descriptions now say “Copy local path …”; Grafana Shortcuts panel link title is `Copy path` (not `Open`).
4. **Loopback/local-only + CLI-primary presentation** — `gt dashboard` group docstring, `dashboard start` echo lines, `dashboard_service` argparse description, and Grafana header text now emphasize loopback binding and `gt dashboard init|install|start|refresh` as the primary setup path.
5. **Regenerated** `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` from the updated generator.

## Specification Links

- `DELIB-20265873` — combined GT-KB + adopter scope badges/metadata.
- `DELIB-20265874` — copyable local path affordances.
- `DELIB-20265875` — loopback/local-only refresh presentation.
- `DELIB-20265876` — `gt dashboard` as primary visible setup path.
- `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` — bridge/governance counter semantics preserved; governance bridge items stay yellow when actionable > 0.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — metric statuses derive from refreshed intelligence payload, not static red defaults.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — combined surface labels platform + named adopter when `current_work_subject` is present.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — bridge GO + PAUTH implementation.

## Prior Deliberations

- `bridge/gtkb-dashboard-operations-cockpit-reliability-scope-slice-001.md` — proposal.
- `bridge/gtkb-dashboard-operations-cockpit-reliability-scope-slice-002.md` — GO.
- Advisory disposition chain cited in `-001`.

## Files Changed

| Path | Change |
|------|--------|
| `scripts/gtkb_dashboard/refresh_dashboard_db.py` | `_metric_count_status`, `_dashboard_subject_scope_label`, dynamic statuses, metadata keys |
| `scripts/gtkb_dashboard/generate_grafana_dashboard.py` | Header copy; Shortcuts `Copy path` link title |
| `groundtruth-kb/src/groundtruth_kb/dashboard.py` | Shortcut descriptions → copyable path text |
| `groundtruth-kb/src/groundtruth_kb/cli.py` | Loopback + CLI-primary docstrings/echo |
| `groundtruth-kb/src/groundtruth_kb/dashboard_service.py` | Loopback description on argparse |
| `groundtruth-kb/tests/test_dashboard.py` | `test_dashboard_shortcuts_use_copyable_path_labels` |
| `platform_tests/scripts/test_gtkb_dashboard_grafana.py` | Metric status, metadata scope, Copy path link tests |
| `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` | Regenerated from generator |

## Verification Evidence

```text
python scripts/gtkb_dashboard/generate_grafana_dashboard.py
# Wrote docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json

python -m pytest groundtruth-kb/tests/test_dashboard.py -q --tb=short
# 20 passed

python -m pytest platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_dashboard_subject_selector.py -q --tb=short
# 24 passed

python -m ruff check <touched python files>
# All checks passed (after E501 wrap on dashboard.py shortcuts row)
```

### Spec-derived assertions (mapped)

| Requirement | Test / evidence |
|-------------|-----------------|
| Clean metric sources → green status | `test_current_metric_statuses_green_when_sources_clean` |
| Combined subject scope label | same test asserts `dashboard_subject_scope` contains adopter name |
| Copyable paths, no misleading Open for workspace files | `test_dashboard_shortcuts_use_copyable_path_labels`, `test_shortcuts_panel_uses_copy_path_link_title` |
| Loopback refresh scope metadata | `refresh_service_scope` in metadata test |
| `gt dashboard` primary path | CLI docstring + Grafana header text (manual review) |

## Out of Scope (unchanged)

Visual redesign, public refresh hardening, schema changes, Agent Red subtree edits, formal KB artifact mutation.

## Loyal Opposition Verification Request

Please run independent VERIFIED on this report in a separate session context. Re-run the verification commands above and confirm generated Grafana JSON matches generator output.
