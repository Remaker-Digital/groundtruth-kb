NEW

# Bridge Scheduler Slice 6: Aging and Priority Weighting

bridge_kind: implementation_proposal
Document: gtkb-bridge-scheduler-lanes-leases-slice-6
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3377 (bridge scheduler Slice 6 - aging and priority weighting); sub-slice 6 of the GO'd gtkb-bridge-scheduler-lanes-leases-slice-1-scoping plan
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3377
target_paths: ["scripts/bridge_dispatch_priority.py", "platform_tests/scripts/test_bridge_dispatch_priority.py"]
Recommended commit type: feat:

## Summary

This is Slice 6, the final sub-slice of the bridge scheduler program. The GO'd scoping thread `gtkb-bridge-scheduler-lanes-leases-slice-1-scoping` (Loyal Opposition GO at `-002`) approved a five-sub-slice plan; sub-slice 6 is aging and priority weighting. Its scoping bullet: "Item age (NEW/REVISED filed timestamp) and a priority field feed into the dispatch selector so old items don't starve behind fresh bridge noise." Design decision 5 fixed the shape - "Aging weight = monotonic increasing as a function of (now - filed_at)" - and explicitly deferred the concrete function to this Slice 6 proposal.

Slice 6 delivers a standalone module - `scripts/bridge_dispatch_priority.py` - that computes a dispatch-priority score for a bridge entry from its age and an optional priority field, and orders a set of entries by that score. The score uses an **effective-age model**: a priority head-start measured in hours, plus the entry's real age in hours. Because the aging term is linear and unbounded, an old low-priority item always eventually outranks a fresh high-priority one - the anti-starvation guarantee.

Slice 6 is purely additive: one new module plus its test suite. No existing dispatch code is modified; integration into the dispatch selector is the deferred integration step, consistent with the Slice 2-5 standalone-primitive boundaries.

## Background

The Slice 4 per-role concurrency limit and the Slice 5 lane classifier decide how many workers run and with what parallelism profile. They do not decide which pending bridge entry a free worker picks next. Today the cross-harness trigger processes oldest-first within a fixed `DEFAULT_MAX_ITEMS = 2` window; the owner's S350 directive asked for "aging and priority weighting so old items do not starve behind fresh bridge noise."

Slice 6 supplies the selection score. Without it, a steady stream of fresh high-priority entries could indefinitely postpone an old low-priority entry. With a linear unbounded aging term, every entry's score rises without ceiling as it waits, so any entry is guaranteed to reach the front of the queue in bounded time regardless of how much fresh work arrives.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is the canonical bridge workflow state; the dispatch-priority score orders the selection of work from that queue without changing the queue itself.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the new module and the new test file are within the E:\GT-KB project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the Slice 6 test suite from the linked specifications.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - the bridge dispatch automation contract; Slice 6 adds a mechanism but does not touch the dispatch path, so the auto-trigger contract is preserved unchanged.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 - auto-trigger contract preserved; Slice 6 does not alter dispatch behavior or actionable-signature computation.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the priority module is topology-agnostic; both the cross-harness trigger and the single-harness dispatcher will consume the dispatch-priority score.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the single-harness substrate will consume the same module in the integration step.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the dispatch-priority score is a pure derivation over durable bridge artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the slice family is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - age is derived from the bridge artifact's NEW/REVISED filed timestamp (advisory).

## Prior Deliberations

- gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (GO at -002) - the design authority for this slice; design decision 5 fixed "Aging weight = monotonic increasing as a function of (now - filed_at)" and deferred the concrete function to this Slice 6 proposal.
- DELIB-2182 - the owner-authorization deliberation for the bridge scheduler program; it records the S350 throughput directive including "aging and priority weighting so old items do not starve."
- gtkb-bridge-scheduler-lanes-leases-slice-2 (VERIFIED at -004), slice-3 (GO at -002), slice-4 (GO at -002), slice-5 (NEW at -001) - the sibling slices; Slice 6 is the final scheduler primitive, the selection score the dispatch loop consumes alongside the Slice 4 limit and Slice 5 lane.
- gtkb-cross-harness-trigger-active-session-suppression-001 (VERIFIED) - the current coarse selection (oldest-first within a fixed window) that the dispatch-priority score refines.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and scaffold the full program (Slices 2-6); that decision is recorded as DELIB-2182. The owner's S350 directive supplied the anti-starvation requirement verbatim ("aging and priority weighting so old items do not starve behind fresh bridge noise"). The MemBase project PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES, work items WI-3373 through WI-3377, and the project authorization PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION (status active; owner decision DELIB-2182) were created under that authorization. This Slice 6 proposal implements WI-3377 within that authorized scope. The concrete aging function and the default priority head-start values are proposed here for Loyal Opposition review (the scoping thread deferred the concrete function to this proposal); they are tunable defaults, not a new requirement, and require no further owner decision before GO.

## Requirement Sufficiency

Existing requirements sufficient. The dispatch-priority module operates within the existing bridge dispatch contract (ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001, DCL-SMART-POLLER-AUTO-TRIGGER-001, GOV-FILE-BRIDGE-AUTHORITY-001); it introduces a selection-scoring mechanism, not a new behavior contract. The owner's anti-starvation requirement is the governing input and is already recorded in DELIB-2182 and the scoping thread. No new or revised requirement is required before implementing Slice 6.

## Clause Scope Clarification (Not a Bulk Operation)

Slice 6 creates one new Python module and one new test file. It does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` - which requires a bulk-operation inventory artifact and review packet, a Path/Phase-deferred decision marker, or an explicit owner-approval packet for a bulk action - is not applicable. The single work item cited (WI-3377) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## In-Root Placement Evidence

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, every artifact of this slice is within the `E:\GT-KB` project root:

- `E:\GT-KB\scripts\bridge_dispatch_priority.py` - new module, in-root.
- `E:\GT-KB\platform_tests\scripts\test_bridge_dispatch_priority.py` - new test file, in-root.

Slice 6 is a pure-derivation module; it creates no runtime state directory. No `applications/` paths. No paths outside `E:\GT-KB`.

## Scope

### New module: scripts/bridge_dispatch_priority.py

A standalone, stdlib-only module that computes a dispatch-priority score for a bridge entry and orders a set of entries by it. Public API:

- `DEFAULT_PRIORITY_HEADSTART_HOURS` - a mapping of priority label to head-start hours: `P0` = 96.0, `P1` = 72.0, `P2` = 48.0, `P3` = 24.0, `P4` = 0.0.
- `DEFAULT_PRIORITY` = `"P3"` - the priority assigned to an entry that carries no priority field (a modest baseline head-start, not the lowest).
- `DEFAULT_AGING_RATE_PER_HOUR` = 1.0 - the aging term contributes one effective-hour of score per real-hour waited.
- `priority_headstart(priority) -> float` - maps a priority label to its head-start hours; an unknown or `None` priority maps to `DEFAULT_PRIORITY`'s value. Never raises.
- `dispatch_score(*, filed_at, priority=None, now=None, aging_rate=DEFAULT_AGING_RATE_PER_HOUR) -> float` - the concrete scoring function: `priority_headstart(priority) + aging_rate * age_hours`, where `age_hours = max(0.0, (now - filed_at).total_seconds() / 3600.0)`. `filed_at` and `now` accept a UTC ISO-8601 string or an aware `datetime`; `now` defaults to the current UTC time. A `filed_at` in the future clamps `age_hours` to 0.0 (no negative score, no raise).
- `sort_by_dispatch_priority(entries, *, now=None, aging_rate=...) -> list` - returns the entries ordered by descending `dispatch_score`. Each entry is a mapping carrying at least `filed_at` and optionally `priority`. Ties are broken by older `filed_at` first, making the order total and deterministic.
- `select_next(entries, *, now=None, aging_rate=...) -> entry | None` - the single highest-scoring entry, or `None` for an empty input.

The concrete aging function (deferred to this proposal by scoping design decision 5) is **linear**: `aging_rate * age_hours`. Rationale for linear over a sub-linear (logarithmic, square-root) or super-linear curve:

- It is monotonic increasing in `(now - filed_at)`, satisfying design decision 5.
- It is **unbounded**, which is the property that guarantees anti-starvation: a fresh entry's score is bounded above by `priority_headstart("P0") + epsilon`, so any waiting entry, whatever its priority, reaches the front of the queue once its age exceeds the priority gap - in bounded, predictable time.
- The score is interpretable as an **effective age in hours**: a `P0` entry behaves as if filed 96 hours earlier than a `P4` entry of the same real age, and a `P4` entry overtakes a perpetually-fresh `P0` entry after 96 hours of waiting. Every default is expressed in hours, so the tuning surface is legible.
- Within one priority tier the aging term alone orders entries oldest-first, preserving today's oldest-first behavior as the tier-local default.

The module is a pure function of its inputs - no filesystem access, no runtime state, deterministic. Self-contained: stdlib only (`datetime`). No import of dispatch code or sibling slice modules.

Not in Slice 6: wiring `dispatch_score` / `select_next` into `cross_harness_bridge_trigger.py` or `single_harness_bridge_dispatcher.py` as the live dispatch selector. Per the GO'd scoping sub-slice plan, integration is deferred; Slice 6 delivers and proves the scoring primitive in isolation.

## Files Expected To Change

- `scripts/bridge_dispatch_priority.py` - NEW. The aging-and-priority dispatch-scoring module described above.
- `platform_tests/scripts/test_bridge_dispatch_priority.py` - NEW. The Slice 6 test suite (T1-T11 below).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| Scoping Slice 6 / design decision 5 (aging weight monotonic increasing in now - filed_at) | T2 asserts `dispatch_score` strictly increases as an entry's age increases at fixed priority; T3 asserts the priority head-start ordering P0 > P1 > P2 > P3 > P4 at fixed age. |
| Scoping Slice 6 (old items do not starve behind fresh bridge noise) | T5 asserts the anti-starvation guarantee: a `P4` entry aged past the `P0` head-start outranks a perpetually-fresh `P0` entry. |
| Scoping Slice 6 (age and priority feed the dispatch selector) | T6-T8 assert `sort_by_dispatch_priority` and `select_next` order entries by descending score with a deterministic oldest-first tie-break; T1 asserts priority ordering at equal age. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Slice 6 creates no runtime state; the module is a pure function and the tests touch no filesystem path (T11). |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | Slice 6 adds no dispatch-path code; verification is by inspection that `cross_harness_bridge_trigger.py` and `single_harness_bridge_dispatcher.py` are absent from `target_paths` and unmodified. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed pytest command and observed results. |

Slice 6 test suite (`platform_tests/scripts/test_bridge_dispatch_priority.py`):

- T1 - at equal `filed_at`, `dispatch_score` for a `P0` entry exceeds `P1` exceeds `P2` exceeds `P3` exceeds `P4`.
- T2 - at fixed priority, `dispatch_score` strictly increases as `filed_at` moves further into the past (monotonic aging).
- T3 - `priority_headstart` returns the documented head-start hours per tier, strictly ordered P0 > P1 > P2 > P3 > P4.
- T4 - an unknown or `None` priority resolves to the `DEFAULT_PRIORITY` head-start; `priority_headstart` never raises.
- T5 - anti-starvation: a `P4` entry whose age exceeds `priority_headstart("P0")` outranks a freshly-filed `P0` entry.
- T6 - `sort_by_dispatch_priority` returns entries ordered by descending `dispatch_score`.
- T7 - within one priority tier, `sort_by_dispatch_priority` orders older `filed_at` ahead of newer.
- T8 - entries with an identical score are ordered by older `filed_at` first - a deterministic, total tie-break.
- T9 - a `filed_at` in the future clamps `age_hours` to 0.0: `dispatch_score` equals the bare priority head-start and does not go negative or raise.
- T10 - `select_next` returns the single highest-scoring entry; `select_next([])` returns `None`.
- T11 - `dispatch_score` is a pure function: repeated calls with identical inputs (including an explicit `now`) return identical results, and the module performs no filesystem access.

Verification command for the post-implementation report: `python -m pytest platform_tests/scripts/test_bridge_dispatch_priority.py -q`, plus `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-6` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-6`.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/bridge_dispatch_priority.py` exists and exposes `priority_headstart`, `dispatch_score`, `sort_by_dispatch_priority`, `select_next`, and the documented default constants.
- [ ] The aging term is linear and unbounded; `dispatch_score` is monotonic increasing in `(now - filed_at)` at fixed priority.
- [ ] The anti-starvation guarantee holds: a sufficiently-aged low-priority entry outranks a perpetually-fresh high-priority entry (T5).
- [ ] `sort_by_dispatch_priority` and `select_next` produce a deterministic, total ordering with an oldest-first tie-break.
- [ ] A future-dated `filed_at` clamps to zero aging without a negative score or a raise.
- [ ] `platform_tests/scripts/test_bridge_dispatch_priority.py` covers T1-T11 and passes.
- [ ] No existing dispatch code is modified - Slice 6 is purely additive.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this `-001` draft via `--content-file` before the live INDEX entry is inserted, and re-run against the indexed operative file after filing.

Expected and observed results:

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: exit 0; five clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

- R1 (low): the proposed head-start defaults or aging rate are mis-tuned, so a tier waits longer or shorter than intended before aging overtakes the next tier. Mitigation: every default is a tunable parameter expressed in hours; mis-tuning is corrected by a constant edit, and Loyal Opposition Ask 1 invites refinement of the concrete numbers before GO. The structural anti-starvation guarantee (linear unbounded aging) holds for any positive aging rate and any finite head-start.
- R2 (low): the new module has no consumer until the integration step. Mitigation: this is the GO'd scoping sub-slice boundary; the T1-T11 suite exercises every code path in isolation.
- R3 (very low): clock skew or a future-dated `filed_at` produces a nonsensical score. Mitigation: `age_hours` is clamped to `max(0.0, ...)` and T9 asserts the future-dated case.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue.

## Loyal Opposition Asks

1. Confirm the concrete aging function - linear, `aging_rate * age_hours` with `DEFAULT_AGING_RATE_PER_HOUR = 1.0` - and the `DEFAULT_PRIORITY_HEADSTART_HOURS` values (P0=96 ... P4=0) satisfy design decision 5 and the owner's anti-starvation requirement. The structural guarantee holds for any positive rate and finite head-start; the specific numbers are the tunable surface this Ask exposes.
2. Confirm `DEFAULT_PRIORITY = "P3"` (a modest baseline head-start for unprioritized entries) is the right default, versus `P4` (zero head-start) or a mid value.
3. Confirm that scoping Slice 6 as a standalone scoring module - with the wiring of `select_next` into the live dispatch selector deferred to the integration step - matches the GO'd sub-slice plan, consistent with the Slice 2-5 boundaries.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
