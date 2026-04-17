NO-GO

# Loyal Opposition Review: GT-KB Docs Memory Architecture Edit Plan

Reviewed document: `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md`
Prior versions reviewed: `bridge/gtkb-docs-memory-architecture-alignment-editplan-001.md`, `bridge/gtkb-docs-memory-architecture-alignment-editplan-002.md`
Parent GO reviewed: `bridge/gtkb-docs-memory-architecture-alignment-004.md`
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target HEAD inspected: `d9325c9`
Verdict: NO-GO

## Claim

The revised edit preview resolves the stale-baseline problem and provides a
reproducible 36-file / 250-line disposition set for the proposed EDIT bucket.
However, it is still not an approvable implementation gate because the binding
commit scope contradicts the per-file tables.

Six files are classified inside the 36-file EDIT set but are also assigned only
PRESERVE dispositions and explicit "no ADR-0001 citation needed" rationales.
If Prime follows the tables, the implementation commit will not modify those
files and will fail the proposed "exactly 36 files modified" exit criterion. If
Prime follows the exit criterion, it must touch files for which the preview
authorizes no target-repo edits.

## Evidence

Baseline verification:

```text
cd E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
git rev-parse --short HEAD
# d9325c9

git status --short -- docs templates
# M docs/method/06-dual-agent.md
# M docs/method/11-operational-configuration.md
# M templates/project/AGENTS.md
# M templates/rules/prime-bridge-collaboration-protocol.md

git grep -l -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates | Measure-Object
# Count: 52

git grep -n -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates | Measure-Object
# Count: 466
```

EDIT-bucket coverage verification:

```text
# Extracting `#### path (N hit[s])` headings from -003 found:
# headings=36 sum=250

# Running the same grep against those 36 paths at HEAD found:
# files=36 total=250
```

Relevant bridge evidence:

- `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:599`
  says 28 of 36 EDIT files receive ADR-0001 citations and the remaining 8
  receive "no citation needed" rationales.
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:608`
  makes the binding commit scope "Exactly 36 files modified -- every file in
  the EDIT set, no more."
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:620`
  repeats the exit criterion: "Single commit touches exactly the 36 files
  classified EDIT."

Six of the no-citation files have no replacement action in the target repo:

```text
HEAD:templates/project/AGENTS.md:69:
  - `memory/MEMORY.md` (current state and recent sessions)

HEAD:docs/reference/templates.md:14:
  | `templates/MEMORY.md` | `MEMORY.md` | Session state and operational memory |

HEAD:docs/tutorials/dual-agent-setup.md:27:
  - `CLAUDE.md` and `MEMORY.md` -- session state templates

HEAD:docs/tutorials/first-spec.md:40,42,77,79,105,107,182,184:
  `KnowledgeDB` API examples in Python code blocks

HEAD:docs/user-journey.md:49:
  The scaffold creates: `groundtruth.db`, `.claude/hooks/`, `CLAUDE.md`, `MEMORY.md`.

HEAD:docs/contributing.md:1:
  # Contributing to GroundTruth Knowledge DB
```

The corresponding -003 table entries explicitly preserve them:

- `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:191`
  says `templates/project/AGENTS.md` needs no ADR citation; its only hit is a
  literal file reference.
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:430`
  says `docs/reference/templates.md` needs no ADR citation; its only hit is a
  literal path mapping.
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:440`
  says `docs/tutorials/dual-agent-setup.md` needs no ADR citation; its only hit
  references templates.
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:448`
  says `docs/tutorials/first-spec.md` needs no ADR citation; every hit is a
  `KnowledgeDB` API literal inside Python blocks.
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:548`
  says `docs/user-journey.md` needs no ADR citation; its only hit is a literal
  scaffold-output list.
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:556`
  says `docs/contributing.md` needs no ADR citation; its only hit is the
  product brand name in the H1.

Two other no-citation files, `docs/method/03-testing.md` and
`docs/method/04-work-items.md`, do have EDIT replacements at
`bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:281` and
`:289`; they are not part of this contradiction.

## Findings

### 1. High - Binding commit scope conflicts with preserve-only dispositions

The proposal's table authorizes no target-repo edit for six files, but the
commit gate requires every one of the 36 EDIT-set files to be modified.

Risk/impact:

This breaks the implementation verification contract. A correct implementation
of the per-hit dispositions would likely modify 30 files, not 36. A commit that
touches all 36 files would need to add noise edits or otherwise change files
that the preview says should remain preserve-only. Either path makes the
post-implementation verification ambiguous and increases the chance of
unreviewed documentation churn.

Required action:

Revise the next bridge to separate "files with target-repo edits" from
"scan-covered all-preserve files." Acceptable fixes:

1. Move the six preserve-only/no-citation files out of the EDIT/modified-file
   bucket into an ACTIVE-ALL-PRESERVE or PRESERVE-ONLY bucket, and change the
   implementation gate to the resulting exact modified-file count.
2. Or explicitly add justified ADR-0001 citation insertions or other reviewed
   target-repo edits for those six files, then keep them in the modified-file
   set.

Do not keep a gate that simultaneously says "no edit needed" and "file must be
modified" for the same paths.

### 2. Low - Reproduced file-count command is imprecise

`bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:32` shows
`git grep -c ... HEAD -- docs templates` followed by `# 52 files`. That command
prints per-file match counts, not a single file count, unless it is piped to a
line counter.

Risk/impact:

The numeric claim is reproducible, but the written reproduction command is easy
to mis-run during later verification.

Required action:

Write the exact counting commands in the next revision, for example:

```text
git grep -l -i -E "<regex>" HEAD -- docs templates | wc -l
git grep -n -i -E "<regex>" HEAD -- docs templates | wc -l
```

Use the PowerShell `Measure-Object` equivalents if the verification runbook is
Windows-native.

### 3. Low - Rule 3 placement count label is off by one

`bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md:601` says
"6 high-impact files" but lists 7 files.

Risk/impact:

This is not a substantive architecture issue, but it is another verification
paper cut in a proposal whose implementation gate depends on exact counts.

Required action:

Correct the label or the list in the next revision.

## Answers To Prime's Review Questions

1. Re-anchored baseline: acceptable. `d9325c9` is the inspected HEAD, and the
   52-file / 466-line total is reproducible against `HEAD`.
2. Per-hit tables: materially improved and count-reproducible for the 36-file /
   250-line EDIT-bucket set, but the preserve-only/no-citation files must not
   be treated as mandatory modified files unless the revision adds reviewed
   edits for them.
3. Bucket split: HISTORICAL 6 / ACTIVE-ALL-PRESERVE 1 / DEFER 9 is acceptable.
   The same separation discipline should be applied to the six preserve-only
   files currently left inside the EDIT modified-file gate.
4. New-file classifications: `templates/skills/decision-capture/SKILL.md` as
   EDIT is acceptable because the proposal adds an ADR-0001 citation;
   `templates/skills/decision-capture/helpers/record_decision.py` as DEFER is
   acceptable because it is Python source and the sweep excludes `.py` edits.
5. Plain-text ADR-0001 citation convention: acceptable.

## Required Action Items

Before GO:

1. Reconcile the modified-file count with the per-file dispositions.
2. Either move the six all-preserve/no-citation files out of the modified-file
   gate or add explicit reviewed edits for them.
3. Update the commit-scope and exit-criteria counts accordingly.
4. Correct the reproduced count command.
5. Correct the Rule 3 placement count label.

## Decision Needed From Owner

None. Prime can revise the bridge package under the action items above.
