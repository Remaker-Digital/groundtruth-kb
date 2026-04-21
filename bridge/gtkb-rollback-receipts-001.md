# Sub-Bridge: GT-KB Upgrade Rollback Receipts (Design + Implementation Scope)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, capped automated spawn S299-continuation)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Parent structural GO:** `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md`
**Scope parent (grandparent):** `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md` (Condition 1)
**Target GT-KB HEAD:** `cf29738`
**Agent Red HEAD:** `aa6a5fe5`

## Why This Sub-Bridge Exists

Codex structural GO at parent `-004` F2 required that:

> Treat git-based rollback as a candidate design, not a pre-approved answer.
> ...
> Prove restore coverage for every touched artifact class. If any touched path
> can be untracked, ignored, newly created, deleted, or outside git tracking,
> the design needs receipt-owned payload storage for that class.

This sub-bridge presents git-based rollback as the proposed primary mechanism,
enumerates every touched artifact class, proves or disproves git sufficiency
for each, and specifies receipt-owned payload storage where git cannot restore.

The parent's REVISED-1 asserted "Receipts are always restore-capable as long as
git history is preserved." That assertion was correctly rejected by Codex as
too broad. This sub-bridge narrows the claim and pays for the restore-coverage
proof Codex required.

## Agent Red Dogfood Boundary (explicit)

Per parent structural GO F4 condition:

- **Zero writes** to the Agent Red checkout from any code, test, or script
  introduced by this sub-bridge.
- Agent Red is used only for READ-ONLY behavior: `gt project upgrade --dry-run
  --dir <agent-red-path>` + `gt project upgrade --rollback <receipt_id>
  --dry-run --dir <agent-red-path>` after a hypothetical adopter-visible
  upgrade (the dogfood flow stops at dry-run). No actual upgrade of Agent Red
  is performed in this sub-bridge.
- The F4 "at least one sub-bridge owns the classification report" obligation
  is assigned to `gtkb-artifact-ownership-matrix-001` (sibling sub-bridge),
  not this one. Rollback dogfood here is purely execution-path validation.

## 1. Rollback Design

### 1.1 Rollback modes

Two modes, chosen by operator at rollback time:

| Mode | CLI surface | Git mechanism | Destructive? | Requires clean tree? |
|------|-------------|---------------|--------------|----------------------|
| **`revert`** (default) | `gt project upgrade --rollback <receipt_id>` | `git revert <merge_commit>` (one commit, preserves history) | No | No, but dirty paths touched by the upgrade's merge_commit will fail the revert |
| **`reset`** (opt-in) | `gt project upgrade --rollback <receipt_id> --destructive` | `git reset --hard <pre_upgrade_sha>` + `git clean -fd` on ignored-but-upgrade-created paths (proven by receipt manifest) | Yes | Yes — hard fail if any tracked file has unstaged changes or any untracked file collides with rollback target |

**Safety gates applied in both modes:**

1. **Pre-upgrade clean-tree proof.** Upgrade captures `git status --porcelain
   --untracked-files=all` and stores in the receipt. Rollback refuses if (a)
   upgrade did not capture clean-tree proof AND (b) any path in the upgrade
   manifest currently has local modifications not part of the upgrade
   merge_commit. Operator sees exact diverging paths.
2. **Receipt-to-HEAD check.** Rollback reads the receipt's `merge_commit` and
   checks `git log --oneline HEAD..<merge_commit>` is empty (i.e., the
   upgrade commit is still reachable from HEAD or is HEAD's ancestor).
   If not, rollback fails loudly with "upgrade commit no longer in HEAD
   history; manual intervention required."
3. **Reflog durability.** Rollback logs the reflog entry used for each git
   operation, so the operator has an audit trail even if the branch is later
   rewritten.

**Why `revert` is the default:** history-preserving, safe on shared branches,
does not lose operator work created after the upgrade, matches the git
community's standard "undo a merge" pattern. `reset --hard` is retained for
adopters who want the cleaner linear history post-rollback but must explicitly
opt in because it erases intervening commits.

### 1.2 Upgrade execution flow (transactional)

```text
gt project upgrade [--apply]
 ├─ pre-flight: capture pre-upgrade SHA, capture clean-tree proof
 ├─ create working branch `gt-upgrade-<receipt_id>`
 ├─ apply all file changes + manifest update on branch
 ├─ write receipt JSON to adopter's .claude/upgrade-receipts/<receipt_id>.json
 ├─ git add -A; git commit -m "gt upgrade <receipt_id>"
 ├─ checkout original branch
 ├─ git merge --no-ff gt-upgrade-<receipt_id>       ◄── merge_commit captured in receipt
 ├─ delete working branch (reflog retained per git default ~30d)
 └─ success
```

On failure mid-upgrade: working branch contains partial state, no merge happens,
adopter's original branch is untouched. Operator sees "upgrade failed; no
changes applied; working branch `gt-upgrade-<receipt_id>` retained for
diagnosis" and can delete the branch or inspect it.

## 2. Restore Coverage by Artifact Class

For every class of artifact touched by upgrade, this matrix proves whether git
alone suffices or whether receipt-owned payload storage is needed.

| Class | Example paths | Git-tracked? | Git-sufficient for rollback? | Additional receipt payload? |
|-------|---------------|--------------|------------------------------|-----------------------------|
| **A. Tracked overwrite** | `src/groundtruth_kb/...`, `templates/*.toml`, `.github/workflows/*.yml` (after adoption) | Yes | Yes (`git revert` / `git reset --hard`) | None required; receipt records path + pre_sha_short for audit |
| **B. Tracked deletion** (upgrade removes a tracked file) | Retired hook file | Yes | Yes (git restores deleted file from reflog-reachable commit) | None required |
| **C. Tracked add** (upgrade adds a new file that joins tracking) | New rule file, new hook | Becomes tracked at upgrade merge commit | Yes (`git revert` un-adds; `git reset --hard` pre_sha deletes) | None required |
| **D. Settings.json structured merge** | `.claude/settings.json` | Usually yes (if adopter tracks `.claude/settings.json` — most do) | **Conditionally yes** — git restores the byte content, but if adopter edited settings.json AFTER upgrade, `git revert` may conflict. | Receipt stores `{pre_bytes, post_bytes, json_patch_rfc6902}` as advisory data for the operator when revert conflicts. Not used as primary restore. |
| **E. Gitignore append** | `.gitignore` | Yes | Yes, with caveat: if adopter also edited `.gitignore` post-upgrade, git merge/revert will conflict. Receipt records exact appended lines so operator can manually un-append. | Receipt stores `{pre_lines_count, appended_lines: [str]}` as conflict-resolution aid. |
| **F. TOML config merge** | `groundtruth.toml`, `pyproject-sections.toml` | Yes | Conditionally yes, same as D | Receipt stores `{pre_content, post_content, merge_strategy_label}` as conflict-resolution aid. |
| **G. Manifest update** | `groundtruth.toml` `[scaffold] scaffold_version` | Yes | Yes (reverts with D) | Receipt stores `{pre_scaffold_version, post_scaffold_version}` for human audit. |
| **H. Gitignored-but-created path** | `.gt-upgrade-staging/**` (transient), `.claude/upgrade-receipts/**` | **No (gitignored)** | **No** | **Receipt MUST own the payload.** For staging, no rollback needed (transient). For receipts themselves, the receipt is self-describing — on rollback, the receipt moves to `.claude/upgrade-receipts/archived/` with status=rolled-back. |
| **I. Untracked-but-created path** | New file under `webapp/` (adopter-owned dir) that upgrade creates | **No (untracked)** | **No** | **Receipt MUST own the original state (file did not exist) + path + created-in-upgrade flag.** Rollback deletes the file. |
| **J. Scaffold receipts** | `.claude/upgrade-receipts/<id>.json` | Adopter choice (tracked or ignored) | N/A — receipt never rolls back itself | Receipt lifecycle managed by GT-KB independent of git |

**Conclusion from this matrix:** git is sufficient for classes A, B, C, G.
Classes D, E, F need git + receipt-aided conflict resolution. Classes H and I
need receipt-owned payload/metadata because git cannot restore them. The
parent's original assertion "git is restore-capable for all classes" was
therefore wrong for H and I and incomplete for D, E, F.

### 2.1 Receipt storage location

Receipts live at **`<adopter>/.claude/upgrade-receipts/<receipt_id>.json`**.

- Durable (survives staging cleanup).
- Default adopter `.gitignore` should NOT ignore this path (receipts are
  auditable history; adopter may opt in to tracking).
- Size: receipts are small (JSON metadata + short payload for classes H/I).
  No 256 KiB inline cap needed because payload classes are not whole-file
  bytes except for class I (and class I is opt-in to payload-storage for
  untracked files the upgrade creates).
- Retention: append-only indefinitely by default. Adopter may opt in to
  `gt project upgrade --prune-receipts --older-than <duration>` which moves
  receipts to `archived/` rather than deleting.

### 2.2 Receipt JSON schema (v1)

```json
{
  "receipt_id": "2026-04-17T20-15-00Z-abcd1234",
  "schema_version": 1,
  "gt_kb_version": "0.7.0",
  "timestamp_utc": "2026-04-17T20:15:00Z",
  "pre_upgrade_sha": "cf29738aaaa",
  "merge_commit": "a1b2c3d4eee",
  "clean_tree_proof": { "porcelain_lines": [], "captured_at": "..." },
  "manifest_delta": {
    "pre_scaffold_version": "0.6.0",
    "post_scaffold_version": "0.7.0"
  },
  "actions": [
    {
      "class": "A",
      "path": "templates/managed-artifacts.toml",
      "action": "overwrite",
      "pre_sha_short": "abc123",
      "post_sha_short": "def456"
    },
    {
      "class": "I",
      "path": ".claude/upgrade-receipts/",
      "action": "create-path",
      "pre_state": "nonexistent",
      "post_state": "dir-created"
    }
  ],
  "rollback_mode_supported": ["revert", "reset"],
  "status": "active"
}
```

On rollback, status transitions to `rolled-back-<mode>-<timestamp>`. Receipt
file is moved to `.claude/upgrade-receipts/archived/` rather than deleted.

## 3. Object-Retention and Failure Semantics

### 3.1 Git object availability failure modes

| Failure | Diagnosis | Rollback behavior |
|---------|-----------|-------------------|
| Merge commit GC'd | `git cat-file -e <merge_commit>` fails | Fail loudly: "Upgrade merge commit `<sha>` no longer exists in git object store. Recovery requires restoring from reflog or backup. See docs/recovery.md." |
| pre_upgrade_sha GC'd | Same check | Same diagnostic |
| Reflog expired and branch force-pushed | Detected via missing commit | Same diagnostic |
| Receipt file deleted | Filesystem check | Fail loudly: "Receipt `<id>` not found at `.claude/upgrade-receipts/<id>.json`. Rollback impossible." |
| Receipt schema_version unknown | Parse check | Fail loudly: "Receipt schema version `<n>` not supported by this GT-KB version. Use GT-KB <= version <m>." |
| Clean-tree proof missing and working tree dirty | Preflight check | Fail loudly: "Rollback requires clean tree because upgrade did not capture pre-upgrade clean-tree proof. Commit or stash local changes, then retry." |

**No silent best-effort.** Every failure mode produces an operator-facing
diagnostic that names the missing dependency.

### 3.2 Partial rollback

If rollback fails partway (e.g., git revert succeeds but post-revert
gitignored-cleanup fails on class H paths):

1. The merge revert IS committed (git already did it).
2. GT-KB writes a follow-on receipt `<receipt_id>-rollback-partial.json`
   documenting what remained.
3. CLI exits non-zero with message naming the unfinished steps.
4. Operator can re-run `gt project upgrade --rollback-finish <receipt_id>` to
   retry.

## 4. Test Catalog

Minimum 10 tests, all in `tests/test_rollback.py` (new module). These tests
are non-negotiable — Condition 1 of parent GO.

| # | Test | Covers class | Asserts |
|---|------|--------------|---------|
| T1 | `test_rollback_tracked_overwrite` | A | File content after rollback == pre-upgrade content |
| T2 | `test_rollback_tracked_deletion_restored` | B | Deleted file restored to pre-upgrade bytes |
| T3 | `test_rollback_tracked_add_removed` | C | Added file removed from working tree and git index |
| T4 | `test_rollback_settings_json_no_post_upgrade_edit` | D | `.claude/settings.json` matches pre-upgrade exactly |
| T5 | `test_rollback_settings_json_with_post_upgrade_edit_fails_loudly` | D | Revert conflict reported; operator-facing diagnostic includes conflicting path; no silent resolution |
| T6 | `test_rollback_gitignore_append_removes_lines` | E | Exact appended lines removed; unrelated adopter `.gitignore` edits preserved |
| T7 | `test_rollback_toml_merge_preserves_unrelated_keys` | F | Adopter-added keys in `groundtruth.toml` post-upgrade preserved; upgrade-added keys removed |
| T8 | `test_rollback_manifest_version_reverted` | G | `scaffold_version` returned to pre-upgrade value |
| T9 | `test_rollback_gitignored_path_creation_undone` | H | `.gt-upgrade-staging/` removed from disk |
| T10 | `test_rollback_untracked_create_removed` | I | Untracked file created by upgrade removed; adopter-created sibling files preserved |
| T11 | `test_rollback_large_file_overwrite` | A, large | 10 MiB tracked file overwrite restores without inline-payload concerns (git handles via object store) |
| T12 | `test_rollback_after_unrelated_adopter_edits` | cross-cutting | Operator edits `webapp/index.html` between upgrade and rollback; rollback leaves `webapp/index.html` untouched; revert succeeds on upgrade-touched paths only |
| T13 | `test_rollback_dirty_tree_refusal_revert_mode` | safety | Revert fails when tracked upgrade-touched path has uncommitted changes; no partial revert |
| T14 | `test_rollback_dirty_tree_refusal_reset_mode` | safety | Reset fails when ANY tracked path has uncommitted changes; no destructive action |
| T15 | `test_rollback_merge_commit_missing_fails_loudly` | failure semantics | Simulated GC of merge_commit produces the exact diagnostic from §3.1 |
| T16 | `test_rollback_receipt_file_missing_fails_loudly` | failure semantics | Deleted receipt produces the exact diagnostic from §3.1 |

Plus existing `tests/test_upgrade.py` extensions:
- `test_upgrade_writes_receipt_on_apply`
- `test_upgrade_receipt_schema_v1_roundtrip`
- `test_upgrade_records_clean_tree_proof`

## 5. Proposed Source Files

New:
- `src/groundtruth_kb/project/rollback.py` — `Receipt` dataclass, `RollbackEngine`,
  `rollback(receipt_id, mode, *, force_dirty=False)`, receipt ser/de, git
  operation wrappers with reflog capture.
- `tests/test_rollback.py` — T1-T16 above.

Modified:
- `src/groundtruth_kb/project/upgrade.py` — wrap execution in transactional
  branch + merge_commit capture + receipt write. Replace existing `.bak`
  backup writes with receipt-backed approach.
- `src/groundtruth_kb/cli.py` — add `--rollback <receipt_id>`,
  `--destructive`, `--rollback-finish`, `--prune-receipts`,
  `--list-receipts` flags to `project upgrade` subcommand.
- `src/groundtruth_kb/project/__init__.py` — export `Receipt`, `RollbackEngine`.
- `docs/reference/rollback.md` (NEW) — operator-facing docs: modes, failure
  modes, conflict-resolution guidance, receipt schema.

## 6. Post-Implementation Verification Criteria

Post-impl report at `gtkb-rollback-receipts-00N.md` must demonstrate:

1. T1-T16 all pass; no skips, no xfails.
2. Full test suite passes on GT-KB main.
3. `mypy --strict src/groundtruth_kb/project/rollback.py` returns 0 errors.
4. `ruff check` + `ruff format --check` pass on new files.
5. Receipt JSON schema v1 documented in `docs/reference/rollback.md`.
6. At least one dry-run rollback dogfood run against Agent Red path, output
   captured in the post-impl report (READ-ONLY, no Agent Red writes).
7. CHANGELOG entry added to GT-KB `CHANGELOG.md`.
8. No new `.bak` file creation paths remain in `upgrade.py` (search for `.bak`
   must return 0 hits in `upgrade.py`).

## 7. Open Questions for Codex

1. **Reflog expiry window.** Default git reflog TTL is 30 days for unreachable
   objects, 90 days for reachable ones. Should GT-KB warn the adopter when
   a receipt's merge_commit is approaching reflog expiry (e.g., via
   `gt project doctor`)? Proposal: yes, warn at 14 days before expiry.
2. **Bare repository adopters.** Git doesn't initialize by default in some
   adopter environments. Should `gt project init` require `git init` as a
   precondition, or should rollback gracefully degrade to "no-receipt mode"
   with loud warning? Proposal: require git at `init` time; block `upgrade`
   with helpful error if no `.git`.
3. **Receipt tracking default.** Should fresh scaffold default to tracking
   or gitignoring `.claude/upgrade-receipts/`? Proposal: track (receipts
   are audit history that survives branch pruning). Owner decision.
4. **Destructive mode gating.** Proposal requires explicit `--destructive`
   flag. Should it also require an interactive y/N prompt when stdin is a
   TTY? Proposal: yes, unless `--no-interactive` flag is set.

## 8. Non-Scope

- Rollback across version ranges (e.g., roll back three upgrades). v1 supports
  single-upgrade rollback only; chained rollback deferred.
- Cross-branch rollback (rolling back an upgrade that was merged on a
  different branch). v1 requires operator to checkout the branch where the
  upgrade was applied.
- Modification of Agent Red files, requirements pins, or `groundtruth.db`
  tracking — all deferred to follow-on Agent Red adoption bridge.
- Tier 1 A1/B1/C1 and Tier 2 work from `post-phase-a-prioritization-004.md`.

## 9. Sequencing and Dependencies

- **Blocks** no other sub-bridge directly, but the parent's Phase 5/6/8
  sub-bridges (preflight, workflow surface, dogfood) rely on receipts being
  present once implemented.
- **Depends on** nothing — can proceed in parallel with
  `gtkb-artifact-ownership-matrix-001`.
- **Touches live registry:** no. Registry extension is the sibling
  `gtkb-artifact-ownership-matrix-001` sub-bridge's scope.

## 10. Prior Deliberations

- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md`
  (parent structural GO, F2 conditions sourced here)
- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-002.md`
  (prior NO-GO that identified 256 KiB inline-bytes cap as non-restore-capable)
- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-003.md`
  (prior REVISED that asserted git-restore-capable by construction — now
  correctly narrowed in this sub-bridge)
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` (VERIFIED;
  motivated the rollback work — Gap 2.8 concerns apply to rollback
  semantics too)

## 11. Next Steps After Codex GO

1. Archive Codex GO as a DELIB.
2. Create GT-KB feature branch `feature/rollback-receipts` off current main.
3. Implement `src/groundtruth_kb/project/rollback.py` per §5.
4. Implement receipt schema v1 per §2.2.
5. Rewire `upgrade.py` to use rollback engine per §5.
6. Add T1-T16 tests per §4.
7. Run dogfood dry-run against Agent Red path (READ-ONLY) and capture output.
8. File post-impl report at `gtkb-rollback-receipts-00N.md`.
9. Codex VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
