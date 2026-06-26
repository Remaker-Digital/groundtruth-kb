GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi4852-watchdog-dormancy-auto-restart
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-26 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4852
Recommended commit type: feat

## Separation Check

Proposal -001 author session `e150e9ce-4657-4130-9e10-af48d3e79a44` (harness B, Claude Prime Builder); independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E). Distinct session contexts — review eligible.

## Clause Applicability (Slice 2; mandatory gate)

Preflight exit 0; 4 must_apply clauses with evidence; 0 blocking gaps.

## Review Summary

**GO.** WI-4852 correctly extends the WI-4790 health-response substrate with watchdog dormancy detection and fail-soft auto-restart. **Option B accepted** (heartbeat artifact age vs threshold). The watchdog already writes `.gtkb-state/ops/storm-watchdog-heartbeat.txt` each run — implementation should consume that existing artifact, not add a parallel heartbeat surface.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| Storm watchdog + reap module exist | pass | `harness_storm_watchdog.ps1`, `storm_watchdog_reap.py` |
| `health_response()` remediation hints exist | pass | `dispatch_monitor.py` (`reap_stale_dispatch_runs`, `drain_and_hold`) |
| Daemon tick wires monitoring fail-soft | pass | `gtkb_dispatcher_daemon.py` + `test_run_tick_monitoring_failsoft` |
| WI-4790 slices VERIFIED | pass | bridge threads cited in -001 |
| Spec-derived test plan | pass | 5 named tests across monitor + daemon modules |
| PAUTH covers work | pass | `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4852-WATCHDOG-DORMANCY-AUTO-RESTART` |
| Heartbeat write needed (Option B) | partial | heartbeat already written at line 92 of `harness_storm_watchdog.ps1` |

## Design Decision (Option B vs A)

**Option B — GO.** Reuse `.gtkb-state/ops/storm-watchdog-heartbeat.txt` as the dormancy signal. Pure `watchdog_dormancy(last_evidence_epoch, now, threshold_seconds)` over parsed epoch is unit-testable and symmetric with daemon heartbeat. Option A (schtasks LastRunTime) rejected: platform-coupled, untestable when task deregistered.

## Implementation Conditions

1. Read existing heartbeat path; do not duplicate heartbeat write unless format change is required (document if so).
2. Keep watchdog dormancy as a **daemon-level** sibling to per-role `health_response()` — do not widen the per-role contract.
3. `restart_storm_watchdog` execution must be fail-soft (record in status/tick result; never abort tick).
4. Default threshold 2× watchdog cadence; treat missing/zero epoch as dormant per test plan.
5. Platform restart step may remain Windows scheduled-task bound; pure detection tests must not require live task registration.

## Prior Deliberations

- DELIB-20266192 — owner AUQ authorizing WI-4852 / covering PAUTH.
- DELIB-20266132 — WI-4670 re-scope; watchdog-liveness follow-on.
- DELIB-20266137 / DELIB-20266138 — dispatcher reliability program / activation drive.
- WI-4790 slice 2/3 VERIFIED — health-response core + daemon wiring.

## Verdict

**GO.** Implement per -001 with Option B and existing heartbeat artifact.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
