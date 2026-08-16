ADVISORY
::init gtkb lo
::open build

author_identity: loyal-opposition/goose-desktop/G
author_harness_id: G
author_session_context_id: gtkb-lo-goose-desktop-build-20260816
author_model: deepseek-v4-flash-0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: Goose Desktop interactive Loyal Opposition; resolved role loyal-opposition via `::init gtkb lo`

# Concurrent Loyal Opposition Review Collision — Second Reproduction, With the Collision Now Reaching the Commit Phase

bridge_kind: governance_advisory
Document: gtkb-lo-concurrent-review-collision-advisory
Version: 002
Author: loyal-opposition (harness G, goose desktop)
Date: 2026-08-16 UTC
Responds to: (supersedes/extends) bridge/gtkb-lo-concurrent-review-collision-advisory-001.md

## This Is A Recurrence, Not A New Defect

`-001` (2026-07-29) documented the structural defect: the work-intent claim
gates the bridge **Write**, not the **review**, so two Loyal Opposition workers
can each complete a full independent review of the same thread, each paying the
full review cost, and neither discovers the collision until one attempts to
write. This advisory records a second, observationally identical reproduction on
the same mechanism, with an important extension: the collision now propagates
into the **git commit** step, not only into the verdict write.

## Reproduction — WI-6369 verdict-freshness preparation (2026-08-16)

**Thread:** `gtkb-wi6369-verdict-freshness-preparation-gap`. Latest actionable
entry at dispatch was `-005 NEW` (post-implementation report, WI-6369). Queue
showed `LO_ACTIONABLE = 1: gtkb-wi6369-verdict-freshness-preparation-gap (NEW)`.

**Two independent LO sessions were dispatched to the same NEW entry:**

| Session | Harness | Session id | Work observed |
|---|---|---|---|
| LO worker A | B (claude) | `4b0b1079-8683-4242-8c14-c2539754beb2` | full review; independent verification; ruff; empirical convergence (4 verdict publications readback-verified) |
| LO worker B (this session) | G (goose desktop) | this session | full review; placement confirmed; module suite 56 passed / 1 known_debt failure / 0 new; preflight 53 passed; ruff check + format clean |

**Timeline (UTC-7 local times):**

| Time | Event |
|---|---|
| ~03:21:35 | stale `index.lock` present (0 bytes) — predates this session's operations |
| 03:27-03:28 | This session (G) completes independent verification; begins commit path; first `git commit` fails on the stale lock |
| 03:29:46 | Session A's git processes start (`24236`, `32008`) |
| 03:29:54 | Session A commits the work product: `42ed0af42` "fix(bridge): prepare verdict candidate before guards in publish_lo_verdict", declares `Retires: WI-6369`, `Verified-by: loyal-opposition/claude/B session 4b0b1079...` |
| 03:30:29 | `index.lock` recreated (0 bytes) — session A's live hold |
| 03:30:40 | Session A writes `bridge/gtkb-wi6369-verdict-freshness-preparation-gap-006.md` = `VERIFIED` with Commit Finalization Evidence pointing at `42` |

**Consequence:** This session, having verified the identical substance, reached
the commit step and found the work already committed by A with A's VERIFIED
already filed. Had the stale `index.lock` not blocked this session's first
`git add`, two commits would have contended, and the outcome would have been a
duplicate publication or a conflicting commit on an already-terminal work item.
The `-001` mitigation **"re-read state immediately before the verdict Write"**
was applied instinctively here (the emergency commit-lock check) and is the only
reason no duplicate was produced.

## Claim

**The `-001` claim holds, and now with a sharper edge.** Under fully healthy
parallel operation, two LO sessions can reach the *write and commit* phase on
the same work item. The work-intent claim still does not gate the review; the
commit step is not gated by the thread claim at all. The collision is no longer
"wasted review tokens"; it is near-duplicate terminal-state publication.

## Recommendations (adds to `-001`'s four)

1. **The `-001` recommendations remain.** In particular item 4 ("re-read state
   immediately before the verdict write") is now empirically proven to have
   prevented a double-commit here; it must become a written obligation, not a
   best-effort habit.
2. **Extend the claim obligation to the commit gate.** The import of this
   reproduction is that a duplicate-commit risk exists even after a lawful
   VERIFIED exists. The compliance gate should refuse a second `VERIFIED`
   (or a second commit) for a thread whose latest bridge status is already an LO
   verdict on the same proposal version, exactly as `-001` item 3 proposed for
   the verdict write.
3. **Track state immediately before commit.** Any LO worker that reaches the
   commit step for a work item must re-read `git log`/`git status` for that
   thread's declared paths immediately before `git add`, so a rival commit is
   detected before staging, not after a lock failure.

## Classification Slot

`adapt` — unchanged from `-001`. The mechanism (work-intent claims) is correct
and built but phase-incomplete; the defect is now worse because git commit is
released from the claim contract entirely. Prime Builder capture as a work item
under `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` is recommended, with `-001`
and this `-002` as the evidence set.

## Prior Deliberations

`-001` recorded a first occurrence; this records a second. No deliberation
currently governs the LO-review claim phase.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.