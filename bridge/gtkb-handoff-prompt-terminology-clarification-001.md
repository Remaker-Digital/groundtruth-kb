NEW

author_identity: Claude Code
author_harness_id: B
author_session_context_id: 544b584c-7392-4d40-81d8-dba187ba11eb
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code; interactive; Prime Builder; envelope closeout
author_metadata_source: prime-builder session; inline author metadata

# Implementation Proposal — Handoff Prompt vs. Session Prompt Terminology Clarification (WI-4363)

bridge_kind: implementation_proposal
Document: gtkb-handoff-prompt-terminology-clarification
Version: 001
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-05 UTC

Project: GTKB-SYSTEMS-TERMINOLOGY-MAP-001
Work Item: WI-4363
Recommended commit type: docs

target_paths: [".claude/rules/canonical-terminology.md"]

implementation_scope: protected_narrative_artifact_amendment
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Clarify the prompt vocabulary across the envelope/handoff program so future
proposals use one term per concept. Per owner decision `DELIB-20260883`
(`AskUserQuestion`, 2026-06-05), adopt the **generated-vs-stored** model:

- **handoff prompt** = the deterministic-service OUTPUT generated at session
  close (`::wrap`) by `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`.
- **Session Prompt** = the PERSISTED RECORD of that output (the
  `session_prompts` MemBase table; existing canonical glossary term
  "structured handoff message for next session").
- The two are two views of one thing (generator output vs. stored artifact).
  **No renames.**
- **"continuation prompt" is explicitly REJECTED** as a redundant third term.
  A terminology survey confirmed it has no canonical usage (one incidental hit
  in `memory/pending-owner-decisions.md`, a prose artifact, not a definition).

The proposal amends the canonical glossary
(`.claude/rules/canonical-terminology.md`) to (1) add a `handoff prompt`
glossary entry in the GT-KB vocabulary section style, cross-referencing
`Session Prompt`; and (2) cross-reference the existing `Session Prompt`
Supporting-Records row back to `handoff prompt`. No MemBase mutation; no spec
drafting; the only change surface is the protected narrative artifact.

## Proposed Glossary Amendment (exact text for review)

**(1) New vocabulary entry** (to be added in the GT-KB DA Read-Surface /
operational vocabulary section, alphabetically near other prompt/session
terms):

```
### handoff prompt

**Definition:** The deterministic-service OUTPUT generated at session close
(canonical `::wrap`) by the handoff-prompt generator
(`SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`). A handoff prompt is the
structured content that carries forward session context, continuation scope,
and next-step direction to the next session. It is *generated content*,
distinct from its *persisted record*.

**Canonical alias:** none. Do NOT use "continuation prompt" — that label is
explicitly rejected (per `DELIB-20260883`) as a redundant third term for the
same concept.

**Not to be confused with:** `Session Prompt` — the PERSISTED RECORD of a
handoff prompt (the `session_prompts` MemBase row; see Supporting Records). A
handoff prompt is the generator output; a Session Prompt is that output stored
as a governed record. Two views of one thing: the handoff prompt is what
`::wrap` produces; the Session Prompt is what persists it for the next session
to consume.

**Source:** `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (the generator);
`DELIB-20260883` (owner terminology decision: generated-vs-stored model;
"continuation prompt" rejected); WI-4363 (`GTKB-SYSTEMS-TERMINOLOGY-MAP-001`).

**Implementation pointer:** `groundtruth_kb.session.wrap` / the handoff-prompt
deterministic service invoked at canonical `::wrap`; persisted as a
`session_prompts` row (the Session Prompt record).
```

**(2) Supporting-Records row cross-reference** (amend the existing
`Session Prompt` row, line ~1575):

```
| Session Prompt | `session_prompts` | Structured handoff message for next session (the persisted record of a handoff prompt — see "handoff prompt") |
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge index authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in the verification plan below.
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` — the handoff-prompt generator that the new term names; the governing surface for "handoff prompt".
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval governance; the glossary edit is a protected narrative-artifact amendment requiring a per-file approval packet at implementation time.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact-approval-gate contract for the protected `.claude/rules/*.md` edit.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — the glossary is the agent-side DA read surface; the new entry cites its DA source (`DELIB-20260883`).
- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` — each glossary entry cites its DA/spec source (satisfied by the Source field above).
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` — session-lifecycle/wrap context where handoff prompts are produced.
- `GOV-STANDING-BACKLOG-001` — WI-4363 standing-backlog governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory.

### Requirement Sufficiency

Existing requirements sufficient. The governing requirement surface is
`SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` plus the owner terminology
decision `DELIB-20260883`. No new or revised requirement is needed before
implementation; the change is a glossary amendment recording an
already-decided vocabulary.

## Spec-Derived Verification Plan

| Spec / Acceptance Item | Test / Check | Expected |
|---|---|---|
| `DELIB-20260883` — "handoff prompt" defined as `::wrap` generator output | `grep -n "### handoff prompt" .claude/rules/canonical-terminology.md` | match present |
| `DELIB-20260883` — generated-vs-stored relationship recorded | grep for "persisted record of a handoff prompt" in the glossary | match present |
| `DELIB-20260883` — "continuation prompt" rejection recorded | grep for "continuation prompt" + "rejected" in the new entry | match present |
| `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` — entry cites DA source | grep for `DELIB-20260883` in the new entry's Source field | match present |
| Canonical-terminology integrity | `gt project doctor` canonical-terminology check | PASS / no new ERROR |
| Markdown lint (no structural breakage) | section renders; GOV-01-style line-count unaffected (target file is the glossary, not CLAUDE.md) | clean |

## Owner Decisions / Input

The proposal depends on owner approval; the authorizing evidence:

- **`DELIB-20260883`** (`source_type=owner_conversation`, `outcome=owner_decision`,
  2026-06-05) — owner Mike adopted the "Generated vs. stored" vocabulary model
  via `AskUserQuestion` (Option A of four: A generated-vs-stored [CHOSEN];
  B unify-on-Session-Prompt; C unify-on-handoff-prompt; D defer). The AUQ answer
  is mechanically recorded in `memory/pending-owner-decisions.md`
  (`detected_via: ask_user_question`).
- The owner decision approves the **direction** (the generated-vs-stored model
  and the continuation-prompt rejection). The **content-level** approval of the
  exact glossary text is a separate step: because the target is a protected
  narrative artifact, implementation requires a per-file
  formal-artifact-approval packet with `presented_to_user=true` and
  `transcript_captured=true` per `GOV-ARTIFACT-APPROVAL-001` /
  `DCL-ARTIFACT-APPROVAL-HOOK-001`. That packet will be created at
  implementation time citing this proposal's reviewed text and `DELIB-20260883`.

No additional owner decision is required for Loyal Opposition to review this
proposal.

## Prior Deliberations

- `DELIB-20260883` — owner terminology decision for WI-4363 (the basis for this proposal).
- Envelope-program deliberations establishing the handoff-prompt service and the
  three-part envelope anatomy: the WI-4299 handoff-prompt deterministic-service
  thread (`gtkb-handoff-prompt-deterministic-service-impl`, VERIFIED) and the
  WI-4302 envelope meta-model ADR thread.
- No retrieved deliberation rejects the generated-vs-stored model; `DELIB-20260883`
  is the governing decision.

## Risk and Rollback

**Risk after merge:** Minimal. The change is additive glossary text plus a
one-line cross-reference on an existing row. No code, no MemBase mutation, no
behavior change. The only governance surface is the protected narrative-artifact
edit, which is gated by its own formal-artifact-approval packet at
implementation time.

**Rollback:** Revert the single glossary commit. The `session_prompts` table,
the handoff-prompt service, and all envelope runtime behavior are unaffected.

## Notes for Loyal Opposition

This proposal carries the exact proposed glossary text inline for review so the
content can be assessed before the protected-file edit. The implementation phase
will (1) acquire the implementation-start authorization packet from this thread's
GO, (2) present the exact text to the owner and create the
formal-artifact-approval packet (narrative-artifact gate), then (3) apply the
edit and run the verification checks above. The continuation-prompt rejection is
owner-decided (`DELIB-20260883`); the survey evidence (one incidental,
non-definitional hit) is in the Claim section.

## Recommended Commit Type

`docs:` — glossary/terminology documentation amendment; no code or behavior change.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
