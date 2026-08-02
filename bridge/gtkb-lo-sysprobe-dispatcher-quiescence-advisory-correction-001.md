ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 469b6155-827b-44cb-a56d-f838893bffa3
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task system-statusprogress-check; resolved role loyal-opposition

bridge_kind: governance_advisory
Document: gtkb-lo-sysprobe-dispatcher-quiescence-advisory-correction
Version: 001
Author: Loyal Opposition (claude, harness B)
Date: 2026-08-01 UTC

## Source

Scheduled system status/progress probe (system-statusprogress-check), 2026-08-01,
session context 469b6155-827b-44cb-a56d-f838893bffa3. This advisory CORRECTS a
live advisory filed by the previous run of the same scheduled task.

## Claim

gtkb-lo-sysprobe-dispatcher-outage-lo-queue-stall-001.md (2026-07-31) asks the
owner to decide whether the ~12-day dispatcher outage is intentional or a fault.
That question was already answered by owner decision
DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO, captured 2026-07-24T22:47:18Z -
three days BEFORE that advisory was filed. The advisory states it "cannot rule
out an out-of-band owner decision"; the decision was in the Deliberation Archive
and a semantic search would have surfaced it. Acting on that advisory as written
would restore a dispatcher the owner deliberately stopped.

## Evidence

DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO, source_type=owner_conversation,
outcome=owner_decision, session 932aad8d-99df-440f-82e5-b1e122e5eb0f, states:

- "The TAFE dispatcher is deliberately quiesced. Loyal Opposition review and
  verification are processed manually by owner routing, not by automated
  dispatch. This is an intentional operating posture, not an outage."
- "Do NOT diagnose the dispatcher health WARN as a defect, and do NOT propose or
  perform dispatcher repair work on the strength of it."
- "Do NOT re-enable the dispatcher daemon, restore retired pollers, or introduce
  any substitute automated dispatch substrate. Re-enablement requires a fresh
  explicit owner directive."
- "A backlog of latest-GO bridge threads awaiting verification is the EXPECTED
  consequence of manual processing. It is a queue awaiting owner routing, not
  evidence of breakage."

The decision explicitly names the same evidence the 2026-07-31 advisory cites as
alarming: the 2026-07-19T20:52:37Z heartbeat, the health WARN, and the
loyal-opposition:D subprocess_execution_failed run, which it classifies as "stale
residue, not a live failure".

Confirmed unchanged at 2026-08-01: daemon Running=False, heartbeat age
1,073,386 s, GTKB-DispatcherDaemon task Disabled, health WARN with the identical
loyal-opposition:D finding.

## What The Prior Advisory Got RIGHT And Should Be Preserved

Item 5 of its Recommended Prime Action - the disposition of GTKB-DbSnapshot - is
NOT covered by the quiescence decision. That decision addresses the dispatcher
only. GTKB-DbSnapshot Disabled is a separate, live DR gap; this session measured
the newest snapshot at 200h old against a 48h doctor threshold and filed WI-5856.
Its item 4 (test traffic in the production dispatch-failure log) and item 2 (the
stale .git/index.lock, WI-5819) are also unaffected by the quiescence decision.

## Risk / Impact

- A Prime Builder session converting the 2026-07-31 advisory into work could
  re-enable the dispatcher against an explicit standing owner directive.
- The prior advisory records "operator quiesce: expired" as evidence that the
  outage was unauthorized. The runtime quiesce record and the owner decision are
  different surfaces; an expired runtime record does not revoke a captured owner
  decision. Any future check that infers authorization from operator-quiesce
  state alone will keep producing this false positive.
- Both 2026-07-31 sysprobe advisories carry an unfilled Prior Deliberations
  placeholder reading "_No prior deliberations: <fill in reason before filing>._".
  That is the proximate mechanism of this error: the mandatory pre-filing
  deliberation search was templated but not performed.

## Owner Decision Needed

None. This advisory records an existing owner decision; it does not seek a new
one. If the owner now WANTS the dispatcher restored, that requires a fresh
explicit directive per the cited decision.

## Recommended Prime Action

1. Do not action the dispatcher-restoration items (1 and 6) of
   gtkb-lo-sysprobe-dispatcher-outage-lo-queue-stall-001.md. Dispose of that
   advisory as superseded-in-part, citing this correction.
2. Carve out its still-live items - GTKB-DbSnapshot disposition (WI-5856), the
   stale .git/index.lock (WI-5819), and test traffic polluting
   dispatch-failures.jsonl - into their own work rather than discarding the
   advisory wholesale.
3. Consider a mechanical guard: any advisory whose Prior Deliberations section
   still contains the literal placeholder "<fill in reason before filing>" should
   fail the bridge compliance gate. This defect was cheap to prevent and
   expensive to catch.
4. Consider surfacing DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO in the
   dispatcher health output itself, so the WARN carries its own authorization
   context.

## Prior Deliberations

- DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO - the owner decision this
  advisory restores to view. Primary authority.
- DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD - prior dispatcher
  hold, cited by the quiescence decision as consistent posture.
- DELIB-HARNESS-HEARTBEAT-SCOPE-20260701 - heartbeat state applies only to
  dispatchable harnesses; relevant to reading the stale heartbeat correctly.

## Classification Slot

adapt.

This advisory is not implementation approval. It does not authorize protected
edits, does not open an implementation-start packet, and does not bypass the
Prime Builder proposal, Loyal Opposition GO, or verification gates.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
