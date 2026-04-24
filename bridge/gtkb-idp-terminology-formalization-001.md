NEW

# GT-KB as Internal Developer Platform (IDP) — Terminology Formalization

**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Session:** S305

bridge_kind: proposal
scope: governance + documentation
work_item_ids: []
target_paths: ["CLAUDE-REFERENCE.md", "memory/MEMORY.md", "docs/gtkb-idp-concept.md"]

## Requested Verdict

GO to formalize **Internal Developer Platform (IDP)** as the canonical
terminology for GT-KB across Agent Red's documentation, reports, and
materials, per explicit owner decision in S305.

Or NO-GO with required revisions.

## Owner Decision (for Deliberation Archive)

**Decision:** GT-KB (GroundTruth-KB) is to be categorized as an **Internal
Developer Platform (IDP)** in all user-facing documentation, reports, release
notes, adopter materials, and future governance artifacts.

**Rationale** (owner, S305):
- Well-worn industry vocabulary accelerates comprehension for audiences
  familiar with contemporary enterprise SaaS technology (Platform
  Engineering discipline; IDPs like Backstage, Humanitec, Port).
- Avoids re-inventing terminology where an established term fits.
- Positions GT-KB in a recognizable category rather than requiring each
  adopter to learn a bespoke vocabulary.

**Prior Codex consultation (recorded in this session's main transcript):**
- "Platform" is the closest established term among framework / harness /
  platform / development environment / pipeline / engineering wheel.
- IDP is the canonical sub-category for platforms that provide shared
  project infrastructure, governance, runtime services, and conventions
  that developers consume.
- The specific sub-pattern of wrapping multiple AI coding harnesses under
  shared governance is not yet industry-standardized; IDP is the accepted
  parent category.

**Deliberation entry to be archived** (text draft, for owner
acknowledgement and subsequent KB insertion via `db.insert_deliberation`):

```
id: DELIB-GTKB-IDP-TERMINOLOGY
source_type: owner_conversation
outcome: owner_decision
content: GT-KB (GroundTruth-KB) is formally categorized as an Internal
Developer Platform (IDP). All user-facing documentation, reports, adopter
materials, and governance artifacts should use this terminology. Rationale:
established Platform Engineering / IDP vocabulary accelerates comprehension
for audiences familiar with contemporary enterprise SaaS technology and
positions GT-KB in a recognizable category. Sub-pattern (wrapping multiple
AI coding harnesses) is not industry-standardized yet; IDP is the accepted
parent category.
```

## Canonical Definition (proposed for doc reuse)

A minimal definition, ~70 words, suitable for README intros, adopter
onboarding, and governance artifact references:

> **GT-KB (GroundTruth-KB) is an Internal Developer Platform (IDP)** for
> individual developers building and maintaining production software with
> AI assistance. Like any IDP, it provides shared project infrastructure,
> governance artifacts, runtime services, and conventions that applications
> consume. Unlike traditional org-scale IDPs, it is sized for a
> single-developer context and integrates multiple AI coding harnesses
> (Claude Code, Codex) under shared specifications, bridges, and
> protocols.

## Scope

### In scope for this Agent Red-side bridge

1. **`CLAUDE-REFERENCE.md`** — add an "IDP Concept" section containing the
   canonical definition above, a one-paragraph rationale, and a short
   glossary of related terms (Platform Engineering, Internal Developer
   Platform, harness, adopter, work subject). One new section; no
   restructuring of existing content.

2. **`memory/MEMORY.md`** — the GT-KB status line currently reads
   "groundtruth-kb: v0.6.1 on PyPI ...". Revise the opening phrase to
   "GT-KB (Internal Developer Platform): v0.6.1 on PyPI ..." so the term
   enters the session-loaded memory surface.

3. **`docs/gtkb-idp-concept.md`** (NEW) — a one-page standalone reference
   that adopters or reviewers can cite. Contents: canonical definition,
   three bullet points distinguishing GT-KB from framework / toolchain /
   scaffold, and links to Platform Engineering background (without
   externally generated URLs — use descriptive references to well-known
   patterns and allow the reader to search).

4. **Governance convention going forward** — documented in
   `CLAUDE-REFERENCE.md`: when bridge proposals, reports, or other
   governance artifacts reference GT-KB's role, they should use "GT-KB
   (GroundTruth-KB), an Internal Developer Platform" on first mention in
   a document, and "GT-KB" thereafter. This applies to Agent Red-side
   artifacts; the GT-KB repo-side convention is handled separately below.

### Explicitly out of scope for this bridge

1. **GT-KB repo changes** — README.md, CHANGELOG.md, docs/ site, adopter
   onboarding materials in the `groundtruth-kb` checkout require their own
   upstream bridge filed in that working directory. A follow-on bridge
   recommendation is included below.

2. **Canonical-terminology surface updates in the GT-KB v0.6.1 package** —
   the shipped `canonical-terminology` surface may need an IDP entry; that
   is a separate upstream bridge.

3. **Adopter marketing / website materials** — out of scope; separate
   workstream.

4. **Renaming of existing files, commands, or artifact types** — no
   renames. "IDP" is added as descriptive terminology; existing artifact
   names (GOV, SPEC, PB, ADR, DCL, etc.) are unchanged.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0877` — GTKB-ISOLATION parent decision (relevant because
  GTKB-ISOLATION's target state produces a cleanly IDP-shaped model).
- No prior DELIB on GT-KB terminology itself; this is the first canonical
  naming decision at this level.

## Implementation Sequence

1. Archive the DELIB entry above via the KB Python API.
2. Add the "IDP Concept" section to `CLAUDE-REFERENCE.md`.
3. Update the `MEMORY.md` GT-KB status line to include the IDP label.
4. Create `docs/gtkb-idp-concept.md`.
5. Add the first-mention convention to `CLAUDE-REFERENCE.md` governance
   conventions section.
6. Post-implementation report citing exact line changes.

## Verification

- Read-only text checks:
  - `grep -l "Internal Developer Platform" CLAUDE-REFERENCE.md memory/MEMORY.md docs/gtkb-idp-concept.md` returns 3 matches.
  - DELIB-GTKB-IDP-TERMINOLOGY retrievable via
    `python tools/knowledge-db/db.py get_deliberation --id DELIB-GTKB-IDP-TERMINOLOGY`.
- No existing tests are affected. No code changes. No behavioral changes.

## Recommended Follow-On Bridges (not included in this scope)

1. **`gtkb-readme-idp-formalization`** (filed in GT-KB repo) — update
   `groundtruth-kb/README.md` opening paragraph to lead with the IDP
   framing. Canonical definition text can be reused verbatim from the
   Agent Red-side `docs/gtkb-idp-concept.md`.

2. **`gtkb-canonical-terminology-idp-entry`** (filed in GT-KB repo) — add
   IDP to the v0.6.1-shipped canonical-terminology surface.

3. **`agent-red-changelog-idp-framing`** (Agent Red repo) — on the next
   Agent Red changelog / release notes entry, ensure GT-KB is referenced
   as an IDP.

## Review Focus

A GO on this proposal authorizes only the three Agent Red-side file
changes above and the DELIB archive insertion. It does not authorize GT-KB
repo changes, adopter marketing updates, or file renames.

A NO-GO should identify:
- Objection to "Internal Developer Platform" as the canonical term
  (unlikely given explicit owner decision but surfaceable here).
- Additional Agent Red-side surfaces that should be in scope beyond the
  three named files.
- Preference for a different definition phrasing.
- Objection to the first-mention convention as governance policy.

## Non-Scope Reminder

This bridge does not rename artifacts, change any code, modify tests,
update CI pipelines, affect the bridge protocol itself, or close any
in-flight GTKB-ISOLATION bridges.

## Decision Needed From Owner

None — the owner has already made the terminology decision in the session
transcript. This bridge formalizes that decision into the governance
system.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
