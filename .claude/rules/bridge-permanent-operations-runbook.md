# Bridge Permanent Operations Runbook

Date: 2026-04-15
Owner decision source: Mike, live session instruction
Scope: Agent Red file bridge for GroundTruth-KB coordination

## Owner Decision

The file bridge is critical infrastructure. There is no accepted future state in
which the bridge is allowed to stop being maintained, monitored, or treated as
top-priority operational work.

Required behavior:

- The Prime and Codex bridge pollers must run on a 3-minute cycle.
- The bridge must have a visible liveness surface so Mike can see normal
  heartbeat, work-in-progress, failures, and recovery.
- If the bridge fails, restoring bridge function is always the top-priority
  task before ordinary review or implementation work.
- GroundTruth-KB is not operationally functional when the bridge is not working.

## Current Durable Controls

Bridge automation lives in:

`independent-progress-assessments/bridge-automation/`

Scheduled tasks:

- `AgentRedFileBridgeIndexScan-Codex`
  - every 3 minutes
  - handles latest `NEW` and `REVISED` entries in `bridge/INDEX.md`
- `AgentRedFileBridgeIndexScan-Claude`
  - every 3 minutes
  - handles latest `GO` and `NO-GO` entries in `bridge/INDEX.md`
- `AgentRedPollerLivenessWatcher`
  - every 2 minutes
  - runs `poller-liveness-stable-watcher.ps1`
  - writes `logs/poller-liveness-external.json`
  - debounces the brief "running child PID disappeared" completion race before
    publishing a dead liveness verdict
  - treats fresh scanner `error` states as failed liveness, not as healthy
    heartbeat

User-logon watchdog:

- `Agent Red Bridge Monitor Watchdog.lnk`
  - stored in the current user's Windows Startup folder
  - runs `run-bridge-monitor-watchdog-hidden.vbs`
  - starts `bridge-monitor-watchdog.ps1` hidden
  - every 2 minutes, ensures the visible monitor exists and runs the liveness
    alert check
  - every 2 minutes, disables a stale `.local/claude-oauth-token.txt` handoff
    token if injected-token auth fails but Claude managed desktop auth works

## Visible Status Surfaces

Primary visible surface:

`independent-progress-assessments/bridge-automation/bridge-scan-monitor-window.ps1`

The monitor displays:

- Claude poller state
- Codex poller state
- combined external liveness verdict
- clear/running/completed/skipped/error state transitions

Failure notifications:

`independent-progress-assessments/bridge-automation/show-bridge-liveness-alert.ps1`

This script emits Windows notifications when liveness is not `ok`, and emits a
recovery notification when liveness returns to `ok`.

Startup watchdog:

`independent-progress-assessments/bridge-automation/bridge-monitor-watchdog.ps1`

This hidden process is launched from the Windows Startup folder. It keeps the
visible monitor open, repairs stale Claude token handoff when possible, and
calls the liveness alert script every 2 minutes.

Machine-readable surfaces:

- `logs/claude-scan-status.json`
- `logs/codex-scan-status.json`
- `logs/poller-liveness-external.json`
- `logs/poller-liveness-stable.log`
- `logs/bridge-liveness-alert-state.json`
- `logs/claude-token-handoff-repair.log`

## Repair / Verification

Register or repair all durable scheduled tasks:

```powershell
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File independent-progress-assessments/bridge-automation/repair-permanent-bridge-automation.ps1
```

Verify without changing task registration:

```powershell
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File independent-progress-assessments/bridge-automation/repair-permanent-bridge-automation.ps1 -VerifyOnly
```

Expected verification:

- core scheduled tasks present
- Codex scanner interval is `PT3M`
- Claude scanner interval is `PT3M`
- liveness watcher interval is `PT2M`
- startup watchdog shortcut exists
- visible monitor process is running or can be started by the watchdog
- `poller-liveness-external.json` reports `overall=ok`

## Escalation Rule

If verification fails, stop ordinary work and repair the bridge first. The
minimum acceptable recovery evidence is:

1. scheduled tasks present and enabled
2. scanner tasks set to 3-minute intervals
3. liveness JSON updated within the alert threshold
4. external liveness `overallState` is `ok`
5. visible monitor window is running or can be started by the ensure task
