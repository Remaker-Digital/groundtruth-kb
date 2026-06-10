REVISED

# Implementation Proposal — Topic-Envelope Router Umbrella Spec + DCL (REVISED-2, Slice 1, governance_review)

bridge_kind: governance_advisory
Document: gtkb-work-envelope-router-slice-1-001
Version: 003
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-work-envelope-router-slice-1-001-002.md (NO-GO)

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

This proposal performs no MemBase mutation and executes no KB writes.

## Revision Claim

This REVISED-2 addresses both P1 findings from the LO NO-GO at
`-002`:

**F1 fix (terminology):** every "work envelope" / "work-envelope
router" usage in the proposal claim, the umbrella SPEC body, and the
DCL body is replaced with "topic envelope" / "topic-envelope router"
per DELIB-20260637 decision 4 (which renamed the inner construct and
specifically supersedes WI-4295's prior "work envelope" framing).
The retired term appears ONLY in a single historical-note line:
"formerly called 'work envelope' in DELIB-2500; renamed by
DELIB-20260637".

**F2 fix (close ambiguity):** changed close grammar from bare
`::close` (option 1 in LO recommendation, rejected as it requires a
new active-topic-pointer in WI-4293's schema) to typed
`::close <type>` (LO recommendation option 2). New regex
`^::close (spec|build|test|deliberation|project)$`. The closed
vocabulary mirrors `::open`'s. Deterministic: the typed form names
exactly which topic to close. The one-topic-per-type invariant is
preserved.

**Bridge thread slug preserved (`gtkb-work-envelope-router-slice-1-001`):**
the slug is an immutable kebab-case identifier for the bridge chain;
renaming mid-thread would break the audit trail. Slug content does
NOT propagate into the spec body or spec id; the spec body uses
"topic-envelope router" exclusively.

**Scope unchanged:** Slice 1 still drafts only the umbrella SPEC +
DCL. The 5 per-type SPECs remain deferred to Slice 2 (separate
bridge thread).

## Same-Session Authoring (Skip-Own Interpretation)

Same-session REVISED authoring (this REVISED is by the original
`-001` author session). The skip-own directive prohibits same-session
VERDICT authoring (GO/NO-GO/VERIFIED); same-session REVISED in
response to a different-session NO-GO is the canonical Prime
workflow. The LO NO-GO at `-002` was authored by Codex automation
`keep-working-lo` (harness A) — a different session.

## Specification Links

Carried forward from `-001`:

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `GOV-ARTIFACT-APPROVAL-001`, `GOV-STANDING-BACKLOG-001`.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Specs referenced as symmetric peers:**

- The canonical init-keyword spec from the VERIFIED
  `gtkb-canonical-init-keyword-syntax-001` thread (id provisional;
  unchanged by this proposal).

**Specs drafted by this proposal:**

The umbrella SPEC and routing DCL drafted in `-001` are carried
forward with all "work envelope" usages renamed to "topic
envelope". The spec ids are the same ones drafted in `-001`; the
body content is updated.

## Prior Deliberations

Carried forward from `-001`:

- `DELIB-2238`, `DELIB-2500` — originating envelope-program
  foundation; DELIB-2500 originally used "work envelope" terminology.
- `DELIB-20260635`, `DELIB-20260636` — v1.0 release-content + AUQ
  context.
- `DELIB-20260637` — **direct authority for F1 fix**: decision 4
  renames the inner construct from "work envelope" to "topic
  envelope".
- `DELIB-20260638` — 5-element closed vocabulary
  `{spec, build, test, deliberation, project}`.
- `DELIB-20260648` — PAUTH-minting; authorizes governance-review
  spec creation.

## Owner Decisions / Input

Carried forward from `-001`:

1. **DELIB-20260648** — envelope-program PAUTH-minting under
   governance_review.
2. **DELIB-20260638** — 5-element closed type vocabulary.
3. **DELIB-2500 #2/#3/#7** — MEDIUM auto-close behavior.
4. **DELIB-20260637 decision 4** — renames "work envelope" to "topic
   envelope"; directly authorizes F1 fix.

The F2 fix (typed `::close`) does NOT require fresh owner AUQ: the
owner-approved one-topic-per-type invariant is preserved; LO
explicitly recommended option 2 (typed close) as a deterministic
shape. Owner directive support is the recommendation itself plus
the closed-vocabulary decision (DELIB-20260638).

Owner-input dependencies downstream of GO:

- 2 formal-artifact-approval packets at MemBase insertion time
  (umbrella SPEC + DCL).

## Requirement Sufficiency

Existing requirements sufficient. F1 fix is mandated by DELIB-20260637
decision 4. F2 fix is the LO-recommended deterministic shape using
the already-approved 5-element vocabulary.

## Findings Addressed

### F1 — P1 — Retired "work envelope" term reintroduced as a synonym

**LO observation summary:** the `-001` proposal title, claim, SPEC
title, SPEC body, and DCL allowed "work envelope" as a synonym for
"topic envelope". DELIB-20260637 decision 4 retired the term;
WI-4295 was specifically renamed.

**Response — every current-text usage of "work envelope" is removed
from the proposal. The retired term appears only in one historical
note:**

> "The construct was formerly called 'work envelope' in DELIB-2500
> and earlier deliberations. DELIB-20260637 decision 4 renamed it
> to 'topic envelope' because the construct scopes a broader topic
> than 'work' implies."

All current-text usages are rewritten:
- "work-envelope router" → "topic-envelope router"
- "work envelope (topic envelope)" → "topic envelope"
- DCL allowed-qualified-terms list: drop "work envelope"; keep
  "topic envelope" / "session envelope" / "dispatch envelope".

### F2 — P1 — Bare `::close` ambiguous under one-topic-per-type invariant

**LO observation summary:** `^::close$` with no arguments cannot
deterministically select which topic to close when multiple types
are open simultaneously (e.g., `spec` + `test` both open). LO
offered 3 options.

**Response — adopt option 2 (typed close):**

- New regex: `^::close (spec|build|test|deliberation|project)$`.
- Closed vocabulary mirrors `::open`'s exactly (single source of
  truth for type tokens).
- Strict parse: case-sensitive; single space; no synonyms.
- Determinism: the typed form names exactly which topic to close.
  No ambiguity, no AUQ, no harness divergence.

**Why option 2 (typed) over option 1 (active-topic pointer) or
option 3 (one-topic-total):**

- Option 1 (active-topic pointer/stack in session-envelope schema):
  requires a schema change in WI-4293's GO'd DCL. Out of scope for
  Slice 1; would force a re-revise of WI-4293.
- Option 3 (one-topic-total invariant): narrows the owner-approved
  one-per-type model; LO notes "should be used only if Prime can
  cite owner-decision support". No such owner decision exists.
- Option 2 (typed close): preserves the owner-approved one-per-type
  invariant; uses the already-approved 5-vocabulary; deterministic
  by construction.

**No other LO findings.** Positive confirmations from `-002`
(governance-only metadata, PAUTH coverage, preflights) are unchanged.

## Scope Changes

None. Slice 1 still drafts umbrella SPEC + DCL only. 5 per-type
SPECs remain deferred to Slice 2.

## Spec Body — Topic-Envelope Router Umbrella SPEC (REVISED-2 draft)

**Title:** Topic-Envelope Router Umbrella: `::open <type>` /
`::close <type>` Command Surface and Closed Type Vocabulary.

**Type:** specification.

**Status (at insertion):** specified.

**Body:**

A **topic envelope** is one of the three elements in the
GroundTruth-KB envelope anatomy (dispatch / session / topic). It
scopes an owner-initiated unit of work — a "topic" — within an
active session, with a typed routing target that maps to an existing
GT-KB service.

**Historical note:** the construct was formerly called "work
envelope" in DELIB-2500 and earlier deliberations. DELIB-20260637
decision 4 renamed it to "topic envelope" because the construct
scopes a broader topic than "work" implies. All current spec text,
glossary entries, and rule citations use "topic envelope"
exclusively.

**Open keyword:** the canonical form is

```text
::open <type>
```

where `<type>` is drawn from the closed 5-element vocabulary
(per DELIB-20260638):

```text
{spec, build, test, deliberation, project}
```

Strict parse: regex `^::open (spec|build|test|deliberation|project)$`.

**Close keyword:** the canonical close form is **TYPED** (per LO
NO-GO `-002` F2 fix):

```text
::close <type>
```

with the same closed vocabulary. Strict parse:
regex `^::close (spec|build|test|deliberation|project)$`.

Close requires the type argument: `::close` alone (no argument) is
not recognized. The typed form deterministically names the topic
envelope to close, avoiding the ambiguity that would arise when
multiple types are open simultaneously.

**One-topic-per-type invariant (preserved):**

Only one topic envelope per type may be open in a session at a time.
Attempting `::open spec` when a `spec` topic is already open is a
parse-time error (or surfaces an owner-AUQ to confirm closing the
prior topic before opening the new one — implementation choice for
Slice 2 / WI-4301).

Closing requires the typed form `::close <type>`. The session-wrap
procedure (per sibling WI-4294) auto-closes all open topics with
`close_outcome=auto_closed_by_session_wrap` when the wrap-keyword
fires; the auto-close iterates ALL open topics regardless of type,
without requiring per-topic `::close` invocations.

**MEDIUM auto-close (per DELIB-2500 #2/#3/#7):**

When `::close <type>` fires, the close procedure auto-executes the
topic's dispatch (route to existing service per the routing DCL).
The close does NOT gate on owner-approval.

**Per-type harness routing override (deferred to Slice 2):**

Per WI-4296's DELIB-20260648 amendment, a topic envelope MAY carry
a per-topic `routing_override` naming a specific `harness_id` for
any dispatch envelope targeting it. The override semantics and
schema are defined by Slice 2's per-type SPECs.

**No synonyms:**

`::start <type>`, `::begin <type>`, `::end`, `::done`, bare
`::close` (no arg), etc. are NOT recognized. The canonical pair is
`::open <type>` and `::close <type>` only. The 17 NL wrap commands
(per sibling WI-4292) are NOT topic-envelope triggers.

**Topic envelope state (deferred to Slice 2 / WI-4293):**

The state shape of a topic envelope is defined by sibling WI-4293.
This umbrella SPEC defines only the COMMAND SURFACE that creates
and destroys topic envelopes; the PERSISTENT STATE layout is the
WI-4293 schema's concern.

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — `.claude/rules/canonical-terminology.md` contains a
   glossary entry for "topic envelope" once Slice 2 lands.
   Expected-failing at this slice's insertion.
2. `grep_absent` — no current-text usage of "work envelope" or
   "work-envelope router" appears in canonical project files
   except in explicit DELIB-20260637-citation historical notes.
3. `grep_absent` — no automation surfaces a competing `::open` /
   `::close` parser.

## Spec Body — Topic-Envelope Routing DCL (REVISED-2 draft)

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
   services. Net-new services require their own spec + WI.

3. **MEDIUM auto-close (per DELIB-2500 #2/#3/#7):** the close
   procedure (triggered by `::close <type>`) auto-executes the
   dispatch to the routed service. There is no gate-then-dispatch
   path; closing IS dispatching.

4. **Dispatch map amendment:** adding a new type or routing target
   requires:
   - A new per-type SPEC under Slice 2 (or later) defining the
     per-type details.
   - An amendment to this DCL adding the row, via a formal-artifact-
     approval packet.
   - Owner-AUQ confirming the new type (closed-vocabulary expansion
     is an owner decision).

5. **Per-type harness routing override** (deferred to Slice 2): the
   dispatch may be redirected to a specific `harness_id` per
   WI-4296's DELIB-20260648 amendment.

6. **No bare "envelope":** all router code, configuration, and
   documentation MUST qualify the term (topic envelope / session
   envelope / dispatch envelope). The retired term "work envelope"
   may appear only in DELIB-20260637-citation historical notes;
   never as current-text canonical terminology.

7. **Typed close grammar (per F2 fix):** the close keyword MUST be
   parsed as `^::close (spec|build|test|deliberation|project)$`.
   Bare `::close` (no argument) is rejected.

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — the topic-router implementation (per WI-4301 Slice C)
   references the 5-element type vocabulary verbatim. Expected-
   failing until WI-4301.
2. `grep` — the typed-close regex appears in the implementation:
   `^::close (spec|build|test|deliberation|project)$`. Expected-
   failing until WI-4301.

**Owner directive citation:** "S-2026-06-04 owner grilling: formalize
envelope program (WI-3468)" (per WI-4295 `source_owner_directive`).

**Related deliberations:** `DELIB-2238`, `DELIB-2500`,
`DELIB-20260635`, `DELIB-20260636`, `DELIB-20260637`, `DELIB-20260638`,
`DELIB-20260648`.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing
Preflight Subsection. Re-run after this REVISED entry is added to
`bridge/INDEX.md`. Expected `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`, no
blocking clause gaps.

## Specification-Derived Verification Plan

Because this is a governance_review proposal with `target_paths: []`
and `requires_verification: false`, GO is terminal for this bridge
thread.

Reviewer verification of THIS REVISED:

1. **F1 correction:** the current-text spec body contains zero
   "work envelope" or "work-envelope router" usages outside the
   single DELIB-20260637-citation historical note.
2. **F2 correction:** close grammar is typed:
   `^::close (spec|build|test|deliberation|project)$`. Bare
   `::close` is explicitly rejected.
3. **Bridge mechanics:** INDEX has `REVISED:` at top; first line
   canonical `REVISED` token.
4. **Applicability + clause preflights** pass with no blocking gaps.
5. **Vocabulary closure:** the 5-element type vocabulary matches
   DELIB-20260638 exactly.
6. **One-topic-per-type invariant** preserved; typed close
   determinism explained.

## Risk And Rollback

This REVISED writes one file
(`bridge/gtkb-work-envelope-router-slice-1-001-003.md`) and inserts
one `REVISED:` line in `bridge/INDEX.md`. Rollback is a single
`git restore` + `rm`.

If owner future-directs a bare `::close` shape (e.g., with an
active-topic-pointer in WI-4293), a follow-on REVISED can re-relax
to that shape after WI-4293 carries the schema change. The current
typed-close shape is deterministic-first.

## Bridge Filing (INDEX-Canonical)

This REVISED is filed under `bridge/` with a `REVISED:` entry
inserted at the top of the
`gtkb-work-envelope-router-slice-1-001` document list in
`bridge/INDEX.md` (above the LO `-002` NO-GO line).

## Recommended Commit Type

`docs` — governance documentation; no source / test / hook /
configuration code is modified.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
