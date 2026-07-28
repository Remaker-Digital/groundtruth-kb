ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 931ea858-10a4-4933-ab18-678db95e9c6e
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_advisory
Document: gtkb-lo-wi5441-strand-correction-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

# LO Advisory - Same-Session Correction To gtkb-lo-wi5441-stranded-terminal-verified-advisory-001: The Strand Was Transient, Not Permanent. Fail-Closed Cleanup Worked. A1 Is Downgraded P0 To P2, And The Real Standing Blocker Is Packet Expiry

---

## Source

Same scheduled Loyal Opposition worker run and session context as `-001`
(`931ea858-10a4-4933-ab18-678db95e9c6e`), branch `research`, HEAD `1c82158e8`,
2026-07-28 UTC. Filed minutes after `-001`, correcting it before any reader acts
on it.

Correcting an own-filed advisory in the same run follows the precedent of
`bridge/gtkb-lo-auto-finalize-sweep-zero-success-advisory-002.md`.

---

## Claim

### C1 - correction to `-001` A1: the strand resolved itself; fail-closed cleanup succeeded

`-001` A1 asserted that WI-5441 rested at a published terminal `VERIFIED` with
no commit, and that the thread had permanently left the review queue. **That is
no longer true, and the permanence claim was wrong.**

Re-read at 07:31 UTC, roughly fifteen minutes after the observation in `-001`:

```
Test-Path bridge/gtkb-wi5441-global-registry-membership-reconciliation-012.md
  NO - removed

gt bridge show gtkb-wi5441-global-registry-membership-reconciliation --json --compact
  "latest_path":   "bridge/gtkb-wi5441-global-registry-membership-reconciliation-011.md",
  "latest_status": "REVISED",
  "version_count": 11

gt bridge state-report
  LO_ACTIONABLE_LATEST_NEW_REVISED_NO_ACTION | 1: gtkb-wi5441-global-registry-membership-reconciliation (REVISED at ...-011.md)

git log --oneline -1
  1c82158e8   (unmoved)
```

The `-012` artifact was removed, published state rolled back from `VERIFIED`
at `version_count: 12` to `REVISED` at `version_count: 11`, and the thread
returned to the Loyal Opposition queue. This is the documented fail-closed
contract behaving **correctly**: the helper removed the just-written verdict and
failed closed.

**What `-001` A1 got right, and what it got wrong.** It correctly captured, with
timestamps, that terminal state is published before the commit exists. It
incorrectly inferred permanence from a snapshot taken inside that window. The
correct reading is that `-001` observed the transaction mid-flight, not a
completed strand.

### C2 - the ordering defect is real but conditional, and this run bounds it

`bridge/gtkb-lo-tooling-defect-advisory-011.md` A11a reported a **permanent**
strand. This run shows the same ordering with a **clean** outcome. The two are
consistent, and together they bound the defect:

- The publish-before-commit ordering is confirmed on both runs.
- In-process fail-closed cleanup works whenever the helper survives to run it -
  demonstrated here.
- The permanent strand in v011 required the helper to be **killed** by a tool
  timeout, so cleanup never executed.

So the defect is not "every failed finalization strands." It is "a finalization
killed inside the publish-to-commit window strands, and nothing outside the dead
process will notice." That is a narrower and more actionable statement than
`-001` made, and it sharpens rather than weakens the case for recommendation 4
in `-001` (publish after commit): inverting the order removes the dependency on
a cleanup path that only runs when the process lives.

**Severity revision.** `-001` A1 is downgraded from **P0 to P2**. It is a
read-consistency defect, not a durable-corruption defect. A concurrent reader -
this run - observed `VERIFIED 1719` and `LO_ACTIONABLE 0` for work that was
never committed and that shortly reverted. Any automation sampling bridge state
in that window would act on a verdict that does not exist. That is worth fixing,
and it is not data loss.

### C3 - the real standing blocker is finalization failure plus packet expiry, not stranding

The finalization did not merely publish early. It **failed**, for the second
time on this thread (`-010` blocked on formatting; this attempt failed after the
formatting was fixed). The thread is LO-actionable again at `-011 REVISED`, and
the substantive work remains verified-correct and uncommitted.

The implementation-start packet measured during this run:

```
expires_at : 2026-07-28T07:33:36Z
checked at : 2026-07-28T07:31:19Z   -> 2.3 minutes remaining
```

Against a protected-commit gate measured at roughly thirteen minutes (v011 A11c,
taken after the WI-5658 performance fix), a two-minute residue is not a usable
window. `-001` A4 stands and is now reinforced by a second independent data
point: the packet clock starts at implementation time, so by the time an
independent reviewer has finished a real verification the window is gone.

This, not stranding, is why WI-5441 cannot close. Recommendation 5 in `-001`
(packet TTL that survives an independent verification cycle) is therefore the
item on the critical path for this thread, ahead of recommendation 4.

### C4 - findings unaffected by this correction

`-001` A2 is **unaffected and stands in full**. The independent verification of
`-011` - lint and format gates across all 29 declared Python paths, the two noqa
suppressions traced to HEAD, registry postimage and all four digests, both
journals chained with zero removals, the 2,032-row manifest reconciled with
`groundtruth.db` as the sole waiver-covered member, all seven test suites
reproducing their claimed counts, both baselines confirmed pre-existing, exact
scope accounting, and both mandatory preflights passing - was completed before
any of the state churn described here and does not depend on it.

Its operative conclusion is unchanged and is the most useful thing in either
version of this advisory: **WI-5441 needs a commit, not another review.** A
future session should not re-derive that result.

`-001` A3, A5, and A6 are unaffected. `-001` A4 is reinforced per C3.

---

## Owner Decision Needed

**Status:** unchanged in substance, improved in character. WI-5441 is not
corrupted and not silently dequeued; it is LO-actionable at `-011 REVISED` with
verified-correct, uncommitted work. WI-5640 Stage B remains paused.

**Decision / Question:** `-001` offered options A, B, and C on the assumption
that published state needed correcting. Option B is now **moot** - the state
corrected itself. The live question is narrower: should the next finalization
attempt be preceded by a packet-TTL fix (so the independent reviewer actually
has a usable window), or should a Prime Builder session simply refresh the
packet and finalize immediately within a fresh two-hour window?

**Needed from Mike:** a choice between those two, and the same yes/no as `-001`
on promoting the publish-after-commit ordering fix to implementation-approved
work.

**Why it matters:** two finalization attempts on this thread have now failed.
The second failed after its stated blocker was fixed, which indicates the
remaining obstacle is the finalization path itself rather than anything about
the implementation.

**Options:**

- **A-revised.** Prime Builder refreshes the packet and finalizes immediately,
  treating the fresh two-hour window as sufficient because no new review is
  needed. Fastest; relies on the finalization path working this time.
- **C-revised.** Fix the packet TTL for reviewer-side finalization
  (recommendation 5) first, then finalize. Slower; removes the recurring cause.

**Reply requested:** one option label, plus a yes/no on promoting the
publish-after-commit ordering fix.

This advisory requests no implementation authority and grants none.

---

## Recommended Prime Action

1. Treat `-001` A1 as corrected by C1 and C2 before acting on it. Do not attempt
   to "repair" published bridge state for WI-5441 - it is already correct at
   `-011 REVISED`, `version_count: 11`.
2. Carry `-001` A2 forward verbatim as reusable verification evidence. The
   implementation is verified-correct by two mutually independent reviewers. Do
   not re-run the reconciliation or either registry transaction.
3. Refresh the implementation-start packet, then create the finalization commit
   for the 32 declared paths plus a fresh terminal verdict, excluding
   `groundtruth.db` per the by-reference waiver.
4. Reprioritize `-001` recommendation 5 (packet TTL) ahead of recommendation 4
   (publish-after-commit ordering) for this thread specifically. Both remain
   worth doing; C3 shows 5 is the one blocking closure.
5. `-001` recommendations 6, 7, and 8 are unchanged.

**Verification expectation.** A packet-TTL fix should be provable by a test
asserting that a reviewer-side finalization commit succeeds against a packet
created outside the reviewer's own session window.

---

## Classification Slot

Recommended Prime Builder disposition: **adapt**, unchanged from `-001`.

The correction narrows scope rather than changing disposition: fewer items are
P0, the ordering fix is bounded to the helper-killed case, and the packet-TTL
item moves onto the critical path. Prime Builder disposition to be recorded on
intake, one of: adopt, adapt, reject, defer, monitor.

Readers must treat `-001` and `-002` as a single unit. `-001` A1 read alone
overstates severity and asserts a permanence that this version withdraws.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
