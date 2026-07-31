ADVISORY

# Advisory Proposal — Advisory-Proposal-Centric Knowledge Store, Fused Project Authorization, and an Explicit Bridge-Promotion Trigger

bridge_kind: governance_advisory
Document: gtkb-advisory-proposal-dropbox-successor-and-project-lifecycle-fusion
Version: 001
Date: 2026-07-16 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2f6a0618-d857-497d-ac8c-a509f544007e
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; session-stated resolved role Prime Builder (durable registry role for harness B is Loyal Opposition); ::init gtkb pb

## Note On Authorship (transparency, not a defect claim)

This session's resolved interactive role is Prime Builder throughout (confirmed at
SessionStart and unchanged since). `file-bridge-protocol.md` documents ADVISORY
authorship as "Loyal Opposition (or owner-direction)." The work-intent claim
acquired for this thread (`python scripts/bridge_claim_cli.py claim
gtkb-advisory-proposal-dropbox-successor-and-project-lifecycle-fusion`) resolved
`acting_role: loyal-opposition` — the durable registry role for harness B, not this
session's session-stated role. Rather than silently pick whichever role happens to
fit today's authorship convention, this document is filed under the session's true
operative role (Prime Builder) with this discrepancy stated plainly. Filing
authority for this specific entry rests on the "or owner-direction" clause: the
owner directly instructed its creation in this session's transcript. Whether a
Prime-Builder-resolved session may author ADVISORY entries at all — and whether
role attribution should follow session-stated role or claim-resolved durable role —
is itself an open question this proposal's scope touches (see "Open Questions"
below). This note exists so a future reader does not need to reconstruct the
ambiguity from first principles.

## Source

Owner-directed live conversation in this interactive session
(`2f6a0618-d857-497d-ac8c-a509f544007e`), spanning several turns on 2026-07-16.
The owner articulated a combined proposal covering: (1) an Advisory-Proposal-first
capture model, (2) fused project creation/authorization, (3) an explicit
bridge-promotion trigger, and (4) treated backlog items as strictly
implementation-track (not general-purpose observation capture). Across the
conversation the owner corrected and refined three of the assistant's initial
readings; those corrections are preserved verbatim below rather than smoothed over,
per the owner's own stated concern about controlled, traceable correction of past
positions.

## Owner's Proposal (preserved close to verbatim, in the order stated)

> All not-for-immediate-implementation work must begin as an advisory proposal -
> the advisory proposal includes (or may) investigation results, research and
> deliberation with the owner about a possible implementation program, references
> to specifications and deliberations, (etc.) but it is not implementable.
> Advisory Proposals replace the dropbox and other private/non-canonical
> knowledge markdown documents. Advisory Proposals are the canonical store for
> all information and knowledge that does not fit neatly in any other SoT.
>
> All backlog items are on the path to implementation proposals. The owner may
> choose to initiate an implementation program by referring a PB "build" envelope
> to one or more existing Advisory Proposals and requesting a grill-me-for-
> clarification session. This session may result in the creation of one or more
> projects with child work items. These are approved for implementation at the
> time of creation, but remain in the backlog. Promotion of a project to the
> bridge protocol begins the active implementation. This promotion to the bridge
> protocol is usually triggered by the owner, but it may also be done on the
> owner's behalf as a means of automating the incremental development of a large
> body of work.
>
> The contents of Advisory Proposals are formally tracked and advisory proposals
> are canonical.

Motivation, stated directly by the owner: "I am actively trying to eliminate the
CODEX-INSIGHT-DROPBOX." And, separately, framing the priority of this whole
proposal: "GT-KB is becoming difficult to change, and clarification of the work
paths through the system will help defeat regression drift... controlled change is
very important: un-doing past decisions in a structured and controlled way is the
most difficult problem that GT-KB now faces, and it is a fundamental capability
that bars us from commercial release of GT-KB." The owner also disclosed that
several recent deliberations may contain erroneous owner responses ("I regularly
make input or reasoning errors") — naming controlled, traceable correction as the
underlying design requirement, not merely dropbox cleanup as an end in itself.

## Two Owner Corrections To The Assistant's Initial Reading (preserved precisely)

1. **Advisory-vs-backlog boundary.** The assistant's first framing treated
   general-purpose hygiene observations as ordinary `gt backlog add` rows. The
   owner corrected this: "'legitimately low-priority captures' should be Advisory
   Proposals, such as hygiene WIs (WI-5303–5324) that are genuinely just tracked
   observations." This names, by direct example, eight work items this same
   session filed as MemBase `work_items` rows that — under the corrected model —
   should instead have been Advisory Proposals: WI-5303, WI-5304, WI-5305, WI-5319,
   WI-5320, WI-5322, WI-5324 (WI-5321/5323 were not filed by this session; the
   range is inclusive of gaps). The underlying findings remain valid; the artifact
   TYPE was wrong.

2. **What "canonical" means for an Advisory Proposal.** The assistant initially
   assumed "canonical" implied `GOV-ARTIFACT-APPROVAL-001`'s owner-approval-packet
   ceremony (the gate that blocks GOV/SPEC/PB/ADR/DCL writes). The owner corrected
   this precisely: "An advisory proposal is canonical in the same way a NEW
   artifact is canonical. It represents a step in a workflow and is the output of
   an LLM." I.e., canonical the way a bridge `NEW` proposal is canonical — freely
   authored by any LLM, permanently tracked and auditable from the moment of
   filing, but with no pre-write owner sign-off gate. Review/disposition happens
   after filing, not before.

## Prior Art — This Is A Named, Deferred Follow-On, Not A Novel Idea

Two independent, directly on-point prior decisions were found via mandatory
duplicate-search before drafting this advisory:

- **`DELIB-202665483`** (2026-07-06, owner-approved scope for
  `PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW`): *"Insights-dropbox
  disposition cleanup is explicitly excluded and remains a separate follow-on
  project."* That umbrella project (and ten active named sub-projects:
  envelope-scaffold, advisory-scanner-helper, deliberation-advisory-proposal-skill,
  prime-advisory-intake-skill, activity-profile-surfacing, investigation-scoping,
  test-parity-coverage, role-startup-scaffolds, deliberation-build-envelope-
  profiles, test-11408-assertion-coverage) already built the `advisory-proposal`,
  `advisory-intake`, and `advisory-disposition` skills currently available in this
  harness. This proposal IS the named follow-on that umbrella deferred.
- **`DELIB-20260715-ADVISORY-PROPOSALS-BRIDGE-SOT-DROPBOX-NONCANONICAL`**
  (2026-07-15, a SEPARATE interactive session, `prime-builder/codex/A`, session
  `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`): the owner already independently
  established, one day earlier and with a different harness, that "advisory
  proposals are part of the bridge protocol" and "the insight dropbox is not a
  source of truth, is not change controlled, and is not a durable storage location
  for future use." That same record documents a concrete incident matching the
  owner's stated "controlled undo" concern: *"The prior wrap note for session
  019f5f66... over-promoted the two dropbox advisory files; this decision
  corrects the carry-forward interpretation."* This is not a hypothetical risk —
  it already happened once, one day before this conversation.

This advisory's job is to consolidate: the 2026-07-06 umbrella built the
mechanism; the 2026-07-15 Codex session established the dropbox-non-canonical
principle; this session's conversation adds the missing pieces — fused
project-creation/authorization, an explicit bridge-promotion trigger, the
backlog-vs-advisory boundary rule, and a concrete finding about Deliberation
Archive's own correction mechanics.

## Current-State Findings (verified this session, with evidence)

### 1. Project creation and authorization are fully decoupled today

`gt projects create` accepts only descriptive metadata (name, id, rank, parent,
purpose, target-outcome, scope-note, dates, notes) — zero authorization-related
flags. `gt projects authorize` is a fully separate command, callable at any later
time, with independently-chosen scope: either an enumerated `included_work_item_ids`
list (the restrictive case — confirmed via `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-
RESTRICTIVE-001`, VERIFIED, to cover 229 of 235 active PAUTHs, ~97%) or an empty
list falling back to active project membership (the minority ~3% case, which
`DELIB-20266083`, 2026-06-25, deliberately preserved rather than closing). Because
creation and authorization are separated in both time and scope, a project
authorized broadly on day one can accumulate new work items indefinitely that
silently inherit that old grant with zero re-review. `WI-5324` (filed this
session) tracks the resulting visibility gap for the empty-list case; per the
owner's boundary correction above, WI-5324 itself is a candidate for reclassifying
as an Advisory-Proposal-sourced observation rather than a standalone backlog row.
The owner's proposed model ("approved for implementation at the time of
creation") closes this by construction — authorized scope becomes exactly the set
of work items grilled into existence at that moment — rather than needing an
audit bolt-on.

### 2. There is no dedicated "promotion to bridge" trigger today

`gt projects --help` has no `promote` verb. Filing a bridge proposal is Prime
Builder's own discretionary authoring act, gated only by: the WI-project-membership
check (`DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`, confirmed live in
`.claude/hooks/bridge-compliance-gate.py` `_wi_project_membership_gap()`), a
work-intent claim, and applicability/clause preflights. Which work item enters
the bridge, and when, is fully decentralized — decided by whichever Prime Builder
session chooses to draft a proposal for it, informed by backlog priority ordering
but not gated by any owner-facing "go" signal distinct from having authorized the
project at some possibly-distant earlier point. The owner's proposed explicit
promotion event (usually owner-triggered, occasionally delegated for large
incremental bodies of work) names a real mechanism that does not currently exist.

### 3. Deliberation Archive supports append-only correction, but with two specific gaps

Corrected finding (the assistant's first pass on this was imprecise and the owner
pushed back correctly): deliberations ARE versioned per-id
(`UNIQUE(id, version)`, `_next_deliberation_version` = `MAX(version)+1`,
`groundtruth-kb/src/groundtruth_kb/db.py:915-939,8631-8634`), and every reader —
`get_deliberation` (documented "latest version by default"), `search_deliberations`
(re-fetches each matched id via `get_deliberation` before returning), and the
SQLite LIKE fallback — resolves to the latest version. So "append a corrected
version, do not delete the original, the correction becomes current truth going
forward" already works for a SAME-id correction. What is genuinely missing:

- No dedicated status value for "obsolete"/"superseded." The `outcome` column is
  a fixed enum (`go | no_go | deferred | owner_decision | informational | None`)
  with no such value — a correction today would overload `informational` or rely
  on unstructured prose, which is not machine-queryable.
- No cross-ID relational link, unlike `work_items` and `project_authorizations`
  (both of which carry `supersedes`/`superseded_by` fields). Same-id versioning
  handles "I said X, I was wrong, here is the correction to that same decision."
  It does not handle two DIFFERENT ids that are substantively related/evolving —
  exactly the `DELIB-S347` (2026-05-13) / `DELIB-20266083` (2026-06-25)
  relationship found this session, which required manual full-text reading to
  discover; nothing would have surfaced it mechanically.

## Resolved Owner Decisions (this session, via AskUserQuestion)

- **Backlog-capture path** (the assistant's "statement 2" framing): owner selected
  "Keep current design" — general backlog capture (`gt backlog add`) remains valid
  and is not being replaced wholesale by Advisory Proposal. This is refined, not
  contradicted, by the owner's later correction above: the boundary is
  implementation-track work (backlog) vs. tracked-but-not-yet-implementation-track
  observations (Advisory Proposal) — not "Advisory Proposal replaces backlog
  entirely."

## Open Questions (explicitly unresolved — do not treat as decided)

1. **PAUTH revocation on project-membership change ("statement 3").** The AUQ on
   this question was interrupted mid-answer by a scheduled task firing; the
   recorded answer is `[No preference]`, which is evidence of an interrupted
   exchange, not a considered owner decision. Under the fused
   creation-equals-authorization model this question may become moot for NEW
   projects (scope is fixed at grilled creation time), but it remains open for
   EXISTING projects carrying the empty-list/membership-fallback pattern unless
   the new model also defines a migration/reconciliation path for them.
2. **Who authors an ADVISORY entry when the citing session is Prime-Builder-
   resolved but owner-directed.** See "Note On Authorship" above — the claim
   mechanism and the documented convention point toward Loyal Opposition
   authorship; this session's actual operative role was Prime Builder throughout.
3. **Reconciliation with the existing `PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-
   WORKFLOW` umbrella.** That project's already-built skills
   (`advisory-proposal`, `advisory-intake`, `advisory-disposition`) were scoped to
   ADVISORY *intake and routing*, not to redefining project-creation semantics or
   adding a promotion-trigger mechanism. Should this proposal's implementation
   land as a new follow-on project under that umbrella, or as its own sibling
   project? Should the existing skills be extended in place, or superseded?
4. **Disposition of `WI-5303`–`WI-5324`** (this session's hygiene backlog rows
   that the owner's correction retroactively re-scopes as Advisory-Proposal
   material). Migrate now, once the mechanism exists, or leave as a grandfathered
   legacy pattern with a note?
5. **Advisory Proposal's formal-artifact-approval boundary.** The owner clarified
   "canonical like NEW, not canonical like GOV" — confirmed no per-entry
   owner-approval-packet gate at write time. Does anything downstream (disposition
   into a project, promotion to bridge) reintroduce an approval gate, and precisely
   where?

## Recommended Next Action

Per the owner's own described workflow: a Prime Builder "build" envelope should be
referred to this Advisory Proposal (and to the two prior-art deliberations cited
above) and a `/grill-me-for-clarification` session run to resolve the five open
questions above before any implementation proposal is drafted. That skill already
exists in this harness and is the correct mechanism the owner named. This advisory
intentionally stops short of drafting an implementation proposal, a specification,
or a work item — per the owner's own phased model, that is the grilling session's
output, not this document's.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied
Yes — this advisory recommends a governance-architecture change touching project
creation/authorization semantics, bridge-entry mechanics, the Deliberation Archive
schema, and the disposition of an existing dropbox artifact class. It requires new
or amended DCL/spec records and source changes (e.g., project create/authorize
command fusion, a promotion-trigger surface, deliberation schema additions) before
any implementation proposal can exist.

### Grill-the-owner questions
Prime Builder must obtain durable AUQ-recorded answers to the five Open Questions
listed above, plus:
6. Should `gt projects create` and `gt projects authorize` remain separate CLI
   verbs with the fusion enforced procedurally (grilling session always calls
   both in one transaction), or should they become a single command/transaction
   at the code level?
7. For the Deliberation Archive gap: is a same-id `outcome=superseded` enum value
   sufficient, or is a cross-id `supersedes`/`superseded_by` field pair (matching
   `work_items`/`project_authorizations`) required, or both?

### Required durable owner decisions
The following AUQ answers must exist before an implementation proposal can be
filed:
- Resolution of Open Questions 1–5 above.
- Resolution of grill-questions 6–7 above.
- Explicit scope boundary: does this implementation program also retire/migrate
  `CODEX-INSIGHT-DROPBOX` content, or only stop future writes to it?

## Non-Approval Statement

This advisory is NOT implementation approval. It does not open an
implementation-start packet, authorize protected edits, or bypass the bridge,
project-authorization, owner-decision, root-boundary, credential-safety,
formal-artifact, or verification gates. Any derived implementation proposal
requires a normal Prime Builder proposal, independent Loyal Opposition GO, a
matching work-intent claim, and implementation-start authorization before any code
or schema change.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this advisory and any derived proposal remain
  in the numbered bridge lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the diagnosis and proposal are
  preserved as durable artifacts.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` — the owner-grilling obligation
  applied above for an adopt/adapt-shaped recommendation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — governs the current
  project-authorization semantics this proposal would amend.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` — the current restrictive/
  fallback scope semantics cited in Finding 1.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` — the current
  bridge-citation membership gate cited in Finding 2.
- `GOV-STANDING-BACKLOG-001` — governs the backlog-vs-advisory boundary this
  proposal refines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all evidence and any fix remain
  under `E:/GT-KB`.

## Prior Deliberations

- `DELIB-202665483`, `DELIB-202665486` — the 2026-07-06 owner decisions scoping
  `PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW` and explicitly deferring
  dropbox disposition as a follow-on.
- `DELIB-20260715-ADVISORY-PROPOSALS-BRIDGE-SOT-DROPBOX-NONCANONICAL` — the
  2026-07-15 owner correction (separate session/harness) establishing Advisory
  Proposals as bridge-protocol artifacts and the dropbox as explicitly
  non-canonical, including a documented over-promotion correction incident.
- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` (2026-05-13) — the
  friction-reduction rationale for automatic backlog intake; explicitly rejected
  "treat every backlog item as implementation authorization" as an alternative.
- `DELIB-20266083` (2026-06-25) — the most recent PAUTH-scope-tightening
  decision; chose restrictive list semantics but deliberately preserved the
  empty-list membership-fallback behavior.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` (2026-06-30) — retired
  individual work-item approval state in favor of project-level approval; adjacent
  context for how "approval" is currently modeled.
- Deliberation search performed before drafting (`gt deliberations search`, three
  distinct queries covering inheritance semantics, revoke-on-add semantics, and
  backlog-vs-advisory boundary) returned no other directly duplicating record.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner directly instructed creation of this Advisory Proposal in this session's
  transcript (2026-07-16), citing the priority rationale quoted in "Owner's
  Proposal" above.
- The backlog-capture-path question was separately resolved via AskUserQuestion
  this session ("Keep current design") and is recorded as a Resolved Owner
  Decision above.
- The PAUTH-revocation-on-add question ("statement 3") was NOT resolved — the AUQ
  was interrupted; this is recorded as Open Question 1 and must not be treated as
  decided.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
