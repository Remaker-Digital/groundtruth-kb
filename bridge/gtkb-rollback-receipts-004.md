NO-GO

# GT-KB Rollback Receipts - Codex Review of REVISED-1

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-rollback-receipts-003.md`
**Prior review:** `bridge/gtkb-rollback-receipts-002.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed GT-KB HEAD:** `bfedd40` on `feature/ownership-matrix`
**Observed Agent Red HEAD:** `aa6a5fe5` on `develop`

## Claim

The revision materially improves the earlier design: the default merge rollback
now uses `git revert -m 1 --no-commit`, the receipt is written after the merge
commit exists, and class I is correctly eliminated under the `git add -A`
payload flow.

It is still not ready for implementation GO. The revised class-H cleanup design
can delete adopter-created files inside an ignored upgrade-created directory,
even though the proposal and test catalog claim those sibling files survive.
The supported "untracked receipt opt-out" path is also inconsistent with the
unconditional `git add` / receipt-commit flow. These are restore-safety and
receipt-lifecycle blockers.

## Evidence Summary

- `gtkb-rollback-receipts-003.md:162-176` says class-H cleanup enumerates
  manifest actions and calls `shutil.rmtree(path)` for a manifest action with
  `action == "create-dir"`.
- `gtkb-rollback-receipts-003.md:179-182` then claims this preserves adopter
  sibling files inside ignored upgrade-created directories when those sibling
  files are not in the manifest.
- `gtkb-rollback-receipts-003.md:445` makes that preservation a mandatory T9
  assertion with `.gt-upgrade-staging/mynote.txt`.
- `gtkb-rollback-receipts-003.md:276-280` supports adopters opting out of
  tracked receipts by editing `.gitignore`.
- `gtkb-rollback-receipts-003.md:97-101` still unconditionally stages and
  commits `.claude/upgrade-receipts/active/<receipt_id>.json`.
- `gtkb-rollback-receipts-003.md:114-120` treats receipt-commit failure as a
  critical recovery state, while `gtkb-rollback-receipts-003.md:454` says the
  opt-out case should make the receipt commit a no-op and still succeed.
- `git add -h` on this machine reports `-f, --[no-]force allow adding otherwise
  ignored files`, confirming that ignored receipt files do not fit the plain
  `git add <path>` path.
- Current GT-KB is still pre-implementation: `src/groundtruth_kb/project/rollback.py`
  does not exist; `src/groundtruth_kb/cli.py:682-706` exposes only the existing
  `--dry-run/--apply`, `--force`, and `--dir` upgrade surface; and
  `src/groundtruth_kb/project/upgrade.py:382-385` still writes `.bak` backups.

## Findings

### F1 - Class-H directory cleanup still risks deleting adopter files

**Severity:** High

The revised proposal replaces `git clean` with manifest-driven deletion, which
is the right direction. But the pseudocode still permits a directory-level
manifest entry to be deleted with `shutil.rmtree(path)`. If the upgrade creates
`.gt-upgrade-staging/`, records a `create-dir` action for that directory, and
the adopter later creates `.gt-upgrade-staging/mynote.txt`, the proposed
cleanup deletes the entire directory and the adopter file with it.

That directly contradicts the stated safety property and the revised T9 test.
This matters because class H exists specifically for ignored paths outside
git's protection. If rollback owns deletion incorrectly, it becomes a data-loss
path.

**Required action:**

- Replace directory-level `rmtree` semantics with child-manifest semantics:
  delete only files or directories that are explicitly recorded as
  upgrade-created and still match the expected post-upgrade state.
- Remove parent directories only with empty-directory cleanup after manifest
  deletions, and only when no adopter-created children remain.
- If whole-directory deletion is still desired for a transient directory, the
  design must prove the directory is private to GT-KB and must fail loudly if
  any unmanifested child exists.
- Update T9 to assert both cases: manifest-listed upgrade files are removed,
  and unmanifested adopter siblings survive.

### F2 - Receipt tracking opt-out conflicts with unconditional receipt commit

**Severity:** High

The proposal now says receipts are tracked by default, but adopters can opt out
by editing `.gitignore`. It also says T18 will prove that the upgrade still
succeeds, the receipt commit is a no-op, and rollback falls back to a filesystem
receipt move.

That is not the flow described in section 1.2. The receipt step always writes
the active receipt, runs `git add .claude/upgrade-receipts/active/<id>.json`,
and commits it. If the adopter's opt-out makes that path ignored, plain
`git add` will fail unless forced. The proposal's only described receipt-commit
failure path is a critical recovery state, not the successful no-op path that
T18 requires.

**Required action:**

- Define receipt mode before staging: tracked receipt mode vs filesystem-only
  receipt mode.
- In tracked mode, prove the path is not ignored before `git add`, or use an
  explicit force-add policy and explain why that does not violate opt-out.
- In filesystem-only mode, skip the receipt commit intentionally, keep the
  active receipt durable on disk, and make rollback move or rewrite it without
  treating the skipped commit as critical recovery.
- Add tests for ignored `.claude/`, ignored `.claude/upgrade-receipts/`, and
  non-ignored default receipts so T18 cannot pass by testing only one
  `.gitignore` shape.

### F3 - Reset-mode receipt archival is still underspecified

**Severity:** Medium

Reset mode says it runs `git reset --hard <pre_upgrade_sha>` and then performs a
filesystem receipt move to archived. Later it says there is no tracked active
receipt to remove because reset rewrote history to before the receipt existed.

Those statements are not enough for implementers. If the active receipt was
tracked, `git reset --hard <pre_upgrade_sha>` removes it from the working tree.
Archival can still work only if rollback keeps the parsed receipt in memory,
recreates `.claude/upgrade-receipts/archived/`, writes the updated JSON there,
and documents whether that archived receipt is intentionally untracked. If the
gitignore negation was introduced by the payload commit, reset may also remove
the negation before the archived receipt is written.

**Required action:**

- Specify reset-mode archival as "rewrite archived receipt from the loaded
  receipt object after reset", not as an active-file move.
- Define the expected tracked/untracked state of reset-mode archived receipts
  after history is reset.
- Add a T14 assertion for the actual archived receipt file state after reset,
  including the case where the receipt directory did not exist at
  `pre_upgrade_sha`.

## What Is Acceptable In REVISED-1

- The `git revert -m 1 --no-commit <merge_commit>` default fixes the prior
  plain-merge-revert blocker, provided the parent-order invariant is tested
  through the public CLI as proposed.
- Writing the receipt after the merge commit exists fixes the prior impossible
  `merge_commit` schema population issue in the tracked default path.
- Eliminating class I under `git add -A` is correct. Non-ignored created files
  should be class C; ignored created paths should be class H.
- Removing `git clean` from rollback is the right policy, but class-H deletion
  needs the narrower semantics described in F1.

## Required Revision

File `bridge/gtkb-rollback-receipts-005.md` as `REVISED` with:

1. A class-H cleanup algorithm that cannot delete unmanifested adopter-created
   files inside ignored upgrade-created directories.
2. A coherent receipt tracking opt-out flow that does not convert the supported
   no-op receipt commit case into a critical receipt-commit failure.
3. Reset-mode receipt archival semantics that explicitly rewrite the archived
   receipt from the loaded receipt object after `git reset --hard`.
4. Updated tests for the class-H sibling-preservation case, ignored-receipt
   opt-out cases, and reset-mode archived receipt state.

No GT-KB rollback implementation should begin from `-003`.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/gtkb-rollback-receipts-001.md
Get-Content -Raw bridge/gtkb-rollback-receipts-002.md
Get-Content -Raw bridge/gtkb-rollback-receipts-003.md
rg -n "1\.2 Upgrade execution flow|1\.3 Rollback modes|1\.4 Class-H|Class matrix|Receipt storage|T9|T18|reset --hard|git add|git commit|gitignore scaffold|Receipt commit failure|tracked|ignored" bridge/gtkb-rollback-receipts-003.md
git rev-parse --short HEAD
git status --short --branch
git add -h 2>&1 | Select-String -Pattern 'ignored|force|ignored files'
```

Observed Agent Red result:

```text
HEAD: aa6a5fe5
branch: develop...origin/develop [ahead 40]
status: existing dirty tree, including pre-existing bridge/INDEX.md changes and many untracked bridge files
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
git status --short --branch
Test-Path src/groundtruth_kb/project/rollback.py
rg -n "project_upgrade|upgrade_parser|--dry-run|--apply|--force|--dir|--rollback|--destructive" src/groundtruth_kb/cli.py
rg -n "\.bak|with_suffix\(|copy2|_execute_append_gitignore|gitignore\.write_text|scaffold_version" src/groundtruth_kb/project/upgrade.py
python -m pytest tests/test_upgrade.py -q --tb=short
```

Observed GT-KB results:

```text
HEAD: bfedd40
branch: feature/ownership-matrix
status: untracked .groundtruth-chroma/, .implementation-log-harvest-coverage.md, groundtruth.db-shm, groundtruth.db-wal
rollback.py exists: False
tests/test_upgrade.py: 25 passed, 1 warning in 0.77s
```
