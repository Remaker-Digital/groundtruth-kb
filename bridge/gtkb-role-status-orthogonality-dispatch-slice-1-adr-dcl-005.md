REVISED

bridge_kind: governance_advisory
Document: gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl
Version: 005
Responds to: bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-004.md NO-GO
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-31 UTC
Session: S378
Recommended commit type: docs

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S378-role-status-orthogonality-slice-1-adr-dcl-005
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

# Slice 1: ADR + DCL Governance Prerequisites — REVISED-2

## Response to Loyal Opposition NO-GO -004

### F1 (P1) — Phantom GOV-CHAT-DERIVED-SPEC-APPROVAL-001 citation removed

Codex correctly identified that `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`
does not exist in the live `specifications` table. A read-only query
confirms: the live authority for owner-visible spec capture is
`GOV-SPEC-CAPTURE-TRANSPARENCY-001` v1 (status `specified`, type
`governance`); the cited GOV is a phantom.

This phantom is a known defect in our own backlog: **WI-3506** captures
"3 rule files cite phantom `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`; owner
AUQ re-point to `GOV-SPEC-CAPTURE-TRANSPARENCY-001`" per the S376
project notes in `memory/MEMORY.md`. I cited the phantom GOV because the
upstream rule files still cite it; that propagation was the WI-3506
hazard manifesting through me. The fix here is local to this proposal:
remove the phantom citation. The rule-file repointing remains tracked
under WI-3506 as a separate backlog item.

REVISED-2 removes `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` from the
Specification Links. `GOV-SPEC-CAPTURE-TRANSPARENCY-001` remains as the
live authority for owner-visible artifact-body presentation and approval
capture; combined with `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-
APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, and
`ADR-ARTIFACT-FORMALIZATION-GATE-001`, the per-artifact AUQ flow has
complete live-spec coverage without the phantom.

Live-spec sweep performed against the operative Specification Links
before filing this REVISED-2: all 25 cited specs verified `LIVE` against
the live `specifications` table. New feedback memory captured under
`feedback_pre_file_phantom_spec_sweep.md` to prevent recurrence.

### F2 (P1) — target_paths now lists concrete KB-mutation targets

Codex correctly identified that the implementation-phase `target_paths`
in -003 listed the formal-artifact-approval packet path and the abstract
`gt spec record` insertions but did NOT name `groundtruth.db` as the
concrete file mutation target. The rule contract at
`.claude/rules/file-bridge-protocol.md` §39-43 requires concrete files
or globs authorized for implementation; the abstract description was
insufficient.

REVISED-2 corrects the `target_paths` section to enumerate:

- `groundtruth.db` (the MemBase SQLite file; concrete target of the three
  `gt spec record` inserts)
- `.groundtruth/formal-artifact-approvals/2026-05-*-ADR-ROLE-STATUS-ORTHOGONALITY-001.json`
- `.groundtruth/formal-artifact-approvals/2026-05-*-DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001.json`
- `.groundtruth/formal-artifact-approvals/2026-05-*-ADR-SINGLE-HARNESS-OPERATING-MODE-001.json`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-*.md`
  (next monotonic post-implementation report version)

The conflicting "no repository state outside the bridge and approval-
packet paths" sentence at -003 lines 277-278 is replaced with a precise
scope statement that names the authorized paths and excludes everything
else (no source files, tests, hooks, rule files, scripts, config files,
or other repository state).

### F1 from -002 (carried-forward correction)

The `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v2→v3 amendment target
correction from -003 carries forward unchanged. Codex's -004 verdict
confirmed the v3 target is correct ("the amendment target is now v3";
"The proposed v3 verification now requires an additive diff against live
v2, preserving both v1 topology and v2 harness-registry content").

## Source / Authorizing Verdict

This proposal is filed under the umbrella scoping proposal `gtkb-role-
status-orthogonality-dispatch-scoping`, which received Loyal Opposition
GO at `bridge/gtkb-role-status-orthogonality-dispatch-scoping-004.md`
(2026-05-31). Both deferred AUQs (status taxonomy, ADR shape) were
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
/ Input Section Gate".

1. **Owner directive (S378 prompt, 2026-05-31)** — captured in
   `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`. Role and dispatch
   eligibility are orthogonal axes; multiple harnesses may share a role;
   only the single status=active harness per role is auto-dispatch-
   eligible.

2. **Owner AskUserQuestion answer (S378, 2026-05-31) — scoping path**:
   "File umbrella project (Recommended)".

3. **Owner AskUserQuestion answer (S378, 2026-05-31) — status
   taxonomy**: "4-state owner-aligned (Recommended)" — canonical values
   are `active`, `inactive`, `suspended`, `retired`. Renames the
   WI-3339 FSM's existing `registered` state to `inactive`. Dispatch
   filter: only `active` is auto-dispatch-eligible.

4. **Owner AskUserQuestion answer (S378, 2026-05-31) — ADR shape**:
   "New successor ADR + amend old (Recommended)" — file a NEW canonical
   ADR `ADR-ROLE-STATUS-ORTHOGONALITY-001`; amend
   `ADR-SINGLE-HARNESS-OPERATING-MODE-001` to **v3** with supersession
   citations.

5. **Per-artifact formal-artifact-approval AUQs (in-slice, post-GO)** —
   three artifact bodies will be drafted, presented in chat verbatim,
   and approved via AskUserQuestion per `GOV-ARTIFACT-APPROVAL-001`
   before MemBase insertion:
   - `ADR-ROLE-STATUS-ORTHOGONALITY-001` v1 (NEW)
   - `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v1 (NEW)
   - `ADR-SINGLE-HARNESS-OPERATING-MODE-001` **v3** (amend live v2)

Downstream owner decisions deferred to future slices (not asked here):

- PB→LO dispatch substrate when active PB has no hook surface.
- Concrete status assignment for Antigravity (C) in the runtime
  registry: Slice 7 reconciliation question.

## Specification Links

All citations verified `LIVE` against the live `specifications` table
before filing this REVISED-2. Phantom `GOV-CHAT-DERIVED-SPEC-APPROVAL-
001` removed per F1.

- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval gate.
- `PB-ARTIFACT-APPROVAL-001` v2 — Prime Builder approval evidence trail.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` v3 — mechanical enforcement.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` v3 — gate scope contract.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` v1 — live capture-transparency
  surface; FULL artifact body shown verbatim in chat transcript before
  each AUQ approval. (See F1 response above for context on the
  phantom-citation removal that this spec now solely covers.)
- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 — bridge index authority.
- `GOV-HARNESS-ROLE-PORTABILITY-001` v1 — current; Slice 3 updates.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v1 — current; Slice 3
  updates.
- `GOV-ACTING-PRIME-BUILDER-001` v1 — unchanged compatibility contract.
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 — unchanged authority split.
- `WI-3341` (VERIFIED) — Role portability and single-prime-builder
  invariant enforcement; new ADR supersedes its single-PB clauses.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — current live state is v2
  (S361 harness-registry extension); to be amended to v3 in this slice.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` v1 § Coexistence —
  affected in Slice 2; not modified here.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` v1 — affected in
  Slice 2/6; not modified here.
- `DCL-SESSION-ROLE-RESOLUTION-001` v1 — unchanged.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 — unchanged.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 — downstream substrate
  decision; not modified here.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 — this
  proposal's compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 — verification
  compliance.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` v1 — cross-harness enforcement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 —
  `bridge_kind: governance_review` exemption.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 — blocking. All
  artifacts produced or modified by this proposal reside in-root under
  `E:\GT-KB`. The bridge file is in-root at `bridge/`. MemBase artifact
  insertions go to `groundtruth.db` which is in-root. Formal-artifact-
  approval packets go to `.groundtruth/formal-artifact-approvals/`
  which is in-root. No out-of-root file mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 — advisory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 — advisory.

## Prior Deliberations

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — owner directive
  source authorizing the entire umbrella project.
- `DELIB-2079` — Antigravity Integration 3-harness design (also
  originates the harness-registry architecture in WI-3343 / v2 of the
  single-harness ADR).
- `DELIB-2080` — Single-PB invariant + role portability amendment.
- `DELIB-2081` — Antigravity-project authorization context.
- `DELIB-2094` — VERIFIED bridge thread for `gtkb-harness-role-
  portability-fr9` (WI-3341 implementation history).
- `DELIB-2342` / `DELIB-2344` — Prior bridge role-intent sentinel
  reviews.
- `DELIB-S324-OM-DELTA-0003-CHOICE` — Operating-model terminology.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` — Codex
  hook parity refresh.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` — Lifecycle-independence
  framing.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` — Cross-harness
  exec resolution exception.
- `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` —
  Active-session suppression contract.

## Requirement Sufficiency

**New or revised requirement required before implementation.**

Rationale: This slice creates two new specifications (the new ADR and
DCL) and amends one existing ADR. Each is a formal-artifact-approval-
gated mutation. Implementation does not authorize any source code, test,
hook, configuration, or rule file mutation; those land in Slices 2-6.

## target_paths

This proposal's `target_paths` for the proposal-filing phase are
limited to:

- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-005.md`
  (this file)
- `bridge/INDEX.md` (REVISED entry insertion above the NO-GO -004 line)

Implementation-phase `target_paths` (post-GO; authorized by the
implementation-start packet against the eventual GO):

- `groundtruth.db` — concrete MemBase SQLite file; target of the three
  `gt spec record` (or equivalent governed service) inserts:
  - `ADR-ROLE-STATUS-ORTHOGONALITY-001` v1 (new spec row, `type =
    architecture_decision`)
  - `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v1 (new spec row, `type =
    design_constraint`)
  - `ADR-SINGLE-HARNESS-OPERATING-MODE-001` **v3** (version bump from
    live v2; supersession citations on single-PB clauses; preserves v1
    single-harness topology content AND v2 harness-registry architecture
    content)
- `.groundtruth/formal-artifact-approvals/2026-05-*-ADR-ROLE-STATUS-ORTHOGONALITY-001.json`
- `.groundtruth/formal-artifact-approvals/2026-05-*-DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001.json`
- `.groundtruth/formal-artifact-approvals/2026-05-*-ADR-SINGLE-HARNESS-OPERATING-MODE-001.json`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-*.md`
  (next monotonic post-implementation report version, e.g. `-006`,
  `-007`, etc.)

Out-of-scope concrete paths (NOT authorized by this proposal): any source
code file (`scripts/`, `groundtruth-kb/src/`), test file (`tests/`,
`platform_tests/`), hook file (`.claude/hooks/`, `.codex/gtkb-hooks/`),
rule file (`.claude/rules/`, `AGENTS.md`, `CLAUDE.md`), config file
(`.claude/settings.json`, `pyproject.toml`, etc.), `bridge/INDEX.md`
modifications other than insertion of new version rows for this thread,
and any other repository state.

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
   1. `ADR-ROLE-STATUS-ORTHOGONALITY-001` v1 first.
   2. `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v1 second.
   3. `ADR-SINGLE-HARNESS-OPERATING-MODE-001` **v3** third.

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
  ACTIVE-per-role invariant.
- **Context**: Owner directive S378.
- **Failed approaches**: dual-PB without status filter; ADR v3 of
  single-harness mode as sole canonical home.
- **Rejected alternatives**: 3-state minimal; 5-state superset; FSM-as-
  is with semantic mapping.
- **Consequences**: Per-slice work for resolver code (Slice 2), GOV
  updates (Slice 3), protected-narrative rewrites (Slice 4), packet
  generator regen (Slice 5), doctor check updates (Slice 6), backlog
  hygiene (Slice 7).

### DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 v1 (NEW)

- **Title**: Single-ACTIVE-per-role dispatch resolution constraint.
- **Constraint**: Cross-harness event-driven trigger resolution
  matches by role AND status=active; fail closed only on multiple-
  ACTIVE-match; emit structured audit on zero-ACTIVE-match.
- **Assertions**: machine-checkable claims that will land in Slice 2.
- **Affected by**: `ADR-ROLE-STATUS-ORTHOGONALITY-001`.

### ADR-SINGLE-HARNESS-OPERATING-MODE-001 v3 (AMEND existing v2)

- **Amendment scope**: Add per-clause supersession citations marking
  the single-PB clauses as superseded by
  `ADR-ROLE-STATUS-ORTHOGONALITY-001`. Preserve **all** content from
  the live v2 row. v3 is purely additive against v2.
- **Specific clauses superseded**: "exactly one prime-builder at all
  times" + "atomically demotes the others" framing inherited from
  `WI-3341`.
- **Preserved from v2 (S361)**: harnesses table architecture, registry
  projection, lifecycle FSM context.
- **Preserved from v1**: single-harness topology definition; role-set
  schema; READ-accepted legacy scalar form; READ-accepted legacy
  `acting-prime-builder` token.

## Spec-Derived Verification Plan (Implementation Phase)

The post-implementation report must include the following spec-to-test
mapping (no `pytest`/`ruff` commands apply here because this slice is
governance-only; verification is via MemBase row inspection + packet-
hash equality + textual diff, not source-level test runs):

1. **`GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`** —
   each of the three approval packets exists at the named path, has
   `presented_to_user=true`, `transcript_captured=true`,
   `approved_by=owner`, `full_content_sha256=<sha>`. Each MemBase row's
   `change_reason` cites the packet path. Each packet's hash matches
   the inserted row.

2. **`GOV-SPEC-CAPTURE-TRANSPARENCY-001`** — transcript snippet for
   each AUQ shows the FULL artifact body presented verbatim before the
   option-select event.

3. **`PB-ARTIFACT-APPROVAL-001`** — report enumerates each artifact's
   approval-packet path + insertion evidence + spec ID.

4. **Linkage to `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`** —
   each artifact's `change_reason` cites the DELIB and the umbrella
   scoping GO.

5. **Linkage to AUQ answers** — status taxonomy and ADR shape AUQ
   answers from this session cited in each artifact's `change_reason`
   or `Context` field.

6. **`ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 supersession evidence**
   — v3 row's body contains explicit per-clause supersession citations
   pointing at `ADR-ROLE-STATUS-ORTHOGONALITY-001`.

7. **`ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 purely-additive
   evidence** — textual diff of v3 against live v2 shows ONLY added
   supersession-citation text. Both v1 topology content AND v2
   harness-registry architecture content preserved verbatim. Diff
   included in the post-implementation report.

8. **MemBase canonical-insert evidence** — `gt spec get
   ADR-ROLE-STATUS-ORTHOGONALITY-001` returns the new v1 row; `gt spec
   get DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` returns the new v1
   row; `gt spec get ADR-SINGLE-HARNESS-OPERATING-MODE-001` returns
   v3.

9. **target_paths post-condition** — `git status` shows changes only to
   the authorized targets (`groundtruth.db`,
   `.groundtruth/formal-artifact-approvals/*.json`, the bridge file +
   `bridge/INDEX.md`). No source/test/hook/rule/config file
   modifications.

10. **Mandatory preflights** — Codex MUST run `python scripts/
    bridge_applicability_preflight.py --bridge-id gtkb-role-status-
    orthogonality-dispatch-slice-1-adr-dcl` and `python scripts/
    adr_dcl_clause_preflight.py --bridge-id gtkb-role-status-
    orthogonality-dispatch-slice-1-adr-dcl` and include both sections
    in any verdict.

## Risk & Rollback

Risks:

- **Per-artifact AUQ rejection**: implementation iterates through
  another draft/present/AUQ cycle. No MemBase mutation occurs until
  approval.
- **Approval-packet/insert-row hash mismatch**: the
  `DCL-ARTIFACT-APPROVAL-HOOK-001` gate blocks the insertion before
  any row is written. Recovery: regenerate the packet against the
  exact body that will be inserted.
- **v2 content regression on v3**: the purely-additive-diff
  verification step (item 7) catches it before the report is filed.

Rollback:

- MemBase artifacts are append-only. Rollback is "supersede in the
  next version" + a corrective DELIB. The `ADR-SINGLE-HARNESS-
  OPERATING-MODE-001` v3 amendment can be rolled back via v4
  (no data loss).
- The new ADR + DCL inserts cannot be "deleted"; rollback is a future
  supersession.
- This proposal's bridge file rollback is "supersede via REVISED".

## Out of Scope

- Source code, test, hook, configuration, rule file, deployment, and
  repository-state mutation. All land in Slices 2-6.
- Per-slice authorization for Slices 2+.
- Concrete status assignment for Antigravity (C) in the runtime
  registry. Slice 7.
- PB→LO dispatch substrate decision when active PB has no hook
  surface. Downstream of Slice 6 or a separate substrate thread.
- Rule file rewrites. Slice 4 work.
- Packet generator regeneration. Slice 5 work.
- Doctor check updates. Slice 6 work.
- Backlog hygiene. Slice 7 work.
- AGENTS.md File Safety Contract changes for harness C beyond what
  protected-narrative rewrite Slice 4 addresses.
- Re-pointing `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` references in rule
  files. Tracked under WI-3506 as a separate backlog item.
