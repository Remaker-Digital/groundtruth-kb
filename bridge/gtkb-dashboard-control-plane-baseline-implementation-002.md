GO

# GTKB Dashboard Control-Plane Baseline Review

**Status:** GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-dashboard-control-plane-baseline-implementation-001.md`

## Verdict

GO for the narrow Phase 5 control-plane baseline slice, with the compatibility
boundary below treated as part of the approved scope.

The proposal chooses the correct host surface for the first registry-backed
control-plane work: the existing local dashboard refresh service already brokers
one bounded runtime operation, so it is the right place to prove registry
lookup, typed responses, and dry-run/apply separation.

## Prior Deliberations

- `DELIB-0877` is the current GTKB application-isolation planning record most
  directly related to this slice.
- `DELIB-0018`, `DELIB-0117`, and `DELIB-0119` are older related dashboard /
  control-surface deliberations surfaced by the read-only
  `search_deliberations()` pass.
- No exact prior deliberation for this specific baseline implementation thread
  was surfaced beyond that related context.

## Approval Basis

- The proposal keeps the first operation set intentionally small:
  `dashboard.read`, `dashboard.refresh`, and `control_plane.status` only:
  `bridge/gtkb-dashboard-control-plane-baseline-implementation-001.md:75-96`.
- The live repo does have a single bounded refresh service already, and it is
  the natural place to add registry dispatch:
  `bridge/gtkb-dashboard-control-plane-baseline-implementation-001.md:44-59`,
  `scripts/gtkb_dashboard/refresh_service.py:131-170`, and
  `scripts/gtkb_dashboard/start_local_dashboard.ps1:122-127`.
- The guard rules correctly forbid arbitrary browser-supplied roots, paths, or
  function dispatch:
  `bridge/gtkb-dashboard-control-plane-baseline-implementation-001.md:146-155`.

## Required Implementation Boundaries

1. Preserve the current external refresh-service compatibility surface in this
   first slice:
   - `GET /`
   - `GET /health`
   - `POST /refresh`
2. The registry may become the internal dispatch path for those routes, but the
   first slice must not break the existing browser form or local dashboard
   startup path.
3. Keep `dashboard.refresh` as the only apply-capable operation in this slice.
   All other operations remain read-only.
4. Do not expand this GO into bridge writes, projection apply, mode/work-subject
   changes, restart controls, or arbitrary command execution.

## Findings

No blocking findings.

## Owner Decision Needed

None.
