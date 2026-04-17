# REVISED: Deliberation Archive Completion Proposal v2

## Proposal (Prime Builder → Codex Review)

**Source:** `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-12-00-58-DELIBERATION-ARCHIVE-COMPLETION-ADVISORY.md`
**Session:** S282
**Revision reason:** Owner requested behavioral protocol (CLAUDE.md + rules file) be included.

---

## Context

Same as v1. Phase 1 storage/API is complete (schema, CRUD, redaction, dedup,
ChromaDB code, backfill script, 111 tests). Live KB has zero deliberation rows.
This revision adds Phase C6: behavioral protocol for both agents.

## Owner Policy Decisions (2026-04-12)

| Question | Decision |
|----------|----------|
| Backfill scope | All 648 reports |
| ChromaDB semantic search | Required for completion |
| Harvest timing | Session wrap only |
| Behavioral protocol | Include in completion proposal (requested explicitly) |

---

## Phase C1: Controlled Backfill (P1)

_Unchanged from v1._ Run `scripts/backfill_lo_reports.py --apply`. Verify
`current_deliberations > 0`, idempotent rerun = 0 new rows, 0 redaction
survivors, no conflict reports with unreviewed GO/NO-GO.

**Files touched:** None (script execution + DB population)

---

## Phase C2: Enable ChromaDB Semantic Search (P1)

_Unchanged from v1._ Install `chromadb>=0.4.0` in `requirements-test.txt`,
run `gt deliberations rebuild-index`, create known-answer validation test
(`tests/unit/test_deliberation_search.py`, 10 curated queries, >= 80% top-3).

**Files created:** `tests/unit/test_deliberation_search.py`
**Files modified:** `requirements-test.txt`

---

## Phase C3: Session-Wrap Harvest (P1)

_Unchanged from v1._ Create `scripts/harvest_session_deliberations.py`, integrate
into `kb-session-wrap` skill. Idempotent via `upsert_deliberation_source()`.
Sources: new LO reports, completed bridge threads, owner decisions.

**Files created:** `scripts/harvest_session_deliberations.py`
**Files modified:** `.claude/skills/kb-session-wrap/SKILL.md`

---

## Phase C4: Archive Health Metrics (P2)

_Unchanged from v1._ Create `scripts/deliberation_health.py` and
`/check-deliberations` skill. 5 metrics: population, linkage, conflict
quarantine, redaction survivors, duplicate suppression.

**Files created:** `scripts/deliberation_health.py`, `.claude/skills/check-deliberations/SKILL.md`

---

## Phase C5: Traceability Repair (P2)

_Unchanged from v1._ Fix WI-3159 identity collision. Create
DOC-DELIB-COMPLETION in KB documenting the four completion states.

**Files modified:** KB records only

---

## Phase C6: Behavioral Protocol (P1) — NEW

**Goal:** Encode when and how both agents read from and write to the archive,
so the feature delivers value beyond the initial backfill.

### File 1: `.claude/rules/deliberation-protocol.md`

```markdown
# Deliberation Archive Protocol

This rule file defines mandatory behavior for both Prime Builder and Loyal
Opposition when interacting with the Deliberation Archive (SPEC-2098).

## When To Search Deliberations

Both agents MUST search deliberations before starting substantive work:

### Prime Builder — Before Proposing
- Before writing any bridge proposal, run `search_deliberations()` for the
  target spec, work item, or component.
- If prior reviews exist: cite DELIB-IDs in the proposal's "Prior Art" section
  and explain how this proposal differs from or builds on prior decisions.
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
```

### File 2: CLAUDE.md Addition

Insert after the "Knowledge Database Access" section (after line 201), before
"Session Wrap-Up & Handoff":

```markdown
### Deliberation Archive Protocol

**Deliberation search is mandatory before proposals and reviews.** See
`.claude/rules/deliberation-protocol.md` for full rules.

- **Before proposing:** Search `search_deliberations()` for prior reviews on the
  same spec/WI/component. Cite DELIB-IDs in proposals.
- **Before reviewing:** Search for prior deliberations. Add "Prior Deliberations"
  section to reviews.
- **Owner decisions:** Archive immediately as `source_type=owner_conversation`.
- **Session wrap:** Harvest runs automatically as part of `kb-session-wrap`.
- **LO reports:** Include SPEC/WI IDs in report headers for linkage coverage.
```

### Acceptance Criteria

- `.claude/rules/deliberation-protocol.md` exists and is loaded at session start
- CLAUDE.md contains the Deliberation Archive Protocol section
- Both agents can verify protocol compliance by checking proposals/reviews for
  "Prior Deliberations" sections

**Files created:** `.claude/rules/deliberation-protocol.md`
**Files modified:** `CLAUDE.md` (5-line addition)

---

## Updated Execution Order

| Phase | Priority | Dependencies | Scope |
|-------|----------|-------------|-------|
| C1: Backfill | P1 | None | Script execution |
| C2: ChromaDB | P1 | C1 | 1 test, 1 requirement |
| C3: Harvest | P1 | C1 | 1 script, 1 skill update |
| C6: Protocol | P1 | None (can land immediately) | 1 rules file, 1 CLAUDE.md edit |
| C4: Health metrics | P2 | C1 | 1 script, 1 skill |
| C5: Traceability | P2 | C1-C3 | KB records |

**C6 has no code dependencies** — it can land in the same commit as C1 or
independently. The protocol is useful immediately even before the archive is
populated (establishes the search-before-propose habit).

---

## Total File Count

| Action | Count |
|--------|-------|
| Files created | 7 (health script, health skill, harvest script, search test, deliberation protocol, `.gitkeep` placeholder if needed, check-deliberations skill) |
| Files modified | 3 (CLAUDE.md, requirements-test.txt, kb-session-wrap skill) |
| KB records | 2+ (DOC-DELIB-COMPLETION, WI-3159 repair) |

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
