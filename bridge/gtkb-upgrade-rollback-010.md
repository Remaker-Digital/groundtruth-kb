NO-GO

# GT-KB Upgrade Rollback - Codex Verification 2

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed report:** `bridge/gtkb-upgrade-rollback-009.md`
**Approved scope:** `bridge/gtkb-upgrade-rollback-005.md` / `bridge/gtkb-upgrade-rollback-006.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed target branch:** `main`
**Observed target HEAD:** `87d174d`

## Claim

The F6 documentation gap from `-008` is fixed: `docs/reference/upgrade-receipts.md`
now contains the required rollback section, and the combined C3 implementation
touches exactly the five approved files.

Verification still cannot pass. The implemented `--commit` path does not use the
approved auto-commit message, and a syntactically valid but nonexistent receipt
SHA leaks a raw `CalledProcessError` instead of returning one of the documented
rollback errors.

## Findings

### F7 - Blocker - `--commit` does not create the approved commit message

**Evidence:**

- `-005` specified that `--apply --commit` auto-commits with message
  `"gt: rollback upgrade payload {receipt_id}"` (`bridge/gtkb-upgrade-rollback-005.md:54`).
- The shipped CLI help and docs repeat that contract:
  `src/groundtruth_kb/cli.py:801` through `src/groundtruth_kb/cli.py:806`,
  `docs/reference/upgrade-receipts.md:136` through
  `docs/reference/upgrade-receipts.md:137`, and `docs/reference/cli.md:463`
  through `docs/reference/cli.md:464`.
- The implementation runs plain `git revert -m 1 <merge_commit>` when
  `commit=True`; it appends `--no-commit` only when `commit=False`, and never
  supplies a custom commit message (`src/groundtruth_kb/project/rollback.py:543`
  through `src/groundtruth_kb/project/rollback.py:566`).
- A scratch real-git execution of `execute_rollback(root, plan, commit=True)`
  produced:

```text
commit_sha=5420f6ff666fe576b64d15ee46b6d4109d65c44e
subject=Revert "merge payload"
```

**Risk/impact:**

The public contract and docs say automated rollback commits are machine-readable
as `gt: rollback upgrade payload {receipt_id}`. The actual commits get Git's
default `Revert "..."` subject, so audit trails and automation cannot reliably
identify C3 rollback commits by the documented message.

**Required action:**

Change the commit path so `commit=True` creates exactly
`gt: rollback upgrade payload {receipt_id}`. One safe implementation is to run
the revert with `--no-commit` and then run `git commit -m ...`, preserving the
existing `commit=False` behavior. Add a test that asserts the latest commit
subject after `execute_rollback(..., commit=True)` and CLI `--apply --commit`.

### F8 - Blocker - Missing/nonexistent merge commits leak `CalledProcessError`

**Evidence:**

- `-005` requires documented error handling for rollback failures including
  `NotAMergeCommitError` and `MergeCommitNotInHistoryError`
  (`bridge/gtkb-upgrade-rollback-005.md:102`).
- `plan_rollback()` calls `_assert_is_two_parent_merge()` before
  `_assert_merge_commit_reachable()` (`src/groundtruth_kb/project/rollback.py:485`
  through `src/groundtruth_kb/project/rollback.py:508`).
- `_assert_is_two_parent_merge()` runs
  `git rev-list --parents -n 1 <merge_commit>` with `check=True`
  (`src/groundtruth_kb/project/rollback.py:436` through
  `src/groundtruth_kb/project/rollback.py:443`). If the receipt contains a
  40-character lowercase hex SHA that is not an object in the repo, the raw
  subprocess exception escapes before any documented rollback exception is
  raised.
- A scratch receipt using `merge_commit = "a" * 40` produced:

```text
CalledProcessError
Command '['git', 'rev-list', '--parents', '-n', '1', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']' returned non-zero exit status 128.
```

**Risk/impact:**

A corrupt or stale receipt can crash the CLI/library path with an internal
subprocess error instead of the documented adopter-facing error and exit-code
contract. This contradicts the proposal's receipt-consumption safety gates and
leaves a common corruption mode untested.

**Required action:**

Handle nonexistent or unreadable receipt SHAs explicitly. Acceptable fixes:

1. Check reachability/existence before parent-shape validation and map failures
   to `MergeCommitNotInHistoryError`; or
2. Catch `subprocess.CalledProcessError` from `rev-list` and raise a documented
   rollback exception with a clear message.

Add tests for a valid-looking 40-character SHA that is absent from the repo,
covering both the library API and CLI exit behavior.

### F9 - Medium - CLI command tree omits the new rollback command

**Evidence:**

- The new command exists at `src/groundtruth_kb/cli.py:781` and is documented in
  the Project Commands section at `docs/reference/cli.md:450`.
- The CLI command tree near the bottom of the same reference still lists only
  `init`, `doctor`, and `upgrade` under `project`; it omits `rollback`
  (`docs/reference/cli.md:995` through `docs/reference/cli.md:1000`).

**Risk/impact:**

The command reference is internally inconsistent: one section documents
`gt project rollback`, while the summary tree suggests it does not exist.

**Required action:**

Update the command tree to include
`rollback [--dry-run] [--apply] [--commit] [--receipt-id] [--target-dir]`.

## Positive Verification

The following checks passed in
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
$ git log --oneline --decorate -5
87d174d (HEAD -> main, origin/main, origin/HEAD) docs(upgrade): C3 follow-up - add 'Rolling Back an Upgrade' section
ebd0f04 feat(upgrade): C3 - gtkb-upgrade-rollback
92615e8 feat(azure): D2 - gtkb-azure-adr-template-activation

$ git diff --name-status ebd0f04^..HEAD
M       docs/reference/cli.md
M       docs/reference/upgrade-receipts.md
M       src/groundtruth_kb/cli.py
M       src/groundtruth_kb/project/rollback.py
A       tests/test_upgrade_rollback.py

$ rg -n "Rolling Back an Upgrade|gt project rollback|plan_rollback|execute_rollback" docs/reference/upgrade-receipts.md
125:## Rolling Back an Upgrade (C3)
130:gt project rollback [--dry-run | --apply] [--commit] [--receipt-id <id>]
180:    find_latest_receipt, plan_rollback, execute_rollback,

$ python -m pytest tests/test_upgrade_rollback.py tests/test_rollback_receipts.py -q
55 passed, 1 warning in 22.79s

$ python -m mypy --strict src/groundtruth_kb/project/rollback.py
Success: no issues found in 1 source file

$ python -m ruff check src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
All checks passed!

$ python -m ruff format --check src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
3 files already formatted
```

Pre-existing untracked files remain untracked:

```text
?? .groundtruth-chroma/
?? .implementation-log-gtkb-da-governance-completeness.md
?? .implementation-log-harvest-coverage.md
```

The two-commit implementation shape is not a blocker by itself. The aggregate
scope is exactly the approved five files, and avoiding an amend/force-push after
`ebd0f04` was already pushed is reasonable.

## Decision

NO-GO. Do not mark C3 verified until F7 and F8 are fixed, tests are added for
both behaviors, and the CLI command tree is updated.
