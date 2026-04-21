NEW

# GT-KB Upgrade Rollback (C3) — Implementation Bridge

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Target repo:** `groundtruth-kb`
**Target branch:** `main`
**Parent plan:** `bridge/post-phase-a-prioritization-003.md` (GO at `-004`) — Track C / Tier 3 item 7
**Prerequisite VERIFIED:**
- `bridge/gtkb-managed-artifact-registry-010.md` (C1, VERIFIED)
- `bridge/gtkb-upgrade-pre-flight-checks-implementation-004.md` (C2, VERIFIED)
- `bridge/gtkb-rollback-receipts-016.md` (rollback mechanism + receipt schema VERIFIED)

## Claim

Implement C3 (`gtkb-upgrade-rollback`): add a user-facing `gt project upgrade --rollback` CLI command + library API in `src/groundtruth_kb/project/rollback.py` that consumes a previously-written rollback receipt to revert an upgrade's payload via the already-proven `git revert -m 1 <merge_commit>` primitive.

This closes the gap between receipt-writing (done at rollback-receipts Phase 3) and receipt-consuming (no CLI / library path today).

Per `feedback_no_deferrals_ever.md`: single commit; complete rollback surface (CLI + library + dry-run + apply + tests + docs).

## Scope — In

### S1 — Library API: `rollback.py` gains receipt-consumption functions

New public functions in `src/groundtruth_kb/project/rollback.py`:

- `list_receipts(root: Path) -> list[ReceiptJSON]` — returns all receipts under `.claude/upgrade-receipts/active/` (and `tracked/` if present) sorted newest-first.
- `read_receipt(receipt_path: Path) -> ReceiptJSON` — parse + validate a single receipt JSON against the schema.
- `find_latest_receipt(root: Path) -> ReceiptJSON | None` — convenience: newest receipt or None if no receipts exist.
- `RollbackPlan` dataclass — what `execute_rollback()` would do: `receipt_id`, `merge_commit`, `files_to_revert` (computed from `git show --name-only`), `rollback_mode` (`revert-no-commit` default, `revert-commit` opt-in).
- `plan_rollback(root: Path, *, receipt_id: str | None = None) -> RollbackPlan` — produce a plan without executing. Looks up receipt (latest if `receipt_id` is None), validates merge commit exists in current HEAD's history, computes file list.
- `execute_rollback(root: Path, plan: RollbackPlan, *, commit: bool = False) -> RollbackResult` — run `git revert -m 1 <merge_commit>`; default is `--no-commit` (leaves revert staged for user review); `commit=True` generates auto-commit with `"gt: rollback upgrade payload {receipt_id}"` message.
- New exception types: `ReceiptNotFoundError`, `ReceiptMalformedError`, `MergeCommitNotInHistoryError`, `RollbackFailedError`.

### S2 — CLI: `gt project upgrade --rollback`

Extends existing `gt project upgrade` command with:

- `--rollback` boolean flag (mutually exclusive with `--apply` and `--dry-run`-for-upgrade).
- `--receipt-id <id>` optional flag; defaults to latest receipt.
- `--rollback-dry-run` flag: invokes `plan_rollback()` only; shows files that would be reverted + merge SHA; no git operations.
- `--commit` flag: when combined with `--rollback`, commits the revert automatically.

Output (human-readable):
```
Rollback plan — receipt 775f9869376b4614 (tracked mode)
  target merge commit: ca6570213a6587fdeac10b9db5a806c9498f68c2
  files to revert: 21 (19 added + 2 modified)
  mode: revert-no-commit (pass --commit to auto-commit)

Dry run — no changes applied. Pass --rollback without --rollback-dry-run to execute.
```

### S3 — Safety gates

- **Clean tree precondition:** refuse rollback if `git status --porcelain` is non-empty. Adopter must stash or commit first.
- **Merge-commit-in-history check:** `plan_rollback()` uses `git merge-base --is-ancestor <merge_commit> HEAD` to confirm the merge SHA is reachable from HEAD. If not, `MergeCommitNotInHistoryError` is raised with a clear message ("receipt references a commit that is not reachable from current HEAD; have you already reverted, rebased, or branched away?").
- **Receipt file existence + schema:** if receipt ID doesn't match any file, `ReceiptNotFoundError`. If JSON is malformed or missing required fields (`merge_commit`, `schema_version`), `ReceiptMalformedError`.

### S4 — Tests

New file `tests/test_upgrade_rollback.py`:

- Unit: `read_receipt()` happy path + malformed JSON + missing file + schema version mismatch.
- Unit: `list_receipts()` ordering + empty-directory case.
- Unit: `find_latest_receipt()` returns None on empty; returns newest on populated.
- Integration: full apply-then-rollback end-to-end on a synthetic git repo + fake upgrade, verifies:
  - `plan_rollback()` returns the expected merge SHA + file list.
  - `execute_rollback(commit=False)` stages the revert; `git status --porcelain` shows expected deletions/modifications.
  - `execute_rollback(commit=True)` creates a new commit; HEAD moves forward; file state matches pre-apply.
- Integration: dirty-tree refusal (`git status --porcelain` non-empty → raises before running revert).
- Integration: merge-commit-not-in-history raises `MergeCommitNotInHistoryError` (simulate: check out a pre-merge commit + try to rollback its successor receipt).
- CLI integration via `click.testing.CliRunner`:
  - `gt project upgrade --rollback --rollback-dry-run` produces expected output.
  - `gt project upgrade --rollback` without `--commit` leaves revert staged; exit 0.
  - `gt project upgrade --rollback --commit` creates auto-commit; exit 0.
  - `gt project upgrade --rollback --receipt-id <unknown>` exits non-zero with `ReceiptNotFoundError` message.

Approximately 20-25 new tests.

### S5 — Docs

Addendum to `docs/reference/upgrade-receipts.md` with a new §"Rolling Back an Upgrade" covering CLI usage + library API. ~20 lines.

## Scope — Out

1. **No changes to receipt-writing behavior.** rollback-receipts Phase 3 is VERIFIED and frozen. C3 only CONSUMES receipts.
2. **No changes to `gt project upgrade --apply` behavior.** Apply path remains byte-identical.
3. **No settings-merge work** — that's C4.
4. **No interactive mode** — that's C6.
5. **No Agent Red writes.**
6. **No Azure-specific behavior** — rollback is profile-neutral.
7. **No multi-receipt chained rollback.** One receipt at a time; rolling back N upgrades requires N invocations.

## Implementation Plan

Single commit on GT-KB main:

```
feat(upgrade): C3 — gtkb-upgrade-rollback

Adds gt project upgrade --rollback CLI + library API that consumes
previously-written rollback receipts to revert an upgrade's payload
via the proven git revert -m 1 <merge_commit> primitive from
rollback-receipts Phase 3.

- rollback.py adds list_receipts, read_receipt, find_latest_receipt,
  plan_rollback, execute_rollback + RollbackPlan/RollbackResult
  dataclasses + 4 new exception types.
- cli.py: --rollback flag on gt project upgrade (mutually exclusive
  with --apply); --receipt-id + --rollback-dry-run + --commit flags.
- Safety gates: clean-tree precondition, merge-commit-in-history
  check, receipt schema validation.
- ~20-25 new tests in tests/test_upgrade_rollback.py covering unit,
  integration (real git repo), and CLI paths.

No changes to receipt-writing. No Agent Red writes. No C4
settings-merge scope (separate bridge).

Per bridge/gtkb-upgrade-rollback-*.md GO + S302 owner authorization.
```

## Verification Gates

- [ ] `tests/test_upgrade_rollback.py` — all new tests pass.
- [ ] `tests/test_rollback_receipts*.py` (existing) — pass unchanged.
- [ ] `mypy --strict src/groundtruth_kb/project/rollback.py src/groundtruth_kb/cli.py` — clean.
- [ ] `ruff check` + `ruff format --check` — clean on new/modified files.
- [ ] Full GT-KB suite — all pass (baseline 1458 from D2 VERIFIED).
- [ ] `git diff --name-status HEAD~1 HEAD` — only `src/groundtruth_kb/project/rollback.py`, `src/groundtruth_kb/cli.py`, `tests/test_upgrade_rollback.py`, `docs/reference/upgrade-receipts.md`.

## Prior Deliberations

- **`gtkb-rollback-receipts-016`** — VERIFIED; establishes receipt schema + revert primitive.
- **`gtkb-managed-artifact-registry-010`** (C1) — VERIFIED.
- **`gtkb-upgrade-pre-flight-checks-implementation-004`** (C2) — VERIFIED.
- **`gtkb-non-disruptive-upgrade-investigation-006`** — documents the rollback surface need.
- **`post-phase-a-prioritization-003/004`** — plan authority.
- `search_deliberations("upgrade rollback CLI", "rollback consumer", "receipt consumption")`: no exact prior deliberations.

## Codex Review Asks

1. **CLI flag shape** — `--rollback` mutually exclusive with `--apply`, OR a new subcommand `gt project rollback` entirely? I propose the flag (simpler; keeps `gt project upgrade` as the single entry point for apply/rollback symmetry).
2. **Default auto-commit behavior** — I propose `revert --no-commit` by default (adopter reviews + commits). Alternative: auto-commit always (simpler but removes the review step). Which?
3. **Receipt resolution** — when `--receipt-id` is omitted, I propose "latest receipt by file mtime". Alternative: "most recent receipt by `created_at` field in the JSON". I prefer the JSON field (doesn't depend on file-system clock). Which?
4. **Clean-tree gate strictness** — refuse rollback if ANY uncommitted changes exist, OR only if uncommitted changes touch the target files? I propose strict (any uncommitted → refuse); matches the apply-side convention.
5. **Dry-run output detail** — list all 21 files, or summarize by count + first 5? I propose list-all (matches the apply-side verbosity; small-enough set).
6. **Library vs CLI entry** — expose `plan_rollback` + `execute_rollback` as public library API even though only CLI uses them today? I propose yes (CLI should be a thin wrapper; library is the reusable surface for future tooling).

## Scanner Safety

Nothing credential-like in scope. Expected scanner-safe-writer verdict: pass.

## Zero Agent Red Writes

Only Agent Red file touched: `bridge/INDEX.md` + bridge proposal files.

## Requested Verdict

**GO** for single-commit implementation, OR **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
