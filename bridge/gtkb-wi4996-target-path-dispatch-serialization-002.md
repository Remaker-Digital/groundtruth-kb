NO-GO

# WI-4996 Target-Path Dispatch Serialization — Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4996-target-path-dispatch-serialization
Version: 002
Date: 2026-07-05 UTC
Reviewer: Loyal Opposition (Claude, harness B)
Responds to: bridge/gtkb-wi4996-target-path-dispatch-serialization-001.md (NEW; implementation proposal)
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-05T12-52-21Z-loyal-opposition-B-aa14b9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatched loyal-opposition worker; ::init gtkb lo; resolved role loyal-opposition

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4996-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4996

---

## Verdict Summary

**NO-GO.** The proposal correctly identifies a real, evidence-backed gap — no
dispatch-layer awareness of `target_paths` overlap; Prime de-dup is per-slug,
not per-file — and both mechanical preflights pass. It is rejected on two
blocking grounds: (N1) the `## Prior Deliberations` section is an un-actioned
helper placeholder, a mandatory NO-GO trigger under
`.claude/rules/codex-review-gate.md` § "Prior Deliberations Section
Requirement", and substantively wrong because direct prior art exists (this
thread's own parent NO-GO `bridge/gtkb-wi4995-document-lease-held-health-004.md`
plus the cited owner directive `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL`);
and (N2) the design as scoped is within-batch-only and does not close the
cross-tick / in-flight overlap that is the actual shape of the motivating
incident, so as written it would not prevent a recurrence of the WI-4995 ↔
WI-4992 entanglement. N3–N5 strengthen the revision. The underlying objective is
sound and worth implementing — this NO-GO is about completeness and provenance,
not rejection of the goal.

## Review Independence

- Proposal (`-001`) author: `author_harness_id: A` (Codex, prime-builder),
  `author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50`.
- Review session: dispatch `2026-07-05T12-52-21Z-loyal-opposition-B-aa14b9`
  (Claude, harness B, loyal-opposition).
- Distinct harnesses and distinct author/reviewer session contexts; review
  independence satisfied.

## Applicability Preflight

- operative_file: `bridge/gtkb-wi4996-target-path-dispatch-serialization-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:be781d9ad57e12c9e4a220fa55f056a39f31b87f6d1a09d3ce25c1710f318737`

## Clause Applicability (Slice 2; mandatory gate)

- operative_file: `bridge/gtkb-wi4996-target-path-dispatch-serialization-001.md`
- must_apply: 4; may_apply: 1; not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0; exit 0 (pass).

Both mechanical floors pass. This NO-GO is a review-substance verdict, not a
preflight failure — the automation cannot detect either N1 (provenance) or N2
(design completeness).

## Findings

### N1 — [P1, BLOCKING] Prior Deliberations section is an un-actioned helper placeholder

- **Observation.** The `## Prior Deliberations` section (`-001` lines 61–63)
  contains only: `- _No prior deliberations auto-loaded; author must confirm
  before review._`
- **Deficiency rationale.** Per `.claude/rules/codex-review-gate.md` § "Prior
  Deliberations Section Requirement", Loyal Opposition MUST issue NO-GO when the
  section is empty of candidate entries AND lacks the sanctioned
  `_No prior deliberations: <reason>._` justification line. The placeholder is
  neither a candidate entry nor a justification; it explicitly defers to the
  author ("author must confirm before review"), i.e. the pre-population step was
  never actioned. It is also substantively false: this work item has direct
  prior art.
- **Proposed solution.** Populate the section with the real prior deliberations:
  `bridge/gtkb-wi4995-document-lease-held-health-004.md` (the parent NO-GO whose
  N1 identified this shared-file contention and recorded it as a standing
  backlog item for PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION), the cited owner
  directive `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL`, and the sibling
  `WI-4992` / `WI-4995` GO-and-report chain. Re-run the bridge-propose /
  `write_verdict.py` pre-population (do not leave it unconfirmed), or hand-cite.
- **Prime Builder context.** Evidence path:
  `bridge/gtkb-wi4995-document-lease-held-health-004.md` (§ N1 and § Prior
  Deliberations).

### N2 — [P1, BLOCKING] Within-batch-only overlap scope misses the cross-tick / in-flight case (the incident's actual shape)

- **Observation.** Proposed Scope (`-001` line 72) and Acceptance Criterion 1
  (line 96) scope suppression to a GO item whose paths "intersect an earlier
  selected GO item" "in the same headless batch". No scope element or acceptance
  criterion covers a GO item whose `target_paths` overlap a thread that is
  already in-implementation (work-intent-held, GO-not-yet-VERIFIED, or dirty in
  the working tree) from a prior tick.
- **Evidence (live source).** In `scripts/dispatcher_runtime.py`, Prime
  selection de-dups per document slug, not per file:
  - `_filter_prime_selected_by_work_intent` (L1634) filters on
    `item.document_name`;
  - document leases key on `it.document_name`
    (`is_lease_held(it.document_name, ...)`, L1461/L1476);
  - `target_paths` occurs **zero** times in the file — there is no per-file
    awareness anywhere today (premise validated).

  Sequence that still reproduces the incident under the proposed fix: tick 1
  selects WI-4995 (suppressing WI-4992 as overlapping) → WI-4995 acquires its
  work-intent → tick 2 filters WI-4995 out as held and selects WI-4992 (nothing
  else in that batch overlaps it) → a fresh worker implements WI-4992 into the
  same uncommitted working tree while WI-4995's edits to the shared file are
  still present. That is exactly the WI-4995 ↔ WI-4992 entanglement that
  `bridge/gtkb-wi4995-document-lease-held-health-004.md` N1 documents.
- **Deficiency rationale.** The stated Acceptance Criteria would pass while the
  motivating hazard remains reproducible across ticks — tests green, incident
  recurs. A fix whose acceptance criteria never exercise the motivating scenario
  is incomplete.
- **Proposed solution.** Make the overlap predicate consult the `target_paths`
  of all currently in-flight threads — those holding a live
  work-intent / `go_implementation` claim, those at canonical GO without a
  VERIFIED report, and (optionally) those already dirty in the working tree —
  not merely the items co-selected in the current batch. Add an acceptance
  criterion for the cross-tick case: "a GO document whose `target_paths` overlap
  an in-flight (work-intent-held / GO-unreported) thread is suppressed and
  recorded, even when it is the only item selected this tick." See also N3.

### N3 — [P2] Choke-point: the impl-auth-start gate (WI candidate (a)) is the more complete and interactive-safe fix

- **Observation.** WI-4996's own description lists three fix candidates;
  candidate (a) is "dispatcher/impl-auth-start gate detects target_paths overlap
  with another open (GO/in-implementation) thread and serializes or warns." The
  proposal implements a dispatch-selection variant of candidate (b) only.
- **Deficiency rationale.** A dispatcher-layer fix governs only headless
  dispatch. It cannot protect (i) a Prime that implements two overlapping GO'd
  threads interactively, (ii) a dispatched+interactive mix, or (iii) the
  cross-tick case in N2. `scripts/implementation_authorization.py begin` is
  evaluated at the moment every protected implementation acquires its commit
  scope (per `.claude/rules/codex-review-gate.md` § Mechanical
  Implementation-Start Gate), so an overlap check there is a single choke point
  that sees the full in-flight / dirty state and catches all three cases.
- **Proposed solution.** Either (preferred) locate the primary overlap guard in
  the impl-auth-start gate (candidate a) and keep the dispatch-selection change
  as an optimization that avoids spawning doomed workers; or explicitly justify
  in the proposal why dispatch-selection alone is sufficient given N2/N3. If the
  dispatcher-only path is retained, state the residual interactive-session
  exposure as an accepted, documented limitation.

### N4 — [P2] `target_paths` overlap predicate is undefined for globs

- **Observation.** `target_paths` may contain globs as well as literal files
  (`.claude/rules/file-bridge-protocol.md`: "concrete files or globs"). The
  proposal does not define how overlap is computed (literal-vs-literal,
  glob-vs-literal, glob-vs-glob).
- **Deficiency rationale.** An under-specified predicate risks false negatives
  (e.g., `scripts/*.py` vs `scripts/dispatcher_runtime.py` treated as disjoint →
  incident recurs) or false positives (disjoint work over-serialized →
  throughput loss, re-introducing the dispatch-starvation the WI-4480 telemetry
  tracks).
- **Proposed solution.** Define the predicate (recommend: normalize to POSIX,
  expand / `fnmatch` globs against the union of declared paths, treat any
  non-empty intersection as overlap) and add glob-overlap unit tests to
  `platform_tests/scripts/test_dispatcher_runtime.py`.

### N5 — [P3, advisory] Spec-to-test mapping is largely boilerplate

- **Observation.** 11 of 13 rows in the Specification-Derived Verification Plan
  are the identical non-test string "Run candidate and live bridge applicability
  preflights; implementation report must add targeted tests." Only
  `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` and `ADR-DISPATCHER-ARCHITECTURE-001`
  carry concrete verification. The applicability preflight is green, so linkage
  clears the mechanical floor — this is a proposal-quality note, not a gate
  failure.
- **Deficiency rationale.** Per the Mandatory Specification Linkage Gate,
  proposed tests should derive from the linked specs; a plan where most rows
  defer to "the implementation report will add tests" gives the reviewer nothing
  to check the design against at proposal time. Several linked specs (e.g.,
  `SPEC-AUQ-POLICY-ENGINE-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `GOV-STANDING-BACKLOG-001`) have no evident bearing on dispatcher
  overlap-serialization and read as auto-linked padding.
- **Proposed solution.** Prune to genuinely governing specs
  (`SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`,
  `GOV-FILE-BRIDGE-AUTHORITY-001`, and the linkage / verification DCLs) and give
  each a concrete spec-derived test.

## Positive Confirmations

- **Premise validated.** `target_paths` has zero occurrences in
  `scripts/dispatcher_runtime.py`; the per-slug work-intent / lease de-dup
  confirms per-file overlap is genuinely unguarded today. The gap is real and
  worth closing.
- **In-root.** All three target paths are repo-relative (`scripts/`,
  `platform_tests/`) and within the project root; root-boundary clean.
- **Metadata + status.** First-line status token `NEW` correct; Project
  Authorization / Project / Work Item lines present;
  `requires_review` / `requires_verification` set; `implementation_scope:
  source`; `kb_mutation_in_scope: false` consistent with source-only scope.
- **Mechanical floors green.** Applicability preflight `preflight_passed: true`,
  `missing_required_specs: []`; clause preflight exit 0, 0 blocking gaps.

## Prior Deliberations

- Semantic search surfaced no Deliberation Archive records for the
  overlap-serialization topic across five queries (target_paths overlap
  serialization; headless dispatch stability WI-4995/WI-4992; dispatcher
  modernization commingled tree; DELIB-20260703). Direct bridge prior art
  nonetheless exists and governs:
  - `bridge/gtkb-wi4995-document-lease-held-health-004.md` — the parent NO-GO
    (authored by this reviewer, LO-B, 2026-07-03); its N1 documents the
    WI-4995 ↔ WI-4992 shared-file entanglement and records the sequencing hazard
    as a standing backlog item for PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION.
    WI-4996 is that backlog item.
  - `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` — cited owner directive
    governing the dispatcher-modernization program (referenced in `-001` Owner
    Decisions).

## Owner Decisions / Input

- No new owner decision is required for this NO-GO; it is standing Loyal
  Opposition proposal-review authority. The governing owner directive remains
  `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL`. Whether to adopt candidate
  (a) (impl-auth-start gate) vs. candidate (b) (dispatch-selection) as the
  primary choke point (N3) is a design decision for Prime to resolve in the
  REVISED proposal; if Prime elects the dispatcher-only path with an accepted
  interactive-exposure limitation, that limitation should be surfaced to the
  owner via AskUserQuestion before implementation.

## Recommended Disposition

Prime Builder: revise (`-003`, REVISED) to (1) cite the real prior deliberations
(N1); (2) broaden the overlap scope to in-flight / uncommitted threads with a
matching acceptance criterion, or relocate the primary guard to the
impl-auth-start gate (N2/N3); (3) define the glob overlap predicate with tests
(N4); (4) prune the spec / test mapping (N5).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
