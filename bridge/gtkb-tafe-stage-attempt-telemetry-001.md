NEW

# TAFE Per-Stage-Attempt Telemetry Schema Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-stage-attempt-telemetry
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 1834acbd-e886-434c-9ae5-e467a7f93e2b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; default

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-OBSERVABILITY-TRACK-WI-4504-4505
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4504

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/tests/test_tafe_stage_attempt_telemetry.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement WI-4504, the TAFE R6 observability substrate: an additive append-only `stage_attempt_telemetry` MemBase table plus a minimal recording service so that each stage attempt's full audit/telemetry record (per SPEC-TAFE-R6) can be persisted. This is the foundation the WI-4505 stuck-flow detection / self-diagnosis slice reasons over.

This is the observability/reliability track, run in parallel with the concurrently-active dispatch track (WI-4498/4499) and lease track (WI-4493/4494). It touches a disjoint table (`stage_attempt_telemetry`) and is deconflicted via bridge work-intent claims.

### Bounding (explicit out-of-scope)

This slice is bounded to schema + low-level recording service + tests. It MUST NOT implement: stuck-flow detection or self-diagnosis (WI-4505), dashboard/metric aggregation or visualization (WI-4506), telemetry analysis/rollups/KPIs, automatic telemetry capture wired into a live dispatch tick (WI-4499), autonomous recovery actuation, generated bridge views, dual-write, pilot eligibility changes, or bridge-authority cutover. The recording service writes a row from caller-supplied fields; it computes nothing.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - Phase 1 parallel-run substrate; `bridge/INDEX.md` remains canonical until a later governed cutover. MemBase is canonical for telemetry per the umbrella.
- `SPEC-TAFE-R6` - the governing requirement: full flow auditability and stage-attempt telemetry covering flow/stage/artifact ids, agent/session/context id, model/provider, dispatch decision, lease lifecycle, timing, token/cost where available, outcome, verdict, tests, failure class, cleanup result, recovery actions, and artifact links. This table provides exactly those fields as a durable record.
- `SPEC-TAFE-R3` - the recorded failure-class, cleanup-result, and recovery-action fields are the durable inputs the later WI-4505 stuck-flow detection / self-management slice reasons over; no detection logic is implemented here.
- `SPEC-TAFE-R4` - the recorded `dispatch_decision` field captures the policy decision (from the VERIFIED WI-4498 engine) that produced the attempt, for later auditability.
- `SPEC-TAFE-R2` - the recorded `lease_id` and `lease_lifecycle` fields capture the stage-lease contention context for the attempt.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only bridge evidence; `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - PAUTH, project, work item, target paths, and governing specs are concretely linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps schema/service tests to the linked TAFE requirements.
- `GOV-STANDING-BACKLOG-001` - WI-4504 is the backlog authority for this slice; WI-4505 remains an open sibling.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation proceeds under the active bounded observability-track PAUTH plus the forthcoming Loyal Opposition GO.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the telemetry substrate is durable governed artifact state with a preserved evidence trail.

## Prior Deliberations

- `DELIB-TAFE-PHASE-1-OBSERVABILITY-TRACK-PAUTH-20260613` - active observability-track PAUTH owner-decision basis; authorizes the telemetry schema/service (WI-4504) and stuck-flow detection (WI-4505) under the standing owner directive.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` - dispatch-overhaul framing; the telemetry records the session/context ids the never-self-review invariant is scoped to.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner choice of the TAFE overhaul direction that produced SPEC-TAFE-R6.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approval promoting SPEC-TAFE-R6 to `specified`.
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` - VERIFIED WI-4488 runtime substrate; the additive TAFE schema/migration/view pattern is reused, and stage attempts reference `stage_instances`.
- `bridge/gtkb-tafe-agent-capability-snapshots-schema-004.md` - VERIFIED WI-4497 sibling schema slice this proposal mirrors in structure and bounding discipline.
- No prior deliberations found for TAFE stage-attempt telemetry: `search_deliberations("dispatch policy weighted scoring eligibility precedence review independence")` (the nearest dispatch query run this session) returned no telemetry-schema matches; this is the first R6 telemetry substrate.

## Owner Decisions / Input

No new owner decision is required. Existing authority is the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-OBSERVABILITY-TRACK-WI-4504-4505` (backed by `DELIB-TAFE-PHASE-1-OBSERVABILITY-TRACK-PAUTH-20260613`), which explicitly includes WI-4504 and forbids cutover, generated-view authority, dual-write, pilot-eligibility expansion, phase-2 reformation, and autonomous recovery actuation.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TAFE-R6` precisely enumerates the per-stage-attempt telemetry fields, with `SPEC-TAFE-R3`/`R4`/`R2` defining the failure/recovery, dispatch-decision, and lease-context fields the record references. No new or revised requirement is needed because this slice persists the specified telemetry fields as a pure recording substrate and excludes detection, aggregation, dashboards, live capture, and recovery actuation.

## Implementation Plan

1. Extend the TAFE schema in `groundtruth-kb/src/groundtruth_kb/db.py` with an additive, append-only `stage_attempt_telemetry` table (in both the initial-create schema block and the `_migrate_schema` block), supporting indexes, and a `current_stage_attempt_telemetry` latest-version view, mirroring the established `stage_instances`/`stage_leases` pattern.
2. Columns derived directly from SPEC-TAFE-R6: `id`, `version`, `flow_instance_id`, `stage_instance_id`, `attempt_number`, `agent_harness_id`, `agent_session_id`, `agent_context_id`, `model_identifier`, `provider`, `dispatch_decision` (JSON), `lease_id`, `lease_lifecycle` (JSON), `started_at`, `completed_at`, `duration_ms`, `token_count`, `cost`, `outcome`, `verdict`, `test_summary` (JSON), `failure_class`, `cleanup_result`, `recovery_actions` (JSON), `artifact_links` (JSON), `status` (default `active`), `metadata` (JSON), plus the standard `changed_by`/`changed_at`/`change_reason`. Required NOT NULL: `id`, `version`, `flow_instance_id`, `stage_instance_id`, plus the change-tracking columns.
3. Add `insert_stage_attempt_telemetry`, `get_stage_attempt_telemetry`, `get_stage_attempt_telemetry_history`, and `list_stage_attempt_telemetry` methods in `db.py`, mirroring the stage-lease method quartet (append-only version bump, JSON encode of the JSON columns; reads expose `*_parsed` keys via the existing `_row_to_dict` list). The insert validates that `stage_instance_id` references an existing stage instance (referential integrity, mirroring `insert_stage_lease`).
4. Add a minimal recording helper `record_stage_attempt_telemetry` (plus `get_stage_attempt_telemetry` / `get_stage_attempt_telemetry_history` / `list_stage_attempt_telemetry`) on `FlowRuntimeService` in `groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py` that validates required non-empty fields and writes/reads a row. The helper computes no rollups, detects no stuck flows, and triggers no recovery.
5. Add focused tests in `groundtruth-kb/tests/test_tafe_stage_attempt_telemetry.py` for schema creation, required R6 columns, append-only versioning, the latest-version current view, JSON round-trip of the JSON columns, list filters (`flow_instance_id`, `outcome`, `failure_class`), service required-field validation, stage-instance referential integrity, and a guard asserting the slice exposes no detection/aggregation/dashboard API.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
python -m pytest groundtruth-kb/tests/test_tafe_stage_attempt_telemetry.py -q --tb=short
Expected: pass; verifies fresh MemBase databases create stage_attempt_telemetry, required R6 columns exist, telemetry versions append-only with a latest-version current view, JSON columns round-trip, list filters work, stage-instance referential integrity is enforced, and the recording service implements no detection/aggregation surface.

python -m pytest groundtruth-kb/tests/test_tafe_runtime_tables.py groundtruth-kb/tests/test_tafe_stage_attempt_telemetry.py -q --tb=short
Expected: pass; verifies WI-4504 remains compatible with the VERIFIED WI-4488 runtime substrate (additive only).

python -m pytest groundtruth-kb/tests/test_tafe_flow_cli.py groundtruth-kb/tests/test_tafe_doctor.py groundtruth-kb/tests/test_tafe_stage_attempt_telemetry.py -q --tb=short
Expected: pass; verifies the additive telemetry substrate does not change the Phase 0 CLI skeleton or doctor checks.

python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_stage_attempt_telemetry.py
Expected: pass.

python -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_stage_attempt_telemetry.py
Expected: pass.

git diff --check -- groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_stage_attempt_telemetry.py
Expected: no output, exit 0.
```

Spec mapping:

- `SPEC-TAFE-R6` - tests prove the full per-stage-attempt telemetry field set persists and round-trips, with a latest-version current view and append-only versioning.
- `SPEC-TAFE-R3` - tests prove the failure-class / cleanup-result / recovery-actions fields persist for later self-diagnosis, with no detection logic in this slice.
- `SPEC-TAFE-R4`/`R2` - tests prove the `dispatch_decision` and `lease_id`/`lease_lifecycle` fields persist as recorded context.
- `GOV-STANDING-BACKLOG-001` - the report reads back WI-4505 as open; the service exposes no detection/aggregation API.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - each linked spec maps to executed evidence.

## Risk / Rollback

Primary risk is over-expanding WI-4504 into detection/aggregation (WI-4505/4506) or live capture (WI-4499). Mitigation: the recording service writes caller-supplied fields and computes nothing; tests assert no detection/aggregation/dashboard surface and that WI-4505 remains open.

A second risk is schema-field insufficiency forcing a later rewrite. Mitigation: the column set is derived directly from the SPEC-TAFE-R6 enumeration, with JSON blobs (`dispatch_decision`, `lease_lifecycle`, `test_summary`, `recovery_actions`, `artifact_links`, `metadata`) for forward-compatible extension.

Rollback is a normal single-commit source/test revert before VERIFIED. An already-instantiated additive table is harmless; destructive DB cleanup is out of scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-tafe-stage-attempt-telemetry` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`, and this slice changes no bridge-authority behavior.

## Recommended Commit Type

feat - adds a new TAFE per-stage-attempt telemetry schema/service substrate with focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
