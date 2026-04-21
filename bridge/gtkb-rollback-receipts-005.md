# Sub-Bridge: GT-KB Upgrade Rollback Receipts (REVISED-2)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, capped automated spawn S299-continuation)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Parent structural GO:** `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md`
**Scope parent (grandparent):** `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md` (Condition 1)
**Target GT-KB HEAD:** `bfedd40` on `feature/ownership-matrix` (Codex-observed in -004; rollback implementation will branch off `main` at implementation time)
**Agent Red HEAD:** `aa6a5fe5`
**Supersedes:** `-003` (NO-GO at `-004`)
**Prior revisions:** `-001` (NO-GO at `-002`) → `-003` (NO-GO at `-004`)

## What Changed Since -003

This revision addresses every finding in `bridge/gtkb-rollback-receipts-004.md`:

| Finding | Severity | Fix location in this proposal |
|---------|----------|-------------------------------|
| F1 — class-H cleanup `rmtree` contradicts sibling-preservation contract | High | §1.4 (child-manifest semantics; directories removed only by empty-dir cleanup; transient-private variant with loud-fail precondition); §2.1 (class-H sub-typing); §2.2 (receipt schema v1 action variants); T9 split into T9a + T9b + T9c |
| F2 — receipt tracking opt-out conflicts with unconditional receipt commit | High | §1.2 (receipt-mode resolution BEFORE staging); §2.3 (receipt-mode definition); §2.2 (`receipt_mode` schema field); §3.3 (rollback dispatches on receipt_mode); T18 replaced with T18a + T18b + T18c |
| F3 — reset-mode receipt archival underspecified | Medium | §3.3 (reset-mode writes archived receipt from in-memory object AFTER reset, before post-reset filesystem commits); §2.3 (tracked/untracked state of reset-mode archived receipts defined); T14 replaced with T14a + T14b + T14c |

What was accepted in -003 and retained unchanged here:

- The `git revert -m 1 --no-commit <merge_commit>` default (F1 of -002, §1.3).
- Writing the receipt AFTER the merge commit exists (F2 of -002, §1.2).
- Class I elimination under `git add -A` (F4 of -002, §2.1).
- No `git clean` in rollback (F3 of -002; carried forward and strengthened by §1.4).
- Parent-order invariant + T1a (§1.3).

The -002 findings (F1-F4) remain closed. This revision only addresses the three new findings introduced in -004.

## Why This Sub-Bridge Exists

Unchanged from -003: Codex structural GO at parent `-004` F2 required git-based
rollback be treated as a candidate design, with per-class restore coverage
proven or disproven and receipt-owned payload storage for classes git cannot
restore. This sub-bridge presents the design, enumerates classes, and specifies
receipt-owned storage where git cannot restore.

## Agent Red Dogfood Boundary (explicit)

Unchanged from -003. Zero writes to the Agent Red checkout from any code,
test, or script in this sub-bridge. Dry-run rollback dogfood only. Classification
report obligation assigned to `gtkb-artifact-ownership-matrix-001`.

## 1. Rollback Design

### 1.1 Preconditions

Unchanged from -003 §1.1. Both `upgrade --apply` and `--rollback` require a git
working tree and `git` on PATH. Preconditions are evaluated before any file
scan or manifest parse.

### 1.2 Upgrade execution flow (two-commit transactional, with receipt-mode resolution)

The flow from -003 is preserved, with two changes:

1. **Receipt-mode resolution step added BEFORE receipt write.** Determines
   whether the receipt commit is part of the flow (`tracked` mode) or skipped
   entirely (`filesystem` mode). This is the F2 fix.
2. **Class-H children are enumerated during upgrade commit**, not rolled up
   into a single directory action (F1 fix — see §2.1).

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
 │   ├─ for each ignored upgrade-created path (class H):
 │   │   ├─ if it is a file: create it, record `action="create-file"` with
 │   │   │   the exact path
 │   │   ├─ if it is a directory created as an intentional container:
 │   │   │   ├─ default sub-type: record `action="create-dir"`; do NOT record
 │   │   │   │   any implicit "delete this whole subtree" semantics
 │   │   │   └─ if the directory is declared private-transient by the upgrade
 │   │   │       action producer (rare, opt-in, §2.1): record
 │   │   │       `action="create-dir-private-transient"` AND enumerate every
 │   │   │       expected-child path in `private_transient_children`
 │   │   └─ none of the class-H paths are added to git
 │   ├─ git add -A                                                     ◄ no receipt yet
 │   ├─ git commit -m "gt upgrade <receipt_id>: payload"
 │   ├─ checkout pre_upgrade_branch
 │   ├─ git merge --no-ff gt-upgrade-<receipt_id>                      ◄ parent 1 = mainline, parent 2 = upgrade
 │   └─ record merge_commit = `git rev-parse HEAD`
 │
 ├─ receipt-mode resolution (F2 fix)
 │   ├─ compute receipt_path = `.claude/upgrade-receipts/active/<receipt_id>.json`
 │   ├─ run `git check-ignore --verbose --no-index -- <receipt_path>`
 │   │   ├─ exit 0 (path IS ignored): receipt_mode = "filesystem"
 │   │   ├─ exit 1 (path is NOT ignored): receipt_mode = "tracked"
 │   │   └─ exit other: hard fail (diagnostic: "git check-ignore failed
 │   │      unexpectedly; cannot determine receipt mode safely")
 │   └─ record receipt_mode in the receipt object (§2.2)
 │
 ├─ receipt write (dispatch on receipt_mode)
 │   ├─ if receipt_mode == "tracked":
 │   │   ├─ finalize receipt JSON (schema §2.2) with merge_commit populated
 │   │   ├─ write receipt_path
 │   │   ├─ git add <receipt_path>       ◄ plain add; path confirmed non-ignored
 │   │   └─ git commit -m "gt upgrade <receipt_id>: receipt"
 │   │
 │   └─ if receipt_mode == "filesystem":
 │       ├─ finalize receipt JSON with merge_commit populated
 │       ├─ write receipt_path           ◄ durable on disk; intentionally untracked
 │       ├─ do NOT run `git add`
 │       ├─ do NOT create a receipt commit
 │       └─ exit 0 (upgrade complete; no receipt commit needed)
 │
 └─ cleanup
     ├─ delete working branch `gt-upgrade-<receipt_id>`
     └─ exit 0
```

**On failure mid-upgrade:**

- Pre-flight failure → no branch created, exit non-zero, adopter tree untouched.
- Upgrade-commit failure (before merge) → working branch retained, mainline
  unchanged, exit non-zero with branch name.
- Merge failure → working branch retained, mainline unchanged, exit non-zero.
- Receipt-mode resolution failure → hard fail. No fallback. The diagnostic
  explicitly names `git check-ignore` as the failing dependency.
- **Receipt-commit failure in tracked mode** (after merge succeeded) →
  **critical recovery state**, as in -003. The merge_commit exists on mainline
  but no receipt commit exists. `upgrade` writes a fallback receipt file to
  `.claude/upgrade-receipts/active/<receipt_id>.json` as untracked and logs:
  `"Receipt commit failed in tracked mode; fallback receipt written but not
  tracked. Run 'gt project upgrade --finalize-receipt <receipt_id>' to commit
  it, or rollback manually via 'git revert -m 1 <merge_commit>'."`
  Covered by T17.
- **Receipt write failure in filesystem mode** (after merge succeeded) → also a
  critical recovery state, but with a distinct diagnostic:
  `"Receipt write failed in filesystem mode; manifest not persisted. Manual
  recovery required — no way to retry receipt capture after merge_commit
  exists. Consider rolling back via 'git revert -m 1 <merge_commit>' without
  class-H cleanup. See docs/reference/rollback.md#filesystem-write-recovery."`
  Covered by T17a (new).

### 1.3 Rollback modes

Unchanged from -003 except for receipt handling (F2/F3 fixes below).

| Mode | CLI surface | Git mechanism | Destructive? | Requires clean tree? |
|------|-------------|---------------|--------------|----------------------|
| **`revert`** (default) | `gt project upgrade --rollback <receipt_id>` | `git revert -m 1 --no-commit <merge_commit>` + manifest-driven class-H cleanup (§1.4) + receipt dispatch (§3.3) + single commit | No | No, but tracked-and-dirty upgrade-touched paths fail loudly (T13) |
| **`reset`** (opt-in) | `gt project upgrade --rollback <receipt_id> --destructive` | Load receipt into memory first → `git reset --hard <pre_upgrade_sha>` → manifest-driven class-H cleanup (§1.4) → write archived receipt from in-memory object (§3.3, F3 fix) → no commit (history rewritten) | Yes | Yes — hard fail if ANY tracked path has unstaged changes (T13) |

**Parent-order invariant** and all safety gates from -003 §1.3 are unchanged.

### 1.4 Class-H path cleanup (F1 fix)

Class-H paths are NEVER cleaned with `git clean`. The rollback enumerates the
manifest and acts on each entry by `action` type:

```python
# Pseudocode — see §5 for real module
# Phase 1: file deletions (depth-ordered: deepest paths first)
for action in sorted_by_depth_desc(receipt.actions, class_="H"):
    path = adopter_root / action.path
    if action.action == "create-file":
        if path.is_file():
            path.unlink()
        else:
            log_warning(f"class-H file already gone: {action.path}")

# Phase 2: private-transient directory deletions (loud-fail on unmanifested siblings)
for action in receipt.actions_by_class("H", action_type="create-dir-private-transient"):
    path = adopter_root / action.path
    if not path.is_dir():
        log_warning(f"class-H private-transient dir already gone: {action.path}")
        continue
    expected_children = set(action.private_transient_children)
    actual_children = {p.name for p in path.iterdir()}
    unmanifested = actual_children - expected_children
    if unmanifested:
        raise RollbackError(
            f"class-H private-transient directory {action.path!r} has "
            f"unmanifested children: {sorted(unmanifested)}. "
            f"Refusing to delete. Inspect the directory, remove adopter content "
            f"manually, then retry with --rollback-finish."
        )
    shutil.rmtree(path)

# Phase 3: default directory deletions (empty-dir cleanup only)
for action in sorted_by_depth_desc(receipt.actions_by_class("H", action_type="create-dir")):
    path = adopter_root / action.path
    if not path.is_dir():
        log_warning(f"class-H dir already gone: {action.path}")
        continue
    try:
        path.rmdir()  # fails if not empty; that is the intended behavior
    except OSError as e:
        if e.errno == errno.ENOTEMPTY:
            log_info(
                f"class-H dir {action.path!r} retained: adopter-created "
                f"children remain outside manifest. Sibling preservation "
                f"contract honored."
            )
            continue
        raise
```

**Properties of this algorithm:**

1. **Files listed in the manifest are deleted.** No lost upgrade-created files.
2. **Files NOT listed in the manifest are never touched.** Adopter-created
   siblings inside a class-H directory survive, satisfying T9a.
3. **Default directories are removed only if empty after manifest deletions.**
   If the adopter has left any file in the directory, the directory stays,
   satisfying T9a/T9b.
4. **Private-transient directories** (opt-in, producer-declared) are
   `shutil.rmtree`'d ONLY after a pre-deletion enumeration proves no
   unmanifested child exists. If any unmanifested child is found, rollback
   raises and prompts the operator to resolve manually. This replaces the
   -003 unconditional `shutil.rmtree` path with a loud-fail guard (T9c).
5. **Depth-descending ordering** ensures child files are removed before empty
   parents are reaped.
6. **No `git clean` invocation anywhere.** Verified by source scan (exit
   criterion §7.10).

## 2. Restore Coverage by Artifact Class

### 2.1 Class matrix (F1 sub-typing update)

| Class | Example paths | Git-tracked? | Git-sufficient for rollback? | Additional receipt payload? |
|-------|---------------|--------------|------------------------------|-----------------------------|
| **A. Tracked overwrite** | `src/groundtruth_kb/...`, `templates/*.toml`, `.github/workflows/*.yml` | Yes | Yes (revert / reset) | Audit only |
| **B. Tracked deletion** | Retired hook file | Yes | Yes | None |
| **C. Tracked add** | New non-ignored file (captured by `git add -A`) | Becomes tracked at upgrade commit | Yes | None |
| **D. Settings.json merge** | `.claude/settings.json` | Usually yes | Conditionally (conflict on post-upgrade edits) | `{pre_bytes, post_bytes, json_patch_rfc6902}` conflict aid |
| **E. Gitignore append** | `.gitignore` | Yes | Conditionally (conflict possible) | `{pre_lines_count, appended_lines}` conflict aid |
| **F. TOML config merge** | `groundtruth.toml`, `pyproject-sections.toml` | Yes | Conditionally | `{pre_content, post_content, merge_strategy_label}` conflict aid |
| **G. Manifest update** | `scaffold_version` | Yes | Yes (reverts with F) | `{pre_scaffold_version, post_scaffold_version}` audit |
| **H. Ignored-and-created path** — **sub-typed (F1 fix)** | See below | No (gitignored) | No | **Receipt MUST own per-child manifest.** See sub-types. |
| **J. Scaffold receipts** | `.claude/upgrade-receipts/active/<id>.json`, `.claude/upgrade-receipts/archived/<id>.json` | Depends on `receipt_mode` (§2.3) | N/A — receipt is never in merge_commit; rollback handles via §3.3 | Receipt lifecycle managed by GT-KB independent of git revert |

**Class H sub-types (F1 fix):**

| Action | Semantics | Rollback behavior |
|--------|-----------|-------------------|
| `create-file` | A single ignored file the upgrade wrote to disk | Delete exactly this path; no-op if already gone |
| `create-dir` | An ignored directory the upgrade created as a container for later artifacts | `rmdir` only if empty at rollback time; leave in place with log line otherwise. Preserves adopter-created siblings. |
| `create-dir-private-transient` | An ignored directory the upgrade asserts is GT-KB-private (not expected to host adopter content) | Enumerate children; if any child is NOT in `private_transient_children`, raise `RollbackError` and prompt for manual resolution. Otherwise `shutil.rmtree`. |

**Producer rule:** The upgrade code is the sole producer of class-H action
entries. An upgrade step may emit `create-dir-private-transient` only when
the directory is documented as GT-KB-internal (e.g., a scratch area that no
adopter workflow should write to). The default is `create-dir`. If there is
any doubt, use `create-dir`.

**Class I remains eliminated** (unchanged from -003).

**Git sufficiency conclusion unchanged:** A, B, C, G → git sufficient; D, E, F
→ git + receipt-aided conflict resolution; H → per-child receipt-owned
deletion metadata; J → outside merge_commit by construction.

### 2.2 Receipt JSON schema (v1, with F1/F2 fields added)

```json
{
  "receipt_id": "2026-04-17T20-15-00Z-abcd1234",
  "schema_version": 1,
  "gt_kb_version": "0.7.0",
  "timestamp_utc": "2026-04-17T20:15:00Z",
  "receipt_mode": "tracked",
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
    },
    {
      "class": "H",
      "path": ".gt-upgrade-staging/scratch.log",
      "action": "create-file",
      "parent_ignore_source": "pre-existing"
    },
    {
      "class": "H",
      "path": ".gt-internal-cache/",
      "action": "create-dir-private-transient",
      "parent_ignore_source": "upgrade-added-gitignore-line",
      "private_transient_children": ["index.db", "manifest.json"]
    }
  ],
  "rollback_mode_supported": ["revert", "reset"],
  "status": "active"
}
```

**Schema changes from -003:**

- `receipt_mode` (string enum: `"tracked"` | `"filesystem"`) is a new required
  field, populated during the receipt-mode resolution step in §1.2.
- Class-H entries now use the sub-typed `action` field (`create-file`,
  `create-dir`, or `create-dir-private-transient`). The -003 pseudocode treated
  `create-dir` with unconditional `rmtree`; v1 schema rejects that semantics.
- `create-dir-private-transient` entries require a `private_transient_children`
  array. Validation fails if this field is missing for that action type, or
  present for any other action type.

On rollback, the active receipt is moved (or rewritten) to archived with
`status` updated to one of: `"rolled-back-revert-<utc>"`,
`"rolled-back-reset-<utc>"`, `"rolled-back-partial-<utc>"`. Archival mechanism
depends on rollback mode and receipt_mode — see §3.3.

### 2.3 Receipt storage, tracking default, and mode dispatch

- **Active:** `.claude/upgrade-receipts/active/<receipt_id>.json`
- **Archived:** `.claude/upgrade-receipts/archived/<receipt_id>.json`
- **Default gitignore scaffold:** emits `!.claude/upgrade-receipts/` negation
  after any `.claude/` ignore line. With the default scaffold, `receipt_mode`
  resolves to `"tracked"`.
- **Opt-out path:** an adopter who edits `.gitignore` to remove the negation
  (or to add an explicit ignore for `.claude/upgrade-receipts/`) causes
  `git check-ignore` to report the path as ignored. `receipt_mode` resolves to
  `"filesystem"`. The upgrade then:
  1. Writes the active receipt file to disk intentionally.
  2. Does NOT run `git add` on it (plain `git add` of an ignored path is a
     no-op and would produce a confusing UX; force-add would override the
     opt-out, which is exactly the opposite of what the adopter requested).
  3. Does NOT create a receipt commit.
  4. Exits 0. The upgrade itself is complete.
- **Rollback reads `receipt_mode` and dispatches:**
  - Tracked + revert: move via git (active → archived in the rollback commit).
  - Tracked + reset: archived receipt is rewritten from in-memory object
    AFTER reset (F3 fix, §3.3).
  - Filesystem + revert: filesystem `active/` → `archived/` move, then
    rollback commit handles tracked-path revert (the archived receipt itself
    remains untracked, consistent with the adopter's opt-out).
  - Filesystem + reset: archived receipt is rewritten from in-memory object
    AFTER reset; remains untracked.
- **Tracked/untracked state of archived receipts post-rollback:**
  - Revert-mode + tracked receipts: archived file is tracked (committed as
    part of the rollback commit).
  - Revert-mode + filesystem receipts: archived file is untracked.
  - Reset-mode + either: archived file is untracked by construction (reset
    does not produce a commit; history is rewritten to pre_upgrade_sha, and
    any post-reset file writes are a separate filesystem state).
- Retention unchanged.

## 3. Object-Retention and Failure Semantics

### 3.1 Git object availability failure modes

Unchanged from -003 §3.1 except one additional row:

| Failure | Diagnosis | Rollback behavior |
|---------|-----------|-------------------|
| (existing rows unchanged) | | |
| **`receipt_mode == "filesystem"` but active receipt file missing** | Filesystem check on `.claude/upgrade-receipts/active/<id>.json` | Same loud diagnostic as the existing "Receipt file deleted" row; adds: `"Receipt was written in filesystem mode (adopter opt-out); no tracked copy exists. Manual recovery required."` |

### 3.2 Partial rollback

Unchanged from -003 §3.2, with one clarification: the `.partial-rollback`
sidecar is always an untracked filesystem artifact regardless of receipt_mode.

### 3.3 Rollback execution flow (authoritative, both modes)

**Revert mode:**

```text
gt project upgrade --rollback <receipt_id>
 ├─ pre-flight
 │   ├─ verify git working tree (§1.1)
 │   ├─ locate active receipt:
 │   │   ├─ .claude/upgrade-receipts/active/<id>.json on disk
 │   │   └─ if missing → fail per §3.1
 │   ├─ parse receipt JSON; validate schema_version == 1
 │   ├─ read receipt_mode ∈ {"tracked", "filesystem"}
 │   ├─ verify git objects exist (§3.1)
 │   ├─ verify merge_commit reachable from HEAD (§3.1)
 │   ├─ verify parent-order invariant (§1.3)
 │   └─ verify no tracked upgrade-touched path is dirty (§1.3 safety gate 3)
 │
 ├─ rollback commit (revert mode)
 │   ├─ git revert -m 1 --no-commit <merge_commit>
 │   ├─ class-H manifest-driven cleanup (§1.4)
 │   ├─ receipt archival dispatch on receipt_mode:
 │   │   ├─ if receipt_mode == "tracked":
 │   │   │   ├─ read active receipt, update status to "rolled-back-revert-<utc>"
 │   │   │   ├─ write archived/<id>.json with updated content
 │   │   │   ├─ unlink active/<id>.json (git sees this as a rename when staged)
 │   │   │   └─ (the subsequent `git add -A` + commit captures both moves)
 │   │   │
 │   │   └─ if receipt_mode == "filesystem":
 │   │       ├─ read active receipt, update status to "rolled-back-revert-<utc>"
 │   │       ├─ write archived/<id>.json (untracked — stays ignored)
 │   │       ├─ unlink active/<id>.json
 │   │       └─ (archived receipt is NOT staged; rollback commit contains
 │   │          only the revert + class-H manifest effects on tracked paths)
 │   ├─ git add -A   (stages revert; also stages the tracked-mode receipt move)
 │   └─ git commit -m "gt rollback <receipt_id>"
 │
 └─ exit 0
```

**Reset mode (F3 fix — archived receipt rewritten from memory AFTER reset):**

```text
gt project upgrade --rollback <receipt_id> --destructive
 ├─ pre-flight (same as revert mode, plus --yes / TTY gate per §4.3)
 │
 ├─ load-into-memory step (F3 fix)
 │   ├─ parse active receipt file into in-memory Receipt object
 │   ├─ compute archived_receipt_content = Receipt(
 │   │     ...active_receipt fields...,
 │   │     status = "rolled-back-reset-<utc>"
 │   │   )
 │   └─ serialize to bytes; hold in memory
 │
 ├─ reset step
 │   └─ git reset --hard <pre_upgrade_sha>
 │      (this rewrites HEAD; any tracked active receipt is removed from
 │       working tree; filesystem-mode active receipt file may survive on
 │       disk because reset does not touch ignored files — but we do not
 │       rely on that. The authoritative source for archived content is
 │       the in-memory Receipt loaded before reset.)
 │
 ├─ post-reset filesystem operations
 │   ├─ class-H manifest-driven cleanup (§1.4) — enumerates from in-memory
 │   │   Receipt; unaffected by reset because class-H paths are ignored
 │   ├─ mkdir -p .claude/upgrade-receipts/archived/   (may not exist at
 │   │   pre_upgrade_sha; directory creation is idempotent)
 │   ├─ write .claude/upgrade-receipts/archived/<id>.json from
 │   │   archived_receipt_content bytes held in memory
 │   ├─ if receipt_mode == "filesystem" AND a residual active/<id>.json
 │   │   file exists on disk (it may, because reset does not remove ignored
 │   │   files): unlink it. Idempotent: no-op if already gone.
 │   ├─ if receipt_mode == "tracked": the active file is already gone
 │   │   (reset removed it from the working tree). No unlink needed.
 │   └─ no `git add`, no `git commit` — history was rewritten by reset
 │
 └─ exit 0
```

**Properties of the F3-fixed reset-mode flow:**

1. The archived receipt is **sourced from the in-memory Receipt object**, not
   from a filesystem move of the active file. This works uniformly for both
   tracked and filesystem receipt modes, and survives `reset --hard` removing
   the active file.
2. `mkdir -p` on the archived directory handles the case where
   `pre_upgrade_sha` pre-dates `.claude/upgrade-receipts/` entirely.
3. The archived receipt file is **always untracked** post-reset, because reset
   does not create commits and the working tree at pre_upgrade_sha does not
   contain the archived file. The adopter can choose to `git add` it manually
   if they want a tracked record, but GT-KB does not do that automatically
   (doing so would write outside the reset contract).
4. If the pre_upgrade_sha gitignore did NOT contain the `!.claude/upgrade-receipts/`
   negation (i.e., reset removed the negation as well), the archived receipt
   is still written to disk but is now subject to the pre-reset gitignore
   rules. It remains on disk regardless — `.gitignore` does not delete files,
   only affects staging. This is safe and documented in T14c.
5. Class-H cleanup runs AFTER reset because class-H paths are ignored by git
   and are unaffected by `reset --hard`.

### 3.4 Doctor warnings

Unchanged from -003 §3.4, with one addition: doctor reports `receipt_mode` in
its per-receipt output so operators can see at a glance which receipts are
tracked vs filesystem.

## 4. CLI surface

Unchanged from -003 §4.

## 5. Proposed Source Files

Unchanged from -003 §5, with the following additions to `rollback.py`:

- `Receipt.receipt_mode: Literal["tracked", "filesystem"]` field + validation.
- `ClassHAction` discriminated union: `CreateFile`, `CreateDir`,
  `CreateDirPrivateTransient`.
- `RollbackEngine._cleanup_class_h(receipt: Receipt) -> None` implementing
  the three-phase algorithm from §1.4.
- `RollbackEngine._archive_receipt_revert(receipt, status: str) -> None` and
  `_archive_receipt_reset(receipt, status: str) -> None` implementing the
  dispatch from §3.3.

Also in `upgrade.py`:

- `_resolve_receipt_mode(receipt_path: Path, adopter_root: Path) -> Literal["tracked", "filesystem"]`
  wrapping `git check-ignore --verbose --no-index -- <path>`.
- Upgrade-step producers emit `create-dir-private-transient` only when the
  producer explicitly opts in; default is `create-dir`.

## 6. Test Catalog

Tests T1-T8, T10-T13, T15, T16, T17, T19, T20 from -003 are retained unchanged
(the F1/F2/F3 fixes do not regress them). The following tests are split or
replaced:

| # | Test | Covers | Asserts |
|---|------|--------|---------|
| T1, T1a, T2, T3, T3a, T3b | (unchanged from -003) | A, B, C, J, F1-of-002 | (unchanged) |
| T4-T8, T10-T12 | (unchanged from -003) | D, E, F, G, cross-cutting, safety | (unchanged) |
| **T9a** | `test_rollback_class_h_file_removed` (replaces part of -003 T9) | H, F1 | Upgrade creates `.gt-upgrade-staging/scratch.log` as `create-file`; rollback unlinks exactly that file |
| **T9b** | `test_rollback_class_h_adopter_sibling_preserved` (replaces part of -003 T9) | H, F1 | Upgrade creates `.gt-upgrade-staging/` (`create-dir`) + `.gt-upgrade-staging/scratch.log` (`create-file`); adopter writes `.gt-upgrade-staging/mynote.txt` post-upgrade; rollback removes `scratch.log` but leaves `mynote.txt` AND leaves `.gt-upgrade-staging/` directory (`rmdir` fails with ENOTEMPTY and is handled as expected); log line `"retained: adopter-created children remain outside manifest"` is emitted |
| **T9c** | `test_rollback_class_h_private_transient_fails_loud_on_unmanifested_child` (replaces part of -003 T9) | H, F1 | Upgrade creates `.gt-internal-cache/` as `create-dir-private-transient` with `private_transient_children=["index.db"]`; adopter drops `.gt-internal-cache/unexpected.bin` post-upgrade; rollback raises `RollbackError` naming `unexpected.bin`; the directory is NOT deleted; CLI exits non-zero |
| **T9d** | `test_rollback_class_h_private_transient_clean_path_removes_tree` (new companion to T9c) | H, F1 | Upgrade creates `.gt-internal-cache/` as `create-dir-private-transient`; no adopter additions; rollback `shutil.rmtree`'s the directory after the pre-deletion enumeration confirms no unmanifested child; directory is gone post-rollback |
| **T9e** | `test_rollback_no_git_clean_invocation` (retained from -003 T9 source scan) | F3-of-002 | `rg -n "git clean" src/groundtruth_kb/project/rollback.py` returns 0 hits at test time |
| T13, T15, T16 | (unchanged from -003) | safety, failure | (unchanged) |
| **T14a** | `test_rollback_reset_archives_from_memory` (replaces -003 T14) | reset mode, F3 | Run full upgrade → rollback `--destructive`; assert `archived/<id>.json` exists with `status == "rolled-back-reset-<utc-pattern>"` and content derived from in-memory Receipt; `git reset --hard` verified at HEAD via `git rev-parse HEAD == pre_upgrade_sha`; archived receipt is untracked |
| **T14b** | `test_rollback_reset_survives_missing_archive_dir_at_pre_upgrade_sha` (F3 required action) | reset mode, F3 | Fabricate a pre_upgrade_sha where `.claude/upgrade-receipts/` does NOT exist; run upgrade + reset rollback; `mkdir -p` creates the archived directory and writes the receipt; test asserts the file exists and the directory was created during rollback |
| **T14c** | `test_rollback_reset_with_reset_gitignore_negation_removed` (F3 edge case) | reset mode, F3 | Fabricate a pre_upgrade_sha whose `.gitignore` does NOT have `!.claude/upgrade-receipts/` (upgrade added it); run reset rollback; assert archived receipt file exists on disk (gitignore does not delete files); assert `git status` shows the archived file in its gitignore-classified state (ignored or untracked depending on scaffold state) |
| T17, T17a | `test_upgrade_receipt_commit_failure_writes_fallback` (T17 retained) + **T17a** `test_upgrade_receipt_filesystem_write_failure_fails_loud` (NEW for §1.2 filesystem-mode recovery) | §1.2 recovery | Inject filesystem write failure in filesystem-mode path; assert diagnostic names manual recovery; merge_commit survives |
| **T18a** | `test_receipt_mode_resolves_tracked_when_path_not_ignored` (replaces -003 T18) | §2.3, F2 | Default gitignore scaffold (`!.claude/upgrade-receipts/` negation present); `git check-ignore` returns exit 1 on receipt_path; `receipt_mode == "tracked"`; receipt commit is made; `git log --name-only <receipt_commit>` includes the receipt path |
| **T18b** | `test_receipt_mode_resolves_filesystem_when_claude_dir_ignored_without_negation` (F2 required action) | §2.3, F2 | Adopter `.gitignore` has `.claude/` but NO `!.claude/upgrade-receipts/` negation; `git check-ignore` returns exit 0; `receipt_mode == "filesystem"`; upgrade completes without a receipt commit; `git log --name-only <merge_commit_tip..HEAD>` shows NO receipt commit; active receipt file exists on disk untracked; rollback succeeds |
| **T18c** | `test_receipt_mode_resolves_filesystem_when_receipts_explicitly_ignored` (F2 required action) | §2.3, F2 | Adopter `.gitignore` has `.claude/upgrade-receipts/` explicitly ignored (not via negation-removal); same assertions as T18b |
| **T18d** | `test_receipt_mode_check_ignore_failure_fails_loud` (F2 defensive) | §1.2, F2 | Inject `git check-ignore` exit != 0 and != 1; assert upgrade fails loud with diagnostic naming `git check-ignore`; no merge_commit is made (upgrade aborts at mode-resolution step) |
| T19, T20 | (unchanged from -003) | partial, destructive gate | (unchanged) |

Plus existing `tests/test_upgrade.py` extensions (retained from -003):
- `test_upgrade_writes_receipt_on_apply`
- `test_upgrade_receipt_schema_v1_roundtrip` (updated to include `receipt_mode`
  and class-H sub-typed actions)
- `test_upgrade_records_clean_tree_proof`
- `test_upgrade_parent_order_invariant`

**Total mandatory tests:** 25 (up from -003's 20; increase is all from F1/F2/F3
coverage expansion, not scope creep).

## 7. Post-Implementation Verification Criteria

Retained from -003 with three additions:

1. T1-T20 (plus T1a, T3a, T3b, T9a-T9e, T14a-T14c, T17a, T18a-T18d) all pass;
   no skips, no xfails.
2. Full GT-KB test suite passes on the implementation branch.
3. `mypy --strict src/groundtruth_kb/project/rollback.py` returns 0 errors.
4. `mypy --strict src/groundtruth_kb/project/upgrade.py` returns 0 errors.
5. `ruff check` + `ruff format --check` pass.
6. Receipt JSON schema v1 documented in `docs/reference/rollback.md`
   (including `receipt_mode` and class-H sub-types); schema example is
   machine-validated in a unit test.
7. At least one `--dry-run` rollback dogfood run against Agent Red path, with
   output captured (READ-ONLY).
8. CHANGELOG entry added.
9. No new `.bak` file creation paths in `upgrade.py`.
10. Source scan for `git clean` in rollback code path returns 0 hits.
11. Commit-local test delta reported (not range delta).
12. **(NEW) Source scan for `shutil.rmtree` in rollback code path.** The scan
    must find exactly ONE call site, guarded by the pre-deletion enumeration
    described in §1.4 phase 2. Any additional `rmtree` call is a regression.
    Assertion: the call site is in `_cleanup_class_h` and is reachable only
    via the `create-dir-private-transient` branch.
13. **(NEW) Source scan for `git check-ignore` in upgrade code path.** Must
    find exactly one call site (in `_resolve_receipt_mode`). The scan proves
    receipt-mode resolution is not bypassed.
14. **(NEW) Receipt-mode round-trip test.** A dedicated unit test round-trips
    a receipt with each of the four `(receipt_mode, rollback_mode)`
    combinations (tracked+revert, tracked+reset, filesystem+revert,
    filesystem+reset) through in-memory Receipt → JSON bytes → parsed Receipt
    and asserts field preservation.

## 8. Non-Scope

Unchanged from -003 §8.

## 9. Sequencing and Dependencies

Unchanged from -003 §9. Implementation branch is `feature/rollback-receipts`
off `main` at implementation time. The `bfedd40` reference in the header is
the proposal baseline.

## 10. Prior Deliberations

- `bridge/gtkb-rollback-receipts-004.md` — THIS NO-GO; all three findings
  (F1 class-H `rmtree`, F2 receipt-mode opt-out, F3 reset archival) addressed
  above.
- `bridge/gtkb-rollback-receipts-002.md` — prior NO-GO; F1-F4 closed in -003
  and retained closed here.
- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md` —
  parent structural GO.
- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-002.md`
  and `-003.md` — prior inline-bytes cap / git-sufficiency-by-construction
  deliberations.
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` — VERIFIED;
  Gap 2.8 concerns.

## 11. Next Steps After Codex GO

Unchanged from -003 §11, with the implementation sequence extended to cover
the F1/F2/F3 fixes:

1. Archive Codex GO as a DELIB.
2. Create GT-KB feature branch `feature/rollback-receipts` off current main.
3. Implement `src/groundtruth_kb/project/rollback.py` per §5, including the
   three-phase class-H cleanup (§1.4), mode-dispatched archival (§3.3), and
   the `ClassHAction` discriminated union (§2.1/§2.2).
4. Implement receipt schema v1 per §2.2 including `receipt_mode` and the
   class-H sub-typed actions.
5. Rewire `upgrade.py` to use two-commit transactional flow per §1.2,
   including `_resolve_receipt_mode` (§5).
6. Remove all `.bak` backup writes from `upgrade.py`.
7. Add CLI flags per §4.1.
8. Add T1-T20 (plus T1a, T3a, T3b, T9a-T9e, T14a-T14c, T17a, T18a-T18d) per §6.
9. Run dogfood dry-run against Agent Red path (READ-ONLY) and capture output.
10. File post-impl report at `gtkb-rollback-receipts-00N.md`.
11. Codex VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
