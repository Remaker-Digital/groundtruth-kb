# Agent Red — Existing Incident Surfaces Inventory

**Status:** v001 (initial inventory)
**Date:** 2026-04-26 (S310)
**Authority:** `bridge/gtkb-incident-response-ir-0-1-008.md` (Codex GO; 4-cycle inventory revision)
**Upstream SPEC:** `SPEC-INCIDENT-SURFACES-BOUNDARY-001` at upstream `groundtruth-kb` commit `3b5a527c0c4493cc0e39cbc3389a341154ca8f59` (`docs/architecture/specs/SPEC-INCIDENT-SURFACES-BOUNDARY-001.md`)
**ADR placement:** This document lives at `<gt-kb-root>/applications/Agent_Red/...` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` upstream commit `affa5a0567a64f79bb4c5aae891889d4af50a72a`

---

## 0. Purpose

Map every existing Agent Red incident-related surface against the boundary rules in `SPEC-INCIDENT-SURFACES-BOUNDARY-001` so future framework capability slices (`::incident-update`, postmortem skill, fast-path mitigation registry, etc.) do not create parallel concepts.

## 1. Methodology

The survey scope is `src/`, `tests/`, AND `admin/` namespaces. Procedure documented in `bridge/gtkb-incident-response-ir-0-1-007.md` §5; reproduced here:

```
Step 1: grep -rln "incident\|Incident" src/ tests/ admin/ | grep -vE "node_modules|dist|__pycache__|results"
Step 2: For each file, grep -n "incident" <path> to capture line numbers
Step 3: For each cited line, sed -n '<near-context>p' to verify the reference is material
Step 4: Assign category per the 7-category framework + I/J for UI and barrel contracts
Step 5: Cross-check Codex review findings against survey output
Step 6: For files in admin/ namespace, manually inspect TSX components for runtime/UI surface vs. fixture/mock
```

## 2. Categorized In-Scope Inventory (33 rows)

The full categorized table with line citations and dispositions is in `bridge/gtkb-incident-response-ir-0-1-007.md` §2 (REVISED-3 of the proposal; GO'd at `-008`). Categories:

| Category | Rows | Subject |
|---|---:|---|
| A | 2 | Persistence schema & repository |
| B | 2 | Mutation/control API (request/response models + endpoints + dispatcher) |
| C | 2 | Read projections/routes (public response models + endpoint + router mount) |
| D | 3 | Runtime wiring/lifecycle (lifecycle.py creates IncidentRepository for superadmin, status_api, alert_engine) |
| E | 1 | Alert/telemetry consumers (alert_engine.list_active) |
| F | 1 | Verification/runtime checks (verification_runner incidents_endpoint) |
| G | 7 | Tests (repository, superadmin CRUD, public status, mutation auth, alert engine, superadmin endpoints, repository class signature) |
| H | 1 | DORA/dashboard backlog (GTKB-DORA-001 incident table; **migrate** disposition) |
| I | 11 | **Frontend / Admin UI** (provider StatusPage, route/nav, mock handlers/fixtures/store/plugin, AlertConfig consumer, dashboard count fields) |
| J | 3 | **Import/barrel contracts** (repository.py re-export + barrel/split contract tests) |
| **Total** | **33** | **In-scope under SPEC rules 1-5** |

## 3. Out-of-Scope (9 rows; explicit justifications)

Per `bridge/gtkb-incident-response-ir-0-1-007.md` §3:

- **O1**: `tests/multi_tenant/conftest.py:122` — test fixture infrastructure
- **O2**: `tests/multi_tenant/test_config_constants_and_models.py:46` — adopter-internal constant
- **O3**: `tests/multi_tenant/test_middleware_pipeline.py:643` — incidental docstring reference
- **O4**: `src/multi_tenant/superadmin_api/_diagnostics.py:1434` — incidental docstring mention
- **O5**: `__init__.py` re-exports (covered by Category J canonical re-export)
- **O6**: `tests/e2e_live/provider/test_*.py` — verification of in-scope I1-I11 contracts; not boundary-defining
- **O7**: `tests/security/test_superadmin_api_split.py` general security audit beyond J3 lines
- **O8**: `tests/regression/test_upgrade_regression.py` — upgrade-path regression
- **O9**: `docs/operations/*.md`, `docs/AGENT-RED-QUALITY-EVALUATION.md` — operational documentation

## 4. Boundary Rule Applications

How the SPEC's 5 rules apply per category:

| Rule | Categories applied |
|---|---|
| Rule 1 (framework owns lifecycle) | A1, A2 (`incident_delib_id` field) |
| Rule 2 (adopter owns persistence) | A1, A2, B1, B2, D1-D3 (no framework rewrite) |
| Rule 3 (framework provides postmortem assembler) | Future framework code reads via A2, F1 — does not modify B/C/D |
| Rule 4 (consumers subscribe to framework outputs) | C1, C2, E1, H1, I1-I11 (mutation through B1, not C1) |
| Rule 5 (DELIB linkage compatibility) | A1 (cosmos field), A2 (repo methods), B1 (API models), I1, I4, I5 (TS contract + mocks) |

## 5. Disposition Summary

- **wrap** (8): A1, A2, B1, I1, I4, I5 (gain DELIB-linkage field; otherwise unchanged)
- **reuse** (22): B2, C1, C2, D1-D3, E1, F1, G1-G7, I2, I3, I6, I7, I8, I9, J1, J2, J3 (no framework changes; existing contracts continue)
- **migrate** (3): H1, I10, I11 (dashboard count fields move from runtime-only to framework-event consumers; tracked alongside H1)

Total: 8 + 22 + 3 = 33 in-scope rows.

## 6. Future Work

- Framework capability slices (IR-1 through IR-6) implement against the SPEC rules
- Phase 9 productization adds adopter conformance test in `tests/adopter/`
- Migration of H1, I10, I11 happens in IR-2 alongside framework DELIB lifecycle

## 7. Provenance

| Artifact | Reference |
|---|---|
| Bridge proposal chain | `bridge/gtkb-incident-response-ir-0-1-{001..008}.md` (4 cycles) |
| Codex GO | `bridge/gtkb-incident-response-ir-0-1-008.md` |
| Upstream SPEC | `groundtruth-kb` commit `3b5a527c0c4493cc0e39cbc3389a341154ca8f59` |
| Parent program | `bridge/gtkb-incident-response-006.md` (GO) |
| ADR enabling this path | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` upstream commit `affa5a0567a64f79bb4c5aae891889d4af50a72a` |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
