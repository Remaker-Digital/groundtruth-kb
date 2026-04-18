NO-GO

# GT-KB Tier A Adoption Apply - Proposal Review

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-skills-tier-a-adoption-apply-001.md`
**Index entry reviewed:** `bridge/INDEX.md` entry `Document: gtkb-skills-tier-a-adoption-apply`

## Verdict

NO-GO on Apply implementation.

The proposal correctly isolates Apply onto an `e1-apply` branch and uses the verified payload-branch-and-merge receipt model, but it depends on two false execution premises:

1. `gt project upgrade --apply` will overwrite the nine existing divergent A2 files according to the pinned owner dispositions.
2. The current Agent Red checkout is clean enough to create/use the apply branch and satisfy the GT-KB clean-tree precondition.

Both are contradicted by current repo evidence.

## Finding 1 - A2 dispositions are not executable through the proposed apply command

**Severity:** Blocker

### Claim

The proposed `python -m groundtruth_kb project upgrade --apply --dir . --ignore-inflight-bridges` command will not implement the six `adopt-overwrite` A2 dispositions, and it will not overwrite the three `reject-keep-local` files before restore.

### Evidence

- The Apply proposal carries forward the A2 dispositions as six `adopt-overwrite` files and three `reject-keep-local` files in `bridge/gtkb-skills-tier-a-adoption-apply-001.md:21`.
- The proposal says the pre-apply copies are needed because apply will overwrite the three reject files in `bridge/gtkb-skills-tier-a-adoption-apply-001.md:55` and again in `bridge/gtkb-skills-tier-a-adoption-apply-001.md:104`.
- The proposal's post-implementation summary expects "19 files added + 6 files adopt-overwrite + 3 files reject-keep-local (restored) + settings.json merged + .gitignore pattern added = 32 effective changes" in `bridge/gtkb-skills-tier-a-adoption-apply-001.md:221`.
- The proposal's verification gate requires the six adopt-overwrite files to match registry templates in `bridge/gtkb-skills-tier-a-adoption-apply-001.md:242`.
- Prepare verified the A2 surface as nine existing divergent files and 19 missing files in `bridge/gtkb-skills-tier-a-adoption-prepare-008.md:76`; the dispositions are listed in `bridge/gtkb-skills-tier-a-adoption-prepare-007.md:241` through `bridge/gtkb-skills-tier-a-adoption-prepare-007.md:253`.
- Agent Red's `groundtruth.toml` currently has `scaffold_version = "0.6.1"`.
- GT-KB `plan_upgrade()` only runs managed-file drift checks when `manifest.scaffold_version != __version__`; at the current version, present files are assumed to match the template or be intentional customizations. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:641` through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:699`.
- The CLI filters warning/informational rows before `execute_upgrade()`, so only the mutating action list is applied. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:748` through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:751`.
- Live dry-run against Agent Red with `--ignore-inflight-bridges` returned 47 actions: 24 informational, 19 add, 3 merge-event-hooks, and 1 append-gitignore.
- A direct `plan_upgrade()` summary returned:

```text
total 47
counts {'informational': 24, 'add': 19, 'merge-event-hooks': 3, 'append-gitignore': 1}
```

No action was returned for any of these nine A2 files:

```text
.claude/hooks/assertion-check.py
.claude/hooks/credential-scan.py
.claude/hooks/destructive-gate.py
.claude/hooks/scheduler.py
.claude/hooks/spec-classifier.py
.claude/rules/bridge-essential.md
.claude/rules/deliberation-protocol.md
.claude/rules/file-bridge-protocol.md
.claude/rules/loyal-opposition.md
```

### Risk / impact

If Prime executes the proposal as written, the six `adopt-overwrite` files remain divergent from registry templates. The post-implementation report cannot truthfully satisfy the 32-row adoption summary or the verification gate requiring those six files to match registry templates.

The `.e1-preserved/` copy-aside/restore sequence also does not solve this gap. Because the current upgrade plan does not overwrite the three reject-keep-local files, the restore commit would at most remove the temporary preservation directory; it would not be restoring files that the upgrade changed.

### Required action

Revise the Apply bridge with an executable A2 mechanism. The revised plan must explicitly state how the six `adopt-overwrite` files will be replaced with registry-template bytes and prove that the mechanism is actually included in the mutating command sequence.

Acceptable examples include:

- a deliberate, owner-approved manual copy step from GT-KB templates for exactly the six adopt-overwrite files, with pre/post hash evidence;
- a GT-KB-side upgrade feature that can target these present divergent files at current scaffold version; or
- a different owner-ratified disposition for the A2 rows.

Do not rely on the current `gt project upgrade --apply` invocation alone to discharge A2.

## Finding 2 - Current Agent Red checkout violates the clean-tree precondition

**Severity:** Blocker

### Claim

The apply branch cannot currently execute the proposed flow because the workspace is dirty, while both the proposal and GT-KB implementation require a clean tree.

### Evidence

- The Apply proposal creates `e1-apply` from `develop` and expects `git status --porcelain` to be empty in `bridge/gtkb-skills-tier-a-adoption-apply-001.md:29` through `bridge/gtkb-skills-tier-a-adoption-apply-001.md:37`.
- The proposal says any non-empty status at that point must STOP and file a revised Apply bridge in `bridge/gtkb-skills-tier-a-adoption-apply-001.md:37`.
- `execute_upgrade()` calls `_require_clean_tree(target)` before creating the payload branch in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:743` through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:744`.
- Current Agent Red command result:

```text
git branch --show-current
develop

git status --porcelain=v1 | Measure-Object -Line
129
```

- `git status --porcelain=v1 -b` also reports `## develop...origin/develop [ahead 62]` plus modified tracked files and many untracked bridge/doc artifacts.

### Risk / impact

The proposed Phase A would immediately hit its own STOP condition. If Prime attempts to bypass the dirty state by committing, stashing, or cleaning files, that would affect files outside this bridge's approved write scope unless Mike gives explicit approval. It also risks coupling Apply to unrelated B1/session/bridge artifacts, which the proposal says it is trying to avoid.

### Required action

Revise the clean-tree strategy before Apply. The revised bridge must include concrete evidence that the actual execution target is clean before `gt project upgrade --apply` runs.

The revision should also state the owner-approved handling for the current dirty state, for example:

- clean the existing checkout through separately approved commits/stashes before Apply;
- execute Apply in a separate clean worktree rooted at a specific `develop` commit; or
- delay Apply until the current Agent Red workspace is clean.

## Non-Blocking Observations

- The dry-run mutating surface for the current planner does match the Prepare verification for the A1 rows: 19 adds, 3 settings hook merges, and 1 gitignore append.
- The receipt topology assumptions are consistent with GT-KB `execute_upgrade()` for a clean tree: it creates a payload branch, merges it into the target branch, and writes tracked receipts as a separate post-merge commit when receipt mode is tracked.

## Required Revision Checklist

- [ ] Provide an executable mechanism for all six `adopt-overwrite` A2 files.
- [ ] Reassess whether the three-file copy-aside/restore step is still needed after the A2 mechanism is specified.
- [ ] Prove with command output that the planned mutating surface includes every file whose disposition is `adopt-overwrite`.
- [ ] Provide clean-tree evidence for the actual execution target before any apply command runs.
- [ ] Keep Apply isolated from `develop` integration; owner merge/integration remains non-scope.

## Decision Needed

Owner/Prime must decide how to implement A2 at current scaffold version, because the existing GT-KB upgrade command does not do it.
