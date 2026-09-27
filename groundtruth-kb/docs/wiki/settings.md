# Settings

**Status:** Illustrated General Settings reference and navigation; interaction checks pending

**Reviewed:** 2026-09-26

Open **Settings** at the lower left of [GTKB Home](GTKB-Home), then select
**General**. This page describes the supplied view of the integrated harness
GUI; it does not change any settings or document unobserved dropdown options.

For the **GTKB** tab, see the separate illustrated [GTKB status guide](Status).
For **GTKB services**, see the illustrated [service-management guide](Services).
For **GTKB controls**, see the illustrated [operational-controls reference](Controls).
For **Models**, see the illustrated [models and providers guide](Models).

## General Settings

![GTKB Home Settings with General selected: Permission is Workspace Write, Language is English, Appearance is System, Font size is 14 px, Conversation display is Compact, and Enter behavior while busy is Queue.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-settings-general.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged. The exact
build/version is not visible. The values below are selected in this capture;
they are not established factory defaults or recommendations for every user.

| Setting | Value shown | Explanation supported by the visible UI |
| --- | --- | --- |
| **Permission** | **Workspace Write** | The helper text identifies this as the default permission mode for **new sessions**. The available alternatives and the precise operations this mode permits are not shown. |
| **Language** | **English** | English is selected. The list of supported languages is not expanded. |
| **Appearance** | **System** | System is highlighted; Light and Dark are also offered. Theme switching and system-theme tracking have not been tested in this review. |
| **Font size** | **14 px** | The helper text says this affects conversation content only. It does not promise to resize the complete interface. |
| **Conversation display** | **Compact** | The helper text says this controls process content in completed turns. The exact content collapsed or retained, and other display choices, are not shown. |
| **Enter behavior while busy** | **Queue** | The setting applies while busy. The helper text says Cmd/Ctrl+Enter uses the other behavior, but does not name that behavior in this view. |

## Session permissions and governed work

Session permissions and project authorization are separate concepts. Choosing a
harness permission mode is not authorization to implement a project and does
not replace the review requirements in [Core concepts](Core-Concepts).

Do not infer the precise file boundary, permitted operations, or approval-prompt
behavior from the name **Workspace Write** alone. Those details need a tested
permission-mode reference. The **Standard mode** selector on Home is a
differently labeled control; its relationship to the Permission setting has not
been established by these screenshots.

The Permission helper explicitly refers to new sessions. Do not assume a change
will alter an already running session. The effect and persistence of changes
must be checked against the installed release before relying on them.

## Other visible settings sections

The navigation also includes **GTKB**, **GTKB services**, **GTKB controls**,
**Models**, **Plugins**, and **Agent presets**. Their contents are not visible in
the General capture. Separate screenshots now document the **GTKB**
[status pane](Status), **GTKB services** [panel](Services), including its visible
Start/Stop controls, and **GTKB controls** [reference](Controls), including
numeric values, units, and ranges. The [Models guide](Models) now illustrates a
provider entry and the Edit/Add entry points. Those images establish the
displayed interface, not current health or tested control behavior. Provider
setup and model selection still need an end-to-end walkthrough; **Plugins** and
**Agent presets** still need content and interaction coverage.
The presence of a tab does not establish which providers, plugins, presets, or
controls are available or configured.

Use the checks in [Services](Services) and
[Verify installation](Verify-Installation) for the selected installation.

## Configuration-file access and saving

An **Open configuration file** button and an X-shaped close control are visible
at the top of the dialog. The screenshot does not identify the file opened, its
scope, or the application used to open it. Do not assume it is `groundtruth.toml`
or use it as a reason to edit generated harness configuration manually. This
page does not prescribe a manual configuration-file edit.

The separate [GTKB controls capture](Controls#configuration-path-and-value-source)
shows an operational-controls path in its subtitle. That does not establish the
target of this shared dialog-level button, or whether it changes between tabs.

No Save, Apply, or Reset control is visible in the supplied General pane. This
does not prove that changes are saved automatically or that recovery controls
are absent elsewhere. A tested procedure still needs to establish when each
change is applied, whether it survives reopening Home, whether a new session is
required, and how to restore the previous value.

For documentation and usability follow-up, see
[Known issues: Settings review](Known-Issues#settings-review). For a problem with
the installed product, use [Troubleshooting](Troubleshooting) and
[Support](Support). Do not post configuration files or credentials in a public
support request.
