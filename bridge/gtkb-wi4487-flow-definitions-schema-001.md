NEW

# WI-4487 Flow Definitions Schema Proposal

bridge_kind: prime_proposal
Document: gtkb-wi4487-flow-definitions-schema
Version: 001
Author: Codex Prime Builder (interactive PB override)
Date: 2026-06-13 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebe11-2c38-7f42-9383-81db49281ddd
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4487

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_db.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Create the Phase-0 TAFE `flow_definitions` MemBase schema and DB helper surface
for `WI-4487`. The table will be append-only/versioned and will hold typed flow
templates for the later implementation, operation, remediation, deliberation,
and report flows without making any flow type authoritative yet.

This slice is intentionally substrate-only: it adds the schema, current-view
read surface, focused KnowledgeDB helper methods, and regression tests. It does
not seed the five canonical flow definitions, does not create runtime flow
tables, does not add `gt flow` CLI commands, does not run a pilot, and does not
change bridge or `INDEX.md` authority.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — requires canonical typed artifact-flow state to move toward MemBase-backed dedicated services while bridge markdown remains compatibility/presentation until governed cutover.
- `SPEC-TAFE-R1` — requires controlled, auditable, extensible reviewed-task flows and typed flow definitions that can grow without re-architecting the substrate.
- `SPEC-TAFE-R7` — requires canonical typed artifact-flow data and services to be accessed through dedicated DB/CLI/service surfaces, with MemBase as canonical for flow state.
- `SPEC-TAFE-R6` — constrains the schema direction toward auditability and later telemetry, so this table must leave room for stage metadata and future runtime tables without claiming to implement telemetry in this slice.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — implementation remains bridge-mediated and `bridge/INDEX.md` remains the canonical coordination state.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal carries PAUTH, project, work item, and concrete `target_paths` metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal links governing specifications and maps verification to each.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must carry this mapping forward with executed test, lint, and format evidence.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the active Phase-0 PAUTH does not bypass this required proposal, GO, implementation-start packet, or post-implementation verification.
- `GOV-STANDING-BACKLOG-001` — `WI-4487` remains the canonical backlog work item and no bulk backlog mutation is requested in this implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — this work preserves TAFE schema decisions, work item scope, bridge evidence, and verification as durable artifacts rather than transient chat state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — this slice preserves traceability from owner decisions to project authorization, work item, bridge proposal, tests, and report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — `WI-4487` remains open until the implementation report is reviewed and a valid Loyal Opposition `VERIFIED` verdict is recorded.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all files and verification work remain inside `E:\GT-KB` and affect GT-KB platform MemBase code only.

## Prior Deliberations

- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` — TAFE Phase 0 enablement: owner authorizes WI-4487..WI-4491 via single PAUTH
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612` — all work entering the typed flow engine must be pre-classified into one of the reviewed-task flow types.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-PILOT-ELIGIBILITY-20260612` — live pilot eligibility remains constrained; this schema slice does not run or expand an implementation-flow pilot.
- `bridge/gtkb-tafe-phase-0-enablement-005.md` — Codex GO authorized creation of the Phase-0 PAUTH and explicitly required each WI to proceed through its own proposal, GO, implementation-start packet, report, and verification.

## Owner Decisions / Input

No new owner decision is required.

- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` authorizes the Phase-0 PAUTH covering `WI-4487` through `WI-4491`.
- `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491` is active and includes `WI-4487`, `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R1`, and `SPEC-TAFE-R7`.
- This proposal still requires Loyal Opposition GO and an implementation-start packet before source/test edits.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R1`, `SPEC-TAFE-R6`,
`SPEC-TAFE-R7`, `WI-4487`, and the active Phase-0 PAUTH are sufficient for this
bounded schema/helper/test slice. New or revised requirements are not needed
because this proposal deliberately excludes seeding, runtime flow instances,
dispatch policy, CLI commands, doctor checks, pilots, generated bridge views,
and any bridge-authority change.

## Spec-Derived Verification Plan

| Specification / surface | Verification |
| --- | --- |
| `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R1`, `SPEC-TAFE-R7` | Add focused tests proving fresh `KnowledgeDB` instances create `flow_definitions`, `current_flow_definitions`, expected indexes, append-only versioning, and read helpers. |
| `SPEC-TAFE-R6` | Schema tests assert metadata columns exist for ordered stages, required roles, AUQ gates, never-self-review points, deterministic carve-outs, workspace isolation, lifecycle status, and changed-by/change-reason audit fields. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | After GO, run `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4487-flow-definitions-schema`; implementation report cites the fresh packet hash. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4487-flow-definitions-schema` and `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4487-flow-definitions-schema`; expected no missing required specs and zero blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries forward this table with observed command output. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge proposal/report preserve durable traceability; no backlog closure is claimed until a valid `VERIFIED` verdict exists. |
| Python code quality | Run `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\tests\test_db.py` and `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\tests\test_db.py`. |
| Targeted regression | Run `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_db.py -q --tb=short`. |

## Risk / Rollback

Primary risk is schema overreach: adding seed records or runtime flow tables in
this slice would collide with `WI-4488` and `WI-4489`. The proposal avoids that
by adding only the definition table/view/indexes and helper methods.

Rollback is straightforward: revert the edits to `groundtruth-kb/src/groundtruth_kb/db.py`
and `groundtruth-kb/tests/test_db.py`, then rerun the targeted DB tests. Existing
databases with the additive table can safely retain it unused; no destructive
migration is proposed.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-wi4487-flow-definitions-schema` document list in `bridge/INDEX.md`; no prior version is deleted or
rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat` — the diff adds a new MemBase schema/helper capability for the TAFE
substrate, plus focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
