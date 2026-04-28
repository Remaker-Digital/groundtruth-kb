---
name: S299 governance lessons — durability test results
description: S299 exposed three governance gaps (terminology surface, DA harvest coverage, session-decision durability). Agreements + decisions + next-session carryover checklist so nothing is lost at session boundary.
type: project
originSessionId: 3962ccef-cb65-4005-8e24-65c30a9f0ba2
---
**Why this exists:** Owner diagnosis 2026-04-17 ~1:05 PM: "We are leaving sessions with too many directives unactioned, and they are lost. If we start a fresh session, all of our agreements and shared understanding is not durable. This is exactly what the DA was intended to resolve, but this session has been a test of what we implemented and we have found gaps."

This file is the durable carryover record for S300+ so the operational understanding reached this session is not lost at session boundary.

## Three governance gaps exposed this session

1. **Terminology surface gap.** Canonical terms (MemBase, DA, MEMORY.md, GT-KB, Prime Builder, Loyal Opposition) exist in prior DA entries, standalone docs (`MEMBASE-4-CLAUDE.md` 858-line repo-root doc), and GT-KB templates — but **not in the always-loaded control surface** (CLAUDE.md, AGENTS.md, MEMORY.md). A fresh Prime session could (and did) treat MemBase as unfamiliar. Remediation: `bridge/gtkb-canonical-terminology-surface-002.md` (Codex GO, 6 conditions, 2 owner decisions pending).

2. **DA harvest coverage gap.** Only 60 of 785 bridge files (~7.6%) have DA entries with bridge source_ref. Of 720 DA entries, 649 (~90%) are `lo_review` type. Owner conversations, bridge threads, and governance-diagnosis documents are under-harvested. Transcripts from S280+ branding discussions (Apr 13, 16, 17) contain 34+, 84+, 85+ mentions never reaching DA. Remediation: harvest-coverage policy + scope bridge proposed to owner for decision on whether to fold into canonical-terminology-surface or file separately.

3. **Session-decision durability gap.** Agreements reached in session are lost unless mechanically archived. Owner directive, Codex GO conditions, pinned implementation decisions — all at risk of dissolving at context rollover. Remediation: this file + DELIB-0715 (MemBase definition) + DELIB-0716/0717/0718 (bridge thread summaries).

## S299 artifacts (all durable, all searchable)

**Deliberations archived this session:**
- `DELIB-0715` — MemBase Canonical Definition (Owner Settlement 2026-04-17)
- `DELIB-0716` — Bridge Thread: gtkb-canonical-terminology-surface
- `DELIB-0717` — Bridge Thread: gtkb-start-here-adopter-rewrite
- `DELIB-0718` — Bridge Thread: gtkb-start-here-adopter-rewrite-implementation

**Bridge threads active (all Codex-GO with conditions):**
- `gtkb-canonical-terminology-surface-002` — GO; 6 implementation conditions; 2 owner decisions pending (MEMORY.md target, doctor severity)
- `gtkb-start-here-adopter-rewrite-002` — GO (scope); retired after implementation bridge filed
- `gtkb-start-here-adopter-rewrite-implementation-002` — GO (implementation); pins Mermaid-only + protagonist "Allison"; awaits implementation execution

**Memory files added/updated:**
- `memory/canonical_vocabulary.md` (new, type=reference, stopgap definitions)
- `memory/project_cto_trial_onboarding_docs.md` (corrected — was wrong about MemBase)
- `memory/feedback_canonical_terminology_governance.md` (new, rule for pre-proposal DA search)
- `memory/project_s299_governance_lessons.md` (this file)

## Owner decisions pending at session boundary (CRITICAL — do not let these dissolve)

1. **Start Here diagram rendering:** Mermaid-only (pinned by implementation-001), committed SVG, or both? Codex accepted Mermaid-only.
2. **Day-in-the-life protagonist:** synthetic "Allison" (pinned by implementation-001) or re-narration of actual S299 GT-KB session?
3. **Agent Red MEMORY.md target:** (a) harness-resolved only, (b) new repo-root MEMORY.md with CLAUDE.md:10 update, or (c) no Agent Red MEMORY.md edit this phase?
4. **Doctor severity defaults:** ERROR for missing required startup terms, WARN for minor drift — accept or adjust?
5. **DA harvest coverage remediation:** separate `gtkb-da-harvest-coverage-001` bridge or fold into `gtkb-canonical-terminology-surface` as Phase 7?

**S300 bootstrap action:** first turn must read this file, read `canonical_vocabulary.md`, then either present these 5 decisions to owner OR process owner's pre-session answers. Do NOT start implementation work before these clear.

## What needs to be "encoded and enforced" before this is truly durable

Owner directive 2026-04-17 ~1:05 PM: "encoded and enforced". Not enough to document — must be mechanically checked. Items that the canonical-terminology-surface + harvest-coverage work must land:

1. **Encoded:** canonical vocabulary in CLAUDE.md/AGENTS.md glossary block; MemBase `DOC-CANONICAL-TERMINOLOGY` record; GT-KB template inheritance.
2. **Enforced:** `gt project doctor` rule flagging missing terminology; bridge review gate requiring propagation targets for new canonical terms; session-start assertion that glossary is loaded; session-wrap harvest failure is LOUD not silent.
3. **Retroactive:** one-time sweep of the ~130 historical bridge threads to bring DA bridge coverage from 7.6% toward ≥95%.

## How to apply at S300 start

1. Read `canonical_vocabulary.md` first — get vocab before any other work.
2. Read this file — understand what decisions are pending.
3. Run `search_deliberations()` per `.claude/rules/deliberation-protocol.md` before drafting anything.
4. Present the 5 pending decisions to owner; do not proceed until answered.
5. Then resume implementation of either/both Tier-1 bridges depending on decisions.
