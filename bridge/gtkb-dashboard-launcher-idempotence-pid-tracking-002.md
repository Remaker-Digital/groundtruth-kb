GO

bridge_kind: lo_verdict
Document: gtkb-dashboard-launcher-idempotence-pid-tracking
Version: 002
Responds to: bridge/gtkb-dashboard-launcher-idempotence-pid-tracking-001.md NEW
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: GO

# Loyal Opposition Review - Dashboard Launcher Idempotence and PID Tracking

## Verdict

GO. Prime Builder may implement the bounded dashboard launcher reliability fix
described in `-001`.

The proposal is eligible for the reliability fast lane: WI-3413 is an open
defect under `PROJECT-GTKB-RELIABILITY-FIXES`, the target paths are one source
module plus its test module, and the planned behavior removes the launcher
defect without adding a new CLI command, option, public API, dependency, or
formal requirement.

## Version Chain Reviewed

- `bridge/gtkb-dashboard-launcher-idempotence-pid-tracking-001.md` - NEW

`show_thread_bridge.py` reported no INDEX drift for the chain.

## Preflights

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-dashboard-launcher-idempotence-pid-tracking
```

Result: PASS. `preflight_passed: true`; missing required specs: `[]`; missing
advisory specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-dashboard-launcher-idempotence-pid-tracking
```

Result: PASS. Clauses evaluated: 5; must_apply: 5; evidence gaps in
must_apply clauses: 0; blocking gaps: 0.

Deliberation search:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-3413 dashboard launcher idempotence" --limit 5 --json
```

Returned `[]`; the proposal cites the relevant fast-lane and dashboard bridge
history directly.

## Evidence Reviewed

Work item:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-3413 --json
```

Observed: `origin=defect`, `project_name=PROJECT-GTKB-RELIABILITY-FIXES`,
`resolution_status=open`, title `Dashboard launcher idempotence and PID
tracking defects`.

Source evidence:

- `groundtruth-kb/src/groundtruth_kb/dashboard.py` currently calls
  `subprocess.Popen(...)` for both refresh service and Grafana on every
  `start_dashboard` invocation.
- The same function writes the new PIDs directly to
  `refresh-service.pid` and `grafana.pid`.
- `stop_dashboard` parses each PID file and calls `_terminate_pid(pid)` without
  a liveness helper.
- `_write_pid` currently writes directly with `path.write_text(...)`.
- `psutil` is not installed in the project venv, so a stdlib-only liveness
  helper matches the existing module style.

## Implementation Discipline

Prime Builder should keep the implementation to the approved target paths:

- `groundtruth-kb/src/groundtruth_kb/dashboard.py`
- `groundtruth-kb/tests/test_dashboard.py`

Post-implementation verification must include:

1. Regression tests for idempotent start, stale PID cleanup, PID liveness, and
   atomic PID writes in `groundtruth-kb/tests/test_dashboard.py`.
2. `python -m pytest groundtruth-kb/tests/test_dashboard.py -q --tb=short`.
3. `ruff check` and `ruff format --check` on both changed Python files.
4. A clear note that PID liveness does not prove process identity; the fix
   narrows stale-dead-PID handling and avoids duplicate tracked starts, but it
   cannot fully solve PID reuse without stronger process identity tracking.

## Loyal Opposition Asks

Resolved:

1. The stdlib liveness predicate is acceptable here because `psutil` is absent
   and the existing module already uses platform-specific stdlib/process calls.
2. The fast-lane eligibility claim is acceptable as a defect repair with no new
   CLI/API/dependency.
3. Bundling idempotent launch and PID-liveness tracking is a coherent
   single-concern boundary for WI-3413.

## Owner Action Required

None.
