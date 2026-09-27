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
| **Choose workspace** | Start here to choose the intended working directory. Follow-up captures illustrate the [Windows directory picker](Get-Started#the-windows-directory-picker) and [Home with a selected workspace](Get-Started#home-with-a-selected-workspace). The selected state is visible; the transition, full-path identity, cancellation, and persistence remain untested. |
| **Choose a workspace to start** | This is a prerequisite message in the prompt composer, not an instruction to type a workspace path into the prompt. |
| **Standard mode** | A mode selector is shown with this value. The [Agent presets guide](Agent-Presets#choose-a-mode-from-home) covers the later open Home menu with Standard checked and PTC, Minimal, and Creator also visible. Switching behavior and scope still need testing; a preset is not a governed role or project authorization. |
| **New Session** | The sidebar's session entry point. A later selected-workspace capture also shows a New Session entry beneath its workspace, but no submitted prompt or response. |
| **Workspaces / No sessions yet** | The displayed navigation view has no sessions. That does not establish whether canonical projects or work items exist. |
| **Settings** | The settings entry point is at the lower left. See the illustrated [General Settings reference](Settings) for a separate capture of the open dialog. |

The capture also contains icon-only controls beside **Workspaces** and inside the
composer. Their tooltips, accessible names, keyboard behavior, and resulting
dialogs have not been inspected; this guide does not assign them unverified
functions. The separate directory-picker capture is documented through the
labeled **Choose workspace** route; it does not establish what the sidebar's
folder-shaped icon does. The [selected-workspace view](Get-Started#home-with-a-selected-workspace)
also exposes a separate right-hand composer selector labeled with an
`@preset/...` reference. Keep the workspace, agent mode, model/provider
configuration, and session permissions distinct; a visible name or send arrow
is not a completed first-response test. A further [Home permission capture](Settings#session-permission-menu-on-home)
shows Read Only, Workspace Write (checked), and Full access at the lower left
of the composer. This documents the menu, not the enforcement boundary or an
instruction to broaden access.

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
frequent service controls. **Settings → GTKB services** already exposes a
[service-management panel](Services); do not assume that these controls need
to be built from scratch. Its presence does not replace a convenient launch
entry or prove startup and recovery qualification.

## Privacy and network boundary

Home is intended to remain on loopback. Telemetry and credential behavior must
be verified against the selected release. Do not expose Home to another network
or assume that browser reachability establishes host qualification.
