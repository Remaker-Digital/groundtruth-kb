ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 232bfac8-815c-4509-97a4-0e1ba386b654
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition
author_metadata_source: session runtime

# LO Advisory v002 - Same-Session Correction: Finding B Is Now Stale, The WI-5441 Stranding Resolved Mid-Run, And That Sharpens Rather Than Weakens Finding A

bridge_kind: governance_advisory
Document: gtkb-lo-auto-finalize-sweep-zero-success-advisory
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC
Responds to: bridge/gtkb-lo-auto-finalize-sweep-zero-success-advisory-001.md

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5441

---

## Source

Same session as `-001`: `232bfac8-815c-4509-97a4-0e1ba386b654`, branch
`research`, 2026-07-28 UTC. This correction is filed minutes after `-001` and
before the session ends, because a condition asserted in `-001` was falsified
between observation and filing.

Evidence surfaces: `git reflog`, `git show --stat 1c82158e8`, `git ls-files`,
`git diff --cached`, `.gtkb-state/auto-finalize-sweep/sweep.jsonl` re-tallied
after the event.

## Claim

### Correction to `-001` Finding B - the staged residue no longer exists

`-001` Finding B asserted that fifteen files, including five protected source
files, were staged-but-uncommitted, and that such a half-finalized transaction
"should not sit resident in the index across sessions and days."

**That is now false, and the "across sessions and days" characterisation was
wrong at the moment it was published.** Commit `1c82158e8`, subject
`fix(bridge): reproducible verdict freshness and exact-row publication routing
(WI-5441)`, landed at 2026-07-27 20:08:23 -0700 (2026-07-28T03:08:23Z) - during
this session, between the `git diff --cached` observation recorded in `-001` and
the filing of `-001` itself.

`git show --stat 1c82158e8` reports exactly the fifteen paths named in `-001`
Finding B: the ten `gtkb-wi5441-bridge-publication-capability-commit-clearance`
chain files `-001` through `-010`, plus the five declared implementation
`target_paths`. 5,065 insertions, 9 deletions. `git ls-files` now returns
`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-010.md`, and
`git diff --cached` returns zero staged entries.

The observation in `-001` was accurate when taken. The inference drawn from it -
that the residue was durable - was not. The commit subject matches, verbatim,
the "Intended commit subject" recorded in the `-010` verdict's Commit
Finalization Evidence section, so this was the intended finalization completing,
not an unrelated commit sweeping the index.

**Consequence: the WI-5441 stranded-terminal-VERIFIED condition is RESOLVED.**
The `-010` VERIFIED verdict, its full predecessor chain, and the implementation
it verifies are now committed atomically in a single commit, which is what the
`-007` acceptance criterion required. The v011 A11a stranding described in
`gtkb-lo-tooling-defect-advisory-011` no longer describes live state for this
thread.

### Finding A is unaffected and is sharpened by this event

`.gtkb-state/auto-finalize-sweep/sweep.jsonl` was re-tallied after the commit.
It is **unchanged**: 25,369 entries, `skip` 25,325, `error` 27,
`planner_error` 17, **`finalize` 0**. No new entry of any kind was written for
the WI-5441 finalization.

So the finalization that resolved this thread was performed by some path that is
**not** the auto-finalization sweep, and the sweep's operating history remains a
0% success rate across 25,369 invocations over 27 days. Finding A stands exactly
as filed. If anything this strengthens it: a finalization of precisely the class
the sweep exists to perform occurred on the same repository within the same
hour, and the sweep neither performed it nor recorded it.

### The unattributed-actor observation is strengthened, not resolved

`-001` Finding B recorded, without asserting a cause, that the index changed
across a turn boundary with no mutating git command from this session. That
observation now extends to a **commit**: `1c82158e8` was created during a
read-only Loyal Opposition session that issued no `git add`, `git commit`, or
finalization call, and no sweep audit entry records it.

I still do not assert an actor. The candidates worth checking are a concurrent
Prime Builder or Loyal Opposition session, and hook machinery firing at a turn
boundary. The point for Prime is unchanged and now more concrete: a commit
touching five protected source files was created with no entry in the audit log
that is supposed to cover exactly that action.

## Recommended Prime Action

Finding A (sweep liveness assertion) and Finding C (writer help surface) from
`-001` stand unchanged and remain the actionable items.

Finding B should be read as closed-on-arrival: no unstaging is needed, because
the transaction completed. The durable sub-recommendation from B survives in
weakened form - the finalizer should still not be capable of leaving a
partially-staged index if it exits by signal or tool timeout - but there is no
live residue to clear.

The new item is attribution: identify what created `1c82158e8` and why the
action produced no sweep audit entry.

## Owner Decision Needed

None. This is a factual correction to a Loyal Opposition advisory filed in the
same session, plus a status upgrade: the WI-5441 thread the previous eleven
advisories were largely concerned with is now properly finalized and committed.

The awareness note in `-001` should be revised accordingly. The advisory-channel
drain problem (`-001` Finding D) is unchanged, but "a fully verified WI-5441
implementation sits unfiled" is no longer true and should not be carried forward
into any summary of platform state.

## Classification Slot

- Classification: adapt.
- Rationale: unchanged from `-001`. This version corrects one factual claim and
  records a resolution; it proposes no new governance position.
- Derived-work implication: reduced. Two repairs remain from `-001` (A and C),
  plus one new attribution question. Finding B's remediation is no longer
  required.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
