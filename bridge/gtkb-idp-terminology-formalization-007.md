NEW

# GT-KB IDP Terminology Formalization — Post-Implementation Report

bridge_kind: post_implementation_report
scope: governance + documentation
work_item_ids: []
spec_ids: []
target_paths: ["CLAUDE.md", "AGENTS.md", "docs/gtkb-idp-concept.md"]
reviewed_file: bridge/gtkb-idp-terminology-formalization-006.md
reviewed_status: GO

## Summary

Implemented the IDP terminology formalization per GO -006. Three file
changes plus one DELIB insertion. All three GO conditions satisfied. All
verification commands pass.

## Changes

### 1. `CLAUDE.md` — Glossary block added

A concise "Canonical Terminology (Glossary)" section was added to
`CLAUDE.md`. Prime Builder's initial placement (near the end, before the
copyright footer) was subsequently refined by owner/linter adjustment to
**lines 12-16** — near the top of the file, directly following the
reference-data pointer block and preceding the CLAUDE.md vs MEMORY.md
boundary section. This is a stronger placement: the canonical glossary is
now visible as part of the session-loaded primary content rather than
appearing as a trailing appendix.

Final content (3 entries):

- **GT-KB (GroundTruth-KB) / Internal Developer Platform (IDP)** — canonical
  definition; expanded reference pointer to `docs/gtkb-idp-concept.md`;
  forward pointer to `.claude/rules/canonical-terminology.md` for the
  future managed-artifact adoption.
- **AI coding harness** — Claude Code, Codex CLI; role assignment by owner,
  not by vendor.
- **Adopter** — project that consumes GT-KB; Agent Red is the reference
  adopter.

### 2. `AGENTS.md` — Same glossary block added

Added to the end of the file with identical three-entry structure matching
the pattern established in `bridge/gtkb-canonical-terminology-surface-002.md:117-139`
(concise glossary in the startup/control surfaces).

### 3. `docs/gtkb-idp-concept.md` — NEW supplementary reference

Created as expanded supplementary material. Explicitly self-labels as
supplementary (not canonical authority) per GO condition 1:

> "The **canonical** local terminology surface for this repo is the concise
> glossary block in `CLAUDE.md` and `AGENTS.md`. Once Agent Red adopts the
> GT-KB managed canonical-terminology artifacts [...] those managed
> artifacts become the authoritative source and this file remains a
> human-readable companion."

Content: canonical definition, industry context (Platform Engineering,
IDP category, Backstage/Humanitec/Port reference), distinctions from
framework/toolchain/scaffold/harness, what GT-KB provides as an IDP,
first-mention convention, related deliberations and bridges, and
follow-on work (not part of this document).

### 4. Deliberation Archive — `DELIB-GTKB-IDP-TERMINOLOGY` inserted

Archived via `.claude/skills/decision-capture/helpers/record_decision.py`.

```
DELIB archived: id=DELIB-GTKB-IDP-TERMINOLOGY, version=1, outcome=owner_decision
```

## GO Conditions — Compliance

**Condition 1:** `docs/gtkb-idp-concept.md` must explicitly present itself as
a supplementary reference, not the canonical terminology authority.

**Satisfied.** The new file opens with an explicit "Supplementary reference
material. Not the canonical terminology authority." banner. The body
repeatedly defers to the `CLAUDE.md`/`AGENTS.md` glossary blocks as
canonical.

**Condition 2:** The post-implementation report must state that full
managed-artifact adoption (`.claude/rules/canonical-terminology.md` and
`.toml`) is still absent in Agent Red and remains the responsibility of
the named follow-on bridge.

**Satisfied (explicit statement):** Agent Red does **not** carry
`.claude/rules/canonical-terminology.md` or
`.claude/rules/canonical-terminology.toml` after this implementation.
This bridge did **not** attempt managed-artifact adoption. That adoption
remains the responsibility of the proposed follow-on bridge
`agent-red-canonical-terminology-surface-adoption`, which will:

- Install the GT-KB v0.6.1 managed canonical-terminology artifacts in
  `.claude/rules/`.
- Move the canonical IDP term definition into the managed artifact.
- Regenerate or retire `docs/gtkb-idp-concept.md` accordingly.
- Update the `CLAUDE.md` / `AGENTS.md` glossary blocks to point at the
  managed artifact.

This bridge only extends the canonical-terminology control-surface
convention with one new term today; it does not claim full upstream
adoption.

**Condition 3:** Re-measure `CLAUDE.md` at implementation time and keep
the final file at or below 300 lines. Use the actual count in the
post-implementation report.

**Satisfied.** Actual post-implementation line count: **289 lines**
(CLAUDE.md). This is below the GOV-01 budget of 300. The -005 proposal
estimate of 267 was stale (Codex's live probe at -006 showed 273, and
the post-edit count is 289 after the glossary block addition plus the
owner/linter refinement into a tighter 3-bullet block).

## Verification Commands — Live Output

### Surface content checks

```
$ python -c "from pathlib import Path; ..."
CLAUDE.md OK
AGENTS.md OK
docs/gtkb-idp-concept.md OK
CLAUDE.md lines: 289/300 (OK)
AGENTS.md lines: 227
```

### DELIB round-trip

```
$ python -c "from groundtruth_kb.db import KnowledgeDB; ..."
DELIB-GTKB-IDP-TERMINOLOGY OK; version=1
```

All fields confirmed on retrieval: `outcome == 'owner_decision'`,
`source_type == 'owner_conversation'`, content contains "Internal Developer
Platform".

## Files Changed (Commit-Local Delta)

Pending commit:

```
 CLAUDE.md                    |  +5 lines (glossary block at lines 12-16)
 AGENTS.md                    |  +8 lines (glossary block appended)
 docs/gtkb-idp-concept.md     | +95 lines (new file)
```

Plus one DELIB row inserted into `groundtruth.db` via the helper.

## Non-Scope Confirmation

- `CLAUDE-REFERENCE.md` unchanged (dropped from target_paths in Rev 2 per
  -004 F1).
- `memory/MEMORY.md` unchanged (dropped in Rev 1 per -002 F1).
- `.claude/rules/canonical-terminology.md` and `.toml` **NOT** created
  (scoped out; follow-on bridge).
- No code changes, no test changes, no CI changes, no renames.
- No GT-KB repo changes.
- Follow-on bridges recommended in Rev 2 not filed yet.

## Recommended Next Steps (for owner prioritization, not automatic)

1. **`agent-red-canonical-terminology-surface-adoption`** — adopt the
   GT-KB v0.6.1 managed canonical-terminology artifacts in Agent Red.
2. **`gtkb-readme-idp-formalization`** (GT-KB repo) — update
   `groundtruth-kb/README.md` opening paragraph.
3. **`gtkb-canonical-terminology-idp-entry`** (GT-KB repo) — add IDP
   entry to shipped canonical-terminology surface.
4. **`agent-red-changelog-idp-framing`** (Agent Red) — next release
   notes entry leads with IDP framing.

## Requested Verdict

VERIFIED.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-GTKB-IDP-TERMINOLOGY` (S305) — owner decision formalized by this
  bridge.
- `DELIB-0716`, `DELIB-0722` — prior canonical-terminology governance
  deliberations (the contract this bridge extends).
- `DELIB-0877` — GTKB-ISOLATION parent decision.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
