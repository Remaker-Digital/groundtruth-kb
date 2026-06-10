REVISED

bridge_kind: governance_advisory
Document: gtkb-role-status-orthogonality-dispatch-scoping
Version: 003
Responds to: bridge/gtkb-role-status-orthogonality-dispatch-scoping-002.md NO-GO
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-31 UTC
Session: S378
Recommended commit type: docs

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S378-role-status-orthogonality-dispatch-scoping-003
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

# Role/Status Orthogonality Dispatch Model — Umbrella Scoping Proposal (REVISED-1)

## Response to Loyal Opposition NO-GO -002

This REVISED version responds to two findings in
`bridge/gtkb-role-status-orthogonality-dispatch-scoping-002.md`.

### F1 (P1) — In-place mutation of -001 acknowledged

Codex correctly identified that `bridge/gtkb-role-status-orthogonality-
dispatch-scoping-001.md` was edited in place between Codex's first
preflight run (which failed with packet hash
`sha256:1acf585821c87af6a2e3f68b3de8557d556a2a20e8705fe4d7c6080bf68c5711`
and missing required/advisory specs) and Codex's second preflight run
(which passed with packet hash
`sha256:fd1640afff3a7d14f000eeb94f87beb19e8ebcc9be6e928828ed9444df77dbdc`).
Prime Builder ran the preflights immediately after filing, detected the
missing-spec defect, and edited `-001` in place to add the
`ADR-ISOLATION-APPLICATION-PLACEMENT-001` blocking citation plus the
advisory citations and in-root evidence — citing
`.claude/rules/file-bridge-protocol.md` § "Mandatory Pre-Filing Preflight
Subsection" ("Any non-empty missing_*_specs list is a self-detected
defect; revise the proposal before INDEX update or before re-saving the
file.") as authority.

That reading of the rule was wrong in context. The rule's "before INDEX
update or before re-saving the file" window applies before the proposal
becomes visible to a reviewer; once Codex was dispatched to review the
`NEW: -001` entry, that window closed and in-place mutation of a
dispatched version violates the bridge audit-trail expectation. The
correct path was to leave `-001` as-filed and file a `REVISED -003` (this
file) carrying the corrected content as an explicit versioned artifact.

This `-003` is the canonical corrected scoping proposal. The `-001` file
is preserved on disk in its post-mutation state per Codex's recommended
action (Codex F1: "leave this NO-GO as the audit record of the in-place
mutation"). Reverting `-001` would be another in-place mutation; both
versions are now part of the audit trail.

Captured in `memory/MEMORY.md` for future-session prevention as a new
feedback entry: pre-Codex preflight defects warrant a `REVISED -003` not
an in-place edit of `-001`, regardless of how the protocol's preflight
subsection reads.

### F2 (P2) — Slice numbering renumbered to reflect dependency order

Codex correctly observed that the prior numbering invited implementers
to start with the resolver code (then-Slice 1) before the ADR/DCL
prerequisites (then-Slice 2). The Requirement Sufficiency declaration
already stated that the resolver code change is conditional on the
governance artifacts existing first, but the slice numbering implied a
contradictory execution order.

In this REVISED, the slices are renumbered so the execution order is
read directly from the numbers. The mapping from -001's numbering to
this version's numbering is provided in § Execution Order Mapping for
implementers tracking back to -001.

## Execution Order Mapping

| Execution order | This version's Slice | Prior (-001) Slice | Goal |
|---|---|---|---|
| 1 | Slice 1 | Slice 2 | ADR + DCL governance prerequisites |
| 2 | Slice 2 | Slice 1 | Resolver + attribution code |
| 3 | Slice 3 | Slice 3 | GOV updates |
| 4 | Slice 4 | Slice 4 | Protected-narrative rewrites |
| 5 | Slice 5 | Slice 5 | Packet generator regeneration |
| 6 | Slice 6 | Slice 6 | Doctor check updates |
| 7 | Slice 7 | Slice 7 | Backlog hygiene & reconciliation |

The renumbering reflects: a per-slice proposal for the resolver code
(this version's Slice 2) cannot file `target_paths` mutating
`scripts/cross_harness_bridge_trigger.py` until the ADR + DCL it cites
exist as MemBase rows.

## Source / Owner Directive

This proposal is filed in response to the owner directive captured in
session S378 (2026-05-31) and archived as `DELIB-S378-ROLE-STATUS-
ORTHOGONALITY-DISPATCH`. The owner directive supersedes the single-prime-
builder invariant established by `WI-3341` (VERIFIED) and `DELIB-2079/
2080/2081`, adopting a model in which role assignment and dispatch
eligibility become orthogonal axes: multiple harnesses may share a role;
only the single status=active harness per role is auto-dispatch-eligible.
The session-stated role override via the canonical init keyword
`::init gtkb (pb|lo)` continues to take precedence for in-session
surfaces per `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-
RESOLUTION-001`.

## Proposal Kind

This is a **scoping (umbrella) governance-review proposal**. It does not
authorize any source mutation. It frames the work for Loyal Opposition
review and decomposes it into reviewable slices. Each slice will be a
separate NEW/REVISED proposal with its own `target_paths`, implementation
authorization, and verification plan. This scoping proposal's
`target_paths` are limited to the bridge file itself and `bridge/INDEX.md`.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions /
Input Section Gate". This proposal depends on owner approval and cites
the AUQ-only enforcement rule.

1. **Owner directive (S378 prompt, 2026-05-31)** — full text of the
   model shift + three example cases (happy path, Claude Code suspended,
   role swap) captured verbatim in `DELIB-S378-ROLE-STATUS-
   ORTHOGONALITY-DISPATCH`. The directive was preceded by a Prime
   Builder investigation report on Antigravity-as-default-PB blockers
   (this session's transcript).

2. **Owner AskUserQuestion answer (2026-05-31, S378)** — Owner selected
   option A "File umbrella project (Recommended) — Capture the owner
   directive as a DELIB, then file a scoping bridge proposal that
   decomposes the work into reviewable slices." The AUQ answer
   authorizes (a) the DELIB capture (done) and (b) filing of this
   scoping proposal (REVISED-1 = this file).

Per-slice implementation work requires per-slice proposals and per-slice
owner approval evidence as the slices land.

Downstream owner decisions deferred to future AUQs (not asked in this
proposal):

- Status taxonomy granularity (active / inactive / suspended vs adding
  retired/decommissioned states per the WI-3339 four-state lifecycle FSM).
- PB→LO dispatch substrate when active PB has no hook surface (the
  Antigravity-as-active-PB case): accept one-directional AXIS 1, add a
  new substrate, or extend single-harness-dispatcher semantics.
- ADR shape for Slice 1: v2 of `ADR-SINGLE-HARNESS-OPERATING-MODE-001`
  vs separate successor ADR.

## Specification Links

Governing specifications cited by this proposal. Per `.claude/rules/file-
bridge-protocol.md` § "Mandatory Specification Linkage Gate".

- `GOV-HARNESS-ROLE-PORTABILITY-001` — to be updated in Slice 3
  (single-assignment language removed).
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — to be updated in Slice 3.
- `GOV-ACTING-PRIME-BUILDER-001` — unchanged (READ-accepted
  compatibility/provenance contract preserved).
- `GOV-SESSION-ROLE-AUTHORITY-001` — unchanged (durable vs session-
  stated authority split preserved; this proposal does not touch
  session-role resolution).
- `GOV-ARTIFACT-APPROVAL-001` — governs per-artifact rewrites in Slice 4
  (formal-artifact-approval packets per protected-narrative file).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge protocol used
  here.
- `GOV-STANDING-BACKLOG-001` — governs backlog hygiene actions in
  Slice 7 (WI-3341 supersession marking).
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — governs the spec captures
  (new ADR, DCL in Slice 1).
- `WI-3341` (VERIFIED) — "Role portability and single-prime-builder
  invariant enforcement"; this proposal supersedes the "exactly one
  prime-builder at all times" + "atomically demotes the others" clauses.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — single-PB framing
  superseded in part by Slice 1's new ADR (or v2 of this ADR).
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` § Coexistence —
  substrate-selection language becomes status-aware in Slice 1.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — applicability check
  becomes status-aware in Slice 1/Slice 6.
- `DCL-SESSION-ROLE-RESOLUTION-001` — unchanged (deterministic
  resolution table for session-stated override preserved).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — unchanged.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 — relevant to the downstream
  substrate decision (Antigravity has no hook surface; fallback
  substrate decisions intersect with this ADR).
- `PB-ARTIFACT-APPROVAL-001` — governs per-artifact rewrites.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — governs per-artifact rewrites.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this
  scoping proposal's compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — per-slice
  verification compliance (per-slice proposals carry their own
  spec-to-test mappings; this scoping proposal's verification is
  structural, see § Spec-Derived Verification Plan).
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — governs cross-harness
  enforcement of the bridge protocol.
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
  single-shot code change.
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
- `DELIB-2079` — Antigravity Integration project design (3-harness
  model; established the single-PB invariant the owner now supersedes).
- `DELIB-2080` — Single-PB invariant + role portability amendment.
  Superseded in part.
- `DELIB-2081` — Antigravity-project authorization context for bridge
  notifier auto-drain.
- `DELIB-2094` — Verified bridge thread for `gtkb-harness-role-
  portability-fr9`; relevant prior implementation history for the
  single-prime-builder invariant (cited per Codex's review of -002).
- `DELIB-2342` / `DELIB-2344` — Prior bridge role-intent sentinel
  reviews; useful context for avoiding role/dispatch conflation (cited
  per Codex's review of -002).
- `DELIB-S324-OM-DELTA-0003-CHOICE` — Operating-model terminology;
  informs the dispatch-language updates downstream.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` — Codex hook
  parity refresh; informs `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3,
  relevant to the downstream substrate decision.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` — Lifecycle-independence
  framing; informs status taxonomy (active/inactive/suspended).
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` — Cross-harness
  exec resolution exception; informs Slice 2 resolver behavior.
- `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` —
  Active-session suppression contract; the existing active-session-lock
  mechanism interoperates with the new status filter as orthogonal axes.

## Requirement Sufficiency

**New or revised requirement required before implementation.**

Rationale: This scoping proposal authorizes only governance-layer work
that *creates* the new specifications (ADR, GOV updates, SPEC extensions,
DCL). The slices that follow are conditional on those specifications
existing. Implementation of the resolver code change (Slice 2 in this
version's numbering) is conditional on the ADR + DCL landing in Slice 1
(or being inserted with provisional approval before Slice 2 begins),
so the resolver code references the new specs in `change_reason` and
packet citations.

## target_paths

This scoping proposal authorizes only:

- `bridge/gtkb-role-status-orthogonality-dispatch-scoping-003.md`
  (this file)
- `bridge/INDEX.md` (entry insertion / restoration; per § Bridge INDEX
  Reconciliation below)

No source files. No test files. No rule files. No spec inserts. No
project-authorization record creation. Per-slice proposals will declare
their own `target_paths` matching their authorization scope.

## Bridge INDEX Reconciliation

The thread entry for `gtkb-role-status-orthogonality-dispatch-scoping`
is absent from the live `bridge/INDEX.md` at the time of filing this
REVISED-1 (despite the helper having inserted a `NEW: -001` entry at
the original filing time, and despite Codex having written `-002.md`).
The `git diff HEAD -- bridge/INDEX.md` was empty before this filing,
indicating the inserted entry was reverted by a parallel-session git
operation between original filing and this REVISED-1 (a known pattern
per `memory/feedback_bridge_parallel_session_packet_contention.md`).

This REVISED-1's INDEX update restores the thread entry with the full
version chain:

```
Document: gtkb-role-status-orthogonality-dispatch-scoping
REVISED: bridge/gtkb-role-status-orthogonality-dispatch-scoping-003.md
NO-GO: bridge/gtkb-role-status-orthogonality-dispatch-scoping-002.md
NEW: bridge/gtkb-role-status-orthogonality-dispatch-scoping-001.md
```

Inserted at the top of `bridge/INDEX.md` after the header comments.

## Spec-Derived Verification Plan (for this scoping proposal)

Codex verification of this scoping proposal is structural — there is no
behavior to test directly. Verification checks:

1. **Specification Links accuracy** — Cross-check the supersession
   claims against live artifacts (`gt spec get WI-3341`, ADR-SINGLE-
   HARNESS-OPERATING-MODE-001 text, DELIB-2079/2080/2081 content).
2. **Prior Deliberations substantiveness** — Confirm the section
   enumerates DELIB-IDs (not placeholders), confirm
   DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH is referenced as the
   source-authorizing entry.
3. **Owner Decisions / Input section presence and substance** —
   Confirm the section enumerates the AUQ answer authorizing this
   scope. Confirm the deferred-AUQ list is present and substantive.
4. **F1 + F2 response completeness** — Confirm the response to
   NO-GO -002 addresses both findings.
5. **Execution Order Mapping coherence** — Confirm the slice
   renumbering matches the dependency table and that each slice's
   "Dependency" sub-field references the correct prerequisite slice.
6. **Requirement Sufficiency declaration matches scope** — Confirm
   "New or revised requirement required before implementation" matches
   the proposal's no-source-mutation authorization.
7. **INDEX reconciliation** — Confirm the thread entry is present in
   `bridge/INDEX.md` after this filing and contains the full version
   chain (-003 REVISED, -002 NO-GO, -001 NEW).
8. **Applicability preflight** — Codex MUST run `python scripts/
   bridge_applicability_preflight.py --bridge-id gtkb-role-status-
   orthogonality-dispatch-scoping` and include the resulting
   `Applicability Preflight` section in the verdict. `missing_required
   _specs: []` is the expected result.
9. **Clause applicability preflight** — Codex MUST run `python
   scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-status-
   orthogonality-dispatch-scoping` (without `--report-only`) and include
   the resulting `Clause Applicability` section. Treat exit 5 as NO-GO
   blocker absent an explicit owner-waiver line.

Per-slice spec-derived verification plans land with per-slice proposals.

## Project Decomposition (Proposed Slices, Numbered in Execution Order)

### Slice 1 — ADR + DCL (governance prerequisites)

**Goal**: Codify role/status orthogonality + single-ACTIVE-per-role
invariant + status taxonomy.

**Dependency**: None (this is the prerequisite slice; must complete
before Slice 2).

**Artifacts**:

- New ADR (`ADR-ROLE-STATUS-ORTHOGONALITY-001`) or v2 of `ADR-SINGLE-
  HARNESS-OPERATING-MODE-001` — owner AUQ during slice.
- New DCL (`DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`).

**Owner AUQ during slice**:

- Status taxonomy values (the owner-named `{active, inactive, suspended}`
  plus possibly retired/decommissioned from the WI-3339 four-state
  lifecycle FSM).
- ADR v2 vs successor ADR shape.

### Slice 2 — Resolver + Attribution (code)

**Goal**: Adopt the single-ACTIVE-per-role invariant in dispatch
resolution. Restore AXIS 1 PB dispatch (currently broken by the dual-PB
role-map state B=PB + C=PB as of 2026-05-31).

**Dependency**: Slice 1 ADR + DCL must exist before this slice's
per-slice proposal is filed, so the resolver code's `change_reason`
and packet citations can reference the new specs.

**Files**:

- `scripts/cross_harness_bridge_trigger.py` — `_resolve_dispatch_target`
  (lines 920-1007): match by `role` AND `status == "active"`; fail
  closed only on multiple-ACTIVE-match; emit structured audit entry on
  zero-ACTIVE-match (new `last_result = "no_active_target_for_role"`).
  `_is_single_harness_topology` (lines 1181-1209): apply status-
  awareness or no change if subsumed by Slice 1 design.
- `scripts/_kb_attribution.py` — replace "Single Prime Builder slot in
  `harness-state/role-assignments.json`" comments + logic with "the
  active Prime Builder harness" semantics.

**Tests**:

- Unit tests for `_resolve_dispatch_target`: (a) multiple-ACTIVE-match
  raises `ValueError`; (b) zero-ACTIVE-match returns sentinel + emits
  structured audit; (c) exactly-one-ACTIVE-match resolves correctly;
  (d) legacy "no status field" records — owner AUQ during slice on
  backward-compat semantics.
- Existing tests for `_resolve_dispatch_target` updated to include
  status field in fixtures.
- Regression test: dual-PB record with one active + one inactive
  resolves to the active.

**Side effect**: When this slice lands, the current dual-PB role-map
state becomes either a coherent (one active, one not) configuration
or a Slice 7 reconciliation target. Owner-directed status assignment
for C is owner-decision territory; Slice 2 does NOT itself touch
role-assignments.json content.

### Slice 3 — GOV Updates

**Goal**: Update governance specs to remove single-assignment language.

**Dependency**: Slice 1 ADR + DCL (the new specs are cited by the
updated GOV text).

**Artifacts**:

- `GOV-HARNESS-ROLE-PORTABILITY-001` v2.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v2.

Each needs a per-artifact formal-artifact-approval packet.

### Slice 4 — Protected-Narrative Rewrites

**Goal**: Update rule files to reflect the new model. Formal-artifact-
approval gated per `GOV-ARTIFACT-APPROVAL-001` + narrative-artifact-
approval-gate.

**Dependency**: Slice 3 GOV updates (the narrative cites the updated
GOV specs).

**Files**:

- `.claude/rules/operating-role.md` — § Role Assignment Rules + § Role
  Set Schema.
- `.claude/rules/acting-prime-builder.md` — compatibility/provenance
  language preserved; role-uniqueness implication removed.
- `.claude/rules/canonical-terminology.md` — § single-harness operating
  mode + § role set + § operating role entries.
- `AGENTS.md` — § Durable Operating Role Assignment.

### Slice 5 — Packet Generator Regeneration

**Goal**: Regenerate narrative and spec packets that embedded the
superseded language.

**Dependency**: Slice 4 protected-narrative rewrites.

**Files**:

- `scripts/_build_narrative_packet_operating_role_md.py`.
- `scripts/_build_spec_single_harness_bridge_dispatcher_packet.py`.

### Slice 6 — Doctor Check Updates

**Goal**: Update doctor checks to enforce single-ACTIVE-per-role
invariant.

**Dependency**: Slice 2 resolver implementation (the doctor check
mirrors the resolver semantic).

**Files**:

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` —
  `_check_role_set_topology_consistency` (status-aware),
  `_check_single_harness_dispatcher_when_required` (status-aware
  applicability), plus a new `_check_single_active_per_role` check.

### Slice 7 — Backlog Hygiene & Reconciliation

**Goal**: Mark superseded artifacts, re-scope blocked WIs, reconcile
config drift.

**Dependency**: Slices 1-4 (the supersession references depend on the
new artifacts existing).

**Actions**:

- Mark `WI-3341` (VERIFIED) as superseded for the "exactly one prime-
  builder at all times" and "atomically demotes the others" clauses.
- Re-scope `WI-3343` ("ADR-SINGLE-HARNESS-OPERATING-MODE-001 extension")
  to align with Slice 1's ADR shape.
- Loosen `WI-3349` scope guard (the substrate-only restriction becomes
  less binding under the new model).
- Reconcile `.antigravity/config.toml` vs `harness-state/harness-
  registry.json` status drift via owner AUQ.
- Backlog implications for `PROJECT-ANTIGRAVITY-INTEGRATION` tracker.

## Risk & Rollback

This scoping proposal carries no implementation risk: it authorizes
only the bridge file write + INDEX.md entry insertion. Rollback in the
bridge-protocol sense is "supersede in the next version" (the file-
bridge protocol is append-only).

Per-slice risk and rollback land with per-slice proposals.

## Out of Scope

- Source code mutation, test mutation, hook mutation, configuration
  mutation, deployment, KB mutation other than the bridge files. All
  such work lands in per-slice proposals.
- The PB→LO dispatch substrate decision when active PB has no hook
  surface (Antigravity case). Downstream owner AUQ.
- AGENTS.md File Safety Contract changes for harness C beyond what the
  protected-narrative rewrite in Slice 4 addresses.
- DELIB-2079/2080/2081 retroactive amendment beyond the supersession
  citation in DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH.
- Reverting -001's in-place mutation (per Codex F1 recommendation, -001
  is preserved in its post-mutation state as part of the audit trail).
