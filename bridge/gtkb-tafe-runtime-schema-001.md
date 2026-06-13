NEW

# TAFE Runtime Schema Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-runtime-schema
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
Work Item: WI-4488

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/tests/test_tafe_runtime_schema.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the second Phase 0 Typed Artifact-Flow Engine substrate slice for
`WI-4488`: additive MemBase runtime tables for flow instances, per-stage state,
append-only events, and artifact links. The work builds on verified WI-4487
flow definitions and keeps `bridge/INDEX.md` authoritative until a later
governed cutover.

This proposal is schema/service/test only. It does not seed the five canonical
flow definitions, add `gt flow` CLI commands, run a pilot, change dispatch
behavior, generate a bridge view, or alter bridge authority.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - requires canonical typed
  artifact-flow state to move toward MemBase-backed services while markdown
  remains compatibility/presentation until governed cutover.
- `SPEC-TAFE-R1` - requires controlled, auditable, extensible reviewed-task
  flow instances across implementation, operation, remediation, deliberation,
  and report verification families.
- `SPEC-TAFE-R2` - requires single-claim semantics at stage granularity, lease
  owner/session/context metadata, TTL/heartbeat/release state, stale recovery
  hooks, and isolated mutation workspace metadata.
- `SPEC-TAFE-R6` - requires full flow auditability and stage-attempt telemetry,
  including actors, models/providers, dispatch decisions, lease lifecycle,
  timing, outcome, verdict, tests, failure class, cleanup, recovery, and
  artifact links.
- `SPEC-TAFE-R7` - requires canonical typed artifact-flow data and services to
  be accessed through dedicated DB/CLI/service surfaces with MemBase as
  canonical.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation remains bridge-mediated and
  `bridge/INDEX.md` remains the canonical coordination state.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the Phase 0 PAUTH permits
  autonomous passage through the bridge protocol, not direct implementation
  without GO and an implementation-start packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries
  PAUTH, project, work item, and concrete `target_paths` metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links
  governing specifications and maps verification to each.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report
  must carry forward spec-to-test mapping and executed evidence.
- `GOV-STANDING-BACKLOG-001` - `WI-4488` remains the canonical backlog authority
  until the bridge records terminal verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work stays within `E:\GT-KB`
  and affects GT-KB platform code only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the work preserves scope,
  rationale, implementation evidence, and verification as durable artifacts.

## Prior Deliberations

- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approved promoting the
  eight TAFE specs to `specified`, making `SPEC-TAFE-R1`, `SPEC-TAFE-R2`,
  `SPEC-TAFE-R6`, and `SPEC-TAFE-R7` available as governing requirements.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` - owner authorized Phase 0
  WI-4487 through WI-4491 via one PAUTH, while preserving per-WI bridge review,
  implementation-start, report, and verification.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612` - records the valid
  Codex GO requirement after an invalid harness-C GO; the later `-005` GO is
  the governing enablement approval.
- `bridge/gtkb-tafe-phase-0-enablement-005.md` - Codex GO accepted the Phase 0
  PAUTH/enrichment and explicitly required each WI to proceed through its own
  proposal, GO, implementation-start packet, implementation report, and
  verification.
- `bridge/gtkb-tafe-flow-definitions-schema-004.md` - WI-4487 is VERIFIED, so
  the runtime schema can depend on the existing `flow_definitions` table and
  `FlowDefinitionService` substrate.

Direct Deliberation Archive search for `WI-4488 TAFE runtime schema
flow_instances stage_instances flow_events flow_artifacts` returned no
additional records.

## Owner Decisions / Input

No new owner decision is required.

`DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` authorizes the Phase 0 PAUTH
covering `WI-4488`, and `bridge/gtkb-tafe-phase-0-enablement-005.md` confirms
that each included WI may proceed autonomously through its own bridge proposal,
GO, implementation-start packet, report, and verification.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R1`,
`SPEC-TAFE-R2`, `SPEC-TAFE-R6`, `SPEC-TAFE-R7`, the verified WI-4487
flow-definition substrate, `WI-4488`, and the active Phase 0 PAUTH are
sufficient for this bounded runtime schema/service/test slice.

The F5 scoping decision from the enablement thread is resolved as follows:
stage lease state belongs in this WI through `stage_instances` lease columns;
stage attempt telemetry belongs in this WI through append-only `flow_events`;
`agent_capability_snapshots` are R4 policy/dispatch inputs and remain out of
scope for a later policy-capability slice.

## Spec-Derived Verification Plan

| Specification / surface | Verification |
| --- | --- |
| `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R1`, `SPEC-TAFE-R7` | Add `groundtruth-kb/tests/test_tafe_runtime_schema.py` proving fresh `KnowledgeDB` instances create `flow_instances`, `stage_instances`, `flow_events`, `flow_artifacts`, current-state views or equivalent read helpers, and service-level create/list/get behavior without changing bridge authority. |
| `SPEC-TAFE-R2` | Tests assert stage state carries single active lease metadata: owner session/context id, lease token/status, TTL expiry, heartbeat timestamp, release/recovery fields, and workspace-isolation metadata. |
| `SPEC-TAFE-R6` | Tests assert append-only `flow_events` and `flow_artifacts` preserve audit/telemetry columns for actor/session/model/provider, dispatch decision, lease lifecycle, timing, outcome/verdict/tests/failure/cleanup/recovery fields, and artifact references. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | After GO, run `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-tafe-runtime-schema`; implementation report cites the fresh packet hash. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-tafe-runtime-schema` and `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-tafe-runtime-schema`; expected no missing required specs and zero blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries forward this table with observed command output. |
| Existing WI-4487 substrate compatibility | Run existing `groundtruth-kb\tests\test_tafe_flow_definitions.py` plus new runtime tests to ensure runtime additions do not break flow-definition behavior. |
| Python code quality | Run `groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_runtime_schema.py` and `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check` on the same paths. |

## Risk / Rollback

Primary risk is schema overreach: accidentally adding policy/capability
snapshots, CLI behavior, seed records, or dispatch semantics would blur WI-4488
into later Phase 0/Phase 1 work. The proposal avoids that by limiting the diff
to runtime storage, small service helpers, and tests.

Rollback is a single source/test revert before verification. Existing local
databases that initialize the additive runtime tables can retain them unused;
no destructive migration or live data cleanup is proposed.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-tafe-runtime-schema` document list in `bridge/INDEX.md`; no prior
version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the
canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat` - the eventual implementation adds a new TAFE runtime schema/service
capability plus focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
