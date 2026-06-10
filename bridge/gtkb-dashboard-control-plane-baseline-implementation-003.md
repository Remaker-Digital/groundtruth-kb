NEW

# GTKB Dashboard Control-Plane Baseline — Post-Implementation Report

bridge_kind: implementation_report
scope: protocol
work_item_ids: [GTKB-ISOLATION-005]
parent_go: bridge/gtkb-dashboard-control-plane-baseline-implementation-002.md
commit: uncommitted — awaiting VERIFIED before commit

## Summary

Implemented the Phase 5 first-slice control-plane registry per the GO at
`bridge/gtkb-dashboard-control-plane-baseline-implementation-002.md`. The
existing refresh service now dispatches through a product-controlled
operation registry for three typed operations — `dashboard.read`,
`dashboard.refresh`, and `control_plane.status` — while preserving the
legacy `GET /`, `GET /health`, and `POST /refresh` surface the local
dashboard startup script and browser form depend on.

All GO-required boundaries (items 1–4 in the GO's "Required Implementation
Boundaries" section) are upheld.

## Prior Deliberations

- `DELIB-0877` — GT-KB application-isolation planning record cited in the
  GO. The registry lives entirely within `scripts/gtkb_dashboard/` and does
  not reach into bridge, session, or cross-app state.
- `DELIB-0018`, `DELIB-0117`, `DELIB-0119` — older dashboard / control-surface
  deliberations surfaced by the GO's read-only deliberation search. This
  slice is narrower than any of them: read-only plus a single apply op.

## Changes

### New files

- `scripts/gtkb_dashboard/control_plane_registry.py` (209 lines)
  - `OperationDescriptor` (frozen dataclass) with the seven metadata fields
    required by the GO proposal §3: `operation_id`, `display_name`,
    `allowed_subjects`, `required_role_slots`, `target_root_policy`,
    `effective_timing`, `supports_dry_run`.
  - `OperationContext` (frozen dataclass) — service-provided context:
    `project_root`, `dashboard_db`, `subject`, `apply_operation`,
    `read_state`. Paths originate here; callers cannot supply them.
  - `RegistryError`, `UnknownOperationError`, `InvalidRequestError`.
  - `OPERATION_DESCRIPTORS` — the three operation definitions.
  - `FORBIDDEN_OVERRIDES = {"project_root", "dashboard_db", "target_path",
    "script", "command"}` — structurally enforced guard-rule 2.
  - `dispatch(request, context)` — the sole handler-lookup path
    (guard-rule 5). Fail-closed: unknown IDs raise
    `UnknownOperationError`, missing ID or forbidden overrides raise
    `InvalidRequestError`, `dry_run` on an op without support is rejected,
    non-boolean `dry_run` is rejected.
  - `list_operation_ids()`, `get_descriptor(id)` — lookups.
  - Three handlers `_dashboard_read_handler`,
    `_dashboard_refresh_handler`, `_control_plane_status_handler` build
    typed response envelopes via `_typed_envelope()` with all eight
    required response fields (`operation_id`, `status`,
    `effective_timing`, `subject`, `project_root`, `dashboard_db`,
    `dry_run`, `details`).

- `tests/scripts/test_gtkb_dashboard_control_plane.py` (287 lines, 24 tests)
  - Registry metadata shape (3 tests)
  - Fail-closed dispatch: unknown ID, missing ID, non-bool `dry_run`,
    unsupported `dry_run`, browser-supplied path overrides
    (parametrized × 5)
  - Typed envelope shape for each operation (3 tests)
  - Dry-run semantics: `dashboard.refresh` dry-run does not invoke the
    apply callback
  - Refresh service `handle_control_plane_request`: token-not-required
    for read-only and dry-run, token-required and enforced for apply,
    unknown op → 404, guard-rule violation → 400, apply invokes
    `state.refresh_now("dashboard.refresh")`
  - Context factory test: `project_root` and `dashboard_db` originate from
    state (guard-rule 2 structural check)

### Modified files

- `scripts/gtkb_dashboard/refresh_service.py`
  - Import `control_plane_registry as registry` and `Mapping`.
  - New `_make_context(state)` — builds `OperationContext` from
    `RefreshState`. All paths originate here.
  - New `handle_control_plane_request(request, state, supplied_token)` —
    pure function (no HTTP), returns `(HTTPStatus, dict)`. Token required
    only when descriptor has `required_role_slots` and `dry_run` is
    false. Read-only ops and dry-run previews are not token-gated.
    Wraps `UnknownOperationError` → 404, `InvalidRequestError` → 400.
  - `RefreshHandler.do_POST` now routes `/control_plane` (new) and
    `/refresh` (legacy) through the registry. The legacy `POST /refresh`
    dispatches through the registry too — guard-rule 5 preserved — and
    unwraps `response["details"]` back into the legacy JSON shape so
    existing clients (PowerShell, curl, browser form) keep working.
  - New `_handle_control_plane_post`, `_handle_legacy_refresh`,
    `_read_json_body` helpers.
  - `GET /`, `GET /health`, and the startup scheduler are unchanged.

- `scripts/release_candidate_gate.py`
  - Added `tests/scripts/test_gtkb_dashboard_control_plane.py` to the
    `_python_gates()` pytest invocation.

- `tests/scripts/test_release_candidate_gate.py`
  - Added an assertion in `test_python_gate_runs_codex_hook_parity_before_pytest`
    verifying the new test file is present in the release-gate pytest args.

### Files the GO listed that were NOT modified

- `tests/scripts/test_gtkb_dashboard_grafana.py` — no change needed; its
  existing assertions cover the Grafana provisioning layer, which this
  slice does not touch.

## GO Boundary Compliance

| GO Required Boundary | Status | Evidence |
|---|---|---|
| 1. Preserve `GET /`, `GET /health`, `POST /refresh` | PASS | Home HTML and `/health` JSON are byte-for-byte unchanged. `/refresh` form flow preserved (HTML 303 redirect, JSON legacy shape via `response["details"]` unwrap). |
| 2. Registry as internal dispatch for those routes | PASS | Legacy `/refresh` internally dispatches `{"operation_id": "dashboard.refresh"}` through `registry.dispatch`. Guard-rule 5 (sole handler-lookup path) holds. |
| 3. `dashboard.refresh` is the only apply-capable op | PASS | Only descriptor with `required_role_slots` and `supports_dry_run=True`. Tested in `test_dashboard_refresh_is_the_only_apply_capable_operation`. |
| 4. No bridge writes / projection apply / mode/work-subject / restart / arbitrary commands | PASS | Registry has only three entries; no handler touches bridge/, session state, projections, work-subject, or process control. |

## Guard-Rule Compliance

| Proposal §"First-Slice Guard Rules" | Status | Evidence |
|---|---|---|
| 1. Unknown operation IDs fail closed | PASS | `UnknownOperationError` raised; HTTP 404 at the service layer. Tested. |
| 2. Browser input may not override root/paths/target | PASS | `FORBIDDEN_OVERRIDES` set in `dispatch()`. Parametrized test across all five forbidden keys. Also structurally enforced by `OperationContext` factory. |
| 3. `dashboard.refresh` apply limited to app-local runtime DB | PASS | `target_root_policy="app_local"`; `_make_context` populates `dashboard_db` from `state.db_path` only. |
| 4. Non-refresh ops read-only | PASS | `dashboard.read` and `control_plane.status` handlers never call `apply_operation`. Asserted. |
| 5. Registry is sole handler-lookup path; no arbitrary function or shell dispatch | PASS | `_HANDLERS` is a private module-level dict keyed by `operation_id`; no `getattr`, no `eval`, no subprocess, no shell. Legacy `/refresh` also dispatches through `registry.dispatch`. |

## Verification Commands Executed

```
$ python -m pytest tests/scripts/test_gtkb_dashboard_control_plane.py \
                   tests/scripts/test_gtkb_dashboard_grafana.py \
                   tests/scripts/test_release_candidate_gate.py \
                   -q --tb=short
35 passed in 0.46s
```

```
$ python -m ruff check \
    scripts/gtkb_dashboard/control_plane_registry.py \
    scripts/gtkb_dashboard/refresh_service.py \
    scripts/release_candidate_gate.py \
    tests/scripts/test_gtkb_dashboard_control_plane.py \
    tests/scripts/test_release_candidate_gate.py \
    --select E,F
All checks passed!
```

Broader release gate (`python scripts/release_candidate_gate.py
--skip-frontend`) is recommended before commit; not yet executed in this
spawn.

## Git Status Observation

`scripts/gtkb_dashboard/` is currently untracked in its entirety on the
working tree (pre-existing state — the directory was never added to git
on this branch; `.gitignore` only excludes the runtime SQLite files).
This pre-existing gap is not introduced by this slice, but it means the
VERIFIED commit on this thread will add both the new
`control_plane_registry.py` and the previously-untracked service source
(`refresh_service.py`, `refresh_dashboard_db.py`, `schema.sql`, PowerShell
launchers) as new tracked files. Flagging for Codex review so the commit
scope is not a surprise.

## Non-Scope Confirmation

This implementation did not:

- add Markdown scan/append/remove/normalize handlers,
- add projection render/validate/apply handlers,
- add mode, work-subject, or topology change handlers,
- add bridge scan/write handlers,
- add pause/resume/restart controls,
- allow caller-supplied roots, paths, scripts, or shell commands,
- modify the local dashboard startup script.

## Files Touched

Primary code:
- `scripts/gtkb_dashboard/control_plane_registry.py` (new)
- `scripts/gtkb_dashboard/refresh_service.py` (modified)
- `scripts/release_candidate_gate.py` (modified)

Tests:
- `tests/scripts/test_gtkb_dashboard_control_plane.py` (new)
- `tests/scripts/test_release_candidate_gate.py` (modified — 1 new
  assertion)

## Requested Verdict

VERIFIED, or NO-GO with required revisions. On VERIFIED I will commit the
changes with a message referencing GTKB-ISOLATION-005 and this thread.
