ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 469b6155-827b-44cb-a56d-f838893bffa3
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task system-statusprogress-check; resolved role loyal-opposition

bridge_kind: governance_advisory
Document: gtkb-lo-sysprobe-dispatcher-next-stale-blocker-narrative
Version: 001
Author: Loyal Opposition (claude, harness B)
Date: 2026-08-01 UTC

## Source

Scheduled system status/progress probe (system-statusprogress-check), 2026-08-01,
session context 469b6155-827b-44cb-a56d-f838893bffa3. Evidence from MemBase
current_work_items and projects tables.

## Claim

WI-5617 status_detail states the Dispatcher Next foundation spike is
non-executable because its parent project is retired. The parent project was
reactivated to status=active on 2026-07-31, one day before this probe. The
work-item narrative still asserts the resolved blocker, and a session reading
status_detail as current state would mis-scope or skip the work.

## Evidence

projects table, name "GT-KB Dispatcher Next Control Plane":

| version | status | changed_at |
| --- | --- | --- |
| v1 | active | 2026-07-19T03:20:25Z |
| v2 | retired | 2026-07-24T08:08:36Z |
| v3 | active | 2026-07-31T03:12:01Z |

WI-5617 status_detail (current): "Current typed bridge state is NO-GO v010 after
Prime NO-ACTION v009. GO v008 is non-executable because parent
PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE is retired, its legacy PAUTH cannot be
widened into current whole-project authority, and the accepted six-target
verification cohort has drifted because
groundtruth-kb/requirements-dispatcher-next-spike.txt is absent."

The first cited blocker is stale as of v3. This probe did NOT re-verify the second
(legacy PAUTH widening) or third (missing requirements file) blockers; they may
still hold. Only the retirement claim is falsified.

Program state: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE has 13 work items, 12
open, WI-5617 through WI-5624 all P0. Every backing table is empty - dispatch_lanes,
dispatch_events, dispatch_lane_matrix, dispatch_lane_projection_snapshots,
dispatch_lane_score_dimensions, dispatch_lane_score_snapshots,
dispatch_lane_scoring_evidence, dispatch_default_metric_events,
dispatch_default_metrics_snapshots: 0 rows each. Schema landed; no producer runs.
WI-5284 (live dispatch metrics producer) sits at NO-ACTION.

## Risk / Impact

- Narrative state ages independently of the records it describes. A P0 program
  can appear blocked when its blocker is gone.
- This is a general class, not a one-off: any status_detail that names a
  lifecycle state of another artifact becomes a stale mirror of that artifact.
- Dispatcher Next is the designated successor to the currently-quiesced dispatcher
  (DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO). A falsely-blocked successor
  program while the incumbent is deliberately stopped leaves no active dispatch
  path at all.

## Owner Decision Needed

None to file this advisory. Whether to resume the Dispatcher Next program is an
owner priority decision and should be raised via AskUserQuestion separately.

## Recommended Prime Action

1. Re-verify WI-5617 remaining two blockers (legacy PAUTH widening; presence of
   groundtruth-kb/requirements-dispatcher-next-spike.txt) and refresh
   status_detail to current fact.
2. Sweep the other 11 open Dispatcher Next work items for status_detail that
   cites the same retirement.
3. Consider whether status_detail should cite another artifact lifecycle state at
   all, versus referencing it by id so the reader resolves it live. This is the
   durable fix for the class.
4. Confirm whether the empty dispatch_* tables are expected pre-implementation
   state or an unlanded producer, and reconcile with WI-5284.

## Prior Deliberations

- DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO - establishes the incumbent
  dispatcher is deliberately stopped, which raises the cost of a falsely-blocked
  successor program.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 - state claims must derive from fresh
  canonical reads; a status_detail mirror of another artifact lifecycle state is
  the anti-pattern that governance names.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 and DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 -
  explicit lifecycle states must be preserved so durable memory does not become
  stale clutter.

## Classification Slot

adapt.

This advisory is not implementation approval. It does not authorize protected
edits, does not open an implementation-start packet, and does not bypass the
Prime Builder proposal, Loyal Opposition GO, or verification gates.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
