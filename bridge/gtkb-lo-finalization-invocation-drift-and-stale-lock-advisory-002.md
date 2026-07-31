ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 84f97bc5-39a5-4126-bfa9-5afd34d25a63
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled loyal-opposition-worker; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# Stale index.lock Recurred Within the Same Session — Evidence Points to a Leak in the Bridge Write Path, Not an Occasional Crash

bridge_kind: governance_advisory
Document: gtkb-lo-finalization-invocation-drift-and-stale-lock-advisory
Version: 002
Author: loyal-opposition/claude (harness B, session 84f97bc5-39a5-4126-bfa9-5afd34d25a63)
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-lo-finalization-invocation-drift-and-stale-lock-advisory-001.md

## Source

Observed after filing version 001 of this advisory, in the same scheduled
`loyal-opposition-worker` run. Version 001 recorded claim C2, a stale
`.git/index.lock` blocking finalization with no detector, and recommended a
doctor check for it.

That recommendation is now insufficient on its own. A second stale lock appeared
during this session, which changes the probable cause and therefore the fix. This
version records the new evidence and revises the C2 recommendation. Everything
else in version 001 stands unchanged.

## Claim

### C2-revised - P1: the stale lock recurs within minutes and correlates with the bridge write path

Two distinct stale locks were observed in one session, roughly three hours apart:

| Observation | Created | Size | Live `git` process | Age when found |
| --- | --- | --- | --- | --- |
| First | `2026-07-29T13:14:57Z` | 0 bytes | none | about 2h47m |
| Second | `2026-07-29T16:31:31Z` | 0 bytes | none | about 4m |

The first predated this reviewer session, which opened at `15:35:45Z`, so its
origin is unknown. The second is the informative one. It was created at
`16:31:31Z`, inside the window in which this session was publishing bridge
verdicts through `scripts.gtkb_bridge_writer.write_bridge_file`, and it was
found four minutes later with no `git` process alive on the host.

Both were removed under standing Loyal Opposition bridge-repair authority, and
`git status` and `git log` were confirmed healthy after each removal.

### What this changes

Version 001 framed C2 as an environmental hazard: a lock left behind by some
crashed process, needing detection. The second observation does not fit that
framing well. A zero-byte lock appearing during normal, successful bridge-write
activity, with every write returning exit 0 and no process left running, is more
consistent with a lock leak in the write path than with an external crash.

If that is right, a doctor check alone treats the symptom. Every session would
keep finding and clearing locks, and any session that does not know to look would
silently fail every finalization it attempts, which is exactly the recurring
class version 001 documents across WI-4682, WI-4723, WI-5345, and WI-5688.

### Confidence

Correlation is strong; causation is not proven. I did not instrument
`write_bridge_file` or bisect its git invocations, because doing so is
implementation work outside Loyal Opposition scope and outside this run's
authorization. What is established:

- two zero-byte locks, no live `git` process for either;
- the second created inside the bridge-write window of this session;
- all bridge writes in that window returned exit 0, so no write reported failure;
- read-only git commands continued to work throughout, which is why the condition
  is invisible until something needs the index.

What is not established: which specific git invocation inside the write path
leaves the lock, or whether an unrelated concurrent process is responsible.
Prime Builder should determine that before choosing a fix.

## Owner Decision Needed

None additional beyond the two decisions already recorded in version 001. The
scope question there now carries more weight: C1 and C2 were proposed as the
cheap pair, and C2 has grown from a doctor check into a defect investigation.

## Recommended Prime Action

Supersedes the C2 recommendation in version 001. Do both, in this order:

1. Investigate the leak first. Instrument or audit the git invocations in
   `scripts/gtkb_bridge_writer.py` and the disposable-index handling in
   `.claude/skills/gtkb-verify/helpers/write_verdict.py` for a path that creates
   `.git/index.lock` and returns without releasing it, including on the success
   path. The `_set_real_index_entries` and disposable-index restore logic are the
   natural first place to look, since that is where this session's first
   finalization attempt failed.
2. Keep the detector, but treat it as a backstop rather than the fix. A doctor
   check for a zero-byte `.git/index.lock` with no live `git` process beyond a
   short threshold remains worth having, because it converts a silent
   session-wide outage into a visible startup finding.

Do not treat this advisory as implementation approval. It is future-work
initiation only.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes. Item 1 is a defect investigation in the bridge write path and may lead to a
source change in `gtkb_bridge_writer.py` or `write_verdict.py`. Item 2 adds a
doctor check.

### Grill-the-owner questions

Prime Builder must obtain durable `AskUserQuestion` answers to:

1. Sequencing. Should the detector ship immediately as a standalone quick fix
   while the leak investigation proceeds, or should both land together? Shipping
   the detector first makes the condition visible during the investigation, at
   the cost of two bridge cycles instead of one.
2. Scope boundary. If the investigation finds the leak is in the shared git
   helper used by both the writer and the finalizer, the fix touches the
   finalization path that WI-5688 is currently recovering. Should this work wait
   for the WI-5688 recovery to reach terminal state first, to avoid two threads
   mutating the same surface?

### Required durable owner decisions

Before any derived implementation proposal is filed:

- the sequencing decision from question 1;
- the ordering decision from question 2, since it constrains whether this work
  may proceed concurrently with the WI-5688 recovery.

## Classification Slot

`adopt`.

The evidence is direct and reproducible within a single session, and the
condition silently disables the entire VERIFIED finalization path repository-wide
while every command still reports success. Recommended disposition is adopt, with
the leak investigation preceding the detector.

## Evidence Commands

```text
Get-Item .git\index.lock
Get-Process -Name git
git status --porcelain
git log --oneline -1
Test-Path .git\index.lock
```

Both locks were zero bytes with no live `git` process. After each removal,
`git status --porcelain` and `git log --oneline -1` returned normally, and HEAD
remained `e9052e9c4`.

## Owner Action Required

None to record this advisory. See Owner Decision Needed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
