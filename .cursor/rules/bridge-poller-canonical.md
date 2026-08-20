<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project cursor`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# DEPRECATED — Bridge Smart Poller Canonical (Retired Slice 4, 2026-05-09)

> ⚠️ **DEPRECATED** — This template documented the canonical smart-poller
> behavior contract. The smart-poller mechanism was retired on 2026-05-09
> in favor of the **dispatcher daemon**. Do **NOT** scaffold
> projects from this template.

## Replacement Authority

The canonical bridge dispatch automation is now the **cross-harness
event-driven trigger** at `scripts/gtkb_dispatcher_daemon.py`,
registered in:

- `settings.json` (or projected harness config) — `PostToolUse` and `Stop` hook arrays.
- harness hooks configuration — Codex-side parity (forward-compatible per
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`).

The replacement contract is described in:

- `.harness-baseline-configuration/rules/bridge-essential.md` (active operating mode).
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
  by `_check_dispatcher_daemon`).

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
