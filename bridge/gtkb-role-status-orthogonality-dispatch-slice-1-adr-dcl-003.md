REVISED

bridge_kind: governance_advisory
Document: gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl
Version: 003
Responds to: bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-002.md NO-GO
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-31 UTC
Session: S378
Recommended commit type: docs

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S378-role-status-orthogonality-slice-1-adr-dcl-003
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

# Slice 1: ADR + DCL Governance Prerequisites — REVISED-1

## Response to Loyal Opposition NO-GO -002

### F1 (P1) — ADR-SINGLE-HARNESS-OPERATING-MODE-001 version target corrected: v2 → v3

Codex correctly identified that `bridge/gtkb-role-status-orthogonality-
dispatch-slice-1-adr-dcl-001.md` repeatedly targeted v2 of
`ADR-SINGLE-HARNESS-OPERATING-MODE-001` even though v2 already exists in
the live `specifications` table (changed at 2026-05-18T19:27:02 per
WI-3343 / DELIB-2079 Q11 — the harness-registry extension). Live-state
verification:

```text
v1  2026-05-12T04:20:42  IP-1 of gtkb-single-harness-bridge-dispatcher-001
v2  2026-05-18T19:27:02  WI-3343 harness-registry architecture extension
```

The append-only versioned `specifications` table has `UNIQUE(id, version)`,
so re-inserting v2 would either collide or silently overwrite the existing
S361 v2 history. The correct target for this slice's supersession-citation
amendment is **v3**.

This REVISED-1 corrects every occurrence of "v2" referring to the
`ADR-SINGLE-HARNESS-OPERATING-MODE-001` amendment target to "v3" — across
the owner-input section, specification links, target paths,
implementation sequence, artifact outline, verification plan, and
rollback section. The verification plan is also strengthened to require
evidence that v3 contains the per-clause supersession citations AND that
a diff against the existing v2 preserves both the single-harness topology
content (v1 origin) AND the harness-registry architecture content (v2
S361 origin); v3 must be purely additive.

The lesson — "probe live MemBase version state before naming target
versions in proposals" — extends the existing `feedback_probe_live_
state_before_quoting_counts.md` memory entry; saved as a new feedback
memory at session wrap.

Codex's positive confirmations from -002 carry forward unchanged:
`bridge_kind: governance_review` self-declaration accepted; Owner
Decisions / Input section substantive; specification linkage sufficient
(preflights pass); the two NEW spec IDs (`ADR-ROLE-STATUS-ORTHOGONALITY-
001` and `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`) confirmed absent from
live `specifications` (consistent with the create-after-GO plan).

## Source / Authorizing Verdict

This proposal is filed under the umbrella scoping proposal `gtkb-role-
status-orthogonality-dispatch-scoping`, which received Loyal Opposition
GO at `bridge/gtkb-role-status-orthogonality-dispatch-scoping-004.md`
(2026-05-31). Codex's verdict explicitly authorized "Prime Builder may
proceed to the next bridge proposal in the scoped sequence, beginning
with Slice 1 governance prerequisites" and required: "Slice 1 must
still obtain the deferred AUQs named in -003 for status taxonomy and
ADR-shape choices before formal artifact mutation." Both AUQs were
obtained in S378 and are captured below.

## Proposal Kind

`bridge_kind: governance_review`. This proposal does not authorize any
source code, test, hook, configuration, or deployment mutation. It
authorizes governance-layer MemBase mutations only — specifically the
insertion of one new ADR, one new DCL, and one new version of an
existing ADR. Each MemBase mutation requires a per-artifact formal-
artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001` collected via
AskUserQuestion during the implementation phase (post-GO).

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions
/ Input Section Gate". This proposal depends on owner approval evidence
and cites the AUQ-only enforcement rule.

1. **Owner directive (S378 prompt, 2026-05-31)** — captured in
   `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`. Role and dispatch
   eligibility are orthogonal axes; multiple harnesses may share a role;
   only the single status=active harness per role is auto-dispatch-
   eligible. The session-stated role override via the canonical init
   keyword continues to take precedence for in-session surfaces.

2. **Owner AskUserQuestion answer (S378, 2026-05-31) — scoping path**:
   "File umbrella project (Recommended)". Authorizes the umbrella +
   per-slice approach this proposal continues.

3. **Owner AskUserQuestion answer (S378, 2026-05-31) — status
   taxonomy**: "4-state owner-aligned (Recommended)" — canonical values
   are `active`, `inactive`, `suspended`, `retired`. Renames the
   WI-3339 FSM's existing `registered` state to `inactive` (matches
   S378 verbatim terminology while preserving the four-state lifecycle
   FSM structure). Keeps `retired` for fully-decommissioned harnesses.
   Dispatch filter: only `active` is auto-dispatch-eligible.

4. **Owner AskUserQuestion answer (S378, 2026-05-31) — ADR shape**:
   "New successor ADR + amend old (Recommended)" — file a NEW canonical
   ADR `ADR-ROLE-STATUS-ORTHOGONALITY-001` covering role/status
   orthogonality, the 4-state taxonomy, the single-ACTIVE-per-role
   invariant, and dispatch-filter semantics. Separately amend
   `ADR-SINGLE-HARNESS-OPERATING-MODE-001` to **v3** with citations
   marking the single-PB clauses as superseded by the new ADR.

5. **Per-artifact formal-artifact-approval AUQs (in-slice, post-GO)** —
   three artifact bodies will be drafted, presented in chat verbatim,
   and approved via AskUserQuestion per `GOV-ARTIFACT-APPROVAL-001`
   before MemBase insertion:
   - `ADR-ROLE-STATUS-ORTHOGONALITY-001` v1 (NEW)
   - `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v1 (NEW)
   - `ADR-SINGLE-HARNESS-OPERATING-MODE-001` **v3** (amend live v2 with
     supersession citations on single-PB clauses; preserve single-
     harness mode content from v1 AND harness-registry architecture
     content from v2)

Downstream owner decisions deferred to future slices (not asked here):

- PB→LO dispatch substrate when active PB has no hook surface (the
  Antigravity-as-active-PB case): downstream of Slice 6 doctor work or
  a separate substrate-decision thread.
- Concrete status assignment for Antigravity (C) in the runtime
  registry: Slice 7 reconciliation question.

## Specification Links

Governing specifications cited by this proposal. Per `.claude/rules/file-
bridge-protocol.md` § "Mandatory Specification Linkage Gate".

- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval gate; each of
  the three artifact mutations passes its own approval packet.
- `PB-ARTIFACT-APPROVAL-001` — Prime Builder responsibility for
  approval evidence trail.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — mechanical enforcement at
  insertion time.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — gate scope contract.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — live capture-transparency
  surface; FULL artifact body shown verbatim in chat transcript before
  each AUQ approval.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge index authority for this
  proposal and the post-implementation report.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — current GOV governing role
  portability; Slice 3 updates this spec; Slice 1 cites the existing
  contract that will be extended.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — current GOV governing
  multi-harness role config; Slice 3 updates; Slice 1 cites the
  existing contract.
- `GOV-ACTING-PRIME-BUILDER-001` — unchanged compatibility/provenance
  contract.
- `GOV-SESSION-ROLE-AUTHORITY-001` — unchanged authority split (durable
  vs session-stated); this slice does not touch session-role resolution.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner-visible spec capture
  workflow; applied to the per-artifact AUQ flow.
- `WI-3341` (VERIFIED) — "Role portability and single-prime-builder
  invariant enforcement"; the new ADR supersedes its "exactly one
  prime-builder at all times" and "atomically demotes the others"
  clauses. Slice 7 marks WI-3341 superseded.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — current live state is v2
  (S361 harness-registry extension); to be amended to v3 in this slice
  with per-clause supersession citations layered onto v2 content.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` § Coexistence — affected
  language about substrate selection becomes status-aware in Slice 2;
  not modified in Slice 1.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — applicability
  check becomes status-aware in Slice 2/Slice 6; not modified in
  Slice 1.
- `DCL-SESSION-ROLE-RESOLUTION-001` — unchanged.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — unchanged.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 — relevant to downstream
  substrate decision; not modified in Slice 1.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this
  proposal's compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — this slice's
  verification compliance (see § Spec-Derived Verification Plan).
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — governs cross-harness
  enforcement of the bridge protocol.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal
  self-declares `bridge_kind: governance_review` for exemption from
  the project-linkage requirement.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking. All artifacts
  produced or modified by this proposal reside in-root under
  `E:\GT-KB`. The bridge file is in-root at `bridge/`. MemBase
  artifact insertions go to `groundtruth.db` which is in-root. Formal-
  artifact-approval packets go to `.groundtruth/formal-artifact-
  approvals/` which is in-root. No out-of-root file mutation in this
  slice.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory. This slice
  produces durable artifacts (ADR + DCL + ADR version bump).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory. The slice
  references superseded, candidate, verified, and deferred lifecycle
  states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory. The slice
  preserves the artifact-oriented governance default by routing every
  artifact through the per-artifact formal-artifact-approval flow.

## Prior Deliberations

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — owner directive
  source authorizing the entire umbrella project.
- `DELIB-2079` — Antigravity Integration 3-harness design (established
  the single-PB invariant being superseded; also originates the
  harness-registry architecture in WI-3343 / v2 of the single-harness
  ADR).
- `DELIB-2080` — Single-PB invariant + role portability amendment;
  superseded in part by this slice.
- `DELIB-2081` — Antigravity-project authorization context.
- `DELIB-2094` — VERIFIED bridge thread for `gtkb-harness-role-
  portability-fr9` (WI-3341 implementation history).
- `DELIB-2342` / `DELIB-2344` — Prior bridge role-intent sentinel
  reviews; useful context for keeping role authority distinct from
  mirror/checksum surfaces.
- `DELIB-S324-OM-DELTA-0003-CHOICE` — Operating-model terminology.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` — Codex
  hook parity refresh.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` — Lifecycle-independence
  framing.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` — Cross-harness
  exec resolution exception.
- `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` —
  Active-session suppression contract (orthogonal to status filter).

## Requirement Sufficiency

**New or revised requirement required before implementation.**

Rationale: This slice creates two new specifications (the new ADR and
DCL) and amends one existing ADR. Each is a formal-artifact-approval-
gated mutation. The artifact bodies will be drafted in the
implementation phase, presented to the owner verbatim per
`GOV-SPEC-CAPTURE-TRANSPARENCY-001`, approved via AskUserQuestion, and
inserted into MemBase via the governed CLI service path. Implementation
does not authorize any source code, test, hook, configuration, or rule
file mutation; those land in Slices 2-6.

## target_paths

This proposal's `target_paths` for the proposal-filing phase are
limited to:

- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-003.md`
  (this file)
- `bridge/INDEX.md` (REVISED entry insertion above the NO-GO -002 line)

Implementation-phase mutations (post-GO, separate authorization via
implementation-start packet against the GO):

- Three formal-artifact-approval packets at `.groundtruth/formal-
  artifact-approvals/2026-05-NN-<artifact-id>.json` (one per artifact;
  exact dates depend on implementation timing).
- Three MemBase inserts via `gt spec record` or equivalent governed
  service path:
  - `ADR-ROLE-STATUS-ORTHOGONALITY-001` v1 (new spec, `type =
    architecture_decision`).
  - `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v1 (new spec, `type =
    design_constraint`).
  - `ADR-SINGLE-HARNESS-OPERATING-MODE-001` **v3** (version bump from
    live v2 with supersession citations on single-PB clauses; preserves
    v1 single-harness topology content AND v2 harness-registry
    architecture content).
- The post-implementation report at `bridge/gtkb-role-status-
  orthogonality-dispatch-slice-1-adr-dcl-NNN.md` (next version
  monotonic).

No source files, no test files, no rule files, no hook files, no
config files, no deployment, no repository state outside the bridge
and approval-packet paths.

## Project Decomposition (This Slice's Sub-Steps)

This slice is single-step. Implementation sequence post-GO:

1. **Draft the three artifact bodies** offline (no MemBase mutation
   yet). Each body follows the canonical ADR/DCL template per
   `templates/managed-artifacts.toml`. The `ADR-SINGLE-HARNESS-
   OPERATING-MODE-001` v3 draft is built by reading the live v2 row
   and adding per-clause supersession citations — no deletion of v2
   content.

2. **Present and approve each artifact via AskUserQuestion**:
   - Present the FULL artifact body verbatim in chat per
     `GOV-SPEC-CAPTURE-TRANSPARENCY-001`.
   - Ask owner: "Approve as drafted / request revisions / withdraw."
   - On approval, capture the formal-artifact-approval packet with
     `presented_to_user=true`, `transcript_captured=true`,
     `approved_by=owner`, `full_content_sha256=<sha>`.

3. **Insert each approved artifact via the governed service path** (`gt
   spec record` or equivalent). The `DCL-ARTIFACT-APPROVAL-HOOK-001`
   gate validates the packet hash matches the inserted row.

4. **Order**:
   1. `ADR-ROLE-STATUS-ORTHOGONALITY-001` v1 first (foundation
      artifact; codifies the model).
   2. `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v1 second (extends the
      ADR; references it for `affected_by`).
   3. `ADR-SINGLE-HARNESS-OPERATING-MODE-001` **v3** third (amendment;
      cites the new `ADR-ROLE-STATUS-ORTHOGONALITY-001` for the
      superseded single-PB clauses; preserves v2 harness-registry
      content; layers supersession citations onto the v2 body).

5. **File post-implementation report** as `gtkb-role-status-
   orthogonality-dispatch-slice-1-adr-dcl-NNN.md` (next monotonic
   version), enumerating packet paths + insertion evidence +
   per-artifact diff evidence.

## Artifact Outlines (Drafted Post-GO; Listed Here for Scope Visibility)

### ADR-ROLE-STATUS-ORTHOGONALITY-001 v1 (NEW)

- **Title**: Role/status orthogonality with single-ACTIVE-per-role
  dispatch.
- **Decision**: Role assignment and dispatch eligibility are orthogonal
  axes. Status taxonomy: `active`, `inactive`, `suspended`, `retired`
  (the WI-3339 FSM's `registered` is renamed to `inactive`). Single-
  ACTIVE-per-role invariant: at most one harness per role may carry
  status=active for the purpose of auto-dispatch routing. The session-
  stated role override via the canonical init keyword takes precedence
  for in-session surfaces (preserved per
  `GOV-SESSION-ROLE-AUTHORITY-001`).
- **Context**: Owner directive S378; supersedes parts of `DELIB-2080`
  and `WI-3341`.
- **Failed approaches**: dual-PB without status filter (current state;
  resolver fails closed); ADR v3 of single-harness mode used as sole
  canonical home (conflates topology with dispatch rule).
- **Rejected alternatives**: 3-state minimal vocabulary; 5-state
  superset; FSM-as-is with semantic mapping. (Owner selected 4-state
  owner-aligned via AUQ.)
- **Consequences**: Per-slice work for resolver code (Slice 2), GOV
  updates (Slice 3), protected-narrative rewrites (Slice 4), packet
  generator regen (Slice 5), doctor check updates (Slice 6), backlog
  hygiene (Slice 7).

### DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 v1 (NEW)

- **Title**: Single-ACTIVE-per-role dispatch resolution constraint.
- **Constraint**: Cross-harness event-driven trigger resolution
  (`scripts/cross_harness_bridge_trigger.py:_resolve_dispatch_target`)
  matches by role AND status=active; fail closed only on multiple-
  ACTIVE-match; emit structured audit on zero-ACTIVE-match. Single-
  harness mode dispatcher applicability also status-aware.
- **Assertions**: (machine-checkable claims that will land in Slice 2
  alongside the resolver code).
- **Affected by**: `ADR-ROLE-STATUS-ORTHOGONALITY-001`.
- **Affects**: future doctor checks (Slice 6).

### ADR-SINGLE-HARNESS-OPERATING-MODE-001 v3 (AMEND existing v2)

- **Amendment scope**: Add per-clause supersession citations marking
  the single-PB clauses as superseded by
  `ADR-ROLE-STATUS-ORTHOGONALITY-001`. Preserve **all** content from
  the live v2 row — both v1's single-harness topology content (role-
  set wire form, atomic migration path, Path 2 framing) AND v2's
  harness-registry architecture content (per WI-3343 / DELIB-2079 Q11).
  v3 is purely additive against v2: the diff shows added supersession
  citations on specific clauses, nothing removed.
- **Specific clauses superseded**: the "exactly one prime-builder at
  all times" + "atomically demotes the others" framing previously
  inherited from `WI-3341`.
- **Preserved from v2 (S361)**: harnesses table architecture, registry
  projection, lifecycle FSM context.
- **Preserved from v1**: single-harness topology definition; role-set
  schema for in-process Python `frozenset[str]`; READ-accepted legacy
  scalar form; READ-accepted legacy `acting-prime-builder` token.

## Spec-Derived Verification Plan (Implementation Phase)

After implementation, the post-implementation report must include the
following spec-to-test mapping:

1. **`GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`** —
   verification: each of the three formal-artifact-approval packets
   exists at `.groundtruth/formal-artifact-approvals/`, has
   `presented_to_user=true`, `transcript_captured=true`,
   `approved_by=owner`, `full_content_sha256=<sha>`. Each MemBase row's
   `change_reason` cites the packet path. Each packet's
   `full_content_sha256` matches the inserted row's body hash.

2. **`GOV-SPEC-CAPTURE-TRANSPARENCY-001`** — verification: the
   transcript snippet for each AUQ shows the FULL artifact body
   presented verbatim before the AUQ option-select event.

3. **`PB-ARTIFACT-APPROVAL-001`** — verification: the report enumerates
   each artifact's approval-packet path + insertion evidence + spec ID.

4. **Linkage to `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`** —
   verification: each artifact's `change_reason` cites the DELIB and
   the umbrella scoping GO (`bridge/gtkb-role-status-orthogonality-
   dispatch-scoping-004.md`).

5. **Linkage to AUQ answers** — verification: status taxonomy and ADR
   shape AUQ answers from this session are cited in each artifact's
   `change_reason` or `Context` field.

6. **`ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 supersession evidence**
   — verification: the v3 row's body contains explicit per-clause
   supersession citations pointing at `ADR-ROLE-STATUS-ORTHOGONALITY-
   001`.

7. **`ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 purely-additive
   evidence** — verification: a textual diff of v3 against the live v2
   row shows ONLY added supersession-citation text. No content removed.
   Both v1's single-harness topology content AND v2's harness-registry
   architecture content are preserved verbatim. The diff is included in
   the post-implementation report.

8. **MemBase canonical-insert evidence** — verification: `gt spec get
   ADR-ROLE-STATUS-ORTHOGONALITY-001` returns the new v1 row; `gt spec
   get DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` returns the new v1
   row; `gt spec get ADR-SINGLE-HARNESS-OPERATING-MODE-001` returns v3
   (verifying v3 is the new latest version, not a re-insert of v2).

9. **Mandatory preflights** — Codex MUST run `python scripts/
   bridge_applicability_preflight.py --bridge-id gtkb-role-status-
   orthogonality-dispatch-slice-1-adr-dcl` and `python scripts/
   adr_dcl_clause_preflight.py --bridge-id gtkb-role-status-
   orthogonality-dispatch-slice-1-adr-dcl` and include both sections
   in any verdict. Treat exit 5 as NO-GO blocker absent owner waiver.

## Risk & Rollback

Risks:

- **Per-artifact AUQ rejection**: if the owner requests revisions to
  any drafted artifact body, the implementation iterates through
  another draft/present/AUQ cycle. No MemBase mutation occurs until
  approval.
- **Approval-packet/insert-row hash mismatch**: the
  `DCL-ARTIFACT-APPROVAL-HOOK-001` gate blocks the insertion before
  any row is written. Recovery: regenerate the packet against the
  exact body that will be inserted.
- **Citation drift**: if the new ADR's content drifts from the AUQ-
  approved body during insertion, the packet's `full_content_sha256`
  will mismatch and the gate will block. Recovery: keep the AUQ-
  approved body byte-identical with the inserted row.
- **v2 content regression on v3**: if v3 accidentally omits any v2
  content (e.g., the WI-3343 harness-registry architecture clauses),
  the purely-additive-diff verification step (item 7) will catch it
  before the implementation report is filed.

Rollback:

- MemBase artifacts are append-only/versioned. Rollback in the
  MemBase sense is "supersede in the next version" + a corrective
  DELIB. The `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 amendment
  can be rolled back via a v4 that removes the supersession
  citations (no data loss; the v3 row stays as history).
- The new ADR + DCL inserts cannot be "deleted" in MemBase; rollback
  is a future supersession.
- This proposal's bridge file rollback is "supersede via REVISED" per
  the file-bridge protocol's append-only invariant.

## Out of Scope

- Source code, test, hook, configuration, rule file, deployment, and
  repository-state mutation. All land in Slices 2-6.
- Per-slice authorization for Slices 2+. Each requires its own
  separate bridge proposal.
- Concrete status assignment for Antigravity (C) in the runtime
  registry. Slice 7 reconciliation question, blocked on owner AUQ.
- PB→LO dispatch substrate decision when active PB has no hook
  surface. Downstream of Slice 6 or a separate substrate thread.
- Rule file rewrites (operating-role.md, AGENTS.md, canonical-
  terminology.md, acting-prime-builder.md). Slice 4 work.
- Packet generator regeneration. Slice 5 work.
- Doctor check updates. Slice 6 work.
- Backlog hygiene (WI-3341 supersession marking, WI-3343 re-scope,
  WI-3349 scope loosening, .antigravity/config.toml drift). Slice 7
  work.
- AGENTS.md File Safety Contract changes for harness C beyond what
  protected-narrative rewrite Slice 4 addresses.
