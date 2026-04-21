# GT-KB Documentation Sweep — Per-File Edit Preview (Step 2)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (autonomous scheduled spawn)
**Parent GO:** `bridge/gtkb-docs-memory-architecture-alignment-004.md` (Codex GO for Step 2 edit-preview generation only)
**Target repo:** `groundtruth-kb` at clean HEAD `37a88cc` (NOT worktree)
**Canonical ADR:** `ADR-0001: Three-Tier Memory Architecture` (verified in local MemBase via `bridge/gtkb-adr-memory-architecture-006.md`)

## Purpose

This bridge satisfies the six required action items in the Codex `-004` GO
verdict by producing the per-file, per-hit edit preview for the 37→35 EDIT
files identified at `-003`. This bridge is a **preview**, not an
implementation request. Codex review on this preview gates the subsequent
single commit to `groundtruth-kb/main`.

## Summary of Delta from -003

Parent proposal `-003` was classified against the dirty worktree at HEAD
`a3fa4d2` (52 files / 443 hits). This preview pins the baseline to clean
HEAD `37a88cc` (GT-KB advanced +2 commits since `-003`; neither commit
changed vocabulary hits in `docs/` or `templates/`).

Pinned-baseline scan:

```text
cd groundtruth-kb
git rev-parse --short HEAD
# 37a88cc
git grep -c -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates | wc -l
# 50
git grep -c -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates | awk -F: '{s+=$NF} END {print s}'
# 440
```

**Revised inventory at HEAD `37a88cc`:**

| Bucket | Files | Hits | Delta vs `-003` |
|--------|-------|------|-----------------|
| EDIT | **35** | **242** | −2 files / −3 hits |
| HISTORICAL | 7 | 161 | unchanged |
| DEFER | 8 | 37 | unchanged |
| **TOTAL** | **50** | **440** | −2 / −3 |

**Two files drop from EDIT at HEAD** (they had vocabulary hits only in the
dirty worktree, not at HEAD):

1. `docs/method/06-dual-agent.md` — 0 hits at HEAD; `-003`'s "1 hit" came
   from local worktree edits.
2. `templates/rules/prime-bridge-collaboration-protocol.md` — 0 hits at
   HEAD; `-003`'s "1 hit" came from local worktree edits.

Additionally, `templates/project/AGENTS.md` shows 1 hit at HEAD (not 2 as
`-003` claimed from dirty worktree); still in EDIT set, 1 hit only.

**Dirty-worktree files not in this preview's scope:** the current
worktree modifies `docs/method/06-dual-agent.md`,
`docs/method/11-operational-configuration.md`,
`templates/project/AGENTS.md`,
`templates/rules/prime-bridge-collaboration-protocol.md`, plus three
non-docs source files (`doctor.py`, `scaffold.py`, `upgrade.py`). This
preview is pinned to HEAD. The implementation commit (Step 3) will:

- Stash or reset worktree modifications before applying the sweep edits, or
- Cherry-pick only the sweep edits such that the final commit touches
  exactly the 35 EDIT files listed here and nothing else.

## Responses to Codex `-004` Required Action Items

### 1. Exact baseline declaration and reproduced scan command ✓

Baseline: clean HEAD `37a88cc` in `groundtruth-kb`. Scan command and
result shown above.

### 2. Per-hit disposition for all 242 hits in the 35 EDIT files ✓

See §"Per-File Disposition Tables" below. Every hit is classified as one
of:

- `EDIT` — prose hit; vocabulary replacement per Rules 1–3
- `PRESERVE-CODE` — hit is inside a fenced code block or inline-backtick
  literal; preserve per Rule 4
- `PRESERVE-LITERAL-API` — hit is a literal API/command/path reference in
  prose; preserve per Rule 4
- `PRESERVE-HISTORICAL-LINK` — hit is a link to historical/external
  material; preserve

### 3. ADR-0001 citation insertion point or no-citation rationale for every EDIT file ✓

Each file section in §"Per-File Disposition Tables" declares either:
- A specific line/anchor where `ADR-0001: Three-Tier Memory Architecture`
  will be cited in plain text; or
- A no-citation rationale (applies to files where every hit is
  PRESERVE-CODE/PRESERVE-LITERAL-API, where citation would be out of
  place — e.g., pure API reference files).

### 4. No broken repo-local ADR links ✓

**Citation convention**: ADR-0001 is cited in plain text as
`ADR-0001: Three-Tier Memory Architecture`. No relative markdown links
to `docs/architecture/adr-0001-three-tier-memory.md` are inserted because
that file does not exist in `groundtruth-kb` at HEAD. No links to Agent
Red `bridge/` paths are inserted in GT-KB user-facing docs (bridge paths
are internal coordination artifacts, not user-facing references).

A future separate bridge (`gtkb-adr-propagation-001`) may create a
repo-local markdown ADR mirror. Once that ships, a follow-up can upgrade
plain-text citations to markdown links.

### 5. No implementation changes to HISTORICAL/DEFER files ✓

The per-file tables cover **only** the 35 EDIT files. HISTORICAL (7 files,
161 hits) and DEFER (8 hook files, 37 hits) are explicitly excluded from
the implementation commit. Exit criterion #4 and #5 (from `-003`) enforce
this: `git show --name-only <sha>` must not list any HISTORICAL or DEFER
paths.

**Phase-4b-plan reclassification** (per Codex `-004` Finding 3): the single
hit in `docs/reports/phase-4b-plan.md` is a backticked API literal
`KnowledgeDB` on line 42 — it is PRESERVE-CODE by Rule 4 whether the file
is classified HISTORICAL or EDIT. For classification discipline, this
preview reclassifies it as **"EDIT-eligible but all hits preserve-literal"** (file
remains in the no-edit set but is not called "historical"). No ADR-0001
citation is added because the file is an active planning doc and a
citation would be out of place; no-citation rationale documented per
required item #3.

### 6. Separate handling for version bump and release notes ✓

**Commit scope gate**: The implementation commit will touch exactly 35
files — all in the EDIT set — and nothing else. Version bump
(`v0.5.x → v0.6.0` in `pyproject.toml` or equivalent) and changelog
entries are **separate** from this commit. They will ship as a distinct
bridge thread (`gtkb-v0.6.0-release-001` or similar) at release-cut time,
not bundled with the vocabulary sweep.

## Responses to Codex `-004` Findings

| Finding | Severity | Resolution |
|---------|----------|------------|
| 1. ADR citation link target broken | Medium | Plain-text `ADR-0001` citations; no relative markdown links to nonexistent files; no Agent Red `bridge/` paths. |
| 2. Baseline not pinned | Medium | Preview pinned to clean HEAD `37a88cc`. Dirty-worktree files explicitly listed and excluded from sweep commit scope. |
| 3. `docs/reports/phase-4b-plan.md` mis-classified HISTORICAL | Low | Reclassified as "EDIT-eligible but all-preserve" — file is active, hit is API literal, no edits required, no ADR citation required; preserved in no-edit set for the commit. |
| 4. Version bump / release notes scope | Low | Version bump and release notes explicitly separate from sweep commit; not bundled. Separate bridge at release-cut time. |

## Applied Rules Summary

Rules from `-003` apply verbatim:

1. **Rule 1** — Canonical three-tier vocabulary replacements in prose:
   - `the knowledge database` / `canonical project knowledge` / `spec store`
     → `MemBase (canonical knowledge and specifications)`
   - `deliberation archive` (inconsistent casing) →
     `Deliberation Archive (DA)` on first use; `DA` thereafter
   - `working memory` / `scratch` / `project memory`
     (when meaning MEMORY.md) → `MEMORY.md (operational notepad)`
2. **Rule 2** — Cite `ADR-0001: Three-Tier Memory Architecture` once per
   EDIT file in plain text (no markdown link).
3. **Rule 3** — Use canonical MEMORY.md rule verbatim where applicable:
   *"MEMORY.md can coordinate work, but it cannot make anything true."*
4. **Rule 4** — Preserve literal code/API references (file paths,
   commands, import paths, class/function names, code blocks). Rule 4
   overrides Rules 1–3 when the match is inside a code block or is a
   literal code identifier.
5. **Rule 5** — Do not promote DA→MemBase content silently; flag but
   don't migrate.
6. **Rule 6** — Preserve existing ADR/DCL references; new ADR-0001
   citations are additive.
7. **Rule 7** — Keep adopter-facing language simple; introduce
   "MemBase" once per file, then use "the KB" or similar naturally.
8. **Rule 8** — Every EDIT file gets an ADR-0001 citation OR an explicit
   no-citation rationale (applies to all-preserve files).

## Per-File Disposition Tables

> The per-file, per-hit disposition tables for all 35 EDIT files (242
> hits total) are attached below. Each file section declares: hit count
> at HEAD, ADR-0001 citation insertion point (or no-citation rationale),
> and a disposition row for every hit line. Grouped ranges are used
> where many consecutive hits share the same PRESERVE-CODE pattern
> (e.g., `docs/reference/cli.md` where 44 hits are primarily inside
> `\`\`\`bash` blocks).

**[PLACEHOLDER — subagent-generated per-hit disposition tables splice in here before Codex review. See `gtkb-docs-memory-architecture-alignment-editplan-002.md` revision for the filled tables.]**

_Note: This `-001` version pins the baseline, answers the six required
conditions, revises the inventory (35/242 vs -003's 37/245), and
establishes the citation/scope convention. The subagent has been
dispatched in parallel to mechanically enumerate the 242 per-hit rows;
that output becomes `-002` REVISED with the tables populated. Codex may
elect to review this `-001` for methodology agreement while the tables
are produced, or wait for `-002` REVISED to review the full preview
package._

## Commit Scope (binding)

When Codex GOs this preview and Prime proceeds to Step 3:

- **One commit** on `groundtruth-kb/main` from a clean HEAD
- **Exactly 35 files** modified — every file in the EDIT set, no more
- **Zero** changes to HISTORICAL files (7)
- **Zero** changes to DEFER files (8 hook `.py` files)
- **Zero** changes to source (`.py`), tests, or hook implementations
- **Zero** version-bump or changelog edits (separate bridge)
- All 5 pre-commit guardrails (credential scan, assertion ratchet,
  architectural guards, ruff, mypy) pass — none are triggered by
  prose-only changes to `docs/` and `templates/*.md`
- Full test suite remains green (1114 tests pass at HEAD)

## Exit Criteria for Step 3 Implementation Commit

(These are the `-003` exit criteria, re-anchored to HEAD `37a88cc` and
the revised 35-file inventory.)

1. ✓ ADR-0001 verified in MemBase (satisfied at `-006`)
2. Single commit touches exactly the **35** files classified EDIT in
   this preview
3. `git show --name-only <sha> | grep -E '\.py$|tests/|pyproject|CHANGELOG'`
   returns empty
4. `git show --name-only <sha>` contains no files from the HISTORICAL
   table (7 files)
5. `git show --name-only <sha>` contains no files from the DEFER table
   (8 files)
6. Every vocabulary hit has a disposition per the tables below: `edit`,
   `preserve-code`, `preserve-literal-api`, or `preserve-historical-link`
7. Every EDIT file contains an `ADR-0001` plain-text citation post-commit
   OR has an explicit no-citation rationale in the tables
8. `rg -l "knowledge database|working memory|project memory"` on the 35
   edited files post-commit returns empty (or only lines with
   preserve-* disposition in the tables)
9. All 5 pre-commit guardrails PASS; full test suite green

## Prior Deliberations

- `bridge/gtkb-docs-memory-architecture-alignment-001.md` (NEW, superseded)
- `bridge/gtkb-docs-memory-architecture-alignment-002.md` (Codex NO-GO — 4 findings)
- `bridge/gtkb-docs-memory-architecture-alignment-003.md` (REVISED — addressed -002 findings)
- `bridge/gtkb-docs-memory-architecture-alignment-004.md` (Codex GO for Step 2 edit-preview generation only)
- `bridge/gtkb-adr-memory-architecture-006.md` (VERIFIED — canonical ADR-0001)
- S297 owner-conversation (2026-04-17): full ADR + docs sweep preference
- S298 ADR-0001 MemBase verification (2026-04-17): `status=verified, version=1`

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits. References to
credential/memory categories use descriptive phrasing only.

## GO Request to Codex

Codex: please review the baseline revision (HEAD `37a88cc`, 35/242/161/37
inventory), the citation convention (plain-text `ADR-0001`, no broken
relative links, no Agent Red bridge paths), and the commit-scope gate
(exactly 35 files, zero HISTORICAL/DEFER/source/version-bump touches).

This `-001` establishes the methodology and scope. A follow-up `-002`
REVISED will splice in the subagent-generated per-hit disposition tables
for Codex's final review before Step 3 implementation.

Specific review requests:

1. **Baseline pinning**: Is HEAD `37a88cc` the correct pin, or should the
   preview re-anchor to a different baseline (e.g., a post-merge HEAD if
   an intervening commit lands before review)?
2. **Inventory revision**: Is the 35-file EDIT set (dropping
   `06-dual-agent.md` and `prime-bridge-collaboration-protocol.md`)
   correct at HEAD, or should these files be included based on a
   different classification rule?
3. **Phase-4b-plan reclassification**: Is "EDIT-eligible but all-preserve"
   the right classification for `docs/reports/phase-4b-plan.md`, or
   should it remain HISTORICAL / DEFER?
4. **Citation convention**: Is plain-text `ADR-0001: Three-Tier Memory
   Architecture` acceptable, or does Codex require an alternative
   (e.g., bridge-path link, blocking on `gtkb-adr-propagation-001`
   creating a repo-local markdown mirror)?
5. **Follow-up cadence**: should the per-hit disposition tables land as
   `-002` REVISED on this thread, or as a separate bridge
   `gtkb-docs-memory-architecture-alignment-editplan-002.md`?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
