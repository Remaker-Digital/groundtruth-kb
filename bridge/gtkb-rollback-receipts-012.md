NO-GO

# GT-KB Rollback Receipts - Codex Review of REVISED-5

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-rollback-receipts-011.md`
**Prior reviews:** `bridge/gtkb-rollback-receipts-002.md`, `bridge/gtkb-rollback-receipts-004.md`, `bridge/gtkb-rollback-receipts-006.md`, `bridge/gtkb-rollback-receipts-008.md`, `bridge/gtkb-rollback-receipts-010.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed GT-KB HEAD:** `f5b0051` on `main`

## Claim

`-011` fixes both blockers from `-010` at the narrow receipt-lifecycle level:
the receipt is again written after the payload merge commit exists, tracked
mode uses a separate post-merge receipt commit, and the documented legacy
opt-in block correctly re-includes an ignored `.claude/` parent.

It is still not ready for implementation GO. The new "fresh scaffold writes the
above 4-line block by default" rule would make the existing GT-KB scaffold
ignore its managed `.claude/` artifacts. That turns a receipt-tracking fix into
a broad scaffold tracking regression.

## Findings

### F1 - Fresh scaffold default block ignores managed `.claude/` artifacts

**Severity:** High

The corrected block in `-011` is valid for its original purpose: re-including
only `.claude/upgrade-receipts/**` when an adopter already has a broad
`.claude/` ignore. It does that by re-including the parent, then re-ignoring
all direct children with `/.claude/*`, then re-including the receipt subtree.

`-011` newly says `gt project init` writes that same 4-line block by default
for fresh scaffolds (`bridge/gtkb-rollback-receipts-011.md:105-107`). In the
current GT-KB scaffold, fresh projects do not broadly ignore `.claude/`.
`DEFAULT_PROJECT_GITIGNORE` ignores `.claude/settings.local.json` only
(`src/groundtruth_kb/bootstrap.py:19-27`), and the scaffold intentionally
creates tracked `.claude` assets: hooks and rules
(`src/groundtruth_kb/bootstrap.py:250`), `.claude/settings.json`
(`src/groundtruth_kb/project/scaffold.py:380`), plus managed hook/rule/skill
records in `templates/managed-artifacts.toml`.

With only the proposed 4-line block in a fresh repo, real Git classifies the
receipt file as addable, but it also ignores the managed scaffold files:

```text
?? .claude/upgrade-receipts/active/r.json
?? .gitignore
!! .claude/hooks/assertion-check.py
!! .claude/rules/file-bridge-protocol.md
!! .claude/settings.json
hooks_check_ignore_exit=0
receipt_check_ignore_exit=1
```

That contradicts the existing scaffold contract. GT-KB already has a test that
`.claude/settings.json` must not be ignored (`tests/test_scaffold_settings.py:131-137`),
and the registry shows `.claude/settings.json` as the target for multiple
settings-hook registrations (`templates/managed-artifacts.toml:474-661`).

The receipt block is therefore safe only when paired with a broad `.claude/`
ignore policy, or when followed by additional re-inclusions for every managed
`.claude` subtree that GT-KB expects adopters to track.

**Required action:**

1. Split the legacy opt-in block from the fresh scaffold default.
2. For legacy adopters with `.claude/` already ignored, keep the corrected
   re-inclusion block from `-011` or an equivalent real-git-tested sequence.
3. For fresh scaffolds, do not emit `/.claude/*` unless the scaffold also
   explicitly re-includes all tracked managed `.claude` artifacts and proves
   that `.claude/hooks/`, `.claude/rules/`, `.claude/skills/`, and
   `.claude/settings.json` remain addable.
4. Add a mandatory fresh-scaffold test that runs real `git check-ignore` and
   `git add -n` for both receipt JSON and representative managed scaffold
   files, not only for the receipt path.

### F2 - T-state-4 still contains an impossible `git log -1` assertion

**Severity:** Medium

The corrected flow says tracked mode creates a separate receipt commit after
`merge_commit`, with `receipt_commit` at `HEAD`
(`bridge/gtkb-rollback-receipts-011.md:31-43`). But T-state-4 still says
`git log -1 --format=%H` names the merge commit
(`bridge/gtkb-rollback-receipts-011.md:128`), while the next assertions expect
`git log <target> -n 2` to show receipt commit then merge commit
(`bridge/gtkb-rollback-receipts-011.md:131-133`).

The latter is the correct shape. The `git log -1` assertion would fail after a
successful tracked-mode upgrade, because `HEAD` is the receipt commit.

**Required action:**

- Update T-state-4 to capture `merge_commit` from the receipt or from
  `HEAD~1` after verifying the commit subjects/topology. Do not assert that
  `git log -1` names the merge commit in tracked mode.

## What Is Acceptable In REVISED-5

- The post-merge receipt write fixes the `-010` F1 regression at the design
  level.
- The tracked receipt commit being separate from the payload merge is the
  correct lifecycle model.
- The corrected 4-line block works for the legacy case where `.claude/` is
  already ignored and the goal is to re-include only `upgrade-receipts`.
- `upgrade --apply` not mutating `.gitignore` for receipt tracking remains
  acceptable.

## Required Revision

File `bridge/gtkb-rollback-receipts-013.md` as `REVISED` with:

1. A fresh-scaffold `.gitignore` plan that does not ignore GT-KB-managed
   `.claude` artifacts.
2. Separate tests for legacy opt-in behavior and fresh scaffold behavior.
3. Real-git assertions that representative managed `.claude` files remain
   addable in a fresh scaffold after the receipt tracking rule is present.
4. Corrected T-state-4 topology assertions for the post-merge receipt commit.

No GT-KB rollback implementation should begin from `-011`.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-rollback-receipts' -Context 8,40
Get-Content -Raw bridge/gtkb-rollback-receipts-001.md
Get-Content -Raw bridge/gtkb-rollback-receipts-002.md
Get-Content -Raw bridge/gtkb-rollback-receipts-003.md
Get-Content -Raw bridge/gtkb-rollback-receipts-004.md
Get-Content -Raw bridge/gtkb-rollback-receipts-005.md
Get-Content -Raw bridge/gtkb-rollback-receipts-006.md
Get-Content -Raw bridge/gtkb-rollback-receipts-007.md
Get-Content -Raw bridge/gtkb-rollback-receipts-008.md
Get-Content -Raw bridge/gtkb-rollback-receipts-009.md
Get-Content -Raw bridge/gtkb-rollback-receipts-010.md
Get-Content -Raw bridge/gtkb-rollback-receipts-011.md
rg -n "Fresh scaffold|Line 2|T-state-4|git log -1|git log <target>|separate post-merge|Corrected opt-in block|upgrade --apply" bridge/gtkb-rollback-receipts-011.md
```

Temporary git verification:

```text
Corrected legacy block with prior .claude/ ignore:
  git check-ignore --no-index -- .claude/upgrade-receipts/active/r.json
  => exit 1
  git add -n -- .claude/upgrade-receipts/active/r.json
  => exit 0, add '.claude/upgrade-receipts/active/r.json'

Corrected block plus later explicit .claude/upgrade-receipts/ ignore:
  git check-ignore --no-index -- .claude/upgrade-receipts/active/r.json
  => exit 0
  git add -n -- .claude/upgrade-receipts/active/r.json
  => exit 1, ignored

Separate post-merge receipt commit topology:
  merge_tree_receipt_hits=0
  receipt_exists_after_revert_no_commit=True
  status_after_revert_no_commit: D  payload.txt

Fresh scaffold side-effect using only the proposed 4-line block:
  ?? .claude/upgrade-receipts/active/r.json
  !! .claude/hooks/assertion-check.py
  !! .claude/rules/file-bridge-protocol.md
  !! .claude/settings.json
  hooks_check_ignore_exit=0
  receipt_check_ignore_exit=1
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
git status --short --branch
Test-Path src/groundtruth_kb/project/rollback.py
rg -n "project_upgrade|upgrade_parser|--dry-run|--apply|--force|--dir|--rollback|--destructive|upgrade-receipts|check-ignore" src/groundtruth_kb/cli.py src/groundtruth_kb/project/upgrade.py templates docs tests .github
rg -n "DEFAULT_PROJECT_GITIGNORE|\\.claude/settings.local.json|_write_project_gitignore|\\.claude/hooks and \\.claude/rules|\\.claude/settings.json|gitignore-pattern|\\.claude/hooks/\\*\\.log" src/groundtruth_kb/bootstrap.py src/groundtruth_kb/project/scaffold.py templates/managed-artifacts.toml tests/test_scaffold_settings.py docs/reference/cli.md
```

Observed GT-KB results:

```text
HEAD: f5b0051 on main
status: untracked .groundtruth-chroma/, .implementation-log-gtkb-da-governance-completeness.md, .implementation-log-harvest-coverage.md
rollback.py exists: False
current upgrade CLI: --dry-run/--apply, --force, --dir only
```
