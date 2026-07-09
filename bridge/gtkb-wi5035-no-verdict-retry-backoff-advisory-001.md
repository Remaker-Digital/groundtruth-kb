ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: c0dc7bd5-3e1a-4215-921d-bc79d92a36be
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; Loyal Opposition dispatcher watch

bridge_kind: governance_advisory
Document: gtkb-wi5035-no-verdict-retry-backoff-advisory
Version: 001 (ADVISORY)
Author: Loyal Opposition (Claude, interactive dispatcher watch)
Date: 2026-07-06 UTC
Work Item: WI-5035

# Advisory: dispatcher lacks backoff on repeated no-verdict launches

## Source
Dispatcher watch (2026-07-05/06), Loyal Opposition harness B. Cited: WI-5035; evidence .gtkb-state/bridge-poller/dispatch-failures.jsonl.

## Claim
When a dispatched worker exits without producing a verdict, the daemon re-detects error_type=no_verdict_produced / reason=previous_launch_failed and re-attempts on a tight ~15s cadence with no backoff, churning dispatch cycles without terminal progress. This amplified the F failures into rapid re-dispatch, a spawn-rate-limited event, and a live-worker surge.

## Owner Decision Needed
No owner decision is required to file. Owner may prioritize the fix relative to other dispatcher-reliability work.

## Recommended Prime Action
1. Verify the retry cadence and the absence of backoff in the daemon no-verdict handling path.
2. Determine the optimal resolution: exponential backoff, bounded retries then quarantine, or integration with the existing circuit-breaker.
3. Author an implementation proposal for WI-5035, with a dispatcher test asserting backoff/bounded-retry on repeated no_verdict_produced for the same signature.

## Classification Slot
Defect-remediation advisory (dispatcher reliability). Prime Builder disposition: adopt / defer. Convert into a normal implementation proposal for WI-5035.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
