# GTKB Home

**Status:** Current component overview
**Reviewed:** 2026-09-26

GTKB Home is the primary interactive interface. The current implementation is a
pinned local web application bound to `127.0.0.1:3080` and opened in the user's
browser.

## Open Home

```powershell
gt --config E:\GTKB\groundtruth.toml home open
```

The command obtains the current launch URL and opens it in the default browser.
Do not store or publish the launch URL as a permanent shortcut; it contains
launch authentication material intended for the browser.

## Startup behavior

The production design registers `GTKB-Home` as a logon task. It starts Home at
owner logon and can restart an unexpected stop. Supported service controls pause
the task before an intentional stop so that the stop remains effective.

```powershell
gt --config E:\GTKB\groundtruth.toml home status
gt --config E:\GTKB\groundtruth.toml services status --json
```

## Windows launch affordances

A standard Start-menu entry and optional desktop shortcut are desired product
improvements, but they are not yet documented as part of a unified installer.
Any future shortcut should invoke the supported Home opener rather than embed a
fixed URL or secret.

GTKB does not currently require a taskbar icon. A system-tray controller should
be added only if measured user needs justify persistent health visibility or
frequent service controls.

## Privacy and network boundary

Home is intended to remain on loopback. Telemetry and credential behavior must
be verified against the selected release. Do not expose Home to another network
or assume that browser reachability establishes host qualification.
