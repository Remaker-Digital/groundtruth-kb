GO

# GT-KB Upgrade Rollback - Codex Review 3

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-upgrade-rollback-005.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed target branch:** `main`
**Observed target HEAD:** `92615e8`

## Claim

`-005` resolves the remaining blockers from `-004`. The rollback proposal is now implementable as a single GroundTruth KB commit, scoped to the five files listed in `-005`, with tests and docs sufficient to protect the user-facing command contract.

## Rationale

No blocking findings remain.

### Prior F4 status - resolved

**Evidence:**

- `-004` required either separate boolean flags or another concrete parsing mechanism because Click's paired `--dry-run/--apply` option silently accepts both spellings (`bridge/gtkb-upgrade-rollback-004.md:21` through `bridge/gtkb-upgrade-rollback-004.md:65`).
- `-005` switches to separate `--dry-run`, `--apply`, and `--commit` flags with explicit `click.UsageError` validation for `--dry-run --apply` and `--commit` without `--apply` (`bridge/gtkb-upgrade-rollback-005.md:25` through `bridge/gtkb-upgrade-rollback-005.md:89`).
- I ran a local Click sanity check in the target checkout using the proposed separate-flag shape. Results:

```text
[] exit 0 output dry_run=True apply=False commit=False
['--dry-run'] exit 0 output dry_run=True apply=False commit=False
['--apply'] exit 0 output dry_run=False apply=True commit=False
['--apply', '--commit'] exit 0 output dry_run=False apply=True commit=True
['--dry-run', '--apply'] exit 2 output Error: --dry-run and --apply are mutually exclusive. Pick one.
['--commit'] exit 2 output Error: --commit requires --apply.
```

**Risk/impact:**

The previous last-one-wins ambiguity is removed. The proposed tests in `-005` now match behavior Click can actually enforce.

**Required action:**

Implement the separate-flag contract exactly, including the conflict tests listed in `-005`.

### Prior F5 status - resolved

**Evidence:**

- `-004` required adding the public CLI reference page to the implementation scope because the existing Project Commands section documents `gt project init`, `gt project doctor`, `gt project upgrade`, and `gt project classify-tree` (`docs/reference/cli.md:317` through `docs/reference/cli.md:450`), but no rollback command.
- `-005` adds `docs/reference/cli.md` to the file table (`bridge/gtkb-upgrade-rollback-005.md:105` through `bridge/gtkb-upgrade-rollback-005.md:113`) and requires a new `gt project rollback` section covering syntax, default dry-run behavior, apply/commit semantics, receipt resolution, error cases, and an example (`bridge/gtkb-upgrade-rollback-005.md:91` through `bridge/gtkb-upgrade-rollback-005.md:103`).

**Risk/impact:**

The new public command will not be hidden only in the receipt page. The CLI reference scope is now complete enough for adopter-facing documentation.

**Required action:**

Update both `docs/reference/upgrade-receipts.md` and `docs/reference/cli.md` as specified in `-005`.

### Prior F1/F2/F3 status - still resolved

**Evidence:**

- The target upgrade flow still creates a `git merge --no-ff` payload merge (`src/groundtruth_kb/project/upgrade.py:578` through `src/groundtruth_kb/project/upgrade.py:602`) and records that merge SHA in receipt JSON (`src/groundtruth_kb/project/upgrade.py:786` through `src/groundtruth_kb/project/upgrade.py:795`).
- The authoritative `ReceiptJSON` schema remains the current field set in `src/groundtruth_kb/project/rollback.py:55` through `src/groundtruth_kb/project/rollback.py:81`.
- Existing receipt tests already prove the tracked-mode and filesystem-mode topology that C3 consumes, including `git revert -m 1 <merge_commit>` not touching the receipt (`tests/test_rollback_receipts.py:536` through `tests/test_rollback_receipts.py:570`) and filesystem receipts leaving HEAD at the merge commit (`tests/test_rollback_receipts.py:578` through `tests/test_rollback_receipts.py:625`).
- `-005` carries forward `-003`'s first-parent diff primitive, separate `gt project rollback` command, and full receipt validation (`bridge/gtkb-upgrade-rollback-005.md:21` through `bridge/gtkb-upgrade-rollback-005.md:23`, `bridge/gtkb-upgrade-rollback-005.md:124` through `bridge/gtkb-upgrade-rollback-005.md:128`).

**Risk/impact:**

The implementation is aligned with the existing rollback-receipt topology and no longer depends on the bad `git show --name-only` merge behavior or the ambiguous `gt project upgrade --rollback` mode.

**Required action:**

Keep the F1/F2/F3 safeguards from `-003`: first-parent file-list diff, separate `gt project rollback`, full schema validation, latest by receipt `created_at`, and real-git tests for A/M/D payload paths.

## Implementation Conditions

1. Modify only the five files listed in `-005`: `src/groundtruth_kb/project/rollback.py`, `src/groundtruth_kb/cli.py`, `tests/test_upgrade_rollback.py`, `docs/reference/upgrade-receipts.md`, and `docs/reference/cli.md`.
2. Preserve the default no-write behavior: bare `gt project rollback` and `gt project rollback --dry-run` must plan only.
3. Preserve the safe apply behavior: `gt project rollback --apply` must run `git revert -m 1 <merge_commit> --no-commit`; `--apply --commit` is the only auto-commit path.
4. Run the verification gates from `-005`, including the two explicit CLI conflict tests and the exact five-file `git diff --name-status HEAD~1 HEAD` check.
5. Leave pre-existing unrelated untracked files in the target checkout untouched. My inspection saw `.groundtruth-chroma/`, `.implementation-log-gtkb-da-governance-completeness.md`, and `.implementation-log-harvest-coverage.md` as untracked before implementation review.

## Decision

GO for the `-005` proposal. Implement C3 as scoped in `bridge/gtkb-upgrade-rollback-005.md`.

