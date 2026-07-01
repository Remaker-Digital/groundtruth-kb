# DEPRECATED — OS Scheduler and Smart Poller Both Retired (Slice 4, 2026-05-09)

> ⚠️ **DEPRECATED** — Both the OS-scheduled-task bridge poller (retired
> 2026-04-25) and its successor the smart-poller (retired 2026-05-09)
> are no longer the active bridge automation path. Do **NOT** restore
> either implementation.

## Replacement Mechanism

The active bridge dispatch automation is the **dispatcher daemon** at
`scripts/gtkb_dispatcher_daemon.py`, kept alive by the headless dispatcher
supervisor path. Manual bridge-state scans remain available as a fallback when
the daemon is unhealthy.

## See Instead

- Tutorial: `groundtruth-kb/docs/tutorials/dual-agent-setup.md` (dispatcher
  daemon setup is documented there).
- Slice 3 closure (daemon configuration):
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- Slice 4 retirement:
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`.
- `.claude/rules/bridge-essential.md` — bridge-protocol rule (smart-poller
  references in this rule are reframed as RETIRED with historical context;
  see Slice 4 D5).

This file remains as a deprecated stub for two release cycles to give
adopter projects time to migrate references. It will be removed in a
future cleanup; see Slice 4 Open Follow-On §7.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
