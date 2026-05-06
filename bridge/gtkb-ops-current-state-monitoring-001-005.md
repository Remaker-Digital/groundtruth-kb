NEW

# Implementation Report - GTKB-OPS-CURRENT-STATE-MONITORING-001

**Author:** Prime Builder (Codex, harness A)
**Date:** 2026-05-06
**Type:** Post-implementation report
**Backlog item:** `GTKB-OPS-CURRENT-STATE-MONITORING-001`
**Proposal authority:** `bridge/gtkb-ops-current-state-monitoring-001-003.md`
**Review authority:** `bridge/gtkb-ops-current-state-monitoring-001-004.md` (`GO`)

---

## Claim

The deterministic operating-state surface is implemented as a reusable
collector, CLI command, dashboard SQLite/Grafana surface, and startup-safe
renderer. It does not add LLM/API calls, API keys, or external service probes.

## Implemented Changes

- Added `groundtruth_kb.operating_state` with schema-versioned JSON output.
- Added `gt status`, `gt status --json`, `gt status --startup`,
  `gt status --startup --json`, and repeatable `--component <name>` filters.
- Added probes for project/config, SQLite, ChromaDB, bridge latest-status
  counts, smart-poller notifications, dashboard SQLite, hooks/rules, and
  startup report presence.
- Added dashboard ingestion through the same collector:
  `operating_state_components` table plus an "Operating State" Grafana panel.
- Added startup-safe rendering through `format_startup_operating_state()` and
  `gt status --startup`, using the same collector payload.
- Startup mode uses a bounded SQLite read probe instead of full
  `PRAGMA integrity_check`; a live root collection completed in about
  0.003 seconds after this fix.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/operating_state.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/dashboard.py`
- `groundtruth-kb/tests/test_operating_state.py`
- `groundtruth-kb/tests/test_dashboard.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed under the active bridge
  lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the implemented
  surface follows the approved proposal and linked requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below maps
  tests to requirement coverage.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - current state is now durable,
  deterministic artifact output instead of reconstructed chat state.
- `.claude/rules/project-root-boundary.md` and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - archive paths are rejected as live
  state and collector probes stay anchored to the configured project root.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repeated AI inspection is now
  moved behind deterministic code.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart-poller state is probed
  without restoring the retired OS poller.

## Spec-To-Test Map

| Requirement | Evidence |
|---|---|
| Schema-valid `gt status --startup --json` | `tests/test_operating_state.py::test_status_cli_json_and_startup_use_same_collector` |
| No LLM/API dependency or API key | `tests/test_operating_state.py::test_operating_state_module_has_no_llm_or_network_dependency` |
| Deterministic CLI text/JSON and component filters | `tests/test_operating_state.py` plus `tests/test_cli.py` regression run |
| SQLite and ChromaDB states degrade explicitly | `tests/test_operating_state.py::test_collect_operating_state_reports_project_and_db`; `test_missing_chromadb_is_unknown_not_crash` |
| Bridge queue counts distinguish Prime and Loyal Opposition actionability | `tests/test_operating_state.py::test_bridge_probe_counts_latest_role_actionable_statuses` |
| Dashboard consumes same collector output | `tests/test_dashboard.py::test_dashboard_init_generates_sqlite_and_grafana_assets` |
| Startup consumes same collector output | `format_startup_operating_state()` and `gt status --startup` tested in `test_status_cli_json_and_startup_use_same_collector` |
| Root-boundary/archive rejection | `tests/test_operating_state.py::test_archive_path_is_rejected` |

## Verification

```powershell
cd E:\GT-KB\groundtruth-kb
python -m pytest tests/test_operating_state.py tests/test_dashboard.py -q --tb=short
# 10 passed, 1 warning

python -m pytest tests/test_cli.py tests/test_dashboard.py tests/test_operating_state.py -q --tb=short
# 45 passed, 1 warning

python -m ruff check src/groundtruth_kb/operating_state.py src/groundtruth_kb/cli.py src/groundtruth_kb/dashboard.py tests/test_operating_state.py tests/test_dashboard.py
# All checks passed.

python -m ruff format --check src/groundtruth_kb/operating_state.py src/groundtruth_kb/cli.py src/groundtruth_kb/dashboard.py tests/test_operating_state.py tests/test_dashboard.py
# 5 files already formatted
```

Live startup probe check:

```json
{"components": ["project", "db", "chroma", "bridge", "smart-poller", "dashboard", "hooks", "startup"], "elapsed_seconds": 0.003, "overall_status": "WARN"}
```

The warning in the pytest runs is the same upstream ChromaDB deprecation
warning observed in Slice 5.5:
`chromadb\telemetry\opentelemetry\__init__.py:128`.

## Applicability Preflight

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ops-current-state-monitoring-001
```

- operative_file: `bridge/gtkb-ops-current-state-monitoring-001-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Risk / Impact

- Normal `gt status` may still run deeper local checks, but `--startup` avoids
  long-running SQLite integrity checks.
- Missing optional ChromaDB support degrades to `UNKNOWN` instead of crashing.
- Dashboard refresh now records operating-state rows; existing dashboard tables
  and panels remain intact.
- The implementation does not start or restore the retired OS poller.
- Full-repo `ruff format --check src tests` remains affected by pre-existing
  unrelated drift and was not run as a closure claim for this item.

## Recommended Action

Loyal Opposition should verify the operating-state collector, CLI, dashboard
ingestion, startup renderer, and mapped tests.

## Decision Needed From Owner

None.
