NEW

# TAFE Dispatch Policy Engine (Weighted Scoring) Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-dispatch-policy-engine
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
Work Item: WI-4498

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_dispatch_policy.py", "groundtruth-kb/tests/test_tafe_dispatch_policy.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4498, the TAFE R4 policy-driven dispatch engine, as a new pure, deterministic decision module `groundtruth-kb/src/groundtruth_kb/tafe_dispatch_policy.py`. Given a dispatch need plus a set of candidate harnesses (each a WI-4497 `agent_capability_snapshots` profile augmented with caller-supplied runtime context), the engine applies the SPEC-TAFE-R4 hard eligibility gates first, then selects among eligible candidates using calibrated precedence tiers, with cost used only for reporting, waste detection, and tie-breaking among practically-equivalent routes.

WI-4497 (the capability-snapshot substrate this engine consumes) is VERIFIED at `bridge/gtkb-tafe-agent-capability-snapshots-schema-004.md`.

### Bounding (explicit out-of-scope)

This slice is a **pure decision function only**. It MUST NOT:

- Perform any actual dispatch, harness spawning, subprocess launch, or DB/file/network I/O. It computes a decision from in-memory inputs and returns it.
- Query MemBase, the harness registry, `stage_leases`, owner-gate state, or workspace state itself. Stage-lease availability, owner-gate status, workspace availability, the candidate's active session id, and optional cost are **caller-supplied inputs** to the engine.
- Modify or integrate with `scripts/cross_harness_bridge_trigger.py`, the single-harness dispatcher, or any live dispatch substrate. Live-substrate integration is later/WI-4499 (`gt flow dispatch tick/health`) work and is not implemented here.
- Implement need-driven activation (SPEC-TAFE-R5 / WI-4499), telemetry persistence (SPEC-TAFE-R6 storage), generated bridge views, dual-write, pilot eligibility changes, or bridge-authority cutover.

This bounding mirrors the WI-4497 discipline (schema/service without claim semantics) and keeps the engine fully unit-testable in isolation. WI-4499 remains the open sibling that gathers live context and invokes this engine.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - Phase 1 parallel-run substrate; `bridge/INDEX.md` remains canonical until a later governed cutover. The engine is a pure library, not a live dispatch substrate.
- `SPEC-TAFE-R4` - the governing requirement: V1 policy applies hard eligibility gates first (role, capability, subject, review-independence, health, stage-lease availability, owner-gate status, workspace availability), then selects using calibrated precedence tiers; cost is only for reporting, waste detection, and tie-breaking. This proposal implements exactly that decision procedure.
- `SPEC-TAFE-R2` - the review-independence and single-claim eligibility gates honor the session-scoped never-self-review invariant and the stage-lease availability gate; the engine never selects a candidate whose stage lease is unavailable or whose active session authored the artifact under review.
- `SPEC-TAFE-R6` - the engine returns a structured per-candidate eligibility breakdown and selection rationale (including dispatch decision inputs and cost) suitable for later telemetry recording; it does not itself persist telemetry.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only bridge evidence chain; `bridge/INDEX.md` remains canonical workflow state; this slice changes no bridge authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - PAUTH, project, work item, target paths, and governing specs are linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps each R4 gate and the selection/tie-break behavior to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-4498 is the backlog authority for this slice; WI-4499 remains an open sibling.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation proceeds under the active bounded dispatch-track PAUTH (which already includes WI-4498) plus the forthcoming Loyal Opposition GO.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the policy engine is durable governed artifact state with preserved evidence trail.

## Prior Deliberations

- `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613` - active dispatch-track PAUTH owner-decision basis; authorizes WI-4497/WI-4498/WI-4499.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` - owner decision that the never-self-review invariant is **session-scoped** (applies to session context, not model identity); the review-independence gate implements exactly this scoping.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner choice of the TAFE overhaul direction that produced SPEC-TAFE-R4.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approval promoting SPEC-TAFE-R4 to `specified`.
- `bridge/gtkb-tafe-agent-capability-snapshots-schema-004.md` - VERIFIED WI-4497 capability-snapshot substrate; the direct input dependency this engine consumes.
- No prior deliberations found for the dispatch-policy weighted-scoring engine: `search_deliberations("dispatch policy weighted scoring eligibility precedence review independence")` returned no matches on 2026-06-13. This is the first implementation of the R4 policy, not a revisit of a rejected approach.

## Owner Decisions / Input

No new owner decision is required. Existing authority is the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-DISPATCH-TRACK-WI-4497-4498-4499` (backed by `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613`), which explicitly includes WI-4498 and forbids cutover, generated-view authority, dual-write, pilot-eligibility expansion, and phase-2 reformation.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TAFE-R4` precisely specifies the V1 dispatch policy (hard eligibility gates first, then calibrated precedence tiers, cost only for reporting/waste/tie-break), with `SPEC-TAFE-R2` defining the review-independence and single-claim semantics and `SPEC-TAFE-R6` defining the decision-evidence fields. No new or revised requirement is needed because this slice implements the specified decision procedure as a pure library and excludes live dispatch, context gathering, and telemetry persistence.

## Implementation Plan

New module `groundtruth-kb/src/groundtruth_kb/tafe_dispatch_policy.py`:

1. **Inputs (frozen dataclasses):**
   - `DispatchNeed`: `required_role`, `subject_scope`, `artifact_author_session_id`, optional `required_capabilities` (sequence of capability keys), `owner_gate_blocked: bool`, `requires_workspace: bool`, optional `stage_id`/`flow_instance_id` for labeling.
   - `DispatchCandidate`: the caller composes this from a WI-4497 capability snapshot plus runtime context — `harness_id`, `role`, `subject_scope`, `health_status`, `reviewer_precedence`, `capabilities` (mapping), `active_session_id`, `stage_lease_available: bool`, `workspace_available: bool`, optional `cost`, optional `model_identifier`.
2. **Hard eligibility gates** (each a pure predicate returning `(passed, reason)`), evaluated in SPEC-TAFE-R4 order:
   1. `role` — `candidate.role == need.required_role`.
   2. `capability` — every key in `need.required_capabilities` is present/truthy in `candidate.capabilities`.
   3. `subject` — `candidate.subject_scope` covers `need.subject_scope` (exact match or candidate scope `both`/`all`).
   4. `review_independence` — `candidate.active_session_id != need.artifact_author_session_id` (session-scoped per D1); a missing candidate session id fails closed.
   5. `health` — `candidate.health_status == "active"`.
   6. `stage_lease_availability` — `candidate.stage_lease_available is True`.
   7. `owner_gate` — `need.owner_gate_blocked is False`.
   8. `workspace_availability` — `True` unless `need.requires_workspace` and not `candidate.workspace_available`.
3. **`evaluate_eligibility(need, candidate) -> EligibilityResult`** — runs all gates, returns per-gate `(passed, reason)` plus `eligible` (all gates passed). Fail-closed on missing required fields.
4. **`select_dispatch_target(need, candidates) -> DispatchDecision`** — filters to eligible candidates, ranks by a calibrated sort key `(reviewer_precedence ascending, cost ascending if present else 0, harness_id ascending)` so precedence tiers dominate and cost only breaks ties among equal-precedence routes (per R4). Returns `selected` (the top eligible `harness_id` or `None` when no candidate is eligible), the full ranked eligible list, the per-candidate eligibility breakdown, and a human-readable `rationale`. Cost never overrides precedence.
5. Module exposes `__all__` with the dataclasses and the two public functions. No module-level side effects, no imports of `db`/registry/subprocess.

New tests `groundtruth-kb/tests/test_tafe_dispatch_policy.py` covering: each gate's pass and fail path; `eligible` requires all gates; review-independence excludes the authoring session; precedence-tier ordering; cost tie-break only among equal precedence (and never overriding precedence); `selected is None` when no candidate is eligible; deterministic stable ordering by `harness_id`; a `requires_workspace=False` need ignoring workspace availability; and a full mixed-candidate scenario producing the expected selection + rationale.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
python -m pytest groundtruth-kb/tests/test_tafe_dispatch_policy.py -q --tb=short
Expected: pass; exercises all eight R4 eligibility gates (pass+fail), precedence-tier selection, cost tie-break (equal-precedence only, never overriding precedence), review-independence exclusion, no-eligible-candidate (selected None), and deterministic ordering.

python -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_dispatch_policy.py groundtruth-kb/tests/test_tafe_dispatch_policy.py
Expected: pass.

python -m ruff format --check groundtruth-kb/src/groundtruth_kb/tafe_dispatch_policy.py groundtruth-kb/tests/test_tafe_dispatch_policy.py
Expected: pass.

git diff --check -- groundtruth-kb/src/groundtruth_kb/tafe_dispatch_policy.py groundtruth-kb/tests/test_tafe_dispatch_policy.py
Expected: no output, exit 0.
```

Spec mapping:

- `SPEC-TAFE-R4` - tests prove each hard eligibility gate is applied first and that selection uses calibrated precedence tiers with cost only for tie-break/reporting.
- `SPEC-TAFE-R2` - the `review_independence` and `stage_lease_availability` gate tests prove session-scoped never-self-review and single-claim respect.
- `SPEC-TAFE-R6` - tests assert the decision returns a per-candidate eligibility breakdown + rationale + cost suitable for later telemetry.
- `GOV-STANDING-BACKLOG-001` - the report reads back WI-4499 as open; the engine implements no dispatch tick/health command surface.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - each linked spec maps to executed test evidence.

## Risk / Rollback

Primary risk is scope creep into live dispatch, context gathering, or trigger integration that belongs to WI-4499. Mitigation: the engine is a pure function with no I/O imports, and tests assert it exposes no spawn/dispatch/DB surface; the report reads back WI-4499 as open.

A second risk is precedence-direction or tie-break ambiguity. Mitigation: the sort key is explicit (lower `reviewer_precedence` = higher priority, matching the registry convention where the existing trigger selects the lowest-precedence reviewer first), cost is strictly secondary, and `harness_id` provides a deterministic final tie-break; tests pin all three layers.

Rollback is a single-commit revert of the two new files before VERIFIED. No KB mutation, no schema change, no integration to unwind.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-tafe-dispatch-policy-engine` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`, and this slice changes no bridge-authority behavior.

## Recommended Commit Type

feat - adds a new pure TAFE R4 dispatch policy engine module with comprehensive tests; no behavior change to existing surfaces.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
