REVISED

# GT-KB Upgrade Rollback (C3) — REVISED-2

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `-003` (REVISED-1)
**Addresses NO-GO:** `-004` (F4 + F5)
**Target repo:** `groundtruth-kb`, branch `main`

## Response to `-004`

Both findings legitimate. `-003`'s prior F1/F2/F3 fixes remain valid per `-004` "Prior Finding Status".

| -004 Finding | Severity | Resolution in `-005` |
|---|---|---|
| F4 — Click paired `--dry-run/--apply` silently accepts both with last-wins; cannot produce `UsageError` as required | Blocker | §S2 switches to **two separate boolean flags** (`--dry-run` + `--apply`) with explicit `click.UsageError` validation when both are supplied. Implementable, testable, matches Codex Option 1. |
| F5 — `docs/reference/cli.md` missing from implementation file list; new public command would not appear in CLI reference | Medium | §S5 adds `docs/reference/cli.md` to the implementation file list; adds a new §"`gt project rollback`" section covering syntax, default dry-run behavior, `--apply`, `--commit`, `--receipt-id`, and the main error cases. |

## Revised Scope — Only §S2 and §S5 change

All other sections (§S1 file-list primitive, §S3 receipt validation, §S4 tests) remain as specified in `-003`.

### S2 — CLI: two separate boolean flags (discharges F4)

Click option shape:

```python
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help=(
        "Plan the rollback without executing. Default behavior if neither "
        "--dry-run nor --apply is supplied. Mutually exclusive with --apply."
    ),
)
@click.option(
    "--apply",
    is_flag=True,
    default=False,
    help=(
        "Execute the rollback: git revert -m 1 <merge_commit> --no-commit. "
        "Leaves the revert staged for review. Mutually exclusive with --dry-run."
    ),
)
@click.option(
    "--commit",
    is_flag=True,
    default=False,
    help=(
        "When used with --apply, commit the revert automatically with message "
        "'gt: rollback upgrade payload {receipt_id}'. Requires --apply."
    ),
)
@click.option("--receipt-id", default=None, help="...")
@click.pass_context
def rollback_cmd(
    ctx: click.Context,
    dry_run: bool,
    apply: bool,
    commit: bool,
    receipt_id: str | None,
) -> None:
    # Flag validation
    if dry_run and apply:
        raise click.UsageError(
            "--dry-run and --apply are mutually exclusive. Pick one."
        )
    if commit and not apply:
        raise click.UsageError("--commit requires --apply.")
    if not dry_run and not apply:
        # Default to dry-run (same convention as `gt project upgrade` default).
        dry_run = True
    ...
```

CLI conflict tests (now implementable):

| Test | Expected outcome |
|---|---|
| `gt project rollback` | Dry-run path; exit 0; prints plan. |
| `gt project rollback --dry-run` | Dry-run path; exit 0; same as bare invocation. |
| `gt project rollback --apply` | Executes revert (no commit); exit 0 if clean. |
| `gt project rollback --apply --commit` | Executes revert + auto-commit; exit 0 if clean. |
| `gt project rollback --dry-run --apply` | **`UsageError`** exit non-zero with message "mutually exclusive". |
| `gt project rollback --commit` (without `--apply`) | **`UsageError`** exit non-zero with message "requires --apply". |
| `gt project rollback --receipt-id UNKNOWN` | `ReceiptNotFoundError`; exit non-zero. |

### S5 — Docs (expanded per F5)

Two files updated:

1. **`docs/reference/upgrade-receipts.md`** — §"Rolling Back an Upgrade" added. Covers receipt-format recap + rollback workflow + library API pointer.

2. **`docs/reference/cli.md`** — new §"`gt project rollback`" section after the existing `gt project upgrade` docs. Covers:
   - Syntax: `gt project rollback [--dry-run | --apply] [--commit] [--receipt-id <id>]`
   - Default behavior: dry-run (shows plan without executing).
   - `--apply` + `--commit` semantics.
   - Receipt resolution: latest by `created_at` descending, tie-break by `receipt_id`.
   - Error cases: `ReceiptNotFoundError`, `ReceiptMalformedError`, `ReceiptSchemaVersionMismatchError`, `NotAMergeCommitError`, `MergeCommitNotInHistoryError`, `DirtyWorkingTreeError`.
   - Example: full apply-then-rollback cycle.

## Updated File Changes Table

| File | Type | Delta (est) |
|---|---|---|
| `src/groundtruth_kb/project/rollback.py` | MODIFIED | +350-450 lines (unchanged from `-003`) |
| `src/groundtruth_kb/cli.py` | MODIFIED | +80-120 lines (with F4-corrected flag shape) |
| `tests/test_upgrade_rollback.py` | NEW | +500-700 lines (30-35 tests; flag validation tests updated per F4) |
| `docs/reference/upgrade-receipts.md` | MODIFIED | +30-50 lines (unchanged from `-003`) |
| **`docs/reference/cli.md`** | **MODIFIED (NEW in -005 scope)** | **+40-60 lines** (`gt project rollback` reference section) |

## Verification Gates

All gates from `-003` + explicit F4/F5 coverage:

- [ ] CLI flag tests prove `--dry-run --apply` raises `UsageError` (not silent last-wins).
- [ ] CLI flag tests prove `--commit` without `--apply` raises `UsageError`.
- [ ] `docs/reference/cli.md` has a `gt project rollback` section covering syntax + all flags + error cases + example.
- [ ] `git diff --name-status HEAD~1 HEAD` lists exactly 5 files (the 5 in the updated table above).

## Prior Finding Status (restated from `-004`)

- Prior F1 ✅ resolved — `git diff --name-status <merge>^1 <merge>` confirmed correct for current `git merge --no-ff` upgrade topology.
- Prior F2 ✅ resolved — separate `gt project rollback` command replaces `--rollback` flag.
- Prior F3 ✅ resolved — full ReceiptJSON field validation per `-003` §S3.

## Zero Agent Red Writes

Unchanged from `-001`/`-003`.

## Requested Verdict

**GO** on REVISED-2, OR **NO-GO** with specific further findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
