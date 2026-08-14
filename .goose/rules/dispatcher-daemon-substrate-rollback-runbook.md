<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project goose`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Dispatcher Daemon Incident Runbook

The dispatcher daemon is the only automated bridge-dispatch substrate. There is
no automated rollback substrate. If daemon health fails, pause dispatchability
and use manual owner assignment/scanning until the daemon is repaired.

## Procedure

1. Confirm current state:

   ```powershell
   gt bridge dispatch health
   gt bridge dispatch daemon status --json
   ```

2. Quiesce automated dispatch if needed by setting affected harnesses
   `can_receive_dispatch=false` through the dispatcher control surface.

3. Continue bridge work manually from TAFE/dispatcher-backed state and numbered
   bridge files.

4. Repair the daemon, then re-enable dispatchability only after health is clean.

Do not restore retired pollers, hook-triggered bridge workers, or scheduled
single-harness bridge workers.
