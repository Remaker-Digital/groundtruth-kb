NEW

# Implementation Proposal — Work-Envelope Router Umbrella Spec + DCL (Slice 1, governance_review)

bridge_kind: governance_review
Document: gtkb-work-envelope-router-slice-1-001
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
Work Item: WI-4295
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and executes no KB writes. The
two net-new artifacts drafted in this slice
(`SPEC-TOPIC-ENVELOPE-ROUTER-001` and `DCL-TOPIC-ENVELOPE-ROUTING-001`)
are inserted downstream via the active PAUTH's `approval_packet_creation`
mutation class as separate formal-artifact-approval-packet operations
after GO. (Trips `KB_MUTATION_NEGATION_RE` in
`.claude/hooks/bridge-compliance-gate.py:203-207`.)

## Claim

Define the **work-envelope router** as the thin command-surface
construct that owners use to open and close topic envelopes via the
`::open <type>` / `::close` keyword family, plus the design constraint
governing how topic-envelope state is routed to existing GT-KB services
(spec intake, build, test, deliberation, project).

This is **Slice 1** of WI-4295. It drafts the umbrella router SPEC plus
the routing DCL only. The 5 per-type SPECs (per WI-4295 status_detail's
"7 artifacts" target) are deferred to **Slice 2**, filed as a sibling
bridge thread once the umbrella's GO terminates this slice.

Two artifacts drafted in Slice 1:

1. **`SPEC-TOPIC-ENVELOPE-ROUTER-001`** — the umbrella spec defining
   the `::open <type>` / `::close` command-surface, the closed
   5-element type vocabulary `{spec, build, test, deliberation,
   project}`, the parse rule (regex `^::open (spec|build|test|deliberation|project)$`),
   the one-topic-per-type-at-a-time invariant, and the explicit
   `::close` requirement before re-opening the same type.

2. **`DCL-TOPIC-ENVELOPE-ROUTING-001`** — the routing constraint:
   activity (`type`) -> existing-service dispatch map. Each opened
   topic envelope routes its state to a named GT-KB service; the
   dispatch map is owned by this DCL and amended via formal artifact
   approval only. MEDIUM auto-close (auto-execute, never gate, per
   DELIB-2500 #2/#3/#7).

The 5 per-type SPECs (planned ids; not yet drafted: one per type in
the closed 5-vocabulary, sibling-named under WI-4295 Slice 2) provide
per-type preload sources, routing targets, and per-type harness-routing
overrides (per WI-4296 amendment). They are out of scope for Slice 1
and are recorded in Slice 2's pre-loaded design.

## Why Now

The owner's 2026-06-04 envelope-program grilling (per DELIB-20260635,
DELIB-20260637, DELIB-20260638, DELIB-20260648) formalized the work
envelope as one of the three envelope types
(dispatch / session / topic). The work-envelope router is the
command-surface side: how the owner OPENS a topic envelope inside a
session.

Today there is no canonical `::open <type>` syntax; owners use
free-form chat to start topical work. This:

- Has no machine-recognizable activator (parity gap with `::init` and
  the WI-4292 `::wrap` keyword).
- Cannot be reliably dispatched to existing services (spec intake,
  build, test, deliberation, project) without an intermediate parsing
  layer.
- Cannot leverage WI-4296's per-topic harness routing override
  feature without a typed topic envelope to attach the override to.

Slice 1 unblocks Slice 2 (per-type SPECs) and downstream WI-4301
implementation by establishing the umbrella vocabulary and routing
constraint. Slice 2 then fills in the per-type details independently
under the same PAUTH.

## Why Not (alternatives considered)

- **Single SPEC covering all 7 artifacts** (rejected for this slice):
  WI-4295 status_detail describes 7 artifacts (umbrella SPEC + DCL + 5
  per-type SPECs). A single 7-artifact proposal would be long, hard to
  review in one pass, and would conflate the umbrella design (which is
  load-bearing for the entire envelope program) with per-type details
  (which are mostly independent). Slicing umbrella-first lets the
  umbrella land cleanly and the 5 per-type SPECs land in a separate
  reviewable bundle.
- **`::open <freeform>` without closed vocabulary** (rejected per
  DELIB-20260638): would let owners invent topic types ad-hoc,
  defeating the dispatch-to-existing-service routing goal.
- **Original 8-element vocabulary `{deliberation, build, test, push,
  project, upgrade, operation}`** (rejected per DELIB-20260638
  reduction to 5): the dropped types (`ops`, `push`, `upgrade`) have
  other CLI entry points (`gt project doctor`, `gt commit`,
  `gt project upgrade`) and don't need topic-envelope wrappers.
- **MEDIUM gate-rather-than-auto-execute close** (rejected per
  DELIB-2500 #2/#3/#7): would force owner-approval for routine
  topic closes, recreating the prose-decision-ask anti-pattern. Auto-
  execute close with `wrap_outcome` capture is the correct path.
- **Multiple-topics-per-type concurrently** (rejected per WI-4295
  status_detail #3): would require per-instance routing disambiguation
  and complicate the wrap-procedure's auto-close iteration. One topic
  per type at a time keeps the model simple.

## Prior Deliberations

- `DELIB-2238` — establishes the envelope-program foundation;
  referenced by all WI-4292..WI-4297 siblings including this WI.
- `DELIB-2500` — owner directive on the MEDIUM auto-close behavior
  (#2/#3/#7): topic-envelope closes auto-execute, never gate.
- `DELIB-20260635` — originating v1.0 release-content directive;
  envelopes are headline content; work envelopes (topics) are the
  command-surface side.
- `DELIB-20260636` — envelope-program AUQ context.
- `DELIB-20260637` — 3-part envelope anatomy; work envelopes are
  routed by their type to existing services.
- `DELIB-20260638` — reduced topic-type vocabulary from 8 elements to
  5: `{spec, build, test, deliberation, project}`. Dropped types
  (`ops`, `push`, `upgrade`) have other CLI entry points.
- `DELIB-20260648` — PAUTH-minting; authorizes governance-review
  spec/DCL creation. Authorizes the per-topic harness-routing override
  feature that this slice's umbrella SPEC accommodates.
- `bridge/gtkb-canonical-init-keyword-syntax-001.md` chain (VERIFIED
  at -012) — the sibling `::init <subject> <role>` keyword; this slice
  reuses the `::` command-surface prefix discipline.
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md` (NEW, prior
  session) — the sibling `::wrap` keyword; this slice's auto-close
  behavior couples to the wrap procedure's open-topic auto-close step.
- `bridge/gtkb-envelope-dispatch-element-001-001.md` (GO at -002,
  prior session) — the dispatch-envelope schema; this slice's
  per-topic harness routing override (deferred to Slice 2 per-type
  SPECs) integrates with the dispatch-envelope element.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical
  workflow state; this proposal does not modify bridge mechanics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this
  Specification Links section satisfies the linkage gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` —
  `Project Authorization`, `Project`, and `Work Item` metadata cite
  the active PAUTH covering WI-4295.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — this proposal
  declares `requires_verification: false` because it is a
  `bridge_kind: governance_review` with `target_paths: []`; GO is
  terminal for the spec-body approval step per
  `feedback_latest_go_terminal_for_governance_review.md`. The
  Specification-Derived Verification Plan section below enumerates
  reviewer-side gates; downstream spec-insertion verification runs
  at the formal-artifact-approval-packet gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files remain
  under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` — the two downstream artifacts each
  require a formal-artifact-approval packet; those packets are
  **not** filed here.
- `GOV-STANDING-BACKLOG-001` — WI-4295 is the governing backlog item
  in `approval_state=implementation_authorized` covered by the active
  PAUTH.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — both proposed artifacts are
  governed records.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — informs artifact-oriented
  framing.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — net-new spec + DCL creation
  are lifecycle events covered by the PAUTH's
  `allowed_mutation_classes`.

**Specs referenced as symmetric peers (not modified by this proposal):**

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (VERIFIED at -012) — the
  sibling `::init <subject> <role>` keyword; the topic-envelope router
  mirrors its parse discipline (strict regex, no synonyms, machine-emit
  safety).

**Specs drafted by this proposal (downstream insert via approval packets):**

- `SPEC-TOPIC-ENVELOPE-ROUTER-001` (NEW; body drafted below).
- `DCL-TOPIC-ENVELOPE-ROUTING-001` (NEW; body drafted below).

**Sibling spec ids deferred to Slice 2 (forward references only):**

The 5 per-type SPECs that complete WI-4295's 7-artifact target are
deferred to Slice 2 (separate bridge thread filed after this slice's
GO terminates). The per-type spec ids are not cited verbatim in this
slice; Slice 2's bridge proposal names them at filing time. The
umbrella SPEC references them by WI-4295's promised 5-element type
vocabulary (the type tokens themselves: spec, build, test,
deliberation, project), with each type's per-type SPEC referenced
narratively as "the WI-4295 Slice 2 per-type SPEC for type T".

## Owner Decisions / Input

This governance-review proposal is authorized by the active PAUTH; no
fresh AUQ is required at proposal-filing time:

1. **DELIB-20260648 (envelope-program PAUTH-minting)** — owner
   approved the envelope-program spec-WI batch (WI-4291..WI-4297)
   under `bridge_kind=governance_review`. This proposal operates
   under that scope.
2. **DELIB-20260638** — owner-decided reduction to 5-element type
   vocabulary; direct authority for the umbrella SPEC's closed
   vocabulary clause.
3. **DELIB-2500 #2/#3/#7** — owner-directed MEDIUM auto-close behavior;
   authority for the DCL's auto-execute close rule.
4. **DELIB-20260637** — owner-articulated 3-part envelope anatomy;
   authority for the work-envelope's framing as one of the three
   envelope types.

Owner-input dependencies downstream of GO:

- 2 formal-artifact-approval packets at MemBase insertion time
  (umbrella SPEC + DCL).
- No source / hook / test mutation requested in this thread; the
  router implementation lands in WI-4301 (envelope-program
  implementation umbrella), a separate WI under its own
  authorization.
- Slice 2 (per-type SPECs) is a separate bridge thread filed after
  this slice's GO terminates.

## Requirement Sufficiency

Existing requirements sufficient. The owner-grilling AUQ for WI-4295
captured the complete umbrella design (closed 5-element vocabulary,
strict parse rule, one-topic-per-type invariant, MEDIUM auto-close,
per-type harness routing override accommodation); the PAUTH covers
spec+DCL creation; the sibling
`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` establishes the parse-rule
template. No new owner requirement is needed to draft and approve
this slice's umbrella SPEC and DCL.

## Spec Body — SPEC-TOPIC-ENVELOPE-ROUTER-001 (umbrella; draft)

**Title:** Work-Envelope Router Umbrella: `::open <type>` / `::close`
Command Surface and Closed Type Vocabulary.

**Type:** specification.

**Status (at insertion):** specified.

**Body:**

A **work envelope** (synonym: topic envelope) is one of the three
elements in the GroundTruth-KB envelope anatomy
(dispatch / session / topic). It scopes an owner-initiated unit of
work — a "topic" — within an active session, with a typed routing
target that maps to an existing GT-KB service.

**Open keyword:** the canonical machine-and-owner-recognized form is

```text
::open <type>
```

where `<type>` is drawn from the closed 5-element vocabulary:

```text
{spec, build, test, deliberation, project}
```

Strict parse: regex `^::open (spec|build|test|deliberation|project)$`.
The keyword occupies the entire first non-blank line of an owner
message; subsequent prompt content on later lines is unconstrained
and may carry the topic's payload (preload state, intent, etc.).

**Close keyword:** the canonical close form is

```text
::close
```

Strict parse: regex `^::close$`. No arguments. Closes the
currently-open topic envelope of any type (one-at-a-time invariant
below means only one is open per type).

**One-topic-per-type invariant:**

Only one topic envelope per type may be open in a session at a time.
Attempting `::open spec` when a `spec` topic is already open is a
parse-time error (or surfaces an owner-AUQ to confirm closing the
prior topic before opening the new one — implementation choice for
Slice 2 / WI-4301).

Explicit `::close` is REQUIRED before re-opening the same type. The
session-wrap procedure (per WI-4294, separate proposal) auto-closes
all open topics with `wrap_outcome=auto_closed_by_session_wrap` when
the wrap-keyword fires.

**MEDIUM auto-close (per DELIB-2500 #2/#3/#7):**

When `::close` fires, the close procedure auto-executes the topic's
dispatch (route to existing service per
`DCL-TOPIC-ENVELOPE-ROUTING-001`). The close does NOT gate on
owner-approval; the dispatch is the topic's purpose and runs
deterministically.

**Per-type harness routing override (deferred to Slice 2 per-type SPECs):**

Per WI-4296's DELIB-20260648 amendment, a topic envelope MAY carry a
per-topic `routing_override` naming a specific `harness_id` for any
dispatch envelope targeting it. The override semantics and schema are
defined by Slice 2's per-type SPECs, not by this umbrella.

**No synonyms:**

`::start <type>`, `::begin <type>`, `::end`, `::done`, etc. are NOT
recognized. One canonical pair (`::open`, `::close`) only. The 17 NL
wrap commands (per WI-4292 spec) are NOT topic-envelope triggers;
they trigger session wrap, which auto-closes open topics as a side
effect.

**Topic envelope state (deferred to Slice 2 / WI-4293):**

The state shape of a topic envelope is defined by the sibling
WI-4293 spec (envelope.json schema). This umbrella SPEC only defines
the COMMAND SURFACE that creates and destroys topic envelopes; the
PERSISTENT STATE layout is the schema spec's concern.

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — `.claude/rules/canonical-terminology.md` contains a
   glossary entry for "work envelope" or "topic envelope" once Slice
   2 lands. Expected-failing at this slice's insertion.
2. `grep_absent` — no automation outside the envelope-program
   surfaces a competing `::open` / `::close` parser. (Cross-checks
   against archived substrates.)

## Spec Body — DCL-TOPIC-ENVELOPE-ROUTING-001 (draft)

**Title:** Topic-Envelope Routing: Activity-Type to Existing-Service
Dispatch Map.

**Type:** design_constraint.

**Status (at insertion):** specified.

**Body:**

The topic-envelope router MUST conform to the following routing
constraints:

1. **Activity-type to service dispatch map** (closed; amended via
   formal-artifact-approval only):

   | Type | Routed to existing GT-KB service / surface |
   |------|----------------------------------------------|
   | `spec` | spec-intake pipeline (`gt intake ...`); per-type SPEC body deferred to Slice 2 |
   | `build` | build / packaging / scaffold service; per-type SPEC body deferred to Slice 2 |
   | `test` | test execution + assertion-run service; per-type SPEC body deferred to Slice 2 |
   | `deliberation` | Deliberation Archive write path (`gt deliberations record`); per-type SPEC body deferred to Slice 2 |
   | `project` | project lifecycle service (`gt projects` family); per-type SPEC body deferred to Slice 2 |

2. **No new services:** the router MUST route to existing GT-KB
   services. Net-new services require their own spec + WI; the router
   is a thin dispatcher, not a service builder. Routing to a service
   that does not yet exist (e.g., until Slice 2 defines the build
   dispatch map in detail) is a Slice 2 implementation concern; the
   umbrella SPEC promises the routing surface.

3. **MEDIUM auto-close (per DELIB-2500 #2/#3/#7):** the close
   procedure auto-executes the dispatch to the routed service. There
   is no gate-then-dispatch path; closing IS dispatching. This is the
   "MEDIUM" choice in DELIB-2500's gating spectrum: not session-wrap
   (which is a HEAVY auto-close iterating all open topics) and not
   keystroke-level (which would be LIGHT or no-close-at-all).

4. **Dispatch map amendment:** adding a new type or routing target
   requires:
   - A new per-type SPEC under Slice 2 (or later) defining the
     per-type details and naming itself at filing time.
   - An amendment to this DCL adding the row, via a formal-artifact-
     approval packet.
   - Owner-AUQ confirming the new type (closed-vocabulary expansion
     is an owner decision).

5. **Per-type harness routing override:** the dispatch may be
   redirected to a specific `harness_id` per WI-4296's DELIB-20260648
   amendment. The override is a per-topic-envelope choice; the
   default routing remains the role-default per the dispatch-envelope
   substrate.

6. **No bare "envelope":** all router code, configuration, and
   documentation MUST qualify the term (work envelope / topic
   envelope / dispatch envelope / session envelope) per WI-4302
   meta-model ADR. Bare "envelope" in topic-router context is a
   validation warning.

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — the topic-router implementation (per WI-4301 Slice C)
   references the 5-element type vocabulary verbatim. Expected-
   failing until WI-4301.
2. `grep` — the dispatch map is encoded in
   `config/topic-router/dispatch-map.toml` (or equivalent) per
   Slice 2 / WI-4301 implementation. Expected-failing until then.

**Owner directive citation:** "S-2026-06-04 owner grilling: formalize
envelope program (WI-3468)" (per WI-4295 `source_owner_directive`).

**Related deliberations:** `DELIB-2238`, `DELIB-2500`,
`DELIB-20260635`, `DELIB-20260636`, `DELIB-20260637`, `DELIB-20260638`,
`DELIB-20260648`.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing
Preflight Subsection. Re-run after this NEW entry is added to
`bridge/INDEX.md`. Expected `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`, no
blocking clause gaps.

## Specification-Derived Verification Plan

Because this is a governance_review proposal with `target_paths: []`
and `requires_verification: false`, GO is terminal for this bridge
thread (per `feedback_latest_go_terminal_for_governance_review.md`).
No follow-on post-impl report or VERIFIED verdict is required for
the umbrella SPEC + DCL approval step.

The downstream MemBase insertions are verified at their own gates:

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type specification --id SPEC-TOPIC-ENVELOPE-ROUTER-001 --json

groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type design_constraint --id DCL-TOPIC-ENVELOPE-ROUTING-001 --json
```

Each MUST return one row at version 1 with body fingerprints matching
the respective formal-artifact-approval packets. The verification
runs at *spec-insertion* time, not at this bridge thread's review
time.

Reviewer verification of THIS bridge thread:

1. **Bridge mechanics:** `bridge/INDEX.md` has `NEW: ...-001.md` at
   the top of the `gtkb-work-envelope-router-slice-1-001` document
   entry; the file exists on disk; first line is the canonical `NEW`
   status token.
2. **Applicability preflight:** `python scripts/bridge_applicability_preflight.py
   --bridge-id gtkb-work-envelope-router-slice-1-001` returns
   `preflight_passed: true`, `missing_required_specs: []`.
3. **Clause preflight:** `python scripts/adr_dcl_clause_preflight.py
   --bridge-id gtkb-work-envelope-router-slice-1-001` returns
   `Blocking gaps: 0`.
4. **Project linkage:** `Project Authorization`, `Project`, and
   `Work Item` metadata point at the active PAUTH and the live work
   item; the WI is in the PAUTH's `included_work_item_ids`.
5. **Slice-1 scope:** reviewer confirms only the umbrella SPEC + DCL
   are drafted here; the 5 per-type SPECs (Slice 2) are explicitly
   deferred and not cited verbatim in spec bodies.
6. **Phantom-spec sweep:** every cited SPEC / GOV / ADR / DCL / PB id
   exists in the live `specifications` table, except the two
   artifacts being created here.
7. **Vocabulary closure:** the 5-element type vocabulary
   `{spec, build, test, deliberation, project}` matches DELIB-20260638
   exactly. Reviewer confirms no drift from the owner-decided set.
8. **MEDIUM auto-close semantics:** the DCL's clause #3 (MEDIUM
   auto-close) matches DELIB-2500 #2/#3/#7 verbatim in intent.
9. **No KB mutation in scope:** `kb_mutation_in_scope: false`; no
   `groundtruth.db` write is performed by this thread.

## Risk / Rollback

This proposal writes one file
(`bridge/gtkb-work-envelope-router-slice-1-001-001.md`) and inserts
one entry pair (`Document:` + `NEW:`) in `bridge/INDEX.md`. Rollback
is a single `git restore` of `bridge/INDEX.md` and `rm` of the
versioned file (or a WITHDRAWN follow-on). The downstream spec/DCL
insertions (under the approval-packet path) are separate, gated
operations governed by `GOV-ARTIFACT-APPROVAL-001`.

Slice 1 establishes the umbrella and routing constraint; Slice 2
fills in per-type details. If Slice 1's umbrella SPEC needs revision
based on Slice 2 discovery, the umbrella SPEC version can be
incremented (new approval packet) without breaking Slice 1's GO
audit trail (the bridge thread is terminal at GO; the spec rows are
versioned independently).

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted
at the top of the `gtkb-work-envelope-router-slice-1-001` document
list in `bridge/INDEX.md`; no prior version is deleted or rewritten
(append-only). `bridge/INDEX.md` remains the canonical workflow
state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — this bridge proposal is governance documentation; no
source / test / hook / configuration code is modified by this
thread.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
