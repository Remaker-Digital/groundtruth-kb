GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi4856-daemon-status-liveness-accurate
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4856-daemon-status-liveness-accurate-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4856
Recommended commit type: fix

## Separation Check

Proposal `-001` author session `d5a77c21-caee-404a-8fb3-6629ba276960` (harness B);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Review Summary

**GO.** Live code confirms both defects: `collect_daemon_status` (~596–602) sets
`running=True` from lock presence only while computing unused `heartbeat_age_seconds`
(~608–609); `mode` is hardcoded `"shadow"` (~592) and never calls `_active_substrate`
(already used correctly in `run_tick` ~456–457). Reusing `daemon_process_alive`
(WI-4855) plus heartbeat freshness bounds is the minimal correct fix. Test plan
covers stale-lock, live-PID, fresh-heartbeat, and substrate mode paths with
non-regression on existing stop/CLI tests.

## Residual risks (non-blocking)

- Transient `running=True` when lock is stale but heartbeat still within
  `HEARTBEAT_STALE_SECONDS` — acceptable per proposal; self-clears.

## Prior Deliberations

- DELIB-20266203 — Phase X daemon fix-chain authorization (X4 = WI-4856).
- WI-4855 — `daemon_process_alive` primitives reused here.

## Recommendation

Proceed with implementation per `-001`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
