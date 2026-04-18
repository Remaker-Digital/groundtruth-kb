NO-GO

# GT-KB Tier A Adoption Apply - Revised Proposal Review

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-skills-tier-a-adoption-apply-003.md`
**Prior review:** `bridge/gtkb-skills-tier-a-adoption-apply-002.md`
**Index entry reviewed:** `bridge/INDEX.md` entry `Document: gtkb-skills-tier-a-adoption-apply`

## Verdict

NO-GO on REVISED-1 Apply implementation.

The revised bridge correctly stops relying on `gt project upgrade --apply` to overwrite present same-version A2 drift, and a fresh worktree is a reasonable way to avoid the dirty main checkout. However, the selected worktree root is `develop` HEAD, and `develop` HEAD does not contain seven of the nine A2 files that the proposal treats as present local files.

That makes the revised plan non-executable as written and breaks the `reject-keep-local` disposition. In the proposed clean worktree, those three reject files are missing, not preserved.

## Finding 1 - Worktree root drops ignored local A2 files and violates reject-keep-local

**Severity:** Blocker

### Claim

`bridge/gtkb-skills-tier-a-adoption-apply-003.md` creates `../agent-red-e1-apply` from committed `develop` HEAD, but the committed tree lacks most of the A2 files. The proposal then assumes those files exist in the worktree and that the three `reject-keep-local` files remain unchanged.

### Evidence

- The revised proposal creates the worktree from `develop` at `bridge/gtkb-skills-tier-a-adoption-apply-003.md:41` through `bridge/gtkb-skills-tier-a-adoption-apply-003.md:57`, specifically `git worktree add ../agent-red-e1-apply -b e1-apply develop` at line 53.
- It says all later commands run inside that worktree and the main workspace is untouched at `bridge/gtkb-skills-tier-a-adoption-apply-003.md:66`.
- It says the three reject files are unchanged and still contain AR customized content at `bridge/gtkb-skills-tier-a-adoption-apply-003.md:139` through `bridge/gtkb-skills-tier-a-adoption-apply-003.md:141`.
- It requires the three reject files to byte-match the pre-worktree AR `develop` HEAD state at `bridge/gtkb-skills-tier-a-adoption-apply-003.md:295`.
- Prepare classified the three reject files as A2 `reject-keep-local` at `bridge/gtkb-skills-tier-a-adoption-prepare-007.md:245`, `:247`, and `:248`.
- Current committed `develop` HEAD is `2810ac7cb51ab8fa31803a4591ae2b6dd19be9e6`:

```text
git rev-parse develop
2810ac7cb51ab8fa31803a4591ae2b6dd19be9e6
```

- Direct inspection of the committed `develop` tree shows only two of the nine A2 files are tracked there:

```text
git ls-tree -r --name-only develop -- .claude/hooks .claude/rules
.claude/hooks/credential-scan.py
.claude/hooks/poller-freshness.py
.claude/rules/bridge-essential.md
```

- The seven missing A2 paths include all three `reject-keep-local` files and four of the six `adopt-overwrite` files:

```text
OK develop:.claude/hooks/credential-scan.py
MISSING develop:.claude/hooks/spec-classifier.py
OK develop:.claude/rules/bridge-essential.md
MISSING develop:.claude/rules/deliberation-protocol.md
MISSING develop:.claude/rules/file-bridge-protocol.md
MISSING develop:.claude/rules/loyal-opposition.md
MISSING develop:.claude/hooks/assertion-check.py
MISSING develop:.claude/hooks/destructive-gate.py
MISSING develop:.claude/hooks/scheduler.py
```

- Those local files exist in the current main workspace because `.gitignore` ignores almost all `.claude/hooks/*` and `.claude/rules/*`, except selected re-inclusions. See `.gitignore:187` through `.gitignore:195`:

```text
.claude/*
!.claude/settings.json
!.claude/hooks/
.claude/hooks/*
!.claude/hooks/poller-freshness.py
!.claude/hooks/credential-scan.py
!.claude/rules/
.claude/rules/*
!.claude/rules/bridge-essential.md
```

- `git check-ignore -v` confirms representative missing A2 files are ignored in the main workspace:

```text
.gitignore:190:.claude/hooks/*    .claude/hooks/spec-classifier.py
.gitignore:190:.claude/hooks/*    .claude/hooks/assertion-check.py
.gitignore:194:.claude/rules/*    .claude/rules/file-bridge-protocol.md
```

- GT-KB plans `add` actions unconditionally for missing managed files at current scaffold version. See `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:151` through `:178`.
- The relevant files are managed artifacts in GT-KB templates: `assertion-check.py` at `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\managed-artifacts.toml:27` through `:36`, `spec-classifier.py` at `:39` through `:46`, `destructive-gate.py` at `:63` through `:72`, `scheduler.py` at `:87` through `:94`, `loyal-opposition.md` at `:276` through `:285`, `file-bridge-protocol.md` at `:324` through `:333`, `bridge-essential.md` at `:336` through `:345`, and `deliberation-protocol.md` at `:348` through `:354`.

### Risk / impact

The proposed A.2 pre-copy hash loop is not executable as written for four `adopt-overwrite` paths because those files do not exist in the clean worktree rooted at `develop` HEAD:

```text
.claude/hooks/spec-classifier.py
.claude/rules/deliberation-protocol.md
.claude/rules/file-bridge-protocol.md
.claude/rules/loyal-opposition.md
```

More importantly, the three `reject-keep-local` files are not present in that worktree. Since GT-KB repairs missing managed files unconditionally, the later apply step can add registry-template versions of:

```text
.claude/hooks/assertion-check.py
.claude/hooks/destructive-gate.py
.claude/hooks/scheduler.py
```

That is the opposite of `reject-keep-local`. It also makes the verification gate "byte-match the pre-worktree AR develop HEAD state" impossible, because there is no `develop` HEAD blob for those three paths.

The live 47-action planner output previously used to justify the revised plan was run against the dirty main working directory, where ignored local files exist on disk. It is not valid evidence for the proposed clean worktree rooted at committed `develop`.

### Required action

Revise the Apply bridge to make the execution target match the A2 evidence source.

At minimum, the revised plan must:

1. State whether the A2 source of truth is committed `develop` HEAD or the current ignored local files in the main workspace.
2. If the three `reject-keep-local` files are to be preserved, explicitly copy or otherwise materialize them into the clean worktree before apply, with owner-approved source paths and hash evidence.
3. Decide whether those three files remain ignored/untracked local runtime files or become tracked/force-added artifacts on `e1-apply`. The current proposal cannot claim the main workspace is untouched and also claim the clean worktree inherits ignored local files.
4. Recompute the expected mutating surface inside the actual execution target after the A2 setup step, not against the dirty main checkout.
5. Update the adoption summary and rollback proof so missing-file adds, manual additions, and preserved ignored files are accurately classified.

## Non-Blocking Observations

- The revised manual copy mechanism is directionally correct for the two A2 paths that are actually tracked in `develop` HEAD (`credential-scan.py` and `bridge-essential.md`).
- `e1-apply` is not currently an existing local branch, and `../agent-red-e1-apply` does not currently exist, so the branch/path names are not blocked by current repo state.
- `python -c "from groundtruth_kb import get_templates_dir; print(get_templates_dir())"` resolves to `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates`, and the six proposed template source files exist there.

## Required Revision Checklist

- [ ] Rebase the plan around the committed `develop` tree, not the dirty main working tree, or explicitly import the ignored local A2 files into the clean worktree with hash evidence.
- [ ] Provide a concrete preservation mechanism for `.claude/hooks/assertion-check.py`, `.claude/hooks/destructive-gate.py`, and `.claude/hooks/scheduler.py`.
- [ ] Specify whether preserved reject files are tracked on `e1-apply`, force-added despite `.gitignore`, or intentionally left as ignored local files with a separate integration story.
- [ ] Replace the A.2 pre-hash loop with commands that handle missing paths deliberately instead of failing implicitly.
- [ ] Run or model the upgrade planner against the actual clean worktree state after A2 setup and list the resulting mutating actions.

## Decision Needed

Owner/Prime must decide whether the ignored local `.claude` A2 files are part of the Apply artifact set. If yes, the bridge needs an explicit import/preservation strategy before `gt project upgrade --apply` runs in a clean worktree.
