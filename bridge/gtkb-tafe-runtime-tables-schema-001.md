NEW

# TAFE Runtime Tables Schema Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-runtime-tables-schema
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
Work Item: WI-4488

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/tests/test_tafe_runtime_tables.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement the second Phase 0 Typed Artifact-Flow Engine (TAFE) schema slice:
add append-only MemBase runtime-substrate tables for flow instances, stage
instances, flow events, and flow artifact references. This follows the now
VERIFIED WI-4487 `flow_definitions` table/service slice and gives later CLI,
doctor, dispatch, and telemetry work a durable place to store runtime state.

The slice is intentionally schema/service/test only. It does not start runtime
flow execution, does not implement stage leases, does not seed flow definitions,
does not add CLI commands or doctor checks, does not add dispatch policy, and
does not change `bridge/INDEX.md` authority. The WI-4488 acceptance question
about `stage_leases`, `stage_attempts`, and `agent_capability_snapshots` is
resolved conservatively: those surfaces remain split to their already-tracked
follow-on work items (`WI-4492`, `WI-4504`, and `WI-4497`) rather than being
folded into this Phase 0 table slice.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — this slice adds the runtime-state substrate while preserving bridge-authoritative parallel-run boundaries.
- `SPEC-TAFE-R1` — flow instances must reference typed flow definitions and model reviewed-task progression without hard-coded bridge behavior.
- `SPEC-TAFE-R2` — stage instances must provide the later single-claim/contention substrate without implementing claim/lease behavior here.
- `SPEC-TAFE-R6` — flow events and artifact references provide append-only audit and telemetry structure for later stage-attempt reporting.
- `SPEC-TAFE-R7` — canonical runtime state remains MemBase-backed and service-mediated through GT-KB source APIs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal/report/verdict chain remains append-only bridge evidence; `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — project, PAUTH, WI, target paths, and governing specs are linked before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable project authorization metadata is present in the proposal header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must map runtime schema/service tests to the linked TAFE specs.
- `GOV-STANDING-BACKLOG-001` — WI-4488 remains the backlog authority and sibling WIs must not be silently consumed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all work stays under `E:\GT-KB` and affects GT-KB platform code, not Agent Red application code.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the runtime schema decision is preserved through PAUTH, proposal, implementation report, and LO verdict.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — this durable substrate is a governed artifact, not transient implementation convenience.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — WI-4488 should only close after implementation evidence and a terminal VERIFIED verdict.

## Prior Deliberations

- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` — owner approved promoting the eight TAFE specs to `specified`.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` — owner authorized WI-4487 through WI-4491 under the active Phase 0 PAUTH.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612` — Phase 0 enablement was parked until valid Codex review, preserving review discipline.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` — owner selected the TAFE overhaul direction that produced this Phase 0 backlog.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612` — all work entering TAFE must be classified into reviewed-task flow types; this slice stores instances of those later seeded definitions.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-PILOT-ELIGIBILITY-20260612` — live pilot eligibility remains constrained; this schema slice does not run a pilot.

## Owner Decisions / Input

No new owner decision is required. Existing owner authority is the active Phase
0 PAUTH
`PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491`,
backed by `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612`; WI-4488 is explicitly
included in that authorization.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`,
`SPEC-TAFE-R1`, `SPEC-TAFE-R2`, `SPEC-TAFE-R6`, `SPEC-TAFE-R7`, WI-4488, the
VERIFIED WI-4487 substrate, and the active Phase 0 PAUTH provide enough
requirement detail for this bounded runtime-table schema/service/test slice.

No new or revised requirement is needed because this proposal deliberately
excludes seed rows, stage leases, stage attempts, capability snapshots, CLI
commands, doctor checks, dispatch policy, pilots, generated bridge views, and
any bridge-authority change.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_runtime_tables.py -q --tb=short
Expected: pass; verifies fresh MemBase databases create `flow_instances`, `stage_instances`, `flow_events`, and `flow_artifacts`; verifies required FK/reference fields, lifecycle/status fields, append-only event semantics, service create/list/get behavior, and no dependency on live bridge state.

groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_flow_definitions.py groundtruth-kb/tests/test_tafe_runtime_tables.py -q --tb=short
Expected: pass; verifies the WI-4488 runtime schema remains compatible with the VERIFIED WI-4487 flow-definition substrate.

groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_runtime_tables.py
Expected: pass.

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_runtime_tables.py
Expected: pass.
```

Spec mapping:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — tests prove runtime substrate exists without bridge-authority cutover.
- `SPEC-TAFE-R1` — tests prove instances reference flow definitions and stage rows represent reviewed-task progression.
- `SPEC-TAFE-R2` — tests prove stage rows carry claim-ready identity/status fields while leaving actual claim/lease behavior out of scope.
- `SPEC-TAFE-R6` — tests prove events and artifacts are append-only/auditable data surfaces for later telemetry.
- `SPEC-TAFE-R7` — service tests prove MemBase-backed canonical access through GT-KB source APIs.
- `GOV-STANDING-BACKLOG-001` — report must explicitly confirm `WI-4492`, `WI-4504`, and `WI-4497` remain open sibling work, not silently implemented.

## Risk / Rollback

Primary risk is over-expanding WI-4488 into later runtime behavior. The
mitigation is to keep this proposal limited to additive tables, light service
helpers, and tests. Stage leases, per-attempt telemetry, and capability
snapshots remain in their own backlog items.

Rollback is a normal single-commit source revert before VERIFIED. If a local DB
has already instantiated the additive tables, source rollback removes future
use while leaving unused tables harmlessly present; no destructive DB cleanup is
in scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top
of the `gtkb-tafe-runtime-tables-schema` document list in `bridge/INDEX.md`; no
prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains
the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

feat — this adds a new TAFE runtime schema/service capability, backed by
focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
