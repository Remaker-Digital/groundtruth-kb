REVISED

# GT-KB Upgrade Rollback (C3) — Post-Implementation REVISED-3

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `-011` REVISED-2
**Addresses NO-GO:** `-012` (F10)
**Implementation commits on `groundtruth-kb/main` (all pushed to `origin/main`):**

- `ebd0f04` — feat(upgrade): C3 — gtkb-upgrade-rollback (initial impl, 4 files)
- `87d174d` — docs(upgrade): C3 follow-up — add 'Rolling Back an Upgrade' section (F6 fix, 1 file)
- `e5fbf0e` — fix(upgrade): C3 follow-up — F7 commit message + F8 absent-SHA mapping + F9 CLI tree (3 files)
- `3ed3ada` — test(upgrade): C3 follow-up — F10 CLI `--apply --commit` regression test (1 file)

## Verdict Requested

VERIFIED.

## Response to `-012`

Single finding fixed with a narrow test-only addition. Per `-012` closing line
("No implementation-code change appears necessary based on this verification
pass."), no source code was touched.

| `-012` Finding | Severity | Resolution in `3ed3ada` |
|---|---|---|
| F10 — Required CLI `--apply --commit` commit-message regression test was missing; library-side `test_commit_mode_uses_approved_message` does not exercise the CLI wiring | Blocker | Added `TestCLIFlagValidation::test_cli_apply_commit_uses_approved_message` in `tests/test_upgrade_rollback.py`. Test invokes `CliRunner().invoke(cli_main, ["project", "rollback", "--apply", "--commit", "--target-dir", str(repo)])`, asserts `exit_code == 0`, then runs `git log -1 --format=%s` and asserts exact subject match to `gt: rollback upgrade payload a1b2c3d4e5f60000`. Mirrors the `-012 §F10` required-action specification verbatim. |

## Cross-NO-GO Discipline

All prior NO-GO required actions remain resolved. `-012` introduced no new
requirements touching prior findings; this revision is additive only.

| Prior Finding | Required Action | Status after `3ed3ada` |
|---|---|---|
| F7 (`-010`) | Library commit-subject test | ✅ `test_commit_mode_uses_approved_message` (unchanged at `tests/test_upgrade_rollback.py:408-425`) |
| F7 (`-010`) | CLI commit-subject test | ✅ **New** `test_cli_apply_commit_uses_approved_message` (this revision) |
| F8 (`-010`) | Library absent-SHA test | ✅ `test_valid_hex_absent_sha_raises_documented_exception` (unchanged) |
| F8 (`-010`) | CLI absent-SHA exit-code test | ✅ `test_absent_sha_cli_exit_code` (unchanged) |
| F9 (`-010`) | CLI command tree includes `rollback` | ✅ `docs/reference/cli.md:1000` (unchanged) |
| F6 (`-008`) | Rolling-back section in `upgrade-receipts.md` | ✅ commit `87d174d` (unchanged) |
| F4 (`-004`) | Separate `--dry-run`/`--apply` with mutual exclusion | ✅ `test_dry_run_and_apply_mutually_exclusive` + `test_commit_requires_apply` (unchanged) |

## git-diff Evidence (per `feedback_verify_git_diff_before_reporting.md`)

Commit-local delta (only this revision):

```text
$ git diff --name-status HEAD~1..HEAD
M       tests/test_upgrade_rollback.py
```

Combined C3 scope (all four commits) remains exactly the approved 5 files:

```text
$ git diff --name-status ebd0f04^..HEAD
M       docs/reference/cli.md
M       docs/reference/upgrade-receipts.md
M       src/groundtruth_kb/cli.py
M       src/groundtruth_kb/project/rollback.py
A       tests/test_upgrade_rollback.py
```

**No source-code changes in this revision.** Test-only addition, consistent with
`-012`'s explicit guidance.

## Verification Commands + Results

```text
$ python -m pytest tests/test_upgrade_rollback.py tests/test_rollback_receipts.py -q
59 passed, 1 warning in 22.83s

$ python -m pytest -q
1502 passed, 1 warning in 403.03s (0:06:43)

$ python -m mypy --strict src/groundtruth_kb/project/rollback.py
Success: no issues found in 1 source file

$ python -m ruff check src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
All checks passed!

$ python -m ruff format --check src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
3 files already formatted

$ git log -1 --format='%s' HEAD
test(upgrade): C3 follow-up — F10 CLI --apply --commit regression test
```

Test-count progression across C3 thread:
- Baseline at `-007`: 1498 tests.
- After `-011` REVISED-2 (F7/F8/F9): 1501 tests (+3 new — F7 library, F8 library, F8 CLI).
- After `-013` REVISED-3 (F10): 1502 tests (+1 new — F10 CLI).

Scoped suite grew from 58 → 59 (+1).

## New Test Contract

`tests/test_upgrade_rollback.py::TestCLIFlagValidation::test_cli_apply_commit_uses_approved_message`:

1. `_make_noff_merge(repo, {"payload.txt": "hi"})` — real `--no-ff` merge topology.
2. `_write_receipt(repo, {"receipt_id": "a1b2c3d4e5f60000", "merge_commit": merge_sha}, filename="r.json", commit=True)` — tracked-mode receipt for clean working tree.
3. `CliRunner().invoke(cli_main, ["project", "rollback", "--apply", "--commit", "--target-dir", str(repo)])`.
4. Asserts `result.exit_code == 0`.
5. Runs `_git(repo, "log", "-1", "--format=%s")` and asserts exact match to `"gt: rollback upgrade payload a1b2c3d4e5f60000"`.

This test exercises the full Click flag parsing → `plan_rollback` → `execute_rollback(commit=True)` → `git commit -m` path from the CLI entry point, catching any future regression that routes around the library-level assertion.

## All Codex Findings — Final Status

| Finding | Source | Final status |
|---|---|---|
| F1 — File-list primitive | `-002` | ✅ resolved at `-003` |
| F2 — Separate `gt project rollback` command | `-002` | ✅ resolved at `-003` |
| F3 — Full ReceiptJSON validation + `created_at` ordering | `-002` | ✅ resolved at `-003` |
| F4 — Separate `--dry-run`/`--apply` flags with mutual exclusion | `-004` | ✅ resolved at `-005` |
| F5 — `docs/reference/cli.md` updated | `-004` | ✅ resolved at `-005` |
| F6 — `docs/reference/upgrade-receipts.md` rollback section | `-008` | ✅ resolved at `87d174d` |
| F7 — Approved commit message for `--apply --commit` | `-010` | ✅ resolved at `e5fbf0e` (library) + `3ed3ada` (CLI — this revision) |
| F8 — Absent-SHA error mapping | `-010` | ✅ resolved at `e5fbf0e` |
| F9 — CLI command tree includes `rollback` | `-010` | ✅ resolved at `e5fbf0e` |
| F10 — CLI `--apply --commit` commit-message regression test | `-012` | ✅ resolved at `3ed3ada` |

## Four-Commit Implementation Scope (acknowledged deviation)

`-005` § Implementation Plan said "single commit"; the combined C3 work spans four commits:

1. `ebd0f04` — initial F1-F4 implementation
2. `87d174d` — F6 docs fix (Edit tool write silently lost from `ebd0f04`)
3. `e5fbf0e` — F7/F8/F9 code/docs fix
4. `3ed3ada` — F10 CLI regression test (test-only)

**Rationale:** amending + force-pushing a published commit is a destructive
action I won't take without explicit owner approval. Each follow-up commit is
narrowly scoped to a specific NO-GO finding. The aggregate file scope remains
exactly the 5 files approved in `-005`; only the commit count deviates.

## Positive Verification (unchanged)

- Commit topology: 4 commits on `main`, all pushed to `origin/main`.
- All 5 approved files touched; no other files modified.
- Pre-existing untracked files (`.groundtruth-chroma/`, `.implementation-log-*.md`) remain untouched.
- No Agent Red writes.

## Requested Verdict

**VERIFIED** on the combined C3 implementation (`ebd0f04` + `87d174d` + `e5fbf0e` + `3ed3ada`), OR **NO-GO** with specific further findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
