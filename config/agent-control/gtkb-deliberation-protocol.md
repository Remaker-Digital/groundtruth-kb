# Deliberation Archive Protocol

This rule file defines mandatory behavior for both Prime Builder and Loyal
Opposition when interacting with the Deliberation Archive (SPEC-2098).

The active AI harness loads this file via AGENTS.md startup checklist item 15a
or via `.claude/rules/` auto-load.

## Canonical Terminology Anchored Here

The Deliberation Archive (DA) is one tier of ADR-0001's Three-Tier Memory
Architecture: **MemBase** (canonical knowledge and specifications;
`groundtruth.db`) / **MEMORY.md** (operational notepad; `memory/MEMORY.md` in
the GT-KB checkout, repo-root in scaffolded adopter projects per the
harness-memory vs dual-agent profile distinction) / **Deliberation Archive**
(this file's subject — design-reasoning record). Canonical-term references
to MemBase, MEMORY.md, and Deliberation Archive must use these exact forms;
see `.claude/rules/canonical-terminology.md` for the full glossary. Doctor's
canonical-terminology check enforces these strings in this rule file as part
of the dual-agent / harness-memory `required_files` contract.

## When To Search Deliberations

Both agents MUST search deliberations before starting substantive work:

### Prime Builder — Before Proposing
- Before writing any bridge proposal, run `search_deliberations()` for the
  target spec, work item, or component.
- If prior reviews exist: cite DELIB-IDs in the proposal's "Prior Deliberations"
  section and explain how this proposal differs from or builds on prior decisions.
- If a prior NO-GO rejected the same approach: explicitly acknowledge it and
  explain what changed.

### Loyal Opposition — Before Reviewing
- Before reviewing any NEW or REVISED bridge entry, search deliberations for
  the target spec/WI/component.
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
- Run the session-wrap harvest (`scripts/harvest_session_deliberations.py`)
  as part of `kb-session-wrap`.
- Sources: new LO reports, completed bridge threads (VERIFIED status),
  post-implementation reports, owner decisions from the session.

### Prime Builder — Owner Decisions
- When the owner makes a policy decision (via AskUserQuestion or direct
  instruction), archive it immediately as a deliberation with
  `source_type=owner_conversation` and `outcome=owner_decision`.
- Include the question, options presented, decision, and rationale.

### Loyal Opposition — Insight Reports
- Tag all `CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` reports with SPEC/WI IDs
  in a frontmatter-style header block for linkage coverage.
- Format: `Specs: SPEC-NNNN, SPEC-NNNN` and `WIs: WI-NNNN` near the top.

### Both Agents — Rejected Alternatives
- When a proposal is revised after NO-GO, the NO-GO rationale documents the
  rejected approach. The final GO version must reference what was rejected
  and why. This is the "decision + rejected alternatives" record.

## What NOT To Archive

- Bridge liveness/protocol chatter (< 100 bytes, routine acks)
- Duplicate content already in KB (idempotent via content_hash)
- Raw credential values (redaction handles AR-key patterns)
- Session start boilerplate

## Citation Format

When citing deliberations in proposals or reviews:
- Use `DELIB-NNNN` IDs when known
- Use `bridge/{name}-NNN.md` file refs when DELIB-ID not yet assigned
- Use `INSIGHTS-{date}-{topic}.md` for LO reports not yet harvested
