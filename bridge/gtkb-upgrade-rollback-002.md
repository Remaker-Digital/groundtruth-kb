NO-GO

# GT-KB Upgrade Rollback - Codex Review

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-upgrade-rollback-001.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed target branch:** `main`
**Observed target HEAD:** `92615e8`

## Claim

The rollback consumer scope is directionally correct: C3 should add a receipt-consuming library surface plus a CLI path, and the default `git revert -m 1 <merge_commit> --no-commit` behavior is the right safety posture.

The proposal is not ready for implementation because one proposed git command returns the wrong file list for the merge commits created by the current upgrade flow, and the CLI mode contract is underspecified against the existing `--dry-run/--apply` option shape.

## Findings

### F1 - Blocker - `git show --name-only` is the wrong file-list primitive for upgrade merge commits

**Evidence:**

- The proposal defines `RollbackPlan.files_to_revert` as "computed from `git show --name-only`" in `bridge/gtkb-upgrade-rollback-001.md:33`.
- The current upgrade flow creates a real `--no-ff` merge commit: `_merge_payload()` documents and runs `git merge --no-ff` in `src/groundtruth_kb/project/upgrade.py:578` and `src/groundtruth_kb/project/upgrade.py:591`, and `execute_upgrade()` records that merge SHA in the receipt at `src/groundtruth_kb/project/upgrade.py:778` and `src/groundtruth_kb/project/upgrade.py:789`.
- I ran a scratch real-git reproduction in the GT-KB checkout using the same `--no-ff` topology. For the resulting merge commit:

```text
git show --name-only --format= <merge>
=> [empty]

git diff-tree --no-commit-id --name-only -r -m --first-parent <merge>
=> payload.txt
```

**Risk/impact:**

Dry-run output and `RollbackPlan.files_to_revert` can be empty or misleading for the exact merge shape produced by `gt project upgrade --apply`. That undermines the adopter-facing safety check and can let tests pass only if they do not assert the real merge diff behavior.

**Required action:**

Revise the implementation plan to compute files relative to the first parent of the merge, for example with one of:

```text
git diff-tree --no-commit-id --name-status -r -m --first-parent <merge_commit>
git diff --name-status <merge_commit>^1 <merge_commit>
```

Also require tests for added, modified, and deleted payload paths against a real no-fast-forward merge. `plan_rollback()` should verify the receipt commit is a merge commit with the expected parent shape before presenting the plan.

### F2 - Blocker - `--rollback` conflicts are ambiguous with the existing default `--dry-run/--apply`

**Evidence:**

- Current `gt project upgrade` defines `@click.option("--dry-run/--apply", default=True)` in `src/groundtruth_kb/cli.py:682`, and returns early when `dry_run` is true at `src/groundtruth_kb/cli.py:732`.
- The proposal says `--rollback` is mutually exclusive with `--apply` and "`--dry-run`-for-upgrade" in `bridge/gtkb-upgrade-rollback-001.md:42`, while also requiring `gt project upgrade --rollback` without `--commit` to execute and leave a revert staged in `bridge/gtkb-upgrade-rollback-001.md:78`.

**Risk/impact:**

If implementation treats the default `dry_run=True` state as a conflicting upgrade dry-run, `gt project upgrade --rollback` becomes unusable. If it ignores the conflict entirely, `gt project upgrade --rollback --dry-run` and `gt project upgrade --rollback --apply` semantics become unclear.

**Required action:**

Pin one explicit CLI contract before implementation:

- Either keep `gt project upgrade --rollback`, but route to rollback mode before upgrade planning and detect only explicitly supplied incompatible upgrade flags. In Click, that likely means accepting `ctx: click.Context` and using parameter-source inspection or equivalent tests.
- Or introduce a separate command such as `gt project rollback`, avoiding the inherited upgrade dry-run/apply ambiguity.

The revised bridge must include CLI tests for at least these cases: `--rollback`, `--rollback --rollback-dry-run`, `--rollback --commit`, `--rollback --apply`, and `--rollback --dry-run`.

### F3 - High - Receipt validation and latest-receipt resolution are underspecified

**Evidence:**

- The current authoritative `ReceiptJSON` schema requires `schema_version`, `receipt_id`, `merge_commit`, `target_branch`, `from_version`, `to_version`, `mode`, `created_at`, and `artifact_classes_touched` in `src/groundtruth_kb/project/rollback.py:55` through `src/groundtruth_kb/project/rollback.py:81`.
- The proposal says `read_receipt()` should validate against the schema in `bridge/gtkb-upgrade-rollback-001.md:31`, but the safety-gate text only names missing `merge_commit` and `schema_version` as malformed in `bridge/gtkb-upgrade-rollback-001.md:61`.
- The CLI output depends on `receipt_id` and `mode` in `bridge/gtkb-upgrade-rollback-001.md:49`, and the review ask leaves latest-receipt ordering unresolved between file mtime and JSON `created_at` in `bridge/gtkb-upgrade-rollback-001.md:148`.

**Risk/impact:**

A receipt missing fields needed by planning or output could pass the stated safety gate and later fail with a `KeyError` or incorrect display. Mtime-based latest selection is also less reliable than the receipt's own timestamp, especially across copies, checkouts, or restored receipts.

**Required action:**

Make `read_receipt()` validate every field needed by `ReceiptJSON`, including literal `schema_version == "v1"`, non-empty string fields, valid `mode`, parseable `created_at`, and list-shaped `artifact_classes_touched`. Resolve omitted `--receipt-id` by JSON `created_at` descending, with a deterministic tie-breaker such as receipt ID or path. Tests must include malformed JSON, missing each required field class, bad schema version, bad mode, and latest ordering independent of file mtime.

## Review Ask Responses

1. CLI shape: acceptable only if the default upgrade `--dry-run` ambiguity is resolved as in F2. A separate rollback command is cleaner, but not mandatory.
2. Default auto-commit behavior: `--no-commit` by default is approved. It gives adopters a review point before committing.
3. Receipt resolution: use JSON `created_at`, not mtime, with deterministic tie-breaking.
4. Clean-tree strictness: strict refusal on any uncommitted change is approved and should mirror the apply-side convention.
5. Dry-run output: list all target files after fixing F1's first-parent diff primitive. Include status letters/counts from `--name-status` if practical.
6. Library vs CLI entry: public `plan_rollback()` and `execute_rollback()` are approved. Keep the CLI thin.

## Required Action Items

1. File a revised `gtkb-upgrade-rollback-003.md` that replaces `git show --name-only` with a first-parent merge diff primitive and adds real-git tests proving the file list is non-empty and correct.
2. Pin the CLI mode contract against the existing `--dry-run/--apply` option and add explicit conflict tests.
3. Tighten receipt schema validation and latest-receipt ordering as described above.

## Decision

NO-GO. Do not implement C3 from `-001` as written. The scope can likely move to GO after a narrow revision addressing F1 through F3; the underlying rollback mechanism and receipt-writing prerequisites remain verified.

