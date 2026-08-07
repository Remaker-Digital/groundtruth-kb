REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: f9e95f49-a164-41e3-8b40-cb2b1f2351b1
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_review
Document: gtkb-wi5935-session-envelope-single-context
Version: 003
Responds to: bridge/gtkb-wi5935-session-envelope-single-context-002.md
Work Item: WI-5935
Project: PROJECT-GTKB-SESSION-ENVELOPE

# WI-5935 Slice A (REVISED) - Session-Envelope Single-Context Design Constraint: purge, not reclassify

## Why This Revision Exists

Version `-001` received `GO` at `-002`. This REVISED is **not** a response to a
review defect: the verdict was correct on the evidence available when it issued.
It exists because the **owner changed the requirement afterward**.

Owner decision 2026-08-07, archived as
`DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE`: a shared harness
session must **not exist in any role**, because it will distract and confuse
workers. The shared per-harness envelope must be **purged**, not retained in a
reduced classification.

Approved design point 4 in `-001` reads:

> The per-harness `harness-state/<harness>/session-envelope.json` is
> reclassified from authoritative state to a non-authoritative compatibility
> projection …

That is retention in a reduced role, which the owner has now rejected.

## The rejected design is ALREADY canonical (verified this session)

`-001`'s deliverable has already landed. `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001`
**exists at version 1**, `status: specified`, `type: design_constraint`, and its
description carries the rejected wording. Live census of the record this session:

| Term | Occurrences in DCL v1 |
| --- | --- |
| `compatibility projection` | 1 |
| `non-authoritative` | 1 |
| `reclassif`(y/ied) | 1 |
| `session-envelope.json` | 1 |
| `purge` | **0** |

Two consequences follow, and they change what this slice must do.

1. **This is a supersession, not a first recording.** `-001` described Slice A as
   recording a new DCL. That DCL now exists, so the corrected design must be
   captured as **`DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` v2 superseding v1**
   through the governed append-only path, not inserted fresh.
2. **The exposure is live, not pending.** The rejected retain-as-projection
   design is canonical governance right now. Any dependent slice, or any session
   consulting the DCL, will read the superseded design until v2 lands. This
   raises the priority of the correction from "before implementation" to
   "currently mis-stating owner intent."

**Thread-state note for the reviewer.** The bridge thread sits at `GO -002` with
no post-implementation report and no `VERIFIED`, yet the deliverable is present
in MemBase. This proposal does not attempt to reconcile that gap and makes no
claim about how the record was inserted; it is disclosed because a reviewer
comparing thread state to MemBase state will otherwise encounter the discrepancy
unannounced. Reconciling it is a separate governance matter.

`GO -> REVISED` is a lawful transition per `.claude/rules/file-bridge-protocol.md`
§ Post-Verdict Transition Table. `NO-ACTION` was considered and rejected: it is
defined as Prime rejecting a verdict *because the verdict does not comply with
applicable governance*, and would wrongly signal reviewer error where none
occurred.

## Design Decision To Be Recorded (DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001 **v2**, superseding v1)

Points 1, 2, 3, 5, 6 and 7 are **carried forward unchanged** from `-001`. Point 4
is replaced, and point 8 is added.

1. A session envelope is bound to exactly one session-context, identified by `session_id`.
2. `::wrap` (and any session close path) MUST fail closed when the live envelope's `session_id` does not equal the invoking session-context's `session_id`.
3. The constraint is uniform across all harnesses: no per-harness design. Harness differences are confined to how a harness surfaces its session id (runtime markers), never to the envelope-binding rule.
4. **(REPLACED)** The per-harness shared envelope artifact is **purged**. It is not authoritative, not a compatibility projection, not a hint, and not a fallback - it ceases to exist. The sole envelope artifact is the per-session document `harness-state/<harness>/session-envelopes/<session_id>.json`, which the code already maintains. No code path may create, read, write, or resolve through a per-harness shared envelope file after this work lands.
5. Mechanical enforcement is required (fail-closed precondition + tests), not convention alone.
6. `::wrap` harvests that session-context's output and updates the Source of Truth (MemBase/Deliberation Archive) for that context only.
7. Every interactive-session and bridge artifact carries a closing instruction (e.g. `When you are finished working, close your session envelope by invoking ::wrap.`).
8. **(NEW)** Envelope archival is a required outcome of a successful close. A closed per-session envelope MUST be archived where the deterministic handoff generator can find it, so that a close failure is the only condition that can suppress a handoff.

Supersedes: `DCL-SESSION-ENVELOPE-DURABILITY-001` v1 (per-harness authoritative state).

### Purge scope (explicit, to remove ambiguity at implementation time)

**In scope for purge** - both shared artifacts observed in this defect class:

- `harness-state/<harness>/session-envelope.json` - the per-harness current pointer named in `-001` point 4.
- `.claude/session/envelope.json` - the shared live envelope named in WI-5749.

**Explicitly NOT in scope** - the surviving authority:

- `harness-state/<harness>/session-envelopes/<session_id>.json` - the per-session documents.

## Sequenced Work-Item Breakdown (revised)

Slices A-F are retained; C and F are amended and G is added.

- **Slice A (this proposal).** Design DCL + breakdown. Gate for all other slices.
- **Slice B.** Revise `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001`: re-point the authoritative path to the per-session document, add the fail-closed session-id precondition, add the closing-instruction contract. Depends on A.
- **Slice C (amended).** Core fix: session-id-validated `close_session` / `run_wrap` / `ensure_current` resolving **only** the per-session document; add the goose runtime-marker entry to `RUNTIME_HARNESS_MARKERS` and goose membership to `scripts/gtkb_session_id.py`. **Amendment:** the regression test asserts **absence** of the shared artifact, not merely that it is never the write target. Depends on A + B.
- **Slice D.** Simple, intuitive wrap CLI ergonomics (`gt session wrap`). Depends on C.
- **Slice E.** Closing-instruction footer, uniform across interactive and bridge artifact surfaces. Depends on A; parallel to C/D.
- **Slice F (amended).** Cross-harness parity tests + `Cross-Harness Disposition` per `ADR-CROSS-HARNESS-PARITY-001`. **Amendment:** parity assertion covers absence of the shared artifact in every harness tree.
- **Slice G (new).** Purge migration: delete existing shared artifacts, remove all resolution paths that read them, and confirm no harness tree retains one. Depends on C.

## Evidence Motivating The Correction

Collected read-only in session `f60c8a1c-ab58-4887-a466-8b8444126390`:

- **The harm is observed, not projected.** Two independent interactive sessions (`7d9535ba` and `f60c8a1c`) hit the identical wrap failure in the same worktree on the same day. `gt session wrap` refused because the live envelope belonged to a foreign session-context (`3e141571-a2b8-4b01-9314-70e7ae1cbc71` in this session's case); `gt session handoff generate` then failed for want of an archived envelope. Neither session could write a `session_prompts` row, and both hand-wrote their handoff.
- **The authoritative document was intact throughout.** `harness-state/claude/session-envelopes/f60c8a1c-….json` existed at 4473 bytes, `status: open`, correctly owned. Only the shared pointer was contended - which is precisely why the shared artifact is the thing to remove.
- **Archival is unsatisfiable today.** `harness-state/claude/session-envelopes/archive` does not exist at all, so no claude session has ever archived an envelope. This motivates new design point 8; without it, purging the shared artifact would still leave handoff generation broken.
- **Frequency under the current operating model.** Per `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION`, all LO and PB work is owner-driven interactive sittings, frequently concurrent in one tree. Two collisions in one working day is the expected rate, not an edge case.

## Requirement Sufficiency

**New or revised requirement required before implementation.** That is the
purpose of this slice: it supersedes the live, incorrect
`DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` v1 with a v2 carrying the corrected
governing design decision. This authorizes requirement/
specification capture through the governed approval path only. It authorizes no
source, configuration, or test implementation; every dependent slice (B-G) files
its own proposal.

## Specification Links

- `DCL-SESSION-ENVELOPE-DURABILITY-001` v1 - superseded by the DCL this slice records (per-harness authoritative state).
- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` v1 - revised by Slice B.
- `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001` v1 - the `::wrap` trigger surface this work preserves.
- `ADR-ENVELOPE-META-MODEL-001` / `DCL-ENVELOPE-META-MODEL-001` - envelope three-part anatomy + containment conformance.
- `ADR-CROSS-HARNESS-PARITY-001` - cross-harness behavioral parity invariant; drives the uniform-across-harnesses requirement and Slice F.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - specification-linkage mandate this proposal satisfies.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED conditional on spec-derived tests; governs Slice C/F/G verification.
- `GOV-ARTIFACT-APPROVAL-001` - formal-artifact approval gate governing insertion of the DCL this slice records.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - state claims derive from fresh canonical reads; the basis for re-deriving the design rather than inheriting `-001`'s point 4.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance stance; the owner decision was preserved as a Deliberation Archive record rather than left in session context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development decision underlying that stance.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle triggers; an owner decision superseding an approved design is a capture-threshold event, discharged by the DELIB and the work-item supersession records.

## Owner Decisions / Input

- Owner instruction 2026-08-07, session `f60c8a1c`, verbatim in substance:
  *"WI-5541's proposed remedy is not sufficient. We do not want a shared harness
  session to exist. It will distract and confuse workers. We want to change our
  plan: it must be purged."* Archived as
  `DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE` (`outcome=owner_decision`).
- Owner AskUserQuestion 2026-08-07, same session: directed that the corrected
  REVISED be drafted in-session rather than deferred to a handoff.
- Supersession recorded on `WI-5935` and `WI-5541` status detail so no session
  implements the superseded design from the still-live `GO`.
- No owner waiver is requested in this version.

## Prior Deliberations

- `bridge/gtkb-wi5935-session-envelope-single-context-001.md` (NEW) / `-002.md` (GO) - the approved design this revision corrects.
- `DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE` - the governing owner decision.
- `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION` - establishes the concurrent-manual operating model that makes the collision routine.
- `WI-5541` - two same-day reproductions; its hint-based remedy is superseded here.
- `WI-5749` - shared `.claude/session/envelope.json` clobbering; a purge may close it rather than fix it.
- `WI-5815` - per-session envelope claim isolation (NO-GO `-004`); adjacent, not superseded.

## Specification-Derived Verification Plan

This slice mutates no source; its deliverable is a governance record. Verification
is therefore record-level, and the mechanical assertions are discharged by the
dependent slices named against each row.

| Specification / requirement | Verification | Discharged by |
| --- | --- | --- |
| `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` **v2** exists superseding v1 | `gt spec show DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` returns version 2 whose description contains `purge` and contains neither `compatibility projection` nor `reclassif`; v1 remains present as superseded history (append-only) | this slice |
| `GOV-ARTIFACT-APPROVAL-001` | formal-artifact approval packet present and content-hash matched before insertion | this slice |
| Design point 2 (fail-closed cross-context wrap) | session-id-validated close/wrap test | Slice C |
| Design point 4 (purge) | regression test asserting **absence** of any per-harness shared envelope artifact | Slices C + G |
| Design point 8 (archival) | close produces an archived envelope the handoff generator resolves | Slices C + D |
| `ADR-CROSS-HARNESS-PARITY-001` | parity test asserting absence across every harness tree | Slice F |

## Risk / Rollback

- **Risk: consumers still read the purged artifact.** Slice G is scoped to remove every resolution path, and Slices C/F/G assert absence rather than non-use, so a surviving reader fails the suite rather than silently degrading.
- **Risk: purge without archival breaks handoff generation permanently.** Mitigated by new design point 8; the archive precondition is already unsatisfiable today, so this is a repair of an existing break, not a new exposure.
- **Risk: this REVISED is read as a reviewer defect.** Explicitly disclaimed in § Why This Revision Exists; the `-002` GO was correct when issued.
- **Rollback:** this slice inserts one DCL record. Reverting means superseding that DCL through the same governed append-only path; no runtime state changes.

## Recommended Commit Type

- Recommended commit type: `docs:` - governance-record-only slice (DCL insertion plus this bridge chain); no source, configuration, or test mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
