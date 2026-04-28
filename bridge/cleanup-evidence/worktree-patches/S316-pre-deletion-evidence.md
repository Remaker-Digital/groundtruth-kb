# S316 Pre-Deletion Evidence — 2 Outside-Root Worktrees

**Date:** 2026-04-27
**Context:** Owner directive to delete all of `E:\` except `E:\GT-KB`. This file
captures forensic evidence for the 2 outside-root git worktrees being
decommissioned, in compliance with `.claude/rules/project-root-boundary.md` and
the cleanup-manifest protocol.

## Worktrees (per `git worktree list` from `E:\GT-KB`)

| Worktree path | Branch | Tip commit | Pushed to origin? | Working tree state |
|---|---|---|---|---|
| `E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-e1-apply` | `e1-apply` | `f7da3080d6e8ff705e647c9e1d0c0a39643c1e91` | NO (push pending S316) | `A groundtruth.db` (uncommitted) |
| `E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-gtkb-current-main-integration` | `codex/gtkb-current-main-integration` | `6f48a3f84645351dea247561a7f9f3af62eb2879` | NO (push pending S316) | `A groundtruth.db` (uncommitted) |

## Commits not in `develop` (preserved via push to origin)

### `e1-apply` branch (6 commits)

```
f7da3080 e1-apply: scope bytecode ignore under tracked skill subtrees
7c256595 gt: upgrade receipt for c39c1a7da6
c39c1a7d gt: merge upgrade payload to 0.6.1
13cb44b1 gt: upgrade payload to 0.6.1
fe14c554 e1-apply: adopt-overwrite 6 A2 files from GT-KB v0.6.1 templates
c90e4e8e e1-apply: expand .gitignore !-negation for Tier A governance artifacts + tracked receipts
```

### `codex/gtkb-current-main-integration` branch (3 commits)

```
6f48a3f8 gt: track canonical terminology config
a91ece5f gt: merge upgrade payload to 0.6.1
66a2a746 gt: upgrade payload to 0.6.1
```

## Uncommitted `groundtruth.db` evidence (will be discarded)

| Worktree | Path | Size | Last write | SHA256 |
|---|---|---|---|---|
| e1-apply | `agent-red-e1-apply/groundtruth.db` | 80,003,072 B (76 MB) | 2026-04-18T08:47 | `42229f378491fd95b2cd3e87adeae4ebb7eb79beffc5921d029c9070f6acc575` |
| gtkb-current-main-integration | `agent-red-gtkb-current-main-integration/groundtruth.db` | 152,305,664 B (145 MB) | 2026-04-22T02:10 | `6c0298c7b0e679e223c0b92fde20fe7a0a9c24d18f5ed700d8232cf5e21c59cb` |

**Canonical KB for comparison** (preserved):

| Path | Size | Last write | SHA256 |
|---|---|---|---|
| `E:\GT-KB\groundtruth.db` | 891,940,864 B (850 MB) | 2026-04-27T12:39 | `989024030a854a4e5b1ea334b8502274615746b0ad6b93b94edf7f6b77b3a1d6` |

The worktree KB files are older smaller snapshots superseded by the canonical
KB. All three SHA256s differ; the worktree KBs do not contain a superset of
the canonical KB content. Stale-snapshot disposition is appropriate; no
content-recovery effort is warranted.

## Disposition (S316 actions)

1. **Push branches to origin** — durability beyond local `.git/objects` (owner
   pre-authorized 2026-04-27).
2. **`git worktree remove --force <path>`** for each worktree — discards working
   tree files and the uncommitted `groundtruth.db` adds; preserves branch refs
   and commits in `E:\GT-KB\.git\`.
3. **`git worktree prune`** — clean the `.git/worktrees/<name>/` metadata
   directories.
4. **`git fsck`** from `E:\GT-KB` — confirm object store integrity post-cleanup.

After step 2, the only remaining git worktrees from `E:\GT-KB` are:
- `E:/GT-KB` (in-root, canonical)
- `C:/Users/micha/.codex/worktrees/claude-design-backlog` (user-home, on C: drive — unaffected by E: deletion)
- `C:/Users/micha/AppData/Local/Temp/gh-dep2` (temp, on C: drive — unaffected by E: deletion)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
