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
composer. A later capture identifies the composer's plus-shaped control with a
**Commands** tooltip and shows the [Commands menu](#commands-menu). A further
capture identifies the sliders-shaped control beside **Workspaces**
as the entry point for [grouping and ordering](#sidebar-grouping-and-ordering).
The remaining sidebar icons' functions, accessible names, and keyboard behavior
remain unverified.
The separate directory-picker capture is documented through the
labeled **Choose workspace** route; it does not establish what the sidebar's
folder-shaped icon does. The [selected-workspace view](Get-Started#home-with-a-selected-workspace)
also exposes a separate right-hand composer control labeled with an
`@preset/...` reference. Its later [open popover](Models#read-the-home-composer-reference)
explicitly shows **Model** and a right-facing chevron, but not the next view or
alternative models. Keep the workspace, agent mode, model/provider
configuration, and session permissions distinct; a visible name or send arrow
is not a completed first-response test. A further [Home permission capture](Settings#session-permission-menu-on-home)
shows Read Only, Workspace Write (checked), and Full access at the lower left
of the composer. This documents the menu, not the enforcement boundary or an
instruction to broaden access.

Continue with [Get started](Get-Started) for the next steps. The remaining
first-run guidance and screenshot coverage are listed in
[Known issues](Known-Issues).

## Sidebar grouping and ordering

The sliders-shaped control beside **Workspaces**, between the magnifying-glass
and folder-shaped icons, has a menu open in this capture. It separates **Group
by** from **Order by**, with a checkmark in each section. Its partly obscured
tooltip is not used here to invent a complete button label.

![GTKB Home with the sidebar grouping and ordering menu open beneath the sliders-shaped control beside Workspaces. Group by offers Workspace with a checkmark and In one list; Order by offers Manual and Last updated with a checkmark. The menu covers part of the session list; GT-KB, Standard mode, Workspace Write, and the model reference remain visible in the main view.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-sidebar-options.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged; exact
build/version not shown. These are the selections visible in this installation,
not established factory defaults. No sidebar option was changed, session
reordered, or workspace switched for this documentation pass.

| Section | Visible option | State in the capture | Meaning and remaining questions |
| --- | --- | --- | --- |
| **Group by** | **Workspace** | Checked. | Advertises workspace grouping. The image does not demonstrate switching groups, full-path identification, or handling similarly named workspaces. |
| **Group by** | **In one list** | Not checked. | Advertises an ungrouped list. The resulting view, workspace labels retained there, and return to grouped view are not shown. |
| **Order by** | **Manual** | Not checked. | Offers manual ordering. The actual method, items affected, keyboard alternative, and saved-order behavior are not shown; do not assume drag-and-drop. |
| **Order by** | **Last updated** | Checked. | Names an update-based order. Which updates count, sort direction, tie handling, and behavior during active work remain unverified. |

Grouping and ordering are separate navigation choices. **Workspace** here is a
grouping criterion, not a replacement for the **Choose workspace** control that
selects the working directory. Do not use sidebar order as evidence of canonical
work priority, dispatch order, project membership, or an agent's ownership of
work. See [Core concepts](Core-Concepts) for those distinctions.

The open menu obscures part of the list, so this image does not demonstrate the
resulting order or a complete session inventory. A tested walkthrough still
needs to show switching and dismissal, preference scope and persistence,
retention of the selected session and unsent input, and restoration of a prior
view. Changing this view is not a first-session prerequisite. Use the
[sidebar review checklist](Known-Issues#sidebar-grouping-and-ordering-review)
to qualify these behaviors with non-sensitive sample sessions.

## Commands menu

The plus-shaped control at the lower left of the composer is labeled
**Commands** in this capture. Its open panel lists seven conversation commands
and their helper text. The composer also advertises **/ commands, @ files or
sessions**; exact typed syntax, arguments, and keyboard behavior have not been
tested. These are Home conversation controls, not terminal CLI commands.

![GTKB Home with the Commands panel open above the composer, listing compact, export, feedback, goal, permission, plan, and model with helper text. The plus-shaped control has a Commands tooltip; compact is highlighted, Workspace Write and the model reference remain visible, and no command result is shown.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-commands.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged; exact
build/version not shown. The highlighted compact row is not proof that it ran.
No command was invoked, history compacted, export downloaded, feedback sent,
goal set, plan mode entered, permission changed, or model selected for this
documentation pass.

| Command | Purpose stated by the visible helper | Before relying on it |
| --- | --- | --- |
| `compact` | Compact older conversation history. | Establish what is summarized or removed, what remains available, persistence, and recovery. This is not the **Conversation display → Compact** presentation setting. |
| `export` | Download this Session log as a ZIP archive. | Inspect contents and handling using non-sensitive test data. Redaction, destination, and import/recovery are unverified. A session-log ZIP is not a [platform backup](Backup-And-Restore#session-export-is-not-a-platform-backup). |
| `feedback` | Record feedback about this session. | Establish destination, included data, confirmation/consent, and failure handling. Do not assume this creates a GitHub issue or canonical defect record; see [Support](Support#feedback-and-session-log-export-in-home). |
| `goal` | Set or view the goal for a long-running task. | Document the actual set/view flow, scope, progress, cancellation, persistence, and any provider usage. The menu does not demonstrate unattended execution or a startup service. |
| `permission` | Switch the permission preset (sandbox mode + approval policy). | The helper names the advertised combination, not tested enforcement. Compare the actual command flow with the [Home permission menu](Settings#session-permission-menu-on-home) before recommending a change. |
| `plan` | Enter or leave plan mode. | Qualify both transitions and their effect on tool execution. Harness plan mode is not a GTKB governed activity or project authorization, nor proof that all actions are read-only. |
| `model` | Select the model for this conversation. | This states the intended conversation scope. Available choices, reference resolution, change timing, and persistence still require testing; see [Models](Models#read-the-home-composer-reference). |

These are the rows visible in this build, not a complete command inventory for
every release or preset. The screenshot does not show command arguments,
confirmations, results, or failure states. No conversation command is established
as a first-session prerequisite. Follow the [Commands review checklist](Known-Issues#commands-review)
when qualifying behavior in a separate test installation, and keep private
conversation content and credentials out of public exports and recordings.

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
