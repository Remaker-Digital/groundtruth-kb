NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-20260702-ops-dispatcher-synthesis
author_model: GPT-5
author_model_version: 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

# Dispatch Lane Scoring Registry And Projections

bridge_kind: prime_proposal
Document: gtkb-dispatch-lane-scoring-registry-projections
Version: 001
Date: 2026-07-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY-WI-4958
Project: PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY
Work Item: WI-4958

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/dispatcher", "groundtruth-kb/src/groundtruth_kb/bridge", "groundtruth-kb/src/groundtruth_kb/cli.py", "config/dispatcher", "harness-state/harness-registry.json", "scripts/benchmarks", "scripts/ops/dispatch_parity.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts", "platform_tests/groundtruth_kb", "groundtruth-kb/tests"]

implementation_scope: source+formal-artifact+schema+generated-projection+tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Implement the governed dispatch lane-scoring authority domain and compact dispatcher projections selected during the lane-scoring grill, reconciled with `OPS-LIFECYCLE-DISPATCHER-MODEL-CONSOLIDATION-2026-07-02.md`. This is the Wave 1 schema/projection foundation for target selection among lifecycle-eligible dispatch work.

This proposal does not activate production utility ranking. Runtime ranking, telemetry automation, and production cutover require later governed work after this schema/projection foundation is reviewed and verified.

## Claim

Prime Builder proposes to add the lane-scoring registry and projection substrate that distinguishes harness functional capability from model quality, and ranks candidate lanes by harness + provider/model route + session role + activity type after OPS lifecycle eligibility has already passed.

## Requirement Sufficiency

Existing requirements sufficient.

Existing dispatcher architecture, centralized dispatch service, and dispatch-envelope rule constraints are sufficient for proposal filing and implementation-start authorization. This slice still creates or amends formal records and MemBase/KB schema because the owner selected lane scoring as a governed extension to the OPS lifecycle model.

## In-Root Placement Evidence

All implementation outputs, generated projections, tests, and formalization side effects for this proposal remain under the GT-KB project root `E:/GT-KB`. The status-bearing bridge proposal is filed under `E:/GT-KB/bridge/gtkb-dispatch-lane-scoring-registry-projections-001.md`. No Agent Red application source or external archive path is in scope.

## OPS Consolidation Integration

The OPS lifecycle model decides whether a work item/artifact is dispatchable. This lane-scoring extension decides who receives already-eligible dispatchable work. The deterministic precedence is lifecycle first and scoring last.

The lane-scoring authority follows the same MemBase/KB-plus-generated-projection pattern as OPS lifecycle records, but in a separate domain. OPS lifecycle tables govern artifact lifecycle, quarantine, NO-ACTION, circuit breakers, service logs, and audit records. Lane-scoring tables govern the lane matrix, scoring evidence, snapshots, score dimensions, caps, route identity, and projection metadata.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires protected source/config changes to proceed through bridge proposal, GO, implementation report, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification mapped to cited specifications.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform work inside GT-KB and out of Agent Red application source.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - governs dispatcher rules and dispatch-envelope constraints.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher resolves targets and records dispatch activity.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher is the isolated daemon-owned control plane.

## Prior Deliberations

- `DELIB-20260702-DISPATCH-RANKING-ATOMIC-TARGET` - atomic dispatch target is harness + provider/model route + role/activity lane.
- `DELIB-20260702-DISPATCH-LANE-MATRIX-SCOPE` - complete role/activity lane matrix with explicit toggles.
- `DELIB-20260702-DISPATCH-LANE-ACTIVITY-VOCAB-V1` - v1 activity vocabulary uses build, test, spec, ops, project, deliberation.
- `DELIB-20260702-DISPATCH-SCORING-REGISTRY-SOT` - lane matrix and snapshots live in a separate governed scoring registry/table.
- `DELIB-20260702-DISPATCH-LANE-SCORING-MEMBASE-AUTHORITY-SEPARATE-DOMAIN` - lane scoring uses MemBase/KB authority in a separate domain from OPS lifecycle.
- `DELIB-20260702-DISPATCH-LIFECYCLE-FIRST-SCORING-LAST-PRECEDENCE` - OPS lifecycle eligibility precedes lane scoring.
- `DELIB-20260702-DISPATCH-LANE-LIFECYCLE-ENUM-PLUS-FIELDS` - lanes use lifecycle enum plus independent behavior fields.
- `DELIB-20260702-DISPATCH-MODEL-ROUTE-LANE-IDENTITY` - provider/model route is part of lane identity.
- `DELIB-20260702-DISPATCH-NATIVE-HARNESS-FIXED-ROUTE-LANES` - native harnesses use fixed configured routes when not launch-selectable.
- `DELIB-20260702-DISPATCH-PRODUCTION-LANE-MINIMUM-EVIDENCE` - production lanes require parity, readiness, and benchmark/performance evidence.
- `DELIB-20260702-DISPATCH-COMPACT-HOT-PATH-LANE-PROJECTION` - dispatcher hot path consumes compact generated projection only.
- `DELIB-20260702-DISPATCH-LANE-SCORING-SHADOW-ROLLOUT` - rollout starts shadow/advisory before governed activation.
- `DELIB-20260702-DISPATCH-OPS-DIAGNOSIS-AS-OPS-ACTIVITY-SUBTYPE` - OPS diagnosis/remediation remain activity=ops subtypes.

## Owner Decisions / Input

- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected actual project, WI, and bridge proposal creation.
- `PAUTH-PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY-WI-4958` - active child-project authorization for this work item.

## Proposed Scope

- Create or update formal records defining dispatch lane identity, lane lifecycle/status fields, production eligibility evidence, score dimensions, snapshot promotion semantics, projection authority, freshness/drift invalidation, and model-route selectability.
- Add MemBase/KB schema for lane matrix records, scoring evidence, candidate snapshots, approved snapshots, score dimensions, weight-profile references, caps, route identity/versioning, and projection metadata.
- Add deterministic generator for compact dispatcher projection with active snapshot id, effective ranked lanes per role/activity, summarized blocked lanes/reasons, compact utility components, caps, freshness, and runtime-suppression fields.
- Seed the lane matrix from registered non-retired harnesses and configured non-retired provider/model routes, including fixed native harness routes with `route_selectable=false` where applicable.
- Add validation that missing/stale required evidence fails closed for production projection unless explicit waiver/fallback metadata exists.
- Add tests for schema creation, projection generation, complete lane-matrix population, lifecycle enum plus independent fields, model-route identity, stale-evidence fail-closed behavior, and no raw evidence in hot-path dispatcher config.

## Out Of Scope

- OPS lifecycle/protocol behavior; that is `WI-4957`.
- Production runtime lane utility ranking and dispatch target selection; follow-on after Wave 1.
- Automated telemetry ingestion and benchmark score promotion; follow-on after Wave 1.
- Production activation of lane scoring; explicitly forbidden by PAUTH until a later governed activation GO.
- AUQ/headless hook launch hygiene; that is `WI-4959`.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Tests prove dispatch rules remain what/when authority while lane-scoring projection ranks who among eligible targets; dispatcher config is not overloaded with raw scoring evidence. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Tests prove generated projection contains enough target-selection data for the centralized dispatcher without introducing harness-side target decisions. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests prove the dispatcher remains the daemon-owned control plane and lane projections are consumed by dispatcher code only. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path and preflight checks prove all mutations are in GT-KB platform paths and no Agent Red application source is changed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map schema/projection behavior to focused tests and preflights. |

Required focused checks include schema migration/creation tests, projection generation tests, registered-harness/model-route lane population tests, lifecycle/status field tests, stale evidence fail-closed tests, projection compactness tests, and dispatcher config separation tests.

## Acceptance Criteria

- Lane-scoring authority lives in governed MemBase/KB records separate from OPS lifecycle records.
- Projection generation produces compact hot-path lane views without raw evidence bloat.
- Lane identity includes harness, provider, model route, durable role, and activity type.
- All registered non-retired harnesses and configured non-retired provider/model routes are represented in the complete matrix.
- Lanes represent lifecycle/status enum plus independent behavior fields such as dispatch_enabled, shadow_enabled, route_selectable, waiver_id, and blockage reasons.
- Missing/stale evidence fails closed for production projection.
- Production ranking activation remains unavailable until later governed activation evidence and GO.

## Risks / Rollback

Risk is moderate because this introduces new authority tables/projections that the dispatcher will later consume. Mitigation: Wave 1 is schema/projection only and does not activate production ranking.

Rollback is a source/test revert plus append-only retirement/supersession of new formal records or schema-projection use. Existing OPS lifecycle authority and dispatcher runtime behavior must continue to operate if this projection is absent.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher/`
- `groundtruth-kb/src/groundtruth_kb/bridge/`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `config/dispatcher/`
- `harness-state/harness-registry.json`
- `scripts/benchmarks/`
- `scripts/ops/dispatch_parity.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/`
- `platform_tests/groundtruth_kb/`
- `groundtruth-kb/tests/`

## Recommended Commit Type

`feat`
