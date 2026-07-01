GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi4861-soft-reset-prune-stale-dispatch-runs
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4861-soft-reset-prune-stale-dispatch-runs-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4861
Recommended commit type: fix

## Separation Check

Proposal `-001` author session `d5a77c21-caee-404a-8fb3-6629ba276960` (harness B);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Review Summary

**GO.** Live code confirms `soft_reset` (~275–295) clears recipients/quiesce/guards/leases
but never prunes `dispatch-runs/` sidecars; stale dead-PID records can inflate live-worker
count. Proposed `_prune_stale_dispatch_runs` with preserve-live / dry-run semantics and
local PID probe (avoiding reverse import from trigger) is the minimal correct fix. Test
plan covers dead-PID, exited, live-preserved, and dry-run paths.

## Prior Deliberations

- DELIB-20266268 — owner AUQ authorizing daemon residue cleanup WIs.
- WI-4857 / WI-4805 — related lifecycle work; soft-reset prune gap correctly scoped.

## Recommendation

Proceed with implementation per `-001`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
