---
name: CTO trial onboarding docs push
description: Weekend deadline (2026-04-19) for CTO-trial adopter-onboarding doc rewrite; Codex GO'd scope at -002 with 7 conditions; paired with new canonical-terminology-surface workstream.
type: project
originSessionId: 3962ccef-cb65-4005-8e24-65c30a9f0ba2
---
**Trigger (2026-04-17):** CTO trial reviewer reacted to v0.5.0/v0.6.0 Start Here docs with prerequisite-level questions ("What is this for?", "Does this require me to install Claude Code?", "Do I install Claude Code or GT-KB first?"). Owner directive: docs must assume the target user knows very little about the problems GT-KB solves and has never used Claude Code.

**Deadline:** Owner told the CTO "later today or over the weekend" — effective end-of-weekend (~2026-04-19).

**Status:** Scope bridge `bridge/gtkb-start-here-adopter-rewrite-001.md` posted, Codex GO on `-002` with 7 implementation conditions. Two owner decisions still needed (SVG-vs-Mermaid rendering contract, synthetic-vs-actual-session protagonist).

**Codex GO conditions (`-002`):**
1. Resolve MemBase before diagram — treat as Core Knowledge Database / local SQLite `groundtruth.db` canonical spec tier, distinct from ChromaDB and MEMORY.md.
2. Use live evidence, not proposal-era numbers. Current collection is 1249 tests (commit `e12aab3`), not 1209. Cite command, commit, date, and source per metric.
3. Make the docs discoverable in `mkdocs.yml` nav.
4. Define the diagram rendering contract (Mermaid source approved; owner decides on committed SVG vs MkDocs-rendered).
5. Keep external install docs stable — link to Anthropic's Claude Code install with retrieval date, not copied steps.
6. Split owner-gated CTO-persona walkthrough from machine-verifiable Codex gates.
7. Run repo-native docs gates: `python scripts/check_docs_cli_coverage.py`, `python -m mkdocs build --strict`.

**Paired workstream (2026-04-17 ~12:20):** After Prime listed "MemBase" as an open clarification question despite the term being actively documented in `docs/architecture/product-split.md:13`, owner scoped a governance corrective workstream: `bridge/gtkb-canonical-terminology-surface-001.md`. Covers MemBase record in MemBase, CLAUDE.md/AGENTS.md glossary block, template inheritance, doctor check, bridge review gate. This is the system-level fix for the gap that made the Start Here rewrite necessary.

**Settled MemBase definition (owner 2026-04-17 12:16):** MemBase = authoritative, curated, schema-governed project truth (specs, tests, WIs, architecture decisions, procedures, env configs, validated documents). **Distinct** from Deliberation Archive (evidentiary working-process record, not authoritative) and MEMORY.md (operational notepad, not truth-making).

**How to apply:**
- Treat both scope bridge timelines as load-bearing. Codex GO on either is the gating event; do not defer.
- Three-tier memory vocabulary (`gtkb-docs-memory-architecture-alignment-editplan` VERIFIED) must be preserved.
- Azure-deployment block in the Start Here diagram must reference `docs/reference/azure-readiness-taxonomy.md`, not duplicate.
- Known-limitations section must cite live audit findings (Gap 2.8, 11-of-12 hook re-registrations, 20 U-class scaffold rows).
- If the canonical-terminology-surface bridge lands first, Start Here rewrite references the governed terminology record. If Start Here lands first, it carries the inline vocab table and the terminology-surface bridge propagates.
