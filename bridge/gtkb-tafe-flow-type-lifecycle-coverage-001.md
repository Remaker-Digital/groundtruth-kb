NEW

# WI-4500–4503: TAFE Flow-Type Lifecycle Coverage (operation, remediation, deliberation, report)

bridge_kind: prime_proposal
Document: gtkb-tafe-flow-type-lifecycle-coverage
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: fa1f93c9-018a-4328-9c1a-e5f3a1921c9e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; autonomous Prime Builder declared via ::init gtkb pb; explanatory output style; owner-authorized /loop autonomous drive

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-TRANCHE-2-LEASE-RECOVERY-FLOW-TYPES-WI-4494-4500-4503
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4500

target_paths: ["groundtruth-kb/tests/test_tafe_flow_type_lifecycle.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: test:

---

## Summary

Implement the remaining flow-type work for `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE` — WI-4500 (Operation), WI-4501 (Remediation), WI-4502 (Deliberation), WI-4503 (Report) — as an **executable specification**: a single parameterized full-lifecycle test that proves each of the four flow types can be seeded, instantiated, and advanced through its declared stage sequence with its declared per-stage role gates, AUQ-gate positions, and never-self-review constraints, using the already-generic TAFE runtime.

This is **test-only** by design and by evidence:

- The five canonical flow definitions (including operation/remediation/deliberation/report) already exist as VERIFIED seed records in `CANONICAL_REVIEWED_TASK_FLOW_DEFINITIONS` (`groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py:31-112`), each carrying `stage_sequence`, `required_roles_by_stage`, `auq_gate_positions`, and `never_self_review_stages` (WI-4489).
- The runtime (`FlowRuntimeService`/`TypedArtifactFlowService`) is intentionally **flow-type-agnostic**: `create_flow_instance` / `create_stage_instance` / `claim_stage_lease` / `release_stage_lease` walk the definition's `stage_sequence` with no per-flow-type branching, handler, executor, validator, or registry anywhere in `groundtruth-kb/src/`.
- Consequently the remaining "implementation" of these four flow types is the **verification that each declared flow-type contract holds end-to-end** through the generic runtime. Today only the `implementation` flow type has full-lifecycle test coverage; operation/remediation/deliberation/report have ~0 lifecycle coverage. This slice closes that gap.

The new test file mirrors the existing canonical lifecycle test `groundtruth-kb/tests/test_tafe_runtime_tables.py::test_runtime_service_round_trips_current_history_events_and_artifacts` (lines 87-182), parameterized over the four flow types.

## Scope and Multi-Work-Item Note

The bridge-compliance gate captures a **single** `Work Item:` metadata line, so this thread cites **WI-4500** (Operation) as the gate primary. The parameterized test in scope covers all four flow-type work items — WI-4500 (operation), WI-4501 (remediation), WI-4502 (deliberation), WI-4503 (report) — which are bundled together in the active tranche-2 Project Authorization `...TAFE-TRANCHE-2-LEASE-RECOVERY-FLOW-TYPES-WI-4494-4500-4503` (owner decision `DELIB-20263160`). Each flow type is an explicit, individually-named `pytest.mark.parametrize` case, so per-flow-type traceability is preserved in the test output. On VERIFIED, WI-4500-4503 each resolve against this thread (mirroring the resolution pattern already used for sibling tranche WIs).

If Loyal Opposition prefers four separate single-WI threads instead of one bundled thread, NO-GO with that direction and Prime Builder will split into per-WI proposals.

## Bounding (explicit out-of-scope)

This slice ships **lifecycle test coverage only**. It MUST NOT:

- Change any source under `groundtruth-kb/src/` (the runtime is already generic and the definitions already seeded; no per-flow-type handler is added). Only the new test file is created.
- Stand up a **live dispatch substrate**, perform **session-initiation**, route real work through TAFE, or actuate any flow live. The tranche-2 PAUTH forbids `live_dispatch_substrate`; advisory-004 Condition 2 reserves any live implementation-flow pilot for a separate owner decision. This slice exercises only in-test (non-live) flow records in a temporary database.
- Perform **cutover** or **dual-write** toward `bridge/INDEX.md` (PAUTH forbids `cutover`; `GOV-FILE-BRIDGE-AUTHORITY-001` keeps the live `bridge/INDEX.md` canonical).
- Change MemBase schema (`kb_schema_change` is forbidden by the PAUTH; the test runs against a fresh temporary `KnowledgeDB` whose schema is created by existing migrations).
- Add a CLI command, hook, scheduled task, poller, or alert rule.
- Promote any spec status (advisory-004: "does not authorize ... formal spec promotion").

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — TAFE governs reviewed task flows as typed, staged artifacts; this slice proves the four remaining typed flows are instantiable and advanceable as specified, with `bridge/INDEX.md` preserved as canonical until a separate governed cutover.
- `SPEC-TAFE-R1` (Controlled Artifact Routing) — each flow type routes its subject through an ordered, role-gated stage sequence; the test asserts the declared `stage_sequence` and `required_roles_by_stage` per flow type drive the lifecycle.
- `SPEC-TAFE-R7` (Interface Principle) — MemBase remains canonical and is reached through the existing Python service API; the test uses only the public `TypedArtifactFlowService` surface and a temporary DB, mutating no canonical state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the live `bridge/INDEX.md` remains the canonical workflow state; this slice is test-only, reads/writes no bridge index, and changes no bridge-authority behavior (verified by the post-run `bridge/INDEX.md` smoke check).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — PAUTH, project, work item, target paths, and governing specs are concretely linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable project-authorization metadata is in the header; the cited WI-4500 is an active member of the cited project and is in the cited PAUTH's `included_work_item_ids`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps each linked spec clause (per-flow-type stage sequence, role gates, AUQ-gate metadata, never-self-review metadata, lifecycle advance) to executed test assertions.
- `GOV-STANDING-BACKLOG-001` — WI-4500-4503 are the backlog authority for this slice; cutover-class WI-4508/4509/4510 remain excluded.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds under the active tranche-2 PAUTH (`DELIB-20263160`) plus the forthcoming Loyal Opposition GO and an implementation-start packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the test target is inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the lifecycle test is a durable governed verification artifact; WI-4500-4503 stay unresolved until terminal VERIFIED.

## Prior Deliberations

- `DELIB-20263160` — owner decision backing the active tranche-2 PAUTH that explicitly authorizes WI-4500-4503 flow-type implementations (source + test; cutover/live-dispatch/schema-change forbidden).
- `bridge/gtkb-typed-artifact-flow-engine-advisory-004.md` — GO constrained to advisory/planning; Condition 2 reserves a live implementation-flow pilot for a separate owner decision. This slice respects that by being non-live (in-test records only).
- `bridge/gtkb-tafe-flow-definition-seed-records-004.md` — VERIFIED seed records for the five flow families this test exercises (WI-4489).
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` — VERIFIED `flow_instances` + `stage_instances` runtime substrate the test drives; the closest existing lifecycle-test template lives in this thread's test file.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` — owner approval promoting the TAFE R-specs to `specified`; the flow types verified here implement state defined by those specs.
- No prior deliberations found for per-flow-type lifecycle test coverage of operation/remediation/deliberation/report (`search_deliberations("TAFE operation remediation deliberation report flow type lifecycle test coverage")` returned no matches on 2026-06-13). This is the first lifecycle-coverage slice for these four flow types, not a revisit of a rejected approach.

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-20263160`** — the owner decision backing the active tranche-2 PAUTH whose `scope_summary` explicitly authorizes "WI-4500-4503 flow-type implementations. GT-KB platform code/tests only under `E:/GT-KB`; `bridge/INDEX.md` remains canonical (no cutover); no new live dispatch substrate or session-initiation." This slice respects every clause (test-only; no live dispatch; no cutover; no schema change).
- **Owner-authorized autonomous drive directive (2026-06-13)** — the standing owner directive for this session is to drive `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE` to completion autonomously using live project state. WI-4500-4503 are the remaining tranche-2-authorized items now that WI-4494/4498/4499/4504/4505/4506 are resolved and WI-4507 is in flight under another session's claim.
- The slice stays strictly within the `test` mutation class (a subset of the PAUTH's `source`/`test`) and respects every `forbidden_operations` clause (`cutover`, `live_dispatch_substrate`, `kb_schema_change`). No expanded owner authorization is requested.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` and `SPEC-TAFE-R1` define the four flow types as ordered, role-gated stage sequences; `SPEC-TAFE-R7` keeps MemBase canonical and constrains derived/test access to the public service API. The tranche-2 PAUTH (owner decision `DELIB-20263160`) explicitly enumerates WI-4500-4503 with the source/test mutation classes. No new or revised requirement is needed: this slice verifies the already-specified, already-seeded flow-type contracts hold through the already-generic runtime, and explicitly excludes any live-dispatch, cutover, or schema change.

## Implementation Plan

Create `groundtruth-kb/tests/test_tafe_flow_type_lifecycle.py` (new file) containing a parameterized full-lifecycle test plus per-flow-type contract assertions.

1. **Fixture / helper** — a `_service(tmp_path)` helper returning `(KnowledgeDB(tmp_path / "groundtruth.db"), TypedArtifactFlowService(db))`, mirroring `test_tafe_runtime_tables.py:9-11`.
2. **Contract data** — a parametrize table of the four flow types with their expected canonical contract, sourced from `CANONICAL_REVIEWED_TASK_FLOW_DEFINITIONS`:
   - operation: `["plan","execute","verify","complete"]`, AUQ `["after:plan"]`, never-self-review `["verify"]`.
   - remediation: `["diagnose","propose_fix","review","implement","verify","complete"]`, AUQ `["after:diagnose"]`, never-self-review `["review","verify"]`.
   - deliberation: `["surface","investigate","decide","record","complete"]`, AUQ `["before:decide"]`, never-self-review `["investigate","record"]`, with `decide` requiring role `owner`.
   - report: `["investigate","draft","review","finalize","complete"]`, AUQ `["after:review"]`, never-self-review `["review"]`.
3. **Definition-contract test** (`test_flow_type_definition_contract`) — seed via `service.seed_reviewed_task_flow_definitions(...)`, then for each flow type assert `get_flow_definition(flow_type)` returns the expected `stage_sequence`/`required_roles_by_stage_parsed`/`auq_gate_positions`/`never_self_review_stages` parsed fields. This locks each declared per-flow-type contract.
4. **Lifecycle test** (`test_flow_type_full_lifecycle`, parametrized over the four flow types) — seed definitions; `create_flow_instance(flow_definition_id=<flow_type>, status="created", ...)`; create one `stage_instance` per stage in `stage_sequence`, deriving each stage's `required_role` from the definition's `required_roles_by_stage_parsed` (not hardcoded); advance the flow instance to `in_progress` setting `current_stage_instance_id`; `claim_stage_lease` then `release_stage_lease` on the first stage; assert: flow instance current `status`, version monotonicity, stage count equals `len(stage_sequence)`, each stage's `required_role` matches the definition, lease `lease_status` transitions active→released, and `list_stage_instances` returns the full ordered set. No `bridge/INDEX.md` is read or written; all records live in the temporary DB.
5. **AUQ-gate + never-self-review metadata test** (`test_flow_type_gate_metadata`) — assert the seeded definition's `auq_gate_positions` reference real stages in the sequence and `never_self_review_stages` reference real stages, per flow type (a non-live consistency check that the declared gate metadata is internally coherent).

All assertions exercise the public `TypedArtifactFlowService` API; no private members, no canonical-DB mutation, no live dispatch.

## Spec-Derived Verification Plan

The implementation report will include these commands and expected outcomes:

```text
python -m pytest groundtruth-kb/tests/test_tafe_flow_type_lifecycle.py -q --tb=short
Expected: pass; exercises the four flow types' definition contracts, full instantiate→stage→lease→advance lifecycle, and AUQ/never-self-review metadata coherence.

python -m ruff check groundtruth-kb/tests/test_tafe_flow_type_lifecycle.py
python -m ruff format --check groundtruth-kb/tests/test_tafe_flow_type_lifecycle.py
Expected: pass (both gates).

git diff --check -- groundtruth-kb/tests/test_tafe_flow_type_lifecycle.py
Expected: no output, exit 0.

# Live bridge/INDEX.md unchanged after the test run (smoke check):
git status --short bridge/INDEX.md
Expected: empty output (no change).
```

Spec mapping:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` + `SPEC-TAFE-R1` — `test_flow_type_definition_contract` + `test_flow_type_full_lifecycle` prove each flow type's declared ordered, role-gated stage sequence is instantiable and advanceable.
- `SPEC-TAFE-R7` — the tests use only the public service API against a temporary DB; no canonical MemBase mutation (verified by the `bridge/INDEX.md` smoke check and test isolation).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — each linked spec maps to executed test assertions enumerated above.

## Risk / Rollback

Primary risk is scope creep from "lifecycle coverage" into live-dispatch or per-flow-type handler territory. Mitigation: the slice creates exactly one new test file (no `src/` change), drives only in-test records in a temporary DB, and asserts no live dispatch occurs. The PAUTH's `forbidden_operations` (`cutover`, `live_dispatch_substrate`, `kb_schema_change`) are each respected and called out in the Bounding section.

Secondary risk is that a flow type's generic-runtime lifecycle surfaces a latent defect (e.g., a stage-advance edge case). If the test discovers a genuine source defect, that is a NO-GO/REVISED trigger: Prime Builder will surface the defect as a finding and either scope a bounded source fix under the tranche-2 PAUTH's `source` mutation class (in a REVISED proposal) or capture it as a separate work item, rather than silently widening this slice.

Tertiary risk is multi-WI traceability ambiguity (one thread, four WIs). Mitigation: each flow type is an explicitly-named parametrize case, the PAUTH bundles all four, and the body documents the gate-single-WI constraint; Loyal Opposition may NO-GO toward per-WI threads if preferred.

Rollback is a single-commit revert of the new test file. No source change, no KB mutation, no schema change, no integration to unwind.

## Recommended Commit Type

`test:` — adds a single new test file providing full-lifecycle coverage for the four remaining TAFE flow types; no source behavior change, no new capability surface, no canonical bridge authority change, no live dispatch.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
