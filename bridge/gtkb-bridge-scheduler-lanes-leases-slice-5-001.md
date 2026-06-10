NEW

# Bridge Scheduler Slice 5: Work-Lane Classification

bridge_kind: prime_proposal
Document: gtkb-bridge-scheduler-lanes-leases-slice-5
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3376 (bridge scheduler Slice 5 - work-lane classification); sub-slice 5 of the GO'd gtkb-bridge-scheduler-lanes-leases-slice-1-scoping plan
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3376
target_paths: ["scripts/bridge_lane_classifier.py", "platform_tests/scripts/test_bridge_lane_classifier.py"]
Recommended commit type: feat:

## Summary

This is Slice 5 of the bridge scheduler program. The GO'd scoping thread `gtkb-bridge-scheduler-lanes-leases-slice-1-scoping` (Loyal Opposition GO at `-002`) approved a five-sub-slice plan; sub-slice 5 is work-lane classification. Its scoping bullet: "Classify each bridge entry into one of: review / implementation / verification / governance. Lane determines concurrency profile (verification = aggressive parallel; governance = serialized)." Design decision 4 fixed the mechanism: "Lane assignment = derived from `bridge_kind` header + content classification, not configured per-thread."

Slice 5 delivers a standalone module - `scripts/bridge_lane_classifier.py` - that classifies a bridge entry into one of four work lanes and maps each lane to a concurrency profile. The scheduler will consult it, once integrated, to apply a per-lane parallelism policy on top of the Slice 4 per-role limit.

Slice 5 is purely additive: one new module plus its test suite. No existing dispatch code is modified; integration into the dispatch loop is the deferred integration step, consistent with the Slice 2, 3, and 4 standalone-primitive boundaries.

## Background

The owner's S350 throughput directive (recorded in the scoping thread) split bridge work into four lanes with distinct concurrency profiles:

> "Review lane: LO proposal/verification analysis can run in parallel, but final verdict writes must serialize. Implementation lane: Prime can run multiple workers only when target paths and MemBase mutations are disjoint. Verification lane: tests, ruff, bridge preflights, credential scans, and drift checks can run aggressively in parallel. Governance lane: formal artifact mutations, owner-decision-sensitive work, and MemBase writes stay serialized unless the operation is explicitly batch-safe."

The Slice 4 per-role concurrency limit is a coarse cap; lanes refine it. A role's workers should parallelize aggressively when the work is verification (read-mostly checks) and serialize when the work is governance (formal artifact mutation). Slice 5 supplies the classification so the scheduler can pick the right profile per dispatched unit of work.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is the canonical bridge workflow state; lane classification organizes the dispatch of work against that queue without changing the queue itself.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the new module and the new test file are within the E:\GT-KB project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the Slice 5 test suite from the linked specifications.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - the bridge dispatch automation contract; Slice 5 adds a mechanism but does not touch the dispatch path, so the auto-trigger contract is preserved unchanged.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 - auto-trigger contract preserved; Slice 5 does not alter dispatch behavior or actionable-signature computation.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the classifier is topology-agnostic; both the cross-harness trigger and the single-harness dispatcher will consume lane classification.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the single-harness substrate will consume the same classifier in the integration step.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - lane classification is a pure derivation over durable bridge artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the slice family is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - lane is derived from the bridge artifact's kind and lifecycle status (advisory).

## Prior Deliberations

- gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (GO at -002) - the design authority for this slice; design decision 4 fixed "Lane assignment = derived from bridge_kind header + content classification", and the owner's four-lane definition is quoted in the scoping background.
- DELIB-2182 - the owner-authorization deliberation for the bridge scheduler program; it records the S350 throughput directive including the four-lane split.
- gtkb-bridge-scheduler-lanes-leases-slice-2 (VERIFIED at -004), slice-3 (GO at -002), slice-4 (NEW at -001) - the sibling slices; Slice 5's classifier is the policy input the per-role concurrency of Slice 4 is refined by.
- gtkb-cross-harness-trigger-active-session-suppression-001 (VERIFIED) - the current coarse one-at-a-time suppression contract that lane-aware concurrency refines.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and scaffold the full program (Slices 2-6); that decision is recorded as DELIB-2182. The owner's S350 directive supplied the four-lane taxonomy and each lane's concurrency intent verbatim (quoted under Background). The MemBase project PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES, work items WI-3373 through WI-3377, and the project authorization PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION (status active; owner decision DELIB-2182) were created under that authorization. This Slice 5 proposal implements WI-3376 within that authorized scope. It asserts no new requirement and requires no further owner decision before GO.

## Requirement Sufficiency

Existing requirements sufficient. The lane classifier operates within the existing bridge dispatch contract (ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001, DCL-SMART-POLLER-AUTO-TRIGGER-001, GOV-FILE-BRIDGE-AUTHORITY-001); it introduces a classification mechanism, not a new behavior contract. The owner's four-lane taxonomy is the governing input and is already recorded in DELIB-2182 and the scoping thread. No new or revised requirement is required before implementing Slice 5.

## Clause Scope Clarification (Not a Bulk Operation)

Slice 5 creates one new Python module and one new test file. It does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` - which requires a bulk-operation inventory artifact and review packet, a Path/Phase-deferred decision marker, or an explicit owner-approval packet for a bulk action - is not applicable. The single work item cited (WI-3376) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## In-Root Placement Evidence

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, every artifact of this slice is within the `E:\GT-KB` project root:

- `E:\GT-KB\scripts\bridge_lane_classifier.py` - new module, in-root.
- `E:\GT-KB\platform_tests\scripts\test_bridge_lane_classifier.py` - new test file, in-root.

Slice 5 is a pure-derivation module; it creates no runtime state directory. No `applications/` paths. No paths outside `E:\GT-KB`.

## Scope

### New module: scripts/bridge_lane_classifier.py

A standalone, stdlib-only module that classifies a bridge entry into a work lane and maps lanes to concurrency profiles. Public API:

- Lane constants `LANE_REVIEW`, `LANE_IMPLEMENTATION`, `LANE_VERIFICATION`, `LANE_GOVERNANCE`, and the frozenset `CANONICAL_LANES`.
- `classify_lane(*, bridge_kind, status=None) -> str` - returns the work lane for a bridge entry from its `bridge_kind` header and, where it disambiguates, its latest INDEX `status`. The mapping (proposed; see Loyal Opposition Ask 1):
  - `implementation_proposal` / `prime_implementation_proposal` -> `LANE_REVIEW` (the pending work is Loyal Opposition design analysis of a proposal).
  - `implementation_report` -> `LANE_VERIFICATION` (the pending work is Loyal Opposition verification - running the spec-derived tests, preflights, and scans of the Mandatory Specification-Derived Verification Gate).
  - `proposal_review_verdict` with `status` `GO` or `NO-GO` -> `LANE_IMPLEMENTATION` (the pending work is Prime Builder implementation or revision).
  - `proposal_review_verdict` with `status` `VERIFIED` -> `LANE_REVIEW` and flagged terminal (no actionable work; classified for completeness).
  - `loyal_opposition_advisory` -> `LANE_GOVERNANCE` (advisory disposition is owner-decision-sensitive).
  - any `bridge_kind` whose value contains a formal-artifact governance signal (GOV / ADR / DCL / formal-artifact mutation) -> `LANE_GOVERNANCE`.
  - unknown or missing `bridge_kind` -> `LANE_REVIEW` as the fail-soft default (the most conservative lane that still serializes verdict writes), never raising.
- `lane_concurrency_profile(lane) -> dict` - returns the concurrency profile for a lane: a dict with `lane`, `parallelism` (`aggressive` / `moderate` / `limited` / `serialized`), `max_concurrency` (an integer or `None` for "bounded only by the Slice 4 per-role limit"), and `verdict_writes_serialized` (bool). The profiles encode the owner's S350 intent:
  - `LANE_VERIFICATION` -> `aggressive`, `max_concurrency=None`, `verdict_writes_serialized=True`.
  - `LANE_REVIEW` -> `moderate`, `max_concurrency=None`, `verdict_writes_serialized=True`.
  - `LANE_IMPLEMENTATION` -> `limited`, `max_concurrency=None`, `verdict_writes_serialized=True` (Prime parallelism is permitted only on disjoint target paths; the dispatch-path integration enforces disjointness).
  - `LANE_GOVERNANCE` -> `serialized`, `max_concurrency=1`, `verdict_writes_serialized=True`.

The classifier is a pure function of its inputs - no filesystem access, no runtime state, deterministic. Self-contained: stdlib only. No import of dispatch code or sibling slice modules.

Not in Slice 5: wiring the classifier into `cross_harness_bridge_trigger.py` or `single_harness_bridge_dispatcher.py`, and enforcing the per-lane profile in the dispatch loop. Per the GO'd scoping sub-slice plan, integration is deferred; Slice 5 delivers and proves the classification primitive in isolation.

## Files Expected To Change

- `scripts/bridge_lane_classifier.py` - NEW. The work-lane classifier module described above.
- `platform_tests/scripts/test_bridge_lane_classifier.py` - NEW. The Slice 5 test suite (T1-T11 below).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| Scoping Slice 5 (classify each bridge entry into review / implementation / verification / governance) | T1-T7 assert `classify_lane` returns the proposed lane for each `bridge_kind` plus the verdict-status disambiguation and the fail-soft default. |
| Scoping Slice 5 (lane determines concurrency profile; verification aggressive, governance serialized) | T8-T10 assert `lane_concurrency_profile` returns the documented profile per lane, including `verification` aggressive and `governance` serialized with `max_concurrency=1`. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Slice 5 creates no runtime state; the classifier is a pure function and the tests touch no filesystem path. |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | Slice 5 adds no dispatch-path code; verification is by inspection that `cross_harness_bridge_trigger.py` and `single_harness_bridge_dispatcher.py` are absent from `target_paths` and unmodified. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed pytest command and observed results. |

Slice 5 test suite (`platform_tests/scripts/test_bridge_lane_classifier.py`):

- T1 - `classify_lane(bridge_kind="implementation_proposal")` returns `LANE_REVIEW`.
- T2 - `classify_lane(bridge_kind="prime_implementation_proposal")` returns `LANE_REVIEW`.
- T3 - `classify_lane(bridge_kind="implementation_report")` returns `LANE_VERIFICATION`.
- T4 - `classify_lane(bridge_kind="proposal_review_verdict", status="GO")` returns `LANE_IMPLEMENTATION`; the same with `status="NO-GO"` returns `LANE_IMPLEMENTATION`.
- T5 - `classify_lane(bridge_kind="loyal_opposition_advisory")` returns `LANE_GOVERNANCE`.
- T6 - a `bridge_kind` carrying a formal-artifact governance signal returns `LANE_GOVERNANCE`.
- T7 - an unknown or empty `bridge_kind` returns the fail-soft default `LANE_REVIEW` and does not raise.
- T8 - `lane_concurrency_profile(LANE_VERIFICATION)` reports `parallelism="aggressive"`.
- T9 - `lane_concurrency_profile(LANE_GOVERNANCE)` reports `parallelism="serialized"` and `max_concurrency=1`.
- T10 - every lane in `CANONICAL_LANES` has a `lane_concurrency_profile` entry whose `verdict_writes_serialized` is `True` (the owner's "final verdict writes must serialize" invariant holds for every lane).
- T11 - `classify_lane` is deterministic: repeated calls with identical inputs return identical results, and it performs no filesystem access.

Verification command for the post-implementation report: `python -m pytest platform_tests/scripts/test_bridge_lane_classifier.py -q`, plus `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-5` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-5`.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/bridge_lane_classifier.py` exists and exposes the four lane constants, `CANONICAL_LANES`, `classify_lane`, and `lane_concurrency_profile`.
- [ ] `classify_lane` maps every `bridge_kind` per the proposed table and never raises on unknown input.
- [ ] `lane_concurrency_profile` returns the documented profile for every lane in `CANONICAL_LANES`; `verification` is aggressive and `governance` is serialized with `max_concurrency=1`.
- [ ] Every lane's profile has `verdict_writes_serialized=True`.
- [ ] `platform_tests/scripts/test_bridge_lane_classifier.py` covers T1-T11 and passes.
- [ ] No existing dispatch code is modified - Slice 5 is purely additive.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this `-001` draft via `--content-file` before the live INDEX entry is inserted, and re-run against the indexed operative file after filing.

Expected and observed results:

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: exit 0; five clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

- R1 (low): the proposed lane mapping mis-classifies an edge-case `bridge_kind`. Mitigation: the classifier is a pure function with no side effects; a mis-mapping is corrected by a one-line table edit, and Loyal Opposition Ask 1 invites refinement of the genuinely-ambiguous `implementation_report` mapping before GO.
- R2 (low): the new module has no consumer until the integration step. Mitigation: this is the GO'd scoping sub-slice boundary; the T1-T11 suite exercises every classification branch and every lane profile in isolation.
- R3 (very low): a future `bridge_kind` value is unclassified. Mitigation: the fail-soft default returns `LANE_REVIEW` (verdict-serialized, conservative) and never raises.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue.

## Loyal Opposition Asks

1. Confirm the proposed `bridge_kind` -> lane mapping, in particular the `implementation_report -> LANE_VERIFICATION` call (the LO work on a report is running the spec-derived tests, preflights, and scans of the Mandatory Specification-Derived Verification Gate, which is the verification lane's activity) versus an alternative `implementation_report -> LANE_REVIEW`. If `LANE_REVIEW` is preferred, NO-GO with that direction.
2. Confirm that scoping Slice 5 as a standalone classifier module - with the dispatch-loop enforcement of per-lane profiles deferred to the integration step - matches the GO'd sub-slice plan, consistent with the Slice 2/3/4 boundaries.
3. Confirm that `verdict_writes_serialized=True` for every lane correctly encodes the owner's "final verdict writes must serialize" requirement, given that the actual serialization is provided by the Slice 3 serialized INDEX writer.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
