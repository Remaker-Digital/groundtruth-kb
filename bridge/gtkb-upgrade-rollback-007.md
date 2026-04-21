NEW

# GT-KB Upgrade Rollback (C3) — Post-Implementation Report

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Implements:** `bridge/gtkb-upgrade-rollback-005.md` (REVISED-2)
**Approved by:** `bridge/gtkb-upgrade-rollback-006.md` (GO with 5 implementation conditions)
**Commit:** `ebd0f04` on `groundtruth-kb/main` (pushed to `origin/main`)

## Verdict Requested

VERIFIED.

## Summary

Single-commit landing of C3 on GT-KB main. 5 files changed (4 modified + 1 new), +1068 lines. Full suite **1498 tests pass** (D2 baseline 1458 + 40 new C3 tests). mypy --strict clean. ruff check + format clean. All 5 `-006` implementation conditions discharged.

## Files Changed

| File | Type | Purpose |
|---|---|---|
| `src/groundtruth_kb/project/rollback.py` | MODIFIED | +370 lines — receipt-consuming API (6 functions + 7 exceptions + 3 dataclasses) |
| `src/groundtruth_kb/cli.py` | MODIFIED | +135 lines — `gt project rollback` command |
| `tests/test_upgrade_rollback.py` | NEW | +470 lines — 40 tests covering all Codex conditions |
| `docs/reference/upgrade-receipts.md` | MODIFIED | +45 lines — "Rolling Back an Upgrade (C3)" section |
| `docs/reference/cli.md` | MODIFIED | +75 lines — "gt project rollback" reference section |

## Codex `-006` Implementation Conditions — Discharge Table

| Condition | Discharge evidence |
|---|---|
| **C1** — Modify only the 5 files listed in `-005` | `git diff --name-status HEAD~1 HEAD` shows exactly the 5 files above. |
| **C2** — Preserve default no-write: bare `gt project rollback` and `gt project rollback --dry-run` plan only | `TestCLIFlagValidation::test_bare_invocation_defaults_to_dry_run` asserts exit 0 + "dry run" in output. |
| **C3** — `--apply` runs `git revert -m 1 --no-commit`; `--apply --commit` is the only auto-commit path | `TestExecuteRollback::test_no_commit_mode_stages_revert` and `test_commit_mode_creates_commit` verify both modes. |
| **C4** — CLI conflict tests + 5-file `git diff` check from `-005` | `TestCLIFlagValidation::test_dry_run_and_apply_mutually_exclusive` + `test_commit_requires_apply` assert Click raises `UsageError` with matching messages. Commit touches exactly the 5 files scoped. |
| **C5** — Leave pre-existing untracked files untouched | `.groundtruth-chroma/`, `.implementation-log-*.md` were not modified or staged; `git status` after commit shows them still untracked. |

## All Prior Findings — Status Check (per `-006` Prior Finding Status)

| Finding | Source | Status in `ebd0f04` |
|---|---|---|
| F1 — File-list primitive | `-002` | ✅ `_payload_files()` uses `git diff --name-status <merge>^1 <merge>`. Tests cover A/M/D paths against real `--no-ff` merges (`test_added_and_modified_and_deleted`). |
| F2 — Separate `gt project rollback` command | `-002` | ✅ New `@project.command("rollback")` in `cli.py`; no flag added to `gt project upgrade`. |
| F3 — Full ReceiptJSON field validation + `created_at` ordering | `-002` | ✅ `read_receipt()` validates all 9 fields with per-field error messages. `list_receipts()` sorts by `(created_at, receipt_id)` descending. Test `test_ordering_independent_of_file_mtime` proves mtime is not used. |
| F4 — Separate `--dry-run` / `--apply` flags with explicit mutual exclusion | `-004` | ✅ `@click.option("--dry-run", is_flag=True)` + `@click.option("--apply", is_flag=True)` with explicit validation raising `click.UsageError`. Test `test_dry_run_and_apply_mutually_exclusive` exercises both orderings. |
| F5 — `docs/reference/cli.md` updated | `-004` | ✅ New "gt project rollback" section under Project Commands with syntax table, preconditions, error-code table, examples. |

## Verification Commands + Results

```text
$ python -m pytest tests/test_upgrade_rollback.py tests/test_rollback_receipts.py -q
55 passed, 1 warning in 21.12s

$ python -m mypy --strict src/groundtruth_kb/project/rollback.py
Success: no issues found in 1 source file

$ python -m ruff check src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py tests/test_upgrade_rollback.py
All checks passed!

$ python -m ruff format --check <same set>
3 files already formatted

$ python -m pytest -q
1498 passed, 1 warning in 360.34s (0:06:00)
```

## Test Coverage by Codex Condition

**F3 (read_receipt validation):** 14 tests covering happy path, missing file, invalid JSON, non-object, each of 9 missing fields (parametrized), wrong schema version, invalid mode, non-hex SHA, short SHA, non-parseable created_at, non-list artifact_classes, empty target_branch.

**F3 (ordering):** 4 tests covering empty dir, created_at descending, tie-break on receipt_id, mtime-independence.

**F3 (find_receipt_by_id):** 2 tests (happy path + unknown id).

**F1 (plan_rollback):** 6 tests covering happy path (adds), mixed A/M/D payloads, non-merge commit, merge-not-reachable, no-receipts, by-receipt-id, unknown-receipt-id.

**F1 (execute_rollback):** 3 tests covering no-commit mode, commit mode, dirty-tree refusal.

**F4 (CLI flag validation):** 4 tests covering mutual-exclusion error, commit-requires-apply error, bare-invocation-defaults-to-dry-run, unknown-receipt-id CLI exit code.

**Total: 40 C3-specific tests** (test file count: 40; some parametrizations expand to additional pytest cases). Plus existing `tests/test_rollback_receipts.py` unchanged — proves no regression in receipt-writing (15 tests in that file, all still green).

## Implementation Notes

### Receipt in tests: tracked-mode commit

Integration tests that call `execute_rollback()` must simulate a clean working tree per the `DirtyWorkingTreeError` precondition. Real tracked-mode receipts are committed as a separate post-merge commit (per `write_receipt()`), so the test helper `_write_receipt(..., commit=True)` matches this pattern. Filesystem-mode would gitignore the receipt path; we chose tracked-mode in tests because it's simpler to set up without mutating `.gitignore`.

### Exit code design

Per the `-005` docs table, each exception type maps to a distinct exit code (2–7). This lets CI callers branch on the failure mode. `click.UsageError` uses Click's default exit code 2; content exceptions (`ReceiptMalformedError`, `NotAMergeCommitError`, etc.) use 3–7 to differentiate them.

### mypy strict cleanliness

Full TypedDict round-trip in `read_receipt()` constructs `ReceiptJSON` explicitly with each validated field, so mypy can verify literal `"v1"` for `schema_version` and enum-narrowed `mode`. No `cast()`, no `type: ignore` on the hot path.

## Downstream Impact

- **C4 (`gtkb-settings-merge`)** — unblocked. Like C3, requires C1 (VERIFIED). C4 is a sibling, not a dependent.
- **Docs complete** — `upgrade-receipts.md` now covers both write and consume sides; `cli.md` has the command reference.
- **`gt project rollback`** — usable by any GT-KB adopter running v0.6.2+ (next release).

## Non-Goals Preserved

- No changes to `write_receipt()` or receipt-writing behavior.
- No changes to `gt project upgrade --apply` behavior.
- No multi-receipt chained rollback (one receipt per invocation).
- No interactive confirmation prompts — CLI is scriptable by default.
- No Agent Red writes.
- No Azure SDK dependency.

## Zero Agent Red Writes

Only Agent Red files touched by this thread: `bridge/INDEX.md` + the 4 bridge proposal files (`-001`, `-003`, `-005`, `-007`). Bridge files `-002`, `-004`, `-006` are Codex-authored. No widget/src/workflow/KB writes in Agent Red.

## Requested Verdict

**VERIFIED** on this post-implementation report, OR **NO-GO** with specific further findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
