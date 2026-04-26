NO-GO

# GTKB-INCIDENT-RESPONSE IR-0.1 Proposal Review

**Date:** 2026-04-26
**Reviewed proposal:** `bridge/gtkb-incident-response-ir-0-1-001.md`
**Mode:** Implementation proposal review
**Decision:** NO-GO

## Verdict

NO-GO. The cross-repo execution pattern is directionally consistent with the ADR-supersession pattern, but the proposed inventory is not complete enough for its stated purpose and misidentifies the public status API as a write path.

## Blocking Findings

### [P1] Inventory omits existing incident write and consumer surfaces

The proposal says IR-0.1 maps existing incident-related surfaces so the framework does not create parallel concepts. The five-row table omits material existing surfaces:

- `src/multi_tenant/superadmin_api/_operations.py:114-242` defines the incident list/create/get/update/resolve API routes. This is the actual write/control API surface.
- `src/multi_tenant/alert_engine.py:148-166` consumes active incident count through `incident_repo.list_active()` for alert rules.
- `tests/multi_tenant/test_incident_repository.py:1-12` covers repository CRUD behavior directly.
- `tests/multi_tenant/test_mutation_superadmin_operations.py:113-210` covers authenticated mutation routes for create/update/resolve.

Risk / impact:

- The inventory would approve an upstream boundary SPEC while leaving out the existing runtime API that creates and updates incidents.
- Later framework commands could diverge from the already-existing superadmin mutation surface, which is exactly the parallel-concept risk IR-0 was meant to prevent.

Recommended action:

- Add rows for the superadmin incident operations, alert-engine incident metric, repository CRUD tests, and mutation-route tests.
- For each row, define disposition and compatibility notes against `SPEC-INCIDENT-SURFACES-BOUNDARY-001`.

### [P1] Public status API is read-only, but the proposal treats it as a write path

The proposal's table says the public status API is `reuse` and that the framework's `::incident-update` writes through it. Live code shows the opposite:

- `src/multi_tenant/status_api.py:79-146` defines only `GET /api/status`.
- `public_status()` calls `_incident_repo.list_active()` and renders `PublicStatusResponse`.
- The write paths are in `src/multi_tenant/superadmin_api/_operations.py:133-242` and `src/multi_tenant/repositories/incidents.py:48-249`.

Risk / impact:

- If this disposition is codified, the boundary-map SPEC will point future command work at a read-only projection instead of the mutation/repository layer.

Recommended action:

- Reclassify `status_api.py` as a read projection / consumer surface.
- Point `::incident-update` and related write commands to the framework boundary interface backed by `IncidentRepository` or the superadmin mutation layer, not the public status API.

## Non-Blocking Notes

- Keeping D0.1 Agent Red-local is consistent with `bridge/gtkb-incident-response-003.md` section 5, which explicitly leaves the existing-surfaces inventory as the local exception to otherwise-upstream routing.
- The upstream SPEC should be held until the corrected inventory rows are reviewed, because the SPEC's boundary rules need to reflect the complete surface map.

## Verification

Static review only. I inspected the proposal, parent bridge files, and the referenced Agent Red incident/status/alert code and tests. No tests were run for this proposal review.

## Decision Needed From Owner

None.

