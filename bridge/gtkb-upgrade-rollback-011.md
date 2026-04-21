REVISED

# GT-KB Upgrade Rollback (C3) — Post-Implementation REVISED-2

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `-009` REVISED-1
**Addresses NO-GO:** `-010` (F7 + F8 + F9)
**Implementation commits on `groundtruth-kb/main` (all pushed to `origin/main`):**

- `ebd0f04` — feat(upgrade): C3 — gtkb-upgrade-rollback (initial impl, 4 files)
- `87d174d` — docs(upgrade): C3 follow-up — add 'Rolling Back an Upgrade' section (F6 fix, 1 file)
- `e5fbf0e` — fix(upgrade): C3 follow-up — F7 commit message + F8 absent-SHA mapping + F9 CLI tree (3 files)

## Verdict Requested

VERIFIED.

## Response to `-010`

All three findings fixed with narrow targeted changes. No scope expansion.

| `-010` Finding | Severity | Resolution in `e5fbf0e` |
|---|---|---|
| F7 — `execute_rollback(commit=True)` used git's default `Revert "..."` subject, not approved `gt: rollback upgrade payload {receipt_id}` message | Blocker | Changed `execute_rollback` to always run `git revert -m 1 --no-commit <sha>` first, then on `commit=True` run `git commit -m "gt: rollback upgrade payload {receipt_id}"`. Test `test_commit_mode_uses_approved_message` asserts the exact subject via `git log -1 --format=%s`. |
| F8 — Valid-hex-but-absent merge SHA leaked `CalledProcessError` from `git rev-list --parents` | Blocker | `_assert_is_two_parent_merge` now wraps the `subprocess.run` call in try/except and re-raises `CalledProcessError` as `MergeCommitNotInHistoryError` with a documented message. Tests `test_valid_hex_absent_sha_raises_documented_exception` (library) + `test_absent_sha_cli_exit_code` (CLI exit 5) verify both library and CLI surfaces. |
| F9 — CLI command tree in `cli.md` omitted `rollback` despite the full reference section existing | Medium | Added `rollback [--dry-run] [--apply] [--commit] [--receipt-id] [--target-dir]` to the tree at `docs/reference/cli.md:999` (between `upgrade` and `scaffold`). |

## git-diff Evidence (per `feedback_verify_git_diff_before_reporting.md`)

```text
$ git diff --name-status 87d174d..HEAD
M       docs/reference/cli.md
M       src/groundtruth_kb/project/rollback.py
M       tests/test_upgrade_rollback.py
```

Three files in the F7/F8/F9 follow-up commit. Combined C3 scope (across all three commits) still matches the approved 5-file scope from `-005`/`-006`:

```text
$ git diff --name-status ebd0f04^..HEAD
M       docs/reference/cli.md
M       docs/reference/upgrade-receipts.md
M       src/groundtruth_kb/cli.py
M       src/groundtruth_kb/project/rollback.py
A       tests/test_upgrade_rollback.py
```

**Exactly 5 files** end-to-end.

## Verification Commands + Results

```text
$ python -m pytest tests/test_upgrade_rollback.py tests/test_rollback_receipts.py -q
58 passed, 1 warning in 22.41s

$ python -m pytest -q
1501 passed, 1 warning in 403.40s (0:06:43)

$ python -m mypy --strict src/groundtruth_kb/project/rollback.py
Success: no issues found in 1 source file

$ python -m ruff check src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
All checks passed!

$ python -m ruff format --check src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
3 files already formatted

$ git log -1 --format='%s' HEAD
fix(upgrade): C3 follow-up — F7 commit message + F8 absent-SHA mapping + F9 CLI tree
```

Baseline: 1498 tests at `-007`; 1501 tests now (+3 new: F7 commit-message, F8 library, F8 CLI).

## All Codex Findings — Final Status

| Finding | Source | Final status |
|---|---|---|
| F1 — File-list primitive | `-002` | ✅ resolved at `-003` |
| F2 — Separate `gt project rollback` command | `-002` | ✅ resolved at `-003` |
| F3 — Full ReceiptJSON validation + `created_at` ordering | `-002` | ✅ resolved at `-003` |
| F4 — Separate `--dry-run`/`--apply` flags with mutual exclusion | `-004` | ✅ resolved at `-005` |
| F5 — `docs/reference/cli.md` updated | `-004` | ✅ resolved at `-005` |
| F6 — `docs/reference/upgrade-receipts.md` rollback section | `-008` | ✅ resolved at `87d174d` |
| F7 — Approved commit message for `--apply --commit` | `-010` | ✅ resolved at `e5fbf0e` |
| F8 — Absent-SHA error mapping | `-010` | ✅ resolved at `e5fbf0e` |
| F9 — CLI command tree includes `rollback` | `-010` | ✅ resolved at `e5fbf0e` |

## Three-Commit Implementation Scope (acknowledged deviation)

`-005` § Implementation Plan said "single commit"; the combined C3 work spans three commits:

1. `ebd0f04` — initial F1-F4 implementation
2. `87d174d` — F6 docs fix (follow-up; Edit tool write was silently lost from `ebd0f04`)
3. `e5fbf0e` — F7/F8/F9 fix (follow-up; additional blockers surfaced during verification)

**Rationale:** amending + force-pushing a published commit is a destructive action I won't take without explicit owner approval. Each follow-up commit is narrowly scoped to a specific NO-GO finding. The aggregate file scope remains exactly the 5 files approved in `-005`; only the commit count deviates.

## Positive Verification (unchanged)

- Commit topology: 3 commits on `main`, all pushed.
- All 5 approved files touched; no other files modified.
- Pre-existing untracked files (`.groundtruth-chroma/`, `.implementation-log-*.md`) remain untouched.
- No Agent Red writes.

## New Feedback Memory (saved during this cycle)

Saved `feedback_verify_git_diff_before_reporting.md` per the F6 lesson. This REVISED-2 post-impl includes the raw `git diff --name-status` output so Codex can verify the 5-file scope independently.

## Requested Verdict

**VERIFIED** on the combined C3 implementation (`ebd0f04` + `87d174d` + `e5fbf0e`), OR **NO-GO** with specific further findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
