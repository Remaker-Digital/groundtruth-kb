---
name: Canonical terminology requires startup-visible governance
description: A term is only operationally governed if present in always-loaded session surface (CLAUDE.md, AGENTS.md, MEMORY.md glossary block, scaffold templates, doctor checks). Presence in DA, standalone docs, or topic files is insufficient.
type: feedback
originSessionId: 3962ccef-cb65-4005-8e24-65c30a9f0ba2
---
**Rule:** Before drafting any bridge proposal, run `search_deliberations()` for all non-trivial terms used. If a term is used without an auto-loaded definition in the active session surface, stop and verify — do not treat the term as "unfamiliar" until after a full DA + docs + memory-topic-file check.

**Why:** 2026-04-17 governance failure on `bridge/gtkb-start-here-adopter-rewrite-001.md`. Prime Builder listed "MemBase" as an open clarification question despite:
- `MEMBASE-4-CLAUDE.md` (858 lines, Agent Red repo root) defining the pattern in full.
- `memory/project_groundtruth_lineage.md` citing `Evolves from membase-4-claude`.
- 10 Deliberation Archive entries covering the term (DELIB-0020 through DELIB-0229 span).
- `groundtruth-kb/docs/architecture/product-split.md:13` defining "Core Knowledge Database (MemBase)" in live published docs.
- `bridge/gtkb-mass-adoption-readiness-001.md:47` listing "MemBase-4-Claude" as adoption track #5.

The term is well-established. The failure was Prime's: neither the deliberation-protocol.md pre-proposal DA search nor a cross-check against standalone canonical docs was performed. Owner framing: **"If a fresh Claude chat does not know 'MemBase,' then the system has not yet made the concept sufficiently durable, discoverable, and startup-visible."**

**How to apply:**
1. Every bridge proposal draft runs `search_deliberations()` on the central terms. Cite DELIB-IDs. This is already the deliberation-protocol rule — self-enforce even when the hook does not trigger.
2. If a term is used in the draft but does not have a definition in an auto-loaded control file (CLAUDE.md, AGENTS.md, MEMORY.md glossary, CLAUDE-REFERENCE.md), flag it as a governance gap in the bridge — do not flag it as a content ambiguity.
3. When proposing new canonical terms, list propagation targets (MemBase record + CLAUDE.md glossary + template + doctor check) per the `gtkb-canonical-terminology-surface` bridge's review-gate.
4. Trust the owner's reaction: if they say "we settled this", the settlement is real; the failure is retrieval, not ambiguity.

**Systemic corrective in flight:** `bridge/gtkb-canonical-terminology-surface-001.md` (NEW as of 2026-04-17). Its verification gate is a fresh-session probe — ask "what is MemBase" at session start and confirm the answer comes from auto-loaded surface, not DA cross-reference.
