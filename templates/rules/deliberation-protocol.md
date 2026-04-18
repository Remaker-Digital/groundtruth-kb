# Deliberation Archive (DA) Protocol

This rule file defines mandatory behavior for both Prime Builder and Loyal
Opposition when interacting with the Deliberation Archive (DA).

The Deliberation Archive (DA) is the design-reasoning tier of ADR-0001: Three-Tier Memory Architecture. MemBase holds specifications and canonical knowledge; MEMORY.md is the operational notepad; the DA holds the why.

## When To Search Deliberations

Both agents MUST search deliberations before starting substantive work.

### Prime Builder — Before Proposing

- Before writing any bridge proposal, search MemBase (and the DA) for
  prior deliberations on the target spec, work item, or component.
- If prior reviews exist: cite DELIB-IDs in the proposal's "Prior Deliberations"
  section and explain how this proposal differs from or builds on prior decisions.
- If a prior NO-GO rejected the same approach: explicitly acknowledge it and
  explain what changed.

### Loyal Opposition — Before Reviewing

- Before reviewing any NEW or REVISED bridge entry, search deliberations for
  the target spec or work item.
- If prior reviews exist: add a "Prior Deliberations" section to the review.
  Cite DELIB-IDs. Flag if the proposal revisits a previously rejected approach
  without acknowledging it.
- If no relevant prior deliberations exist: state "No prior deliberations
  found for [topic]."

### Both Agents — Before Creating WIs or Specs

- Search deliberations for the topic before creating new artifacts.
- Check for rejected alternatives that would make the new artifact redundant
  or contradictory.

## When To Archive Deliberations

### Prime Builder — Session Wrap

- Run the session-wrap harvest as part of session cleanup.
- Sources: new Loyal Opposition reports, completed bridge threads (VERIFIED
  status), post-implementation reports, owner decisions from the session.

### Prime Builder — Owner Decisions

- When the owner makes a policy decision, archive it immediately as a
  deliberation with `source_type=owner_conversation` and
  `outcome=owner_decision`.
- Include the question, options presented, decision, and rationale.

### Both Agents — Rejected Alternatives

- When a proposal is revised after NO-GO, the NO-GO rationale documents the
  rejected approach. The final GO version must reference what was rejected
  and why.

## What NOT To Archive

- Bridge liveness/protocol chatter (routine acks, status pings)
- Duplicate content already in MemBase
- Raw credential values
- Session start boilerplate

## Citation Format

When citing deliberations in proposals or reviews:
- Use `DELIB-NNNN` IDs when known
- Use `bridge/{name}-NNN.md` file refs when DELIB-ID not yet assigned

## Canonical Term Propagation Gate

Any bridge proposal that introduces a NEW canonical term — a term that will
appear in MemBase records, startup files, templates, or the doctor check —
MUST list its propagation targets before Loyal Opposition issues GO:

1. **MemBase record** — where the canonical definition will live (spec ID or
   document ID).
2. **CLAUDE.md glossary pointer** — confirm the term appears in the
   CLAUDE.md glossary block or explicit pointer to
   `.claude/rules/canonical-terminology.md`.
3. **AGENTS.md glossary pointer** — confirm the term appears in the
   AGENTS.md glossary block (dual-agent profiles).
4. **`.claude/rules/canonical-terminology.md`** — confirm the term is defined
   with not-to-be-confused-with, source, and implementation pointer.
5. **Doctor check coverage** — if the term is profile-required, confirm
   the required-term list in `.claude/rules/canonical-terminology.toml` is
   updated.

Reviews that introduce canonical terms without these propagation targets
must be returned NO-GO with a propagation-targets finding. This converts
canonical-term creation from a judgement call into a mechanical governance
step (per SPEC-TERMINOLOGY-BRIDGE-GATE).
