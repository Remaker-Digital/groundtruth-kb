NEW

# Implementation Proposal — Envelope-Program Implementation Umbrella Capstone (governance_review)

bridge_kind: governance_review
Document: gtkb-envelope-implementation-umbrella-capstone
Version: 001
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 35ed98f8-ae1c-4a5f-bf3f-219c579f144e
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous /loop dynamic mode

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4301
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_scoping_capstone
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation. It is a SCOPING capstone
that defines the implementation plan; the actual code work is
spawned in 5 sub-WIs at implementation kickoff, each with its own
implementation_proposal bridge thread.

## PAUTH Coverage Note

WI-4301 is not in the envelope-program PAUTH's
`included_work_item_ids` (WI-4291..WI-4297). Codex's WI-4302 and my
WI-4298/4299/4300 filings under the same PAUTH established the
coverage-gap-precedent pattern; this filing follows it.

The PAUTH covers governance_review scoping work. Each sub-WI
(A-E) spawned at impl kickoff will require ITS OWN PAUTH covering
the impl scope (source-code writes, hook mutations, test additions)
— that's owner-decision territory and not within this thread's
scope.

## Claim

Capstone of the envelope-program design phase. WI-4301 is the
implementation umbrella that:

1. Defines the 5 implementation slices (A-E) that together build
   the envelope program runtime.
2. Establishes the sequencing gate: implementation kickoff requires
   all 7 spec WIs (WI-4291..WI-4297) at terminal-verdict-state per
   the bridge protocol.
3. Specifies the sub-WI lifecycle: sub-WIs are spawned at
   implementation kickoff (not pre-created), each filing its own
   implementation_proposal bridge thread.
4. Preserves the topic-envelope terminology per DELIB-20260637 #4
   and WI-4300's glossary entries.

This is a **scoping capstone**, not an implementation proposal. The
GO terminal on this thread authorizes the impl-kickoff workflow;
each sub-WI's actual implementation runs under its own thread's
GO + impl-start packet flow.

## Sequencing-Gate Clarification

WI-4301's status_detail (drafted 2026-06-04 in the per-WI grill)
expresses the sequencing gate as "ALL 7 spec WIs (WI-4291..WI-4297)
must reach bridge-VERIFIED before WI-4301 implementation starts."

The envelope-program reality (as of 2026-06-04 envelope-program
filing window):

- The 6 of 7 governance_review threads (WI-4292, WI-4293, WI-4294,
  WI-4295 Slice 1, WI-4295 Slice 2, WI-4296, WI-4297) are at
  **GO-terminal** state, not VERIFIED. The governance_review pattern
  with `target_paths: []` and `requires_verification: false` makes
  GO terminal (per the
  `feedback_latest_go_terminal_for_governance_review.md` auto-memory).
- WI-4291 has a different trajectory: its REVISED-3 at -005 is the
  impl_proposal scope (target_paths populated; kb_mutation_in_scope:
  true) that GO'd at -006. Its post-impl report at -007 records a
  block waiting on owner-evidence; LO at -008 NO-GO'd the report
  intentionally to preserve the blocked state until owner-presented
  approval packets arrive.

**Sequencing-gate interpretation for impl kickoff:**

The gate is satisfied when each spec WI has reached its terminal
bridge verdict (whether GO-terminal for governance_review threads or
VERIFIED for full impl-cycle threads). The "bridge-VERIFIED" wording
in WI-4301's status_detail predates the GO-terminal pattern's
establishment and should be read as "terminal verdict".

WI-4291 is a special case: its impl-cycle is owner-evidence-pending.
For sub-WI A (markers + state writer; depends on WI-4291 +
WI-4293), the implementing PB session must verify that WI-4291's
spec content is owner-approved at packet creation BEFORE running
the actual SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 v3 insert.

WI-4298 (disclosure UI) and WI-4299 (handoff service) — both
governance_review GO-terminal — "MAY lag" per WI-4301 status_detail:
sub-WI E (disclosure UI + handoff service) does NOT block other
sub-WIs but DOES require WI-4298 + WI-4299 terminal verdicts at
sub-WI E kickoff (both currently satisfied).

WI-4302 (meta-model ADR/DCL; Codex's filing) and WI-4300 (glossary;
mine) — both GO-terminal — are referenced by all sub-WIs for
terminology + meta-model framing.

## 5 Implementation Slices

### Slice A — Markers + State Writer

**Scope:** UserPromptSubmit recognition of canonical init/wrap/
open/close keywords + the per-harness session-envelope.json state
writer.

**Spec dependencies (must be terminal verdict at sub-WI kickoff):**

- WI-4291: `::init <subject> <role>` recognition (impl_proposal
  scope; owner-evidence-pending at packet level).
- WI-4292: `::wrap` recognition (governance_review GO-terminal).
- WI-4293: per-harness session-envelope.json schema
  (governance_review GO-terminal; parallel session's filing).
- WI-4295 Slice 1 + Slice 2: `::open <type>` / `::close <type>`
  recognition + the 5 per-type token tokens (governance_review
  GO-terminal).

**Target files (illustrative; finalized at sub-WI A's
implementation_proposal):**

- `.claude/hooks/session_start_dispatch.py` (Claude Code init
  hook).
- `.codex/gtkb-hooks/session_start_dispatch.py` (Codex parity).
- `groundtruth-kb/src/groundtruth_kb/session/envelope_writer.py`
  (new module).
- Tests: `tests/scripts/test_envelope_writer.py` + parser tests
  per existing test conventions.

### Slice B — Wrap Procedure

**Scope:** Deterministic `::wrap` -> 4-tier procedure runner per
WI-4294's GO'd 12-step framework. Includes handoff-prompt service
invocation per WI-4299.

**Spec dependencies:** WI-4294 (procedure spec; GO-terminal),
WI-4293 (state file), WI-4299 (handoff service contract;
GO-terminal).

**Target files (illustrative):**

- `groundtruth-kb/src/groundtruth_kb/session/wrap.py` (new module).
- `groundtruth-kb/src/groundtruth_kb/session/handoff.py` (new
  module; per WI-4299).
- CLI subcommands: `gt session handoff generate`, `gt session
  handoff get`.
- Tests: `tests/scripts/test_wrap_procedure.py`,
  `tests/scripts/test_handoff_service.py`.

### Slice C — Topic-Envelope Router

**Scope:** `::open <type>` / `::close <type>` recognition + per-type
preload sources + service dispatch per the routing map in
WI-4295 Slice 1's DCL.

**Spec dependencies:** WI-4295 Slice 1 (umbrella + DCL;
GO-terminal), WI-4295 Slice 2 (5 per-type SPECs; GO-terminal).

**Target files (illustrative):**

- `groundtruth-kb/src/groundtruth_kb/session/topic_router.py` (new
  module).
- `config/topic-router/dispatch-map.toml` (per the DCL clause #1
  asserting registry location).
- Tests: `tests/scripts/test_topic_router.py`.

### Slice D — Dispatcher

**Scope:** `config/dispatcher/rules.toml` loader + hot-reload +
activity-gated scheduler + project-completion drive (per WI-4296
+ WI-4297). The dispatcher integrates with the existing
cross-harness event-driven trigger.

**Spec dependencies:** WI-4296 (dispatch-envelope element schema;
GO-terminal), WI-4297 (project-completion drive payload + AUQ
marker; GO-terminal).

**Target files (illustrative):**

- `groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py`
  (new module).
- `groundtruth-kb/src/groundtruth_kb/dispatcher/scheduler.py` (new
  module).
- `config/dispatcher/rules.toml` (initial empty file under the
  DCL's registry-location clause).
- `.gtkb-state/dispatcher/state.json` (activity-gate state per
  WI-4296 spec).
- Tests: `tests/scripts/test_dispatcher_*.py`.

### Slice E — Disclosure UI + Handoff Service

**Scope:** Open disclosure refactor (`scripts/session_self_initialization.py`)
per WI-4298 contract + close disclosure rendering per WI-4298 close
shape + integration with handoff service (WI-4299).

**Spec dependencies:** WI-4298 (disclosure UI redesign; GO-terminal),
WI-4299 (handoff service; GO-terminal), WI-4300 (glossary +
GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 amendment;
GO-terminal).

**Target files (illustrative):**

- `scripts/session_self_initialization.py` (refactor; per
  WI-4298's open-disclosure shape).
- `groundtruth-kb/src/groundtruth_kb/session/close_renderer.py`
  (new module for the per-step JSON + terminal summary).
- Backlog state: WI-3467 marked `superseded_by=WI-4298` at sub-WI
  E completion.

## Sub-WI Lifecycle (Spawning Convention)

At implementation kickoff, the implementing PB session does NOT
pre-create sub-WIs (A-E) in MemBase. Each sub-WI is created when its
slice is ready to enter the bridge cycle:

1. PB session opens an `::open spec` topic envelope (per WI-4295
   Slice 1's umbrella) for the slice.
2. Within the topic, drafts a SPEC for the slice's behavioral
   contract (if not already covered by the GO'd governance_review
   threads) and / OR drafts an implementation_proposal bridge thread.
3. On `::close spec`, MemBase records the slice's sub-WI under
   PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT with
   appropriate naming (e.g., `WI-4301-A-markers-and-state-writer`).
4. Sub-WI lifecycle proceeds: NEW proposal → LO review → GO →
   implement → post-impl → VERIFIED.

This convention is per WI-4301 status_detail #3 ("Sub-WI lifecycle:
sub-WIs (A-E) are spawned at impl kickoff (not pre-created now)").

## Terminology

Per DELIB-20260637 #4 and WI-4300's glossary entries (GO-terminal):

- The construct previously called "work envelope" is renamed
  **"topic envelope"** in all current text. The retired term
  appears only in historical-note framing.
- "Topic-envelope router" (not "work-envelope router") is the
  canonical name for the in-session topic open/close mechanism.
- "Session envelope" is the outer-tier per-harness container.
- "Dispatch envelope" is the optional outermost transport wrapper.

This proposal's text uses "topic envelope" exclusively in current-
text references; "work envelope" appears only in this paragraph's
historical-note framing (consistent with WI-4300's
retirement-note convention).

## Why Now

The envelope-program governance_review phase is essentially complete
(12 of 13 WIs have at least body-approval GO terminal). WI-4301 is
the natural capstone:

- All spec dependencies (WI-4292..WI-4300 + WI-4302) are at
  terminal verdict state.
- WI-4291 is in owner-evidence-pending state; sub-WI A may proceed
  to draft impl_proposal scope without blocking on WI-4291's
  packet-level resolution (the sub-WI cites WI-4291's GO'd -006
  spec body).
- Filing the umbrella capstone closes the design-phase loop and
  sets up the next-session-or-owner implementation phase with a
  clear plan.

## Why Not (alternatives considered)

- **Pre-create the 5 sub-WIs in MemBase now** (rejected per owner
  AUQ #3): sub-WI lifecycle convention explicitly defers creation
  to impl kickoff. Pre-creating bloats the standing backlog with
  not-yet-actionable rows.
- **File WI-4301 as implementation_proposal** (rejected): the
  umbrella defines the implementation plan but does NOT itself
  authorize source-code mutation. Each sub-WI does that under its
  own PAUTH and impl_proposal scope. governance_review-terminal-at-GO
  is the correct framing for this scoping capstone.
- **Defer WI-4301 until WI-4291's owner-evidence resolves**
  (rejected): WI-4291's pending state does not block the umbrella
  capstone's scoping work. Sub-WI A may proceed once impl kickoff
  starts; WI-4291's resolution feeds into sub-WI A's actual spec
  insertion (separate concern from this umbrella).
- **Include sub-WI A's impl_proposal scope in this umbrella**
  (rejected): umbrella is governance_review; sub-WI work is
  impl_proposal. Mixing scope in one thread defeats the layered
  approval discipline.

## Prior Deliberations

- `DELIB-2238`, `DELIB-2500` — originating envelope-program
  foundation.
- `DELIB-20260635`, `DELIB-20260636`, `DELIB-20260637`,
  `DELIB-20260638`, `DELIB-20260648` — envelope-program shaping
  deliberations.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — implementation
  Slice B and Slice D adhere to the deterministic-services
  principle.
- All 12 envelope-program GO-terminal bridge threads:
  `gtkb-canonical-wrap-keyword-syntax-001`,
  `gtkb-session-envelope-durability-001`,
  `gtkb-session-wrap-procedure-001`,
  `gtkb-work-envelope-router-slice-1-001`,
  `gtkb-work-envelope-router-slice-2-per-type-specs`,
  `gtkb-envelope-dispatch-element-001`,
  `gtkb-project-completion-drive-payload-001`,
  `gtkb-envelope-meta-model-adr-dcl-001`,
  `gtkb-envelope-glossary-and-gov-lifecycle-amendment`,
  `gtkb-handoff-prompt-deterministic-service`,
  `gtkb-envelope-disclosure-ui-redesign`,
  `gtkb-envelope-init-keyword-amendment-slice-1` (special: GO at
  -006, then -008 NO-GO preserving owner-evidence-pending state).

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `GOV-ARTIFACT-APPROVAL-001`,
  `GOV-STANDING-BACKLOG-001`,
  `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` (amended by
  WI-4300; the operational mechanics defined here are the vehicle
  for this GOV's proactive-engagement mandate),
  `GOV-SESSION-SELF-INITIALIZATION-001` (the open-disclosure
  governance baseline that Slice E refactors operationally).

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `DCL-CONCEPT-ON-CONTACT-001`.

**Specs referenced (forward references; sibling WIs):**

All 12 envelope-program WIs' specs are forward-references; their
spec ids are provisional until insertion (downstream of each WI's
own formal-artifact-approval packet). The capstone references them
by sibling WI id per the established convention.

**Specs drafted by this proposal:**

None directly. This is a scoping capstone; sub-WIs draft their own
specs at impl kickoff.

## Owner Decisions / Input

This governance-review scoping proposal is authorized by the active
PAUTH; no fresh AUQ is required:

1. **DELIB-20260648** — envelope-program PAUTH-minting; covers
   governance_review scoping under
   `narrative_artifact_write +
   approval_packet_creation +
   bridge_report_write +
   deliberation_record_create +
   work_item_lifecycle_update`.
2. **WI-4301 status_detail owner AUQ** — direct authority for the
   5-slice partition + sequencing-gate semantic + sub-WI lifecycle
   convention.

Owner-input dependencies downstream of GO:

- Each sub-WI's impl_proposal will require ITS OWN PAUTH covering
  the impl scope (source-code writes, test mutations, hook changes,
  CLI extensions). The existing envelope-program PAUTH does NOT
  cover those mutation classes; a new PAUTH per sub-WI (or a
  consolidated implementation PAUTH) is required at impl kickoff
  (owner-decision territory).

## Requirement Sufficiency

Existing requirements sufficient. The 5-slice partition is captured
in WI-4301 status_detail. The sequencing-gate semantic is
clarified in this proposal's "Sequencing-Gate Clarification"
section (which reconciles the status_detail's "bridge-VERIFIED"
wording with the established GO-terminal pattern). No new owner
requirement is needed for the capstone.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing
Preflight Subsection. Re-run after this NEW entry is added to
`bridge/INDEX.md`. Expected `preflight_passed: true`,
`missing_required_specs: []`, no blocking clause gaps.

## Specification-Derived Verification Plan

Because this is a governance_review scoping proposal with
`target_paths: []` and `requires_verification: false`, GO is
terminal for this bridge thread.

Reviewer verification of THIS bridge thread:

1. **Bridge mechanics** — INDEX has `NEW:` at top of the
   `gtkb-envelope-implementation-umbrella-capstone` document
   entry.
2. **Applicability + clause preflights** pass with no blocking gaps.
3. **PAUTH coverage note** — follows the established
   coverage-gap-precedent pattern.
4. **5-slice partition completeness** — all 5 slices (A-E) match
   WI-4301 status_detail #1 exactly; each slice's spec
   dependencies are listed.
5. **Sequencing-gate clarification** — reconciles "bridge-VERIFIED"
   status_detail wording with GO-terminal pattern; WI-4291's
   owner-evidence-pending state is acknowledged explicitly.
6. **Sub-WI lifecycle convention** — matches status_detail #3.
7. **Terminology preservation** — "topic envelope" used
   exclusively in current text; "work envelope" only in
   historical-note framing.
8. **No source-code targets** — this proposal does NOT propose
   source-code mutations directly; all impl work is deferred to
   sub-WI impl_proposals.

## Risk / Rollback

This proposal writes one bridge file + one INDEX entry. Rollback
single `git restore` + `rm`.

If LO disagrees with the sequencing-gate clarification (e.g.,
insists on literal bridge-VERIFIED for all 7 spec WIs before any
sub-WI may proceed), file a REVISED REVISED with the alternate
gate semantic. Note that literal VERIFIED requires each
governance_review thread to go through a post-impl + VERIFIED
cycle — which is NOT supported by the GO-terminal pattern. The
clarification is therefore load-bearing.

If LO disagrees with the sub-WI lifecycle convention (e.g., prefers
pre-creation), file a REVISED with pre-created sub-WIs. Note that
pre-creation contradicts WI-4301 status_detail #3.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted
at the top of the
`gtkb-envelope-implementation-umbrella-capstone` document list in
`bridge/INDEX.md`.

## Recommended Commit Type

`docs` — governance documentation; no source / test / hook /
configuration code is modified by this thread.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
