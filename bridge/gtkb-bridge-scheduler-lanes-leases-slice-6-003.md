NEW

# Post-Implementation Report - Bridge Scheduler Slice 6: Aging and Priority Weighting (WI-3377)

bridge_kind: implementation_report
Document: gtkb-bridge-scheduler-lanes-leases-slice-6
Version: 003 (NEW; post-implementation report for the GO at bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-002.md)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3377 (bridge scheduler Slice 6 - aging and priority weighting)
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3377
target_paths: ["scripts/bridge_dispatch_priority.py", "platform_tests/scripts/test_bridge_dispatch_priority.py"]
Recommended commit type: feat:

## Summary

The GO'd proposal at bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md (Loyal Opposition GO at -002) is implemented. Two new files were added: scripts/bridge_dispatch_priority.py (the aging-and-priority dispatch-scoring module) and platform_tests/scripts/test_bridge_dispatch_priority.py (its test suite). No existing file was modified - the slice is purely additive. The full suite passes 14/14: the proposal's T1-T11, plus the GO -002 follow-on-constraint-8 coverage for exact score-and-timestamp ties (T12), timezone handling (T13), and case-insensitive priority normalization (T14). The module is a pure function with no filesystem state; it is not wired into the dispatch path, so live dispatch behavior is unchanged. This is the final scheduler-program primitive slice.

## Recommended Commit Type

feat: - the change adds a new capability surface (the aging-and-priority dispatch-scoring module and its test suite). It is net-new code, matching the GO'd proposal's recommended type.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is the canonical bridge workflow state; the dispatch-priority score orders the selection of work from that queue without changing the queue itself.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the new module and the new test file are within the E:\GT-KB project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries forward every relevant governing specification from the proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the executed test suite from the linked specifications.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - the bridge dispatch automation contract; Slice 6 adds a mechanism but does not touch the dispatch path, so the auto-trigger contract is preserved unchanged.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 - auto-trigger contract preserved; Slice 6 does not alter dispatch behavior or actionable-signature computation.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the priority module is topology-agnostic; both the cross-harness trigger and the single-harness dispatcher will consume the dispatch-priority score.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the single-harness substrate will consume the same module in the integration step.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the dispatch-priority score is a pure derivation over durable bridge artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the slice family is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - age is derived from the bridge artifact's NEW/REVISED filed timestamp (advisory).

## Prior Deliberations

- bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-002.md - the GO on this slice; its P3-CONSTRAINT (deterministic ordering for exact ties), its P4-INFO (integration pending), and its eleven follow-on constraints are addressed in this report.
- bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md - the GO'd proposal; this report implements its scope.
- gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (GO at -002) - the design authority; design decision 5 fixed "Aging weight = monotonic increasing as a function of (now - filed_at)" and deferred the concrete function to the Slice 6 proposal.
- DELIB-2182 - the owner-authorization deliberation for the bridge scheduler program; it records the S350 anti-starvation requirement verbatim.
- gtkb-bridge-scheduler-lanes-leases-slice-2 (VERIFIED at -004), slice-3 (VERIFIED at -006), slice-4 (NEW post-impl at -003), slice-5 (VERIFIED at -006) - the sibling slices; Slice 6 is the final scheduler primitive, the selection score the dispatch loop will consume alongside the Slice 4 limit and Slice 5 lane.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and scaffold the full program (Slices 2-6); that decision is recorded as DELIB-2182. The owner's S350 directive supplied the anti-starvation requirement verbatim ("aging and priority weighting so old items do not starve behind fresh bridge noise"). The MemBase project PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES, work items WI-3373 through WI-3377, and the project authorization PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION were created under that authorization. This Slice 6 implementation is within that authorized scope, asserts no new requirement, and requires no further owner decision before verification.

## Clause Scope Clarification (Not a Bulk Operation)

This implementation creates one new Python module and one new test file. It does not resolve, retire, promote, or batch-mutate work items, and it produces no work-item inventory and requests no formal-artifact-approval packet for a bulk action. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS is not applicable. The single work item cited (WI-3377) is this report's own implementing work item under the mandatory project-linkage metadata.

## What Was Implemented

scripts/bridge_dispatch_priority.py - a standalone, stdlib-only module (imports only datetime) that computes a dispatch-priority score for a bridge entry and orders a set of entries by it. It exposes the GO-approved public API names exactly: the constants DEFAULT_PRIORITY_HEADSTART_HOURS, DEFAULT_PRIORITY, DEFAULT_AGING_RATE_PER_HOUR, and the functions priority_headstart, dispatch_score, sort_by_dispatch_priority, select_next.

- The scoring model is linear effective-age: dispatch_score = priority_headstart(priority) + aging_rate * age_hours, age_hours = max(0.0, (now - filed_at) in hours). The aging term is linear and unbounded, so a sufficiently-aged low-priority entry always eventually outranks a perpetually-fresh high-priority one - the anti-starvation guarantee.
- DEFAULT_PRIORITY_HEADSTART_HOURS = P0 96, P1 72, P2 48, P3 24, P4 0; DEFAULT_PRIORITY = "P3"; DEFAULT_AGING_RATE_PER_HOUR = 1.0.
- A future-dated filed_at clamps age_hours to 0.0 - no negative score, no raise.
- sort_by_dispatch_priority orders entries by descending score; select_next returns the single top entry, or None for empty input.

The GO -002 follow-on constraints are addressed as follows.

Constraint 5 - UTC-aware parsing. The helper _to_utc coerces every filed_at / now input to an aware UTC datetime. The GO permitted "reject or clearly handle" for naive datetimes; this implementation clearly handles them: a naive datetime, or an ISO-8601 string with no offset, is interpreted as UTC - the documented "UTC ISO-8601" input contract - via .replace(tzinfo=timezone.utc); an aware datetime in another zone is converted with .astimezone(timezone.utc). A host-local timezone default never influences a score. "Clearly handle" was chosen over "reject" so that a bare UTC ISO string (the common machine-emitted form) remains a valid input, consistent with the proposal's stated contract; T13 proves four spellings of the same instant score identically.

Constraint 6 - deterministic priority normalization. _normalize_priority upper-cases and whitespace-trims a label before lookup, so "p2" and " P2 " resolve to the canonical "P2" head-start (48 h) rather than silently degrading to DEFAULT_PRIORITY. Only a None, non-string, or genuinely unrecognized label resolves to DEFAULT_PRIORITY. T14 covers this and asserts "p2" does not collapse to the "P3" head-start.

Constraint 7 / P3-CONSTRAINT - deterministic ordering for exact ties. sort_by_dispatch_priority sorts on the key (-score, filed_at); Python's sorted is stable, so two entries with an identical score and an identical filed_at keep their input order. The order is therefore total and deterministic. T12 asserts the input order is preserved for two entries of identical priority and identical filed_at, in both input orders.

platform_tests/scripts/test_bridge_dispatch_priority.py - the test suite, 14 tests; 14 passed. Every test passes an explicit now, so no test depends on the wall clock.

## Spec-To-Test Mapping

| Spec / governing surface | Verification | Result |
| --- | --- | --- |
| Scoping Slice 6 / design decision 5 - aging weight monotonic increasing in (now - filed_at) | T2 asserts dispatch_score strictly increases as an entry's age increases at fixed priority; T1 asserts the priority head-start ordering P0 > P1 > P2 > P3 > P4 at equal age; T3 asserts priority_headstart returns the documented strictly-ordered per-tier values. | PASS - T1, T2, T3. |
| Scoping Slice 6 - old items do not starve behind fresh bridge noise | T5 asserts the anti-starvation guarantee: a P4 entry aged past the P0 head-start outranks a perpetually-fresh P0 entry. | PASS - T5. |
| Scoping Slice 6 - age and priority feed the dispatch selector | T6 sort orders by descending score; T7 within-tier oldest-first; T8 equal-score oldest-first tie-break; T10 select_next returns the top entry and None for empty input. | PASS - T6, T7, T8, T10. |
| GO -002 P3-CONSTRAINT / follow-on constraint 7 - deterministic ordering for exact ties | T12 asserts two entries with identical priority and identical filed_at keep their input order under sort_by_dispatch_priority, in both input orders (stable sort). | PASS - T12. |
| GO -002 follow-on constraint 5 - UTC-aware parsing; host-local time must not influence scores | T13 asserts the same instant expressed as an offset ISO string, a bare (no-offset) ISO string, an aware non-UTC datetime, and a naive datetime all score identically. | PASS - T13. |
| GO -002 follow-on constraint 6 - deterministic case-insensitive priority normalization | T14 asserts "p2" and " P0 " resolve to the P2/P0 head-starts and that "p2" does not degrade to the DEFAULT_PRIORITY head-start; T4 asserts an unknown/None/non-string priority resolves to DEFAULT_PRIORITY without raising. | PASS - T4, T14. |
| Future-dated filed_at clamp | T9 asserts a future filed_at yields the bare priority head-start - no negative score, no raise. | PASS - T9. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Slice 6 creates no runtime state; the module is a pure function. T11 asserts repeated calls are deterministic and that the module source performs no filesystem access (no os/pathlib import, no open). | PASS - T11. |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | Slice 6 adds no dispatch-path code; cross_harness_bridge_trigger.py and single_harness_bridge_dispatcher.py are absent from target_paths and unmodified. | PASS - by inspection. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This report carries the mapping plus the executed pytest command and observed results below. | PASS. |

## Verification Commands And Observed Results

1. `python -m pytest platform_tests/scripts/test_bridge_dispatch_priority.py -q`
   Result: 14 passed in 0.20s. T1-T11 (proposal) plus T12 (exact-tie input order), T13 (timezone handling), T14 (case-insensitive priority normalization).

2. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-6 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-003.md` - see the Applicability Preflight section.

3. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-6 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-003.md` - see the Clause Applicability section.

## Live Dispatch Behavior Unchanged

Per GO -002 P4-INFO and follow-on constraint 11: Slice 6 adds no dispatch-path code. The fixed DEFAULT_MAX_ITEMS caps remain in scripts/cross_harness_bridge_trigger.py and scripts/single_harness_bridge_dispatcher.py, unmodified. Live bridge dispatch behavior is unchanged by this slice. A later integration proposal must consume the Slice 2 lease registry, the Slice 3 serialized INDEX writer, the Slice 4 concurrency module, the Slice 5 lane classifier, and this Slice 6 priority scorer together before the flat cap is retired. The GO -002 P4-INFO noted that the sibling Slice 5 classifier was then at NO-GO; as of this report Slice 5 has reached VERIFIED (bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-006.md), so the integration prerequisite the GO flagged is now satisfied - though the integration proposal itself remains a separate, not-yet-filed bridge thread.

## Acceptance Criteria

- [x] Loyal Opposition returned GO on the proposal (-002).
- [x] scripts/bridge_dispatch_priority.py exists and exposes priority_headstart, dispatch_score, sort_by_dispatch_priority, select_next, and the documented default constants.
- [x] The aging term is linear and unbounded; dispatch_score is monotonic increasing in (now - filed_at) at fixed priority (T2).
- [x] The anti-starvation guarantee holds: a sufficiently-aged low-priority entry outranks a perpetually-fresh high-priority entry (T5).
- [x] sort_by_dispatch_priority and select_next produce a deterministic, total ordering with an oldest-first tie-break and stable input-order preservation for exact ties (T7, T8, T12).
- [x] A future-dated filed_at clamps to zero aging without a negative score or a raise (T9).
- [x] UTC-aware parsing: host-local time never influences a score; priority normalization is deterministic and case-insensitive (T13, T14).
- [x] platform_tests/scripts/test_bridge_dispatch_priority.py covers T1-T11 plus exact-tie, timezone, and case-insensitive coverage, and passes.
- [x] No existing dispatch code is modified - Slice 6 is purely additive; live dispatch behavior is unchanged.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Applicability Preflight

The applicability preflight was run against this -003 report via `--content-file` prior to filing the INDEX entry:

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-6 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-003.md`

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:5d5f5a74db275862270be2205ce0106a5fb54e4d1700c25c3165d0cb123a29fa

All applicable required and advisory cross-cutting specs are cited in this report's Specification Links.

## Clause Applicability

The ADR/DCL clause preflight was run against this -003 report via `--content-file` prior to filing the INDEX entry:

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-6 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-003.md`

- Clauses evaluated: 5 (must_apply: 5, may_apply: 0, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0 (pass)

| Clause | Applicability | Evidence found |
|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | must_apply | yes |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | must_apply | yes |

## Risk And Rollback

- R1 (low): the head-start defaults or aging rate are mis-tuned, so a tier waits longer or shorter than intended before aging overtakes the next tier. Mitigation: every default is a module constant expressed in hours; mis-tuning is corrected by a constant edit. The structural anti-starvation guarantee (linear unbounded aging) holds for any positive aging rate and any finite head-start, and T5 asserts it.
- R2 (low): the new module has no consumer until the integration step. Mitigation: this is the GO'd scoping sub-slice boundary; the 14-test suite exercises every code path in isolation.
- R3 (very low): clock skew or a future-dated filed_at produces a nonsensical score. Mitigation: age_hours is clamped to max(0.0, ...); T9 asserts the future-dated case.
- R4 (very low): a non-UTC or naive timestamp shifts a score by the host offset. Mitigation: _to_utc anchors every input to UTC; T13 asserts four spellings of one instant score identically.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue (the module creates no runtime state).

## Loyal Opposition Asks

1. Confirm scripts/bridge_dispatch_priority.py implements the GO'd -001 design: the linear effective-age model priority_headstart(priority) + aging_rate * age_hours, the documented default constants, the future-dated clamp, and the approved public API names.
2. Confirm GO -002 follow-on constraint 5 is satisfied by the "clearly handle" disposition: a naive datetime or a no-offset ISO string is interpreted as UTC (not host-local), and constraint 6 by case-insensitive priority normalization where "p2" resolves to P2 rather than degrading to DEFAULT_PRIORITY.
3. Confirm the P3-CONSTRAINT is satisfied: sort_by_dispatch_priority is a stable sort, so two entries with an identical score and an identical filed_at keep their input order (T12).
4. Confirm that scoping Slice 6 as a standalone scoring module - with the wiring of select_next into the live dispatch selector deferred to a separate integration proposal - matches the GO'd sub-slice plan; live dispatch behavior is unchanged by this slice.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
