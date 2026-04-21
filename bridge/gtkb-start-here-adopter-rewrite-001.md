# Scope Proposal: GT-KB Start Here Adopter Rewrite

**Status:** NEW
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb` (docs), cross-cutting with Agent Red
**Timeline driver:** Owner committed CTO trial material delivery "later today or over the weekend" (2026-04-17 through ~2026-04-19).

## Context

CTO trial reviewer reacted to the v0.5.0/v0.6.0 Start Here docs with basic-questions feedback, verbatim:

> "What is this for? I don't get it. Does this require me to install Claude Code? How do I use Claude Code to write software? Do I have to install GT-KB first or do I install Claude Code first or does GT-KB include the Claude Code install?"

Owner diagnosis (2026-04-17, follow-up): the Start Here and README must assume the reader **knows very little about the problems GT-KB solves and has not used Claude Code before**, and must answer prerequisite questions *before* reaching installation. Installation itself must assume only a Windows machine with internet.

This is adopter-onboarding gap, not feature gap. The v0.5.0/v0.6.0 docs were written for a reader already fluent in the problem space.

## Owner Specification Language (GOV-09 trigger)

Captured verbatim from the 2026-04-17 directive:

1. **Target-reader assumption:** "The readme and documentation starts with an assumption that the target user knows very little about the problems that GT-KB solves and has not used Claude Code before."
2. **Structure:** "We should answer the basic questions and then explain how each GT-KB 'feature' helps solve one or more of the problems we have identified."
3. **Block diagram required** with these entities:
   - Developer
   - Development environment
   - Azure deployment environment
   - Application user (a mobile device or Web browser somewhere on the internet)
   - **MemBase** *(term requires owner clarification — see Open Questions)*
   - MEMORY.md and the use of markdown for transient project state data
   - Deliberation Archive
   - GT-KB Skills
   - GT-KB Plugins
   - GT-KB tests and test runner
   - GT-KB directives embedded in CLAUDE.md and MEMORY.md
   - GT-KB Dashboard and how to interpret metrics
   - GT-KB Templates and patterns (e.g., `development→staging→prod`; `implementation proposal→review→implementation→verification`)
   - GT-KB integration with 3rd party tools (which ones, why, and how)
4. **Evidence section:** "Specific evidence/data that shows how much of a positive effect we have observed from GT-KB."
5. **Day-in-the-life narrative:** "Illustrates how to start adding specifications and answering questions, directing tasks like testing, deployment to staging, committing/pushing/building, requesting investigations or informational reports and how those are stored in the DA and retrieved later to help inform specification clarifications during work, and so forth."
6. **Known limitations section:** "Known limitations and areas where more user validation/feedback is required."
7. **Ordering constraint:** "This is the kind of material that the CTO needs to understand before he even gets to the installation instructions."
8. **Install baseline:** "The installation should assume that the person installing has a Windows computer connected to the internet but nothing more."

## Prior Deliberations

- `bridge/gtkb-docs-memory-architecture-alignment-editplan-008.md` (VERIFIED 2026-04-13) — three-tier memory vocabulary (CLAUDE.md / MEMORY.md / topic files) already aligned across 30 docs. The rewrite must stay consistent with that vocabulary.
- `bridge/gtkb-azure-enterprise-readiness-taxonomy-008.md` (VERIFIED 2026-04-17) — `docs/reference/azure-readiness-taxonomy.md` (666 lines) exists. The Azure-deployment-environment block in the diagram must reference, not duplicate, that taxonomy.
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` (VERIFIED 2026-04-17) — `docs/reports/non-disruptive-upgrade-audit.md` names known limitations (Gap 2.8, 11-of-12 hook re-registrations, 20 U-class rows). The limitations section must cite these live.
- v0.6.0 release line — `docs/start-here.md`, `docs/groundtruth-kb-executive-overview.md`, `docs/architecture/product-split.md` (commit `3786f49` on GT-KB main). These are the files being rewritten or superseded.
- No prior DELIB for adopter-facing rewrite was found in the 710-entry archive (search terms: "adopter", "start here", "CTO", "basic questions"). This is a net-new onboarding workstream.

## Scope (in)

**Primary deliverable:** Rewritten adopter onboarding stack in `groundtruth-kb` repo, structured for the zero-context Windows + internet reader:

1. **Repo-root `README.md`** — front door. One-page. Answers "What is this? Who is it for? What does it do?" and links into the Start Here flow.
2. **`docs/start-here.md`** — the main guided path. Prerequisites-first, installation-second. ToC below.
3. **Block diagram asset** — rendered SVG + source (Mermaid or equivalent text source for maintainability), referenced from both README and `start-here.md`.
4. **`docs/day-in-the-life.md`** — narrative companion doc. Walk-through of a realistic session covering adding a spec, directing a test run, requesting an investigation, and retrieving a DA report during later work.
5. **`docs/evidence.md`** — quantitative evidence of GT-KB effect (test-count deltas, mypy strictness, coverage gates, deliberation archive size, bridge cycle times — pulled from existing records).
6. **`docs/known-limitations.md`** — current gaps, including the audit-surfaced ones (Gap 2.8, hook re-registration, U-class scaffold rows) and explicit calls for user validation on specific areas.

**Proposed `docs/start-here.md` Table of Contents:**

```
1. What is GT-KB? (Plain-language problem statement)
2. What problem does each GT-KB feature solve?
3. Prerequisites you need to understand
   3.1 Software engineering: specifications, tests, implementation
   3.2 What is an LLM?
   3.3 What is Claude Code? What is Codex?
   3.4 How developers use Claude Code day-to-day
   3.5 Terminals (Windows PowerShell basics)
   3.6 Azure deployment (one-paragraph overview + link to taxonomy)
   3.7 Known Claude Code limitations
   3.8 How GT-KB addresses those limitations
4. How GT-KB fits together (block diagram + narrated tour)
5. Evidence: what we have measured (link to docs/evidence.md)
6. A day in the life of a GT-KB user (link to docs/day-in-the-life.md)
7. Known limitations and where we need your feedback (link to docs/known-limitations.md)
8. Installation (Windows + internet assumed)
   8.1 Install Claude Code (what it is, where to get it, how to authenticate)
   8.2 Install GT-KB (pip install, gt init, first skills)
   8.3 Verify your setup (doctor, first bridge round-trip)
9. Next steps (pointers to SKILL.md, executive overview, architecture docs)
```

## Scope (out)

- No KB mutations in the scope-drafting phase. Spec inventory is *proposed* here; actual `db.insert_spec()` calls wait for Codex GO on this scope bridge and are governed by the follow-on implementation bridge.
- No rewrite of technical reference docs (`docs/reference/*`, `docs/architecture/*` beyond `product-split.md` which may need a pointer update).
- No changes to CLAUDE.md or MEMORY.md directive content — only the rewrite may *reference* the directives, not rewrite them.
- No changes to the Azure taxonomy doc — the block diagram references it.
- No rewrite of Agent Red customer-facing docs (separate product).
- No design-system or visual redesign of the dashboard — metrics interpretation is text.

## Proposed Spec Inventory (for Codex review)

After Codex GO on this scope bridge, these specs will be recorded in the GT-KB KB (`type=requirement`, `tags=['adopter-onboarding','cto-trial']`). IDs are placeholders until owner-approved prefix is chosen:

| # | Draft ID | Requirement |
|---|----------|-------------|
| 1 | SPEC-STARTHERE-READER-PROFILE | Docs MUST assume reader has never used Claude Code, does not know what problems GT-KB solves, and owns only a Windows PC with internet. |
| 2 | SPEC-STARTHERE-FEATURE-PROBLEM-MAP | Each named GT-KB feature MUST be explicitly tied to one or more problems it solves, with the problem stated before the feature. |
| 3 | SPEC-STARTHERE-BLOCKDIAGRAM | Docs MUST include a block diagram showing relationships between the 14 entities listed in the directive. Diagram source MUST be text-based (Mermaid or equivalent) for maintainability. |
| 4 | SPEC-STARTHERE-PREREQ-ORDERING | Prerequisite explanation (problems, Claude Code, SWE concepts, Azure overview, Claude Code limitations, GT-KB's answers) MUST precede installation instructions. |
| 5 | SPEC-STARTHERE-EVIDENCE | Docs MUST include a quantitative evidence section drawn from live project records (test counts, coverage, type strictness, DA size, bridge throughput). |
| 6 | SPEC-STARTHERE-DAYINLIFE | Docs MUST include a day-in-the-life narrative covering: adding specs, directing test runs, directing staging deploy, directing commit/push/build, requesting investigations, and retrieving prior DA reports during later work. |
| 7 | SPEC-STARTHERE-LIMITATIONS | Docs MUST disclose known limitations with explicit call-outs for areas requiring user validation; MUST cite live audit-surfaced gaps. |
| 8 | SPEC-STARTHERE-INSTALL-BASELINE | Installation instructions MUST assume a Windows PC with internet only; MUST cover Claude Code install, GT-KB install, and Claude Code vs GT-KB ordering. |
| 9 | SPEC-STARTHERE-TERMINAL | Installation MUST include a terminal (PowerShell) primer sufficient for a first-time Claude Code user to execute the documented commands. |
| 10 | SPEC-STARTHERE-3RDPARTY | Docs MUST enumerate GT-KB's 3rd-party tool integrations (which tools, why integrated, how they are used). |
| 11 | SPEC-STARTHERE-DASHBOARD | Docs MUST explain the GT-KB Dashboard and how to interpret its metrics for decision-making. |
| 12 | SPEC-STARTHERE-TEMPLATES | Docs MUST document GT-KB templates/patterns, including `development→staging→prod` and `propose→review→implement→verify`. |

These will be cross-referenced from WIs (one WI per spec or grouped as sensible — Codex to advise).

## Open Questions for Owner / Codex

1. **"MemBase" clarification.** The directive lists MemBase as a first-class diagram entity, alongside MEMORY.md and the Deliberation Archive. Existing vocabulary I can map it to: (a) `groundtruth.db` (the KB), (b) the memory/ directory family (MEMORY.md + topic files), (c) ChromaDB (`.groundtruth-chroma/`), (d) something new/planned. **Blocking question — needed before spec inventory is final.**
2. **README.md scope.** Keep existing README and add a new one-page front door, or rewrite the existing README entirely?
3. **Installation delegation to external installers.** If Claude Code is a separate product, do we document the Claude Code install ourselves or link to Anthropic's official install flow (and version-pin against it)?
4. **Evidence doc sources.** I can pull from: 1209 tests on main, 70.04% coverage, 100% public-API docstrings, 710 deliberations, 55 Phase A commits, bridge cycle times. Is there additional owner-preferred evidence (e.g., time-to-first-spec for an adopter, MEMORY.md growth rate)?
5. **Dashboard screenshots.** Owner's previous preference was text-first docs. Is the dashboard section text-only, or should it include screenshots? (Visual-diff test surface for later, per Claude Design discussion.)
6. **Day-in-the-life protagonist.** Realistic synthetic scenario (e.g., "an adopter building a Flask API") or re-narration of actual S299 GT-KB session work?

## Implementation Approach (overview, not commitment)

**Phase 1 — Spec recording (post-Codex-GO):** Insert the 12 proposed specs into GT-KB KB via `db.insert_spec()`. Create 1 WI per spec. File follow-on implementation bridge (`gtkb-start-here-adopter-rewrite-implementation-001.md`) referencing the WIs.

**Phase 2 — Draft content:** Produce the 6 deliverables on a feature branch in `groundtruth-kb`. Block diagram drafted in Mermaid first; SVG rendered deterministically via a build step or manual export (Codex to advise).

**Phase 3 — CTO-persona walk-through test:** Before VERIFIED, owner (or an agreed stand-in) reads the top of `docs/start-here.md` cold and flags any remaining "basic question" gap. This is the qualitative gate.

**Phase 4 — PyPI release prep:** Docs changes may or may not trigger a v0.6.1 release. Codex to advise whether docs-only rewrites warrant a release line (bias: release for adopter visibility if the rewrite is material).

## Verification Approach

- **Spec compliance:** each of the 12 specs has a single-sentence assertion testable by Codex or the owner reading the rendered doc (e.g., "Section 2 names 14 entities, matching the directive list").
- **Link integrity:** standard `mkdocs build` or equivalent link-check pass on docs tree.
- **Evidence numbers are live:** the evidence doc cites live-verifiable metrics; a small `scripts/verify_evidence.py` or markdown-linked query trail ensures numbers are reproducible.
- **No vocabulary drift:** three-tier memory vocabulary (`gtkb-docs-memory-architecture-alignment-editplan`) preserved; Codex spot-checks.
- **CTO-persona test:** qualitative, owner-gated.

## Timeline

- **2026-04-17 (today):** Scope bridge posted NEW (this file). Codex reviews overnight.
- **2026-04-18:** On Codex GO, Phase 1 (spec recording) + Phase 2 (draft content) begins. Target: first draft end-of-day.
- **2026-04-19 (weekend):** CTO-persona walk-through + revisions. Target: VERIFIED and pushed to `groundtruth-kb` main, optionally v0.6.1 published.
- **Delivery to CTO:** end of weekend window.

## Rollback / Containment

- Docs changes are non-destructive and fully reversible via git revert.
- No production systems affected.
- No KB mutations until Codex GO.
- If timeline slips, partial delivery (README + `start-here.md` + block diagram) is still shippable; day-in-life and evidence docs can follow as fast-follows.

## Next Steps After Codex GO

1. File implementation bridge `gtkb-start-here-adopter-rewrite-implementation-001.md` referencing approved spec inventory.
2. Insert 12 specs into GT-KB KB.
3. Create WIs per spec.
4. Create feature branch on groundtruth-kb.
5. Execute Phases 2–4.

## Questions Specifically For Codex

1. Is the 6-deliverable split right, or should README and start-here.md consolidate?
2. Is Mermaid the right block-diagram source format, given GT-KB's text-first bias?
3. Should the evidence doc be auto-generated (script that queries KB/test output) or manually curated?
4. Is the day-in-the-life protagonist choice material for GO, or can it be owner-picked at implementation time?
5. Any adopter-onboarding pattern you've seen in prior GT-KB reviews that should shape the ToC?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
