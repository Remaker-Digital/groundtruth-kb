REVISED

# GT-KB as Internal Developer Platform (IDP) — Terminology Formalization Rev 1

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/gtkb-idp-terminology-formalization-001.md`
**Addresses:** `bridge/gtkb-idp-terminology-formalization-002.md` (NO-GO)

bridge_kind: proposal
scope: governance + documentation
work_item_ids: []
target_paths: ["CLAUDE-REFERENCE.md", "docs/gtkb-idp-concept.md"]

## Requested Verdict

GO to formalize **Internal Developer Platform (IDP)** as the canonical
terminology for GT-KB across Agent Red's documentation, reports, and
materials, per explicit owner decision in S305.

Or NO-GO with required revisions.

## Change From Revision 0 (-001)

Revision 0 was NO-GO'd in `-002` for two blocking findings:

- **F1**: target path `memory/MEMORY.md` does not exist in this Agent Red
  checkout. The file I conflated it with (`MEMORY.md` under
  `~/.claude/projects/...`) is user-profile auto-memory, not project-tracked.
- **F2**: the verification command
  `python tools/knowledge-db/db.py get_deliberation --id ...` is not
  executable; `db.py` is a re-export shim with no CLI entry point, and the
  documented DELIB write path is the `record_decision` helper at
  `.claude/skills/decision-capture/helpers/record_decision.py`.

Revision 1 resolves both:

1. **Drops** `memory/MEMORY.md` from `target_paths`. The Agent Red session
   auto-memory is not a canonical project artifact and is out of scope for
   this governance-surface change. Project-tracked memory files in
   `memory/` (e.g., `work_list.md`, `release-readiness.md`) also do not
   require IDP-label edits; the canonical definition lives in the two
   documentation surfaces below.
2. **Replaces** the verification section with commands that invoke the
   real `record_decision` helper and use `KnowledgeDB.get_deliberation`
   directly from Python rather than a nonexistent CLI.

## Owner Decision (to be archived)

**Decision:** GT-KB (GroundTruth-KB) is to be categorized as an **Internal
Developer Platform (IDP)** in all user-facing documentation, reports,
release notes, adopter materials, and future governance artifacts.

**Rationale** (owner, S305):
- Well-worn industry vocabulary accelerates comprehension for audiences
  familiar with contemporary enterprise SaaS technology (Platform
  Engineering discipline; IDPs like Backstage, Humanitec, Port).
- Avoids re-inventing terminology where an established term fits.
- Positions GT-KB in a recognizable category rather than requiring each
  adopter to learn a bespoke vocabulary.

**Deliberation entry** (draft text, to be archived via `record_decision`):

```
delib_id: DELIB-GTKB-IDP-TERMINOLOGY
title: GT-KB formally categorized as an Internal Developer Platform (IDP)
summary: Owner decision to adopt Internal Developer Platform (IDP)
  terminology for GT-KB across documentation, reports, and adopter
  materials.
content: |
  GT-KB (GroundTruth-KB) is formally categorized as an Internal Developer
  Platform (IDP). All user-facing documentation, reports, adopter
  materials, and governance artifacts should use this terminology.
  Rationale: established Platform Engineering / IDP vocabulary accelerates
  comprehension for audiences familiar with contemporary enterprise SaaS
  technology and positions GT-KB in a recognizable category. Sub-pattern
  (wrapping multiple AI coding harnesses) is not industry-standardized
  yet; IDP is the accepted parent category.
session_id: S305
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
> (Claude Code, Codex) under shared specifications, bridges, and protocols.

## Scope

### In scope for this Agent Red-side bridge

1. **`CLAUDE-REFERENCE.md`** — add an "IDP Concept" section containing the
   canonical definition above, a one-paragraph rationale, and a short
   glossary of related terms (Platform Engineering, Internal Developer
   Platform, harness, adopter, work subject). One new section; no
   restructuring of existing content.

2. **`docs/gtkb-idp-concept.md`** (NEW) — a one-page standalone reference
   that adopters or reviewers can cite. Contents: canonical definition,
   three bullet points distinguishing GT-KB from framework / toolchain /
   scaffold, and brief links to Platform Engineering background (using
   descriptive references, not externally generated URLs).

3. **Governance convention going forward** — documented in
   `CLAUDE-REFERENCE.md`: when bridge proposals, reports, or other
   governance artifacts reference GT-KB's role, they should use "GT-KB
   (GroundTruth-KB), an Internal Developer Platform" on first mention in
   a document, and "GT-KB" thereafter. This applies to Agent Red-side
   artifacts; the GT-KB repo-side convention is handled by a separate
   upstream bridge (see "Recommended Follow-On Bridges" below).

### Explicitly out of scope for this bridge

1. **`memory/MEMORY.md`** — removed from scope per `-002` F1. Agent Red
   session auto-memory lives under the user profile (`~/.claude/projects/...`)
   and is not a canonical project artifact.
2. **Other `memory/*.md` files** — no edits proposed. If a future
   project-memory surface wants the IDP label, that is a separate bridge.
3. **GT-KB repo changes** — README.md, CHANGELOG.md, docs site, adopter
   onboarding require their own upstream bridge filed in the
   `groundtruth-kb` checkout.
4. **Canonical-terminology surface in GT-KB v0.6.1 package** — separate
   upstream bridge.
5. **File renames, code changes, artifact-type renames** — none. "IDP" is
   added as descriptive terminology; existing artifact names are unchanged.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0877` — GTKB-ISOLATION parent decision (relevant context).
- No prior DELIB on GT-KB terminology itself.
- `-002` NO-GO is the direct prior for this thread.

## Implementation Sequence

1. Archive the DELIB entry via:
   ```python
   from groundtruth_kb.db import KnowledgeDB
   from pathlib import Path
   # Import the decision-capture helper
   import sys; sys.path.insert(0, str(Path(".claude/skills/decision-capture/helpers").resolve()))
   from record_decision import record_decision
   db = KnowledgeDB(Path("groundtruth.db"))
   try:
       record_decision(
           db,
           delib_id="DELIB-GTKB-IDP-TERMINOLOGY",
           title="GT-KB formally categorized as an Internal Developer Platform (IDP)",
           summary="Owner decision to adopt IDP terminology for GT-KB across documentation, reports, and adopter materials.",
           content=(
               "GT-KB (GroundTruth-KB) is formally categorized as an Internal "
               "Developer Platform (IDP). All user-facing documentation, reports, "
               "adopter materials, and governance artifacts should use this "
               "terminology. Rationale: established Platform Engineering / IDP "
               "vocabulary accelerates comprehension for audiences familiar with "
               "contemporary enterprise SaaS technology and positions GT-KB in a "
               "recognizable category. Sub-pattern (wrapping multiple AI coding "
               "harnesses) is not industry-standardized yet; IDP is the accepted "
               "parent category."
           ),
           session_id="S305",
       )
   finally:
       db.close()
   ```
2. Add the "IDP Concept" section to `CLAUDE-REFERENCE.md`.
3. Create `docs/gtkb-idp-concept.md`.
4. Add the first-mention convention to `CLAUDE-REFERENCE.md` governance
   conventions section.
5. Post-implementation report citing exact line changes and DELIB verification.

## Verification Commands (replacing `-001` broken commands)

### Doc presence

```powershell
python -c "from pathlib import Path; assert 'Internal Developer Platform' in Path('CLAUDE-REFERENCE.md').read_text(encoding='utf-8'); print('CLAUDE-REFERENCE.md OK')"
python -c "from pathlib import Path; assert 'Internal Developer Platform' in Path('docs/gtkb-idp-concept.md').read_text(encoding='utf-8'); print('docs/gtkb-idp-concept.md OK')"
```

### DELIB retrieval (observable round-trip)

```powershell
python -c "
from groundtruth_kb.db import KnowledgeDB
from pathlib import Path
db = KnowledgeDB(Path('groundtruth.db'))
try:
    row = db.get_deliberation('DELIB-GTKB-IDP-TERMINOLOGY')
    assert row is not None, 'DELIB not found'
    assert row['outcome'] == 'owner_decision'
    assert row['source_type'] == 'owner_conversation'
    assert 'Internal Developer Platform' in row['content']
    print('DELIB-GTKB-IDP-TERMINOLOGY OK; version=' + str(row.get('version')))
finally:
    db.close()
"
```

Both commands produce observable output and non-zero exit on failure.

## Recommended Follow-On Bridges (not included in this scope)

1. **`gtkb-readme-idp-formalization`** (filed in GT-KB repo) — update
   `groundtruth-kb/README.md` opening paragraph to lead with the IDP
   framing. Canonical definition text can be reused verbatim from
   `docs/gtkb-idp-concept.md`.
2. **`gtkb-canonical-terminology-idp-entry`** (filed in GT-KB repo) — add
   IDP to the v0.6.1-shipped canonical-terminology surface.
3. **`agent-red-changelog-idp-framing`** (Agent Red repo) — ensure the
   next Agent Red release notes entry references GT-KB as an IDP.

## Review Focus

A GO on this revision authorizes only:
- Addition of the "IDP Concept" section to `CLAUDE-REFERENCE.md`.
- Creation of `docs/gtkb-idp-concept.md`.
- Addition of the first-mention governance convention to
  `CLAUDE-REFERENCE.md`.
- Archival of DELIB-GTKB-IDP-TERMINOLOGY via the `record_decision`
  helper.

A NO-GO should identify:
- Objection to "Internal Developer Platform" as the canonical term.
- Additional Agent Red-side surfaces that should be in scope beyond the
  two named files.
- Preference for a different definition phrasing.
- Issues with the revised verification commands.

## Non-Scope Reminder

Unchanged from `-001` except for the removal of `memory/MEMORY.md`.

## Decision Needed From Owner

None. The owner made the terminology decision in the S305 session
transcript. This bridge formalizes the decision and archives the
deliberation.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
