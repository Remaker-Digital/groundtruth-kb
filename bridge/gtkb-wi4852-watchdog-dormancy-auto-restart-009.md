VERIFIED
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: implementation_verification
Document: gtkb-wi4852-watchdog-dormancy-auto-restart
Version: 009
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-26 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-008.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4852
Recommended commit type: feat

## Separation Check

Report `-008` author session `3972336c-f3d6-47b7-bc56-051c146e2f7c` (harness B);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Verification Summary

**VERIFIED.** Implementation matches GO `-007` / REVISED `-006` intent. Pure
`watchdog_dormancy` detector in `dispatch_monitor.py`; daemon reads heartbeat,
records verdict, fail-soft restarts via `schtasks` when dormant in live mode only.

## Evidence

Independent re-run (2026-06-26):

```text
python -m pytest platform_tests/scripts/test_dispatch_monitor.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
=> 25 passed in 2.26s
```

Code review confirms:

- `_read_watchdog_heartbeat_epoch` parses leading ISO token only (`text.split()[0]`);
  fixes real-format line with trailing population fields.
- Restart gated `if not dry_run and mode == "live"` — preserves shadow-never-spawns
  invariant; dormancy verdict + remediation hint recorded in both modes.
- Fail-soft restart path; tick never aborts on restart failure.

## Design Decision (reviewer acceptance)

Shadow/live gating is **accepted**: live substrate owns remediation execution;
shadow observes and records. Consistent with committed WI-4848 daemon invariants
and existing monitoring/health block pattern.

## Prior Deliberations

- bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-007.md (GO),
  -008.md (implementation report).
- DELIB-20266192 — owner AUQ for WI-4852 PAUTH.

## Residual Notes

- `--finalize-verified` not attempted this cycle (standing inventory-drift
  pre-commit blocker on accumulated verified work).
