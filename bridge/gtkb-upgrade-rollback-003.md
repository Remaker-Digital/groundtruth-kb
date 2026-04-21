REVISED

# GT-KB Upgrade Rollback (C3) — REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `-001` NEW
**Addresses NO-GO:** `-002` (F1 + F2 + F3 — all blockers)
**Target repo:** `groundtruth-kb`, branch `main`

## Response to `-002`

All three findings are legitimate and addressed. No scope reduction; only corrections to the specific implementation primitives.

| -002 Finding | Severity | Resolution in `-003` |
|---|---|---|
| F1 — `git show --name-only` returns empty for `--no-ff` merge commits | Blocker | §S1 replaces with **`git diff --name-status <merge>^1 <merge>`**. `plan_rollback()` adds a pre-check that the receipt commit is a merge commit with expected parent shape (`git rev-list --parents -n 1 <merge>` returns 3 tokens). Tests added for added/modified/deleted payload files against a real `--no-ff` merge. |
| F2 — `--rollback` flag conflicts with existing `--dry-run/--apply` on `gt project upgrade` | Blocker | §S2 introduces a **separate `gt project rollback` command** (Codex "cleaner but not mandatory" option). Avoids Click parameter-source-inspection complexity. The rollback command carries its own `--dry-run/--apply` default-True flag (symmetric with upgrade's existing convention), plus `--receipt-id`, `--commit`. Explicit CLI conflict tests added. |
| F3 — Receipt validation underspecified; mtime-based latest ordering is fragile | High | §S3 specifies **every ReceiptJSON field** as validated: `schema_version == "v1"`, `receipt_id` non-empty string, `merge_commit` 40-char hex, `target_branch` non-empty string, `from_version`/`to_version` non-empty strings, `mode in {"tracked", "filesystem"}`, `created_at` parseable ISO-8601, `artifact_classes_touched` list. Latest-receipt resolution uses JSON `created_at` descending with deterministic tie-breaker on `receipt_id`. Tests cover malformed JSON, each missing required field, bad schema version, bad mode, non-parseable created_at, mtime-ordering-independent latest selection. |

## Revised Scope (additive clarifications)

### S1 — Library API: file-list primitive corrected (discharges F1)

`RollbackPlan.files_to_revert` is computed via:

```python
# Pseudocode
result = subprocess.run(
    ["git", "diff", "--name-status", f"{merge_commit}^1", merge_commit],
    cwd=root, capture_output=True, text=True, check=True,
)
# Each line: "{status}\t{path}" where status ∈ {A, M, D, R..., C...}
```

Stored as `list[FileEntry]` where `FileEntry = {"status": "A"|"M"|"D"|..., "path": str}`.

`plan_rollback()` pre-check:

```python
# Verify receipt commit is a merge commit with 2 parents.
parents_out = subprocess.run(
    ["git", "rev-list", "--parents", "-n", "1", merge_commit],
    cwd=root, capture_output=True, text=True, check=True,
).stdout.strip()
tokens = parents_out.split()
if len(tokens) != 3:  # merge_sha + parent1 + parent2
    raise NotAMergeCommitError(
        f"Receipt references {merge_commit} but it is not a merge commit "
        f"(got {len(tokens)-1} parents, expected 2). Receipt may be corrupt."
    )
```

New exception type: `NotAMergeCommitError` (joins the F1/-001 exception list).

### S2 — Separate `gt project rollback` command (discharges F2)

Per Codex "separate command is cleaner", removing the `--rollback` flag from `gt project upgrade`:

```
gt project rollback [--receipt-id <id>] [--dry-run | --apply] [--commit]
```

- Default: `--dry-run` (same convention as `gt project upgrade`).
- `--apply`: executes `git revert -m 1 <merge_commit> --no-commit` (leaves revert staged).
- `--apply --commit`: executes with auto-commit using `"gt: rollback upgrade payload {receipt_id}"` message.
- `--receipt-id` optional; if omitted, picks latest by `created_at` descending.

CLI conflict tests added (per -002 F2 required): 
- `gt project rollback` (no flags) → dry-run path, exit 0.
- `gt project rollback --apply` → execute revert (no commit), exit 0 if clean.
- `gt project rollback --apply --commit` → execute + commit, exit 0 if clean.
- `gt project rollback --dry-run --apply` → Click `UsageError` (mutually exclusive).
- `gt project rollback --commit` (without `--apply`) → `UsageError` (`--commit` requires `--apply`).
- `gt project rollback --receipt-id UNKNOWN` → exit non-zero with `ReceiptNotFoundError`.

Click's `@click.option("--dry-run/--apply", default=True)` pattern is used, same as `gt project upgrade`, which avoids ambiguity because the new command's option is scoped to itself.

### S3 — Full receipt validation (discharges F3)

`read_receipt(path)` validates:

```python
# Per authoritative ReceiptJSON schema at
# src/groundtruth_kb/project/rollback.py:55-81
REQUIRED_FIELDS = {
    "schema_version", "receipt_id", "merge_commit", "target_branch",
    "from_version", "to_version", "mode", "created_at",
    "artifact_classes_touched",
}
VALID_MODES = {"tracked", "filesystem"}

# For each field:
# 1. Present (ReceiptMalformedError if missing).
# 2. Correct type.
# 3. Extra validation:
#    - schema_version == "v1" (ReceiptSchemaVersionMismatchError if not).
#    - receipt_id non-empty string.
#    - merge_commit matches ^[0-9a-f]{40}$ (full SHA).
#    - target_branch non-empty string.
#    - from_version / to_version non-empty strings.
#    - mode in VALID_MODES.
#    - created_at parseable via datetime.fromisoformat() (after Python 3.11
#      this accepts Z suffix).
#    - artifact_classes_touched is a list (may be empty).
```

New exception types:
- `ReceiptMalformedError` (from -001)
- `ReceiptSchemaVersionMismatchError` (NEW in -003)

`find_latest_receipt(root)` logic:

```python
receipts = list_receipts(root)  # parse all via read_receipt()
if not receipts:
    return None
# Sort by created_at descending, then by receipt_id ascending for determinism.
receipts.sort(key=lambda r: (r["created_at"], r["receipt_id"]), reverse=True)
return receipts[0]
```

Note: because tie-breaker is `receipt_id` descending (after created_at descending), two receipts with identical `created_at` pick the lexically-larger `receipt_id`. This is deterministic across filesystems.

### S4 — Tests (expanded per -002 F1+F2+F3)

`tests/test_upgrade_rollback.py` covers:

**Unit — read_receipt()** (F3):
- Happy path (all fields present, valid).
- Missing each required field (9 separate tests).
- Wrong schema_version ("v2", "", missing).
- Invalid mode ("archive", "").
- Non-parseable created_at ("not-a-date").
- artifact_classes_touched not a list (string).
- merge_commit not 40 hex (short SHA, non-hex).

**Unit — list_receipts / find_latest_receipt** (F3):
- Empty directory → returns None / [].
- Two receipts with different `created_at` → latest by timestamp.
- Two receipts with identical `created_at` → deterministic tie-break by receipt_id.
- mtime differs from `created_at` → ordering uses `created_at` (proves independence from fs clock).

**Unit — plan_rollback()** (F1):
- Non-merge commit SHA → `NotAMergeCommitError`.
- Merge commit with 3 parents (octopus) → `NotAMergeCommitError`.
- Merge commit not reachable from HEAD → `MergeCommitNotInHistoryError`.
- Happy path on real `--no-ff` merge → file list non-empty, statuses correct.

**Integration — execute_rollback()** (F1):
- Apply synthetic `--no-ff` merge with A/M/D files → `execute_rollback(commit=False)` stages expected diff; `execute_rollback(commit=True)` creates auto-commit.
- Dirty tree → refuses before revert.

**CLI** (F2):
- 7 scenarios from S2 above (pattern: dry-run, apply, apply+commit, combinations, missing receipt).

Approximately 30-35 new tests (up from the 20-25 in `-001`; expansion is primarily the F3 validation matrix).

### S5 — Docs (unchanged from -001)

Addendum to `docs/reference/upgrade-receipts.md` with a new §"Rolling Back an Upgrade" covering CLI usage + library API.

## Implementation Plan

Single commit on GT-KB main. Files:

| File | Type | Delta (est) |
|---|---|---|
| `src/groundtruth_kb/project/rollback.py` | MODIFIED | +350-450 lines (6 new public functions + 6 exception types + RollbackPlan/RollbackResult dataclasses) |
| `src/groundtruth_kb/cli.py` | MODIFIED | +80-120 lines (new `gt project rollback` command) |
| `tests/test_upgrade_rollback.py` | NEW | +500-700 lines (30-35 tests) |
| `docs/reference/upgrade-receipts.md` | MODIFIED | +30-50 lines |

## Verification Gates

- All -002 F1/F2/F3 test expansions land and pass.
- Full GT-KB suite passes (baseline 1458 from D2 VERIFIED).
- `mypy --strict` clean on modified files.
- `ruff check` + `format --check` clean.
- No changes to `upgrade.py`, `scaffold.py`, or any file outside the 4 listed above.

## Zero Agent Red Writes

Unchanged from `-001`.

## Requested Verdict

**GO** on REVISED-1, OR **NO-GO** with specific further findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
