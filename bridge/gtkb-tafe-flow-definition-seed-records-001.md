NEW

# TAFE Flow Definition Seed Records Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-flow-definition-seed-records
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
Work Item: WI-4489

target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/tests/test_tafe_flow_definition_seed_records.py"]

implementation_scope: source, test, data
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement the third Phase 0 Typed Artifact-Flow Engine (TAFE) slice: seed the
five canonical reviewed-task `flow_definitions` records in MemBase and add the
small idempotent service helper needed to make that seed operation repeatable.

This is a data-only behavior slice on top of the already VERIFIED WI-4487
`flow_definitions` schema/service. The implementation may add source helpers
and focused tests, then run the helper once against the root `groundtruth.db`
to create the five current seed rows. It must not add runtime dispatch
behavior, stage leases, CLI commands, doctor checks, generated bridge views, or
any `bridge/INDEX.md` authority change.

The seed set is:

| Flow definition id | Flow type | Stage sequence |
|---|---|---|
| `implementation` | `implementation` | `propose`, `review`, `implement`, `verify`, `complete` |
| `operation` | `operation` | `plan`, `execute`, `verify`, `complete` |
| `remediation` | `remediation` | `diagnose`, `propose_fix`, `review`, `implement`, `verify`, `complete` |
| `deliberation` | `deliberation` | `surface`, `investigate`, `decide`, `record`, `complete` |
| `report` | `report` | `investigate`, `draft`, `review`, `finalize`, `complete` |

Each record also stores required role by stage, AUQ gate positions,
never-self-review points, deterministic carve-out metadata, workspace-isolation
metadata, and source spec ids. The seed helper must be idempotent: a second run
against already-current seed rows must report them unchanged and must not
append duplicate versions.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - governs the shared typed flow substrate and requires the initial implementation, operation, remediation, deliberation, and report flows.
- `SPEC-TAFE-R1` - requires controlled, auditable, extensible reviewed-task flow definitions; this slice records the initial row-backed flow families.
- `SPEC-TAFE-R7` - requires canonical access through GT-KB services/CLI with MemBase as canonical flow state; this slice adds the service-mediated seed surface and live MemBase rows.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal/report/verdict chain remains append-only bridge evidence; `bridge/INDEX.md` stays canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - project, PAUTH, WI, target paths, and governing specs are linked before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present in the proposal header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map seed-record tests and live read-back evidence to the linked TAFE specs.
- `GOV-STANDING-BACKLOG-001` - WI-4489 remains the backlog authority; sibling CLI and doctor work must not be silently consumed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work stays under `E:\GT-KB` and affects GT-KB platform code/data, not Agent Red application code.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the seed decision is preserved through PAUTH, bridge proposal, implementation report, and LO verdict.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the seed records are durable governed artifacts, not transient test fixtures.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4489 should only close after implementation evidence and a terminal VERIFIED verdict.

## Prior Deliberations

- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approved promoting the eight TAFE specs to `specified`.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` - owner authorized WI-4487 through WI-4491 under the active Phase 0 PAUTH.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612` - Phase 0 enablement was parked until valid Codex review, preserving review discipline.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner selected the TAFE overhaul direction that produced this Phase 0 backlog.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612` - all work entering TAFE must be classified into one of the five typed flow families.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-PILOT-ELIGIBILITY-20260612` - live pilot eligibility remains constrained; this seed slice does not run a pilot.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

No new owner decision is required. Existing owner authority is the active Phase
0 PAUTH
`PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491`,
backed by `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612`; WI-4489 and the
`flow_definition_seed_records` mutation class are explicitly included in that
authorization.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`,
`SPEC-TAFE-R1`, `SPEC-TAFE-R7`, WI-4489, the VERIFIED WI-4487 substrate, and
the active Phase 0 PAUTH provide enough requirement detail for this bounded
seed-record slice.

No new or revised requirement is needed because this proposal deliberately
excludes runtime execution, dispatch policy, stage leases, stage attempts,
capability snapshots, CLI commands, doctor checks, generated bridge views,
pilot activation, and bridge-authority change.

## Implementation Plan

1. Add canonical seed definitions and an idempotent seed helper to
   `groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py`.
2. Add focused temp-DB tests in
   `groundtruth-kb/tests/test_tafe_flow_definition_seed_records.py` proving:
   the first seed run creates five current rows, the second run is unchanged,
   drifted current rows are converged by one new version, and all seed rows
   carry stages, roles, AUQ gates, never-self-review points, deterministic
   carve-outs, workspace-isolation metadata, and source spec ids.
3. Run the helper once against root `groundtruth.db` after tests pass and read
   back exactly the five current seed rows.
4. File a post-implementation report with the implementation-start packet hash,
   command evidence, root MemBase read-back, and explicit confirmation that
   WI-4490 CLI work and WI-4491 doctor work remain open siblings.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_flow_definition_seed_records.py -q --tb=short
Expected: pass; verifies idempotent seed behavior, five canonical flow definitions, required-role mapping, AUQ gates, never-self-review metadata, deterministic carve-outs, workspace-isolation metadata, and source spec ids in temporary MemBase databases.

groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_flow_definitions.py groundtruth-kb/tests/test_tafe_flow_definition_seed_records.py -q --tb=short
Expected: pass; verifies the WI-4489 seed helper remains compatible with the VERIFIED WI-4487 schema/service substrate.

groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_flow_definition_seed_records.py
Expected: pass.

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_flow_definition_seed_records.py
Expected: pass.

groundtruth-kb/.venv/Scripts/python.exe - <<'PY'
from groundtruth_kb.db import KnowledgeDB
rows = KnowledgeDB("groundtruth.db").list_flow_definitions(status="active")
ids = sorted(row["id"] for row in rows)
print(ids)
assert ids == ["deliberation", "implementation", "operation", "remediation", "report"]
PY
Expected: pass; verifies the live root MemBase has exactly the five current seed definitions after the seed run.
```

Spec mapping:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - tests and read-back prove the five initial flow families exist as canonical MemBase rows without cutover.
- `SPEC-TAFE-R1` - tests prove the flow set is row-backed, auditable, and extensible through definitions rather than hard-coded bridge behavior.
- `SPEC-TAFE-R7` - tests prove the seed operation is service-mediated and root read-back proves MemBase holds the canonical seed data.
- `GOV-STANDING-BACKLOG-001` - report must explicitly confirm WI-4490 and WI-4491 remain open sibling work, not silently implemented.

## Risk / Rollback

The main risk is encoding unstable policy details as behavior too early. The
mitigation is to store them as seed metadata only: no dispatch decisions,
claiming, AUQ enforcement, or review-independence enforcement is implemented
in this slice.

Rollback before VERIFIED is a normal source/test revert plus an append-only
seed correction if needed. Because `groundtruth.db` is ignored live MemBase
state, destructive deletion is not in scope; any correction should be made by
appending a corrected current flow-definition version through the same service
surface and reporting that evidence.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top
of the `gtkb-tafe-flow-definition-seed-records` document list in
`bridge/INDEX.md`; no prior version is deleted or rewritten (append-only).
`bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

feat - this adds the canonical TAFE seed-record helper, tests, and live
MemBase seed data for WI-4489.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
