NEW

# Implementation Proposal — Canonical Wrap-Keyword Syntax for Session Close (governance_review)

bridge_kind: governance_advisory
Document: gtkb-canonical-wrap-keyword-syntax-001
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
Work Item: WI-4292
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and executes no KB writes. The
actual `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` insertion is a downstream
operation under the active PAUTH's `approval_packet_creation` mutation class
and is filed as a separate post-GO step, not part of this bridge thread.
(Trips `KB_MUTATION_NEGATION_RE` in
`.claude/hooks/bridge-compliance-gate.py:203-207`, short-circuiting
`_declares_kb_mutation` to False.)

## Claim

Establish `::wrap` as the canonical session-close keyword for GroundTruth-KB
sessions, symmetric with the init-keyword family (`::init gtkb <role>`).

Syntax: exact regex `^::wrap$`. Bare keyword, no arguments, no mode vocabulary.
The keyword occupies the entire first line of an owner message (or is the
sole content of that message). Subsequent prompt content, if present, is
unconstrained but ignored by the wrap-trigger layer.

Behavioral contract:

1. When `::wrap` is detected, the session-wrap procedure executes.
2. Before closing the session, the procedure iterates open work-envelope
   records from `.claude/session/envelope.json` and auto-closes each open
   topic with `wrap_outcome=auto_closed_by_session_wrap`.
3. The 17 natural-language wrap commands documented in the startup-disclosure
   "Wrap-Up Trigger Commands" section (`wrap up`, `session wrap-up`, etc.)
   remain additive triggers; they resolve to the same wrap procedure.

The wrap procedure itself (the deterministic sequence of steps it executes)
is the subject of sibling WI-4294 (separate spec, separate proposal,
not yet drafted); this spec defines only the keyword trigger surface and
its open-topic-auto-close obligation.

## Why Now

Per the 2026-06-04 owner grilling (envelope-program AUQ over WI-3468),
the envelope program formalizes a 3-part anatomy
(work-envelope / dispatch-envelope / session-topic) plus the deterministic
open/close action surface. The wrap-keyword spec is one of seven sibling
spec WIs (WI-4291..WI-4297) authored under
`PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297`.

Today, session wrap-up is triggered only by natural-language phrases per the
startup disclosure's "Wrap-Up Trigger Commands" list. Those phrases work
conversationally but:

- They have no canonical machine-recognizable form.
- They cannot be safely emitted by automation or other harnesses without
  ambiguity against ordinary owner prose containing the phrase fragments.
- They do not unify with the established `::` command-surface prefix used by
  `::init gtkb <role>` (the canonical init-keyword).

A canonical `::` keyword closes the gap symmetrically with init and provides
a stable machine-emit surface for dispatcher automation, while the 17 NL
phrases remain available as conversational triggers.

## Why Not (alternatives considered)

- **`::wrap <outcome>` with mode vocabulary** (rejected per DELIB-2500): would
  embed wrap-outcome semantics in the keyword. Owner directive: wrap outcome
  is captured by the wrap procedure (its open-topic-iteration + post-wrap
  report), not by the trigger keyword. The keyword stays bare.
- **`::wrap gtkb`** (parallel to `::init gtkb <role>`): would force a
  subject-mandatory shape symmetric with init. Owner refinement per
  DELIB-20260648 (the PAUTH-minting deliberation) clarified
  `subject-mandatory/role-optional` for init; for wrap, there is no role
  vocabulary, and no subject ambiguity since wrap targets the current
  session. Rejected; the bare form is correct.
- **NL phrases only (status quo)**: no canonical machine-emit surface;
  cannot be safely used by automation. Rejected.
- **`::end` / `::close` / synonyms**: expands the parse surface for no
  operational benefit. Rejected; one canonical form.

## Prior Deliberations

- `DELIB-2238` — owner-archived deliberation citing the wrap-keyword
  requirement as part of the envelope-program scope.
- `DELIB-2500` — owner decision specifying that wrap-outcome semantics are
  captured by the wrap procedure (not the keyword), and that the 17 NL
  phrases remain additive triggers.
- `DELIB-20260636` — envelope-program AUQ context referenced by WI-4292.
- `DELIB-20260637` — refined the envelope-program scope; informs the
  WI-4293/WI-4294 coupling captured in WI-4292 `status_detail`.
- `DELIB-20260648` — PAUTH-minting decision for the envelope-program spec WI
  batch (WI-4291..WI-4297). Refines DELIB-2500 #4 and DELIB-20260637 #2 with
  the subject-mandatory/role-optional clarification (init-shape); wrap is
  bare per DELIB-2500. Unblocks this filing.
- `bridge/gtkb-canonical-init-keyword-syntax-001.md` chain (VERIFIED at
  `-012`) — the sibling init-keyword bridge thread; establishes the `::`
  command-surface prefix discipline mirrored here.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical
  workflow state; this proposal is filed under the file-bridge protocol and
  does not modify bridge mechanics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this
  Specification Links section satisfies the linkage gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — `Project:` and
  `Project Authorization:` metadata cite the active PAUTH covering WI-4292.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — this proposal
  declares `requires_verification: false` because it is a
  `bridge_kind: governance_review` with `target_paths: []`; GO is terminal
  for the spec-body approval step per
  `feedback_latest_go_terminal_for_governance_review.md`. The
  Specification-Derived Verification Plan section below enumerates the
  reviewer-side gates that ARE performed in this thread; the downstream
  spec-insertion verification runs at the formal-artifact-approval-packet
  gate (a separate operation under `GOV-ARTIFACT-APPROVAL-001`).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files (this
  proposal and the future approval packet) remain under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` — the downstream
  `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` insertion will require a
  formal-artifact-approval packet; that packet is **not** filed here.
- `GOV-STANDING-BACKLOG-001` — WI-4292 is the governing backlog item and is
  in `approval_state=implementation_authorized` covered by the active PAUTH.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the proposed spec is a governed
  artifact, not a transient session file.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — informs the artifact-oriented
  framing: the wrap-keyword spec is a durable MemBase artifact (created via
  approval packet), not a procedural or transient construct.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — net-new spec creation is a
  lifecycle event covered by the PAUTH's `allowed_mutation_classes`.

**Specs referenced as symmetric peers (not modified by this proposal):**

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (VERIFIED at -012 sibling chain) —
  the init-keyword counterpart; the wrap-keyword spec mirrors its parse
  discipline (strict regex, no synonyms, machine-emit safety).
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — paired with the init-keyword
  spec; no parallel construct is needed for wrap because wrap has no role
  vocabulary and no consistency-assertion concern.

**Specs drafted by this proposal (downstream insert via approval packet):**

- `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` (NEW; body drafted below).

## Owner Decisions / Input

This governance-review proposal is authorized by the active PAUTH; no fresh
AUQ is required at proposal-filing time. The PAUTH cites the operative owner
decisions:

1. **DELIB-20260648 (envelope-program PAUTH-minting)** — owner approved the
   envelope-program spec-WI batch (WI-4291..WI-4297) under
   `bridge_kind=governance_review`, with new-spec creation authorized via
   the formal-artifact-approval-packet path. This proposal operates under
   that scope.
2. **DELIB-2238 + DELIB-2500** — the originating wrap-keyword deliberations:
   bare `::wrap`, regex `^::wrap$`, NL wrap commands remain additive
   triggers, wrap outcome captured by the procedure (not the keyword).
3. **DELIB-20260636 + DELIB-20260637 (envelope-program AUQ context)** —
   inform the WI-4293 / WI-4294 coupling and the 3-part envelope anatomy
   that contextualizes the wrap-keyword's open-topic-auto-close obligation.

Owner-input dependencies downstream of GO:

- 1 formal-artifact-approval packet at MemBase insertion time for
  `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001`.
- No source / hook / test mutation requested in this thread; those land in
  WI-4294 (wrap procedure implementation) and WI-4301 (envelope
  implementation), which are separate WIs under the same PAUTH umbrella.

## Requirement Sufficiency

Existing requirements sufficient. The owner-grilling AUQ for WI-4292 captured
the complete spec design (keyword shape, parse rule, open-topic interaction,
NL-additive-trigger relationship); the PAUTH covers spec creation; the
sibling `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` establishes the parse-rule
template. No new owner requirement is needed to draft and approve the spec
body proposed below.

## Spec Body — SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001 (draft)

**Title:** Canonical Wrap-Keyword Syntax for Session Close.

**Type:** specification.

**Status (at insertion):** specified.

**Body:**

The canonical wrap-keyword syntax for GroundTruth-KB sessions is the exact
regex `^::wrap$`. The keyword is bare: no arguments, no mode vocabulary, no
trailing whitespace, case-sensitive.

The keyword occupies the entire first non-blank line of an owner message,
and may also be the sole content of that message. Subsequent prompt content
on later lines is unconstrained and is not consumed by the wrap-trigger
layer; the wrap procedure consumes it only if it forms part of the standard
post-wrap report inputs.

Recognition contract:

1. The active AI harness's session-wrap detection logic MUST treat
   `^::wrap$` on the first non-blank line as a wrap-trigger event identical
   to the natural-language wrap phrases enumerated in the startup
   disclosure's "Wrap-Up Trigger Commands" section.
2. The 17 NL wrap commands (`wrap up`, `wrap up this session`,
   `session wrap-up`, `run session wrap-up`, `close this session`,
   `end this session`, `new session`, `fresh session`,
   `start a new session`, `start a fresh session`, `begin a new session`,
   `begin a fresh session`, `open a new session`, `prepare a new session`,
   `initialize a new session`, `start fresh`, `begin fresh`) remain
   additive triggers and continue to resolve to the same wrap procedure.
3. No synonyms (`::end`, `::close`, `::done`, `::finish`, etc.) are
   recognized. Owner-typed approximations may still hit one of the NL
   phrases but do not satisfy the canonical-keyword form.

Behavioral contract (delegated to the wrap procedure spec WI-4294):

1. On wrap-trigger, before closing the session, the wrap procedure iterates
   open work-envelope records in `.claude/session/envelope.json` and
   auto-closes each open topic with `wrap_outcome=auto_closed_by_session_wrap`.
2. The wrap procedure then executes its standard session-close steps as
   specified by sibling WI-4294 (separate proposal, not yet drafted).

Coupling:

- This spec defines only the keyword trigger surface and the open-topic
  auto-close obligation it imposes on the wrap procedure. It does not
  define the envelope.json schema (sibling WI-4293, separate proposal,
  not yet drafted) or the wrap procedure deterministic sequence (sibling
  WI-4294, separate proposal, not yet drafted).

**Note on forward references:** the spec ids that WI-4293 and WI-4294
will create (per those WI titles) are not cited verbatim in this proposal
because they are not yet drafted. The WI ids are the durable authority
during the envelope-program batch; the planned spec ids will be cited by
those siblings' own bridge proposals at filing time.

**Assertions:**

The spec carries the following machine-checkable assertions (executed by
`gt assert` and the assertion-check hook):

1. `grep` — file `.claude/rules/canonical-terminology.md` MUST contain the
   token `::wrap` and a glossary entry for the wrap-keyword (added in a
   downstream rule-file slice; not required at spec insertion time).
2. `grep` — at least one of the startup-disclosure templates under
   `config/agent-control/` MUST list `::wrap` alongside the NL wrap
   commands (downstream slice; not required at insertion time).

Both assertions ship as `status=specified` at insertion time and promote to
`status=implemented` when the downstream rule-file / startup-template slices
land. This is the standard "spec lands first, implementation follows"
discipline per `GOV-01` (spec-first) and `GOV-06` (specify-on-contact).

**Owner directive citation:** "S-2026-06-04 owner grilling: formalize
envelope program (WI-3468)" (per WI-4292 `source_owner_directive`).

**Related deliberations:** `DELIB-2238`, `DELIB-2500`, `DELIB-20260636`,
`DELIB-20260637`, `DELIB-20260648`.

**Symmetric peer specs:** `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight
Subsection. Re-run after this NEW entry is added to `bridge/INDEX.md`.
Expected `preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`, no blocking clause gaps.

## Specification-Derived Verification Plan

Because this is a governance_review proposal with `target_paths: []` and
`requires_verification: false`, GO is terminal for this bridge thread
(per `feedback_latest_go_terminal_for_governance_review.md`). No follow-on
post-impl report or VERIFIED verdict is required for the spec-body approval
step.

The downstream MemBase insertion is verified by:

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type specification --id SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001 --json
```

That command MUST return one row at version 1 with the body fingerprint
matching the formal-artifact-approval packet — but the verification runs at
*spec-insertion* time, not at this bridge thread's review time.

Reviewer verification of THIS bridge thread:

1. **Bridge mechanics:** `bridge/INDEX.md` has `NEW: ...-001.md` at the top
   of the `gtkb-canonical-wrap-keyword-syntax-001` document entry; the file
   exists on disk; first line is the canonical `NEW` status token.
2. **Applicability preflight:** `python scripts/bridge_applicability_preflight.py
   --bridge-id gtkb-canonical-wrap-keyword-syntax-001` returns
   `preflight_passed: true`, `missing_required_specs: []`.
3. **Clause preflight:** `python scripts/adr_dcl_clause_preflight.py
   --bridge-id gtkb-canonical-wrap-keyword-syntax-001` returns `Blocking
   gaps: 0`.
4. **Project linkage:** `Project Authorization`, `Project`, and `Work Item`
   metadata point at the active PAUTH and the live work item; the WI is in
   the PAUTH's `included_work_item_ids`.
5. **Phantom-spec sweep:** every cited SPEC / GOV / ADR / DCL / PB id
   exists in the live `specifications` table.
6. **Spec body completeness:** the SPEC body section above contains the
   keyword shape, parse rule, behavioral contract, coupling notes,
   assertions, and DELIB citations sufficient for a downstream
   formal-artifact-approval packet to fingerprint without further editing.
7. **No KB mutation in scope:** `kb_mutation_in_scope: false`; no
   `groundtruth.db` write is performed by this thread.

## Risk / Rollback

This proposal writes one file (`bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md`)
and inserts one entry pair (`Document:` + `NEW:`) in `bridge/INDEX.md`.
Rollback is a single `git restore` of `bridge/INDEX.md` and `rm` of the
versioned file (or a WITHDRAWN follow-on). The downstream
`SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` insertion is a separate, gated
operation governed by `GOV-ARTIFACT-APPROVAL-001` and is not part of this
thread's blast radius.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the
top of the `gtkb-canonical-wrap-keyword-syntax-001` document list in
`bridge/INDEX.md`; no prior version is deleted or rewritten (append-only).
`bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — this bridge proposal is governance documentation; no source / test
/ hook / configuration code is modified by this thread. The downstream
spec insertion (under the approval-packet path) will record its own commit
type when filed.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
