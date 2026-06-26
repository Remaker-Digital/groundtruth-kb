GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-autoproc-2026-06-27-queue
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Loyal Opposition auto-process

bridge_kind: proposal_review
Document: gtkb-wi4805-reset-recipient-stale-last-launch-pid-reap
Version: 003
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4805-reset-recipient-stale-last-launch-pid-reap-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4805
Recommended commit type: fix

## Separation Check

Proposal `-001` author session `130bf9ae-15f0-4373-a7b5-9286568dbc97` (harness B); independent Cursor LO session. Supersedes withdrawn duplicate `gtkb-wi4805-reset-recipient-clears-stale-last-launch-002` (WITHDRAWN).

## Review Summary

**GO.** With the subset thread withdrawn, this is the canonical WI-4805 proposal. Root cause confirmed: `_reset_recipient_state` clears circuit-breaker fields but leaves stale `last_launch`/signature state and any hung worker pid. Clean-slate reset + gated straggler reap (operator-initiated only, provenance from `last_launch.pid`, age >= worker lifetime) is appropriately bounded. PID-reap is optimization post-WI-4845/WI-4803 but still valuable for immediate operator recovery.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| Reset leaves last_launch/signature | pass | `cross_harness_bridge_trigger.py` L714-722 |
| Reap scoped to recorded straggler | pass | proposal gates on liveness + lifetime threshold |
| Interactive safety | pass | manual `--reset-recipient` only; no auto path |
| PAUTH authorization | pass | `DELIB-20266137` |

## Prior Deliberations

- `DELIB-20266137` — drive authorization.

## Verdict

**GO.** Implement per `-001`; scope pid-reap as operator-recovery optimization if lifetime cap already handles hung workers.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
