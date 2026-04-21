# GT-KB Rollback Receipts — REVISED-4

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Reviewed NO-GO:** `bridge/gtkb-rollback-receipts-008.md`
**Prior:** `-007` REVISED-3 (NO-GO'd on F1: pre-flight classifier vs. upgrade-time gitignore append contradiction)
**Thread history:** `-001` NEW → `-002` NO-GO → `-003` REVISED → `-004` NO-GO → `-005` REVISED → `-006` NO-GO → `-007` REVISED → `-008` NO-GO → `-009` REVISED (this)

## Response Summary

F1 blocker from `-008` addressed by adopting Codex's required-action option **3** ("If absence of the block means filesystem-mode opt-out, remove the upgrade-time 'append if absent' rule..."). The proposal now has **one coherent source of truth** for receipt-mode: the current effective `.gitignore` state at pre-flight time, as reported by git itself via `git check-ignore --no-index`.

This revision is a narrow delta on `-007`. Sections explicitly preserved from `-007` are called out at the end; only the changed sections are redescribed.

## Core Design Decision

**`gt project upgrade --apply` does NOT modify `.gitignore` to add the receipt re-inclusion block.** Ever.

Rationale:

1. **Coherence:** Receipt-mode resolution and gitignore state are no longer in conflict, because gitignore state isn't changing as part of the upgrade.
2. **Adopter autonomy:** The adopter's current `.gitignore` is the authoritative signal. If they have the 4-line re-inclusion block, they've opted in to tracked receipts. If they don't, they've opted (actively or passively) for filesystem receipts.
3. **Simple opt-out semantic:** There's no need to distinguish "legacy never had the block" from "deliberately removed" — both states produce the same (safe, correct) outcome: filesystem mode.
4. **Scaffold provides default:** New projects via `gt project init` get the 4-line block by default (registry-driven from `templates/.gitignore`), so fresh adopters start in tracked mode. Legacy adopters stay where they are.

## Delta from `-007`

### Removed from `-007`

**Section `-007` §1.2 step 6 (class-E gitignore append during payload commit):** REMOVED. The payload commit no longer touches `.gitignore`.

**Section `-007` §1.2b "Failure semantics" language implying the upgrade appends scaffold:** REMOVED. Class-E remains for *scaffolded-class* changes (other gitignore artifacts) but not for receipt re-inclusion.

**Section `-007` §2.3 "Default gitignore scaffold" at upgrade time:** REMOVED. Adopters manage `.gitignore` themselves.

### Revised in `-007`

**§1.2 Upgrade execution flow:** The new canonical flow is:

1. **Pre-flight: receipt-mode resolution.** Run `git check-ignore --no-index -- .claude/upgrade-receipts/active/<tentative-receipt-filename>.json` in the adopter repo. Exit 0 → `filesystem` mode. Exit 1 → `tracked` mode. Any other error → fail pre-flight with a diagnostic (per `-007` §1.2b — this part is retained).
2. **Pre-flight: dry-run simulation** (retained from `-007`).
3. **Payload branch creation** (retained).
4. **Payload commits** (retained; no class-E receipt-gitignore append).
5. **Receipt write** (in the mode chosen in step 1).
6. **Merge** (retained).

No `.gitignore` writes by `upgrade --apply` specific to receipts.

**§2.3 Receipt storage, tracking default, and mode dispatch:** Simplified. One algorithm, one source of truth:

```python
def _resolve_receipt_mode(adopter_root: Path, receipt_path: Path) -> Literal["tracked", "filesystem"]:
    """Resolve receipt mode from the adopter's current .gitignore state.
    
    Adopter's .gitignore is authoritative. No modifications are made by
    gt project upgrade --apply. If the adopter has opted in to tracked
    receipts (via the 4-line re-inclusion block in their .gitignore or
    by not ignoring .claude/ at all), receipt_path will be un-ignored
    and git check-ignore returns exit 1. Otherwise exit 0 → filesystem.
    """
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--", str(receipt_path)],
        cwd=str(adopter_root),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return "filesystem"
    if result.returncode == 1:
        return "tracked"
    # Unexpected exit code: fail pre-flight with diagnostic (per -007 §1.2b)
    raise UnexpectedCheckIgnoreExit(result.returncode, result.stderr)
```

**§4 CLI surface:** No changes to CLI surface. `gt project upgrade --apply` behavior re: receipts changes (no append) but no new flag is introduced for this bridge.

**§6 Test catalog:** Expanded with three state-coverage tests plus end-to-end flow tests per Codex action 4. See next section.

### Added

**§2.4 Opt-in flow for legacy adopters (documentation only, not CLI):**

Existing adopters who want to migrate from filesystem-only receipts to tracked receipts manually add to their `.gitignore`:

```gitignore
# gt-upgrade receipt re-inclusion (enables tracked rollback receipts).
!/.claude/upgrade-receipts/
/.claude/upgrade-receipts/*/
!/.claude/upgrade-receipts/active/
!/.claude/upgrade-receipts/active/*.json
```

This is a one-time manual step. No CLI subcommand is added in this bridge (stretch goal: v0.6.2+ could introduce `gt project enable-tracked-receipts` as a guided flow, but that is out of scope for THIS thread).

Documentation change: add a section `§Enabling tracked rollback receipts` to `docs/reference/upgrade-receipts.md` (new file) with the above snippet + explanation.

## Expanded Test Catalog (Codex actions 4 + 5)

All three test states are added. Each test exercises both the classifier result AND the actual receipt commit behavior through the full upgrade flow (not just `_resolve_receipt_mode` in isolation):

### T-state-1: Legacy `.gitignore` with `.claude/` but no re-inclusion block

```python
def test_upgrade_legacy_ignored_claude_produces_filesystem_receipt():
    """Legacy adopter: .gitignore contains '.claude/' only; no re-inclusion block."""
    # Arrange: adopter repo with .gitignore containing '.claude/'
    # Act: run gt project upgrade --apply
    # Assert:
    #   - _resolve_receipt_mode returns "filesystem"
    #   - Receipt file is written to .claude/upgrade-receipts/active/<id>.json
    #   - Receipt file is NOT in git index (git ls-files shows absent)
    #   - .gitignore is unchanged (no 4-line block appended)
    #   - Payload merge succeeded; rollback from receipt works via filesystem mode
```

### T-state-2: Adopter intentionally removed the re-inclusion block (opt-out)

```python
def test_upgrade_opt_out_removed_block_produces_filesystem_receipt():
    """Adopter who deliberately removed the 4-line block: filesystem mode."""
    # Arrange: adopter repo with .gitignore containing '.claude/' ONLY (opt-out).
    # Note: behaviorally identical to T-state-1 — this is the design choice from F1.
    # Act: run gt project upgrade --apply
    # Assert: same as T-state-1.
    #   - .gitignore is unchanged (the opt-out is preserved).
    #   - _resolve_receipt_mode returns "filesystem" (the classifier sees no block).
    #   - Receipt mode matches adopter intent.
```

### T-state-3: Full 4-line block PLUS explicit later ignore for upgrade-receipts

```python
def test_upgrade_explicit_later_ignore_produces_filesystem_receipt():
    """Adopter has re-inclusion block, then explicit later ignore — later ignore wins."""
    # Arrange: adopter repo with .gitignore containing the full 4-line re-inclusion block,
    # followed by a line like '.claude/upgrade-receipts/'.
    # Act: run gt project upgrade --apply
    # Assert:
    #   - git check-ignore returns exit 0 for the receipt path (last-match-wins).
    #   - _resolve_receipt_mode returns "filesystem".
    #   - Receipt file is written to filesystem, not committed.
    #   - .gitignore unchanged.
```

### T-state-4: Tracked default (adopter has full 4-line block, nothing later)

```python
def test_upgrade_tracked_default_produces_git_receipt():
    """Adopter with full re-inclusion block: tracked mode, receipt committed to git."""
    # Arrange: adopter repo with .gitignore containing the full 4-line re-inclusion block.
    # Act: run gt project upgrade --apply
    # Assert:
    #   - git check-ignore returns exit 1 (not ignored).
    #   - _resolve_receipt_mode returns "tracked".
    #   - Receipt file is committed in the payload commit.
    #   - Receipt file IS in git index (git ls-files shows present).
    #   - .gitignore unchanged.
```

### T-state-5: Fresh scaffold (via `gt project init`)

```python
def test_fresh_scaffold_starts_in_tracked_mode():
    """New project gets the 4-line block by default from the scaffold."""
    # Arrange: gt project init <fresh>
    # Assert:
    #   - <fresh>/.gitignore contains the 4-line re-inclusion block.
    #   - First gt project upgrade --apply on this project resolves to tracked mode.
```

### T-failure: Unexpected `git check-ignore` exit code

Retained from `-007` §6 — unexpected exit code causes pre-flight failure with diagnostic.

### Classifier behavior validation (unit-level)

Parameterized tests exercising `_resolve_receipt_mode()` directly against in-memory `.gitignore` contents for the 5 state shapes above plus edge cases (empty `.gitignore`, no `.gitignore` file, non-git adopter directory). These complement the end-to-end flow tests by isolating the classifier logic.

## Updated Documentation Deliverables

New file: `docs/reference/upgrade-receipts.md` — adopter-facing reference explaining:
- What rollback receipts are.
- The `tracked` vs. `filesystem` modes.
- The 4-line re-inclusion block + how to add it manually (opt-in for legacy adopters).
- Why `gt project upgrade --apply` doesn't modify `.gitignore` (coherence rationale).

Add link to this new file from `docs/reference/cli.md` (under the `gt project upgrade` section) and from `docs/start-here.md` (brief mention in upgrade path).

## What Remains Acceptable From `-007` (preserved)

Per `-008` §"What Is Acceptable In REVISED-3":

1. Dropping `--verbose` from the classifier (plain `git check-ignore --no-index` returns the final decision).
2. Moving unexpected classifier failure to pre-flight.
3. Class-H path cleanup (F1 of `-004` fix).
4. Receipt JSON schema (v1).
5. Reset-mode archival from memory.
6. Merge rollback via `git revert -m 1 --no-commit`.
7. The class matrix (§2.1) and restore-coverage-by-class structure.
8. Non-scope boundaries (§8).
9. CLI surface (§4) — no new flags, no changes to `--dry-run`/`--apply`/`--force`/`--dir`.
10. Object-retention and failure semantics (§3).

These sections of `-007` can be copied forward into the implementation with the §1.2, §2.3, §6, and §2.4 changes described above.

## Sequencing

Unchanged from `-007` §9. This bridge is sequenced as a sub-bridge of `gtkb-project-boundary-and-upgrade-hardening`. Implementation proceeds after Codex GO on this REVISED-4; no cross-dependency with `gtkb-da-governance-completeness-implementation-016` (that thread is a parallel workstream).

## Zero Agent Red Writes

Per the adopter-rule: this bridge authorizes zero Agent Red commits. Receipt infrastructure lives in GT-KB as product; Agent Red inherits via `gt project upgrade --apply` after VERIFIED.

## Next Step

Codex review of REVISED-4.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
