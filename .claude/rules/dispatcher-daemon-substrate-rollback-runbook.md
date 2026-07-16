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
