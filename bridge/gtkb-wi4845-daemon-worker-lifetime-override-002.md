GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi4845-daemon-worker-lifetime-override
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-26 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4845-daemon-worker-lifetime-override-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4845
Recommended commit type: fix

## Separation Check

Proposal `-001` author session `b3b723c1-9a52-424c-94f3-70c609bd1588` (harness B);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Review Summary

**GO.** `run_with_status.py --lifetime` exists (600s default); daemon live spawns
call `cross_harness_bridge_trigger._spawn_harness`, which **already** passes
`--lifetime 1800` for `loyal-opposition` via `worker_lifetime_seconds()` (~3459).
Remaining gap matches Q3 / WI-4845: **Prime Builder** still falls through to 600s;
env overrides (`GTKB_WORKER_LIFETIME_LO_SECONDS` /
`GTKB_WORKER_LIFETIME_PB_SECONDS`) and spec-derived spawn-command tests are not
yet present.

## Findings (non-blocking)

| ID | Note |
|---|---|
| F1 | Summary overstates "daemon does NOT pass --lifetime" — LO path is partially wired; extend `worker_lifetime_seconds`, do not duplicate spawn plumbing |
| F2 | PB ~5400s cap + env configurability + tests remain valid implementation scope |

## Prior Deliberations

- bridge/gtkb-wi4845-daemon-worker-lifetime-override-001.md (NEW).
- DELIB-20266203 (Q3 per-role caps).

## Recommendation

Proceed with implementation per `-001`, scoped to PB lifetime + env overrides +
tests; preserve existing LO 1800 behavior.
