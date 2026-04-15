# Deliberation Archive Protocol

This rule file defines mandatory behavior for both Prime Builder and Loyal
Opposition when interacting with the Deliberation Archive.

## When To Search Deliberations

Both agents MUST search deliberations before starting substantive work.

### Prime Builder — Before Proposing

- Before writing any bridge proposal, search the knowledge database for
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
- Duplicate content already in the knowledge database
- Raw credential values
- Session start boilerplate

## Citation Format

When citing deliberations in proposals or reviews:
- Use `DELIB-NNNN` IDs when known
- Use `bridge/{name}-NNN.md` file refs when DELIB-ID not yet assigned
