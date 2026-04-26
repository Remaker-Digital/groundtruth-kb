NO-GO

# GTKB-INCIDENT-RESPONSE IR-0.1 Revised Proposal Review

**Date:** 2026-04-26
**Reviewed proposal:** `bridge/gtkb-incident-response-ir-0-1-003.md`
**Prior review:** `bridge/gtkb-incident-response-ir-0-1-002.md`
**Mode:** Implementation proposal review
**Decision:** NO-GO

## Verdict

NO-GO. The revision fixes the original public-status write-path mistake and adds the four surfaces called out in `-002`, but its stated ask is to confirm that the inventory captures the existing incident surface set completely. A live static survey still finds material runtime wiring and verification surfaces outside the nine-row table.

## Blocking Finding

### [P1] Inventory still omits runtime wiring and adjacent verification surfaces

The revised table captures persistence, core repository behavior, superadmin operations, public status projection, alert-engine consumption, and a subset of tests. It does not yet capture the surfaces that wire those pieces into the running app or the tests/checks that enforce that wiring.

Evidence from static survey:

- `src/app/lifecycle.py:1229-1262` creates and passes `IncidentRepository` into superadmin API configuration.
- `src/app/lifecycle.py:1598-1603` configures `status_api` with an `IncidentRepository`.
- `src/app/lifecycle.py:1617-1634` configures the alert engine with an `IncidentRepository`.
- `src/app/routers.py:56` imports the status router, and `src/app/routers.py:106` mounts it.
- `src/multi_tenant/verification_runner.py:210` schedules the incident endpoint check, and `src/multi_tenant/verification_runner.py:511-513` checks `GET /api/superadmin/incidents`.
- `tests/multi_tenant/test_alert_engine.py:547-613` covers incident-count collection and alert-engine incident-repo configuration.
- `tests/multi_tenant/test_superadmin_api_endpoints.py:461-595` covers superadmin incident endpoint behavior.
- `tests/multi_tenant/test_incidents_api.py:181-538` covers the superadmin incident CRUD paths in the same file that row 6 currently narrows to public-status assertions at `549-795`.
- `tests/multi_tenant/test_repository_classes.py:90-142` covers `IncidentRepository` importability, method presence, async shape, and signatures.

Risk / impact:

- A boundary-map SPEC based on the current table can still miss where the incident repository is injected at runtime, where the public route is mounted, and where live verification asserts incident endpoint availability.
- Future framework work could update repository and operation surfaces while leaving lifecycle wiring, route registration, or live verification checks stale.
- Row 6 under-represents `tests/multi_tenant/test_incidents_api.py`; the file contains both superadmin CRUD coverage and public status coverage, not public status coverage only.

Recommended action:

- Revise the inventory into explicit categories: persistence schema/repository, mutation/control API, read projections/routes, runtime wiring/lifecycle, alert/telemetry consumers, verification/test surfaces, and DORA/dashboard backlog surface.
- Add rows, or explicit out-of-scope justification, for `src/app/lifecycle.py`, `src/app/routers.py`, `src/multi_tenant/verification_runner.py`, `tests/multi_tenant/test_alert_engine.py`, `tests/multi_tenant/test_superadmin_api_endpoints.py`, `tests/multi_tenant/test_repository_classes.py`, and the superadmin CRUD section of `tests/multi_tenant/test_incidents_api.py`.
- Correct row 6 to cover the whole relevant `tests/multi_tenant/test_incidents_api.py:181-795` span, or split that file into separate rows for superadmin CRUD tests and public-status tests.

## Non-Blocking Notes

- The corrected rule 4 is directionally right: public status is a read projection, while mutation belongs to the superadmin operation layer or `IncidentRepository`.
- Export and re-export surfaces such as `src/multi_tenant/superadmin_api/__init__.py` and repository package exports may be captured as a lower-priority import-surface category if the final inventory methodology treats import contracts as in scope.

## Verification

Static review only. I inspected the revised proposal and ran targeted repository searches across `src` and `tests/multi_tenant` for incident, status API, repository, lifecycle, router, alert-engine, and verification-runner references. No tests were run for this proposal review.

## Decision Needed From Owner

None.

