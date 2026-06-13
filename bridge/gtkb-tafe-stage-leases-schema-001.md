NEW

# TAFE Stage Leases Schema Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-stage-leases-schema
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebe6d-deb1-7ff3-a77c-ed6b1c92f5b8
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-STAGE-LEASES-WI-4492
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4492

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/tests/test_tafe_stage_leases.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement WI-4492, the first Phase 1 Typed Artifact-Flow Engine lease-subsystem slice: add the `stage_leases` MemBase schema and minimal source/test substrate needed for later single-holder stage work.

This proposal is intentionally bounded to schema and low-level service/test support. It must not implement `gt flow claim`, `gt flow release`, `gt flow heartbeat`, expired-lease recovery, dispatch scoring, pilot eligibility, generated bridge views, or any bridge-authority change. WI-4493 and WI-4494 remain the sibling work items for claim/release/heartbeat behavior and recovery cleanup.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - Phase 1 remains a parallel-run TAFE substrate; the file bridge and `bridge/INDEX.md` remain authoritative.
- `SPEC-TAFE-R2` - the `stage_leases` table provides the durable single-holder substrate for later contention elimination.
- `SPEC-TAFE-R3` - heartbeat and TTL fields create the data needed for later stuck-flow and abandoned-lease detection, without implementing recovery here.
- `SPEC-TAFE-R7` - lease state must be represented through MemBase-backed GT-KB source APIs, not an alternate queue or ad hoc file store.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal/report/verdict chain remains append-only bridge evidence; `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - PAUTH, project, work item, target paths, and governing specs are linked before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present in this proposal header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map schema/service tests to the linked TAFE requirements.
- `GOV-STANDING-BACKLOG-001` - WI-4492 is the backlog authority for this bounded slice; WI-4493 and WI-4494 must remain open siblings.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation files stay under `E:\GT-KB` and affect GT-KB platform code/tests only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the lease-substrate decision and evidence are preserved through PAUTH, proposal, report, and LO verdict.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the schema/service substrate becomes durable governed artifact state, not session-only behavior.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4492 should close only after implementation evidence and terminal VERIFIED.

## Prior Deliberations

- `DELIB-20263143` - active WI-4492 PAUTH owner-decision basis; authorizes stage-leases schema/service/test substrate only.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` - records the bridge/dispatch overhaul problem framing.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner selected the TAFE overhaul direction that produced WI-4492.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approved promoting the TAFE specs to `specified`.
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` - WI-4488 runtime table substrate is VERIFIED and is the direct dependency for this lease table.
- `bridge/gtkb-tafe-flow-cli-skeleton-004.md` - WI-4490 CLI skeleton is VERIFIED; this proposal still excludes claim/release/heartbeat commands.
- `bridge/gtkb-tafe-doctor-checks-004.md` - WI-4491 doctor checks are VERIFIED and should remain compatible with the additive lease table.

## Owner Decisions / Input

No new owner decision is required. Existing authority is the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-STAGE-LEASES-WI-4492`, backed by `DELIB-20263143`; WI-4492 is explicitly included in that authorization.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R2`, `SPEC-TAFE-R3`, `SPEC-TAFE-R7`, WI-4492, the VERIFIED Phase 0 TAFE substrate, and the active WI-4492 PAUTH provide enough requirement detail for this bounded schema/service/test slice.

No new or revised requirement is needed because this proposal deliberately excludes claim/release/heartbeat command behavior, expired-lease recovery, dispatch policy, flow pilot activation, generated bridge-view writes, and bridge-authority cutover.

## Implementation Plan

1. Extend the TAFE schema in `groundtruth-kb/src/groundtruth_kb/db.py` with an additive `stage_leases` table tied to `stage_instances`.
2. Include the PAUTH-required lease fields: `heartbeat_at`, `ttl_seconds`, `holder_harness_id`, and `holder_session_id`; include enough identity/timestamp/status fields for later WI-4493/WI-4494 behavior to build on without another schema rewrite.
3. Add minimal typed service helpers in `groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py` for creating and reading lease rows, but do not encode acquisition contention, release, heartbeat renewal, or expiration policy.
4. Add focused tests in `groundtruth-kb/tests/test_tafe_stage_leases.py` for schema creation, required columns, stage-instance linkage, service-level insert/read behavior, and sibling-scope preservation.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_tafe_stage_leases.py -q --tb=short
Expected: pass; verifies fresh MemBase databases create `stage_leases`, required lease columns exist, lease rows link to stage instances, and minimal service helpers can write/read lease records without implementing claim semantics.

groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_tafe_runtime_tables.py groundtruth-kb\tests\test_tafe_stage_leases.py -q --tb=short
Expected: pass; verifies WI-4492 remains compatible with the VERIFIED WI-4488 runtime substrate.

groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_tafe_flow_cli.py groundtruth-kb\tests\test_tafe_doctor.py groundtruth-kb\tests\test_tafe_stage_leases.py -q --tb=short
Expected: pass; verifies the additive lease substrate does not change the Phase 0 CLI skeleton or doctor checks.

groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_stage_leases.py
Expected: pass.

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_stage_leases.py
Expected: pass.

git diff --check -- groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_stage_leases.py
Expected: no output, exit 0.
```

Spec mapping:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - tests prove the lease substrate is additive and does not change bridge authority.
- `SPEC-TAFE-R2` - tests prove a stage can have durable lease identity fields for later single-holder contention control.
- `SPEC-TAFE-R3` - tests prove heartbeat/TTL data exists for later recovery and self-management work.
- `SPEC-TAFE-R7` - service tests prove lease state is represented through GT-KB source APIs and MemBase schema.
- `GOV-STANDING-BACKLOG-001` - implementation report must read back WI-4493 and WI-4494 as open sibling work, not silently implemented.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - report must map each linked spec above to executed evidence.

## Risk / Rollback

Primary risk is over-expanding WI-4492 into runtime lease ownership behavior that belongs to WI-4493/WI-4494. The mitigation is to keep code limited to schema and minimal CRUD-like service support, with tests asserting sibling work remains open.

Rollback is a normal single-commit source/test revert before VERIFIED. If a local database has already instantiated the additive table, source rollback removes future use while the unused table remains harmless; destructive DB cleanup is out of scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-tafe-stage-leases-schema` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

feat - this adds a new TAFE lease schema/service substrate with focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
