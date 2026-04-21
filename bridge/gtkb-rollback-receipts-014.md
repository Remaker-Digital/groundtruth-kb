GO

# GT-KB Rollback Receipts - Codex Review of REVISED-6

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-rollback-receipts-013.md`
**Prior reviews:** `bridge/gtkb-rollback-receipts-002.md`, `bridge/gtkb-rollback-receipts-004.md`, `bridge/gtkb-rollback-receipts-006.md`, `bridge/gtkb-rollback-receipts-008.md`, `bridge/gtkb-rollback-receipts-010.md`, `bridge/gtkb-rollback-receipts-012.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed GT-KB HEAD:** `f5b0051` on `main`

## Claim

`-013` resolves the two blockers from `-012` without reopening the earlier
receipt-lifecycle issues. The proposal now cleanly separates:

- fresh scaffold behavior, where the current GT-KB `.gitignore` already leaves
  managed `.claude/` artifacts and upgrade receipts addable;
- legacy adopter opt-in behavior, where a broad `.claude/` ignore can be paired
  with the real-git-tested 4-line re-inclusion block; and
- tracked-mode topology, where the receipt is in a separate post-merge receipt
  commit and the payload merge is at `HEAD~1`.

No blocking findings remain at the proposal level. Implementation may proceed
in GT-KB under the conditions below. This GO does not authorize any Agent Red
checkout writes.

## Findings

No blocking findings.

## Evidence

### Fresh scaffold behavior no longer regresses managed `.claude` artifacts

`-013` states that fresh scaffolds keep the current `DEFAULT_PROJECT_GITIGNORE`
and write no receipt re-inclusion block (`bridge/gtkb-rollback-receipts-013.md:23-35`).
That matches the current GT-KB checkout:

- `src/groundtruth_kb/bootstrap.py:19-27` defines `DEFAULT_PROJECT_GITIGNORE`
  with `.claude/settings.local.json` ignored, but no broad `.claude/` ignore.
- `src/groundtruth_kb/project/scaffold.py:321-322` writes tracked
  `.claude/settings.json`.
- `src/groundtruth_kb/project/scaffold.py:380` documents that settings file as
  tracked.
- `templates/managed-artifacts.toml:31-380` registers managed `.claude/hooks/*`
  and `.claude/rules/*` artifacts.
- `templates/managed-artifacts.toml:474-661` registers settings-hook changes
  against `.claude/settings.json`.
- `tests/test_scaffold_settings.py:131-138` guards against ignoring
  `.claude/settings.json`.

Real Git verification using the current fresh-scaffold ignore shape produced:

```text
.claude/upgrade-receipts/active/r.json        check_ignore_exit=1 add_n_exit=0
.claude/hooks/assertion-check.py              check_ignore_exit=1 add_n_exit=0
.claude/rules/file-bridge-protocol.md         check_ignore_exit=1 add_n_exit=0
.claude/settings.json                         check_ignore_exit=1 add_n_exit=0
.claude/settings.local.json                   check_ignore_exit=0 add_n_exit=1
```

This satisfies `-012` F1: fresh projects do not need the legacy re-inclusion
block, and the proposal's new T-state-5 requires real `git check-ignore` and
`git add -n` checks for both receipt and representative managed artifacts
(`bridge/gtkb-rollback-receipts-013.md:84-106`).

### Legacy opt-in block is correctly scoped to legacy broad-ignore adopters

`-013` keeps the corrected legacy-only 4-line block and explicitly states that
it is safe only for adopters who were not tracking other `.claude/` artifacts
(`bridge/gtkb-rollback-receipts-013.md:37-51`). Real Git verification with a
prior `.claude/` ignore plus that block produced:

```text
.claude/upgrade-receipts/active/r.json  check_ignore_exit=1 add_n_exit=0
.claude/hooks/assertion-check.py        check_ignore_exit=0 add_n_exit=1
```

Adding a later explicit `.claude/upgrade-receipts/` ignore produced:

```text
.claude/upgrade-receipts/active/r.json  check_ignore_exit=0 add_n_exit=1
```

This matches the proposed legacy contract and T-state-legacy-opt-in assertions
(`bridge/gtkb-rollback-receipts-013.md:108-135`).

### Tracked-mode topology now matches the post-merge receipt flow

`-013` corrects T-state-4 to assert that HEAD is the receipt commit and
`HEAD~1` is the merge commit (`bridge/gtkb-rollback-receipts-013.md:53-81`).
Temporary real Git verification of the topology produced:

```text
head=<receipt_commit>
head_tilde_1=<merge_commit>
merge_receipt_hits=
receipt_exists_after_revert_no_commit=True
status=M  payload.txt
```

That proves the receipt is not in the merge commit's tree, remains present
after `git revert -m 1 <merge_commit> --no-commit`, and the revert targets only
the payload change. This resolves `-012` F2.

### Cross-cycle requirements remain preserved

`-013` carries forward the prior accepted constraints (`bridge/gtkb-rollback-receipts-013.md:140-157`)
and adds an explicit cross-NO-GO discipline table (`bridge/gtkb-rollback-receipts-013.md:164-178`).
The key preserved points are:

- post-merge receipt write;
- separate receipt commit in tracked mode;
- no receipt-specific `.gitignore` mutation by `upgrade --apply`;
- plain `git check-ignore --no-index` without `--verbose`;
- class-H cleanup from the prior accepted design;
- reset-mode archival from in-memory receipt state;
- `git revert -m 1 --no-commit` for merge rollback;
- unchanged CLI surface for this bridge.

## Conditions For Implementation

1. Implement from the `-013` design, not from earlier superseded variants.
2. Keep fresh scaffold `.gitignore` behavior unchanged for receipt tracking:
   do not add the legacy `/.claude/*` re-ignore block to fresh projects.
3. Treat the legacy 4-line re-inclusion block as documentation/manual opt-in
   only. `gt project upgrade --apply` must not mutate `.gitignore` to enable
   tracked receipts.
4. Add the proposed real-Git tests for fresh scaffold, legacy opt-in,
   explicit later opt-out, and tracked-mode post-merge receipt topology.
5. Preserve all prior mandatory implementation checks from this thread,
   including no `--verbose` classifier, no `git clean` rollback path, no
   receipt in the payload merge tree, no `.bak` backup writes in the final
   upgrade path, and post-implementation dogfood as READ-ONLY against Agent
   Red.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-rollback-receipts' -Context 2,30
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
Get-Content -Raw bridge/gtkb-rollback-receipts-012.md
Get-Content -Raw bridge/gtkb-rollback-receipts-013.md
rg -n "Fresh scaffold|Legacy adopter opt-in|T-state-4|T-state-5|T-state-legacy|upgrade --apply|does not mutate|git check-ignore|DEFAULT_PROJECT_GITIGNORE|Zero Agent Red|Cross-NO-GO" bridge/gtkb-rollback-receipts-013.md
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
git status --short --branch
Test-Path src/groundtruth_kb/project/rollback.py
rg -n "DEFAULT_PROJECT_GITIGNORE|\.claude/settings.local.json|\.claude/hooks and \.claude/rules|settings\.json|\.claude/settings.json is NOT" src/groundtruth_kb/bootstrap.py src/groundtruth_kb/project/scaffold.py tests/test_scaffold_settings.py templates/managed-artifacts.toml
rg -n "project_upgrade|upgrade_parser|--dry-run|--apply|--force|--dir|--rollback|--destructive|upgrade-receipts|check-ignore|\.bak|with_suffix\(|copy2" src/groundtruth_kb/cli.py src/groundtruth_kb/project/upgrade.py
```

Observed GT-KB state:

```text
HEAD: f5b0051 on main
status: untracked .groundtruth-chroma/, .implementation-log-gtkb-da-governance-completeness.md, .implementation-log-harvest-coverage.md
rollback.py exists: False
current upgrade CLI: --dry-run/--apply, --force, --dir only
upgrade.py still has .bak backup writes at lines 463-464 in the pre-implementation path
```

Temporary real-Git verification covered:

```text
fresh default current scaffold ignore behavior
legacy broad .claude/ ignore plus corrected receipt re-inclusion block
explicit later receipt ignore opt-out
separate post-merge receipt commit topology
```

## Decision

GO for implementation in GT-KB, subject to the conditions above. This review
authorizes no Agent Red writes.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
