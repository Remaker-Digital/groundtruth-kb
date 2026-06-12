NEW

# Implementation Proposal — Explicit-Hint Layer Specification (governance_review)

bridge_kind: governance_advisory
Document: gtkb-explicit-hint-layer-specification
Version: 001
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-12 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 46dbd0f7-6e3d-42b4-81bf-2c2432324069
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, interactive Prime Builder session

Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4482
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and writes no protected narrative
files. The glossary entries, ADR, DCL, and init-keyword reconciliation drafted
below land downstream via formal-artifact-approval-packet and
narrative-artifact-approval-packet writes, each gated by
`GOV-ARTIFACT-APPROVAL-001`.

## Claim

The explicit-hint layer is formalized as the user-facing supra-category over
GroundTruth-KB's already-SPECIFIED (status=specified, not yet implemented)
envelope program (WI-4291..WI-4302). This governance_review proposal drafts the
governance surface for that layer, comprising six coupled deliverables:

1. **Glossary term `explicit hint`** (new entry in
   `.claude/rules/canonical-terminology.md`): an inline `::`-prefixed
   first-line token that mutates the current session's stance (role / scope /
   schedule / priorities / knowledge / objective) through harness hooks and
   priority directives — NOT a skill. Grammar `::<verb> [<arg>]`,
   first-line-only, closed verb vocabulary, strict parse (mirroring
   `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`'s discipline). The init-keyword
   family, wrap-keyword family, and activity-open/close keywords are MEMBERS of
   this category; the dispatch envelope is its autonomous-dispatch sibling.

2. **`ADR-EXPLICIT-HINT-LAYER-001`** (new architecture_decision): records the
   umbrella decision — explicit hints unify and name the existing envelope
   program rather than redesigning it; the closed activity vocabulary
   `{spec, build, test, deliberation, project}` is preserved; authority limits
   (hints never bypass bridge gates, role authority, owner approval,
   work-subject boundaries, or durable harness role assignment); rejected
   alternatives (free-form vocabulary; supersede/redesign).

3. **Canonical-term rename `topic envelope` -> `activity envelope`**: lineage
   work envelope -> topic envelope -> activity envelope. "activity" signals the
   work-TYPE axis (matching `DCL-TOPIC-ENVELOPE-ROUTING-001`'s own "activity-type
   to service dispatch map" language) rather than subject, fixing the universal
   subject mis-read. Spec IDs (`SPEC-TOPIC-*`) persist per append-only
   versioning; the canonical TERM in their bodies + the glossary changes. The
   retired terms ("work envelope", "topic envelope") are recorded with lineage.

4. **Three-axis disambiguation in the glossary**: explicitly separate the three
   axes the term collapse conflated — activity-TYPE (the `::open <type>`
   keyword, closed vocabulary), TARGET/subject (a payload field on the typed
   open, e.g. `::open project <target>` per `SPEC-TOPIC-PROJECT-001` /
   `SPEC-TOPIC-SPEC-001`), and AREA (the `::init` subject `{gtkb, application}`).
   Optionally surface the target as
   `^::open (spec|build|test|deliberation|project)( <target>)?$` — the payload
   field the per-type specs already define.

5. **Init-keyword glossary reconciliation**: the always-loaded glossary entry in
   `canonical-terminology.md` describes the stale v2 form
   `^::init gtkb (pb|lo)$` (role mandatory, no `application` subject);
   `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 (per DELIB-20260648) is
   `^::init (gtkb|application)( (pb|lo))?$` (subject mandatory `{gtkb,
   application}`, role optional, fully additive). Update the glossary to the v3
   canonical form.

6. **`DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`** (new design_constraint): the
   activity-envelope interception model is hook-primary (a UserPromptSubmit
   hook intercepts `::open <type>`/`::close <type>` and injects the type's
   preload context + routing, matching the `::init`/`::wrap` hook precedent)
   with an agent-enforced fallback (turn-start read of the session-envelope JSON
   topics array) where a harness lacks compatible hook events (parity-conditional
   per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`). The remaining lifecycle is already
   canon and unchanged: type-keyed concurrency (<=1 per type, up to 5
   simultaneously), typed `::close <type>` (bare close rejected), auto-close +
   predicate-gated harvest on `::wrap`, storage in the session-envelope JSON
   topics array.

## Why Now

The owner ran a three-harness deliberation (Prime/Claude, Loyal Opposition/Codex,
advisory/Gemini) producing six AUQ-backed decisions captured at
`DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET`. The envelope program is fully
specified but not yet implemented, so locking the explicit-hint umbrella
terminology + the activity rename + the interception DCL NOW — before WI-4301
implementation consumes them — prevents the implementation umbrella from baking
in drift (the topic/subject mis-read) or a stale init-keyword form. This is the
cheapest possible moment: spec-text + glossary edits, not a code migration.

## Why Not (alternatives considered)

- Extend the activity vocabulary to free-form (rejected per DELIB-20260612
  Decision 1; DELIB-2500 already redirected a free-subject `::open` proposal).
  The subject axis is served by a payload field on the typed open, not a
  free-form keyword.
- Supersede/redesign the envelope program (rejected — discards specified
  WI-4291..4302 work).
- Keep "topic" + docs-only (rejected per Decision 6 — the word keeps
  mis-signaling "subject").
- Defer the init-keyword glossary fix (rejected — it is an always-loaded agent
  read surface; the drift mis-informs every session, including this one).

## Prior Deliberations

- `DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET` (2026-06-12) — the six owner
  decisions this proposal implements (umbrella, alias+window, gtkb- prefix +
  curated, platform-core/dual-use ownership, hook-primary+fallback interception,
  topic->activity rename).
- `DELIB-20260637` #4 — work envelope -> topic envelope rename; Decision 6
  (topic -> activity) refines it and preserves its anti-work-item-conflation
  intent.
- `DELIB-20260648` — init-keyword v3 optionality (subject mandatory, role
  optional); basis for deliverable 5.
- `DELIB-2238` / `DELIB-2500` — envelope-convention foundation; DELIB-2500
  redirected an earlier free-subject `::open` proposal toward the closed-type +
  payload model (supports deliverables 1, 3, 4).
- `DELIB-20260635` / `DELIB-20260636` / `DELIB-20260638` / `DELIB-20260658` —
  envelope meta-model + 3-part anatomy shaping.
- `DELIB-20260692` — envelope glossary + GOV-lifecycle amendment review (the
  prior glossary surface this extends).
- `DELIB-20260697` / `DELIB-20260698` — topic-envelope router umbrella spec + DCL
  reviews (the closed-vocabulary + typed-close decisions this preserves).

## Specification Links

Cross-cutting (blocking):

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001` (the formal-artifact-approval gate governing the
  downstream ADR/DCL/glossary writes)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`

Domain specs amended or extended:

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 (init-keyword glossary
  reconciliation, deliverable 5)
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` (term rename + axis clarification,
  deliverables 3-4)
- `SPEC-TOPIC-SPEC-001` / `SPEC-TOPIC-BUILD-001` / `SPEC-TOPIC-TEST-001` /
  `SPEC-TOPIC-DELIBERATION-001` / `SPEC-TOPIC-PROJECT-001` (term-in-body rename)
- `DCL-TOPIC-ENVELOPE-ROUTING-001` (term rename; the activity-type dispatch map
  this aligns with)
- `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` (wrap-keyword family member of the
  explicit-hint category)
- `DCL-SESSION-ENVELOPE-DURABILITY-001` (topics-array storage referenced by the
  interception DCL)

Cross-cutting (advisory):

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-CONCEPT-ON-CONTACT-001` (the new glossary terms are concept-on-contact
  promotion)
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (basis for the interception fallback)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (lifecycle states: the retired-term
  lineage work->topic->activity and spec status transitions)

Narrative files modified downstream (via narrative-artifact-approval-packet):

- `.claude/rules/canonical-terminology.md` (explicit-hint term; topic->activity
  rename; init-keyword v3 fix; three-axis clarification)

New formal artifacts created downstream (via formal-artifact-approval-packet):

- `ADR-EXPLICIT-HINT-LAYER-001` (architecture_decision)
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` (design_constraint)

## Owner Decisions / Input

This proposal is authorized by a fresh, durable owner-decision record — not a
precedent PAUTH:

- `DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET` (source_type=owner_conversation,
  outcome=owner_decision, session 46dbd0f7) captures all six decisions, each
  collected via AskUserQuestion (the only valid owner-decision channel per the
  AUQ-only enforcement stack):
  1. Umbrella over existing specs (keep closed activity vocabulary).
  2. Alias + deprecation window (skill back-compat).
  3. gtkb- prefix swap + curated stem fixes.
  4. GT-KB-owned = platform-core OR dual-use; Agent-Red-specific excluded by
     definition.
  5. Activity-envelope interception = hook-primary + agent fallback.
  6. Rename topic envelope -> activity envelope.
- Owner directive (2026-06-12): "Capture the decision set as Deliberation Archive
  records, then file Bridge #1 (gtkb-explicit-hint-layer-specification)."

Downstream owner-input dependencies (after GO):

- 1 narrative-artifact-approval packet for the `canonical-terminology.md` edits
  (`GOV-ARTIFACT-APPROVAL-001`).
- 2 formal-artifact-approval packets for `ADR-EXPLICIT-HINT-LAYER-001` and
  `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`.

## Requirement Sufficiency

Existing requirements sufficient. All six deliverables derive from
`DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET` (owner AUQ) plus
GO-terminal / specified envelope-program artifacts. No new owner requirement is
needed before drafting; the downstream artifact insertions are owner-gated at
their own approval packets.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`. Run after this NEW entry is added to
`bridge/INDEX.md`:

```
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-explicit-hint-layer-specification
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-explicit-hint-layer-specification
```

Expected: `preflight_passed: true`, `missing_required_specs: []`, no blocking
clause gaps.

## Specification-Derived Verification Plan

Because this is a governance_review proposal with `target_paths: []` and
`requires_verification: false`, GO is terminal for this bridge thread (per the
governance-review-terminal pattern). No follow-on post-impl report is required
for THIS thread.

The downstream artifact insertions are verified at their own gates:

- Glossary edits: `git diff --stat .claude/rules/canonical-terminology.md` (new
  explicit-hint entry; topic->activity rename; init-keyword v3 form).
- ADR/DCL inserts: formal-artifact-approval packets at
  `.groundtruth/formal-artifact-approvals/` + MemBase rows for
  `ADR-EXPLICIT-HINT-LAYER-001` and `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`.
- Doctor canonical-terminology check passes with the new/renamed terms.

Reviewer verification of THIS thread:

1. Bridge mechanics — INDEX has `NEW` at top of the entry.
2. Applicability + clause preflights pass with no blocking gaps.
3. Prior Deliberations cites DELIB-20260612 + the work->topic and init-keyword
   priors.
4. Owner Decisions / Input cites the fresh owner DELIB + AUQ evidence.
5. Closed-vocabulary preservation — the proposal does NOT widen the activity
   vocabulary; the subject axis is a payload field, not a free-form keyword.
6. Init-keyword reconciliation matches SPEC v3 (DELIB-20260648), not a new form.

## Risk / Rollback

This proposal writes one bridge file + one INDEX entry. Rollback = `git restore`
+ `rm` + INDEX revert. The downstream narrative + formal artifact writes are
owner-gated separately; this thread's blast radius is the proposal file itself.
The activity rename touches term-in-body across ~10 envelope specs but preserves
all IDs (append-only safe) and is cheapest now (specs not yet implemented).

## Bridge Filing (INDEX-Canonical)

Filed under `bridge/` with a `NEW` entry inserted at the top of the
`gtkb-explicit-hint-layer-specification` document list in `bridge/INDEX.md`.

## Recommended Commit Type

`docs` — governance documentation (glossary, ADR, DCL drafting); no source /
test / hook / configuration code is modified by this thread.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
