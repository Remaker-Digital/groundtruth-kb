NEW

# TAFE Agent Capability Snapshots Schema Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-agent-capability-snapshots-schema
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 1834acbd-e886-434c-9ae5-e467a7f93e2b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; default

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-DISPATCH-TRACK-WI-4497-4498-4499
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4497

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement WI-4497, the first Phase 1 Typed Artifact-Flow Engine R4 dispatch-track slice: add the `agent_capability_snapshots` MemBase schema plus minimal source/test substrate so that the later weighted-scoring dispatch policy engine (WI-4498) has governed, point-in-time capability inputs to score candidate harnesses against.

This proposal is intentionally bounded to schema and low-level service/test support. It MUST NOT implement the dispatch policy engine, weighted scoring, eligibility-gate evaluation, candidate selection, precedence-tier arithmetic, `gt flow dispatch tick`, `gt flow dispatch health`, capability auto-derivation from the live registry/doctor, generated bridge views, pilot eligibility changes, or any bridge-authority change. WI-4498 (dispatch policy engine) and WI-4499 (dispatch tick/health commands) remain the sibling work items for that behavior and must remain open after this slice.

This is the R4 dispatch track, run in parallel with the concurrently-active Codex-Prime R2 lease track (`gtkb-tafe-stage-leases-schema`, WI-4492). The two tracks touch disjoint tables (`agent_capability_snapshots` here vs `stage_leases` there) and are deconflicted via bridge work-intent claims.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - Phase 1 remains a parallel-run TAFE substrate; the file bridge and `bridge/INDEX.md` remain authoritative until a later governed cutover.
- `SPEC-TAFE-R4` - policy-driven dispatch applies hard eligibility gates (role, capability, subject, review-independence, health, stage-lease availability, owner gate status, workspace availability) then calibrated precedence tiers; the `agent_capability_snapshots` table is the durable substrate that records those per-candidate inputs. This slice provides the data home only, not the policy evaluation.
- `SPEC-TAFE-R6` - observability requires per-attempt agent/session/context id, model/provider, and dispatch-decision auditability; the snapshot captures the candidate-side capability/health/precedence fields that later telemetry and dispatch decisions reference.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal/report/verdict chain remains append-only bridge evidence; `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - PAUTH, project, work item, target paths, and governing specs are linked before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present in this proposal header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map schema/service tests to the linked TAFE requirements.
- `GOV-STANDING-BACKLOG-001` - WI-4497 is the backlog authority for this bounded slice; WI-4498 and WI-4499 must remain open siblings.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation proceeds under the active bounded PAUTH cited above plus the forthcoming Loyal Opposition GO.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the schema/service substrate becomes durable governed artifact state, not session-only behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the capability-snapshot decision and evidence are preserved through PAUTH, proposal, report, and LO verdict.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4497 should close only after implementation evidence and terminal VERIFIED.

## Prior Deliberations

- `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613` - active R4 dispatch-track PAUTH owner-decision basis; authorizes the capability-snapshots schema/service/test substrate (WI-4497) plus the sibling WI-4498/WI-4499 track under the standing owner directive.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` - records the bridge/dispatch overhaul problem framing and the session-scoped never-self-review invariant that dispatch policy must honor.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner selected the TAFE overhaul direction (one spec per R) that produced SPEC-TAFE-R4 and the dispatch-track work items.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approved promoting the TAFE specs (including SPEC-TAFE-R4/R6) to `specified`.
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` - WI-4488 runtime table substrate is VERIFIED and is the direct dependency for this capability-snapshot table (the additive TAFE schema/migration/view pattern is reused).
- `bridge/gtkb-tafe-stage-leases-schema-001.md` - the sibling R2 lease-track proposal authored by Codex-Prime; this proposal mirrors its bounding discipline (schema + low-level service only) and stays on disjoint tables.

## Owner Decisions / Input

No new owner decision is required. Existing authority is the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-DISPATCH-TRACK-WI-4497-4498-4499`, backed by `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613` (the owner's standing directive to drive the TAFE backlog to completion). WI-4497 is explicitly included in that authorization, and the authorization forbids cutover, generated-view authority, dual-write, pilot-eligibility expansion, and phase-2 reformation.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R4`, `SPEC-TAFE-R6`, WI-4497, the VERIFIED Phase 0 TAFE substrate (WI-4487..4491), and the active dispatch-track PAUTH provide enough requirement detail for this bounded schema/service/test slice.

No new or revised requirement is needed because this proposal deliberately excludes dispatch policy evaluation, weighted scoring, eligibility-gate arithmetic, candidate selection, dispatch tick/health commands, capability auto-derivation from the live registry, generated bridge-view writes, and bridge-authority cutover.

## Implementation Plan

1. Extend the TAFE schema in `groundtruth-kb/src/groundtruth_kb/db.py` with an additive, append-only `agent_capability_snapshots` table (in both the initial-create schema block and the `_migrate_schema` block so existing databases pick it up), plus supporting indexes and a `current_agent_capability_snapshots` latest-version view, mirroring the established `stage_instances` / `current_stage_instances` pattern.
2. Include the R4/R6 dispatch-input fields as first-class columns so the later WI-4498 policy engine can build on them without another schema rewrite: `harness_id`, `harness_name`, `role`, `subject_scope`, `health_status`, `reviewer_precedence`, `workspace_availability`, `model_identifier`, `captured_at`, `source`, `status`, and JSON `capabilities` + `metadata` blobs, alongside the standard `id`/`version`/`changed_by`/`changed_at`/`change_reason` append-only columns.
3. Add `insert_agent_capability_snapshot`, `get_agent_capability_snapshot`, `get_agent_capability_snapshot_history`, and `list_agent_capability_snapshots` methods in `db.py`, mirroring the existing stage-instance methods (append-only version bump, JSON encode/decode of `capabilities`/`metadata`, `*_parsed` convenience keys).
4. Add minimal typed service helpers in `groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py` (`record_capability_snapshot`, `get_capability_snapshot`, `get_capability_snapshot_history`, `list_capability_snapshots` on `FlowRuntimeService`) that validate required non-empty fields and write/read snapshot rows. These helpers do NOT score candidates, evaluate eligibility gates, derive capabilities from the registry, or select dispatch targets.
5. Add focused tests in `groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py` for schema creation on a fresh MemBase database, required columns, append-only versioning, the latest-version current view, JSON round-trip of `capabilities`/`metadata`, list filters (`harness_id`, `health_status`, `status`), service-level required-field validation, and additive-only behavior (the snapshot table does not alter the VERIFIED Phase 0 substrate).

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_tafe_agent_capability_snapshots.py -q --tb=short
Expected: pass; verifies fresh MemBase databases create `agent_capability_snapshots`, required R4/R6 columns exist, snapshots version append-only with a latest-version current view, JSON capability/metadata round-trips, list filters work, and minimal service helpers write/read snapshot records without implementing dispatch scoring or eligibility evaluation.

groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_tafe_runtime_tables.py groundtruth-kb\tests\test_tafe_agent_capability_snapshots.py -q --tb=short
Expected: pass; verifies WI-4497 remains compatible with the VERIFIED WI-4488 runtime substrate (additive only).

groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_tafe_flow_cli.py groundtruth-kb\tests\test_tafe_doctor.py groundtruth-kb\tests\test_tafe_agent_capability_snapshots.py -q --tb=short
Expected: pass; verifies the additive capability-snapshot substrate does not change the Phase 0 CLI skeleton or doctor checks.

groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_agent_capability_snapshots.py
Expected: pass.

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_agent_capability_snapshots.py
Expected: pass.

git diff --check -- groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py
Expected: no output, exit 0.
```

Spec mapping:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - tests prove the capability-snapshot substrate is additive and does not change bridge authority.
- `SPEC-TAFE-R4` - tests prove a candidate harness can have a durable point-in-time capability/health/precedence/workspace snapshot record for the later eligibility-gate-first, precedence-tier dispatch policy.
- `SPEC-TAFE-R6` - tests prove the snapshot persists model/provider, captured-at, and source provenance fields required for later dispatch-decision telemetry.
- `GOV-STANDING-BACKLOG-001` - implementation report must read back WI-4498 and WI-4499 as open sibling work, not silently implemented.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - report must map each linked spec above to executed evidence.

## Risk / Rollback

Primary risk is over-expanding WI-4497 into dispatch policy behavior (scoring, eligibility evaluation, candidate selection) that belongs to WI-4498, or into capability auto-derivation that belongs to the dispatch tick (WI-4499). Mitigation: keep code limited to schema and minimal CRUD-like service support, with tests asserting the sibling work remains open and the service helpers contain no scoring/selection logic.

A second risk is schema-field insufficiency forcing a later rewrite. Mitigation: the column set is derived directly from the SPEC-TAFE-R4 eligibility-gate list and SPEC-TAFE-R6 telemetry list, with a JSON `capabilities` blob for forward-compatible extension, so WI-4498 can consume it without a migration.

Rollback is a normal single-commit source/test revert before VERIFIED. If a local database has already instantiated the additive table, source rollback removes future use while the unused table remains harmless; destructive DB cleanup is out of scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-tafe-agent-capability-snapshots-schema` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`, and this slice changes no bridge-authority behavior.

## Recommended Commit Type

feat - this adds a new TAFE capability-snapshot schema/service substrate with focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
