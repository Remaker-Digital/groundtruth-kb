NO-GO

# GTKB-INCIDENT-RESPONSE IR-0.1 Revised-2 Proposal Review

**Date:** 2026-04-26
**Reviewed proposal:** `bridge/gtkb-incident-response-ir-0-1-005.md`
**Prior review:** `bridge/gtkb-incident-response-ir-0-1-004.md`
**Mode:** Implementation proposal review
**Decision:** NO-GO

## Verdict

NO-GO. The revision correctly adds the backend lifecycle, router, verification-runner, and adjacent test surfaces requested in `-004`, but the inventory is still not complete enough for the stated "existing incident surface set" claim. The survey was bounded to `src/` and `tests/`, which missed the provider-admin incident management UI and its mock incident API.

## Blocking Findings

### [P1] Inventory omits the provider-admin incident management surface

The revised proposal says the inventory was built from `grep -rln "incident" src/ tests/`. That scope misses first-class incident surfaces under `admin/provider`, including the UI that creates, updates, resolves, and displays incidents.

Evidence:

- `admin/provider/pages/StatusPage.tsx:3-8` describes the page as incident management and status-page functionality for `GET/POST /api/superadmin/incidents`, update, and resolve.
- `admin/provider/pages/StatusPage.tsx:41-63` defines the frontend incident/update/list response contract.
- `admin/provider/pages/StatusPage.tsx:136-221` calls the superadmin incident list/create/update/resolve endpoints.
- `admin/provider/pages/StatusPage.tsx:232-433` renders active/resolved incidents and create/update modals.
- `admin/provider/index.tsx:40,166` imports and mounts `StatusPageManagement` at `/status`.
- `admin/provider/layouts/ProviderLayout.tsx` includes the Status Page nav item with "Incident management" description.
- `admin/provider/mocks/handlers/incidents.ts:10-48` implements mock handlers for list/create/update/resolve incident endpoints.
- `admin/provider/mocks/fixtures/incidents.ts:6-35`, `admin/provider/mocks/store.ts:15,28,46`, and `admin/provider/mocks/plugin.ts:17,33` wire incident fixtures and handlers into the mock provider API.

Risk / impact:

- IR-0 is supposed to prevent the framework from creating parallel incident concepts. The provider UI and mock API are already a parallel contract surface if they are omitted from the boundary map.
- Future `::incident-update`, status-page draft, or DELIB-linkage work can update backend repository/API surfaces while leaving the provider status page and mock contract stale.
- The out-of-scope table excludes E2E live tests that exercise this UI, but it does not identify the underlying UI and mock surfaces at all.

Recommended action:

- Expand the survey scope beyond `src/` and `tests/` to include `admin/provider` incident references.
- Add in-scope rows for the provider status page component, route/nav registration, mock incident handlers, mock fixture/store/plugin wiring, and the E2E live provider tests that validate the UI.
- If any of these are intentionally deferred, place them in an explicit out-of-scope/deferred category with a reason tied to IR-0 scope.

### [P2] Backend API model and import-contract surfaces are under-specified

The backend inventory now names endpoint functions and runtime wiring, but several contract surfaces are either outside the cited line spans or only partially accounted for.

Evidence:

- `src/multi_tenant/superadmin_api/_operations.py:34-83` defines `IncidentUpdateModel`, `IncidentModel`, `IncidentListResponse`, `CreateIncidentRequest`, and `AddIncidentUpdateRequest`; row B1 starts at line 114, so it excludes the API request/response model contract.
- `src/multi_tenant/superadmin_api/_operations.py:87-107` maps persistence documents into API models via `_incident_to_model`; row B1 also excludes that conversion surface.
- `src/multi_tenant/status_api.py:32-56` defines the public incident/status response models; row C1 starts at line 79, so it excludes the response contract used by `GET /api/status`.
- The out-of-scope import-contract row mentions `src/multi_tenant/superadmin_api/__init__.py` and `src/multi_tenant/repositories/__init__.py`, but `src/multi_tenant/repository.py:36,75` also re-exports `IncidentRepository`, and `tests/unit/test_code_quality_s132.py:447-457` explicitly verifies that barrel contract.
- `tests/security/test_superadmin_api_split.py:58,108,134` verifies incident-model import compatibility, `_operations` exposes `list_incidents`, and `_monolith` does not. That is at least an explicit deferred import/API split contract if not an in-scope boundary row.

Risk / impact:

- DELIB linkage may require model/serializer updates, not only repository and endpoint-function updates.
- Import/barrel compatibility can silently break downstream callers if it is not included or explicitly deferred.

Recommended action:

- Expand B1 to include `_operations.py:34-242`, or split response/request models and `_incident_to_model()` into their own API-contract row.
- Expand C1 to include `status_api.py:32-146`, or split public response models from the endpoint implementation.
- Add or explicitly defer `src/multi_tenant/repository.py`, `tests/unit/test_code_quality_s132.py`, and `tests/security/test_superadmin_api_split.py` in the import/API-split contract section.

## Non-Blocking Notes

- The seven backend categories requested in `-004` are now present.
- The row split for `tests/multi_tenant/test_incidents_api.py:181-538` and `549-795` is the right correction.
- The corrected rule 4 remains directionally sound: public status is a read projection, while mutation belongs to the superadmin operation layer or `IncidentRepository`.

## Verification

Static review only. I inspected the revised proposal, repeated incident-reference searches across Python source/tests, and expanded the survey to provider frontend TypeScript/TSX surfaces. No tests were run for this proposal review.

## Decision Needed From Owner

None.

