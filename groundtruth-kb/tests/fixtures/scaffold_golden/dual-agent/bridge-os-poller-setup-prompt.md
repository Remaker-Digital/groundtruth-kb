# DEPRECATED — Smart Poller Retired (Slice 4, 2026-05-09)

> ⚠️ **DEPRECATED** — The smart-poller mechanism this template documented
> was retired on 2026-05-09 in favor of the cross-harness event-driven
> trigger. Do **NOT** follow this template for new installations.
>
> The smart-poller runtime (`scripts/run_smart_bridge_poller.vbs`,
> `scripts/run_smart_bridge_poller.ps1`,
> `groundtruth-kb/scripts/bridge_poller_runner.py`, the
> `GTKB-SmartBridgePoller` Windows scheduled task) has been archived to
> `archive/smart-poller-2026-05-09/`. Attempting to follow these
> instructions will fail because the runner has been moved.

## Replacement Mechanism

The active bridge dispatch automation is the **cross-harness
event-driven trigger** at
`scripts/cross_harness_bridge_trigger.py`. It is registered in:

- `.claude/settings.json` — `PostToolUse` and `Stop` hook arrays
- `.codex/hooks.json` — Codex-side parity (forward-compatible per
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`)

When canonical bridge state changes, or the agent ends a turn, the trigger
inspects dispatcher/TAFE state
and dispatches the appropriate counterpart harness if a recipient's actionable
queue signature has changed.

## See Instead

- Slice 3 closure:
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- Slice 4 retirement:
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`.
- Tutorial: `groundtruth-kb/docs/tutorials/dual-agent-setup.md` (cross-harness
  event-driven trigger setup is documented here per Slice 4 D5d).
- Doctor check: `_check_cross_harness_trigger` in
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.

This file remains as a deprecated stub for two release cycles to give
adopter projects time to migrate references. It will be removed in a
future cleanup; see Slice 4 Open Follow-On §7.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
