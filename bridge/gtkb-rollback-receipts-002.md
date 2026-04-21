NO-GO

# GT-KB Rollback Receipts - Codex Review

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-rollback-receipts-001.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Proposal target GT-KB HEAD:** `cf29738`
**Observed GT-KB HEAD:** `e12aab3` on `feature/ownership-matrix`
**Observed Agent Red HEAD:** `aa6a5fe5`

## Claim

The proposal satisfies the parent requirement to treat git rollback as a
candidate design and it covers the right artifact classes, but it is not ready
for implementation GO. The default rollback command is invalid for the
proposed `--no-ff` merge topology, and the receipt lifecycle is internally
inconsistent when receipts are tracked and included in the upgrade merge
commit.

These are design blockers, not implementation nits. If implemented as written,
`gt project upgrade --rollback <receipt_id>` can fail before doing any restore,
or can remove the receipt it is supposed to update and archive.

## Evidence Summary

- The proposal defines default rollback as `git revert <merge_commit>` and
  creates the upgrade as `git merge --no-ff gt-upgrade-<receipt_id>`
  (`bridge/gtkb-rollback-receipts-001.md:54`, `:89`).
- A local git reproduction showed that plain `git revert <merge_commit>` fails
  for a two-parent merge commit: `RevertExit: 128`, with
  `error: commit <sha> is a merge but no -m option was given.`
- The proposal writes the receipt before `git add -A; git commit`, then says
  the merge commit is captured in the receipt after the merge
  (`bridge/gtkb-rollback-receipts-001.md:86-89`). That order cannot produce the
  schema shown later, which requires `merge_commit`
  (`bridge/gtkb-rollback-receipts-001.md:147`).
- The proposal says receipt paths should not be ignored by default
  (`bridge/gtkb-rollback-receipts-001.md:128-129`) and class J says the
  receipt never rolls back itself (`bridge/gtkb-rollback-receipts-001.md:115`).
  But with the stated execution flow, `git add -A` includes the receipt in the
  upgrade commit, so reverting the merge will delete or conflict with the
  receipt unless rollback explicitly protects that path.
- Reset mode proposes `git clean -fd` for ignored-but-upgrade-created paths
  (`bridge/gtkb-rollback-receipts-001.md:55`). A local git reproduction showed
  `git clean -fdn` does not list an ignored `.gt-upgrade-staging/` path, while
  `git clean -fdxn` does.
- Current GT-KB still has the old upgrade surface: `project upgrade` exposes
  only `--dry-run/--apply`, `--force`, and `--dir`
  (`src/groundtruth_kb/cli.py:683-686`), and `execute_upgrade` still writes
  `.bak` files plus direct settings/gitignore/manifest writes
  (`src/groundtruth_kb/project/upgrade.py:355-369`, `:423`, `:448`, `:453`).

## Findings

### F1 - Default revert command is invalid for the proposed merge commit

**Severity:** High

The proposal uses `git merge --no-ff` to create the upgrade commit and then
uses `git revert <merge_commit>` as the default rollback mechanism. Git cannot
plain-revert a merge commit without a mainline parent. That makes the default
rollback path fail before any receipt or artifact-class logic can run.

This is not hypothetical. In a temporary repo with a `--no-ff` merge, the
reproduction command returned:

```text
RevertExit: 128
error: commit 6a1e599... is a merge but no -m option was given.
fatal: revert failed
```

**Required action:**

- Specify the exact merge-revert command, including mainline parent selection
  such as `git revert -m 1 <merge_commit>`, or change the upgrade topology to a
  single-parent upgrade commit.
- Add a mandatory test that creates the real proposed `--no-ff` merge commit
  and rolls it back through the public rollback entry point.
- Include the parent-order invariant in the receipt or rollback engine so the
  mainline parent is not guessed.

### F2 - Receipt tracking conflicts with rollback and archival semantics

**Severity:** High

The proposal says receipts live under `.claude/upgrade-receipts/`, should not
be ignored by default, and are written before `git add -A`. Therefore the
receipt file becomes part of the upgrade branch commit and the final merge
commit. A revert of that merge will try to remove the active receipt even
though the proposal says the receipt "never rolls back itself" and should move
to `archived/` with a rolled-back status.

The schema also cannot be populated in the stated order: `merge_commit` does
not exist when the proposal writes the receipt before the branch commit and
merge.

**Required action:**

- Define whether active receipts are included in the upgrade commit, excluded
  from it, or written/updated after the merge commit exists.
- If receipts are tracked, specify rollback as a protected-path operation, for
  example `git revert -m 1 --no-commit`, restore or move the receipt path
  intentionally, then commit the rollback plus archived receipt update.
- Add tests for tracked and ignored receipt defaults proving that rollback
  preserves an archived receipt with updated status.
- Correct the execution flow so `merge_commit` is captured after it exists and
  the final receipt state is durable.

### F3 - Reset cleanup command does not remove ignored upgrade-created paths

**Severity:** Medium

The proposal says destructive reset mode uses `git reset --hard
<pre_upgrade_sha>` plus `git clean -fd` on ignored-but-upgrade-created paths.
Plain `git clean -fd` does not clean ignored paths. In a temporary repo with
`.gt-upgrade-staging/` ignored, `git clean -fdn` returned no removal candidate,
while `git clean -fdxn` listed `.gt-upgrade-staging/`.

**Required action:**

- Do not describe ignored-path cleanup as plain `git clean -fd`.
- Use a path-specific deletion routine driven by the receipt manifest, or use
  the correct git clean flags with explicit pathspecs and tests proving
  adopter-created ignored siblings are preserved.
- Add a test for ignored path cleanup in reset mode, not only revert mode.

### F4 - Artifact class I is not proven under the proposed `git add -A` flow

**Severity:** Medium

Class I is described as an "untracked-but-created" path that git cannot restore
and that rollback deletes from receipt metadata
(`bridge/gtkb-rollback-receipts-001.md:114`). But the proposed execution flow
runs `git add -A` before committing the upgrade (`bridge/gtkb-rollback-receipts-001.md:87`).
Any non-ignored file created under `webapp/` by the upgrade will normally
become a tracked add in the upgrade commit, which is class C, not class I.

**Required action:**

- Define exactly which upgrade-created paths are intentionally not committed
  and why they survive branch checkout/merge safely.
- If class I remains in scope, add an execution-path test proving a
  non-committed, untracked upgrade-created file is recorded and removed without
  deleting adopter-created sibling files.
- Otherwise reclassify class I as class C for non-ignored files and reserve
  receipt-owned deletion metadata for ignored or deliberately excluded paths.

## Direct Answers To Open Questions

1. **Reflog expiry warning:** yes, but this is secondary. The implementation
   must first make rollback independent of reflog folklore by checking object
   existence and commit reachability every time. A doctor warning is useful for
   stale active receipts whose referenced objects are missing or no longer
   reachable from the current branch.
2. **Bare/non-git adopters:** require git for `upgrade --apply` and rollback.
   A no-receipt apply mode would violate the parent restore-capability
   condition. Whether `gt project init` itself requires git can remain a
   separate product decision, but `upgrade --apply` should fail loudly without
   a usable `.git`.
3. **Receipt tracking default:** tracking receipts is acceptable only after F2
   is fixed. The receipt path must not be blindly part of the merge-revert
   payload unless rollback explicitly protects and updates it.
4. **Destructive prompt:** yes. `--destructive` should require an interactive
   confirmation on a TTY, with a separate explicit non-interactive bypass flag
   for CI or scripted use.

## Required Revision

File `bridge/gtkb-rollback-receipts-003.md` as `REVISED` with:

1. Correct merge rollback semantics (`-m` mainline or a different topology).
2. A coherent receipt write/update/archive lifecycle that survives rollback.
3. Correct ignored-path cleanup semantics for reset mode.
4. A reconciled class-I story under `git add -A`.
5. Tests added to the catalog for merge-mainline revert, receipt preservation,
   ignored-path cleanup, and any intentionally untracked created file behavior.

No GT-KB rollback implementation should begin from `-001`.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw bridge/gtkb-rollback-receipts-001.md
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-002.md
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md
Get-Content -Raw bridge/gtkb-project-boundary-and-upgrade-hardening-002.md
rg -n "Rollback modes|git revert|merge_commit|write receipt|git add -A|Receipt JSON schema|Receipt storage location|Receipt tracking default|tracked or ignored|receipt never rolls back|Default adopter|clean-tree proof|reflog|reset --hard|partial rollback|Test Catalog|Post-Implementation Verification|Open Questions|Receipt file is moved" bridge/gtkb-rollback-receipts-001.md
git rev-parse --short HEAD
git status --short --branch
```

Temporary git reproductions:

```text
plain merge revert: RevertExit 128; "commit ... is a merge but no -m option was given"
ignored clean preview: git clean -fdn -> no output; git clean -fdxn -> "Would remove .gt-upgrade-staging/"
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
git status --short --branch
rg -n "project upgrade|--rollback|--destructive|rollback|dry-run|apply|force|dir" src/groundtruth_kb/cli.py
rg -n "\.bak|copy2|write_text|append-gitignore|scaffold_version|dry_run|apply|UpgradePlanner|UpgradeExecutor|shutil|backup|ProjectManifest|groundtruth\.toml" src/groundtruth_kb/project/upgrade.py
rg -n "rollback|upgrade|Receipt|receipt|\.bak|staging" tests src docs templates
python -m pytest tests/test_upgrade.py -q --tb=short
python -m pytest tests/test_upgrade_skills.py tests/test_gap_28_bridge_rule_repair.py -q --tb=short
python -m groundtruth_kb project upgrade --dry-run --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
```

Observed command results:

```text
GT-KB HEAD: e12aab3 on feature/ownership-matrix
GT-KB status: M src/groundtruth_kb/project/managed_registry.py; untracked .groundtruth-chroma/ and .implementation-log-harvest-coverage.md
tests/test_upgrade.py: 25 passed, 1 warning in 0.59s
tests/test_upgrade_skills.py + tests/test_gap_28_bridge_rule_repair.py: 17 passed, 1 warning in 0.82s
Agent Red dry-run: [SKIP] groundtruth.toml - No [project] manifest found - run `gt project init` first
```
