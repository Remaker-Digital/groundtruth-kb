ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: c0dc7bd5-3e1a-4215-921d-bc79d92a36be
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; Loyal Opposition dispatcher watch

bridge_kind: governance_advisory
Document: gtkb-wi5036-stale-lease-reaping-advisory
Version: 001 (ADVISORY)
Author: Loyal Opposition (Claude, interactive dispatcher watch)
Date: 2026-07-06 UTC
Work Item: WI-5036

# Advisory: expired document leases linger for hours without reaping

## Source
Dispatcher watch (2026-07-05/06), Loyal Opposition harness B. Cited: WI-5036; evidence .gtkb-state/bridge-poller/leases/*.lock.

## Claim
Expired document-lease .lock files (TTL 3900s / 65 min) accumulate far past their TTL: the wi4996 lease reached ~10 hours old and the lease count grew from ~13 to ~26 over the watch. The daemon honors TTL in its held-count (so expired locks do not currently block dispatch), but they are not reaped and accumulate as transient-state debt.

## Owner Decision Needed
No owner decision is required to file. Owner may prioritize relative to other hygiene work.

## Recommended Prime Action
1. Verify the expired-lease reaping behavior (or absence) in the daemon.
2. Determine the optimal resolution: periodic reap of expired locks, reap-on-tick, and/or whether the drain/reset commands should cover it.
3. Author an implementation proposal for WI-5036 so the leases directory does not accumulate hours-stale locks.

## Classification Slot
Hygiene advisory (dispatcher transient-state). Prime Builder disposition: adopt / defer. Convert into a normal implementation proposal for WI-5036.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
