GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-05T13-57-33Z-loyal-opposition-B-6850eb
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatched loyal-opposition worker; ::init gtkb lo; resolved role loyal-opposition; reasoning=max

# WI-4996 Target-Path Dispatch Serialization — REVISED Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4996-target-path-dispatch-serialization
Version: 004
Date: 2026-07-05 UTC
Reviewer: Loyal Opposition (Claude, harness B)
Responds to: bridge/gtkb-wi4996-target-path-dispatch-serialization-003.md (REVISED; implementation proposal)

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4996-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4996

---

## Verdict Summary

**GO.** The REVISED proposal resolves all five findings from the prior NO-GO
(`bridge/gtkb-wi4996-target-path-dispatch-serialization-002.md`, N1–N5), both
mechanical preflights pass on the live `-003` operative file, and — critically —
every design premise the revision adds is independently confirmed against live
source this session. The N3 pivot (make the implementation-start authorization
path the primary overlap guard, with dispatcher filtering as an optimization) is
not new machinery: it wires an existing, tested helper
(`cross_claim_path_collision_reason`, WI-4471) into the begin-time path where it
is not yet invoked, which makes the corrected design *lower* risk than the
original dispatcher-only approach. Approved for implementation within the
declared `target_paths` scope.

## Review Independence

- Proposal (`-003`) author: `author_harness_id: A` (Codex, prime-builder),
  `author_session_context_id: 2026-07-05T13-46-01Z-prime-builder-A-0e1a17`.
- Review session: dispatch `2026-07-05T13-57-33Z-loyal-opposition-B-6850eb`
  (Claude, harness B, loyal-opposition).
- Distinct harnesses and distinct author/reviewer session contexts; review
  independence satisfied. (The `-002` NO-GO was authored by this reviewer in a
  different prior session, `2026-07-05T12-52-21Z-loyal-opposition-B-aa14b9`;
  that is not the artifact under review and does not affect independence for
  `-003`.)

## Applicability Preflight

- operative_file: `bridge/gtkb-wi4996-target-path-dispatch-serialization-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:33c4be51693c770b0cbf34b88d83d77ef490bba0fcf115a63b521a4490ea7570`

## Clause Applicability (Slice 2; mandatory gate)

- operative_file: `bridge/gtkb-wi4996-target-path-dispatch-serialization-003.md`
- Clauses evaluated: 5; must_apply: 4; may_apply: 1; not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0; exit 0 (pass).

Both mechanical floors pass on the operative `-003` file.

## Resolution Of Prior NO-GO Findings (N1–N5)

### N1 — [RESOLVED] Prior Deliberations placeholder removed

The `-001` placeholder ("_No prior deliberations auto-loaded; author must
confirm before review._") is gone. `-003` Prior Deliberations now cites the
parent NO-GO `bridge/gtkb-wi4995-document-lease-held-health-004.md`, the owner
directive `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL`, the `-002` NO-GO,
and the sibling WI-4992 / WI-4995 chains, and discloses that the DA semantic
searches returned no records. I independently re-ran three DA searches this
session (target_paths overlap serialization; impl-authorization begin
cross-claim collision WI-4471; WI-4996/WI-4995/WI-4992 entanglement) and
confirm zero DA hits — the disclosed direct bridge prior art is the correct
governing provenance.

### N2 — [RESOLVED] Cross-tick / in-flight overlap now in scope

`-003` Revision Response N2 broadens overlap coverage to an active
work-intent / `go_implementation` claim from a prior tick, a valid named
authorization packet held by another session, and a GO thread whose
implementation is unreported or not yet VERIFIED — not merely co-selected
batch items. A matching acceptance criterion was added: "A later dispatcher
tick suppresses a GO document whose target_paths overlap an in-flight
work-intent-held or packet-held thread, even when the later document is the
only selected item for that tick." That criterion exercises the exact
WI-4995 to WI-4992 cross-tick sequence the `-002` N2 showed the original scope
would have missed.

### N3 — [RESOLVED, and independently validated as the lower-risk design]

`-003` adopts the LO-preferred candidate (a): the implementation-start
authorization path is the primary guard; dispatcher filtering is an
optimization that avoids launching doomed workers. I verified this is sound
against live source:

- `scripts/implementation_authorization.py:1796` defines
  `cross_claim_path_collision_reason(project_root, *, targets, bridge_id,
  session_id)` — it already scans by-bridge named packets, checks live
  claim-holders with a *different* session_id, computes overlap via
  `path_authorized`, and returns a collision reason citing
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`.
- That helper is already invoked by the protected-mutation backstop at
  `scripts/implementation_start_gate.py:1170` (the WI-4471 cross-claim
  path-collision check). So the proposal's claim to "preserve the existing
  `implementation_start_gate.py` collision backstop" references real behavior,
  not a phantom.
- `create_packet` (the body `begin` runs, `scripts/implementation_authorization.py`
  around L1239 to L1330) does NOT currently call
  `cross_claim_path_collision_reason`. The proposal's "add or complete
  begin-time target-path collision protection" is therefore genuine,
  well-scoped new work: invoke the existing helper (or an equivalent) inside the
  begin path before the packet is written. This is a small, low-risk change
  that reuses a tested predicate.

### N4 — [RESOLVED] Glob overlap predicate defined and consistent with live code

`-003` Revision Response N4 defines a 5-step predicate. I confirmed it is
consistent with — and a correct superset of — the existing
`path_authorized(packet, relative_path)` at
`scripts/implementation_authorization.py:1655`, which already implements
exact-match, `fnmatch` glob-vs-file, and `/**` directory-prefix semantics
(predicate steps 1 to 3). Step 4 (glob-vs-glob) is the genuinely new case the
existing helper does not handle (calling `path_authorized` with a glob as the
`relative_path` would fnmatch the glob-as-literal, which is wrong), and the
proposal handles it conservatively (fail-closed as overlapping unless provably
disjoint by top-level prefix). This directly closes the
`scripts/*.py` vs `scripts/dispatcher_runtime.py` false-negative I raised in
`-002` N4, while bounding false positives via top-level prefix disjointness.

### N5 — [RESOLVED, advisory] Spec-to-test mapping now concrete

Every row of the `-003` Specification-Derived Verification Plan now carries a
concrete verification action rather than the identical "implementation report
must add targeted tests" boilerplate. Prime elected to give each auto-linked
spec a concrete verification rather than prune the list — an acceptable
resolution: the applicability preflight *requires* the blocking cross-cutting
specs (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`),
so pruning them would risk `missing_required_specs`. N5 was P3/advisory; the
substance (concrete verification per spec) is satisfied.

## Independent Premise Verification (live source, this session)

- **Per-file overlap is genuinely unguarded at dispatch today.** `target_paths`
  appears only in import/helper wiring in `scripts/dispatcher_runtime.py`
  (`write_named_packet` import path, packet construction) — Prime selection
  de-dups per document slug, not per source file, so the motivating gap is real.
- **Suppression routing infrastructure already exists.**
  `scripts/dispatcher_runtime.py:211` defines
  `DISPATCH_SUPPRESSIONS_FILENAME = "dispatch-suppressions.jsonl"` and
  `scripts/dispatcher_runtime.py:1262` defines `_record_dispatch_suppression`,
  the WI-4396 pattern that routes expected lease/contention suppressions to
  `dispatch-suppressions.jsonl` instead of `dispatch-failures.jsonl`. The
  proposal's plan to route `target_path_overlap_*` suppressions there follows
  the established pattern exactly, so those suppressions will not be misread as
  provider failures.
- **In-root.** All seven `target_paths` are under `scripts/` and
  `platform_tests/`; root-boundary clean; no `applications/Agent_Red/` or
  external repository path in scope.

## Positive Confirmations

- First-line status token `REVISED` correct on `-003`; Project Authorization /
  Project / Work Item lines present; `target_paths` inline-JSON parses;
  `implementation_scope: source`; `kb_mutation_in_scope: false` consistent with
  source-only scope.
- Owner Decisions / Input section present and substantive (carries
  `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` and the active PAUTH); no
  new owner decision is required because Prime adopted the LO-preferred design
  (the residual interactive-exposure limitation that `-002` N3 flagged for
  possible AUQ is eliminated by making the impl-auth begin path the primary
  guard, since that choke point sees interactive and headless mutations alike).
- Recommended commit type `fix` is consistent with the diff shape (repair of an
  unguarded coordination path plus regression tests; no net-new capability
  surface).

## Implementation-Phase Guidance (advisory; non-blocking — for the report/verification)

These do not gate the GO; they are notes the implementation report and its
verification should address so the post-impl VERIFIED review is clean:

1. **Preserve the two distinct failure axes.** `cross_claim_path_collision_reason`
   is deliberately fail-*soft* on registry/IO read errors (returns None → allow)
   so a lookup failure never converts an authorized edit into a spurious block.
   The N4 predicate is fail-*closed* on glob-vs-glob *ambiguity* (treat as
   overlap unless provably disjoint). These are different axes and must both be
   preserved — do not let the new glob-ambiguity fail-closed leak into the
   registry-read path and reintroduce spurious blocks.
2. **Reuse, don't fork, the overlap predicate.** The begin-time guard should
   call the existing `cross_claim_path_collision_reason` (extended for the
   glob-vs-glob case) rather than introduce a second, drifting overlap
   implementation. A single predicate keeps the dispatch-side optimization and
   the impl-auth-start choke point byte-consistent.
3. **Add a same-session non-collision test.** The existing helper intentionally
   skips same-session holders (legitimate multi-thread). The new begin-time and
   dispatcher paths must keep that exemption; include a regression asserting a
   single session working two overlapping threads is NOT self-suppressed.
4. **Throughput regression witness.** Because conservative glob-vs-glob
   fail-closed can over-serialize, include a test proving disjoint concrete
   `target_paths` still fan out to the effective cap (the WI-4996 own paths are
   all concrete, so the immediate blast radius is small, but the predicate is
   general).

## Prior Deliberations

- Semantic DA search returned no records across three queries this session
  (target_paths overlap serialization dispatch; implementation authorization
  begin cross-claim collision WI-4471; WI-4996 / WI-4995 / WI-4992 shared-file
  entanglement). Direct bridge prior art governs:
  - `bridge/gtkb-wi4995-document-lease-held-health-004.md` — the parent NO-GO
    (authored by this reviewer, LO-B, 2026-07-03) whose N1 documents the
    WI-4995 to WI-4992 shared-file entanglement and records it as a standing
    backlog item for PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION. WI-4996 is that
    item.
  - `bridge/gtkb-wi4996-target-path-dispatch-serialization-002.md` — this
    reviewer's prior NO-GO; `-003` addresses its N1–N5.
  - `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` — owner directive
    governing the dispatcher-modernization program.

## Owner Decisions / Input

- No new owner decision is required for this GO; it is standing Loyal
  Opposition proposal-review authority. The governing owner directive remains
  `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL`; the active
  `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4996-IMPLEMENTATION-PROPOSAL-FILING`
  covers WI-4996 implementation scope.

## Recommended Disposition

Prime Builder: proceed to implementation within the declared `target_paths`.
After GO, run `python scripts/implementation_authorization.py begin --bridge-id
gtkb-wi4996-target-path-dispatch-serialization`, implement the begin-time
overlap guard (primary), the impl-start-gate glob-overlap coverage (backstop),
and the dispatcher-side suppression optimization, then file a post-implementation
report carrying the Specification-Derived Verification Plan forward with observed
pytest, `ruff check`, and `ruff format --check` results for all changed Python
files. The advisory implementation-phase notes above should be visible in the
report so the post-impl VERIFIED review can confirm them.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
