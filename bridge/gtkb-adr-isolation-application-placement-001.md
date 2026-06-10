NEW

# ADR-ISOLATION-APPLICATION-PLACEMENT — Governance Proposal

**Status:** NEW (governance/architecture; awaiting Codex review)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-ISOLATION-016 (governance prerequisite); blocks `-011` revision
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** governance_proposal
**Routing:** Upstream (`groundtruth-kb`). The ADR is platform-wide; supersedes a Phase 9 plan paragraph that was authored before the IDP filesystem topology question was settled.

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-009, GTKB-ISOLATION-016, GTKB-ISOLATION-017]
spec_ids: []
target_project: groundtruth-kb (ADR) + agent-red (Phase 9 plan annotation)
implementation_scope: adr_insertion_and_plan_supersession
requires_review: true
requires_verification: true

---

## 0. What This Proposal Is

Owner-directed Option B (S310, 2026-04-26) in response to the
ISOLATION-016 `-012` NO-GO finding: capture the architectural
decision "adopter applications live at `<gt-kb-root>/applications/<name>/`"
as a formal ADR that supersedes the contradicting paragraph in the
already-VERIFIED Phase 9 plan.

The Codex `-012` finding correctly identified that
`bridge/gtkb-isolation-016-phase8-rehearsal-implementation-011.md`
asserted the apps-under-GT-KB convention while the Phase 9 plan
(VERIFIED at `gtkb-isolation-009-adopter-packaging-plan-review-004`)
explicitly says `gt project init` creates an application root that is
NOT a subdirectory of the GT-KB product root
(`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:93-98`).

Owner's S310 architectural correction overrides the prior plan's
placement decision because:

1. The IDP model in `CLAUDE.md` defines GT-KB as the platform that
   hosts adopter projects; siblings-on-disk doesn't map cleanly to
   the platform-hosting-projects mental model.
2. Cross-root portability (apps running from paths without GT-KB at
   root) is **not validated**. The harness-adjacent infrastructure
   (`.claude/`, `.codex/`, `groundtruth.db`, `bridge/`, dashboard,
   hooks, skills) all resolve from project root via
   `Path(__file__).resolve().parents[N]`. Whether any of that works
   from a non-GT-KB-root path is untested.
3. The first conformant adopter migration (Agent Red) sets the
   template every future adopter follows. Establishing an unvalidated
   topology as that template is unacceptably risky.

This proposal is **scope and approval only**. On Codex GO, three
mechanical follow-ups happen as a coordinated change set:

1. ADR `ADR-ISOLATION-APPLICATION-PLACEMENT-001` inserted into KB via
   the `kb-adr` skill.
2. Phase 9 plan document annotated with a SUPERSEDED-BY notice
   pointing at the ADR. The Phase 9 plan-review bridge thread itself
   stays VERIFIED (the plan was correctly written under prior
   assumptions; the supersession is via ADR not via re-VERIFY of the
   bridge).
3. `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md`
   filed REVISED-6 with the same content as `-011` plus citation to
   the now-inserted ADR, plus the conflated-surface list expansion
   per Codex `-012` non-blocking note (`scripts`, `website`, `widget`,
   `tools`).

## 1. Prior Deliberations

- **Owner directive S310 (2026-04-26):** "Proceed with Option B —
  Supersede Phase 9 plan: File a formal ADR
  ADR-ISOLATION-APPLICATION-PLACEMENT-001 capturing the apps-under-GT-KB
  convention as binding, AND revise the Phase 9 plan to match."
- **Codex `-012` NO-GO** on ISOLATION-016 `-011`: identified the
  Phase 9 plan contradiction; recommended explicit supersession or
  alignment.
- **Owner architectural correction S310:** repeated assertion that
  applications live at `<gt-kb-root>/applications/<name>/`, with the
  load-bearing concern that cross-root operation has not been
  validated.
- **Phase 9 plan VERIFIED:**
  `gtkb-isolation-009-adopter-packaging-plan-review-004` — the plan
  document's §1 (`gt project init` placement rule) is the specific
  paragraph being superseded.
- **`CLAUDE.md` IDP definition:** "GT-KB is an Internal Developer
  Platform for individual developers building production software with
  AI assistance; it provides shared project infrastructure, governance
  artifacts, and conventions that adopter applications consume."
- **`docs/gtkb-idp-concept.md:97-99`:** mentions parent-IDP-with-apps-
  as-subdirectories as an adjacent deliberation pointer (not
  previously codified as a formal rule).
- **No prior ADR governs application placement.** This is the first.

## 2. Proposed ADR Content

When inserted via `kb-adr`, the ADR carries:

### 2.1 ADR ID

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`

### 2.2 Title

Adopter applications live at `<gt-kb-root>/applications/<name>/`

### 2.3 Decision (one paragraph, binding)

Adopter applications adopting GroundTruth-KB live as named
subdirectories under `<gt-kb-root>/applications/<name>/`, where
`<gt-kb-root>` is the platform's project root and `<name>` is a valid
identifier matching `^[A-Za-z][A-Za-z0-9_-]*$`. The application's
filesystem boundary is a strict descendant of
`<gt-kb-root>/applications/`. The platform retains write authority on
its own product artifacts; the application has write authority on its
own root and any platform-allowed adopter-owned artifacts as defined
by the managed artifact registry.

### 2.4 Context

GT-KB is an Internal Developer Platform. Adopter applications consume
GT-KB's shared infrastructure (specs, work items, bridge protocol,
deliberation archive, MemBase, dashboard, hooks, skills). Two
filesystem topologies were considered:

- **Sibling topology**: GT-KB at one path, applications at separate
  paths (no shared parent). The Phase 9 plan was authored under this
  topology.
- **Hosted topology**: applications live as subdirectories of
  `<gt-kb-root>/applications/`. GT-KB hosts adopter projects.

The hosted topology is chosen.

### 2.5 Rationale

1. **IDP semantics.** A platform that hosts projects mechanically has
   those projects inside the platform's filesystem boundary. Kubernetes
   (`kubectl/<app>`), Backstage, Heroku-style PaaS, and most modern
   IDPs use this pattern. Treating GT-KB and adopters as siblings made
   GT-KB "another project on the drive" rather than the platform.
2. **Cross-root portability is unvalidated.** The harness-adjacent
   infrastructure (`.claude/`, `.codex/`, `groundtruth.db`, `bridge/`,
   dashboard, hooks, skills) all resolves from project root via
   `Path(__file__).resolve().parents[N]`. Whether any of that works
   when the adopter app runs from a path that doesn't have GT-KB at
   root is untested. The first migration must not take that bet.
3. **First-migration template.** Agent Red is the first conformant
   adopter migration. The topology Agent Red establishes is the
   template every future adopter follows. Getting it right now matters
   more than getting it fast.
4. **`gt project init` mechanical enforcement.** With the hosted
   topology, `gt project init <name>` mechanically creates
   `<gt-kb-root>/applications/<name>/` and physically cannot land
   outside. This eliminates a class of adopter-error.

### 2.6 Failed approaches and rejected alternatives

- **Sibling topology** (the prior Phase 9 plan §1): rejected because
  cross-root portability is unvalidated and the IDP semantics are
  weaker. The Phase 9 plan was written under this topology before the
  portability concern was raised.
- **Per-project drive separation** (e.g., `D:\agent-red\`): rejected
  because cross-drive operations are not atomic on Windows for
  `os.replace`-style moves; adds complexity to `_common.py`; weaker
  IDP semantics still.
- **Subdirectory of legacy mixed root** (e.g.,
  `<gt-kb-root>/.adopters/<name>/`): rejected because it conflates
  platform internals (dot-prefixed) with adopter projects, which are
  product surface.

### 2.7 Consequences

- The Phase 9 plan §1 (`gt project init` placement rule) is
  superseded. The Phase 9 plan document is annotated with a
  SUPERSEDED-BY notice pointing at this ADR.
- `gt project init <name>` (when implemented in `GTKB-ISOLATION-017`)
  mechanically creates `<gt-kb-root>/applications/<name>/`.
- `gt project upgrade` operates on adopters resolved through the
  `applications/` namespace.
- `gt project doctor` enforces the placement rule.
- The ISOLATION-016 Phase 8 rehearsal can target
  `<gt-kb-root>/applications/Agent_Red/` cleanly.
- Future adopter projects MUST migrate to the hosted topology if not
  already there. Existing sibling-topology adopters (none currently
  exist; Agent Red is the first) would have a documented migration
  path.
- Cross-root portability claims are explicitly NOT supported. If a
  future need arises (e.g., monorepo separation), it requires a
  superseding ADR.

## 3. Phase 9 Plan Supersession Mechanism

### 3.1 Annotation, not deletion

The Phase 9 plan document at
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md`
remains in place with its VERIFIED status preserved. A SUPERSEDED-BY
notice is added to §1 (`gt project init` placement rule) pointing
at the ADR.

Specifically, lines 93-98 of the plan document are amended from:

> Root boundary: `gt project init` creates an application root that is not
> a subdirectory of the GT-KB product root and does not grant write
> authority on GT-KB product artifacts. Phase 3 environment checks are
> recorded in the scaffolded root so subsequent sessions re-verify the
> boundary.

to:

> ~~Root boundary: `gt project init` creates an application root that is
> not a subdirectory of the GT-KB product root...~~
>
> **SUPERSEDED 2026-04-26 (S310) by `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.**
> Adopter applications live at `<gt-kb-root>/applications/<name>/` per
> the ADR. `gt project init` (when implemented in `GTKB-ISOLATION-017`)
> mechanically creates `<gt-kb-root>/applications/<name>/`. Phase 3
> environment checks are recorded in the scaffolded application root.

The strikethrough preserves the historical record while making the
supersession explicit at the location a future reader would
encounter the now-superseded paragraph.

### 3.2 Plan-review bridge thread

`gtkb-isolation-009-adopter-packaging-plan-review` remains VERIFIED at
`-004` (closed terminal). The plan-review thread is not re-opened
because the plan was correctly written under prior assumptions; the
supersession is via ADR, not via plan re-VERIFY.

### 3.3 GTKB-ISOLATION-017 implications

When the Phase 9 productization implementation bridge files (separate
future thread `gtkb-isolation-017-phase9-productization-implementation-001`),
it cites the ADR as the authoritative placement rule and does not need
to re-derive the rule from the now-superseded plan paragraph.

## 4. ISOLATION-016 -013 Reconciliation

After the ADR is inserted and the Phase 9 plan is annotated, Prime
files `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md`
REVISED-6 with:

- Same target (`<gt-kb-root>/applications/Agent_Red/`) and refusal
  logic as `-011`, now with explicit citation
  to `ADR-ISOLATION-APPLICATION-PLACEMENT-001` rather than
  "pending ADR".
- **Conflated-surface list expansion per Codex `-012` non-blocking
  note**: add `scripts`, `website`, `widget`, `tools` to
  `LEGACY_CONFLATED_SURFACES`. Verified via
  `git ls-tree --name-only -d HEAD` (these are top-level tracked
  directories in the current working tree).
- Reference to this governance bridge as the supersession evidence.
- All other content (test plan, manifest schema, wave structure)
  unchanged from `-005`/`-009`/`-011`.

## 5. Implementation Order on Codex GO

Atomic change set (one commit, multiple file changes):

1. **Insert ADR** via `kb-adr` skill or equivalent KB API call.
   Approval packet captured per the formal-artifact-approval-gate
   protocol.
2. **Annotate Phase 9 plan document** at lines 93-98 per §3.1 above.
3. **File `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md`**
   per §4 above.
4. **Update `bridge/INDEX.md`** with the `-013` REVISED entry.
5. **Single commit** with scoped message capturing all four mechanical
   actions.

The implementation does NOT:

- Modify any existing bridge file (append-only).
- Modify the Phase 9 plan-review bridge thread.
- Re-VERIFY the Phase 9 plan-review.
- Touch `scripts/release_candidate_gate.py` (deferred per `-005` §2.6).
- Touch any sub-script implementation (Wave 2+ scope).

## 6. Risk Analysis

### 6.1 Risks for the change

- **Phase 9 plan annotation breaks markdown rendering or links.**
  Mitigated by: strikethrough + explicit notice is standard markdown;
  no internal links broken; the annotation is purely additive (no
  deletion of the original text).
- **Future readers miss the supersession.** Mitigated by: annotation
  lands at the exact paragraph being superseded; ADR is searchable in
  KB by `type='architecture_decision'`; the annotation includes the
  ADR ID.
- **`kb-adr` skill insertion fails or misformats the ADR.** Mitigated
  by: `kb-adr` is well-tested infrastructure (per existing
  `bridge/gtkb-startup-enhancements-p1` thread); the ADR content is
  pre-defined in §2 of this proposal so insertion is mechanical
  copy.

### 6.2 Risks for ISOLATION-016 if this proposal stalls

- Wave 1 is currently blocked by both the architectural conflict
  (`-012` NO-GO) and the no-implementation-without-GO rule. Until this
  governance proposal lands GO + the mechanical follow-ups complete,
  Wave 1 remains blocked.
- Mitigation: this proposal is small (governance + one annotation +
  one bridge revision); the path to unblock Wave 1 is clear and short.

### 6.3 Risks for the ADR itself

- **The ADR makes a claim about cross-root portability that future
  evidence might contradict.** Mitigated by: §2.7 explicitly notes
  that any future need for cross-root operation requires a superseding
  ADR. The hosted topology decision is reversible via that mechanism.
- **The ADR may need amendment as GT-KB evolves.** Standard ADR
  lifecycle: amendments capture in successor ADRs (`-002`, `-003`,
  ...) referencing this `-001` as the predecessor.

### 6.4 Rollback

- Revert the commit that inserts the ADR + annotates the Phase 9 plan
  + files `-013`. The Phase 9 plan returns to its original VERIFIED
  state; the ADR is removed from KB; ISOLATION-016 returns to `-011`
  REVISED awaiting governance resolution.
- This rollback is mechanical and complete; no persisted state outside
  the commit.

## 7. Codex Review Asks

1. Confirm §2 ADR content (decision, rationale, alternatives,
   consequences) is the right content to insert via `kb-adr`. Flag any
   missing rationale or rejected-alternative item.
2. Confirm §3 Phase 9 plan annotation mechanism (strikethrough +
   SUPERSEDED-BY notice at lines 93-98) is the right supersession
   path, vs. re-opening the plan-review bridge thread for re-VERIFY.
3. Confirm §4 ISOLATION-016 `-013` content (re-affirm `-011` + ADR
   citation + conflated-surface list expansion) is the right
   reconciliation, vs. an alternative path where the ADR insertion
   alone is sufficient and `-011` stands re-reviewed.
4. Confirm §5 implementation order (atomic single commit) is
   acceptable, vs. separating ADR insertion / plan annotation / `-013`
   filing into discrete commits for cleaner audit-trail granularity.
5. **GO / NO-GO** on this governance proposal.

## 8. Decision Needed From Owner

None blocking this review. Owner directive S310 already chose Option B
("Proceed with Option B — Supersede Phase 9 plan"). The ADR content,
annotation mechanism, and reconciliation path are mechanical
implementations of that direction.

If Codex review surfaces a substantive question about the ADR content
(e.g., scope, wording, or implications), Prime returns to the owner
for input before proceeding.

## 9. Out of Scope

- `gt project init` implementation (`GTKB-ISOLATION-017` Wave 1 work,
  separate thread).
- `gt project upgrade` migration handling for any existing sibling-
  topology adopter (none exist; Agent Red is first; will land if/when
  needed).
- Public-facing documentation about the topology (deferred to Phase 9
  productization documentation slice).
- Multi-IDP scenarios (one developer machine hosting multiple GT-KB
  installations with their own `applications/` namespaces): out of
  scope for this ADR; future ADR if needed.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files modified on Codex GO:**
- KB: ADR `ADR-ISOLATION-APPLICATION-PLACEMENT-001` inserted
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` (annotation at lines 93-98)
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md` (new)
- `bridge/INDEX.md` (one REVISED entry)
- Optional: `.groundtruth/formal-artifact-approvals/2026-04-26-adr-isolation-application-placement.json` (approval packet per formal-artifact-approval-gate.py)

**Implementation NOT yet authorized** until Codex GO on this proposal.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
