# DEPRECATED — Smart Poller Retired (Slice 4, 2026-05-09)

> ⚠️ **DEPRECATED** — The smart-poller activation procedure this
> tutorial documented was retired on 2026-05-09 in favor of the
> cross-harness event-driven trigger. Do **NOT** run
> `install_smart_poller_task.ps1` or attempt to register the
> `GTKB-SmartBridgePoller` scheduled task; those scripts have been
> archived and will fail.
>
> The smart-poller runtime
> (`scripts/run_smart_bridge_poller.vbs`,
> `scripts/run_smart_bridge_poller.ps1`,
> `scripts/install_smart_poller_task.ps1`,
> `scripts/uninstall_smart_poller_task.ps1`,
> `groundtruth-kb/scripts/bridge_poller_runner.py`) has been archived to
> `archive/smart-poller-2026-05-09/`.

## Replacement Mechanism

The active bridge dispatch automation is the **cross-harness
event-driven trigger** at
`scripts/cross_harness_bridge_trigger.py`. There is no installation
procedure analogous to `install_smart_poller_task.ps1`; the trigger is
activated by hook registrations in `.claude/settings.json`
(`PostToolUse` + `Stop`) and `.codex/hooks.json`. Hook registrations
are scaffolded automatically by `gt project init` for the
`dual-agent` profile and are present in this repository at
`HEAD`.

To verify the trigger is active:

```text
python -c "from groundtruth_kb.cli import main; main(['project','doctor','--dir','.'], standalone_mode=False)"
```

The doctor reports the cross-harness-trigger status via
`_check_cross_harness_trigger` (PASS/WARN/FAIL covering trigger script
presence, both hook registrations, and dispatch-state freshness) and
the per-recipient dispatch-state liveness via
`_check_bridge_dispatch_liveness`.

## See Instead

- Tutorial: `groundtruth-kb/docs/tutorials/dual-agent-setup.md` (cross-harness
  event-driven trigger setup is documented here per Slice 4 D5d).
- Slice 3 closure (hook registrations):
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- Slice 4 retirement:
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`.

This file remains as a deprecated stub for two release cycles to give
adopter projects time to migrate references. It will be removed in a
future cleanup; see Slice 4 Open Follow-On §7.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
