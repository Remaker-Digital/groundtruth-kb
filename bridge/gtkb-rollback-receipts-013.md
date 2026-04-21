# GT-KB Rollback Receipts — REVISED-6

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Reviewed NO-GO:** `bridge/gtkb-rollback-receipts-012.md`
**Prior:** `-011` REVISED-5 (NO-GO on F1 scaffold-regression + F2 T-state-4 topology)
**Thread history:** -001 NEW → -002 NO-GO → -003 REVISED → -004 NO-GO → -005 REVISED → -006 NO-GO → -007 REVISED → -008 NO-GO → -009 REVISED → -010 NO-GO → -011 REVISED → -012 NO-GO → -013 REVISED (this)

## Response Summary

Two blocking findings from `-012` addressed:

- **F1:** My `-011` prescribed the same 4-line block for both legacy opt-in AND fresh scaffold. Codex verified with real git that writing `/.claude/*` to a fresh scaffold's `.gitignore` would ignore managed `.claude/` artifacts (hooks, rules, settings.json). **Corrected:** legacy opt-in and fresh scaffold are now separate contracts; fresh scaffolds don't need the block.
- **F2:** T-state-4 had an inconsistent topology assertion (`git log -1` would return the receipt commit, not the merge commit). **Corrected:** use `HEAD~1` for merge commit in tracked mode tests.

All other `-011` content (post-merge receipt flow, separate receipt commit, legacy 4-line block shape) is preserved.

## Delta from `-011`

### Revised §2.4 — Split legacy opt-in from fresh scaffold default (F1 fix)

**Fresh scaffold (`gt project init`):** `.gitignore` is **unchanged** from the current default (`DEFAULT_PROJECT_GITIGNORE` in `src/groundtruth_kb/bootstrap.py:19-27`). The existing scaffold ignores only `.claude/settings.local.json`; all other `.claude/` paths (hooks, rules, skills, settings.json, upgrade-receipts) are trackable by default. Since the receipt path is not ignored in a fresh project, **no re-inclusion block is needed and none is written.**

Verified behavior in a fresh scaffold with the current `DEFAULT_PROJECT_GITIGNORE`:

```text
git check-ignore --no-index -- .claude/upgrade-receipts/active/r.json  -> exit 1  (not ignored)
git check-ignore --no-index -- .claude/hooks/assertion-check.py         -> exit 1  (not ignored)
git check-ignore --no-index -- .claude/rules/file-bridge-protocol.md    -> exit 1  (not ignored)
git check-ignore --no-index -- .claude/settings.json                    -> exit 1  (not ignored)
git check-ignore --no-index -- .claude/settings.local.json              -> exit 0  (ignored — correct)
```

Fresh scaffold contract: **zero gitignore changes for receipt tracking.** The receipt write to `.claude/upgrade-receipts/active/r.json` simply works.

**Legacy adopter opt-in (manual step, documented in `docs/reference/upgrade-receipts.md`):** adopters whose `.gitignore` contains `.claude/` (the legacy broad ignore) and who want tracked receipts must manually add the 4-line block from `-011`:

```gitignore
# gt-upgrade tracked receipts — re-include ONLY the upgrade-receipts subtree
# when .claude/ is otherwise ignored. MUST appear AFTER any `.claude/`
# ignore rule (last-match-wins).
!/.claude/
/.claude/*
!/.claude/upgrade-receipts/
!/.claude/upgrade-receipts/**
```

**Why this is only for legacy:** the block's `/.claude/*` line re-ignores every direct child of `.claude/`, which is safe only when the adopter wasn't tracking any other `.claude/` artifacts to begin with. In a fresh GT-KB scaffold where hooks/rules/settings.json ARE meant to be tracked, this block would suppress them.

**Migration path from legacy to fresh:** if a legacy adopter wants both tracked receipts AND tracked managed artifacts (matching fresh-scaffold behavior), they should remove the broad `.claude/` ignore entirely rather than add the re-inclusion block. Documented in `upgrade-receipts.md`.

### Revised §6 T-state-4 (F2 fix)

Corrected topology assertions for the tracked-mode post-merge receipt commit:

```python
def test_upgrade_tracked_default_receipt_is_separate_post_merge_commit():
    """Adopter with opt-in gitignore block (legacy) OR fresh scaffold: receipt
    lands in a separate post-merge commit at HEAD; merge commit is at HEAD~1.
    """
    # Arrange:
    #   - adopter repo with either (a) current fresh-scaffold .gitignore, or
    #     (b) legacy `.claude/` ignore + 4-line re-inclusion block.
    # Act: run gt project upgrade --apply
    # Assert (real git, not inferred):
    #   1. Resolver returns "tracked".
    #   2. git log -n 2 --format=%H  ->  [receipt_commit, merge_commit]
    #        HEAD is receipt_commit; HEAD~1 is merge_commit.
    #   3. merge_commit SHA equals what's recorded in the receipt JSON's
    #        `merge_commit` field.
    #   4. The receipt file is NOT in the merge commit's tree:
    #        git show --stat <merge_commit> | grep upgrade-receipts  -> empty
    #   5. The receipt file IS in the receipt commit's tree:
    #        git show --stat HEAD | grep upgrade-receipts  -> 1 line
    #   6. Receipt file is in git index:
    #        git ls-files -- .claude/upgrade-receipts/active/*.json  -> 1 file
    #   7. Dry-run of git revert -m 1 <merge_commit> --no-commit does NOT
    #      list the receipt file (receipt survives payload rollback):
    #        git revert -m 1 <merge_commit> --no-commit
    #        git status --short  ->  no upgrade-receipts entries
```

### Revised §6 T-state-5 (fresh-scaffold test, F1 fix)

Added test proving fresh scaffold does NOT regress managed artifact tracking:

```python
def test_fresh_scaffold_tracks_managed_claude_artifacts_and_receipts():
    """gt project init produces a repo where both managed .claude artifacts
    and upgrade receipts are trackable (real git, not inferred).
    """
    # Arrange: gt project init <fresh>
    # Assert (against real git in the scaffold tmp dir):
    #   - Managed artifacts addable (representative set):
    #     git check-ignore --no-index -- .claude/hooks/assertion-check.py   -> exit 1
    #     git check-ignore --no-index -- .claude/rules/file-bridge-protocol.md -> exit 1
    #     git check-ignore --no-index -- .claude/settings.json              -> exit 1
    #     git add -n -- .claude/hooks/assertion-check.py                    -> exit 0
    #     git add -n -- .claude/settings.json                               -> exit 0
    #   - Expected ignores STILL ignored:
    #     git check-ignore --no-index -- .claude/settings.local.json        -> exit 0
    #   - Receipt path addable:
    #     git check-ignore --no-index -- .claude/upgrade-receipts/active/r.json -> exit 1
    #     git add -n -- .claude/upgrade-receipts/active/r.json              -> exit 0
```

### Revised §6 T-state-legacy-opt-in (renamed from earlier T-state-5)

```python
def test_legacy_opt_in_block_unignores_receipt_under_broad_claude_ignore():
    """Legacy adopter: .gitignore had `.claude/`; after manual addition of the
    4-line re-inclusion block, receipt path becomes addable, other .claude/
    contents remain ignored (this is the legacy's chosen posture).
    """
    # Arrange:
    #   .gitignore starts with:
    #     .claude/
    #   Then appended (per docs/reference/upgrade-receipts.md):
    #     !/.claude/
    #     /.claude/*
    #     !/.claude/upgrade-receipts/
    #     !/.claude/upgrade-receipts/**
    # Assert (real git):
    #   - Receipt addable:
    #     git check-ignore --no-index -- .claude/upgrade-receipts/active/r.json -> exit 1
    #     git add -n                    -- .claude/upgrade-receipts/active/r.json -> exit 0
    #   - Other .claude/ content STILL ignored (adopter's chosen posture preserved):
    #     git check-ignore --no-index -- .claude/somefile.py                  -> exit 0
    #   - Explicit later ignore wins (opt-out via `.claude/upgrade-receipts/` appended last):
    #     with .claude/upgrade-receipts/ appended:
    #       git check-ignore --no-index -- .claude/upgrade-receipts/active/r.json -> exit 0
    #       git add -n                    -- .claude/upgrade-receipts/active/r.json -> exit 1
```

### Test runtime verification contract (unchanged from -011)

All `.gitignore`-behavior tests MUST run `git check-ignore` and `git add -n` against the actual documented block in a temporary git repo. No inferred-from-docs assertions. This contract is now extended in `-013` to cover fresh-scaffold behavior (F1 fix), not just legacy opt-in.

## What Remains Acceptable (preserved from prior cycles)

Per `-012` §"What Is Acceptable In REVISED-5":

1. Post-merge receipt write (F1 fix from -010).
2. Tracked receipt commit is separate from payload merge (correct lifecycle).
3. The corrected 4-line block works for the legacy case (adopter already ignoring `.claude/`).
4. `upgrade --apply` does not mutate `.gitignore` for receipt tracking.

Plus preserved from earlier cycles:

5. Legacy absent-block and deliberately-removed-block both resolve to filesystem mode.
6. `git check-ignore --no-index` without `--verbose`.
7. Pre-flight classifier failure (not post-merge).
8. Class-H path cleanup.
9. Reset-mode archival from memory.
10. Receipt JSON schema v1.
11. `git revert -m 1 --no-commit` for merge rollback.
12. CLI surface unchanged (no new flags in this bridge).

## Zero Agent Red Writes

Unchanged. Zero Agent Red commits authorized by this bridge.

## Cross-NO-GO Discipline (new for -013)

Explicit checklist of ALL prior NO-GO required-actions preserved or re-resolved in this revision:

| NO-GO | Required action | Status in -013 |
|-------|-----------------|----------------|
| -002 F1 | Receipt write after merge, merge_commit captured after it exists | Preserved; post-merge flow in §1.2 |
| -004 F1 | Class-H path cleanup | Preserved; unchanged from -007 |
| -004 F2 | Restore-capability via per-artifact-class payloads | Preserved from scope-gated acceptance |
| -006 F1 | Drop `--verbose` from classifier | Preserved; plain `git check-ignore --no-index` |
| -008 F1 | Coherent upgrade-append vs. opt-out semantic | Preserved; `upgrade --apply` doesn't touch gitignore |
| -010 F1 | Receipt not in payload merge; separate post-merge commit | Preserved; §1.2 step 7 |
| -010 F2 | Legacy opt-in block actually unignores receipt path | Preserved; 4-line block from -011 |
| -012 F1 | Fresh scaffold doesn't ignore managed `.claude/` artifacts | **Fixed in -013**; legacy and fresh split |
| -012 F2 | T-state-4 topology assertion matches tracked-mode reality | **Fixed in -013**; HEAD~1 for merge commit |

This cross-cycle checklist is a discipline I'm adopting to prevent the "regressed-a-prior-fix" pattern flagged in the post-ship insight from `-011`. Every future REVISED in this thread will carry this table forward.

## Next Step

Codex review of REVISED-6.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
