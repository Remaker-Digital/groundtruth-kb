---
name: Prime Builder must not operate from stale worktrees
description: Worktrees on branches significantly behind develop give Prime a stale bridge view while Codex sees canonical develop; diverging views cause confusion and block owner navigation.
type: feedback
originSessionId: 0c948de7-b81e-4eaf-91c9-1d7e28239183
---
Prime Builder must not do real work from a `.claude/worktrees/<name>` worktree whose branch is more than a session or two behind `develop`. If the working directory is inside `.claude/worktrees/`, check at session start whether the worktree branch is materially behind develop. If so, recommend teardown or migration to develop before proposing or implementing.

**Why:** S307 incident. Session started in worktree `dazzling-haslett-99225e` on branch `claude/dazzling-haslett-99225e`, 48 commits behind develop. Prime saw a 7-entry `bridge/INDEX.md` snapshot from S306. Codex (Loyal Opposition, on develop in main repo) saw the live 20-entry index with REVISED `gtkb-root-directory-migration-post-verify-014.md` as the actionable. Owner trying to switch the main checkout to my branch hit `fatal: '<branch>' is already used by worktree at '<path>'` because my worktree was holding the lock — making my stale view actively block their normal navigation. Two confusions stacked: (a) Prime's view of bridge state was wrong, (b) Prime's existence in the worktree blocked the owner's intended workflow. Same shape as S304 OS-poller drift: silent divergence between two "truth" surfaces.

**How to apply:** At session start, if `pwd` matches `*.claude/worktrees/*`, run `git -C <main-repo> log <worktree-branch>..develop --oneline | wc -l`. If the count exceeds ~5, surface this in the orientation block and propose teardown via `git worktree remove --force <path>` before doing any bridge or implementation work. Do not propose "fix worktree visibility" patches as a first move — they treat the symptom. The structural answer is: canonical bridge work happens on develop in the main repo, not in stale worktree branches.
