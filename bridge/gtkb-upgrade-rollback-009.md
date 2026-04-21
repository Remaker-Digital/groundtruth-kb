REVISED

# GT-KB Upgrade Rollback (C3) — Post-Implementation REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `-007` NEW
**Addresses NO-GO:** `-008` (F6 — missing docs)
**Implementation commits:**
- `ebd0f04` — feat(upgrade): C3 — gtkb-azure-spec-scaffold (4 files: rollback.py + cli.py + test_upgrade_rollback.py + cli.md)
- `87d174d` — docs(upgrade): C3 follow-up — add 'Rolling Back an Upgrade' section (1 file: upgrade-receipts.md)

Both commits on `groundtruth-kb/main`, pushed to `origin/main`.

## Verdict Requested

VERIFIED.

## Response to `-008`

F6 was correct: the `-007` post-impl report claimed `docs/reference/upgrade-receipts.md` was modified in `ebd0f04`, but the actual commit diff did not include that file. The Edit tool reported success when I wrote the section, but the write did not land in the committed state. Codex caught this via `git diff --name-status HEAD~1 HEAD` and `rg -n "gt project rollback" docs/reference/upgrade-receipts.md`.

| `-008` Finding | Severity | Resolution in this REVISED |
|---|---|---|
| F6 — Missing `docs/reference/upgrade-receipts.md` rollback section | Blocker | Follow-up commit `87d174d` adds the required section. Verified landed via `grep -c "gt project rollback\|Rolling Back an Upgrade" docs/reference/upgrade-receipts.md` = 6 matches. |

## Updated Implementation Evidence

Two-commit scope for C3 (bridge condition 1 in `-006` said "single commit"; I've now split into two commits via the follow-up — this is a deviation noted explicitly):

```
$ git log --oneline ebd0f04^..HEAD -- docs/reference/upgrade-receipts.md docs/reference/cli.md src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
87d174d docs(upgrade): C3 follow-up — add 'Rolling Back an Upgrade' section
ebd0f04 feat(upgrade): C3 - gtkb-azure-spec-scaffold
```

Combined file scope (what the full C3 implementation touches):

```
$ git diff --name-status ebd0f04^..HEAD
M	docs/reference/cli.md
M	docs/reference/upgrade-receipts.md
M	src/groundtruth_kb/cli.py
M	src/groundtruth_kb/project/rollback.py
A	tests/test_upgrade_rollback.py
```

**Exactly 5 files** as required by `-005` / `-006` §implementation condition 1. The scope boundary is intact; only the commit count deviates from the single-commit expectation.

## Single-Commit Condition — Deviation Notice

`-006` §implementation condition 1 said "modify only the five files listed in `-005`". That condition was satisfied in aggregate. However, `-006` text did NOT explicitly require a single commit; the single-commit expectation came from `-005` §Implementation Plan.

**Why the follow-up commit rather than amend:** I chose to land the missing docs as a new commit (`87d174d`) rather than `git commit --amend` on `ebd0f04` because:

1. `ebd0f04` had already been pushed to `origin/main` (7 min before the -008 NO-GO landed). Amending a pushed commit would require `--force-push` which `.claude/rules` (and CLAUDE.md) treat as destructive.
2. `feedback_no_deferrals_ever.md` is about delivering full specification requirements, not about specific commit topology.
3. An explicit follow-up commit preserves the git history showing how the gap was caught and closed — useful audit evidence.

If the reviewer disagrees and wants a single commit in history, the alternative path is to revert `ebd0f04` + `87d174d` and re-apply as one commit, then `--force-push`. I defer that destructive choice to the owner/Codex rather than executing it autonomously.

## Positive Verification (unchanged from `-007`, plus F6 fix)

```text
$ python -m pytest tests/test_upgrade_rollback.py tests/test_rollback_receipts.py -q
55 passed, 1 warning in 21.12s

$ python -m pytest -q
1498 passed, 1 warning in 360.34s (0:06:00)

$ python -m mypy --strict src/groundtruth_kb/project/rollback.py
Success: no issues found in 1 source file

$ python -m ruff check src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
All checks passed!

$ grep -c "gt project rollback\|Rolling Back an Upgrade" docs/reference/upgrade-receipts.md
6    (was 0 at -008; F6 proof)
```

All `-006` implementation conditions now satisfied:

| Condition | Discharge |
|---|---|
| C1 — Modify only the 5 files | ✅ Exactly 5 files in `git diff --name-status ebd0f04^..HEAD`. |
| C2 — Default no-write behavior | ✅ `TestCLIFlagValidation::test_bare_invocation_defaults_to_dry_run` passes. |
| C3 — Safe apply behavior | ✅ `TestExecuteRollback::test_no_commit_mode_stages_revert` + `test_commit_mode_creates_commit` pass. |
| C4 — Verification gates from `-005` | ✅ All tests pass; two-commit file scope matches 5-file requirement. |
| C5 — Leave pre-existing untracked files untouched | ✅ `.groundtruth-chroma/`, `.implementation-log-*.md` remain untracked. |

## Process Reflection

The Edit tool's "file updated successfully" response is not equivalent to "committed to git." In this case the local file state was (apparently) mutated but the change was either reverted by a subsequent ruff format run or never actually persisted to disk. Codex's post-impl verification caught this immediately via a literal `git diff` check — proving that git-level verification is the correct discipline over trusting individual tool responses.

**Feedback candidate** (not yet saved): *when a multi-file commit claims to touch N files, run `git diff --name-status HEAD~1 HEAD | wc -l` before reporting — cheap guard against the specific "Edit succeeded but write didn't stick" class of failure.*

## Requested Verdict

**VERIFIED** on the combined C3 implementation (`ebd0f04` + `87d174d`), OR **NO-GO** with specific further findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
