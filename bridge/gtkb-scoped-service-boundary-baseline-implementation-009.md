NEW

# GTKB Scoped Service Boundary Baseline Post-Implementation Report

**Status:** NEW (post-implementation verification requested)
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Approved proposal:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md`
**GO verdict:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-008.md`

bridge_kind: post_impl_report
scope: protocol
work_item_ids: [GTKB-ISOLATION-012]
target_paths: ["groundtruth.toml", "scripts/gtkb_scoped_client.py", "scripts/check_scoped_service_boundary.py", "scripts/release_candidate_gate.py", "scripts/session_self_initialization.py", "tests/scripts/test_gtkb_scoped_client.py", "tests/scripts/test_release_candidate_gate.py", "tests/scripts/test_session_self_initialization.py"]

## Requested Verdict

VERIFIED, or NO-GO with required remediation.

## Summary

Revision 3 was implemented as written. The Phase 4 baseline scoped-service
slice now owns exactly one read operation (`dashboard.summary.read`), fully
routes the live startup/dashboard summary path through the scoped client,
and mechanically guards against regression via an AST-driven no-raw-read
check in `scripts/check_scoped_service_boundary.py`. Release-gate ordering
puts that checker before the pytest suite, and a new ordering test asserts
that invariant.

All three GO Conditions of Approval from `-008` are met; evidence is below.

## Conditions Of Approval — Evidence

### Condition 1 — Full summary-path migration (no client-alongside-raw-reader)

- Live `_database_metrics(...)` now calls `GtkbScopedClient.invoke(DASHBOARD_SUMMARY_READ, ...)`
  and consumes the scoped-client envelope (payload + source/freshness metadata):
  `scripts/session_self_initialization.py:653-739`.
- There is no `sqlite3.connect(...)` inside that function body. A repo-wide
  scan confirms the only remaining `sqlite3.connect` in
  `scripts/session_self_initialization.py` is at line 2587 inside
  `_historical_agent_red_backfill(...)` (lines 2582-2649) — the deferred
  history path explicitly out of scope per Revision 3 §"Not in this slice".
- Call site on the startup-model assembly path is preserved at
  `scripts/session_self_initialization.py` in `build_startup_model(...)`
  near line 2355, and now receives the scoped-client envelope's
  `source_metadata` rather than pretending the read model is canonical state.

Diagnostic command (repeatable):

```
python -c "import ast, pathlib; src = pathlib.Path('scripts/session_self_initialization.py').read_text(encoding='utf-8'); tree = ast.parse(src); [print(f'{n.name}: lines {n.lineno}-{n.end_lineno}') for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_database_metrics']"
```

Output on current tree:

```
_database_metrics: lines 653-739
```

### Condition 2 — Checker fails closed on raw `sqlite3.connect(...groundtruth.db...)` on the migrated summary path

Implementation: `scripts/check_scoped_service_boundary.py:91-149` walks the
AST of `session_self_initialization.py`, flags any `sqlite3.connect(...)`
call inside any function in `SUMMARY_PATH_FUNCTIONS` (currently
`("_database_metrics",)`), and string-checks call-site source for the
`groundtruth.db` marker so the guard is scoped to the GT-KB DB.

The behavior is proved by a dedicated unit test that substitutes a poisoned
module file and asserts the checker returns `status=fail` with a
`raw groundtruth.db` error:
`tests/scripts/test_gtkb_scoped_client.py::test_boundary_checker_detects_raw_sqlite_reader_on_summary_path`.

### Condition 3 — Fresh checker + pytest evidence

**`python scripts/check_scoped_service_boundary.py --json` (exit 0):**

```json
{
  "project_root": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement",
  "status": "pass",
  "checks": {
    "config": {
      "source_path": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement\\groundtruth.toml",
      "project_root": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement",
      "default_subject": "application",
      "application_id": "agent-red",
      "allowed_read_operations": [
        "dashboard.summary.read"
      ],
      "runtime_root": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement\\memory",
      "dashboard_db": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement\\memory\\gtkb-dashboard.sqlite"
    },
    "no_raw_read_on_summary_path": {
      "summary_path_file": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement\\scripts\\session_self_initialization.py",
      "checked_functions": [
        "_database_metrics"
      ],
      "sqlite_connect_findings": []
    }
  }
}
```

**`python -m pytest tests/scripts/test_gtkb_scoped_client.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_session_self_initialization.py -q --tb=short`:**

```
collected 51 items

tests\scripts\test_gtkb_scoped_client.py ...................             [ 37%]
tests\scripts\test_release_candidate_gate.py ..........                  [ 56%]
tests\scripts\test_session_self_initialization.py ...................... [100%]

================== 51 passed, 1 warning in 205.73s (0:03:25) ==================
```

(The one deprecation warning is from `chromadb` upstream —
`asyncio.iscoroutinefunction` — unrelated to this slice.)

## Implementation Walkthrough

### 1. Root `groundtruth.toml` — single-entry allowlist

`groundtruth.toml:17-28` now contains:

```toml
[scoped_service]
default_subject = "application"
application_id = "agent-red"
project_root = "."
allowed_read_operations = [
  "dashboard.summary.read",
]
# Intentionally omitted in this slice (added by later Phase 4 sub-slices):
#   - "dashboard.history.read"
#   - allowed_request_operations
runtime_root = "memory"
dashboard_db = "memory/gtkb-dashboard.sqlite"
```

`tools/knowledge-db/groundtruth.toml` was not touched (F1 from `-002`).

### 2. Scoped client — `scripts/gtkb_scoped_client.py`

- `ScopedServiceConfig` dataclass (`scripts/gtkb_scoped_client.py:81-92`)
  parses `[scoped_service]` and enforces all required fields + allowlist
  validity including mutating-marker rejection.
- `GtkbScopedClient.invoke(...)` (`scripts/gtkb_scoped_client.py:214-254`)
  rejects mutating operations, unknown read operations, foreign subjects,
  and foreign project roots before dispatching to the single handler.
- `_dashboard_summary_read(...)` (`scripts/gtkb_scoped_client.py:256-304`)
  owns the only `sqlite3.connect(...)` on `groundtruth.db` for the summary
  surface and returns a typed envelope with `source`, `source_path`, and
  `freshness` metadata.
- CLI surface (`scripts/gtkb_scoped_client.py:307-355`) exposes
  `python scripts/gtkb_scoped_client.py dashboard.summary.read --json` with
  a trimmed payload for CLI-safe output.

### 3. Boundary checker — `scripts/check_scoped_service_boundary.py`

- `_check_config(...)` (`scripts/check_scoped_service_boundary.py:54-88`)
  loads the TOML via the client module and asserts the allowlist equals
  `("dashboard.summary.read",)` exactly, and that `allowed_request_operations`
  is empty.
- `_collect_function_sqlite_connects(...)` + `_check_no_raw_read_on_summary_path(...)`
  (`scripts/check_scoped_service_boundary.py:91-155`) implement the AST
  guard with a `groundtruth.db` string-check on the call snippet so the
  guard is scoped to the GT-KB DB rather than any `sqlite3` usage.
- `run_checks(...)` (`scripts/check_scoped_service_boundary.py:158-183`)
  returns a structured report and surfaces errors for either check without
  short-circuiting.

### 4. Release-gate wiring — `scripts/release_candidate_gate.py`

- `_python_gates()` now runs `python scripts/check_scoped_service_boundary.py`
  alongside the other Phase 3/4 checkers (`check_environment_isolation.py`
  and `check_session_overlay_policy.py`) before the pytest lane:
  `scripts/release_candidate_gate.py:87-92`.
- The pytest lane registers `tests/scripts/test_gtkb_scoped_client.py`
  among the lane's suites: `scripts/release_candidate_gate.py:101-125`.

### 5. Migrated summary path — `scripts/session_self_initialization.py`

- `_database_metrics(project_root)` (`scripts/session_self_initialization.py:653-739`)
  now invokes the scoped client, surfaces source/freshness metadata on the
  envelope, and returns the same downstream shape that
  `build_startup_model(...)` expects. The in-body docstring names the
  `check_scoped_service_boundary.py` guard as the mechanical enforcement.
- `build_startup_model(...)` still calls `_database_metrics(...)` at the
  existing site near `:2355`; the call signature is unchanged because the
  envelope's `source_metadata` is embedded into the returned dict.
- No other sqlite3 connection to `groundtruth.db` exists in that function
  body; the sole remaining call in the module (line 2587) is inside
  `_historical_agent_red_backfill(...)` (lines 2582-2649), which is the
  explicitly deferred history path.

### 6. Focused tests

`tests/scripts/test_gtkb_scoped_client.py` (19 tests, 100 pass):

- Config load happy path
- Missing section raises
- Missing required field raises
- Empty allowlist raises
- Mutating op in allowlist raises
- Unsupported read op raises
- Non-empty `allowed_request_operations` raises
- Summary response shape + freshness metadata
- Summary path when `groundtruth.db` missing → `available=false`
- Mutating op rejected at invoke
- Unknown in-namespace read op rejected (covers `dashboard.history.read`)
- Unknown op outside namespace rejected
- Foreign subject rejected
- Foreign project root rejected
- Boundary checker live repo passes (regression canary)
- Boundary checker detects allowlist drift
- Boundary checker detects raw `sqlite3.connect` reappearing on summary path
- CLI returns trimmed JSON on summary read
- CLI rejects mutating op with exit code 2

`tests/scripts/test_release_candidate_gate.py` adds one new ordering test
(`test_python_gate_runs_scoped_service_boundary_before_pytest`) that asserts
the scoped checker runs before the pytest lane and that
`tests/scripts/test_gtkb_scoped_client.py` is registered in that lane.
10/10 pass (including 4 pre-existing ordering tests).

`tests/scripts/test_session_self_initialization.py` is unchanged on this
slice; 22/22 pass against the migrated summary path.

## Response To `-008` Observation O1 (stale governance-adoption baseline)

Per `-008` O1: `test_groundtruth_governance_adoption.py` baseline has
shifted to `1 failed, 29 passed` (bridge-protocol wording assertion at
`tests/scripts/test_groundtruth_governance_adoption.py:762-775`). This suite
remains out of the focused verification lane for this slice, as reaffirmed
in Revision 3 §Focused Verification Lane, and is handled in the Phase 7
thread. This report does not repeat the older "3 failures" claim.

## Commit Intent

Proposed commit message (staged on branch `main`, to be committed AFTER
this report is VERIFIED):

```
bridge: gtkb-scoped-service-boundary-baseline-implementation Phase 4 baseline (GO -008)

- Add [scoped_service] section to root groundtruth.toml (single-entry
  allowlist: dashboard.summary.read).
- Add scripts/gtkb_scoped_client.py: narrow typed client owning the sole
  raw groundtruth.db connection on the summary path.
- Add scripts/check_scoped_service_boundary.py: config + AST no-raw-read
  guard on _database_metrics.
- Wire checker into scripts/release_candidate_gate.py before the pytest
  lane; register tests/scripts/test_gtkb_scoped_client.py in the lane.
- Migrate scripts/session_self_initialization.py::_database_metrics to
  GtkbScopedClient.invoke(DASHBOARD_SUMMARY_READ).
- Add tests/scripts/test_gtkb_scoped_client.py (19 tests) including
  live-repo regression canary and poisoned-module guard test.
- Add ordering test in tests/scripts/test_release_candidate_gate.py for
  the new scoped checker.

GTKB-ISOLATION-012, DELIB-0877, DELIB-0878, DELIB-0879.
```

The commit is intentionally deferred until VERIFIED per CLAUDE.md bridge
protocol.

## Open Items / Deferred

None for this slice. The following remain deferred to later Phase 4
sub-slices, unchanged from Revision 3 §"Not in this slice":

- `dashboard.history.read` operation (with migration of `_historical_agent_red_backfill`
  at `scripts/session_self_initialization.py:2582-2649`)
- Deliberation / MemBase / bridge-write / deployment / hosted-service / overlay
  operations
- Dashboard control-plane registry
- `workstream-focus.py` drift normalization (separate Phase 7 thread)

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0877`, `DELIB-0878`, `DELIB-0879` — GTKB application-isolation
  planning records.
- Bridge thread history: `-001 NEW → -002 NO-GO → -003 REVISED → -004 NO-GO
  → -005 REVISED → -006 NO-GO → -007 REVISED → -008 GO`.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
