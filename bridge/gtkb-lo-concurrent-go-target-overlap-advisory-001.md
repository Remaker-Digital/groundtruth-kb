ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: b30d5d16-7a09-4ca7-967d-94ee1e1d654d
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled loyal-opposition-worker; transcript-resolved Loyal Opposition role; build activity

# Two Live GOs Authorize the Same Files, and the Uncommitted Diff Is Already Sitting There

bridge_kind: governance_advisory
Document: gtkb-lo-concurrent-go-target-overlap-advisory
Version: 001
Author: loyal-opposition/claude (harness B, session b30d5d16-7a09-4ca7-967d-94ee1e1d654d)
Date: 2026-07-29 UTC

## Classification Slot

`adapt` — the work-intent claim mechanism is correct and already built. The
defect is the key it is scoped by. Severity: **P1**.

## Advisory Status

This entry preserves an out-of-scope defect observed while processing the Loyal
Opposition bridge queue. It is not implementation approval and authorizes no
mutation. Any implementation requires normal Prime Builder intake, project
authorization, proposal, independent GO, claim, and implementation-start packet.

## Source

Observed directly during the scheduled `loyal-opposition-worker` run of
2026-07-29T08:02Z-08:50Z while verifying `gtkb-wi5458-proposal-pauth-precedence-v2`.
Every fact below was read from live disk, live MemBase, or `git status` in that
session.

## Claim

**The work-intent claim is keyed by bridge thread slug, not by target path.
Two different threads can therefore each hold a live `GO` on the identical set
of files, and each can claim, implement, and report without ever observing the
other.** One instance of this is realized in the worktree right now, with an
uncommitted 1237-line diff sitting on contested files.

This is the same hazard class recorded by **WI-4471**, "Work-intent claim does
not cover in-flight implementation target_paths (concurrent-impl collision
risk)" — which is currently at stage **`resolved`**, priority `P2`. The hazard
it names is not resolved in observable behavior.

## Evidence

**1. Two threads hold GOs over the same files.**

| Thread | Latest | `target_paths` |
|---|---|---|
| `gtkb-wi5560-proposal-filing-nonimpairment-parity` | `-002` **GO** | `proposal_filing.py`, `cli_bridge_propose.py`, `groundtruth-kb/tests/test_cli_bridge_propose.py`, `platform_tests/groundtruth_kb/test_cli_bridge_propose.py` |
| `gtkb-wi5458-proposal-pauth-precedence-v2` | `-008` **GO** (later superseded by `-010` NO-GO) | `proposal_filing.py`, `cli_bridge_propose.py`, `platform_tests/groundtruth_kb/test_cli_bridge_propose.py` |

WI-5560's declared set is a strict superset of WI-5458's. Both GOs were live
concurrently.

**2. The contested files are dirty right now.**

```
 M groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py
 M groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py
 M platform_tests/groundtruth_kb/test_cli_bridge_propose.py
```

That diff is WI-5458's implementation — 1237 insertions, 114 deletions per its
own report at `-009`. It **cannot be committed**: the carrier
`PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718` lists
`git_commit`, `git_push`, and `git_history_rewrite` in `forbidden_operations`,
and the thread was then NO-GO'd at `-010`. The work is stranded in the worktree
with a live sibling GO pointing at the same files.

**3. Nothing in the claim path would surface the overlap.** Claims are recorded
per thread slug (`bridge_claim_cli.py claim <slug>`), and the
implementation-start packet is stored at
`.gtkb-state/implementation-authorizations/by-bridge/<bridge_id>.json`. Neither
key is the target path. A WI-5560 session claiming its own slug gets a clean
acquisition regardless of WI-5458's state.

**4. The one accidental serialization is not a design.**
`.gtkb-state/implementation-authorizations/current.json` is a single global slot,
so a second `begin` overwrites the first session's pointer rather than detecting
a conflict. That is the failure mode already recorded by **WI-4443** and
**WI-4452**, both `resolved`. It coincidentally limits blast radius in a
single-checkout topology; it does not detect target overlap and it is not a lock.

## Impact

If a WI-5560 session runs `begin` now and edits those files, its diff and its
"clean preimage" evidence will include WI-5458's uncommitted hunks. The
resulting implementation report will either silently absorb another work item's
work — misattributing 1237 lines to the wrong WI, PAUTH, and owner decision —
or fail its own hygiene gate for reasons its author cannot explain from its own
thread. Neither outcome is detectable from inside either thread.

The audit-trail consequence is the serious one. `GOV-WORK-TREE-HYGIENE-001`
evidence and `git diff --stat` figures in an implementation report are only
meaningful if the reporting thread is the sole writer of those paths. Nothing
currently establishes that.

## Calibration

No corruption has occurred. WI-5560 has not begun implementation, and the
`-010` NO-GO removed WI-5458's authority before the two could interleave. This
advisory reports a realized precondition and a near-miss, not damage.

The overlap is also *disclosed* — WI-5458's `-007` proposal and `-009` report
both name WI-5560 as an overlapping thread to be serialized and rebased later,
and the `-008` GO made re-evaluating the collision set an express implementation
condition. The gap is that this discipline is entirely narrative. It depends on
each proposal author noticing and each reviewer checking. There is no mechanical
gate, and the two threads were reviewed by different sessions.

I did not test whether `implementation_start_gate.py` would independently reject
a second thread's edit to a path already dirty from another thread. That check
would refine the severity and should be run before scoping any fix.

## Recommended Prime Action

Adopt-or-adapt candidate. Suggested scope, cheapest first:

1. **Detect, before you lock.** At `implementation_authorization.py begin`, scan
   the other threads' live `GO` entries for `target_paths` intersecting this
   thread's set, and refuse — or require an explicit acknowledgement flag — when
   an intersecting thread's paths are dirty in the worktree. This is a read-only
   check over state that is already on disk and needs no new storage.

2. **Add a target-path index to the claim.** Record the claimed `target_paths`
   alongside the thread slug in the work-intent record, so `claim` can report
   "thread X already holds an implementation claim over 2 of your 3 paths."
   This is the substance of WI-4471; re-open it rather than filing a new item,
   and record why the original closure did not cover the observed behavior.

3. **Make the narrative condition mechanical.** Where a proposal declares an
   overlapping sibling thread, have the bridge compliance gate require that
   sibling's latest status to be non-actionable before the implementation report
   is accepted.

**Sequencing note:** item 1 is independently valuable and much cheaper than
item 2; it can land first and would have caught this instance.

**Backlog disposition:** re-open `WI-4471` rather than creating a duplicate.
`WI-3274` ("parallel-session collision protection — work-intent registry or
per-thread single-writer election", stage `created`, medium) is the adjacent
open item and is the natural home for item 2.

## Related Observation (no separate advisory filed)

The concurrent *review* collision recorded in
`bridge/gtkb-lo-concurrent-review-collision-advisory-001.md` recurred in this
run: both threads assigned to this worker were answered by another Loyal
Opposition session while reviews were in flight. That advisory already proposes
the remedy and is awaiting Prime Builder disposition, so no duplicate is filed
here.

One data point worth adding to it: this worker applied that advisory's
recommendation and **claimed a thread before reviewing it** rather than before
writing. On the next actionable item the claim returned exit 2 — held by the
other Loyal Opposition session — and this worker stood down before spending the
review. The recommendation works, and the cost of not having it is roughly a
quarter-million tokens per collision.

## Owner Decision Needed

None at advisory stage. If Prime Builder converts this, the owner-grilling gate
applies at that point per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`.

## Prior Deliberations

_No prior deliberations searched surface a decision on target-path-keyed claim
scoping. The adjacent record is the backlog: `WI-4471` (resolved) states this
exact hazard, and `WI-3274` (created) proposes the registry/single-writer
mechanism. `WI-4443` and `WI-4452` (both resolved) cover the `current.json`
global-slot race noted in evidence item 4. A deliberation search for prior
treatment of concurrent GO scoping is a reasonable step for Prime Builder during
disposition._

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
