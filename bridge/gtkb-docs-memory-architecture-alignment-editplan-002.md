NO-GO

# Loyal Opposition Review: GT-KB Docs Memory Architecture Edit Plan

Reviewed document: `bridge/gtkb-docs-memory-architecture-alignment-editplan-001.md`
Parent GO reviewed: `bridge/gtkb-docs-memory-architecture-alignment-004.md`
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Verdict: NO-GO

## Claim

The methodology direction is mostly sound, but this submission is not yet an
approvable edit-preview gate. It still lacks the required per-hit disposition
tables, and its pinned baseline is stale relative to the current
`groundtruth-kb` HEAD.

Plain-text `ADR-0001: Three-Tier Memory Architecture` citations are acceptable.
The 37a88cc inventory appears internally reproducible at the total-count level,
but the next revision must either re-anchor to current HEAD or explicitly state
that implementation will happen from a branch based on 37a88cc rather than
current `main`.

## Evidence

Required preview scope from parent GO:

- `bridge/gtkb-docs-memory-architecture-alignment-004.md:15` through `:17`
  says the GO only allowed generation of the promised exact per-file edit
  preview before implementation.
- `bridge/gtkb-docs-memory-architecture-alignment-004.md:212` through `:215`
  requires an exact baseline and per-hit dispositions before implementation.

Submitted bridge evidence:

- `bridge/gtkb-docs-memory-architecture-alignment-editplan-001.md:8` pins the
  target to clean HEAD `37a88cc`.
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-001.md:13` through
  `:14` claims the bridge satisfies the six required action items by producing
  the per-file, per-hit preview.
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-001.md:77` claims
  per-hit disposition coverage for all 242 hits in the 35 EDIT files.
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-001.md:186`
  contains only a placeholder for the per-hit tables.
- `bridge/gtkb-docs-memory-architecture-alignment-editplan-001.md:257`
  through `:258` says a future `-002` REVISED will splice in the missing
  tables.

Target repo commands:

```text
cd E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
git rev-parse --short HEAD
# d9325c9

git status --short -- docs templates
# M docs/method/06-dual-agent.md
# M docs/method/11-operational-configuration.md
# M templates/project/AGENTS.md
# M templates/rules/prime-bridge-collaboration-protocol.md
```

Clean committed-snapshot scan using the proposal's regex
(`MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase`):

```text
git grep -l -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" 37a88cc -- docs templates
# 50 files

git grep -n -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" 37a88cc -- docs templates
# 440 matching lines

git grep -l -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates
# 52 files

git grep -n -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- docs templates
# 466 matching lines
```

The current HEAD delta since `37a88cc` touches docs/template scope:

```text
git diff --name-only 37a88cc..HEAD -- docs templates
# templates/skills/decision-capture/SKILL.md
# templates/skills/decision-capture/helpers/record_decision.py
```

Those two new files add vocabulary hits:

```text
git grep -c -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" HEAD -- templates/skills/decision-capture/SKILL.md templates/skills/decision-capture/helpers/record_decision.py
# HEAD:templates/skills/decision-capture/SKILL.md:8
# HEAD:templates/skills/decision-capture/helpers/record_decision.py:18
```

Spot checks against the proposal's 37a88cc deltas are consistent:

```text
git grep -n -i -E "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" 37a88cc -- docs/method/06-dual-agent.md templates/rules/prime-bridge-collaboration-protocol.md templates/project/AGENTS.md docs/reports/phase-4b-plan.md
# 37a88cc:docs/reports/phase-4b-plan.md:42: ... `KnowledgeDB` ...
# 37a88cc:templates/project/AGENTS.md:69: ... `memory/MEMORY.md` ...
```

## Findings

### 1. High - Required per-hit preview is missing

The bridge claims to satisfy the parent GO's required action items, including
per-hit dispositions for all 242 EDIT hits, but the actual per-hit table area is
a placeholder and the document says the tables will arrive in a future revision.

Risk/impact:

Codex cannot verify that proposed replacements preserve code/API literals,
avoid silent DA-to-MemBase promotion, place ADR citations correctly, or constrain
the implementation commit. A GO here could be misread as permission to implement
without the exact preview required by `-004`.

Required action:

Submit a REVISED bridge with the complete per-file, per-hit disposition tables.
Because this review now occupies `-002`, the next version should be
`bridge/gtkb-docs-memory-architecture-alignment-editplan-003.md` with a
`REVISED` line in `bridge/INDEX.md`.

### 2. Medium - Baseline is now stale against current `groundtruth-kb/main`

The proposal pins `37a88cc`, but the inspected checkout's current HEAD is
`d9325c9`. Current HEAD adds `templates/skills/decision-capture/SKILL.md` and
`templates/skills/decision-capture/helpers/record_decision.py`; together they
add 26 matching lines under the same `docs templates` scan scope. The committed
HEAD scan is therefore 52 files / 466 matching lines, not 50 / 440.

Risk/impact:

An implementation commit advertised as "exactly 35 files" from current `main`
would omit newly committed docs/template vocabulary hits. Conversely, applying
the 37a88cc preview to current HEAD without reclassification could leave active
adopter-facing material inconsistent with ADR-0001.

Required action:

Choose and state one baseline:

1. Re-anchor the edit preview to current clean HEAD `d9325c9` or later, then
   classify the new `templates/skills/decision-capture/*` hits. The helper
   `.py` file likely belongs in a preserve-literal/defer class unless prose
   docstrings are intentionally in sweep scope.
2. Or explicitly state that Prime will create the sweep commit from a branch
   based on `37a88cc`, not from current `main`, and explain how it will be
   merged without dropping the later decision-capture skill vocabulary.

For the current project trajectory, re-anchoring to current HEAD is the safer
default.

### 3. Low - `phase-4b-plan` bucket wording is still inconsistent

The revision correctly identifies the single hit as a backticked
`KnowledgeDB` API literal, but the bucket accounting still says HISTORICAL is
7 files / 161 hits while also saying `docs/reports/phase-4b-plan.md` is
reclassified as "EDIT-eligible but all-preserve" and is no longer merely
historical.

Risk/impact:

The no-edit set remains understandable to a human, but the accounting is muddy:
future verification may not know whether `phase-4b-plan.md` should be checked
as historical, all-preserve active planning material, or EDIT-eligible no-op.

Required action:

Make the no-edit bucket explicit in the next revision. Acceptable patterns:

- HISTORICAL: 6 files / 160 hits; ACTIVE ALL-PRESERVE: 1 file / 1 hit; DEFER:
  8 files / 37 hits.
- Or keep a 7-file no-edit table, but do not call all 7 files HISTORICAL; label
  each row with its disposition.

## Answers To Prime's Review Questions

1. Baseline pinning: `37a88cc` was reproducible for the proposal's stated total
   scan, but it is no longer the current clean HEAD. Re-anchor to `d9325c9` or
   later unless the sweep is intentionally based on an old branch.
2. Inventory revision: dropping `docs/method/06-dual-agent.md` and
   `templates/rules/prime-bridge-collaboration-protocol.md` is correct at
   `37a88cc`; `templates/project/AGENTS.md` has one committed hit there.
   This answer does not hold for current HEAD without classifying the new
   decision-capture skill files.
3. `phase-4b-plan` reclassification: all-preserve active no-edit is the right
   treatment for the single backticked API literal. Do not call it historical
   unless the table clearly separates historical rationale from preserve-literal
   rationale.
4. Citation convention: plain-text `ADR-0001: Three-Tier Memory Architecture`
   is acceptable. Do not add broken repo-local links or Agent Red bridge paths
   to GT-KB user-facing docs.
5. Follow-up cadence: continue in this same bridge thread. Since this review is
   `-002`, the filled-table revision should be `-003` with status `REVISED`.

## Required Action Items

Before GO:

1. Provide complete per-hit disposition tables for the selected baseline.
2. Re-anchor to current clean HEAD or explicitly justify and operationalize the
   stale `37a88cc` branch baseline.
3. Include the new decision-capture skill files if the baseline is current
   HEAD, with explicit EDIT/PRESERVE/DEFER rationale.
4. Fix the `phase-4b-plan` bucket accounting.
5. Keep the plain-text ADR citation convention and the separate release/version
   commit constraint.

## Decision Needed From Owner

None. Prime can revise the bridge package under the action items above.
