NEW

# Implementation Proposal - Envelope Meta-Model ADR + DCL

bridge_kind: governance_review
Document: gtkb-envelope-meta-model-adr-dcl-001
Version: 001
Author: Prime Builder (Codex automation, owner prompt role)
Date: 2026-06-04 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4302
Recommended commit type: docs(bridge)

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

author_identity: Codex Prime Builder automation
author_harness_id: A
author_session_context_id: keep-working-2026-06-04T11Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation, Keep Working PB, PowerShell workspace-write

## Proposal Claim

Approve the body text for two downstream formal artifacts:

1. `ADR-ENVELOPE-META-MODEL-001` - defines the envelope conceptual model.
2. `DCL-ENVELOPE-META-MODEL-001` - defines conformance assertions for runtime and archived envelope records.

This bridge thread is a governance-review drafting proposal only. It does not
insert ADR/DCL rows into MemBase, generate formal-artifact approval packets, or
mutate runtime code. Downstream insertion remains a separate
formal-artifact-approval-packet operation under `GOV-ARTIFACT-APPROVAL-001`.

This proposal has precedence over WI-4301 runtime implementation because
WI-4301 is explicitly gated until the envelope governance WIs reach
bridge-VERIFIED, and WI-4302 is the meta-model spine the runtime slices cite.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`
- `PB-SESSION-WRAP-UP-PROACTIVE-001`

## Prior Deliberations

- `DELIB-20260658` - primary authority for the dispatch-optional refinement:
  `dispatch ?contains session contains topic`; synthetic dispatch envelope
  rejected; conformance assertions named.
- `DELIB-20260637` - generalized envelope meta-model: every envelope has
  invocation + intent hint + payload, and the original dispatch/session/topic
  containment framing.
- `DELIB-20260636` - envelope-program grilling and work-item formalization,
  including WI-4302 as the ADR + DCL conceptual spine.
- `DELIB-20260635` - owner folded dispatch/work-envelope design into the
  existing session-lifecycle envelope program.
- `DELIB-2500` - session/work envelope refinement and de-overloading lineage.
- `DELIB-2238` - session-envelope convention origin.
- `DELIB-20260648` - complementary init-keyword optionality refinement.

## Owner Decisions / Input

Existing owner evidence is sufficient for this drafting proposal.

- WI-4302 is `implementation_authorized`.
- `DELIB-20260658` records the owner-chosen dispatch-optional refinement and
  rejected synthetic-dispatch alternative.
- The owner-selected scope is: file a DELIB capturing dispatch optionality, then
  promote WI-4302; both steps are already complete.

No new owner decision is requested by this proposal. The later formal ADR/DCL
insertion still requires normal formal-artifact approval-packet evidence.

## Requirement Sufficiency

Sufficient. The ADR/DCL body below follows directly from `DELIB-20260658` and
keeps the downstream couplings from WI-4293, WI-4296, WI-4297, and WI-4301
explicit so runtime implementation cannot reinterpret the model.

## Proposed ADR Body

### `ADR-ENVELOPE-META-MODEL-001`

**Type:** architecture_decision

**Status:** specified

**Decision:** GT-KB adopts a qualified envelope meta-model with a three-part
anatomy and a dispatch-optional containment chain.

Every envelope has:

1. `invocation` - the explicit triggering action or source that opened the envelope.
2. `intent_hint` - the qualified envelope type the agent uses to disambiguate
   owner or dispatcher intent.
3. `payload` - deterministic context and prompt material needed to execute the
   envelope. Payload may include project ID, work item IDs, role, harness ID,
   model ID, prompt template text, generated prompt text, and other deterministic
   routing fields.

Containment is:

```text
dispatch ?contains session contains topic
```

The question mark means the dispatch tier is optional:

- Dispatched sessions use the full three-tier chain. A dispatch envelope wraps
  the session envelope; the session envelope contains zero or more topic envelopes.
- Interactive sessions skip the dispatch tier. The session envelope is the outer
  runtime wrapper and contains zero or more topic envelopes.

**Consequences:**

- Runtime `.claude/session/envelope.json` records the active session envelope
  and nested topic envelopes.
- Interactive sessions do not synthesize an empty dispatch envelope.
- Dispatched sessions record `dispatched_from_rule_id` and `dispatch_event_id`
  on the session envelope payload or metadata rather than adding a runtime
  `dispatch` parent field.
- The dispatcher records dispatch events separately in
  `.gtkb-state/dispatcher/log.jsonl` when persistence is enabled.
- WI-4293 must omit top-level dispatch state from the interactive runtime schema.
- WI-4296 owns dispatcher rules and dispatch-event persistence.
- WI-4297 project-completion drive emits dispatched sessions, never interactive
  sessions.
- WI-4301 runtime implementation must use this ADR as the conceptual spine for
  markers, state writing, wrap procedure, topic routing, and dispatch integration.

**Rejected alternatives:**

- Synthetic dispatch envelope for interactive sessions. Rejected because it
  adds mostly empty fields, makes conformance checks noisier, and implies a
  dispatch event occurred when none did.
- Treat dispatch, session, and topic as sibling envelope tiers. Rejected because
  the owner selected containment, not parallel categories.
- Use bare "envelope" as an overloaded term. Rejected by the de-overloading
  lineage; qualified terms are mandatory.

## Proposed DCL Body

### `DCL-ENVELOPE-META-MODEL-001`

**Type:** design_constraint

**Status:** specified

GT-KB envelope-producing and envelope-consuming code must satisfy these
assertions:

1. **Three-part anatomy:** every envelope instance recorded in
   `.claude/session/envelope.json` or its archive contains `invocation`,
   `intent_hint`, and `payload`. Missing any of the three fields is a
   conformance failure.
2. **Containment cardinality:** topic envelopes appear only under a session
   envelope `topics` array. No runtime process may create an orphan topic
   envelope outside a session envelope.
3. **Session root:** runtime `.claude/session/envelope.json` has a session
   envelope as its root object for interactive sessions.
4. **Dispatch optionality:** runtime `.claude/session/envelope.json` does not
   contain a top-level `dispatch` field for interactive sessions.
5. **Dispatched-session references:** dispatched sessions carry
   `dispatched_from_rule_id` and `dispatch_event_id` on the session envelope
   rather than as a parent containing envelope in runtime state.
6. **Dispatch-event persistence:** when dispatcher persistence is enabled,
   dispatch envelopes are recorded in `.gtkb-state/dispatcher/log.jsonl` or a
   successor dispatcher-event log, not in active interactive runtime session state.
7. **Qualified terminology:** code, specs, reports, and UI text use qualified
   envelope terms (`dispatch envelope`, `session envelope`, `topic envelope`,
   `authorization envelope`) whenever ambiguity is possible.

## Specification-Derived Verification Plan

| Spec / governing surface | Verification evidence expected |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` contains `Document: gtkb-envelope-meta-model-adr-dcl-001` with `NEW: bridge/gtkb-envelope-meta-model-adr-dcl-001-001.md`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal carries concrete governing specs plus the proposed ADR/DCL body. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header includes `Project Authorization`, `Project`, and `Work Item: WI-4302`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `gt backlog show WI-4302 --json` shows `approval_state: implementation_authorized`; PAUTH is cited in the header. |
| `GOV-ARTIFACT-APPROVAL-001` | This thread is terminal for body review only. Formal ADR/DCL insertion requires later approval packets with body hashes matching the approved body. |
| `ADR-ENVELOPE-META-MODEL-001` / `DCL-ENVELOPE-META-MODEL-001` | Post-packet insertion verification should query the live artifacts and confirm the body preserves dispatch optionality, three-part anatomy, and containment cardinality. |

## Acceptance Criteria

- LO confirms `DELIB-20260658` is carried forward accurately.
- LO confirms the ADR and DCL do not invent runtime implementation beyond the
  owner-approved WI-4302 scope.
- LO confirms the proposal does not authorize runtime code changes or MemBase
  mutation.
- LO confirms WI-4301 remains gated until the governance WIs reach the required
  bridge state.

## Risk And Rollback

Risk is limited to governance-body ambiguity. No code, DB row, approval packet,
or runtime state changes in this bridge step. If LO finds ambiguity, return
`NO-GO` with the exact sentence or assertion to revise. If the body is later
inserted and found defective, supersede through a later ADR/DCL version.

## Loyal Opposition Asks

1. Review the ADR/DCL body against `DELIB-20260658`, `DELIB-20260637`, and
   WI-4302.
2. Return `GO` if the proposal is sufficient for body approval; otherwise
   return `NO-GO` with concrete corrections.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
