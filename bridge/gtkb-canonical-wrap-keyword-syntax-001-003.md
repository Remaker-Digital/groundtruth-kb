REVISED

# Implementation Proposal — Canonical Wrap-Keyword Syntax (REVISED-2, governance_review)

bridge_kind: governance_review
Document: gtkb-canonical-wrap-keyword-syntax-001
Version: 003
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-canonical-wrap-keyword-syntax-001-002.md (NO-GO)

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

This proposal performs no MemBase mutation and executes no KB writes.

## Revision Claim

This REVISED-2 addresses the single P1 finding from the LO NO-GO at
`-002`: the wrap-keyword spec body in `-001` hardcoded the legacy
shared session-envelope path (the in-root projection path under
`.claude/session/`) as the open-topic auto-close state surface,
preempting the WI-4293 durability DCL's authoritative state
decision (per-harness `harness-state/<harness_name>/`).

**Concrete change from `-001`:** every direct legacy-projection-path
reference in this spec is replaced with abstract delegation: "the
authoritative session-envelope state surface defined by sibling
WI-4293's durability DCL". The wrap-keyword spec defines the
TRIGGER surface; the STATE surface is WI-4293's concern.

**Scope unchanged:** still governance_review with `target_paths: []`,
`requires_verification: false`, `kb_mutation_in_scope: false`.

**Accepted trigger semantics carried forward (per LO recommendation 1):**

- Exact regex `^::wrap$`.
- Bare keyword (no arguments, no mode vocabulary).
- No synonyms (`::end`, `::close`, `::done` are NOT recognized).
- 17 natural-language wrap phrases remain additive triggers per the
  startup disclosure's "Wrap-Up Trigger Commands" section.

## Same-Session Authoring (Skip-Own Interpretation)

Same-session REVISED authoring (this REVISED is by the original
`-001` author session). The skip-own directive prohibits same-session
VERDICT authoring (GO/NO-GO/VERIFIED); same-session REVISED in
response to a different-session NO-GO is the canonical Prime
workflow. The LO NO-GO at `-002` was authored by Codex automation
`keep-working-lo` (harness A) — a different session. Fresh-eyes
review step performed.

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

**Specs referenced (forward references; sibling WIs):**

- The session-envelope durability spec planned for sibling WI-4293
  (bridge thread `gtkb-session-envelope-durability-001`, GO at -006).
  This wrap-keyword spec delegates authoritative state-surface
  semantics to WI-4293's DCL; the spec id (a DCL drafted in that
  GO'd thread) is provisional until insertion.
- The wrap-procedure spec planned for sibling WI-4294 (bridge thread
  `gtkb-session-wrap-procedure-001`, REVISED-2 at -003 pending LO
  re-review). The wrap-keyword trigger is the entry point; the
  4-tier procedure runs the deterministic close-steps.

**Specs drafted by this proposal:**

The canonical wrap-keyword syntax spec drafted in `-001` is carried
forward with trigger semantics unchanged. The spec id is the same
one drafted in `-001`; the body is rewritten only to remove the
state-path hardcoding.

## Prior Deliberations

Carried forward from `-001`:

- `DELIB-2238`, `DELIB-2500`, `DELIB-20260636`, `DELIB-20260637`,
  `DELIB-20260648` — originating wrap-keyword + envelope-program
  deliberations.
- `bridge/gtkb-canonical-init-keyword-syntax-001.md` chain (VERIFIED
  at `-012`) — the sibling init-keyword bridge thread.
- `bridge/gtkb-session-envelope-durability-001-006.md` (GO; parallel
  session) — the per-harness authoritative state model. This
  wrap-keyword REVISED defers state-path semantics to that sibling.
- LO advisory at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-29-07-12-delib-2500-envelope-convention-advisory.md`
  — prior LO advisory recommending per-harness state authority.

## Owner Decisions / Input

Carried forward from `-001`:

1. **DELIB-20260648 (envelope-program PAUTH-minting)** — authorizes
   governance-review spec creation under this PAUTH.
2. **DELIB-2238 + DELIB-2500** — originating wrap-keyword
   deliberations: bare `::wrap`, regex `^::wrap$`, NL wrap commands
   as additive triggers, wrap outcome captured by the procedure not
   the keyword.
3. **DELIB-20260636 + DELIB-20260637** — envelope-program AUQ
   context.

Owner-input dependencies downstream of GO:

- 1 formal-artifact-approval packet at MemBase insertion time.

## Requirement Sufficiency

Existing requirements sufficient. The owner-grilling AUQ for WI-4292
captured the complete spec design. The state-path semantics are
sourced from the GO'd WI-4293 (no fresh owner AUQ required).

## Findings Addressed

### F1 — P1 — Spec body hardcoded a state path rejected by the sibling durability review

**LO observation summary:** the `-001` proposal hardcoded the legacy
shared session-envelope path in the behavioral contract (lines
52-55) and in the spec body (lines 246-250). The LO advisory + the
WI-4293 thread's evolution favor per-harness
`harness-state/<harness_name>/session-envelope.json` as the
authoritative state surface. The wrap-keyword spec should NOT
preempt the durability DCL's state-authority decision.

**Response — every legacy-path reference is removed from the spec
body and replaced with abstract delegation to sibling WI-4293:**

| Original location | Correction |
|-------------------|------------|
| Behavioral contract (open-topic interaction) | "iterate open topic envelopes from the authoritative session-envelope state surface defined by sibling WI-4293's durability DCL" |
| Spec body Coupling section | "WI-4293 defines the envelope state surface; this spec defines only the trigger" |
| Any other path reference | removed; deferred to WI-4293 |

**Trigger semantics preserved (per LO recommendation 1):**

- regex `^::wrap$` — unchanged
- bare keyword, no mode vocabulary — unchanged
- no synonyms — unchanged
- 17 NL wrap phrases additive — unchanged

**No other LO findings.** Positive confirmations from `-002`
(governance-only metadata, PAUTH coverage, applicability+clause
preflights, DELIB citations) are unchanged.

## Scope Changes

None. Same governance_review scope; same trigger semantics; same
target_paths/requires_verification/kb_mutation_in_scope metadata.

## Spec Body — Canonical Wrap-Keyword Syntax Spec (REVISED-2 draft)

**Title:** Canonical Wrap-Keyword Syntax for Session Close.

**Type:** specification.

**Status (at insertion):** specified.

**Body:**

The canonical wrap-keyword syntax for GroundTruth-KB sessions is the
exact regex `^::wrap$`. The keyword is bare: no arguments, no mode
vocabulary, no trailing whitespace, case-sensitive.

The keyword occupies the entire first non-blank line of an owner
message, and may also be the sole content of that message.
Subsequent prompt content on later lines is unconstrained and is
not consumed by the wrap-trigger layer.

**Recognition contract:**

1. The active AI harness's session-wrap detection logic MUST treat
   `^::wrap$` on the first non-blank line as a wrap-trigger event
   identical to the natural-language wrap phrases enumerated in the
   startup disclosure's "Wrap-Up Trigger Commands" section.
2. The 17 NL wrap commands (`wrap up`, `wrap up this session`,
   `session wrap-up`, `run session wrap-up`, `close this session`,
   `end this session`, `new session`, `fresh session`,
   `start a new session`, `start a fresh session`, `begin a new session`,
   `begin a fresh session`, `open a new session`, `prepare a new session`,
   `initialize a new session`, `start fresh`, `begin fresh`) remain
   additive triggers and continue to resolve to the same wrap procedure.
3. No synonyms (`::end`, `::close`, `::done`, `::finish`, etc.) are
   recognized.

**Behavioral contract (delegated to the wrap-procedure spec, sibling
WI-4294):**

The wrap procedure (defined by sibling WI-4294) is the deterministic
sequence of close-steps that runs when this keyword fires. This
spec defines only the trigger surface. Two behavioral obligations
this spec imposes on the wrap procedure:

1. On wrap-trigger, BEFORE the session is closed, the wrap procedure
   MUST iterate open topic envelopes from the authoritative
   session-envelope state surface (defined by sibling WI-4293's
   durability DCL) and auto-close each with
   `wrap_outcome=auto_closed_by_session_wrap`. The specific state
   path (per-harness, shared, or other) is the durability DCL's
   concern, not this spec's.
2. The wrap procedure then executes its standard session-close
   steps per WI-4294's 4-tier framework.

**State surface delegation (per LO NO-GO `-002`):**

This spec does NOT define the live state path, archive path, or
projection rules for the session envelope. Those are the WI-4293
durability DCL's concern. The wrap-keyword spec references the
state surface abstractly; the durability DCL provides the concrete
schema and paths.

**Coupling (by sibling WI):**

- Sibling WI-4293 (envelope-durability DCL; GO at -006) — defines
  the authoritative state surface this wrap-keyword obligates the
  wrap procedure to operate on.
- Sibling WI-4294 (wrap-procedure spec; REVISED-2 at -003 pending
  LO re-review) — defines the deterministic 4-tier procedure this
  wrap-keyword triggers.

**Owner directive citation:** "S-2026-06-04 owner grilling: formalize
envelope program (WI-3468)" (per WI-4292 `source_owner_directive`).

**Related deliberations:** `DELIB-2238`, `DELIB-2500`, `DELIB-20260636`,
`DELIB-20260637`, `DELIB-20260648`.

**Symmetric peer specs:** the canonical init-keyword spec from the
VERIFIED `gtkb-canonical-init-keyword-syntax-001` thread (id is
provisional during its own bridge cycle and unchanged by this
proposal).

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — `.claude/rules/canonical-terminology.md` MUST contain
   the token `::wrap` once the WI-4301 implementation rule-file
   slice lands. Expected-failing until then.
2. `grep` — at least one of the startup-disclosure templates under
   `config/agent-control/` MUST list `::wrap` alongside the NL wrap
   commands.

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

1. **F1 correction:** the spec body contains zero literal legacy
   shared-session-envelope path mentions; state surface references
   go through "sibling WI-4293's durability DCL".
2. **Trigger semantics preservation:** regex `^::wrap$`, bare
   keyword, no synonyms, 17 NL phrases additive — all unchanged
   from `-001`.
3. **Bridge mechanics:** INDEX has `REVISED:` at top; first line
   canonical `REVISED` token.
4. **Applicability + clause preflights** pass with no blocking gaps.
5. **Project linkage** unchanged.

## Risk And Rollback

This REVISED writes one file
(`bridge/gtkb-canonical-wrap-keyword-syntax-001-003.md`) and inserts
one `REVISED:` line in `bridge/INDEX.md`. Rollback is a single
`git restore` + `rm`.

If WI-4293's durability DCL evolves further, this REVISED's abstract
delegation remains correct (delegation is path-agnostic).

## Bridge Filing (INDEX-Canonical)

This REVISED is filed under `bridge/` with a `REVISED:` entry
inserted at the top of the `gtkb-canonical-wrap-keyword-syntax-001`
document list in `bridge/INDEX.md` (above the LO `-002` NO-GO line).

## Recommended Commit Type

`docs` — governance documentation; no source / test / hook /
configuration code is modified.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
