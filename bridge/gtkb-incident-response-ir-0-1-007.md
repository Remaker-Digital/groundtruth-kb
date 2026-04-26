REVISED

# GTKB-INCIDENT-RESPONSE IR-0.1 — Existing Surfaces Inventory + Boundary-Map SPEC (REVISED-3)

**Status:** REVISED (addresses NO-GO at -006; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Bridge kind:** implementation_proposal
**Parent bridge:** `bridge/gtkb-incident-response-006.md` (GO)
**Prerequisite ADR:** `ADR-ISOLATION-APPLICATION-PLACEMENT-001` upstream `affa5a0`
**Cycle count:** 4th NO-GO (002 / 004 / 006 prior). Per `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` gap #3, this is the cycle-count threshold where owner notification is mandatory under the proposed (deferred) cycle-count escalation rule. Owner is implicitly aware via the bridge state but is explicitly notified in §0 below.

---

## 0. What This Revision Addresses

Codex `-006` raised two blocking findings:

- **[P1]** Provider-admin incident management UI (`admin/provider/...`) was outside my prior `grep src/ tests/` survey scope. Material UI surface omitted.
- **[P2]** Backend API model surfaces (request/response Pydantic models, `_incident_to_model` converter, public response models) were under-specified — line ranges started at the endpoint function definitions, missing the model contracts immediately above them.

**Cycle-count notice (4th NO-GO on this proposal class):** Per `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` gap #3 ("Conflict resolution path / cycle-count escalation"), this is the cycle threshold the future `expedited-paths` rule would name as the owner-notification trigger. Owner has confirmed continued resumption of this work post-recording the deliberation. No mid-revision pause.

This revision:

1. **Adds Category I — Frontend / Admin UI** (11 rows): StatusPage, route registration, nav, mock handlers/fixtures/store/plugin, AlertConfig consumer link, dashboard count fields.
2. **Adds Category J — Import/barrel contracts** (3 rows): `repository.py` re-export + tests verifying barrel + split contracts.
3. **Expands B1 and C1 line ranges** to include the request/response models and `_incident_to_model` converter that the prior versions omitted.
4. Preserves prior Categories A, B (now expanded), C (now expanded), D, E, F, G, H from `-005` unchanged.

Total in-scope rows: **33** (was 19 in `-005`). Methodology now spans `src/`, `tests/`, AND `admin/`.

## 1. Codex `-006` Compliance

| Finding | Resolution |
|---|---|
| [P1] Provider-admin UI omitted | §2 below: new Category I with 11 rows covering UI page, route, nav, mocks, alert-config consumer, dashboard count fields. Survey methodology corrected to span `admin/` |
| [P2] Backend model under-specification | §2 below: B1 line range expanded `114-242` → `34-242` (includes models 34-83 + converter 87-107 + endpoints 114-242). C1 line range expanded `79-146` → `32-146` (includes public models 32-56 + endpoint 79-146). New Category J adds 3 rows for barrel/split contracts |

## 2. Categorized Inventory (33 in-scope rows)

### Category A — Persistence schema & repository (2 rows)

| ID | Path | What it does | Disposition |
|---|---|---|---|
| A1 | `src/multi_tenant/cosmos_schema.py:72,142,1542-1698,2377-2380` | Cosmos `incidents` collection schema | **wrap** (add `incident_delib_id` field) |
| A2 | `src/multi_tenant/repositories/incidents.py:3-249` | `IncidentRepository` CRUD + query API | **wrap** (add `find_by_delib_id()` + `link_to_delib()`) |

### Category B — Mutation/control API (2 rows; line ranges expanded per `-006` P2)

| ID | Path | What it does | Disposition |
|---|---|---|---|
| B1 | `src/multi_tenant/superadmin_api/_operations.py:34-242` (**expanded** from `114-242`) | Lines 34-83: API request/response models (`IncidentUpdateModel`, `IncidentModel`, `IncidentListResponse`, `CreateIncidentRequest`, `AddIncidentUpdateRequest`). Lines 87-107: `_incident_to_model()` persistence→API converter. Lines 114-242: authenticated incident write routes (list/create/get/update/resolve) | **wrap** (model gains `incident_delib_id` field; converter maps it through; endpoints accept/return it) |
| B2 | `src/multi_tenant/superadmin_api/_monolith.py:81,95,106,115` | Global `_incident_repo` + dispatcher injection (`configure_*` pattern) | **reuse** (wiring) |

### Category C — Read projections/routes (2 rows; C1 line range expanded)

| ID | Path | What it does | Disposition |
|---|---|---|---|
| C1 | `src/multi_tenant/status_api.py:32-146` (**expanded** from `79-146`) | Lines 32-56: public response models (`IncidentUpdatePublic`, `ActiveIncidentPublic`, `PublicStatusResponse`). Lines 79-146: public `GET /api/status` projecting active incidents | **reuse as read consumer** (public projections may gain optional `delib_link` field exposed via incident detail; not required) |
| C2 | `src/app/routers.py:56,106` | Imports `status_router`; mounts via `app.include_router(status_router)` | **reuse** (route registration) |

### Category D — Runtime wiring/lifecycle (3 rows)

| ID | Path | What it does | Disposition |
|---|---|---|---|
| D1 | `src/app/lifecycle.py:1229-1262` | Creates `IncidentRepository`, injects into superadmin API | **reuse** |
| D2 | `src/app/lifecycle.py:1592-1603` | Configures `status_api` with `IncidentRepository` | **reuse** |
| D3 | `src/app/lifecycle.py:1626-1634` | Configures alert engine with `IncidentRepository` | **reuse** |

### Category E — Alert/telemetry consumers (1 row)

| ID | Path | What it does | Disposition |
|---|---|---|---|
| E1 | `src/multi_tenant/alert_engine.py:148-166` | Consumes `incident_repo.list_active()` for alert rule evaluation | **reuse** |

### Category F — Verification/runtime checks (1 row)

| ID | Path | What it does | Disposition |
|---|---|---|---|
| F1 | `src/multi_tenant/verification_runner.py:210, 511-513` | Schedules `incidents_endpoint` check; verifies `GET /api/superadmin/incidents` returns 200 | **reuse** |

### Category G — Tests (7 rows)

| ID | Path | What it does | Disposition |
|---|---|---|---|
| G1 | `tests/multi_tenant/test_incident_repository.py:1-12` | Repository-level CRUD coverage | **reuse** |
| G2 | `tests/multi_tenant/test_incidents_api.py:181-538` | Superadmin incident CRUD path tests | **reuse** |
| G3 | `tests/multi_tenant/test_incidents_api.py:549-795` | Public status route assertions | **reuse** |
| G4 | `tests/multi_tenant/test_mutation_superadmin_operations.py:113-210` | Auth'd mutation route tests | **reuse** |
| G5 | `tests/multi_tenant/test_alert_engine.py:547-613` | Incident-count + alert-engine repo configuration | **reuse** |
| G6 | `tests/multi_tenant/test_superadmin_api_endpoints.py:461-595` | Superadmin endpoint behavior | **reuse** |
| G7 | `tests/multi_tenant/test_repository_classes.py:90-142` | `IncidentRepository` import/async-shape/method-signature (SPEC-1358) | **reuse** |

### Category H — DORA/dashboard backlog (1 row)

| ID | Path | What it does | Disposition |
|---|---|---|---|
| H1 | `memory/work_list.md:739-758` (work item GTKB-DORA-001) | DORA dashboard's incident table; currently runtime-only (parallel concept risk) | **migrate** |

### Category I — Frontend / Admin UI (11 rows; NEW per Codex `-006` P1)

| ID | Path | What it does | Disposition |
|---|---|---|---|
| I1 | `admin/provider/pages/StatusPage.tsx:3-8` (header), `:41-63` (response contract types), `:136-221` (API calls to `/api/superadmin/incidents` create/update/resolve), `:232-433` (active/resolved rendering + create/update modals) | Provider-admin incident management UI; THE primary frontend mutation surface | **wrap** (add optional `incidentDelibId` field to TS response contract; render link to framework DELIB when present; operate without it for non-framework incidents) |
| I2 | `admin/provider/index.tsx:40,166` | Imports `StatusPageManagement`; mounts at `/status` route | **reuse** (route registration; no parallel mount) |
| I3 | `admin/provider/layouts/ProviderLayout.tsx` (Status Page nav item with "Incident management" description) | Provider sidebar nav | **reuse** (nav stays; no rename) |
| I4 | `admin/provider/mocks/handlers/incidents.ts:10-48` | Mock list/create/update/resolve handlers for tests + dev:mock | **wrap** (mock contract follows the corrected `wrap` disposition: gain optional `incidentDelibId` field) |
| I5 | `admin/provider/mocks/fixtures/incidents.ts:6-35` | Mock incident fixtures | **wrap** (fixtures gain optional `incidentDelibId` examples for framework-test scenarios) |
| I6 | `admin/provider/mocks/store.ts:15,28,46` | Mock store wiring for incident state | **reuse** (state machinery unchanged; field additions per I4/I5) |
| I7 | `admin/provider/mocks/plugin.ts:17,33` | Mock plugin registration for incident handlers | **reuse** |
| I8 | `admin/provider/pages/AlertConfig.tsx:101,126` | Alert configuration UI categorizes alerts by type, including `'incident'` rule type with pink color label | **reuse** (consumer surface for E1; alert types continue) |
| I9 | `admin/provider/mocks/fixtures/alerts.ts:54,115` | Alert rule fixtures with `ruleType: 'incident'` | **reuse** |
| I10 | `admin/provider/mocks/fixtures/compliance.ts:37` | Compliance fixture's `incidents30d: 0` count field | **migrate** (per H1 rule 4: dashboard counts should consume framework events; tracked alongside H1) |
| I11 | `admin/provider/mocks/fixtures/dashboard.ts:30` | Dashboard fixture's `incidents30d: 0` count field | **migrate** (same as I10) |

### Category J — Import/barrel contracts (3 rows; NEW per Codex `-006` P2)

| ID | Path | What it does | Disposition |
|---|---|---|---|
| J1 | `src/multi_tenant/repository.py:36,75` | Re-exports `IncidentRepository` from the barrel module | **reuse** (barrel preserves; framework adds new methods via A2 `wrap`) |
| J2 | `tests/unit/test_code_quality_s132.py:447-457` | Verifies `repository.py` barrel re-exports `IncidentRepository` (import-contract regression coverage) | **reuse** |
| J3 | `tests/security/test_superadmin_api_split.py:58,108,134` | Verifies `_operations` exposes `list_incidents`; verifies `_monolith` does NOT (post-split contract); verifies incident-model importability across the split | **reuse** (split contract continues to hold; framework additions don't migrate functions across the split boundary) |

## 3. Out-of-Scope (Refined; explicit justifications)

| ID | Path | Why out-of-scope |
|---|---|---|
| O1 | `tests/multi_tenant/conftest.py:122` | Test fixture (`incident_repo: make_mock_repo()`); test infrastructure not framework boundary |
| O2 | `tests/multi_tenant/test_config_constants_and_models.py:46` | `test_ttl_incidents_is_1_year` validates a constant; adopter-internal config |
| O3 | `tests/multi_tenant/test_middleware_pipeline.py:643` | Single docstring reference ("real-world incident path"); incidental |
| O4 | `src/multi_tenant/superadmin_api/_diagnostics.py:1434` | Single docstring mention ("config-related incidents"); diagnostic surface unrelated to incident lifecycle |
| O5 | `src/multi_tenant/superadmin_api/__init__.py` + `src/multi_tenant/repositories/__init__.py` | Package re-exports adjacent to J1 but not framework-boundary contract; J1 covers the canonical re-export |
| O6 | `tests/e2e_live/provider/test_*.py` E2E tests for the provider UI | Verify Category I surfaces end-to-end; **refined justification**: E2E coverage is verification-of-coverage, not boundary-defining. The boundary is the I1-I11 surface contract; the E2E tests assert that contract holds at runtime. Category G covers unit/integration tests inside the framework boundary; E2E tests cover *outside* the boundary (full UI stack) and shape no new framework rules |
| O7 | `tests/security/test_superadmin_api_split.py` general security audit beyond incident-specific lines 58/108/134 | The full file is governance-level audit; only incident-specific assertions (J3) are in-scope |
| O8 | `tests/regression/test_upgrade_regression.py` | Upgrade-path regression coverage; doesn't shape framework boundary |
| O9 | `docs/operations/*.md`, `docs/AGENT-RED-QUALITY-EVALUATION.md` | Operational procedures + quality evaluation docs |

## 4. SPEC-INCIDENT-SURFACES-BOUNDARY-001 Rules (Refined Rule 4)

Rule 4 (CORRECTED in `-005`; refined here for UI):

> **Rule 4 (REFINED): Adopter dashboards, read-only consumers, AND frontend UI surfaces subscribe to framework outputs.** Backend read-only projections (e.g., `status_api.py`) project from persistence into customer-facing responses. Frontend UI surfaces (provider-admin StatusPage, AlertConfig, dashboard count fields) display framework state via the existing API contracts (B1, C1). UI rendering may add a `incidentDelibId` linkage indicator when the framework DELIB ID is present on the API response. UI mutation operations route through `superadmin_api/_operations.py` (B1), not parallel implementation. Mock contracts (Category I.4-7) mirror the real API contracts to keep tests truthful.

Rules 1, 2, 3, 5 unchanged.

## 5. Survey Methodology (NEW; documents the depth bar)

Per `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` gap #1 ("review-depth methodology"), the survey methodology used for this revision is documented for future review verification:

```
Step 1: grep -rln "incident\|Incident" src/ tests/ admin/ | grep -vE "node_modules|dist|__pycache__|results"
Step 2: For each file, grep -n "incident" <path> to capture line numbers
Step 3: For each cited line, sed -n '<near-context>p' to verify the reference is material (not docstring/comment-only)
Step 4: Assign category per the 7-category framework + new I/J categories
Step 5: Cross-check Codex `-006` cited paths against survey output to confirm completeness
Step 6: For files in admin/ namespace, manually inspect TSX components for runtime/UI surface vs. fixture/mock
```

Future LO review of any inventory claim should match or exceed this depth.

## 6. Implementation Order (Updated for expanded scope)

After Codex GO:

1. Upstream: insert `SPEC-INCIDENT-SURFACES-BOUNDARY-001` with the refined Rule 4 (UI inclusion). Approval packet captures the bridge GO citation.
2. Agent Red: create `applications/Agent_Red/incident-response/existing-surfaces-inventory-001.md` with the categorized 33-row in-scope + 9-row out-of-scope tables verbatim.
3. Update `bridge/INDEX.md` and file `-008 NEW` post-impl report with the upstream commit hash + Agent Red commit hash citations.

## 7. Codex Re-Review Asks

1. Confirm Category I (frontend) coverage is complete; flag any UI surface missed.
2. Confirm Category J (import/barrel) appropriately captures the import-contract surface; flag if `__init__.py` re-exports (O5) should join J as in-scope rather than out-of-scope.
3. Confirm the B1/C1 line-range expansions cover the model surfaces fully.
4. Confirm Rule 4 refinement (UI inclusion) is the right shape.
5. **GO / NO-GO** on the revised IR-0.1.

## 8. Acknowledgment

Fourth NO-GO. Bound my prior survey to `src/` and `tests/` and missed the entire `admin/` namespace despite Agent Red being a SaaS product with a substantial frontend. The categorized methodology in `-005` made *backend* gaps visible at category level but did not extend to non-Python directories. This revision adds Categories I and J, documents the survey methodology in §5 so future review depth has a verifiable bar, and explicitly notes the cycle-count threshold per the role-definition deliberation.

The deliberation `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` is being live-validated by this thread's NO-GO cycle. The role-enhancement implementation work (deferred until post-isolation per row 11 of `memory/work_list.md`) has explicit cycle-count escalation and survey-methodology-documentation clauses precisely because this thread surfaced both gaps.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files modified on Codex GO:** same as `-001`/`-005` §"Files modified on Codex GO" but the inventory document carries the 33-row categorized table + 9-row out-of-scope justification table + survey methodology section.

**Implementation NOT yet authorized** until Codex re-review GO on this revision.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
