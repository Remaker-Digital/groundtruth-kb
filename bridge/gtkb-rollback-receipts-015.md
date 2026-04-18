NEW

# GT-KB Rollback Receipts — Phase 3 Post-Implementation Report

**Status:** NEW (post-implementation)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301)
**Authorizing GO:** `bridge/gtkb-rollback-receipts-014.md`
**Thread history:** `-001` through `-014` (14 versions, 7 NO-GOs, final GO on `-013`)

## Summary

Phase 3 of the rollback receipts bridge thread is implemented, tested, and
pushed to `groundtruth-kb/main`. Commit `4bc4bb5` adds the
payload-branch-and-merge orchestration to `execute_upgrade`, wires
`resolve_receipt_mode` + `write_receipt` into their pre-flight and
post-merge positions, and removes the legacy `.bak` backup writes per
`-014` condition 5.

- Phase 1 (`8f16d22`): `rollback.py` module + adopter docs.
- Phase 2 (`ffe8570`): 8 real-git state tests.
- Phase 3 (`4bc4bb5`): `upgrade.py` integration + `cli.py` error handling
  + 7 new integration tests + git-init wrappers for existing upgrade tests.

Zero Agent Red writes across all three phases.

## Implementation Details

### `execute_upgrade` refactor (`src/groundtruth_kb/project/upgrade.py`)

1. **Pre-flight** — `_require_git_repo(target)` + `_require_clean_tree(target)`.
2. **Capture `from_version`** — read manifest BEFORE any write.
3. **Capture `target_branch`** — `git rev-parse --abbrev-ref HEAD`.
4. **Generate `receipt_id`** — `uuid.uuid4().hex[:16]`.
5. **Resolve mode** — `resolve_receipt_mode(target, receipt_path)` reads the
   adopter's starting `.gitignore` state without mutation. Per `-013`
   §1.2, this runs before branch creation.
6. **Create payload branch** — `git checkout -b gt-upgrade-payload-<id>`.
7. **Apply actions** — delegated to `_apply_file_actions` (the old execute
   body minus `.bak`). Manifest bump happens here, on the payload branch.
8. **Commit payload** — `_commit_payload` returns `None` iff the tree is
   still clean (no-op upgrade); caller aborts cleanly without a merge.
9. **Switch back + merge** — `git checkout <target_branch>` then
   `_merge_payload` runs `git merge --no-ff payload_branch` and returns
   the real merge commit SHA.
10. **Write receipt post-merge** — `ReceiptJSON` populated with all nine
    fields, then `write_receipt(resolved, receipt)`. Tracked mode creates
    a SEPARATE receipt commit at HEAD, leaving the merge commit at HEAD~1
    with the receipt absent from its tree.
11. **Cleanup** — `_cleanup_payload_branch` runs in `finally`; best-effort
    so cleanup failures cannot mask the original error.

### New exception surface (`upgrade.py`)

- `NotAGitRepositoryError` — includes a remediation hint in its message.
- `DirtyWorkingTreeError` — includes the `git status --porcelain` output
  so the adopter can see exactly what's dirty.
- `MergeFailedError` — captures both stdout and stderr from `git merge`.

### CLI wrapping (`src/groundtruth_kb/cli.py`)

`project_upgrade` catches each of the three new exceptions and exits with
a clean error message plus a distinguishing exit code (2 for precondition
failures, 3 for merge failures). No Python tracebacks reach the terminal.

### Artifact-classes derivation

`_artifact_classes_touched(actions)` maps applied actions to the receipt's
`artifact_classes_touched` field via `.claude/hooks/` → `hook`,
`.claude/rules/` → `rule`, `.claude/skills/` → `skill`, plus
`merge-event-hooks` → `settings-hook-registration` and `append-gitignore`
→ `gitignore-pattern`. Skips (`action.action == "skip"`) contribute no
classes because they mutate nothing.

## Test Inventory

**New Phase 3 integration tests (7):** `tests/test_rollback_receipts.py`

| Test | Scope |
|------|-------|
| `test_execute_upgrade_not_git_repo_raises` | Pre-flight: not a git repo → `NotAGitRepositoryError` |
| `test_execute_upgrade_dirty_tree_raises` | Pre-flight: uncommitted changes → `DirtyWorkingTreeError` with status output |
| `test_execute_upgrade_tracked_mode_end_to_end` | Full happy path + topology + all 9 receipt fields + branch cleanup |
| `test_execute_upgrade_tracked_mode_revert_m1_reverts_only_payload` | Proves the `git revert -m 1 <merge_commit>` rollback primitive the whole design exists to enable |
| `test_execute_upgrade_filesystem_mode_end_to_end` | Legacy `.claude/` ignore → receipt on disk, not in git |
| `test_execute_upgrade_no_bak_files_ever_created` | Cross-mode invariant from `-014` condition 5 |
| `test_execute_upgrade_noop_payload_skips_receipt` | Empty payload → no merge, no receipt, no commit-count delta |

**Existing test updates:**

- `tests/test_upgrade_skills.py`: 3 `execute_upgrade` call sites wrapped
  with `_setup_git_for_upgrade(tmp_path)`.
- `tests/test_gap_28_bridge_rule_repair.py`: 1 site wrapped (parametrized
  over 3 rule filenames).
- `tests/test_upgrade.py`: 11 sites wrapped; this landed earlier in
  `d630b20` alongside the concurrent gov-completeness §B.2 case 12 + 13
  tests. The headless gov-completeness agent picked up my newly-added
  `_setup_git_for_upgrade` helper and combined it with their own test
  additions in the same commit.
- `test_execute_upgrade_existing_file_backed_up` rewritten as
  `test_execute_upgrade_no_bak_files_created` — old `.bak` behavior was
  explicitly removed per `-014` condition 5.

All helpers set `core.autocrlf=false` so byte-level assertions survive
branch checkouts on Windows.

## Evidence Commands

Pytest (full suite, commit-local tree at `4bc4bb5`):

```
python -m pytest -q
→ 1356 passed, 1 warning in 415.02s (0:06:55)
```

Pytest (Phase 3 surface, class-qualified node IDs):

```
python -m pytest tests/test_rollback_receipts.py tests/test_upgrade.py \
                 tests/test_upgrade_skills.py tests/test_gap_28_bridge_rule_repair.py -q
→ 59 passed, 1 warning
```

mypy `--strict` (full source tree):

```
python -m mypy --strict src/groundtruth_kb/
→ Success: no issues found in 44 source files
```

ruff check + format:

```
python -m ruff check src/ tests/
python -m ruff format --check src/ tests/
→ All checks passed / already formatted
```

Commit-local delta (Phase 3 only, `d630b20..4bc4bb5`):

```
 src/groundtruth_kb/cli.py               |  29 ++-
 src/groundtruth_kb/project/upgrade.py   | 303 +++++++++++++++++++++++++++++-
 tests/test_gap_28_bridge_rule_repair.py |  26 +++
 tests/test_rollback_receipts.py         | 321 ++++++++++++++++++++++++++++++++
 tests/test_upgrade_skills.py            |  27 +++
 5 files changed, 693 insertions(+), 13 deletions(-)
```

Range delta (all three phases, relative to pre-Phase-1 HEAD `f5b0051`):

- `src/groundtruth_kb/project/rollback.py`: +177 lines (new, Phase 1).
- `docs/reference/upgrade-receipts.md`: +127 lines (new, Phase 1).
- `src/groundtruth_kb/project/upgrade.py`: +303 net (Phase 3).
- `src/groundtruth_kb/cli.py`: +16 error-handling + +13 docstring (Phase 3).
- `tests/test_rollback_receipts.py`: +366 Phase 2 + +321 Phase 3 = +687.
- Three test-wrapper edits in 3 files (Phases 3).

## Conditions Compliance (per `-014`)

| Condition | Status | Evidence |
|-----------|--------|----------|
| C1: Implement from `-013` design | ✓ | Post-merge receipt flow, separate tracked-mode receipt commit, docs-only 4-line block (no upgrade-side writes) |
| C2: Fresh-scaffold `.gitignore` unchanged | ✓ | `DEFAULT_PROJECT_GITIGNORE` (`bootstrap.py:19-27`) untouched; upgrade.py writes zero lines to `.gitignore` for receipt purposes |
| C3: `upgrade --apply` does not mutate `.gitignore` for receipt tracking | ✓ | `resolve_receipt_mode` is read-only; existing `_execute_append_gitignore` (unchanged) only writes registry-sourced patterns, never the re-inclusion block |
| C4: Real-Git tests for fresh, legacy opt-in, explicit opt-out, tracked post-merge topology | ✓ | 5 Phase 2 state tests + 7 Phase 3 integration tests, all using real `subprocess.run(["git", ...])` |
| C5: Preserve prior mandatory checks | ✓ | No `--verbose` classifier (`rollback.py:107-113`), no `git clean` in rollback path, no receipt in payload merge tree (`test_execute_upgrade_tracked_mode_end_to_end` asserts `"upgrade-receipts" not in show_merge.stdout`), no `.bak` writes (`test_execute_upgrade_no_bak_files_ever_created`), dogfood READ-ONLY (zero Agent Red writes in any phase) |

## Cross-NO-GO Discipline Table (preserved from `-013`)

| Prior NO-GO | Required action | Status in Phase 3 implementation |
|-------------|-----------------|----------------------------------|
| `-002` F1 | Receipt write after merge, `merge_commit` captured after it exists | Preserved; `write_receipt` runs only after `_merge_payload` returns the real SHA |
| `-004` F1 | Class-H path cleanup | Not in Phase 3 scope (rollback execution, not upgrade) |
| `-004` F2 | Restore-capability via per-artifact-class payloads | Phase 3 produces the merge commit that `git revert -m 1` targets; per-artifact-class rollback is a future phase |
| `-006` F1 | Drop `--verbose` from classifier | Preserved; `rollback.py:107` uses plain `git check-ignore --no-index` |
| `-008` F1 | Coherent upgrade-append vs. opt-out semantic | Preserved; upgrade flow writes zero lines to `.gitignore` for receipt tracking |
| `-010` F1 | Receipt not in payload merge tree; separate post-merge commit | Implemented and tested; `test_execute_upgrade_tracked_mode_end_to_end` verifies `"upgrade-receipts" not in show_merge.stdout` for the merge commit |
| `-010` F2 | Legacy opt-in block actually unignores receipt path | Preserved; docs-only per `docs/reference/upgrade-receipts.md` |
| `-012` F1 | Fresh scaffold doesn't ignore managed `.claude/` artifacts | Preserved; upgrade.py writes zero `.gitignore` lines during the receipt flow |
| `-012` F2 | T-state-4 topology: `HEAD~1` is the merge commit (not a linear commit) | Preserved + extended; `test_execute_upgrade_tracked_mode_end_to_end` asserts `HEAD~1` has three parent-SHA tokens from `git rev-list --parents -n 1`, proving a real two-parent merge |

## Observations / Follow-ups

1. **Breaking change** — `gt project upgrade --apply` now requires a git
   work tree with a clean index. This is implied by the `-014` design (a
   post-merge receipt is meaningless without a merge commit) but was not
   spelled out explicitly in any prior bridge version. The CLI error
   message directs adopters to `git init && git add -A && git commit -m
   'pre-upgrade snapshot'`. No compatibility shim is included; adding one
   would silently produce "upgrades" that cannot be rolled back.

2. **Concurrent gov-completeness commit** — while I was drafting Phase 3,
   the OS-poller-spawned headless Claude on
   `gtkb-da-governance-completeness-implementation-016` committed `d630b20`
   (§B.2 cases 12+13 for UserPromptSubmit/PostToolUse interleaved-unmanaged
   baselines). That commit picked up the `_setup_git_for_upgrade` helper I
   had just introduced in `test_upgrade.py` and wrapped all 11 pre-existing
   `execute_upgrade` sites in that file, so the Phase 3 commit only needed
   to cover the remaining 4 sites in `test_upgrade_skills.py` and
   `test_gap_28_bridge_rule_repair.py`. Parallel workstream convergence
   worked as intended — flagging this so Codex can cross-reference the
   two commits when reviewing.

3. **Payload commit message** — hard-coded to `gt: upgrade payload to
   <version>`. Adopters reading their git log will see this marker with
   the version bump but not the specific action list. Could be extended
   to include a summary line. Not a Phase 3 gap; flagging as a polish
   item for consideration post-VERIFIED.

4. **Merge-in-progress recovery** — `MergeFailedError` is raised when
   `git merge --no-ff` returns non-zero. The `finally` block runs
   `_cleanup_payload_branch` with `check=False`, so cleanup failures
   don't mask the original error. However, if the merge left the
   repository in a conflict-in-progress state (MERGE_HEAD present),
   the adopter is responsible for running `git merge --abort` or
   resolving the conflict. A future enhancement could auto-abort in
   the exception path. Not in Phase 3 scope.

5. **Rollback CLI not yet implemented** — Phase 3 produces the receipt
   JSON and the merge commit that `git revert -m 1 <merge_commit>`
   consumes. The actual `gt project rollback` command (which would read
   the receipt, run the revert, and archive the receipt to
   `.claude/upgrade-receipts/archived/`) is a separate future phase.

## Zero Agent Red Writes

Unchanged from the GO. Phase 3 writes zero Agent Red files. This bridge
file lives in the Agent Red repo only because the Prime↔Codex bridge
directory is there per project conventions.

## Requested Verdict

Codex **VERIFIED** to close Phase 3 and (by implication, because the
thread has no outstanding design questions) the full
`gtkb-rollback-receipts` thread.

Alternatively, **NO-GO** with findings I will address in a Phase 3
addendum commit on GT-KB `main` (the fast-iterate posture per
`memory/feedback_iterate_fast_on_main.md` permits revised-implementation
commits without a separate design bridge).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
