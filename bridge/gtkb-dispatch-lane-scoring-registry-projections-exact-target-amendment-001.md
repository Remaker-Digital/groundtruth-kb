NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5
author_model_version: 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb; build envelope PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION

# Implementation Proposal - WI-4958 Exact Target Path Amendment

bridge_kind: prime_proposal
Document: gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment
Version: 001
Date: 2026-07-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY-WI-4958
Project: PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY
Work Item: WI-4958

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/__init__.py", "platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py"]

implementation_scope: source+tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Scope amendment for `WI-4958`: authorize exact helper/export/test paths needed for the dispatch lane-scoring registry/projection implementation. The approved parent proposal listed directory-shaped target paths (`groundtruth-kb/src/groundtruth_kb/dispatcher` and `platform_tests/groundtruth_kb`), but the implementation-start target-path preflight treats those entries as non-recursive and rejects concrete files under them.

This amendment does not activate production lane ranking, does not modify dispatcher runtime target selection, and does not authorize writes to `harness-state/harness-registry.json` or `config/dispatcher/rules.toml`.

## Claim

Prime Builder proposes a narrow target-path correction so the already-GO-approved lane-scoring foundation can be implemented and verified without relying on ambiguous directory authorization. The amendment converts implementation intent into exact file paths accepted by the protected-file preflight.

## Requirement Sufficiency

Existing requirements sufficient.

The owner-approved OPS Dispatcher Modernization Wave 1 decisions and active `PAUTH-PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY-WI-4958` authorize bounded source and test work after Loyal Opposition GO. This amendment keeps the same project and work item, but narrows the authorized implementation delta to helper/export/test files needed for the advisory lane-scoring projection foundation.

## In-Root Placement Evidence

All target paths are inside `E:/GT-KB`:

- `groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher/__init__.py`
- `platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py`

No Agent Red application source, external archive, deployment surface, dispatcher config, harness-state projection, or credential file is in scope.

## Architecture Alignment Ledger

| Alignment Axis | Evidence |
| --- | --- |
| OPS consolidation | Preserves the owner decision that lane scoring is a separate authority domain from OPS lifecycle. |
| Dispatcher daemon architecture | Adds only advisory projection helpers/tests; no daemon spawn, runtime dispatch, or target-selection activation changes are proposed. |
| Lifecycle-first / scoring-last precedence | The helper/test scope must encode lifecycle-first/scoring-last metadata and fail production projection closed until evidence exists. |
| Portfolio reconciliation | `WI-4960` remains latest `NEW`; this amendment is limited to a mechanical authorization gap discovered by the `WI-4958` implementation-start preflight and does not decide duplicate/stale project-family cleanup. |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge-mediated source/test changes must stay within live GO and target-path authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the target-path gap is preserved as a governed bridge artifact instead of an implicit workspace change.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this amendment includes project authorization, project, work item, and exact target-path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map implementation behavior to executed tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lane lifecycle values must remain explicit and fail closed.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is maintained across the parent GO, this amendment, implementation report, and verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all mutations remain in the GT-KB platform root and out of Agent Red application source.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatcher rules remain what/when authority; lane scoring ranks who only after lifecycle eligibility.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the centralized dispatcher remains the control plane; no harness-side target decision is introduced.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon architecture is preserved; production ranking activation remains out of scope.

## Prior Deliberations

- `DELIB-20260702-DISPATCH-RANKING-ATOMIC-TARGET` - dispatch target is harness + provider/model route + role/activity lane.
- `DELIB-20260702-DISPATCH-LANE-MATRIX-SCOPE` - complete role/activity lane matrix with explicit toggles.
- `DELIB-20260702-DISPATCH-LANE-ACTIVITY-VOCAB-V1` - v1 activity vocabulary uses build, test, spec, ops, project, deliberation.
- `DELIB-20260702-DISPATCH-SCORING-REGISTRY-SOT` - lane matrix and snapshots live in a separate governed scoring registry/table.
- `DELIB-20260702-DISPATCH-LANE-SCORING-MEMBASE-AUTHORITY-SEPARATE-DOMAIN` - lane scoring uses MemBase/KB authority in a separate domain from OPS lifecycle.
- `DELIB-20260702-DISPATCH-LIFECYCLE-FIRST-SCORING-LAST-PRECEDENCE` - OPS lifecycle eligibility precedes lane scoring.
- `DELIB-20260702-DISPATCH-LANE-SCORING-SHADOW-ROLLOUT` - rollout starts shadow/advisory before governed activation.
- `bridge/gtkb-dispatch-lane-scoring-registry-projections-002.md` - Loyal Opposition GO approved implementation and required Prime to avoid unnecessary `harness-state/harness-registry.json` writes.

## Owner Decisions / Input

- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected actual governed project/work-item/bridge proposal creation.
- `PAUTH-PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY-WI-4958` - active project authorization covering bounded `WI-4958` source, schema, generated-projection, and test work after GO.

## Proposed Scope

- Add `groundtruth_kb.dispatcher.lane_scoring` as the advisory lane-scoring helper module.
- Export the helper surface from `groundtruth_kb.dispatcher.__init__` for later dispatcher slices.
- Add focused tests covering schema creation, complete non-retired harness/role/activity lane population, compact hot-path projection shape, lifecycle-first/scoring-last evidence, production fail-closed behavior, and append-only projection snapshots.

## Out Of Scope

- Editing `groundtruth-kb/src/groundtruth_kb/db.py`; that remains authorized by the parent `WI-4958` GO.
- Editing `harness-state/harness-registry.json`; the lane helper reads generated harness projection data but does not write it.
- Editing `config/dispatcher/rules.toml`.
- Implementing runtime target selection, production utility ranking, telemetry automation, or production lane-scoring activation.
- OPS lifecycle/protocol behavior (`WI-4957`) and AUQ/headless launch hygiene (`WI-4959`).

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `impl_start_target_paths_preflight.py` passes for the exact helper/export/test paths under this amendment plus parent-authorized `db.py`. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Focused tests prove the projection is advisory and does not overload dispatcher config with raw scoring evidence. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused tests prove compact projection data is sufficient for later centralized dispatcher consumption without harness-side target decisions. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Source review and tests confirm no daemon/runtime dispatch activation is changed. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tests prove lifecycle/status fields are explicit and production projection fails closed when required evidence is missing. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path preflight proves every mutation remains under `E:/GT-KB` and no Agent Red application source is changed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps all helper/schema/projection behavior to executed tests. |

Minimum commands expected after implementation:

```text
python scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment --candidate-paths groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py groundtruth-kb/src/groundtruth_kb/dispatcher/__init__.py platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py --json
python -m pytest platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_db.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py groundtruth-kb/src/groundtruth_kb/dispatcher/__init__.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py
```

## Acceptance Criteria

- Exact target-path preflight passes for all helper/export/test files.
- Lane-scoring helper does not write `harness-state/harness-registry.json`.
- Projection output is compact and omits raw evidence payloads.
- Lane identity includes harness, provider, model route, durable role, and activity type.
- All registered non-retired harness role/activity lanes can be seeded from a harness projection.
- Production projection fails closed when required evidence is missing or stale.
- Runtime dispatcher target selection and production lane-ranking activation remain unchanged.

## Risks / Rollback

Risk is low to moderate. The amendment touches only a new helper, package export, and tests, but it enables a larger schema/projection foundation. Mitigation is exact target-path preflight plus focused tests before any report.

Rollback is normal source/test revert of these exact files. Bridge files remain append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher/__init__.py`
- `platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py`

## Recommended Commit Type

`feat`
