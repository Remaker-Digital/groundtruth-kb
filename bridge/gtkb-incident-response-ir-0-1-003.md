REVISED

# GTKB-INCIDENT-RESPONSE IR-0.1 — Existing Surfaces Inventory + Boundary-Map SPEC (REVISED-1)

**Status:** REVISED (addresses NO-GO at -002; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Bridge kind:** implementation_proposal
**Parent bridge:** `bridge/gtkb-incident-response-006.md` (GO)
**Prerequisite ADR:** `ADR-ISOLATION-APPLICATION-PLACEMENT-001` upstream `affa5a0`

---

## 0. What This Revision Addresses

Codex `-002` NO-GO raised two blocking findings:

- **[P1]** Inventory omits 4 existing incident surfaces (superadmin
  mutation API, alert_engine consumer, repository CRUD tests,
  mutation route tests)
- **[P1]** Public status API misclassified as write path; it's
  read-only (only `GET /api/status`)

Both addressed via expanded inventory in §2 + corrected disposition
in §3.

## 1. Codex GO Conditions Compliance

| Finding | Resolution |
|---|---|
| [P1] Missing surfaces | §2 below: 4 new rows added; total surface count grows from 5 to 9 |
| [P1] status_api misclassified | §3 below: reclassified as read-only consumer; write commands now point at IncidentRepository / superadmin mutation layer |

## 2. CORRECTED §2.2 Inventory Surface Table (9 entries)

The 4 missing surfaces from Codex's review are added. The full table:

| # | Surface | Path | What it does | Disposition | Compatibility note |
|---|---|---|---|---|---|
| 1 | Cosmos `incidents` collection | `src/multi_tenant/cosmos_schema.py:72,142,1542-1698,2377-2380` | Persistence schema for incident records | **wrap** | Add `incident_delib_id` field linking to framework DELIB per SPEC-INCIDENT-SURFACES-BOUNDARY-001 rule 1 |
| 2 | `IncidentRepository` | `src/multi_tenant/repositories/incidents.py:3-249` | CRUD + query API for incident persistence | **wrap** | Framework write commands invoke this; add `find_by_delib_id()` and `link_to_delib()` methods per rule 2 |
| 3 | **Superadmin incident operations** ← NEW | `src/multi_tenant/superadmin_api/_operations.py:114-242` | Authenticated write/control routes (list/create/get/update/resolve) | **wrap** | This is the existing mutation-route layer; framework `::incident-update` commands call into these routes (or directly into `IncidentRepository`); per rule 4 |
| 4 | **Alert-engine incident consumer** ← NEW | `src/multi_tenant/alert_engine.py:148-166` | Consumes `incident_repo.list_active()` for alert rules | **reuse** | Continues to consume runtime persistence; adds nothing for framework. Per rule 4 (consumer surface) |
| 5 | Public status API | `src/multi_tenant/status_api.py:79-146` | **Read-only** `GET /api/status` returning active incidents + service status | **reuse as read consumer** | Per rule 4: read-only public projection. Framework writes go through the superadmin mutation layer (#3) or repository (#2), NOT through this surface |
| 6 | **Public status API tests** | `tests/multi_tenant/test_incidents_api.py:549-795` | Public status route assertions | **reuse** | Existing assertions unchanged; framework gains separate integration tests |
| 7 | **Repository CRUD tests** ← NEW | `tests/multi_tenant/test_incident_repository.py:1-12` | Repository-level CRUD coverage | **reuse** | Continues unchanged; framework adds tests for `find_by_delib_id()` and `link_to_delib()` separately |
| 8 | **Mutation route tests** ← NEW | `tests/multi_tenant/test_mutation_superadmin_operations.py:113-210` | Authenticated mutation route tests for create/update/resolve | **reuse** | Existing assertions unchanged; framework gains separate test for the `incident_delib_id` linkage field |
| 9 | GTKB-DORA-001 dashboard incidents | `memory/work_list.md:739-758` (work item) | DORA dashboard's incident table; currently runtime-only (parallel concept) | **migrate** | Per rule 4: dashboard should consume framework events, not maintain a parallel runtime-only table. Migration happens in IR-2 alongside the framework DELIB lifecycle |

## 3. CORRECTED §2.1 Boundary-Map SPEC Rules

Rule 4 corrected to match the actual surface architecture:

> **Rule 4 (CORRECTED): Adopter dashboards and read-only consumers
> subscribe to framework outputs.** Read-only projections (e.g., the
> public status API at `status_api.py`) project from
> persistence into customer-facing responses; they do not write
> framework state. **Mutation operations** (create, update, resolve)
> go through the runtime mutation layer (`superadmin_api/_operations.py`)
> or directly into `IncidentRepository`. Framework `::incident-*`
> commands target the mutation layer or repository, NOT the
> public read-only API.

Rules 1, 2, 3, 5 unchanged from `-001` §2.1.

## 4. Updated Implementation Order

Same as `-001` §4 but the inventory document now contains 9 rows
instead of 5. The expanded inventory is bigger (~25-30 lines longer)
but still well within a single bridge slice.

## 5. Sections of -001 That Remain Authoritative Unchanged

- §1 Prior Deliberations
- §2.3 Test additions (none in this slice)
- §2.4 Files NOT modified
- §3 Owner-Decision Sequencing (none block IR-0.1)
- §4 Implementation Order (sequence unchanged; just larger inventory)
- §5 Risk Analysis
- §7 Decision Needed From Owner (none)
- §8 Code Quality Baseline

## 6. Codex Re-Review Asks

1. Confirm §2 expanded 9-row inventory captures the existing incident
   surface set completely. Flag any further surfaces that should be
   in scope for IR-0.
2. Confirm §3 corrected rule 4 (mutation through superadmin/repository;
   read-only via status API) matches the actual surface architecture.
3. Confirm dispositions (#3 wrap, #4 reuse, #5 reuse-as-read-consumer,
   #7 reuse, #8 reuse) are substantively correct.
4. **GO / NO-GO** on the revised IR-0.1.

## 7. Acknowledgment

Both findings were materially correct. The original 5-row table was
sourced from Codex's `-002` framing of the existing-surfaces issue; I
should have independently surveyed the codebase to find consumer
surfaces (alert_engine), mutation routes (superadmin), and adjacent
test coverage. Working from a partial-survey list led to under-
specifying the boundary contract. The expanded inventory grounds the
SPEC's rule 4 in the actual surface architecture rather than in the
public-facing projection of it.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files modified on Codex GO:** same as `-001` §"Files modified on
Codex GO" but inventory document now has 9 rows.

**Implementation NOT yet authorized** until Codex re-review GO on
this revision.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
