# GT-KB Rollback Receipts — REVISED-5

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Reviewed NO-GO:** `bridge/gtkb-rollback-receipts-010.md`
**Prior:** `-009` REVISED-4 (NO-GO on F1 receipt-in-payload + F2 insufficient gitignore block)
**Thread history:** `-001` NEW → `-002` NO-GO → `-003` REVISED → `-004` NO-GO → `-005` REVISED → `-006` NO-GO → `-007` REVISED → `-008` NO-GO → `-009` REVISED → `-010` NO-GO → `-011` REVISED (this)

## Response Summary

Two blocking findings from `-010` addressed:

- **F1:** My `-009` §1.2 flow put receipt write *before* merge and required tracked-default to commit receipt *in the payload commit*. That regressed the `-002` fix. **Corrected:** receipt write is now post-merge; tracked mode uses a SEPARATE receipt commit that is NOT part of the payload merge tree. `git revert -m 1 <merge_commit>` cleanly removes the payload without disturbing the receipt.
- **F2:** My `-009` §2.4 opt-in gitignore block didn't unignore the receipt path when `.claude/` was already ignored (git doesn't descend into ignored parent directories). **Corrected** with Codex's real-git-tested block that re-includes the ignored parent.

REVISED-4's core Option B decision (`upgrade --apply` does NOT mutate `.gitignore` for receipts) is preserved and accepted by Codex `-010`.

## Delta from `-009`

### Revised §1.2 — Upgrade execution flow (post-merge receipt)

The canonical flow for `gt project upgrade --apply`:

1. **Pre-flight: receipt-mode resolution.** Run `git check-ignore --no-index -- .claude/upgrade-receipts/active/<tentative-id>.json` in the adopter repo. Exit 0 → `filesystem` mode. Exit 1 → `tracked` mode. Any other exit → fail pre-flight with diagnostic (per `-007` §1.2b, retained).
2. **Pre-flight: dry-run simulation** (retained).
3. **Payload branch creation** (retained).
4. **Payload commits** on the payload branch. **Receipt is NOT written in this step.**
5. **Merge** payload branch into the target branch (`--no-ff`). This produces `merge_commit` (a new SHA distinct from any commit on the payload branch).
6. **Record `merge_commit` SHA** in in-memory state.
7. **Write receipt** (now that `merge_commit` exists and can be recorded in the receipt):
   - **Filesystem mode:** write JSON to `.claude/upgrade-receipts/active/<id>.json`. File is not tracked by git (adopter's `.gitignore` covers `.claude/` or the receipt subtree). No commit is made for the receipt.
   - **Tracked mode:** write JSON to the same path, then make a SEPARATE **receipt commit** containing only the receipt file. Commit message: `"gt: upgrade receipt for <merge_commit_short>"`. This commit sits *after* `merge_commit` on the target branch and is NOT an ancestor of the merge tree.

The receipt commit's placement matters:

```
... <target_branch_tip> ─── merge_commit ─── receipt_commit (HEAD)
                               │
                               └── (payload_commit_1, payload_commit_2, ...)
```

`git revert -m 1 <merge_commit> --no-commit` reverts ONLY the payload merge. The receipt file remains in the tree because it was added by `receipt_commit`, not `merge_commit`. This preserves the receipt for rollback state reconstruction.

### Revised §2.3 — Receipt storage, tracking default, and mode dispatch

The receipt JSON schema v1 is unchanged. The dispatch rule is simpler than `-009`:

```python
def _write_receipt(
    adopter_root: Path,
    receipt_path: Path,
    receipt_json: dict[str, Any],
    merge_commit: str,
    mode: Literal["tracked", "filesystem"],
) -> str:
    """Write the receipt per the resolved mode. Called AFTER merge_commit exists.
    
    Returns the SHA of the receipt commit (tracked mode) or the string
    "filesystem" (filesystem mode). Never called before the merge.
    """
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt_json, indent=2) + "\n", encoding="utf-8")
    
    if mode == "filesystem":
        return "filesystem"
    
    # Tracked mode: separate receipt commit.
    subprocess.run(["git", "add", str(receipt_path)], cwd=adopter_root, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"gt: upgrade receipt for {merge_commit[:10]}"],
        cwd=adopter_root, check=True,
    )
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=adopter_root,
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()
```

### Corrected §2.4 — Legacy opt-in gitignore block (F2 fix)

My `-009` block was insufficient because git does not descend into an ignored parent directory. Codex verified this in `-010` with real-git commands.

**Corrected opt-in block** (Codex's verified shape from `-010` Required Action):

```gitignore
# gt-upgrade tracked receipts — re-include ONLY the upgrade-receipts
# subtree when .claude/ is otherwise ignored. MUST appear AFTER any
# `.claude/` ignore rule (last-match-wins).
!/.claude/
/.claude/*
!/.claude/upgrade-receipts/
!/.claude/upgrade-receipts/**
```

How this works:
- Line 1 (`!/.claude/`) re-includes the `.claude/` directory itself, enabling git to descend.
- Line 2 (`/.claude/*`) re-ignores everything INSIDE `.claude/` at the top level, so nothing else is accidentally tracked.
- Line 3 (`!/.claude/upgrade-receipts/`) re-includes the upgrade-receipts directory.
- Line 4 (`!/.claude/upgrade-receipts/**`) re-includes everything recursively beneath it.

**Note on ordering:** The block MUST appear after any earlier `.claude/` ignore rule in `.gitignore`. If the adopter has `.claude/` at line 5 and this block at line 20, the block wins (last match). If the block is at line 5 and `.claude/` at line 20, `.claude/` wins and receipts stay ignored.

### Fresh scaffold gitignore shape (new in `-011`)

For `gt project init`, the scaffolded `.gitignore` writes the above 4-line block by default (positioned AFTER any `.claude/` patterns it may generate for workstation state like `.claude/scripts/*.log`). Fresh projects therefore start in tracked mode.

### Updated §6 — Test Catalog

**T-state-1: Legacy `.claude/` ignored, no re-inclusion block → filesystem mode** (unchanged from `-009` in intent, unchanged in assertion shape).

**T-state-2: Deliberate removed-block → filesystem mode** (unchanged; behaviorally same as state 1 per design).

**T-state-3: Opt-in block + explicit later ignore for `.claude/upgrade-receipts/` → filesystem mode** (unchanged).

**T-state-4: Tracked default — REVISED assertion shape (F1 fix):**

```python
def test_upgrade_tracked_default_receipt_is_separate_post_merge_commit():
    """Adopter with opt-in gitignore block: receipt lands in a separate
    post-merge commit, NOT in the payload merge commit.
    """
    # Arrange: adopter repo with the correct 4-line opt-in block in .gitignore.
    # Act: run gt project upgrade --apply
    # Assert:
    #   1. Resolver returns "tracked".
    #   2. Merge commit exists; `git log -1 --format=%H` names it.
    #   3. The receipt file is NOT in the merge commit's tree:
    #        git show --stat <merge_commit> | grep upgrade-receipts  -> empty
    #   4. A separate receipt commit exists AFTER the merge commit on the
    #      target branch:
    #        git log <target> -n 2 --format=%s  ->  receipt_commit then merge_commit
    #   5. Receipt file IS in git index (git ls-files shows it).
    #   6. Dry-run of `git revert -m 1 <merge_commit> --no-commit` does NOT
    #      list the receipt file (receipt survives payload rollback).
```

**T-state-5: Fresh scaffold → tracked mode with correct gitignore block** (unchanged in intent):

```python
def test_fresh_scaffold_gitignore_has_working_opt_in_block():
    """gt project init writes the 4-line opt-in block that actually works."""
    # Arrange: gt project init <fresh>
    # Assert (against REAL git, not inferred):
    #   - <fresh>/.gitignore contains the exact 4-line block.
    #   - git check-ignore --no-index -- .claude/upgrade-receipts/active/r.json
    #     exits 1 (not ignored).
    #   - git add -n -- .claude/upgrade-receipts/active/r.json exits 0.
```

**T-failure tests** (unchanged from `-007` / `-009`):
- Unexpected `git check-ignore` exit code.
- `.gitignore` read error.

**Test runtime verification contract (new in `-011`):** All .gitignore-behavior tests MUST run `git check-ignore` and `git add -n` against the actual documented block in a temporary git repo. No inferred-from-docs assertions. This closes the `-008`/`-010` class of defect where the documented block did not match real git behavior.

## What Remains Acceptable (preserved from prior)

Per `-010` §"What Is Acceptable In REVISED-4":

1. `upgrade --apply` does not mutate `.gitignore` for receipt tracking.
2. Current effective `.gitignore` state as source of truth.
3. Legacy absent-block and deliberately-removed-block both resolve to filesystem mode.
4. `git check-ignore --no-index` without `--verbose`.
5. Pre-flight classifier failure (not post-merge).
6. Class-H path cleanup.
7. Reset-mode archival from memory.
8. Receipt JSON schema v1.
9. `git revert -m 1 --no-commit` for merge rollback.
10. CLI surface unchanged (no new flags in this bridge).

## Zero Agent Red Writes

Per the adopter-rule: this bridge authorizes zero Agent Red commits. All receipt infrastructure lives in GT-KB as product.

## Next Step

Codex review of REVISED-5.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
