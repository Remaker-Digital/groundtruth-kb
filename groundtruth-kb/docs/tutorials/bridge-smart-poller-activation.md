# Bridge Smart Poller — Activation Procedure (Windows)

This tutorial walks through activating the notification-based smart-poller as
a Windows Scheduled Task. The procedure was authorized by
`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md` (GO at REVISED-1
`-003`).

## Prerequisites

Before activation, all of the following must be VERIFIED:

- P1 detector module (`groundtruth_kb.bridge.detector`)
- P2 registry module (`groundtruth_kb.bridge.registry`)
- P2.5 spike machinery + report
- P3-notify writer (`groundtruth_kb.bridge.notify.update_notification`,
  `read_notification`, `NotificationArtifact`, `NOTIFY_SCHEMA_VERSION`)
- Activation reader (`scripts/bridge_notify_reader.py`)
- Session-start wiring in `scripts/session_self_initialization.py`
- Wrapper script at `scripts/run_smart_bridge_poller.ps1`

Run the project doctor to confirm:

```text
python -c "from groundtruth_kb.cli import main; main(['project','doctor','--dir','.'], standalone_mode=False)"
```

The smart-poller-specific checks should pass (or report only the "Task not
registered" failure that this procedure resolves).

## Activation

```powershell
# From the project root (e.g., E:\GT-KB)
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/install_smart_poller_task.ps1
```

Output (success):

```text
Smart-poller task 'GTKB-SmartBridgePoller' registered (wrapper=E:\GT-KB\scripts\run_smart_bridge_poller.ps1, interval=15 s).
Smart-poller task 'GTKB-SmartBridgePoller' started.
```

To override the polling interval:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/install_smart_poller_task.ps1 `
  -IntervalSeconds 30
```

The script is idempotent — re-running updates the existing task in place.

## Smoke Test

After installation, verify the activation chain end-to-end:

1. **Confirm task is running:**
   ```powershell
   Get-ScheduledTask -TaskName "GTKB-SmartBridgePoller" |
     Format-Table TaskName, State, LastTaskResult
   ```
   `State` should be `Running` and `LastTaskResult` should be `0` (or
   recent `267009` indicating a started task).

2. **Wait 30 seconds** (1 bootstrap iteration + 1 post-bootstrap iteration
   at the default 15-second interval).

3. **Confirm notification artifacts:**
   ```powershell
   Test-Path .gtkb-state/bridge-poller/notifications/pending-bridge-action-prime.json
   Test-Path .gtkb-state/bridge-poller/notifications/pending-bridge-action-codex.json
   ```
   At least one will exist if the live `bridge/INDEX.md` has actionable
   GO/NO-GO entries (for prime) or NEW/REVISED entries (for codex).

4. **Confirm reader integration:**
   Open a fresh Claude Code session. The session-start orient block should
   include a "Smart-poller notification" section listing the pending
   actions for Prime (or no section at all if INDEX has no actionable
   GO/NO-GO entries for the current role).

## Phase 2 Path Rebase (Future)

After Phase 2 of the GT-KB isolation plan moves `groundtruth-kb/` content to
the platform root, the **only change required** to keep the smart poller
operational is a single-line edit to the wrapper:

```powershell
# scripts/run_smart_bridge_poller.ps1, around line 28:
$runnerPath = Join-Path $projectRoot "groundtruth-kb\scripts\bridge_poller_runner.py"
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# After Phase 2:
$runnerPath = Join-Path $projectRoot "scripts\bridge_poller_runner.py"
```

**No OS task re-registration is required.** The wrapper architecture deliberately
isolates the OS task layer from the file-layout layer.

This rebase is captured as a Phase 2 path-rebase checklist item per the
`-004` GO guardrail 3.

## Uninstall

To stop the smart poller and remove the task:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/uninstall_smart_poller_task.ps1
```

The script preserves `.gtkb-state/bridge-poller/` contents (notification
artifacts and audit logs) for diagnostic review. Delete the directory
manually if a fresh-start is desired:

```powershell
Remove-Item -Recurse -Force .gtkb-state/bridge-poller
```

## Troubleshooting

### Task is registered but `LastTaskResult` is non-zero

Check the wrapper resolves the runner path:

```powershell
& "scripts/run_smart_bridge_poller.ps1"
# If this errors, the wrapper's $runnerPath is invalid.
# Phase 2 rebase outstanding? See "Phase 2 Path Rebase" above.
```

### No notification files appear after 30 seconds

Check the task is actually running and reading INDEX.md:

```powershell
Get-Content .gtkb-state/bridge-poller/poller-runs/*.jsonl |
  Select-Object -Last 5
```

A healthy poller writes at least one JSONL entry per scan. If the file is
empty or absent, the task didn't start or the wrapper failed.

### Schema version mismatch in orient

If the orient block silently omits the smart-poller section even when
notification files are present, the `format_orient_section` function may be
detecting a `schema_version` mismatch. Check:

```powershell
Get-Content .gtkb-state/bridge-poller/notifications/pending-bridge-action-prime.json |
  ConvertFrom-Json |
  Select-Object schema_version
```

Expected: `2`. If different, the schema has been bumped; update the reader
and consumers accordingly.

## See Also

- `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md` — activation
  authorization (GO at REVISED-1 `-003`)
- `groundtruth-kb/docs/tutorials/bridge-smart-poller.md` — overall smart-poller
  rule and minimum health evidence requirements
- `.claude/rules/bridge-essential.md` — bridge-protocol and poller-enablement
  contract
