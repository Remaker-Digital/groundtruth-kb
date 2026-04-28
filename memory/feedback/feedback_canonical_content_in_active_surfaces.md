---
name: Canonical governance content lives in active control surfaces
description: Default placement for canonical terms, conventions, and governing vocabulary is session-loaded control surfaces (CLAUDE.md, AGENTS.md, .claude/rules/), not read-on-demand reference files
type: feedback
originSessionId: c002f66c-aced-4409-9602-c16758fcfa14
---
**Rule:** When placing a canonical term, governance convention, naming rule, or any content meant to **govern** future work, default to session-loaded active control surfaces (`CLAUDE.md`, `AGENTS.md`, `.claude/rules/`). Do not default to read-on-demand reference files (`CLAUDE-REFERENCE.md`, `docs/`).

**Why:** S305 incident. I proposed putting the IDP canonical definition in `CLAUDE-REFERENCE.md`. Codex NO-GO'd because:
- `CLAUDE-REFERENCE.md:1-5` explicitly labels itself "Static Reference Material" and "not loaded automatically."
- `CLAUDE.md:7-10` classifies `CLAUDE-REFERENCE.md` as read-on-demand reference data, distinct from active control surface.
- Prior canonical-terminology contract (`DELIB-0716`, `DELIB-0722`, bridge `gtkb-canonical-terminology-surface-*`) established that canonical terms belong in the active surface with managed-artifact propagation.
- Placing governing vocabulary in an on-demand reference file means adopters/reviewers searching for governance don't find it where they look. Governing content must live where it governs.

**How to apply:**
- **Decision rule:** ask "is this active guidance or reference material?" If it governs future sessions, bridge reviews, adopter onboarding, or any cross-session behavior, it's active. If it's one-shot lookup data (legal boilerplate, version tables, schema detail readable on demand), it's reference.
- **Active → `CLAUDE.md`, `AGENTS.md`, `.claude/rules/<name>.md`**. These are session-loaded; additions to them shape every session immediately.
- **Reference → `CLAUDE-REFERENCE.md`, `docs/`**. These are for lookup material and supplementary detail. Valid location for expanded content linked *from* an active surface, but not valid as the canonical definition location.
- **Budget awareness:** `CLAUDE.md` has a 300-line GOV-01 budget. A concise glossary block (8-15 lines) is fine. Full prose definitions belong in a linked `docs/<topic>.md` with a pointer from the CLAUDE.md glossary entry.
- **Pattern**: concise entry in active surface → link to expanded reference doc. Not the reverse.
- **When reviewing placement proposals from future sessions:** if a proposal puts canonical content in `CLAUDE-REFERENCE.md` or `docs/` without a pointer from `CLAUDE.md` or `AGENTS.md`, flag it.
