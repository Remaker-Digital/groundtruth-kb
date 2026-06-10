NEW

# Implementation Proposal — Envelope Open/Close Disclosure UI Redesign (governance_review; subsumes WI-3467)

bridge_kind: governance_advisory
Document: gtkb-envelope-disclosure-ui-redesign
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
Work Item: WI-4298
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation. The net-new
`SPEC-ENVELOPE-DISCLOSURE-UI-001` inserts downstream via the active
PAUTH's `approval_packet_creation` mutation class as a separate
formal-artifact-approval-packet operation after GO.

## PAUTH Coverage Note

WI-4298 is not in the envelope-program PAUTH's
`included_work_item_ids` (WI-4291..WI-4297). Codex's WI-4302 and my
WI-4300 + WI-4299 filings under the same PAUTH establish the
coverage-gap-precedent pattern; this filing follows it.

## Claim

Draft `SPEC-ENVELOPE-DISCLOSURE-UI-001`: the redesigned shape for
GroundTruth-KB session open and close disclosure surfaces.

**Open disclosure** (session-start, owner-facing): tightly bounded to
~2-3 KB. Keeps the role declaration, the bridge-actionable surface
summary, the top-3 priorities derived from MemBase, and the
dashboard link. Moves the glossary preview and wrap-commands list to
AXIS 2 surfacing or on-demand `gt help` invocations. Drops the
"Work State" and "Recommended Session Focus" sections entirely
(per WI-3467 subsume).

**Close disclosure** (session-wrap, owner-facing): per-step JSON
written to the per-harness session-envelope-archive file (machine-
parseable) plus a human-readable summary rendered to the terminal
at wrap time (each wrap-procedure step with ok/fail + key result
value).

**WI-3467 subsume:** the Work-State + Recommended-Session-Focus
section removals — previously a separate slice (WI-3467) — are
folded into this WI per the 2026-06-04 supersede decision recorded
in the owner-AUQ grill sequence. WI-3467 should be marked as
superseded-by WI-4298 in the standing backlog when the spec
insertion lands downstream.

## Why Now

The envelope-program design phase has covered 11 of 13 WIs (8
GO-terminal, 3 NEW pending LO — including WI-4300 and WI-4299
filed in the prior turns of this session, plus the current WI-4298).
Disclosure UI is the user-visible surface that anchors the program
to operator experience:

- Without the open-disclosure redesign, the existing startup
  disclosure carries the legacy glossary preview + wrap-commands
  inline — bloating the prompt context the agent starts each
  session with.
- Without the close-disclosure structure, the wrap procedure (per
  WI-4294 GO'd spec) has no canonical output shape; each session
  would emit free-form summaries.
- WI-3467's intent (remove the two stale sections) sits in the
  standing backlog unfulfilled; subsuming it into WI-4298 closes
  the duplicate-work risk.

## Why Not (alternatives considered)

- **Keep the current disclosure shape; just add envelope summary**
  (rejected per WI-4298 owner AUQ #1): the current shape has
  drifted toward bloat (Work State + Recommended Focus + full
  glossary preview). Owner directive: tightly bound to ~2-3 KB.
- **Split WI-3467 (Work-State + Focus removal) and WI-4298 (envelope
  disclosure) into separate threads** (rejected per the
  2026-06-04 owner supersede decision): the two changes are
  coherent — both reshape the same startup disclosure file. One
  thread is simpler.
- **Move glossary INLINE into the open disclosure** (rejected per
  owner AUQ #1): glossary is large; AXIS 2 surfacing (on-demand)
  is the canonical home. `gt help` provides the lookup path.
- **Free-form close-disclosure terminal echo** (rejected per owner
  AUQ #3): owner directive requires structured per-step JSON for
  machine consumption + human-readable summary. Free-form would
  defeat downstream tooling that reads the archive file.
- **Top-3 priorities from `all` work items** (rejected per owner
  AUQ #2): owner directive limits source to
  `approval_state=implementation_authorized` only (skip
  `unapproved` + `auq_required` + `auq_resolved`); selection is
  highest-priority unblocked, deterministic.

## Prior Deliberations

- `DELIB-2238`, `DELIB-2500` — envelope-program foundation.
- `DELIB-20260635`, `DELIB-20260636`, `DELIB-20260637`,
  `DELIB-20260638`, `DELIB-20260648` — envelope-program shaping.
- WI-3467 — the originating Work-State + Recommended-Session-Focus
  removal scope, subsumed by this WI per the owner-AUQ supersede
  decision (the decision is captured in the owner-grilling
  sequence; a DELIB record formalizing the supersede may be
  required downstream).
- `bridge/gtkb-session-wrap-procedure-001-004.md` (GO; my
  REVISED-2) — defines the wrap-procedure's per-step outputs that
  the close-disclosure consumes.
- `bridge/gtkb-session-envelope-durability-001-006.md` (GO; parallel
  session) — defines the per-harness archive file format the
  close-disclosure writes into.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `GOV-ARTIFACT-APPROVAL-001`,
  `GOV-STANDING-BACKLOG-001`,
  `GOV-SESSION-SELF-INITIALIZATION-001` — the open-disclosure
  governance baseline this proposal amends operationally.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Specs referenced (forward references; sibling WIs):**

- Sibling WI-4293 (session-envelope durability; GO at -006) —
  defines the per-harness archive file format the close-disclosure
  writes structured JSON into.
- Sibling WI-4294 (wrap procedure; GO at -004) — defines the
  per-step outputs the close-disclosure renders.

**Specs drafted by this proposal:**

- The envelope disclosure-UI spec drafted below (NEW; spec id
  provisional until insertion).

## Owner Decisions / Input

This governance-review proposal is authorized by the active PAUTH;
no fresh AUQ is required for the design:

1. **DELIB-20260648** — envelope-program PAUTH-minting.
2. **WI-4298 status_detail owner AUQ** — direct authority for the
   5 design points (open budget + content; top-3 source; close
   shape; producer; WI-3467 subsume).
3. **2026-06-04 owner supersede decision** — folds WI-3467 into
   WI-4298 (the supersede mechanic).

Owner-input dependencies downstream of GO:

- 1 formal-artifact-approval packet at MemBase insertion time.
- The actual Python implementation (refactor of
  `scripts/session_self_initialization.py` + wrap-procedure render
  handler) is a separate impl_proposal scope under WI-4301.

## Requirement Sufficiency

Existing requirements sufficient. The owner-grilling AUQ for WI-4298
captured all 5 design points. WI-3467's removal scope is folded in
per the supersede decision. No new owner requirement is needed.

## Spec Body — Envelope Disclosure UI Spec (draft)

**Title:** Envelope Open/Close Disclosure UI Contract.

**Type:** specification.

**Status (at insertion):** specified.

**Body:**

The session open and close disclosures are the operator-facing
surface of the envelope program. This SPEC defines the canonical
content shape for both surfaces.

### Open Disclosure (session-start)

**Budget:** ~2-3 KB of disclosure body content. The budget is a
soft cap; producers (per the deterministic startup service) should
trim discretionary content rather than hit hard limits.

**Required content sections (keep):**

1. **Role declaration**: the resolved active role for the session
   (durable from `harness-state/harness-registry.json`, or
   session-stated via the canonical init-keyword family). Format:
   one line.
2. **Bridge-actionable surface summary**: latest GO / NO-GO counts
   for the active role, derived from `bridge/INDEX.md`. Format: one
   line listing the counts; the AXIS 2 surface delivers per-thread
   details on demand.
3. **Top-3 priorities**: 3 highest-priority unblocked WIs derived
   from MemBase per the source rules below.
4. **Dashboard link**: the GroundTruth-KB dashboard URL (current:
   the local Grafana surface).

**Content sections to MOVE (no longer inline):**

- **Glossary preview**: the multi-page glossary preview previously
  inlined. Relocate to AXIS 2 surfacing (the existing AXIS 2 hook
  delivers glossary entries on demand) or `gt help` invocations.
- **Wrap-commands list**: the 17 NL wrap-trigger phrases. Relocate
  to `gt help wrap` or equivalent on-demand surface.

**Content sections to DROP (per WI-3467 subsume):**

- **"Work State"** section: drift indicator block. Dropped in
  full; the bridge-actionable summary covers the operationally
  meaningful subset.
- **"Recommended Session Focus"** section: the menu of focus
  options. Dropped in full; the top-3 priorities provide the
  forward path.

**Top-3 priorities source (deterministic):**

The producer (`scripts/session_self_initialization.py` refactor per
WI-4301) MUST select the top-3 WIs from MemBase with:

- `approval_state = 'implementation_authorized'` only.
- Skip `unapproved`, `auq_required`, `auq_resolved`.
- Selection algorithm: highest-priority (P0 > P1 > P2 > P3 >
  P4 > none); within same priority, lowest WI id (stable order).
- Filter: `resolution_status` in `('open', 'in_progress',
  'blocked')`.

The selection MUST be deterministic for a given MemBase snapshot.
Re-running the open-disclosure producer with the same MemBase state
produces the same top-3 ordering.

### Close Disclosure (session-wrap)

The close disclosure is produced by the wrap procedure (per WI-4294
GO'd spec) and has TWO output surfaces:

**Surface 1 — Machine-parseable per-step JSON:**

Each wrap-procedure step writes a JSON record into the per-harness
session-envelope archive file (per WI-4293's GO'd schema). The JSON
schema:

```json
{
  "wrap_step_results": [
    {"step_id": 1, "step_name": "envelope_state_finalization",
     "tier": "MANDATORY", "outcome": "ok",
     "key_result": "closed_at=2026-06-04T...; wrap_outcome=manual_wrap"},
    {"step_id": 4, "step_name": "da_harvest", "tier": "MANDATORY",
     "outcome": "ok|fail|skipped", "key_result": "..."},
    ...
  ]
}
```

The `wrap_step_results` array contains exactly one entry per step
that the wrap procedure attempted (skipped steps may or may not
appear; implementation choice for WI-4301).

**Surface 2 — Human-readable terminal summary:**

At wrap time, the wrap procedure renders the per-step results to
the terminal in a compact human-readable form:

```text
::wrap (manual_wrap)
  [OK]  1 envelope finalization  -> closed_at=2026-06-04T...
  [OK]  4 da harvest              -> 2 deliberations harvested
  [OK]  8 working-tree attestation -> clean
  [OK] 11 topic auto-close        -> 0 topics open
  [OK] 12 session-envelope archive -> harness-state/B/session-envelope-archive/...
session closed.
```

The terminal summary is for the closing operator's immediate
read; it is not consumed programmatically.

### Producer Refactor (WI-4301 scope, not this thread)

The open disclosure producer is the existing
`scripts/session_self_initialization.py`; WI-4301 Slice B refactors
it to emit the new content shape (drop Work State + Focus sections;
move glossary + wrap-commands; produce top-3 from MemBase per the
rules above).

The close disclosure producer is a new wrap-procedure render
handler (per WI-4294 spec, integrated at the wrap procedure's
terminal-close-summary call-site); WI-4301 Slice B / impl umbrella
lands the actual handler.

### WI-3467 Subsume

This SPEC subsumes WI-3467's intended scope (remove Work State +
Recommended Session Focus sections). On insertion, WI-3467's
backlog row should be marked `superseded_by=WI-4298` per
`GOV-STANDING-BACKLOG-001` discipline. The supersede mechanic is
not enacted by this proposal (which is governance_review only); it
runs as a separate work-item-lifecycle update under PAUTH.

### Assertions (machine-checkable; shipped at `status=specified`)

1. `grep` — `scripts/session_self_initialization.py` (post WI-4301
   Slice B refactor) does NOT emit "Work State" or "Recommended
   Session Focus" section headers. Expected-failing until refactor.
2. `grep` — the same script emits top-3 priorities derived from
   MemBase WIs filtered by `approval_state='implementation_authorized'`.
3. `grep` — wrap-procedure render handler emits `wrap_step_results`
   JSON array in the archive file. Expected-failing until WI-4301
   Slice B impl.
4. `grep_absent` — `gt help wrap` (or equivalent) surface delivers
   the 17 NL wrap-trigger phrases at WI-4301 impl time.

### Owner directive citation

"S-2026-06-04 owner grilling: formalize envelope program (WI-3468)"
(per WI-4298 `source_owner_directive`).

### Related deliberations

`DELIB-2238`, `DELIB-2500`, `DELIB-20260635`, `DELIB-20260636`,
`DELIB-20260637`, `DELIB-20260638`, `DELIB-20260648`.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing
Preflight Subsection. Re-run after this NEW entry is added to
`bridge/INDEX.md`. Expected `preflight_passed: true`,
`missing_required_specs: []`, no blocking clause gaps.

## Specification-Derived Verification Plan

Because this is a governance_review proposal with `target_paths: []`
and `requires_verification: false`, GO is terminal for this bridge
thread.

Reviewer verification of THIS bridge thread:

1. **Bridge mechanics** — INDEX has `NEW:` at top.
2. **Applicability + clause preflights** pass with no blocking gaps.
3. **PAUTH coverage note** — follows the precedent set by WI-4302,
   WI-4300, and WI-4299 under the same PAUTH.
4. **5 design points captured** — open budget + content + top-3
   rules + close JSON + close terminal + producer locations.
5. **WI-3467 subsume mechanic referenced** — supersede recorded as
   a downstream work-item-lifecycle update.
6. **Determinism** — top-3 selection rules are deterministic for a
   fixed MemBase snapshot; the close-disclosure JSON schema is
   stable.

## Risk / Rollback

This proposal writes one bridge file + one INDEX entry. Rollback
single `git restore` + `rm`.

If the WI-3467 subsume is contested (e.g., owner prefers to keep
Work-State or Focus sections), a REVISED can carve those sections
out of the drop list without affecting the rest of the design.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted
at the top of the `gtkb-envelope-disclosure-ui-redesign` document
list in `bridge/INDEX.md`.

## Recommended Commit Type

`docs` — governance documentation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
