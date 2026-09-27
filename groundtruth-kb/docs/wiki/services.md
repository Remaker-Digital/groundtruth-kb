# Services

**Status:** Current first-pass operator overview
**Reviewed:** 2026-09-26

GTKB is composed of independently inspectable components. There is no need to
invent a second authority or master state store to coordinate them.

| Component | Normal Windows behavior |
| --- | --- |
| PostgreSQL | Windows service, local canonical database substrate |
| Native GTKB domain service | Registered background task/service route for the selected installation |
| GTKB Home | Owner-logon scheduled task, loopback web interface |
| Dashboard and optional model services | Installation-dependent; inspect explicitly |

## Find the status view in Home

Open **Settings → GTKB** for the illustrated [status pane](Status). This provides
displayed diagnostics, but a row must be read with its explanatory text: the
documented dashboard row says **PASS** and **not contacted**, so it does not
prove that the dashboard is reachable.

The separately labeled **GTKB services** and **GTKB controls** tabs are visible
navigation destinations; their contents and start/stop behavior have not yet
been documented from supplied screenshots. The status pane is not evidence of
those controls' behavior.

## Inspect and operate services

Use the installed configuration when inspecting services:

```powershell
gt --config E:\GTKB\groundtruth.toml services status --json
```

Start and stop components only through supported operator controls. A process ID,
task registration, service registration, or old log entry does not prove current
readiness. Never stop a process by executable name alone; identify the exact
owned process or registered component first.

After a workstation restart, verify the real listeners and readiness responses.
See [Verify installation](Verify-Installation) and [Troubleshooting](Troubleshooting).
