# DEPRECATED — Smart Poller Retired (Slice 4, 2026-05-09)

> ⚠️ **DEPRECATED** — The smart-poller mechanism this template documented
> was retired on 2026-05-09 in favor of the dispatcher-daemon
> trigger. Do **NOT** follow this template for new installations.
>
> The smart-poller runtime (`scripts/run_smart_bridge_poller.vbs`,
> `scripts/run_smart_bridge_poller.ps1`,
> `groundtruth-kb/scripts/bridge_poller_runner.py`, the
> `GTKB-SmartBridgePoller` Windows scheduled task) has been archived to
> `archive/smart-poller-2026-05-09/`. Attempting to follow these
> instructions will fail because the runner has been moved.

## Replacement Mechanism

The active bridge dispatch automation is the **dispatcher daemon** at
`scripts/gtkb_dispatcher_daemon.py`, kept alive by the headless dispatcher
supervisor path. On each daemon cycle it inspects dispatcher/TAFE state and
dispatches the appropriate counterpart harness if a recipient's actionable
queue signature has changed.

## See Instead

- Slice 3 closure:
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- Slice 4 retirement:
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`.
- Tutorial: `groundtruth-kb/docs/tutorials/dual-agent-setup.md` (dispatcher
  daemon setup is documented there).
- Doctor check: `_check_dispatcher_daemon_substrate_readiness` in
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.

This file remains as a deprecated stub for two release cycles to give
adopter projects time to migrate references. It will be removed in a
future cleanup; see Slice 4 Open Follow-On §7.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
