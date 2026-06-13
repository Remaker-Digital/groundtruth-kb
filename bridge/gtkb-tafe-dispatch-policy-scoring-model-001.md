NEW

# gtkb-tafe-dispatch-policy-scoring-model - WI-4498 Dispatch Policy Scoring Model

bridge_kind: prime_proposal
Document: gtkb-tafe-dispatch-policy-scoring-model
Version: 001
Author: Codex Prime Builder
Date: 2026-06-13 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-pb-20260613-wi4498
author_model: GPT-5
author_model_version: 5
author_model_configuration: default

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-DISPATCH-TRACK-WI-4497-4498-4499
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4498

target_paths: ["groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/tests/test_tafe_dispatch_policy.py", "groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4498, the bounded Typed Artifact-Flow Engine dispatch-policy scoring model. The approved work adds deterministic candidate eligibility, scoring, ranking, and target-selection calculation APIs over the already-VERIFIED `agent_capability_snapshots` substrate from WI-4497.

This proposal deliberately does not run dispatch, acquire or release leases, launch harnesses, write bridge files, replace `bridge/INDEX.md`, add generated bridge views, or implement `gt flow dispatch tick` / `gt flow dispatch health`. WI-4499 remains the sibling work item for dispatch tick/health command behavior.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - governs the TAFE architecture and the requirement that dispatch policy remain a MemBase-backed service surface during bridge-authoritative parallel run.
- `SPEC-TAFE-R4` - directly governs policy-driven dispatch by role, capability, cost, and subject; this slice implements the deterministic scoring model and hard eligibility gates.
- `SPEC-TAFE-R5` - constrains this slice to need-driven evaluation only; it must not add polling, blind activation, or automatic dispatch execution.
- `SPEC-TAFE-R6` - requires reproducible/auditable dispatch decisions; this slice must return structured eligibility reasons and score components rather than opaque totals.
- `SPEC-TAFE-R7` - requires canonical data/services behind CLI/service surfaces rather than protocol-bearing markdown; this slice adds a service-level policy API while leaving future CLI dispatch commands to WI-4499.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - keeps the live file bridge authoritative until a later governed cutover; this slice must not change bridge authority.
- `GOV-STANDING-BACKLOG-001` - WI-4498 is an approved backlog item under the active TAFE dispatch-track PAUTH.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this work is a concrete backlog implementation proposal and therefore preserves durable artifact state through the bridge rather than informal chat-only intent.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this proposal keeps the requirement, work item, implementation scope, tests, and later verification evidence artifact-linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this proposal is the lifecycle trigger for moving WI-4498 from backlogged candidate work into bridge-reviewed implementation work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specs before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes the required PAUTH, project, and work-item header lines.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map each linked spec to focused tests and command evidence before LO can mark VERIFIED.

## Prior Deliberations

- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner selected one Typed Artifact-Flow Engine with multiple typed flows, producing the TAFE spec family and work-item decomposition.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D12-20260612` - owner selected the role + capability + cost + subject weighted scoring model for dispatch policy.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612` - owner selected point-in-time agent capability snapshots so dispatch decisions are reproducible.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D14-20260612` - owner selected per-stage-attempt telemetry granularity; this slice contributes auditable decision components but not telemetry table writes.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approved promoting the TAFE specs, including `SPEC-TAFE-R4`, to `specified`.
- `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613` - owner authorized the dispatch track containing WI-4497, WI-4498, and WI-4499.

## Owner Decisions / Input

No new owner decision is required for this bounded implementation. Owner approval already exists through `DELIB-BRIDGE-DISPATCH-OVERHAUL-D12-20260612`, `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612`, and `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613`; this proposal stays inside that authorization and does not request a cutover, pilot expansion, bridge-authority change, or new external action.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R4`, `SPEC-TAFE-R5`, `SPEC-TAFE-R6`, `SPEC-TAFE-R7`, WI-4498, and the active dispatch-track PAUTH provide enough detail for a deterministic scoring model bounded to service/test code.

No new or revised requirement is needed because this slice defines the exact implementation boundary: hard eligibility gates plus weighted score calculation over candidate snapshots, with no live dispatch side effects.

## Proposed Implementation

1. Extend `FlowRuntimeService` in `groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py` with pure dispatch-policy calculation methods:
   - `evaluate_eligibility(candidate, dispatch_request)` returns `eligible: bool`, failing gate ids, and human-readable reasons.
   - `compute_dispatch_score(candidate, dispatch_request, weights=None)` returns component scores and a deterministic total for one eligible candidate.
   - `score_candidates(dispatch_request, candidates=None, weights=None)` evaluates all supplied candidates, or current active capability snapshots when omitted, and returns structured score rows.
   - `rank_candidates(...)` returns scored rows in deterministic dispatch order.
   - `select_dispatch_target(...)` returns the top eligible scored row, or `None` when no candidate clears the gates.
2. Apply hard eligibility gates before any weighted score:
   - role match against `dispatch_request["required_role"]`;
   - capability match against `dispatch_request["required_capabilities"]` and snapshot `capabilities_parsed`/`capabilities`;
   - subject match against request subject and snapshot `subject_scope` using exact, list, and wildcard forms;
   - reviewer independence through request-provided excluded session/context ids and snapshot metadata;
   - health/status gates (`active`/`healthy` style states only);
   - stage-lease availability, owner-gate status, and workspace availability as explicit request/candidate inputs, without mutating leases or owner-gate state.
3. Implement calibrated but transparent scoring components for eligible candidates:
   - capability coverage;
   - subject affinity;
   - cost efficiency from candidate metadata/capabilities;
   - reviewer precedence from `reviewer_precedence`;
   - health confidence / recency where existing snapshot fields permit deterministic comparison.
4. Define deterministic tie-breaking so repeated runs over the same snapshots produce the same selection: total score descending, reviewer precedence descending, captured timestamp descending when present, then `harness_id`, then snapshot `id`.
5. Update `groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py` so the WI-4497 anti-scope test no longer forbids WI-4498 scoring APIs, while it still forbids `dispatch_tick` and `dispatch_health`.
6. Add `groundtruth-kb/tests/test_tafe_dispatch_policy.py` with positive and negative cases for the gates, scoring components, tie-breaking, and no-side-effect boundary.

## Out Of Scope

- No `gt flow dispatch tick` command.
- No `gt flow dispatch health` command.
- No harness launch, session creation, auto-dispatch, polling, or blind activation.
- No stage-lease claim/release/heartbeat behavior.
- No generated bridge-view, compatibility-view write, bridge `INDEX.md` replacement, dual-write mode, pilot eligibility expansion, or governed cutover.
- No MemBase schema mutation.

## Acceptance Criteria

- Candidate scoring is deterministic and side-effect free.
- Ineligible candidates appear with explicit failing gates and no dispatch selection.
- Eligible candidates include score components that explain the total.
- `select_dispatch_target` returns the highest-ranked eligible candidate and `None` when no candidate qualifies.
- Existing WI-4497 capability-snapshot CRUD tests still pass.
- The service still exposes no WI-4499 dispatch tick/health behavior.

## Spec-Derived Verification Plan

`SPEC-TAFE-R4`:

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m pytest groundtruth-kb\tests\test_tafe_dispatch_policy.py -q --tb=short
```

Expected: pass; verifies role, capability, cost, subject, health/status, reviewer-independence, owner-gate, stage-lease, and workspace hard gates plus weighted scoring, ranking, and selection.

`SPEC-TAFE-R5`:

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m pytest groundtruth-kb\tests\test_tafe_dispatch_policy.py groundtruth-kb\tests\test_tafe_agent_capability_snapshots.py -q --tb=short
```

Expected: pass; verifies scoring remains an invoked calculation surface and does not expose `dispatch_tick` or `dispatch_health`.

`SPEC-TAFE-R6`:

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m pytest groundtruth-kb\tests\test_tafe_dispatch_policy.py -q --tb=short
```

Expected: pass; verifies score rows include component breakdowns and eligibility reasons suitable for later audit/telemetry records.

`SPEC-TAFE-R7` and bridge-governance specs:

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m ruff check groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_dispatch_policy.py groundtruth-kb\tests\test_tafe_agent_capability_snapshots.py
python -m ruff format --check groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_dispatch_policy.py groundtruth-kb\tests\test_tafe_agent_capability_snapshots.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_dispatch_policy.py groundtruth-kb/tests/test_tafe_agent_capability_snapshots.py
```

Expected: pass; verifies the service/test implementation is syntactically clean and no whitespace artifact is introduced. The implementation report must disclose if the repo-local venv remains unavailable and ambient `python` is used with `PYTHONPATH`.

## Risk / Rollback

Primary risk is accidentally turning the scoring model into a dispatcher. Mitigation: keep every new method side-effect free, require explicit inputs for owner/lease/workspace gates, and add tests that forbid WI-4499 `dispatch_tick`/`dispatch_health` behavior.

Secondary risk is overfitting the first weight profile. Mitigation: implement a documented default weight mapping with an optional override parameter and structured score components so later calibration is additive.

Rollback is straightforward: revert the source/test hunks for this bridge thread. No schema, bridge-authority, or external-state mutation is in scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-tafe-dispatch-policy-scoring-model` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat:` - this slice adds a new TAFE dispatch-policy scoring service surface and focused tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
