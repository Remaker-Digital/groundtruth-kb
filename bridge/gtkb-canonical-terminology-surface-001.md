# Scope Proposal: Canonical Terminology Surface

**Status:** NEW
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Origin:** Owner directive 2026-04-17 ~12:20 PM following the MemBase-recognition governance failure on `gtkb-start-here-adopter-rewrite-001`.
**Target repos:** Agent Red Customer Engagement + groundtruth-kb (template propagation).
**Priority bias:** Owner-flagged as the corrective workstream. Runs alongside (or ahead of) `gtkb-start-here-adopter-rewrite` so canonical definitions exist when the adopter rewrite ships.

## Problem Statement (owner framing, verbatim)

> "A term can be 'known' in prior conversations, bridge reports, or GT-KB docs, but if it is not present in the startup files, glossary, scaffold templates, and retrieval/check procedures used by a fresh agent session, then it is not operationally governed."
>
> "This is exactly the kind of thing MemBase is supposed to prevent. If a fresh Claude chat does not know 'MemBase,' then the system has not yet made the concept sufficiently durable, discoverable, and startup-visible."

**The trigger incident:** On 2026-04-17, Prime Builder drafted `gtkb-start-here-adopter-rewrite-001.md` and listed "MemBase" as an **open clarification question** even though:
- `MEMBASE-4-CLAUDE.md` (858 lines, repo root) defines the pattern in full.
- `memory/project_groundtruth_lineage.md` cites `Evolves from membase-4-claude`.
- The Deliberation Archive contains 10 deliberations on the term, including `DELIB-0105` "GroundTruth Rename Transition".
- `groundtruth-kb/docs/architecture/product-split.md:13` defines "Core Knowledge Database (MemBase)" — live published doc.
- `bridge/gtkb-mass-adoption-readiness-001.md:47` lists "MemBase-4-Claude" as adoption track #5.

None of those entry points are in the **always-loaded control surface** of a fresh Prime session (CLAUDE.md, AGENTS.md, CLAUDE-REFERENCE.md, CLAUDE-ARCHITECTURE.md — zero MemBase matches across all four).

## Owner Specification Language (GOV-09 trigger)

Owner directive, verbatim:

> I would treat this as a new backlog/workstream item, probably: `gtkb-canonical-terminology-surface`.
>
> Scope should include:
> 1. Add a canonical Terminology / Glossary record set in MemBase.
> 2. Define MemBase, Deliberation Archive, MEMORY.md, Knowledge Database, GroundTruth KB, GT-KB, Prime Builder, and Loyal Opposition.
> 3. Add a startup-visible glossary block to Agent Red's CLAUDE.md / AGENTS.md equivalents.
> 4. Add a GT-KB template update so newly scaffolded projects inherit the terminology.
> 5. Add a doctor/check rule: if ADR-0001 terminology is missing or inconsistent across CLAUDE.md, AGENTS.md, MEMORY.md, docs, and templates, flag it.
> 6. Add a bridge review gate: new canonical terms require explicit propagation targets before GO.

## Prior Deliberations (cited per deliberation-protocol.md)

- `DELIB-0020` / `DELIB-0021` / `DELIB-0022` / `DELIB-0023` — original Membase-4-Claude productization, platform spec, backlog, structural separation (2026-03-26).
- `DELIB-0105` — GroundTruth rename transition (2026-04-12).
- `DELIB-0109` — Membase evaluation and implementation (2026-03-28).
- `DELIB-0215` / `DELIB-0229` — S238/S240 advisory reviews keeping the term in live process (2026-04-12).
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-008.md` (VERIFIED 2026-04-13) — three-tier memory vocabulary (CLAUDE.md / MEMORY.md / topic files). This work lands alongside it.
- `bridge/gtkb-adr-memory-architecture-006.md` (VERIFIED 2026-04-13) — ADR-0001 governs memory architecture; owner's check-rule explicitly names it.
- `MEMBASE-4-CLAUDE.md` (repo root) — 858-line canonical pattern doc. Glossary at lines 738–775 is the anchor for Phase 1 content.
- `groundtruth-kb/docs/architecture/product-split.md:13` — "Core Knowledge Database (MemBase)" definition in live published docs.

## Scope (in)

**Deliverable A — MemBase terminology record set (Agent Red):**
1. Insert a `Terminology` glossary as a `documents` artifact in MemBase (`groundtruth.db`) with `category='governance'`, `tags=['terminology','adr-0001']`, versioned under append-only rules.
2. Cover the owner-listed 8 terms at minimum (MemBase, Deliberation Archive, MEMORY.md, Knowledge Database, GroundTruth KB, GT-KB, Prime Builder, Loyal Opposition) plus the full `MEMBASE-4-CLAUDE.md` glossary (artifact types, supporting records, concepts).
3. Each term: definition + "not to be confused with" + source citation (originating DELIB or doc) + implementation pointer (table name, file path, or URL).

**Deliverable B — Startup-visible glossary block:**
1. Add a glossary section to `CLAUDE.md` (Prime's auto-load) and `AGENTS.md` (Codex's auto-load). Must be concise enough to fit the 300-line CLAUDE.md cap (GOV-01); detail lives in the MemBase record. CLAUDE.md carries the inline block + a pointer to the MemBase record.
2. Add a `CLAUDE-TERMINOLOGY.md` (or append to `CLAUDE-REFERENCE.md`) that mirrors the MemBase record for read-only at-boot use without a DB query.
3. Update `memory/MEMORY.md` header block with a one-line "glossary lives at X, MemBase record Y" pointer.

**Deliverable C — GT-KB template inheritance:**
1. Update `groundtruth-kb/templates/CLAUDE.md`, `templates/MEMORY.md`, and related scaffolded files so `gt init` produces a project with the terminology block present by default.
2. Update `groundtruth-kb/templates/rules/prime-builder.md` and `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md` to reference the glossary.
3. New projects start already operationally governed on terminology.

**Deliverable D — Doctor check rule:**
1. Add a `gt doctor` check (or extension of existing doctor) that scans `CLAUDE.md`, `AGENTS.md`, `MEMORY.md`, `docs/` tree, and `templates/` for terminology presence and consistency against the ADR-0001 canonical set.
2. Inconsistencies (missing terms, conflicting definitions) flagged with specific file:line evidence.
3. Owner's ADR-0001 reference: the current `bridge/gtkb-adr-memory-architecture-006.md` VERIFIED memory-architecture ADR is the one named. If that ADR is renamed/re-ID'd, the doctor rule tracks to the canonical ADR.

**Deliverable E — Bridge review gate:**
1. Update `.claude/rules/deliberation-protocol.md` or add a new rule `.claude/rules/canonical-terminology-propagation.md` requiring: any bridge proposal that introduces a NEW canonical term must list its propagation targets (MemBase record, CLAUDE.md glossary, template, doctor check) before Codex issues GO.
2. Codex review template updated to include a propagation-target line item.
3. This converts canonical-term creation from a judgement call into a mechanical governance step.

## Scope (out)

- Not rewriting MEMBASE-4-CLAUDE.md. The 858-line pattern doc stays as the long-form reference; the glossary block is a distilled subset.
- Not ingesting all of MEMBASE-4-CLAUDE.md into MemBase as a single document (it's too large for that role). The glossary subset + a pointer is sufficient.
- Not rewriting any existing user-facing docs (that is the Start Here rewrite's scope). This bridge produces the vocabulary they reference.
- Not changing ADR-0001 content. Doctor rule references the existing ADR; if ADR-0001 needs refinement, that is a separate bridge.

## Proposed Spec Inventory

After Codex GO, record in MemBase (`type=requirement`, `tags=['canonical-terminology','governance']`):

| # | Draft ID | Requirement |
|---|----------|-------------|
| 1 | SPEC-TERMINOLOGY-RECORD | A canonical terminology record set MUST live in MemBase as a governed document artifact with append-only versioning. |
| 2 | SPEC-TERMINOLOGY-MINIMUM-SET | The record MUST define at minimum the 8 owner-listed terms (MemBase, DA, MEMORY.md, Knowledge Database, GroundTruth KB, GT-KB, Prime Builder, Loyal Opposition) and the full `MEMBASE-4-CLAUDE.md` glossary. |
| 3 | SPEC-TERMINOLOGY-STARTUP-VISIBLE | CLAUDE.md (Prime) and AGENTS.md (Codex) MUST contain a startup-visible glossary block or pointer loaded by default at session start. |
| 4 | SPEC-TERMINOLOGY-TEMPLATE-INHERITANCE | GT-KB scaffold templates MUST produce projects where the terminology block is present by default on `gt init`. |
| 5 | SPEC-TERMINOLOGY-DOCTOR-CHECK | `gt doctor` MUST flag missing or inconsistent terminology across CLAUDE.md, AGENTS.md, MEMORY.md, docs, and templates, referenced against ADR-0001. |
| 6 | SPEC-TERMINOLOGY-BRIDGE-GATE | The bridge review gate MUST require new canonical terms to list propagation targets before GO. |
| 7 | SPEC-TERMINOLOGY-ASSERTION | A machine-verifiable assertion MUST exist on SPEC-TERMINOLOGY-STARTUP-VISIBLE, e.g., `grep "MemBase" CLAUDE.md` returns ≥1 match. Runs at session start via the existing assertion-check hook. |

## Open Questions

**For owner:**
1. **Scope of "MemBase" implementation-agnostic definition.** Your 12:16 message distinguished MemBase (authoritative truth) from DA (evidentiary) from MEMORY.md (operational). Is the canonical terminology record the correct place to formalize that hierarchy, or do you want that hierarchy in ADR-0001 itself with the terminology record pointing to it?
2. **Glossary block size in CLAUDE.md.** CLAUDE.md is capped at 300 lines (GOV-01). A concise glossary block covering 8 terms + pointers fits; the full glossary (MEMBASE-4-CLAUDE.md lines 738–775) does not. Is the concise + pointer pattern acceptable?
3. **Doctor check severity.** Missing canonical term → ERROR (fails doctor), WARN (logs), or INFO? My default: ERROR for missing; WARN for minor inconsistency.
4. **Template propagation timing.** Should template updates land in the same v0.6.1 release as the Start Here rewrite, or as a separate docs-and-governance release?

**For Codex:**
1. Is `templates/rules/prime-builder.md` the right file for the GT-KB template pointer, or is there a better template file for this role?
2. Is there an existing `gt doctor` extension point, or does this need a new subcommand?
3. Should the bridge review gate live in `.claude/rules/deliberation-protocol.md` (existing) or in a new file `.claude/rules/canonical-terminology-propagation.md`?
4. Are there canonical terms I'm missing from the owner's 8 that should also be in the minimum set? (Candidates: "Work Item", "Specification", "Test Plan", "Backlog", "Protected Behavior", "Assertion Run".)

## Implementation Approach (overview)

**Phase 1 — Spec recording:** insert 7 specs into MemBase + 1 WI per spec.

**Phase 2 — Content:** draft the terminology record as a `documents` artifact. Draft the CLAUDE.md / AGENTS.md glossary blocks. Draft the CLAUDE-TERMINOLOGY.md (or CLAUDE-REFERENCE.md update).

**Phase 3 — Templates:** apply the same blocks in groundtruth-kb templates. Verify `gt init` produces a project with terminology block present.

**Phase 4 — Doctor check:** implement the check in the existing doctor infrastructure. Add tests.

**Phase 5 — Bridge review gate:** update the rule file + Codex review template. Add tests.

**Phase 6 — Release:** decide v0.6.1 combined with Start Here rewrite, or separate governance release.

## Verification Approach

- Machine-verifiable: the assertion on SPEC-TERMINOLOGY-STARTUP-VISIBLE runs at session start.
- `gt doctor` emits zero terminology flags on the post-implementation tree.
- Fresh-clone test: a new clone + `gt init` on an empty dir produces a project whose CLAUDE.md contains the glossary block.
- Self-consistency: a grep of "MemBase" across the full tree shows no stale or conflicting definitions.
- Fresh-session probe: at the next Prime session start, asking "what is MemBase" should hit an auto-loaded definition, not require cross-referencing.

## Timeline

- **2026-04-17 (today):** scope bridge NEW (this file). Codex reviews overnight.
- **2026-04-18:** on GO, Phase 1–2 begin. Phase 3 may start in parallel.
- **2026-04-19:** Phase 4–5 land. CTO-persona: a fresh session trying to answer "what is MemBase" without cross-reference.
- **Post-weekend:** Phase 6 release decision.

This work is timed to complete before or alongside the Start Here rewrite so its product docs reference governed terminology rather than the other way around.

## Relationship to `gtkb-start-here-adopter-rewrite`

- The Start Here rewrite depends on canonical terminology being present somewhere authoritative. Codex's GO conditions on `-002` (condition 1: resolve MemBase) implicitly acknowledge this.
- If this bridge lands first, the Start Here rewrite references the governed terminology record directly.
- If the Start Here rewrite lands first, it will carry the vocabulary reconciliation table inline; this bridge will then propagate those definitions into the startup surface and reconcile anything that drifted.
- Both paths are fine. Owner to advise on preference.

## Rollback / Containment

- All changes reversible via git revert.
- No KB mutations until Codex GO.
- No production impact.
- Doctor check is additive; if it proves too aggressive, severity can be downgraded without reverting the record.

## Next Steps After Codex GO

1. File implementation bridge `gtkb-canonical-terminology-surface-implementation-001.md`.
2. Execute Phases 1–5.
3. Post-implementation report + Codex VERIFIED.
4. Release decision per Open Question 4.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
