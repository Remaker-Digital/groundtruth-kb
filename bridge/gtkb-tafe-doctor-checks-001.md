NEW

# TAFE Doctor Checks Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-doctor-checks
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebe6d-deb1-7ff3-a77c-ed6b1c92f5b8
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4491

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_tafe_doctor.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4491, the fifth and final approved Phase 0 TAFE slice: add WARN-level `gt project doctor` checks for TAFE schema health and canonical flow-definition health.

The proposed checks are diagnostic only. They may inspect `groundtruth.db`, verify that the Phase 0 TAFE tables/views are present, and verify that the five canonical reviewed-task flow definitions are seeded and internally well-formed. They must not seed definitions, alter MemBase, advance flows, claim or release work, dispatch stages, render bridge views, or change bridge authority.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - Phase 0 remains a parallel-run TAFE substrate with MemBase-backed flow state and no bridge-authority cutover.
- `SPEC-TAFE-R1` - doctor checks should verify the canonical five reviewed-task flow families exist and remain extensible through typed flow definitions.
- `SPEC-TAFE-R3` - the work directly implements self-health visibility and self-diagnosis for the Phase 0 TAFE substrate.
- `SPEC-TAFE-R6` - the checks add observable health evidence for flow schema and definition state.
- `SPEC-TAFE-R7` - doctor checks must read canonical TAFE state through GT-KB service/DB surfaces, with MemBase as the canonical store.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal/report/verdict chain remains append-only bridge evidence; `bridge/INDEX.md` remains workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - PAUTH, project, WI, target paths, and governing specs are linked before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present in this proposal header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map doctor tests and smoke commands to the linked TAFE requirements.
- `GOV-STANDING-BACKLOG-001` - WI-4492 and later lease/dispatch/render/pilot work remain visible sibling backlog, not silently absorbed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work stays under `E:\GT-KB` and affects GT-KB platform code/tests only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the doctor-check decision and evidence are preserved through PAUTH, bridge proposal, report, and LO verdict.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the checks and tests become durable governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4491 should only close after implementation evidence and a terminal VERIFIED verdict.

## Prior Deliberations

- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approved promoting the TAFE specs to `specified`.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` - owner authorized WI-4487 through WI-4491 under the active Phase 0 PAUTH.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612` - Phase 0 enablement was parked until valid Codex review, preserving bridge discipline.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner selected the TAFE overhaul direction that produced this Phase 0 backlog.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612` - all work entering TAFE must be classified into one of the five typed flow families.
- `bridge/gtkb-tafe-flow-definitions-schema-005.md` - WI-4487 flow-definition schema/service substrate is VERIFIED.
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` - WI-4488 runtime table/service substrate is VERIFIED.
- `bridge/gtkb-tafe-flow-definition-seed-records-004.md` - WI-4489 seed records are VERIFIED.
- `bridge/gtkb-tafe-flow-cli-skeleton-004.md` - WI-4490 CLI skeleton is VERIFIED.

## Owner Decisions / Input

No new owner decision is required. Existing owner authority is the active Phase 0 PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491`, backed by `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612`; WI-4491 and the Phase 0 doctor checks are explicitly included in that authorization.

## Requirement Sufficiency

Existing requirements sufficient - `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R1`, `SPEC-TAFE-R3`, `SPEC-TAFE-R6`, `SPEC-TAFE-R7`, WI-4491, the VERIFIED WI-4487/WI-4488/WI-4489/WI-4490 substrate, and the active Phase 0 PAUTH provide enough requirement detail for this bounded doctor-check slice.

No new or revised requirement is needed because this proposal deliberately excludes schema migration, runtime execution, stage leases, claim/release/heartbeat behavior, dispatch policy, generated bridge-view writes, pilot activation, and bridge-authority change.

## Implementation Plan

1. Add `_check_tafe_schema(target: Path) -> ToolCheck` to `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.
2. Add `_check_tafe_flow_definitions(target: Path) -> ToolCheck` to the same module.
3. Register both checks in `run_doctor()` for bridge-enabled profiles near the existing MemBase and TAFE-adjacent health checks.
4. Keep both checks WARN-level initially:
   - missing `groundtruth.db`, missing TAFE tables/views, malformed schema, missing canonical definitions, invalid stage sequence, missing required roles, or unseeded definitions should return `status="warning"`;
   - a healthy database should return `status="pass"`.
5. Add focused tests in `groundtruth-kb/tests/test_tafe_doctor.py` covering clean pass, missing database/schema warning, missing or drifted flow-definition warning, and public `run_doctor()` inclusion.

Implementation should prefer structured DB/service access where reasonable. It must not call `seed_reviewed_task_flow_definitions()` or otherwise mutate MemBase.

## Spec-Derived Verification Plan

| Spec / governing surface | Proposed verification evidence |
| --- | --- |
| `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` | Focused doctor tests prove the checks observe TAFE state without activating TAFE as bridge authority or dispatcher. |
| `SPEC-TAFE-R1` | Tests verify the five canonical flow families are required and invalid/missing definitions warn. |
| `SPEC-TAFE-R3` | Tests verify the new self-health checks report pass/warning states for healthy and unhealthy TAFE substrate conditions. |
| `SPEC-TAFE-R6` | JSON/human doctor smoke checks verify the health evidence is visible through the project doctor surface. |
| `SPEC-TAFE-R7` | Tests verify doctor checks read MemBase-backed TAFE schema/definition state through package surfaces and do not mutate state. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation report confirms no doctor command writes `bridge/INDEX.md` or generated bridge authority surfaces. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Implementation-start authorization is created from the live latest GO before source/test edits. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The proposal/report carry PAUTH/project/WI metadata and exact target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests, adjacent doctor/TAFE tests, Ruff lint, Ruff format, and doctor smoke commands are executed and reported. |
| `GOV-STANDING-BACKLOG-001` | Backlog read-back confirms WI-4492+ remain open sibling work. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --check` and path inspection confirm implementation files remain under `E:\GT-KB`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Evidence is captured in the implementation report and LO verdict. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Tests exercise durable doctor behavior rather than session-only inspection. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | WI-4491 is resolved only after terminal VERIFIED. |

Expected command set:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_tafe_doctor.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_doctor.py groundtruth-kb\tests\test_tafe_flow_definitions.py groundtruth-kb\tests\test_tafe_flow_definition_seed_records.py groundtruth-kb\tests\test_tafe_doctor.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_tafe_doctor.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\tests\test_tafe_doctor.py
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb project doctor --dir . --json
git diff --check -- groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_tafe_doctor.py
```

## Acceptance Criteria

- [ ] `gt project doctor` includes a TAFE schema health check for bridge-enabled profiles.
- [ ] `gt project doctor` includes a TAFE flow-definition health check for bridge-enabled profiles.
- [ ] Healthy Phase 0 TAFE schema and seed definitions return pass.
- [ ] Missing schema/definition drift returns warning, not fail, during Phase 0.
- [ ] Checks do not mutate MemBase or bridge files.
- [ ] WI-4492 and later runtime/lease/dispatch work remain out of scope.

## Risk / Rollback

Main risk is false-positive warning noise if the checks are too strict against transitional Phase 0 data. This is mitigated by WARN severity, focused fixture tests, and limiting the checks to the VERIFIED Phase 0 schema/seed contract.

Rollback is a normal source/test revert of `groundtruth-kb/src/groundtruth_kb/project/doctor.py` and `groundtruth-kb/tests/test_tafe_doctor.py`. No live MemBase correction should be needed because the implementation is read-only.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-tafe-doctor-checks` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

Recommended commit type: `feat:`

Justification: the implementation will add new user-visible doctor health-check capability plus focused regression tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
