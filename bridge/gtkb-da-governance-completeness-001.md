# Scope Proposal: Deliberation Archive Governance Completeness

**Status:** NEW
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb` (product scope — this is GT-KB governance plumbing, not Agent Red-specific)
**Relationship to in-flight work:** extends, does not duplicate, `bridge/gtkb-da-harvest-coverage-implementation-005.md` (Codex GO; covers bridge-thread compression + retroactive sweep + bridge-thread coverage doctor).

## Problem Statement

Codex self-assessment 2026-04-17: the Deliberation Archive is NOT ready to serve as a governance memory backbone without additional controls. Confidence levels:

| Dimension | Current confidence |
|-----------|--------------------|
| DA contains substantial historical value | Medium-high |
| DA is complete for useful documents | **Low** |
| DA is complete for session transcripts | **Very low** |
| DA is used consistently and correctly during sessions | Low to medium |
| DA is ready as governance memory backbone without additional controls | **No** |

Concrete evidence (Codex 2026-04-17 audit):
- 722 current DA rows vs 1,020 candidate sources → **315 source refs with no current DA row** (304 bridge files, 11 LO reports).
- 71 verdict-parsing warnings in dry-run → even harvested content is partially unreliable.
- MemBase incident (this session): canonical term not retrievably present in always-loaded context, forcing Prime governance failure on `gtkb-start-here-adopter-rewrite-001` before owner caught it manually.
- Procedural rule (deliberation-protocol.md) for pre-proposal search — no mechanical enforcement; Prime can skip without blocking.

The in-flight `gtkb-da-harvest-coverage` work addresses bridge-thread compression and retroactive bridge-thread sweep **only**. That is one slice of ~8 pieces needed. This bridge scopes the remaining 7.

## Owner Settlements (via AskUserQuestion 2026-04-17 ~2:40 PM)

| # | Decision | Settlement |
|---|----------|------------|
| 1 | Scope approach | File umbrella scope bridge now (not wait / not split per piece) |
| 2 | Preflight gate enforcement | **Hard block** via PreToolUse hook (not soft warning / not post-hoc doctor) |
| 3 | Transcript handling | **Extract owner decisions + key discussions** (not raw transcripts / not no-harvest) |

## Prior Deliberations (cited per deliberation-protocol.md)

- `DELIB-0715` — MemBase canonical definition (triggering owner conversation).
- `DELIB-0716`, `DELIB-0717`, `DELIB-0718` — first examples of bridge-thread compression (harvested manually).
- `DELIB-0719` — S299 owner decision round including separate-bridge decision for harvest coverage.
- `DELIB-0105`, `DELIB-0020`–`0023`, `DELIB-0109` — Membase historical deliberation trail (proved retrievable via DA search after failure).
- `bridge/gtkb-da-harvest-coverage-implementation-005.md` (Codex GO) — the in-flight bridge whose scope this umbrella extends.
- `scripts/harvest_session_deliberations.py` line 7 header comment — current source classes (LO insight reports, VERIFIED bridges, GO bridge proposals). Documented as incomplete.
- `.claude/rules/deliberation-protocol.md` — the rule that failed to enforce mechanically.

## Scope (in) — the 7 pieces NOT covered by harvest-coverage

### A. LO-report coverage closure

- 11 LO reports in `CODEX-INSIGHT-DROPBOX/` currently lack DA rows per Codex audit.
- Extend harvest script to enumerate all `CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` files and cross-check against existing DA `source_type='lo_review'` entries by `source_ref`.
- Retroactive backfill for the 11 gaps with owner-approval dry-run pattern (same as bridge-thread sweep).
- Going forward: wrap-hook asserts that every LO report filed in the session is in DA before wrap completes.

### B. Owner-decision extraction policy (automation of today's manual work)

- Today's DELIB-0715, DELIB-0719 were inserted by Prime manually after owner prompt. That doesn't scale.
- **Policy:** every `AskUserQuestion` response + explicit owner specification-language message (GOV-09 trigger) is archived as `source_type='owner_conversation'` at the end of the turn.
- **Implementation:** hook on post-`AskUserQuestion` completion that captures Q, options, chosen option, any free-text notes, and inserts a DELIB with structured metadata.
- **Implementation:** detection of GOV-09 specification-language patterns ("must", "should", numbered requirements) in owner prompts → insert as `source_type='owner_conversation'` with the prompt content (redacted if credential patterns detected).

### C. Transcript extraction (owner decisions + key discussions)

- Raw transcripts stay out of DA (noise).
- **Extracted material:** owner-decision messages, specification-language messages, substantive design discussions (both sides — Prime and owner).
- **Heuristic:** session-wrap scans the session transcript (`~/.claude/projects/<hash>/*.jsonl`) for owner messages ≥ 50 chars + Prime response patterns indicating substantive discussion. Extracted content → DA as `source_type='session_harvest'` with reference back to session_id and transcript filename.
- **NOT** the full JSONL content; only the extracted pair-level discussions.

### D. Redaction gates

- DA content is not git-tracked per-se (lives in `groundtruth.db`) but is searchable and exportable.
- Pre-insert redaction: scan content for credential patterns (Azure keys, OpenAI keys, ACS tokens, bearer tokens, JWT patterns, connection strings) using existing `credential_patterns` canonical module.
- Match → redact to `[REDACTED:<pattern-name>]` and tag `redaction_state='redacted'` with `redaction_notes` populated.
- Verification: test that known-credential-pattern content fails pre-insert validation and is redacted correctly before storage.

### E. Source-ref identity rules (formalized)

- Current DA has 59 `bridge_thread` rows: 3 canonical wildcard + 56 legacy file-level (Codex audit).
- Formalize canonical source-ref conventions per source_type:
  - `bridge_thread` → `bridge/{thread-name}-*.md`
  - `lo_review` → `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-{date}-{topic}.md`
  - `owner_conversation` → `{YYYY-MM-DDTHH:MM}-{topic-slug}`
  - `session_harvest` → `session:{session-id}:{turn-range}`
  - `report` → path to the report file or `methodology-review:{topic}` for legacy compat
- Validation in `insert_deliberation()` / `upsert_deliberation_source()`: reject inserts whose `source_ref` doesn't match the canonical pattern for its `source_type`.

### F. Missing-source backfill framework

- Generalize the bridge-thread retroactive sweep pattern into a reusable backfill framework covering LO reports, owner conversations (pre-policy archives), and any source class with historical gaps.
- Framework provides: dry-run JSON schema, owner-approval gate, idempotent-via-content-hash insert, post-run coverage evidence.
- Future source classes (e.g., ADRs, post-impl reports) use the same framework.

### G. Session preflight gate — HARD BLOCK (owner decision)

- **PreToolUse hook** intercepts `Write` tool calls targeting `bridge/*-001.md` (new bridge proposals).
- Blocks the Write if no `search_deliberations()` / equivalent DA search call has been made in the current turn's conversation history.
- Error message directs Prime to run the search first.
- This is the mechanical enforcement that would have prevented the 2026-04-17 MemBase governance failure.
- Configurable to also cover Codex-side proposal writes (`bridge/*` writes by Codex before submitting review).

### H. Session wrap gate (expanded)

- Beyond just "harvest ran without errors", wrap-hook asserts:
  - All LO reports from this session present in DA
  - All `AskUserQuestion` interactions from this session archived as `owner_conversation`
  - All bridge-thread activity from this session archived (if VERIFIED threads completed)
  - Session-transcript extraction ran and produced zero errors
  - Redaction gate ran on all inserts this session

## Scope (out)

- Full raw transcript ingestion (owner decision #3 — extraction only).
- Code for harvest-coverage bridge-thread pieces (handled by `gtkb-da-harvest-coverage-implementation-005` and its follow-on).
- DA schema changes beyond what's needed for `redaction_state` / `redaction_notes` (already exist in schema per Codex evidence).
- Cross-project harvesting (this bridge is for Agent-Red-as-dogfood-adopter + GT-KB-as-product; other adopter projects inherit via template).

## Proposed Spec Inventory (for Codex review)

After Codex GO, record in GT-KB MemBase (`type=requirement`, `tags=['da-governance','completeness']`):

| # | Draft ID | Requirement |
|---|----------|-------------|
| 1 | SPEC-DA-GOV-LO-COVERAGE | Every LO report filed in a session MUST reach DA before session wrap completes; coverage gap triggers ALARM. |
| 2 | SPEC-DA-GOV-OWNER-DECISION-CAPTURE | Every AskUserQuestion response and every GOV-09 specification-language owner message MUST be archived as `owner_conversation` by end of turn. |
| 3 | SPEC-DA-GOV-TRANSCRIPT-EXTRACT | Session-wrap MUST extract owner decisions + substantive discussions from session transcripts into DA as `session_harvest`, MUST NOT ingest raw transcript text verbatim. |
| 4 | SPEC-DA-GOV-REDACTION | All DA inserts MUST run through credential-pattern redaction before storage; `redaction_state` populated accordingly. |
| 5 | SPEC-DA-GOV-SOURCE-REF-IDENTITY | `insert_deliberation()` MUST validate `source_ref` against canonical pattern for the given `source_type`; invalid rejects. |
| 6 | SPEC-DA-GOV-BACKFILL-FRAMEWORK | Reusable missing-source backfill framework MUST exist, callable for any supported source class with idempotent content-hash dedupe. |
| 7 | SPEC-DA-GOV-PREFLIGHT-HARDBLOCK | PreToolUse hook MUST hard-block Write to `bridge/*-001.md` without prior `search_deliberations()` in the same turn. |
| 8 | SPEC-DA-GOV-WRAP-GATE | Session wrap-hook MUST assert LO/owner-conversation/bridge/transcript coverage before marking wrap complete; any gap → ALARM. |

## Open Questions for Codex

1. Should the PreToolUse hook have a bypass mechanism for emergency bridge work (e.g., infrastructure repair like the S294 hook-tracking fix)? If yes, bypass should require explicit session-local configuration, not permanent.
2. Owner-decision extraction from GOV-09 — how to tune detection signal (simple keyword match vs LLM-based classification)? v1 keyword-based, v2 improve?
3. Transcript extraction heuristic — is ≥50 chars + response pattern sufficient, or should we use a more semantic filter?
4. Redaction gate — should redacted content be stored redacted (current model) or should the original be unretrievable entirely? Current model preferred for audit completeness.
5. Source-ref validation — breaking change for existing `DELIB-0712` (methodology_review legacy anomaly) and 56 file-level bridge_thread rows. Validation activates only for NEW inserts; legacy rows grandfathered. Confirm?
6. Relationship to `gtkb-canonical-terminology-surface` implementation — the terminology-surface bridge review gate covers canonical-term propagation. This bridge's preflight gate covers DA-search-before-proposal. Both are preflight gates; should they share hook infrastructure?

## Open Questions for Owner

1. Scope for "substantive discussion" in transcript extraction — owner comfortable with heuristic-based extraction, or want a manual annotation pass for v1?
2. Redaction gate severity — should failed redaction (credential-pattern match that can't be cleanly redacted, e.g., in middle of structured data) be BLOCK (insert rejected) or WARN (stored with `redaction_state='partial'`)?
3. Preflight bypass — is there any scenario where you'd want to override the hard block? If yes, what authorization?

## Implementation Approach (high level, not binding)

**Phase 1 — Spec recording:** 8 specs into GT-KB MemBase.

**Phase 2 — Redaction gate (A, first because foundational):** implement pre-insert redaction in `src/groundtruth_kb/db.py` using existing `credential_patterns` module.

**Phase 3 — Source-ref identity rules:** validation + tests for each source_type pattern.

**Phase 4 — LO-report coverage extension (A):** extend harvest script + retroactive backfill for the 11 gaps.

**Phase 5 — Owner-decision + transcript extraction (B, C):** AskUserQuestion post-hook + GOV-09 detector + transcript extractor.

**Phase 6 — Preflight hook (G):** PreToolUse implementation + tests.

**Phase 7 — Wrap-gate expansion (H):** assertions beyond harvest success.

**Phase 8 — Backfill framework generalization (F):** refactor bridge-thread sweep into reusable framework.

**Phase 9 — Dogfooding:** run end-to-end on a fresh session; confirm every discussed term is searchable, every owner decision captured, preflight blocks attempted bad-proposal Write, wrap-gate catches simulated gaps.

**Phase 10 — Post-impl + Codex VERIFIED.**

## Timeline

- **2026-04-17:** scope bridge NEW (this file). Codex review overnight.
- **2026-04-18–19:** on GO, Phases 1–9 in sequence (or parallel where independent). Several phases are subagent-friendly.
- **2026-04-20:** Post-impl + VERIFIED target.

## Rollback / Containment

- Phase 2 (redaction): if gate rejects content that should be stored, immediate session impact. Mitigation: WARN-level by default for v1, tighten to BLOCK after baseline proven.
- Phase 6 (preflight hook): if false-positive blocks legitimate work, bypass flag exists (still requires session-local enable).
- Phase 3 (source-ref validation): legacy rows grandfathered; only new inserts validated.
- All changes reversible via git revert + optionally clearing DA rows inserted since the change landed (if any problem surfaces).

## Next Steps After Codex GO

1. File implementation bridge `gtkb-da-governance-completeness-implementation-001.md`.
2. Execute Phases 1–10 on feature branch in GT-KB.
3. Dogfood in fresh session, verify gate behavior.
4. VERIFIED + merge.
5. This becomes the DA's mechanical governance backbone going forward.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
