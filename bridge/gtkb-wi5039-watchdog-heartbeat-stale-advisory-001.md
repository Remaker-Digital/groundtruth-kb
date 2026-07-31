ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: c0dc7bd5-3e1a-4215-921d-bc79d92a36be
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; Loyal Opposition dispatcher watch

bridge_kind: governance_advisory
Document: gtkb-wi5039-watchdog-heartbeat-stale-advisory
Version: 001 (ADVISORY)
Author: Loyal Opposition (Claude, interactive dispatcher watch)
Date: 2026-07-06 UTC
Work Item: WI-5039

# Advisory: dispatcher watchdog heartbeat persistently stale, holds health at WARN

## Source
Dispatcher watch (2026-07-05/06), Loyal Opposition harness B. Cited: WI-5039; evidence gt bridge dispatch health complex_lifecycle finding.

## Claim
The dispatcher supervisor watchdog heartbeat is persistently stale: gt bridge dispatch health reports complex_lifecycle WARN "watchdog heartbeat is stale" at 33s (session start) and 48.4s (about an hour later), both exceeding the 15s SLA, while the daemon own heartbeat stays fresh and dispatch works. The staleness is growing rather than oscillating, suggesting a frozen or non-heartbeating supervisor. This is the sole finding holding dispatch health at WARN instead of PASS, and it is a supervisor-liveness concern: a stale or dead watchdog would not promptly restart a crashed daemon.

## Owner Decision Needed
No owner decision is required to file. This is the sole blocker to a clean health PASS; the owner may treat dispatch as substantively clean (no failures, verdicts flowing on B/D/C) or require the watchdog fix before declaring PASS.

## Recommended Prime Action
1. Verify whether the watchdog process is heartbeating at all (frozen vs oscillating) and why the heartbeat exceeds the 15s SLA.
2. Determine the optimal resolution: repair the watchdog heartbeat cadence, restart or repair the supervisor, or adjust the SLA if 15s is unrealistically tight.
3. Author an implementation proposal for WI-5039.

## Classification Slot
Defect-remediation advisory (dispatcher supervisor liveness). Prime Builder disposition: adopt / defer. Convert into a normal implementation proposal for WI-5039.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
