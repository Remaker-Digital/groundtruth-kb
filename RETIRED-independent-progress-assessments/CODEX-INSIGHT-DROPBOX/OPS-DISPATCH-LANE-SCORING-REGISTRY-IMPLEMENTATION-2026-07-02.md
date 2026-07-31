NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

# WI-4958 Dispatch Lane-Scoring Registry And Projections Implementation Report

bridge_kind: implementation_report
Document: gtkb-dispatch-lane-scoring-registry-projections
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-dispatch-lane-scoring-registry-projections-002.md
Supplemental GO: bridge/gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment-002.md
Approved proposal: bridge/gtkb-dispatch-lane-scoring-registry-projections-001.md
Supplemental proposal: bridge/gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment-001.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY-WI-4958
Work Item: WI-4958
Recommended commit type: feat:

## Implementation Claim

WI-4958 now has a non-activating Wave 1 lane-scoring foundation:

- MemBase schema creates append-only lane, score-dimension, scoring-evidence, score-snapshot, and projection-snapshot tables with current views and indexes.
- `groundtruth_kb.dispatcher.lane_scoring` seeds advisory role/activity lanes from caller-supplied harness projection data, keeps native harness model routes fixed and non-selectable, and renders compact shadow/production projections.
- Production projection remains fail-closed unless a lane is approved, dispatch-enabled, and backed by fresh required parity, readiness, and benchmark evidence.
- Runtime dispatcher target selection, `config/dispatcher/rules.toml`, `scripts/gtkb_dispatcher_daemon.py`, `scripts/dispatcher_runtime.py`, and `harness-state/harness-registry.json` were not changed by this slice.

The implementation is schema/projection only. It does not activate production ranking or replace dispatcher daemon routing.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

`GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` is cited per the parent GO finding. The implementation reads caller-supplied harness projection mappings and tests that the helper does not write a harness registry file.

## Prior Deliberations

- `DELIB-20260702-DISPATCH-RANKING-ATOMIC-TARGET` - dispatch target = harness + provider/model route + role/activity lane.
- `DELIB-20260702-DISPATCH-LANE-MATRIX-SCOPE` - complete role/activity lane matrix with explicit toggles.
- `DELIB-20260702-DISPATCH-LANE-ACTIVITY-VOCAB-V1` - v1 activity vocabulary is build, test, spec, ops, project, deliberation.
- `DELIB-20260702-DISPATCH-SCORING-REGISTRY-SOT` - lane matrix and snapshots live in a separate governed scoring registry/table.
- `DELIB-20260702-DISPATCH-LANE-SCORING-MEMBASE-AUTHORITY-SEPARATE-DOMAIN` - lane scoring uses MemBase/KB authority in a domain separate from OPS lifecycle.
- `DELIB-20260702-DISPATCH-LIFECYCLE-FIRST-SCORING-LAST-PRECEDENCE` - lifecycle eligibility precedes lane scoring.
- `DELIB-20260702-DISPATCH-LANE-LIFECYCLE-ENUM-PLUS-FIELDS` - lanes use lifecycle plus independent behavior fields.
- `DELIB-20260702-DISPATCH-MODEL-ROUTE-LANE-IDENTITY` - provider/model route is part of lane identity.
- `DELIB-20260702-DISPATCH-NATIVE-HARNESS-FIXED-ROUTE-LANES` - native harnesses use fixed configured routes when not launch-selectable.
- `DELIB-20260702-DISPATCH-PRODUCTION-LANE-MINIMUM-EVIDENCE` - production lanes require parity, readiness, and benchmark/performance evidence.
- `DELIB-20260702-DISPATCH-COMPACT-HOT-PATH-LANE-PROJECTION` - dispatcher hot path consumes compact generated projection only.
- `DELIB-20260702-DISPATCH-LANE-SCORING-SHADOW-ROLLOUT` - rollout starts shadow/advisory before governed activation.
- `DELIB-20260702-DISPATCH-OPS-DIAGNOSIS-AS-OPS-ACTIVITY-SUBTYPE` - OPS diagnosis/remediation remain activity=ops subtypes.
- `bridge/gtkb-dispatch-lane-scoring-registry-projections-002.md` - LO GO authorizing implementation and requiring harness-registry write clarification.
- `bridge/gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment-002.md` - LO GO authorizing exact helper/export/test target paths and requiring split-packet documentation.

## Authorization Evidence

- Parent latest bridge status before implementation: `GO` at `bridge/gtkb-dispatch-lane-scoring-registry-projections-002.md`.
- Supplemental latest bridge status before implementation: `GO` at `bridge/gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment-002.md`.
- Parent work-intent claim: rowid `28433`, session `019f23f0-b16e-7481-8a18-9622ab564d50`, `claim_kind: go_implementation`, extended once, `ttl_expires_at: 2026-07-02T20:58:16Z`.
- Supplemental work-intent claim: rowid `28434`, session `019f23f0-b16e-7481-8a18-9622ab564d50`, `claim_kind: go_implementation`, extended once, `ttl_expires_at: 2026-07-02T20:58:16Z`.
- Parent implementation-start packet: `sha256:552eb756a0502f4cf075acac4f8d2298dedf910d86f01ef8391cd441c68a4e58`, expires `2026-07-02T21:18:32Z`, used for `groundtruth-kb/src/groundtruth_kb/db.py`.
- Supplemental implementation-start packet: `sha256:cddd81fa614416b3c2d092cb6afc341c6feab63fb54ab1caa478dfefb9b26b7a`, expires `2026-07-02T21:18:32Z`, used for `groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py`, `groundtruth-kb/src/groundtruth_kb/dispatcher/__init__.py`, and `platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py`.
- Parent exact target preflight: `groundtruth-kb/src/groundtruth_kb/db.py` returned `verdict: in_scope`.
- Supplemental exact target preflight: helper/export/test files returned `verdict: in_scope`.

This directly addresses the supplemental GO P2 finding: the implementation used two distinct packets and records which paths each packet governed.

## Files Changed

WI-4958 implementation-owned paths:

- `groundtruth-kb/src/groundtruth_kb/db.py` - added dispatch lane-scoring schema, current views, indexes, JSON parsing hooks, lane upsert/list helpers, and projection snapshot helpers.
- `groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py` - new advisory lane-scoring helper module.
- `groundtruth-kb/src/groundtruth_kb/dispatcher/__init__.py` - exported the lane-scoring helper API.
- `platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py` - new focused schema/projection test coverage.

Scope separation notes:

- `harness-state/harness-registry.json` has unrelated pre-existing worktree changes, but this WI-4958 slice did not edit it.
- `config/dispatcher/rules.toml` has unrelated pre-existing worktree changes, but this WI-4958 slice did not edit dispatcher rules.
- No Agent Red application source, credential file, production deployment config, dispatcher daemon runtime file, or release worktree file was changed by this slice.

## Architecture Alignment Ledger

| Axis | Alignment evidence |
| --- | --- |
| OPS consolidation | Lane-scoring is implemented as a separate MemBase authority domain and helper surface, preserving the owner decision that OPS lifecycle decides eligibility before scoring chooses between eligible routes. |
| Dispatcher daemon architecture | The helper builds compact advisory/projection payloads only; daemon runtime files and dispatcher rules are untouched, so live dispatch continues through the existing dispatcher daemon control plane. |
| Lifecycle-first/scoring-last precedence | Lane records carry lifecycle, dispatch_enabled, shadow_enabled, route_selectable, blockage reasons, and evidence counts. Production projection fails closed unless lifecycle/evidence gates pass. |
| Portfolio reconciliation findings | The slice stays inside canonical `PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY`/`WI-4958` scope and does not fold release-dispatcher, TAFE, runtime-orchestration, AUQ, or parity projects into this work. |

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirmed parent and supplemental latest statuses are `GO`, held matching claims, held valid implementation-start packets, and reran exact target preflights before/after edits. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Both implementation-start packets resolved `PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY`, `WI-4958`, and the active PAUTH. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report links all parent blocking specs plus the harness-state governance spec requested by LO. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests cover schema creation, lane seeding, compact projection shape, fail-closed production projection, append-only projection snapshots, and read-only harness-registry behavior. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation files are under `E:/GT-KB`; no Agent Red source was touched. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Runtime ranking activation and dispatcher rules edits stayed out of scope; projection mode remains `shadow_advisory` unless explicitly invoked as production, where it fails closed. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | The schema/projection foundation can feed dispatcher target evidence later, but no production dispatcher selection was activated in this slice. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | The dispatcher daemon remains the control plane; this slice adds a reusable projection helper instead of a parallel dispatcher path. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | Test coverage proves `lanes_from_harness_projection` reads caller-provided projection data without writing `harness-state/harness-registry.json`. |
| Artifact-oriented governance specs | The report preserves authorization, architecture alignment, and lifecycle evidence as durable review input rather than relying on transcript memory. |

## Commands Run

- `gt bridge threads --wi WI-4958 --json --compact`
- `python scripts\bridge_claim_cli.py status gtkb-dispatch-lane-scoring-registry-projections`
- `python scripts\bridge_claim_cli.py status gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment`
- `python scripts\bridge_claim_cli.py extend gtkb-dispatch-lane-scoring-registry-projections --session-id 019f23f0-b16e-7481-8a18-9622ab564d50`
- `python scripts\bridge_claim_cli.py extend gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment --session-id 019f23f0-b16e-7481-8a18-9622ab564d50`
- `python scripts\implementation_authorization.py list`
- `python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-dispatch-lane-scoring-registry-projections --candidate-paths groundtruth-kb/src/groundtruth_kb/db.py --json`
- `python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment --candidate-paths groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py groundtruth-kb/src/groundtruth_kb/dispatcher/__init__.py platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py --json`
- `python -m pytest platform_tests\groundtruth_kb\test_dispatch_lane_scoring_projection.py -q --tb=short`
- `python -m pytest groundtruth-kb\tests\test_db.py -q --tb=short`
- `python -m ruff check groundtruth-kb\src\groundtruth_kb\dispatcher\lane_scoring.py groundtruth-kb\src\groundtruth_kb\dispatcher\__init__.py groundtruth-kb\src\groundtruth_kb\db.py platform_tests\groundtruth_kb\test_dispatch_lane_scoring_projection.py`
- `python -m ruff format --check groundtruth-kb\src\groundtruth_kb\dispatcher\lane_scoring.py groundtruth-kb\src\groundtruth_kb\dispatcher\__init__.py groundtruth-kb\src\groundtruth_kb\db.py platform_tests\groundtruth_kb\test_dispatch_lane_scoring_projection.py`

## Observed Results

- `gt bridge threads --wi WI-4958 --json --compact`: 2 matching threads; parent latest `GO`, exact-target amendment latest `GO`.
- Parent claim status before extension: held by this session, latest bridge status `GO`, not expired.
- Supplemental claim status before extension: held by this session, latest bridge status `GO`, not expired.
- Claim extension: both parent and supplemental holds extended to `ttl_expires_at: 2026-07-02T20:58:16Z`.
- `implementation_authorization.py list`: both WI-4958 packets valid until `2026-07-02T21:18:32Z`.
- Parent target preflight: `groundtruth-kb/src/groundtruth_kb/db.py` in scope.
- Supplemental target preflight: helper/export/test files in scope.
- Focused test: `6 passed in 1.06s`.
- DB adjacency test: `108 passed, 1 warning in 40.82s`; warning was a third-party ChromaDB deprecation warning for `asyncio.iscoroutinefunction`.
- Ruff check: `All checks passed!`
- Ruff format check: `4 files already formatted`.

## Acceptance Criteria Status

- [x] Lane-scoring registry/schema artifacts exist with append-only current views for lanes and projection snapshots.
- [x] Projection helper seeds role/activity lanes from non-retired harness projection data.
- [x] Provider/model route is part of lane identity, and native fixed routes remain `route_selectable=False`.
- [x] Lifecycle and behavior fields are distinct: `lifecycle`, `dispatch_enabled`, `shadow_enabled`, `route_selectable`, `blockage_reasons`, `caps`, and evidence metadata are separate.
- [x] Compact projection omits raw evidence payloads and carries only compact counts/metadata.
- [x] Production projection fails closed without approved lifecycle, dispatch enablement, and fresh parity/readiness/benchmark evidence.
- [x] Projection snapshots are append-only by version.
- [x] Helper does not write `harness-state/harness-registry.json`.
- [x] Runtime dispatcher ranking activation remains out of scope.

## Risk And Rollback

Residual risk is limited to schema/API shape before later producers consume the lane-scoring registry. The rollout is non-activating and shadow/advisory only, so rollback is a normal source revert of:

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher/__init__.py`
- `platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py`

No database content migration was run against production data, no runtime dispatcher route selector was changed, and bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the split authorization evidence against the parent and amendment GO verdicts.
2. Verify that no harness-state or dispatcher-config write is attributable to this slice.
3. Verify the schema/projection implementation against the linked specifications and command evidence.
4. Return `VERIFIED` if WI-4958 satisfies the Wave 1 schema/projection foundation, otherwise return `NO-GO` with concrete findings.
