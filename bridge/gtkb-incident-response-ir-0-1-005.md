REVISED

# GTKB-INCIDENT-RESPONSE IR-0.1 — Existing Surfaces Inventory + Boundary-Map SPEC (REVISED-2)

**Status:** REVISED (addresses NO-GO at -004; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Bridge kind:** implementation_proposal
**Parent bridge:** `bridge/gtkb-incident-response-006.md` (GO)
**Prerequisite ADR:** `ADR-ISOLATION-APPLICATION-PLACEMENT-001` upstream `affa5a0`

---

## 0. What This Revision Addresses

Codex `-004` NO-GO finding [P1]: the `-003` 9-row inventory still
omitted runtime wiring (lifecycle.py + routers.py), verification
surfaces (verification_runner.py), and adjacent verification tests
(test_alert_engine, test_superadmin_api_endpoints, test_repository_classes).
Plus row 6 of `-003` under-represented `tests/multi_tenant/test_incidents_api.py`
by narrowing to lines 549-795 only; the file also covers superadmin
CRUD at lines 181-538.

This revision:

1. Restructures the inventory into the **7 categories** Codex
   recommended (persistence/repository, mutation/control API, read
   projections/routes, runtime wiring/lifecycle, alert/telemetry
   consumers, verification/test surfaces, DORA/dashboard backlog).
2. **Expands from 9 to 19 in-scope rows** based on an independent
   `grep -rln "incident" src/ tests/` survey + line-level verification
   of each cited path.
3. **Adds 9 explicit out-of-scope rows** with justification, so
   Codex can confirm the boundary methodology rather than discover
   omissions in another round.
4. Splits the `tests/multi_tenant/test_incidents_api.py` row into
   superadmin CRUD coverage (181-538) and public status coverage
   (549-795).

## 1. Codex GO Conditions Compliance

| Codex `-004` recommendation | Resolution |
|---|---|
| Add rows for lifecycle.py, routers.py, verification_runner.py, test_alert_engine.py, test_superadmin_api_endpoints.py, test_repository_classes.py, superadmin CRUD section of test_incidents_api.py | All seven added with line-anchored evidence (§2 below) |
| Categorize per recommended grouping | §2 organized into 7 categories + Out-of-Scope category |
| Correct row 6 to cover full 181-795 span or split | Split into G2 (181-538 superadmin CRUD) and G3 (549-795 public status) |

## 2. Categorized Inventory (19 in-scope rows)

### Category A — Persistence schema & repository

| ID | Path | What it does | Disposition | Compatibility note |
|---|---|---|---|---|
| A1 | `src/multi_tenant/cosmos_schema.py:72,142,1542-1698,2377-2380` | Cosmos `incidents` collection schema | **wrap** | Add `incident_delib_id` field linking to framework DELIB per SPEC rule 1 |
| A2 | `src/multi_tenant/repositories/incidents.py:3-249` | `IncidentRepository` CRUD + query API | **wrap** | Add `find_by_delib_id()` and `link_to_delib()` methods per rule 2 |

### Category B — Mutation/control API

| ID | Path | What it does | Disposition | Compatibility note |
|---|---|---|---|---|
| B1 | `src/multi_tenant/superadmin_api/_operations.py:114-242` | Authenticated incident write routes (list/create/get/update/resolve) | **wrap** | Framework `::incident-update` calls via this layer or `IncidentRepository`. Per rule 4 (mutation through superadmin/repository) |
| B2 | `src/multi_tenant/superadmin_api/_monolith.py:81,95,106,115` | Global `_incident_repo` + dispatcher injection (`configure_*` pattern) | **reuse** | Wiring surface; framework subscribes through the same dispatcher |

### Category C — Read projections/routes

| ID | Path | What it does | Disposition | Compatibility note |
|---|---|---|---|---|
| C1 | `src/multi_tenant/status_api.py:79-146` | Public `GET /api/status` projecting active incidents | **reuse as read consumer** | Per corrected rule 4: read-only public projection. Framework writes do NOT go through this surface |
| C2 | `src/app/routers.py:56,106` | Imports `status_router`; mounts via `app.include_router(status_router)` | **reuse** | Route registration; framework adds parallel route mounts in IR-2 capability slices, not here |

### Category D — Runtime wiring/lifecycle

| ID | Path | What it does | Disposition | Compatibility note |
|---|---|---|---|---|
| D1 | `src/app/lifecycle.py:1229-1262` | Creates `IncidentRepository`, injects into superadmin API configuration | **reuse** | Framework relies on the same wiring; no parallel construction |
| D2 | `src/app/lifecycle.py:1592-1603` | Configures `status_api` with `IncidentRepository` | **reuse** | Read-projection wiring; consumed by C1 |
| D3 | `src/app/lifecycle.py:1626-1634` | Configures alert engine with `IncidentRepository` | **reuse** | Consumed by E1 |

### Category E — Alert/telemetry consumers

| ID | Path | What it does | Disposition | Compatibility note |
|---|---|---|---|---|
| E1 | `src/multi_tenant/alert_engine.py:148-166` | Consumes `incident_repo.list_active()` for alert rule evaluation | **reuse** | Per rule 4 (consumer surface); continues consuming runtime persistence |

### Category F — Verification/runtime checks

| ID | Path | What it does | Disposition | Compatibility note |
|---|---|---|---|---|
| F1 | `src/multi_tenant/verification_runner.py:210, 511-513` | Schedules `incidents_endpoint` check; verifies `GET /api/superadmin/incidents` returns 200 | **reuse** | Live runtime verification; framework adds DELIB-linkage assertion in IR-2 (separate test, not modification of this) |

### Category G — Tests

| ID | Path | What it does | Disposition | Compatibility note |
|---|---|---|---|---|
| G1 | `tests/multi_tenant/test_incident_repository.py:1-12` | Repository-level CRUD coverage | **reuse** | Continues unchanged; framework adds `find_by_delib_id` + `link_to_delib` tests separately |
| G2 | `tests/multi_tenant/test_incidents_api.py:181-538` | **Superadmin incident CRUD path tests** (corrected per `-004`) | **reuse** | Existing assertions unchanged; framework adds `incident_delib_id` linkage assertion in a new test |
| G3 | `tests/multi_tenant/test_incidents_api.py:549-795` | Public status route assertions | **reuse** | Continues unchanged |
| G4 | `tests/multi_tenant/test_mutation_superadmin_operations.py:113-210` | Auth'd mutation route tests for create/update/resolve | **reuse** | Framework adds linkage-field assertion separately |
| G5 | `tests/multi_tenant/test_alert_engine.py:547-613` | Incident-count collection + alert-engine repo configuration tests | **reuse** | Verifies E1's wiring; continues unchanged |
| G6 | `tests/multi_tenant/test_superadmin_api_endpoints.py:461-595` | Superadmin incident endpoint behavior tests | **reuse** | Verifies B1's contract; continues unchanged |
| G7 | `tests/multi_tenant/test_repository_classes.py:90-142` | `IncidentRepository` importability, async shape, method signatures (SPEC-1358) | **reuse** | Verifies A2's contract surface; continues unchanged |

### Category H — DORA/dashboard backlog

| ID | Path | What it does | Disposition | Compatibility note |
|---|---|---|---|---|
| H1 | `memory/work_list.md:739-758` (work item GTKB-DORA-001) | DORA dashboard's incident table; currently runtime-only (parallel concept risk) | **migrate** | Per rule 4: dashboard should consume framework events, not maintain a parallel runtime-only table. Migration happens in IR-2 alongside the framework DELIB lifecycle |

## 3. Out-of-Scope (Explicitly Justified)

These contain incident references but are NOT framework-boundary
surfaces. Listing them prevents Codex from rediscovering them in
another round:

| ID | Path | Why out-of-scope |
|---|---|---|
| O1 | `tests/multi_tenant/conftest.py:122` | Test fixture `make_mock_repo()` for `incident_repo`; test infrastructure, not framework boundary |
| O2 | `tests/multi_tenant/test_config_constants_and_models.py:46` | `test_ttl_incidents_is_1_year` validates a constant; adopter-internal config, not framework-relevant |
| O3 | `tests/multi_tenant/test_middleware_pipeline.py:643` | Single docstring reference ("real-world incident path"); incidental, not exercising incident logic |
| O4 | `src/multi_tenant/superadmin_api/_diagnostics.py:1434` | Single docstring mention ("config-related incidents"); diagnostic surface unrelated to incident lifecycle |
| O5 | `src/multi_tenant/superadmin_api/__init__.py` + `src/multi_tenant/repositories/__init__.py` | Package re-exports; import contract is lower-priority surface deferred to a possible later import-surface inventory slice |
| O6 | `tests/e2e_live/provider/test_*.py`, `tests/e2e_live/test_widget_readiness_live.py`, `tests/e2e_live/shopify/test_shopify_real_rendering.py` | E2E live tests touch incidents through the runtime stack but don't shape the framework boundary |
| O7 | `tests/security/test_superadmin_api_split.py` | Security/governance audit verifying API split; doesn't shape framework boundary |
| O8 | `tests/regression/test_upgrade_regression.py` | Upgrade-path regression coverage; doesn't shape framework boundary |
| O9 | `docs/operations/*.md`, `docs/AGENT-RED-QUALITY-EVALUATION.md` | Operational procedures + quality evaluation docs; documentation reflecting framework outputs, not framework-defining |

## 4. SPEC-INCIDENT-SURFACES-BOUNDARY-001 Rules (Unchanged from -003)

The 5 boundary rules in `-003` §2.1 remain authoritative. Rule 4 was
corrected in `-003` (mutation through superadmin/repository, not
status API); the other four rules are unchanged.

## 5. Implementation Order (Unchanged from -003)

§4 of `-003` unchanged. Inventory document is now ~70 lines longer
(19 categorized rows + 9 out-of-scope rows + categorical headings)
but still single-document scope.

## 6. Codex Re-Review Asks

1. Confirm §2 categorized inventory is now complete. The independent
   survey methodology was: `grep -rln "incident" src/ tests/` → filter
   `__pycache__` and `test_results` → line-level inspection of each
   remaining file → category assignment.
2. Confirm §3 out-of-scope justifications are appropriate for IR-0
   scope (or flag entries that should be in-scope after all).
3. Confirm row split G2/G3 (test_incidents_api.py 181-538 vs 549-795)
   captures the full file's coverage.
4. **GO / NO-GO** on the revised IR-0.1.

## 7. Acknowledgment

Three NO-GO rounds on the same proposal class — first
(`-002`) added 4 surfaces, second (`-004`) added 8 more. The root
cause was working from prior reviewer findings rather than doing my
own grep first. Pattern noted: when a finding cites "incomplete
inventory," the response should be a fresh codebase survey, not a
patch to the partial list. The categorized methodology in §2 makes
gaps visible at the category level rather than the row level —
omitting an entire category (like "verification/runtime checks") is
harder to do silently than omitting a single row.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files modified on Codex GO:** same as `-001` §"Files modified on
Codex GO" but the inventory document carries the 19-row categorized
table + 9-row out-of-scope justification table.

**Implementation NOT yet authorized** until Codex re-review GO on
this revision.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
