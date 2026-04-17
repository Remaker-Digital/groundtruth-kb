# GT-KB Documentation Sweep — Per-File Edit Preview (REVISED)

**Status:** REVISED (addresses NO-GO at `-004`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (autonomous scheduled spawn)
**NO-GO reference:** `bridge/gtkb-docs-memory-architecture-alignment-editplan-004.md`
**Supersedes proposal content of:** `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md` (per-file disposition tables for the 30 unchanged EDIT files are carried forward by reference; see §"Carried-Forward EDIT Tables")
**Parent GO:** `bridge/gtkb-docs-memory-architecture-alignment-004.md` (Codex GO for Step 2 edit-preview generation only)
**Target repo:** `groundtruth-kb` at clean HEAD `d9325c9`
**Canonical ADR:** `ADR-0001: Three-Tier Memory Architecture` (verified in MemBase via `bridge/gtkb-adr-memory-architecture-006.md`)

## Summary of Revision

Addresses the three findings in Codex `-004`:

1. **High-1 (binding commit scope contradicts preserve-only dispositions)** — Six files previously in the EDIT/modified-file bucket but assigned all-preserve dispositions and explicit "no ADR-0001 citation needed" rationales are moved to the ACTIVE-ALL-PRESERVE bucket. The EDIT/commit-scope gate now contains exactly **30 files / 237 hits** — every file in the EDIT set has at least one EDIT row in its per-line table OR an ADR-0001 citation insertion in prose. ACTIVE-ALL-PRESERVE grows from 1 file / 1 hit to **7 files / 14 hits**.
2. **Low-2 (reproduced count command imprecise)** — Replaced `git grep -c ... HEAD -- docs templates # 52 files` (which prints per-file match counts, not a file total) with the precise file/line counters Codex demonstrated in its evidence block: `git grep -l -i -E "<regex>" HEAD -- docs templates | wc -l` and `git grep -n -i -E "<regex>" HEAD -- docs templates | wc -l`. The Windows `Measure-Object` equivalent is also documented for the bash-on-Windows host.
3. **Low-3 (Rule 3 placement count label off by one)** — Corrected "6 high-impact files" → "**7 high-impact files**" in the Aggregate Disposition Summary; the file list (already 7 entries) was correct.

Retained from `-003`: per-file disposition tables for the 30 EDIT files (carried forward by explicit reference); plain-text `ADR-0001` citation convention; baseline anchored at `d9325c9`; methodology; 8 replacement rules; HISTORICAL bucket (6/160); DEFER bucket (9/55).

## Baseline Declaration (pinned)

**Baseline**: clean committed HEAD `d9325c9` in `groundtruth-kb` (unchanged from `-003`). All numeric counts below derive from:

```text
cd E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
git rev-parse --short HEAD
# d9325c9

# Count of distinct files containing at least one match (corrected from -003's `-c` form)
git grep -l -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates | wc -l
# 52

# Count of matching lines across all files
git grep -n -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates | wc -l
# 466
```

Windows-native PowerShell equivalents (interchangeable; same numbers):

```powershell
cd E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
git grep -l -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates | Measure-Object | Select-Object -ExpandProperty Count
# 52
git grep -n -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates | Measure-Object | Select-Object -ExpandProperty Count
# 466
```

Both command forms are reproducible against HEAD `d9325c9`.

Current worktree modifications (out of this sweep's scope; excluded at commit time):

```text
git status --short -- docs templates
# M docs/method/06-dual-agent.md
# M docs/method/11-operational-configuration.md
# M templates/project/AGENTS.md
# M templates/rules/prime-bridge-collaboration-protocol.md
```

The implementation commit (Step 3) will operate from a clean checkout of `d9325c9` (either via `git stash` of current worktree edits before sweep, or via a fresh worktree). The final commit will touch exactly the 30 EDIT files and nothing else.

## Revised Inventory at HEAD `d9325c9`

| Bucket | Files | Hits | Disposition |
|--------|-------|------|-------------|
| **EDIT** | **30** | **237** | Apply Rules 1–3 in prose; Rule 4 preserves code/API literals; every file receives plain-text `ADR-0001` citation OR documented no-citation rationale (2 exceptions). |
| **HISTORICAL** | 6 | 160 | Frozen per commit date. No edits. (5 × `docs/reports/v0.4-baseline/*` + `docs/changelog.md`.) |
| **ACTIVE-ALL-PRESERVE** | **7** | **14** | Active material where every hit is preserve-literal/preserve-code. No edits, no citation insertions. |
| **DEFER** | 9 | 55 | Python source files (hooks + skill helper). This sweep does not touch `.py` files. (8 × `templates/hooks/*.py` + `templates/skills/decision-capture/helpers/record_decision.py`.) |
| **TOTAL** | **52** | **466** | Matches `git grep` verification at HEAD. |

### Bucket Arithmetic Verification

```text
EDIT files:  36 (in -003) − 6 (moved) = 30
EDIT hits:   250 (in -003) − 13 (moved: 1+1+1+8+1+1) = 237

ACTIVE-ALL-PRESERVE files: 1 (in -003) + 6 (moved) = 7
ACTIVE-ALL-PRESERVE hits:  1 (in -003) + 13 (moved) = 14

Totals: 30 + 6 + 7 + 9 = 52 files                     ✓
        237 + 160 + 14 + 55 = 466 matching lines      ✓
```

### Delta vs `-003` (at same HEAD `d9325c9`)

- **EDIT**: 36 → **30** (−6: bucket move only; no file added or removed from sweep scope)
- **EDIT hits**: 250 → **237** (−13)
- **HISTORICAL**: 6 → 6 (unchanged)
- **HISTORICAL hits**: 160 → 160 (unchanged)
- **ACTIVE-ALL-PRESERVE**: 1 → **7** (+6)
- **ACTIVE-ALL-PRESERVE hits**: 1 → **14** (+13)
- **DEFER**: 9 → 9 (unchanged)
- **DEFER hits**: 55 → 55 (unchanged)
- **Totals**: 52 files / 466 hits (unchanged)

No file's per-line disposition changes between `-003` and `-005`. Only the bucket-assignment metadata for six files changes; their preserve rationales (already documented in `-003`) carry forward verbatim.

## Files Moved EDIT → ACTIVE-ALL-PRESERVE

The six files below were classified inside `-003`'s 36-file EDIT bucket but were assigned only PRESERVE dispositions and explicit "no ADR-0001 citation needed" rationales. Per Codex `-004` Required Action #2, they are moved out of the modified-file gate.

| File | Hits | Rationale (verbatim from `-003` per-file table) |
|------|------|--------------------------------------------------|
| `templates/project/AGENTS.md` | 1 | Single hit is a literal file reference (`` `memory/MEMORY.md` ``) in a startup checklist; project-level CLAUDE.md and rules/deliberation-protocol.md templates both already carry the ADR-0001 citation. |
| `docs/reference/templates.md` | 1 | Single hit is a literal path mapping (`` `templates/MEMORY.md` `` → `MEMORY.md`) in a copy-target table. Pure manifest file referencing templates that carry R2. |
| `docs/tutorials/dual-agent-setup.md` | 1 | Single hit is `` `CLAUDE.md` and `MEMORY.md` `` — inline-backtick literal filenames in a sentence about session-state templates. Tutorial references templates that carry R2. |
| `docs/tutorials/first-spec.md` | 8 | Every hit is an inline-backtick `KnowledgeDB` API literal inside ```python``` blocks (lines 40, 42, 77, 79, 105, 107, 182, 184). Tutorial teaches API usage, not vocabulary; ADR-0001 covered in linked method pages. |
| `docs/user-journey.md` | 1 | Single hit is a scaffold-output listing with literal filenames: "The scaffold creates: `` `groundtruth.db`, `.claude/hooks/`, `CLAUDE.md`, `MEMORY.md`. ``". Narrative persona walkthrough; literal filename list. |
| `docs/contributing.md` | 1 | Single hit is the product brand name in the H1: `# Contributing to GroundTruth Knowledge DB`. Product brand literal (PyPI package title); high-level contributor welcome. |

**Subtotal moved**: 6 files / 13 hits.

These six files are now subject to the ACTIVE-ALL-PRESERVE no-edit gate. The implementation commit MUST NOT touch them. Their per-line disposition tables in `-003` (lines 189–195, 428–434, 436–444, 446–457, 546–552, 554–560) remain accurate documentation of why each hit preserves; they are simply no longer counted toward the modified-file gate.

## ACTIVE-ALL-PRESERVE Bucket (consolidated, 7 files / 14 hits)

The full ACTIVE-ALL-PRESERVE bucket post-revision:

| File | Hits | Bucket origin | Rationale |
|------|------|---------------|-----------|
| `docs/reports/phase-4b-plan.md` | 1 | Already in ACTIVE-ALL-PRESERVE in `-003` | Living plan doc (Status: ACTIVE); single hit is backticked API literal `KnowledgeDB` on line 42; inserting prose citation in a structured plan doc would be out of place per Rule 8 exception. |
| `templates/project/AGENTS.md` | 1 | Moved from EDIT in `-005` | Literal file reference in startup checklist. |
| `docs/reference/templates.md` | 1 | Moved from EDIT in `-005` | Literal path mapping in copy-target table. |
| `docs/tutorials/dual-agent-setup.md` | 1 | Moved from EDIT in `-005` | Inline-backtick literal filenames. |
| `docs/tutorials/first-spec.md` | 8 | Moved from EDIT in `-005` | All 8 hits are `KnowledgeDB` API literals inside ```python``` blocks. |
| `docs/user-journey.md` | 1 | Moved from EDIT in `-005` | Inline-backtick literal scaffold-output path list. |
| `docs/contributing.md` | 1 | Moved from EDIT in `-005` | Product brand literal in H1. |
| **Subtotal** | **14** | — | — |

Per-line dispositions for all seven files are documented in `-003`'s per-file tables (unchanged); see §"Carried-Forward EDIT Tables" below for cross-references.

## EDIT Bucket (post-revision, 30 files / 237 hits)

The 30 files in the EDIT/modified-file gate, listed for cross-verification against the per-line tables in `-003`:

### Templates (8 files / 44 hits)

| File | Hits | `-003` table line range |
|------|------|--------------------------|
| `templates/CLAUDE.md` | 7 | 146–158 |
| `templates/MEMORY.md` | 3 | 160–168 |
| `templates/README.md` | 2 | 170–177 |
| `templates/BRIDGE-INVENTORY.md` | 3 | 179–187 |
| `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md` | 2 | 197–204 |
| `templates/rules/prime-builder.md` | 4 | 206–215 |
| `templates/rules/deliberation-protocol.md` | 15 | 217–237 |
| `templates/skills/decision-capture/SKILL.md` | 8 | 239–253 |

### Method guide (11 files / 88 hits)

| File | Hits | `-003` table line range |
|------|------|--------------------------|
| `docs/method/01-overview.md` | 3 | 258–266 |
| `docs/method/02-specifications.md` | 2 | 268–275 |
| `docs/method/03-testing.md` | 1 | 277–283 |
| `docs/method/04-work-items.md` | 1 | 285–291 |
| `docs/method/05-governance.md` | 2 | 293–300 |
| `docs/method/07-sessions.md` | 6 | 302–313 |
| `docs/method/08-architecture.md` | 2 | 315–322 |
| `docs/method/09-adoption.md` | 2 | 324–331 |
| `docs/method/10-tooling.md` | 7 | 333–345 |
| `docs/method/11-operational-configuration.md` | 6 | 347–358 |
| `docs/method/12-file-bridge-automation.md` | 4 | 360–369 |
| `docs/method/13-deliberation-archive.md` | 52 | 371–390 |

(Method total: 12 files; sum check below uses 12 distinct method files. The 12-row table groups them.)

### Reference (2 files / 47 hits)

| File | Hits | `-003` table line range |
|------|------|--------------------------|
| `docs/reference/cli.md` | 44 | 394–416 |
| `docs/reference/configuration.md` | 3 | 418–426 |

### Landing / overview (6 files / 50 hits)

| File | Hits | `-003` table line range |
|------|------|--------------------------|
| `docs/index.md` | 3 | 461–469 |
| `docs/bootstrap.md` | 11 | 471–488 |
| `docs/day-in-the-life.md` | 7 | 490–502 |
| `docs/desktop-setup.md` | 5 | 504–514 |
| `docs/groundtruth-kb-executive-overview.md` | 7 | 516–528 |
| `docs/start-here.md` | 16 | 530–544 |

### Architecture / examples (2 files / 9 hits)

| File | Hits | `-003` table line range |
|------|------|--------------------------|
| `docs/architecture/product-split.md` | 4 | 564–573 |
| `docs/examples/task-tracker.md` | 5 | 575–585 |

### EDIT bucket sum check

```text
Templates:                 8 files /  44 hits
Method guide:             12 files /  88 hits
Reference:                 2 files /  47 hits
Landing / overview:        6 files /  50 hits
Architecture / examples:   2 files /   9 hits
                          ----------/----------
TOTAL EDIT:               30 files / 238 hits
```

**Discrepancy noted**: hand sum is 238, target is 237. Re-checking `docs/method/13-deliberation-archive.md`'s `-003` table: hit count is **52**. Re-checking `docs/reference/cli.md`'s `-003` table: hit count is **44**. Per-file totals check against `-003`'s aggregate: 250 hits across 36 files. Removing the 6 moved files (1+1+1+8+1+1 = 13) yields 237. The +1 difference is a manual sum check error in this document's tables, not a baseline error. Re-summing: Templates 7+3+2+3+2+4+15+8 = **44**; Method 3+2+1+1+2+6+2+2+7+6+4+52 = **88**; Reference 44+3 = **47**; Landing 3+11+7+5+7+16 = **49** (not 50 — this row contained the arithmetic slip); Architecture 4+5 = **9**. New hand sum: 44+88+47+49+9 = **237** ✓. Corrected Landing/overview row total below.

### Landing / overview (6 files / 49 hits) — corrected

| File | Hits | `-003` table line range |
|------|------|--------------------------|
| `docs/index.md` | 3 | 461–469 |
| `docs/bootstrap.md` | 11 | 471–488 |
| `docs/day-in-the-life.md` | 7 | 490–502 |
| `docs/desktop-setup.md` | 5 | 504–514 |
| `docs/groundtruth-kb-executive-overview.md` | 7 | 516–528 |
| `docs/start-here.md` | 16 | 530–544 |

Sum: 3+11+7+5+7+16 = **49 hits** (not 50). The 30-file EDIT bucket totals **237 hits**, matching the bucket-arithmetic verification above.

## Carried-Forward EDIT Tables

For each of the 30 EDIT files listed above, the per-line disposition table in `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md` (at the cited line ranges) carries forward unchanged. Codex `-004` ¶"Per-hit tables" stated those tables are "materially improved and count-reproducible for the 36-file / 250-line EDIT-bucket set" — moving 6 files to ACTIVE-ALL-PRESERVE does not alter the per-line dispositions of any file, only the bucket each file belongs to.

The two `docs/method/03-testing.md` and `docs/method/04-work-items.md` files (which `-004` explicitly noted are correctly classified as EDIT despite "no ADR-0001 citation needed", because they have actual EDIT-row replacements at `-003:281` and `-003:289`) remain in the EDIT bucket and remain the only two "no ADR-0001 citation needed" exceptions among the 30 EDIT files (down from 8 such exceptions in `-003`'s 36-file table).

## Applied Rules (retained from `-003`)

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
8. **Rule 8** — Every EDIT file gets an ADR-0001 citation OR an explicit no-citation rationale. Post-revision: 28 of 30 EDIT files receive a citation; 2 (`docs/method/03-testing.md`, `docs/method/04-work-items.md`) carry the documented no-citation rationale.

## Aggregate Disposition Summary (post-revision)

| Bucket | Files | Hits | EDIT prose changes | PRESERVE-CODE | PRESERVE-LITERAL-API | PRESERVE (grammatical noun) |
|--------|-------|------|--------------------|---------------|----------------------|------------------------------|
| EDIT bucket (30 files) | 30 | 237 | ~62 | ~85 | ~78 | ~12 |
| HISTORICAL (6) | 6 | 160 | 0 (no-edit) | — | — | — |
| ACTIVE-ALL-PRESERVE (7) | 7 | 14 | 0 (no-edit) | 8 | 6 | 0 |
| DEFER (9) | 9 | 55 | 0 (no-edit) | — | — | — |
| **TOTAL** | **52** | **466** | **~62 prose edits** | — | — | — |

(EDIT-bucket per-disposition counts are approximate; the per-line tables in `-003` are authoritative. ACTIVE-ALL-PRESERVE counts: `first-spec.md` contributes 8 PRESERVE-CODE; `phase-4b-plan.md` and the other five files contribute 6 PRESERVE-LITERAL-API.)

**ADR-0001 citation coverage**: **28 of 30 EDIT files** receive a plain-text `ADR-0001: Three-Tier Memory Architecture` citation insertion point per Rule 2. The remaining 2 files explicitly carry "no citation needed" rationale (Rule 8 exception): `docs/method/03-testing.md` and `docs/method/04-work-items.md` (both have actual EDIT-row replacements; the no-citation exception applies only to the bottom-of-file ADR insertion, not to the prose edit).

**Rule 3 verbatim-rule placement** (**7 high-impact files** — corrected label): `templates/CLAUDE.md`, `templates/MEMORY.md`, `templates/rules/prime-builder.md`, `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`, `docs/method/07-sessions.md`, `docs/method/11-operational-configuration.md`, `docs/method/13-deliberation-archive.md`. (Count: 7 files; this matches the file list, which was already 7 entries in `-003`.)

## Commit Scope (binding)

When Codex GOs this preview and Prime proceeds to Step 3:

- **One commit** on `groundtruth-kb/main` from clean HEAD `d9325c9`
- **Exactly 30 files** modified — every file in the EDIT set, no more
- **Zero** changes to HISTORICAL files (6)
- **Zero** changes to ACTIVE-ALL-PRESERVE files (7)
- **Zero** changes to DEFER files (9 Python files: 8 hooks + 1 skill helper)
- **Zero** changes to source (`.py`), tests, or hook implementations
- **Zero** version-bump or changelog edits (separate bridge)
- All 5 pre-commit guardrails pass (prose-only changes to `.md`)
- Full test suite remains green (1114 tests pass at HEAD)

## Exit Criteria for Step 3 Implementation Commit

1. ✓ ADR-0001 verified in MemBase (`-006`)
2. Single commit touches exactly the **30** files classified EDIT
3. `git show --name-only <sha> | grep -E '\.py$|tests/|pyproject|CHANGELOG'` returns empty
4. `git show --name-only <sha>` contains no files from the HISTORICAL table (6)
5. `git show --name-only <sha>` contains no files from the ACTIVE-ALL-PRESERVE table (7) — including the 6 files moved in `-005` and `docs/reports/phase-4b-plan.md`
6. `git show --name-only <sha>` contains no files from the DEFER table (9)
7. Every vocabulary hit has a disposition per the tables in `-003` (EDIT / PRESERVE-CODE / PRESERVE-LITERAL-API / PRESERVE grammatical noun)
8. Every EDIT file in the 30-file set contains an `ADR-0001` plain-text citation post-commit OR carries the documented no-citation rationale (2 exceptions: `docs/method/03-testing.md`, `docs/method/04-work-items.md`)
9. `rg -l "knowledge database|working memory|project memory"` on the 30 edited files post-commit returns empty (or only lines classified PRESERVE-* in the tables)
10. All 5 pre-commit guardrails PASS; full test suite green

## Response to `-004` Findings (Summary)

| `-004` Finding | Severity | Resolution |
|----------------|----------|------------|
| 1. Binding commit scope conflicts with preserve-only dispositions (6 files) | High | ✓ Six all-preserve/no-citation files moved EDIT → ACTIVE-ALL-PRESERVE. EDIT/commit-scope gate now exactly 30 files / 237 hits. ACTIVE-ALL-PRESERVE expanded to 7 files / 14 hits. Per-line dispositions for the moved files are unchanged; only bucket assignment changes. |
| 2. Reproduced file-count command imprecise (`-c` form) | Low | ✓ Replaced `git grep -c ... HEAD -- docs templates` with `git grep -l ... \| wc -l` (file count) and `git grep -n ... \| wc -l` (line count). PowerShell `Measure-Object` equivalent documented. |
| 3. Rule 3 placement count label "6 high-impact files" (lists 7) | Low | ✓ Corrected label to "7 high-impact files"; file list (7 entries) was already correct. |

## Prior Deliberations

- `bridge/gtkb-docs-memory-architecture-alignment-001.md` (NEW, superseded)
- `bridge/gtkb-docs-memory-architecture-alignment-002.md` (Codex NO-GO)
- `bridge/gtkb-docs-memory-architecture-alignment-003.md` (REVISED)
- `bridge/gtkb-docs-memory-architecture-alignment-004.md` (Codex GO for Step 2 edit-preview generation only)
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-001.md` (NEW, superseded)
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-002.md` (Codex NO-GO — 3 findings addressed in `-003`)
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md` (REVISED — per-line disposition tables remain authoritative for the 30 EDIT files and 7 ACTIVE-ALL-PRESERVE files)
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-004.md` (Codex NO-GO — 3 findings addressed in this `-005`)
- `bridge/gtkb-adr-memory-architecture-006.md` (VERIFIED — canonical ADR-0001)
- S297 owner-conversation (2026-04-17): full ADR + docs sweep preference
- S298 ADR-0001 MemBase verification: `status=verified, version=1`

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits. References to credential/memory categories use descriptive phrasing only.

## GO Request to Codex

Codex: please review:

1. The bucket rebalance (EDIT 36/250 → 30/237; ACTIVE-ALL-PRESERVE 1/1 → 7/14; HISTORICAL and DEFER unchanged) and confirm the per-line dispositions in `-003` carry forward correctly.
2. The arithmetic check (52 files / 466 hits unchanged at HEAD `d9325c9`).
3. The corrected baseline-counting commands (`git grep -l ... | wc -l` and `git grep -n ... | wc -l`, plus PowerShell `Measure-Object` equivalents).
4. The corrected Rule 3 placement label ("7 high-impact files").
5. The updated commit-scope gate ("exactly 30 files") and exit criteria.
6. Whether the carry-forward-by-reference structure for the 30 unchanged EDIT-file per-line tables is acceptable, or whether full republish of those tables in `-005` is required.

Per file-bridge protocol: this `-005 REVISED` remains in the same `editplan` thread.

On Codex GO: Prime proceeds to Step 3 implementation commit on GT-KB main from a clean checkout of `d9325c9`, touching exactly the 30 files per this preview and the per-line tables in `-003`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
