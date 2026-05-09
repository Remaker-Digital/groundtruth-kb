# Smart Poller Retirement Archive — 2026-05-09

This directory archives the smart-poller runtime surfaces retired by Slice 4
of the bridge-poller event-driven replacement program.

## Retirement Authority

- Bridge thread: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`
  (filed REVISED-1..REVISED-7; GO at `-016`).
- Owner directive: "Mitigate now, then land Slice 4 (Recommended)" — AskUserQuestion answer, 2026-05-09 UTC.
- Deliberation record: `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09`.
- Replacement mechanism: cross-harness event-driven trigger via
  `scripts/cross_harness_bridge_trigger.py`, registered in
  `.claude/settings.json` and `.codex/hooks.json` PostToolUse + Stop hook
  arrays (Slice 3 closure: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`).

## Archived Surfaces

### Scripts (`scripts/`)

- `run_smart_bridge_poller.vbs` — VBS daemon entrypoint for the Windows
  scheduled-task `GTKB-SmartBridgePoller`.
- `run_smart_bridge_poller.ps1` — PowerShell driver invoked by the VBS.
- `install_smart_poller_task.ps1` — installer that registered the
  scheduled task.
- `uninstall_smart_poller_task.ps1` — uninstaller for the scheduled task.
- `bridge_notify_reader.py` — read-only inspector for the dead
  `.gtkb-state/bridge-poller/notifications/` directory.

### `groundtruth-kb/` package

- `groundtruth-kb/scripts/bridge_poller_runner.py` — single-instance runner
  that scanned `bridge/INDEX.md` every 15s and dispatched harnesses on
  actionable signature changes.
- `groundtruth-kb/tests/test_bridge_poller_runner.py` — pytest coverage for
  the runner.
- `tests/test_doctor_smart_poller.py` — pytest coverage for the now-removed
  `_check_smart_bridge_poller` doctor check (archived by Slice 4 D4 after
  the doctor refactor; archived at the approved REVISED-7 target
  `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py` per
  bridge `-018` F2).

## Why Archived (not deleted)

The bridge protocol invariants under `.claude/rules/bridge-essential.md`
are append-only; the file class is "archive on retirement" rather than
"delete." Future references (post-mortems, regression-fixture tests,
historical research) read from this directory.

The Windows scheduled task `GTKB-SmartBridgePoller` was deleted via
`schtasks /Delete /F` as part of Slice 4 D1 (no-archive operation; the
task definition is recreatable from this archive's installer script if
ever needed historically, but doing so reactivates the retired
mechanism and is forbidden by `.claude/rules/bridge-essential.md`
§"Re-Enabling Pollers").

## Do Not Restore As Active Path

Per `.claude/rules/bridge-essential.md` §"Re-Enabling Pollers", the OS
poller class must not be restored as the active automation path
without explicit owner approval and a fresh cost/benefit analysis. The
files in this archive are historical evidence, not a deployment kit.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
