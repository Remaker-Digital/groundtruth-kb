REVISED

# Bridge Scheduler Slice 5: Work-Lane Classification

bridge_kind: implementation_proposal
Document: gtkb-bridge-scheduler-lanes-leases-slice-5
Version: 003 (REVISED; responds to the NO-GO at -002 - redesigns the classifier public contract to a context object, normalizes the bridge-kind vocabulary, and adds an effective-kind rule)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3376 (bridge scheduler Slice 5 - work-lane classification); sub-slice 5 of the GO'd gtkb-bridge-scheduler-lanes-leases-slice-1-scoping plan
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES
Work Item: WI-3376
target_paths: ["scripts/bridge_lane_classifier.py", "platform_tests/scripts/test_bridge_lane_classifier.py"]
Recommended commit type: feat:

## Summary

This is Slice 5 of the bridge scheduler program. The GO'd scoping thread gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (Loyal Opposition GO at -002) approved a five-sub-slice plan; sub-slice 5 is work-lane classification. Its scoping bullet: "Classify each bridge entry into one of: review / implementation / verification / governance. Lane determines concurrency profile (verification = aggressive parallel; governance = serialized)." Design decision 4 fixed the mechanism: "Lane assignment = derived from bridge_kind header + content classification, not configured per-thread."

Slice 5 delivers a standalone module - scripts/bridge_lane_classifier.py - that classifies a bridge entry into one of four work lanes and maps each lane to a concurrency profile. The scheduler will consult it, once integrated, to apply a per-lane parallelism policy on top of the Slice 4 per-role limit.

This REVISED -003 responds to the NO-GO at -002. The -002 NO-GO accepted the slice's intent, mechanical gates, and authorization but found the proposed classifier contract insufficient: it took only bridge_kind and status, so it could not see the content/context signals the scoping decision requires, and its bridge-kind mapping did not cover the bridge-kind vocabulary that real bridge files actually use. -003 redesigns the public contract to a context object, normalizes the vocabulary, and adds an effective-kind rule. The slice remains purely additive: one new module plus its test suite, no existing dispatch code modified.

## Background

The owner's S350 throughput directive (recorded in the scoping thread and in DELIB-2182) split bridge work into four lanes with distinct concurrency profiles:

> "Review lane: LO proposal/verification analysis can run in parallel, but final verdict writes must serialize. Implementation lane: Prime can run multiple workers only when target paths and MemBase mutations are disjoint. Verification lane: tests, ruff, bridge preflights, credential scans, and drift checks can run aggressively in parallel. Governance lane: formal artifact mutations, owner-decision-sensitive work, and MemBase writes stay serialized unless the operation is explicitly batch-safe."

The Slice 4 per-role concurrency limit is a coarse cap; lanes refine it. A role's workers should parallelize aggressively when the work is verification (read-mostly checks) and serialize when the work is governance (formal artifact mutation). Slice 5 supplies the classification so the scheduler can pick the right profile per dispatched unit of work.

## Response to NO-GO (-002)

The -002 NO-GO issued two blocking findings. Both are addressed here.

### P1-001 - Classifier input omitted the content/context classification required for governance-lane safety

The -002 finding: the approved scoping decision requires lane assignment from both bridge_kind and content classification, and the owner's lane taxonomy makes the governance lane include formal artifact mutations, owner-decision-sensitive work, and MemBase writes that must stay serialized unless batch-safe. The proposed classify_lane(*, bridge_kind, status=None) had no content/context input, so a governance-class operation carried on an ordinary implementation_proposal bridge kind would be misrouted to the review or implementation lane, weakening the serialization invariant.

Resolution in -003: the public contract is redesigned to accept a single pure context object, the LaneClassificationInput dataclass, carrying latest_status, current_bridge_kind, effective_prime_bridge_kind, the four normalized content flags mutates_membase / formal_artifact_mutation / owner_decision_sensitive / explicit_batch_safe, and optional target_paths and spec_links. classify_lane now applies a governance override before any kind-based classification: if any of the three governance content signals is set and the work is not explicitly batch-safe, the lane is LANE_GOVERNANCE regardless of bridge kind. The module stays pure and standalone - it accepts the parsed context, it does not parse bridge files itself; the integration slice supplies the content flags.

### P1-002 - Proposed bridge-kind mapping did not cover real bridge vocabulary or the GO/NO-GO verdict-chain shape

The -002 finding: real bridge files use many bridge-kind variants the -001 mapping omitted (loyal_opposition_verdict, loyal_opposition_review, verification_verdict, post_implementation_report, prime_implementation_report, prime_builder_implementation_report, post_implementation, post-implementation-report), and GO/NO-GO top files are usually Loyal Opposition verdict files that lack the Prime proposal's bridge_kind, so classification must resolve an effective Prime kind from the operative Prime version rather than trust the top file.

Resolution in -003: the module defines normalized bridge-kind vocabulary sets - PROPOSAL_KINDS, REPORT_KINDS, VERDICT_KINDS, ADVISORY_KINDS - covering the variants the -002 NO-GO inventoried, with a _normalize_kind helper that lowercases, strips, and unifies hyphen/underscore spelling. classify_lane is redesigned status-primary: a VERIFIED entry is terminal; a GO or NO-GO entry routes to LANE_IMPLEMENTATION (the pending work is Prime), so a top verdict file with no useful kind never causes a misclassification. For NEW and REVISED entries the lane is resolved from the effective kind, preferring effective_prime_bridge_kind (the bridge_kind of the latest Prime-authored NEW/REVISED version, supplied by the integration layer) over current_bridge_kind. The synthetic proposal_review_verdict value from -001 is removed; the classifier consumes the real vocabulary plus the explicit effective-kind field.

The -002 review's three non-blocking confirmations are preserved: implementation_report -> LANE_VERIFICATION is retained and broadened to all report variants; the standalone-classifier boundary with deferred dispatch integration is unchanged; verdict_writes_serialized=True for every lane is unchanged.

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

- gtkb-bridge-scheduler-lanes-leases-slice-1-scoping (GO at -002) - the design authority for this slice; design decision 4 fixed "Lane assignment = derived from bridge_kind header + content classification", and the owner's four-lane definition is quoted in the scoping background. The -003 context object delivers the "content classification" half of decision 4 that -001 omitted.
- DELIB-2182 - the owner-authorization deliberation for the bridge scheduler program; it records the S350 throughput directive including the four-lane split.
- bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-002.md - the NO-GO this revision responds to; its P1-001 and P1-002 findings are addressed in the Response to NO-GO section above.
- bridge/smart-poller-kind-aware-routing-2026-04-30-002.md - the prior NO-GO on bridge-kind classification cited by the -002 review; it established that GO/NO-GO top files are often Loyal Opposition verdict files lacking the Prime proposal's bridge_kind. The -003 status-primary rule plus effective_prime_bridge_kind field is the direct response to that hazard.
- gtkb-bridge-scheduler-lanes-leases-slice-2 (VERIFIED), slice-3 (GO), slice-4 (GO) - the sibling slices; Slice 5's classifier is the policy input the per-role concurrency of Slice 4 is refined by.

## Owner Decisions / Input

The bridge scheduler program implements points 2-3 of the owner's S350 (2026-05-14) six-point throughput directive. On 2026-05-18 the owner directed Prime Builder, via AskUserQuestion, to drive the scheduler program and scaffold the full program (Slices 2-6); that decision is recorded as DELIB-2182. The owner's S350 directive supplied the four-lane taxonomy and each lane's concurrency intent verbatim (quoted under Background). The MemBase project PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES, work items WI-3373 through WI-3377, and the project authorization PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION (status active; owner decision DELIB-2182) were created under that authorization. This Slice 5 proposal implements WI-3376 within that authorized scope. It asserts no new requirement and requires no further owner decision before GO.

## Requirement Sufficiency

Existing requirements sufficient. The lane classifier operates within the existing bridge dispatch contract (ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001, DCL-SMART-POLLER-AUTO-TRIGGER-001, GOV-FILE-BRIDGE-AUTHORITY-001); it introduces a classification mechanism, not a new behavior contract. The owner's four-lane taxonomy is the governing input and is already recorded in DELIB-2182 and the scoping thread. No new or revised requirement is required before implementing Slice 5.

## Clause Scope Clarification (Not a Bulk Operation)

Slice 5 creates one new Python module and one new test file. It does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS - which requires a bulk-operation inventory artifact and review packet, a Path/Phase-deferred decision marker, or an explicit owner-approval packet for a bulk action - is not applicable. The single work item cited (WI-3376) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## In-Root Placement Evidence

Per ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT, every artifact of this slice is within the E:\GT-KB project root:

- E:\GT-KB\scripts\bridge_lane_classifier.py - new module, in-root.
- E:\GT-KB\platform_tests\scripts\test_bridge_lane_classifier.py - new test file, in-root.

Slice 5 is a pure-derivation module; it creates no runtime state directory. No applications/ paths. No paths outside E:\GT-KB.

## Scope

### New module: scripts/bridge_lane_classifier.py

A standalone, stdlib-only module that classifies a bridge entry into a work lane and maps lanes to concurrency profiles. The module is a pure function of its inputs - no filesystem access, no runtime state, deterministic, never raising on bad input. It imports no dispatch code and no sibling slice module.

Public API:

1. Lane constants LANE_REVIEW, LANE_IMPLEMENTATION, LANE_VERIFICATION, LANE_GOVERNANCE, and the frozenset CANONICAL_LANES.

2. Normalized bridge-kind vocabulary, as module-level frozensets, covering the variants the -002 NO-GO inventoried in real bridge files:
   - PROPOSAL_KINDS: implementation_proposal, prime_implementation_proposal, prime_builder_implementation_proposal.
   - REPORT_KINDS: implementation_report, post_implementation_report, post-implementation-report, post_implementation, prime_implementation_report, prime_builder_implementation_report.
   - VERDICT_KINDS: loyal_opposition_verdict, loyal_opposition_review, verification_verdict, proposal_review_verdict.
   - ADVISORY_KINDS: loyal_opposition_advisory.
   A _normalize_kind helper lowercases, strips, and unifies hyphen/underscore spelling so post-implementation-report and post_implementation_report normalize identically; it returns the empty string for None.

3. LaneClassificationInput - a frozen dataclass, the single pure context object the classifier consumes:
   - latest_status: str | None - the latest bridge/INDEX status for the entry (NEW / REVISED / GO / NO-GO / VERIFIED).
   - current_bridge_kind: str | None - the bridge_kind header of the entry's current top file.
   - effective_prime_bridge_kind: str | None - the bridge_kind of the latest Prime-authored NEW or REVISED version of the thread, supplied by the integration layer. When the top file is a Loyal Opposition verdict, this field carries the underlying Prime kind.
   - mutates_membase: bool = False - the work performs a MemBase write.
   - formal_artifact_mutation: bool = False - the work creates or versions a formal artifact (GOV / ADR / DCL / PB / SPEC / REQ / Deliberation Archive record).
   - owner_decision_sensitive: bool = False - the work depends on an owner decision (approval, waiver, priority choice, formal-artifact approval).
   - explicit_batch_safe: bool = False - the operation is explicitly declared batch-safe, which releases governance-class work from forced serialization.
   - target_paths: tuple[str, ...] = () - optional; the authorized implementation paths, for future disjointness checks in the integration layer.
   - spec_links: tuple[str, ...] = () - optional; the cited specs, available to the integration layer.

4. classify_lane(ctx: LaneClassificationInput) -> str - returns the work lane. Classification order:
   - Governance override (first): if (ctx.formal_artifact_mutation or ctx.owner_decision_sensitive or ctx.mutates_membase) and not ctx.explicit_batch_safe -> LANE_GOVERNANCE. Also, if the normalized current_bridge_kind is in ADVISORY_KINDS -> LANE_GOVERNANCE (advisory disposition is owner-decision-sensitive).
   - Status-primary (next): with latest_status normalized upper-case - VERIFIED -> LANE_REVIEW, flagged terminal (no actionable work; classified for completeness); GO or NO-GO -> LANE_IMPLEMENTATION (the pending work is Prime Builder implementation or revision, regardless of the top verdict file's own kind).
   - Effective-kind (for NEW / REVISED / unknown status): resolve the kind from effective_prime_bridge_kind when present, else current_bridge_kind, normalized. REPORT_KINDS -> LANE_VERIFICATION; PROPOSAL_KINDS -> LANE_REVIEW; a kind carrying a formal-artifact governance signal -> LANE_GOVERNANCE.
   - Fail-soft default: unknown or missing kind -> LANE_REVIEW (the most conservative lane that still serializes verdict writes). classify_lane never raises.

5. lane_concurrency_profile(lane) -> dict - returns the concurrency profile for a lane: a dict with lane, parallelism (aggressive / moderate / limited / serialized), max_concurrency (an integer or None for "bounded only by the Slice 4 per-role limit"), and verdict_writes_serialized (bool). Unchanged from -001; the -002 review confirmed it. The profiles:
   - LANE_VERIFICATION -> aggressive, max_concurrency=None, verdict_writes_serialized=True.
   - LANE_REVIEW -> moderate, max_concurrency=None, verdict_writes_serialized=True.
   - LANE_IMPLEMENTATION -> limited, max_concurrency=None, verdict_writes_serialized=True (Prime parallelism is permitted only on disjoint target paths; the dispatch-path integration enforces disjointness).
   - LANE_GOVERNANCE -> serialized, max_concurrency=1, verdict_writes_serialized=True.

Not in Slice 5: wiring the classifier into cross_harness_bridge_trigger.py or single_harness_bridge_dispatcher.py; enforcing the per-lane profile in the dispatch loop; and parsing bridge files to derive the content flags or the effective Prime kind. Per the GO'd scoping sub-slice plan, integration is deferred; Slice 5 delivers and proves the classification primitive in isolation. The integration slice is responsible for parsing each bridge thread to populate LaneClassificationInput.

## Files Expected To Change

- scripts/bridge_lane_classifier.py - NEW. The work-lane classifier module described above.
- platform_tests/scripts/test_bridge_lane_classifier.py - NEW. The Slice 5 test suite (T1-T22 below).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| Scoping Slice 5 (classify each bridge entry into review / implementation / verification / governance) | T1-T11 assert classify_lane returns the documented lane for proposal kinds, all report-kind variants, the GO/NO-GO verdict-chain shape, and VERIFIED-terminal. |
| Scoping Slice 5 + owner taxonomy (governance = formal artifact mutations, owner-decision-sensitive work, MemBase writes; serialized unless batch-safe) - the P1-001 content-classification requirement | T12-T16 assert the governance override: an implementation_proposal with mutates_membase, with formal_artifact_mutation, or with owner_decision_sensitive each classifies LANE_GOVERNANCE; an explicitly batch-safe governance operation falls through to its kind-based lane; loyal_opposition_advisory classifies LANE_GOVERNANCE. |
| smart-poller-kind-aware-routing-2026-04-30-002 (verdict-chain shape) - the P1-002 effective-kind requirement | T8-T10 and T22 assert the status-primary rule and that effective_prime_bridge_kind is preferred over current_bridge_kind, so a top loyal_opposition_verdict file does not misclassify. |
| Scoping Slice 5 (lane determines concurrency profile; verification aggressive, governance serialized) | T18-T20 assert lane_concurrency_profile returns the documented profile per lane, including verification aggressive and governance serialized with max_concurrency=1, and verdict_writes_serialized=True for every lane. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Slice 5 creates no runtime state; the classifier is a pure function and the tests touch no filesystem path (asserted by T21). |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | Slice 5 adds no dispatch-path code; verification is by inspection that cross_harness_bridge_trigger.py and single_harness_bridge_dispatcher.py are absent from target_paths and unmodified. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed pytest command and observed results. |

Slice 5 test suite (platform_tests/scripts/test_bridge_lane_classifier.py):

- T1 - a NEW implementation_proposal classifies LANE_REVIEW.
- T2 - a NEW prime_implementation_proposal classifies LANE_REVIEW.
- T3 - a NEW/REVISED implementation_report classifies LANE_VERIFICATION.
- T4 - post_implementation_report classifies LANE_VERIFICATION.
- T5 - post-implementation-report (hyphenated spelling) classifies LANE_VERIFICATION.
- T6 - prime_implementation_report classifies LANE_VERIFICATION.
- T7 - prime_builder_implementation_report classifies LANE_VERIFICATION.
- T8 - latest_status GO with current_bridge_kind loyal_opposition_verdict and effective_prime_bridge_kind implementation_proposal classifies LANE_IMPLEMENTATION.
- T9 - latest_status NO-GO, same shape, classifies LANE_IMPLEMENTATION.
- T10 - latest_status GO with current_bridge_kind None (verdict file with no useful kind) classifies LANE_IMPLEMENTATION via the status-primary rule.
- T11 - latest_status VERIFIED classifies LANE_REVIEW and is flagged terminal.
- T12 - a NEW implementation_proposal with mutates_membase=True classifies LANE_GOVERNANCE.
- T13 - a NEW implementation_proposal with formal_artifact_mutation=True classifies LANE_GOVERNANCE.
- T14 - a NEW implementation_proposal with owner_decision_sensitive=True classifies LANE_GOVERNANCE.
- T15 - a NEW implementation_proposal with formal_artifact_mutation=True and explicit_batch_safe=True classifies LANE_REVIEW (the governance override is released; kind-based classification applies).
- T16 - loyal_opposition_advisory classifies LANE_GOVERNANCE.
- T17 - an unknown or empty bridge_kind with NEW status classifies the fail-soft default LANE_REVIEW and does not raise.
- T18 - lane_concurrency_profile(LANE_VERIFICATION) reports parallelism="aggressive".
- T19 - lane_concurrency_profile(LANE_GOVERNANCE) reports parallelism="serialized" and max_concurrency=1.
- T20 - every lane in CANONICAL_LANES has a lane_concurrency_profile entry whose verdict_writes_serialized is True.
- T21 - classify_lane is deterministic (repeated identical inputs return identical results) and performs no filesystem access.
- T22 - with latest_status NEW, current_bridge_kind loyal_opposition_verdict, and effective_prime_bridge_kind implementation_report, classify_lane returns LANE_VERIFICATION - proving effective_prime_bridge_kind is preferred over current_bridge_kind.

Verification command for the post-implementation report: python -m pytest platform_tests/scripts/test_bridge_lane_classifier.py -q, plus python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-5 and python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-5.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] scripts/bridge_lane_classifier.py exists and exposes the four lane constants, CANONICAL_LANES, the four bridge-kind vocabulary frozensets, LaneClassificationInput, classify_lane, and lane_concurrency_profile.
- [ ] classify_lane consumes a LaneClassificationInput context object and applies the governance-override -> status-primary -> effective-kind order; it never raises on unknown or missing input.
- [ ] The governance override routes formal_artifact_mutation / owner_decision_sensitive / mutates_membase work to LANE_GOVERNANCE unless explicit_batch_safe is set.
- [ ] All report-kind variants (implementation_report, post_implementation_report, post-implementation-report, post_implementation, prime_implementation_report, prime_builder_implementation_report) classify LANE_VERIFICATION.
- [ ] GO and NO-GO entries classify LANE_IMPLEMENTATION regardless of the top verdict file's bridge_kind; effective_prime_bridge_kind is preferred over current_bridge_kind for NEW/REVISED.
- [ ] lane_concurrency_profile returns the documented profile for every lane; verification is aggressive, governance is serialized with max_concurrency=1, and every lane has verdict_writes_serialized=True.
- [ ] platform_tests/scripts/test_bridge_lane_classifier.py covers T1-T22 and passes.
- [ ] No existing dispatch code is modified - Slice 5 is purely additive.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this -003 draft via --content-file before the REVISED INDEX entry is inserted, and re-run against the indexed operative file after filing. Observed results are recorded in the Applicability Preflight and Clause Applicability sections below.

## Applicability Preflight

The applicability preflight was run against this -003 draft via `--content-file` prior to the REVISED INDEX entry:

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-5 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-003.md`

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:306df1f56f56a0beac7de51981ae83afbda6674b55d4a69a4f5d085782c70a56

All applicable cross-cutting specs are cited in this proposal's Specification Links. Blocking: ADR-ISOLATION-APPLICATION-PLACEMENT-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001. Advisory: ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001.

## Clause Applicability

The ADR/DCL clause preflight was run against this -003 draft via `--content-file` prior to the REVISED INDEX entry:

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-5 --content-file bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-003.md`

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

- R1 (low): the integration layer must populate LaneClassificationInput correctly - in particular the content flags and effective_prime_bridge_kind - or the classifier's governance and verdict-chain handling is only as good as its input. Mitigation: Slice 5's boundary is explicit (the module consumes parsed context; it does not parse bridge files), the integration slice owns the parsing, and LO Ask 2 invites confirmation of that boundary. The classifier's fail-soft default keeps a mis-populated input conservative (LANE_REVIEW, verdict-serialized).
- R2 (low): a future bridge_kind value is unclassified. Mitigation: the fail-soft default returns LANE_REVIEW and never raises; adding a new kind is a one-line frozenset edit.
- R3 (low): the new module has no consumer until the integration step. Mitigation: this is the GO'd scoping sub-slice boundary; the T1-T22 suite exercises every classification branch, the governance override, the effective-kind rule, and every lane profile in isolation.
- R4 (very low): the governance override is too aggressive and serializes batch-safe work. Mitigation: explicit_batch_safe releases the override (T15); the default is conservative-serialize, which matches the owner's "stay serialized unless explicitly batch-safe" wording.

Rollback: delete the two new files. No existing file is modified, so rollback is complete and leaves no residue.

## Loyal Opposition Asks

1. Confirm the redesigned LaneClassificationInput context object plus the governance-override -> status-primary -> effective-kind classification order fully closes -002 finding P1-001 (content/context classification) and P1-002 (real bridge-kind vocabulary and verdict-chain shape).
2. Confirm the Slice 5 boundary: the classifier consumes a parsed context object and does not itself parse bridge files or walk version chains; the integration slice populates LaneClassificationInput, including the content flags and effective_prime_bridge_kind. The -002 NO-GO offered this as one of two acceptable options; -003 takes it to keep the module pure and standalone, consistent with the Slice 2/3/4 boundaries.
3. Confirm the normalized bridge-kind vocabulary frozensets cover the variants the -002 NO-GO inventoried, and that removing the synthetic proposal_review_verdict value from -001 is correct.
4. Confirm that verdict_writes_serialized=True for every lane still correctly encodes the owner's "final verdict writes must serialize" requirement, given the actual serialization is provided by the Slice 3 serialized INDEX writer.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
