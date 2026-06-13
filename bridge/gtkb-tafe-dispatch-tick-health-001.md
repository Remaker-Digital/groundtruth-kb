NEW

# TAFE `gt flow dispatch tick` / `dispatch health` (Need-Driven Evaluation) Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-dispatch-tick-health
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: fa771f21-61e3-4123-9427-e73327ca1f1f
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; default

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-DISPATCH-TRACK-WI-4497-4498-4499
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4499

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_dispatch_runtime.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4499, the `gt flow dispatch tick` and `gt flow dispatch health` command surface, as a **need-driven evaluation and observability layer** over the WI-4498 dispatch policy engine. `tick` evaluates actual dispatch *need* (SPEC-TAFE-R5) by reading current flow/stage state and capability snapshots, composes `DispatchNeed` + `DispatchCandidate` inputs, and invokes `select_dispatch_target` (the VERIFIED-pending WI-4498 engine) to compute — and report — what *would* be dispatched for each eligible unclaimed stage. `health` aggregates dispatch readiness (pending stages, eligible candidates by role, stale/owner-gated/blocked counts).

The work is structured as a pure, injected-service runtime module (`tafe_dispatch_runtime.py`) returning structured reports, plus a thin Click CLI wrapper added to the existing `flow` group in `cli.py`. This mirrors the WI-4498 engine's functional-core / imperative-shell shape and keeps the need-evaluation logic unit-testable against a temporary MemBase.

WI-4498 (the engine this layer consumes) is implemented and reported at `bridge/gtkb-tafe-dispatch-policy-engine-003.md` (pending Loyal Opposition VERIFIED). Its public API (`DispatchNeed`, `DispatchCandidate`, `select_dispatch_target`, `evaluate_eligibility`) is the stable contract this layer builds on.

### Bounding (explicit out-of-scope)

This slice is **evaluation, computation, and reporting only**. It MUST NOT:

- Perform any actual dispatch, harness spawning, subprocess launch, session initiation, or live routing. `tick` computes and reports decisions; it does not act on them. Per SPEC-TAFE-R5, scheduled wakes may *evaluate* need but must not bulk-initiate sessions.
- Create or register any new dispatch substrate, scheduled task, hook, or poller. The cross-harness event-driven trigger and `bridge/INDEX.md` remain the canonical live dispatch state per `GOV-FILE-BRIDGE-AUTHORITY-001` and the `gtkb-typed-artifact-flow-engine-advisory` GO conditions (no cutover; existing file bridge remains canonical).
- Mutate MemBase, `stage_leases`, owner-gate state, workspace state, `bridge/INDEX.md`, or any flow/stage row. Reads only. No claim/release/heartbeat (that is WI-4493) and no lease recovery (WI-4494).
- Persist telemetry. Per-stage-attempt telemetry recording is WI-4504; this slice surfaces decision evidence in command output for live inspection but writes no telemetry store.
- Implement implementation-flow routing, generated-view authority, dual-write, pilot-eligibility expansion, or governed cutover. A live implementation-flow pilot requires a separate owner decision and a separate bridge proposal per `bridge/gtkb-typed-artifact-flow-engine-advisory-004.md` Condition 2.

This bounding keeps the slice strictly within the active dispatch-track PAUTH scope ("dispatch tick/health CLI; GT-KB platform code/tests only; bridge/INDEX.md remains canonical; no cutover").

## Specification Links

- `SPEC-TAFE-R5` — the governing requirement: the engine acts on actual need, not blind interval polling; activation is evaluated from state changes, eligible unclaimed work, stale/expired leases, failed/stuck flow detection, owner-gated work surfacing, or explicit operator action, and scheduled wakes that evaluate need must not bulk-initiate sessions lacking actionable information. `tick` is exactly the need-evaluation surface; it surfaces actionable need without initiating sessions.
- `SPEC-TAFE-R4` — `tick` invokes the WI-4498 policy engine to apply the hard eligibility gates first and select by calibrated precedence tiers; this slice adds no new policy logic, it consumes the engine.
- `SPEC-TAFE-R2` — need detection respects single-claim semantics: only eligible *unclaimed* stages (no active stage lease) are candidate dispatch needs; the slice reads lease availability and never mutates leases.
- `SPEC-TAFE-R6` — `tick` and `health` surface the dispatch decision evidence (flow/stage ids, candidate eligibility breakdown, selection rationale, cost) for live observability; persistence of that evidence remains WI-4504.
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — Phase 1 parallel-run substrate; `bridge/INDEX.md` remains canonical until a later governed cutover; this slice adds an observability surface, not a live dispatch substrate.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains the canonical workflow/dispatch state; this slice changes no bridge authority and writes nothing to the index.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — PAUTH, project, work item, target paths, and governing specs are linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable project authorization metadata is present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps R5 need-evaluation, R4 engine invocation, R2 unclaimed-only candidacy, and the non-mutating bound to executed tests.
- `GOV-STANDING-BACKLOG-001` — WI-4499 is the backlog authority for this slice; WI-4493/4494/4500–4510 remain open siblings and are out of scope.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds under the active bounded dispatch-track PAUTH (which already includes WI-4499) plus the forthcoming Loyal Opposition GO.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the runtime layer is durable governed artifact state with a preserved evidence trail.

## Prior Deliberations

- `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613` — active dispatch-track PAUTH owner-decision basis; authorizes WI-4497/WI-4498/WI-4499 including the dispatch tick/health CLI.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` — never-self-review invariant is session-scoped; `tick` candidate composition carries the candidate's active session id so the engine's review-independence gate is honored.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` — owner choice of the TAFE overhaul direction that produced SPEC-TAFE-R4/R5.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` — owner approval promoting the TAFE R-specs to `specified`.
- `bridge/gtkb-typed-artifact-flow-engine-advisory-004.md` — GO constrained to advisory/planning; conditions carried forward (no cutover; `bridge/INDEX.md` canonical; live pilot needs a separate owner decision). This slice respects those conditions by being evaluation-only.
- `bridge/gtkb-tafe-dispatch-policy-engine-003.md` — the WI-4498 engine implementation/report this layer consumes (pending VERIFIED).
- No prior deliberations found for the dispatch tick/health need-evaluation surface: `search_deliberations("dispatch tick health need-driven activation flow runtime")` and `search_deliberations("TAFE dispatch evaluation observability phase 1 no live dispatch")` returned no matches on 2026-06-13. This is the first implementation of the R5 need-evaluation command surface, not a revisit of a rejected approach.

## Owner Decisions / Input

No new owner decision is required to file or implement this proposal. Existing authority is the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-DISPATCH-TRACK-WI-4497-4498-4499` (backed by `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613`), which explicitly includes WI-4499 and bounds it to platform code/tests with no cutover.

Boundary acknowledgement: this slice deliberately stops at *evaluation and reporting*. Wiring `tick` to actually initiate dispatch (a live implementation-flow pilot or any parallel dispatch substrate) is explicitly out of scope and would require a **separate owner decision** per `bridge/gtkb-typed-artifact-flow-engine-advisory-004.md` Condition 2 and the bridge-essential "Adding new bridge automation" gate. No such activation is proposed here.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TAFE-R5` precisely specifies need-driven activation (evaluate need from state changes, eligible unclaimed work, stale leases, stuck flows, owner-gated work, or explicit operator action; do not bulk-initiate). `SPEC-TAFE-R4` (engine), `SPEC-TAFE-R2` (single-claim eligibility), and `SPEC-TAFE-R6` (decision evidence fields) bound the inputs and outputs. No new or revised requirement is needed because this slice implements the specified need-evaluation surface as a non-mutating read/compute/report layer and excludes live activation, telemetry persistence, and cutover.

## Implementation Plan

New module `groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py`:

1. **`evaluate_dispatch_tick(service, *, subject_scope=None, now=None) -> DispatchTickReport`** — a pure, injected-service function:
   - Reads current flow instances (`service.list_flow_instances`) and their stage state to identify stages that are *pending dispatch*: a required role for the stage exists, the stage is not terminal, and the stage has no active lease (SPEC-TAFE-R2 unclaimed-only). Lease availability is read via the existing stage-lease read surface; no lease is created or mutated.
   - Reads current capability snapshots (`service.list_capability_snapshots`, `status="active"`) and maps each to a `DispatchCandidate` (role, subject_scope, health_status, reviewer_precedence, capabilities, active_session_id, `stage_lease_available`, `workspace_available`, cost, model_identifier). The string `workspace_availability` snapshot field maps to the engine's `workspace_available` bool; missing runtime context fails closed at the engine gate.
   - For each pending stage, composes a `DispatchNeed` (required_role, subject_scope, artifact_author_session_id, required_capabilities, owner_gate_blocked, requires_workspace, stage_id, flow_instance_id) and calls `select_dispatch_target(need, candidates)`.
   - Returns a frozen `DispatchTickReport` listing each pending stage's `DispatchDecision` (selected target or `None` + rationale + per-candidate eligibility), plus aggregate counts. `mutated=False` always.
2. **`evaluate_dispatch_health(service, *, subject_scope=None) -> DispatchHealthReport`** — reads snapshot/flow/lease state and returns counts: active candidates by role, pending unclaimed stages, stages with no eligible candidate, stale-lease and owner-gated indicators surfaced from current state. Non-mutating.
3. Module exposes `__all__` with the two report dataclasses and the two functions. It imports `tafe_dispatch_policy` and reads through the injected `TypedArtifactFlowService`; it has **no** `subprocess`, no harness-spawn, no `bridge/INDEX.md` write, and no MemBase write.

CLI wiring in `groundtruth-kb/src/groundtruth_kb/cli.py`:

4. Add a `dispatch` subgroup under the existing `flow` group with two read-only commands: `gt flow dispatch tick` and `gt flow dispatch health`. Each resolves the service via the existing `_flow_service` helper, calls the runtime function, and emits the existing JSON/summary payload shape (`{"...": ..., "mutated": false, "status": "phase1_evaluate_only", "summary": ...}`). `--subject-scope` and `--json` options mirror sibling `flow` commands.

New tests `groundtruth-kb/tests/test_tafe_dispatch_runtime.py` covering: a pending unclaimed stage producing a computed decision; a claimed (leased) stage excluded from need; no-eligible-candidate producing `selected=None` with breakdown; subject-scope filtering; health aggregation counts; `mutated=False` invariant after `tick`/`health` against a temp DB (assert no new rows / unchanged state); a structural test asserting the module source contains no `subprocess`, no `bridge/INDEX.md` write, and exposes no `dispatch_now`/`spawn`/`initiate_session` surface; and CLI tests (Click `CliRunner`) for `flow dispatch tick`/`health` JSON output.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
python -m pytest groundtruth-kb/tests/test_tafe_dispatch_runtime.py -q --tb=short
Expected: pass; exercises R5 need-evaluation (pending unclaimed stages), R2 unclaimed-only candidacy (leased stages excluded), R4 engine invocation (decision computed via select_dispatch_target), R6 decision-evidence surfacing, the non-mutating invariant, and the CLI commands.

python -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_dispatch_runtime.py
Expected: pass.

python -m ruff format --check groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_dispatch_runtime.py
Expected: pass.

git diff --check
Expected: no output, exit 0.
```

Spec mapping:

- `SPEC-TAFE-R5` — tests prove `tick` evaluates need from current state and surfaces actionable dispatch needs without initiating sessions (no spawn/subprocess; `mutated=False`).
- `SPEC-TAFE-R4` — a pending stage with eligible candidates yields a `DispatchDecision` whose selection matches the engine's precedence-tier policy.
- `SPEC-TAFE-R2` — a leased/claimed stage is excluded from need; only unclaimed eligible stages are candidates.
- `SPEC-TAFE-R6` — the report exposes per-stage decision evidence (selected target, rationale, per-candidate eligibility, cost).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — each linked spec maps to executed test evidence.

## Risk / Rollback

Primary risk is scope creep into live dispatch, session initiation, or a new dispatch substrate that belongs to a later owner-approved pilot. Mitigation: the runtime is a read/compute/report function with no spawn/subprocess imports and no `bridge/INDEX.md` or MemBase write; a structural test asserts the absence of that surface, and `mutated=False` is asserted against a temp DB.

A second risk is building on the WI-4498 engine before it is VERIFIED. Mitigation: the engine's public API is fixed by its GO'd proposal contract and the implementation is reported at `bridge/gtkb-tafe-dispatch-policy-engine-003.md`; this proposal recommends WI-4499 implementation land **after** WI-4498 reaches VERIFIED so the consumed contract is verified first. Filing the proposal in parallel keeps the authorized pipeline moving without pre-committing implementation.

A third risk is need-detection coupling to flow/stage schema details. Mitigation: the runtime reads through the existing `TypedArtifactFlowService` read methods (`list_flow_instances`, `list_capability_snapshots`, stage-lease reads) rather than raw SQL, so it tracks the verified schema surface.

Rollback is a single-commit revert of the new module + test plus the additive `flow dispatch` CLI block in `cli.py` (no removal of existing commands). No KB mutation, no schema change, no integration to unwind.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of a new `gtkb-tafe-dispatch-tick-health` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`, and this slice changes no bridge-authority behavior.

## Recommended Commit Type

feat — adds a new pure TAFE R5 need-evaluation runtime module plus an additive `gt flow dispatch tick/health` CLI surface with comprehensive tests; no behavior change to existing commands and no live dispatch.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
