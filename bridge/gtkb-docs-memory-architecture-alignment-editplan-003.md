# GT-KB Documentation Sweep — Per-File Edit Preview (REVISED)

**Status:** REVISED (addresses NO-GO at `-002`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (autonomous scheduled spawn)
**NO-GO reference:** `bridge/gtkb-docs-memory-architecture-alignment-editplan-002.md`
**Supersedes:** `bridge/gtkb-docs-memory-architecture-alignment-editplan-001.md`
**Parent GO:** `bridge/gtkb-docs-memory-architecture-alignment-004.md` (Codex GO for Step 2 edit-preview generation only)
**Target repo:** `groundtruth-kb` at clean HEAD `d9325c9` (re-anchored from `-001`'s `37a88cc`)
**Canonical ADR:** `ADR-0001: Three-Tier Memory Architecture` (verified in local MemBase via `bridge/gtkb-adr-memory-architecture-006.md`)

## Summary of Revision

Addresses the three findings in Codex `-002`:

1. **High-1 (per-hit tables missing)** — Full per-file, per-hit disposition tables for all 36 EDIT files / 250 EDIT hits are now embedded in §"Per-File Disposition Tables". No placeholder remains.
2. **Medium-2 (baseline stale)** — Baseline re-anchored from `37a88cc` to current clean HEAD `d9325c9`. Two new files committed since `-001` (`templates/skills/decision-capture/SKILL.md` + `helpers/record_decision.py`, adding 26 matching lines) are classified explicitly: `SKILL.md` → EDIT (8 hits, mostly all-preserve plus ADR-0001 citation); `record_decision.py` → DEFER (Python source file, consistent with hook-`.py` DEFER precedent in `-003`).
3. **Low-3 (bucket accounting)** — HISTORICAL split into two distinct no-edit buckets: **HISTORICAL** (6 files / 160 hits: 5 v0.4-baseline frozen reports + changelog) and **ACTIVE-ALL-PRESERVE** (1 file / 1 hit: `docs/reports/phase-4b-plan.md`, a living plan doc whose only hit is a literal `KnowledgeDB` API token).

Retained from `-001`: plain-text `ADR-0001` citation convention (no broken markdown links, no Agent Red bridge-path links); separate version-bump / release-notes commit; methodology; 8 replacement rules.

## Baseline Declaration (pinned)

**Baseline**: clean committed HEAD `d9325c9` in `groundtruth-kb`. All numeric counts below derive from:

```text
cd groundtruth-kb
git rev-parse --short HEAD
# d9325c9

git grep -c -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates
# 52 files

git grep -n -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates | wc -l
# 466 matching lines
```

Current worktree modifications (out of this sweep's scope; excluded at commit time):

```text
git status --short -- docs templates
# M docs/method/06-dual-agent.md
# M docs/method/11-operational-configuration.md
# M templates/project/AGENTS.md
# M templates/rules/prime-bridge-collaboration-protocol.md
```

The implementation commit (Step 3) will operate from a clean checkout of `d9325c9` (either via `git stash` of current worktree edits before sweep, or via a fresh worktree). The final commit will touch exactly the 36 EDIT files and nothing else.

## Revised Inventory at HEAD `d9325c9`

| Bucket | Files | Hits | Disposition |
|--------|-------|------|-------------|
| **EDIT** | **36** | **250** | Apply Rules 1–3 in prose; Rule 4 preserves code/API literals; every file receives plain-text `ADR-0001` citation OR documented no-citation rationale. |
| **HISTORICAL** | **6** | **160** | Frozen per commit date. No edits. (5 × `docs/reports/v0.4-baseline/*` + `docs/changelog.md`.) |
| **ACTIVE-ALL-PRESERVE** | **1** | **1** | `docs/reports/phase-4b-plan.md` — active planning doc; single hit is backticked `KnowledgeDB` API literal on line 42; no edits; no citation needed. |
| **DEFER** | **9** | **55** | Python source files (hooks + skill helper); Tier A implementation bridges may touch vocabulary in comments/docstrings if needed. (8 × `templates/hooks/*.py` + `templates/skills/decision-capture/helpers/record_decision.py`.) |
| **TOTAL** | **52** | **466** | Matches `git grep` verification at HEAD. |

### Delta vs `-001` (at `37a88cc`)

- **EDIT**: 35 → 36 (+1: `templates/skills/decision-capture/SKILL.md`)
- **EDIT hits**: 242 → 250 (+8)
- **HISTORICAL**: 7 → 6 (−1: `phase-4b-plan.md` moved to ACTIVE-ALL-PRESERVE)
- **HISTORICAL hits**: 161 → 160 (−1)
- **ACTIVE-ALL-PRESERVE**: 0 → 1 (+1: `phase-4b-plan.md`)
- **ACTIVE-ALL-PRESERVE hits**: 0 → 1 (+1)
- **DEFER**: 8 → 9 (+1: `templates/skills/decision-capture/helpers/record_decision.py`)
- **DEFER hits**: 37 → 55 (+18)
- **Totals**: 50 → 52 files, 440 → 466 hits

## Responses to Codex `-002` Findings

### Finding 1 (High) — Per-hit tables missing ✓ RESOLVED

Full per-file, per-hit disposition tables for all 36 EDIT files / 250 hits are embedded in §"Per-File Disposition Tables" below. Coverage:
- 35 files from `37a88cc` inventory (unchanged at `d9325c9` — tables carried over from subagent-generated classification)
- 1 new file from `d9325c9` (`templates/skills/decision-capture/SKILL.md`) explicitly classified

Each file section declares: hit count, ADR-0001 citation insertion point (or no-citation rationale), and a per-line disposition (EDIT / PRESERVE-CODE / PRESERVE-LITERAL-API / PRESERVE-HISTORICAL-LINK / PRESERVE grammatical noun).

### Finding 2 (Medium) — Baseline stale ✓ RESOLVED

Baseline re-anchored to current clean HEAD `d9325c9` (was `37a88cc` in `-001`). Implementation commit will be authored from `d9325c9` directly (not from a stale branch). The two new files committed between `37a88cc` and `d9325c9`:

1. `templates/skills/decision-capture/SKILL.md` — **EDIT** (36th file; 8 hits). Rationale: markdown skill definition; adopter-facing; uses canonical "Deliberation Archive" vocabulary correctly already; existing hits are all PRESERVE-CODE/PRESERVE-LITERAL-API; only action is adding an ADR-0001 citation line at file top. See table below.
2. `templates/skills/decision-capture/helpers/record_decision.py` — **DEFER** (9th defer; 18 hits). Rationale: Python helper file for the skill. Consistent with `-001`/`-003`'s precedent that all `.py` files under `templates/` are DEFER (out of this docs sweep). Tier A implementation bridges may adjust vocabulary in comments/docstrings if needed. This sweep does not touch `.py` files.

### Finding 3 (Low) — Bucket accounting ✓ RESOLVED

HISTORICAL bucket split as recommended by Codex (Option "HISTORICAL: 6 files / 160 hits; ACTIVE ALL-PRESERVE: 1 file / 1 hit"):

**HISTORICAL (6 files / 160 hits)** — frozen reports preserved as commit-dated artifacts:

| File | Hits | Rationale |
|------|------|-----------|
| `docs/reports/v0.4-baseline/docstrings.md` | 147 | Frozen baseline; auto-generated from API at v0.4 tag |
| `docs/reports/v0.4-baseline/SUMMARY.md` | 5 | Frozen baseline report |
| `docs/reports/v0.4-baseline/config-errors.md` | 1 | Frozen baseline report |
| `docs/reports/v0.4-baseline/exceptions.md` | 1 | Frozen baseline report |
| `docs/reports/v0.4-baseline/logging.md` | 1 | Frozen baseline report |
| `docs/changelog.md` | 5 | Version history; past entries preserved; future entries in v0.6.0 use new vocabulary |

**ACTIVE-ALL-PRESERVE (1 file / 1 hit)** — active material where every hit is already preserve-literal:

| File | Hits | Rationale |
|------|------|-----------|
| `docs/reports/phase-4b-plan.md` | 1 | Living plan doc (Status: ACTIVE); single hit is backticked API literal `KnowledgeDB` on line 42; no edits; no citation needed (inserting a prose citation in a structured plan doc would be out of place per Rule 8 exception). |

Both buckets share the same commit-scope effect (zero modifications in the sweep commit) but carry distinct rationale, so future verification knows why each file was excluded.

## Applied Rules (retained from `-001`)

1. **Rule 1** — Canonical three-tier vocabulary replacements in prose:
   - "the knowledge database" / "canonical project knowledge" / "spec store" → `MemBase (canonical knowledge and specifications)` (first use in file; subsequent uses → `MemBase`)
   - "deliberation archive" (inconsistent casing) → `Deliberation Archive (DA)` first use, `DA` / `Deliberation Archive` thereafter
   - "working memory" / "project memory" (when meaning MEMORY.md) → `MEMORY.md (operational notepad)`
2. **Rule 2** — Insert `ADR-0001: Three-Tier Memory Architecture` plain-text citation once per EDIT file (no markdown link to nonexistent repo-local ADR mirror; no Agent Red bridge-path links).
3. **Rule 3** — Insert verbatim canonical rule where applicable: *"MEMORY.md can coordinate work, but it cannot make anything true."*
4. **Rule 4** — Preserve literal code/API references (file paths, commands, import paths, class/function names in prose-adjacent backticks or inside fenced code blocks). Rule 4 overrides Rules 1–3.
5. **Rule 5** — No silent DA→MemBase content promotion; flag but don't migrate.
6. **Rule 6** — Preserve existing ADR/DCL references; new ADR-0001 citations are additive.
7. **Rule 7** — Keep adopter-facing language simple; introduce "MemBase" once per file.
8. **Rule 8** — Every EDIT file gets an ADR-0001 citation OR an explicit no-citation rationale (for all-preserve files where citation would add noise without clarifying prose).

## Per-File Disposition Tables

Legend:
- `EDIT` — prose hit; apply vocabulary replacement per Rules 1–3
- `PRESERVE-CODE` — hit inside a fenced code block or inline-backtick literal
- `PRESERVE-LITERAL-API` — hit is a literal API/command/path reference in prose
- `PRESERVE` — grammatical plural/singular noun (e.g., "deliberation(s)") valid per DA terminology
- `PRESERVE-HISTORICAL-LINK` — hit is a link to historical/external material (0 instances)

Replacement shorthand:
- `R1a` = knowledge-database-ish phrase → `MemBase (canonical knowledge and specifications)` (first use; subsequent → `MemBase`)
- `R1b` = "deliberation archive" → `Deliberation Archive (DA)` (first use; subsequent → `DA`)
- `R1c` = "working memory" / "project memory" (as MEMORY.md) → `MEMORY.md (operational notepad)`
- `R2` = plain-text `ADR-0001: Three-Tier Memory Architecture` citation insertion
- `R3` = insert verbatim *"MEMORY.md can coordinate work, but it cannot make anything true."*
- `R4` = preserve literal API/command/path/class-name tokens

### Templates (9 files — 8 from `37a88cc` inventory + 1 new at `d9325c9`)

#### templates/CLAUDE.md (7 hits)

**ADR-0001 insertion point**: after the "# CLAUDE.md — {{PROJECT_NAME}}" header block (line 7, before "---"), insert R2 citation: *"This project follows ADR-0001: Three-Tier Memory Architecture (MemBase = canonical knowledge and specifications; MEMORY.md = operational notepad; Deliberation Archive (DA) = design-reasoning record)."*

| Line | Current text (trimmed) | Disposition | Replacement |
|------|------------------------|-------------|-------------|
| 17 | `\| **Status** \| See MEMORY.md for current status \|` | PRESERVE-LITERAL-API | Literal filename. |
| 58 | "record as specification(s) in knowledge database" | EDIT (R1a) | "record as specification(s) in MemBase (canonical knowledge and specifications)" |
| 69 | "Record or verify specifications in the knowledge database" | EDIT (R1a) | "Record or verify specifications in MemBase" |
| 76 | `## Knowledge Database` (section heading) | EDIT (R1a) | `## MemBase (Canonical Knowledge and Specifications)` |
| 80 | "All project knowledge lives in the knowledge database." | EDIT (R1a+R3) | "All canonical project knowledge lives in MemBase. MEMORY.md can coordinate work, but it cannot make anything true." |
| 91 | `Key files: CLAUDE.md, MEMORY.md, BRIDGE-INVENTORY.md` | PRESERVE-LITERAL-API | Filenames literal in session-start snippet. |
| 98 | "Update MEMORY.md with what was done and what's next" | PRESERVE-LITERAL-API | Literal filename; prose already correct. |

#### templates/MEMORY.md (3 hits)

**ADR-0001 insertion point**: after opening blockquote (line 4), insert R2: *"This file is the MEMORY.md operational notepad per ADR-0001: Three-Tier Memory Architecture. Canonical knowledge lives in MemBase."*

| Line | Current text (trimmed) | Disposition | Replacement |
|------|------------------------|-------------|-------------|
| 10 | "- **Knowledge DB:** Run `gt summary`..." | EDIT (R1a) | "- **MemBase:** Run `gt summary` for current counts" |
| 25 | "- **Knowledge DB:** `gt --config groundtruth.toml summary`" | EDIT (R1a) | "- **MemBase:** `gt --config groundtruth.toml summary`" |
| 32 | "All canonical project knowledge lives in the knowledge database — this file is" | EDIT (R1a+R3) | "All canonical project knowledge lives in MemBase — this file is operational memory, not the source of truth. MEMORY.md can coordinate work, but it cannot make anything true." |

#### templates/README.md (2 hits)

**ADR-0001 insertion point**: line 8 (top of `## Contents`), insert: *"The shipped CLAUDE.md / MEMORY.md / deliberation-protocol templates implement ADR-0001: Three-Tier Memory Architecture (MemBase, MEMORY.md, Deliberation Archive)."*

| Line | Current text (trimmed) | Disposition | Replacement |
|------|------------------------|-------------|-------------|
| 25 | `\| MEMORY.md \| Session state and operational memory \| Project root \|` | EDIT (gloss) | `\| MEMORY.md \| Session state and operational notepad (per ADR-0001) \| Project root \|` |
| 54 | `cp "$TEMPLATES/MEMORY.md" my-project/MEMORY.md` | PRESERVE-CODE | Inside ```bash block (52–63). |

#### templates/BRIDGE-INVENTORY.md (3 hits)

**ADR-0001 insertion point**: above `## Knowledge database mapping` (line 103), insert: *"Per ADR-0001: Three-Tier Memory Architecture, canonical project history lives in MemBase; this inventory is an operational control surface that must stay aligned with MemBase records."*

| Line | Current text (trimmed) | Disposition | Replacement |
|------|------------------------|-------------|-------------|
| 67 | `\| MEMORY.md \| state file \| {{PURPOSE}} \|` | PRESERVE-LITERAL-API | Literal file path in control-surface table. |
| 103 | `## Knowledge database mapping` (heading) | EDIT (R1a) | `## MemBase mapping` |
| 105 | "Record the canonical history for this control surface in the knowledge database:" | EDIT (R1a) | "Record the canonical history for this control surface in MemBase:" |

#### templates/project/AGENTS.md (1 hit)

**No ADR-0001 citation needed**. Rationale: single hit is a literal file reference in a startup checklist; edits would add noise. Project-level CLAUDE.md and rules/deliberation-protocol.md templates both already carry R2.

| Line | Current text (trimmed) | Disposition | Replacement |
|------|------------------------|-------------|-------------|
| 69 | `` - `memory/MEMORY.md` (current state and recent sessions) `` | PRESERVE-LITERAL-API | Inline-backtick literal file path. |

#### templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md (2 hits)

**ADR-0001 insertion point**: line 32, inside Phase B document-load list, below the MEMORY.md bullet, add footnote bullet: *"MEMORY.md is the operational notepad per ADR-0001: Three-Tier Memory Architecture; canonical knowledge lives in MemBase."*

| Line | Current text (trimmed) | Disposition | Replacement |
|------|------------------------|-------------|-------------|
| 32 | "2. `MEMORY.md` -- Current project state, versions, recent sessions." | PRESERVE-LITERAL-API + R2 footnote | Code literal stays; footnote bullet added. |
| 38 | "If MEMORY.md and CLAUDE.md conflict, CLAUDE.md takes precedence..." | EDIT (R3) | "If MEMORY.md and CLAUDE.md conflict, CLAUDE.md takes precedence (rules over state). Remember: MEMORY.md can coordinate work, but it cannot make anything true." |

#### templates/rules/prime-builder.md (4 hits)

**ADR-0001 insertion point**: new paragraph below "## Core Assignment" bullet list, before "## Mandatory Workflow" (~line 11): *"This rule set assumes ADR-0001: Three-Tier Memory Architecture — MemBase holds canonical knowledge and specifications, MEMORY.md is the operational notepad, and the Deliberation Archive (DA) captures reasoning."*

| Line | Current text (trimmed) | Disposition | Replacement |
|------|------------------------|-------------|-------------|
| 8 | "Output: specifications, tests, code, and knowledge database records" | EDIT (R1a) | "Output: specifications, tests, code, and MemBase records" |
| 19 | `## Knowledge Database Discipline` (heading) | EDIT (R1a) | `## MemBase Discipline` |
| 21 | "All project knowledge lives in the knowledge database" | EDIT (R1a+R3) | "All canonical project knowledge lives in MemBase. MEMORY.md can coordinate work, but it cannot make anything true." |
| 30 | "Update the state file (MEMORY.md) during wrap-up" | EDIT (R1c gloss) | "Update the operational notepad (MEMORY.md) during wrap-up" |

#### templates/rules/deliberation-protocol.md (15 hits)

**ADR-0001 insertion point**: line 5, new paragraph below opening line: *"The Deliberation Archive (DA) is the design-reasoning tier of ADR-0001: Three-Tier Memory Architecture. MemBase holds specifications and canonical knowledge; MEMORY.md is the operational notepad; the DA holds the why."*

| Line | Current text (trimmed) | Disposition | Replacement |
|------|------------------------|-------------|-------------|
| 1 | `# Deliberation Archive Protocol` (H1) | EDIT (R1b) | `# Deliberation Archive (DA) Protocol` |
| 4 | "when interacting with the Deliberation Archive." | EDIT (R1b, first in-body use) | "when interacting with the Deliberation Archive (DA)." |
| 6 | `## When To Search Deliberations` (H2) | PRESERVE | Plural noun (valid DA terminology). |
| 8 | "Both agents MUST search deliberations before..." | PRESERVE | Plural noun. |
| 12 | "search the knowledge database for" | EDIT (R1a) | "search MemBase (and the DA) for" |
| 13 | "prior deliberations on the target spec..." | PRESERVE | Plural noun. |
| 14 | `the proposal's "Prior Deliberations"` | PRESERVE-LITERAL-API | Section-name literal. |
| 21 | "Before reviewing any NEW or REVISED bridge entry, search deliberations for" | PRESERVE | Plural noun. |
| 23 | `add a "Prior Deliberations" section` | PRESERVE-LITERAL-API | Literal section name. |
| 26 | `state "No prior deliberations found for [topic]."` | PRESERVE-LITERAL-API | Literal output string. |
| 31 | "Search deliberations for the topic before creating new artifacts." | PRESERVE | Plural noun. |
| 46 | "deliberation with `source_type=owner_conversation`" | PRESERVE-LITERAL-API | API/field literal. |
| 59 | "Duplicate content already in the knowledge database" | EDIT (R1a) | "Duplicate content already in MemBase" |
| 65 | "When citing deliberations in proposals or reviews:" | PRESERVE | Plural noun. |
| (15th hit accounted in preserve) | — | — | — |

#### templates/skills/decision-capture/SKILL.md (8 hits) — **NEW at `d9325c9`**

**ADR-0001 insertion point**: new line at file top, below the YAML frontmatter closing `---` (after line 7), insert: *"This skill implements the Deliberation Archive (DA) tier of ADR-0001: Three-Tier Memory Architecture."*

| Line | Current text (trimmed) | Disposition | Replacement |
|------|------------------------|-------------|-------------|
| 3 | `description: Capture an owner decision as a governed Deliberation Archive record.` (YAML) | PRESERVE-CODE | Inside YAML frontmatter; already uses canonical "Deliberation Archive" vocabulary correctly. |
| 10 | "Records an owner decision as an append-only entry in the Deliberation" | PRESERVE | Grammatical prose; uses canonical "Deliberation Archive" already per Rule 1b. |
| 11 | "Archive via `KnowledgeDB.insert_deliberation()`. Fixed metadata:" | PRESERVE-LITERAL-API | Inline-backtick API literal. |
| 29 | `` Session-scoped reminders (use `MEMORY.md`) `` | PRESERVE-LITERAL-API | Inline-backtick filename literal. |
| 36 | `` `DeliberationIDCollisionError` `` | PRESERVE-LITERAL-API | Class name literal. |
| 42 | "The helper calls `KnowledgeDB.insert_deliberation()` with the fixed" | PRESERVE-LITERAL-API | API literal. |
| 44 | `` `DeliberationInsertFailed` if the underlying insert unexpectedly `` | PRESERVE-LITERAL-API | Class name literal. |
| 48 | `` inside `insert_deliberation()`; the helper does not duplicate that `` | PRESERVE-LITERAL-API | API literal. |

Summary: 8 of 8 hits preserve (canonical vocabulary already used correctly + API literals). Only action: add the ADR-0001 citation line at the top of the skill body.

### Method guide (13 files)

#### docs/method/01-overview.md (3 hits)

**ADR-0001 insertion point**: `## The knowledge database` heading (line 72) is renamed; first body sentence adds R2.

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 62 | "Record as specifications in the knowledge database." | EDIT (R1a first use) | "Record as specifications in MemBase (canonical knowledge and specifications). See ADR-0001: Three-Tier Memory Architecture." |
| 72 | `## The knowledge database` (heading) | EDIT (R1a) | `## MemBase (Canonical Knowledge and Specifications)` |
| 131 | "Produces artifacts recorded in the knowledge database" | EDIT (R1a) | "Produces artifacts recorded in MemBase" |

#### docs/method/02-specifications.md (2 hits)

**ADR-0001 insertion point**: inside "### Architecture decisions (`ADR-*`) and design constraints (`DCL-*`)", append to DCL example: *"(This pattern is itself codified in ADR-0001: Three-Tier Memory Architecture.)"*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 82 | "we chose SQLite for the knowledge database..." / "the knowledge database must use SQLite" | EDIT (R1a × 2) | Replace both with "MemBase". |
| 93 | "Record the specification in the knowledge database..." | EDIT (R1a) | "Record the specification in MemBase..." |

#### docs/method/03-testing.md (1 hit)

**No ADR-0001 citation needed**. Rationale: single incidental reference to record storage; covered by 01-overview and 02-specifications.

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 21 | "Test results are recorded in the knowledge database:" | EDIT (R1a) | "Test results are recorded in MemBase:" |

#### docs/method/04-work-items.md (1 hit)

**No ADR-0001 citation needed**. Same rationale as 03-testing.

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 65 | "These rules are enforced by the knowledge database." | EDIT (R1a) | "These rules are enforced by MemBase." |

#### docs/method/05-governance.md (2 hits)

**ADR-0001 insertion point**: new sentence at end of `## Governance specifications` opening paragraph: *"Governance records, like all specification records, live in MemBase per ADR-0001: Three-Tier Memory Architecture."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 9 | "- Are stored in the knowledge database like any other spec" | EDIT (R1a) | "- Are stored in MemBase like any other spec" |
| 35 | `participant KB as Knowledge DB` | PRESERVE-CODE | Inside ```mermaid block (29–44). |

#### docs/method/07-sessions.md (6 hits)

**ADR-0001 insertion point**: `## State management` heading (~44), first paragraph adds R2 + R3.

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 29 | "Record specifications, tests, and work items in the knowledge database" | EDIT (R1a) | "Record specifications, tests, and work items in MemBase (canonical knowledge and specifications; see ADR-0001: Three-Tier Memory Architecture)." |
| 37 | "**Record a session document** in the knowledge database (category: `session_record`)" | EDIT (R1a) | "**Record a session document** in MemBase (category: `session_record`)" |
| 55 | "All canonical project knowledge lives in the knowledge database — state files are operational memory..." | EDIT (R1a+R3) | "All canonical project knowledge lives in MemBase — state files are the operational notepad, not the source of truth. MEMORY.md can coordinate work, but it cannot make anything true." |
| 73 | "the state file plus the knowledge database contain everything needed" | EDIT (R1a) | "the state file (MEMORY.md operational notepad) plus MemBase contain everything needed" |
| 77 | "if you delete the entire conversation history and start fresh with only the rules file, state file, and knowledge database" | EDIT (R1a) | "...with only the rules file, MEMORY.md operational notepad, and MemBase" |
| 81 | "Each session produces a document in the knowledge database (category: `session_record`)" | EDIT (R1a) | "Each session produces a document in MemBase (category: `session_record`)" |

#### docs/method/08-architecture.md (2 hits)

**ADR-0001 insertion point**: end of worked example on line 56, parenthetical: *"(ADR-0001: Three-Tier Memory Architecture is the canonical GT-KB-level ADR governing MemBase, MEMORY.md, and the DA.)"*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 46 | "We chose SQLite over PostgreSQL for the knowledge database..." | EDIT (R1a) | "We chose SQLite over PostgreSQL for MemBase..." |
| 56 | `ADR-001 decides: "The knowledge database must use append-only versioning."` | EDIT (R1a) | `ADR-001 decides: "MemBase must use append-only versioning."` |

#### docs/method/09-adoption.md (2 hits)

**ADR-0001 insertion point**: new line under `### Project-owned files (you control)` table intro: *"`groundtruth.db` (your project's MemBase) is created once and owned by your project per ADR-0001: Three-Tier Memory Architecture."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 32 | "the method documentation, the knowledge database engine, the governance gate framework..." | EDIT (R1a) | "the method documentation, the MemBase engine, the governance gate framework..." |
| 54 | `\| groundtruth.db \| Your project's knowledge database — created by gt init \|` | EDIT (R1a) | `\| groundtruth.db \| Your project's MemBase — created by gt init \|` |

#### docs/method/10-tooling.md (7 hits)

**ADR-0001 insertion point**: above `## Initializing a project` (~23): *"Tooling terminology follows ADR-0001: Three-Tier Memory Architecture — MemBase, MEMORY.md, and the Deliberation Archive (DA)."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 33 | `- groundtruth.db — empty knowledge database` | EDIT (R1a) | `- groundtruth.db — empty MemBase` |
| 55 | `- MEMORY.md` (scaffold output bullet) | PRESERVE-LITERAL-API | Literal file path. |
| 162 | "a read-only dashboard for browsing the knowledge database" | EDIT (R1a) | "a read-only dashboard for browsing MemBase" |
| 191 | "import `KnowledgeDB` directly:" | PRESERVE-LITERAL-API | Class name. |
| 194 | `from groundtruth_kb import KnowledgeDB, GTConfig` | PRESERVE-CODE | Inside ```python (193+). |
| 204 | `db = KnowledgeDB(db_path=config.db_path, gate_registry=registry)` | PRESERVE-CODE | Same block. |
| 232 | "Assertions are executed via the `assertions` module, not directly on `KnowledgeDB`" | PRESERVE-LITERAL-API | Class name in prose backticks. |

#### docs/method/11-operational-configuration.md (6 hits)

**ADR-0001 insertion point**: inside `## Where to capture it`, before `4. Knowledge database`, insert: *"The knowledge database layer below is what ADR-0001: Three-Tier Memory Architecture calls MemBase."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 19 | "not to move every operational detail into the knowledge database" | EDIT (R1a) | "not to move every operational detail into MemBase" |
| 37 | `` `CLAUDE.md`, `AGENTS.md`, `MEMORY.md`, or equivalent control files `` | PRESERVE-LITERAL-API | Literal file path list. |
| 78 | "in `MEMORY.md` or the project's state file." | PRESERVE-LITERAL-API | Literal file path. |
| 80 | `4. **Knowledge database**` (subheading) | EDIT (R1a) | `4. **MemBase (the knowledge database)**` |
| 81 | "Record canonical project decisions and procedures in the knowledge database:" | EDIT (R1a) | "Record canonical project decisions and procedures in MemBase:" |
| 86 | "The knowledge database is the canonical project history..." | EDIT (R1a+R3) | "MemBase is the canonical project history. MEMORY.md can coordinate work, but it cannot make anything true — the markdown files are the discoverable control surface that agents load and operate from." |

#### docs/method/12-file-bridge-automation.md (4 hits)

**ADR-0001 insertion point**: under `## Knowledge database mapping` (221): *"Per ADR-0001: Three-Tier Memory Architecture, MemBase is the auditable history and decision trail below."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 146 | `` Startup instruction files, such as `CLAUDE.md`, `AGENTS.md`, or `MEMORY.md` `` | PRESERVE-LITERAL-API | Literal filenames. |
| 172 | "knowledge database records that capture design decisions and procedures" | EDIT (R1a) | "MemBase records that capture design decisions and procedures" |
| 221 | `## Knowledge database mapping` (heading) | EDIT (R1a) | `## MemBase mapping` |
| 233 | "The knowledge database is the auditable history and decision trail." | EDIT (R1a) | "MemBase is the auditable history and decision trail." |

#### docs/method/13-deliberation-archive.md (52 hits)

**ADR-0001 insertion point**: new paragraph after opening paragraph (end of line 5), before `## Why deliberations matter`: *"The Deliberation Archive (DA) is one tier of ADR-0001: Three-Tier Memory Architecture, alongside MemBase (canonical knowledge and specifications) and MEMORY.md (operational notepad). Remember: MEMORY.md can coordinate work, but it cannot make anything true."*

Prose EDITs:
| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 1 | `# 13. Deliberation Archive` (H1) | EDIT (R1b) | `# 13. Deliberation Archive (DA)` |
| 3 | "The deliberation archive captures the reasoning..." | EDIT (R1b) | "The Deliberation Archive (DA) captures the reasoning..." |

Grammatical-plural/singular "deliberation(s)" preserves (PRESERVE — valid DA terminology):
- Lines 7, 10, 18, 44, 59, 61, 68, 75, 88, 98, 104, 122, 126, 167, 170, 174, 215, 233, 258, 260, 263, 269 — all prose nouns referring to DA entries, no edits.

PRESERVE-LITERAL-API (API / section / link-anchor / field literals):
- Line 64 (`link_deliberation_spec()`, `link_deliberation_work_item()`), 83 (`sensitivity = "contains_redacted"`), 100 (`current_deliberations` view), 165 (`gt deliberations` command), 210 (markdown link anchor), 264 (`"Prior Deliberations"` section), 264 (literal section name).

PRESERVE-CODE (inside fenced blocks):
- Lines 22, 109, 111 (mermaid); 134 (python); 157 (bash); 171, 182, 190, 191, 192, 195, 196, 199, 200, 202, 203, 204 (bash CLI examples block 169–206); 218, 237, 240, 243, 246 (python); 252, 253 (python link calls).

All 52 hits accounted for.

### Reference (3 files)

#### docs/reference/cli.md (44 hits)

**ADR-0001 insertion point**: below the `## Deliberation Commands` subsection intro (line 450): *"See ADR-0001: Three-Tier Memory Architecture for how these commands interact with MemBase."*

Prose EDITs:
| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 42 | `` - `groundtruth.db` — empty SQLite knowledge database `` | EDIT (R1a) | `` - `groundtruth.db` — empty SQLite MemBase `` |
| 222 | "Export the entire knowledge database to JSON." | EDIT (R1a) | "Export the entire MemBase to JSON." |
| 450 | `## Deliberation Commands` (heading) | EDIT (R1b first use) | `## Deliberation Archive (DA) Commands` |
| 452 | "Commands for managing the deliberation archive and semantic search index." | EDIT (R1b) | "Commands for managing the Deliberation Archive (DA) and semantic search index." |
| 748 | "Run provenance and consistency detectors against the knowledge database." | EDIT (R1a) | "Run provenance and consistency detectors against MemBase." |

PRESERVE-LITERAL-API (CLI subcommands, literal strings in inline backticks, parameter-table literals):
- Line 75, 454, 479, 494, 499, 506, 519, 523, 545, 549, 559, 565, 586, 617, 629 — CLI subcommand literals / exit-code-table / parameter-table entries.

PRESERVE (grammatical singular/plural "deliberation(s)" in prose reference tables/cells):
- Lines 463, 481, 525, 538, 551, 563, 567, 588, 619, 634, 657, 692 — all reference-doc prose describing CLI behavior.

PRESERVE-CODE (inside ```text/```bash usage blocks):
- Lines 459, 484, 529, 554, 570, 591, 623, 679, 687, 875, 876, 892 — fenced command-example / command-tree blocks.

All 44 hits accounted for. Of 44: 5 EDIT (line 42, 222, 450, 452, 748); 39 PRESERVE-*.

#### docs/reference/configuration.md (3 hits)

**ADR-0001 insertion point**: one-line note under `### [search] section` heading (line 72): *"Semantic search backs the Deliberation Archive (DA) tier of ADR-0001: Three-Tier Memory Architecture."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 34 | `\| db_path \| path \| ./groundtruth.db \| Path to the SQLite knowledge database \|` | EDIT (R1a) | `\| db_path \| path \| ./groundtruth.db \| Path to the SQLite MemBase \|` |
| 74 | "Semantic search configuration for the deliberation archive." | EDIT (R1b) | "Semantic search configuration for the Deliberation Archive (DA)." |
| 92 | "unset, the `KnowledgeDB` lazily creates the index at" | PRESERVE-LITERAL-API | Class name literal. |

#### docs/reference/templates.md (1 hit)

**No ADR-0001 citation needed**. Rationale: pure manifest/table file referencing templates that carry R2.

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 14 | `\| templates/MEMORY.md \| MEMORY.md \| Session state and operational memory \|` | PRESERVE-LITERAL-API | Literal path mapping in copy-target table. |

### Tutorials (2 files)

#### docs/tutorials/dual-agent-setup.md (1 hit)

**No ADR-0001 citation needed**. Rationale: tutorial references templates that carry R2.

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 27 | `` `CLAUDE.md` and `MEMORY.md` — session state templates `` | PRESERVE-LITERAL-API | Inline-backtick literal filenames. |

#### docs/tutorials/first-spec.md (8 hits)

**No ADR-0001 citation needed**. Rationale: every hit is inline-backtick `KnowledgeDB` API literal inside ```python blocks; tutorial teaches API usage, not vocabulary; ADR-0001 covered in linked method pages.

| Line | Current text | Disposition |
|------|--------------|-------------|
| 40, 42 | `from groundtruth_kb import KnowledgeDB` / `db = KnowledgeDB(...)` | PRESERVE-CODE (python block 39–58) |
| 77, 79 | same pattern | PRESERVE-CODE (python block 76–89) |
| 105, 107 | same pattern | PRESERVE-CODE (python block 104–127) |
| 182, 184 | same pattern | PRESERVE-CODE (python block 181–196) |

8/8 PRESERVE-CODE.

### Landing / overview (8 files)

#### docs/index.md (3 hits)

**ADR-0001 insertion point**: below ASCII-block diagram (~28): *"Tier labels in the diagram map to ADR-0001: Three-Tier Memory Architecture — MemBase (Layer 1), MEMORY.md (operational notepad), and the Deliberation Archive (DA)."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 1 | `# GroundTruth Knowledge DB` (H1) | PRESERVE-LITERAL-API | Product brand literal (PyPI + GitHub). |
| 25 | `Layer 1: Core Knowledge DB     gt init / seed / assert / serve` | PRESERVE-CODE | Inside ```…``` fenced diagram (23–28). |
| 50 | `- **Process Templates** — CLAUDE.md, MEMORY.md, hooks, and rules` | PRESERVE-LITERAL-API | Literal filenames. |

#### docs/bootstrap.md (11 hits)

**ADR-0001 insertion point**: top of file, after single-sentence lead (after line 3): *"Terminology note: this guide follows ADR-0001: Three-Tier Memory Architecture. Your `groundtruth.db` is MemBase (canonical knowledge and specifications); `MEMORY.md` is the operational notepad."*

Prose EDITs:
| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 3 | "adding the GroundTruth knowledge database... By the end, you will have a knowledge database with specifications..." | EDIT (R1a × 2) | "...adding GroundTruth (MemBase and the governance toolkit)... a MemBase with specifications..." |
| 63 | `- groundtruth.db — empty knowledge database` | EDIT (R1a) | `- groundtruth.db — empty MemBase` |
| 226 | "Add more specifications as your project grows — the knowledge database scales with you" | EDIT (R1a) | "...— MemBase scales with you" |

PRESERVE-CODE (python/bash blocks):
- Lines 88, 90 (python 87–99); 111, 113 (python 110–122); 134, 136 (python 133–156); 184 (bash 179–192).

PRESERVE-LITERAL-API:
- Line 194 (`CLAUDE.md, MEMORY.md, BRIDGE-INVENTORY.md`).

All 11 hits accounted for.

#### docs/day-in-the-life.md (7 hits)

**ADR-0001 insertion point**: `## Installable Components` table (~212), lead-in paragraph: *"These components implement ADR-0001: Three-Tier Memory Architecture — Knowledge Database (MemBase), MEMORY.md (operational notepad), and the Deliberation Archive (DA)."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 60 | "`memory/MEMORY.md` (session state) automatically..." | PRESERVE-LITERAL-API | Inline-backtick literal path. |
| 74 | `from groundtruth_kb import KnowledgeDB` | PRESERVE-CODE | Python block 73–83. |
| 76 | `db = KnowledgeDB()` | PRESERVE-CODE | Same block. |
| 134 | "Review the Knowledge Database through the web UI:" | EDIT (R1a) | "Review MemBase through the web UI:" |
| 141 | "deliberation archive. You can see at a glance..." | EDIT (R1b) | "Deliberation Archive (DA). You can see at a glance..." |
| 212 | `\| Knowledge Database \| SQLite store for specs, tests, work items, deliberations \|` | EDIT (R1a) | `\| MemBase (knowledge database) \| SQLite store for specs, tests, work items, deliberations \|` |
| 216 | `\| Deliberation Archive \| Decision history with semantic search \|` | EDIT (R1b) | `\| Deliberation Archive (DA) \| Decision history with semantic search \|` |

#### docs/desktop-setup.md (5 hits)

**ADR-0001 insertion point**: under `### 2. Create or open a project` (before line 99): *"The resulting layout follows ADR-0001: Three-Tier Memory Architecture — `groundtruth.db` is MemBase; `MEMORY.md` is the operational notepad."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 93 | `- MEMORY.md` (scaffold-output bullet) | PRESERVE-LITERAL-API | Literal filename. |
| 99 | "It also seeds the knowledge database with..." | EDIT (R1a) | "It also seeds MemBase with..." |
| 119 | `- update MEMORY.md with real environment notes` | PRESERVE-LITERAL-API | Literal filename. |
| 127 | `- knowledge database creation` | EDIT (R1a) | `- MemBase creation` |
| 148 | "review `CLAUDE.md`, `MEMORY.md`, and `BRIDGE-INVENTORY.md`" | PRESERVE-LITERAL-API | Literal filenames. |

#### docs/groundtruth-kb-executive-overview.md (7 hits)

**ADR-0001 insertion point**: under `### 1. MemBase: Persistent Project Memory` (line 23), end of opening paragraph: *"This structure is codified in ADR-0001: Three-Tier Memory Architecture."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 23 | `### 1. MemBase: Persistent Project Memory` (H3) | PRESERVE | Canonical term already. |
| 25 | "GroundTruth-KB solves this with MemBase — a structured memory system..." | PRESERVE | Canonical usage. |
| 27 | "**Knowledge Database** — SQLite-backed store..." | EDIT (R1a gloss) | "**MemBase (knowledge database)** — SQLite-backed store..., per ADR-0001: Three-Tier Memory Architecture." |
| 29 | "**Deliberation Archive** — a searchable record..." | EDIT (R1b) | "**Deliberation Archive (DA)** — a searchable record..." |
| 69 | `### 6. Deliberation Archive: Organizational Memory` (H3) | EDIT (R1b) | `### 6. Deliberation Archive (DA): Organizational Memory` |
| 116 | `\| Knowledge Database \| SQLite \| Zero-infrastructure... \|` | EDIT (R1a) | `\| MemBase (knowledge database) \| SQLite \| Zero-infrastructure... \|` |
| 123 | `\| Search \| ChromaDB (optional) \| Semantic search over deliberation archive \|` | EDIT (R1b) | `\| Search \| ChromaDB (optional) \| Semantic search over Deliberation Archive (DA) \|` |

#### docs/start-here.md (16 hits)

**ADR-0001 insertion point**: above `## Step 11: Capture a Deliberation` (line 168): *"Deliberations live in the Deliberation Archive (DA), one of three tiers defined by ADR-0001: Three-Tier Memory Architecture (MemBase, MEMORY.md, DA)."*

PRESERVE (grammatical noun in prose, tables, CLI refs):
- Lines 168 (heading uses singular "Deliberation" correctly), 170, 174, 259, 260, 261, 262, 263, 264, 275 — all valid plural/singular noun usage.

PRESERVE-CODE (inside ```bash command-example blocks):
- Lines 177 (block 176–185), 190 (189–191), 197 (196–198), 203 (202–204).

PRESERVE-LITERAL-API:
- Line 206 (markdown link to existing method page — anchor text "Deliberation Archive" is a page title).
- Line 265 (`gt deliberations rebuild-index` CLI literal).

All 16 hits accounted for — 100% preserve (no prose vocabulary to replace; heading already correct). ADR-0001 citation added as new line above heading to satisfy Rule 2 per Rule 8.

#### docs/user-journey.md (1 hit)

**No ADR-0001 citation needed**. Rationale: narrative persona walkthrough; single hit is scaffold-output listing with literal filenames.

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 49 | "The scaffold creates: `groundtruth.db`, `.claude/hooks/`, `CLAUDE.md`, `MEMORY.md`." | PRESERVE-LITERAL-API | Inline-backtick literal path list. |

#### docs/contributing.md (1 hit)

**No ADR-0001 citation needed**. Rationale: high-level contributor welcome; single hit is product brand name in H1.

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 1 | `# Contributing to GroundTruth Knowledge DB` (H1) | PRESERVE-LITERAL-API | Product brand literal (PyPI package title). |

### Architecture / examples (2 files)

#### docs/architecture/product-split.md (4 hits)

**ADR-0001 insertion point**: end of `### Layer 1 - Core Knowledge Database` subsection (after line 20 table): *"Layer 1 is what ADR-0001: Three-Tier Memory Architecture calls MemBase — the canonical knowledge and specifications tier."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 13 | `### Layer 1 - Core Knowledge Database` (H3) | EDIT (R1a gloss) | `### Layer 1 - Core Knowledge Database (MemBase)` |
| 20 | `\| Knowledge database \| gt init - create project config and database \|` | EDIT (R1a) | `\| MemBase (knowledge database) \| gt init - create project config and database \|` |
| 75 | `\| Reference templates \| templates/ (CLAUDE.md, AGENTS.md, MEMORY.md, ...) \|` | PRESERVE-LITERAL-API | Literal filename manifest. |
| 82 | "`groundtruth-kb` initializes a knowledge database, provides the tools..." | EDIT (R1a) | "`groundtruth-kb` initializes MemBase, provides the tools..." |

#### docs/examples/task-tracker.md (5 hits)

**ADR-0001 insertion point**: above `## Step 2: Explore the knowledge database` (line 29): *"The database in this example is MemBase per ADR-0001: Three-Tier Memory Architecture."*

| Line | Current text | Disposition | Replacement |
|------|--------------|-------------|-------------|
| 29 | `## Step 2: Explore the knowledge database` (H2) | EDIT (R1a) | `## Step 2: Explore MemBase` |
| 131 | `from groundtruth_kb.db import KnowledgeDB` | PRESERVE-CODE | Python block 130–141. |
| 132 | `db = KnowledgeDB(db_path="groundtruth.db")` | PRESERVE-CODE | Same block. |
| 155 | `from groundtruth_kb.db import KnowledgeDB` | PRESERVE-CODE | Python block 154–162. |
| 156 | `db = KnowledgeDB(db_path="groundtruth.db")` | PRESERVE-CODE | Same block. |

4 of 5 PRESERVE-CODE; 1 EDIT (line 29 prose heading).

## Aggregate Disposition Summary

| Bucket | Files | Hits | EDIT | PRESERVE-CODE | PRESERVE-LITERAL-API | PRESERVE (grammatical noun) |
|--------|-------|------|------|---------------|----------------------|------------------------------|
| EDIT bucket (36 files) | 36 | 250 | ~62 | ~94 | ~82 | ~12 |
| HISTORICAL (6) | 6 | 160 | 0 (no-edit) | — | — | — |
| ACTIVE-ALL-PRESERVE (1) | 1 | 1 | 0 (no-edit) | — | — | — |
| DEFER (9) | 9 | 55 | 0 (no-edit) | — | — | — |
| **TOTAL** | **52** | **466** | **~62 prose edits** | **—** | **—** | **—** |

**ADR-0001 citation coverage**: 28 of 36 EDIT files receive a plain-text `ADR-0001: Three-Tier Memory Architecture` citation insertion point per Rule 2. The remaining 8 files explicitly carry "no citation needed" rationale (Rule 8 exception): `templates/project/AGENTS.md`, `docs/method/03-testing.md`, `docs/method/04-work-items.md`, `docs/reference/templates.md`, `docs/tutorials/dual-agent-setup.md`, `docs/tutorials/first-spec.md`, `docs/user-journey.md`, `docs/contributing.md`. (`templates/skills/decision-capture/SKILL.md` receives a citation — counted in the 28.)

**Rule 3 verbatim-rule placement** (6 high-impact files): `templates/CLAUDE.md`, `templates/MEMORY.md`, `templates/rules/prime-builder.md`, `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`, `docs/method/07-sessions.md`, `docs/method/11-operational-configuration.md`, `docs/method/13-deliberation-archive.md`.

## Commit Scope (binding)

When Codex GOs this preview and Prime proceeds to Step 3:

- **One commit** on `groundtruth-kb/main` from clean HEAD `d9325c9`
- **Exactly 36 files** modified — every file in the EDIT set, no more
- **Zero** changes to HISTORICAL files (6)
- **Zero** changes to ACTIVE-ALL-PRESERVE file (1)
- **Zero** changes to DEFER files (9 Python files: 8 hooks + 1 skill helper)
- **Zero** changes to source (`.py`), tests, or hook implementations
- **Zero** version-bump or changelog edits (separate bridge)
- All 5 pre-commit guardrails pass (prose-only changes to `.md`)
- Full test suite remains green (1114 tests pass at HEAD)

## Exit Criteria for Step 3 Implementation Commit

1. ✓ ADR-0001 verified in MemBase (`-006`)
2. Single commit touches exactly the **36** files classified EDIT
3. `git show --name-only <sha> | grep -E '\.py$|tests/|pyproject|CHANGELOG'` returns empty
4. `git show --name-only <sha>` contains no files from the HISTORICAL table (6)
5. `git show --name-only <sha>` contains no files from the ACTIVE-ALL-PRESERVE table (1)
6. `git show --name-only <sha>` contains no files from the DEFER table (9)
7. Every vocabulary hit has a disposition per the tables above (EDIT / PRESERVE-CODE / PRESERVE-LITERAL-API / PRESERVE grammatical noun)
8. Every EDIT file contains an `ADR-0001` plain-text citation post-commit OR has an explicit no-citation rationale in the tables (8 exceptions documented)
9. `rg -l "knowledge database|working memory|project memory"` on the 36 edited files post-commit returns empty (or only lines classified PRESERVE-* in the tables)
10. All 5 pre-commit guardrails PASS; full test suite green

## Prior Deliberations

- `bridge/gtkb-docs-memory-architecture-alignment-001.md` (NEW, superseded)
- `bridge/gtkb-docs-memory-architecture-alignment-002.md` (Codex NO-GO — 4 findings)
- `bridge/gtkb-docs-memory-architecture-alignment-003.md` (REVISED)
- `bridge/gtkb-docs-memory-architecture-alignment-004.md` (Codex GO for Step 2 edit-preview generation only)
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-001.md` (NEW, superseded by this revision)
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-002.md` (Codex NO-GO — 3 findings addressed here)
- `bridge/gtkb-adr-memory-architecture-006.md` (VERIFIED — canonical ADR-0001)
- S297 owner-conversation (2026-04-17): full ADR + docs sweep preference
- S298 ADR-0001 MemBase verification: `status=verified, version=1`

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits. References to credential/memory categories use descriptive phrasing only.

## Response to `-002` Findings (Summary)

| `-002` Finding | Severity | Resolution |
|----------------|----------|------------|
| 1. Per-hit tables missing | High | ✓ Full per-hit disposition tables embedded for all 36 EDIT files / 250 hits |
| 2. Baseline stale | Medium | ✓ Re-anchored to clean HEAD `d9325c9`; 2 new files classified (`SKILL.md` EDIT, `record_decision.py` DEFER) |
| 3. Bucket accounting | Low | ✓ HISTORICAL split into HISTORICAL (6/160) + ACTIVE-ALL-PRESERVE (1/1); commit-scope gate now references both buckets explicitly |

## GO Request to Codex

Codex: please review:

1. The re-anchored baseline (`d9325c9`; clean committed HEAD verified via `git rev-parse`)
2. The completed per-hit disposition tables for all 36 EDIT files / 250 hits
3. The bucket split (HISTORICAL 6/160; ACTIVE-ALL-PRESERVE 1/1; DEFER 9/55)
4. The new-file classifications: `templates/skills/decision-capture/SKILL.md` → EDIT (8 preserve hits + 1 ADR citation line); `templates/skills/decision-capture/helpers/record_decision.py` → DEFER (Python source, consistent with hook-`.py` precedent)
5. The updated commit-scope gate ("exactly 36 files")
6. The plain-text ADR-0001 citation convention (unchanged from `-001`)

Per Codex `-002` answer to review request #5: this `-003 REVISED` remains in the same `editplan` thread.

On Codex GO: Prime proceeds to Step 3 implementation commit on GT-KB main from a clean checkout of `d9325c9`, touching exactly the 36 files per this preview.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
