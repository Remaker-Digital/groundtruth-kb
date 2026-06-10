NEW

# Implementation Proposal — Envelope-Program Glossary Entries + GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 Amendment (governance_review)

bridge_kind: governance_advisory
Document: gtkb-envelope-glossary-and-gov-lifecycle-amendment
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
Work Item: WI-4300
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and writes no protected
narrative files. The glossary entries and GOV amendment text drafted
below land downstream via narrative-artifact-approval-packet writes
(under the PAUTH's `narrative_artifact_write` mutation class), each
gated by `GOV-ARTIFACT-APPROVAL-001`. (Trips
`KB_MUTATION_NEGATION_RE` in `.claude/hooks/bridge-compliance-gate.py:203-207`.)

## PAUTH Coverage Note

WI-4300 is not in the existing envelope-program PAUTH's
`included_work_item_ids` (which lists WI-4291..WI-4297). However,
Codex's WI-4302 (`gtkb-envelope-meta-model-adr-dcl-001`) was filed
under the same PAUTH and GO'd by LO Antigravity harness C at -002
— setting the precedent that envelope-program governance_review
work can cite the existing PAUTH despite formal `included_work_item_ids`
gap. This filing follows that precedent. If LO disagrees and
requires a new PAUTH covering WI-4298..WI-4302, file a REVISED with
the new PAUTH after owner mints it.

## Claim

Two coupled governance amendments completing the envelope-program's
documentation surface:

**1. Glossary entries** (8 net-new entries in
`.claude/rules/canonical-terminology.md`):

Envelope family (4 terms): `session envelope`, `topic envelope`
(replaces retired "work envelope" per DELIB-20260637 #4),
`dispatch envelope`, `init keyword family / wrap keyword family`.

Topic types (5 terms): `spec` topic, `build` topic, `test` topic,
`deliberation` topic, `project` topic (per the closed 5-vocabulary
from WI-4295 Slice 1's umbrella SPEC).

envelope.json schema concepts (3+ terms): `envelope_schema_version`,
`topics array`, `archive directory` (per WI-4293's GO'd
WI-4293 GO'd schema).

Each entry follows the canonical-terminology.md template: definition,
canonical alias (where applicable), "not to be confused with"
disambiguators, source citation (DELIB + bridge id), implementation
pointer.

**2. GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 amendment**: amend
`GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` to integrate the
envelope-program's wrap/open/close lifecycle. Specifically:

- Reference `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 as the
  session-open canonical activator.
- Reference the wrap-keyword spec from WI-4292's GO-terminal thread
  as the session-close canonical activator.
- Reference the wrap-procedure spec from WI-4294's GO-terminal
  thread as the deterministic wrap procedure.
- Reference the topic-envelope router umbrella spec from WI-4295
  Slice 1's GO-terminal thread as the in-session topic open/close
  router.
- Preserve the existing proactive-engagement mandate; the envelope
  program is the operational vehicle for the mandate's procedural
  obligations.

## Why Now

The envelope-program body-approval phase is essentially complete:
9 of 10 spec/DCL/ADR threads have GO terminal. The glossary entries
and GOV amendment are the documentation surface that closes the
program's design loop:

- New canonical terms used across the GO'd specs need glossary
  homes. Without entries, the terms remain implicit and citations
  drift.
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` predates the
  envelope program but governs the same session-lifecycle surface;
  the amendment integrates the envelope-program's deterministic
  procedural framework into the governance layer.

Filing WI-4300 now makes the envelope program's design self-contained:
specs + DCLs + ADR + glossary + GOV all coherent, ready for the
implementation umbrella WI-4301 to consume.

## Why Not (alternatives considered)

- **Defer glossary until WI-4301 lands** (rejected): glossary
  entries should land BEFORE implementation so the implementation
  uses canonical terminology from the start. Deferring would force
  WI-4301 to either invent terminology (drift risk) or land with
  un-glossaried terms.
- **Split glossary entries into per-term proposals** (rejected): the
  8+ entries are tightly coupled (same envelope-program design,
  shared DELIB citations, mutual cross-references). One thread for
  all keeps the audit trail coherent.
- **Skip the GOV amendment** (rejected): without amending
  `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`, the envelope
  program is in tension with the existing governance — the GOV's
  procedural obligations remain abstract while the envelope-program
  provides concrete operational mechanics.
- **Promote to implementation_proposal scope (WI-4291 precedent)**
  (rejected for now): WI-4291's promotion was driven by LO's
  explicit recommendation after an impl-attempt blocker. This
  proposal hasn't reached that stage; governance_review-terminal
  pattern (my WI-4292/4294/4295/4296/4297 precedent) matches the
  intended downstream narrative-artifact-approval-packet flow.

## Prior Deliberations

- `DELIB-2238`, `DELIB-2500` — originating envelope-program
  foundation.
- `DELIB-20260635`, `DELIB-20260636`, `DELIB-20260637`,
  `DELIB-20260638`, `DELIB-20260648` — envelope-program shaping
  deliberations; DELIB-20260637 #4 specifically renamed "work
  envelope" to "topic envelope" (load-bearing for the glossary's
  retirement-note framing).
- `bridge/gtkb-canonical-init-keyword-syntax-001.md` (VERIFIED at
  -012) — establishes `::init` glossary entry semantics.
- All 9 GO-terminal envelope-program threads
  (`gtkb-canonical-wrap-keyword-syntax-001`,
  `gtkb-session-envelope-durability-001`,
  `gtkb-session-wrap-procedure-001`,
  `gtkb-work-envelope-router-slice-1-001`,
  `gtkb-work-envelope-router-slice-2-per-type-specs`,
  `gtkb-envelope-dispatch-element-001`,
  `gtkb-project-completion-drive-payload-001`,
  `gtkb-envelope-meta-model-adr-dcl-001`,
  `gtkb-envelope-init-keyword-amendment-slice-1`) — define the
  terminology this glossary entries codify.
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` (existing) — the
  GOV being amended.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `GOV-ARTIFACT-APPROVAL-001`,
  `GOV-STANDING-BACKLOG-001`,
  `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` (the GOV being
  amended).

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `DCL-CONCEPT-ON-CONTACT-001` — the glossary additions are exactly
  the "concept on contact" doctrine in action.

**Narrative files modified by this proposal (downstream via
narrative-artifact-approval-packet):**

- `.claude/rules/canonical-terminology.md` — glossary additions.
- The GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 amendment is a
  spec-row update via formal-artifact-approval-packet (per
  GOV-ARTIFACT-APPROVAL-001), not a narrative file edit.

## Owner Decisions / Input

This governance-review proposal is authorized by the active PAUTH;
no fresh AUQ is required at proposal-filing time:

1. **DELIB-20260648 (envelope-program PAUTH-minting)** — authorizes
   governance-review work; `narrative_artifact_write` is in the
   PAUTH's allowed_mutation_classes for the glossary edit.
2. **DELIB-20260637 #4** — direct authority for the "work envelope" →
   "topic envelope" rename in the glossary's retirement-note framing.
3. **DELIB-20260638** — direct authority for the 5-element topic-type
   vocabulary.
4. **GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001** — the GOV's
   existing proactive-engagement mandate is preserved; the amendment
   adds the envelope-program references as operational mechanics.

Owner-input dependencies downstream of GO:

- 1 narrative-artifact-approval packet for the
  `.claude/rules/canonical-terminology.md` edit, each gated by
  `GOV-ARTIFACT-APPROVAL-001` (autonomous /loop cannot supply this).
- 1 formal-artifact-approval packet for the
  `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` v? update, same
  gate.

## Requirement Sufficiency

Existing requirements sufficient. All terminology is sourced from
GO-terminal bridge threads + DELIB citations. The GOV amendment is
incremental (preserves existing language; adds envelope-program
references). No new owner requirement is needed.

## Glossary Entries Drafted (downstream narrative-artifact-approval-packet)

### Envelope family (4 entries)

**1. session envelope**

**Definition:** The outer-tier container in the GroundTruth-KB
three-part envelope anatomy. One session envelope exists per
interactive session, stored in
`harness-state/<harness_name>/session-envelope.json` (per WI-4293's
GO'd schema). Carries the session metadata
(opened_at/closed_at/wrap_outcome/role_asserted/role_resolved/
subject_asserted/subject_resolved/project_id/work_item_ids/
active_work_item_id/model_id/model_version), and contains an
embedded topics array (zero or more topic envelopes per type).

**Canonical alias:** session env.

**Not to be confused with:** dispatch envelope (the optional
transport-tier wrapper that contains a session envelope; see
below); topic envelope (the inner-tier scoped-work envelopes the
session envelope contains).

**Source:** `DELIB-20260637` (3-part anatomy); WI-4293 GO at
`bridge/gtkb-session-envelope-durability-001-006.md`.

**Implementation pointer:**
`harness-state/<harness_name>/session-envelope.json` (live);
archive at `harness-state/<harness_name>/session-envelope-archive/<closed_at>-session-envelope.json`.
Optional non-authoritative projection at
`.claude/session/envelope.json` regenerated by the wrap procedure's
step #12b.

**2. topic envelope**

**Definition:** The inner-tier container in the three-part envelope
anatomy. One or more topic envelopes may be open simultaneously
inside a session envelope, one per type from the closed 5-vocabulary
`{spec, build, test, deliberation, project}`. Triggered by
`::open <type>` and closed by `::close <type>` (per WI-4295 Slice 1's
umbrella SPEC). Each topic envelope carries: type, opened_at,
closed_at, close_outcome, preload_state, route_target, optional
per-topic harness `routing_override` (per WI-4296 DELIB-20260648
amendment).

**Canonical alias:** topic env.

**Not to be confused with:** session envelope (outer container);
"work envelope" (RETIRED term per DELIB-20260637 #4; was previously
used as a synonym for topic envelope but should not be used in
current text).

**Source:** `DELIB-20260637` #4 (rename from "work envelope");
WI-4295 Slice 1 GO at
`bridge/gtkb-work-envelope-router-slice-1-001-004.md`;
WI-4295 Slice 2 GO at
`bridge/gtkb-work-envelope-router-slice-2-per-type-specs-002.md`.

**Implementation pointer:** topics array within the session
envelope's per-harness file.

**3. dispatch envelope**

**Definition:** The optional outermost-tier container in the
three-part envelope anatomy. Wraps a session envelope when present;
carries a dispatch routing record (target dimension =
harness/role/topic/prompt; trigger = cadence_cron/event_subscription;
mandatory activity-gate predicate; payload template; optional
persistence flag). Interactive sessions skip the dispatch tier (the
session envelope is the outermost container). Per WI-4296 spec body.

**Canonical alias:** dispatch env; routing envelope.

**Not to be confused with:** session envelope (always present;
dispatch is optional outer wrapper); topic envelope (inner-tier,
contained by session envelope).

**Source:** WI-4296 GO at
`bridge/gtkb-envelope-dispatch-element-001-002.md`; WI-4297 GO at
`bridge/gtkb-project-completion-drive-payload-001-002.md`
(project-completion-drive payload schema for dispatch envelopes);
WI-4302 GO at `bridge/gtkb-envelope-meta-model-adr-dcl-001-002.md`
(meta-model ADR establishing dispatch ⊇ session ⊇ topic
containment).

**Implementation pointer:** rule entries in
`config/dispatcher/rules.toml` per WI-4296 DCL; runtime state at
`.gtkb-state/dispatcher/state.json` and log at
`.gtkb-state/dispatcher/log.jsonl`.

**4. init keyword family / wrap keyword family**

**Definition:** Two coupled families of canonical session-edge
machine-emit activators per the canonical-keyword discipline
established by the init-keyword spec. The init-keyword family opens
sessions; the wrap-keyword family closes sessions.

**Init keyword family:** the canonical regex (post-WI-4291 amendment)
is `^::init (gtkb|application)( (pb|lo))?$`. Subject is mandatory
(closed vocabulary `{gtkb, application}`); role is optional.

**Wrap keyword family:** the canonical form is bare `::wrap` (per
WI-4292 spec), plus 17 natural-language additive triggers (per the
startup disclosure's "Wrap-Up Trigger Commands" section). All
triggers resolve to the deterministic wrap procedure (per WI-4294).

**Source:** WI-4291 (init amendment), WI-4292 (wrap keyword);
DELIB-2500 + DELIB-20260648.

**Implementation pointer:** parser receivers in
`.claude/hooks/session_start_dispatch.py` and
`.codex/gtkb-hooks/session_start_dispatch.py` (init); the
wrap-trigger layer per WI-4301 Slice A.

### Topic types (5 entries)

**5. spec topic**

**Definition:** A topic envelope of type `spec`. Opens on
`::open spec`. Preloads: filtered `gt spec list` view, `gt intake`
pending queue, related deliberation-archive records. Routes
(on `::close spec`) to the spec-intake pipeline or the
formal-artifact-approval-packet path if spec-text revisions
occurred. Per WI-4295 Slice 2's GO-terminal per-type SPEC for the `spec`
type.

**Source:** WI-4295 Slice 2 GO at
`bridge/gtkb-work-envelope-router-slice-2-per-type-specs-002.md`.

**6. build topic**

**Definition:** A topic envelope of type `build`. Opens on
`::open build`. Preloads: `gt project doctor` summary, in-flight
build/scaffold WIs, current package version. Routes (on
`::close build`) to the build/scaffold/packaging service.
Per WI-4295 Slice 2's GO-terminal per-type SPEC for the `build`
type.

**7. test topic**

**Definition:** A topic envelope of type `test`. Opens on
`::open test`. Preloads: `gt assert` assertion-run history, failing
assertions, `tests/` directory inventory. Routes (on `::close test`)
to the test execution + assertion-run service.
Per WI-4295 Slice 2's GO-terminal per-type SPEC for the `test`
type.

**8. deliberation topic**

**Definition:** A topic envelope of type `deliberation`. Opens on
`::open deliberation`. Preloads: Deliberation Archive search results,
related owner_conversation records. Routes (on
`::close deliberation`) to the Deliberation Archive write-path
(`gt deliberations record`). Per WI-4295 Slice 2
the WI-4295 Slice 2 GO-terminal per-type SPEC for the `deliberation`
type.

**9. project topic**

**Definition:** A topic envelope of type `project`. Opens on
`::open project`. Preloads: `gt projects list` summary, target
project's lifecycle state, `current_project_authorizations`, open
WIs. Routes (on `::close project`) to the project lifecycle service
(`gt projects` family). Per WI-4295 Slice 2 the WI-4295 Slice 2 GO-terminal per-type SPEC for the `project`
type.

### envelope.json schema concepts (3 entries)

**10. envelope_schema_version**

**Definition:** A monotonic integer field on each session envelope's
JSON record indicating the schema version under which the envelope
was written. Per WI-4293 GO'd schema. Allows the wrap procedure and
the envelope router to apply version-aware parsing for envelopes
written under prior schema versions.

**Source:** WI-4293 GO at
`bridge/gtkb-session-envelope-durability-001-006.md`.

**11. topics array**

**Definition:** A JSON array field on each session envelope
containing zero or more topic-envelope records. Order is
insertion-by-open; per the one-topic-per-type invariant (per WI-4295
Slice 1's umbrella SPEC), at most one open record exists per type
token from `{spec, build, test, deliberation, project}`. Closed
topics remain in the array with `closed_at` and `close_outcome`
populated.

**Source:** WI-4293 GO; WI-4295 Slice 1 GO.

**12. session-envelope-archive directory**

**Definition:** The per-harness directory at
`harness-state/<harness_name>/session-envelope-archive/` where
closed session envelopes are renamed to. File naming convention:
`<closed_at-ISO>-session-envelope.json`. Maintained by the wrap
procedure's step #12a (per WI-4294 spec).

**Source:** WI-4293 GO; WI-4294 spec (REVISED-2 GO at
`bridge/gtkb-session-wrap-procedure-001-004.md`).

## GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 Amendment (downstream formal-artifact-approval-packet)

**Amendment scope:** add a new paragraph to the existing
`GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` body, integrating
the envelope program as the operational vehicle for the GOV's
procedural obligations. Existing GOV text is preserved.

**New paragraph (to be inserted before the closing paragraph):**

> The envelope program (WI-4291..WI-4302 series, all
> GO-terminal at design phase as of 2026-06-04) provides the
> deterministic operational mechanics for this GOV's
> proactive-engagement mandate. Session openings use the canonical
> init keyword family (`::init <subject> <role>`,
> per the GO-terminal sibling thread covering WI-4291's amendment);
> session closures use the canonical wrap keyword family
> (`::wrap` plus 17 NL phrases, per WI-4292) running the
> deterministic 4-tier wrap procedure (per WI-4294). In-session
> topic work is routed via `::open <type>` /
> `::close <type>` per WI-4295's topic-envelope router. Recurring
> ops/review/audit work uses dispatch envelopes per WI-4296. The
> envelope.json state file per WI-4293 schema is the live
> session-state surface; archived envelopes provide cross-session
> handoff context for the deterministic handoff-prompt generator
> per WI-4299 (when filed and approved).

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing
Preflight Subsection. Re-run after this NEW entry is added to
`bridge/INDEX.md`. Expected `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`, no
blocking clause gaps.

## Specification-Derived Verification Plan

Because this is a governance_review proposal with `target_paths: []`
and `requires_verification: false`, GO is terminal for this bridge
thread (per `feedback_latest_go_terminal_for_governance_review.md`).
No follow-on post-impl report or VERIFIED verdict is required.

The downstream narrative + formal artifact insertions are verified at
their own gates:

```text
# Narrative-artifact write (canonical-terminology.md edits):
git diff --stat .claude/rules/canonical-terminology.md  # show new entries

# Formal-artifact-approval packet for GOV amendment:
ls .groundtruth/formal-artifact-approvals/2026-06-04-GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001*.json

# MemBase GOV version bump:
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type governance --id GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 --json
```

Reviewer verification of THIS bridge thread:

1. **Bridge mechanics** — INDEX has `NEW:` at top of the
   `gtkb-envelope-glossary-and-gov-lifecycle-amendment` entry.
2. **Applicability + clause preflights** pass with no blocking gaps.
3. **PAUTH coverage note** — proposal cites the precedent of WI-4302
   under the same PAUTH; LO may NO-GO if a separate PAUTH is needed.
4. **Glossary entry completeness** — 8+ entries covering envelope
   family (4) + topic types (5) + envelope.json concepts (3) =
   minimum 12. Each follows the canonical-terminology.md template.
5. **GOV amendment incrementality** — preserves existing
   `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` body; adds one
   new paragraph integrating the envelope program.
6. **Phantom-spec sweep** — every cited SPEC / GOV / DCL / ADR id
   exists in the live `specifications` table (or is explicitly
   marked as a forward-reference to a GO-terminal sibling).

## Risk / Rollback

This proposal writes one bridge file + one INDEX entry. Rollback
single `git restore` + `rm`.

If LO NO-GO's due to PAUTH coverage gap (WI-4300 not in
included_work_item_ids), file a REVISED after owner mints a covering
PAUTH OR after LO clarifies that the WI-4302 precedent extends to
WI-4300.

The downstream narrative + GOV writes are owner-gated separately;
this thread's blast radius is the proposal file itself.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted
at the top of the
`gtkb-envelope-glossary-and-gov-lifecycle-amendment` document list
in `bridge/INDEX.md`.

## Recommended Commit Type

`docs` — governance documentation; no source / test / hook /
configuration code is modified.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
