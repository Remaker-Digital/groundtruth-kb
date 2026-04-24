NEW

# GTKB Dashboard Control-Plane Baseline Implementation Proposal

bridge_kind: proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-005]
target_paths: ["scripts/gtkb_dashboard/control_plane_registry.py", "scripts/gtkb_dashboard/refresh_service.py", "scripts/release_candidate_gate.py", "tests/scripts/test_gtkb_dashboard_control_plane.py", "tests/scripts/test_gtkb_dashboard_grafana.py", "tests/scripts/test_release_candidate_gate.py"]

## Requested Verdict

GO to implement the narrow Phase 5 control-plane baseline below, or NO-GO with
required revisions.

## Parent GO Inputs

This proposal is the first concrete implementation slice after the accepted
Phase 5 planning review:

- `bridge/gtkb-isolation-005-control-plane-plan-review-002.md`

The Phase 5 plan accepted the dashboard control-plane design and required later
concrete implementation proposals before behavior changes.

## Claim

The correct first Phase 5 implementation slice is the broker foundation, not
the broad mutation surface:

1. introduce a product-controlled operation registry with deterministic
   metadata and handler lookup,
2. wrap the current dashboard refresh service behind typed operations so the
   browser no longer talks to an ad hoc `/refresh` control surface directly,
3. require dry-run semantics for the runtime-DB refresh path before any apply
   path is accepted, and
4. keep all Markdown mutation, projection apply, bridge write, and session
   control operations out of this first slice.

This slice should establish safe control-plane structure without pretending the
full Phase 5 registry is already implemented.

## Current Evidence

### Existing Refresh Surface

- `scripts/gtkb_dashboard/refresh_service.py` currently exposes only `GET /`,
  `GET /health`, and token-gated `POST /refresh`, then directly calls
  `refresh_database(db_path, project_root)`.
- The current service does not expose a typed registry, declared operation IDs,
  dry-run preview, role-slot metadata, or audit-oriented response structure.

### Existing Dashboard Posture

- `scripts/session_self_initialization.py` intentionally reports that the
  static dashboard cannot execute local shell/apply actions.
- The local Grafana startup path in
  `scripts/gtkb_dashboard/start_local_dashboard.ps1` already depends on the
  refresh service and local dashboard DB/runtime roots, so it is the natural
  first control-plane host surface.

### Why This Slice Is First

- Phase 5 requires a typed operation registry before any new mutating dashboard
  endpoint exists.
- The current refresh service is already a broker for one bounded runtime
  operation, so it is the safest place to introduce the registry contract.
- Jumping straight to Markdown edits, projection apply, bridge writes, or
  session restart controls would create too much surface before the registry,
  dry-run, and handler lookup rules are proven.

## Scope

Implement only:

1. A new `scripts/gtkb_dashboard/control_plane_registry.py` module defining the
   first registry entries and their metadata.
2. Initial operation IDs limited to:
   - `dashboard.read`
   - `dashboard.refresh`
   - `control_plane.status`
3. Registry metadata for each operation:
   - `operation_id`
   - `display_name`
   - `allowed_subjects`
   - `required_role_slots`
   - `target_root_policy`
   - `effective_timing`
   - `supports_dry_run`
4. `refresh_service.py` changes so browser/API requests resolve through the
   registry and return typed JSON payloads instead of a one-off refresh shape.
5. Dry-run support for `dashboard.refresh` that reports target runtime DB,
   project root, refresh token presence, and intended operation without writing.
6. Apply support only for `dashboard.refresh`, still constrained to the local
   app dashboard DB/runtime path.
7. Focused tests for registry metadata, invalid operation rejection, dry-run
   behavior, typed refresh apply behavior, and release-gate wiring.

Do not implement in this slice:

- Markdown scan/append/remove/normalize,
- projection render/validate/apply,
- mode or work-subject change handlers,
- harness-topology registration,
- bridge scan/write handlers,
- pause/resume/restart controls,
- rollback apply beyond refresh-runtime status reporting,
- arbitrary browser-supplied roots, paths, scripts, or commands.

## Proposed Operation Contract

Example request shapes:

```json
{
  "operation_id": "dashboard.read"
}
```

```json
{
  "operation_id": "dashboard.refresh",
  "dry_run": true
}
```

```json
{
  "operation_id": "dashboard.refresh",
  "dry_run": false
}
```

Required response fields for this slice:

- `operation_id`
- `status`
- `effective_timing`
- `subject`
- `project_root`
- `dashboard_db`
- `dry_run`
- `details`

`dashboard.refresh` dry runs must not write the SQLite runtime DB.

## Proposed First-Slice Guard Rules

1. Unknown operation IDs fail closed.
2. Browser input may not override project root, dashboard DB path, or handler
   target path in this slice.
3. `dashboard.refresh` apply remains limited to the app-local dashboard runtime
   DB and current project root.
4. Non-refresh operations in this slice remain read-only.
5. The registry must be the only handler lookup path; `refresh_service.py`
   should not dispatch arbitrary function names or shell commands.

## Proposed File Touchpoints

Primary code:

- `scripts/gtkb_dashboard/control_plane_registry.py`
- `scripts/gtkb_dashboard/refresh_service.py`
- `scripts/release_candidate_gate.py`

Tests:

- `tests/scripts/test_gtkb_dashboard_control_plane.py`
- `tests/scripts/test_gtkb_dashboard_grafana.py`
- `tests/scripts/test_release_candidate_gate.py`

## Implementation Sequence

1. Add the registry module with the first three operation entries.
2. Refactor `refresh_service.py` to resolve operations through the registry.
3. Add dry-run and typed apply responses for `dashboard.refresh`.
4. Add focused tests for registry metadata and request handling.
5. Wire the new tests into the release gate.

## Verification Commands

Required focused checks:

```powershell
python -m pytest tests/scripts/test_gtkb_dashboard_control_plane.py tests/scripts/test_gtkb_dashboard_grafana.py tests/scripts/test_release_candidate_gate.py -q --tb=short
```

Recommended broader check after focused green:

```powershell
python scripts/release_candidate_gate.py --skip-frontend
```

## Review Questions

1. Is limiting the first Phase 5 slice to registry foundation plus typed
   `dashboard.read` / `dashboard.refresh` / `control_plane.status` the right
   boundary?
2. Is it acceptable that `dashboard.refresh` is the only apply-capable
   operation in this slice, with all other planned Phase 5 operations deferred?
3. Should the current `/refresh` route be preserved as a compatibility wrapper
   over the registry in this first slice, or should the registry endpoint
   replace it immediately?

## Non-Scope Reminder

This proposal does not request Markdown mutation, projection apply, bridge
writes, session controls, mode toggles, topology registry, or arbitrary file
operations. Those remain later slices.
