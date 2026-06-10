REVISED

# Implementation Proposal — Session Wrap Procedure Deterministic Trigger Spec (REVISED-2, governance_review)

bridge_kind: governance_advisory
Document: gtkb-session-wrap-procedure-001
Version: 003
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-session-wrap-procedure-001-002.md (NO-GO)

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

## Revision Claim

This REVISED-2 addresses the single P1 finding from the LO NO-GO at
`-002`: every live-state, predicate, topic-iteration, and archive
reference in the spec body is rewritten to use the per-harness
authoritative model from the GO'd sibling WI-4293
(`bridge/gtkb-session-envelope-durability-001-006.md`).

**Concrete changes from `-001`:**

1. Step #1 (envelope-state finalization): mutates
   `harness-state/<harness_name>/session-envelope.json` (not
   `.claude/session/envelope.json`).
2. Step #11 (topic auto-close): iterates open topic envelopes inside
   `harness-state/<harness_name>/session-envelope.json` (per WI-4293
   schema's embedded topics array).
3. Step #12 (envelope archive): renames the live per-harness file to
   `harness-state/<harness_name>/session-envelope-archive/<closed_at-ISO>-session-envelope.json`
   (the per-harness archive directory model from WI-4293's `-005`
   revision).
4. Step #12 (post-archive projection): adds an explicit substep that
   regenerates `.claude/session/envelope.json` as an OPTIONAL
   non-authoritative projection AFTER the authoritative per-harness
   mutation lands. Projection generation is best-effort; failure does
   NOT abort wrap.
5. Predicate-input table: `envelope.json state` source is now
   `harness-state/<harness_name>/session-envelope.json` (live
   authoritative file at wrap time); the `.claude/session/envelope.json`
   projection is listed as a secondary/optional source for
   read-only-projection-aware predicates.
6. Coupling block: WI-4293 sibling reference is updated to cite the
   per-harness model and the optional-projection clause.

**Terminology correction** (inherited from WI-4295 Slice 1 NO-GO at
`-002`): the term "work envelope" as a synonym for "topic envelope" is
dropped. Topic envelopes are the inner type-keyed records carried by
the per-harness session envelope. The session envelope is the outer
per-harness container. No "work envelope" usage remains in this
REVISED.

**Scope unchanged:** still governance_review with `target_paths: []`,
`requires_verification: false`, `kb_mutation_in_scope: false`. The
4-tier framework (5/4/1/2) and step-count invariants are unchanged
(MANDATORY steps #1, #4, #8, #11, #12 remain MANDATORY; only their
state-file references change).

## Same-Session Authoring (Skip-Own Interpretation)

This REVISED is authored by the same session that authored `-001`
(`35ed98f8-ae1c-4a5f-bf3f-219c579f144e`). The skip-own directive from
the autonomous /loop owner prompt prohibits same-session **verdict**
authoring (GO/NO-GO/VERIFIED) on a session's own proposals; it does
NOT prohibit same-session REVISED authoring in response to a
different-session NO-GO.

The LO verdict at `-002` was authored by Codex automation
`keep-working-lo` (harness A) — a different session. The fresh-eyes
review step has been performed. This REVISED acts on LO's specific
feedback (a deterministic, mechanical change) and does not bypass any
review step.

If owner intent is stricter (i.e., REVISED also requires a different
session), a future session may re-revise; the audit trail remains
intact via the append-only chain.

## Specification Links

Carried forward from `-001` (the NO-GO did not change spec linkage):

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical
  workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied
  by this Specification Links section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project
  metadata cites the active PAUTH covering WI-4294.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` —
  `requires_verification: false` because governance_review with
  `target_paths: []`; GO is terminal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files remain
  under `E:\GT-KB`; per-harness state path is under
  `E:\GT-KB\harness-state\<harness_name>\`.
- `GOV-ARTIFACT-APPROVAL-001` — downstream artifact requires
  formal-artifact-approval packet; not filed here.
- `GOV-STANDING-BACKLOG-001` — WI-4294 is `implementation_authorized`
  under the active PAUTH.
- `DCL-CONCEPT-ON-CONTACT-001` — terminology entry for "session
  envelope" / "topic envelope" lands in downstream rule-file edits.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Specs referenced (forward references; sibling WIs):**

- The wrap-keyword TRIGGER spec planned for sibling WI-4292 (bridge
  thread `gtkb-canonical-wrap-keyword-syntax-001`, NO-GO at -002,
  pending revise). Referenced by WI; spec id provisional.
- The topic-envelope router umbrella spec planned for sibling WI-4295
  Slice 1 (bridge thread `gtkb-work-envelope-router-slice-1-001`,
  NO-GO at -002, pending revise). Referenced by WI; spec id
  provisional.
- The session-envelope durability spec planned for sibling WI-4293
  (bridge thread `gtkb-session-envelope-durability-001`, GO at -006).
  Referenced by WI for path semantics; the spec id (a DCL drafted in
  that GO'd thread) is provisional until insertion.

**Specs drafted by this proposal:**

- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` (NEW; body
  rewritten below per F1 correction).

## Prior Deliberations

Carried forward from `-001`:

- `DELIB-2238`, `DELIB-2500`, `DELIB-20260637` — originating wrap-
  procedure deliberations and 3-part envelope anatomy.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic
  predicate requirement.
- `bridge/gtkb-session-envelope-durability-001-006.md` (GO; parallel
  session) — the per-harness authoritative state model that this
  REVISED aligns with.
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md` and `-002`
  NO-GO — the trigger surface; this procedure runs when that trigger
  fires.
- Auto-memory `feedback_latest_go_terminal_for_governance_review.md`
  — terminal-at-GO pattern applied here.

## Owner Decisions / Input

This governance-review REVISED is authorized by the active PAUTH; no
fresh AUQ is required:

1. **DELIB-20260648 (envelope-program PAUTH-minting)** — owner
   approved the envelope-program spec-WI batch (WI-4291..WI-4297)
   under `bridge_kind=governance_review`.
2. **DELIB-2238 + DELIB-2500** — originating wrap-procedure
   deliberations; the 12 candidate steps and wrap-outcome capture
   directives derive from these.
3. **Owner AUQ 2026-06-04 (envelope-project per-WI grill)** — direct
   authority for the 4-tier framework. WI-4294 `status_detail` records
   the AUQ outcome.
4. **DELIB-20260637 + DELIB-20260648** — the per-harness session-
   envelope state model authority (carried by WI-4293's GO at -006).

Owner-input dependencies downstream of GO:

- 1 formal-artifact-approval packet at MemBase insertion time.
- No source / hook / test mutation requested in this thread; the
  wrap-procedure implementation lands in WI-4301 (envelope-program
  implementation umbrella) Slice B.

## Requirement Sufficiency

Existing requirements sufficient. The owner-grilling AUQ for WI-4294
captured the complete 4-tier framework. The per-harness state model is
sourced from the GO'd WI-4293 (no fresh owner AUQ required). No new
owner requirement is needed to draft and approve the rewritten spec
body.

## Findings Addressed

### F1 — P1 — Wrap procedure targets the rejected shared session-envelope path

**LO observation summary:** the `-001` spec body referenced
`.claude/session/envelope.json` at lines 239-245 (step #1), 253-258
(step #11), 259-263 (step #12), and 304-318 (predicate inputs). The
GO'd sibling (WI-4293 `-006`) authorizes only the per-harness
`harness-state/<harness_name>/session-envelope.json` as the live state
target, with archive under
`harness-state/<harness_name>/session-envelope-archive/`. The shared
`.claude/session/envelope.json` exists only as an optional
non-authoritative projection.

**Response — every offending reference is corrected in the rewritten
spec body below:**

| Original location | Correction |
|-------------------|------------|
| Step #1 envelope-state target | `harness-state/<harness_name>/session-envelope.json` |
| Step #11 topics iteration source | same per-harness file |
| Step #12 live file rename source | same per-harness file |
| Step #12 archive target | `harness-state/<harness_name>/session-envelope-archive/<closed_at-ISO>-session-envelope.json` |
| Predicate-input table source | per-harness file is authoritative; `.claude/session/envelope.json` listed as optional projection |
| Coupling block reference | updated to per-harness model |

New step #12 substep: regenerate `.claude/session/envelope.json` as
an optional non-authoritative projection AFTER the per-harness
mutation. Projection failure does NOT abort wrap.

**No other LO findings.** Positive confirmations from `-002`
(governance-only metadata, PAUTH coverage, applicability+clause
preflights, 4-tier step counts) are unchanged by this REVISED.

## Scope Changes

None. Same governance_review scope; same 4-tier framework; same
12-step inventory; same target_paths/requires_verification/
kb_mutation_in_scope metadata.

## Spec Body — SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001 (REVISED-2 draft)

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
provisional during WI-4292's bridge cycle.

**Authoritative state path** (per WI-4293 sibling at `-006` GO): the
session envelope live state is
`harness-state/<harness_name>/session-envelope.json`. The
`<harness_name>` token resolves from `harness-state/harness-identities.json`
at session-open time. The shared `.claude/session/envelope.json`
exists only as an optional non-authoritative projection.

### Tier 1 — MANDATORY (5; always run; no override)

1. **Envelope-state finalization.** Set `closed_at` (ISO-8601 UTC) and
   `wrap_outcome` (string) on the active session envelope in
   `harness-state/<harness_name>/session-envelope.json` per the
   WI-4293 schema. The `wrap_outcome` value is supplied by the
   wrap-trigger context or defaults to `manual_wrap` (NL or `::wrap`
   keyword) / `auto_closed_by_session_wrap` (recursive from a wrap
   invocation on an outer scope).
4. **DA harvest IF uncaptured decisions exist.** Predicate-gated
   subset of `gt deliberations harvest`. Predicate: at least one
   in-session deliberation candidate exists per the harvest helper's
   inclusion rules. If predicate false, this step is a no-op (cheap).
8. **Working-tree state attestation.** Run `git status --short` (or
   equivalent) and record the resulting state in the closing envelope
   record. Does NOT auto-commit or auto-stash. Attestation only.
11. **Topic auto-close.** Iterate open topic envelopes inside the
    session envelope at
    `harness-state/<harness_name>/session-envelope.json` (per WI-4293
    schema's embedded topics array). For each open topic, set its
    `close_outcome=auto_closed_by_session_wrap` and `closed_at`. The
    topic-router (per sibling WI-4295 Slice 1's umbrella spec)
    treats this as a MEDIUM auto-close: the topic's dispatch-to-
    service still runs deterministically.
12. **Session-envelope archive.** Two substeps:
    - **12a (authoritative).** Rename the live per-harness file from
      `harness-state/<harness_name>/session-envelope.json` to
      `harness-state/<harness_name>/session-envelope-archive/<closed_at-ISO>-session-envelope.json`
      (per WI-4293's archive-path model). Unset the live per-harness
      file (no placeholder; next `::init` opens a fresh one).
    - **12b (optional projection regeneration).** Regenerate
      `.claude/session/envelope.json` as an OPTIONAL non-authoritative
      projection AFTER 12a lands. Projection generation is
      best-effort; failure does NOT abort wrap. The projection is a
      read-only reflection of the now-archived state for tooling that
      reads the legacy shared path.

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

| Predicate input | Source (authoritative) |
|------------------|------------------------|
| session-envelope state | `harness-state/<harness_name>/session-envelope.json` (live per-harness file at wrap time) |
| MemBase rows | `groundtruth.db` read-only queries |
| Git state | `git status`, `git diff --stat`, `git rev-parse HEAD` |

The `.claude/session/envelope.json` projection MAY be consulted by
predicates that explicitly opt-in to the projection (read-only,
allowing-stale-data semantics); the authoritative path remains the
per-harness file.

Predicates are **deterministic**: same inputs at the same wrap
moment produce the same boolean. No AI judgment is consulted in
predicate evaluation. The wrap-trigger layer is a service, not an
agent (per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`).

**`--suppress <step>` plumbing:**

CONDITIONAL-WITH-DEFAULT-ON steps support a wrap-time suppression
flag. Example: `::wrap --suppress task_list_preservation` skips
step #5 for this one wrap. MANDATORY steps do NOT support
`--suppress` (the flag is rejected with an error).

**Recursion guard:**

The procedure is not idempotent on re-entry: invoking `::wrap`
during a wrap-in-flight is a parse-time error (or silently dropped
by the wrap-trigger layer). Implementation detail; the procedure
itself assumes single-instance execution per wrap.

**Step ordering:**

The four tiers execute in order: Tier 1 → Tier 2 → Tier 3 → Tier 4.
Within Tier 1, steps run in the order #1 → #4 → #8 → #11 → #12
(envelope-state first, archive last). Within step #12, substeps run
12a → 12b (authoritative mutation before projection regeneration).
Tier 2 / 3 / 4 ordering is implementation-defined; the spec does not
constrain it.

**Failure handling:**

A MANDATORY step failure aborts the wrap; the session remains "open"
and the failure is reported. EXCEPTION: step #12b (projection
regeneration) is best-effort even though it is part of a MANDATORY
step; failure of 12b is logged but does NOT abort wrap (12a is the
authoritative mutation; 12b is a downstream convenience). A
CONDITIONAL-WITH-DEFAULT-ON, CONDITIONAL, or OPTIONAL step failure
is logged but does NOT abort the wrap.

**Couplings (by sibling WI):**

- Sibling WI-4293 (`bridge/gtkb-session-envelope-durability-001-006.md`
  GO): the per-harness session-envelope schema (live state at
  `harness-state/<harness_name>/session-envelope.json`; archive at
  `harness-state/<harness_name>/session-envelope-archive/`; optional
  projection at `.claude/session/envelope.json`). All Tier-1 file
  references in this procedure use the per-harness model from this
  sibling.
- Sibling WI-4292
  (`bridge/gtkb-canonical-wrap-keyword-syntax-001-002.md`
  NO-GO; pending revise): the trigger surface; this procedure runs
  when that trigger fires.
- Sibling WI-4295 Slice 1
  (`bridge/gtkb-work-envelope-router-slice-1-001-002.md` NO-GO;
  pending revise): the topic-router; step #11's MEDIUM auto-close
  semantic delegates to the topic-router's per-type dispatch.

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — the wrap procedure implementation (per WI-4301 Slice B)
   contains exactly 5 MANDATORY step identifiers AND uses the
   per-harness session-envelope path verbatim. Expected-failing
   until WI-4301.
2. `grep` — at least one regression test exercises the `--suppress`
   plumbing on a CONDITIONAL-WITH-DEFAULT-ON step. Expected-failing
   until WI-4301.
3. `grep_absent` — the implementation MUST NOT write to
   `.claude/session/envelope.json` as a live mutation target. The
   projection regeneration in step #12b is the only acceptable
   write to that path, and only AFTER 12a has archived the
   per-harness file.

**Owner directive citation:** "S-2026-06-04 owner grilling: formalize
envelope program (WI-3468)" (per WI-4294 `source_owner_directive`).

**Related deliberations:** `DELIB-2238`, `DELIB-2500`, `DELIB-20260637`,
`DELIB-20260648`.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing
Preflight Subsection. Re-run after this REVISED entry is added to
`bridge/INDEX.md`. Expected `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`, no
blocking clause gaps. The CLAUSE-IN-ROOT absolute-home-path failure
pattern that fired in `-001` is mitigated in this REVISED: the
per-harness state path uses `harness-state/<harness_name>/` (an
in-root relative path); the optional projection mention uses the
in-root `.claude/session/envelope.json` path; no absolute
home-directory paths remain.

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
formal-artifact-approval packet.

Reviewer verification of THIS REVISED:

1. **F1 correction:** every offending `.claude/session/envelope.json`
   reference from `-001` (lines 239-245, 253-258, 259-263, 304-318)
   is rewritten to use the per-harness authoritative model. Reviewer
   greps the new spec body for the offending string and confirms it
   appears only inside step #12b (projection regeneration substep)
   and the predicate-input "optional projection" note.
2. **Bridge mechanics:** `bridge/INDEX.md` has
   `REVISED: bridge/gtkb-session-wrap-procedure-001-003.md` inserted
   at the top of the document entry; the file exists on disk; first
   non-blank line is the canonical `REVISED` status token.
3. **Applicability + clause preflights** pass with no blocking gaps.
4. **Project linkage** metadata unchanged from `-001`.
5. **Step-count invariants** unchanged (5/4/1/2 = 12).
6. **No KB mutation in scope** unchanged.

## Risk And Rollback

This REVISED writes one file
(`bridge/gtkb-session-wrap-procedure-001-003.md`) and inserts one
`REVISED:` line at the top of the
`gtkb-session-wrap-procedure-001` document entry in
`bridge/INDEX.md`. Rollback is a single `git restore` of
`bridge/INDEX.md` and `rm` of the versioned file.

If LO surfaces additional findings, a `-005` REVISED can address
them (incremental refinement). The audit trail remains intact via
the append-only chain.

## Bridge Filing (INDEX-Canonical)

This REVISED is filed under `bridge/` with a `REVISED:` entry
inserted at the top of the `gtkb-session-wrap-procedure-001`
document list in `bridge/INDEX.md` (above the LO `-002` NO-GO line).
No prior version is deleted or rewritten (append-only).
`bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — this REVISED is governance documentation; no source /
test / hook / configuration code is modified by this thread.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
