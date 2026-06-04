NEW

# Implementation Proposal — Session Wrap Procedure Deterministic Trigger Spec (governance_review)

bridge_kind: governance_review
Document: gtkb-session-wrap-procedure-001
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
Work Item: WI-4294
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and executes no KB writes. The
net-new artifact (`SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001`)
is inserted downstream via the active PAUTH's `approval_packet_creation`
mutation class as a separate formal-artifact-approval-packet operation
after GO. (Trips `KB_MUTATION_NEGATION_RE` in
`.claude/hooks/bridge-compliance-gate.py:203-207`.)

## Claim

Define `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001`: the
deterministic procedure that runs when the canonical `::wrap` keyword
or any of the 17 natural-language wrap commands fires. The spec
encodes a **4-tier framework** for 12 candidate close-steps drawn
from DELIB-2238 + DELIB-2500:

- **MANDATORY (5; always run, no override):** envelope-state
  finalization, DA harvest (if uncaptured), working-tree attestation,
  topic auto-close, envelope.json archive.
- **CONDITIONAL-WITH-DEFAULT-ON (4; auto-fire unless owner
  `--suppress <step>` at wrap time):** project-authorization envelope
  reconciliation, bridge-thread state attestation, task-list state
  preservation, standing-backlog touch evidence.
- **CONDITIONAL (1; fires only if a declarative predicate is true):**
  auto-memory delta capture.
- **OPTIONAL (2; owner-elective at wrap time):** MemBase rollup
  snapshot, ChromaDB index freshness assertion.

Each conditional step carries a declarative predicate evaluated
against envelope.json + MemBase + git state at wrap time. Predicates
are deterministic; no AI judgment in the wrap-trigger layer.

## Why Now

The wrap-keyword spec (WI-4292, sibling proposal at
`bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md`, currently
NO-GO'd in a parallel thread) defines the TRIGGER surface. The
envelope.json schema (WI-4293, sibling at
`bridge/gtkb-session-envelope-durability-001-006.md` GO'd) defines the
STATE surface. The wrap-procedure spec (this WI) defines the
PROCEDURE surface — what happens when the trigger fires.

Without a deterministic procedure spec:

- The 17 NL wrap phrases and the canonical `::wrap` would fire ad-hoc,
  inconsistent steps depending on which session is running.
- Owner has no `--suppress` knob for routine but skippable steps.
- Predicate gating for the CONDITIONAL step is undefined, leading to
  AI-judgment-at-wrap-time (which violates the deterministic-services
  principle per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`).
- WI-4301 (envelope-program implementation umbrella) has no spec to
  implement against for the wrap procedure's Slice B.

The 4-tier framework formalizes the owner's 2026-06-04 grilling AUQ
that triaged the 12 candidate close-steps into the four buckets.

## Why Not (alternatives considered)

- **2-tier MANDATORY/OPTIONAL** (rejected per owner AUQ 2026-06-04):
  would collapse the CONDITIONAL-WITH-DEFAULT-ON tier into either
  MANDATORY (over-tight) or OPTIONAL (under-tight). The 4-tier model
  separates "auto-fire with override" from "predicate-gated" cleanly.
- **All-MANDATORY** (rejected): would force MemBase rollup snapshots
  and ChromaDB freshness assertions on every wrap, even when not
  needed (e.g., a quick wrap after a no-op session). Too rigid.
- **All-OPTIONAL** (rejected): would let routine cleanup drift; the 5
  MANDATORY steps are the load-bearing finalization that prevents
  the bridge protocol from accumulating stale state.
- **AI-judgment predicates** (rejected per
  `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`): the wrap-trigger
  layer must be deterministic. Each CONDITIONAL predicate is a
  declarative check over envelope.json + MemBase + git state.
- **`--suppress` on MANDATORY steps** (rejected per owner AUQ):
  MANDATORY means MANDATORY. The 5 always-run steps protect the
  audit-trail invariant.

## Prior Deliberations

- `DELIB-2238` — establishes wrap-on-exit + envelope-program
  foundation; enumerates the 10 original candidate close-steps.
- `DELIB-2500` — owner directive on wrap-outcome capture and the
  NL-additive-trigger relationship; informs the MANDATORY #1
  (envelope-state finalization with `wrap_outcome`).
- `DELIB-20260637` — 3-part envelope anatomy; the wrap procedure
  operates on the session envelope (and iterates its contained topic
  envelopes for auto-close).
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md` (NEW, prior
  session; NO-GO at `-002`) — the wrap-keyword TRIGGER spec sibling.
  Trigger and procedure are independently versioned; this proposal
  references the trigger conceptually (NL phrases + `::wrap`) but
  does not depend on the keyword spec's specific GO state.
- `bridge/gtkb-session-envelope-durability-001-006.md` (GO at
  `-006`, parallel session) — the envelope.json schema; this
  procedure spec depends on the schema for the topic-iteration +
  archive-path semantics.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — informs the
  deterministic-predicate requirement on CONDITIONAL steps.
- Auto-memory `feedback_latest_go_terminal_for_governance_review.md`
  — terminal-at-GO pattern applied here.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical
  workflow state; this proposal does not modify bridge mechanics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied
  by this Specification Links section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project
  metadata cites the active PAUTH covering WI-4294.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — this proposal
  declares `requires_verification: false` because it is a
  `bridge_kind: governance_review` with `target_paths: []`; GO is
  terminal for the spec-body approval step per
  `feedback_latest_go_terminal_for_governance_review.md`. The
  Specification-Derived Verification Plan section below enumerates
  reviewer-side gates.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files remain
  under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` — the downstream artifact requires a
  formal-artifact-approval packet; not filed here.
- `GOV-STANDING-BACKLOG-001` — WI-4294 is `implementation_authorized`
  under the active PAUTH.
- `DCL-CONCEPT-ON-CONTACT-001` — the procedure spec touches the
  session-envelope concept; the canonical-terminology entry for
  "session envelope" is added in Slice 2's downstream rule-file edits
  (not in this proposal).

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the proposed spec is a
  governed artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — informs the
  artifact-oriented framing of the wrap-procedure as a versioned spec.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — net-new spec creation is a
  lifecycle event covered by the PAUTH's `allowed_mutation_classes`.

**Specs referenced (forward references; sibling WIs):**

- The wrap-keyword TRIGGER spec planned for sibling WI-4292 (bridge
  thread `gtkb-canonical-wrap-keyword-syntax-001`, NO-GO at -002,
  pending revise). The spec id is provisional; this procedure spec
  references the trigger surface by WI rather than by spec id.
- The topic-envelope router umbrella spec planned for sibling WI-4295
  Slice 1 (bridge thread `gtkb-work-envelope-router-slice-1-001`,
  NEW at -001, pending LO review). Step #11 (topic auto-close)
  references the router's MEDIUM auto-close semantic by WI.

**Specs drafted by this proposal (downstream insert via approval packet):**

- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` (NEW; body
  drafted below).

## Owner Decisions / Input

This governance-review proposal is authorized by the active PAUTH; no
fresh AUQ is required at proposal-filing time:

1. **DELIB-20260648 (envelope-program PAUTH-minting)** — owner
   approved the envelope-program spec-WI batch (WI-4291..WI-4297)
   under `bridge_kind=governance_review`.
2. **DELIB-2238 + DELIB-2500** — originating wrap-procedure
   deliberations; the 12 candidate steps and wrap-outcome capture
   directives derive from these.
3. **Owner AUQ 2026-06-04 (envelope-project per-WI grill)** — direct
   authority for the 4-tier framework, the specific step assignments
   (5/4/1/2), and the `--suppress` plumbing on CONDITIONAL-WITH-
   DEFAULT-ON steps. Captured as the WI-4294 `status_detail`.

Owner-input dependencies downstream of GO:

- 1 formal-artifact-approval packet at MemBase insertion time.
- No source / hook / test mutation requested in this thread; the
  wrap-procedure implementation lands in WI-4301 (envelope-program
  implementation umbrella) Slice B.

## Requirement Sufficiency

Existing requirements sufficient. The owner-grilling AUQ for WI-4294
captured the complete 4-tier framework, the specific step assignments,
predicate-determinism requirements, and `--suppress` plumbing. The
PAUTH covers spec creation. The sibling WI-4293 envelope.json schema
(GO'd at `-006`) provides the consuming state surface. No new owner
requirement is needed to draft and approve the spec body.

## Spec Body — SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001 (draft)

**Title:** Session Wrap Procedure: Deterministic 4-Tier Trigger
Sequence.

**Type:** specification.

**Status (at insertion):** specified.

**Body:**

The session wrap procedure is the deterministic sequence of
close-steps that runs when the wrap trigger fires. The trigger
surface is defined by sibling WI-4292 (the canonical `::wrap`
keyword spec plus the 17 NL wrap phrases as additive triggers). All
triggers resolve to this same procedure. The trigger spec id is
provisional during WI-4292's bridge cycle; the trigger surface is
referenced here by WI, not by spec id.

**4-tier step framework (12 candidate steps):**

### Tier 1 — MANDATORY (5; always run; no override)

1. **Envelope-state finalization.** Set `closed_at` (ISO-8601 UTC) and
   `wrap_outcome` (string) on the active session envelope in
   `.claude/session/envelope.json` per the WI-4293 schema. The
   `wrap_outcome` value is supplied by the wrap-trigger context or
   defaults to `manual_wrap` (NL or `::wrap` keyword) /
   `auto_closed_by_session_wrap` (recursive from a `::wrap` invocation
   on an outer scope).
4. **DA harvest IF uncaptured decisions exist.** Predicate-gated
   subset of `gt deliberations harvest`. Predicate: at least one
   in-session deliberation candidate exists per the harvest helper's
   inclusion rules. If predicate false, this step is a no-op (cheap).
8. **Working-tree state attestation.** Run `git status --short` (or
   equivalent) and record the resulting state in the closing envelope
   record. Does NOT auto-commit or auto-stash. Attestation only.
11. **Topic auto-close.** Iterate open work envelopes (topics) in
    `.claude/session/envelope.json`. For each open topic, set its
    `close_outcome=auto_closed_by_session_wrap` and `closed_at`. The
    topic-router (per sibling WI-4295 Slice 1's umbrella spec)
    treats this as a MEDIUM auto-close: the topic's dispatch-to-
    service still runs deterministically.
12. **envelope.json archive.** Rename the live file from
    `.claude/session/envelope.json` to
    `.claude/session/archive/<closed_at>-envelope.json` (per
    WI-4293's archive path semantics). Unset the live file (no
    placeholder; next `::init` opens a fresh one).

### Tier 2 — CONDITIONAL-WITH-DEFAULT-ON (4; auto-fire unless `--suppress <step>` at wrap time)

2. **Project-authorization envelope reconciliation.** Validate that
   every active `current_project_authorizations` row referenced in
   the session's bridge filings is still active. Surface any expired
   or revoked PAUTHs as a wrap-time WARN line.
3. **Bridge-thread state attestation.** Snapshot the latest status
   per bridge thread touched in the session. Record in the closing
   envelope record (informational; does not gate close).
5. **Task list state preservation.** Capture the session's
   TaskList state (pending / in_progress / completed) into the
   closing envelope record. Lets a future session resume in-flight
   tasks if applicable.
10. **Standing-backlog touch evidence.** Record which work_items
    the session created, updated, or referenced. Lets the dashboard
    surface session-level backlog churn.

### Tier 3 — CONDITIONAL (1; fires only if a declarative predicate is true)

7. **Auto-memory delta capture.** Predicate: the session produced
   at least one auto-memory write under the harness-managed
   per-project auto-memory directory (resolved via the harness
   configuration; observed read-only) since the session's open. If
   true, capture the new/modified memory file names (basename only,
   no absolute paths) into the closing envelope record. If false,
   skip silently.

### Tier 4 — OPTIONAL (2; owner-elective at wrap time)

6. **MemBase rollup snapshot.** Owner-elective via `--include-rollup`.
   Emits a point-in-time summary of work_items + deliberations + specs
   counts at wrap. Useful for session-level reports; not used for
   protocol invariants.
9. **ChromaDB index freshness assertion.** Owner-elective via
   `--check-chroma-freshness`. Asserts that the ChromaDB semantic
   index matches the MemBase deliberation count within a tolerance.
   Useful for cross-tier-consistency audits; not used for protocol
   invariants.

**Predicate semantics:**

Each CONDITIONAL or CONDITIONAL-WITH-DEFAULT-ON step carries a
**declarative predicate** evaluated against fixed inputs at wrap time:

| Predicate input | Source |
|------------------|--------|
| envelope.json state | `.claude/session/envelope.json` (live file at wrap time) |
| MemBase rows | `groundtruth.db` read-only queries |
| Git state | `git status`, `git diff --stat`, `git rev-parse HEAD` |

Predicates are **deterministic**: same inputs at the same wrap
moment produce the same boolean. No AI judgment is consulted in
predicate evaluation. The wrap-trigger layer is a service, not an
agent (per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`).

**`--suppress <step>` plumbing:**

CONDITIONAL-WITH-DEFAULT-ON steps support a wrap-time suppression
flag. Example: `::wrap --suppress task_list_preservation` skips
step #5 for this one wrap. MANDATORY steps do NOT support
`--suppress` (the flag is rejected with an error). The owner MAY
make `--suppress` a session-persistent override via a future
session-level option (out of scope here).

**Recursion guard:**

The procedure is not idempotent on re-entry: invoking `::wrap`
during a wrap-in-flight is a parse-time error (or silently dropped
by the wrap-trigger layer). Implementation detail; the procedure
itself assumes single-instance execution per wrap.

**Step ordering:**

The four tiers execute in order: Tier 1 → Tier 2 → Tier 3 → Tier 4.
Within Tier 1, steps run in the order #1 → #4 → #8 → #11 → #12
(envelope-state first, archive last). Tier 2 / 3 / 4 ordering is
implementation-defined; the spec does not constrain it.

**Failure handling:**

A MANDATORY step failure aborts the wrap; the session remains "open"
and the failure is reported. A CONDITIONAL-WITH-DEFAULT-ON,
CONDITIONAL, or OPTIONAL step failure is logged but does NOT abort
the wrap (failed step records the failure in the closing envelope;
wrap proceeds).

**Couplings (by sibling WI):**

- Sibling WI-4293 (`bridge/gtkb-session-envelope-durability-001-006.md`
  GO): envelope.json schema MUST support the
  `closed_at` + `wrap_outcome` + topics array + `close_outcome`
  fields used by Tier-1 steps #1, #11, #12.
- Sibling WI-4292
  (`bridge/gtkb-canonical-wrap-keyword-syntax-001-002.md`
  NO-GO; pending revise): the trigger surface; this procedure runs
  when that trigger fires.
- Sibling WI-4295 Slice 1
  (`bridge/gtkb-work-envelope-router-slice-1-001-001.md` NEW): the
  topic-router; step #11's MEDIUM auto-close semantic delegates to
  the topic-router's per-type dispatch.

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — the wrap procedure implementation (per WI-4301 Slice B)
   contains exactly 5 MANDATORY step identifiers. Expected-failing
   until WI-4301.
2. `grep` — at least one regression test exercises the `--suppress`
   plumbing on a CONDITIONAL-WITH-DEFAULT-ON step. Expected-failing
   until WI-4301.

**Owner directive citation:** "S-2026-06-04 owner grilling: formalize
envelope program (WI-3468)" (per WI-4294 `source_owner_directive`).

**Related deliberations:** `DELIB-2238`, `DELIB-2500`, `DELIB-20260637`.

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
the spec-body approval step.

The downstream MemBase insertion is verified at its own gate:

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type specification \
    --id SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001 --json
```

MUST return one row at version 1 with body fingerprint matching the
formal-artifact-approval packet. The verification runs at
*spec-insertion* time, not at this bridge thread's review time.

Reviewer verification of THIS bridge thread:

1. **Bridge mechanics:** `bridge/INDEX.md` has `NEW: ...-001.md` at
   the top of the `gtkb-session-wrap-procedure-001` document entry;
   the file exists on disk; first line is the canonical `NEW` status
   token.
2. **Applicability preflight:** `python scripts/bridge_applicability_preflight.py
   --bridge-id gtkb-session-wrap-procedure-001` returns
   `preflight_passed: true`, `missing_required_specs: []`.
3. **Clause preflight:** `python scripts/adr_dcl_clause_preflight.py
   --bridge-id gtkb-session-wrap-procedure-001` returns
   `Blocking gaps: 0`.
4. **Project linkage:** `Project Authorization`, `Project`, and
   `Work Item` metadata point at the active PAUTH and the live WI.
5. **Step-count invariants:** reviewer confirms Tier 1 has exactly 5
   MANDATORY steps, Tier 2 has exactly 4 CONDITIONAL-WITH-DEFAULT-ON
   steps, Tier 3 has exactly 1 CONDITIONAL step, Tier 4 has exactly
   2 OPTIONAL steps — totaling 12 candidate steps (matching DELIB-2238).
6. **Predicate determinism:** reviewer confirms each CONDITIONAL or
   CONDITIONAL-WITH-DEFAULT-ON step's predicate is expressible as a
   read-only query over envelope.json / MemBase / git state with no
   AI judgment.
7. **`--suppress` scope:** reviewer confirms `--suppress <step>` is
   accepted for Tier 2 steps only; MANDATORY rejection is explicit.
8. **No KB mutation in scope:** `kb_mutation_in_scope: false`; no
   `groundtruth.db` write is performed by this thread.

## Risk / Rollback

This proposal writes one file
(`bridge/gtkb-session-wrap-procedure-001-001.md`) and inserts one
entry pair (`Document:` + `NEW:`) in `bridge/INDEX.md`. Rollback is
a single `git restore` of `bridge/INDEX.md` and `rm` of the
versioned file (or a WITHDRAWN follow-on). The downstream spec
insertion (under the approval-packet path) is a separate gated
operation governed by `GOV-ARTIFACT-APPROVAL-001`.

If WI-4292's wrap-keyword spec changes shape during its NO-GO →
REVISED → GO cycle, this procedure spec may need a minor revision
to reference the final trigger surface form. The procedure body is
keyword-shape-agnostic (it executes regardless of which trigger
fired), so a revision would touch only the "Trigger surface"
references, not the 4-tier framework.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted
at the top of the `gtkb-session-wrap-procedure-001` document list
in `bridge/INDEX.md`; no prior version is deleted or rewritten
(append-only). `bridge/INDEX.md` remains the canonical workflow
state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — this bridge proposal is governance documentation; no
source / test / hook / configuration code is modified by this
thread.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
