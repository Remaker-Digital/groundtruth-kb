# DEPRECATED — Bridge Smart Poller Canonical (Retired Slice 4, 2026-05-09)

> ⚠️ **DEPRECATED** — This template documented the canonical smart-poller
> behavior contract. The smart-poller mechanism was retired on 2026-05-09
> in favor of the **cross-harness event-driven trigger**. Do **NOT** scaffold
> projects from this template.

## Replacement Authority

The canonical bridge dispatch automation is now the **cross-harness
event-driven trigger** at `scripts/cross_harness_bridge_trigger.py`,
registered in:

- `.claude/settings.json` — `PostToolUse` and `Stop` hook arrays.
- `.codex/hooks.json` — Codex-side parity (forward-compatible per
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`).

The replacement contract is described in:

- `.claude/rules/bridge-essential.md` (active operating mode).
- `templates/rules/prime-bridge-collaboration-protocol.md` § Bridge Dispatch
  Automation (per Slice 4 D5k).
- `groundtruth-kb/docs/tutorials/dual-agent-setup.md` (tutorial; Slice 4 D5d).

## What Was Retired

- The `GTKB-SmartBridgePoller` Windows scheduled task (deleted, not just disabled).
- `scripts/run_smart_bridge_poller.vbs`, `scripts/run_smart_bridge_poller.ps1`,
  `scripts/install_smart_poller_task.ps1`,
  `scripts/uninstall_smart_poller_task.ps1` (archived).
- `groundtruth-kb/scripts/bridge_poller_runner.py` (archived).
- The doctor's `_check_smart_bridge_poller` end-to-end activation check (replaced
  by `_check_cross_harness_trigger`).

All archived files live under `archive/smart-poller-2026-05-09/`.

## Why Retired

Per `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` and
`DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09`, the smart-poller's
empirical foundation (Codex hook execution on Windows) became reliable
in `codex_hooks` `stable, true` (CLI ≥ 0.128.0-alpha.1). The
event-driven trigger replaces interval polling with hook-driven dispatch,
removing the registered-task surface, the daemon liveness pattern, and
the per-recipient lock contention class.

This stub remains for two release cycles to give adopter projects time
to migrate scaffold references. It will be removed in a future cleanup;
see Slice 4 Open Follow-On §7.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
