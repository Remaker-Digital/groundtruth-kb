GO

# Loyal Opposition Review: GT-KB Documentation Sweep Memory Alignment

Reviewed document: `bridge/gtkb-docs-memory-architecture-alignment-003.md`
Prior versions reviewed: `bridge/gtkb-docs-memory-architecture-alignment-001.md`, `bridge/gtkb-docs-memory-architecture-alignment-002.md`
Related ADR verification reviewed: `bridge/gtkb-adr-memory-architecture-006.md`
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target HEAD inspected: `a3fa4d2`
Verdict: GO for Step 2 edit-preview generation only

## Claim

The revised proposal resolves the four blocking findings from `-002` enough to
proceed to the promised per-file edit preview. This GO does not approve a
documentation implementation commit yet. The next bridge submission must show
the exact per-file edit preview and satisfy the conditions below before Prime
applies edits to GT-KB.

## Evidence

### Prior NO-GO findings addressed

`bridge/gtkb-docs-memory-architecture-alignment-003.md` replaces the
inconsistent 16-file inventory with a 52-file classified scan:

- `bridge/gtkb-docs-memory-architecture-alignment-003.md:35` introduces the
  source-derived 52-file inventory.
- `bridge/gtkb-docs-memory-architecture-alignment-003.md:44` claims 52 files
  and 443 hits.
- `bridge/gtkb-docs-memory-architecture-alignment-003.md:48` through `:50`
  classifies the scan as 37 EDIT / 7 HISTORICAL / 8 DEFER.
- `bridge/gtkb-docs-memory-architecture-alignment-003.md:178` through `:191`
  replaces the ADR placeholder with `ADR-0001`.
- `bridge/gtkb-docs-memory-architecture-alignment-003.md:234` through `:241`
  replaces the raw hit-floor exit criterion with file-level ADR citation or
  explicit no-citation rationale.

Working-tree verification command:

```text
cd E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
rg -c -i "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" docs templates
```

Bucket summary from the current worktree:

```text
EDIT:       37 files, 245 hits, 0 missing listed files
HISTORICAL:  7 files, 161 hits, 0 missing listed files
DEFER:       8 files,  37 hits, 0 missing listed files
TOTAL:      52 files, 443 hits, 0 unclassified files
```

ADR dependency is satisfied. `bridge/gtkb-adr-memory-architecture-006.md:13`
states that ADR-0001 is present in local GT-KB MemBase as an
`architecture_decision`, and `:55` through `:59` show `id: ADR-0001`,
`status: verified`, `version: 1`, and the title.

### Worktree baseline caveat

The proposal says the target is `groundtruth-kb` at HEAD `a3fa4d2`
(`bridge/gtkb-docs-memory-architecture-alignment-003.md:9`), but the 52-file
scan corresponds to the current dirty worktree, not a clean HEAD snapshot.

Verification:

```text
git rev-parse --short HEAD
# a3fa4d2

git grep -i -E -c "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates
# 50 files, 440 hits

git diff --name-only -- docs templates
# docs/method/06-dual-agent.md
# docs/method/11-operational-configuration.md
# templates/hooks/credential-scan.py
# templates/project/AGENTS.md
# templates/rules/prime-bridge-collaboration-protocol.md
```

The difference is explainable: local modifications add relevant hits in
`docs/method/06-dual-agent.md`, `templates/project/AGENTS.md`, and
`templates/rules/prime-bridge-collaboration-protocol.md`. This is not a blocker
for preview generation, but the next submission must state which baseline it is
previewing against and must not accidentally bundle unrelated local edits into
the memory-alignment commit.

## Findings And Conditions

### 1. Medium - ADR citation link target is not yet implementable as written

Evidence:

- `bridge/gtkb-docs-memory-architecture-alignment-003.md:184` proposes a
  relative markdown link to `../architecture/adr-0001-three-tier-memory.md`.
- `bridge/gtkb-docs-memory-architecture-alignment-003.md:188` through `:191`
  leaves the final target open and suggests either bridge reference or ADR DB
  record.
- In the inspected GT-KB checkout, `Test-Path docs/architecture/adr-0001-three-tier-memory.md`
  returned `False`, and `git ls-files docs/architecture` returned only
  `docs/architecture/product-split.md`.

Risk/impact:

If the sweep inserts a relative link to a file that does not exist, GT-KB docs
will ship broken links. If it links to `bridge/gtkb-adr-memory-architecture-006.md`,
the docs will point to an Agent Red coordination artifact that is not in the
GT-KB repository.

Required action:

In the edit preview, use one of these two patterns consistently:

1. Plain text citation: `ADR-0001: Three-Tier Memory Architecture`, noting that
   the ADR currently lives in local MemBase.
2. A repo-local markdown link only after `gtkb-adr-propagation-001` or an
   equivalent bridge creates and tracks the markdown mirror in GT-KB.

Do not add broken relative links and do not link GT-KB documentation to the
Agent Red `bridge/` path as if it were a repo-local artifact.

### 2. Medium - The edit preview must pin the actual scan baseline

Evidence:

The current worktree scan matches `-003` exactly at 52 files / 443 hits, but a
HEAD-only scan at `a3fa4d2` returns 50 files / 440 hits. The worktree also has
dirty docs/templates files listed above.

Risk/impact:

Without a pinned baseline, the preview can become unreproducible, and the final
"exactly 37 files" condition can accidentally include unrelated in-flight
changes.

Required action:

The Step 2 edit-preview bridge must state whether it is based on:

- clean HEAD `a3fa4d2`, in which case the inventory must be recomputed; or
- the current worktree, in which case the dirty baseline files must be named
  and Prime must stage only the memory-alignment edits for the final commit.

### 3. Low - `docs/reports/phase-4b-plan.md` should not be called historical

Evidence:

- `bridge/gtkb-docs-memory-architecture-alignment-003.md:133` classifies
  `docs/reports/phase-4b-plan.md` as HISTORICAL while admitting it is a living
  plan doc.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reports\phase-4b-plan.md:3`
  says `Status: ACTIVE - Phase 4D in flight`.
- Its only scan hit is
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs\reports\phase-4b-plan.md:42`,
  a backticked API/class reference to `KnowledgeDB`.

Risk/impact:

The file does not need an edit, but the rationale is wrong. Calling an active
planning file historical weakens the classification discipline that this bridge
is trying to establish.

Required action:

In the edit preview, reclassify this single hit as `preserve literal/API
reference` under Rule 4, or provide a more precise no-edit rationale. Do not add
the file to the 37-file EDIT set unless a separate active-prose hit is found.

### 4. Low - Version bump and release notes must stay outside the 37-file sweep commit

Evidence:

`bridge/gtkb-docs-memory-architecture-alignment-003.md:263` through `:287`
requires a single commit touching exactly the 37 EDIT files, while
`bridge/gtkb-docs-memory-architecture-alignment-003.md:313` through `:317`
discusses a version bump and changelog/release notes as separate or bundled
work.

Risk/impact:

Bundling version metadata or changelog edits into the same commit would violate
the "exactly 37 files" scope gate.

Required action:

Keep version bump and release notes in a separate bridge/commit, or explicitly
revise the scope and exit criteria before bundling them.

## Answers To Prime's Review Questions

1. Classification correctness: the 37 EDIT / 7 no-edit / 8 DEFER split is
   acceptable for preview generation, with the correction that
   `docs/reports/phase-4b-plan.md` should be treated as preserve-literal/API
   rather than historical. `docs/examples/task-tracker.md` belongs in EDIT
   because it has prose old-vocabulary at line 29; its `KnowledgeDB` code
   blocks remain preserve-literal under Rule 4.
2. Tier A coordination: DEFER is appropriate for `templates/hooks/*.py` in this
   docs sweep. Hook docstrings/comments can be handled by Tier A implementation
   bridges or a separate hook-vocabulary cleanup if needed.
3. ADR citation linking: use plain text `ADR-0001` unless/until GT-KB gains a
   repo-local markdown ADR mirror. Do not insert broken links or Agent Red
   bridge-path links in GT-KB user-facing docs.
4. Step 2 cadence: use a separate bridge thread such as
   `gtkb-docs-memory-architecture-alignment-editplan-001`. That keeps this GO
   scoped to inventory/rules and avoids making a GO status look like approval
   to edit files before Codex reviews the preview.

## Required Action Items

Before implementation, submit the per-file edit preview with:

1. exact baseline declaration and reproduced scan command;
2. per-hit disposition for all 245 hits in the 37 EDIT files;
3. ADR-0001 citation insertion point or no-citation rationale for every EDIT
   file;
4. no broken repo-local ADR links;
5. no implementation changes to HISTORICAL/DEFER files;
6. separate handling for version bump and release notes.

## Decision Needed From Owner

None. Prime may proceed with the edit-preview bridge under the conditions above.
