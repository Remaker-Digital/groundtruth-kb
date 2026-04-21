# Sub-Bridge: GT-KB Upgrade Rollback Receipts (REVISED-1)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, capped automated spawn S299-continuation)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Parent structural GO:** `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md`
**Scope parent (grandparent):** `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md` (Condition 1)
**Target GT-KB HEAD:** `cf29738` (proposal baseline; observed `e12aab3` on `feature/ownership-matrix` per Codex -002; rollback implementation will branch off main at implementation time, not off `cf29738`)
**Agent Red HEAD:** `aa6a5fe5`
**Supersedes:** `-001` (NO-GO at `-002`)

## What Changed Since -001

This revision addresses every finding in `bridge/gtkb-rollback-receipts-002.md`:

| Finding | Severity | Fix location in this proposal |
|---------|----------|-------------------------------|
| F1 — plain `git revert <merge_commit>` invalid for `--no-ff` topology | High | §1.3 (explicit `-m 1` mainline + parent-order invariant + T1a) |
| F2 — receipt lifecycle inconsistent (merge_commit field unfillable, `git add -A` captures the receipt, revert destroys it) | High | §1.2 (two-commit upgrade flow); §2.2 (write-after-merge schema population); §3.3 (rollback is a protected-path operation that moves receipt active→archived in the rollback commit); T3a, T3b |
| F3 — `git clean -fd` does not touch ignored paths | Medium | §1.4 (no `git clean` anywhere — manifest-driven deletion only); T9 revised |
| F4 — class I contradicted by `git add -A` | Medium | §2.1 (class I eliminated; non-ignored upgrade-created files are class C; ignored upgrade-created paths are class H; matrix now 9 classes A-H + J) |

Open-question answers from `-002` are integrated into the design (not left as open questions):

- **Reflog expiry → §3.1:** object-existence check is primary (`git cat-file -e`); reachability check is secondary (`git merge-base --is-ancestor`); doctor warning on stale active receipts is §3.4.
- **Non-git adopters → §1.1:** `gt project upgrade --apply` and `--rollback` hard-require a usable `.git`. `gt project init`'s git requirement remains a separate decision, deferred.
- **Receipt tracking default → §2.3:** tracked, made safe by the two-commit flow. Gitignore scaffold does NOT ignore `.claude/upgrade-receipts/`.
- **Destructive prompt → §4.3:** TTY interactive confirmation required; explicit `--yes` (or `CI=1` env) bypass for non-interactive use.

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

### 1.1 Preconditions

Both `upgrade --apply` and any `--rollback` invocation require:

1. Target `--dir` resolves to a git working tree:
   - `git rev-parse --show-toplevel` must succeed from that directory.
   - If it fails, CLI exits non-zero with: `"gt project upgrade --apply requires a git working tree. Initialize with 'git init' or run against a cloned repository."`
2. `git` binary is on PATH. Absence produces the same class of diagnostic.

These preconditions are evaluated BEFORE any file scan or manifest parse.
`gt project init`'s own git requirement is a separate product decision and is
deferred.

### 1.2 Upgrade execution flow (two-commit transactional)

```text
gt project upgrade --apply
 ├─ pre-flight
 │   ├─ verify git working tree (§1.1)
 │   ├─ record pre_upgrade_sha = `git rev-parse HEAD`
 │   ├─ record pre_upgrade_branch = `git rev-parse --abbrev-ref HEAD`   ◄ mainline
 │   ├─ capture clean-tree proof = `git status --porcelain --untracked-files=all`
 │   └─ allocate receipt_id = `<utc>-<rand8>`
 │
 ├─ upgrade commit
 │   ├─ create working branch `gt-upgrade-<receipt_id>` from HEAD
 │   ├─ apply upgrade file changes (classes A-G as defined in §2.1)
 │   ├─ for each ignored upgrade-created path (class H): create on disk,
 │   │   record in in-memory manifest (NOT added to git)
 │   ├─ git add -A                                                     ◄ no receipt yet
 │   ├─ git commit -m "gt upgrade <receipt_id>: payload"
 │   ├─ checkout pre_upgrade_branch
 │   ├─ git merge --no-ff gt-upgrade-<receipt_id>                      ◄ parent 1 = mainline, parent 2 = upgrade
 │   └─ record merge_commit = `git rev-parse HEAD`
 │
 ├─ receipt commit
 │   ├─ finalize receipt JSON (schema §2.2) with merge_commit populated
 │   ├─ write `.claude/upgrade-receipts/active/<receipt_id>.json`
 │   ├─ git add .claude/upgrade-receipts/active/<receipt_id>.json
 │   └─ git commit -m "gt upgrade <receipt_id>: receipt"
 │
 └─ cleanup
     ├─ delete working branch `gt-upgrade-<receipt_id>`
     └─ exit 0
```

**On failure mid-upgrade:**

- Pre-flight failure → no branch created, exit non-zero, adopter tree untouched.
- Upgrade-commit failure (before merge) → working branch retained for diagnosis,
  mainline unchanged, exit non-zero with branch name.
- Merge failure → working branch retained, mainline unchanged, exit non-zero.
- Receipt-commit failure (after merge succeeded) → **critical recovery state**.
  The merge_commit exists on mainline but no receipt exists. `upgrade` writes
  a **fallback receipt** to `.claude/upgrade-receipts/active/<receipt_id>.json`
  as untracked file and logs: `"Receipt commit failed; fallback receipt written
  but not tracked. Run 'gt project upgrade --finalize-receipt <receipt_id>' to
  commit it, or rollback manually via 'git revert -m 1 <merge_commit>'."`
  This state is covered by test T17.

### 1.3 Rollback modes

Two modes, chosen by operator at rollback time:

| Mode | CLI surface | Git mechanism | Destructive? | Requires clean tree? |
|------|-------------|---------------|--------------|----------------------|
| **`revert`** (default) | `gt project upgrade --rollback <receipt_id>` | `git revert -m 1 --no-commit <merge_commit>` + manifest-driven class-H cleanup + receipt move (active→archived with status update) + single commit | No | No, but tracked-and-dirty upgrade-touched paths fail loudly (T13) |
| **`reset`** (opt-in) | `gt project upgrade --rollback <receipt_id> --destructive` | `git reset --hard <pre_upgrade_sha>` + manifest-driven class-H cleanup + filesystem receipt move to archived (no commit, because history is rewritten) | Yes | Yes — hard fail if ANY tracked path has unstaged changes (T14) |

**Parent-order invariant (F1 fix):**

- `git merge --no-ff gt-upgrade-<receipt_id>` is always invoked from the
  mainline branch, so in the resulting merge commit, **parent 1 is the
  pre-upgrade mainline tip** and parent 2 is the upgrade-branch tip.
- Therefore `git revert -m 1 <merge_commit>` is always correct because parent 1
  is mainline by construction, not by inspection.
- The receipt records both `pre_upgrade_sha` (the mainline parent's sha) AND
  the merge commit's parent 1. On rollback, we verify
  `git rev-parse <merge_commit>^1 == pre_upgrade_sha` before invoking revert.
  If this invariant fails, rollback aborts with:
  `"Parent-order invariant failed: merge_commit parent 1 (<sha>) does not
  match receipt pre_upgrade_sha (<sha>). Manual intervention required."`
- Test T1a asserts this end-to-end by performing the real `--no-ff` merge
  and running rollback through the public CLI entry point, which is what
  the NO-GO required.

**Safety gates applied in both modes:**

1. **Git object existence.** Rollback runs `git cat-file -e <merge_commit>`
   and `git cat-file -e <pre_upgrade_sha>`. Either missing → fail loudly per §3.1.
2. **Reachability check.** Rollback runs `git merge-base --is-ancestor <merge_commit> HEAD`.
   Non-ancestor → fail loudly: `"Upgrade merge commit no longer reachable from HEAD.
   A branch rewrite or reset may have removed it. Manual recovery required."`
3. **Pre-upgrade clean-tree divergence.** If upgrade captured clean-tree proof
   AND any tracked upgrade-touched path currently has unstaged changes not part
   of merge_commit, rollback refuses with exact diverging paths listed.
4. **Parent-order invariant check** as defined above.

### 1.4 Class-H path cleanup (F3 fix)

Class-H paths (gitignored, upgrade-created — see §2.1) are NEVER cleaned with
`git clean`. The upgrade receipt's `actions[*]` entries with `class == "H"`
carry the exact paths. Rollback deletes them by enumerating the manifest:

```python
# Pseudocode - see §5 for real module
for action in receipt.actions:
    if action.class_ != "H":
        continue
    path = adopter_root / action.path
    if action.action == "create-dir" and path.is_dir():
        shutil.rmtree(path)
    elif action.action == "create-file" and path.is_file():
        path.unlink()
    # No-op if path already gone (idempotent); log warning only
```

Rollback does NOT call `git clean` in either mode. This preserves adopter
sibling files inside upgrade-created ignored directories only if they were not
enumerated in the manifest. Test T9 asserts exactly this (adopter-created
sibling file inside `.gt-upgrade-staging/` survives rollback).

## 2. Restore Coverage by Artifact Class

### 2.1 Class matrix (F4 fix)

For every class of artifact touched by upgrade, this matrix proves whether git
alone suffices or whether receipt-owned payload storage is needed.

| Class | Example paths | Git-tracked? | Git-sufficient for rollback? | Additional receipt payload? |
|-------|---------------|--------------|------------------------------|-----------------------------|
| **A. Tracked overwrite** | `src/groundtruth_kb/...`, `templates/*.toml`, `.github/workflows/*.yml` (after adoption) | Yes | Yes (`git revert -m 1` / `git reset --hard`) | None required; receipt records path + pre_sha_short for audit |
| **B. Tracked deletion** (upgrade removes a tracked file) | Retired hook file | Yes | Yes (git restores deleted file from merge_commit^1) | None required |
| **C. Tracked add** (upgrade adds a new file; `git add -A` captures it) | New rule file, new hook, new non-ignored file under `webapp/` | Becomes tracked at upgrade commit | Yes (`git revert -m 1` removes it; `git reset --hard pre_upgrade_sha` removes it) | None required |
| **D. Settings.json structured merge** | `.claude/settings.json` | Usually yes | Conditionally yes — git restores bytes, but adopter post-upgrade edits may cause `git revert` conflict | Receipt stores `{pre_bytes, post_bytes, json_patch_rfc6902}` as conflict-resolution aid. Not used as primary restore. |
| **E. Gitignore append** | `.gitignore` | Yes | Conditionally yes (conflict possible on post-upgrade edits) | Receipt stores `{pre_lines_count, appended_lines: [str]}` as conflict-resolution aid |
| **F. TOML config merge** | `groundtruth.toml`, `pyproject-sections.toml` | Yes | Conditionally yes (same as D) | Receipt stores `{pre_content, post_content, merge_strategy_label}` as conflict-resolution aid |
| **G. Manifest update** | `groundtruth.toml` `[scaffold] scaffold_version` | Yes | Yes (reverts with F) | Receipt stores `{pre_scaffold_version, post_scaffold_version}` for human audit |
| **H. Ignored-and-created path** | `.gt-upgrade-staging/**` (transient); any other ignored-by-receipt-added-gitignore-or-pre-existing-ignore path | **No (gitignored)** | **No** (git revert ignores it; reset doesn't either) | **Receipt MUST own the manifest.** Each entry records `{path, action: "create-file" / "create-dir", parent_ignore_source: "pre-existing" / "upgrade-added-gitignore-line"}`. Rollback calls path-specific deletion per §1.4. |
| **J. Scaffold receipts** | `.claude/upgrade-receipts/active/<id>.json`, `.claude/upgrade-receipts/archived/<id>.json` | Tracked by default (§2.3) | N/A — receipt is not in merge_commit; rollback moves active→archived in the rollback commit | Receipt lifecycle managed by GT-KB independent of git revert |

**Class I is eliminated.** Under the proposed `git add -A` flow, any
non-ignored upgrade-created file becomes class C. Ignored upgrade-created
paths are class H (receipt-owned deletion metadata). There is no residual
"untracked-but-created" case because the upgrade never intentionally leaves
a non-ignored file outside the commit.

**Conclusion from this matrix:** git is sufficient for classes A, B, C, G.
Classes D, E, F need git + receipt-aided conflict resolution. Class H needs
receipt-owned path manifest because git cannot restore ignored paths. Class J
is outside the merge_commit by construction (§1.2), so revert does not touch it.

### 2.2 Receipt JSON schema (v1)

Receipts are written ONLY after the merge_commit exists, so all schema fields
can be populated truthfully.

```json
{
  "receipt_id": "2026-04-17T20-15-00Z-abcd1234",
  "schema_version": 1,
  "gt_kb_version": "0.7.0",
  "timestamp_utc": "2026-04-17T20:15:00Z",
  "pre_upgrade_sha": "cf29738aaaa",
  "pre_upgrade_branch": "develop",
  "merge_commit": "a1b2c3d4eee",
  "merge_commit_parent_1": "cf29738aaaa",
  "merge_commit_parent_2": "9876fed0ccc",
  "clean_tree_proof": {
    "porcelain_lines": [],
    "captured_at_utc": "2026-04-17T20:14:55Z"
  },
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
      "class": "C",
      "path": "webapp/new-file.html",
      "action": "create",
      "post_sha_short": "fff111"
    },
    {
      "class": "H",
      "path": ".gt-upgrade-staging/",
      "action": "create-dir",
      "parent_ignore_source": "pre-existing"
    }
  ],
  "rollback_mode_supported": ["revert", "reset"],
  "status": "active"
}
```

On rollback, the active receipt is moved to
`.claude/upgrade-receipts/archived/<receipt_id>.json` with `status` updated to
one of: `"rolled-back-revert-<utc-timestamp>"`,
`"rolled-back-reset-<utc-timestamp>"`, or
`"rolled-back-partial-<utc-timestamp>"`. In `revert` mode the move is part of
the rollback commit (§3.3); in `reset` mode the move is a pure filesystem
operation because `git reset --hard` already rewrote history to pre_upgrade_sha.

### 2.3 Receipt storage and tracking default

- **Active:** `.claude/upgrade-receipts/active/<receipt_id>.json`
- **Archived:** `.claude/upgrade-receipts/archived/<receipt_id>.json`
- **Default tracking:** tracked. The gitignore scaffold emits
  `!.claude/upgrade-receipts/` (negation) after the `.claude/` ignore line, so
  receipts survive `.claude/` ignores. Adopters who prefer untracked receipts
  can flip this by editing their `.gitignore`; this is explicitly a supported
  customization and test T18 covers it.
- Receipts are small (<~10 KiB typical; upper bound ~100 KiB for large
  structured-merge diffs). No byte-inline cap is needed because class H
  stores only paths, not file contents.
- Retention: append-only indefinitely. `gt project upgrade --prune-receipts
  --older-than <duration>` moves receipts to an offline location; not in scope
  for v1.

## 3. Object-Retention and Failure Semantics

### 3.1 Git object availability failure modes

| Failure | Diagnosis | Rollback behavior |
|---------|-----------|-------------------|
| Merge commit GC'd / missing | `git cat-file -e <merge_commit>` fails | Fail loudly: `"Upgrade merge commit <sha> no longer exists in git object store. Manual recovery required. See docs/reference/rollback.md#recovery."` |
| pre_upgrade_sha GC'd / missing | Same check | Same diagnostic template |
| Merge commit not reachable from HEAD | `git merge-base --is-ancestor <merge_commit> HEAD` returns non-zero | Fail loudly with branch-rewrite guidance |
| Parent-order invariant fails | `git rev-parse <merge_commit>^1 != pre_upgrade_sha` | Fail loudly with both SHAs named |
| Receipt file deleted | Filesystem check on `.claude/upgrade-receipts/active/<id>.json` | Fail loudly: `"Receipt <id> not found at .claude/upgrade-receipts/active/<id>.json. Rollback impossible. Check archived/ for prior rollback."` |
| Receipt schema_version unknown | Parse check | Fail loudly with supported range |
| Clean-tree proof missing and working tree dirty | Preflight check | Fail loudly: `"Rollback requires clean tree because upgrade did not capture pre-upgrade clean-tree proof. Commit or stash local changes, then retry."` |

**No silent best-effort.** Every failure mode produces an operator-facing
diagnostic that names the missing dependency.

### 3.2 Partial rollback

If rollback fails partway (e.g., `git revert -m 1 --no-commit` succeeds but
class-H filesystem cleanup fails on one path due to adopter-held file lock):

1. The revert IS staged but not yet committed.
2. GT-KB writes a follow-on action log to
   `.claude/upgrade-receipts/active/<receipt_id>.json.partial-rollback` with
   the staged revert SHA, the failing class-H path, and the error.
3. CLI exits non-zero with: `"Partial rollback. Staged revert in working tree;
   class-H cleanup failed on <path>. Run 'gt project upgrade --rollback-finish
   <receipt_id>' to retry cleanup and commit, or 'git reset HEAD' to abort."`
4. Operator can either retry (expected resolution) or abort (emergency escape).

Partial rollback is covered by T19.

### 3.3 Rollback execution flow (revert mode, authoritative)

```text
gt project upgrade --rollback <receipt_id>
 ├─ pre-flight
 │   ├─ verify git working tree (§1.1)
 │   ├─ load receipt from .claude/upgrade-receipts/active/<receipt_id>.json
 │   ├─ verify schema_version == 1 (else fail per §3.1)
 │   ├─ verify git objects exist (§3.1)
 │   ├─ verify merge_commit reachable from HEAD (§3.1)
 │   ├─ verify parent-order invariant (§1.3)
 │   ├─ verify no tracked upgrade-touched path is dirty (§1.3 safety gate 3)
 │   └─ if --destructive: also require tree fully clean (any dirty tracked path)
 │
 ├─ rollback commit (revert mode)
 │   ├─ git revert -m 1 --no-commit <merge_commit>
 │   ├─ for each class-H action in receipt: path-specific delete (§1.4)
 │   ├─ move active/<id>.json → archived/<id>.json
 │   ├─ update archived receipt: status = "rolled-back-revert-<utc>"
 │   ├─ git add -A   (stages revert + receipt move atomically)
 │   └─ git commit -m "gt rollback <receipt_id>"
 │
 └─ exit 0
```

Reset mode is similar but replaces the revert step with `git reset --hard
<pre_upgrade_sha>` and the receipt move is a filesystem-only operation
(because reset rewrote history to before the receipt existed, so there is no
tracked active receipt to remove). Test T14 covers this.

### 3.4 Doctor warnings

`gt project doctor` scans `.claude/upgrade-receipts/active/` and for each
active receipt verifies:

- `merge_commit` and `pre_upgrade_sha` still exist in the git object store.
- `merge_commit` is reachable from `HEAD` (any branch).
- Parent-order invariant holds.

On any failure it emits a WARN diagnostic with the receipt id, the broken
check, and a pointer to `docs/reference/rollback.md#recovery`. This is
advisory and does not block any other doctor action.

## 4. CLI surface

### 4.1 New/changed flags on `gt project upgrade`

- `--rollback <receipt_id>` — invoke rollback in `revert` mode.
- `--destructive` — used only with `--rollback`; switches to `reset` mode.
- `--rollback-finish <receipt_id>` — retry a partial rollback (§3.2).
- `--finalize-receipt <receipt_id>` — commit a fallback receipt that was
  written but not tracked due to receipt-commit failure (§1.2 recovery state).
- `--list-receipts` — print active + archived receipts with status.

### 4.2 Flags retained from current CLI

- `--dry-run` / `--apply` / `--force` / `--dir` (§F5 of NO-GO noted these are
  current surface; this proposal extends them but does not remove them).

### 4.3 Destructive mode interactive gate

When `--destructive` is used:

- If `sys.stdin.isatty()` is true AND env `CI` is unset AND `--yes` is absent:
  prompt `"This will perform 'git reset --hard' and discard all commits after
  <merge_commit>. Type 'YES' to proceed: "` and require exact `"YES"`.
- If `sys.stdin.isatty()` is false OR env `CI=1` is set: require explicit
  `--yes` flag or exit with:
  `"--destructive in non-interactive mode requires --yes to bypass TTY
  confirmation."`

Test T20 covers all three branches (TTY accept, TTY reject, non-TTY without
--yes).

## 5. Proposed Source Files

New:
- `src/groundtruth_kb/project/rollback.py`
  - `Receipt` dataclass (schema v1 deserialization + validation)
  - `RollbackEngine` class
  - `rollback(receipt_id: str, *, mode: Literal["revert", "reset"] = "revert", yes: bool = False, dir: Path | None = None) -> int`
  - `finalize_partial_rollback(receipt_id: str, ...) -> int`
  - `finalize_receipt(receipt_id: str, ...) -> int`
  - `list_receipts(...) -> list[Receipt]`
  - Git operation wrappers with explicit reflog capture
- `tests/test_rollback.py` — T1 through T20 (§6)

Modified:
- `src/groundtruth_kb/project/upgrade.py`
  - Wrap execution in two-commit transactional flow per §1.2
  - Remove all `.bak` backup writes (the NO-GO observed these still exist at
    `upgrade.py:355-369, 423, 448, 453`); see §7 exit criterion 8
  - Capture pre_upgrade_sha, pre_upgrade_branch, clean_tree_proof, merge_commit
  - Write active receipt in receipt commit AFTER merge
  - Fallback receipt path for recovery state (§1.2)
- `src/groundtruth_kb/cli.py` — add flags per §4.1
- `src/groundtruth_kb/project/__init__.py` — export `Receipt`, `RollbackEngine`,
  `rollback`, `finalize_partial_rollback`, `finalize_receipt`, `list_receipts`
- `docs/reference/rollback.md` (NEW) — operator-facing docs: modes, failure
  modes, recovery runbook, receipt schema, worked example including the
  partial-rollback recovery and fallback-receipt recovery paths
- `CHANGELOG.md` — entry under the next unreleased GT-KB version
- Gitignore scaffold template — emit `!.claude/upgrade-receipts/` negation
  after any `.claude/` ignore (§2.3)

## 6. Test Catalog

Minimum 20 tests, all in `tests/test_rollback.py` (new module). Tests T1-T16
from `-001` are retained where still applicable; T1a, T3a, T3b, T9, T17-T20
are added or revised in this revision.

| # | Test | Covers | Asserts |
|---|------|--------|---------|
| T1 | `test_rollback_tracked_overwrite` | A | File content after rollback == pre-upgrade content |
| **T1a** | `test_rollback_through_public_cli_on_real_no_ff_merge` (NEW, F1 required action) | F1 | Creates actual `--no-ff` merge commit using real upgrade flow; invokes `gt project upgrade --rollback <id>` via CLI; asserts rollback succeeds and tree matches pre-upgrade state. Proves `-m 1` mainline is correct by construction. |
| T2 | `test_rollback_tracked_deletion_restored` | B | Deleted file restored to pre-upgrade bytes |
| T3 | `test_rollback_tracked_add_removed` | C | Added file removed from working tree and git index |
| **T3a** | `test_rollback_receipt_not_in_merge_commit` (NEW, F2 required action) | F2, J | After upgrade, verify `git log --name-only <merge_commit> -1` does NOT include any path under `.claude/upgrade-receipts/` |
| **T3b** | `test_rollback_preserves_archived_receipt` (NEW, F2 required action) | F2, J | After rollback, `.claude/upgrade-receipts/archived/<id>.json` exists with `status` starting with `rolled-back-`; the rollback commit includes this file |
| T4 | `test_rollback_settings_json_no_post_upgrade_edit` | D | `.claude/settings.json` matches pre-upgrade exactly |
| T5 | `test_rollback_settings_json_with_post_upgrade_edit_fails_loudly` | D | Revert conflict reported; operator-facing diagnostic includes conflicting path; no silent resolution |
| T6 | `test_rollback_gitignore_append_removes_lines` | E | Exact appended lines removed; unrelated adopter `.gitignore` edits preserved |
| T7 | `test_rollback_toml_merge_preserves_unrelated_keys` | F | Adopter-added keys in `groundtruth.toml` post-upgrade preserved; upgrade-added keys removed |
| T8 | `test_rollback_manifest_version_reverted` | G | `scaffold_version` returned to pre-upgrade value |
| **T9** | `test_rollback_class_h_preserves_adopter_siblings` (REVISED, F3 required action) | H, F3 | Upgrade creates `.gt-upgrade-staging/`; adopter drops `.gt-upgrade-staging/mynote.txt` post-upgrade; rollback removes the manifest-listed directory contents but asserts `mynote.txt` is preserved IF outside the manifest scope (test covers both directory-removal and file-preservation semantics explicitly). No `git clean` invocation anywhere in rollback code path (verified by source scan). |
| T10 | `test_rollback_cross_cut_adopter_edits_preserved` | cross-cutting | Operator edits `webapp/index.html` between upgrade and rollback; rollback leaves `webapp/index.html` untouched; revert succeeds on upgrade-touched paths only |
| T11 | `test_rollback_large_file_overwrite` | A | 10 MiB tracked file overwrite restores without inline-payload concerns |
| T12 | `test_rollback_dirty_tree_refusal_revert_mode` | safety | Revert fails when tracked upgrade-touched path has uncommitted changes; no partial revert |
| T13 | `test_rollback_dirty_tree_refusal_reset_mode` | safety | Reset fails when ANY tracked path has uncommitted changes; no destructive action |
| T14 | `test_rollback_reset_mode_rewrites_history` | reset mode | `git reset --hard` branch HEAD equals pre_upgrade_sha; active receipt moved to archived on disk (no commit) |
| T15 | `test_rollback_merge_commit_missing_fails_loudly` | failure semantics | Simulated GC of merge_commit produces the exact diagnostic from §3.1 |
| T16 | `test_rollback_receipt_file_missing_fails_loudly` | failure semantics | Deleted receipt produces the exact diagnostic from §3.1 |
| **T17** | `test_upgrade_receipt_commit_failure_writes_fallback` (NEW) | §1.2 recovery | Inject failure in receipt-commit step after merge succeeded; assert fallback receipt file exists, CLI exit is non-zero, diagnostic names `--finalize-receipt`; `--finalize-receipt` then commits the receipt cleanly |
| **T18** | `test_receipt_tracking_opt_out` (NEW) | §2.3 | Adopter removes `!.claude/upgrade-receipts/` from `.gitignore`; upgrade still succeeds but receipt commit is a no-op (no tracked change); rollback falls back to filesystem-only receipt move and still succeeds |
| **T19** | `test_partial_rollback_recovers_via_finish` (NEW, §3.2) | partial rollback | Inject class-H deletion failure; assert `.partial-rollback` sidecar exists, CLI exit non-zero, `--rollback-finish` then completes and commits cleanly |
| **T20** | `test_destructive_requires_confirmation` (NEW) | §4.3 | Parametrized: (a) TTY + "YES" → proceeds; (b) TTY + "no" → aborts non-destructively; (c) non-TTY without `--yes` → exits with diagnostic; (d) non-TTY with `--yes` → proceeds |

Plus existing `tests/test_upgrade.py` extensions (from `-001`):
- `test_upgrade_writes_receipt_on_apply`
- `test_upgrade_receipt_schema_v1_roundtrip`
- `test_upgrade_records_clean_tree_proof`
- `test_upgrade_parent_order_invariant` (verifies merge_commit^1 == pre_upgrade_sha)

## 7. Post-Implementation Verification Criteria

Post-impl report at `gtkb-rollback-receipts-00N.md` must demonstrate:

1. T1-T20 (plus T1a, T3a, T3b) all pass; no skips, no xfails.
2. Full GT-KB test suite passes on the implementation branch.
3. `mypy --strict src/groundtruth_kb/project/rollback.py` returns 0 errors.
4. `mypy --strict src/groundtruth_kb/project/upgrade.py` returns 0 errors
   (regression guard — upgrade.py is being substantially rewritten).
5. `ruff check` + `ruff format --check` pass on new and modified files.
6. Receipt JSON schema v1 documented in `docs/reference/rollback.md`; schema
   example is machine-validated in a unit test.
7. At least one `--dry-run` rollback dogfood run against Agent Red path, with
   full output captured in the post-impl report (READ-ONLY, no Agent Red
   writes; verified by pre/post `git status` snapshots of Agent Red tree).
8. CHANGELOG entry added to GT-KB `CHANGELOG.md`.
9. No new `.bak` file creation paths remain in `upgrade.py`. Search
   `rg -n "\.bak" src/groundtruth_kb/project/upgrade.py` must return 0 hits.
10. Source scan for `git clean` in rollback code path: `rg -n "git clean"
    src/groundtruth_kb/project/rollback.py` must return 0 hits (F3 invariant).
11. Commit-local test delta reported (not range delta, per S299 hygiene note).

## 8. Non-Scope

- Rollback across version ranges (e.g., roll back three upgrades). v1 supports
  single-upgrade rollback only; chained rollback deferred.
- Cross-branch rollback (rolling back an upgrade that was merged on a
  different branch). v1 requires operator to checkout the branch where the
  upgrade was applied.
- Retention/pruning automation (`--prune-receipts`). v1 leaves receipts
  append-only.
- Modification of Agent Red files, requirements pins, or `groundtruth.db`
  tracking — all deferred to follow-on Agent Red adoption bridge.
- Tier 1 A1/B1/C1 and Tier 2 work from `post-phase-a-prioritization-004.md`.
- `gt project init`'s own git requirement (deferred per §1.1).

## 9. Sequencing and Dependencies

- **Blocks** no other sub-bridge directly, but parent's Phase 5/6/8 sub-bridges
  (preflight, workflow surface, dogfood) rely on receipts being present once
  implemented.
- **Depends on** nothing — can proceed in parallel with
  `gtkb-artifact-ownership-matrix-001`.
- **Touches live registry:** no. Registry extension is the sibling
  `gtkb-artifact-ownership-matrix-001` sub-bridge's scope.
- Rollback branch of GT-KB is `feature/rollback-receipts`, branched off
  `main` at implementation time. The `cf29738` reference in the header is the
  proposal baseline, not a forced branch point.

## 10. Prior Deliberations

- `bridge/gtkb-rollback-receipts-002.md` (THIS NO-GO; all four findings
  addressed above)
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
5. Rewire `upgrade.py` to use two-commit transactional flow per §1.2.
6. Remove all `.bak` backup writes from `upgrade.py` (exit criterion 9).
7. Add CLI flags per §4.1.
8. Add T1-T20 (plus T1a, T3a, T3b) tests per §6.
9. Run dogfood dry-run against Agent Red path (READ-ONLY) and capture output.
10. File post-impl report at `gtkb-rollback-receipts-00N.md`.
11. Codex VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
