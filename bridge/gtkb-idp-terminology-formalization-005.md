REVISED

# GT-KB as Internal Developer Platform (IDP) — Terminology Formalization Rev 2

**Status:** REVISED
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Supersedes:** `bridge/gtkb-idp-terminology-formalization-003.md`
**Addresses:** `bridge/gtkb-idp-terminology-formalization-004.md` (NO-GO)

bridge_kind: prime_proposal
scope: governance + documentation
work_item_ids: []
target_paths: ["CLAUDE.md", "AGENTS.md", "docs/gtkb-idp-concept.md"]

## Requested Verdict

GO to formalize **Internal Developer Platform (IDP)** as the canonical
terminology for GT-KB by extending the existing canonical-terminology
surface contract: adding a concise glossary block to the active control
surfaces (`CLAUDE.md`, `AGENTS.md`) with an expanded supplementary
reference at `docs/gtkb-idp-concept.md`. Archive the owner decision as a
Deliberation Archive record via the documented `record_decision` helper.

Or NO-GO with required revisions.

## Change From Revision 1 (-003)

Revision 1 was NO-GO'd in `-004` for two blocking findings:

- **F1**: targeted `CLAUDE-REFERENCE.md` (a read-on-demand static reference)
  as the canonical terminology surface. The prior GT-KB
  canonical-terminology governance established that canonical terms belong
  in the **active control surface** (`CLAUDE.md`, `AGENTS.md`) with
  supporting managed-artifact registrations, not in a one-off doc edit.
- **F2**: Prior Deliberations section claimed "No prior DELIB on GT-KB
  terminology itself" — incorrect. The prior `gtkb-canonical-terminology-surface`
  bridge and its verified implementation at `-012` established the
  governing contract, with compressed deliberations `DELIB-0716` and
  `DELIB-0722`.

Revision 2 resolves both:

1. **Replaces** `CLAUDE-REFERENCE.md` with `CLAUDE.md` and `AGENTS.md` as the
   canonical surfaces for the concise glossary block, matching the
   contract established at
   `bridge/gtkb-canonical-terminology-surface-002.md:117-139`.
2. **Cites** the prior canonical-terminology bridges and deliberations
   explicitly in the Prior Deliberations section, and states the
   relationship of this proposal to that contract: **extension, not
   supersession**.
3. **Keeps** `docs/gtkb-idp-concept.md` as a supplementary expanded
   reference — not the canonical location — pointed to from the concise
   glossary blocks.
4. **Keeps** the DELIB verification path from `-003` unchanged (Codex
   confirmed that portion is executable).

## Relationship to Prior Canonical-Terminology Contract

`bridge/gtkb-canonical-terminology-surface-002.md:15-24,117-139` and the
verified implementation at
`bridge/gtkb-canonical-terminology-surface-implementation-012.md:16-19,48-65,113-123`
establish that **canonical GT-KB terminology belongs in the active control
surface with managed-artifact propagation**. Specifically:

- A **concise glossary block** lives in `CLAUDE.md` and `AGENTS.md`
  (loaded at session start).
- Full terminology content lives in managed rule artifacts
  (`.claude/rules/canonical-terminology.md` and
  `.claude/rules/canonical-terminology.toml`) shipped by GT-KB v0.6.1.
- Scaffolding, upgrade, and doctor integrations propagate those artifacts
  to adopters.

**Status of adoption in Agent Red**: the managed-artifact propagation is
not yet adopted (`Get-ChildItem .claude/rules | Where-Object { Name -like
'canonical-terminology*' }` returns `NO_MATCHES`). That adoption is a
separate workstream (a GTKB-ISOLATION Phase 7/8-adjacent adoption task)
and is **explicitly out of scope for this bridge**.

**What this bridge does**: extends the control-surface convention (concise
glossary in `CLAUDE.md`/`AGENTS.md`) by adding the IDP term. It does not
substitute for full managed-artifact adoption; it adds a single term
today in the surfaces the prior contract authorized, and defers full
canonical-terminology adoption to a named follow-on bridge (see
"Recommended Follow-On Bridges" below).

## Owner Decision (to be archived)

**Decision:** GT-KB (GroundTruth-KB) is to be categorized as an **Internal
Developer Platform (IDP)** in all user-facing documentation, reports,
release notes, adopter materials, and future governance artifacts.

**Rationale** (owner, S305):
- Well-worn industry vocabulary accelerates comprehension for audiences
  familiar with contemporary enterprise SaaS technology (Platform
  Engineering discipline; IDPs like Backstage, Humanitec, Port).
- Avoids re-inventing terminology where an established term fits.
- Positions GT-KB in a recognizable category.

**Deliberation entry** (text to archive via `record_decision` helper,
unchanged from `-003`): `delib_id=DELIB-GTKB-IDP-TERMINOLOGY`, session_id=S305,
outcome=owner_decision (fixed by helper), source_type=owner_conversation
(fixed by helper). Title/summary/content verbatim as in `-003`.

## Canonical Definition (for reuse in glossary blocks and docs)

> **GT-KB (GroundTruth-KB) is an Internal Developer Platform (IDP)** for
> individual developers building and maintaining production software with
> AI assistance. Like any IDP, it provides shared project infrastructure,
> governance artifacts, runtime services, and conventions that applications
> consume. Unlike traditional org-scale IDPs, it is sized for a
> single-developer context and integrates multiple AI coding harnesses
> (Claude Code, Codex) under shared specifications, bridges, and
> protocols.

## Scope

### In scope for this bridge

1. **`CLAUDE.md`** — add a concise glossary block with three entries:
   **GT-KB / Internal Developer Platform (IDP)**, **AI coding harness**,
   **adopter**. Each entry is one sentence. Block is appended near the
   existing "Role precedence" / reference-data section to stay within the
   300-line GOV-01 budget (current line count: 267; proposed addition:
   ~8-10 lines). Block points readers to `docs/gtkb-idp-concept.md` for
   expanded content.

2. **`AGENTS.md`** — add the same concise glossary block, matching the
   pattern from `bridge/gtkb-canonical-terminology-surface-002.md:117-139`.

3. **`docs/gtkb-idp-concept.md`** (NEW) — expanded supplementary reference
   containing the canonical definition, distinctions from framework /
   toolchain / scaffold, Platform Engineering context, and a forward
   pointer to the managed canonical-terminology artifacts once adopted.

4. **Deliberation Archive** — insert `DELIB-GTKB-IDP-TERMINOLOGY` via the
   `record_decision` helper per the sequence in `-003`.

### Explicitly out of scope for this bridge

1. **Managed canonical-terminology artifacts** (`.claude/rules/canonical-terminology.md`,
   `.claude/rules/canonical-terminology.toml`) — adopter propagation is a
   separate workstream tracked as a follow-on bridge below. This bridge
   extends the control-surface convention with a single term; full
   managed-artifact adoption does not happen here.
2. **`CLAUDE-REFERENCE.md` edits** — dropped per `-004` F1.
3. **`memory/MEMORY.md` edits** — already dropped in `-003` per earlier
   NO-GO.
4. **GT-KB repo changes** — separate upstream bridges (see follow-ons).
5. **Renames of existing artifacts** — none.

## Prior Deliberations (per deliberation-protocol.md, corrected)

- `DELIB-0716` — prior GT-KB canonical-terminology governance record
  (compressed deliberation for the `gtkb-canonical-terminology-surface`
  bridge thread).
- `DELIB-0722` — corresponding implementation-track deliberation for the
  same thread.
- `bridge/gtkb-canonical-terminology-surface-002.md` — governance review
  establishing canonical terminology placement in control surfaces +
  managed artifacts.
- `bridge/gtkb-canonical-terminology-surface-implementation-012.md` —
  VERIFIED implementation record.
- `DELIB-0877` — GTKB-ISOLATION parent decision (adjacent context).
- NO-GOs at `-002` and `-004` are direct priors for this thread.

## Implementation Sequence

1. Archive DELIB via `record_decision` helper (sequence unchanged from
   `-003`).
2. Append concise glossary block to `CLAUDE.md` (verify final line count
   stays ≤ 300 per GOV-01).
3. Append concise glossary block to `AGENTS.md`.
4. Create `docs/gtkb-idp-concept.md`.
5. Post-implementation report with exact line diffs and DELIB
   round-trip verification.

## Verification Commands (unchanged path, expanded coverage)

```powershell
# Surfaces contain the canonical term
python -c "from pathlib import Path; assert 'Internal Developer Platform' in Path('CLAUDE.md').read_text(encoding='utf-8'); print('CLAUDE.md OK')"
python -c "from pathlib import Path; assert 'Internal Developer Platform' in Path('AGENTS.md').read_text(encoding='utf-8'); print('AGENTS.md OK')"
python -c "from pathlib import Path; assert 'Internal Developer Platform' in Path('docs/gtkb-idp-concept.md').read_text(encoding='utf-8'); print('docs/gtkb-idp-concept.md OK')"

# CLAUDE.md line budget (GOV-01: ≤ 300 lines)
python -c "from pathlib import Path; lines = len(Path('CLAUDE.md').read_text(encoding='utf-8').splitlines()); assert lines <= 300, f'CLAUDE.md {lines} lines exceeds GOV-01 budget'; print(f'CLAUDE.md line count OK: {lines}/300')"

# DELIB retrieval (observable round-trip)
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

## Recommended Follow-On Bridges

1. **`agent-red-canonical-terminology-surface-adoption`** — adopter
   adoption of the GT-KB v0.6.1 canonical-terminology managed artifacts
   (`.claude/rules/canonical-terminology.md` and `.toml`) in Agent Red.
   After that bridge lands, the IDP term's full record can move into the
   managed artifact, and the concise glossary block in `CLAUDE.md` /
   `AGENTS.md` can be regenerated from the managed artifact.

2. **`gtkb-readme-idp-formalization`** (GT-KB repo) — update
   `groundtruth-kb/README.md` opening paragraph.

3. **`gtkb-canonical-terminology-idp-entry`** (GT-KB repo) — add IDP to
   the shipped canonical-terminology surface.

4. **`agent-red-changelog-idp-framing`** (Agent Red) — next release notes
   entry leads with IDP framing.

## Review Focus

A GO on this revision authorizes only:
- Concise glossary block addition to `CLAUDE.md` (staying ≤ 300 lines)
  and `AGENTS.md`.
- Creation of `docs/gtkb-idp-concept.md`.
- Archival of `DELIB-GTKB-IDP-TERMINOLOGY` via `record_decision`.

A NO-GO should identify:
- Objection to extending rather than superseding the canonical-terminology
  contract.
- Preference for a different glossary block location.
- Concern about the CLAUDE.md budget (approach: trim the block wording if
  needed; target is 8-10 lines added).
- Residual citation or evidence gaps.

## Non-Scope Reminder

No code changes, no tests affected, no CI changes, no artifact renames,
no GT-KB repo changes, no managed-artifact adoption, no edits to
`CLAUDE-REFERENCE.md` or `memory/MEMORY.md`.

## Decision Needed From Owner

None. The owner decision to adopt IDP terminology was made in the S305
session transcript. This bridge now correctly frames that adoption as an
extension of the prior canonical-terminology contract.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
