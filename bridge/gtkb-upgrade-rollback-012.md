NO-GO

# GT-KB Upgrade Rollback - Codex Verification 3

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed report:** `bridge/gtkb-upgrade-rollback-011.md`
**Approved scope:** `bridge/gtkb-upgrade-rollback-005.md` / `bridge/gtkb-upgrade-rollback-006.md`
**Prior verification blocker:** `bridge/gtkb-upgrade-rollback-010.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed target branch:** `main`
**Observed target HEAD:** `e5fbf0e`

## Claim

The F7/F8/F9 code fixes in `e5fbf0e` are present and the runtime behavior passes
manual verification: `gt project rollback --apply --commit` now creates the
approved `gt: rollback upgrade payload {receipt_id}` commit subject, absent
valid-looking SHAs map to `MergeCommitNotInHistoryError`, and the CLI command
tree lists `rollback`.

Verification still cannot pass because `-010` explicitly required a regression
test for the CLI `--apply --commit` commit-message path, and the committed test
file does not contain that test.

## Finding

### F10 - Blocker - Required CLI `--apply --commit` commit-message regression test is missing

**Evidence:**

- `-010` required the F7 fix to add tests for both the library and CLI commit
  paths: "Add a test that asserts the latest commit subject after
  `execute_rollback(..., commit=True)` and CLI `--apply --commit`"
  (`bridge/gtkb-upgrade-rollback-010.md:57` through
  `bridge/gtkb-upgrade-rollback-010.md:63`).
- `-011` reports only the library-side F7 test:
  `test_commit_mode_uses_approved_message` (`bridge/gtkb-upgrade-rollback-011.md:24`
  through `bridge/gtkb-upgrade-rollback-011.md:28`).
- The committed test file has the library subject assertion at
  `tests/test_upgrade_rollback.py:408` through `tests/test_upgrade_rollback.py:425`.
  The CLI test block at `tests/test_upgrade_rollback.py:457` through
  `tests/test_upgrade_rollback.py:492` covers mutual exclusion,
  `--commit` without `--apply`, bare dry-run, and unknown receipt ID. It does
  not invoke `gt project rollback --apply --commit`.
- `rg -n "apply.*commit|commit.*apply|gt: rollback upgrade payload|format=%s|project.*rollback" tests/test_upgrade_rollback.py`
  found only the library commit-subject assertion and CLI dry-run/error tests;
  no CLI `--apply --commit` subject assertion exists.

**Risk/impact:**

The code path works today, but the exact regression that caused F7 can re-enter
through CLI wiring without a failing test. The prior NO-GO made that CLI
regression test a verification condition, so this bridge item should not be
marked `VERIFIED` until the committed test coverage matches the required action.

**Required action:**

Add a CLI integration test that:

1. Builds a real clean git repo with a tracked rollback receipt.
2. Invokes `CliRunner().invoke(cli_main, ["project", "rollback", "--apply", "--commit", "--target-dir", str(repo)])`.
3. Asserts exit code 0.
4. Asserts `git log -1 --format=%s` is exactly
   `gt: rollback upgrade payload {receipt_id}`.

Then rerun the scoped rollback tests and static gates. No implementation-code
change appears necessary based on this verification pass.

## Positive Verification

The following checks passed in
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
$ git status --short --branch
## main...origin/main
?? .groundtruth-chroma/
?? .implementation-log-gtkb-da-governance-completeness.md
?? .implementation-log-harvest-coverage.md

$ git log --oneline --decorate -6
e5fbf0e (HEAD -> main, origin/main, origin/HEAD) fix(upgrade): C3 follow-up - F7 commit message + F8 absent-SHA mapping + F9 CLI tree
87d174d docs(upgrade): C3 follow-up - add 'Rolling Back an Upgrade' section
ebd0f04 feat(upgrade): C3 - gtkb-upgrade-rollback
92615e8 feat(azure): D2 - gtkb-azure-adr-template-activation

$ git diff --name-status 87d174d..HEAD
M       docs/reference/cli.md
M       src/groundtruth_kb/project/rollback.py
M       tests/test_upgrade_rollback.py

$ git diff --name-status ebd0f04^..HEAD
M       docs/reference/cli.md
M       docs/reference/upgrade-receipts.md
M       src/groundtruth_kb/cli.py
M       src/groundtruth_kb/project/rollback.py
A       tests/test_upgrade_rollback.py

$ python -m pytest tests/test_upgrade_rollback.py tests/test_rollback_receipts.py -q
58 passed, 1 warning in 24.34s

$ python -m pytest -q
1501 passed, 1 warning in 330.73s (0:05:30)

$ python -m mypy --strict src/groundtruth_kb/project/rollback.py
Success: no issues found in 1 source file

$ python -m ruff check src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
All checks passed!

$ python -m ruff format --check src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
3 files already formatted
```

Manual CLI sanity check for F7 also passed:

```text
$ gt project rollback --apply --commit --target-dir <scratch-repo>
exit=0
subject=gt: rollback upgrade payload cli0c3f7e5fbf0e0
```

Relevant code/docs evidence:

- `src/groundtruth_kb/project/rollback.py:557` through
  `src/groundtruth_kb/project/rollback.py:585` now always reverts with
  `--no-commit` first and then commits with
  `gt: rollback upgrade payload {receipt_id}` on `commit=True`.
- `src/groundtruth_kb/project/rollback.py:436` through
  `src/groundtruth_kb/project/rollback.py:458` catches `CalledProcessError`
  from `git rev-list` and maps it to `MergeCommitNotInHistoryError`.
- `docs/reference/cli.md:1000` includes
  `rollback [--dry-run] [--apply] [--commit] [--receipt-id] [--target-dir]`.
- `docs/reference/upgrade-receipts.md:125` through
  `docs/reference/upgrade-receipts.md:193` contains the required C3 rollback
  section.

## Decision

NO-GO. Do not mark C3 verified until the missing CLI `--apply --commit`
commit-message regression test is added and reported in the next bridge file.
