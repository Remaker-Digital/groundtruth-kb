NEW

bridge_kind: governance_review
Document: gtkb-role-status-orthogonality-dispatch-scoping
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-31 UTC
Session: S378
Recommended commit type: docs
Self-check preflights: applicability passed (no missing specs); clause preflight passed (0 evidence gaps, 0 blocking gaps). Codex MUST rerun both against the live operative file and include the regenerated sections in any verdict.

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S378-role-status-orthogonality-dispatch-scoping
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

# Role/Status Orthogonality Dispatch Model — Umbrella Scoping Proposal

## Source / Owner Directive

This proposal is filed in response to the owner directive captured in session
S378 (2026-05-31) and archived as `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-
DISPATCH`. The owner directive supersedes the single-prime-builder invariant
established by `WI-3341` (VERIFIED) and `DELIB-2079/2080/2081`, adopting a
model in which role assignment and dispatch eligibility become orthogonal
axes: multiple harnesses may share a role; only the single status=active
harness per role is auto-dispatch-eligible. The session-stated role override
via the canonical init keyword `::init gtkb (pb|lo)` continues to take
precedence for in-session surfaces per `GOV-SESSION-ROLE-AUTHORITY-001` and
`DCL-SESSION-ROLE-RESOLUTION-001`.

## Proposal Kind

This is a **scoping (umbrella) governance-review proposal**. It does not
authorize any source mutation. It frames the work for Loyal Opposition review
and decomposes it into reviewable slices. Each slice will be a separate
NEW/REVISED proposal with its own `target_paths`, implementation
authorization, and verification plan. This scoping proposal's `target_paths`
are limited to the bridge file itself and `bridge/INDEX.md`.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions /
Input Section Gate". This proposal depends on owner approval and cites the
AUQ-only enforcement rule.

1. **Owner directive (S378 prompt, 2026-05-31)** — full text of the model
   shift + three example cases (happy path, Claude Code suspended, role
   swap) captured verbatim in `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-
   DISPATCH`. The directive was preceded by a Prime Builder investigation
   report on Antigravity-as-default-PB blockers (this session's transcript).

2. **Owner AskUserQuestion answer (2026-05-31, S378)** — Question: "How
   should I proceed with the owner-directed model-shift proposal (role/
   status orthogonality with single-ACTIVE-per-role dispatch)?" Owner
   selected option A: "File umbrella project (Recommended) — Capture the
   owner directive as a DELIB, then file a scoping bridge proposal that
   decomposes the work into reviewable slices. Slice 1 is the resolver
   change (status-filtered dispatch), which resolves the current AXIS 1 PB
   dispatch break as a side effect. Subsequent slices handle ADR/GOV/SPEC/
   DCL updates, protected-narrative rewrites (operating-role.md, acting-
   prime-builder.md, canonical-terminology.md, AGENTS.md), packet generator
   regeneration, and doctor-check updates."

The AUQ answer authorizes (a) the DELIB capture (already done) and (b)
filing of this scoping proposal. Per-slice implementation work requires
per-slice proposals and per-slice owner approval evidence as the slices
land.

Downstream owner decisions deferred to future AUQs (not asked in this
proposal):

- Status taxonomy granularity (active / inactive / suspended vs adding
  retired/decommissioned states per the WI-3339 four-state lifecycle FSM).
- PB→LO dispatch substrate when active PB has no hook surface (the
  Antigravity-as-active-PB case): accept one-directional AXIS 1, add a new
  substrate, or extend single-harness-dispatcher semantics.
- ADR shape for Slice 2: v2 of `ADR-SINGLE-HARNESS-OPERATING-MODE-001` vs
  separate successor ADR.

## Specification Links

Governing specifications cited by this proposal. Per `.claude/rules/file-
bridge-protocol.md` § "Mandatory Specification Linkage Gate".

- `GOV-HARNESS-ROLE-PORTABILITY-001` — to be updated in Slice 3 (single-
  assignment language removed).
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — to be updated in Slice 3.
- `GOV-ACTING-PRIME-BUILDER-001` — unchanged (READ-accepted compatibility/
  provenance contract preserved).
- `GOV-SESSION-ROLE-AUTHORITY-001` — unchanged (durable vs session-stated
  authority split preserved; this proposal does not touch session-role
  resolution).
- `GOV-ARTIFACT-APPROVAL-001` — governs per-artifact rewrites in Slice 4
  (formal-artifact-approval packets per protected-narrative file).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge protocol used here.
- `GOV-STANDING-BACKLOG-001` — governs backlog hygiene actions in Slice 7
  (WI-3341 supersession marking).
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — governs the spec captures (new
  ADR, DCL in Slice 2).
- `WI-3341` (VERIFIED) — "Role portability and single-prime-builder
  invariant enforcement"; this proposal supersedes the "exactly one prime-
  builder at all times" + "atomically demotes the others" clauses.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — single-PB framing superseded
  in part by Slice 2's new ADR (or v2 of this ADR).
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` § Coexistence — substrate-
  selection language becomes status-aware in Slice 2.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — applicability check
  becomes status-aware in Slice 2/Slice 6.
- `DCL-SESSION-ROLE-RESOLUTION-001` — unchanged (deterministic resolution
  table for session-stated override preserved).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — unchanged.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 — relevant to the downstream
  substrate decision (Antigravity has no hook surface; fallback substrate
  decisions intersect with this ADR).
- `PB-ARTIFACT-APPROVAL-001` — governs per-artifact rewrites.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — governs per-artifact rewrites.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this scoping
  proposal's compliance (linkage shown above; this proposal is governance-
  review-kind and does not authorize implementation).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — per-slice
  verification compliance (per-slice proposals will carry their own
  spec-to-test mappings; this scoping proposal's verification is
  structural, see § Spec-Derived Verification Plan).
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — governs cross-harness enforcement
  of the bridge protocol.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal
  self-declares `bridge_kind: governance_review` for exemption from the
  project-linkage requirement (scoping/umbrella artifact, not
  implementation-targeting).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking. All artifacts
  produced or modified by this proposal reside in-root under `E:\GT-KB`.
  This scoping proposal's `target_paths` (the bridge file and
  `bridge/INDEX.md`) are in-root. Slice 6 modifies
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py` which is in-root.
  All per-slice proposals will declare in-root `target_paths` matching
  this placement contract; no slice authorizes any out-of-root file
  mutation. The external-harness-executable resolution exception (per
  `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`) does not apply
  to this proposal because no slice invokes an out-of-root harness
  executable as part of its authorized work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory. This proposal
  treats the model shift as a durable multi-artifact landing (DELIB
  already captured; ADR + DCL + GOV updates + protected-narrative
  rewrites + doctor-check updates planned across the slices), not a
  single-shot code change. The artifact-oriented stance applies.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory. The proposal
  references superseded (WI-3341 clauses), unchanged (preserved specs),
  candidate (new ADR / DCL not yet drafted), and deferred (downstream
  substrate decision) lifecycle states; each is named with the
  appropriate transition language.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory. The model shift is
  reified across multiple formal-artifact classes (ADR, DCL, GOV, DELIB,
  protected narrative) consistent with the artifact-oriented governance
  default interpretation stance.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` § "Prime Builder — Before
Proposing". Searches conducted across the Deliberation Archive for prior
reviews on single-prime-builder invariant, role portability, Antigravity
integration, and harness lifecycle FSM. Cited entries:

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — the owner directive
  captured in this session that authorizes this proposal (the source).
- `DELIB-2079` — Antigravity Integration project design (3-harness model;
  established the single-PB invariant the owner now supersedes).
- `DELIB-2080` — Single-PB invariant + role portability amendment.
  Superseded in part.
- `DELIB-2081` — Historical WI-3359 auto-drain authorization (superseded
  by the 2026-05-19 owner removal directive).
- `DELIB-S324-OM-DELTA-0003-CHOICE` — Operating-model terminology
  (application/project/platform/hosted-application); informs the
  dispatch-language updates downstream.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` — Codex hook
  parity refresh; informs `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 which
  is relevant to the downstream substrate decision (Antigravity no-hooks
  case).
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` — Lifecycle-independence
  framing; informs status taxonomy (active/inactive/suspended distinction).
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` — Cross-harness
  exec resolution exception; informs Slice 1 resolver behavior when an
  active harness's invocation_surfaces points outside the project root.
- `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` —
  Active-session suppression contract; the existing active-session-lock
  mechanism in `check_counterpart_active()` interoperates with the new
  status filter (active session locks are session-scoped; status is
  harness-scoped — they are orthogonal axes).


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1514` — seed=search; bridge_thread; Loyal Opposition Review - Canonical Init-Keyword Syntax REVISED-1
- DA: `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` — seed=search; owner_conversation; Prime Builder / Loyal Opposition Role-Definition Assessment (S310)
- DA: `DELIB-2251` — seed=search; bridge_thread; Loyal Opposition Verdict - Headless Gemini LO Dispatch Verification - 004
- DA: `DELIB-1512` — seed=search; bridge_thread; Loyal Opposition Review - Canonical Init-Keyword Syntax REVISED-3
- DA: `DELIB-1004` — seed=search; bridge_thread; GTKB-ISOLATION-015 - Loyal Opposition Review

## Requirement Sufficiency

**New or revised requirement required before implementation.**

Rationale: This scoping proposal authorizes only governance-layer work that
*creates* the new specifications (ADR, GOV updates, SPEC extensions, DCL).
The slices that follow are conditional on those specifications existing.
Implementation of the resolver code change (Slice 1) is conditional on the
ADR + DCL landing in Slice 2 (or being inserted with provisional approval
before Slice 1 implementation), so the resolver code references the new
specs in `change_reason` and packet citations.

## target_paths

This scoping proposal authorizes only:

- `bridge/gtkb-role-status-orthogonality-dispatch-scoping-001.md` (this file)
- `bridge/INDEX.md` (entry insertion)

No source files. No test files. No rule files. No spec inserts. No
project-authorization record creation. Per-slice proposals will declare
their own `target_paths` matching their authorization scope.

## Spec-Derived Verification Plan (for this scoping proposal)

Codex verification of this scoping proposal is structural — there is no
behavior to test directly. Verification checks:

1. **Specification Links accuracy** — Cross-check the supersession claims
   against live artifacts: WI-3341 in MemBase (`gt spec get WI-3341` or
   equivalent), `ADR-SINGLE-HARNESS-OPERATING-MODE-001` text, DELIB-2079/
   2080/2081 content. Confirm the cited specs exist and the supersession
   claims are accurate.

2. **Prior Deliberations substantiveness** — Confirm the section enumerates
   DELIB-IDs (not placeholders), confirm DELIB-S378-ROLE-STATUS-
   ORTHOGONALITY-DISPATCH is referenced as the source-authorizing entry.

3. **Owner Decisions / Input section presence and substance** — Confirm
   the section enumerates the AUQ answer authorizing this scope. Confirm
   the deferred-AUQ list is present and substantive.

4. **Requirement Sufficiency declaration matches scope** — Confirm "New or
   revised requirement required before implementation" matches the
   proposal's no-source-mutation authorization.

5. **Slice decomposition coherence** — Confirm each of the 7 slices has a
   clearly stated goal, target files, and dependency relationship. Confirm
   no slice silently overlaps source files with another slice's authorized
   scope. Confirm the Slice 1 (resolver change) is sequenced before
   downstream slices that rely on the new dispatch semantic.

6. **Applicability preflight** — Codex MUST run `python scripts/bridge_
   applicability_preflight.py --bridge-id gtkb-role-status-orthogonality-
   dispatch-scoping` and include the resulting `Applicability Preflight`
   section in any verdict file. `missing_required_specs: []` is the
   expected result given the linkage above.

7. **Clause applicability preflight** — Codex MUST run `python scripts/
   adr_dcl_clause_preflight.py --bridge-id gtkb-role-status-orthogonality-
   dispatch-scoping` (without `--report-only`) and include the resulting
   `Clause Applicability` section. Treat exit 5 as NO-GO blocker absent an
   explicit owner-waiver line.

Per-slice spec-derived verification plans land with per-slice proposals.

## Project Decomposition (Proposed Slices)

### Slice 1 — Resolver + Attribution (code)

**Goal**: Adopt the single-ACTIVE-per-role invariant in dispatch resolution.
Restore AXIS 1 PB dispatch (currently broken by the dual-PB role-map state
B=PB + C=PB as of 2026-05-31).

**Files**:

- `scripts/cross_harness_bridge_trigger.py` — `_resolve_dispatch_target`
  (lines 920-1007): match by `role` AND `status == "active"`; fail closed
  only on multiple-ACTIVE-match; emit structured audit entry on zero-
  ACTIVE-match (new `last_result = "no_active_target_for_role"`).
  `_is_single_harness_topology` (lines 1181-1209): apply status-awareness
  (single-harness mode now requires the harness to be active for both
  roles) or no change if subsumed by Slice 2 design.
- `scripts/_kb_attribution.py` — replace "Single Prime Builder slot in
  `harness-state/role-assignments.json`" comments + logic with "the active
  Prime Builder harness" semantics consistent with the new invariant.

**Tests**:

- Unit tests for `_resolve_dispatch_target` with: (a) multiple-ACTIVE-match
  raises `ValueError` with informative message; (b) zero-ACTIVE-match
  returns sentinel and emits structured audit (no exception); (c) exactly-
  one-ACTIVE-match resolves correctly; (d) legacy "no status field"
  records treated as active (backward-compat) OR (e) explicit fail-closed
  on missing status field (owner AUQ decision during Slice 1).
- Existing tests for `_resolve_dispatch_target` updated to include status
  field in fixtures.
- Regression test: dual-PB record with one active and one inactive
  resolves to the active.

**Dependency**: Slice 2 ADR + DCL must exist before Slice 1 lands so the
resolver code references the new specs in `change_reason` and packet
citations.

**Side effect**: When this slice lands, the current dual-PB role-map state
(B=active/PB + C=PB/status=active per `harness-state/harness-registry.json:
73-77`) becomes either a coherent dual-PB configuration (one active, one
not) or a Slice 7 reconciliation target (both active = configuration error
that doctor will FAIL). Owner-directed status assignment for C is owner-
decision territory; Slice 1 does NOT itself touch role-assignments.json
content.

### Slice 2 — ADR + DCL (governance artifacts)

**Goal**: Codify role/status orthogonality + single-ACTIVE-per-role
invariant + status taxonomy.

**Artifacts**:

- New ADR (`ADR-ROLE-STATUS-ORTHOGONALITY-001`) or v2 of `ADR-SINGLE-
  HARNESS-OPERATING-MODE-001` — owner AUQ during slice.
- New DCL (`DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`).

**Owner AUQ during slice**:

- Status taxonomy values (the owner-named `{active, inactive, suspended}`
  plus possibly retired/decommissioned from the WI-3339 four-state
  lifecycle FSM).
- ADR v2 vs successor ADR shape.

### Slice 3 — GOV Updates

**Goal**: Update governance specs to remove single-assignment language.

**Artifacts**:

- `GOV-HARNESS-ROLE-PORTABILITY-001` v2.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v2.

Each needs a per-artifact formal-artifact-approval packet.

### Slice 4 — Protected-Narrative Rewrites

**Goal**: Update rule files to reflect the new model. Formal-artifact-
approval gated per `GOV-ARTIFACT-APPROVAL-001` + narrative-artifact-
approval-gate.

**Files**:

- `.claude/rules/operating-role.md` — § Role Assignment Rules (the demote-
  all-others rule) + § Role Set Schema (the "singleton role sets are the
  multi-harness norm" language).
- `.claude/rules/acting-prime-builder.md` — compatibility/provenance
  language preserved; references to the role-uniqueness implication
  updated.
- `.claude/rules/canonical-terminology.md` — § single-harness operating
  mode + § role set + § operating role entries (the "switching a harness
  to Prime Builder demotes all other recorded harnesses" line).
- `AGENTS.md` — § Durable Operating Role Assignment (the self-correction
  logic + role-uniqueness implications).

### Slice 5 — Packet Generator Regeneration

**Goal**: Regenerate narrative and spec packets that embedded the
superseded language.

**Files**:

- `scripts/_build_narrative_packet_operating_role_md.py` — embeds the
  superseded demote-all-others text.
- `scripts/_build_spec_single_harness_bridge_dispatcher_packet.py` —
  embeds "harness ID whose role-set has cardinality >= 2" framing.

### Slice 6 — Doctor Check Updates

**Goal**: Update doctor checks to enforce single-ACTIVE-per-role invariant.

**Files**:

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — `_check_role_set
  _topology_consistency` (status-aware), `_check_single_harness_dispatcher
  _when_required` (status-aware applicability), plus a new `_check_single
  _active_per_role` check (FAIL on 2+ active per role, WARN on 0 active
  per role).

### Slice 7 — Backlog Hygiene & Reconciliation

**Goal**: Mark superseded artifacts, re-scope blocked WIs, reconcile
config drift.

**Actions**:

- Mark `WI-3341` (VERIFIED) as superseded for the "exactly one prime-
  builder at all times" and "atomically demotes the others" clauses (
  per-artifact owner approval).
- Re-scope `WI-3343` ("ADR-SINGLE-HARNESS-OPERATING-MODE-001 extension")
  to align with Slice 2's ADR shape (if Slice 2 picks v2, WI-3343 may roll
  into Slice 2; if Slice 2 picks separate successor, WI-3343 may be
  retired).
- Loosen `WI-3349` (end-to-end Gemini CLI headless LO-review dispatch
  verification) scope guard (per the 2026-05-27 change-log entry in
  `memory/antigravity-integration-status.md` §7, WI-3349 is currently
  scoped "substrate-only: no harness C activation, role assignment, role-
  topology change, dispatcher source change, or production routing
  change"; under the new model these guards become less restrictive).
- Reconcile `.antigravity/config.toml` (`status = "suspended"`, `role = []`)
  vs `harness-state/harness-registry.json` (`status = "active"`, `role =
  ["prime-builder"]`) status drift via owner AUQ during slice.
- Backlog implications for `PROJECT-ANTIGRAVITY-INTEGRATION` tracker
  (`memory/antigravity-integration-status.md`).

## Risk & Rollback

This scoping proposal carries no implementation risk: it authorizes only
the bridge file write + INDEX.md entry insertion. Rollback in the bridge-
protocol sense is "supersede in the next version" (the file-bridge protocol
is append-only).

Per-slice risk and rollback land with per-slice proposals.

## Out of Scope

- Source code mutation, test mutation, hook mutation, configuration
  mutation, deployment, KB mutation other than the bridge files (per
  `bridge/INDEX.md` insertion). All such work lands in per-slice proposals.
- The PB→LO dispatch substrate decision when active PB has no hook surface
  (Antigravity case). This question is downstream of this scoping proposal
  and will be raised in a separate AskUserQuestion when the project
  reaches the substrate-decision phase.
- AGENTS.md File Safety Contract changes for harness C beyond what the
  protected-narrative rewrite in Slice 4 addresses. The 2026-05-31 owner
  reversal is already in AGENTS.md text (lines 291-292); reconciliation
  with `.antigravity/config.toml` is part of Slice 7.
- DELIB-2079/2080/2081 retroactive amendment beyond the supersession
  citation in DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH (DA is
  append-only; supersession is a forward citation, not a back-edit).
