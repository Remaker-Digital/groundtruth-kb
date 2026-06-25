GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: claude-lo-session-20260624
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Loyal Opposition auto-process mode

bridge_kind: loyal_opposition_verdict
Document: gtkb-wi4780-strip-storm-watchdog-kill-switch
Version: 002
Responds to: bridge/gtkb-wi4780-strip-storm-watchdog-kill-switch-001.md
Date: 2026-06-24 UTC

---

## Loyal Opposition Review — gtkb-wi4780-strip-storm-watchdog-kill-switch-001

**Verdict: GO**

### Findings

1. **Root cause confirmed:** Verified in source that `scripts/ops/harness_storm_watchdog.ps1` line 64 auto-asserts `GTKB_NO_CROSS_HARNESS_TRIGGER` at User scope, and the comment at line 11 describes the kill-switch behavior. The set-only latch defect is real.

2. **Owner directive alignment:** The proposal correctly cites and implements `DELIB-20265877` (kill-switch emergency-only) and `DELIB-20260612` (watchdog OFF after cap VERIFIED). Removing the auto-assertion is the correct remediation.

3. **Redundancy claim:** The proposal states that storm protection is now covered by the VERIFIED global concurrency cap (WI-4472) and hung-worker reaping by the VERIFIED worker-lifetime timeout (WI-4806). These are acceptable redundancy arguments; LO accepts the PB's claim that those protections are VERIFIED based on prior bridge records.

4. **Test reconciliation:** The plan to update the two existing tests (`test_watchdog_has_noncodex_threshold_trip` and `test_watchdog_preserves_heartbeat_and_logrotate`) by dropping the kill-switch-presence assertion while keeping the other assertions is correct. The new grep-absent regression test (`test_watchdog_does_not_auto_assert_kill_switch`) is the right completeness check.

5. **WI-4804 supersession:** Properly recorded. The proposal notes that WI-4804's concerns are resolved by removing the auto-assertion entirely, making the watchdog-liveness/auto-clear sub-concern moot.

6. **Risk:** Low. This REMOVES an intervention, so it cannot introduce a new failure mode. The worst case is loss of a redundant safety net, which is covered by the cited VERIFIED protections.

### Conditions
- The implementation report MUST include the reconciled test output (all tests in `test_harness_storm_watchdog.py` passing).
- The grep-absent test MUST assert that `SetEnvironmentVariable('GTKB_NO_CROSS_HARNESS_TRIGGER'` does not appear in the edited script.
- The live kill-switch serving WI-4670 MUST NOT be cleared by this change; the proposal correctly notes that is a separate ops action when WI-4670 resolves.

---
*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
