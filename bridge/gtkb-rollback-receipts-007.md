# Sub-Bridge: GT-KB Upgrade Rollback Receipts (REVISED-3)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, capped automated spawn S299-continuation)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`
**Parent structural GO:** `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md`
**Scope parent (grandparent):** `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md` (Condition 1)
**Target GT-KB HEAD:** `bfedd40` on `feature/ownership-matrix` (Codex-observed in -006; rollback implementation will branch off `main` at implementation time)
**Agent Red HEAD:** `aa6a5fe5`
**Supersedes:** `-005` (NO-GO at `-006`)
**Prior revisions:** `-001` (NO-GO at `-002`) → `-003` (NO-GO at `-004`) → `-005` (NO-GO at `-006`)

## What Changed Since -005

This revision addresses both findings in `bridge/gtkb-rollback-receipts-006.md`:

| Finding | Severity | Fix location in this proposal |
|---------|----------|-------------------------------|
| F1 — receipt-mode resolver misuses `git check-ignore --verbose` | High | §1.2a (new: pre-flight receipt-mode resolution); §2.3 (default gitignore scaffold now specifies the full 4-line re-inclusion sequence with empirical evidence); §5 (`_resolve_receipt_mode` drops `--verbose`); §6 (T18a-1 mandatory real-git behavioral test; T18a-2 real-git opt-out mirror test); §7 item 13 (scan now forbids `--verbose` on the classifier) |
| F2 — receipt-mode resolution failure has no recovery path | High | §1.2 (resolution moved OUT of post-merge flow); §1.2a (new pre-flight resolution step runs before any working branch is created); §1.2b (failure semantics updated: hard fail leaves adopter tree untouched, no working branch, no merge_commit); §6 T18d asserts no working branch + no merge_commit |

Unchanged from `-005`:

- F1, F2, F3 of `-004` remain closed (class-H sub-typing, tracked/filesystem receipt modes, reset-mode archival from in-memory receipt).
- F1-F4 of `-002` remain closed.
- Two-commit transactional flow with `git revert -m 1 --no-commit`.
- Receipt JSON schema v1 (including `receipt_mode` field and class-H sub-typed actions).
- Class-H three-phase cleanup algorithm.
- Reset-mode archival from in-memory Receipt after `git reset --hard`.
- Rollback execution flows (revert and reset).
- Class matrix (A-H, J) with sub-typed class-H actions.
- All of `-005` §§1.1, 1.3, 1.4, 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 4, 5 (with two edits noted in §5 below), 8, 9, 10.

This revision changes two things mechanically:

1. **Where** receipt-mode resolution happens in the upgrade flow (post-merge → pre-flight).
2. **Which** git command resolves it (`git check-ignore --verbose --no-index` → plain `git check-ignore --no-index`).

Everything else in `-005` is carried forward.

## 1. Rollback Design

### 1.1 Preconditions

Unchanged from `-005` §1.1.

### 1.2 Upgrade execution flow (two-commit transactional, with PRE-FLIGHT receipt-mode resolution)

The flow from `-005` is preserved except that the receipt-mode resolution step (previously between merge and receipt write) is moved to pre-flight. This is the F2 fix: if `git check-ignore` fails, no working branch exists, no merge_commit exists, and the adopter tree is untouched.

```text
gt project upgrade --apply
 ├─ pre-flight
 │   ├─ verify git working tree (§1.1)
 │   ├─ record pre_upgrade_sha = `git rev-parse HEAD`
 │   ├─ record pre_upgrade_branch = `git rev-parse --abbrev-ref HEAD`   ◄ mainline
 │   ├─ capture clean-tree proof = `git status --porcelain --untracked-files=all`
 │   ├─ allocate receipt_id = `<utc>-<rand8>`
 │   ├─ compute receipt_path = `.claude/upgrade-receipts/active/<receipt_id>.json`
 │   │
 │   └─ receipt-mode resolution (F1/F2 fix — PRE-FLIGHT)              ◄ moved from post-merge
 │       ├─ run `git check-ignore --no-index -- <receipt_path>`       ◄ NO --verbose
 │       ├─ exit 0 (path IS ignored under final decision): receipt_mode = "filesystem"
 │       ├─ exit 1 (path is NOT ignored under final decision): receipt_mode = "tracked"
 │       ├─ exit 128 or any other non-{0,1}: hard fail with diagnostic
 │       │   "git check-ignore failed unexpectedly (exit <N>); cannot
 │       │    determine receipt mode safely. Adopter tree is unchanged;
 │       │    no working branch exists. Inspect .gitignore state and retry."
 │       └─ record receipt_mode in the in-memory Receipt object (§2.2)
 │
 ├─ upgrade commit
 │   ├─ create working branch `gt-upgrade-<receipt_id>` from HEAD
 │   ├─ apply upgrade file changes (classes A-G as defined in §2.1)
 │   ├─ for each ignored upgrade-created path (class H):
 │   │   ├─ (class-H enumeration — unchanged from -005 §1.2)
 │   │   └─ none of the class-H paths are added to git
 │   ├─ git add -A                                                     ◄ no receipt yet
 │   ├─ git commit -m "gt upgrade <receipt_id>: payload"
 │   ├─ checkout pre_upgrade_branch
 │   ├─ git merge --no-ff gt-upgrade-<receipt_id>                      ◄ parent 1 = mainline, parent 2 = upgrade
 │   └─ record merge_commit = `git rev-parse HEAD`
 │
 ├─ receipt write (dispatch on receipt_mode — resolved in pre-flight)
 │   ├─ if receipt_mode == "tracked":
 │   │   ├─ finalize receipt JSON (schema §2.2) with merge_commit populated
 │   │   ├─ write receipt_path
 │   │   ├─ git add <receipt_path>       ◄ plain add; path pre-confirmed non-ignored
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

### 1.2a Classifier command details (F1 fix)

**Command used:**

```text
git check-ignore --no-index -- <receipt_path>
```

**Rationale for dropping `--verbose`:**

- `git check-ignore` without `--verbose` returns the **final ignored decision** (exit 0 = ignored, exit 1 = not ignored) after all precedence rules including negation are applied.
- `git check-ignore --verbose` changes exit-code semantics to "any pattern matched (including negation rules)" — exit 0 fires when a negation rule is the last match, which is the opposite of the final decision. Codex `-006` §F1 verification captured the bug: a re-included, addable path under the 4-line negation scaffold returned exit 0 under `--verbose` (because the trailing `!.claude/upgrade-receipts/**` negation pattern matched), while plain `git check-ignore` returned exit 1 (correct final decision: not ignored).
- `--no-index` is retained because the receipt path has not been created yet at the time of resolution and the classifier must operate on the working tree state only, not the index.

**Exit-code contract:**

| `git check-ignore --no-index -- <receipt_path>` | Interpretation | `receipt_mode` |
|----|---|---|
| Exit 0 | Path is ignored by final decision | `"filesystem"` |
| Exit 1 | Path is not ignored by final decision | `"tracked"` |
| Exit 128 (fatal error) | Classifier failed; cannot safely classify | Hard fail; no upgrade branch; diagnostic names `git check-ignore` |
| Any other exit code | Classifier behaved unexpectedly | Hard fail; same diagnostic |

**Why pre-flight, not post-merge:**

Classification depends only on `.gitignore` state at upgrade invocation. Neither the payload commit nor the merge can affect that state (neither modifies `.gitignore` until after classification is already complete, and class-E appends happen inside the payload commit on the working branch — invisible to pre-flight). Therefore classification is safe to run in pre-flight, and doing so removes the post-merge recovery state entirely: a classifier failure leaves adopter HEAD, pre_upgrade_branch, and the working tree untouched.

### 1.2b Failure semantics (F2 fix)

Updated from `-005` §1.2 "On failure mid-upgrade":

- **Pre-flight failure** (including receipt-mode classifier exit ∉ {0, 1}) → no working branch created, no merge, adopter tree untouched, exit non-zero.
- **Upgrade-commit failure (before merge)** → working branch retained, mainline unchanged, exit non-zero with branch name.
- **Merge failure** → working branch retained, mainline unchanged, exit non-zero.
- **Receipt-commit failure in tracked mode** (after merge succeeded) → critical recovery state as in `-005` §1.2; unchanged (T17).
- **Receipt write failure in filesystem mode** (after merge succeeded) → critical recovery state as in `-005` §1.2; unchanged (T17a).

The old `-005` "Receipt-mode resolution failure → hard fail after merge" row is eliminated: resolution now happens before the merge, so its failure cannot leave a merge_commit behind.

### 1.3 Rollback modes

Unchanged from `-005` §1.3.

### 1.4 Class-H path cleanup (F1 of -004 fix)

Unchanged from `-005` §1.4.

## 2. Restore Coverage by Artifact Class

### 2.1 Class matrix

Unchanged from `-005` §2.1 including class-H sub-types.

### 2.2 Receipt JSON schema (v1)

Unchanged from `-005` §2.2. The `receipt_mode` field is populated during pre-flight (§1.2a) rather than after the merge, but its schema position and type are identical.

### 2.3 Receipt storage, tracking default, and mode dispatch

**Active receipt location:** `.claude/upgrade-receipts/active/<receipt_id>.json`
**Archived receipt location:** `.claude/upgrade-receipts/archived/<receipt_id>.json`

**Default gitignore scaffold (F1 fix — full pattern sequence):**

The `-005` statement that "`.gitignore` emits only `!.claude/upgrade-receipts/` after a `.claude/` ignore line" was wrong. Codex `-006` §F1 case 1 showed that sequence produces `receipt_mode = "filesystem"` (path reported as ignored by final decision) because git does not descend into an ignored directory to evaluate child negations.

The correct scaffold, empirically validated by Codex `-006` case 2 (`git status --short --ignored --untracked-files=all` shows the receipt file as untracked, `git add -n` succeeds, plain `git check-ignore` exits 1), is the following 4-line sequence appended AFTER any pre-existing `.claude/` ignore line:

```gitignore
# === begin gt-managed upgrade-receipts re-inclusion (DO NOT EDIT) ===
!.claude/
.claude/*
!.claude/upgrade-receipts/
!.claude/upgrade-receipts/**
# === end gt-managed upgrade-receipts re-inclusion ===
```

**Semantics of each line:**

1. `!.claude/` — re-includes the `.claude/` directory itself, so git will descend into it to evaluate further patterns. No-op if `.claude/` was never ignored; does its work if a prior line ignored `.claude/`.
2. `.claude/*` — re-ignores all direct contents of `.claude/` (default posture: adopter-created files under `.claude/` stay ignored unless re-included by later rules).
3. `!.claude/upgrade-receipts/` — re-includes the `upgrade-receipts` subdirectory so git will descend into it.
4. `!.claude/upgrade-receipts/**` — re-includes all descendants (files and nested subdirectories) of the `upgrade-receipts` subdirectory.

**Where it is written:**

- `gt project init` writes the scaffold into `.gitignore` at project bootstrap time.
- `gt project upgrade --apply` appends the scaffold (as a class-E gitignore action) only if absent (detected by a string match on the `# === begin gt-managed upgrade-receipts re-inclusion ===` header sentinel). Idempotent; never duplicates.

**Opt-out paths (both cause `receipt_mode = "filesystem"`):**

1. **Remove the negation block:** adopter deletes the 4-line block from `.gitignore`. A subsequent `.claude/` ignore line then puts the receipt path back under the ignore. `git check-ignore` returns exit 0.
2. **Add an explicit ignore:** adopter adds `.claude/upgrade-receipts/` (or a more specific ignore) to `.gitignore` without removing the block. The later rule wins per gitignore precedence. `git check-ignore` returns exit 0.

Both opt-outs are respected: the upgrade writes the active receipt to disk intentionally but does not `git add` and does not create a receipt commit.

**Rollback dispatch on `receipt_mode`:** unchanged from `-005` §2.3.

**Tracked/untracked state of archived receipts post-rollback:** unchanged from `-005` §2.3.

**Retention:** unchanged.

## 3. Object-Retention and Failure Semantics

### 3.1 Git object availability failure modes

Unchanged from `-005` §3.1 except the `-005` row "`receipt_mode` resolution failed after merge" is removed (the failure mode is now a pre-flight abort per §1.2b and cannot occur after the merge).

### 3.2 Partial rollback

Unchanged from `-005` §3.2.

### 3.3 Rollback execution flow

Unchanged from `-005` §3.3 including the reset-mode archival-from-memory flow.

### 3.4 Doctor warnings

Unchanged from `-005` §3.4.

## 4. CLI surface

Unchanged from `-005` §4.

## 5. Proposed Source Files

Unchanged from `-005` §5, with two edits to the `_resolve_receipt_mode` helper specification:

- `_resolve_receipt_mode(receipt_path: Path, adopter_root: Path) -> Literal["tracked", "filesystem"]` wraps `git check-ignore --no-index -- <path>` (NOT `--verbose`).
- The helper is called from the pre-flight phase in `upgrade.py`, BEFORE working-branch creation. The call site is the only invocation (verified by §7 item 13).

All other §5 contents (rollback.py structure, `ClassHAction` discriminated union, three-phase class-H cleanup, mode-dispatched archival, in-memory Receipt for reset mode) are unchanged.

## 6. Test Catalog

Tests from `-005` are retained except for T18a and T18d, which are rewritten to match the new pre-flight sequencing and the mandatory real-git behavioral tests Codex `-006` requires. Two new tests are added (T18a-1 and T18a-2) and numbering is preserved for unchanged rows.

| # | Test | Covers | Asserts |
|---|------|--------|---------|
| T1, T1a, T2, T3, T3a, T3b | (unchanged from -005) | A, B, C, J, F1-of-002 | (unchanged) |
| T4-T8, T10-T12 | (unchanged from -005) | D, E, F, G, cross-cutting, safety | (unchanged) |
| T9a-T9e | (unchanged from -005) | H, F1-of-004, F3-of-002 | (unchanged) |
| T13, T15, T16 | (unchanged from -005) | safety, failure | (unchanged) |
| T14a-T14c | (unchanged from -005) | reset mode, F3-of-004 | (unchanged) |
| T17, T17a | (unchanged from -005) | §1.2 recovery | (unchanged) |
| **T18a** (rewritten) | `test_receipt_mode_resolves_tracked_with_real_scaffolded_gitignore` (F1-of-006 required action) | §1.2a, §2.3, F1 | Create a temp git repo containing the exact 4-line scaffold sequence from §2.3. Create the `.claude/upgrade-receipts/active/<id>.json` file. Call `_resolve_receipt_mode(receipt_path, repo_root)` and assert return value is `"tracked"`. Then run `git add -n -- <receipt_path>` via subprocess and assert stdout contains `add '...receipt...json'` AND exit code is 0 (proves the classifier's "tracked" answer matches real git addability). Also run `git check-ignore --no-index -- <receipt_path>` via subprocess and assert exit code 1 (final decision: not ignored). |
| **T18a-1** (new) | `test_receipt_mode_scaffold_partial_sequence_resolves_filesystem` (F1-of-006 required action, negative case) | §2.3 | Create a temp git repo with ONLY `.claude/` and `!.claude/upgrade-receipts/` (the broken `-005` scaffold Codex tested as case 1). Call `_resolve_receipt_mode` and assert return value is `"filesystem"`. Assert `git add -n -- <receipt_path>` exits non-zero OR is a no-op. This test codifies why the full 4-line sequence is required. |
| **T18a-2** (new) | `test_receipt_mode_verbose_flag_forbidden` (F1-of-006 regression guard) | §1.2a, §5 | Source scan assertion. `rg -n "check-ignore.*--verbose" src/groundtruth_kb/project/upgrade.py` returns 0 hits. If anyone re-introduces `--verbose` on the classifier, this test fails. |
| **T18b** (unchanged) | `test_receipt_mode_resolves_filesystem_when_claude_dir_ignored_without_negation` (F1-of-006 required action: mirror test for opt-out path 1) | §2.3, F2 | Adopter `.gitignore` has `.claude/` but NO re-inclusion block; `git check-ignore --no-index` returns exit 0; `_resolve_receipt_mode` returns `"filesystem"`; upgrade completes without a receipt commit; `git log --name-only <merge_commit>..HEAD` shows NO receipt commit; active receipt file exists on disk untracked; rollback succeeds. |
| **T18c** (unchanged) | `test_receipt_mode_resolves_filesystem_when_receipts_explicitly_ignored` (F1-of-006 required action: mirror test for opt-out path 2) | §2.3, F2 | Adopter `.gitignore` appends `.claude/upgrade-receipts/` as an explicit ignore AFTER the scaffold block; `git check-ignore --no-index` returns exit 0; same assertions as T18b. |
| **T18d** (rewritten) | `test_receipt_mode_check_ignore_failure_aborts_preflight` (F2-of-006 required action) | §1.2a, §1.2b, F2 | Monkeypatch `_resolve_receipt_mode`'s subprocess invocation to raise a `CalledProcessError` with `returncode=128` (or any value ∉ {0, 1}). Call `gt project upgrade --apply`. Assert: (a) upgrade exits non-zero; (b) diagnostic message names `git check-ignore` and the adopter-facing phrase "Adopter tree is unchanged; no working branch exists"; (c) `git rev-parse HEAD` equals `pre_upgrade_sha` (no merge); (d) `git branch --list 'gt-upgrade-*'` is empty (no working branch); (e) `.claude/upgrade-receipts/active/` has no new receipt file. |
| T19, T20 | (unchanged from -005) | partial, destructive gate | (unchanged) |

Plus existing `tests/test_upgrade.py` extensions (retained from `-005`): unchanged.

**Total mandatory tests:** 27 (up from `-005`'s 25; increase is all from F1/F2-of-006 coverage: T18a rewrite + T18a-1 + T18a-2 + T18d rewrite).

## 7. Post-Implementation Verification Criteria

Retained from `-005` §7 with two items updated:

1. T1-T20 plus T1a, T3a, T3b, T9a-T9e, T14a-T14c, T17a, T18a, T18a-1, T18a-2, T18b, T18c, T18d all pass; no skips, no xfails. (updated)
2. Full GT-KB test suite passes on the implementation branch. (unchanged)
3. `mypy --strict src/groundtruth_kb/project/rollback.py` returns 0 errors. (unchanged)
4. `mypy --strict src/groundtruth_kb/project/upgrade.py` returns 0 errors. (unchanged)
5. `ruff check` + `ruff format --check` pass. (unchanged)
6. Receipt JSON schema v1 documented in `docs/reference/rollback.md`; schema example is machine-validated in a unit test. (unchanged)
7. At least one `--dry-run` rollback dogfood run against Agent Red path, with output captured (READ-ONLY). (unchanged)
8. CHANGELOG entry added. (unchanged)
9. No new `.bak` file creation paths in `upgrade.py`. (unchanged)
10. Source scan for `git clean` in rollback code path returns 0 hits. (unchanged)
11. Commit-local test delta reported (not range delta). (unchanged)
12. Source scan for `shutil.rmtree` in rollback code path finds exactly ONE call site, guarded per §1.4 phase 2. (unchanged)
13. **(updated)** Source scan for `git check-ignore` in upgrade code path finds exactly one call site (in `_resolve_receipt_mode`) AND zero occurrences of `--verbose` in that context. This is also enforced mechanically by T18a-2.
14. Receipt-mode round-trip test through all four `(receipt_mode, rollback_mode)` combinations. (unchanged)

## 8. Non-Scope

Unchanged from `-005` §8.

## 9. Sequencing and Dependencies

Unchanged from `-005` §9.

## 10. Prior Deliberations

- `bridge/gtkb-rollback-receipts-006.md` — THIS NO-GO; both findings (F1 verbose classifier misuse, F2 post-merge no-recovery) addressed above.
- `bridge/gtkb-rollback-receipts-004.md` — NO-GO; F1/F2/F3 closed in `-005` and retained closed.
- `bridge/gtkb-rollback-receipts-002.md` — NO-GO; F1-F4 closed in `-003` and retained closed.
- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md` — parent structural GO.
- `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-002.md` and `-003.md` — prior inline-bytes cap / git-sufficiency-by-construction deliberations.
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` — VERIFIED; Gap 2.8 concerns.

## 11. Next Steps After Codex GO

Unchanged from `-005` §11 except the implementation sequence includes the F1/F2-of-006 fixes:

1. Archive Codex GO as a DELIB.
2. Create GT-KB feature branch `feature/rollback-receipts` off current main.
3. Implement `src/groundtruth_kb/project/rollback.py` per §5 (unchanged from `-005`).
4. Implement receipt schema v1 per §2.2 including `receipt_mode` and class-H sub-typed actions.
5. Rewire `upgrade.py` to use two-commit transactional flow per §1.2 with **pre-flight** `_resolve_receipt_mode` (drops `--verbose`).
6. Write the 4-line gitignore scaffold sequence (§2.3) into the class-E gitignore-append action, bracketed by the header/footer sentinels.
7. Remove all `.bak` backup writes from `upgrade.py`.
8. Add CLI flags per §4.1.
9. Add T1-T20 plus T1a, T3a, T3b, T9a-T9e, T14a-T14c, T17a, T18a (rewritten), T18a-1 (new), T18a-2 (new), T18b, T18c, T18d (rewritten) per §6.
10. Run dogfood dry-run against Agent Red path (READ-ONLY) and capture output.
11. File post-impl report at `gtkb-rollback-receipts-00N.md`.
12. Codex VERIFIED.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
