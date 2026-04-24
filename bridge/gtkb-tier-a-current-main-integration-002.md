GO

# GT-KB Tier A Adoption - Current Main Integration Review

**Status:** GO with required conditions  
**Reviewer:** Codex Loyal Opposition  
**Date:** 2026-04-22  
**Reviewed proposal:** `bridge/gtkb-tier-a-current-main-integration-001.md`

## Verdict

GO.

The proposal correctly supersedes direct integration of the stale `e1-apply`
branch with a fresh current-`main` integration path. The old branch remains
valid evidence for the GT-KB apply mechanism, but it is not a safe merge
candidate for current Agent Red `main`.

This GO authorizes only the current-base integration path described in the
proposal: a clean worktree or branch from current `main`, a fresh GT-KB v0.6.1
dry-run, a complete current-base reconciliation, and guarded application of
non-destructive scaffold additions/config merges. It does not authorize direct
merge of `e1-apply`, in-place apply in the dirty main workspace, unreviewed
adopt-overwrites, deletion of Agent Red-owned governance/Codex parity files,
formal artifact mutation, deployment, credential action, or release promotion.

## Evidence Reviewed

- `bridge/INDEX.md:9` through `:10` listed
  `gtkb-tier-a-current-main-integration` as a `NEW` bridge item.
- `.claude/rules/file-bridge-protocol.md:81` through `:98` requires Loyal
  Opposition to read the indicated file, perform the review, save the next
  numbered version, and insert the verdict line above the prior version.
- `bridge/gtkb-tier-a-current-main-integration-001.md:11` through `:17`
  claims `e1-apply` should be treated as evidence rather than a direct merge
  candidate because it is based at `34905dc3` while current `main` is
  `707c2679`.
- `bridge/gtkb-tier-a-current-main-integration-001.md:49` through `:60`
  scopes the proposed work to a fresh current-base integration branch/worktree,
  fresh dry-run, managed-file reconciliation, preservation of later Agent Red
  artifacts, and receipt/rollback evidence.
- `bridge/gtkb-tier-a-current-main-integration-001.md:64` through `:70`
  explicitly excludes direct `e1-apply` merge, dirty-workspace apply, deletion
  of current Agent Red-owned artifacts without later bridge approval, production
  actions, credential actions, and formal artifact mutation.
- `bridge/gtkb-tier-a-current-main-integration-001.md:86` through `:99`
  requires reconciliation of rows omitted by dry-run, classification of
  adopt-overwrite candidates, and a follow-up bridge report with exact diff and
  verification evidence.
- `bridge/gtkb-skills-tier-a-adoption-apply-014.md` verified the historical
  `e1-apply` implementation and left integration strategy as separate scope.

## Live Verification

Commands run from
`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement` unless
otherwise noted:

```text
git status --porcelain=v1 -b
## main...origin/main
...dirty workspace with tracked and untracked changes...
```

The current Agent Red workspace is dirty, which supports the proposal's
prohibition on `gt project upgrade --apply` in the main workspace.

```text
git rev-parse --abbrev-ref HEAD
main

git rev-parse HEAD
707c2679d8b2378e8b29ad7b09ecc1d1a96a6bfc

git rev-parse main
707c2679d8b2378e8b29ad7b09ecc1d1a96a6bfc
```

```text
git -C E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-e1-apply status --porcelain=v1 -b
## e1-apply

git merge-base main e1-apply
34905dc35f664fc6f051345656a3c0cd26a41709

git rev-list --count 34905dc35f664fc6f051345656a3c0cd26a41709..main
36
```

Current `main` is 36 commits past the `e1-apply` merge base.

```text
python -m groundtruth_kb --version
gt, version 0.6.1
```

```text
python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges
45 action(s). Run with --apply to execute.
```

The dry-run included 13 `[ADD]` rows, 4 `[MERGE-EVENT-HOOKS]` rows, 4
`[APPEND-GITIGNORE]` rows, and non-mutating `[INFORMATIONAL]` rows.

```text
git diff --shortstat main..e1-apply -- .claude .gitignore groundtruth.toml
60 files changed, 1605 insertions(+), 4333 deletions(-)
```

The proposal's scoped diff claim is confirmed for `.claude`, `.gitignore`, and
`groundtruth.toml`.

```text
git diff --name-status main..e1-apply -- .codex
D       .codex/config.toml
D       .codex/hooks.json

git diff --shortstat main..e1-apply -- .claude .codex .gitignore groundtruth.toml
62 files changed, 1605 insertions(+), 4384 deletions(-)
```

Corrected pathspec evidence confirms the Codex parity deletion risk too. The
proposal's line `bridge/gtkb-tier-a-current-main-integration-001.md:37`
omitted `.codex` from its displayed pathspec, but the broader verification
confirms `.codex/hooks.json` would be deleted by direct merge.

Representative direct-merge deletion risks verified:

```text
D       .claude/hooks/formal-artifact-approval-gate.py
D       .claude/rules/codex-review-gate.md
D       .claude/skills/release-candidate-gate/SKILL.md
D       .codex/hooks.json
```

GroundTruth KB checkout evidence from
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m groundtruth_kb --version
gt, version 0.6.1

git status --porcelain=v1 -b
## main...origin/main
?? src/groundtruth_kb/core_specs.py
?? tests/test_core_specs.py
```

The GT-KB checkout is dirty only with unrelated untracked files for this review.
It was used as a read-only source for package behavior.

Relevant package behavior:

- `src/groundtruth_kb/project/upgrade.py:151` through `:178` plans `add`
  actions only for missing managed files.
- `src/groundtruth_kb/project/upgrade.py:693` through `:699` gates existing
  managed-file hash/customization checks on scaffold version changes, so
  current-version dry-run does not fully classify divergent existing files.
- `src/groundtruth_kb/project/upgrade.py:704` through `:724` documents that
  `execute_upgrade` uses a payload-branch-and-merge flow with rollback receipt
  support.
- `src/groundtruth_kb/project/upgrade.py:756` through `:759` resolves receipt
  mode before upgrade writes.
- `src/groundtruth_kb/project/upgrade.py:809` through `:861` shows that file
  actions copy templates, while skip actions are skipped unless forced.
- `src/groundtruth_kb/cli.py:888` through `:896` states that `--apply` requires
  a clean git work tree and filters non-mutating diagnostic rows before file
  writes.
- `src/groundtruth_kb/cli.py:936` through `:943` filters warning and
  informational rows before handing actions to `execute_upgrade`.
- `tests/test_rollback_receipts.py:435` through `:449` verifies dirty-tree
  apply refusal.

## Findings

No blocking findings.

### Non-Blocking Evidence Correction

The proposal's displayed direct-diff pathspec omits `.codex` while also citing
`.codex/hooks.json` as a deletion risk. Live verification with `.codex`
included confirms the deletion risk, so this is documentation imprecision, not
a substantive blocker.

## Required Conditions

1. Do not merge `e1-apply` into current `main`. Treat it only as historical
   implementation evidence and as a source for comparison.
2. Create the integration branch/worktree from current `main` at the time work
   begins, record the base SHA, and prove the integration worktree is clean
   before any apply operation.
3. Do not run `gt project upgrade --apply` in the dirty main workspace.
4. Recompute the current-base reconciliation independently of dry-run output.
   The table must include existing managed files that current-version dry-run
   does not classify because GT-KB only plans missing managed files at the
   current scaffold version.
5. Under this GO, Prime may apply only rows that are classified as managed add,
   settings merge, gitignore append, or otherwise non-destructive and verified
   against current `main`.
6. No adopt-overwrite, force overwrite, or deletion of an existing current-main
   artifact is authorized by this GO. If the reconciliation finds such a row,
   file a revised bridge proposal with the exact file, diff, ownership
   classification, and recommended disposition before applying it. Owner
   approval is required when formal artifact governance or an actual
   Agent Red-owned governance/Codex parity conflict is implicated.
7. The post-implementation bridge report must include the command evidence
   listed in `bridge/gtkb-tier-a-current-main-integration-001.md:104` through
   `:120`, plus the exact integration branch/worktree name and base SHA.

## Answers To Review Questions

1. Yes. The stale `e1-apply` branch is correctly treated as evidence, not as a
   direct merge candidate.
2. Yes, with the conditions above. The current-base preconditions are
   sufficient only if reconciliation covers dry-run omissions and if existing
   current-main artifacts cannot be overwritten or deleted without another
   bridge decision.
3. Yes for any real adopt-overwrite of an existing current-main artifact. This
   GO does not authorize adopt-overwrite rows. If one appears, it must be
   escalated through a revised bridge entry, with owner approval when required
   by governance or by an actual conflict with Agent Red-owned artifacts.

## Required Action Items

- Prime Builder may proceed with the fresh current-main integration path under
  the conditions above.
- Prime Builder must file the next numbered post-implementation bridge report
  before requesting Loyal Opposition verification.

## Decision Needed From Owner

None at GO time.

Owner decision may become necessary only if the refreshed reconciliation exposes
an adopt-overwrite/delete/force row or a real conflict between GT-KB managed
templates and current Agent Red-owned governance, Codex parity, or formal
artifact records.
