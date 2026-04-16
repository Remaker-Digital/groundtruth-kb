# Bridge OS Scheduler

<!-- © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. -->

Configure the file bridge pollers on your operating system so that Prime
Builder and Loyal Opposition scan `bridge/INDEX.md` every 3 minutes without
requiring a running terminal session.

## Overview

The file bridge needs two recurring pollers:

- **Prime Builder poller** — checks for GO or NO-GO entries and dispatches
  `claude` (or your configured Prime Builder CLI).
- **Loyal Opposition poller** — checks for NEW or REVISED entries and
  dispatches `codex exec` (or your configured Loyal Opposition CLI).

Each poller:

1. Parses `bridge/INDEX.md`
2. Acquires a lock file to prevent overlapping runs
3. Dispatches the agent only when actionable entries exist
4. Writes a status file to
   `independent-progress-assessments/bridge-automation/logs/`
5. Appends to a rolling log file

The `templates/bridge-os-poller-setup-prompt.md` file (generated in your
project root) contains a fully-parameterized prompt. Use it with Claude Code
or Codex to generate the poller scripts and register them with the OS
scheduler automatically.

---

## Status-File Contract

Each poller writes a JSON status file after every scan:

**Paths (relative to project root):**

| Agent | Path |
|-------|------|
| Claude (Prime) | `independent-progress-assessments/bridge-automation/logs/claude-scan-status.json` |
| Codex (LO) | `independent-progress-assessments/bridge-automation/logs/codex-scan-status.json` |

**Schema:**

```json
{
  "updatedAtUtc": "2026-04-15T14:30:00Z",
  "state": "clear",
  "message": "No actionable bridge entries found."
}
```

**Fields:**

- `updatedAtUtc` — ISO 8601 UTC timestamp of the last scan
- `state` — opaque string; common values include `clear`, `dispatched`,
  `skipped`, `error` — display as-is
- `message` — human-readable scan summary

**Freshness thresholds (used by `gt project doctor`):**

| Age | Reported as |
|-----|-------------|
| < 4 minutes | OK |
| 4–10 minutes | WARN |
| > 10 minutes | ALARM |
| File absent | not started |
| Missing/unparseable `updatedAtUtc` | ALARM |

---

## macOS / Linux — cron

Add two cron entries, one for each agent:

```bash
crontab -e
```

```cron
# Prime Builder poller — every 3 minutes
*/3 * * * * cd /path/to/your/project && /path/to/prime-poller.sh >> \
    independent-progress-assessments/bridge-automation/logs/prime-poller.log 2>&1

# Loyal Opposition poller — every 3 minutes
*/3 * * * * cd /path/to/your/project && /path/to/lo-poller.sh >> \
    independent-progress-assessments/bridge-automation/logs/lo-poller.log 2>&1
```

Replace `/path/to/your/project` with the absolute path to your project root
and `/path/to/prime-poller.sh` with the path to the generated poller script.

If your CLI tools are only in your user PATH (not the cron `PATH`), source
your profile at the top of each poller script:

```bash
#!/bin/bash
source ~/.bashrc   # or ~/.zshrc / ~/.profile
```

---

## macOS — launchd (recommended over cron for user sessions)

Create a plist at `~/Library/LaunchAgents/com.yourproject.prime-poller.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yourproject.prime-poller</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/path/to/your/project/prime-poller.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/your/project</string>
    <key>StartInterval</key>
    <integer>180</integer>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/path/to/your/project/independent-progress-assessments/bridge-automation/logs/prime-poller.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/your/project/independent-progress-assessments/bridge-automation/logs/prime-poller-err.log</string>
</dict>
</plist>
```

Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.yourproject.prime-poller.plist
```

Create a parallel plist for the Loyal Opposition poller with label
`com.yourproject.lo-poller`.

---

## Windows — Task Scheduler

On Windows, use Task Scheduler with a hidden PowerShell launcher to avoid a
visible console window on every poll.

The generated `bridge-os-poller-setup-prompt.md` contains instructions for
creating:

- `independent-progress-assessments/bridge-automation/prime-poller.ps1`
- `independent-progress-assessments/bridge-automation/lo-poller.ps1`
- `independent-progress-assessments/bridge-automation/launch-prime.vbs`
  (hidden launcher)
- `independent-progress-assessments/bridge-automation/launch-lo.vbs`
  (hidden launcher)

Register each task with a 3-minute repeat:

```powershell
# Example for Prime Builder poller
$action = New-ScheduledTaskAction -Execute "wscript.exe" `
    -Argument "C:\path\to\project\independent-progress-assessments\bridge-automation\launch-prime.vbs"
$trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 3) `
    -Once -At (Get-Date)
Register-ScheduledTask -TaskName "MyProject-PrimePoller" `
    -Action $action -Trigger $trigger -RunLevel Highest
```

!!! warning "Run as your user account"
    The scheduled task must run as your Windows user account (not SYSTEM)
    to inherit your Claude Desktop OAuth session. If the task runs as SYSTEM,
    authentication will fail. See [Auth Troubleshooting](../troubleshooting/auth.md).

---

## Verifying the Setup

After registering the pollers, run a manual health check:

```bash
gt project doctor
```

The doctor reports bridge status for each agent:

```
  [OK]   Claude bridge poller: OK (last scan 1m 23s ago, state: clear)
  [OK]   Codex bridge poller:  OK (last scan 0m 47s ago, state: clear)
```

If either poller shows WARN or ALARM, check the log files under
`independent-progress-assessments/bridge-automation/logs/` and see
[Auth Troubleshooting](../troubleshooting/auth.md) if authentication is
the cause.

---

## Updating Poller Scripts

After any of the following changes, update and re-register the pollers:

- New Claude Code version or model flag
- New Codex CLI version or endpoint
- Prompt text changes (re-run `bridge-os-poller-setup-prompt.md`)
- Project root move or rename

Update `BRIDGE-INVENTORY.md` whenever you change a scheduler task, script
path, log path, or agent CLI command.
