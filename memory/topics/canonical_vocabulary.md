---
name: Canonical vocabulary (interim stopgap)
description: Startup-visible definitions for MemBase, DA, MEMORY.md, GT-KB, Prime Builder, Loyal Opposition, pending the gtkb-canonical-terminology-surface bridge implementation.
type: reference
originSessionId: 3962ccef-cb65-4005-8e24-65c30a9f0ba2
---
**Status:** Interim stopgap until `bridge/gtkb-canonical-terminology-surface-002.md` (Codex GO 2026-04-17) is implemented. Canonical record will live in MemBase as `DOC-CANONICAL-TERMINOLOGY`; this memory topic file is the pre-implementation shim so the definitions are auto-loaded at session start.

**Authority:** Owner settlement recorded as `DELIB-0715` (2026-04-17 12:16 PM). Lineage: see `MEMBASE-4-CLAUDE.md` (repo root, 858 lines) and `DELIB-0105` (GroundTruth Rename Transition).

## Terms

**MemBase** — the authoritative project knowledge base: curated, labeled, schema-governed project truth. Durable facts, decisions, specs, accepted architecture, work-item state, validated project knowledge. Currently implemented as `groundtruth.db` (Agent Red) and `knowledge.db` (GT-KB adopter template). **Not** the same as `groundtruth.db` the file — that's the implementation; MemBase is the governed-truth concept.

**Deliberation Archive (DA)** — the evidentiary working-process record. Preserves discussions, reasoning, searches, attempts, decision trails, LO reviews, bridge threads, owner decisions. **Not itself authoritative truth** — it is evidence of deliberation, not the conclusion. Physically lives in the `deliberations` table of the same SQLite file as MemBase, but epistemically distinct.

**MEMORY.md / memory topic files** — operational notepad and handoff aid. Useful for continuity. **Does not make anything true.** Auto-loaded from the Claude Code harness path `~/.claude/projects/<project-hash>/memory/`, not the repo `memory/` directory (per `CLAUDE.md:10`).

**GT-KB / GroundTruth KB** — the product and toolkit brand. Encompasses MemBase + DA + MEMORY.md contract + hooks + skills + templates + governance rules. The engineering method, not any single component.

**Knowledge Database** — the broad platform-internal term for MemBase. Still used in some Agent Red docs (`CLAUDE.md:19`, `CLAUDE-ARCHITECTURE.md:225`). Preferred user-facing term is now **MemBase**; Knowledge Database is retained for historical compatibility.

**ChromaDB / search index** — optional retrieval layer. Lives at `.groundtruth-chroma/`. **Not authority** — it indexes MemBase and DA for semantic search; it doesn't contain canonical truth.

**Prime Builder** — Claude Code (Opus 4.6+). Creates, manages, maintains implementation artifacts. Proposes specifications, implements approved changes, runs tests, keeps the system internally consistent. Responsible for the *how* during implementation.

**Loyal Opposition** — GPT-5.3-Codex. Inspects, critiques, analyzes plans, code, prompts, hooks, permissions, configuration. Produces evidence-based reports. Does not implement or modify existing files without explicit owner authorization.

## Epistemic hierarchy

| Layer | Role | Stored in |
|-------|------|-----------|
| MemBase | Authoritative curated truth | `specifications`, `tests`, `work_items`, `documents`, etc. tables |
| Deliberation Archive | Evidence of process | `deliberations` table |
| MEMORY.md / topic files | Operational continuity | `~/.claude/projects/<hash>/memory/` markdown |

## Governance rule

A term is "operationally governed" only if it is present in the always-loaded startup surface (CLAUDE.md, AGENTS.md, MEMORY.md glossary, scaffold templates, doctor checks). Presence in prior conversations, DA entries, or standalone docs is **insufficient**. This file is the interim MEMORY.md-resolved stopgap until `gtkb-canonical-terminology-surface` lands the permanent CLAUDE.md/AGENTS.md glossary blocks.

## What to do when you encounter an unfamiliar term

1. Search DA first: `search_deliberations("<term>")`.
2. Grep repo root for standalone canonical docs (e.g., `MEMBASE-4-CLAUDE.md`).
3. Check memory topic files (`memory/*.md`).
4. Only after all three come up empty should the term be flagged as genuinely novel.
