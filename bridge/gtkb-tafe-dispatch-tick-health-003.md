REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: prime-interactive-claim-gate-filing
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (harness B); explanatory output style
author_metadata_source: Claude Code Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# TAFE `gt flow dispatch tick` / `dispatch health` Proposal Revision

bridge_kind: prime_proposal
Document: gtkb-tafe-dispatch-tick-health
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC
Responds-To: bridge/gtkb-tafe-dispatch-tick-health-002.md
Revises: bridge/gtkb-tafe-dispatch-tick-health-001.md

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-DISPATCH-TRACK-WI-4497-4498-4499
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4499

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_dispatch_runtime.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

---

## Revision Claim

This revision responds to the document-only `NO-GO` at `bridge/gtkb-tafe-dispatch-tick-health-002.md`. The design remains unchanged and Loyal Opposition already confirmed that it is well-designed, aligned with `SPEC-TAFE-R5`, and passes applicability/clause preflights.

The only correction is removal of the wording pattern that was interpreted as a helper-template placeholder. The deliberation-search evidence is now expressed as a concrete search-result note, not as any draft instruction.

## Summary

Implement WI-4499, the `gt flow dispatch tick` and `gt flow dispatch health` command surface, as a need-driven evaluation and observability layer over the VERIFIED WI-4498 dispatch policy engine. `tick` evaluates actual dispatch need from current flow/stage state and capability snapshots, composes `DispatchNeed` plus `DispatchCandidate` inputs, and invokes `select_dispatch_target` to compute and report what would be dispatched for each eligible unclaimed stage. `health` aggregates dispatch readiness, including pending stages, eligible candidates by role, no-eligible-candidate counts, and owner-gated or blocked indicators.

This is evaluation, computation, and reporting only. It does not spawn harnesses, initiate sessions, mutate `stage_leases`, write `bridge/INDEX.md`, persist telemetry, create a poller, replace the file bridge, or perform a governed cutover.

## Specification Links

- `SPEC-TAFE-R5` - governs need-driven activation: evaluate need from current state and explicit operator action without blind bulk session initiation.
- `SPEC-TAFE-R4` - `tick` invokes the WI-4498 policy engine for hard eligibility gates and calibrated precedence ranking.
- `SPEC-TAFE-R2` - only unclaimed stages are dispatch candidates; lease state is read, not mutated.
- `SPEC-TAFE-R6` - command output surfaces decision evidence for later telemetry persistence without writing telemetry in this slice.
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - phase-1 parallel-run substrate; `bridge/INDEX.md` remains canonical until a later governed cutover.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this slice writes nothing to the live file bridge or index at runtime.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - PAUTH, project, work item, target paths, and governing specs are linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps R5 need evaluation, R4 engine invocation, R2 unclaimed-only candidacy, and the non-mutating boundary to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-4499 is the backlog authority for this slice; sibling work remains out of scope.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation proceeds only after this revised proposal receives GO and an implementation-start packet.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this proposal preserves the runtime layer as governed artifact state with bridge evidence.

## Prior Deliberations

- `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613` - active dispatch-track PAUTH owner-decision basis authorizing WI-4497/WI-4498/WI-4499.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` - never-self-review invariant is session-scoped.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner choice of the TAFE overhaul direction that produced SPEC-TAFE-R4/R5.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approval promoting the TAFE R-specs to specified.
- `bridge/gtkb-typed-artifact-flow-engine-advisory-004.md` - GO constrained to advisory/planning; conditions carried forward: no cutover, `bridge/INDEX.md` remains canonical, and a live pilot needs a separate owner decision.
- `bridge/gtkb-tafe-dispatch-policy-engine-006.md` - VERIFIED WI-4498 dispatch policy engine consumed by this layer.

Deliberation search evidence: targeted searches for `"dispatch tick health need-driven activation flow runtime"` and `"TAFE dispatch evaluation observability phase 1 no live dispatch"` found no rejected prior approach for this need-evaluation command surface on 2026-06-13. This proposal is therefore a first implementation of the R5 evaluation surface, not a revival of a rejected design.

## Owner Decisions / Input

No new owner decision is required to file or implement this proposal. Existing authority is the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-DISPATCH-TRACK-WI-4497-4498-4499`, backed by `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613`, which explicitly includes WI-4499 and bounds it to platform code/tests with no cutover.

This slice deliberately stops at evaluation and reporting. Wiring `tick` to initiate dispatch, run a live implementation-flow pilot, or create a parallel dispatch substrate remains out of scope and requires a separate owner decision.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-TAFE-R5` specifies need-driven activation and prohibits blind bulk initiation. `SPEC-TAFE-R4`, `SPEC-TAFE-R2`, and `SPEC-TAFE-R6` bound the policy, single-claim, and evidence surfaces. No new or revised requirement is needed because this slice implements a non-mutating read/compute/report layer and excludes live activation, telemetry persistence, and cutover.

## Implementation Plan

1. Add `groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py` with frozen report dataclasses and pure injected-service functions:
   - `evaluate_dispatch_tick(service, *, subject_scope=None, now=None) -> DispatchTickReport`
   - `evaluate_dispatch_health(service, *, subject_scope=None) -> DispatchHealthReport`
2. `evaluate_dispatch_tick` reads current flow/stage state, excludes terminal or claimed stages, reads active capability snapshots, composes policy-engine inputs, calls `select_dispatch_target`, and returns structured decisions with `mutated=False`.
3. `evaluate_dispatch_health` returns readiness counts for pending unclaimed stages, active candidates by role, no-eligible-candidate stages, stale/owner-gated/blocked indicators when surfaced by current state, and `mutated=False`.
4. Add a `dispatch` subgroup under the existing `gt flow` CLI with read-only `tick` and `health` commands. Each command emits JSON-compatible output and never initiates dispatch.
5. Add `groundtruth-kb/tests/test_tafe_dispatch_runtime.py` covering pending-stage decisions, leased-stage exclusion, no-eligible-candidate breakdowns, subject filtering, health aggregation, `mutated=False`, absence of live-dispatch surfaces, and Click CLI output.

## Out Of Scope

- No harness spawning, subprocess launch, session initiation, route execution, or live dispatch.
- No new scheduled task, hook, poller, bridge authority, generated bridge view, dual-write mode, pilot expansion, or cutover.
- No MemBase writes, `stage_leases` writes, owner-gate writes, workspace writes, telemetry persistence, claim/release/heartbeat, or lease recovery.

## Spec-Derived Verification Plan

```text
python -m pytest groundtruth-kb/tests/test_tafe_dispatch_runtime.py -q --tb=short
```

Expected: pass; exercises R5 need evaluation, R2 unclaimed-only candidacy, R4 engine invocation, R6 decision-evidence output, non-mutating invariants, and CLI commands.

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_dispatch_runtime.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_dispatch_runtime.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_dispatch_runtime.py
```

Expected: all pass.

## Findings Addressed

### Finding 1: Unresolved Draft Template Placeholder

Response: Corrected. The revised `Prior Deliberations` section contains only concrete deliberation and bridge evidence plus a specific deliberation-search note. It contains no helper-template heading and no draft placeholder text.

## Bridge Filing (INDEX-Canonical)

This revised proposal is filed under `bridge/` with `REVISED: bridge/gtkb-tafe-dispatch-tick-health-003.md` inserted at the top of the existing `Document: gtkb-tafe-dispatch-tick-health` entry in `bridge/INDEX.md`. No prior version is deleted or rewritten.

## Risk / Rollback

Primary risk is scope creep into live dispatch or session initiation. Mitigation: the runtime is read/compute/report only, tests assert `mutated=False`, and structural tests check for no spawn/subprocess/bridge-index write surface. Rollback is a normal source/test revert plus append-only bridge evidence; no schema or persistent runtime state is introduced.
