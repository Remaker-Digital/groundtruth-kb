# GTKB Home

**Status:** Current component overview

**Reviewed:** 2026-09-26

GTKB Home is GroundTruth KB's integrated harness GUI and primary interactive
interface. The current implementation is a pinned local web application bound to
`127.0.0.1:3080` and opened in the user's browser.

## Open Home

```powershell
gt --config E:\GTKB\groundtruth.toml home open
```

The command obtains the current launch URL and opens it in the default browser.
Do not store or publish the launch URL as a permanent shortcut; it contains
launch authentication material intended for the browser.

## Recognize the first screen

![GTKB Home Preview in a browser, with New Session and an empty Workspaces sidebar, Choose workspace and Standard mode selectors, and a composer saying Choose a workspace to start.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-empty-state.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged. The UI is
marked **Preview**; its exact build/version is not visible. This is an orientation
image, not an installation, service-health, or end-to-end workflow test.

| Visible control or message | How to read it |
| --- | --- |
| **Choose workspace** | Start here to select the workspace you intend to use. The composer explicitly asks for a workspace before starting. |
| **Choose a workspace to start** | This is a prerequisite message in the prompt composer, not an instruction to type a workspace path into the prompt. |
| **Standard mode** | A mode selector is shown with this value. Do not treat its label as proof of a governed agent role or project authorization. Mode options and their effects still need a tested reference. |
| **New Session** | The sidebar's session entry point. The capture does not show the subsequent session flow. |
| **Workspaces / No sessions yet** | The displayed navigation view has no sessions. That does not establish whether canonical projects or work items exist. |
| **Settings** | The settings entry point is at the lower left. Its contents are not shown in this capture. |

The capture also contains icon-only controls beside **Workspaces** and inside the
composer. Their tooltips, accessible names, keyboard behavior, and resulting
dialogs have not been inspected; this guide does not assign them unverified
functions.

Continue with [Get started](Get-Started) for the next steps. The remaining
first-run guidance and screenshot coverage are listed in
[Known issues](Known-Issues).

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
