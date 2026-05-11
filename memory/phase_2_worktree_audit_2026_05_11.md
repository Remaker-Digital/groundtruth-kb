---
name: Phase 2 worktree-cleanup audit (S341 hygiene plan re-scope)
description: Inventory of 39 local claude/* branches; 37 unmerged with 633-780 unique commits each; bulk cleanup is unsafe
type: project
---

# Phase 2 Hygiene Plan — Re-Scope

**Session:** S341 (2026-05-11)
**Origin:** Hygiene Plan Phase 2 ("worktree cleanup; 37 abandoned claude/* branches")
**Verdict:** Audit-agent's "abandoned" claim was wrong. Re-scope required before any deletion.

## Inventory

- **Total local `claude/*` branches:** 39
- **Merged into develop (safe to delete):** 2
- **Unmerged (have unique commits; NOT safe to bulk-delete):** 37
- **Remote `claude/*` refs:** 1 (`origin/claude/s333-audit-remediation`, merged into develop; safe to delete)

## Unique-commit distribution (sample of 10)

| Branch | Commits ahead of develop | Commit SHA |
|---|---|---|
| `claude/adoring-einstein` | 633 | `b1990241` |
| `claude/amazing-lehmann-1ac129` | 780 | `8f97aaf2` |
| `claude/blissful-leakey-9e636a` | 773 | `1656e488` |
| `claude/charming-ellis-a02aa8` | 633 | `b1990241` |
| `claude/compassionate-edison` | 633 | `b1990241` |
| `claude/dazzling-banzai-9ccb4c` | 769 | `b4441c67` |
| `claude/dazzling-buck-69ab6e` | 780 | `8f97aaf2` |
| `claude/dazzling-haslett-99225e` | 780 | `8f97aaf2` |
| `claude/determined-wing-837a24` | 780 | `8f97aaf2` |
| `claude/dreamy-faraday-534a8e` | 780 | `8f97aaf2` |

Note: many branches share SHA tips (e.g., 5 branches at `b1990241`; many at `8f97aaf2`). These appear to be Claude Code worktree branches created from a few common ancestors (probably old develop checkpoints). They accumulated independent work over many sessions and were never merged back.

## Why bulk-delete is unsafe

Each unmerged branch has 633-780 commits that are NOT in develop. Deleting them would lose that work irreversibly (no remote backup for local-only branches).

## Re-scope recommendation

Phase 2 changes from "delete 37 abandoned branches" to "per-branch audit and disposition":

1. **For each of the 37 unmerged branches**, run `git log develop..<branch>` and inspect commit messages. Classify each branch as:
   - **Redundant with develop** (work was redone later) → safe to delete after explicit owner OK.
   - **Holds unique value** (e.g., abandoned but interesting design exploration) → tag the tip commit and then delete.
   - **Active intent** (genuinely WIP that should be merged) → file a bridge proposal to bring the work into develop.

2. **Sample-audit first:** pick 3-5 branches and do the classification to estimate per-branch effort.

3. **Only after sample-audit**, file a separate bridge thread (e.g., `gtkb-worktree-branch-cleanup-001`) that proposes:
   - The classification methodology.
   - A batched disposition plan (e.g., "delete 25 redundant branches; tag-and-delete 8; preserve 4 for follow-on bridges").
   - The owner-approval gate for the deletions.

4. **The 1 remote `claude/s333-audit-remediation`** is safe to delete (merged into develop). Can be done in a small standalone PR; doesn't need a bridge thread.

## Lessons captured

- The audit-agent's "abandoned 37 branches" claim was based on naming conventions (`claude/<adjective>-<noun>`) rather than git-history inspection. Always probe live merge status before recommending destructive cleanup.
- Claude Code's worktree-branch lifecycle has no clean exit. Each session creates a worktree branch and accumulates commits; without an explicit merge-back step, branches drift forever. A future hygiene proposal should specify what "wrap-up" looks like for worktree branches (the analog of `kb-session-wrap` for the git branch surface).

## Disposition for this session

Phase 2 re-scope deferred to a separate bridge thread. No deletions executed in S341.
