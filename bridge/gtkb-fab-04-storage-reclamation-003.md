REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-04-storage-reclamation
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — bridge auto-dispatch session
Date: 2026-06-11
Responds to: bridge/gtkb-fab-04-storage-reclamation-002.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4416
Project Authorization: PAUTH-FAB04-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 1bcfec08-a06c-4274-be29-95dedddcf350
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: bridge auto-dispatch, ::init gtkb pb

target_paths: ["scripts/hygiene/stray_detector.py", "platform_tests/scripts/test_work_tree_stray_detector.py", ".claude/worktrees/**", "groundtruth.db.corrupt-S311-20260426-104115", "groundtruth.db.pre-backfill-20260412-135740", "knowledge-export-20260516T235145Z.json", ".git/cursor/**", ".git/*.index", ".git/lfs/**", ".git/objects/**", ".git/packed-refs", ".git/refs/**", ".git/logs/**", "groundtruth.db"]

KB mutation: the sole MemBase mutation is the WI-3394 not-reproducing closure (owner-approved per the HYG-013 decision); `groundtruth.db` is included in target_paths to declare it.

---

# FAB-04 — Storage reclamation: git-LFS orphans, orphaned worktrees, root DB residue

WI-4416 (FAB-04) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-013, HYG-057, HYG-058.
Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

## Revision Scope (REVISED-003, addressing NO-GO `-002`)

`-002` issued a single NO-GO finding (FINDING-P1-001): the `-001` `target_paths`
list omitted paths the proposal says implementation will mutate. This revision
takes the **expand** option Codex offered (not the narrow option), because the
proposed work genuinely edits a test file and genuinely rewrites `.git`
repository state:

1. **Test surface.** The proposal extends `scripts/hygiene/stray_detector.py`
   and verifies with `pytest platform_tests/scripts/test_work_tree_stray_detector.py`.
   That existing test file **will be edited** (a new assertion that a stale
   `.claude/worktrees/*` dir is detected), so
   `platform_tests/scripts/test_work_tree_stray_detector.py` is now listed in
   `target_paths`.
2. **Repository-state surface.** `git lfs prune` and `git gc` rewrite material
   `.git` state beyond the previously-listed `.git/cursor/**` and `.git/*.index`.
   `target_paths` now additionally covers `.git/lfs/**` (LFS object cache pruned
   by `git lfs prune`), `.git/objects/**` (loose→packed object rewrite by `git
   gc`), `.git/packed-refs`, `.git/refs/**`, and `.git/logs/**` (reflog/ref state
   that `git gc` repacks and prunes). These are the destructive repository-state
   surfaces the prune/gc pass touches; per the destructive nature of this item
   they are now explicit rather than implicit.

No other content changed. The owner decision set, PAUTH scope, spec links,
acceptance criteria, and risk/rollback are unchanged from `-001`.

## Summary

~10.8 GB of dead file-level residue on the `E:\` volume, across three surfaces:

- **HYG-013** — `.git` is 5.4 GB; **4.76 GB is 4 orphaned 1.19 GB LFS objects**
  (corrupt-DB-era copies; `git lfs ls-files` empty + no `.gitattributes` LFS
  patterns = unreachable cache) plus 152 MB `.git/cursor` residue and 6 stray
  `*.index` files. The stale work item that claimed a broken blob verifies clean
  today (`git cat-file -e` exit 0), so it is closed not-reproducing.
- **HYG-057** — `.claude/worktrees/` holds **12 orphaned working copies (~3 GB)**
  (one is 1.52 GB), none registered with `git worktree` — dead detached checkouts
  that also pollute repo-wide greps with worktree-internal hits.
- **HYG-058** — **~3 GB of dead DB residue** at root: `groundtruth.db.corrupt-S311-20260426-104115`
  (1.25 GB), `groundtruth.db.pre-backfill-20260412-135740` (80 MB),
  `knowledge-export-20260516T235145Z.json` (1.66 GB) — all gitignored, canonical
  1.38 GB MemBase healthy.

Owner-approved (`DELIB-FAB04-REMEDIATION-20260610`): full `.git` maintenance pass
+ close the stale WI, verify-then-delete all 12 worktrees, delete all three DB
artifacts. This cluster is **file-level storage reclamation only**.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority governing this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant governing
  specs cited (satisfied here).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives
  measurable checks from the linked specs.
- `GOV-STANDING-BACKLOG-001` — WI-4416 is the governed backlog authority for this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — FAB-04 **relocates nothing and writes
  no out-of-root artifacts**: this bridge file resides under `E:\GT-KB\bridge\`, and
  all deletion targets plus the `stray_detector` edit are in-root. It notes (does not
  fix) that the only git-registered worktrees currently live outside the project root
  under the user profile and temp directories, and it **routes** the absorbed stale
  `applications/`-origin Docusaurus build residue to FAB-12 rather than touching it
  here. No new out-of-placement artifacts are introduced.

Governing rule (non-spec): `.claude/rules/project-root-boundary.md` (Drive-sync
amplification rationale; `.git/` and DB snapshots already `.driveignore`-excluded).

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory
  (HYG-013/057/058 in the FAB-04 row); evidence frozen, do not re-derive.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB04-REMEDIATION-20260610` — this cluster's owner-decision set (the AUQ batch).
- `bridge/gtkb-fab-04-storage-reclamation-002.md` — Codex NO-GO that scoped this
  REVISED (FINDING-P1-001, target-path precision before destructive work).
- _The stale broken-blob defect WI-3394 (verifies clean today) is closed by this
  proposal, not absorbed as scope; no prior bridge thread exists on this storage
  reclamation._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10 (interactive owner session),
persisted to `DELIB-FAB04-REMEDIATION-20260610`:

1. **HYG-013 = Full `.git` pass + close WI-3394** — `git lfs prune` the 4 orphaned
   objects + remove 6 stray `*.index` + `.git/cursor` + `git gc`; close WI-3394
   not-reproducing. (Rejected: LFS-prune-only; defer.)
2. **HYG-057 = Verify-then-delete all 12 worktrees** — check each for
   uncommitted/unpushed deltas, archive stranded drafts, then prune + delete;
   extend `stray_detector` scope. (Rejected: delete-only->30d; keep-detector-only.)
3. **HYG-058 = Delete all three DB artifacts** — corrupt-S311 + pre-backfill +
   knowledge-export. (Rejected: move-to-offline-first; keep-corrupt-for-forensics; defer.)

This REVISED introduces no new owner decision; the target-path expansion is a
mechanical scope-precision correction within the already-approved actions.

## Requirement Sufficiency

**Existing requirements sufficient.** Governed by `GOV-STANDING-BACKLOG-001`
(WI authority) and `.claude/rules/project-root-boundary.md` (storage/Drive-sync
discipline); the specific destructive actions are fixed by
`DELIB-FAB04-REMEDIATION-20260610`. No new requirement is needed; the
`stray_detector` scope extension encodes a recurrence-prevention invariant derived
from HYG-057.

## Scope and Boundaries

In scope: `git lfs prune` + stray `.git` cleanup + `git gc`; verify-then-delete the
12 `.claude/worktrees/` copies + extend `stray_detector` (source + test); delete the 3 root DB
artifacts; close WI-3394.

Out of scope (routed, not handled here):
- The in-DB `pipeline_events` bloat (HYG-014, ~90% of groundtruth.db) → **FAB-11**
  (retention + VACUUM). FAB-04 touches no MemBase table rows except the WI-3394
  closure.
- HYG-058 absorbed tracked-residue: stale agentredcx.com Docusaurus build
  (`assets/` + `sitemap.xml` + empty `docs-site/` husk) → **FAB-12** (Agent-Red
  residue); tracked root scratch (`.tmp-*.py`, `_split_superadmin.py`, `vision.md`,
  `uv.lock`) + the active `$null`-producer bug + `.gitignore` gaps → **FAB-23**.

## Proposed Implementation

1. **`.git` maintenance** (repository_state): confirm `git lfs ls-files` empty →
   `git lfs prune`; delete the 6 stray `*.index` files + `.git/cursor/`; `git gc`.
   Record before/after `.git` size. (Touches `.git/lfs/**`, `.git/objects/**`,
   `.git/packed-refs`, `.git/refs/**`, `.git/logs/**`, `.git/cursor/**`,
   `.git/*.index`.)
2. **Worktrees**: for each of the 12 `.claude/worktrees/` dirs, check
   `git status`/unpushed deltas; archive any stranded bridge drafts; `git worktree
   prune` + delete. Extend `scripts/hygiene/stray_detector.py` scope to flag
   stale `.claude/worktrees/*` so harness-spawned worktrees are reaped automatically,
   and extend `platform_tests/scripts/test_work_tree_stray_detector.py` with a
   stale-worktree detection assertion.
3. **Root DB residue**: delete the three gitignored artifacts.
4. **WI-3394 closure**: resolve as not-reproducing with `git cat-file -e` evidence
   (post-GO MemBase op; `--owner-approved` per the recorded decision).

## Spec-Derived Verification Plan

| Spec / requirement | Derived check |
|---|---|
| `.claude/rules/project-root-boundary.md` (storage/Drive discipline) | before/after sizes: `.git` drops ~4.9 GB, `.claude/worktrees/` → 0, root sheds ~3 GB; `git lfs ls-files` empty post-prune |
| HYG-057 recurrence prevention | `stray_detector` now flags stale `.claude/worktrees/*`; `test_work_tree_stray_detector.py` asserts a stale worktree dir is detected |
| `GOV-STANDING-BACKLOG-001` | WI-3394 closed not-reproducing with `git cat-file -e` exit-0 evidence |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest` for the extended `stray_detector`; `git fsck` clean post-gc |

Commands (at verification): `git count-objects -vH` (before/after), `git lfs ls-files`,
`git worktree list`, `git fsck`, `pytest platform_tests/scripts/test_work_tree_stray_detector.py`,
`ruff check`/`ruff format --check` on changed `.py`.

## Acceptance Criteria

1. `.git` LFS cache pruned (size down ~4.76 GB), stray `*.index` + `.git/cursor` gone,
   `git gc` run, `git fsck` clean.
2. All 12 `.claude/worktrees/` copies verified free of stranded work and deleted;
   `git worktree prune` clean; `stray_detector` scope + test extended.
3. The three root DB artifacts deleted.
4. WI-3394 closed not-reproducing with cited evidence.

## Risk and Rollback

- **Risk:** a worktree holds stranded uncommitted work → mitigated by the
  mandatory per-dir `git status`/unpushed check + draft archival before deletion.
- **Risk:** `git gc`/`lfs prune` corruption → `.git/` is `.driveignore`-excluded
  (no Drive race), the 4 LFS objects are verified unreachable, `gc` is standard;
  reachable objects are recoverable from `origin` if ever needed.
- **Risk:** deleting DB artifacts → gitignored dead copies, canonical DB healthy,
  no rollback needed; FAB-03 (sanctioned backup) supersedes the ad-hoc-copy habit.

## Recommended Implementation Routing

**NOT a cheap-local-model candidate.** Destructive + repository-state + irreversible
(git gc, file deletion, verify-before-delete judgment). Per the tiered routing this
is the high-risk tier — reserve for Claude/Codex-supervised execution or careful
owner-run. The verify-before-delete step on each worktree requires judgment a 14B
local model should not exercise unsupervised.

## Recommended Commit Type

`chore:` — storage maintenance (git gc/prune, residue deletion, WI closure) with a
small `feat:`-class `stray_detector` scope extension.
